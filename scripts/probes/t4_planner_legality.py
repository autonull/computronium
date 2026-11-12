"""T4: after deleting the flat matrix, every dropped coordinate names a cause.

The flat ``_INCOMPATIBILITY_RULES`` table voided 15 348 of 58 968 space-legal
coordinates at the planner while the declared constraints had already spoken.
It is now deleted; ``iter_candidates`` is the only filter and its rejection
sink is the only place a drop can happen.

This probe walks a full-registry spec, counts the cells ``iter_candidates``
yields, and checks that yielded + counted rejections accounts for every unique
coordinate. A non-zero ``silent`` means a second filter still exists.

Run: uv run python scripts/probes/t4_planner_legality.py
Measured (2026-11-12, 13 tasks, curated 5x5x4x3x5x3 space):
**58,500 walked, 10,296 yielded, 48,204 counted rejections, 0 silent.**
Before the deletion the flat matrix dropped 15,348 of 58,968 coordinates
without a cause; now every drop carries a declared-constraint key.
"""

from __future__ import annotations

import json
from collections import Counter

from computronium.experiment.kernel.search_space import (
    _schedule,
    _walk,
    iter_candidates,
    search_space_from_spec,
)
from computronium.experiment.schema import AxisSelection, RunSpec, StructuralAxis
from computronium.experiment.schema.seed_registries import seed_all_registries

__all__ = ["main"]

RESULTS: dict[str, object] = {}


def main() -> int:
    seed_all_registries()
    tasks = (
        "mnist",
        "digits",
        "fashion_mnist",
        "kmnist",
        "usps",
        "cifar10",
        "proteins",
        "graph_classification",
        "cora",
        "citeseer",
        "iris",
        "wine",
        "pendulum",
    )
    spec = RunSpec(
        profile="t4-drift",
        fidelity="L0",
        n_seeds=1,
        epochs=1,
        budget_seconds=600.0,
        tasks=tasks,
        axes=(
            AxisSelection(
                axis=StructuralAxis.SUBSTRATE,
                primitives=("digital", "analog", "sparse", "ternary", "memristive"),
            ),
            AxisSelection(
                axis=StructuralAxis.GEOMETRY,
                primitives=("feedforward", "recurrent", "conv", "attention", "graph"),
            ),
            AxisSelection(
                axis=StructuralAxis.DYNAMICS,
                primitives=(
                    "instantaneous",
                    "energy_minimization",
                    "predictive_settling",
                    "pc_alm",
                ),
            ),
            AxisSelection(
                axis=StructuralAxis.PLASTICITY,
                primitives=("null", "routing", "fast_weights"),
            ),
            AxisSelection(
                axis=StructuralAxis.CREDIT,
                primitives=(
                    "gradient",
                    "random_projections",
                    "local_goodness",
                    "pc_alm",
                    "thermodynamic_contrast",
                ),
            ),
            AxisSelection(
                axis=StructuralAxis.UPDATE,
                primitives=("adam", "euclidean", "lion"),
            ),
        ),
    )
    space = search_space_from_spec(spec, tasks=tasks)
    walked = list(_walk(spec, space))
    unique = {
        coordinate.measurement_key(_schedule(spec, task)) for coordinate, task in walked
    }

    rejections: Counter[str] = Counter()
    yielded = list(
        iter_candidates(
            spec,
            space,
            check_composable=False,
            page_size=len(walked) + 1,
            use_void_cache=False,
            rejections=rejections,
        )
    )
    counted = sum(rejections.values())
    RESULTS.update({
        "tasks": len(tasks),
        "walked": len(walked),
        "unique_coordinates": len(unique),
        "yielded": len(yielded),
        "rejections": dict(rejections),
        "counted_rejections": counted,
        "silent": len(unique) - len(yielded) - counted,
    })
    print(json.dumps(RESULTS, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
