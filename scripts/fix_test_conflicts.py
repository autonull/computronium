#!/usr/bin/env python
"""Fix test file naming conflicts between primitives and algorithms.

Renames primitive test files to include the axis name:
- test_routing_*.py -> test_plasticity_routing_*.py
- test_fast_weight_*.py -> test_plasticity_fast_weight_*.py
"""

from pathlib import Path


def fix_conflicts():
    test_root = Path("tests")
    
    # Conflicts: primitive names that also exist as algorithm names
    conflicts = {
        "routing": "plasticity",
        "fast_weight": "plasticity",
    }
    
    for prim_name, axis_name in conflicts.items():
        for test_file in test_root.glob(f"primitives/**/{prim_name}/test_{prim_name}_*.py"):
            new_name = test_file.name.replace(f"test_{prim_name}_", f"test_{axis_name}_{prim_name}_")
            new_path = test_file.parent / new_name
            test_file.rename(new_path)
            print(f"Renamed: {test_file} -> {new_path}")


if __name__ == "__main__":
    fix_conflicts()