# api/models.py
from pydantic import BaseModel, Field
from typing import Optional, List

# --- Pipeline Models ---
class PipelineRequest(BaseModel):
    """
    Defines the expected structure for triggering the pipeline.
    """
    persona: str = Field(..., example="vibecoding", description="The persona key to process data for.")
    subreddit: str = Field(..., example="reddit_cursor_hot_500.json", description="The subreddit JSON file to process.")

class PipelineResponse(BaseModel):
    """
    Defines the structure of the response after triggering the pipeline.
    """
    message: str = Field(..., description="A message indicating the status of the pipeline trigger.")
    task_id: str = Field(..., description="A unique ID for the background pipeline task.")
    expected_output_directory_hint: str = Field(..., description="A hint for the expected output directory path where results will be saved.")
    
class PipelineStatusResponse(BaseModel):
    """
    Defines the structure of the response when checking pipeline status.
    """
    status: str = Field(..., description="The current status of the pipeline task (e.g., 'running', 'completed', 'failed').")
    output_directory: Optional[str] = Field(None, description="The absolute path to the directory where results are saved, if completed.")
    visualization_path: Optional[str] = Field(None, description="The absolute path to the generated HTML visualization, if completed.")
    error: Optional[str] = Field(None, description="Error message if the pipeline failed.")

class PersonaListResponse(BaseModel):
    """
    Defines the structure for listing available personas.
    """
    personas: List[str] = Field(..., description="A list of available persona keys.")

# --- PRD Generation Models ---
class ClusterSummary(BaseModel):
    """Model for a single cluster summary."""
    cluster_id: int = Field(..., description="The ID of the cluster (0-indexed).")
    num_posts: int = Field(..., description="Number of posts in this cluster.")
    pain_point_summary: str = Field(..., description="The summarized pain point for this cluster.")
    
class ClusterSummariesResponse(BaseModel):
    """Response model for fetching all cluster summaries."""
    summaries: List[ClusterSummary] = Field(..., description="List of all cluster summaries.")
    persona_display_name: str = Field(..., description="Display name of the persona.")
    subreddit_file: str = Field(..., description="The subreddit file name.")

class PRDRequest(BaseModel):
    """Request model for generating a PRD."""
    persona: str = Field(..., example="vibecoding", description="The persona key.")
    subreddit: str = Field(..., example="reddit_cursor_hot_500.json", description="The subreddit JSON file.")
    selected_cluster_ids: List[int] = Field(..., description="List of 0-indexed cluster IDs to include in the PRD.")

class PRDResponse(BaseModel):
    """Response model after triggering PRD generation."""
    message: str = Field(..., description="A message about the PRD generation task.")
    prd_task_id: str = Field(..., description="Unique ID for the PRD generation task.")

class PRDStatusResponse(BaseModel):
    """Response model for checking PRD generation status."""
    status: str = Field(..., description="Status of the PRD generation task (running, completed, failed).")
    prd_path: Optional[str] = Field(None, description="Path to the generated PRD document.")
    error: Optional[str] = Field(None, description="Error message if PRD generation failed.")