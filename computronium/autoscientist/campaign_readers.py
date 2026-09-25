"""Read-only campaign-artifact readers (heartbeat, liveness, cost, maturation,
front history, voids, graveyard, outcome badges).

These loaders are the single read path over a continuous-discovery campaign
root: every function is read-only (never creates or writes) and returns plain
rows/dicts for downstream assembly. They back
`autoscientist.report.generate_report` (the daemon's campaign summary) and the
daemon liveness probe. Rendering lives elsewhere.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, Any, cast

from computronium.autoscientist.objectives import (
    DEFAULT_OBJECTIVES,
    ObjectiveSpec,
)

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger("campaign_readers")

MESSAGE_HEAD_CHARS = 80

HEARTBEAT_NAME = "heartbeat.json"

HEARTBEAT_STALE_S = 10.0

LEARNED_ACC_THRESHOLD = 0.5  # task-specific; MNIST chance=0.1

MARGINAL_ACC_THRESHOLD = 0.15  # above chance but below learned


class OutcomeBadge(StrEnum):
    """§3.3 per-cell outcome badges."""

    LEARNED = "LEARNED"
    MARGINAL = "MARGINAL"
    CHANCE = "CHANCE"  # below marginal threshold
    DIVERGED = "DIVERGED"  # nan_loss
    DEFECT = "DEFECT"  # runtime crash, quarantined
    VOID = "VOID"  # gate-rejected
    PARETO_OPTIMAL = "PARETO_OPTIMAL"  # multi-objective: on Pareto front
    PARETO_NEAR = "PARETO_NEAR"  # multi-objective: near Pareto front
    DOMINATED = "DOMINATED"  # multi-objective: dominated


@dataclass(frozen=True, slots=True)
class OutcomeStyle:
    icon: str
    color: str
    label: str


_OUTCOME_STYLES: dict[OutcomeBadge, OutcomeStyle] = {
    OutcomeBadge.LEARNED: OutcomeStyle("🟢", "green", "LEARNED"),
    OutcomeBadge.MARGINAL: OutcomeStyle("🟡", "amber", "MARGINAL"),
    OutcomeBadge.CHANCE: OutcomeStyle("⚪", "grey", "CHANCE"),
    OutcomeBadge.DIVERGED: OutcomeStyle("🔴", "red", "DIVERGED"),
    OutcomeBadge.DEFECT: OutcomeStyle("⚫", "red", "DEFECT"),
    OutcomeBadge.VOID: OutcomeStyle("⬜", "grey", "VOID"),
    OutcomeBadge.PARETO_OPTIMAL: OutcomeStyle("★", "gold", "PARETO OPTIMAL"),
    OutcomeBadge.PARETO_NEAR: OutcomeStyle("✦", "yellow", "PARETO NEAR"),
    OutcomeBadge.DOMINATED: OutcomeStyle("⊘", "grey", "DOMINATED"),
}


def outcome_badge_from_metrics(
    accuracy: float | None = None,
    nan_loss: bool = False,
    is_defect: bool = False,
    is_void: bool = False,
) -> OutcomeBadge:
    """Determine outcome badge from cell metrics (accuracy-only, legacy)."""
    if is_void:
        badge = OutcomeBadge.VOID
    elif is_defect:
        badge = OutcomeBadge.DEFECT
    elif nan_loss:
        badge = OutcomeBadge.DIVERGED
    elif accuracy is None:
        badge = OutcomeBadge.CHANCE
    elif accuracy >= LEARNED_ACC_THRESHOLD:
        badge = OutcomeBadge.LEARNED
    elif accuracy >= MARGINAL_ACC_THRESHOLD:
        badge = OutcomeBadge.MARGINAL
    else:
        badge = OutcomeBadge.CHANCE
    return badge


def outcome_style(badge: OutcomeBadge) -> OutcomeStyle:
    return _OUTCOME_STYLES[badge]


def read_heartbeat(root: Path) -> dict[str, object] | None:
    """Parse ``heartbeat.json`` (the daemon's liveness beacon), if present."""

    try:
        return cast(
            "dict[str, object] | None",
            json.loads((root / HEARTBEAT_NAME).read_text(encoding="utf-8")),
        )
    except OSError, ValueError:
        return None


@dataclass(frozen=True, slots=True)
class Liveness:
    """§2.2 badge payload: dual-source (heartbeat freshness + API reach)."""

    label: str
    color: str
    detail: str


_STATE_COLORS = {
    "idle": ("● IDLE — ready, no campaign active", "green"),
    "proposing": ("● RUNNING", "green"),
    "training": ("● RUNNING", "green"),
    "sleeping": ("● SLEEPING", "yellow"),
    "paused": ("● PAUSED", "amber"),
    "stopped": ("● STOPPED", "grey"),
}


def liveness(root: Path, daemon_reachable: bool, now: float | None = None) -> Liveness:
    """Badge state from the heartbeat artifact; the API adds connection
    context only — the heartbeat alone drives the landscape (hybrid
    transport, §0), so a fresh heartbeat with a dead API still renders."""
    heartbeat = read_heartbeat(root)
    if heartbeat is None:
        return Liveness(
            "● OFFLINE", "grey", "no heartbeat — daemon not running on this root"
        )
    now = time.time() if now is None else now
    updated_at = heartbeat.get("updated_at")
    if not isinstance(updated_at, int | float) or now - updated_at > HEARTBEAT_STALE_S:
        return Liveness("● CONNECTION LOST", "red", "heartbeat stale (>10 s)")
    state = str(heartbeat.get("state", ""))
    label, color = _STATE_COLORS.get(state, (f"● {state.upper()}", "grey"))
    if state in {"proposing", "training"}:
        label = "● RUNNING"
    detail_parts = [
        f"pid {heartbeat.get('pid')}",
        f"cells {heartbeat.get('cell_index')}",
        f"burst {heartbeat.get('burst') or '—'}",
    ]
    if not daemon_reachable:
        detail_parts.append("API unreachable (artifact-polling mode)")
    return Liveness(label, color, " · ".join(detail_parts))


class DaemonClient:
    """Minimal REST client for the daemon lifecycle API (urllib, 1 s timeout).

    Every call returns ``None``/``False`` when the daemon is unreachable —
    callers degrade to artifact reads, never error."""

    def __init__(self, base_url: str, timeout: float = 1.0) -> None:
        self._base = base_url.rstrip("/")
        self._timeout = timeout

    def get_state(self) -> dict[str, object] | None:
        import urllib.request

        try:
            with urllib.request.urlopen(  # ruff: ignore[suspicious-url-open-usage] (base_url is operator-supplied)
                f"{self._base}/state", timeout=self._timeout
            ) as response:
                return cast("dict[str, object] | None", json.loads(response.read()))
        except OSError, ValueError:
            return None

    def control(self, action: str) -> bool:
        import urllib.request

        request = urllib.request.Request(  # ruff: ignore[suspicious-url-open-usage] (operator-supplied base)
            f"{self._base}/control/{action}",
            method="POST",
            data=b"",
        )
        try:
            urllib.request.urlopen(  # ruff: ignore[suspicious-url-open-usage] (base_url is operator-supplied)
                request, timeout=self._timeout
            ).read()
        except OSError:
            return False
        return True


def _measured_cells(root: Path) -> list[Any]:
    """Private-but-shared `_CellRow` rows from the KB (broad_map owns the
    schema; readers only consume)."""
    from computronium.autoscientist.broad_map import _load_measured_cells

    try:
        return _load_measured_cells(root / "kb.sqlite")
    except Exception:  # Corrupt or missing KB -> empty, not crash
        return []


def graveyard_rows(root: Path) -> list[dict[str, object]]:
    """§4.3: NaN-diverged cells grouped per axis primitive to expose
    patterns (e.g. '80% of diverged cells use PhotonicSubstrate')."""
    from collections import Counter

    cells = _measured_cells(root)
    diverged = [row for row in cells if row.nan_loss]  # type: ignore[attr-defined]
    if not diverged:
        return []
    rows: list[dict[str, object]] = []
    for axis in ("dynamics", "credit", "update", "topology"):
        total: Counter[str] = Counter(
            str(getattr(row, axis))
            for row in cells  # type: ignore[attr-defined]
        )
        bad: Counter[str] = Counter(
            str(getattr(row, axis))
            for row in diverged  # type: ignore[attr-defined]
        )
        for primitive, n in bad.most_common():
            badge = outcome_badge_from_metrics(nan_loss=True)
            style = outcome_style(badge)
            rows.append({
                "axis": axis,
                "primitive": primitive,
                "outcome": style.label,
                "outcome_icon": style.icon,
                "diverged": n,
                "measured": total[primitive],
                "share": f"{100.0 * n / max(total[primitive], 1):.0f}%",
            })
    return rows


def void_summary_rows(root: Path) -> list[dict[str, object]]:
    """§4.3: structural voids by rejection category — boundaries, not
    failures."""

    badge = outcome_badge_from_metrics(is_void=True)
    style = outcome_style(badge)
    by_category: dict[str, list[str]] = {}
    path = root / "structural_voids.jsonl"
    if not path.exists():
        return []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record: dict[str, Any] = json.loads(line)
        except json.JSONDecodeError:
            logger.warning("Skipping malformed void line in %s", path)
            continue
        by_category.setdefault(str(record.get("category", "unknown")), []).append(
            str(record.get("dynamics", "?"))
            + " × "
            + str(record.get("credit", "?"))
            + " × "
            + str(record.get("update", "?"))
        )
    return [
        {
            "category": category,
            "outcome": style.label,
            "outcome_icon": style.icon,
            "count": len(group),
            "example": group[0][:MESSAGE_HEAD_CHARS],
        }
        for category, group in sorted(by_category.items(), key=lambda kv: -len(kv[1]))
    ]


def front_history_rows(
    root: Path,
    sample_points: int = 5,
    k: int = 3,
    objectives: tuple[ObjectiveSpec, ...] = DEFAULT_OBJECTIVES,
) -> list[dict[str, object]]:
    """§4.2: the Pareto front at sampled burst cutoffs; `new_front` marks
    cells that expanded the front (★). Uses configurable objectives."""
    import pandas as pd

    from computronium.analysis.dominance import pareto_top

    cells = _measured_cells(root)
    bursts = sorted({b for row in cells for b in row.bursts})  # type: ignore[attr-defined]
    if not bursts:
        return []
    cutpoints = sorted({
        bursts[
            min(
                round(i * (len(bursts) - 1) / max(sample_points - 1, 1)),
                len(bursts) - 1,
            )
        ]
        for i in range(sample_points)
    })
    rows: list[dict[str, object]] = []
    previous: set[str] = set()
    for cutoff in cutpoints:
        cumulative = [
            row
            for row in cells
            if (bursts_list := list(row.bursts) if hasattr(row, "bursts") else [])
            and min(bursts_list) <= cutoff  # type: ignore[attr-defined]
        ]
        if not cumulative:
            continue
        # Convert to DataFrame for pareto_top
        df = pd.DataFrame([
            {
                "key": row.key,
                "accuracy": row.accuracy,
                "walltime_s": row.walltime,
                "param_count": float(getattr(row, "param_budget", 0)),
                "bp_deficit": getattr(row, "bp_deficit", 0.0),
                "flops": getattr(row, "flops", 0.0),
                "memory_mb": getattr(row, "memory_mb", 0.0),
                "energy_per_step": getattr(row, "energy_per_step", 0.0),
                "latency_ms": getattr(row, "latency_ms", 0.0),
                "spectral_radius": getattr(row, "spectral_radius", 0.0),
                "lyapunov_exponent": getattr(row, "lyapunov_exponent", 0.0),
                "max_singular_value": getattr(row, "max_singular_value", 0.0),
                "psi_capacity": getattr(row, "psi_capacity", 0.0),
                "consolidation_cost": getattr(row, "consolidation_cost", 0.0),
                "rewrite_rate": getattr(row, "rewrite_rate", 0.0),
                "credit_alignment": getattr(row, "credit_alignment", 0.0),
                "feedback_path_length": getattr(row, "feedback_path_length", 0.0),
                "trace_variance": getattr(row, "trace_variance", 0.0),
                "settle_horizon": getattr(row, "settle_horizon", 0.0),
                "stability_plasticity_ratio": getattr(
                    row, "stability_plasticity_ratio", 0.0
                ),
                "credit_efficiency": getattr(row, "credit_efficiency", 0.0),
            }
            for row in cumulative
            if not getattr(row, "nan_loss", False)
        ])
        if df.empty:
            continue
        top = pareto_top(df, k=len(df), objectives=objectives)
        front_keys = set(top["key"].tolist())
        for row in cumulative:
            if row.key in front_keys:
                rows.append({
                    "burst": cutoff,
                    "cell": row.key,
                    "accuracy": round(row.accuracy, 3),
                    "walltime_s": round(row.walltime, 1),
                    "new_front": "★" if row.key not in previous else "",
                })
        previous = front_keys
    return rows


def cost_stats(root: Path) -> dict[str, object]:
    """§5: projection-bar payload from the KB (honest aggregation — no
    smoothing, credit-trace-inclusive cells weighted as measured)."""
    from computronium.autoscientist.defects import read_defects

    cells = _measured_cells(root)
    walltimes = [row.walltime for row in cells if row.walltime > 0]  # type: ignore[attr-defined]
    heartbeat = read_heartbeat(root)
    target = heartbeat.get("target_cells") if heartbeat else None
    mean_walltime = sum(walltimes) / len(walltimes) if walltimes else 0.0
    remaining: float | None = None
    if isinstance(target, int) and target > len(cells):
        remaining = (target - len(cells)) * mean_walltime
    defects = read_defects(root / "runtime_defects.jsonl")
    return {
        "measured": len(cells),
        "target": target,
        "coverage_pct": (
            f"{100.0 * len(cells) / target:.0f}%"
            if isinstance(target, int) and target > 0
            else "∞ (loop mode)"
            if heartbeat and heartbeat.get("loop")
            else None
        ),
        "mean_walltime_s": round(mean_walltime, 1),
        "projected_remaining_s": (round(remaining) if remaining is not None else None),
        "defects": len({record.defect_id for record in defects}),
    }


def cost_breakdown_rows(root: Path, top: int = 8) -> list[dict[str, object]]:
    """§5.2: mean walltime per primitive on the dynamics and credit axes —
    the 40× physics-learning cost spread, surfaced honestly."""
    from collections import defaultdict

    per_axis: dict[str, dict[str, list[float]]] = {
        "dynamics": defaultdict(list),
        "credit": defaultdict(list),
    }
    cells = _measured_cells(root)
    for row in cells:
        for axis in per_axis:
            if row.walltime > 0:  # type: ignore[attr-defined]
                per_axis[axis][str(getattr(row, axis))].append(row.walltime)  # type: ignore[attr-defined]
    rows: list[dict[str, object]] = []
    for axis, means in per_axis.items():
        for primitive, times in sorted(
            means.items(), key=lambda kv: -sum(kv[1]) / len(kv[1])
        )[:top]:
            rows.append({
                "axis": axis,
                "primitive": primitive,
                "mean_walltime_s": round(sum(times) / len(times), 1),
                "n": len(times),
            })
    return rows


def maturation_rows(root: Path) -> list[dict[str, object]]:
    """§7.2: maturity rollup. Only l2 cells may back comparative claims."""
    meanings = {
        "l0": "mapping fidelity (1 epoch, 1 seed)",
        "l1": "promoted (3 epochs)",
        "l2": "claim-grade (10 epochs, 3 seeds)",
    }
    counts: dict[str, int] = {"l0": 0, "l1": 0, "l2": 0}
    for row in _measured_cells(root):
        for level in row.levels:  # type: ignore[attr-defined]
            tag = str(level).removeprefix("maturity:")
            if tag in counts:
                counts[tag] += 1
    return [
        {"level": f"maturity:{tag}", "meaning": meaning, "count": counts[tag]}
        for tag, meaning in meanings.items()
    ]


def health_stats(root: Path) -> dict[str, object]:
    """Open/resolved defects, cells-per-burst rate, last-burst mean walltime."""
    from computronium.autoscientist.defects import read_defects

    records = read_defects(root / "runtime_defects.jsonl")
    last_status: dict[str, str] = {}
    for record in records:
        last_status[record.defect_id] = record.status
    open_defects = sum(1 for status in last_status.values() if status == "open")

    rows = _measured_cells(root)
    bursts = {b for r in rows for b in r.bursts}
    last_burst = max(bursts) if bursts else None
    last_walltimes = [
        r.walltime
        for r in rows
        if r.walltime > 0 and (last_burst is None or last_burst in r.bursts)
    ]
    return {
        "open_defects": open_defects,
        "resolved_defects": len(last_status) - open_defects,
        "measured_cells": len(rows),
        "nan_cells": sum(1 for r in rows if r.nan_loss),
        "bursts": len(bursts),
        "cells_per_burst": round(len(rows) / len(bursts), 1) if bursts else 0.0,
        "last_burst": last_burst,
        "last_burst_walltime_s": (
            round(sum(last_walltimes) / len(last_walltimes), 3)
            if last_walltimes
            else None
        ),
    }
