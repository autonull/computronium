"""Case factory tests for Neuromorphic Substrate primitive."""

from computronium.primitives.substrate.neuromorphic.cases import (
    Case,
    make_case,
    make_case_noisy,
)


def test_make_case_returns_case():
    """Test that make_case returns a Case instance."""
    case = make_case(device="cpu", seed=0)

    assert isinstance(case, Case)
    assert hasattr(case, "spec")
    assert hasattr(case, "config")
    # Check spec is a SubstrateSpec
    assert case.spec.device_model.value == "neuromorphic"


def test_make_case_deterministic():
    """Test that make_case is deterministic with fixed seed."""
    case1 = make_case(device="cpu", seed=42)
    case2 = make_case(device="cpu", seed=42)

    assert case1.config == case2.config


def test_make_case_different_seeds():
    """Test that different seeds produce different cases."""
    case1 = make_case(device="cpu", seed=0)
    case2 = make_case(device="cpu", seed=1)

    assert case1.config != case2.config


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


def test_make_case_noisy_returns_case():
    """Test that make_case_noisy returns a Case instance."""
    case = make_case_noisy(device="cpu", seed=0, noise_level=0.1)

    assert isinstance(case, Case)
    assert hasattr(case, "spec")
    assert hasattr(case, "config")
    # Check spec has noise
    assert case.spec.noise_model.kind == "additive_gaussian"
    assert case.spec.noise_model.level == 0.1
