# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
"""HolomorphicEp algorithm.

Holomorphic Equilibrium Propagation with complex-valued dynamics

Reference implementation:
    computronium.algorithms.holomorphic_ep.reference

Accelerated kernel:
    computronium.algorithms.holomorphic_ep.kernel
"""

# Register the spec when this module is imported
from computronium.acceleration.registry import register as _register

from .cases import make_case
from .factory import create_holomorphic_ep_mlp
from .kernel import step as kernel_step
from .reference import step as reference_step
from .spec import SPEC

_register(SPEC)  # noqa: RUF067

__all__ = [
    "SPEC",
    "create_holomorphic_ep_mlp",
    "kernel_step",
    "make_case",
    "reference_step",
]
