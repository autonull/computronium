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

import torch

from computronium.core.logging import get_logger
from computronium.core.system_trainer import (
    DistributedSystemTrainer,
    SystemTrainer,
    SystemTrainerConfig,
)
from computronium.domains.base import TaskSplit
from computronium.experiment.kernel._metrics import (
    compute_energy_metrics,
    compute_plasticity_metrics,
    compute_stability_metrics,
    history_metrics,
)
from computronium.experiment.kernel._task_scheduler import TaskScheduler
from computronium.experiment.kernel._trainer_utils import (
    _bounded_batches,
    _create_trainer_config,
    _run_training,
    _sample_inputs,
    _setup_checkpointing,
    _val_batches,
)
from computronium.experiment.kernel.compose import (
    ComposedCell,
    compose_cell_system,
)
from computronium.experiment.schema.metrics import HISTORY_METRICS
from computronium.experiment.schema.registries import (
    ASSESSMENT_PROCEDURE_VERSION,
    PARAM_BUDGET_TOLERANCE,
)
from computronium.ontology.substrate._substrate import SubstrateConfig
from computronium.ontology.substrate.spec import (
    SubstrateSpec,
    compute_substrate_objectives,
)

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping

    from computronium.experiment.schema.coordinate import (
        Coordinate,
        Provenance,
        Schedule,
    )
    from computronium.experiment.schema.record import Record, Status

__all__ = [
    "CellEvaluation",
    "TaskScheduler",
    "TaskShape",
    "cell_record",
    "compute_energy_metrics",
    "compute_stability_metrics",
    "evaluate_cell",
    "history_metrics",
    "task_shape",
]

# An exact Jacobian costs d backward passes and an O(d^3) eigen-decomposition.
# Measured on CUDA at the campaign's widest cell (hidden 256 x 5 layers, d=1536):
# 2.6s to build, 0.4s to factor — 3% of the cell it describes, so the cap sits
# above the declared space rather than truncating it. A cap, not a silent
# wrong number: past it the settle telemetry is reported without a Jacobian.
_MAX_JACOBIAN_WIDTH: Final[int] = 1536

logger = get_logger(__name__)

# Tasks are reused within a process: setup costs ~1s, and a campaign evaluates
# hundreds of cells against a handful of tasks. The lock is required under
# free-threaded CPython — several workers ask for the same task at once.
_TASK_CACHE: dict[tuple[str, str, int], Any] = {}
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
    checkpoint_path: str | None = None
    convergence_curve: list[dict[str, float]] | None = None


def _task(task_id: str, device: str, num_workers: int = 0) -> Any:
    """The set-up task, cached per (task, device, num_workers)."""
    from computronium.domains.factory import create_task

    resolved_device = _resolve_device(device)
    key = (task_id, resolved_device, num_workers)
    with _TASK_LOCK:
        cached = _TASK_CACHE.get(key)
    if cached is not None:
        return cached
    task = create_task(
        task_id, device=resolved_device, quick_mode=True, num_workers=num_workers
    )
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


def evaluate_cell(  # ruff: ignore[complex-structure, too-many-statements, too-many-locals, too-many-branches]
    coordinate: Coordinate,
    schedule: Schedule,
    geometry: Mapping[str, Any] | None = None,
    checkpoint_dir: str | None = None,
    resume_checkpoint_path: str | None = None,
    params: Mapping[str, Any] | None = None,
) -> CellEvaluation:
    """Train one coordinate on the schedule's task and measure it.

    Args:
        coordinate: The six-axis selection and its hyperparameters.
        schedule: Epochs, seed, batch limit, task identity, and device.
        geometry: Topology overrides for the geometry axis.
        checkpoint_dir: Optional directory to save checkpoints. If provided and
            schedule.checkpoint_every_n > 0, checkpoints are saved here.
        params: Optional experiment parameters, may include deadline_check callback.

    Returns:
        CellEvaluation carrying the measured metrics and the effective
        hyperparameters the composed config actually held (R6).

    Raises:
        EvaluationError: The task, the composition, or the training run failed.
    """

    # Resolve device and set seeds
    import os
    import random

    import numpy as np
    import torch

    resolved_device = _resolve_device(schedule.device)

    _set_seeds(schedule.seed, schedule.deterministic)

    task = _task(schedule.task_id, schedule.device, schedule.num_workers)
    shape = _task_shape(task)

    cell = compose_cell_system(
        coordinate=coordinate,
        geometry=dict(geometry or {}),
        input_shape=shape.input_shape,
        output_dim=shape.output_dim,
        param_budget=schedule.param_budget,
        task=task,
    )

    config = _create_trainer_config(schedule, resolved_device, params)

    # Choose trainer class based on distributed backend
    trainer_class = _choose_trainer_class(schedule)

    # Set up checkpointing
    temp_dir, checkpoint_path_ref, checkpoint_callback = _setup_checkpointing(
        schedule, checkpoint_dir, config
    )

    start = time.monotonic()
    trainer, history = _run_training(
        trainer_class, cell, task, config, resume_checkpoint_path, checkpoint_callback
    )
    walltime_s = time.monotonic() - start

    # Clean up temp dir after training
    if temp_dir is not None:
        temp_dir.cleanup()

    metrics = _collect_all_metrics(trainer, history, cell, task, schedule, coordinate)

    # Ensure system geometry is on the correct device for metrics computation
    # (trainer.close() moves geometry to CPU)
    device = _resolve_device(config.device)
    if hasattr(cell.system.geometry, "to"):
        cell.system.geometry.to(device)

    sample_x = _sample_inputs(task, config.device)
    metrics.update(compute_stability_metrics(cell.system, sample_x))
    metrics.update(compute_energy_metrics(cell.system, batch_size=sample_x.shape[0]))

    # Substrate-specific objectives
    metrics.update(_compute_substrate_objectives(coordinate, metrics, walltime_s))

    # Plasticity objectives
    metrics.update(compute_plasticity_metrics(cell.system))

    # Domain-specific evaluation (perplexity, f1_score, bleu_score, mean_reward, etc.)
    # Use the task's own evaluate() method which knows the proper metrics for its domain.
    _update_task_metrics(task, metrics, cell, schedule, coordinate)

    # Derived metric: energy_efficiency = validation_accuracy / energy_per_sample
    _add_energy_efficiency(metrics)

    _validate_metrics_finite(metrics, coordinate)

    convergence_curve = _extract_convergence_curve(schedule, history)

    return CellEvaluation(
        metrics=metrics,
        params=dict(cell.params),
        param_count=cell.param_count,
        walltime_s=walltime_s,
        epochs_completed=len(history),
        task_id=schedule.task_id,
        checkpoint_path=checkpoint_path_ref[0],
        convergence_curve=convergence_curve,
    )


def _set_seeds(seed: int, deterministic: bool) -> None:
    """Set all random seeds for reproducibility."""
    import os
    import random

    import numpy as np
    import torch

    torch.manual_seed(seed)
    if deterministic:
        os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
        torch.use_deterministic_algorithms(True)
    np.random.seed(seed)
    random.seed(seed)


def _choose_trainer_class(schedule: Schedule):
    """Choose trainer class based on distributed backend."""
    return (
        DistributedSystemTrainer
        if schedule.distributed_backend != "none"
        else SystemTrainer
    )


def _collect_all_metrics(
    trainer: SystemTrainer,
    history: list[dict[str, float]],
    cell: ComposedCell,
    task: Any,
    schedule: Schedule,
    coordinate: Coordinate,
) -> dict[str, float]:
    """Collect all metrics from history, trainer, and substrate."""
    metrics = history_metrics(history)
    metrics.update(_collect_trainer_metrics(trainer))
    return metrics


def _update_task_metrics(
    task: Any,
    metrics: dict[str, float],
    cell: ComposedCell,
    schedule: Schedule,
    coordinate: Coordinate,
) -> None:
    """Update metrics with task-specific evaluation."""
    try:
        task_metrics = task.evaluate(
            cell.system.geometry, split=TaskSplit.VAL, max_batches=schedule.batch_limit
        )
        metrics.update(task_metrics.to_dict())
    except Exception as exc:  # ruff: ignore[blind-except] - evaluation must not fail the cell
        logger.warning(
            "task.evaluate() failed for %s: %s | coordinate=%s | geometry=%s | substrate=%s | dynamics=%s | credit=%s | update=%s | plasticity=%s",
            schedule.task_id,
            exc,
            coordinate.cell_key()[:12],
            coordinate.geometry,
            coordinate.substrate,
            coordinate.dynamics,
            coordinate.credit,
            coordinate.update,
            coordinate.plasticity,
            exc_info=True,
        )


def _add_energy_efficiency(metrics: dict[str, float]) -> None:
    """Add derived energy_efficiency metric if components exist."""
    val_acc = metrics.get("val_acc")
    energy_per_sample = metrics.get("energy_per_sample")
    if val_acc is not None and energy_per_sample is not None and energy_per_sample > 0:
        metrics["energy_efficiency"] = float(val_acc) / float(energy_per_sample)


def _validate_metrics_finite(metrics: dict[str, float], coordinate: Coordinate) -> None:
    """Validate all metrics are finite."""
    import math
    if not all(math.isfinite(v) for v in metrics.values()):
        msg = f"non-finite metrics {sorted(metrics)} for {coordinate.cell_key()[:12]}"
        raise EvaluationError("numerical", msg)


def _compute_substrate_objectives(
    coordinate: Coordinate,
    metrics: dict[str, float],
    walltime_s: float,
) -> dict[str, float]:
    """Compute substrate-specific objectives."""

    name_lower = coordinate.substrate.lower()
    factory_map = {
        "digital": SubstrateConfig.digital,
        "analog": SubstrateConfig.analog,
        "memristive": SubstrateConfig.memristive,
        "neuromorphic": SubstrateConfig.neuromorphic,
        "optical": SubstrateConfig.optical,
        "quantum": SubstrateConfig.quantum,
        "sparse": SubstrateConfig.sparse,
        "ternary": SubstrateConfig.ternary,
        "complex": SubstrateConfig.complex,
    }
    factory = factory_map.get(name_lower, SubstrateConfig.digital)
    dynamics_name = coordinate.dynamics
    if dynamics_name in {"diffusion", "spike_integration", "pc_alm"}:
        substrate_config = factory(noise_level=0.05)
    else:
        substrate_config = factory()
    substrate_spec = SubstrateSpec.from_config(substrate_config)
    settle_telemetry = {
        "energy_per_step": metrics.get("energy_per_step", 0.0),
        "settle_steps_used": metrics.get("settle_steps", 0),
        "free_energy_final": metrics.get(
            "hopfield_energy", metrics.get("free_energy", 0.0)
        ),
        "spike_rate": metrics.get("spike_rate", 0.0),
        "event_density": metrics.get("event_density", 0.0),
    }
    runtime_stats = {
        "walltime_s": walltime_s,
        "memory_mb": metrics.get("memory_usage", 0.0),
        "flops": metrics.get("flops", 0.0),
        "latency_ms": metrics.get("latency_ms", 0.0),
    }
    substrate_objectives = compute_substrate_objectives(
        substrate_spec, settle_telemetry, runtime_stats
    )
    return substrate_objectives


def _extract_convergence_curve(
    schedule: Schedule, history: list[dict[str, float]]
) -> list[dict[str, float]] | None:
    """Extract convergence curve for L1/L2 fidelity."""
    if schedule.fidelity not in {"L1", "L2", "L3"} or not history:
        return None
    curve_keys = {"train_loss", "val_loss", "train_acc", "val_acc", "learning_rate"}
    return [
        {
            **{k: float(v) for k, v in epoch.items() if k in curve_keys},
            "epoch": i + 1,
        }
        for i, epoch in enumerate(history)
    ]


def _collect_trainer_metrics(trainer: SystemTrainer) -> dict[str, float]:
    """Extract resource metrics from trainer's last epoch."""
    if not trainer.epoch_resources:
        return {}
    return _trainer_epoch_to_metrics(trainer.epoch_resources[-1])


def _trainer_epoch_to_metrics(epoch) -> dict[str, float]:
    """Convert a single epoch's resource data to metrics dict."""
    metrics: dict[str, float] = {}
    if epoch.forward_flops is not None and epoch.steps > 0:
        flops_per_step = epoch.forward_flops / epoch.steps
        metrics["flops"] = float(flops_per_step)
        metrics["macs_per_step"] = float(flops_per_step / 2)  # 1 MAC = 2 FLOPs
    if epoch.peak_memory_mb is not None:
        metrics["memory_usage"] = epoch.peak_memory_mb
    if epoch.steps > 0:
        metrics["latency_ms"] = (epoch.epoch_time_s / epoch.steps) * 1000.0
    if epoch.energy_joules is not None and epoch.steps > 0:
        metrics["energy_per_step"] = epoch.energy_joules / epoch.steps
    return metrics


def _determine_procedure_metadata() -> tuple[str, str, str]:
    """Extract procedure name, version, and code_hash from assessment procedures."""
    from computronium.experiment.evidence.procedures import (
        ASSESSMENT_PROCEDURES,
        get_assessment_procedure,
    )

    gate_verdict_proc = get_assessment_procedure(
        "gate_verdict", "1.0"
    ) or ASSESSMENT_PROCEDURES.get(
        "gate_verdict@1.0#" + "gate_verdict"[:8]  # Fallback key
    )

    if gate_verdict_proc is None:
        return "gate_verdict", "1.0", "default"
    return (
        gate_verdict_proc.name.split("@")[0],
        gate_verdict_proc.version,
        gate_verdict_proc.code_hash,
    )


def _build_status_with_procedures(
    passed: bool,
    complete: bool,
    within_ceiling: bool,
    param_count: int,
    param_budget: int,
) -> Status:
    """Build schema Status with assessment procedure metadata (WP5)."""
    from computronium.experiment.evidence.status import (
        StatusLegacy,
        build_assessments_from_legacy,
    )
    from computronium.experiment.schema.record import (
        FailureCause,
        GateVerdict,
        Maturity,
        ReproducibilityClass,
        Severity,
        Status,
    )

    procedure_name, procedure_version, procedure_code_hash = (
        _determine_procedure_metadata()
    )
    legacy_status = StatusLegacy(
        gate_verdict=GateVerdict.PASS_ if passed else GateVerdict.FAIL,
        defect=_defect(complete, within_ceiling, param_count, param_budget),
        cause=FailureCause.UNKNOWN if passed else FailureCause.CONSTRAINT_VIOLATION,
        severity=Severity.LOW if passed else Severity.MEDIUM,
        quarantine=not passed,
        maturity=Maturity.L0,
        uncertainty={},
        reproducibility=ReproducibilityClass.REPLAYABLE,
        assessment_procedure_version=procedure_version,
        ceec_link=None,
    )

    assessments = build_assessments_from_legacy(
        legacy_status,
        procedure_name=procedure_name,
        procedure_version=procedure_version,
        procedure_code_hash=procedure_code_hash,
    )

    return Status(
        gate_verdict=assessments.gate_verdict,
        defect=assessments.defect,
        cause=assessments.failure_classification,
        severity=assessments.severity,
        quarantine=assessments.quarantine,
        maturity=assessments.maturity,
        uncertainty=assessments.uncertainty,
        reproducibility=assessments.reproducibility,
        assessment_procedure_version=assessments.procedure_version,
        ceec_link=assessments.ceec_link,
    )


def cell_record(
    coordinate: Coordinate,
    schedule: Schedule,
    provenance: Provenance,
    geometry: Mapping[str, Any] | None = None,
    checkpoint_dir: str | None = None,
    resume_checkpoint_path: str | None = None,
    params: Mapping[str, Any] | None = None,
) -> Record:
    """Evaluate one cell and wrap the measurement in a Record.

    The gate verdict is derived from what happened — the requested epochs ran
    and the metrics are finite — rather than stamped PENDING as the placeholder
    did.

    Assessment procedures are run to stamp procedure metadata (name, version, code_hash)
    into the record's status, implementing the three-tier evidence model (WP5).
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
        evaluation = evaluate_cell(
            coordinate,
            schedule,
            geometry,
            checkpoint_dir,
            resume_checkpoint_path,
            params,
        )
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
    if evaluation.checkpoint_path:
        payload["checkpoint_path"] = evaluation.checkpoint_path
    if evaluation.convergence_curve:
        payload["convergence_curve"] = evaluation.convergence_curve
    passed = complete and within_ceiling

    # Build legacy status and convert to schema Status with procedure metadata
    status = _build_status_with_procedures(
        passed,
        complete,
        within_ceiling,
        evaluation.param_count,
        schedule.param_budget,
    )

    return Record.create(
        run_id=provenance.links.get("run_id", str(uuid.uuid4())),
        coordinate=coordinate,
        schedule=schedule,
        provenance=provenance,
        status=status,
        payload=payload,
        effective_params=dict(evaluation.params),
    )


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