"""Binding conditions: what must be true for an axis to act in a cell.

TODO95 P0.75. An axis whose condition is unmet is **inert**: the cell measures
the companions, not the varied primitive. The condition is declared once, here,
so the map labels what a box can see instead of recording every row as a result.

A condition is met by the box, not by the primitive: a substrate needs a
substrate-sensitive ruler, a credit needs a label channel, an update needs its
own declared step, a dynamics needs a settle, a plasticity needs a ψ lifecycle,
a geometry needs a layer/cell/graph form (which every composed cell has).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from computronium.experiment.schema.axis import StructuralAxis

__all__ = ["BINDING_CONDITIONS", "BindingCondition", "binding_reason"]


@dataclass(frozen=True, slots=True)
class BindingCondition:
    """What a box must carry for one axis to act, and the names that never act."""

    axis: StructuralAxis
    requires: str
    #: Primitive names whose contract is "do nothing on this axis" at any box.
    inert_names: frozenset[str] = frozenset()


BINDING_CONDITIONS: Final[dict[StructuralAxis, BindingCondition]] = {
    StructuralAxis.SUBSTRATE: BindingCondition(
        axis=StructuralAxis.SUBSTRATE,
        requires=(
            "a substrate-sensitive ruler (bit width, energy, spike timing), "
            "not accuracy alone"
        ),
    ),
    StructuralAxis.GEOMETRY: BindingCondition(
        axis=StructuralAxis.GEOMETRY,
        requires="a layer/cell/graph form the task's input shape can occupy",
    ),
    StructuralAxis.DYNAMICS: BindingCondition(
        axis=StructuralAxis.DYNAMICS,
        requires="a settle the cell actually runs",
        inert_names=frozenset({"instantaneous"}),
    ),
    StructuralAxis.PLASTICITY: BindingCondition(
        axis=StructuralAxis.PLASTICITY,
        requires="a ψ lifecycle the train step evolves",
        inert_names=frozenset({"null"}),
    ),
    StructuralAxis.CREDIT: BindingCondition(
        axis=StructuralAxis.CREDIT,
        requires="a label channel the credit reads",
    ),
    StructuralAxis.UPDATE: BindingCondition(
        axis=StructuralAxis.UPDATE,
        requires="the update's own declared step size",
    ),
}


def binding_reason(
    axis: str,
    name: str,
    *,
    criterion: str,
    own_knobs: bool,
) -> str | None:
    """Why this axis is inert in this box, or ``None`` when it binds.

    Args:
        axis: Runtime axis segment (``substrate``, ``credit``, ...).
        name: The varied primitive's runtime coordinate.
        criterion: The ruler's metric key, e.g. ``"val_acc"``.
        own_knobs: Whether the varied primitive ran at its declared defaults.

    Returns:
        The reason the slice is inert, or ``None`` when the condition is met.
    """
    try:
        axis_kind = StructuralAxis(axis)
    except ValueError:
        return None
    condition = BINDING_CONDITIONS[axis_kind]
    if name in condition.inert_names:
        return f"`{name}` has no {condition.requires}"
    match axis_kind:
        case StructuralAxis.SUBSTRATE:
            if criterion == "val_acc":
                return (
                    f"the box reads {criterion}; a substrate needs {condition.requires}"
                )
        case StructuralAxis.CREDIT:
            from computronium.core.system_trainer.spec import error_blind_credit

            if error_blind_credit(name):
                return f"`{name}` reads no label; a credit needs {condition.requires}"
        case StructuralAxis.UPDATE:
            if not own_knobs:
                return f"the box shares one step size; an update needs {condition.requires}"
    return None
