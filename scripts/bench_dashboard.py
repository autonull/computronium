#!/usr/bin/env python
"""Benchmark dashboard - plots latency vs commit from microbench JSONL artifacts.

Usage:
    uv run python scripts/bench_dashboard.py --input artifacts/benchmarks/ --output dashboard.html
    uv run python scripts/bench_dashboard.py --input artifacts/benchmarks/ --spec primitive.state_dynamics.energy_minimization
"""

import argparse
import json
import pathlib
import sys
from collections import defaultdict

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


def load_benchmarks(bench_dir: pathlib.Path) -> list[dict]:
    """Load all benchmark JSONL files from directory."""
    results = []
    for jsonl_file in bench_dir.glob("*.jsonl"):
        with jsonl_file.open() as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    results.append(data)
                except json.JSONDecodeError:
                    continue
    return results


def filter_by_spec(results: list[dict], spec_id: str) -> list[dict]:
    """Filter results by spec ID."""
    return [r for r in results if r.get("id") == spec_id]


def aggregate_by_commit(results: list[dict]) -> dict[str, list[dict]]:
    """Group results by git SHA/tag."""
    grouped = defaultdict(list)
    for r in results:
        tag = r.get("tag") or r.get("git_sha") or "unknown"
        grouped[tag].append(r)
    return grouped


def compute_stats(values: list[float]) -> dict[str, float]:
    """Compute median, p95, mean from values."""
    if not values:
        return {"median": 0.0, "p95": 0.0, "mean": 0.0, "count": 0}
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    return {
        "median": sorted_vals[n // 2],
        "p95": sorted_vals[int(n * 0.95)] if n > 1 else sorted_vals[0],
        "mean": sum(sorted_vals) / n,
        "count": n,
    }


def _extract_commit_series(grouped: dict[str, list[dict]]) -> tuple[list[str], list[float], list[float]]:
    """Extract commit labels, median latencies, and p95 latencies from grouped results."""
    commits = sorted(grouped.keys())
    medians = []
    p95s = []
    labels = []
    for commit in commits:
        commit_results = grouped[commit]
        kernel_results = [r for r in commit_results if r.get("backend") == "kernel"]
        if not kernel_results:
            continue
        latencies = [r.get("wall_time_ms", 0) for r in kernel_results]
        stats = compute_stats(latencies)
        medians.append(stats["median"])
        p95s.append(stats["p95"])
        labels.append(commit[:8] if len(commit) > 8 else commit)
    return labels, medians, p95s


def _extract_memory_series(grouped: dict[str, list[dict]]) -> tuple[list[str], list[float]]:
    """Extract commit labels and median memory from grouped results."""
    commits = sorted(grouped.keys())
    mem_medians = []
    labels = []
    for commit in commits:
        commit_results = grouped[commit]
        kernel_results = [r for r in commit_results if r.get("backend") == "kernel"]
        if not kernel_results:
            continue
        mems = [r.get("peak_mem_mb", 0) for r in kernel_results]
        stats = compute_stats(mems)
        mem_medians.append(stats["median"])
        labels.append(commit[:8] if len(commit) > 8 else commit)
    return labels, mem_medians


def _plot_latency(ax, spec_id: str, labels: list[str], medians: list[float], p95s: list[float]) -> None:
    """Plot latency series on axis."""
    if not medians:
        return
    x = range(len(labels))
    ax.plot(x, medians, "o-", label="median", color="tab:blue")
    ax.plot(x, p95s, "s--", label="p95", color="tab:orange")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_ylabel("Latency (ms)")
    ax.set_title(f"{spec_id} - Latency")
    ax.legend()
    ax.grid(True, alpha=0.3)


def _plot_memory(ax, spec_id: str, labels: list[str], mem_medians: list[float]) -> None:
    """Plot memory series on axis."""
    if not mem_medians:
        return
    x = range(len(mem_medians))
    ax.plot(x, mem_medians, "o-", label="median", color="tab:green")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_ylabel("Peak Memory (MB)")
    ax.set_title(f"{spec_id} - Memory")
    ax.legend()
    ax.grid(True, alpha=0.3)


def plot_dashboard(
    results: list[dict], output_path: pathlib.Path, spec_filter: str | None = None
) -> None:
    """Generate dashboard plots."""
    if not MATPLOTLIB_AVAILABLE:
        print("matplotlib not available; skipping plot generation", file=sys.stderr)
        return

    # Filter by spec if provided
    if spec_filter:
        results = filter_by_spec(results, spec_filter)
        if not results:
            print(f"No results for spec: {spec_filter}", file=sys.stderr)
            return
        specs = [spec_filter]
    else:
        # Get unique spec IDs
        specs = sorted({r.get("id") for r in results if r.get("id")})

    fig, axes = plt.subplots(len(specs), 2, figsize=(14, 5 * len(specs)), squeeze=False)

    for i, spec_id in enumerate(specs):
        spec_results = filter_by_spec(results, spec_id)
        grouped = aggregate_by_commit(spec_results)

        labels, medians, p95s = _extract_commit_series(grouped)
        _plot_latency(axes[i, 0], spec_id, labels, medians, p95s)

        mem_labels, mem_medians = _extract_memory_series(grouped)
        _plot_memory(axes[i, 1], spec_id, mem_labels, mem_medians)

    fig.suptitle("Benchmark Dashboard - Latency & Memory vs Commit", fontsize=14)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Dashboard saved to {output_path}")


def print_summary(results: list[dict], spec_filter: str | None = None) -> None:
    """Print text summary to stdout."""
    if spec_filter:
        results = filter_by_spec(results, spec_filter)
        specs = [spec_filter]
    else:
        specs = sorted({r.get("id") for r in results if r.get("id") is not None})

    for spec_id in specs:
        spec_results = filter_by_spec(results, spec_id)
        grouped = aggregate_by_commit(spec_results)

        print(f"\n{'=' * 60}")
        print(f"Spec: {spec_id}")
        print(f"{'=' * 60}")

        for commit in sorted(grouped.keys()):
            commit_results = grouped[commit]
            kernel_results = [r for r in commit_results if r.get("backend") == "kernel"]
            ref_results = [r for r in commit_results if r.get("backend") == "reference"]

            print(f"\n  Commit: {commit[:12]}")
            if kernel_results:
                latencies = [r.get("wall_time_ms", 0) for r in kernel_results]
                mems = [r.get("peak_mem_mb", 0) for r in kernel_results]
                lat_stats = compute_stats(latencies)
                mem_stats = compute_stats(mems)
                print(
                    f"    Kernel:  median={lat_stats['median']:.2f}ms, p95={lat_stats['p95']:.2f}ms, mem={mem_stats['median']:.1f}MB (n={lat_stats['count']})"
                )
            if ref_results:
                latencies = [r.get("wall_time_ms", 0) for r in ref_results]
                lat_stats = compute_stats(latencies)
                print(
                    f"    Reference: median={lat_stats['median']:.2f}ms, p95={lat_stats['p95']:.2f}ms (n={lat_stats['count']})"
                )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark dashboard from microbench JSONL artifacts"
    )
    parser.add_argument(
        "--input",
        default="artifacts/benchmarks",
        help="Input directory with JSONL files",
    )
    parser.add_argument(
        "--output",
        default="artifacts/dashboard.html",
        help="Output HTML file (not used, saves PNG)",
    )
    parser.add_argument("--spec", help="Filter to specific spec ID")
    parser.add_argument(
        "--png", default="artifacts/bench_dashboard.png", help="Output PNG file"
    )
    parser.add_argument(
        "--summary-only", action="store_true", help="Print text summary only, no plots"
    )
    args = parser.parse_args()

    bench_dir = pathlib.Path(args.input)
    if not bench_dir.exists():
        print(f"Error: Benchmark directory not found: {bench_dir}", file=sys.stderr)
        return 1

    results = load_benchmarks(bench_dir)
    if not results:
        print("No benchmark data found", file=sys.stderr)
        return 1

    print(f"Loaded {len(results)} benchmark records from {bench_dir}")

    if args.summary_only:
        print_summary(results, args.spec)
    else:
        print_summary(results, args.spec)
        plot_dashboard(results, pathlib.Path(args.png), args.spec)

    return 0


if __name__ == "__main__":
    sys.exit(main())
