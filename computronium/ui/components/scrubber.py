"""Burst-log scrubber (§4.4) — time-indexed cursor over on-disk burst log."""

from __future__ import annotations

from typing import TYPE_CHECKING

from nicegui import ui

from computronium.ui.panels import BasePanel

if TYPE_CHECKING:
    from computronium.ui.adapters import ScrubberData, ScrubberEvent


class ScrubberPanel(BasePanel):
    """Scrubber: pause live stream, filter by kind, jump-to-alert, LIVE button."""

    def __init__(self) -> None:
        super().__init__(
            panel_key="scrubber",
            plain="Replay the campaign's event stream: pause, filter, jump to alerts",
            why="Understand what happened and when; correlate bursts, defects, alerts",
            expert="Reads burst log JSONL; stride-indexed for large logs; LIVE button returns to tail",
        )
        self.data: ScrubberData | None = None
        self._filter_kind: str | None = None
        self._live_mode: bool = True

    def update_data(self, data: ScrubberData | None = None, **_: object) -> None:
        self.data = data
        if data is not None:
            self._filter_kind = data.kind_filter
            self._live_mode = data.live_mode
        self.on_data_update()

    def _filtered_events(self) -> list[ScrubberEvent]:
        if not self.data:
            return []
        events = self.data.events
        if self._filter_kind and self._filter_kind != "all":
            events = [e for e in events if e.kind == self._filter_kind]
        return events

    def _on_kind_change(self, e: object) -> None:
        value = getattr(e, "value", None)
        self._filter_kind = value if value != "all" else None
        if self.data:
            self.data = self.data.__class__(
                events=self.data.events,
                total_lines=self.data.total_lines,
                current_index=self.data.current_index,
                kind_filter=self._filter_kind,
                live_mode=self._live_mode,
            )

    def _on_live_toggle(self, e: object) -> None:
        self._live_mode = bool(getattr(e, "value", False))
        if self.data:
            self.data = self.data.__class__(
                events=self.data.events,
                total_lines=self.data.total_lines,
                current_index=self.data.current_index,
                kind_filter=self._filter_kind,
                live_mode=self._live_mode,
            )

    def _jump_to_alert(self, direction: int) -> None:
        if not self.data:
            return
        filtered = self._filtered_events()
        alerts = [i for i, e in enumerate(filtered) if e.is_alert]
        if not alerts:
            return
        idx = self.data.current_index
        if direction > 0:
            nxt = [a for a in alerts if a > idx]
            target = nxt[0] if nxt else alerts[0]
        else:
            prv = [a for a in alerts if a < idx]
            target = prv[-1] if prv else alerts[-1]
        self.data = self.data.__class__(
            events=self.data.events,
            total_lines=self.data.total_lines,
            current_index=target,
            kind_filter=self._filter_kind,
            live_mode=self._live_mode,
        )

    def _on_index_change(self, e: object) -> None:
        value = getattr(e, "value", None)
        if isinstance(value, int) and self.data:
            self.data = self.data.__class__(
                events=self.data.events,
                total_lines=self.data.total_lines,
                current_index=max(0, min(value, len(self._filtered_events()) - 1)),
                kind_filter=self._filter_kind,
                live_mode=self._live_mode,
            )

    def render(self) -> ui.element:
        with ui.column().classes("w-full gap-4") as panel:
            self.render_header("Burst-log scrubber")
            if not self.data or not self.data.events:
                ui.label("No burst log found.").classes("text-grey")
                return panel

            events = self._filtered_events()
            total = len(events)
            idx = self.data.current_index if self.data else 0
            idx = max(0, min(idx, total - 1)) if total > 0 else 0

            # Controls row
            with ui.row().classes("w-full items-center gap-2"):
                kinds = ["all", *sorted({e.kind for e in self.data.events})]
                ui.select(
                    kinds,
                    value=self._filter_kind or "all",
                    label="Filter",
                    on_change=self._on_kind_change,
                ).props("dense")
                ui.switch(
                    value=self._live_mode,
                    on_change=self._on_live_toggle,
                ).props("inline")
                ui.label("LIVE").classes(
                    "text-caption"
                    if not self._live_mode
                    else "text-caption text-primary"
                )
                ui.button("⏮", on_click=lambda: self._jump_to_alert(-1)).props(
                    "flat dense size=sm"
                ).tooltip("Previous alert")
                ui.button("⏭", on_click=lambda: self._jump_to_alert(1)).props(
                    "flat dense size=sm"
                ).tooltip("Next alert")
                if total > 1:
                    ui.slider(
                        min=0,
                        max=total - 1,
                        value=idx,
                        on_change=self._on_index_change,
                    ).props("label-always").classes("flex-1")

            # Event list (virtualized view - show window around current)
            window = 50
            start = max(0, idx - window // 2)
            end = min(total, start + window)
            if end - start < window:
                start = max(0, end - window)

            with ui.column().classes("w-full gap-1 max-h-96 overflow-auto"):
                for i in range(start, end):
                    e = events[i]
                    is_current = i == idx
                    is_alert = e.is_alert
                    classes = "p-2 border-l-4 "
                    classes += (
                        "bg-primary-100 border-primary" if is_current else "bg-grey-1"
                    )
                    classes += " border-red" if is_alert else ""
                    with ui.row().classes(f"{classes} w-full items-center gap-2"):
                        ui.label(f"{e.line_num:>5}").classes(
                            "text-caption font-mono text-grey"
                        )
                        icon = "🔔" if is_alert else _KIND_ICONS.get(e.kind, "📋")
                        ui.label(icon).classes("text-lg")
                        ui.label(f"{e.timestamp:.1f}").classes(
                            "text-caption font-mono text-grey w-16"
                        )
                        ui.label(e.kind).classes("text-caption text-grey w-24")
                        ui.label(e.summary).classes("text-body flex-1 truncate")

        return panel


_KIND_ICONS = {
    "state": "📊",
    "daemon_started": "🚀",
    "daemon_stopped": "🛑",
    "burst_finished": "✅",
    "campaign_complete": "🏁",
    "alert": "⚠️",
    "report": "📄",
    "cell_completed": "🧬",
    "defect_quarantined": "🔒",
    "proposal_batch": "📦",
}
