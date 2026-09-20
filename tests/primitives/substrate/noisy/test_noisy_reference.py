"""Reference implementation tests for Noisy Substrate primitive."""

from computronium.ontology.substrate._substrate import NoisySubstrate
from computronium.primitives.substrate.noisy import (
    make_case,
    reference_make_substrate,
)


def test_reference_make_substrate_returns_substrate():
    """Test that reference_make_substrate returns a NoisySubstrate instance."""
    case = make_case(device="cpu", seed=0)
    substrate = reference_make_substrate(case.spec)

    assert substrate is not None
    assert isinstance(substrate, NoisySubstrate)


def test_reference_make_substrate_deterministic():
    """Test that reference_make_substrate is deterministic with fixed spec."""
    case1 = make_case(device="cpu", seed=42)
    case2 = make_case(device="cpu", seed=42)

    substrate1 = reference_make_substrate(case1.spec)
    substrate2 = reference_make_substrate(case2.spec)

    assert isinstance(substrate1, NoisySubstrate)
    assert isinstance(substrate2, NoisySubstrate)


def test_reference_make_substrate_high_noise():
    """Test that reference_make_substrate handles high noise spec."""
    from computronium.primitives.substrate.noisy import make_case_high_noise

    case = make_case_high_noise(device="cpu", seed=0, noise_level=0.5)
    substrate = reference_make_substrate(case.spec)

    assert substrate is not None
    assert isinstance(substrate, NoisySubstrate)
