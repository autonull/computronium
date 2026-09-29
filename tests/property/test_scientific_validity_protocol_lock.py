"""Lockstep tests for WP1.5 Scientific Validity Protocol.

Asserts that the protocol fields exist, splits are enforced,
comparisons are guarded, and the synthetic fixture recovers known effects.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from computronium.experiment.evidence.protocol import (
    SYNTHETIC_FIXTURE,
    ComparisonGuard,
    CostBudget,
    CostBudgetKind,
    EffectSizeResult,
    SyntheticGroundTruth,
    cohens_d_paired,
    compute_effect_size,
    create_synthetic_fixture,
    wilcoxon_paired,
)
from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.schema.coordinate import (
    Coordinate,
    DataOrigin,
    Provenance,
    Schedule,
    TransferMode,
)
from computronium.experiment.schema.record import (
    FailureCause,
    GateVerdict,
    Maturity,
    Record,
    ReproducibilityClass,
    Severity,
    Status,
)


class TestCostBudget:
    """Tests for CostBudget and matched-cost comparison protocol."""

    def test_cost_budget_creation(self) -> None:
        budget = CostBudget.eval_count(100)
        assert budget.kind == CostBudgetKind.EVAL_COUNT
        assert budget.limit == 100.0

    def test_cost_budget_matches_same(self) -> None:
        budget1 = CostBudget.walltime(60.0)
        budget2 = CostBudget.walltime(60.0)
        assert budget1.matches(budget2)

    def test_cost_budget_mismatch_kind(self) -> None:
        budget1 = CostBudget.eval_count(100)
        budget2 = CostBudget.walltime(100.0)
        assert not budget1.matches(budget2)

    def test_cost_budget_mismatch_limit(self) -> None:
        budget1 = CostBudget.eval_count(100)
        budget2 = CostBudget.eval_count(200)
        assert not budget1.matches(budget2)

    def test_comparison_guard_passes_matching(self) -> None:
        budget = CostBudget.flops(1e12)
        guard = ComparisonGuard(budget)
        guard.check(CostBudget.flops(1e12))  # Should not raise

    def test_comparison_guard_raises_mismatch(self) -> None:
        budget = CostBudget.eval_count(100)
        guard = ComparisonGuard(budget)
        with pytest.raises(Exception, match="Budget mismatch"):
            guard.check(CostBudget.eval_count(200))

    def test_comparison_guard_label_unmatched(self) -> None:
        budget = CostBudget.eval_count(100)
        guard = ComparisonGuard(budget)
        matches, label = guard.check_or_label(
            CostBudget.walltime(60.0), label_unmatched=True
        )
        assert matches is False
        assert label is not None
        assert "BUDGET_MISMATCH" in label


class TestEffectSize:
    """Tests for effect size computation with CI and p-values."""

    def test_cohens_d_paired_basic(self) -> None:
        treatment = [0.8, 0.85, 0.9, 0.82, 0.88]
        control = [0.7, 0.75, 0.8, 0.72, 0.78]
        d, ci_lower, ci_upper, p = cohens_d_paired(treatment, control)
        assert d > 0  # Treatment better
        assert ci_lower < d < ci_upper
        assert 0 <= p <= 1

    def test_cohens_d_paired_zero_diff(self) -> None:
        treatment = [0.8, 0.8, 0.8, 0.8]
        control = [0.8, 0.8, 0.8, 0.8]
        d, ci_lower, ci_upper, p = cohens_d_paired(treatment, control)
        assert d == 0.0
        assert ci_lower < d < ci_upper
        assert p == 1.0

    def test_wilcoxon_paired(self) -> None:
        # Use clearly different samples - just verify function runs and returns valid p-value
        treatment = [0.9, 0.95, 0.92, 0.88, 0.94]
        control = [0.5, 0.55, 0.6, 0.45, 0.5]
        stat, p = wilcoxon_paired(treatment, control)
        assert isinstance(stat, float)
        assert 0 <= p <= 1

    def test_compute_effect_size_protocol_requirements(self) -> None:
        """Protocol requires N_tasks >= 10, N_seeds >= 5."""
        treatment = [0.85] * 10
        control = [0.75] * 10
        budget = CostBudget.eval_count(100)

        # Should pass with N_tasks=10, N_seeds=5
        result = compute_effect_size(
            treatment, control, "accuracy", budget, n_tasks=10, n_seeds=5
        )
        assert isinstance(result, EffectSizeResult)
        assert result.n_tasks == 10
        assert result.n_seeds == 5
        assert result.budget == budget

    def test_compute_effect_size_rejects_insufficient_tasks(self) -> None:
        treatment = [0.85] * 5
        control = [0.75] * 5
        budget = CostBudget.eval_count(100)
        with pytest.raises(ValueError, match="N_tasks >= 10"):
            compute_effect_size(
                treatment, control, "accuracy", budget, n_tasks=5, n_seeds=5
            )

    def test_compute_effect_size_rejects_insufficient_seeds(self) -> None:
        treatment = [0.85] * 10
        control = [0.75] * 10
        budget = CostBudget.eval_count(100)
        with pytest.raises(ValueError, match="N_seeds >= 5"):
            compute_effect_size(
                treatment, control, "accuracy", budget, n_tasks=10, n_seeds=3
            )

    def test_effect_size_result_significance(self) -> None:
        result = EffectSizeResult(
            primary_metric="accuracy",
            effect_size=0.8,
            ci_lower=0.3,
            ci_upper=1.3,
            p_value=0.01,
            test_used="paired_t",
            n_tasks=10,
            n_seeds=5,
            budget=CostBudget.eval_count(100),
        )
        assert result.is_significant(0.05)
        assert not result.is_significant(0.001)


class TestSyntheticFixture:
    """Tests for the synthetic known-ground-truth fixture."""

    def test_synthetic_fixture_creation(self) -> None:
        fixture = create_synthetic_fixture(dimension=4, noise_std=0.0)
        assert fixture.dimension == 4
        assert fixture.optimum == (1.0, 2.0, 3.0, 4.0)
        assert fixture.noise_std == 0.0

    def test_synthetic_fixture_evaluate_at_optimum(self) -> None:
        fixture = create_synthetic_fixture(dimension=3, noise_std=0.0)
        value = fixture.evaluate(fixture.true_optimum(), seed=42)
        assert value == 0.0  # At optimum, no noise

    def test_synthetic_fixture_evaluate_away_from_optimum(self) -> None:
        # Use interaction_strength=0 to avoid interaction terms
        fixture = create_synthetic_fixture(
            dimension=2, noise_std=0.0, interaction_strength=0.0
        )
        value = fixture.evaluate((0.0, 0.0), seed=42)
        expected = (0.0 - 1.0) ** 2 + (0.0 - 2.0) ** 2
        assert value == expected

    def test_synthetic_fixture_with_interactions(self) -> None:
        fixture = create_synthetic_fixture(
            dimension=2, interaction_strength=0.5, noise_std=0.0
        )
        # At optimum
        assert fixture.evaluate((1.0, 2.0), seed=42) == 0.0
        # Away from optimum - includes interaction terms
        val = fixture.evaluate((0.0, 0.0), seed=42)
        # (x-1)^2 + (y-2)^2 + 2*0.5*(x-1)*(y-2)
        # = 1 + 4 + 2*0.5*1*2 = 5 + 2 = 7
        assert val == 7.0

    def test_synthetic_fixture_true_effect_size(self) -> None:
        fixture = create_synthetic_fixture(dimension=2, noise_std=0.1)
        baseline = (0.0, 0.0)
        effect = fixture.true_effect_size(baseline)
        # True difference / noise_std
        # baseline_val = 1^2 + 2^2 = 5
        # opt_val = 0
        # effect = 5 / 0.1 = 50
        assert effect == 50.0

    def test_global_synthetic_fixture_exists(self) -> None:
        assert SYNTHETIC_FIXTURE is not None
        assert isinstance(SYNTHETIC_FIXTURE, SyntheticGroundTruth)
        assert SYNTHETIC_FIXTURE.dimension == 6


class TestDataOriginAndTransferProvenance:
    """Tests for data origin tagging and transfer learning provenance."""

    def test_data_origin_enum(self) -> None:
        assert DataOrigin.EXPLORATION == "exploration"
        assert DataOrigin.POLICY_SELECTED == "policy_selected"
        assert DataOrigin.CALIBRATION == "calibration"
        assert DataOrigin.TEST == "test"

    def test_transfer_mode_enum(self) -> None:
        assert TransferMode.ZERO_SHOT == "zero_shot"
        assert TransferMode.FEW_SHOT == "few_shot"
        assert TransferMode.FULL == "full"

    def test_provenance_with_data_origin(self) -> None:
        prov = Provenance(
            env={"python": "3.14"},
            dataset="mnist",
            dataset_version="1.0",
            code_sha="abc123",
            policy="test_policy",
            links={},
            data_origin=DataOrigin.POLICY_SELECTED,
            training_tasks=("task1", "task2"),
            transfer_source_ids=("src1", "src2"),
            transfer_cutoff="2024-01-01",
            target_task="target1",
            transfer_mode=TransferMode.FEW_SHOT,
        )
        assert prov.data_origin == DataOrigin.POLICY_SELECTED
        assert prov.training_tasks == ("task1", "task2")
        assert prov.transfer_mode == TransferMode.FEW_SHOT

    def test_provenance_roundtrip(self) -> None:
        prov = Provenance(
            env={"python": "3.14"},
            dataset="mnist",
            dataset_version="1.0",
            code_sha="abc123",
            policy="test_policy",
            links={},
            data_origin=DataOrigin.CALIBRATION,
        )
        data = prov.to_dict()
        restored = Provenance.from_dict(data)
        assert restored.data_origin == DataOrigin.CALIBRATION
        assert restored.dataset == "mnist"

    def test_provenance_defaults(self) -> None:
        prov = Provenance(
            env={},
            dataset="test",
            dataset_version="1.0",
            code_sha="sha",
            policy="policy",
            links={},
        )
        assert prov.data_origin == DataOrigin.EXPLORATION
        assert prov.training_tasks == ()
        assert prov.transfer_mode is None


class TestReproducibilityClasses:
    """Tests for the three reproducibility classes."""

    def test_reproducibility_class_enum(self) -> None:
        assert ReproducibilityClass.REPLAYABLE == "replayable"
        assert (
            ReproducibilityClass.COMPUTATIONALLY_REPRODUCIBLE
            == "computationally_reproducible"
        )
        assert (
            ReproducibilityClass.SCIENTIFICALLY_REPRODUCIBLE
            == "scientifically_reproducible"
        )

    def test_status_requires_reproducibility_class(self) -> None:
        status = Status(
            gate_verdict=GateVerdict.PASS_,
            defect="",
            cause=FailureCause.UNKNOWN,
            severity=Severity.LOW,
            quarantine=False,
            maturity=Maturity.L1,
            uncertainty={},
            reproducibility=ReproducibilityClass.REPLAYABLE,
            assessment_procedure_version="1.0",
            ceec_link=None,
        )
        assert status.reproducibility == ReproducibilityClass.REPLAYABLE

    def test_status_rejects_string_reproducibility(self) -> None:
        with pytest.raises(TypeError, match="ReproducibilityClass"):
            Status(
                gate_verdict=GateVerdict.PASS_,
                defect="",
                cause=FailureCause.UNKNOWN,
                severity=Severity.LOW,
                quarantine=False,
                maturity=Maturity.L1,
                uncertainty={},
                reproducibility="replayable",  # String, not enum
                assessment_procedure_version="1.0",
                ceec_link=None,
            )

    def test_status_requires_assessment_procedure_version(self) -> None:
        with pytest.raises(TypeError):
            Status(
                gate_verdict=GateVerdict.PASS_,
                defect="",
                cause=FailureCause.UNKNOWN,
                severity=Severity.LOW,
                quarantine=False,
                maturity=Maturity.L1,
                uncertainty={},
                reproducibility=ReproducibilityClass.REPLAYABLE,
                # assessment_procedure_version missing
                ceec_link=None,
            )


class TestScientificValidityProtocolIntegration:
    """Integration tests: synthetic fixture recovers known effects through the full pipeline."""

    def test_synthetic_fixture_recovers_known_optimum(self) -> None:
        """The synthetic fixture should allow recovering the known analytical optimum."""
        fixture = SYNTHETIC_FIXTURE

        # Evaluate at various points
        opt_val = fixture.evaluate(fixture.true_optimum())
        baseline_val = fixture.evaluate((0.0,) * fixture.dimension)

        # Optimum should be better (lower) than baseline
        assert opt_val < baseline_val

    def test_synthetic_fixture_knows_true_effect_size(self) -> None:
        """The fixture knows the true effect size analytically."""
        fixture = SYNTHETIC_FIXTURE
        baseline = (0.0,) * fixture.dimension
        true_effect = fixture.true_effect_size(baseline)

        # With noise_std=0.1 and baseline at origin, effect should be large
        assert true_effect > 10.0  # Significant effect

    def test_protocol_enforces_minimum_tasks_and_seeds(self) -> None:
        """The effect size protocol enforces N_tasks >= 10, N_seeds >= 5."""
        budget = CostBudget.eval_count(100)

        # Generate synthetic data for 10 tasks x 5 seeds
        treatment = [0.85] * 50  # 10 tasks * 5 seeds
        control = [0.75] * 50

        result = compute_effect_size(
            treatment, control, "accuracy", budget, n_tasks=10, n_seeds=5
        )
        assert result.n_tasks == 10
        assert result.n_seeds == 5

    def test_store_persists_protocol_fields(self) -> None:
        """RecordStore should persist all protocol fields including data_origin, reproducibility_class."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "test.duckdb"
            config = StoreConfig(path=store_path)

            with RecordStore(config) as store:
                # Create run
                run_id = store.create_run()

                # Create coordinate
                coord = Coordinate(
                    substrate="Digital",
                    geometry="Feedforward",
                    dynamics="Instantaneous",
                    plasticity="NullPlasticity",
                    credit="Backprop",
                    update="Euclidean",
                    params={"lr": 0.01},
                )

                # Create schedule
                sched = Schedule(
                    fidelity="L1",
                    seed=42,
                    n_seeds=1,
                    epochs=10,
                    batch_limit=100,
                    budget_id="test_budget",
                )

                # Create provenance with protocol fields
                prov = Provenance(
                    env={"python": "3.14"},
                    dataset="synthetic",
                    dataset_version="1.0",
                    code_sha="sha123",
                    policy="test_policy",
                    links={"run_id": run_id},
                    data_origin=DataOrigin.EXPLORATION,
                )

                # Create status with protocol fields
                status = Status(
                    gate_verdict=GateVerdict.PASS_,
                    defect="",
                    cause=FailureCause.UNKNOWN,
                    severity=Severity.LOW,
                    quarantine=False,
                    maturity=Maturity.L1,
                    uncertainty={"std": 0.01},
                    reproducibility=ReproducibilityClass.COMPUTATIONALLY_REPRODUCIBLE,
                    assessment_procedure_version="1.0",
                    ceec_link=None,
                )

                # Create and append record
                record = Record.create(
                    run_id=run_id,
                    coordinate=coord,
                    schedule=sched,
                    provenance=prov,
                    status=status,
                    payload={"accuracy": 0.95},
                )

                appended = store.append(record)

                # Retrieve and verify
                retrieved = store.get_record(appended.record_id)
                assert retrieved is not None
                assert retrieved.provenance.data_origin == DataOrigin.EXPLORATION
                assert (
                    retrieved.status.reproducibility
                    == ReproducibilityClass.COMPUTATIONALLY_REPRODUCIBLE
                )
                assert retrieved.status.assessment_procedure_version == "1.0"

    def test_claim_eligible_prefilter_uses_protocol_fields(self) -> None:
        """The SQL prefilter should work with protocol fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "test.duckdb"
            config = StoreConfig(path=store_path)

            with RecordStore(config) as store:
                run_id = store.create_run()

                coord = Coordinate(
                    substrate="Digital",
                    geometry="Feedforward",
                    dynamics="Instantaneous",
                    plasticity="NullPlasticity",
                    credit="Backprop",
                    update="Euclidean",
                    params={},
                )

                # Add records with different fidelities and n_seeds
                for i, (fidelity, n_seeds, verdict) in enumerate([
                    ("L0", 1, GateVerdict.PASS_),
                    ("L1", 3, GateVerdict.PASS_),
                    ("L2", 5, GateVerdict.PASS_),
                    ("L2", 10, GateVerdict.PASS_),
                    ("L2", 5, GateVerdict.FAIL),  # Should be excluded
                ]):
                    sched = Schedule(
                        fidelity=fidelity,
                        seed=42
                        + i,  # Different seed per iteration to ensure unique measurement_key
                        n_seeds=n_seeds,
                        epochs=10,
                        batch_limit=100,
                        budget_id="test",
                    )
                    prov = Provenance(
                        env={},
                        dataset="test",
                        dataset_version="1.0",
                        code_sha="sha",
                        policy="policy",
                        links={"run_id": run_id},
                    )
                    status = Status(
                        gate_verdict=verdict,
                        defect="",
                        cause=FailureCause.UNKNOWN,
                        severity=Severity.LOW,
                        quarantine=False,
                        maturity=Maturity.L1,
                        uncertainty={},
                        reproducibility=ReproducibilityClass.REPLAYABLE,
                        assessment_procedure_version="1.0",
                        ceec_link=None,
                    )
                    record = Record.create(
                        run_id=run_id,
                        coordinate=coord,
                        schedule=sched,
                        provenance=prov,
                        status=status,
                        payload={},
                    )
                    store.append(record)

                # Prefilter: L2, n_seeds >= 5, PASS, not quarantined
                eligible = store.claim_eligible_prefilter(fidelity="L2", min_n_seeds=5)
                # Should get 2 records: (L2, 5) and (L2, 10)
                assert len(eligible) == 2
                for rec in eligible:
                    assert rec.schedule.fidelity == "L2"
                    assert rec.schedule.n_seeds >= 5
                    assert rec.status.gate_verdict == GateVerdict.PASS_
                    assert not rec.status.quarantine


__all__ = []
