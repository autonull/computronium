"""Kernel: Shared core for experiment execution.

This package contains the core infrastructure shared by all experiment
runners: composition, evaluation, search space, resource tracking, and
database persistence.
"""

from computronium.experiment.kernel.compose import (
    compose_cell_system,
    compose_configs,
    ProposalComposeError,
)
from computronium.experiment.kernel.evaluate import (
    CellEvaluation,
    evaluate_cell,
    task_shape,
    TaskShape,
    EvaluationError,
    cell_record,
)
from computronium.experiment.kernel.resources import (
    Budget,
    CostModel,
    SimpleCostModel,
    ResourceUsage,
    CostTracker,
    CampaignCostTracker,
    estimate_campaign_cost,
    CARBON_INTENSITY,
    GPU_POWER_WATTS,
    GPU_PRICING_USD_PER_HOUR,
)
from computronium.experiment.kernel.search_space import (
    SearchSpace,
    VoidCache,
    iter_candidates,
    search_space_from_spec,
    generate_candidates,
)
from computronium.experiment.evidence.store import (
    RecordStore,
    StoreConfig,
    RunInfo,
    DuplicateMeasurementError,
    StoreError,
)

__all__ = [
    # Composition
    "compose_cell_system",
    "compose_configs",
    "ProposalComposeError",
    # Evaluation
    "CellEvaluation",
    "evaluate_cell",
    "task_shape",
    "TaskShape",
    "EvaluationError",
    "cell_record",
    # Resources
    "Budget",
    "CostModel",
    "SimpleCostModel",
    "ResourceUsage",
    "CostTracker",
    "CampaignCostTracker",
    "estimate_campaign_cost",
    "CARBON_INTENSITY",
    "GPU_POWER_WATTS",
    "GPU_PRICING_USD_PER_HOUR",
    # Search space
    "SearchSpace",
    "VoidCache",
    "iter_candidates",
    "search_space_from_spec",
    # Database (DuckDB-backed)
    "RecordStore",
    "StoreConfig",
    "RunInfo",
    "DuplicateMeasurementError",
    "StoreError",
]
