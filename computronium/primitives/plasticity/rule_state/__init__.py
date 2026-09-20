# ruff: file-ignore[import-outside-top-level]
# ruff: file-ignore[implicit-namespace-package]
"""Rule State primitive.

This primitive implements the rule state plasticity (z3): frozen-θ algorithm switching via ψ

Reference implementation:
    computronium.primitives.plasticity.rule_state.reference

Accelerated kernel:
    computronium.primitives.plasticity.rule_state.kernel
"""

# Register the spec when this module is imported
from computronium.acceleration.registry import register as _register

from .cases import make_case
from .kernel import is_available
from .kernel import step as kernel_step
from .reference import step as reference_step
from .spec import SPEC

_register(SPEC)  # ruff: ignore[non-empty-init-module]

__all__ = [
    "SPEC",
    "is_available",
    "kernel_step",
    "make_case",
    "reference_step",
]
