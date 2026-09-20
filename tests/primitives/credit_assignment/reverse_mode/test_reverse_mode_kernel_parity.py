"""Kernel parity tests for Reverse Mode primitive."""

import pytest

from computronium.acceleration.parity import assert_parity
from computronium.primitives.credit_assignment.reverse_mode import (
    SPEC,
    make_case,
    reference_step,
)
from computronium.primitives.credit_assignment.reverse_mode.kernel import (
    is_available,
)
from computronium.primitives.credit_assignment.reverse_mode.kernel import (
    step as kernel_step,
)


def test_kernel_parity():
    """Test that kernel output matches reference within tolerance."""
    if not is_available():
        pytest.skip("kernel not available")

    # Use separate cases for reference and kernel since autograd frees the graph
    case_ref = make_case(device="cpu", seed=0)
    case_kern = make_case(device="cpu", seed=0)

    reference_output = reference_step(case_ref)
    kernel_output = kernel_step(case_kern)

    assert_parity(reference_output, kernel_output, SPEC.parity)


def test_kernel_parity_different_seeds():
    """Test kernel parity with different seeds."""
    if not is_available():
        pytest.skip("kernel not available")

    for seed in [1, 2, 42]:
        case_ref = make_case(device="cpu", seed=seed)
        case_kern = make_case(device="cpu", seed=seed)

        reference_output = reference_step(case_ref)
        kernel_output = kernel_step(case_kern)

        assert_parity(reference_output, kernel_output, SPEC.parity)
