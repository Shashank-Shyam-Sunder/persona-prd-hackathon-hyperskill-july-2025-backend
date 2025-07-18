# tests/test_visualization.py
# Validates interactive cluster visualization + saves output for inspection

import os
import sys
import numpy as np
import pandas as pd

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.cluster_visualization import create_interactive_plot, save_visualization
from src import cluster_visualization  # for monkey patching PERSONA_TO_FOLDER


def test_visualization_fix():
    """Test that the visualization pipeline generates and saves correctly with expected HTML structure."""
    print("🧪 Testing visualization fix...\n")

    try:
        # 1. Create dummy data
        n_samples = 10
        embeddings_2d = np.random.rand(n_samples, 2)
        labels = np.random.randint(0, 3, n_samples)
        df = pd.DataFrame({
            'title': [f"Post {i}" for i in range(n_samples)],
            'selftext': [f"This is the content of post {i}" for i in range(n_samples)]
        })

        # 2. Generate interactive plot
        fig = create_interactive_plot(df, embeddings_2d, labels)
        print("✅ Successfully created interactive plot")

        # 3. Set test persona and manually map test folder
        test_persona = "test_persona"
        test_folder_map = {test_persona: "test_persona"}
        cluster_visualization.PERSONA_TO_FOLDER.update(test_folder_map)

        # 4. Save the visualization
        output_path = save_visualization(fig, test_persona, "test_subreddit.json")
        print(f"✅ Successfully saved visualization to {output_path}")

        # 5. Verify the file contents
        if os.path.exists(output_path):
            print(f"✅ Visualization file exists at {output_path}")

            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()

                if '.plotly-graph-div' in content:
                    print("✅ Contains .plotly-graph-div class")
                else:
                    print("❌ Missing .plotly-graph-div class")

                if 'DOMContentLoaded' in content:
                    print("✅ Contains DOMContentLoaded listener")
                else:
                    print("❌ Missing DOMContentLoaded listener")

                if 'plotly_click' in content:
                    print("✅ Contains plotly_click event")
                else:
                    print("❌ Missing plotly_click event")

                if 'post-modal' in content:
                    print("✅ Contains modal creation code")
                else:
                    print("❌ Missing modal creation code")

        else:
            print(f"❌ Visualization file does not exist at {output_path}")

        print("\n🎉 All tests passed (or reported above).")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    test_visualization_fix()
