"""Computronium Dashboard — five-panel architecture with lens system.

Panels: Map / Repair / Console / Composer / Record
Lenses: Map→(Map, Trade-offs, Gallery), Repair→(Defects, Maturation), Record→(History, Ledger, Lessons)
Navigation: header tabs + command palette (⌘K) + panel hotkeys 1–5
Status chip: persistent header with deep links
URL state: panel/lens/filters/selection encoded
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from nicegui import ui

from computronium.ui.a11y.tokens import a11y_css
from computronium.ui.adapters import get_adapter
from computronium.ui.components import (
    CampaignInfo,
    Composer,
    Console,
    ConsoleData,
    DiscoveryMap,
    DriverIntent,
    Record,
    RecordData,
    RepairBench,
    StatusChip,
)
from computronium.ui.components.record import RecordLens as ComponentRecordLens
from computronium.ui.components.status_chip import StatusChipData
from computronium.ui.design_tokens import PRIMARY, SECONDARY, css_custom_properties
from computronium.ui.event_bus import (
    ArtifactChanged,
    ConfigChanged,
    ModeChanged,
    WebSocketEvent,
    event_bus,
)
from computronium.ui.lenses import (
    MapLens,
    PanelLenses,
    RepairLens,
    parse_deep_link,
)
from computronium.ui.lenses import (
    RecordLens as LensRecordLens,
)
from computronium.ui.metrics import metrics
from computronium.ui.mode_toggle import (
    get_mode,
    initialize_mode,
    mode_toggle_select,
    set_mode,
)
from computronium.ui.panel_registry import panel_registry
from computronium.visualization.live_atlas import (
    POLL_SECONDS,
    DaemonClient,
    DashboardSnapshot,
    EmbedCache,
    _objectives_from_heartbeat,
    render_snapshot,
    resolve_log_path,
    watch_signature,
)

if TYPE_CHECKING:
    from plotly.graph_objects import Figure

    from computronium.autoscientist.objectives import ObjectiveSpec

logger = logging.getLogger("computronium.ui.dashboard")

# Panels that support lenses
_LENS_PANELS: frozenset[str] = frozenset({"map", "repair", "record"})


# Register all 5 panels with lenses
def _register_panels() -> None:
    """Register the five core panels with their lenses."""

    # Map panel with 3 lenses
    panel_registry.register(
        "map",
        "map",
        "map",
        factory=DiscoveryMap,
        adapter=get_adapter("discovery_map"),
        order=0,
        lenses={
            MapLens.MAP: "Map",
            MapLens.TRADEOFFS: "Trade-offs",
            MapLens.GALLERY: "Gallery",
        },
        default_lens=MapLens.MAP,
    )

    # Repair panel with 2 lenses
    panel_registry.register(
        "repair",
        "repair",
        "build",
        factory=RepairBench,
        adapter=get_adapter("repair_bench"),
        order=1,
        lenses={
            RepairLens.DEFECTS: "Defects",
            RepairLens.MATURATION: "Maturation",
        },
        default_lens=RepairLens.DEFECTS,
    )

    # Console panel (no lenses)
    panel_registry.register(
        "console",
        "console",
        "terminal",
        factory=Console,
        adapter=None,  # Uses live WS + snapshot
        order=2,
        lenses={},
    )

    # Composer panel (no lenses)
    panel_registry.register(
        "composer",
        "composer",
        "tune",
        factory=Composer,
        adapter=None,  # No adapter needed
        order=3,
        lenses={},
    )

    # Record panel with 3 lenses
    panel_registry.register(
        "record",
        "record",
        "history",
        factory=Record,
        adapter=None,  # Uses derived data from snapshot
        order=4,
        lenses={
            LensRecordLens.HISTORY: "History",
            LensRecordLens.LEDGER: "Ledger",
            LensRecordLens.LESSONS: "Lessons",
        },
        default_lens=LensRecordLens.HISTORY,
    )


_register_panels()


class DashboardApp:
    """Main dashboard application with 5-panel routing and lens system."""

    _CONFIG_WATCHED = ("campaign.yaml", "heartbeat.json")

    def __init__(
        self,
        root: Path,
        log_path: Path | None,
        poll_seconds: float,
        daemon_url: str | None,
        ui_mode: str,
        ui_actions: bool,
        quiet: bool,
        *,
        roots: tuple[Path, ...] | None = None,
    ):
        self.roots: tuple[Path, ...] = roots or (root,)
        self.root = root
        self._explicit_log_path = log_path
        self.log_path = resolve_log_path(root, log_path)
        self.poll_seconds = poll_seconds
        self.daemon_url = daemon_url
        self.ui_actions = ui_actions
        self.quiet = quiet

        # Initialize mode
        initialize_mode()
        if ui_mode != "auto":
            set_mode(ui_mode)  # type: ignore[arg-type]

        # State
        self.current_panel = PanelLenses.MAP
        self.current_lens = MapLens.MAP
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

        # Stream state
        self.loss_history: list[float] = []
        self.event_history: list[Any] = []
        self.last_signature = watch_signature(root)
        self._last_ws_paint = 0.0

        # One render_snapshot per refresh cycle
        self._snapshot: DashboardSnapshot | None = None
        self._snapshot_has_atlas = False

        # Campaign config signature for hot-reload
        self._config_signature = self._config_signature_of()
        self._last_config_signature = self._config_signature

        # Panel instances (lazy-loaded)
        self._panels: dict[str, Any] = {}
        self._panel_data: dict[str, Any] = {}

        # UI containers
        self.header: Any = None
        self.main_content: Any = None
        self.pareto_selector: Any = None
        self.root_selector: Any = None
        self.status_chip: StatusChip | None = None
        self.command_palette: Any = None

        # Session tracking
        self._session_start = time.time()
        self._session_cells_at_start = 0
        self._session_records_at_start = 0
        self._session_crashes_at_start = 0

        # Subscribe to event bus
        self._unsubscribe_artifact = event_bus.subscribe(
            ArtifactChanged, self._on_artifact_changed
        )
        self._unsubscribe_mode = event_bus.subscribe(ModeChanged, self._on_mode_changed)
        self._unsubscribe_ws = event_bus.subscribe(WebSocketEvent, self._on_ws_event)
        self._unsubscribe_config = event_bus.subscribe(
            ConfigChanged, self._on_config_changed
        )

    def _on_artifact_changed(self, event: ArtifactChanged) -> None:
        """Handle artifact change event (ignore foreign roots)."""
        if event.root != self.root:
            return
        self.last_signature = event.signature
        self._refresh_cheap()

    def _on_mode_changed(self, event: ModeChanged) -> None:
        """Handle mode change event."""
        self._render_header()
        self._render_current_panel()

    def _on_config_changed(self, event: ConfigChanged) -> None:
        """Campaign objectives changed — recompute panels once."""
        from computronium.autoscientist.objectives import parse_objectives

        try:
            objectives = parse_objectives(",".join(event.objectives))
        except ValueError:
            logger.warning("Ignoring unparsable ConfigChanged: %s", event.objectives)
            return
        if objectives == self.pareto_state["objectives"]:
            return
        self.pareto_state["objectives"] = objectives
        self._clear_panel_data()
        self._render_current_panel()

    _WS_PAINT_INTERVAL_S = 2.0

    def _on_ws_event(self, event: WebSocketEvent) -> None:
        """Route WebSocket events with ≤1/2s paint throttling."""
        metrics.inc("dashboard_ws_events_total", labels={"topic": event.topic})
        now = time.time()
        match event.topic:
            case "events":
                self._route_ws_events(event.payload, now)
            case "telemetry":
                self._route_ws_telemetry(event.payload)
            case _:
                logger.debug("Unhandled WS topic: %s", event.topic)

    def _route_ws_events(self, raw: dict[str, Any], now: float) -> None:
        """Fan out a classified /ws/events record to console + status chip."""
        from computronium.ui.components.activity_feed import FeedEvent
        from computronium.visualization.live_atlas import (
            _classify_event,
            _toast_for_alert,
        )

        ev = _classify_event(raw, now)
        _toast_for_alert(ev)
        self.event_history.append(ev)
        if len(self.event_history) > 100:
            self.event_history.pop(0)

        # Update console panel if active
        if (console := self._panel_as("console", Console)) is not None:
            feed_event = FeedEvent(
                timestamp=ev.timestamp,
                icon=ev.icon,
                color=ev.color,
                summary=ev.summary,
                raw=str(raw),
            )
            console.add_stream_event(feed_event)

            # Add field report for alert events (breakthrough/cascade/completion)
            if ev.kind == "alert":
                from computronium.ui.components.field_reports import FieldReport

                field_report = FieldReport(
                    icon=ev.icon,
                    color=ev.color,
                    sentence=ev.summary,
                    deep_link=None,
                    unread=True,
                )
                console.add_report(field_report)

            # Parse driver intent from proposal_batch
            if ev.kind == "proposal_batch":
                n = raw.get("n_proposals", raw.get("count", 0))
                _ = raw.get("quarantined", 0)
                _ = raw.get("voids_pruned", 0)
                primitives = []
                if "dynamics" in raw:
                    primitives.append(raw["dynamics"])
                if "credit" in raw:
                    primitives.append(raw["credit"])
                strategy = "·".join(primitives) if primitives else "exploring"
                console.data = ConsoleData(
                    campaigns=console.data.campaigns,
                    active_campaign=console.data.active_campaign,
                    liveness=console.data.liveness,
                    driver_intent=DriverIntent(
                        proposing=n,
                        last_batch_ago_s=0,  # Just now
                        strategy_hint=strategy,
                    ),
                    session_delta=console.data.session_delta,
                    loss_history=console.data.loss_history,
                    ticker=console.data.ticker,
                    reports=console.data.reports,
                )

            # Increment session delta for crashes
            if ev.kind == "defect_quarantined":
                console.increment_session_delta(crashes=1)

        # Update status chip
        snapshot = self._snapshot_for(with_atlas=False)
        self._update_status_chip(snapshot)

    def _route_ws_telemetry(self, payload: dict[str, Any]) -> None:
        """Push loss history to console panel (throttled paint)."""
        now = time.time()
        if now - self._last_ws_paint < self._WS_PAINT_INTERVAL_S:
            return
        self._last_ws_paint = now
        loss = payload.get("train_loss", payload.get("loss"))
        if isinstance(loss, int | float):
            self.loss_history.append(float(loss))
            if len(self.loss_history) > 60:
                self.loss_history.pop(0)
            if (console := self._panel_as("console", Console)) is not None:
                console.add_loss_point(float(loss))

    def _get_panel(self, key: str) -> Any:
        """Lazy-load panel instance."""
        if key in self._panels:
            return self._panels[key]

        spec = panel_registry.get(key)
        if spec is None:
            raise ValueError(f"Unknown panel: {key}")

        self._panels[key] = spec.factory()
        return self._panels[key]

    def _panel_as(self, key: str, typ: type) -> Any | None:
        """Typed panel lookup."""
        panel = self._panels.get(key)
        return panel if isinstance(panel, typ) else None

    def _snapshot_for(self, *, with_atlas: bool) -> DashboardSnapshot:
        """One render_snapshot per refresh cycle."""
        if self._snapshot is None or (with_atlas and not self._snapshot_has_atlas):
            start = time.perf_counter()
            self._snapshot = render_snapshot(
                self.root,
                self.log_path,
                self.cache,
                objectives=self.pareto_state["objectives"],
                with_atlas=with_atlas,
                event_history=list(self.event_history),
            )
            metrics.observe_seconds("dashboard_snapshot", time.perf_counter() - start)
            self._snapshot_has_atlas = with_atlas
        return self._snapshot

    def _get_panel_data(self, key: str) -> Any:
        """Get or compute panel data using the panel's adapter."""
        if key in self._panel_data:
            return self._panel_data[key]

        spec = panel_registry.get(key)
        if spec is None or spec.adapter is None:
            return None

        snapshot = self._snapshot_for(with_atlas=key == "map")
        from computronium.ui.data_adapters import AdapterContext

        ctx = AdapterContext(root=self.root, snapshot=snapshot)
        start = time.perf_counter()
        data = spec.adapter.adapt(ctx)
        metrics.observe_seconds("dashboard_adapter", time.perf_counter() - start)
        self._panel_data[key] = data
        return data

    def _clear_panel_data(self, key: str | None = None) -> None:
        """Clear cached panel data and the cycle snapshot."""
        if key is None:
            self._panel_data.clear()
            self._snapshot = None
            self._snapshot_has_atlas = False
        else:
            self._panel_data.pop(key, None)

    def _is_panel_visible(self, key: str) -> bool:
        """Check if panel should be visible in current mode."""
        mode = get_mode()
        context = {"mode": mode, "ui_actions": self.ui_actions}
        spec = panel_registry.get(key)
        if spec is None:
            return False
        return spec.visible_predicate(context)

    def _render_header(self) -> None:
        """Build the top header with status chip, panel tabs, palette, root selector."""
        with ui.header().classes(
            "items-center justify-between bg-primary text-white"
        ) as self.header:
            # Status chip (left)
            with ui.row().classes("items-center gap-2"):
                self.status_chip = StatusChip(
                    on_deep_link=self._on_deep_link,
                    quiet=self.quiet,
                )
                self.status_chip.render()

            ui.separator().props("vertical").classes("mx-2")

            # Panel tabs (center) - 1-5 hotkeys
            with ui.tabs().classes("flex-1") as self._panel_tabs:
                self._tab_map = ui.tab("Map", icon="map").props('keyboard="1"')
                self._tab_repair = ui.tab("Repair", icon="build").props('keyboard="2"')
                self._tab_console = ui.tab("Console", icon="terminal").props(
                    'keyboard="3"'
                )
                self._tab_composer = ui.tab("Composer", icon="tune").props(
                    'keyboard="4"'
                )
                self._tab_record = ui.tab("Record", icon="history").props(
                    'keyboard="5"'
                )

            with ui.tab_panels(
                self._panel_tabs, value=self._get_tab_for_panel(self.current_panel)
            ).classes("w-full"):
                # Panels rendered in main_content, not here
                pass

            ui.separator().props("vertical").classes("mx-2")

            # Right side: pareto selector, mode toggle, command palette
            with ui.row().classes("items-center gap-2"):
                # Pareto selector (only for Map panel)
                if self.current_panel == "map":
                    with ui.row().classes("items-center gap-2"):
                        ui.label("Pareto:").classes("text-sm text-white/90")
                        self.pareto_selector = (
                            ui
                            .select(
                                options=list(self.pareto_presets.keys()),
                                value=self.pareto_state["selected"],
                                on_change=lambda e: self._on_pareto_change(e.value),
                            )
                            .props("dense outlined")
                            .classes("w-48")
                            .style("color: white;")
                        )

                # Root selector (multi-root)
                if len(self.roots) > 1:
                    self.root_selector = (
                        ui
                        .select(
                            options=[str(p) for p in self.roots],
                            value=str(self.root),
                            on_change=lambda e: self.switch_root(Path(str(e.value))),
                        )
                        .props("dense outlined")
                        .classes("w-56")
                        .style("color: white;")
                    )
                    ui.separator().props("vertical").classes("mx-2")

                # Mode toggle
                mode_toggle_select().style("color: white;")

                # Command palette button (⌘K)
                ui.button(icon="search", on_click=self._open_palette).props(
                    'flat round color=white aria-label="Command Palette (⌘K)"'
                ).classes("text-white").tooltip("Command Palette (⌘K)")

    def _get_tab_for_panel(self, panel: str) -> Any:
        """Get the tab element for a panel."""
        tab_map = {
            "map": self._tab_map,
            "repair": self._tab_repair,
            "console": self._tab_console,
            "composer": self._tab_composer,
            "record": self._tab_record,
        }
        return tab_map.get(panel, self._tab_map)

    def _on_deep_link(self, deep_link: str) -> None:
        """Handle cross-panel deep link from status chip."""
        parsed = parse_deep_link(deep_link)
        if parsed:
            panel, lens = parsed
            self._switch_panel(panel)
            if lens and panel in _LENS_PANELS:
                panel_obj = self._get_panel(panel)
                if hasattr(panel_obj, "set_lens"):
                    panel_obj.set_lens(lens)
                self.current_lens = lens
                self._update_url_state()

    def _open_palette(self) -> None:
        """Open command palette."""
        from computronium.ui.command_palette import open_palette

        open_palette(
            current_panel=self.current_panel,
            current_lens=self.current_lens,
            on_select=self._on_palette_select,
        )

    def _on_palette_select(self, action: str) -> None:
        """Handle palette selection (panel:lens or action)."""
        parsed = parse_deep_link(action)
        if parsed:
            panel, lens = parsed
            self._switch_panel(panel)
            if lens and panel in _LENS_PANELS:
                panel_obj = self._get_panel(panel)
                if hasattr(panel_obj, "set_lens"):
                    panel_obj.set_lens(lens)
                self.current_lens = lens
            self._update_url_state()

    def _switch_panel(self, key: str) -> None:
        """Switch to a different panel."""
        if not self._is_panel_visible(key):
            return
        self.current_panel = key
        spec = panel_registry.get(key)
        if spec and spec.default_lens:
            self.current_lens = spec.default_lens
        self._render_current_panel()
        self._update_url_state()

    def _update_status_chip(self, snapshot: DashboardSnapshot | None = None) -> None:
        """Update status chip from current snapshot."""
        if self.status_chip is None:
            return
        if snapshot is None:
            snapshot = self._snapshot_for(with_atlas=False)
        # Get console panel for session delta
        console = self._panel_as("console", Console)
        session_delta = console.data.session_delta if console else None
        chip_data = StatusChipData.from_snapshot(  # type: ignore[attr-defined]
            snapshot, session_delta=session_delta, quiet=self.quiet
        )
        self.status_chip.update_data(chip_data)

    def _update_url_state(self) -> None:
        """Update URL with current panel/lens state."""
        # Store in client-side URL hash for bookmarking
        # Skip in headless tests where no client context exists
        try:
            state = f"#{self.current_panel}"
            if self.current_lens and self.current_panel in _LENS_PANELS:
                state += f":{self.current_lens}"
            ui.run_javascript(f"window.location.hash = '{state}';")
        except (AssertionError, RuntimeError):
            # No client context (headless test) - skip URL update
            pass

    def _restore_url_state(self) -> None:
        """Restore panel/lens from URL hash on load."""
        # This would be called on initial load to parse window.location.hash

    @staticmethod
    def _push_data(panel: Any, data: object, /, **kwargs: object) -> None:
        """Duck-typed data push."""
        update = getattr(panel, "update_data", None)
        if update is not None:
            update(data, **kwargs)

    def _render_current_panel(self) -> None:
        """Render the currently selected panel with its active lens."""
        start = time.perf_counter()
        self.main_content.clear()
        with self.main_content:
            panel = self._get_panel(self.current_panel)

            # Get data for adapter-backed panels
            if self.current_panel in {"map", "repair"}:
                data = self._get_panel_data(self.current_panel)
                if data is not None:
                    self._push_data(panel, data)

            # Set lens for lens-aware panels
            if hasattr(panel, "set_lens") and self.current_lens:
                panel.set_lens(self.current_lens)

            # Special handling for console/composer
            if self.current_panel == "console":
                self._update_console_panel(panel)
            elif self.current_panel == "composer":
                self._update_composer_panel(panel)
            elif self.current_panel == "record":
                self._update_record_panel(panel)

            panel.render()
        metrics.observe_seconds("dashboard_render_panel", time.perf_counter() - start)

    def _update_console_panel(self, panel: Console) -> None:
        """Update console panel with live data."""
        # Build campaign list from roots
        campaigns = []
        for r in self.roots:
            campaigns.append(
                CampaignInfo(
                    root=str(r),
                    name=r.name,
                    state="running" if self.client else "idle",
                    cells=len(self._snapshot_for(with_atlas=False).event_history),
                    burst=None,
                    target=None,
                    uptime_s=time.time() - self._session_start,
                )
            )

        # Get liveness
        from computronium.visualization.live_atlas import liveness

        liveness_data = liveness(self.root, self.client is not None)

        panel.update_data(
            ConsoleData(
                campaigns=campaigns,
                active_campaign=str(self.root),
                liveness={
                    "label": liveness_data.label,
                    "color": liveness_data.color,
                    "detail": liveness_data.detail,
                },
                driver_intent=panel.data.driver_intent,
                session_delta=panel.data.session_delta,
                loss_history=self.loss_history,
                ticker=panel.data.ticker,
                reports=panel.data.reports,
            )
        )

    def _update_composer_panel(self, panel: Composer) -> None:
        """Update composer panel with campaign list."""
        campaigns = {str(r): r.name for r in self.roots}
        panel.set_campaigns(campaigns)

    def _update_record_panel(self, panel: Record) -> None:
        """Update record panel with derived data from snapshot."""
        snapshot = self._snapshot_for(with_atlas=False)

        # Build history from event_history + front_history
        history = []
        for ev in snapshot.event_history:
            history.append(
                type(
                    "HistoryEvent",
                    (),
                    {
                        "timestamp": ev.get("timestamp", 0),
                        "kind": ev.get("kind", ""),
                        "campaign": self.root.name,
                        "message": ev.get("summary", ""),
                        "cell_key": ev.get("cell"),
                        "metrics": {},
                        "severity": ev.get("color", "info"),
                    },
                )()
            )

        # Build ledger from maturation + front_history
        def _to_int(val: Any, default: int = 0) -> int:
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

        ledger = []
        for row in snapshot.maturation:
            count_val = _to_int(row.get("count"))
            ledger.append(
                type(
                    "LedgerEntry",
                    (),
                    {
                        "timestamp": time.time(),
                        "experiment": str(row.get("level", "")),
                        "belief": str(row.get("meaning", "")),
                        "gate": "promoted" if count_val > 0 else "pending",
                        "evidence_refs": [],
                        "calibration": None,
                    },
                )()
            )

        # Build lessons from graveyard + voids
        lessons = []
        for row in snapshot.graveyard:
            lessons.append(
                type(
                    "LessonEntry",
                    (),
                    {
                        "timestamp": time.time(),
                        "cell_key": str(row.get("primitive", "")),
                        "lesson": f"{row.get('axis', '')}={row.get('primitive', '')} diverged {row.get('share', '0%')}",
                        "context": dict(row),
                    },
                )()
            )

        panel.update_data(
            RecordData(
                history=history,
                ledger=ledger,
                lessons=lessons,
                active_lens=cast(
                    "ComponentRecordLens",
                    (
                        ComponentRecordLens(self.current_lens)
                        if self.current_lens in {e.value for e in ComponentRecordLens}
                        else ComponentRecordLens.HISTORY
                    ),
                ),
            )
        )

    def _on_pareto_change(self, value: str) -> None:
        """Handle Pareto objective selector change."""
        self.pareto_state["selected"] = value
        obj_names = self.pareto_presets[value]
        from computronium.autoscientist.objectives import parse_objectives

        self.pareto_state["objectives"] = parse_objectives(",".join(obj_names))
        self._clear_panel_data()
        self._render_current_panel()

    def switch_root(self, root: Path) -> None:
        """Switch the active campaign root."""
        if root == self.root or root not in self.roots:
            return
        self.root = root
        self.log_path = resolve_log_path(root, self._explicit_log_path)
        self.cache = EmbedCache()
        self.objectives = _objectives_from_heartbeat(root)
        self.pareto_state["objectives"] = self.objectives
        self.loss_history.clear()
        self.event_history.clear()
        self.last_signature = watch_signature(root)
        self._config_signature = self._config_signature_of()
        self._last_config_signature = self._config_signature
        self._panels.clear()
        self._clear_panel_data()
        self._render_header()
        self._render_current_panel()

    def _build_main_content(self) -> None:
        """Build main content area."""
        self.main_content = (
            ui.column().classes("w-full p-4 q-ma-auto").style("max-width: 1400px;")
        )

    def _refresh_cheap(self) -> None:
        """Fast paint: everything except UMAP fit."""
        self._clear_panel_data()

        # Update panels that need live data
        for key in ("map", "repair", "console"):
            if key in self._panels:
                data = self._get_panel_data(key)
                if data is not None:
                    self._push_data(self._panels[key], data)

        # Check for artifact changes
        new_sig = watch_signature(self.root)
        if new_sig != self.last_signature:
            self.last_signature = new_sig
            event_bus.publish(ArtifactChanged(signature=new_sig, root=self.root))
            self._render_current_panel()

        # Update status chip
        snapshot = self._snapshot_for(with_atlas=False)
        self._update_status_chip(snapshot)

    async def _load_atlas(self) -> None:
        """Off-thread UMAP refit."""
        from nicegui import run

        try:
            result = await run.io_bound(self._atlas_data_impl, self.root, self.cache)
            if result is None:
                return
            self._apply_atlas_result(result)
        except Exception as e:
            logger.warning("Atlas load failed: %s", e)

    def _atlas_data_impl(
        self, root: Path, cache: EmbedCache
    ) -> tuple[Figure | None, str | None, list[str]]:
        """Sync atlas data loader for run.io_bound."""
        from computronium.visualization.live_atlas import _atlas_data

        return _atlas_data(root, cache)

    def _apply_atlas_result(
        self, result: tuple[Figure | None, str | None, list[str]]
    ) -> None:
        """Push a loaded atlas figure into the Map panel."""
        figure, _, _ = result
        if self.current_panel == "map":
            self._panel_data.pop("map", None)
            panel = self._get_panel("map")
            self._push_data(panel, None, atlas_figure=figure)

    def _config_signature_of(self) -> tuple[tuple[int, int], ...]:
        """(mtime_ns, size) stamps for campaign.yaml + heartbeat.json."""
        stamps: list[tuple[int, int]] = []
        for name in self._CONFIG_WATCHED:
            try:
                stat = (self.root / name).stat()
            except OSError:
                continue
            stamps.append((stat.st_mtime_ns, stat.st_size))
        return tuple(stamps)

    def _reload_objectives(self) -> tuple[ObjectiveSpec, ...] | None:
        """Re-parse objectives from campaign.yaml, else heartbeat."""
        import yaml

        from computronium.autoscientist.objectives import parse_objectives

        path = self.root / "campaign.yaml"
        if path.exists():
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
                raw = (data.get("hpo") or {}).get("objectives")
                if isinstance(raw, list):
                    raw = ",".join(str(item) for item in raw)
                if isinstance(raw, str) and raw:
                    return parse_objectives(raw)
            except (ValueError, OSError, yaml.YAMLError) as error:
                logger.warning("campaign.yaml objectives reload failed: %s", error)
                return None
        return _objectives_from_heartbeat(self.root)

    def _maybe_reload_objectives(self) -> None:
        """Publish ConfigChanged only when objectives actually changed."""
        from computronium.autoscientist.objectives import objective_names

        new = self._reload_objectives()
        if new is None or objective_names(new) == objective_names(
            self.pareto_state["objectives"]
        ):
            return
        event_bus.publish(ConfigChanged(objectives=objective_names(new)))

    def _poll(self) -> None:
        """Poll for artifact + campaign-config changes."""
        new_sig = watch_signature(self.root)
        if new_sig != self.last_signature:
            self.last_signature = new_sig
            event_bus.publish(ArtifactChanged(signature=new_sig, root=self.root))
            self._refresh_cheap()
        config_sig = self._config_signature_of()
        if config_sig != self._last_config_signature:
            self._last_config_signature = config_sig
            self._maybe_reload_objectives()

    def _telemetry_consumer(self) -> Any:
        """Telemetry WebSocket consumer."""
        import json

        import websockets

        if not self.daemon_url:
            return
        daemon_url = self.daemon_url

        async def _consume() -> None:
            ws_url = f"{daemon_url.replace('http://', 'ws://')}/ws/telemetry"
            try:
                async with websockets.connect(ws_url) as ws:
                    async for message in ws:
                        self._record_telemetry(json.loads(message))
            except OSError:
                pass

        return _consume()

    def _record_telemetry(self, record: dict[str, Any]) -> None:
        """Append one telemetry record to the loss history + bus."""
        loss = record.get("train_loss", record.get("loss"))
        if not isinstance(loss, int | float):
            return
        self.loss_history.append(float(loss))
        if len(self.loss_history) > 60:
            self.loss_history.pop(0)
        event_bus.publish(WebSocketEvent(topic="telemetry", payload=record))

    def _events_consumer(self) -> Any:
        """Events WebSocket consumer."""
        import json

        import websockets

        if not self.daemon_url:
            return
        daemon_url = self.daemon_url

        async def _consume() -> None:
            ws_url = f"{daemon_url.replace('http://', 'ws://')}/ws/events"
            try:
                async with websockets.connect(ws_url) as ws:
                    async for message in ws:
                        raw = json.loads(message)
                        event_bus.publish(WebSocketEvent(topic="events", payload=raw))
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
        # AA-compliant colors
        ui.colors(primary=PRIMARY, secondary=SECONDARY)
        # Inject design tokens and a11y CSS
        ui.add_head_html(f"<style>{css_custom_properties()}</style>")
        ui.add_head_html(f"<style>{a11y_css()}</style>")
        # Custom badge colors for WCAG AA contrast (Quasar built-ins fail)
        ui.add_head_html("""
        <style>
        .bg-warning-custom { background-color: var(--color-warning) !important; }
        .text-warning-custom { color: var(--color-warning) !important; }
        </style>
        """)

        # Page title
        ui.page_title("Computronium — Live Broad Map")

        # Build header
        self._render_header()

        # Main content area
        self._build_main_content()

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
    ui_actions: bool = False,
    quiet: bool = False,
    roots: tuple[Path, ...] | None = None,
) -> None:
    """Build the Computronium dashboard (five-panel architecture)."""
    app = DashboardApp(
        root=root,
        log_path=log_path,
        poll_seconds=poll_seconds,
        daemon_url=daemon_url,
        ui_mode=ui_mode,
        ui_actions=ui_actions,
        quiet=quiet,
        roots=roots,
    )
    app.build()
