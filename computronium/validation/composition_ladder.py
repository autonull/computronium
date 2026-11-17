"""F1: the composition ladder (TODO93 §6a, track F).

The question is one sentence: **does any legal 6-axis composition beat the best
single-axis default by a pre-registered delta at a matched budget?** The 6-axis
generator and its legality filter already exist; what is missing is one matched
comparison between a composition and the strongest arm that varies one axis.

**The box.** ``digits`` quick mode (1797 samples, 64 features, 10 classes) at
batch 32 and one epoch (57 batches), one seed, CPU, parameter ceiling 50k. Every
cell runs the same number of batches, so the ruler is *matched
forward-equivalents* (57 per cell) by construction.

**The reference.** Every legal single-axis arm (one axis varied, the rest at the
default data/feedforward/instantaneous/null/gradient/euclidean cell) is measured
at the same box. The strongest of these is the **best single-axis default**. It
is the bar a composition must clear, so the reference is not chosen from the
compositions it is meant to judge.

**The screen.** Fifty legal cells with at least two non-default axes are drawn
uniformly (seeded reservoir) from the generator's first page of composable
candidates. A cell that refuses to train is a row in the table, not a skipped
cell: the refusal rate is part of the result.

**The family ladder.** A refusal is not written from one un-tuned cell. Screen
cells are grouped by their credit primitive; the family with the highest median
accuracy gets a three-point ladder on its composition width (2, 4, 6 non-default
axes), built from the family's best cell and the best measured single-axis arm
of each remaining axis. The family must clear the reference by
:data:`DELTA` at one of those points before a promotion is written.

**Gate (pre-registered).** The registration is written before the first cell.
Controls first: the reference must clear :data:`FLOOR`, and a second seed of the
reference must reproduce it within :data:`CONTROL_TOL`; either failure
invalidates the run. Then:

- a ladder point at ``reference + DELTA`` or above **promotes to F2** (a
  five-seed replication and task family, not a claim);
- a screen winner that does not survive its family ladder is a **coordinate**,
  not a promotion;
- a flat screen (no family at the bar after its ladder) **refuses composition
  at this box** with its knob box, reversal trigger, and re-open command.

Run it with::

    uv run python -m computronium.validation.composition_ladder --device cpu
    uv run python -m computronium.validation.composition_ladder --replay
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import random
import statistics
import time
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import torch

from computronium.experiment.kernel.evaluate import evaluate_cell, task_shape
from computronium.experiment.kernel.search_space import (
    iter_candidates,
    schedule_for,
    search_space_from_spec,
)
from computronium.experiment.schema.coordinate import Coordinate
from computronium.experiment.schema.run_spec import RunSpec
from computronium.experiment.schema.seed_registries import seed_all_registries

if TYPE_CHECKING:
    from collections.abc import Iterable

logger = logging.getLogger(__name__)

__all__ = [
    "BATCH_LIMIT",
    "CONTROL_SEED",
    "CONTROL_TOL",
    "DEFAULT_VALUES",
    "DELTA",
    "FLOOR",
    "LADDER_WIDTHS",
    "MIN_SCREEN_MEASURED",
    "SCREEN_CELLS",
    "SCREEN_SEED",
    "CompositionCell",
    "CompositionGate",
    "CompositionReport",
    "read_cells",
    "replay_composition_ladder",
    "run_composition_ladder",
    "write_registration",
    "write_report",
]

#: The cheap task. Digits is 1797x64, cached, and learns in one epoch.
TASK_ID = "digits"
#: One epoch at batch 32 is 57 batches: the matched forward-equivalent ruler.
BATCH_LIMIT = 57
#: One seed for the screen; the reference's second seed is the instrument check.
SCREEN_SEED = 42
CONTROL_SEED = 43
#: Fifty multi-axis cells, sampled from the generator's first page.
SCREEN_CELLS = 50
SCAN_LIMIT = 2000
#: The pre-registered material effect: one percentage point of accuracy.
DELTA = 0.01
#: The reference must learn before it can be a bar.
FLOOR = 0.55
#: The reference's second seed must reproduce it within this band. The cheap
#: one-epoch box has a measured ~7 pp data-order swing (C1 recorded 9 pp on
#: SplitMNIST), so the band catches a gross apparatus failure, not seed noise;
#: the ladder's confirmation seed is what guards a promotion.
CONTROL_TOL = 0.10
#: The family ladder's composition widths: two axes, four axes, all six.
LADDER_WIDTHS = (2, 4, 6)
#: A screen with fewer measured cells than this is a coordinate, not a verdict.
MIN_SCREEN_MEASURED = 40
PARAM_BUDGET = 50_000
DEVICE = "cpu"
#: The registration committed to the repo before the screen ran; the runner
#: copies it to the results directory so every replay reads the same box.
COMMITTED_REGISTRATION = (
    Path(__file__).resolve().parents[2]
    / "configs"
    / "preregistrations"
    / "t93_composition_registered.json"
)

#: The default cell every arm is measured against.
DEFAULT_VALUES: dict[str, str] = {
    "substrate": "digital",
    "geometry": "feedforward",
    "dynamics": "instantaneous",
    "plasticity": "null",
    "credit": "gradient",
    "update": "euclidean",
}
_AXES: tuple[str, ...] = tuple(DEFAULT_VALUES)
#: The axis order is fixed so a tie is resolved by the same order everywhere.
_AXIS_ORDER: tuple[str, ...] = (
    "substrate",
    "geometry",
    "dynamics",
    "plasticity",
    "credit",
    "update",
)


@dataclass(frozen=True, slots=True)
class CompositionCell:
    """One measured cell: its six axes, its budget, and its accuracy."""

    stage: str
    axis: str
    width: int
    seed: int
    batch_limit: int
    substrate: str
    geometry: str
    dynamics: str
    plasticity: str
    credit: str
    update: str
    params: dict[str, Any]
    val_acc: float | None
    param_count: int | None
    forward_equivalents: int
    walltime_s: float | None
    refused: bool
    reason: str
    measurement_key: str = ""

    def values(self) -> dict[str, str]:
        """The cell's structural values, keyed by axis name."""
        return {axis: getattr(self, axis) for axis in _AXES}

    def coordinate(self) -> Coordinate:
        """Reconstruct the coordinate this row measured."""
        return Coordinate(**self.values(), params=dict(self.params))


@dataclass(frozen=True, slots=True)
class CompositionGate:
    """The pre-registered verdict, with the numbers it was read from."""

    verdict: str
    reason: str
    reference_acc: float | None
    reference_axis: str
    best_screen_acc: float | None
    best_family: str | None
    best_ladder_acc: float | None


@dataclass(frozen=True, slots=True)
class CompositionReport:
    """F1's registration, its tables, and its verdict."""

    stage: str
    box: dict[str, object]
    registration: dict[str, object]
    reference: tuple[CompositionCell, ...]
    controls: tuple[CompositionCell, ...]
    screen: tuple[CompositionCell, ...]
    ladder: tuple[CompositionCell, ...]
    cells: tuple[CompositionCell, ...]
    verdict: str
    reason: str
    reference_acc: float | None
    reference_axis: str
    best_screen_acc: float | None
    best_family: str | None
    best_ladder_acc: float | None


def _spec(seed: int = SCREEN_SEED) -> RunSpec:
    """The run declaration: every axis, one cheap task, a fixed budget."""
    return RunSpec(
        profile="survey",
        task=TASK_ID,
        tasks=(TASK_ID,),
        objectives=("validation_accuracy",),
        fidelity="L0",
        n_seeds=1,
        epochs=1,
        batch_limit=BATCH_LIMIT,
        seed=seed,
        param_budget=PARAM_BUDGET,
        device=DEVICE,
        axes=(),
    )


@cache
def _shape(task_id: str) -> Any:
    """The task's shape, resolved once; the generator asks for it per page."""
    return task_shape(task_id, device=DEVICE)


def _width(coord: Coordinate) -> int:
    """How many axes leave the default cell."""
    return sum(1 for axis in _AXES if getattr(coord, axis) != DEFAULT_VALUES[axis])


def _legal(coord: Coordinate) -> bool:
    """Whether the composition validates for the cheap task's shape."""
    from computronium.experiment.kernel.compose import compose_configs

    shape = _shape(TASK_ID)
    try:
        compose_configs(
            coordinate=coord,
            geometry={},
            input_shape=shape.input_shape,
            output_dim=shape.output_dim,
            param_budget=PARAM_BUDGET,
        )
    except Exception:  # ruff: ignore[blind-except] - legality is a predicate
        return False
    return True


def _default_coordinate() -> Coordinate:
    """The reference cell: every axis at its default value."""
    return Coordinate(**DEFAULT_VALUES, params={})


def _single_axis_arms(space: Any) -> tuple[tuple[str, str, Coordinate], ...]:
    """Every legal cell that varies at most one axis, including the default."""
    arms: list[tuple[str, str, Coordinate]] = [("default", "", _default_coordinate())]
    seen = {_default_coordinate().cell_key()}
    for axis in _AXIS_ORDER:
        for primitive in space.primitives(axis):
            values = dict(DEFAULT_VALUES)
            values[axis] = primitive
            coord = Coordinate(**values, params={})
            if coord.cell_key() in seen:
                continue
            if not _legal(coord):
                continue
            seen.add(coord.cell_key())
            arms.append((axis, primitive, coord))
    return tuple(arms)


def _sample_screen(space: Any, spec: RunSpec) -> tuple[Coordinate, ...]:
    """A seeded uniform sample of the generator's multi-axis cells.

    A reservoir over the first :data:`SCAN_LIMIT` composable candidates keeps
    the sample uniform without walking the whole 731,808-point space; the
    generator's own legality filter has already run on every yielded cell.
    """
    rng = random.Random(SCREEN_SEED)  # ruff: ignore[suspicious-non-cryptographic-random-usage] - reproducible sampling
    reservoir: list[Coordinate] = []
    seen = 0
    for coord, _schedule in iter_candidates(
        spec,
        space,
        shape=_shape,
        max_scan=SCAN_LIMIT,
        check_composable=True,
    ):
        if _width(coord) < 2:
            continue
        seen += 1
        if len(reservoir) < SCREEN_CELLS:
            reservoir.append(coord)
            continue
        replace = rng.randrange(seen)
        if replace < SCREEN_CELLS:
            reservoir[replace] = coord
    return tuple(reservoir)


def _key(coord: Coordinate, schedule: Any) -> str:
    """The measurement key shared by the runner and the replay."""
    return coord.measurement_key(schedule)


def _cell(
    *,
    stage: str,
    axis: str,
    coord: Coordinate,
    schedule: Any,
    val_acc: float | None,
    param_count: int | None,
    walltime_s: float | None,
    refused: bool = False,
    reason: str = "",
) -> CompositionCell:
    """Build one row from a coordinate and its measurement."""
    return CompositionCell(
        stage=stage,
        axis=axis,
        width=_width(coord),
        seed=schedule.seed,
        batch_limit=schedule.batch_limit,
        **{axis: getattr(coord, axis) for axis in _AXES},
        params=dict(coord.params),
        val_acc=val_acc,
        param_count=param_count,
        forward_equivalents=BATCH_LIMIT,
        walltime_s=walltime_s,
        refused=refused,
        reason=reason,
        measurement_key=_key(coord, schedule),
    )


def _row(coord: Coordinate, schedule: Any) -> dict[str, object]:
    """The JSONL payload for one cell (flattened, replayable)."""
    return {
        "seed": schedule.seed,
        "batch_limit": schedule.batch_limit,
        "params": dict(coord.params),
        **{axis: getattr(coord, axis) for axis in _AXES},
        "measurement_key": _key(coord, schedule),
    }


def _write_cell(cell: CompositionCell, progress: str | Path | None) -> None:
    """Append a measured cell to the kill-safe log."""
    if progress is None:
        return
    path = Path(progress)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(_as_cell_dict(cell)) + "\n")


def _as_cell_dict(cell: CompositionCell) -> dict[str, object]:
    """A cell's JSON payload, including the measurement."""
    payload = {
        "stage": cell.stage,
        "axis": cell.axis,
        "width": cell.width,
        "seed": cell.seed,
        "batch_limit": cell.batch_limit,
        "params": cell.params,
        **{axis: getattr(cell, axis) for axis in _AXES},
        "val_acc": cell.val_acc,
        "param_count": cell.param_count,
        "forward_equivalents": cell.forward_equivalents,
        "walltime_s": cell.walltime_s,
        "refused": cell.refused,
        "reason": cell.reason,
        "measurement_key": cell.measurement_key,
    }
    return payload


def read_cells(progress: str | Path) -> tuple[CompositionCell, ...]:
    """Read the kill-safe log; a truncated line is ignored."""
    path = Path(progress)
    if not path.exists():
        return ()
    cells: list[CompositionCell] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        cells.append(
            CompositionCell(
                stage=str(payload["stage"]),
                axis=str(payload["axis"]),
                width=int(payload["width"]),
                seed=int(payload["seed"]),
                batch_limit=int(payload["batch_limit"]),
                **{axis: str(payload[axis]) for axis in _AXES},
                params=dict(payload["params"]),
                val_acc=payload["val_acc"],
                param_count=payload["param_count"],
                forward_equivalents=int(payload["forward_equivalents"]),
                walltime_s=payload["walltime_s"],
                refused=bool(payload["refused"]),
                reason=str(payload["reason"]),
                measurement_key=str(payload["measurement_key"]),
            )
        )
    return tuple(cells)


def _resume(progress: str | Path | None) -> dict[str, CompositionCell]:
    """Measured cells keyed by their measurement key."""
    if progress is None:
        return {}
    cells = read_cells(progress)
    if cells:
        logger.info("reusing %d measured cells from %s", len(cells), progress)
    return {cell.measurement_key: cell for cell in cells}


def _measure(
    done: dict[str, CompositionCell],
    *,
    stage: str,
    axis: str,
    coord: Coordinate,
    seed: int,
    progress: str | Path | None,
) -> CompositionCell:
    """Reuse a measured cell, otherwise evaluate it at the F1 box."""
    schedule = schedule_for(_spec(seed), TASK_ID, "L0")
    key = _key(coord, schedule)
    if key in done:
        return done[key]
    start = time.monotonic()
    try:
        evaluation = evaluate_cell(coord, schedule)
    except Exception as exc:  # ruff: ignore[blind-except] - a crash is a refusal
        cell = _cell(
            stage=stage,
            axis=axis,
            coord=coord,
            schedule=schedule,
            val_acc=None,
            param_count=None,
            walltime_s=time.monotonic() - start,
            refused=True,
            reason=f"{type(exc).__name__}: {exc}",
        )
    else:
        value = float(evaluation.metrics.get("val_acc", float("nan")))
        cell = _cell(
            stage=stage,
            axis=axis,
            coord=coord,
            schedule=schedule,
            val_acc=None if math.isnan(value) else value,
            param_count=evaluation.param_count,
            walltime_s=time.monotonic() - start,
            refused=math.isnan(value),
            reason="evaluation returned a NaN validation accuracy"
            if math.isnan(value)
            else "",
        )
    done[key] = cell
    _write_cell(cell, progress)
    return cell


def _best(cells: Iterable[CompositionCell]) -> CompositionCell | None:
    """The highest measured accuracy, or ``None`` when nothing trained."""
    measured = [cell for cell in cells if not cell.refused and cell.val_acc is not None]
    if not measured:
        return None
    return max(measured, key=lambda cell: cell.val_acc or 0.0)


def _best_family(screen: tuple[CompositionCell, ...]) -> str | None:
    """The credit family with the highest median accuracy (n >= 2).

    A median resists one lucky cell; a family that appears once cannot be
    laddered and is not eligible. Ties go to the larger family, then to the
    lexical credit name so the choice is deterministic.
    """
    families: dict[str, list[float]] = {}
    for cell in screen:
        if cell.refused or cell.val_acc is None:
            continue
        families.setdefault(cell.credit, []).append(cell.val_acc)
    eligible = {
        name: (statistics.median(values), len(values))
        for name, values in families.items()
        if len(values) >= 2
    }
    if not eligible:
        return None
    return max(
        eligible,
        key=lambda name: (eligible[name][0], eligible[name][1], name),
    )


def _axis_reference(
    reference: tuple[CompositionCell, ...],
) -> dict[str, tuple[str, float]]:
    """The best measured non-default primitive on each axis, with its accuracy."""
    best: dict[str, tuple[str, float]] = {}
    for cell in reference:
        if cell.axis in {"", "default"} or cell.refused or cell.val_acc is None:
            continue
        current = best.get(cell.axis)
        if current is None or cell.val_acc > current[1]:
            best[cell.axis] = (getattr(cell, cell.axis), cell.val_acc)
    return best


def _ladder_coordinates(
    screen: tuple[CompositionCell, ...],
    reference: tuple[CompositionCell, ...],
) -> tuple[tuple[str, int, Coordinate], ...]:
    """The best family's width ladder: 2, 4, and 6 non-default axes.

    The best cell of the family supplies the values already non-default; the
    remaining axes are filled with the best measured single-axis primitive.
    The family's credit is always one of the non-default axes; a width that
    cannot be filled from measured arms is returned as an empty-value point and
    recorded as a refusal by the caller.
    """
    family = _best_family(screen)
    if family is None:
        return ()
    family_cells = [
        cell
        for cell in screen
        if cell.credit == family and not cell.refused and cell.val_acc is not None
    ]
    best = _best(family_cells)
    if best is None:
        return ()
    ranks = _axis_reference(reference)
    base = best.values()
    ordered = sorted(
        _AXIS_ORDER,
        key=lambda axis: (
            0 if base[axis] != DEFAULT_VALUES[axis] else 1,
            -(ranks[axis][1] if axis in ranks else 0.0),
            _AXIS_ORDER.index(axis),
        ),
    )
    points: list[tuple[str, int, Coordinate]] = []
    for width in LADDER_WIDTHS:
        selected = ordered[:width]
        if family != DEFAULT_VALUES["credit"] and "credit" not in selected:
            selected = [*selected[:-1], "credit"]
        values = dict(DEFAULT_VALUES)
        for axis in selected:
            if base[axis] != DEFAULT_VALUES[axis]:
                values[axis] = base[axis]
            elif axis in ranks:
                values[axis] = ranks[axis][0]
            else:
                values = {}
                break
        if values:
            points.append((family, width, Coordinate(**values, params={})))
    return tuple(points)


def _reference_gate(reference: tuple[CompositionCell, ...]) -> CompositionGate | None:
    """The reference must learn before it can be the bar."""
    ref = _best(reference)
    if ref is not None and ref.val_acc is not None and ref.val_acc >= FLOOR:
        return None
    measured = f"{ref.val_acc:.3f} on {ref.axis}" if ref else "no measured arm"
    return CompositionGate(
        "invalid-reference",
        f"the best single-axis arm reads {measured} against the floor "
        f"{FLOOR:.2f}; a reference below the floor cannot decide the "
        "comparison",
        ref.val_acc if ref else None,
        ref.axis if ref else "",
        None,
        None,
        None,
    )


def _control_gate(
    reference: CompositionCell, controls: tuple[CompositionCell, ...]
) -> CompositionGate | None:
    """The reference's second seed must reproduce it within the control band."""
    ref_acc = cast("float", reference.val_acc)  # the caller narrowed it
    control = _best(controls)
    if control is None or control.val_acc is None:
        return CompositionGate(
            "invalid-control",
            "the reference's second seed did not measure; an apparatus failure "
            "invalidates the run, not the composition thesis",
            reference.val_acc,
            reference.axis,
            None,
            None,
            None,
        )
    control_acc = cast("float", control.val_acc)  # guarded above
    drift = abs(control_acc - ref_acc)
    if drift <= CONTROL_TOL:
        return None
    return CompositionGate(
        "invalid-control",
        f"the reference's second seed reads {control_acc:.3f} against "
        f"{ref_acc:.3f} on the screen seed (drift {drift:.3f} > "
        f"{CONTROL_TOL:.2f}); the box is not stable enough to compare",
        ref_acc,
        reference.axis,
        None,
        None,
        None,
    )


def _ladder_gate(
    *,
    reference: CompositionCell,
    family: str,
    best_screen: CompositionCell | None,
    best_ladder: CompositionCell | None,
    confirmation: CompositionCell | None,
    values: tuple[float | None, str, float | None, str, float | None],
) -> CompositionGate | None:
    """The family ladder's bar and its disjoint-seed confirmation."""
    ref_acc = cast("float", reference.val_acc)  # the caller narrowed it
    if best_ladder is None or best_ladder.val_acc is None:
        return None
    ladder_acc = cast("float", best_ladder.val_acc)
    bar = ref_acc + DELTA
    if best_ladder.val_acc >= bar:
        if confirmation is None or confirmation.val_acc is None:
            return CompositionGate(
                "coordinate",
                f"the family ladder's best ({ladder_acc:.3f} at "
                f"width {best_ladder.width}) clears the {bar:.3f} bar but its "
                "confirmation seed did not train; a promotion needs the "
                "disjoint-seed confirmation",
                *values,
            )
        confirmation_acc = cast("float", confirmation.val_acc)
        if confirmation_acc < bar:
            return CompositionGate(
                "coordinate",
                f"the family ladder's best reads {ladder_acc:.3f} at "
                f"width {best_ladder.width} on the screen seed but "
                f"{confirmation_acc:.3f} on the confirmation seed, below "
                f"the {bar:.3f} bar; the point did not reproduce, so a wider "
                "family ladder is the trigger, not a promotion",
                *values,
            )
        return CompositionGate(
            "promote",
            f"the best single-axis default reads {ref_acc:.3f} "
            f"({reference.axis}); the best-growing family ({family}) clears the "
            f"pre-registered bar at {ladder_acc:.3f} (width "
            f"{best_ladder.width}, +"
            f"{(ladder_acc - ref_acc) * 100:.1f} pp against "
            f"delta {DELTA * 100:.0f} pp) and its confirmation seed repeats it "
            f"({confirmation_acc:.3f}). F2 is a five-seed replication on a "
            "second task family, not a claim",
            *values,
        )
    if (
        best_screen is not None
        and best_screen.val_acc is not None
        and best_screen.val_acc >= bar
    ):
        return CompositionGate(
            "coordinate",
            f"the screen's best composition reads {best_screen.val_acc:.3f} (+"
            f"{(best_screen.val_acc - ref_acc) * 100:.1f} pp) but its "
            f"family ladder's best reads {ladder_acc:.3f} at width "
            f"{best_ladder.width}, below the {bar:.3f} bar; the screen winner "
            "did not survive its own ladder, so F2's wider ladder is the "
            "trigger, not a promotion",
            *values,
        )
    return None


def _screen_gate(
    reference: CompositionCell,
    screen: tuple[CompositionCell, ...],
    ladder: tuple[CompositionCell, ...],
) -> CompositionGate:
    """The screen and the family ladder, measured against the bar."""
    ref_acc = cast("float", reference.val_acc)  # the caller narrowed it
    measured = [
        cell for cell in screen if not cell.refused and cell.val_acc is not None
    ]
    best_screen = _best(screen)
    main_ladder = [cell for cell in ladder if cell.seed == SCREEN_SEED]
    confirm_ladder = [cell for cell in ladder if cell.seed != SCREEN_SEED]
    best_ladder = _best(main_ladder)
    confirmation = _best(confirm_ladder)
    family = _best_family(screen)
    if len(measured) < MIN_SCREEN_MEASURED:
        return CompositionGate(
            "coordinate",
            f"only {len(measured)} of {len(screen)} screen cells trained "
            f"(minimum {MIN_SCREEN_MEASURED}); the refusal rate is the screen "
            "result, and a narrower axis set is the re-open command",
            ref_acc,
            reference.axis,
            best_screen.val_acc if best_screen else None,
            None,
            best_ladder.val_acc if best_ladder else None,
        )
    if family is None:
        return CompositionGate(
            "coordinate",
            "no credit family had two measured screen cells, so no family "
            "could be laddered; a deterministic family grouping or a larger "
            "screen is the re-open command",
            ref_acc,
            reference.axis,
            best_screen.val_acc if best_screen else None,
            None,
            best_ladder.val_acc if best_ladder else None,
        )
    values = (
        ref_acc,
        reference.axis,
        best_screen.val_acc if best_screen else None,
        family,
        best_ladder.val_acc if best_ladder else None,
    )
    ladder_verdict = _ladder_gate(
        reference=reference,
        family=family,
        best_screen=best_screen,
        best_ladder=best_ladder,
        confirmation=confirmation,
        values=values,
    )
    if ladder_verdict is not None:
        return ladder_verdict
    screen_now = best_screen.val_acc if best_screen else float("nan")
    ladder_now = cast("float", best_ladder.val_acc) if best_ladder else float("nan")
    spread = (
        abs(cast("float", confirmation.val_acc) - ladder_now)
        if confirmation is not None and confirmation.val_acc is not None
        else None
    )
    seed_note = (
        f"its confirmation seed reads {cast('float', confirmation.val_acc):.3f}, a "
        f"{spread * 100:.1f} pp seed spread"
        if confirmation is not None
        and confirmation.val_acc is not None
        and spread is not None
        else "its confirmation seed did not measure"
    )
    return CompositionGate(
        "refuse",
        f"composition is flat at this box: the best single-axis default reads "
        f"{ref_acc:.3f} ({reference.axis}); the screen's best "
        f"composition reads {screen_now:.3f} and the {family} family ladder's "
        f"best reads {ladder_now:.3f} at width "
        f"{best_ladder.width if best_ladder else '—'}, short of the "
        f"{ref_acc + DELTA:.3f} bar (delta {DELTA * 100:.0f} pp), "
        f"while {seed_note} -- the seed spread is wider than delta, so F2's "
        f"five seeds are the trigger. The knob box is {len(measured)}/"
        f"{len(screen)} measured screen cells, one seed, one epoch, 57 "
        "forward-equivalents. Re-open: a matched-parameter composition (same "
        "parameter count as the reference), a real task family (MNIST/CIFAR), or "
        "a wider axis set",
        *values,
    )


def _gate(
    *,
    reference: tuple[CompositionCell, ...],
    controls: tuple[CompositionCell, ...],
    screen: tuple[CompositionCell, ...],
    ladder: tuple[CompositionCell, ...],
) -> CompositionGate:
    """Controls first, then the screen and the family ladder against the bar."""
    ref = _best(reference)
    reference_failure = _reference_gate(reference)
    if reference_failure is not None or ref is None or ref.val_acc is None:
        return reference_failure or CompositionGate(
            "invalid-reference", "no measured reference arm", None, "", None, None, None
        )
    control_failure = _control_gate(ref, controls)
    if control_failure is not None:
        return control_failure
    return _screen_gate(ref, screen, ladder)


def _box(device: str) -> dict[str, object]:
    """The declared knob box, carried by every table and the registration."""
    return {
        "task": TASK_ID,
        "fidelity": "L0",
        "device": device,
        "epochs": 1,
        "batch_limit": BATCH_LIMIT,
        "forward_equivalents": BATCH_LIMIT,
        "param_budget": PARAM_BUDGET,
        "screen_cells": SCREEN_CELLS,
        "scan_limit": SCAN_LIMIT,
        "screen_seed": SCREEN_SEED,
        "control_seed": CONTROL_SEED,
        "delta": DELTA,
        "floor": FLOOR,
        "control_tol": CONTROL_TOL,
        "ladder_widths": LADDER_WIDTHS,
        "default": DEFAULT_VALUES,
    }


def _registration(device: str) -> dict[str, object]:
    """The pre-registration written before the first cell is measured."""
    return {
        "claim": (
            "a legal 6-axis composition beats the best single-axis default "
            "by at least delta at matched forward-equivalents"
        ),
        "metric": "val_acc",
        "threshold": DELTA,
        "alpha": 0.05,
        "min_seeds": 1,
        "created": "2026-11-16",
        "box": _box(device),
        "note": (
            "screening registration: a promotion is F2's five-seed "
            "replication, not a claim"
        ),
    }


def write_registration(output_dir: str | Path, *, device: str = DEVICE) -> Path:
    """Write the registration before any cell; never overwrite an existing one."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "composition.registered.json"
    if not path.exists():
        if COMMITTED_REGISTRATION.exists():
            path.write_text(COMMITTED_REGISTRATION.read_text(encoding="utf-8"))
        else:
            path.write_text(json.dumps(_registration(device), indent=2) + "\n")
    return path


def _load_registration(path: str | Path | None, *, device: str) -> dict[str, object]:
    """The committed registration when present, else the module's constants."""
    for candidate in (path, COMMITTED_REGISTRATION):
        if candidate is not None and Path(candidate).exists():
            return json.loads(Path(candidate).read_text(encoding="utf-8"))
    return _registration(device)


def _report(
    *,
    reference: tuple[CompositionCell, ...],
    controls: tuple[CompositionCell, ...],
    screen: tuple[CompositionCell, ...],
    ladder: tuple[CompositionCell, ...],
    registration: dict[str, object],
    device: str,
) -> CompositionReport:
    """Build the table and its verdict from the measured rows."""
    gate = _gate(
        reference=reference,
        controls=controls,
        screen=screen,
        ladder=ladder,
    )
    return CompositionReport(
        stage="composition",
        box=_box(device),
        registration=registration,
        reference=reference,
        controls=controls,
        screen=screen,
        ladder=ladder,
        cells=(*reference, *controls, *screen, *ladder),
        verdict=gate.verdict,
        reason=gate.reason,
        reference_acc=gate.reference_acc,
        reference_axis=gate.reference_axis,
        best_screen_acc=gate.best_screen_acc,
        best_family=gate.best_family,
        best_ladder_acc=gate.best_ladder_acc,
    )


def run_composition_ladder(
    *,
    device: str = DEVICE,
    progress: str | Path | None = None,
    output_dir: str | Path = "results/t93_f1",
) -> CompositionReport:
    """Register the box, measure the reference, screen 50 cells, ladder one family."""
    seed_all_registries()
    registration = _load_registration(
        write_registration(output_dir, device=device), device=device
    )
    done = _resume(progress)
    spec = _spec()
    space = search_space_from_spec(spec, tasks=(TASK_ID,))

    reference = tuple(
        _measure(
            done,
            stage="reference",
            axis=axis,
            coord=coord,
            seed=SCREEN_SEED,
            progress=progress,
        )
        for axis, _primitive, coord in _single_axis_arms(space)
    )
    best = _best(reference)
    controls: tuple[CompositionCell, ...] = ()
    if best is not None:
        controls = (
            _measure(
                done,
                stage="control",
                axis=best.axis,
                coord=best.coordinate(),
                seed=CONTROL_SEED,
                progress=progress,
            ),
        )
    screen = tuple(
        _measure(
            done,
            stage="screen",
            axis="",
            coord=coord,
            seed=SCREEN_SEED,
            progress=progress,
        )
        for coord in _sample_screen(space, spec)
    )
    ladder_cells = [
        _measure(
            done,
            stage="ladder",
            axis=family,
            coord=coord,
            seed=SCREEN_SEED,
            progress=progress,
        )
        for family, _width_value, coord in _ladder_coordinates(screen, reference)
    ]
    best_ladder = _best([cell for cell in ladder_cells if cell.seed == SCREEN_SEED])
    if best_ladder is not None:
        ladder_cells.append(
            _measure(
                done,
                stage="ladder",
                axis=best_ladder.axis,
                coord=best_ladder.coordinate(),
                seed=CONTROL_SEED,
                progress=progress,
            )
        )
    ladder = tuple(ladder_cells)
    return _report(
        reference=reference,
        controls=controls,
        screen=screen,
        ladder=ladder,
        registration=registration,
        device=device,
    )


def replay_composition_ladder(
    *,
    progress: str | Path,
    registration_path: str | Path | None = None,
    device: str = DEVICE,
) -> CompositionReport:
    """Recompute the tables and the gate from the cell log, without training."""
    cells = read_cells(progress)
    if not cells:
        raise RuntimeError(f"no cells in {progress}; run the ladder first")
    registration = _load_registration(registration_path, device=device)
    return _report(
        reference=tuple(cell for cell in cells if cell.stage == "reference"),
        controls=tuple(cell for cell in cells if cell.stage == "control"),
        screen=tuple(cell for cell in cells if cell.stage == "screen"),
        ladder=tuple(cell for cell in cells if cell.stage == "ladder"),
        registration=registration,
        device=device,
    )


def _accuracy(value: float | None, refused: bool) -> str:
    """A table cell: the accuracy, or the refusal marker."""
    if refused or value is None:
        return "refused"
    return f"{value:.3f}"


def _markdown(report: CompositionReport) -> str:
    """The table a third party can read, with its rulers and command."""
    lines = [
        "# F1 composition ladder -- 6-axis composition vs the best single axis",
        "",
        f"**Box.** {report.box}",
        "",
        "**Rulers.** matched forward-equivalents (57 batches per cell), "
        "validation accuracy on the held-out split, parameter ceiling, and the "
        "walltime beside each row. The delta is one percentage point, written "
        "in `composition.registered.json` before the first cell.",
        "",
        "## Reference -- every legal single-axis arm",
        "",
        "| axis | primitive | width | val acc | params | walltime (s) |",
        "|---|---|---|---|---|---|",
    ]
    for cell in report.reference:
        primitive = cell.axis if cell.axis else "default"
        lines.append(
            f"| {cell.axis or 'default'} | {primitive} | {cell.width} | "
            f"{_accuracy(cell.val_acc, cell.refused)} | "
            f"{cell.param_count if cell.param_count is not None else '—'} | "
            f"{f'{cell.walltime_s:.2f}' if cell.walltime_s is not None else '—'} |"
        )
    lines.extend([
        "",
        "## Control -- the reference's second seed",
        "",
        "| axis | seed | val acc | walltime (s) |",
        "|---|---|---|---|",
    ])
    for cell in report.controls:
        lines.append(
            f"| {cell.axis or 'default'} | {cell.seed} | "
            f"{_accuracy(cell.val_acc, cell.refused)} | "
            f"{f'{cell.walltime_s:.2f}' if cell.walltime_s is not None else '—'} |"
        )
    lines.extend([
        "",
        "## Screen -- 50 legal multi-axis cells",
        "",
        "| substrate | geometry | dynamics | plasticity | credit | update | "
        "width | val acc | walltime (s) |",
        "|---|---|---|---|---|---|---|---|---|",
    ])
    for cell in report.screen:
        shown = _accuracy(cell.val_acc, cell.refused)
        if cell.refused and cell.reason:
            shown = f"refused ({cell.reason[:48]})"
        lines.append(
            f"| {cell.substrate} | {cell.geometry} | {cell.dynamics} | "
            f"{cell.plasticity} | {cell.credit} | {cell.update} | "
            f"{cell.width} | {shown} | "
            f"{f'{cell.walltime_s:.2f}' if cell.walltime_s is not None else '—'} |"
        )
    lines.extend([
        "",
        "## Family ladder -- the best-looking credit family at widths 2/4/6",
        "",
        "| family | seed | width | val acc | walltime (s) |",
        "|---|---|---|---|---|",
    ])
    for cell in report.ladder:
        lines.append(
            f"| {cell.axis} | {cell.seed} | {cell.width} | "
            f"{_accuracy(cell.val_acc, cell.refused)} | "
            f"{f'{cell.walltime_s:.2f}' if cell.walltime_s is not None else '—'} |"
        )
    lines.extend([
        "",
        f"**Verdict: {report.verdict}** -- {report.reason}",
        "",
        "**Rulers, restated.** reference = best measured single-axis arm; "
        "bar = reference + delta; best screen = best multi-axis cell; family = "
        "credit group with the highest median screen accuracy (n >= 2); "
        "ladder = width 2/4/6 built from the family's best cell.",
        "",
        "Command: `uv run python -m computronium.validation."
        f"composition_ladder --device {report.box.get('device')}`; replay "
        "from the cell log: `... --replay`.",
        "",
    ])
    return "\n".join(lines)


def write_report(report: CompositionReport, output_dir: str | Path) -> Path:
    """Write ``composition.json`` and ``composition.md``; return the JSON path."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "stage": report.stage,
        "box": report.box,
        "registration": report.registration,
        "reference": [_as_cell_dict(cell) for cell in report.reference],
        "controls": [_as_cell_dict(cell) for cell in report.controls],
        "screen": [_as_cell_dict(cell) for cell in report.screen],
        "ladder": [_as_cell_dict(cell) for cell in report.ladder],
        "verdict": report.verdict,
        "reason": report.reason,
        "reference_acc": report.reference_acc,
        "reference_axis": report.reference_axis,
        "best_screen_acc": report.best_screen_acc,
        "best_family": report.best_family,
        "best_ladder_acc": report.best_ladder_acc,
    }
    path = output_dir / "composition.json"
    path.write_text(json.dumps(payload, indent=2) + "\n")
    (output_dir / "composition.md").write_text(_markdown(report))
    return path


def _main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--device", default="cuda" if torch.cuda.is_available() else DEVICE
    )
    parser.add_argument(
        "--replay", action="store_true", help="recompute the gate from the cell log"
    )
    parser.add_argument("--out", default="results/t93_f1")
    args = parser.parse_args()
    progress = Path(args.out) / "composition.cells.jsonl"
    if args.replay:
        report = replay_composition_ladder(
            progress=progress,
            registration_path=Path(args.out) / "composition.registered.json",
            device=args.device,
        )
    else:
        report = run_composition_ladder(
            device=args.device, progress=progress, output_dir=args.out
        )
    path = write_report(report, args.out)
    print(f"wrote {path}")
    print(f"verdict: {report.verdict} -- {report.reason}")


if __name__ == "__main__":
    _main()
