"""Tests for Predictive Settling kernel parity."""

import pytest

from computronium.acceleration.parity import assert_parity
from computronium.acceleration.registry import get
from computronium.primitives.state_dynamics.predictive_settling.kernel import (
    is_available,
)
from computronium.primitives.state_dynamics.predictive_settling.kernel import (
    step as kernel_step,
)

spec = get("primitive.state_dynamics.predictive_settling")


@pytest.mark.skipif(not is_available(), reason="kernel not available")
def test_kernel_parity(
    predictive_settling_kernel_warmup: None,
    predictive_settling_cases: dict,
    predictive_settling_ref_outputs: dict,
):
    """Test that kernel output matches reference within tolerance."""
    case = predictive_settling_cases[42]
    reference_output = predictive_settling_ref_outputs[42]
    kernel_output = kernel_step(case)

    assert_parity(reference_output, kernel_output, spec.parity)


@pytest.mark.skipif(not is_available(), reason="kernel not available")
def test_kernel_parity_different_seeds(
    predictive_settling_kernel_warmup: None,
    predictive_settling_cases: dict,
    predictive_settling_ref_outputs: dict,
):
    """Test kernel parity with different seeds."""
    for seed in [0, 1, 2, 42]:
        case = predictive_settling_cases[seed]
        reference_output = predictive_settling_ref_outputs[seed]
        kernel_output = kernel_step(case)

        assert_parity(reference_output, kernel_output, spec.parity)
