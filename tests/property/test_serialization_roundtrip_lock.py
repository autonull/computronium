"""Serialization round-trip lock (WP13 E1).

DuckDB sections survive write/read verbatim; `unknown` is preserved
exactly; unknown schema versions fail closed at both the store read path
and the versioned-reader registry (Directive 2). Schedule `task_id`
(L17) persists so cross-task identity survives the round trip.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from computronium.experiment.evidence.store import (
    RecordStore,
    StoreConfig,
    UnsupportedSchemaVersionError,
)
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
from computronium.experiment.schema.versioning import SCHEMA_REGISTRY


def _make_record(
    run_id: str,
    seed: int = 7,
    task_id: str = "task-alpha",
    unknown: dict | None = None,
) -> Record:
    coord = Coordinate(
        substrate="Digital",
        geometry="Feedforward",
        dynamics="Instantaneous",
        plasticity="NullPlasticity",
        credit="Backprop",
        update="Euclidean",
        params={"step_size": 0.01, "depth": 3},
    )
    sched = Schedule(
        fidelity="L2",
        seed=seed,
        n_seeds=5,
        epochs=4,
        batch_limit=100,
        budget_id="bench",
        task_id=task_id,
    )
    prov = Provenance(
        env={"arch": "cpu"},
        dataset="synthetic",
        dataset_version="2.0",
        code_sha="abc123",
        policy="RoundRobinGrid",
        links={},
    )
    status = Status(
        gate_verdict=GateVerdict.PASS_,
        defect="",
        cause=FailureCause.UNKNOWN,
        severity=Severity.LOW,
        quarantine=False,
        maturity=Maturity.L2,
        uncertainty={"ci": [0.8, 0.95]},
        reproducibility=ReproducibilityClass.COMPUTATIONALLY_REPRODUCIBLE,
        assessment_procedure_version="1.0",
        ceec_link=None,
    )
    return Record.create(
        run_id=run_id,
        coordinate=coord,
        schedule=sched,
        provenance=prov,
        status=status,
        payload={"accuracy": 0.91, "curve": [0.5, 0.7, 0.91]},
        unknown=unknown,
    )


def _open_store(tmpdir: str) -> RecordStore:
    store = RecordStore(StoreConfig(path=Path(tmpdir) / "roundtrip.duckdb"))
    store.__enter__()
    store.create_run("run-rt", spec_version=1)
    return store


class TestSerializationRoundTrip:
    def test_schedule_task_id_round_trips(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = _open_store(tmpdir)
            with store:
                rec = _make_record("run-rt", task_id="task-alpha")
                stored = store.append(rec)
                fetched = store.get_record(stored.record_id)
                assert fetched is not None
                assert fetched.schedule.task_id == "task-alpha"
                assert fetched.schedule.fidelity == "L2"
                assert fetched.schedule.seed == 7
                assert fetched.schedule.n_seeds == 5

    def test_cross_task_keys_distinct_and_persisted(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = _open_store(tmpdir)
            with store:
                a = store.append(_make_record("run-rt", seed=1, task_id="task-a"))
                b = store.append(_make_record("run-rt", seed=1, task_id="task-b"))
                assert a.measurement_key != b.measurement_key
                assert store.get_record(a.record_id) is not None
                assert store.get_record(b.record_id) is not None
                assert (
                    store.get_record(a.record_id).schedule.task_id == "task-a"  # type: ignore[union-attr]
                )
                assert (
                    store.get_record(b.record_id).schedule.task_id == "task-b"  # type: ignore[union-attr]
                )

    def test_unknown_preserved_verbatim(self) -> None:
        unknown = {
            "future_flag": True,
            "nested": {"levels": [1, 2, {"deep": "valué ✓"}]},
            "score": 3.14159,
            "nothing": None,
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            store = _open_store(tmpdir)
            with store:
                stored = store.append(_make_record("run-rt", unknown=unknown))
                fetched = store.get_record(stored.record_id)
                assert fetched is not None
                assert fetched.unknown == unknown

    def test_none_unknown_round_trips(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = _open_store(tmpdir)
            with store:
                stored = store.append(_make_record("run-rt", unknown=None))
                fetched = store.get_record(stored.record_id)
                assert fetched is not None
                assert fetched.unknown is None

    def test_params_payload_provenance_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = _open_store(tmpdir)
            with store:
                rec = _make_record("run-rt")
                stored = store.append(rec)
                fetched = store.get_record(stored.record_id)
                assert fetched is not None
                assert fetched.params == {"step_size": 0.01, "depth": 3}
                assert fetched.payload == {"accuracy": 0.91, "curve": [0.5, 0.7, 0.91]}
                assert fetched.provenance.dataset == "synthetic"
                assert fetched.status.assessment_procedure_version == "1.0"

    def test_store_read_fails_closed_on_unknown_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = _open_store(tmpdir)
            with store:
                stored = store.append(_make_record("run-rt"))
                assert store._conn is not None
                store._conn.execute(
                    "UPDATE records SET schema_version = 999 WHERE record_id = ?",
                    [stored.record_id],
                )
                with pytest.raises(UnsupportedSchemaVersionError):
                    store.get_record(stored.record_id)

    def test_registry_read_fails_closed_on_unknown_version(self) -> None:
        rec = _make_record("run-rt")
        data = rec.to_dict()
        data["schema_version"] = 999
        with pytest.raises(ValueError, match="999"):
            SCHEMA_REGISTRY.read_record(data)

    def test_registry_reads_known_version(self) -> None:
        rec = _make_record("run-rt")
        data = rec.to_dict()
        data["schema_version"] = 1
        back = SCHEMA_REGISTRY.read_record(data)
        assert back.record_id == rec.record_id
