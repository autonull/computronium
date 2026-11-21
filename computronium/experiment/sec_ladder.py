"""S6b: one ladder per near-chance bound row, recorded in the map.

A near-chance row is a measurement, not a verdict: it says the primitive ran
at the base box, not that the primitive cannot train. The ladder decides that
question at the primitive's own declared knob -- three points, one seed each,
then one confirmation seed at the best point (TODO97 §4.2). A best point clear
of the near-chance band is a coordinate; a best point inside the band is
``unimplemented`` with a failing test and the primitive that would close it.

The record is one row of the map's ``ladders`` table, written beside the
number it adjudicates. It carries the rungs, the best point, the cost, the
verdict and a replay hash, so a map row is never published without its box.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Final, Literal

from computronium.experiment.sec_deep_dive import LADDER_FACTORS, LADDER_KNOBS

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping

    from computronium.experiment.kernel.evaluate import CellEvaluation
    from computronium.experiment.schema.coordinate import Schedule

__all__ = [
    "CONFIRM_SEED",
    "LADDER_SEED",
    "NEAR_CHANCE_FACTOR",
    "PRIMARY_KNOBS",
    "VERDICTS",
    "LadderRecord",
    "LadderRung",
    "chance_of",
    "ladder_rows",
    "main",
    "map_findings",
    "record_problems",
    "replay_hash",
    "run_ladder",
    "tuning_rows",
]

#: The ladder's seed; the confirmation seed is one step past it. One seed per
#: rung is a screen, not a control: the pair at the best point is the control.
LADDER_SEED: Final[int] = 0
CONFIRM_SEED: Final[int] = LADDER_SEED + 1
#: The near-chance band, as a multiple of the ruler's chance rate. The same
#: factor is the audit's near-chance predicate: one ruler, not two tables.
NEAR_CHANCE_FACTOR: Final[float] = 2.0

Verdict = Literal["tuned", "unimplemented", "defective"]
VERDICTS: Final[frozenset[str]] = frozenset({"tuned", "unimplemented", "defective"})

_AXIS: Final[str] = "credit"
_TASK: Final[str] = "mnist"

#: The plan's triage (§4.2), as data the record carries: the mechanism a
#: near-chance ladder names when it does not clear the band. It is not
#: re-derived from the numbers -- a low cell names its defect, never a verdict.
_TRIAGE: Final[Mapping[str, str]] = {
    "primitive.credit_assignment.forward_tangent": (
        "the forward-mode estimator declares no JVP scale: estimator_samples "
        "is a topology parameter, and its feedback_scale knob does not bind"
    ),
    "primitive.credit_assignment.local_contrastive": (
        "the label channel the contrast reads is not carried through the "
        "instantaneous settle"
    ),
    "primitive.credit_assignment.pc_alm": (
        "the dual-variable settle that produces lambda is not composed with "
        "instantaneous dynamics"
    ),
    "primitive.credit_assignment.random_projections": (
        "a feedback width and parameter budget the base box can reach"
    ),
    "primitive.credit_assignment.target_inversion": (
        "transpose feedback vanishes on vision: needs feedback alignment "
        "(a random B) or a learned inverse"
    ),
    "primitive.geometry.conv": (
        "no ladder point clears the near-chance band: the conv path does not "
        "train at the vision box (close: a conv-specific credit path or a "
        "wider box)"
    ),
    "primitive.state_dynamics.error_predictive_coding": (
        "no ladder point clears the near-chance band: the target/error channel "
        "the settle reads is not carried through the vision step (close: the "
        "error-prediction primitive on this geometry)"
    ),
    "primitive.parameter_update.quantized_adam": (
        "the quantized update state carries no step at the base box: the best "
        "rung is at chance (close: a quantization scale that preserves the "
        "step, or a declared block size)"
    ),
}


#: A ladder point that crashes at the primitive's own box is a defect, and a
#: defect names the lock that fails today and the capability that closes it.
#: Measured 2026-11-20 (S9b): ``pc_alm``'s ×10 step diverged at settle step 6.
_DEFECT_LOCKS: Final[Mapping[str, tuple[str, str]]] = MappingProxyType({
    "primitive.state_dynamics.pc_alm": (
        "tests/property/test_ladder_record_lock.py"
        "::test_a_pc_alm_step_above_its_stability_bound_trains",
        "the ALM settle diverges at a step above its stability bound: close "
        "with a backtracking step or a declared stability ceiling, then re-run "
        "the ladder",
    ),
})

#: Each near-chance primitive's primary knob (TODO97 §4.2), in preference
#: order. A name the primitive's active space does not declare is skipped: a
#: missing knob is the record's close condition, not a fallback to another one.
PRIMARY_KNOBS: Final[Mapping[str, tuple[str, ...]]] = MappingProxyType({
    "primitive.credit_assignment.forward_tangent": ("feedback_scale", "feedback_lr"),
    "primitive.credit_assignment.local_contrastive": ("readout_scale",),
    "primitive.credit_assignment.pc_alm": ("beta",),
    "primitive.credit_assignment.random_projections": ("feedback_scale",),
    "primitive.credit_assignment.target_inversion": ("feedback_scale",),
    "primitive.geometry.conv": ("hidden_dim", "depth"),
    "primitive.state_dynamics.error_predictive_coding": ("beta", "step_size"),
})


def chance_of(ruler: str) -> float | None:
    """The ruler's declared chance rate, or ``None`` when it declares none."""
    marker = "chance "
    if marker not in ruler:
        return None
    try:
        return float(ruler.split(marker, 1)[1].split()[0].strip(",)"))
    except IndexError, ValueError:
        return None


def near_chance_band(chance: float) -> float:
    """The band a ladder point must clear to be a coordinate."""
    return NEAR_CHANCE_FACTOR * chance


@dataclass(frozen=True, slots=True)
class LadderRung:
    """One point of the ladder: its factor, its knob value and its number."""

    factor: float
    value: float
    status: Literal["measured", "refused", "crashed"]
    val_acc: float | None
    walltime_s: float | None
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class LadderRecord:
    """The record: the candidate, the rungs, the pair and the verdict."""

    primitive: str
    axis: str
    task: str
    knob: str | None
    default: float | None
    rungs: tuple[LadderRung, ...]
    confirm: LadderRung | None
    best: LadderRung | None
    verdict: Verdict
    reason: str | None
    failing_test: str | None
    close_condition: str | None
    runs: int
    walltime_s: float

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "primitive": self.primitive,
            "axis": self.axis,
            "task": self.task,
            "knob": self.knob,
            "default": self.default,
            "rungs": [rung.to_dict() for rung in self.rungs],
            "confirm": None if self.confirm is None else self.confirm.to_dict(),
            "best": None if self.best is None else self.best.to_dict(),
            "verdict": self.verdict,
            "reason": self.reason,
            "failing_test": self.failing_test,
            "close_condition": self.close_condition,
            "runs": self.runs,
            "walltime_s": self.walltime_s,
        }
        data["replay"] = replay_hash(data)
        return data


@dataclass(frozen=True, slots=True)
class _Measured:
    """One ladder's points and its triage, before the record is built."""

    rungs: tuple[LadderRung, ...]
    confirm: LadderRung | None
    best: LadderRung | None
    verdict: Verdict
    reason: str | None
    close: str | None
    walltime_s: float


def replay_hash(record: Mapping[str, Any]) -> str:
    """The numbers' identity: a changed rung changes the hash."""
    payload = {
        key: record.get(key)
        for key in (
            "primitive",
            "axis",
            "task",
            "knob",
            "default",
            "rungs",
            "confirm",
            "best",
            "verdict",
        )
    }
    return hashlib.blake2b(
        json.dumps(payload, sort_keys=True, default=str).encode(),
        digest_size=8,
    ).hexdigest()


def failing_test(primitive: str) -> str:
    """The lock test a non-tuned verdict leaves failing (strict xfail)."""
    lock = _DEFECT_LOCKS.get(primitive)
    if lock is not None:
        return lock[0]
    return (
        "tests/property/test_ladder_record_lock.py"
        f"::test_an_unimplemented_ladder_clears_its_band[{primitive}]"
    )


def ladder_rows(
    document: Mapping[str, Any],
) -> list[tuple[str, Mapping[str, Any], float]]:
    """Every bound row inside the near-chance band, with its chance rate.

    The family's own base coordinate is the control, not a candidate: the
    calibration measured it over ``CONTROL_SEEDS`` and the map carries that
    mean in ``inventory``. A screen that swaps an axis back to the box's own
    value (``credit=gradient`` on vision) re-measures the control, so asking it
    for a ladder would adjudicate a number the control already decides.
    """
    base = document.get("base") or {}
    rows: list[tuple[str, Mapping[str, Any], float]] = []
    for spec_id, row in (document.get("primitives") or {}).items():
        if row.get("binding") != "bound":
            continue
        axis = row.get("axis")
        box = row.get("box") or {}
        if axis and box.get(axis) == base.get(axis):
            continue
        value = (row.get("measurement") or {}).get("val_acc")
        chance = chance_of(str(row.get("ruler", "")))
        if value is None or chance is None:
            continue
        if float(value) > near_chance_band(chance):
            continue
        rows.append((str(spec_id), row, chance))
    return rows


def tuning_rows(
    document: Mapping[str, Any], limit: int | None = 2
) -> list[tuple[str, Mapping[str, Any], float]]:
    """The above-bar rows S9 ladders for the claim list.

    The rows are the map's own ranking (``tuning_candidates``): the largest
    margin over the family bar, walltime aside. A row's chance rate is its
    ruler's, not the tabular default, so the band the ladder must clear is
    the band its family declares.
    """
    from computronium.experiment.sec_deep_dive import tuning_candidates

    primitives = document.get("primitives") or {}
    rows: list[tuple[str, Mapping[str, Any], float]] = []
    for candidate in tuning_candidates(document, limit):
        row = primitives[candidate.primitive]
        chance = chance_of(str(row.get("ruler", "")))
        if chance is not None:
            rows.append((candidate.primitive, row, chance))
    return rows


def map_findings(document: Mapping[str, Any]) -> list[str]:
    """Every near-chance row's record problems, each naming its primitive."""
    ladders = document.get("ladders") or {}
    findings: list[str] = []
    for spec_id, _row, _chance in ladder_rows(document):
        findings += [
            f"{spec_id} {problem}"
            for problem in record_problems(spec_id, ladders.get(spec_id))
        ]
    return findings


def record_problems(spec_id: str, record: Mapping[str, Any] | None) -> list[str]:
    """What a ladder record must carry, and what it is missing.

    A record is ``tuned`` (a coordinate), ``unimplemented`` (a failing test and
    the primitive that closes it), or ``defective`` (the mechanism, named). A
    no-knob record is unimplemented with the close condition; it cannot claim
    a rung it did not run.
    """
    if not record:
        return ["no ladder record"]
    verdict = record.get("verdict")
    problems = _header_problems(spec_id, record)
    problems += _run_problems(record, verdict)
    problems += _verdict_problems(record, verdict)
    return problems


def _header_problems(spec_id: str, record: Mapping[str, Any]) -> list[str]:
    problems: list[str] = []
    if record.get("primitive") != spec_id:
        problems.append("record names another primitive")
    if record.get("axis") != spec_axis(spec_id):
        problems.append(
            f"record axis {record.get('axis')!r} is not {spec_axis(spec_id)}"
        )
    if record.get("verdict") not in VERDICTS:
        problems.append(f"verdict {record.get('verdict')!r} is not declared")
    if record.get("replay") != replay_hash(record):
        problems.append("replay hash does not match the numbers")
    return problems


def _run_problems(record: Mapping[str, Any], verdict: object) -> list[str]:
    runs = record.get("runs")
    if not isinstance(runs, int) or isinstance(runs, bool) or runs < 0:
        return [f"runs {runs!r} is not a count"]
    problems: list[str] = []
    walltime = record.get("walltime_s")
    if not isinstance(walltime, int | float) or isinstance(walltime, bool):
        problems.append(f"walltime {walltime!r} is not a cost")
    rungs = record.get("rungs")
    if runs == 0:
        if verdict != "unimplemented":
            problems.append("no rung ran and the verdict is not unimplemented")
        return problems
    if not isinstance(rungs, list) or len(rungs) < 2:
        problems.append(f"runs={runs} but the ladder carries {rungs!r}")
        return problems
    expected = len(rungs) + (1 if record.get("confirm") else 0)
    if runs != expected:
        problems.append(f"runs={runs} but {expected} point(s) are recorded")
    if verdict == "tuned" and record.get("best") is None:
        problems.append("tuned without a best point")
    return problems


def _verdict_problems(record: Mapping[str, Any], verdict: object) -> list[str]:
    problems: list[str] = []
    if verdict == "unimplemented":
        if not record.get("failing_test"):
            problems.append("unimplemented without a failing test")
        if not record.get("close_condition"):
            problems.append("unimplemented without a close condition")
    if verdict == "defective":
        if not record.get("failing_test"):
            problems.append("defective without a failing test")
        if not record.get("reason"):
            problems.append("defective without the named mechanism")
    return problems


def _run_point(
    evaluate: Callable[[Any, Schedule], CellEvaluation],
    coordinate: Any,
    schedule: Schedule,
    factor: float,
    value: float,
    seed: int,
) -> LadderRung:
    """One rung: the coordinate at the seed, or the execution fact it raised."""
    from computronium.experiment.sec_loop import _is_legal

    legal, refusal = _is_legal(coordinate, schedule.task_id)
    if not legal:
        # The declared space refuses the box: a ladder point that cannot
        # exist is refused by name, never trained around the rule. Measured
        # 2026-11-20: the tile record's illegal box trained and published a
        # false coordinate.
        return LadderRung(factor, value, "refused", None, 0.0, refusal)
    started = time.perf_counter()
    try:
        evaluation = evaluate(coordinate, replace(schedule, seed=seed, n_seeds=1))
    except ValueError as exc:
        # The declared space refuses the box: a rung that cannot exist is
        # not a crash, and it is not a point of the ladder either.
        return LadderRung(
            factor,
            value,
            "refused",
            None,
            time.perf_counter() - started,
            f"{type(exc).__name__}: {exc}",
        )
    except Exception as exc:  # ruff: ignore[blind-except] - the ladder records it
        return LadderRung(
            factor,
            value,
            "crashed",
            None,
            time.perf_counter() - started,
            f"{type(exc).__name__}: {exc}",
        )
    acc = evaluation.metrics.get("val_acc")
    if acc is None or not math.isfinite(float(acc)):
        return LadderRung(
            factor,
            value,
            "refused",
            None,
            evaluation.walltime_s,
            "no finite val_acc",
        )
    return LadderRung(factor, value, "measured", float(acc), evaluation.walltime_s)


def ladder_knob(spec_id: str, base: Any, axis: str = _AXIS) -> tuple[str, float] | None:
    """The primitive's primary active numeric knob and its default.

    The active space is the one declaration of which knobs a coordinate can
    carry: a factory signature names nothing a swept value reaches (D13). The
    axis is the primitive's own: a dynamics row ladders a dynamics knob, not a
    credit one (measured 2026-11-20: the credit-only ladder recorded conv and
    error_predictive_coding as "no point trained").
    """
    from computronium.experiment.kernel.compose import harvest_schema
    from computronium.experiment.schema.axis import StructuralAxis

    names = PRIMARY_KNOBS.get(spec_id, LADDER_KNOBS[axis])
    values = harvest_schema().active(base).values_for_axis(StructuralAxis(axis))
    for name in names:
        value = values.get(name)
        if isinstance(value, float) and not isinstance(value, bool) and value > 0:
            return f"{axis}.{name}", value
    return None


def spec_axis(spec_id: str) -> str:
    """The runtime axis a primitive id selects (``primitive.<axis>.<name>``)."""
    from computronium.acceleration.spec import axis_segment

    return axis_segment(spec_id.split(".")[1])


def _best(rungs: Iterable[LadderRung]) -> LadderRung | None:
    """The highest measured rung; a tie goes to the point nearest the default.

    A tie is not a change: picking the farthest factor would publish a
    ``tuned`` record whose knob never moved the number (measured 2026-11-20:
    ``thermodynamic_contrast`` and ``local_goodness`` tied at all three points,
    and the smallest factor was read as the best).
    """
    measured = [
        rung for rung in rungs if rung.status == "measured" and rung.val_acc is not None
    ]
    if not measured:
        return None
    return min(
        measured,
        key=lambda rung: (
            -(rung.val_acc or 0.0),
            abs(math.log10(rung.factor)) if rung.factor > 0 else math.inf,
        ),
    )


def _unimplemented(
    spec_id: str,
    *,
    best: float | None,
    band: float,
    reason: str,
) -> tuple[str, str]:
    """The verdict's close condition, with the primitive that closes it."""
    note = _TRIAGE.get(spec_id, "the primitive's own missing capability")
    if best is None:
        return reason, f"{note}; no ladder point trained"
    return (
        reason,
        f"{note}; best {best:.3f} is inside the near-chance band {band:.3f}",
    )


def run_ladder(
    spec_id: str,
    row: Mapping[str, Any],
    chance: float,
    *,
    evaluate: Callable[[Any, Schedule], CellEvaluation] | None = None,
    schedule: Schedule | None = None,
) -> LadderRecord:
    """Run the primitive's 3-point ladder and one confirmation seed.

    The ladder points are the primitive's own declared knob times
    ``LADDER_FACTORS``. A primitive with no numeric knob runs no rung: it is
    ``unimplemented`` with the knob it would need, not a quiet cell.
    """
    runner, sched, base = _ladder_setup(spec_id, row, evaluate, schedule)
    task = str(row.get("task") or _TASK)
    axis = spec_axis(spec_id)
    band = near_chance_band(chance)
    knob = ladder_knob(spec_id, base, axis)
    if knob is None:
        return _no_knob_record(spec_id, task, band, axis)
    key, default = knob
    measured = _measure(runner, base, sched, key, default, spec_id, band)
    return LadderRecord(
        primitive=spec_id,
        axis=axis,
        task=task,
        knob=key,
        default=default,
        rungs=measured.rungs,
        confirm=measured.confirm,
        best=measured.best,
        verdict=measured.verdict,
        reason=measured.reason,
        failing_test=(None if measured.verdict == "tuned" else failing_test(spec_id)),
        close_condition=measured.close,
        runs=len(measured.rungs) + (1 if measured.confirm is not None else 0),
        walltime_s=measured.walltime_s,
    )


def _measure(
    runner: Callable[[Any, Schedule], CellEvaluation],
    base: Any,
    schedule: Schedule,
    key: str,
    default: float,
    spec_id: str,
    band: float,
) -> _Measured:
    """Run the rungs and the confirmation, then triage the result."""
    started = time.perf_counter()
    rungs = _run_rungs(runner, base, schedule, key, default)
    best = _best(rungs)
    confirm = (
        None
        if best is None
        else _run_point(
            runner,
            replace(base, params={**base.params, key: best.value}),
            schedule,
            1.0,
            best.value,
            CONFIRM_SEED,
        )
    )
    walltime = time.perf_counter() - started
    verdict, reason, close = _triage(spec_id, rungs, confirm, band)
    return _Measured(rungs, confirm, best, verdict, reason, close, walltime)


def _ladder_setup(
    spec_id: str,
    row: Mapping[str, Any],
    evaluate: Callable[[Any, Schedule], CellEvaluation] | None,
    schedule: Schedule | None,
) -> tuple[Callable[[Any, Schedule], CellEvaluation], Schedule, Any]:
    """The row's own box as the ladder's base, with its companions.

    The screen found a compose-legal box for the primitive (it swapped a
    companion when the base box refused). The ladder starts from that box, and
    the box is rebuilt by the screen's own builder (:func:`screen_coordinate`),
    so the factor-1.0 rung is the row's measurement and not another box
    (TODO97 S9b: the axes alone dropped the base's structural params).
    """
    from computronium.experiment.kernel.evaluate import evaluate_cell
    from computronium.experiment.sec_loop import screen_coordinate
    from computronium.experiment.sec_pilot import base_schedule

    task = str(row.get("task") or _TASK)
    sched = schedule or base_schedule(task)
    if sched is None:
        raise ValueError(f"{task}: no base schedule for the ladder")
    axis = spec_axis(spec_id)
    base = screen_coordinate(row.get("box") or {}, axis, spec_id.rsplit(".", 1)[-1])
    return evaluate or evaluate_cell, sched, base


def _run_rungs(
    runner: Callable[[Any, Schedule], CellEvaluation],
    base: Any,
    schedule: Schedule,
    key: str,
    default: float,
) -> tuple[LadderRung, ...]:
    return tuple(
        _run_point(
            runner,
            replace(base, params={**base.params, key: default * factor}),
            schedule,
            factor,
            default * factor,
            LADDER_SEED,
        )
        for factor in LADDER_FACTORS
    )


def _no_knob_record(
    spec_id: str, task: str, band: float, axis: str = _AXIS
) -> LadderRecord:
    reason, close = _unimplemented(
        spec_id,
        best=None,
        band=band,
        reason="the primitive declares no numeric ladder knob",
    )
    return LadderRecord(
        primitive=spec_id,
        axis=axis,
        task=task,
        knob=None,
        default=None,
        rungs=(),
        confirm=None,
        best=None,
        verdict="unimplemented",
        reason=reason,
        failing_test=failing_test(spec_id),
        close_condition=close,
        runs=0,
        walltime_s=0.0,
    )


def _triage(
    spec_id: str,
    rungs: tuple[LadderRung, ...],
    confirm: LadderRung | None,
    band: float,
) -> tuple[Verdict, str | None, str | None]:
    """The ladder's verdict: a coordinate, a closing condition, or a defect."""
    crashed = [rung for rung in rungs if rung.status == "crashed"]
    measured = [rung for rung in rungs if rung.status == "measured"]
    if crashed:
        lock = _DEFECT_LOCKS.get(spec_id)
        return (
            "defective",
            crashed[0].reason or "a ladder point crashed",
            lock[1] if lock is not None else None,
        )
    if not measured:
        reason, close = _unimplemented(
            spec_id,
            best=None,
            band=band,
            reason="no ladder point trained",
        )
        return "unimplemented", reason, close
    top = max(rung.val_acc or 0.0 for rung in measured)
    if confirm is not None and confirm.status == "measured":
        top = max(top, confirm.val_acc or 0.0)
    if top > band:
        return "tuned", None, None
    reason, close = _unimplemented(
        spec_id,
        best=top,
        band=band,
        reason="the ladder found no point clear of the near-chance band",
    )
    return "unimplemented", reason, close


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--map", type=Path, default=Path("results/sec/map.json"), help="Map document"
    )
    parser.add_argument(
        "--out", type=Path, default=None, help="Output (default: the map)"
    )
    parser.add_argument(
        "--only",
        action="append",
        help="Ladder only this primitive (repeatable; default: every row)",
    )
    parser.add_argument(
        "--tuning",
        action="store_true",
        help="Also ladder the map's largest-margin bound rows (S9)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=2,
        help="How many tuning rows --tuning adds (default: 2)",
    )
    parser.add_argument("--device", default="auto", help="Run device for the box")
    parser.add_argument("--dry-run", action="store_true", help="Print, do not write")
    args = parser.parse_args(argv)

    document = json.loads(args.map.read_text(encoding="utf-8"))
    out = args.out or args.map
    rows = ladder_rows(document)
    if args.tuning:
        seen = {spec_id for spec_id, *_ in rows}
        rows += [row for row in tuning_rows(document, args.limit) if row[0] not in seen]
    rows = [
        (spec_id, row, chance)
        for spec_id, row, chance in rows
        if not args.only or spec_id in args.only
    ]
    if args.dry_run:
        for spec_id, *_ in rows:
            print(f"ladder {spec_id}")
        return 0
    records: dict[str, dict[str, Any]] = {}
    from computronium.experiment.sec_pilot import base_schedule

    for spec_id, row, chance in rows:
        print(f"ladder {spec_id}", flush=True)
        schedule = base_schedule(str(row.get("task") or _TASK), args.device)
        record = run_ladder(spec_id, row, chance, schedule=schedule)
        records[spec_id] = record.to_dict()
        best = record.best.val_acc if record.best else None
        print(
            f"  {record.verdict}: best={best} runs={record.runs} "
            f"{record.walltime_s:.1f}s",
            flush=True,
        )
        print(f"  {record.close_condition or 'a coordinate'}", flush=True)
    document.setdefault("ladders", {}).update(records)
    document["updated"] = datetime.now(UTC).isoformat()
    out.write_text(json.dumps(document, indent=2, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
