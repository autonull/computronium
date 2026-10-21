"""Accelerated kernel for Direct Feedback Alignment algorithm.

Uses Triton-accelerated DFAKernelBackend when available.
Provides uniform `step(case)` interface.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from computronium.acceleration.backends import kernel_available
from computronium.acceleration.dfa_kernels import (
    TRITON_IMPORTED_DFA,
    DFAKernelBackend,
)
from computronium.acceleration.kernel_backend import (
    AlgorithmFamily,
    HardwareTarget,
    KernelConfig,
    linear_views,
)
from computronium.algorithms.dfa.reference import build_system
from computronium.harness import seeded_rng

if TYPE_CHECKING:
    from computronium.algorithms.dfa.cases import Case

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    """Check if Triton kernel is available."""
    return kernel_available(KERNEL_TECHNOLOGY) and TRITON_IMPORTED_DFA


def step(case: Case) -> dict[str, float]:
    """
    Execute one accelerated step using the opaque case object.

    Uses Triton-accelerated DFAKernelBackend when available.
    Replicates the reference's approach: creates a new system with the seed
    to ensure identical RNG state progression.
    """
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # Use the same approach as reference: create system with seed
    # to match RNG state progression exactly
    with seeded_rng(case.config.get("seed", 0)):
        system = build_system(case)

        # Now use the kernel backend with this system's geometry
        device_str = str(case.state.device)
        hardware = HardwareTarget.TRITON if device_str == "cuda" else HardwareTarget.CPU

        backend = DFAKernelBackend()
        num_layers = len(system.geometry.params) // 2
        config = KernelConfig(
            algorithm=AlgorithmFamily.FA,
            hardware=hardware,
            dtype=case.state.dtype,
            extra={
                "num_layers": num_layers,
                "lr": case.config.get("lr", 1e-3),
                "feedback_scale": case.config.get("feedback_scale", 0.01),
                "activation": "relu",
                "hidden_dim": 4,
                "input_dim": case.state.shape[1],
                "output_dim": case.config.get("output_dim", 4),
                "beta": 0.1,  # Match InstantaneousDynamics beta=0.1
            },
        )
        backend.initialize(config)
        backend.set_model_ref(
            list(linear_views(system.geometry)),
            activation=torch.nn.ReLU(),
            feedback_scale=case.config.get("feedback_scale", 0.01),
        )

        target = case.target
        if target is None:
            target = torch.zeros(
                case.state.shape[0], dtype=torch.long, device=case.state.device
            )

        result = backend.train_step(case.state, target)

    return result
