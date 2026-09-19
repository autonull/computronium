"""Case factory tests for Fabric PC Geometry primitive."""

import torch

from computronium.primitives.geometry.fabric_pc.cases import (
    Case,
    make_case,
)


def test_make_case_returns_case():
    """Test that make_case returns a Case instance."""
    case = make_case(device="cpu", seed=0)

    assert isinstance(case, Case)
    assert isinstance(case.state, torch.Tensor)
    assert isinstance(case.config, dict)
    assert hasattr(case, "geometry")


def test_make_case_deterministic():
    """Test that make_case is deterministic with fixed seed."""
    case1 = make_case(device="cpu", seed=42)
    case2 = make_case(device="cpu", seed=42)

    torch.testing.assert_close(case1.state, case2.state)
    assert case1.config == case2.config


def test_make_case_different_seeds():
    """Test that different seeds produce different cases."""
    case1 = make_case(device="cpu", seed=0)
    case2 = make_case(device="cpu", seed=1)

    # State should differ
    assert not torch.allclose(case1.state, case2.state)


def test_make_case_config_structure():
    """Test that case config has expected structure."""
    case = make_case(device="cpu", seed=0)

    assert "input_dim" in case.config
    assert "output_dim" in case.config
    assert "edge_index" in case.config
    assert "hidden_dims" in case.config
    assert "init_scale" in case.config
    assert "seed" in case.config
    assert case.config["seed"] == 0
