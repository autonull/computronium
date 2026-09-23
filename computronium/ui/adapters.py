"""Concrete Data Adapters (A2) — pure adapters from DashboardSnapshot to panel data.

Each adapter transforms the raw snapshot into the typed dataclass the panel expects.
Adapters reuse live_atlas loaders (_measured_cells, read_defects, pareto_strip_rows, etc.)
rather than re-querying artifacts directly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from computronium.ui.components.discovery_map import MapRegion, MapSpecimen
from computronium.ui.data_adapters import make_adapter

if TYPE_CHECKING:
    from pathlib import Path

    from plotly.graph_objects import Figure as go_Figure

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

    if df.empty or "x" in df.columns:
        return df

    def _coord(label: str, salt: bytes) -> float:
        digest = hashlib.blake2b(label.encode(), key=salt, digest_size=8).digest()
        return int.from_bytes(digest) / 2**64

    def _label(row: Any) -> str:
        parts = [
            str(row.get(c, "?"))
            for c in ("dynamics", "credit", "update", "topology", "task")
        ]
        return "|".join(parts)

    labels = [_label(row) for _, row in df.iterrows()]
    return df.assign(
        x=[_coord(label, b"x") for label in labels],
        y=[_coord(label, b"y") for label in labels],
    )


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
                key=[
                    f"{row['dynamics']}|{row['credit']}|{row['update']}"
                    for _, row in top.iterrows()
                ]
            )
        pareto_keys = set(top["key"].tolist())

    # Create specimens and regions using existing helper
    specimens, regions = create_discovery_map_from_atlas(
        cells_df, voids_df, fog_coverage_pct=0.0
    )

    # Update pareto flags
    specimens = [
        MapSpecimen(
            key=s.key,
            x=s.x,
            y=s.y,
            dynamics=s.dynamics,
            credit=s.credit,
            update=s.update,
            topology=s.topology,
            accuracy=s.accuracy,
            bp_deficit=s.bp_deficit,
            outcome=s.outcome,
            is_void=s.is_void,
            is_pareto=s.key in pareto_keys,
        )
        for s in specimens
    ]

    # Get atlas figure from snapshot
    atlas_figure = snapshot.atlas

    # Calculate fog coverage from strata
    total_triples = (
        int(snapshot.strata_rows[0]["triples"]) if snapshot.strata_rows else 0
    )
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
    open_defects = int(health.get("open_defects", 0))
    resolved_defects = int(health.get("resolved_defects", 0))
    measured_cells = int(health.get("measured_cells", 0))
    nan_cells = int(health.get("nan_cells", 0))
    cells_per_burst = float(health.get("cells_per_burst", 0.0))
    last_burst_walltime = health.get("last_burst_walltime_s")
    last_burst = health.get("last_burst", "N/A")

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
            value=f"{float(last_burst_walltime):.1f}s"
            if last_burst_walltime is not None
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
    """Adapt snapshot to TradeoffsPanel data."""
    from computronium.autoscientist.objectives import DEFAULT_OBJECTIVES
    from computronium.visualization.live_atlas import pareto_strip_rows

    pareto_rows = pareto_strip_rows(root, objectives=DEFAULT_OBJECTIVES)
    pareto_cells = [
        ParetoCell(
            key=str(row.get("label", "")),
            label=str(row.get("label", "")),
            accuracy=float(row.get("accuracy", 0.0)),
            bp_deficit=float(row.get("bp_deficit", 0.0)),
            credit_alignment=float(row.get("credit_alignment", 0.0)),
            settle_horizon=float(row.get("settle_horizon", 0.0)),
            walltime_s=float(row.get("walltime_s", 0.0)),
            dynamics="",
            credit="",
            update="",
            topology="",
        )
        for row in pareto_rows
    ]

    return TradeoffsData(
        pareto_cells=pareto_cells,
        objectives=[obj.name for obj in DEFAULT_OBJECTIVES],
        selected_objective="accuracy",
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
            count=int(row.get("count", 0)),
            cells=int(row.get("cells", 0)),
            status=str(row.get("status", "")),
            error_class=str(row.get("error_class", "")),
            last_seen=float(row.get("last_seen", 0.0)),
            message=str(row.get("message", "")),
        )
        for row in snapshot.funnel_rows
    ]
    return RepairBenchData(defects=defects)


# ============================================================================
# ConstitutionHealthPanel Adapter
# ============================================================================


@dataclass(frozen=True, slots=True)
class ConstitutionInvariant:
    """A constitution invariant check."""

    name: str
    passed: bool
    value: float
    threshold: float
    detail: str


@dataclass(frozen=True, slots=True)
class ConstitutionHealthData:
    """Data for ConstitutionHealthPanel."""

    invariants: list[ConstitutionInvariant]


def adapt_constitution_health(
    snapshot: DashboardSnapshot, root: Path
) -> ConstitutionHealthData:
    """Adapt snapshot to ConstitutionHealthPanel data."""
    # Placeholder - would read from constitution checks
    invariants = [
        ConstitutionInvariant(
            name="Gradient Flow",
            passed=True,
            value=0.95,
            threshold=0.9,
            detail="Gradient norm within bounds",
        ),
        ConstitutionInvariant(
            name="Stability Margin",
            passed=True,
            value=1.2,
            threshold=1.0,
            detail="Spectral radius < 1",
        ),
        ConstitutionInvariant(
            name="Credit Alignment",
            passed=True,
            value=0.85,
            threshold=0.7,
            detail="Credit assignment aligned",
        ),
        ConstitutionInvariant(
            name="Energy Decrease",
            passed=True,
            value=0.99,
            threshold=0.95,
            detail="Free energy decreasing",
        ),
        ConstitutionInvariant(
            name="Bounded Activations",
            passed=True,
            value=0.0,
            threshold=1.0,
            detail="No exploding activations",
        ),
        ConstitutionInvariant(
            name="Dale's Law",
            passed=True,
            value=1.0,
            threshold=1.0,
            detail="Excitatory/inhibitory separation",
        ),
    ]
    return ConstitutionHealthData(invariants=invariants)


# ============================================================================
# LineageViewer Adapter
# ============================================================================


@dataclass(frozen=True, slots=True)
class LineageNode:
    """A node in the lineage graph."""

    id: str
    label: str
    x: float
    y: float
    color: str
    size: float
    metadata: dict[str, str]


@dataclass(frozen=True, slots=True)
class LineageEdge:
    """An edge in the lineage graph."""

    source: str
    target: str
    weight: float
    style: str


@dataclass(frozen=True, slots=True)
class LineageData:
    """Data for LineageViewer panel."""

    nodes: list[LineageNode]
    edges: list[LineageEdge]


def adapt_lineage_viewer(snapshot: DashboardSnapshot, root: Path) -> LineageData:
    """Adapt snapshot to LineageViewer data."""
    # Placeholder - would build from actual lineage data
    return LineageData(nodes=[], edges=[])


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
    # Convert event history to episode events
    episodes = [
        EpisodeEvent(
            timestamp=ev.timestamp,
            event_type=ev.kind,
            cell_key=ev.payload.get("cell", ""),
            metrics={},
            details=ev.summary,
        )
        for ev in []  # Would come from event history
    ]
    return EpisodeTimelineData(episodes=episodes)


# ============================================================================
# ProgressPanel Adapter
# ============================================================================


@dataclass(frozen=True, slots=True)
class Badge:
    """A badge."""

    id: str
    name: str
    description: str
    icon: str
    evidence_kind: str
    evidence_query: str
    register_explorer: str
    register_lab: str


@dataclass(frozen=True, slots=True)
class Quest:
    """A quest."""

    id: str
    name: str
    description: str
    icon: str
    objective: str
    completion_message_explorer: str
    completion_message_lab: str
    progress_current: int
    progress_target: int
    completed: bool
    opted_in: bool
    completed_at: float | None


@dataclass(frozen=True, slots=True)
class Record:
    """A personal best record."""

    id: str
    objective: str
    value: float
    cell_key: str
    timestamp: float
    scope: str
    register_explorer: str
    register_lab: str


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

    from computronium.ui.recognition import Badge, Quest, Record

    state = recognition_store.rebuild_from_events()

    # Convert RecognitionState to ProgressData types
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
    """Adapt snapshot to WorkshopPanel data."""
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
    """Adapt snapshot to ProbeAnalytics data."""
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
    """Adapt snapshot to GenomeHealthTracker data."""
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
    """Adapt snapshot to MutationExplorer data."""
    return MutationExplorerData(proposals=[])


# ============================================================================
# VetoLog Adapter
# ============================================================================


@dataclass(frozen=True, slots=True)
class VetoLogData:
    """Data for VetoLog panel."""

    entries: list[VetoEntry]


def adapt_veto_log(snapshot: DashboardSnapshot, root: Path) -> VetoLogData:
    """Adapt snapshot to VetoLog data."""
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
    """Adapt snapshot to ActivityFeed data."""
    return ActivityFeedData(events=[])


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
    """Adapt snapshot to FieldReports data."""
    return FieldReportsData(reports=[])


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
    "progress": make_adapter(adapt_progress_panel),
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
