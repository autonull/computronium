"""Structural equivalence tests for Noisy Substrate primitive.

Tests factory determinism for structural primitives.
"""

import torch

from computronium.ontology.substrate._substrate import (
    NoisySubstrate,
    SubstrateConfig,
    SubstrateType,
)


def test_noisy_substrate_factory_deterministic():
    """Two NoisySubstrate instances with same config have identical config."""
    config = SubstrateConfig(
        substrate_type=SubstrateType.DIGITAL,
        precision="float32",
        noise_level=0.1,
        weight_bounds=None,
        sparsity=0.0,
        device="cpu",
    )

    substrate1 = NoisySubstrate(config)
    substrate2 = NoisySubstrate(config)

    # Both should be same type
    assert type(substrate1) is type(substrate2)
    assert isinstance(substrate1, NoisySubstrate)
    assert isinstance(substrate2, NoisySubstrate)

    # Configs should be identical
    assert substrate1.config == substrate2.config


def test_noisy_substrate_deterministic_output():
    """Two NoisySubstrate instances with same seed produce bitwise-equal noise."""
    config = SubstrateConfig(
        substrate_type=SubstrateType.DIGITAL,
        precision="float32",
        noise_level=0.1,
        weight_bounds=None,
        sparsity=0.0,
        device="cpu",
    )

    # Create two substrates with same config
    substrate1 = NoisySubstrate(config)
    substrate2 = NoisySubstrate(config)

    # Test with same input and RNG state
    x = torch.randn(4, 8)

    torch.manual_seed(42)
    out1 = substrate1.inject_state_noise(x.clone())

    torch.manual_seed(42)
    out2 = substrate2.inject_state_noise(x.clone())

    torch.testing.assert_close(out1, out2, rtol=0, atol=0)
