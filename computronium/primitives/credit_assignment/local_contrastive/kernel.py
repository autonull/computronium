"""Accelerated kernel for Local Contrastive Credit.

No separate fused kernel exists: the credit builds each layer's graph itself,
so the kernel rung resolves to the reference rung and the spec stays
``reference_only``.
"""

from typing import Any

from computronium.acceleration.backends import kernel_available

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def step(case: Any) -> list:
    """Execute one step using the opaque case object."""
    from .reference import step as reference_step

    return reference_step(case)
