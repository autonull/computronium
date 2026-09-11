"""Tensor-in/tensor-out spectral-norm power iteration (TODO21 T21.3A.2).

Canonical kernel for warm-started power iteration on the largest singular
value. Internal call sites (Lipschitz audits, spectral constraints,
contrastive spectral normalization) route here; the CUDA kernel in
``computronium.mep.cuda.kernels`` and the NumPy/CuPy path in
``core.utils.activations`` remain device-special exceptions.
"""

from __future__ import annotations

import torch
from torch import Tensor

__all__ = ["spectral_norm_power_iteration", "spectral_normalized_weight"]


def spectral_norm_power_iteration(
    W: Tensor,
    u: Tensor | None = None,
    v: Tensor | None = None,
    num_iters: int = 10,
    eps: float = 1e-12,
) -> tuple[Tensor, Tensor, Tensor]:
    """Estimate the largest singular value of ``W`` by power iteration.

    Args:
        W: Weight tensor; flattened to ``[out, in]`` across leading dims.
        u: Warm-start left vector (``[out]``).
        v: Warm-start right vector (``[in]``).
        num_iters: Power-iteration steps.
        eps: Normalization floor for stability on zero matrices.

    Returns:
        ``(sigma, u, v)`` with ``sigma`` a 0-D tensor and warm-started
        unit vectors suitable for the next call.
    """
    w_mat = W.view(W.shape[0], -1)
    if u is None:
        u_init = torch.randn(w_mat.shape[0], device=W.device, dtype=W.dtype)
        u = u_init / (u_init.norm() + eps)
    if v is None:
        v_init = torch.randn(w_mat.shape[1], device=W.device, dtype=W.dtype)
        v = v_init / (v_init.norm() + eps)
    u_cur, v_cur = u, v
    for _ in range(num_iters):
        v_new = w_mat.T @ u_cur
        v_cur = v_new / (v_new.norm() + eps)
        u_new = w_mat @ v_cur
        u_cur = u_new / (u_new.norm() + eps)
    sigma = (u_cur @ w_mat @ v_cur).abs()
    return sigma, u_cur, v_cur


def spectral_normalized_weight(
    W: Tensor,
    u: Tensor | None = None,
    num_iters: int = 1,
) -> tuple[Tensor, Tensor, Tensor]:
    """Return ``(W / sigma_max, u, sigma)`` for spectral normalization."""
    sigma, u, _v = spectral_norm_power_iteration(W, u=u, num_iters=num_iters)
    return W / sigma, u, sigma
