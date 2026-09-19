"""Case factory tests for Substrate-Coupled Plasticity primitive."""

import torch

from computronium.primitives.plasticity.substrate_coupled.cases import (
    Case,
    make_case,
)


def test_make_case_returns_case():
    """Test that make_case returns a Case instance."""
    case = make_case(device="cpu", seed=0)

    assert isinstance(case, Case)
    assert isinstance(case.pre_activity, torch.Tensor)
    assert isinstance(case.post_activity, torch.Tensor)
    assert isinstance(case.config, dict)


def test_make_case_deterministic():
    """Test that make_case is deterministic with fixed seed."""
    case1 = make_case(device="cpu", seed=42)
    case2 = make_case(device="cpu", seed=42)

    torch.testing.assert_close(case1.pre_activity, case2.pre_activity)
    torch.testing.assert_close(case1.post_activity, case2.post_activity)
    assert case1.config == case2.config


def test_make_case_different_seeds():
    """Test that different seeds produce different cases."""
    case1 = make_case(device="cpu", seed=0)
    case2 = make_case(device="cpu", seed=1)

    # At least one tensor should differ
    assert not torch.allclose(
        case1.pre_activity, case2.pre_activity
    ) or not torch.allclose(case1.post_activity, case2.post_activity)


def test_make_case_config_structure():
    """Test that case config has expected structure."""
    case = make_case(device="cpu", seed=0)

    assert "seed" in case.config
    assert case.config["seed"] == 0
