"""Regression: Jacobian amplification vs spectral radius (TODO18 2.1).

Level 4 sampled numerical tests. The estimator family must never conflate
the operator-norm amplification σ_max(J) with the spectral radius ρ(J):
for normal matrices they coincide; for the canonical Jordan block
J = [[0.5, 10], [0, 0.5]], ρ = 0.5 while ‖J‖₂ ≈ 10.025.
"""

from typing import cast

import pytest
import torch

from computronium.stability.spectral_radius import (
    dominant_singular_value,
    estimate_directional_amplification,
    spectral_radius_from_jacobian,
)
from computronium.state import CompositeState, SystemContext


@pytest.fixture(autouse=True)
def _seed():
    torch.manual_seed(0)


class _Ctx:
    theta: tuple = ()


ctx = cast("SystemContext", _Ctx())


def _linear_transition(J: torch.Tensor):
    def fn(z: CompositeState, _ctx: object) -> CompositeState:
        x = z.activity["x"]
        assert isinstance(x, torch.Tensor)
        return CompositeState(
            activity={"x": x @ J.T},
            plastic=z.plastic,
            substrate=z.substrate,
        )

    return fn


def _state(x: torch.Tensor) -> CompositeState:
    return CompositeState(activity={"x": x}, plastic={}, substrate={})


@pytest.mark.parametrize("diag,expected_rho", [((0.9, 0.7), 0.9), ((0.3, 0.3), 0.3)])
def test_normal_matrix_rho_equals_sigma_max(diag, expected_rho):
    """Normal (diagonal) J: ρ(J) = σ_max(J); both estimators must agree."""
    J = torch.diag(torch.tensor(diag))
    z = _state(torch.randn(1, 2))

    rho = spectral_radius_from_jacobian(_linear_transition(J), z, context=ctx)
    sigma = dominant_singular_value(_linear_transition(J), z, context=ctx)
    amp = estimate_directional_amplification(_linear_transition(J), z, context=ctx)

    assert rho == pytest.approx(expected_rho, abs=1e-5)
    assert sigma == pytest.approx(expected_rho, abs=1e-5)
    assert amp == pytest.approx(expected_rho, abs=0.05)


def test_nonnormal_jordan_block_not_conflated():
    """J = [[0.5, 10], [0, 0.5]]: ρ = 0.5 but ‖J‖₂ ≈ 10.01.

    The amplification estimator must report ~σ_max, never ρ, and the two
    exact metrics must stay strictly separated.
    """
    J = torch.tensor([[0.5, 10.0], [0.0, 0.5]])
    z = _state(torch.randn(1, 2))
    fn = _linear_transition(J)

    rho = spectral_radius_from_jacobian(fn, z, context=ctx)
    sigma = dominant_singular_value(fn, z, context=ctx)
    amp = estimate_directional_amplification(fn, z, context=ctx)

    assert rho == pytest.approx(0.5, abs=1e-4)
    assert sigma == pytest.approx(10.0246, abs=0.05)
    assert amp == pytest.approx(0.5, rel=0.1)  # eigen-direction convergence
    assert sigma > rho * 10  # transient amplification: σ_max ≫ ρ here


def test_estimator_is_not_sigma_max_on_nonnormal():
    """Power iteration on J aligns with eigen-directions on nonnormal J.

    The estimator's ‖Jv‖ must never be reported as σ_max(J) for nonnormal J:
    it converges to the dominant eigenvalue magnitude (0.5) while ‖J‖₂ ≈ 10.02.
    """
    J = torch.tensor([[0.5, 10.0], [0.0, 0.5]])
    fn = _linear_transition(J)
    z = _state(torch.randn(1, 2))

    amp = estimate_directional_amplification(fn, z, context=ctx, num_iterations=50)
    sigma = dominant_singular_value(fn, z, context=ctx)

    assert amp == pytest.approx(0.5, rel=0.1)
    assert sigma == pytest.approx(10.0246, abs=0.05)
