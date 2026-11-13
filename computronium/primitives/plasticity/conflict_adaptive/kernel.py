"""Accelerated kernel for Conflict-Adaptive Plasticity.

Delegates to computronium.core.plasticity.adaptive_psi.ConflictAdaptivePsiPlasticity;
no separate fused kernel exists, so the kernel rung resolves to the same
code and the spec stays ``reference_only``.
"""

from typing import Any

from computronium.acceleration.backends import kernel_available

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def step(case: Any) -> Any:
    """Execute one step using the opaque case object."""
    from .reference import step as reference_step

    return reference_step(case)
