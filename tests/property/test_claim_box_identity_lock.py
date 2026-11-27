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
from computronium.validation.preregistration import (
    EffectSizeRegistration,
    ThresholdRegistration,
)

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


def test_the_varied_knob_is_not_a_box_field() -> None:
    """The intervention is not part of the box identity (TODO104 A26).

    A registration that pinned the knob refused every treatment: the n=100
    claim measured d-CI-lower 0.876 against 0.8 and still returned
    coordinate, because the box disagreed on the knob it varies.
    """
    registration = EffectSizeRegistration(
        claim="tuning feedback_scale on random_projections",
        metric="val_acc",
        min_d=0.8,
        box={
            "credit": "random_projections",
            "fidelity": "L0",
            "epochs": 1,
            "task_id": "mnist",
        },
    )
    treatment = {
        "credit": "random_projections",
        "credit.feedback_scale": 0.2265,
        "fidelity": "L0",
        "seed": 64,
        "n_seeds": 1,
        "epochs": 1,
        "task_id": "mnist",
    }
    assert registration.box_mismatch(treatment) is None


def test_a_claim_below_the_registered_seed_floor_is_refused() -> None:
    """The registration's min_seeds gates the claim, not only its CI (W41).

    The n=64 confirmatory block cleared the d CI lower bound, but the
    registration is the n=205 rung; below its floor the comparison is not the
    registered test.
    """
    from computronium.validation.preregistration import PairedComparison

    box = {
        "credit": "random_projections",
        "fidelity": "L0",
        "epochs": 1,
        "batch_size": 32,
        "task_id": "mnist",
    }
    registration = EffectSizeRegistration(
        claim="tuning feedback_scale on random_projections",
        metric="val_acc",
        min_d=0.276769,
        min_seeds=205,
        box=dict(box),
    )
    pilot = PairedComparison(
        n=64,
        mean_diff=0.011976,
        ci_lower=0.005642,
        ci_upper=0.018305,
        p_value=4e-4,
        cohens_dz=0.453624,
    )
    assert not pilot.passes_effect_size(registration, box=box)

    # The same effect at the registered n clears the CI gate: the floor is the
    # only reason the n=64 comparison was refused.
    at_n_max = PairedComparison(
        n=205,
        mean_diff=0.011976,
        ci_lower=0.008360,
        ci_upper=0.015592,
        p_value=4e-4,
        cohens_dz=0.453624,
    )
    assert at_n_max.passes_effect_size(registration, box=box)
