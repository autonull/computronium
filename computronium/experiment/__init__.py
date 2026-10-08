"""Computronium Experiment Kernel — unified experiment orchestration.

This module uses lazy loading to avoid eager imports of heavy submodules.
Submodules and symbols are imported on first access via __getattr__.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from types import ModuleType

# Define all public symbols for static analysis and tab completion
__all__ = [
    "AXES_REGISTRIES",
    "CREDIT_REGISTRY",
    "DYNAMICS_REGISTRY",
    "GEOMETRY_REGISTRY",
    "PLASTICITY_REGISTRY",
    "RUN_SPEC_VERSION",
    "SUBSTRATE_REGISTRY",
    "UPDATE_REGISTRY",
    "AxisKind",
    "AxisPrimitive",
    "AxisSelection",
    "AxisSpec",
    "Domain",
    "FailureCause",
    "Fidelity",
    "GateVerdict",
    "HyperparameterSpec",
    "Maturity",
    "Record",
    "Registry",
    "RegistryDiff",
    "ReproducibilityClass",
    "RunSpec",
    "RunSpecBuilder",
    "Scale",
    "Severity",
    "Status",
    "StructuralAxis",
    "evidence",
    "execution",
    "get_axis_spec",
    "get_registry",
    "is_available",
    "list_axis_specs",
    "register_axis_spec",
    "schema",
    "surface",
]

# Lazy submodule cache - maps submodule name to module
_lazy_submodules: dict[str, ModuleType] = {}

# Symbol to submodule mapping
_symbol_to_module: dict[str, str] = {
    # schema.axis
    "AXES_REGISTRIES": "schema.axis",
    "CREDIT_REGISTRY": "schema.axis",
    "DYNAMICS_REGISTRY": "schema.axis",
    "GEOMETRY_REGISTRY": "schema.axis",
    "PLASTICITY_REGISTRY": "schema.axis",
    "SUBSTRATE_REGISTRY": "schema.axis",
    "UPDATE_REGISTRY": "schema.axis",
    "AxisKind": "schema.axis",
    "AxisPrimitive": "schema.axis",
    "AxisSpec": "schema.axis",
    "Domain": "schema.axis",
    "HyperparameterSpec": "schema.axis",
    "Scale": "schema.axis",
    "StructuralAxis": "schema.axis",
    "get_axis_spec": "schema.axis",
    "get_registry": "schema.axis",
    "is_available": "schema.axis",
    "list_axis_specs": "schema.axis",
    "register_axis_spec": "schema.axis",
    # schema.record
    "FailureCause": "schema.record",
    "GateVerdict": "schema.record",
    "Maturity": "schema.record",
    "Record": "schema.record",
    "ReproducibilityClass": "schema.record",
    "Severity": "schema.record",
    "Status": "schema.record",
    # schema.registry
    "Registry": "schema.registry",
    "RegistryDiff": "schema.registry",
    # schema.run_spec
    "RUN_SPEC_VERSION": "schema.run_spec",
    "AxisSelection": "schema.run_spec",
    "Fidelity": "schema.run_spec",
    "RunSpec": "schema.run_spec",
    # schema.builder
    "RunSpecBuilder": "schema.builder",
}


def _get_submodule(full_name: str) -> ModuleType:
    """Get or import a submodule by full name."""
    if full_name not in _lazy_submodules:
        _lazy_submodules[full_name] = __import__(full_name, fromlist=["*"])
    return _lazy_submodules[full_name]


def __getattr__(name: str) -> Any:
    """Lazy load submodules and symbols on first access."""
    # Submodules
    if name in {"evidence", "execution", "schema", "surface"}:
        return _get_submodule(f"computronium.experiment.{name}")

    # Symbols from specific submodules
    if name in _symbol_to_module:
        submodule = _get_submodule(f"computronium.experiment.{_symbol_to_module[name]}")
        return getattr(submodule, name)

    raise AttributeError(f"module 'computronium.experiment' has no attribute '{name}'")


def __dir__() -> list[str]:
    """Include lazy symbols in dir() for tab completion."""
    return __all__
