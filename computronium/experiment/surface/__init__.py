"""Experiment surface package — lazy loading.

This module uses lazy loading to avoid eager imports of heavy submodules.
Submodules and symbols are imported on first access via __getattr__.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from types import ModuleType

# Define all public symbols for static analysis and tab completion
__all__ = [
    "DEFAULT_Q14_ROUTES",
    "INDEX",
    "QUESTION_FIRST_STAGES",
    "RUN_PROFILES",
    "AlertDedup",
    "AxisImpact",
    "Claim",
    "ConformanceHarness",
    "ConformanceResult",
    "ConformanceStatus",
    "CurrencyLock",
    "ExportBundle",
    "FlagProjectionLock",
    "Limitation",
    "OperatorIntent",
    "OperatorIntentKind",
    "ReportGenerator",
    "RunController",
    "RunState",
    "RunSummary",
    "ServiceConfig",
    "ServiceLoop",
    "ServiceLoopConfig",
    "ServiceManager",
    "Significance",
    "SourceIndex",
    "TestEvidence",
    "WebhookConfig",
    "check_conformance",
    "cli",
    "codegen",
    "conformance",
    "create_operator_intent",
    "default_events_for",
    "evidence",
    "evidence_for",
    "execute_spec",
    "export_to_json",
    "export_to_parquet",
    "generate_all",
    "generate_axes_listing",
    "generate_capabilities_listing",
    "generate_cli_flag_tables",
    "generate_compatibility_matrix",
    "generate_conformance_report",
    "generate_conformance_stubs",
    "generate_constraints_listing",
    "generate_flag_projection_lock",
    "generate_json_schema_validators",
    "generate_objectives_listing",
    "generate_policies_listing",
    "generate_priors_listing",
    "generate_run_report",
    "generate_stages_listing",
    "load_currency_lock",
    "load_export_bundle",
    "load_flag_projection_lock",
    "main",
    "narrative_handoff_summary",
    "non_dominated",
    "operations",
    "poll_control_file",
    "profiles",
    "question_first",
    "report",
    "run_verifying_test",
    "save_currency_lock",
    "save_flag_projection_lock",
    "service",
    "submit_intent_to_run",
    "write_control_intent",
    "write_generated_docs",
]

# Lazy submodule cache
_lazy_submodules: dict[str, ModuleType] = {}

# Symbol to submodule mapping
_symbol_to_module: dict[str, str] = {
    # cli
    "main": "cli",
    "RUN_PROFILES": "cli",
    "execute_spec": "cli",
    # codegen
    "generate_all": "codegen",
    "generate_axes_listing": "codegen",
    "generate_capabilities_listing": "codegen",
    "generate_cli_flag_tables": "codegen",
    "generate_compatibility_matrix": "codegen",
    "generate_conformance_stubs": "codegen",
    "generate_constraints_listing": "codegen",
    "generate_json_schema_validators": "codegen",
    "generate_objectives_listing": "codegen",
    "generate_policies_listing": "codegen",
    "generate_priors_listing": "codegen",
    "generate_stages_listing": "codegen",
    "write_generated_docs": "codegen",
    # conformance
    "ConformanceHarness": "conformance",
    "ConformanceResult": "conformance",
    "ConformanceStatus": "conformance",
    "CurrencyLock": "conformance",
    "FlagProjectionLock": "conformance",
    "check_conformance": "conformance",
    "generate_conformance_report": "conformance",
    "generate_flag_projection_lock": "conformance",
    "load_currency_lock": "conformance",
    "load_flag_projection_lock": "conformance",
    "run_verifying_test": "conformance",
    "save_currency_lock": "conformance",
    "save_flag_projection_lock": "conformance",
    # evidence
    "INDEX": "evidence",
    "SourceIndex": "evidence",
    "evidence_for": "evidence",
    "TestEvidence": "evidence",
    # operations
    "DEFAULT_Q14_ROUTES": "operations",
    "AlertDedup": "operations",
    "OperatorIntent": "operations",
    "OperatorIntentKind": "operations",
    "RunController": "operations",
    "RunState": "operations",
    "ServiceConfig": "operations",
    "ServiceManager": "operations",
    "WebhookConfig": "operations",
    "create_operator_intent": "operations",
    "default_events_for": "operations",
    "submit_intent_to_run": "operations",
    # profiles
    "QUESTION_FIRST_STAGES": "profiles",
    "question_first": "profiles",
    # report
    "AxisImpact": "report",
    "Claim": "report",
    "ExportBundle": "report",
    "Limitation": "report",
    "ReportGenerator": "report",
    "RunSummary": "report",
    "Significance": "report",
    "export_to_json": "report",
    "export_to_parquet": "report",
    "generate_run_report": "report",
    "load_export_bundle": "report",
    "narrative_handoff_summary": "report",
    "non_dominated": "report",
    # service
    "ServiceLoop": "service",
    "ServiceLoopConfig": "service",
    "poll_control_file": "service",
    "write_control_intent": "service",
}


def _get_submodule(full_name: str) -> ModuleType:
    """Get or import a submodule by full name."""
    if full_name not in _lazy_submodules:
        _lazy_submodules[full_name] = __import__(full_name, fromlist=["*"])
    return _lazy_submodules[full_name]


def __getattr__(name: str) -> Any:
    """Lazy load submodules and symbols on first access."""
    # Submodules
    if name in {
        "cli",
        "codegen",
        "conformance",
        "evidence",
        "operations",
        "profiles",
        "report",
        "service",
    }:
        return _get_submodule(f"computronium.experiment.surface.{name}")

    # Symbols from specific submodules
    if name in _symbol_to_module:
        submodule_name = _symbol_to_module[name]
        submodule = _get_submodule(f"computronium.experiment.surface.{submodule_name}")
        return getattr(submodule, name)

    raise AttributeError(
        f"module 'computronium.experiment.surface' has no attribute '{name}'"
    )


def __dir__() -> list[str]:
    """Include lazy symbols in dir() for tab completion."""
    return __all__
