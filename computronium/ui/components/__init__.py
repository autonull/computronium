"""UI components package."""

from computronium.ui.components.activity_feed import ActivityFeed, FeedEvent
from computronium.ui.components.constitution_health import (
    ConstitutionHealthPanel,
    ConstitutionInvariant,
    create_invariants_from_monitor,
)
from computronium.ui.components.discovery_map import (
    DiscoveryMap,
    MapRegion,
    MapSpecimen,
    create_discovery_map_from_atlas,
    get_dynamics_shape,
    get_outcome_style,
)
from computronium.ui.components.episode_timeline import (
    EpisodeEvent,
    EpisodeTimeline,
)
from computronium.ui.components.field_reports import FieldReport, FieldReports
from computronium.ui.components.health_panel import HealthPanel, HealthTile
from computronium.ui.components.lineage_viewer import (
    LineageEdge,
    LineageNode,
    LineageViewer,
    create_lineage_from_phylogeny,
)
from computronium.ui.components.repair_bench import (
    DefectRow,
    RepairBench,
    create_repair_rows_from_defects,
)
from computronium.ui.components.tradeoffs_panel import (
    ParetoCell,
    TradeoffsPanel,
    create_pareto_cells_from_atlas,
)

__all__ = [
    "ActivityFeed",
    "ConstitutionHealthPanel",
    "ConstitutionInvariant",
    "DefectRow",
    "DiscoveryMap",
    "EpisodeEvent",
    "EpisodeTimeline",
    "FeedEvent",
    "FieldReport",
    "FieldReports",
    "HealthPanel",
    "HealthTile",
    "LineageEdge",
    "LineageNode",
    "LineageViewer",
    "MapRegion",
    "MapSpecimen",
    "ParetoCell",
    "RepairBench",
    "TradeoffsPanel",
    "create_discovery_map_from_atlas",
    "create_invariants_from_monitor",
    "create_lineage_from_phylogeny",
    "create_pareto_cells_from_atlas",
    "create_repair_rows_from_defects",
    "get_dynamics_shape",
    "get_outcome_style",
]
