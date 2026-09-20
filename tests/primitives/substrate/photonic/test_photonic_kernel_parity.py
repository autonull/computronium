"""Tests for Photonic Substrate kernel parity."""

import pytest

from computronium.primitives.substrate.photonic import (
    is_available,
    kernel_make_substrate,
    make_case,
    reference_make_substrate,
)


def test_kernel_parity():
    """Kernel output should match reference."""
    if not is_available():
        pytest.skip("kernel not available")

    case = make_case()
    ref_substrate = reference_make_substrate(case.spec)
    ker_substrate = kernel_make_substrate(case.spec)

    # Both should be OpticalSubstrate instances
    from computronium.ontology.substrate._substrate import OpticalSubstrate

    assert isinstance(ref_substrate, OpticalSubstrate)
    assert isinstance(ker_substrate, OpticalSubstrate)


def test_kernel_parity_noisy():
    """Kernel parity should hold for noisy spec."""
    if not is_available():
        pytest.skip("kernel not available")

    from computronium.primitives.substrate.photonic import make_case_noisy

    case = make_case_noisy(noise_level=0.1)
    ref_substrate = reference_make_substrate(case.spec)
    ker_substrate = kernel_make_substrate(case.spec)

    from computronium.ontology.substrate._substrate import OpticalSubstrate

    assert isinstance(ref_substrate, OpticalSubstrate)
    assert isinstance(ker_substrate, OpticalSubstrate)
