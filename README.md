# PersonaPRD – AI Hackathon July 2025 🚀

PersonaPRD is an AI-powered system developed during the AI Hackathon July 2025. It transforms unstructured Reddit feedback into structured, persona-specific Product Requirements Documents (PRDs) using semantic embeddings, clustering, and Gemini-based summarization.

🎯 **The goal**: Accelerate early-stage product discovery and prioritization by extracting pain points directly from community conversations.

---

## 🔍 What It Does

- Loads persona-aligned Reddit data from curated datasets.
- Cleans and embeds posts using SBERT (`all-MiniLM-L6-v2`).
- Saves a cleaned Excel snapshot with original + cleaned text for validation (`cleaned_posts.xlsx`).
- Clusters posts with UMAP + KMeans for topic grouping.
- Computes diagnostics like silhouette and intra/inter-cluster distance ratios.
- Generates interactive visualizations of clusters with Plotly.
- Summarizes each cluster into user pain points using Gemini (LangChain).
- Lets you select clusters to auto-generate a structured PRD (`.docx`).

---

## 🗂️ Project Structure

```
persona-prd-hackathon-july-2025/
│
├── .venv/                               # Python virtual environment (optional)
├── .env                                 # ⚙️ API credentials (GOOGLE_API_KEY)
├── requirements.txt                     # 🧰 All Python dependencies
├── LICENSE                              # 📜 Open-source license (MIT)
├── README.md                            # You're reading it
│
├── run_full_mvp_cli.py                  # 🔁 Main CLI to run entire pipeline (data loading to PRD generation)
│
├── data/
│   ├── raw/
│   │   └── starter_datasets/
│   │       ├── data_neighbourhood/
│   │       ├── vibecoding_neighbourhood/
│   │       └── selfhost_neighbourhood/
│   └── processed/
│       └── <persona>/<subreddit>/
│           ├── cleaned_posts.xlsx
│           ├── embeddings.npy
│           ├── clusters_KMeans_UMAP.csv
│           ├── cluster_diagnostics_metrics.csv
│           ├── cluster_visualization.html
│           ├── pain_point_summaries.csv
│           └── PRD_DRAFT_with_selected_pain_points.docx
│
├── src/
│   ├── pipeline.py
│   ├── preprocessing.py
│   ├── embedding.py
│   ├── clustering_KMeans_UMAP.py
│   ├── cluster_diagnostics_module.py
│   ├── cluster_visualization.py
│   ├── summarization.py
│   ├── prd_generator.py
│   ├── persona_config.py
│   ├── run_generate_prd.py
│   ├── user_selection_utils.py
│   └── utils.py
│
│
├── tests/                               # 🧪 Unit tests for critical modules
│   ├── test_cluster_numbering.py        # Ensures consistent cluster labels
│   ├── test_imports.py                  # Checks if all imports work across files
│   ├── test_requirements.py             # Verifies dependency alignment
│   ├── test_user_selection.py           # Tests cluster selection logic
│   └── test_visualization.py            # Validates cluster visualization logic

```

---

## 🚀 Quickstart

1. 🔧 **Install requirements**
```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

2. 🔑 **Set your Google API key**
Create a file named `.env` in the root:
```
GOOGLE_API_KEY=your-real-key-here
```

3. 🧠 **Run the full MVP pipeline**
```bash
python run_full_mvp_cli.py
```

You'll be prompted to:
- Select a persona
- Select a subreddit dataset
- Review pain point summaries
- Select which clusters to include in the PRD

---

## 📄 Output Files Explained

Each processed subreddit folder (`data/processed/<persona>/<subreddit>/`) contains:

- `cleaned_posts.xlsx` – Original + cleaned post text (title, selftext, combined_text, cleaned_text)
- `embeddings.npy` – SBERT-based embeddings (384-d)
- `clusters_KMeans_UMAP.csv` – Mapping of `post_id` to cluster (labels range from 0–9 internally)
- `cluster_diagnostics_metrics.csv` – Clustering quality metrics (silhouette, distances)
- `cluster_visualization.html` – Interactive Plotly visualization (cluster labels shown as 1–10)
- `pain_point_summaries.csv` – LLM-generated pain point summaries
- `PRD_DRAFT_with_selected_pain_points.docx` – Final PRD document

---

## 🧾 Input JSON Format

Each dataset is a .json file containing an array of Reddit posts, where each post includes:

- **Post metadata**: `id`, `title`, `selftext`, `url`, `score`, `upvote_ratio`, `num_comments`, `created_utc`, `author`, `subreddit`
- **Post flags**: e.g., `is_self`, `stickied`, `locked`, `spoiler`, etc.
- **Comment threads (up to 100)**: Nested objects with `id`, `body`, `score`, `created_utc`, `author`, and parent relationships
- **Engagement metrics**: Vote scores, comment counts, interaction ratios

📌 **Current Scope in MVP**:  
We currently use only the post title and selftext for our semantic analysis. These are combined into a single string (`combined_text`) per post to generate embeddings.

---

## 🧾 Clustering Diagnostics: Interpretation Guide

<details>
<summary><strong>Interpretation Guide (Click to expand)</strong></summary>

<br>

| Metric                    | What It Means                                                                 | Good Range                   | Interpretation                                                                 |
|---------------------------|-------------------------------------------------------------------------------|------------------------------|---------------------------------------------------------------------------------|
| **Silhouette Score**      | How well points fit their clusters vs. others                                 | > 0.5 (Good), > 0.2 (Moderate) | Higher means well-separated, dense clusters. Negative or near 0 is bad.        |
| **Intra-cluster Distance**| Avg. distance from points to their own cluster centroid (compactness)         | < 0.5 (Tight), < 0.8 (OK)     | Lower = denser clusters. High = clusters are loose or incoherent.              |
| **Inter-cluster Distance**| Avg. distance between cluster centroids (separation)                          | > 1.0 (Good), > 0.6 (OK)      | Higher = clusters are well-separated in space.                                 |
| **Intra/Inter Ratio**     | Intra-cluster distance ÷ Inter-cluster distance                               | < 1.0 (Ideal), < 1.2 (Good)   | Lower = clusters are compact and well-separated. > 1.5 usually means weak results. |

</details>
---

## 🔍 Notes for Users to interpret clustering metrics 

- ✅ **Use these metrics comparatively** — they are best for comparing multiple runs (e.g., UMAP vs no UMAP).
- ⚠️ A *low Silhouette Score* doesn't always mean bad clustering — especially if your goal is diversity or coverage.
- 🧠 Always **visualize clusters** and **inspect actual content** for final decisions. You may see the interactive plotly plot for each subreddit processed data in the file `cluster_visualization.html`.

---


## 🧪 Running Tests

This project includes a minimal test suite to validate core functionality across modules.

To run all tests:

```bash
pytest tests/
```

Make sure your virtual environment is activated and dependencies are installed (`pip install -r requirements.txt`).

Please note: All tests should pass, though you may see warnings if some test functions return True/False instead of using assert statements. This does not affect the outcome but can be improved for better practice.

### ✅ What's Covered

| Test File                     | Purpose                                                       |
|------------------------------|---------------------------------------------------------------|
| `test_cluster_numbering.py`  | Ensures consistent and gap-free cluster labeling              |
| `test_imports.py`            | Verifies all key modules can be imported correctly            |
| `test_requirements.py`       | Confirms required packages are installed and version-matched  |
| `test_user_selection.py`     | Tests CLI-based user cluster selection logic                  |
| `test_visualization.py`      | Validates cluster visualization rendering (Plotly HTML output)|

Tests are designed to be fast and run without requiring internet access or real API keys.

---

## ⚠️ Important Notes & Developer Tips

### 1. 💥 Changing LLM or Embedding Model?
If you change either:
- The **embedding model** in `embedding.py`, or
- The **LLM model** in `summarization.py`

👉 **Delete or back up** the corresponding folder under `data/processed/` so fresh embeddings, clusters, summaries, and PRD are regenerated.

### 2. 📎 Relative Imports & Testing
The code in `src/` uses **relative paths**. If you try to run a module like `src/pipeline.py` directly, you’ll get import errors.  
✅ Use the `run_full_mvp_cli.py` script at the root level to run the full pipeline.

To test individual files directly, add this to the top of the file:
```python
import sys
import os
sys.path.append(os.path.abspath(".."))
```

### 3. 🔢 Cluster Label Conventions
- Internally saved cluster labels (in `.csv`) are from `0–9`.
- For display in CLI and Plotly plots, they are **converted to 1–10** for human readability.

### 4. 🔁 Switch to a Different LLM or Embedding?
Update the following files:
- **LLM summarization** → `src/summarization.py` and `src/prd_generator.py`
- **Embedding model** → `src/embedding.py`

### 5. 🔐 .env Setup Reminder
Before running the code, create a `.env` file and paste your Google API key:
```
GOOGLE_API_KEY=your-real-key-here
```
💡 You can switch to GPT-4, Claude, or other providers with minor adjustments.

### 6. 🆔 Why `post_id`?
The original Reddit JSON contains a field called `id`.  
We **rename it to `post_id`** in preprocessing to improve clarity and ensure consistent referencing across files (clustering, summaries, PRD).

---

## 🔬 Model Configuration

- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`
- **LLM Summarization**: `Gemini 1.5 Flash` (via LangChain)
- Both can be swapped based on preferences and quota availability.

---

## 💡 Ideal Use Cases

- Product Managers and Designers doing early-stage user discovery
- AI teams building semantic feedback clustering tools
- Startups validating ideas using community pain points
- UX Researchers summarizing feedback at scale
- AI Engineers building LLM-based research or discovery pipelines

---

## 🧠 Credits

Built by Team Clouded Sky (Hackathon team name) as part of the Hyperskill AI Engineer Bootcamp + Hackathon (July 2025).

## 📜 License

MIT License — feel free to fork, use, and build on top of this project.
