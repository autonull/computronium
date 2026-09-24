"""Console component — live run & monitor view."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nicegui import ui

from computronium.ui.components.activity_feed import ActivityFeed, FeedEvent
from computronium.ui.components.field_reports import FieldReport, FieldReports
from computronium.ui.design_tokens import ICONS
from computronium.ui.mode_toggle import BasePanel


@dataclass(frozen=True, slots=True)
class CampaignInfo:
    """Campaign summary for the selector."""

    root: str
    name: str
    state: str  # "idle" | "proposing" | "training" | "sleeping" | "paused" | "stopped"
    cells: int
    burst: int | None
    target: int | None
    uptime_s: float


@dataclass(frozen=True, slots=True)
class DriverIntent:
    """Driver intent from proposal_batch events."""

    proposing: int
    last_batch_ago_s: float
    strategy_hint: str  # e.g. "spiking·recurrent"


@dataclass(frozen=True, slots=True)
class SessionDelta:
    """Session delta since dashboard opened."""

    cells: int = 0
    records: int = 0
    crashes: int = 0


@dataclass(frozen=True, slots=True)
class ConsoleData:
    """Data for Console panel."""

    campaigns: list[CampaignInfo]
    active_campaign: str | None
    liveness: dict[str, Any]
    driver_intent: DriverIntent | None
    session_delta: SessionDelta
    loss_history: list[float]
    ticker: list[str]
    reports: list[FieldReport]


class Console(BasePanel):
    """Console panel: campaign selector + status strip + driver intent +
    session delta + live stream + reports tray + controls."""

    def __init__(
        self,
        *,
        data: ConsoleData | None = None,
        on_campaign_change: Any | None = None,
        on_launch: Any | None = None,
        on_pause: Any | None = None,
        on_stop: Any | None = None,
        on_config: Any | None = None,
        ui_actions: bool = False,
    ) -> None:
        super().__init__(
            panel_key="console",
            plain_explanation=(
                "The Console shows the live campaign. Pick a campaign, "
                "see its vitals, and watch cells complete in real time."
            ),
            why_explanation=(
                "Monitoring the live run lets you see when the driver "
                "proposes new cells, when bursts finish, and if defects appear."
            ),
            expert_explanation=(
                "Status strip: liveness (heartbeat + API), vitals from "
                "health_stats(), loss curve from /ws/telemetry. Driver "
                "intent parsed from proposal_batch events (n_proposals, "
                "strategy primitives). Session delta = counts since page "
                "load. Controls gated by --ui-actions flag."
            ),
            docs_url="https://computronium.readthedocs.io/en/latest/dashboard/console.html",
        )
        self.data = data or ConsoleData(
            campaigns=[],
            active_campaign=None,
            liveness={},
            driver_intent=None,
            session_delta=SessionDelta(),
            loss_history=[],
            ticker=[],
            reports=[],
        )
        self._on_campaign_change = on_campaign_change
        self._on_launch = on_launch
        self._on_pause = on_pause
        self._on_stop = on_stop
        self._on_config = on_config
        self._ui_actions = ui_actions

        self._selector: Any = None
        self._status_container: Any = None
        self._loss_container: Any = None
        self._stream_container: Any = None
        self._reports_container: Any = None
        self._activity_feed = ActivityFeed()
        self._field_reports = FieldReports()

    def render(self) -> ui.element:
        """Render the Console panel."""
        with ui.column().classes("w-full gap-4") as panel:
            self.render_header("console")

            # Campaign selector + status strip
            self._render_header_strip()

            # Driver intent + session delta
            self._render_intent_delta()

            # Live stream (loss curve + event feed)
            self._render_live_stream()

            # Reports tray (badge-only)
            self._render_reports_tray()

            # Controls (--ui-actions gated)
            if self._ui_actions:
                self._render_controls()

        return panel

    def _render_header_strip(self) -> None:
        """Render campaign selector and status strip."""
        with ui.row().classes("w-full items-center gap-4 flex-wrap") as container:
            self._selector = (
                ui
                .select(
                    options={c.root: c.name for c in self.data.campaigns},
                    value=self.data.active_campaign,
                    on_change=lambda e: (
                        self._on_campaign_change and self._on_campaign_change(e.value)
                    ),
                )
                .props("dense outlined")
                .classes("w-64")
            )

            # Liveness badge
            liveness = self.data.liveness
            badge_color = liveness.get("color", "grey")
            ui.badge(liveness.get("label", "● OFFLINE"), color=badge_color).classes(
                "text-sm"
            )

            # Vitals
            if self.data.active_campaign:
                camp = next(
                    (
                        c
                        for c in self.data.campaigns
                        if c.root == self.data.active_campaign
                    ),
                    None,
                )
                if camp:
                    ui.label(f"Cells: {camp.cells}").classes("text-sm font-mono")
                    ui.label(f"Burst: {camp.burst or '—'}").classes("text-sm font-mono")
                    if camp.target:
                        pct = f"{100 * camp.cells / camp.target:.0f}%"
                        ui.label(f"Target: {pct}").classes("text-sm font-mono")

        self._status_container = container

    def _render_intent_delta(self) -> None:
        """Render driver intent and session delta."""
        with ui.row().classes("w-full items-center gap-4 flex-wrap"):
            # Driver intent
            intent = self.data.driver_intent
            if intent:
                with ui.row().classes("items-center gap-2"):
                    ui.icon(ICONS.get("intent", "psychology")).classes("text-primary")
                    ui.label(
                        f"Proposing {intent.proposing} cells · {intent.last_batch_ago_s:.0f}s ago · {intent.strategy_hint}"
                    ).classes("text-sm text-grey-7")
            else:
                ui.label("Driver: idle").classes("text-sm text-grey-7")

            ui.separator().props("vertical").classes("mx-2")

            # Session delta
            delta = self.data.session_delta
            parts = []
            if delta.cells:
                parts.append(f"+{delta.cells} cells")
            if delta.records:
                parts.append(f"+{delta.records} records")
            if delta.crashes:
                parts.append(f"+{delta.crashes} crashes")
            ui.label(
                "Session: " + (" · ".join(parts) if parts else "no activity")
            ).classes("text-sm font-mono text-primary")

    def _render_live_stream(self) -> None:
        """Render loss curve and live event stream."""
        with ui.row().classes("w-full gap-4"):
            # Loss curve
            with ui.card().classes("w-1/2").props("flat"):
                ui.label("Loss Curve").classes("text-bold mb-2")
                self._loss_container = ui.column().classes("w-full h-48")
                with self._loss_container:
                    self._render_loss_curve()

            # Event stream (activity feed)
            with ui.card().classes("w-1/2").props("flat"):
                ui.label("Live Stream").classes("text-bold mb-2")
                self._stream_container = ui.column().classes(
                    "w-full h-48 overflow-auto"
                )
                with self._stream_container:
                    self._activity_feed.render()

    def _render_loss_curve(self) -> None:
        """Render the loss curve using a simple plot."""
        if not self.data.loss_history:
            ui.label("No telemetry yet").classes("text-grey text-center p-8")
            return

        # Simple text-based loss display for now
        recent = self.data.loss_history[-20:]
        for i, loss in enumerate(recent):
            bar_len = int(loss * 20) if loss < 5 else 100
            bar = "█" * min(bar_len, 50)
            ui.label(f"{bar} {loss:.3f}").classes("font-mono text-xs text-grey")

    def _render_reports_tray(self) -> None:
        """Render reports tray (badge-only)."""
        count = len(self.data.reports)
        with ui.row().classes("w-full items-center justify-between"):
            ui.label("Reports").classes("text-bold")
            if count:
                ui.badge(str(count), color="primary").classes("cursor-pointer").on(
                    "click", self._show_reports_dialog
                )
            else:
                ui.label("No reports").classes("text-caption text-grey")

    def _show_reports_dialog(self) -> None:
        """Show field reports in a dialog."""
        with ui.dialog() as dialog, ui.card().classes("w-96"):
            ui.label("Field Reports").classes("text-h6 mb-4")
            with ui.column().classes("w-full gap-2"):
                for report in self.data.reports:
                    self._render_report_item(report)
            ui.button("Close", on_click=dialog.close).props("flat")
        dialog.open()

    def _render_report_item(self, report: FieldReport) -> None:
        """Render a single report item in the dialog."""
        with (
            ui.card().classes("w-full").props("flat"),
            ui.row().classes("w-full items-start gap-3"),
        ):
            ui.label(report.icon).classes("text-lg")
            with ui.column().classes("flex-1 gap-1"):
                ui.label(report.sentence).classes("text-body")
                if report.deep_link:
                    ui.link(
                        "See Evidence",
                        report.deep_link,
                    ).props("target=_blank").classes("text-primary text-sm")

    def _render_controls(self) -> None:
        """Render launch/pause/stop/config controls."""
        with ui.row().classes("w-full items-center gap-2"):
            ui.button("Launch", icon="play_arrow", on_click=self._on_launch).props(
                "color=positive"
            )
            ui.button("Pause", icon="pause", on_click=self._on_pause).props(
                "color=warning"
            )
            ui.button("Stop", icon="stop", on_click=self._on_stop).props(
                "color=negative"
            )
            ui.button("Config", icon="settings", on_click=self._on_config).props("flat")

    def update_data(
        self,
        data: ConsoleData | None = None,
        *,
        campaigns: list[CampaignInfo] | None = None,
        active_campaign: str | None = None,
        liveness: dict[str, Any] | None = None,
        driver_intent: DriverIntent | None = None,
        session_delta: SessionDelta | None = None,
        loss_history: list[float] | None = None,
        ticker: list[str] | None = None,
        reports: list[FieldReport] | None = None,
    ) -> None:
        """Update panel data and re-render."""
        if data is not None:
            self.data = data
        else:
            self.data = ConsoleData(
                campaigns=campaigns if campaigns is not None else self.data.campaigns,
                active_campaign=active_campaign
                if active_campaign is not None
                else self.data.active_campaign,
                liveness=liveness if liveness is not None else self.data.liveness,
                driver_intent=driver_intent
                if driver_intent is not None
                else self.data.driver_intent,
                session_delta=session_delta
                if session_delta is not None
                else self.data.session_delta,
                loss_history=loss_history
                if loss_history is not None
                else self.data.loss_history,
                ticker=ticker if ticker is not None else self.data.ticker,
                reports=reports if reports is not None else self.data.reports,
            )

        # Re-render affected parts
        if self._selector:
            self._selector.options = {c.root: c.name for c in self.data.campaigns}
        if self._status_container:
            self._status_container.clear()
            with self._status_container:
                self._render_header_strip()
        if self._loss_container:
            self._loss_container.clear()
            with self._loss_container:
                self._render_loss_curve()
        if self._stream_container:
            self._stream_container.clear()
            with self._stream_container:
                self._activity_feed.render()
        if self._reports_container:
            self._reports_container.clear()
            with self._reports_container:
                self._render_reports_tray()

    def add_stream_event(self, event: FeedEvent) -> None:
        """Add an event to the live stream."""
        self._activity_feed.add_event(event)

    def add_loss_point(self, loss: float) -> None:
        """Add a loss point to the history."""
        self.data.loss_history.append(loss)
        if len(self.data.loss_history) > 100:
            self.data.loss_history.pop(0)
        if self._loss_container:
            self._loss_container.clear()
            with self._loss_container:
                self._render_loss_curve()

    def add_report(self, report: FieldReport) -> None:
        """Add a report to the tray."""
        self.data.reports.append(report)
        self._field_reports.add_report(report)
        if self._reports_container:
            self._reports_container.clear()
            with self._reports_container:
                self._render_reports_tray()

    def increment_session_delta(
        self, cells: int = 0, records: int = 0, crashes: int = 0
    ) -> None:
        """Increment session delta counters."""
        self.data = ConsoleData(
            campaigns=self.data.campaigns,
            active_campaign=self.data.active_campaign,
            liveness=self.data.liveness,
            driver_intent=self.data.driver_intent,
            session_delta=SessionDelta(
                cells=self.data.session_delta.cells + cells,
                records=self.data.session_delta.records + records,
                crashes=self.data.session_delta.crashes + crashes,
            ),
            loss_history=self.data.loss_history,
            ticker=self.data.ticker,
            reports=self.data.reports,
        )

    def set_lens(self, lens: str) -> None:
        """Set active lens (Console has no lenses)."""


__all__ = [
    "CampaignInfo",
    "Console",
    "ConsoleData",
    "DriverIntent",
    "SessionDelta",
]
