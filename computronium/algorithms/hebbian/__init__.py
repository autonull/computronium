# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
"""Hebbian/STDP algorithm.

Local correlation-based plasticity. Wraps
computronium.core.presets.create_hebbian_mlp.

Reference implementation:
    computronium.algorithms.hebbian.reference

Accelerated kernel:
    computronium.algorithms.hebbian.kernel
"""

# Register the spec when this module is imported
from computronium.acceleration.registry import register as _register

from .cases import make_case
from .factory import create_hebbian_mlp
from .kernel import step as kernel_step
from .reference import step as reference_step
from .spec import SPEC

_register(SPEC)  # ruff: ignore[non-empty-init-module]

__all__ = [
    "SPEC",
    "create_hebbian_mlp",
    "kernel_step",
    "make_case",
    "reference_step",
]
