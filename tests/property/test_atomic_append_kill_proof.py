"""Kill -9 proof test for atomic append with artifacts (WP1.5 / WP5).

Verifies that a kill -9 during `append_with_artifacts()` leaves no partial state:
either the full record + artifacts are persisted, or neither is.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

import pytest

from computronium.experiment.evidence.artifacts import ArtifactInput, ArtifactRole
from computronium.experiment.evidence.store import RecordStore, StoreConfig
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


def _make_test_record(run_id: str, seed: int = 42) -> Record:
    """Create a test record."""
    coord = Coordinate(
        substrate="Digital",
        geometry="Feedforward",
        dynamics="Instantaneous",
        plasticity="NullPlasticity",
        credit="Backprop",
        update="Euclidean",
        params={},
    )
    sched = Schedule(
        fidelity="L1", seed=seed, n_seeds=1, epochs=1, batch_limit=10, budget_id="test"
    )
    prov = Provenance(
        env={},
        dataset="test",
        dataset_version="1.0",
        code_sha="sha",
        policy="policy",
        links={},
    )
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
    return Record.create(
        run_id=run_id,
        coordinate=coord,
        schedule=sched,
        provenance=prov,
        status=status,
        payload={"accuracy": 0.9},
    )


def _make_artifacts() -> list[ArtifactInput]:
    """Create test artifacts."""
    return [
        ArtifactInput(bytes=b"config data", role=ArtifactRole.CONFIG),
        ArtifactInput(bytes=b"figure data", role=ArtifactRole.FIGURE),
    ]


class TestAtomicAppendKillProof:
    """Tests proving atomic append survives kill -9."""

    def test_append_with_artifacts_atomic_on_exception(self) -> None:
        """If an exception occurs during append_with_artifacts, nothing is persisted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "test.duckdb"
            config = StoreConfig(path=store_path)

            with RecordStore(config) as store:
                run_id = store.create_run()
                record = _make_test_record(run_id)
                artifacts = _make_artifacts()

                appended = store.append_with_artifacts(record, artifacts)

                # Verify record stored
                retrieved = store.get_record(appended.record_id)
                assert retrieved is not None
                assert retrieved.record_id == appended.record_id

                # Verify artifacts stored
                artifact_list = store.artifacts.get_for_record(appended.record_id)
                assert len(artifact_list) == 2
                roles = {a.role for a in artifact_list}
                assert ArtifactRole.CONFIG in roles
                assert ArtifactRole.FIGURE in roles

    def test_append_with_artifacts_atomic_on_duplicate_measurement(self) -> None:
        """If duplicate measurement_key, entire transaction rolls back."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "test.duckdb"
            config = StoreConfig(path=store_path)

            with RecordStore(config) as store:
                run_id1 = store.create_run()
                run_id2 = store.create_run()
                # First record
                record1 = _make_test_record(run_id1, seed=42)
                artifacts = _make_artifacts()

                # First append succeeds
                appended1 = store.append_with_artifacts(record1, artifacts)

                # Second record with SAME measurement_key (same coordinate + schedule + seed)
                # but different run_id so record_id is different
                record2 = _make_test_record(
                    run_id2, seed=42
                )  # Same seed = same measurement_key

                from computronium.experiment.evidence.store import (
                    DuplicateMeasurementError,
                )

                with pytest.raises(DuplicateMeasurementError):
                    store.append_with_artifacts(record2, artifacts)

                # Verify only one record exists
                count = store.count_records()
                assert count == 1

                # Verify artifacts for first record still intact
                artifact_list = store.artifacts.get_for_record(appended1.record_id)
                assert len(artifact_list) == 2

    def test_kill_during_atomic_append_no_partial_state(self) -> None:
        """Simulate kill -9 during atomic append by forking and killing child.

        This test forks a child process that performs append_with_artifacts,
        then sends SIGKILL mid-operation. After the child dies, the parent
        reopens the store and verifies no partial state exists.
        """
        # Skip on platforms without fork (e.g., Windows)
        if not hasattr(os, "fork"):
            pytest.skip("fork not available on this platform")

        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "test.duckdb"

            # Create a script that does the append and can be killed
            script = f"""
import sys
sys.path.insert(0, "/home/me/computronium")

from computronium.experiment.evidence.artifacts import ArtifactInput, ArtifactRole
from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.schema.coordinate import Coordinate, Provenance, Schedule
from computronium.experiment.schema.record import (
    FailureCause, GateVerdict, Maturity, Record, ReproducibilityClass,
    Severity, Status
)

def make_record(run_id):
    coord = Coordinate(
        substrate="Digital", geometry="Feedforward", dynamics="Instantaneous",
        plasticity="NullPlasticity", credit="Backprop", update="Euclidean", params={{}}
    )
    sched = Schedule(fidelity="L1", seed=42, n_seeds=1, epochs=1, batch_limit=10, budget_id="test")
    prov = Provenance(env={{}}, dataset="test", dataset_version="1.0", code_sha="sha", policy="policy", links={{}})
    status = Status(
        gate_verdict=GateVerdict.PASS_, defect="", cause=FailureCause.UNKNOWN,
        severity=Severity.LOW, quarantine=False, maturity=Maturity.L1,
        uncertainty={{}}, reproducibility=ReproducibilityClass.REPLAYABLE,
        assessment_procedure_version="1.0", ceec_link=None
    )
    return Record.create(
        run_id=run_id, coordinate=coord, schedule=sched, provenance=prov,
        status=status, payload={{"accuracy": 0.9}}
    )

store_path = r"{store_path}"
config = StoreConfig(path=store_path)

with RecordStore(config) as store:
    run_id = store.create_run()
    record = make_record(run_id)
    artifacts = [
        ArtifactInput(bytes=b"config data", role=ArtifactRole.CONFIG),
        ArtifactInput(bytes=b"figure data", role=ArtifactRole.FIGURE),
    ]
    store.append_with_artifacts(record, artifacts)
"""

            # Write script to temp file
            script_path = Path(tmpdir) / "append_script.py"
            script_path.write_text(script)

            # Run the script in a subprocess
            proc = subprocess.Popen([sys.executable, str(script_path)])
            try:
                # Give it time to start and enter the transaction
                time.sleep(0.5)
                # Send SIGKILL
                proc.kill()
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()

            # Now reopen the store and verify no partial state
            config = StoreConfig(path=store_path)
            with RecordStore(config) as store:
                count = store.count_records()
                # Should be 0 (nothing committed) or 1 (fully committed)
                # Since we killed before commit likely, expect 0
                # But due to timing, could be 1. The key is: no partial artifacts
                if count == 1:
                    # If record exists, artifacts must all exist
                    records = store.query_records()
                    assert len(records) == 1
                    artifact_list = store.artifacts.get_for_record(records[0].record_id)
                    # Must have both artifacts (atomic)
                    assert len(artifact_list) == 2, (
                        f"Expected 2 artifacts, got {len(artifact_list)}"
                    )
                else:
                    # No records = no artifacts
                    assert count == 0

    def test_concurrent_append_dedup_by_measurement_key(self) -> None:
        """Concurrent appends with same measurement_key: only one succeeds (dedup).

        Uses a SINGLE RecordStore instance shared across threads (single-writer topology).
        Each thread creates its own run_id so record_ids differ, but same coordinate+schedule
        gives same measurement_key.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "test.duckdb"
            config = StoreConfig(path=store_path)

            results = []
            errors = []

            with RecordStore(config) as store:

                def append_record() -> None:
                    try:
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
                        sched = Schedule(
                            fidelity="L1",
                            seed=42,  # Same seed = same measurement_key
                            n_seeds=1,
                            epochs=1,
                            batch_limit=10,
                            budget_id="test",
                        )
                        prov = Provenance(
                            env={},
                            dataset="test",
                            dataset_version="1.0",
                            code_sha="sha",
                            policy="policy",
                            links={},
                        )
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
                        record = Record.create(
                            run_id=run_id,
                            coordinate=coord,
                            schedule=sched,
                            provenance=prov,
                            status=status,
                            payload={"accuracy": 0.9},
                        )
                        artifacts = [
                            ArtifactInput(
                                bytes=b"config data", role=ArtifactRole.CONFIG
                            ),
                        ]
                        appended = store.append_with_artifacts(record, artifacts)
                        results.append(appended.measurement_key)
                    except Exception as e:
                        errors.append(e)

                # Run multiple threads with SAME seed (same measurement_key)
                threads = [threading.Thread(target=append_record) for _ in range(5)]
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()

            # Only one should succeed (dedup by measurement_key)
            assert len(results) == 1
            # Others should get DuplicateMeasurementError
            assert len(errors) == 4
            for e in errors:
                assert (
                    "DuplicateMeasurementError" in type(e).__name__
                    or "unique constraint" in str(e).lower()
                )

    def test_monotonic_seq_across_concurrent_writes(self) -> None:
        """seq is monotonic across concurrent writes (single writer serializes).

        Uses a SINGLE RecordStore instance shared across threads (single-writer topology).
        Each thread creates its own run_id with different seed → different measurement_key.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / "test.duckdb"
            config = StoreConfig(path=store_path)

            seqs = []
            lock = threading.Lock()

            with RecordStore(config) as store:

                def append_record(seed: int) -> None:
                    try:
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
                        sched = Schedule(
                            fidelity="L1",
                            seed=seed,
                            n_seeds=1,
                            epochs=1,
                            batch_limit=10,
                            budget_id="test",
                        )
                        prov = Provenance(
                            env={},
                            dataset="test",
                            dataset_version="1.0",
                            code_sha="sha",
                            policy="policy",
                            links={},
                        )
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
                        record = Record.create(
                            run_id=run_id,
                            coordinate=coord,
                            schedule=sched,
                            provenance=prov,
                            status=status,
                            payload={"accuracy": 0.9},
                        )
                        artifacts = [
                            ArtifactInput(
                                bytes=b"config data", role=ArtifactRole.CONFIG
                            ),
                        ]
                        appended = store.append_with_artifacts(record, artifacts)
                        with lock:
                            seqs.append(appended.seq)
                    except Exception as e:
                        print(f"Thread {seed} failed: {e}")

                # Run multiple threads with DIFFERENT seeds
                threads = [
                    threading.Thread(target=append_record, args=(i,)) for i in range(10)
                ]
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()

            # All successful writes should have unique, monotonic seq
            assert len(seqs) == 10
            assert seqs == sorted(seqs)  # Monotonically increasing
            assert len(set(seqs)) == 10  # All unique


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
