#!/usr/bin/env python
"""Validate Composition - Static check for algorithm primitive dependencies.

Each algorithm spec carries `uses_primitives` tuple listing the primitive IDs
it depends on. This script verifies that all declared dependencies:
1. Exist in the registry
2. Are importable (no circular/broken imports)
3. Are of kind="primitive"

Usage:
    uv run python scripts/validate_composition.py --all-algorithms
    uv run python scripts/validate_composition.py --algorithm algorithm.backprop
"""

import argparse
import importlib
import sys

from computronium.acceleration.registry import algorithms, all_specs


def _find_primitive_spec(prim_id: str):
    """Find a primitive spec by ID."""
    for s in all_specs():
        if s.id == prim_id:
            return s
    return None


def _check_primitive_exists(spec, prim_id: str, errors: list[str]) -> bool:
    """Check if primitive exists in registry."""
    prim_spec = _find_primitive_spec(prim_id)
    if prim_spec is None:
        errors.append(f"  {spec.id} -> {prim_id}: NOT FOUND in registry")
        return False
    return True


def _check_primitive_kind(spec, prim_spec, prim_id: str, errors: list[str]) -> bool:
    """Check if spec is a primitive (not algorithm)."""
    if prim_spec.kind != "primitive":
        errors.append(
            f"  {spec.id} -> {prim_id}: is {prim_spec.kind}, expected primitive"
        )
        return False
    return True


def _check_primitive_importable(
    spec, prim_spec, prim_id: str, errors: list[str]
) -> bool:
    """Check if primitive is importable."""
    try:
        module_path = prim_spec.reference_entrypoint.rsplit(".", 1)[0]
        importlib.import_module(module_path)
    except Exception as e:
        errors.append(f"  {spec.id} -> {prim_id}: import failed: {e}")
        return False
    return True


def validate_algorithm(spec, verbose: bool = False) -> tuple[bool, list[str]]:
    """Validate an algorithm's primitive dependencies.

    Returns:
        (all_ok, list_of_errors)
    """
    errors = []

    if not spec.uses_primitives:
        if verbose:
            print(f"  {spec.id}: no primitive dependencies declared")
        return True, []

    for prim_id in spec.uses_primitives:
        if not _check_primitive_exists(spec, prim_id, errors):
            continue

        prim_spec = _find_primitive_spec(prim_id)
        if prim_spec is None:
            continue

        if not _check_primitive_kind(spec, prim_spec, prim_id, errors):
            continue

        if not _check_primitive_importable(spec, prim_spec, prim_id, errors):
            continue

        if verbose:
            print(f"  {spec.id} -> {prim_id}: OK ({prim_spec.axis})")

    return len(errors) == 0, errors


def _parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate algorithm primitive dependencies"
    )
    parser.add_argument(
        "--all-algorithms", action="store_true", help="Validate all algorithm specs"
    )
    parser.add_argument("--algorithm", help="Validate a specific algorithm by ID")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    return parser.parse_args()


def _get_specs_to_check(args, all_algo_specs):
    """Get the list of specs to validate."""
    if args.all_algorithms:
        return all_algo_specs
    specs_to_check = [s for s in all_algo_specs if s.id == args.algorithm]
    if not specs_to_check:
        print(f"Algorithm not found: {args.algorithm}", file=sys.stderr)
        sys.exit(1)
    return specs_to_check


def _check_specs(specs_to_check, verbose: bool, all_algorithms: bool):
    """Check all specs and return error counts."""
    total_errors = 0
    algorithms_with_errors = 0

    for spec in specs_to_check:
        if verbose or not all_algorithms:
            print(f"Checking {spec.id} (family: {spec.family or 'unknown'})...")

        _ok, errors = validate_algorithm(spec, verbose=verbose)

        if errors:
            algorithms_with_errors += 1
            total_errors += len(errors)
            print(f"  {spec.id}: {len(errors)} error(s)")
            for err in errors:
                print(err)
        elif verbose:
            print(f"  {spec.id}: OK")

        if not all_algorithms:
            print()

    return total_errors, algorithms_with_errors


def _print_summary(specs_to_check, total_errors, algorithms_with_errors):
    """Print validation summary."""
    print("\n=== Summary ===")
    print(f"Algorithms checked: {len(specs_to_check)}")
    print(f"Algorithms with errors: {algorithms_with_errors}")
    print(f"Total dependency errors: {total_errors}")

    if total_errors > 0:
        print("\nValidation FAILED")
        return 1
    else:
        print("\nValidation PASSED")
        return 0


def main() -> int:
    args = _parse_args()

    all_algo_specs = algorithms()
    specs_to_check = _get_specs_to_check(args, all_algo_specs)

    print(f"Validating {len(specs_to_check)} algorithm(s)...\n")

    total_errors, algorithms_with_errors = _check_specs(
        specs_to_check, args.verbose, args.all_algorithms
    )

    return _print_summary(specs_to_check, total_errors, algorithms_with_errors)


if __name__ == "__main__":
    sys.exit(main())
