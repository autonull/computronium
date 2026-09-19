"""Reference implementation tests for Substrate-Coupled Plasticity primitive."""

import torch

from computronium.primitives.plasticity.substrate_coupled import (
    make_case,
    reference_step,
)


def test_reference_step_returns_psi():
    """Test that reference_step returns a plastic state dict."""
    case = make_case(device="cpu", seed=0)
    result = reference_step(case)

    assert isinstance(result, dict)
    # SubstrateCoupledPlasticity returns empty dict (ψ ≡ σ)
    assert result == {}


def test_reference_step_deterministic():
    """Test that reference_step is deterministic with fixed seed."""
    case = make_case(device="cpu", seed=42)
    result1 = reference_step(case)

    case2 = make_case(device="cpu", seed=42)
    result2 = reference_step(case2)

    assert result1 == result2


def test_reference_step_different_seeds():
    """Test that different seeds produce different results (still empty dict)."""
    case1 = make_case(device="cpu", seed=0)
    case2 = make_case(device="cpu", seed=1)

    result1 = reference_step(case1)
    result2 = reference_step(case2)

    # Both return empty dict, but the computation should be deterministic
    assert result1 == result2 == {}
