"""Reference implementation tests for Sparse Substrate primitive."""

from computronium.primitives.substrate.sparse import (
    make_case,
    reference_make_substrate,
)
from computronium.ontology.substrate._substrate import SparseSubstrate


def test_reference_make_substrate_returns_substrate():
    """Test that reference_make_substrate returns a SparseSubstrate instance."""
    case = make_case(device="cpu", seed=0)
    substrate = reference_make_substrate(case.spec)

    assert substrate is not None
    assert isinstance(substrate, SparseSubstrate)


def test_reference_make_substrate_deterministic():
    """Test that reference_make_substrate is deterministic with fixed spec."""
    case1 = make_case(device="cpu", seed=42)
    case2 = make_case(device="cpu", seed=42)

    substrate1 = reference_make_substrate(case1.spec)
    substrate2 = reference_make_substrate(case2.spec)

    assert isinstance(substrate1, SparseSubstrate)
    assert isinstance(substrate2, SparseSubstrate)


def test_reference_make_substrate_high_sparsity():
    """Test that reference_make_substrate handles high sparsity spec."""
    from computronium.primitives.substrate.sparse import make_case_high_sparsity

    case = make_case_high_sparsity(device="cpu", seed=0, sparsity=0.9)
    substrate = reference_make_substrate(case.spec)

    assert substrate is not None
    assert isinstance(substrate, SparseSubstrate)
    assert substrate.config.sparsity == 0.9
