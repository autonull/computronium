"""Reference implementation tests for Spectral Constrained primitive."""

import torch

from computronium.primitives.parameter_update.spectral_constrained import (
    make_case,
    reference_step,
)


def test_reference_step_returns_updated_params():
    """Test that reference_step returns a dict of updated parameters."""
    case = make_case(device="cpu", seed=0)
    result = reference_step(case)

    assert isinstance(result, dict)
    assert len(result) > 0
    # Check that all values are tensors
    for v in result.values():
        assert isinstance(v, torch.Tensor)


def test_reference_step_deterministic():
    """Test that reference_step is deterministic with fixed seed."""
    case = make_case(device="cpu", seed=42)
    result1 = reference_step(case)

    case2 = make_case(device="cpu", seed=42)
    result2 = reference_step(case2)

    assert len(result1) == len(result2)
    for k in result1:
        assert k in result2
        torch.testing.assert_close(result1[k], result2[k])


def test_reference_step_different_seeds():
    """Test that different seeds produce different results."""
    case1 = make_case(device="cpu", seed=0)
    case2 = make_case(device="cpu", seed=1)

    result1 = reference_step(case1)
    result2 = reference_step(case2)

    assert len(result1) == len(result2)
    for k in result1:
        assert k in result2
        assert not torch.allclose(result1[k], result2[k])
