from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import uuid
import time

# --- IMPORTANT PATH CONFIGURATION ---
# Add the parent directory of 'src' to the Python path.
# This is crucial so that 'from src.pipeline import run_pipeline' works correctly
# when the FastAPI app is run from a different directory (e.g., via uvicorn).
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Project-specific Imports from your 'src' directory ---
from src.pipeline import run_pipeline
from src.persona_config import PERSONA_TO_FOLDER, PERSONA_DISPLAY_NAMES # Added PERSONA_DISPLAY_NAMES
from src.prd_generator import load_summaries, generate_prd_for_api # New imports from modified prd_generator.py
from src.data_loader import list_available_subreddits # New import for listing subreddits for frontend

# --- Import Pydantic Models from api/models.py ---
# These define the expected data structures for API requests and responses.
from .models import (
    PipelineRequest, PipelineResponse, PipelineStatusResponse, PersonaListResponse,
    ClusterSummary, ClusterSummariesResponse, PRDRequest, PRDResponse, PRDStatusResponse
)

# --- FastAPI Application Initialization ---
app = FastAPI(
    title="Reddit Persona Clustering & PRD Generation API",
    description="API for processing Reddit data, generating clusters, summaries, and Product Requirements Documents.",
    version="1.0.0"
)

# --- CORS Configuration ---
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8001", # For frontend served by `python -m http.server`
    # Add other specific frontend origins here when deploying, e.g., "https://your-frontend-domain.com"
    # WARNING: For production, DO NOT use ["*"] as it allows requests from ANY origin, which is a security risk.
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- In-memory Task Storage ---
# NOTE: For production, replace these with persistent storage (e.g., database, Redis).
running_tasks = {} # For main pipeline tasks
prd_running_tasks = {} # For PRD generation tasks


# --- Define Absolute Path for Processed Data ---
PROCESSED_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "processed"))
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True) # Ensure the base processed data directory exists


# --- Static Files Mounting ---
app.mount(
    "/static",
    StaticFiles(directory=PROCESSED_DATA_DIR),
    name="static_processed_data"
)

# ───────────────────────────────────────────────────────────────────────────────
# Background Task Functions
# ───────────────────────────────────────────────────────────────────────────────

async def run_pipeline_in_background(persona: str, subreddit: str, task_id: str):
    """
    Asynchronously executes the core data processing pipeline in the background.
    Updates the global `running_tasks` dictionary with the task's status and results.
    """
    start_time_task = time.time()
    print(f"[{time.ctime()}] [{task_id}] Starting pipeline for persona: '{persona}', subreddit: '{subreddit}'...")
    try:
        output_dir, visualization_path = run_pipeline(persona, subreddit)

        running_tasks[task_id] = {
            "status": "completed",
            "output_directory": output_dir,
            "visualization_path": visualization_path,
            "error": None
        }
        end_time_task = time.time()
        print(f"[{time.ctime()}] [{task_id}] Pipeline completed successfully in {end_time_task - start_time_task:.2f} seconds.")
        print(f"[{task_id}] Output Dir: {output_dir}")
        print(f"[{task_id}] Visualization Path: {visualization_path}")

    except Exception as e:
        error_message = f"Pipeline execution failed: {type(e).__name__}: {str(e)}"
        print(f"[{time.ctime()}] [{task_id}] {error_message}")
        running_tasks[task_id] = {
            "status": "failed",
            "output_directory": None,
            "visualization_path": None,
            "error": error_message
        }
    finally:
        pass


async def run_prd_generation_in_background(
    persona: str,
    subreddit: str,
    selected_cluster_ids: list[int], # CHANGED: from List[int] to list[int]
    prd_task_id: str
):
    """
    Asynchronously runs the PRD generation in the background.
    Updates the global `prd_running_tasks` dictionary.
    """
    start_time_prd = time.time()
    print(f"[{time.ctime()}] [PRD Task {prd_task_id}] Starting PRD generation for persona: '{persona}', subreddit: '{subreddit}', clusters: {selected_cluster_ids}...")
    try:
        # Call the orchestrator function from prd_generator
        prd_file_path = generate_prd_for_api(persona, subreddit, selected_cluster_ids)

        prd_running_tasks[prd_task_id] = {
            "status": "completed",
            "prd_path": prd_file_path,
            "error": None
        }
        end_time_prd = time.time()
        print(f"[{time.ctime()}] [PRD Task {prd_task_id}] PRD generation completed successfully in {end_time_prd - start_time_prd:.2f} seconds.")
        print(f"[{prd_task_id}] Generated PRD: {prd_file_path}")

    except Exception as e:
        error_message = f"PRD generation failed: {type(e).__name__}: {str(e)}"
        print(f"[{time.ctime()}] [PRD Task {prd_task_id}] {error_message}")
        prd_running_tasks[prd_task_id] = {
            "status": "failed",
            "prd_path": None,
            "error": error_message
        }

# ───────────────────────────────────────────────────────────────────────────────
# API Endpoints
# ───────────────────────────────────────────────────────────────────────────────

@app.post("/run_pipeline/", response_model=PipelineResponse, status_code=202)
async def trigger_pipeline(request: PipelineRequest, background_tasks: BackgroundTasks):
    """
    Triggers the Reddit persona clustering pipeline.
    The pipeline runs as a background task, and a unique task ID is returned
    to allow the client to poll for status updates.
    """
    task_id = str(uuid.uuid4())

    running_tasks[task_id] = {
        "status": "running",
        "output_directory": None,
        "visualization_path": None,
        "error": None
    }
    
    background_tasks.add_task(run_pipeline_in_background, request.persona, request.subreddit, task_id)
    
    persona_folder = PERSONA_TO_FOLDER.get(request.persona, "unknown_persona")
    subreddit_folder_name = request.subreddit.replace(".json", "")
    expected_hint_path = os.path.join(persona_folder, subreddit_folder_name).replace(os.sep, '/')

    return PipelineResponse(
        message=f"Pipeline started successfully for persona '{request.persona}' and subreddit '{request.subreddit}'.",
        task_id=task_id,
        expected_output_directory_hint=expected_hint_path
    )

@app.get("/pipeline_status/{task_id}", response_model=PipelineStatusResponse)
async def get_pipeline_status(task_id: str):
    """
    Checks the current status of a previously triggered pipeline task.
    Returns the status, output directory, and visualization path (if completed).
    """
    task_info = running_tasks.get(task_id)
    if not task_info:
        raise HTTPException(status_code=404, detail=f"Pipeline task with ID '{task_id}' not found.")
    
    frontend_visualization_url = None
    if task_info.get("visualization_path") and task_info["status"] == "completed":
        relative_path = os.path.relpath(task_info["visualization_path"], PROCESSED_DATA_DIR)
        frontend_visualization_url = f"/static/{relative_path.replace(os.sep, '/')}"

    return PipelineStatusResponse(
        status=task_info["status"],
        output_directory=task_info.get("output_directory"),
        visualization_path=frontend_visualization_url,
        error=task_info.get("error")
    )

@app.get("/available_personas/", response_model=PersonaListResponse)
async def get_available_personas():
    """
    Returns a list of available persona keys from the persona_config,
    which can be used to trigger the pipeline.
    """
    return PersonaListResponse(personas=list(PERSONA_TO_FOLDER.keys()))

@app.get("/available_subreddits/{persona_key}", response_model=list[str]) # CHANGED: from List[str] to list[str]
async def get_available_subreddits(persona_key: str):
    """
    Returns a list of available subreddit JSON filenames for a given persona.
    """
    try:
        # Using the list_available_subreddits function from data_loader.py
        subreddits = list_available_subreddits(persona_key)
        return subreddits
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Persona data folder not found: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching subreddits: {str(e)}")


@app.get("/cluster_summaries/{persona}/{subreddit}", response_model=ClusterSummariesResponse)
async def get_cluster_summaries(persona: str, subreddit: str):
    """
    Retrieves all generated cluster summaries for a given persona and subreddit.
    """
    try:
        df_summaries = load_summaries(persona, subreddit) # Uses load_summaries from prd_generator.py
        
        summaries_list = [
            ClusterSummary(
                cluster_id=row['cluster_id'],
                num_posts=row['num_posts'],
                pain_point_summary=row['pain_point_summary']
            ) for _, row in df_summaries.iterrows()
        ]
        
        persona_display_name = PERSONA_DISPLAY_NAMES.get(persona, persona)

        return ClusterSummariesResponse(
            summaries=summaries_list,
            persona_display_name=persona_display_name,
            subreddit_file=subreddit
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Cluster summaries not found for this persona/subreddit. Please run the main pipeline first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading cluster summaries: {str(e)}")


@app.post("/generate_prd/", response_model=PRDResponse, status_code=202)
async def trigger_prd_generation(request: PRDRequest, background_tasks: BackgroundTasks):
    """
    Triggers the generation of a Product Requirements Document (PRD).
    The PRD generation runs as a background task.
    """
    prd_task_id = str(uuid.uuid4())

    prd_running_tasks[prd_task_id] = {
        "status": "running",
        "prd_path": None,
        "error": None
    }

    background_tasks.add_task(
        run_prd_generation_in_background,
        request.persona,
        request.subreddit,
        request.selected_cluster_ids,
        prd_task_id
    )
    
    return PRDResponse(
        message=f"PRD generation started for persona '{request.persona}' and subreddit '{request.subreddit}'. PRD Task ID: {prd_task_id}",
        prd_task_id=prd_task_id
    )

@app.get("/prd_status/{prd_task_id}", response_model=PRDStatusResponse)
async def get_prd_status(prd_task_id: str):
    """
    Checks the status of a previously triggered PRD generation task.
    Returns the status and path to the generated PRD document if completed.
    """
    prd_task_info = prd_running_tasks.get(prd_task_id)
    if not prd_task_info:
        raise HTTPException(status_code=404, detail=f"PRD task with ID '{prd_task_id}' not found.")
    
    frontend_prd_url = None
    if prd_task_info.get("prd_path") and prd_task_info["status"] == "completed":
        # Make the path relative to the mounted static directory
        relative_path = os.path.relpath(prd_task_info["prd_path"], PROCESSED_DATA_DIR)
        frontend_prd_url = f"/static/{relative_path.replace(os.sep, '/')}" # Ensure forward slashes for URL

    return PRDStatusResponse(
        status=prd_task_info["status"],
        prd_path=frontend_prd_url, # Frontend will use this URL to download
        error=prd_task_info.get("error")
    )