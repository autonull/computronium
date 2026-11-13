# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
# ruff: file-ignore[non-empty-init-module]
"""
Convolutional Geometry Primitive.

This primitive implements shared convolutional kernels applied to im2col patches, routed through the substrate operator.

Reference implementation:
    computronium.primitives.geometry.conv.reference

Accelerated kernel:
    computronium.primitives.geometry.conv.kernel
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
