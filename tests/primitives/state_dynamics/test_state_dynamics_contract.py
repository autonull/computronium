"""The state-dynamics axis contract, parameterized by spec.

The case/reference seed contract is axis-independent and lives in
``tests/primitives/test_primitive_contract.py``. What is specific to a dynamics
law is the settled state it returns: a composite state whose activity carries
the settled ``x`` the geometry was given, plus the settled activation stack and
plastic/substrate slots. The legacy per-package triples asserted the composite
shape law by law.
"""

from __future__ import annotations

import pytest

from tests.primitives._contract import axis_specs, make_case, reference

SPECS = axis_specs("state_dynamics")
IDS = [spec.id for spec in SPECS]


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_settle_returns_a_composite_state(spec) -> None:
    """The settled state exposes activity, plastic, and substrate slots."""
    case = make_case(spec, seed=0)
    settled = reference(spec, case)

    assert hasattr(settled, "activity"), spec.id
    assert hasattr(settled, "plastic"), spec.id
    assert hasattr(settled, "substrate"), spec.id
    assert "x" in settled.activity, spec.id


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_settled_activities_keep_the_input_batch(spec) -> None:
    """The settled activation stack starts from the case's presentation."""
    case = make_case(spec, seed=0)
    settled = reference(spec, case)

    assert settled.activity["x"].shape == case.state.shape, spec.id
    assert settled.activations, spec.id
    for activation in settled.activations:
        assert activation.shape[0] == case.state.shape[0], spec.id
