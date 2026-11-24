#!/usr/bin/env python
"""
Full SEC competitive run with learned void rules and meta-SEC params.

This script runs the complete SEC competitive evaluation across all 6 axes
using the optimized meta-SEC parameters and learned void rules.

Usage:
    uv run python scripts/run_full_sec_competitive.py

Note: This is a long-running GPU job. Recommended to run in background:
    nohup uv run python scripts/run_full_sec_competitive.py > logs/full_sec_$(date +%Y%m%d_%H%M%S).log 2>&1 &
"""

from __future__ import annotations

import asyncio
import json
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, '/home/me/computronium')

# Apply learned void rules BEFORE importing other modules that use DEFECT_REGISTRY
from computronium.experiment.legality.void_rules_learned import apply_learned_rules
apply_learned_rules()
print("✅ Applied learned void rules")

# Load meta-SEC best params
with open('/home/me/computronium/configs/meta_sec_best.json', 'r') as f:
    meta = json.load(f)

best_params = meta.get('best_params', {})

# Extract params
N_LADDER_POINTS = best_params.get('n_ladder_points', 4)
LADDER_LOG_MIN = best_params.get('ladder_log_min', -1.1)
LADDER_LOG_MAX = best_params.get('ladder_log_max', 1.5)
CLAIM_SEEDS = best_params.get('claim_seeds', 3)
MIN_EFFECT_SIZE_BY_FAMILY = {
    k.replace('min_d_', ''): v
    for k, v in best_params.items()
    if k.startswith('min_d_')
}
FIDELITY_SCHEDULE = best_params.get('fidelity_schedule', 'L0_L2')
SEMAPHORE = best_params.get('semaphore', 8)

print(f"\n📊 Meta-SEC params:")
print(f"  Ladder points: {N_LADDER_POINTS} (log-spaced {LADDER_LOG_MIN:.2f} to {LADDER_LOG_MAX:.2f})")
print(f"  Claim seeds: {CLAIM_SEEDS}")
print(f"  Min effect sizes: {MIN_EFFECT_SIZE_BY_FAMILY}")
print(f"  Fidelity: {FIDELITY_SCHEDULE}")
print(f"  Semaphore: {SEMAPHORE}")

# Import after applying void rules and setting params
from computronium.experiment.sec_all_axes import (
    AXIS_DEFAULTS,
    FAMILY_TO_TASK,
    _build_axis_box,
    _get_primary_knob,
    _get_task_families_for_primitive,
    run_rung2_comparison,
    create_registration,
    screen_coordinate,
)
from computronium.experiment.sec_loop import _measure, _task_bar
from computronium.experiment.schema.coordinate import Schedule
from computronium.experiment.sec_all_axes import LadderRung, PairedCell, RungResult
from computronium.validation.preregistration import (
    DEFAULT_ALPHA,
    EffectSizeRegistration,
    ThresholdRegistration,
    paired_comparison,
)

# Override module constants with meta-SEC best params
import computronium.experiment.sec_all_axes as sec_all_axes

# Generate log-spaced ladder factors
sec_all_axes.LADDER_FACTORS = tuple(
    10 ** (LADDER_LOG_MIN + i * (LADDER_LOG_MAX - LADDER_LOG_MIN) / (N_LADDER_POINTS - 1))
    for i in range(N_LADDER_POINTS)
)
sec_all_axes.CLAIM_SEEDS = CLAIM_SEEDS
sec_all_axes.MIN_EFFECT_SIZE_BY_FAMILY.update(MIN_EFFECT_SIZE_BY_FAMILY)

print(f"\n🔧 Updated constants:")
print(f"  LADDER_FACTORS: {[f'{f:.3f}' for f in sec_all_axes.LADDER_FACTORS]}")
print(f"  CLAIM_SEEDS: {sec_all_axes.CLAIM_SEEDS}")
print(f"  MIN_EFFECT_SIZE_BY_FAMILY: {sec_all_axes.MIN_EFFECT_SIZE_BY_FAMILY}")

# Fidelity mapping
FIDELITY_EPOCHS = {"L0": 1, "L1": 5, "L2": 20}
FIDELITY_SEEDS = {"L0": 1, "L1": 3, "L2": 5}

# Determine Rung 2 fidelity from schedule
if "L2" in FIDELITY_SCHEDULE:
    RUNG2_FIDELITY = "L2"
elif "L1" in FIDELITY_SCHEDULE:
    RUNG2_FIDELITY = "L1"
else:
    RUNG2_FIDELITY = "L0"

RUNG2_EPOCHS = FIDELITY_EPOCHS[RUNG2_FIDELITY]
RUNG2_SEEDS = FIDELITY_SEEDS[RUNG2_FIDELITY]

print(f"\n🎯 Rung 2 fidelity: {RUNG2_FIDELITY} (epochs={RUNG2_EPOCHS}, seeds={RUNG2_SEEDS})")

# All axes to run
AXES = list(AXIS_DEFAULTS.keys())
print(f"\n🎯 Running SEC on axes: {AXES}")

# Results directory
RESULTS_DIR = Path("results/sec/full_competitive")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


async def run_rung1_ladder_fixed(
    axis: str,
    primitive: str,
    task_id: str,
    semaphore_limit: int = 2,
) -> tuple[list[LadderRung], LadderRung | None, str]:
    """Run 3-point ladder for a primitive on its primary knob (L0 fidelity)."""
    knob_info = _get_primary_knob(axis, primitive, task_id=task_id)
    if knob_info is None:
        return [], None, "no_knob"

    knob_key, default_value = knob_info
    knob_name = knob_key.split(".", 1)[1]

    int_params = {
        "max_steps", "hidden_dim", "depth", "width", "num_layers",
        "num_experts", "top_k", "conv_channels", "kernel_size",
        "num_heads", "seq_len", "lattice_dims", "mem_slots",
        "mem_width", "grid_hw", "neurons_per_tile", "tiles_per_layer",
    }
    is_int_param = knob_name in int_params

    base_box = _build_axis_box(axis, primitive, task_id)

    rungs: list[LadderRung] = []
    semaphore = asyncio.Semaphore(semaphore_limit)

    async def run_rung(factor: float, value: float) -> LadderRung:
        async with semaphore:
            box = dict(base_box)
            box[knob_key] = round(value) if is_int_param else value
            # Use L0 fidelity for fast screening
            box["epochs"] = 1
            box["n_seeds"] = 1
            box["fidelity"] = "L0"

            schedule = Schedule(
                fidelity="L0",
                seed=0,
                n_seeds=1,
                epochs=1,
                batch_limit=box.get("batch_limit", 0),
                batch_size=box.get("batch_size", 32),
                budget_id=f"rung1-{axis}-{primitive}-{task_id}",
                task_id=task_id,
                param_budget=box.get("param_budget", 150000),
                device=box.get("device", "cuda"),
                deterministic=True,
                num_workers=0,
                precision="fp32",
                checkpoint_every_n=0,
            )

            coord = screen_coordinate(box, axis, primitive)
            measured = await asyncio.to_thread(_measure, coord, schedule)

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
        for factor in sec_all_axes.LADDER_FACTORS
    ]
    rungs = await asyncio.gather(*tasks)

    # Find best rung
    measured_rungs = [
        r for r in rungs if r.status == "measured" and r.val_acc is not None
    ]
    if not measured_rungs:
        return rungs, None, "all_refused"

    best = max(measured_rungs, key=lambda r: r.val_acc or 0.0)

    # Check if best clears the bar
    bar = _task_bar(task_id)
    if bar is not None and (best.val_acc or 0.0) <= bar.value:
        return rungs, best, "below_bar"

    return rungs, best, "viable"


async def run_primitive_full_fixed(
    axis: str,
    primitive: str,
    task_id: str,
    semaphore_limit: int = 2,
) -> RungResult:
    """Run Rung 1 ladder + Rung 2 comparison for one primitive."""
    started = time.monotonic()

    task_families = _get_task_families_for_primitive(axis, primitive)
    task_family = task_families[0] if task_families else "vision"

    # Rung 1: L0 fidelity ladder
    rungs, best, rung1_verdict = await run_rung1_ladder_fixed(
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

        # Create registration if not exists (will use RUNG2_FIDELITY epochs)
        if not reg_path.exists():
            await create_registration(axis, primitive, task_id, reg_path)

        result = await run_rung2_comparison(
            axis,
            primitive,
            task_id,
            best.value,
            reg_path,
            n_seeds=RUNG2_SEEDS,
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


async def run_axis_full(
    axis: str,
    semaphore_limit: int = 2,
) -> dict:
    """Run full SEC (Rung 1 + 2) for all primitives in an axis."""
    primitives = sec_all_axes._get_primitives_for_axis(axis)
    results = []

    for primitive in primitives:
        task_families = _get_task_families_for_primitive(axis, primitive)
        if not task_families:
            continue

        task_family = task_families[0]
        task_id = FAMILY_TO_TASK.get(task_family, "mnist")

        print(f"\n=== {axis}/{primitive} on {task_id} ({task_family}) ===")
        result = await run_primitive_full_fixed(axis, primitive, task_id, semaphore_limit)
        results.append(result)

        print(f"  Rung 1: {result.rung1_verdict}")
        if result.best_rung:
            print(f"  Best: {result.best_rung['factor']}x = {result.best_rung['val_acc']:.4f}")
        if result.rung2_verdict:
            d = result.rung2_effect.get('cohens_dz', 0) if result.rung2_effect else 0
            print(f"  Rung 2: {result.rung2_verdict} (d={d:.2f})")

    return {
        'axis': axis,
        'results': [r.to_dict() for r in results],
        'summary': {
            'total_primitives': len(results),
            'viable': sum(1 for r in results if r.rung1_verdict == 'viable'),
            'claims': sum(1 for r in results if r.rung2_verdict == 'claim'),
            'coordinates': sum(1 for r in results if r.rung2_verdict == 'coordinate'),
            'defects': sum(1 for r in results if r.rung2_verdict == 'defect'),
        }
    }


async def main():
    """Run full competitive SEC across all axes."""
    all_results = {}

    for axis in AXES:
        print(f"\n{'='*60}")
        print(f"🏃 Axis: {axis}")
        print(f"{'='*60}")

        axis_result = await run_axis_full(axis, semaphore_limit=SEMAPHORE)
        all_results[axis] = axis_result

        # Save axis results
        axis_file = RESULTS_DIR / f"{axis}_results.json"
        axis_file.write_text(json.dumps(axis_result, indent=2), encoding="utf-8")
        print(f"  Saved: {axis_file}")

        s = axis_result['summary']
        print(f"  Summary: {s['claims']} claims, {s['coordinates']} coords, {s['defects']} defects ({s['viable']}/{s['total_primitives']} viable)")

    # Save combined results
    combined_file = RESULTS_DIR / "full_competitive_results.json"
    combined_file.write_text(json.dumps(all_results, indent=2), encoding="utf-8")
    print(f"\n💾 Combined results saved: {combined_file}")

    # Print summary
    print(f"\n{'='*60}")
    print("📊 FULL COMPETITIVE SEC SUMMARY")
    print(f"{'='*60}")

    total_claims = 0
    total_coords = 0
    total_defects = 0
    total_primitives = 0

    for axis, data in all_results.items():
        s = data['summary']
        print(f"  {axis:12s}: {s['claims']:2d} claims, {s['coordinates']:2d} coords, {s['defects']:2d} defects ({s['viable']}/{s['total_primitives']} viable)")
        total_claims += s['claims']
        total_coords += s['coordinates']
        total_defects += s['defects']
        total_primitives += s['total_primitives']

    print(f"{'='*60}")
    print(f"  TOTAL:      {total_claims:2d} claims, {total_coords:2d} coords, {total_defects:2d} defects")
    print(f"  Primitives tested: {total_primitives}")

    return all_results


if __name__ == "__main__":
    asyncio.run(main())