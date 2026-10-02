"""Real cell evaluation: coordinate + schedule + task → trained system metrics.

The kernel's only evaluator. ``LocalBackend`` and ``MultiprocessBackend`` both
delegate here, because two implementations of "evaluate" is how the placeholder
evaluator came to exist (TODO46 §D1).

Shape comes from the task, never from a default: ``resolve_task`` builds the
concrete ``DomainTask`` and reads its own ``input_dim``/``output_dim``.
"""

from __future__ import annotations

import math
import threading
import time
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Final

from computronium.core.logging import get_logger
from computronium.core.system_trainer import SystemTrainer, SystemTrainerConfig
from computronium.experiment.execution.compose import compose_cell_system

if TYPE_CHECKING:
    from collections.abc import Mapping

    from computronium.experiment.schema.coordinate import (
        Coordinate,
        Provenance,
        Schedule,
    )
    from computronium.experiment.schema.record import Record

__all__ = ["CellEvaluation", "cell_record", "evaluate_cell", "task_shape"]

logger = get_logger(__name__)

# Tasks are reused within a process: setup costs ~1s, and a campaign evaluates
# hundreds of cells against a handful of tasks. The lock is required under
# free-threaded CPython — several workers ask for the same task at once.
_TASK_CACHE: dict[tuple[str, str], Any] = {}
_TASK_LOCK: Final[threading.Lock] = threading.Lock()


class EvaluationError(RuntimeError):
    """A cell could not be evaluated. Carries the taxonomy code."""

    def __init__(self, cause: str, message: str) -> None:
        self.cause = cause
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class CellEvaluation:
    """One trained cell: what it measured and what it was actually given."""

    metrics: Mapping[str, float]
    params: Mapping[str, Any]
    walltime_s: float
    epochs_completed: int
    task_id: str


def _task(task_id: str, device: str) -> Any:
    """The set-up task, cached per (task, device)."""
    from computronium.domains.factory import create_task

    key = (task_id, device)
    with _TASK_LOCK:
        cached = _TASK_CACHE.get(key)
    if cached is not None:
        return cached
    task = create_task(task_id, device=device, quick_mode=True, num_workers=0)
    task.setup()
    with _TASK_LOCK:
        _TASK_CACHE.setdefault(key, task)
        return _TASK_CACHE[key]


def _flat_input_dim(task: Any) -> int:
    """The task's flattened input width — ``(1, 8, 8)`` becomes 64."""
    shape = task.input_dim
    if shape is None:
        msg = f"task {task.name!r} declares no input_dim"
        raise EvaluationError("invalid_config", msg)
    return (
        int(math.prod(int(d) for d in shape))
        if isinstance(shape, tuple | list)
        else int(shape)
    )


def task_shape(task_id: str, device: str = "cpu") -> tuple[int, int]:
    """The ``(input_dim, output_dim)`` a task will be trained at.

    The search space asks the evaluator for this rather than composing against
    a guessed shape: shape is a property of the task, and the space must
    filter cells with the same shape the evaluator will use.
    """
    task = _task(task_id, device)
    return _flat_input_dim(task), int(task.output_dim)


def _history_metrics(history: list[dict[str, float]]) -> dict[str, float]:
    """Final-epoch observations, flattened to the metric namespace."""
    if not history:
        msg = "training produced no epochs"
        raise EvaluationError("runtime_error", msg)
    final = history[-1]
    metrics = {
        key: float(value)
        for key, value in final.items()
        if key in {"train_acc", "train_loss", "train_energy", "val_acc", "val_loss"}
    }
    metrics["epochs_run"] = float(final.get("global_step", 0))
    return metrics


def _finite(metrics: Mapping[str, float]) -> bool:
    return all(math.isfinite(v) for v in metrics.values())


def evaluate_cell(
    coordinate: Coordinate,
    schedule: Schedule,
    geometry: Mapping[str, Any] | None = None,
    *,
    device: str = "auto",
) -> CellEvaluation:
    """Train one coordinate on the schedule's task and measure it.

    Args:
        coordinate: The six-axis selection and its hyperparameters.
        schedule: Epochs, seed, batch limit and task identity.
        geometry: Topology overrides for the geometry axis.
        device: ``"auto"`` prefers CUDA when present.

    Returns:
        CellEvaluation carrying the measured metrics and the effective
        hyperparameters the composed config actually held (R6).

    Raises:
        EvaluationError: The task, the composition, or the training run failed.
    """
    import torch

    task = _task(schedule.task_id, "cpu")
    input_dim = _flat_input_dim(task)
    output_dim = int(task.output_dim)

    cell = compose_cell_system(
        coordinate=coordinate,
        geometry=dict(geometry or {}),
        input_dim=input_dim,
        output_dim=output_dim,
    )

    config = SystemTrainerConfig(
        max_epochs=schedule.epochs,
        device=device,
        seed=schedule.seed,
        limit_train_batches=schedule.batch_limit or None,
        track_flops=False,
        track_memory=False,
    )
    torch.manual_seed(schedule.seed)

    start = time.monotonic()
    try:
        with SystemTrainer(
            cell.system, config, task.get_dataloader("train")
        ) as trainer:
            history = trainer.fit()
    except EvaluationError:
        raise
    except Exception as exc:
        msg = f"{coordinate.dynamics}/{coordinate.credit} on {schedule.task_id}: {exc}"
        raise EvaluationError("runtime_error", msg) from exc
    walltime_s = time.monotonic() - start

    metrics = _history_metrics(history)
    if not _finite(metrics):
        msg = f"non-finite metrics {sorted(metrics)} for {coordinate.cell_key()[:12]}"
        raise EvaluationError("numerical", msg)

    return CellEvaluation(
        metrics=metrics,
        params=dict(cell.params),
        walltime_s=walltime_s,
        epochs_completed=len(history),
        task_id=schedule.task_id,
    )


def cell_record(
    coordinate: Coordinate,
    schedule: Schedule,
    provenance: Provenance,
    geometry: Mapping[str, Any] | None = None,
    *,
    device: str = "auto",
) -> Record:
    """Evaluate one cell and wrap the measurement in a Record.

    The gate verdict is derived from what happened — the requested epochs ran
    and the metrics are finite — rather than stamped PENDING as the placeholder
    did.
    """
    from computronium.experiment.schema.record import (
        FailureCause,
        GateVerdict,
        Maturity,
        Record,
        ReproducibilityClass,
        Severity,
        Status,
    )

    try:
        evaluation = evaluate_cell(coordinate, schedule, geometry, device=device)
    except EvaluationError as exc:
        cause = FailureCause(exc.cause)
        return Record.create(
            run_id=provenance.links.get("run_id", str(uuid.uuid4())),
            coordinate=coordinate,
            schedule=schedule,
            provenance=provenance,
            status=Status(
                gate_verdict=GateVerdict.FAIL,
                defect=str(exc),
                cause=cause,
                severity=Severity.HIGH,
                quarantine=True,
                maturity=Maturity.L0,
                uncertainty={},
                reproducibility=ReproducibilityClass.REPLAYABLE,
                assessment_procedure_version="1.0",
                ceec_link=None,
            ),
            payload={"status": "failed", "cause": exc.cause, "error": str(exc)},
        )

    complete = evaluation.epochs_completed >= schedule.epochs
    payload: dict[str, Any] = {
        "status": "evaluated",
        **evaluation.metrics,
        "walltime_s": evaluation.walltime_s,
        "epochs_completed": evaluation.epochs_completed,
        "epochs_requested": schedule.epochs,
        "seed": schedule.seed,
        "fidelity": schedule.fidelity,
        "task_id": evaluation.task_id,
        "params": dict(evaluation.params),
    }
    return Record.create(
        run_id=provenance.links.get("run_id", str(uuid.uuid4())),
        coordinate=coordinate,
        schedule=schedule,
        provenance=provenance,
        status=Status(
            gate_verdict=GateVerdict.PASS_ if complete else GateVerdict.FAIL,
            defect="" if complete else "training stopped before the requested epochs",
            cause=FailureCause.UNKNOWN if complete else FailureCause.TIMEOUT,
            severity=Severity.LOW if complete else Severity.MEDIUM,
            quarantine=not complete,
            maturity=Maturity.L0,
            uncertainty={},
            reproducibility=ReproducibilityClass.REPLAYABLE,
            assessment_procedure_version="1.0",
            ceec_link=None,
        ),
        payload=payload,
    )
