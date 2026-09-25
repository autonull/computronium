"""Computronium Dashboard — extensible single-page architecture.

Views: Monitor (live status) / Atlas (discovery map) / Defects (triage) /
Evolution (probes, genome) / Evidence (beliefs, claims). One snapshot per
refresh cycle; artifact polling plus optional daemon WebSocket streams.
Read-only over the campaign root — actions route through the daemon API.

All panels are registered in the ViewRegistry and available via:
- Top-level navigation (5 core views)
- Command Palette (Cmd+K)
- Contextual tabs within views
- Modals/drawers
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from collections.abc import Callable
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from nicegui import app as gui_app
from nicegui import ui

from computronium.autoscientist.stream_protocol import (
    STREAM_PROTOCOL_VERSION,
    STREAM_TOPIC,
    parse_envelope,
)
from computronium.ui.a11y.tokens import a11y_css
from computronium.ui.adapters import get_adapter
from computronium.ui.components import (
    BudgetPanel,
    CampaignCardGallery,
    Composer,
    ComposerData,
    ConstitutionHealthPanel,
    DiscoveryMap,
    EpisodeTimeline,
    EvidencePanel,
    FieldReports,
    GenomeHealthTracker,
    LineageViewer,
    MonitorView,
    MutationExplorer,
    ObjectiveExplorerPanel,
    ProbeAnalytics,
    ProgressPanel,
    RegionNaming,
    RepairBench,
    ScrubberPanel,
    StagnationDashboard,
    TeamWall,
    TradeoffsPanel,
    VetoLog,
)
from computronium.ui.components.activity_feed import ActivityFeed, FeedEvent
from computronium.ui.components.field_reports import FieldReport
from computronium.ui.components.monitor import DriverIntent, SessionDelta
from computronium.ui.design_tokens import PRIMARY, SECONDARY, css_custom_properties
from computronium.ui.event_bus import (
    ArtifactChanged,
    ConfigChanged,
    PanelRenderFailed,
    WebSocketEvent,
    event_bus,
)
from computronium.ui.metrics import metrics
from computronium.ui.navigation import format_hash, parse_hash
from computronium.ui.panels import BasePanel
from computronium.ui.view_registry import (
    PanelPlacement,
    PanelSpec,
    ViewSpec,
    registry,
)
from computronium.visualization.live_atlas import (
    POLL_SECONDS,
    DaemonClient,
    DashboardSnapshot,
    EmbedCache,
    _classify_event,
    _objectives_from_heartbeat,
    _toast_for_alert,
    liveness,
    render_snapshot,
    resolve_log_path,
    watch_signature,
)

if TYPE_CHECKING:
    from plotly.graph_objects import Figure

    from computronium.autoscientist.objectives import ObjectiveSpec
    from computronium.visualization.live_atlas import DashboardEvent

logger = logging.getLogger("computronium.ui.dashboard")

_FEED_LIMIT = 200
_LOSS_LIMIT = 240


def _feed_events(history: list[DashboardEvent]) -> list[FeedEvent]:
    """Project classified events into feed-renderable events."""
    return [
        FeedEvent(
            timestamp=ev.timestamp,
            icon=ev.icon,
            color=ev.color,
            summary=ev.summary,
            raw=str(ev.payload),
        )
        for ev in history
    ]


# ═══════════════════════════════════════════════════════════════════════════
# VIEW & PANEL REGISTRATION
# ═══════════════════════════════════════════════════════════════════════════


def _make_composer() -> Composer:
    return Composer()


def _make_constitution() -> ConstitutionHealthPanel:
    return ConstitutionHealthPanel()


def _make_lineage() -> LineageViewer:
    return LineageViewer()


def _make_episodes() -> EpisodeTimeline:
    return EpisodeTimeline()


def _make_campaign_gallery() -> Any:
    raise RuntimeError("campaigns tab is root-bound; built per-app in _render_tabs")


def _make_preview_shelf() -> Any:
    from computronium.ui.components.preview_shelf import PreviewShelf

    return PreviewShelf()


def _make_region_naming() -> RegionNaming:
    return RegionNaming()


def _make_team_wall() -> TeamWall:
    return TeamWall()


def _make_probe_analytics() -> ProbeAnalytics:
    return ProbeAnalytics()


def _make_stagnation() -> StagnationDashboard:
    return StagnationDashboard()


def _make_genome_health() -> GenomeHealthTracker:
    return GenomeHealthTracker()


def _make_mutations() -> MutationExplorer:
    return MutationExplorer()


def _make_veto_log() -> VetoLog:
    return VetoLog()


def _make_progress() -> ProgressPanel:
    return ProgressPanel()


def _make_workshop() -> Any:
    from computronium.ui.components.workshop import WorkshopPanel

    return WorkshopPanel()


def _make_field_reports() -> FieldReports:
    return FieldReports()


def _make_budget() -> BudgetPanel:
    return BudgetPanel()


def _make_objective_explorer() -> ObjectiveExplorerPanel:
    return ObjectiveExplorerPanel()


# Register core views with their tabs
# Monitor tabs
class _ActivityFeedPanel(ActivityFeed, BasePanel):
    def __init__(self):
        BasePanel.__init__(
            self,
            panel_key="activity_feed",
            plain="Live stream of what the system is doing right now",
            why="Shows proposals, defects, alerts, and completions in real time",
            expert="Event bus subscription renders classified DashboardEvents as FeedEvents",
        )
        ActivityFeed.__init__(self)

    def render(self):
        return ActivityFeed.render(self)

    def update_data(self, data: Any = None, **kwargs):
        if data:
            ActivityFeed.update_data(self, data.events)


class _TradeoffsPanel(TradeoffsPanel, BasePanel):
    def __init__(self):
        BasePanel.__init__(
            self,
            panel_key="tradeoffs",
            plain="See the best trade-offs between accuracy and cost",
            why="Pareto front shows which configurations you can't improve without making something worse",
            expert="ParetoCell metrics dict with objective names as keys; sorted by first objective",
        )
        TradeoffsPanel.__init__(self)

    def render(self):
        return TradeoffsPanel.render(self)

    def update_data(self, data: Any = None, **kwargs):
        if data:
            TradeoffsPanel.update_data(
                self,
                cells=list(data.pareto_cells),
                objectives=list(data.objectives[:2]) if data.objectives else None,
            )


class _CampaignGalleryPanel(BasePanel):
    """Root-bound campaigns tab (the registry factory is root-free)."""

    def __init__(self, manifests_dir: Path):
        BasePanel.__init__(
            self,
            panel_key="campaigns",
            plain="Past campaigns and their results",
            why="Compare what was tried before starting something new",
            expert="CampaignCardGallery over <root>/campaigns manifests",
        )
        self._gallery = CampaignCardGallery(manifests_dir)

    def render(self):
        return self._gallery.render()

    def update_data(self, data: Any = None, **kwargs):
        pass


class _EvidencePanel(EvidencePanel):
    """Evidence view factory (CEEC adapters live in `ui/adapters.py`)."""

    def __init__(self):
        EvidencePanel.__init__(self)


def _make_scrubber() -> ScrubberPanel:
    return ScrubberPanel()


# Monitor tabs
registry.register_view(
    ViewSpec(
        key="monitor",
        label="Monitor",
        icon="dashboard",
        factory=MonitorView,
        order=0,
        hotkey="1",
        tabs=[
            PanelSpec(
                key="activity_feed",
                label="Activity",
                icon="rss_feed",
                factory=_ActivityFeedPanel,
                placement=PanelPlacement.TAB,
                parent_view="monitor",
                order=0,
            ),
            PanelSpec(
                key="field_reports",
                label="Field reports",
                icon="report",
                factory=_make_field_reports,
                placement=PanelPlacement.TAB,
                parent_view="monitor",
                order=1,
            ),
            PanelSpec(
                key="budget",
                label="Budget",
                icon="savings",
                factory=_make_budget,
                adapter_key="budget",
                placement=PanelPlacement.TAB,
                parent_view="monitor",
                order=2,
            ),
            PanelSpec(
                key="scrubber",
                label="Scrubber",
                icon="history",
                factory=_make_scrubber,
                adapter_key="scrubber",
                placement=PanelPlacement.TAB,
                parent_view="monitor",
                order=3,
            ),
        ],
    )
)

# Atlas tabs
registry.register_view(
    ViewSpec(
        key="atlas",
        label="Atlas",
        icon="map",
        factory=DiscoveryMap,
        adapter_key="discovery_map",
        order=1,
        hotkey="2",
        tabs=[
            PanelSpec(
                key="tradeoffs",
                label="Trade-offs",
                icon="trending_up",
                factory=_TradeoffsPanel,
                adapter_key="tradeoffs",
                placement=PanelPlacement.TAB,
                parent_view="atlas",
                order=0,
            ),
            PanelSpec(
                key="campaigns",
                label="Campaigns",
                icon="folder",
                factory=_make_campaign_gallery,
                adapter_key="campaigns",
                placement=PanelPlacement.TAB,
                parent_view="atlas",
                order=1,
            ),
            PanelSpec(
                key="preview",
                label="Preview",
                icon="preview",
                factory=_make_preview_shelf,
                adapter_key="preview",
                placement=PanelPlacement.TAB,
                parent_view="atlas",
                order=2,
            ),
            PanelSpec(
                key="region_naming",
                label="Regions",
                icon="label",
                factory=_make_region_naming,
                adapter_key="region_naming",
                placement=PanelPlacement.TAB,
                parent_view="atlas",
                order=3,
            ),
            PanelSpec(
                key="team",
                label="Team",
                icon="groups",
                factory=_make_team_wall,
                adapter_key="team",
                placement=PanelPlacement.TAB,
                parent_view="atlas",
                order=4,
            ),
            PanelSpec(
                key="objective_explorer",
                label="Objectives",
                icon="parallel_coords",
                factory=_make_objective_explorer,
                adapter_key="objective_explorer",
                placement=PanelPlacement.TAB,
                parent_view="atlas",
                order=5,
            ),
        ],
    )
)

# Defects tabs
registry.register_view(
    ViewSpec(
        key="defects",
        label="Defects",
        icon="build",
        factory=RepairBench,
        adapter_key="repair_bench",
        order=2,
        hotkey="3",
        tabs=[
            PanelSpec(
                key="constitution",
                label="Constitution",
                icon="shield",
                factory=_make_constitution,
                adapter_key="constitution",
                placement=PanelPlacement.TAB,
                parent_view="defects",
                order=0,
            ),
            PanelSpec(
                key="lineage",
                label="Lineage",
                icon="account_tree",
                factory=_make_lineage,
                adapter_key="lineage",
                placement=PanelPlacement.TAB,
                parent_view="defects",
                order=1,
            ),
            PanelSpec(
                key="episodes",
                label="Episodes",
                icon="timeline",
                factory=_make_episodes,
                adapter_key="episodes",
                placement=PanelPlacement.TAB,
                parent_view="defects",
                order=2,
            ),
        ],
    )
)

# Evolution tabs
registry.register_view(
    ViewSpec(
        key="evolution",
        label="Evolution",
        icon="tune",
        factory=_make_composer,
        order=3,
        hotkey="4",
        tabs=[
            PanelSpec(
                key="probe_analytics",
                label="Probes",
                icon="analytics",
                factory=_make_probe_analytics,
                adapter_key="probe_analytics",
                placement=PanelPlacement.TAB,
                parent_view="evolution",
                order=0,
            ),
            PanelSpec(
                key="stagnation",
                label="Stagnation",
                icon="warning",
                factory=_make_stagnation,
                adapter_key="stagnation",
                placement=PanelPlacement.TAB,
                parent_view="evolution",
                order=1,
            ),
            PanelSpec(
                key="genome_health",
                label="Genome",
                icon="dna",
                factory=_make_genome_health,
                adapter_key="genome_health",
                placement=PanelPlacement.TAB,
                parent_view="evolution",
                order=2,
            ),
            PanelSpec(
                key="mutations",
                label="Mutations",
                icon="biotech",
                factory=_make_mutations,
                adapter_key="mutations",
                placement=PanelPlacement.TAB,
                parent_view="evolution",
                order=3,
            ),
            PanelSpec(
                key="veto_log",
                label="Veto log",
                icon="gavel",
                factory=_make_veto_log,
                adapter_key="veto_log",
                placement=PanelPlacement.TAB,
                parent_view="evolution",
                order=4,
            ),
        ],
    )
)

# Evidence (CEEC beliefs, experiments, decisions — read-only)
registry.register_view(
    ViewSpec(
        key="evidence",
        label="Evidence",
        icon="verified",
        factory=_EvidencePanel,
        adapter_key="evidence",
        order=4,
        hotkey="5",
    )
)

# Progress modal (always available via palette hotkey `b`)
registry.register_panel(
    PanelSpec(
        key="progress",
        label="Progress",
        icon="emoji_events",
        factory=_make_progress,
        adapter_key=None,  # Uses recognition store
        placement=PanelPlacement.MODAL,
        order=0,
        hotkey="b",
    )
)

# Workshop modal (always available via palette hotkey `w`)
registry.register_panel(
    PanelSpec(
        key="workshop",
        label="Workshop",
        icon="build",
        factory=_make_workshop,
        adapter_key=None,
        placement=PanelPlacement.MODAL,
        order=0,
        hotkey="w",
    )
)


def _make_forensics() -> Any:
    from computronium.ui.components.cell_forensics import CellForensicsPanel

    return CellForensicsPanel()


# Cell forensics drawer (Atlas table row → selected_cell_key signal → drawer)
registry.register_panel(
    PanelSpec(
        key="cell_forensics",
        label="Cell forensics",
        icon="biotech",
        factory=_make_forensics,
        adapter_key=None,
        placement=PanelPlacement.DRAWER,
        order=0,
    )
)


# ═══════════════════════════════════════════════════════════════════════════
# DASHBOARD APP
# ═══════════════════════════════════════════════════════════════════════════


class DashboardApp:
    """Live dashboard: header nav + one visible view + poll/WS refresh."""

    _CONFIG_WATCHED = ("campaign.yaml", "heartbeat.json")
    _WS_PAINT_INTERVAL_S = 2.0

    _DENSITY_STORAGE_KEY = "computronium_ui_density"

    def __init__(
        self,
        root: Path,
        log_path: Path | None,
        poll_seconds: float,
        daemon_url: str | None,
        density: Literal["comfortable", "compact"] = "comfortable",
        *,
        roots: tuple[Path, ...] | None = None,
    ):
        self.roots: tuple[Path, ...] = roots or (root,)
        self.root = root
        self._explicit_log_path = log_path
        self.log_path = resolve_log_path(root, log_path)
        self.poll_seconds = poll_seconds
        self.daemon_url = daemon_url
        self.density: Literal["comfortable", "compact"] = (
            density if density in {"comfortable", "compact"} else "comfortable"
        )
        with suppress(RuntimeError):
            stored = gui_app.storage.user.get(self._DENSITY_STORAGE_KEY)
            if stored in {"comfortable", "compact"}:
                self.density = stored
        self.quiet = self.density == "compact"

        # State
        self.view = "monitor"
        self.cache = EmbedCache()
        self.client = DaemonClient(daemon_url) if daemon_url else None
        self.objectives = _objectives_from_heartbeat(root)
        self.last_signature = watch_signature(root)

        # Stream state
        self.loss_history: list[float] = []
        self.event_history: list[Any] = []
        self.reports: list[FieldReport] = []
        self.session_delta = SessionDelta()
        self.intent: DriverIntent | None = None
        self._last_ws_paint = 0.0

        # One render_snapshot per refresh cycle
        self._snapshot: DashboardSnapshot | None = None
        self._snapshot_has_atlas = False
        self.atlas_figure: Figure | None = None

        # Campaign config signature for hot-reload
        self._config_signature = self._config_signature_of()
        self._last_config_signature = self._config_signature

        # Views (lazy instances) + containers + tabs
        self._views: dict[str, BasePanel] = {}
        self._view_containers: dict[str, Any] = {}
        self._tab_containers: dict[
            str, dict[str, Any]
        ] = {}  # view_key -> {tab_key: container}
        self._active_tab: dict[str, str] = {}  # view_key -> active tab_key
        self._rendered: set[str] = set()
        self._tab_panels: dict[str, BasePanel] = {}  # spec.key -> cached instance
        self._tab_membership: dict[str, tuple[str, ...]] = {}
        self._tab_buttons: dict[str, dict[str, Any]] = {}

        # UI elements
        self.header: Any = None
        self._nav: Any = None
        self._liveness_badge: Any = None
        self._root_selector: Any = None

        # Extensions
        self._command_palette: Any = None

        # Session tracking
        self._session_start = time.time()

        # Bus subscriptions
        self._unsub_artifact = event_bus.subscribe(
            ArtifactChanged, self._on_artifact_changed
        )
        self._unsub_ws = event_bus.subscribe(WebSocketEvent, self._on_ws_event)
        self._unsub_config = event_bus.subscribe(ConfigChanged, self._on_config_changed)

        # Interaction-state subscription: Atlas selection → forensics drawer
        from computronium.ui.state import selected_cell_key

        self._forensics: Any = None
        self._unsub_select = selected_cell_key.subscribe(self._on_cell_selected)

    def _on_cell_selected(self, cell_key: str | None) -> None:
        """Open the forensics drawer for the selected Atlas cell (§4.1)."""
        if not cell_key:
            return
        from computronium.ui.adapters import adapt_cell_forensics

        snapshot = self._snapshot_for(with_atlas=False)
        data = adapt_cell_forensics(snapshot, self.root, cell_key)
        if self._forensics is None:
            spec = registry.get_panel("cell_forensics")
            if spec is None:
                return
            self._forensics = spec.factory()
        self._forensics.daemon_client = self.client
        self._forensics.show(data)

    # ── Bus handlers ──────────────────────────────────────────────────────────

    def _on_artifact_changed(self, event: ArtifactChanged) -> None:
        if event.root != self.root:
            return
        self.last_signature = event.signature
        self._refresh_current()

    def _on_config_changed(self, event: ConfigChanged) -> None:
        from computronium.autoscientist.objectives import parse_objectives

        try:
            objectives = parse_objectives(",".join(event.objectives))
        except ValueError:
            logger.warning("Ignoring unparsable ConfigChanged: %s", event.objectives)
            return
        if objectives == self.objectives:
            return
        self.objectives = objectives
        self._invalidate()
        self._refresh_current()

    # ── WebSocket streams ─────────────────────────────────────────────────────

    def _on_ws_event(self, event: WebSocketEvent) -> None:
        if event.topic != STREAM_TOPIC:
            logger.debug("Unhandled WS topic: %s", event.topic)
            return
        envelope = parse_envelope(event.payload)
        if envelope is None:
            logger.debug("Dropping malformed stream envelope")
            return
        metrics.inc(
            "dashboard_ws_events_total",
            labels={"topic": STREAM_TOPIC, "kind": envelope.kind},
        )
        match envelope.kind:
            case "events":
                self._route_ws_events(dict(envelope.payload), time.time())
            case "telemetry":
                self._route_ws_telemetry(dict(envelope.payload))

    def _route_ws_events(self, raw: dict[str, Any], now: float) -> None:
        ev = _classify_event(raw, now)
        _toast_for_alert(ev)
        self.event_history.append(ev)
        if len(self.event_history) > _FEED_LIMIT:
            self.event_history.pop(0)

        if ev.kind == "alert":
            self.reports.append(
                FieldReport(
                    icon=ev.icon,
                    color=ev.color,
                    sentence=ev.summary,
                    deep_link=None,
                    unread=True,
                )
            )
        if ev.kind == "proposal_batch":
            n = raw.get("n_proposals", raw.get("count", 0))
            primitives = [raw[axis] for axis in ("dynamics", "credit") if axis in raw]
            self.intent = DriverIntent(
                proposing=int(n) if isinstance(n, int | float) else 0,
                last_batch_ago_s=0.0,
                strategy_hint="·".join(primitives) if primitives else "exploring",
            )
        if ev.kind == "defect_quarantined":
            self.session_delta = SessionDelta(
                cells=self.session_delta.cells,
                records=self.session_delta.records,
                crashes=self.session_delta.crashes + 1,
            )

        self._refresh_liveness()
        self._throttled_monitor_paint()

    def _route_ws_telemetry(self, payload: dict[str, Any]) -> None:
        now = time.time()
        if now - self._last_ws_paint < self._WS_PAINT_INTERVAL_S:
            return
        self._last_ws_paint = now
        loss = payload.get("train_loss", payload.get("loss"))
        if isinstance(loss, int | float):
            self.loss_history.append(float(loss))
            if len(self.loss_history) > _LOSS_LIMIT:
                self.loss_history.pop(0)
            self._throttled_monitor_paint(force=True)

    def _throttled_monitor_paint(self, *, force: bool = False) -> None:
        if self.view != "monitor" or "monitor" not in self._rendered:
            return
        now = time.time()
        if not force and now - self._last_ws_paint < self._WS_PAINT_INTERVAL_S:
            return
        if force:
            self._last_ws_paint = now
        self._render_view("monitor")

    def _start_streams(self) -> None:
        if not self.client:
            return
        asyncio.create_task(self._ws_loop())

    async def _ws_loop(self) -> None:
        assert self.daemon_url is not None
        ws_url = (
            f"{self.daemon_url.replace('http://', 'ws://')}"
            f"/ws/stream?v={STREAM_PROTOCOL_VERSION}"
        )
        while True:
            try:
                await self._consume_stream(ws_url)
            except asyncio.CancelledError:
                return
            except OSError, ValueError:
                await asyncio.sleep(self.poll_seconds)

    async def _consume_stream(self, ws_url: str) -> None:
        import websockets

        async with websockets.connect(ws_url) as ws:
            async for message in ws:
                self._handle_stream_message(message)

    def _handle_stream_message(self, message: str | bytes) -> None:
        try:
            raw = json.loads(message)
        except ValueError:
            logger.debug("Dropping undecodable stream message")
            return
        envelope = parse_envelope(raw)
        if envelope is None:
            logger.debug("Dropping malformed stream envelope")
            return
        event_bus.publish(
            WebSocketEvent(topic=STREAM_TOPIC, payload=envelope.model_dump())
        )

    # ── Snapshot + data ───────────────────────────────────────────────────────

    def _snapshot_for(self, *, with_atlas: bool) -> DashboardSnapshot:
        if self._snapshot is None or (with_atlas and not self._snapshot_has_atlas):
            start = time.perf_counter()
            self._snapshot = render_snapshot(
                self.root,
                self.log_path,
                self.cache,
                objectives=self.objectives,
                with_atlas=with_atlas,
                event_history=list(self.event_history),
            )
            metrics.observe_seconds("dashboard_snapshot", time.perf_counter() - start)
            self._snapshot_has_atlas = with_atlas
        return self._snapshot

    def _invalidate(self) -> None:
        self._snapshot = None
        self._snapshot_has_atlas = False
        for key in ("atlas", "defects", "evolution", "evidence"):
            self._views.pop(key, None)
            self._rendered.discard(key)

    def _refresh_current(self) -> None:
        self._invalidate()
        self._refresh_liveness()
        self._render_view(self.view)
        # Also refresh visible tabs
        for view_key in self._tab_containers:
            active = self._active_tab.get(view_key)
            if active:
                self._render_tabs(view_key)

    def _refresh_liveness(self) -> None:
        if self._liveness_badge is None:
            return
        liv = liveness(self.root, self.client is not None)
        self._liveness_badge.set_text(liv.label)
        self._liveness_badge.props(f"color={liv.color or 'grey'}")

    # ── View & Tab rendering ──────────────────────────────────────────────────

    def _ensure_view(self, key: str) -> BasePanel:
        spec = registry.get_view(key)
        if spec is None:
            raise ValueError(f"Unknown view: {key}")
        if key not in self._views:
            panel = spec.factory()
            if isinstance(panel, MonitorView):
                panel.quiet = self.quiet
            self._views[key] = panel
        return self._views[key]

    def _push_view_data(self, key: str, panel: BasePanel) -> None:
        spec = registry.get_view(key)
        if spec is None:
            return

        if key == "monitor":
            from computronium.ui.adapters import adapt_health_panel
            from computronium.ui.components.monitor import MonitorData

            snapshot = self._snapshot_for(with_atlas=False)
            panel.update_data(
                MonitorData(
                    liveness=liveness(self.root, self.client is not None),
                    tiles=adapt_health_panel(snapshot, self.root),
                    loss_history=self.loss_history,
                    feed=_feed_events(self.event_history),
                    intent=self.intent,
                    session_delta=self.session_delta,
                    ticker=snapshot.ticker if not self.quiet else None,
                    layout_note=snapshot.layout_note,
                )
            )
            return

        if isinstance(panel, Composer):
            panel.update_data(
                ComposerData(campaigns={str(r): r.name for r in self.roots})
            )
            return

        adapter = get_adapter(spec.adapter_key) if spec.adapter_key else None
        if adapter is None:
            return
        snapshot = self._snapshot_for(with_atlas=False)
        from computronium.ui.data_adapters import AdapterContext

        ctx = AdapterContext(root=self.root, snapshot=snapshot)
        start = time.perf_counter()
        data = adapter.adapt(ctx)
        metrics.observe_seconds("dashboard_adapter", time.perf_counter() - start)
        panel.update_data(data)
        if key == "atlas" and isinstance(panel, DiscoveryMap):
            panel.atlas_figure = self.atlas_figure

    def _render_panel_safe(
        self, container: Any, panel_key: str, render: Callable[[], object]
    ) -> None:
        """Render a panel with a server-side error-card fallback (§4.9).

        One failed panel publishes ``PanelRenderFailed``, bumps a metrics
        counter, and renders a retry card — it never kills the page.
        """
        try:
            with container:
                render()
        except Exception as error:
            logger.exception("Panel %s render failed", panel_key)
            metrics.inc(
                "dashboard_panel_render_failed_total", labels={"panel": panel_key}
            )
            event_bus.publish(PanelRenderFailed(panel_key=panel_key, error=str(error)))
            try:
                container.clear()
            except AssertionError, RuntimeError:
                return
            with container, ui.card().classes("w-full p-4"):
                ui.label(f"Panel unavailable: {panel_key}").classes("text-h6")
                ui.label(str(error)).classes("text-body")
                ui.button("Retry", on_click=self.force_refresh).props("flat dense")

    def _render_view(self, key: str) -> None:
        container = self._view_containers.get(key)
        if container is None:
            logger.warning("No container for view: %s", key)
            return
        container.clear()
        panel = self._ensure_view(key)
        first = key not in self._rendered
        self._render_panel_safe(
            container,
            key,
            lambda: (
                self._push_view_data(key, panel),
                panel.on_data_update(),
                panel.render(),
            ),
        )
        self._rendered.add(key)
        if first:
            panel.on_mount()

        # Render tabs for this view (outside the cleared container to avoid deletion issues)
        self._render_tabs(key)

    def _render_tabs(self, view_key: str) -> None:
        """Render tab bar and tab containers for a view.

        The tab bar rebuilds only when tab membership changes; tab panel
        instances are cached by spec key so refresh reuses them instead of
        calling ``spec.factory()`` on every paint.
        """
        tabs_specs = registry.get_panels_for_view(view_key)
        if not tabs_specs:
            return

        tab_container = self._tab_containers.get(view_key, {})
        active_tab = self._active_tab.get(view_key, tabs_specs[0].key)
        membership = tuple(spec.key for spec in tabs_specs)

        # Tab bar: rebuild only on membership change, else restyle in place
        if hasattr(self, "_tab_area") and self._tab_area:
            if self._tab_membership.get(view_key) != membership:
                self._tab_membership[view_key] = membership
                with self._tab_area:
                    # Clear existing tab bar
                    for child in list(self._tab_area.default_slot.children):
                        child.delete()

                    with ui.row().classes("w-full"):
                        buttons: dict[str, Any] = {}
                        for spec in tabs_specs:
                            btn = (
                                ui
                                .button(
                                    spec.icon + " " + spec.label,
                                    on_click=lambda s=spec: self._switch_tab(
                                        view_key, s.key
                                    ),
                                )
                                .props("flat dense no-caps")
                                .classes("text-grey hover:text-primary")
                            )
                            buttons[spec.key] = btn
                        self._tab_buttons[view_key] = buttons
            self._style_tab_buttons(view_key, active_tab)

        self._render_tab_contents(view_key, tabs_specs, tab_container, active_tab)

    def _render_tab_contents(
        self,
        view_key: str,
        tabs_specs: list[PanelSpec],
        tab_container: dict[str, Any],
        active_tab: str,
    ) -> None:
        """Render tab content containers, reusing cached panel instances."""
        for spec in tabs_specs:
            container = tab_container.get(spec.key)
            if container is None:
                continue
            try:
                container.clear()
            except AssertionError, RuntimeError:
                # Element was deleted, recreate
                self._tab_containers[view_key][spec.key] = ui.column().classes(
                    "w-full gap-4"
                )
                container = self._tab_containers[view_key][spec.key]

            if spec.key == active_tab:
                container.classes(remove="hidden")
                panel = self._tab_panels.get(spec.key)
                if panel is None:
                    if spec.key == "campaigns":
                        panel = _CampaignGalleryPanel(self.root / "campaigns")
                    else:
                        panel = spec.factory()
                    self._tab_panels[spec.key] = panel
                    panel.on_mount()
                self._render_panel_safe(
                    container,
                    spec.key,
                    lambda p=panel, s=spec: (
                        self._push_tab_data(s, p),
                        p.on_data_update(),
                        p.render(),
                    ),
                )
            else:
                container.classes(add="hidden")

    def _style_tab_buttons(self, view_key: str, active_tab: str) -> None:
        """Highlight the active tab button without rebuilding the bar."""
        for tab_key, btn in self._tab_buttons.get(view_key, {}).items():
            if tab_key == active_tab:
                btn.classes(
                    remove="text-grey hover:text-primary",
                    add="text-primary font-medium",
                )
            else:
                btn.classes(
                    remove="text-primary font-medium",
                    add="text-grey hover:text-primary",
                )

    def _push_tab_data(self, spec: Any, panel: BasePanel) -> None:
        """Push data to a tab panel."""
        adapter = get_adapter(spec.adapter_key) if spec.adapter_key else None
        if adapter is None:
            return
        snapshot = self._snapshot_for(with_atlas=False)
        from computronium.ui.data_adapters import AdapterContext

        ctx = AdapterContext(root=self.root, snapshot=snapshot)
        start = time.perf_counter()
        data = adapter.adapt(ctx)
        metrics.observe_seconds("dashboard_adapter", time.perf_counter() - start)
        panel.update_data(data)

    def _switch_tab(self, view_key: str, tab_key: str) -> None:
        prev = self._active_tab.get(view_key)
        self._active_tab[view_key] = tab_key
        self._render_tabs(view_key)
        if prev and prev in self._tab_panels:
            self._tab_panels[prev].on_visibility_change(False)
        if tab_key in self._tab_panels:
            self._tab_panels[tab_key].on_visibility_change(True)
        if view_key == self.view:
            self._update_hash(view_key, tab_key)

    def _render_current_panel(self) -> None:
        self._render_view(self.view)

    def switch_view(self, key: str) -> None:
        views = registry.get_visible_views()
        view_keys = [v.key for v in views]
        if key not in view_keys or key == self.view:
            return
        prev = self.view
        self.view = key
        for view_key, container in self._view_containers.items():
            if view_key == key:
                container.classes(remove="hidden")
            else:
                container.classes(add="hidden")
        if key not in self._rendered:
            self._render_view(key)
        else:
            # Re-render tabs for the newly visible view
            self._render_tabs(key)
        if prev in self._views:
            self._views[prev].on_visibility_change(False)
        if key in self._views:
            self._views[key].on_visibility_change(True)

        # Show/hide tab area
        if hasattr(self, "_tab_area") and self._tab_area:
            tabs = registry.get_panels_for_view(key)
            if tabs:
                self._tab_area.classes(remove="hidden")
            else:
                self._tab_area.classes(add="hidden")

        # Initialize active tab
        tabs = registry.get_panels_for_view(key)
        if tabs:
            self._active_tab[key] = tabs[0].key
        self._update_hash(key)

    def set_density(self, density: str) -> None:
        """Density toggle (comfortable/compact); compact quiets the feed."""
        if density not in {"comfortable", "compact"} or density == self.density:
            return
        self.density = density  # type: ignore[assignment]
        self.quiet = density == "compact"
        if "monitor" in self._views:
            monitor = self._views["monitor"]
            if hasattr(monitor, "quiet"):
                monitor.quiet = self.quiet
        with suppress(RuntimeError):
            gui_app.storage.user[self._DENSITY_STORAGE_KEY] = density
        self._refresh_current()

    def toggle_density(self) -> None:
        self.set_density("compact" if self.density == "comfortable" else "comfortable")

    def force_refresh(self) -> None:
        self._refresh_current()

    # ── Chrome ────────────────────────────────────────────────────────────────

    def _render_header(self) -> None:
        with ui.header().classes(
            "items-center justify-between bg-primary text-white"
        ) as self.header:
            with ui.row().classes("items-center gap-3"):
                ui.label("Computronium").classes("text-h6 font-bold")
                self._liveness_badge = (
                    ui.badge("● …", color="grey").classes("text-sm").props("outline")
                )
                self._refresh_liveness()

            # Navigation toggle
            views = registry.get_visible_views()
            self._nav = (
                ui
                .toggle(
                    {v.key: v.label for v in views},
                    value=self.view,
                    on_change=lambda e: self.switch_view(str(e.value)),
                )
                .props("dense no-caps flat")
                .classes("text-white")
            )

            with ui.row().classes("items-center gap-2"):
                if len(self.roots) > 1:
                    self._root_selector = (
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
                (
                    ui
                    .select(
                        options={
                            "comfortable": "Comfortable",
                            "compact": "Compact",
                        },
                        value=self.density,
                        on_change=lambda e: self.set_density(str(e.value)),
                    )
                    .props("dense outlined")
                    .classes("w-40")
                    .style("color: white;")
                    .tooltip("Density")
                )
                # Command palette trigger
                ui.button(icon="search", on_click=self._open_command_palette).props(
                    "flat dense round"
                ).classes("text-white").tooltip("Command Palette (⌘K)")

    def _render_body(self) -> None:
        with ui.column().classes("w-full max-w-[1400px] mx-auto p-4") as body:
            # View containers
            views = registry.get_visible_views()
            for spec in views:
                self._view_containers[spec.key] = ui.column().classes("w-full gap-4")
                if spec.key != self.view:
                    self._view_containers[spec.key].classes(add="hidden")

            # Tab containers (separate from view containers to avoid deletion issues)
            self._tab_area = ui.column().classes("w-full gap-4")
            for spec in views:
                self._tab_containers[spec.key] = {}
                for tab_spec in registry.get_panels_for_view(spec.key):
                    self._tab_containers[spec.key][tab_spec.key] = ui.column().classes(
                        "w-full gap-4 hidden"
                    )

    def _bind_hotkeys(self) -> None:
        views = registry.get_visible_views()
        hotkeys = {}
        for v in views:
            if v.hotkey:
                hotkeys[v.hotkey] = v.key

        def _on_key(e: Any) -> None:
            palette = self._command_palette
            if palette is not None and palette.is_open:
                return
            if e.action != "keydown" or any(
                getattr(e.modifiers, f, False) for f in ("alt", "ctrl", "meta", "shift")
            ):
                return
            view = hotkeys.get(e.key.name) if hasattr(e.key, "name") else None
            if view:
                self.switch_view(view)

        ui.keyboard().on_key(_on_key)

    def _open_command_palette(self) -> None:
        if self._command_palette is None:
            from computronium.ui.components.command_palette import (
                create_command_palette,
            )

            self._command_palette = create_command_palette(self)
            self._command_palette.build()
        self._command_palette.toggle()

    # ── Polling + atlas ───────────────────────────────────────────────────────

    async def _load_atlas(self) -> None:
        from nicegui import run

        try:
            result = await run.io_bound(self._atlas_data_impl, self.root, self.cache)
        except Exception as e:  # ruff: ignore[blind-except]
            logger.warning("Atlas load failed: %s", e)
            return
        if result is None or result[0] is None:
            return
        self._apply_atlas_result(result)

    def _atlas_data_impl(
        self, root: Path, cache: EmbedCache
    ) -> tuple[Figure | None, str | None, list[str]]:
        from computronium.visualization.live_atlas import _atlas_data

        return _atlas_data(root, cache)

    def _apply_atlas_result(
        self, result: tuple[Figure | None, str | None, list[str]]
    ) -> None:
        self.atlas_figure = result[0]
        if self.view == "atlas":
            self._views.pop("atlas", None)
            self._rendered.discard("atlas")
            self._render_view("atlas")

    def _config_signature_of(self) -> tuple[tuple[int, int], ...]:
        stamps: list[tuple[int, int]] = []
        for name in self._CONFIG_WATCHED:
            try:
                stat = (self.root / name).stat()
            except OSError:
                continue
            stamps.append((stat.st_mtime_ns, stat.st_size))
        return tuple(stamps)

    def _reload_objectives(self) -> tuple[ObjectiveSpec, ...] | None:
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
        from computronium.autoscientist.objectives import objective_names

        new = self._reload_objectives()
        if new is None or objective_names(new) == objective_names(self.objectives):
            return
        event_bus.publish(ConfigChanged(objectives=objective_names(new)))

    def _poll(self) -> None:
        new_sig = watch_signature(self.root)
        if new_sig != self.last_signature:
            self.last_signature = new_sig
            event_bus.publish(ArtifactChanged(signature=new_sig, root=self.root))
            self._refresh_current()
        config_sig = self._config_signature_of()
        if config_sig != self._last_config_signature:
            self._last_config_signature = config_sig
            self._maybe_reload_objectives()

    def switch_root(self, root: Path) -> None:
        if root == self.root or root not in self.roots:
            return
        self.root = root
        self.log_path = resolve_log_path(root, self._explicit_log_path)
        self.cache = EmbedCache()
        self.objectives = _objectives_from_heartbeat(root)
        self.atlas_figure = None
        self.loss_history.clear()
        self.event_history.clear()
        self.reports.clear()
        self.session_delta = SessionDelta()
        self.intent = None
        self.last_signature = watch_signature(root)
        self._config_signature = self._config_signature_of()
        self._last_config_signature = self._config_signature
        for panel in self._views.values():
            panel.on_unmount()
        for panel in self._tab_panels.values():
            panel.on_unmount()
        self._views.clear()
        self._tab_panels.clear()
        self._rendered.clear()
        if self._forensics is not None:
            self._forensics.update_data(None)
        from computronium.ui.state import selected_cell_key

        selected_cell_key.set(None)
        self._invalidate()
        self._refresh_current()

    # ── Build ─────────────────────────────────────────────────────────────────

    def build(self) -> None:
        ui.colors(primary=PRIMARY, secondary=SECONDARY)
        ui.add_head_html(f"<style>{css_custom_properties()}</style>")
        ui.add_head_html(f"<style>{a11y_css()}</style>")
        ui.page_title("Computronium")

        self._render_header()
        self._render_body()
        self._bind_hotkeys()
        self._bind_hash_navigation()
        self._render_view(self.view)
        # Initialize active tab for current view
        tabs = registry.get_panels_for_view(self.view)
        if tabs:
            self._active_tab[self.view] = tabs[0].key

        ui.timer(0.1, self._start_streams, once=True)
        ui.timer(0.5, self._load_atlas, once=True)
        ui.timer(self.poll_seconds, self._poll)

    def _bind_hash_navigation(self) -> None:
        """Sync the URL hash both ways: writes happen on navigation, client
        state is read back on a 1 s timer (deep-link load, refresh,
        back/forward). Headless-safe: without a client the read is a no-op.
        """
        ui.timer(1.0, self._sync_hash_from_client)

    async def _sync_hash_from_client(self) -> None:
        try:
            current = await ui.run_javascript("window.location.hash")
        except Exception:  # noqa: BLE001 (no client in headless tests)
            return
        self._apply_hash(str(current or ""))

    def _apply_hash(self, raw: str) -> None:
        """Navigate to a ``#view`` or ``#view/tab`` hash; ignore unknowns."""
        view_key, tab_key = parse_hash(raw)
        if view_key is None or registry.get_view(view_key) is None:
            return
        if view_key != self.view:
            self.switch_view(view_key)
        if tab_key is not None:
            tabs = {spec.key for spec in registry.get_panels_for_view(view_key)}
            if tab_key in tabs and self._active_tab.get(view_key) != tab_key:
                self._switch_tab(view_key, tab_key)

    def _update_hash(self, view_key: str, tab_key: str | None = None) -> None:
        """Update URL hash for deep linking."""
        try:
            ui.run_javascript(
                f"window.location.hash = '{format_hash(view_key, tab_key)}'"
            )
        except AssertionError, RuntimeError:
            pass  # No client context (headless test)


def build_dashboard(
    root: Path,
    log_path: Path | None = None,
    poll_seconds: float = POLL_SECONDS,
    daemon_url: str | None = None,
    *,
    density: Literal["comfortable", "compact"] = "comfortable",
    roots: tuple[Path, ...] | None = None,
) -> None:
    """Build the Computronium dashboard."""
    app = DashboardApp(
        root=root,
        log_path=log_path,
        poll_seconds=poll_seconds,
        daemon_url=daemon_url,
        density=density,
        roots=roots,
    )
    app.build()
