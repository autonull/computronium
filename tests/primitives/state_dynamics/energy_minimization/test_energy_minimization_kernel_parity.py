"""Kernel parity tests for Energy Minimization primitive."""

import pytest

from computronium.acceleration.parity import assert_parity
from computronium.primitives.state_dynamics.energy_minimization import (
    SPEC,
    make_case,
    reference_step,
)
from computronium.primitives.state_dynamics.energy_minimization.kernel import (
    is_available,
)
from computronium.primitives.state_dynamics.energy_minimization.kernel import (
    step as kernel_step,
)


def test_kernel_parity():
    """Test that kernel output matches reference within tolerance."""
    if not is_available():
        pytest.skip("kernel not available")

    case = make_case(device="cpu", seed=0)

    reference_output = reference_step(case)
    kernel_output = kernel_step(case)

    assert_parity(reference_output, kernel_output, SPEC.parity)


def test_kernel_parity_different_seeds():
    """Test kernel parity with different seeds."""
    if not is_available():
        pytest.skip("kernel not available")

    for seed in [1, 2, 42]:
        case = make_case(device="cpu", seed=seed)

        reference_output = reference_step(case)
        kernel_output = kernel_step(case)

        assert_parity(reference_output, kernel_output, SPEC.parity)
