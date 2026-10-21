# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
# ruff: file-ignore[non-empty-init-module]
"""
Thermodynamic Contrast Credit Primitive.

This primitive implements Equilibrium Propagation contrastive credit assignment
using the free/nudged phase difference.

Reference implementation:
    computronium.primitives.credit_assignment.thermodynamic_contrast.reference

Accelerated kernel:
    computronium.primitives.credit_assignment.thermodynamic_contrast.kernel
"""

from computronium.acceleration.registry import register_module

globals().update(
    register_module(
        __name__,
        __doc__,
        has_factory=False,
    )
)
