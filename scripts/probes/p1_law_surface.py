"""TODO98 P1: the law-surface batch.

One program enumerates the declared surface, asks each law the one question
its axis declares, writes one row per law, and exits a verdict. A carrier
law: does its step differ from its declared neutral companion (µs)? A signal
law: does its cell train, and does it stop training with the channel cut?
Knob binding is not asked: the search space discovers it at the cost it
already pays.

Run:
    uv run python scripts/probes/p1_law_surface.py --only carrier \
        --lanes 12 --row-budget 150 --out results/p1
    uv run python scripts/probes/p1_law_surface.py --only signal --resume \
        --steps 200 --row-budget 120 --out results/p1

Exit: 0 every selected law has a state (a named defect or gap is a result);
1 a test defect (a declared non-pass fits, or a signal control reaches); 2
the surface disagrees with the registry; 3 partial (an unfinished row or a
missing law remains).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from computronium.primitives import cases, fit
from computronium.primitives.registry import get_primitive_spec
from computronium.primitives.surface import laws, surface, validate
from computronium.experiment.sec_pilot import BASE_BOXES

if TYPE_CHECKING:
    from computronium.experiment.schema.coordinate import Coordinate
    from computronium.primitives.surface import Law

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "results" / "p1"

#: The instrument's version. A change to what a row measures invalidates
#: the rows written before it: a version bump starts the merge from zero
#: instead of keeping verdicts the current instrument did not produce.
INSTRUMENT: Final[int] = 6

#: The calibration gate: a row the repository already declares non-pass must
#: not come out ``works``, and one that does is the instrument's defect — the
#: program then writes no law table. The rows are the ones this instrument
#: can price: a declared void constraint (``refused``) and a ladder row with
#: no legal setting (``defect-or-gap``). ``geometry.nca`` and ``geometry.conv``
#: are not here: the screen priced them as a cross-config wiring defect and a
#: 60 s cost cap, and P1 prices both classes with its own cells (measured
#: 2026-11-21: nca ``works``, conv ``works`` at the digest).
CALIBRATION: Final[dict[str, str]] = {
    "primitive.substrate.complex": "refused",
    "primitive.credit_assignment.forward_tangent": "defect-or-gap (mechanism)",
}


@dataclass(frozen=True, slots=True)
class Options:
    """The batch's declared box: what it runs, on how many lanes, in what time."""

    axes: tuple[str, ...] = ()
    only: str = "all"
    steps: int = fit.STEPS
    samples: int = fit.SAMPLES
    lanes: int = 12
    seed: int = 0
    out: Path = DEFAULT_OUT
    resume: bool = False
    limit: int = 0
    row_budget: float = 180.0


@dataclass(slots=True)
class Report:
    """The batch's result: its rows, its calibration, and its verdict."""

    options: Options
    rows: dict[str, dict[str, Any]] = field(default_factory=dict)
    calibration: dict[str, dict[str, Any]] = field(default_factory=dict)
    problems: list[str] = field(default_factory=list)
    exit_code: int = 0


def declaration(spec: Any) -> str:
    """The law's declaration hash: its ID, axis, kind, families and equations."""
    payload = {
        "id": spec.id,
        "axis": spec.axis,
        "kind": fit.kind(spec),
        "families": list(spec.task_families),
        "equations": spec.equations,
        "invariants": list(spec.invariants),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def fingerprint(spec: Any, task_id: str) -> str:
    """The case's canonical fingerprint: the digest of its reference output."""
    from computronium.acceleration.parity import digest

    try:
        case = cases.build_case(spec, task_id, {}, 0)
        return digest(cases.step(spec, case))
    except Exception:  # ruff: ignore[blind-except] - a refused case has no fingerprint
        return ""


def _previous(out: Path) -> list[dict[str, Any]]:
    """The finished rows of this instrument; an older one's rows are ignored."""
    path = Path(out) / "surface.json"
    if not path.exists():
        return []
    payload = json.loads(path.read_text())
    return payload["rows"] if payload.get("instrument") == INSTRUMENT else []


def _spec(law: Law) -> Any:
    spec = get_primitive_spec(law.id)
    if spec is None:
        msg = f"{law.id} is not registered"
        raise LookupError(msg)
    return spec


def _satisfied(measured: fit.Fit, criterion: str) -> bool:
    """Whether a fit satisfied the law's declared criterion."""
    return measured.moved if criterion == "moved" else measured.reached


def _criterion(spec: Any) -> str:
    """The fit criterion this law declares: a floor, or a moving loss."""
    from computronium.core.system_trainer.spec import error_blind_credit

    if spec.axis == "credit" and error_blind_credit(spec.id.rsplit(".", 1)[-1]):
        return "moved"
    return "reach"


def _fit_at(
    spec: Any,
    declared: Coordinate,
    *,
    steps: int,
    seconds: float,
    seed: int,
) -> fit.Fit:
    """Compose a fresh cell at ``declared`` and run one fit on it."""
    composed = fit.cell(spec, declared)
    batch = fit.problem(composed.system, composed, seed=seed)
    return fit.measure(
        composed.system,
        batch,
        steps=steps,
        seconds=seconds,
        criterion=_criterion(spec),
    )


def _grid(
    spec: Any,
    base: Coordinate,
    row: dict[str, Any],
    options: Options,
    watchdog: float,
) -> tuple[fit.Fit | None, list[str]]:
    """The law's own knob grid: the best legal fit, and what was dropped.

    Sweeps each law's declared knobs (from fit.ladder) at 3 log-spaced points
    in-domain, including the box default. Caps at the first 3 knobs (≤9 fits).
    Points outside the declared domain are dropped and reported.
    """
    from computronium.primitives import fit

    knob_grid = fit.ladder(spec)
    fits: list[fit.Fit] = []
    dropped: list[str] = []

    # Cap at first 3 knobs, ≤9 fits per row
    for knob, (knob_min, knob_max, knob_scale) in knob_grid[:3]:
        # Generate 3 points: min, mid, max (log-spaced if scale is "log")
        if knob_scale == "log":
            import math

            log_min = math.log(knob_min)
            log_max = math.log(knob_max)
            points = [
                knob_min,
                math.exp((log_min + log_max) / 2),
                knob_max,
            ]
        else:
            points = [knob_min, (knob_min + knob_max) / 2, knob_max]

        # Include the box default if it's within bounds
        box_default = base.params.get(knob)
        if box_default is not None:
            box_val = float(box_default)
            if knob_min <= box_val <= knob_max and box_val not in points:
                points.append(box_val)

        for value in points:
            # Drop points outside declared domain
            if not (knob_min <= value <= knob_max):
                dropped.append(f"{knob}={value:.6f}: outside declared domain [{knob_min}, {knob_max}]")
                continue
            trial = replace(base, params={**base.params, knob: value})
            try:
                measured = _fit_at(
                    spec, trial, steps=options.steps, seconds=watchdog, seed=options.seed
                )
            except (ValueError, fit.FitError) as exc:
                dropped.append(f"{knob}={value:.6f}: {type(exc).__name__}: {exc}")
                row["error"] = row["error"] or f"{type(exc).__name__}: {exc}"
                continue
            if measured.killed:
                dropped.append(f"{knob}={value:.6f}: over budget ({measured.seconds:.1f}s)")
                continue
            fits.append(measured)
    return (min(fits, key=lambda measured: measured.final) if fits else None), dropped


def _control(
    spec: Any,
    base: Coordinate,
    row: dict[str, Any],
    options: Options,
    watchdog: float,
) -> fit.Fit | None:
    """The mechanism-removed fit on a fresh cell: ``None`` when it cannot run."""
    try:
        fresh = fit.control(spec, base)
    except ValueError as exc:
        row["error"] = f"control: {type(exc).__name__}: {exc}"
        return None
    batch = fit.problem(fresh.system, fresh, seed=options.seed)
    try:
        control = fit.measure(
            fresh.system,
            batch,
            steps=options.steps,
            seconds=watchdog,
            criterion=_criterion(spec),
        )
    except fit.FitError as exc:
        row["error"] = f"control: {type(exc).__name__}: {exc}"
        return None
    if control.killed:
        return None
    row["control_loss"] = control.final
    return control


def _carrier(
    spec: Any, base: Coordinate, row: dict[str, Any], seed: int
) -> fit.Removal | None:
    """The carrier reading: its step digest against its declared companion."""
    try:
        removal = fit.bound(spec, base, seed)
    except (ValueError, RuntimeError) as exc:
        row["error"] = f"companion: {type(exc).__name__}: {exc}"
        return None
    row.update(
        digest=removal.digest,
        companion=removal.companion,
        differs=removal.differs,
        silent=removal.silent,
    )
    return removal


def run_row(law: Law, options: Options) -> dict[str, Any]:
    """One law's row, tested by the instrument its axis declares."""
    started = time.monotonic()
    spec = _spec(law)
    row: dict[str, Any] = {
        "id": spec.id,
        "axis": spec.axis,
        "kind": fit.kind(spec),
        "family": fit.family(spec),
        "task": "",
        "state": "incomplete",
        "decided_by": "",
        "fit_loss": None,
        "fit_final": None,
        "control_loss": None,
        "digest": "",
        "companion": "",
        "differs": None,
        "silent": None,
        "steps": 0,
        "seconds": 0.0,
        "killed": False,
        "box": {},
        "declaration": declaration(spec),
        "error": None,
    }
    if law.refusal is not None:
        row.update(
            state="refused", decided_by=law.refusal, box={"refusal": law.refusal}
        )
        row["seconds"] = time.monotonic() - started
        return row
    if not row["family"]:
        row.update(
            state="defect-or-gap (mechanism)",
            decided_by="no declared family base box: the box that would price it",
        )
        row["seconds"] = time.monotonic() - started
        return row

    from computronium.experiment.sec_loop import _is_legal
    from computronium.experiment.sec_pilot import BASE_BOXES

    task_id = BASE_BOXES[row["family"]].task_id
    row["task"] = task_id
    row["fingerprint"] = fingerprint(spec, task_id)
    base = fit.coordinate(spec)
    legal, refusal = _is_legal(base, task_id)
    row["box"] = {**asdict(base), "steps": options.steps, "samples": options.samples}
    if not legal:
        row.update(state="refused", decided_by=refusal or "the declared space refuses")
        row["seconds"] = time.monotonic() - started
        return row

    try:
        invariant = cases.invariant(
            spec, cases.build_case(spec, task_id, {}, options.seed)
        )
    except Exception as exc:  # ruff: ignore[blind-except] - a law that cannot run L-a is the finding
        invariant = False
        row["error"] = f"l-a: {type(exc).__name__}: {exc}"

    if row["kind"] == "carrier":
        removal = _carrier(spec, base, row, options.seed)
        state, decided_by = fit.decide(
            law_kind="carrier", invariant=invariant, removal=removal
        )
        row.update(state=state, decided_by=decided_by)
        row["seconds"] = time.monotonic() - started
        return row

    watchdog = max(1.0, options.row_budget - (time.monotonic() - started))
    best, dropped = _grid(spec, base, row, options, watchdog)
    row["box"] = {**row["box"], "dropped": dropped}
    if best is None:
        row.update(
            state="refused",
            decided_by=f"over budget: the row spent its {options.row_budget:.0f}s",
            killed=True,
        )
        row["seconds"] = time.monotonic() - started
        return row

    row.update(fit_loss=best.loss, fit_final=best.final, steps=best.steps, killed=False)
    trained = _satisfied(best, _criterion(spec))
    remaining = max(1.0, options.row_budget - (time.monotonic() - started))
    control = _control(spec, base, row, options, remaining) if trained else None

    state, decided_by = fit.decide(
        law_kind="signal",
        invariant=invariant,
        fits=trained,
        control=None if control is None else _satisfied(control, _criterion(spec)),
    )
    row.update(
        state=state, decided_by=decided_by, box={**row["box"], "dropped": dropped}
    )
    row["seconds"] = time.monotonic() - started
    return row


def _key(row: dict[str, Any]) -> str:
    """The row's restart key: its declaration hash and case fingerprint."""
    return f"{row['id']}:{row['declaration']}:{row.get('fingerprint', '')}"


def _select(options: Options) -> list[Law]:
    """The laws this run selects: an axis filter, then the class filter."""
    selected = [law for law in laws() if not options.axes or law.axis in options.axes]
    if options.only in {"carrier", "signal"}:
        selected = [law for law in selected if law.kind == options.only]
    selected.sort(key=lambda law: (law.axis, law.id))
    return selected[: options.limit] if options.limit else selected


def _run(options: Options) -> Report:
    """Run the selected waves and collect their rows."""
    report = Report(options=options)
    report.problems = validate(surface())
    if report.problems:
        report.exit_code = 2
        return report
    selected = _select(options)

    previous = (
        {row["key"]: row for row in _previous(options.out)} if options.resume else {}
    )

    started = time.monotonic()
    pending: list[Law] = []
    for law in selected:
        spec = _spec(law)
        known = {
            "id": spec.id,
            "declaration": declaration(spec),
            "fingerprint": fingerprint(spec, BASE_BOXES[fit.family(spec)].task_id),
        }
        cached = next(
            (
                row
                for row in previous.values()
                if row["id"] == known["id"]
                and row["declaration"] == known["declaration"]
                and row.get("fingerprint", "") == known["fingerprint"]
                and row.get("state") != "incomplete"
                and (
                    law.kind == "carrier"
                    or row.get("box", {}).get("steps") == options.steps
                )
            ),
            None,
        )
        if cached is not None:
            report.rows[cached["key"]] = cached
        else:
            pending.append(law)

    with ProcessPoolExecutor(
        max_workers=max(1, options.lanes),
        max_tasks_per_child=1,
    ) as pool:
        futures = {pool.submit(_child, law, options): law for law in pending}
        for future in futures:
            row = future.result()
            row["key"] = _key(row)
            report.rows[row["key"]] = row

    report.rows = {
        **{row["key"]: row for row in _previous(options.out)},
        **report.rows,
    }
    report.exit_code = _exit(report, selected)
    report.calibration = _calibrate(report)
    if report.calibration and any(
        entry["state"] == "works" for entry in report.calibration.values()
    ):
        report.exit_code = 1
    _write(report)
    print(
        f"{len(report.rows)} rows, {len(report.calibration)} calibration, "
        f"{time.monotonic() - started:.0f}s, exit {report.exit_code}",
        file=sys.stderr,
    )
    return report


def _child(law: Law, options: Options) -> dict[str, Any]:
    """One lane: the law's row, on its own process with two threads."""
    import torch

    torch.set_num_threads(2)
    torch.manual_seed(options.seed)
    try:
        return run_row(law, options)
    except Exception as exc:  # ruff: ignore[blind-except] - one lane must not end the batch
        return _failed(law, exc)


def _failed(law: Law, exc: Exception) -> dict[str, Any]:
    """A lane that raised: the row records the defect instead of ending the batch."""
    spec = _spec(law)
    return {
        "id": spec.id,
        "axis": spec.axis,
        "kind": fit.kind(spec),
        "family": fit.family(spec),
        "task": "",
        "state": "defect-or-gap (mechanism)",
        "decided_by": "the fits could not run",
        "fit_loss": None,
        "fit_final": None,
        "control_loss": None,
        "digest": "",
        "companion": "",
        "differs": None,
        "silent": None,
        "steps": 0,
        "seconds": 0.0,
        "killed": False,
        "box": {},
        "declaration": declaration(spec),
        "fingerprint": "",
        "error": f"{type(exc).__name__}: {exc}",
    }


def _exit(report: Report, selected: list[Law]) -> int:
    """The batch's verdict: a test defect, a partial run, or measured rows.

    A named defect or gap is a result, so it does not block exit 0; an
    unfinished row or a missing selected law is partial (exit 3).
    """
    states = [row["state"] for row in report.rows.values()]
    if any(state == "test defect" for state in states):
        return 1
    if any(state == "incomplete" for state in states):
        return 3
    measured = {row["id"] for row in report.rows.values()}
    missing = [law.id for law in selected if law.id not in measured]
    return 3 if missing else 0


def _calibrate(report: Report) -> dict[str, dict[str, Any]]:
    """The gate: each declared non-pass row's expected class against its state."""
    measured = {row["id"]: row for row in report.rows.values()}
    return {
        law_id: {
            "expected": expected,
            "state": measured[law_id]["state"],
            "reproduced": measured[law_id]["state"] == expected,
        }
        for law_id, expected in CALIBRATION.items()
        if law_id in measured
    }


def _write(report: Report) -> None:
    """Write the rows and the table: a table only when the gate reproduced.

    The rows are the caller's: ``_run`` merged the earlier waves in before
    the verdict, so the calibration and the exit code describe the table as a
    whole and not just this run's selection.
    """
    out = Path(report.options.out)
    out.mkdir(parents=True, exist_ok=True)
    calibrated = all(entry["state"] != "works" for entry in report.calibration.values())
    payload = {
        "version": 1,
        "instrument": INSTRUMENT,
        "options": {
            "axes": list(report.options.axes),
            "only": report.options.only,
            "steps": report.options.steps,
            "samples": report.options.samples,
            "seed": report.options.seed,
            "lanes": report.options.lanes,
        },
        "calibration": report.calibration,
        "problems": report.problems,
        "exit_code": report.exit_code,
        "rows": sorted(report.rows.values(), key=lambda row: (row["axis"], row["id"])),
    }
    (out / "surface.json").write_text(json.dumps(payload, indent=2, default=str))
    if not calibrated:
        (out / "calibration.md").write_text(
            _table(report.calibration, calibration=True)
        )
        return
    (out / "surface.md").write_text(_table(report.rows))


def _table(rows: Any, *, calibration: bool = False) -> str:
    """A Markdown table of the rows, or of the gate."""
    if calibration:
        lines = ["| Law | Expected | Measured | Reproduced |", "|---|---|---|---|"]
        lines += [
            f"| {law_id} | {entry['expected']} | {entry['state']} "
            f"| {'yes' if entry.get('reproduced') else 'no'} |"
            for law_id, entry in sorted(rows.items())
        ]
        return "\n".join(lines) + "\n"
    lines = [
        "| Law | Axis | Kind | Family | State | Fit | Removal | s |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in sorted(rows.values(), key=lambda row: (row["axis"], row["id"])):
        if row.get("kind") == "carrier":
            removal = (
                f"digest {'differs' if row['differs'] else 'equal'}"
                if row["differs"] is not None
                else "-"
            )
        else:
            removal = _number(row["control_loss"])
        lines.append(
            f"| {row['id'].rsplit('.', 1)[-1]} | {row['axis']} "
            f"| {row.get('kind', '-')} | {row['family']} | {row['state']} "
            f"| {_number(row['fit_loss'], row['fit_final'])} "
            f"| {removal} | {row['seconds']:.1f} |"
        )
    return "\n".join(lines) + "\n"


def _number(loss: float | None, final: float | None = None) -> str:
    """A fit's loss pair, or a single number, as a cell."""
    if loss is None:
        return "-"
    if final is None:
        return f"{loss:.3f}"
    return f"{loss:.3f} → {final:.3f}"


def main(argv: list[str] | None = None) -> int:
    """Parse the batch's box, run it, and exit its verdict."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--axes", default="")
    parser.add_argument(
        "--only",
        choices=("all", "signal", "carrier"),
        default="all",
        help="Select a class: carriers are digested, signals are fitted",
    )
    parser.add_argument("--steps", type=int, default=fit.STEPS)
    parser.add_argument("--samples", type=int, default=fit.SAMPLES)
    parser.add_argument("--lanes", type=int, default=12)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--row-budget", type=float, default=180.0)
    options = parser.parse_args(argv)
    axes = tuple(axis for axis in options.axes.split(",") if axis)
    declared = Options(
        axes=axes,
        only=options.only,
        steps=options.steps,
        samples=options.samples,
        lanes=options.lanes,
        seed=options.seed,
        out=options.out,
        resume=options.resume,
        limit=options.limit,
        row_budget=options.row_budget,
    )
    report = _run(declared)
    return report.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
