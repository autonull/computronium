#!/usr/bin/env python3
"""Script to fix ImplementationSpec.family vocabulary to align with AlgorithmFamily.

This implements Option B from TODO37 §4.1: make ImplementationSpec.family values
align to AlgorithmFamily values.
"""

from pathlib import Path

# Mapping from algorithm spec file to new family value (AlgorithmFamily enum value)
FAMILY_MAP = {
    "backprop": "backprop",
    "fa": "fa",
    "dfa": "fa",  # DFA is a variant of FA
    "eqprop": "eqprop",
    "directed_ep": "eqprop",  # variant of EQPROP
    "finite_nudge_ep": "eqprop",  # variant of EQPROP
    "ternary_eqprop": "eqprop",  # variant of EQPROP
    "momentum_eqprop": "eqprop",  # variant of EQPROP
    "sparse_eqprop": "eqprop",  # variant of EQPROP
    "diffusion_eqprop": "eqprop",  # variant of EQPROP
    "holomorphic_ep": "eqprop",  # variant of EQPROP
    "ff": "ff",
    "pepita": "pepita",
    "pc": "pc",
    "pcalm": "pcalm",  # new AlgorithmFamily.PCALM
    "hebbian": "hebbian",
    "tile": "tile",
    "routing": "mep",  # uses MEP kernel backend
    "fast_weight": "o1memory",  # uses O1Memory kernel backend
    "spiking_snn": "snn",
    "tp": "tp",
}


def update_spec_file(algo_name: str, new_family: str) -> bool:
    """Update the family field in an algorithm spec file."""
    spec_path = Path(
        f"/home/me/computronium/computronium/algorithms/{algo_name}/spec.py"
    )
    if not spec_path.exists():
        print(f"  WARNING: {spec_path} not found")
        return False

    content = spec_path.read_text()

    # Find and replace the family line
    import re

    # Pattern: family="old_value",
    pattern = r'(family=)"[^"]*"'
    replacement = rf'\1"{new_family}"'

    new_content = re.sub(pattern, replacement, content)

    if new_content == content:
        print(f"  WARNING: No change made to {spec_path}")
        return False

    spec_path.write_text(new_content)
    print(f"  Updated {algo_name}: family -> {new_family}")
    return True


def main():
    print("Fixing ImplementationSpec.family vocabulary...")
    print("=" * 60)

    updated = 0
    for algo_name, new_family in FAMILY_MAP.items():
        if update_spec_file(algo_name, new_family):
            updated += 1

    print(f"\nUpdated {updated} algorithm spec files.")

    # Also update kernel_backend.py to add PCALM
    kernel_backend_path = Path(
        "/home/me/computronium/computronium/acceleration/kernel_backend.py"
    )
    content = kernel_backend_path.read_text()

    # Add PCALM to AlgorithmFamily enum
    if "PCALM = " not in content:
        # Find the AlgorithmFamily enum and add PCALM before O1MEMORY
        import re

        pattern = r'(O1MEMORY = "o1memory")'
        replacement = r'PCALM = "pcalm"\n    \1'
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            kernel_backend_path.write_text(new_content)
            print("  Added PCALM to AlgorithmFamily enum")
        else:
            print("  WARNING: Could not add PCALM to AlgorithmFamily enum")
    else:
        print("  PCALM already in AlgorithmFamily enum")

    # Update families.py to add PCALM binding
    families_path = Path("/home/me/computronium/computronium/acceleration/families.py")
    content = families_path.read_text()

    if "AlgorithmFamily.PCALM" not in content:
        # Add PCALM binding after PC binding
        import re

        pattern = r"(FamilyBinding\(\s*AlgorithmFamily\.PC,)"
        replacement = r"""FamilyBinding(
        AlgorithmFamily.PCALM,
        "computronium.acceleration.pcalm_kernels",
        "PCALMKernelBackend",
    ),
    \1"""
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            families_path.write_text(new_content)
            print("  Added PCALM binding to families.py")
        else:
            print("  WARNING: Could not add PCALM binding to families.py")
    else:
        print("  PCALM binding already in families.py")

    print("\nDone!")


if __name__ == "__main__":
    main()
