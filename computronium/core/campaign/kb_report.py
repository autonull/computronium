"""KB-based Campaign Report for Continuous Discovery (TODO40 P1.1).

Renders a comprehensive HTML/JSON report from the KnowledgeBase used by
``comp continuous`` campaigns. Includes:
- Pareto front over configured objectives
- Structural void breakdown by category
- Energy clamp frequency by (dynamics, credit, update)
- Walltime by dynamics family
- Maturation pipeline status (L0/L1/L2 counts)
- Defect quarantine status
"""

from __future__ import annotations

import json
import sqlite3
from collections import Counter
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass(frozen=True, slots=True)
class ParetoPoint:
    """One point on the Pareto front."""

    key: str
    dynamics: str
    credit: str
    update: str
    topology: str
    accuracy: float
    walltime_s: float
    param_count: int
    flops: float
    memory_mb: float
    energy_per_step: float
    latency_ms: float
    bp_deficit: float
    spectral_radius: float
    maturity: str  # l0, l1, l2


@dataclass(frozen=True, slots=True)
class VoidSummary:
    """Structural void summary by category."""

    category: str
    count: int
    examples: list[str]


@dataclass(frozen=True, slots=True)
class ClampSummary:
    """Energy clamp frequency by (dynamics, credit, update) triple."""

    dynamics: str
    credit: str
    update: str
    total_cells: int
    clamp_count: int
    clamp_rate: float


@dataclass(frozen=True, slots=True)
class WalltimeSummary:
    """Mean walltime by dynamics family."""

    dynamics: str
    cells: int
    mean_walltime_s: float
    min_walltime_s: float
    max_walltime_s: float


@dataclass(frozen=True, slots=True)
class MaturationSummary:
    """Maturation pipeline status counts."""

    l0_cells: int
    l1_cells: int
    l2_cells: int
    l1_keys: list[str]
    l2_keys: list[str]


@dataclass(frozen=True, slots=True)
class DefectSummary:
    """Defect quarantine status."""

    open_defects: int
    resolved_defects: int
    quarantined_cells: int
    defect_types: dict[str, int]


@dataclass(frozen=True, slots=True)
class KBReport:
    """Complete KB-based campaign report."""

    campaign_root: str
    task: str
    objectives: list[str]
    pareto_front: list[ParetoPoint]
    voids: list[VoidSummary]
    clamps: list[ClampSummary]
    walltimes: list[WalltimeSummary]
    maturation: MaturationSummary
    defects: DefectSummary
    kb_stats: dict

    def to_dict(self) -> dict:
        """JSON-serializable payload."""
        return {
            "campaign_root": self.campaign_root,
            "task": self.task,
            "objectives": self.objectives,
            "pareto_front": [
                {
                    "key": p.key,
                    "dynamics": p.dynamics,
                    "credit": p.credit,
                    "update": p.update,
                    "topology": p.topology,
                    "accuracy": p.accuracy,
                    "walltime_s": p.walltime_s,
                    "param_count": p.param_count,
                    "flops": p.flops,
                    "memory_mb": p.memory_mb,
                    "energy_per_step": p.energy_per_step,
                    "latency_ms": p.latency_ms,
                    "bp_deficit": p.bp_deficit,
                    "spectral_radius": p.spectral_radius,
                    "maturity": p.maturity,
                }
                for p in self.pareto_front
            ],
            "voids": [
                {"category": v.category, "count": v.count, "examples": v.examples}
                for v in self.voids
            ],
            "clamps": [
                {
                    "dynamics": c.dynamics,
                    "credit": c.credit,
                    "update": c.update,
                    "total_cells": c.total_cells,
                    "clamp_count": c.clamp_count,
                    "clamp_rate": c.clamp_rate,
                }
                for c in self.clamps
            ],
            "walltimes": [
                {
                    "dynamics": w.dynamics,
                    "cells": w.cells,
                    "mean_walltime_s": w.mean_walltime_s,
                    "min_walltime_s": w.min_walltime_s,
                    "max_walltime_s": w.max_walltime_s,
                }
                for w in self.walltimes
            ],
            "maturation": {
                "l0_cells": self.maturation.l0_cells,
                "l1_cells": self.maturation.l1_cells,
                "l2_cells": self.maturation.l2_cells,
                "l1_keys": self.maturation.l1_keys,
                "l2_keys": self.maturation.l2_keys,
            },
            "defects": {
                "open_defects": self.defects.open_defects,
                "resolved_defects": self.defects.resolved_defects,
                "quarantined_cells": self.defects.quarantined_cells,
                "defect_types": self.defects.defect_types,
            },
            "kb_stats": self.kb_stats,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2) + "\n"

    def to_html(self) -> str:
        return _render_html(self)

    def write(
        self, directory: str | Path, *, stem: str = "kb_campaign_report"
    ) -> tuple[Path, Path]:
        out = Path(directory)
        out.mkdir(parents=True, exist_ok=True)
        json_path = out / f"{stem}.json"
        html_path = out / f"{stem}.html"
        json_path.write_text(self.to_json(), encoding="utf-8")
        html_path.write_text(self.to_html(), encoding="utf-8")
        return json_path, html_path


# ---- Data extraction ---------------------------------------------------------


def _connect(kb_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(kb_path)
    conn.row_factory = sqlite3.Row
    return conn


def _load_experiments(kb_path: Path, task: str | None = None) -> list[sqlite3.Row]:
    """Load all experiment entries from KB."""
    conn = _connect(kb_path)
    if task:
        rows = conn.execute(
            "SELECT * FROM knowledge WHERE topic LIKE ? AND source = 'experiment'",
            (f"experiment:{task}",),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM knowledge WHERE topic LIKE 'experiment:%' AND source = 'experiment'"
        ).fetchall()
    conn.close()
    return rows


def _load_structural_voids(kb_path: Path, task: str | None = None) -> list[sqlite3.Row]:
    """Load structural voids from KB."""
    conn = _connect(kb_path)
    if task:
        rows = conn.execute(
            "SELECT * FROM structural_voids WHERE task = ?", (task,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM structural_voids").fetchall()
    conn.close()
    return rows


def _load_maturation(kb_path: Path, root: Path) -> MaturationSummary:
    """Load maturation pipeline status from maturation.jsonl."""
    maturation_path = root / "maturation.jsonl"
    if not maturation_path.exists():
        return MaturationSummary(0, 0, 0, [], [])

    l0_cells = 0
    l1_cells = 0
    l2_cells = 0
    l1_keys = []
    l2_keys = []

    for line in maturation_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        maturity = row.get("maturity", "")
        cell = row.get("cell", "")
        if maturity == "l1":
            l1_cells += 1
            if cell:
                l1_keys.append(cell)
        elif maturity == "l2":
            l2_cells += 1
            if cell:
                l2_keys.append(cell)
        elif maturity == "l0":
            l0_cells += 1

    return MaturationSummary(l0_cells, l1_cells, l2_cells, l1_keys, l2_keys)


def _load_defects(root: Path) -> DefectSummary:
    """Load defect quarantine status."""
    from computronium.autoscientist.defects import (
        quarantined_cells,
        read_defects,
    )

    defects_path = root / "runtime_defects.jsonl"
    if not defects_path.exists():
        return DefectSummary(0, 0, 0, {})

    records = read_defects(defects_path)
    q_cells = quarantined_cells(records)

    open_defects = sum(1 for r in records if r.status == "open")
    resolved_defects = sum(1 for r in records if r.status == "resolved")
    defect_types: dict[str, int] = Counter(r.error_class for r in records)

    return DefectSummary(
        open_defects=open_defects,
        resolved_defects=resolved_defects,
        quarantined_cells=len(q_cells),
        defect_types=dict(defect_types),
    )


def _parse_experiment_row(row: sqlite3.Row) -> dict | None:
    """Parse a single experiment row into cell data dict."""
    hp = json.loads(row["hyperparameters"]) if row["hyperparameters"] else {}
    metrics = json.loads(row["metrics"]) if row["metrics"] else {}
    tags = json.loads(row["tags"]) if row["tags"] else []

    dynamics = hp.get("dynamics", "")
    credit = hp.get("credit", "")
    update = hp.get("update", "")
    geometry = hp.get("geometry", {})
    if not isinstance(geometry, dict):
        geometry = {}
    topology = geometry.get("topology_type", "feedforward")

    if not (dynamics and credit and update):
        return None

    key = f"{dynamics}|{credit}|{update}|{topology}"

    maturity = "l0"
    for tag in tags:
        if tag.startswith("maturity:"):
            maturity = tag.split(":", 1)[1]
            break

    return {
        "key": key,
        "dynamics": dynamics,
        "credit": credit,
        "update": update,
        "topology": topology,
        "maturity": maturity,
        "accuracy": metrics.get("final_accuracy", 0.0),
        "walltime_s": metrics.get("walltime_s", 0.0),
        "param_count": metrics.get("param_count", 0),
        "flops": metrics.get("flops", 0.0),
        "memory_mb": metrics.get("memory_mb", 0.0),
        "energy_per_step": metrics.get("energy_per_step", 0.0),
        "latency_ms": metrics.get("latency_ms", 0.0),
        "bp_deficit": metrics.get("bp_deficit", 0.0),
        "spectral_radius": metrics.get("spectral_radius", 0.0),
        "nan_loss": metrics.get("nan_loss", False),
    }


def _build_per_cell_best(experiments: list[sqlite3.Row]) -> list[dict]:
    """Group experiments by cell key and select best per cell."""
    by_key: dict[str, list[dict]] = {}
    for row in experiments:
        cell = _parse_experiment_row(row)
        if cell is None:
            continue
        by_key.setdefault(cell["key"], []).append(cell)

    per_cell = []
    for group in by_key.values():
        if any(m.get("nan_loss") for m in group):
            continue
        best = max(group, key=lambda g: g["accuracy"])
        per_cell.append(best)
    return per_cell


def _extract_pareto_front(
    experiments: list[sqlite3.Row],
    objectives: list[str],
    maturation: MaturationSummary,
) -> list[ParetoPoint]:
    """Extract Pareto front from experiment entries."""
    import pandas as pd

    from computronium.analysis.dominance import pareto_top
    from computronium.autoscientist.objectives import parse_objectives

    if not experiments:
        return []

    obj_specs = parse_objectives(",".join(objectives))
    per_cell = _build_per_cell_best(experiments)

    if not per_cell:
        return []

    df = pd.DataFrame(per_cell)
    obj_names = [o for o in objectives if o in df.columns]
    if len(obj_names) < 2:
        return []

    front_df = pareto_top(df, k=len(df), objectives=obj_specs)

    points = []
    for _, row in front_df.iterrows():
        points.append(
            ParetoPoint(
                key=row["key"],
                dynamics=row["dynamics"],
                credit=row["credit"],
                update=row["update"],
                topology=row["topology"],
                accuracy=row["accuracy"],
                walltime_s=row["walltime_s"],
                param_count=int(row["param_count"]),
                flops=row["flops"],
                memory_mb=row["memory_mb"],
                energy_per_step=row["energy_per_step"],
                latency_ms=row["latency_ms"],
                bp_deficit=row["bp_deficit"],
                spectral_radius=row["spectral_radius"],
                maturity=row["maturity"],
            )
        )
    return points


def _extract_voids(kb_path: Path, task: str | None) -> list[VoidSummary]:
    """Extract void breakdown by category."""
    rows = _load_structural_voids(kb_path, task)
    by_category: dict[str, list[str]] = {}
    for row in rows:
        cat = row["category"]
        key = f"{row['dynamics']}|{row['credit']}|{row['update']}|{row['topology']}"
        by_category.setdefault(cat, []).append(key)

    summaries = []
    for cat, keys in sorted(by_category.items(), key=lambda x: -len(x[1])):
        summaries.append(
            VoidSummary(
                category=cat,
                count=len(keys),
                examples=sorted(keys)[:5],
            )
        )
    return summaries


def _extract_clamps(kb_path: Path, task: str | None) -> list[ClampSummary]:
    """Extract energy clamp frequency by (dynamics, credit, update)."""
    conn = _connect(kb_path)
    if task:
        rows = conn.execute(
            "SELECT * FROM knowledge WHERE topic LIKE ? AND source = 'experiment'",
            (f"experiment:{task}",),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM knowledge WHERE topic LIKE 'experiment:%' AND source = 'experiment'"
        ).fetchall()
    conn.close()

    by_triple: dict[tuple[str, str, str], dict] = {}
    for row in rows:
        hp = json.loads(row["hyperparameters"]) if row["hyperparameters"] else {}
        metrics = json.loads(row["metrics"]) if row["metrics"] else {}

        dynamics = hp.get("dynamics", "")
        credit = hp.get("credit", "")
        update = hp.get("update", "")

        if not (dynamics and credit and update):
            continue

        triple = (dynamics, credit, update)
        clamped = metrics.get("energy_clamp_count", 0) > 0

        if triple not in by_triple:
            by_triple[triple] = {"total": 0, "clamped": 0}
        by_triple[triple]["total"] += 1
        if clamped:
            by_triple[triple]["clamped"] += 1

    summaries = []
    for (dynamics, credit, update), counts in sorted(
        by_triple.items(), key=lambda x: -x[1]["clamped"] / max(x[1]["total"], 1)
    ):
        total = counts["total"]
        clamped = counts["clamped"]
        summaries.append(
            ClampSummary(
                dynamics=dynamics,
                credit=credit,
                update=update,
                total_cells=total,
                clamp_count=clamped,
                clamp_rate=clamped / total if total > 0 else 0.0,
            )
        )
    return summaries


def _extract_walltimes(kb_path: Path, task: str | None) -> list[WalltimeSummary]:
    """Extract walltime statistics by dynamics family."""
    conn = _connect(kb_path)
    if task:
        rows = conn.execute(
            "SELECT * FROM knowledge WHERE topic LIKE ? AND source = 'experiment'",
            (f"experiment:{task}",),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM knowledge WHERE topic LIKE 'experiment:%' AND source = 'experiment'"
        ).fetchall()
    conn.close()

    by_dynamics: dict[str, list[float]] = {}
    for row in rows:
        hp = json.loads(row["hyperparameters"]) if row["hyperparameters"] else {}
        metrics = json.loads(row["metrics"]) if row["metrics"] else {}

        dynamics = hp.get("dynamics", "")
        walltime = metrics.get("walltime_s", 0.0)

        if dynamics and walltime > 0:
            by_dynamics.setdefault(dynamics, []).append(walltime)

    summaries = []
    for dynamics, times in sorted(
        by_dynamics.items(), key=lambda x: -sum(x[1]) / len(x[1])
    ):
        summaries.append(
            WalltimeSummary(
                dynamics=dynamics,
                cells=len(times),
                mean_walltime_s=sum(times) / len(times),
                min_walltime_s=min(times),
                max_walltime_s=max(times),
            )
        )
    return summaries


def _get_kb_stats(
    kb_path: Path,
    *,
    experiments: Sequence[sqlite3.Row],
) -> dict:
    """Get KB statistics, with the experiment count scoped to the report's task.

    The void count stays a table total: ``structural_voids`` is per-campaign
    root, one task per root, and the report renders deduplicated summaries.
    """
    conn = _connect(kb_path)
    stats = {}
    stats["total_entries"] = conn.execute("SELECT COUNT(*) FROM knowledge").fetchone()[
        0
    ]
    stats["total_experiments"] = len(experiments)
    stats["total_voids"] = conn.execute(
        "SELECT COUNT(*) FROM structural_voids"
    ).fetchone()[0]
    stats["by_model_family"] = dict(
        conn.execute(
            "SELECT model_family, COUNT(*) FROM knowledge GROUP BY model_family"
        ).fetchall()
    )
    stats["by_source"] = dict(
        conn.execute(
            "SELECT source, COUNT(*) FROM knowledge GROUP BY source"
        ).fetchall()
    )
    conn.close()
    return stats


# ---- Main entry point --------------------------------------------------------


def build_kb_report(
    root: Path,
    task: str = "mnist",
    objectives: list[str] | None = None,
) -> KBReport:
    """Build the complete KB-based campaign report."""
    kb_path = root / "kb.sqlite"
    if not kb_path.exists():
        raise FileNotFoundError(f"KB not found: {kb_path}")

    if objectives is None:
        objectives = ["accuracy", "walltime_s", "param_count"]

    maturation = _load_maturation(kb_path, root)
    defects = _load_defects(root)
    experiments = _load_experiments(kb_path, task)
    pareto = _extract_pareto_front(experiments, objectives, maturation)
    voids = _extract_voids(kb_path, task)
    clamps = _extract_clamps(kb_path, task)
    walltimes = _extract_walltimes(kb_path, task)
    kb_stats = _get_kb_stats(kb_path, experiments=experiments)

    return KBReport(
        campaign_root=str(root),
        task=task,
        objectives=objectives,
        pareto_front=pareto,
        voids=voids,
        clamps=clamps,
        walltimes=walltimes,
        maturation=maturation,
        defects=defects,
        kb_stats=kb_stats,
    )


# ---- HTML rendering ----------------------------------------------------------


_CSS = """\
body { font-family: system-ui, sans-serif; margin: 2rem auto; max-width: 80rem;
  color: #1a1a1a; line-height: 1.5; }
h1 { font-size: 1.5rem; border-bottom: 2px solid #333; padding-bottom: 0.5rem; }
h2 { font-size: 1.2rem; margin-top: 2rem; color: #333; }
h3 { font-size: 1.0rem; margin-top: 1.5rem; color: #555; }
table { border-collapse: collapse; margin: 0.5rem 0; font-size: 0.85rem; width: 100%; }
th, td { border: 1px solid #ccc; padding: 0.3rem 0.6rem; text-align: left; }
th { background: #f4f4f4; position: sticky; top: 0; }
.num { text-align: right; font-variant-numeric: tabular-nums; }
code { background: #f5f5f5; padding: 0.1rem 0.3rem; border-radius: 3px; font-size: 0.85em; }
.badge { display: inline-block; padding: 0.1rem 0.5rem; border-radius: 3px; font-size: 0.75rem; font-weight: bold; }
.badge-l0 { background: #e3f2fd; color: #1565c0; }
.badge-l1 { background: #fff3e0; color: #e65100; }
.badge-l2 { background: #e8f5e9; color: #2e7d32; }
.ok { color: #0a7d28; } .warn { color: #b3261e; }
p.note { color: #555; max-width: 90ch; font-size: 0.9rem; }
.section { margin-bottom: 2rem; }
"""


def _fmt(val: float, precision: int = 3) -> str:
    if val == 0:
        return "0"
    if abs(val) < 0.001:
        return f"{val:.2e}"
    return f"{val:.{precision}f}"


def _badge(maturity: str) -> str:
    return f'<span class="badge badge-{maturity}">{maturity}</span>'


def _table(headers: list[str], rows: list[list[str]]) -> list[str]:
    return [
        "<table>",
        "<thead><tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr></thead>",
        "<tbody>",
        *(
            "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
            for row in rows
        ),
        "</tbody>",
        "</table>",
    ]


def _render_pareto_table(pareto_front: list[ParetoPoint]) -> list[str]:
    if not pareto_front:
        return ["<p>No Pareto data available.</p>"]
    return _table(
        [
            "Key",
            "Dynamics",
            "Credit",
            "Update",
            "Topology",
            "Maturity",
            "Accuracy",
            "Walltime (s)",
            "Params",
            "FLOPs",
            "Memory (MB)",
            "Energy/step",
            "Latency (ms)",
            "BP Deficit",
            "Spectral ρ",
        ],
        [
            [
                f"<code>{escape(p.key)}</code>",
                escape(p.dynamics),
                escape(p.credit),
                escape(p.update),
                escape(p.topology),
                _badge(p.maturity),
                _fmt(p.accuracy, 4),
                _fmt(p.walltime_s, 2),
                f"{p.param_count:,}",
                _fmt(p.flops),
                _fmt(p.memory_mb, 1),
                _fmt(p.energy_per_step, 4),
                _fmt(p.latency_ms, 1),
                _fmt(p.bp_deficit, 4),
                _fmt(p.spectral_radius, 4),
            ]
            for p in pareto_front
        ],
    )


def _render_voids_table(voids: list[VoidSummary]) -> list[str]:
    if not voids:
        return ["<p>No voids recorded.</p>"]
    return _table(
        ["Category", "Count", "Examples"],
        [
            [
                escape(v.category),
                str(v.count),
                ", ".join(f"<code>{escape(e)}</code>" for e in v.examples[:3])
                + ("..." if len(v.examples) > 3 else ""),
            ]
            for v in voids
        ],
    )


def _render_clamps_table(clamps: list[ClampSummary]) -> list[str]:
    if not clamps:
        return ["<p>No clamp data available.</p>"]
    return _table(
        ["Dynamics", "Credit", "Update", "Cells", "Clamps", "Rate"],
        [
            [
                escape(c.dynamics),
                escape(c.credit),
                escape(c.update),
                str(c.total_cells),
                str(c.clamp_count),
                f"{c.clamp_rate:.1%}" + (" ⚠️" if c.clamp_rate > 0.2 else ""),
            ]
            for c in clamps
        ],
    )


def _render_walltimes_table(walltimes: list[WalltimeSummary]) -> list[str]:
    if not walltimes:
        return ["<p>No walltime data available.</p>"]
    return _table(
        ["Dynamics", "Cells", "Mean (s)", "Min (s)", "Max (s)"],
        [
            [
                escape(w.dynamics),
                str(w.cells),
                _fmt(w.mean_walltime_s, 2),
                _fmt(w.min_walltime_s, 2),
                _fmt(w.max_walltime_s, 2),
            ]
            for w in walltimes
        ],
    )


def _render_defects_table(defect_types: dict[str, int]) -> list[str]:
    if not defect_types:
        return ["<p>No defects recorded.</p>"]
    return _table(
        ["Error Class", "Count"],
        [
            [escape(k), str(v)]
            for k, v in sorted(defect_types.items(), key=lambda x: -x[1])
        ],
    )


def _render_html(report: KBReport) -> str:
    parts = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        "<title>KB Campaign Report</title>",
        f"<style>{_CSS}</style>",
        "</head>",
        "<body>",
        "<h1>KB Campaign Report</h1>",
        '<p class="note">Generated from continuous discovery KB at '
        f"<code>{escape(report.campaign_root)}</code> for task "
        f"<code>{escape(report.task)}</code>.</p>",
        # Summary
        '<section class="section" id="summary">',
        "<h2>Summary</h2>",
        *_table(
            ["Metric", "Value"],
            [
                ["KB entries", str(report.kb_stats.get("total_entries", 0))],
                ["Experiments", str(report.kb_stats.get("total_experiments", 0))],
                ["Structural voids", str(report.kb_stats.get("total_voids", 0))],
                ["Pareto front size", str(len(report.pareto_front))],
                ["L0 cells", str(report.maturation.l0_cells)],
                ["L1 cells", str(report.maturation.l1_cells)],
                ["L2 cells", str(report.maturation.l2_cells)],
                ["Open defects", str(report.defects.open_defects)],
                ["Quarantined cells", str(report.defects.quarantined_cells)],
            ],
        ),
        "</section>",
        # Pareto Front
        '<section class="section" id="pareto">',
        "<h2>Pareto Front</h2>",
        f"<p>Objectives: {', '.join(report.objectives)}</p>",
        *_render_pareto_table(report.pareto_front),
        "</section>",
        # Voids
        '<section class="section" id="voids">',
        "<h2>Structural Voids by Category</h2>",
        *_render_voids_table(report.voids),
        "</section>",
        # Energy Clamps
        '<section class="section" id="clamps">',
        "<h2>Energy Clamp Frequency</h2>",
        '<p class="note">Clamp rate > 20% suggests step_size too high for that (dynamics, credit, update) combo.</p>',
        *_render_clamps_table(report.clamps),
        "</section>",
        # Walltimes
        '<section class="section" id="walltimes">',
        "<h2>Walltime by Dynamics Family</h2>",
        *_render_walltimes_table(report.walltimes),
        "</section>",
        # Maturation
        '<section class="section" id="maturation">',
        "<h2>Maturation Pipeline</h2>",
        *_table(
            ["Stage", "Count", "Cells"],
            [
                ["L0 (burst)", str(report.maturation.l0_cells), "—"],
                [
                    "L1 (epochs=3)",
                    str(report.maturation.l1_cells),
                    ", ".join(
                        f"<code>{escape(k)}</code>"
                        for k in report.maturation.l1_keys[:5]
                    )
                    + ("..." if len(report.maturation.l1_keys) > 5 else ""),
                ],
                [
                    "L2 (full epochs × seeds)",
                    str(report.maturation.l2_cells),
                    ", ".join(
                        f"<code>{escape(k)}</code>"
                        for k in report.maturation.l2_keys[:5]
                    )
                    + ("..." if len(report.maturation.l2_keys) > 5 else ""),
                ],
            ],
        ),
        "</section>",
        # Defects
        '<section class="section" id="defects">',
        "<h2>Defect Quarantine</h2>",
        *_table(
            ["Metric", "Value"],
            [
                ["Open defects", str(report.defects.open_defects)],
                ["Resolved defects", str(report.defects.resolved_defects)],
                ["Quarantined cells", str(report.defects.quarantined_cells)],
            ],
        ),
        "<h3>Defect Types</h3>",
        *_render_defects_table(report.defects.defect_types),
        "</section>",
        "</body>",
        "</html>",
        "",
    ]
    return "\n".join(parts)


__all__ = [
    "ClampSummary",
    "DefectSummary",
    "KBReport",
    "MaturationSummary",
    "ParetoPoint",
    "VoidSummary",
    "WalltimeSummary",
    "build_kb_report",
]
