"""Test cases for Ternary Substrate primitive."""

from computronium.ontology.substrate.spec import (
    DeviceModel,
    ExecutionModel,
    NumericRepresentation,
)
from computronium.primitives.substrate.ternary import make_case


def test_make_case_returns_case():
    """Test that make_case returns a Case with correct structure."""
    case = make_case(device="cpu", seed=0)

    assert hasattr(case, "spec")
    assert hasattr(case, "config")

    assert case.spec.execution_model == ExecutionModel.NATIVE
    assert case.spec.device_model == DeviceModel.DIGITAL
    assert case.spec.numeric_representation == NumericRepresentation.TERNARY
    assert case.spec.noise_model.kind == "none"
    assert case.spec.noise_model.level == 0.0
    assert case.spec.structural_constraints.weight_bounds == (-1.0, 1.0)


def test_make_case_deterministic():
    """Test that make_case is deterministic with fixed seed."""
    case1 = make_case(device="cpu", seed=42)
    case2 = make_case(device="cpu", seed=42)

    assert case1.spec == case2.spec
    assert case1.config == case2.config


def test_make_case_config_structure():
    """Test that case config has expected keys."""
    case = make_case(device="cpu", seed=0)

    expected_keys = {
        "precision",
        "noise_level",
        "weight_bounds",
        "sparsity",
        "device",
        "seed",
    }
    assert set(case.config.keys()) == expected_keys
    assert case.config["precision"] == "ternary"
    assert case.config["weight_bounds"] == (-1.0, 1.0)