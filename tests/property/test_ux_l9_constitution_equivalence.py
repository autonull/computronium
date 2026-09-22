"""UX-L9: Constitution Health Panel equivalence lock.

Constitution panel metrics must match StabilityMonitor output byte-identically.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest
import torch
from torch import Tensor

if TYPE_CHECKING:
    from stability import (
        StabilityGuard,
        SettlingMonitor,
        LyapunovEstimator,
        JacobianAmplificationEstimator,
        ResourceUsage,
    )


@dataclass(frozen=True, slots=True)
class ConstitutionMetrics:
    """The 6 constitutional invariants as computed by the panel."""

    causality_dag: bool          # No circular dependencies
    passivity: bool              # Δℰ ≤ ℰ_in
    lyapunov_bound: bool         # ρ(J_F) ≤ τ
    resource_ceiling: bool       # ||Z|| + |Ω| ≤ budget
    protocol_conformance: bool   # Valid per SystemConfig.validate()
    recursion_invariant: bool    # Well-founded recursion

    # Raw metric values for byte-identical comparison
    spectral_radius: float
    lyapunov_exponent: float
    jacobian_amplification: float
    settling_steps: int
    energy_consumed: float
    energy_injected: float
    resource_usage: float
    resource_budget: float
    max_recursion_depth: int


def _compute_constitution_from_stability(
    model: torch.nn.Module,
    input_tensor: Tensor,
    resource_budget: float = 1e9,
    max_recursion_depth: int = 10,
    tau: float = 1.029,
) -> ConstitutionMetrics:
    """Compute constitution metrics using the stability package directly.

    This is the reference implementation that the Constitution Health Panel must match.
    Uses the external (dict-based) API for simplicity.
    """
    from stability import (
        StabilityGuard,
        SettlingMonitor,
        LyapunovEstimator,
        JacobianAmplificationEstimator,
        ResourceUsage,
        GuardConfig,
        SettlingConfig,
        LyapunovConfig,
        JacobianAmplificationConfig,
    )

    # Create estimators using config objects
    guard = StabilityGuard(GuardConfig(threshold=tau, statistic="fast_proxy", window=10))
    settling_monitor = SettlingMonitor(SettlingConfig(tolerance=1e-4, max_steps=1000))
    lyapunov_estimator = LyapunovEstimator(LyapunovConfig(num_steps=50, fast_mode=True))
    jacobian_estimator = JacobianAmplificationEstimator(
        JacobianAmplificationConfig(fast_mode=True)
    )

    # Create simple external transition function
    def transition_fn(state: dict[str, object]) -> dict[str, object]:
        x = state.get("x")
        if x is None or not isinstance(x, torch.Tensor):
            return {"x": torch.zeros_like(input_tensor)}
        with torch.no_grad():
            y = model(x)
        return {"x": y, "y": y}

    # Create initial state
    initial_state = {"x": input_tensor}

    # Compute metrics using external API
    # 1. Lyapunov bound (spectral radius proxy) - use guard's external probe
    lyap_exp = lyapunov_estimator._fast_proxy(transition_fn, initial_state)  # type: ignore
    jac_amp = guard._fast_proxy_external(transition_fn, initial_state)

    # 2. Settling (passivity proxy) - use external windowed growth
    settling_steps = 0
    step_norms = []
    current = initial_state
    for _ in range(1000):
        x_before = current.get("x")
        if not isinstance(x_before, torch.Tensor):
            break
        before_norm = float(x_before.norm().item())
        current = transition_fn(current)
        x_after = current.get("x")
        if not isinstance(x_after, torch.Tensor):
            break
        after_norm = float(x_after.norm().item())
        delta_norm = abs(after_norm - before_norm) / (before_norm + 1e-8)
        step_norms.append(delta_norm)
        settling_steps += 1
        if delta_norm < 1e-4:
            break

    energy_injected = float(input_tensor.norm().item())
    energy_consumed = sum(step_norms) if step_norms else 0.0

    # 3. Resource usage
    resource_usage_obj = ResourceUsage.measure(model, input_tensor)
    resource_usage_val = resource_usage_obj.compute + resource_usage_obj.memory * 1e6

    # 4. Causality (DAG) - check model has no cycles (simplified)
    # In practice, this would check the system coordinate DAG
    causality_ok = True  # Placeholder - would check SystemConfig.validate()

    # 5. Protocol conformance
    protocol_ok = True  # Placeholder - would check SystemConfig.validate()

    # 6. Recursion invariant
    recursion_ok = max_recursion_depth < 100  # Placeholder

    return ConstitutionMetrics(
        causality_dag=causality_ok,
        passivity=energy_consumed <= energy_injected + 1e-6,
        lyapunov_bound=lyap_exp <= tau,
        resource_ceiling=resource_usage_val <= resource_budget,
        protocol_conformance=protocol_ok,
        recursion_invariant=recursion_ok,
        spectral_radius=jac_amp,  # Using Jacobian amplification as ρ(J_F) proxy
        lyapunov_exponent=lyap_exp,
        jacobian_amplification=jac_amp,
        settling_steps=settling_steps,
        energy_consumed=energy_consumed,
        energy_injected=energy_injected,
        resource_usage=resource_usage_val,
        resource_budget=resource_budget,
        max_recursion_depth=max_recursion_depth,
    )


def _compute_constitution_from_panel(
    model: torch.nn.Module,
    input_tensor: Tensor,
    resource_budget: float = 1e9,
    max_recursion_depth: int = 10,
    tau: float = 1.029,
) -> ConstitutionMetrics:
    """Compute constitution metrics using the panel implementation.

    This will be implemented once the Constitution Health Panel exists.
    For now, it delegates to the reference implementation.
    """
    # TODO: Import and use the actual panel implementation
    # from computronium.ui.components.constitution_health import compute_constitution_metrics
    # return compute_constitution_metrics(model, input_tensor, resource_budget, max_recursion_depth, tau)

    # Placeholder: use reference implementation
    return _compute_constitution_from_stability(
        model, input_tensor, resource_budget, max_recursion_depth, tau
    )


class TestConstitutionEquivalence:
    """UX-L9: Panel metrics must match StabilityMonitor byte-identically."""

    @pytest.fixture(scope="class")
    def simple_model(self) -> torch.nn.Module:
        """A simple linear model for testing."""
        return torch.nn.Linear(10, 5)

    @pytest.fixture(scope="class")
    def input_tensor(self) -> Tensor:
        """Standard input tensor."""
        return torch.randn(4, 10)

    @pytest.mark.skip(reason="ConstitutionHealthPanel not yet implemented; will verify byte-identical match when panel exists")
    def test_constitution_metrics_byte_identical(
        self, simple_model: torch.nn.Module, input_tensor: Tensor
    ) -> None:
        """Panel and StabilityMonitor must produce identical metrics."""
        ref = _compute_constitution_from_stability(simple_model, input_tensor)
        panel = _compute_constitution_from_panel(simple_model, input_tensor)

        # Boolean invariants must match exactly
        assert panel.causality_dag == ref.causality_dag, "Causality (DAG) mismatch"
        assert panel.passivity == ref.passivity, "Passivity mismatch"
        assert panel.lyapunov_bound == ref.lyapunov_bound, "Lyapunov bound mismatch"
        assert panel.resource_ceiling == ref.resource_ceiling, "Resource ceiling mismatch"
        assert panel.protocol_conformance == ref.protocol_conformance, "Protocol conformance mismatch"
        assert panel.recursion_invariant == ref.recursion_invariant, "Recursion invariant mismatch"

        # Raw metrics must match byte-identically (within float tolerance)
        assert panel.spectral_radius == pytest.approx(ref.spectral_radius, rel=1e-6), (
            f"Spectral radius mismatch: panel={panel.spectral_radius}, ref={ref.spectral_radius}"
        )
        assert panel.lyapunov_exponent == pytest.approx(ref.lyapunov_exponent, rel=1e-6), (
            f"Lyapunov exponent mismatch: panel={panel.lyapunov_exponent}, ref={ref.lyapunov_exponent}"
        )
        assert panel.jacobian_amplification == pytest.approx(ref.jacobian_amplification, rel=1e-6), (
            f"Jacobian amplification mismatch: panel={panel.jacobian_amplification}, ref={ref.jacobian_amplification}"
        )
        assert panel.settling_steps == ref.settling_steps, "Settling steps mismatch"
        assert panel.energy_consumed == pytest.approx(ref.energy_consumed, rel=1e-6), "Energy consumed mismatch"
        assert panel.energy_injected == pytest.approx(ref.energy_injected, rel=1e-6), "Energy injected mismatch"
        assert panel.resource_usage == pytest.approx(ref.resource_usage, rel=1e-6), "Resource usage mismatch"
        assert panel.resource_budget == ref.resource_budget, "Resource budget mismatch"
        assert panel.max_recursion_depth == ref.max_recursion_depth, "Max recursion depth mismatch"

    def test_constitution_explorer_strings_exist(self) -> None:
        """All 6 invariants must have Explorer register strings in glossary."""
        from computronium.ui.glossary_service import get_glossary_service

        svc = get_glossary_service()
        required_keys = [
            "constitution_health",
            "causality_dag",
            "passivity",
            "lyapunov_bound",
            "resource_ceiling",
            "protocol_conformance",
            "recursion_invariant",
        ]

        for key in required_keys:
            assert svc.has(key), f"Missing glossary key: {key}"
            explorer = svc.get(key, register="explorer")
            lab = svc.get(key, register="lab")
            assert explorer != key, f"Key '{key}' has no Explorer translation"
            assert lab != key, f"Key '{key}' has no Lab translation"

    def test_constitution_explorer_readability(self) -> None:
        """Explorer strings for constitution must be ≤ FK grade 8."""
        from computronium.ui.glossary_service import get_glossary_service
        import re

        svc = get_glossary_service()
        keys = [
            "causality_dag",
            "passivity",
            "lyapunov_bound",
            "resource_ceiling",
            "protocol_conformance",
            "recursion_invariant",
        ]

        for key in keys:
            explorer = svc.get(key, register="explorer")
            # Simple FK approximation: short sentences, simple words
            words = len(explorer.split())
            sentences = len(re.split(r"[.!?]+", explorer)) or 1
            avg_words_per_sentence = words / sentences
            # FK grade ≈ 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59
            # Rough check: avg words/sentence ≤ 15, no overly complex words
            assert avg_words_per_sentence <= 15, (
                f"Explorer string for '{key}' too complex: '{explorer}' "
                f"(avg {avg_words_per_sentence:.1f} words/sentence)"
            )


class TestConstitutionPanelIntegration:
    """Integration tests for the Constitution Health Panel component."""

    def test_panel_exists(self) -> None:
        """ConstitutionHealthPanel component must exist."""
        # TODO: Uncomment when component is implemented
        # from computronium.ui.components.constitution_health import ConstitutionHealthPanel
        # assert ConstitutionHealthPanel is not None
        pytest.skip("ConstitutionHealthPanel not yet implemented")

    def test_panel_renders_all_six_invariants(self) -> None:
        """Panel must render all 6 invariants with status indicators."""
        pytest.skip("ConstitutionHealthPanel not yet implemented")

    def test_panel_register_aware(self) -> None:
        """Panel must show plain language in Explorer, technical in Lab."""
        pytest.skip("ConstitutionHealthPanel not yet implemented")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])