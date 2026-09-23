"""Stagnation Dashboard (M2.12 → M3) — per-campaign stagnation status."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nicegui import ui

from computronium.ui.design_tokens import ICONS
from computronium.ui.mode_toggle import BasePanel


@dataclass(frozen=True, slots=True)
class StagnationDetector:
    """One stagnation detector status."""

    name: str  # WindowedMean, EMA, StatTest, VetoRate
    status: str  # "active", "triggered", "inactive"
    value: float
    threshold: float
    window: int
    last_triggered: float | None = None


@dataclass(frozen=True, slots=True)
class StagnationSnapshot:
    """Stagnation status for one campaign."""

    campaign_id: str
    detectors: list[StagnationDetector]
    overall_status: str  # "progressing", "stagnating", "stalled"
    history: list[dict[str, Any]] = None  # type: ignore[assignment]


class StagnationDashboard(BasePanel):
    """Stagnation Dashboard: per-campaign stagnation status.

    Shows 4 detector protocols: WindowedMean, EMA, StatTest, VetoRate.
    """

    def __init__(
        self,
        snapshots: list[StagnationSnapshot] | None = None,
    ) -> None:
        super().__init__(
            panel_key="stagnation_dashboard",
            plain_explanation=(
                "This panel shows whether campaigns are making progress or "
                "stuck. Four different detectors watch for stagnation — if any "
                "trigger, probes are launched to search for better recipes."
            ),
            why_explanation=(
                "Stagnation detection is the load-bearing gate: probes only "
                "fire when progress stalls, keeping overhead near zero in "
                "stable regimes. Four detectors catch different failure modes."
            ),
            expert_explanation=(
                "Per AUTOTILE.md §2.4: four stagnation detector protocols. "
                "1. WindowedMean: rolling mean of Pareto front improvement. "
                "2. EMA: exponential moving average of fitness. "
                "3. StatTest: statistical test (Mann-Whitney) on recent vs "
                "historical fitness. 4. VetoRate: Constitution veto rate trend. "
                "Campaign event log + SystemContext as data sources."
            ),
            docs_url="https://computronium.readthedocs.io/en/latest/auto-evolve/stagnation.html",
        )
        self.snapshots = snapshots or []

    def set_snapshots(self, snapshots: list[StagnationSnapshot]) -> None:
        """Set stagnation snapshots."""
        self.snapshots = snapshots
        self._refresh()

    def update_data(self, data: object | None = None, **kwargs: object) -> None:
        """Accept adapter StagnationDashboardData (diversity/alerts pass-through)."""
        # Snapshot carries diversity/alerts; detector snapshots come from
        # campaign event logs not yet part of DashboardSnapshot — keep current.

    def render(self) -> ui.element:
        """Render the stagnation dashboard."""
        with ui.column().classes("w-full gap-4") as panel:
            self.render_header("stagnation_dashboard")

            if not self.snapshots:
                ui.label("No stagnation data — run a campaign first.").classes(
                    "text-grey"
                )
                return panel

            for snapshot in self.snapshots:
                self._render_snapshot(snapshot)

        return panel

    def _render_snapshot(self, snapshot: StagnationSnapshot) -> None:
        """Render one campaign's stagnation status."""
        # Overall status badge
        status_colors = {
            "progressing": ("positive", ICONS["success"]),
            "stagnating": ("warning", ICONS["warning"]),
            "stalled": ("negative", ICONS["error"]),
        }
        color, icon = status_colors.get(
            snapshot.overall_status, ("grey", ICONS["info"])
        )

        with ui.card().classes("w-full").props("flat bordered"):
            with ui.row().classes("w-full items-center gap-4"):
                ui.icon(icon).classes(f"text-2xl text-{color}")
                ui.label(f"Campaign: {snapshot.campaign_id}").classes("text-h6")
                ui.badge(snapshot.overall_status.title(), color=color).classes(
                    "text-caption"
                )

            ui.separator()

            # Detectors
            ui.label("Detectors").classes("text-h6 mb-2")
            with ui.row().classes("w-full gap-4 flex-wrap"):
                for det in snapshot.detectors:
                    self._render_detector(det)

            # History
            if snapshot.history:
                ui.label("Status History").classes("text-h6 mt-4 mb-2")
                rows = []
                for entry in snapshot.history[-20:]:  # Last 20 entries
                    rows.append({
                        "timestamp": self._format_time(entry.get("timestamp", 0)),
                        "status": entry.get("status", "unknown"),
                        "triggered": ", ".join(entry.get("triggered_detectors", []))
                        or "—",
                    })
                ui.table(
                    columns=[
                        {"name": "timestamp", "label": "Time", "field": "timestamp"},
                        {"name": "status", "label": "Status", "field": "status"},
                        {
                            "name": "triggered",
                            "label": "Triggered",
                            "field": "triggered",
                        },
                    ],
                    rows=rows,
                    row_key="timestamp",
                ).classes("w-full")

    def _render_detector(self, det: StagnationDetector) -> None:
        """Render one detector card."""
        status_colors = {
            "active": ("positive", ICONS["success"]),
            "triggered": ("warning", ICONS["warning"]),
            "inactive": ("grey", ICONS["info"]),
        }
        color, icon = status_colors.get(det.status, ("grey", ICONS["info"]))

        with ui.card().classes("flex-1 min-w-[200px]").props("flat bordered"):
            with ui.row().classes("w-full items-center gap-2"):
                ui.icon(icon).classes(f"text-xl text-{color}")
                ui.label(det.name).classes("text-bold")

            ui.separator()

            if self.is_explorer:
                ui.label(f"Value: {det.value:.3f}").classes("text-body")
                ui.label(f"Threshold: {det.threshold:.3f}").classes(
                    "text-body text-grey"
                )
                ui.label(f"Window: {det.window}").classes("text-body text-grey")
            else:
                ui.label(f"{det.value:.3f} / {det.threshold:.3f}").classes(
                    "font-mono text-sm"
                )
                ui.label(f"Window: {det.window}").classes("text-caption text-grey")

            if det.last_triggered:
                ui.label(
                    f"Last triggered: {self._format_time(det.last_triggered)}"
                ).classes("text-caption text-grey")

    def _format_time(self, timestamp: float) -> str:
        import time

        return time.strftime("%H:%M:%S", time.localtime(timestamp))

    def _refresh(self) -> None:
        """Refresh on mode change."""


def create_stagnation_dashboard(
    snapshots: list[StagnationSnapshot] | None = None,
) -> StagnationDashboard:
    """Create the stagnation dashboard component."""
    return StagnationDashboard(snapshots=snapshots)
