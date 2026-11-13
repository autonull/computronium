"""Accelerated kernel for Analog Substrate.

No fused analog kernel exists; the kernel rung resolves to the reference rung
and the spec stays ``reference_only``.
"""

from computronium.acceleration.backends import kernel_available

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def make_substrate(spec):
    """Create an analog substrate instance from a SubstrateSpec."""
    from .reference import make_substrate as reference_make_substrate

    return reference_make_substrate(spec)
