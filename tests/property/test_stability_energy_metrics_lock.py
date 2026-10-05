"""Lock: the stability and energy metrics describe the cell they measured.

TODO51's campaigns are Pareto frontiers over (rho, sigma_max) and joules, so a
metric that does not respond to the cell is not a noisy frontier — it is a
constant line, and no schema check catches it. Three defects shipped behind
schema-valid payloads:

* **The horizon, not the step.** ``compute_stability_metrics`` differentiated
  the whole ``settle()`` with respect to the input, so it reported rho^N. A
  contracting cell (rho=0.998) read as rho=0.0087, and a transient
  amplification sigma_max > 1 — the entire subject of the frontier — was
  invisible. The step Jacobian and the whole-settle Jacobian disagree by a
  factor of ``max_steps``, so the lock asserts they do.
* **A weight shape that was not the cell's.** Energy was estimated from a
  hardcoded ``(output_dim, input_dim)``, so a 13k-parameter cell and an 88k
  one reported byte-identical joules. Widening the network must move the
  joules.
* **Walltime under unbounded fan-out.** Ten cells trained simultaneously on
  one device each reported the walltime of all ten. Bounded admission must
  make a cell's walltime its own.

Also: every metric the evaluator writes must be a metric the objectives
registry can name, or an objective a run declares resolves to nothing.
"""

from __future__ import annotations

import inspect
import math
from typing import cast

import pytest
import torch
from torch.autograd.functional import jacobian

from computronium.experiment.execution.backends import LocalBackend
from computronium.experiment.execution.evaluate import (
    compute_energy_metrics,
    compute_stability_metrics,
)
from computronium.experiment.execution.settle_operator import (
    layer_weight_shapes,
    settle_step_operator,
)
from computronium.experiment.schema.metrics import (
    MEASURED_METRICS,
    MEASURED_OBJECTIVES,
)

pytestmark = pytest.mark.filterwarnings("ignore::UserWarning")


def _system(hidden: int, layers: int = 3, step_size: float | None = None):
    from computronium.experiment.execution.compose import compose_cell_system
    from computronium.experiment.schema.coordinate import Coordinate

    coordinate = Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="energy_minimization",
        plasticity="null",
        credit="thermodynamic_contrast",
        update="euclidean",
        params={
            "hidden_dim": hidden,
            "num_layers": layers,
            "settle_step": step_size if step_size is not None else 0.1,
            "settle_beta": 0.5,
            "feedback_scale": 0.5,
            "precision": "float32",
        },
    )
    cell = compose_cell_system(
        coordinate=coordinate,
        geometry={},
        input_shape=(64,),
        output_dim=10,
        param_budget=2_000_000,
    )
    return cell.system


def _radius(jac: torch.Tensor) -> float:
    singular = torch.linalg.svdvals(jac)
    if jac.shape[0] == jac.shape[1]:
        return float(torch.linalg.eigvals(jac).abs().max().item())
    return float(singular.max().item())


def test_the_step_and_the_whole_settle_are_different_operators() -> None:
    """The gap is the horizon: rho_step^N is what the old code reported.

    Without this assertion the two can be swapped again and every frontier
    still looks plausible.
    """
    torch.manual_seed(0)
    system = _system(hidden=64)
    x = torch.randn(4, 64)
    horizon = system.dynamics.config.max_steps

    operator = settle_step_operator(system, x)
    assert operator is not None, "a layered geometry must expose its settle step"
    step, width = operator

    def whole_settle(x_in: torch.Tensor) -> torch.Tensor:
        from computronium.ontology import SystemState

        settled = system.dynamics.settle(
            SystemState(x=x_in, y=None), system.geometry, system.substrate
        )
        return settled.activations[-1]

    per_step = _radius(jacobian(step, torch.zeros(width)))
    composed = _radius(cast("torch.Tensor", jacobian(whole_settle, x[:1])[0, :, 0, :]))

    assert horizon > 1
    assert composed < 0.5 * per_step, (
        f"whole-settle radius {composed:.4f} vs step radius {per_step:.4f}: "
        "the horizon must not be inside the reported spectral radius"
    )
    metrics = compute_stability_metrics(system, x)
    assert metrics["spectral_radius"] == pytest.approx(per_step, rel=0.2), (
        "the reported radius must be the step's, which a horizon-inflated "
        "Jacobian cannot be"
    )


def test_spectral_radius_is_near_one_not_collapsed_by_the_horizon() -> None:
    """rho in [0.5, 2) on a settling cell; the old value was 0.0087."""
    torch.manual_seed(0)
    system = _system(hidden=64)
    metrics = compute_stability_metrics(system, torch.randn(4, 64))

    assert "spectral_radius" in metrics
    radius = metrics["spectral_radius"]
    assert 0.5 < radius < 2.0, f"settle-step rho {radius} is not a settling operator"


def test_nonnormality_is_separable_from_contraction() -> None:
    """sigma_max is reported apart from rho, which is the frontier's subject.

    A metric that collapses sigma_max onto rho cannot express "contracts
    eventually, amplifies transiently" at all — which is the hypothesis
    TODO51 §2 exists to test.
    """
    torch.manual_seed(0)
    system = _system(hidden=96, layers=4)
    metrics = compute_stability_metrics(system, torch.randn(4, 64))

    assert metrics["min_singular_value"] <= metrics["max_singular_value"]
    assert "nonnormality" in metrics
    assert metrics["lyapunov_exponent"] == pytest.approx(
        torch.log(torch.tensor(metrics["spectral_radius"])).item(), abs=1e-5
    )


def test_settling_telemetry_is_read_from_a_settle_that_ran() -> None:
    """settle_converged must reflect a settle, not a counter left at zero."""
    torch.manual_seed(0)
    system = _system(hidden=64)
    metrics = compute_stability_metrics(system, torch.randn(4, 64))

    assert metrics["settle_steps"] > 0
    assert metrics["settle_horizon"] >= metrics["settle_steps"]
    assert metrics["settle_converged"] in {0.0, 1.0}


@pytest.mark.parametrize("hidden", [64, 128])
def test_energy_responds_to_the_cell_not_to_a_hardcoded_shape(hidden: int) -> None:
    """More weights must cost more joules. The defect: one number for all cells."""
    torch.manual_seed(0)
    narrow = compute_energy_metrics(_system(hidden), batch_size=8)
    wide = compute_energy_metrics(_system(hidden * 2), batch_size=8)

    assert wide["macs_per_step"] > narrow["macs_per_step"]
    assert wide["energy_per_batch"] > narrow["energy_per_batch"]
    assert wide["energy_per_sample"] > narrow["energy_per_sample"]
    assert narrow["energy_per_mac"] == pytest.approx(wide["energy_per_mac"])


def test_weight_shapes_are_the_geometrys_own() -> None:
    system = _system(hidden=64, layers=3)
    shapes = layer_weight_shapes(system.geometry)

    assert len(shapes) >= 3, "one shape per linear layer, plus the recurrent one"
    assert all(out > 0 and inn > 0 for out, inn in shapes)
    assert shapes[0] == (64, 64)
    assert shapes[-1] == (10, 64), "the last layer is the output projection"


def test_backend_bounds_its_own_concurrency() -> None:
    """max_workers is a declaration; it must reach the submission path."""
    source = inspect.getsource(LocalBackend.__mro__[1].submit_batch)
    assert "_admission" in source, (
        "submit_batch no longer gates on max_workers, so every cell in a round "
        "trains at once and walltime_total measures contention"
    )


def test_every_evaluator_metric_is_nameable_by_an_objective() -> None:
    """A payload key the objectives registry cannot name reaches no study."""
    from computronium.experiment.execution import evaluate

    source = inspect.getsource(evaluate)
    written = {
        line.split('"')[1]
        for line in source.splitlines()
        if 'metrics["' in line and '"' in line.split("metrics[")[1]
    }
    unregistered = sorted(written - MEASURED_METRICS)
    assert not unregistered, (
        f"evaluator writes metrics no objective can name: {unregistered}"
    )
    assert MEASURED_OBJECTIVES["spectral_radius"] == "spectral_radius"
    assert MEASURED_OBJECTIVES["energy_per_step"] == "energy_per_sample"


@pytest.mark.parametrize(
    ("name", "factory"),
    [
        ("digital", "digital"),
        ("analog", "analog"),
        ("memristive", "memristive"),
        ("neuromorphic", "neuromorphic"),
        ("optical", "optical"),
        ("quantum", "quantum"),
        ("complex", "complex"),
        ("sparse", "sparse"),
        ("ternary", "ternary"),
    ],
)
def test_every_substrate_energy_model_scales_with_layer_width(
    name: str, factory: str
) -> None:
    """A substrate whose joules ignore the layer size is a constant axis.

    Batch monotonicity is deliberately non-strict: an optical substrate's laser
    power does not scale with the batch and a memristive one's programming cost
    is paid once per weight. Layer width is the MAC-driven term and must.
    """
    from computronium.ontology.substrate._substrate import (
        SubstrateConfig,
        substrate_from_config,
    )

    substrate = substrate_from_config(getattr(SubstrateConfig, factory)())

    def joules(batch: int, out: int) -> float:
        return float(
            substrate.estimate_energy(
                input_shape=(batch, 64),
                weight_shape=(out, 64),
                batch_size=batch,
            )["total_energy_per_step"]
        )

    assert joules(64, 256) / joules(8, 64) > 3.0, (
        f"{name}: quadrupling the layer width must raise the joules"
    )
    assert joules(64, 64) >= joules(8, 64), f"{name}: energy falls as the batch grows"


def test_device_substrates_are_an_order_below_digital() -> None:
    """The coarse literature claim: a digital MAC is >10x dearer than a device's.

    Not the finer ordering among the device substrates — neuromorphic charges
    per event and memristive per programming op, so comparing those two per MAC
    compares two units rather than two devices.
    """
    from computronium.ontology.substrate._substrate import (
        SubstrateConfig,
        substrate_from_config,
    )

    def joules(factory: str) -> float:
        return float(
            substrate_from_config(getattr(SubstrateConfig, factory)()).estimate_energy(
                input_shape=(8, 64), weight_shape=(64, 64), batch_size=8
            )["total_energy_per_step"]
        )

    digital = joules("digital")
    for device in ("memristive", "neuromorphic", "optical"):
        assert digital / joules(device) > 10.0, (
            f"{device} is not an order of magnitude below digital"
        )


@pytest.mark.parametrize("eta", [0.2, 0.03, 0.001])
def test_the_drift_radius_is_invariant_to_the_step_size(eta: float) -> None:
    """The relaxation radius cannot resolve anything; the drift radius can.

    A relaxation step is ``h <- h + eta * (f(h) - h)``, so ``J = I + eta*D`` and
    the identity pins ``rho(J)`` at 1 for any small ``eta``. Over a 500x range of
    ``eta`` this cell's ``rho_step`` stayed within 1.0000 +/- 0.0003 while its
    ``rho_drift`` read ~2.0 throughout — 20x the resolution, and the quantity a
    frontier is about.
    """
    torch.manual_seed(0)
    system = _system(hidden=64, step_size=eta)
    metrics = compute_stability_metrics(system, torch.randn(4, 64))

    assert metrics["settle_step_size"] == eta
    assert 1.5 < metrics["drift_spectral_radius"] < 2.5, (
        f"drift radius {metrics['drift_spectral_radius']} at eta={eta}"
    )
    assert metrics["contraction_rate"] == pytest.approx(
        1.0 - eta * metrics["drift_spectral_radius"]
    )


def test_drift_and_relaxation_are_different_operators() -> None:
    """Reporting rho(J) alone reads 1.00 for a cell whose network gain is 2.0."""
    torch.manual_seed(0)
    system = _system(hidden=64)
    metrics = compute_stability_metrics(system, torch.randn(4, 64))

    assert abs(metrics["spectral_radius"] - 1.0) < 0.05, (
        "the relaxation operator sits on the unit circle by construction"
    )
    assert abs(metrics["drift_spectral_radius"] - 1.0) > 0.2, (
        "so the drift operator is the one that carries the gain"
    )
    assert metrics["drift_max_singular_value"] >= metrics["drift_spectral_radius"]


# ============================================================
# Dynamics coverage: stability metrics must work across all legal
# dynamics primitives, not just the one the campaign pinned.
# ============================================================

# Each dynamics with a credit/geometry the framework accepts for it.
# Probing an illegal pairing measures the validity check, not the metric:
# diffusion demands recurrent geometry and non-gradient credit, spike
# integration demands temporal-trace or target-inversion credit, and
# thermodynamic contrast demands an energy-based or PC-family dynamics.
_LEGAL_DYNAMICS = {
    "energy_minimization": ("thermodynamic_contrast", "feedforward"),
    "error_predictive_coding": ("thermodynamic_contrast", "feedforward"),
    "pc_alm": ("thermodynamic_contrast", "feedforward"),
    "predictive_settling": ("thermodynamic_contrast", "feedforward"),
    "instantaneous": ("gradient", "feedforward"),
    "diffusion": ("random_projections", "recurrent"),
    "lazy": ("gradient", "feedforward"),
    "spike_integration": ("temporal_trace", "feedforward"),
}

_STABILITY_METRICS = (
    "spectral_radius",
    "max_singular_value",
    "min_singular_value",
    "lyapunov_exponent",
    "drift_spectral_radius",
    "drift_max_singular_value",
    "contraction_rate",
)


def _system_for_dynamics(dynamics: str, geometry: str, credit: str):
    from computronium.experiment.execution.compose import compose_cell_system
    from computronium.experiment.schema.coordinate import Coordinate

    return compose_cell_system(
        coordinate=Coordinate(
            substrate="digital",
            geometry=geometry,
            dynamics=dynamics,
            plasticity="null",
            credit=credit,
            update="euclidean",
            params={"hidden_dim": 64, "num_layers": 3},
        ),
        geometry={},
        input_shape=(64,),
        output_dim=10,
        param_budget=2_000_000,
    ).system


@pytest.mark.parametrize("dynamics", sorted(_LEGAL_DYNAMICS.keys()))
def test_stability_metrics_cover_dynamics_family(dynamics: str) -> None:
    """Every legal dynamics produces the core stability metrics.

    The stability-plasticity campaign pinned energy_minimization +
    thermodynamic_contrast, so every number in TODO51 §2 came from one
    dynamics primitive out of eight. This test ensures a regression that
    made compute_stability_metrics energy-only again would fail.
    """
    credit, geometry = _LEGAL_DYNAMICS[dynamics]
    torch.manual_seed(0)
    system = _system_for_dynamics(dynamics, geometry, credit)
    metrics = compute_stability_metrics(system, torch.randn(4, 64))

    for key in _STABILITY_METRICS:
        assert key in metrics, f"{dynamics}: missing stability metric {key}"
        assert math.isfinite(metrics[key]), f"{dynamics}: {key} is not finite"


# Energy metrics must also be produced per dynamics family
_ENERGY_METRICS = (
    "hopfield_energy",
    "pc_free_energy",
    "augmented_lagrangian",
    "spike_proxy_energy",
    "instantaneous_proxy_energy",
    "free_energy",  # alias for hopfield_energy
)


def _expected_energy_key(dynamics: str) -> str:
    if dynamics in {"energy_minimization", "lazy", "diffusion"}:
        return "hopfield_energy"
    if dynamics in {"predictive_settling", "error_predictive_coding"}:
        return "pc_free_energy"
    if dynamics == "pc_alm":
        return "augmented_lagrangian"
    if dynamics == "spike_integration":
        return "spike_proxy_energy"
    if dynamics == "instantaneous":
        return "instantaneous_proxy_energy"
    return "unknown"


@pytest.mark.parametrize("dynamics", sorted(_LEGAL_DYNAMICS.keys()))
def test_energy_metrics_cover_dynamics_family(dynamics: str) -> None:
    """Every legal dynamics produces its family-specific energy metric.

    The free_energy metric was a single name for different quantities across
    families (Hopfield energy, variational free energy, augmented Lagrangian,
    proxies). Now each family has its own metric name; free_energy remains
    as an alias for the hopfield family only.
    """
    credit, geometry = _LEGAL_DYNAMICS[dynamics]
    torch.manual_seed(0)
    system = _system_for_dynamics(dynamics, geometry, credit)
    metrics = compute_stability_metrics(system, torch.randn(4, 64))

    expected = _expected_energy_key(dynamics)
    assert expected in metrics, f"{dynamics}: missing energy metric {expected}"
    assert math.isfinite(metrics[expected]), f"{dynamics}: {expected} is not finite"

    # free_energy alias only for hopfield family
    if expected == "hopfield_energy":
        assert "free_energy" in metrics
        assert metrics["free_energy"] == pytest.approx(metrics["hopfield_energy"])
    else:
        assert "free_energy" not in metrics, (
            f"{dynamics}: free_energy alias should not appear for non-hopfield family"
        )
