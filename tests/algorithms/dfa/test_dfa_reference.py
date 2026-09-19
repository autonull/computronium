"""Tests for Direct Feedback Alignment algorithm reference implementation."""

from computronium.algorithms.dfa import (
    make_case,
    reference_step,
)


def test_reference_step_deterministic():
    case = make_case(seed=42)
    out1 = reference_step(case)
    out2 = reference_step(case)

    assert out1 is not None
    assert out2 is not None


def test_reference_step_different_seeds():
    case1 = make_case(seed=42)
    case2 = make_case(seed=43)

    out1 = reference_step(case1)
    out2 = reference_step(case2)

    assert out1 is not None
    assert out2 is not None


def test_reference_step_returns_dict():
    case = make_case(seed=0)
    result = reference_step(case)

    # Check that result is a dict with expected keys
    assert isinstance(result, dict)
    assert "loss" in result
    assert "nudged_fit_accuracy" in result
