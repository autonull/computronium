"""E2 surrogate-acquisition effect-size probe (WP13).

Treatment: GP-surrogate policy (shared encoder subspace) over a random base.
Control: the same random base. Both run the closed-loop harness on synthetic
benchmark tasks; the protocol reports task-level Cohen's d + p-value.

Measured regime (to be filled on run): tasks, seeds, budget, d, p, walltime.
Informs: E2 calibration — whether a competent surrogate beats random on the
smooth bowl (naive learners lose; see TODO43.plan.md item 5).

Usage:
    uv run python scripts/probes/e2_surrogate_acquisition.py \
        --tasks 10 --seeds 5 --budget 100 [--out logs/e2_summary.json]
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from computronium.experiment.evidence.protocol import CostBudget
from computronium.experiment.learning.benchmark import (
    BenchmarkConfig,
    create_synthetic_benchmark_tasks,
    embedding_dims,
    run_acquisition_benchmark,
)
from computronium.experiment.learning.surrogate import (
    GaussianProcessSurrogate,
    SurrogateConfig,
    SurrogatePolicy,
)
from computronium.experiment.schema.coordinate import Coordinate

if TYPE_CHECKING:
    from computronium.experiment.schema.record import Record


class RandomBase:
    """Uniform-random proposer over the embedding spec ranges."""

    def __init__(self, seed: int) -> None:
        self._rng = np.random.RandomState(seed)
        self._specs = embedding_dims(6)

    def propose(self, n: int, context: dict) -> list[Coordinate]:
        del context
        out = []
        for _ in range(n):
            params = {
                s.name: float(self._rng.uniform(s.domain.lo or 0.0, s.domain.hi or 1.0))
                for s in self._specs
            }
            out.append(
                Coordinate(
                    substrate="Digital",
                    geometry="Feedforward",
                    dynamics="Instantaneous",
                    plasticity="NullPlasticity",
                    credit="Backprop",
                    update="Euclidean",
                    params=params,
                )
            )
        return out

    def observe(self, record: Record) -> None:
        del record

    def get_name(self) -> str:
        return "random-base"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", type=int, default=10)
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--budget", type=int, default=100)
    ap.add_argument("--out", default="logs/e2_summary.json")
    args = ap.parse_args()

    started = time.monotonic()
    tasks = create_synthetic_benchmark_tasks(n_tasks=args.tasks)
    config = BenchmarkConfig(
        n_tasks=args.tasks,
        n_seeds=args.seeds,
        budget=CostBudget.eval_count(args.budget),
    )
    gp_config = SurrogateConfig(n_initial_points=10, random_state=0)

    def treatment_factory() -> SurrogatePolicy:
        return SurrogatePolicy(
            RandomBase(seed=11),
            GaussianProcessSurrogate(gp_config),
            gp_config,
        )

    def control_factory() -> RandomBase:
        return RandomBase(seed=22)

    result = run_acquisition_benchmark(
        treatment_factory, control_factory, tasks, config
    )
    walltime_s = time.monotonic() - started

    effect = result.effect_size
    summary = {
        "tasks": args.tasks,
        "seeds": args.seeds,
        "budget_eval_count": args.budget,
        "cohens_d": effect.effect_size,
        "p_value": effect.p_value,
        "test_used": effect.test_used,
        "ci": [effect.ci_lower, effect.ci_upper],
        "walltime_s": round(walltime_s, 1),
    }
    with Path(args.out).open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
