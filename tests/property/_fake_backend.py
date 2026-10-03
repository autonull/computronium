"""An ExecutionBackend that answers with records instead of training (TODO48b R1).

Everything the round loop *decides* is downstream of ``submit_batch``: the
seed-level dedup, the budget charge, the rejection classification, the resume
seeding, the S10 decision read, the termination heuristics. Verifying that
plumbing by training cells costs seconds per assertion and proves the wrong
thing — a cell that trains says the kernel trains.

This backend substitutes the evaluation and nothing else, so those assertions
cost milliseconds. It is tied to reality by the synchronization test in
``test_round_loop_mechanism_lock.py``: the same declaration run through this
backend and through a real ``LocalBackend`` must store an *identical* set of
``measurement_key``s. A fake that skipped the dedup, or the legality screen,
would make that set differ.
"""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

from computronium.experiment.evidence.failure import FailureEvent
from computronium.experiment.execution.backends import Failure, Success
from computronium.experiment.schema.record import (
    FailureCause,
    GateVerdict,
    Maturity,
    Record,
    ReproducibilityClass,
    Severity,
    Status,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.execution.backends import EvaluationResult
    from computronium.experiment.schema.coordinate import (
        Coordinate,
        Provenance,
        Schedule,
    )

# The payload key a synthetic accuracy is derived from, and the one cost
# metric the budget charge reads (``SimpleCostModel.actual_cost``).
SYNTHETIC_METRIC = "val_acc"
SYNTHETIC_WALLTIME_S = 0.01

type Rejection = Callable[[Coordinate, Schedule], str | None]


def _pseudo_metric(measurement_key: str) -> float:
    """A deterministic spread in [0.05, 0.95) from the measurement's own identity.

    Claims need a difference to test, so the fake's records must not all carry
    the same number: the spread is derived from the key rather than from a
    counter, so it does not depend on the order the round loop measured in.
    """
    digest = hashlib.sha256(measurement_key.encode()).digest()
    return 0.05 + (int.from_bytes(digest[:4], "big") % 90_000) / 100_000.0


def _status() -> Status:
    """The verdict a fake measurement passes with: it is a claim-free L0 record."""
    return Status(
        gate_verdict=GateVerdict.PASS_,
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


def synthetic_record(
    coordinate: Coordinate,
    schedule: Schedule,
    provenance: Provenance,
    *,
    run_id: str | None = None,
    walltime_s: float = SYNTHETIC_WALLTIME_S,
) -> Record:
    """A record for one measured seed, carrying the metrics a claim reads.

    Args:
        coordinate: The measured cell.
        schedule: The seed's own schedule (records are keyed per seed).
        provenance: The run's provenance.
        run_id: Overrides the run id the provenance links to.
        walltime_s: The synthetic cost the budget charge consumes.

    Returns:
        A pass-eligible record whose payload carries every measured metric.
    """
    measurement_key = coordinate.measurement_key(schedule)
    metric = _pseudo_metric(measurement_key)
    return Record.create(
        run_id=run_id or str(provenance.links.get("run_id", "")),
        coordinate=coordinate,
        schedule=schedule,
        provenance=provenance,
        status=_status(),
        payload={
            "status": "evaluated",
            "train_acc": metric,
            "val_acc": metric,
            "walltime_s": walltime_s,
            "param_count": 1024,
            "seed": schedule.seed,
            "fidelity": schedule.fidelity,
            "task_id": schedule.task_id,
            "epochs_completed": schedule.epochs,
            "epochs_requested": schedule.epochs,
            "params": dict(coordinate.params),
            "param_budget": schedule.param_budget,
        },
    )


class FakeBackend:
    """Records without training, and a rejection the caller asks for by name.

    Args:
        rejects: Returns a failure message for a cell, or ``None`` to measure
            it. This is how the round loop's failure-isolation path is reached
            without an illegal configuration.
        walltime_s: Synthetic seconds per record, consumed by the budget
            charge; a caller asserting the charge picks this.
    """

    def __init__(
        self,
        *,
        rejects: Rejection | None = None,
        walltime_s: float = SYNTHETIC_WALLTIME_S,
    ) -> None:
        self._rejects = rejects
        self._walltime_s = walltime_s
        self.submitted: list[str] = []
        self._shutdown = False

    async def submit(
        self,
        coordinate: Coordinate,
        schedule: Schedule,
        provenance: Provenance,
        params: dict[str, object],
        store: RecordStore,
    ) -> list[Record]:
        """One record per planned seed, unless this cell is declared a failure."""
        _ = (params, store)
        message = None if self._rejects is None else self._rejects(coordinate, schedule)
        if message is not None:
            msg = message
            raise RuntimeError(msg)
        return [
            synthetic_record(
                coordinate,
                seed_schedule,
                provenance,
                walltime_s=self._walltime_s,
            )
            for seed_schedule in schedule.seed_plan
        ]

    async def submit_batch(
        self,
        items: list[tuple[Coordinate, Schedule, Provenance, dict[str, object]]],
        store: RecordStore,
    ) -> list[EvaluationResult]:
        """Per-item isolation, the same contract ``_ThreadedBackend`` implements."""
        results: list[EvaluationResult] = []
        for coordinate, schedule, provenance, params in items:
            try:
                records = await self.submit(
                    coordinate, schedule, provenance, params, store
                )
            except Exception as exc:
                results.append(Failure(failure_event=self._failure(coordinate, exc)))
            else:
                self.submitted.extend(record.measurement_key for record in records)
                results.append(Success(records=tuple(records)))
        return results

    def _failure(self, coordinate: Coordinate, exc: Exception) -> FailureEvent:
        return FailureEvent(
            cell_key=coordinate.cell_key(),
            failure_cause=FailureCause.INVALID_CONFIG,
            error_message=str(exc),
            coordinate=coordinate.to_dict(),
            schedule={},
            provenance={},
        )

    def shutdown(self) -> None:
        """Release the backend; it holds nothing that needs releasing."""
        self._shutdown = True


__all__ = ["FakeBackend", "synthetic_record"]
