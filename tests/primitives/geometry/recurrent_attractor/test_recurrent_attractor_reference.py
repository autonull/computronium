"""Reference implementation tests for Recurrent Attractor primitive."""

import torch

from computronium.primitives.geometry.recurrent_attractor import (
    make_case,
    reference_forward,
)


def test_reference_forward_returns_tensor():
    """Test that reference_forward returns a tensor."""
    case = make_case(device="cpu", seed=0)
    result = reference_forward(case)

    assert result is not None
    assert isinstance(result, torch.Tensor)
    assert result.shape == (2, 4)  # batch=2, output_dim=4


def test_reference_forward_deterministic():
    """Test that reference_forward is deterministic with fixed seed."""
    case = make_case(device="cpu", seed=42)
    result1 = reference_forward(case)

    case2 = make_case(device="cpu", seed=42)
    result2 = reference_forward(case2)

    torch.testing.assert_close(result1, result2)


def test_reference_forward_different_seeds():
    """Test that different seeds produce different results."""
    case1 = make_case(device="cpu", seed=0)
    case2 = make_case(device="cpu", seed=1)

    result1 = reference_forward(case1)
    result2 = reference_forward(case2)

    # Results should differ
    assert not torch.allclose(result1, result2)