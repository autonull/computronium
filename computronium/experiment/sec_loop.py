"""SEC Loop: Result-first capability harvest loop.

Runs:
- Track R (result-first): R1 (SplitMNIST batch-1 local vs backprop)
- Track P0 (breadth delta): screen unscreened/changed/failed primitives
- Track P1 (confirmation): 3 seeds, paired, only on P0 PASS

Run:
    uv run python -m computronium.experiment.sec_loop --track R1 --breadth delta --out results/sec
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import torch

from computronium.core.continual.metrics import CLConfig, CLMetrics
from computronium.core.continual.runner import run_continual_learning
from computronium.core.logging import get_logger
from computronium.experiment.kernel.evaluate import (
    CellEvaluation,
    EvaluationError,
    evaluate_cell,
)
from computronium.experiment.schema.coordinate import Coordinate, Schedule
from computronium.experiment.sec_census import PrimitiveCensusEntry, build_census

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

                result_entry = {
                    "track": "R1",
                    "credit": credit_name,
                    "seed": seed,
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


# ============================================================
# Track P0: Breadth Delta Screen
# ============================================================

P0_EPOCHS = 1
P0_BATCH_LIMIT = 32
P0_SEED = 0
P0_HIDDEN_DIM = 128
P0_PARAM_BUDGET = 10000


def get_legal_coordinate_for_primitive(
    entry: PrimitiveCensusEntry,
    task_id: str = "mnist",
) -> Coordinate | None:
    """Build a minimal legal coordinate for a primitive.

    Returns None if no legal box exists (mark as UNAVAILABLE).
    """
    # Default primitives for each axis
    defaults = {
        "substrate": "digital",
        "geometry": "feedforward",
        "dynamics": "instantaneous",
        "plasticity": "null",
        "credit": "gradient",
        "update": "euclidean",
    }

    # Override with the primitive under test
    axis_map = {
        "substrate": "substrate",
        "geometry": "geometry",
        "state_dynamics": "dynamics",
        "plasticity": "plasticity",
        "credit_assignment": "credit",
        "parameter_update": "update",
    }

    axis = axis_map.get(entry.axis, entry.axis)
    # Use the primitive key (from entry.id) not the display name
    # entry.id format: "primitive.substrate.digital" -> key is "digital"
    primitive_key = entry.id.split(".")[-1] if "." in entry.id else entry.id
    defaults[axis] = primitive_key

    # Check availability
    if not entry.available:
        return None

    # Check task family compatibility
    if (
        entry.task_families
        and "vision" not in entry.task_families
        and task_id in {"mnist", "cifar10", "split_mnist"}
    ):
        # Primitive not declared for vision tasks
        return None

    # Build coordinate with minimal params - only set structural params that are
    # universally required. Let the schema defaults handle geometry-specific params.
    params: dict[str, Any] = {
        "credit.lr": 0.01,
        "update.lr": 0.01,
    }

    # Add geometry-specific params based on the geometry being used
    geometry = defaults["geometry"]
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
        params["geometry.grid_hw"] = (16, 16)
    elif geometry == "spatial_lattice":
        params["geometry.lattice_dims"] = (8, 8)

    # Add dynamics-specific params
    dynamics = defaults["dynamics"]
    if dynamics == "energy_minimization":
        params["dynamics.max_steps"] = 10
        params["dynamics.convergence_threshold"] = 1e-3

    # Add credit-specific params for local credits
    credit = defaults["credit"]
    if credit in {
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

    coord = Coordinate(
        substrate=defaults["substrate"],
        geometry=defaults["geometry"],
        dynamics=defaults["dynamics"],
        plasticity=defaults["plasticity"],
        credit=defaults["credit"],
        update=defaults["update"],
        params=params,
    )
    return coord


def run_p0_track(
    out_dir: Path,
    census_entries: list[PrimitiveCensusEntry],
    max_primitives: int = 6,
    device: str = "auto",
) -> dict[str, Any]:
    """Run Track P0: Delta breadth screen for unscreened/changed/failed primitives.

    Only screens primitives with screen_status in {unscreened, defect, failed}.
    Reads screening status from map.json (last_screened) and census (available).
    """
    logger.info("Starting Track P0: Delta breadth screen")

    # Load map to check which primitives have been screened
    map_path = out_dir / "map.json"
    screened_primitives = set()
    if map_path.exists():
        map_data = json.loads(map_path.read_text())
        for prim_id, entry in map_data.get("primitives", {}).items():
            if entry.get("last_screened") and entry.get("status") in {
                "pass",
                "defect",
                "unavailable",
                "coordinate",
            }:
                screened_primitives.add(prim_id)

    # Filter to delta: unscreened, defect, or failed (from map status)
    delta_entries = [
        e
        for e in census_entries
        if e.id not in screened_primitives or e.screen_status in {"defect", "failed"}
    ]

    # Limit to max_primitives
    delta_entries = delta_entries[:max_primitives]

    logger.info(
        f"P0 delta: {len(delta_entries)} primitives to screen (from {len(census_entries)} total)"
    )

    results: list[dict[str, Any]] = []
    pass_count = 0
    defect_count = 0
    unavailable_count = 0
    coordinate_count = 0

    schedule = Schedule(
        fidelity="L0",
        seed=P0_SEED,
        n_seeds=1,
        epochs=P0_EPOCHS,
        batch_limit=P0_BATCH_LIMIT,
        budget_id="p0",
        task_id="mnist",
        param_budget=P0_PARAM_BUDGET,
        device=device,
        deterministic=True,
        num_workers=0,
        precision="fp32",
        checkpoint_every_n=0,
    )

    for entry in delta_entries:
        logger.info(f"P0 screening: {entry.id}")

        coord = get_legal_coordinate_for_primitive(entry)
        if coord is None:
            result = {
                "track": "P0",
                "primitive": entry.id,
                "status": "UNAVAILABLE",
                "reason": "no legal box or not available",
            }
            results.append(result)
            unavailable_count += 1
            continue

        try:
            eval_result: CellEvaluation = evaluate_cell(coord, schedule)
            metrics = dict(eval_result.metrics)
            val_acc = metrics.get("val_acc", 0.0)
            loss = metrics.get("loss", float("inf"))

            # Gate: PASS = above chance + 2σ, no crash, finite loss
            chance = 0.1  # MNIST 10-class chance
            if (
                val_acc > chance + 0.02
                and loss < float("inf")
                and not torch.isnan(torch.tensor(loss))
            ):
                status = "PASS"
                pass_count += 1
            else:
                status = "COORDINATE"
                coordinate_count += 1

            result = {
                "track": "P0",
                "primitive": entry.id,
                "status": status,
                "val_acc": val_acc,
                "loss": loss,
                "metrics": metrics,
                "walltime_s": eval_result.walltime_s,
            }
            results.append(result)

        except EvaluationError as e:
            logger.exception(f"P0 cell failed: {entry.id}")
            result = {
                "track": "P0",
                "primitive": entry.id,
                "status": "DEFECT",
                "error": str(e),
                "cause": e.cause,
            }
            results.append(result)
            defect_count += 1
        except ValueError as e:
            # Validation errors (incompatible primitive combinations)
            logger.warning(f"P0 validation failed: {entry.id}, error={e}")
            result = {
                "track": "P0",
                "primitive": entry.id,
                "status": "UNAVAILABLE",
                "reason": f"validation: {e}",
            }
            results.append(result)
            unavailable_count += 1
        except Exception as e:
            # Other unexpected errors
            logger.exception(f"P0 cell failed: {entry.id}")
            result = {
                "track": "P0",
                "primitive": entry.id,
                "status": "DEFECT",
                "error": str(e),
            }
            results.append(result)
            defect_count += 1

    total = len(delta_entries)
    defect_rate = defect_count / total if total > 0 else 0.0
    pause_r = defect_rate > 0.2

    result_summary = {
        "track": "P0",
        "screened": total,
        "pass": pass_count,
        "defect": defect_count,
        "unavailable": unavailable_count,
        "coordinate": coordinate_count,
        "defect_rate": defect_rate,
        "pause_r": pause_r,
        "cells": results,
    }

    logger.info(
        f"P0 complete: screened={total}, pass={pass_count}, defect={defect_count}, unavailable={unavailable_count}, coordinate={coordinate_count}, pause_R={pause_r}"
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
                    "pass": p0_result["pass"],
                    "defect": p0_result["defect"],
                    "unavailable": p0_result["unavailable"],
                    "coordinate": p0_result["coordinate"],
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
    """Append results to cells.jsonl."""
    cell_log_path = out_dir / "cells.jsonl"
    with cell_log_path.open("a") as f:
        for result in all_results:
            f.write(json.dumps(result, default=str) + "\n")
    logger.info(f"Cell log updated: {cell_log_path} (+{len(all_results)} entries)")


def update_map(
    out_dir: Path,
    census_entries: list[PrimitiveCensusEntry],
    p0_result: dict | None,
    p1_result: dict | None = None,
) -> None:
    """Update map.json with P0 screening and P1 confirmation results."""
    map_path = out_dir / "map.json"

    if map_path.exists():
        map_data = json.loads(map_path.read_text())
    else:
        map_data = {"primitives": {}}

    if p0_result:
        for cell in p0_result["cells"]:
            prim_id = cell["primitive"]
            if prim_id not in map_data["primitives"]:
                entry = next((e for e in census_entries if e.id == prim_id), None)
                map_data["primitives"][prim_id] = {
                    "primitive": prim_id,
                    "status": "unknown",
                    "family": entry.axis if entry else "unknown",
                    "box": {},
                    "ruler": "val_acc on mnist",
                    "best_coordinate": None,
                    "defect": None,
                    "capability": entry.capability_card if entry else "",
                    "last_screened": datetime.now().isoformat(),
                }

            map_entry = map_data["primitives"][prim_id]
            map_entry["status"] = cell["status"].lower()
            map_entry["last_screened"] = datetime.now().isoformat()
            if cell["status"] == "PASS":
                map_entry["best_coordinate"] = {"val_acc": cell.get("val_acc", 0.0)}
            elif cell["status"] == "DEFECT":
                map_entry["defect"] = cell.get("error", "unknown")

    if p1_result:
        for cell in p1_result["cells"]:
            prim_id = cell["primitive"]
            if prim_id in map_data["primitives"]:
                map_entry = map_data["primitives"][prim_id]
                map_entry["p1_confirmed"] = True
                map_entry["p1_surprise"] = cell.get("surprise", False)
                map_entry["p1_mean_acc"] = cell.get("mean_acc", 0.0)
                map_entry["p1_effect"] = cell.get("effect", 0.0)
                map_entry["p1_delta"] = cell.get("delta", 0.0)
                map_entry["p1_seeds"] = cell.get("seed_results", [])
                # Update best_coordinate with P1 mean if it's a surprise
                if cell.get("surprise", False):
                    map_entry["best_coordinate"] = {
                        "val_acc": cell.get("mean_acc", 0.0),
                        "p1_confirmed": True,
                    }

    map_path.write_text(json.dumps(map_data, indent=2, default=str))
    logger.info(f"Map updated: {map_path}")


# ============================================================
# Main Loop
# ============================================================


def main() -> None:
    import argparse

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
    parser.add_argument("--out", type=Path, required=True, help="Output directory")
    parser.add_argument(
        "--device", type=str, default="auto", help="Device (auto, cpu, cuda)"
    )
    parser.add_argument(
        "--p1-from-map",
        action="store_true",
        help="Run P1 on PASS primitives from map.json (not just current P0 run)",
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
    if args.track in {"P0", "all"} and args.breadth == "delta":
        p0_result = run_p0_track(
            out_dir,
            census_entries,
            max_primitives=args.max_primitives,
            device=args.device,
        )
        all_results.extend(p0_result["cells"])

    # Determine P0 passes for P1
    p0_passes: list[str] = []
    if args.p1_from_map:
        # Read PASS primitives from map.json
        map_path = out_dir / "map.json"
        if map_path.exists():
            map_data = json.loads(map_path.read_text())
            p0_passes = [
                k
                for k, v in map_data.get("primitives", {}).items()
                if v.get("status") == "pass"
            ]
            logger.info(f"P1 from map: {len(p0_passes)} PASS primitives")
    else:
        # Use passes from current P0 run
        p0_passes = [
            c["primitive"]
            for c in (p0_result["cells"] if p0_result else [])
            if c["status"] == "PASS"
        ]

    # Run P1 if there are passes
    if args.track in {"P1", "all"} and p0_passes:
        p1_result = run_p1_track(out_dir, p0_passes, census_entries, device=args.device)
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
            f"P0: pass={p0_result['pass']}, defect={p0_result['defect']}, unavailable={p0_result['unavailable']}, coordinate={p0_result['coordinate']}, pause_R={p0_result['pause_r']}"
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
