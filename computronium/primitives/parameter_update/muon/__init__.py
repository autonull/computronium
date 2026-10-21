# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
# ruff: file-ignore[non-empty-init-module]
"""
Muon (Riemannian Orthogonal Update) primitive.

This primitive implements orthogonal parameter updates via Riemannian optimization
on the Stiefel manifold.

Reference implementation:
    computronium.primitives.parameter_update.muon.reference

Accelerated kernel:
    computronium.primitives.parameter_update.muon.kernel
"""

from computronium.acceleration.registry import register_module

globals().update(
    register_module(
        __name__,
        __doc__,
        has_factory=False,
    )
)
