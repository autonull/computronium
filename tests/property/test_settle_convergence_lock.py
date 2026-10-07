"""A shipped campaign must declare a settle that can converge (TODO48b R3).

The convergence early-exit (``convergence_threshold=1e-4``,
``convergence_start=5``) is the settle loop's only defence against paying the
full ``max_steps`` horizon — and ``~80%`` of an EqProp cell is that loop
(``scripts/probes/dynamics_cost.py``). It did not fire once in the campaign:
the shipped spec swept ``settle_step`` over ``[0.001, 0.1]``, and at every step
size in that band EqProp contracts by ``0.92`` per sweep, so the absolute
``1e-4`` delta is unreachable inside 30 sweeps. Measured
(``scripts/probes/settle_convergence.py``):

===============  ==========  ==========  ==========
settle_step      0.01        0.1         0.5
===============  ==========  ==========  ==========
energy_min       30 sweeps   30 sweeps   17 sweeps
lazy             30 sweeps   30 sweeps   17 sweeps
===============  ==========  ==========  ==========

Two claims are locked here, and the second is the one that bites:

1. **mechanism** — a settle that converges stops before ``max_steps``, and the
   telemetry says how many sweeps actually ran;
2. **declaration** — a *shipped* spec's ``settle_step`` domain contains a step
   size at which each EqProp dynamics it declares converges. Claim 1 is
   already covered by ``TestSettleHorizonTelemetry``; claim 2 is what a
   campaign fixture can silently violate, and it is invisible in a run: a
   non-converging settle returns a plausible state and a plausible number.

Falsifiable: narrowing the shipped domain back to ``hi: 0.1`` turns
``test_shipped_campaign_declares_a_converging_settle`` red, because no point in
the band reaches the threshold inside the horizon.
"""

from __future__ import annotations

import math
from pathlib import Path

import pytest
import torch

from computronium.ontology.dynamics import (
    EnergyMinimizationDynamics,
    LazyStateDynamics,
    StateDynamicsConfig,
)
from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig
from computronium.state.composite import CompositeState

SHIPPED_SPECS = sorted(Path("examples").glob("*.yaml"))
INPUT_DIM, HIDDEN_DIM, OUTPUT_DIM, BATCH = 64, 64, 10, 2
MAX_STEPS = 30
GRID = 3
CONVERGING_STEP = 1.0
NON_CONVERGING_STEP = 0.01

type Settleable = EnergyMinimizationDynamics | LazyStateDynamics

DYNAMICS_BY_NAME: dict[str, type[Settleable]] = {
    "energy_minimization": EnergyMinimizationDynamics,
    "lazy": LazyStateDynamics,
}
_FACTORY_BY_NAME = {
    "energy_minimization": StateDynamicsConfig.energy_minimization,
    "lazy": StateDynamicsConfig.lazy,
}


def _log_grid(lo: float, hi: float, points: int) -> tuple[float, ...]:
    """``points`` log-spaced samples of ``[lo, hi]``, endpoints included."""
    log_lo, log_hi = math.log10(lo), math.log10(hi)
    return tuple(
        10 ** (log_lo + (log_hi - log_lo) * i / (points - 1)) for i in range(points)
    )


def _sweeps(dynamics_name: str, step_size: float) -> tuple[int, bool]:
    """Free settle at ``step_size``; return (sweeps executed, converged flag)."""
    dynamics = DYNAMICS_BY_NAME[dynamics_name](
        _FACTORY_BY_NAME[dynamics_name](max_steps=MAX_STEPS, step_size=step_size)
    )
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=INPUT_DIM, hidden_dims=(HIDDEN_DIM,), output_dim=OUTPUT_DIM
        )
    )
    substrate = DigitalSubstrate(SubstrateConfig.digital())
    torch.manual_seed(0)
    state = CompositeState(
        activity={"x": torch.randn(BATCH, INPUT_DIM)}, plastic={}, substrate={}
    )
    with torch.no_grad():
        dynamics.settle(state, geometry, substrate, target=None)
    return dynamics._settle_steps_used, dynamics._converged


def _shipped_eqprop_names() -> list[str]:
    from computronium.experiment.schema import RunSpec

    return [
        primitive
        for path in SHIPPED_SPECS
        for sel in RunSpec.load(path).axes
        if sel.axis.value == "dynamics"
        for primitive in sel.primitives or ()
        if primitive in DYNAMICS_BY_NAME
    ]


def _shipped_settle_step() -> tuple[float, float]:
    """The first shipped spec's declared ``settle_step`` band."""
    from computronium.experiment.schema import RunSpec

    domain = RunSpec.load(SHIPPED_SPECS[0]).hyperparameters["settle_step"]
    assert domain is not None and domain.lo is not None and domain.hi is not None, (
        f"{SHIPPED_SPECS[0].name} declares no bounded settle_step band"
    )
    return domain.lo, domain.hi


def test_shipped_specs_exist() -> None:
    """The fixture must contain the spec the lock exists for."""
    assert SHIPPED_SPECS, "no shipped spec found; the lock has nothing to declare"


def test_shipped_campaign_declares_an_eqprop_dynamics() -> None:
    assert _shipped_eqprop_names(), "the shipped campaign declares no EqProp dynamics"


@pytest.mark.parametrize("dynamics_name", sorted(DYNAMICS_BY_NAME))
def test_a_converging_settle_stops_before_the_horizon(dynamics_name: str) -> None:
    """Claim 1: the exit fires, and the telemetry counts executed sweeps."""
    converging, converged = _sweeps(dynamics_name, CONVERGING_STEP)
    sweeping, not_converged = _sweeps(dynamics_name, NON_CONVERGING_STEP)
    assert converged is True, f"{dynamics_name} did not early-stop at {CONVERGING_STEP}"
    assert 0 < converging < MAX_STEPS, f"{dynamics_name} ran {converging} sweeps"
    assert not_converged is False, (
        f"{dynamics_name} early-stopped at {NON_CONVERGING_STEP}; the lock's "
        "band assumption has moved"
    )
    assert sweeping == MAX_STEPS


@pytest.mark.parametrize(
    "dynamics_name", _shipped_eqprop_names() or sorted(DYNAMICS_BY_NAME)
)
def test_shipped_campaign_declares_a_converging_settle(dynamics_name: str) -> None:
    """Claim 2: the *declared* band contains a step size that converges."""
    lo, hi = _shipped_settle_step()
    sweeps = [_sweeps(dynamics_name, s)[0] for s in _log_grid(lo, hi, GRID)]
    assert min(sweeps) < MAX_STEPS, (
        f"{dynamics_name} never converges inside settle_step [{lo}, {hi}] over "
        f"{GRID} samples (sweeps {sweeps}); the campaign measures unconverged "
        "settles"
    )
