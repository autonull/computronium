"""Reference implementation tests for Routing Plasticity primitive."""

import torch

from computronium.primitives.plasticity.routing import (
    make_case,
    reference_step,
)


def test_reference_step_returns_dict():
    """Test that reference_step returns a dict with gate_logits and active_routes."""
    case = make_case(device="cpu", seed=0)
    result = reference_step(case)

    assert result is not None
    assert isinstance(result, dict)
    assert "gate_logits" in result
    assert "active_routes" in result
    assert isinstance(result["gate_logits"], torch.Tensor)
    assert isinstance(result["active_routes"], torch.Tensor)


def test_reference_step_shape():
    """Test that tensors have correct shape."""
    case = make_case(device="cpu", seed=0)
    result = reference_step(case)

    assert result["gate_logits"].shape == (2, 8)  # batch=2, gate_dim=8
    assert result["active_routes"].shape == (2, 8)


def test_reference_step_deterministic():
    """Test that reference_step is deterministic with fixed seed."""
    case = make_case(device="cpu", seed=42)
    result1 = reference_step(case)

    case2 = make_case(device="cpu", seed=42)
    result2 = reference_step(case2)

    torch.testing.assert_close(result1["gate_logits"], result2["gate_logits"])
    torch.testing.assert_close(result1["active_routes"], result2["active_routes"])


def test_reference_step_different_seeds():
    """Test that different seeds produce different results."""
    case1 = make_case(device="cpu", seed=0)
    case2 = make_case(device="cpu", seed=1)

    result1 = reference_step(case1)
    result2 = reference_step(case2)

    # Results should differ
    assert not torch.allclose(result1["gate_logits"], result2["gate_logits"])


def test_reference_step_gate_logits_change():
    """Test that gate logits are updated (not zero)."""
    case = make_case(device="cpu", seed=0)
    result = reference_step(case)

    # Gate logits should have been updated from zeros
    assert not torch.allclose(
        result["gate_logits"], torch.zeros_like(result["gate_logits"])
    )


def test_reference_step_active_routes_non_negative():
    """Test that active routes are non-negative (sigmoid/Gumbel-Softmax output)."""
    case = make_case(device="cpu", seed=0)
    result = reference_step(case)

    assert (result["active_routes"] >= 0).all()
    assert (result["active_routes"] <= 1).all()
