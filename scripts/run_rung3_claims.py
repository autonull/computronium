#!/usr/bin/env python
"""Run Rung 3 (paired comparison) claims on specific primitives.

This script runs the deep dive (ladder + paired comparison) on a list of
primitives for a given task, without requiring the full SEC pipeline.
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any

from computronium.experiment.schema.coordinate import Schedule
from computronium.experiment.sec_deep_dive import (
    CLAIM_SEEDS,
    LADDER_FACTORS,
    DeepDiveCandidate,
    LadderRung,
    best_rung,
    ladder_points,
    load_registration,
    primary_knob,
)
from computronium.experiment.sec_loop import (
    _box_summary,
    _coordinate,
    _deep_dive_coordinate,
    _is_legal,
    _measure,
    _pair_verdict,
    _paired_cells_async,
    _task_bar,
    base_schedule,
)
from computronium.experiment.sec_pilot import BASE_BOXES, base_family
from computronium.validation.preregistration import (
    EffectSizeRegistration,
)

# Primitives to test for each task (8 each as per TODO103)
MNIST_PRIMITIVES = [
    # Geometry
    "primitive.geometry.feedforward",
    "primitive.geometry.nca",
    "primitive.geometry.attention",
    "primitive.geometry.routing",
    "primitive.geometry.spatial_lattice",
    "primitive.geometry.tile_mesh",
    # Credit
    "primitive.credit_assignment.gradient",
    "primitive.credit_assignment.pepita",
]

# Also include other credit primitives for MNIST
MNIST_CREDIT_PRIMITIVES = [
    "primitive.credit_assignment.random_projections",
    "primitive.credit_assignment.thermodynamic_contrast",
    "primitive.credit_assignment.forward_tangent",
    "primitive.credit_assignment.local_goodness",
    "primitive.credit_assignment.local_supervision",
    "primitive.credit_assignment.pc_alm",
    "primitive.credit_assignment.score_function",
    "primitive.credit_assignment.target_inversion",
]

# Update primitives for MNIST
MNIST_UPDATE_PRIMITIVES = [
    "primitive.parameter_update.adam",
    "primitive.parameter_update.euclidean",
    "primitive.parameter_update.lion",
    "primitive.parameter_update.muon",
    "primitive.parameter_update.ortho_adam",
    "primitive.parameter_update.riemannian_orthogonal",
    "primitive.parameter_update.adafactor",
    "primitive.parameter_update.local_adam",
]

# Dynamics primitives for MNIST
MNIST_DYNAMICS_PRIMITIVES = [
    "primitive.state_dynamics.instantaneous",
    "primitive.state_dynamics.energy_minimization",
    "primitive.state_dynamics.predictive_settling",
    "primitive.state_dynamics.pc_alm",
    "primitive.state_dynamics.error_predictive_coding",
    "primitive.state_dynamics.spike_integration",
    "primitive.state_dynamics.diffusion",
    "primitive.state_dynamics.lazy",
]

IRIS_PRIMITIVES = [
    # Update (these showed best on iris)
    "primitive.parameter_update.adafactor",
    "primitive.parameter_update.lion",
    "primitive.parameter_update.adam",
    "primitive.parameter_update.muon",
    "primitive.parameter_update.local_adam",
    "primitive.parameter_update.ortho_adam",
    "primitive.parameter_update.riemannian_orthogonal",
    "primitive.parameter_update.euclidean",
]


async def run_deep_dive_on_primitive(
    primitive_id: str,
    task_id: str,
    device: str = "cuda",
    registration_path: Path | None = None,
) -> dict[str, Any]:
    """Run the deep dive (Rung 2 ladder + Rung 3 paired) on a single primitive."""

    # Get the base family for this task
    family = base_family(task_id)
    if family is None:
        raise ValueError(f"No base family for task {task_id}")

    base = BASE_BOXES.get(family)
    if base is None:
        raise ValueError(f"No base box for family {family}")

    # Parse primitive axis and name
    parts = primitive_id.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid primitive ID: {primitive_id}")
    axis = parts[1]
    level = parts[2]
    # Map axis names to structural axis names
    axis_map = {
        "credit_assignment": "credit",
        "state_dynamics": "dynamics",
        "parameter_update": "update",
    }
    axis = axis_map.get(axis, axis)

    # Get the primary knob for this primitive
    axis_enum = axis  # axis segment
    knob_info = primary_knob(axis_enum, level, task_id=task_id)
    if knob_info is None:
        return {
            "primitive": primitive_id,
            "task": task_id,
            "status": "no_knob",
            "reason": f"No primary knob found for {primitive_id} on {task_id}",
        }

    knob_key, knob_default = knob_info

    # Use the family's base coordinate (from BASE_BOXES)
    base_axes = base.base_coordinate.copy() if base.base_coordinate else {}
    # Ensure all required axes are present
    default_axes = {
        "substrate": "digital",
        "geometry": "feedforward",
        "dynamics": "instantaneous",
        "plasticity": "null",
        "credit": "gradient",
        "update": "euclidean",
    }
    # Merge: family's base coordinate overrides defaults
    for k, v in default_axes.items():
        if k not in base_axes:
            base_axes[k] = v
    # Override the axis under test
    base_axes[axis] = level

    # Get the base schedule
    schedule = base_schedule(task_id, device)
    if schedule is None:
        raise ValueError(f"No schedule for task {task_id}")

    # Build the coordinate with the family's base axes
    base_coord = _coordinate(base_axes)

    # Get the box summary for the base coordinate
    base_box = _box_summary(base_coord, schedule)

    # Check if legal
    legal, refusal = _is_legal(base_coord, task_id)
    if not legal:
        return {
            "primitive": primitive_id,
            "task": task_id,
            "status": "refused",
            "reason": refusal,
        }

    # Build the candidate
    candidate = DeepDiveCandidate(
        primitive=primitive_id,
        axis=axis,
        level=level,
        val_acc=0.0,  # Will be filled after ladder
        margin=0.0,
        knob=knob_key,
        default=knob_default,
        box=base_box,
        walltime_s=None,
    )

    # Get the task bar
    bar = _task_bar(task_id)
    bar_value = bar.value if bar else None

    # Run the ladder (Rung 2)
    print(f"\n{'=' * 60}")
    print(f"Running ladder for {primitive_id} on {task_id}")
    print(f"Knob: {knob_key} = {knob_default}")
    print(f"Ladder factors: {LADDER_FACTORS}")
    print(f"{'=' * 60}")

    rungs = await _ladder_async(candidate, schedule)

    best = best_rung(tuple(rungs))

    print("\nLadder results:")
    for rung in rungs:
        status_str = (
            f"val_acc={rung.val_acc:.4f}" if rung.val_acc is not None else rung.status
        )
        print(f"  factor={rung.factor}, value={rung.value:.4f}, {status_str}")

    if best is None:
        return {
            "primitive": primitive_id,
            "task": task_id,
            "status": "no_ladder_point",
            "reason": "No valid ladder point",
            "rungs": [r.to_dict() for r in rungs],
        }

    print(
        f"\nBest rung: factor={best.factor}, value={best.value:.4f}, val_acc={best.val_acc:.4f}"
    )

    # Check if best rung clears the bar
    if bar_value is not None and (best.val_acc or 0.0) <= bar_value:
        return {
            "primitive": primitive_id,
            "task": task_id,
            "status": "below_bar",
            "reason": f"Best rung val_acc={best.val_acc:.4f} <= bar={bar_value:.4f}",
            "rungs": [r.to_dict() for r in rungs],
            "best_rung": best.to_dict(),
        }

    # Load or create registration
    if registration_path and registration_path.exists():
        registration = load_registration(registration_path)
    else:
        # Create a default effect size registration
        registration = EffectSizeRegistration.for_task_family(
            claim=f"{primitive_id} improves {task_id} with knob {knob_key}",
            metric="val_acc",
            task_id=task_id,
            alpha=0.05,
            min_seeds=CLAIM_SEEDS,
            created=time.strftime("%Y-%m-%d"),
            box=base_box,
        )

    # Run paired comparison (Rung 3)
    print(f"\nRunning paired comparison (n={CLAIM_SEEDS} seeds per arm)...")
    cells = await _paired_cells_async(candidate, schedule, best.factor)

    print("\nPaired results:")
    for cell in cells:
        print(
            f"  {cell.arm}: seed={cell.seed}, val_acc={cell.val_acc:.4f}, status={cell.status}"
        )

    # Compute verdict
    result = _pair_verdict(
        candidate, rungs, best, cells, registration, schedule, time.monotonic()
    )

    return result


async def _ladder_async(
    candidate: DeepDiveCandidate,
    schedule: Schedule,
    semaphore: asyncio.Semaphore | None = None,
) -> list[LadderRung]:
    """Run the 3-point ladder asynchronously."""
    from dataclasses import replace

    from computronium.experiment.sec_deep_dive import LadderRung

    if semaphore is None:
        semaphore = asyncio.Semaphore(2)

    async def _measure_async(coord: Any, run: Schedule) -> dict[str, Any]:
        return await asyncio.to_thread(_measure, coord, run)

    async def _run_one(factor: float, value: float) -> LadderRung:
        async with semaphore:
            measured = await _measure_async(
                _deep_dive_coordinate(candidate, factor, schedule.task_id),
                replace(schedule, seed=0, n_seeds=1),
            )
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

    tasks = [_run_one(factor, value) for factor, value in ladder_points(candidate)]
    results = await asyncio.gather(*tasks)
    return list(results)


async def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Run Rung 3 claims on specific primitives"
    )
    parser.add_argument(
        "--task",
        required=True,
        help="Task to run on (e.g., mnist, iris, spiking_mnist, optical_mnist, memristor_simulation)",
    )
    parser.add_argument("--device", default="cuda", help="Device to use")
    parser.add_argument("--out", type=Path, required=True, help="Output directory")
    parser.add_argument("--registration", type=Path, help="Pre-registration file")
    parser.add_argument(
        "--primitives",
        nargs="+",
        help="Specific primitives to test (overrides defaults)",
    )
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)

    if args.primitives:
        primitives = args.primitives
    elif args.task == "mnist":
        primitives = MNIST_PRIMITIVES
    elif args.task == "iris":
        primitives = IRIS_PRIMITIVES
    else:
        # For other tasks, use the primitives passed via --primitives
        primitives = []

    print(f"Running Rung 3 claims on {len(primitives)} primitives for {args.task}")
    print(f"Primitives: {primitives}")

    results = []
    for primitive_id in primitives:
        try:
            result = await run_deep_dive_on_primitive(
                primitive_id,
                args.task,
                device=args.device,
                registration_path=args.registration,
            )
            results.append(result)

            # Save individual result
            result_file = (
                args.out / f"{primitive_id.replace('.', '_')}_{args.task}_rung3.json"
            )
            result_file.write_text(json.dumps(result, indent=2, default=str))
            print(f"Saved result to {result_file}")

        except Exception as e:
            print(f"Error running {primitive_id}: {e}")
            results.append({
                "primitive": primitive_id,
                "task": args.task,
                "status": "error",
                "reason": str(e),
            })

    # Save summary (append to existing)
    summary_file = args.out / f"rung3_summary_{args.task}.json"
    existing_results = []
    if summary_file.exists():
        try:
            existing_results = json.loads(summary_file.read_text())
        except Exception:
            pass
    all_results = existing_results + results
    summary_file.write_text(json.dumps(all_results, indent=2, default=str))
    print(f"\nSummary saved to {summary_file}")

    # Print summary
    print("\n=== Summary ===")
    for r in results:
        # The result structure has track and deep_dive
        if "deep_dive" in r:
            status = r["deep_dive"].get(
                "verdict", r["deep_dive"].get("status", "unknown")
            )
        else:
            status = r.get("verdict", r.get("status", "unknown"))
        primitive = (
            r
            .get("deep_dive", {})
            .get("candidate", {})
            .get("primitive", r.get("primitive", "unknown"))
        )
        print(f"  {primitive}: {status}")


if __name__ == "__main__":
    asyncio.run(main())
