"""The declared legal space, and the cells the system refuses (TODO68).

A map can only show a gap if it knows the space the gap sits in. That space is
declared twice over: the primitive registry says which values an axis may
take, and the system's own void rules say which combinations of those values
mean anything at all. Both are read here, from the places the run itself reads
them, so the picture and the run cannot disagree about what is possible.

The grid is a *slice* of that space: three axes are free and the other three
are held at one value, so every cell on the grid is a whole coordinate and
can be judged legal or void exactly. What the slice holds, and where each
held value came from, is part of the answer — a grid whose held axes are
silent about themselves is a picture of nothing in particular.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from computronium.experiment.schema.axis import AXES_REGISTRIES, StructuralAxis
from computronium.experiment.schema.harvest import AXIS_KIND_ORDER

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from computronium.experiment.legality.engine import VoidRule
    from computronium.experiment.schema.record import Record
    from computronium.experiment.schema.run_spec import RunSpec

# The grid shows a slice of the space, and a slice wider than this stops being
# readable. The map says what it left out rather than showing a picture it
# cannot label; the run's own evidence is never among the things left out.
MAX_VALUES_PER_AXIS = 8

# Where a held axis's value came from.
SOURCE_MEASURED = "measured"
SOURCE_DECLARED = "declared"
SOURCE_DEFAULT = "default"

CellStatus = Literal["legal", "void"]


@dataclass(frozen=True, slots=True)
class SpaceCell:
    """One cell of the declared space, and what the system says of it."""

    coordinate: dict[str, str]
    status: CellStatus
    reason: str
    in_declaration: bool

    def to_dict(self) -> dict[str, Any]:
        """The cell as the dashboard reads it."""
        return {
            "coordinate": self.coordinate,
            "status": self.status,
            "reason": self.reason,
            "in_declaration": self.in_declaration,
        }


def axis_values(axis: StructuralAxis) -> tuple[str, ...]:
    """The primitives the registry declares on an axis, in registry order."""
    return tuple(spec.name for spec in AXES_REGISTRIES[axis].values() if spec.available)


def declared_values(spec: RunSpec | None, axis: StructuralAxis) -> tuple[str, ...]:
    """The primitives the run's own declaration permits on an axis.

    A run that does not narrow an axis permits everything on it, which is the
    honest reading: the declaration says nothing about that axis.
    """
    if spec is None:
        return ()
    return tuple(spec.selected_primitives(axis))


def measured_values(records: Sequence[Record], axis: StructuralAxis) -> tuple[str, ...]:
    """The values the run actually measured on an axis."""
    seen: dict[str, None] = {}
    for record in records:
        value = getattr(record, axis.value, "")
        if value:
            seen.setdefault(value, None)
    return tuple(seen)


def grid_values(
    axis: StructuralAxis,
    spec: RunSpec | None,
    records: Sequence[Record],
    *,
    limit: int = MAX_VALUES_PER_AXIS,
) -> tuple[str, ...]:
    """The values the grid shows on one axis.

    The run's own evidence comes first, because a grid that hid it would show
    a picture the run does not support; the run's declaration follows while
    there is room; the rest of the axis fills in registry order. The evidence
    is never dropped: a limit that cannot hold it yields rather than lie.
    """
    available = axis_values(axis)
    if not available:
        return ()

    selected = set(measured_values(records, axis))
    for value in declared_values(spec, axis):
        if len(selected) >= limit:
            break
        selected.add(value)
    for value in available:
        if len(selected) >= limit:
            break
        selected.add(value)
    return tuple(value for value in available if value in selected)


def held_axes(
    spec: RunSpec | None,
    records: Sequence[Record],
    free: Sequence[StructuralAxis],
) -> tuple[dict[str, str], dict[str, str]]:
    """The value each held axis is fixed at, and where that value came from.

    A held axis is one the grid does not show. Its value is the one the run
    used, so the run's evidence lies inside the slice; the declaration is the
    next answer, and the registry's first value the last.
    """
    free_values = {axis.value for axis in free}
    values: dict[str, str] = {}
    sources: dict[str, str] = {}

    for axis in AXIS_KIND_ORDER:
        if axis.value in free_values:
            continue
        measured = measured_values(records, axis)
        if len(measured) == 1:
            values[axis.value] = measured[0]
            sources[axis.value] = SOURCE_MEASURED
            continue
        declared = declared_values(spec, axis)
        if len(declared) == 1:
            values[axis.value] = declared[0]
            sources[axis.value] = SOURCE_DECLARED
            continue
        available = axis_values(axis)
        if available:
            values[axis.value] = available[0]
            sources[axis.value] = SOURCE_DEFAULT

    return values, sources


def void_reason(
    coordinate: Mapping[str, str],
    task: str | None = None,
    rules: Sequence[VoidRule] | None = None,
) -> str | None:
    """Why the system refuses this cell, or ``None`` when it does not.

    The rules are the system's own — the ones the gate applies to a proposal
    and the search space applies before it offers a cell — so a cell marked
    legal here is a cell the run can actually measure.

    The rules are read once and handed in when the caller has many cells to
    judge: reading them for every cell of a slice costs more than judging
    them does, and they do not change between cells.
    """
    from computronium.experiment.legality.dsl import CoordinateContext, evaluate
    from computronium.experiment.legality.engine import void_rules
    from computronium.experiment.schema.coordinate import Coordinate

    selection = {axis.value: coordinate.get(axis.value, "") for axis in AXIS_KIND_ORDER}
    if not all(selection.values()):
        return "the coordinate does not name every axis"

    ctx = CoordinateContext(Coordinate(**selection, params={}), task=task)
    for rule in void_rules() if rules is None else rules:
        if not evaluate(rule.predicate, ctx):
            return f"{rule.name}: {rule.description}"
    return None


def declared_space(
    spec: RunSpec | None,
    records: Sequence[Record],
    free: Sequence[StructuralAxis],
    *,
    task: str | None = None,
    limit: int = MAX_VALUES_PER_AXIS,
) -> dict[str, Any]:
    """The grid's slice of the declared space.

    Args:
        spec: The run's own declaration, when the run has one.
        records: The run's records, which say what it measured.
        free: The three axes the grid shows.
        task: The task the cells would be measured on.
        limit: How many values one axis may show.

    Returns:
        The values each free axis takes, the value each held axis is fixed
        at, the run's declaration per axis, and every cell of the slice with
        the system's verdict on it.

    Raises:
        ValueError: The grid is not three axes wide.
    """
    if len(free) != 3:
        msg = f"the grid shows three axes, not {len(free)}"
        raise ValueError(msg)

    values = {
        axis.value: list(grid_values(axis, spec, records, limit=limit)) for axis in free
    }
    held, sources = held_axes(spec, records, free)
    declared = {
        axis.value: list(declared_values(spec, axis)) for axis in AXIS_KIND_ORDER
    }
    available = {axis.value: len(axis_values(axis)) for axis in AXIS_KIND_ORDER}

    # The rules are read once: a slice holds hundreds of cells, and reading
    # the rules for each of them costs more than judging them does.
    from computronium.experiment.legality.engine import void_rules as system_rules

    rules = system_rules()

    cells: list[SpaceCell] = []
    for x in values[free[0].value]:
        for y in values[free[1].value]:
            for z in values[free[2].value]:
                selection = dict(held)
                selection[free[0].value] = x
                selection[free[1].value] = y
                selection[free[2].value] = z
                reason = void_reason(selection, task, rules)
                in_declaration = all(
                    selection.get(axis.value, "") in declared[axis.value]
                    for axis in AXIS_KIND_ORDER
                    if declared[axis.value]
                )
                cells.append(
                    SpaceCell(
                        coordinate=selection,
                        status="void" if reason else "legal",
                        reason=reason or "",
                        in_declaration=in_declaration,
                    )
                )

    void_rules: dict[str, int] = {}
    for cell in cells:
        if cell.status != "void":
            continue
        rule = cell.reason.split(":", 1)[0]
        void_rules[rule] = void_rules.get(rule, 0) + 1

    return {
        "axes": [axis.value for axis in free],
        "values": values,
        "held": held,
        "held_source": sources,
        "declared": declared,
        "available": available,
        "cells": [cell.to_dict() for cell in cells],
        "counts": {
            "legal": sum(1 for cell in cells if cell.status == "legal"),
            "void": sum(1 for cell in cells if cell.status == "void"),
        },
        "void_rules": void_rules,
    }


__all__ = [
    "MAX_VALUES_PER_AXIS",
    "SOURCE_DECLARED",
    "SOURCE_DEFAULT",
    "SOURCE_MEASURED",
    "SpaceCell",
    "axis_values",
    "declared_space",
    "declared_values",
    "grid_values",
    "held_axes",
    "measured_values",
    "void_reason",
]
