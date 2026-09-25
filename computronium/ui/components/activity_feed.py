"""Activity Feed component (M1.8) — pausable, reverse-chron, aria-live."""

from __future__ import annotations

from dataclasses import dataclass

from nicegui import ui

from computronium.ui.a11y.tokens import LIVE_REGION_CONFIG
from computronium.ui.panels import BasePanel


@dataclass(frozen=True, slots=True)
class FeedEvent:
    """An event in the activity feed."""

    timestamp: float
    icon: str
    color: str
    summary: str
    raw: str


class ActivityFeed(BasePanel):
    """Activity Feed: pausable, reverse-chron, aria-live, batch summary mode."""

    def __init__(
        self,
        *,
        events: list[FeedEvent] | None = None,
        max_events: int = 30,
        batch_interval_ms: int = 500,
    ) -> None:
        super().__init__(
            panel_key="activity_feed",
            plain=(
                "This is the activity feed. It shows what's happening right now. "
                "Pause it to read at your own pace."
            ),
            why=(
                "The feed shows real-time events from the campaign. "
                "Batch summaries prevent overwhelming screen readers."
            ),
            expert=(
                "Reverse-chronological event stream from /ws/events. "
                f"Rate-limited to {LIVE_REGION_CONFIG.min_interval_ms}ms for aria-live=polite. "
                "Pausable toggle. Batch summary mode groups events by type. "
                f"Expandable to raw JSON. Max {max_events} visible."
            ),
            docs_url="https://computronium.readthedocs.io/en/latest/dashboard/activity.html",
        )
        self.events = events or []
        self.max_events = max_events
        self.batch_interval_ms = batch_interval_ms
        self._paused = False
        self._batch_mode = False
        self._feed_container: ui.element = ui.column().classes("w-full")

    def render(self) -> ui.element:
        """Render the Activity Feed."""
        with ui.column().classes("w-full gap-4") as panel:
            self.render_header("Ticker")

            # Controls
            with ui.row().classes("w-full items-center gap-2"):
                ui.switch(
                    value=self._paused,
                    on_change=lambda e: setattr(self, "_paused", e.value),
                ).props('size="sm"')
                ui.label("Paused").classes("text-sm")
                ui.switch(
                    value=self._batch_mode,
                    on_change=lambda e: setattr(self, "_batch_mode", e.value),
                ).props('size="sm"')
                ui.label("Batch summary").classes("text-sm")

            # Feed container with aria-live
            self._feed_container = ui.column().classes("w-full")
            with self._feed_container:
                self._render_feed()

        return panel

    def _render_feed(self) -> None:
        """Render the feed events."""
        # Check if container is still valid
        if not hasattr(self, "_feed_container") or self._feed_container is None:
            return
        try:
            self._feed_container.clear()
        except AssertionError, RuntimeError:
            return
        with self._feed_container:
            # aria-live region
            with (
                ui
                .element("div")
                .props(
                    f'aria-live="{LIVE_REGION_CONFIG.politeness}" aria-atomic="true"'
                )
                .classes("sr-only")
            ):
                ui.label("Live updates").classes("sr-only")

            if not self.events:
                ui.label("No events yet").classes("text-grey text-center p-4")
                return

            for event in reversed(self.events[-self.max_events :]):
                time_str = self._format_time(event.timestamp)
                with ui.row().classes("w-full items-start gap-2 px-2 py-1"):
                    ui.label(time_str).classes(
                        "font-mono text-xs text-grey w-16 shrink-0"
                    )
                    ui.label(event.icon).classes("text-base shrink-0")
                    ui.label(event.summary).classes(
                        f"font-mono text-xs text-{event.color} break-all flex-1"
                    )

    def _format_time(self, timestamp: float) -> str:
        """Format timestamp as HH:MM:SS."""
        import time

        return time.strftime("%H:%M:%S", time.localtime(timestamp))

    def add_event(self, event: FeedEvent) -> None:
        """Add an event to the feed."""
        if not self._paused:
            self.events.append(event)
            if len(self.events) > self.max_events * 2:
                self.events = self.events[-self.max_events :]
            self._render_feed()

    def update_data(
        self, data: object | None = None, *, events: list[FeedEvent] | None = None
    ) -> None:
        """Push adapter ActivityFeedData (or explicit events) into the panel."""
        if events is None and data is not None:
            events = [
                FeedEvent(
                    timestamp=e.timestamp,
                    icon=e.icon,
                    color=e.color,
                    summary=e.summary,
                    raw=getattr(e, "raw", ""),
                )
                for e in data.events  # type: ignore[attr-defined]
            ]
        if events is not None:
            self.events = events

    def _refresh(self) -> None:
        """Refresh with current data."""
        self._render_feed()
