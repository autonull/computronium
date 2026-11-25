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

import hashlib
import importlib
import json
import math
import time
from dataclasses import dataclass, fields, replace
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Final

from computronium.experiment.kernel.evaluate import task_shape
from computronium.experiment.registry.task_registry import (
    PassBar,
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
#: fallback. ``base_coordinate`` is the one source of the family's axes: a
#: screen, a calibration and the P3 slice all compose from it.
BASE_BOXES: Final[Mapping[str, BaseBox]] = MappingProxyType({
    "vision": BaseBox(
        "vision",
        "mnist",
        32,
        375,
        1,
        base_coordinate={
            "geometry": "feedforward",
            "geometry.input_hw": (28, 28),
            "geometry.in_channels": 1,
        },
    ),
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
        "delayed_cue",
        32,
        0,
        10,
        base_coordinate={"geometry": "recurrent"},
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
        40,
        1,
        base_coordinate={
            "substrate": "neuromorphic",
            "dynamics": "energy_minimization",
            "geometry.input_hw": (28, 28),
            "geometry.in_channels": 1,
        },
    ),
    "lm": BaseBox(
        "lm",
        "tiny_shakespeare",
        32,
        0,
        3,
        param_budget=600_000,
        base_coordinate={
            "geometry": "causal_transformer",
            "geometry.vocab_size": 65,
            "geometry.d_model": 256,
            "geometry.n_layers": 4,
            "geometry.n_heads": 4,
            "geometry.seq_len": 128,
            "geometry.patch_size": 0,
        },
    ),
    "quantum": BaseBox(
        "quantum",
        "mnist",
        32,
        375,
        1,
        base_coordinate={
            "substrate": "quantum",
            "geometry": "feedforward",
            "dynamics": "instantaneous",
            "credit": "gradient",
            "update": "euclidean",
            "geometry.input_hw": (28, 28),
            "geometry.in_channels": 1,
        },
    ),
    "photonic": BaseBox(
        "photonic",
        "mnist",
        32,
        375,
        1,
        base_coordinate={
            "substrate": "photonic",
            "geometry": "feedforward",
            "dynamics": "instantaneous",
            "credit": "gradient",
            "update": "euclidean",
            "geometry.input_hw": (28, 28),
            "geometry.in_channels": 1,
        },
    ),
    "analog": BaseBox(
        "analog",
        "memristor_simulation",
        32,
        375,
        1,
        base_coordinate={
            "substrate": "memristive",
            "geometry": "feedforward",
            "dynamics": "instantaneous",
            "credit": "gradient",
            "update": "euclidean",
            "geometry.input_hw": (28, 28),
            "geometry.in_channels": 1,
        },
    ),
    # Energy-minimization variants for credits requiring settle (TODO99 #3)
    "graph_energy_min": BaseBox(
        "graph",
        "cora",
        1,
        1,
        200,
        param_budget=200_000,
        base_coordinate={
            "geometry": "graph",
            "dynamics": "energy_minimization",
            "credit": "gradient",
            "update": "euclidean",
        },
    ),
    "sequence_energy_min": BaseBox(
        "sequence",
        "delayed_cue",
        32,
        0,
        10,
        base_coordinate={
            "geometry": "recurrent",
            "dynamics": "energy_minimization",
        },
    ),
    "continual_energy_min": BaseBox(
        "continual",
        "copy_task",
        16,
        0,
        5,
        base_coordinate={
            "plasticity": "null",
            "dynamics": "energy_minimization",
        },
    ),
})


@dataclass(frozen=True, slots=True)
class Calibration:
    """The control's power at one family's base box.

    ``bar`` is the task's ``PassBar`` itself, so the direction, metric key and
    floor travel with the number instead of a second copy of the comparison.
    """

    task_id: str
    bar: PassBar
    control_mean: float
    control_std: float
    seeds: int
    cell_seconds: float = 0.0
    param_count: int = 0
    replay: str = ""

    @property
    def has_power(self) -> bool:
        """The control clears the bar: otherwise the slice measures noise."""
        from computronium.experiment.kernel.evaluate import clears_task_bar

        return clears_task_bar(self.bar, {self.bar.metric_key: self.control_mean})

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


def _geometry_defaults(  # ruff: ignore[complex-structure, too-many-return-statements, too-many-branches]
    factory: Callable[..., Any], primitive: str, task_id: str | None
) -> Any | None:
    """The geometry factory at its declared defaults and the task's own shape.

    Structural arguments are task facts (TODO104 A10): a topology that needs an
    extent or channels the task does not declare is refused by its builder, so
    this returns ``None`` rather than inventing one. A graph's connectivity is
    the task's data (``compose_configs`` extracts it), never a literal chain.
    """
    from computronium.experiment.kernel._geometry_builders import (
        channel_count,
        spatial_extent,
    )

    if task_id is None:
        return None
    try:
        shape = task_shape(task_id, "cpu")
    except Exception:  # ruff: ignore[blind-except] - a shape-less task has no defaults
        return None
    input_dim = math.prod(shape.input_shape)
    output_dim = shape.output_dim
    spatial = len(shape.input_shape) > 1
    channels = channel_count(shape.input_shape)
    hw = spatial_extent(shape.input_shape)
    match primitive:
        case "feedforward" | "recurrent" | "routing":
            return factory(
                input_dim=input_dim, output_dim=output_dim, hidden_dims=(128,)
            )
        case "attention":
            return factory(
                input_dim=input_dim, output_dim=output_dim, hidden_dim=128, num_layers=2
            )
        case "causal_transformer":
            if not spatial:
                return None
            patch = 4
            return factory(
                vocab_size=output_dim,
                d_model=128,
                n_layers=2,
                n_heads=8,
                seq_len=(hw[0] // patch) * (hw[1] // patch),
                patch_size=patch,
                patch_embed_dim=128,
                image_hw=hw,
                in_channels=channels,
            )
        case "tile" | "tile_mesh":
            return factory(input_dim=input_dim, output_dim=output_dim, num_layers=2)
        case "conv":
            if not spatial:
                return None
            return factory(
                input_dim=input_dim,
                output_dim=output_dim,
                in_channels=channels,
                input_hw=hw,
                pool_hw=(max(1, hw[0] // 4), max(1, hw[1] // 4)),
                conv_channels=(32, 64),
            )
        case "nca":
            if not spatial:
                return None
            return factory(
                channels=channels, hidden=32, grid_hw=hw, output_dim=output_dim
            )
        case "spatial_lattice":
            if len(shape.input_shape) < 3:
                return None
            return factory(
                input_dim=input_dim,
                output_dim=output_dim,
                lattice_dims=tuple(shape.input_shape[-3:]),
            )
        case "ntm":
            return factory(input_dim=input_dim, output_dim=output_dim)
        case _:
            return None


def own_knob_params(
    axis: str, primitive: str, task_id: str | None = None
) -> dict[str, object]:
    """The varied axis at its own declared config defaults (TODO95 S2).

    The base box shares one step size and one geometry width across
    primitives. This is the other instrument: the varied axis runs at the
    defaults its config classmethod declares, companions stay at the base.
    A geometry primitive's structural arguments are the task's own shape; a
    topology the task cannot declare gets no defaults here.
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

    # For geometry axis, the factory needs structural arguments from the task
    if kind == StructuralAxis.GEOMETRY:
        config = _geometry_defaults(factory, primitive, task_id)
        if config is None:
            return {}
    else:
        try:
            config: Any = factory()
        except TypeError:
            return {}

    own = {}

    # For plasticity axis, hyperparameters are stored in consolidation_config dict
    if kind == StructuralAxis.PLASTICITY and config.consolidation_config:
        for param_name in spec.accepted_params:
            if param_name in config.consolidation_config:
                own[param_name] = config.consolidation_config[param_name]
    else:
        # For other axes, the factory signature parameters are the true knobs
        # (config fields may have different names, e.g., pepita: gamma -> feedback_scale)
        import inspect

        factory_params = inspect.signature(factory).parameters
        for param_name, param in factory_params.items():
            if param_name in spec.accepted_params:
                # Use the default value from the factory signature
                if param.default is not inspect.Parameter.empty:
                    own[param_name] = param.default
                # Also check if config has a field with this name
                if hasattr(config, param_name):
                    own[param_name] = getattr(config, param_name)
        # Also include config fields that are in accepted_params
        for field in fields(config):
            if field.name in spec.accepted_params:
                own[field.name] = getattr(config, field.name)

    return {f"{kind.value}.{name}": value for name, value in own.items()}


def base_schedule(task_id: str, device: str = "auto") -> Schedule | None:
    """The family's declared base box as a schedule, or ``None`` when unpriced."""
    family = base_family(task_id)
    box = BASE_BOXES.get(family) if family is not None else None
    if box is None:
        return None
    # Use the family's base box task_id for the schedule params (epochs, batch_size, etc.)
    # but keep the original task_id for the run identification.
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

    The base coordinate is the family box's own declaration: the composition is
    ``sec_loop._base_axes``, so a calibration and a screen cannot run at
    different axes.

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
    from computronium.experiment.sec_loop import _base_axes, _coordinate

    coordinate = _coordinate(_base_axes(schedule.task_id))
    values: list[float] = []
    seconds: list[float] = []
    evaluations: list[CellEvaluation] = []
    for seed in range(CONTROL_SEEDS):
        started = time.monotonic()
        evaluation = runner(coordinate, replace(schedule, seed=seed, n_seeds=1))
        seconds.append(time.monotonic() - started)
        evaluations.append(evaluation)
        values.append(float(evaluation.metrics.get(bar.metric_key, math.nan)))
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    cell_seconds = sum(seconds) / len(seconds)
    return Calibration(
        task_id=schedule.task_id,
        bar=bar,
        control_mean=mean,
        control_std=math.sqrt(variance),
        seeds=CONTROL_SEEDS,
        cell_seconds=cell_seconds,
        param_count=evaluations[0].param_count,
        replay=calibration_replay(schedule.task_id, schedule, bar, values),
    )


def calibration_replay(
    task_id: str,
    schedule: Schedule,
    bar: PassBar,
    values: list[float],
) -> str:
    """The replay identity of a measured control.

    The box, the ruler and the three numbers are the record; a rerun that
    changes any of them is a different calibration, not a confirmation. The
    cost is beside the number, not part of its identity.
    """
    payload = {
        "task": task_id,
        "schedule": schedule.to_dict(),
        "bar": {
            "metric_key": bar.metric_key,
            "direction": bar.direction,
            "value": bar.value,
            "floor": bar.floor,
            "resolution": bar.resolution,
            "sigma": bar.sigma,
        },
        "seeds": values,
    }
    encoded = json.dumps(payload, sort_keys=True, default=str).encode()
    return hashlib.sha256(encoded).hexdigest()[:16]


def resource_vector(metrics: Mapping[str, float]) -> dict[str, float | None]:
    """The cost beside the number: walltime, memory and energy per batch."""
    memory = metrics.get("memory_usage")
    energy = metrics.get("energy_per_step")
    return {
        "memory_mb": None if memory is None else float(memory),
        "energy_per_batch": None if energy is None else float(energy),
    }
