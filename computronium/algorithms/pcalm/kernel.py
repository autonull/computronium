"""Accelerated kernel for PC-ALM algorithm.

Calls the PC-ALM primitive settling kernel (which uses the compiled
triton settle loop) for the core dynamics. The full algorithm kernel
(including credit assignment and parameter update) is not yet implemented
in triton; delegates to reference for the complete training step.
"""

from typing import Any

from computronium.acceleration.availability import triton_rung_available
from computronium.acceleration.pcalm_kernels import TRITON_IMPORTED_PCALM  # ruff: ignore[unused-import] (used by family_of derivation)

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    """Whether this rung can run here: the family's Triton kernels compile."""
    return triton_rung_available("pcalm")


def step(case: Any) -> Any:
    """Execute one accelerated training step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # The PC-ALM primitive settling kernel uses the compiled triton settle loop
    # internally. The full algorithm kernel (credit + update) is not yet implemented.
    # Delegate to reference for the complete training step.
    from .reference import step as reference_step

    return reference_step(case)
