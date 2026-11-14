"""Tests for Elastic Consolidation Update kernel parity."""

import pytest
import torch

from computronium.primitives.parameter_update.elastic_consolidation import (
    is_available,
    kernel_step,
    make_case,
    reference_step,
)


def test_kernel_parity():
    """Kernel output should match reference within tolerance."""
    if not is_available():
        pytest.skip("kernel not available")

    case = make_case()
    ref_out = reference_step(case)
    ker_out = kernel_step(case)

    assert set(ref_out.keys()) == set(ker_out.keys())
    for k in ref_out:
        assert torch.allclose(ref_out[k], ker_out[k], atol=1e-4, rtol=1e-3)


def test_kernel_parity_different_seeds():
    """Kernel parity should hold across different seeds."""
    if not is_available():
        pytest.skip("kernel not available")

    for seed in [0, 1, 42]:
        case = make_case(seed=seed)
        ref_out = reference_step(case)
        ker_out = kernel_step(case)

        assert set(ref_out.keys()) == set(ker_out.keys())
        for k in ref_out:
            assert torch.allclose(ref_out[k], ker_out[k], atol=1e-4, rtol=1e-3)
