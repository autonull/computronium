"""Kernel parity tests for PC-ALM settling primitive."""

import pytest

from computronium.acceleration.parity import assert_parity
from computronium.acceleration.registry import get
from computronium.primitives.state_dynamics.pc_alm_settling import kernel


@pytest.mark.skipif("kernel" not in get("primitive.state_dynamics.pc_alm_settling").supported_backends, reason="no kernel backend")
@pytest.mark.skipif(not kernel.is_available(), reason="kernel not available")
def test_kernel_parity(
    pc_alm_kernel_warmup: None,
    pc_alm_cases: dict,
    pc_alm_ref_outputs: dict,
):
    """Test that kernel output matches reference within tolerance."""
    spec = get("primitive.state_dynamics.pc_alm_settling")
    case = pc_alm_cases[0]
    reference_output = pc_alm_ref_outputs[0]
    kernel_output = kernel.step(case)

    assert_parity(reference_output, kernel_output, spec.parity)


@pytest.mark.skipif("kernel" not in get("primitive.state_dynamics.pc_alm_settling").supported_backends, reason="no kernel backend")
@pytest.mark.skipif(not kernel.is_available(), reason="kernel not available")
def test_kernel_parity_different_seeds(
    pc_alm_kernel_warmup: None,
    pc_alm_cases: dict,
    pc_alm_ref_outputs: dict,
):
    """Test kernel parity with multiple seeds."""
    spec = get("primitive.state_dynamics.pc_alm_settling")

    for seed in [0, 1, 2, 42]:
        case = pc_alm_cases[seed]
        reference_output = pc_alm_ref_outputs[seed]
        kernel_output = kernel.step(case)

        assert_parity(reference_output, kernel_output, spec.parity)
