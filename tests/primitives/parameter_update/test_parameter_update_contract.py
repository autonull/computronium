"""The parameter-update axis contract, parameterized by spec.

The case/reference seed contract is axis-independent and lives in
``tests/primitives/test_primitive_contract.py``; kernel parity is in
``test_primitive_kernel_parity.py``. What is specific to an update rule is its
output: one updated tensor per geometry parameter, with the parameter's shape.
"""

from __future__ import annotations

import pytest
import torch

from computronium.harness import update_geometry
from computronium.primitives.registry import list_primitives
from tests.primitives._contract import axis_specs, make_case, reference

SPECS = axis_specs("update")
IDS = [spec.id for spec in SPECS]


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_step_returns_one_tensor_per_parameter(spec) -> None:
    """The step keys and shapes match the geometry's parameters."""
    case = make_case(spec, seed=0)
    params = update_geometry(case).params
    updated = reference(spec, case).state["updated"]

    assert isinstance(updated, dict), spec.id
    assert set(updated) == set(params), spec.id
    for name, tensor in updated.items():
        assert tensor.shape == params[name].shape, (spec.id, name)
        assert torch.isfinite(tensor).all(), (spec.id, name)


def test_the_registry_covers_every_update() -> None:
    """The contract runs over the registry's update rows, not a hand-kept list."""
    assert {spec.id for spec in SPECS} == {
        spec.id for spec in list_primitives("update")
    }
