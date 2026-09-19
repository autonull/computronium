"""Test case validation for Feedforward DAG Geometry primitive."""

import torch

from computronium.primitives.geometry.feedforward_dag import make_case


def test_make_case_returns_case():
    """Test that make_case returns a Case with all required fields."""
    case = make_case(device="cpu", seed=0)

    assert case is not None
    assert hasattr(case, "state")
    assert hasattr(case, "config")
    assert isinstance(case.state, torch.Tensor)
    assert isinstance(case.config, dict)


def test_make_case_state_shape():
    """Test that state has expected shape."""
    case = make_case(device="cpu", seed=0)

    assert case.state.shape == (2, 8)  # batch=2, input_dim=8


def test_make_case_config_keys():
    """Test that config has all required keys."""
    case = make_case(device="cpu", seed=0)

    required_keys = [
        "input_dim",
        "output_dim",
        "hidden_dims",
        "init_scale",
        "seed",
    ]
    for key in required_keys:
        assert key in case.config


def test_make_case_deterministic():
    """Test that make_case is deterministic with fixed seed."""
    case1 = make_case(device="cpu", seed=42)
    case2 = make_case(device="cpu", seed=42)

    torch.testing.assert_close(case1.state, case2.state)
    assert case1.config == case2.config


def test_make_case_different_seeds():
    """Test that different seeds produce different states."""
    case1 = make_case(device="cpu", seed=0)
    case2 = make_case(device="cpu", seed=1)

    assert not torch.allclose(case1.state, case2.state)
