# ruff: file-ignore: [PLC0415, INP001]
"""Direct Feedback Alignment algorithm.

Composes primitives into a named method. Wraps
computronium.core.presets.create_fa_mlp for Direct Feedback Alignment.

Reference implementation:
    computronium.algorithms.dfa.reference

Accelerated kernel:
    computronium.algorithms.dfa.kernel
"""

# Register the spec when this module is imported
from computronium.acceleration.registry import register as _register

from .cases import make_case
from .factory import create_dfa_mlp
from .kernel import step as kernel_step
from .reference import step as reference_step
from .spec import SPEC

_register(SPEC)  # ruff: ignore[non-empty-init-module]

__all__ = [
    "SPEC",
    "create_dfa_mlp",
    "kernel_step",
    "make_case",
    "reference_step",
]
