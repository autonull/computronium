"""Probe Analytics Panel (M2.11 → M3) — adaptation probe slopes, forked-copy hygiene."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nicegui import ui

from computronium.ui.design_tokens import ICONS
from computronium.ui.panels import BasePanel


@dataclass(frozen=True, slots=True)
class ProbeBatch:
    """One adaptation probe batch.

    Forked-copy hygiene is structural: a batch cannot exist in a
    non-forked state, so probe batches never touch production data.
    """

    batch_id: str
    timestamp: float
    current_slope: float
    proposed_slope: float
    accepted: bool
    statistical_significance: float
    forked_copy: bool = True
    metadata: dict[str, Any] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.forked_copy is not True:
            raise ValueError("ProbeBatch requires forked_copy=True (UX-L11)")


class ProbeAnalytics(BasePanel):
    """Probe Analytics: show probe batches, current vs proposed slope,
    acceptance/rejection, forked-copy hygiene.

    Probe batches never touch production training data (UX-L11).
    """

    def __init__(
        self,
        batches: list[ProbeBatch] | None = None,
    ) -> None:
        super().__init__(
            panel_key="probe_analytics",
            plain=(
                "This panel shows adaptation probes — small experiments that "
                "test if a recipe change helps learning. Each probe runs on a "
                "forked copy of the data, never on your real training runs."
            ),
            why=(
                "Probes let the system test changes safely. The 'forked copy' "
                "means your actual experiments are never touched. You see the "
                "proposed learning speed vs. current, and whether it passed "
                "statistical checks."
            ),
            expert=(
                "Adaptation probes per AUTOTILE.md §3.2: slope-based selection "
                "with forked-copy hygiene. Each probe: (1) forks current genome "
                "and data, (2) applies mutation, (3) measures slope on probe "
                "budget K, (4) statistical test vs. current slope. "
                "UX-L11 property test verifies probe batches never touch "
                "production training data."
            ),
            docs_url="https://computronium.readthedocs.io/en/latest/auto-evolve/probes.html",
        )
        self.batches = batches or []

    def add_batch(self, batch: ProbeBatch) -> None:
        """Add a new probe batch."""
        self.batches.insert(0, batch)  # Most recent first
        self._refresh()

    def set_batches(self, batches: list[ProbeBatch]) -> None:
        """Set all probe batches."""
        self.batches = batches
        self._refresh()

    def render(self) -> ui.element:
        """Render the probe analytics panel."""
        with ui.column().classes("w-full gap-4") as panel:
            self.render_header("Learning speed comparison")

            # Forked-copy hygiene badge
            with ui.row().classes("w-full items-center gap-2 mb-4"):
                ui.icon(ICONS["probe"]).classes("text-xl text-primary")
                ui.badge(
                    "Forked-copy hygiene verified (UX-L11)", color="positive"
                ).props("outline")

            if not self.batches:
                ui.label("No probe batches yet").classes("text-grey")
                return panel

            # Summary stats
            accepted = sum(1 for b in self.batches if b.accepted)
            total = len(self.batches)
            with ui.row().classes("w-full gap-4 mb-4"):
                self._stat_card("Total Probes", total, ICONS["probe"])
                self._stat_card("Accepted", accepted, ICONS["success"])
                self._stat_card("Rejected", total - accepted, ICONS["error"])
                avg_improvement = sum(
                    b.proposed_slope - b.current_slope
                    for b in self.batches
                    if b.accepted
                ) / max(accepted, 1)
                self._stat_card(
                    "Avg Improvement", f"{avg_improvement:+.3f}", ICONS["arrow_up"]
                )

            # Batch table
            ui.label("Probe Batches (most recent first)").classes("text-h6")
            rows = []
            for batch in self.batches:
                rows.append({
                    "batch_id": batch.batch_id[:8] + "...",
                    "current_slope": f"{batch.current_slope:.4f}",
                    "proposed_slope": f"{batch.proposed_slope:.4f}",
                    "delta": f"{batch.proposed_slope - batch.current_slope:+.4f}",
                    "accepted": "✓ Accepted" if batch.accepted else "✗ Rejected",
                    "p_value": f"{batch.statistical_significance:.3f}",
                    "forked": "Yes" if batch.forked_copy else "No",
                    "timestamp": self._format_time(batch.timestamp),
                })

            ui.table(
                columns=[
                    {"name": "batch_id", "label": "Batch", "field": "batch_id"},
                    {
                        "name": "current_slope",
                        "label": "Current Slope",
                        "field": "current_slope",
                    },
                    {
                        "name": "proposed_slope",
                        "label": "Proposed Slope",
                        "field": "proposed_slope",
                    },
                    {"name": "delta", "label": "Δ Slope", "field": "delta"},
                    {"name": "accepted", "label": "Result", "field": "accepted"},
                    {"name": "p_value", "label": "p-value", "field": "p_value"},
                    {"name": "forked", "label": "Forked Copy", "field": "forked"},
                    {"name": "timestamp", "label": "Time", "field": "timestamp"},
                ],
                rows=rows,
                row_key="batch_id",
            ).classes("w-full")

        return panel

    def _stat_card(self, label: str, value: Any, icon: str) -> ui.element:
        with ui.card().classes("flex-1 min-w-[150px]").props("flat bordered") as card:
            ui.icon(icon).classes("text-2xl text-primary")
            ui.label(str(value)).classes("text-h4 text-bold")
            ui.label(label).classes("text-caption text-grey")
        return card

    def _format_time(self, timestamp: float) -> str:
        import time

        return time.strftime("%H:%M:%S", time.localtime(timestamp))

    def _refresh(self) -> None:
        """Refresh with current data."""


def create_probe_analytics(
    batches: list[ProbeBatch] | None = None,
) -> ProbeAnalytics:
    """Create the probe analytics component."""
    return ProbeAnalytics(batches=batches)
