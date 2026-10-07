"""Schema forward-tolerance lock (TODO44 D4).

Proves two invariants of the RecordStore schema contract (Directive 2:
fail-closed + forward tolerance):

1. A record written under an older schema version carrying fields the
   current schema does not model survives a version bump verbatim via the
   ``unknown`` JSON column.
2. Records stamped with an unsupported (future/foreign) schema version are
   rejected fail-closed by :class:`UnsupportedSchemaVersionError`, never
   silently reinterpreted.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from computronium.experiment.evidence import (
    RecordStore,
    StoreConfig,
    UnsupportedSchemaVersionError,
)
from computronium.experiment.schema import (
    Coordinate,
    FailureCause,
    GateVerdict,
    Maturity,
    Provenance,
    Record,
    ReproducibilityClass,
    Schedule,
    Severity,
    Status,
)


def _make_record(
    run_id: str, unknown: dict[str, object] | None = None, schema_version: int = 3
) -> Record:
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
        fidelity="L1", seed=42, n_seeds=1, epochs=1, batch_limit=10, budget_id="test"
    )
    prov = Provenance(
        env={},
        dataset="test",
        dataset_version="1.0",
        code_sha="sha",
        policy="p",
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
        unknown=unknown,
        schema_version=schema_version,
    )


def _store(tmpdir: str) -> RecordStore:
    return RecordStore(StoreConfig(path=Path(tmpdir) / "test.duckdb"))


class TestSchemaForwardTolerance:
    def test_unknown_fields_survive_version_bump(self) -> None:
        """v2 record with extra fields → read under the current (v3) schema → verbatim."""
        legacy_fields = {"legacy_metric": 1.25, "legacy_tags": ["a", "b"]}
        with tempfile.TemporaryDirectory() as tmpdir:
            with _store(tmpdir) as store:
                run_id = store.create_run()
                appended = store.append(
                    _make_record(run_id, unknown=legacy_fields, schema_version=2)
                )
                assert appended.schema_version == 2

            with _store(tmpdir) as reopened:
                assert reopened._SCHEMA_VERSION == 3
                with pytest.MonkeyPatch.context() as mp:
                    mp.setattr(
                        RecordStore, "SUPPORTED_SCHEMA_VERSIONS", frozenset({2, 3})
                    )
                    loaded = reopened.get_record(appended.record_id)
                assert loaded is not None
                assert loaded.schema_version == 2
                assert loaded.unknown == legacy_fields

    def test_unknown_survives_round_trip_when_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with _store(tmpdir) as store:
                run_id = store.create_run()
                appended = store.append(_make_record(run_id))
                loaded = store.get_record(appended.record_id)
            assert loaded is not None
            assert loaded.unknown is None

    def test_unsupported_schema_version_fails_closed(self) -> None:
        """A row stamped with a foreign schema_version raises, never misparses."""
        with tempfile.TemporaryDirectory() as tmpdir, _store(tmpdir) as store:
            run_id = store.create_run()
            appended = store.append(_make_record(run_id))
            conn = store._conn
            assert conn is not None
            conn.execute(
                "UPDATE records SET schema_version = 99 WHERE record_id = ?",
                [appended.record_id],
            )
            with pytest.raises(UnsupportedSchemaVersionError):
                store.get_record(appended.record_id)
