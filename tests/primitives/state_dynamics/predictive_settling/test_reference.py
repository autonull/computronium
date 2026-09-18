"""Tests for Predictive Settling reference implementation."""

from computronium.primitives.state_dynamics.predictive_settling import (
    make_case,
    reference_step,
)


def test_reference_step_deterministic():
    case = make_case(seed=42)
    out1 = reference_step(case)
    out2 = reference_step(case)

    assert out1.activations is not None
    assert out2.activations is not None
    # activations is a list of tensors
    assert len(out1.activations) == len(out2.activations)
    for a, b in zip(out1.activations, out2.activations, strict=True):
        assert a.shape == b.shape
        assert a.allclose(b)


def test_reference_step_different_seeds():
    case1 = make_case(seed=42)
    case2 = make_case(seed=43)

    out1 = reference_step(case1)
    out2 = reference_step(case2)

    # Different seeds should produce different outputs
    assert out1.activations is not None
    assert out2.activations is not None
    assert len(out1.activations) == len(out2.activations)
    for a, b in zip(out1.activations, out2.activations, strict=True):
        assert a.shape == b.shape
        assert not a.allclose(b)


def test_reference_step_returns_composite_state():
    case = make_case(seed=0)
    result = reference_step(case)

    # Check that result is a CompositeState with expected fields
    assert hasattr(result, "activations")
    assert result.activations is not None
    assert isinstance(result.activations, list)
    assert len(result.activations) > 0
    assert result.activations[0].shape == (2, 4)