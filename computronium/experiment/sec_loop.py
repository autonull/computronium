"""SEC Loop: result-first capability harvest loop.

Runs:
- Track R (result-first): R1 (SplitMNIST local vs backprop with EWC)
- Track P0 (breadth delta): screen unscreened/changed/failed primitives
- Track P1 (confirmation): 3 seeds, paired, on a measured, bound P0 cell

A screen measures; it never adjudicates. P1 stays for the review meeting, but
its comparison is not yet a claim: a verdict needs a pre-registered comparison
at a calibrated box (TODO95 D4/D5), and its hard-coded `chance = 0.1` is the
open defect that session owns.

Run:
    uv run python -m computronium.experiment.sec_loop --track R1 --breadth delta --out results/sec
"""

from __future__ import annotations

import json
import logging
import math
import time
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from computronium.acceleration.spec import axis_segment
from computronium.core.continual.metrics import CLConfig, CLMetrics
from computronium.core.continual.runner import run_continual_learning
from computronium.core.logging import get_logger
from computronium.experiment.kernel.compose import compose_configs
from computronium.experiment.kernel.evaluate import (
    CellEvaluation,
    EvaluationError,
    evaluate_cell,
    record_from_evaluation,
)
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.coordinate import (
    Coordinate,
    Provenance,
    Schedule,
)
from computronium.experiment.schema.record import (
    FailureCause,
    GateVerdict,
    Maturity,
    ReproducibilityClass,
    Severity,
    Status,
)
from computronium.experiment.schema.registries import PARAM_BUDGET_TOLERANCE
from computronium.experiment.sec_binding import binding_reason
from computronium.experiment.sec_census import (
    MAP_VERSION,
    PrimitiveCensusEntry,
    build_census,
)
from computronium.experiment.sec_pilot import (
    base_schedule,
    calibrate_control,
    resource_vector,
)

if TYPE_CHECKING:
    from computronium.experiment.sec_interaction import (
        InteractionCell,
        InteractionEffect,
        SlicePlan,
    )

logger = get_logger(__name__)

# ============================================================
# Track R1: Result-First (SplitMNIST, batch 1, local×EWC vs backprop×EWC)
# ============================================================

R1_TASK = "split_mnist"
R1_EPOCHS_PER_TASK = 1
R1_BATCH_LIMIT = 32  # batch size 32
R1_HIDDEN_DIM = 128  # minimal for MNIST
R1_SEEDS = 5  # 5 data-order seeds
R1_CREDITS = ("local_supervision", "gradient")  # local vs backprop


def run_r1_track(
    out_dir: Path,
    census_entries: list[PrimitiveCensusEntry],
    device: str = "auto",
) -> dict[str, Any]:
    """Run Track R1: local×EWC vs backprop×EWC on SplitMNIST, 5 data-order seeds.

    Uses the continual learning runner for proper multi-task evaluation.

    Returns dict with results and verdict.
    """
    logger.info("Starting Track R1: SplitMNIST batch-1 local vs backprop with EWC")

    seeds = list(range(R1_SEEDS))  # 0, 1, 2, 3, 4

    # Map credit name to arm name for continual runner
    credit_to_arm = {
        "local_supervision": "local_ewc",
        "gradient": "backprop_ewc",
    }

    results: list[dict[str, Any]] = []
    local_results: list[float] = []
    backprop_results: list[float] = []
    local_forgetting: list[float] = []
    backprop_forgetting: list[float] = []

    for credit_name in R1_CREDITS:
        arm_name = credit_to_arm[credit_name]
        credit_results = []
        credit_forgetting = []

        for seed in seeds:
            logger.info(f"Running R1: credit={credit_name}, seed={seed}")

            config = CLConfig(
                input_dim=784,  # 28*28 flattened
                hidden_dim=R1_HIDDEN_DIM,
                output_dim=10,  # CL_TOTAL_CLASSES (5 tasks * 2 classes = 10)
                epochs_per_task=R1_EPOCHS_PER_TASK,
                batch_size=R1_BATCH_LIMIT,
                lr=0.01,
                ewc_lambda=1000.0,
                device=device,
                seed=seed,
                protocol="task_incremental",
                num_workers=0,
            )

            try:
                metrics: CLMetrics = run_continual_learning(arm_name, config)

                # Extract final accuracy (average over all 5 tasks)
                final_acc = (
                    sum(metrics.final_accuracies) / len(metrics.final_accuracies)
                    if metrics.final_accuracies
                    else 0.0
                )
                avg_forgetting = metrics.avg_forgetting

                credit_results.append(final_acc)
                credit_forgetting.append(avg_forgetting)

                box = _continual_box(config, budget_id="r1", task_id=R1_TASK)
                result_entry = {
                    "track": "R1",
                    "credit": credit_name,
                    "seed": seed,
                    "box": box.to_dict(),
                    "val_acc": final_acc,
                    "final_accuracies": metrics.final_accuracies,
                    "avg_forgetting": avg_forgetting,
                    "backward_transfer": metrics.backward_transfer,
                    "forward_transfer": metrics.forward_transfer,
                    "plastic_state_bytes": metrics.plastic_state_bytes,
                    "peak_memory_mb": metrics.peak_memory_mb,
                    "total_time_s": metrics.total_time_s,
                    "accuracy_matrix": metrics.accuracy_matrix,
                }
                results.append(result_entry)

            except Exception as e:
                logger.exception(f"R1 cell failed: credit={credit_name}, seed={seed}")
                result_entry = {
                    "track": "R1",
                    "credit": credit_name,
                    "seed": seed,
                    "val_acc": 0.0,
                    "error": str(e),
                }
                results.append(result_entry)
                credit_results.append(0.0)
                credit_forgetting.append(1.0)

        if credit_name == "local_supervision":
            local_results = credit_results
            local_forgetting = credit_forgetting
        elif credit_name == "gradient":
            backprop_results = credit_results
            backprop_forgetting = credit_forgetting

    # Compute metrics (no verdict - that's for the human review meeting)
    local_worst = min(local_results) if local_results else 0.0
    backprop_worst = min(backprop_results) if backprop_results else 0.0
    local_mean = sum(local_results) / len(local_results) if local_results else 0.0
    backprop_mean = (
        sum(backprop_results) / len(backprop_results) if backprop_results else 0.0
    )

    local_forgetting_mean = (
        sum(local_forgetting) / len(local_forgetting) if local_forgetting else 1.0
    )
    backprop_forgetting_mean = (
        sum(backprop_forgetting) / len(backprop_forgetting)
        if backprop_forgetting
        else 1.0
    )

    gap_worst = local_worst - backprop_worst
    gap_mean = local_mean - backprop_mean

    # Kill rule: gap < 2 pp on 5 seeds (recorded for review, not enforced)
    kill_rule_triggered = gap_worst < 0.02
    # Surprise: gap ≥ 5 pp (recorded for review)
    surprise = gap_worst >= 0.05

    result_summary = {
        "track": "R1",
        "local_results": local_results,
        "backprop_results": backprop_results,
        "local_forgetting": local_forgetting,
        "backprop_forgetting": backprop_forgetting,
        "local_worst": local_worst,
        "backprop_worst": backprop_worst,
        "local_mean": local_mean,
        "backprop_mean": backprop_mean,
        "local_forgetting_mean": local_forgetting_mean,
        "backprop_forgetting_mean": backprop_forgetting_mean,
        "gap_worst": gap_worst,
        "gap_mean": gap_mean,
        "kill_rule_triggered": kill_rule_triggered,
        "surprise": surprise,
        "cells": results,
    }

    logger.info(
        f"R1 complete: kill_rule={kill_rule_triggered}, surprise={surprise}, local_worst={local_worst:.4f}, backprop_worst={backprop_worst:.4f}, gap={gap_worst:.4f}"
    )
    logger.info(
        f"  local_forgetting={local_forgetting_mean:.4f}, backprop_forgetting={backprop_forgetting_mean:.4f}"
    )
    return result_summary


# ============================================================
# Track R2: Result-First (Permuted MNIST, 20 tasks, local×EWC vs backprop×EWC)
# ============================================================

R2_TASK = "permuted_mnist"
R2_NUM_TASKS = 20
R2_CLASSES_PER_TASK = 10
R2_EPOCHS_PER_TASK = 1
R2_BATCH_LIMIT = 32
R2_HIDDEN_DIM = 128  # minimal for MNIST
R2_SEEDS = 5  # 5 data-order seeds
R2_CREDITS = ("local_supervision", "gradient")  # local vs backprop


def run_r2_track(
    out_dir: Path,
    census_entries: list[PrimitiveCensusEntry],
    device: str = "auto",
) -> dict[str, Any]:
    """Run Track R2: local×EWC vs backprop×EWC on Permuted MNIST (20 tasks), 5 data-order seeds.

    Uses the continual learning runner for proper multi-task evaluation.

    Returns dict with results and verdict.
    """
    logger.info("Starting Track R2: Permuted MNIST 20-task local vs backprop with EWC")

    seeds = list(range(R2_SEEDS))  # 0, 1, 2, 3, 4

    # Map credit name to arm name for continual runner
    credit_to_arm = {
        "local_supervision": "local_ewc",
        "gradient": "backprop_ewc",
    }

    results: list[dict[str, Any]] = []
    local_results: list[float] = []
    backprop_results: list[float] = []
    local_forgetting: list[float] = []
    backprop_forgetting: list[float] = []

    for credit_name in R2_CREDITS:
        arm_name = credit_to_arm[credit_name]
        credit_results = []
        credit_forgetting = []

        for seed in seeds:
            logger.info(f"Running R2: credit={credit_name}, seed={seed}")

            config = CLConfig(
                input_dim=784,  # 28*28 flattened
                hidden_dim=R2_HIDDEN_DIM,
                output_dim=R2_NUM_TASKS * R2_CLASSES_PER_TASK,  # 200 total classes
                num_tasks=R2_NUM_TASKS,
                classes_per_task=R2_CLASSES_PER_TASK,
                epochs_per_task=R2_EPOCHS_PER_TASK,
                batch_size=R2_BATCH_LIMIT,
                lr=0.01,
                ewc_lambda=1000.0,
                device=device,
                seed=seed,
                protocol="task_incremental",
                num_workers=0,
            )

            try:
                metrics: CLMetrics = run_continual_learning(arm_name, config)

                # Extract final accuracy (average over all 20 tasks)
                final_acc = (
                    sum(metrics.final_accuracies) / len(metrics.final_accuracies)
                    if metrics.final_accuracies
                    else 0.0
                )
                avg_forgetting = metrics.avg_forgetting

                credit_results.append(final_acc)
                credit_forgetting.append(avg_forgetting)

                result_entry = {
                    "track": "R2",
                    "credit": credit_name,
                    "seed": seed,
                    "box": _continual_box(
                        config, budget_id="r2", task_id="permuted_mnist"
                    ).to_dict(),
                    "val_acc": final_acc,
                    "final_accuracies": metrics.final_accuracies,
                    "avg_forgetting": avg_forgetting,
                    "backward_transfer": metrics.backward_transfer,
                    "forward_transfer": metrics.forward_transfer,
                    "plastic_state_bytes": metrics.plastic_state_bytes,
                    "peak_memory_mb": metrics.peak_memory_mb,
                    "total_time_s": metrics.total_time_s,
                    "accuracy_matrix": metrics.accuracy_matrix,
                }
                results.append(result_entry)

            except Exception as e:
                logger.exception(f"R2 cell failed: credit={credit_name}, seed={seed}")
                result_entry = {
                    "track": "R2",
                    "credit": credit_name,
                    "seed": seed,
                    "val_acc": 0.0,
                    "error": str(e),
                }
                results.append(result_entry)
                credit_results.append(0.0)
                credit_forgetting.append(1.0)

        if credit_name == "local_supervision":
            local_results = credit_results
            local_forgetting = credit_forgetting
        elif credit_name == "gradient":
            backprop_results = credit_results
            backprop_forgetting = credit_forgetting

    # Compute metrics (no verdict - that's for the human review meeting)
    local_worst = min(local_results) if local_results else 0.0
    backprop_worst = min(backprop_results) if backprop_results else 0.0
    local_mean = sum(local_results) / len(local_results) if local_results else 0.0
    backprop_mean = (
        sum(backprop_results) / len(backprop_results) if backprop_results else 0.0
    )

    local_forgetting_mean = (
        sum(local_forgetting) / len(local_forgetting) if local_forgetting else 1.0
    )
    backprop_forgetting_mean = (
        sum(backprop_forgetting) / len(backprop_forgetting)
        if backprop_forgetting
        else 1.0
    )

    gap_worst = local_worst - backprop_worst
    gap_mean = local_mean - backprop_mean

    # Kill rule: gap < 2 pp on 5 seeds (recorded for review, not enforced)
    kill_rule_triggered = gap_worst < 0.02
    # Surprise: gap ≥ 5 pp (recorded for review)
    surprise = gap_worst >= 0.05

    result_summary = {
        "track": "R2",
        "local_results": local_results,
        "backprop_results": backprop_results,
        "local_forgetting": local_forgetting,
        "backprop_forgetting": backprop_forgetting,
        "local_worst": local_worst,
        "backprop_worst": backprop_worst,
        "local_mean": local_mean,
        "backprop_mean": backprop_mean,
        "local_forgetting_mean": local_forgetting_mean,
        "backprop_forgetting_mean": backprop_forgetting_mean,
        "gap_worst": gap_worst,
        "gap_mean": gap_mean,
        "kill_rule_triggered": kill_rule_triggered,
        "surprise": surprise,
        "cells": results,
    }

    logger.info(
        f"R2 complete: local_worst={local_worst:.4f}, backprop_worst={backprop_worst:.4f}, gap={gap_worst:.4f}"
    )
    logger.info(
        f"  local_forgetting={local_forgetting_mean:.4f}, backprop_forgetting={backprop_forgetting_mean:.4f}"
    )
    return result_summary


def _continual_box(config: CLConfig, *, budget_id: str, task_id: str) -> Schedule:
    """The box a continual-learning cell trains at: its kernel schedule.

    The CL config's own knobs (lr, ewc_lambda, num_tasks) stay the cell's
    params; the box records what the *kernel* ran at, so a claim can refuse a
    re-run at another batch size or seed (TODO95 P0b).
    """
    return Schedule(
        fidelity="L0",
        seed=config.seed,
        n_seeds=1,
        epochs=config.epochs_per_task,
        batch_limit=0,
        batch_size=config.batch_size,
        budget_id=budget_id,
        task_id=task_id,
        device=config.device,
        deterministic=True,
        num_workers=0,
        precision="fp32",
        checkpoint_every_n=0,
    )


# ============================================================
# Track P0: Breadth Delta Screen
# ============================================================

# The screen's slice: one task family, its declared base box (TODO95 S2).
# The box is not restated here — ``sec_pilot.BASE_BOXES`` is the one source,
# and a second literal is how the screen trained at a different box than the
# map printed.
P0_TASK = "mnist"
P0_HIDDEN_DIM = 128
# The parameter ceiling is the base box's own field (``Schedule.param_budget``),
# not a second literal: a 10k ceiling with a 128-wide layer was an impossible
# box (measured 2026-11-18), and the declared base now fits its geometry.
# How many compose-legal boxes to try per primitive before declaring it cannot
# train. Most resolve on the first (base) box; a few need a companion swap.
P0_MAX_COORDINATES = 24
# A swap chain is not a fair search: one slow primitive can spend the axis's
# whole watchdog on 24 training attempts. The cap is a refusal (a box
# statement), not a verdict, and it is 8× the measured 375-batch cell.
P0_PRIMITIVE_BUDGET_S = 60.0
# The base box shares one step size and one geometry width across primitives.
# A primitive's own declared defaults are the `own-knobs` pass (TODO95 S2);
# it runs on request (``--own-knobs``) so the two boxes stay distinct
# instruments. An update row in the base box is `inert` (see sec_binding).


def _box_summary(coord: Coordinate, schedule: Schedule | None = None) -> dict[str, Any]:
    """The box a cell was screened in: the six axes plus the whole schedule.

    A row without its task, batch and step count cannot be reproduced and cannot
    be compared with another row (TODO95 D2/D3). The schedule is the box, so its
    own serialization is the one source; the six axes are added to it.
    """
    box: dict[str, Any] = {}
    for field in StructuralAxis:
        box[field.value] = getattr(coord, field.value)
    if schedule is not None:
        box |= schedule.to_dict()
        # ``Schedule.to_dict`` names the task ``task_id``; the map's row
        # (and its readers) name it ``task``. One box, one spelling each.
        box["task"] = schedule.task_id
    return box


def _provenance(task_id: str, box: dict[str, Any], replay_hash: str) -> Provenance:
    """The run declaration one screened cell belongs to."""
    return Provenance(
        env={"task": task_id, "fidelity": str(box.get("fidelity", "L0"))},
        dataset=task_id,
        dataset_version=str(box.get("budget_id", "")),
        code_sha=replay_hash,
        policy=str(box.get("budget_id", "")),
        links={"run_id": f"sec-{box.get('budget_id', task_id)}"},
    )


def _screen_status() -> Status:
    """A screen's status: measured, not adjudicated (TODO95 D5)."""
    return Status(
        gate_verdict=GateVerdict.PENDING,
        defect="",
        cause=FailureCause.UNKNOWN,
        severity=Severity.LOW,
        quarantine=False,
        maturity=Maturity.L0,
        uncertainty={},
        reproducibility=ReproducibilityClass.REPLAYABLE,
        assessment_procedure_version="sec-screen",
        ceec_link=None,
    )


def _control_stats(
    schedule: Schedule, device: str
) -> tuple[float | None, float | None]:
    """The base control over ``CONTROL_SEEDS`` seeds: mean and spread.

    One seed is a cell, not a control. A control whose mean sits inside the
    bar's 2σ band has no power, and its slice is refused before it is priced
    (TODO95 S2). The calibration rule is ``sec_pilot.calibrate_control``;
    this is its measurement at the screen's box.
    """
    del device  # the schedule carries the device the control runs on
    try:
        calibration = calibrate_control(schedule, evaluate=evaluate_cell)
    except Exception:  # ruff: ignore[blind-except] - a broken control must not end the screen
        logger.exception("P0 control cell failed at the box")
        return None, None
    if calibration is None:
        return None, None
    return calibration.control_mean, calibration.control_std


def _ruler(task_id: str) -> tuple[str, str]:
    """The task's primary metric key and the ruler string a map row carries."""
    from computronium.experiment.registry.task_registry import TaskRegistry

    spec = TaskRegistry().get(task_id)
    objective = next(
        (obj for obj in spec.objectives if obj.name == spec.primary_objective), None
    )
    key = (objective.payload_key if objective is not None else None) or "val_acc"
    chance = (
        f", chance {1 / spec.output_dim:.3f}"
        if spec.output_dim and spec.domain.value in {"vision", "tabular"}
        else ""
    )
    return key, f"{key} on {task_id} (primary {spec.primary_objective}{chance})"


_AXIS_DEFAULTS = {
    "substrate": "digital",
    "geometry": "feedforward",
    "dynamics": "instantaneous",
    "plasticity": "null",
    "credit": "gradient",
    "update": "euclidean",
}


# Companion axes are enumerated from the registry, never hardcoded: a second
# list would silently drop a primitive the system actually accepts. The
# oracle is `compose_configs` (the system's own validator), not a table.
def _axis_values(field: str) -> list[str]:
    from computronium.experiment.schema.axis import AXES_REGISTRIES

    default = _AXIS_DEFAULTS[field]
    values = sorted(
        name for name, spec in AXES_REGISTRIES[field].items() if spec.available
    )
    if default in values:
        values.remove(default)
        values.insert(0, default)
    return values


def _params_for(axes: dict[str, str], own_knobs: str | None = None) -> dict[str, Any]:
    """Structural hyperparameters a coordinate needs for the given axes.

    ``own_knobs`` names the varied axis of the viability pass: that axis runs
    at its own declared config defaults, companions stay at the base box
    (TODO95 S2). The base box shares one step size and one geometry width.
    """
    params: dict[str, Any] = {"credit.lr": 0.01, "update.lr": 0.01}
    geometry = axes["geometry"]
    if geometry in {
        "feedforward",
        "recurrent",
        "conv",
        "graph",
        "causal_transformer",
        "attention",
    }:
        params["geometry.hidden_dim"] = P0_HIDDEN_DIM
        params["geometry.depth"] = 2
    elif geometry in {"tile", "tile_mesh"}:
        params["geometry.neurons_per_tile"] = 8
        params["geometry.tiles_per_layer"] = 2
    elif geometry == "nca":
        params["geometry.grid_hw"] = (28, 28)
        params["geometry.input_dim"] = 1
    elif geometry == "spatial_lattice":
        params["geometry.lattice_dims"] = (8, 8)
    elif geometry == "routing":
        params["geometry.hidden_dim"] = P0_HIDDEN_DIM
        params["geometry.depth"] = 2
        params["geometry.num_experts"] = 8
        params["geometry.top_k"] = 2
    if geometry == "graph":
        # The graph topology also needs its connectivity; it is not a
        # feedforward width, so the first branch cannot carry it.
        params["geometry.edge_index"] = [[0, 1], [1, 0]]

    dynamics = axes["dynamics"]
    if dynamics in {
        "energy_minimization",
        "predictive_settling",
        "error_predictive_coding",
        "pc_alm",
    }:
        params["dynamics.max_steps"] = 10
        params["dynamics.step_size"] = 0.1
    elif dynamics == "spike_integration":
        params["dynamics.tau"] = 20.0
        params["dynamics.dt"] = 1.0
    elif dynamics == "diffusion":
        params["dynamics.step_size"] = 0.01
        params["dynamics.num_steps"] = 10

    if axes["credit"] in {
        "local_supervision",
        "local_goodness",
        "local_contrastive",
        "thermodynamic_contrast",
        "random_projections",
        "target_inversion",
        "pepita",
        "pc_alm",
        "forward_tangent",
        "score_function",
        "zeroth_order",
        "surrogate",
    }:
        params["credit.feedback_scale"] = 0.01
    if own_knobs is not None:
        params = _own_knob_overrides(axes, params, own_knobs)
    return params


def _own_knob_overrides(
    axes: dict[str, str], params: dict[str, Any], own_knobs: str
) -> dict[str, Any]:
    """The varied axis at its declared defaults, filtered by the system's verdict."""
    from computronium.experiment.schema.axis import StructuralAxis
    from computronium.experiment.schema.harvest import harvest_schema
    from computronium.experiment.sec_pilot import own_knob_params

    # Which of the primitive's declared defaults this selection can use is the
    # system's own availability verdict, not a second table.
    base = Coordinate(
        substrate=axes["substrate"],
        geometry=axes["geometry"],
        dynamics=axes["dynamics"],
        plasticity=axes["plasticity"],
        credit=axes["credit"],
        update=axes["update"],
        params=params,
    )
    active = harvest_schema().active(base)
    kind = StructuralAxis(own_knobs)
    accepted = set(active.values_for_axis(kind))
    kept = {
        key: value
        for key, value in params.items()
        if not key.startswith(f"{own_knobs}.")
    }
    kept.update({
        key: value
        for key, value in own_knob_params(own_knobs, axes[own_knobs]).items()
        if key.split(".", 1)[-1] in accepted
    })
    return kept


def _coordinate(axes: dict[str, str], own_knobs: str | None = None) -> Coordinate:
    return Coordinate(
        substrate=axes["substrate"],
        geometry=axes["geometry"],
        dynamics=axes["dynamics"],
        plasticity=axes["plasticity"],
        credit=axes["credit"],
        update=axes["update"],
        params=_params_for(axes, own_knobs=own_knobs),
    )


def _is_legal(coord: Coordinate) -> tuple[bool, str | None]:
    """Ask the system's own validator whether this cell can exist."""
    try:
        compose_configs(
            coordinate=coord,
            geometry={},
            input_shape=(1, 28, 28),
            output_dim=10,
        )
        return True, None
    except ValueError as exc:
        return False, str(exc)
    except Exception as exc:  # ruff: ignore[blind-except] - report, never crash the screen
        return False, f"{type(exc).__name__}: {exc}"


def _iter_legal_coordinates(
    entry: PrimitiveCensusEntry,
    limit: int = 64,
    own_knobs: bool = False,
) -> list[Coordinate]:
    """Compose-legal boxes for a primitive, nearest-to-default first.

    Base, then one-axis swaps, then two-axis swaps, deduplicated. ``compose_configs``
    (the system's validator) is the only source of truth. Training-time contracts
    (e.g. a surrogate credit needs a hard top-k gate) are *not* caught here — the
    caller must still run ``evaluate_cell`` and fall through to the next candidate.
    """
    if not entry.available:
        return []
    primitive_key = entry.id.split(".")[-1] if "." in entry.id else entry.id
    axis = axis_segment(entry.axis)
    base = dict(_AXIS_DEFAULTS)
    base[axis] = primitive_key
    own = axis if own_knobs else None

    def emit(axes: dict[str, str]) -> Coordinate | None:
        coord = _coordinate(axes, own_knobs=own)
        ok, _ = _is_legal(coord)
        return coord if ok else None

    seen_keys: set[tuple[tuple[str, str], ...]] = set()
    out: list[Coordinate] = []

    def attempt(axes: dict[str, str]) -> None:
        key = tuple(sorted(axes.items()))
        if key in seen_keys:
            return
        seen_keys.add(key)
        coord = emit(axes)
        if coord is not None:
            out.append(coord)

    attempt(base)
    # Geometry and dynamics are the most common constraint axes; try them before
    # substrate/plasticity/update so a training-time-only contract (e.g. a
    # surrogate credit needing a hard top-k gate on `routing`) is reached while
    # the candidate list is still short.
    priority = ["geometry", "dynamics", "credit", "plasticity", "substrate", "update"]
    companions = [a for a in priority if a in _AXIS_DEFAULTS and a != axis]
    for comp in companions:
        for value in _axis_values(comp):
            attempt({**base, comp: value})
    for i, first in enumerate(companions):
        for second in companions[i + 1 :]:
            for v1 in _axis_values(first):
                for v2 in _axis_values(second):
                    attempt({**base, first: v1, second: v2})
    return out[:limit]


def get_legal_coordinate_for_primitive(
    entry: PrimitiveCensusEntry,
    task_id: str = "mnist",
) -> Coordinate | None:
    """Nearest legal box for a primitive (compose-validated), or None."""
    coords = _iter_legal_coordinates(entry, limit=1)
    return coords[0] if coords else None


def _train_nearest(
    candidates: list[Coordinate], schedule: Schedule
) -> tuple[CellEvaluation | None, Coordinate | None, Exception | None, int, bool]:
    """Try compose-legal boxes nearest-to-default until one actually trains.

    A compose-legal box can still fail at training time (a surrogate credit with
    no hard top-k gate, a readout-replacing plasticity), so the run is the final
    oracle. Returns ``(evaluation, coordinate, last error, tried, timed out)``.
    """
    last_error: Exception | None = None
    started = time.monotonic()
    deadline = started + P0_PRIMITIVE_BUDGET_S

    def within_budget() -> bool:
        return time.monotonic() < deadline

    params = {
        "deadline_check": within_budget,
        "deadline_check_every_n_steps": 1,
    }
    tried = 0
    for coord in candidates:
        if not within_budget():
            return None, None, last_error, tried, True
        tried += 1
        try:
            return (
                evaluate_cell(coord, schedule, params=params),
                coord,
                None,
                tried,
                False,
            )
        except EvaluationError as exc:
            last_error = exc
            if getattr(exc, "cause", None) == "timeout":
                return None, None, last_error, tried, True
        except Exception as exc:  # ruff: ignore[blind-except] - one bad cell ends its cell, never the screen
            # A compose rejection is a refused row; any other failure
            # (a crash, a missing objective) is an execution fact (a defect).
            # Neither may abandon the other 74 rows.
            last_error = exc
    return None, None, last_error, tried, False


def _unmeasured_cell(  # ruff: ignore[too-many-arguments]
    entry: PrimitiveCensusEntry,
    *,
    tried: int,
    candidates: int,
    last_error: Exception | None,
    timed_out: bool,
    ruler: str,
    criterion: str,
    axis: str,
    primitive_key: str,
    box: dict[str, Any],
    own_knobs: bool = False,
) -> dict[str, Any]:
    """The cell a primitive emits when no compose-legal box trained."""
    if timed_out:
        logger.warning(f"P0 candidate budget spent: {entry.id}")
        return {
            "track": "P0",
            "primitive": entry.id,
            "status": "UNAVAILABLE",
            "reason": (
                f"cost cap: {P0_PRIMITIVE_BUDGET_S:.0f}s after "
                f"{tried}/{candidates} boxes; last error: {last_error}"
            ),
            "ruler": ruler,
            "box": box,
            "rule": "refused at the base box (cost cap)",
        }

    # No compose-legal box trained. Distinguish a compose rejection (never
    # should happen here — candidates are already compose-legal) from a
    # training-time contract failure.
    if isinstance(last_error, ValueError):
        logger.warning(f"P0 all boxes rejected: {entry.id}, error={last_error}")
        return {
            "track": "P0",
            "primitive": entry.id,
            "status": "UNAVAILABLE",
            "reason": f"validation: {last_error}",
            "ruler": ruler,
            "box": box,
            "rule": "refused at the base box (validation)",
        }
    logger.exception(f"P0 every legal box failed to train: {entry.id}")
    inert = binding_reason(
        axis, primitive_key, criterion=criterion, own_knobs=own_knobs
    )
    return {
        "track": "P0",
        "primitive": entry.id,
        "status": "DEFECT",
        "error": str(last_error),
        "cause": getattr(last_error, "cause", None),
        "ruler": ruler,
        "box": box,
        "rule": "base box, no legal box trained",
        "binding": "inert" if inert else "bound",
        "binding_reason": inert,
        "tried": tried,
    }


def _defect_for(
    eval_result: CellEvaluation, schedule: Schedule
) -> tuple[str | None, bool]:
    """An execution fact (non-finite metric, ceiling) or ``None`` when measured.

    A screen names a DEFECT only for an execution fact (TODO95 D5); the rule is
    one source, read by the breadth screen and the interaction slice.
    """
    metrics = dict(eval_result.metrics)
    val_acc = float(metrics.get("val_acc", 0.0))
    loss = float(metrics.get("loss", float("inf")))
    finite = math.isfinite(val_acc) and math.isfinite(loss)
    ceiling = schedule.param_budget
    within = ceiling <= 0 or eval_result.param_count <= ceiling * (
        1 + PARAM_BUDGET_TOLERANCE
    )
    if finite and within:
        return None, within
    return (
        "non-finite metric"
        if not finite
        else f"param_count {eval_result.param_count} over ceiling"
    ), within


def _screen_coordinate(  # ruff: ignore[too-many-arguments]
    entry: PrimitiveCensusEntry,
    candidates: list[Coordinate],
    schedule: Schedule,
    *,
    control_acc: float | None,
    ruler: str,
    criterion: str,
    axis: str,
    primitive_key: str,
    own_knobs: bool = False,
) -> dict[str, Any]:
    """Screen one primitive over its nearest compose-legal boxes.

    Emits one cell: the number, the box and the cost beside a MEASURED status;
    a DEFECT only for an execution fact (a crash, a non-finite metric, a
    ceiling violation). A bar is a gate's floor; a screen never mints a verdict
    (TODO95 D5), so no cell carries one.
    """
    box_binding = binding_reason(
        axis, primitive_key, criterion=criterion, own_knobs=own_knobs
    )
    if not candidates:
        return {
            "track": "P0",
            "primitive": entry.id,
            "status": "UNAVAILABLE",
            "reason": "no legal box or not available",
            "ruler": ruler,
            "box": _box_summary(_coordinate(_AXIS_DEFAULTS), schedule),
            "rule": "refused at the base box",
            "binding": "inert" if box_binding else "bound",
            "binding_reason": box_binding,
        }

    eval_result, coord, last_error, tried, timed_out = _train_nearest(
        candidates, schedule
    )
    if eval_result is None or coord is None:
        return _unmeasured_cell(
            entry,
            tried=tried,
            candidates=len(candidates),
            last_error=last_error,
            timed_out=timed_out,
            ruler=ruler,
            criterion=criterion,
            axis=axis,
            primitive_key=primitive_key,
            own_knobs=own_knobs,
            box=_box_summary(_coordinate(_AXIS_DEFAULTS), schedule),
        )

    defect, within = _defect_for(eval_result, schedule)
    metrics = dict(eval_result.metrics)
    val_acc = float(metrics.get("val_acc", 0.0))
    loss = float(metrics.get("loss", float("inf")))
    box = _box_summary(coord, schedule)
    record = record_from_evaluation(
        coordinate=coord,
        schedule=schedule,
        provenance=_provenance(schedule.task_id, box, coord.measurement_key(schedule)),
        evaluation=eval_result,
        status=_screen_status(),
        extra_payload={
            "defect": defect,
            "binding": box_binding or "bound",
            "swapped": getattr(coord, axis) != primitive_key,
        },
    )
    return {
        "track": "P0",
        "primitive": entry.id,
        "status": "DEFECT" if defect else "MEASURED",
        "val_acc": val_acc,
        "loss": loss,
        "param_count": eval_result.param_count,
        "within_ceiling": within,
        "metrics": metrics,
        "box": box,
        "ruler": ruler,
        "control_val_acc": control_acc,
        "binding": "inert" if box_binding else "bound",
        "binding_reason": box_binding,
        "swapped": getattr(coord, axis) != primitive_key,
        "defect": defect,
        "walltime_s": eval_result.walltime_s,
        "resource": resource_vector(metrics),
        "record": record.to_dict(),
    }


def _task_bar(task_id: str) -> Any:
    from computronium.experiment.registry.task_registry import (
        TaskRegistry,
        primary_pass_bar,
    )

    return primary_pass_bar(TaskRegistry().get(task_id))


def _param_budget(task_id: str) -> int:
    """The family's declared parameter ceiling; 0 when undeclared."""
    schedule = base_schedule(task_id)
    return 0 if schedule is None else schedule.param_budget


def _refused_cell(
    entry: PrimitiveCensusEntry,
    reason: str,
    ruler: str,
    box: dict[str, Any],
) -> dict[str, Any]:
    """One cell a slice refuses before it is priced: the trigger is the row.

    A refusal is a box statement, so the box it was refused at travels with
    it; otherwise the row cannot be told apart from a box it was never near.
    """
    return {
        "track": "P0",
        "primitive": entry.id,
        "status": "UNAVAILABLE",
        "reason": reason,
        "ruler": ruler,
        "box": box,
        "rule": "refused at the base box",
    }


def _refused_cells(
    entries: list[PrimitiveCensusEntry],
    reason: str,
    ruler: str,
    box: dict[str, Any],
) -> list[dict[str, Any]]:
    """A slice refused at one box: one row per primitive, each with the box."""
    return [_refused_cell(entry, reason, ruler, box) for entry in entries]


def _screen_entries(
    entries: list[PrimitiveCensusEntry],
    schedule: Schedule,
    base_box: dict[str, Any],
    *,
    control_acc: float | None,
    ruler: str,
    criterion: str,
    own_knobs: bool,
) -> list[dict[str, Any]]:
    """Screen every entry at the base box: one cell each, refusals included."""
    from computronium.experiment.sec_pilot import refusal_for

    cells: list[dict[str, Any]] = []
    for entry in entries:
        family_reason = refusal_for(entry, schedule.task_id)
        if family_reason is not None:
            logger.info(f"P0 refused by task family: {entry.id}")
            cells.append(_refused_cell(entry, family_reason, ruler, base_box))
            continue
        logger.info(f"P0 screening: {entry.id}")
        axis = axis_segment(entry.axis)
        cells.append(
            _screen_coordinate(
                entry,
                _iter_legal_coordinates(
                    entry, limit=P0_MAX_COORDINATES, own_knobs=own_knobs
                ),
                schedule,
                control_acc=control_acc,
                ruler=ruler,
                criterion=criterion,
                axis=axis,
                primitive_key=entry.id.split(".")[-1],
                own_knobs=own_knobs,
            )
        )
    return cells


def run_p0_track(
    out_dir: Path,
    census_entries: list[PrimitiveCensusEntry],
    max_primitives: int = 6,
    device: str = "auto",
    breadth: str = "delta",
    own_knobs: bool = False,
) -> dict[str, Any]:
    """Run Track P0: Breadth screen for primitives.

    Delta mode: only unscreened, defect, or failed primitives.
    Full mode: all primitives (re-screen everything).
    ``own_knobs`` runs the viability box: each varied axis at its own declared
    config defaults instead of the shared comparison box (TODO95 S2).
    """
    logger.info(f"Starting Track P0: {breadth} breadth screen")

    # Load map to check which primitives have been screened
    map_path = out_dir / "map.json"
    screened_primitives = set()
    if map_path.exists():
        map_data = json.loads(map_path.read_text())
        for prim_id, entry in map_data.get("primitives", {}).items():
            if entry.get("last_screened") and entry.get("status") in {
                "measured",
                "defect",
                "refused",
            }:
                screened_primitives.add(prim_id)

    if breadth == "delta":
        # Filter to delta: unscreened, defect, or failed (from map status)
        entries_to_screen = [
            e
            for e in census_entries
            if e.id not in screened_primitives
            or e.screen_status in {"defect", "failed"}
        ]
    else:  # full
        entries_to_screen = list(census_entries)

    # Limit to max_primitives
    entries_to_screen = entries_to_screen[:max_primitives]

    logger.info(
        f"P0 {breadth}: {len(entries_to_screen)} primitives to screen "
        f"(from {len(census_entries)} total)"
    )

    schedule = base_schedule(P0_TASK, device)
    criterion, ruler = _ruler(P0_TASK)
    base_box = (
        {} if schedule is None else _box_summary(_coordinate(_AXIS_DEFAULTS), schedule)
    )
    control_acc: float | None = None
    control_spread: float | None = None
    powered = False
    bar = _task_bar(P0_TASK)
    results: list[dict[str, Any]] = []
    if schedule is None:
        # A family with no declared base has no box to price and no control
        # to read: its slice is refused at the census's own gap (TODO95 S2).
        reason = f"{P0_TASK} declares no base box; the slice is refused"
        results = _refused_cells(entries_to_screen, reason, ruler, base_box)
    else:
        control_acc, control_spread = _control_stats(schedule, device)
        logger.info(
            f"P0 control at this box: val_acc={control_acc} "
            f"(spread {control_spread}, bar {None if bar is None else bar.value})"
        )
        powered = control_acc is not None and (bar is None or control_acc > bar.value)
        if not powered:
            # The control is inside the bar's band: the slice measures noise,
            # so it is refused before it is priced (TODO95 S2).
            reason = (
                f"control at chance at this box: val_acc={control_acc} inside "
                f"bar {None if bar is None else bar.value}; slice refused "
                "before it is priced (TODO95 S2)"
            )
            results = _refused_cells(entries_to_screen, reason, ruler, base_box)
        else:
            results = _screen_entries(
                entries_to_screen,
                schedule,
                base_box,
                control_acc=control_acc,
                ruler=ruler,
                criterion=criterion,
                own_knobs=own_knobs,
            )

    total = len(entries_to_screen)
    measured_count = sum(1 for cell in results if cell["status"] == "MEASURED")
    defect_count = sum(1 for cell in results if cell["status"] == "DEFECT")
    unavailable_count = sum(1 for cell in results if cell["status"] == "UNAVAILABLE")
    box_defect_count = sum(1 for cell in results if cell.get("within_ceiling") is False)
    defect_rate = defect_count / total if total > 0 else 0.0
    pause_r = defect_rate > 0.2 or not powered

    result_summary = {
        "track": "P0",
        "screened": total,
        "measured": measured_count,
        "defect": defect_count,
        "unavailable": unavailable_count,
        "box_defect": box_defect_count,
        "control_val_acc": control_acc,
        "control_spread": control_spread,
        "bar": None if bar is None else bar.value,
        "own_knobs": own_knobs,
        "ruler": ruler,
        "base_box": base_box,
        "defect_rate": defect_rate,
        "pause_r": pause_r,
        "cells": results,
    }

    logger.info(
        f"P0 complete: screened={total}, measured={measured_count}, "
        f"defect={defect_count}, unavailable={unavailable_count}, "
        f"box_defect={box_defect_count}"
    )
    return result_summary


# ============================================================
# Track P1: Confirmation (3 seeds, paired)
# ============================================================

P1_SEEDS = 3
P1_EPOCHS = 1
P1_BATCH_LIMIT = 1


def run_p1_track(
    out_dir: Path,
    p0_passes: list[str],  # primitive IDs that passed P0
    census_entries: list[PrimitiveCensusEntry],
    device: str = "auto",
) -> dict[str, Any]:
    """Run Track P1: Confirmation for P0 passes (3 seeds, paired)."""
    logger.info(f"Starting Track P1: Confirmation for {len(p0_passes)} primitives")

    # Map primitive ID to census entry
    entry_map = {e.id: e for e in census_entries}

    results: list[dict[str, Any]] = []
    surprise_count = 0

    for prim_id in p0_passes:
        entry = entry_map.get(prim_id)
        if entry is None:
            continue

        coord = get_legal_coordinate_for_primitive(entry)
        if coord is None:
            continue

        seeds = list(range(P1_SEEDS))
        schedules = [
            Schedule(
                fidelity="L0",
                seed=seed,
                n_seeds=1,
                epochs=P1_EPOCHS,
                batch_limit=P1_BATCH_LIMIT,
                budget_id="p1",
                task_id="mnist",
                param_budget=_param_budget(P0_TASK),
                device=device,
                deterministic=True,
                num_workers=0,
                precision="fp32",
                checkpoint_every_n=0,
            )
            for seed in seeds
        ]

        seed_results = []
        for schedule in schedules:
            try:
                eval_result: CellEvaluation = evaluate_cell(coord, schedule)
                val_acc = eval_result.metrics.get("val_acc", 0.0)
                seed_results.append(val_acc)
            except EvaluationError:
                seed_results.append(0.0)

        # Surprise: paired effect > 2δ (simplified: mean > chance + 2σ)
        mean_acc = sum(seed_results) / len(seed_results) if seed_results else 0.0
        std_acc = (
            (sum((x - mean_acc) ** 2 for x in seed_results) / len(seed_results)) ** 0.5
            if len(seed_results) > 1
            else 0.0
        )
        chance = 0.1
        delta = std_acc
        effect = mean_acc - chance
        is_surprise = effect > 2 * delta and delta > 0

        if is_surprise:
            surprise_count += 1

        results.append({
            "track": "P1",
            "primitive": prim_id,
            "seed_results": seed_results,
            "mean_acc": mean_acc,
            "std_acc": std_acc,
            "effect": effect,
            "delta": delta,
            "surprise": is_surprise,
        })

    result_summary = {
        "track": "P1",
        "confirmed": len(results),
        "surprises": surprise_count,
        "cells": results,
    }

    logger.info(f"P1 complete: confirmed={len(results)}, surprises={surprise_count}")
    return result_summary


# ============================================================
# Track P3: The interaction slice
# ============================================================


def _measure(coord: Coordinate, run: Schedule) -> dict[str, Any]:
    """One screened cell: status, number, cost, box and replay hash.

    A compose-legal box is checked before it is priced; a training-time
    contract failure is a defect with its mechanism named, never a crash. The
    record is written from the evaluation, so the replay hash is the run's
    provenance — one source read by the interaction slice and the deep dive.
    """
    box = _box_summary(coord, run)
    legal, reason = _is_legal(coord)
    if not legal:
        return {
            "status": "refused",
            "val_acc": None,
            "loss": None,
            "walltime_s": None,
            "replay_hash": None,
            "box": box,
            "reason": reason,
        }
    try:
        eval_result = evaluate_cell(coord, run)
    except EvaluationError as exc:
        return {
            "status": "defect",
            "val_acc": None,
            "loss": None,
            "walltime_s": None,
            "replay_hash": None,
            "box": box,
            "reason": f"{exc.cause}: {exc}",
        }
    except Exception as exc:  # ruff: ignore[blind-except] - one bad cell, never the slice
        return {
            "status": "defect",
            "val_acc": None,
            "loss": None,
            "walltime_s": None,
            "replay_hash": None,
            "box": box,
            "reason": f"{type(exc).__name__}: {exc}",
        }

    defect, _within = _defect_for(eval_result, run)
    metrics = dict(eval_result.metrics)
    record = record_from_evaluation(
        coordinate=coord,
        schedule=run,
        provenance=_provenance(run.task_id, box, coord.measurement_key(run)),
        evaluation=eval_result,
        status=_screen_status(),
        extra_payload={"defect": defect},
    )
    return {
        "status": "defect" if defect else "measured",
        "val_acc": None if defect else float(metrics.get("val_acc", 0.0)),
        "loss": float(metrics.get("loss", float("inf"))),
        "walltime_s": eval_result.walltime_s,
        "replay_hash": record.to_dict()["provenance"]["code_sha"],
        "box": box,
        "reason": defect,
    }


def _interaction_cell(
    levels: dict[str, str],
    schedule: Schedule,
    *,
    seed: int,
) -> InteractionCell:
    """One run of the factorial: its box, its seed and its replay hash."""
    from computronium.experiment.sec_interaction import InteractionCell

    axes = {**_AXIS_DEFAULTS, **levels}
    measured = _measure(_coordinate(axes), replace(schedule, seed=seed, n_seeds=1))
    return InteractionCell(
        levels=dict(levels),
        seed=seed,
        status=measured["status"],
        val_acc=measured["val_acc"],
        loss=measured["loss"],
        walltime_s=measured["walltime_s"],
        replay_hash=measured["replay_hash"],
        box=measured["box"],
        reason=measured["reason"],
    )


def legal_levels(levels: dict[str, str]) -> bool:
    """The system's validator on a pair's levels: it seats or refuses the cell."""
    legal, _reason = _is_legal(_coordinate({**_AXIS_DEFAULTS, **levels}))
    return legal


def _p3_setup(out_dir: Path, device: str) -> tuple[SlicePlan, Schedule] | None:
    """The map's slice and its base schedule, or ``None`` when P3 is refused."""
    from computronium.experiment.sec_interaction import axis_spreads, plan_slice

    map_path = out_dir / "map.json"
    if not map_path.exists():
        logger.warning("P3: no map.json — the census is not screened; slice refused")
        return None
    map_data = json.loads(map_path.read_text())
    if map_data.get("version") != MAP_VERSION:
        logger.warning(
            f"P3: map version {map_data.get('version')} is not {MAP_VERSION}; "
            "slice refused"
        )
        return None
    if len(axis_spreads(map_data)) < 2:
        logger.warning("P3: fewer than two axes rank at this box; slice refused")
        return None
    plan = plan_slice(map_data, legal=legal_levels)
    if plan is None:
        logger.warning("P3: the top pair seats no legal 2×2 at this box; slice refused")
        return None
    task_id = str((map_data.get("base") or {}).get("task") or P0_TASK)
    schedule = base_schedule(task_id, device)
    if schedule is None:
        logger.warning(f"P3: {task_id} declares no base box; slice refused")
        return None
    return plan, schedule


def run_p3_track(out_dir: Path, device: str = "auto") -> dict[str, Any] | None:
    """Run Track P3: the pair the map allocates, at the base box (TODO95 S3).

    The base cell is the control: its three seeds carry the bar check and the
    2×2's baseline in one instrument. A control inside the bar marks the slice
    ``no_power`` before it is priced; the other three cells screen at one seed,
    then the pair confirms at three seeds, so the effect carries an interval.

    Returns ``None`` when the slice is refused: no map, no ranked pair, or no
    declared base box.
    """
    from computronium.experiment.sec_interaction import INTERACTION_SEEDS

    setup = _p3_setup(out_dir, device)
    if setup is None:
        return None
    plan, schedule = setup
    levels = plan.combinations()
    base_runs = [
        _interaction_cell(dict(levels[0]), schedule, seed=seed)
        for seed in range(INTERACTION_SEEDS)
    ]
    base_values = [cell.val_acc for cell in base_runs if cell.val_acc is not None]
    control = sum(base_values) / len(base_values) if base_values else None
    bar = _task_bar(schedule.task_id)
    if control is None or (bar is not None and control <= bar.value):
        return _no_power_slice(plan, schedule, base_runs, control, bar)
    return _confirmed_slice(plan, schedule, base_runs, levels, control)


def _no_power_slice(
    plan: SlicePlan,
    schedule: Schedule,
    base_runs: list[InteractionCell],
    control: float | None,
    bar: Any,
) -> dict[str, Any]:
    """A control inside the bar marks the slice; it never prices the cells."""
    from computronium.experiment.sec_interaction import InteractionCell

    reason = (
        f"control at chance at this box: val_acc={control} inside bar "
        f"{None if bar is None else bar.value}; the slice is refused before "
        "it is priced (TODO95 S2)"
    )
    box = _box_summary(_coordinate(_AXIS_DEFAULTS), schedule)
    cells: list[InteractionCell] = list(base_runs)
    for level in plan.combinations()[1:]:
        cells.append(
            InteractionCell(
                levels=level,
                seed=0,
                status="refused",
                val_acc=None,
                loss=None,
                walltime_s=None,
                replay_hash=None,
                box=box,
                reason=reason,
            )
        )
    logger.warning(f"P3 marked no power: {reason}")
    return _interaction_result(
        plan, cells, status="no_power", stop_reason=reason, control=control
    )


def _confirmed_slice(
    plan: SlicePlan,
    schedule: Schedule,
    base_runs: list[InteractionCell],
    levels: list[dict[str, str]],
    control: float,
) -> dict[str, Any]:
    """One seed screens each cell; three seeds confirm the pair (TODO95 S3)."""
    from computronium.experiment.sec_interaction import (
        INTERACTION_SEEDS,
        interaction_effect,
    )

    started = time.monotonic()
    screened = [
        _interaction_cell(dict(level), schedule, seed=0) for level in levels[1:]
    ]
    cells = [*base_runs, *screened]
    failed = next((cell for cell in screened if cell.status != "measured"), None)
    if failed is not None:
        reason = f"{failed.levels} did not measure: {failed.reason or failed.status}"
        logger.warning(f"P3 incomplete: {reason}")
        return _interaction_result(
            plan,
            cells,
            status="incomplete",
            stop_reason=reason,
            control=control,
            screened=interaction_effect(plan, cells),
        )

    # The extra seeds are declared here, before the pair's number exists, so
    # the confirm is fixed-n and cannot be stopped early (TODO95 S3).
    for seed in range(1, INTERACTION_SEEDS):
        cells.extend(
            _interaction_cell(dict(level), schedule, seed=seed) for level in levels[1:]
        )
    effect = interaction_effect(plan, cells)
    walltime = time.monotonic() - started
    logger.info(
        f"P3 complete: pair={plan.axes}, "
        f"effect={None if effect is None else effect.effect}"
    )
    return _interaction_result(
        plan,
        cells,
        status="measured" if effect is not None else "incomplete",
        stop_reason=(
            "rung 3: the pair's 2×2 at three seeds"
            if effect is not None
            else "the confirmed 2×2 did not measure"
        ),
        control=control,
        screened=interaction_effect(plan, cells[: 2 * INTERACTION_SEEDS]),
        effect=effect,
        walltime_s=walltime,
    )


def _interaction_result(
    plan: SlicePlan,
    cells: list[InteractionCell],
    *,
    status: str,
    stop_reason: str,
    control: float | None,
    screened: InteractionEffect | None = None,
    effect: InteractionEffect | None = None,
    walltime_s: float | None = None,
) -> dict[str, Any]:
    """The interaction layer: the design, the cells and the effect."""
    from computronium.experiment.sec_interaction import analysis

    layer = analysis(plan)
    layer |= {
        "cells": [cell.to_dict() for cell in cells],
        "status": status,
        "stop_reason": stop_reason,
        "control_val_acc": control,
        "screened": None if screened is None else screened.to_dict(),
        "effect": None if effect is None else effect.to_dict(),
        "walltime_s": walltime_s,
    }
    return {"track": "P3", "interaction": layer, "cells": layer["cells"]}


# ============================================================
# Track P4: The deep dive (one claim, one box)
# ============================================================

#: The committed registration the claim reads. The margin is declared in the
#: repo before the run, so a session that cannot name its claim refuses.
DEEP_DIVE_REGISTRATION = Path("configs/preregistrations/sec_deep_dive.json")


def _deep_dive_coordinate(candidate: Any, factor: float) -> Coordinate:
    """The candidate's base box with its primary knob at one ladder point."""
    axes = {**_AXIS_DEFAULTS, candidate.axis: candidate.level}
    coord = _coordinate(axes)
    return replace(
        coord,
        params={**coord.params, candidate.knob: candidate.default * factor},
    )


def _deep_dive_setup(
    out_dir: Path, device: str, registration_path: Path
) -> tuple[Any, Any, Schedule] | None:
    """The map's candidate, the committed claim and the base box, or ``None``."""
    from computronium.experiment.sec_deep_dive import (
        load_registration,
        select_candidate,
    )

    map_path = out_dir / "map.json"
    if not map_path.exists():
        logger.warning("P4: no map.json — the census is not screened; dive refused")
        return None
    map_data = json.loads(map_path.read_text())
    if map_data.get("version") != MAP_VERSION:
        logger.warning(
            f"P4: map version {map_data.get('version')} is not {MAP_VERSION}; "
            "dive refused"
        )
        return None
    candidate = select_candidate(map_data)
    if candidate is None:
        logger.warning("P4: no surprising bound row with a declared knob; dive refused")
        return None
    task_id = str((map_data.get("base") or {}).get("task") or P0_TASK)
    schedule = base_schedule(task_id, device)
    if schedule is None:
        logger.warning(f"P4: {task_id} declares no base box; dive refused")
        return None
    registration = load_registration(registration_path, schedule)
    if registration is None:
        logger.warning(
            f"P4: no pre-registration for {task_id} at {registration_path}; "
            "the claim is refused before the first cell (TODO95 S4)"
        )
        return None
    return candidate, registration, schedule


def run_p4_track(
    out_dir: Path,
    device: str = "auto",
    *,
    registration_path: Path | None = None,
) -> dict[str, Any] | None:
    """Run Track P4: the map's surprising bound row, at one box (TODO95 S4).

    The ladder screens three points on the primitive's primary knob at one seed;
    the best point then pairs five seeds against the primitive's own default at
    the matched base box. The margin is read from the committed registration,
    so the claim is fixed-n and cannot be stopped early.

    Returns ``None`` when the dive is refused: no map, no candidate, no
    declared base box, or no pre-registered claim at this box.
    """
    from computronium.experiment.sec_deep_dive import best_rung

    setup = _deep_dive_setup(
        out_dir, device, registration_path or DEEP_DIVE_REGISTRATION
    )
    if setup is None:
        return None
    candidate, registration, schedule = setup
    started = time.monotonic()
    rungs = _ladder(candidate, schedule)
    best = best_rung(tuple(rungs))
    bar = _task_bar(schedule.task_id)
    if best is None or (bar is not None and (best.val_acc or 0.0) <= bar.value):
        reason = (
            "rung 2: no ladder point clears the bar at this box; the knob is "
            "priced, not claimed (a capability gap, TODO95 P4)"
        )
        return _deep_dive_result(
            candidate,
            tuple(rungs),
            best,
            (),
            None,
            registration,
            verdict="coordinate",
            stop_reason=reason,
            started=started,
        )

    cells = _paired_cells(candidate, schedule, best.factor)
    failed = next((cell for cell in cells if cell.status == "defect"), None)
    if failed is not None:
        return _deep_dive_result(
            candidate,
            tuple(rungs),
            best,
            tuple(cells),
            None,
            registration,
            verdict="defect",
            stop_reason=(
                f"rung 4: the {failed.arm} arm at seed {failed.seed} is an "
                f"execution fact: {failed.reason}"
            ),
            started=started,
        )
    return _pair_verdict(candidate, rungs, best, cells, registration, schedule, started)


def _ladder(candidate: Any, schedule: Schedule) -> list[Any]:
    """The three-point ladder at one seed: the knob's declared neighbours."""
    from computronium.experiment.sec_deep_dive import LadderRung, ladder_points

    rungs: list[LadderRung] = []
    for factor, value in ladder_points(candidate):
        measured = _measure(
            _deep_dive_coordinate(candidate, factor),
            replace(schedule, seed=0, n_seeds=1),
        )
        rungs.append(
            LadderRung(
                factor=factor,
                value=value,
                status=measured["status"],
                val_acc=measured["val_acc"],
                walltime_s=measured["walltime_s"],
                replay_hash=measured["replay_hash"],
                box=measured["box"],
                reason=measured["reason"],
            )
        )
    return rungs


def _paired_cells(candidate: Any, schedule: Schedule, treatment: float) -> list[Any]:
    """Five index-matched seeds per arm at the matched base box."""
    from computronium.experiment.sec_deep_dive import CLAIM_SEEDS, PairedCell

    cells: list[PairedCell] = []
    for seed in range(CLAIM_SEEDS):
        for arm, factor in (("control", 1.0), ("treatment", treatment)):
            measured = _measure(
                _deep_dive_coordinate(candidate, factor),
                replace(schedule, seed=seed, n_seeds=1),
            )
            cells.append(
                PairedCell(
                    arm=arm,
                    factor=factor,
                    seed=seed,
                    status=measured["status"],
                    val_acc=measured["val_acc"],
                    loss=measured["loss"],
                    walltime_s=measured["walltime_s"],
                    replay_hash=measured["replay_hash"],
                    box=measured["box"],
                    reason=measured["reason"],
                )
            )
    return cells


def _pair_verdict(  # ruff: ignore[too-many-arguments]
    candidate: Any,
    rungs: list[Any],
    best: Any,
    cells: list[Any],
    registration: Any,
    schedule: Schedule,
    started: float,
) -> dict[str, Any]:
    """The pair's verdict: a claim, a coordinate, or an inert knob.

    The comparison is fixed-n: every seed is run before ``passes`` is asked.
    Two arms that agree at every seed are bit-identical, so their difference is
    structurally zero and the pair has no power — it is marked, not priced.
    """
    from dataclasses import asdict

    from computronium.experiment.sec_deep_dive import claim_verdict
    from computronium.validation.preregistration import paired_comparison

    treatments = [cell for cell in cells if cell.arm == "treatment"]
    controls = [cell for cell in cells if cell.arm == "control"]
    identical = all(
        treatment.val_acc == control.val_acc
        for treatment, control in zip(treatments, controls, strict=True)
    )
    if identical:
        return _deep_dive_result(
            candidate,
            tuple(rungs),
            best,
            tuple(cells),
            None,
            registration,
            verdict="coordinate",
            stop_reason=(
                "rung 4: the arms are identical at every seed — the knob does "
                "not bind at this box, so the pair has no power and is marked, "
                "not priced (a capability gap, TODO95 S4)"
            ),
            started=started,
            no_power=True,
        )
    paired = paired_comparison(
        [float(cell.val_acc or 0.0) for cell in treatments],
        [float(cell.val_acc or 0.0) for cell in controls],
        seed=schedule.seed,
    )
    verdict = claim_verdict(paired, registration, schedule)
    logger.info(
        f"P4 complete: {candidate.primitive} best={best.factor} "
        f"effect={paired.mean_diff:.4f} verdict={verdict}"
    )
    return _deep_dive_result(
        candidate,
        tuple(rungs),
        best,
        tuple(cells),
        asdict(paired),
        registration,
        verdict=verdict,
        stop_reason=(
            "rung 4: five paired seeds at the base box; the CI clears the "
            "registered margin"
            if verdict == "claim"
            else "rung 4: five paired seeds at the base box; the effect sits "
            "inside the registered margin"
        ),
        started=started,
    )


def _deep_dive_result(  # ruff: ignore[too-many-arguments]
    candidate: Any,
    rungs: tuple[Any, ...],
    best: Any,
    cells: tuple[Any, ...],
    paired: dict[str, Any] | None,
    registration: Any,
    *,
    verdict: str,
    stop_reason: str,
    started: float,
    no_power: bool = False,
) -> dict[str, Any]:
    """The deep dive layer: the candidate, the ladder, the pair and the claim."""
    from computronium.experiment.sec_deep_dive import DeepDive

    measured = [rung.val_acc for rung in rungs if rung.status == "measured"]
    dive = DeepDive(
        candidate=candidate,
        rungs=rungs,
        best=best,
        cells=cells,
        paired=paired,
        claim=registration.to_dict(),
        verdict=verdict,
        stop_reason=stop_reason,
        walltime_s=time.monotonic() - started,
        knob_binds=len(set(measured)) > 1,
        no_power=no_power,
    )
    layer = dive.to_dict()
    return {"track": "P4", "deep_dive": layer, "cells": layer["cells"]}


# ============================================================
# Portfolio & Map Updates
# ============================================================


def _portfolio_track(portfolio: dict[str, Any], track_id: str) -> dict[str, Any]:
    """The portfolio's row for a track, created from the declared default.

    An older portfolio may predate a track; the default row is the one source
    of a track's rank and kill rule, so the update never invents a second one.
    """
    from dataclasses import asdict

    from computronium.experiment.sec_init import DEFAULT_TRACKS

    for track in portfolio.setdefault("tracks", []):
        if track["track"] == track_id:
            return track
    default = asdict(next(t for t in DEFAULT_TRACKS if t.track == track_id))
    portfolio["tracks"].append(default)
    return default


def update_portfolio(
    out_dir: Path,
    r1_result: dict | None,
    r2_result: dict | None,
    p0_result: dict | None,
    p1_result: dict | None,
    p3_result: dict | None = None,
    p4_result: dict | None = None,
) -> None:
    """Update portfolio.json with track results."""
    portfolio_path = out_dir / "portfolio.json"

    if portfolio_path.exists():
        portfolio = json.loads(portfolio_path.read_text())
    else:
        portfolio = {"tracks": [], "active_track": "R1", "session_count": 0}

    portfolio["session_count"] += 1
    portfolio["last_session"] = datetime.now().isoformat()

    if r1_result:
        track = _portfolio_track(portfolio, "R1")
        track["last_result"] = {
            "gap_worst": r1_result["gap_worst"],
            "gap_mean": r1_result["gap_mean"],
            "local_worst": r1_result["local_worst"],
            "backprop_worst": r1_result["backprop_worst"],
            "local_forgetting_mean": r1_result["local_forgetting_mean"],
            "backprop_forgetting_mean": r1_result["backprop_forgetting_mean"],
            "kill_rule_triggered": r1_result["kill_rule_triggered"],
            "surprise": r1_result["surprise"],
        }
        track["budget_used"]["cells"] = len(r1_result["cells"])
        track["budget_used"]["seeds"] = len({c["seed"] for c in r1_result["cells"]})
        track["contention"] = False

    if r2_result:
        track = _portfolio_track(portfolio, "R2")
        track["last_result"] = {
            "gap_worst": r2_result["gap_worst"],
            "gap_mean": r2_result["gap_mean"],
            "local_worst": r2_result["local_worst"],
            "backprop_worst": r2_result["backprop_worst"],
            "local_forgetting_mean": r2_result["local_forgetting_mean"],
            "backprop_forgetting_mean": r2_result["backprop_forgetting_mean"],
            "kill_rule_triggered": r2_result["kill_rule_triggered"],
            "surprise": r2_result["surprise"],
        }
        track["budget_used"]["cells"] = len(r2_result["cells"])
        track["budget_used"]["seeds"] = len({c["seed"] for c in r2_result["cells"]})
        track["contention"] = False

    if p0_result:
        track = _portfolio_track(portfolio, "P0")
        track["last_result"] = {
            "measured": p0_result["measured"],
            "defect": p0_result["defect"],
            "unavailable": p0_result["unavailable"],
            "box_defect": p0_result["box_defect"],
            "control_val_acc": p0_result["control_val_acc"],
            "defect_rate": p0_result["defect_rate"],
            "pause_r": p0_result["pause_r"],
        }
        track["budget_used"]["cells"] = p0_result["screened"]
        track["budget_used"]["primitives"] = p0_result["screened"]

    if p1_result:
        track = _portfolio_track(portfolio, "P1")
        track["last_result"] = {
            "confirmed": p1_result["confirmed"],
            "surprises": p1_result["surprises"],
        }
        track["budget_used"]["cells"] = p1_result["confirmed"] * P1_SEEDS
        track["budget_used"]["seeds"] = P1_SEEDS

    if p3_result:
        layer = p3_result["interaction"]
        track = _portfolio_track(portfolio, "P3")
        track["last_result"] = {
            "pair": layer["pair"],
            "status": layer["status"],
            "effect": None if layer["effect"] is None else layer["effect"]["effect"],
            "seeds": None if layer["effect"] is None else layer["effect"]["seeds"],
            "stop_reason": layer["stop_reason"],
        }
        track["budget_used"]["cells"] = len(p3_result["cells"])
        track["budget_used"]["seeds"] = sum(
            1 for cell in p3_result["cells"] if cell["status"] == "measured"
        )

    if p4_result:
        layer = p4_result["deep_dive"]
        track = _portfolio_track(portfolio, "P4")
        effect = layer.get("effect")
        track["last_result"] = {
            "primitive": layer["candidate"]["primitive"],
            "knob": layer["candidate"]["knob"],
            "verdict": layer["verdict"],
            "effect": None if effect is None else effect["mean_diff"],
            "ci": None if effect is None else [effect["ci_lower"], effect["ci_upper"]],
            "n_max": None if effect is None else effect["n"],
            "stop_reason": layer["stop_reason"],
        }
        track["budget_used"]["cells"] = len(layer["ladder"]) + len(layer["cells"])
        track["budget_used"]["seeds"] = len({cell["seed"] for cell in layer["cells"]})

    portfolio_path.write_text(json.dumps(portfolio, indent=2, default=str))
    logger.info(f"Portfolio updated: {portfolio_path}")


def update_cell_log(out_dir: Path, all_results: list[dict]) -> None:
    """Append every cell to cells.jsonl, record-first (TODO95 P0b).

    One line per cell: ``{"screen": <cell>, "record": <Record|None>}``. The
    record is the cell's evidence — its box and replay hash; the screen is what
    the run measured and how the varied axis bound. Both keys are always
    present, so a reader never has to guess which shape it holds.
    """
    cell_log_path = out_dir / "cells.jsonl"
    with cell_log_path.open("a") as f:
        for result in all_results:
            screen = {k: v for k, v in result.items() if k != "record"}
            f.write(
                json.dumps(
                    {"screen": screen, "record": result.get("record")},
                    default=str,
                )
                + "\n"
            )
    logger.info(f"Cell log updated: {cell_log_path} (+{len(all_results)} entries)")


def _map_row(
    entry: PrimitiveCensusEntry, cell: dict[str, Any] | None
) -> dict[str, Any]:
    """One map row: the primitive, its task, ruler, box, control and resources.

    The row always exists. A row with no cell is `unmeasured`; a row the
    pipeline refused carries its reopen trigger; a row that ran carries the
    number and the box beside it (TODO95 P2).
    """
    row: dict[str, Any] = {
        "primitive": entry.id,
        "axis": entry.axis,
        "capability": entry.capability_card,
        "status": "unmeasured",
        "binding": None,
        "binding_reason": None,
        "task": None,
        "ruler": None,
        "rule": None,
        "box": {},
        "control": None,
        "measurement": None,
        "resource": {},
        "swapped": False,
        "defect": None,
        "trigger": None,
        "replay_hash": None,
        "last_screened": None,
    }
    if not entry.available:
        row["status"] = "refused"
        row["trigger"] = entry.unavailable_reason
        return row
    if cell is None:
        return row

    status = {
        "MEASURED": "measured",
        "DEFECT": "defect",
        "UNAVAILABLE": "refused",
    }[cell["status"]]
    row["status"] = status
    row["last_screened"] = datetime.now().isoformat()
    row["trigger"] = cell.get("reason")
    row["defect"] = cell.get("defect") or cell.get("error")
    if "box" in cell:
        box = cell["box"]
        row["box"] = box
        row["task"] = box.get("task")
        row["binding"] = cell.get("binding")
        row["binding_reason"] = cell.get("binding_reason")
        row["swapped"] = cell.get("swapped", False)
        row["rule"] = cell.get("rule") or (
            "nearest-legal swap" if row["swapped"] else "base box, one axis varied"
        )
        row["ruler"] = cell.get("ruler")
        row["control"] = {"val_acc": cell.get("control_val_acc")}
        row["resource"] = {
            "walltime_s": cell.get("walltime_s"),
            "param_count": cell.get("param_count"),
            "within_ceiling": cell.get("within_ceiling"),
            **(cell.get("resource") or {}),
        }
        record = cell.get("record")
        if record:
            # The replay hash is the record's provenance, not a second hash:
            # a row whose claim cannot be replayed is not reproducible.
            row["replay_hash"] = record["provenance"]["code_sha"]
    if status == "measured":
        row["measurement"] = {
            "val_acc": cell.get("val_acc"),
            "loss": cell.get("loss"),
        }
    return row


def _carried_reading(
    prior: dict[str, Any], p0_result: dict[str, Any] | None, key: str
) -> Any:
    """A reading the new run did not measure, as the earlier map published it.

    P1 and P3 keep the box an earlier screen calibrated; rewriting it empty is
    how two artifacts drift (TODO95 D2).
    """
    measured = (p0_result or {}).get(key)
    if measured is not None:
        return measured
    return (prior.get("inventory") or {}).get(key)


def _carried_base(
    prior: dict[str, Any], p0_result: dict[str, Any] | None
) -> dict[str, Any]:
    """The base box a slice that did not re-screen keeps from the earlier map."""
    measured = (p0_result or {}).get("base_box")
    return (prior.get("base") or {}) if measured is None else measured


def update_map(
    out_dir: Path,
    census_entries: list[PrimitiveCensusEntry],
    p0_result: dict | None,
    p1_result: dict | None = None,
    p3_result: dict | None = None,
    *,
    p4_result: dict | None = None,
    report: bool = True,
) -> None:
    """Write map.json v3: one row per censused primitive, never a missing row.

    The interaction layer and the deep dive are part of the same document: an
    axis-by-axis run keeps the layers an earlier run measured, and only P3/P4
    replace them (TODO95 S3/S4). ``report`` suppresses the printed census on
    an intermediate write, so a P3/P4 run reads the screen it just wrote, not
    the previous one.
    """
    map_path = out_dir / "map.json"
    cells = {cell["primitive"]: cell for cell in (p0_result or {}).get("cells", [])}

    # The map accumulates: an axis-by-axis run replaces its own rows and keeps
    # the rows an earlier v3 run measured. A v2 map is not merged — its rows
    # carry a different box and a different status taxonomy.
    prior: dict[str, Any] = {}
    previous: dict[str, dict] = {}
    interaction: dict[str, Any] | None = None
    deep_dive: dict[str, Any] | None = None
    if map_path.exists():
        prior = json.loads(map_path.read_text())
        if prior.get("version") == MAP_VERSION:
            previous = prior.get("primitives", {})
            interaction = prior.get("interaction")
            deep_dive = prior.get("deep_dive")

    primitives: dict[str, dict] = {}
    for entry in census_entries:
        cell = cells.get(entry.id)
        row = _map_row(entry, cell)
        if cell is None and entry.id in previous:
            row = previous[entry.id]
        primitives[entry.id] = row

    if p1_result:
        for cell in p1_result["cells"]:
            row = primitives.get(cell["primitive"])
            if row is not None:
                row["confirmation"] = {
                    "seeds": cell.get("seed_results"),
                    "mean_acc": cell.get("mean_acc"),
                    "std_acc": cell.get("delta"),
                }

    by_axis: dict[str, dict[str, int]] = {}
    for row in primitives.values():
        counts = by_axis.setdefault(row["axis"], {})
        counts[row["status"]] = counts.get(row["status"], 0) + 1

    interaction = (p3_result or {}).get("interaction") or interaction
    deep_dive = (p4_result or {}).get("deep_dive") or deep_dive

    map_data = {
        "version": MAP_VERSION,
        "updated": datetime.now().isoformat(),
        "inventory": {
            "total": len(census_entries),
            "available": sum(1 for entry in census_entries if entry.available),
            "control_val_acc": _carried_reading(prior, p0_result, "control_val_acc"),
            "control_spread": _carried_reading(prior, p0_result, "control_spread"),
            "bar": _carried_reading(prior, p0_result, "bar"),
        },
        "base": _carried_base(prior, p0_result),
        "by_axis": by_axis,
        "interaction": interaction,
        "deep_dive": deep_dive,
        "primitives": primitives,
    }
    map_path.write_text(json.dumps(map_data, indent=2, default=str))
    logger.info(f"Map updated: {map_path} ({len(primitives)} rows)")
    if report:
        _print_map_report(map_data)


def _print_deep_dive(deep: dict[str, Any]) -> None:
    """The deep dive layer: the candidate, the ladder, the pair and the stop."""
    candidate = deep["candidate"]
    print(f"Deep dive: {candidate['primitive']} — verdict={deep['verdict']}")
    print(
        f"  knob: {candidate['knob']} default={candidate['default']:g} "
        f"(margin over bar {candidate['margin']:.4f})"
    )
    for rung in deep["ladder"]:
        print(
            f"  rung {rung['factor']:g}× -> {rung['value']:g}: "
            f"{rung['status']} val_acc={rung['val_acc']}"
        )
    print(f"  knob binds: {deep['knob_binds']}; no power: {deep['no_power']}")
    effect = deep.get("effect")
    if effect:
        print(
            f"  effect: {effect['mean_diff']:.4f} "
            f"[{effect['ci_lower']:.4f}, {effect['ci_upper']:.4f}] at "
            f"{effect['n']} paired seeds, p={effect['p_value']:.4f}"
        )
    print(f"  stop: {deep['stop_reason']}")


def _print_map_report(map_data: dict[str, Any]) -> None:
    """The census's short report: counts per axis, and every defect's mechanism."""
    print("\n=== SEC map: census report ===")
    inventory = map_data["inventory"]
    print(
        f"Inventory: {inventory['total']} primitives, "
        f"{inventory['available']} available; "
        f"control val_acc={inventory['control_val_acc']}"
    )
    totals: dict[str, int] = {}
    for counts in map_data["by_axis"].values():
        for status, count in counts.items():
            totals[status] = totals.get(status, 0) + count
    print(
        "Screen: "
        + ", ".join(
            f"{status}={totals.get(status, 0)}"
            for status in (
                "measured",
                "defect",
                "refused",
                "unmeasured",
            )
        )
    )
    for axis, counts in sorted(map_data["by_axis"].items()):
        detail = ", ".join(
            f"{status}={count}" for status, count in sorted(counts.items())
        )
        print(f"  {axis:22} {detail}")
    defects = [
        row for row in map_data["primitives"].values() if row["status"] == "defect"
    ]
    for row in defects:
        print(f"  defect: {row['primitive']} — {row['defect']}")
    refused = [
        row for row in map_data["primitives"].values() if row["status"] == "refused"
    ]
    for row in refused:
        print(f"  refused: {row['primitive']} — {row['trigger']}")
    interaction = map_data.get("interaction")
    if interaction:
        pair = " × ".join(interaction["pair"])
        print(f"Interaction: {pair} — status={interaction['status']}")
        print(f"  levels: {interaction['levels']}")
        print(f"  control val_acc={interaction['control_val_acc']}")
        effect = interaction.get("effect")
        if effect is None:
            print(f"  effect: none ({interaction['stop_reason']})")
        elif effect["lower"] is None:
            print(
                f"  effect: {effect['effect']:.4f} (no interval, "
                f"{effect['seeds']} seed per cell)"
            )
        else:
            print(
                f"  effect: {effect['effect']:.4f} "
                f"[{effect['lower']:.4f}, {effect['upper']:.4f}] at "
                f"{effect['seeds']} seeds"
            )
    if map_data.get("deep_dive"):
        _print_deep_dive(map_data["deep_dive"])


# ============================================================
# Main Loop
# ============================================================


def _p4_after_screen(
    out_dir: Path,
    census_entries: list[PrimitiveCensusEntry],
    p0_result: dict | None,
    p1_result: dict | None,
    p3_result: dict | None,
    args: Any,
) -> dict[str, Any] | None:
    """Land the screen and the slice, then run the dive the map chooses."""
    update_map(out_dir, census_entries, p0_result, p1_result, p3_result, report=False)
    return run_p4_track(
        out_dir, device=args.device, registration_path=args.registration
    )


def main() -> None:
    import argparse

    # A census of 75 rows runs for minutes; without a handler its INFO
    # heartbeat is dropped and the only poll is the GPU meter.
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    parser = argparse.ArgumentParser(
        description="SEC Loop - result-first capability harvest"
    )
    parser.add_argument(
        "--track",
        choices=["R1", "R2", "P0", "P1", "P3", "P4", "all"],
        default="all",
        help="Track to run",
    )
    parser.add_argument(
        "--breadth",
        choices=["delta", "full"],
        default="delta",
        help="Breadth screen mode",
    )
    parser.add_argument("--max-cells", type=int, default=12, help="Max cells for R1/R2")
    parser.add_argument(
        "--max-primitives", type=int, default=6, help="Max primitives for P0"
    )
    parser.add_argument(
        "--axis",
        action="append",
        choices=["substrate", "geometry", "dynamics", "plasticity", "credit", "update"],
        help="Screen only this axis (repeatable); the map keeps earlier rows",
    )
    parser.add_argument(
        "--p1-from-map",
        action="store_true",
        help="Run P1 on measured, bound primitives from map.json (not just this P0 run)",
    )
    parser.add_argument(
        "--own-knobs",
        action="store_true",
        help="Run the viability box: each varied axis at its own defaults",
    )
    parser.add_argument("--out", type=Path, required=True, help="Output directory")
    parser.add_argument(
        "--device", type=str, default="auto", help="Device (auto, cpu, cuda)"
    )
    parser.add_argument(
        "--registration",
        type=Path,
        default=DEEP_DIVE_REGISTRATION,
        help="Committed pre-registration the P4 claim reads",
    )
    args = parser.parse_args()

    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load census
    census_entries = build_census()

    all_results: list[dict] = []
    r1_result = None
    r2_result = None
    p0_result = None
    p1_result = None
    p3_result = None
    p4_result = None

    # Run R1 if requested
    if args.track in {"R1", "all"}:
        r1_result = run_r1_track(out_dir, census_entries, device=args.device)
        all_results.extend(r1_result["cells"])

    # Run R2 if requested
    if args.track in {"R2", "all"}:
        r2_result = run_r2_track(out_dir, census_entries, device=args.device)
        all_results.extend(r2_result["cells"])

    # Run P0 if requested
    if args.track in {"P0", "all"}:
        entries_to_screen = [
            entry
            for entry in census_entries
            if not args.axis or entry.axis in args.axis
        ]
        p0_result = run_p0_track(
            out_dir,
            entries_to_screen,
            max_primitives=args.max_primitives,
            device=args.device,
            breadth=args.breadth,
            own_knobs=args.own_knobs,
        )
        all_results.extend(p0_result["cells"])

    # Determine measured primitives to confirm (3 seeds), where the axis binds
    p0_candidates: list[str] = []
    if args.p1_from_map:
        map_path = out_dir / "map.json"
        if map_path.exists():
            map_data = json.loads(map_path.read_text())
            p0_candidates = [
                k
                for k, v in map_data.get("primitives", {}).items()
                if v.get("status") == "measured" and v.get("binding") == "bound"
            ]
            logger.info(f"P1 from map: {len(p0_candidates)} measured, bound primitives")
    else:
        p0_candidates = [
            c["primitive"]
            for c in (p0_result["cells"] if p0_result else [])
            if c["status"] == "MEASURED" and c.get("binding") == "bound"
        ]

    # Run P1 if there are candidates
    if args.track in {"P1", "all"} and p0_candidates:
        p1_result = run_p1_track(
            out_dir, p0_candidates, census_entries, device=args.device
        )
        all_results.extend(p1_result["cells"])

    # The interaction slice reads the map the screen writes: land the screen
    # first, silently, then let P3 rank it.
    if args.track in {"P3", "all"}:
        update_map(out_dir, census_entries, p0_result, p1_result, report=False)
        p3_result = run_p3_track(out_dir, device=args.device)
        if p3_result:
            all_results.extend(p3_result["cells"])

    # The deep dive reads the same map: land the screen and the slice first,
    # silently, then let the map's candidate (not a second ranking) choose.
    if args.track in {"P4", "all"}:
        p4_result = _p4_after_screen(
            out_dir, census_entries, p0_result, p1_result, p3_result, args
        )
        if p4_result:
            all_results.extend(p4_result["cells"])

    # Update artifacts
    update_cell_log(out_dir, all_results)
    update_portfolio(
        out_dir,
        r1_result or {},
        r2_result or {},
        p0_result,
        p1_result,
        p3_result,
        p4_result,
    )
    update_map(
        out_dir,
        census_entries,
        p0_result,
        p1_result,
        p3_result,
        p4_result=p4_result,
    )

    # Print summary (raw metrics for human review)
    print("\n=== SEC Loop Summary ===")
    if r1_result:
        print(
            f"R1: gap_worst={r1_result['gap_worst']:.4f}, local_worst={r1_result['local_worst']:.4f}, backprop_worst={r1_result['backprop_worst']:.4f}, local_forgetting={r1_result['local_forgetting_mean']:.4f}, backprop_forgetting={r1_result['backprop_forgetting_mean']:.4f}, kill_triggered={r1_result['kill_rule_triggered']}, surprise={r1_result['surprise']}"
        )
    if r2_result:
        print(
            f"R2: gap_worst={r2_result['gap_worst']:.4f}, local_worst={r2_result['local_worst']:.4f}, backprop_worst={r2_result['backprop_worst']:.4f}, local_forgetting={r2_result['local_forgetting_mean']:.4f}, backprop_forgetting={r2_result['backprop_forgetting_mean']:.4f}, kill_triggered={r2_result['kill_rule_triggered']}, surprise={r2_result['surprise']}"
        )
    if p0_result:
        print(
            f"P0: measured={p0_result['measured']}, "
            f"defect={p0_result['defect']}, "
            f"refused={p0_result['unavailable']}, "
            f"box_defect={p0_result['box_defect']}, "
            f"pause_R={p0_result['pause_r']}"
        )

    if p1_result:
        print(
            f"P1: confirmed={p1_result['confirmed']}, surprises={p1_result['surprises']}"
        )

    if p3_result:
        layer = p3_result["interaction"]
        effect = layer["effect"]
        print(
            f"P3: pair={' × '.join(layer['pair'])}, status={layer['status']}, "
            f"effect={None if effect is None else round(effect['effect'], 4)}"
        )

    if p4_result:
        layer = p4_result["deep_dive"]
        effect = layer["effect"]
        print(
            f"P4: primitive={layer['candidate']['primitive']}, "
            f"knob={layer['candidate']['knob']}, "
            f"verdict={layer['verdict']}, "
            f"effect={None if effect is None else round(effect['mean_diff'], 4)}, "
            f"n={None if effect is None else effect['n']}"
        )

    # Surprise flags (recorded for review meeting)
    if r1_result and r1_result.get("surprise"):
        print("\n⚡ R1 SURPRISE FLAG: gap ≥ 5 pp — review for promotion")
    if r2_result and r2_result.get("surprise"):
        print("\n⚡ R2 SURPRISE FLAG: gap ≥ 5 pp — review for promotion")
    if p1_result and p1_result.get("surprises", 0) > 0:
        print(
            f"\n⚡ P1 SURPRISE FLAG: {p1_result['surprises']} primitive(s) confirmed — review"
        )


if __name__ == "__main__":
    main()
