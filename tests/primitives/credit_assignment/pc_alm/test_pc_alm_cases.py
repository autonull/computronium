"""Tests for PC-ALM Credit Assignment case factory."""

from computronium.primitives.credit_assignment.pc_alm import make_case


def test_make_case_deterministic():
    case1 = make_case(seed=42)
    case2 = make_case(seed=42)

    assert case1.state.shape == case2.state.shape
    assert case1.state.allclose(case2.state)
    for a1, a2 in zip(case1.activations, case2.activations, strict=True):
        assert a1.shape == a2.shape
        assert a1.allclose(a2)
    for n1, n2 in zip(case1.nudged_activations, case2.nudged_activations, strict=True):
        assert n1.shape == n2.shape
        assert n1.allclose(n2)
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


def test_make_case_has_dual_vars():
    case = make_case(seed=42)

    assert case.dual_vars is not None
    assert len(case.dual_vars) == 2
    assert case.dual_vars_nudged is not None
    assert len(case.dual_vars_nudged) == 2
    for dv in case.dual_vars:
        assert dv.shape == (2, 4)
    for dv in case.dual_vars_nudged:
        assert dv.shape == (2, 4)
