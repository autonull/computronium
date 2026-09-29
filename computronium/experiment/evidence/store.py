"""DuckDB-backed record store for experiment evidence."""

from __future__ import annotations

import json
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Self

import duckdb

from computronium.experiment.schema.coordinate import (
    Provenance,
    Schedule,
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

if TYPE_CHECKING:
    from pathlib import Path


class DuplicateMeasurementError(Exception):
    """Raised when a measurement_key already exists (UNIQUE constraint violation)."""

    def __init__(self, measurement_key: str) -> None:
        self.measurement_key = measurement_key
        super().__init__(f"Duplicate measurement_key: {measurement_key}")


class StoreError(Exception):
    """Base exception for store errors."""


@dataclass(frozen=True, slots=True)
class StoreConfig:
    """Configuration for RecordStore."""

    path: Path
    read_only: bool = False


class RecordStore:
    """DuckDB-backed record store with single-writer guarantee.

    All writes flow through a single instance guarded by a threading.Lock.
    DuckDB allows one writer process; this design concentrates writes
    in the orchestrating process.
    """

    _SCHEMA_VERSION = 1

    def __init__(self, config: StoreConfig) -> None:
        self._config = config
        self._conn: duckdb.DuckDBPyConnection | None = None
        self._write_lock = threading.Lock()
        self._initialized = False

    def __enter__(self) -> Self:
        self._conn = duckdb.connect(
            str(self._config.path), read_only=self._config.read_only
        )
        if not self._initialized and not self._config.read_only:
            self._init_schema()
            self._initialized = True
        return self

    def __exit__(
        self,
        exc_type: object,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        if self._conn is not None:
            if not self._config.read_only:
                self._conn.execute("CHECKPOINT")
            self._conn.close()
            self._conn = None

    def _init_schema(self) -> None:
        """Initialize the database schema."""
        if self._conn is None:
            raise StoreError("Connection not initialized")
        # Create sequence for write ordering
        self._conn.execute("CREATE SEQUENCE IF NOT EXISTS record_seq")

        # Runs table
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                run_id            TEXT PRIMARY KEY,
                spec              JSON,
                spec_version      INTEGER NOT NULL,
                status            TEXT NOT NULL,
                budget_consumed_s DOUBLE,
                replay_hash       TEXT,
                started_at        TIMESTAMP NOT NULL,
                finished_at       TIMESTAMP
            )
        """)

        # Records table
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS records (
                record_id       TEXT PRIMARY KEY,
                seq             BIGINT UNIQUE DEFAULT nextval('record_seq'),
                run_id          TEXT NOT NULL REFERENCES runs(run_id),
                schema_version  INTEGER NOT NULL,
                cell_key        TEXT NOT NULL,
                measurement_key TEXT NOT NULL UNIQUE,
                substrate       TEXT NOT NULL,
                geometry        TEXT NOT NULL,
                dynamics        TEXT NOT NULL,
                plasticity      TEXT NOT NULL,
                credit          TEXT NOT NULL,
                update          TEXT NOT NULL,
                params          JSON NOT NULL,
                schedule        STRUCT(fidelity TEXT, seed INTEGER, n_seeds INTEGER,
                                       epochs INTEGER, batch_limit INTEGER, budget_id TEXT) NOT NULL,
                provenance      JSON NOT NULL,
                status          STRUCT(gate_verdict TEXT, defect TEXT, cause TEXT, severity TEXT,
                                       quarantine BOOLEAN, maturity TEXT, uncertainty JSON,
                                       reproducibility TEXT, assessment_procedure_version TEXT,
                                       ceec_link TEXT) NOT NULL,
                payload         JSON NOT NULL,
                unknown         JSON
            )
        """)

        # Record artifacts table (bytes live in ceec-core)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS record_artifacts (
                record_id TEXT NOT NULL REFERENCES records(record_id),
                digest    TEXT NOT NULL,
                role      TEXT NOT NULL,
                PRIMARY KEY (record_id, digest, role)
            )
        """)

        # Vector index table
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS vector_index (
                record_id        TEXT PRIMARY KEY REFERENCES records(record_id),
                embedding        FLOAT[384] NOT NULL,
                embedding_version INTEGER NOT NULL
            )
        """)

        # Indexes for common query patterns
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_records_run_id ON records(run_id)"
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_records_cell_key ON records(cell_key)"
        )

    def create_run(
        self,
        run_id: str | None = None,
        spec: dict[str, Any] | None = None,
        spec_version: int = 1,
    ) -> str:
        """Create a new run and return its run_id."""
        if self._conn is None:
            raise StoreError("Connection not initialized")
        if run_id is None:
            run_id = str(uuid.uuid4())
        with self._write_lock:
            self._conn.execute(
                """
                INSERT INTO runs (run_id, spec, spec_version, status, started_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    run_id,
                    json.dumps(spec) if spec else None,
                    spec_version,
                    "running",
                    datetime.now(),
                ],
            )
        return run_id

    def finish_run(
        self,
        run_id: str,
        status: str,
        budget_consumed_s: float | None = None,
        replay_hash: str | None = None,
    ) -> None:
        """Mark a run as finished."""
        if self._conn is None:
            raise StoreError("Connection not initialized")
        with self._write_lock:
            self._conn.execute(
                """
                UPDATE runs SET status = ?, budget_consumed_s = ?, replay_hash = ?, finished_at = ?
                WHERE run_id = ?
                """,
                [status, budget_consumed_s, replay_hash, datetime.now(), run_id],
            )

    def append(self, record: Record) -> Record:
        """Append a record to the store. Returns record with assigned seq.

        Raises DuplicateMeasurementError if measurement_key already exists.
        """
        if self._conn is None:
            raise StoreError("Connection not initialized")

        with self._write_lock:
            try:
                # Insert record - seq is assigned by DEFAULT nextval('record_seq')
                self._conn.execute(
                    """
                    INSERT INTO records (
                        record_id, run_id, schema_version, cell_key, measurement_key,
                        substrate, geometry, dynamics, plasticity, credit, update,
                        params, schedule, provenance, status, payload, unknown
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        record.record_id,
                        record.run_id,
                        record.schema_version,
                        record.cell_key,
                        record.measurement_key,
                        record.substrate,
                        record.geometry,
                        record.dynamics,
                        record.plasticity,
                        record.credit,
                        record.update,
                        json.dumps(record.params),
                        {
                            "fidelity": record.schedule.fidelity,
                            "seed": record.schedule.seed,
                            "n_seeds": record.schedule.n_seeds,
                            "epochs": record.schedule.epochs,
                            "batch_limit": record.schedule.batch_limit,
                            "budget_id": record.schedule.budget_id,
                        },
                        json.dumps(record.provenance.to_dict()),
                        {
                            "gate_verdict": record.status.gate_verdict.value,
                            "defect": record.status.defect,
                            "cause": record.status.cause.value,
                            "severity": record.status.severity.value,
                            "quarantine": record.status.quarantine,
                            "maturity": record.status.maturity.value,
                            "uncertainty": json.dumps(record.status.uncertainty),
                            "reproducibility": record.status.reproducibility.value,
                            "assessment_procedure_version": record.status.assessment_procedure_version,
                            "ceec_link": record.status.ceec_link,
                        },
                        json.dumps(record.payload),
                        json.dumps(record.unknown) if record.unknown else None,
                    ],
                )
            except duckdb.ConstraintException as e:
                if (
                    "measurement_key" in str(e)
                    and "unique constraint" in str(e).lower()
                ):
                    raise DuplicateMeasurementError(record.measurement_key) from e
                raise StoreError(f"Constraint violation: {e}") from e

            # Fetch the assigned seq
            result = self._conn.execute(
                "SELECT seq FROM records WHERE record_id = ?", [record.record_id]
            ).fetchone()

            if result is None:
                raise StoreError("Failed to retrieve seq after insert")

            # Create new record with assigned seq, preserving original objects
            return Record(
                record_id=record.record_id,
                seq=result[0],
                run_id=record.run_id,
                schema_version=record.schema_version,
                cell_key=record.cell_key,
                measurement_key=record.measurement_key,
                substrate=record.substrate,
                geometry=record.geometry,
                dynamics=record.dynamics,
                plasticity=record.plasticity,
                credit=record.credit,
                update=record.update,
                params=record.params,
                schedule=record.schedule,
                provenance=record.provenance,
                status=record.status,
                payload=record.payload,
                unknown=record.unknown,
            )

    def append_artifacts(
        self, record_id: str, artifacts: list[tuple[str, str]]
    ) -> None:
        """Append artifact references for a record.

        Args:
            record_id: The record ID
            artifacts: List of (digest, role) tuples
        """
        if self._conn is None:
            raise StoreError("Connection not initialized")
        with self._write_lock:
            for digest, role in artifacts:
                self._conn.execute(
                    """
                    INSERT INTO record_artifacts (record_id, digest, role)
                    VALUES (?, ?, ?)
                    ON CONFLICT DO NOTHING
                    """,
                    [record_id, digest, role],
                )

    def get_record(self, record_id: str) -> Record | None:
        """Get a record by record_id."""
        if self._conn is None:
            raise StoreError("Connection not initialized")
        row = self._conn.execute(
            "SELECT * FROM records WHERE record_id = ?", [record_id]
        ).fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def get_record_by_measurement_key(self, measurement_key: str) -> Record | None:
        """Get a record by measurement_key (for resume/dedup)."""
        if self._conn is None:
            raise StoreError("Connection not initialized")
        row = self._conn.execute(
            "SELECT * FROM records WHERE measurement_key = ?", [measurement_key]
        ).fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def query_records(
        self,
        run_id: str | None = None,
        cell_key: str | None = None,
        gate_verdict: GateVerdict | None = None,
        fidelity: str | None = None,
        quarantine: bool | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Record]:
        """Query records with filters."""
        if self._conn is None:
            raise StoreError("Connection not initialized")

        conditions = []
        params = []

        if run_id is not None:
            conditions.append("run_id = ?")
            params.append(run_id)
        if cell_key is not None:
            conditions.append("cell_key = ?")
            params.append(cell_key)
        if gate_verdict is not None:
            conditions.append("status.gate_verdict = ?")
            params.append(gate_verdict.value)
        if fidelity is not None:
            conditions.append("schedule.fidelity = ?")
            params.append(fidelity)
        if quarantine is not None:
            conditions.append("status.quarantine = ?")
            params.append(quarantine)

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        limit_clause = f" LIMIT {limit}" if limit else ""
        offset_clause = f" OFFSET {offset}" if offset else ""

        # ruff: noqa: S608 - query is parameterized, not interpolated
        query = f"SELECT * FROM records{where_clause} ORDER BY seq{limit_clause}{offset_clause}"
        rows = self._conn.execute(query, params).fetchall()
        return [self._row_to_record(row) for row in rows]

    def claim_eligible_prefilter(
        self,
        fidelity: str = "L2",
        min_n_seeds: int = 5,
    ) -> list[Record]:
        """SQL prefilter for claim eligibility.

        Claim prefilter: WHERE status.gate_verdict = 'PASS'
        AND NOT status.quarantine
        AND schedule.fidelity = 'L2'
        AND schedule.n_seeds >= 5
        """
        return self.query_records(
            gate_verdict=GateVerdict.PASS_,
            fidelity=fidelity,
            quarantine=False,
        )

    def _row_to_record(self, row: tuple) -> Record:
        """Convert a database row to a Record."""
        return self._build_record_from_row(row)

    def _build_record_from_row(self, row: tuple) -> Record:
        """Build a Record from a database row tuple."""
        schedule = self._parse_schedule(row[13])
        provenance = self._parse_provenance(row[14])
        status = self._parse_status(row[15])

        return Record(
            record_id=row[0],
            seq=row[1],
            run_id=row[2],
            schema_version=row[3],
            cell_key=row[4],
            measurement_key=row[5],
            substrate=row[6],
            geometry=row[7],
            dynamics=row[8],
            plasticity=row[9],
            credit=row[10],
            update=row[11],
            params=json.loads(row[12]),
            schedule=schedule,
            provenance=provenance,
            status=status,
            payload=json.loads(row[16]),
            unknown=json.loads(row[17]) if row[17] else None,
        )

    def _parse_schedule(self, schedule_struct: dict[str, Any]) -> Schedule:
        """Parse schedule from database struct."""
        return Schedule(
            fidelity=schedule_struct["fidelity"],
            seed=schedule_struct["seed"],
            n_seeds=schedule_struct["n_seeds"],
            epochs=schedule_struct["epochs"],
            batch_limit=schedule_struct["batch_limit"],
            budget_id=schedule_struct["budget_id"],
        )

    def _parse_provenance(self, provenance_json: str) -> Provenance:
        """Parse provenance from database JSON."""
        return Provenance.from_dict(json.loads(provenance_json))

    def _parse_status(self, status_struct: dict[str, Any]) -> Status:
        """Parse status from database struct."""
        return Status(
            gate_verdict=GateVerdict(status_struct["gate_verdict"]),
            defect=status_struct["defect"],
            cause=FailureCause(status_struct["cause"]),
            severity=Severity(status_struct["severity"]),
            quarantine=status_struct["quarantine"],
            maturity=Maturity(status_struct["maturity"]),
            uncertainty=json.loads(status_struct["uncertainty"]),
            reproducibility=ReproducibilityClass(status_struct["reproducibility"]),
            assessment_procedure_version=status_struct["assessment_procedure_version"],
            ceec_link=status_struct["ceec_link"],
        )

    def count_records(self, run_id: str | None = None) -> int:
        """Count records, optionally filtered by run_id."""
        if self._conn is None:
            raise StoreError("Connection not initialized")
        if run_id:
            result = self._conn.execute(
                "SELECT COUNT(*) FROM records WHERE run_id = ?", [run_id]
            ).fetchone()
        else:
            result = self._conn.execute("SELECT COUNT(*) FROM records").fetchone()
        return result[0] if result is not None else 0


__all__ = [
    "DuplicateMeasurementError",
    "RecordStore",
    "StoreConfig",
    "StoreError",
]
