# src/clustering_kMeans_UMAP.py

import os
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import umap
import warnings
from .persona_config import PERSONA_TO_FOLDER

warnings.filterwarnings("ignore", message="n_jobs value 1 overridden to 1 by setting random_state")

def get_cluster_labels_path(persona: str, subreddit_filename: str) -> str:
    """
    Return structured path to cache cluster labels in a dedicated folder per subreddit.
    """
    persona_folder = PERSONA_TO_FOLDER.get(persona)
    if not persona_folder:
        raise ValueError(f"Unknown persona '{persona}'")

    subreddit_folder = subreddit_filename.replace('.json', '')
    output_folder = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "data", "processed", persona_folder, subreddit_folder)
    )
    os.makedirs(output_folder, exist_ok=True)

    return os.path.join(output_folder, "clusters_KMeans_UMAP.csv")

def load_cluster_labels(persona: str, subreddit_filename: str) -> np.ndarray:
    """
    Load cached cluster labels if available.
    """
    cluster_labels_path = get_cluster_labels_path(persona, subreddit_filename)
    if os.path.exists(cluster_labels_path):
        df = pd.read_csv(cluster_labels_path)
        return df["cluster"].values
    return None

def cluster_embeddings_kmeans_umap(embeddings: np.ndarray, n_clusters: int = 10, n_components: int = 10, random_state: int = 42) -> (np.ndarray, np.ndarray):
    """
    Reduce dimensionality with UMAP and cluster using KMeans.
    Returns both the cluster labels and the reduced embeddings (optional for reuse).
    """
    print(f"Reducing dimensionality with UMAP to {n_components} components...")
    reducer = umap.UMAP(n_components=n_components, random_state=random_state)
    scaled_embeddings = StandardScaler().fit_transform(embeddings)
    reduced_embeddings = reducer.fit_transform(scaled_embeddings)

    print(f"Clustering reduced embeddings into {n_clusters} clusters using KMeans...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state)
    labels = kmeans.fit_predict(reduced_embeddings)
    print("Clustering completed.")
    return labels, reduced_embeddings

def save_cluster_labels_kmeans_umap(labels: np.ndarray, post_ids: list, persona: str, subreddit_filename: str):
    """
    Save post_id and cluster labels to:
    data/processed/<persona_folder>/<subreddit_folder>/clusters_KMeans_UMAP.csv
    """
    output_path = get_cluster_labels_path(persona, subreddit_filename)
    df = pd.DataFrame({
        "post_id": post_ids,
        "cluster": labels
    })
    df.to_csv(output_path, index=False)
    print(f"Saved cluster labels to {output_path}")

def load_or_generate_cluster_labels(embeddings: np.ndarray, post_ids: list, persona: str, subreddit_filename: str, n_clusters: int = 10, n_components: int = 10) -> np.ndarray:
    """
    Load cached cluster labels if available, else generate and save with post_ids.
    """
    labels = load_cluster_labels(persona, subreddit_filename)
    if labels is not None:
        print(f"✅ Loading cached cluster labels for {persona} - {subreddit_filename}")
        return labels
    else:
        print(f"🔄 No cached cluster labels found. Generating clusters for {persona} - {subreddit_filename}...")
        labels, _ = cluster_embeddings_kmeans_umap(embeddings, n_clusters, n_components)
        save_cluster_labels_kmeans_umap(labels, post_ids, persona, subreddit_filename)
        return labels

# ───────────────────────────────────────────────
# 🧪 Optional local test
# ───────────────────────────────────────────────
if __name__ == "__main__":
    dummy_embeddings = np.random.rand(100, 384)
    dummy_post_ids = [f"post_{i}" for i in range(100)]
    dummy_labels, _ = cluster_embeddings_kmeans_umap(dummy_embeddings, n_clusters=10)
    save_cluster_labels_kmeans_umap(dummy_labels, dummy_post_ids, "vibecoding", "reddit_PromptEngineering_hot_500.json")
