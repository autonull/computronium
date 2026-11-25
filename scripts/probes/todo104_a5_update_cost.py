"""TODO104 A5 probe: price `adafactor` and `natural_gradient` at L0.

Each arm runs one L0 cell beside a control (`adam`) at the same box. A cell
that spends its cooperative budget or costs an order of magnitude more than the
control is declared unavailable with the measured reason, instead of hanging
past the watchdog.
"""

from __future__ import annotations

import sys

from computronium.experiment.sec_all_axes import _build_axis_box, screen_coordinate
from computronium.experiment.sec_loop import _measure, base_schedule
from computronium.experiment.schema.seed_registries import seed_all_registries

ARMS = ("adam", "adafactor", "natural_gradient")
BUDGET_S = 300.0


def main() -> int:
    seed_all_registries()
    schedule = base_schedule("mnist", "auto")
    results = {}
    for arm in ARMS:
        box = _build_axis_box("update", arm, "mnist")
        box["epochs"] = 1
        box["fidelity"] = "L0"
        coord = screen_coordinate(box, "update", arm)
        result = _measure(coord, schedule, BUDGET_S)
        results[arm] = result
        print(
            f"update/{arm}: {result['status']} val_acc={result['val_acc']} "
            f"walltime={result['walltime_s']} reason={result['reason']}"
        )
    control = results["adam"]["walltime_s"] or 0.0
    for arm in ARMS[1:]:
        status = results[arm]["status"]
        cost = results[arm]["walltime_s"] or 0.0
        if status == "timeout":
            print(f"VERDICT {arm}: unavailable (cost) — spent {BUDGET_S:.0f}s")
        elif control and cost > 10 * control:
            print(f"VERDICT {arm}: unavailable (cost) — {cost / control:.1f}x adam")
        else:
            print(f"VERDICT {arm}: available (status={status})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
