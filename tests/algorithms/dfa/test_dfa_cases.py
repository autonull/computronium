"""Tests for Direct Feedback Alignment algorithm case factory."""

from computronium.algorithms.dfa import make_case


def test_make_case_deterministic():
    case1 = make_case(seed=42)
    case2 = make_case(seed=42)

    assert case1.state.shape == case2.state.shape
    assert case1.state.allclose(case2.state)
    assert case1.target is not None and case2.target is not None
    assert case1.target.shape == case2.target.shape
    assert case1.target.allclose(case2.target)
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
