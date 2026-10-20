"""Record serialization for API boundaries (TODO68).

Single source of truth for how Record objects are serialized to JSON for
the dashboard frontend. Eliminates duplicate logic between REST endpoints
and WebSocket broadcasts.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from computronium.experiment.schema.record import Record


def _serialize_schedule(schedule: Any) -> dict[str, Any]:
    """Serialize a Schedule to a dict."""
    return {
        "fidelity": schedule.fidelity,
        "seed": schedule.seed,
        "n_seeds": schedule.n_seeds,
        "epochs": schedule.epochs,
        "batch_limit": schedule.batch_limit,
        "budget_id": schedule.budget_id,
        "task_id": schedule.task_id,
        "param_budget": schedule.param_budget,
        "device": schedule.device,
        "deterministic": schedule.deterministic,
        "num_workers": schedule.num_workers,
        "precision": schedule.precision,
        "checkpoint_every_n": schedule.checkpoint_every_n,
    }


def _serialize_provenance(provenance: Any) -> dict[str, Any]:
    """Serialize Provenance to a dict."""
    return {
        "code_sha": provenance.code_sha,
        "policy": provenance.policy,
        "dataset": provenance.dataset,
        "dataset_version": provenance.dataset_version,
        "data_origin": provenance.data_origin.value,
        "env": provenance.env,
        "task_versions": provenance.task_versions,
        "hardware_hash": provenance.hardware_hash,
        "links": provenance.links,
    }


def _serialize_status(status: Any) -> dict[str, Any]:
    """Serialize Status to a dict."""
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


class RecordSerializer:
    """Single serialization point for Record objects across API boundaries.

    Usage:
        serializer = RecordSerializer()
        api_dict = serializer.to_api_dict(record)
    """

    def to_api_dict(self, record: Record) -> dict[str, Any]:
        """Convert a Record to an API-friendly dict."""
        return {
            "record_id": record.record_id,
            "seq": record.seq,
            "run_id": record.run_id,
            "schema_version": record.schema_version,
            "cell_key": record.cell_key,
            "measurement_key": record.measurement_key,
            "substrate": record.substrate,
            "geometry": record.geometry,
            "dynamics": record.dynamics,
            "plasticity": record.plasticity,
            "credit": record.credit,
            "update": record.update,
            "params": record.params,
            "effective_params": record.effective_params,
            "schedule": _serialize_schedule(record.schedule),
            "provenance": _serialize_provenance(record.provenance),
            "status": _serialize_status(record.status),
            "payload": record.payload,
            "unknown": record.unknown,
        }

    def to_minimal_dict(self, record: Record) -> dict[str, Any]:
        """Convert a Record to a minimal dict for list views."""
        return {
            "record_id": record.record_id,
            "run_id": record.run_id,
            "cell_key": record.cell_key,
            "coordinate": {
                "substrate": record.substrate,
                "geometry": record.geometry,
                "dynamics": record.dynamics,
                "plasticity": record.plasticity,
                "credit": record.credit,
                "update": record.update,
            },
            "schedule": {
                "fidelity": record.schedule.fidelity,
                "seed": record.schedule.seed,
                "n_seeds": record.schedule.n_seeds,
            },
            "status": {
                "gate_verdict": record.status.gate_verdict.value,
                "maturity": record.status.maturity.value,
            },
            "payload": record.payload,
        }


serializer = RecordSerializer()
