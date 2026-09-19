#!/usr/bin/env python
"""Rename test files to avoid pytest collection conflicts.

Renames to include the primitive/algorithm name in the filename:
- test_primitive_reference.py -> test_<name>_reference.py
- test_primitive_kernel_parity.py -> test_<name>_kernel_parity.py
- test_primitive_cases.py -> test_<name>_cases.py
- test_algorithm_reference.py -> test_<name>_reference.py
- etc.
"""

from pathlib import Path


def rename_tests():
    test_root = Path("tests")

    # Rename primitive tests - use parent directory name (primitive name)
    for test_file in test_root.glob("primitives/**/test_primitive_*.py"):
        prim_name = test_file.parent.name
        new_name = test_file.name.replace("test_primitive_", f"test_{prim_name}_")
        new_path = test_file.parent / new_name
        test_file.rename(new_path)
        print(f"Renamed: {test_file} -> {new_path}")

    # Rename algorithm tests - use parent directory name (algorithm name)
    for test_file in test_root.glob("algorithms/**/test_algorithm_*.py"):
        algo_name = test_file.parent.name
        new_name = test_file.name.replace("test_algorithm_", f"test_{algo_name}_")
        new_path = test_file.parent / new_name
        test_file.rename(new_path)
        print(f"Renamed: {test_file} -> {new_path}")


if __name__ == "__main__":
    rename_tests()
