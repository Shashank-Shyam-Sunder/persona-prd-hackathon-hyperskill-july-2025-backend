# src/cluster_diagnostics_module.py

import numpy as np
import os
import pandas as pd
from sklearn.metrics import silhouette_score
from .persona_config import PERSONA_TO_FOLDER


def get_diagnostics_path(persona: str, subreddit_filename: str) -> str:
    """
    Return structured path to cache cluster diagnostics in a dedicated folder per subreddit.
    Example: data/processed/data_neighbourhood/reddit_BusinessIntelligence_hot_500/cluster_diagnostics_metrics.csv
    """
    persona_folder = PERSONA_TO_FOLDER.get(persona)
    if not persona_folder:
        raise ValueError(f"Unknown persona '{persona}'")

    subreddit_folder = subreddit_filename.replace('.json', '')
    output_folder = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "data", "processed", persona_folder, subreddit_folder)
    )
    os.makedirs(output_folder, exist_ok=True)

    return os.path.join(output_folder, "cluster_diagnostics_metrics.csv")


def load_diagnostics(persona: str, subreddit_filename: str) -> pd.DataFrame:
    """
    Load cached cluster diagnostics if available.
    """
    diagnostics_path = get_diagnostics_path(persona, subreddit_filename)
    
    if os.path.exists(diagnostics_path):
        return pd.read_csv(diagnostics_path)
    
    return None


def compute_intra_inter_cluster_distances(embeddings, labels):
    unique_labels = set(labels)
    if -1 in unique_labels:
        unique_labels.remove(-1)  # Exclude noise, if any

    intra_dists = []
    inter_dists = []

    centroids = {}

    for label in unique_labels:
        cluster_points = embeddings[labels == label]
        if len(cluster_points) < 2:
            continue
        centroid = cluster_points.mean(axis=0)
        centroids[label] = centroid

        # Intra-cluster distances: distance of each point to its cluster centroid
        dists = np.linalg.norm(cluster_points - centroid, axis=1)
        intra_dists.extend(dists)

    # Inter-cluster distances: distance between cluster centroids
    cluster_ids = list(centroids.keys())
    for i in range(len(cluster_ids)):
        for j in range(i + 1, len(cluster_ids)):
            dist = np.linalg.norm(centroids[cluster_ids[i]] - centroids[cluster_ids[j]])
            inter_dists.append(dist)

    return intra_dists, inter_dists


def run_cluster_diagnostics(embeddings, labels, output_folder):
    """
    Compute and save clustering diagnostics including:
    - Silhouette score
    - Intra/inter-cluster distances
    - Summary CSV of all metrics
    """
    print("\n📊 Running clustering diagnostics...")

    print("\n# 🧾 Clustering Diagnostics: Interpretation Guide")
    print("• Silhouette Score: Higher is better (>0.2 acceptable, >0.5 strong separation).")
    print("• Intra-cluster Distance: Lower is better (<0.5 tight, <0.8 acceptable).")
    print("• Inter-cluster Distance: Higher is better (>0.6 OK, >1.0 strong separation).")
    print("• Intra/Inter Ratio: Lower is better (<1.2 good, <1.0 ideal, >1.5 poor clustering).")

    print("\n🧠 Note: Clustering metrics on real-world Reddit data are often low due to noisy, high-dimensional discussions.")
    print("✔️ Focus on *interpreting summaries + visualizations* for actionable insights, not just numeric scores.\n")

    os.makedirs(output_folder, exist_ok=True)

    # Metrics
    silhouette = silhouette_score(embeddings, labels)
    intra, inter = compute_intra_inter_cluster_distances(embeddings, labels)
    intra_mean = np.mean(intra)
    inter_mean = np.mean(inter)
    intra_inter_ratio = intra_mean / inter_mean
    num_clusters = len(set(labels))

    print(f"📈 Silhouette Score: {silhouette:.4f}")
    print(f"📌 Avg. Intra-cluster distance: {intra_mean:.4f}")
    print(f"📍 Avg. Inter-cluster distance: {inter_mean:.4f}")
    print(f"📉 Intra/Inter Ratio (lower is better): {intra_inter_ratio:.4f}")

    # Save metrics CSV
    metrics_df = pd.DataFrame({
        "silhouette_score": [silhouette],
        "avg_intra_cluster_distance": [intra_mean],
        "avg_inter_cluster_distance": [inter_mean],
        "intra_inter_ratio": [intra_inter_ratio],
        "num_clusters": [num_clusters]
    })

    metrics_path = os.path.join(output_folder, "cluster_diagnostics_metrics.csv")
    metrics_df.to_csv(metrics_path, index=False)
    print(f"📁 Saved diagnostics CSV to: {metrics_path}\n")
    
    return metrics_df


def load_or_generate_diagnostics(embeddings, labels, persona: str, subreddit_filename: str):
    """
    Load cached cluster diagnostics if available, else generate and save to disk.
    """
    # Try to load cached diagnostics
    diagnostics_df = load_diagnostics(persona, subreddit_filename)
    
    if diagnostics_df is not None:
        print(f"✅ Loading cached cluster diagnostics for {persona} - {subreddit_filename}")
        print("\n# 🧾 Clustering Diagnostics: Interpretation Guide")
        print("• Silhouette Score: Higher is better (>0.2 acceptable, >0.5 strong separation).")
        print("• Intra-cluster Distance: Lower is better (<0.5 tight, <0.8 acceptable).")
        print("• Inter-cluster Distance: Higher is better (>0.6 OK, >1.0 strong separation).")
        print("• Intra/Inter Ratio: Lower is better (<1.2 good, <1.0 ideal, >1.5 poor clustering).")

        print("\n🧠 Note: Clustering metrics on real-world Reddit data are often low due to noisy, high-dimensional discussions.")
        print("✔️ Focus on *interpreting summaries + visualizations* for actionable insights, not just numeric scores.\n")

        silhouette = diagnostics_df["silhouette_score"].values[0]
        intra_mean = diagnostics_df["avg_intra_cluster_distance"].values[0]
        inter_mean = diagnostics_df["avg_inter_cluster_distance"].values[0]
        intra_inter_ratio = diagnostics_df["intra_inter_ratio"].values[0]
        
        print(f"📈 Silhouette Score: {silhouette:.4f}")
        print(f"📌 Avg. Intra-cluster distance: {intra_mean:.4f}")
        print(f"📍 Avg. Inter-cluster distance: {inter_mean:.4f}")
        print(f"📉 Intra/Inter Ratio (lower is better): {intra_inter_ratio:.4f}")
        
        return diagnostics_df
    else:
        print(f"🔄 No cached diagnostics found. Generating diagnostics for {persona} - {subreddit_filename}...")
        persona_folder = PERSONA_TO_FOLDER.get(persona)
        subreddit_folder = subreddit_filename.replace(".json", "")
        output_folder = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "data", "processed", persona_folder, subreddit_folder)
        )
        os.makedirs(output_folder, exist_ok=True)
        
        return run_cluster_diagnostics(embeddings, labels, output_folder)
