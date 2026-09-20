"""Tests for Quantum Substrate kernel parity."""

import pytest

from computronium.primitives.substrate.quantum import (
    make_case,
    reference_make_substrate,
    kernel_make_substrate,
    is_available,
)


def test_kernel_parity():
    """Kernel output should match reference."""
    if not is_available():
        pytest.skip("kernel not available")

    case = make_case()
    ref_substrate = reference_make_substrate(case.spec)
    ker_substrate = kernel_make_substrate(case.spec)

    # Both should be QuantumSubstrate instances
    from computronium.ontology.substrate._substrate import QuantumSubstrate

    assert isinstance(ref_substrate, QuantumSubstrate)
    assert isinstance(ker_substrate, QuantumSubstrate)


def test_kernel_parity_noisy():
    """Kernel parity should hold for noisy spec."""
    if not is_available():
        pytest.skip("kernel not available")

    from computronium.primitives.substrate.quantum import make_case_noisy

    case = make_case_noisy(noise_level=0.1)
    ref_substrate = reference_make_substrate(case.spec)
    ker_substrate = kernel_make_substrate(case.spec)

    from computronium.ontology.substrate._substrate import QuantumSubstrate

    assert isinstance(ref_substrate, QuantumSubstrate)
    assert isinstance(ker_substrate, QuantumSubstrate)
