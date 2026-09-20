"""Microbenchmark Runner.

Runs tiny, non-scientific benchmark smoke tests for implementations.
Outputs JSON or CSV to stdout or file.
"""

import argparse
import importlib
import json
import pathlib
import subprocess  # needed for git SHA detection
import time
from typing import Any

import torch

# ruff: file-ignore[suspicious-subprocess-import,subprocess-without-shell-equals-true,start-process-with-partial-path] (subprocess import/run with fixed args is intentional for git SHA detection)


def _get_git_sha() -> str | None:
    """Get current git SHA if available."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        return None
    return None


def _get_peak_memory(device: str) -> float:
    """Get peak memory in MB."""
    if device != "cpu" and torch.cuda.is_available():
        return torch.cuda.max_memory_allocated() / (1024 * 1024)
    import resource

    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024  # MB on Linux


def _reset_peak_memory(device: str) -> None:
    """Reset peak memory counters."""
    if device != "cpu" and torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()


def _import_step_func(spec, backend_name: str):
    """Import the step function for the given spec and backend."""
    if backend_name == "reference":
        module_path = spec.reference_entrypoint.rsplit(".", 1)[0]
        func_name = spec.reference_entrypoint.rsplit(".", 1)[1]
    else:
        if spec.kernel_entrypoint is None:
            raise ValueError(f"No kernel entrypoint for {spec.id}")
        module_path = spec.kernel_entrypoint.rsplit(".", 1)[0]
        func_name = spec.kernel_entrypoint.rsplit(".", 1)[1]

    module = importlib.import_module(module_path)
    return getattr(module, func_name), module_path


def _import_cases_module(module_path: str):
    """Import the cases module."""
    cases_module_path = module_path.rsplit(".", 1)[0] + ".cases"
    return importlib.import_module(cases_module_path)


def _create_case(cases_module, device: str, dtype: str, seed: int):
    """Create a test case."""
    torch_dtype = getattr(torch, dtype)
    return cases_module.make_case(device=device, dtype=torch_dtype, seed=seed)


def _run_warmup(step_func, case, warmup: int) -> None:
    """Run warmup iterations."""
    for _ in range(warmup):
        _ = step_func(case)


def _run_iteration(step_func, case, device: str, steps: int) -> tuple[float, float]:
    """Run a single benchmark iteration. Returns (elapsed_s, peak_mem_mb)."""
    _reset_peak_memory(device)

    if device != "cpu" and torch.cuda.is_available():
        torch.cuda.synchronize()

    start = time.perf_counter()
    for _ in range(steps):
        _ = step_func(case)
    if device != "cpu" and torch.cuda.is_available():
        torch.cuda.synchronize()
    elapsed = time.perf_counter() - start

    peak_mem_mb = _get_peak_memory(device)
    return elapsed, peak_mem_mb


def run_microbench(
    implementation_id: str,
    backend: str = "auto",
    device: str = "cpu",
    steps: int = 3,
    dtype: str = "float32",
    seed: int = 0,
    warmup: int = 1,
    iterations: int = 1,
) -> list[dict[str, Any]]:
    """Run a microbenchmark for a registered implementation.

    Args:
        implementation_id: Registry ID (e.g., "primitive.state_dynamics.pc_alm_settling")
        backend: "auto", "reference", or "kernel"
        device: Device to run on
        steps: Number of steps/iterations per run
        dtype: Data type
        seed: Random seed for reproducibility
        warmup: Number of warmup runs (not measured)
        iterations: Number of measured iterations (for statistics)

    Returns:
        List of dictionaries with benchmark results (one per iteration)
    """
    from computronium.acceleration.dispatch import select_backend
    from computronium.acceleration.registry import get

    spec = get(implementation_id)
    backend_name = select_backend(spec, backend)

    step_func, module_path = _import_step_func(spec, backend_name)
    cases_module = _import_cases_module(module_path)
    case = _create_case(cases_module, device, dtype, seed)

    _run_warmup(step_func, case, warmup)

    results = []
    git_sha = _get_git_sha()

    for iter_idx in range(iterations):
        elapsed, peak_mem_mb = _run_iteration(step_func, case, device, steps)

        result = {
            "id": implementation_id,
            "backend": backend_name,
            "device": device,
            "steps": steps,
            "dtype": dtype,
            "seed": seed,
            "iteration": iter_idx,
            "wall_time_s": elapsed,
            "wall_time_ms": elapsed * 1000,
            "peak_mem_mb": peak_mem_mb,
            "status": "ok",
        }
        if git_sha:
            result["git_sha"] = git_sha

        results.append(result)

    return results


def _compute_stats(results: list[dict[str, Any]]) -> dict[str, float]:
    """Compute median, p95, throughput from iteration results."""
    if not results:
        return {}

    times_ms = [r["wall_time_ms"] for r in results]
    times_ms.sort()

    n = len(times_ms)
    median = (
        times_ms[n // 2]
        if n % 2 == 1
        else (times_ms[n // 2 - 1] + times_ms[n // 2]) / 2
    )
    p95_idx = min(int(0.95 * n), n - 1)
    p95 = times_ms[p95_idx]

    total_time_s = sum(r["wall_time_s"] for r in results)
    throughput = len(results) / total_time_s if total_time_s > 0 else 0.0

    return {
        "median_ms": median,
        "p95_ms": p95,
        "throughput": throughput,
    }


def _write_jsonl(results: list[dict[str, Any]], output_path: str) -> None:
    """Write results as JSONL (one JSON object per line)."""
    with pathlib.Path(output_path).open("w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")


def _write_csv(results: list[dict[str, Any]], output_path: str) -> None:
    """Write results as CSV with summary statistics."""
    import csv

    if not results:
        return

    stats = _compute_stats(results)
    first = results[0]

    with pathlib.Path(output_path).open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "id",
            "backend",
            "device",
            "dtype",
            "seed",
            "steps",
            "median_ms",
            "p95_ms",
            "throughput",
            "peak_mem_mb",
            "git_sha",
            "iterations",
            "warmup",
        ])
        writer.writerow([
            first["id"],
            first["backend"],
            first["device"],
            first.get("dtype", "float32"),
            first.get("seed", 0),
            first["steps"],
            f"{stats.get('median_ms', 0):.3f}",
            f"{stats.get('p95_ms', 0):.3f}",
            f"{stats.get('throughput', 0):.3f}",
            f"{first.get('peak_mem_mb', 0):.3f}",
            first.get("git_sha", ""),
            len(results),
            first.get("warmup", 1),
        ])


def _add_tag(results: list[dict[str, Any]], tag: str | None) -> None:
    """Add tag to all results."""
    if tag:
        for r in results:
            r["tag"] = tag


def _run_all_benchmarks(args, tag: str | None) -> list[dict[str, Any]]:
    """Run benchmarks for all specs."""
    from computronium.acceleration.registry import all_specs

    specs = all_specs()
    all_results = []
    for spec in specs:
        if args.id and spec.id != args.id:
            continue
        try:
            results = run_microbench(
                implementation_id=spec.id,
                backend=args.backend,
                device=args.device,
                steps=args.steps,
                dtype=args.dtype,
                seed=args.seed,
                warmup=args.warmup,
                iterations=args.iterations,
            )
            _add_tag(results, tag)
            all_results.extend(results)
        except Exception as e:
            all_results.append({
                "id": spec.id,
                "backend": args.backend,
                "device": args.device,
                "steps": args.steps,
                "dtype": args.dtype,
                "seed": args.seed,
                "iteration": 0,
                "wall_time_s": 0.0,
                "wall_time_ms": 0.0,
                "peak_mem_mb": 0.0,
                "status": f"error: {e}",
            })
            _add_tag(all_results[-1:], tag)
    return all_results


def _run_single_benchmark(args, tag: str | None) -> list[dict[str, Any]]:
    """Run benchmark for a single spec."""
    results = run_microbench(
        implementation_id=args.id,
        backend=args.backend,
        device=args.device,
        steps=args.steps,
        dtype=args.dtype,
        seed=args.seed,
        warmup=args.warmup,
        iterations=args.iterations,
    )
    _add_tag(results, tag)
    return results


def _output_results(results: list[dict[str, Any]], args) -> None:
    """Output results based on format and output path."""
    if args.output:
        if args.format == "jsonl" or args.output.endswith(".jsonl"):
            _write_jsonl(results, args.output)
            print(f"Wrote {len(results)} results to {args.output}")
        elif args.format == "csv" or args.output.endswith(".csv"):
            _write_csv(results, args.output)
            print(f"Wrote CSV summary to {args.output}")
        elif args.format == "json":
            with pathlib.Path(args.output).open("w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
            print(f"Wrote {len(results)} results to {args.output}")
    else:
        _print_to_stdout(results, args)


def _print_to_stdout(results: list[dict[str, Any]], args) -> None:
    """Print results to stdout."""
    if args.format == "json":
        print(json.dumps(results))
    elif args.format == "jsonl":
        for r in results:
            print(json.dumps(r))
    elif args.format == "csv":
        _write_csv(results, "/dev/stdout")
    else:
        print(json.dumps(results, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run microbenchmark for an implementation"
    )
    parser.add_argument("--id", help="Implementation ID from registry")
    parser.add_argument(
        "--backend",
        default="auto",
        choices=["auto", "reference", "kernel"],
        help="Backend to benchmark",
    )
    parser.add_argument("--device", default="cpu", help="Device (cpu, cuda)")
    parser.add_argument(
        "--steps", type=int, default=3, help="Number of steps per iteration"
    )
    parser.add_argument("--dtype", default="float32", help="Data type")
    parser.add_argument("--seed", type=int, default=0, help="Random seed")
    parser.add_argument("--warmup", type=int, default=1, help="Number of warmup runs")
    parser.add_argument(
        "--iterations", type=int, default=3, help="Number of measured iterations"
    )
    parser.add_argument(
        "--all", action="store_true", help="Run for all registered implementations"
    )
    parser.add_argument(
        "--format",
        choices=["json", "pretty", "jsonl", "csv"],
        default="pretty",
        help="Output format",
    )
    parser.add_argument(
        "--output",
        help="Output file path (JSONL or CSV). If not set, prints to stdout.",
    )
    parser.add_argument(
        "--tag",
        help="Git SHA or custom tag to embed in results (default: auto-detect git SHA)",
    )

    args = parser.parse_args()

    tag = args.tag or _get_git_sha()

    if args.all:
        results = _run_all_benchmarks(args, tag)
    elif args.id:
        results = _run_single_benchmark(args, tag)
    else:
        parser.error("Either --id or --all is required")

    _output_results(results, args)


if __name__ == "__main__":
    main()
