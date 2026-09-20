"""Test cases for Spatial Lattice 3D Geometry primitive."""

import torch

from computronium.primitives.geometry.spatial_lattice_3d import make_case


def test_make_case_returns_case():
    """Test that make_case returns a Case with correct structure."""
    case = make_case(device="cpu", seed=0)

    assert hasattr(case, "state")
    assert hasattr(case, "config")
    assert hasattr(case, "geometry")

    assert isinstance(case.state, torch.Tensor)
    assert case.state.shape == (2, 16)  # batch=2, input_dim=16
    assert isinstance(case.config, dict)
    assert "seed" in case.config


def test_make_case_deterministic():
    """Test that make_case is deterministic with fixed seed."""
    case1 = make_case(device="cpu", seed=42)
    case2 = make_case(device="cpu", seed=42)

    assert torch.allclose(case1.state, case2.state)
    assert case1.config == case2.config
    # Geometry should have same parameters
    for p1, p2 in zip(case1.geometry.parameters(), case2.geometry.parameters()):
        assert torch.allclose(p1, p2)


def test_make_case_config_structure():
    """Test that case config has expected keys."""
    case = make_case(device="cpu", seed=0)

    expected_keys = {
        "input_dim",
        "output_dim",
        "lattice_dims",
        "hidden_dims",
        "connectivity_radius",
        "init_scale",
        "seed",
    }
    assert set(case.config.keys()) == expected_keys
