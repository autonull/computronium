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
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from collections.abc import Sequence

import torch

from computronium.core.logging import get_logger
from computronium.experiment.evidence.store import RecordStore
from computronium.experiment.evidence.store._models import StoreConfig
from computronium.experiment.kernel.evaluate import cell_record, task_shape
from computronium.experiment.kernel.search_space import (
    iter_candidates,
    schedule_for,
)
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
    """Per-cell timing used to size a run against its budget."""

    cost_per_cell_s: float
    startup_s: float
    measured: bool = False
    workers: int = 1
    per_task: dict[str, float] | None = None

    @property
    def source(self) -> str:
        return "measured" if self.measured else "default"


def _load_cost_model(device: str, fidelity: str, workers: int) -> CostModel:
    try:
        entry = json.loads(TIMING_CACHE.read_text())[f"{device}/{fidelity}/{workers}"]
        return CostModel(
            cost_per_cell_s=float(entry["cost_per_cell_s"]),
            startup_s=float(entry["startup_s"]),
            measured=True,
            workers=workers,
            per_task=entry.get("per_task"),
        )
    except OSError, ValueError, KeyError, TypeError:
        return CostModel(
            DEFAULT_COSTS.get(fidelity, 30.0), DEFAULT_STARTUP_S, workers=workers
        )


def _save_cost_model(device: str, fidelity: str, model: CostModel) -> None:
    with contextlib.suppress(OSError, ValueError):
        TIMING_CACHE.parent.mkdir(parents=True, exist_ok=True)
        existing = json.loads(TIMING_CACHE.read_text()) if TIMING_CACHE.exists() else {}
        key = f"{device}/{fidelity}/{model.workers}"
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
        workers=measured.workers,
        per_task=per_task,
    )


def _estimate_cell_count(budget_seconds: int, model: CostModel, workers: int) -> int:
    """Cells that fit ``budget_seconds`` at ``workers``-way parallelism.

    The budget pays startup once and serialized cell time thereafter, so the
    cell count scales with the worker count: dividing by the serial cost alone
    sized CPU runs for one worker while the pool ran four.
    """
    usable = budget_seconds - model.startup_s
    return max(1, int(usable * max(1, workers) // model.cost_per_cell_s))


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
    fidelity: str,
) -> tuple[Coordinate, Schedule] | None:
    """Create a known-working cell for positive control (P3).

    Uses digital/feedforward/instantaneous/null/gradient/euclidean on digits task,
    which is a canonical configuration known to train successfully.
    """
    from computronium.experiment.kernel.search_space import schedule_for
    from computronium.experiment.schema.coordinate import Coordinate

    # Known good coordinate: digital substrate, feedforward geometry, instantaneous dynamics,
    # null plasticity, gradient credit (Backprop), euclidean update
    coord = Coordinate(
        substrate="digital",
        geometry="feedforward",
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
    schedule = schedule_for(spec, task, fidelity)

    return (coord, schedule)


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
    Use `iter(planner)` to get a fresh iterator for each wave.
    """

    def __iter__(self):
        """Return an iterator of (Coordinate, Schedule) for the next wave."""
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
            valid_records = [r for r in records if r.payload.get("val_acc") is not None]
            if not valid_records:
                logger.warning(
                    "Promotion requested but no PASS records with val_acc found"
                )
                return []

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
        self._task_cycle = list(spec.scheduled_tasks)
        self._task_index = 0
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
        """Iterator of (Coordinate, Schedule) from the policy."""
        from computronium.experiment.execution.policy import ProposalContext
        from computronium.experiment.kernel.evaluate import task_shape

        base_task = self._task_cycle[0]

        # One context for the whole wave keeps the sampler's diversity.
        ctx = ProposalContext(
            search_space=self.search_space,
            spec=self.spec,
            run_id="learning_survey",
            n_propose=self._wave_size,
            task=base_task,
            shape=task_shape,
            deadline=None,
        )
        proposals = list(self._policy.propose(ctx))

        for prop in proposals:
            if len(self._seen) >= self._wave_size:
                break
            coord = prop.coordinate
            if not _check_coord_compatibility(coord):
                continue
            task = self._task_cycle[self._task_index % len(self._task_cycle)]
            self._task_index += 1
            schedule = schedule_for(self.spec, task, self.fidelity)
            measurement_key = coord.measurement_key(schedule)
            if measurement_key in self._seen:
                continue
            self._seen.add(measurement_key)
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


def _init_worker(cpu_threads: int, device: str) -> None:
    if device == "cpu":
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
    if cpu_threads > 0:
        import torch

        torch.set_num_threads(cpu_threads)


def _evaluate_one(
    cell: tuple[Coordinate, Schedule],
    fidelity: str,
    store_path: str,
    provenance: Provenance,
) -> Any:
    coord, schedule = cell
    try:
        return cell_record(coordinate=coord, schedule=schedule, provenance=provenance)
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
    val_acc = record.payload.get("val_acc", "N/A")
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
        "  [%d/%d] %s | val_acc=%s | params=%s | task=%s | %s/%s/%s/%s/%s/%s",
        i,
        n_total,
        gate,
        f"{val_acc:.4f}" if isinstance(val_acc, float) else val_acc,
        param_str,
        record.schedule.task_id,
        record.substrate,
        record.geometry,
        record.dynamics,
        record.plasticity,
        record.credit,
        record.update,
    )


def _evaluate_cells_parallel(
    cells: list[tuple[Coordinate, Schedule]],
    fidelity: str,
    store_path: str,
    provenance: Provenance,
    max_workers: int,
    verbose: bool,
    budget_seconds: int | None = None,
    cpu_threads: int = 1,
    device_str: str = "cpu",
    run_id: str | None = None,
    spec: RunSpec | None = None,
    cell_timeout_seconds: float | None = None,
) -> _Evaluation:
    n_total = len(cells)
    results: list = []
    started = time.monotonic()
    deadline = started + budget_seconds if budget_seconds else None
    queue = iter(cells)
    pending: dict[Any, tuple[Coordinate, Schedule]] = {}
    startup_s = 0.0

    store_config = StoreConfig(path=Path(store_path))

    # Use context manager for store to ensure proper initialization and cleanup
    # Run is already created in run_waves before calling this function
    with RecordStore(store_config) as store:

        def _sigterm_handler(signum, frame):
            logger.info("SIGTERM received, closing store after current record...")
            # The context manager will handle cleanup on exit
            sys.exit(130)

        old_sigterm = signal.signal(signal.SIGTERM, _sigterm_handler)
        old_sigint = signal.signal(signal.SIGINT, _sigterm_handler)

        logger.info(
            "Evaluating up to %d cells with %d workers...", n_total, max_workers
        )

        # Force 'spawn' start method to avoid forkserver issues with PyTorch (scipy sets forkserver)
        import multiprocessing as mp

        try:
            mp.set_start_method("spawn", force=True)
        except RuntimeError:
            pass  # Already set

        try:
            with ProcessPoolExecutor(
                max_workers=max_workers,
                initializer=_init_worker,
                initargs=(cpu_threads, device_str),
                mp_context=mp.get_context("spawn"),
            ) as pool:

                def _submit_next() -> None:
                    cell = next(queue, None)
                    if cell is not None:
                        pending[
                            pool.submit(
                                _evaluate_one, cell, fidelity, store_path, provenance
                            )
                        ] = cell

                for _ in range(min(max_workers, n_total)):
                    _submit_next()

                while pending:
                    now = time.monotonic()
                    if deadline is not None and now >= deadline:
                        logger.warning(
                            "Budget deadline reached (%.0fs), killing %d in-flight cells",
                            budget_seconds,
                            len(pending),
                        )
                        for fut in pending:
                            fut.cancel()
                        pool.kill_workers()
                        pending.clear()
                        break

                    # Use timeout to periodically check deadline even if no futures complete
                    wait_timeout = 10.0
                    if deadline is not None:
                        wait_timeout = min(wait_timeout, max(0.1, deadline - now))
                    done_futures = wait(
                        pending, return_when=FIRST_COMPLETED, timeout=wait_timeout
                    ).done
                    for future in done_futures:
                        del pending[future]
                        try:
                            record = future.result(timeout=cell_timeout_seconds)
                        except TimeoutError:
                            logger.warning(
                                "Cell evaluation timed out after %.1fs",
                                cell_timeout_seconds,
                            )
                            continue
                        except Exception as exc:
                            logger.warning("Cell evaluation raised: %s", exc)
                            continue
                        results.append(record)

                        store.append(record)

                        if not startup_s:
                            startup_s = max(
                                0.0,
                                (time.monotonic() - started)
                                - float(record.payload.get("walltime_s", 0.0)),
                            )

                        i = len(results)
                        _log_progress(i, n_total, record)

                        if deadline is None or time.monotonic() < deadline:
                            _submit_next()

        finally:
            signal.signal(signal.SIGTERM, old_sigterm)
            signal.signal(signal.SIGINT, old_sigint)

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
    workers: int,
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
    print(f"Estimated cells: {n} across {workers} workers")
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

    total_est = model.startup_s + n * model.cost_per_cell_s / max(1, workers)
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


def _run_ladder_promotion(
    spec: RunSpec,
    planner: Planner,
    all_results: list,
    store_path: str,
    provenance: Provenance,
    workers: int,
    cpu_threads: int,
    device_str: str,
    run_id: str,
    budget_remaining: float,
    total_elapsed: float,
    fidelity_walltime: dict[str, float],
    verbose: bool,
) -> tuple[float, list, float]:
    """Run fidelity ladder promotion: L0 -> L1 -> L2.

    Promotes top-performing cells to higher fidelity (more seeds, more epochs).
    Stages are sized from measured per-cell cost and the time actually left
    after L0, not from a fixed split: L1 may reserve at most 60% of the
    remaining budget, and L2 takes whatever is left after L1. A stage that
    cannot afford one cell is skipped and its budget carries forward.
    """
    from computronium.experiment.kernel.search_space import schedule_for

    # Get PASS records with val_acc, group by coordinate (cell_key)
    pass_records = [
        r
        for r in all_results
        if r.status.gate_verdict.value == "PASS"
        and r.payload.get("val_acc") is not None
    ]
    if not pass_records:
        logger.info("Ladder: no PASS records to promote")
        return total_elapsed, all_results, budget_remaining

    # Group by cell_key, keep best val_acc per cell
    from computronium.experiment.schema.record import Record

    best_by_cell: dict[str, tuple[float, Record]] = {}
    for record in pass_records:
        cell_key = record.cell_key
        val_acc = record.payload.get("val_acc", 0.0)
        if cell_key not in best_by_cell or val_acc > best_by_cell[cell_key][0]:
            best_by_cell[cell_key] = (val_acc, record)

    # Sort by val_acc descending
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
            (cell_key, val_acc, record, _expected_replicate_cost(record, target_fid))
            for cell_key, (val_acc, record) in sorted_cells
        ]
        if not expected:
            continue

        # A promoted cell expands into n_seeds replicate cells that run in
        # parallel. The stage walltime is ceil(replicates / workers) rounds of
        # the slowest selected replicate.
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
        slowest = 0.0
        for _cell_key, _val_acc, _record, cost in affordable:
            if n_promote >= MAX_PROMOTE_CELLS:
                break
            tentative = max(slowest, cost)
            replicates = (n_promote + 1) * target_n_seeds
            if (-(-replicates // workers)) * tentative > fid_budget:
                break
            slowest = tentative
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
            "Ladder %s: promoting %d cell(s), ~%.0fs per replicate, budget %.0fs",
            target_fid,
            n_promote,
            slowest,
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
            # Expand into n_seeds replicates with different seeds
            base_seed = new_schedule.seed
            n_replicates = new_schedule.n_seeds
            for rep_idx in range(n_replicates):
                rep_schedule = Schedule(
                    fidelity=new_schedule.fidelity,
                    seed=base_seed + rep_idx,
                    n_seeds=new_schedule.n_seeds,
                    epochs=new_schedule.epochs,
                    batch_limit=new_schedule.batch_limit,
                    budget_id=f"{new_schedule.budget_id}_rep{rep_idx}",
                    task_id=new_schedule.task_id,
                    param_budget=new_schedule.param_budget,
                    device=new_schedule.device,
                    deterministic=new_schedule.deterministic,
                    num_workers=new_schedule.num_workers,
                    precision=new_schedule.precision,
                    checkpoint_every_n=new_schedule.checkpoint_every_n,
                    early_stopping_patience=new_schedule.early_stopping_patience,
                )
                cells_to_promote.append((coord, rep_schedule))

        if not cells_to_promote:
            continue

        logger.info(
            "=== Ladder promotion to %s (%d cells, budget %.0fs) ===",
            target_fid,
            len(cells_to_promote),
            fid_budget,
        )

        # Per-cell timeout based on fidelity (L1: 5min, L2: 10min)
        fidelity_timeout = {"L1": 300.0, "L2": 600.0}.get(target_fid, 300.0)

        # Evaluate promoted cells
        wave_start = time.monotonic()
        evaluation = _evaluate_cells_parallel(
            cells=cells_to_promote,
            fidelity=target_fid,
            store_path=store_path,
            provenance=provenance,
            max_workers=workers,
            verbose=verbose,
            budget_seconds=fid_budget,
            cpu_threads=cpu_threads,
            device_str=device_str,
            run_id=run_id,
            spec=spec,
            cell_timeout_seconds=fidelity_timeout,
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
            and r.payload.get("val_acc") is not None
        ]
        for record in new_pass:
            cell_key = record.cell_key
            val_acc = record.payload.get("val_acc", 0.0)
            if cell_key not in best_by_cell or val_acc > best_by_cell[cell_key][0]:
                best_by_cell[cell_key] = (val_acc, record)
        sorted_cells = sorted(best_by_cell.items(), key=lambda x: x[1][0], reverse=True)

        logger.info(
            "Ladder %s: %.1fs/cell, %d results",
            target_fid,
            wave_elapsed * workers / len(evaluation.results)
            if evaluation.results
            else 0,
            len(evaluation.results),
        )

    return total_elapsed, all_results, budget_remaining


def run_waves(
    spec: RunSpec,
    planner: Planner,
    *,
    budget_seconds: int,
    workers: int,
    store_path: str,
    fidelity: str,
    verbose: bool,
    cpu_threads: int,
    device_str: str,
    run_id: str | None = None,
    dry_run: bool = False,
    wave0_cells: list[tuple[Coordinate, Schedule]] | None = None,
    ladder: bool = False,
) -> RunSummary:
    """Execute waves until budget exhausted.

    Args:
        spec: Run specification.
        planner: Planner instance (StaticPlanner or PolicyPlanner).
        budget_seconds: Total time budget.
        workers: Number of parallel workers.
        store_path: Path to DuckDB store.
        fidelity: Fidelity level (L0/L1/L2).
        verbose: Verbose progress output.
        cpu_threads: Torch threads per worker.
        device_str: Device string (cpu/cuda).
        run_id: Optional run ID (generated if not provided).
        dry_run: If True, only return wave 0 cells without evaluation.
        wave0_cells: Pre-computed wave 0 cells for dry-run.

    Returns:
        RunSummary with results.
    """
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

    # Ladder: L0 explores on half the budget; L1/L2 size themselves from the
    # measured cell cost and the time actually left (see _run_ladder_promotion).
    if ladder:
        budget_remaining = budget_seconds * 0.5
        fidelity_walltime = {"L0": 0.0, "L1": 0.0, "L2": 0.0}
    else:
        budget_remaining = budget_seconds
        fidelity_walltime: dict[str, float] = {}
    evaluation = None

    # Create run in store before any evaluation
    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.evidence.store._models import StoreConfig

    store_config = StoreConfig(path=Path(store_path))
    with RecordStore(store_config) as init_store:
        init_store.create_run(run_id, spec)

    # Positive control (P3): gate the report with a known-working cell
    positive_control_results: list = []
    positive_control_cell = _make_positive_control_cell(spec, fidelity)
    if positive_control_cell is not None:
        logger.info(
            "Running positive control: %s/%s/%s/%s/%s/%s on %s",
            positive_control_cell[0].substrate,
            positive_control_cell[0].geometry,
            positive_control_cell[0].dynamics,
            positive_control_cell[0].plasticity,
            positive_control_cell[0].credit,
            positive_control_cell[0].update,
            positive_control_cell[1].task_id,
        )
        pc_start = time.monotonic()
        pc_eval = _evaluate_cells_parallel(
            cells=[positive_control_cell],
            fidelity=fidelity,
            store_path=store_path,
            provenance=provenance,
            max_workers=1,
            verbose=verbose,
            budget_seconds=int(min(300, budget_remaining)),
            cpu_threads=cpu_threads,
            device_str=device_str,
            run_id=run_id,
            spec=spec,
            cell_timeout_seconds=300.0,
        )
        pc_elapsed = time.monotonic() - pc_start
        positive_control_results.extend(pc_eval.results)
        all_results.extend(pc_eval.results)
        budget_remaining -= pc_elapsed
        total_elapsed += pc_elapsed
        fidelity_walltime[fidelity] = fidelity_walltime.get(fidelity, 0.0) + pc_elapsed
        for record in pc_eval.results:
            planner.observe(record)
        gate = (
            positive_control_results[0].status.gate_verdict.value
            if positive_control_results
            else "N/A"
        )
        val_acc = (
            positive_control_results[0].payload.get("val_acc", "N/A")
            if positive_control_results
            else "N/A"
        )
        logger.info(
            "Positive control: gate=%s, val_acc=%s",
            gate,
            f"{val_acc:.4f}" if isinstance(val_acc, float) else val_acc,
        )

    while budget_remaining > 0:
        wave += 1
        logger.info("=== Wave %d (budget remaining: %.0fs) ===", wave, budget_remaining)

        # Size wave based on measured throughput
        if all_results:
            measured_cost = total_elapsed * workers / len(all_results)
            n_wave = max(
                1,
                min(
                    MAX_WAVE_CELLS,
                    int(budget_remaining * workers / max(1.0, measured_cost)),
                ),
            )
        else:
            n_wave = min(MAX_WAVE_CELLS, workers * 2)

        # Propose cells
        planner._set_wave_size(n_wave)
        cells = list(iter(planner))
        if not cells:
            logger.info("No more cells to evaluate")
            break

        # Per-cell timeout based on fidelity (L0: 3min, L1: 5min, L2: 10min)
        fidelity_timeout = {"L0": 180.0, "L1": 300.0, "L2": 600.0}.get(fidelity, 180.0)

        # Evaluate wave
        wave_start = time.monotonic()
        evaluation = _evaluate_cells_parallel(
            cells=cells,
            fidelity=fidelity,
            store_path=store_path,
            provenance=provenance,
            max_workers=workers,
            verbose=verbose,
            budget_seconds=int(budget_remaining),
            cpu_threads=cpu_threads,
            device_str=device_str,
            run_id=run_id,
            spec=spec,
            cell_timeout_seconds=fidelity_timeout,
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
                wave_elapsed * workers / len(evaluation.results),
                evaluation.startup_s,
                len(evaluation.results),
            )

        if evaluation.skipped > 0:
            logger.info("Budget exhausted mid-wave")
            break

    report = _generate_report(store_path, run_id)

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

    # Fidelity ladder promotion: L0 -> L1 -> L2
    if ladder and budget_remaining > 0:
        total_elapsed, all_results, budget_remaining = _run_ladder_promotion(
            spec=spec,
            planner=planner,
            all_results=all_results,
            store_path=store_path,
            provenance=provenance,
            workers=workers,
            cpu_threads=cpu_threads,
            device_str=device_str,
            run_id=run_id,
            # Everything the L0 loop did not spend is available to L1/L2.
            budget_remaining=max(0.0, budget_seconds - total_elapsed),
            total_elapsed=total_elapsed,
            fidelity_walltime=fidelity_walltime,
            verbose=verbose,
        )

    report = _generate_report(store_path, run_id)

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

    return RunSummary(
        run_id=run_id,
        store_path=store_path,
        cells_evaluated=len(all_results),
        cells_passed=passed,
        cells_failed=failed,
        cells_skipped=evaluation.skipped if evaluation and evaluation.results else 0,
        walltime_s=total_elapsed,
        report=report,
        waves_completed=wave,
        budget_split=budget_split,
    )


# ============================================================
# Spec Builder & Helpers
# ============================================================


@dataclass(frozen=True, slots=True)
class _SpecParams:
    hours: float
    fidelity: str
    tasks: Sequence[str] | None
    seed: int
    device: str
    param_budget: int
    n_seeds: int
    epochs: int
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

    n_seeds = params.n_seeds if params.n_seeds != 1 else None
    epochs = params.epochs if params.epochs != 1 else None

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


def _resolve_max_workers(max_workers: int | str, device: torch.device) -> int:
    import os

    import psutil

    if max_workers == "auto" or (isinstance(max_workers, int) and max_workers <= 0):
        if device.type == "cuda":
            return torch.cuda.device_count() or 1
        cores = os.cpu_count() or 4
        try:
            available_gb = psutil.virtual_memory().available / (1024**3)
            max_by_memory = max(1, int(available_gb / 2))
            return min(cores, max_by_memory)
        except Exception:
            return cores
    return int(max_workers)


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
    import torch

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
