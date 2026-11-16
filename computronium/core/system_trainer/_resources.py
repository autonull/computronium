"""Per-epoch resource accounting for :class:`SystemTrainer`.

``SystemTrainerConfig`` has carried ``track_flops`` and ``track_memory`` as
configuration, and until this module nothing read them. A caller that asked a
trainer for a resource budget got an epoch dict with loss and accuracy in it
and no resource numbers -- the ``cpu_only`` defect again: a declared switch
read by nothing.

These records are deliberately **not** in the epoch metrics dict. A run's
metrics are a claim about the model and must be bit-for-bit reproducible from
a seed; an epoch's wall time, peak memory and FLOP count are observations
about the machine it ran on. Putting them in the same dict broke
``test_geometry_execution_is_bit_for_bit_reproducible`` on the first run,
which is the sharpest available statement of why they are separate.

Three rules shape the output. A metric that was *measured* is reported; a
metric that could not be measured is ``None``, not zero, so "unmeasured" and
"measured as zero" stay distinguishable. And the ``max_epoch_time`` budget is
recorded on the epoch it truncated, because a partial epoch's time and memory
are not comparable with a full epoch's.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import TYPE_CHECKING, cast

import torch

from computronium.core.logging import get_logger

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from torch import Tensor

    from computronium.ontology import System

logger = get_logger()

_MB = 1024 * 1024

# A cell is memory-bound when the plain-backprop arm's activations are at least
# this share of its peak. Below it, both arms fit and a "memory" verdict is
# vacuous (TODO93 §9.5); the cell is ``[regime-mismatch]``, not evidence.
BINDING_SHARE = 0.5

__all__ = [
    "BINDING_SHARE",
    "EpochResource",
    "EpochResources",
    "binding_verdict",
    "credit_path_of",
]


def credit_path_of(system: object) -> str:
    """Name the credit-assignment route a training step actually took.

    A composed system's ``train_step`` runs the pipeline through its credit
    rule, so the rule's class name is the route. An adapted plain module has
    two other routes -- the module's own ``train_step``, or the BPTT fallback
    -- and those are the routes worth surfacing: a bio-family probe that
    silently reports ``bptt`` is a defect, and a name is how a consumer sees
    it without reading the run.
    """
    route = getattr(system, "last_training_path", None)
    if isinstance(route, str) and route:
        return route
    credit = getattr(system, "credit", None)
    return type(credit).__name__ if credit is not None else "unknown"


@dataclass(frozen=True, slots=True)
class EpochResource:
    """What one epoch cost, on the machine it ran on.

    The memory fields decompose the CUDA peak into the terms a claim has to
    name: parameters, optimizer state, and the remainder the epoch allocated.
    ``activations_mb`` is that remainder -- Graph-B allocation the forward and
    backward passes hold -- and it is ``None`` when the peak is unmeasured or
    when the optimizer's state could not be enumerated, never a fabricated 0.0.
    """

    epoch: int
    epoch_time_s: float
    steps: int
    training_paths: Mapping[str, int]
    budget_stopped: bool = False
    deadline_exceeded: bool = False
    peak_memory_mb: float | None = None
    forward_flops: int | None = None
    backward_flops: int | None = None
    energy_joules: float | None = None
    params_mb: float | None = None
    optimizer_mb: float | None = None
    activations_mb: float | None = None
    auxiliary_mb: float | None = None
    cpu_rss_mb: float | None = None

    @property
    def activation_share(self) -> float | None:
        """Activations as a share of peak, or ``None`` when either is unknown."""
        if self.activations_mb is None or not self.peak_memory_mb:
            return None
        return self.activations_mb / self.peak_memory_mb


def binding_verdict(resource: EpochResource) -> bool | None:
    """Is this cell's regime memory-bound?

    Computed on the plain-backprop arm, never on the checkpointed one:
    checkpointing exists to shrink activations below the gate, so gating on it
    self-defeats (TODO93 B1). ``None`` means the share was not measured, which
    is not a pass.
    """
    share = resource.activation_share
    return None if share is None else share >= BINDING_SHARE


@dataclass(slots=True)
class EpochResources:
    """Accumulates one epoch's cost and emits an :class:`EpochResource`."""

    system: System
    device: torch.device
    track_flops: bool
    track_memory: bool
    max_epoch_time: float = 0.0
    steps: int = 0
    paths: dict[str, int] = field(default_factory=dict)
    _started: float = 0.0
    _elapsed: float = 0.0
    _stopped: bool = False
    _flops_per_batch: int = 0
    _peak_mb: float = 0.0
    _energy_j: float = 0.0
    _start_power_w: float = 0.0
    deadline_exceeded: bool = False

    @property
    def _cuda(self) -> bool:
        """Is peak memory a metric this run can actually measure?"""
        return (
            self.track_memory
            and self.device.type == "cuda"
            and torch.cuda.is_available()
        )

    @property
    def elapsed(self) -> float:
        """Seconds since the epoch started, live until :meth:`stop` freezes it.

        The budget is checked *inside* the batch loop, so it has to read a
        running clock; a value only written at the end of the epoch would make
        the budget unenforceable for exactly the epochs that overrun it.
        """
        return self._elapsed if self._stopped else time.perf_counter() - self._started

    @property
    def over_budget(self) -> bool:
        """Did this epoch run past ``max_epoch_time``?"""
        return self.max_epoch_time > 0 and self.elapsed > self.max_epoch_time

    def start(self) -> None:
        """Begin timing, and reset the CUDA peak counter the epoch reports."""
        self._started = time.perf_counter()
        self._stopped = False
        self.steps = 0
        self.paths = {}
        self._flops_per_batch = 0
        self._energy_j = 0.0
        self.deadline_exceeded = False
        if self._cuda:
            torch.cuda.reset_peak_memory_stats()
            # Sample initial power for energy estimation
            try:
                from computronium.core.profiling import get_gpu_power_watts

                self._start_power_w = get_gpu_power_watts()
            except Exception:
                self._start_power_w = 0.0

    def note_step(self, batch_size: int) -> None:
        """Record one completed training batch."""
        self.steps += 1
        route = credit_path_of(self.system)
        self.paths[route] = self.paths.get(route, 0) + 1
        if self.track_flops and not self._flops_per_batch:
            self._flops_per_batch = _flops_per_batch(self.system, batch_size)

    def stop(self) -> None:
        """Close the epoch's timer and read the peak memory it reached."""
        self._elapsed = time.perf_counter() - self._started
        self._stopped = True
        if self._cuda:
            self._peak_mb = torch.cuda.max_memory_allocated() / _MB
            # Estimate energy: average power × time
            try:
                from computronium.core.profiling import get_gpu_power_watts

                end_power_w = get_gpu_power_watts()
                avg_power_w = (self._start_power_w + end_power_w) / 2
                self._energy_j = avg_power_w * self._elapsed
            except Exception:
                self._energy_j = 0.0

    def record(self, epoch: int) -> EpochResource:
        """Freeze this epoch's cost. Call after :meth:`stop`."""
        forward = self._flops_per_batch * self.steps or None
        params_mb, optimizer_mb, auxiliary_mb = self._decomposition()
        peak = self._peak_mb if self._cuda else None
        # An unenumerable optimizer makes the remainder unknown, not zero:
        # reporting activations from a partial decomposition would attribute
        # the optimizer's state to the activation term.
        activations_mb = (
            None
            if peak is None or optimizer_mb is None
            else max(peak - params_mb - optimizer_mb - auxiliary_mb, 0.0)
        )
        return EpochResource(
            epoch=epoch,
            epoch_time_s=self.elapsed,
            steps=self.steps,
            training_paths=MappingProxyType(dict(self.paths)),
            budget_stopped=self.over_budget,
            deadline_exceeded=self.deadline_exceeded,
            peak_memory_mb=peak,
            forward_flops=forward,
            backward_flops=2 * forward if forward is not None else None,
            energy_joules=self._energy_j if self._cuda and self._energy_j > 0 else None,
            params_mb=params_mb,
            optimizer_mb=optimizer_mb,
            activations_mb=activations_mb,
            auxiliary_mb=auxiliary_mb,
            cpu_rss_mb=_cpu_rss_mb(),
        )

    def _decomposition(self) -> tuple[float, float | None, float]:
        """``(params, optimizer, auxiliary)`` in MB, all measured.

        Parameters are the geometry's live tensors. Optimizer state is whatever
        the update rule declares through ``state_tensors`` -- ``0.0`` for a
        stateless rule, which is a measurement. ``auxiliary`` is the state a
        mechanism holds outside both (feedback matrices, consolidation
        buffers); until a mechanism declares it, the remainder is reported as
        activations and named as such in the row.
        """
        params = cast("Mapping[str, Tensor]", self.system.geometry.params)
        params_mb = _tensor_mb(params.values())
        update = getattr(self.system, "update", None)
        state_tensors = getattr(update, "state_tensors", None)
        optimizer_mb: float | None = None
        if callable(state_tensors):
            optimizer_state = cast("Mapping[str, Tensor]", state_tensors())
            optimizer_mb = _tensor_mb(optimizer_state.values())
        return params_mb, optimizer_mb, 0.0


def _tensor_mb(tensors: Iterable[Tensor]) -> float:
    """Bytes held by ``tensors``, in MB."""
    return sum(t.numel() * t.element_size() for t in tensors) / _MB


def _cpu_rss_mb() -> float | None:
    """Resident set size of this process, or ``None`` when psutil is absent.

    CPU runs measure RSS only, so a CPU cell is an instrument-validity cell and
    never a claim row; the number is recorded so the distinction is visible.
    """
    try:
        import psutil
    except ImportError:  # pragma: no cover - declared dependency, guarded
        return None
    return psutil.Process().memory_info().rss / _MB


def _flops_per_batch(system: System, batch_size: int) -> int:
    """One train step's FLOP estimate, or 0 when the system cannot supply one.

    The estimator needs a layered geometry and a known settle structure; a
    system without either reports no FLOPs rather than a fabricated number.
    """
    from computronium.core.profiling import (
        count_flops,
        estimate_train_step_flops,
    )

    # Try structure-derived estimate first (deterministic, no device dependence)
    try:
        return estimate_train_step_flops(system, batch_size)
    except (ValueError, TypeError, AttributeError, KeyError) as exc:
        logger.debug(
            "structure FLOP estimate failed for %s: %s", type(system).__name__, exc
        )

    # Fallback to parameter-counting estimate
    try:
        input_shape = _get_input_shape(system)
        if input_shape:
            return count_flops(system.geometry, (batch_size, *input_shape[1:]))
    except Exception as exc:
        logger.debug(
            "parameter FLOP count failed for %s: %s", type(system).__name__, exc
        )

    return 0


def _get_input_shape(system: System) -> tuple[int, ...] | None:
    """Extract input shape from system geometry."""
    geometry = system.geometry
    if hasattr(geometry, "config") and hasattr(geometry.config, "input_dim"):
        return (1, geometry.config.input_dim)
    if hasattr(geometry, "input_dim"):
        return (1, geometry.input_dim)
    return None
