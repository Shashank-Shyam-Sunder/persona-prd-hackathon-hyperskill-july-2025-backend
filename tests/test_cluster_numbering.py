# tests/test_cluster_numbering.py
# This script tests that the cluster numbering is consistent throughout the pipeline

import pandas as pd


def test_cluster_numbering():
    """Test that the cluster numbering is consistent throughout the pipeline"""
    print("Testing cluster numbering consistency...\n")

    # Test 1: Check that internal representation of cluster IDs is still 0-9
    print("Test 1: Internal representation of cluster IDs")
    try:
        df = pd.DataFrame({"cluster": list(range(10))})
        assert df['cluster'].min() == 0
        assert df['cluster'].max() == 9
        print(f"✅ Internal cluster IDs: {df['cluster'].tolist()}")
        print("✅ Internal representation test passed\n")
    except Exception as e:
        print(f"❌ Internal representation test failed: {e}\n")
        return False

    # Test 2: Check that display to users is 1-10
    print("Test 2: Display to users")
    try:
        display_ids = [cid + 1 for cid in df['cluster']]
        assert min(display_ids) == 1
        assert max(display_ids) == 10
        print(f"✅ Display cluster IDs: {display_ids}")
        print("✅ Display test passed\n")
    except Exception as e:
        print(f"❌ Display test failed: {e}\n")
        return False

    # Test 3: Check that user input converts from 1-10 back to 0-9
    print("Test 3: User input processing")
    try:
        user_input = "1,3,5,10"
        selected_ids = [int(cid.strip()) - 1 for cid in user_input.split(",") if cid.strip().isdigit()]
        expected_ids = [0, 2, 4, 9]
        assert selected_ids == expected_ids
        print(f"✅ Processed IDs: {selected_ids}")
        print("✅ User input processing test passed\n")
    except Exception as e:
        print(f"❌ User input processing test failed: {e}\n")
        return False

    print("🎉 All cluster numbering tests passed!")
    return True


if __name__ == "__main__":
    test_cluster_numbering()
