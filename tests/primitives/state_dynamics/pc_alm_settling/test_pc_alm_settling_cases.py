"""Test cases for PC-ALM settling primitive."""

import torch

from computronium.primitives.state_dynamics.pc_alm_settling import make_case


def test_make_case_returns_case():
    """Test that make_case returns a Case with expected fields."""
    case = make_case(device="cpu", seed=0)

    assert case is not None
    assert hasattr(case, "state")
    assert hasattr(case, "prediction")
    assert hasattr(case, "multiplier")
    assert hasattr(case, "config")


def test_make_case_shapes():
    """Test that make_case returns tensors with expected shapes."""
    case = make_case(device="cpu", seed=0)

    assert case.state.shape == (2, 4)
    assert case.prediction.shape == (2, 4)
    assert case.multiplier.shape == (2, 4)


def test_make_case_config():
    """Test that make_case returns expected config keys."""
    case = make_case(device="cpu", seed=0)

    expected_keys = {
        "steps",
        "step_size",
        "rho",
        "beta",
        "prospective_leak",
        "tol",
        "target",
        "seed",
    }
    assert set(case.config.keys()) == expected_keys
    assert case.config["steps"] == 3
    assert case.config["target"] is None
    assert case.config["seed"] == 0


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

    differ = False
    for a1, a2 in zip(
        [case1.state, case1.prediction, case1.multiplier],
        [case2.state, case2.prediction, case2.multiplier],
    ):
        if not torch.allclose(a1, a2):
            differ = True
            break
    assert differ
