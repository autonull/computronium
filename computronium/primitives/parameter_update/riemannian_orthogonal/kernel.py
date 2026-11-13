"""Accelerated kernel for Riemannian Orthogonal Update.

Delegates to computronium.ontology.update.RiemannianOrthogonalUpdate; the update axis ships no
separate fused kernel, so the kernel rung resolves to the same code and the
spec stays ``reference_only`` (never auto-promoted).
"""

from typing import TYPE_CHECKING, Any

from computronium.acceleration.backends import kernel_available

if TYPE_CHECKING:
    import torch

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def step(case: Any) -> dict[str, torch.Tensor]:
    """Execute one step using the opaque case object."""
    from .reference import step as reference_step

    return reference_step(case)
