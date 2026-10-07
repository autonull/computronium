"""Experiment evidence package — lazy loading.

This module uses lazy loading to avoid eager imports of heavy submodules.
Submodules and symbols are imported on first access via __getattr__.
"""

from __future__ import annotations

from types import ModuleType
from typing import Any

# Define all public symbols for static analysis and tab completion
__all__ = [
    # Submodules (lazy)
    "artifacts",
    "claims",
    "failure",
    "limitations",
    "procedures",
    "protocol",
    "significance",
    "statistics",
    "status",
    "store",
    # artifacts
    "Artifact",
    "ArtifactInput",
    "ArtifactRole",
    "ArtifactStorage",
    "ArtifactStore",
    "ExternalStore",
    "FilesystemExternalStore",
    # claims
    "DEFAULT_MIN_SEEDS",
    "Alert",
    "AxisImpact",
    "CellMetrics",
    "Claim",
    "alert_on_constraint_violation",
    "alert_on_divergence",
    "alert_on_resource_exhaustion",
    "alert_on_stagnation",
    "beats_baseline",
    "cell_metrics_by_axis_value",
    "check_all_alerts",
    "check_leakage",
    "claim_eligible",
    "claim_eligible_by_achieved_seeds",
    "claim_eligible_strict",
    "compare_matched_cost",
    "derive_claims",
    "evaluation_data_allowed",
    "filter_by_data_origin",
    "filter_by_maturity",
    "filter_claim_eligible",
    "filter_promoted",
    "generalizes",
    "group_by_cell_key",
    "group_by_replication_key",
    "is_calibration_data",
    "is_exploration_data",
    "is_policy_selected_data",
    "is_test_data",
    "pairing_key",
    "replication_key",
    "strongest_axis",
    # failure
    "FailureCluster",
    "FailureEvent",
    "FailurePattern",
    "FixLinkage",
    "FixLinkageStore",
    "Reproducer",
    "analyze_store_failures",
    "cluster_failures",
    "detect_failure_patterns",
    "emit_reproducer",
    "save_reproducer",
    # limitations
    "Limitation",
    "LimitationKind",
    "derive_limitations",
    "replication_keys_of",
    # procedures
    "ASSESSMENT_PROCEDURES",
    "get_assessment_procedure",
    "list_assessment_procedures",
    "register_assessment_procedure",
    # protocol
    "SYNTHETIC_FIXTURE",
    "ComparisonError",
    "ComparisonGuard",
    "CostBudget",
    "CostBudgetKind",
    "EffectSizeResult",
    "SyntheticGroundTruth",
    "cohens_d_paired",
    "compute_effect_size",
    "create_synthetic_fixture",
    "wilcoxon_paired",
    # significance
    "DEFAULT_ALPHA",
    "MIN_SHARED_CELLS",
    "SIGNIFICANCE_TEST",
    "Resampling",
    "Significance",
    "paired_significance",
    # statistics
    "bootstrap_percentile_ci",
    "cohens_dz",
    "permutation_test_p",
    # status
    "AssessmentProcedure",
    "AssessmentProcedureKind",
    "Assessments",
    "DerivedClaims",
    "Observations",
    "StatusBundle",
    "StatusLegacy",
    "_canonical_json",
    "build_assessments_from_legacy",
    "build_legacy_from_assessments",
    # store
    "DuplicateMeasurementError",
    "ProvenanceModel",
    "RecordInputModel",
    "RecordOutputModel",
    "RecordStore",
    "RunInfo",
    "ScheduleModel",
    "StatusModel",
    "StoreConfig",
    "StoreError",
    "TableName",
    "TableSlice",
    "UnsupportedSchemaVersionError",
    "format_replication_key",
    "validate_record_input",
    "validate_record_output",
]

# Lazy submodule cache
_lazy_submodules: dict[str, ModuleType] = {}

# Symbol to submodule mapping
_symbol_to_module: dict[str, str] = {
    # artifacts
    "Artifact": "artifacts",
    "ArtifactInput": "artifacts",
    "ArtifactRole": "artifacts",
    "ArtifactStorage": "artifacts",
    "ArtifactStore": "artifacts",
    "ExternalStore": "artifacts",
    "FilesystemExternalStore": "artifacts",
    # claims
    "DEFAULT_MIN_SEEDS": "claims",
    "Alert": "claims",
    "AxisImpact": "claims",
    "CellMetrics": "claims",
    "Claim": "claims",
    "alert_on_constraint_violation": "claims",
    "alert_on_divergence": "claims",
    "alert_on_resource_exhaustion": "claims",
    "alert_on_stagnation": "claims",
    "beats_baseline": "claims",
    "cell_metrics_by_axis_value": "claims",
    "check_all_alerts": "claims",
    "check_leakage": "claims",
    "claim_eligible": "claims",
    "claim_eligible_by_achieved_seeds": "claims",
    "claim_eligible_strict": "claims",
    "compare_matched_cost": "claims",
    "derive_claims": "claims",
    "evaluation_data_allowed": "claims",
    "filter_by_data_origin": "claims",
    "filter_by_maturity": "claims",
    "filter_claim_eligible": "claims",
    "filter_promoted": "claims",
    "generalizes": "claims",
    "group_by_cell_key": "claims",
    "group_by_replication_key": "claims",
    "is_calibration_data": "claims",
    "is_exploration_data": "claims",
    "is_policy_selected_data": "claims",
    "is_test_data": "claims",
    "pairing_key": "claims",
    "replication_key": "claims",
    "strongest_axis": "claims",
    # failure
    "FailureCluster": "failure",
    "FailureEvent": "failure",
    "FailurePattern": "failure",
    "FixLinkage": "failure",
    "FixLinkageStore": "failure",
    "Reproducer": "failure",
    "analyze_store_failures": "failure",
    "cluster_failures": "failure",
    "detect_failure_patterns": "failure",
    "emit_reproducer": "failure",
    "save_reproducer": "failure",
    # limitations
    "Limitation": "limitations",
    "LimitationKind": "limitations",
    "derive_limitations": "limitations",
    "replication_keys_of": "limitations",
    # procedures
    "ASSESSMENT_PROCEDURES": "procedures",
    "get_assessment_procedure": "procedures",
    "list_assessment_procedures": "procedures",
    "register_assessment_procedure": "procedures",
    # protocol
    "SYNTHETIC_FIXTURE": "protocol",
    "ComparisonError": "protocol",
    "ComparisonGuard": "protocol",
    "CostBudget": "protocol",
    "CostBudgetKind": "protocol",
    "EffectSizeResult": "protocol",
    "SyntheticGroundTruth": "protocol",
    "cohens_d_paired": "protocol",
    "compute_effect_size": "protocol",
    "create_synthetic_fixture": "protocol",
    "wilcoxon_paired": "protocol",
    # significance
    "DEFAULT_ALPHA": "significance",
    "MIN_SHARED_CELLS": "significance",
    "SIGNIFICANCE_TEST": "significance",
    "Resampling": "significance",
    "Significance": "significance",
    "paired_significance": "significance",
    # statistics
    "bootstrap_percentile_ci": "statistics",
    "cohens_dz": "statistics",
    "permutation_test_p": "statistics",
    # status
    "AssessmentProcedure": "status",
    "AssessmentProcedureKind": "status",
    "Assessments": "status",
    "DerivedClaims": "status",
    "Observations": "status",
    "StatusBundle": "status",
    "StatusLegacy": "status",
    "_canonical_json": "status",
    "build_assessments_from_legacy": "status",
    "build_legacy_from_assessments": "status",
    # store
    "DuplicateMeasurementError": "store",
    "ProvenanceModel": "store",
    "RecordInputModel": "store",
    "RecordOutputModel": "store",
    "RecordStore": "store",
    "RunInfo": "store",
    "ScheduleModel": "store",
    "StatusModel": "store",
    "StoreConfig": "store",
    "StoreError": "store",
    "TableName": "store",
    "TableSlice": "store",
    "UnsupportedSchemaVersionError": "store",
    "format_replication_key": "store",
    "validate_record_input": "store",
    "validate_record_output": "store",
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
        "artifacts",
        "claims",
        "failure",
        "limitations",
        "procedures",
        "protocol",
        "significance",
        "statistics",
        "status",
        "store",
    ):
        return _get_submodule(f"computronium.experiment.evidence.{name}")

    # Symbols from specific submodules
    if name in _symbol_to_module:
        submodule_name = _symbol_to_module[name]
        submodule = _get_submodule(f"computronium.experiment.evidence.{submodule_name}")
        return getattr(submodule, name)

    raise AttributeError(f"module 'computronium.experiment.evidence' has no attribute '{name}'")


def __dir__() -> list[str]:
    """Include lazy symbols in dir() for tab completion."""
    return __all__