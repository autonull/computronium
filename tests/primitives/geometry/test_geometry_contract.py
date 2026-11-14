"""The geometry axis contract, parameterized by spec.

The case/reference seed contract is axis-independent and lives in
``tests/primitives/test_primitive_contract.py``; the forward shape, route shape,
and parameter count per coordinate are declared in
``tests/primitives/test_geometry_forward_contract.py``; kernel parity is in
``test_primitive_kernel_parity.py``. What the legacy per-package triples added
was that the reference forward returns a bare tensor, which is asserted here
over the case path they used.
"""

from __future__ import annotations

import pytest
import torch

from tests.primitives._contract import axis_specs, make_case, reference

SPECS = axis_specs("geometry")
IDS = [spec.id for spec in SPECS]


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_forward_returns_a_tensor(spec) -> None:
    """The reference forward returns logits, not a container."""
    logits = reference(spec, make_case(spec, seed=0))
    assert isinstance(logits, torch.Tensor), spec.id
    assert logits.numel() > 0, spec.id
