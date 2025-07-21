# tests/test_imports.py
# This script tests that the imports in run_full_mvp_cli.py work correctly

import os
import sys
import importlib

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_imports():
    """Test that all imports in run_full_mvp_cli.py work correctly"""
    print("Testing imports in run_full_mvp_cli.py...")

    try:
        from src.user_selection_utils import get_available_personas, get_subreddits_for_persona
        from src.persona_config import DISPLAY_TO_PERSONA, PERSONA_DISPLAY_NAMES
        from src.pipeline import run_pipeline
        from src.run_generate_prd import run_generate_prd
        print("✅ All direct imports successful")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

    modules_to_test = [
        "src.user_selection_utils",
        "src.persona_config",
        "src.pipeline",
        "src.run_generate_prd",
        "src.prd_generator",
        "src.summarization",
        "src.clustering_KMeans_UMAP",
        "src.embedding",
        "src.data_loader",
        "src.preprocessing",
        "src.cluster_diagnostics_module",
        "src.utils"
    ]

    for module_name in modules_to_test:
        try:
            importlib.import_module(module_name)
            print(f"✅ Successfully imported {module_name}")
        except ImportError as e:
            print(f"❌ Failed to import {module_name}: {e}")
            return False

    print("\nAll imports tested successfully!")
    return True

def test_file_paths():
    """Test that the file paths in the modules are correct"""
    print("\nTesting file paths...")

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_dir = os.path.join(repo_root, "data")

    starter_datasets_dir = os.path.join(data_dir, "raw", "starter_datasets")
    processed_dir = os.path.join(data_dir, "processed")

    if not os.path.exists(data_dir):
        print(f"❌ Data directory not found at {data_dir}")
        return False

    if not os.path.exists(starter_datasets_dir):
        print(f"❌ Starter datasets directory not found at {starter_datasets_dir}")
        return False

    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir, exist_ok=True)
        print(f"📁 Created missing 'processed' directory at {processed_dir}")

    print("✅ All file paths tested successfully!")
    return True

if __name__ == "__main__":
    imports_ok = test_imports()
    paths_ok = test_file_paths()

    if imports_ok and paths_ok:
        print("\n🎉 All tests passed! The pipeline structure is intact.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
