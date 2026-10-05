"""Real cell evaluation: coordinate + schedule + task → trained system metrics.

The kernel's only evaluator. ``LocalBackend`` and ``MultiprocessBackend`` both
delegate here, because two implementations of "evaluate" is how the placeholder
evaluator came to exist (TODO46 §D1).

Shape comes from the task, never from a default: ``resolve_task`` builds the
concrete ``DomainTask`` and reads its own ``input_dim``/``output_dim``.
"""

from __future__ import annotations

import math
import pathlib
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
    "compute_energy_metrics",
    "compute_stability_metrics",
    "evaluate_cell",
    "history_metrics",
    "task_shape",
]

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


def compute_stability_metrics(
    system: Any,
    x: torch.Tensor,
    max_steps: int = 50,
) -> dict[str, float]:
    """Compute stability metrics from the trained system.

    Computes:
    - spectral_radius: spectral radius of the Jacobian (asymptotic stability margin)
    - max_singular_value: maximum singular value of the Jacobian (transient amplification bound)
    - settle_steps: number of settle steps to convergence
    - lyapunov_exponent: largest Lyapunov exponent estimate
    - free_energy: free energy at convergence
    """
    from torch.autograd.functional import jacobian

    from computronium.core.pipeline import forward_pass
    from computronium.ontology import SystemState

    metrics = {}

    try:
        with torch.no_grad():
            # Determine device from system parameters (where training happened)
            # This ensures x is on the same device as model weights
            device = next(system.geometry.parameters()).device

            # Get the settled state from a free-phase forward pass
            state = SystemState(x=x.to(device), y=None)
            initial_acts = forward_pass(system.substrate, system.geometry, x.to(device))
            state.activations = initial_acts
            settled = system.dynamics.settle(
                state, system.geometry, system.substrate, target=None
            )

            # Settle steps used (from dynamics telemetry)
            settle_steps = getattr(system.dynamics, "_settle_steps_used", 0)
            converged = getattr(system.dynamics, "_converged", False)
            metrics["settle_steps"] = float(settle_steps)
            metrics["settle_converged"] = 1.0 if converged else 0.0

            # Compute free energy at convergence using the dynamics' compute_energy
            try:
                free_energy = system.dynamics.compute_energy(settled, system.geometry)
                if free_energy is not None:
                    metrics["free_energy"] = float(
                        free_energy.item()
                        if hasattr(free_energy, "item")
                        else free_energy
                    )
            except Exception as e:
                logger.debug(f"Free energy computation failed: {e}")

            # Compute Jacobian of the dynamics for stability analysis
            # Use torch.autograd.functional.jacobian for proper Jacobian matrix
            try:
                # Use a single sample for Jacobian computation
                x_single = x[:1].detach().clone().requires_grad_(True).to(device)

                def settle_fn(x_input):
                    state_jac = SystemState(x=x_input, y=None)
                    initial_acts_jac = forward_pass(
                        system.substrate, system.geometry, x_input
                    )
                    state_jac.activations = initial_acts_jac
                    settled_jac = system.dynamics.settle(
                        state_jac, system.geometry, system.substrate, target=None
                    )
                    return (
                        settled_jac.activations[-1]
                        if isinstance(settled_jac.activations, list)
                        else settled_jac.activations
                    )

                # Compute Jacobian: [1, out_dim, 1, in_dim] -> [out_dim, in_dim]
                J_full = jacobian(settle_fn, x_single)
                # Squeeze batch dimensions to get [out_dim, in_dim]
                J = J_full.squeeze(0).squeeze(1) if J_full.dim() == 4 else J_full
                if J.dim() != 2:
                    raise ValueError(f"Unexpected Jacobian shape after squeeze: {J.shape}")

                # Compute singular values
                _, S, _ = torch.linalg.svd(J, full_matrices=False)
                metrics["max_singular_value"] = float(S.max().item())
                metrics["min_singular_value"] = float(S.min().item())

                # Spectral radius (for square matrices) or approximate
                if J.shape[0] == J.shape[1]:
                    eigvals = torch.linalg.eigvals(J)
                    spectral_radius = eigvals.abs().max().item()
                    metrics["spectral_radius"] = float(spectral_radius)

                    # Lyapunov exponent approximation
                    metrics["lyapunov_exponent"] = float(
                        math.log(max(spectral_radius, 1e-10))
                    )
                else:
                    # Non-square: use max singular value as bound
                    metrics["spectral_radius"] = float(S.max().item())
                    metrics["lyapunov_exponent"] = float(
                        math.log(max(S.max().item(), 1e-10))
                    )

            except Exception as e:
                import os
                import traceback

                log_path = os.path.join(os.getcwd(), "stability_error.log")
                try:
                    with pathlib.Path(log_path).open("w") as f:
                        f.write(f"Jacobian computation failed: {e}\n")
                        traceback.print_exc(file=f)
                        f.flush()
                        os.fsync(f.fileno())
                    logger.debug(f"Wrote Jacobian error to {log_path}")
                except Exception as write_e:
                    logger.debug(f"Failed to write Jacobian log: {write_e}")

    except Exception as e:
        import os
        import traceback

        logger.debug(f"OUTER EXCEPT BLOCK REACHED: {e}")
        log_path = os.path.join(os.getcwd(), "stability_error.log")
        try:
            with pathlib.Path(log_path).open("w") as f:
                f.write(f"Stability metrics computation failed: {e}\n")
                traceback.print_exc(file=f)
                f.flush()
                os.fsync(f.fileno())
            logger.debug(f"Wrote stability error to {log_path}")
        except Exception as write_e:
            logger.debug(f"Failed to write stability log: {write_e}")

    return metrics


def compute_energy_metrics(
    system: Any,
    batch_size: int,
    input_shape: tuple[int, ...],
    weight_shape: tuple[int, ...],
    num_layers: int = 1,
) -> dict[str, float]:
    """Compute energy metrics using substrate's estimate_energy method."""
    metrics = {}
    try:
        substrate = system.substrate
        if hasattr(substrate, "estimate_energy"):
            energy_est = substrate.estimate_energy(
                input_shape=input_shape,
                weight_shape=weight_shape,
                batch_size=batch_size,
                num_layers=num_layers,
            )
            metrics.update({
                "energy_per_batch": energy_est.get("total_energy_per_step", 0.0),
                "energy_per_sample": energy_est.get("energy_per_sample", 0.0),
                "forward_energy_per_batch": energy_est.get(
                    "forward_energy_per_batch", 0.0
                ),
                "update_energy_per_batch": energy_est.get(
                    "update_energy_per_batch", 0.0
                ),
            })
    except Exception as e:
        logger.debug(f"Energy metrics computation failed: {e}")
    return metrics


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
    import random

    import numpy as np
    import torch

    # Resolve device early so "auto" becomes "cuda" or "cpu" before any PyTorch ops
    # This is critical when called from thread pools where device context may differ
    resolved_device = _resolve_device(schedule.device)

    # Set all seeds BEFORE model creation for reproducible initialization
    torch.manual_seed(schedule.seed)
    if schedule.deterministic:
        torch.use_deterministic_algorithms(True)
    np.random.seed(schedule.seed)
    random.seed(schedule.seed)

    task = _task(schedule.task_id, schedule.device, schedule.num_workers)
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
        device=resolved_device,
        seed=schedule.seed,
        limit_train_batches=limit,
        limit_val_batches=limit,
        track_flops=False,
        track_memory=False,
        deterministic=schedule.deterministic,
    )

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

    # Compute stability metrics (spectral_radius, max_singular_value, settle_steps, etc.)
    try:
        # Get a sample batch for stability computation
        sample_batch = next(iter(task.get_dataloader("train")))
        sample_x, _ = sample_batch
        sample_x = sample_x.to(config.device)
        if sample_x.dim() > 2:
            sample_x = sample_x.reshape(sample_x.size(0), -1)
        stability_metrics = compute_stability_metrics(cell.system, sample_x)
        metrics.update(stability_metrics)
    except Exception as e:
        logger.debug(f"Stability metrics computation failed: {e}")

    # Compute energy metrics using substrate's estimate_energy
    try:
        # Get input/weight shapes for energy estimation
        input_dim = math.prod(shape.input_shape)
        output_dim = shape.output_dim
        # Estimate weight shape from param_count and geometry
        # For a typical MLP: input_dim * hidden + hidden * hidden * (depth-1) + hidden * output
        # We approximate weight_shape as (output_dim, input_dim) for energy estimation
        weight_shape = (output_dim, input_dim)
        batch_size = (
            config.limit_train_batches or sample_x.size(0)
            if "sample_x" in locals()
            else 64
        )
        energy_metrics = compute_energy_metrics(
            cell.system,
            batch_size=batch_size,
            input_shape=(batch_size, input_dim),
            weight_shape=weight_shape,
            num_layers=1,  # Approximate
        )
        metrics.update(energy_metrics)
    except Exception as e:
        logger.debug(f"Energy metrics computation failed: {e}")

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
