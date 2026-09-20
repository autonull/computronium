"""Accelerated kernel for Local Goodness Credit Assignment (Triton rung).

Supports both FF (Forward-Forward) and LEMMA modes.
- FF mode: Uses autograd of layer-local goodness contrast (requires autograd graph)
- LEMMA mode: Closed-form fixed random projections (Triton-acceleratable)

Note: Credit assignment primitives compute pseudo-gradients via autograd.
torch.compile rung is NOT applicable for FF mode (breaks autograd graph).
LEMMA mode can use Triton directly.
Kernel ladder: reference → Triton (for LEMMA mode).
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


def _init_feedback_weights(
    weights: list[torch.Tensor],
    out_dim: int,
    feedback_scale: float,
    orthogonal_init: bool,
    seed: int,
) -> list[torch.Tensor]:
    """Initialize deterministic feedback weights matching reference's zlib.crc32 seed."""
    import zlib

    feedback_weights = []
    for i, w in enumerate(weights):
        layer_name = f"{i}.weight"
        layer_seed = zlib.crc32(layer_name.encode())
        layer_output_dim = w.shape[0]
        fb = torch.empty(out_dim, layer_output_dim, device=w.device, dtype=w.dtype)
        if orthogonal_init:
            torch.nn.init.orthogonal_(
                fb, generator=torch.Generator(device=w.device).manual_seed(layer_seed)
            )
        else:
            fb.normal_(generator=torch.Generator(device=w.device).manual_seed(layer_seed))
        fb *= feedback_scale
        feedback_weights.append(fb)
    return feedback_weights


def _build_covariate_stream(
    free_activations: list[torch.Tensor],
    nudged_activations: list[torch.Tensor],
) -> tuple[list[torch.Tensor], int]:
    """Build covariate stream matching reference's _pepita_covariate_stream."""
    stream = list(nudged_activations)
    x_in = free_activations[0]
    if stream and x_in.shape[-1] != stream[0].shape[-1]:
        stream.insert(0, x_in)
    offset = len(stream) - len(nudged_activations)
    return stream, offset


def _lemma_backward_triton(  # noqa: PLR0914
    free_activations: list[torch.Tensor],
    nudged_activations: list[torch.Tensor],
    weights: list[torch.Tensor],
    config: dict[str, Any],
    target: torch.Tensor,
) -> list[torch.Tensor] | None:
    """Triton-accelerated LEMMA backward pass."""
    num_layers = len(weights)
    if num_layers != len(free_activations) - 1:
        return None  # Fallback to reference

    batch = free_activations[0].shape[0]
    out_dim = free_activations[-1].shape[-1]

    # Compute e1 = one_hot(y) - softmax(free_out)
    free_out = free_activations[-1].detach()
    y_onehot = torch.nn.functional.one_hot(target, out_dim).to(free_out.dtype)
    softmax_out = torch.softmax(free_out, dim=-1)
    e1 = (y_onehot - softmax_out).detach()

    # Initialize deterministic feedback weights
    feedback_scale = config.get("feedback_scale", 1.0)
    orthogonal_init = config.get("orthogonal_init", True)
    learned_feedback = config.get("learned_feedback", False)

    if learned_feedback:
        return None  # Fallback to reference

    feedback_weights = _init_feedback_weights(
        weights, out_dim, feedback_scale, orthogonal_init, config.get("seed", 0)
    )

    # Build covariate stream
    stream, offset = _build_covariate_stream(free_activations, nudged_activations)

    # PEPITA/LEMMA gradient computation
    credit_norm = config.get("credit_norm", "rms")

    grads = []
    cursor = 0
    for k, w in enumerate(weights):
        # Find matching covariate in stream
        c = None
        for c_idx in range(cursor, len(stream)):
            if stream[c_idx].shape[-1] == w.shape[1]:
                c = c_idx
                break
        if c is None or k >= num_layers:
            grads.append(torch.zeros_like(w))
            continue
        cursor = c + 1

        # Reference covariate for credit_norm
        ref_idx = c - offset
        ref = free_activations[ref_idx] if 0 <= ref_idx < len(free_activations) else None

        # Project e1 through feedback matrix: err = e1 @ B
        B = feedback_weights[k]
        if HAS_TRITON_FA and e1.is_cuda:
            err = fa_feedback_projection_notrans_triton(e1, B)
        else:
            err = e1 @ B

        # Apply credit norm
        err = _apply_credit_norm([err], credit_norm, [ref] if ref is not None else None)[0]

        # Gradient: -(err.T @ stream[c]) / batch
        if HAS_TRITON_FA and err.is_cuda:
            wgrad = fa_batched_outer_triton(stream[c], err)
        else:
            wgrad = (err.T @ stream[c]) / batch
        grads.append(-wgrad)

    return grads


def step(case: Any) -> list[Any]:
    """Execute one accelerated step."""
    local_objective = case.config.get("local_objective", "ff")

    # FF mode uses autograd - not easily Triton-acceleratable
    # Delegate to reference for now
    if local_objective == "ff":
        from .reference import step as reference_step
        return reference_step(case)

    # LEMMA mode: Triton acceleration possible
    if not is_available():
        from .reference import step as reference_step
        return reference_step(case)

    # Extract data from case
    weights = case.weights
    free_activations = case.free_activations
    nudged_activations = case.nudged_activations
    config = case.config
    target = config.get("target")

    if target is None:
        from .reference import step as reference_step
        return reference_step(case)

    # Try Triton-accelerated LEMMA backward
    grads = _lemma_backward_triton(
        free_activations=free_activations,
        nudged_activations=nudged_activations,
        weights=weights,
        config=config,
        target=target,
    )

    if grads is None:
        from .reference import step as reference_step
        return reference_step(case)

    return grads
