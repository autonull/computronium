#!/usr/bin/env python3
"""Benchmark comparison script for nightly CI."""

import json
import argparse
from pathlib import Path
from typing import Any


def load_results(path: str) -> dict[str, Any]:
    """Load benchmark results from JSON file."""
    with open(path) as f:
        return json.load(f)


def compare_results(baseline: dict, current: dict) -> dict:
    """Compare two benchmark result sets."""
    comparison = {
        "improvements": [],
        "regressions": [],
        "unchanged": [],
        "new_metrics": [],
        "missing_metrics": [],
    }
    
    baseline_metrics = baseline.get("metrics", {})
    current_metrics = current.get("metrics", {})
    
    all_keys = set(baseline_metrics.keys()) | set(current_metrics.keys())
    
    for key in all_keys:
        if key not in baseline_metrics:
            comparison["new_metrics"].append(key)
            continue
        if key not in current_metrics:
            comparison["missing_metrics"].append(key)
            continue
        
        base_val = baseline_metrics[key]
        curr_val = current_metrics[key]
        
        if isinstance(base_val, (int, float)) and isinstance(curr_val, (int, float)):
            diff = curr_val - base_val
            pct_change = (diff / base_val * 100) if base_val != 0 else float('inf')
            
            if pct_change > 5:
                comparison["improvements"].append({
                    "metric": key,
                    "baseline": base_val,
                    "current": curr_val,
                    "change_pct": pct_change,
                })
            elif pct_change < -5:
                comparison["regressions"].append({
                    "metric": key,
                    "baseline": base_val,
                    "current": curr_val,
                    "change_pct": pct_change,
                })
            else:
                comparison["unchanged"].append({
                    "metric": key,
                    "baseline": base_val,
                    "current": curr_val,
                    "change_pct": pct_change,
                })
    
    return comparison


def generate_markdown_report(comparison: dict, baseline_path: str, current_path: str) -> str:
    """Generate markdown report from comparison."""
    lines = [
        "# Benchmark Comparison Report",
        f"Baseline: {baseline_path}",
        f"Current: {current_path}",
        "",
        f"## Summary",
        f"- Improvements: {len(comparison['improvements'])}",
        f"- Regressions: {len(comparison['regressions'])}",
        f"- Unchanged: {len(comparison['unchanged'])}",
        f"- New metrics: {len(comparison['new_metrics'])}",
        f"- Missing metrics: {len(comparison['missing_metrics'])}",
        "",
    ]
    
    if comparison["regressions"]:
        lines.append("## ⚠️ Regressions")
        for r in comparison["regressions"]:
            lines.append(
                f"- **{r['metric']}**: {r['baseline']:.4g} → {r['current']:.4g} "
                f"({r['change_pct']:+.1f}%)"
            )
        lines.append("")
    
    if comparison["improvements"]:
        lines.append("## ✅ Improvements")
        for r in comparison["improvements"]:
            lines.append(
                f"- **{r['metric']}**: {r['baseline']:.4g} → {r['current']:.4g} "
                f"({r['change_pct']:+.1f}%)"
            )
        lines.append("")
    
    if comparison["new_metrics"]:
        lines.append("## 🆕 New Metrics")
        for m in comparison["new_metrics"]:
            lines.append(f"- {m}")
        lines.append("")
    
    if comparison["missing_metrics"]:
        lines.append("## ❌ Missing Metrics")
        for m in comparison["missing_metrics"]:
            lines.append(f"- {m}")
        lines.append("")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Compare benchmark results")
    parser.add_argument("--baseline", required=True, help="Baseline results JSON file")
    parser.add_argument("--current", required=True, help="Current results JSON file")
    parser.add_argument("--output", default="comparison_report.md", help="Output markdown file")
    
    args = parser.parse_args()
    
    baseline = load_results(args.baseline)
    current = load_results(args.current)
    
    comparison = compare_results(baseline, current)
    report = generate_markdown_report(comparison, args.baseline, args.current)
    
    Path(args.output).write_text(report)
    print(f"Comparison report written to {args.output}")
    
    # Print summary
    print(f"Improvements: {len(comparison['improvements'])}")
    print(f"Regressions: {len(comparison['regressions'])}")
    print(f"Unchanged: {len(comparison['unchanged'])}")
    
    if comparison["regressions"]:
        print("⚠️ Regressions detected!")
        for r in comparison["regressions"]:
            print(f"  {r['metric']}: {r['change_pct']:+.1f}%")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())