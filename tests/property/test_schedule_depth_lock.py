"""Lock: an explicit seed/epoch count survives; only ``None`` follows the ladder.

``schedule_for`` read ``spec.n_seeds != 1`` as "unset", so ``--n-seeds 1`` ran
the L1 ladder's 3 seeds and ``--epochs 1`` ran 5. The spec field is
``int | None`` precisely so the two cases are distinguishable: ``None`` means
"follow the ladder", an explicit ``1`` is a literal.

Falsified by restoring the ``!= 1`` test: the explicit-1 cases return the
ladder values (3 seeds, 5 epochs at L1).
"""

from __future__ import annotations

from computronium.experiment.kernel.search_space import schedule_for

from ._specs import mechanism_spec

_LADDER_L1 = (3, 5)


def test_explicit_one_is_a_literal() -> None:
    spec = mechanism_spec().model_copy(update={"n_seeds": 1, "epochs": 1})
    schedule = schedule_for(spec, "digits", "L1")
    assert schedule.n_seeds == 1
    assert schedule.epochs == 1


def test_none_follows_the_ladder() -> None:
    spec = mechanism_spec().model_copy(update={"n_seeds": None, "epochs": None})
    schedule = schedule_for(spec, "digits", "L1")
    assert (schedule.n_seeds, schedule.epochs) == _LADDER_L1


def test_explicit_values_other_than_one_pass_through() -> None:
    spec = mechanism_spec().model_copy(update={"n_seeds": 4, "epochs": 7})
    schedule = schedule_for(spec, "digits", "L1")
    assert (schedule.n_seeds, schedule.epochs) == (4, 7)
