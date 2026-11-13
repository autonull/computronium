# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
# ruff: file-ignore[non-empty-init-module]
"""
Causal Transformer Geometry Primitive.

This primitive implements causal transformer language-model topology over token ids with a causal mask.

Reference implementation:
    computronium.primitives.geometry.causal_transformer.reference

Accelerated kernel:
    computronium.primitives.geometry.causal_transformer.kernel
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
