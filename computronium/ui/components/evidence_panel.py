"""Evidence panel (§4.6) — CEEC beliefs, experiments, decisions. Read-only."""

from __future__ import annotations

from typing import TYPE_CHECKING

from nicegui import ui

from computronium.ui.panels import BasePanel

if TYPE_CHECKING:
    from computronium.ui.adapters import EvidenceData


class EvidencePanel(BasePanel):
    """Evidence view: what the campaign believes and why. Ledger writes stay in ceec.run."""

    def __init__(self) -> None:
        super().__init__(
            panel_key="evidence",
            plain="What the campaign believes and why",
            why="Beliefs, claims, calibration, and decisions in one place",
            expert="CEEC ledger projections via read-only SQLite; ledger writes stay in ceec.run",
        )
        self.data: EvidenceData | None = None

    def update_data(self, data: EvidenceData | None = None, **_: object) -> None:
        self.data = data
        self.on_data_update()

    def render(self) -> ui.element:
        with ui.column().classes("w-full gap-4") as panel:
            self.render_header("Evidence")
            if self.data is None:
                ui.label("Waiting for first refresh…").classes("text-grey")
                return panel
            data = self.data
            if data.empty_reason and not data.beliefs and not data.experiments:
                ui.label(f"No evidence yet — {data.empty_reason}.").classes("text-grey")
                return panel
            if data.beliefs:
                ui.label("Beliefs").classes("text-h6")
                with ui.column().classes("w-full gap-2"):
                    for belief in data.beliefs:
                        prob = (
                            f"{belief.probability_point:.2f}"
                            if belief.probability_point is not None
                            else "—"
                        )
                        ui.label(
                            f"{belief.statement} · p={prob} · {belief.status}"
                        ).classes("text-body")
            if data.experiments:
                ui.label("Experiments").classes("text-h6")
                with ui.column().classes("w-full gap-2"):
                    for experiment in data.experiments:
                        ui.label(
                            f"{experiment.question} · {experiment.status}"
                        ).classes("text-body")
            if data.decisions:
                ui.label("Decisions").classes("text-h6")
                with ui.column().classes("w-full gap-2"):
                    for decision in data.decisions:
                        ui.label(
                            f"{decision.selected_experiment}: {decision.rationale}"
                        ).classes("text-body")
        return panel
