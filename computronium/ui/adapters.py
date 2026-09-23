"""Concrete Data Adapters (A2) — pure adapters from DashboardSnapshot to panel data.

Each adapter transforms the raw snapshot into the typed dataclass the panel expects.
Adapters reuse live_atlas loaders (_measured_cells, read_defects, pareto_strip_rows, etc.)
rather than re-querying artifacts directly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from computronium.ui.components.constitution_health import (
    ConstitutionHealthData,
    create_invariants_from_monitor,
)
from computronium.ui.components.lineage_viewer import LineageEdge, LineageNode
from computronium.ui.data_adapters import (
    AdapterContext,
    make_adapter,
    make_context_adapter,
)
from computronium.ui.recognition import Badge, Quest, Record

if TYPE_CHECKING:
    from pathlib import Path

    from plotly.graph_objects import Figure as go_Figure

    from computronium.ui.components.discovery_map import MapRegion, MapSpecimen
    from computronium.visualization.live_atlas import DashboardSnapshot


@dataclass(frozen=True, slots=True)
class DiscoveryMapData:
    """Data for DiscoveryMap panel."""

    specimens: list[MapSpecimen]
    regions: list[MapRegion]
    fog_coverage_pct: float
    atlas_figure: go_Figure | None


def _with_layout(df: Any) -> Any:
    """Attach deterministic 2-D coordinates derived from the cell identity.

    Pure stand-in for the UMAP atlas layout: coordinates are a stable hash
    of the cell's primitive tuple, so the map never depends on a refit.
    """
    import hashlib

    import pandas as pd

    if df.empty or "x" in df.columns:
        return df

    def _coord_pair(label: str) -> tuple[float, float]:
        digest = hashlib.blake2b(label.encode(), digest_size=16).digest()
        return (
            int.from_bytes(digest[:8]) / 2**64,
            int.from_bytes(digest[8:]) / 2**64,
        )

    identity = ("dynamics", "credit", "update", "topology", "task")
    missing = pd.Series("?", index=df.index, dtype=object)
    parts = [df[col].astype(str) if col in df.columns else missing for col in identity]
    labels = parts[0]
    for part in parts[1:]:
        labels = labels + "|" + part
    coords = [_coord_pair(label) for label in labels]
    xs, ys = zip(*coords, strict=True)
    return df.assign(x=list(xs), y=list(ys))


def _coerce_float(mapping: dict[str, object], key: str, default: float = 0.0) -> float:
    value = mapping.get(key, default)
    return value if isinstance(value, int | float) else default


def _coerce_str(mapping: dict[str, object], key: str, default: str = "") -> str:
    value = mapping.get(key, default)
    return value if isinstance(value, str) else default


def adapt_discovery_map(snapshot: DashboardSnapshot, root: Path) -> DiscoveryMapData:
    """Adapt snapshot to DiscoveryMap data."""
    from computronium.ui.components.discovery_map import (
        create_discovery_map_from_atlas,
    )
    from computronium.visualization.atlas import (
        align_void_columns,
        load_cells,
        load_voids,
        pareto_top,
    )

    # Load cells and voids for the atlas
    cells_df = load_cells(root / "kb.sqlite")
    voids_df = align_void_columns(load_voids(root / "structural_voids.jsonl"))
    cells_df = _with_layout(cells_df)
    voids_df = _with_layout(voids_df)

    # Get Pareto front keys
    pareto_keys: set[str] = set()
    if not cells_df.empty:
        from computronium.autoscientist.objectives import DEFAULT_OBJECTIVES

        top = pareto_top(cells_df, k=len(cells_df), objectives=DEFAULT_OBJECTIVES)
        if "key" not in top.columns:
            top = top.assign(
                key=top["dynamics"].astype(str)
                + "|"
                + top["credit"].astype(str)
                + "|"
                + top["update"].astype(str)
            )
        pareto_keys = set(top["key"].tolist())

    # Create specimens and regions using existing helper; Pareto flags set
    # directly (no second specimen rebuild).
    specimens, regions = create_discovery_map_from_atlas(
        cells_df,
        voids_df,
        fog_coverage_pct=0.0,
        pareto_keys=pareto_keys or None,
    )

    # Get atlas figure from snapshot
    atlas_figure = snapshot.atlas

    # Calculate fog coverage from strata
    if snapshot.strata_rows:
        triples = snapshot.strata_rows[0].get("triples", 0)
        total_triples = int(triples) if isinstance(triples, int | float) else 0
    else:
        total_triples = 0
    fog_coverage_pct = min(100.0, float(total_triples) * 10.0)  # rough heuristic

    return DiscoveryMapData(
        specimens=specimens,
        regions=regions,
        fog_coverage_pct=fog_coverage_pct,
        atlas_figure=atlas_figure,
    )


# ============================================================================
# HealthPanel Adapter
# ============================================================================


@dataclass(frozen=True, slots=True)
class HealthTile:
    """A health status tile."""

    label: str
    value: str
    status: str  # "running_smoothly" | "needs_attention" | "unstable"
    detail: str


def adapt_health_panel(snapshot: DashboardSnapshot, root: Path) -> list[HealthTile]:
    """Adapt snapshot to HealthPanel tiles."""
    health = snapshot.health
    open_defects = int(_coerce_float(health, "open_defects"))
    resolved_defects = int(_coerce_float(health, "resolved_defects"))
    measured_cells = int(_coerce_float(health, "measured_cells"))
    nan_cells = int(_coerce_float(health, "nan_cells"))
    cells_per_burst = _coerce_float(health, "cells_per_burst")
    last_burst_walltime = health.get("last_burst_walltime_s")
    last_burst = _coerce_str(health, "last_burst", "N/A")

    tiles = [
        HealthTile(
            label="Open Defects",
            value=str(open_defects),
            status="needs_attention" if open_defects > 0 else "running_smoothly",
            detail="Unresolved runtime defects",
        ),
        HealthTile(
            label="Resolved Defects",
            value=str(resolved_defects),
            status="running_smoothly",
            detail="Fixed runtime defects",
        ),
        HealthTile(
            label="Measured Cells",
            value=str(measured_cells),
            status="running_smoothly",
            detail="Total cells in knowledge base",
        ),
        HealthTile(
            label="Diverged (NaN)",
            value=str(nan_cells),
            status="unstable"
            if nan_cells > 5
            else "needs_attention"
            if nan_cells > 0
            else "running_smoothly",
            detail="Cells with NaN loss",
        ),
        HealthTile(
            label="Cells / Burst",
            value=str(cells_per_burst),
            status="running_smoothly",
            detail="Average cells per burst",
        ),
        HealthTile(
            label="Last Burst Walltime",
            value=f"{last_burst_walltime:.1f}s"
            if isinstance(last_burst_walltime, int | float)
            else "—",
            status="running_smoothly",
            detail=f"Burst {last_burst}",
        ),
    ]
    return tiles


# ============================================================================
# TradeoffsPanel Adapter
# ============================================================================


@dataclass(frozen=True, slots=True)
class ParetoCell:
    """A cell on the Pareto front."""

    key: str
    label: str
    accuracy: float
    bp_deficit: float
    credit_alignment: float
    settle_horizon: float
    walltime_s: float
    dynamics: str
    credit: str
    update: str
    topology: str


@dataclass(frozen=True, slots=True)
class TradeoffsData:
    """Data for TradeoffsPanel."""

    pareto_cells: list[ParetoCell]
    objectives: list[str]
    selected_objective: str


def adapt_tradeoffs_panel(snapshot: DashboardSnapshot, root: Path) -> TradeoffsData:
    """Adapt snapshot to TradeoffsPanel data (membership from snapshot.pareto_rows)."""
    from computronium.autoscientist.objectives import objective_names

    pareto_cells = [
        ParetoCell(
            key=str(row.get("label", "")),
            label=str(row.get("label", "")),
            accuracy=_coerce_float(row, "accuracy"),
            bp_deficit=_coerce_float(row, "bp_deficit"),
            credit_alignment=_coerce_float(row, "credit_alignment"),
            settle_horizon=_coerce_float(row, "settle_horizon"),
            walltime_s=_coerce_float(row, "walltime_s"),
            dynamics="",
            credit="",
            update="",
            topology="",
        )
        for row in snapshot.pareto_rows
    ]

    return TradeoffsData(
        pareto_cells=pareto_cells,
        objectives=list(objective_names(snapshot.objectives))
        if snapshot.objectives
        else [],
        selected_objective=snapshot.objectives[0].name.value
        if snapshot.objectives
        else "accuracy",
    )


# ============================================================================
# RepairBench Adapter
# ============================================================================


@dataclass(frozen=True, slots=True)
class DefectRow:
    """A defect row for the repair bench."""

    defect_id: str
    count: int
    cells: int
    status: str
    error_class: str
    last_seen: float
    message: str


@dataclass(frozen=True, slots=True)
class RepairBenchData:
    """Data for RepairBench panel."""

    defects: list[DefectRow]


def adapt_repair_bench(snapshot: DashboardSnapshot, root: Path) -> RepairBenchData:
    """Adapt snapshot to RepairBench data."""
    defects = [
        DefectRow(
            defect_id=str(row.get("defect_id", "")),
            count=int(_coerce_float(row, "count")),
            cells=int(_coerce_float(row, "cells")),
            status=str(row.get("status", "")),
            error_class=str(row.get("error_class", "")),
            last_seen=_coerce_float(row, "last_seen"),
            message=str(row.get("message", "")),
        )
        for row in snapshot.funnel_rows
    ]
    return RepairBenchData(defects=defects)


# ============================================================================
# ConstitutionHealthPanel Adapter
# ============================================================================


def adapt_constitution_health(
    snapshot: DashboardSnapshot, root: Path
) -> ConstitutionHealthData:
    """Adapt snapshot to ConstitutionHealthPanel data."""
    health = snapshot.health
    return ConstitutionHealthData(
        invariants=create_invariants_from_monitor(
            spectral_radius=_coerce_float(health, "spectral_radius", 0.85),
            lyapunov_exponent=_coerce_float(health, "lyapunov_exponent", 0.1),
            energy_injected=_coerce_float(health, "energy_injected", 1.0),
            energy_consumed=_coerce_float(health, "energy_consumed", 0.5),
            resource_usage=_coerce_float(health, "resource_usage", 1e6),
            resource_budget=_coerce_float(health, "resource_budget", 1e9),
            max_recursion_depth=int(_coerce_float(health, "max_recursion_depth", 10)),
            tau=_coerce_float(health, "tau", 1.029),
        )
    )


# ============================================================================
# LineageViewer Adapter
# ============================================================================


@dataclass(frozen=True, slots=True)
class LineageData:
    """Data for LineageViewer panel."""

    nodes: list[LineageNode]
    edges: list[LineageEdge]


def _build_lineage_from_events(
    events: list[dict],
) -> tuple[list[LineageNode], list[LineageEdge]]:
    """Build lineage graph from event log (reference implementation from UX-L10)."""
    nodes: dict[str, LineageNode] = {}
    edges: dict[tuple[str, str], LineageEdge] = {}

    for event in events:
        kind = event.get("kind", "")

        if kind == "genome_created":
            genome_id = event.get("genome_id", "")
            tier = event.get("tier", 1)
            fitness = event.get("fitness", 0.0)
            episode = event.get("episode", 0)
            parent_id = event.get("parent_id")
            mutation_type = event.get("mutation_type", "Unknown")
            slope = event.get("slope", 0.0)
            accepted = event.get("accepted", True)

            # Create or update node
            if genome_id in nodes:
                old = nodes[genome_id]
                nodes[genome_id] = LineageNode(
                    genome_id=old.genome_id,
                    tier=tier,
                    fitness=fitness,
                    episode=episode,
                    parent_id=parent_id,
                    mutation_type=mutation_type,
                    slope=slope,
                )
            else:
                nodes[genome_id] = LineageNode(
                    genome_id=genome_id,
                    tier=tier,
                    fitness=fitness,
                    episode=episode,
                    parent_id=parent_id,
                    mutation_type=mutation_type,
                    slope=slope,
                )

            # Add edge if parent exists
            if parent_id:
                edge_key = (parent_id, genome_id)
                if edge_key not in edges:  # Idempotent: first event wins
                    edges[edge_key] = LineageEdge(
                        from_genome=parent_id,
                        to_genome=genome_id,
                        mutation_type=mutation_type,
                        slope=slope,
                        accepted=accepted,
                    )

        elif kind == "genome_fitness_updated":
            genome_id = event.get("genome_id", "")
            if genome_id in nodes:
                old = nodes[genome_id]
                nodes[genome_id] = LineageNode(
                    genome_id=old.genome_id,
                    tier=old.tier,
                    fitness=event.get("fitness", old.fitness),
                    episode=old.episode,
                    parent_id=old.parent_id,
                    mutation_type=old.mutation_type,
                    slope=old.slope,
                )

    return list(nodes.values()), list(edges.values())


def adapt_lineage_viewer(snapshot: DashboardSnapshot, root: Path) -> LineageData:
    """Adapt snapshot to LineageViewer data."""
    # Build lineage from event history in snapshot (or from a lineage file)
    events = getattr(snapshot, "event_history", [])
    nodes, edges = _build_lineage_from_events(events)
    return LineageData(nodes=nodes, edges=edges)


# ============================================================================
# EpisodeTimeline Adapter
# ============================================================================


@dataclass(frozen=True, slots=True)
class EpisodeEvent:
    """An episode event."""

    timestamp: float
    event_type: str
    cell_key: str
    metrics: dict[str, float]
    details: str


@dataclass(frozen=True, slots=True)
class EpisodeTimelineData:
    """Data for EpisodeTimeline panel."""

    episodes: list[EpisodeEvent]


def adapt_episode_timeline(
    snapshot: DashboardSnapshot, root: Path
) -> EpisodeTimelineData:
    """Adapt snapshot to EpisodeTimeline data."""
    episodes = [
        EpisodeEvent(
            timestamp=_coerce_float(ev, "timestamp"),
            event_type=str(ev.get("kind", "")),
            cell_key=str(ev.get("cell", "")),
            metrics={},
            details=str(ev.get("summary", "")),
        )
        for ev in snapshot.event_history
    ]
    return EpisodeTimelineData(episodes=episodes)


# ============================================================================
# ProgressPanel Adapter
# ============================================================================


@dataclass(frozen=True, slots=True)
class ProgressData:
    """Data for ProgressPanel."""

    badges: list[Badge]
    quests: list[Quest]
    records: list[Record]


def adapt_progress_panel(
    snapshot: DashboardSnapshot, root: Path, recognition_store: Any | None = None
) -> ProgressData:
    """Adapt snapshot to ProgressPanel data using recognition state store."""
    if recognition_store is None:
        return ProgressData(badges=[], quests=[], records=[])

    state = recognition_store.rebuild_from_events()

    badges = [
        Badge(
            id=b.id,
            name=b.name,
            description=b.description,
            icon=b.icon,
            evidence_kind=b.evidence_kind,
            evidence_query=b.evidence_query,
            register_explorer=b.register_explorer,
            register_lab=b.register_lab,
        )
        for b in state.badges
    ]

    quests = [
        Quest(
            id=q.id,
            name=q.name,
            description=q.description,
            icon=q.icon,
            objective=q.objective,
            completion_message_explorer=q.completion_message_explorer,
            completion_message_lab=q.completion_message_lab,
            progress_current=q.progress_current,
            progress_target=q.progress_target,
            completed=q.completed,
            opted_in=q.opted_in,
            completed_at=q.completed_at,
        )
        for q in state.quests
    ]

    records = [
        Record(
            id=r.id,
            objective=r.objective,
            value=r.value,
            cell_key=r.cell_key,
            timestamp=r.timestamp,
            scope=r.scope,
            register_explorer=r.register_explorer,
            register_lab=r.register_lab,
        )
        for r in state.records
    ]

    return ProgressData(badges=badges, quests=quests, records=records)


def _adapt_progress_from_ctx(ctx: AdapterContext) -> ProgressData:
    """Context-aware progress adapter: recognition store rides AdapterContext."""
    return adapt_progress_panel(ctx.snapshot, ctx.root, ctx.recognition_store)


# ============================================================================
# WorkshopPanel Adapter
# ============================================================================


@dataclass(frozen=True, slots=True)
class ProbeBatch:
    """A batch of probes."""

    id: str
    timestamp: float
    n_probes: int
    status: str
    metrics: dict[str, float]


@dataclass(frozen=True, slots=True)
class StagnationSnapshot:
    """A stagnation snapshot."""

    timestamp: float
    diversity_score: float
    novelty_rate: float
    stratum_repeat_rate: float


@dataclass(frozen=True, slots=True)
class GenomeHealthPoint:
    """A genome health data point."""

    generation: int
    fitness: float
    diversity: float
    mutations: int


@dataclass(frozen=True, slots=True)
class MutationProposal:
    """A mutation proposal."""

    id: str
    parent: str
    mutation_type: str
    params: dict[str, float]
    predicted_improvement: float


@dataclass(frozen=True, slots=True)
class VetoEntry:
    """A veto entry."""

    timestamp: float
    proposal_id: str
    reason: str
    vetoed_by: str


@dataclass(frozen=True, slots=True)
class WorkshopData:
    """Data for WorkshopPanel."""

    probe_batches: list[ProbeBatch]
    stagnation_snapshots: list[StagnationSnapshot]
    genome_health: list[GenomeHealthPoint]
    mutation_proposals: list[MutationProposal]
    veto_log: list[VetoEntry]


def adapt_workshop_panel(snapshot: DashboardSnapshot, root: Path) -> WorkshopData:
    """Adapt snapshot to WorkshopPanel data.

    Intentionally empty: probe batches, stagnation snapshots, genome
    points, mutation proposals, and veto entries would come from the
    Auto-Evolve event log, which no producer writes yet.
    """
    return WorkshopData(
        probe_batches=[],
        stagnation_snapshots=[],
        genome_health=[],
        mutation_proposals=[],
        veto_log=[],
    )


# ============================================================================
# CampaignCardGallery Adapter
# ============================================================================


@dataclass(frozen=True, slots=True)
class CampaignCard:
    """A campaign card."""

    path: str
    name: str
    status: str
    cells: int
    best_accuracy: float
    last_updated: float


@dataclass(frozen=True, slots=True)
class CampaignGalleryData:
    """Data for CampaignCardGallery."""

    campaigns: list[CampaignCard]


def adapt_campaign_gallery(
    snapshot: DashboardSnapshot, root: Path
) -> CampaignGalleryData:
    """Adapt snapshot to CampaignCardGallery data."""
    campaigns_dir = root / "campaigns"
    campaigns = []
    if campaigns_dir.exists():
        for item in campaigns_dir.iterdir():
            if item.is_dir():
                campaigns.append(
                    CampaignCard(
                        path=str(item),
                        name=item.name,
                        status="active",
                        cells=0,
                        best_accuracy=0.0,
                        last_updated=item.stat().st_mtime,
                    )
                )
    return CampaignGalleryData(campaigns=campaigns)


# ============================================================================
# PreviewShelf Adapter
# ============================================================================


@dataclass(frozen=True, slots=True)
class PreviewItem:
    """A preview shelf item."""

    key: str
    label: str
    metrics: dict[str, float]
    status: str


@dataclass(frozen=True, slots=True)
class PreviewShelfData:
    """Data for PreviewShelf."""

    items: list[PreviewItem]


def adapt_preview_shelf(snapshot: DashboardSnapshot, root: Path) -> PreviewShelfData:
    """Adapt snapshot to PreviewShelf data."""
    return PreviewShelfData(items=[])


# ============================================================================
# RegionNaming Adapter
# ============================================================================


@dataclass(frozen=True, slots=True)
class RegionName:
    """A named region."""

    name: str
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    cells: list[str]


@dataclass(frozen=True, slots=True)
class RegionNamingData:
    """Data for RegionNaming panel."""

    regions: list[RegionName]


def adapt_region_naming(snapshot: DashboardSnapshot, root: Path) -> RegionNamingData:
    """Adapt snapshot to RegionNaming data."""
    return RegionNamingData(regions=[])


# ============================================================================
# TeamWall Adapter
# ============================================================================


@dataclass(frozen=True, slots=True)
class TeamMember:
    """A team member."""

    name: str
    role: str
    avatar: str
    stats: dict[str, float]


@dataclass(frozen=True, slots=True)
class TeamWallData:
    """Data for TeamWall panel."""

    members: list[TeamMember]


def adapt_team_wall(snapshot: DashboardSnapshot, root: Path) -> TeamWallData:
    """Adapt snapshot to TeamWall data."""
    return TeamWallData(members=[])


# ============================================================================
# ProbeAnalytics Adapter
# ============================================================================


@dataclass(frozen=True, slots=True)
class ProbeAnalyticsData:
    """Data for ProbeAnalytics panel."""

    probes: list[ProbeBatch]
    metrics_history: list[dict[str, float]]


def adapt_probe_analytics(
    snapshot: DashboardSnapshot, root: Path
) -> ProbeAnalyticsData:
    """Adapt snapshot to ProbeAnalytics data.

    Intentionally empty: probe batches would come from the Auto-Evolve
    event log (probe-batch records), which no producer writes yet.
    """
    return ProbeAnalyticsData(probes=[], metrics_history=[])


# ============================================================================
# StagnationDashboard Adapter
# ============================================================================


@dataclass(frozen=True, slots=True)
class StagnationDashboardData:
    """Data for StagnationDashboard panel."""

    diversity: dict[str, float]
    alerts: list[str]


def adapt_stagnation_dashboard(
    snapshot: DashboardSnapshot, root: Path
) -> StagnationDashboardData:
    """Adapt snapshot to StagnationDashboard data."""
    return StagnationDashboardData(
        diversity=snapshot.diversity,
        alerts=snapshot.alerts,
    )


# ============================================================================
# GenomeHealthTracker Adapter
# ============================================================================


@dataclass(frozen=True, slots=True)
class GenomeHealthData:
    """Data for GenomeHealthTracker panel."""

    history: list[GenomeHealthPoint]


def adapt_genome_health(snapshot: DashboardSnapshot, root: Path) -> GenomeHealthData:
    """Adapt snapshot to GenomeHealthTracker data.

    Intentionally empty: genome fitness history would come from the
    Auto-Evolve event log (per-generation records), which no producer
    writes yet.
    """
    return GenomeHealthData(history=[])


# ============================================================================
# MutationExplorer Adapter
# ============================================================================


@dataclass(frozen=True, slots=True)
class MutationExplorerData:
    """Data for MutationExplorer panel."""

    proposals: list[MutationProposal]


def adapt_mutation_explorer(
    snapshot: DashboardSnapshot, root: Path
) -> MutationExplorerData:
    """Adapt snapshot to MutationExplorer data.

    Intentionally empty: mutation proposals would come from the
    Auto-Evolve event log, which no producer writes yet.
    """
    return MutationExplorerData(proposals=[])


# ============================================================================
# VetoLog Adapter
# ============================================================================


@dataclass(frozen=True, slots=True)
class VetoLogData:
    """Data for VetoLog panel."""

    entries: list[VetoEntry]


def adapt_veto_log(snapshot: DashboardSnapshot, root: Path) -> VetoLogData:
    """Adapt snapshot to VetoLog data.

    Intentionally empty: veto entries would come from the Auto-Evolve
    event log (veto events), which no producer writes yet.
    """
    return VetoLogData(entries=[])


# ============================================================================
# ActivityFeed Adapter
# ============================================================================


@dataclass(frozen=True, slots=True)
class FeedEvent:
    """A feed event."""

    timestamp: float
    kind: str
    icon: str
    color: str
    summary: str


@dataclass(frozen=True, slots=True)
class ActivityFeedData:
    """Data for ActivityFeed panel."""

    events: list[FeedEvent]


def adapt_activity_feed(snapshot: DashboardSnapshot, root: Path) -> ActivityFeedData:
    """Adapt snapshot event history to ActivityFeed data."""
    events = [
        FeedEvent(
            timestamp=_coerce_float(ev, "timestamp"),
            kind=str(ev.get("kind", "")),
            icon=str(ev.get("icon", "ℹ️")),
            color=str(ev.get("color", "primary")),
            summary=str(ev.get("summary", "")),
        )
        for ev in snapshot.event_history
    ]
    return ActivityFeedData(events=events)


# ============================================================================
# FieldReports Adapter
# ============================================================================


@dataclass(frozen=True, slots=True)
class FieldReport:
    """A field report."""

    timestamp: float
    title: str
    content: str
    severity: str


@dataclass(frozen=True, slots=True)
class FieldReportsData:
    """Data for FieldReports panel."""

    reports: list[FieldReport]


def adapt_field_reports(snapshot: DashboardSnapshot, root: Path) -> FieldReportsData:
    """Adapt snapshot event history to FieldReports data (alerts only)."""
    reports = [
        FieldReport(
            timestamp=_coerce_float(ev, "timestamp"),
            title=str(ev.get("kind", "")),
            content=str(ev.get("summary", "")),
            severity=str(ev.get("color", "info")),
        )
        for ev in snapshot.event_history
        if str(ev.get("color", "")) in {"negative", "warning", "positive"}
    ]
    return FieldReportsData(reports=reports)


# ============================================================================
# Adapter Registry
# ============================================================================

ADAPTERS = {
    "discovery_map": make_adapter(adapt_discovery_map),
    "health": make_adapter(adapt_health_panel),
    "tradeoffs": make_adapter(adapt_tradeoffs_panel),
    "repair_bench": make_adapter(adapt_repair_bench),
    "constitution": make_adapter(adapt_constitution_health),
    "lineage": make_adapter(adapt_lineage_viewer),
    "episodes": make_adapter(adapt_episode_timeline),
    "progress": make_context_adapter(_adapt_progress_from_ctx),
    "workshop": make_adapter(adapt_workshop_panel),
    "campaigns": make_adapter(adapt_campaign_gallery),
    "preview": make_adapter(adapt_preview_shelf),
    "region_naming": make_adapter(adapt_region_naming),
    "team": make_adapter(adapt_team_wall),
    "probe_analytics": make_adapter(adapt_probe_analytics),
    "stagnation": make_adapter(adapt_stagnation_dashboard),
    "genome_health": make_adapter(adapt_genome_health),
    "mutations": make_adapter(adapt_mutation_explorer),
    "veto_log": make_adapter(adapt_veto_log),
    "activity_feed": make_adapter(adapt_activity_feed),
    "field_reports": make_adapter(adapt_field_reports),
}


def get_adapter(panel_key: str):
    """Get adapter for a panel key."""
    return ADAPTERS.get(panel_key)
