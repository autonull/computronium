"""Live dashboard library (TODO29 Phase 5) — the continuous-discovery window.

Read-only: polls the campaign root's artifacts (KB, voids, defects, burst
log) on a timer and re-renders panels on change only. The polling signature
pattern is lifted from ``demo/campaign_tab.py`` (mtime_ns, size).

Instrument honesty: the map embeds a *sampled* σ_max(J) proxy and a UMAP
layout that is refit per cell-count change — the dashboard labels it as a
recomputed snapshot, never a trajectory or a stability frontier.
"""

from __future__ import annotations

import logging
import time
from collections import deque
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from pathlib import Path

    import numpy as np
    import pandas as pd
    from nicegui.element import Element
    from plotly.graph_objects import Figure

logger = logging.getLogger("live_atlas")

POLL_SECONDS = 2.0
TICKER_LINES = 30
MESSAGE_HEAD_CHARS = 80
WATCHED = ("kb.sqlite", "structural_voids.jsonl", "runtime_defects.jsonl")
HEARTBEAT_NAME = "heartbeat.json"
HEARTBEAT_STALE_S = 10.0


def read_heartbeat(root: Path) -> dict[str, object] | None:
    """Parse ``heartbeat.json`` (the daemon's liveness beacon), if present."""
    import json

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
        import json
        import urllib.request

        try:
            with urllib.request.urlopen(  # noqa: S310 (base_url is operator-supplied)
                f"{self._base}/state", timeout=self._timeout
            ) as response:
                return cast("dict[str, object] | None", json.loads(response.read()))
        except OSError, ValueError:
            return None

    def control(self, action: str) -> bool:
        import urllib.request

        request = urllib.request.Request(  # noqa: S310 (operator-supplied base)
            f"{self._base}/control/{action}",
            method="POST",
            data=b"",
        )
        try:
            urllib.request.urlopen(  # noqa: S310 (base_url is operator-supplied)
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


def health_stats(root: Path) -> dict[str, object]:
    """Open/resolved defects, cells-per-burst rate, last-burst mean walltime."""
    from computronium.autoscientist.broad_map import _load_measured_cells
    from computronium.autoscientist.defects import read_defects

    records = read_defects(root / "runtime_defects.jsonl")
    last_status: dict[str, str] = {}
    for record in records:
        last_status[record.defect_id] = record.status
    open_defects = sum(1 for status in last_status.values() if status == "open")

    rows = _load_measured_cells(root / "kb.sqlite")
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


def pareto_strip_rows(root: Path, k: int = 3) -> list[dict[str, object]]:
    """Current top-k Pareto cells with their instrument spokes."""
    from computronium.visualization.atlas import (
        apply_bp_deficit,
        load_cells,
        pareto_top,
    )

    ruler_table = root / "ruler_table.json"
    df = load_cells(root / "kb.sqlite")
    if df.empty:
        return []
    df = apply_bp_deficit(df, ruler_table, None)
    if "nan_loss" in df.columns:
        df = df.query("~nan_loss")
    top = pareto_top(df, k)
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


def _atlas_data(
    root: Path, cache: EmbedCache
) -> tuple[Figure | None, str | None, list[str]]:
    """Islands figure + layout note, never raising (bad artifacts become notes)."""
    try:
        return (*_load_atlas(root, cache), [])
    except Exception as error:  # noqa: BLE001 (dashboard must survive bad artifacts)
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
    *,
    with_atlas: bool = True,
) -> DashboardSnapshot:
    """Compute all panel payloads in one pass (no UI, no live loop).
    ``with_atlas=False`` skips the UMAP fit (the slow part) for the fast
    paint path."""
    cache = cache if cache is not None else EmbedCache()
    figure, layout_note, errors = (
        _atlas_data(root, cache) if with_atlas else (None, None, [])
    )
    return DashboardSnapshot(
        health=health_stats(root),
        funnel_rows=defect_funnel_rows(root / "runtime_defects.jsonl"),
        pareto_rows=pareto_strip_rows(root),
        ticker=log_tail(log_path),
        atlas=figure,
        layout_note=layout_note,
        errors=errors,
    )


def _health_cards(container: Element, health: dict[str, object]) -> None:
    """Gauge row: open/resolved defects, cells-per-burst, last-burst walltime."""
    from nicegui import ui

    cards = (
        ("open defects", str(health["open_defects"])),
        ("resolved defects", str(health["resolved_defects"])),
        ("measured cells", str(health["measured_cells"])),
        ("diverged (NaN)", str(health["nan_cells"])),
        ("cells / burst", str(health["cells_per_burst"])),
    )
    with container:
        for label, value in cards:
            with ui.card().classes("items-center py-2"):
                ui.label(value).classes("text-lg font-bold")
                ui.label(label).classes("text-xs text-grey")
        walltime = health["last_burst_walltime_s"]
        with ui.card().classes("items-center py-2"):
            ui.label(
                f"{walltime:.1f}s" if isinstance(walltime, int | float) else "—"
            ).classes("text-lg font-bold")
            ui.label(
                f"last-burst mean walltime ({health['last_burst'] or 'no burst yet'})"
            ).classes("text-xs text-grey")


def _atlas_panel(container: Element, snapshot: DashboardSnapshot) -> None:
    """Living-atlas panel with the instrument-honesty caption."""
    from nicegui import ui

    container.clear()
    with container:
        if snapshot.atlas is not None:
            ui.plotly(snapshot.atlas)
            ui.label(
                f"UMAP {snapshot.layout_note}: a recomputed embedding, "
                "not a trajectory. σ_max(J) is a sampled ‖Jv‖ proxy."
            ).classes("text-caption text-grey")
        else:
            ui.label(
                "atlas pending — the layout is computed off-thread and "
                "appears here (refit only when the cell count changes)."
            ).classes("text-grey")
        for error in snapshot.errors:
            ui.label(error).classes("text-caption text-red")


def _table_panel(
    container: Element, title: str, rows: list[dict[str, object]], **kwargs: object
) -> None:
    from nicegui import ui

    container.clear()
    with container:
        ui.label(title).classes("text-bold")
        if not rows:
            ui.label("nothing recorded yet.").classes("text-grey")
        else:
            ui.table(rows=rows, **kwargs)  # type: ignore[arg-type]


def _ticker_panel(container: Element, log_path: Path | None, lines: list[str]) -> None:
    from nicegui import ui

    container.clear()
    with container:
        ui.label(f"ticker — {log_path or 'no burst log'}").classes("text-bold")
        if lines:
            ui.label("\n".join(lines)).classes("font-mono text-xs whitespace-pre")
        else:
            ui.label("no log lines yet.").classes("text-grey")


def _lifecycle_bar(
    container: Element,
    badge: Liveness,
    actions: tuple[str, ...],
    on_action: object | None = None,
) -> None:
    """§2.1 bar: liveness badge + (at most) three lifecycle buttons. No
    other controls — the campaign config is CLI-immutable."""
    from nicegui import ui

    container.clear()
    with container:
        with ui.card().classes("items-center py-2"):
            ui.label(badge.label).classes(f"text-lg font-bold text-{badge.color}")
            ui.label(badge.detail).classes("text-xs text-grey")
        for action in actions:
            icon, text = {
                "start": ("▶", "Start"),
                "pause": ("⏸", "Pause"),
                "resume": ("▶", "Resume"),
                "stop": ("⏹", "Stop"),
            }[action]
            handler = (
                (lambda a=action: on_action(a))  # type: ignore[misc, operator]
                if on_action is not None
                else None
            )
            ui.button(text, icon=icon, on_click=handler).props(
                f"flat {'color=red' if action == 'stop' else ''}"
            )


def _panel_scaffold() -> tuple[Element, ...]:
    """Page row/column layout containers, in render order."""
    from nicegui import ui

    lifecycle_row = ui.row().classes("w-full items-center flex-wrap")
    health_row = ui.row().classes("w-full flex-wrap")
    atlas_box = ui.column().classes("w-full")
    funnel_box = ui.column().classes("w-full")
    pareto_box = ui.column().classes("w-full")
    ticker_box = ui.column().classes("w-full")
    return lifecycle_row, health_row, atlas_box, funnel_box, pareto_box, ticker_box


def _poll_only_bar(container: Element) -> None:
    """§2.1 stub when no daemon URL was configured: badge only, no buttons."""
    _lifecycle_bar(
        container,
        Liveness("● POLL-ONLY", "grey", "no --daemon-url: artifact polling only"),
        (),
    )


def build_dashboard(
    root: Path,
    log_path: Path | None = None,
    poll_seconds: float = POLL_SECONDS,
    daemon_url: str | None = None,
) -> None:
    """Build the read-only NiceGUI page. Call inside a UI context, then
    ``ui.run`` (see ``computronium.cli.dashboard``). ``daemon_url`` opts in
    to the lifecycle bar + live badge; without it the dashboard is
    polling-only (TODO30 §0 hybrid transport)."""
    from nicegui import run, ui

    log_path = resolve_log_path(root, log_path)
    cache = EmbedCache()
    client = DaemonClient(daemon_url) if daemon_url else None
    state: dict[str, object] = {
        "signature": watch_signature(root),
        "atlas_busy": False,
        "daemon_state": None,
    }

    ui.label("Computronium — live broad map").classes("text-h5 q-mb-none")
    ui.label(f"root: {root} · poll {poll_seconds:.0f}s · read-only").classes(
        "text-caption text-grey"
    )

    lifecycle_row, health_row, atlas_box, funnel_box, pareto_box, ticker_box = (
        _panel_scaffold()
    )

    send_action = client.control if client is not None else (lambda _action: None)

    def _render_panels(snapshot: DashboardSnapshot) -> None:
        health_row.clear()
        _health_cards(health_row, snapshot.health)
        _atlas_panel(atlas_box, snapshot)
        _table_panel(
            funnel_box,
            "Defect funnel (bug bounty — open first, then most hits)",
            snapshot.funnel_rows,
            pagination=10,
        )
        _table_panel(
            pareto_box,
            "Pareto strip (top cells with instrument spokes)",
            snapshot.pareto_rows,
        )
        _ticker_panel(ticker_box, log_path, snapshot.ticker)

    def _refresh_lifecycle() -> None:
        """Badge + buttons from one daemon probe (or the poll-only stub)."""
        if client is None:
            _poll_only_bar(lifecycle_row)
            return
        daemon_state = client.get_state()
        state["daemon_state"] = str(daemon_state.get("state")) if daemon_state else None
        _lifecycle_bar(
            lifecycle_row,
            liveness(root, daemon_state is not None),
            lifecycle_buttons(state["daemon_state"]),  # type: ignore[arg-type]
            on_action=send_action,
        )

    def refresh_cheap() -> None:
        """Fast paint: everything except the UMAP fit."""
        _refresh_lifecycle()
        _render_panels(render_snapshot(root, log_path, cache, with_atlas=False))

    async def load_atlas() -> None:
        """Off-thread UMAP refit; the panel swaps in when it lands."""
        if state["atlas_busy"]:
            return
        state["atlas_busy"] = True
        try:
            result = await run.io_bound(_atlas_data, root, cache)
            figure, note, errors = cast(
                "tuple[Figure | None, str | None, list[str]]", result
            )
            _atlas_panel(
                atlas_box,
                DashboardSnapshot(
                    health={},
                    funnel_rows=[],
                    pareto_rows=[],
                    ticker=[],
                    atlas=figure,
                    layout_note=note,
                    errors=errors,
                ),
            )
        finally:
            state["atlas_busy"] = False

    async def poll() -> None:
        signature = watch_signature(root)
        if signature != state["signature"]:
            state["signature"] = signature
            await run.io_bound(refresh_cheap)
            await load_atlas()

    refresh_cheap()
    ui.timer(0.5, load_atlas, once=True)
    ui.timer(poll_seconds, poll)
