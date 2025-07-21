# src/run_generate_prd.py

import os
import argparse
import pandas as pd
from .prd_generator import generate_prd, save_prd_to_docx
from .persona_config import PERSONA_TO_FOLDER, PERSONA_DISPLAY_NAMES


def run_generate_prd(persona: str, subreddit_file: str):
    display_name = PERSONA_DISPLAY_NAMES.get(persona, persona)
    print(f"\n📝 Generating PRD for Persona: {display_name} / Subreddit: {subreddit_file}")

    # Construct paths
    persona_folder = PERSONA_TO_FOLDER.get(persona)
    subreddit_folder = subreddit_file.replace(".json", "")
    if not persona_folder:
        raise ValueError(f"Invalid persona key: {persona}")

    summary_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "data", "processed", persona_folder, subreddit_folder, "pain_point_summaries.csv"
    ))
    if not os.path.exists(summary_path):
        raise FileNotFoundError(f"Pain point summaries not found at: {summary_path}")

    # Load summaries
    df = pd.read_csv(summary_path)
    print(f"\n📌 Found {len(df)} pain point summaries. Here they are:\n")
    for idx, row in df.iterrows():
        print(f"[{row['cluster_id']+1}] {row['pain_point_summary']}\n")

    # Prompt user to select cluster IDs (1-indexed)
    raw_input = input("👉 Enter comma-separated cluster IDs to include in PRD (e.g. 1,2,5): ").strip()
    selected_cluster_ids = [int(cid.strip())-1 for cid in raw_input.split(",") if cid.strip().isdigit() and 1 <= int(cid.strip()) <= 10]

    selected_df = df[df["cluster_id"].isin(selected_cluster_ids)]
    if selected_df.empty:
        print("⚠️ No valid clusters selected. Exiting.")
        return

    pain_point_summaries = selected_df["pain_point_summary"].tolist()
    actual_cluster_ids = list(selected_df["cluster_id"].unique())
    num_posts = selected_df["num_posts"].sum() if "num_posts" in selected_df.columns else 0

    # Generate PRD
    prd_text = generate_prd(
        pain_point_summaries=pain_point_summaries,
        persona_display_name=display_name,
        subreddit_file=subreddit_file,
        selected_cluster_ids=actual_cluster_ids,
        num_posts=num_posts
    )

    print("\n=== Generated PRD Draft ===\n")
    print(prd_text)

    # Save to DOCX
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "processed", persona_folder, subreddit_folder))
    os.makedirs(output_dir, exist_ok=True)
    docx_path = os.path.join(output_dir, "PRD_DRAFT_with_selected_pain_points.docx")
    save_prd_to_docx(prd_text, docx_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate PRD from pain point summaries")
    parser.add_argument("--persona", type=str, required=True, help="Persona key (e.g. 'vibecoding')")
    parser.add_argument("--subreddit", type=str, required=True, help="Subreddit JSON filename")
    args = parser.parse_args()
    run_generate_prd(args.persona, args.subreddit)
