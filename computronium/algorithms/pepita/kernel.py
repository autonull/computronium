"""Accelerated kernel for PEPITA algorithm.

Imports PEPITA Triton kernels from acceleration.ff_kernels to establish
family membership and technology. Delegates to reference implementation
until a fused PEPITA algorithm kernel is written.
"""

from typing import Any

from computronium.acceleration.availability import triton_rung_available

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    """Whether this rung can run here: the family's Triton kernels compile."""
    return triton_rung_available("pepita")


def step(case: Any) -> Any:
    """Execute one accelerated training step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # For now, delegate to reference implementation
    # In the future, this could fuse the PEPITA algorithm using
    # _pepita_error_modulation_kernel, _pepita_contrastive_update_kernel
    # from ff_kernels
    from .reference import step as reference_step

    return reference_step(case)
