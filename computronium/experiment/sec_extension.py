"""P5: the extension path — one scanner, any primitive, one map row (TODO95 P5).

A stranger adds a credit and must hold a map row without reading internals. The
scanner reads only the published document: the row, its box, ruler, control,
replay hash and the slice family's declared base. It never composes a config and
never trains, so the recipe in ``docs/sec/map.md`` is the recipe a contributor
runs — and ``comp verify`` is that recipe as a check.

A slice with no declared base box is refused before it is priced; a measured row
without its box, ruler, control or replay hash cannot be compared or reproduced;
and a row screened on another family is not a row in this slice. ``unmeasured``
is a held row with no result, never a missing row (TODO95 D1).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from computronium.experiment.sec_census import MAP_VERSION
from computronium.experiment.sec_pilot import BASE_BOXES, task_family

if TYPE_CHECKING:
    from collections.abc import Mapping

__all__ = ["RowVerdict", "verify_row"]


@dataclass(frozen=True, slots=True)
class RowVerdict:
    """One primitive's map row, checked against its slice family."""

    primitive: str
    family: str
    status: str
    held: bool
    problems: tuple[str, ...]
    box: dict[str, Any]
    ruler: str | None
    control: float | None
    replay_hash: str | None
    measurement: float | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "primitive": self.primitive,
            "slice": self.family,
            "status": self.status,
            "held": self.held,
            "problems": list(self.problems),
            "box": self.box,
            "ruler": self.ruler,
            "control": self.control,
            "replay_hash": self.replay_hash,
            "measurement": self.measurement,
        }


def _val_acc(value: Any) -> float | None:
    return None if value is None else float(value)


def _slice_problems(
    map_data: Mapping[str, Any], row: Mapping[str, Any], family: str
) -> list[str]:
    """The version, the family's base box and the row's own task family."""
    problems: list[str] = []
    if map_data.get("version") != MAP_VERSION:
        problems.append(f"map version {map_data.get('version')} is not {MAP_VERSION}")
    if family not in BASE_BOXES:
        problems.append(
            f"slice {family!r} declares no base box; the slice is refused "
            "before it is priced"
        )
    task = row.get("task")
    if task is not None and task_family(str(task)) != family:
        screened = task_family(str(task)) or "an undeclared family"
        problems.append(f"row screened on {screened}, not {family}")
    return problems


def _missing(value: Any) -> bool:
    """A field the row must carry and does not (an empty string or box)."""
    return value is None or (isinstance(value, (str, dict)) and not value)


def _row_problems(row: Mapping[str, Any], status: str) -> list[str]:
    """What a row of this status must carry, and what it is missing."""
    match status:
        case "measured":
            wanted = {
                "val_acc": (row.get("measurement") or {}).get("val_acc"),
                "box": row.get("box"),
                "ruler": row.get("ruler"),
                "control": (row.get("control") or {}).get("val_acc"),
                "rule": row.get("rule"),
                "replay hash": row.get("replay_hash"),
            }
            problems = [
                f"measured row carries no {name}"
                for name, value in wanted.items()
                if _missing(value)
            ]
            if row.get("swapped"):
                problems.append("swapped row: not a comparable cell")
            return problems
        case "defect":
            problems = []
            if not row.get("defect"):
                problems.append("defect row names no mechanism")
            if not row.get("replay_hash"):
                problems.append("defect row carries no replay hash")
            return problems
        case "refused":
            return [] if row.get("trigger") else ["refused row carries no trigger"]
        case "unmeasured":
            return (
                ["unmeasured row carries a measurement"]
                if row.get("measurement")
                else []
            )
        case _:
            return [f"unknown row status {status!r}"]


def verify_row(
    map_data: Mapping[str, Any],
    primitive: str,
    family: str,
) -> RowVerdict:
    """Scan one primitive's row for a family: does it hold, and why not?

    Args:
        map_data: The published map document (the only artifact read).
        primitive: The primitive ID the row names.
        family: The task family the slice is verified in.

    Returns:
        The verdict, with every problem named; a held row has no problems.
    """
    row = (map_data.get("primitives") or {}).get(primitive)
    status = "missing" if row is None else str(row.get("status") or "unmeasured")
    problems = _slice_problems(map_data, row or {}, family)
    if row is None:
        problems.append("no map row: the census is not screened for it")
    else:
        problems += _row_problems(row, status)
    row = row or {}
    return RowVerdict(
        primitive=primitive,
        family=family,
        status=status,
        held=not problems,
        problems=tuple(problems),
        box=dict(row.get("box") or {}),
        ruler=None if row.get("ruler") is None else str(row.get("ruler")),
        control=_val_acc((row.get("control") or {}).get("val_acc")),
        replay_hash=(
            None if row.get("replay_hash") is None else str(row.get("replay_hash"))
        ),
        measurement=_val_acc((row.get("measurement") or {}).get("val_acc")),
    )
