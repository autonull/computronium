"""Schema creation and presence checks for the evidence store."""

from __future__ import annotations

import time

import duckdb

from ._base import _SCHEMA_INIT_ATTEMPTS, _SCHEMA_INIT_BACKOFF_S, _StoreBase
from ._models import StoreError


class _SchemaMixin(_StoreBase):
    _conn: duckdb.DuckDBPyConnection | None

    def _schema_present(self) -> bool:
        """Whether the store already carries the whole schema.

        A second connection to a store that already has it must not re-run the
        DDL: two connections creating the same sequence is a catalog
        write-write conflict, and the reader of a live campaign is exactly
        that second connection.
        """
        if self._conn is None:
            return False
        row = self._conn.execute(
            "SELECT count(*) FROM information_schema.tables "
            "WHERE table_name IN "
            "('runs', 'records', 'artifacts', 'vector_index', 'checkpoints')"
        ).fetchone()
        return bool(row) and int(row[0]) == 5

    def _init_schema(self) -> None:
        """Initialize the database schema.

        Two connections to a fresh store race to create it, and the loser
        gets a catalog write-write conflict on the sequence. Every statement
        is ``IF NOT EXISTS``, so retrying converges: whatever the winner
        created is already there, and the loser's statements become no-ops.
        """
        if self._conn is None:
            raise StoreError("Connection not initialized")

        for attempt in range(_SCHEMA_INIT_ATTEMPTS):
            try:
                self._create_schema_objects()
            except duckdb.Error:
                if self._schema_present():
                    return
                if attempt == _SCHEMA_INIT_ATTEMPTS - 1:
                    raise
                time.sleep(_SCHEMA_INIT_BACKOFF_S * (attempt + 1))
            else:
                return

    def _create_schema_objects(self) -> None:
        """Create every table, sequence and index the store needs."""
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
                finished_at       TIMESTAMP,
                last_heartbeat    TIMESTAMP
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
                                        task_id TEXT, param_budget INTEGER, device TEXT,
                                        deterministic BOOLEAN, num_workers INTEGER,
                                        precision TEXT, checkpoint_every_n INTEGER,
                                        distributed_backend TEXT, ddp_backend TEXT,
                                        fsdp_sharding_strategy TEXT, fsdp_min_params INTEGER,
                                        fsdp_cpu_offload BOOLEAN, fsdp_mixed_precision BOOLEAN) NOT NULL,
                provenance      JSON NOT NULL,
                status          STRUCT(gate_verdict TEXT, defect TEXT, cause TEXT, severity TEXT,
                                        quarantine BOOLEAN, maturity TEXT, uncertainty JSON,
                                        reproducibility TEXT, assessment_procedure_version TEXT,
                                        ceec_link TEXT) NOT NULL,
                payload         JSON NOT NULL,
                unknown         JSON,
                effective_params JSON NOT NULL DEFAULT '{}',
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

        # Checkpoints table (for SIGTERM-aware resume)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                run_id           TEXT PRIMARY KEY REFERENCES runs(run_id),
                checkpoint_data  JSON NOT NULL,
                created_at       TIMESTAMP NOT NULL
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
