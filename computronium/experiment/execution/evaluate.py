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

# ρ(J) is exactly 0 for a nilpotent step and ln(0) is -inf, which would fail
# the finite-metrics gate on a measurement that succeeded.
_RADIUS_FLOOR: Final[float] = 1e-10

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
    """Stability of one relaxation step, measured on the trained system.

    Reports, for the settle step's Jacobian ``J`` over the hidden stack:

    - ``spectral_radius`` ρ(J) — asymptotic stability margin
    - ``max_singular_value`` σ_max(J) — transient amplification bound
    - ``min_singular_value`` σ_min(J) — the condition-number floor
    - ``lyapunov_exponent`` — ln ρ(J), negative exactly when contracting
    - ``settle_steps`` / ``settle_converged`` — the free phase's own telemetry
    - ``free_energy`` — the dynamics' energy at the settled state

    The step, not the settle: a loop that runs ``N`` steps composes the step
    Jacobian N times, so measuring the whole settle reports ρ^N. At ρ=0.997 and
    N=30 that is 0.91, and any σ_max > 1 is long since below 1 — a contracting
    but transiently amplifying cell reads as a collapse (TODO51 §2).

    The Jacobian is exact (``torch.autograd.functional.jacobian``), so the
    hidden stack is capped: an O(d²) SVD on an uncapped stack is how a
    measurement turns into a timeout.
    """
    from computronium.experiment.execution.settle_operator import settle_step_operator

    metrics: dict[str, float] = {}
    free_energy = _free_settle_metrics(system, x)
    metrics.update(free_energy)

    operator = settle_step_operator(system, x)
    if operator is None:
        logger.debug("geometry is not layered; reporting settle telemetry only")
        return metrics

    step, width = operator
    if width > _MAX_JACOBIAN_WIDTH:
        logger.info(
            "hidden width %d exceeds the Jacobian cap %d; reporting settle telemetry",
            width,
            _MAX_JACOBIAN_WIDTH,
        )
        return metrics

    try:  # ruff: ignore[too-many-statements-in-try-clause]
        jac = torch.autograd.functional.jacobian(
            step, torch.zeros(width, device=_param_device(system))
        )
        singular = torch.linalg.svdvals(jac)
        sigma_max = float(singular.max().item())
        sigma_min = float(singular.min().item())
        radius = (
            float(torch.linalg.eigvals(jac).abs().max().item())
            if jac.shape[0] == jac.shape[1]
            else sigma_max
        )
        metrics["spectral_radius"] = radius
        metrics["max_singular_value"] = sigma_max
        metrics["min_singular_value"] = sigma_min
        metrics["lyapunov_exponent"] = math.log(max(radius, _RADIUS_FLOOR))
        metrics["stability_margin"] = 1.0 - radius
        metrics["nonnormality"] = sigma_max / max(radius, _RADIUS_FLOOR)
    except Exception as exc:  # ruff: ignore[blind-except] - a metric must not fail the cell
        logger.warning("settle-step Jacobian failed: %s", exc)
    return metrics


def _free_settle_metrics(system: Any, x: torch.Tensor) -> dict[str, float]:
    """The free phase's own telemetry: horizon used, convergence, energy.

    Read after a settle this function owns. The dynamics' telemetry counters
    are reset by the settle that runs next, so a caller reading them after its
    own settle reads the counters of whichever settle ran last — which is why
    ``settle_converged`` was ``0`` on cells that converged within the budget.
    """
    from computronium.core.pipeline import forward_pass
    from computronium.ontology import SystemState

    metrics: dict[str, float] = {}
    device = _param_device(system)
    try:  # ruff: ignore[too-many-statements-in-try-clause]
        with torch.no_grad():
            state = SystemState(x=x.to(device), y=None)
            state.activations = forward_pass(
                system.substrate, system.geometry, x.to(device)
            )
            settled = system.dynamics.settle(
                state, system.geometry, system.substrate, target=None
            )
            metrics["settle_steps"] = float(
                getattr(system.dynamics, "_settle_steps_used", 0)
            )
            metrics["settle_converged"] = float(
                bool(getattr(system.dynamics, "_converged", False))
            )
            metrics["settle_horizon"] = float(
                getattr(system.dynamics, "_settle_horizon", 0)
            )
            try:
                energy = system.dynamics.compute_energy(settled, system.geometry)
                if energy is not None:
                    metrics["free_energy"] = float(
                        energy.item() if hasattr(energy, "item") else energy
                    )
            except Exception as exc:  # ruff: ignore[blind-except] - a proxy energy is optional
                logger.debug("free energy unavailable: %s", exc)
    except Exception as exc:  # ruff: ignore[blind-except] - a metric must not fail the cell
        logger.warning("free settle telemetry failed: %s", exc)
    return metrics


def _param_device(system: Any) -> torch.device:
    """The device the cell's weights live on, wherever it was trained.

    The evaluator may run on a thread whose device differs from the one the
    system was built on, so the device is read from the parameters rather than
    from the caller's tensor.
    """
    return next(system.geometry.parameters()).device


def compute_energy_metrics(system: Any, *, batch_size: int) -> dict[str, float]:
    """Per-step energy from the substrate's own per-MAC model.

    Charged over the geometry's real layer shapes, one estimate per layer and
    summed. A single hardcoded ``(out, in)`` weight shape reports one number for
    every cell, which is how 36k-parameter and 305k-parameter cells came back
    with byte-identical joules (TODO51 §5).
    """
    from computronium.experiment.execution.settle_operator import layer_weight_shapes

    metrics: dict[str, float] = {}
    estimator = getattr(system.substrate, "estimate_energy", None)
    if estimator is None:
        return metrics

    shapes = layer_weight_shapes(system.geometry)
    if not shapes:
        return metrics

    forward = update = 0.0
    per_sample = 0.0
    for out_features, in_features in shapes:
        estimate = estimator(
            input_shape=(batch_size, in_features),
            weight_shape=(out_features, in_features),
            batch_size=batch_size,
        )
        forward += float(estimate.get("forward_energy_per_batch", 0.0))
        update += float(estimate.get("update_energy_per_batch", 0.0))
        per_sample += float(estimate.get("energy_per_sample", 0.0))

    metrics["forward_energy_per_batch"] = forward
    metrics["update_energy_per_batch"] = update
    metrics["energy_per_batch"] = forward + update
    metrics["energy_per_sample"] = per_sample
    metrics["macs_per_step"] = float(
        batch_size * 2 * sum(out * inn for out, inn in shapes)
    )
    metrics["energy_per_mac"] = (
        (forward + update) / metrics["macs_per_step"]
        if metrics["macs_per_step"] > 0
        else 0.0
    )
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


def _sample_inputs(task: Any, device: str) -> torch.Tensor:
    """One flattened training batch, on ``device``.

    Flattened because the stability and energy metrics both read the task's
    own input extent; a rank-4 image batch would make the energy model's
    ``input_shape[-1]`` the pixel count of a row.
    """
    sample_x, _ = next(iter(task.get_dataloader("train")))
    flat = sample_x.to(device).reshape(sample_x.shape[0], -1)
    return flat


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

    sample_x = _sample_inputs(task, config.device)
    metrics.update(compute_stability_metrics(cell.system, sample_x))
    metrics.update(compute_energy_metrics(cell.system, batch_size=sample_x.shape[0]))

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
