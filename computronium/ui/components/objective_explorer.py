"""Objective explorer (§4.3) — parallel coordinates over measured cells.

Radar rejected (axis-order/scale distortion with 5+ objectives); 2D Pareto
scatter stays in Trade-offs. Linked selection runs through the shared
``selected_cell_key`` signal (NiceGUI Plotly has no server click events),
so the Atlas table and this panel open the same forensics drawer.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from nicegui import ui
from plotly.graph_objects import Parcoords

from computronium.ui.panels import BasePanel
from computronium.ui.state import selected_cell_key

if TYPE_CHECKING:
    from plotly.graph_objects import Figure as go_Figure

    from computronium.ui.adapters import ObjectiveExplorerData

_DEFAULT_AXES = ("accuracy", "walltime_s", "param_count", "energy_per_step")
_MAX_AXES = 6


def build_parcoords_figure(
    data: ObjectiveExplorerData, axes: tuple[str, ...]
) -> go_Figure:
    """Pure figure builder: dominated lines grey, front lines colored by accuracy."""
    import plotly.graph_objects as go

    picked = [axis for axis in axes if axis in data.axes] or list(data.axes[:4])
    positions = [data.axes.index(axis) for axis in picked]
    dimensions = [
        {"label": axis, "values": list(data.columns[position])}
        for axis, position in zip(picked, positions, strict=True)
    ]
    if "accuracy" in data.axes:
        accuracy = list(data.columns[data.axes.index("accuracy")])
    else:
        accuracy = [0.0] * len(data.cell_keys)
    front_idx = [i for i, flag in enumerate(data.pareto_mask) if flag]
    traces = [
        Parcoords(
            line={
                "color": accuracy,
                "colorscale": "Greys",
                "showscale": False,
            },
            dimensions=dimensions,
            name="dominated",
        )
    ]
    if front_idx:
        traces.append(
            Parcoords(
                line={
                    "color": [accuracy[i] for i in front_idx],
                    "colorscale": "Viridis",
                    "showscale": True,
                    "colorbar": {"title": "accuracy"},
                },
                dimensions=[
                    {**dim, "values": [dim["values"][i] for i in front_idx]}
                    for dim in dimensions
                ],
                name="pareto",
            )
        )
    return go.Figure(data=traces)


class ObjectiveExplorerPanel(BasePanel):
    """Parallel-coordinates explorer with axis picker and exports."""

    def __init__(self) -> None:
        super().__init__(
            panel_key="objective_explorer",
            plain="Every measured cell as one line across the goals you pick",
            why="Lines that stay high across axes are the trade-offs worth maturing",
            expert="Plotly parcoords over KB objectives; stride-decimated past 2k cells; front trace colored by accuracy",
        )
        self.data: ObjectiveExplorerData | None = None
        self.axes: tuple[str, ...] = _DEFAULT_AXES

    def update_data(
        self, data: ObjectiveExplorerData | None = None, **_: object
    ) -> None:
        self.data = data
        if data is not None:
            kept = tuple(axis for axis in self.axes if axis in data.axes)
            self.axes = kept or tuple(data.axes[:4])
        self.on_data_update()

    def _export_csv(self) -> None:
        from computronium.ui.exports import explorer_csv

        if self.data is not None:
            ui.download(explorer_csv(self.data), "cells.csv", "text/csv")

    def _export_html(self) -> None:
        from computronium.ui.exports import figure_html

        if self.data is not None:
            ui.download(
                figure_html(build_parcoords_figure(self.data, self.axes)),
                "parallel_coordinates.html",
                "text/html",
            )

    def render(self) -> ui.element:
        with ui.column().classes("w-full gap-4") as panel:
            self.render_header("Objective explorer")
            if self.data is None or not self.data.cell_keys:
                ui.label("No measured cells yet.").classes("text-grey")
                return panel
            data = self.data
            with ui.row().classes("w-full items-center gap-2"):
                ui.select(
                    list(data.axes),
                    multiple=True,
                    label="Axes (max 6)",
                    value=list(self.axes),
                    on_change=self._on_axes_change,
                ).props("dense")
                ui.button("Cells CSV", on_click=self._export_csv).props(
                    "flat dense"
                ).tooltip("Download plotted cells as CSV")
                ui.button("Figure HTML", on_click=self._export_html).props(
                    "flat dense"
                ).tooltip("Download standalone figure HTML")
            if data.decimated:
                ui.label(
                    f"Showing {len(data.cell_keys)} sampled lines (decimated past 2000)."
                ).classes("text-caption")
            ui.plotly(build_parcoords_figure(data, self.axes)).classes("w-full")
            ui.label(
                "Grey lines are dominated cells; colored lines are the Pareto front. "
                "Pick a cell below to open its forensics."
            ).classes("text-caption")
            ui.select(
                list(data.cell_keys),
                label="Inspect cell",
                on_change=lambda e: (
                    selected_cell_key.set(str(e.value)) if e.value else None
                ),
            ).props("dense")
        return panel

    def _on_axes_change(self, event: object) -> None:
        value = getattr(event, "value", None) or []
        self.axes = tuple(value[:_MAX_AXES]) or self.axes
