"""Shared normalization utilities for credit and update rules."""

from __future__ import annotations

import torch
from torch import Tensor


def apply_norm(
    grads: list[Tensor],
    mode: str,
    refs: list[Tensor] | None = None,
) -> list[Tensor]:
    """Per-layer normalization of gradient-like tensors.

    Args:
        grads: List of gradient tensors to normalize
        mode: Normalization mode -- "none", "relative", "rms", "beta_adaptive", "spectral"
        refs: Optional reference tensors for relative/beta_adaptive modes

    Returns:
        Normalized gradients (same list structure, zeros stay zeros)
    """
    if mode == "none":
        return grads
    out: list[Tensor] = []
    for i, g in enumerate(grads):
        if not torch.isfinite(g).all():
            # Diverged gradient: pass through untouched (RiemannianOrthogonalUpdate precedent)
            out.append(g)
            continue
        if mode == "spectral":
            if g.ndim < 2:
                out.append(g)
                continue
            radius = torch.linalg.matrix_norm(g, ord=2)
            out.append(g / (radius + 1e-8) if radius > 0 else g)
        elif mode == "rms":
            rms = g.square().mean().sqrt()
            out.append(g / (rms + 1e-8) if rms > 0 else g)
        else:  # "relative" | "beta_adaptive"
            ref = refs[i] if refs is not None and i < len(refs) else None
            if ref is None:
                out.append(g)
                continue
            mag = ref.norm() if mode == "relative" else ref.square().mean().sqrt()
            out.append(g / (mag + 1e-8) if mag > 0 else g)
    return out


__all__ = ["apply_norm"]
