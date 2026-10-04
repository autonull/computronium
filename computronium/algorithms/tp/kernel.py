"""Accelerated kernel for Target Propagation algorithm.

Uses Triton-accelerated TPKernelBackend when available.
Provides uniform `step(case)` interface.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch
from torch import nn

from computronium.acceleration.backends import kernel_available
from computronium.acceleration.kernel_backend import (
    AlgorithmFamily,
    HardwareTarget,
    KernelConfig,
    linear_views,
)
from computronium.acceleration.tp_kernels import (
    TRITON_IMPORTED_TP,
    TPKernelBackend,
)
from computronium.algorithms.tp.reference import _make_tp_system, _SystemConfig

if TYPE_CHECKING:
    from computronium.algorithms.tp.cases import Case
KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    """Check if Triton kernel is available."""
    return kernel_available(KERNEL_TECHNOLOGY) and TRITON_IMPORTED_TP


def _linear_view_to_linear(view) -> nn.Linear:
    """Convert a LinearView to an nn.Linear module sharing the same parameters."""
    linear = nn.Linear(view.in_features, view.out_features, bias=view.bias is not None)
    linear.weight = view.weight
    linear.bias = view.bias
    return linear


def step(case: Case) -> dict[str, float]:
    """
    Execute one accelerated step using the opaque case object.

    Uses Triton-accelerated TPKernelBackend when available.
    Replicates the reference's approach: creates a new system with the seed
    to ensure identical RNG state progression.
    """
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # Use the same approach as reference: create system with seed
    # to match RNG state progression exactly
    rng_state = torch.get_rng_state()
    seed = case.config.get("seed", 0)
    torch.manual_seed(seed)
    try:
        device_str = str(case.state.device)
        system_config = _SystemConfig(
            input_dim=case.state.shape[1],
            output_dim=case.config.get("output_dim", case.state.shape[1]),
            lr=case.config.get("lr", 1e-3),
            beta=case.config.get("beta", 0.1),
            settle_steps=case.config.get("settle_steps", 10),
            device=device_str,
        )
        system = _make_tp_system(system_config)

        # Now use the kernel backend with this system's geometry
        hardware = HardwareTarget.TRITON if device_str == "cuda" else HardwareTarget.CPU

        backend = TPKernelBackend()
        num_layers = len(system.geometry.params) // 2
        config = KernelConfig(
            algorithm=AlgorithmFamily.TP,
            hardware=hardware,
            dtype=case.state.dtype,
            extra={
                "num_layers": num_layers,
                "lr": case.config.get("lr", 1e-3),
                "beta": case.config.get("beta", 0.1),
                "activation": "tanh",
                "max_steps": case.config.get("settle_steps", 10),
                "step_size": 0.1,
                "convergence_threshold": 1e-4,
                "convergence_start": 5,
            },
        )
        backend.initialize(config)

        # Convert LinearViews to nn.Linear for TPKernelBackend compatibility
        views = list(linear_views(system.geometry))
        forward_layers = [_linear_view_to_linear(v) for v in views]

        backend.set_model_ref(
            forward_layers,
            activation=torch.nn.Tanh(),
        )

        target = case.target
        if target is None:
            target = torch.zeros(
                case.state.shape[0], dtype=torch.long, device=case.state.device
            )

        result = backend.train_step(case.state, target)
    finally:
        torch.set_rng_state(rng_state)

    return result
