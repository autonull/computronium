"""Tests for Predictive Settling kernel parity."""

import pytest

from computronium.acceleration.parity import assert_parity
from computronium.acceleration.registry import get
from computronium.primitives.state_dynamics.predictive_settling import (
    make_case,
    reference_step,
)

# Try to import kernel; skip if not available
try:
    from computronium.primitives.state_dynamics.predictive_settling.kernel import (
        is_available,
        step as kernel_step,
    )

    KERNEL_AVAILABLE = is_available()
except ImportError:
    KERNEL_AVAILABLE = False

spec = get("primitive.state_dynamics.predictive_settling")


@pytest.mark.skipif(not KERNEL_AVAILABLE, reason="kernel not available")
def test_kernel_parity():
    case = make_case(seed=42)

    reference_output = reference_step(case)
    kernel_output = kernel_step(case)

    assert_parity(reference_output, kernel_output, spec.parity)


@pytest.mark.skipif(not KERNEL_AVAILABLE, reason="kernel not available")
def test_kernel_parity_different_seeds():
    for seed in [0, 1, 42, 123]:
        case = make_case(seed=seed)

        reference_output = reference_step(case)
        kernel_output = kernel_step(case)

        assert_parity(reference_output, kernel_output, spec.parity)