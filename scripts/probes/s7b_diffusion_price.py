"""Price the vision diffusion row at its own-knob box (TODO97 §3.3c).

The corrected recurrence made ``state_dynamics.diffusion`` the only row the
screen's shared 60 s cell cap refused. This probe runs that row alone and
prints the measured cell, the basis for ``P0_BUDGET_OVERRIDES_S`` in
``computronium/experiment/sec_loop.py`` (2x the measured cell, the SEC
watchdog rule).

Measured 2026-11-21 (mnist L0, 375 batches, own knobs): **76.9 s**, val_acc
0.1069 against chance 0.100 — a coordinate result at the re-opened box.

Run: ``uv run python scripts/probes/s7b_diffusion_price.py``
"""

from __future__ import annotations

import time

from computronium.experiment.kernel.evaluate import task_shape
from computronium.experiment.sec_loop import (
    _iter_legal_coordinates,
    _row_budget,
    _train_nearest,
    base_schedule,
    build_census,
)

PRIMITIVE = "primitive.state_dynamics.diffusion"


def main() -> None:
    entry = next(e for e in build_census() if e.id == PRIMITIVE)
    schedule = base_schedule("mnist", "cpu")
    if schedule is None:
        raise SystemExit("mnist declares no base box")
    candidates = list(
        _iter_legal_coordinates(
            entry,
            limit=8,
            own_knobs=True,
            task_id="mnist",
            shape=task_shape("mnist", "cpu"),
        )
    )
    started = time.monotonic()
    cell, coord, error, tried, timed_out = _train_nearest(
        candidates, schedule, _row_budget(PRIMITIVE)
    )
    print(f"wall={time.monotonic() - started:.1f}s tried={tried} timed_out={timed_out}")
    if cell is None or coord is None:
        print(f"no cell: {error!r}")
        return
    print(f"cell={cell.walltime_s:.1f}s val_acc={cell.metrics.get('val_acc')}")


if __name__ == "__main__":
    main()
