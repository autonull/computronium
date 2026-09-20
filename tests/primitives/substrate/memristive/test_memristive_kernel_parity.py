"""Kernel parity tests for Memristive Substrate primitive.

For substrate primitives, parity means structural equivalence of created substrates.
"""

import pytest

from computronium.primitives.substrate.memristive import (
    make_case,
    reference_make_substrate,
)
from computronium.primitives.substrate.memristive.kernel import (
    is_available,
)
from computronium.primitives.substrate.memristive.kernel import (
    make_substrate as kernel_make_substrate,
)


def test_kernel_substrate_equivalence():
    """Test that kernel creates equivalent substrate to reference."""
    if not is_available():
        pytest.skip("kernel not available")

    case = make_case(device="cpu", seed=0)

    reference_substrate = reference_make_substrate(case.spec)
    kernel_substrate = kernel_make_substrate(case.spec)

    # Both should be same type
    assert type(reference_substrate) is type(kernel_substrate)

    # Both should be MemristiveSubstrate
    from computronium.ontology.substrate._substrate import MemristiveSubstrate

    assert isinstance(reference_substrate, MemristiveSubstrate)
    assert isinstance(kernel_substrate, MemristiveSubstrate)


def test_kernel_substrate_equivalence_noisy():
    """Test kernel substrate equivalence with noisy spec."""
    if not is_available():
        pytest.skip("kernel not available")

    from computronium.primitives.substrate.memristive import make_case_noisy

    case = make_case_noisy(device="cpu", seed=0, noise_level=0.1)

    reference_substrate = reference_make_substrate(case.spec)
    kernel_substrate = kernel_make_substrate(case.spec)

    assert type(reference_substrate) is type(kernel_substrate)
