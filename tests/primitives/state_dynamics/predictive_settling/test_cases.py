"""Tests for Predictive Settling case factory."""

from computronium.primitives.state_dynamics.predictive_settling import make_case


def test_make_case_deterministic():
    case1 = make_case(seed=42)
    case2 = make_case(seed=42)

    assert case1.state.shape == case2.state.shape
    assert case1.state.allclose(case2.state)
    # Config differs in seed
    config1 = {k: v for k, v in case1.config.items() if k != "seed"}
    config2 = {k: v for k, v in case2.config.items() if k != "seed"}
    assert config1 == config2


def test_make_case_different_seeds():
    case1 = make_case(seed=42)
    case2 = make_case(seed=43)

    assert case1.state.shape == case2.state.shape
    assert not case1.state.allclose(case2.state)
    # Config differs in seed
    config1 = {k: v for k, v in case1.config.items() if k != "seed"}
    config2 = {k: v for k, v in case2.config.items() if k != "seed"}
    assert config1 == config2