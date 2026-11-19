"""S2: calibrate the bar, bind the axes, price the cell (TODO95 S2).

A bar at the chance rate alone is a coin flip: at 10,000 held-out samples
the chance rate 0.100 has a 2σ band of ±0.006, so a cell measuring 0.101 has
cleared no floor. The bar is the task's chance/majority rate plus 2σ at the
task's own resolution (``TaskSpecEnriched.resolution``); a task with no
declared resolution keeps the chance floor and says so.

The control is the same base box measured over ``CONTROL_SEEDS`` seeds: a
control inside the band has no power, and its slice is refused before it is
priced instead of launching 73 unpriceable cells. Both instruments -- the
viability box (each primitive at its own defaults) and the comparison box (one
fixed knob for all) -- are published, never mixed.

This module is the binding half: it does not screen; ``sec_loop`` screens.
"""

from __future__ import annotations

import importlib
import math
from dataclasses import dataclass, fields, replace
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Final

from computronium.experiment.registry.task_registry import (
    TaskRegistry,
    primary_pass_bar,
)
from computronium.experiment.schema.axis import StructuralAxis, get_axis_spec
from computronium.experiment.schema.harvest import AXIS_CONFIG_CLASSES

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from computronium.experiment.kernel.evaluate import CellEvaluation
    from computronium.experiment.schema.coordinate import Schedule
    from computronium.experiment.sec_census import PrimitiveCensusEntry

__all__ = [
    "BASE_BOXES",
    "CONTROL_SEEDS",
    "SIGMAS",
    "BaseBox",
    "Calibration",
    "base_schedule",
    "calibrate_control",
    "family_of",
    "own_knob_params",
    "refusal_for",
    "resource_vector",
    "task_family",
]

#: How many seeds the base control runs at. One seed is a cell, not a control.
CONTROL_SEEDS: Final[int] = 3
#: The ruler's noise band, in standard errors of the difficulty rate.
SIGMAS: Final[float] = 2.0
#: Chance / 2σ is not a ruler: the difficulty rate sits at the trivial
#: predictor, and the band is the resolution of the measurement, not a target.


@dataclass(frozen=True, slots=True)
class BaseBox:
    """One family's calibrated base: the box a control and a cell share."""

    family: str
    task_id: str
    batch_size: int
    batch_limit: int
    epochs: int
    param_budget: int = 150_000


#: The declared base per task family. A family with no row has no base box and
#: its slice is refused before it is priced; the table is the decision, not a
#: fallback, so graph and sequence wait for their own measured base.
BASE_BOXES: Final[Mapping[str, BaseBox]] = MappingProxyType({
    "vision": BaseBox("vision", "mnist", 32, 375, 1),
    "tabular": BaseBox("tabular", "iris", 32, 0, 20),
})


@dataclass(frozen=True, slots=True)
class Calibration:
    """The control's power at one family's base box."""

    task_id: str
    bar: float
    control_mean: float
    control_std: float
    seeds: int

    @property
    def has_power(self) -> bool:
        """The control clears the bar: otherwise the slice measures noise."""
        return math.isfinite(self.control_mean) and self.control_mean > self.bar

    @property
    def sigma(self) -> float:
        """Between-seed spread of the control, at the bar's resolution."""
        return self.control_std / math.sqrt(self.seeds)


# Axis -> task family, declared once. A task family the axis vocabulary does
# not name maps to ``None`` and is not filtered (the axis binds elsewhere).
_FAMILY_OF_DOMAIN: Final[Mapping[str, str]] = MappingProxyType({
    "vision": "vision",
    "tabular": "tabular",
    "graph": "graph",
    "timeseries": "sequence",
    "lm": "sequence",
    "language": "sequence",
    "rl": "rl",
    "continual": "continual",
    "memory": "continual",
})


def task_family(task_id: str) -> str | None:
    """The task family a task belongs to, or ``None`` when undeclared."""
    try:
        domain = TaskRegistry().get(task_id).domain.value
    except Exception:
        return None
    return _FAMILY_OF_DOMAIN.get(str(domain))


def family_of(entry: PrimitiveCensusEntry) -> frozenset[str]:
    """The families a primitive's spec declares; empty means all families."""
    return frozenset(entry.task_families)


def refusal_for(entry: PrimitiveCensusEntry, task_id: str) -> str | None:
    """Why a primitive cannot run on the task, or ``None`` when it composes.

    The rule is the primitive's own ``task_families`` declaration against the
    task's family. An empty declaration composes everywhere; an unknown task
    family is not filtered, because the primitive's declaration is the only
    source and a missing domain is not a refusal.
    """
    families = family_of(entry)
    if not families:
        return None
    family = task_family(task_id)
    if family is None or family in families:
        return None
    return (
        f"`{entry.id}` composes no {family} task family "
        f"(declares {', '.join(sorted(families))}); the slice refuses it before "
        "it is priced (TODO95 S2)"
    )


def own_knob_params(axis: str, primitive: str) -> dict[str, object]:
    """The varied axis at its own declared config defaults (TODO95 S2).

    The base box shares one step size and one geometry width across
    primitives. This is the other instrument: the varied axis runs at the
    defaults its config classmethod declares, companions stay at the base.
    A primitive whose config factory needs structural arguments has no
    own-knob box of its own and returns ``{}``.
    """
    kind = StructuralAxis(axis)
    spec = get_axis_spec(kind, primitive)
    if spec is None:
        return {}
    module_name, class_name = AXIS_CONFIG_CLASSES[kind]
    config_cls = getattr(importlib.import_module(module_name), class_name)
    factory = getattr(config_cls, primitive, None)
    if not callable(factory):
        return {}
    try:
        config: Any = factory()
    except TypeError:
        # A structural factory (geometry) needs the task's shape: it has no
        # viability box of its own, so the base box stays.
        return {}
    structural = {param.name for param in spec.topology_params}
    own = {
        field.name: getattr(config, field.name)
        for field in fields(config)
        if field.name in spec.accepted_params and field.name not in structural
    }
    return {f"{kind.value}.{name}": value for name, value in own.items()}


def base_schedule(task_id: str, device: str = "auto") -> Schedule | None:
    """The family's declared base box as a schedule, or ``None`` when unpriced."""
    family = task_family(task_id)
    box = BASE_BOXES.get(family) if family is not None else None
    if box is None or box.task_id != task_id:
        return None
    from computronium.experiment.schema.coordinate import Schedule

    return Schedule(
        fidelity="L0",
        seed=0,
        n_seeds=1,
        epochs=box.epochs,
        batch_limit=box.batch_limit,
        batch_size=box.batch_size,
        budget_id=f"base-{family}",
        task_id=task_id,
        param_budget=box.param_budget,
        device=device,
        deterministic=True,
        num_workers=0,
        precision="fp32",
        checkpoint_every_n=0,
    )


def calibrate_control(
    schedule: Schedule,
    *,
    evaluate: Callable[..., CellEvaluation] | None = None,
) -> Calibration | None:
    """Measure the base control over ``CONTROL_SEEDS`` seeds.

    Args:
        schedule: The base box; only its seed varies between runs.
        evaluate: The evaluator (``evaluate_cell`` by default), injectable so
            the calibration rule is testable without a training run.

    Returns:
        The control's power, or ``None`` when the task declares no bar.
    """
    bar = primary_pass_bar(TaskRegistry().get(schedule.task_id))
    if bar is None:
        return None
    if evaluate is None:
        from computronium.experiment.kernel.evaluate import evaluate_cell

        runner: Callable[..., CellEvaluation] = evaluate_cell
    else:
        runner = evaluate
    from computronium.experiment.sec_loop import _AXIS_DEFAULTS, _coordinate

    coordinate = _coordinate(dict(_AXIS_DEFAULTS))
    values = [
        float(
            runner(coordinate, replace(schedule, seed=seed, n_seeds=1)).metrics.get(
                bar.metric_key, math.nan
            )
        )
        for seed in range(CONTROL_SEEDS)
    ]
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return Calibration(
        task_id=schedule.task_id,
        bar=bar.value,
        control_mean=mean,
        control_std=math.sqrt(variance),
        seeds=CONTROL_SEEDS,
    )


def resource_vector(metrics: Mapping[str, float]) -> dict[str, float | None]:
    """The cost beside the number: walltime, memory and energy per batch."""
    memory = metrics.get("memory_usage")
    energy = metrics.get("energy_per_step")
    return {
        "memory_mb": None if memory is None else float(memory),
        "energy_per_batch": None if energy is None else float(energy),
    }
