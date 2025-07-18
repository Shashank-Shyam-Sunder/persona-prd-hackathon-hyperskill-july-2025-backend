# src/preprocessing.py

import os
import re
import json
import pandas as pd
from typing import List, Union

from .persona_config import PERSONA_TO_FOLDER

def clean_text(text: str) -> str:
    """Clean a single text string for NLP tasks."""
    if not isinstance(text, str):
        return ""

    text = text.lower()
    text = re.sub(r'http\S+|www\.\S+', '', text)                         # Remove URLs
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)                # Markdown links
    text = re.sub(r'[^a-z0-9\s.,;!?\'"-]', ' ', text)                   # Keep basic punctuation
    text = re.sub(r'\s+', ' ', text)                                    # Normalize whitespace
    return text.strip()

def preprocess_texts(texts: Union[List[str], pd.Series]) -> pd.Series:
    """Clean a list or Series of raw texts."""
    texts = pd.Series(texts) if isinstance(texts, list) else texts
    return texts.apply(clean_text)

def preprocess_and_save_posts(json_path: str, persona_key: str):
    """Load raw Reddit posts, preprocess, and save cleaned results for validation."""
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df = df.rename(columns={"id": "post_id"})  # 👈 Ensure consistency across pipeline

    df["title"] = df["title"].fillna("")
    df["selftext"] = df["selftext"].fillna("")

    df["combined_text"] = df["title"] + " " + df["selftext"]
    df["cleaned_text"] = preprocess_texts(df["combined_text"])

    # Select key columns
    output_df = df[["post_id", "title", "selftext", "combined_text", "cleaned_text"]].copy()

    # Determine output path
    subreddit_file = os.path.basename(json_path)
    subreddit_folder = subreddit_file.replace(".json", "")
    persona_folder = PERSONA_TO_FOLDER.get(persona_key)
    if not persona_folder:
        raise ValueError(f"Unknown persona key: {persona_key}")

    output_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "processed", persona_folder, subreddit_folder))
    os.makedirs(output_folder, exist_ok=True)

    output_path = os.path.join(output_folder, "cleaned_posts.xlsx")
    output_df.to_excel(output_path, index=False)
    print(f"✅ Saved cleaned posts to {output_path}")

    return df["cleaned_text"].tolist()
