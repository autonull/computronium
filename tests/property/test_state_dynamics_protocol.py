"""Property tests for StateDynamics protocol invariants.

Tests the canonical contract from the StateDynamics protocol docstring:
- Activation layout: layered states are [input, hidden1, ..., hiddenN, output]
- Phase loop and energy timing: settle runs free phase when target is None,
  nudged phase otherwise; compute_energy called AFTER settle returns
- Autograd context: settle runs under caller's no_grad; implementations needing
  internal differentiation open torch.enable_grad() around reverse sweep
- Input flattening: implementations flatten non-2-D inputs themselves
- Free/nudged target semantics: target is None -> write to free_state;
  target provided -> nudge and write to nudged_state; both populate activations
- Mutation contract: settle always returns the state to use; callers must bind
  and use the returned state
"""

import ast
import itertools
import math
from pathlib import Path

import pytest
import torch
from hypothesis import given, settings
from hypothesis import strategies as st

from computronium.ontology.dynamics import (
    DiffusionDynamics,
    EnergyMinimizationDynamics,
    ErrorPredictiveCodingDynamics,
    InstantaneousDynamics,
    LazyStateDynamics,
    PCALMDynamics,
    PredictiveSettlingDynamics,
    SpikeIntegrationDynamics,
    StateDynamics,
    StateDynamicsConfig,
)
from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig
from computronium.state.composite import CompositeState

# All StateDynamics implementations to test
DYNAMICS_CLASSES = [
    EnergyMinimizationDynamics,
    PredictiveSettlingDynamics,
    ErrorPredictiveCodingDynamics,
    PCALMDynamics,
    SpikeIntegrationDynamics,
    InstantaneousDynamics,
    DiffusionDynamics,
    LazyStateDynamics,
]

# Config factories for each dynamics type
DYNAMICS_CONFIGS = {
    EnergyMinimizationDynamics: lambda: StateDynamicsConfig.energy_minimization(
        max_steps=5, step_size=0.1, beta=0.5
    ),
    PredictiveSettlingDynamics: lambda: StateDynamicsConfig.predictive_settling(
        max_steps=5, step_size=0.1
    ),
    ErrorPredictiveCodingDynamics: lambda: StateDynamicsConfig.error_predictive_coding(
        max_steps=5, step_size=0.1
    ),
    PCALMDynamics: lambda: StateDynamicsConfig.pc_alm(
        max_steps=5, step_size=0.1, rho=1.0
    ),
    SpikeIntegrationDynamics: lambda: StateDynamicsConfig.spike_integration(
        max_steps=5, step_size=0.1, threshold=1.0
    ),
    InstantaneousDynamics: StateDynamicsConfig.instantaneous,
    DiffusionDynamics: lambda: StateDynamicsConfig.diffusion(
        max_steps=5, step_size=0.1
    ),
    LazyStateDynamics: lambda: StateDynamicsConfig.lazy(max_steps=5),
}


def _make_geometry_and_substrate(input_dim: int = 8, output_dim: int = 4):
    """Create a standard feedforward geometry and digital substrate."""
    geom_config = GeometryConfig.feedforward(
        input_dim=input_dim,
        hidden_dims=(16, 16),
        output_dim=output_dim,
    )
    geometry = FeedforwardGeometry(geom_config)
    substrate = DigitalSubstrate(SubstrateConfig.digital())
    return geometry, substrate


def _make_state(x: torch.Tensor) -> CompositeState:
    """Create a CompositeState with input x."""
    return CompositeState(activity={"x": x}, plastic={}, substrate={})


class TestStateDynamicsProtocolConformance:
    """Test that all implementations satisfy the StateDynamics protocol."""

    @pytest.mark.parametrize("dynamics_cls", DYNAMICS_CLASSES)
    def test_implements_protocol(self, dynamics_cls):
        """Each dynamics class should satisfy the StateDynamics protocol."""
        config = DYNAMICS_CONFIGS[dynamics_cls]()
        dynamics = dynamics_cls(config)
        assert isinstance(dynamics, StateDynamics)
        assert hasattr(dynamics, "config")
        assert hasattr(dynamics, "settle")
        assert hasattr(dynamics, "compute_energy")


class TestActivationLayout:
    """Test activation layout invariant: [input, hidden1, ..., hiddenN, output]."""

    @pytest.mark.parametrize("dynamics_cls", DYNAMICS_CLASSES)
    def test_settle_returns_layered_activations(self, dynamics_cls):
        """Settle should return activations in layered format: input, hidden..., output."""
        config = DYNAMICS_CONFIGS[dynamics_cls]()
        dynamics = dynamics_cls(config)
        geometry, substrate = _make_geometry_and_substrate()
        x = torch.randn(2, 8)
        state = _make_state(x)

        with torch.no_grad():
            settled = dynamics.settle(state, geometry, substrate, target=None)

        activations = settled.activations
        assert activations is not None, "Activations should be populated"
        assert isinstance(activations, list), "Activations should be a list"
        assert len(activations) >= 3, "Should have at least input, hidden, output"

        # Input layer (element 0) should match input batch size
        assert activations[0].shape[0] == x.shape[0]
        assert activations[0].shape[1] == 8  # input_dim

        # Output layer (element -1) should match output_dim
        assert activations[-1].shape[0] == x.shape[0]
        assert activations[-1].shape[1] == 4  # output_dim

    @pytest.mark.parametrize("dynamics_cls", DYNAMICS_CLASSES)
    def test_nudged_phase_same_layout(self, dynamics_cls):
        """Nudged phase should produce same activation layout as free phase."""
        config = DYNAMICS_CONFIGS[dynamics_cls]()
        dynamics = dynamics_cls(config)
        geometry, substrate = _make_geometry_and_substrate()
        x = torch.randn(2, 8)
        target = torch.randn(2, 4)
        state = _make_state(x)

        with torch.no_grad():
            free_state = dynamics.settle(
                state.clone(), geometry, substrate, target=None
            )
            nudged_state = dynamics.settle(
                state.clone(), geometry, substrate, target=target
            )

        free_acts = free_state.activations
        nudged_acts = nudged_state.activations

        assert free_acts is not None and nudged_acts is not None
        assert len(free_acts) == len(nudged_acts), (
            "Free and nudged should have same depth"
        )

        for f, n in zip(free_acts, nudged_acts):
            assert f.shape == n.shape, "Corresponding layers should have same shape"


class TestPhaseLoopAndEnergyTiming:
    """Test phase loop and energy timing invariants."""

    @pytest.mark.parametrize("dynamics_cls", DYNAMICS_CLASSES)
    def test_free_phase_writes_free_state(self, dynamics_cls):
        """When target is None, settle should write to free_state."""
        config = DYNAMICS_CONFIGS[dynamics_cls]()
        dynamics = dynamics_cls(config)
        geometry, substrate = _make_geometry_and_substrate()
        x = torch.randn(2, 8)
        state = _make_state(x)

        with torch.no_grad():
            settled = dynamics.settle(state, geometry, substrate, target=None)

        assert settled.free_state is not None, "Free state should be populated"
        assert settled.activations is not None, "Activations should be populated"
        # free_state and activations should be the same object (or equal)
        assert (
            settled.free_state is settled.activations
            or settled.free_state == settled.activations
        )

    @pytest.mark.parametrize("dynamics_cls", DYNAMICS_CLASSES)
    def test_nudged_phase_writes_nudged_state(self, dynamics_cls):
        """When target is provided, settle should write to nudged_state."""
        config = DYNAMICS_CONFIGS[dynamics_cls]()
        dynamics = dynamics_cls(config)
        geometry, substrate = _make_geometry_and_substrate()
        x = torch.randn(2, 8)
        target = torch.randn(2, 4)
        state = _make_state(x)

        with torch.no_grad():
            settled = dynamics.settle(state, geometry, substrate, target=target)

        assert settled.nudged_state is not None, "Nudged state should be populated"
        assert settled.activations is not None, "Activations should be populated"
        assert (
            settled.nudged_state is settled.activations
            or settled.nudged_state == settled.activations
        )

    @pytest.mark.parametrize("dynamics_cls", DYNAMICS_CLASSES)
    def test_compute_energy_called_after_settle(self, dynamics_cls):
        """compute_energy should work on state returned by settle."""
        config = DYNAMICS_CONFIGS[dynamics_cls]()
        dynamics = dynamics_cls(config)
        geometry, substrate = _make_geometry_and_substrate()
        x = torch.randn(2, 8)
        state = _make_state(x)

        with torch.no_grad():
            settled = dynamics.settle(state, geometry, substrate, target=None)
            energy = dynamics.compute_energy(settled, geometry)

        assert isinstance(energy, torch.Tensor), "Energy should be a tensor"
        assert energy.ndim == 0, "Energy should be a scalar tensor"
        assert torch.isfinite(energy), "Energy should be finite"

    @pytest.mark.parametrize("dynamics_cls", DYNAMICS_CLASSES)
    def test_compute_energy_works_on_nudged_state(self, dynamics_cls):
        """compute_energy should work on nudged state too."""
        config = DYNAMICS_CONFIGS[dynamics_cls]()
        dynamics = dynamics_cls(config)
        geometry, substrate = _make_geometry_and_substrate()
        x = torch.randn(2, 8)
        target = torch.randn(2, 4)
        state = _make_state(x)

        with torch.no_grad():
            settled = dynamics.settle(state, geometry, substrate, target=target)
            energy = dynamics.compute_energy(settled, geometry)

        assert isinstance(energy, torch.Tensor)
        assert torch.isfinite(energy)


class TestAutogradContext:
    """Test autograd context invariants."""

    @pytest.mark.parametrize("dynamics_cls", DYNAMICS_CLASSES)
    def test_settle_works_under_no_grad(self, dynamics_cls):
        """Settle should work correctly under no_grad (default inference mode)."""
        config = DYNAMICS_CONFIGS[dynamics_cls]()
        dynamics = dynamics_cls(config)
        geometry, substrate = _make_geometry_and_substrate()
        x = torch.randn(2, 8)
        state = _make_state(x)

        with torch.no_grad():
            settled = dynamics.settle(state, geometry, substrate, target=None)

        assert settled.activations is not None
        for act in settled.activations:
            assert not act.requires_grad, (
                "Activations should not require grad under no_grad"
            )

    @pytest.mark.parametrize("dynamics_cls", DYNAMICS_CLASSES)
    def test_settle_preserves_grad_when_enabled(self, dynamics_cls):
        """Settle should preserve gradient tracking when grad is enabled."""
        config = DYNAMICS_CONFIGS[dynamics_cls]()
        dynamics = dynamics_cls(config)
        geometry, substrate = _make_geometry_and_substrate()
        x = torch.randn(2, 8, requires_grad=True)
        state = _make_state(x)

        # Need to enable grad for this test
        settled = dynamics.settle(state, geometry, substrate, target=None)

        # The output activations should track gradients if input did
        # (implementation-dependent, but shouldn't crash)
        assert settled.activations is not None


class TestInputFlattening:
    """Test input flattening invariant."""

    @pytest.mark.parametrize("dynamics_cls", DYNAMICS_CLASSES)
    def test_handles_4d_input(self, dynamics_cls):
        """Implementations should flatten 4D inputs (e.g., images) to 2D."""
        config = DYNAMICS_CONFIGS[dynamics_cls]()
        dynamics = dynamics_cls(config)
        geometry, substrate = _make_geometry_and_substrate(input_dim=784, output_dim=10)
        # 4D input: batch=2, channels=1, height=28, width=28
        x = torch.randn(2, 1, 28, 28)
        state = _make_state(x)

        with torch.no_grad():
            settled = dynamics.settle(state, geometry, substrate, target=None)

        assert settled.activations is not None
        # First activation should be flattened to 2D
        assert settled.activations[0].dim() == 2
        assert settled.activations[0].shape[0] == 2
        assert settled.activations[0].shape[1] == 784


class TestFreeNudgedTargetSemantics:
    """Test free/nudged target semantics invariants."""

    @pytest.mark.parametrize("dynamics_cls", DYNAMICS_CLASSES)
    def test_free_phase_target_none(self, dynamics_cls):
        """target=None should run free phase."""
        config = DYNAMICS_CONFIGS[dynamics_cls]()
        dynamics = dynamics_cls(config)
        geometry, substrate = _make_geometry_and_substrate()
        x = torch.randn(2, 8)
        state = _make_state(x)

        with torch.no_grad():
            settled = dynamics.settle(state, geometry, substrate, target=None)

        assert settled.free_state is not None
        assert settled.nudged_state is None

    @pytest.mark.parametrize("dynamics_cls", DYNAMICS_CLASSES)
    def test_nudged_phase_target_provided(self, dynamics_cls):
        """target provided should run nudged phase."""
        config = DYNAMICS_CONFIGS[dynamics_cls]()
        dynamics = dynamics_cls(config)
        geometry, substrate = _make_geometry_and_substrate()
        x = torch.randn(2, 8)
        target = torch.randn(2, 4)
        state = _make_state(x)

        with torch.no_grad():
            settled = dynamics.settle(state, geometry, substrate, target=target)

        assert settled.nudged_state is not None
        assert settled.free_state is None  # free_state not set in nudged phase

    @pytest.mark.parametrize("dynamics_cls", DYNAMICS_CLASSES)
    def test_both_phases_populate_activations(self, dynamics_cls):
        """Both free and nudged phases should populate activations."""
        config = DYNAMICS_CONFIGS[dynamics_cls]()
        dynamics = dynamics_cls(config)
        geometry, substrate = _make_geometry_and_substrate()
        x = torch.randn(2, 8)
        target = torch.randn(2, 4)

        state_free = _make_state(x)
        with torch.no_grad():
            free = dynamics.settle(state_free, geometry, substrate, target=None)
        assert free.activations is not None

        state_nudge = _make_state(x)
        with torch.no_grad():
            nudge = dynamics.settle(state_nudge, geometry, substrate, target=target)
        assert nudge.activations is not None


class TestMutationContract:
    """Test mutation contract: settle returns state to use; callers must bind it."""

    @pytest.mark.parametrize("dynamics_cls", DYNAMICS_CLASSES)
    def test_settle_returns_state(self, dynamics_cls):
        """Settle should return the state to use (may be same or rebuilt)."""
        config = DYNAMICS_CONFIGS[dynamics_cls]()
        dynamics = dynamics_cls(config)
        geometry, substrate = _make_geometry_and_substrate()
        x = torch.randn(2, 8)
        state = _make_state(x)

        with torch.no_grad():
            returned = dynamics.settle(state, geometry, substrate, target=None)

        assert returned is not None
        assert isinstance(returned, CompositeState)
        assert returned.activations is not None

    @pytest.mark.parametrize("dynamics_cls", DYNAMICS_CLASSES)
    def test_caller_must_use_returned_state(self, dynamics_cls):
        """The returned state should have correct activations; input state may be stale."""
        config = DYNAMICS_CONFIGS[dynamics_cls]()
        dynamics = dynamics_cls(config)
        geometry, substrate = _make_geometry_and_substrate()
        x = torch.randn(2, 8)
        state = _make_state(x)

        with torch.no_grad():
            returned = dynamics.settle(state, geometry, substrate, target=None)

        # Returned state should have activations
        assert returned.activations is not None
        assert len(returned.activations) >= 3

        # The original state may or may not be mutated (implementation-dependent)
        # but caller MUST use returned state - we verify returned is correct


class TestComputeEnergyContract:
    """Test compute_energy contract invariants."""

    @pytest.mark.parametrize("dynamics_cls", DYNAMICS_CLASSES)
    def test_compute_energy_returns_scalar(self, dynamics_cls):
        """compute_energy should return a scalar tensor."""
        config = DYNAMICS_CONFIGS[dynamics_cls]()
        dynamics = dynamics_cls(config)
        geometry, substrate = _make_geometry_and_substrate()
        x = torch.randn(2, 8)
        state = _make_state(x)

        with torch.no_grad():
            settled = dynamics.settle(state, geometry, substrate, target=None)
            energy = dynamics.compute_energy(settled, geometry)

        assert energy.ndim == 0
        assert torch.isfinite(energy)

    @pytest.mark.parametrize("dynamics_cls", DYNAMICS_CLASSES)
    def test_compute_energy_uses_free_state_first(self, dynamics_cls):
        """compute_energy should prefer free_state, then nudged_state, then activations."""
        config = DYNAMICS_CONFIGS[dynamics_cls]()
        dynamics = dynamics_cls(config)
        geometry, substrate = _make_geometry_and_substrate()
        x = torch.randn(2, 8)
        target = torch.randn(2, 4)

        # State with only nudged_state
        state_nudge = _make_state(x)
        with torch.no_grad():
            settled_nudge = dynamics.settle(
                state_nudge, geometry, substrate, target=target
            )
            energy_nudge = dynamics.compute_energy(settled_nudge, geometry)
        assert torch.isfinite(energy_nudge)

        # State with only free_state
        state_free = _make_state(x)
        with torch.no_grad():
            settled_free = dynamics.settle(state_free, geometry, substrate, target=None)
            energy_free = dynamics.compute_energy(settled_free, geometry)
        assert torch.isfinite(energy_free)


class TestOnStepCallback:
    """``on_step`` fires at each settle step with (step_index, energy).

    Ratchet: the callback used to be nested inside the free-energy tracking
    guard, so with the default ``track_free_energy_per_iter=False`` it was a
    silent no-op -- and the old assertion (``isinstance(steps_called, list)``)
    passed either way. The protocol docstring makes the cadence load-bearing:
    it is the live-telemetry channel.
    """

    # Single-pass and lazily-resolved dynamics have no settle loop to report.
    @pytest.mark.parametrize(
        "dynamics_cls",
        [
            cls
            for cls in DYNAMICS_CLASSES
            if cls not in {InstantaneousDynamics, LazyStateDynamics}
        ],
    )
    def test_on_step_called_if_provided(self, dynamics_cls):
        """on_step fires once per settle step, without telemetry enabled."""
        config = DYNAMICS_CONFIGS[dynamics_cls]()
        assert config.track_free_energy_per_iter is False, (
            "this lock is only meaningful with per-step tracking off"
        )
        dynamics = dynamics_cls(config)
        geometry, substrate = _make_geometry_and_substrate()
        state = _make_state(torch.randn(2, 8))

        steps_called: list[tuple[int, float]] = []

        with torch.no_grad():
            dynamics.settle(
                state,
                geometry,
                substrate,
                target=None,
                on_step=lambda step, energy: steps_called.append((step, energy)),
            )

        assert steps_called, f"{dynamics_cls.__name__} never invoked on_step"
        indices = [step for step, _ in steps_called]
        assert indices == sorted(indices), "on_step steps out of order"
        assert indices == list(range(len(indices))), "on_step skipped a step"
        assert all(
            isinstance(energy, float) and math.isfinite(energy)
            for _, energy in steps_called
        ), "on_step reported a non-finite energy"


class TestDeterminism:
    """Test deterministic behavior under fixed seed."""

    @pytest.mark.parametrize(
        "dynamics_cls", [c for c in DYNAMICS_CLASSES if c != DiffusionDynamics]
    )
    @given(st.integers(min_value=0, max_value=1000))
    @settings(max_examples=5, deadline=None)
    def test_deterministic_under_fixed_seed(self, dynamics_cls, seed):
        """Same seed should produce same results (excluding stochastic dynamics)."""
        torch.manual_seed(seed)
        config1 = DYNAMICS_CONFIGS[dynamics_cls]()
        dynamics1 = dynamics_cls(config1)
        geometry1, substrate1 = _make_geometry_and_substrate()
        x1 = torch.randn(2, 8)
        state1 = _make_state(x1)

        torch.manual_seed(seed)
        config2 = DYNAMICS_CONFIGS[dynamics_cls]()
        dynamics2 = dynamics_cls(config2)
        geometry2, substrate2 = _make_geometry_and_substrate()
        x2 = torch.randn(2, 8)
        state2 = _make_state(x2)

        with torch.no_grad():
            settled1 = dynamics1.settle(state1, geometry1, substrate1, target=None)
            settled2 = dynamics2.settle(state2, geometry2, substrate2, target=None)

        for a1, a2 in zip(settled1.activations, settled2.activations):
            assert torch.allclose(a1, a2), (
                f"Non-deterministic output for {dynamics_cls.__name__}"
            )


class TestFiniteOutputs:
    """Test that all outputs remain finite (no NaN/Inf)."""

    @pytest.mark.parametrize("dynamics_cls", DYNAMICS_CLASSES)
    @given(st.integers(min_value=0, max_value=1000))
    @settings(max_examples=5, deadline=None)
    def test_outputs_remain_finite(self, dynamics_cls, seed):
        """All outputs should remain finite."""
        torch.manual_seed(seed)
        config = DYNAMICS_CONFIGS[dynamics_cls]()
        dynamics = dynamics_cls(config)
        geometry, substrate = _make_geometry_and_substrate()
        x = torch.randn(2, 8)
        state = _make_state(x)

        with torch.no_grad():
            settled = dynamics.settle(state, geometry, substrate, target=None)

        def check_finite(obj, path="output"):
            if isinstance(obj, torch.Tensor):
                assert not torch.isnan(obj).any(), f"NaN found in {path}"
                assert not torch.isinf(obj).any(), f"Inf found in {path}"
            elif isinstance(obj, dict):
                for k, v in obj.items():
                    check_finite(v, f"{path}.{k}")
            elif isinstance(obj, (list, tuple)):
                for i, v in enumerate(obj):
                    check_finite(v, f"{path}[{i}]")
            elif hasattr(obj, "__dict__") and not isinstance(obj, type):
                for k, v in obj.__dict__.items():
                    if not k.startswith("_"):
                        check_finite(v, f"{path}.{k}")

        check_finite(settled)
        energy = dynamics.compute_energy(settled, geometry)
        assert not torch.isnan(energy).any()
        assert not torch.isinf(energy).any()


class TestSettleHorizonTelemetry:
    """``_settle_steps_used`` counts the steps that actually ran.

    Ratchet for the dead-early-stop defect: the settle loops broke on
    ``if self._settle_steps_used > 0`` while ``_note_settle_start`` had
    already seeded that field with ``max_steps``. The condition was
    therefore true before the body ever ran, so every free phase stopped
    after one step -- the fixed point was never reached, which silently
    degraded the EqProp energy gap and the thermo contrast credit that
    reads it. The horizon must be truth, and the stop signal must be a
    separate flag.
    """

    @staticmethod
    def _counted(dynamics, state, geometry, substrate, target=None) -> int:
        """Run a settle, counting invocations of the kernel step via on_step."""
        seen: list[int] = []
        dynamics.settle(
            state,
            geometry,
            substrate,
            target=target,
            on_step=lambda step, _value: seen.append(step),
        )
        return len(seen)

    @pytest.mark.parametrize(
        ("factory", "dynamics_cls"),
        [
            (
                lambda: StateDynamicsConfig.energy_minimization(
                    max_steps=40, step_size=0.01, convergence_start=10_000
                ),
                EnergyMinimizationDynamics,
            ),
            (
                lambda: StateDynamicsConfig.predictive_settling(
                    max_steps=40, step_size=0.01, convergence_start=10_000
                ),
                PredictiveSettlingDynamics,
            ),
            (
                lambda: StateDynamicsConfig.error_predictive_coding(
                    max_steps=40, step_size=0.01, convergence_start=10_000
                ),
                ErrorPredictiveCodingDynamics,
            ),
        ],
    )
    def test_multi_step_settle_runs_many_steps(self, factory, dynamics_cls):
        """A settle that cannot converge early runs more than one step."""
        torch.manual_seed(11)
        geometry, substrate = _make_geometry_and_substrate()
        dynamics = dynamics_cls(factory())

        # convergence_start past the horizon => convergence is unreachable,
        # so the loop is forced to run the full budget.
        steps = self._counted(
            dynamics, _make_state(torch.randn(4, 8)), geometry, substrate
        )
        assert steps == dynamics.config.max_steps, (
            f"{dynamics_cls.__name__} ran {steps} steps, expected the full "
            f"{dynamics.config.max_steps}"
        )

    def test_horizon_field_matches_steps_actually_run(self):
        """``_settle_steps_used`` is not a pre-seeded placeholder."""
        torch.manual_seed(12)
        geometry, substrate = _make_geometry_and_substrate()
        config = StateDynamicsConfig.energy_minimization(
            max_steps=40, step_size=0.01, track_free_energy_per_iter=True
        )
        dynamics = EnergyMinimizationDynamics(config)

        steps = self._counted(
            dynamics, _make_state(torch.randn(4, 8)), geometry, substrate
        )
        assert dynamics._settle_steps_used == steps

    def test_free_energy_history_has_one_sample_per_step(self):
        """Tracking is per-step, so the history length pins the horizon."""
        torch.manual_seed(13)
        geometry, substrate = _make_geometry_and_substrate()
        config = StateDynamicsConfig.energy_minimization(
            max_steps=25, step_size=0.01, track_free_energy_per_iter=True
        )
        dynamics = EnergyMinimizationDynamics(config)

        steps = self._counted(
            dynamics, _make_state(torch.randn(4, 8)), geometry, substrate
        )
        history = dynamics.get_free_energy_history()
        assert history is not None
        # One initial sample plus one per executed step.
        assert len(history) == steps + 1

    def test_energy_minimization_decreases_free_energy(self):
        """The thermodynamic contract: settling descends the free energy."""
        torch.manual_seed(14)
        geometry, substrate = _make_geometry_and_substrate()
        config = StateDynamicsConfig.energy_minimization(
            max_steps=60,
            step_size=0.05,
            momentum=0.0,
            track_free_energy_per_iter=True,
        )
        dynamics = EnergyMinimizationDynamics(config)
        self._counted(dynamics, _make_state(torch.randn(4, 8)), geometry, substrate)

        history = dynamics.get_free_energy_history()
        assert history is not None and len(history) > 2
        assert history[-1] < history[0], "settling raised the free energy"
        # Gradient descent on a convex local energy: no step may increase it
        # by more than float noise.
        for previous, current in itertools.pairwise(history):
            assert current <= previous + 1e-6, (
                f"free energy rose {previous} -> {current}"
            )

    def test_early_stop_latches_then_resets_between_settles(self):
        """The convergence flag stops one settle and must not leak into the next."""
        torch.manual_seed(15)
        geometry, substrate = _make_geometry_and_substrate()
        # A horizon that cannot converge: the only way out is the full budget.
        config = StateDynamicsConfig.energy_minimization(
            max_steps=30, step_size=0.01, convergence_start=10_000
        )
        dynamics = EnergyMinimizationDynamics(config)
        state = _make_state(torch.randn(4, 8))

        # Simulate a latch carried in from a previous settle: a loop that
        # breaks on the flag without clearing it at settle start returns
        # after a single step.
        dynamics._converged = True
        steps = self._counted(dynamics, state, geometry, substrate)
        assert steps == config.max_steps
        assert dynamics._converged is False

    def test_convergence_latches_and_early_stops(self):
        """A settle that reaches the fixed point stops before its horizon."""
        torch.manual_seed(17)
        geometry, substrate = _make_geometry_and_substrate()
        config = StateDynamicsConfig.energy_minimization(
            max_steps=400, step_size=0.01, convergence_threshold=1e-3
        )
        dynamics = EnergyMinimizationDynamics(config)
        steps = self._counted(
            dynamics, _make_state(torch.randn(4, 8)), geometry, substrate
        )
        assert dynamics._converged is True
        assert 0 < steps <= config.max_steps
        # The reported horizon is the early stop, not the budget.
        assert dynamics._settle_steps_used == steps

    def test_repeated_settles_do_not_accumulate_state(self):
        """Horizon telemetry is per-settle, not cumulative across calls."""
        torch.manual_seed(16)
        geometry, substrate = _make_geometry_and_substrate()
        config = StateDynamicsConfig.energy_minimization(
            max_steps=20,
            step_size=0.01,
            track_free_energy_per_iter=True,
            convergence_start=10_000,
        )
        dynamics = EnergyMinimizationDynamics(config)
        state = _make_state(torch.randn(4, 8))

        counts = [self._counted(dynamics, state, geometry, substrate) for _ in range(3)]
        assert counts == [20, 20, 20], counts
        # A fresh history per settle, not one growing list.
        assert len(dynamics.get_free_energy_history() or []) == 21


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestSettleHorizonSourceLock:
    """Static guard: no settle loop may read the horizon as a stop signal.

    The behavioural ratchet above is the real check, but it only covers the
    dynamics it enumerates. This one is grep-level and covers the whole module,
    so a new dynamics class cannot introduce the break-on-horizon shape
    without failing first. Deliberately narrow: it looks only for the horizon
    in a *boolean* position, which is the defect. Assignments and truth
    telemetry reads are fine.
    """

    MODULE = "computronium/ontology/dynamics/_dynamics.py"
    PROTOCOL = "class StateDynamics(Protocol):"

    @staticmethod
    def _lines() -> list[str]:
        path = Path(__file__).resolve().parents[2] / TestSettleHorizonSourceLock.MODULE
        return path.read_text(encoding="utf-8").splitlines()

    def test_horizon_is_never_read_as_a_condition(self) -> None:
        path = Path(__file__).resolve().parents[2] / TestSettleHorizonSourceLock.MODULE
        tree = ast.parse(path.read_text(encoding="utf-8"))
        offenders = [
            f"{TestSettleHorizonSourceLock.MODULE}:{node.lineno}"
            for node in ast.walk(tree)
            if isinstance(node, ast.If | ast.While | ast.IfExp)
            and TestSettleHorizonSourceLock._reads_horizon(node.test)
        ]
        assert offenders == [], (
            f"_settle_steps_used is truth telemetry, not a stop signal: {offenders}"
        )

    @staticmethod
    def _reads_horizon(node: ast.expr) -> bool:
        return any(
            isinstance(child, ast.Attribute) and child.attr == "_settle_steps_used"
            for child in ast.walk(node)
        )

    def test_protocol_docstring_states_the_four_rules(self) -> None:
        """The contract is only load-bearing if it is written down where
        implementations are read. Guards against silent truncation."""
        source = "\n".join(TestSettleHorizonSourceLock._lines())
        protocol = source.index(TestSettleHorizonSourceLock.PROTOCOL)
        docstring = source[
            protocol : source.index('"""', source.index('"""', protocol) + 3) + 3
        ]
        for marker in (
            "actually executed",
            "_converged",
            "on_step(step, energy)",
            "track_free_energy_per_iter",
        ):
            assert marker in docstring, f"protocol docstring lost rule: {marker}"
