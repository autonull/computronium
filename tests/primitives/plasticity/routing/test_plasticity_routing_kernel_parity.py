"""Kernel parity tests for Routing Plasticity primitive."""

import pytest

from computronium.acceleration.parity import assert_parity
from computronium.acceleration.registry import get
from computronium.primitives.plasticity.routing import (
    kernel_step,
    make_case,
    reference_step,
)


def test_kernel_parity():
    """Test that kernel output matches reference within tolerance."""
    spec = get("primitive.plasticity.routing")

    if "kernel" not in spec.supported_backends:
        pytest.skip("no kernel backend")

    # Import kernel module to check availability
    from computronium.primitives.plasticity.routing import kernel

    if not kernel.is_available():
        pytest.skip("kernel not available")

    case = make_case(device="cpu", seed=0)
    reference_output = reference_step(case)
    kernel_output = kernel_step(case)

    assert_parity(reference_output, kernel_output, spec.parity)


def test_kernel_parity_different_seeds():
    """Test kernel parity with multiple seeds."""
    spec = get("primitive.plasticity.routing")

    if "kernel" not in spec.supported_backends:
        pytest.skip("no kernel backend")

    from computronium.primitives.plasticity.routing import kernel

    if not kernel.is_available():
        pytest.skip("kernel not available")

    for seed in [0, 1, 2, 42]:
        case = make_case(device="cpu", seed=seed)
        reference_output = reference_step(case)
        kernel_output = kernel_step(case)

        assert_parity(reference_output, kernel_output, spec.parity)
