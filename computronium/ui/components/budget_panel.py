"""Budget panel (§4.5) — burn-down, throughput, maturation, cost spread."""

from __future__ import annotations

from typing import TYPE_CHECKING

from nicegui import ui

from computronium.ui.panels import BasePanel

if TYPE_CHECKING:
    from computronium.ui.adapters import BudgetData


class BudgetPanel(BasePanel):
    """Budget & resources: how much campaign is left and where time goes."""

    def __init__(self) -> None:
        super().__init__(
            panel_key="budget",
            plain=(
                "How much of the campaign budget is spent, how fast cells "
                "finish, and how many cells reached each maturity stage."
            ),
            why=(
                "A campaign is a budget. Burn-down tells you whether the "
                "target is reachable; the cost spread tells you which "
                "primitives are expensive."
            ),
            expert=(
                "cost_stats()/cost_breakdown_rows()/maturation_rows() "
                "projections; throughput is 3600/mean_walltime."
            ),
        )
        self.data: BudgetData | None = None

    def update_data(self, data: BudgetData | None = None, **_: object) -> None:
        self.data = data
        self.on_data_update()

    def render(self) -> ui.element:
        with ui.column().classes("w-full gap-4") as panel:
            self.render_header("Budget & resources")
            if self.data is None:
                ui.label("Waiting for first refresh…").classes("text-grey")
                return panel
            data = self.data
            target = str(data.target) if data.target is not None else "∞"
            remaining = (
                f"{data.projected_remaining_s}s"
                if data.projected_remaining_s is not None
                else "—"
            )
            ui.label(
                f"{data.measured} / {target} cells ({data.coverage_label}) · "
                f"{data.cells_per_hour} cells/h · ~{remaining} left"
            ).classes("text-body")
            with ui.row().classes("w-full gap-4"):
                for stage in ("l0", "l1", "l2"):
                    with ui.card().classes("p-4"):
                        ui.label(stage).classes("text-h6")
                        ui.label(str(data.maturation.get(stage, 0))).classes("text-h4")
            if data.breakdown:
                with ui.table(
                    columns=[
                        {"name": "axis", "label": "Axis", "field": "axis"},
                        {
                            "name": "primitive",
                            "label": "Primitive",
                            "field": "primitive",
                        },
                        {"name": "mean", "label": "Mean s", "field": "mean"},
                        {"name": "n", "label": "n", "field": "n"},
                    ],
                    rows=[
                        {
                            "axis": row.axis,
                            "primitive": row.primitive,
                            "mean": row.mean_walltime_s,
                            "n": row.n,
                        }
                        for row in data.breakdown
                    ],
                ).classes("w-full"):
                    pass
        return panel
