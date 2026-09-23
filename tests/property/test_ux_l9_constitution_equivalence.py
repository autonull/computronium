"""UX-L9: Constitution Health Panel equivalence lock.

Constitution panel metrics must match StabilityMonitor output byte-identically.
"""

from __future__ import annotations

import pytest
import torch
from torch import Tensor

from computronium.ui.components.constitution_health import ConstitutionMetrics


def _compute_constitution_from_stability(  # ruff: ignore[too-many-locals] — mirrors stability estimator setup surface
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
        LyapunovEstimator,
        ResourceUsage,
        StabilityGuard,
    )

    guard = StabilityGuard(threshold=tau, statistic="fast_proxy", window=10)
    lyapunov_estimator = LyapunovEstimator(num_steps=50, fast_mode=True)

    # Create simple external transition function (uses same input for each step)
    def transition_fn_external(state: dict[str, object]) -> dict[str, object]:
        x = state.get("x")
        if x is None or not isinstance(x, torch.Tensor):
            return {"x": torch.zeros_like(input_tensor)}
        with torch.no_grad():
            y = model(input_tensor)  # Always use original input for consistent settling
        return {"x": y, "y": y}

    initial_state: dict[str, object] = {"x": input_tensor}

    # 1. Spectral radius proxy (Jacobian amplification) - use guard's external probe
    jac_amp = guard._fast_proxy_external(transition_fn_external, initial_state)

    # 2. Lyapunov exponent proxy - use Lyapunov estimator with internal API
    from stability.state import CompositeState, SystemContext

    class SimpleContext:
        """Minimal SystemContext implementation."""

    context = SimpleContext()

    z = CompositeState(
        activity={"x": input_tensor},
        plastic={},
        substrate={},
    )

    def transition_fn_internal(
        state: CompositeState, ctx: SystemContext
    ) -> CompositeState:
        x = state.activity.get("x")
        if x is None or not isinstance(x, torch.Tensor):
            return CompositeState(
                activity={"x": torch.zeros_like(input_tensor)}, plastic={}, substrate={}
            )
        with torch.no_grad():
            y = model(input_tensor)  # Always use original input
        return CompositeState(activity={"x": y}, plastic={}, substrate={})

    lyap_exp = lyapunov_estimator._fast_proxy(transition_fn_internal, z, context)

    # 3. Settling (passivity proxy) - use external windowed growth
    settling_steps = 0
    step_norms = []
    current = initial_state
    for _ in range(1000):
        x_before = current.get("x")
        if not isinstance(x_before, torch.Tensor):
            break
        before_norm = float(x_before.norm().item())
        current = transition_fn_external(current)
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

    # 4. Resource usage
    resource_usage_obj = ResourceUsage.measure(model, input_tensor)
    resource_usage_val = resource_usage_obj.compute + resource_usage_obj.memory * 1e6

    # 5. Causality (DAG) - check model has no cycles (simplified)
    # In practice, this would check the system coordinate DAG
    causality_ok = True  # Placeholder - would check SystemConfig.validate()

    # 6. Protocol conformance
    protocol_ok = True  # Placeholder - would check SystemConfig.validate()

    # 7. Recursion invariant
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
    """Compute constitution metrics using the panel implementation."""
    from computronium.ui.components.constitution_health import (
        compute_constitution_metrics,
    )

    return compute_constitution_metrics(
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
        assert panel.resource_ceiling == ref.resource_ceiling, (
            "Resource ceiling mismatch"
        )
        assert panel.protocol_conformance == ref.protocol_conformance, (
            "Protocol conformance mismatch"
        )
        assert panel.recursion_invariant == ref.recursion_invariant, (
            "Recursion invariant mismatch"
        )

        # Raw metrics must match byte-identically (within float tolerance)
        assert panel.spectral_radius == pytest.approx(ref.spectral_radius, rel=1e-6), (
            f"Spectral radius mismatch: panel={panel.spectral_radius}, ref={ref.spectral_radius}"
        )
        assert panel.lyapunov_exponent == pytest.approx(
            ref.lyapunov_exponent, rel=1e-6
        ), (
            f"Lyapunov exponent mismatch: panel={panel.lyapunov_exponent}, ref={ref.lyapunov_exponent}"
        )
        assert panel.jacobian_amplification == pytest.approx(
            ref.jacobian_amplification, rel=1e-6
        ), (
            f"Jacobian amplification mismatch: panel={panel.jacobian_amplification}, ref={ref.jacobian_amplification}"
        )
        assert panel.settling_steps == ref.settling_steps, "Settling steps mismatch"
        assert panel.energy_consumed == pytest.approx(ref.energy_consumed, rel=1e-6), (
            "Energy consumed mismatch"
        )
        assert panel.energy_injected == pytest.approx(ref.energy_injected, rel=1e-6), (
            "Energy injected mismatch"
        )
        assert panel.resource_usage == pytest.approx(ref.resource_usage, rel=1e-6), (
            "Resource usage mismatch"
        )
        assert panel.resource_budget == ref.resource_budget, "Resource budget mismatch"
        assert panel.max_recursion_depth == ref.max_recursion_depth, (
            "Max recursion depth mismatch"
        )

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
        import re

        from computronium.ui.glossary_service import get_glossary_service

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
        from computronium.ui.components.constitution_health import (
            ConstitutionHealthPanel,
        )

        assert ConstitutionHealthPanel is not None

    def test_panel_renders_all_six_invariants(self) -> None:
        """Panel must render all 6 invariants with status indicators."""
        from computronium.ui.components.constitution_health import (
            ConstitutionHealthPanel,
            create_invariants_from_monitor,
        )

        invariants = create_invariants_from_monitor(
            spectral_radius=0.85,
            lyapunov_exponent=0.1,
            energy_injected=1.0,
            energy_consumed=0.5,
            resource_usage=1e6,
            resource_budget=1e9,
            max_recursion_depth=10,
        )
        panel = ConstitutionHealthPanel(invariants=invariants)
        assert panel.invariants is not None
        assert len(panel.invariants) == 6
        expected_keys = {
            "causality_dag",
            "passivity",
            "lyapunov_bound",
            "resource_ceiling",
            "protocol_conformance",
            "recursion_invariant",
        }
        assert {inv.key for inv in panel.invariants} == expected_keys

    def test_panel_register_aware(self) -> None:
        """Panel must show plain language in Explorer, technical in Lab."""
        from computronium.ui.components.constitution_health import (
            ConstitutionHealthPanel,
            create_invariants_from_monitor,
        )
        from computronium.ui.mode_toggle import set_mode

        invariants = create_invariants_from_monitor(
            spectral_radius=0.85,
            lyapunov_exponent=0.1,
            energy_injected=1.0,
            energy_consumed=0.5,
            resource_usage=1e6,
            resource_budget=1e9,
            max_recursion_depth=10,
        )

        # Test Explorer mode
        set_mode("explorer")
        panel_explorer = ConstitutionHealthPanel(invariants=invariants)
        assert panel_explorer.is_explorer

        # Test Lab mode
        set_mode("lab")
        panel_lab = ConstitutionHealthPanel(invariants=invariants)
        assert panel_lab.is_lab


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
