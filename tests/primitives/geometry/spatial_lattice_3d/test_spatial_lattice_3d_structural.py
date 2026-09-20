"""Structural equivalence tests for Spatial Lattice 3D Geometry primitive.

Tests factory determinism for structural primitives.
"""

import torch

from computronium.ontology.geometry import GeometryConfig, SpatialLattice3DGeometry


def test_spatial_lattice_3d_geometry_factory_deterministic():
    """Two SpatialLattice3DGeometry instances with same config and seed have bitwise-equal parameters."""
    config = GeometryConfig.spatial_lattice(
        input_dim=8,
        output_dim=4,
        lattice_dims=(4, 4, 4),
        connectivity_radius=1,
        init_scale=0.1,
    )

    # Create first geometry with fixed seed
    torch.manual_seed(42)
    geom1 = SpatialLattice3DGeometry(config)

    # Create second geometry with same seed
    torch.manual_seed(42)
    geom2 = SpatialLattice3DGeometry(config)

    # Parameters should be bitwise-equal
    for (name1, param1), (name2, param2) in zip(
        geom1.named_parameters(), geom2.named_parameters()
    ):
        assert name1 == name2
        torch.testing.assert_close(param1, param2, rtol=0, atol=0)


def test_spatial_lattice_3d_geometry_different_seeds_produce_different_params():
    """Different seeds produce different parameters."""
    config = GeometryConfig.spatial_lattice(
        input_dim=8,
        output_dim=4,
        lattice_dims=(4, 4, 4),
        connectivity_radius=1,
        init_scale=0.1,
    )

    torch.manual_seed(0)
    geom1 = SpatialLattice3DGeometry(config)

    torch.manual_seed(1)
    geom2 = SpatialLattice3DGeometry(config)

    # At least one parameter should differ
    params_differ = False
    for param1, param2 in zip(geom1.parameters(), geom2.parameters()):
        if not torch.allclose(param1, param2, rtol=0, atol=0):
            params_differ = True
            break

    assert params_differ, "Different seeds should produce different parameters"
