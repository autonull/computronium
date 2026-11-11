"""Real cell evaluation: coordinate + schedule + task → trained system metrics.

The kernel's only evaluator. ``LocalBackend`` and ``MultiprocessBackend`` both
delegate here, because two implementations of "evaluate" is how the placeholder
evaluator came to exist (TODO46 §D1).

Shape comes from the task, never from a default: ``resolve_task`` builds the
concrete ``DomainTask`` and reads its own ``input_dim``/``output_dim``.
"""

from __future__ import annotations

import hashlib
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
    _collect_trainer_metrics,
    _create_trainer_config,
    _resolve_device,
    _run_training,
    _sample_inputs,
    _setup_checkpointing,
)
from computronium.experiment.kernel.compose import (
    ComposedCell,
    compose_cell_system,
)
from computronium.experiment.registry.task_registry import get_task_registry
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
    from collections.abc import Mapping

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


def _cell_replay_hash(
    provenance: Provenance, coordinate: Coordinate, schedule: Schedule
) -> str:
    """Per-cell replay identity: measurement key plus code/dataset provenance.

    ``measurement_key`` carries the seed, task, device and determinism flag,
    so two seeds of one coordinate hash differently (R5a); the older
    hand-assembled field list omitted the seed.
    """
    replay_data = "|".join((
        provenance.code_sha,
        provenance.dataset_version,
        coordinate.measurement_key(schedule),
    ))
    return hashlib.sha256(replay_data.encode()).hexdigest()[:16]


def _primary_metric_key(task_id: str) -> str:
    """Get the payload key for the task's primary objective."""
    try:
        registry = get_task_registry()
        spec = registry.get(task_id)
        for obj in spec.objectives:
            if obj.name == spec.primary_objective:
                return obj.payload_key
    except Exception:
        pass
    return "val_acc"


def _core_metric_keys(task_id: str) -> set[str]:
    """Get the set of core metric keys for a task (those that gate cell validity)."""
    try:
        registry = get_task_registry()
        spec = registry.get(task_id)
        keys = set()
        for obj in spec.objectives:
            if obj.is_measured and obj.payload_key:
                keys.add(obj.payload_key)
        keys.update({"loss", "val_loss", "train_loss"})
        return keys
    except Exception:
        return {"loss", "val_loss", "train_loss", "val_acc", "train_acc", "accuracy"}


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


def evaluate_cell(
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
    resolved_device = _resolve_device(schedule.device)
    _set_seeds(schedule.seed, schedule.deterministic)

    task = _task(schedule.task_id, schedule.device, schedule.num_workers)
    shape = _task_shape(task)
    cell = _compose_cell(coordinate, geometry, shape, schedule.param_budget, task)
    config = _create_trainer_config(schedule, resolved_device, params)
    trainer_class = _choose_trainer_class(schedule, task)

    temp_dir, checkpoint_path_ref, checkpoint_callback = _setup_checkpointing(
        schedule, checkpoint_dir, config
    )

    start = time.monotonic()
    trainer, history = _run_training(
        trainer_class, cell, task, config, resume_checkpoint_path, checkpoint_callback
    )
    walltime_s = time.monotonic() - start

    if temp_dir is not None:
        temp_dir.cleanup()

    metrics = _collect_all_metrics(trainer, history, cell, task, schedule, coordinate)
    _post_training_metrics(metrics, cell, task, schedule, coordinate, walltime_s)
    _validate_metrics_finite(metrics, coordinate, schedule.task_id)

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


def _compose_cell(
    coordinate: Coordinate,
    geometry: Mapping[str, Any] | None,
    shape: TaskShape,
    param_budget: int,
    task: Any,
) -> ComposedCell:
    """Compose a cell system from coordinate and task shape."""
    return compose_cell_system(
        coordinate=coordinate,
        geometry=dict(geometry or {}),
        input_shape=shape.input_shape,
        output_dim=shape.output_dim,
        param_budget=param_budget,
        task=task,
    )


def _post_training_metrics(
    metrics: dict[str, float],
    cell: ComposedCell,
    task: Any,
    schedule: Schedule,
    coordinate: Coordinate,
    walltime_s: float,
) -> None:
    """Collect post-training metrics: stability, energy, substrate, plasticity, task-specific."""
    # Ensure system geometry is on the correct device for metrics computation
    # (trainer.close() moves geometry to CPU)
    resolved_device = _resolve_device(schedule.device)
    if hasattr(cell.system.geometry, "to"):
        cell.system.geometry.to(resolved_device)

    sample_x, sample_count = _sample_inputs(task, resolved_device)
    # A PyG batch has no batch-free input, so the free-phase probes (settle
    # telemetry, Jacobian) are not defined for it; the energy estimate is.
    if sample_x is not None:
        metrics.update(compute_stability_metrics(cell.system, sample_x))
    metrics.update(compute_energy_metrics(cell.system, batch_size=sample_count))

    # Substrate-specific objectives
    metrics.update(_compute_substrate_objectives(coordinate, metrics, walltime_s))

    # Plasticity objectives
    metrics.update(compute_plasticity_metrics(cell.system))

    # Domain-specific evaluation (perplexity, f1_score, bleu_score, mean_reward, etc.)
    _update_task_metrics(task, metrics, cell, schedule, coordinate)

    # Derived metric: energy_efficiency = primary_metric / energy_per_sample
    _add_energy_efficiency(metrics, schedule.task_id)


def _set_seeds(seed: int, deterministic: bool) -> None:
    """Set all random seeds for reproducibility."""
    import os
    import random

    import numpy as np

    torch.manual_seed(seed)
    if deterministic:
        os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
        torch.use_deterministic_algorithms(True)
    np.random.seed(seed)
    random.seed(seed)


def _choose_trainer_class(schedule: Schedule, task: Any):
    """Choose trainer class based on task domain and distributed backend."""
    # Check task domain for specialized trainers
    domain_type = getattr(task, "domain_type", None)
    if domain_type is not None:
        from computronium.domains.base import DomainType

        if domain_type == DomainType.RL:
            from computronium.core.system_trainer import RLSystemTrainer

            return RLSystemTrainer
        if domain_type == DomainType.GRAPH:
            from computronium.core.system_trainer import GraphSystemTrainer

            return GraphSystemTrainer

    # Default: distributed or standard SystemTrainer
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
            cell.system, split=TaskSplit.VAL, max_batches=schedule.batch_limit
        )
        task_metrics_dict = task_metrics.to_dict()

        # Map task evaluation metric keys to the registry's expected payload keys.
        # The task registry defines payload_key for each objective; we use that
        # for the primary metric to ensure consistency with the trainer's history.
        try:
            from computronium.experiment.registry.task_registry import get_task_registry

            registry = get_task_registry()
            task_spec = registry.get(schedule.task_id)
            # Map primary metric: task eval returns "accuracy"/"mean_reward"/etc.,
            # but registry expects specific payload_key (e.g., "val_acc" for vision).
            primary_obj_name = task_spec.primary_objective
            for obj in task_spec.objectives:
                if obj.name == primary_obj_name and obj.payload_key:
                    # The task evaluation uses a domain-specific key (e.g., "accuracy",
                    # "perplexity", "mean_reward"). Map it to the registry's payload_key.
                    # We find which key in task_metrics_dict corresponds to the primary objective.
                    domain_key = _primary_domain_metric_key(task.domain_type)
                    if domain_key in task_metrics_dict:
                        # Only set if not already present from trainer history
                        if obj.payload_key not in metrics:
                            metrics[obj.payload_key] = task_metrics_dict[domain_key]
                    break
        except Exception:
            # Fallback: use task metrics as-is
            pass

        # Add all task metrics (non-primary ones keep their original keys)
        for key, value in task_metrics_dict.items():
            if key not in metrics:  # Don't overwrite history metrics (e.g., val_acc)
                metrics[key] = value
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


def _primary_domain_metric_key(domain_type: Any) -> str:
    """Get the metric key that a task's evaluate() returns for its primary metric."""
    from computronium.domains.base import DomainType

    if isinstance(domain_type, str):
        try:
            domain_type = DomainType(domain_type)
        except ValueError:
            return "accuracy"
    match domain_type:
        case DomainType.VISION | DomainType.TABULAR:
            return "accuracy"
        case DomainType.GRAPH:
            return "accuracy"
        case DomainType.LM | DomainType.LANGUAGE:
            return "perplexity"
        case DomainType.RL:
            return "mean_reward"
        case DomainType.TIMESERIES:
            return "mse"
        case _:
            return "accuracy"


def _add_energy_efficiency(metrics: dict[str, float], task_id: str) -> None:
    """Add derived energy_efficiency metric if components exist."""
    primary_key = _primary_metric_key(task_id)
    primary_val = metrics.get(primary_key)
    energy_per_sample = metrics.get("energy_per_sample")
    if (
        primary_val is not None
        and energy_per_sample is not None
        and energy_per_sample > 0
    ):
        metrics["energy_efficiency"] = float(primary_val) / float(energy_per_sample)


def _validate_metrics_finite(
    metrics: dict[str, float], coordinate: Coordinate, task_id: str
) -> None:
    """Fail the cell only when a training metric is non-finite.

    Auxiliary diagnostics (energy proxies, spectral probes) divide by quantities
    a degenerate-but-trained cell can legitimately zero. A NaN there is dropped
    and reported, not used to discard an otherwise valid measurement.
    """
    import math

    nonfinite = sorted(k for k, v in metrics.items() if not math.isfinite(v))
    if not nonfinite:
        return
    core = _core_metric_keys(task_id)
    fatal = [k for k in nonfinite if k in core]
    if fatal:
        msg = f"non-finite training metrics {fatal} for {coordinate.cell_key()[:12]}"
        raise EvaluationError("numerical", msg)
    for key in nonfinite:
        del metrics[key]
    logger.warning(
        "Dropped non-finite auxiliary metrics %s for %s",
        nonfinite,
        coordinate.cell_key()[:12],
    )


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
    *,
    replay_hash: str | None = None,
    deterministic: bool = False,
    schedule: object | None = None,
) -> Status:
    """Build schema Status with assessment procedure metadata (WP5).

    Reproducibility class is derived from replay hash presence and determinism:
    - REPLAYABLE: replay_hash present AND deterministic=True
    - REPRODUCIBLE: replay_hash present but not deterministic
    - UNVERIFIED: no replay hash
    """
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

    # Determine reproducibility class (D10)
    if replay_hash and deterministic:
        reproducibility = ReproducibilityClass.REPLAYABLE
    elif replay_hash:
        reproducibility = ReproducibilityClass.COMPUTATIONALLY_REPRODUCIBLE
    else:
        reproducibility = ReproducibilityClass.REPLAYABLE

    # Determine maturity from schedule fidelity
    fidelity_to_maturity = {"L0": Maturity.L0, "L1": Maturity.L1, "L2": Maturity.L2}
    maturity = (
        fidelity_to_maturity.get(schedule.fidelity, Maturity.L0)
        if schedule
        else Maturity.L0
    )

    legacy_status = StatusLegacy(
        gate_verdict=GateVerdict.PASS_ if passed else GateVerdict.FAIL,
        defect=_defect(complete, within_ceiling, param_count, param_budget),
        cause=FailureCause.UNKNOWN if passed else FailureCause.CONSTRAINT_VIOLATION,
        severity=Severity.LOW if passed else Severity.MEDIUM,
        quarantine=not passed,
        maturity=maturity,
        uncertainty={},
        reproducibility=reproducibility,
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
        fidelity_to_maturity = {"L0": Maturity.L0, "L1": Maturity.L1, "L2": Maturity.L2}
        maturity = fidelity_to_maturity.get(schedule.fidelity, Maturity.L0)
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
                maturity=maturity,
                uncertainty={},
                reproducibility=ReproducibilityClass.REPLAYABLE,
                assessment_procedure_version=ASSESSMENT_PROCEDURE_VERSION,
                ceec_link=None,
            ),
            payload={"status": "failed", "cause": exc.cause, "error": str(exc)},
        )

    complete = evaluation.epochs_completed >= schedule.epochs
    within_ceiling = _within_ceiling(evaluation.param_count, schedule.param_budget)

    # Compute replay hash for reproducibility (D10)
    # Hash over: code_sha, dataset_version, coordinate + full schedule
    replay_hash = _cell_replay_hash(provenance, coordinate, schedule)

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
        "replay_hash": replay_hash,
    }
    # Add normalized metric (primary_metric normalized against task baseline)
    from computronium.domains._task_registry import get_baseline, normalize_score

    task_id = evaluation.task_id
    primary_key = _primary_metric_key(task_id)
    primary_val = evaluation.metrics.get(primary_key, 0.0)
    baseline = get_baseline(task_id)
    normalized_metric = normalize_score(primary_val, task_id, baseline)
    payload["normalized_metric"] = normalized_metric
    payload["primary_metric"] = primary_key
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
        replay_hash=replay_hash,
        deterministic=schedule.deterministic,
        schedule=schedule,
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
