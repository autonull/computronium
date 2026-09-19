"""Reference implementation tests for Fast Weight Plasticity primitive."""

import torch

from computronium.primitives.plasticity.fast_weight import (
    make_case,
    reference_step,
)


def test_reference_step_returns_dict():
    """Test that reference_step returns a dict with fast_weights."""
    case = make_case(device="cpu", seed=0)
    result = reference_step(case)

    assert result is not None
    assert isinstance(result, dict)
    assert "fast_weights" in result
    assert isinstance(result["fast_weights"], torch.Tensor)


def test_reference_step_shape():
    """Test that fast_weights has correct shape."""
    case = make_case(device="cpu", seed=0)
    result = reference_step(case)

    assert result["fast_weights"].shape == (2, 16)  # batch=2, fast_weight_dim=16


def test_reference_step_deterministic():
    """Test that reference_step is deterministic with fixed seed."""
    case = make_case(device="cpu", seed=42)
    result1 = reference_step(case)

    case2 = make_case(device="cpu", seed=42)
    result2 = reference_step(case2)

    torch.testing.assert_close(result1["fast_weights"], result2["fast_weights"])


def test_reference_step_different_seeds():
    """Test that different seeds produce different results."""
    case1 = make_case(device="cpu", seed=0)
    case2 = make_case(device="cpu", seed=1)

    result1 = reference_step(case1)
    result2 = reference_step(case2)

    # Results should differ
    assert not torch.allclose(result1["fast_weights"], result2["fast_weights"])


def test_reference_step_fast_weights_change():
    """Test that fast weights are updated (not zero)."""
    case = make_case(device="cpu", seed=0)
    result = reference_step(case)

    # Fast weights should have been updated from zeros
    assert not torch.allclose(
        result["fast_weights"], torch.zeros_like(result["fast_weights"])
    )
