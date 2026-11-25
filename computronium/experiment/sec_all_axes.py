"""Rung 1 & 2 runner for all 6 axes (Credit, Dynamics, Geometry, Update, Plasticity, Substrate).

This module generalizes the credit-only runner in sec_deep_dive.py to handle
any structural axis. It runs:
- Rung 1: 3-point ladder on the axis's primary knob (1 epoch, 1 seed)
- Rung 2: Paired comparison (n=5 seeds) at best ladder point vs axis default
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import os
import time
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Final

from computronium.experiment.schema.axis import (
    AXES_REGISTRIES,
    StructuralAxis,
    get_axis_spec,
)
from computronium.experiment.sec_loop import (
    _measure,
    base_schedule,
    screen_coordinate,
)
from computronium.experiment.sec_pilot import BASE_BOXES, base_family, own_knob_params
from computronium.validation.preregistration import (
    DEFAULT_ALPHA,
    EffectSizeRegistration,
    ThresholdRegistration,
    paired_comparison,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from computronium.experiment.schema.coordinate import Schedule

__all__ = [
    "AXIS_DEFAULTS",
    "AXIS_PRIMARY_KNOB",
    "preregister_axis_primitives",
    "run_axis_rung1_all",
    "run_axis_rung2_all",
    "run_rung1_ladder",
    "run_rung2_comparison",
]

# Ladder factors: 0.1x, 1.0x, 10.0x of declared default
LADDER_FACTORS: Final[tuple[float, ...]] = (0.1, 1.0, 10.0)
# Cooperative per-cell training budget in seconds (TODO104 A3). A cancelled
# ``asyncio.to_thread`` keeps its thread and the GPU; a deadline passed into the
# trainer stops the cell itself and returns a record. 0 disables the deadline.
MEASURE_BUDGET_S: float = float(os.environ.get("SEC_MEASURE_BUDGET_S", "0") or 0.0)
# Paired seeds per arm
CLAIM_SEEDS: Final[int] = 5
# Minimum effect size per task family (Cohen's d)
MIN_EFFECT_SIZE_BY_FAMILY: dict[str, float] = {
    "vision": 0.8,
    "tabular": 0.5,
    "graph": 0.5,
    "sequence": 0.8,
    "continual": 0.8,
    "rl": 0.8,
    "scientific": 0.5,
    "lm": 0.5,
    "neuromorphic": 0.8,
    "quantum": 0.8,
    "photonic": 0.8,
}

# Primary knob per primitive per axis (from TODO100 Rung 1 results or config defaults)
# These will be populated from config factories at runtime
AXIS_PRIMARY_KNOB: dict[str, dict[str, str]] = {}

# Axis default primitives for paired comparison (the "control" at each axis)
AXIS_DEFAULTS: Final[MappingProxyType[str, str]] = MappingProxyType({
    "credit": "gradient",
    "dynamics": "instantaneous",
    "geometry": "feedforward",
    "update": "euclidean",
    "plasticity": "null",
    "substrate": "digital",
})

# Task family -> example task_id (cheapest task in family)
FAMILY_TO_TASK: Final[MappingProxyType[str, str]] = MappingProxyType({
    "vision": "mnist",
    "tabular": "iris",
    "graph": "cora",
    "sequence": "sequential_mnist",
    "continual": "split_mnist",
    "rl": "cartpole",
    "scientific": "pendulum",
    "lm": "char_ngram",
    "neuromorphic": "spiking_mnist",
    "quantum": "quantum_circuit_learning",
    "photonic": "optical_mnist_sim",
    "analog": "memristor_simulation",
})


@dataclass(frozen=True, slots=True)
class LadderRung:
    """One point of the 3-point ladder."""

    factor: float
    value: float
    status: str
    val_acc: float | None
    walltime_s: float | None
    replay_hash: str | None
    box: dict[str, Any]
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "factor": self.factor,
            "value": self.value,
            "status": self.status,
            "val_acc": self.val_acc,
            "walltime_s": self.walltime_s,
            "replay_hash": self.replay_hash,
            "box": self.box,
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class PairedCell:
    """One arm of the paired comparison."""

    arm: str  # treatment | control
    factor: float
    seed: int
    status: str
    val_acc: float | None
    loss: float | None
    walltime_s: float | None
    replay_hash: str | None
    box: dict[str, Any]
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "arm": self.arm,
            "factor": self.factor,
            "seed": self.seed,
            "status": self.status,
            "val_acc": self.val_acc,
            "loss": self.loss,
            "walltime_s": self.walltime_s,
            "replay_hash": self.replay_hash,
            "box": self.box,
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class RungResult:
    """Result of Rung 1 + Rung 2 for one primitive."""

    axis: str
    primitive: str
    task_id: str
    task_family: str
    rung1_ladder: list[dict[str, Any]]
    best_rung: dict[str, Any] | None
    rung1_verdict: str  # viable | marginal | refused | defect
    rung2_cells: list[dict[str, Any]] | None
    rung2_effect: dict[str, Any] | None
    rung2_verdict: str | None  # claim | coordinate | defect | None
    walltime_s: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "axis": self.axis,
            "primitive": self.primitive,
            "task_id": self.task_id,
            "task_family": self.task_family,
            "rung1_ladder": self.rung1_ladder,
            "best_rung": self.best_rung,
            "rung1_verdict": self.rung1_verdict,
            "rung2_cells": self.rung2_cells,
            "rung2_effect": self.rung2_effect,
            "rung2_verdict": self.rung2_verdict,
            "walltime_s": self.walltime_s,
        }


def _get_primitives_for_axis(axis: str) -> list[str]:
    """Get all primitive IDs for a given axis."""
    axis_enum = StructuralAxis(axis.lower())
    return list(AXES_REGISTRIES[axis_enum].keys())


# Axis name mapping from StructuralAxis to registry key prefix
_AXIS_REGISTRY_PREFIX: Final[Mapping[str, str]] = MappingProxyType({
    "substrate": "substrate",
    "geometry": "geometry",
    "dynamics": "state_dynamics",
    "plasticity": "plasticity",
    "credit": "credit_assignment",
    "update": "parameter_update",
})


def _get_task_families_for_primitive(axis: str, primitive: str) -> list[str]:
    """Get declared task families for a primitive."""
    from computronium.primitives.registry import _TASK_FAMILIES

    prefix = _AXIS_REGISTRY_PREFIX.get(axis, axis)
    key = f"primitive.{prefix}.{primitive}"
    families = _TASK_FAMILIES.get(key, [])
    return list(families) if families else []


#: Knobs whose domain is integer: a ladder point or a comparison box rounds
#: them, so one declaration serves the ladder and the paired comparison.
INT_KNOBS: Final[frozenset[str]] = frozenset({
    "max_steps",
    "hidden_dim",
    "depth",
    "width",
    "num_layers",
    "num_experts",
    "top_k",
    "conv_channels",
    "kernel_size",
    "num_heads",
    "seq_len",
    "lattice_dims",
    "mem_slots",
    "mem_width",
    "grid_hw",
    "neurons_per_tile",
    "tiles_per_layer",
})


def preferred_task_family(families: list[str]) -> str | None:
    """The family a mechanism map measures on (TODO104 A17).

    An axis rule's declared families say where the row is *available*, not
    which one a map compares: a family the base box cannot express (a 4096-wide
    head over a 2-class split) measures the box, not the mechanism. ``vision``
    is the common, coherent box; any declared family is the fallback.
    """
    if not families:
        return None
    return "vision" if "vision" in families else families[0]


def _accepted_knobs(axis: str, primitive: str) -> frozenset[str]:
    """The knobs this axis' primitive reads (a harvested fact, TODO104 A4).

    A box that carries a knob the primitive does not accept fails loud at
    composition ("inactive hyperparameters"), so a ladder must vary only an
    accepted knob and never ship a dead one.
    """
    spec = get_axis_spec(StructuralAxis(axis), primitive)
    return spec.accepted_params if spec is not None else frozenset()


def _declared_reads(axis: str, primitive: str) -> frozenset[str] | None:
    """The config fields a rule declares it reads (``reads``), or ``None``.

    A rule that declares ``reads`` names the fields its own output depends on,
    so the ladder must sweep one of them: sweeping a field the rule ignores
    trained the identical cell at every rung (measured 2026-11-25 — ``gradient``
    at 0.015x..22.65x of ``feedback_scale`` returned val_acc 0.9172 four
    times). An empty set means the rule reads no axis knob at all: measure its
    declared default once instead of sweeping a dead field.
    """
    import importlib

    from computronium.primitives.registry import _CONFIG_FACTORIES, _ONTOLOGY_CLASSES

    prefix = _AXIS_REGISTRY_PREFIX.get(axis, axis)
    dotted = _ONTOLOGY_CLASSES.get(f"primitive.{prefix}.{primitive}")
    factory_path = _CONFIG_FACTORIES.get(f"primitive.{prefix}.{primitive}")
    if not dotted or not factory_path:
        return None
    module_name, _, class_name = dotted.rpartition(".")
    module = importlib.import_module(module_name)
    rule_class = getattr(module, class_name, None)
    reads = getattr(rule_class, "reads", None)
    if reads is None:
        return None
    parts = factory_path.split(".")
    config_module = importlib.import_module(".".join(parts[:-2]))
    config_cls = getattr(config_module, parts[-2])
    try:
        config = getattr(config_cls, parts[-1])()
        declared = reads(config)
    except Exception:
        return None
    return None if declared is None else frozenset(declared)


def _get_primary_knob(
    axis: str, primitive: str, task_id: str | None = None
) -> tuple[str, float] | None:
    """Get the primary knob and its default for a primitive.

    Checks both own_knob_params (hyperparameters) and config class hyperparameters().
    """
    # First try hyperparameters (own_knob_params)
    params = own_knob_params(axis, primitive, task_id=task_id)
    # Integer-typed params that should be converted from float
    int_params = {
        "max_steps",
        "hidden_dim",
        "depth",
        "width",
        "num_layers",
        "num_experts",
        "top_k",
        "conv_channels",
        "kernel_size",
        "num_heads",
        "seq_len",
        "lattice_dims",
        "mem_slots",
        "mem_width",
        "grid_hw",
        "neurons_per_tile",
        "tiles_per_layer",
    }
    accepted = _accepted_knobs(axis, primitive)
    declared_reads = _declared_reads(axis, primitive)
    for name in [
        "step_size",
        "max_steps",
        "hidden_dim",
        "depth",
        "width",
        "num_layers",
        "momentum",
        "trace_decay",
        "noise_level",
        "sparsity",
        "feedback_scale",
        "beta",
        "readout_scale",
        "fd_step",
        "estimator_samples",
        "aux_head_scale",
        "lr",
    ]:
        if accepted and name not in accepted:
            continue
        if declared_reads is not None and name not in declared_reads:
            continue
        key = f"{axis}.{name}"
        value = params.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        if value > 0:
            if name in int_params:
                return key, round(value)
            return key, float(value)

    # If own_knob_params returns empty, check config class's hyperparameters() method
    from computronium.primitives.registry import _CONFIG_FACTORIES

    key = f"primitive.{axis}.{primitive}"
    factory_path = _CONFIG_FACTORIES.get(key)
    if factory_path:
        parts = factory_path.split(".")
        module_name = ".".join(parts[:-2])
        class_name = parts[-2]
        import importlib

        module = importlib.import_module(module_name)
        config_cls = getattr(module, class_name)
        if hasattr(config_cls, "hyperparameters"):
            hp_dict = config_cls.hyperparameters(primitive)
            # Check the preferred knobs for this axis from LADDER_KNOBS
            from computronium.experiment.sec_deep_dive import LADDER_KNOBS

            for name in LADDER_KNOBS.get(axis, ()):
                if name in hp_dict:
                    hp_spec = hp_dict[name]
                    # Check if available for this primitive
                    avail = True
                    avail_pred = hp_spec.get("availability")
                    if avail_pred is not None:
                        from computronium.experiment.legality.dsl import evaluate
                        from computronium.experiment.schema.coordinate import Coordinate
                        from computronium.experiment.schema.harvest import (
                            CoordinateContext,
                        )

                        # Build coordinate with the actual primitive for the axis being tested
                        axes = {
                            "substrate": "digital",
                            "geometry": "feedforward",
                            "dynamics": "instantaneous",
                            "plasticity": "null",
                            "credit": "gradient",
                            "update": "euclidean",
                        }
                        axes[axis] = (
                            primitive  # Use the actual primitive for availability check
                        )
                        coord = Coordinate(
                            substrate=axes["substrate"],
                            geometry=axes["geometry"],
                            dynamics=axes["dynamics"],
                            plasticity=axes["plasticity"],
                            credit=axes["credit"],
                            update=axes["update"],
                            params={},
                        )
                        ctx = CoordinateContext(coord)
                        avail = evaluate(avail_pred, ctx)
                    if not avail:
                        continue
                    # Get default from domain
                    domain = hp_spec.get("domain")
                    if domain:
                        if isinstance(domain, tuple) and len(domain) >= 2:
                            domain_type = domain[2] if len(domain) > 2 else "linear"
                            if domain_type == "log":
                                import math

                                return f"{axis}.{name}", math.sqrt(
                                    domain[0] * domain[1]
                                )
                            elif domain_type in {"log_int", "int"}:
                                import math

                                if domain_type == "log_int":
                                    val = math.sqrt(domain[0] * domain[1])
                                else:
                                    val = (domain[0] + domain[1]) / 2
                                return f"{axis}.{name}", round(val)
                            else:
                                return f"{axis}.{name}", (domain[0] + domain[1]) / 2
                        elif isinstance(domain, list):
                            return f"{axis}.{name}", float(domain[0])

    # For structural axes (geometry), check topology_params from axis spec
    from computronium.experiment.schema.axis import StructuralAxis, get_axis_spec

    axis_enum = StructuralAxis(axis.lower())
    spec = get_axis_spec(axis_enum, primitive)
    if spec and spec.topology_params:
        for hp in spec.topology_params:
            name = hp.name
            key = f"primitive.{axis}.{primitive}"
            factory_path = _CONFIG_FACTORIES.get(key)
            if factory_path:
                parts = factory_path.split(".")
                module_name = ".".join(parts[:-2])
                class_name = parts[-2]
                method_name = parts[-1]
                import importlib

                module = importlib.import_module(module_name)
                config_cls = getattr(module, class_name)
                factory = getattr(config_cls, method_name, None)
                if callable(factory):
                    try:
                        config = factory()
                        if hasattr(config, name):
                            value = getattr(config, name)
                            if isinstance(value, (int, float)) and value > 0:
                                return f"{axis}.{name}", float(value)
                    except TypeError:
                        pass
    return None


# Default axes for base box
_DEFAULT_AXES: dict[str, str] = {
    "substrate": "digital",
    "geometry": "feedforward",
    "dynamics": "instantaneous",
    "plasticity": "null",
    "credit": "gradient",
    "update": "euclidean",
}


def _build_axis_box(axis: str, primitive: str, task_id: str) -> dict[str, Any]:
    """Build the base box for an axis primitive on a task.

    For axes with structural arguments (geometry, some dynamics), the config
    factory needs task shape. We just set the axis primitive and let the
    composition system handle structural params at compose time.
    Only includes hyperparams that are available for the given primitive.
    """
    # Find the task's family and use that family's base box task_id for the schedule
    family = base_family(task_id)
    if not family:
        raise ValueError(f"{task_id} declares no task family")

    base_box = BASE_BOXES.get(family)
    if not base_box:
        raise ValueError(f"Family {family} has no base box")

    base_coord = base_box.base_coordinate
    schedule_task_id = base_box.task_id

    schedule = base_schedule(schedule_task_id, "auto")
    if schedule is None:
        raise ValueError(
            f"Base task {schedule_task_id} for family {family} declares no base box"
        )

    # Start with base schedule
    box = schedule.to_dict()
    box["device"] = "cuda"
    box["task"] = task_id  # Keep original task_id for the run

    # Structural axes that come from base_coordinate (not hyperparameters)

    # Set axes: use base_coordinate for structural axes, _DEFAULT_AXES for others
    for ax_name, default in _DEFAULT_AXES.items():
        if base_coord and ax_name in base_coord:
            box[ax_name] = base_coord[ax_name]
        else:
            box[ax_name] = default

    # Override the target axis (unless it's structural and we're testing a different primitive)
    if axis == "credit":
        box["credit"] = primitive
    elif axis == "dynamics":
        box["dynamics"] = primitive
    elif axis == "geometry":
        box["geometry"] = primitive
    elif axis == "update":
        box["update"] = primitive
    elif axis == "plasticity":
        box["plasticity"] = primitive
    elif axis == "substrate":
        box["substrate"] = primitive

    # Get hyperparams from config class's hyperparameters() method
    from computronium.experiment.legality.dsl import evaluate
    from computronium.experiment.schema.coordinate import Coordinate
    from computronium.experiment.schema.harvest import CoordinateContext
    from computronium.primitives.registry import _CONFIG_FACTORIES

    # Create coordinate for availability checking
    axes = {
        "substrate": box.get("substrate", "digital"),
        "geometry": box.get("geometry", "feedforward"),
        "dynamics": box.get("dynamics", "instantaneous"),
        "plasticity": box.get("plasticity", "null"),
        "credit": box.get("credit", "gradient"),
        "update": box.get("update", "euclidean"),
    }
    coord = Coordinate(
        substrate=axes["substrate"],
        geometry=axes["geometry"],
        dynamics=axes["dynamics"],
        plasticity=axes["plasticity"],
        credit=axes["credit"],
        update=axes["update"],
        params={},
    )
    ctx = CoordinateContext(coord)

    # Get hyperparams from config factory's class for ALL axes
    for ax_name, ax_primitive in axes.items():
        prefix = _AXIS_REGISTRY_PREFIX.get(ax_name, ax_name)
        key = f"primitive.{prefix}.{ax_primitive}"
        factory_path = _CONFIG_FACTORIES.get(key)
        if factory_path:
            parts = factory_path.split(".")
            module_name = ".".join(parts[:-2])
            class_name = parts[-2]
            method_name = parts[-1]
            import importlib

            module = importlib.import_module(module_name)
            config_cls = getattr(module, class_name)
            # Get available hyperparameters from hyperparameters() FIRST
            available_fields = set()
            if hasattr(config_cls, "hyperparameters"):
                hp_dict = config_cls.hyperparameters(ax_primitive)
                for hp_name, hp_spec in hp_dict.items():
                    avail = True
                    avail_pred = hp_spec.get("availability")
                    if avail_pred is not None:
                        avail = evaluate(avail_pred, ctx)
                    if avail:
                        available_fields.add(hp_name)
            # Call the config factory method to get actual defaults for available fields
            if hasattr(config_cls, method_name):
                try:
                    config = getattr(config_cls, method_name)()
                    for field_name in dir(config):
                        if not field_name.startswith("_") and not callable(
                            getattr(config, field_name)
                        ):
                            # Only add if this field is available for the current primitive
                            if field_name in available_fields or field_name in {
                                "update_type",
                                "credit_type",
                                "dynamics_type",
                                "substrate_type",
                                "geometry_type",
                                "plasticity_type",
                            }:
                                value = getattr(config, field_name)
                                if isinstance(value, (int, float, bool, str)):
                                    box[f"{ax_name}.{field_name}"] = value
                except Exception:
                    pass
            # For available hyperparams not set by config factory, add from domain
            if hasattr(config_cls, "hyperparameters"):
                hp_dict = config_cls.hyperparameters(ax_primitive)
                for hp_name, hp_spec in hp_dict.items():
                    if hp_name not in available_fields:
                        continue  # Skip unavailable hyperparams
                    if f"{ax_name}.{hp_name}" not in box:
                        domain = hp_spec.get("domain")
                        if domain:
                            if isinstance(domain, tuple) and len(domain) >= 2:
                                domain_type = domain[2] if len(domain) > 2 else "linear"
                                if domain_type == "log":
                                    import math

                                    box[f"{ax_name}.{hp_name}"] = math.sqrt(
                                        domain[0] * domain[1]
                                    )
                                elif domain_type in {"log_int", "int"}:
                                    import math

                                    if domain_type == "log_int":
                                        val = math.sqrt(domain[0] * domain[1])
                                    else:
                                        val = (domain[0] + domain[1]) / 2
                                    box[f"{ax_name}.{hp_name}"] = round(val)
                                else:
                                    box[f"{ax_name}.{hp_name}"] = (
                                        domain[0] + domain[1]
                                    ) / 2
                            elif isinstance(domain, list):
                                box[f"{ax_name}.{hp_name}"] = domain[0]

    # Axis-specific extra params for the test axis
    if axis == "dynamics" and primitive in {"energy_minimization", "pc_alm"}:
        box["dynamics.max_steps"] = 10
        box["dynamics.step_size"] = 0.1

    # A box may carry a dead knob for the treatment primitive (TODO104 A4): the
    # companion axes resolve their own specs, but the varied axis must ship only
    # what its primitive accepts, or composition fails as "inactive".
    accepted = _accepted_knobs(axis, primitive)
    if accepted:
        prefix = f"{axis}."
        box = {
            field: value
            for field, value in box.items()
            if not field.startswith(prefix) or field[len(prefix) :] in accepted
        }
    return box


def resolve_semaphore(requested: int, devices: int | None = None) -> int:
    """One CUDA device trains one cell at a time (TODO104 A1).

    Concurrent settle on one GPU re-traces the compiled graphs per shape and
    hits ``config.recompile_limit``; the resulting timeouts are infrastructure,
    not mechanism verdicts. Only a multi-device host runs cells in parallel.
    """
    if requested <= 1:
        return 1
    if devices is None:
        import torch

        devices = torch.cuda.device_count() if torch.cuda.is_available() else 0
    if devices <= 1:
        return 1
    return min(requested, devices)


async def _measure_async(
    coord: Any, run: Schedule, budget_s: float | None = None
) -> dict[str, Any]:
    """Run ``_measure`` in a thread with a cooperative cell budget.

    The deadline stops the trainer mid-epoch, so a spent budget returns a
    ``timeout`` cell instead of leaving a live thread holding the device
    (TODO104 A3).
    """
    if budget_s is None:
        budget_s = MEASURE_BUDGET_S or None
    if budget_s is None:
        return await asyncio.to_thread(_measure, coord, run)
    return await asyncio.to_thread(_measure, coord, run, budget_s)


async def measure_declared_default(
    axis: str, primitive: str, task_id: str, budget_s: float | None = None
) -> tuple[LadderRung, str]:
    """One cell at the primitive's declared default box.

    A rule that declares no live knob still has a capability to measure: the
    single cell enters the map with its measured accuracy, and a claim stays
    refused as "no power by construction" because the ladder moved no knob.
    """
    box = _build_axis_box(axis, primitive, task_id)
    box["epochs"] = 1
    box["fidelity"] = "L0"
    coord = screen_coordinate(box, axis, primitive)
    schedule = base_schedule(task_id, "auto")
    measured = await _measure_async(coord, schedule, budget_s)
    rung = LadderRung(
        factor=1.0,
        value=0.0,
        status=measured["status"],
        val_acc=measured["val_acc"],
        walltime_s=measured["walltime_s"],
        replay_hash=measured["replay_hash"],
        box=measured["box"],
        reason=measured["reason"],
    )
    verdict = ladder_verdict(axis, primitive, task_id, rung)
    return rung, verdict


def ladder_verdict(
    axis: str, primitive: str, task_id: str, rung: LadderRung | None
) -> str:
    """The ladder verdict for the best rung (TODO104 A13).

    An error-blind credit reads no target, so chance accuracy is its contract,
    not a failure: the bar does not decide it. Such a row is reported as
    ``error_blind`` and counted apart, so it never inflates or deflates the
    error-aware breadth count.
    """
    from computronium.experiment.sec_loop import _task_bar

    if rung is None:
        return "no_cell"
    if rung.status != "measured" or rung.val_acc is None:
        return rung.status
    if axis == "credit":
        from computronium.core.system_trainer.spec import error_blind_credit

        if error_blind_credit(primitive):
            return "error_blind"
    bar = _task_bar(task_id)
    if bar is not None and rung.val_acc <= bar.value:
        return "below_bar"
    return "viable"


async def run_rung1_ladder(
    axis: str,
    primitive: str,
    task_id: str,
    semaphore_limit: int = 2,
) -> tuple[list[LadderRung], LadderRung | None, str]:
    """Run 3-point ladder for a primitive on its primary knob."""
    import asyncio

    knob_info = _get_primary_knob(axis, primitive, task_id=task_id)
    if knob_info is None:
        rung, verdict = await measure_declared_default(axis, primitive, task_id)
        return [rung], (rung if verdict == "viable" else None), verdict

    knob_key, default_value = knob_info
    knob_name = knob_key.split(".", 1)[1]

    is_int_param = knob_name in INT_KNOBS

    base_box = _build_axis_box(axis, primitive, task_id)
    schedule = base_schedule(task_id, "auto")

    rungs: list[LadderRung] = []
    semaphore = asyncio.Semaphore(semaphore_limit)

    async def run_rung(factor: float, value: float) -> LadderRung:
        async with semaphore:
            box = dict(base_box)
            # Convert to int for integer params
            box[knob_key] = knob_point(axis, primitive, knob_name, value)
            coord = screen_coordinate(box, axis, primitive)
            measured = await _measure_async(coord, schedule)
            return LadderRung(
                factor=factor,
                value=value,
                status=measured["status"],
                val_acc=measured["val_acc"],
                walltime_s=measured["walltime_s"],
                replay_hash=measured["replay_hash"],
                box=measured["box"],
                reason=measured["reason"],
            )

    tasks = [
        run_rung(
            factor,
            round(default_value * factor) if is_int_param else default_value * factor,
        )
        for factor in LADDER_FACTORS
    ]
    rungs = await asyncio.gather(*tasks)

    # Find best rung
    measured_rungs = [
        r for r in rungs if r.status == "measured" and r.val_acc is not None
    ]
    if not measured_rungs:
        return rungs, None, "all_refused"

    best = max(measured_rungs, key=lambda r: r.val_acc or 0.0)
    return rungs, best, ladder_verdict(axis, primitive, task_id, best)


def pair_schedule(schedule: Schedule, seed: int) -> Schedule:
    """The schedule for one arm at one seed (TODO104 A8/A3).

    A paired comparison is ``n`` index-matched seeds; reusing the base
    schedule's seed ran the same cell twice and reported ``d=0.00``. Each cell
    is one seed, so the replicate count is 1.
    """
    return replace(schedule, seed=seed, n_seeds=1)


def knob_bounds(axis: str, primitive: str, name: str) -> tuple[float, float] | None:
    """The declared domain of a knob, or ``None`` when it declares none.

    A rounded ladder point can leave the domain (``num_layers`` 3 x 0.0152
    rounds to 0 — a degenerate geometry), so a point is clamped to the domain
    the config class declares, never to an invented floor (TODO104 A23).
    """
    import importlib

    from computronium.primitives.registry import _CONFIG_FACTORIES

    prefix = _AXIS_REGISTRY_PREFIX.get(axis, axis)
    factory_path = _CONFIG_FACTORIES.get(f"primitive.{prefix}.{primitive}")
    if not factory_path:
        return None
    parts = factory_path.split(".")
    module = importlib.import_module(".".join(parts[:-2]))
    config_cls = getattr(module, parts[-2], None)
    hyperparameters = getattr(config_cls, "hyperparameters", None)
    if hyperparameters is None:
        return None
    spec = hyperparameters(primitive).get(name)
    domain = (spec or {}).get("domain")
    if isinstance(domain, tuple | list) and len(domain) >= 2:
        low, high = float(domain[0]), float(domain[1])
        if low < high:
            return low, high
    return None


def knob_point(axis: str, primitive: str, name: str, value: float) -> float:
    """One legal ladder point: rounded for an integer knob, clamped to domain."""
    point = round(value) if name in INT_KNOBS else value
    bounds = knob_bounds(axis, primitive, name)
    if bounds is None:
        return point
    low, high = bounds
    return min(max(point, low), high)


def comparison_boxes(
    axis: str,
    primitive: str,
    task_id: str,
    best_value: float,
    default_value: float,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """The two boxes a paired comparison runs: one primitive, two knob values.

    The registration's claim is about tuning one knob on one primitive, so a
    control drawn from another primitive measures a different question
    (TODO104 A21: conv against feedforward reported d=-61.27).
    """
    knob_info = _get_primary_knob(axis, primitive, task_id=task_id)
    if knob_info is None:
        raise ValueError(f"{axis}/{primitive} declares no knob to compare")
    knob_key = knob_info[0]
    name = knob_key.split(".", 1)[1]
    control = knob_point(axis, primitive, name, default_value)
    treatment = knob_point(axis, primitive, name, best_value)
    control_box = _build_axis_box(axis, primitive, task_id)
    control_box[knob_key] = control
    treatment_box = dict(control_box)
    treatment_box[knob_key] = treatment
    return treatment_box, control_box


async def run_rung2_comparison(
    axis: str,
    primitive: str,
    task_id: str,
    best_value: float,
    registration_path: Path,
    n_seeds: int = CLAIM_SEEDS,
    semaphore_limit: int = 2,
    budget_s: float | None = None,
    seed_offset: int = 0,
) -> tuple[list[PairedCell], dict[str, Any], str] | None:
    """Run paired comparison: treatment (primitive at best) vs control (axis default).

    ``budget_s`` is the cooperative per-cell training deadline (TODO104 A3).
    """
    import asyncio

    knob_info = _get_primary_knob(axis, primitive, task_id=task_id)
    if knob_info is None:
        return None
    knob_key = knob_info[0]

    # Load registration
    temp_schedule = base_schedule(task_id, "auto")
    temp_box = temp_schedule.to_dict()
    temp_box["device"] = "cuda"
    temp_box["task"] = task_id
    registration = None
    try:
        registration = EffectSizeRegistration.load(registration_path)
    except KeyError, ValueError:
        with contextlib.suppress(KeyError, ValueError):
            registration = ThresholdRegistration.load(registration_path)

    if registration is None:
        return None

    declared_default = (
        registration.box.get(knob_key, knob_info[1])
        if registration.box
        else knob_info[1]
    )
    treatment_box, control_box = comparison_boxes(
        axis, primitive, task_id, best_value, declared_default
    )
    control_coord = screen_coordinate(control_box, axis, primitive)
    # Apply axis-specific extra params for the treatment primitive from registration
    if axis == "dynamics" and primitive in {"energy_minimization", "pc_alm"}:
        treatment_box["dynamics.max_steps"] = 10
        treatment_box["dynamics.step_size"] = 0.1
        treatment_box["dynamics.convergence_threshold"] = 1e-3
        # Also copy dynamics params from registration box if available
        if hasattr(registration, "box") and registration.box:
            for key, value in registration.box.items():
                if key.startswith("dynamics.") and key != knob_key:
                    treatment_box[key] = value
    treatment_coord = screen_coordinate(treatment_box, axis, primitive)

    schedule = base_schedule(task_id, "auto")

    cells: list[PairedCell] = []
    semaphore = asyncio.Semaphore(semaphore_limit)

    async def run_cell(arm: str, coord: Any, seed: int) -> PairedCell:
        async with semaphore:
            # One pair is one seed: a constant schedule seed made every pair
            # bit-identical, so the paired difference was 0 and d collapsed to
            # 0.00 on every comparison (measured 2026-11-25).
            paired_schedule = pair_schedule(schedule, seed)
            measured = await _measure_async(coord, paired_schedule, budget_s)
            return PairedCell(
                arm=arm,
                factor=1.0,
                seed=seed,
                status=measured["status"],
                val_acc=measured["val_acc"],
                loss=measured["loss"],
                walltime_s=measured["walltime_s"],
                replay_hash=measured["replay_hash"],
                box=measured["box"],
                reason=measured["reason"],
            )

    tasks = []
    for seed in range(seed_offset, seed_offset + n_seeds):
        tasks.append(run_cell("treatment", treatment_coord, seed))
        tasks.append(run_cell("control", control_coord, seed))

    cells = await asyncio.gather(*tasks)

    # Check for defects
    failed = next((c for c in cells if c.status == "defect"), None)
    if failed:
        return cells, {}, "defect"

    # Check identical arms
    treatments = [c for c in cells if c.arm == "treatment"]
    controls = [c for c in cells if c.arm == "control"]
    identical = all(
        t.val_acc == c.val_acc for t, c in zip(treatments, controls, strict=True)
    )
    if identical:
        return cells, {}, "no_power"

    # Paired comparison
    paired = paired_comparison(
        [float(c.val_acc or 0.0) for c in treatments],
        [float(c.val_acc or 0.0) for c in controls],
        seed=schedule.seed,
    )

    # Check claim
    verdict = "coordinate"
    if isinstance(registration, EffectSizeRegistration):
        if paired.passes_effect_size(registration, box=treatment_box):
            verdict = "claim"
    elif isinstance(registration, ThresholdRegistration):
        if paired.passes(registration, box=treatment_box):
            verdict = "claim"

    effect_dict = {
        "n": paired.n,
        "mean_diff": paired.mean_diff,
        "ci_lower": paired.ci_lower,
        "ci_upper": paired.ci_upper,
        "p_value": paired.p_value,
        "cohens_dz": paired.cohens_dz,
    }

    return cells, effect_dict, verdict


async def run_primitive_full(
    axis: str,
    primitive: str,
    task_id: str,
    semaphore_limit: int = 2,
) -> RungResult:
    """Run Rung 1 ladder + Rung 2 comparison for one primitive."""
    started = time.monotonic()

    task_families = _get_task_families_for_primitive(axis, primitive)
    task_family = preferred_task_family(task_families) or "vision"

    # Rung 1: 3-point ladder
    rungs, best, rung1_verdict = await run_rung1_ladder(
        axis, primitive, task_id, semaphore_limit
    )

    rung2_cells = None
    rung2_effect = None
    rung2_verdict = None

    # Rung 2: paired comparison at best point
    if best is not None and rung1_verdict == "viable":
        # Generate registration path
        reg_dir = Path("configs/preregistrations")
        reg_dir.mkdir(parents=True, exist_ok=True)
        reg_path = reg_dir / f"sec_{axis}_{primitive}.json"

        # Create registration if not exists
        if not reg_path.exists():
            await create_registration(axis, primitive, task_id, reg_path)

        result = await run_rung2_comparison(
            axis,
            primitive,
            task_id,
            best.value,
            reg_path,
            semaphore_limit=semaphore_limit,
        )
        if result:
            rung2_cells, rung2_effect, rung2_verdict = result

    return RungResult(
        axis=axis,
        primitive=primitive,
        task_id=task_id,
        task_family=task_family,
        rung1_ladder=[r.to_dict() for r in rungs],
        best_rung=best.to_dict() if best else None,
        rung1_verdict=rung1_verdict,
        rung2_cells=[c.to_dict() for c in rung2_cells] if rung2_cells else None,
        rung2_effect=rung2_effect,
        rung2_verdict=rung2_verdict,
        walltime_s=time.monotonic() - started,
    )


async def create_registration(
    axis: str,
    primitive: str,
    task_id: str,
    reg_path: Path,
) -> ThresholdRegistration | EffectSizeRegistration:
    """Create a pre-registration file for an axis primitive."""
    base_box = _build_axis_box(axis, primitive, task_id)

    task_families = _get_task_families_for_primitive(axis, primitive)
    task_family = preferred_task_family(task_families) or "vision"
    min_d = MIN_EFFECT_SIZE_BY_FAMILY.get(task_family, 0.5)

    knob_info = _get_primary_knob(axis, primitive, task_id=task_id)
    knob_key = knob_info[0] if knob_info else f"{axis}.step_size"

    # Only register the axis primitive and its primary knob, not all structural params.
    # The box_mismatch check compares ALL fields, so we must limit to what the
    # treatment run will actually match (axis primitive + knob). The control arm
    # uses the axis default primitive, which has different structural params.
    # The varied knob is the intervention, not part of the box: a declared box
    # that pins it refuses every treatment, which is the one cell the claim
    # varies (TODO104 A26). The control arm still runs at the knob's declared
    # default, read from the primitive's own config.
    minimal_box = {axis: primitive}
    # Also include the base schedule params that are constant across runs
    # A paired run varies the seed per pair and runs one seed per cell, so
    # neither is a box field: the identity is the box the pair is measured at
    # (TODO104 A26).
    for key in (
        "fidelity",
        "epochs",
        "batch_size",
        "task_id",
        "device",
        "precision",
    ):
        if key in base_box:
            minimal_box[key] = base_box[key]

    registration = EffectSizeRegistration.for_task_family(
        min_d=min_d,
        claim=(
            f"tuning {knob_key} on primitive.{axis}.{primitive} improves val_acc "
            f"with Cohen's d >= {min_d} at the {task_id} base"
        ),
        metric="val_acc",
        task_id=task_id,
        alpha=DEFAULT_ALPHA,
        min_seeds=CLAIM_SEEDS,
        created=date.today().isoformat(),
        box=minimal_box,
    )

    reg_path.parent.mkdir(parents=True, exist_ok=True)
    reg_path.write_text(json.dumps(registration.to_dict(), indent=2), encoding="utf-8")
    return registration


async def run_axis_rung1_all(
    axis: str,
    semaphore_limit: int = 2,
    task_override: dict[str, str] | None = None,
) -> list[RungResult]:
    """Run Rung 1 ladder for all primitives in an axis."""
    primitives = _get_primitives_for_axis(axis)
    results = []

    for primitive in primitives:
        task_families = _get_task_families_for_primitive(axis, primitive)
        if not task_families:
            continue

        task_family = preferred_task_family(task_families) or "vision"
        task_id = (task_override or {}).get(
            task_family, FAMILY_TO_TASK.get(task_family, "mnist")
        )

        print(f"\n=== Rung 1: {axis}/{primitive} on {task_id} ===")
        result = await run_primitive_full(axis, primitive, task_id, semaphore_limit)
        results.append(result)

        print(f"  Rung 1 verdict: {result.rung1_verdict}")
        if result.best_rung:
            print(
                f"  Best: {result.best_rung['factor']}x = {result.best_rung['val_acc']:.4f}"
            )
        if result.rung2_verdict:
            print(
                f"  Rung 2: {result.rung2_verdict} (d={result.rung2_effect.get('cohens_dz', 0):.2f})"
            )

    return results


async def run_axis_rung2_all(
    axis: str,
    semaphore_limit: int = 2,
) -> list[RungResult]:
    """Run Rung 2 for all primitives that passed Rung 1."""
    # Load previous Rung 1 results
    results_file = Path(f"results/sec/rung1_{axis}.json")
    if not results_file.exists():
        return []

    results = json.loads(results_file.read_text(encoding="utf-8"))
    viable = [
        r for r in results if r.get("rung1_verdict") == "viable" and r.get("best_rung")
    ]

    rung2_results = []
    for r in viable:
        primitive = r["primitive"]
        task_id = r["task_id"]
        best_value = r["best_rung"]["value"]

        reg_dir = Path("configs/preregistrations")
        reg_path = reg_dir / f"sec_{axis}_{primitive}.json"

        if not reg_path.exists():
            await create_registration(axis, primitive, task_id, reg_path)

        rung2_result = await run_rung2_comparison(
            axis,
            primitive,
            task_id,
            best_value,
            reg_path,
            semaphore_limit=semaphore_limit,
        )

        r["rung2_cells"] = (
            [c.to_dict() for c in rung2_result[0]] if rung2_result else None
        )
        r["rung2_effect"] = rung2_result[1] if rung2_result else None
        r["rung2_verdict"] = rung2_result[2] if rung2_result else None
        rung2_results.append(r)

    # Save combined results
    out_path = Path(f"results/sec/rung2_{axis}.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rung2_results, indent=2), encoding="utf-8")

    return rung2_results


async def preregister_axis_primitives(axis: str) -> None:
    """Create pre-registration files for all primitives in an axis."""
    primitives = _get_primitives_for_axis(axis)
    for primitive in primitives:
        task_families = _get_task_families_for_primitive(axis, primitive)
        if not task_families:
            continue
        task_id = FAMILY_TO_TASK.get(
            preferred_task_family(task_families) or "mnist", "mnist"
        )

        reg_dir = Path("configs/preregistrations")
        reg_path = reg_dir / f"sec_{axis}_{primitive}.json"

        if not reg_path.exists():
            await create_registration(axis, primitive, task_id, reg_path)
            print(f"Created registration: {reg_path}")


async def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="SEC Rung 1/2 for all axes")
    parser.add_argument(
        "--axis",
        choices=[
            "credit",
            "dynamics",
            "geometry",
            "update",
            "plasticity",
            "substrate",
            "all",
        ],
        default="all",
    )
    parser.add_argument("--rung", choices=["1", "2", "both"], default="both")
    parser.add_argument("--primitive", type=str, help="Run only this primitive")
    parser.add_argument("--semaphore", type=int, default=2)
    parser.add_argument("--task", type=str, help="Override task_id (e.g., mnist)")
    parser.add_argument(
        "--preregister", action="store_true", help="Create registration files"
    )

    args = parser.parse_args()

    axes = [args.axis] if args.axis != "all" else list(AXIS_DEFAULTS.keys())

    if args.preregister:
        for axis in axes:
            await preregister_axis_primitives(axis)
        return

    for axis in axes:
        if args.rung in {"1", "both"}:
            if args.primitive:
                primitives = [args.primitive]
            else:
                primitives = _get_primitives_for_axis(axis)

            for primitive in primitives:
                task_families = _get_task_families_for_primitive(axis, primitive)
                if not task_families:
                    continue
                task_family = preferred_task_family(task_families) or "vision"
                task_id = args.task or FAMILY_TO_TASK.get(task_family, "mnist")
                result = await run_primitive_full(
                    axis, primitive, task_id, args.semaphore
                )
                # Save result with task_id in filename to avoid overwrites
                safe_task_id = task_id.replace("/", "_")
                out_path = Path(
                    f"results/sec/rung12_{axis}_{primitive}_{safe_task_id}.json"
                )
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(
                    json.dumps(result.to_dict(), indent=2), encoding="utf-8"
                )


if __name__ == "__main__":
    asyncio.run(main())
