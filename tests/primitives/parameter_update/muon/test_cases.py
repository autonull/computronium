"""Tests for Muon case factory."""

import torch

from computronium.primitives.parameter_update.muon import make_case


def _config_equal(config1: dict, config2: dict, ignore_keys: set[str]) -> bool:
    """Compare two configs, handling tensors properly."""
    for k in config1:
        if k in ignore_keys:
            continue
        v1, v2 = config1[k], config2[k]
        if isinstance(v1, torch.Tensor) and isinstance(v2, torch.Tensor):
            if not v1.allclose(v2):
                return False
        elif v1 != v2:
            return False
    return True


def test_make_case_deterministic():
    case1 = make_case(seed=42)
    case2 = make_case(seed=42)

    assert case1.state.shape == case2.state.shape
    assert case1.state.allclose(case2.state)
    assert _config_equal(case1.config, case2.config, {"seed", "loss"})


def test_make_case_different_seeds():
    case1 = make_case(seed=42)
    case2 = make_case(seed=43)

    assert case1.state.shape == case2.state.shape
    assert not case1.state.allclose(case2.state)
    assert _config_equal(case1.config, case2.config, {"seed", "loss"})
