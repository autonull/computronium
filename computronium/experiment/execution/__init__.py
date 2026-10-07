"""Experiment execution package — lazy loading.

This module uses lazy loading to avoid eager imports of heavy submodules.
Submodules and symbols are imported on first access via __getattr__.
"""

from __future__ import annotations

from types import ModuleType
from typing import Any

# Define all public symbols for static analysis and tab completion
__all__ = [
    # Submodules (lazy)
    "allocator",
    "backends",
    "budget",
    "compose",
    "decision",
    "optuna_adapter",
    "pipeline",
    "policy",
    "pricing",
    "replay",
    "search_space",
    "settle_operator",
    "stage",
    "stages_impl",
    "sysctx",
    # allocator
    "Abandonment",
    "AllocationPolicy",
    "AllocationState",
    "EvidenceDrivenAllocator",
    "Promotion",
    "PromotionCandidate",
    # backends
    "EvaluationResult",
    "EvaluationTask",
    "ExecutionBackend",
    "Failure",
    "LocalBackend",
    "MultiprocessBackend",
    "Success",
    # budget
    "Budget",
    "CostModel",
    "SimpleCostModel",
    # compose
    "GRID_CREDITS",
    "GRID_DYNAMICS",
    "GRID_UPDATES",
    "ComposedCell",
    "ProposalComposeError",
    "_fit_geometry",
    "build_geometry_config",
    "compose_cell_system",
    "compose_configs",
    "geometry_param_count",
    "_GEOMETRY_ALIASES",
    # contrast_design
    "ContrastAssignment",
    "ContrastDesign",
    "ContrastDesignKind",
    "Factor",
    "create_contrast_design",
    "create_fractional_factorial_design",
    "create_full_factorial_design",
    "create_ofat_design",
    "create_plackett_burman_design",
    # decision
    "Decision",
    "Replication",
    "RoundController",
    "complete_run",
    "continue_round",
    "create_decision",
    "pause_run",
    "stop_run",
    # evaluate
    "CellEvaluation",
    "TaskShape",
    "cell_record",
    "compute_energy_metrics",
    "compute_stability_metrics",
    "evaluate_cell",
    "history_metrics",
    "task_shape",
    # optuna_adapter
    "OptunaDistributionAdapter",
    # pipeline
    "PipelineConfig",
    "PipelineRunner",
    "PipelineState",
    # policy
    "POLICY_CATALOG",
    "EvolutionPolicy",
    "ModelBasedPolicy",
    "Policy",
    "ProposalContext",
    "RecordSource",
    "RoundRobinGridPolicy",
    "StrategyProgressionPolicy",
    "StratifiedRandomPolicy",
    "SynthesisPolicy",
    "TrainerDrivenPolicy",
    "UniformRandomPolicy",
    "create_policy",
    "policy_context",
    "resolve_objectives",
    # pricing
    "PricePlan",
    "price_plan",
    # replay
    "compute_run_replay_hash",
    # search_space
    "SearchSpace",
    "ShapeResolver",
    "declared_cell_count",
    "generate_candidates",
    "iter_candidates",
    "narrow_domain",
    "search_space_from_spec",
    # settle_operator
    "hidden_stack_operator",
    "layer_weight_shapes",
    "settle_step_operator",
    # stage
    "S1_FRAME",
    "S2_SPACE",
    "S3_SCHEDULE",
    "S4_GATE",
    "S5_COMPOSE",
    "S6_TRAIN",
    "S7_MEASURE",
    "S8_RECORD",
    "S9_ATTRIBUTE",
    "S10_DECIDE",
    "S11_REPORT",
    "STAGE_REGISTRY",
    "STAGE_SPECS",
    "Fragment",
    "Proposal",
    "Stage",
    "StageContext",
    "StageGate",
    "StageId",
    "StageSpec",
    "StageTransition",
    "get_next_stage",
    "get_previous_stage",
    "get_stage_spec",
    # stages_impl
    "STAGE_IMPLEMENTATIONS",
    "AttributeStage",
    "ComposeStage",
    "DecideStage",
    "FrameStage",
    "GateStage",
    "MeasureStage",
    "RecordStage",
    "ReportStage",
    "ScheduleStage",
    "SpaceStage",
    "TrainStage",
    "get_stage_implementation",
    "_allocate_origins",
    "_design_factors",
    "_is_assignment",
    "_match_design",
    "_origins_for_design",
    # sysctx
    "EnvironmentSnapshot",
    "SystemContext",
    "capture_environment_snapshot",
]

# Lazy submodule cache
_lazy_submodules: dict[str, ModuleType] = {}

# Symbol to submodule mapping
_symbol_to_module: dict[str, str] = {
    # allocator
    "Abandonment": "allocator",
    "AllocationPolicy": "allocator",
    "AllocationState": "allocator",
    "EvidenceDrivenAllocator": "allocator",
    "Promotion": "allocator",
    "PromotionCandidate": "allocator",
    # backends
    "EvaluationResult": "backends",
    "EvaluationTask": "backends",
    "ExecutionBackend": "backends",
    "Failure": "backends",
    "LocalBackend": "backends",
    "MultiprocessBackend": "backends",
    "Success": "backends",
    # budget
    "Budget": "budget",
    "CostModel": "budget",
    "SimpleCostModel": "budget",
    # compose
    "GRID_CREDITS": "compose",
    "GRID_DYNAMICS": "compose",
    "GRID_UPDATES": "compose",
    "ComposedCell": "compose",
    "ProposalComposeError": "compose",
    "_fit_geometry": "compose",
    "build_geometry_config": "compose",
    "compose_cell_system": "compose",
    "compose_configs": "compose",
    "geometry_param_count": "compose",
    "_GEOMETRY_ALIASES": "compose",
    # contrast_design
    "ContrastAssignment": "contrast_design",
    "ContrastDesign": "contrast_design",
    "ContrastDesignKind": "contrast_design",
    "Factor": "contrast_design",
    "create_contrast_design": "contrast_design",
    "create_fractional_factorial_design": "contrast_design",
    "create_full_factorial_design": "contrast_design",
    "create_ofat_design": "contrast_design",
    "create_plackett_burman_design": "contrast_design",
    # decision
    "Decision": "decision",
    "Replication": "decision",
    "RoundController": "decision",
    "complete_run": "decision",
    "continue_round": "decision",
    "create_decision": "decision",
    "pause_run": "decision",
    "stop_run": "decision",
    # evaluate
    "CellEvaluation": "evaluate",
    "TaskShape": "evaluate",
    "cell_record": "evaluate",
    "compute_energy_metrics": "evaluate",
    "compute_stability_metrics": "evaluate",
    "evaluate_cell": "evaluate",
    "history_metrics": "evaluate",
    "task_shape": "evaluate",
    # optuna_adapter
    "OptunaDistributionAdapter": "optuna_adapter",
    # pipeline
    "PipelineConfig": "pipeline",
    "PipelineRunner": "pipeline",
    "PipelineState": "pipeline",
    # policy
    "POLICY_CATALOG": "policy",
    "EvolutionPolicy": "policy",
    "ModelBasedPolicy": "policy",
    "Policy": "policy",
    "ProposalContext": "policy",
    "RecordSource": "policy",
    "RoundRobinGridPolicy": "policy",
    "StrategyProgressionPolicy": "policy",
    "StratifiedRandomPolicy": "policy",
    "SynthesisPolicy": "policy",
    "TrainerDrivenPolicy": "policy",
    "UniformRandomPolicy": "policy",
    "create_policy": "policy",
    "policy_context": "policy",
    "resolve_objectives": "policy",
    # pricing
    "PricePlan": "pricing",
    "price_plan": "pricing",
    # replay
    "compute_run_replay_hash": "replay",
    # search_space
    "SearchSpace": "search_space",
    "ShapeResolver": "search_space",
    "declared_cell_count": "search_space",
    "generate_candidates": "search_space",
    "iter_candidates": "search_space",
    "narrow_domain": "search_space",
    "search_space_from_spec": "search_space",
    # settle_operator
    "hidden_stack_operator": "settle_operator",
    "layer_weight_shapes": "settle_operator",
    "settle_step_operator": "settle_operator",
    # stage
    "S1_FRAME": "stage",
    "S2_SPACE": "stage",
    "S3_SCHEDULE": "stage",
    "S4_GATE": "stage",
    "S5_COMPOSE": "stage",
    "S6_TRAIN": "stage",
    "S7_MEASURE": "stage",
    "S8_RECORD": "stage",
    "S9_ATTRIBUTE": "stage",
    "S10_DECIDE": "stage",
    "S11_REPORT": "stage",
    "STAGE_REGISTRY": "stage",
    "STAGE_SPECS": "stage",
    "Fragment": "stage",
    "Proposal": "stage",
    "Stage": "stage",
    "StageContext": "stage",
    "StageGate": "stage",
    "StageId": "stage",
    "StageSpec": "stage",
    "StageTransition": "stage",
    "get_next_stage": "stage",
    "get_previous_stage": "stage",
    "get_stage_spec": "stage",
    # stages_impl
    "STAGE_IMPLEMENTATIONS": "stages_impl",
    "AttributeStage": "stages_impl",
    "ComposeStage": "stages_impl",
    "DecideStage": "stages_impl",
    "FrameStage": "stages_impl",
    "GateStage": "stages_impl",
    "MeasureStage": "stages_impl",
    "RecordStage": "stages_impl",
    "ReportStage": "stages_impl",
    "ScheduleStage": "stages_impl",
    "SpaceStage": "stages_impl",
    "TrainStage": "stages_impl",
    "get_stage_implementation": "stages_impl",
    "_allocate_origins": "stages_impl",
    "_design_factors": "stages_impl",
    "_is_assignment": "stages_impl",
    "_match_design": "stages_impl",
    "_origins_for_design": "stages_impl",
    # sysctx
    "EnvironmentSnapshot": "sysctx",
    "SystemContext": "sysctx",
    "capture_environment_snapshot": "sysctx",
}


def _get_submodule(full_name: str) -> ModuleType:
    """Get or import a submodule by full name."""
    if full_name not in _lazy_submodules:
        _lazy_submodules[full_name] = __import__(full_name, fromlist=["*"])
    return _lazy_submodules[full_name]


def __getattr__(name: str) -> Any:
    """Lazy load submodules and symbols on first access."""
    # Submodules
    if name in (
        "allocator",
        "backends",
        "budget",
        "compose",
        "contrast_design",
        "decision",
        "evaluate",
        "optuna_adapter",
        "pipeline",
        "policy",
        "pricing",
        "replay",
        "search_space",
        "settle_operator",
        "stage",
        "stages_impl",
        "sysctx",
    ):
        return _get_submodule(f"computronium.experiment.execution.{name}")

    # Symbols from specific submodules
    if name in _symbol_to_module:
        submodule_name = _symbol_to_module[name]
        submodule = _get_submodule(f"computronium.experiment.execution.{submodule_name}")
        return getattr(submodule, name)

    raise AttributeError(f"module 'computronium.experiment.execution' has no attribute '{name}'")


def __dir__() -> list[str]:
    """Include lazy symbols in dir() for tab completion."""
    return __all__
