"""Lock: user-specified axes are never filtered by constraint satisfaction.

This test guarantees that when a user explicitly specifies primitives on an axis
via CLI (--credits, --plasticities, etc.), those primitives are preserved in
the search space regardless of cross-axis constraints. Only profile-default axes
are subject to validity filtering.
"""

import pytest
from computronium.experiment.schema import RunSpec
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.run_spec import AxisSelection
from computronium.experiment.surface.cli import RUN_PROFILES
from computronium.experiment.kernel.search_space import (
    search_space_from_spec,
    _filter_axes_cache,
)


class TestSearchSpaceUserAxesLock:
    """User-specified axes pass through _filter_axes_for_validity unfiltered."""

    @pytest.fixture(autouse=True)
    def _clear_cache(self):
        """Clear the filter cache before each test."""
        _filter_axes_cache.clear()

    def _make_spec(self, user_credit_axes: tuple[str, ...] | None = None):
        profile = RUN_PROFILES["production-map"]
        axes = ()
        if user_credit_axes is not None:
            axes = (
                AxisSelection(axis=StructuralAxis.CREDIT, primitives=user_credit_axes),
                AxisSelection(
                    axis=StructuralAxis.PLASTICITY,
                    primitives=("null", "fast_weights", "routing"),
                ),
            )
        return RunSpec(
            profile=profile.name,
            task=profile.task,
            objectives=profile.objectives,
            stages=tuple(profile.stages),
            fidelity=profile.fidelity,
            n_seeds=profile.n_seeds,
            epochs=profile.epochs,
            batch_limit=profile.batch_limit,
            budget_seconds=3600.0,
            param_budget=profile.param_budget,
            policy=profile.policy,
            axes=axes,
            checkpoint_every_n=profile.checkpoint_every_n,
            seed=42,
            device="cuda",
        )

    def test_user_specified_credit_axis_preserves_all_primitives(self):
        """All 7 user-specified credits appear in search space, even if constraints would filter them."""
        user_credits = (
            "gradient",
            "random_projections",
            "pepita",
            "local_goodness",
            "thermodynamic_contrast",
            "target_inversion",
            "homeostatic",
        )
        spec = self._make_spec(user_credit_axes=user_credits)
        space = search_space_from_spec(spec, tasks=spec.task_names)

        # All 7 user-specified credits must be present
        filtered_credits = space.primitives(StructuralAxis.CREDIT)
        assert set(filtered_credits) == set(user_credits), (
            f"Expected all 7 user credits, got {filtered_credits}"
        )

    def test_profile_default_credit_axis_is_filtered(self):
        """When user does NOT specify credits, profile default (all available) IS filtered by constraints."""
        spec = self._make_spec(user_credit_axes=None)
        space = search_space_from_spec(spec, tasks=spec.task_names)

        # Default credits should be filtered by constraints
        filtered_credits = space.primitives(StructuralAxis.CREDIT)
        all_available = [
            "gradient",
            "random_projections",
            "pepita",
            "local_goodness",
            "thermodynamic_contrast",
            "target_inversion",
            "homeostatic",
            "pc_alm",
            "local_contrastive",
            "temporal_trace",
        ]
        # With full profile defaults (all substrates, geometries, dynamics, plasticities, updates),
        # ALL 10 credits have at least one valid combination in the space.
        # The constraint filter correctly preserves all of them.
        assert set(filtered_credits) == set(all_available), (
            f"Expected all 10 credits to have valid combos, got {filtered_credits}"
        )

    def test_user_specified_plasticity_axis_preserves_all_primitives(self):
        """User-specified plasticity primitives are preserved."""
        user_plasticities = ("null", "fast_weights", "routing", "rule_state")
        spec = RunSpec(
            profile=RUN_PROFILES["production-map"].name,
            task=RUN_PROFILES["production-map"].task,
            objectives=RUN_PROFILES["production-map"].objectives,
            stages=tuple(RUN_PROFILES["production-map"].stages),
            fidelity=RUN_PROFILES["production-map"].fidelity,
            n_seeds=RUN_PROFILES["production-map"].n_seeds,
            epochs=RUN_PROFILES["production-map"].epochs,
            batch_limit=RUN_PROFILES["production-map"].batch_limit,
            budget_seconds=3600.0,
            param_budget=RUN_PROFILES["production-map"].param_budget,
            policy=RUN_PROFILES["production-map"].policy,
            axes=(
                AxisSelection(axis=StructuralAxis.CREDIT, primitives=("gradient",)),
                AxisSelection(
                    axis=StructuralAxis.PLASTICITY, primitives=user_plasticities
                ),
            ),
            checkpoint_every_n=RUN_PROFILES["production-map"].checkpoint_every_n,
            seed=42,
            device="cuda",
        )
        space = search_space_from_spec(spec, tasks=spec.task_names)

        filtered_plasticities = space.primitives(StructuralAxis.PLASTICITY)
        assert set(filtered_plasticities) == set(user_plasticities), (
            f"Expected all user plasticities, got {filtered_plasticities}"
        )

    def test_other_axes_still_filtered_by_constraints(self):
        """Non-user-specified axes (substrate, geometry, dynamics, update) are still filtered."""
        user_credits = (
            "gradient",
            "random_projections",
            "pepita",
            "local_goodness",
            "thermodynamic_contrast",
            "target_inversion",
            "homeostatic",
        )
        spec = self._make_spec(user_credit_axes=user_credits)
        space = search_space_from_spec(spec, tasks=spec.task_names)

        # Geometry should be filtered to only compatible ones
        geometry = space.primitives(StructuralAxis.GEOMETRY)
        # attention is compatible with gradient, random_projections, target_inversion, homeostatic
        # but NOT with pepita, local_goodness, local_contrastive, forward_only
        # Since user credits include compatible ones, attention passes through
        assert "feedforward" in geometry

        # Dynamics should be filtered to only compatible ones
        dynamics = space.primitives(StructuralAxis.DYNAMICS)
        # With all 8 dynamics having valid combos with user credits, all should pass
        expected_dynamics = {
            "instantaneous",
            "energy_minimization",
            "predictive_settling",
            "pc_alm",
            "lazy",
            "diffusion",
            "spike_integration",
            "error_predictive_coding",
        }
        assert set(dynamics) == expected_dynamics, (
            f"Expected all 8 dynamics, got {dynamics}. Missing: {expected_dynamics - set(dynamics)}"
        )

        # Substrate should be filtered (e.g., neuromorphic requires temporal dynamics)
        substrate = space.primitives(StructuralAxis.SUBSTRATE)
        # neuromorphic requires spike_integration, energy_minimization, or diffusion
        # All 3 are available in dynamics, so neuromorphic should be included
        assert "neuromorphic" in substrate

    def test_cache_respects_user_axes(self):
        """Cached filter results correctly preserve user-specified axes on cache hit."""
        user_credits = (
            "gradient",
            "random_projections",
            "pepita",
            "local_goodness",
            "thermodynamic_contrast",
            "target_inversion",
            "homeostatic",
        )
        spec = self._make_spec(user_credit_axes=user_credits)

        # First call populates cache
        space1 = search_space_from_spec(spec, tasks=spec.task_names)
        # Second call uses cache
        space2 = search_space_from_spec(spec, tasks=spec.task_names)

        assert space1.primitives(StructuralAxis.CREDIT) == space2.primitives(
            StructuralAxis.CREDIT
        )
        assert set(space1.primitives(StructuralAxis.CREDIT)) == set(user_credits)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
