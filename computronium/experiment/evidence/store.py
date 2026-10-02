"""DuckDB-backed record store for experiment evidence.

Implements WP5: unified artifact storage, vector retrieval, atomic append
with artifacts, Pydantic v2 models for I/O boundaries.
"""

from __future__ import annotations

import json
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Final, Literal, Self

import duckdb

if TYPE_CHECKING:
    from pathlib import Path

from computronium.experiment.evidence.artifacts import (
    ArtifactInput,
    ArtifactStore,
)
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
from computronium.experiment.schema.run_spec import RunSpec
from computronium.experiment.schema.versioning import current_schema_version

if TYPE_CHECKING:
    from collections.abc import Sequence

    from pydantic import BaseModel

    from computronium.experiment.schema.axis import StructuralAxis


class DuplicateMeasurementError(Exception):
    """Raised when a measurement_key already exists (UNIQUE constraint violation)."""

    def __init__(self, measurement_key: str) -> None:
        self.measurement_key = measurement_key
        super().__init__(f"Duplicate measurement_key: {measurement_key}")


class StoreError(Exception):
    """Base exception for store errors."""


class UnsupportedSchemaVersionError(StoreError):
    """Raised when a row carries an unknown schema_version (fail-closed, Directive 2)."""


type TableName = Literal["records", "artifacts", "runs", "vector_index"]


@dataclass(frozen=True, slots=True)
class RunInfo:
    """Public read-model row for the runs table."""

    run_id: str
    spec: RunSpec | None
    spec_version: int
    status: str
    budget_consumed_s: float | None
    replay_hash: str | None
    started_at: datetime
    finished_at: datetime | None


@dataclass(frozen=True, slots=True)
class TableSlice:
    """Column-typed result of a public table read."""

    columns: tuple[str, ...]
    rows: tuple[tuple[Any, ...], ...]


@dataclass(frozen=True, slots=True)
class StoreConfig:
    """Configuration for RecordStore."""

    path: Path
    read_only: bool = False
    artifact_inline_threshold_mb: float = 10.0
    artifact_external_path: Path | None = None


class RecordStore:  # ruff: ignore[too-many-public-methods] - single-writer topology concentrates the read/write API here by design (§1.1)
    """DuckDB-backed record store with single-writer guarantee.

    All writes flow through a single instance guarded by a threading.RLock.
    DuckDB allows one writer process; this design concentrates writes
    in the orchestrating process.

    Features:
    - Atomic record + artifact append (single transaction)
    - Vector retrieval (brute-force + optional HNSW via vss)
    - Pydantic v2 validation at I/O boundaries
    """

    _SCHEMA_VERSION = current_schema_version()
    SUPPORTED_SCHEMA_VERSIONS = frozenset({_SCHEMA_VERSION})

    def __init__(self, config: StoreConfig) -> None:
        self._config = config
        self._conn: duckdb.DuckDBPyConnection | None = None
        self._write_lock = threading.RLock()
        self._initialized = False
        self._artifact_store: ArtifactStore | None = None

    def __enter__(self) -> Self:
        self._conn = duckdb.connect(
            str(self._config.path), read_only=self._config.read_only
        )
        if not self._initialized and not self._config.read_only:
            self._init_schema()
            self._initialized = True
        # Initialize artifact store
        self._artifact_store = ArtifactStore(
            conn=self._conn,
            write_lock=self._write_lock,
            inline_threshold_mb=self._config.artifact_inline_threshold_mb,
            external_store_path=self._config.artifact_external_path,
        )
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
        self._artifact_store = None

    @property
    def is_open(self) -> bool:
        """Whether the store is inside its connection context."""
        return self._conn is not None

    @property
    def artifacts(self) -> ArtifactStore:
        """Access the artifact store."""
        if self._artifact_store is None:
            raise StoreError("Artifact store not initialized (enter context first)")
        return self._artifact_store

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
                measurement_key TEXT NOT NULL,
                substrate       TEXT NOT NULL,
                geometry        TEXT NOT NULL,
                dynamics        TEXT NOT NULL,
                plasticity      TEXT NOT NULL,
                credit          TEXT NOT NULL,
                update          TEXT NOT NULL,
                params          JSON NOT NULL,
                schedule        STRUCT(fidelity TEXT, seed INTEGER, n_seeds INTEGER,
                                       epochs INTEGER, batch_limit INTEGER, budget_id TEXT,
                                       task_id TEXT) NOT NULL,
                provenance      JSON NOT NULL,
                status          STRUCT(gate_verdict TEXT, defect TEXT, cause TEXT, severity TEXT,
                                       quarantine BOOLEAN, maturity TEXT, uncertainty JSON,
                                       reproducibility TEXT, assessment_procedure_version TEXT,
                                       ceec_link TEXT) NOT NULL,
                payload         JSON NOT NULL,
                unknown         JSON,
                UNIQUE(run_id, measurement_key)
            )
        """)

        # Artifacts table (unified - replaces record_artifacts + CEEC delegation)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS artifacts (
                digest            TEXT PRIMARY KEY,
                bytes             BLOB,
                role              TEXT NOT NULL,
                record_id         TEXT NOT NULL REFERENCES records(record_id),
                created_at        TIMESTAMP NOT NULL,
                external_uri      TEXT,
                external_size     BIGINT,
                external_checksum TEXT
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
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_artifacts_record_id ON artifacts(record_id)"
        )

    @staticmethod
    def _read_spec(run_id: str, raw: str | None) -> RunSpec | None:
        """Parse a persisted spec, failing closed on one that no longer validates.

        A spec that cannot be validated is drift, not an inconvenience: it
        names fields the run no longer understands, so a report built from it
        would be describing a run that cannot be reproduced.
        """
        if not raw:
            return None
        try:
            return RunSpec.from_dict(json.loads(raw))
        except (ValueError, json.JSONDecodeError) as exc:
            msg = f"run {run_id} has a spec that does not validate: {exc}"
            raise StoreError(msg) from exc

    def create_run(
        self,
        run_id: str | None = None,
        spec: RunSpec | None = None,
    ) -> str:
        """Create a new run and return its run_id.

        Args:
            run_id: Identifier to use; a UUID4 when omitted.
            spec: The run's typed spec. Its ``version`` is the persisted
                ``spec_version`` — the spec declares its own version, so a
                caller cannot record a version the spec does not claim.

        Returns:
            The run_id written.
        """
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
                    json.dumps(spec.to_dict()) if spec else None,
                    spec.version if spec else 0,
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
                            "task_id": record.schedule.task_id,
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
                if "measurement_key" in str(e) or "record_id" in str(e):
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

    def append_with_artifacts(
        self, record: Record, artifacts: list[ArtifactInput]
    ) -> Record:
        """Atomic append: record + all artifacts in single transaction.

        Args:
            record: The record to append
            artifacts: List of ArtifactInput objects

        Returns:
            Record with assigned seq

        Raises:
            DuplicateMeasurementError: If measurement_key already exists
            StoreError: On any storage failure (transaction rolled back)
        """
        if self._conn is None:
            raise StoreError("Connection not initialized")
        if self._artifact_store is None:
            raise StoreError("Artifact store not initialized")

        with self._write_lock:
            self._conn.execute("BEGIN")
            try:
                # Insert record
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
                            "task_id": record.schedule.task_id,
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

                # Store artifacts
                for art_input in artifacts:
                    self._artifact_store.put(art_input, record.record_id)

                self._conn.execute("COMMIT")

            except duckdb.ConstraintException as e:
                self._conn.execute("ROLLBACK")
                if "measurement_key" in str(e) or "record_id" in str(e):
                    raise DuplicateMeasurementError(record.measurement_key) from e
                raise StoreError(f"Constraint violation: {e}") from e
            except Exception:
                self._conn.execute("ROLLBACK")
                raise

            # Fetch the assigned seq and return updated record (inside lock for thread safety)
            result = self._conn.execute(
                "SELECT seq FROM records WHERE record_id = ?", [record.record_id]
            ).fetchone()

            if result is None:
                raise StoreError("Failed to retrieve seq after insert")

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

    def query_records(  # ruff: ignore[too-many-arguments, too-many-positional-arguments] - a query builder's filters are one parameter each
        self,
        run_id: str | None = None,
        *,
        cell_key: str | None = None,
        gate_verdict: GateVerdict | None = None,
        fidelity: str | None = None,
        quarantine: bool | None = None,
        min_n_seeds: int | None = None,
        data_origin: str | None = None,
        payload_kind: str | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Record]:
        """Query records with filters.

        Args:
            run_id: Filter by run ID.
            cell_key: Filter by cell key (groups repeated evaluations).
            gate_verdict: Filter by gate verdict.
            fidelity: Filter by schedule fidelity (L0/L1/L2).
            quarantine: Filter by quarantine status.
            min_n_seeds: Filter to schedules that *plan* at least this many seeds.
            data_origin: Filter by provenance.data_origin (exploration/policy_selected/calibration/test).
            payload_kind: Filter by payload.kind (e.g., "icu", "hypothesis", "literature").
            limit: Maximum number of records to return.
            offset: Number of records to skip.
        """
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
        if min_n_seeds is not None:
            conditions.append("schedule.n_seeds >= ?")
            params.append(int(min_n_seeds))
        if data_origin is not None:
            conditions.append("json_extract_string(provenance, '$.data_origin') = ?")
            params.append(data_origin)
        if payload_kind is not None:
            conditions.append("json_extract_string(payload, '$.kind') = ?")
            params.append(payload_kind)

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        limit_clause = f" LIMIT {limit}" if limit else ""
        offset_clause = f" OFFSET {offset}" if offset else ""

        # ruff: file-ignore[S608] - query is parameterized, not interpolated
        query = f"SELECT * FROM records{where_clause} ORDER BY seq{limit_clause}{offset_clause}"
        rows = self._conn.execute(query, params).fetchall()
        return [self._row_to_record(row) for row in rows]

    def query_records_by_payload_kind(
        self,
        payload_kind: str,
        run_id: str | None = None,
        data_origin: str | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Record]:
        """Query records by payload kind with optional filters.

        Args:
            payload_kind: The payload kind to filter by (e.g., "icu", "hypothesis", "literature").
            run_id: Optional run ID filter.
            data_origin: Optional data origin filter.
            limit: Maximum number of records.
            offset: Number of records to skip.
        """
        return self.query_records(
            run_id=run_id,
            data_origin=data_origin,
            payload_kind=payload_kind,
            limit=limit,
            offset=offset,
        )

    def claim_eligible_prefilter(
        self,
        fidelity: str = "L2",
        min_n_seeds: int = 5,
    ) -> list[Record]:
        """SQL prefilter for claim eligibility (R35).

        ``WHERE status.gate_verdict = 'PASS' AND NOT status.quarantine
        AND schedule.fidelity = ? AND schedule.n_seeds >= ?`` — the same four
        conditions ``claims.claim_eligible`` reads, so the store and the pure
        predicate cannot disagree. ``min_n_seeds`` filters the *planned* seed
        count, which is what the predicate asks; the *achieved* count is a
        property of a replication group, and
        :meth:`claim_eligible_replication_keys` is where that is decided.
        """
        return self.query_records(
            gate_verdict=GateVerdict.PASS_,
            fidelity=fidelity,
            quarantine=False,
            min_n_seeds=min_n_seeds,
        )

    def claim_eligible_replication_keys(
        self,
        run_id: str | None = None,
        min_n_seeds: int = 5,
        fidelity: str = "L2",
    ) -> tuple[str, ...]:
        """Replication keys that *achieved* ``min_n_seeds`` distinct passing seeds.

        Claim eligibility is a property of a cell, not of one of its seeds: the
        executor writes one record per seed with ``schedule.n_seeds == 1``, so
        no record-level filter can answer it. One grouped query, so the answer
        costs one round trip rather than one per cell.
        """
        if self._conn is None:
            raise StoreError("Connection not initialized")
        conditions = ["status.gate_verdict = ?", "schedule.fidelity = ?"]
        params: list[Any] = [GateVerdict.PASS_.value, fidelity]
        if run_id is not None:
            conditions.append("run_id = ?")
            params.append(run_id)
        query = (
            f"SELECT {_REPLICATION_COLUMNS}, COUNT(DISTINCT schedule.seed) "
            "FROM records WHERE "
            + " AND ".join(conditions)
            + f" GROUP BY {_REPLICATION_COLUMNS}"
        )
        rows = self._conn.execute(query, params).fetchall()  # ruff: ignore[hardcoded-sql-expression] - static columns, bound params
        return tuple(
            format_replication_key(row[:6])
            for row in rows
            if row[6] >= int(min_n_seeds)
        )

    # =========================================================================
    # Vector Retrieval (brute-force + optional HNSW)
    # =========================================================================

    def add_embedding(
        self,
        record_id: str,
        embedding: list[float],
        version: int = 1,
    ) -> None:
        """Add or update a vector embedding for a record."""
        if self._conn is None:
            raise StoreError("Connection not initialized")
        if len(embedding) != 384:
            raise ValueError(f"Embedding must be 384-dimensional, got {len(embedding)}")

        with self._write_lock:
            self._conn.execute(
                """
                INSERT INTO vector_index (record_id, embedding, embedding_version)
                VALUES (?, ?, ?)
                ON CONFLICT (record_id) DO UPDATE SET
                    embedding = EXCLUDED.embedding,
                    embedding_version = EXCLUDED.embedding_version
                """,
                [record_id, embedding, version],
            )

    def get_embedding(self, record_id: str) -> list[float] | None:
        """Get embedding for a record."""
        if self._conn is None:
            raise StoreError("Connection not initialized")
        row = self._conn.execute(
            "SELECT embedding FROM vector_index WHERE record_id = ?", [record_id]
        ).fetchone()
        return list(row[0]) if row else None

    def vector_search_brute_force(
        self,
        query_embedding: list[float],
        k: int = 10,
        metric: str = "cosine",
        filter_run_id: str | None = None,
    ) -> list[tuple[Record, float]]:
        """Brute-force vector search using DuckDB's array operations.

        Args:
            query_embedding: Query vector (384-dim)
            k: Number of results to return
            metric: "cosine" or "dot"
            filter_run_id: Optional run_id to restrict search

        Returns:
            List of (Record, score) tuples, highest score first
        """
        if self._conn is None:
            raise StoreError("Connection not initialized")
        if len(query_embedding) != 384:
            raise ValueError(
                f"Embedding must be 384-dimensional, got {len(query_embedding)}"
            )

        # Build filter
        where_clause = ""
        params: list[Any] = []
        if filter_run_id:
            where_clause = "WHERE r.run_id = ?"
            params.append(filter_run_id)

        if metric == "cosine":
            # Cosine similarity = dot(a,b) / (|a|*|b|)
            # DuckDB: list_dot(a,b) / (list_norm(a) * list_norm(b))
            score_expr = (
                "list_dot(vi.embedding, ?) / (list_norm(vi.embedding) * list_norm(?))"
            )
            params.extend([query_embedding, query_embedding])
        else:
            # Dot product
            score_expr = "list_dot(vi.embedding, ?)"
            params.append(query_embedding)

        query = f"""
            SELECT r.*, {score_expr} AS score
            FROM records r
            JOIN vector_index vi ON r.record_id = vi.record_id
            {where_clause}
            ORDER BY score DESC
            LIMIT ?
        """
        params.append(k)

        rows = self._conn.execute(query, params).fetchall()
        return [(self._row_to_record(row[:-1]), row[-1]) for row in rows]

    def vector_search_hnsw(
        self,
        query_embedding: list[float],
        k: int = 10,
        filter_run_id: str | None = None,
    ) -> list[tuple[Record, float]]:
        """HNSW vector search via DuckDB vss extension (experimental).

        Falls back to brute-force if vss not available.

        Args:
            query_embedding: Query vector (384-dim)
            k: Number of results to return
            filter_run_id: Optional run_id to restrict search

        Returns:
            List of (Record, score) tuples, highest score first
        """
        if self._conn is None:
            raise StoreError("Connection not initialized")

        # Check if vss extension is available
        try:
            self._conn.execute("LOAD vss")
        except duckdb.CatalogException:
            # Fall back to brute force
            return self.vector_search_brute_force(
                query_embedding, k, "cosine", filter_run_id
            )

        where_clause = ""
        params = [query_embedding, k]
        if filter_run_id:
            where_clause = "AND r.run_id = ?"
            params.append(filter_run_id)

        query = f"""
            SELECT r.*, vi.embedding <=> ? AS distance
            FROM records r
            JOIN vector_index vi ON r.record_id = vi.record_id
            WHERE 1=1 {where_clause}
            ORDER BY distance ASC
            LIMIT ?
        """

        try:
            rows = self._conn.execute(query, params).fetchall()
            # Convert distance to similarity score (1 - distance for cosine)
            return [(self._row_to_record(row[:-1]), 1.0 - row[-1]) for row in rows]
        except Exception:
            # Fall back on any error
            return self.vector_search_brute_force(
                query_embedding, k, "cosine", filter_run_id
            )

    def vector_search(
        self,
        query_embedding: list[float],
        k: int = 10,
        metric: str = "cosine",
        filter_run_id: str | None = None,
        use_hnsw: bool = False,
    ) -> list[tuple[Record, float]]:
        """Unified vector search interface.

        Args:
            query_embedding: Query vector (384-dim)
            k: Number of results
            metric: "cosine" or "dot" (for brute force)
            filter_run_id: Optional run filter
            use_hnsw: Try HNSW first (requires vss extension)

        Returns:
            List of (Record, score) tuples
        """
        if use_hnsw:
            return self.vector_search_hnsw(query_embedding, k, filter_run_id)
        return self.vector_search_brute_force(query_embedding, k, metric, filter_run_id)

    # =========================================================================
    # Pydantic Models for I/O Boundaries
    # =========================================================================

    def _row_to_record(self, row: tuple) -> Record:
        """Convert a database row to a Record."""
        return self._build_record_from_row(row)

    def _build_record_from_row(self, row: tuple) -> Record:
        """Build a Record from a database row tuple."""
        if row[3] not in self.SUPPORTED_SCHEMA_VERSIONS:
            raise UnsupportedSchemaVersionError(
                f"Unsupported schema_version {row[3]} for record {row[0]}; "
                f"supported: {sorted(self.SUPPORTED_SCHEMA_VERSIONS)}"
            )
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
            task_id=schedule_struct["task_id"],
            # Rows written before the ceiling existed declare none.
            param_budget=schedule_struct.get("param_budget", 0),
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

    def count_achieved_seeds(
        self,
        replication_key: str,
        run_id: str | None = None,
        gate_verdict: GateVerdict | None = GateVerdict.PASS_,
    ) -> int:
        """Count distinct seeds achieved for one replication key.

        Args:
            replication_key: The replication key, as ``claims.replication_key``
                formats it (coordinate + schedule without seed).
            run_id: Optional run ID filter.
            gate_verdict: Filter by gate verdict (default PASS).

        Returns:
            Number of distinct seeds achieved for this replication key.
        """
        if self._conn is None:
            raise StoreError("Connection not initialized")
        conditions, params = _replication_predicate(replication_key)
        if gate_verdict is not None:
            conditions.append("status.gate_verdict = ?")
            params.append(gate_verdict.value)
        if run_id is not None:
            conditions.append("run_id = ?")
            params.append(run_id)
        query = (
            "SELECT COUNT(DISTINCT schedule.seed) FROM records WHERE "
            + " AND ".join(conditions)
        )
        row = self._conn.execute(query, params).fetchone()  # ruff: ignore[hardcoded-sql-expression] - static conditions, bound params
        return row[0] if row is not None else 0

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

    # =========================================================================
    # Public read API (L14: surface consumes these; no _conn reach-ins)
    # =========================================================================

    def query_run(self, run_id: str) -> RunInfo | None:
        """Get a single run's info, or None if absent."""
        rows = self.query_runs(run_id)
        return rows[0] if rows else None

    def query_runs(
        self, run_id: str | None = None, limit: int | None = None
    ) -> list[RunInfo]:
        """Query runs (latest first when run_id is omitted)."""
        if self._conn is None:
            raise StoreError("Connection not initialized")
        conditions: list[str] = []
        params: list[Any] = []
        if run_id is not None:
            conditions.append("run_id = ?")
            params.append(run_id)
        where_clause = f" WHERE {' AND '.join(conditions)}" if conditions else ""  # noqa: S608 - static fragment, parameterized values
        limit_clause = f" LIMIT {int(limit)}" if limit else ""  # noqa: S608 - int-coerced
        rows = self._conn.execute(
            f"SELECT run_id, spec, spec_version, status, budget_consumed_s, "  # ruff: ignore[hardcoded-sql-expression] - static column list
            f"replay_hash, started_at, finished_at FROM runs{where_clause} "
            f"ORDER BY started_at DESC{limit_clause}",
            params,
        ).fetchall()
        return [
            RunInfo(
                run_id=row[0],
                spec=self._read_spec(row[0], row[1]),
                spec_version=row[2],
                status=row[3],
                budget_consumed_s=row[4],
                replay_hash=row[5],
                started_at=row[6],
                finished_at=row[7],
            )
            for row in rows
        ]

    def latest_run_id(self) -> str | None:
        """Return the most recently started run_id, or None."""
        runs = self.query_runs(limit=1)
        return runs[0].run_id if runs else None

    def count_passing_records(self, run_id: str | None = None) -> int:
        """Count records with PASS gate verdict and no quarantine."""
        if self._conn is None:
            raise StoreError("Connection not initialized")
        conditions = ["status.gate_verdict = 'PASS'", "status.quarantine = 0"]
        params: list[Any] = []
        if run_id:
            conditions.append("run_id = ?")
            params.append(run_id)
        where_clause = " WHERE " + " AND ".join(conditions)
        result = self._conn.execute(
            f"SELECT COUNT(*) FROM records{where_clause}",
            params,  # noqa: S608 - parameterized, static conditions
        ).fetchone()
        return result[0] if result is not None else 0

    def count_by_status_field(
        self, field: Literal["maturity", "gate_verdict"], run_id: str | None = None
    ) -> dict[str, int]:
        """Count records grouped by a status struct field."""
        if self._conn is None:
            raise StoreError("Connection not initialized")
        column = "status.maturity" if field == "maturity" else "status.gate_verdict"
        conditions = []
        params: list[Any] = []
        if run_id:
            conditions.append("run_id = ?")
            params.append(run_id)
        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        rows = self._conn.execute(
            f"SELECT {column}, COUNT(*) FROM records{where_clause} "  # ruff: ignore[hardcoded-sql-expression] - column from Literal whitelist
            f"GROUP BY {column}",
            params,
        ).fetchall()
        return {row[0]: row[1] for row in rows}

    def cell_seed_counts(self, run_id: str | None = None) -> dict[str, int]:
        """Count records per cell_key (seed replication counts)."""
        if self._conn is None:
            raise StoreError("Connection not initialized")
        conditions = []
        params: list[Any] = []
        if run_id:
            conditions.append("run_id = ?")
            params.append(run_id)
        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        rows = self._conn.execute(
            f"SELECT cell_key, COUNT(*) FROM records{where_clause} "  # ruff: ignore[hardcoded-sql-expression] - parameterized
            "GROUP BY cell_key",
            params,
        ).fetchall()
        return {row[0]: row[1] for row in rows}

    def count_by_failure_cause(self, run_id: str | None = None) -> dict[str, int]:
        """Count records grouped by failure cause (non-unknown causes only)."""
        if self._conn is None:
            raise StoreError("Connection not initialized")
        conditions = ["status.cause != 'unknown'"]
        params: list[Any] = []
        if run_id:
            conditions.append("run_id = ?")
            params.append(run_id)
        where_clause = " WHERE " + " AND ".join(conditions)
        rows = self._conn.execute(
            f"SELECT status.cause, COUNT(*) FROM records{where_clause} "  # ruff: ignore[hardcoded-sql-expression] - parameterized
            "GROUP BY status.cause",
            params,
        ).fetchall()
        return {row[0]: row[1] for row in rows}

    def count_by_axis(
        self,
        axis: StructuralAxis,
        run_id: str | None = None,
    ) -> dict[str, int]:
        """Count records grouped by a structural axis value (axis coverage, R18)."""
        if self._conn is None:
            raise StoreError("Connection not initialized")
        conditions = []
        params: list[Any] = []
        if run_id:
            conditions.append("run_id = ?")
            params.append(run_id)
        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        rows = self._conn.execute(
            f"SELECT {axis}, COUNT(*) FROM records{where_clause} "  # ruff: ignore[hardcoded-sql-expression] - axis from Literal whitelist
            f"GROUP BY {axis}",
            params,
        ).fetchall()
        return {row[0]: row[1] for row in rows}

    def read_table(self, table: TableName, run_id: str | None = None) -> TableSlice:
        """Read a full table (optionally scoped to a run) with columns.

        Public bulk-read for exporters; table name is a Literal whitelist and
        values are parameterized.
        """
        if self._conn is None:
            raise StoreError("Connection not initialized")
        match table:
            case "records":
                query = (
                    "SELECT * FROM records WHERE run_id = ? ORDER BY seq"
                    if run_id
                    else "SELECT * FROM records ORDER BY seq"
                )
            case "artifacts":
                query = (
                    "SELECT * FROM artifacts WHERE record_id IN "
                    "(SELECT record_id FROM records WHERE run_id = ?) ORDER BY created_at"
                    if run_id
                    else "SELECT * FROM artifacts ORDER BY created_at"
                )
            case "runs":
                query = (
                    "SELECT * FROM runs WHERE run_id = ? ORDER BY started_at"
                    if run_id
                    else "SELECT * FROM runs ORDER BY started_at"
                )
            case "vector_index":
                query = (
                    "SELECT * FROM vector_index WHERE record_id IN "
                    "(SELECT record_id FROM records WHERE run_id = ?)"
                    if run_id
                    else "SELECT * FROM vector_index"
                )
        params = [run_id] if run_id else []
        cursor = self._conn.execute(query, params)
        columns = tuple(d[0] for d in cursor.description)
        rows = tuple(cursor.fetchall())
        return TableSlice(columns=columns, rows=rows)

    def record_intent(self, run_id: str, intent: dict[str, Any]) -> Record:
        """Persist an operator intent as a run-linked record (R84, L13).

        Payload kind is ``operator_intent``; uniqueness derives from
        ``intent_id`` via ``schedule.task_id``, so redelivery dedups through
        the single writer like any other measurement.
        """
        from computronium.experiment.schema.coordinate import Coordinate, DataOrigin

        intent_id = str(intent.get("intent_id", uuid.uuid4()))
        record = Record.create(
            run_id=run_id,
            coordinate=Coordinate(
                substrate="operator",
                geometry="control",
                dynamics="none",
                plasticity="none",
                credit="none",
                update="none",
                params={"intent_id": intent_id},
            ),
            schedule=Schedule(
                fidelity="L0",
                seed=0,
                n_seeds=1,
                epochs=1,
                batch_limit=0,
                budget_id="operator",
                task_id=intent_id,
            ),
            provenance=Provenance(
                env={},
                dataset="operator",
                dataset_version="v1",
                code_sha="kernel",
                policy="operator",
                links={"run_id": run_id},
                data_origin=DataOrigin.EXPLORATION,
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
            payload={
                "kind": "operator_intent",
                "intent_kind": intent.get("kind"),
                **{k: v for k, v in intent.items() if k != "kind"},
            },
        )
        return self.append(record)

    def query_intent_records(self, run_id: str | None = None) -> list[Record]:
        """Operator-intent records, optionally scoped to a run (R84)."""
        return self.query_records_by_payload_kind("operator_intent", run_id=run_id)

    def export_snapshot(self, run_id: str | None = None) -> dict[str, Any]:
        """Public bulk-export read model (R73, L14).

        Returns JSON-serializable ``records``/``runs``/``artifacts``/
        ``vector_index`` collections without exposing the connection.
        Artifact bytes stay out; manifests carry digest, role, and
        external references.
        """
        records = [r.to_dict() for r in self.query_records(run_id=run_id)]
        runs = [
            {
                "run_id": info.run_id,
                "spec": info.spec.to_dict() if info.spec else None,
                "spec_version": info.spec_version,
                "status": info.status,
                "budget_consumed_s": info.budget_consumed_s,
                "replay_hash": info.replay_hash,
                "started_at": info.started_at.isoformat() if info.started_at else None,
                "finished_at": info.finished_at.isoformat()
                if info.finished_at
                else None,
            }
            for info in self.query_runs(run_id=run_id)
        ]
        artifacts: list[dict[str, Any]] = []
        table = self.read_table("artifacts", run_id)
        for row in table.rows:
            entry = dict(zip(table.columns, row, strict=True))
            created = entry.get("created_at")
            artifacts.append({
                "digest": entry.get("digest"),
                "role": entry.get("role"),
                "record_id": entry.get("record_id"),
                "created_at": created.isoformat() if created is not None else None,
                "external_uri": entry.get("external_uri"),
                "external_size": entry.get("external_size"),
                "external_checksum": entry.get("external_checksum"),
            })
        vectors: list[dict[str, Any]] = []
        vi = self.read_table("vector_index", run_id)
        for row in vi.rows:
            entry = dict(zip(vi.columns, row, strict=True))
            vectors.append({
                "record_id": entry.get("record_id"),
                "embedding": list(entry.get("embedding") or []),
                "embedding_version": entry.get("embedding_version"),
            })
        return {
            "records": records,
            "runs": runs,
            "artifacts": artifacts,
            "vector_index": vectors,
        }


# =========================================================================
# Pydantic v2 Models for I/O Validation
# =========================================================================

try:
    from typing import Annotated

    from pydantic import BaseModel, ConfigDict, Field

    class ScheduleModel(BaseModel):
        """Pydantic model for Schedule validation at I/O boundaries."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        fidelity: Annotated[str, Field(pattern="^(L0|L1|L2)$")]
        seed: Annotated[int, Field(ge=0)]
        n_seeds: Annotated[int, Field(gt=0)]
        epochs: Annotated[int, Field(gt=0)]
        batch_limit: Annotated[int, Field(ge=0)]
        budget_id: str

    class ProvenanceModel(BaseModel):
        """Pydantic model for Provenance validation at I/O boundaries."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        env: dict[str, str]
        dataset: str
        dataset_version: str
        code_sha: str
        policy: str
        links: dict[str, str]
        data_origin: str = "exploration"
        training_tasks: list[str] = []
        transfer_source_ids: list[str] = []
        transfer_cutoff: str | None = None
        target_task: str | None = None
        transfer_mode: str | None = None

    class StatusModel(BaseModel):
        """Pydantic model for Status validation at I/O boundaries."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        gate_verdict: Annotated[str, Field(pattern="^(PASS|FAIL|QUARANTINE|PENDING)$")]
        defect: str
        cause: Annotated[
            str,
            Field(
                pattern="^(unknown|numerical|timeout|oom|invalid_config|runtime_error|constraint_violation|divergence)$"
            ),
        ]
        severity: Annotated[str, Field(pattern="^(low|medium|high|critical)$")]
        quarantine: bool
        maturity: Annotated[str, Field(pattern="^(l0|l1|l2)$")]
        uncertainty: dict[str, Any]
        reproducibility: Annotated[
            str,
            Field(
                pattern="^(replayable|computationally_reproducible|scientifically_reproducible)$"
            ),
        ]
        assessment_procedure_version: str
        ceec_link: str | None = None

    class RecordInputModel(BaseModel):
        """Pydantic model for Record input validation (create/append)."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        run_id: str
        coordinate: dict[str, Any]
        schedule: ScheduleModel
        provenance: ProvenanceModel
        status: StatusModel
        payload: dict[str, Any]
        unknown: dict[str, Any] | None = None
        schema_version: int = 2

    class RecordOutputModel(BaseModel):
        """Pydantic model for Record output validation (query results)."""

        model_config = ConfigDict(frozen=True, extra="forbid")

        record_id: str
        seq: int
        run_id: str
        schema_version: int
        cell_key: str
        measurement_key: str
        substrate: str
        geometry: str
        dynamics: str
        plasticity: str
        credit: str
        update: str
        params: dict[str, Any]
        schedule: ScheduleModel
        provenance: ProvenanceModel
        status: StatusModel
        payload: dict[str, Any]
        unknown: dict[str, Any] | None = None

    # Validation helpers
    def validate_record_input(data: dict[str, Any]) -> RecordInputModel:
        """Validate record input data using Pydantic."""
        return RecordInputModel.model_validate(data)

    def validate_record_output(data: dict[str, Any]) -> RecordOutputModel:
        """Validate record output data using Pydantic."""
        return RecordOutputModel.model_validate(data)

except ImportError:
    # Pydantic not available - provide no-op validators
    class _MissingPydantic:
        def __getattr__(self, name: str) -> Any:
            raise ImportError(
                "pydantic v2 required for I/O validation. Install with: uv add pydantic"
            )

    validate_record_input = _MissingPydantic()  # type: ignore[assignment]
    validate_record_output = _MissingPydantic()  # type: ignore[assignment]
    ScheduleModel = _MissingPydantic  # type: ignore[assignment]
    ProvenanceModel = _MissingPydantic  # type: ignore[assignment]
    StatusModel = _MissingPydantic  # type: ignore[assignment]
    RecordInputModel = _MissingPydantic  # type: ignore[assignment]
    RecordOutputModel = _MissingPydantic  # type: ignore[assignment]


# A replication key is ``cell_key|fidelity|n_seeds|epochs|batch_limit|budget_id``
# (claims.replication_key); one SQL condition list and one formatter, so the
# store and the pure predicate cannot disagree about what a cell is.
_REPLICATION_COLUMNS: Final[str] = (
    "cell_key, schedule.fidelity, schedule.n_seeds, schedule.epochs, "
    "schedule.batch_limit, schedule.budget_id"
)
_REPLICATION_CONDITIONS: Final[tuple[str, ...]] = (
    "cell_key = ?",
    "schedule.fidelity = ?",
    "schedule.n_seeds = ?",
    "schedule.epochs = ?",
    "schedule.batch_limit = ?",
    "schedule.budget_id = ?",
)


def format_replication_key(parts: Sequence[object]) -> str:
    """Format a replication key from its six parts, in the canonical order."""
    return "|".join(str(part) for part in parts)


def _replication_predicate(replication_key: str) -> tuple[list[str], list[Any]]:
    """Split a replication key into its SQL conditions and bound parameters."""
    parts = replication_key.split("|")
    if len(parts) != 6:
        msg = f"malformed replication key: {replication_key!r}"
        raise StoreError(msg)
    return [*_REPLICATION_CONDITIONS], [
        parts[0],
        parts[1],
        int(parts[2]),
        int(parts[3]),
        int(parts[4]),
        parts[5],
    ]


__all__ = [
    "DuplicateMeasurementError",
    "ProvenanceModel",
    "RecordInputModel",
    "RecordOutputModel",
    "RecordStore",
    "RunInfo",
    "ScheduleModel",
    "StatusModel",
    "StoreConfig",
    "StoreError",
    "TableName",
    "TableSlice",
    "UnsupportedSchemaVersionError",
    "format_replication_key",
    "validate_record_input",
    "validate_record_output",
]
