"""Low-level Jacobian spectral analysis for raw tensor transitions.

This module provides Jacobian-based stability metrics that work with simple
tensor-to-tensor transition functions, independent of the joint architecture
types (CompositeState, SystemContext). Suitable for both 5-D and 6-D systems.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, cast

import torch
from torch import Tensor

if TYPE_CHECKING:
    from collections.abc import Callable


_RADIUS_FLOOR: float = 1e-10


def _full_jacobian_tensor(
    step_fn: Callable[[Tensor], Tensor],
    x: Tensor,
) -> Tensor:
    """Exact Jacobian of a tensor-to-tensor function via autograd."""
    x = x.clone().requires_grad_(True)
    jac = cast("Tensor", torch.autograd.functional.jacobian(step_fn, x))
    if jac.dim() == 4:
        # per-sample slice of batched jacobian
        jac = jac[0, :, 0, :]
    return jac


def spectral_radius_from_jacobian_tensor(
    step_fn: Callable[[Tensor], Tensor],
    x: Tensor,
) -> float:
    """Exact ρ(J) = max |λ_i(J)| via autograd Jacobian + eigenvalues.

    This is the asymptotic stability margin — for nonnormal J it is strictly
    smaller than σ_max(J). Small systems only (O(d³) eigendecomposition).

    Args:
        step_fn: Transition function h -> h_next
        x: Point at which to evaluate Jacobian

    Returns:
        Spectral radius ρ(J)
    """
    jac = _full_jacobian_tensor(step_fn, x)
    return float(torch.linalg.eigvals(jac).abs().max().item())


def dominant_singular_value_tensor(
    step_fn: Callable[[Tensor], Tensor],
    x: Tensor,
) -> float:
    """Exact σ_max(J) via autograd Jacobian + SVD (expensive; validation only).

    This is the transient amplification bound ‖J‖_2 — distinct from ρ(J).

    Args:
        step_fn: Transition function h -> h_next
        x: Point at which to evaluate Jacobian

    Returns:
        Maximum singular value σ_max(J)
    """
    jac = _full_jacobian_tensor(step_fn, x)
    _u, s, _vh = torch.linalg.svd(jac)
    return float(s[0].item())


def jacobian_spectral_metrics(
    step_fn: Callable[[Tensor], Tensor],
    x: Tensor,
    *,
    compute_min_singular: bool = True,
    use_lowrank_for_large: bool = True,
    lowrank_k: int = 16,
    lowrank_niter: int = 2,
) -> dict[str, float]:
    """Compute full spectral metrics from a step function and point.

    Computes:
    - spectral_radius: ρ(J) — asymptotic stability margin
    - max_singular_value: σ_max(J) — transient amplification bound
    - min_singular_value: σ_min(J) — condition-number floor
    - lyapunov_exponent: ln ρ(J)
    - stability_margin: 1 - ρ(J)
    - nonnormality: σ_max / ρ(J)

    For large matrices (>512), uses randomized SVD (svd_lowrank) for speed.

    Args:
        step_fn: Transition function h -> h_next
        x: Point at which to evaluate Jacobian
        compute_min_singular: Whether to compute σ_min (requires full SVD)
        use_lowrank_for_large: Use svd_lowrank for large matrices
        lowrank_k: Number of singular values for lowrank SVD
        lowrank_niter: Iterations for lowrank SVD

    Returns:
        Dictionary of spectral metrics
    """
    metrics: dict[str, float] = {}

    jac = _full_jacobian_tensor(step_fn, x)

    # Use randomized SVD for large matrices
    if use_lowrank_for_large and (jac.shape[0] > 512 or jac.shape[1] > 512):
        k = min(lowrank_k, *jac.shape)
        _u, s, _vh = torch.svd_lowrank(jac, q=k, niter=lowrank_niter)
        singular = s
    else:
        singular = torch.linalg.svdvals(jac)

    sigma_max = float(singular.max().item())
    sigma_min = float(singular.min().item()) if compute_min_singular else 0.0
    radius = spectral_radius_from_jacobian_tensor(step_fn, x)

    metrics["spectral_radius"] = radius
    metrics["max_singular_value"] = sigma_max
    metrics["min_singular_value"] = sigma_min
    metrics["lyapunov_exponent"] = math.log(max(radius, _RADIUS_FLOOR))
    metrics["stability_margin"] = 1.0 - radius
    metrics["nonnormality"] = sigma_max / max(radius, _RADIUS_FLOOR)

    return metrics


def drift_metrics(
    step_fn: Callable[[Tensor], Tensor],
    x: Tensor,
    step_size: float,
) -> dict[str, float]:
    """Compute drift operator metrics: D = (J - I) / η.

    The drift operator f(h) - h captures the network's own gain with step size
    removed. A relaxation step is h <- h + η * (f(h) - h), so J = I + η * D.

    Args:
        step_fn: Transition function h -> h_next
        x: Point at which to evaluate Jacobian
        step_size: Step size η used in the relaxation

    Returns:
        Dictionary with drift spectral radius, max singular value, nonnormality,
        step size, and predicted contraction rate (1 - η * ρ(D))
    """
    if step_size <= 0:
        return {}

    jac = _full_jacobian_tensor(step_fn, x)
    eye = torch.eye(jac.shape[0], device=jac.device, dtype=jac.dtype)
    drift = (jac - eye) / step_size

    singular = torch.linalg.svdvals(drift)
    sigma_max = float(singular.max().item())
    radius = float(torch.linalg.eigvals(drift).abs().max().item())

    return {
        "drift_spectral_radius": radius,
        "drift_max_singular_value": sigma_max,
        "drift_nonnormality": sigma_max / max(radius, _RADIUS_FLOOR),
        "settle_step_size": step_size,
        "contraction_rate": 1.0 - step_size * radius,
    }


__all__ = [
    "dominant_singular_value_tensor",
    "drift_metrics",
    "jacobian_spectral_metrics",
    "spectral_radius_from_jacobian_tensor",
]
