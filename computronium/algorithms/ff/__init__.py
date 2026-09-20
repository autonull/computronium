# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
"""Forward-Forward (FF) algorithm.

Layer-local goodness objective with two forward passes. Wraps
computronium.core.presets.create_ff_mlp.

Reference implementation:
    computronium.algorithms.ff.reference

Accelerated kernel:
    computronium.algorithms.ff.kernel
"""

# Register the spec when this module is imported
from computronium.acceleration.registry import register as _register

from .cases import make_case
from .factory import create_ff_mlp
from .kernel import step as kernel_step
from .reference import step as reference_step
from .spec import SPEC

_register(SPEC)  # noqa: RUF067

__all__ = [
    "SPEC",
    "create_ff_mlp",
    "kernel_step",
    "make_case",
    "reference_step",
]
