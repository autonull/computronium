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
from typing import TYPE_CHECKING

import torch

from computronium.core.logging import get_logger

if TYPE_CHECKING:
    from collections.abc import Mapping

    from computronium.ontology import System

logger = get_logger()

_MB = 1024 * 1024

__all__ = ["EpochResource", "EpochResources", "credit_path_of"]


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
    """What one epoch cost, on the machine it ran on."""

    epoch: int
    epoch_time_s: float
    steps: int
    training_paths: Mapping[str, int]
    budget_stopped: bool = False
    peak_memory_mb: float | None = None
    forward_flops: int | None = None
    backward_flops: int | None = None


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
        if self._cuda:
            torch.cuda.reset_peak_memory_stats()

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
        self._peak_mb = torch.cuda.max_memory_allocated() / _MB if self._cuda else 0.0

    def record(self, epoch: int) -> EpochResource:
        """Freeze this epoch's cost. Call after :meth:`stop`."""
        forward = self._flops_per_batch * self.steps or None
        return EpochResource(
            epoch=epoch,
            epoch_time_s=self.elapsed,
            steps=self.steps,
            training_paths=MappingProxyType(dict(self.paths)),
            budget_stopped=self.over_budget,
            peak_memory_mb=self._peak_mb if self._cuda else None,
            forward_flops=forward,
            backward_flops=2 * forward if forward is not None else None,
        )


def _flops_per_batch(system: System, batch_size: int) -> int:
    """One train step's FLOP estimate, or 0 when the system cannot supply one.

    The estimator needs a layered geometry and a known settle structure; a
    system without either reports no FLOPs rather than a fabricated number.
    """
    from computronium.core.profiling import (
        count_flops_fvcore,
        estimate_train_step_flops,
    )

    # Try fvcore first for accurate measurement
    try:
        # Get input shape from the system's geometry
        input_shape = _get_input_shape(system)
        if input_shape:
            return count_flops_fvcore(system.geometry, (batch_size, *input_shape[1:]))
    except Exception as exc:
        logger.debug("fvcore FLOP count failed for %s: %s", type(system).__name__, exc)

    # Fallback to structure-derived estimate
    try:
        return estimate_train_step_flops(system, batch_size)
    except (ValueError, TypeError, AttributeError, KeyError) as exc:
        logger.debug("no FLOP estimate for %s: %s", type(system).__name__, exc)
        return 0


def _get_input_shape(system: System) -> tuple[int, ...] | None:
    """Extract input shape from system geometry."""
    geometry = system.geometry
    if hasattr(geometry, "config") and hasattr(geometry.config, "input_dim"):
        return (1, geometry.config.input_dim)
    if hasattr(geometry, "input_dim"):
        return (1, geometry.input_dim)
    return None
