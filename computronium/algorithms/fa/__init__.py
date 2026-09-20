# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
"""Feedback Alignment (FA) algorithm.

Fixed random feedback weights for credit assignment. Wraps
computronium.core.presets.create_fa_mlp.

Reference implementation:
    computronium.algorithms.fa.reference

Accelerated kernel:
    computronium.algorithms.fa.kernel
"""

# Register the spec when this module is imported
from computronium.acceleration.registry import register as _register

from .cases import make_case
from .factory import create_fa_mlp
from .kernel import step as kernel_step
from .reference import step as reference_step
from .spec import SPEC

_register(SPEC)  # ruff: ignore[non-empty-init-module]

__all__ = [
    "SPEC",
    "create_fa_mlp",
    "kernel_step",
    "make_case",
    "reference_step",
]
