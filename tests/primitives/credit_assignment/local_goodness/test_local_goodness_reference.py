"""Tests for local_goodness reference implementation."""

import torch

from computronium.primitives.credit_assignment.local_goodness import (
    make_case,  # pyright: ignore[reportAttributeAccessIssue]
    reference_step,  # pyright: ignore[reportAttributeAccessIssue]
)


def test_reference_step_deterministic() -> None:
    # FF consumes the case's autograd graph, so determinism uses fresh cases.
    result1 = reference_step(make_case(seed=42))
    result2 = reference_step(make_case(seed=42))

    assert len(result1) == len(result2)
    for r1, r2 in zip(result1, result2, strict=True):
        assert torch.allclose(r1, r2)


def test_reference_step_different_seeds() -> None:
    case1 = make_case(seed=42)
    case2 = make_case(seed=43)

    result1 = reference_step(case1)
    result2 = reference_step(case2)

    assert len(result1) == len(result2)
    assert any(
        not torch.allclose(r1, r2) for r1, r2 in zip(result1, result2, strict=True)
    )


def test_reference_step_is_nonzero() -> None:
    """The FF autograd path must reach the parameters, not fall back to zeros."""
    result = reference_step(make_case(seed=0))

    assert all(float(grad.abs().sum()) > 0 for grad in result)


def test_reference_step_returns_list() -> None:
    case = make_case(seed=42)
    result = reference_step(case)

    assert isinstance(result, list)
    assert len(result) == 3  # Three weight matrices
    for r in result:
        assert isinstance(r, torch.Tensor)
        assert r.shape == (4, 4)
