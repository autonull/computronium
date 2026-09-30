"""Accelerated kernel for Hebbian algorithm.

Imports Hebbian Triton kernels from acceleration.hebbian_kernels to establish
family membership and technology. Delegates to reference implementation
until a fused Hebbian algorithm kernel is written.
"""

from typing import Any

from computronium.acceleration.availability import triton_rung_available

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    """Whether this rung can run here: the family's Triton kernels compile."""
    return triton_rung_available("hebbian")


def step(case: Any) -> Any:
    """Execute one accelerated training step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # For now, delegate to reference implementation
    # In the future, this could fuse the Hebbian algorithm using
    # _hebbian_update_kernel, _three_factor_hebbian_kernel,
    # _contrastive_hebbian_kernel from hebbian_kernels
    from .reference import step as reference_step

    return reference_step(case)
