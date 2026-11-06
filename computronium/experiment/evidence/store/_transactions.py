"""Run lifecycle, checkpoints and record writes for the evidence store."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

import duckdb

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
from computronium.experiment.schema.run_spec import RunSpec

from ._base import _StoreBase
from ._models import DuplicateMeasurementError, StoreError


class _TransactionMixin(_StoreBase):
    _conn: duckdb.DuckDBPyConnection | None
    _write_lock: Any

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

    def update_run_spec(self, run_id: str, spec: RunSpec) -> None:
        """Record the declaration a continuing run now runs under.

        A run that is continued under a larger seed plan has a different
        declaration, and the store is where a reader finds it: the persisted
        spec is the run's, not the launch's.

        Raises:
            StoreError: The connection is closed or the run is unknown.
        """
        if self._conn is None:
            raise StoreError("Connection not initialized")
        with self._write_lock:
            updated = self._conn.execute(
                "UPDATE runs SET spec = ?, spec_version = ? WHERE run_id = ? "
                "RETURNING run_id",
                [json.dumps(spec.to_dict()), spec.version, run_id],
            ).fetchall()
            if not updated:
                msg = f"run {run_id} is not in the store"
                raise StoreError(msg)

    def set_replay_hash(self, run_id: str, replay_hash: str) -> None:
        """Record the replay hash a run computed when it finished measuring."""
        if self._conn is None:
            raise StoreError("Connection not initialized")
        with self._write_lock:
            self._conn.execute(
                "UPDATE runs SET replay_hash = ? WHERE run_id = ?",
                [replay_hash, run_id],
            )

    def update_heartbeat(self, run_id: str) -> None:
        """Update the run's last heartbeat timestamp."""
        if self._conn is None:
            raise StoreError("Connection not initialized")
        with self._write_lock:
            self._conn.execute(
                "UPDATE runs SET last_heartbeat = ? WHERE run_id = ?",
                [datetime.now(), run_id],
            )

    def _update_status_field(
        self,
        run_id: str,
        cell_key: str,
        field: str,
        value: Any,
    ) -> int:
        """Update a single field in the status struct for all records of a cell.

        DuckDB refuses a qualified SET target, so the struct is rebuilt with
        the specified field changed and all others carried through unchanged.

        Args:
            run_id: The run identifier.
            cell_key: The cell key.
            field: The status field to update (e.g., 'maturity', 'uncertainty', 'ceec_link', 'reproducibility').
            value: The new value for the field (will be JSON-serialized if dict/list).

        Returns:
            Number of records updated.
        """
        if self._conn is None:
            raise StoreError("Connection not initialized")

        # Serialize value if it's a dict/list
        import json

        if isinstance(value, dict | list):
            serialized_value = json.dumps(value)
        else:
            serialized_value = value

        # Build the SET clause carrying through all other fields
        set_clause = (
            "UPDATE records SET status = {"
            "'gate_verdict': status.gate_verdict, 'defect': status.defect, "
            "'cause': status.cause, 'severity': status.severity, "
            "'quarantine': status.quarantine, 'maturity': status.maturity, "
            "'uncertainty': status.uncertainty, "
            "'reproducibility': status.reproducibility, "
            "'assessment_procedure_version': "
            "status.assessment_procedure_version, "
            "'ceec_link': status.ceec_link} "
        )
        # Replace the target field
        set_clause = set_clause.replace(
            f"'{field}': status.{field}",
            f"'{field}': ?",
        )

        with self._write_lock:
            result = self._conn.execute(
                set_clause + "WHERE run_id = ? AND cell_key = ?",
                [serialized_value, run_id, cell_key],
            )
        return len(result.fetchall())

    def set_cell_maturity(
        self,
        run_id: str,
        cell_key: str,
        maturity: Maturity,
        reproducibility: ReproducibilityClass | None = None,
    ) -> int:
        """Write one status.maturity for every record of a cell.

        The promotion stage is the only writer; a maturity the store did not
        earn is a claim the store cannot back. A replay-verdict upgrade also
        writes the reproducibility class the verdict measured.
        """
        updated = self._update_status_field(
            run_id, cell_key, "maturity", maturity.value
        )
        if reproducibility is not None:
            self._update_status_field(
                run_id, cell_key, "reproducibility", reproducibility.value
            )
        return updated

    def set_cell_uncertainty(
        self,
        run_id: str,
        cell_key: str,
        uncertainty: dict[str, Any],
    ) -> int:
        """Write uncertainty for every record of a cell.

        The uncertainty is computed from across-seed measurements and stored
        in the status struct. This is the E1 implementation: uncertainty is
        a measurement, not {}.
        """
        return self._update_status_field(run_id, cell_key, "uncertainty", uncertainty)

    def set_cell_ceec_link(
        self,
        run_id: str,
        cell_key: str,
        ceec_link: str | None,
    ) -> int:
        """Write ``status.ceec_link`` for every record of a cell.

        The CEEC export is the only writer: a link a record cannot resolve in
        the governed ledger is worse than no link. Called after a belief is
        created so the record and the ledger agree on the claim's identity.
        """
        return self._update_status_field(run_id, cell_key, "ceec_link", ceec_link)

    def finish_run(
        self,
        run_id: str,
        status: str,
        budget_consumed_s: float | None = None,
        replay_hash: str | None = None,
    ) -> None:
        """Mark a run as finished.

        A ``replay_hash`` already written is preserved: the hash is written when
        the run completes, and a later status update that knows nothing about it
        must not erase the only record of what the run measured.
        """
        if self._conn is None:
            raise StoreError("Connection not initialized")
        with self._write_lock:
            self._conn.execute(
                """
                UPDATE runs SET status = ?, budget_consumed_s = ?,
                    replay_hash = COALESCE(?, replay_hash), finished_at = ?
                WHERE run_id = ?
                """,
                [status, budget_consumed_s, replay_hash, datetime.now(), run_id],
            )

    def save_checkpoint(self, run_id: str, checkpoint_data: dict[str, Any]) -> None:
        """Save a pipeline checkpoint for SIGTERM-aware resume.

        Args:
            run_id: The run identifier
            checkpoint_data: Serializable checkpoint data (from CheckpointData)
        """
        if self._conn is None:
            raise StoreError("Connection not initialized")
        with self._write_lock:
            self._conn.execute(
                """
                INSERT INTO checkpoints (run_id, checkpoint_data, created_at)
                VALUES (?, ?, ?)
                ON CONFLICT (run_id) DO UPDATE SET
                    checkpoint_data = excluded.checkpoint_data,
                    created_at = excluded.created_at
                """,
                [run_id, json.dumps(checkpoint_data), datetime.now()],
            )

    def load_checkpoint(self, run_id: str) -> dict[str, Any] | None:
        """Load a pipeline checkpoint for resume.

        Args:
            run_id: The run identifier

        Returns:
            Checkpoint data dict, or None if no checkpoint exists
        """
        if self._conn is None:
            raise StoreError("Connection not initialized")
        row = self._conn.execute(
            "SELECT checkpoint_data FROM checkpoints WHERE run_id = ?", [run_id]
        ).fetchone()
        if row is None:
            return None
        return json.loads(row[0])

    def delete_checkpoint(self, run_id: str) -> None:
        """Delete a checkpoint after successful completion."""
        if self._conn is None:
            raise StoreError("Connection not initialized")
        with self._write_lock:
            self._conn.execute("DELETE FROM checkpoints WHERE run_id = ?", [run_id])

    def _serialize_status(self, status) -> dict[str, Any]:
        """Serialize a Status object to a dict for DuckDB storage."""
        return {
            "gate_verdict": status.gate_verdict.value,
            "defect": status.defect,
            "cause": status.cause.value,
            "severity": status.severity.value,
            "quarantine": status.quarantine,
            "maturity": status.maturity.value,
            "uncertainty": status.uncertainty,
            "reproducibility": status.reproducibility.value,
            "assessment_procedure_version": status.assessment_procedure_version,
            "ceec_link": status.ceec_link,
        }

    def _dedup_key(self, record: Record) -> tuple[str, int, str]:
        """Compute the deduplication key: (cell_key, seed, fidelity).

        This key identifies a unique cell measurement across runs/rounds,
        ignoring budget_id which differs across rounds.
        """
        return (record.cell_key, record.schedule.seed, record.schedule.fidelity)

    def _build_insert_values(self, record: Record) -> list:
        """Build the VALUES list for INSERT statement from a Record."""
        return [
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
            record.schedule.to_dict(),
            json.dumps(record.provenance.to_dict()),
            self._serialize_status(record.status),
            json.dumps(record.payload),
            json.dumps(record.unknown) if record.unknown else None,
            json.dumps(record.effective_params),
        ]

    def append(self, record: Record) -> Record:
        """Upsert a record on (cell_key, seed, fidelity) composite key.

        Keeps the latest record (highest maturity/epochs) for the same
        cell_key+seed+fidelity within a run. This deduplicates across rounds
        where budget_id differs but the structural identity is the same.

        Returns the stored record with assigned seq.
        """
        return self.append_batch([record])[0]

    def append_batch(self, records: list[Record]) -> list[Record]:
        """Upsert multiple records in a single transaction.

        Buffers 10-50 records per transaction for throughput. Each record is
        upserted on (cell_key, seed, fidelity) composite key, keeping the
        latest record for the same cell_key+seed+fidelity within a run.

        Args:
            records: List of records to append. Must not be empty.

        Returns:
            List of stored records with assigned seq, in the same order.
        """
        if not records:
            raise ValueError("append_batch requires at least one record")
        if self._conn is None:
            raise StoreError("Connection not initialized")

        # Validate provenance before write
        for record in records:
            self._validate_record_provenance(record)

        with self._write_lock:
            results = []
            for record in records:
                # Check for existing record with same dedup key
                cell_key, seed, fidelity = self._dedup_key(record)
                row = self._conn.execute(
                    """
                    SELECT record_id FROM records
                    WHERE run_id = ? AND cell_key = ?
                      AND CAST(schedule.seed AS INTEGER) = ?
                      AND CAST(schedule.fidelity AS TEXT) = ?
                    ORDER BY seq DESC
                    LIMIT 1
                    """,
                    [record.run_id, cell_key, seed, fidelity],
                ).fetchone()
                if row:
                    # Upsert: delete old, insert new (keeps latest)
                    self._conn.execute("DELETE FROM records WHERE record_id = ?", [row[0]])

                # Insert record - seq is assigned by DEFAULT nextval('record_seq')
                try:
                    self._conn.execute(
                        """
                        INSERT INTO records (
                            record_id, run_id, schema_version, cell_key, measurement_key,
                            substrate, geometry, dynamics, plasticity, credit, update,
                            params, schedule, provenance, status, payload, unknown,
                            effective_params
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        self._build_insert_values(record),
                    )
                except duckdb.ConstraintException as e:
                    if "record_id" in str(e):
                        raise DuplicateMeasurementError(record.measurement_key) from e
                    raise StoreError(f"Constraint violation: {e}") from e

                # Fetch the assigned seq
                result = self._conn.execute(
                    "SELECT seq FROM records WHERE record_id = ?", [record.record_id]
                ).fetchone()

                if result is None:
                    raise StoreError("Failed to retrieve seq after insert")

                # Create new record with assigned seq, preserving original objects
                results.append(
                    Record(
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
                        effective_params=record.effective_params,
                        schedule=record.schedule,
                        provenance=record.provenance,
                        status=record.status,
                        payload=record.payload,
                        unknown=record.unknown,
                    )
                )

            # A reader in another process cannot open this store: publish the
            # picture for it.
            self._publish_mirror()

            return results

    def record_intent(self, run_id: str, intent: dict[str, Any]) -> Record:
        """Persist an operator intent as a run-linked record (R84, L13).

        Payload kind is ``operator_intent``; uniqueness derives from
        ``intent_id`` via ``schedule.task_id``, so redelivery dedups through
        the single writer like any other measurement.
        """
        from computronium.experiment.environment import environment_variables
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
                env=environment_variables(),
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
