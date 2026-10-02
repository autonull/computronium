"""Hyperparameter harvesting and schema reflection for experiment configurations."""

from __future__ import annotations

from dataclasses import MISSING, dataclass, field, fields
from typing import TYPE_CHECKING, Any

from computronium.experiment.legality.dsl import (
    CoordinateContext,
    evaluate,
    expr_from_string,
)
from computronium.experiment.schema.axis import (
    AxisKind,
    Domain,
    HyperparameterSpec,
    Scale,
    StructuralAxis,
    get_axis_spec,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from computronium.experiment.legality.dsl import Expr
    from computronium.experiment.schema.coordinate import Coordinate


class ConflictingHyperparameterError(ValueError):
    """Raised when two axis primitives define the same hyperparameter name with different semantics."""

    def __init__(self, name: str, sources: list[str]) -> None:
        self.name = name
        self.sources = sources
        super().__init__(
            f"Conflicting hyperparameter '{name}' defined by: {', '.join(sources)}"
        )


class InactiveHyperparameterError(ValueError):
    """Raised when a coordinate carries a hyperparameter its selection cannot use.

    Dead configuration is a defect, not a harmless extra: the value would be
    silently discarded at composition time.
    """

    def __init__(self, names: tuple[str, ...], coordinate: object) -> None:
        self.names = names
        self.coordinate = coordinate
        super().__init__(
            f"Hyperparameters {', '.join(names)} are inactive for coordinate "
            f"{getattr(coordinate, 'cell_key', lambda: coordinate)()!s}"
        )


# Structural axis -> (module path, config class). The single source of the
# axis/config correspondence, shared by harvesting and composition.
AXIS_CONFIG_CLASSES: dict[StructuralAxis, tuple[str, str]] = {
    StructuralAxis.SUBSTRATE: ("computronium.ontology.substrate", "SubstrateConfig"),
    StructuralAxis.GEOMETRY: ("computronium.ontology.geometry", "GeometryConfig"),
    StructuralAxis.DYNAMICS: ("computronium.ontology.dynamics", "StateDynamicsConfig"),
    StructuralAxis.PLASTICITY: ("computronium.state.transitions", "PlasticityConfig"),
    StructuralAxis.CREDIT: ("computronium.ontology.credit", "CreditAssignmentConfig"),
    StructuralAxis.UPDATE: ("computronium.ontology.update", "ParameterUpdateConfig"),
}

AXIS_KIND_ORDER: tuple[StructuralAxis, ...] = (
    StructuralAxis.SUBSTRATE,
    StructuralAxis.GEOMETRY,
    StructuralAxis.DYNAMICS,
    StructuralAxis.PLASTICITY,
    StructuralAxis.CREDIT,
    StructuralAxis.UPDATE,
)


def load_axis_config(axis: StructuralAxis) -> Any | None:
    """Import an axis's config class, or None when the axis has none."""
    module_path, class_name = AXIS_CONFIG_CLASSES[axis]
    try:
        module = __import__(module_path, fromlist=[class_name])
    except ImportError:
        return None
    return getattr(module, class_name, None)


@dataclass(frozen=True, slots=True)
class ActiveSpace:
    """The hyperparameters a coordinate's own primitive selection can accept.

    Produced by availability predicates alone, so composition never has to ask
    which knobs a factory happens to accept.
    """

    values: Mapping[str, Any]
    specs: tuple[HyperparameterSpec, ...]
    inactive: frozenset[str]

    def by_axis(self, axis: StructuralAxis) -> dict[str, Any]:
        """Effective values belonging to one structural axis.

        A name several axes declare (``step_size`` is read by both dynamics and
        update) resolves once and reaches each axis that declared it.
        """
        return {
            s.name: self.values[s.name] for s in self.specs if s.axis_name == axis.value
        }

    def by_axis_specs_for(self, axis: StructuralAxis) -> tuple[HyperparameterSpec, ...]:
        """The active specs belonging to one structural axis."""
        return tuple(s for s in self.specs if s.axis_name == axis.value)

    def for_axis(self, axis: StructuralAxis, primitive: str) -> dict[str, Any]:
        """Active values for one axis, restricted to what its primitive accepts.

        The restriction is a harvested fact (``AxisSpec.accepted_params``), not a
        signature inspection, so composition never asks a factory what it takes.
        """
        axis_spec = get_axis_spec(axis, primitive)
        if axis_spec is None:
            return {}
        values = self.by_axis(axis)
        return {k: v for k, v in values.items() if k in axis_spec.accepted_params}


@dataclass(frozen=True, slots=True)
class HarvestedSchema:
    """Result of harvesting hyperparameters from all registered axis primitives."""

    hyperparameters: tuple[HyperparameterSpec, ...]
    axis_kind_order: tuple[StructuralAxis, ...]
    version: int
    by_axis_specs: Mapping[StructuralAxis, tuple[HyperparameterSpec, ...]] = field(
        default_factory=dict, repr=False, compare=False
    )

    def by_name(self) -> dict[str, HyperparameterSpec]:
        """Hyperparameter specs keyed by name."""
        return {h.name: h for h in self.hyperparameters}

    def active(self, coordinate: Coordinate) -> ActiveSpace:
        """Resolve the active space for a coordinate's primitive selection.

        Availability is decided by the predicates declared in ``AXES`` — for the
        primitive and for the hyperparameter — evaluated against the coordinate.
        No axis-name comparisons live here, so a new pairing needs a spec row.

        Args:
            coordinate: The primitive selection and its overrides.

        Returns:
            ActiveSpace carrying effective values, active specs, and the names
            the predicates excluded.

        Raises:
            InactiveHyperparameterError: The coordinate carries a parameter its
                own selection cannot use.
        """
        ctx = CoordinateContext(coordinate)
        active: list[HyperparameterSpec] = []
        inactive: set[str] = set()
        for axis in self.axis_kind_order:
            for spec in self.by_axis_specs.get(axis, ()):
                if _available(spec, coordinate, ctx):
                    active.append(spec)
                else:
                    inactive.add(spec.name)

        dead = tuple(sorted(n for n in coordinate.params if n in inactive))
        if dead:
            raise InactiveHyperparameterError(dead, coordinate)

        values = {spec.name: _resolve_value(spec, coordinate.params) for spec in active}
        return ActiveSpace(
            values=values,
            specs=tuple(active),
            inactive=frozenset(inactive),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "version": self.version,
            "axis_kind_order": [k.value for k in self.axis_kind_order],
            "hyperparameters": [
                {
                    "name": t.name,
                    "axis_kind": t.axis_kind.value,
                    "axis_name": t.axis_name,
                    "domain": {
                        "members": t.domain.members,
                        "lo": t.domain.lo,
                        "hi": t.domain.hi,
                        "scale": t.domain.scale.value,
                    },
                    "availability": str(t.availability) if t.availability else None,
                    "prior": t.prior,
                    "override_scope": t.override_scope,
                }
                for t in self.hyperparameters
            ],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HarvestedSchema:
        """Create from dictionary."""
        return cls(
            version=data["version"],
            axis_kind_order=tuple(StructuralAxis(k) for k in data["axis_kind_order"]),
            hyperparameters=tuple(
                HyperparameterSpec(
                    name=t["name"],
                    axis_kind=AxisKind(t["axis_kind"]),
                    axis_name=t["axis_name"],
                    domain=Domain(
                        members=tuple(t["domain"]["members"])
                        if t["domain"]["members"]
                        else None,
                        lo=t["domain"]["lo"],
                        hi=t["domain"]["hi"],
                        scale=Scale(t["domain"]["scale"]),
                    ),
                    availability=None,  # String representation only for serialization
                    prior=t.get("prior"),
                    override_scope=t.get("override_scope", "coordinate"),
                )
                for t in data["hyperparameters"]
            ),
        )


def _available(
    spec: HyperparameterSpec, coordinate: Coordinate, ctx: CoordinateContext
) -> bool:
    """Whether a hyperparameter is usable by a coordinate's primitive selection.

    Both predicates must hold: the selected primitive for the spec's axis must
    be available, and the hyperparameter's own availability expression must be
    satisfied. Both come from ``AXES``.
    """
    axis = StructuralAxis(spec.axis_name)
    axis_spec = get_axis_spec(axis, getattr(coordinate, spec.axis_name))
    if axis_spec is None or not axis_spec.available:
        return False
    predicates: list[Expr] = []
    if axis_spec.availability_predicate is not None:
        predicates.append(axis_spec.availability_predicate)
    if spec.availability is not None:
        predicates.append(spec.availability)
    return all(evaluate(p, ctx) for p in predicates)


def _config_default(spec: HyperparameterSpec) -> Any:
    """The config dataclass's own default for a hyperparameter — the last resort."""
    config_cls = load_axis_config(StructuralAxis(spec.axis_name))
    if config_cls is None:
        return spec.domain.members[0] if spec.domain.members else spec.domain.lo
    match = {f.name: f for f in fields(config_cls)}
    if spec.name not in match:
        return spec.domain.members[0] if spec.domain.members else spec.domain.lo
    field = match[spec.name]
    if field.default is not MISSING:
        return field.default
    if field.default_factory is not MISSING:
        return field.default_factory()
    return spec.domain.members[0] if spec.domain.members else spec.domain.lo


def _resolve_value(spec: HyperparameterSpec, overrides: Mapping[str, Any]) -> Any:
    """Resolve a hyperparameter's effective value: override, then prior, then default."""
    if spec.name in overrides:
        return overrides[spec.name]
    if spec.prior:
        from computronium.experiment.schema.registries import prior_value

        resolved = prior_value(spec.prior)
        if resolved is not None:
            return resolved[0]
    return _config_default(spec)


def _domain_from_range(lo: float, hi: float, scale: str) -> Domain:
    """Create a Domain from range parameters."""
    return Domain(lo=lo, hi=hi, scale=Scale(scale))


def _domain_from_enum(choices: list[str]) -> Domain:
    """Create a Domain from enumerated choices."""
    return Domain(members=tuple(choices))


def declare(declared: dict[str, HyperparameterSpec], hp: HyperparameterSpec) -> None:
    """Record one hyperparameter declaration.

    Two axes may legitimately declare the same name — ``step_size`` is read by
    both dynamics and update — but they must mean the same thing by it. A
    disagreement is a registry failure, not a silent merge.
    """
    existing = declared.get(hp.name)
    if existing is None:
        declared[hp.name] = hp
        return
    if existing.domain != hp.domain or existing.axis_kind != hp.axis_kind:
        raise ConflictingHyperparameterError(
            hp.name,
            [
                f"{existing.axis_kind.value}.{existing.axis_name}",
                f"{hp.axis_kind.value}.{hp.axis_name}",
            ],
        )


def _from_dict(name: str, spec: dict[str, Any], axis_name: str) -> HyperparameterSpec:
    """One fully-declared hyperparameter: domain, kind, availability, prior."""
    domain_spec = spec.get("domain")
    domain, axis_kind = _domain_and_kind(name, domain_spec)
    availability = spec.get("availability")
    if isinstance(availability, str):
        availability = expr_from_string(availability)
    # A knob the primitive reads but a run may not choose: the task's own shape,
    # the run's device. Declared structural so no sweep and no sampler moves it.
    return HyperparameterSpec(
        name=name,
        domain=domain,
        axis_kind=(
            AxisKind.STRUCTURAL if spec.get("kind") == "structural" else axis_kind
        ),
        axis_name=axis_name,
        availability=availability,
        prior=spec.get("prior"),
        override_scope=spec.get("override_scope", "coordinate"),
    )


def _domain_and_kind(name: str, domain_spec: Any) -> tuple[Domain, AxisKind]:
    """A declared domain and the kind of axis it is sampled on."""
    if isinstance(domain_spec, tuple) and len(domain_spec) == 3:
        lo, hi, scale = domain_spec
        if scale == "int":
            return _domain_from_range(lo, hi, "linear"), AxisKind.INTEGER
        return _domain_from_range(lo, hi, scale), AxisKind.CONTINUOUS
    if isinstance(domain_spec, list):
        return _domain_from_enum(domain_spec), AxisKind.CATEGORICAL
    msg = f"invalid domain spec for {name}: {domain_spec}"
    raise ValueError(msg)


def _parse_hyperparameters(
    hp_dict: dict[str, Any], axis_name: str
) -> list[HyperparameterSpec]:
    """Parse hyperparameters from a config class's hyperparameters() dict.

    Expected format:
    {
        "param_name": (lo, hi, scale),  # for continuous/integer
        "param_name": [choice1, choice2, ...],  # for categorical
        "param_name": {"domain": (lo, hi, scale), "availability": Expr, "prior": "prior_name", "override_scope": "coordinate"},
    }
    """
    specs = []
    for name, spec in hp_dict.items():
        if isinstance(spec, tuple) and len(spec) == 3:
            # Simple range: (lo, hi, scale)
            lo, hi, scale = spec
            if scale == "int":
                specs.append(
                    HyperparameterSpec(
                        name=name,
                        domain=_domain_from_range(lo, hi, "linear"),
                        axis_kind=AxisKind.INTEGER,
                        axis_name=axis_name,
                    )
                )
            else:
                specs.append(
                    HyperparameterSpec(
                        name=name,
                        domain=_domain_from_range(lo, hi, scale),
                        axis_kind=AxisKind.CONTINUOUS,
                        axis_name=axis_name,
                    )
                )
        elif isinstance(spec, list):
            # Categorical
            specs.append(
                HyperparameterSpec(
                    name=name,
                    domain=_domain_from_enum(spec),
                    axis_kind=AxisKind.CATEGORICAL,
                    axis_name=axis_name,
                )
            )
        elif isinstance(spec, dict):
            specs.append(_from_dict(name, spec, axis_name))
        else:
            raise ValueError(f"Unknown hyperparameter spec format for {name}: {spec}")
    return specs


def harvest_schema(version: int = 1) -> HarvestedSchema:
    """Harvest all hyperparameters from registered axis primitives.

    Iterates over all structural axes, calls the config class's
    hyperparameters() method once per axis (config classes are shared
    across primitives), and deduplicates across axes.

    Args:
        version: Schema version to assign (default 1).

    Returns:
        HarvestedSchema with all hyperparameters, ordered by structural axis.

    Raises:
        ConflictingHyperparameterError: If a hyperparameter name has conflicting definitions.
    """
    per_axis: dict[StructuralAxis, tuple[HyperparameterSpec, ...]] = {}
    declared: dict[str, HyperparameterSpec] = {}

    for axis_kind in AXIS_KIND_ORDER:
        config_cls = load_axis_config(axis_kind)
        if config_cls is None:
            continue
        specs = _parse_hyperparameters(config_cls.hyperparameters(), axis_kind.value)
        for hp in specs:
            declare(declared, hp)
        per_axis[axis_kind] = tuple(specs)

    return HarvestedSchema(
        hyperparameters=tuple(declared.values()),
        axis_kind_order=AXIS_KIND_ORDER,
        version=version,
        by_axis_specs=per_axis,
    )


def get_hyperparameter_names() -> frozenset[str]:
    """Get the set of all harvested hyperparameter names."""
    schema = harvest_schema()
    return frozenset(t.name for t in schema.hyperparameters)


def get_hyperparameter_spec(name: str) -> HyperparameterSpec | None:
    """Get the specification for a specific hyperparameter."""
    schema = harvest_schema()
    for t in schema.hyperparameters:
        if t.name == name:
            return t
    return None


__all__ = [
    "AXIS_KIND_ORDER",
    "ActiveSpace",
    "ConflictingHyperparameterError",
    "HarvestedSchema",
    "InactiveHyperparameterError",
    "declare",
    "get_hyperparameter_names",
    "get_hyperparameter_spec",
    "harvest_schema",
    "load_axis_config",
]
