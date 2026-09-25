"""Concrete Data Adapters (A2) — pure adapters from DashboardSnapshot to panel data.

Each adapter transforms the raw snapshot into the typed dataclass the panel expects.
Adapters reuse live_atlas loaders (_measured_cells, read_defects, pareto_strip_rows, etc.)
rather than re-querying artifacts directly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from computronium.ui.components.constitution_health import (
    ConstitutionHealthData,
    create_invariants_from_monitor,
)
from computronium.ui.components.lineage_viewer import LineageEdge, LineageNode
from computronium.ui.components.monitor import HealthTile
from computronium.ui.components.repair_bench import DefectRow, MaturationNode
from computronium.ui.components.tradeoffs_panel import (
    ParetoCell,
    create_pareto_cells_from_atlas,
)
from computronium.ui.data_adapters import (
    make_adapter,
)

if TYPE_CHECKING:
    from pathlib import Path

    from plotly.graph_objects import Figure as go_Figure

    from computronium.autoscientist.objectives import ObjectiveSpec
    from computronium.ui.components.discovery_map import MapRegion, MapSpecimen
    from computronium.visualization.live_atlas import DashboardSnapshot


@dataclass(frozen=True, slots=True)
class DiscoveryMapData:
    """Data for DiscoveryMap panel."""

    specimens: list[MapSpecimen]
    regions: list[MapRegion]
    fog_coverage_pct: float
    atlas_figure: go_Figure | None
    pareto_cells: list[ParetoCell] | None = None
    campaigns_dir: Path | None = None


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


def _pareto_key_set(root: Path) -> set[str]:
    """Full cell keys on the Pareto front (shared by map + forensics adapters)."""
    from computronium.visualization.atlas import load_cells, pareto_top

    cells_df = load_cells(root / "kb.sqlite")
    if cells_df.empty:
        return set()
    from computronium.autoscientist.objectives import DEFAULT_OBJECTIVES

    top = pareto_top(cells_df, k=len(cells_df), objectives=DEFAULT_OBJECTIVES)
    if "key" not in top.columns:
        topo = top["topology"].astype(str) if "topology" in top.columns else "?"
        top = top.assign(
            key=top["dynamics"].astype(str)
            + "|"
            + top["credit"].astype(str)
            + "|"
            + top["update"].astype(str)
            + "|"
            + topo
        )
    return set(top["key"].tolist())


def adapt_discovery_map(snapshot: DashboardSnapshot, root: Path) -> DiscoveryMapData:
    """Adapt snapshot to DiscoveryMap data."""
    from computronium.ui.components.discovery_map import (
        create_discovery_map_from_atlas,
    )
    from computronium.visualization.atlas import (
        align_void_columns,
        load_cells,
        load_voids,
    )

    # Load cells and voids for the atlas
    cells_df = load_cells(root / "kb.sqlite")
    voids_df = align_void_columns(load_voids(root / "structural_voids.jsonl"))
    cells_df = _with_layout(cells_df)
    voids_df = _with_layout(voids_df)

    # Get Pareto front keys
    pareto_keys = _pareto_key_set(root)

    # Create specimens and regions using existing helper; Pareto/defect/
    # maturity flags set directly (no second specimen rebuild).
    specimens, regions = create_discovery_map_from_atlas(
        cells_df,
        voids_df,
        fog_coverage_pct=0.0,
        pareto_keys=pareto_keys or None,
        defect_cells=_defect_cell_keys(root),
        maturity_by_key=_maturity_by_key(root),
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
        pareto_cells=_pareto_cells_from_rows(snapshot.pareto_rows, snapshot.objectives),
        campaigns_dir=root / "campaigns",
    )


# ============================================================================
# HealthPanel Adapter
# ============================================================================


def adapt_health_panel(snapshot: DashboardSnapshot, root: Path) -> list[HealthTile]:
    """Adapt snapshot to health tiles."""
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
class TradeoffsData:
    """Data for TradeoffsPanel."""

    pareto_cells: list[ParetoCell]
    objectives: list[str]
    selected_objective: str


def _pareto_cells_from_rows(
    rows: list[dict[str, object]],
    objectives: tuple[ObjectiveSpec, ...] = (),
) -> list[ParetoCell]:
    """Shared Pareto-strip projection (used by Map + Trade-offs adapters)."""
    return create_pareto_cells_from_atlas(rows)


def adapt_tradeoffs_panel(snapshot: DashboardSnapshot, root: Path) -> TradeoffsData:
    """Adapt snapshot to TradeoffsPanel data (membership from snapshot.pareto_rows)."""
    from computronium.autoscientist.objectives import objective_names

    return TradeoffsData(
        pareto_cells=_pareto_cells_from_rows(snapshot.pareto_rows, snapshot.objectives),
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
class RepairBenchData:
    """Data for RepairBench panel."""

    defects: list[DefectRow]
    maturation_nodes: list[MaturationNode] = field(default_factory=list)


def adapt_repair_bench(snapshot: DashboardSnapshot, root: Path) -> RepairBenchData:
    """Adapt snapshot to RepairBench data (defects + maturation)."""
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
    maturation_nodes = [
        MaturationNode(
            level=str(row.get("level", "")).removeprefix("maturity:"),
            campaign=root.name,
            cells=[],
            count=int(_coerce_float(row, "count")),
        )
        for row in snapshot.maturation
        if str(row.get("level", "")).removeprefix("maturity:") in {"l0", "l1", "l2"}
    ]
    return RepairBenchData(defects=defects, maturation_nodes=maturation_nodes)


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
# WorkshopPanel Adapter (removed - replaced by Composer)
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
# Budget Adapter (§4.5) — burn-down, throughput, maturation, cost spread
# ============================================================================


@dataclass(frozen=True, slots=True)
class CostBreakdownRow:
    """Mean walltime per primitive on one axis."""

    axis: str
    primitive: str
    mean_walltime_s: float
    n: int


@dataclass(frozen=True, slots=True)
class BudgetData:
    """Data for the Budget panel (Monitor tab)."""

    measured: int
    target: int | None
    coverage_label: str
    mean_walltime_s: float
    cells_per_hour: float
    projected_remaining_s: int | None
    maturation: dict[str, int]
    breakdown: list[CostBreakdownRow]


def adapt_budget(snapshot: DashboardSnapshot, root: Path) -> BudgetData:
    """Adapt snapshot costs/maturation/health to budget data."""
    del root
    costs = snapshot.costs
    measured = int(_coerce_float(costs, "measured"))
    target = costs.get("target")
    target = target if isinstance(target, int) else None
    mean_walltime = _coerce_float(costs, "mean_walltime_s")
    remaining = costs.get("projected_remaining_s")
    remaining = remaining if isinstance(remaining, int) else None
    coverage = costs.get("coverage_pct")
    maturation = {
        str(row.get("level", "")).removeprefix("maturity:"): int(
            _coerce_float(row, "count")
        )
        for row in snapshot.maturation
    }
    breakdown = [
        CostBreakdownRow(
            axis=str(row.get("axis", "")),
            primitive=str(row.get("primitive", "")),
            mean_walltime_s=_coerce_float(row, "mean_walltime_s"),
            n=int(_coerce_float(row, "n")),
        )
        for row in snapshot.cost_breakdown
    ]
    return BudgetData(
        measured=measured,
        target=target,
        coverage_label=str(coverage) if isinstance(coverage, str) else "unknown",
        mean_walltime_s=mean_walltime,
        cells_per_hour=round(3600.0 / mean_walltime, 1) if mean_walltime > 0 else 0.0,
        projected_remaining_s=remaining,
        maturation=maturation,
        breakdown=breakdown,
    )


# ============================================================================
# Evidence Adapter (§4.6) — CEEC beliefs, experiments, decisions (read-only)
# ============================================================================


@dataclass(frozen=True, slots=True)
class BeliefRow:
    """One belief with its latest revision."""

    id: str
    statement: str
    probability_point: float | None
    status: str


@dataclass(frozen=True, slots=True)
class ExperimentRow:
    """One CEEC experiment (claim record)."""

    id: str
    question: str
    status: str


@dataclass(frozen=True, slots=True)
class DecisionRow:
    """One ledger decision."""

    id: str
    selected_experiment: str
    rationale: str


@dataclass(frozen=True, slots=True)
class EvidenceData:
    """Data for the Evidence view. Empty with a reason when no ledger exists."""

    beliefs: list[BeliefRow]
    experiments: list[ExperimentRow]
    decisions: list[DecisionRow]
    ledger_path: str | None = None
    empty_reason: str = ""


_LEDGER_NAMES = ("ledger.sqlite", "ceec.sqlite3")


def _coerce_optional_float(mapping: dict[str, object], key: str) -> float | None:
    value = mapping.get(key)
    return value if isinstance(value, float | int) else None


def _ledger_path(root: Path) -> Path | None:
    for name in _LEDGER_NAMES:
        candidate = root / name
        if candidate.is_file():
            return candidate
    return None


def _read_table(path: Path, table: str) -> list[dict[str, object]]:
    """Read one ledger table over a read-only connection. Never writes."""
    import sqlite3

    uri = f"file:{path}?mode=ro"
    with sqlite3.connect(uri, uri=True) as conn:
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(f"SELECT * FROM {table}").fetchall()  # ruff: ignore[hardcoded-sql-expression] — table is an internal constant
        except sqlite3.Error:
            return []
    return [dict(row) for row in rows]


def adapt_evidence(snapshot: DashboardSnapshot, root: Path) -> EvidenceData:
    """Adapt the CEEC ledger beside the campaign root to evidence rows.

    Read-only: opens the ledger with ``mode=ro`` and never creates it.
    A missing ledger yields empty data with an honest reason, not an error.
    """
    del snapshot
    path = _ledger_path(root)
    if path is None:
        return EvidenceData(
            beliefs=[],
            experiments=[],
            decisions=[],
            empty_reason="no CEEC ledger found",
        )
    revisions: dict[str, dict[str, object]] = {}
    for row in _read_table(path, "belief_revisions"):
        belief_id = str(row.get("belief_id", ""))
        if belief_id not in revisions or str(row.get("created_at", "")) >= str(
            revisions[belief_id].get("created_at", "")
        ):
            revisions[belief_id] = row
    beliefs = [
        BeliefRow(
            id=str(row.get("id", "")),
            statement=str(row.get("statement", "")),
            probability_point=_coerce_optional_float(rev, "probability_point"),
            status=str(rev.get("status", "unknown")),
        )
        for row in _read_table(path, "beliefs")
        if (rev := revisions.get(str(row.get("id", "")), {})) is not None
    ]
    experiments = [
        ExperimentRow(
            id=str(row.get("id", "")),
            question=str(row.get("question", "")),
            status=str(row.get("status", "")),
        )
        for row in _read_table(path, "experiments")
    ]
    decisions = [
        DecisionRow(
            id=str(row.get("id", "")),
            selected_experiment=str(row.get("selected_experiment", "")),
            rationale=str(row.get("rationale", "")),
        )
        for row in _read_table(path, "decisions")
    ]
    reason = ""
    if not beliefs and not experiments and not decisions:
        reason = "ledger is empty"
    return EvidenceData(
        beliefs=beliefs,
        experiments=experiments,
        decisions=decisions,
        ledger_path=str(path),
        empty_reason=reason,
    )


# ============================================================================
# Cell Forensics (§4.1) — everything about one cell for the Atlas drawer
# ============================================================================


@dataclass(frozen=True, slots=True)
class DefectExcerpt:
    """One defect record touching the cell (message head + status)."""

    defect_id: str
    error_class: str
    message: str
    status: str
    timestamp: float


@dataclass(frozen=True, slots=True)
class CellForensicsData:
    """Forensics for one cell key: coordinate, objectives, Pareto status,
    lineage (bursts/maturity), stability instruments, defect excerpts."""

    cell_key: str
    dynamics: str
    credit: str
    update: str
    topology: str
    accuracy: float
    walltime_s: float
    param_count: int
    flops: float
    memory_mb: float
    energy_per_step: float
    bp_deficit: float
    spectral_radius: float
    lyapunov_exponent: float
    max_singular_value: float
    credit_alignment: float
    psi_capacity: float
    settle_horizon: float
    maturity: tuple[str, ...]
    bursts: tuple[str, ...]
    is_pareto: bool
    is_nan: bool
    defects: tuple[DefectExcerpt, ...]


def _maturity_levels(levels: tuple[str, ...]) -> tuple[str, ...]:
    cleaned = [str(level).removeprefix("maturity:") for level in levels]
    return tuple(level for level in cleaned if level in {"l0", "l1", "l2"})


def _defect_cell_keys(root: Path) -> set[str]:
    """Cell keys with at least one defect record (read-only)."""
    from computronium.autoscientist.defects import read_defects

    return {record.cell for record in read_defects(root / "runtime_defects.jsonl")}


def _maturity_by_key(root: Path) -> dict[str, str]:
    """Highest maturity level per cell key (l2 > l1 > l0)."""
    from computronium.visualization.live_atlas import _measured_cells

    order = {"l0": 0, "l1": 1, "l2": 2}
    best: dict[str, str] = {}
    for row in _measured_cells(root):
        for level in _maturity_levels(row.levels):
            if order.get(level, -1) > order.get(best.get(row.key, ""), -1):
                best[row.key] = level
    return best


def adapt_cell_forensics(
    snapshot: DashboardSnapshot, root: Path, cell_key: str
) -> CellForensicsData | None:
    """Adapt one KB cell to forensics rows. Read-only; ``None`` when unknown.

    Representative row is the best-accuracy entry; bursts/maturity union
    across repeat measurements. Not in ``ADAPTERS`` — it takes a cell key,
    resolved from the ``selected_cell_key`` interaction signal.
    """
    from computronium.autoscientist.defects import read_defects
    from computronium.visualization.live_atlas import _measured_cells

    del snapshot
    rows = [row for row in _measured_cells(root) if row.key == cell_key]
    if not rows:
        return None
    best = max(rows, key=lambda row: row.accuracy)
    bursts: tuple[str, ...] = tuple(
        dict.fromkeys(burst for row in rows for burst in row.bursts)
    )
    maturity = _maturity_levels(tuple(level for row in rows for level in row.levels))
    defects = tuple(
        DefectExcerpt(
            defect_id=record.defect_id,
            error_class=record.error_class,
            message=record.message[:280],
            status=record.status,
            timestamp=record.timestamp,
        )
        for record in read_defects(root / "runtime_defects.jsonl")
        if record.cell == cell_key
    )
    return CellForensicsData(
        cell_key=cell_key,
        dynamics=best.dynamics,
        credit=best.credit,
        update=best.update,
        topology=best.topology,
        accuracy=best.accuracy,
        walltime_s=best.walltime,
        param_count=best.param_budget,
        flops=best.flops,
        memory_mb=best.memory_mb,
        energy_per_step=best.energy_per_step,
        bp_deficit=best.bp_deficit,
        spectral_radius=best.spectral_radius,
        lyapunov_exponent=best.lyapunov_exponent,
        max_singular_value=best.max_singular_value,
        credit_alignment=best.credit_alignment,
        psi_capacity=best.psi_capacity,
        settle_horizon=best.settle_horizon,
        maturity=maturity,
        bursts=bursts,
        is_pareto=cell_key in _pareto_key_set(root),
        is_nan=best.nan_loss,
        defects=defects,
    )


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
    "budget": make_adapter(adapt_budget),
    "evidence": make_adapter(adapt_evidence),
}


def get_adapter(panel_key: str):
    """Get adapter for a panel key."""
    return ADAPTERS.get(panel_key)
