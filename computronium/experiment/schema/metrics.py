"""What a measurement actually carries, and which objectives can read it.

``OBJECTIVES`` states what the research program cares about; it is not a claim
that the kernel measures any of it. This module is the single declaration of
the two facts that turn an objective name into a number:

* :data:`HISTORY_METRICS` — the per-epoch observations the trainer reports, and
  :data:`MEASURED_METRICS`, those plus what the evaluator measures around them.
  ``evaluate.history_metrics`` filters on this set, so a metric nobody
  declares does not reach a payload.
* :data:`MEASURED_OBJECTIVES` — the objective names a payload key satisfies.

Everything else in ``OBJECTIVES`` is a research target awaiting a measurement.
It stays registered, and it carries the reason (``ObjectiveSpec``), because an
objective a run names and cannot measure is a claim the run makes and then
withdraws silently — the shape TODO46 §2.0 describes.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

__all__ = [
    "HISTORY_METRICS",
    "MEASURED_METRICS",
    "MEASURED_OBJECTIVES",
    "ObjectiveResolutionError",
    "UnknownObjectiveError",
    "UnmeasuredObjectiveError",
    "measured_objectives",
    "objective_metric",
    "objective_name",
    "objective_values",
    "optimizes",
]

# Per-epoch observations the trainer reports in its history.
HISTORY_METRICS: Final[frozenset[str]] = frozenset({
    "train_acc",
    "train_loss",
    "train_energy",
    "val_acc",
    "val_loss",
})

# What a record's payload offers an objective: the history plus the cost the
# evaluator itself timed and counted.
MEASURED_METRICS: Final[frozenset[str]] = HISTORY_METRICS | {
    "epochs_run",
    "walltime_s",
    "param_count",
    "settle_steps",
    "settle_converged",
    "settle_horizon",
    "spectral_radius",
    "max_singular_value",
    "min_singular_value",
    "lyapunov_exponent",
    "stability_margin",
    "nonnormality",
    "free_energy",
    "energy_per_batch",
    "energy_per_sample",
    "energy_per_mac",
    "macs_per_step",
    "forward_energy_per_batch",
    "update_energy_per_batch",
}

# Objective name -> the payload key that satisfies it.
MEASURED_OBJECTIVES: Final[Mapping[str, str]] = MappingProxyType({
    "validation_accuracy": "val_acc",
    "validation_loss": "val_loss",
    "walltime_total": "walltime_s",
    "param_count": "param_count",
    "settle_steps": "settle_steps",
    "spectral_radius": "spectral_radius",
    "max_singular_value": "max_singular_value",
    "lyapunov_exponent": "lyapunov_exponent",
    "free_energy": "free_energy",
    "energy_per_step": "energy_per_sample",
    "energy_per_mac": "energy_per_mac",
    "macs_per_step": "macs_per_step",
    "stability_margin": "stability_margin",
    "nonnormality": "nonnormality",
})


class ObjectiveResolutionError(LookupError):
    """An objective name cannot be turned into a measurement."""


class UnknownObjectiveError(ObjectiveResolutionError):
    """No such objective in ``OBJECTIVES``."""


class UnmeasuredObjectiveError(ObjectiveResolutionError):
    """The objective is registered, but nothing emits a metric for it."""


def measured_objectives() -> tuple[str, ...]:
    """The objective names a payload key can satisfy."""
    return tuple(sorted(MEASURED_OBJECTIVES))


def objective_name(metric_key: str) -> str | None:
    """The objective name a payload key satisfies, or ``None`` if none does.

    The reverse of :func:`objective_metric`, so a consumer holding a payload key
    can still ask which declared objective it is — and in which direction.
    """
    for name, key in MEASURED_OBJECTIVES.items():
        if key == metric_key:
            return name
    return None


def optimizes(name: str) -> bool:
    """Whether an objective is maximized (True) or minimized (False)."""
    from computronium.experiment.schema.registries import OBJECTIVES_REGISTRY

    return OBJECTIVES_REGISTRY[name].direction == "maximize"


def objective_metric(name: str) -> str:
    """The payload key that satisfies one objective name.

    Args:
        name: An objective name from ``OBJECTIVES``.

    Returns:
        The payload key holding that objective's value.

    Raises:
        UnknownObjectiveError: No such registered objective.
        UnmeasuredObjectiveError: Registered, but no measurement produces it.
    """
    from computronium.experiment.schema.registries import OBJECTIVES_REGISTRY

    if name not in OBJECTIVES_REGISTRY:
        msg = f"unknown objective {name!r}; available: {sorted(OBJECTIVES_REGISTRY.keys())}"
        raise UnknownObjectiveError(msg)
    key = MEASURED_OBJECTIVES.get(name)
    if key is None:
        spec = OBJECTIVES_REGISTRY[name]
        msg = (
            f"objective {name!r} is registered but unmeasured: "
            f"{spec.unavailable_reason or 'no evaluator metric is declared for it'}. "
            f"Measured objectives: {list(measured_objectives())}"
        )
        raise UnmeasuredObjectiveError(msg)
    return key


def objective_values(
    names: Sequence[str], payload: Mapping[str, object]
) -> tuple[float, ...] | None:
    """The values a record's payload holds for the given objectives.

    Args:
        names: Objective names, in the order the study declared them.
        payload: A record's measured payload.

    Returns:
        One float per objective, or ``None`` when the payload did not measure
        one of them — a trial that was told a value it never earned is the
        silent-maximize defect §3.4 names.

    Raises:
        UnknownObjectiveError: A name is not a registered objective.
        UnmeasuredObjectiveError: A name has no measurement behind it.
    """
    values: list[float] = []
    for name in names:
        key = objective_metric(name)
        raw = payload.get(key)
        if not isinstance(raw, int | float) or isinstance(raw, bool):
            return None
        values.append(float(raw))
    return tuple(values)
