"""Monitor component — live status, health tiles, loss curve, activity feed."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from nicegui import ui

from computronium.ui.components.activity_feed import ActivityFeed, FeedEvent
from computronium.ui.panels import BasePanel

if TYPE_CHECKING:
    from computronium.visualization.live_atlas import Liveness


@dataclass(frozen=True, slots=True)
class HealthTile:
    """One health metric with a tri-state status."""

    label: str
    value: str
    status: str  # "running_smoothly" | "needs_attention" | "unstable"
    detail: str


@dataclass(frozen=True, slots=True)
class DriverIntent:
    """What the driver is doing right now (from proposal_batch events)."""

    proposing: int
    last_batch_ago_s: float
    strategy_hint: str


@dataclass(frozen=True, slots=True)
class SessionDelta:
    """Counters accumulated since the dashboard opened."""

    cells: int = 0
    records: int = 0
    crashes: int = 0

    def summary(self) -> str:
        parts = []
        if self.cells:
            parts.append(f"+{self.cells} cells")
        if self.records:
            parts.append(f"+{self.records} records")
        if self.crashes:
            parts.append(f"+{self.crashes} crashes")
        return " · ".join(parts) if parts else "no activity"


@dataclass(frozen=True, slots=True)
class MonitorData:
    """Everything the Monitor view shows in one refresh cycle."""

    liveness: Liveness
    tiles: list[HealthTile]
    loss_history: list[float]
    feed: list[FeedEvent]
    intent: DriverIntent | None = None
    session_delta: SessionDelta = SessionDelta()
    ticker: list[str] | None = None
    layout_note: str | None = None


_TILE_STATUS = {
    "running_smoothly": ("positive", "OK"),
    "needs_attention": ("warning", "Attention"),
    "unstable": ("negative", "Unstable"),
}


class MonitorView(BasePanel):
    """Monitor view: one glance answers 'is it running, is it healthy, what happened?'"""

    def __init__(self, *, quiet: bool = False) -> None:
        super().__init__(
            panel_key="monitor",
            plain=(
                "This is the live view of your campaign. The badge shows whether it "
                "is running, the tiles show campaign health, and the stream shows "
                "what happened recently."
            ),
            why=(
                "A single glance answers the three questions that matter: is the "
                "campaign alive, is it making progress, and did anything break."
            ),
            expert=(
                "Liveness from heartbeat freshness + daemon reachability. Tiles from "
                "health_stats(). Loss curve from the stream topic (throttled paint). "
                "Feed from stream events, classified; alerts raise toasts and reports."
            ),
            docs_url="https://computronium.readthedocs.io/en/latest/dashboard/monitor.html",
        )
        self.quiet = quiet
        self.data: MonitorData | None = None
        self._feed = ActivityFeed()

    def render(self) -> ui.element:
        """Render the Monitor view (fresh UI every call)."""
        with ui.column().classes("w-full gap-4") as panel:
            self.render_header("Monitor")

            if self.data is None:
                ui.label("Waiting for first refresh…").classes("text-grey")
                return panel

            self._render_status_row()
            self._render_tiles()
            self._render_loss()
            self._render_feed()
            if not self.quiet:
                self._render_ticker()

        return panel

    def _render_status_row(self) -> None:
        """Liveness badge + driver intent + session delta on one row."""
        data = self.data
        assert data is not None
        with ui.row().classes("w-full items-center gap-4 flex-wrap"):
            ui.badge(data.liveness.label, color=data.liveness.color or "grey").classes(
                "text-sm"
            )
            ui.label(data.liveness.detail).classes("text-caption text-grey")

            ui.separator().props("vertical")

            if data.intent:
                ui.icon("psychology").classes("text-primary")
                ui.label(
                    f"Proposing {data.intent.proposing} cells · "
                    f"{data.intent.last_batch_ago_s:.0f}s ago · "
                    f"{data.intent.strategy_hint}"
                ).classes("text-sm text-grey-7")
            else:
                ui.label("Driver: idle").classes("text-sm text-grey-7")

            ui.separator().props("vertical")

            delta = data.session_delta
            ui.label(f"Session: {delta.summary()}").classes(
                "text-sm font-mono text-primary"
            )

    def _render_tiles(self) -> None:
        """Health tiles as a wrap grid of status cards."""
        data = self.data
        assert data is not None
        with ui.row().classes("w-full flex-wrap gap-2"):
            for tile in data.tiles:
                color, label = _TILE_STATUS.get(tile.status, ("grey", tile.status))
                with ui.card().classes("w-52").props("flat bordered"):
                    with ui.row().classes("w-full items-center justify-between"):
                        ui.label(tile.label).classes("text-caption text-grey")
                        ui.badge(label, color=color).props("outline").classes("text-xs")
                    ui.label(tile.value).classes("text-h5 font-mono")
                    ui.label(tile.detail).classes("text-caption text-grey")

    def _render_loss(self) -> None:
        """Loss curve (echart line) or an explicit empty state."""
        data = self.data
        assert data is not None
        with ui.card().classes("w-full").props("flat bordered"):
            ui.label("Loss").classes("text-bold")
            if not data.loss_history:
                ui.label("No telemetry yet — connect a daemon for live loss.").classes(
                    "text-grey text-caption"
                )
                return
            losses = [round(v, 4) for v in data.loss_history[-60:]]
            option = {
                "animation": False,
                "grid": {"left": 48, "right": 16, "top": 16, "bottom": 28},
                "xAxis": {"type": "category", "show": False},
                "yAxis": {"type": "value", "scale": True},
                "series": [
                    {
                        "type": "line",
                        "data": losses,
                        "smooth": True,
                        "symbol": "none",
                        "lineStyle": {"color": "#1a5fa8", "width": 2},
                    }
                ],
            }
            ui.echart(option).classes("w-full h-48")

    def _render_feed(self) -> None:
        """Recent activity (live stream + alerts)."""
        data = self.data
        assert data is not None
        with ui.card().classes("w-full").props("flat bordered"):
            ui.label("Activity").classes("text-bold")
            if not data.feed:
                ui.label("No events yet.").classes("text-grey text-caption")
                return
            self._feed = ActivityFeed(events=list(data.feed[-50:]))
            self._feed.render()

    def _render_ticker(self) -> None:
        """Raw log ticker, collapsed by default."""
        data = self.data
        assert data is not None
        if not data.ticker:
            return
        with ui.expansion("Log ticker", icon="notes").classes("w-full"):
            for line in data.ticker[-30:]:
                ui.label(line).classes("font-mono text-xs text-grey")
            if data.layout_note:
                ui.label(f"Layout note: {data.layout_note}").classes(
                    "text-caption text-grey"
                )

    def update_data(self, data: MonitorData, **_: object) -> None:
        """Push fresh data; next render() reflects it."""
        self.data = data

    def set_lens(self, lens: str) -> None:
        """Monitor has no lenses."""
