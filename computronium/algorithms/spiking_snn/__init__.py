# ruff: file-ignore[I001]
# ruff: file-ignore[INP001]
"""Spiking SNN algorithm.

Spike-timing-dependent plasticity with LIF dynamics. Wraps
computronium.core.presets.create_spiking_snn_mlp.

Reference implementation:
    computronium.algorithms.spiking_snn.reference

Accelerated kernel:
    computronium.algorithms.spiking_snn.kernel
"""

# Register the spec when this module is imported
from computronium.acceleration.registry import register as _register

from .cases import make_case
from .factory import create_spiking_snn_mlp
from .kernel import step as kernel_step
from .reference import step as reference_step
from .spec import SPEC

_register(SPEC)  # noqa: RUF067

__all__ = [
    "SPEC",
    "create_spiking_snn_mlp",
    "kernel_step",
    "make_case",
    "reference_step",
]
