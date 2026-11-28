"""W64: the wave planner's pricing and admission rules, locked.

``experiment/wave.py`` is 2,229 lines and the only test that reaches it runs a
whole wave. The two decisions it makes before a cell starts were unchecked:

* **What a cell costs.** TODO104 A29 measured one task's cells spanning two
  orders of magnitude, so the box price must win over the task price and the
  task price over the run-wide estimate. A wrong precedence mis-sizes every
  run it plans.
* **Whether the next cell still fits.** The deadline is enforced inside a cell
  too, so a cell admitted without headroom does not fail fast: it trains a
  truncated epoch and records the budget cut as a FAIL (measured on mnist/L1:
  216 s needed, 173 s left, 9/10 epochs reported).

Both are policies, so both are asserted directly — no store, no training (D6).
"""

from __future__ import annotations

from collections import Counter
from types import SimpleNamespace

from computronium.experiment.schema.coordinate import Coordinate, Schedule
from computronium.experiment.wave import (
    CostModel,
    _estimate_cell_count,
    _expand_replicates,
    _rejection_summary,
    _SerialAdmission,
    box_key,
)

_PRICE = CostModel(
    cost_per_cell_s=30.0,
    startup_s=10.0,
    measured=True,
    per_task={"digits": 250.0},
    per_box={box_key("digits", "feedforward", "instantaneous", "gradient"): 4.4},
)
_COORD = Coordinate(
    substrate="digital",
    geometry="feedforward",
    dynamics="instantaneous",
    plasticity="null",
    credit="gradient",
    update="euclidean",
    params={},
)
_OTHER = Coordinate(
    substrate="digital",
    geometry="recurrent",
    dynamics="instantaneous",
    plasticity="null",
    credit="gradient",
    update="euclidean",
    params={},
)


def test_a_box_price_wins_over_its_task_price() -> None:
    """The most specific price wins; the run-wide estimate is the last resort."""
    assert (
        _PRICE.cost_for_box("digits", "feedforward", "instantaneous", "gradient") == 4.4
    )
    assert (
        _PRICE.cost_for_box("digits", "recurrent", "instantaneous", "gradient") == 250.0
    )
    # An unmeasured task pays the run-wide price; a task-less box inherits the
    # single measured task, which is the only price a one-task run has.
    assert (
        _PRICE.cost_for_box("mutag", "recurrent", "instantaneous", "gradient") == 30.0
    )
    assert _PRICE.cost_for_box(None, "recurrent", "instantaneous", "gradient") == 250.0

    two_tasks = CostModel(
        cost_per_cell_s=30.0,
        startup_s=10.0,
        measured=True,
        per_task={"digits": 250.0, "mutag": 2.0},
    )
    assert two_tasks.cost_for("mutag") == 2.0
    assert two_tasks.cost_for("cifar") == 30.0


def test_an_unmeasured_model_has_no_prices_to_prefer() -> None:
    default = CostModel(cost_per_cell_s=30.0, startup_s=10.0)

    assert default.source == "default"
    assert default.cost_for("digits") == 30.0
    assert (
        default.cost_for_box("digits", "feedforward", "instantaneous", "gradient")
        == 30.0
    )
    assert _PRICE.source == "measured"


def test_a_wave_is_priced_by_the_boxes_it_plans() -> None:
    """A wave of two boxes costs their mean, not the run-wide estimate."""
    schedule = Schedule(
        fidelity="L1",
        seed=0,
        n_seeds=1,
        epochs=1,
        batch_limit=2,
        budget_id="b",
        task_id="digits",
    )
    cells = [(_COORD, schedule), (_OTHER, schedule)]

    assert _PRICE.cost_for_cells(cells) == (4.4 + 250.0) / 2
    assert _PRICE.cost_for_cells([]) == 30.0


def test_a_budget_pays_startup_once_and_keeps_one_cell() -> None:
    """Startup is spent once; a budget too small for a cell still buys one."""
    assert _estimate_cell_count(1010, _PRICE) == 33
    assert _estimate_cell_count(0, _PRICE) == 1
    assert _estimate_cell_count(10, _PRICE) == 1


def test_a_serial_wave_admits_only_with_margin_over_the_last_cell() -> None:
    """Admission needs 1.05x the last measured walltime, not merely 'some'."""
    now = 900.0
    admission = _SerialAdmission(lambda: True, 1000.0, clock=lambda: now)
    admission.observe(SimpleNamespace(payload={"walltime_s": 95.0}))

    assert admission.fits()
    assert admission.needed_s() == 95.0 * 1.05
    assert admission.headroom_s() == 100.0

    now = 903.0
    assert not admission.fits()
    assert admission.headroom_s() < admission.needed_s()


def test_a_first_cell_needs_no_history() -> None:
    admission = _SerialAdmission(lambda: True, 1000.0, clock=lambda: 999.0)

    assert admission.fits()
    assert admission.needed_s() == 0.0


def test_a_passed_deadline_refuses_whatever_the_history() -> None:
    admission = _SerialAdmission(lambda: False, None, clock=lambda: 0.0)
    admission.observe(SimpleNamespace(payload={"walltime_s": 1.0}))

    assert not admission.fits()
    assert admission.headroom_s() == -1.0


def test_replicates_expand_to_one_cell_per_seed() -> None:
    """A ``n_seeds=3`` cell is three measurements, three measurement keys."""
    schedule = Schedule(
        fidelity="L1", seed=7, n_seeds=3, epochs=1, batch_limit=2, budget_id="b"
    )
    expanded = _expand_replicates([(_COORD, schedule)])

    assert len(expanded) == 3
    assert {s.seed for _, s in expanded} == {7, 8, 9}
    assert all(s.n_seeds == 1 for _, s in expanded)
    keys = {coord.measurement_key(s) for coord, s in expanded}
    assert len(keys) == 3


def test_the_rejection_summary_names_the_most_common_reasons() -> None:
    summary = _rejection_summary(Counter({"illegal box": 5, "duplicate": 2, "rare": 1}))

    assert summary == "illegal box (5), duplicate (2), rare (1)"
    assert _rejection_summary(Counter()) == ""
