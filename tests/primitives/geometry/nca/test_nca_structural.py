"""Structural equivalence tests for NCA Geometry primitive.

Tests factory determinism for structural primitives.
"""

import torch

from computronium.ontology.geometry import GeometryConfig, NcaGeometry


def test_nca_geometry_factory_deterministic():
    """Two NcaGeometry instances with same config and seed have bitwise-equal parameters."""
    config = GeometryConfig.nca(
        channels=8,
        hidden=8,
        grid_hw=(8, 8),
        delta_scale=0.5,
        mask_prob=0.5,
        init_scale=0.1,
    )

    # Create first geometry with fixed seed
    torch.manual_seed(42)
    geom1 = NcaGeometry(config)

    # Create second geometry with same seed
    torch.manual_seed(42)
    geom2 = NcaGeometry(config)

    # Parameters should be bitwise-equal
    for (name1, param1), (name2, param2) in zip(
        geom1.named_parameters(), geom2.named_parameters()
    ):
        assert name1 == name2
        torch.testing.assert_close(param1, param2, rtol=0, atol=0)


def test_nca_geometry_different_seeds_produce_different_params():
    """Different seeds produce different parameters."""
    config = GeometryConfig.nca(
        channels=8,
        hidden=8,
        grid_hw=(8, 8),
        delta_scale=0.5,
        mask_prob=0.5,
        init_scale=0.1,
    )

    torch.manual_seed(0)
    geom1 = NcaGeometry(config)

    torch.manual_seed(1)
    geom2 = NcaGeometry(config)

    # At least one parameter should differ
    params_differ = False
    for param1, param2 in zip(geom1.parameters(), geom2.parameters()):
        if not torch.allclose(param1, param2, rtol=0, atol=0):
            params_differ = True
            break

    assert params_differ, "Different seeds should produce different parameters"
