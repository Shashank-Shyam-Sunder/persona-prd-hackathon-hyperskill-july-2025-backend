# tests/test_user_selection.py
# Tests that the prompt_user_selection function works correctly with 1-based numbering

import sys
import os
from unittest.mock import patch

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from run_full_mvp_cli import prompt_user_selection


def test_prompt_user_selection():
    print("🧪 Testing prompt_user_selection with 1-based numbering...\n")

    options = ["Option A", "Option B", "Option C"]

    # Test 1: Input '1' → Option A
    with patch('builtins.input', return_value='1'):
        result = prompt_user_selection(options, "Select an option:")
        assert result == "Option A"
        print("✅ Test 1 passed: Input '1' returns 'Option A'")

    # Test 2: Input '3' → Option C
    with patch('builtins.input', return_value='3'):
        result = prompt_user_selection(options, "Select an option:")
        assert result == "Option C"
        print("✅ Test 2 passed: Input '3' returns 'Option C'")

    # Test 3: Invalid '0' then '1'
    with patch('builtins.input', side_effect=['0', '1']):
        result = prompt_user_selection(options, "Select an option:")
        assert result == "Option A"
        print("✅ Test 3 passed: Invalid input '0' handled")

    # Test 4: Invalid '4' then '2'
    with patch('builtins.input', side_effect=['4', '2']):
        result = prompt_user_selection(options, "Select an option:")
        assert result == "Option B"
        print("✅ Test 4 passed: Invalid input '4' handled")

    print("\n🎉 All tests passed for prompt_user_selection!")


if __name__ == "__main__":
    test_prompt_user_selection()
