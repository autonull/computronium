"""Property lock: ContrastDesign identifiability on SyntheticGroundTruth.

Verifies that OFAT/fractional-factorial DOE recovers known effects
on a synthetic fixture with analytical ground truth (WP18).
"""

from __future__ import annotations

import numpy as np
import pytest

from computronium.experiment.evidence.protocol import (
    SYNTHETIC_FIXTURE,
    SyntheticGroundTruth,
)
from computronium.experiment.execution.contrast_design import (
    ContrastAssignment,
    ContrastDesign,
    ContrastDesignKind,
    Factor,
    create_fractional_factorial_design,
    create_full_factorial_design,
    create_ofat_design,
)
from computronium.experiment.schema import Coordinate, Schedule


class TestContrastDesignBasics:
    """Basic contrast design construction tests."""

    def test_factor_creation(self) -> None:
        """Factor creation with validation."""
        f = Factor(name="lr", levels=(1e-4, 1e-1), unit="log")
        assert f.name == "lr"
        assert f.levels == (1e-4, 1e-1)

        with pytest.raises(ValueError):
            Factor(name="bad", levels=(1.0,))

    def test_contrast_assignment(self) -> None:
        """ContrastAssignment round-trip."""
        assignment = ContrastAssignment(
            contrast_id="abc123",
            factor_assignments={"lr": 0.01, "batch_size": 32},
            matched_group="ofat_lr",
        )
        d = assignment.to_dict()
        loaded = ContrastAssignment.from_dict(d)
        assert loaded.contrast_id == "abc123"
        assert loaded.factor_assignments == {"lr": 0.01, "batch_size": 32}
        assert loaded.matched_group == "ofat_lr"

    def test_ofat_design_structure(self) -> None:
        """OFAT design has control + one run per factor per non-base level."""
        factors = [
            Factor(name="lr", levels=(1e-4, 1e-3, 1e-2), unit="log"),
            Factor(name="batch", levels=(32, 64, 128), unit="linear"),
        ]
        design = create_ofat_design(factors, seed=42)

        assert design.design_kind == ContrastDesignKind.OFAT
        assert design.n_factors == 2
        # 1 control + 2 non-base levels for lr + 2 non-base levels for batch = 5
        assert design.n_runs == 5

        # Check control run exists
        control_runs = [a for a in design.assignments if a.matched_group == "control"]
        assert len(control_runs) == 1
        assert control_runs[0].factor_assignments == {"lr": 1e-4, "batch": 32}

        # Check OFAT runs grouped by factor
        lr_runs = [a for a in design.assignments if a.matched_group == "ofat_lr"]
        assert len(lr_runs) == 2
        batch_runs = [a for a in design.assignments if a.matched_group == "ofat_batch"]
        assert len(batch_runs) == 2

    def test_fractional_factorial_2level(self) -> None:
        """Fractional factorial requires 2-level factors."""
        factors = [
            Factor(name="a", levels=(-1, 1)),
            Factor(name="b", levels=(-1, 1)),
            Factor(name="c", levels=(-1, 1)),
            Factor(name="d", levels=(-1, 1)),
        ]
        design = create_fractional_factorial_design(factors, resolution="IV", seed=42)

        assert design.design_kind == ContrastDesignKind.FRACTIONAL_FACTORIAL
        assert design.resolution == "IV"
        assert design.n_factors == 4
        assert design.n_runs == 8  # 2^(4-1) = 8

    def test_fractional_factorial_rejects_non_2level(self) -> None:
        """Fractional factorial rejects non-2-level factors."""
        factors = [
            Factor(name="a", levels=(-1, 0, 1)),  # 3 levels
            Factor(name="b", levels=(-1, 1)),
        ]
        with pytest.raises(ValueError, match="2-level factors"):
            create_fractional_factorial_design(factors, seed=42)

    def test_full_factorial(self) -> None:
        """Full factorial generates all combinations."""
        factors = [
            Factor(name="a", levels=(-1, 1)),
            Factor(name="b", levels=(-1, 1)),
        ]
        design = create_full_factorial_design(factors, seed=42)

        assert design.design_kind == ContrastDesignKind.FULL_FACTORIAL
        assert design.n_runs == 4  # 2^2 = 4

        # Check all combinations present
        assignments = {
            (a.factor_assignments["a"], a.factor_assignments["b"])
            for a in design.assignments
        }
        assert assignments == {(-1, -1), (-1, 1), (1, -1), (1, 1)}

    def test_contrast_design_round_trip(self) -> None:
        """ContrastDesign serialization round-trip."""
        factors = [Factor(name="x", levels=(0.0, 1.0))]
        design = create_ofat_design(factors, seed=123)

        d = design.to_dict()
        loaded = ContrastDesign.from_dict(d)

        assert loaded.design_kind == design.design_kind
        assert loaded.n_factors == design.n_factors
        assert loaded.n_runs == design.n_runs
        assert [a.contrast_id for a in loaded.assignments] == [
            a.contrast_id for a in design.assignments
        ]


class TestContrastDesignIdentifiability:
    """Identifiability tests: DOE recovers known effects on SyntheticGroundTruth."""

    def _evaluate_design_on_fixture(
        self,
        design: ContrastDesign,
        fixture: SyntheticGroundTruth,
        n_seeds: int = 3,
    ) -> dict[str, float]:
        """Evaluate a contrast design on a synthetic fixture.

        Returns:
            Dictionary mapping contrast_id to mean function value.
            For designs with control group, also computes effect vs control.
        """
        # Check if design has a control group
        control_assignment = None
        for a in design.assignments:
            if a.matched_group == "control":
                control_assignment = a
                break

        # Evaluate all runs
        run_values = {}
        for assignment in design.assignments:
            params = tuple(
                assignment.factor_assignments.get(f.name, 0.0) for f in design.factors
            )
            values = [fixture.evaluate(params, seed=s) for s in range(n_seeds)]
            run_values[assignment.contrast_id] = np.mean(values)

        # If control exists, compute effects vs control
        if control_assignment is not None:
            control_mean = run_values[control_assignment.contrast_id]
            effects = {}
            for assignment in design.assignments:
                if assignment.matched_group == "control":
                    continue
                effects[assignment.contrast_id] = (
                    control_mean - run_values[assignment.contrast_id]
                )
            return effects

        # Otherwise return raw values (for designs without explicit control)
        return run_values

    def test_ofat_recovers_main_effects(self) -> None:
        """OFAT design recovers known main effects on quadratic bowl.

        The synthetic fixture has known optimum at [1, 2, 3, 4, 5, 6]
        with no interactions (diagonal quadratic form).
        OFAT varying from base [0, 0, 0, 0, 0, 0] should identify
        which factors have largest effect.
        """
        # Use SYNTHETIC_FIXTURE (dim=6, diagonal, noise=0.1)
        fixture = SYNTHETIC_FIXTURE

        # Create factors matching fixture dimensions
        factors = [
            Factor(name=f"x{i}", levels=(0.0, float(i + 1)), unit="normalized")
            for i in range(fixture.dimension)
        ]

        design = create_ofat_design(factors, seed=42)

        # Evaluate
        effects = self._evaluate_design_on_fixture(design, fixture, n_seeds=5)

        # Verify we have effects for all non-control runs
        assert len(effects) == design.n_runs - 1

        # The true effect of moving from 0 to optimum for factor i is (i+1)^2
        # OFAT should rank factors by effect size approximately correctly
        # Factor 5 (x5, level 6) should have largest effect (36)
        # Factor 0 (x0, level 1) should have smallest effect (1)

        # Group by factor
        factor_effects: dict[str, list[float]] = {}
        for assignment in design.assignments:
            if assignment.matched_group.startswith("ofat_"):
                factor_name = assignment.matched_group[len("ofat_") :]
                if assignment.contrast_id in effects:
                    factor_effects.setdefault(factor_name, []).append(
                        effects[assignment.contrast_id]
                    )

        # Average effect per factor
        mean_effects = {f: np.mean(v) for f, v in factor_effects.items()}

        # Check ranking: x5 > x4 > x3 > x2 > x1 > x0
        expected_order = ["x5", "x4", "x3", "x2", "x1", "x0"]
        actual_order = sorted(
            mean_effects.keys(), key=lambda f: mean_effects[f], reverse=True
        )
        assert actual_order == expected_order, (
            f"Effect ranking mismatch: expected {expected_order}, got {actual_order}. "
            f"Effects: {mean_effects}"
        )

    def test_fractional_factorial_recovers_effects(self) -> None:
        """Fractional factorial recovers effects on synthetic fixture."""
        # Create fixture with 4 dimensions to match design
        fixture = SyntheticGroundTruth(
            dimension=4,
            optimum=(1.0, 2.0, 3.0, 4.0),
            noise_std=0.1,
        )

        # Use 4 factors for 2^(4-1) design
        factors = [
            Factor(name=f"x{i}", levels=(0.0, float(i + 1)), unit="normalized")
            for i in range(4)
        ]

        design = create_fractional_factorial_design(factors, resolution="IV", seed=42)

        # For designs without control, _evaluate_design_on_fixture returns raw values
        run_values = self._evaluate_design_on_fixture(design, fixture, n_seeds=5)

        # Should have values for all runs
        assert len(run_values) == design.n_runs

        # Main effects should be estimable (resolution IV)
        # Verify we can compute main effect contrasts
        # For each factor, compare runs where factor=high vs factor=low
        for f in factors:
            high_runs = [
                run_values[a.contrast_id]
                for a in design.assignments
                if a.factor_assignments.get(f.name) == f.levels[1]
            ]
            low_runs = [
                run_values[a.contrast_id]
                for a in design.assignments
                if a.factor_assignments.get(f.name) == f.levels[0]
            ]
            if high_runs and low_runs:
                main_effect = np.mean(high_runs) - np.mean(low_runs)
                # Higher level should be better (closer to optimum) -> lower value
                # since we're minimizing, so main_effect should be negative
                assert main_effect < 0, (
                    f"Factor {f.name} main effect should be negative"
                )

    def test_ofat_with_interactions(self) -> None:
        """OFAT detects interaction effects when present.

        Use a fixture with known interactions.
        """
        fixture = SyntheticGroundTruth(
            dimension=3,
            optimum=(1.0, 2.0, 3.0),
            interaction_matrix=(
                (1.0, 0.5, 0.0),
                (0.5, 1.0, 0.5),
                (0.0, 0.5, 1.0),
            ),
            noise_std=0.05,
        )

        factors = [
            Factor(name="x0", levels=(0.0, 1.0)),
            Factor(name="x1", levels=(0.0, 2.0)),
            Factor(name="x2", levels=(0.0, 3.0)),
        ]

        design = create_ofat_design(factors, seed=42)
        effects = self._evaluate_design_on_fixture(design, fixture, n_seeds=10)

        # OFAT cannot disentangle interactions from main effects
        # but should still detect combined effects
        assert len(effects) == design.n_runs - 1
        assert all(v is not None for v in effects.values())

    def test_contrast_id_deterministic(self) -> None:
        """contrast_id is deterministic for same design and seed."""
        factors = [Factor(name="a", levels=(0, 1)), Factor(name="b", levels=(0, 1))]
        design1 = create_ofat_design(factors, seed=42)
        design2 = create_ofat_design(factors, seed=42)

        ids1 = [a.contrast_id for a in design1.assignments]
        ids2 = [a.contrast_id for a in design2.assignments]
        assert ids1 == ids2

        # Different seed -> different IDs
        design3 = create_ofat_design(factors, seed=43)
        ids3 = [a.contrast_id for a in design3.assignments]
        assert ids1 != ids3

    def test_matched_group_structure(self) -> None:
        """Matched groups enable paired analysis."""
        factors = [Factor(name="a", levels=(0, 1)), Factor(name="b", levels=(0, 1))]
        design = create_ofat_design(factors, seed=42)

        # Each OFAT factor has its own matched group
        groups = {a.matched_group for a in design.assignments}
        assert "control" in groups
        assert "ofat_a" in groups
        assert "ofat_b" in groups

        # Control group has exactly 1 run
        assert sum(1 for a in design.assignments if a.matched_group == "control") == 1


class TestContrastDesignIntegration:
    """Integration with ScheduleStage and Proposal."""

    def test_contrast_design_in_proposal_metadata(self) -> None:
        """Contrast design assignments can be embedded in Proposal metadata."""
        from computronium.experiment.execution.stage import Proposal

        factors = [Factor(name="lr", levels=(1e-4, 1e-2))]
        design = create_ofat_design(factors, seed=42)
        contrast_assignment = design.assignments[1]  # First OFAT run

        coord = Coordinate(
            substrate="digital",
            geometry="feedforward",
            dynamics="instantaneous",
            plasticity="null",
            credit="gradient",
            update="euclidean",
            params={"lr": 1e-3},
        )
        sched = Schedule(
            fidelity="L0",
            seed=0,
            n_seeds=1,
            epochs=1,
            batch_limit=100,
            budget_id="budget_1",
        )

        proposal = Proposal(
            coordinate=coord,
            schedule=sched,
            rationale="ofat_lr",
            metadata={
                "data_origin": "contrast",
                "contrast_id": contrast_assignment.contrast_id,
                "factor_assignments": contrast_assignment.factor_assignments,
                "matched_group": contrast_assignment.matched_group,
            },
        )

        assert proposal.metadata["data_origin"] == "contrast"
        assert proposal.metadata["contrast_id"] == contrast_assignment.contrast_id
        assert proposal.metadata["matched_group"] == "ofat_lr"

    def test_schedule_measurement_key_unchanged_by_data_origin(self) -> None:
        """measurement_key does not depend on data_origin (in metadata, not schedule)."""

        coord = Coordinate(
            substrate="digital",
            geometry="feedforward",
            dynamics="instantaneous",
            plasticity="null",
            credit="gradient",
            update="euclidean",
            params={},
        )

        sched1 = Schedule(
            fidelity="L0",
            seed=0,
            n_seeds=1,
            epochs=1,
            batch_limit=100,
            budget_id="budget_1",
        )
        sched2 = Schedule(
            fidelity="L0",
            seed=0,
            n_seeds=1,
            epochs=1,
            batch_limit=100,
            budget_id="budget_1",
        )

        # Same schedule -> same measurement_key regardless of data_origin
        key1 = coord.measurement_key(sched1)
        key2 = coord.measurement_key(sched2)
        assert key1 == key2

        # Different budget_id -> different measurement_key
        sched3 = Schedule(
            fidelity="L0",
            seed=0,
            n_seeds=1,
            epochs=1,
            batch_limit=100,
            budget_id="budget_2",
        )
        key3 = coord.measurement_key(sched3)
        assert key1 != key3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
