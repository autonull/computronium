"""Structural equivalence tests for Sparse Substrate primitive.

Tests factory determinism and spec round-trip for structural primitives.
"""

from computronium.ontology.substrate import SparseSubstrate, SubstrateConfig
from computronium.ontology.substrate.spec import SubstrateSpec, make_substrate


def test_sparse_substrate_factory_deterministic():
    """Two substrate instances with same spec have identical config."""
    config = SubstrateConfig.sparse(device="cpu", sparsity=0.5)
    spec = SubstrateSpec.from_config(config)

    substrate1 = make_substrate(spec)
    substrate2 = make_substrate(spec)

    # Both should be same type
    assert type(substrate1) is type(substrate2)
    assert isinstance(substrate1, SparseSubstrate)
    assert isinstance(substrate2, SparseSubstrate)

    # Configs should be identical
    assert substrate1.config == substrate2.config


def test_sparse_substrate_spec_round_trip():
    """SubstrateSpec round-trips losslessly through SubstrateConfig."""
    config = SubstrateConfig.sparse(device="cpu", sparsity=0.5)

    # Convert config -> spec -> config
    spec = SubstrateSpec.from_config(config)
    roundtrip_config = spec.to_config()

    # Round-trip config should match original
    assert roundtrip_config == config
