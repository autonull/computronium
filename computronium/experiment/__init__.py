"""Computronium Experiment Kernel — unified experiment orchestration."""

from __future__ import annotations

from computronium.experiment import evidence, execution, schema
from computronium.experiment.schema.axis import (
    AXES_REGISTRIES,
    CREDIT_REGISTRY,
    DYNAMICS_REGISTRY,
    GEOMETRY_REGISTRY,
    PLASTICITY_REGISTRY,
    SUBSTRATE_REGISTRY,
    UPDATE_REGISTRY,
    AxisKind,
    AxisPrimitive,
    AxisSpec,
    get_axis_spec,
    get_registry,
    is_available,
    list_axis_specs,
    register_axis_spec,
)
from computronium.experiment.schema.registry import Registry, RegistryDiff

__all__ = [
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
    "Registry",
    "RegistryDiff",
    "evidence",
    "execution",
    "get_axis_spec",
    "get_registry",
    "is_available",
    "list_axis_specs",
    "register_axis_spec",
    "schema",
]
