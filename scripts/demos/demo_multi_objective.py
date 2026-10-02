"""Demo: multi-objective Pareto discovery via the OBJECTIVES registry.

Expected: a non-dominated set printed over (param_count, walltime_s), both
minimize per OBJECTIVES_REGISTRY directions. Kernel records feed the front.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _support import fresh_store, make_pipeline_config, make_run_spec, run_pipeline


def _param_estimate(params: dict) -> int:
    dims = [params.get(k, 32) for k in ("hidden_dim",)]
    hidden = max(1, int(dims[0]))
    layers = max(1, int(params.get("num_layers", 1)))
    return 784 * hidden + hidden * layers * hidden + hidden * 10


def _non_dominated(points: list[tuple[int, float]]) -> list[int]:
    front = []
    for i, (pi, wi) in enumerate(points):
        dominated = any(p <= pi and w <= wi and (p, w) != (pi, wi) for p, w in points)
        if not dominated:
            front.append(i)
    return front


def main() -> int:
    from computronium.experiment.schema.registries import OBJECTIVES_REGISTRY

    with tempfile.TemporaryDirectory() as tmp:
        store, _ = fresh_store(Path(tmp), "pareto")
        directions = {
            name: OBJECTIVES_REGISTRY[name].direction
            for name in ("param_count", "walltime_total")
        }
        print(f"objective directions: {directions}")
        with store:
            run_spec = make_run_spec("digits")
            run_id = store.create_run(spec=run_spec)
            config = make_pipeline_config(
                run_id, run_spec, "stratified_random", 3, Path(tmp)
            )
            records = run_pipeline(config, store)
            store.finish_run(run_id, "completed")

    points = [
        (_param_estimate(r.params), float(r.payload.get("walltime_s", 0.0)))
        for r in records
    ]
    front = _non_dominated(points)
    print(f"records: {len(records)}, non-dominated: {len(front)}")
    for i in sorted(front, key=lambda j: points[j]):
        p, w = points[i]
        print(f"  params={p:>9} walltime={w:.3e}  cell={records[i].cell_key[:16]}…")
    assert front
    print("Multi-objective demo: OK (non-dominated set printed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
