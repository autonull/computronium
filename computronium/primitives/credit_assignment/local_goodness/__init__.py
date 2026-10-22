# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
# ruff: file-ignore[non-empty-init-module]
"""
Local Goodness Credit Assignment primitive.

This primitive implements layer-local contrastive credit assignment with
two variants:
- Forward-Forward (local_objective="ff"): autograd of goodness contrast
- LEMMA (local_objective="lemma"): closed-form fixed/learned feedback

Reference implementation:
    computronium.primitives.credit_assignment.local_goodness.reference

Accelerated kernel:
    computronium.primitives.credit_assignment.local_goodness.kernel
"""

from computronium.acceleration.registry import register_module

globals().update(
    register_module(
        __name__,
        __doc__ or "",
        has_factory=False,
    )
)
