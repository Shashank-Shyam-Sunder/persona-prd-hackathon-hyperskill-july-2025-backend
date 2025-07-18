# src/pipeline.py

import os
import argparse
from .data_loader import load_data_for_persona_subreddit
from .preprocessing import preprocess_texts
from .embedding import load_or_generate_embeddings
from .clustering_KMeans_UMAP import load_or_generate_cluster_labels
from .cluster_diagnostics_module import load_or_generate_diagnostics
from .cluster_visualization import load_or_generate_visualization
from .summarization import summarise_all_clusters
from .persona_config import PERSONA_TO_FOLDER


def run_pipeline(persona: str, subreddit_file: str):
    # NOTE: No duplicate print here — already handled in CLI

    # ───────────────────────────────────────────────────────────────
    # STEP 1: Load Reddit data for the selected persona/subreddit
    # ───────────────────────────────────────────────────────────────
    df = load_data_for_persona_subreddit(persona, subreddit_file)
    print(f"📥 Loaded {len(df)} posts.")

    # ───────────────────────────────────────────────────────────────
    # STEP 2: Clean and normalize the text
    # ───────────────────────────────────────────────────────────────
    df["cleaned_text"] = preprocess_texts(df["combined_text"])
    print("🧼 Text cleaning and preprocessing complete.")

    # ✅ Save cleaned posts for inspection
    persona_folder = PERSONA_TO_FOLDER.get(persona)
    subreddit_folder = subreddit_file.replace(".json", "")
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "processed", persona_folder, subreddit_folder))
    os.makedirs(output_dir, exist_ok=True)
    excel_path = os.path.join(output_dir, "cleaned_posts.xlsx")
    df[["post_id", "title", "selftext", "combined_text", "cleaned_text"]].to_excel(excel_path, index=False)
    print(f"📁 Cleaned posts saved to: {excel_path}")

    # ───────────────────────────────────────────────────────────────
    # STEP 3: Generate or load cached sentence embeddings
    # ───────────────────────────────────────────────────────────────
    embeddings = load_or_generate_embeddings(df["cleaned_text"].tolist(), persona, subreddit_file)
    print(f"🔑 Embeddings ready. Shape: {embeddings.shape}")

    # ───────────────────────────────────────────────────────────────
    # STEP 4: Load or generate cluster labels
    # ───────────────────────────────────────────────────────────────
    labels = load_or_generate_cluster_labels(
        embeddings,
        post_ids=df["post_id"].tolist(),  # 👈 pass post_ids
        persona=persona,
        subreddit_filename=subreddit_file,
        n_clusters=10,
        n_components=10
    )
    df["cluster"] = labels
    print(f"🔗 Clustering ready. Total clusters: {len(set(labels))}")

    # ───────────────────────────────────────────────────────────────
    # STEP 5: Load or generate cluster diagnostics
    # ───────────────────────────────────────────────────────────────
    load_or_generate_diagnostics(embeddings, labels, persona, subreddit_file)

    # ───────────────────────────────────────────────────────────────
    # STEP 6: Generate or load interactive cluster visualization
    # ───────────────────────────────────────────────────────────────
    print("🔍 Generating interactive cluster visualization...")
    visualization_path = load_or_generate_visualization(df, embeddings, labels, persona, subreddit_file)
    print(f"📊 Interactive visualization ready. Open {visualization_path} in a web browser to explore clusters.\n")

    # ───────────────────────────────────────────────────────────────
    # STEP 7: Summarise each cluster
    # ───────────────────────────────────────────────────────────────
    print("🧠 Summarising clusters using Gemini LLM (always generates new summaries)...")
    summarise_all_clusters(df, n_clusters=10, persona=persona, subreddit_filename=subreddit_file)
    print("📝 Cluster summaries generated and saved.\n")

    # ───────────────────────────────────────────────────────────────
    # DONE
    # ───────────────────────────────────────────────────────────────
    print(f"✅ Pipeline completed successfully for {persona} / {subreddit_file}")
    print(f"📁 Results saved to: {output_dir}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run clustering pipeline for a given persona and subreddit")
    parser.add_argument("--persona", type=str, required=True, help="Persona key (e.g. 'vibecoding')")
    parser.add_argument("--subreddit", type=str, required=True, help="Subreddit JSON file (e.g. 'reddit_cursor_hot_500.json')")

    args = parser.parse_args()
    run_pipeline(args.persona, args.subreddit)
