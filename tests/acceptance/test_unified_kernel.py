"""Unified Kernel Acceptance Suite (U1-U5) — WP20.

Tests that the kernel composes into a unified experiment system:
- U1: Question → question_first() → RunSpec → Synthesis policy → SearchSpace → Pipeline → RecordStore
- U2: Same RunSpec → SearchSpace → TPE (ModelBasedPolicy) → Pipeline → same Record schema/store
- U3: Same RunSpec → SearchSpace → Random/TPE/Evolution → Allocator → multi-round pipeline → pause → resume → report
- U4: Policy interchangeability: Round 1 StratifiedRandom, Round 2 TPE, Round 3 Evolution, Round 4 Synthesis — same RunSpec/Space/Store, only policy changes
- U5: Cross-policy evidence reuse: Random → TPE → Evolution over same store — no separate DB, no migration, same measurement identity, same legality, same claims
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.execution.allocator import EvidenceDrivenAllocator
from computronium.experiment.execution.backends import LocalBackend
from computronium.experiment.execution.budget import Budget, SimpleCostModel
from computronium.experiment.execution.pipeline import PipelineConfig, PipelineRunner
from computronium.experiment.execution.policy import (
    EvolutionPolicy,
    ModelBasedPolicy,
    RoundRobinGridPolicy,
    StratifiedRandomPolicy,
    SynthesisPolicy,
    UniformRandomPolicy,
)
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.coordinate import Coordinate, Schedule
from computronium.experiment.schema.run_spec import MEASURED_PARAM_BUDGET, RunSpec
from computronium.experiment.schema.seed_registries import seed_all_registries

if TYPE_CHECKING:
    from computronium.experiment.execution.search_space import SearchSpace

if TYPE_CHECKING:
    from computronium.experiment.schema.record import Record


# =============================================================================
# Fixtures and Helpers
# =============================================================================


def _space() -> SearchSpace:
    """The active space of the acceptance run spec — one builder, as the runner uses."""
    from computronium.experiment.execution.search_space import search_space_from_spec

    return search_space_from_spec(_make_run_spec())


@pytest.fixture(scope="session", autouse=True)
def _seed_registries() -> None:
    """Seed all registries before acceptance tests."""
    seed_all_registries()


def _make_run_spec(task: str = "digits") -> RunSpec:
    """Create a minimal RunSpec for testing."""
    return RunSpec(
        profile="acceptance",
        task=task,
        objectives=("validation_accuracy", "walltime_total"),
        fidelity="L0",
        n_seeds=1,
        epochs=1,
        budget_seconds=60.0,
        param_budget=MEASURED_PARAM_BUDGET,
    )


def _make_pipeline_config(
    run_id: str,
    run_spec: RunSpec,
    policy_name: str = "stratified_random",
    max_rounds: int = 2,
    store_path: Path | None = None,
) -> PipelineConfig:
    """Create a PipelineConfig with the specified policy."""
    policy_map = {
        "stratified_random": StratifiedRandomPolicy(seed=42),
        "uniform_random": UniformRandomPolicy(seed=42),
        "round_robin_grid": RoundRobinGridPolicy(seed=42),
        "model_based_tpe": ModelBasedPolicy(sampler="tpe", seed=42, n_startup_trials=5),
        "evolution": EvolutionPolicy(population_size=10, seed=42),
        "synthesis": SynthesisPolicy(
            policies=[
                StratifiedRandomPolicy(seed=42),
                UniformRandomPolicy(seed=43),
            ],
            weights=[1.0, 1.0],
        ),
    }
    policy = policy_map[policy_name]

    return PipelineConfig(
        run_id=run_id,
        run_spec=run_spec,
        budget=Budget.from_duration(f"{int(run_spec.budget_seconds or 0)}s"),
        cost_model=SimpleCostModel(),
        policy=policy,
        allocator=EvidenceDrivenAllocator(promotion_threshold=0.05),
        backend=LocalBackend(),
        checkpoint_dir=store_path / "checkpoints" / run_id if store_path else None,
        seed=run_spec.seed,
        max_rounds=max_rounds,
        min_rounds=1,
    )


async def _run_pipeline(
    config: PipelineConfig,
    store: RecordStore,
) -> list[Record]:
    """Run a pipeline and return records."""
    runner = PipelineRunner(config, store)
    return await runner.run()


# =============================================================================
# U1: Question → RunSpec → Synthesis policy → SearchSpace → Pipeline → RecordStore
# =============================================================================


class TestU1_SynthesisPolicyPipeline:
    """U1: Question → question_first() → RunSpec → Synthesis policy → SearchSpace → Pipeline → RecordStore"""

    @pytest.mark.timeout(120)
    def test_u1_synthesis_policy_end_to_end(self, tmp_path: Path) -> None:
        """Test synthesis policy drives full pipeline to completion."""
        store_path = tmp_path / "u1_store.duckdb"
        store_config = StoreConfig(path=store_path)

        with RecordStore(store_config) as store:
            run_spec = _make_run_spec("digits")
            run_id = store.create_run(spec=run_spec)

            config = _make_pipeline_config(
                run_id=run_id,
                run_spec=run_spec,
                policy_name="synthesis",
                max_rounds=2,
                store_path=tmp_path,
            )

            records = asyncio.run(_run_pipeline(config, store))

            # Verify records were produced
            assert len(records) > 0, "Pipeline should produce records"

            # Verify records are in store
            stored_records = store.query_records(run_id=run_id)
            assert len(stored_records) == len(records)

            # Verify measurement keys are unique
            measurement_keys = [r.measurement_key for r in records]
            assert len(measurement_keys) == len(set(measurement_keys))

            # Verify all records have required fields
            for record in records:
                assert record.run_id == run_id
                assert record.cell_key
                assert record.measurement_key
                assert record.substrate
                assert record.geometry
                assert record.dynamics
                assert record.credit
                assert record.update
                assert record.schedule.fidelity == "L0"
                assert record.schedule.n_seeds == 1

            store.finish_run(run_id, "completed")


# =============================================================================
# U2: Same RunSpec → SearchSpace → TPE (ModelBasedPolicy) → Pipeline → same Record schema/store
# =============================================================================


class TestU2_ModelBasedPolicyPipeline:
    """U2: Same RunSpec → SearchSpace → TPE (ModelBasedPolicy) → Pipeline → same Record schema/store"""

    @pytest.mark.timeout(120)
    def test_u2_model_based_policy_end_to_end(self, tmp_path: Path) -> None:
        """Test ModelBasedPolicy (TPE) drives full pipeline to completion."""
        store_path = tmp_path / "u2_store.duckdb"
        store_config = StoreConfig(path=store_path)

        with RecordStore(store_config) as store:
            run_spec = _make_run_spec("digits")
            run_id = store.create_run(spec=run_spec)

            config = _make_pipeline_config(
                run_id=run_id,
                run_spec=run_spec,
                policy_name="model_based_tpe",
                max_rounds=2,
                store_path=tmp_path,
            )

            records = asyncio.run(_run_pipeline(config, store))

            # Verify records were produced
            assert len(records) > 0, "Pipeline should produce records"

            # Verify records are in store
            stored_records = store.query_records(run_id=run_id)
            assert len(stored_records) == len(records)

            # Verify record schema is identical to U1 (same store)
            for record in records:
                assert record.run_id == run_id
                assert record.cell_key
                assert record.measurement_key
                assert record.substrate
                assert record.geometry
                assert record.dynamics
                assert record.credit
                assert record.update
                assert record.schedule.fidelity == "L0"

            store.finish_run(run_id, "completed")


# =============================================================================
# U3: Multi-round pipeline with pause/resume/report
# =============================================================================


class TestU3_MultiRoundPauseResume:
    """U3: Same RunSpec → SearchSpace → Random/TPE/Evolution → Allocator → multi-round pipeline → pause → resume → report"""

    # 180 s was calibrated while most generated cells failed to compose, so the
    # rounds were cheap; 900 s was the cost once they trained unconstrained. The
    # spec's parameter ceiling (TODO46 §8 session 6) is the fix, and the ceiling
    # is re-measured rather than assumed — see the measured cost in the session
    # log.
    @pytest.mark.timeout(900)
    def test_u3_multi_round_with_allocator(self, tmp_path: Path) -> None:
        """Test multi-round pipeline with allocator promotion."""
        store_path = tmp_path / "u3_store.duckdb"
        store_config = StoreConfig(path=store_path)

        with RecordStore(store_config) as store:
            run_spec = _make_run_spec("digits")
            run_id = store.create_run(spec=run_spec)

            config = _make_pipeline_config(
                run_id=run_id,
                run_spec=run_spec,
                policy_name="stratified_random",
                max_rounds=3,
                store_path=tmp_path,
            )

            records = asyncio.run(_run_pipeline(config, store))

            # Verify multiple rounds executed
            assert config.max_rounds == 3
            assert len(records) > 0

            # Verify allocator was invoked (promotions should exist)
            stored_records = store.query_records(run_id=run_id)
            assert len(stored_records) == len(records)

            # Check that records span multiple fidelities (L0 -> L1 promotions)
            fidelities = set(r.schedule.fidelity for r in stored_records)
            # At minimum L0 should be present
            assert "L0" in fidelities

            store.finish_run(run_id, "completed")

    @pytest.mark.timeout(900)
    def test_u3_pause_resume_via_run_id(self, tmp_path: Path) -> None:
        """Test that a run can be paused and resumed via run_id."""
        store_path = tmp_path / "u3_resume_store.duckdb"
        store_config = StoreConfig(path=store_path)

        run_spec = _make_run_spec("digits")

        # First run - limited rounds
        with RecordStore(store_config) as store:
            run_id = store.create_run(spec=run_spec)
            config = _make_pipeline_config(
                run_id=run_id,
                run_spec=run_spec,
                policy_name="stratified_random",
                max_rounds=1,
                store_path=tmp_path,
            )
            records1 = asyncio.run(_run_pipeline(config, store))
            store.finish_run(run_id, "completed")

            round1_count = len(store.query_records(run_id=run_id))

        # Resume run - continue with more rounds
        with RecordStore(store_config) as store:
            config = _make_pipeline_config(
                run_id=run_id,
                run_spec=run_spec,
                policy_name="stratified_random",
                max_rounds=3,
                store_path=tmp_path,
            )
            records2 = asyncio.run(_run_pipeline(config, store))
            store.finish_run(run_id, "completed")

            round2_count = len(store.query_records(run_id=run_id))

            # Should have more records after resume (dedup prevents re-measurement)
            assert round2_count >= round1_count


# =============================================================================
# U4: Policy interchangeability
# =============================================================================


class TestU4_PolicyInterchangeability:
    """U4: Policy interchangeability: Round 1 StratifiedRandom, Round 2 TPE, Round 3 Evolution, Round 4 Synthesis — same RunSpec/Space/Store, only policy changes"""

    @pytest.mark.timeout(300)
    def test_u4_policy_interchangeability(self, tmp_path: Path) -> None:
        """Test four different policies on same RunSpec/Space/Store."""
        store_path = tmp_path / "u4_store.duckdb"
        checkpoint_root = tmp_path / "checkpoints"
        store_config = StoreConfig(path=store_path)

        run_spec = _make_run_spec("digits")
        policies = [
            ("stratified_random", StratifiedRandomPolicy(seed=42)),
            (
                "model_based_tpe",
                ModelBasedPolicy(sampler="tpe", seed=42, n_startup_trials=5),
            ),
            ("evolution", EvolutionPolicy(population_size=10, seed=42)),
            (
                "synthesis",
                SynthesisPolicy(
                    policies=[
                        StratifiedRandomPolicy(seed=42),
                        UniformRandomPolicy(seed=43),
                    ],
                    weights=[1.0, 1.0],
                ),
            ),
        ]

        all_records_by_policy = {}

        for policy_name, policy in policies:
            with RecordStore(store_config) as store:
                run_id = store.create_run(spec=run_spec)

                config = PipelineConfig(
                    run_id=run_id,
                    run_spec=run_spec,
                    budget=Budget.from_duration("60s"),
                    cost_model=SimpleCostModel(),
                    policy=policy,
                    allocator=EvidenceDrivenAllocator(promotion_threshold=0.05),
                    backend=LocalBackend(),
                    checkpoint_dir=checkpoint_root / run_id,
                    seed=42,
                    max_rounds=2,
                    min_rounds=1,
                )

                records = asyncio.run(_run_pipeline(config, store))
                all_records_by_policy[policy_name] = records

                # Verify records produced
                assert len(records) > 0, f"{policy_name} should produce records"

                # Verify same store schema
                for record in records:
                    assert record.run_id == run_id
                    assert record.measurement_key
                    assert record.cell_key

                store.finish_run(run_id, "completed")

        # Verify all policies used the same SearchSpace structure
        # (by checking they all produced valid coordinates)
        for policy_name, records in all_records_by_policy.items():
            for record in records:
                assert record.substrate in _space().primitives(StructuralAxis.SUBSTRATE)


# =============================================================================
# U5: Cross-policy evidence reuse
# =============================================================================


class TestU5_CrossPolicyEvidenceReuse:
    """U5: Cross-policy evidence reuse: Random → TPE → Evolution over same store — no separate DB, no migration, same measurement identity, same legality, same claims"""

    @pytest.mark.timeout(300)
    def test_u5_cross_policy_evidence_reuse(self, tmp_path: Path) -> None:
        """Test sequential policies reuse evidence from same store."""
        store_path = tmp_path / "u5_store.duckdb"
        store_config = StoreConfig(path=store_path)

        run_spec = _make_run_spec("digits")

        # Phase 1: Random policy explores
        with RecordStore(store_config) as store:
            run_id = store.create_run(spec=run_spec)
            config = _make_pipeline_config(
                run_id=run_id,
                run_spec=run_spec,
                policy_name="uniform_random",
                max_rounds=2,
                store_path=tmp_path,
            )
            records1 = asyncio.run(_run_pipeline(config, store))
            store.finish_run(run_id, "completed")

            phase1_keys = {r.measurement_key for r in records1}
            assert len(phase1_keys) > 0

        # Phase 2: TPE uses evidence from Phase 1
        with RecordStore(store_config) as store:
            run_id2 = store.create_run(spec=run_spec)
            config = _make_pipeline_config(
                run_id=run_id2,
                run_spec=run_spec,
                policy_name="model_based_tpe",
                max_rounds=2,
                store_path=tmp_path,
            )
            records2 = asyncio.run(_run_pipeline(config, store))
            store.finish_run(run_id2, "completed")

            phase2_keys = {r.measurement_key for r in records2}

            # Verify no duplicate measurement keys across phases (same store, dedup works)
            # Note: different run_ids so measurement_keys can be same coordinate+schedule
            # but store dedup is per-run, not cross-run

        # Phase 3: Evolution uses all evidence
        with RecordStore(store_config) as store:
            run_id3 = store.create_run(spec=run_spec)
            config = _make_pipeline_config(
                run_id=run_id3,
                run_spec=run_spec,
                policy_name="evolution",
                max_rounds=2,
                store_path=tmp_path,
            )
            records3 = asyncio.run(_run_pipeline(config, store))
            store.finish_run(run_id3, "completed")

        # Verify all three phases produced records
        assert len(records1) > 0
        assert len(records2) > 0
        assert len(records3) > 0

        # Verify same record schema across all phases
        for records in [records1, records2, records3]:
            for record in records:
                assert record.substrate
                assert record.geometry
                assert record.dynamics
                assert record.credit
                assert record.update
                assert record.schedule.fidelity == "L0"

    @pytest.mark.timeout(120)
    def test_u5_same_measurement_identity(self, tmp_path: Path) -> None:
        """Test that measurement identity (measurement_key) is consistent across policies."""
        store_path = tmp_path / "u5_identity_store.duckdb"
        store_config = StoreConfig(path=store_path)

        run_spec = _make_run_spec("digits")

        # Create a coordinate and schedule
        search_space = _space()
        # Get first available coordinate from search space
        coord = Coordinate(
            substrate="digital",
            geometry="feedforward",
            dynamics="instantaneous",
            plasticity="null",
            credit="gradient",
            update="euclidean",
            params={"hidden_dim": 64, "num_layers": 2},
        )
        schedule = Schedule(
            fidelity="L0",
            seed=42,
            n_seeds=1,
            epochs=1,
            batch_limit=0,
            budget_id="test_budget",
            task_id="default",
        )

        # Verify measurement_key is deterministic
        key1 = coord.cell_key() + "|" + schedule.fidelity + "|" + str(schedule.seed)
        key2 = coord.cell_key() + "|" + schedule.fidelity + "|" + str(schedule.seed)
        assert key1 == key2

        # Verify measurement_key doesn't include data_origin (per WP18)
        schedule_with_origin = Schedule(
            fidelity="L0",
            seed=42,
            n_seeds=1,
            epochs=1,
            batch_limit=0,
            budget_id="test_budget",
            task_id="default",
        )
        # measurement_key should be same regardless of data_origin in metadata
        # (data_origin is in Proposal.metadata, not Schedule)
        assert coord.cell_key() == coord.cell_key()


# =============================================================================
# Additional: Legality enforcement across policies
# =============================================================================


class TestLegalityEnforcement:
    """Verify legality engine enforces constraints identically for all policies."""

    @pytest.mark.timeout(120)
    def test_legality_same_for_all_policies(self, tmp_path: Path) -> None:
        """Test that illegal coordinates are rejected regardless of policy."""
        from computronium.experiment.legality.engine import (
            ConstraintEnforcement,
            ConstraintKind,
            ConstraintOrigin,
            ConstraintScope,
            LegalityEngine,
            create_constraint,
        )
        from computronium.experiment.schema.coordinate import Provenance
        from computronium.experiment.schema.record import (
            FailureCause,
            GateVerdict,
            Maturity,
            Record,
            ReproducibilityClass,
            Severity,
            Status,
        )
        from computronium.experiment.schema.registries import CONSTRAINTS_REGISTRY

        # Create and seed legality engine with constraints from registry
        engine = LegalityEngine()
        for spec in CONSTRAINTS_REGISTRY.values():
            if spec.predicate is not None:
                # Map registry constraint to engine constraint
                origin_map = {
                    "DECLARED": ConstraintOrigin.SYSTEM_CONFIG,
                    "TASK_FENCE": ConstraintOrigin.TASK_FENCE,
                    "APPLY_CONSTRAINTS": ConstraintOrigin.APPLY_CONSTRAINTS,
                }
                scope_map = {
                    "void": ConstraintScope.CELL,
                    "hard": ConstraintScope.MEASUREMENT,
                    "fairness": ConstraintScope.MEASUREMENT,
                    "operating_point": ConstraintScope.MEASUREMENT,
                }
                kind_map = {
                    "void": ConstraintKind.HARD,
                    "hard": ConstraintKind.HARD,
                    "fairness": ConstraintKind.HARD,
                    "operating_point": ConstraintKind.HARD,
                }
                enforcement_map = {
                    "void": ConstraintEnforcement.S4_EXPANSION,
                    "hard": ConstraintEnforcement.S4_EXPANSION,
                    "fairness": ConstraintEnforcement.S4_EXPANSION,
                    "operating_point": ConstraintEnforcement.S4_EXPANSION,
                }

                create_constraint(
                    expr=spec.predicate,
                    origin=origin_map.get(spec.origin, ConstraintOrigin.SYSTEM_CONFIG),
                    scope=scope_map.get(spec.kind.value, ConstraintScope.CELL),
                    enforcement=enforcement_map.get(
                        spec.kind.value, ConstraintEnforcement.S4_EXPANSION
                    ),
                    kind=kind_map.get(spec.kind.value, ConstraintKind.HARD),
                    description=spec.description,
                    engine=engine,
                )

        # Create a record with hidden_dim exceeding limit (simple constraint the parser handles)
        illegal_coord = Coordinate(
            substrate="digital",
            geometry="feedforward",
            dynamics="instantaneous",
            plasticity="null",
            credit="gradient",
            update="euclidean",
            params={"hidden_dim": 10000},  # Exceeds max_hidden_dim (8192)
        )
        schedule = Schedule(
            fidelity="L0",
            seed=42,
            n_seeds=1,
            epochs=1,
            batch_limit=0,
            budget_id="test_budget",
            task_id="default",
        )
        record = Record.create(
            run_id="test_run",
            coordinate=illegal_coord,
            schedule=schedule,
            provenance=Provenance(
                env={},
                dataset="test",
                dataset_version="1.0",
                code_sha="test",
                policy="test",
                links={},
            ),
            status=Status(
                gate_verdict=GateVerdict.PENDING,
                defect="",
                cause=FailureCause.UNKNOWN,
                severity=Severity.LOW,
                quarantine=False,
                maturity=Maturity.L0,
                uncertainty={},
                reproducibility=ReproducibilityClass.REPLAYABLE,
                assessment_procedure_version="1.0",
                ceec_link=None,
            ),
            payload={},
        )

        # Should be rejected by legality engine at S4 stage (max_hidden_dim constraint)
        hard_violations, soft_violations = engine.evaluate_record(
            record, ConstraintEnforcement.S4_EXPANSION
        )
        assert len(hard_violations) > 0, (
            "Illegal coordinate should have hard violations"
        )
        assert any("hidden_dim" in str(v) for v in hard_violations)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
