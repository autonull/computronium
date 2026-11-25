"""TODO104 A2 probe: settle compiles once across geometries.

Runs the same substrate primitive at two task shapes in one process. Before the
fix, the second shape re-traced the ``dynamic=False`` graph and hit
``config.recompile_limit``, killing the cell and leaking a semaphore. The probe
fails when either cell is not ``measured`` or a recompile-limit error is raised.
"""

from __future__ import annotations

import torch

from computronium.experiment.sec_all_axes import _build_axis_box, screen_coordinate
from computronium.experiment.sec_loop import _measure, base_schedule
from computronium.experiment.schema.seed_registries import seed_all_registries

# Two widths of the same task: a second shape reaches the same settle kernel.
CASES = (
    ("substrate", "neuromorphic", "spiking_mnist", {}),
    ("substrate", "neuromorphic", "spiking_mnist", {"geometry.hidden_dim": 96}),
)


def main() -> int:
    seed_all_registries()
    print(f"device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu'}")
    failures = 0
    for axis, primitive, task_id, overrides in CASES:
        box = _build_axis_box(axis, primitive, task_id)
        box.update(overrides)
        box["epochs"] = 1
        box["fidelity"] = "L0"
        coord = screen_coordinate(box, axis, primitive)
        schedule = base_schedule(task_id, "auto")
        result = _measure(coord, schedule, 120.0)
        width = box.get("geometry.hidden_dim")
        print(
            f"{axis}/{primitive} @ {task_id} hidden={width}: {result['status']} "
            f"val_acc={result['val_acc']} walltime={result['walltime_s']} "
            f"reason={result['reason']}"
        )
        if result["status"] != "measured":
            failures += 1
    print("PASS" if failures == 0 else f"FAIL ({failures} cell(s) not measured)")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
