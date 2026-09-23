"""Health Panel component (M1.7) — three plain tiles with relative time."""

from __future__ import annotations

from dataclasses import dataclass

from nicegui import ui

from computronium.ui.design_tokens import ICONS
from computronium.ui.mode_toggle import BasePanel


@dataclass(frozen=True, slots=True)
class HealthTile:
    """A health status tile."""

    label: str
    value: str
    status: str  # "running_smoothly" | "needs_attention" | "unstable"
    detail: str


class HealthPanel(BasePanel):
    """Health Panel: three plain tiles with relative time."""

    def __init__(
        self,
        *,
        tiles: list[HealthTile] | None = None,
        divergence_count: int = 0,
        last_burst: str | None = None,
        last_burst_walltime: float | None = None,
    ) -> None:
        super().__init__(
            panel_key="health",
            plain_explanation=(
                "This panel shows the health of the campaign at a glance. "
                "Green = running smoothly, Yellow = needs attention, Red = unstable."
            ),
            why_explanation=(
                "Quick health check lets you know if the campaign is healthy "
                "or if there are problems that need fixing."
            ),
            expert_explanation=(
                "Tiles: open/resolved defects, measured cells, diverged (NaN) cells, "
                "cells/burst, last-burst mean walltime. "
                "Divergence count = NaN loss cells. "
                "Relative time for last burst (e.g., '5 min ago')."
            ),
            docs_url="https://computronium.readthedocs.io/en/latest/dashboard/health.html",
        )
        self.tiles = tiles or []
        self.divergence_count = divergence_count
        self.last_burst = last_burst
        self.last_burst_walltime = last_burst_walltime
        self.loss_history: list[float] = []

    def render(self) -> ui.element:
        """Render the Health Panel."""
        with ui.column().classes("w-full gap-4") as panel:
            self.render_header("health")

            if not self.tiles:
                self._render_default_tiles()
            else:
                self._render_tiles()

            if self.loss_history:
                self._render_loss_curve()

        return panel

    def _render_loss_curve(self) -> None:
        """Render live loss history as an echart (B2)."""
        with ui.card().classes("w-full").props("flat"):
            ui.label(self.tr("loss_curve")).classes("text-h6")
            ui.echart({
                "xAxis": {"type": "category", "show": False},
                "yAxis": {"type": "value", "scale": True},
                "series": [
                    {
                        "type": "line",
                        "data": self.loss_history,
                        "showSymbol": False,
                    }
                ],
                "grid": {"left": 40, "top": 10, "right": 10, "bottom": 20},
            }).classes("w-full h-40")

    def _render_default_tiles(self) -> None:
        """Render default health tiles from raw data."""
        status = (
            "unstable"
            if self.divergence_count > 5
            else "needs_attention"
            if self.divergence_count > 0
            else "running_smoothly"
        )
        status_labels = {
            "running_smoothly": self.tr("running_smoothly"),
            "needs_attention": self.tr("needs_attention"),
            "unstable": self.tr("unstable"),
        }

        with ui.row().classes("w-full gap-4 flex-wrap"):
            # Overall status
            with ui.card().classes("flex-1 min-w-[200px]").props("flat"):
                ui.icon(ICONS["health"]).classes("text-3xl")
                ui.label(status_labels[status]).classes("text-h6")
                ui.label(self.tr("overall_status")).classes("text-caption text-grey")

            # Divergence
            with ui.card().classes("flex-1 min-w-[200px]").props("flat"):
                ui.icon(ICONS["diverged"]).classes("text-3xl")
                ui.label(str(self.divergence_count)).classes("text-h4")
                ui.label(self.tr("diverged_runs")).classes("text-caption text-grey")

            # Last burst
            with ui.card().classes("flex-1 min-w-[200px]").props("flat"):
                ui.icon(ICONS["history"]).classes("text-3xl")
                walltime_str = (
                    f"{self.last_burst_walltime:.1f}s"
                    if isinstance(self.last_burst_walltime, int | float)
                    else "—"
                )
                ui.label(walltime_str).classes("text-h4")
                ui.label(
                    f"{self.tr('last_burst')} {self._relative_time(self.last_burst)}"
                ).classes("text-caption text-grey")

    def _render_tiles(self) -> None:
        """Render custom health tiles."""
        with ui.row().classes("w-full gap-4 flex-wrap"):
            for tile in self.tiles:
                with ui.card().classes("flex-1 min-w-[200px]").props("flat"):
                    ui.label(tile.label).classes("text-h6")
                    ui.label(tile.value).classes("text-h4")
                    ui.label(tile.detail).classes("text-caption text-grey")

    def _relative_time(self, timestamp: str | None) -> str:
        """Format timestamp as relative time."""
        if not timestamp:
            return self.tr("no_burst_yet")
        # Simplified - would use actual relative time formatting
        return f"({timestamp})"

    def update_data(
        self,
        data: list[HealthTile] | None = None,
        *,
        tiles: list[HealthTile] | None = None,
        divergence_count: int | None = None,
        last_burst: str | None = None,
        last_burst_walltime: float | None = None,
        loss_history: list[float] | None = None,
    ) -> None:
        """Update panel data; positional data is the tile list."""
        if tiles is None and data is not None:
            tiles = data
        if tiles is not None:
            self.tiles = tiles
        if divergence_count is not None:
            self.divergence_count = divergence_count
        if last_burst is not None:
            self.last_burst = last_burst
        if last_burst_walltime is not None:
            self.last_burst_walltime = last_burst_walltime
        if loss_history is not None:
            self.loss_history = loss_history

    def _refresh(self) -> None:
        """Refresh on mode change."""
