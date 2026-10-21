# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
# ruff: file-ignore[non-empty-init-module]
"""Feedback Alignment (FA) algorithm.

Fixed random feedback weights for credit assignment. Wraps
computronium.core.presets.create_fa_mlp.

Reference implementation:
    computronium.algorithms.fa.reference

Accelerated kernel:
    computronium.algorithms.fa.kernel
"""

from computronium.acceleration.registry import register_module

globals().update(
    register_module(
        __name__,
        __doc__,
        has_factory=True,
        factory_name="create_fa_mlp",
    )
)
