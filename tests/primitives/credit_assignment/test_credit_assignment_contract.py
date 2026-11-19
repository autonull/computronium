"""The credit-assignment axis contract, parameterized by spec.

The case/reference seed contract is axis-independent and lives in
``tests/primitives/test_primitive_contract.py``. A credit rule returns one
pseudo-gradient per weight matrix, in the geometry's parameter order, and a
credit that is all zeros cannot train anything.
"""

from __future__ import annotations

import pytest
import torch

from computronium.primitives.registry import list_primitives
from tests.primitives._contract import axis_specs, make_case, reference

SPECS = axis_specs("credit")
IDS = [spec.id for spec in SPECS]


#: The learnable weight matrices of a geometry, in the ontology's own order.
def _weights(spec) -> list[str]:
    """The 2-D parameter names of the geometry a credit case carries."""
    geometry = make_case(spec, seed=0).extra["geometry"]
    return [
        name
        for name, param in geometry.params.items()
        if param.dim() == 2 and "weight" in name
    ]


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_step_returns_one_pseudo_gradient_per_weight_matrix(spec) -> None:
    """The credit list covers the geometry's weight matrices, in order and shape."""
    case = make_case(spec, seed=0)
    geometry = case.extra["geometry"]
    credits = reference(spec, case).weights

    names = _weights(spec)
    weights = [geometry.params[name] for name in names]
    assert len(credits) == len(weights), (spec.id, len(credits), len(weights))
    for credit, weight in zip(credits, weights, strict=True):
        assert credit.shape == weight.shape, (spec.id, credit.shape, weight.shape)


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_a_credit_is_not_all_zeros(spec) -> None:
    """Every law produces a nonzero credit somewhere."""
    credits = reference(spec, make_case(spec, seed=0)).weights
    assert any(torch.count_nonzero(credit) for credit in credits), spec.id


def test_the_registry_covers_every_credit() -> None:
    """The contract runs over the registry's credit rows, not a hand-kept list."""
    assert {spec.id for spec in SPECS} == {
        spec.id for spec in list_primitives("credit")
    }
