"""The C1 gate must promote only on the pre-registered condition.

The ladder's verdict is a predicate the repository evaluates: a local arm at
the floor on two seeds promotes; at the floor on one seed it refuses; a
control below the floor invalidates the run rather than promoting the
treatment. Removing the second-seed check fails this test.
"""

from __future__ import annotations

from computronium.validation.plasticity_ladder import (
    FLOOR,
    LadderCell,
    _verdict,
)


def _cell(arm: str, acc: float, seed: int = 0) -> LadderCell:
    return LadderCell(
        stage="plasticity",
        arm=arm,
        knob=0.01,
        seed=seed,
        mean_final_acc=acc,
        last_task_acc=acc,
        backward_transfer=0.0,
        avg_forgetting=0.0,
        state_mb=0.0,
        time_s=0.0,
        accuracy_matrix=(),
    )


def test_two_seeds_above_floor_promote() -> None:
    best = {"local": _cell("local", FLOOR + 0.05), "backprop": _cell("backprop", 0.8)}
    verdict, _ = _verdict(best, (_cell("local", FLOOR + 0.01, seed=42),))
    assert verdict == "promote"


def test_confirmation_seed_below_floor_refuses() -> None:
    best = {"local": _cell("local", FLOOR + 0.05), "backprop": _cell("backprop", 0.8)}
    verdict, _ = _verdict(best, (_cell("local", FLOOR - 0.05, seed=42),))
    assert verdict == "refuse"


def test_control_at_chance_invalidates_the_run() -> None:
    best = {"local": _cell("local", FLOOR + 0.05), "backprop": _cell("backprop", 0.5)}
    verdict, _ = _verdict(best, (_cell("local", FLOOR + 0.01, seed=42),))
    assert verdict == "invalid-control"
