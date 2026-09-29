"""Axis specification and primitive registration for the experiment ontology."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol, runtime_checkable

from computronium.experiment.schema.registry import Registry


class AxisKind(StrEnum):
    """The six axes of the experiment ontology."""

    SUBSTRATE = "substrate"
    GEOMETRY = "geometry"
    DYNAMICS = "dynamics"
    PLASTICITY = "plasticity"
    CREDIT = "credit"
    UPDATE = "update"


@runtime_checkable
class AxisPrimitive(Protocol):
    """Protocol for axis primitives that can be auto-registered."""

    name: str
    axis_kind: AxisKind

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Auto-register subclasses with the appropriate axis registry."""
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "axis_kind") and hasattr(cls, "name"):
            registry = AXES_REGISTRIES.get(cls.axis_kind)
            if registry is not None:
                registry.register(cls)  # type: ignore[arg-type]


@dataclass(frozen=True, slots=True)
class AxisSpec:
    """Specification for an axis primitive."""

    name: str
    axis_kind: AxisKind
    description: str = ""
    available: bool = True
    availability_predicate: str = ""  # Optional predicate for conditional availability

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("AxisSpec.name must be non-empty")
        if not isinstance(self.axis_kind, AxisKind):
            raise TypeError(f"axis_kind must be AxisKind, got {type(self.axis_kind)}")


# Global axis registries - one per axis kind
AXES_REGISTRIES: dict[AxisKind, Registry[AxisSpec]] = {
    AxisKind.SUBSTRATE: Registry[AxisSpec](),
    AxisKind.GEOMETRY: Registry[AxisSpec](),
    AxisKind.DYNAMICS: Registry[AxisSpec](),
    AxisKind.PLASTICITY: Registry[AxisSpec](),
    AxisKind.CREDIT: Registry[AxisSpec](),
    AxisKind.UPDATE: Registry[AxisSpec](),
}

# Convenience access
SUBSTRATE_REGISTRY = AXES_REGISTRIES[AxisKind.SUBSTRATE]
GEOMETRY_REGISTRY = AXES_REGISTRIES[AxisKind.GEOMETRY]
DYNAMICS_REGISTRY = AXES_REGISTRIES[AxisKind.DYNAMICS]
PLASTICITY_REGISTRY = AXES_REGISTRIES[AxisKind.PLASTICITY]
CREDIT_REGISTRY = AXES_REGISTRIES[AxisKind.CREDIT]
UPDATE_REGISTRY = AXES_REGISTRIES[AxisKind.UPDATE]


def get_registry(kind: AxisKind) -> Registry[AxisSpec]:
    """Get the registry for a given axis kind."""
    return AXES_REGISTRIES[kind]


def register_axis_spec(spec: AxisSpec) -> None:
    """Register an axis specification in the appropriate registry."""
    registry = AXES_REGISTRIES[spec.axis_kind]
    registry.register(spec)


def get_axis_spec(kind: AxisKind, name: str) -> AxisSpec | None:
    """Get an axis specification by kind and name."""
    return AXES_REGISTRIES[kind].get(name)


def list_axis_specs(kind: AxisKind) -> tuple[AxisSpec, ...]:
    """List all axis specifications for a given kind."""
    return AXES_REGISTRIES[kind].values()


def is_available(kind: AxisKind, name: str) -> bool:
    """Check if an axis primitive is available."""
    spec = get_axis_spec(kind, name)
    return spec is not None and spec.available


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
    "get_axis_spec",
    "get_registry",
    "is_available",
    "list_axis_specs",
    "register_axis_spec",
]
