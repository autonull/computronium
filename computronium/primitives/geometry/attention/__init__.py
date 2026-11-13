# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
# ruff: file-ignore[non-empty-init-module]
"""
Attention Geometry Primitive.

This primitive implements multi-head self-attention blocks with residual connections and layer norm.

Reference implementation:
    computronium.primitives.geometry.attention.reference

Accelerated kernel:
    computronium.primitives.geometry.attention.kernel
"""

from computronium.acceleration.registry import register_module

globals().update(
    register_module(
        __name__,
        __doc__,
        has_factory=False,
        kernel_fn="step",
        reference_fn="step",
    )
)
