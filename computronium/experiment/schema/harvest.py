"""Hyperparameter harvesting and schema reflection for experiment configurations."""

from __future__ import annotations

import inspect
from dataclasses import MISSING, dataclass, field, fields
from typing import TYPE_CHECKING, Any

from computronium.experiment.legality.dsl import (
    CoordinateContext,
    evaluate,
    expr_from_string,
)
from computronium.experiment.schema.axis import (
    NO_DEFAULT,
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

# Schema hyperparameter name -> the config dataclass field that consumes it.
# Names are per-axis (no name is declared by two axes — the schema seam lock
# enforces this), so a schema name may spell a config field differently where
# that field predates the schema name.
CONFIG_FIELD_ALIASES: dict[str, str] = {
    "settle_step": "step_size",
    "settle_beta": "beta",
    "settle_momentum": "momentum",
    "update_lr": "step_size",
    "credit_beta": "beta",
}


def config_field_name(name: str) -> str:
    """The config dataclass field a schema hyperparameter feeds."""
    return CONFIG_FIELD_ALIASES.get(name, name)


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

    def values_for_axis(self, axis: StructuralAxis) -> dict[str, Any]:
        """Effective values belonging to one structural axis."""
        return {
            s.name: self.values[s.name] for s in self.specs if s.axis_name == axis.value
        }

    def by_axis(self, axis: StructuralAxis) -> dict[str, Any]:
        """Effective values for one axis, keyed by the config field each feeds."""
        return {
            config_field_name(s.name): self.values[s.name]
            for s in self.specs
            if s.axis_name == axis.value
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

        # Names are per-axis (the declaration audit rejects a second axis
        # claiming one), so each active spec resolves independently.
        values = {
            spec.name: _resolve_value(spec, coordinate.params, coordinate)
            for spec in active
        }
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
                    "default": None if t.default is NO_DEFAULT else t.default,
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
                    default=(NO_DEFAULT if t.get("default") is None else t["default"]),
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


class UnresolvedHyperparameterError(ValueError):
    """A hyperparameter with no override, no prior, and no config default.

    The Domain.lo fallback (an unswept continuous value resolving to the lower
    bound — 1e-5, the defect that trained every unswept cell at a dead lr,
    TODO47 §6.1) is deleted: a value no source names is a schema error at
    declaration time, not a silent lower bound.
    """


def _config_default(spec: HyperparameterSpec, coordinate: Coordinate) -> Any:
    """The default a hyperparameter resolves to when unswept and unprior'd."""
    axis = StructuralAxis(spec.axis_name)
    field_name = config_field_name(spec.name)
    if spec.default is not NO_DEFAULT:
        return spec.default
    return _config_default_inner(axis, field_name, coordinate)


def _config_default_inner(axis: StructuralAxis, field_name: str, coordinate: Coordinate) -> Any:
    """Inner resolution using config_cls and factories."""
    config_cls = load_axis_config(axis)
    if config_cls is None:
        raise UnresolvedHyperparameterError(
            f"hyperparameter '{field_name}' ({axis.value}) has no config class"
        )
    match = {f.name: f for f in fields(config_cls)}
    field = match.get(field_name)
    if field is not None:
        if field.default is not MISSING:
            return field.default
        if field.default_factory is not MISSING:
            return field.default_factory()
    primitive = getattr(coordinate, axis.value, "")
    factory = getattr(config_cls, primitive, None) if primitive else None
    if callable(factory):
        default = _factory_default(factory, field_name)
        if default is not NO_DEFAULT:
            return default
    return _any_factory_default_value(config_cls, field_name)


def _any_factory_default_value(config_cls: Any, field_name: str) -> Any:
    """Any factory default on the axis for ``field_name``, else raise."""
    for attr in dir(config_cls):
        if attr.startswith("_"):
            continue
        other = getattr(config_cls, attr, None)
        if callable(other):
            default = _factory_default(other, field_name)
            if default is not NO_DEFAULT:
                return default
    raise UnresolvedHyperparameterError(
        f"hyperparameter '{field_name}' has no prior and no "
        f"config default; declare one or register a prior"
    )


def _resolve_value(
    spec: HyperparameterSpec, overrides: Mapping[str, Any], coordinate: Coordinate
) -> Any:
    """Resolve a hyperparameter's effective value: override, then prior, then config default."""
    if spec.name in overrides:
        return overrides[spec.name]
    if spec.prior:
        from computronium.experiment.schema.registries import prior_value

        resolved = prior_value(spec.prior)
        if resolved is not None:
            return resolved[0]
    return _config_default(spec, coordinate)


def _domain_from_range(lo: float, hi: float, scale: str) -> Domain:
    """Create a Domain from range parameters."""
    return Domain(lo=lo, hi=hi, scale=Scale(scale))


def _domain_from_enum(choices: list[str]) -> Domain:
    """Create a Domain from enumerated choices."""
    return Domain(members=tuple(choices))


def _audit_declared(
    hp: HyperparameterSpec,
    axis_kind: StructuralAxis,
    config_cls: Any,
    declared: dict[str, HyperparameterSpec],
) -> None:
    """Declaration-time seam audit for one hyperparameter row.

    Two rules, both loud at harvest instead of silent at resolve:

    - a name is declared by exactly one axis (a second claim raises);
    - a value has a source: a registered prior, a config field default, or a
      factory signature default. The Domain.lo fallback is deleted — an
      unswept value with no source trained every unswept cell at 1e-5
      (TODO47 §6.1).
    """
    if hp.name in declared and declared[hp.name].axis_name != axis_kind.value:
        msg = (
            f"hyperparameter '{hp.name}' declared by two axes: "
            f"{declared[hp.name].axis_name} and {axis_kind.value}"
        )
        raise UnresolvedHyperparameterError(msg)
    if hp.prior or hp.default is not NO_DEFAULT:
        return
    field_name = config_field_name(hp.name)
    for f in fields(config_cls):
        if f.name == field_name and (
            f.default is not MISSING or f.default_factory is not MISSING
        ):
            return
    if _any_factory_default(config_cls, field_name):
        return
    raise UnresolvedHyperparameterError(
        f"hyperparameter '{hp.name}' ({axis_kind.value}) has no prior and no "
        f"config default; declare one or register a prior"
    )


def _factory_default(factory: Any, field_name: str) -> Any:
    """The signature default ``factory`` carries for ``field_name``, or NO_DEFAULT."""
    try:
        sig = inspect.signature(factory)
    except TypeError, ValueError:
        return NO_DEFAULT
    param = sig.parameters.get(field_name)
    if param is not None and param.default is not inspect.Parameter.empty:
        return param.default
    return NO_DEFAULT


def _any_factory_default(config_cls: Any, name: str) -> bool:
    """Whether any factory on the axis accepts ``name`` with a signature default."""
    for attr_name in dir(config_cls):
        if attr_name.startswith("_"):
            continue
        factory = getattr(config_cls, attr_name, None)
        if not callable(factory):
            continue
        if _factory_default(factory, name) is not NO_DEFAULT:
            return True
    return False


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
        default=spec.get("default", NO_DEFAULT),
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
        UnresolvedHyperparameterError: A hyperparameter has no prior and no
            config default — declaration-time, not a silent domain-edge value.
    """
    per_axis: dict[StructuralAxis, tuple[HyperparameterSpec, ...]] = {}
    declared: dict[str, HyperparameterSpec] = {}

    for axis_kind in AXIS_KIND_ORDER:
        config_cls = load_axis_config(axis_kind)
        if config_cls is None:
            continue
        specs = _parse_hyperparameters(config_cls.hyperparameters(), axis_kind.value)
        for hp in specs:
            _audit_declared(hp, axis_kind, config_cls, declared)
            declared[hp.name] = hp
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
    "CONFIG_FIELD_ALIASES",
    "ActiveSpace",
    "HarvestedSchema",
    "InactiveHyperparameterError",
    "UnresolvedHyperparameterError",
    "config_field_name",
    "get_hyperparameter_names",
    "get_hyperparameter_spec",
    "harvest_schema",
    "load_axis_config",
]
