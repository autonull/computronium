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
    "TASK_FAMILIES",
    "BaseBox",
    "Calibration",
    "base_family",
    "base_schedule",
    "calibrate_control",
    "family_of",
    "own_knob_params",
    "refusal_for",
    "resource_vector",
    "task_families",
]

#: Every task family the primitive layer declares, in one place. A family in
#: this tuple must have a ``BASE_BOXES`` row and a calibrated control before a
#: screen can run on it; ``scripts/audit.py`` reads this tuple as the gate.
TASK_FAMILIES: Final[tuple[str, ...]] = (
    "vision",
    "tabular",
    "graph",
    "sequence",
    "continual",
    "rl",
    "scientific",
    "neuromorphic",
    "lm",
)

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
    base_coordinate: dict[str, str] | None = None


#: The declared base per task family. A family with no row has no base box and
#: its slice is refused before it is priced; the table is the decision, not a
#: fallback, so graph and sequence wait for their own measured base.
BASE_BOXES: Final[Mapping[str, BaseBox]] = MappingProxyType({
    "vision": BaseBox("vision", "mnist", 32, 375, 1),
    "tabular": BaseBox("tabular", "iris", 32, 0, 20),
    "graph": BaseBox(
        "graph",
        "cora",
        1,
        1,
        200,
        param_budget=200_000,
        base_coordinate={
            "geometry": "graph",
            "credit": "gradient",
            "update": "euclidean",
        },
    ),
    "sequence": BaseBox(
        "sequence",
        "char_ngram",
        32,
        0,
        10,
        base_coordinate={"geometry": "recurrent", "dynamics": "instantaneous"},
    ),
    "continual": BaseBox(
        "continual",
        "copy_task",
        16,
        0,
        5,
        base_coordinate={"plasticity": "null"},
    ),
    "rl": BaseBox(
        "rl",
        "cartpole",
        8,
        0,
        5,
        base_coordinate={"geometry": "recurrent"},
    ),
    "scientific": BaseBox(
        "scientific",
        "lorenz_state",
        32,
        0,
        10,
        base_coordinate={"geometry": "feedforward"},
    ),
    "neuromorphic": BaseBox(
        "neuromorphic",
        "spiking_mnist",
        32,
        0,
        5,
        base_coordinate={"substrate": "neuromorphic"},
    ),
    "lm": BaseBox(
        "lm",
        "tiny_shakespeare",
        32,
        0,
        3,
        param_budget=600_000,
        base_coordinate={"geometry": "causal_transformer"},
    ),
})


#: Family-specific base coordinate overrides. Merged with _AXIS_DEFAULTS.
BASE_COORDINATES: Final[Mapping[str, dict[str, str]]] = MappingProxyType({
    "graph": {"geometry": "graph"},
    "sequence": {"geometry": "recurrent", "dynamics": "instantaneous"},
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


def task_families(task_id: str) -> tuple[str, ...]:
    """The families a task declares, in base-preference order.

    An undeclared or unknown task has no families, so no family filter applies:
    a missing declaration is not a refusal.
    """
    try:
        return TaskRegistry().get(task_id).task_families
    except Exception:
        return ()


def base_family(task_id: str) -> str | None:
    """The declared family whose base box is this task, else the first declared."""
    families = task_families(task_id)
    for family in families:
        box = BASE_BOXES.get(family)
        if box is not None and box.task_id == task_id:
            return family
    return families[0] if families else None


def family_of(entry: PrimitiveCensusEntry) -> frozenset[str]:
    """The families a primitive's spec declares; empty means all families."""
    return frozenset(entry.task_families)


def refusal_for(entry: PrimitiveCensusEntry, task_id: str) -> str | None:
    """Why a primitive cannot run on the task, or ``None`` when it composes.

    The rule is the primitive's own ``task_families`` declaration against the
    task's declared families: one shared family composes the pair (split_mnist
    is both a vision and a continual task). An empty declaration composes
    everywhere; an undeclared task family is not filtered, because the
    primitive's declaration is the only source.
    """
    declared = family_of(entry)
    if not declared:
        return None
    families = frozenset(task_families(task_id))
    if not families or declared & families:
        return None
    return (
        f"`{entry.id}` composes no {' or '.join(sorted(families))} task family "
        f"(declares {', '.join(sorted(declared))}); the slice refuses it before "
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
    family = base_family(task_id)
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
    family: str | None = None,
) -> Calibration | None:
    """Measure the base control over ``CONTROL_SEEDS`` seeds.

    Args:
        schedule: The base box; only its seed varies between runs.
        evaluate: The evaluator (``evaluate_cell`` by default), injectable so
            the calibration rule is testable without a training run.
        family: Optional task family for family-specific base coordinate.

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

    # Use family-specific base coordinate if available
    base_axes = dict(_AXIS_DEFAULTS)
    if family is not None and family in BASE_COORDINATES:
        base_axes.update(BASE_COORDINATES[family])
    coordinate = _coordinate(base_axes)
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
