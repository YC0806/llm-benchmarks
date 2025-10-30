#!/usr/bin/env python3
"""Test script to verify pandas dependency has been removed from benchmark_dataset.py"""

import sys
import importlib.util

def test_pandas_not_imported():
    """Verify that pandas is not imported when loading benchmark_dataset module"""
    # Track imported modules before loading
    modules_before = set(sys.modules.keys())

    # Import the benchmark_dataset module
    spec = importlib.util.spec_from_file_location(
        "benchmark_dataset",
        "/Users/guoyuchen/Documents/Project/llm-benchmarks/benchmark_dataset.py"
    )
    module = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Error loading module: {e}")
        return False

    # Track imported modules after loading
    modules_after = set(sys.modules.keys())
    new_modules = modules_after - modules_before

    # Check if pandas was imported
    pandas_modules = [m for m in new_modules if m.startswith('pandas')]

    if pandas_modules:
        print(f"FAIL: pandas is still being imported: {pandas_modules}")
        return False
    else:
        print("PASS: pandas is not imported")
        return True

def test_imports():
    """Test that the module can be imported without errors"""
    try:
        import benchmark_dataset
        print("PASS: benchmark_dataset module imported successfully")
        return True
    except ImportError as e:
        print(f"FAIL: Import error: {e}")
        return False
    except Exception as e:
        print(f"FAIL: Unexpected error during import: {e}")
        return False

if __name__ == "__main__":
    print("Testing pandas removal from benchmark_dataset.py\n")

    test1 = test_pandas_not_imported()
    print()
    test2 = test_imports()

    print("\n" + "="*50)
    if test1 and test2:
        print("All tests PASSED!")
        sys.exit(0)
    else:
        print("Some tests FAILED!")
        sys.exit(1)
