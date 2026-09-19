"""Case factory tests for Digital Substrate primitive."""

import torch

from computronium.primitives.substrate.digital.cases import (
    Case,
    make_case,
    make_case_noisy,
    make_case_sparse,
)


def test_make_case_returns_case():
    """Test that make_case returns a Case instance."""
    case = make_case(device="cpu", seed=0)

    assert isinstance(case, Case)
    assert hasattr(case, "spec")
    assert isinstance(case.config, dict)


def test_make_case_deterministic():
    """Test that make_case is deterministic with fixed seed."""
    case1 = make_case(device="cpu", seed=42)
    case2 = make_case(device="cpu", seed=42)

    assert case1.spec == case2.spec
    assert case1.config == case2.config


def test_make_case_different_seeds():
    """Test that different seeds produce different cases (config differs)."""
    case1 = make_case(device="cpu", seed=0)
    case2 = make_case(device="cpu", seed=1)

    # Config should differ (seed field)
    assert case1.config["seed"] != case2.config["seed"]


def test_make_case_config_structure():
    """Test that case config has expected structure."""
    case = make_case(device="cpu", seed=0)

    assert "precision" in case.config
    assert "noise_level" in case.config
    assert "weight_bounds" in case.config
    assert "sparsity" in case.config
    assert "device" in case.config
    assert "seed" in case.config
    assert case.config["seed"] == 0


def test_make_case_noisy():
    """Test that make_case_noisy creates noisy spec."""
    case = make_case_noisy(device="cpu", seed=0, noise_level=0.1)

    assert isinstance(case, Case)
    assert case.spec.noise_model.level == 0.1
    assert case.spec.noise_model.kind == "additive_gaussian"
    assert case.config["noise_level"] == 0.1


def test_make_case_sparse():
    """Test that make_case_sparse creates sparse spec."""
    case = make_case_sparse(device="cpu", seed=0, sparsity=0.5)

    assert isinstance(case, Case)
    assert case.spec.structural_constraints.sparsity == 0.5
    assert case.config["sparsity"] == 0.5