# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
# ruff: file-ignore[non-empty-init-module]
"""
Hybrid Credit Assignment primitive (TODO93 T3b).

Lockstep-local trunk with an exact-gradient head: the trunk's two-pass local
rule keeps one layer's two chains live, and the head's 2-layer autograd graph
is the only stored activation set.

Reference implementation:
    computronium.primitives.credit_assignment.hybrid.reference

Accelerated kernel:
    computronium.primitives.credit_assignment.hybrid.kernel
"""

from computronium.acceleration.registry import register_module

globals().update(
    register_module(
        __name__,
        __doc__ or "",
        has_factory=False,
    )
)
