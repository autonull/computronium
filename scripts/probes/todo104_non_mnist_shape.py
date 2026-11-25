"""TODO104 6.3 probe: a non-MNIST task trains at its own extent.

Before the fix the family base box's mnist grid (28x28) travelled into a usps
(1,16,16) or digits (1,8,8) cell, so a spatial topology could not match its
task's input. Each case asserts the composed box carries the task's own extent
and that one L0 epoch is measured.
"""

from __future__ import annotations

from dataclasses import replace

from computronium.experiment.kernel.evaluate import task_shape
from computronium.experiment.schema.seed_registries import seed_all_registries
from computronium.experiment.sec_all_axes import _build_axis_box
from computronium.experiment.sec_loop import _measure, base_schedule, screen_coordinate

CASES = (
    ("conv", "usps", (1, 16, 16)),
    ("nca", "digits", (1, 8, 8)),
)
BUDGET_S = 180.0


def main() -> int:
    seed_all_registries()
    failures = 0
    for primitive, task_id, expected in CASES:
        shape = task_shape(task_id, "cpu")
        box = _build_axis_box("geometry", primitive, task_id)
        coord = screen_coordinate(
            box, "geometry", primitive, shape=shape, task_id=task_id
        )
        extent = coord.params.get("geometry.input_hw")
        grid = coord.params.get("geometry.grid_hw", extent)
        schedule = base_schedule(task_id, box.get("device", "auto"))
        schedule = replace(schedule, epochs=1, n_seeds=1, seed=0) if schedule else None
        result = (
            _measure(coord, schedule, BUDGET_S) if schedule else {"status": "no-box"}
        )
        print(
            f"{primitive}@{task_id}: input_shape={shape.input_shape} "
            f"extent={extent} grid={grid} status={result['status']} "
            f"val_acc={result['val_acc']} walltime={result['walltime_s']} "
            f"reason={result['reason']}"
        )
        if shape.input_shape != expected:
            print(f"  task shape moved: expected {expected}")
            failures += 1
        if extent != expected[-2:]:
            print(f"  box extent is not the task's: expected {expected[-2:]}")
            failures += 1
        if result["status"] != "measured":
            failures += 1
    print("PASS" if failures == 0 else f"FAIL ({failures} check(s))")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
