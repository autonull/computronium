"""Shared wave execution for SimpleSurvey and LearningSurvey.

Extracts the common evaluation loop so both planners reuse one implementation.
"""

from __future__ import annotations

import contextlib
import json
import os
import random
import signal
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

    from computronium.experiment.schema.run_spec import Fidelity

import torch

from computronium.core.logging import get_logger
from computronium.experiment.evidence.store import RecordStore
from computronium.experiment.evidence.store._models import StoreConfig
from computronium.experiment.kernel.evaluate import cell_record, task_shape
from computronium.experiment.kernel.search_space import (
    iter_candidates,
    schedule_for,
)
from computronium.experiment.registry.task_registry import get_task_registry
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.coordinate import (
    Coordinate,
    DataOrigin,
    Provenance,
    Schedule,
)
from computronium.experiment.schema.record import GateVerdict
from computronium.experiment.schema.run_spec import RunSpec
from computronium.ontology.system import check_compatibility_matrix

logger = get_logger(__name__)


def _primary_metric_key(task_id: str) -> str:
    """Get the payload key for the task's primary objective."""
    try:
        registry = get_task_registry()
        spec = registry.get(task_id)
        for obj in spec.objectives:
            if obj.name == spec.primary_objective and obj.payload_key:
                return obj.payload_key
    except Exception:
        pass
    return "val_acc"


# ============================================================
# Constants
# ============================================================

MAX_PROMOTE_CELLS: int = 20
MAX_WAVE_CELLS: int = 64


# ============================================================
# Cost Model
# ============================================================

DEFAULT_COSTS: dict[str, float] = {
    "L0": 5.0,
    "L1": 30.0,
    "L2": 300.0,
}

DEFAULT_STARTUP_S = 10.0
TIMING_CACHE = Path("experiments") / ".timing.json"
MAX_PREVIEW_CELLS = 20


@dataclass(frozen=True, slots=True)
class CostModel:
    """Per-cell wall-clock time, used to size a run against its budget.

    Cells run one at a time, so this is the rate at which the budget is spent.
    """

    cost_per_cell_s: float
    startup_s: float
    measured: bool = False
    per_task: dict[str, float] | None = None

    @property
    def source(self) -> str:
        return "measured" if self.measured else "default"


def _load_cost_model(device: str, fidelity: str) -> CostModel:
    try:
        entry = json.loads(TIMING_CACHE.read_text())[f"{device}/{fidelity}"]
        return CostModel(
            cost_per_cell_s=float(entry["cost_per_cell_s"]),
            startup_s=float(entry["startup_s"]),
            measured=True,
            per_task=entry.get("per_task"),
        )
    except OSError, ValueError, KeyError, TypeError:
        return CostModel(DEFAULT_COSTS.get(fidelity, 30.0), DEFAULT_STARTUP_S)


def _save_cost_model(device: str, fidelity: str, model: CostModel) -> None:
    with contextlib.suppress(OSError, ValueError):
        TIMING_CACHE.parent.mkdir(parents=True, exist_ok=True)
        existing = json.loads(TIMING_CACHE.read_text()) if TIMING_CACHE.exists() else {}
        key = f"{device}/{fidelity}"
        data: dict[str, Any] = {
            "cost_per_cell_s": round(model.cost_per_cell_s, 3),
            "startup_s": round(model.startup_s, 3),
        }
        if model.per_task:
            data["per_task"] = {k: round(v, 3) for k, v in model.per_task.items()}
        existing[key] = data
        TIMING_CACHE.write_text(json.dumps(existing, indent=2, sort_keys=True))


def _blend(previous: CostModel, measured: CostModel) -> CostModel:
    per_task = None
    if previous.per_task and measured.per_task:
        per_task = {}
        all_tasks = set(previous.per_task.keys()) | set(measured.per_task.keys())
        for task in all_tasks:
            prev = previous.per_task.get(task)
            meas = measured.per_task.get(task)
            if prev is not None and meas is not None:
                per_task[task] = 0.5 * (prev + meas)
            elif meas is not None:
                per_task[task] = meas
            else:
                per_task[task] = prev
    elif measured.per_task:
        per_task = measured.per_task

    return CostModel(
        cost_per_cell_s=0.5 * (previous.cost_per_cell_s + measured.cost_per_cell_s),
        startup_s=0.5 * (previous.startup_s + measured.startup_s),
        measured=True,
        per_task=per_task,
    )


def _estimate_cell_count(budget_seconds: int, model: CostModel) -> int:
    """Cells that fit ``budget_seconds``, paying startup once and cell time after."""
    usable = budget_seconds - model.startup_s
    return max(1, int(usable // model.cost_per_cell_s))


# ============================================================
# Compatibility & Provenance
# ============================================================

MUTATION_AXES: list[StructuralAxis] = [
    StructuralAxis.SUBSTRATE,
    StructuralAxis.GEOMETRY,
    StructuralAxis.DYNAMICS,
    StructuralAxis.PLASTICITY,
    StructuralAxis.CREDIT,
    StructuralAxis.UPDATE,
]


def _check_coord_compatibility(coord: Coordinate) -> bool:
    violations = check_compatibility_matrix(
        coord.substrate,
        coord.geometry,
        coord.dynamics,
        coord.plasticity,
        coord.credit,
        coord.update,
    )
    return not violations


def _make_positive_control_cell(
    spec: RunSpec,
) -> tuple[Coordinate, Schedule] | None:
    """Create a known-working cell for positive control (P3).

    Uses a task-appropriate geometry based on the task's geometry_hint:
    - Vision: conv (or feedforward for digits)
    - Graph: graph
    - RL: feedforward
    - Language: causal_transformer
    - Tabular: feedforward
    """
    from computronium.experiment.kernel.search_space import schedule_for
    from computronium.experiment.registry.task_registry import get_task_registry
    from computronium.experiment.schema.coordinate import Coordinate

    task_name = spec.task_names[0]
    registry = get_task_registry()
    task_spec = registry.get(task_name)
    geometry = task_spec.geometry_hint or "feedforward"

    # Known good coordinate: digital substrate, task-appropriate geometry,
    # instantaneous dynamics, null plasticity, gradient credit, euclidean update
    coord = Coordinate(
        substrate="digital",
        geometry=geometry,
        dynamics="instantaneous",
        plasticity="null",
        credit="gradient",
        update="euclidean",
        params={},
    )

    # Verify compatibility
    if not _check_coord_compatibility(coord):
        logger.warning("Positive control coordinate failed compatibility check")
        return None

    # The run's own first task; a run always names at least one.
    task = spec.task_names[0]
    schedule = schedule_for(spec, task, "L0")
    # The control is a one-epoch sanity check, never the run's declared depth:
    # an explicit --epochs 20 must not turn the control into a 60s-capped
    # training run that can fail and poison the run's evidence.
    return (coord, replace(schedule, epochs=1, n_seeds=1))


def _build_provenance(
    spec: RunSpec, run_id: str, data_origin: DataOrigin = DataOrigin.EXPLORATION
) -> Provenance:
    import shutil
    import subprocess

    git_path = shutil.which("git")
    code_sha = "unknown"
    if git_path:
        with contextlib.suppress(Exception):
            code_sha = subprocess.check_output(
                [git_path, "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True
            ).strip()
        with contextlib.suppress(Exception):
            if code_sha == "unknown":
                code_sha = subprocess.check_output(
                    [git_path, "rev-parse", "--short", "HEAD"],
                    stderr=subprocess.DEVNULL,
                    text=True,
                ).strip()

    dataset = spec.dataset if spec.dataset != "unknown" else spec.task_names[0]
    dataset_version = spec.dataset_version

    return Provenance(
        env={
            k: v
            for k, v in os.environ.items()
            if k.startswith(("CUDA", "TORCH", "OMP"))
        },
        dataset=dataset,
        dataset_version=dataset_version,
        code_sha=code_sha,
        policy="simple_survey",
        links={"run_id": run_id},
        data_origin=data_origin,
    )


# ============================================================
# Planner Protocol & Implementations
# ============================================================


class Planner(Protocol):
    """Protocol for cell planners (static or policy-driven).

    Planners are iterable streams of (Coordinate, Schedule) pairs.
    ``run_waves`` resizes the next wave with ``_set_wave_size`` before taking
    ``iter(planner)``, and reads ``search_space`` to size the ladder stages.
    """

    search_space: Any

    def __iter__(self) -> Iterator[tuple[Coordinate, Schedule]]:
        """Return an iterator of (Coordinate, Schedule) for the next wave."""
        ...

    def _set_wave_size(self, n: int) -> None:
        """Set how many cells the next wave yields."""
        ...

    def mark_seen(self, measurement_key: str) -> None:
        """Declare a cell already measured, so the planner never re-proposes it."""
        ...

    def observe(self, record: Any) -> None:
        """Feed a completed record back to the planner."""
        ...

    def after_wave(self) -> None:
        """Called after each wave; can trigger fidelity promotion etc."""
        ...


class StaticPlanner:
    """SimpleSurvey's deterministic planner: fixed affine permutation prefix."""

    def __init__(
        self,
        spec: RunSpec,
        fidelity: str,
        tasks: Sequence[str],
        seed: int,
        search_space,
        promote_from: str | None = None,
        promote_top: int = 20,
        resume_from: str | None = None,
    ):
        self.spec = spec
        self.fidelity = fidelity
        self.tasks = tasks
        self.seed = seed
        self.search_space = search_space
        self.promote_from = promote_from
        self.promote_top = promote_top
        self.resume_from = resume_from

        self._offset = 0
        self._page_size = 50000
        self._exploitation_done = False
        self._top_coords: list[Coordinate] = []
        self._wave_size = 0
        self._init_resume()

    def _init_resume(self) -> None:
        self._seen: set[str] = set()
        if self.resume_from:
            try:
                store = RecordStore(StoreConfig(path=Path(self.resume_from)))
                with store:
                    records = store.query_records()
                    self._seen = {r.measurement_key for r in records}
                logger.info(
                    "Resume: skipping %d already-measured cells", len(self._seen)
                )
            except Exception as exc:
                logger.warning(
                    "Could not read resume store %s: %s", self.resume_from, exc
                )

    def _load_promotion_coords(self) -> list[Coordinate]:
        if not self.promote_from:
            return []
        try:
            store = RecordStore(StoreConfig(path=Path(self.promote_from)))
            with store:
                records = store.query_records(
                    gate_verdict=GateVerdict.PASS_, quarantine=False
                )
            valid_records = [
                r for r in records if r.payload.get("normalized_metric") is not None
            ]
            if not valid_records:
                logger.warning(
                    "Promotion requested but no PASS records with normalized_metric found"
                )
                return []

            def _norm_val(record):
                return record.payload.get("normalized_metric", 0.0)

            valid_records.sort(key=_norm_val, reverse=True)

            promoted_count = min(self.promote_top, len(valid_records))
            logger.info(
                "Promoted %d of top %d coordinates from prior store",
                promoted_count,
                len(valid_records),
            )

            if promoted_count == 0:
                raise ValueError("Promotion requested but produced zero coordinates")

            coords = []
            for record in valid_records[:promoted_count]:
                coords.append(Coordinate.from_record(record))
            return coords
        except Exception as exc:
            logger.debug(
                "Prior store unavailable, falling back to random exploration: %s", exc
            )
            return []

    def _mutate_around(
        self, top_coords: list[Coordinate], n: int
    ) -> list[tuple[Coordinate, Schedule]]:
        mutated_cells: list[tuple[Coordinate, Schedule]] = []

        if not top_coords:
            return mutated_cells

        per_coord = max(1, n // len(top_coords))

        for coord in top_coords:
            for _ in range(per_coord):
                if len(mutated_cells) >= n:
                    break

                k = random.randint(1, 2)
                axes_to_mutate = random.sample(MUTATION_AXES, k)

                new_values = {
                    "substrate": coord.substrate,
                    "geometry": coord.geometry,
                    "dynamics": coord.dynamics,
                    "plasticity": coord.plasticity,
                    "credit": coord.credit,
                    "update": coord.update,
                }

                for axis in axes_to_mutate:
                    primitives = self.search_space.primitives(axis)
                    if primitives:
                        new_values[axis.value] = random.choice(primitives)

                mutated_coord = Coordinate(
                    substrate=new_values["substrate"],
                    geometry=new_values["geometry"],
                    dynamics=new_values["dynamics"],
                    plasticity=new_values["plasticity"],
                    credit=new_values["credit"],
                    update=new_values["update"],
                    params=dict(coord.params),
                )

                if not _check_coord_compatibility(mutated_coord):
                    continue

                task = random.choice(self.tasks)
                schedule = schedule_for(self.spec, task, self.fidelity)

                measurement_key = mutated_coord.measurement_key(schedule)
                if measurement_key in self._seen:
                    continue
                self._seen.add(measurement_key)

                mutated_cells.append((mutated_coord, schedule))

        return mutated_cells

    def _random_explore(self, n: int) -> list[tuple[Coordinate, Schedule]]:
        cells: list[tuple[Coordinate, Schedule]] = []

        while len(cells) < n:
            page_cells: list[tuple[Coordinate, Schedule]] = []

            for coord, schedule in iter_candidates(
                self.spec,
                self.search_space,
                shape=task_shape,
                max_scan=self._page_size,
                check_composable=True,
                offset=self._offset,
            ):
                if not _check_coord_compatibility(coord):
                    continue

                cell_schedule = schedule_for(self.spec, schedule.task_id, self.fidelity)

                measurement_key = coord.measurement_key(cell_schedule)
                if measurement_key in self._seen:
                    continue
                self._seen.add(measurement_key)

                page_cells.append((coord, cell_schedule))

                if len(cells) + len(page_cells) >= n:
                    break

            if not page_cells:
                break

            cells.extend(page_cells)
            self._offset += self._page_size

            if len(page_cells) < self._page_size:
                break

        if len(cells) < n:
            logger.warning(
                "Planned %d cells but only found %d valid cells (%.1f%% of target)",
                n,
                len(cells),
                100.0 * len(cells) / max(1, n),
            )

        return cells[:n]

    def __iter__(self):
        """Iterator of (Coordinate, Schedule) for exploration/exploitation."""
        # Exploitation phase: mutate around promoted coordinates
        if not self._exploitation_done and self.promote_from:
            self._top_coords = self._load_promotion_coords()
            if self._top_coords:
                yield from self._mutate_around(self._top_coords, self._wave_size // 2)
            self._exploitation_done = True

        # Exploration phase: random exploration
        yield from self._random_explore(self._wave_size)

    def _set_wave_size(self, n: int) -> None:
        """Set the number of cells to yield this wave."""
        self._wave_size = n

    def propose(self, n: int, *, seen: set[str]) -> list[tuple[Coordinate, Schedule]]:
        """Legacy batch interface (deprecated)."""
        self._set_wave_size(n)
        self._seen.update(seen)
        return list(iter(self))

    def observe(self, record: Any) -> None:
        pass

    def mark_seen(self, measurement_key: str) -> None:
        self._seen.add(measurement_key)

    def after_wave(self) -> None:
        pass


class PolicyPlanner:
    """LearningSurvey's adaptive planner using ModelBasedPolicy."""

    def __init__(
        self,
        spec: RunSpec,
        fidelity: str,
        tasks: Sequence[str],
        seed: int,
        search_space,
        policy: str = "tpe",
        n_startup_trials: int = 3,
        min_samples_per_combo: int = 3,
        resume_from: str | None = None,
        promote_top: int = 20,
    ):
        self.spec = spec
        self.fidelity = fidelity
        self.tasks = tasks
        self.seed = seed
        self.search_space = search_space
        self.policy_name = policy
        self.n_startup_trials = n_startup_trials
        self.min_samples_per_combo = min_samples_per_combo
        self.promote_top = promote_top

        self._seen: set[str] = set()
        self._wave_count = 0
        self._wave_size = 0
        self._policy: Any = None
        self._init_policy()
        self._init_resume(resume_from)

    def _init_resume(self, resume_from: str | None) -> None:
        if not resume_from:
            return
        try:
            store = RecordStore(StoreConfig(path=Path(resume_from)))
            with store:
                records = store.query_records(
                    gate_verdict=GateVerdict.PASS_, quarantine=False
                )
            valid_records = [r for r in records if r.payload.get("val_acc") is not None]
            if not valid_records:
                logger.info("Warm-start store has no valid records")
                return

            from computronium.domains._task_registry import (
                get_baseline,
                normalize_score,
            )

            def _norm_val(record):
                task_id = record.schedule.task_id
                val_acc = record.payload.get("val_acc", 0.0)
                baseline = get_baseline(task_id)
                return normalize_score(val_acc, task_id, baseline)

            valid_records.sort(key=_norm_val, reverse=True)

            top_n = min(self.promote_top, len(valid_records))
            for record in valid_records[:top_n]:
                self._policy.observe(record)
                self._seen.add(record.measurement_key)

            logger.info(
                "Warm-started policy with %d records from %s (top %d of %d)",
                top_n,
                resume_from,
                top_n,
                len(valid_records),
            )
        except Exception as exc:
            logger.warning("Could not warm-start from %s: %s", resume_from, exc)

    def _init_policy(self) -> None:
        from computronium.experiment.execution.policy import (
            ModelBasedPolicy,
            UniformRandomPolicy,
        )

        if self.policy_name == "random":
            self._policy = UniformRandomPolicy(seed=self.seed)
        else:
            sampler = "tpe" if self.policy_name == "tpe" else "nsga2"
            self._policy = ModelBasedPolicy(
                sampler=sampler,
                seed=self.seed,
                n_startup_trials=self.n_startup_trials,
                spec=self.spec,
                axis_objectives=self.spec.axis_objectives,
                min_samples_per_combo=self.min_samples_per_combo,
            )

    def _get_legal_primitives(self) -> dict[str, list[str]]:
        legal: dict[str, list[str]] = {}
        for axis in StructuralAxis:
            primitives = self.search_space.primitives(axis)
            if primitives:
                legal[axis.value] = list(primitives)
        return legal

    def __iter__(self):
        """Iterator of (Coordinate, Schedule) from the policy.

        The context is deliberately unscoped: a wave must be able to measure
        every task the run declared. Scoping it to ``task_cycle[0]`` made a
        multi-task run measure only its first task, because the policy walks
        the context's space and the planner then stamped a cycled task onto
        whatever came back.
        """
        from computronium.experiment.execution.policy import ProposalContext
        from computronium.experiment.kernel.evaluate import task_shape

        # One context for the whole wave keeps the sampler's diversity.
        ctx = ProposalContext(
            search_space=self.search_space,
            spec=self.spec,
            run_id="learning_survey",
            n_propose=self._wave_size,
            task=None,
            shape=task_shape,
            deadline=None,
        )
        proposals = list(self._policy.propose(ctx))

        proposed = 0
        for prop in proposals:
            if proposed >= self._wave_size:
                break
            coord = prop.coordinate
            if not _check_coord_compatibility(coord):
                continue
            task = prop.schedule.task_id
            schedule = schedule_for(self.spec, task, self.fidelity)
            keys = [coord.measurement_key(rep) for rep in schedule.seed_plan]
            if all(key in self._seen for key in keys):
                continue
            self._seen.update(keys)
            proposed += 1
            yield (coord, schedule)

    def _set_wave_size(self, n: int) -> None:
        """Set the number of cells to yield this wave."""
        self._wave_size = n

    def propose(self, n: int, *, seen: set[str]) -> list[tuple[Coordinate, Schedule]]:
        """Legacy batch interface (deprecated)."""
        self._set_wave_size(n)
        self._seen.update(seen)
        return list(iter(self))

    def observe(self, record: Any) -> None:
        self._policy.observe(record)

    def mark_seen(self, measurement_key: str) -> None:
        self._seen.add(measurement_key)

    def after_wave(self) -> None:
        self._wave_count += 1
        logger.debug("Wave %d completed", self._wave_count)


# ============================================================
# Shared Evaluation Loop
# ============================================================


@dataclass(frozen=True, slots=True)
class _Evaluation:
    results: list
    elapsed_s: float
    startup_s: float
    skipped: int


class _ShutdownSignal:
    """SIGTERM/SIGINT handler: stop the run, then close it like a finished run.

    A run killed mid-wave leaves its store row open and writes no manifest,
    so the report reads a run that never ended. The handler asks the wave
    loop to stop and lets the in-flight cell finish its current step; the
    run is then closed with the status ``interrupted``.
    """

    def __init__(self) -> None:
        self.requested = False
        self._old: dict[int, Any] = {}

    def install(self) -> None:
        """Install the handlers (a no-op off the main thread)."""
        for sig in (signal.SIGTERM, signal.SIGINT):
            try:
                self._old[sig] = signal.signal(sig, self._handle)
            except ValueError, OSError:
                pass

    def uninstall(self) -> None:
        """Restore the handlers this object replaced."""
        for sig, handler in self._old.items():
            try:
                signal.signal(sig, handler)
            except ValueError, OSError:
                pass
        self._old.clear()

    def _handle(self, signum: int, frame: Any) -> None:
        if self.requested:
            return
        self.requested = True
        logger.info(
            "Received %s: stopping the run, then closing it as interrupted",
            signal.Signals(signum).name,
        )


def _evaluate_one(
    cell: tuple[Coordinate, Schedule],
    provenance: Provenance,
    deadline_check: Any,
    log_steps: int = 0,
) -> Any:
    """Evaluate one cell in this process, stopping it if the wave deadline passes."""
    coord, schedule = cell
    params = {
        "deadline_check": deadline_check,
        "deadline_check_every_n_steps": 1,
    }
    if log_steps > 0:
        params["log_every_n_steps"] = log_steps
    try:
        return cell_record(
            coordinate=coord,
            schedule=schedule,
            provenance=provenance,
            params=params,
        )
    except Exception:
        logger.exception(
            "Cell evaluation failed: %s/%s/%s/%s/%s/%s",
            coord.substrate,
            coord.geometry,
            coord.dynamics,
            coord.plasticity,
            coord.credit,
            coord.update,
        )
        raise


def _log_progress(i: int, n_total: int, record: Any) -> None:
    gate = record.status.gate_verdict.value
    task_id = record.schedule.task_id
    primary_key = _primary_metric_key(task_id)
    primary_val = record.payload.get(primary_key, "N/A")
    param_count = record.payload.get("param_count", "N/A")
    if isinstance(param_count, int):
        if param_count >= 1_000_000:
            param_str = f"{param_count / 1_000_000:.2f}M"
        elif param_count >= 1_000:
            param_str = f"{param_count / 1_000:.2f}K"
        else:
            param_str = str(param_count)
    else:
        param_str = str(param_count)
    logger.info(
        "  [%d/%d] %s | %s=%s | params=%s | task=%s | seed=%d | %.0fs | %s/%s/%s/%s/%s/%s",
        i,
        n_total,
        gate,
        primary_key,
        f"{primary_val:.4f}" if isinstance(primary_val, float) else primary_val,
        param_str,
        task_id,
        record.schedule.seed,
        record.payload.get("walltime_s", 0.0),
        record.substrate,
        record.geometry,
        record.dynamics,
        record.plasticity,
        record.credit,
        record.update,
    )


def _expand_replicates(
    cells: list[tuple[Coordinate, Schedule]],
) -> list[tuple[Coordinate, Schedule]]:
    """One evaluable cell per seed.

    A record's identity is its own single-seed schedule, so a ``n_seeds=3``
    cell is three measurements, not one measurement labelled 3. Expanding here
    — the one place every cell passes through — is what lets ``--n-seeds 3``
    satisfy the claim gate's ``n>=3`` instead of writing one record and
    reporting a replication it never ran.
    """
    return [
        (coordinate, replicate)
        for coordinate, schedule in cells
        for replicate in schedule.seed_plan
    ]


def _cell_records(
    cells: list[tuple[Coordinate, Schedule]],
    provenance: Provenance,
    before_deadline: Any,
    max_workers: int,
    log_steps: int,
) -> Iterator[Any]:
    """Each cell's record, in submission order.

    One worker: the cells run one after another and a cell that starts
    after the deadline is skipped.

    Several workers: the wave fans out over threads, so the cells share
    one CUDA context, one dataset cache and one store writer — the
    fan-out cannot reproduce the process pool's stall (a CUDA context
    and a dataset lock per child). The cells share the process RNG, so
    concurrent cells are reproducible only at one worker.
    """
    n_total = len(cells)

    def _announce(i: int, cell: tuple[Coordinate, Schedule]) -> None:
        coord, schedule = cell
        logger.info(
            "  cell %d/%d: %s/%s/%s/%s/%s/%s on %s",
            i,
            n_total,
            coord.substrate,
            coord.geometry,
            coord.dynamics,
            coord.plasticity,
            coord.credit,
            coord.update,
            schedule.task_id,
        )

    def _run(cell: tuple[Coordinate, Schedule]) -> Any:
        if not before_deadline():
            return None
        return _evaluate_one(cell, provenance, before_deadline, log_steps)

    if max_workers <= 1:
        for i, cell in enumerate(cells, 1):
            _announce(i, cell)
            try:
                record = _run(cell)
            except Exception as exc:
                logger.warning("Cell evaluation failed: %s", exc)
                continue
            if record is not None:
                yield record
        return

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = []
        for i, cell in enumerate(cells, 1):
            _announce(i, cell)
            futures.append(pool.submit(_run, cell))
        for future in futures:
            try:
                record = future.result()
            except Exception as exc:
                logger.warning("Cell evaluation failed: %s", exc)
                continue
            if record is not None:
                yield record


def _evaluate_cells(
    cells: list[tuple[Coordinate, Schedule]],
    store_path: str,
    provenance: Provenance,
    budget_seconds: int | None = None,
    max_workers: int = 1,
    log_steps: int = 0,
    shutdown: _ShutdownSignal | None = None,
) -> _Evaluation:
    """Evaluate cells until the budget is spent.

    One worker by default: every cell shares one GPU, one dataset cache
    and one store writer. ``max_workers`` fans the wave out over
    threads — one CUDA context, one dataset cache, one writer — so the
    fan-out cannot reproduce the process pool's stall. The deadline is
    handed to the trainer, so a single long cell stops at the wave
    boundary instead of overrunning the run; a shutdown signal stops it
    the same way.
    """
    cells = _expand_replicates(cells)
    n_total = len(cells)
    results: list = []
    started = time.monotonic()
    deadline = started + budget_seconds if budget_seconds else None
    startup_s = 0.0

    def _before_deadline() -> bool:
        if shutdown is not None and shutdown.requested:
            return False
        return deadline is None or time.monotonic() < deadline

    logger.info(
        "Evaluating %d single-seed cell(s) %s",
        n_total,
        "sequentially" if max_workers <= 1 else f"on {max_workers} worker(s)",
    )

    with RecordStore(StoreConfig(path=Path(store_path))) as store:
        records = _cell_records(
            cells, provenance, _before_deadline, max_workers, log_steps
        )
        for record in records:
            results.append(record)
            store.append(record)

            if not startup_s:
                startup_s = max(
                    0.0,
                    (time.monotonic() - started)
                    - float(record.payload.get("walltime_s", 0.0)),
                )

            _log_progress(len(results), n_total, record)

    elapsed = time.monotonic() - started
    skipped = n_total - len(results)
    if skipped:
        logger.info(
            "Budget spent: %d of %d cells evaluated, %d skipped (%.0fs elapsed)",
            len(results),
            n_total,
            skipped,
            elapsed,
        )
    return _Evaluation(results, elapsed, startup_s, skipped)


def _generate_report(store_path: str, run_id: str) -> dict[str, Any]:
    from computronium.experiment.surface.report import (
        ReportGenerator,
    )
    from computronium.experiment.surface.report import (
        RunSummary as ReportRunSummary,
    )

    store_config = StoreConfig(path=Path(store_path))
    with RecordStore(store_config) as store:
        generator = ReportGenerator(store)
        result: ReportRunSummary | None = generator.run_summary(run_id)
        if result is None:
            return {}
        # Convert ReportRunSummary to dict
        return {
            "run_id": result.run_id,
            "spec": result.spec,
            "spec_version": result.spec_version,
            "status": result.status,
            "budget_consumed_s": result.budget_consumed_s,
            "replay_hash": result.replay_hash,
            "started_at": result.started_at,
            "finished_at": result.finished_at,
            "record_count": result.record_count,
            "claim_eligible_cells": result.claim_eligible_cells,
            "promoted_count": result.promoted_count,
            "declared_cells": result.declared_cells,
        }


def _pretty_print_dry_run(
    result: dict[str, Any],
    *,
    hours: float,
    fidelity: str,
    model: CostModel,
) -> None:
    """Pretty-print dry-run results as a table."""
    cells = result.get("cells", [])
    tasks = result.get("tasks", [])
    n = result.get("n", 0)

    print("\n=== SimpleSurvey Dry-Run ===")
    print(
        f"Budget: {hours}h ({int(hours * 3600)}s) | Fidelity: {fidelity} | "
        f"Tasks: {', '.join(tasks)}"
    )
    print(f"Estimated cells: {n}")
    print()

    if not cells:
        print("No cells generated (search space may be empty or over-constrained)")
        return

    header = (
        f"{'#':>3}  {'Substrate':<15} {'Geometry':<15} {'Dynamics':<20} "
        f"{'Plasticity':<15} {'Credit':<20} {'Update':<15}"
    )
    print(header)
    print("-" * 120)
    for i, (coord, _schedule) in enumerate(cells[:MAX_PREVIEW_CELLS], 1):
        print(
            f"{i:>3}  {coord.substrate:<15} {coord.geometry:<15} {coord.dynamics:<20} "
            f"{coord.plasticity:<15} {coord.credit:<20} {coord.update:<15}"
        )
    if n > MAX_PREVIEW_CELLS:
        print(f"  ... {n - MAX_PREVIEW_CELLS} more cells")

    total_est = model.startup_s + n * model.cost_per_cell_s
    print()
    print(
        f"Cost per cell: ~{model.cost_per_cell_s:.1f}s ({model.source}), "
        f"startup ~{model.startup_s:.0f}s"
    )
    print(f"Total estimated time: ~{total_est:.0f}s ({total_est / 60:.1f}m)")


# ============================================================
# Main Wave Runner
# ============================================================


@dataclass(frozen=True, slots=True)
class RunSummary:
    run_id: str
    store_path: str
    cells_evaluated: int
    cells_passed: int
    cells_failed: int
    cells_skipped: int
    walltime_s: float
    report: dict
    waves_completed: int
    budget_split: dict[str, float]


def _close_run(
    summary: RunSummary, *, fidelity: str, planned_cells: int, status: str = "completed"
) -> None:
    """Close the run row and write the manifest the shell reads after a run.

    A run that returns normally is ``completed`` even when its budget stopped
    the last wave: the budget is the run's declared bound, not a failure. A
    run stopped by a signal is ``interrupted`` — it did not reach its budget,
    and the manifest says so without a DuckDB query.
    """
    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.evidence.store._models import StoreConfig

    with RecordStore(StoreConfig(path=Path(summary.store_path))) as store:
        store.finish_run(summary.run_id, status, budget_consumed_s=summary.walltime_s)
    manifest = {
        "run_id": summary.run_id,
        "status": status,
        "fidelity": fidelity,
        "walltime_s": round(summary.walltime_s, 1),
        "cells_planned": planned_cells,
        "cells_evaluated": summary.cells_evaluated,
        "cells_passed": summary.cells_passed,
        "cells_failed": summary.cells_failed,
        "cells_skipped": summary.cells_skipped,
        "waves_completed": summary.waves_completed,
        "budget_split": summary.budget_split,
    }
    Path(summary.store_path).with_suffix(".run.json").write_text(
        json.dumps(manifest, indent=2)
    )


def _run_ladder_promotion(
    spec: RunSpec,
    planner: Planner,
    all_results: list,
    store_path: str,
    provenance: Provenance,
    budget_remaining: float,
    total_elapsed: float,
    fidelity_walltime: dict[str, float],
    max_workers: int = 1,
    log_steps: int = 0,
    shutdown: _ShutdownSignal | None = None,
) -> tuple[float, list, float]:
    """Run fidelity ladder promotion: L0 -> L1 -> L2.

    Promotes top-performing cells to higher fidelity (more seeds, more epochs).
    Stages are sized from measured per-cell cost and the time actually left
    after L0, not from a fixed split: L1 may reserve at most 60% of the
    remaining budget, and L2 takes whatever is left after L1. A stage that
    cannot afford one cell is skipped and its budget carries forward.
    """
    from computronium.experiment.kernel.search_space import schedule_for

    # Get PASS records with normalized_metric, group by coordinate (cell_key)
    pass_records = [
        r
        for r in all_results
        if r.status.gate_verdict.value == "PASS"
        and r.payload.get("normalized_metric") is not None
    ]
    if not pass_records:
        logger.info("Ladder: no PASS records to promote")
        return total_elapsed, all_results, budget_remaining

    # Group by cell_key, keep best normalized_metric per cell
    from computronium.experiment.schema.record import Record

    best_by_cell: dict[str, tuple[float, Record]] = {}
    for record in pass_records:
        cell_key = record.cell_key
        norm_metric = record.payload.get("normalized_metric", 0.0)
        if cell_key not in best_by_cell or norm_metric > best_by_cell[cell_key][0]:
            best_by_cell[cell_key] = (norm_metric, record)

    # Sort by normalized_metric descending
    sorted_cells = sorted(best_by_cell.items(), key=lambda x: x[1][0], reverse=True)

    # Cost model: a record is one seed, so its measured walltime is the cost of
    # one replicate. Scaling by the target epoch count prices each cell from its
    # own dynamics and task instead of a global average that mixes them.
    COST_SAFETY = 1.25

    def _expected_replicate_cost(record: Any, target_fid: str) -> float:
        """One replicate's cost: this record's measured time scaled by epochs.

        A record is one seed, so its own walltime is the per-replicate rate.
        Keying on the record (not a task median) keeps instantaneous and
        energy-minimization cells from being priced as each other.
        """
        measured = float(record.payload.get("walltime_s") or 0.0)
        if measured <= 0.0:
            measured = 60.0
        target = schedule_for(spec, record.schedule.task_id, target_fid)
        return (
            measured
            * max(1, target.epochs)
            / max(1, record.schedule.epochs)
            * COST_SAFETY
        )

    # L0 already done, promote to L1 then L2
    for target_fid in ["L1", "L2"]:
        # Size each stage from the time actually left. L1 may reserve at most
        # 60% of it so L2 keeps a share; L2 takes everything that remains.
        share = 0.6 if target_fid == "L1" else 1.0
        fid_budget = int(max(0.0, budget_remaining) * share)
        if fid_budget <= 0:
            logger.info("Ladder: no budget left for %s", target_fid)
            break

        expected = [
            (
                cell_key,
                norm_metric,
                record,
                _expected_replicate_cost(record, target_fid),
            )
            for cell_key, (norm_metric, record) in sorted_cells
        ]
        if not expected:
            continue

        # A promoted cell expands into n_seeds replicate cells, run one at a
        # time, so the stage walltime is the sum of every selected replicate.
        target_n_seeds = schedule_for(
            spec, expected[0][2].schedule.task_id, target_fid
        ).n_seeds

        # Candidates are ranked by accuracy, but a cell the stage cannot afford
        # is not a candidate: promoting it measures nothing.
        affordable = [entry for entry in expected if entry[3] <= fid_budget]
        if not affordable:
            logger.info(
                "Ladder: skipping %s — cheapest cell needs ~%.0fs, budget is %.0fs",
                target_fid,
                min(cost for *_, cost in expected),
                fid_budget,
            )
            continue

        n_promote = 0
        planned = 0.0
        for _cell_key, _val_acc, _record, cost in affordable:
            if n_promote >= MAX_PROMOTE_CELLS:
                break
            if planned + cost * target_n_seeds > fid_budget:
                break
            planned += cost * target_n_seeds
            n_promote += 1

        if n_promote == 0:
            logger.info(
                "Ladder: skipping %s — one cell needs ~%.0fs, budget is %.0fs",
                target_fid,
                affordable[0][3],
                fid_budget,
            )
            continue

        promote_candidates = [
            (cell_key, (val_acc, record))
            for cell_key, val_acc, record, _cost in affordable[:n_promote]
        ]
        logger.info(
            "Ladder %s: promoting %d cell(s), plan ~%.0fs, budget %.0fs",
            target_fid,
            n_promote,
            planned,
            fid_budget,
        )

        # Create new schedules for target fidelity, expanding each cell into n_seeds replicates
        cells_to_promote = []
        for cell_key, (val_acc, record) in promote_candidates:
            # Reconstruct Coordinate from Record fields
            from computronium.experiment.schema.coordinate import Coordinate

            coord = Coordinate(
                substrate=record.substrate,
                geometry=record.geometry,
                dynamics=record.dynamics,
                plasticity=record.plasticity,
                credit=record.credit,
                update=record.update,
                params=record.params,
            )
            task_id = record.schedule.task_id
            new_schedule = schedule_for(spec, task_id, target_fid)
            # _evaluate_cells expands the seed plan into one record per seed.
            cells_to_promote.append((coord, new_schedule))

        if not cells_to_promote:
            continue

        logger.info(
            "=== Ladder promotion to %s (%d cells, budget %.0fs) ===",
            target_fid,
            len(cells_to_promote),
            fid_budget,
        )

        # Evaluate promoted cells
        wave_start = time.monotonic()
        evaluation = _evaluate_cells(
            cells=cells_to_promote,
            store_path=store_path,
            provenance=provenance,
            budget_seconds=fid_budget,
            max_workers=max_workers,
            log_steps=log_steps,
            shutdown=shutdown,
        )

        wave_elapsed = time.monotonic() - wave_start
        total_elapsed += wave_elapsed
        budget_remaining -= wave_elapsed
        fidelity_walltime[target_fid] = (
            fidelity_walltime.get(target_fid, 0.0) + wave_elapsed
        )

        all_results.extend(evaluation.results)

        # Feed results to planner for future proposals
        for rec in evaluation.results:
            planner.observe(rec)

        # Update sorted_cells for next fidelity promotion
        new_pass = [
            r
            for r in evaluation.results
            if r.status.gate_verdict.value == "PASS"
            and r.payload.get("normalized_metric") is not None
        ]
        for record in new_pass:
            cell_key = record.cell_key
            norm_metric = record.payload.get("normalized_metric", 0.0)
            if cell_key not in best_by_cell or norm_metric > best_by_cell[cell_key][0]:
                best_by_cell[cell_key] = (norm_metric, record)
        sorted_cells = sorted(best_by_cell.items(), key=lambda x: x[1][0], reverse=True)

        logger.info(
            "Ladder %s: %.1fs/cell, %d results",
            target_fid,
            wave_elapsed / len(evaluation.results) if evaluation.results else 0,
            len(evaluation.results),
        )

    return total_elapsed, all_results, budget_remaining


def _measure_cost_model(
    device_str: str,
    fidelity: str,
    store_path: str,
    records: list,
    prior: CostModel,
) -> CostModel:
    """Record what the finished cells actually cost, per task.

    Only complete cells price the cache: a cell cut short by the run deadline is
    cheap because it stopped, and caching that rate would size the next run for
    work it cannot finish.
    """
    from collections import defaultdict

    task_times: defaultdict[str, list[float]] = defaultdict(list)
    for record in records:
        complete = record.payload.get("epochs_completed", 0) >= record.payload.get(
            "epochs_requested", 0
        )
        task_id = record.payload.get("task_id")
        walltime = record.payload.get("walltime_s")
        if complete and task_id and walltime:
            task_times[task_id].append(float(walltime))

    if not task_times:
        return prior

    per_task = {
        task_id: sum(times) / len(times) for task_id, times in task_times.items()
    }
    measured = CostModel(
        cost_per_cell_s=max(0.01, sum(per_task.values()) / len(per_task)),
        startup_s=0.0,
        measured=True,
        per_task=per_task,
    )
    _save_cost_model(device_str, fidelity, measured)
    logger.info(
        "Measured: %.1fs/cell (prior: %.1fs/cell)",
        measured.cost_per_cell_s,
        prior.cost_per_cell_s,
    )
    return measured


def run_waves(
    spec: RunSpec,
    planner: Planner,
    *,
    budget_seconds: int,
    store_path: str,
    fidelity: str,
    verbose: bool,
    cpu_threads: int,
    device_str: str,
    run_id: str | None = None,
    dry_run: bool = False,
    wave0_cells: list[tuple[Coordinate, Schedule]] | None = None,
    ladder: bool = False,
    max_workers: int = 1,
    log_steps: int = 0,
) -> RunSummary:
    """Execute waves until budget exhausted.

    Args:
        spec: Run specification.
        planner: Planner instance (StaticPlanner or PolicyPlanner).
        budget_seconds: Total time budget.
        store_path: Path to DuckDB store.
        fidelity: Fidelity level (L0/L1/L2).
        verbose: Verbose progress output.
        cpu_threads: Torch threads per worker.
        device_str: Device string (cpu/cuda).
        run_id: Optional run ID (generated if not provided).
        dry_run: If True, only return wave 0 cells without evaluation.
        wave0_cells: Pre-computed wave 0 cells for dry-run.
        max_workers: Cells evaluated concurrently within a wave (1 = serial).
        log_steps: Trainer steps between progress logs (0 = epoch only).

    Returns:
        RunSummary with results.
    """
    shutdown = _ShutdownSignal()
    shutdown.install()
    try:
        return _run_waves(
            spec=spec,
            planner=planner,
            budget_seconds=budget_seconds,
            store_path=store_path,
            fidelity=fidelity,
            verbose=verbose,
            cpu_threads=cpu_threads,
            device_str=device_str,
            run_id=run_id,
            dry_run=dry_run,
            wave0_cells=wave0_cells,
            ladder=ladder,
            max_workers=max_workers,
            log_steps=log_steps,
            shutdown=shutdown,
        )
    finally:
        shutdown.uninstall()


def _run_waves(
    spec: RunSpec,
    planner: Planner,
    *,
    budget_seconds: int,
    store_path: str,
    fidelity: str,
    verbose: bool,
    cpu_threads: int,
    device_str: str,
    run_id: str | None = None,
    dry_run: bool = False,
    wave0_cells: list[tuple[Coordinate, Schedule]] | None = None,
    ladder: bool = False,
    max_workers: int = 1,
    log_steps: int = 0,
    shutdown: _ShutdownSignal | None = None,
) -> RunSummary:
    """Execute waves until budget exhausted (the signal handling lives above)."""
    if run_id is None:
        run_id = str(uuid.uuid4())[:8]

    provenance = _build_provenance(spec, run_id)

    if dry_run and wave0_cells is not None:
        if ladder:
            # Ladder dry-run: show cells for all three fidelities
            ladder_fidelities = ["L0", "L1", "L2"]
            ladder_cells = []
            ladder_budget_split = {"L0": 0.6, "L1": 0.3, "L2": 0.1}
            for fid in ladder_fidelities:
                n_fid = max(1, int(len(wave0_cells) * ladder_budget_split[fid]))
                tasks = spec.scheduled_tasks
                for i, (coord, _) in enumerate(wave0_cells[:n_fid]):
                    schedule = schedule_for(spec, tasks[i % len(tasks)], fid)
                    ladder_cells.append((coord, schedule))
            return RunSummary(
                run_id=run_id,
                store_path=store_path,
                cells_evaluated=0,
                cells_passed=0,
                cells_failed=0,
                cells_skipped=0,
                walltime_s=0.0,
                report={},
                waves_completed=0,
                budget_split=ladder_budget_split,
            )
        return RunSummary(
            run_id=run_id,
            store_path=store_path,
            cells_evaluated=0,
            cells_passed=0,
            cells_failed=0,
            cells_skipped=0,
            walltime_s=0.0,
            report={},
            waves_completed=0,
            budget_split={},
        )

    all_results: list = []
    total_elapsed = 0.0
    wave = 0
    planned_cells = 0

    # Ladder: L0 explores on half the budget; L1/L2 size themselves from the
    # measured cell cost and the time actually left (see _run_ladder_promotion).
    if ladder:
        # Adaptive L0 share: for small search spaces, shrink L0 to leave more
        # budget for L1/L2 promotion. The planner yields min(MAX_WAVE_CELLS, space)
        # cells per wave; if space < 1000, L0 needs < 50% budget.
        total_space = sum(
            len(planner.search_space.primitives(axis)) for axis in StructuralAxis
        )
        # Rough estimate: product of primitives across axes
        # For small spaces, use 30% instead of 50% for L0
        l0_share = 0.3 if total_space < 1000 else 0.5
        budget_remaining = budget_seconds * l0_share
        fidelity_walltime = {"L0": 0.0, "L1": 0.0, "L2": 0.0}
    else:
        budget_remaining = budget_seconds
        fidelity_walltime: dict[str, float] = {}
    evaluation = None

    # Create run in store before any evaluation
    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.evidence.store._models import StoreConfig

    # The sequential evaluator runs in this process, so the flag's whole
    # purpose — bounding CPU threads — applies here and nowhere else.
    if cpu_threads > 0:
        torch.set_num_threads(cpu_threads)

    store_config = StoreConfig(path=Path(store_path))
    with RecordStore(store_config) as init_store:
        init_store.create_run(run_id, spec)

    # Positive control (P3): a known-working cell proves the harness trains.
    # Always L0 and capped, so validating the pipeline can never eat the run.
    positive_control_results: list = []
    positive_control_cell = _make_positive_control_cell(spec)
    if positive_control_cell is not None:
        planned_cells += 1
        logger.info(
            "Positive control (L0): %s/%s/%s/%s/%s/%s on %s",
            positive_control_cell[0].substrate,
            positive_control_cell[0].geometry,
            positive_control_cell[0].dynamics,
            positive_control_cell[0].plasticity,
            positive_control_cell[0].credit,
            positive_control_cell[0].update,
            positive_control_cell[1].task_id,
        )
        pc_start = time.monotonic()
        pc_eval = _evaluate_cells(
            cells=[positive_control_cell],
            store_path=store_path,
            provenance=provenance,
            budget_seconds=int(min(60, budget_remaining)),
            max_workers=max_workers,
            log_steps=log_steps,
            shutdown=shutdown,
        )
        pc_elapsed = time.monotonic() - pc_start
        positive_control_results.extend(pc_eval.results)
        all_results.extend(pc_eval.results)
        budget_remaining -= pc_elapsed
        total_elapsed += pc_elapsed
        fidelity_walltime["L0"] = fidelity_walltime.get("L0", 0.0) + pc_elapsed
        for record in pc_eval.results:
            planner.observe(record)
            planner.mark_seen(record.measurement_key)
        gate = (
            positive_control_results[0].status.gate_verdict.value
            if positive_control_results
            else "N/A"
        )
        pc_task_id = positive_control_cell[1].task_id
        primary_key = _primary_metric_key(pc_task_id)
        primary_val = (
            positive_control_results[0].payload.get(primary_key, "N/A")
            if positive_control_results
            else "N/A"
        )
        logger.info(
            "Positive control: gate=%s, %s=%s",
            gate,
            primary_key,
            f"{primary_val:.4f}" if isinstance(primary_val, float) else primary_val,
        )

    while budget_remaining > 0:
        if shutdown is not None and shutdown.requested:
            logger.info("Shutdown requested: no further waves")
            break
        wave += 1
        logger.info("=== Wave %d (budget remaining: %.0fs) ===", wave, budget_remaining)

        # Size the wave from cells measured at *this* fidelity. A positive
        # control record is L0; pricing an L2 wave from it overstates how many
        # cells fit by the fidelity ratio, and every over-proposed cell is an
        # Optuna ask that dies at the deadline.
        fidelity_costs = [
            float(r.payload.get("walltime_s") or 0.0)
            for r in all_results
            if r.payload.get("fidelity") == fidelity
            and float(r.payload.get("walltime_s") or 0.0) > 0.0
        ]
        cost_per_cell = (
            sum(fidelity_costs) / len(fidelity_costs)
            if fidelity_costs
            else DEFAULT_COSTS.get(fidelity, 30.0)
        )
        # A proposed cell costs one replicate per seed; records price a single
        # seed. Divide by the fidelity's seed plan or the wave asks for
        # n_seeds times the work the budget can pay for.
        replicates = schedule_for(spec, spec.task_names[0], fidelity).n_seeds
        cell_cost = cost_per_cell * max(1, replicates)
        n_wave = max(
            1, min(MAX_WAVE_CELLS, int(budget_remaining / max(1.0, cell_cost)))
        )

        planner._set_wave_size(n_wave)
        logger.info(
            "Proposing up to %d cell(s) at ~%.0fs/cell (%s, %d seed(s))",
            n_wave,
            cell_cost,
            "measured" if fidelity_costs else "default",
            replicates,
        )
        cells = list(iter(planner))
        planned_cells += len(cells)
        if not cells:
            logger.info("No more cells to evaluate")
            break
        logger.info("Wave %d: %d cell(s) proposed", wave, len(cells))

        wave_start = time.monotonic()
        evaluation = _evaluate_cells(
            cells=cells,
            store_path=store_path,
            provenance=provenance,
            budget_seconds=int(budget_remaining),
            max_workers=max_workers,
            log_steps=log_steps,
        )

        wave_elapsed = time.monotonic() - wave_start
        total_elapsed += wave_elapsed
        budget_remaining -= wave_elapsed
        fidelity_walltime[fidelity] = (
            fidelity_walltime.get(fidelity, 0.0) + wave_elapsed
        )

        all_results.extend(evaluation.results)

        # Feed results to planner
        for record in evaluation.results:
            planner.observe(record)

        planner.after_wave()

        # Log cost model update
        if evaluation.results:
            from collections import defaultdict

            task_times: defaultdict[str, list[float]] = defaultdict(list)
            for r in evaluation.results:
                task_id = r.payload.get("task_id")
                walltime = r.payload.get("walltime_s")
                if task_id and walltime:
                    task_times[task_id].append(float(walltime))

            per_task = {}
            for task_id, times in task_times.items():
                if times:
                    per_task[task_id] = sum(times) / len(times)

            logger.info(
                "Wave %d measured: %.1fs/cell, %.0fs startup, %d results",
                wave,
                wave_elapsed / len(evaluation.results),
                evaluation.startup_s,
                len(evaluation.results),
            )

        if evaluation.skipped > 0:
            logger.info("Budget exhausted mid-wave")
            break

    # Fidelity ladder promotion: L0 -> L1 -> L2. Runs after the exploration
    # loop so L1/L2 are sized from the time actually left.
    if (
        ladder
        and budget_remaining > 0
        and not (shutdown is not None and shutdown.requested)
    ):
        total_elapsed, all_results, budget_remaining = _run_ladder_promotion(
            spec=spec,
            planner=planner,
            all_results=all_results,
            store_path=store_path,
            provenance=provenance,
            budget_remaining=max(0.0, budget_seconds - total_elapsed),
            total_elapsed=total_elapsed,
            fidelity_walltime=fidelity_walltime,
            max_workers=max_workers,
            log_steps=log_steps,
            shutdown=shutdown,
        )

    passed = sum(1 for r in all_results if r.status.gate_verdict.value == "PASS")
    failed = len(all_results) - passed

    total_walltime = sum(fidelity_walltime.values())
    budget_split = {}
    for fid, wt in fidelity_walltime.items():
        budget_split[fid] = wt / total_walltime if total_walltime > 0 else 0.0

    logger.info(
        "Done: %d evaluated, %d passed, %d failed, %.1fs elapsed, %d waves",
        len(all_results),
        passed,
        failed,
        total_elapsed,
        wave,
    )

    summary = RunSummary(
        run_id=run_id,
        store_path=store_path,
        cells_evaluated=len(all_results),
        cells_passed=passed,
        cells_failed=failed,
        cells_skipped=evaluation.skipped if evaluation and evaluation.results else 0,
        walltime_s=total_elapsed,
        report={},
        waves_completed=wave,
        budget_split=budget_split,
    )
    # Close the run before reading it back, so the report describes a finished
    # run (status, budget consumed) instead of the running row it just left.
    interrupted = shutdown is not None and shutdown.requested
    _close_run(
        summary,
        fidelity=fidelity,
        planned_cells=planned_cells,
        status="interrupted" if interrupted else "completed",
    )
    return replace(summary, report=_generate_report(store_path, run_id))


# ============================================================
# Spec Builder & Helpers
# ============================================================


@dataclass(frozen=True, slots=True)
class _SpecParams:
    hours: float
    fidelity: Fidelity
    tasks: Sequence[str] | None
    seed: int
    device: str
    param_budget: int
    n_seeds: int | None
    epochs: int | None
    batch_limit: int
    axes: dict[str, tuple[str, ...]] | None
    hyperparameters: dict[str, Any] | None
    objectives: tuple[str, ...]
    axis_objectives: dict[str, tuple[str, ...]] | None = None


def _build_spec(params: _SpecParams) -> RunSpec:
    from computronium.experiment.schema.axis import StructuralAxis
    from computronium.experiment.schema.run_spec import AxisSelection
    from computronium.experiment.schema.seed_registries import seed_all_registries

    seed_all_registries()

    axis_selections = []
    if params.axes:
        for axis_name, primitives in params.axes.items():
            axis_enum = getattr(StructuralAxis, axis_name.upper())
            axis_selections.append(AxisSelection(axis=axis_enum, primitives=primitives))

    # ``None`` means "follow the fidelity ladder"; an explicit value (including
    # 1) is the caller's declaration and must survive into the schedule.
    n_seeds = params.n_seeds
    epochs = params.epochs

    spec = RunSpec(
        profile="survey",
        task=params.tasks[0] if params.tasks else "auto",
        tasks=tuple(params.tasks) if params.tasks else (),
        task_cycle=list(params.tasks) if params.tasks else [],
        objectives=params.objectives or ("validation_accuracy", "energy_per_step"),
        fidelity=params.fidelity,
        n_seeds=n_seeds,
        epochs=epochs,
        batch_limit=params.batch_limit,
        seed=params.seed,
        budget_seconds=int(params.hours * 3600),
        param_budget=params.param_budget,
        device=params.device,
        axes=tuple(axis_selections),
        hyperparameters=params.hyperparameters or {},
        axis_objectives=params.axis_objectives or {},
    )
    return spec


def _default_store_path() -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    exp_dir = Path("experiments")
    exp_dir.mkdir(parents=True, exist_ok=True)
    return str(exp_dir / f"experiment_{timestamp}.duckdb")


def _format_error(message: str, hint: str | None = None) -> str:
    lines = [f"Error: {message}"]
    if hint:
        lines.append(f"Hint: {hint}")
    return "\n".join(lines)


def _axis_overrides(
    axes_json: str, *, digital: bool
) -> dict[str, tuple[str, ...]] | None:
    axes: dict[str, tuple[str, ...]] | None = (
        json.loads(axes_json) if axes_json else None
    )
    if not digital:
        return axes
    pinned = dict(axes or {})
    pinned["substrate"] = ("digital",)
    return pinned


# ============================================================
# Self-Test Infrastructure
# ============================================================


@dataclass(frozen=True, slots=True)
class _SelfTestConfig:
    min_python: tuple[int, int] = (3, 14)
    dry_run_hours: float = 0.001
    dry_run_fidelity: str = "L0"
    dry_run_device: str = "cpu"

    def with_device(self, device: str) -> _SelfTestConfig:
        return _SelfTestConfig(
            min_python=self.min_python,
            dry_run_hours=self.dry_run_hours,
            dry_run_fidelity=self.dry_run_fidelity,
            dry_run_device=device,
        )


def _check_python_version(config: _SelfTestConfig) -> bool:
    py_version = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    logger.info("Python: %s", py_version)
    if sys.version_info < config.min_python:
        logger.error("Python %s+ required, got %s", config.min_python, py_version)
        return False
    return True


def _check_uv_available() -> bool:
    import shutil
    import subprocess

    uv_path = shutil.which("uv")
    if uv_path is None:
        logger.error("uv not found in PATH")
        return False
    try:
        result = subprocess.run(
            [uv_path, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except Exception:
        logger.exception("uv check failed")
        return False
    else:
        if result.returncode != 0:
            logger.error("uv not found")
            return False
        logger.info("uv: %s", result.stdout.strip())
        return True


def _check_stdlib_modules() -> bool:
    for mod in [
        "json",
        "uuid",
        "pathlib",
        "dataclasses",
        "concurrent.futures",
        "random",
    ]:
        try:
            __import__(mod)
        except ImportError:
            logger.exception("stdlib %s missing", mod)
            return False
    logger.info("stdlib OK")
    return True


def _check_torch(device: str = "auto") -> bool:
    try:
        import torch
    except ImportError:
        logger.exception("torch import failed")
        logger.exception("Fix: uv sync --dev --all-extras")
        return False
    except Exception:
        logger.exception("torch import crashed")
        logger.exception("This may indicate a CUDA driver/library mismatch")
        logger.exception("Try: export CUDA_VISIBLE_DEVICES='' to force CPU mode")
        return False
    else:
        logger.info("Torch: %s", torch.__version__)
        cuda_available = False
        if device != "cpu":
            try:
                cuda_available = torch.cuda.is_available()
            except Exception as e:
                logger.warning("CUDA check failed: %s", e)
                logger.warning("Forcing CPU mode")

        logger.info("CUDA available: %s", cuda_available)
        if cuda_available:
            try:
                logger.info("GPU: %s", torch.cuda.get_device_name(0))
                logger.info(
                    "GPU memory: %.1f GB",
                    torch.cuda.get_device_properties(0).total_memory / 1e9,
                )
            except Exception as e:
                logger.warning("GPU query failed: %s", e)
        elif device == "cpu":
            logger.info("CUDA: skipped (cpu mode)")
        else:
            logger.info("CUDA: not available, using CPU")

        _test_tensor_ops()
        return True


def _test_tensor_ops() -> None:

    x = torch.tensor([1.0, 2.0])
    y = x * 2
    if y.tolist() != [2.0, 4.0]:
        msg = "tensor ops produced unexpected result"
        raise AssertionError(msg)
    logger.info("Tensor ops: OK")


def _check_computronium_modules() -> bool:
    required = [
        "computronium.core.logging",
        "computronium.domains._task_registry",
        "computronium.experiment.evidence.store",
        "computronium.experiment.evidence.store._models",
        "computronium.experiment.execution.pipeline._budget_constants",
        "computronium.experiment.kernel.evaluate",
        "computronium.experiment.kernel.search_space",
        "computronium.experiment.schema.axis",
        "computronium.experiment.schema.coordinate",
        "computronium.experiment.schema.run_spec",
        "computronium.ontology.system",
    ]
    failed = []
    for mod in required:
        try:
            __import__(mod)
        except Exception:
            logger.exception("%s import failed", mod)
            failed.append(mod)

    if failed:
        logger.error("Failed imports (%d): %s", len(failed), ", ".join(failed))
        logger.error("Fix: uv sync --dev --all-extras")
        return False

    logger.info("All %d modules OK", len(required))
    return True


def _run_self_test(device: str = "cpu") -> bool:
    logger.info("Checking environment...")
    config = _SelfTestConfig().with_device(device)

    checks = [
        ("Python version", lambda: _check_python_version(config)),
        ("uv available", _check_uv_available),
        ("stdlib modules", _check_stdlib_modules),
        ("torch", lambda: _check_torch(device)),
        ("computronium modules", _check_computronium_modules),
    ]

    for idx, (name, check) in enumerate(checks, 1):
        logger.info("Test %d/%d: %s...", idx, len(checks), name)
        if not check():
            logger.error("FAIL: %s", name)
            return False

    logger.info("ALL TESTS PASSED")
    return True
