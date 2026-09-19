"""Tests for Thermodynamic Contrast kernel parity."""

import pytest
import torch

from computronium.primitives.credit_assignment.thermodynamic_contrast import (
    make_case,
    reference_step,
    kernel_step,
    is_available,
)


def test_kernel_parity():
    """Kernel output should match reference within tolerance."""
    if not is_available():
        pytest.skip("kernel not available")

    case = make_case()
    ref_out = reference_step(case)
    ker_out = kernel_step(case)

    assert len(ref_out) == len(ker_out)
    for ref, ker in zip(ref_out, ker_out):
        assert torch.allclose(ref, ker, atol=1e-4, rtol=1e-3)


def test_kernel_parity_different_seeds():
    """Kernel parity should hold across different seeds."""
    if not is_available():
        pytest.skip("kernel not available")

    for seed in [0, 1, 42]:
        case = make_case(seed=seed)
        ref_out = reference_step(case)
        ker_out = kernel_step(case)

        assert len(ref_out) == len(ker_out)
        for ref, ker in zip(ref_out, ker_out):
            assert torch.allclose(ref, ker, atol=1e-4, rtol=1e-3)
