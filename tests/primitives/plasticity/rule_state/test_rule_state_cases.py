"""Tests for Rule State Plasticity case generation."""

import torch

from computronium.primitives.plasticity.rule_state import make_case


def test_make_case_deterministic():
    """make_case should be deterministic with fixed seed."""
    case1 = make_case(seed=42)
    case2 = make_case(seed=42)

    assert torch.allclose(case1.state, case2.state)
    assert torch.allclose(case1.prediction, case2.prediction)
    assert torch.allclose(case1.multiplier, case2.multiplier)
    assert case1.config == case2.config
    assert torch.allclose(case1.psi["operator_logits"], case2.psi["operator_logits"])
    assert torch.allclose(case1.psi["controller_state"], case2.psi["controller_state"])


def test_make_case_different_seeds():
    """make_case should produce different outputs with different seeds."""
    case1 = make_case(seed=0)
    case2 = make_case(seed=1)

    # At least one tensor should differ
    assert not torch.allclose(case1.state, case2.state)


def test_make_case_config_structure():
    """make_case should return expected config keys."""
    case = make_case()
    assert "seed" in case.config
    assert "num_operators" in case.config
    assert "operator_dim" in case.config
    assert "controller_hidden" in case.config
    assert "temperature" in case.config
    assert "learning_rate" in case.config
    assert "decay" in case.config
    assert case.config["seed"] == 0
    assert "operator_logits" in case.psi
    assert "controller_state" in case.psi


def test_make_case_tensors_on_device():
    """make_case should place tensors on requested device."""
    case = make_case(device="cpu")
    assert case.state.device.type == "cpu"
