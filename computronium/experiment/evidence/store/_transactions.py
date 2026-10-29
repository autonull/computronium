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
        if self._conn is None:
            raise StoreError("Connection not initialized")
        # DuckDB refuses a qualified SET target, so the struct is rebuilt: the
        # earned fields change, every other field is carried through unchanged.
        reproducibility_sql = "?" if reproducibility else "status.reproducibility"
        with self._write_lock:
            result = self._conn.execute(
                "UPDATE records SET status = {"
                "'gate_verdict': status.gate_verdict, 'defect': status.defect, "
                "'cause': status.cause, 'severity': status.severity, "
                "'quarantine': status.quarantine, 'maturity': ?, "
                "'uncertainty': status.uncertainty, "
                f"'reproducibility': {reproducibility_sql}, "
                "'assessment_procedure_version': "
                "status.assessment_procedure_version, "
                "'ceec_link': status.ceec_link} "
                "WHERE run_id = ? AND cell_key = ?",
                [
                    maturity.value,
                    *([reproducibility.value] if reproducibility else []),
                    run_id,
                    cell_key,
                ],
            )
        return len(result.fetchall())

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
        if self._conn is None:
            raise StoreError("Connection not initialized")
        # DuckDB refuses a qualified SET target, so the struct is rebuilt.
        import json

        uncertainty_json = json.dumps(uncertainty)
        with self._write_lock:
            result = self._conn.execute(
                "UPDATE records SET status = {"
                "'gate_verdict': status.gate_verdict, 'defect': status.defect, "
                "'cause': status.cause, 'severity': status.severity, "
                "'quarantine': status.quarantine, 'maturity': status.maturity, "
                "'uncertainty': ?, "
                "'reproducibility': status.reproducibility, "
                "'assessment_procedure_version': "
                "status.assessment_procedure_version, "
                "'ceec_link': status.ceec_link} "
                "WHERE run_id = ? AND cell_key = ?",
                [
                    uncertainty_json,
                    run_id,
                    cell_key,
                ],
            )
        return len(result.fetchall())

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
        if self._conn is None:
            raise StoreError("Connection not initialized")
        with self._write_lock:
            result = self._conn.execute(
                "UPDATE records SET status = {"
                "'gate_verdict': status.gate_verdict, 'defect': status.defect, "
                "'cause': status.cause, 'severity': status.severity, "
                "'quarantine': status.quarantine, 'maturity': status.maturity, "
                "'uncertainty': status.uncertainty, "
                "'reproducibility': status.reproducibility, "
                "'assessment_procedure_version': "
                "status.assessment_procedure_version, "
                "'ceec_link': ?} "
                "WHERE run_id = ? AND cell_key = ?",
                [ceec_link, run_id, cell_key],
            )
        return len(result.fetchall())

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

    def append(self, record: Record) -> Record:
        """Append a record to the store. Returns record with assigned seq.

        Raises DuplicateMeasurementError if measurement_key already exists.
        Raises ValueError if record provenance is incomplete.
        """
        if self._conn is None:
            raise StoreError("Connection not initialized")

        # Validate provenance before write
        self._validate_record_provenance(record)

        with self._write_lock:
            try:
                # Insert record - seq is assigned by DEFAULT nextval('record_seq')
                self._conn.execute(
                    """
                    INSERT INTO records (
                        record_id, run_id, schema_version, cell_key, measurement_key,
                        substrate, geometry, dynamics, plasticity, credit, update,
                        params, schedule, provenance, status, payload, unknown,
                        effective_params
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                        json.dumps(record.schedule.to_dict()),
                        json.dumps(record.provenance.to_dict()),
                        json.dumps({
                            "gate_verdict": record.status.gate_verdict.value,
                            "defect": record.status.defect,
                            "cause": record.status.cause.value,
                            "severity": record.status.severity.value,
                            "quarantine": record.status.quarantine,
                            "maturity": record.status.maturity.value,
                            "uncertainty": record.status.uncertainty,
                            "reproducibility": record.status.reproducibility.value,
                            "assessment_procedure_version": record.status.assessment_procedure_version,
                            "ceec_link": record.status.ceec_link,
                        }),
                        json.dumps(record.payload),
                        json.dumps(record.unknown) if record.unknown else None,
                        json.dumps(record.effective_params),
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

            # A reader in another process cannot open this store: publish the
            # picture for it.
            self._publish_mirror()

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
                effective_params=record.effective_params,
                schedule=record.schedule,
                provenance=record.provenance,
                status=record.status,
                payload=record.payload,
                unknown=record.unknown,
            )

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
