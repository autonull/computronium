"""Tests for Photonic Substrate case generation."""

import pytest
import torch

from computronium.primitives.substrate.photonic import make_case, make_case_noisy


def test_make_case_deterministic():
    """make_case should be deterministic with fixed seed."""
    case1 = make_case(seed=42)
    case2 = make_case(seed=42)

    assert case1.spec == case2.spec
    assert case1.config == case2.config


def test_make_case_different_seeds():
    """make_case should produce different outputs with different seeds."""
    case1 = make_case(seed=0)
    case2 = make_case(seed=1)

    # Config differs in seed
    assert case1.config["seed"] != case2.config["seed"]


def test_make_case_config_structure():
    """make_case should return expected config keys."""
    case = make_case()
    assert "precision" in case.config
    assert "noise_level" in case.config
    assert "weight_bounds" in case.config
    assert "sparsity" in case.config
    assert "device" in case.config
    assert "seed" in case.config
    assert case.config["seed"] == 0
    assert case.config["precision"] == "complex64"
    assert case.spec.device_model.value == "photonic"
    assert case.spec.numeric_representation.value == "complex"


def test_make_case_noisy():
    """make_case_noisy should create spec with noise."""
    case = make_case_noisy(noise_level=0.1)
    assert case.config["noise_level"] == 0.1
    assert case.spec.noise_model.kind == "additive_gaussian"
    assert case.spec.noise_model.level == 0.1


def test_make_case_tensors_on_device():
    """make_case should place tensors on requested device."""
    case = make_case(device="cpu")
    assert case.config["device"] == "cpu"