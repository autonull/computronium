"""Test cases for Sparse Substrate primitive."""

from computronium.ontology.substrate.spec import (
    DeviceModel,
    ExecutionModel,
    NumericRepresentation,
)
from computronium.primitives.substrate.sparse import make_case, make_case_high_sparsity


def test_make_case_returns_case():
    """Test that make_case returns a Case with correct structure."""
    case = make_case(device="cpu", seed=0)

    assert hasattr(case, "spec")
    assert hasattr(case, "config")

    assert case.spec.execution_model == ExecutionModel.NATIVE
    assert case.spec.device_model == DeviceModel.DIGITAL
    assert case.spec.numeric_representation == NumericRepresentation.REAL
    assert case.spec.noise_model.kind == "none"
    assert case.spec.noise_model.level == 0.0
    assert case.spec.structural_constraints.sparsity == 0.5


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


def test_make_case_high_sparsity():
    """Test make_case_high_sparsity with custom sparsity level."""
    case = make_case_high_sparsity(device="cpu", seed=0, sparsity=0.9)

    assert case.spec.structural_constraints.sparsity == 0.9
    assert case.config["sparsity"] == 0.9
