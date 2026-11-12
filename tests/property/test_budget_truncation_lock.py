"""Lock: a budget cut is a timeout, and an unaffordable cell is not started (N1).

Two misreadings of one budget cut, both measured on mnist/L1:

1. A cell whose last epoch was killed by the run deadline was recorded with
   ``cause=constraint_violation`` — the cause that sends an investigator after
   a compatibility bug. It is now ``timeout``; only a parameter-ceiling
   breach stays ``constraint_violation``.
2. A serial wave started a seed with 173 s left for work it had just measured
   at 216 s. It trains a truncated epoch and reports 9/10 epochs FAIL. The
   wave now admits the next cell only with its own measured cost as headroom,
   and reports the remainder as skipped.

Falsified by removing either: the incomplete cell reports a constraint
violation, or ``fits`` admits a cell the remaining budget cannot pay for.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from computronium.experiment.kernel.evaluate import _build_status_with_procedures
from computronium.experiment.kernel.search_space import schedule_for
from computronium.experiment.schema import FailureCause
from computronium.experiment.wave import (
    _ADMISSION_MARGIN,
    _first_wave_price,
    _SerialAdmission,
)

from ._specs import mechanism_spec

_ALWAYS = lambda: True  # ruff: ignore[lambda-assignment] — a two-line stand-in, not a mechanism


def _control(walltime: float, epochs: float) -> SimpleNamespace:
    return SimpleNamespace(payload={"walltime_s": walltime, "epochs_completed": epochs})


def test_first_wave_price_scales_the_control_epoch_time() -> None:
    """A control epoch is a measurement; the wave multiplies it by its own epochs."""
    spec = mechanism_spec()
    declared = schedule_for(spec, "digits", "L0").epochs
    price = _first_wave_price([_control(12.0, 2)], spec, "L0")
    assert price == 12.0 / 2 * max(1, declared)


def test_first_wave_price_declines_an_unusable_control() -> None:
    spec = mechanism_spec()
    assert _first_wave_price([], spec, "L0") is None
    assert _first_wave_price([_control(0.0, 1)], spec, "L0") is None
    assert _first_wave_price([_control(10.0, 0)], spec, "L0") is None


def _priced(task: str, fidelity: str, walltime: float, epochs: int = 1):
    return SimpleNamespace(
        payload={
            "task_id": task,
            "fidelity": fidelity,
            "walltime_s": walltime,
            "epochs_completed": epochs,
            "epochs_requested": epochs,
        }
    )


def test_only_cells_at_the_run_fidelity_price_the_cache() -> None:
    """The L0 positive control is not an L1 cell and must not price L1."""
    from computronium.experiment.wave import CostModel, _measure_cost_model

    prior = CostModel(30.0, 0.0, measured=False)
    model = _measure_cost_model(
        "cuda",
        "L1",
        "unused",
        [_priced("mnist", "L0", 20.3), _priced("mnist", "L1", 265.0)],
        prior,
    )
    assert model.per_task == {"mnist": 265.0}


def test_a_cheap_cell_does_not_become_the_run_wide_price() -> None:
    """A 0.1 s wine cell must not price an unmeasured task at 0.1 s."""
    from computronium.experiment.wave import CostModel, _measure_cost_model

    prior = CostModel(60.0, 0.0, measured=True, per_task={"mnist": 200.0})
    model = _measure_cost_model(
        "cuda", "L1", "unused", [_priced("wine", "L1", 0.1)], prior
    )
    assert model.per_task == {"mnist": 200.0, "wine": 0.1}
    assert model.cost_per_cell_s == pytest.approx((200.0 + 0.1) / 2)


def test_a_truncated_cell_does_not_price_the_cache() -> None:
    from computronium.experiment.wave import CostModel, _measure_cost_model

    prior = CostModel(30.0, 0.0, measured=False)
    truncated = SimpleNamespace(
        payload={
            "task_id": "mnist",
            "fidelity": "L1",
            "walltime_s": 216.0,
            "epochs_completed": 9,
            "epochs_requested": 10,
        }
    )
    model = _measure_cost_model("cuda", "L1", "unused", [truncated], prior)
    assert model is prior


def _status(complete: bool, within_ceiling: bool):
    return _build_status_with_procedures(
        False,
        complete,
        within_ceiling,
        param_count=2000 if not within_ceiling else 100,
        param_budget=1000,
        replay_hash="lock",
    )


def test_a_truncated_cell_is_a_timeout() -> None:
    assert _status(complete=False, within_ceiling=True).cause == FailureCause.TIMEOUT


def test_a_ceiling_breach_stays_a_constraint_violation() -> None:
    status = _status(complete=True, within_ceiling=False)
    assert status.cause == FailureCause.CONSTRAINT_VIOLATION


def test_a_passing_cell_has_no_failure_cause() -> None:
    ok = _build_status_with_procedures(
        True, True, True, param_count=100, param_budget=1000, replay_hash="lock"
    )
    assert ok.cause == FailureCause.UNKNOWN


class _Clock:
    """A clock the test advances by hand."""

    def __init__(self, now: float = 0.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now


def test_admission_needs_the_measured_cost_as_headroom() -> None:
    clock = _Clock()
    admission = _SerialAdmission(_ALWAYS, deadline_at=100.0, clock=clock)
    assert admission.fits()  # no measurement yet: the wave's own price decides

    admission.observe(SimpleNamespace(payload={"walltime_s": 20.0}))
    clock.now = 100.0 - 20.0 * _ADMISSION_MARGIN + 0.5  # a hair short
    assert not admission.fits()

    clock.now = 100.0 - 20.0 * _ADMISSION_MARGIN  # exactly enough
    assert admission.fits()


def test_admission_still_honours_the_deadline() -> None:
    admission = _SerialAdmission(lambda: False, deadline_at=None)
    assert not admission.fits()


def test_admission_without_a_deadline_never_blocks() -> None:
    admission = _SerialAdmission(_ALWAYS, deadline_at=None)
    admission.observe(SimpleNamespace(payload={"walltime_s": 10_000.0}))
    assert admission.fits()
