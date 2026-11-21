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


def test_the_quantized_state_step_is_bounded() -> None:
    """A packed second moment must not turn a small element into an eps step.

    An int8 block packs an element below half an LSB to zero; without a one-LSB
    floor on the dequantized second moment, the next step divides by ``eps``
    alone. Measured before the fix: ``max|dW|`` 0.01 -> 120.9 -> 1162.8 and
    the loss 1.34 -> 3.2e10 -> NaN at step 3.
    """
    from computronium.harness import update_geometry, update_pseudo_grads
    from computronium.ontology.update import update_from_config
    from computronium.primitives.cases import cell_config

    spec = next(row for row in SPECS if row.id.endswith(".quantized_adam"))
    case = make_case(spec, seed=0)
    geometry = update_geometry(case)
    grads = update_pseudo_grads(case, geometry)
    law = update_from_config(cell_config(spec, case.task_id).update)
    params = dict(geometry.params)
    for step in range(3):
        before = {name: value.detach().clone() for name, value in params.items()}
        params = law.step(params, grads, geometry)
        moved = max(float((params[name] - before[name]).abs().max()) for name in params)
        assert moved <= 2 * law.config.step_size, (step, moved)


def test_the_registry_covers_every_update() -> None:
    """The contract runs over the registry's update rows, not a hand-kept list."""
    assert {spec.id for spec in SPECS} == {
        spec.id for spec in list_primitives("update")
    }
