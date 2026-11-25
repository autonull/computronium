"""Claim box identity lock (TODO104 A8).

A claim must be measured at the box its registration names. The ladder runs
``epochs=1`` while the registration declares the family base box, so a claim
that kept the ladder's schedule was refused by ``box_mismatch`` — or, worse,
decided at a box the ladder never measured. Removing ``claim_schedule`` lets
the fallback schedule through, and this lock fails.
"""

from __future__ import annotations

import pytest

from computronium.experiment.schema.coordinate import Schedule
from computronium.experiment.sec_claims import claim_schedule
from computronium.validation.preregistration import ThresholdRegistration

_LADDER = Schedule(
    fidelity="L0",
    seed=0,
    n_seeds=1,
    epochs=1,
    batch_limit=0,
    budget_id="rung1-mnist",
    task_id="mnist",
    batch_size=32,
)
_REGISTERED_BOX = {
    "fidelity": "L2",
    "seed": 0,
    "n_seeds": 5,
    "epochs": 20,
    "batch_size": 32,
    "task_id": "mnist",
    "device": "cuda",
    "precision": "fp32",
}


def _registration() -> ThresholdRegistration:
    return ThresholdRegistration(
        claim="tuning step_size on nn.energy_minimization moves val_acc",
        metric="val_acc",
        threshold=0.01,
        box=dict(_REGISTERED_BOX),
    )


def test_the_fixture_contains_the_case() -> None:
    """The ladder box genuinely disagrees with the registration."""
    registration = _registration()
    assert registration.box_mismatch(_LADDER) is not None


def test_claim_runs_at_the_registered_box() -> None:
    """The registration's fidelity/epochs/seeds win over the ladder's."""
    registration = _registration()
    resolved = claim_schedule(registration, _LADDER)
    assert resolved.fidelity == "L2"
    assert resolved.epochs == 20
    assert resolved.n_seeds == 5
    assert resolved.batch_size == 32
    assert registration.box_mismatch(resolved) is None


@pytest.mark.parametrize("field", ["fidelity", "epochs", "n_seeds"])
def test_every_declared_field_is_read(field: str) -> None:
    """A declared field the resolver skipped would re-open the mismatch."""
    registration = _registration()
    resolved = claim_schedule(registration, _LADDER)
    assert getattr(resolved, field) == _REGISTERED_BOX[field]


def test_undeclared_fields_keep_the_caller_value() -> None:
    """A field the registration omits is the caller's, never a silent default."""
    registration = ThresholdRegistration(
        claim="c", metric="val_acc", threshold=0.01, box={"epochs": 20}
    )
    resolved = claim_schedule(registration, _LADDER)
    assert resolved.epochs == 20
    assert resolved.fidelity == "L0"
    assert resolved.batch_limit == _LADDER.batch_limit


def test_the_declared_min_d_wins() -> None:
    """One authority for the threshold: the caller's, not a second table.

    The SEC ladder resolved 0.916 for vision while the registration's own table
    wrote 0.8 — two tables, one claim (TODO104 A25).
    """
    from computronium.validation.preregistration import EffectSizeRegistration

    declared = EffectSizeRegistration.for_task_family(
        claim="c", metric="val_acc", task_id="mnist", min_d=0.916
    )
    assert declared.min_d == 0.916
    fallback = EffectSizeRegistration.for_task_family(
        claim="c", metric="val_acc", task_id="mnist"
    )
    assert fallback.min_d > 0
