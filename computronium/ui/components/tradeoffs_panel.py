"""Trade-offs Panel component (M1.5) — Pareto strip with objective-pair selector."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


from nicegui import ui

from computronium.ui.design_tokens import ICONS
from computronium.ui.panels import BasePanel


@dataclass(frozen=True, slots=True)
class ParetoCell:
    """A cell on the Pareto front."""

    label: str
    dynamics: str
    credit: str
    update: str
    topology: str
    metrics: dict[str, float]
    is_new_front: bool = False


class TradeoffsPanel(BasePanel):
    """Trade-offs Panel: Pareto strip with objective-pair selector and reference anchors."""

    def __init__(
        self,
        *,
        cells: list[ParetoCell] | None = None,
        objectives: list[str] | None = None,
        ruler_metrics: dict[str, float] | None = None,
        on_objective_change: Callable[[list[str]], None] | None = None,
    ) -> None:
        super().__init__(
            panel_key="tradeoffs",
            plain=(
                "This panel shows the best trade-offs between two goals. "
                "Each dot is a recipe. The ruler shows how far each recipe is from the baseline."
            ),
            why=(
                "Comparing two goals at once reveals which recipes give the best balance. "
                "The ruler anchors show performance relative to a standard baseline."
            ),
            expert=(
                "Pareto front computed via non-dominated sorting on selected objectives. "
                "Ruler ratios = cell_value / ruler_value for walltime and energy. "
                "Selector options: accuracy+walltime, accuracy+params, accuracy+flops, "
                "accuracy+memory, accuracy+energy, walltime+params, accuracy+bp_deficit, "
                "stability+plasticity. Updates trigger re-computation via atlas.pareto_top()."
            ),
            docs_url="https://computronium.readthedocs.io/en/latest/dashboard/tradeoffs.html",
        )

        self.cells = cells or []
        self.objectives = objectives or ["accuracy", "walltime"]
        self.ruler_metrics = ruler_metrics or {}
        self.on_objective_change = on_objective_change

        # Objective pair presets (matching live_atlas)
        self._presets: dict[str, tuple[str, str]] = {
            "accuracy + walltime": ("accuracy", "walltime"),
            "accuracy + params": ("accuracy", "params"),
            "accuracy + flops": ("accuracy", "flops"),
            "accuracy + memory": ("accuracy", "memory"),
            "accuracy + energy": ("accuracy", "energy"),
            "walltime + params": ("walltime", "params"),
            "accuracy + bp_deficit": ("accuracy", "bp_deficit"),
            "stability + plasticity": ("stability", "plasticity"),
        }
        self._selected_preset = "accuracy + walltime"

    def render(self) -> ui.element:
        """Render the Trade-offs panel (fresh UI every call)."""
        with ui.column().classes("w-full gap-4") as panel:
            # Header
            self.render_header("Trade-offs")

            # Objective pair selector (renamed "Compare two goals")
            with ui.row().classes("w-full items-center gap-2 mb-2"):
                ui.label("Compare two goals").classes("text-bold")
                selector = (
                    ui
                    .select(
                        options=list(self._presets.keys()),
                        value=self._selected_preset,
                        on_change=self._on_selector_change,
                    )
                    .classes("w-64")
                    .props("dense outlined")
                )

                # Permanent plain semantics line
                ui.separator().classes("mx-2")
                ui.label(f"{'Best trade-off'} = {'Best trade-off recipes'}").classes(
                    "text-caption text-grey"
                )

            # Pareto strip
            strip_container = ui.column().classes("w-full")
            with strip_container:
                self._render_strip(strip_container)

        return panel

    def _on_selector_change(self, e) -> None:
        """Handle objective pair selector change."""
        self._selected_preset = e.value
        self.objectives = list(self._presets[e.value])
        if self.on_objective_change:
            self.on_objective_change(self.objectives)
        # Next render() will reflect the new objectives

    def _render_strip(self, container: ui.element) -> None:
        """Render the Pareto strip with reference anchors."""
        container.clear()
        with container:
            if not self.cells:
                ui.label("No trade-off data yet").classes("text-grey text-center p-4")
                return

            with ui.row().classes("w-full items-start gap-4 flex-wrap"):
                for cell in self.cells:
                    self._render_cell(cell)

    def _render_cell(self, cell: ParetoCell) -> None:
        """Render a single Pareto cell card."""
        with ui.card().classes("w-64 flex-shrink-0").props("flat"):
            self._render_cell_header(cell)
            self._render_cell_composition(cell)
            self._render_cell_anchors(cell)
            self._render_cell_narration_button(cell)

    def _render_cell_header(self, cell: ParetoCell) -> None:
        """Render cell header with label and metrics."""
        with ui.row().classes("w-full items-center justify-between"):
            ui.label(cell.label).classes("text-sm font-mono")
            if cell.is_new_front:
                ui.icon(ICONS["pareto_optimal"]).classes("text-gold")
            ui.badge(
                f"{self.objectives[0]}: {cell.metrics.get(self.objectives[0], 0):.3f}"
            ).classes("text-xs")
            ui.badge(
                f"{self.objectives[1]}: {cell.metrics.get(self.objectives[1], 0):.3f}"
            ).classes("text-xs")

    def _render_cell_composition(self, cell: ParetoCell) -> None:
        """Render cell composition."""
        ui.label(
            f"{cell.dynamics} × {cell.credit} × {cell.update} × {cell.topology}"
        ).classes("text-caption text-grey font-mono")

    def _render_cell_anchors(self, cell: ParetoCell) -> None:
        """Render reference anchors (ruler ratios)."""
        if not self.ruler_metrics:
            return

        with ui.row().classes("w-full gap-2 mt-2"):
            for metric in ["walltime", "energy"]:
                if metric in cell.metrics and metric in self.ruler_metrics:
                    ratio = cell.metrics[metric] / max(self.ruler_metrics[metric], 1e-9)
                    ui.label(f"{metric}: {ratio:.2f}× {'baseline'}").classes(
                        "text-xs text-grey"
                    )

    def _render_cell_narration_button(self, cell: ParetoCell) -> None:
        """Render guided reading narration button."""
        with ui.row().classes("w-full mt-2"):

            def _handler(_=None) -> None:
                self._show_narration(cell)

            ui.button(
                "Guided reading",
                icon=ICONS["info"],
                on_click=_handler,
            ).props("flat dense size=sm").classes("text-xs")

    def _show_narration(self, cell: ParetoCell) -> None:
        """Show guided reading narration for a cell."""
        with ui.dialog() as dialog, ui.card().classes("w-96"):
            ui.label("Guided reading").classes("text-h6 mb-2")
            ui.label(
                f"This recipe ({cell.label}) achieves "
                f"{cell.metrics.get(self.objectives[0], 0):.3f} {self.objectives[0]} "
                f"and {cell.metrics.get(self.objectives[1], 0):.3f} {self.objectives[1]}."
            ).classes("text-body")
            ui.separator()
            ui.label("Reference anchors").classes("text-bold")
            for metric in ["walltime", "energy"]:
                if metric in cell.metrics and metric in self.ruler_metrics:
                    ratio = cell.metrics[metric] / max(self.ruler_metrics[metric], 1e-9)
                    ui.label(f"{metric}: {ratio:.2f}× baseline").classes("text-body")
            ui.separator()
            ui.button("Close", on_click=dialog.close).props("flat")
        dialog.open()

    def update_cells(self, cells: list[ParetoCell]) -> None:
        """Update cells (no UI manipulation - next render() will reflect changes)."""
        self.cells = cells

    def update_data(
        self,
        data: object | None = None,
        *,
        cells: list[ParetoCell] | None = None,
        objectives: list[str] | None = None,
    ) -> None:
        """Push adapter TradeoffsData (or explicit cells) into the panel."""
        if cells is None and data is not None:
            cells = list(data.pareto_cells)  # type: ignore[attr-defined]
            objs = getattr(data, "objectives", None)
            if objs and len(objs) >= 2:
                objectives = list(objs[:2])
        if cells is not None:
            self.cells = cells
        if objectives is not None:
            self.objectives = objectives

    def _refresh(self) -> None:
        """Refresh with current data - no-op since render() creates fresh UI."""


def create_pareto_cells_from_atlas(pareto_rows: list[dict]) -> list[ParetoCell]:
    """Create ParetoCell objects from atlas pareto_strip_rows output."""
    cells = []
    for row in pareto_rows:
        metrics = {k: v for k, v in row.items() if k != "label"}
        cells.append(
            ParetoCell(
                label=row.get("label", ""),
                dynamics="",
                credit="",
                update="",
                topology="",
                metrics=metrics,
            )
        )
    return cells
