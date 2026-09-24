"""
Muon (Riemannian Orthogonal Update) primitive.

This primitive implements orthogonal parameter updates via Riemannian optimization
on the Stiefel manifold.

Reference implementation:
    computronium.primitives.parameter_update.muon.reference

Accelerated kernel:
    computronium.primitives.parameter_update.muon.kernel
"""

from computronium.acceleration.registry import register

from .cases import make_case
from .kernel import step as kernel_step
from .reference import step as reference_step
from .spec import SPEC

register(SPEC)  # ruff: ignore[non-empty-init-module] (registration side effect required)

__all__ = [
    "SPEC",
    "kernel_step",
    "make_case",
    "reference_step",
]
