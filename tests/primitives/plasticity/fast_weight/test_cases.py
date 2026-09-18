"""Test case validation for Fast Weight Plasticity primitive."""

import torch

from computronium.primitives.plasticity.fast_weight import make_case


def test_make_case_returns_case():
    """Test that make_case returns a Case with all required fields."""
    case = make_case(device="cpu", seed=0)

    assert case is not None
    assert hasattr(case, "fast_weights")
    assert hasattr(case, "pre_activity")
    assert hasattr(case, "post_activity")
    assert hasattr(case, "config")
    assert isinstance(case.fast_weights, torch.Tensor)
    assert isinstance(case.config, dict)


def test_make_case_shapes():
    """Test that tensors have expected shapes."""
    case = make_case(device="cpu", seed=0)

    assert case.fast_weights.shape == (2, 16)  # batch=2, fast_weight_dim=16
    assert case.pre_activity.shape == (2, 8)  # batch=2, input_dim=8
    assert case.post_activity.shape == (2, 4)  # batch=2, output_dim=4


def test_make_case_config_keys():
    """Test that config has all required keys."""
    case = make_case(device="cpu", seed=0)

    required_keys = [
        "fast_weight_dim",
        "decay",
        "learning_rate",
        "outer_product_scale",
        "step",
        "seed",
    ]
    for key in required_keys:
        assert key in case.config


def test_make_case_deterministic():
    """Test that make_case is deterministic with fixed seed."""
    case1 = make_case(device="cpu", seed=42)
    case2 = make_case(device="cpu", seed=42)

    torch.testing.assert_close(case1.fast_weights, case2.fast_weights)
    torch.testing.assert_close(case1.pre_activity, case2.pre_activity)
    torch.testing.assert_close(case1.post_activity, case2.post_activity)
    assert case1.config == case2.config


def test_make_case_different_seeds():
    """Test that different seeds produce different states."""
    case1 = make_case(device="cpu", seed=0)
    case2 = make_case(device="cpu", seed=1)

    assert not torch.allclose(case1.pre_activity, case2.pre_activity)
    assert not torch.allclose(case1.post_activity, case2.post_activity)
