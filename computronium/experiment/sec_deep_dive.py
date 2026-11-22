"""S4: the deep dive the map chooses — one claim at one box (TODO95 P4/P5).

The census ranked the axes; the interaction slice measured which pair changes
together. Neither can say whether the surprising bound row — the measured cell
that sits at the bar's edge — is a defect probe or a primitive one knob away
from training. The deep dive is chosen by the map: the bound, non-swapped row
with the smallest margin over the bar becomes one factor-ready primitive.

The comparison is a 3-point ladder on the primitive's primary knob (the declared
default and its two decade neighbours), then five paired seeds of the best rung
against the primitive's own default at the matched base box. The margin is
pre-registered before the first seed, so the claim is fixed-n and cannot be
stopped early (TODO95 S4).

The claim reads the paired interval, never a seed: ``passes`` refuses a claim
whose box disagrees with the run, so a registration written for one box decides
nothing at another (TODO95 D2). A ladder whose best point is at the bar is a
capability gap — the knob is priced, not claimed — and an execution fact on any
rung or pair is a defect with its mechanism named.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Final

from computronium.acceleration.spec import axis_segment
from computronium.experiment.sec_pilot import own_knob_params
from computronium.validation.preregistration import (
    DEFAULT_ALPHA,
    PairedComparison,
    ThresholdRegistration,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from computronium.experiment.schema.coordinate import Schedule

__all__ = [
    "CLAIM_SEEDS",
    "LADDER_FACTORS",
    "LADDER_KNOBS",
    "MARGIN",
    "DeepDive",
    "DeepDiveCandidate",
    "LadderRung",
    "PairedCell",
    "best_rung",
    "candidate_box",
    "claim_verdict",
    "ladder_points",
    "load_registration",
    "preregister",
    "primary_knob",
    "select_candidate",
    "tuning_candidates",
]

#: The ladder's three points, as factors of the knob's declared default. A rung
#: that the validator refuses is a row with its trigger, never a hidden point.
LADDER_FACTORS: Final[tuple[float, ...]] = (0.1, 1.0, 10.0)
#: Paired seeds per arm. Fixed before the first seed, so the claim is fixed-n
#: and cannot be stopped early (TODO95 S4).
CLAIM_SEEDS: Final[int] = 5
#: The smallest material effect at the accuracy ruler: one percentage point of
#: held-out samples. It is committed in the registration before the run.
MARGIN: Final[float] = 0.01
#: The primary knob of a deep dive, per axis, in preference order: the first
#: declared numeric knob of the primitive's own config is the one laddered. The
#: declaration names the knob; the default value stays the config classmethod's.
LADDER_KNOBS: Final[Mapping[str, tuple[str, ...]]] = MappingProxyType({
    "credit": (
        "feedback_scale",
        "beta",
        "readout_scale",
        "fd_step",
        "estimator_samples",
        "aux_head_scale",
        "lr",
    ),
    "dynamics": ("step_size", "max_steps"),
    "geometry": ("hidden_dim", "depth", "width"),
    "update": ("step_size", "momentum"),
    "plasticity": ("trace_decay",),
    "substrate": ("noise_level", "sparsity"),
})


def _val_acc(row: Mapping[str, Any]) -> float | None:
    value = (row.get("measurement") or {}).get("val_acc")
    return None if value is None else float(value)


def primary_knob(axis: str, primitive: str) -> tuple[str, float] | None:
    """The primitive's primary knob and its declared default, or ``None``.

    The knob is the first name in :data:`LADDER_KNOBS` that the primitive's own
    config classmethod declares as a positive number. A primitive with no such
    knob has no ladder and is not a deep dive: it is not factor-ready here.
    """
    params = own_knob_params(axis, primitive)
    for name in LADDER_KNOBS.get(axis, ()):
        key = f"{axis}.{name}"
        value = params.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        if value > 0:
            return key, float(value)
    return None


@dataclass(frozen=True, slots=True)
class DeepDiveCandidate:
    """The surprising bound row: the cell the map sends to a deep dive."""

    primitive: str
    axis: str
    level: str
    val_acc: float
    margin: float
    knob: str
    default: float
    #: The row's screened box: its six axes, its structural params and the
    #: schedule. The pair's arms rebuild from it, so a row screened before
    #: the box carried its params has no dive (TODO97 S9c).
    box: dict[str, Any]
    walltime_s: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _bound_candidate(
    primitive: str, row: Mapping[str, Any], bar: float
) -> DeepDiveCandidate | None:
    """One knobbed bound row above the bar, or ``None`` when it is not one.

    A row that refused, swapped, went inert, or measured at the bar is not a
    candidate: the bar already decided it, or the row re-measures the control.
    """
    if row.get("status") != "measured" or row.get("swapped"):
        return None
    if row.get("binding") != "bound":
        return None
    val_acc = _val_acc(row)
    if val_acc is None or val_acc <= bar:
        return None
    axis = axis_segment(str(row.get("axis", "")))
    level = primitive.rsplit(".", 1)[-1]
    knob = primary_knob(axis, level)
    if knob is None:
        return None
    return DeepDiveCandidate(
        primitive=primitive,
        axis=axis,
        level=level,
        val_acc=val_acc,
        margin=val_acc - bar,
        knob=knob[0],
        default=knob[1],
        box=dict(row.get("box") or {}),
        walltime_s=(row.get("resource") or {}).get("walltime_s"),
    )


def _bound_candidates(map_data: Mapping[str, Any]) -> list[DeepDiveCandidate]:
    bar = (map_data.get("inventory") or {}).get("bar")
    if bar is None:
        return []
    return [
        candidate
        for primitive, row in (map_data.get("primitives") or {}).items()
        if (candidate := _bound_candidate(str(primitive), row, float(bar))) is not None
    ]


def select_candidate(map_data: Mapping[str, Any]) -> DeepDiveCandidate | None:
    """The bound row with the smallest margin over the bar, with a knob.

    The map's ranking is the selection, never a second table (TODO95 P4).
    """
    rows = _bound_candidates(map_data)
    if not rows:
        return None
    return min(rows, key=lambda candidate: (candidate.margin, candidate.primitive))


def tuning_candidates(
    map_data: Mapping[str, Any], limit: int | None = 2
) -> tuple[DeepDiveCandidate, ...]:
    """The rows S9 ladders for the claim list: the largest margin over the bar.

    Walltime does not rank them: a cheap row and a costly row are compared by
    the margin their own family bar leaves, so the two added ladders are the
    rows with the most headroom (TODO97 S9). The base axis's own value
    re-measures the family's control, so it is not a tuning candidate.
    """
    base = map_data.get("base") or {}
    primitives = map_data.get("primitives") or {}
    rows = [
        candidate
        for candidate in _bound_candidates(map_data)
        if (primitives[candidate.primitive].get("box") or {}).get(candidate.axis)
        != base.get(candidate.axis)
    ]
    rows.sort(key=lambda candidate: (-candidate.margin, candidate.primitive))
    return tuple(rows if limit is None else rows[:limit])


def ladder_points(candidate: DeepDiveCandidate) -> tuple[tuple[float, float], ...]:
    """The three ladder points: each factor and the knob value it declares."""
    return tuple((factor, candidate.default * factor) for factor in LADDER_FACTORS)


@dataclass(frozen=True, slots=True)
class LadderRung:
    """One point of the ladder: its knob value, number and box."""

    factor: float
    value: float
    status: str  # measured | refused | defect
    val_acc: float | None
    walltime_s: float | None
    replay_hash: str | None
    box: dict[str, Any]
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PairedCell:
    """One arm of the paired comparison: its seed, number and replay hash."""

    arm: str  # treatment | control
    factor: float
    seed: int
    status: str
    val_acc: float | None
    loss: float | None
    walltime_s: float | None
    replay_hash: str | None
    box: dict[str, Any]
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DeepDive:
    """The record: the candidate, the ladder, the pair and the verdict."""

    candidate: DeepDiveCandidate
    rungs: tuple[LadderRung, ...]
    best: LadderRung | None
    cells: tuple[PairedCell, ...]
    paired: dict[str, Any] | None
    claim: dict[str, Any]
    verdict: str  # claim | coordinate | defect
    stop_reason: str
    walltime_s: float | None
    #: Whether the ladder moved the number: an inert knob is a capability gap,
    #: not a result about the axis (TODO95 D8).
    knob_binds: bool
    #: Whether the pair could carry error control. Identical arms measure a
    #: structurally zero difference, so the pair is marked, not reported.
    no_power: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate": self.candidate.to_dict(),
            "ladder": [rung.to_dict() for rung in self.rungs],
            "best": None if self.best is None else self.best.to_dict(),
            "cells": [cell.to_dict() for cell in self.cells],
            "effect": self.paired,
            "claim": self.claim,
            "verdict": self.verdict,
            "stop_reason": self.stop_reason,
            "walltime_s": self.walltime_s,
            "knob_binds": self.knob_binds,
            "no_power": self.no_power,
        }


def best_rung(rungs: tuple[LadderRung, ...]) -> LadderRung | None:
    """The measured rung with the highest accuracy, or ``None`` when none ran.

    A refused or defective rung is not a point of the ladder's answer; ties go
    to the smallest factor, the point nearest the primitive's own default.
    """
    measured = [rung for rung in rungs if rung.status == "measured"]
    if not measured or any(rung.val_acc is None for rung in measured):
        return None
    return min(
        measured,
        key=lambda rung: (-(rung.val_acc or 0.0), rung.factor),
    )


def candidate_box(
    candidate: DeepDiveCandidate, factor: float, schedule: Schedule
) -> dict[str, Any]:
    """The box one arm trains at: the row's coordinate, its params too.

    One builder: the screen's own ``_box_summary`` reads the coordinate's six
    axes, its structural params and the schedule, so a registration and a pair
    compare the same fields (TODO97 S9c). The factor is the arm's ladder point,
    so the control arm's box is the row's own box.
    """
    from computronium.experiment.sec_loop import _box_summary, _deep_dive_coordinate

    return _box_summary(_deep_dive_coordinate(candidate, factor), schedule)


def claim_registration(
    candidate: DeepDiveCandidate, schedule: Schedule
) -> ThresholdRegistration:
    """The pre-registered threshold, written before the first paired seed.

    The box is the row's own coordinate, not the base schedule alone: a
    registration that declares a box decides only a run at that box, and a
    claim re-boxed between the ladder and the pair is refused by name
    (TODO95 D2, TODO97 S9c).
    """
    return ThresholdRegistration(
        claim=(
            f"tuning {candidate.knob} on {candidate.primitive} moves val_acc "
            f"by at least {MARGIN:.2f} at the {schedule.task_id} base"
        ),
        metric="val_acc",
        threshold=MARGIN,
        alpha=DEFAULT_ALPHA,
        min_seeds=CLAIM_SEEDS,
        created=date.today().isoformat(),
        box=candidate_box(candidate, 1.0, schedule),
    )


def preregister(
    map_data: Mapping[str, Any],
    schedule: Schedule,
    path: Path,
) -> ThresholdRegistration:
    """Register the claim the map's candidate names, before any run.

    Raises:
        ValueError: When the map sends no row to a deep dive.
    """
    candidate = select_candidate(map_data)
    if candidate is None:
        msg = "no surprising bound row with a declared knob in this map"
        raise ValueError(msg)
    registration = claim_registration(candidate, schedule)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registration.to_dict(), indent=2), encoding="utf-8")
    return registration


def load_registration(
    path: Path, box: Schedule | Mapping[str, Any]
) -> ThresholdRegistration | None:
    """The committed registration for this box, or ``None`` when it refuses.

    The box is the coordinate's own (its axes and structural params too), so a
    registration committed for another coordinate is refused before the first
    cell (TODO97 S9c). A session that cannot name its claim before its first
    cell is a budget leak: the run refuses instead of comparing five
    unregistered seeds.
    """
    if not path.exists():
        return None
    registration = ThresholdRegistration.load(path)
    if registration.metric != "val_acc":
        return None
    if registration.box_mismatch(box) is not None:
        return None
    return registration


def claim_verdict(
    paired: PairedComparison | None,
    registration: ThresholdRegistration,
    box: Schedule | Mapping[str, Any],
) -> str:
    """The claim when the paired CI clears the registered margin, else a row.

    ``passes`` refuses a claim at another box and a CI that includes the
    margin: the pair is then a coordinate about the knob, not a verdict. The box
    is the coordinate's own (its axes and structural params), not the schedule
    alone, so the registration and the run compare the same fields (TODO97 S9c).
    """
    if paired is None:
        return "coordinate"
    return "claim" if paired.passes(registration, box=box) else "coordinate"


def main() -> None:
    """Pre-register the deep dive claim, before the first cell is run.

    Run:
        uv run python -m computronium.experiment.sec_deep_dive \
            --map results/sec/map.json --out configs/preregistrations/sec_deep_dive.json
    """
    import argparse

    from computronium.experiment.sec_loop import base_schedule

    parser = argparse.ArgumentParser(
        description="SEC S4 - pre-register the deep dive claim"
    )
    parser.add_argument(
        "--map", type=Path, default=Path("results/sec/map.json"), help="Map document"
    )
    parser.add_argument("--out", type=Path, required=True, help="Registration file")
    args = parser.parse_args()

    map_data = json.loads(args.map.read_text())
    task_id = str((map_data.get("base") or {}).get("task") or "mnist")
    schedule = base_schedule(task_id, "auto")
    if schedule is None:
        msg = f"{task_id} declares no base box; the claim is refused"
        raise SystemExit(msg)
    registration = preregister(map_data, schedule, args.out)
    print(f"Claim registered: {registration.claim}")
    print(
        f"  margin {registration.threshold}, alpha {registration.alpha}, "
        f"n_max {registration.min_seeds} -> {args.out}"
    )


if __name__ == "__main__":
    main()
