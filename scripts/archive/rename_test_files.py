#!/usr/bin/env python
"""Rename test files to avoid pytest collection conflicts.

Renames to include the primitive/algorithm name in the filename:
- test_reference.py -> test_<name>_reference.py
- test_kernel_parity.py -> test_<name>_kernel_parity.py
- test_cases.py -> test_<name>_cases.py
- test_factory.py -> test_<name>_factory.py
"""

from pathlib import Path


def rename_tests():
    test_root = Path("tests")

    # Rename primitive tests - use parent directory name (primitive name)
    for test_dir in test_root.glob("primitives/*/"):
        prim_name = test_dir.name
        for test_file in test_dir.glob("test_*.py"):
            if test_file.name.startswith(f"test_{prim_name}_"):
                continue  # Already renamed
            # Extract the test type from the filename (e.g., factory, reference, kernel_parity, cases)
            test_type = test_file.name[5:-3]  # Remove "test_" and ".py"
            new_name = f"test_{prim_name}_{test_type}.py"
            new_path = test_file.parent / new_name
            test_file.rename(new_path)
            print(f"Renamed: {test_file} -> {new_path}")

    # Rename algorithm tests - use parent directory name (algorithm name)
    for test_dir in test_root.glob("algorithms/*/"):
        algo_name = test_dir.name
        for test_file in test_dir.glob("test_*.py"):
            if test_file.name.startswith(f"test_{algo_name}_"):
                continue  # Already renamed
            # Extract the test type from the filename (e.g., factory, reference, kernel_parity, cases)
            test_type = test_file.name[5:-3]  # Remove "test_" and ".py"
            new_name = f"test_{algo_name}_{test_type}.py"
            new_path = test_file.parent / new_name
            test_file.rename(new_path)
            print(f"Renamed: {test_file} -> {new_path}")


if __name__ == "__main__":
    rename_tests()
