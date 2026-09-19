"""Test cases for PEPITA algorithm."""

import torch

from computronium.algorithms.pepita import make_case
from computronium.ontology.geometry import FeedforwardGeometry


def test_make_case_returns_case():
    """Test that make_case returns a Case with expected fields."""
    case = make_case(device="cpu", seed=0)

    assert case is not None
    assert hasattr(case, "state")
    assert hasattr(case, "target")
    assert hasattr(case, "config")
    assert hasattr(case, "geometry")
    assert isinstance(case.geometry, FeedforwardGeometry)


def test_make_case_shapes():
    """Test that make_case returns tensors with expected shapes."""
    case = make_case(device="cpu", seed=0)

    assert case.state.shape == (2, 4)
    assert case.target.shape == (2,)


def test_make_case_config():
    """Test that make_case returns expected config keys."""
    case = make_case(device="cpu", seed=0)

    expected_keys = {
        "lr",
        "output_dim",
        "seed",
    }
    assert set(case.config.keys()) == expected_keys
    assert case.config["seed"] == 0


def test_make_case_deterministic():
    """Test that make_case is deterministic with fixed seed."""
    case1 = make_case(device="cpu", seed=42)
    case2 = make_case(device="cpu", seed=42)

    torch.testing.assert_close(case1.state, case2.state)
    torch.testing.assert_close(case1.target, case2.target)
    assert case1.config == case2.config

    geom1_params = list(case1.geometry.parameters())
    geom2_params = list(case2.geometry.parameters())
    for p1, p2 in zip(geom1_params, geom2_params):
        torch.testing.assert_close(p1, p2)


def test_make_case_different_seeds():
    """Test that different seeds produce different cases."""
    case1 = make_case(device="cpu", seed=0)
    case2 = make_case(device="cpu", seed=1)

    differ = False
    for a1, a2 in zip([case1.state, case1.target], [case2.state, case2.target]):
        if not torch.allclose(a1, a2):
            differ = True
            break
    assert differ
