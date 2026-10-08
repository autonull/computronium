"""Experiment schema package — lazy loading.

This module uses lazy loading to avoid eager imports of heavy submodules.
Submodules and symbols are imported on first access via __getattr__.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from types import ModuleType

# Define all public symbols for static analysis and tab completion
__all__ = [
    "ALL_REGISTRIES",
    "ASSESSMENT_PROCEDURE_VERSION",
    "AXES_REGISTRIES",
    "AXIS_KIND_ORDER",
    "CAPABILITIES_REGISTRY",
    "CONFIG_FIELD_ALIASES",
    "CONSTRAINTS_REGISTRY",
    "CREDIT_REGISTRY",
    "DEFAULT_CELL_SECONDS",
    "DYNAMICS_REGISTRY",
    "FIXED_RUN_COST_SECONDS",
    "GEOMETRY_REGISTRY",
    "HISTORY_METRICS",
    "MEASURED_BATCH_LIMIT",
    "MEASURED_CELL_SECONDS",
    "MEASURED_CELL_SECONDS_REGIME",
    "MEASURED_METRICS",
    "MEASURED_OBJECTIVES",
    "MEASURED_PARALLEL_SPEEDUP",
    "MEASURED_PARAM_BUDGET",
    "NO_DEFAULT",
    "OBJECTIVES_REGISTRY",
    "PARAM_BUDGET_TOLERANCE",
    "PLASTICITY_REGISTRY",
    "POLICIES_REGISTRY",
    "PRIORS",
    "PRIORS_REGISTRY",
    "RATE_PARAMETERS",
    "REPLAY_METRIC_TOLERANCE",
    "RUN_SPEC_VERSION",
    "SCHEMA_REGISTRY",
    "STAGES_REGISTRY",
    "SUBSTRATE_REGISTRY",
    "UPDATE_REGISTRY",
    "ActiveSpace",
    "AxisKind",
    "AxisPrimitive",
    "AxisSelection",
    "AxisSpec",
    "CapabilityKind",
    "CapabilitySpec",
    "CapabilityStatus",
    "ConstraintKind",
    "ConstraintSpec",
    "Coordinate",
    "DataOrigin",
    "Domain",
    "FailureCause",
    "Fidelity",
    "GateVerdict",
    "HarvestedSchema",
    "HyperparameterSpec",
    "InactiveHyperparameterError",
    "Maturity",
    "ObjectiveResolutionError",
    "ObjectiveSpec",
    "PolicyKind",
    "PolicySpec",
    "PriorSpec",
    "ProofKind",
    "Provenance",
    "Record",
    "Registry",
    "RegistryDiff",
    "ReproducibilityClass",
    "RunSpec",
    "Scale",
    "Schedule",
    "Severity",
    "StageId",
    "StageSpec",
    "Status",
    "StructuralAxis",
    "TransferMode",
    "UnknownObjectiveError",
    "UnmeasuredObjectiveError",
    "UnresolvedHyperparameterError",
    "_config_default",
    "axis",
    "cell_price_seconds",
    "config_field_name",
    "coordinate",
    "current_schema_version",
    "get_axis_spec",
    "get_hyperparameter_names",
    "get_hyperparameter_spec",
    "get_registry",
    "harvest",
    "harvest_schema",
    "is_available",
    "list_axis_specs",
    "load_axis_config",
    "measured_objectives",
    "metrics",
    "objective_metric",
    "objective_name",
    "objective_values",
    "optimizes",
    "prior_value",
    "procedure_version_key",
    "record",
    "register_axis_spec",
    "register_capability",
    "register_card_factor",
    "register_constraint",
    "register_objective",
    "register_policy",
    "register_prior",
    "register_stage",
    "registries",
    "registry",
    "run_spec",
    "seed_all_registries",
    "seed_registries",
    "validate_rate_value",
    "versioning",
]

# Lazy submodule cache
_lazy_submodules: dict[str, ModuleType] = {}

# Symbol to submodule mapping
_symbol_to_module: dict[str, str] = {
    # axis
    "AXES_REGISTRIES": "axis",
    "CREDIT_REGISTRY": "axis",
    "DYNAMICS_REGISTRY": "axis",
    "GEOMETRY_REGISTRY": "axis",
    "PLASTICITY_REGISTRY": "axis",
    "SUBSTRATE_REGISTRY": "axis",
    "UPDATE_REGISTRY": "axis",
    "AxisKind": "axis",
    "AxisPrimitive": "axis",
    "AxisSpec": "axis",
    "Domain": "axis",
    "HyperparameterSpec": "axis",
    "NO_DEFAULT": "axis",
    "Scale": "axis",
    "StructuralAxis": "axis",
    "get_axis_spec": "axis",
    "get_registry": "axis",
    "is_available": "axis",
    "list_axis_specs": "axis",
    "register_axis_spec": "axis",
    # coordinate
    "Coordinate": "coordinate",
    "DataOrigin": "coordinate",
    "Provenance": "coordinate",
    "Schedule": "coordinate",
    "TransferMode": "coordinate",
    # harvest
    "AXIS_KIND_ORDER": "harvest",
    "CONFIG_FIELD_ALIASES": "harvest",
    "ActiveSpace": "harvest",
    "HarvestedSchema": "harvest",
    "InactiveHyperparameterError": "harvest",
    "UnresolvedHyperparameterError": "harvest",
    "config_field_name": "harvest",
    "get_hyperparameter_names": "harvest",
    "get_hyperparameter_spec": "harvest",
    "harvest_schema": "harvest",
    "load_axis_config": "harvest",
    "_config_default": "harvest",
    # metrics
    "HISTORY_METRICS": "metrics",
    "MEASURED_METRICS": "metrics",
    "MEASURED_OBJECTIVES": "metrics",
    "ObjectiveResolutionError": "metrics",
    "UnknownObjectiveError": "metrics",
    "UnmeasuredObjectiveError": "metrics",
    "measured_objectives": "metrics",
    "objective_metric": "metrics",
    "objective_name": "metrics",
    "objective_values": "metrics",
    "optimizes": "metrics",
    # record
    "FailureCause": "record",
    "GateVerdict": "record",
    "Maturity": "record",
    "Record": "record",
    "ReproducibilityClass": "record",
    "Severity": "record",
    "Status": "record",
    # registries
    "ALL_REGISTRIES": "registries",
    "ASSESSMENT_PROCEDURE_VERSION": "registries",
    "CAPABILITIES_REGISTRY": "registries",
    "CapabilityKind": "registries",
    "CapabilitySpec": "registries",
    "CapabilityStatus": "registries",
    "CONSTRAINTS_REGISTRY": "registries",
    "ConstraintKind": "registries",
    "ConstraintSpec": "registries",
    "DEFAULT_CELL_SECONDS": "registries",
    "FIXED_RUN_COST_SECONDS": "registries",
    "MEASURED_CELL_SECONDS": "registries",
    "MEASURED_CELL_SECONDS_REGIME": "registries",
    "MEASURED_PARALLEL_SPEEDUP": "registries",
    "OBJECTIVES_REGISTRY": "registries",
    "ObjectiveSpec": "registries",
    "PARAM_BUDGET_TOLERANCE": "registries",
    "POLICIES_REGISTRY": "registries",
    "PolicyKind": "registries",
    "PolicySpec": "registries",
    "PRIORS_REGISTRY": "registries",
    "PriorSpec": "registries",
    "ProofKind": "registries",
    "RATE_PARAMETERS": "registries",
    "REPLAY_METRIC_TOLERANCE": "registries",
    "STAGES_REGISTRY": "registries",
    "StageId": "registries",
    "StageSpec": "registries",
    "cell_price_seconds": "registries",
    "procedure_version_key": "registries",
    "prior_value": "registries",
    "register_capability": "registries",
    "register_card_factor": "registries",
    "register_constraint": "registries",
    "register_objective": "registries",
    "register_policy": "registries",
    "register_prior": "registries",
    "register_stage": "registries",
    "validate_rate_value": "registries",
    # registry
    "Registry": "registry",
    "RegistryDiff": "registry",
    # run_spec
    "AxisSelection": "run_spec",
    "Fidelity": "run_spec",
    "MEASURED_BATCH_LIMIT": "run_spec",
    "MEASURED_PARAM_BUDGET": "run_spec",
    "RUN_SPEC_VERSION": "run_spec",
    "RunSpec": "run_spec",
    # seed_registries
    "PRIORS": "seed_registries",
    "seed_all_registries": "seed_registries",
    # versioning
    "SCHEMA_REGISTRY": "versioning",
    "current_schema_version": "versioning",
}


def _get_submodule(full_name: str) -> ModuleType:
    """Get or import a submodule by full name."""
    if full_name not in _lazy_submodules:
        _lazy_submodules[full_name] = __import__(full_name, fromlist=["*"])
    return _lazy_submodules[full_name]


# Track if registries have been seeded (mutable container to avoid global statement)
_registries_seeded: list[bool] = [False]


def _ensure_registries_seeded() -> None:
    """Ensure registries are seeded on first access of axis symbols."""
    if not _registries_seeded[0]:
        # Import and call seed_all_registries
        seed_module = _get_submodule("computronium.experiment.schema.seed_registries")
        seed_module.seed_all_registries()
        _registries_seeded[0] = True


def __getattr__(name: str) -> Any:
    """Lazy load submodules and symbols on first access."""
    # Submodules
    if name in {
        "axis",
        "coordinate",
        "harvest",
        "metrics",
        "record",
        "registries",
        "registry",
        "run_spec",
        "seed_registries",
        "versioning",
    }:
        return _get_submodule(f"computronium.experiment.schema.{name}")

    # Ensure registries are seeded before accessing axis symbols
    _ensure_registries_seeded()

    # Symbols from specific submodules
    if name in _symbol_to_module:
        submodule_name = _symbol_to_module[name]
        submodule = _get_submodule(f"computronium.experiment.schema.{submodule_name}")
        return getattr(submodule, name)

    raise AttributeError(
        f"module 'computronium.experiment.schema' has no attribute '{name}'"
    )


def __dir__() -> list[str]:
    """Include lazy symbols in dir() for tab completion."""
    return __all__
