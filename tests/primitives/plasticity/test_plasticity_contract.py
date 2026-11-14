"""The plasticity axis contract, parameterized by spec.

The case/reference seed contract is axis-independent and lives in
``tests/primitives/test_primitive_contract.py``. What is specific to a
plasticity law is its plastic state: a mapping of tensors whose schema the step
preserves, empty for a law that has no plastic state, bounded for the routing
law. The legacy per-package triples asserted these law by law.
"""

from __future__ import annotations

import pytest
import torch

from tests.primitives._contract import axis_specs, make_case, payload, reference

SPECS = axis_specs("plasticity")
IDS = [spec.id for spec in SPECS]

#: Laws that return their input plastic state unchanged.
NO_OP = ("primitive.plasticity.null", "primitive.plasticity.substrate_coupled")


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_step_returns_a_plastic_state_mapping(spec) -> None:
    """The step returns a dict of tensors."""
    output = reference(spec, make_case(spec, seed=0))
    assert isinstance(output, dict), spec.id
    assert all(isinstance(value, torch.Tensor) for value in output.values()), spec.id


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_plastic_state_schema_is_seed_independent(spec) -> None:
    """Both seeds produce the same key set."""
    keys = [frozenset(reference(spec, make_case(spec, seed=seed))) for seed in (0, 1)]
    assert keys[0] == keys[1], spec.id


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_step_preserves_every_state_tensor_it_names(spec) -> None:
    """Every case tensor an output key names survives with its shape.

    Covers a law that carries its plastic state in a ``psi`` mapping and one
    that carries it in named fields (fast weights, routing gates).
    """
    case = make_case(spec, seed=0)
    output = reference(spec, case)
    for name, value in payload(case).items():
        items = value.items() if isinstance(value, dict) else ((name, value),)
        for key, tensor in items:
            if key in output and isinstance(tensor, torch.Tensor):
                assert output[key].shape == tensor.shape, (spec.id, key)


def test_no_op_laws_return_an_empty_state() -> None:
    """A law with no plastic state returns an empty mapping."""
    for spec_id in NO_OP:
        spec = next(spec for spec in SPECS if spec.id == spec_id)
        assert reference(spec, make_case(spec, seed=0)) == {}, spec_id


def test_routing_keeps_active_routes_in_the_unit_interval() -> None:
    """Routing's gate weights stay a convex mixing of routes."""
    spec = next(spec for spec in SPECS if spec.id == "primitive.plasticity.routing")
    routes = reference(spec, make_case(spec, seed=0))["active_routes"]
    assert (routes >= 0).all() and (routes <= 1).all()
