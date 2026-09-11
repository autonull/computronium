"""Markdown report rendering for Lab comparisons."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from computronium_lab.lab import ComparisonResult


def render_table(results: list[ComparisonResult]) -> str:
    """Render comparison results as a markdown table."""
    header = "| preset | final loss | final acc | walltime (s) |\n|---|---|---|---|"
    rows = [
        f"| {r.preset} | {r.final_loss:.4f} | {r.final_accuracy:.4f} | "
        f"{r.walltime_s:.2f} |"
        for r in results
    ]
    return "\n".join([header, *rows])


def write_report(results: list[ComparisonResult], path: str) -> str:
    """Write a markdown comparison report; returns the file's content."""
    content = "# Computronium Lab comparison\n\n" + render_table(results) + "\n"
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return content


def result_json(results: list[ComparisonResult]) -> str:
    """Machine-readable JSON of comparison results."""
    return json.dumps(
        [
            {
                "preset": r.preset,
                "final_loss": r.final_loss,
                "final_accuracy": r.final_accuracy,
                "walltime_s": r.walltime_s,
                "history": r.history,
            }
            for r in results
        ],
        indent=2,
    )
