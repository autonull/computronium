"""Axis specification and primitive registration for the experiment ontology.

Axis system (L1 from Remediation Ledger):
- StructuralAxis: the six ontology axes (Substrate, Geometry, Dynamics, Plasticity, Credit, Update)
- AxisKind: four-kind type system for hyperparameters (STRUCTURAL, CONTINUOUS, INTEGER, CATEGORICAL)
- AxisSpec: unified specification with Domain, availability, prior, override_scope, topology_params
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from computronium.experiment.legality.dsl import Expr

from computronium.experiment.schema.registry import Registry


class StructuralAxis(StrEnum):
    """The six structural axes of the experiment ontology (formerly AxisKind)."""

    SUBSTRATE = "substrate"
    GEOMETRY = "geometry"
    DYNAMICS = "dynamics"
    PLASTICITY = "plasticity"
    CREDIT = "credit"
    UPDATE = "update"


class AxisKind(StrEnum):
    """Axis kind for hyperparameter parameters (four-kind type system)."""

    STRUCTURAL = (
        "structural"  # Fixed by primitive choice (e.g., input_dim, neurons_per_tile)
    )
    CONTINUOUS = "continuous"  # Continuous range (e.g., learning_rate, step_size)
    INTEGER = "integer"  # Integer range (e.g., num_layers, max_steps)
    CATEGORICAL = "categorical"  # Discrete choices (e.g., optimizer, init_scheme)


class Scale(StrEnum):
    """Scale for continuous/integer ranges."""

    LINEAR = "linear"
    LOG = "log"


@dataclass(frozen=True, slots=True)
class Domain:
    """Domain specification for a hyperparameter parameter."""

    members: tuple[Any, ...] | None = None  # For Enumerated/CATEGORICAL
    lo: float | None = None  # For Range/CONTINUOUS/INTEGER
    hi: float | None = None  # For Range/CONTINUOUS/INTEGER
    scale: Scale = Scale.LINEAR  # For Range/CONTINUOUS/INTEGER

    def __post_init__(self) -> None:
        if self.members is not None:
            if not self.members:
                raise ValueError("Enumerated domain must have non-empty members")
            if self.lo is not None or self.hi is not None:
                raise ValueError("Enumerated domain cannot have lo/hi")
        else:
            if self.lo is None or self.hi is None:
                raise ValueError("Range domain must have lo and hi")
            if self.lo >= self.hi:
                raise ValueError(f"Domain lo ({self.lo}) must be < hi ({self.hi})")


# Sentinel: the spec declares no config default of its own. A distinct object
# (not dataclasses.MISSING, which dataclasses read as "no default").
NO_DEFAULT = object()


@dataclass(frozen=True, slots=True)
class HyperparameterSpec:
    """Specification for a hyperparameter (hyperparameter)."""

    name: str
    domain: Domain
    axis_kind: AxisKind
    axis_name: str  # Which structural axis this belongs to
    availability: Expr | None = None  # Conditional availability predicate
    prior: str | None = None  # PriorSpec name
    override_scope: str = "coordinate"  # "coordinate" | "run" | "global"
    # The declared config default for an unswept, unprior'd value. NO_DEFAULT
    # means "no source" — the harvest audit rejects the row (TODO48 Q4: the
    # Domain.lo fallback is deleted).
    default: Any = NO_DEFAULT


@dataclass(frozen=True, slots=True)
class AxisSpec:
    """Specification for an axis primitive."""

    name: str
    axis_kind: StructuralAxis
    description: str = ""
    available: bool = True
    # Why a primitive is unavailable, when it is. A retired row needs a
    # recorded reason (R78), not a silent omission.
    unavailable_reason: str | None = None
    availability_predicate: Expr | None = (
        None  # Conditional availability for the whole primitive
    )
    prior: str | None = None  # PriorSpec for this primitive
    override_scope: str = "coordinate"  # "coordinate" | "run" | "global"
    accepted_params: frozenset[str] = frozenset()  # Harvested from the factory once
    topology_params: tuple[
        HyperparameterSpec, ...
    ] = ()  # Structural params (not searched)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("AxisSpec.name must be non-empty")
        if not isinstance(self.axis_kind, StructuralAxis):
            raise TypeError(
                f"axis_kind must be StructuralAxis, got {type(self.axis_kind)}"
            )


@runtime_checkable
class AxisPrimitive(Protocol):
    """Protocol for axis primitives that can be auto-registered."""

    name: str
    axis_kind: StructuralAxis

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Auto-register subclasses with the appropriate axis registry."""
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "axis_kind") and hasattr(cls, "name"):
            registry = AXES_REGISTRIES.get(cls.axis_kind)
            if registry is not None:
                registry.register(cls)  # type: ignore[arg-type]


# Global axis registries - one per structural axis
AXES_REGISTRIES: dict[StructuralAxis, Registry[AxisSpec]] = {
    StructuralAxis.SUBSTRATE: Registry[AxisSpec](),
    StructuralAxis.GEOMETRY: Registry[AxisSpec](),
    StructuralAxis.DYNAMICS: Registry[AxisSpec](),
    StructuralAxis.PLASTICITY: Registry[AxisSpec](),
    StructuralAxis.CREDIT: Registry[AxisSpec](),
    StructuralAxis.UPDATE: Registry[AxisSpec](),
}

# Convenience access
SUBSTRATE_REGISTRY = AXES_REGISTRIES[StructuralAxis.SUBSTRATE]
GEOMETRY_REGISTRY = AXES_REGISTRIES[StructuralAxis.GEOMETRY]
DYNAMICS_REGISTRY = AXES_REGISTRIES[StructuralAxis.DYNAMICS]
PLASTICITY_REGISTRY = AXES_REGISTRIES[StructuralAxis.PLASTICITY]
CREDIT_REGISTRY = AXES_REGISTRIES[StructuralAxis.CREDIT]
UPDATE_REGISTRY = AXES_REGISTRIES[StructuralAxis.UPDATE]


def get_registry(kind: StructuralAxis) -> Registry[AxisSpec]:
    """Get the registry for a given structural axis."""
    return AXES_REGISTRIES[kind]


def register_axis_spec(spec: AxisSpec) -> None:
    """Register an axis specification in the appropriate registry."""
    registry = AXES_REGISTRIES[spec.axis_kind]
    registry.register(spec)


def get_axis_spec(kind: StructuralAxis, name: str) -> AxisSpec | None:
    """Get an axis specification by kind and name."""
    return AXES_REGISTRIES[kind].get(name)


def list_axis_specs(kind: StructuralAxis) -> tuple[AxisSpec, ...]:
    """List all axis specifications for a given kind."""
    return AXES_REGISTRIES[kind].values()


def is_available(kind: StructuralAxis, name: str) -> bool:
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
    "Domain",
    "HyperparameterSpec",
    "Scale",
    "StructuralAxis",
    "get_axis_spec",
    "get_registry",
    "is_available",
    "list_axis_specs",
    "register_axis_spec",
]
