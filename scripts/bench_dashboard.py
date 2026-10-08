#!/usr/bin/env python3
"""Benchmark dashboard script for tracking latency/memory vs commit."""

import json
import argparse
from pathlib import Path
from typing import Any
import subprocess


def get_git_commit() -> str:
    """Get current git commit hash."""
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()[:8]
    except Exception:
        return "unknown"


def load_results(path: str) -> dict[str, Any]:
    """Load benchmark results from JSON file."""
    with open(path) as f:
        return json.load(f)


def extract_key_metrics(results: dict) -> dict:
    """Extract key metrics for dashboard."""
    metrics = {}
    for suite_name, suite_data in results.get("suites", {}).items():
        for metric_name, metric_data in suite_data.get("metrics", {}).items():
            key = f"{suite_name}.{metric_name}"
            if isinstance(metric_data, dict) and "mean" in metric_data:
                metrics[key] = metric_data["mean"]
            elif isinstance(metric_data, (int, float)):
                metrics[key] = metric_data
    return metrics


def main():
    parser = argparse.ArgumentParser(description="Benchmark dashboard")
    parser.add_argument("--results", required=True, help="Benchmark results JSON file")
    parser.add_argument("--compare", action="store_true", help="Compare with baseline")
    parser.add_argument("--baseline", help="Baseline results JSON file")
    parser.add_argument("--current", help="Current results JSON file")
    parser.add_argument(
        "--output", default="dashboard_report.md", help="Output markdown file"
    )
    parser.add_argument(
        "--history", default="benchmark_history.json", help="History file"
    )

    args = parser.parse_args()

    if args.compare:
        if not args.baseline or not args.current:
            print("Error: --baseline and --current required for comparison")
            return 1

        baseline = load_results(args.baseline)
        current = load_results(args.current)

        base_metrics = extract_key_metrics(baseline)
        curr_metrics = extract_key_metrics(current)

        lines = [
            "# Benchmark Dashboard - Comparison",
            f"Baseline commit: {baseline.get('commit', 'unknown')}",
            f"Current commit: {current.get('commit', 'unknown')}",
            "",
            "| Metric | Baseline | Current | Change |",
            "|--------|----------|---------|--------|",
        ]

        all_keys = set(base_metrics.keys()) | set(curr_metrics.keys())
        for key in sorted(all_keys):
            if key not in base_metrics:
                lines.append(f"| {key} | N/A | {curr_metrics[key]:.4g} | New |")
            elif key not in curr_metrics:
                lines.append(f"| {key} | {base_metrics[key]:.4g} | N/A | Removed |")
            else:
                base = base_metrics[key]
                curr = curr_metrics[key]
                if base != 0:
                    pct = (curr - base) / base * 100
                    change = f"{pct:+.1f}%"
                else:
                    change = "N/A"
                lines.append(f"| {key} | {base:.4g} | {curr:.4g} | {change} |")

        Path(args.output).write_text("\n".join(lines))
        print(f"Comparison report written to {args.output}")
        return 0

    # Single results mode - update history
    results = load_results(args.results)
    commit = results.get("commit", get_git_commit())
    metrics = extract_key_metrics(results)

    # Load history
    history = {}
    if Path(args.history).exists():
        with open(args.history) as f:
            history = json.load(f)

    # Add current commit
    history[commit] = {
        "commit": commit,
        "timestamp": results.get("timestamp", ""),
        "metrics": metrics,
    }

    # Save history
    with open(args.history, "w") as f:
        json.dump(history, f, indent=2)

    # Generate dashboard
    lines = [
        "# Benchmark Dashboard",
        f"Latest commit: {commit}",
        f"Total commits tracked: {len(history)}",
        "",
        "## Key Metrics",
        "| Metric | Value |",
        "|--------|-------|",
    ]

    for key, value in sorted(metrics.items()):
        lines.append(f"| {key} | {value:.4g} |")

    lines.extend([
        "",
        "## History (last 10 commits)",
        "| Commit | " + " | ".join(sorted(metrics.keys())[:5]) + " |",
    ])
    lines.append("|--------|" + "|".join(["-------"] * min(5, len(metrics))) + "|")

    for hist_commit, hist_data in sorted(history.items(), reverse=True)[:10]:
        row = f"| {hist_commit} |"
        for key in sorted(metrics.keys())[:5]:
            val = hist_data.get("metrics", {}).get(key, "N/A")
            if isinstance(val, (int, float)):
                row += f" {val:.4g} |"
            else:
                row += f" {val} |"
        lines.append(row)

    Path(args.output).write_text("\n".join(lines))
    print(f"Dashboard written to {args.output}")
    return 0


if __name__ == "__main__":
    exit(main())
