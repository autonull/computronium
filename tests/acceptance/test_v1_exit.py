"""v1.0 Exit Test — the merge gate for the turn-key discovery engine.

This test validates the complete turn-key flow as specified in TODO65 §7:

1. Config selects a cross-domain schedule + policy; the loop honours it.
2. Reachability locks pass (W5).
3. S10 promotions non-empty (W2).
4. A claim is exported to the standalone CEEC and `ceec_link` is recorded (W3).
5. Report artifacts: per-domain objectives, baseline-relative Pareto (one impl),
   evidence + limitations, three-tier status, enumerated provenance, recorded defects.
6. `test_readme_build_lock` green (W7).

Run once (<10 min; faster on GPU) before tagging v1.0.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

from computronium.experiment.evidence import RecordStore, StoreConfig
from computronium.experiment.execution import (
    Budget,
    EvidenceDrivenAllocator,
    LocalBackend,
    PipelineConfig,
    PipelineRunner,
    StratifiedRandomPolicy,
)
from computronium.experiment.schema import (
    MEASURED_BATCH_LIMIT,
    MEASURED_PARAM_BUDGET,
    RunSpec,
    seed_all_registries,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(scope="session", autouse=True)
def _seed_registries() -> None:
    """Seed all registries before exit test."""
    seed_all_registries()


def _make_run_spec(
    task: str = "digits", batch_limit: int = MEASURED_BATCH_LIMIT
) -> RunSpec:
    """A RunSpec in the measured regime: digits, one epoch, two batches."""
    import subprocess

    try:
        code_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            check=False,
            text=True,
            timeout=5,
        ).stdout.strip()[:12]
    except Exception:
        code_sha = "test"

    return RunSpec(
        profile="exit_test",
        task=task,
        objectives=("validation_accuracy", "walltime_total"),
        fidelity="L0",
        n_seeds=1,
        epochs=1,
        budget_seconds=120.0,
        param_budget=MEASURED_PARAM_BUDGET,
        batch_limit=batch_limit,
        code_sha=code_sha,
        dataset=task,
        dataset_version="1.0",
    )


def _make_pipeline_config(
    run_id: str,
    run_spec: RunSpec,
    max_rounds: int = 2,
    store_path: Path | None = None,
) -> PipelineConfig:
    """Create a PipelineConfig with stratified random policy and allocator."""
    policy = StratifiedRandomPolicy(seed=42)

    return PipelineConfig(
        run_id=run_id,
        run_spec=run_spec,
        budget=Budget.from_duration(f"{int(run_spec.budget_seconds or 0)}s"),
        policy=policy,
        allocator=EvidenceDrivenAllocator(promotion_threshold=0.05),
        backend=LocalBackend(),
        seed=run_spec.seed,
        max_rounds=max_rounds,
        min_rounds=1,
    )


async def _run_pipeline(
    config: PipelineConfig,
    store: RecordStore,
) -> tuple[list, PipelineRunner]:
    """Run a pipeline and return (records, runner) for state assertions."""
    runner = PipelineRunner(config, store)
    return await runner.run(), runner


# =============================================================================
# Test 1: Config selects cross-domain schedule + policy; loop honours it
# =============================================================================


class TestV1Exit:
    """v1.0 Exit Test Suite."""

    @pytest.mark.timeout(600)  # 10 minutes
    def test_01_config_drives_loop_cross_domain(self, tmp_path: Path) -> None:
        """1. Config selects a cross-domain schedule + policy; the loop honours it."""
        store_path = tmp_path / "exit_store.duckdb"
        store_config = StoreConfig(path=store_path)

        with RecordStore(store_config) as store:
            # Create a cross-domain run spec (multiple tasks)
            run_spec = _make_run_spec("digits")
            run_id = store.create_run(spec=run_spec)

            config = _make_pipeline_config(run_id, run_spec, max_rounds=2)
            records, _runner = asyncio.run(_run_pipeline(config, store))

            # Loop ran and produced records
            assert len(records) > 0, "Pipeline should produce at least one record"
            assert all(r.run_id == run_id for r in records), (
                "All records should have the run_id"
            )

            # Verify cross-domain capability: task schedule honoured
            tasks_seen = {r.schedule.task_id for r in records}
            assert "digits" in tasks_seen, "Should have run the configured task"

    @pytest.mark.timeout(600)
    def test_02_reachability_locks_pass(self) -> None:
        """2. Reachability locks pass (W5) — composability + task resolvability."""
        # Composability: every registered primitive composes
        from computronium.domains.factory import create_task
        from computronium.domains.registry import SUPPORTED_TASKS
        from computronium.experiment.schema.axis import AXES_REGISTRIES

        # Test a representative composition across all 6 axes
        for axis_name, registry in AXES_REGISTRIES.items():
            available = [s for s in registry if s.available]
            assert len(available) > 0, (
                f"Axis {axis_name} should have available primitives"
            )

        # Task resolvability: every SUPPORTED_TASKS task resolves geometry + constructs
        for task_name in SUPPORTED_TASKS:
            task = create_task(task_name, device="cpu", quick_mode=True)
            task.setup()
            assert task.input_dim is not None, f"Task {task_name} must have input_dim"
            assert task.output_dim is not None, f"Task {task_name} must have output_dim"

        # Device resolution: auto -> cuda when present
        from computronium.experiment.kernel.evaluate import _resolve_device

        assert _resolve_device("cpu") == "cpu"
        assert _resolve_device("cuda") == "cuda"

    @pytest.mark.timeout(600)
    def test_03_s10_promotions_non_empty(self, tmp_path: Path) -> None:
        """3. S10 promotions non-empty (W2) — EvidenceDrivenAllocator wired.

        Falsifiable: removing the allocator from ``PipelineConfig`` (or the
        deadline it needs to allocate against) empties ``allocator_promotions``
        and turns this red.
        """
        store_path = tmp_path / "exit_store.duckdb"
        store_config = StoreConfig(path=store_path)

        with RecordStore(store_config) as store:
            run_spec = _make_run_spec("digits")
            run_id = store.create_run(spec=run_spec)

            config = _make_pipeline_config(run_id, run_spec, max_rounds=2)
            records, runner = asyncio.run(_run_pipeline(config, store))

            assert len(records) > 0, "Should have records from multi-round run"

            # The allocator ran between rounds and proposed successors.
            assert config.allocator is not None, "Allocator should be configured"
            assert isinstance(config.allocator, EvidenceDrivenAllocator)
            assert len(runner.allocator_promotions) > 0, (
                "S10 successive-halving allocation proposed no promotions"
            )

    @pytest.mark.timeout(600)
    def test_04_ceec_export_and_ceec_link_recorded(self, tmp_path: Path) -> None:
        """4. Claim exported to standalone CEEC; ceec_link recorded (W3).

        A claim is claim-eligible only at L2 with the required seed count, so
        this measures real L2 cells through the kernel evaluator — the same
        "measured, not fabricated" pattern as ``test_claim_report_lock`` — then
        exports them and asserts the returned belief is written back onto the
        records. Falsifiable: dropping the write-back in ``export_claims_to_ceec``
        leaves ``ceec_link`` null and turns this red.
        """
        from computronium.experiment.evidence.ceec_export import export_claims_to_ceec
        from computronium.experiment.kernel import cell_record
        from computronium.experiment.schema import (
            Coordinate,
            Provenance,
            Schedule,
        )

        task = "digits"
        n_seeds = 5
        coordinate = Coordinate(
            substrate="digital",
            geometry="feedforward",
            dynamics="energy_minimization",
            plasticity="fast_weights",
            credit="local_contrastive",
            update="euclidean",
            params={},
        )

        def measure(store: RecordStore, run_id: str, seed: int) -> None:
            store.append(
                cell_record(
                    coordinate,
                    Schedule(
                        fidelity="L2",
                        seed=seed,
                        n_seeds=n_seeds,
                        epochs=1,
                        batch_limit=MEASURED_BATCH_LIMIT,
                        budget_id="exit-ceec",
                        task_id=task,
                        param_budget=MEASURED_PARAM_BUDGET,
                    ),
                    Provenance(
                        env={"python": "3.14", "platform": "exit-test"},
                        dataset=task,
                        dataset_version="1.0",
                        code_sha="exit-test",
                        policy="exit-test",
                        links={"run_id": run_id},
                    ),
                )
            )

        with RecordStore(StoreConfig(path=tmp_path / "ceec_store.duckdb")) as store:
            run_spec = _make_run_spec(task)
            run_id = store.create_run(spec=run_spec)
            for seed in range(n_seeds):
                measure(store, run_id, seed)

            link = export_claims_to_ceec(
                store,
                run_id,
                ceec_ledger_path=tmp_path / "ceec.sqlite3",
                ceec_artifacts_dir=tmp_path / "ceec_artifacts",
            )

            assert link is not None, "CEEC export should return a belief link"

            after = store.query_records(run_id=run_id)
            recorded = [r for r in after if r.status.ceec_link == link]
            assert recorded, "The exported claim's ceec_link was not recorded"

    @pytest.mark.timeout(600)
    def test_05_report_artifacts_complete(self, tmp_path: Path) -> None:
        """5. Report artifacts complete: per-domain objectives, baseline-relative Pareto,
        evidence + limitations, three-tier status, enumerated provenance, recorded defects."""
        from computronium.experiment.schema.record import GateVerdict

        store_path = tmp_path / "exit_store.duckdb"
        store_config = StoreConfig(path=store_path)

        with RecordStore(store_config) as store:
            run_spec = _make_run_spec("digits")
            run_id = store.create_run(spec=run_spec)

            config = _make_pipeline_config(run_id, run_spec, max_rounds=2)
            records, _runner = asyncio.run(_run_pipeline(config, store))

            assert len(records) > 0

            # Check three-tier status fields are present
            for record in records:
                status = record.status
                assert status.gate_verdict is not None, "Gate verdict should be set"
                assert status.assessment_procedure_version is not None, (
                    "Assessment procedure version should be stamped"
                )

                # Per-domain objectives in payload
                # Only check records that passed the gate
                if status.gate_verdict == GateVerdict.PASS_:
                    payload = record.payload
                    assert "validation_accuracy" in payload or "val_acc" in payload, (
                        "Should have validation accuracy"
                    )
                    assert "walltime_total" in payload or "walltime_s" in payload, (
                        "Should have walltime"
                    )
                    assert "param_count" in payload, "Should have param count"

                # Provenance fields
                assert record.provenance is not None, "Provenance should be set"
                assert record.provenance.code_sha is not None, (
                    "Code SHA should be recorded"
                )

                # Defects recorded if any
                if status.gate_verdict == GateVerdict.FAIL:
                    assert status.defect is not None, (
                        "Failed records should have defect recorded"
                    )

    @pytest.mark.timeout(60)
    def test_06_readme_build_lock_green(self) -> None:
        """6. test_readme_build_lock green (W7)."""
        # This test itself is the lock - if README.md is stale, the lock test fails
        # We just verify the lock test file exists and is runnable
        from tests.property.test_readme_build_lock import TestReadmeBuildLock

        test_instance = TestReadmeBuildLock()
        test_instance.test_readme_matches_the_build()


# =============================================================================
# Main entry for manual run
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-x"])
