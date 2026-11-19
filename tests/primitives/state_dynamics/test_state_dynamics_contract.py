"""The state-dynamics axis contract, parameterized by spec.

The case/reference seed contract is axis-independent and lives in
``tests/primitives/test_primitive_contract.py``. What is specific to a dynamics
law is the settled state it returns: a composite state whose activity carries the
settled ``x`` the geometry was given, plus the settled activation stack and the
plastic and substrate slots.
"""

from __future__ import annotations

import pytest

from computronium.primitives.registry import list_primitives
from tests.primitives._contract import axis_specs, make_case, reference

SPECS = axis_specs("dynamics")
IDS = [spec.id for spec in SPECS]


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_settle_returns_a_composite_state(spec) -> None:
    """The settled state exposes activity, plastic, and substrate slots."""
    settled = reference(spec, make_case(spec, seed=0)).state["settled"]

    assert hasattr(settled, "activity"), spec.id
    assert hasattr(settled, "plastic"), spec.id
    assert hasattr(settled, "substrate"), spec.id
    assert "x" in settled.activity, spec.id


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_settled_activities_keep_the_input_batch(spec) -> None:
    """The settled activation stack starts from the case's presentation."""
    case = make_case(spec, seed=0)
    settled = reference(spec, case).state["settled"]
    x = case.extra["state"].activity["x"]

    assert settled.activity["x"].shape == x.shape, spec.id
    assert settled.activations, spec.id
    for activation in settled.activations:
        assert activation.shape[0] == x.shape[0], spec.id


def test_the_registry_covers_every_dynamics() -> None:
    """The contract runs over the registry's dynamics rows, not a hand-kept list."""
    assert {spec.id for spec in SPECS} == {
        spec.id for spec in list_primitives("dynamics")
    }
