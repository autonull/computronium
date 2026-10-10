"""Nonnormality Analysis (Phase D1).

Computes pseudospectra and transient amplification bounds for nonnormal
Jacobians. For nonnormal operators, σ_max(J) ≫ ρ(J) can cause significant
transient growth even when asymptotically stable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import numpy as np
import torch
from scipy.linalg import eigvals, svdvals

if TYPE_CHECKING:
    from collections.abc import Callable

    from stability.state import SystemContext

from stability.state import CompositeState, activity_tensor


@dataclass(frozen=True, slots=True)
class NonnormalityResult:
    """Result of nonnormality analysis."""

    spectral_radius: float
    max_singular_value: float
    nonnormality_ratio: float  # σ_max / ρ
    transient_amplification_bounds: dict[str, float]  # bounds at different times
    pseudospectrum: dict[float, np.ndarray] | None  # ε -> pseudospectrum boundary
    eigenvalues: np.ndarray
    metadata: dict[str, Any]


@dataclass(frozen=True, slots=True)
class NonnormalityConfig:
    """Configuration for nonnormality analysis."""

    epsilon_values: tuple[float, ...] = (1e-3, 1e-2, 1e-1, 1.0)
    num_directions: int = 50
    max_time: int = 100
    activity_key: str = "x"


def _compute_jacobian_autograd(
    transition_fn: Callable[[CompositeState, SystemContext], CompositeState],
    state: CompositeState,
    context: SystemContext,
    activity_key: str = "x",
) -> np.ndarray:
    """Compute exact Jacobian via autograd (for small systems only)."""
    x = activity_tensor(state.activity, activity_key).clone().requires_grad_(True)

    def forward(x_input: torch.Tensor) -> torch.Tensor:
        z_input = CompositeState(
            activity={**state.activity, activity_key: x_input},
            plastic=state.plastic,
            substrate=state.substrate,
        )
        z_out = transition_fn(z_input, context)
        return activity_tensor(z_out.activity, activity_key)

    jac = torch.autograd.functional.jacobian(forward, x)
    if jac.dim() == 4:
        # per-sample slice of batched jacobian
        jac = jac[0, :, 0, :]  # type: ignore[misc]
    elif jac.dim() == 3:
        jac = jac[0, :, :]  # type: ignore[misc]
    return jac.detach().cpu().numpy()


def compute_pseudospectrum(
    jacobian: np.ndarray,
    epsilon_values: list[float] | None = None,
    grid_size: int = 100,
) -> dict[float, np.ndarray]:
    """Compute ε-pseudospectrum of a matrix.

    The ε-pseudospectrum is the set of z ∈ ℂ such that ||(zI - J)⁻¹|| > 1/ε,
    i.e., the eigenvalues of J + E for all ||E|| < ε.

    For computational efficiency, we compute the boundary on a grid in the
    complex plane.
    """
    if epsilon_values is None:
        epsilon_values = [1e-3, 1e-2, 1e-1, 1.0]

    n = jacobian.shape[0]
    # Determine grid bounds from eigenvalues
    eigs = eigvals(jacobian)
    real_min, real_max = eigs.real.min(), eigs.real.max()
    imag_min, imag_max = eigs.imag.min(), eigs.imag.max()

    # Add padding
    padding = max(real_max - real_min, imag_max - imag_min) * 0.5 + 1.0
    real_range = np.linspace(real_min - padding, real_max + padding, grid_size)
    imag_range = np.linspace(imag_min - padding, imag_max + padding, grid_size)

    results = {}
    for eps in epsilon_values:
        boundary = np.zeros((grid_size, grid_size), dtype=bool)
        for i, re in enumerate(real_range):
            for j, im in enumerate(imag_range):
                z = complex(re, im)
                zI_minus_J = z * np.eye(n) - jacobian
                try:
                    inv_norm = np.linalg.norm(np.linalg.inv(zI_minus_J), 2)
                    if inv_norm > 1.0 / eps:
                        boundary[i, j] = True
                except np.linalg.LinAlgError:
                    boundary[i, j] = True  # Singular -> on spectrum
        results[eps] = boundary

    return results


def compute_transient_amplification_bounds(
    jacobian: np.ndarray,
    max_time: int = 100,
) -> dict[str, float]:
    """Compute transient amplification bounds for powers of the matrix.

    For nonnormal J, ||J^t|| can be much larger than ρ(J)^t for transient times.
    """
    eigs = eigvals(jacobian)
    spectral_radius = np.max(np.abs(eigs))

    # Compute ||J^t|| for t = 1..max_time
    jac_powers = np.eye(jacobian.shape[0])
    amplifications = []

    for t in range(1, max_time + 1):
        jac_powers @= jacobian
        norm = np.linalg.norm(jac_powers, 2)
        amplifications.append(norm)

    amplifications = np.array(amplifications)

    return {
        "max_amplification": float(np.max(amplifications)),
        "time_of_max": int(np.argmax(amplifications) + 1),
        "asymptotic_rate": float(spectral_radius),
        "transient_peak_ratio": float(
            np.max(amplifications) / (spectral_radius ** np.argmax(amplifications + 1))
        )
        if spectral_radius > 0
        else float("inf"),
        "amplification_curve": amplifications.tolist(),
    }


def analyze_nonnormality(
    transition_fn: Callable[[CompositeState, SystemContext], CompositeState],
    state: CompositeState,
    context: SystemContext,
    config: NonnormalityConfig | None = None,
) -> NonnormalityResult:
    """Full nonnormality analysis of the transition Jacobian."""
    config = config or NonnormalityConfig()

    # Compute exact Jacobian (expensive, small systems only)
    jac = _compute_jacobian_autograd(transition_fn, state, context, config.activity_key)

    # Eigenvalues and spectral radius
    eigs = eigvals(jac)
    spectral_radius = float(np.max(np.abs(eigs)))

    # Singular values and max singular value
    svals = svdvals(jac)
    max_singular_value = float(svals[0])

    # Nonnormality measure
    nonnormality_ratio = (
        max_singular_value / spectral_radius if spectral_radius > 0 else float("inf")
    )

    # Pseudospectrum
    pseudospectrum = compute_pseudospectrum(jac, list(config.epsilon_values))

    # Transient amplification bounds
    transient_bounds = compute_transient_amplification_bounds(jac, config.max_time)

    return NonnormalityResult(
        spectral_radius=spectral_radius,
        max_singular_value=max_singular_value,
        nonnormality_ratio=nonnormality_ratio,
        transient_amplification_bounds=transient_bounds,
        pseudospectrum=pseudospectrum,
        eigenvalues=eigs,
        metadata={
            "activity_key": config.activity_key,
            "matrix_shape": jac.shape,
            "epsilon_values": config.epsilon_values,
            "max_time": config.max_time,
        },
    )


class NonnormalityAnalyzer:
    """Analyze nonnormality of transition operators."""

    def __init__(
        self,
        transition_fn: Callable[[CompositeState, SystemContext], CompositeState],
        context: SystemContext,
        config: NonnormalityConfig | None = None,
    ):
        self.transition_fn = transition_fn
        self.context = context
        self.config = config or NonnormalityConfig()

    def analyze(self, state: CompositeState) -> NonnormalityResult:
        """Run nonnormality analysis at a given state."""
        return analyze_nonnormality(
            self.transition_fn, state, self.context, self.config
        )

    def analyze_multiple_states(
        self,
        states: list[CompositeState],
    ) -> list[NonnormalityResult]:
        """Analyze nonnormality at multiple states."""
        return [self.analyze(s) for s in states]
