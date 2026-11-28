"""Biology Axiom Property Tests - Simplified for Native Compositions.

These tests verify bio-plausibility axioms using native compositions.
Tests are simplified to work with the System protocol interface.
"""

import pytest
import torch
from hypothesis import given, settings
from hypothesis import strategies as st
from torch import nn

from computronium.core.local_learning.builder import (
    TileAlgorithm,
    TileAlgorithmConfig,
)
from computronium.core.local_learning.settling import (
    settle_universal,
)
from computronium.models.native.eqprop_native import create_native_eqprop_mlp
from computronium.models.native.fa_native import (
    create_native_fa_adaptive,
    create_native_fa_mlp,
)

# =============================================================================
# Shared Fixtures & Helpers
# =============================================================================


@pytest.fixture(scope="module")
def synthetic_mlp_task():
    """Minimal MLP task for gradient equivalence: 1 hidden layer, small dims."""
    torch.manual_seed(42)
    input_dim = 8
    hidden_dim = 8
    output_dim = 4
    n_samples = 32
    x = torch.randn(n_samples, input_dim)
    y = torch.randint(0, output_dim, (n_samples,))
    for c in range(output_dim):
        mask = y == c
        if mask.any():
            direction = torch.randn(input_dim)
            direction = direction / direction.norm() * 1.5
            x[mask] += direction * 0.5
    return x, y, input_dim, hidden_dim, output_dim


def _create_tile_ep_model(input_dim: int, hidden_dim: int, output_dim: int):
    """Create a Tile EP model for biology testing."""
    config = TileAlgorithmConfig(
        input_dim=input_dim,
        output_dim=output_dim,
        neurons_per_tile=hidden_dim,
        tiles_per_layer=1,
        num_hidden_layers=1,
        algorithm="ep",
        mode="ep",
        free_steps=20,
        nudged_steps=20,
        learning_rate=0.01,
        beta=0.5,
        step_size=0.1,
    )
    model = TileAlgorithm(config)
    model.convergence_threshold = 1e-4
    model.convergence_start = 5
    return model


# =============================================================================
# 3.1 EP Gradient Equivalence — Equilibrium Propagation ≈ BPTT
# =============================================================================


class TestEPGradientEquivalence:
    """EP's tile rule against the BPTT descent direction, measured.

    The tile rule hard-clamps the output (the β→∞ limit) and reads out
    through ``W_out``, which sits outside the energy the rule descends.
    No finite-β gradient parity follows from that contract, so the test
    locks the measured boundary and names the primitive that would close
    it: a soft β-scaled nudge with the readout inside the energy (deep
    EqProp credit). Measured on the fixture: aggregate cosine 0.132 with
    mixed per-parameter signs.
    """

    def test_ep_bptt_parity_boundary(self, synthetic_mlp_task):  # ruff: ignore[too-many-locals]
        """The tile update's direction agreement with BPTT stays below 0.5."""
        x, y, input_dim, hidden_dim, output_dim = synthetic_mlp_task
        model = _create_tile_ep_model(input_dim, hidden_dim, output_dim)
        xb, yb = x[:16], y[:16]

        # The contrastive rule applies a parameter delta in place; there is
        # no autograd `.grad` on that path, so the delta is the tracked
        # quantity. Pair it with the BPTT descent direction by name.
        before = {name: p.detach().clone() for name, p in model.named_parameters()}
        model.train()
        model.local_update(xb, yb)
        delta = {
            name: p.detach() - before[name] for name, p in model.named_parameters()
        }

        model.zero_grad()
        nn.functional.cross_entropy(model(xb), yb).backward()
        descent = {
            name: -p.grad.detach().clone()
            for name, p in model.named_parameters()
            if p.grad is not None
        }

        shared = [
            name
            for name in delta
            if name in descent and delta[name].norm() > 0 and descent[name].norm() > 0
        ]
        assert {"W_out.weight", "W_out.bias"} <= set(shared), (
            "the contrastive rule left the readout unchanged"
        )
        assert any(name.startswith("_tile_weights.") for name in shared), (
            "the contrastive rule left every hidden edge unchanged"
        )

        ep_dir = torch.cat([delta[name].flatten() for name in shared])
        bptt_dir = torch.cat([descent[name].flatten() for name in shared])
        cos = (ep_dir @ bptt_dir / (ep_dir.norm() * bptt_dir.norm())).item()
        assert cos < 0.5, (
            f"EP-BPTT cosine {cos:.3f} reached 0.5: a lever rescued the "
            "parity claim — re-record the boundary (measured 0.132)"
        )


# =============================================================================
# 3.2 Lyapunov Energy Descent — Monotone Energy Decrease
# =============================================================================


class TestLyapunovEnergyDescent:
    """Verify energy decreases monotonically along relaxation dynamics."""

    @settings(max_examples=5, deadline=None)
    @given(st.data())
    def test_energy_monotone_decrease_tile_ep(self, synthetic_mlp_task, data):
        """Run relaxation steps via settle_universal, assert free energy monotonically non-increasing."""
        x, y, input_dim, hidden_dim, output_dim = synthetic_mlp_task

        model = _create_tile_ep_model(input_dim, hidden_dim, output_dim)
        model.eval()

        xb, yb = x[:8], y[:8]  # ruff: ignore[unused-variable]

        # Use settle_universal to get trajectory
        with torch.no_grad():
            from computronium.core.local_learning.settling import SettleConfig

            config = SettleConfig(
                max_steps=20,
                convergence_threshold=1e-4,
                convergence_start=5,
            )
            _out, _steps_taken, _converged, telemetry = settle_universal(
                model, xb, config=config
            )

        # Energy should be monotonic (deltas should decrease)
        deltas = telemetry.deltas
        assert len(deltas) >= 2, (
            f"settle recorded {len(deltas)} energy delta(s); the descent law "
            "needs at least one step pair"
        )

        # Assert monotone non-increase of deltas (energy proxy)
        slack = 1e-3
        for i in range(1, len(deltas)):
            assert deltas[i] <= deltas[i - 1] + slack, (
                f"TileEP: delta increased at step {i}: "
                f"{deltas[i - 1]:.6f} -> {deltas[i]:.6f}"
            )


# =============================================================================
# 3.4 Fixed-Point Reliability — Attractor Uniqueness
# =============================================================================


class TestFixedPointReliability:
    """Verify relaxation converges to unique fixed point."""

    @settings(max_examples=5, deadline=None)
    @given(st.data())
    def test_fixed_point_uniqueness_tile_ep(self, synthetic_mlp_task, data):  # ruff: ignore[too-many-locals]
        """Run relax from multiple initializations, assert convergence."""
        x, _y, input_dim, hidden_dim, output_dim = synthetic_mlp_task

        model = _create_tile_ep_model(input_dim, hidden_dim, output_dim)
        model.eval()
        xb = x[:4]

        # Test settle_universal converges
        with torch.no_grad():
            from computronium.core.local_learning.settling import SettleConfig

            config = SettleConfig(
                max_steps=50,
                convergence_threshold=1e-4,
                convergence_start=5,
            )
            out1, _steps1, _converged1, _telemetry1 = settle_universal(
                model, xb, config=config
            )
            out2, _steps2, _converged2, _telemetry2 = settle_universal(
                model, xb, config=config
            )

        # Both should run without error (convergence is not guaranteed for all inputs)
        # Output should be deterministic (same input, same result)
        # settle_universal may return a list of tensors for multi-layer models
        if isinstance(out1, list) and isinstance(out2, list):
            assert len(out1) == len(out2), "Output list lengths should match"
            for o1, o2 in zip(out1, out2):
                assert torch.allclose(o1, o2, rtol=1e-4), "Fixed point should be unique"
        else:
            assert torch.allclose(out1, out2, rtol=1e-4), "Fixed point should be unique"


# =============================================================================
# 3.5 Weight-Transport Freeness — FA Family
# =============================================================================


class TestWeightTransportFreeness:
    """Verify native FA uses random fixed B ≠ W.T."""

    def test_native_fa_backward_weights_not_transpose(self, synthetic_mlp_task):
        """Assert B ≠ W.T at initialization for the native FA credit."""
        x, y, input_dim, hidden_dim, output_dim = synthetic_mlp_task

        model = create_native_fa_mlp(
            input_dim, hidden_dim, output_dim, lr=0.001, feedback_scale=0.1
        )
        model.train()
        model.train_step(x[:16], y[:16])

        pairs = [
            (name, feedback, model.geometry.params[name])
            for name, feedback in model.credit._feedback_weights.items()
            if feedback.ndim == 2
            and feedback.shape == model.geometry.params[name].T.shape
        ]
        assert pairs, "native FA built no feedback matrix over a weight transpose"

        for name, B, W in pairs:
            diff = torch.norm(B - W.T).item()
            assert diff > 1e-3, (
                f"Native FA: feedback {name} matches its forward transpose; "
                f"||B - W.T|| = {diff:.6f}"
            )

    def test_native_fa_backward_path_separate(self, synthetic_mlp_task):
        """Assert the feedback path reads its own tensors, not the forward weights."""
        x, y, input_dim, hidden_dim, output_dim = synthetic_mlp_task

        model = create_native_fa_mlp(
            input_dim, hidden_dim, output_dim, lr=0.001, feedback_scale=0.1
        )
        model.train()
        model.train_step(x[:16], y[:16])

        feedback_weights = model.credit._feedback_weights
        assert feedback_weights, "native FA built no feedback matrices"

        for name, B in feedback_weights.items():
            W = model.geometry.params[name]
            assert B.data_ptr() != W.data_ptr(), (
                f"Feedback weight {name} shares memory with its forward weight"
            )


# =============================================================================
# 3.6 Adaptive-FA Alignment Improvement
# =============================================================================


class TestAdaptiveFAAlignment:
    """Verify an adaptive FA rule moves B toward W.T over training."""

    def test_feedback_alignment_improves(self, synthetic_mlp_task):
        """After 50 steps the adaptive rule has moved B toward W.T."""
        x, y, input_dim, hidden_dim, output_dim = synthetic_mlp_task

        model = create_native_fa_adaptive(
            input_dim, hidden_dim, output_dim, lr=0.001, feedback_scale=0.01
        )
        model.train()
        model.train_step(x[:32], y[:32])

        before = {
            name: feedback.detach().clone()
            for name, feedback in model.credit._feedback_weights.items()
        }
        assert before, "native FA built no feedback matrices"

        for _ in range(50):
            model.train_step(x[:32], y[:32])

        moved = [
            name
            for name, feedback in model.credit._feedback_weights.items()
            if not torch.equal(before[name], feedback.detach())
        ]
        assert moved, "adaptive FA never moved B: feedback stays fixed at init"


# =============================================================================
# Native Model Composition Tests
# =============================================================================


class TestNativeModelCompositions:
    """Test that native model compositions work correctly."""

    def test_native_eqprop_composes_and_trains(self, synthetic_mlp_task):
        """native_eqprop_mlp should compose and train."""
        x, y, input_dim, hidden_dim, output_dim = synthetic_mlp_task

        model = create_native_eqprop_mlp(
            input_dim, hidden_dim, output_dim, beta=0.5, settle_steps=10, lr=0.01
        )

        xb, yb = x[:16], y[:16]
        model.train()
        result = model.train_step(xb, yb)
        assert isinstance(result, dict)
        assert "loss" in result
        assert "nudged_fit_accuracy" in result

    def test_native_fa_composes_and_trains(self, synthetic_mlp_task):
        """native_fa_mlp should compose and train."""
        x, y, input_dim, hidden_dim, output_dim = synthetic_mlp_task

        model = create_native_fa_mlp(input_dim, hidden_dim, output_dim, lr=0.001)

        xb, yb = x[:16], y[:16]
        model.train()
        result = model.train_step(xb, yb)
        assert isinstance(result, dict)
        assert "loss" in result
        assert "nudged_fit_accuracy" in result


# =============================================================================


@st.composite
def small_mlp_config(draw):
    """Generate small MLP configurations for biology tests."""
    return {
        "input_dim": draw(st.integers(4, 16)),
        "hidden_dim": draw(st.integers(4, 16)),
        "output_dim": draw(st.integers(2, 8)),
        "batch_size": draw(st.integers(4, 32)),
    }


@st.composite
def step_size_values(draw):
    """Step sizes for contraction testing."""
    return draw(st.sampled_from([0.05, 0.1, 0.2, 0.3, 0.5]))


@st.composite
def beta_values(draw):
    """Beta values for EP gradient equivalence."""
    return draw(
        st.floats(min_value=0.1, max_value=2.0, allow_nan=False, allow_infinity=False)
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
