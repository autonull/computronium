# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
"""PEPITA algorithm.

Published PEPITA with fixed random B and error-modulated second forward pass. Wraps
computronium.core.presets.create_pepita_mlp.

Reference implementation:
    computronium.algorithms.pepita.reference

Accelerated kernel:
    computronium.algorithms.pepita.kernel
"""

# Register the spec when this module is imported
from computronium.acceleration.registry import register as _register

from .cases import make_case
from .factory import create_pepita_mlp
from .kernel import step as kernel_step
from .reference import step as reference_step
from .spec import SPEC

_register(SPEC)  # noqa: RUF067

__all__ = [
    "SPEC",
    "create_pepita_mlp",
    "kernel_step",
    "make_case",
    "reference_step",
]
