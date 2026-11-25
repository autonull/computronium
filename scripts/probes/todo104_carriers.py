"""TODO104 8.1 probe: the two "unsupplied" structural carriers both train.

The map named graph and spatial_lattice as carriers no task supplies. Both are
declared rows with a task that can carry them: a graph reads `cora`'s own
edge_index, a lattice derives its extent from any 3-D task shape. This probe
screens each at its declared box and measures one L0 epoch; it fails when
either is refused or unmeasured.

Measured 2026-11-25: graph/cora 0.114 at 1.1 s (node classification, 1
epoch on the 140-node split); spatial_lattice/mnist 0.9167 at 67.5 s.
"""

from __future__ import annotations

from dataclasses import replace

from computronium.experiment.kernel.evaluate import task_shape
from computronium.experiment.schema.seed_registries import seed_all_registries
from computronium.experiment.sec_loop import (
    _base_axes,
    _coordinate,
    _is_legal,
    _measure,
    base_schedule,
)

CASES = (("graph", "cora"), ("spatial_lattice", "mnist"))
BUDGET_S = 180.0


def main() -> int:
    seed_all_registries()
    failures = 0
    for geometry, task_id in CASES:
        shape = task_shape(task_id, "cpu")
        axes = _base_axes(task_id)
        axes["geometry"] = geometry
        coord = _coordinate(axes, task_id=task_id, shape=shape)
        legal, reason = _is_legal(coord, task_id, shape)
        schedule = replace(base_schedule(task_id, "auto"), epochs=1, seed=0, n_seeds=1)
        result = _measure(coord, schedule, BUDGET_S)
        print(
            f"{geometry}@{task_id}: legal={legal} reason={reason} "
            f"status={result['status']} val_acc={result['val_acc']} "
            f"walltime={result['walltime_s']}"
        )
        if not legal or result["status"] != "measured":
            failures += 1
    print("PASS" if failures == 0 else f"FAIL ({failures} carrier(s))")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
