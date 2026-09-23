"""New Computronium Dashboard — integrates all GAME.md UI components.

This replaces the old live_atlas.py dashboard with a fully integrated
implementation using the new UI components from computronium.ui.components.
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any

from nicegui import ui

from computronium.ui.a11y.tokens import a11y_css
from computronium.ui.components.activity_feed import ActivityFeed
from computronium.ui.components.campaign_card import CampaignCardGallery
from computronium.ui.components.constitution_health import ConstitutionHealthPanel
from computronium.ui.components.discovery_map import DiscoveryMap
from computronium.ui.components.episode_timeline import EpisodeTimeline
from computronium.ui.components.field_reports import FieldReports
from computronium.ui.components.genome_health import GenomeHealthTracker
from computronium.ui.components.health_panel import HealthPanel
from computronium.ui.components.lineage_viewer import LineageViewer
from computronium.ui.components.mutation_explorer import MutationExplorer
from computronium.ui.components.preview_shelf import PreviewShelf
from computronium.ui.components.probe_analytics import ProbeAnalytics
from computronium.ui.components.progress_panel import ProgressPanel
from computronium.ui.components.region_naming import RegionNaming
from computronium.ui.components.repair_bench import RepairBench
from computronium.ui.components.stagnation_dashboard import StagnationDashboard
from computronium.ui.components.team_wall import TeamWall
from computronium.ui.components.tradeoffs_panel import TradeoffsPanel
from computronium.ui.components.veto_log import VetoLog
from computronium.ui.components.workshop import WorkshopPanel
from computronium.ui.design_tokens import css_custom_properties
from computronium.ui.event_bus import (
    ArtifactChanged,
    ModeChanged,
    WebSocketEvent,
    event_bus,
)
from computronium.ui.mode_toggle import (
    BasePanel,
    Register,
    get_mode,
    initialize_mode,
    mode_toggle_select,
    set_mode,
)
from computronium.ui.onboarding.quiz import ComfortQuiz
from computronium.ui.onboarding.tour import GuidedTour
from computronium.ui.panel_registry import panel_registry
from computronium.ui.recognition.state_store import RecognitionStateStore
from computronium.visualization.live_atlas import (
    POLL_SECONDS,
    DaemonClient,
    EmbedCache,
    _atlas_data,
    _objectives_from_heartbeat,
    render_snapshot,
    watch_signature,
)

if TYPE_CHECKING:
    from pathlib import Path


logger = logging.getLogger("computronium.ui.dashboard")


# Register all panels with the panel registry
def _register_panels() -> None:
    """Register all panels with the panel registry."""
    from computronium.ui.adapters import get_adapter

    # Explorer panels (visible in both modes)
    panel_registry.register(
        "discovery_map",
        "discovery_map",
        "map",
        factory=DiscoveryMap,
        adapter=get_adapter("discovery_map"),
        order=0,
    )
    panel_registry.register(
        "tradeoffs",
        "tradeoffs",
        "balance",
        factory=TradeoffsPanel,
        adapter=get_adapter("tradeoffs"),
        order=1,
    )
    panel_registry.register(
        "repair_bench",
        "repair_bench",
        "build",
        factory=RepairBench,
        adapter=get_adapter("repair_bench"),
        order=2,
    )
    panel_registry.register(
        "health",
        "health",
        "favorite",
        factory=HealthPanel,
        adapter=get_adapter("health"),
        order=3,
    )
    panel_registry.register(
        "campaigns",
        "campaign_card",
        "description",
        factory=lambda: CampaignCardGallery,
        adapter=get_adapter("campaigns"),
        order=4,
        visible_predicate=lambda _: True,
    )
    panel_registry.register(
        "preview",
        "preview_shelf",
        "visibility",
        factory=PreviewShelf,
        adapter=get_adapter("preview"),
        order=5,
    )
    panel_registry.register(
        "region_naming",
        "region_naming",
        "label",
        factory=RegionNaming,
        adapter=get_adapter("region_naming"),
        order=6,
    )
    panel_registry.register(
        "team",
        "team_wall",
        "groups",
        factory=TeamWall,
        adapter=get_adapter("team"),
        order=7,
    )
    panel_registry.register(
        "activity_feed",
        "activity_feed",
        "feed",
        factory=ActivityFeed,
        adapter=get_adapter("activity_feed"),
        order=8,
    )
    panel_registry.register(
        "field_reports",
        "field_reports",
        "article",
        factory=FieldReports,
        adapter=get_adapter("field_reports"),
        order=9,
    )

    # Lab-only panels
    panel_registry.register(
        "constitution",
        "constitution_health",
        "shield",
        factory=ConstitutionHealthPanel,
        adapter=get_adapter("constitution"),
        order=10,
        visible_predicate=lambda ctx: ctx.get("mode") != "explorer",
    )
    panel_registry.register(
        "lineage",
        "lineage_viewer",
        "account_tree",
        factory=LineageViewer,
        adapter=get_adapter("lineage"),
        order=11,
        visible_predicate=lambda ctx: ctx.get("mode") != "explorer",
    )
    panel_registry.register(
        "episodes",
        "episode_timeline",
        "event",
        factory=EpisodeTimeline,
        adapter=get_adapter("episodes"),
        order=12,
        visible_predicate=lambda ctx: ctx.get("mode") != "explorer",
    )
    panel_registry.register(
        "progress",
        "progress",
        "emoji_events",
        factory=lambda: ProgressPanel(gamify_enabled=True),
        adapter=get_adapter("progress"),
        order=13,
        visible_predicate=lambda ctx: ctx.get("gamify", True),
    )
    panel_registry.register(
        "workshop",
        "workshop",
        "settings",
        factory=WorkshopPanel,
        adapter=get_adapter("workshop"),
        order=14,
        visible_predicate=lambda ctx: ctx.get("ui_actions", False),
    )
    # Auto-Evolve instrumentation (Lab mode)
    panel_registry.register(
        "probe_analytics",
        "probe_analytics",
        "biotech",
        factory=ProbeAnalytics,
        adapter=get_adapter("probe_analytics"),
        order=15,
        visible_predicate=lambda ctx: ctx.get("mode") != "explorer",
    )
    panel_registry.register(
        "stagnation",
        "stagnation_dashboard",
        "show_chart",
        factory=StagnationDashboard,
        adapter=get_adapter("stagnation"),
        order=16,
        visible_predicate=lambda ctx: ctx.get("mode") != "explorer",
    )
    panel_registry.register(
        "genome_health",
        "genome_health",
        "monitor_heart",
        factory=GenomeHealthTracker,
        adapter=get_adapter("genome_health"),
        order=17,
        visible_predicate=lambda ctx: ctx.get("mode") != "explorer",
    )
    panel_registry.register(
        "mutations",
        "mutations",
        "science",
        factory=MutationExplorer,
        adapter=get_adapter("mutations"),
        order=18,
        visible_predicate=lambda ctx: ctx.get("mode") != "explorer",
    )
    panel_registry.register(
        "veto_log",
        "veto_log",
        "block",
        factory=VetoLog,
        adapter=get_adapter("veto_log"),
        order=19,
        visible_predicate=lambda ctx: ctx.get("mode") != "explorer",
    )


# Initialize panel registry
_register_panels()


class DashboardApp:
    """Main dashboard application with panel routing."""

    def __init__(
        self,
        root: Path,
        log_path: Path | None,
        poll_seconds: float,
        daemon_url: str | None,
        ui_mode: str,
        gamify: bool,
        ui_actions: bool,
        rebuild_state: bool,
    ):
        self.root = root
        self.log_path = log_path
        self.poll_seconds = poll_seconds
        self.daemon_url = daemon_url
        self.gamify = gamify
        self.ui_actions = ui_actions
        self.rebuild_state = rebuild_state

        # Initialize mode
        if ui_mode != "auto":
            initialize_mode()
            set_mode(Register(ui_mode))  # type: ignore[arg-type]
        else:
            initialize_mode()

        # State
        self.current_panel = "discovery_map"
        self.cache = EmbedCache()
        self.client = DaemonClient(daemon_url) if daemon_url else None
        self.objectives = _objectives_from_heartbeat(root)
        self.pareto_state = {
            "selected": "accuracy + walltime",
            "objectives": self.objectives,
        }
        self.pareto_presets = {
            "accuracy + walltime": ("accuracy", "walltime_s"),
            "accuracy + params": ("accuracy", "param_count"),
            "accuracy + flops": ("accuracy", "flops"),
            "accuracy + memory": ("accuracy", "memory_mb"),
            "accuracy + energy": ("accuracy", "energy_per_step"),
            "walltime + params": ("walltime_s", "param_count"),
            "accuracy + bp_deficit": ("accuracy", "bp_deficit"),
            "stability + plasticity": ("spectral_radius", "psi_capacity"),
        }

        # Recognition state store (for progress panel)
        self.recognition_store = None
        if gamify:
            self.recognition_store = RecognitionStateStore(
                db_path=root / "ui_state.sqlite"
            )
            if rebuild_state:
                self.recognition_store.rebuild_from_events()

        # Stream state
        self.loss_history = []
        self.event_history = []
        self.last_signature = watch_signature(root)

        # Panel instances (lazy-loaded)
        self._panels: dict[str, BasePanel] = {}
        self._panel_data: dict[str, Any] = {}

        # UI containers
        self.left_drawer: Any = None
        self.main_content: Any = None
        self.header: Any = None
        self.pareto_selector: Any = None

        # Subscribe to event bus
        self._unsubscribe_artifact = event_bus.subscribe(
            ArtifactChanged, self._on_artifact_changed
        )
        self._unsubscribe_mode = event_bus.subscribe(ModeChanged, self._on_mode_changed)

    def _on_artifact_changed(self, event: ArtifactChanged) -> None:
        """Handle artifact change event."""
        self.last_signature = event.signature
        self._refresh_cheap()

    def _on_mode_changed(self, event: ModeChanged) -> None:
        """Handle mode change event."""
        self._rebuild_left_drawer()
        self._render_current_panel()

    def _get_panel(self, key: str) -> BasePanel:
        """Lazy-load panel instance."""
        if key in self._panels:
            return self._panels[key]

        spec = panel_registry.get(key)
        if spec is None:
            raise ValueError(f"Unknown panel: {key}")

        factory = spec.factory
        if callable(factory) and not isinstance(factory, type):
            # Handle lambda factories that need context
            self._panels[key] = factory()
        else:
            self._panels[key] = factory()
        return self._panels[key]

    def _get_panel_data(self, key: str) -> Any:
        """Get or compute panel data using adapter."""
        if key in self._panel_data:
            return self._panel_data[key]

        spec = panel_registry.get(key)
        if spec is None or spec.adapter is None:
            return None

        # Get snapshot and adapt
        snapshot = render_snapshot(
            self.root,
            self.log_path,
            self.cache,
            objectives=self.pareto_state["objectives"],
            with_atlas=(key == "discovery_map"),
        )
        # Special handling for progress panel with recognition store
        if key == "progress" and self.recognition_store is not None:
            data = spec.adapter.adapt(snapshot, self.root, self.recognition_store)
        else:
            data = spec.adapter.adapt(snapshot, self.root)
        self._panel_data[key] = data
        return data

    def _clear_panel_data(self, key: str | None = None) -> None:
        """Clear cached panel data."""
        if key is None:
            self._panel_data.clear()
        else:
            self._panel_data.pop(key, None)

    def _is_panel_visible(self, key: str) -> bool:
        """Check if panel should be visible in current mode."""
        mode = get_mode()
        context = {"mode": mode, "gamify": self.gamify, "ui_actions": self.ui_actions}
        spec = panel_registry.get(key)
        if spec is None:
            return False
        return spec.visible_predicate(context)

    def _build_header(self) -> None:
        """Build the top header with mode toggle and pareto selector."""
        with ui.header().classes(
            "items-center justify-between bg-primary text-white"
        ) as self.header:
            with ui.row().classes("items-center gap-4"):
                ui.label("Computronium").classes("text-h6 q-mb-none")
                ui.label("Live Broad Map").classes("text-caption text-white/80")
                ui.separator().props("vertical").classes("mx-2")

                # Pareto objective selector
                with ui.row().classes("items-center gap-2"):
                    ui.label("Pareto:").classes("text-sm text-white/90")
                    self.pareto_selector = (
                        ui
                        .select(
                            options=list(self.pareto_presets.keys()),
                            value=self.pareto_state["selected"],
                            on_change=self._on_pareto_change,  # type: ignore[arg-type]
                        )
                        .props("dense outlined")
                        .classes("w-48")
                        .style("color: white;")
                    )

            with ui.row().classes("items-center gap-4"):
                # Mode toggle
                mode_toggle_select()
                # Gamify toggle
                if self.gamify:
                    ui.switch("Gamify", value=True).props("color=white").classes(
                        "text-white"
                    )
                # Tour button
                ui.button(icon="help_outline", on_click=self._start_tour).props(
                    "flat round color=white"
                ).classes("text-white")
                # Quiz button
                ui.button(icon="psychology", on_click=self._start_quiz).props(
                    "flat round color=white"
                ).classes("text-white")

    def _build_left_drawer(self) -> None:
        """Build left navigation drawer with panel list."""
        self.left_drawer = ui.left_drawer(value=True).classes(
            "bg-grey-1 dark:bg-grey-9"
        )
        with self.left_drawer:
            ui.label("Navigation").classes("text-h6 q-mb-md px-4")

            with ui.column().classes("w-full gap-1 px-2"):
                for spec in panel_registry.visible_specs({
                    "mode": get_mode(),
                    "gamify": self.gamify,
                    "ui_actions": self.ui_actions,
                }):
                    key = spec.key
                    is_active = key == self.current_panel
                    btn = (
                        ui
                        .button(
                            icon=spec.icon,
                            on_click=lambda _e, k=key: self._switch_panel(k),
                        )
                        .props(
                            f"flat no-caps {'color=primary' if is_active else ''} dense"
                        )
                        .classes(
                            "w-full justify-start text-left"
                            + (
                                " bg-primary text-white"
                                if is_active
                                else " hover:bg-grey-2 dark:hover:bg-grey-8"
                            )
                        )
                    )
                    with btn:
                        ui.icon(spec.icon).classes("mr-2")
                        ui.label(spec.label_key)

    def _rebuild_left_drawer(self) -> None:
        """Rebuild left drawer on mode change."""
        if self.left_drawer:
            self.left_drawer.clear()
            with self.left_drawer:
                self._build_left_drawer()

    def _switch_panel(self, key: str) -> None:
        """Switch to a different panel."""
        if not self._is_panel_visible(key):
            return
        self.current_panel = key
        self._render_current_panel()
        if self.left_drawer:
            self.left_drawer.update()

    def _render_current_panel(self) -> None:
        """Render the currently selected panel."""
        self.main_content.clear()
        with self.main_content:
            panel = self._get_panel(self.current_panel)
            data = self._get_panel_data(self.current_panel)
            if data is not None and hasattr(panel, "update_data"):
                panel.update_data(data)
            panel.render()

    def _on_pareto_change(self, value: str) -> None:  # type: ignore[arg-type]
        """Handle Pareto objective selector change."""
        self.pareto_state["selected"] = value
        obj_names = self.pareto_presets[value]
        from computronium.autoscientist.objectives import (
            parse_objectives,
        )

        self.pareto_state["objectives"] = parse_objectives(",".join(obj_names))
        self._clear_panel_data()
        self._render_current_panel()

    def _start_tour(self) -> None:
        """Start the guided tour."""
        tour = GuidedTour()
        tour.start()

    def _start_quiz(self) -> None:
        """Start the comfort quiz."""
        quiz = ComfortQuiz()
        quiz.start()

    def _refresh_lifecycle(self) -> None:
        """Refresh lifecycle badge, active cell inspector, event panel."""
        # This would be in a separate area - for now just update if daemon connected

    def _refresh_cheap(self) -> None:
        """Fast paint: everything except UMAP fit."""
        render_snapshot(
            self.root,
            self.log_path,
            self.cache,
            objectives=self.pareto_state["objectives"],
            with_atlas=False,
        )

        # Update panels that need live data
        for key in {
            "discovery_map",
            "tradeoffs",
            "repair_bench",
            "health",
            "activity_feed",
            "field_reports",
        }:
            if key in self._panels:
                self._panel_data.pop(key, None)
                if hasattr(self._panels[key], "update_data"):
                    data = self._get_panel_data(key)
                    if data is not None:
                        self._panels[key].update_data(data)

        # Check for artifact changes and publish event
        new_sig = watch_signature(self.root)
        if new_sig != self.last_signature:
            self.last_signature = new_sig
            event_bus.publish(ArtifactChanged(signature=new_sig, root=self.root))
            self._render_current_panel()

    async def _load_atlas(self) -> None:
        """Off-thread UMAP refit."""
        from nicegui import run

        try:
            result = await run.io_bound(_atlas_data, self.root, self.cache)
            figure, _, _ = result  # type: ignore[misc]
            if self.current_panel == "discovery_map":
                panel = self._get_panel("discovery_map")
                if hasattr(panel, "update_data"):
                    panel.update_data(atlas_figure=figure)  # type: ignore[attr-defined]
                # Also update cached data
                self._panel_data.pop("discovery_map", None)
        except Exception as e:
            logger.warning("Atlas load failed: %s", e)

    def _poll(self) -> None:
        """Poll for artifact changes."""
        new_sig = watch_signature(self.root)
        if new_sig != self.last_signature:
            self.last_signature = new_sig
            # Publish artifact changed event
            event_bus.publish(ArtifactChanged(signature=new_sig, root=self.root))
            self._refresh_cheap()

    def _telemetry_consumer(self) -> Any:
        """Telemetry WebSocket consumer."""
        import json

        import websockets

        if not self.daemon_url:
            return

        async def _consume() -> None:
            ws_url = f"{self.daemon_url.replace('http://', 'ws://')}/ws/telemetry"  # type: ignore[union-attr]
            try:
                async with websockets.connect(ws_url) as ws:
                    async for message in ws:
                        record = json.loads(message)
                        loss = record.get("train_loss", record.get("loss"))
                        if isinstance(loss, int | float):
                            self.loss_history.append(float(loss))
                            if len(self.loss_history) > 60:
                                self.loss_history.pop(0)
                            # Publish telemetry event
                            event_bus.publish(
                                WebSocketEvent(topic="telemetry", payload=record)
                            )
                            self._refresh_lifecycle()
            except OSError:
                pass

        return _consume()

    def _events_consumer(self) -> Any:
        """Events WebSocket consumer."""
        import json

        import websockets

        from computronium.visualization.live_atlas import (
            _classify_event,
            _toast_for_alert,
        )

        if not self.daemon_url:
            return

        async def _consume() -> None:
            ws_url = f"{self.daemon_url.replace('http://', 'ws://')}/ws/events"  # type: ignore[union-attr]
            try:
                async with websockets.connect(ws_url) as ws:
                    async for message in ws:
                        raw = json.loads(message)
                        now = time.time()
                        ev = _classify_event(raw, now)
                        self.event_history.append(ev)
                        if len(self.event_history) > 100:
                            self.event_history.pop(0)
                        _toast_for_alert(ev)
                        # Publish events event
                        event_bus.publish(WebSocketEvent(topic="events", payload=raw))
                        self._refresh_lifecycle()
            except OSError:
                pass

        return _consume()

    def _start_stream_timers(self) -> None:
        """Start WebSocket consumers for telemetry and events."""
        from nicegui import ui

        ui.timer(self.poll_seconds, self._telemetry_consumer)
        ui.timer(self.poll_seconds, self._events_consumer)

    def build(self) -> None:
        """Build the complete dashboard UI."""
        # Inject design tokens and a11y CSS
        ui.add_head_html(f"<style>{css_custom_properties()}</style>")
        ui.add_head_html(f"<style>{a11y_css()}</style>")

        # Page title
        ui.page_title("Computronium — Live Broad Map")

        # Build header
        self._build_header()

        # Build left drawer
        self._build_left_drawer()

        # Main content area
        self.main_content = (
            ui.column().classes("w-full p-4 q-ma-auto").style("max-width: 1400px;")
        )

        # Initial render
        self._render_current_panel()

        # Set up timers
        ui.timer(0.5, self._load_atlas, once=True)
        ui.timer(self.poll_seconds, self._poll)

        # Start stream timers if daemon connected
        if self.client is not None:
            self._start_stream_timers()


def build_dashboard(
    root: Path,
    log_path: Path | None = None,
    poll_seconds: float = POLL_SECONDS,
    daemon_url: str | None = None,
    *,
    ui_mode: str = "auto",
    gamify: bool = True,
    ui_actions: bool = False,
    rebuild_state: bool = False,
) -> None:
    """Build the new integrated Computronium dashboard.

    This is the main entry point called from the CLI.
    """
    app = DashboardApp(
        root=root,
        log_path=log_path,
        poll_seconds=poll_seconds,
        daemon_url=daemon_url,
        ui_mode=ui_mode,
        gamify=gamify,
        ui_actions=ui_actions,
        rebuild_state=rebuild_state,
    )
    app.build()
