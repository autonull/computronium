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
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, "/home/me/computronium")

# Apply learned void rules BEFORE importing other modules that use DEFECT_REGISTRY
from computronium.experiment.legality.void_rules_learned import apply_learned_rules

apply_learned_rules()
print("✅ Applied learned void rules")

from computronium.experiment.evidence.claims import (  # ruff: ignore[module-import-not-at-top-of-file]
    DEFAULT_MIN_SEEDS,
)
from computronium.experiment.sec_parts import (  # ruff: ignore[module-import-not-at-top-of-file]
    reduce_parts,
    write_part,
)

# Load meta-SEC best params. An invalid study (objective never above 0) already
# carries its declared defaults, so the driver never treats a zero-value optimum
# as tuned (TODO104 A7).
with Path("/home/me/computronium/configs/meta_sec_best.json").open("r") as f:
    meta = json.load(f)

if not meta.get("valid", False):
    print(f"⛔ meta-SEC best is not a live optimum: {meta.get('reason', 'unknown')}")
    print("   using its declared defaults")
best_params = meta.get("best_params", {})

# Extract params
N_LADDER_POINTS = best_params.get("n_ladder_points", 4)
LADDER_LOG_MIN = best_params.get("ladder_log_min", -1.1)
LADDER_LOG_MAX = best_params.get("ladder_log_max", 1.5)
# The seed floor is declared once (DEFAULT_MIN_SEEDS); a sub-floor budget
# cannot carry a paired comparison (TODO104 A6).
CLAIM_SEEDS = max(
    int(best_params.get("claim_seeds", DEFAULT_MIN_SEEDS)), DEFAULT_MIN_SEEDS
)
MIN_EFFECT_SIZE_BY_FAMILY = {
    k.replace("min_d_", ""): v for k, v in best_params.items() if k.startswith("min_d_")
}
FIDELITY_SCHEDULE = best_params.get("fidelity_schedule", "L0_L2")
SEMAPHORE = best_params.get("semaphore", 8)

print("\n📊 Meta-SEC params:")
print(
    f"  Ladder points: {N_LADDER_POINTS} (log-spaced {LADDER_LOG_MIN:.2f} to {LADDER_LOG_MAX:.2f})"
)
print(f"  Claim seeds: {CLAIM_SEEDS}")
print(f"  Min effect sizes: {MIN_EFFECT_SIZE_BY_FAMILY}")
print(f"  Fidelity: {FIDELITY_SCHEDULE}")
print(f"  Semaphore: {SEMAPHORE}")

# Import after applying void rules and setting params
# Override module constants with meta-SEC best params
from computronium.experiment import sec_all_axes
from computronium.experiment.schema.coordinate import Schedule
from computronium.experiment.sec_all_axes import (
    AXIS_DEFAULTS,
    FAMILY_TO_TASK,
    LadderRung,
    RungResult,
    _build_axis_box,
    _get_primary_knob,
    _get_task_families_for_primitive,
    _measure_async,
    create_registration,
    preferred_task_family,
    resolve_semaphore,
    run_rung2_comparison,
    screen_coordinate,
)

# Generate log-spaced ladder factors. The declared default (factor 1.0) is
# always screened: a ladder that never runs the primitive at its own default
# cannot rank the primitive against it, and a calibrated span may not contain
# the default.
sec_all_axes.LADDER_FACTORS = tuple(
    sorted({
        *(
            10
            ** (
                LADDER_LOG_MIN
                + i * (LADDER_LOG_MAX - LADDER_LOG_MIN) / (N_LADDER_POINTS - 1)
            )
            for i in range(N_LADDER_POINTS)
        ),
        1.0,
    })
)
sec_all_axes.CLAIM_SEEDS = CLAIM_SEEDS
sec_all_axes.MIN_EFFECT_SIZE_BY_FAMILY.update(MIN_EFFECT_SIZE_BY_FAMILY)

print("\n🔧 Updated constants:")
print(f"  LADDER_FACTORS: {[f'{f:.3f}' for f in sec_all_axes.LADDER_FACTORS]}")
print(f"  CLAIM_SEEDS: {sec_all_axes.CLAIM_SEEDS}")
print(f"  MIN_EFFECT_SIZE_BY_FAMILY: {sec_all_axes.MIN_EFFECT_SIZE_BY_FAMILY}")

# Fidelity mapping
FIDELITY_EPOCHS = {"L0": 1, "L1": 5, "L2": 20}
FIDELITY_SEEDS = {"L0": 1, "L1": 3, "L2": 5}

# Primitives known to be too slow for ladder screening (estimator-heavy or
# 200-epoch base boxes). Each still runs Rung 1 where cheap; these are skipped
# because they exceed the per-primitive watchdog at their declared base box.
SLOW_PRIMITIVES = {
    # Priced, not guessed: these declare boxes that exceed the per-cell budget
    # at their family base box. The cooperative deadline returns a timeout
    # record for any cell that still overruns (TODO104 A3), so a skip here is
    # a cost statement, never a mechanism verdict.
    "credit": set(),
    "dynamics": {"diffusion", "lazy", "pc_alm", "predictive_settling"},
    "geometry": {"causal_transformer", "nca"},
    "plasticity": set(),
    "substrate": set(),
    "update": {"adafactor", "natural_gradient"},
}

# Rung 2 uses each task family's declared base box (base_schedule) and the seed
# budget its registration declares. One source: the registration's min_seeds is
# CLAIM_SEEDS, so a claim runs exactly the budget it was registered at.
RUNG2_SEEDS = int(os.environ.get("SEC_RUNG2_SEEDS", str(CLAIM_SEEDS)))
# A confirmatory run uses seeds the pilot never touched: the offset is part of
# the pre-registration, so a rerun at a larger n is not a peeked repeat.
RUNG2_SEED_OFFSET = int(os.environ.get("SEC_RUNG2_SEED_OFFSET", "0"))

print(
    f"\n🎯 Rung 2 seeds: {RUNG2_SEEDS} (family base-box epochs, "
    f"floor {DEFAULT_MIN_SEEDS})"
)

# Cooperative cell budgets: a cell stops itself mid-epoch at its deadline and
# returns a timeout record. Priced from the measured L0 pilot (~1-7s/cell); Rung 2
# runs a family base box (epochs x seeds x 2 arms), so allow generously.
RUNG_TIMEOUT = 120.0
RUNG2_TIMEOUT = 600.0

# Environment overrides keep each axis in its own process: a fresh torch.compile
# state per axis and one GPU training at a time (semaphore=1) avoid the
# recompile-thrash timeouts that concurrency causes under one process.
_env_axes = os.environ.get("SEC_AXES", "").strip()
AXES = (
    [a.strip() for a in _env_axes.split(",") if a.strip()]
    if _env_axes
    else list(AXIS_DEFAULTS.keys())
)
SEMAPHORE = int(os.environ.get("SEC_SEMAPHORE", str(SEMAPHORE)))
# Coverage and claims are separate decisions: the coverage map is rung 1, a
# claim is a pre-registered rung 2 at n_seeds x 2 arms. SEC_RUNG2=none maps
# breadth without spending the paired cells.
RUNG2_ENABLED = os.environ.get("SEC_RUNG2", "auto").strip().lower() != "none"
RUNG_TIMEOUT = float(os.environ.get("SEC_RUNG_TIMEOUT", str(RUNG_TIMEOUT)))


_resolved = resolve_semaphore(SEMAPHORE)
if _resolved != SEMAPHORE:
    print(f"⚠️  SEC_SEMAPHORE={SEMAPHORE} refused; running one cell at a time")
SEMAPHORE = _resolved
# Cooperative cell budget: each rung stops itself instead of being killed.
sec_all_axes.MEASURE_BUDGET_S = RUNG_TIMEOUT
print(
    f"\n🎯 Running SEC on axes: {AXES} (semaphore={SEMAPHORE}, "
    f"rung2={'auto' if RUNG2_ENABLED else 'none'})"
)

# Results directory
# The skip list is a cost statement; SEC_INCLUDE_SLOW re-runs those rows once
# the deadline makes their cost measurable.
INCLUDE_SLOW = bool(os.environ.get("SEC_INCLUDE_SLOW"))

# A claim set is chosen, not "everything viable": SEC_PRIMITIVES restricts an
# axis run to the arms a claim is pre-registered for.
PRIMITIVES: set[str] = {
    p.strip() for p in os.environ.get("SEC_PRIMITIVES", "").split(",") if p.strip()
}

RESULTS_DIR = Path(os.environ.get("SEC_RESULTS_DIR", "results/sec/full_competitive"))
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
        # A rule that declares no live knob still has a capability: one cell at
        # its declared default, never a sweep of a field it ignores.
        rung, verdict = await sec_all_axes.measure_declared_default(
            axis, primitive, task_id, RUNG_TIMEOUT
        )
        return [rung], (rung if verdict == "viable" else None), verdict

    knob_key, default_value = knob_info
    knob_name = knob_key.split(".", 1)[1]

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
    is_int_param = knob_name in int_params

    base_box = _build_axis_box(axis, primitive, task_id)

    rungs: list[LadderRung] = []
    semaphore = asyncio.Semaphore(semaphore_limit)

    async def run_rung(factor: float, value: float) -> LadderRung:
        async with semaphore:
            box = dict(base_box)
            box[knob_key] = sec_all_axes.knob_point(axis, primitive, knob_name, value)
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
                device=box.get("device", "auto"),
                deterministic=True,
                num_workers=0,
                precision="fp32",
                checkpoint_every_n=0,
            )

            coord = screen_coordinate(box, axis, primitive)
            measured = await _measure_async(coord, schedule, RUNG_TIMEOUT)

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
    rungs = await asyncio.gather(*tasks, return_exceptions=True)
    # Handle exceptions
    processed_rungs = []
    for i, r in enumerate(rungs):
        if isinstance(r, Exception):
            factor = sec_all_axes.LADDER_FACTORS[i]
            processed_rungs.append(
                LadderRung(
                    factor=factor,
                    value=round(default_value * factor)
                    if is_int_param
                    else default_value * factor,
                    status="error",
                    val_acc=None,
                    walltime_s=0.0,
                    replay_hash=None,
                    box={},
                    reason=f"Exception: {r}",
                )
            )
        else:
            processed_rungs.append(r)
    rungs = processed_rungs

    # Find best rung
    measured_rungs = [
        r for r in rungs if r.status == "measured" and r.val_acc is not None
    ]
    if not measured_rungs:
        return rungs, None, "all_refused"

    best = max(measured_rungs, key=lambda r: r.val_acc or 0.0)
    return rungs, best, sec_all_axes.ladder_verdict(axis, primitive, task_id, best)


async def run_primitive_full_fixed(
    axis: str,
    primitive: str,
    task_id: str,
    semaphore_limit: int = 2,
) -> RungResult:
    """Run Rung 1 ladder + Rung 2 comparison for one primitive."""

    async def _run():
        started = time.monotonic()

        task_families = _get_task_families_for_primitive(axis, primitive)
        task_family = preferred_task_family(task_families) or "vision"

        # Rung 1: L0 fidelity ladder
        rungs, best, rung1_verdict = await run_rung1_ladder_fixed(
            axis, primitive, task_id, semaphore_limit
        )

        rung2_cells = None
        rung2_effect = None
        rung2_verdict = None

        # Rung 2: paired comparison at best point
        if best is not None and rung1_verdict == "viable" and RUNG2_ENABLED:
            # Generate registration path
            reg_dir = Path("configs/preregistrations")
            reg_dir.mkdir(parents=True, exist_ok=True)
            reg_path = reg_dir / f"sec_{axis}_{primitive}.json"

            # Create registration if not exists (will use RUNG2_FIDELITY epochs)
            if not reg_path.exists():
                await create_registration(axis, primitive, task_id, reg_path)

            try:
                result = await run_rung2_comparison(
                    axis,
                    primitive,
                    task_id,
                    best.value,
                    reg_path,
                    n_seeds=RUNG2_SEEDS,
                    semaphore_limit=semaphore_limit,
                    budget_s=RUNG2_TIMEOUT,
                    seed_offset=RUNG2_SEED_OFFSET,
                )
                if result:
                    rung2_cells, rung2_effect, rung2_verdict = result
            except Exception as e:
                print(f"  Rung 2: ERROR - {e}")
                rung2_verdict = "error"

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

    # Each rung carries its own cooperative budget, so a spent rung returns a
    # timeout cell; no thread is left holding the device (TODO104 A3).
    return await _run()


async def run_axis_full(
    axis: str,
    semaphore_limit: int = 2,
) -> dict:
    """Run full SEC (Rung 1 + 2) for all primitives in an axis."""
    primitives = sec_all_axes._get_primitives_for_axis(axis)
    # A claim set is chosen, not "everything viable": SEC_PRIMITIVES runs the
    # coverage map on the arms a claim is pre-registered for.
    if PRIMITIVES:
        primitives = [p for p in primitives if p in PRIMITIVES]

    for primitive in primitives:
        task_families = _get_task_families_for_primitive(axis, primitive)
        if not task_families:
            continue

        # Skip known-slow primitives
        if primitive in SLOW_PRIMITIVES.get(axis, set()) and not INCLUDE_SLOW:
            print(f"\n=== {axis}/{primitive}: SKIPPED (known slow) ===")
            write_part(RESULTS_DIR, axis, primitive, "skipped", {})
            continue

        task_family = preferred_task_family(task_families) or "vision"
        task_id = FAMILY_TO_TASK.get(task_family, "mnist")

        print(f"\n=== {axis}/{primitive} on {task_id} ({task_family}) ===")
        try:
            result = await run_primitive_full_fixed(
                axis, primitive, task_id, semaphore_limit
            )
        except Exception as exc:
            print(f"  ERROR: {exc}")
            write_part(
                RESULTS_DIR,
                axis,
                primitive,
                "error",
                {"primitive": primitive, "error": str(exc)},
            )
            continue

        write_part(RESULTS_DIR, axis, primitive, "measured", result.to_dict())
        print(f"  Rung 1: {result.rung1_verdict}")
        if result.best_rung:
            print(
                f"  Best: {result.best_rung['factor']}x = "
                f"{result.best_rung['val_acc']:.4f}"
            )
        if result.rung2_verdict:
            d = result.rung2_effect.get("cohens_dz", 0) if result.rung2_effect else 0
            print(f"  Rung 2: {result.rung2_verdict} (d={d:.2f})")

    return reduce_parts(RESULTS_DIR, axis)


async def main():
    """Run full competitive SEC across all axes."""
    all_results = {}

    for axis in AXES:
        print(f"\n{'=' * 60}")
        print(f"🏃 Axis: {axis}")
        print(f"{'=' * 60}")

        try:
            await run_axis_full(axis, semaphore_limit=SEMAPHORE)
        except Exception as exc:  # one axis death must not discard the others
            print(f"  AXIS FAILED: {type(exc).__name__}: {exc}")
        finally:
            axis_result = reduce_parts(RESULTS_DIR, axis)
            all_results[axis] = axis_result

            axis_file = RESULTS_DIR / f"{axis}_results.json"
            axis_file.write_text(json.dumps(axis_result, indent=2), encoding="utf-8")
            print(f"  Saved: {axis_file}")

            s = axis_result["summary"]
            print(
                f"  Summary: {s['claims']} claims, {s['coordinates']} coords, "
                f"{s['defects']} defects ({s['viable']}/{s['total_primitives']} viable)"
            )

    # Save combined results
    combined_file = RESULTS_DIR / "full_competitive_results.json"
    combined_file.write_text(json.dumps(all_results, indent=2), encoding="utf-8")
    print(f"\n💾 Combined results saved: {combined_file}")

    # Print summary
    print(f"\n{'=' * 60}")
    print("📊 FULL COMPETITIVE SEC SUMMARY")
    print(f"{'=' * 60}")

    total_claims = 0
    total_coords = 0
    total_defects = 0
    total_primitives = 0

    for axis, data in all_results.items():
        s = data["summary"]
        print(
            f"  {axis:12s}: {s['claims']:2d} claims, {s['coordinates']:2d} coords, {s['defects']:2d} defects ({s['viable']}/{s['total_primitives']} viable)"
        )
        total_claims += s["claims"]
        total_coords += s["coordinates"]
        total_defects += s["defects"]
        total_primitives += s["total_primitives"]

    print(f"{'=' * 60}")
    print(
        f"  TOTAL:      {total_claims:2d} claims, {total_coords:2d} coords, {total_defects:2d} defects"
    )
    print(f"  Primitives tested: {total_primitives}")

    return all_results


if __name__ == "__main__":
    asyncio.run(main())
