"""Status Chip — persistent header chip with deep links.

`running · +12 cells →Console · 3 crashes →Repair:Defects · +2 records →Map:Trade-offs`
- aria-live="polite" on transitions only (running↔idle↔dead)
- counts are deep links (click → jump to that lens)
- persists in --quiet (compact text-only)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

    from computronium.visualization.live_atlas import DashboardSnapshot

from nicegui import ui

from computronium.ui.lenses import palette_deep_link


def _to_int(val: Any, default: int = 0) -> int:
    """Safely convert to int."""
    if val is None:
        return default
    if isinstance(val, int):
        return val
    if isinstance(val, float):
        return int(val)
    try:
        return int(val)
    except ValueError, TypeError:
        return default


@dataclass(frozen=True, slots=True)
class ChipSegment:
    """A single segment in the status chip."""

    label: str
    count: int
    deep_link: str | None = None  # panel:lens format
    color: str = "primary"


@dataclass(frozen=True, slots=True)
class StatusChipData:
    """Data for the status chip."""

    state: str  # "running" | "idle" | "dead"
    segments: list[ChipSegment] = field(default_factory=list)
    quiet: bool = False

    @staticmethod
    def from_snapshot(
        snapshot: DashboardSnapshot,
        *,
        session_delta: Any | None = None,
        quiet: bool = False,
    ) -> StatusChipData:
        """Create chip data from dashboard snapshot."""
        # Determine state from health/liveness
        health = snapshot.health
        open_defects = _to_int(health.get("open_defects"))
        measured_cells = _to_int(health.get("measured_cells"))

        if open_defects > 5:
            state = "dead"
        elif measured_cells > 0:
            state = "running"
        else:
            state = "idle"

        segments = []

        # Cells segment → Console
        if session_delta:
            cells = getattr(session_delta, "cells", 0)
            if cells > 0:
                segments.append(
                    ChipSegment(
                        label="cells",
                        count=cells,
                        deep_link=palette_deep_link("console", ""),
                        color="primary",
                    )
                )

        # Crashes segment → Repair:Defects
        if open_defects > 0:
            segments.append(
                ChipSegment(
                    label="crashes",
                    count=open_defects,
                    deep_link=palette_deep_link("repair", "defects"),
                    color="negative",
                )
            )

        # Records segment → Map:Trade-offs (or Map:Map)
        if session_delta:
            records = getattr(session_delta, "records", 0)
            if records > 0:
                segments.append(
                    ChipSegment(
                        label="records",
                        count=records,
                        deep_link=palette_deep_link("map", "tradeoffs"),
                        color="positive",
                    )
                )

        return StatusChipData(state=state, segments=segments, quiet=quiet)


class StatusChip:
    """Persistent header status chip with cross-panel deep links."""

    def __init__(
        self,
        *,
        data: StatusChipData | None = None,
        on_deep_link: Callable[[str], None] | None = None,
        quiet: bool = False,
    ) -> None:
        self.data = data or StatusChipData(state="idle")
        self._on_deep_link = on_deep_link
        self._quiet = quiet
        self._container: Any = None
        self._prev_state = self.data.state

    def render(self) -> ui.element:
        """Render the status chip."""
        if self._quiet:
            return self._render_quiet()

        with ui.row().classes(
            "items-center gap-1 px-3 py-1 rounded bg-grey-1 dark:bg-grey-9"
        ) as container:
            self._container = container
            self._render_chip()

        return container

    def _render_quiet(self) -> ui.element:
        """Render compact text-only version for --quiet mode."""
        parts = [self.data.state.upper()]
        for seg in self.data.segments:
            if seg.count:
                parts.append(f"{seg.label}:{seg.count}")
        return ui.label(" · ".join(parts)).classes("font-mono text-xs text-grey")

    def _render_chip(self) -> None:
        """Render the full chip with clickable segments."""
        # State badge with aria-live on transition
        state_colors = {
            "running": "positive",
            "idle": "warning",
            "dead": "negative",
        }
        state_color = state_colors.get(self.data.state, "primary")

        # Check for state transition
        aria_live = "polite" if self.data.state != self._prev_state else "off"
        self._prev_state = self.data.state

        ui.badge(self.data.state.upper(), color=state_color).props(
            f'aria-live="{aria_live}"'
        )

        # Segments
        for seg in self.data.segments:
            if seg.count == 0:
                continue
            ui.label("·").classes("text-grey mx-1")
            if self._on_deep_link is not None and seg.deep_link:
                dl = seg.deep_link
                callback = self._on_deep_link
                ui.button(
                    f"{seg.count} {seg.label}",
                    on_click=lambda _, d=dl: callback(d) if callback else None,
                ).props("flat dense no-caps").classes("text-sm font-mono").tooltip(
                    f"Jump to {dl}"
                )
            else:
                ui.label(f"{seg.count} {seg.label}").classes("text-sm font-mono")

    def update_data(
        self,
        data: StatusChipData | None = None,
        *,
        state: str | None = None,
        segments: list[ChipSegment] | None = None,
        quiet: bool | None = None,
    ) -> None:
        """Update chip data and re-render."""
        if data is not None:
            self.data = data
        else:
            self.data = StatusChipData(
                state=state if state is not None else self.data.state,
                segments=segments if segments is not None else self.data.segments,
                quiet=quiet if quiet is not None else self.data.quiet,
            )

        if self._container:
            self._container.clear()
            with self._container:
                self._render_chip()


__all__ = [
    "ChipSegment",
    "StatusChip",
    "StatusChipData",
]
