"""Experiment schema package — lazy loading.

This module uses lazy loading to avoid eager imports of heavy submodules.
Submodules and symbols are imported on first access via __getattr__.
"""

from __future__ import annotations

import sys
from types import ModuleType
from typing import Any

# Define all public symbols for static analysis and tab completion
__all__ = [
    # Submodules (lazy)
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
    # Axis symbols
    "AXES_REGISTRIES",
    "CREDIT_REGISTRY",
    "DYNAMICS_REGISTRY",
    "GEOMETRY_REGISTRY",
    "PLASTICITY_REGISTRY",
    "SUBSTRATE_REGISTRY",
    "UPDATE_REGISTRY",
    "AxisKind",
    "AxisPrimitive",
    "AxisSpec",
    "Domain",
    "HyperparameterSpec",
    "Scale",
    "StructuralAxis",
    "get_axis_spec",
    "get_registry",
    "is_available",
    "list_axis_specs",
    "register_axis_spec",
    # Coordinate symbols
    "Coordinate",
    "DataOrigin",
    "Provenance",
    "Schedule",
    # Harvest symbols
    "AXIS_KIND_ORDER",
    "CONFIG_FIELD_ALIASES",
    "ActiveSpace",
    "HarvestedSchema",
    "InactiveHyperparameterError",
    "UnresolvedHyperparameterError",
    "config_field_name",
    "get_hyperparameter_names",
    "get_hyperparameter_spec",
    "harvest_schema",
    "harvest_weights",
    "load_axis_config",
    # Metrics symbols
    "HISTORY_METRICS",
    "MEASURED_METRICS",
    "MEASURED_OBJECTIVES",
    "ObjectiveResolutionError",
    "UnknownObjectiveError",
    "UnmeasuredObjectiveError",
    "measured_objectives",
    "objective_metric",
    "objective_name",
    "objective_values",
    "optimizes",
    # Record symbols
    "FailureCause",
    "GateVerdict",
    "Maturity",
    "Record",
    "ReproducibilityClass",
    "Severity",
    "Status",
    # Registries symbols
    "ASSESSMENT_PROCEDURE_VERSION",
    "CAPABILITIES_REGISTRY",
    "CapabilityKind",
    "CapabilitySpec",
    "CapabilityStatus",
    "CONSTRAINTS_REGISTRY",
    "ConstraintKind",
    "ConstraintSpec",
    "DEFAULT_CELL_SECONDS",
    "FIXED_RUN_COST_SECONDS",
    "MEASURED_CELL_SECONDS",
    "MEASURED_CELL_SECONDS_REGIME",
    "MEASURED_PARALLEL_SPEEDUP",
    "OBJECTIVES_REGISTRY",
    "ObjectiveSpec",
    "PARAM_BUDGET_TOLERANCE",
    "POLICIES_REGISTRY",
    "PolicyKind",
    "PolicySpec",
    "PRIORS",
    "PRIORS_REGISTRY",
    "PriorSpec",
    "ProofKind",
    "RATE_PARAMETERS",
    "REPLAY_METRIC_TOLERANCE",
    "STAGES_REGISTRY",
    "StageId",
    "StageSpec",
    "cell_price_seconds",
    "procedure_version_key",
    "prior_value",
    "register_capability",
    "register_card_factor",
    "register_constraint",
    "register_objective",
    "register_policy",
    "register_prior",
    "register_stage",
    "validate_rate_value",
    # Registry symbols
    "Registry",
    "RegistryDiff",
    # RunSpec symbols
    "AxisSelection",
    "Fidelity",
    "MEASURED_BATCH_LIMIT",
    "MEASURED_PARAM_BUDGET",
    "RUN_SPEC_VERSION",
    "RunSpec",
    # SeedRegistries symbols
    "PRIORS",
    "seed_all_registries",
    # Versioning symbols
    "SCHEMA_REGISTRY",
    "current_schema_version",
    "schema_version",
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
    "harvest_weights": "harvest",
    "load_axis_config": "harvest",
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
    "PRIORS": "registries",
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
    "schema_version": "versioning",
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
    if name in ("axis", "coordinate", "harvest", "metrics", "record", "registries", "registry", "run_spec", "seed_registries", "versioning"):
        return _get_submodule(f"computronium.experiment.schema.{name}")

    # Symbols from specific submodules
    if name in _symbol_to_module:
        submodule_name = _symbol_to_module[name]
        submodule = _get_submodule(f"computronium.experiment.schema.{submodule_name}")
        # Seed registries on first access of axis symbols
        if submodule_name == "axis":
            _ensure_registries_seeded()
        return getattr(submodule, name)

    raise AttributeError(f"module 'computronium.experiment.schema' has no attribute '{name}'")


def __dir__() -> list[str]:
    """Include lazy symbols in dir() for tab completion."""
    return __all__