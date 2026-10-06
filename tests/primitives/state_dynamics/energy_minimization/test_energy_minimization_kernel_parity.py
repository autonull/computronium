"""Tests for Energy Minimization kernel parity."""

import pytest

from computronium.acceleration.parity import assert_parity
from computronium.acceleration.registry import get
from computronium.primitives.state_dynamics.energy_minimization.kernel import (
    is_available,
)
from computronium.primitives.state_dynamics.energy_minimization.kernel import (
    step as kernel_step,
)

spec = get("primitive.state_dynamics.energy_minimization")


@pytest.mark.skipif(not is_available(), reason="kernel not available")
def test_kernel_parity(
    energy_minimization_kernel_warmup: None,
    energy_minimization_cases: dict,
    energy_minimization_ref_outputs: dict,
):
    """Test that kernel output matches reference within tolerance."""
    case = energy_minimization_cases[42]
    reference_output = energy_minimization_ref_outputs[42]
    kernel_output = kernel_step(case)

    assert_parity(reference_output, kernel_output, spec.parity)


@pytest.mark.skipif(not is_available(), reason="kernel not available")
def test_kernel_parity_different_seeds(
    energy_minimization_kernel_warmup: None,
    energy_minimization_cases: dict,
    energy_minimization_ref_outputs: dict,
):
    """Test kernel parity with different seeds."""
    for seed in [0, 1, 2, 42]:
        case = energy_minimization_cases[seed]
        reference_output = energy_minimization_ref_outputs[seed]
        kernel_output = kernel_step(case)

        assert_parity(reference_output, kernel_output, spec.parity)
