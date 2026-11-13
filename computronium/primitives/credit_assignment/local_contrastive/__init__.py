# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
# ruff: file-ignore[non-empty-init-module]
"""
Local Contrastive Credit Primitive.

This primitive implements per-layer recomputed goodness contrast read from a label-augmented input channel.

Reference implementation:
    computronium.primitives.credit_assignment.local_contrastive.reference

Accelerated kernel:
    computronium.primitives.credit_assignment.local_contrastive.kernel
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
