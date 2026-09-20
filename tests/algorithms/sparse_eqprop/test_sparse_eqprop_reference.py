"""Reference implementation tests for SparseEqprop algorithm."""

import torch

from computronium.algorithms.sparse_eqprop import (
    make_case,
    reference_step,
)


def test_reference_step_returns_dict():
    """Test that reference_step returns a metrics dict."""
    case = make_case(device="cpu", seed=0)
    result = reference_step(case)

    assert result is not None
    assert isinstance(result, dict)
    assert "loss" in result


def test_reference_step_deterministic():
    """Test that reference_step is deterministic with fixed seed."""
    case = make_case(device="cpu", seed=42)
    result1 = reference_step(case)

    case2 = make_case(device="cpu", seed=42)
    result2 = reference_step(case2)

    # Compare metrics
    for key in result1:
        if isinstance(result1[key], torch.Tensor):
            torch.testing.assert_close(result1[key], result2[key])
        else:
            assert result1[key] == result2[key]


def test_reference_step_different_seeds():
    """Test that different seeds produce different results."""
    case1 = make_case(device="cpu", seed=0)
    case2 = make_case(device="cpu", seed=1)

    result1 = reference_step(case1)
    result2 = reference_step(case2)

    # At least one metric should differ
    differ = False
    for key in result1:
        if isinstance(result1[key], torch.Tensor):
            if not torch.allclose(result1[key], result2[key]):
                differ = True
                break
        elif result1[key] != result2[key]:
            differ = True
            break
    assert differ