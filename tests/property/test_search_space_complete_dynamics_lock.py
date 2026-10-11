"""Lock: search space should include all dynamics that have valid combinations.

The approximate filter (for >100k combos) uses a default combination (first primitive
per axis) to test each primitive. If the default combination itself is invalid,
many valid primitives get incorrectly filtered out.

This test documents the current behavior and will pass when the filter is fixed.
"""

import pytest
from computronium.experiment.schema import RunSpec
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.run_spec import AxisSelection
from computronium.experiment.surface.cli import RUN_PROFILES
from computronium.experiment.execution.search_space import (
    search_space_from_spec,
    _filter_axes_cache,
)


class TestSearchSpaceCompleteDynamicsLock:
    """Search space should include all dynamics with at least one valid combination."""

    @pytest.fixture(autouse=True)
    def _clear_cache(self):
        _filter_axes_cache.clear()

    def _make_spec(self):
        profile = RUN_PROFILES["production-map"]
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
            axes=(
                AxisSelection(
                    axis=StructuralAxis.CREDIT,
                    primitives=(
                        "gradient",
                        "random_projections",
                        "pepita",
                        "local_goodness",
                        "thermodynamic_contrast",
                        "target_inversion",
                        "homeostatic",
                    ),
                ),
                AxisSelection(
                    axis=StructuralAxis.PLASTICITY,
                    primitives=("null", "fast_weights", "routing"),
                ),
            ),
            checkpoint_every_n=profile.checkpoint_every_n,
            seed=42,
            device="cuda",
        )

    def test_all_dynamics_with_valid_combinations_are_in_search_space(self):
        """All 8 dynamics have valid combinations with user-specified credits/geometries."""
        spec = self._make_spec()
        space = search_space_from_spec(spec, tasks=spec.task_names)

        dynamics = space.primitives(StructuralAxis.DYNAMICS)

        # All 8 dynamics are valid with feedforward geometry and user credits
        expected_dynamics = (
            "instantaneous",
            "energy_minimization",
            "predictive_settling",
            "pc_alm",
            "lazy",
            "diffusion",
            "spike_integration",
            "error_predictive_coding",
        )

        # Currently only instantaneous is included due to approximate filter bug
        # This test will fail until the filter is fixed
        assert set(dynamics) == set(expected_dynamics), (
            f"Expected all 8 dynamics, got {dynamics}. "
            f"Missing: {set(expected_dynamics) - set(dynamics)}"
        )

    def test_all_dynamics_with_profile_default_credits(self):
        """Even with profile defaults, dynamics should be filtered correctly (not just instantaneous)."""
        profile = RUN_PROFILES["production-map"]
        spec = RunSpec(
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
            axes=(),  # Profile defaults
            checkpoint_every_n=profile.checkpoint_every_n,
            seed=42,
            device="cuda",
        )
        space = search_space_from_spec(spec, tasks=spec.task_names)

        dynamics = space.primitives(StructuralAxis.DYNAMICS)

        # Should include dynamics compatible with filtered credits
        # At minimum: instantaneous, energy_minimization, predictive_settling, pc_alm
        expected_minimum = {"instantaneous", "energy_minimization", "predictive_settling", "pc_alm"}
        assert expected_minimum.issubset(set(dynamics)), (
            f"Missing minimum dynamics: {expected_minimum - set(dynamics)}, got {dynamics}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
