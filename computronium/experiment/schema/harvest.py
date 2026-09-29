"""Tunable harvesting and schema reflection for experiment configurations."""

from __future__ import annotations

import dataclasses
import inspect
from dataclasses import dataclass
from typing import Any

from computronium.experiment.schema.axis import AXES_REGISTRIES, AxisKind


class ConflictingTunableError(ValueError):
    """Raised when two axis primitives define the same tunable name with different semantics."""

    def __init__(self, name: str, sources: list[str]) -> None:
        self.name = name
        self.sources = sources
        super().__init__(
            f"Conflicting tunable '{name}' defined by: {', '.join(sources)}"
        )


@dataclass(frozen=True, slots=True)
class TunableSpec:
    """Specification for a single tunable parameter."""

    name: str
    axis_kind: AxisKind
    axis_name: str
    type_hint: object
    default: Any
    description: str = ""
    constraints: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class HarvestedSchema:
    """Result of harvesting tunables from all registered axis primitives."""

    tunables: tuple[TunableSpec, ...]
    axis_kind_order: tuple[AxisKind, ...]
    version: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "version": self.version,
            "axis_kind_order": [k.value for k in self.axis_kind_order],
            "tunables": [
                {
                    "name": t.name,
                    "axis_kind": t.axis_kind.value,
                    "axis_name": t.axis_name,
                    "type_hint": str(t.type_hint),
                    "default": t.default,
                    "description": t.description,
                    "constraints": list(t.constraints),
                }
                for t in self.tunables
            ],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HarvestedSchema:
        """Create from dictionary."""
        return cls(
            version=data["version"],
            axis_kind_order=tuple(AxisKind(k) for k in data["axis_kind_order"]),
            tunables=tuple(
                TunableSpec(
                    name=t["name"],
                    axis_kind=AxisKind(t["axis_kind"]),
                    axis_name=t["axis_name"],
                    type_hint=t["type_hint"],
                    default=t["default"],
                    description=t.get("description", ""),
                    constraints=tuple(t.get("constraints", ())),
                )
                for t in data["tunables"]
            ),
        )


_RESERVED_FIELDS = frozenset({"name", "axis_kind"})


def _parse_tunables_dict(
    tunables_attr: dict[str, Any], axis_kind: AxisKind, axis_name: str
) -> list[TunableSpec]:
    """Parse tunables from a dict attribute."""
    tunables = []
    for name, spec in tunables_attr.items():
        if isinstance(spec, tuple):
            type_hint, default = spec[0], spec[1] if len(spec) > 1 else None
            description = spec[2] if len(spec) > 2 else ""
            constraints = spec[3] if len(spec) > 3 else ()
        else:
            type_hint, default, description, constraints = spec, None, "", ()
        tunables.append(
            TunableSpec(
                name=name,
                axis_kind=axis_kind,
                axis_name=axis_name,
                type_hint=type_hint,
                default=default,
                description=description,
                constraints=tuple(constraints)
                if isinstance(constraints, (list, tuple))
                else (),
            )
        )
    return tunables


def _parse_tunables_sequence(
    tunables_attr: list | tuple, axis_kind: AxisKind, axis_name: str
) -> list[TunableSpec]:
    """Parse tunables from a list/tuple attribute."""
    tunables = []
    for item in tunables_attr:
        if isinstance(item, str):
            tunables.append(
                TunableSpec(
                    name=item,
                    axis_kind=axis_kind,
                    axis_name=axis_name,
                    type_hint=Any,
                    default=None,
                    description="",
                    constraints=(),
                )
            )
        elif isinstance(item, tuple) and len(item) >= 2:
            name, type_hint = item[0], item[1]
            default = item[2] if len(item) > 2 else None
            description = item[3] if len(item) > 3 else ""
            constraints = item[4] if len(item) > 4 else ()
            tunables.append(
                TunableSpec(
                    name=name,
                    axis_kind=axis_kind,
                    axis_name=axis_name,
                    type_hint=type_hint,
                    default=default,
                    description=description,
                    constraints=tuple(constraints)
                    if isinstance(constraints, (list, tuple))
                    else (),
                )
            )
    return tunables


def _parse_dataclass_fields(
    cls: type[Any], axis_kind: AxisKind, axis_name: str
) -> list[TunableSpec]:
    """Parse tunables from dataclass fields."""
    tunables = []
    for field in dataclasses.fields(cls):
        if field.name in _RESERVED_FIELDS or field.name.startswith("_"):
            continue
        type_hint = field.type if field.type != inspect.Parameter.empty else Any
        default = field.default if field.default != dataclasses.MISSING else None
        tunables.append(
            TunableSpec(
                name=field.name,
                axis_kind=axis_kind,
                axis_name=axis_name,
                type_hint=type_hint,
                default=default,
                description="",
                constraints=(),
            )
        )
    return tunables


def _extract_tunables_from_class(
    cls: type[Any], axis_kind: AxisKind, axis_name: str
) -> list[TunableSpec]:
    """Extract tunable specifications from a primitive class."""
    tunables = []

    if hasattr(cls, "__tunables__"):
        tunables_attr = getattr(cls, "__tunables__")
        if isinstance(tunables_attr, dict):
            tunables.extend(_parse_tunables_dict(tunables_attr, axis_kind, axis_name))
        elif isinstance(tunables_attr, (list, tuple)):
            tunables.extend(
                _parse_tunables_sequence(tunables_attr, axis_kind, axis_name)
            )

    if dataclasses.is_dataclass(cls):
        tunables.extend(_parse_dataclass_fields(cls, axis_kind, axis_name))

    return tunables


def harvest_schema(version: int = 1) -> HarvestedSchema:
    """Harvest all tunables from registered axis primitives.

    Deduplicates by name; raises ConflictingTunableError if the same name
    is defined with different semantics across axes.

    Args:
        version: Schema version to assign (default 1).

    Returns:
        HarvestedSchema with all tunables, ordered by axis kind.

    Raises:
        ConflictingTunableError: If a tunable name has conflicting definitions.
    """
    axis_kind_order = (
        AxisKind.SUBSTRATE,
        AxisKind.GEOMETRY,
        AxisKind.DYNAMICS,
        AxisKind.PLASTICITY,
        AxisKind.CREDIT,
        AxisKind.UPDATE,
    )

    all_tunables: dict[str, list[TunableSpec]] = {}

    for axis_kind in axis_kind_order:
        registry = AXES_REGISTRIES[axis_kind]
        for spec in registry.values():
            primitive_cls = _get_primitive_class(axis_kind, spec.name)
            if primitive_cls is None:
                continue

            tunables = _extract_tunables_from_class(primitive_cls, axis_kind, spec.name)
            for t in tunables:
                all_tunables.setdefault(t.name, []).append(t)

    final_tunables = []
    for name, candidates in all_tunables.items():
        if len(candidates) > 1:
            first = candidates[0]
            for other in candidates[1:]:
                if (
                    other.type_hint != first.type_hint
                    or other.default != first.default
                    or other.constraints != first.constraints
                ):
                    raise ConflictingTunableError(
                        name,
                        [f"{c.axis_kind.value}.{c.axis_name}" for c in candidates],
                    )
            final_tunables.append(first)
        else:
            final_tunables.append(candidates[0])

    return HarvestedSchema(
        tunables=tuple(final_tunables),
        axis_kind_order=axis_kind_order,
        version=version,
    )


def _get_primitive_class(axis_kind: AxisKind, name: str) -> type[Any] | None:
    """Get the primitive class for a registered axis spec."""
    # This would need access to the actual primitive classes
    # For now, we return None and rely on AxisSpec metadata
    # In a full implementation, this would map to the actual classes
    return None


def get_tunable_names() -> frozenset[str]:
    """Get the set of all harvested tunable names."""
    schema = harvest_schema()
    return frozenset(t.name for t in schema.tunables)


def get_tunable_spec(name: str) -> TunableSpec | None:
    """Get the specification for a specific tunable."""
    schema = harvest_schema()
    for t in schema.tunables:
        if t.name == name:
            return t
    return None


__all__ = [
    "ConflictingTunableError",
    "HarvestedSchema",
    "TunableSpec",
    "get_tunable_names",
    "get_tunable_spec",
    "harvest_schema",
]
