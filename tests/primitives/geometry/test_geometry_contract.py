"""The geometry axis contract, parameterized by spec.

The case/reference seed contract is axis-independent and lives in
``tests/primitives/test_primitive_contract.py``; the forward shape, route shape,
and parameter count per coordinate are declared in
``tests/primitives/test_geometry_forward_contract.py``; kernel parity is in
``test_primitive_kernel_parity.py``. What is specific to a geometry here is the
logits the reference forward returns: a bare tensor, never a container.
"""

from __future__ import annotations

import pytest
import torch

from computronium.primitives.registry import list_primitives
from tests.primitives._contract import axis_specs, make_case, reference

SPECS = axis_specs("geometry")
IDS = [spec.id for spec in SPECS]


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_forward_returns_a_tensor(spec) -> None:
    """The reference forward returns logits, not a container."""
    logits = reference(spec, make_case(spec, seed=0)).activations[-1]
    assert isinstance(logits, torch.Tensor), spec.id
    assert logits.numel() > 0, spec.id
    assert torch.isfinite(logits.float()).all(), spec.id


def test_the_registry_covers_every_geometry() -> None:
    """The contract runs over the registry's geometry rows, not a hand-kept list."""
    assert {spec.id for spec in SPECS} == {
        spec.id for spec in list_primitives("geometry")
    }
