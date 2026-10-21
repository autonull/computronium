# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
# ruff: file-ignore[non-empty-init-module]
"""
PEPITA Credit Assignment primitive.

This primitive implements the published PEPITA rule (Dellaferrera & Kreiman 2022,
arXiv 2201.11665): input-modulated second forward pass with exact autograd gradient.

Reference implementation:
    computronium.primitives.credit_assignment.pepita.reference

Accelerated kernel:
    computronium.primitives.credit_assignment.pepita.kernel
"""

from computronium.acceleration.registry import register_module

globals().update(
    register_module(
        __name__,
        __doc__,
        has_factory=False,
    )
)
