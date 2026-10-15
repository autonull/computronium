"""CEEC export for governed claims.

Exports StatisticalResult/claim-eligible records to the standalone CEEC ledger
(packages/ceec-core) and returns the CEEC link for recording in Status.ceec_link.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from computronium.experiment.evidence.claims import (
    claim_eligible,
    derive_claims,
)
from computronium.experiment.evidence.store import RecordStore
from computronium.experiment.schema.record import Record

logger = logging.getLogger(__name__)


def _get_ceec_ledger_path() -> tuple[Path | None, Path | None]:
    """Get the CEEC ledger path and artifacts dir from environment or default locations."""
    import os

    # Check environment variable first
    env_path = os.environ.get("CEEC_LEDGER_PATH")
    env_artifacts = os.environ.get("CEEC_ARTIFACTS_DIR")
    if env_path:
        path = Path(env_path)
        artifacts = Path(env_artifacts) if env_artifacts else path.parent / "artifacts"
        if path.exists():
            return path, artifacts

    # Check default locations
    default_paths = [
        (Path("ceec/ceec.sqlite3"), Path("ceec/artifacts")),
        (Path("scratch/ceec.sqlite3"), Path("scratch/artifacts")),
        (Path.home() / ".ceec" / "ceec.sqlite3", Path.home() / ".ceec" / "artifacts"),
    ]

    for db_path, artifacts_dir in default_paths:
        if db_path.exists():
            return db_path, artifacts_dir

    return None, None


def _ensure_ceec_available() -> bool:
    """Check if CEEC package is available."""
    try:
        from ceec.store import CEECStore  # ruff: ignore[unused-import]

        import ceec  # ruff: ignore[unused-import]

        return True
    except ImportError:
        logger.warning("CEEC package not available; ceec_link will not be populated")
        return False


def _record_to_scope(record: Record) -> dict[str, Any]:
    """Build a CEEC Scope from a computronium Record."""
    return {
        "domain": record.schedule.task_id or "unknown",
        "substrate": record.substrate,
        "geometry": record.geometry,
        "dynamics": record.dynamics,
        "plasticity": record.plasticity,
        "credit": record.credit,
        "update": record.update,
        "fidelity": record.schedule.fidelity,
        "n_seeds": record.schedule.n_seeds,
    }


def export_claims_to_ceec(
    store: RecordStore,
    run_id: str,
    *,
    ceec_ledger_path: Path | None = None,
    ceec_artifacts_dir: Path | None = None,
    min_seeds: int = 5,
    metrics: tuple[str, ...] = ("val_acc", "val_loss", "walltime_s"),
) -> str | None:
    """Export claim-eligible records from a run to the CEEC ledger.

    Args:
        store: The RecordStore containing the run's records.
        run_id: The run ID to export.
        ceec_ledger_path: Path to CEEC ledger (auto-detected if None).
        ceec_artifacts_dir: Path to CEEC artifacts dir (auto-detected if None).
        min_seeds: Minimum seeds for claim eligibility.
        metrics: Payload keys to derive claims from.

    Returns:
        CEEC belief ID (link) if successful, None if CEEC unavailable or no claims.
    """
    if not _ensure_ceec_available():
        return None

    # Resolve CEEC ledger path
    if ceec_ledger_path is None or ceec_artifacts_dir is None:
        detected_db, detected_artifacts = _get_ceec_ledger_path()
        if ceec_ledger_path is None:
            ceec_ledger_path = detected_db
        if ceec_artifacts_dir is None:
            ceec_artifacts_dir = detected_artifacts

    if ceec_ledger_path is None or ceec_artifacts_dir is None:
        logger.warning("CEEC ledger not found; skipping export")
        return None

    try:
        from ceec.store import CEECStore

        from ceec import models

        # Open CEEC store
        ceec_store = CEECStore(
            ceec_ledger_path,
            ceec_artifacts_dir,
        )
        ceec_store.__enter__()

        try:
            # Get claim-eligible records
            records = store.query_records(run_id=run_id)
            eligible_records = [r for r in records if claim_eligible(r)]

            if not eligible_records:
                logger.info("No claim-eligible records for run %s", run_id)
                return None

            # Derive claims
            claims = derive_claims(
                eligible_records, metrics=metrics, min_seeds=min_seeds
            )

            if not claims:
                logger.info("No claims derived for run %s", run_id)
                return None

            # Export each claim group as CEEC evidence
            evidence_ids = []
            for record in eligible_records:
                # Filter claims for this record's structural values
                cell_claims = [
                    c for c in claims if getattr(record, c.axis, None) == c.value
                ]

                if not cell_claims:
                    continue

                scope_dict = _record_to_scope(record)
                scope = models.Scope.of(**scope_dict)

                # Ingest artifact first (the raw record data as JSON)
                artifact = ceec_store.ingest_artifact(
                    source=json.dumps(record.to_dict(), indent=2, default=str).encode(),
                    type_="computronium_record",
                    provenance={
                        "run_id": run_id,
                        "record_id": record.record_id,
                        "cell_key": record.cell_key,
                        "source": "computronium",
                    },
                )

                # Build values_ref data
                values_ref_data = {}
                for claim in cell_claims:
                    values_ref_data[claim.axis] = {
                        "value": claim.value,
                        "mean": claim.mean,
                        "variance": claim.variance,
                        "n": claim.n,
                        "cells": claim.cells,
                    }

                # Record evidence referencing the artifact
                evidence = ceec_store.record_evidence(
                    kind="vector",
                    scope=scope,
                    artifact_refs=[artifact.id],
                    axes=[c.axis for c in cell_claims],
                    values_ref=json.dumps(values_ref_data),
                    uncertainties={
                        c.axis: {"mean": c.mean, "variance": c.variance, "n": c.n}
                        for c in cell_claims
                    },
                    quality={
                        "gate_verdict": record.status.gate_verdict.value,
                        "maturity": record.status.maturity.value,
                        "reproducibility": record.status.reproducibility.value,
                        "assessment_procedure_version": record.status.assessment_procedure_version,
                    },
                    defects=[record.status.defect] if record.status.defect else [],
                    notes=f"Computed from {len(cell_claims)} claims for {record.cell_key}",
                )

                evidence_ids.append(evidence.id)

            # Create a belief summarizing the run's findings
            if evidence_ids:
                # Use first record for scope
                first_record = eligible_records[0]
                belief_scope = models.Scope.of(
                    domain=first_record.schedule.task_id or "unknown",
                    run_id=run_id,
                )
                belief = ceec_store.create_belief(
                    statement=f"Run {run_id} produced {len(evidence_ids)} claim-eligible cells with governed evidence",
                    type_="mechanism",
                    scope=belief_scope,
                    evidence_refs=evidence_ids,
                )
                # Return the belief ID as the ceec_link
                return belief.id

            return None

        finally:
            ceec_store.__exit__(None, None, None)

    except Exception as e:
        logger.exception("Failed to export to CEEC: %s", e)
        return None


def export_statistical_result_to_ceec(
    store: RecordStore,
    run_id: str,
    *,
    ceec_ledger_path: Path | None = None,
    ceec_artifacts_dir: Path | None = None,
) -> str | None:
    """Export statistical results (promoted records) to CEEC.

    This creates a CEEC Experiment and links the statistical evidence
    through the gate process.

    Returns:
        CEEC experiment ID as the ceec_link.
    """
    if not _ensure_ceec_available():
        return None

    if ceec_ledger_path is None or ceec_artifacts_dir is None:
        detected_db, detected_artifacts = _get_ceec_ledger_path()
        if ceec_ledger_path is None:
            ceec_ledger_path = detected_db
        if ceec_artifacts_dir is None:
            ceec_artifacts_dir = detected_artifacts

    if ceec_ledger_path is None or ceec_artifacts_dir is None:
        logger.warning("CEEC ledger not found; skipping export")
        return None

    try:
        from ceec.builders import experiment, quality_flags
        from ceec.store import CEECStore

        from ceec import models

        # Get promoted records
        records = store.query_records(run_id=run_id)
        promoted_records = [r for r in records if r.status.maturity.value == "l2"]

        if not promoted_records:
            logger.info("No promoted (L2) records for run %s", run_id)
            return None

        # Open CEEC store
        ceec_store = CEECStore(
            ceec_ledger_path,
            ceec_artifacts_dir,
        )
        ceec_store.__enter__()

        try:
            # Create experiment payload for this run
            task_id = promoted_records[0].schedule.task_id or "unknown"
            exp_id = f"X-{run_id}_{task_id}_statistical"
            scope = models.Scope.of(domain=task_id, run_id=run_id)

            exp = experiment(
                id_=exp_id,
                question=f"Do the promoted cells in run {run_id} on task {task_id} show measurable effects?",
                prediction="Promoted cells show statistically significant effects",
                scope=scope,
                rationale="Export from computronium experiment kernel",
                design={
                    "source": "computronium",
                    "run_id": run_id,
                    "n_promoted": len(promoted_records),
                },
                controls=["same_hardware", "same_budget", "same_seeds"],
                metrics=["validation_accuracy", "walltime_total", "param_count"],
                budget="medium",
                falsification_criterion="No promoted cell beats baseline",
                overturn_criterion="New evidence contradicts promoted findings",
                hard_gates=["statistical_significance", "reproducibility"],
            )

            # Pre-register experiment
            registered = ceec_store.pre_register_experiment(exp)
            ceec_store.set_experiment_status(registered.id, "running")

            # Export each promoted record as evidence
            evidence_ids = []
            for record in promoted_records:
                # Ingest record as artifact
                artifact = ceec_store.ingest_artifact(
                    source=json.dumps(record.to_dict(), indent=2, default=str).encode(),
                    type_="computronium_promoted_record",
                    provenance={
                        "run_id": run_id,
                        "record_id": record.record_id,
                        "cell_key": record.cell_key,
                    },
                )

                scope = models.Scope.of(**_record_to_scope(record))

                evidence = ceec_store.record_evidence(
                    kind="vector",
                    scope=scope,
                    artifact_refs=[artifact.id],
                    axes=[
                        "substrate",
                        "geometry",
                        "dynamics",
                        "plasticity",
                        "credit",
                        "update",
                    ],
                    values_ref=json.dumps({
                        "substrate": record.substrate,
                        "geometry": record.geometry,
                        "dynamics": record.dynamics,
                        "plasticity": record.plasticity,
                        "credit": record.credit,
                        "update": record.update,
                    }),
                    uncertainties=record.status.uncertainty,
                    quality=quality_flags(
                        seeds=record.schedule.n_seeds,
                        matched_control=True,
                        evaluation_policy="statistical_promotion",
                        defect_audit="pass",
                        integrity_checks="pass",
                    ),
                    defects=[record.status.defect] if record.status.defect else [],
                    notes=f"Promoted cell {record.cell_key} from run {run_id}",
                )
                evidence_ids.append(evidence.id)

            # Link evidence to experiment via a belief
            if evidence_ids:
                belief = ceec_store.create_belief(
                    statement=f"Promoted cells in run {run_id} demonstrate measurable effects on {task_id}",
                    type_="mechanism",
                    scope=scope,
                    evidence_refs=evidence_ids,
                )

                # Update experiment status
                ceec_store.set_experiment_status(registered.id, "completed")

                # Return experiment ID as ceec_link
                return registered.id

            return None

        finally:
            ceec_store.__exit__(None, None, None)

    except Exception as e:
        logger.exception("Failed to export statistical result to CEEC: %s", e)
        return None


__all__ = [
    "export_claims_to_ceec",
    "export_statistical_result_to_ceec",
]
