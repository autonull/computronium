"""Tests for Elastic Consolidation Update case generation."""

import pytest
import torch

from computronium.primitives.parameter_update.elastic_consolidation import make_case


def test_make_case_deterministic():
    """make_case should be deterministic with fixed seed."""
    case1 = make_case(seed=42)
    case2 = make_case(seed=42)

    assert torch.allclose(case1.state, case2.state)
    assert torch.allclose(case1.prediction, case2.prediction)
    assert torch.allclose(case1.multiplier, case2.multiplier)
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
    assert "step_size" in case.config
    assert "momentum" in case.config
    assert "grad_clip" in case.config
    assert "seed" in case.config
    assert case.config["seed"] == 0


def test_make_case_tensors_on_device():
    """make_case should place tensors on requested device."""
    case = make_case(device="cpu")
    assert case.state.device.type == "cpu"