"""Jacobian gain metrics: σ_max(J) and ρ(J) are mathematically distinct.

The finite-difference power-iteration estimator measures *directional
amplification* — ‖Jv‖ along the direction the iteration converges to. For
normal J (symmetric, diagonal) this equals both σ_max(J) and ρ(J). For
nonnormal J (e.g. Jordan blocks) the iteration aligns with the dominant
*eigenvector*, so it converges to ρ(J)-like eigenvalue magnitudes and does
NOT certify σ_max(J) ≫ ρ(J) transients. Use :func:`dominant_singular_value`
and :func:`spectral_radius_from_jacobian` for exact, separated metrics
(TODO18 2.1).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

import torch
from torch import Tensor

from stability.state import CompositeState

if TYPE_CHECKING:
    from collections.abc import Callable

    from stability.state import SystemContext

_ACTIVITY_TYPE_MSG = "activity[{key!r}] must be a Tensor, got {type}"


def _activity_tensor(z: CompositeState, key: str) -> Tensor:
    """Narrow an activity slot to its Tensor (numeric scalars unsupported)."""
    value = z.activity[key]
    if not isinstance(value, Tensor):
        raise TypeError(_ACTIVITY_TYPE_MSG.format(key=key, type=type(value).__name__))
    return value


def estimate_directional_amplification(
    transition_fn: Callable[[CompositeState, SystemContext], CompositeState],
    z: CompositeState,
    context: SystemContext,
    num_iterations: int = 20,
    perturbation_scale: float = 1e-4,
    activity_key: str = "x",
) -> float:
    """Estimate directional amplification ‖Jv‖ of the transition Jacobian.

    Power iteration on J·v (finite-difference JVP) converges to the dominant
    eigen-direction: ρ(J)-like magnitude for diagonalizable nonnormal J,
    σ_max(J) only for normal J. This is neither a certified spectral radius
    nor a certified operator norm — report it as a sampled estimate only.

    Args:
        transition_fn: Joint transition function F_θ(z; G, S, M).
        z: Base joint state to evaluate Jacobian at.
        context: System context with fixed parameters.
        num_iterations: Number of power iterations.
        perturbation_scale: Scale for finite-difference perturbations.
        activity_key: Key in z.activity to perturb (default: "x").

    Returns:
        Estimated σ_max(J_F) (operator-norm amplification).
    """
    x_base = _activity_tensor(z, activity_key)

    v = torch.randn_like(x_base)
    v /= v.norm(dim=-1, keepdim=True) + 1e-8

    for _ in range(num_iterations):
        x_perturbed = x_base + perturbation_scale * v
        z_perturbed = CompositeState(
            activity={**z.activity, activity_key: x_perturbed},
            plastic=z.plastic,
            substrate=z.substrate,
        )
        with torch.no_grad():
            z_next_base = transition_fn(z, context)
            z_next_perturbed = transition_fn(z_perturbed, context)
        delta = _activity_tensor(z_next_perturbed, activity_key) - _activity_tensor(
            z_next_base, activity_key
        )
        Jv = delta / perturbation_scale
        v = Jv / (Jv.norm(dim=-1, keepdim=True) + 1e-8)

    x_perturbed = x_base + perturbation_scale * v
    z_perturbed = CompositeState(
        activity={**z.activity, activity_key: x_perturbed},
        plastic=z.plastic,
        substrate=z.substrate,
    )
    with torch.no_grad():
        z_next_base = transition_fn(z, context)
        z_next_perturbed = transition_fn(z_perturbed, context)
    delta = _activity_tensor(z_next_perturbed, activity_key) - _activity_tensor(
        z_next_base, activity_key
    )
    Jv = delta / perturbation_scale

    return Jv.norm(dim=-1).mean().item()


@dataclass(slots=True)
class JacobianAmplificationEstimator:
    """Configurable Jacobian-amplification estimator for joint transitions.

    ``full`` mode runs power iteration on the JVP (σ_max estimate);
    ``fast_mode`` uses a single-step norm-ratio proxy (1 iteration).
    """

    num_iterations: int = 20
    perturbation_scale: float = 1e-4
    activity_key: str = "x"
    fast_mode: bool = False

    def __call__(
        self,
        transition_fn: Callable[[CompositeState, SystemContext], CompositeState],
        z: CompositeState,
        context: SystemContext,
    ) -> float:
        """Estimate σ_max(J_F)."""
        if self.fast_mode:
            return self._fast_proxy(transition_fn, z, context)
        return estimate_directional_amplification(
            transition_fn,
            z,
            context,
            num_iterations=self.num_iterations,
            perturbation_scale=self.perturbation_scale,
            activity_key=self.activity_key,
        )

    def _fast_proxy(
        self,
        transition_fn: Callable[[CompositeState, SystemContext], CompositeState],
        z: CompositeState,
        context: SystemContext,
    ) -> float:
        """Single finite-difference step: one random direction's ‖Jv‖."""
        x = _activity_tensor(z, self.activity_key)
        eps = self.perturbation_scale
        v = torch.randn_like(x)
        v /= v.norm(dim=-1, keepdim=True) + 1e-8

        x_perturbed = x + eps * v
        z_perturbed = CompositeState(
            activity={**z.activity, self.activity_key: x_perturbed},
            plastic=z.plastic,
            substrate=z.substrate,
        )
        with torch.no_grad():
            z_next = transition_fn(z, context)
            z_next_perturbed = transition_fn(z_perturbed, context)
        delta = _activity_tensor(
            z_next_perturbed, self.activity_key
        ) - _activity_tensor(z_next, self.activity_key)
        return (delta / eps).norm(dim=-1).mean().item()


def _full_jacobian(
    transition_fn: Callable[[CompositeState, SystemContext], CompositeState],
    z: CompositeState,
    context: SystemContext,
    activity_key: str,
) -> Tensor:
    """Exact per-sample Jacobian of the activity transition (small systems)."""
    x = _activity_tensor(z, activity_key).clone().requires_grad_(True)

    def forward(x_input: Tensor) -> Tensor:
        z_input = CompositeState(
            activity={**z.activity, activity_key: x_input},
            plastic=z.plastic,
            substrate=z.substrate,
        )
        z_out = transition_fn(z_input, context)
        return _activity_tensor(z_out, activity_key)

    jac = cast("Tensor", torch.autograd.functional.jacobian(forward, x))
    if jac.dim() == 4:
        jac = jac[0, :, 0, :]  # per-sample slice of batched jacobian
    return jac


def dominant_singular_value(
    transition_fn: Callable[[CompositeState, SystemContext], CompositeState],
    z: CompositeState,
    context: SystemContext,
    activity_key: str = "x",
) -> float:
    """Exact σ_max(J_F) via autograd Jacobian + SVD (expensive; validation only).

    This is the transient amplification bound ‖J‖_2 — distinct from ρ(J).
    """
    jac = _full_jacobian(transition_fn, z, context, activity_key)
    _u, s, _vh = torch.linalg.svd(jac)
    return s[0].item()


def spectral_radius_from_jacobian(
    transition_fn: Callable[[CompositeState, SystemContext], CompositeState],
    z: CompositeState,
    context: SystemContext,
    activity_key: str = "x",
) -> float:
    """Exact ρ(J_F) = max |λ_i(J_F)| via autograd Jacobian + eigenvalues.

    This is the asymptotic stability margin — for nonnormal J it is strictly
    smaller than σ_max(J). Small systems only.
    """
    jac = _full_jacobian(transition_fn, z, context, activity_key)
    return torch.linalg.eigvals(jac).abs().max().item()
