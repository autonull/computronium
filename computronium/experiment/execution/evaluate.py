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
from itertools import islice
from typing import TYPE_CHECKING, Any, Final

import torch

from computronium.core.logging import get_logger
from computronium.core.system_trainer import SystemTrainer, SystemTrainerConfig
from computronium.experiment.execution.compose import compose_cell_system
from computronium.experiment.schema.metrics import HISTORY_METRICS
from computronium.experiment.schema.registries import (
    ASSESSMENT_PROCEDURE_VERSION,
    PARAM_BUDGET_TOLERANCE,
)

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping

    from computronium.experiment.schema.coordinate import (
        Coordinate,
        Provenance,
        Schedule,
    )
    from computronium.experiment.schema.record import Record

__all__ = [
    "CellEvaluation",
    "TaskShape",
    "cell_record",
    "evaluate_cell",
    "history_metrics",
    "task_shape",
]

logger = get_logger(__name__)

# Tasks are reused within a process: setup costs ~1s, and a campaign evaluates
# hundreds of cells against a handful of tasks. The lock is required under
# free-threaded CPython — several workers ask for the same task at once.
_TASK_CACHE: dict[tuple[str, str], Any] = {}
_TASK_LOCK: Final[threading.Lock] = threading.Lock()


def _resolve_device(device: str) -> str:
    """Resolve 'auto' to 'cuda' if available, otherwise 'cpu'."""
    if device == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return device


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
    param_count: int
    walltime_s: float
    epochs_completed: int
    task_id: str


def _task(task_id: str, device: str) -> Any:
    """The set-up task, cached per (task, device)."""
    from computronium.domains.factory import create_task

    resolved_device = _resolve_device(device)
    key = (task_id, resolved_device)
    with _TASK_LOCK:
        cached = _TASK_CACHE.get(key)
    if cached is not None:
        return cached
    task = create_task(task_id, device=resolved_device, quick_mode=True, num_workers=0)
    task.setup()
    with _TASK_LOCK:
        _TASK_CACHE.setdefault(key, task)
        return _TASK_CACHE[key]


@dataclass(frozen=True, slots=True)
class TaskShape:
    """What a task will be trained at: its own input shape and its class count.

    The shape is carried whole rather than flattened, because a topology that
    consumes space (a conv stack wants channels and a grid, an NCA wants a
    grid) must be given the task's real extent instead of a guessed one.
    """

    input_shape: tuple[int, ...]
    output_dim: int

    @property
    def input_dim(self) -> int:
        """Flattened input width — ``(1, 8, 8)`` becomes 64."""
        return math.prod(self.input_shape)


def _task_shape(task: Any) -> TaskShape:
    declared = task.input_dim
    if declared is None:
        msg = f"task {task.name!r} declares no input_dim"
        raise EvaluationError("invalid_config", msg)
    shape = (
        tuple(int(d) for d in declared)
        if isinstance(declared, tuple | list)
        else (int(declared),)
    )
    return TaskShape(input_shape=shape, output_dim=int(task.output_dim))


def task_shape(task_id: str, device: str = "auto") -> TaskShape:
    """The shape a task will be trained at.

    The search space asks the evaluator for this rather than composing against
    a guessed shape: shape is a property of the task, and the space must
    filter cells with the same shape the evaluator will use.
    """
    return _task_shape(_task(task_id, device))


def history_metrics(history: list[dict[str, float]]) -> dict[str, float]:
    """Final-epoch observations, flattened to the metric namespace.

    The kernel-owned history→metrics extraction. The lab's certificates path
    consumes this rather than re-implementing the filter (TODO47 T6): two
    extractions is how the fallback chain hid dead keys from itself.
    """
    if not history:
        msg = "training produced no epochs"
        raise EvaluationError("runtime_error", msg)
    final = history[-1]
    metrics = {
        key: float(value) for key, value in final.items() if key in HISTORY_METRICS
    }
    metrics["epochs_run"] = float(final.get("global_step", 0))
    return metrics


def _within_ceiling(param_count: int, param_budget: int) -> bool:
    """Whether a cell honoured the parameter ceiling its schedule declared.

    The tolerance is R25's registered one, read from the same declaration as
    the ``param_budget_fairness`` predicate, so a cell the constraint accepts is
    a cell the gate passes.
    """
    if param_budget <= 0:
        return True
    return param_count <= param_budget * (1 + PARAM_BUDGET_TOLERANCE)


def _defect(
    complete: bool, within_ceiling: bool, param_count: int, param_budget: int
) -> str:
    match (complete, within_ceiling):
        case (True, True):
            return ""
        case (False, True):
            return "training stopped before the requested epochs"
        case (True, False):
            return (
                f"{param_count} parameters exceeds the declared ceiling {param_budget}"
            )
        case _:
            return (
                "training stopped before the requested epochs; "
                f"{param_count} parameters exceeds the declared ceiling {param_budget}"
            )


def _finite(metrics: Mapping[str, float]) -> bool:
    return all(math.isfinite(v) for v in metrics.values())


class _Batches:
    """A bounded view of a data provider: ``batch_limit`` batches, then stop.

    Validation is charged at the same ceiling as training. An unbounded
    validation pass would make a 2-batch cell cost 45 batch-forwards, which is
    how one honest measurement turned a 9-minute acceptance suite into a
    25-minute one.
    """

    __slots__ = ("_limit", "_source")

    def __init__(self, source: Any, limit: int) -> None:
        self._source = source
        self._limit = limit

    def __iter__(self) -> Iterator[Any]:
        return islice(iter(self._source), self._limit)

    def __len__(self) -> int:
        return min(self._limit, len(self._source))


def _val_batches(task: Any, limit: int | None) -> Any | None:
    """The task's validation split, bounded, or ``None`` when it declares none.

    Without it the evaluator can only report what the cell fit, and
    ``validation_accuracy`` — the primary objective of every profile — would be
    a name with no number behind it.
    """
    from computronium.domains.base import TaskSplit

    try:
        loader = task.get_dataloader(TaskSplit.VAL)
    except (LookupError, ValueError, NotImplementedError) as exc:
        logger.info("task %s declares no validation split: %s", task.name, exc)
        return None
    return _Batches(loader, limit) if limit else loader


def evaluate_cell(
    coordinate: Coordinate,
    schedule: Schedule,
    geometry: Mapping[str, Any] | None = None,
) -> CellEvaluation:
    """Train one coordinate on the schedule's task and measure it.

    Args:
        coordinate: The six-axis selection and its hyperparameters.
        schedule: Epochs, seed, batch limit, task identity, and device.
        geometry: Topology overrides for the geometry axis.

    Returns:
        CellEvaluation carrying the measured metrics and the effective
        hyperparameters the composed config actually held (R6).

    Raises:
        EvaluationError: The task, the composition, or the training run failed.
    """
    import torch

    task = _task(schedule.task_id, schedule.device)
    shape = _task_shape(task)

    cell = compose_cell_system(
        coordinate=coordinate,
        geometry=dict(geometry or {}),
        input_shape=shape.input_shape,
        output_dim=shape.output_dim,
        param_budget=schedule.param_budget,
    )

    limit = schedule.batch_limit or None
    config = SystemTrainerConfig(
        max_epochs=schedule.epochs,
        device=schedule.device,
        seed=schedule.seed,
        limit_train_batches=limit,
        limit_val_batches=limit,
        track_flops=False,
        track_memory=False,
    )
    torch.manual_seed(schedule.seed)

    start = time.monotonic()
    try:
        with SystemTrainer(
            cell.system,
            config,
            task.get_dataloader("train"),
            val_data=_val_batches(task, config.limit_val_batches),
        ) as trainer:
            history = trainer.fit()
    except EvaluationError:
        raise
    except Exception as exc:
        msg = f"{coordinate.dynamics}/{coordinate.credit} on {schedule.task_id}: {exc}"
        raise EvaluationError("runtime_error", msg) from exc
    walltime_s = time.monotonic() - start

    metrics = history_metrics(history)
    if not _finite(metrics):
        msg = f"non-finite metrics {sorted(metrics)} for {coordinate.cell_key()[:12]}"
        raise EvaluationError("numerical", msg)

    return CellEvaluation(
        metrics=metrics,
        params=dict(cell.params),
        param_count=cell.param_count,
        walltime_s=walltime_s,
        epochs_completed=len(history),
        task_id=schedule.task_id,
    )


def cell_record(
    coordinate: Coordinate,
    schedule: Schedule,
    provenance: Provenance,
    geometry: Mapping[str, Any] | None = None,
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
        evaluation = evaluate_cell(coordinate, schedule, geometry)
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
                assessment_procedure_version=ASSESSMENT_PROCEDURE_VERSION,
                ceec_link=None,
            ),
            payload={"status": "failed", "cause": exc.cause, "error": str(exc)},
        )

    complete = evaluation.epochs_completed >= schedule.epochs
    within_ceiling = _within_ceiling(evaluation.param_count, schedule.param_budget)
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
        "param_count": evaluation.param_count,
        "param_budget": schedule.param_budget,
    }
    passed = complete and within_ceiling
    return Record.create(
        run_id=provenance.links.get("run_id", str(uuid.uuid4())),
        coordinate=coordinate,
        schedule=schedule,
        provenance=provenance,
        status=Status(
            gate_verdict=GateVerdict.PASS_ if passed else GateVerdict.FAIL,
            defect=_defect(
                complete, within_ceiling, evaluation.param_count, schedule.param_budget
            ),
            cause=FailureCause.UNKNOWN if passed else FailureCause.CONSTRAINT_VIOLATION,
            severity=Severity.LOW if passed else Severity.MEDIUM,
            quarantine=not passed,
            maturity=Maturity.L0,
            uncertainty={},
            reproducibility=ReproducibilityClass.REPLAYABLE,
            assessment_procedure_version=ASSESSMENT_PROCEDURE_VERSION,
            ceec_link=None,
        ),
        payload=payload,
        effective_params=dict(evaluation.params),
    )
