"""Tests for Thermodynamic Contrast case generation."""

import pytest
import torch

from computronium.primitives.credit_assignment.thermodynamic_contrast import make_case


def test_make_case_deterministic():
    """make_case should be deterministic with fixed seed."""
    case1 = make_case(seed=42)
    case2 = make_case(seed=42)

    assert torch.allclose(case1.state, case2.state)
    assert torch.allclose(case1.prediction, case2.prediction)
    assert torch.allclose(case1.multiplier, case2.multiplier)
    assert torch.allclose(case1.free_activations[0], case2.free_activations[0])
    assert torch.allclose(case1.nudged_activations[0], case2.nudged_activations[0])
    assert torch.allclose(case1.weights[0], case2.weights[0])
    assert case1.config == case2.config


def test_make_case_different_seeds():
    """make_case should produce different outputs with different seeds."""
    case1 = make_case(seed=0)
    case2 = make_case(seed=1)

    # At least one tensor should differ
    assert not torch.allclose(case1.state, case2.state)


def test_make_case_config_structure():
    """make_case should return expected config keys."""
    case = make_case()
    assert "beta" in case.config
    assert "credit_norm" in case.config
    assert "target" in case.config
    assert "seed" in case.config
    assert case.config["seed"] == 0


def test_make_case_tensors_on_device():
    """make_case should place tensors on requested device."""
    case = make_case(device="cpu")
    assert case.state.device.type == "cpu"
    assert case.free_activations[0].device.type == "cpu"
