"""Microbenchmark Runner.

Runs tiny, non-scientific benchmark smoke tests for implementations.
Outputs JSON to stdout.
"""

import argparse
import importlib
import json
import time
from typing import Any

import torch


def run_microbench(
    implementation_id: str,
    backend: str = "auto",
    device: str = "cpu",
    steps: int = 3,
    dtype: str = "float32",
    seed: int = 0,
) -> dict[str, Any]:
    """Run a microbenchmark for a registered implementation.

    Args:
        implementation_id: Registry ID (e.g., "primitive.state_dynamics.pc_alm_settling")
        backend: "auto", "reference", or "kernel"
        device: Device to run on
        steps: Number of steps/iterations
        dtype: Data type
        seed: Random seed for reproducibility

    Returns:
        Dictionary with benchmark results
    """
    from computronium.acceleration.dispatch import select_backend
    from computronium.acceleration.registry import get

    spec = get(implementation_id)

    # Select backend
    backend_name = select_backend(spec, backend)

    # Import the appropriate module
    if backend_name == "reference":
        module_path = spec.reference_entrypoint.rsplit(".", 1)[0]
        func_name = spec.reference_entrypoint.rsplit(".", 1)[1]
    else:
        if spec.kernel_entrypoint is None:
            raise ValueError(f"No kernel entrypoint for {implementation_id}")
        module_path = spec.kernel_entrypoint.rsplit(".", 1)[0]
        func_name = spec.kernel_entrypoint.rsplit(".", 1)[1]

    module = importlib.import_module(module_path)
    step_func = getattr(module, func_name)

    # Import cases module
    cases_module_path = module_path.rsplit(".", 1)[0] + ".cases"
    cases_module = importlib.import_module(cases_module_path)

    # Create case
    torch_dtype = getattr(torch, dtype)
    case = cases_module.make_case(device=device, dtype=torch_dtype, seed=seed)

    # Warmup
    _ = step_func(case)

    # Benchmark
    if device != "cpu" and torch.cuda.is_available():
        torch.cuda.synchronize()

    start = time.perf_counter()
    for _ in range(steps):
        _ = step_func(case)
    if device != "cpu" and torch.cuda.is_available():
        torch.cuda.synchronize()
    elapsed = time.perf_counter() - start

    return {
        "id": implementation_id,
        "backend": backend_name,
        "device": device,
        "steps": steps,
        "wall_time_s": elapsed,
        "status": "ok",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Run microbenchmark for an implementation"
    )
    parser.add_argument("--id", required=True, help="Implementation ID from registry")
    parser.add_argument(
        "--backend",
        default="auto",
        choices=["auto", "reference", "kernel"],
        help="Backend to benchmark",
    )
    parser.add_argument("--device", default="cpu", help="Device (cpu, cuda)")
    parser.add_argument("--steps", type=int, default=3, help="Number of steps")
    parser.add_argument("--dtype", default="float32", help="Data type")
    parser.add_argument("--seed", type=int, default=0, help="Random seed")
    parser.add_argument("--json", action="store_true", help="Output JSON")

    args = parser.parse_args()

    result = run_microbench(
        implementation_id=args.id,
        backend=args.backend,
        device=args.device,
        steps=args.steps,
        dtype=args.dtype,
        seed=args.seed,
    )

    if args.json:
        print(json.dumps(result))
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
