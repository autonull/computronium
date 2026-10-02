"""Execution backends for experiment evaluation (WP4 + WP19)."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from computronium.experiment.evidence.failure import FailureEvent
    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.schema.coordinate import (
        Coordinate,
        Provenance,
        Schedule,
    )
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


class _ThreadedBackend:
    """Shared backend: one evaluation implementation, off the event loop.

    Subclasses differ only in where the blocking body runs; the evaluation
    itself is always :func:`cell_record`, so a stub can never come back in one
    class while the other trains for real (TODO46 §D1).
    """

    def __init__(self, *, max_workers: int = 4) -> None:
        self._max_workers = max_workers
        self._shutdown = False

    def _evaluate(
        self,
        coordinate: Coordinate,
        schedule: Schedule,
        provenance: Provenance,
        params: dict[str, Any],
    ) -> Record:
        """Train one cell and wrap the measurement as a Record."""
        from computronium.experiment.execution.evaluate import cell_record

        return cell_record(coordinate, schedule, provenance, params)

    async def submit(
        self,
        coordinate: Coordinate,
        schedule: Schedule,
        provenance: Provenance,
        params: dict[str, Any],
        store: RecordStore,
    ) -> list[Record]:
        """Evaluate one coordinate across the schedule's seeds."""
        records = []
        for seed_offset in range(schedule.n_seeds):
            seed_schedule = replace(
                schedule, seed=schedule.seed + seed_offset, n_seeds=1
            )
            records.append(
                await asyncio.to_thread(
                    self._evaluate, coordinate, seed_schedule, provenance, params
                )
            )
        return records

    async def submit_batch(
        self,
        items: list[tuple[Coordinate, Schedule, Provenance, dict[str, Any]]],
        store: RecordStore,
    ) -> list[EvaluationResult]:
        """Evaluate a batch with per-item failure isolation (WP19)."""

        async def submit_one(
            coord: Coordinate,
            sched: Schedule,
            prov: Provenance,
            params: dict[str, Any],
        ) -> EvaluationResult:
            try:
                records = await self.submit(coord, sched, prov, params, store)
                if records:
                    return Success(record=records[0])
                return Failure(
                    failure_event=self._create_failure_event(
                        coord, sched, prov, "No records returned"
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

    def shutdown(self) -> None:
        """Release the backend. Evaluation bodies live on the default pool."""
        self._shutdown = True


class LocalBackend(_ThreadedBackend):
    """In-process backend; evaluation bodies run on the default thread pool."""


class MultiprocessBackend(_ThreadedBackend):
    """Worker-pool backend reserved for process isolation.

    Currently the same in-process execution as :class:`LocalBackend`: the
    evaluator owns its own device and threading, so forking adds cost without
    changing what is measured. Kept as the seam where process isolation lands.
    """


__all__ = [
    "EvaluationResult",
    "EvaluationTask",
    "ExecutionBackend",
    "Failure",
    "LocalBackend",
    "MultiprocessBackend",
    "Success",
]
