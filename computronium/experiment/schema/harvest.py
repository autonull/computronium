"""Hyperparameter harvesting and schema reflection for experiment configurations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from computronium.experiment.legality.dsl import expr_from_string, or_
from computronium.experiment.schema.axis import (
    AxisKind,
    Domain,
    HyperparameterSpec,
    Scale,
    StructuralAxis,
)


class ConflictingHyperparameterError(ValueError):
    """Raised when two axis primitives define the same hyperparameter name with different semantics."""

    def __init__(self, name: str, sources: list[str]) -> None:
        self.name = name
        self.sources = sources
        super().__init__(
            f"Conflicting hyperparameter '{name}' defined by: {', '.join(sources)}"
        )


@dataclass(frozen=True, slots=True)
class HarvestedSchema:
    """Result of harvesting hyperparameters from all registered axis primitives."""

    hyperparameters: tuple[HyperparameterSpec, ...]
    axis_kind_order: tuple[StructuralAxis, ...]
    version: int

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


def _domain_from_range(lo: float, hi: float, scale: str) -> Domain:
    """Create a Domain from range parameters."""
    return Domain(lo=lo, hi=hi, scale=Scale(scale))


def _domain_from_enum(choices: list[str]) -> Domain:
    """Create a Domain from enumerated choices."""
    return Domain(members=tuple(choices))


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
            # Full spec with availability, prior, override_scope
            domain_spec = spec.get("domain")
            if isinstance(domain_spec, tuple) and len(domain_spec) == 3:
                lo, hi, scale = domain_spec
                if scale == "int":
                    domain = _domain_from_range(lo, hi, "linear")
                    axis_kind = AxisKind.INTEGER
                else:
                    domain = _domain_from_range(lo, hi, scale)
                    axis_kind = AxisKind.CONTINUOUS
            elif isinstance(domain_spec, list):
                domain = _domain_from_enum(domain_spec)
                axis_kind = AxisKind.CATEGORICAL
            else:
                raise ValueError(f"Invalid domain spec for {name}: {domain_spec}")

            availability = spec.get("availability")
            if isinstance(availability, str):
                availability = expr_from_string(availability)

            specs.append(
                HyperparameterSpec(
                    name=name,
                    domain=domain,
                    axis_kind=axis_kind,
                    axis_name=axis_name,
                    availability=availability,
                    prior=spec.get("prior"),
                    override_scope=spec.get("override_scope", "coordinate"),
                )
            )
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
    axis_kind_order = (
        StructuralAxis.SUBSTRATE,
        StructuralAxis.GEOMETRY,
        StructuralAxis.DYNAMICS,
        StructuralAxis.PLASTICITY,
        StructuralAxis.CREDIT,
        StructuralAxis.UPDATE,
    )

    all_hyperparameters: dict[str, HyperparameterSpec] = {}

    # Map structural axes to their config classes
    axis_config_classes = {
        StructuralAxis.SUBSTRATE: (
            "computronium.ontology.substrate",
            "SubstrateConfig",
        ),
        StructuralAxis.GEOMETRY: ("computronium.ontology.geometry", "GeometryConfig"),
        StructuralAxis.DYNAMICS: (
            "computronium.ontology.dynamics",
            "StateDynamicsConfig",
        ),
        StructuralAxis.PLASTICITY: (
            "computronium.state.transitions",
            "PlasticityConfig",
        ),
        StructuralAxis.CREDIT: (
            "computronium.ontology.credit",
            "CreditAssignmentConfig",
        ),
        StructuralAxis.UPDATE: (
            "computronium.ontology.update",
            "ParameterUpdateConfig",
        ),
    }

    for axis_kind in axis_kind_order:
        module_path, class_name = axis_config_classes[axis_kind]
        try:
            module = __import__(module_path, fromlist=[class_name])
            config_cls = getattr(module, class_name)
            hp_dict = config_cls.hyperparameters()
            # Assign to all primitives in this axis
            axis_name = axis_kind.value
            specs = _parse_hyperparameters(hp_dict, axis_name)
            for hp in specs:
                # Check for conflicts
                if hp.name in all_hyperparameters:
                    existing = all_hyperparameters[hp.name]
                    if (
                        existing.domain != hp.domain
                        or existing.axis_kind != hp.axis_kind
                    ):
                        raise ConflictingHyperparameterError(
                            hp.name,
                            [f"{existing.axis_kind.value}.{existing.axis_name}"],
                            [f"{hp.axis_kind.value}.{hp.axis_name}"],
                        )
                    # Merge availabilities if different
                    if hp.availability and existing.availability:
                        hp = HyperparameterSpec(
                            name=hp.name,
                            domain=hp.domain,
                            axis_kind=hp.axis_kind,
                            axis_name=hp.axis_name,
                            availability=or_(existing.availability, hp.availability),
                            prior=hp.prior or existing.prior,
                            override_scope=hp.override_scope,
                        )
                    elif hp.availability and not existing.availability:
                        hp = HyperparameterSpec(
                            name=hp.name,
                            domain=hp.domain,
                            axis_kind=hp.axis_kind,
                            axis_name=hp.axis_name,
                            availability=hp.availability,
                            prior=hp.prior or existing.prior,
                            override_scope=hp.override_scope,
                        )
                all_hyperparameters[hp.name] = hp
        except Exception:
            # If config class doesn't have hyperparameters() or fails, skip
            pass

    return HarvestedSchema(
        hyperparameters=tuple(all_hyperparameters.values()),
        axis_kind_order=axis_kind_order,
        version=version,
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
    "ConflictingHyperparameterError",
    "HarvestedSchema",
    "get_hyperparameter_names",
    "get_hyperparameter_spec",
    "harvest_schema",
]
