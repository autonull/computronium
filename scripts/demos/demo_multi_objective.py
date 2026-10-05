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

# The front comes from the one filter the report path uses, not a third copy.
# The copy this replaces dropped a duplicate of a non-dominated point (it tested
# inequality of the whole pair, so an exact repeat counted as dominating) and
# estimated param_count from hidden_dim instead of reading what was measured.
from computronium.experiment.surface.report import non_dominated


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
            config = make_pipeline_config(run_id, run_spec, "stratified_random", 3)
            records = run_pipeline(config, store)
            store.finish_run(run_id, "completed")

    points = [
        {
            "param_count": float(r.payload["param_count"]),
            "walltime_s": float(r.payload["walltime_s"]),
        }
        for r in records
        if "param_count" in r.payload and "walltime_s" in r.payload
    ]
    front = non_dominated(points, ("param_count", "walltime_s"), (False, False))
    print(f"records: {len(records)}, non-dominated: {len(front)}")
    for i in sorted(front, key=lambda j: points[j]["walltime_s"]):
        p, w = points[i]["param_count"], points[i]["walltime_s"]
        print(f"  params={p:>9.0f} walltime={w:.3e}  cell={records[i].cell_key[:16]}…")
    assert front
    print("Multi-objective demo: OK (non-dominated set printed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
