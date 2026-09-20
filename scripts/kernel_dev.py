#!/usr/bin/env python
"""Kernel Development Watcher.

Re-runs parity test on file change for a specific primitive.
Uses polling (no new deps) for simplicity.

Usage:
    uv run python scripts/kernel_dev.py --primitive primitive.credit_assignment.random_projections --watch
    uv run python scripts/kernel_dev.py --primitive primitive.credit_assignment.random_projections --once
"""

import argparse
import importlib
import sys
import time
from pathlib import Path

from computronium.acceleration.registry import get


def run_parity_check(spec) -> tuple[bool, str]:
    """Run parity check for a spec. Returns (passed, message)."""
    if spec.axis in ("geometry", "substrate"):
        return False, f"{spec.axis} primitives use different interface"

    if "kernel" not in spec.supported_backends:
        return False, "no kernel backend"

    try:
        module_path = spec.reference_entrypoint.rsplit(".", 2)[0]

        reference_module = importlib.import_module(f"{module_path}.reference")
        kernel_module = importlib.import_module(f"{module_path}.kernel")
        case_module = importlib.import_module(f"{module_path}.cases")

        if not kernel_module.is_available():
            return False, "kernel not available"

        # Use separate cases for reference and kernel to avoid autograd graph reuse issues
        case_ref = case_module.make_case()
        case_kern = case_module.make_case()

        reference_output = reference_module.step(case_ref)
        kernel_output = kernel_module.step(case_kern)

        from computronium.acceleration.parity import assert_parity

        assert_parity(reference_output, kernel_output, spec.parity)

        # Get the report for details
        from computronium.acceleration.parity import compare

        report = compare(reference_output, kernel_output)
        return True, f"PASS: max_abs_diff={report['max_abs_diff']:.2e}, max_rel_diff={report['max_rel_diff']:.2e}, cosine={report['cosine']:.6f}"

    except AssertionError as e:
        return False, f"FAIL: {e}"
    except Exception as e:
        return False, f"ERROR: {e}"


def get_kernel_file_path(spec) -> Path:
    """Get the kernel.py file path for a spec."""
    module_path = spec.reference_entrypoint.rsplit(".", 2)[0]
    parts = module_path.split(".")
    primitive_dir = Path(*parts)
    return primitive_dir / "kernel.py"


def watch_kernel(spec, poll_interval: float = 1.0) -> int:
    """Watch kernel file and re-run parity on change."""
    kernel_path = get_kernel_file_path(spec)

    if not kernel_path.exists():
        print(f"Kernel file not found: {kernel_path}", file=sys.stderr)
        return 1

    print(f"Watching: {kernel_path}")
    print(f"Primitive: {spec.id}")
    print(f"Poll interval: {poll_interval}s")
    print("Press Ctrl+C to stop")
    print()

    last_mtime = kernel_path.stat().st_mtime
    run_count = 0

    # Initial run
    print("=== Initial parity check ===")
    passed, msg = run_parity_check(spec)
    print(msg)
    run_count += 1

    try:
        while True:
            time.sleep(poll_interval)

            try:
                current_mtime = kernel_path.stat().st_mtime
            except FileNotFoundError:
                print(f"Kernel file deleted: {kernel_path}")
                break

            if current_mtime != last_mtime:
                last_mtime = current_mtime
                run_count += 1
                print(f"\n=== Change detected (run #{run_count}) ===")
                passed, msg = run_parity_check(spec)
                print(msg)

    except KeyboardInterrupt:
        print(f"\nStopped after {run_count} runs")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Kernel development watcher")
    parser.add_argument(
        "--primitive",
        required=True,
        help="Primitive registry ID (e.g., primitive.credit_assignment.random_projections)",
    )
    parser.add_argument(
        "--watch", action="store_true", help="Watch for file changes and re-run parity"
    )
    parser.add_argument(
        "--once", action="store_true", help="Run parity check once and exit"
    )
    parser.add_argument(
        "--poll-interval", type=float, default=1.0, help="Poll interval in seconds (watch mode)"
    )

    args = parser.parse_args()

    if not args.watch and not args.once:
        parser.error("Either --watch or --once is required")

    spec = get(args.primitive)

    if spec.kind != "primitive":
        print(f"Error: {args.primitive} is not a primitive (kind={spec.kind})", file=sys.stderr)
        return 1

    if args.once:
        passed, msg = run_parity_check(spec)
        print(msg)
        return 0 if passed else 1

    return watch_kernel(spec, args.poll_interval)


if __name__ == "__main__":
    sys.exit(main())