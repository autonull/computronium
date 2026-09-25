"""Modernized Monitor Panel — demonstrates new component architecture.

This is a refactored version of MonitorView using:
- Component base class with lifecycle hooks
- Reactive state management
- Theming system
- Accessibility utilities
- Virtualization for large lists
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

from computronium.ui.component import Component, StatelessComponent
from computronium.ui.state import signal, effect
from computronium.ui.theme import theme_manager, card_style
from computronium.ui.a11y import announce, create_live_region
from computronium.ui.virtualize import create_virtual_list

if TYPE_CHECKING:
    from nicegui import ui

from computronium.ui.components.monitor import MonitorData, HealthTile, DriverIntent, SessionDelta, FeedEvent


@dataclass(frozen=True, slots=True)
class MonitorProps:
    """Props for MonitorPanel."""
    data: MonitorData | None = None
    quiet: bool = False
    on_refresh: Callable[[], None] | None = None


@dataclass
class MonitorState:
    """Internal state for MonitorPanel."""
    loss_history: list[float] = field(default_factory=list)
    expanded_sections: set[str] = field(default_factory=set)
    filter_text: str = ""


class HealthTileComponent(StatelessComponent[HealthTile]):
    """Individual health tile component."""
    
    def render(self) -> "ui.element":
        from nicegui import ui
        from computronium.ui.theme import theme_manager, card_style, badge_style
        
        tile: HealthTile = self.props  # type: ignore
        t = theme_manager.theme
        
        # Status color mapping
        status_colors = {
            "running_smoothly": ("success", "✅"),
            "needs_attention": ("warning", "⚠"),
            "unstable": ("error", "❌"),
        }
        variant, icon = status_colors.get(tile.status, ("default", "ℹ"))
        
        with ui.card().classes("w-full p-4").style(card_style().build()) as card:
            with ui.row().classes("w-full items-center gap-3"):
                ui.label(icon).classes("text-2xl")
                
                with ui.column().classes("flex-1 min-w-0"):
                    ui.label(tile.label).classes("font-medium text-sm truncate")
                    ui.label(tile.value).classes("text-2xl font-bold text-primary")
                
                ui.badge(tile.status.replace("_", " ").title(), 
                        color=variant).props("outline").classes("whitespace-nowrap")
                
                if tile.detail:
                    ui.tooltip(tile.detail)
        
        return card


class LossChartComponent(StatelessComponent[list[float]]):
    """Loss history chart using ECharts."""
    
    def render(self) -> "ui.element":
        from nicegui import ui
        from computronium.ui.theme import theme_manager, card_style
        
        losses: list[float] = self.props  # type: ignore
        t = theme_manager.theme
        
        if not losses:
            with ui.card().classes("w-full").style(card_style().build()):
                ui.label("No loss data").classes("text-grey text-center p-8")
            return ui.column().classes("w-full")
        
        # Create ECharts line chart
        chart = ui.echart({
            "grid": {"left": "50", "right": "20", "top": "20", "bottom": "40"},
            "xAxis": {"type": "category", "data": list(range(len(losses))), 
                     "axisLine": {"lineStyle": {"color": t.colors.border}},
                     "axisLabel": {"color": t.colors.text_secondary}},
            "yAxis": {"type": "value", "axisLine": {"lineStyle": {"color": t.colors.border}},
                     "axisLabel": {"color": t.colors.text_secondary}},
            "series": [{
                "data": losses,
                "type": "line",
                "smooth": True,
                "showSymbol": False,
                "lineStyle": {"color": t.colors.primary, "width": 2},
                "areaStyle": {"color": {
                    "type": "linear",
                    "x": 0, "y": 0, "x2": 0, "y2": 1,
                    "colorStops": [
                        {"offset": 0, "color": t.colors.primary + "40"},
                        {"offset": 1, "color": t.colors.primary + "00"},
                    ]
                }},
            }],
            "tooltip": {"trigger": "axis", "formatter": "Step {c0}: {c1:.4f}"},
        }).classes("w-full h-64")
        
        with ui.card().classes("w-full").style(card_style().build()) as card:
            ui.label("Training Loss").classes("text-h6 mb-2")
            chart
        
        return card


class ActivityFeedComponent(Component[list[FeedEvent], None]):
    """Virtualized activity feed with live region."""
    
    def initial_state(self) -> None:
        return None
    
    def __init__(self, props: list[FeedEvent] | None = None):
        super().__init__(props)
        self._live_region = create_live_region("polite")
        self._scroller: Any = None
    
    def render(self) -> "ui.element":
        from nicegui import ui
        from computronium.ui.theme import theme_manager, card_style
        
        events: list[FeedEvent] = self.props or []  # type: ignore
        t = theme_manager.theme
        
        if not events:
            with ui.card().classes("w-full").style(card_style().build()):
                ui.label("No activity").classes("text-grey text-center p-8")
            return ui.column().classes("w-full")
        
        # Create virtualized list for large feeds
        def render_event(event: FeedEvent, index: int) -> "ui.element":
            with ui.row().classes("w-full items-start gap-2 px-2 py-1 hover:bg-grey-1") as row:
                row.style(f"background: {t.colors.surface}; border-radius: {t.border_radius.md};")
                
                ui.label(event.timestamp).classes("font-mono text-xs text-grey w-16 shrink-0")
                ui.label(event.icon).classes("text-base shrink-0")
                
                with ui.column().classes("flex-1 min-w-0"):
                    ui.label(event.summary).classes(
                        f"font-mono text-xs text-{event.color} break-all"
                    )
                    if event.raw:
                        ui.label(event.raw).classes("font-mono text-xs text-grey truncate")
            
            return row
        
        scroller, container = create_virtual_list(
            items=list(reversed(events)),  # Show newest first
            render_item=render_event,
            height=300,
            item_height=40,
            overscan=3,
        )
        self._scroller = scroller
        
        # Add live region for announcements
        with ui.column().classes("sr-only"):
            self._live_region.element
        
        return container


class DriverIntentComponent(StatelessComponent[DriverIntent | None]):
    """Driver intent display."""
    
    def render(self) -> "ui.element":
        from nicegui import ui
        from computronium.ui.theme import theme_manager, card_style
        
        intent: DriverIntent | None = self.props  # type: ignore
        t = theme_manager.theme
        
        if not intent or intent.proposing == 0:
            with ui.card().classes("w-full").style(card_style().build()):
                with ui.row().classes("items-center gap-2"):
                    ui.icon("pause").classes("text-grey")
                    ui.label("Idle").classes("text-grey")
            return ui.column().classes("w-full")
        
        with ui.card().classes("w-full").style(card_style().build()) as card:
            with ui.row().classes("w-full items-center gap-3"):
                ui.icon("psychology").classes("text-primary text-2xl")
                
                with ui.column().classes("flex-1"):
                    ui.label(f"Proposing {intent.proposing} cells").classes("font-medium")
                    ui.label(f"Strategy: {intent.strategy_hint}").classes("text-sm text-grey")
                    ui.label(f"Last batch: {intent.last_batch_ago_s:.1f}s ago").classes("text-xs text-grey")
                
                ui.badge("Active", color="primary").props("outline")
        
        return card


class SessionDeltaComponent(StatelessComponent[SessionDelta]):
    """Session statistics display."""
    
    def render(self) -> "ui.element":
        from nicegui import ui
        from computronium.ui.theme import theme_manager, card_style
        
        delta: SessionDelta = self.props  # type: ignore
        t = theme_manager.theme
        
        with ui.card().classes("w-full").style(card_style().build()) as card:
            ui.label("Session Delta").classes("text-h6 mb-3")
            
            with ui.row().classes("w-full gap-4"):
                # Cells
                with ui.column().classes("flex-1 text-center p-3").style(
                    f"background: {t.colors.surface_variant}; border-radius: {t.border_radius.md};"
                ):
                    ui.label(str(delta.cells)).classes("text-3xl font-bold text-primary")
                    ui.label("Cells").classes("text-sm text-grey")
                
                # Records
                with ui.column().classes("flex-1 text-center p-3").style(
                    f"background: {t.colors.surface_variant}; border-radius: {t.border_radius.md};"
                ):
                    ui.label(str(delta.records)).classes("text-3xl font-bold text-success")
                    ui.label("Records").classes("text-sm text-grey")
                
                # Crashes
                with ui.column().classes("flex-1 text-center p-3").style(
                    f"background: {t.colors.surface_variant}; border-radius: {t.border_radius.md};"
                ):
                    color = "error" if delta.crashes > 0 else "success"
                    ui.label(str(delta.crashes)).classes(f"text-3xl font-bold text-{color}")
                    ui.label("Crashes").classes("text-sm text-grey")
        
        return card


# ──────────────────────────────────────────────────────────────────────────────
# Main Monitor Panel
# ──────────────────────────────────────────────────────────────────────────────

class MonitorPanel(Component[MonitorProps, MonitorState]):
    """Main Monitor panel with all sections."""
    
    def initial_state(self) -> MonitorState:
        return MonitorState()
    
    def __init__(self, props: MonitorProps | None = None):
        super().__init__(props)
        
        # Reactive signals for data
        self._loss_signal = signal(list(self.props.data.loss_history) if self.props.data else [])
        self._events_signal = signal(list(self.props.data.feed) if self.props.data else [])
        self._intent_signal = signal(self.props.data.intent if self.props.data else None)
        self._delta_signal = signal(self.props.data.session_delta if self.props.data else SessionDelta())
        
        # Effect to announce new events
        def _announce_events():
            events = self._events_signal.get()
            if events and len(events) > getattr(self, '_last_event_count', 0):
                latest = events[-1]
                announce(f"{latest.icon} {latest.summary}", "polite")
                self._last_event_count = len(events)
        
        effect(_announce_events)
    
    def render(self) -> "ui.element":
        from nicegui import ui
        from computronium.ui.theme import theme_manager
        from computronium.ui.virtualize import create_virtual_list
        
        t = theme_manager.theme
        data = self.props.data
        quiet = self.props.quiet
        
        with ui.column().classes("w-full gap-6") as root:
            # Header with liveness badge
            if data:
                self._render_header(data)
            
            # Health tiles grid
            if data and data.tiles:
                self._render_health_tiles(data.tiles)
            
            # Loss chart
            losses = self._loss_signal.get()
            if losses:
                LossChartComponent(losses).mount(root)
            
            # Driver intent + Session delta row
            with ui.row().classes("w-full gap-4"):
                with ui.column().classes("flex-1 min-w-0"):
                    DriverIntentComponent(self._intent_signal.get()).mount(root)
                
                with ui.column().classes("flex-1 min-w-0"):
                    SessionDeltaComponent(self._delta_signal.get()).mount(root)
            
            # Activity feed (unless quiet)
            if not quiet and data and data.feed:
                ActivityFeedComponent(list(reversed(data.feed))).mount(root)
            
            # Ticker (collapsible)
            if not quiet and data and data.ticker:
                self._render_ticker(data.ticker)
        
        return root
    
    def _render_header(self, data: "MonitorData") -> None:
        from nicegui import ui
        from computronium.ui.theme import theme_manager, badge_style
        
        t = theme_manager.theme
        liv = data.liveness
        
        with ui.row().classes("w-full items-center justify-between"):
            with ui.row().classes("items-center gap-3"):
                ui.label("Monitor").classes("text-h4")
                ui.badge(liv.label, color=liv.color or "grey").props("outline").classes("text-sm")
            
            with ui.row().classes("items-center gap-2"):
                if self.props.on_refresh:
                    ui.button(icon="refresh", on_click=self.props.on_refresh).props(
                        "flat dense round aria-label='Refresh'"
                    ).classes("text-primary")
    
    def _render_health_tiles(self, tiles: list["HealthTile"]) -> None:
        from nicegui import ui
        from computronium.ui.theme import theme_manager
        
        t = theme_manager.theme
        
        with ui.row().classes("w-full flex-wrap gap-3"):
            for tile in tiles:
                HealthTileComponent(tile).mount(ui.column().classes("flex-1 min-w-[200px]"))
    
    def _render_ticker(self, ticker: list[str]) -> None:
        from nicegui import ui
        from computronium.ui.theme import theme_manager
        
        t = theme_manager.theme
        
        with ui.expansion("Log Ticker", icon="description", value=False).classes("w-full"):
            with ui.column().classes("w-full gap-1 max-h-48 overflow-auto"):
                for line in ticker[-50:]:  # Show last 50 lines
                    ui.label(line).classes("font-mono text-xs text-grey px-2 py-0.5")
    
    def update_data(self, data: "MonitorData" | None = None, **kwargs) -> None:
        """Update panel with new data."""
        if data:
            self.props = MonitorProps(data=data, quiet=self.props.quiet, on_refresh=self.props.on_refresh)
            self._loss_signal.set(list(data.loss_history))
            self._events_signal.set(list(data.feed))
            self._intent_signal.set(data.intent)
            self._delta_signal.set(data.session_delta)
    
    def on_mount(self) -> None:
        super().on_mount()
        # Set up periodic refresh if needed
        self.set_timer(2.0, lambda: self.props.on_refresh and self.props.on_refresh())
    
    def on_unmount(self) -> None:
        super().on_unmount()
        # Cleanup timers handled by base class


# ──────────────────────────────────────────────────────────────────────────────
# Factory
# ──────────────────────────────────────────────────────────────────────────────

def create_monitor_panel(data: "MonitorData | None" = None, quiet: bool = False, 
                         on_refresh: Callable[[], None] | None = None) -> MonitorPanel:
    """Factory for MonitorPanel."""
    return MonitorPanel(MonitorProps(data=data, quiet=quiet, on_refresh=on_refresh))