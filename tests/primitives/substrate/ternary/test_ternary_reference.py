"""Reference implementation tests for Ternary Substrate primitive."""

from computronium.ontology.substrate._substrate import TernarySubstrate
from computronium.primitives.substrate.ternary import (
    make_case,
    reference_make_substrate,
)


def test_reference_make_substrate_returns_substrate():
    """Test that reference_make_substrate returns a TernarySubstrate instance."""
    case = make_case(device="cpu", seed=0)
    substrate = reference_make_substrate(case.spec)

    assert substrate is not None
    assert isinstance(substrate, TernarySubstrate)


def test_reference_make_substrate_deterministic():
    """Test that reference_make_substrate is deterministic with fixed spec."""
    case1 = make_case(device="cpu", seed=42)
    case2 = make_case(device="cpu", seed=42)

    substrate1 = reference_make_substrate(case1.spec)
    substrate2 = reference_make_substrate(case2.spec)

    assert isinstance(substrate1, TernarySubstrate)
    assert isinstance(substrate2, TernarySubstrate)
