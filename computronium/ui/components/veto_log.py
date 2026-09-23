"""Veto Log (M2.15 → M3) — vetoed mutations with reasons, veto rate trend."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nicegui import ui

from computronium.ui.design_tokens import ICONS
from computronium.ui.mode_toggle import BasePanel


@dataclass(frozen=True, slots=True)
class VetoEntry:
    """One vetoed mutation entry."""

    veto_id: str
    timestamp: float
    mutation_type: str
    proposal_id: str
    reason: str  # "lyapunov", "passivity", "protocol", "recursion"
    details: str
    genome_size_before: int
    estimated_slope: float
    metadata: dict[str, Any] = None  # type: ignore[assignment]


REASON_LABELS = {
    "lyapunov": "Lyapunov Fast-Proxy Fail",
    "passivity": "Passivity Fail",
    "protocol": "Protocol Conformance Fail",
    "recursion": "Recursion Invariant Fail",
}


class VetoLog(BasePanel):
    """Veto Log: vetoed mutations with reasons and veto rate trend.

    Audit trail of the Constitution at work.
    """

    def __init__(
        self,
        entries: list[VetoEntry] | None = None,
    ) -> None:
        super().__init__(
            panel_key="veto_log",
            plain_explanation=(
                "This log shows every mutation that was rejected by the "
                "Constitution. Each entry explains why — stability, energy, "
                "protocol, or recursion. The veto rate trend shows if the "
                "system is becoming more or less restrictive."
            ),
            why_explanation=(
                "The Constitution isn't just a checklist — it actively blocks "
                "unsafe mutations. This log is the audit trail. A rising veto "
                "rate might mean the Constitution needs calibration (amendment 6)."
            ),
            expert_explanation=(
                "Per AUTOTILE.md §3.5: vetoed mutations with reason "
                "(Lyapunov fast-proxy fail, Passivity fail, Protocol conformance "
                "fail, Recursion invariant). Veto rate trend is a first-class "
                "diagnostic — false-veto rate = calibration signal per amendment 6. "
                "Campaign event log (veto events) as data source."
            ),
            docs_url="https://computronium.readthedocs.io/en/latest/auto-evolve/veto.html",
        )
        self.entries = entries or []

    def add_entry(self, entry: VetoEntry) -> None:
        """Add a veto entry."""
        self.entries.insert(0, entry)  # Most recent first
        self._refresh()

    def set_entries(self, entries: list[VetoEntry]) -> None:
        """Set all veto entries."""
        self.entries = entries
        self._refresh()

    def render(self) -> ui.element:
        """Render the veto log."""
        with ui.column().classes("w-full gap-4") as panel:
            self.render_header("veto_log")

            if not self.entries:
                ui.label("No vetoes — Constitution checks all passing.").classes(
                    "text-grey"
                )
                return panel

            # Veto rate trend
            self._render_veto_rate_trend()

            # Veto breakdown by reason
            self._render_reason_breakdown()

            # Entries table
            ui.label("Recent Vetoes (most recent first)").classes("text-h6")
            rows = []
            for entry in self.entries[:50]:  # Limit to 50 most recent
                rows.append({
                    "veto_id": entry.veto_id[:8] + "...",
                    "timestamp": self._format_time(entry.timestamp),
                    "mutation_type": entry.mutation_type,
                    "reason": REASON_LABELS.get(entry.reason, entry.reason),
                    "details": entry.details[:80]
                    + ("..." if len(entry.details) > 80 else ""),
                    "genome_size": entry.genome_size_before,
                    "est_slope": f"{entry.estimated_slope:+.4f}",
                })

            ui.table(
                columns=[
                    {"name": "veto_id", "label": "Veto ID", "field": "veto_id"},
                    {"name": "timestamp", "label": "Time", "field": "timestamp"},
                    {
                        "name": "mutation_type",
                        "label": "Mutation",
                        "field": "mutation_type",
                    },
                    {"name": "reason", "label": "Reason", "field": "reason"},
                    {"name": "details", "label": "Details", "field": "details"},
                    {
                        "name": "genome_size",
                        "label": "|Ω| Before",
                        "field": "genome_size",
                    },
                    {"name": "est_slope", "label": "Est. Slope", "field": "est_slope"},
                ],
                rows=rows,
                row_key="veto_id",
                pagination=10,
            ).classes("w-full")

        return panel

    def _render_veto_rate_trend(self) -> None:
        """Render veto rate trend chart."""
        if len(self.entries) < 2:
            return

        # Group by time windows (e.g., hourly)
        import time
        from collections import defaultdict

        windows = defaultdict(int)
        for entry in self.entries:
            window = int(entry.timestamp / 3600)  # Hourly windows
            windows[window] += 1

        if len(windows) < 2:
            return

        sorted_windows = sorted(windows.items())
        x_data = [
            time.strftime("%H:00", time.localtime(w * 3600)) for w, _ in sorted_windows
        ]
        y_data = [c for _, c in sorted_windows]

        option = {
            "title": {"text": "Veto Rate Trend (per hour)", "left": "center"},
            "tooltip": {"trigger": "axis"},
            "xAxis": {"type": "category", "data": x_data, "name": "Time"},
            "yAxis": {"type": "value", "name": "Vetoes"},
            "series": [
                {
                    "name": "Vetoes",
                    "type": "line",
                    "data": y_data,
                    "showSymbol": True,
                    "color": "#c82333",
                }
            ],
            "grid": {"top": "40px", "bottom": "40px", "left": "60px", "right": "20px"},
        }
        ui.echart(option).classes("w-full h-[200px] mb-4")

    def _render_reason_breakdown(self) -> None:
        """Render veto breakdown by reason."""
        from collections import Counter

        reason_counts = Counter(e.reason for e in self.entries)
        if not reason_counts:
            return

        ui.label("Veto Reasons Breakdown").classes("text-h6 mb-2")
        with ui.row().classes("w-full gap-4 flex-wrap"):
            for reason, count in reason_counts.most_common():
                label = REASON_LABELS.get(reason, reason)
                with (
                    ui.card().classes("flex-1 min-w-[200px]").props("flat bordered"),
                    ui.row().classes("w-full items-center gap-2 justify-center"),
                ):
                    ui.icon(ICONS["veto"]).classes("text-2xl text-negative")
                    with ui.column().classes("items-center"):
                        ui.label(str(count)).classes("text-h4 text-bold text-negative")
                        ui.label(label).classes("text-caption text-center")

    def _format_time(self, timestamp: float) -> str:
        import time

        return time.strftime("%H:%M:%S", time.localtime(timestamp))

    def _refresh(self) -> None:
        """Refresh on mode change."""


def create_veto_log(
    entries: list[VetoEntry] | None = None,
) -> VetoLog:
    """Create the veto log component."""
    return VetoLog(entries=entries)
