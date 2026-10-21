# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
# ruff: file-ignore[non-empty-init-module]
"""
Null Plasticity Primitive.

This primitive implements the zero-extension identity for plasticity:
ψ_{t+1} = ψ_t — makes 5-D systems valid 6-D coordinates.

Reference implementation:
    computronium.primitives.plasticity.null.reference

Accelerated kernel:
    computronium.primitives.plasticity.null.kernel
"""

from computronium.acceleration.registry import register_module

globals().update(
    register_module(
        __name__,
        __doc__,
        has_factory=False,
    )
)
