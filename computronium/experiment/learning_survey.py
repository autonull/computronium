"""LearningSurvey: Adaptive experiment system with policy-driven exploration.

Reuses SimpleSurvey's spec builder, evaluator, wave executor, store schema and report.
Replaces the static planner with propose → measure → observe using ModelBasedPolicy.
"""

from __future__ import annotations

# Disable CUDA before ANY torch import if --device cpu is in argv
import os
import sys

import torch

if "--device" in sys.argv:
    try:
        idx = sys.argv.index("--device")
        if idx + 1 < len(sys.argv) and sys.argv[idx + 1] == "cpu":
            os.environ["CUDA_VISIBLE_DEVICES"] = ""
    except ValueError, IndexError:
        pass

import argparse
import contextlib
import json
import random
import shutil
import subprocess  # ruff: ignore[suspicious-subprocess-import] - used for git SHA lookup with validated path
import time
import uuid
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from collections.abc import Sequence

from computronium.core.logging import get_logger
from computronium.core.utils.device import get_device
from computronium.domains._task_registry import get_fidelity_tasks
from computronium.experiment.evidence.store import RecordStore
from computronium.experiment.evidence.store._models import StoreConfig
from computronium.experiment.kernel.evaluate import (
    cell_record,
    task_shape,
)
from computronium.experiment.kernel.search_space import (
    iter_candidates,
    schedule_for,
    search_space_from_spec,
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


@dataclass(frozen=True, slots=True)
class LearningSurveyResult:
    """Result of a LearningSurvey run."""

    run_id: str
    store_path: str
    cells_evaluated: int
    cells_passed: int
    cells_failed: int
    walltime_s: float
    report: dict
    waves_completed: int
    budget_split: dict[str, float]  # fidelity -> fraction of walltime


# Fallback per-cell costs (seconds) used until the run has measured its own.
DEFAULT_COSTS: dict[str, float] = {
    "L0": 5.0,  # 1 epoch, 1 seed
    "L1": 30.0,  # 3 epochs, 2 seeds (updated via schedule_for)
    "L2": 300.0,  # 10 epochs, 5 seeds (updated via schedule_for)
}

# Fallback fixed cost of starting a run: imports, task construction, pool spawn.
DEFAULT_STARTUP_S = 10.0

# Measured costs, shared across runs so the second run is not a guess.
TIMING_CACHE = Path("experiments") / ".timing.json"

# Rows the dry-run table shows before summarising the rest.
MAX_PREVIEW_CELLS = 20

# Wave sizing bounds
MIN_WAVE = 1
MAX_WAVE = 64


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
    """Measured cost for this device, fidelity, and worker count, else the fallback table."""
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
    """Persist a measurement so the next run sizes itself from it."""
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


# Structural axes in mutation order (kept for compatibility with promote_from mutation)
MUTATION_AXES: list[StructuralAxis] = [
    StructuralAxis.SUBSTRATE,
    StructuralAxis.GEOMETRY,
    StructuralAxis.DYNAMICS,
    StructuralAxis.PLASTICITY,
    StructuralAxis.CREDIT,
    StructuralAxis.UPDATE,
]


def _build_provenance(
    spec: RunSpec, run_id: str, data_origin: DataOrigin = DataOrigin.POLICY_SELECTED
) -> Provenance:
    """Build provenance metadata for records."""
    git_path = shutil.which("git")
    code_sha = "unknown"
    if git_path:
        with contextlib.suppress(Exception):
            code_sha = subprocess.check_output(  # ruff: ignore[subprocess-without-shell-equals-true]
                [git_path, "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True
            ).strip()
        with contextlib.suppress(Exception):
            if code_sha == "unknown":
                code_sha = subprocess.check_output(  # ruff: ignore[subprocess-without-shell-equals-true]
                    [git_path, "rev-parse", "--short", "HEAD"],
                    stderr=subprocess.DEVNULL,
                    text=True,
                ).strip()

    dataset = spec.dataset if spec.dataset != "unknown" else "digits"
    dataset_version = spec.dataset_version if spec.dataset_version != "1.0" else "1.0"

    return Provenance(
        env={
            k: v
            for k, v in os.environ.items()
            if k.startswith(("CUDA", "TORCH", "OMP"))
        },
        dataset=dataset,
        dataset_version=dataset_version,
        code_sha=code_sha,
        policy="learning_survey",
        links={"run_id": run_id},
        data_origin=data_origin,
    )


def _check_coord_compatibility(coord: Coordinate) -> bool:
    """Check if a coordinate passes the compatibility matrix."""
    violations = check_compatibility_matrix(
        coord.substrate,
        coord.geometry,
        coord.dynamics,
        coord.plasticity,
        coord.credit,
        coord.update,
    )
    return not violations


# ============================================================
# Planner Protocol and Implementations
# ============================================================


class Planner(Protocol):
    """Protocol for cell planners (static or policy-driven)."""

    def propose(self, n: int, *, seen: set[str]) -> list[tuple[Coordinate, Schedule]]:
        """Propose up to n cells, skipping those in `seen`."""
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
        self._init_resume()

    def _init_resume(self) -> None:
        """Load already-measured keys from resume store."""
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
        """Load top coordinates from promotion store (D1 fix: by measurement, not target fidelity)."""
        if not self.promote_from:
            return []
        try:  # ruff: ignore[too-many-nested-blocks] - try block complexity is inherent to store query pattern
            store = RecordStore(StoreConfig(path=Path(self.promote_from)))
            with store:
                records = store.query_records(
                    gate_verdict=GateVerdict.PASS_,
                    quarantine=False,
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
        """Mutate 1-2 axes of top performers to explore neighborhood."""
        mutated_cells: list[tuple[Coordinate, Schedule]] = []

        if not top_coords:
            return mutated_cells

        per_coord = max(1, n // len(top_coords))

        for coord in top_coords:
            for _ in range(per_coord):
                if len(mutated_cells) >= n:
                    break

                k = random.randint(1, 2)  # ruff: ignore[suspicious-non-cryptographic-random-usage]
                axes_to_mutate = random.sample(MUTATION_AXES, k)  # ruff: ignore[suspicious-non-cryptographic-random-usage]

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
                        new_values[axis.value] = random.choice(primitives)  # ruff: ignore[suspicious-non-cryptographic-random-usage]

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

                task = random.choice(self.tasks)  # ruff: ignore[suspicious-non-cryptographic-random-usage]
                schedule = schedule_for(self.spec, task, self.fidelity)

                measurement_key = mutated_coord.measurement_key(schedule)
                if measurement_key in self._seen:
                    continue
                self._seen.add(measurement_key)

                mutated_cells.append((mutated_coord, schedule))

        return mutated_cells

    def _random_explore(self, n: int) -> list[tuple[Coordinate, Schedule]]:
        """Random valid cells from iter_candidates, paging until N or space exhausted."""
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

    def propose(self, n: int, *, seen: set[str]) -> list[tuple[Coordinate, Schedule]]:
        """Propose cells: exploitation (mutated promotion) then exploration."""
        # Merge external seen set (e.g., from concurrent waves)
        self._seen.update(seen)

        cells: list[tuple[Coordinate, Schedule]] = []

        # 1. Exploitation: bias toward prior winners
        if not self._exploitation_done and self.promote_from:
            self._top_coords = self._load_promotion_coords()
            if self._top_coords:
                cells.extend(self._mutate_around(self._top_coords, n // 2))
            self._exploitation_done = True

        # 2. Exploration: random valid cells
        remaining = n - len(cells)
        if remaining > 0:
            cells.extend(self._random_explore(remaining))

        return cells[:n]

    def observe(self, record: Any) -> None:
        """Static planner doesn't learn from observations."""

    def after_wave(self) -> None:
        """Static planner has no wave-end logic."""


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
        resume_from: str | None = None,
    ):
        self.spec = spec
        self.fidelity = fidelity
        self.tasks = tasks
        self.seed = seed
        self.search_space = search_space
        self.policy_name = policy
        self.n_startup_trials = n_startup_trials

        self._seen: set[str] = set()
        self._wave_count = 0
        self._policy: Any = None
        self._study: Any = None
        self._init_policy()
        self._init_resume(resume_from)

    def _init_resume(self, resume_from: str | None) -> None:
        """Warm-start the study from prior store records (§4.7)."""
        if not resume_from:
            return
        try:  # ruff: ignore[too-many-nested-blocks] - try block complexity is inherent to store query pattern
            store = RecordStore(StoreConfig(path=Path(resume_from)))
            with store:
                records = store.query_records(
                    gate_verdict=GateVerdict.PASS_,
                    quarantine=False,
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

            # Replay top records through policy.observe
            for record in valid_records[:20]:  # top 20 by default
                self._policy.observe(record)
                self._seen.add(record.measurement_key)

            logger.info(
                "Warm-started policy with %d records from %s",
                len(valid_records),
                resume_from,
            )
        except Exception as exc:
            logger.warning("Could not warm-start from %s: %s", resume_from, exc)

    def _init_policy(self) -> None:
        """Initialize the sampler policy."""
        from computronium.experiment.execution.policy import (
            DiverseRandomPolicy,
            ModelBasedPolicy,
        )

        # Define the search space for the policy
        # The policy operates over the 6 structural axes
        axes_config = {}
        for axis in StructuralAxis:
            primitives = self.search_space.primitives(axis)
            if primitives:
                axes_config[axis.value] = list(primitives)

        if self.policy_name == "random":
            self._policy = DiverseRandomPolicy(axes_config, seed=self.seed)
        else:
            sampler = "tpe" if self.policy_name == "tpe" else "nsga2"
            self._policy = ModelBasedPolicy(
                axes_config,
                sampler=sampler,
                seed=self.seed,
                n_startup_trials=self.n_startup_trials,
            )

    def propose(self, n: int, *, seen: set[str]) -> list[tuple[Coordinate, Schedule]]:
        """Propose cells using the policy."""
        self._seen.update(seen)

        # Get proposals from policy
        from computronium.experiment.execution.policy import ProposalContext

        context = ProposalContext(
            n_proposals=n,
            legal_primitives=self._get_legal_primitives(),
            seen_keys=self._seen,
            fidelity=self.fidelity,
            tasks=list(self.tasks),
            spec=self.spec,
        )

        proposals = self._policy.propose(context)

        # Convert proposals to (Coordinate, Schedule) pairs
        cells: list[tuple[Coordinate, Schedule]] = []
        for prop in proposals:
            if len(cells) >= n:
                break

            coord = Coordinate(
                substrate=prop["substrate"],
                geometry=prop["geometry"],
                dynamics=prop["dynamics"],
                plasticity=prop["plasticity"],
                credit=prop["credit"],
                update=prop["update"],
                params=prop.get("params", {}),
            )

            if not _check_coord_compatibility(coord):
                continue

            task = prop.get("task", random.choice(self.tasks))  # ruff: ignore[suspicious-non-cryptographic-random-usage]
            schedule = schedule_for(self.spec, task, self.fidelity)

            measurement_key = coord.measurement_key(schedule)
            if measurement_key in self._seen:
                continue
            self._seen.add(measurement_key)

            cells.append((coord, schedule))

        return cells

    def _get_legal_primitives(self) -> dict[str, list[str]]:
        """Get legal primitives per axis for the policy."""
        legal: dict[str, list[str]] = {}
        for axis in StructuralAxis:
            primitives = self.search_space.primitives(axis)
            if primitives:
                legal[axis.value] = list(primitives)
        return legal

    def observe(self, record: Any) -> None:
        """Feed record to policy for learning."""
        self._policy.observe(record)

    def after_wave(self) -> None:
        """Called after each wave; can trigger fidelity promotion."""
        self._wave_count += 1
        # Fidelity promotion logic would go here (§4.5)
        # For now, just log
        logger.debug("Wave %d completed", self._wave_count)


# ============================================================
# Shared Wave Execution (extracted from SimpleSurvey)
# ============================================================


@dataclass(frozen=True, slots=True)
class _Evaluation:
    """What a parallel evaluation measured."""

    results: list
    elapsed_s: float
    startup_s: float
    skipped: int


def _init_worker(cpu_threads: int, device: str) -> None:
    """Pin one worker's torch to ``cpu_threads`` and disable CUDA for cpu mode."""
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
    """Evaluate a single cell (for ProcessPoolExecutor)."""
    coord, schedule = cell
    try:
        return cell_record(
            coordinate=coord,
            schedule=schedule,
            provenance=provenance,
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
    """One progress line for a landed cell."""
    gate = record.status.gate_verdict.value
    val_acc = record.payload.get("val_acc", "N/A")
    logger.info(
        "  [%d/%d] %s | val_acc=%s | %s/%s/%s/%s/%s/%s",
        i,
        n_total,
        gate,
        f"{val_acc:.4f}" if isinstance(val_acc, float) else val_acc,
        record.substrate,
        record.geometry,
        record.dynamics,
        record.plasticity,
        record.credit,
        record.update,
    )


def _blend(previous: CostModel, measured: CostModel) -> CostModel:
    """Half-way between what we believed and what the run just showed."""
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


def _evaluate_cells_parallel(  # ruff: ignore[too-many-branches,too-many-arguments,too-many-statements] - experiment orchestration inherently complex
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
) -> _Evaluation:
    """Evaluate cells in parallel, stopping when the budget is spent.

    Records are appended to the store as they land (streaming), so an interruption
    preserves all completed work.
    """
    import signal

    n_total = len(cells)
    results: list = []
    started = time.monotonic()
    deadline = started + budget_seconds if budget_seconds else None
    queue = iter(cells)
    pending: dict[Any, tuple[Coordinate, Schedule]] = {}
    startup_s = 0.0

    # Initialize store for streaming writes
    store_config = StoreConfig(path=Path(store_path))
    store = RecordStore(store_config)
    if run_id and spec:
        store.create_run(run_id, spec)

    # SIGTERM handler: close store gracefully
    def _sigterm_handler(signum, frame):
        logger.info("SIGTERM received, closing store after current record...")
        store.close()
        sys.exit(130)

    old_sigterm = signal.signal(signal.SIGTERM, _sigterm_handler)
    old_sigint = signal.signal(signal.SIGINT, _sigterm_handler)

    logger.info("Evaluating up to %d cells with %d workers...", n_total, max_workers)

    try:
        with ProcessPoolExecutor(
            max_workers=max_workers,
            initializer=_init_worker,
            initargs=(cpu_threads, device_str),
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
                for future in wait(pending, return_when=FIRST_COMPLETED).done:
                    del pending[future]
                    record = future.result()
                    results.append(record)

                    # Stream record to store immediately
                    store.append(record)

                    if not startup_s:
                        startup_s = max(
                            0.0,
                            (time.monotonic() - started)
                            - float(record.payload.get("walltime_s", 0.0)),
                        )

                    i = len(results)
                    if verbose or i % max(1, n_total // 10) == 0 or i == n_total:
                        _log_progress(i, n_total, record)

                    if deadline is None or time.monotonic() < deadline:
                        _submit_next()

    finally:
        signal.signal(signal.SIGTERM, old_sigterm)
        signal.signal(signal.SIGINT, old_sigint)
        store.close()

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


def _generate_report(store_path: str, run_id: str) -> dict:
    """Generate report from stored results."""
    from computronium.experiment.surface.report import ReportGenerator

    store_config = StoreConfig(path=Path(store_path))
    with RecordStore(store_config) as store:
        generator = ReportGenerator(store)
        return generator.run_summary(run_id)


# ============================================================
# Main Entry Points
# ============================================================


@dataclass(frozen=True, slots=True)
class _SpecParams:
    """Parameters for building a RunSpec."""

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


def _build_spec(params: _SpecParams) -> RunSpec:
    """Build RunSpec from survey parameters."""
    from computronium.experiment.schema.axis import StructuralAxis
    from computronium.experiment.schema.run_spec import AxisSelection
    from computronium.experiment.schema.seed_registries import seed_all_registries

    seed_all_registries()

    axis_selections = []
    if params.axes:
        for axis_name, primitives in params.axes.items():
            axis_enum = getattr(StructuralAxis, axis_name.upper())
            axis_selections.append(AxisSelection(axis=axis_enum, primitives=primitives))

    # n_seeds and epochs: None means "use fidelity ladder"
    n_seeds = params.n_seeds if params.n_seeds != 1 else None
    epochs = params.epochs if params.epochs != 1 else None

    spec = RunSpec(
        profile="learning_survey",
        task=params.tasks[0] if params.tasks else "auto",
        tasks=tuple(params.tasks) if params.tasks else (),
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
    )
    return spec


def _resolve_max_workers(max_workers: int | str, device: torch.device) -> int:
    """Resolve max_workers from 'auto' or int to actual count."""
    import os

    import psutil

    if max_workers == "auto" or (isinstance(max_workers, int) and max_workers <= 0):
        if device.type == "cuda":
            return torch.cuda.device_count() or 1
        # CPU: use all cores, bounded by memory (assume ~2GB per worker)
        cores = os.cpu_count() or 4
        try:
            import psutil

            available_gb = psutil.virtual_memory().available / (1024**3)
            max_by_memory = max(1, int(available_gb / 2))
            return min(cores, max_by_memory)
        except Exception:
            return cores
    return int(max_workers)


def _default_store_path() -> str:
    """Generate default timestamped store path in experiments/ directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    exp_dir = Path("experiments")
    exp_dir.mkdir(parents=True, exist_ok=True)
    return str(exp_dir / f"experiment_{timestamp}.duckdb")


def _format_error(message: str, hint: str | None = None) -> str:
    """Format a user-friendly error message."""
    lines = [f"Error: {message}"]
    if hint:
        lines.append(f"Hint: {hint}")
    return "\n".join(lines)


def run_learning_survey(  # ruff: ignore[too-many-branches, too-many-arguments, too-many-locals, too-many-statements] - experiment orchestration inherently complex
    hours: float,
    fidelity: str = "L0",
    tasks: Sequence[str] | None = None,
    max_workers: int | str = "auto",
    store_path: str = "experiment.duckdb",
    promote_from: str | None = None,
    promote_top: int = 20,
    seed: int = 42,
    dry_run: bool = False,
    device: str = "auto",
    param_budget: int = 0,
    n_seeds: int = 1,
    epochs: int = 1,
    batch_limit: int = 0,
    axes: dict[str, tuple[str, ...]] | None = None,
    hyperparameters: dict[str, Any] | None = None,
    objectives: tuple[str, ...] = (),
    verbose: bool = False,
    cpu_threads: int = 1,
    resume: bool = False,
    ladder: bool = False,
    policy: str = "tpe",
) -> dict[str, Any]:
    """Run a LearningSurvey experiment.

    Args:
        hours: Time budget in hours; evaluation stops when it is spent.
        fidelity: Fidelity level (L0, L1, L2). Used as starting fidelity if ladder=True.
        tasks: Task names to use (defaults to fidelity-appropriate tasks).
        max_workers: Number of parallel workers, or ``"auto"``.
        store_path: Path to DuckDB store.
        promote_from: Path to prior store for warm-start (learning mode) or importance sampling.
        promote_top: Number of top cells to promote from prior run.
        seed: Random seed.
        dry_run: If True, only generate wave-0 cells and return them without evaluation.
        device: Device to run on.
        param_budget: Parameter budget ceiling.
        n_seeds: Number of seeds per cell (1 = use fidelity ladder).
        epochs: Number of epochs (1 = use fidelity ladder).
        batch_limit: Batch limit (0 for full dataset).
        axes: Axis selections (axis -> primitives).
        hyperparameters: Hyperparameter domains.
        objectives: Objective names.
        verbose: Verbose progress output.
        cpu_threads: Torch threads per worker (1 avoids CPU oversubscription).
        resume: If True, warm-start policy from store_path records.
        ladder: If True, run L0→L1→L2 promotion in one invocation.
        policy: Sampler policy: "tpe", "nsga2", or "random".

    Returns:
        If dry_run: {"cells": list[(coord, schedule)], "n": int, "tasks": list[str],
        "model": CostModel, "workers": int, "wave": 0}
        If evaluation: {"run_id": str, "store_path": str, "cells_evaluated": int, ...}
    """

    # Resolve device string for worker init and CUDA control
    device_obj = get_device(device)
    device_str = device_obj.type

    # 1. Build RunSpec
    params = _SpecParams(
        hours=hours,
        fidelity=fidelity,
        tasks=tasks,
        seed=seed,
        device=device,
        param_budget=param_budget,
        n_seeds=n_seeds,
        epochs=epochs,
        batch_limit=batch_limit,
        axes=axes,
        hyperparameters=hyperparameters,
        objectives=objectives,
    )
    spec = _build_spec(params)

    # 2. Determine tasks to use
    if tasks is None:
        tasks = get_fidelity_tasks(fidelity)

    workers = _resolve_max_workers(max_workers, device_obj)
    model = _load_cost_model(device_str, fidelity, workers)

    # 3. Create search space
    search_space = search_space_from_spec(spec, tasks=tasks)

    # 4. Create planner
    if ladder:
        # Ladder mode: start at L0, promote to L1, then L2
        # For now, just log and run at starting fidelity
        # Full ladder implementation is §4.5
        logger.info(
            "Ladder mode enabled: will promote L0→L1→L2 (not yet fully implemented)"
        )
        planner: Planner = PolicyPlanner(
            spec=spec,
            fidelity=fidelity,
            tasks=tasks,
            seed=seed,
            search_space=search_space,
            policy=policy,
            resume_from=store_path if resume else None,
        )
    else:
        planner = PolicyPlanner(
            spec=spec,
            fidelity=fidelity,
            tasks=tasks,
            seed=seed,
            search_space=search_space,
            policy=policy,
            resume_from=store_path if resume else None,
        )

    # 5. Generate initial wave (wave 0 = startup trials)
    n_startup = (
        planner._policy.n_startup_trials
        if hasattr(planner._policy, "n_startup_trials")
        else 3
    )
    startup_cells = planner.propose(n_startup * workers, seen=set())

    if dry_run:
        return {
            "cells": startup_cells,
            "n": len(startup_cells),
            "tasks": list(tasks),
            "fidelity": fidelity,
            "model": model,
            "workers": workers,
            "wave": 0,
        }

    # 6. Run waves until budget exhausted
    run_id = str(uuid.uuid4())[:8]
    provenance = _build_provenance(spec, run_id)

    all_results: list = []
    total_elapsed = 0.0
    wave = 0
    budget_remaining = spec.budget_seconds
    fidelity_walltime: dict[str, float] = {}

    # Positive control (P3): gate the report
    # TODO: Implement positive control cell evaluation

    while budget_remaining > 0:
        wave += 1
        logger.info("=== Wave %d (budget remaining: %.0fs) ===", wave, budget_remaining)

        # Size wave based on measured throughput
        if all_results:
            measured_cost = total_elapsed * workers / len(all_results)
            n_wave = max(
                MIN_WAVE,
                min(
                    MAX_WAVE, int(budget_remaining * workers / max(1.0, measured_cost))
                ),
            )
        else:
            n_wave = min(MAX_WAVE, workers * 2)

        # Propose cells
        cells = planner.propose(n_wave, seen=set())
        if not cells:
            logger.info("No more cells to evaluate")
            break

        # Evaluate wave
        wave_start = time.monotonic()
        evaluation = _evaluate_cells_parallel(
            cells=cells,
            fidelity=fidelity,
            store_path=store_path,
            provenance=provenance,
            max_workers=workers,
            verbose=verbose,
            budget_seconds=budget_remaining,
            cpu_threads=cpu_threads,
            device_str=device_str,
            run_id=run_id,
            spec=spec,
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

            measured = CostModel(
                cost_per_cell_s=max(
                    0.01, wave_elapsed * workers / len(evaluation.results)
                ),
                startup_s=evaluation.startup_s,
                measured=True,
                workers=workers,
                per_task=per_task,
            )
            logger.info(
                "Wave %d measured: %.1fs/cell, %.0fs startup (prior: %.1fs/cell)",
                wave,
                measured.cost_per_cell_s,
                measured.startup_s,
                model.cost_per_cell_s,
            )
            _save_cost_model(device_str, fidelity, _blend(model, measured))
            model = measured

        if evaluation.skipped > 0:
            logger.info("Budget exhausted mid-wave")
            break

    # 7. Generate report
    report = _generate_report(store_path, run_id)

    passed = sum(1 for r in all_results if r.status.gate_verdict.value == "PASS")
    failed = len(all_results) - passed

    # Compute budget split
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

    return {
        "run_id": run_id,
        "store_path": store_path,
        "cells_evaluated": len(all_results),
        "cells_passed": passed,
        "cells_failed": failed,
        "cells_skipped": evaluation.skipped if evaluation.results else 0,
        "walltime_s": total_elapsed,
        "report": report,
        "waves_completed": wave,
        "budget_split": budget_split,
    }


def main() -> None:  # ruff: ignore[too-many-statements, too-many-locals, too-many-branches, complex-structure]
    """CLI entry point for learning_survey."""
    import logging

    logging.basicConfig(level=logging.INFO, format="%(message)s", force=True)

    parser = argparse.ArgumentParser(
        description="LearningSurvey - Adaptive experiment system with policy-driven exploration"
    )
    parser.add_argument(
        "hours",
        type=float,
        nargs="?",
        help="Time budget in hours (required unless --doctor)",
    )
    parser.add_argument("--fidelity", default="L0", choices=["L0", "L1", "L2"])
    parser.add_argument(
        "--tasks", default="", help="Comma-separated task names (default: auto)"
    )
    parser.add_argument(
        "--max-workers", default="auto", help="Max workers (int or 'auto')"
    )
    parser.add_argument(
        "--cpu-threads",
        type=int,
        default=1,
        help="Torch threads per worker (default 1)",
    )
    parser.add_argument(
        "--store",
        default=None,
        help="DuckDB store path (default: experiments/experiment_YYYYMMDD_HHMMSS.duckdb)",
    )
    parser.add_argument("--promote-from", default=None)
    parser.add_argument("--promote-top", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--dry-run-format",
        choices=["json", "table", "summary"],
        default="table",
        help="Dry-run output format",
    )
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    parser.add_argument("--param-budget", type=int, default=0)
    parser.add_argument("--n-seeds", type=int, default=1)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch-limit", type=int, default=0)
    parser.add_argument("--axes", default="", help="JSON: axis -> [primitives]")
    parser.add_argument(
        "--digital", action="store_true", help="Restrict to digital substrate only"
    )
    parser.add_argument("--hyperparameters", default="", help="JSON: hyperparameters")
    parser.add_argument("--objectives", default="", help="Comma-separated objectives")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose progress output"
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress progress output"
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run environment self-test before experiment",
    )
    parser.add_argument(
        "--no-self-test",
        action="store_true",
        help="Deprecated: use --self-test to enable instead",
    )
    parser.add_argument(
        "--doctor", action="store_true", help="Run environment diagnostics and exit"
    )
    parser.add_argument(
        "--resume", action="store_true", help="Warm-start policy from existing store"
    )
    parser.add_argument(
        "--ladder", action="store_true", help="Run L0→L1→L2 fidelity ladder"
    )
    parser.add_argument(
        "--policy",
        default="tpe",
        choices=["tpe", "nsga2", "random"],
        help="Sampler policy (default: tpe)",
    )

    args = parser.parse_args()

    if args.doctor:
        from computronium.experiment.environment.diagnostics import (
            print_diagnostics,
            run_diagnostics,
        )

        result = run_diagnostics(device="cpu", hours=0.001)
        print_diagnostics(result)
        sys.exit(0)

    if args.hours is None:
        parser.error("hours argument required (unless using --doctor)")

    # Handle self-test flags
    run_self_test = args.self_test
    if args.no_self_test and not args.self_test:
        logger.warning(
            "--no-self-test is deprecated; self-test is now opt-in with --self-test"
        )
    elif args.no_self_test and args.self_test:
        parser.error("Cannot use both --self-test and --no-self-test")

    # Resolve device early (before self-test) to avoid CUDA probe in CPU mode
    try:
        device = get_device(args.device)
        device_str = device.type
    except Exception as e:
        print(_format_error(f"Failed to resolve device: {e}", "Try --device cpu"))
        sys.exit(1)

    # Disable CUDA visibility for cpu mode BEFORE any torch.cuda access
    if device_str == "cpu":
        os.environ["CUDA_VISIBLE_DEVICES"] = ""

    # Run self-test if requested
    if run_self_test:
        logger.info("Running self-test...")
        try:
            if not _run_self_test(device_str):
                print(
                    _format_error(
                        "Self-test failed",
                        "Run with --device cpu to skip CUDA checks, or fix the reported issue",
                    )
                )
                sys.exit(1)
        except Exception:
            logger.exception("Self-test CRASHED")
            import traceback

            traceback.print_exc()
            print(_format_error("Self-test crashed", "See traceback above for details"))
            sys.exit(1)
        logger.info("Self-test passed")

    # Determine verbosity: default to True for TTY unless --quiet
    verbose = args.verbose or (not args.quiet and sys.stdout.isatty())

    # Resolve store path
    store_path = args.store or _default_store_path()

    # Resolve max_workers
    max_workers = _resolve_max_workers(args.max_workers, device)

    tasks = args.tasks.split(",") if args.tasks else None
    axes = _axis_overrides(args.axes, digital=args.digital)
    hyperparameters = json.loads(args.hyperparameters) if args.hyperparameters else None
    objectives = tuple(args.objectives.split(",")) if args.objectives else ()

    try:  # ruff: ignore[too-many-nested-blocks] - main entry point try block is inherently complex
        result = run_learning_survey(
            hours=args.hours,
            fidelity=args.fidelity,
            tasks=tasks,
            max_workers=max_workers,
            store_path=store_path,
            promote_from=args.promote_from,
            promote_top=args.promote_top,
            seed=args.seed,
            dry_run=args.dry_run,
            device=device_str,
            param_budget=args.param_budget,
            n_seeds=args.n_seeds,
            epochs=args.epochs,
            batch_limit=args.batch_limit,
            axes=axes,
            hyperparameters=hyperparameters,
            objectives=objectives,
            verbose=verbose,
            cpu_threads=args.cpu_threads,
            resume=args.resume,
            ladder=args.ladder,
            policy=args.policy,
        )

        if args.dry_run:
            if args.dry_run_format == "json":
                print(json.dumps(result, default=str, indent=2))
            elif args.dry_run_format == "table":
                _pretty_print_dry_run(
                    result,
                    hours=args.hours,
                    fidelity=args.fidelity,
                    model=result["model"],
                    workers=result["workers"],
                )
            else:  # summary
                n = result.get("n", 0)
                tasks_str = ", ".join(result.get("tasks", []))
                model: CostModel = result["model"]
                total_est = model.startup_s + n * model.cost_per_cell_s / max(
                    1, result["workers"]
                )
                print(
                    f"Dry-run: {n} cells | {args.fidelity} | {tasks_str} | "
                    f"~{model.cost_per_cell_s:.1f}s/cell ({model.source}) | "
                    f"~{total_est:.0f}s total"
                )
        else:
            print(json.dumps(result, default=str, indent=2))

    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(130)
    except SystemExit:
        raise
    except Exception as e:
        error_msg = str(e)
        hint = None

        if "CUDA" in error_msg or "cuda" in error_msg.lower():
            hint = "Try --device cpu or export CUDA_VISIBLE_DEVICES=''"
        elif "search space" in error_msg.lower() or "no cells" in error_msg.lower():
            hint = "Try --fidelity L0 --device cpu, or check --axes constraints"
        elif "import" in error_msg.lower() or "module" in error_msg.lower():
            hint = "Run: uv sync --dev --all-extras"
        elif "permission" in error_msg.lower():
            hint = "Check file permissions for store path"
        elif "no space" in error_msg.lower() or "disk" in error_msg.lower():
            hint = "Free up disk space or use --store with a different path"

        print(_format_error(error_msg, hint))
        if verbose:
            logger.exception("Full traceback:")
        sys.exit(1)


def _axis_overrides(
    axes_json: str, *, digital: bool
) -> dict[str, tuple[str, ...]] | None:
    """Axes from the ``--axes`` JSON, with ``--digital`` pinning the substrate."""
    axes: dict[str, tuple[str, ...]] | None = (
        json.loads(axes_json) if axes_json else None
    )
    if not digital:
        return axes
    pinned = dict(axes or {})
    pinned["substrate"] = ("digital",)
    return pinned


# Self-test infrastructure (shared with simple_survey)
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
    uv_path = shutil.which("uv")
    if uv_path is None:
        logger.error("uv not found in PATH")
        return False
    try:
        result = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
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


def _check_dry_run(config: _SelfTestConfig) -> bool:
    try:
        result = run_learning_survey(
            config.dry_run_hours,
            fidelity=config.dry_run_fidelity,
            dry_run=True,
            device=config.dry_run_device,
        )
    except Exception:
        logger.exception("dry-run crashed")
        import traceback

        traceback.print_exc()
        return False
    else:
        n_cells = result.get("n", 0)
        logger.debug("Dry-run generated %d cells", n_cells)
        if n_cells == 0:
            logger.error(
                "dry-run generated 0 cells - search space may be empty or over-constrained"
            )
            logger.error("Try: --fidelity L0 --device cpu")
            return False
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
        ("dry-run", lambda: _check_dry_run(config)),
    ]

    for idx, (name, check) in enumerate(checks, 1):
        logger.info("Test %d/%d: %s...", idx, len(checks), name)
        if not check():
            logger.error("FAIL: %s", name)
            return False

    logger.info("ALL TESTS PASSED")
    return True


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

    print("\n=== LearningSurvey Dry-Run (Wave 0) ===")
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


if __name__ == "__main__":
    main()
