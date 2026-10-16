"""Property tests for discovery/confirmation seed separation (C1).

Validates that:
1. Discovery seeds and confirmation seeds are disjoint
2. Confirmation seeds are never reused from discovery
3. Power analysis thresholds are used for L2 promotion
4. Verdicts report power_achieved
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from computronium.core.statistics import power_for_two_sample, required_sample_size
from computronium.experiment.execution.statistical_promotion import GateThresholds
from computronium.experiment.registry.seed import SeedContext

if TYPE_CHECKING:
    from computronium.experiment.schema.record import Record
    from computronium.experiment.schema.run_spec import RunSpec


class TestSeedSeparation:
    """Tests for discovery/confirmation seed separation."""

    def test_discovery_and_confirmation_seeds_are_disjoint(self):
        """Discovery and confirmation seeds must never overlap."""
        ctx = SeedContext(master_seed=42)

        # Get discovery seeds for cycle 0
        discovery = ctx.discovery_seeds(cycle_index=0, cell_count=10)

        # Get confirmation seeds for cycle 0
        confirmation = ctx.confirmation_seeds(cycle_index=0, cell_count=10, n_confirm=3)

        # Flatten confirmation seeds
        all_confirmation = [seed for cell_seeds in confirmation for seed in cell_seeds]

        # No overlap allowed
        discovery_set = set(discovery)
        confirmation_set = set(all_confirmation)

        assert discovery_set.isdisjoint(confirmation_set), (
            f"Discovery and confirmation seeds overlap: {discovery_set & confirmation_set}"
        )

    def test_different_cycles_have_disjoint_seeds(self):
        """Seeds for different cycles must be disjoint."""
        ctx = SeedContext(master_seed=123)

        cycle0_discovery = ctx.discovery_seeds(cycle_index=0, cell_count=5)
        cycle1_discovery = ctx.discovery_seeds(cycle_index=1, cell_count=5)

        cycle0_confirmation = ctx.confirmation_seeds(
            cycle_index=0, cell_count=5, n_confirm=2
        )
        cycle1_confirmation = ctx.confirmation_seeds(
            cycle_index=1, cell_count=5, n_confirm=2
        )

        all_cycle0 = set(cycle0_discovery) | {
            s for cell in cycle0_confirmation for s in cell
        }
        all_cycle1 = set(cycle1_discovery) | {
            s for cell in cycle1_confirmation for s in cell
        }

        assert all_cycle0.isdisjoint(all_cycle1), "Seeds from different cycles overlap"

    def test_seed_plan_contains_both_discovery_and_confirmation(self):
        """Seed plan should contain both discovery and confirmation seeds."""
        from computronium.experiment.registry.seed import SeedContextManager

        manager = SeedContextManager(master_seed=999)

        plan = manager.plan_cell_seeds(
            cell_key="test_cell",
            cell_index=0,
            n_discovery=2,
            n_confirmation=3,
        )

        assert len(plan.discovery_seeds) == 2
        assert len(plan.confirmation_seeds) == 3
        assert len(plan.confirmation_seeds[0]) == 1  # Each confirmation is single seed

        # All seeds should be unique
        all_seeds = plan.all_seeds
        assert len(all_seeds) == len(set(all_seeds)), "Seed plan contains duplicates"

        # Discovery and confirmation should be disjoint
        assert set(plan.discovery_seeds).isdisjoint({
            s for rep in plan.confirmation_seeds for s in rep
        })


class TestPowerAnalysisThresholds:
    """Tests for power analysis based thresholds (C0/C1)."""

    def test_required_sample_size_is_reasonable(self):
        """Required sample size should be reasonable for typical parameters."""
        # Medium effect size (d=0.5), 80% power, alpha=0.05
        n = required_sample_size(effect_size=0.5, power=0.8, alpha=0.05)
        # Cohen's formula: n ≈ 63 per group for d=0.5, power=0.8
        assert 50 <= n <= 100, f"Unexpected sample size: {n}"

    def test_required_sample_size_increases_with_power(self):
        """Higher power should require more samples."""
        n_80 = required_sample_size(effect_size=0.5, power=0.8, alpha=0.05)
        n_90 = required_sample_size(effect_size=0.5, power=0.9, alpha=0.05)
        n_95 = required_sample_size(effect_size=0.5, power=0.95, alpha=0.05)

        assert n_80 < n_90 < n_95

    def test_required_sample_size_decreases_with_effect_size(self):
        """Larger effect size should require fewer samples."""
        n_small = required_sample_size(effect_size=0.2, power=0.8, alpha=0.05)
        n_medium = required_sample_size(effect_size=0.5, power=0.8, alpha=0.05)
        n_large = required_sample_size(effect_size=0.8, power=0.8, alpha=0.05)

        assert n_small > n_medium > n_large

    def test_power_for_two_sample_monotonic(self):
        """Power should increase with sample size and effect size."""
        # More samples -> more power
        p1 = power_for_two_sample(d=0.5, n_per_group=30)
        p2 = power_for_two_sample(d=0.5, n_per_group=60)
        p3 = power_for_two_sample(d=0.5, n_per_group=100)
        assert p1 < p2 < p3

        # Larger effect -> more power
        p_small = power_for_two_sample(d=0.2, n_per_group=50)
        p_large = power_for_two_sample(d=0.8, n_per_group=50)
        assert p_small < p_large


class TestGateThresholdsPowerAnalysis:
    """Tests for GateThresholds using power analysis."""

    def test_required_seeds_per_group_property(self):
        """GateThresholds should expose required_seeds_per_group from power analysis."""
        thresholds = GateThresholds(
            power_target=0.8,
            alpha=0.05,
            effect_size_target=0.5,
        )

        required = thresholds.required_seeds_per_group
        # Should match required_sample_size(0.5, 0.8, 0.05) ≈ 63
        assert 50 <= required <= 100

    def test_power_achieved_in_gate_result(self):
        """GateResult should include power_achieved in details."""
        from computronium.experiment.execution.statistical_promotion import (
            check_superiority_gate,
        )

        # Need enough seeds to meet power analysis requirement
        # For d=0.8, power=0.8, alpha=0.05: n≈25 per group
        cell_values = [0.85, 0.87, 0.86, 0.88, 0.84] * 5  # 25 seeds
        baseline_values = [0.75, 0.76, 0.74, 0.77, 0.75] * 5  # 25 seeds

        thresholds = GateThresholds(
            min_seeds_for_stats=5,
            power_target=0.8,
            alpha=0.05,
            effect_size_target=0.8,  # Larger effect size -> fewer required seeds
        )

        result = check_superiority_gate(cell_values, baseline_values, thresholds)

        # Should pass (clear superiority)
        assert result.passed is True
        # Should include power_achieved
        assert "power_achieved" in result.details
        assert 0 <= result.details["power_achieved"] <= 1
        # Power should be high for this clear effect
        assert result.details["power_achieved"] > 0.5

    def test_insufficient_seeds_reports_required(self):
        """Gate should fail with required seeds count when underpowered."""
        from computronium.experiment.execution.statistical_promotion import (
            check_superiority_gate,
        )

        # Only 10 seeds - below power analysis requirement (~63)
        cell_values = [0.85] * 10
        baseline_values = [0.75] * 10

        thresholds = GateThresholds(
            power_target=0.8,
            alpha=0.05,
            effect_size_target=0.5,
        )

        result = check_superiority_gate(cell_values, baseline_values, thresholds)

        # Should fail due to insufficient seeds
        assert result.passed is False
        assert "required_seeds" in result.details
        assert result.details["required_seeds"] > 10


class TestSeedContextManager:
    """Tests for SeedContextManager integration."""

    def test_manager_plans_discovery_and_confirmation(self):
        """SeedContextManager should plan both discovery and confirmation seeds."""
        from computronium.experiment.registry.seed import SeedContextManager

        manager = SeedContextManager(master_seed=42)

        plan = manager.plan_cell_seeds(
            cell_key="test",
            cell_index=0,
            n_discovery=1,
            n_confirmation=5,
        )

        assert len(plan.discovery_seeds) == 1
        assert len(plan.confirmation_seeds) == 5

        # All seeds unique
        all_seeds = plan.all_seeds
        assert len(all_seeds) == 6
        assert len(set(all_seeds)) == 6

    def test_context_manager_cycle_and_cell_seeds(self):
        """SeedContextManager should generate proper cycle and cell seeds."""
        from computronium.experiment.registry.seed import SeedContextManager

        manager = SeedContextManager(master_seed=42)

        # Get cycle seed
        cycle_seed = manager.get_cycle_seed(0)
        assert isinstance(cycle_seed, int)

        # Plan cell seeds
        plan = manager.plan_cell_seeds(
            cell_key="test_cell",
            cell_index=0,
            n_discovery=2,
            n_confirmation=3,
        )

        assert len(plan.discovery_seeds) == 2
        assert len(plan.confirmation_seeds) == 3


class TestL2ConfirmationWiring:
    """The L2 confirmation path must actually invoke a supplied evaluator (C1).

    Falsifiable: removing the ``confirmation_evaluator`` call (or reverting to
    the broken ``asyncio.run`` on a sync evaluator) turns this red.
    """

    def test_l2_confirmation_invokes_evaluator_with_fresh_seeds(self):
        from types import SimpleNamespace
        from typing import Any, cast

        from computronium.experiment.execution.statistical_promotion import (
            StatisticalGateRunner,
            _evaluate_l2_confirmation,
        )

        spec = cast("RunSpec", SimpleNamespace(seed=1234, n_seeds=3))
        group = cast(
            "list[Record]", [SimpleNamespace(schedule=SimpleNamespace(seed=0))]
        )
        captured: dict[str, Any] = {}

        def evaluator(cell_records, seeds):
            captured["seeds"] = list(seeds)
            return cast("list[Record]", [SimpleNamespace(payload={}) for _ in seeds])

        class _Runner:
            def evaluate_cell(self, records, baseline, *, use_discovery_seeds=True):
                captured["use_discovery_seeds"] = use_discovery_seeds
                return SimpleNamespace(all_passed=True, to_dict=dict)

        passed, status, result = _evaluate_l2_confirmation(
            cast("StatisticalGateRunner", _Runner()),
            group,
            None,
            spec,
            cycle=5,
            confirmation_evaluator=evaluator,
            thresholds=GateThresholds(),
            tolerance=0.05,
        )

        assert passed is True
        assert status == "pass"
        assert result is not None
        assert captured["use_discovery_seeds"] is False
        assert len(captured["seeds"]) == spec.n_seeds
        # Fresh seeds: disjoint from the discovery seeds the group measured on.
        assert set(captured["seeds"]).isdisjoint({r.schedule.seed for r in group})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
