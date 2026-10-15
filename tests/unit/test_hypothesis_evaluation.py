"""Fast unit test for hypothesis evaluation (_test_hypothesis).

Verifies that the hypothesis testing logic returns a StatisticalResult with
p_value, effect_size, and other required fields. Uses synthetic records -
no store, no training, runs in <1s.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from computronium.experiment.design.hypothesis import (
    EffectSizeType,
    HypothesisResult,
    TestType,
    create_default_registry,
)
from computronium.experiment.registry.loop import LoopConfig, LoopDriver
from computronium.experiment.schema.coordinate import Coordinate, Provenance, Schedule
from computronium.experiment.schema.record import (
    FailureCause,
    GateVerdict,
    Maturity,
    Record,
    ReproducibilityClass,
    Severity,
    Status,
)


def _make_synthetic_record(  # ruff: ignore[too-many-arguments]
    *,
    task_id: str = "xor",
    credit: str = "gradient",
    substrate: str = "digital",
    geometry: str = "feedforward",
    dynamics: str = "instantaneous",
    plasticity: str = "null",
    update: str = "euclidean",
    energy_per_step: float = 0.1,
    val_acc: float = 0.9,
    seed: int = 0,
    gate_verdict: GateVerdict = GateVerdict.PASS_,
    maturity: Maturity = Maturity.L1,
) -> Record:
    """Create a synthetic record for testing."""
    coordinate = Coordinate(
        substrate=substrate,
        geometry=geometry,
        dynamics=dynamics,
        plasticity=plasticity,
        credit=credit,
        update=update,
        params={},
    )
    schedule = Schedule(
        fidelity="L1",
        seed=seed,
        n_seeds=1,
        epochs=3,
        batch_limit=0,
        budget_id="test",
        task_id=task_id,
        param_budget=10000,
        device="cpu",
    )
    provenance = Provenance(
        env={},
        dataset=task_id,
        dataset_version="1.0",
        code_sha="test",
        policy="test",
        links={},
    )
    status = Status(
        gate_verdict=gate_verdict,
        defect="",
        cause=FailureCause.UNKNOWN,
        severity=Severity.LOW,
        quarantine=False,
        maturity=maturity,
        uncertainty={},
        reproducibility=ReproducibilityClass.REPLAYABLE,
        assessment_procedure_version="1.0",
        ceec_link=None,
    )
    payload = {"energy_per_step": energy_per_step, "val_acc": val_acc}
    return Record.create(
        run_id="test_run",
        coordinate=coordinate,
        schedule=schedule,
        provenance=provenance,
        status=status,
        payload=payload,
    )


def _make_driver() -> LoopDriver:
    """Create a LoopDriver instance for testing _test_hypothesis."""

    from computronium.experiment.schema import seed_all_registries

    seed_all_registries()

    tmp = tempfile.TemporaryDirectory()
    config = LoopConfig(
        store_path=Path(tmp.name) / "store.duckdb",
        state_dir=Path(tmp.name) / "state",
        stages=("s1_frame", "s2_space", "s3_schedule", "s4_gate", "s5_compose"),
        param_budget=10000,
        policy="round_robin_grid",
        hyperparameters={},
        checkpoint_every_n=0,
        device="cpu",
        master_seed=42,
        hours=0.1,
        cycles=1,
        n_seeds=1,
        explore_fidelity="L0",
        exploit_fidelity="L1",
        explore_hours=0.05,
        exploit_hours=0.05,
        explore_sweep_steps=5,
        exploit_sweep_steps=3,
        epochs_explore=1,
        epochs_exploit=1,
        cell_workers=1,
        task_schedule=("xor",),
        hypothesis_ids=("H1_credit_efficiency",),
    )
    driver = LoopDriver(config)
    # Keep reference to tmpdir to prevent cleanup during test
    # (attached as a private attribute for test lifetime)
    object.__setattr__(driver, "_test_tmpdir", tmp)
    return driver


class TestHypothesisEvaluation:
    """Tests for _test_hypothesis method."""

    def test_test_hypothesis_returns_result_with_p_value_and_effect_size(self):
        """_test_hypothesis returns HypothesisResult with p_value and effect_size."""
        driver = _make_driver()
        registry = create_default_registry()
        hyp = registry.get("H1_credit_efficiency")
        assert hyp is not None

        # Create synthetic records with two credit groups
        records = [
            # gradient credit - higher energy_per_step
            _make_synthetic_record(
                credit="gradient", energy_per_step=0.15, val_acc=0.9, seed=0
            ),
            _make_synthetic_record(
                credit="gradient", energy_per_step=0.16, val_acc=0.91, seed=1
            ),
            _make_synthetic_record(
                credit="gradient", energy_per_step=0.14, val_acc=0.89, seed=2
            ),
            # thermodynamic_contrast credit - lower energy_per_step
            _make_synthetic_record(
                credit="thermodynamic_contrast",
                energy_per_step=0.08,
                val_acc=0.88,
                seed=0,
            ),
            _make_synthetic_record(
                credit="thermodynamic_contrast",
                energy_per_step=0.09,
                val_acc=0.87,
                seed=1,
            ),
            _make_synthetic_record(
                credit="thermodynamic_contrast",
                energy_per_step=0.07,
                val_acc=0.89,
                seed=2,
            ),
        ]

        # Override hypothesis to group by credit (not substrate)
        hyp.grouping_factor = "credit"
        hyp.comparison_values = ["gradient", "thermodynamic_contrast"]
        hyp.primary_metric = "energy_per_step"
        hyp.test_type = TestType.INDEPENDENT_T_TEST
        hyp.paired = False

        result = driver._test_hypothesis(hyp, records, "xor")

        # Verify result structure
        assert isinstance(result, HypothesisResult)
        assert result.hypothesis_id == "H1_credit_efficiency"
        assert result.p_value is not None
        assert result.effect_size is not None
        assert result.test_statistic is not None
        assert result.n_samples == 6
        assert result.n_groups == 2
        assert result.groups_tested == ["gradient", "thermodynamic_contrast"]
        assert result.significant is not None
        assert result.confidence_interval is not None

    def test_test_hypothesis_insufficient_groups_returns_inconclusive(self):
        """_test_hypothesis returns inconclusive when groups < 2."""
        driver = _make_driver()
        registry = create_default_registry()
        hyp = registry.get("H1_credit_efficiency")
        assert hyp is not None

        # Only one credit group
        records = [
            _make_synthetic_record(credit="gradient", energy_per_step=0.15, seed=0),
            _make_synthetic_record(credit="gradient", energy_per_step=0.16, seed=1),
        ]

        hyp.grouping_factor = "credit"
        hyp.comparison_values = ["gradient", "thermodynamic_contrast"]
        hyp.primary_metric = "energy_per_step"

        result = driver._test_hypothesis(hyp, records, "xor")

        assert result.n_groups == 1
        assert result.notes == "Insufficient groups for comparison"
        assert result.p_value is None
        assert result.effect_size is None

    def test_test_hypothesis_no_records_returns_empty(self):
        """_test_hypothesis handles empty records gracefully."""
        driver = _make_driver()
        registry = create_default_registry()
        hyp = registry.get("H1_credit_efficiency")
        assert hyp is not None

        records = []

        hyp.grouping_factor = "credit"
        hyp.comparison_values = ["gradient", "thermodynamic_contrast"]
        hyp.primary_metric = "energy_per_step"

        result = driver._test_hypothesis(hyp, records, "xor")

        assert result.n_samples == 0
        assert result.n_groups == 0
        assert result.notes == "No records for hypothesis"
        assert result.p_value is None

    def test_test_hypothesis_mann_whitney_u(self):
        """_test_hypothesis works with Mann-Whitney U test."""
        driver = _make_driver()
        registry = create_default_registry()
        hyp = registry.get("H1_credit_efficiency")
        assert hyp is not None

        records = [
            _make_synthetic_record(credit="gradient", energy_per_step=0.15, seed=0),
            _make_synthetic_record(credit="gradient", energy_per_step=0.16, seed=1),
            _make_synthetic_record(
                credit="thermodynamic_contrast", energy_per_step=0.08, seed=0
            ),
            _make_synthetic_record(
                credit="thermodynamic_contrast", energy_per_step=0.09, seed=1
            ),
        ]

        hyp.grouping_factor = "credit"
        hyp.comparison_values = ["gradient", "thermodynamic_contrast"]
        hyp.primary_metric = "energy_per_step"
        hyp.test_type = TestType.MANN_WHITNEY_U
        hyp.effect_size_type = EffectSizeType.CLIFFS_DELTA
        hyp.paired = False

        result = driver._test_hypothesis(hyp, records, "xor")

        assert result.p_value is not None
        assert result.effect_size is not None
        assert result.effect_size_type == "cliffs_delta"
        assert result.test_type == "mann_whitney_u"

    def test_test_hypothesis_one_way_anova(self):
        """_test_hypothesis works with one-way ANOVA (pairwise comparison of first two groups)."""
        driver = _make_driver()
        registry = create_default_registry()
        hyp = registry.get("H1_credit_efficiency")
        assert hyp is not None

        records = [
            _make_synthetic_record(credit="gradient", energy_per_step=0.15, seed=0),
            _make_synthetic_record(credit="gradient", energy_per_step=0.16, seed=1),
            _make_synthetic_record(
                credit="thermodynamic_contrast", energy_per_step=0.08, seed=0
            ),
            _make_synthetic_record(
                credit="thermodynamic_contrast", energy_per_step=0.09, seed=1
            ),
            _make_synthetic_record(
                credit="random_projections", energy_per_step=0.12, seed=0
            ),
            _make_synthetic_record(
                credit="random_projections", energy_per_step=0.13, seed=1
            ),
        ]

        hyp.grouping_factor = "credit"
        hyp.comparison_values = [
            "gradient",
            "thermodynamic_contrast",
            "random_projections",
        ]
        hyp.primary_metric = "energy_per_step"
        hyp.test_type = TestType.ANOVA_ONE_WAY
        hyp.effect_size_type = EffectSizeType.ETA_SQUARED
        hyp.paired = False

        result = driver._test_hypothesis(hyp, records, "xor")

        assert result.p_value is not None
        assert result.effect_size is not None
        assert result.effect_size_type == "eta_squared"
        assert result.test_type == "anova_one_way"
        # Current implementation only compares first two groups in comparison_values
        assert len(result.groups_tested) == 2
        assert result.groups_tested == ["gradient", "thermodynamic_contrast"]

    def test_hypothesis_result_to_statistical_result(self):
        """HypothesisResult.to_statistical_result() produces valid StatisticalResult."""
        driver = _make_driver()
        registry = create_default_registry()
        hyp = registry.get("H1_credit_efficiency")
        assert hyp is not None

        records = [
            _make_synthetic_record(credit="gradient", energy_per_step=0.15, seed=0),
            _make_synthetic_record(credit="gradient", energy_per_step=0.16, seed=1),
            _make_synthetic_record(credit="gradient", energy_per_step=0.14, seed=2),
            _make_synthetic_record(
                credit="thermodynamic_contrast", energy_per_step=0.08, seed=0
            ),
            _make_synthetic_record(
                credit="thermodynamic_contrast", energy_per_step=0.09, seed=1
            ),
            _make_synthetic_record(
                credit="thermodynamic_contrast", energy_per_step=0.07, seed=2
            ),
        ]

        hyp.grouping_factor = "credit"
        hyp.comparison_values = ["gradient", "thermodynamic_contrast"]
        hyp.primary_metric = "energy_per_step"
        hyp.test_type = TestType.INDEPENDENT_T_TEST
        hyp.effect_size_type = EffectSizeType.COHENS_D

        result = driver._test_hypothesis(hyp, records, "xor")
        stat_result = result.to_statistical_result()

        assert stat_result.hypothesis_id == "H1_credit_efficiency"
        assert stat_result.test_name == "independent_t_test"
        assert stat_result.p_value is not None
        assert stat_result.effect_size is not None
        assert stat_result.effect_size_type == "cohens_d"
        assert stat_result.confidence_interval is not None
        assert stat_result.significant is not None
        assert stat_result.n_samples == 6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
