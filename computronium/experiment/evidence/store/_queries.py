"""Read models, counts, snapshots and vector-independent queries."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any, Literal

from computronium.experiment.schema.coordinate import Provenance, Schedule
from computronium.experiment.schema.record import (
    FailureCause,
    GateVerdict,
    Maturity,
    Record,
    ReproducibilityClass,
    Severity,
    Status,
)
from computronium.experiment.schema.registries import procedure_version_key
from computronium.experiment.schema.run_spec import RunSpec

from ._base import _StoreBase
from ._models import (
    _REPLICATION_COLUMNS,
    DuplicateMeasurementError,
    RunInfo,
    StoreError,
    TableName,
    TableSlice,
    UnsupportedSchemaVersionError,
    _replication_predicate,
    format_replication_key,
)

if TYPE_CHECKING:
    from computronium.experiment.schema.axis import StructuralAxis


def _assessed_at_least(records: list[Record], version: str | None) -> list[Record]:
    """The records assessed by ``version`` or a later procedure; all, if ``None``.

    A record's procedure version is what a record *means*, so a campaign that
    changed the meaning keeps the old measurements visible through this filter
    instead of averaging them with the new ones (TODO48 F4).
    """
    if version is None:
        return records
    floor = procedure_version_key(version)
    return [
        record
        for record in records
        if procedure_version_key(record.status.assessment_procedure_version) >= floor
    ]


logger = logging.getLogger(__name__)


class _QueryMixin(_StoreBase):
    _conn: Any

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
        min_assessment_procedure_version: str | None = None,
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
            min_assessment_procedure_version: Keep only records assessed by this
                procedure version or later. Versions are compared numerically, so
                ``1.10`` is newer than ``1.9`` — which a string comparison gets
                backwards — and the filter runs in Python for that reason (TODO48 F4).
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
        records = [self._row_to_record(row) for row in rows]
        return _assessed_at_least(records, min_assessment_procedure_version)

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
        fidelity: str | None = "L2",
    ) -> tuple[str, ...]:
        """Replication keys that *achieved* ``min_n_seeds`` distinct passing seeds.

        Claim eligibility is a property of a cell, not of one of its seeds: the
        executor writes one record per seed with ``schedule.n_seeds == 1``, so
        no record-level filter can answer it. One grouped query, so the answer
        costs one round trip rather than one per cell.
        """
        if self._conn is None:
            raise StoreError("Connection not initialized")
        conditions = ["status.gate_verdict = ?"]
        params: list[Any] = [GateVerdict.PASS_.value]
        if fidelity is not None:
            conditions.append("schedule.fidelity = ?")
            params.append(fidelity)
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
        params = json.loads(row[12])
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
            params=params,
            schedule=schedule,
            provenance=provenance,
            status=status,
            payload=json.loads(row[16]),
            unknown=json.loads(row[17]) if row[17] else None,
            effective_params=json.loads(row[18])
            if len(row) > 18 and row[18]
            else params,
        )

    def _parse_schedule(self, schedule_struct: dict[str, Any]) -> Schedule:
        """Parse schedule from database struct."""
        device = schedule_struct.get("device", "auto")
        if device is None:
            device = "auto"
        return Schedule(
            fidelity=schedule_struct["fidelity"],
            seed=schedule_struct["seed"],
            n_seeds=schedule_struct["n_seeds"],
            epochs=schedule_struct["epochs"],
            batch_limit=schedule_struct["batch_limit"],
            budget_id=schedule_struct["budget_id"],
            task_id=schedule_struct["task_id"],
            # Rows written before the ceiling existed declare none.
            param_budget=schedule_struct.get("param_budget", 0) or 0,
            device=device,
            deterministic=schedule_struct.get("deterministic", False) or False,
            num_workers=schedule_struct.get("num_workers", 0) or 0,
            precision=schedule_struct.get("precision", "fp32") or "fp32",
            checkpoint_every_n=schedule_struct.get("checkpoint_every_n", 0) or 0,
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

    def count_records_by_run(self) -> dict[str, int]:
        """Count records grouped by run_id in a single query."""
        if self._conn is None:
            raise StoreError("Connection not initialized")
        rows = self._conn.execute(
            "SELECT run_id, COUNT(*) FROM records GROUP BY run_id"
        ).fetchall()
        return {row[0]: row[1] for row in rows}

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
        where_clause = f" WHERE {' AND '.join(conditions)}" if conditions else ""  # ruff: ignore[hardcoded-sql-expression] - static fragment, parameterized values
        limit_clause = f" LIMIT {int(limit)}" if limit else ""  # ruff: ignore[hardcoded-sql-expression] - int-coerced
        rows = self._conn.execute(
            f"SELECT run_id, spec, spec_version, status, budget_consumed_s, "  # ruff: ignore[hardcoded-sql-expression] - static column list
            f"replay_hash, started_at, finished_at, last_heartbeat FROM runs{where_clause} "
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
                last_heartbeat=row[8],
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
            params,  # ruff: ignore[hardcoded-sql-expression] - parameterized, static conditions
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

    def _import_runs(self, runs_data: list[dict[str, Any]]) -> None:
        """Import runs from snapshot data."""
        if self._conn is None:
            raise StoreError("Connection not initialized")

        for run_data in runs_data:
            run_id = run_data["run_id"]
            existing = self._conn.execute(
                "SELECT run_id FROM runs WHERE run_id = ?", [run_id]
            ).fetchone()
            if existing is None:
                spec_dict = run_data.get("spec")
                spec = RunSpec.from_dict(spec_dict) if spec_dict else None
                spec_json = json.dumps(spec.to_dict()) if spec else None
                self._conn.execute(
                    """
                    INSERT INTO runs (
                        run_id, spec, spec_version, status, started_at,
                        finished_at, budget_consumed_s, replay_hash, last_heartbeat
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        run_id,
                        spec_json,
                        run_data["spec_version"],
                        run_data["status"],
                        run_data["started_at"],
                        run_data.get("finished_at"),
                        run_data.get("budget_consumed_s"),
                        run_data.get("replay_hash"),
                        run_data.get("last_heartbeat"),
                    ],
                )

    def _import_records(self, records_data: list[dict[str, Any]]) -> int:
        """Import records from snapshot data. Returns count imported."""
        from computronium.experiment.schema.record import Record

        imported = 0
        for record_data in records_data:
            record = Record.from_dict(record_data)
            try:
                self.append(record)
                imported += 1
            except DuplicateMeasurementError:
                logger.debug(
                    "Skipping duplicate record: %s", record.measurement_key[:12]
                )
            except Exception as e:
                logger.warning(
                    "Failed to import record %s: %s", record.measurement_key[:12], e
                )
        return imported

    def import_snapshot(self, snapshot: dict[str, Any]) -> int:
        """Import a snapshot exported by ``export_snapshot``.

        Args:
            snapshot: Dictionary with keys "records", "runs", "artifacts",
                "vector_index" as returned by ``export_snapshot``.

        Returns:
            Number of records imported.

        Note:
            This method does not import artifact bytes (they are not included
            in the exported snapshot). Artifact manifests are imported with
            their external references intact.
        """
        if self._conn is None:
            raise StoreError("Connection not initialized")
        if self._config.read_only:
            raise StoreError("Cannot import into read-only store")

        with self._write_lock:
            self._import_runs(snapshot.get("runs", []))
            imported = self._import_records(snapshot.get("records", []))
            self._import_artifacts(snapshot.get("artifacts", []))
            self._import_vector_index(snapshot.get("vector_index", []))

        return imported
