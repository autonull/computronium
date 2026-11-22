"""Rung 1 & 2 runner for all 6 axes (Credit, Dynamics, Geometry, Update, Plasticity, Substrate).

This module generalizes the credit-only runner in sec_deep_dive.py to handle
any structural axis. It runs:
- Rung 1: 3-point ladder on the axis's primary knob (1 epoch, 1 seed)
- Rung 2: Paired comparison (n=5 seeds) at best ladder point vs axis default
"""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final

from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.sec_loop import (
    _measure,
    base_schedule,
    screen_coordinate,
)
from computronium.experiment.sec_pilot import own_knob_params, BASE_BOXES, base_family
from computronium.experiment.schema.coordinate import Schedule
from computronium.experiment.schema.axis import AXES_REGISTRIES
from computronium.validation.preregistration import (
    DEFAULT_ALPHA,
    EffectSizeRegistration,
    PairedComparison,
    ThresholdRegistration,
    paired_comparison,
)

__all__ = [
    "AXIS_PRIMARY_KNOB",
    "AXIS_DEFAULTS",
    "run_rung1_ladder",
    "run_rung2_comparison",
    "run_axis_rung1_all",
    "run_axis_rung2_all",
    "preregister_axis_primitives",
]

# Ladder factors: 0.1x, 1.0x, 10.0x of declared default
LADDER_FACTORS: Final[tuple[float, ...]] = (0.1, 1.0, 10.0)
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
    "neuromorphic": "mnist",
    "quantum": "mnist",
    "photonic": "mnist",
    "analog": "mnist",
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


def _get_primary_knob(axis: str, primitive: str) -> tuple[str, float] | None:
    """Get the primary knob and its default for a primitive.

    Checks both own_knob_params (hyperparameters) and config class hyperparameters().
    """
    # First try hyperparameters (own_knob_params)
    params = own_knob_params(axis, primitive)
    for name in ["step_size", "max_steps", "hidden_dim", "depth", "width", "num_layers", "momentum", "trace_decay", "noise_level", "sparsity",
                  "feedback_scale", "beta", "readout_scale", "fd_step", "estimator_samples", "aux_head_scale", "lr"]:
        key = f"{axis}.{name}"
        value = params.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        if value > 0:
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
                        from computronium.experiment.schema.harvest import CoordinateContext
                        from computronium.experiment.schema.coordinate import Coordinate
                        # Build coordinate with the actual primitive for the axis being tested
                        axes = {
                            "substrate": "digital",
                            "geometry": "feedforward",
                            "dynamics": "instantaneous",
                            "plasticity": "null",
                            "credit": "gradient",
                            "update": "euclidean",
                        }
                        axes[axis] = primitive  # Use the actual primitive for availability check
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
                            if domain[2] == "log":
                                import math
                                return f"{axis}.{name}", math.sqrt(domain[0] * domain[1])
                            else:
                                return f"{axis}.{name}", (domain[0] + domain[1]) / 2
                        elif isinstance(domain, list):
                            return f"{axis}.{name}", float(domain[0])

    # For structural axes (geometry), check topology_params from axis spec
    from computronium.experiment.schema.axis import get_axis_spec, StructuralAxis
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
        raise ValueError(f"Base task {schedule_task_id} for family {family} declares no base box")

    # Start with base schedule
    box = schedule.to_dict()
    box["device"] = "cuda"
    box["task"] = task_id  # Keep original task_id for the run

    # Structural axes that come from base_coordinate (not hyperparameters)
    structural_axes = {"substrate", "geometry", "dynamics", "plasticity"}

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
    from computronium.primitives.registry import _CONFIG_FACTORIES
    from computronium.experiment.schema.harvest import CoordinateContext
    from computronium.experiment.schema.coordinate import Coordinate
    from computronium.experiment.legality.dsl import evaluate

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

    # Get hyperparams from config factory's class
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
        if hasattr(config_cls, "hyperparameters"):
            hp_dict = config_cls.hyperparameters(primitive)
            for hp_name, hp_spec in hp_dict.items():
                avail = True
                avail_pred = hp_spec.get("availability")
                if avail_pred is not None:
                    avail = evaluate(avail_pred, ctx)
                if not avail:
                    continue  # Skip unavailable hyperparams
                # Get default value from domain
                domain = hp_spec.get("domain")
                if domain:
                    if isinstance(domain, tuple) and len(domain) >= 2:
                        if domain[2] == "log":
                            import math
                            box[f"{axis}.{hp_name}"] = math.sqrt(domain[0] * domain[1])
                        else:
                            box[f"{axis}.{hp_name}"] = (domain[0] + domain[1]) / 2
                    elif isinstance(domain, list):
                        box[f"{axis}.{hp_name}"] = domain[0]

    # Axis-specific extra params
    if axis == "dynamics" and primitive in {"energy_minimization", "pc_alm"}:
        box["dynamics.max_steps"] = 10
        box["dynamics.step_size"] = 0.1

    return box


async def _measure_async(coord: Any, run: Schedule) -> dict[str, Any]:
    """Run _measure in a thread pool."""
    return await asyncio.to_thread(_measure, coord, run)


async def run_rung1_ladder(
    axis: str,
    primitive: str,
    task_id: str,
    semaphore_limit: int = 2,
) -> tuple[list[LadderRung], LadderRung | None, str]:
    """Run 3-point ladder for a primitive on its primary knob."""
    import asyncio

    knob_info = _get_primary_knob(axis, primitive)
    if knob_info is None:
        return [], None, "no_knob"

    knob_key, default_value = knob_info
    knob_name = knob_key.split(".", 1)[1]

    base_box = _build_axis_box(axis, primitive, task_id)
    schedule = base_schedule(task_id, "auto")

    rungs: list[LadderRung] = []
    semaphore = asyncio.Semaphore(semaphore_limit)

    async def run_rung(factor: float, value: float) -> LadderRung:
        async with semaphore:
            box = dict(base_box)
            box[knob_key] = value
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

    tasks = [run_rung(factor, default_value * factor) for factor in LADDER_FACTORS]
    rungs = await asyncio.gather(*tasks)

    # Find best rung
    measured_rungs = [r for r in rungs if r.status == "measured" and r.val_acc is not None]
    if not measured_rungs:
        return rungs, None, "all_refused"

    best = max(measured_rungs, key=lambda r: r.val_acc or 0.0)

    # Check if best clears the bar
    from computronium.experiment.sec_loop import _task_bar
    bar = _task_bar(task_id)
    if bar is not None and (best.val_acc or 0.0) <= bar.value:
        return rungs, best, "below_bar"

    return rungs, best, "viable"


async def run_rung2_comparison(
    axis: str,
    primitive: str,
    task_id: str,
    best_value: float,
    registration_path: Path,
    n_seeds: int = CLAIM_SEEDS,
    semaphore_limit: int = 2,
) -> tuple[list[PairedCell], dict[str, Any], str] | None:
    """Run paired comparison: treatment (primitive at best) vs control (axis default)."""
    import asyncio

    knob_info = _get_primary_knob(axis, primitive)
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
    except (KeyError, ValueError):
        try:
            registration = ThresholdRegistration.load(registration_path)
        except (KeyError, ValueError):
            pass

    if registration is None:
        return None

    # Build treatment box (primitive at best knob value)
    treatment_box = _build_axis_box(axis, primitive, task_id)
    treatment_box[knob_key] = best_value
    treatment_coord = screen_coordinate(treatment_box, axis, primitive)

    # Build control box (axis default primitive)
    default_primitive = AXIS_DEFAULTS.get(axis, primitive)
    control_box = _build_axis_box(axis, default_primitive, task_id)
    control_coord = screen_coordinate(control_box, axis, default_primitive)

    schedule = base_schedule(task_id, "auto")

    cells: list[PairedCell] = []
    semaphore = asyncio.Semaphore(semaphore_limit)

    async def run_cell(arm: str, coord: Any, seed: int) -> PairedCell:
        async with semaphore:
            measured = await _measure_async(coord, schedule)
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
    for seed in range(n_seeds):
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
        t.val_acc == c.val_acc
        for t, c in zip(treatments, controls, strict=True)
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
    task_family = task_families[0] if task_families else "vision"

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
            axis, primitive, task_id, best.value, reg_path,
            semaphore_limit=semaphore_limit
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
    task_family = task_families[0] if task_families else "vision"
    min_d = MIN_EFFECT_SIZE_BY_FAMILY.get(task_family, 0.5)

    knob_info = _get_primary_knob(axis, primitive)
    knob_key = knob_info[0] if knob_info else f"{axis}.step_size"

    registration = EffectSizeRegistration.for_task_family(
        claim=(
            f"tuning {knob_key} on primitive.{axis}.{primitive} improves val_acc "
            f"with Cohen's d >= {min_d} at the {task_id} base"
        ),
        metric="val_acc",
        task_id=task_id,
        alpha=DEFAULT_ALPHA,
        min_seeds=CLAIM_SEEDS,
        created=date.today().isoformat(),
        box=base_box,
    )

    reg_path.parent.mkdir(parents=True, exist_ok=True)
    reg_path.write_text(json.dumps(registration.to_dict(), indent=2))
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

        task_family = task_families[0]
        task_id = (task_override or {}).get(task_family, FAMILY_TO_TASK.get(task_family, "mnist"))

        print(f"\n=== Rung 1: {axis}/{primitive} on {task_id} ===")
        result = await run_primitive_full(axis, primitive, task_id, semaphore_limit)
        results.append(result)

        print(f"  Rung 1 verdict: {result.rung1_verdict}")
        if result.best_rung:
            print(f"  Best: {result.best_rung['factor']}x = {result.best_rung['val_acc']:.4f}")
        if result.rung2_verdict:
            print(f"  Rung 2: {result.rung2_verdict} (d={result.rung2_effect.get('cohens_dz', 0):.2f})")

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

    results = json.loads(results_file.read_text())
    viable = [r for r in results if r.get("rung1_verdict") == "viable" and r.get("best_rung")]

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
            axis, primitive, task_id, best_value, reg_path,
            semaphore_limit=semaphore_limit
        )

        r["rung2_cells"] = [c.to_dict() for c in rung2_result[0]] if rung2_result else None
        r["rung2_effect"] = rung2_result[1] if rung2_result else None
        r["rung2_verdict"] = rung2_result[2] if rung2_result else None
        rung2_results.append(r)

    # Save combined results
    out_path = Path(f"results/sec/rung2_{axis}.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rung2_results, indent=2))

    return rung2_results


async def preregister_axis_primitives(axis: str) -> None:
    """Create pre-registration files for all primitives in an axis."""
    primitives = _get_primitives_for_axis(axis)
    for primitive in primitives:
        task_families = _get_task_families_for_primitive(axis, primitive)
        if not task_families:
            continue
        task_id = FAMILY_TO_TASK.get(task_families[0], "mnist")

        reg_dir = Path("configs/preregistrations")
        reg_path = reg_dir / f"sec_{axis}_{primitive}.json"

        if not reg_path.exists():
            await create_registration(axis, primitive, task_id, reg_path)
            print(f"Created registration: {reg_path}")


async def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="SEC Rung 1/2 for all axes")
    parser.add_argument("--axis", choices=["credit", "dynamics", "geometry", "update", "plasticity", "substrate", "all"], default="all")
    parser.add_argument("--rung", choices=["1", "2", "both"], default="both")
    parser.add_argument("--primitive", type=str, help="Run only this primitive")
    parser.add_argument("--semaphore", type=int, default=2)
    parser.add_argument("--task", type=str, help="Override task_id (e.g., mnist)")
    parser.add_argument("--preregister", action="store_true", help="Create registration files")

    args = parser.parse_args()

    axes = [args.axis] if args.axis != "all" else list(AXIS_DEFAULTS.keys())

    if args.preregister:
        for axis in axes:
            await preregister_axis_primitives(axis)
        return

    for axis in axes:
        if args.rung in ("1", "both"):
            task_override = {args.task: args.task} if args.task else None
            if args.primitive:
                primitives = [args.primitive]
            else:
                primitives = _get_primitives_for_axis(axis)

            for primitive in primitives:
                task_families = _get_task_families_for_primitive(axis, primitive)
                if not task_families:
                    continue
                task_family = task_families[0]
                task_id = (args.task or FAMILY_TO_TASK.get(task_family, "mnist"))
                result = await run_primitive_full(axis, primitive, task_id, args.semaphore)
                # Save result
                out_path = Path(f"results/sec/rung12_{axis}_{primitive}.json")
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(json.dumps(result.to_dict(), indent=2))


if __name__ == "__main__":
    asyncio.run(main())