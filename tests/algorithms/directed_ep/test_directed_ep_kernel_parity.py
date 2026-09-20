"""Kernel parity tests for DirectedEp algorithm."""

import pytest
import torch

from computronium.acceleration.parity import assert_parity
from computronium.acceleration.registry import get
from computronium.algorithms.directed_ep import (
    kernel_step,
    make_case,
    reference_step,
)


def test_kernel_parity():
    """Test that kernel output matches reference within tolerance."""
    spec = get("algorithm.directed_ep")

    if "kernel" not in spec.supported_backends:
        pytest.skip("no kernel backend")

    # Import kernel module to check availability
    from computronium.algorithms.directed_ep import kernel

    if not kernel.is_available():
        pytest.skip("kernel not available")

    # Use fixed RNG context for deterministic comparison
    torch.manual_seed(0)
    case = make_case(device="cpu", seed=0)
    reference_output = reference_step(case)

    torch.manual_seed(0)
    case2 = make_case(device="cpu", seed=0)
    kernel_output = kernel_step(case2)

    assert_parity(reference_output, kernel_output, spec.parity)


def test_kernel_parity_different_seeds():
    """Test kernel parity with multiple seeds."""
    spec = get("algorithm.directed_ep")

    if "kernel" not in spec.supported_backends:
        pytest.skip("no kernel backend")

    from computronium.algorithms.directed_ep import kernel

    if not kernel.is_available():
        pytest.skip("kernel not available")

    for seed in [0, 1, 2, 42]:
        torch.manual_seed(0)
        case = make_case(device="cpu", seed=seed)
        reference_output = reference_step(case)

        torch.manual_seed(0)
        case2 = make_case(device="cpu", seed=seed)
        kernel_output = kernel_step(case2)

        assert_parity(reference_output, kernel_output, spec.parity)