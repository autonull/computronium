"""Campaign summary report (TODO30 8.8 / §7.3) — read-only assembly over
the campaign artifacts. This is the artifact a scientist takes to a paper
or review; it never writes to the KB or ledger."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from computronium.autoscientist.campaign_readers import (
    cost_breakdown_rows,
    cost_stats,
    front_history_rows,
    graveyard_rows,
    health_stats,
    maturation_rows,
    read_heartbeat,
    void_summary_rows,
)

if TYPE_CHECKING:
    from pathlib import Path

_REPORT_NAME = "campaign_report.md"


def _markdown_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    if not rows:
        return "_nothing recorded._\n"
    header = " | ".join(columns)
    divider = " | ".join("---" for _ in columns)
    body = "\n".join(
        " | ".join(str(row.get(column, "")) for column in columns) for row in rows
    )
    return f"{header}\n{divider}\n{body}\n"


def generate_report(root: Path, path: Path | None = None) -> Path:
    """Assemble §7.3 from the shipped read paths; returns the report path."""
    cells = health_stats(root)
    heartbeat = read_heartbeat(root)
    task = "unknown"
    if heartbeat is not None:
        task = str(heartbeat.get("task", task))
    costs = cost_stats(root)
    lines = [
        "# Computronium campaign summary",
        "",
        f"Root: `{root}` · task: {task} · "
        f"generated {datetime.datetime.now():%Y-%m-%d %H:%M}",
        "",
        "## Totals",
        "",
        _markdown_table(
            [
                {
                    "measured cells": cells["measured_cells"],
                    "bursts": cells["bursts"],
                    "open defects": cells["open_defects"],
                    "resolved defects": cells["resolved_defects"],
                    "diverged (NaN)": cells["nan_cells"],
                    "defect ids": costs["defects"],
                }
            ],
            [
                "measured cells",
                "bursts",
                "open defects",
                "resolved defects",
                "diverged (NaN)",
                "defect ids",
            ],
        ),
        "## Final Pareto front (front history; ★ = expansion)",
        "",
        _markdown_table(
            front_history_rows(root),
            ["burst", "cell", "accuracy", "walltime_s", "new_front"],
        ),
        "> Verification level: mapping-grade (maturity:l0 unless re-run at",
        "> higher tiers). Only maturity:l2 cells may back comparative claims",
        "> (CEEC governance).",
        "",
        "## Maturation",
        "",
        _markdown_table(maturation_rows(root), ["level", "meaning", "count"]),
        "## Negative results",
        "",
        "### Diverged cells grouped by axis primitive",
        "",
        _markdown_table(
            graveyard_rows(root), ["axis", "primitive", "diverged", "measured", "share"]
        ),
        "### Structural voids by category (boundaries, not failures)",
        "",
        _markdown_table(void_summary_rows(root), ["category", "count", "example"]),
        "## Cost breakdown",
        "",
        f"measured {costs['measured']}"
        f" · mean {costs['mean_walltime_s']}s/cell"
        f" · projected remaining: {costs['projected_remaining_s'] or '—'}s",
        "",
        _markdown_table(
            cost_breakdown_rows(root),
            ["axis", "primitive", "mean_walltime_s", "n"],
        ),
    ]
    target = path if path is not None else root / _REPORT_NAME
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target
