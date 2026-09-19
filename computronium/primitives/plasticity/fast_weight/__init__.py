# ruff: file-ignore[import-outside-top-level]
# ruff: file-ignore[implicit-namespace-package]
"""Fast Weight Plasticity primitive.

This primitive implements episode-local associative memory via Hebbian
outer-product with random projection.

Reference implementation:
    computronium.primitives.plasticity.fast_weight.reference

Accelerated kernel:
    computronium.primitives.plasticity.fast_weight.kernel
"""

# Register the spec when this module is imported
from computronium.acceleration.registry import register as _register

from .cases import make_case
from .kernel import step as kernel_step
from .reference import step as reference_step
from .spec import SPEC

_register(SPEC)  # ruff: ignore[non-empty-init-module]

__all__ = [
    "SPEC",
    "kernel_step",
    "make_case",
    "reference_step",
]
