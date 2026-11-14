"""Reference implementation tests for Target Inversion primitive."""

from computronium.primitives.credit_assignment.target_inversion import (
    make_case,
    reference_step,
)


def test_reference_step_deterministic():
    case = make_case(seed=42)
    out1 = reference_step(case)
    out2 = reference_step(case)

    assert len(out1) == len(out2)
    for a, b in zip(out1, out2, strict=True):
        assert a.shape == b.shape
        assert a.allclose(b)


def test_reference_step_different_seeds():
    case1 = make_case(seed=42)
    case2 = make_case(seed=43)

    out1 = reference_step(case1)
    out2 = reference_step(case2)

    # Different seeds should produce different outputs
    assert len(out1) == len(out2)
    for a, b in zip(out1, out2, strict=True):
        assert a.shape == b.shape
        assert not a.allclose(b)


def test_reference_step_returns_list_of_tensors():
    case = make_case(seed=0)
    result = reference_step(case)

    # Check that result is a list of tensors
    assert isinstance(result, list)
    assert len(result) > 0
    assert result[0].shape == (8, 4)  # weight shape (out_features, in_features)
