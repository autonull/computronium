"""The credit-assignment axis contract, parameterized by spec.

The case/reference seed contract is axis-independent and lives in
``tests/primitives/test_primitive_contract.py``. A credit rule returns one
pseudo-gradient per weight matrix, in the geometry's parameter order, and a
credit that is all zeros cannot train anything. The legacy per-package triples
asserted the return type and count law by law.
"""

from __future__ import annotations

import pytest
import torch

from tests.primitives._contract import axis_specs, make_case, reference

SPECS = axis_specs("credit_assignment")
IDS = [spec.id for spec in SPECS]


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_step_returns_one_pseudo_gradient_per_weight_matrix(spec) -> None:
    """The credit list covers the geometry's 2D parameters, in order and shape."""
    case = make_case(spec, seed=0)
    geometry = getattr(case, "geometry", None)
    credits = reference(spec, case)

    assert isinstance(credits, list), spec.id
    assert all(isinstance(credit, torch.Tensor) for credit in credits), spec.id
    if geometry is None:
        assert credits, spec.id  # a law with no geometry case must still produce credit
        return

    weights = [value for value in geometry.params.values() if value.dim() == 2]
    assert len(credits) == len(weights), (spec.id, len(credits), len(weights))
    for credit, weight in zip(credits, weights, strict=True):
        assert credit.shape == weight.shape, (spec.id, credit.shape, weight.shape)


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_a_credit_is_not_all_zeros(spec) -> None:
    """Every law produces a nonzero credit somewhere."""
    credits = reference(spec, make_case(spec, seed=0))
    assert any(torch.count_nonzero(credit) for credit in credits), spec.id
