"""Structural equivalence tests for Neuromorphic Substrate primitive.

Tests factory determinism and spec round-trip for structural primitives.
"""

from computronium.ontology.substrate import NeuromorphicSubstrate, SubstrateConfig
from computronium.ontology.substrate.spec import SubstrateSpec, make_substrate


def test_neuromorphic_substrate_factory_deterministic():
    """Two substrate instances with same spec have identical config."""
    config = SubstrateConfig.neuromorphic(device="cpu")
    spec = SubstrateSpec.from_config(config)

    substrate1 = make_substrate(spec)
    substrate2 = make_substrate(spec)

    # Both should be same type
    assert type(substrate1) is type(substrate2)
    assert isinstance(substrate1, NeuromorphicSubstrate)
    assert isinstance(substrate2, NeuromorphicSubstrate)

    # Configs should be identical
    assert substrate1.config == substrate2.config


def test_neuromorphic_substrate_spec_round_trip():
    """SubstrateSpec round-trips losslessly through SubstrateConfig (precision may change)."""
    config = SubstrateConfig.neuromorphic(device="cpu")

    # Convert config -> spec -> config
    spec = SubstrateSpec.from_config(config)
    roundtrip_config = spec.to_config()

    # Round-trip config should match original except for precision (which is normalized)
    # The spec normalizes precision to float32, so we check other fields
    assert roundtrip_config.substrate_type == config.substrate_type
    assert roundtrip_config.device == config.device
    assert roundtrip_config.weight_bounds == config.weight_bounds
    assert roundtrip_config.sparsity == config.sparsity
    assert roundtrip_config.noise_level == config.noise_level
