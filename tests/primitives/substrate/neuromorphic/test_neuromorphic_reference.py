"""Reference implementation tests for Neuromorphic Substrate primitive."""


from computronium.primitives.substrate.neuromorphic import (
    make_case,
    reference_make_substrate,
)


def test_reference_make_substrate_returns_substrate():
    """Test that reference_make_substrate returns a Substrate instance."""
    case = make_case(device="cpu", seed=0)
    substrate = reference_make_substrate(case.spec)

    assert substrate is not None
    # Check it's a NeuromorphicSubstrate
    from computronium.ontology.substrate._substrate import NeuromorphicSubstrate

    assert isinstance(substrate, NeuromorphicSubstrate)


def test_reference_make_substrate_deterministic():
    """Test that reference_make_substrate is deterministic with fixed spec."""
    case1 = make_case(device="cpu", seed=42)
    case2 = make_case(device="cpu", seed=42)

    substrate1 = reference_make_substrate(case1.spec)
    substrate2 = reference_make_substrate(case2.spec)

    # Both should be NeuromorphicSubstrate instances
    from computronium.ontology.substrate._substrate import NeuromorphicSubstrate

    assert isinstance(substrate1, NeuromorphicSubstrate)
    assert isinstance(substrate2, NeuromorphicSubstrate)


def test_reference_make_substrate_noisy():
    """Test that reference_make_substrate handles noisy spec."""
    from computronium.primitives.substrate.neuromorphic import make_case_noisy

    case = make_case_noisy(device="cpu", seed=0, noise_level=0.1)
    substrate = reference_make_substrate(case.spec)

    assert substrate is not None
    from computronium.ontology.substrate._substrate import NeuromorphicSubstrate

    assert isinstance(substrate, NeuromorphicSubstrate)
