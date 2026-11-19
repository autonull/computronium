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
from datetime import datetime
from pathlib import Path
from typing import Any

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

P0_EPOCHS = 1
# 32 samples per step. The loader used to read the batch *count* as the batch
# size, so the declared 375-batch screen trained at 375 samples/step (a 118,282
# parameter cell never saw its step size move); the two are separate fields of
# the box (TODO95 D2).
P0_BATCH_SIZE = 32
# 32 batches (1,024 samples) ranked cells by their default step size, not by
# their mechanism: at 32 batches `adam` scored 0.198 and `euclidean` 0.540; at
# 375 batches `adam` scored 0.695 and `euclidean` 0.424 (measured 2026-11-18).
# A screen must run long enough for the slowest declared step size to move.
P0_BATCH_LIMIT = 375
P0_SEED = 0
P0_HIDDEN_DIM = 128
# A 128-wide hidden layer composes 118,282 parameters; a 10k ceiling with a
# 128-wide layer was an impossible box (measured 2026-11-18), and the screen
# never checked it. The ceiling now fits the declared geometry.
P0_PARAM_BUDGET = 150_000
# How many compose-legal boxes to try per primitive before declaring it cannot
# train. Most resolve on the first (base) box; a few need a companion swap.
P0_MAX_COORDINATES = 24
# A swap chain is not a fair search: one slow primitive can spend the axis's
# whole watchdog on 24 training attempts. The cap is a refusal (a box
# statement), not a verdict, and it is 8× the measured 375-batch cell.
P0_PRIMITIVE_BUDGET_S = 60.0
# The base box shares one step size and one geometry width across primitives.
# A primitive's own declared defaults are the `own-knobs` pass (TODO95 P2);
# until that pass runs, an update row is `inert` (an update needs its own step).
P0_OWN_KNOBS = False


def _box_summary(coord: Coordinate, schedule: Schedule | None = None) -> dict[str, Any]:
    """The box a cell was screened in: the six axes plus the whole schedule.

    A row without its task, batch and step count cannot be reproduced and cannot
    be compared with another row (TODO95 D2/D3). The schedule is the box, so its
    own serialization is the one source; the six axes are added to it.
    """
    box: dict[str, Any] = {"substrate": coord.substrate}
    for field in _AXIS_FIELD.values():
        box[field] = getattr(coord, field)
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


def _control_val_acc(schedule: Schedule, device: str) -> float | None:
    """The base coordinate's own accuracy at this box: the ability ruler.

    The gate bar is the task's chance rate, so a cell above it has cleared a
    floor, not a capability. A map row is only readable beside this control:
    the same box, the default six-axis coordinate, one seed.
    """
    try:
        result = evaluate_cell(_coordinate(_AXIS_DEFAULTS), schedule)
    except Exception:  # ruff: ignore[blind-except] - a broken control must not end the screen
        logger.exception("P0 control cell failed at the box")
        return None
    return float(dict(result.metrics).get("val_acc", 0.0))


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


_AXIS_FIELD = {
    "substrate": "substrate",
    "geometry": "geometry",
    "state_dynamics": "dynamics",
    "plasticity": "plasticity",
    "credit_assignment": "credit",
    "parameter_update": "update",
}

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


def _params_for(axes: dict[str, str]) -> dict[str, Any]:
    """Structural hyperparameters a coordinate needs for the given axes."""
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
    elif geometry == "graph":
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
    return params


def _coordinate(axes: dict[str, str]) -> Coordinate:
    return Coordinate(
        substrate=axes["substrate"],
        geometry=axes["geometry"],
        dynamics=axes["dynamics"],
        plasticity=axes["plasticity"],
        credit=axes["credit"],
        update=axes["update"],
        params=_params_for(axes),
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
    except Exception as exc:  # noqa: BLE001 - report, never crash the screen
        return False, f"{type(exc).__name__}: {exc}"


def _iter_legal_coordinates(
    entry: PrimitiveCensusEntry,
    limit: int = 64,
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
    axis = _AXIS_FIELD.get(entry.axis, entry.axis)
    base = dict(_AXIS_DEFAULTS)
    base[axis] = primitive_key

    def emit(axes: dict[str, str]) -> Coordinate | None:
        coord = _coordinate(axes)
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
        except (ValueError, RuntimeError) as exc:
            # ruff: ignore[blind-except] - one bad cell never ends the screen
            last_error = exc
    return None, None, last_error, tried, False


def _unmeasured_cell(
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
        }
    logger.exception(f"P0 every legal box failed to train: {entry.id}")
    inert = binding_reason(
        axis, primitive_key, criterion=criterion, own_knobs=P0_OWN_KNOBS
    )
    return {
        "track": "P0",
        "primitive": entry.id,
        "status": "DEFECT",
        "error": str(last_error),
        "cause": getattr(last_error, "cause", None),
        "ruler": ruler,
        "binding": "inert" if inert else "bound",
        "binding_reason": inert,
        "tried": tried,
    }


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
) -> dict[str, Any]:
    """Screen one primitive over its nearest compose-legal boxes.

    Emits one cell: the number, the box and the cost beside a MEASURED status;
    a DEFECT only for an execution fact (a crash, a non-finite metric, a
    ceiling violation). A bar is a gate's floor; a screen never mints a verdict
    (TODO95 D5), so no cell carries one.
    """
    box_binding = binding_reason(
        axis, primitive_key, criterion=criterion, own_knobs=P0_OWN_KNOBS
    )
    if not candidates:
        return {
            "track": "P0",
            "primitive": entry.id,
            "status": "UNAVAILABLE",
            "reason": "no legal box or not available",
            "ruler": ruler,
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
        )

    metrics = dict(eval_result.metrics)
    val_acc = float(metrics.get("val_acc", 0.0))
    loss = float(metrics.get("loss", float("inf")))
    finite = math.isfinite(val_acc) and math.isfinite(loss)
    within = eval_result.param_count <= P0_PARAM_BUDGET * (1 + PARAM_BUDGET_TOLERANCE)
    defect = (
        None
        if finite and within
        else (
            "non-finite metric"
            if not finite
            else f"param_count {eval_result.param_count} over ceiling"
        )
    )
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
        "record": record.to_dict(),
    }


def run_p0_track(
    out_dir: Path,
    census_entries: list[PrimitiveCensusEntry],
    max_primitives: int = 6,
    device: str = "auto",
    breadth: str = "delta",
) -> dict[str, Any]:
    """Run Track P0: Breadth screen for primitives.

    Delta mode: only unscreened, defect, or failed primitives.
    Full mode: all primitives (re-screen everything).
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

    schedule = Schedule(
        fidelity="L0",
        seed=P0_SEED,
        n_seeds=1,
        epochs=P0_EPOCHS,
        batch_limit=P0_BATCH_LIMIT,
        batch_size=P0_BATCH_SIZE,
        budget_id="p0",
        task_id="mnist",
        param_budget=P0_PARAM_BUDGET,
        device=device,
        deterministic=True,
        num_workers=0,
        precision="fp32",
        checkpoint_every_n=0,
    )

    control_acc = _control_val_acc(schedule, device)
    criterion, ruler = _ruler(schedule.task_id)
    logger.info(f"P0 control at this box: val_acc={control_acc}")

    results: list[dict[str, Any]] = []
    for entry in entries_to_screen:
        logger.info(f"P0 screening: {entry.id}")
        axis = _AXIS_FIELD.get(entry.axis, entry.axis)
        results.append(
            _screen_coordinate(
                entry,
                _iter_legal_coordinates(entry, limit=P0_MAX_COORDINATES),
                schedule,
                control_acc=control_acc,
                ruler=ruler,
                criterion=criterion,
                axis=axis,
                primitive_key=entry.id.split(".")[-1],
            )
        )

    total = len(entries_to_screen)
    measured_count = sum(1 for cell in results if cell["status"] == "MEASURED")
    defect_count = sum(1 for cell in results if cell["status"] == "DEFECT")
    unavailable_count = sum(1 for cell in results if cell["status"] == "UNAVAILABLE")
    box_defect_count = sum(1 for cell in results if cell.get("within_ceiling") is False)
    defect_rate = defect_count / total if total > 0 else 0.0
    pause_r = defect_rate > 0.2

    result_summary = {
        "track": "P0",
        "screened": total,
        "measured": measured_count,
        "defect": defect_count,
        "unavailable": unavailable_count,
        "box_defect": box_defect_count,
        "control_val_acc": control_acc,
        "ruler": ruler,
        "base_box": _box_summary(_coordinate(_AXIS_DEFAULTS), schedule),
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
                param_budget=P0_PARAM_BUDGET,
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
# Portfolio & Map Updates
# ============================================================


def update_portfolio(
    out_dir: Path,
    r1_result: dict | None,
    r2_result: dict | None,
    p0_result: dict | None,
    p1_result: dict | None,
) -> None:
    """Update portfolio.json with track results."""
    portfolio_path = out_dir / "portfolio.json"

    if portfolio_path.exists():
        portfolio = json.loads(portfolio_path.read_text())
    else:
        portfolio = {"tracks": [], "active_track": "R1", "session_count": 0}

    portfolio["session_count"] += 1
    portfolio["last_session"] = datetime.now().isoformat()

    # Update R1 track
    if r1_result:
        for track in portfolio["tracks"]:
            if track["track"] == "R1":
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
                track["budget_used"]["seeds"] = len({
                    c["seed"] for c in r1_result["cells"]
                })
                track["contention"] = False
                break

    # Update R2 track
    if r2_result:
        for track in portfolio["tracks"]:
            if track["track"] == "R2":
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
                track["budget_used"]["seeds"] = len({
                    c["seed"] for c in r2_result["cells"]
                })
                track["contention"] = False
                break

    if p0_result:
        for track in portfolio["tracks"]:
            if track["track"] == "P0":
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
                break

    if p1_result:
        for track in portfolio["tracks"]:
            if track["track"] == "P1":
                track["last_result"] = {
                    "confirmed": p1_result["confirmed"],
                    "surprises": p1_result["surprises"],
                }
                track["budget_used"]["cells"] = p1_result["confirmed"] * P1_SEEDS
                track["budget_used"]["seeds"] = P1_SEEDS
                break

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
        row["rule"] = (
            "nearest-legal swap" if row["swapped"] else "base box, one axis varied"
        )
        row["ruler"] = cell.get("ruler")
        row["control"] = {"val_acc": cell.get("control_val_acc")}
        row["resource"] = {
            "walltime_s": cell.get("walltime_s"),
            "param_count": cell.get("param_count"),
            "within_ceiling": cell.get("within_ceiling"),
        }
    if status == "measured":
        row["measurement"] = {
            "val_acc": cell.get("val_acc"),
            "loss": cell.get("loss"),
        }
    return row


def update_map(
    out_dir: Path,
    census_entries: list[PrimitiveCensusEntry],
    p0_result: dict | None,
    p1_result: dict | None = None,
) -> None:
    """Write map.json v3: one row per censused primitive, never a missing row."""
    map_path = out_dir / "map.json"
    cells = {cell["primitive"]: cell for cell in (p0_result or {}).get("cells", [])}

    # The map accumulates: an axis-by-axis run replaces its own rows and keeps
    # the rows an earlier v3 run measured. A v2 map is not merged — its rows
    # carry a different box and a different status taxonomy.
    previous: dict[str, dict] = {}
    if map_path.exists():
        prior = json.loads(map_path.read_text())
        if prior.get("version") == MAP_VERSION:
            previous = prior.get("primitives", {})

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

    control = (p0_result or {}).get("control_val_acc")
    base = (p0_result or {}).get("base_box", {})
    map_data = {
        "version": MAP_VERSION,
        "updated": datetime.now().isoformat(),
        "inventory": {
            "total": len(census_entries),
            "available": sum(1 for entry in census_entries if entry.available),
            "control_val_acc": control,
        },
        "base": base,
        "by_axis": by_axis,
        "primitives": primitives,
    }
    map_path.write_text(json.dumps(map_data, indent=2, default=str))
    logger.info(f"Map updated: {map_path} ({len(primitives)} rows)")
    _print_map_report(map_data)


def _print_map_report(map_data: dict[str, Any]) -> None:
    """The census's short report: counts per axis, and every defect's mechanism."""
    print("\n=== SEC map: census report ===")
    inventory = map_data["inventory"]
    print(
        f"Inventory: {inventory['total']} primitives, "
        f"{inventory['available']} available; "
        f"control val_acc={inventory['control_val_acc']}"
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


# ============================================================
# Main Loop
# ============================================================


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
        choices=["R1", "R2", "P0", "P1", "all"],
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
    parser.add_argument("--out", type=Path, required=True, help="Output directory")
    parser.add_argument(
        "--device", type=str, default="auto", help="Device (auto, cpu, cuda)"
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

    # Update artifacts
    update_cell_log(out_dir, all_results)
    update_portfolio(out_dir, r1_result or {}, r2_result or {}, p0_result, p1_result)
    update_map(out_dir, census_entries, p0_result, p1_result)

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
