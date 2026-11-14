"""Case factory tests for Diffusion primitive."""

import torch

from computronium.primitives.state_dynamics.diffusion.cases import (
    Case,
    make_case,
)


def test_make_case_returns_case():
    """Test that make_case returns a Case instance."""
    case = make_case(device="cpu", seed=0)

    assert isinstance(case, Case)
    assert isinstance(case.state, torch.Tensor)
    assert isinstance(case.prediction, torch.Tensor)
    assert isinstance(case.multiplier, torch.Tensor)
    assert isinstance(case.config, dict)
    assert hasattr(case, "geometry")


def test_make_case_deterministic():
    """Test that make_case is deterministic with fixed seed."""
    case1 = make_case(device="cpu", seed=42)
    case2 = make_case(device="cpu", seed=42)

    torch.testing.assert_close(case1.state, case2.state)
    torch.testing.assert_close(case1.prediction, case2.prediction)
    torch.testing.assert_close(case1.multiplier, case2.multiplier)
    assert case1.config == case2.config


def test_make_case_different_seeds():
    """Test that different seeds produce different cases."""
    case1 = make_case(device="cpu", seed=0)
    case2 = make_case(device="cpu", seed=1)

    # At least one tensor should differ
    assert (
        not torch.allclose(case1.state, case2.state)
        or not torch.allclose(case1.prediction, case2.prediction)
        or not torch.allclose(case1.multiplier, case2.multiplier)
    )


def test_make_case_config_structure():
    """Test that case config has expected structure."""
    case = make_case(device="cpu", seed=0)

    assert "steps" in case.config
    assert "step_size" in case.config
    assert "target" in case.config
    assert "seed" in case.config
    assert case.config["steps"] > 0
    assert case.config["step_size"] > 0
    assert case.config["seed"] == 0
