"""Accelerated kernel for Random Projections Credit (Triton rung).

Delegates to computronium.acceleration.fa_kernels for Triton-accelerated
FA backward pass. Provides uniform `step(case)` interface.

Note: Credit assignment primitives compute pseudo-gradients via autograd.
torch.compile rung is NOT applicable (breaks autograd graph).
Kernel ladder: reference → Triton (custom FA kernel).
"""

from typing import Any

import torch

from computronium.acceleration.backends import kernel_available
from computronium.acceleration.fa_kernels import (
    HAS_TRITON_FA,
    fa_batched_outer_triton,
    fa_feedback_projection_notrans_triton,
)
from computronium.ontology.credit import _apply_credit_norm

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY) and HAS_TRITON_FA


def step(case: Any) -> list[Any]:  # ruff: ignore[too-many-locals]
    """Execute one accelerated step using Triton-accelerated FA backward pass."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # Extract data from case
    nudged_activations = case.nudged_activations
    geometry = case.geometry
    config = case.config
    seed = config.get("seed", 0)
    feedback_scale = config.get("feedback_scale", 0.1)

    # Get weights from geometry to determine layer dimensions
    weight_names = [
        k
        for k in geometry.params
        if "weight" in k.lower() and geometry.params[k].ndim == 2
    ]
    if not weight_names:
        from .reference import step as reference_step

        return reference_step(case)

    # Initialize deterministic feedback weights (same as RandomProjectionsCredit)
    torch.manual_seed(seed)
    feedback_weights = []
    for name in weight_names:
        param = geometry.params[name]
        fb = torch.randn_like(param) * feedback_scale
        feedback_weights.append(fb)

    # Compute output error via autograd (same as reference)
    # Loss is MSE against zero target
    nudged_output = nudged_activations[-1]
    target = torch.zeros_like(nudged_output)
    loss = torch.nn.functional.mse_loss(nudged_output, target)

    # Preserve RNG state
    rng_state = torch.get_rng_state()
    torch.manual_seed(seed)
    try:
        output_error = torch.autograd.grad(loss, nudged_output, retain_graph=False)[
            0
        ].detach()
    finally:
        torch.set_rng_state(rng_state)

    # Run Triton-accelerated FA backward pass (without activation derivative)
    num_layers = len(feedback_weights)
    if num_layers != len(nudged_activations) - 1:
        from .reference import step as reference_step

        return reference_step(case)

    batch = nudged_activations[0].shape[0]

    # Apply credit norm to output error (RandomProjectionsCredit uses "none" by default)
    credit_norm = "none"
    err = _apply_credit_norm([output_error], credit_norm)[0]

    weight_grads = []

    for i in range(num_layers - 1, -1, -1):
        h_prev = nudged_activations[i]

        # Weight gradient: err.T @ h_prev / batch
        if HAS_TRITON_FA and err.is_cuda:
            wgrad = fa_batched_outer_triton(h_prev, err)
        else:
            wgrad = (err.T @ h_prev) / batch
        weight_grads.append(wgrad)

        # Propagate error to previous layer (no activation derivative for RandomProjectionsCredit)
        # Reference uses: err = err @ B (not B.T)
        if i > 0:
            B = feedback_weights[i]
            if HAS_TRITON_FA and err.is_cuda:
                err = fa_feedback_projection_notrans_triton(err, B)
            else:
                err @= B

            # Apply credit norm only (no activation derivative)
            err = _apply_credit_norm([err], credit_norm, [h_prev])[0]

    weight_grads.reverse()
    return weight_grads
