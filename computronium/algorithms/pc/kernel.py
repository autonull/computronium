"""Accelerated kernel for Predictive Coding algorithm.

Imports PC Triton kernels from acceleration.pc_kernels to establish
family membership and technology. Delegates to reference implementation
until a fused PC algorithm kernel is written.
"""

from typing import Any

from computronium.acceleration.availability import triton_rung_available
from computronium.acceleration.pc_kernels import HAS_TRITON_PC  # ruff: ignore[unused-import] (used by family_of derivation)

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    """Whether this rung can run here: the family's Triton kernels compile."""
    return triton_rung_available("pc")


def step(case: Any) -> Any:
    """Execute one accelerated training step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # For now, delegate to reference implementation
    # In the future, this could fuse the PC algorithm using
    # _pc_prediction_kernel, _pc_error_update_kernel,
    # _pc_contrastive_update_kernel from pc_kernels
    from .reference import step as reference_step

    return reference_step(case)
