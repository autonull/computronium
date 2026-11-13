"""Accelerated kernel for Causal Transformer Geometry.

No separate fused kernel exists for causal_transformer; the kernel rung resolves to the
reference rung and the spec stays ``reference_only``.
"""

from typing import Any

from computronium.acceleration.backends import kernel_available

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def forward(case: Any) -> Any:
    """Execute one forward pass using the opaque case object."""
    from .reference import forward as reference_forward

    return reference_forward(case)


step = forward
