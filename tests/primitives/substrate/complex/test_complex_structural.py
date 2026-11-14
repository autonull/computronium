"""Structural equivalence tests for Complex Substrate primitive.

Tests factory determinism for structural primitives.
"""

from computronium.ontology.substrate._substrate import ComplexSubstrate, SubstrateConfig
from computronium.ontology.substrate.spec import SubstrateSpec


def test_complex_substrate_factory_deterministic():
    """Two ComplexSubstrate instances with same config have identical config."""
    config = SubstrateConfig.complex(
        noise_level=0.0,
        weight_bounds=None,
        sparsity=0.0,
        device="cpu",
    )

    substrate1 = ComplexSubstrate(config)
    substrate2 = ComplexSubstrate(config)

    # Both should be same type
    assert type(substrate1) is type(substrate2)
    assert isinstance(substrate1, ComplexSubstrate)
    assert isinstance(substrate2, ComplexSubstrate)

    # Configs should be identical
    assert substrate1.config == substrate2.config


def test_complex_substrate_spec_round_trip():
    """Complex SubstrateSpec round-trips losslessly through SubstrateConfig."""
    config = SubstrateConfig.complex(
        noise_level=0.0,
        weight_bounds=None,
        sparsity=0.0,
        device="cpu",
    )

    # Convert config -> spec -> config
    spec = SubstrateSpec.from_config(config)
    roundtrip_config = spec.to_config()

    # Round-trip config should match original
    assert roundtrip_config == config
