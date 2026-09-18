"""Test case validation for Routing Plasticity primitive."""

import torch

from computronium.primitives.plasticity.routing import make_case


def test_make_case_returns_case():
    """Test that make_case returns a Case with all required fields."""
    case = make_case(device="cpu", seed=0)

    assert case is not None
    assert hasattr(case, "gate_logits")
    assert hasattr(case, "active_routes")
    assert hasattr(case, "pre_activity")
    assert hasattr(case, "config")
    assert isinstance(case.gate_logits, torch.Tensor)
    assert isinstance(case.config, dict)


def test_make_case_shapes():
    """Test that tensors have expected shapes."""
    case = make_case(device="cpu", seed=0)

    assert case.gate_logits.shape == (2, 8)  # batch=2, gate_dim=8
    assert case.active_routes.shape == (2, 8)
    assert case.pre_activity.shape == (2, 16)  # batch=2, input_dim=16


def test_make_case_config_keys():
    """Test that config has all required keys."""
    case = make_case(device="cpu", seed=0)

    required_keys = [
        "gate_dim",
        "temperature",
        "top_k",
        "decay",
        "learning_rate",
        "seed",
    ]
    for key in required_keys:
        assert key in case.config


def test_make_case_deterministic():
    """Test that make_case is deterministic with fixed seed."""
    case1 = make_case(device="cpu", seed=42)
    case2 = make_case(device="cpu", seed=42)

    torch.testing.assert_close(case1.gate_logits, case2.gate_logits)
    torch.testing.assert_close(case1.active_routes, case2.active_routes)
    torch.testing.assert_close(case1.pre_activity, case2.pre_activity)
    assert case1.config == case2.config


def test_make_case_different_seeds():
    """Test that different seeds produce different states."""
    case1 = make_case(device="cpu", seed=0)
    case2 = make_case(device="cpu", seed=1)

    assert not torch.allclose(case1.pre_activity, case2.pre_activity)
