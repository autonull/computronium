"""Kernel parity tests for Complex Substrate primitive."""

import pytest
import torch

from computronium.acceleration.parity import assert_parity
from computronium.acceleration.registry import get
from computronium.primitives.substrate.complex import (
    kernel_make_substrate,
    make_case,
    reference_make_substrate,
)


def test_kernel_parity():
    """Test that kernel output matches reference within tolerance."""
    spec = get("primitive.substrate.complex")

    if "kernel" not in spec.supported_backends:
        pytest.skip("no kernel backend")

    from computronium.primitives.substrate.complex import kernel

    if not kernel.is_available():
        pytest.skip("kernel not available")

    case = make_case(device="cpu", seed=0)
    reference_substrate = reference_make_substrate(case.spec)
    kernel_substrate = kernel_make_substrate(case.spec)

    # For substrates, parity means same forward behavior
    x = torch.randn(2, 4, dtype=torch.complex64)
    w = torch.randn(4, 4, dtype=torch.complex64)

    ref_forward = reference_substrate.get_forward_operator()
    ker_forward = kernel_substrate.get_forward_operator()

    ref_out = ref_forward(x, w)
    ker_out = ker_forward(x, w)

    assert_parity(ref_out, ker_out, spec.parity)


def test_kernel_parity_different_seeds():
    """Test kernel parity with multiple seeds."""
    spec = get("primitive.substrate.complex")

    if "kernel" not in spec.supported_backends:
        pytest.skip("no kernel backend")

    from computronium.primitives.substrate.complex import kernel

    if not kernel.is_available():
        pytest.skip("kernel not available")

    for seed in [0, 1, 2, 42]:
        case = make_case(device="cpu", seed=seed)
        reference_substrate = reference_make_substrate(case.spec)
        kernel_substrate = kernel_make_substrate(case.spec)

        x = torch.randn(2, 4, dtype=torch.complex64)
        w = torch.randn(4, 4, dtype=torch.complex64)

        ref_forward = reference_substrate.get_forward_operator()
        ker_forward = kernel_substrate.get_forward_operator()

        ref_out = ref_forward(x, w)
        ker_out = ker_forward(x, w)

        assert_parity(ref_out, ker_out, spec.parity)
