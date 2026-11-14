"""Reference implementation tests for Spike Integration primitive."""

import torch

from computronium.primitives.state_dynamics.spike_integration import (
    make_case,
    reference_step,
)


def test_reference_step_returns_state():
    """Test that reference_step returns a CompositeState."""
    case = make_case(device="cpu", seed=0)
    result = reference_step(case)

    assert result is not None
    assert hasattr(result, "activity")
    assert hasattr(result, "plastic")
    assert hasattr(result, "substrate")
    assert "x" in result.activity


def test_reference_step_deterministic():
    """Test that reference_step is deterministic with fixed seed."""
    case = make_case(device="cpu", seed=42)
    result1 = reference_step(case)

    case2 = make_case(device="cpu", seed=42)
    result2 = reference_step(case2)

    # Compare activations
    act1 = result1.activations
    act2 = result2.activations

    assert act1 is not None and act2 is not None
    for a1, a2 in zip(act1, act2):
        torch.testing.assert_close(a1, a2)


def test_reference_step_different_seeds():
    """Test that different seeds produce different results."""
    case1 = make_case(device="cpu", seed=0)
    case2 = make_case(device="cpu", seed=1)

    result1 = reference_step(case1)
    result2 = reference_step(case2)

    act1 = result1.activations
    act2 = result2.activations

    # At least one activation should differ
    differ = False
    for a1, a2 in zip(act1, act2):
        if not torch.allclose(a1, a2):
            differ = True
            break
    assert differ
