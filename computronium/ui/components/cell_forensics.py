"""Cell forensics drawer (§4.1) — everything about one Atlas cell.

Read-only over the campaign root (Invariant 1): actions route through the
daemon lifecycle API and render disabled with a tooltip when no daemon is
attached. The daemon has no per-cell endpoints yet, so actions stay
disabled until they land — rendered honestly, never hidden.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from nicegui import ui

from computronium.ui.panels import BasePanel

if TYPE_CHECKING:
    from computronium.ui.adapters import CellForensicsData
    from computronium.visualization.live_atlas import DaemonClient


class CellForensicsPanel(BasePanel):
    """Right-drawer forensics for the selected Atlas cell."""

    def __init__(self, daemon_client: DaemonClient | None = None) -> None:
        super().__init__(
            panel_key="cell_forensics",
            plain="Everything about the selected cell: what it is, how it did, what went wrong",
            why="Coordinate, objectives, stability, maturity, and defect excerpts in one place",
            expert="Best-accuracy KB entry as representative; bursts/maturity unioned; Pareto via DEFAULT_OBJECTIVES",
        )
        self.data: CellForensicsData | None = None
        self.daemon_client = daemon_client
        self._forensics_drawer: ui.right_drawer | None = None

    def update_data(self, data: CellForensicsData | None = None, **_: object) -> None:
        self.data = data
        self.on_data_update()

    def show(self, data: CellForensicsData | None) -> None:
        """Push forensics data and open the drawer."""
        self.update_data(data)
        drawer = self._forensics_drawer
        if drawer is None:
            drawer = ui.right_drawer(value=True).props("width=520")
            self._forensics_drawer = drawer
            with drawer:
                self._render_body()
        else:
            drawer.clear()
            with drawer:
                self._render_body()
            drawer.show()

    def render(self) -> ui.element:
        with ui.column().classes("w-full gap-4") as panel:
            self.render_header("Cell forensics")
            self._render_body()
        return panel

    def _render_body(self) -> None:
        data = self.data
        if data is None:
            ui.label("Select a cell in the Atlas table to inspect it.").classes(
                "text-grey"
            )
            return
        ui.label(data.cell_key).classes("text-h6")
        with ui.row().classes("w-full items-center gap-2"):
            ui.label(f"Accuracy {data.accuracy:.3f} · {data.walltime_s:.1f}s").classes(
                "text-body"
            )
            if data.is_pareto:
                ui.label("★ Pareto-optimal").classes("text-positive")
            if data.is_nan:
                ui.label("Diverged (NaN)").classes("text-negative")
        ui.label(
            f"Stability ρ={data.spectral_radius:.2f} λ={data.lyapunov_exponent:.2f} "
            f"σ_max={data.max_singular_value:.2f} · ψ={data.psi_capacity:.1f} · "
            f"align={data.credit_alignment:.2f}"
        ).classes("text-caption")
        maturity = ", ".join(data.maturity) if data.maturity else "unknown"
        ui.label(f"Maturity {maturity} · {len(data.bursts)} bursts").classes(
            "text-caption"
        )
        if data.defects:
            ui.label("Defects").classes("text-h6")
            for defect in data.defects:
                with ui.card().classes("w-full p-2"):
                    ui.label(f"{defect.error_class} · {defect.status}").classes(
                        "text-body"
                    )
                    ui.label(defect.message).classes("text-caption")
        else:
            ui.label("No defects recorded for this cell.").classes("text-caption")
        with ui.row().classes("w-full gap-2"):
            for label in ("Promote to L1", "Unquarantine", "Deep-tier"):
                ui.button(label).props("disable flat dense").tooltip("requires daemon")
