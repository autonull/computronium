"""UI components package."""

from computronium.ui.components.activity_feed import ActivityFeed, FeedEvent
from computronium.ui.components.campaign_card import (
    CampaignCard,
    CampaignCardGallery,
    CampaignManifest,
    create_campaign_card,
    create_campaign_gallery,
)
from computronium.ui.components.composer import Composer, ComposerData
from computronium.ui.components.constitution_health import (
    ConstitutionHealthPanel,
    ConstitutionInvariant,
    create_invariants_from_monitor,
)
from computronium.ui.components.console import (
    CampaignInfo,
    Console,
    ConsoleData,
    DriverIntent,
    SessionDelta,
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
from computronium.ui.components.genome_health import (
    GenomeHealthPoint,
    GenomeHealthTracker,
    create_genome_health_tracker,
)
from computronium.ui.components.health_panel import HealthPanel, HealthTile
from computronium.ui.components.lineage_viewer import (
    LineageEdge,
    LineageNode,
    LineageViewer,
    create_lineage_from_phylogeny,
)
from computronium.ui.components.mutation_explorer import (
    MutationExplorer,
    MutationProposal,
    create_mutation_explorer,
)
from computronium.ui.components.preview_shelf import (
    PreviewEntry,
    PreviewShelf,
    create_auto_evolve_preview,
)
from computronium.ui.components.probe_analytics import (
    ProbeAnalytics,
    ProbeBatch,
    create_probe_analytics,
)
from computronium.ui.components.progress_panel import ProgressData, ProgressPanel
from computronium.ui.components.record import (
    HistoryEvent,
    LedgerEntry,
    LessonEntry,
    Record,
    RecordData,
    RecordLens,
)
from computronium.ui.components.region_naming import (
    RegionName,
    RegionNaming,
    create_region_naming,
)
from computronium.ui.components.repair_bench import (
    DefectRow,
    RepairBench,
    create_repair_rows_from_defects,
)
from computronium.ui.components.status_chip import ChipSegment, StatusChip, StatusChipData
from computronium.ui.components.stagnation_dashboard import (
    StagnationDashboard,
    StagnationDetector,
    StagnationSnapshot,
    create_stagnation_dashboard,
)
from computronium.ui.components.team_wall import (
    TeamMember,
    TeamProgress,
    TeamWall,
    create_team_wall,
)
from computronium.ui.components.tradeoffs_panel import (
    ParetoCell,
    TradeoffsPanel,
    create_pareto_cells_from_atlas,
)
from computronium.ui.components.veto_log import VetoEntry, VetoLog, create_veto_log
from computronium.ui.components.workshop import (
    CREDIT_OPTIONS,
    DYNAMICS_OPTIONS,
    GEOMETRY_OPTIONS,
    PLASTICITY_OPTIONS,
    SUBSTRATE_OPTIONS,
    UPDATE_OPTIONS,
    AxisOption,
    DialComposer,
    P2PToggle,
    RecipeCardPanel,
    WorkshopPanel,
    create_workshop_panel,
)

__all__ = [
    "CREDIT_OPTIONS",
    "DYNAMICS_OPTIONS",
    "GEOMETRY_OPTIONS",
    "PLASTICITY_OPTIONS",
    "SUBSTRATE_OPTIONS",
    "UPDATE_OPTIONS",
    "ActivityFeed",
    "AxisOption",
    "CampaignCard",
    "CampaignCardGallery",
    "CampaignInfo",
    "CampaignManifest",
    "ChipSegment",
    "Composer",
    "ComposerData",
    "Console",
    "ConsoleData",
    "ConstitutionHealthPanel",
    "ConstitutionInvariant",
    "DefectRow",
    "DialComposer",
    "DiscoveryMap",
    "DriverIntent",
    "EpisodeEvent",
    "EpisodeTimeline",
    "FeedEvent",
    "FieldReport",
    "FieldReports",
    "GenomeHealthPoint",
    "GenomeHealthTracker",
    "HealthPanel",
    "HealthTile",
    "HistoryEvent",
    "LedgerEntry",
    "LessonEntry",
    "LineageEdge",
    "LineageNode",
    "LineageViewer",
    "MapRegion",
    "MapSpecimen",
    "MutationExplorer",
    "MutationProposal",
    "P2PToggle",
    "ParetoCell",
    "PreviewEntry",
    "PreviewShelf",
    "ProbeAnalytics",
    "ProbeBatch",
    "ProgressData",
    "ProgressPanel",
    "RecipeCardPanel",
    "Record",
    "RecordData",
    "RecordLens",
    "RegionName",
    "RegionNaming",
    "RepairBench",
    "SessionDelta",
    "StagnationDashboard",
    "StagnationDetector",
    "StagnationSnapshot",
    "StatusChip",
    "StatusChipData",
    "TeamMember",
    "TeamProgress",
    "TeamWall",
    "TradeoffsPanel",
    "VetoEntry",
    "VetoLog",
    "WorkshopPanel",
    "create_auto_evolve_preview",
    "create_campaign_card",
    "create_campaign_gallery",
    "create_discovery_map_from_atlas",
    "create_genome_health_tracker",
    "create_invariants_from_monitor",
    "create_lineage_from_phylogeny",
    "create_mutation_explorer",
    "create_pareto_cells_from_atlas",
    "create_probe_analytics",
    "create_region_naming",
    "create_repair_rows_from_defects",
    "create_stagnation_dashboard",
    "create_team_wall",
    "create_veto_log",
    "create_workshop_panel",
    "get_dynamics_shape",
    "get_outcome_style",
]
