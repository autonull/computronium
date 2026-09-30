"""E3 seeded axis-effect reproduction probe (WP13).

Validates that the kernel reproduces a known axis effect across independent
seeds on the SyntheticGroundTruth fixture. The fixture has a known analytical
optimum; the probe measures the effect of moving along one parameter axis
(toward vs. away from the optimum) across N_seeds independent seeds and
reports the effect size with a 95% CI.

Pass criterion: the effect is statistically significant (p < 0.05) and the
CI excludes zero — the effect reproduces across seeds.

Measured regime (filled on run): dimension, n_seeds, effect_size, ci, p_value.
Informs: E3 scientific validity — the kernel detects real effects reproducibly.

Usage:
    uv run python scripts/probes/e3_seeded_axis_effect.py \
        [--dimension 6] [--seeds 10] [--noise 0.1] [--out logs/e3_summary.json]
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from computronium.experiment.evidence.protocol import (
    CostBudget,
    SyntheticGroundTruth,
    compute_effect_size,
    create_synthetic_fixture,
)


def _make_axis_effect(
    fixture: SyntheticGroundTruth,
    axis: int,
    treatment_offset: float,
    control_offset: float,
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Build treatment/control points differing along one parameter axis.

    Treatment moves toward the optimum along ``axis``; control moves away.
    """
    opt = fixture.optimum
    treatment = list(opt)
    control = list(opt)
    treatment[axis] = opt[axis] + treatment_offset
    control[axis] = opt[axis] + control_offset
    return tuple(treatment), tuple(control)


def run_axis_effect_reproduction(
    dimension: int = 6,
    n_seeds: int = 5,
    noise_std: float = 0.1,
    axis: int = 0,
    n_offsets: int = 10,
) -> dict:
    """Run the seeded axis-effect reproduction measurement.

    Measures the axis effect for ``n_offsets`` different treatment offsets
    (each a "task"), each across ``n_seeds`` independent seeds. The effect
    (treatment − control) should be negative (treatment is closer to optimum)
    and reproduce across all task/seed combinations.

    Returns:
        Dict with effect_size, ci, p_value, per-task scores, and metadata.
    """
    fixture = create_synthetic_fixture(
        dimension=dimension, interaction_strength=0.3, noise_std=noise_std
    )

    treatment_scores: list[float] = []
    control_scores: list[float] = []
    task_details: list[dict] = []

    for task_idx in range(n_offsets):
        # Vary the treatment offset: from near-optimum to far from optimum
        treatment_offset = -0.5 + task_idx * 0.3
        control_offset = 2.0
        treatment_pt, control_pt = _make_axis_effect(
            fixture, axis, treatment_offset, control_offset
        )

        task_treatment: list[float] = []
        task_control: list[float] = []
        for seed in range(n_seeds):
            t_score = fixture.evaluate(treatment_pt, seed=seed)
            c_score = fixture.evaluate(control_pt, seed=seed)
            task_treatment.append(t_score)
            task_control.append(c_score)

        # Per-task mean across seeds
        t_mean = float(np.mean(task_treatment))
        c_mean = float(np.mean(task_control))
        treatment_scores.append(t_mean)
        control_scores.append(c_mean)
        task_details.append({
            "task_idx": task_idx,
            "treatment_offset": treatment_offset,
            "treatment_mean": t_mean,
            "control_mean": c_mean,
            "effect": t_mean - c_mean,
        })

    budget = CostBudget.eval_count(n_offsets * n_seeds)
    effect = compute_effect_size(
        treatment=treatment_scores,
        control=control_scores,
        primary_metric="fixture_value",
        budget=budget,
        n_tasks=n_offsets,
        n_seeds=n_seeds,
        paired=True,
    )

    return {
        "dimension": dimension,
        "n_tasks": n_offsets,
        "n_seeds": n_seeds,
        "noise_std": noise_std,
        "axis": axis,
        "task_details": task_details,
        "effect_size": effect.effect_size,
        "ci_lower": effect.ci_lower,
        "ci_upper": effect.ci_upper,
        "p_value": effect.p_value,
        "test_used": effect.test_used,
        "reproduces": effect.is_significant() and effect.ci_upper < 0,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dimension", type=int, default=6)
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--offsets", type=int, default=10)
    ap.add_argument("--noise", type=float, default=0.1)
    ap.add_argument("--axis", type=int, default=0)
    ap.add_argument("--out", default="logs/e3_summary.json")
    args = ap.parse_args()

    started = time.monotonic()
    result = run_axis_effect_reproduction(
        dimension=args.dimension,
        n_seeds=args.seeds,
        noise_std=args.noise,
        axis=args.axis,
        n_offsets=args.offsets,
    )
    result["walltime_s"] = round(time.monotonic() - started, 2)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(json.dumps(result, indent=2))
    if not result["reproduces"]:
        msg = (
            f"Effect did NOT reproduce: d={result['effect_size']:.3f} "
            f"CI=[{result['ci_lower']:.3f}, {result['ci_upper']:.3f}] "
            f"p={result['p_value']:.4f}"
        )
        raise SystemExit(msg)


if __name__ == "__main__":
    main()
