"""Reference implementation tests for Closed-form Ridge Plasticity primitive."""

import torch

from computronium.primitives.plasticity.closed_form_ridge import (
    make_case,
    reference_step,
)


def test_reference_step_deterministic():
    case = make_case(seed=42)
    out1 = reference_step(case)
    out2 = reference_step(case)

    assert set(out1.keys()) == set(out2.keys())
    for k in out1:
        assert out1[k].shape == out2[k].shape
        assert out1[k].allclose(out2[k])


def test_reference_step_different_seeds():
    case1 = make_case(seed=42)
    case2 = make_case(seed=43)

    out1 = reference_step(case1)
    out2 = reference_step(case2)

    # Different seeds should produce different outputs
    assert set(out1.keys()) == set(out2.keys())
    for k in out1:
        assert out1[k].shape == out2[k].shape
        assert not out1[k].allclose(out2[k])


def test_reference_step_returns_dict():
    case = make_case(seed=0)
    result = reference_step(case)

    # Check that result is a dict with expected keys
    assert isinstance(result, dict)
    assert "gram" in result
    assert "cross" in result
    assert "readout_m" in result
    assert "readout_b" in result