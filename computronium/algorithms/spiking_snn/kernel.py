"""Accelerated kernel for Spiking SNN algorithm.

Imports SNN Triton kernels from acceleration.snn_kernels to establish
family membership and technology. Delegates to reference implementation
until a fused SNN algorithm kernel is written.
"""

from typing import Any

from computronium.acceleration.availability import triton_rung_available

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    """Whether this rung can run here: the family's Triton kernels compile."""
    return triton_rung_available("snn")


def step(case: Any) -> Any:
    """Execute one accelerated training step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # For now, delegate to reference implementation
    # In the future, this could fuse the SNN algorithm using
    # _lif_step_kernel, _stdp_update_kernel, _contrastive_stdp_kernel
    # from snn_kernels
    from .reference import step as reference_step

    return reference_step(case)
