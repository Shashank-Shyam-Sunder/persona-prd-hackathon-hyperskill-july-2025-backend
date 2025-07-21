# src/summarization.py

import os
from typing import List, Dict
from dotenv import load_dotenv
import pandas as pd

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from .persona_config import PERSONA_TO_FOLDER

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")

# LLM model setup
model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",  # Fast and cost-efficient
    google_api_key=GOOGLE_API_KEY
)

# Summarization prompt
SUMMARY_PROMPT_TEMPLATE = """
You are an expert Product Manager AI assistant. Summarise the following Reddit posts into a concise pain point summary.

Posts:
{cluster_posts}

Instructions:
- Identify the core pain point(s) expressed in these posts.
- Summarise clearly in 2-3 sentences.
- Do NOT mention Reddit or posts. Only output the pain point summary.

Summary:
"""

prompt = PromptTemplate(
    input_variables=["cluster_posts"],
    template=SUMMARY_PROMPT_TEMPLATE,
)

# Chain setup
summarisation_chain = prompt | model


def summarise_cluster(posts: List[str]) -> str:
    combined_posts = "\n".join(posts)
    response = summarisation_chain.invoke({"cluster_posts": combined_posts})
    return response.content.strip()


def summarise_all_clusters(df: pd.DataFrame, n_clusters: int, persona: str, subreddit_filename: str) -> Dict[int, str]:
    """
    Summarise each cluster using Gemini LLM and save results in CSV.
    Includes num_posts per cluster for better traceability.
    """
    persona_folder = PERSONA_TO_FOLDER.get(persona)
    if not persona_folder:
        raise ValueError(f"Unknown persona '{persona}'")

    subreddit_folder = subreddit_filename.replace(".json", "")
    output_folder = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "data", "processed", persona_folder, subreddit_folder))
    os.makedirs(output_folder, exist_ok=True)

    output_filepath = os.path.join(output_folder, "pain_point_summaries.csv")

    print(f"🔄 Generating new cluster summaries for {persona} - {subreddit_filename}...")

    rows = []
    for cluster_id in range(n_clusters):
        cluster_posts = df[df["cluster"] == cluster_id]["cleaned_text"].tolist()
        num_posts = len(cluster_posts)
        if cluster_posts:
            print(f"✍️  Summarising cluster {cluster_id + 1} with {num_posts} posts...")
            summary = summarise_cluster(cluster_posts)
            print(f"📌 Cluster {cluster_id + 1} summary: {summary}\n")
        else:
            summary = "No posts in this cluster."

        rows.append({
            "cluster_id": cluster_id,
            "num_posts": num_posts,
            "pain_point_summary": summary
        })

    summary_df = pd.DataFrame(rows)
    summary_df.to_csv(output_filepath, index=False)
    print(f"📄 Saved pain point summaries to {output_filepath}")

    return {row["cluster_id"]: row["pain_point_summary"] for row in rows}
