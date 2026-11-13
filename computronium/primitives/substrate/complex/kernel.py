"""Accelerated kernel for Complex Substrate.

No fused complex-substrate kernel exists, so this rung builds the reference
configuration. ``is_available`` reports whether the family's Triton kernels
compile; it does not make this rung a different substrate.
"""

from computronium.acceleration.availability import triton_rung_available

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    """Whether this rung can run here: the family's Triton kernels compile."""
    return triton_rung_available("complex_substrate")


def make_substrate(spec):
    """Create a complex substrate instance from a SubstrateSpec."""
    from .reference import make_substrate as reference_make_substrate

    return reference_make_substrate(spec)
