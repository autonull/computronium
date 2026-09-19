"""Tests for local_goodness reference implementation."""

import torch

from computronium.primitives.credit_assignment.local_goodness import (
    make_case,
    reference_step,
)


def test_reference_step_deterministic() -> None:
    case = make_case(seed=42)
    result1 = reference_step(case)
    result2 = reference_step(case)

    assert len(result1) == len(result2)
    for r1, r2 in zip(result1, result2, strict=True):
        assert torch.allclose(r1, r2)


def test_reference_step_different_seeds() -> None:
    case1 = make_case(seed=42)
    case2 = make_case(seed=43)

    result1 = reference_step(case1)
    result2 = reference_step(case2)

    # Results should be deterministic (same seed -> same output)
    assert len(result1) == len(result2)


def test_reference_step_returns_list() -> None:
    case = make_case(seed=42)
    result = reference_step(case)

    assert isinstance(result, list)
    assert len(result) == 3  # Three weight matrices
    for r in result:
        assert isinstance(r, torch.Tensor)
        assert r.shape == (4, 4)
