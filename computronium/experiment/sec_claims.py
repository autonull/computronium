"""S9: the claim list — every tuned ladder record, pre-registered and paired.

The maps' ``ladders`` table names the primitives a 3-point ladder moved. Each
such record is a claim candidate: the map ranked it by the effect that must
replicate (the confirmation seed against the default rung), so the claim list
is the map's own ranking, never a second table.

A candidate's margin is committed to ``configs/preregistrations`` **before**
its first seed: one percentage point of held-out samples, or the ruler's own
resolution when that is coarser (a 30-sample split cannot resolve 1 pp). The
seed budget is :data:`CLAIM_SEEDS`, fixed before the run, so the comparison is
fixed-n and cannot be stopped early.

The run pairs five index-matched seeds of the best rung against the primitive's
own default at the matched box, then reads ``paired_comparison`` against the
committed registration. A CI that clears the margin is a claim; one that
includes it is a coordinate; a point within one standard error of the margin
is ``marginal``, never rounded up. Two arms that are identical by construction
(the ladder's best point is the default) have no power and are marked, not
run.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from dataclasses import asdict, dataclass, replace
from datetime import UTC, date, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from computronium.experiment.sec_deep_dive import (
    CLAIM_SEEDS,
    MARGIN,
    PairedCell,
    claim_verdict,
    load_registration,
)
from computronium.experiment.sec_loop import _box_summary, _measure, box_params
from computronium.validation.preregistration import (
    DEFAULT_ALPHA,
    PairedComparison,
    ThresholdRegistration,
    paired_comparison,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping

    from computronium.experiment.schema.coordinate import Coordinate, Schedule

__all__ = [
    "CLAIM_LIMIT",
    "DEFAULT_REGISTRATIONS",
    "ClaimCandidate",
    "ClaimRecord",
    "candidate_box",
    "claim_candidates",
    "default_maps",
    "margin_for",
    "register_claim",
    "registration_path",
    "run_claim",
]

#: The claim list's size: five pre-registered claims is the gate. A sixth
#: tuned record is pool depth for S9b, not a sixth claim.
CLAIM_LIMIT: Final[int] = 5

#: Where the committed registrations live. One file per candidate, written by
#: ``--register`` before ``--run`` touches a cell.
DEFAULT_REGISTRATIONS: Final[Path] = Path("configs/preregistrations")


def default_maps() -> tuple[Path, ...]:
    """Every family map, one per base task, in a stable order."""
    return tuple(sorted(Path("results").glob("sec*/map.json")))


def margin_for(task_id: str) -> float:
    """The smallest material effect at the task's ruler.

    One percentage point of accuracy, unless the held-out split is too coarse
    to resolve it: a 30-sample split moves in steps of 1/30, so its margin is
    that step, not a rounding error.
    """
    from computronium.experiment.registry.task_registry import TaskRegistry

    resolution = TaskRegistry().get(task_id).resolution
    if resolution is not None and resolution > 0:
        return max(MARGIN, 1.0 / resolution)
    return MARGIN


@dataclass(frozen=True, slots=True)
class ClaimCandidate:
    """One tuned ladder record: the primitive, its knob and the box it ran at."""

    primitive: str
    axis: str
    level: str
    task: str
    knob: str
    default: float
    best_factor: float
    best_value: float
    effect: float | None
    box: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def coordinate(self, value: float) -> Coordinate:
        """The candidate's box with its primary knob at one value.

        The box is the row's screened box, rebuilt by the screen's own builder
        (:func:`screen_coordinate`): the ladder's base params travel, so the
        two arms are the row's box, not a compose default (TODO97 S9b).
        """
        from dataclasses import replace

        from computronium.experiment.sec_loop import screen_coordinate

        base = screen_coordinate(self.box, self.axis, self.level)
        return replace(base, params={**base.params, self.knob: value})


def _candidate_from_record(
    primitive: str,
    record: Mapping[str, Any],
    row: Mapping[str, Any],
    task: str,
) -> ClaimCandidate | None:
    """One tuned record as a claim candidate, or ``None`` when it cannot claim."""
    if record.get("verdict") != "tuned":
        return None
    knob = record.get("knob")
    default = record.get("default")
    best = record.get("best") or {}
    if not isinstance(knob, str) or default is None or best.get("factor") is None:
        return None
    rungs = record.get("rungs") or []
    at_default = next(
        (rung for rung in rungs if rung.get("factor") == 1.0),
        None,
    )
    confirm = record.get("confirm") or {}
    default_val = None if at_default is None else at_default.get("val_acc")
    confirm_val = confirm.get("val_acc")
    effect = (
        None
        if default_val is None or confirm_val is None
        else float(confirm_val) - float(default_val)
    )
    return ClaimCandidate(
        primitive=primitive,
        axis=str(record.get("axis") or primitive.split(".")[1]),
        level=primitive.rsplit(".", 1)[-1],
        task=task,
        knob=knob,
        default=float(default),
        best_factor=float(best["factor"]),
        best_value=float(best.get("value", float(default))),
        effect=effect,
        box=dict(row.get("box") or {}),
    )


def claim_candidates(maps: Iterable[Path]) -> tuple[ClaimCandidate, ...]:
    """Every tuned ladder record across the maps, ranked by replicated effect.

    The ranking is the confirmation seed's difference from the default rung:
    the effect the five paired seeds must reproduce. A record without a
    confirmation seed is still a candidate; it ranks last.
    """
    candidates: list[ClaimCandidate] = []
    for path in maps:
        document = json.loads(path.read_text(encoding="utf-8"))
        task = str((document.get("base") or {}).get("task") or "")
        primitives = document.get("primitives") or {}
        for primitive, record in (document.get("ladders") or {}).items():
            row = primitives.get(primitive)
            if row is None:
                continue
            candidate = _candidate_from_record(primitive, record, row, task)
            if candidate is not None:
                candidates.append(candidate)
    # One registration per primitive: a primitive tuned on two maps keeps
    # the larger effect, never overwriting another claim's committed box.
    best_by_primitive: dict[str, ClaimCandidate] = {}
    for candidate in candidates:
        current = best_by_primitive.get(candidate.primitive)
        if current is None or (candidate.effect or -1.0) > (current.effect or -1.0):
            best_by_primitive[candidate.primitive] = candidate
    candidates = list(best_by_primitive.values())
    candidates.sort(
        key=lambda candidate: (
            candidate.effect is None,
            -(candidate.effect or 0.0),
            candidate.primitive,
        )
    )
    return tuple(candidates[:CLAIM_LIMIT])


def registration_path(
    candidate: ClaimCandidate, root: Path = DEFAULT_REGISTRATIONS
) -> Path:
    """The committed registration file for one candidate."""
    return root / f"sec_{candidate.axis}_{candidate.level}.json"


def candidate_box(candidate: ClaimCandidate, schedule: Schedule) -> dict[str, Any]:
    """The box both arms train at: the candidate's coordinate, its params too.

    One builder: the screen's own ``_box_summary`` reads the coordinate's six
    axes, its structural params and the schedule, so a registration and a claim
    compare the same fields (TODO97 S9c).
    """
    return _box_summary(candidate.coordinate(candidate.best_value), schedule)


def register_claim(
    candidate: ClaimCandidate, schedule: Schedule
) -> ThresholdRegistration:
    """The claim's pre-registered threshold, written before the first seed.

    The registration carries the coordinate's box, not the schedule alone: a
    claim re-boxed between the ladder and the run is refused before its first
    seed, because the committed box names the params it was measured under.
    """
    margin = margin_for(schedule.task_id)
    return ThresholdRegistration(
        claim=(
            f"tuning {candidate.knob} on {candidate.primitive} moves val_acc "
            f"by at least {margin:.4f} at the {schedule.task_id} base"
        ),
        metric="val_acc",
        threshold=margin,
        alpha=DEFAULT_ALPHA,
        min_seeds=CLAIM_SEEDS,
        created=date.today().isoformat(),
        box=candidate_box(candidate, schedule),
    )


def write_claim(
    candidate: ClaimCandidate,
    schedule: Schedule,
    path: Path = DEFAULT_REGISTRATIONS,
) -> ThresholdRegistration:
    """Commit one registration to the repo before any cell is run."""
    registration = register_claim(candidate, schedule)
    target = path if path.suffix == ".json" else registration_path(candidate, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(registration.to_dict(), indent=2), encoding="utf-8")
    return registration


@dataclass(frozen=True, slots=True)
class ClaimRecord:
    """One candidate's pair and verdict: the numbers, the CI and its box."""

    candidate: ClaimCandidate
    cells: tuple[PairedCell, ...]
    paired: dict[str, Any] | None
    claim: dict[str, Any]
    verdict: str  # claim | marginal | coordinate | defect | refused
    stop_reason: str
    walltime_s: float
    no_power: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate": self.candidate.to_dict(),
            "cells": [cell.to_dict() for cell in self.cells],
            "effect": self.paired,
            "claim": self.claim,
            "verdict": self.verdict,
            "stop_reason": self.stop_reason,
            "walltime_s": self.walltime_s,
            "no_power": self.no_power,
        }


def _paired_cells(
    candidate: ClaimCandidate,
    schedule: Schedule,
    measure: Callable[[Coordinate, Schedule], Mapping[str, Any]],
) -> tuple[PairedCell, ...]:
    """Five index-matched seeds per arm at the candidate's box."""
    cells: list[PairedCell] = []
    for seed in range(CLAIM_SEEDS):
        for arm, value in (
            ("control", candidate.default),
            ("treatment", candidate.best_value),
        ):
            measured = measure(
                candidate.coordinate(value),
                replace(schedule, seed=seed, n_seeds=1),
            )
            cells.append(
                PairedCell(
                    arm=arm,
                    factor=value / candidate.default,
                    seed=seed,
                    status=str(measured["status"]),
                    val_acc=measured["val_acc"],
                    loss=measured["loss"],
                    walltime_s=measured["walltime_s"],
                    replay_hash=measured["replay_hash"],
                    box=measured["box"],
                    reason=measured.get("reason"),
                )
            )
    return tuple(cells)


def _marginal(diffs: list[float], threshold: float) -> bool:
    """Whether the point clears the margin by less than one standard error."""
    mean_diff = statistics.fmean(diffs)
    if mean_diff <= threshold or len(diffs) < 2:
        return False
    spread = statistics.stdev(diffs) / math.sqrt(len(diffs))
    return mean_diff - threshold <= spread


def _decide(
    candidate: ClaimCandidate,
    cells: tuple[PairedCell, ...],
    registration: ThresholdRegistration,
    schedule: Schedule,
) -> tuple[str, dict[str, Any] | None, str, bool]:
    """The pair's verdict, its CI, the stop reason and the no-power mark."""
    failed = next(
        (cell for cell in cells if cell.status in {"defect", "refused"}),
        None,
    )
    if failed is not None:
        return (
            "defect" if failed.status == "defect" else "refused",
            None,
            f"the {failed.arm} arm at seed {failed.seed} is an execution fact: "
            f"{failed.reason}",
            False,
        )
    treatments = [cell for cell in cells if cell.arm == "treatment"]
    controls = [cell for cell in cells if cell.arm == "control"]
    if all(
        treatment.val_acc == control.val_acc
        for treatment, control in zip(treatments, controls, strict=True)
    ):
        return (
            "coordinate",
            None,
            "the arms are identical at every seed: the knob does not bind at "
            "this box, so the pair has no power and is marked, not priced",
            True,
        )
    paired = paired_comparison(
        [float(cell.val_acc or 0.0) for cell in treatments],
        [float(cell.val_acc or 0.0) for cell in controls],
        seed=schedule.seed,
    )
    diffs = [
        float(treatment.val_acc or 0.0) - float(control.val_acc or 0.0)
        for treatment, control in zip(treatments, controls, strict=True)
    ]
    verdict = claim_verdict(paired, registration, candidate_box(candidate, schedule))
    if verdict == "coordinate" and _marginal(diffs, registration.threshold):
        return "marginal", asdict(paired), _margin_reason(paired, registration), False
    return (
        verdict,
        asdict(paired),
        (
            "five paired seeds at the base box; the CI clears the registered margin"
            if verdict == "claim"
            else "five paired seeds at the base box; the effect sits inside "
            "the registered margin"
        ),
        False,
    )


def _margin_reason(
    paired: PairedComparison, registration: ThresholdRegistration
) -> str:
    return (
        f"the point clears the margin by less than one standard error "
        f"(effect {paired.mean_diff:.4f}, margin {registration.threshold:.4f})"
    )


def run_claim(
    candidate: ClaimCandidate,
    registration: ThresholdRegistration,
    schedule: Schedule,
    *,
    measure: Callable[[Coordinate, Schedule], Mapping[str, Any]] | None = None,
) -> ClaimRecord:
    """Run one claim: five paired seeds, then the registered decision.

    A registration written for another box refuses the claim before a cell is
    run. A best point that is the primitive's own default has identical arms
    by construction, so it is marked no-power without spending the ten cells.
    """
    started = time.perf_counter()
    box = candidate_box(candidate, schedule)
    stale = _stale_box(candidate, registration)
    if stale is not None:
        return ClaimRecord(
            candidate,
            (),
            None,
            registration.to_dict(),
            "refused",
            stale,
            time.perf_counter() - started,
            False,
        )
    mismatch = registration.box_mismatch(box)
    if mismatch is not None:
        return ClaimRecord(
            candidate,
            (),
            None,
            registration.to_dict(),
            "refused",
            f"the registration declares another box ({mismatch})",
            time.perf_counter() - started,
            False,
        )
    if math.isclose(candidate.best_value, candidate.default):
        return ClaimRecord(
            candidate,
            (),
            None,
            registration.to_dict(),
            "coordinate",
            "the best rung is the primitive's own default: the ladder moved "
            "no knob value, so the pair has no power by construction",
            time.perf_counter() - started,
            True,
        )
    cells = _paired_cells(candidate, schedule, measure or _measure)
    verdict, paired, reason, no_power = _decide(
        candidate, cells, registration, schedule
    )
    return ClaimRecord(
        candidate,
        cells,
        paired,
        registration.to_dict(),
        verdict,
        reason,
        time.perf_counter() - started,
        no_power,
    )


def _stale_box(
    candidate: ClaimCandidate, registration: ThresholdRegistration
) -> str | None:
    """Why this pair cannot be priced at its box, or ``None`` when it can.

    A row screened before its params were recorded cannot rebuild its
    coordinate, so the ladder's box is a guess; a registration written for
    that guess is stale too (TODO97 S9c). Either refuses the pair before the
    first seed, and the close is the screen's own repair.
    """
    if not box_params(candidate.box):
        return (
            "the row's box carries no structural params: re-screen the row "
            "and re-register the claim before its first seed"
        )
    if registration.box is not None and not box_params(registration.box):
        return (
            "the registration's box carries no structural params: re-register "
            "the claim at the candidate's box before its first seed"
        )
    return None


def _report(records: Iterable[ClaimRecord]) -> dict[str, Any]:
    claims = [record.to_dict() for record in records]
    summary = {
        verdict: sum(1 for record in claims if record["verdict"] == verdict)
        for verdict in ("claim", "marginal", "coordinate", "defect", "refused")
    }
    return {
        "version": "SEC-claims-v1",
        "updated": datetime.now(UTC).isoformat(),
        "n_max": CLAIM_SEEDS,
        "claims": claims,
        "summary": summary,
    }


def _selected(
    maps: tuple[Path, ...], only: Iterable[str] | None
) -> tuple[ClaimCandidate, ...]:
    wanted = set(only or ())
    candidates = claim_candidates(maps)
    if not wanted:
        return candidates
    return tuple(c for c in candidates if c.primitive in wanted)


def main(argv: list[str] | None = None) -> int:
    """Commit the claim registrations, or run them, never both in one step."""
    from computronium.experiment.sec_pilot import base_schedule

    parser = argparse.ArgumentParser(description="SEC S9 - the claim list")
    parser.add_argument(
        "--maps",
        nargs="+",
        type=Path,
        default=None,
        help="Family maps (default: every results/sec*/map.json)",
    )
    parser.add_argument("--register", action="store_true", help="Write registrations")
    parser.add_argument("--run", action="store_true", help="Run registered claims")
    parser.add_argument("--device", default="auto")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/sec_claims/claims.json"),
        help="Claim report (--run)",
    )
    parser.add_argument(
        "--only", action="append", help="Only this primitive (repeatable)"
    )
    args = parser.parse_args(argv)
    if not (args.register or args.run):
        parser.error("choose --register (before any seed) or --run")

    maps = tuple(args.maps) if args.maps else default_maps()
    candidates = _selected(maps, args.only)
    if not candidates:
        print("no tuned ladder record in the selected maps")
        return 1

    if args.register:
        for candidate in candidates:
            schedule = base_schedule(candidate.task, args.device)
            if schedule is None:
                print(
                    f"refused {candidate.primitive}: no base box for {candidate.task}"
                )
                continue
            if not box_params(candidate.box):
                print(
                    f"refused {candidate.primitive}: the row's box carries no "
                    "structural params (re-screen the row)"
                )
                continue
            path = registration_path(candidate)
            registration = write_claim(candidate, schedule, path)
            print(
                f"registered {candidate.primitive} "
                f"effect={_effect(candidate)} margin={registration.threshold:.4f} "
                f"-> {path}"
            )
        return 0

    records: list[ClaimRecord] = []
    for candidate in candidates:
        schedule = base_schedule(candidate.task, args.device)
        if schedule is None:
            print(f"refused {candidate.primitive}: no base box for {candidate.task}")
            continue
        path = registration_path(candidate)
        registration = load_registration(path, candidate_box(candidate, schedule))
        if registration is None:
            record = ClaimRecord(
                candidate,
                (),
                None,
                {},
                "refused",
                f"no committed registration for this box at {path}; the claim "
                "refuses before the first cell",
                0.0,
                False,
            )
        else:
            record = run_claim(candidate, registration, schedule)
        records.append(record)
        print(
            f"{record.verdict} {candidate.primitive} "
            f"effect={_paired_text(record)} {record.walltime_s:.1f}s"
        )
        print(f"  {record.stop_reason}")

    report = _report(records)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {args.out}: {report['summary']}")
    return 0


def _effect(candidate: ClaimCandidate) -> str:
    return "none" if candidate.effect is None else f"{candidate.effect:+.4f}"


def _paired_text(record: ClaimRecord) -> str:
    if record.paired is None:
        return "none"
    effect = record.paired
    return (
        f"{effect['mean_diff']:+.4f} "
        f"[{effect['ci_lower']:+.4f}, {effect['ci_upper']:+.4f}] "
        f"p={effect['p_value']:.4f}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
