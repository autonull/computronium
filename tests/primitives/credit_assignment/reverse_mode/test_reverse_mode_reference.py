"""Reference implementation tests for Reverse Mode primitive."""


from computronium.primitives.credit_assignment.reverse_mode import (
    make_case,
    reference_step,
)


def test_reference_step_returns_list_of_tensors():
    """Test that reference_step returns a list of gradient tensors."""
    case = make_case(device="cpu", seed=0)
    result = reference_step(case)

    # Check that result is a list of tensors
    assert isinstance(result, list)
    assert len(result) > 0
    # Weight shapes: (4, 4) for each Linear layer
    assert result[0].shape == (4, 4)


def test_reference_step_deterministic():
    """Test that reference_step is deterministic with fixed seed."""
    case = make_case(device="cpu", seed=42)
    result1 = reference_step(case)

    case2 = make_case(device="cpu", seed=42)
    result2 = reference_step(case2)

    assert len(result1) == len(result2)
    for a, b in zip(result1, result2, strict=True):
        assert a.shape == b.shape
        assert a.allclose(b)


def test_reference_step_different_seeds():
    """Test that different seeds produce different results."""
    case1 = make_case(device="cpu", seed=0)
    case2 = make_case(device="cpu", seed=1)

    result1 = reference_step(case1)
    result2 = reference_step(case2)

    assert len(result1) == len(result2)
    for a, b in zip(result1, result2, strict=True):
        assert a.shape == b.shape
        assert not a.allclose(b)
