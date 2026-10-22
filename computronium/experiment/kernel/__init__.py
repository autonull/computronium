"""Kernel: Shared core for experiment execution.

This package contains the core infrastructure shared by all experiment
runners: composition, evaluation, search space, resource tracking, and
database persistence.
"""

from computronium.experiment.evidence.store import (
    DuplicateMeasurementError,
    RecordStore,
    RunInfo,
    StoreConfig,
    StoreError,
)
from computronium.experiment.kernel.compose import (
    ProposalComposeError,
    compose_cell_system,
    compose_configs,
)
from computronium.experiment.kernel.evaluate import (
    CellEvaluation,
    EvaluationError,
    TaskShape,
    cell_record,
    evaluate_cell,
    task_shape,
)
from computronium.experiment.kernel.resources import (
    CARBON_INTENSITY,
    GPU_POWER_WATTS,
    GPU_PRICING_USD_PER_HOUR,
    Budget,
    CampaignCostTracker,
    CostModel,
    CostTracker,
    ResourceUsage,
    SimpleCostModel,
    estimate_campaign_cost,
)
from computronium.experiment.kernel.search_space import (
    SearchSpace,
    VoidCache,
    generate_candidates,
    iter_candidates,
    search_space_from_spec,
)

__all__ = [
    "Budget",
    "CampaignCostTracker",
    "CARBON_INTENSITY",
    "CellEvaluation",
    "cell_record",
    "compose_cell_system",
    "compose_configs",
    "CostModel",
    "CostTracker",
    "DuplicateMeasurementError",
    "evaluate_cell",
    "estimate_campaign_cost",
    "EvaluationError",
    "generate_candidates",
    "GPU_POWER_WATTS",
    "GPU_PRICING_USD_PER_HOUR",
    "iter_candidates",
    "ProposalComposeError",
    "RecordStore",
    "ResourceUsage",
    "RunInfo",
    "search_space_from_spec",
    "SearchSpace",
    "SimpleCostModel",
    "StoreConfig",
    "StoreError",
    "task_shape",
    "TaskShape",
    "VoidCache",
]
