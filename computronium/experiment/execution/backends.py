"""Execution backends for experiment evaluation (WP4 + WP19)."""

from __future__ import annotations

import asyncio
import logging
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from computronium.experiment.schema.coordinate import Coordinate, Provenance, Schedule

if TYPE_CHECKING:
    from computronium.experiment.evidence.failure import FailureEvent
    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.schema.record import Record

logger = logging.getLogger(__name__)


# =============================================================================
# Failure Isolation Types (WP19)
# =============================================================================


@dataclass(frozen=True, slots=True)
class Success:
    """Successful evaluation result."""

    record: Record


@dataclass(frozen=True, slots=True)
class Failure:
    """Failed evaluation result."""

    failure_event: FailureEvent


EvaluationResult = Success | Failure


# =============================================================================
# Backend Protocol
# =============================================================================


@runtime_checkable
class ExecutionBackend(Protocol):
    """Protocol for execution backends.

    Workers return Records; the pipeline process is the sole writer
    (single-writer topology per §1.1). In-process concurrency via
    asyncio.TaskGroup; blocking evaluation bodies stay out of the event loop
    via asyncio.to_thread.

    Failure isolation (WP19): submit_batch returns per-item EvaluationResult
    instead of raising exceptions, allowing successful siblings to continue.
    """

    async def submit(
        self,
        coordinate: Coordinate,
        schedule: Schedule,
        provenance: Provenance,
        params: dict[str, Any],
        store: RecordStore,
    ) -> list[Record]:
        """Submit an evaluation and return completed records.

        Args:
            coordinate: The 6-axis experiment coordinate
            schedule: Execution schedule
            provenance: Provenance metadata
            params: Experiment parameters
            store: RecordStore for persistence (pipeline is sole writer)

        Returns:
            List of completed Records (one per seed).
        """
        ...

    async def submit_batch(
        self,
        items: list[tuple[Coordinate, Schedule, Provenance, dict[str, Any]]],
        store: RecordStore,
    ) -> list[EvaluationResult]:
        """Submit a batch of evaluations.

        Args:
            items: List of (coordinate, schedule, provenance, params)
            store: RecordStore for persistence

        Returns:
            List of EvaluationResult (Success or Failure per item).
            Successful siblings continue even if some items fail.
        """
        ...

    def shutdown(self) -> None:
        """Shutdown the backend and release resources."""
        ...


@dataclass(frozen=True, slots=True)
class EvaluationTask:
    """A single evaluation task."""

    coordinate: Coordinate
    schedule: Schedule
    provenance: Provenance
    params: dict[str, Any]


class LocalBackend:
    """Local in-process execution backend using asyncio.TaskGroup.

    Workers run in the same process; evaluation bodies are offloaded to
    threads via asyncio.to_thread to avoid blocking the event loop.
    """

    def __init__(self, *, max_workers: int = 4) -> None:
        self._max_workers = max_workers
        self._executor: ThreadPoolExecutor | None = None
        self._shutdown = False

    async def submit(
        self,
        coordinate: Coordinate,
        schedule: Schedule,
        provenance: Provenance,
        params: dict[str, Any],
        store: RecordStore,
    ) -> list[Record]:
        """Submit a single evaluation (one schedule, multiple seeds)."""
        if self._executor is None:
            self._executor = ThreadPoolExecutor(max_workers=self._max_workers)

        records = []
        for seed_offset in range(schedule.n_seeds):
            seed = schedule.seed + seed_offset
            task_schedule = Schedule(
                fidelity=schedule.fidelity,
                seed=seed,
                n_seeds=1,
                epochs=schedule.epochs,
                batch_limit=schedule.batch_limit,
                budget_id=schedule.budget_id,
            )
            record = await asyncio.to_thread(
                self._evaluate_single,
                coordinate,
                task_schedule,
                provenance,
                params,
            )
            records.append(record)
        return records

    async def submit_batch(
        self,
        items: list[tuple[Coordinate, Schedule, Provenance, dict[str, Any]]],
        store: RecordStore,
    ) -> list[EvaluationResult]:
        """Submit a batch of evaluations concurrently with failure isolation."""
        if self._executor is None:
            self._executor = ThreadPoolExecutor(max_workers=self._max_workers)

        async def submit_one(
            coord: Coordinate,
            sched: Schedule,
            prov: Provenance,
            params: dict[str, Any],
        ) -> EvaluationResult:
            try:
                records = await self.submit(coord, sched, prov, params, store)
                # Return first record as success (submit returns one per seed)
                return (
                    Success(record=records[0])
                    if records
                    else Failure(
                        failure_event=self._create_failure_event(
                            coord, sched, prov, "No records returned"
                        )
                    )
                )
            except Exception as e:
                return Failure(
                    failure_event=self._create_failure_event(coord, sched, prov, str(e))
                )

        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(submit_one(coord, sched, prov, params))
                for coord, sched, prov, params in items
            ]

        return [task.result() for task in tasks]

    def _create_failure_event(
        self,
        coordinate: Coordinate,
        schedule: Schedule,
        provenance: Provenance,
        error_message: str,
    ) -> FailureEvent:
        """Create a FailureEvent for a failed evaluation."""
        from computronium.experiment.evidence.failure import FailureEvent
        from computronium.experiment.schema.record import FailureCause

        return FailureEvent(
            cell_key=coordinate.cell_key(),
            failure_cause=FailureCause.RUNTIME_ERROR,
            error_message=error_message,
            coordinate=coordinate.to_dict(),
            schedule=schedule.to_dict(),
            provenance=provenance.to_dict(),
        )

    def _evaluate_single(
        self,
        coordinate: Coordinate,
        schedule: Schedule,
        provenance: Provenance,
        params: dict[str, Any],
    ) -> Record:
        """Evaluate a single cell (blocking call, runs in thread pool).

        This is a placeholder - actual evaluation integrates with the
        ontology/system stack. For now, returns a minimal valid Record.
        """
        import time

        from computronium.experiment.schema.record import (
            FailureCause,
            GateVerdict,
            Maturity,
            Record,
            ReproducibilityClass,
            Severity,
            Status,
        )

        start = time.monotonic()

        # Placeholder: actual evaluation would go here
        # This integrates with the 6-axis ontology system
        payload = {
            "status": "evaluated",
            "walltime_s": time.monotonic() - start,
            "seed": schedule.seed,
            "fidelity": schedule.fidelity,
            "epochs_completed": schedule.epochs,
        }

        status = Status(
            gate_verdict=GateVerdict.PENDING,
            defect="",
            cause=FailureCause.UNKNOWN,
            severity=Severity.LOW,
            quarantine=False,
            maturity=Maturity.L0,
            uncertainty={},
            reproducibility=ReproducibilityClass.REPLAYABLE,
            assessment_procedure_version="1.0",
            ceec_link=None,
        )

        return Record.create(
            run_id=provenance.links.get("run_id", str(uuid.uuid4())),
            coordinate=coordinate,
            schedule=schedule,
            provenance=provenance,
            status=status,
            payload=payload,
        )

    def shutdown(self) -> None:
        """Shutdown the thread pool."""
        if self._executor is not None:
            self._executor.shutdown(wait=True)
            self._executor = None
        self._shutdown = True


class MultiprocessBackend:
    """Multiprocess execution backend for CPU-intensive evaluations.

    Uses asyncio.to_thread with a process pool for true parallelism.
    Each worker process evaluates independently; results are serialized
    and returned to the pipeline process for writing.
    """

    def __init__(self, *, max_workers: int = 4) -> None:
        self._max_workers = max_workers
        self._executor: ThreadPoolExecutor | None = None
        self._shutdown = False

    async def submit(
        self,
        coordinate: Coordinate,
        schedule: Schedule,
        provenance: Provenance,
        params: dict[str, Any],
        store: RecordStore,
    ) -> list[Record]:
        """Submit a single evaluation across multiple processes."""
        if self._executor is None:
            self._executor = ThreadPoolExecutor(max_workers=self._max_workers)

        records = []
        for seed_offset in range(schedule.n_seeds):
            seed = schedule.seed + seed_offset
            task_schedule = Schedule(
                fidelity=schedule.fidelity,
                seed=seed,
                n_seeds=1,
                epochs=schedule.epochs,
                batch_limit=schedule.batch_limit,
                budget_id=schedule.budget_id,
            )
            record = await asyncio.to_thread(
                self._evaluate_single_process,
                coordinate,
                task_schedule,
                provenance,
                params,
            )
            records.append(record)
        return records

    async def submit_batch(
        self,
        items: list[tuple[Coordinate, Schedule, Provenance, dict[str, Any]]],
        store: RecordStore,
    ) -> list[EvaluationResult]:
        """Submit a batch of evaluations concurrently across processes with failure isolation."""
        if self._executor is None:
            self._executor = ThreadPoolExecutor(max_workers=self._max_workers)

        async def submit_one(
            coord: Coordinate,
            sched: Schedule,
            prov: Provenance,
            params: dict[str, Any],
        ) -> EvaluationResult:
            try:
                records = await self.submit(coord, sched, prov, params, store)
                return (
                    Success(record=records[0])
                    if records
                    else Failure(
                        failure_event=self._create_failure_event(
                            coord, sched, prov, "No records returned"
                        )
                    )
                )
            except Exception as e:
                return Failure(
                    failure_event=self._create_failure_event(coord, sched, prov, str(e))
                )

        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(submit_one(coord, sched, prov, params))
                for coord, sched, prov, params in items
            ]

        return [task.result() for task in tasks]

    def _create_failure_event(
        self,
        coordinate: Coordinate,
        schedule: Schedule,
        provenance: Provenance,
        error_message: str,
    ) -> FailureEvent:
        """Create a FailureEvent for a failed evaluation."""
        from computronium.experiment.evidence.failure import FailureEvent
        from computronium.experiment.schema.record import FailureCause

        return FailureEvent(
            cell_key=coordinate.cell_key(),
            failure_cause=FailureCause.RUNTIME_ERROR,
            error_message=error_message,
            coordinate=coordinate.to_dict(),
            schedule=schedule.to_dict(),
            provenance=provenance.to_dict(),
        )

    def _evaluate_single_process(
        self,
        coordinate: Coordinate,
        schedule: Schedule,
        provenance: Provenance,
        params: dict[str, Any],
    ) -> Record:
        """Evaluate a single cell in a worker process (blocking)."""
        import time

        from computronium.experiment.schema.record import (
            FailureCause,
            GateVerdict,
            Maturity,
            Record,
            ReproducibilityClass,
            Severity,
            Status,
        )

        start = time.monotonic()

        # Placeholder: actual evaluation would integrate with the ontology stack
        payload = {
            "status": "evaluated",
            "walltime_s": time.monotonic() - start,
            "seed": schedule.seed,
            "fidelity": schedule.fidelity,
            "epochs_completed": schedule.epochs,
            "worker_pid": threading.get_ident(),
        }

        status = Status(
            gate_verdict=GateVerdict.PENDING,
            defect="",
            cause=FailureCause.UNKNOWN,
            severity=Severity.LOW,
            quarantine=False,
            maturity=Maturity.L0,
            uncertainty={},
            reproducibility=ReproducibilityClass.REPLAYABLE,
            assessment_procedure_version="1.0",
            ceec_link=None,
        )

        return Record.create(
            run_id=provenance.links.get("run_id", str(uuid.uuid4())),
            coordinate=coordinate,
            schedule=schedule,
            provenance=provenance,
            status=status,
            payload=payload,
        )

    def shutdown(self) -> None:
        """Shutdown the thread pool."""
        if self._executor is not None:
            self._executor.shutdown(wait=True)
            self._executor = None
        self._shutdown = True


__all__ = [
    "EvaluationResult",
    "EvaluationTask",
    "ExecutionBackend",
    "Failure",
    "LocalBackend",
    "MultiprocessBackend",
    "Success",
]
