# tests/test_requirements.py
# This script tests that all dependencies in requirements.txt can be imported

import importlib


def test_imports():
    """Test that all dependencies in requirements.txt can be imported"""
    print("🔍 Testing imports for dependencies in requirements.txt...\n")

    modules_to_test = [
        "numpy",
        "pandas",
        "sklearn",  # scikit-learn
        "matplotlib",
        "sentence_transformers",
        "umap",  # umap-learn
        "langchain",
        "langchain_google_genai",
        "dotenv",  # python-dotenv
        "docx",  # python-docx
        "tqdm"
    ]

    success = True
    for module_name in modules_to_test:
        try:
            importlib.import_module(module_name)
            print(f"✅ Successfully imported: {module_name}")
        except ImportError as e:
            print(f"❌ Failed to import: {module_name} → {e}")
            success = False

    if success:
        print("\n🎉 All dependencies were imported successfully!")
    else:
        print("\n❌ Some imports failed. Please install or check your environment:")
        print("   👉 pip install -r requirements.txt")

    return success


if __name__ == "__main__":
    test_imports()
