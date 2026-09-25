"""Live dashboard library (TODO29 Phase 5) — the continuous-discovery window.

Read-only: polls the campaign root's artifacts (KB, voids, defects, burst
log) on a timer and re-renders panels on change only. The polling signature
pattern is lifted from ``demo/campaign_tab.py`` (mtime_ns, size).

Instrument honesty: the map embeds a *sampled* σ_max(J) proxy and a UMAP
layout that is refit per cell-count change — the dashboard labels it as a
recomputed snapshot, never a trajectory or a stability frontier.
"""

from __future__ import annotations

import json
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Literal, cast

from computronium.autoscientist.objectives import (
    DEFAULT_OBJECTIVES,
    ObjectiveSpec,
    parse_objectives,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    import numpy as np
    import pandas as pd
    from plotly.graph_objects import Figure

logger = logging.getLogger("live_atlas")

POLL_SECONDS = 2.0
TICKER_LINES = 30
MESSAGE_HEAD_CHARS = 80
WATCHED = ("kb.sqlite", "structural_voids.jsonl", "runtime_defects.jsonl")
HEARTBEAT_NAME = "heartbeat.json"
HEARTBEAT_STALE_S = 10.0

# Event panel constants
TOAST_DURATION_S = 8.0

# Outcome badge thresholds
LEARNED_ACC_THRESHOLD = 0.5  # task-specific; MNIST chance=0.1
MARGINAL_ACC_THRESHOLD = 0.15  # above chance but below learned


@dataclass(frozen=True, slots=True)
class DashboardEvent:
    """Structured event from the stream topic for the event panel."""

    kind: str
    timestamp: float
    payload: dict[str, Any]
    # Derived for rendering
    icon: str = ""
    color: str = ""
    summary: str = ""


def _classify_event(raw: dict[str, Any], now: float) -> DashboardEvent:
    """Map a raw stream-topic event record to a rendered DashboardEvent."""
    kind = raw.get("kind", "unknown")
    payload = {k: v for k, v in raw.items() if k != "kind"}

    # Default styling
    icon, color, summary = "📋", "grey", str(raw)[:MESSAGE_HEAD_CHARS]

    handler = _EVENT_HANDLERS.get(kind)
    if handler:
        icon, color, summary = handler(payload)

    return DashboardEvent(
        kind=kind,
        timestamp=now,
        payload=payload,
        icon=icon,
        color=color,
        summary=summary,
    )


def _handle_state(payload: dict[str, Any]) -> tuple[str, str, str]:
    state = str(payload.get("state", ""))
    icons = {
        "idle": "⏸",
        "proposing": "🔍",
        "training": "⚙️",
        "sleeping": "😴",
        "paused": "⏸",
        "stopped": "⏹",
    }
    colors = {
        "idle": "grey",
        "proposing": "blue",
        "training": "green",
        "sleeping": "amber",
        "paused": "orange",
        "stopped": "red",
    }
    return icons.get(state, "📋"), colors.get(state, "grey"), f"State → {state.upper()}"


def _handle_daemon_started(payload: dict[str, Any]) -> tuple[str, str, str]:
    return "🚀", "green", f"Daemon started on {payload.get('root', '?')}"


def _handle_daemon_stopped(_payload: dict[str, Any]) -> tuple[str, str, str]:
    return "🛑", "red", "Daemon stopped gracefully"


def _handle_burst_finished(payload: dict[str, Any]) -> tuple[str, str, str]:
    reason = payload.get("stop_reason", "?")
    icons = {
        "target": "🎯",
        "paused": "⏸",
        "stopped": "⏹",
        "exhausted": "🏁",
        "budget": "💰",
    }
    colors = {
        "target": "green",
        "paused": "amber",
        "stopped": "red",
        "exhausted": "blue",
        "budget": "orange",
    }
    return (
        icons.get(reason, "✅"),
        colors.get(reason, "green"),
        f"Burst finished: {reason}",
    )


def _handle_campaign_complete(_payload: dict[str, Any]) -> tuple[str, str, str]:
    return "🏁", "green", "Campaign complete — target reached"


def _handle_alert(payload: dict[str, Any]) -> tuple[str, str, str]:
    alert_kind = payload.get("alert_kind", "?")
    icons = {"breakthrough": "★", "cascade": "🔥", "completion": "🏁"}
    colors = {"breakthrough": "green", "cascade": "red", "completion": "blue"}
    icon = icons.get(alert_kind, "⚠️")
    color = colors.get(alert_kind, "orange")
    summary = f"{payload.get('title', alert_kind)}: {payload.get('body', '')}"
    return icon, color, summary


def _handle_report(payload: dict[str, Any]) -> tuple[str, str, str]:
    return "📄", "blue", f"Report generated: {payload.get('path', '?')}"


def _handle_cell_completed(payload: dict[str, Any]) -> tuple[str, str, str]:
    cell = payload.get("cell", "?")
    acc = payload.get("val_acc", payload.get("accuracy"))
    nan_loss = payload.get("nan_loss", False)
    badge = outcome_badge_from_metrics(accuracy=acc, nan_loss=nan_loss)
    style = outcome_style(badge)
    acc_str = f"{acc:.3f}" if isinstance(acc, int | float) else "?"
    return style.icon, style.color, f"{style.label}: {cell} (acc={acc_str})"


def _handle_defect_quarantined(payload: dict[str, Any]) -> tuple[str, str, str]:
    return (
        "🦠",
        "red",
        f"Defect quarantined: {payload.get('defect_id', '?')} — {payload.get('message', '')[:50]}",
    )


def _handle_proposal_batch(payload: dict[str, Any]) -> tuple[str, str, str]:
    n = payload.get("n_proposals", payload.get("count", "?"))
    quarantined = payload.get("quarantined", 0)
    voids = payload.get("voids_pruned", 0)
    return (
        "📦",
        "blue",
        f"Proposed {n} cells | {quarantined} quarantined | {voids} voids",
    )


_EVENT_HANDLERS: dict[str, Callable[[dict[str, Any]], tuple[str, str, str]]] = {
    "state": _handle_state,
    "daemon_started": _handle_daemon_started,
    "daemon_stopped": _handle_daemon_stopped,
    "burst_finished": _handle_burst_finished,
    "campaign_complete": _handle_campaign_complete,
    "alert": _handle_alert,
    "report": _handle_report,
    "cell_completed": _handle_cell_completed,
    "defect_quarantined": _handle_defect_quarantined,
    "proposal_batch": _handle_proposal_batch,
}


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


def outcome_badge_multi_objective(
    metrics: dict[str, float],
    objectives: tuple[ObjectiveSpec, ...],
    pareto_front_keys: set[str] | None = None,
    cell_key: str | None = None,
    *,
    nan_loss: bool = False,
    is_defect: bool = False,
    is_void: bool = False,
) -> OutcomeBadge:
    """Determine outcome badge from multi-objective metrics.

    Uses configurable Pareto-front membership and per-objective thresholds.

    Args:
        metrics: Cell metrics including all configured objectives.
        objectives: Configured objectives for this campaign.
        pareto_front_keys: Set of cell keys on the current Pareto front.
        cell_key: This cell's key (for Pareto membership check).
        nan_loss: Whether the cell diverged.
        is_defect: Whether the cell hit a runtime defect.
        is_void: Whether the cell was gate-rejected.

    Returns:
        Multi-objective outcome badge.
    """
    if is_void:
        return OutcomeBadge.VOID
    if is_defect:
        return OutcomeBadge.DEFECT
    if nan_loss:
        return OutcomeBadge.DIVERGED
    if pareto_front_keys is not None and cell_key is not None:
        if cell_key in pareto_front_keys:
            return OutcomeBadge.PARETO_OPTIMAL
        # Check if near Pareto (dominated by ≤1 cell)
        # For now, just return DOMINATED; near detection would need
        # dominance computation per cell
        return OutcomeBadge.DOMINATED
    # Fallback to accuracy-only if no Pareto info
    acc = metrics.get("accuracy", metrics.get("final_accuracy"))
    return outcome_badge_from_metrics(accuracy=acc, nan_loss=nan_loss)


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


def lifecycle_buttons(state: str | None) -> tuple[str, ...]:
    """§2.1 — the only three controls that may ever exist."""
    if state is None or state in {"idle", "stopped"}:
        return ("start",)
    if state == "paused":
        return ("resume", "stop")
    return ("pause", "stop")


class DaemonClient:
    """Minimal REST client for the daemon lifecycle API (urllib, 1 s timeout).

    Every call returns ``None``/``False`` when the daemon is unreachable —
    the dashboard degrades to artifact-polling, never errors."""

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


def watch_signature(root: Path) -> tuple[tuple[int, int], ...]:
    """Combined (mtime_ns, size) change signature over the watched
    artifacts — empty tuple until any artifact exists."""
    stamps: list[tuple[int, int]] = []
    for name in WATCHED:
        try:
            stat = (root / name).stat()
        except OSError:
            continue
        stamps.append((stat.st_mtime_ns, stat.st_size))
    return tuple(stamps)


def defect_funnel_rows(defects_path: Path) -> list[dict[str, object]]:
    """The bug-bounty board: one row per defect_id — count, affected cells,
    open/resolved, last-seen, message head."""
    from computronium.autoscientist.defects import DefectRecord, read_defects

    by_id: dict[str, list[DefectRecord]] = {}
    for record in read_defects(defects_path):
        by_id.setdefault(record.defect_id, []).append(record)
    rows: list[dict[str, object]] = []
    for did, group in by_id.items():
        last = max(group, key=lambda r: r.timestamp)
        rows.append({
            "defect_id": did,
            "count": len(group),
            "cells": len({r.cell for r in group}),
            "status": last.status,
            "error_class": last.error_class,
            "last_seen": round(last.timestamp, 1),
            "message": last.message[:MESSAGE_HEAD_CHARS],
        })
    rows.sort(
        key=lambda r: (
            0 if r["status"] == "open" else 1,
            -int(r["count"]) if isinstance(r["count"], int) else 0,
        )
    )
    return rows


def _measured_cells(root: Path) -> list[Any]:
    """Private-but-shared `_CellRow` rows from the KB (broad_map owns the
    schema; the dashboard only reads)."""
    from computronium.autoscientist.broad_map import _load_measured_cells

    try:
        return _load_measured_cells(root / "kb.sqlite")
    except Exception:  # Corrupt or missing KB -> empty, not crash
        return []


def coverage_by_axis(root: Path) -> list[dict[str, object]]:
    """§4.1: measured-cell count per primitive on each derivable axis —
    instantly reveals under-sampled primitives."""
    from collections import Counter

    counts: dict[str, Counter[str]] = {
        axis: Counter() for axis in ("dynamics", "credit", "update", "topology")
    }
    cells = _measured_cells(root)
    for row in cells:
        for axis in counts:
            counts[axis][str(getattr(row, axis))] += 1
    rows: list[dict[str, object]] = []
    for axis, counter in counts.items():
        for primitive, n in counter.most_common():
            rows.append({"axis": axis, "primitive": primitive, "measured": n})
    return rows


def stratum_coverage(
    root: Path, thresholds: tuple[int, ...] = (1, 3, 5)
) -> list[dict[str, object]]:
    """§4.1: how many (dynamics, credit, update) triples have ≥N cells."""
    from collections import Counter

    triples: Counter[tuple[str, str, str]] = Counter()
    for row in _measured_cells(root):
        triple = (str(row.dynamics), str(row.credit), str(row.update))  # type: ignore[attr-defined]
        triples[triple] += 1
    rows = [{"threshold": "≥1", "triples": len(triples)}]
    for t in thresholds[1:]:
        rows.append({
            "threshold": f"≥{t}",
            "triples": sum(1 for n in triples.values() if n >= t),
        })
    return rows


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


def diversity_stats(root: Path, recent_bursts: int = 3) -> dict[str, float]:
    """§4.4: budget-waste detectors over the last N bursts. The driver is
    coverage-seeded, so these catch re-measuring, not strategy collapse."""
    cells = _measured_cells(root)
    bursts = sorted({b for row in cells for b in row.bursts})  # type: ignore[attr-defined]
    if not bursts:
        return {
            "novelty_rate": 1.0,
            "stratum_repeat_rate": 0.0,
            "quarantine_pressure": 0.0,
        }
    window = set(bursts[-recent_bursts:])
    first_seen: dict[tuple[str, str, str], str] = {}
    recent_triples: list[tuple[str, str, str]] = []
    for row in cells:  # type: ignore[attr-defined]
        triple = (str(row.dynamics), str(row.credit), str(row.update))
        # Guard against empty bursts list
        row_bursts = list(row.bursts) if hasattr(row, "bursts") else []  # type: ignore[attr-defined]
        if row_bursts:
            first_seen.setdefault(triple, min(row_bursts))
        if window & set(row_bursts):
            recent_triples.append(triple)
    repeats = sum(1 for t in recent_triples if first_seen[t] not in window)
    repeat_rate = repeats / max(len(recent_triples), 1)
    from computronium.autoscientist.defects import read_defects

    defect_cells = {
        record.cell for record in read_defects(root / "runtime_defects.jsonl")
    }
    pressure = len(defect_cells) / max(len(defect_cells) + len(cells), 1)
    return {
        "novelty_rate": 1.0 - repeat_rate,
        "stratum_repeat_rate": repeat_rate,
        "quarantine_pressure": pressure,
    }


type AlertOp = Literal["<", ">"]
DIVERSITY_ALERTS: tuple[tuple[str, AlertOp, float, str], ...] = (
    ("novelty_rate", "<", 0.10, "Mostly re-measuring known space."),
    ("stratum_repeat_rate", ">", 0.80, "Exploration declining."),
    ("quarantine_pressure", ">", 0.20, "Defect-driven starvation risk."),
)


def diversity_alerts(stats: dict[str, float]) -> list[str]:
    """§4.4 — alerts only; the dashboard never intervenes."""
    alerts: list[str] = []
    for metric, op, threshold, message in DIVERSITY_ALERTS:
        value = stats.get(metric, 0.0)
        if (op == "<" and value < threshold) or (op == ">" and value > threshold):
            alerts.append(f"⚠️ {message} ({metric}={value:.2f})")
    return alerts


def front_history_rows(
    root: Path,
    sample_points: int = 5,
    k: int = 3,
    objectives: tuple[ObjectiveSpec, ...] = DEFAULT_OBJECTIVES,
) -> list[dict[str, object]]:
    """§4.2: the Pareto front at sampled burst cutoffs; `new_front` marks
    cells that expanded the front (★). Uses configurable objectives."""
    import pandas as pd

    from computronium.visualization.atlas import pareto_top

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


def pareto_strip_rows(
    root: Path, k: int = 3, objectives: tuple[ObjectiveSpec, ...] = DEFAULT_OBJECTIVES
) -> list[dict[str, object]]:
    """Current top-k Pareto cells with their instrument spokes."""
    from computronium.visualization.atlas import (
        apply_bp_deficit,
        load_cells,
        pareto_top,
    )

    ruler_table = root / "ruler_table.json"
    try:
        df = load_cells(root / "kb.sqlite")
    except Exception:  # Corrupt KB -> empty Pareto front
        return []
    if df.empty:
        return []
    df = apply_bp_deficit(df, ruler_table, None)
    if "nan_loss" in df.columns:
        df = df.query("~nan_loss")
    top = pareto_top(df, k, objectives=objectives)
    rows: list[dict[str, object]] = []
    for _, row in top.iterrows():
        rows.append({
            "label": f"{row['dynamics'][:14]}|{row['credit'][:14]}|{row['update'][:12]}|{row['topology'][:10]}",
            "accuracy": float(row["accuracy"]),  # type: ignore[arg-type]
            "bp_deficit": float(row["bp_deficit"]),  # type: ignore[arg-type]
            "credit_alignment": float(row["credit_alignment"]),  # type: ignore[arg-type]
            "settle_horizon": float(row["settle_horizon"]),  # type: ignore[arg-type]
            "walltime_s": float(row["walltime_s"]),  # type: ignore[arg-type]
        })
    return rows


def log_tail(log_path: Path | None, lines: int = TICKER_LINES) -> list[str]:
    """Tail of the burst log (empty when no log has been written yet)."""
    if log_path is None or not log_path.exists():
        return []
    with log_path.open(encoding="utf-8", errors="replace") as fh:
        return [line.rstrip("\n") for line in deque(fh, maxlen=lines)]


def resolve_log_path(root: Path, log_path: Path | None = None) -> Path | None:
    """Explicit flag wins; otherwise the newest ``continuous*.log`` from the
    daemon's two homes — ``<root>/logs/`` and the repo-level ``logs/``."""
    if log_path is not None:
        return log_path
    from pathlib import Path

    candidates = [
        p
        for logs_dir in (root / "logs", Path("logs"))
        if logs_dir.is_dir()
        for p in logs_dir.glob("continuous*.log")
    ]
    return max(candidates, key=lambda p: p.stat().st_mtime_ns) if candidates else None


class EmbedCache:
    """UMAP re-fit only when the cell count changes (a 2 s re-fit is
    wasteful, and the layout is a recomputed snapshot — not a trajectory)."""

    def __init__(self) -> None:
        self.n: int = -1
        self.layout: str | None = None
        self._coords: np.ndarray | None = None

    def coords(self, combined: pd.DataFrame) -> np.ndarray | None:
        from computronium.visualization.atlas import embed, feature_matrix

        n = len(combined)
        if n == 0:
            return None
        if self._coords is None or self.n != n:
            try:
                self._coords = embed(feature_matrix(combined))
            except (ValueError, ImportError) as error:
                logger.warning("Embedding unavailable at n=%d: %s", n, error)
                self._coords = None
                self.layout = None
                return None
            self.n = n
            self.layout = f"layout recomputed at n={n}"
        return self._coords


@dataclass(frozen=True, slots=True)
class DashboardSnapshot:
    """One render pass of every panel (UI-layer input; testable headless)."""

    health: dict[str, object]
    funnel_rows: list[dict[str, object]]
    pareto_rows: list[dict[str, object]]
    ticker: list[str]
    atlas: Figure | None
    layout_note: str | None
    errors: list[str] = field(default_factory=list)
    coverage_rows: list[dict[str, object]] = field(default_factory=list)
    strata_rows: list[dict[str, object]] = field(default_factory=list)
    front_history: list[dict[str, object]] = field(default_factory=list)
    graveyard: list[dict[str, object]] = field(default_factory=list)
    voids_summary: list[dict[str, object]] = field(default_factory=list)
    diversity: dict[str, float] = field(default_factory=dict)
    alerts: list[str] = field(default_factory=list)
    costs: dict[str, object] = field(default_factory=dict)
    cost_breakdown: list[dict[str, object]] = field(default_factory=list)
    maturation: list[dict[str, object]] = field(default_factory=list)
    event_history: list[dict[str, object]] = field(default_factory=list)
    objectives: tuple[ObjectiveSpec, ...] = ()


def _atlas_data(
    root: Path, cache: EmbedCache
) -> tuple[Figure | None, str | None, list[str]]:
    """Islands figure + layout note, never raising (bad artifacts become notes)."""
    try:
        return (*_load_atlas(root, cache), [])
    except Exception as error:  # ruff: ignore[blind-except] (dashboard must survive bad artifacts)
        return None, None, [f"atlas: {error}"]


def _load_atlas(root: Path, cache: EmbedCache) -> tuple[Figure | None, str | None]:
    import pandas as pd

    from computronium.visualization.atlas import (
        _islands_figure,
        align_void_columns,
        load_cells,
        load_voids,
    )

    cells = load_cells(root / "kb.sqlite")
    voids = align_void_columns(load_voids(root / "structural_voids.jsonl"))
    combined = (
        pd.concat([cells, voids], ignore_index=True) if not voids.empty else cells
    )
    coords = cache.coords(combined)
    if coords is None or combined.empty:
        return None, None
    combined["x"], combined["y"] = coords[:, 0], coords[:, 1]
    return (
        _islands_figure(combined.query("~is_void"), combined.query("is_void")),
        cache.layout,
    )


def render_snapshot(
    root: Path,
    log_path: Path | None = None,
    cache: EmbedCache | None = None,
    objectives: tuple[ObjectiveSpec, ...] = DEFAULT_OBJECTIVES,
    *,
    with_atlas: bool = True,
    event_history: list[dict[str, object]] | None = None,
) -> DashboardSnapshot:
    """Compute all panel payloads in one pass (no UI, no live loop).
    ``with_atlas=False`` skips the UMAP fit (the slow part) for the fast
    paint path."""
    cache = cache if cache is not None else EmbedCache()
    figure, layout_note, errors = (
        _atlas_data(root, cache) if with_atlas else (None, None, [])
    )
    diversity = diversity_stats(root)
    return DashboardSnapshot(
        health=health_stats(root),
        funnel_rows=defect_funnel_rows(root / "runtime_defects.jsonl"),
        pareto_rows=pareto_strip_rows(root, objectives=objectives),
        ticker=log_tail(log_path),
        atlas=figure,
        layout_note=layout_note,
        errors=errors,
        coverage_rows=coverage_by_axis(root),
        strata_rows=stratum_coverage(root),
        front_history=front_history_rows(root, objectives=objectives),
        graveyard=graveyard_rows(root),
        voids_summary=void_summary_rows(root),
        diversity=diversity,
        alerts=diversity_alerts(diversity),
        costs=cost_stats(root),
        cost_breakdown=cost_breakdown_rows(root),
        maturation=maturation_rows(root),
        event_history=event_history or [],
        objectives=objectives,
    )


def _toast_for_alert(event: DashboardEvent) -> None:
    """Fire a NiceGUI toast for alert events (breakthrough/cascade/completion)."""
    from nicegui import ui

    if event.kind != "alert":
        return
    alert_kind = event.payload.get("alert_kind", "?")
    title = event.payload.get("title", alert_kind)
    body = event.payload.get("body", "")
    text = f"{title} — {body}" if body else str(title)
    timeout_ms = TOAST_DURATION_S * 1000

    match alert_kind:
        case "breakthrough":
            ui.notify(f"★ {text}", type="positive", timeout=timeout_ms)
        case "cascade":
            ui.notify(f"⚠️ {text}", type="negative", timeout=timeout_ms)
        case "completion":
            ui.notify(f"🏁 {text}", type="info", timeout=timeout_ms)


def _objectives_from_heartbeat(root: Path) -> tuple[ObjectiveSpec, ...]:
    """Read objectives configuration from heartbeat.json if present."""
    heartbeat = read_heartbeat(root)
    if heartbeat is None:
        return DEFAULT_OBJECTIVES
    obj_spec = heartbeat.get("objectives")
    if isinstance(obj_spec, str):
        try:
            return parse_objectives(obj_spec)
        except ValueError:
            pass
    return DEFAULT_OBJECTIVES


async def _drain(
    ws: Any, loss_history: deque[float], refresh: Callable[[], None]
) -> None:
    import json as _json

    async for message in ws:
        record = _json.loads(message)
        loss = record.get("train_loss", record.get("loss"))
        if isinstance(loss, int | float):
            loss_history.append(float(loss))
            refresh()
