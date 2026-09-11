"""Benchmark — adaptive vs fixed local feedback under matched norm.

Arms: fixed, adaptive (slow blend, feedback_lr=0.02), adaptive_reproject
(per-step re-projection, feedback_lr=1.0). Metrics: late-half improvement_per_norm, descent quality
(fraction of steps with loss decrease), final feedback alignment, walltime.
3 seeds, mean±var. Quick mode: 60 steps, small MLP — seconds on CPU.
"""

from __future__ import annotations

import argparse
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))

from local_feedback_demo import run_arm

N_SEEDS = 3
STEPS = 60


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="quick mode (default)")
    parser.parse_args()

    t0 = time.perf_counter()
    arms = {
        "fixed": (False, 0.02),
        "adaptive": (True, 0.02),
        "adaptive_reproject": (True, 1.0),
    }
    table: dict[str, dict[str, list[float]]] = {
        arm: {"late_ipn": [], "descent_quality": [], "final_alignment": []}
        for arm in arms
    }
    for seed in range(N_SEEDS):
        for arm, (adaptive, lr) in arms.items():
            r = run_arm(seed, adaptive=adaptive, steps=STEPS, feedback_lr=lr)
            losses: list[float] = r["losses"]  # type: ignore[assignment]
            table[arm]["late_ipn"].append(r["late_ipn"])  # type: ignore[arg-type]
            table[arm]["descent_quality"].append(
                sum(a < b for a, b in zip(losses[1:], losses[:-1])) / (STEPS - 1)
            )
            table[arm]["final_alignment"].append(r["feedback_alignment"])  # type: ignore[arg-type]

    print(f"seeds={N_SEEDS} steps={STEPS} (quick mode)")
    print(f"{'arm':14s} {'late_ipn':>18s} {'descent_q':>18s} {'align_final':>18s}")
    for arm in arms:
        row = " ".join(
            f"{statistics.mean(v):.4f}±{statistics.pstdev(v):.4f}".rjust(18)
            for v in table[arm].values()
        )
        print(f"{arm:14s} {row}")
    adaptive_better = statistics.mean(table["adaptive"]["late_ipn"]) > statistics.mean(
        table["fixed"]["late_ipn"]
    )
    print(f"adaptive beats fixed (mean late_ipn): {adaptive_better}")
    print(f"walltime: {time.perf_counter() - t0:.2f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
