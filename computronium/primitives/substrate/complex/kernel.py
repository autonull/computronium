"""Accelerated kernel for Complex Substrate.

Imports Triton kernels from computronium.core.substrates.complex_substrate to establish
family membership and technology. Delegates to reference implementation
until a fused complex substrate kernel is written.
"""

from computronium.acceleration.availability import triton_rung_available
from computronium.core.substrates.complex_substrate import ComplexSubstrate

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    """Whether this rung can run here: the family's Triton kernels compile."""
    return triton_rung_available("complex_substrate")


def make_substrate(spec):
    """Create a complex substrate instance from a SubstrateSpec."""
    if not is_available():
        from .reference import make_substrate as reference_make_substrate

        return reference_make_substrate(spec)

    # Use accelerated implementation - convert SubstrateSpec to SubstrateConfig
    config = spec.to_config()
    return ComplexSubstrate(config)
