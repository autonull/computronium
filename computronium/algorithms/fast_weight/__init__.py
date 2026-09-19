# ruff: file-ignore[I001]
# ruff: file-ignore[INP001]
"""Fast-Weight algorithm (6-D joint).

Episode-local associative memory via FastWeightPlasticity. Wraps
computronium.core.presets.create_fast_weight_mlp.

Reference implementation:
    computronium.algorithms.fast_weight.reference

Accelerated kernel:
    computronium.algorithms.fast_weight.kernel
"""

# Register the spec when this module is imported
from computronium.acceleration.registry import register as _register

from .cases import make_case
from .factory import create_fast_weight_mlp
from .kernel import step as kernel_step
from .reference import step as reference_step
from .spec import SPEC

_register(SPEC)  # noqa: RUF067

__all__ = [
    "SPEC",
    "create_fast_weight_mlp",
    "kernel_step",
    "make_case",
    "reference_step",
]
