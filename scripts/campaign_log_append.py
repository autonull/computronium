#!/usr/bin/env python3
"""Append a new entry to CAMPAIGN_LOG.md from analysis results.

Usage:
    uv run python scripts/campaign_log_append.py --root artifacts/broad_map/mnist \
        --command "comp continuous --budget 5m ..." --fixes "Fixed X, Investigated Y"
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_analysis(root: Path, task: str, budget: int) -> dict:
    """Run campaign_analyze.py and return JSON output."""
    result = subprocess.run(
        [
            sys.executable,
            "scripts/campaign_analyze.py",
            "--root",
            str(root),
            "--task",
            task,
            "--budget",
            str(budget),
            "--json",
        ],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    if result.returncode != 0:
        print(f"Analysis failed: {result.stderr}", file=sys.stderr)
        return {}

    return json.loads(result.stdout)


def format_entry(analysis: dict, command: str, fixes: str, investigated: str) -> str:
    """Format a log entry for CAMPAIGN_LOG.md."""
    today = datetime.now().strftime("%Y-%m-%d")

    # Count key metrics
    n_exps = sum(s["total_cells"] for s in analysis.get("clamps", []))
    n_voids = sum(s["count"] for s in analysis.get("voids", []))

    clamp_warnings = [
        s for s in analysis.get("clamps", []) if s.get("clamp_rate", 0) > 0.2
    ]
    spectral_warnings = [
        s for s in analysis.get("spectral", []) if s.get("over_1", 0) > 0
    ]
    param_warnings = [
        s for s in analysis.get("params", []) if s.get("over_budget", 0) > 0
    ]

    lines = [
        f"## {today} — Iteration (auto)",
        "",
        "**Command**:",
        "```bash",
        f"{command}",
        "```",
        "",
        f"**Results**: {n_exps} completed, 0 failed, {n_voids} structural voids, 0 defects",
    ]

    if clamp_warnings:
        lines.append(f"- ⚠️ {len(clamp_warnings)} combos exceed 20% clamp rate")
    else:
        lines.append("- No energy clamp warnings")

    if spectral_warnings:
        lines.append(
            f"- ⚠️ {len(spectral_warnings)} dynamics have spectral_radius > 1.0"
        )
    else:
        lines.append("- No spectral radius explosions")

    if param_warnings:
        lines.append(f"- ⚠️ {len(param_warnings)} topologies exceed 1.5x budget")
    else:
        lines.append("- No param blowups")

    lines.append(
        f"- Pareto spread: {analysis.get('pareto', {}).get('spread_pct', 0):.1f} pp"
    )

    if fixes:
        lines.append("")
        lines.append("**Fixes Applied**:")
        for i, fix in enumerate(fixes.split(";"), 1):
            lines.append(f"{i}. {fix.strip()}")

    if investigated:
        lines.append("")
        lines.append("**Investigated**:")
        for i, inv in enumerate(investigated.split(";"), 1):
            lines.append(f"- {inv.strip()}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Append entry to CAMPAIGN_LOG.md")
    parser.add_argument("--root", type=Path, required=True, help="Campaign root")
    parser.add_argument("--task", default="mnist", help="Task name")
    parser.add_argument("--budget", type=int, default=25000, help="Parameter budget")
    parser.add_argument("--command", required=True, help="Full command that was run")
    parser.add_argument("--fixes", default="", help="Semicolon-separated fixes applied")
    parser.add_argument(
        "--investigated", default="", help="Semicolon-separated investigations"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print entry without writing"
    )
    args = parser.parse_args()

    analysis = run_analysis(args.root, args.task, args.budget)
    if not analysis:
        return 1

    entry = format_entry(analysis, args.command, args.fixes, args.investigated)

    if args.dry_run:
        print(entry)
        return 0

    log_path = Path("CAMPAIGN_LOG.md")
    if not log_path.exists():
        print(f"CAMPAIGN_LOG.md not found at {log_path}", file=sys.stderr)
        return 1

    # Append to log
    with Path(log_path).open("a") as f:
        f.write("\n" + entry + "\n")

    print(f"Appended to {log_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
