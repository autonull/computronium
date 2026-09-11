"""Stable-matrix helpers: constructions with verified realized spectra.

Phase 6A helper for the stable-transient-amplification recipe: build
size-4 Jordan-block and rotation linear maps with ρ ≤ ρ_limit and
σ_max > 1 (non-normal transients), plus realized-spectrum checks that reuse
the guard's exact estimators (:func:`spectral_radius_from_jacobian`,
:func:`dominant_singular_value`) rather than reimplementing them.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch
from torch import Tensor

from stability.spectral_radius import (
    dominant_singular_value,
    spectral_radius_from_jacobian,
)
from stability.state import CompositeState, activity_tensor

if TYPE_CHECKING:
    from collections.abc import Callable

    from stability.state import SystemContext

    LinearTransition = Callable[
        [CompositeState, "SystemContext | None"], CompositeState
    ]

DIM = 4


def jordan_block(gain: float = 1.05, dim: int = DIM) -> Tensor:
    """A Jordan block with eigenvalue ``gain``: ρ = gain, σ_max ≫ ρ."""
    J = gain * torch.eye(dim)
    for i in range(dim - 1):
        J[i, i + 1] = 1.0
    return J


def rotation(theta: float = 0.3, dim: int = DIM) -> Tensor:
    """Block-diagonal plane rotations: normal, ρ = σ_max = 1."""
    R = torch.eye(dim)
    for i in range(0, dim - 1, 2):
        c, s = torch.cos(torch.tensor(theta)), torch.sin(torch.tensor(theta))
        R[i : i + 2, i : i + 2] = torch.tensor([[c, -s], [s, c]])
    return R


def linear_transition(
    weight: Tensor, batch: int = 4
) -> tuple[LinearTransition, CompositeState]:
    """Closed-form transition ``x ↦ x @ W.T`` plus a seeded initial state."""
    dim = weight.shape[0]
    generator = torch.Generator().manual_seed(0)
    state = CompositeState(
        activity={"x": torch.randn(batch, dim, generator=generator)},
        plastic={},
        substrate={},
    )

    def transition(z: CompositeState, _context: SystemContext | None) -> CompositeState:
        x = activity_tensor(z.activity, "x")
        return CompositeState(
            activity={"x": x @ weight.T if isinstance(x, Tensor) else x},
            plastic=z.plastic,
            substrate=z.substrate,
        )

    return transition, state


def realized_rho(transition: LinearTransition, z: CompositeState) -> float:
    """Realized spectral radius ρ(J) via the guard's exact estimator."""
    return spectral_radius_from_jacobian(transition, z, None)  # type: ignore[arg-type]


def realized_sigma_max(transition: LinearTransition, z: CompositeState) -> float:
    """Realized operator norm σ_max(J) via the guard's exact estimator."""
    return dominant_singular_value(transition, z, None)  # type: ignore[arg-type]


def verify_spectrum(
    weight: Tensor,
    *,
    rho_limit: float = 1.0,
    sigma_floor: float | None = None,
    batch: int = 4,
) -> dict[str, float | bool]:
    """Build the transition and report realized ρ and σ_max with pass flags.

    Args:
        weight: Weight matrix of the linear map.
        rho_limit: Inclusive upper bound the realized ρ must meet.
        sigma_floor: Optional lower bound the realized σ_max must exceed.
        batch: Probe batch for the exact estimators.

    Returns:
        ``{"rho", "sigma_max", "rho_ok", "sigma_ok"}``.
    """
    transition, state = linear_transition(weight, batch)
    rho = realized_rho(transition, state)
    sigma_max = realized_sigma_max(transition, state)
    checks: dict[str, float | bool] = {
        "rho": rho,
        "sigma_max": sigma_max,
        "rho_ok": rho <= rho_limit + 1e-6,
        "sigma_ok": True if sigma_floor is None else sigma_max > sigma_floor,
    }
    return checks


__all__ = [
    "DIM",
    "jordan_block",
    "linear_transition",
    "realized_rho",
    "realized_sigma_max",
    "rotation",
    "verify_spectrum",
]
