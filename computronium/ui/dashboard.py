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
from computronium.ui.components.campaign_card import CampaignCardGallery
from computronium.ui.components.constitution_health import ConstitutionHealthPanel
from computronium.ui.components.discovery_map import DiscoveryMap
from computronium.ui.components.episode_timeline import EpisodeTimeline
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

if TYPE_CHECKING:
    from pathlib import Path
from computronium.ui.components.tradeoffs_panel import TradeoffsPanel
from computronium.ui.components.veto_log import VetoLog
from computronium.ui.components.workshop import WorkshopPanel
from computronium.ui.design_tokens import css_custom_properties
from computronium.ui.glossary_service import tr
from computronium.ui.mode_toggle import (
    BasePanel,
    get_mode,
    initialize_mode,
    mode_toggle_select,
    set_mode,
)
from computronium.ui.onboarding.quiz import ComfortQuiz
from computronium.ui.onboarding.tour import GuidedTour
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

logger = logging.getLogger("computronium.ui.dashboard")

# Panel definitions for left rail navigation
PANELS = [
    ("discovery_map", "discovery_map", "map", "Discovery Map"),
    ("tradeoffs", "tradeoffs", "balance", "Trade-offs"),
    ("repair_bench", "repair_bench", "build", "Repair Bench"),
    ("health", "health", "favorite", "Health"),
    ("constitution", "constitution", "shield", "Constitution"),
    ("lineage", "lineage", "account_tree", "Lineage"),
    ("episodes", "episodes", "event", "Episodes"),
    ("progress", "progress", "emoji_events", "Progress"),
    ("workshop", "workshop", "settings", "Workshop"),
    ("campaigns", "campaigns", "description", "Campaigns"),
    ("preview", "preview", "visibility", "Preview"),
    ("region_naming", "region_naming", "label", "Region Names"),
    ("team", "team", "groups", "Team"),
    # Auto-Evolve instrumentation (Lab mode)
    ("probe_analytics", "probe_analytics", "biotech", "Probe Analytics"),
    ("stagnation", "stagnation", "show_chart", "Stagnation"),
    ("genome_health", "genome_health", "monitor_heart", "Genome Health"),
    ("mutations", "mutations", "science", "Mutations"),
    ("veto_log", "veto_log", "block", "Veto Log"),
]

# Panels that are Lab-mode only (hidden in Explorer by default)
LAB_ONLY_PANELS = {
    "constitution",
    "lineage",
    "episodes",
    "probe_analytics",
    "stagnation",
    "genome_health",
    "mutations",
    "veto_log",
}

# Panels that require gamification enabled
GAMIFY_PANELS = {"progress"}


def _panel_label(key: str, gamify: bool) -> str:
    """Get localized label for panel."""
    labels = {
        "discovery_map": tr("discovery_map"),
        "tradeoffs": tr("tradeoffs"),
        "repair_bench": tr("repair_bench"),
        "health": tr("health"),
        "constitution": tr("constitution_health"),
        "lineage": tr("lineage_viewer"),
        "episodes": tr("episode_timeline"),
        "progress": tr("progress"),
        "workshop": tr("workshop"),
        "campaigns": tr("campaign_card"),
        "preview": tr("preview_shelf"),
        "region_naming": tr("region_naming"),
        "team": tr("team_wall"),
        "probe_analytics": tr("probe_analytics"),
        "stagnation": tr("stagnation_dashboard"),
        "genome_health": tr("genome_health"),
        "mutations": tr("mutation_explorer"),
        "veto_log": tr("veto_log"),
    }
    return labels.get(key, key.replace("_", " ").title())


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
            from computronium.ui.mode_toggle import Register

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

        # UI containers
        self.left_drawer: Any = None
        self.main_content: Any = None
        self.header: Any = None
        self.pareto_selector: Any = None

    def _get_panel(self, key: str) -> BasePanel:
        """Lazy-load panel instance."""
        if key in self._panels:
            return self._panels[key]

        panel_map = {
            "discovery_map": DiscoveryMap,
            "tradeoffs": TradeoffsPanel,
            "repair_bench": RepairBench,
            "health": HealthPanel,
            "constitution": ConstitutionHealthPanel,
            "lineage": LineageViewer,
            "episodes": EpisodeTimeline,
            "progress": lambda: ProgressPanel(gamify_enabled=self.gamify),
            "workshop": WorkshopPanel,
            "campaigns": lambda: CampaignCardGallery(self.root / "campaigns"),
            "preview": PreviewShelf,
            "region_naming": RegionNaming,
            "team": TeamWall,
            "probe_analytics": ProbeAnalytics,
            "stagnation": StagnationDashboard,
            "genome_health": GenomeHealthTracker,
            "mutations": MutationExplorer,
            "veto_log": VetoLog,
        }

        if key in panel_map:
            factory = panel_map[key]
            if callable(factory) and not isinstance(factory, type):
                self._panels[key] = factory()  # type: ignore[assignment]
            else:
                self._panels[key] = factory()  # type: ignore[assignment]
            return self._panels[key]

        # Fallback - should not be reached
        raise ValueError(f"Unknown panel: {key}")

    def _is_panel_visible(self, key: str) -> bool:
        """Check if panel should be visible in current mode."""
        mode = get_mode()
        if key in LAB_ONLY_PANELS and mode == "explorer":
            return False
        if key in GAMIFY_PANELS and not self.gamify:
            return False
        return not (key == "workshop" and not self.ui_actions)

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
                for key, _, icon, _ in PANELS:
                    if not self._is_panel_visible(key):
                        continue

                    is_active = key == self.current_panel
                    btn = (
                        ui
                        .button(
                            icon=icon,
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
                        ui.icon(icon).classes("mr-2")
                        ui.label(_panel_label(key, self.gamify))

    def _switch_panel(self, key: str) -> None:
        """Switch to a different panel."""
        if not self._is_panel_visible(key):
            return
        self.current_panel = key
        self._render_current_panel()
        self.left_drawer.update()

    def _render_current_panel(self) -> None:
        """Render the currently selected panel."""
        self.main_content.clear()
        with self.main_content:
            panel = self._get_panel(self.current_panel)
            panel.render()

    def _on_pareto_change(self, value: str) -> None:  # type: ignore[arg-type]
        """Handle Pareto objective selector change."""
        self.pareto_state["selected"] = value
        obj_names = self.pareto_presets[value]
        from computronium.autoscientist.objectives import (
            parse_objectives,
        )

        self.pareto_state["objectives"] = parse_objectives(",".join(obj_names))
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
        if self.current_panel in {
            "discovery_map",
            "tradeoffs",
            "repair_bench",
            "health",
        }:
            self._render_current_panel()

        # Check for artifact changes
        new_sig = watch_signature(self.root)
        if new_sig != self.last_signature:
            self.last_signature = new_sig
            self._render_current_panel()

    async def _load_atlas(self) -> None:
        """Off-thread UMAP refit."""
        from nicegui import run

        try:
            result = await run.io_bound(_atlas_data, self.root, self.cache)
            figure, note, errors = result  # type: ignore[misc]
            if self.current_panel == "discovery_map":
                panel = self._get_panel("discovery_map")
                if hasattr(panel, "update_atlas"):
                    panel.update_atlas(figure, note, errors)  # type: ignore[attr-defined]
        except Exception as e:
            logger.warning("Atlas load failed: %s", e)

    def _poll(self) -> None:
        """Poll for artifact changes."""
        new_sig = watch_signature(self.root)
        if new_sig != self.last_signature:
            self.last_signature = new_sig
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
