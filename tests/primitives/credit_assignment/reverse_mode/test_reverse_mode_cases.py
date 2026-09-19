"""Case factory tests for Reverse Mode primitive."""

import torch

from computronium.primitives.credit_assignment.reverse_mode.cases import (
    Case,
    make_case,
)


def test_make_case_returns_case():
    """Test that make_case returns a Case instance."""
    case = make_case(device="cpu", seed=0)

    assert isinstance(case, Case)
    assert isinstance(case.state, torch.Tensor)
    assert isinstance(case.activations, list)
    assert isinstance(case.nudged_activations, list)
    assert isinstance(case.config, dict)
    assert hasattr(case, "geometry")


def test_make_case_deterministic():
    """Test that make_case is deterministic with fixed seed."""
    case1 = make_case(device="cpu", seed=42)
    case2 = make_case(device="cpu", seed=42)

    torch.testing.assert_close(case1.state, case2.state)
    for a1, a2 in zip(case1.activations, case2.activations):
        torch.testing.assert_close(a1, a2)
    for n1, n2 in zip(case1.nudged_activations, case2.nudged_activations):
        torch.testing.assert_close(n1, n2)
    assert case1.config == case2.config


def test_make_case_different_seeds():
    """Test that different seeds produce different cases."""
    case1 = make_case(device="cpu", seed=0)
    case2 = make_case(device="cpu", seed=1)

    # At least one tensor should differ
    differ = False
    if not torch.allclose(case1.state, case2.state):
        differ = True
    for a1, a2 in zip(case1.activations, case2.activations):
        if not torch.allclose(a1, a2):
            differ = True
            break
    for n1, n2 in zip(case1.nudged_activations, case2.nudged_activations):
        if not torch.allclose(n1, n2):
            differ = True
            break
    assert differ


def test_make_case_config_structure():
    """Test that case config has expected structure."""
    case = make_case(device="cpu", seed=0)

    assert "beta" in case.config
    assert "seed" in case.config
    assert case.config["seed"] == 0
