"""Legal-coordinate combination smoke (TODO91 S6).

The selection surface is complete one axis at a time (S1–S5); what no ticket
proved is that the *combinations* the declared rules admit compose and train.
Scanning the factorial is not the answer: on `iris` the declared space is
665,280 cells and only ~8 % satisfy the void constraints, and a paged walk
re-derives that rejection per candidate.

So this module enumerates the **declared** legal space directly instead. The
void-constraint engine is cheap (~3 µs/candidate, measured), so the whole
product costs seconds; the expensive part (compose) runs only on the cells the
cover admits. A coordinate value no declared cell holds is reported as
``unplaced`` with the rule that refuses it — never inferred, never silent.

Admission is the two declared filters, and only those:

1. ``_void_pass`` over ``CONSTRAINTS_REGISTRY`` (structural legality),
2. ``_is_geometry_task_compatible`` (the geometry × task-shape rule).

Every admitted cell then goes through the real evaluator (``cell_record``:
compose, substrate, trainer, metrics, gate verdict), so a defect in any stage
surfaces as a FAIL row that names its cause. A planner that composed cells
would filter the very defects this ticket exists to find.
"""

from __future__ import annotations

import random
import time
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from itertools import product
from typing import Any, Final

__all__ = [
    "AXIS_ORDER",
    "CombinationReport",
    "CombinationResult",
    "CoverCell",
    "DeclaredSpace",
    "declared_space",
    "plan_cover",
    "render_json",
    "run_combinations",
    "smoke_task",
]

AXIS_ORDER: Final[tuple[str, ...]] = (
    "substrate",
    "geometry",
    "dynamics",
    "plasticity",
    "credit",
    "update",
)
DEFAULT_PARAM_BUDGET: Final[int] = 50_000
SHAPE_RULE: Final[str] = "geometry x task shape rule"

# The canonical smoke cell: the most standard coordinate each axis offers. The
# per-task smoke picks the declared-legal cell matching the most of these, so
# the cell it trains is the plain composition (backprop, no settling, no
# plasticity), not whichever dated broadcast full-graph task still trains.
CANONICAL_CELL: Final[dict[str, str]] = {
    "substrate": "digital",
    "geometry": "",
    "dynamics": "instantaneous",
    "plasticity": "null",
    "credit": "gradient",
    "update": "adam",
}

type Predicate = Callable[[tuple[str, ...]], Any]
type CompiledConstraints = Sequence[tuple[str, Predicate]]


def _key(axis: str, name: str) -> str:
    return f"{axis}={name}"


def _keys(selection: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(
        _key(axis, name) for axis, name in zip(AXIS_ORDER, selection, strict=True)
    )


def _seeded() -> None:
    from computronium.experiment.schema import seed_all_registries

    seed_all_registries()


def _axis_names() -> dict[str, list[str]]:
    from computronium.experiment.schema.axis import AXES_REGISTRIES, StructuralAxis

    return {
        axis: list(AXES_REGISTRIES[StructuralAxis[axis.upper()]].keys())
        for axis in AXIS_ORDER
    }


def _universe(names: dict[str, list[str]]) -> tuple[str, ...]:
    return tuple(_key(axis, name) for axis in AXIS_ORDER for name in names[axis])


@dataclass(frozen=True, slots=True)
class DeclaredSpace:
    """The declared legal cells for one task and the coordinates they reach."""

    task_id: str
    input_shape: tuple[int, ...]
    cells: tuple[tuple[str, ...], ...]
    reached: frozenset[str]
    refused: tuple[tuple[str, str], ...]
    probes: int
    scan_walltime_s: float


def _target_compatible(axis: str, name: str, target_kind: str) -> bool:
    """Whether the axis row can read this task's target kind.

    The rule lives in ``search_space`` beside the geometry × shape rule, so the
    planner and the declared-space command read one implementation.
    """
    from computronium.experiment.kernel.search_space import (
        _is_target_lane_compatible,
    )

    return _is_target_lane_compatible(axis, name, target_kind)


def _refutation(
    axis: str,
    name: str,
    task_id: str,
    axes: list[list[str]],
    indep: CompiledConstraints,
    dep: CompiledConstraints,
) -> str:
    """The rule that refuses a coordinate value in every completion.

    First looks for a constraint that rejects *every* completion of the fixed
    value: that is the refutation, and it is exact. Otherwise no single rule
    blocks the value — the whole sub-space is refused by the constraints
    jointly — so the dominant first violator is reported with its share.
    """
    from computronium.experiment.kernel.search_space import _void_rejection

    completions = list(
        product(
            *(
                [name] if candidate == axis else values
                for candidate, values in zip(AXIS_ORDER, axes, strict=True)
            )
        )
    )

    for constraint_name, fn in indep:
        if all(not fn((*values, "")) for values in completions):
            return (
                f"void constraint: {constraint_name} "
                f"(rejects all {len(completions)} completions)"
            )
    for constraint_name, fn in dep:
        if all(not fn((*values, task_id)) for values in completions):
            return (
                f"void constraint: {constraint_name} "
                f"(rejects all {len(completions)} completions)"
            )

    reasons: Counter[str] = Counter()
    for values in completions:
        reason = _void_rejection(indep, dep, values, task_id)
        if reason is not None:
            reasons[reason] += 1
    if not reasons:
        return "no declared cell (refutation found none)"
    rule, count = reasons.most_common(1)[0]
    return f"{rule} ({count}/{len(completions)} completions)"


GEOMETRY_INDEX: Final[int] = AXIS_ORDER.index("geometry")


def _declared_names(
    names: dict[str, list[str]], shape: Any, task_id: str
) -> tuple[dict[str, tuple[str, ...]], list[list[str]]]:
    """Per-axis names the task's geometry rule and target kind admit.

    Returns the target-lane refusals (so the refusal report can name the rule
    per coordinate) and the axes the product is taken over.
    """
    from computronium.experiment.kernel.search_space import (
        _is_geometry_task_compatible,
    )

    target_refused = {
        axis: tuple(
            name
            for name in names[axis]
            if not _target_compatible(axis, name, shape.target_kind)
        )
        for axis in AXIS_ORDER
    }
    axes = [
        (
            [
                geometry
                for geometry in names["geometry"]
                if _is_geometry_task_compatible(geometry, shape, task_id)
            ]
            if axis == "geometry"
            else [name for name in names[axis] if name not in target_refused[axis]]
        )
        for axis in AXIS_ORDER
    ]
    return target_refused, axes


def declared_space(
    task_id: str,
    *,
    names: dict[str, list[str]] | None = None,
) -> DeclaredSpace:
    """Enumerate every declared legal cell for one task.

    Args:
        task_id: Task the geometry × shape rule and the task-dependent
            constraints are evaluated for.
        names: Axis coordinate names; read from the registry when omitted.

    Returns:
        The space, the coordinates it reaches, and the rule refusing each
        coordinate it cannot reach.
    """
    _seeded()
    from computronium.experiment.kernel.evaluate import (
        EvaluationError,
        TaskShape,
        task_shape,
    )
    from computronium.experiment.kernel.search_space import (
        TARGET_LANE_RULE,
        _compiled_void_constraints,
        _void_pass,
    )

    names = _axis_names() if names is None else names
    try:
        shape = task_shape(task_id, "cpu")
    except EvaluationError:
        # No declared input extent (a batched graph task): the geometry ×
        # shape rule still applies with an empty shape, so conv/causal refuse
        # and the domain branch selects graph geometry.
        shape = TaskShape(input_shape=(), output_dim=0)

    target_refused, axes = _declared_names(names, shape, task_id)

    start = time.perf_counter()
    indep, dep = _compiled_void_constraints()
    cells: list[tuple[str, ...]] = []
    probes = 0
    for values in product(*(axis_values for axis_values in axes)):
        probes += 1
        if _void_pass(indep, dep, values, task_id):
            cells.append(values)
    scan_walltime = time.perf_counter() - start

    reached = {key for cell in cells for key in _keys(cell)}
    refused: list[tuple[str, str]] = []
    for key in _universe(names):
        if key in reached:
            continue
        axis, name = key.split("=", 1)
        if name in target_refused[axis]:
            reason = TARGET_LANE_RULE
        elif name not in axes[GEOMETRY_INDEX] and axis == "geometry":
            reason = SHAPE_RULE
        else:
            reason = _refutation(axis, name, task_id, axes, indep, dep)
        refused.append((key, reason))

    return DeclaredSpace(
        task_id=task_id,
        input_shape=shape.input_shape,
        cells=tuple(cells),
        reached=frozenset(reached),
        refused=tuple(refused),
        probes=probes,
        scan_walltime_s=scan_walltime,
    )


@dataclass(frozen=True, slots=True)
class CoverCell:
    """One cell the cover admits: which task it runs and what it covers."""

    task_id: str
    selection: tuple[str, ...]

    @property
    def covers(self) -> tuple[str, ...]:
        return _keys(self.selection)


def plan_cover(
    spaces: tuple[DeclaredSpace, ...],
    *,
    seed: int = 0,
    budget: int | None = None,
) -> tuple[CoverCell, ...]:
    """Greedily cover every reachable coordinate across the given spaces.

    Picks, at each step, the rarest uncovered coordinate and then the cell that
    covers the most still-uncovered coordinates — so the cover is bounded by
    the widest axis (12 update rules), not by the factorial.

    Args:
        spaces: The declared spaces to draw cells from.
        seed: Seed for the tie-break order; the cover is reproducible from it.
        budget: Maximum cells. ``None`` covers every reachable coordinate.

    Returns:
        The selected cells, in admission order.
    """
    rng = random.Random(seed)  # ruff: ignore[suspicious-non-cryptographic-random-usage]
    index: dict[str, list[CoverCell]] = {}
    for space in spaces:
        cells = list(space.cells)
        rng.shuffle(cells)
        for selection in cells:
            cell = CoverCell(task_id=space.task_id, selection=selection)
            for key in cell.covers:
                index.setdefault(key, []).append(cell)

    uncovered = set(index)
    selected: list[CoverCell] = []
    while uncovered and (budget is None or len(selected) < budget):
        key = min(uncovered, key=lambda k: (len(index[k]), k))
        best = max(
            index[key],
            key=lambda cell: len(set(cell.covers) & uncovered),
        )
        gain = set(best.covers) & uncovered
        if not gain:
            break
        selected.append(best)
        uncovered -= gain
    return tuple(selected)


@dataclass(frozen=True, slots=True)
class CombinationResult:
    """One admitted cell's smoke result."""

    task_id: str
    selection: tuple[str, ...]
    verdict: str
    cause: str | None
    defect: str | None
    walltime_s: float

    @property
    def passed(self) -> bool:
        return self.verdict == "PASS"

    @property
    def covers(self) -> tuple[str, ...]:
        return _keys(self.selection)

    def to_dict(self) -> dict[str, object]:
        return {
            "task_id": self.task_id,
            "coordinate": dict(zip(AXIS_ORDER, self.selection, strict=True)),
            "covers": list(self.covers),
            "verdict": self.verdict,
            "cause": self.cause,
            "defect": self.defect,
            "walltime_s": round(self.walltime_s, 4),
        }


@dataclass(frozen=True, slots=True)
class CombinationReport:
    """A planned-and-trained legal-coordinate smoke at a declared budget."""

    task_ids: tuple[str, ...]
    seed: int
    budget: int
    probes: int
    scan_walltime_s: float
    train_walltime_s: float
    universe: tuple[str, ...]
    results: tuple[CombinationResult, ...]
    refused: tuple[tuple[str, str, str], ...]

    @property
    def failures(self) -> tuple[CombinationResult, ...]:
        return tuple(result for result in self.results if not result.passed)

    @property
    def covered(self) -> tuple[str, ...]:
        """Coordinates covered by a cell that actually trained."""
        return tuple(
            key for result in self.results if result.passed for key in result.covers
        )

    @property
    def uncovered(self) -> tuple[str, ...]:
        """Reachable coordinates the budget did not admit."""
        covered = set(self.covered)
        refused = {key for _task, key, _rule in self.refused}
        return tuple(
            key for key in self.universe if key not in covered and key not in refused
        )

    def refused_rule(self, key: str) -> str:
        """The refused rule for a coordinate, noting any per-task difference."""
        return " | ".join(
            sorted({rule.split(" (")[0] for _task, k, rule in self.refused if k == key})
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "task_ids": list(self.task_ids),
            "seed": self.seed,
            "budget": self.budget,
            "probes": self.probes,
            "scan_walltime_s": round(self.scan_walltime_s, 4),
            "train_walltime_s": round(self.train_walltime_s, 4),
            "universe": len(self.universe),
            "covered": len(set(self.covered)),
            "failures": len(self.failures),
            "refused": [
                {"task_id": task, "coordinate": key, "rule": rule}
                for task, key, rule in self.refused
            ],
            "uncovered": list(self.uncovered),
            "cells": [result.to_dict() for result in self.results],
        }

    def render(self) -> str:
        covered = set(self.covered)
        unresolved = list(self.uncovered)
        refused_keys = sorted({key for _task, key, _rule in self.refused})
        lines = [
            f"Legal-coordinate combination smoke: tasks={','.join(self.task_ids)} "
            f"seed={self.seed} budget={self.budget}",
            "=" * 78,
            (
                f"Scan: {self.probes} declared cells probed in "
                f"{self.scan_walltime_s:.2f} s; admitted {len(self.results)} cells "
                f"trained in {self.train_walltime_s:.2f} s"
            ),
            (
                f"Coordinates: {len(self.universe)} declared, {len(covered)} covered, "
                f"{len(refused_keys)} refused by a rule, {len(unresolved)} uncovered"
            ),
            "",
        ]
        for result in self.results:
            label = " ".join(
                f"{axis}={name}"
                for axis, name in zip(AXIS_ORDER, result.selection, strict=True)
            )
            lines.append(
                f"{result.verdict:4} {result.walltime_s:6.2f}s {result.task_id:14} {label}"
            )
            if not result.passed:
                lines.append(f"     cause={result.cause} defect={result.defect}")
        if refused_keys:
            lines.append("")
            lines.append(
                "REFUSED coordinates (no declared cell in any task, rule named):"
            )
            lines.extend(f"  {key}: {self.refused_rule(key)}" for key in refused_keys)
        if unresolved:
            lines.append("")
            lines.append(
                "UNCOVERED coordinates (reachable, not admitted at this budget):"
            )
            lines.extend(f"  {key}" for key in unresolved)
        if self.failures:
            lines.append("")
            lines.append("FAILURES:")
            for result in self.failures:
                label = " ".join(
                    f"{axis}={name}"
                    for axis, name in zip(AXIS_ORDER, result.selection, strict=True)
                )
                lines.append(
                    f"  {result.task_id} {label}: {result.cause} — {result.defect}"
                )
        return "\n".join(lines)


def _smoke_cell(
    cell: CoverCell,
    *,
    seed: int,
    param_budget: int,
    epochs: int,
    batch_limit: int,
    device: str,
) -> CombinationResult:
    """Train one admitted cell through the real evaluator and keep the verdict."""
    from computronium.experiment.kernel.evaluate import cell_record
    from computronium.experiment.schema.coordinate import (
        Coordinate,
        Provenance,
        Schedule,
    )

    selection = dict(zip(AXIS_ORDER, cell.selection, strict=True))
    schedule = Schedule(
        fidelity="L0",
        seed=seed,
        n_seeds=1,
        epochs=epochs,
        batch_limit=batch_limit,
        budget_id="todo91-s6",
        task_id=cell.task_id,
        param_budget=param_budget,
        device=device,
        num_workers=0,
    )
    provenance = Provenance(
        env={},
        dataset=cell.task_id,
        dataset_version="surface-smoke",
        code_sha="",
        policy="legal-coordinate smoke",
        links={},
    )
    start = time.perf_counter()
    try:
        record = cell_record(Coordinate(**selection, params={}), schedule, provenance)
    except Exception as exc:  # a smoke reports the failure instead of aborting
        return CombinationResult(
            task_id=cell.task_id,
            selection=cell.selection,
            verdict="FAIL",
            cause=type(exc).__name__,
            defect=str(exc),
            walltime_s=time.perf_counter() - start,
        )
    status = record.status
    passed = status.gate_verdict.value == "PASS"
    return CombinationResult(
        task_id=cell.task_id,
        selection=cell.selection,
        verdict=status.gate_verdict.value,
        cause=None if passed else str(status.cause),
        defect=None if passed else (status.defect or None),
        walltime_s=time.perf_counter() - start,
    )


def run_combinations(
    task_ids: tuple[str, ...] = ("iris",),
    *,
    budget: int | None = 50,
    seed: int = 0,
    param_budget: int = DEFAULT_PARAM_BUDGET,
    epochs: int = 1,
    batch_limit: int = 1,
    device: str = "cpu",
) -> CombinationReport:
    """Enumerate the declared spaces, plan the cover, train each cell.

    Args:
        task_ids: Tasks whose declared spaces are joined for the cover.
        budget: Maximum cells to train; ``None`` covers every reachable
            coordinate.
        seed: Planning and training seed.
        param_budget: Parameter ceiling handed to every cell's schedule.
        epochs: Training epochs per cell (1 is the smoke).
        batch_limit: Batches per epoch (1 bounds the smoke; 0 means all).
        device: Training device.

    Returns:
        The report. A FAIL row is a defect or a missing rule, never a silent
        skip; a REFUSED coordinate names the rule that refuses it.
    """
    names = _axis_names()
    spaces = tuple(declared_space(task_id, names=names) for task_id in task_ids)
    selected = plan_cover(spaces, seed=seed, budget=budget)

    start = time.perf_counter()
    results = tuple(
        _smoke_cell(
            cell,
            seed=seed,
            param_budget=param_budget,
            epochs=epochs,
            batch_limit=batch_limit,
            device=device,
        )
        for cell in selected
    )
    reached = set().union(*(space.reached for space in spaces))
    refused = tuple(
        (space.task_id, key, rule)
        for space in spaces
        for key, rule in space.refused
        if key not in reached
    )
    return CombinationReport(
        task_ids=task_ids,
        seed=seed,
        budget=budget if budget is not None else len(selected),
        probes=sum(space.probes for space in spaces),
        scan_walltime_s=sum(space.scan_walltime_s for space in spaces),
        train_walltime_s=time.perf_counter() - start,
        universe=_universe(names),
        results=results,
        refused=refused,
    )


def smoke_task(
    task_id: str,
    *,
    seed: int = 0,
    param_budget: int = DEFAULT_PARAM_BUDGET,
    epochs: int = 1,
    batch_limit: int = 1,
    device: str = "cpu",
) -> CombinationResult:
    """Train one declared legal cell on ``task_id`` — the per-task PASS cell.

    The cell is the first declared legal selection with instantaneous dynamics
    (falling back to the first legal selection), so the smoke costs one batch
    rather than a settle loop. The task's own loader supplies the batch and the
    real evaluator supplies the verdict.

    Args:
        task_id: Task to smoke.
        seed: Schedule seed.
        param_budget: Parameter ceiling.
        epochs: Training epochs (1 is the smoke).
        batch_limit: Batches per epoch.
        device: Training device.

    Returns:
        The cell's result; ``passed`` is the gate verdict, not an inference.
    """
    from computronium.experiment.registry.task_registry import get_task_registry

    space = declared_space(task_id)
    task_spec = get_task_registry().get(task_id)
    hint = None if task_spec is None else task_spec.geometry_hint
    geometry_index = AXIS_ORDER.index("geometry")
    hinted = [cell for cell in space.cells if hint and cell[geometry_index] == hint]
    selection = max(
        hinted or list(space.cells),
        key=lambda cell: sum(
            name == CANONICAL_CELL[axis]
            for axis, name in zip(AXIS_ORDER, cell, strict=True)
        ),
    )
    return _smoke_cell(
        CoverCell(task_id=task_id, selection=selection),
        seed=seed,
        param_budget=param_budget,
        epochs=epochs,
        batch_limit=batch_limit,
        device=device,
    )


def render_json(report: CombinationReport) -> str:
    """Serialize a report for the CLI's ``--format json``."""
    import json

    return json.dumps(report.to_dict(), indent=2)
