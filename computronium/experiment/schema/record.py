"""Record specification for experiment results."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, fields
from enum import StrEnum
from typing import Any

from computronium.experiment.schema.coordinate import Coordinate, Provenance, Schedule


def _canonical_json(obj: Any) -> str:
    """Serialize to canonical JSON for hashing."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class GateVerdict(StrEnum):
    """Gate verdict for experiment status."""

    PASS_ = "PASS"  # noqa: S105
    FAIL = "FAIL"
    QUARANTINE = "QUARANTINE"
    PENDING = "PENDING"


class FailureCause(StrEnum):
    """Failure cause taxonomy."""

    UNKNOWN = "unknown"
    NUMERICAL = "numerical"
    TIMEOUT = "timeout"
    OOM = "oom"
    INVALID_CONFIG = "invalid_config"
    RUNTIME_ERROR = "runtime_error"
    CONSTRAINT_VIOLATION = "constraint_violation"
    DIVERGENCE = "divergence"


class Severity(StrEnum):
    """Severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Maturity(StrEnum):
    """Maturity levels for experiment records."""

    L0 = "l0"  # Initial mapping
    L1 = "l1"  # Verified
    L2 = "l2"  # Claim-grade


@dataclass(frozen=True, slots=True)
class Status:
    """Primary status fields for an experiment record."""

    gate_verdict: GateVerdict
    defect: str
    cause: FailureCause
    severity: Severity
    quarantine: bool
    maturity: Maturity
    uncertainty: dict[str, Any]
    reproducibility: str
    ceec_link: str | None

    def __post_init__(self) -> None:
        if not isinstance(self.gate_verdict, GateVerdict):
            raise TypeError(
                f"gate_verdict must be GateVerdict, got {type(self.gate_verdict)}"
            )
        if not isinstance(self.cause, FailureCause):
            raise TypeError(f"cause must be FailureCause, got {type(self.cause)}")
        if not isinstance(self.severity, Severity):
            raise TypeError(f"severity must be Severity, got {type(self.severity)}")
        if not isinstance(self.maturity, Maturity):
            raise TypeError(f"maturity must be Maturity, got {type(self.maturity)}")


@dataclass(frozen=True, slots=True)
class Record:
    """Complete experiment record."""

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
    schedule: Schedule
    provenance: Provenance
    status: Status
    payload: dict[str, Any]
    unknown: dict[str, Any] | None

    def __post_init__(self) -> None:
        for field in fields(self):
            value = getattr(self, field.name)
            if (
                field.name in {"params", "payload", "unknown"}
                and value is not None
                and not isinstance(value, dict)
            ):
                raise TypeError(f"Record.{field.name} must be dict or None")
            if field.name == "schedule" and not isinstance(value, Schedule):
                raise TypeError("Record.schedule must be Schedule")
            if field.name == "provenance" and not isinstance(value, Provenance):
                raise TypeError("Record.provenance must be Provenance")
            if field.name == "status" and not isinstance(value, Status):
                raise TypeError("Record.status must be Status")

    @classmethod
    def create(
        cls,
        run_id: str,
        coordinate: Coordinate,
        schedule: Schedule,
        provenance: Provenance,
        status: Status,
        payload: dict[str, Any],
        unknown: dict[str, Any] | None = None,
        schema_version: int = 1,
    ) -> Record:
        """Create a new record with computed identity keys."""
        cell_key = coordinate.cell_key()
        measurement_key = coordinate.measurement_key(schedule)
        record_id = hashlib.sha256(
            _canonical_json({
                "run_id": run_id,
                "cell_key": cell_key,
                "measurement_key": measurement_key,
            }).encode()
        ).hexdigest()

        return cls(
            record_id=record_id,
            seq=0,  # Assigned by store on append
            run_id=run_id,
            schema_version=schema_version,
            cell_key=cell_key,
            measurement_key=measurement_key,
            substrate=coordinate.substrate,
            geometry=coordinate.geometry,
            dynamics=coordinate.dynamics,
            plasticity=coordinate.plasticity,
            credit=coordinate.credit,
            update=coordinate.update,
            params=coordinate.params,
            schedule=schedule,
            provenance=provenance,
            status=status,
            payload=payload,
            unknown=unknown,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "record_id": self.record_id,
            "seq": self.seq,
            "run_id": self.run_id,
            "schema_version": self.schema_version,
            "cell_key": self.cell_key,
            "measurement_key": self.measurement_key,
            "substrate": self.substrate,
            "geometry": self.geometry,
            "dynamics": self.dynamics,
            "plasticity": self.plasticity,
            "credit": self.credit,
            "update": self.update,
            "params": self.params,
            "schedule": self.schedule.to_dict(),
            "provenance": self.provenance.to_dict(),
            "status": {
                "gate_verdict": self.status.gate_verdict.value,
                "defect": self.status.defect,
                "cause": self.status.cause.value,
                "severity": self.status.severity.value,
                "quarantine": self.status.quarantine,
                "maturity": self.status.maturity.value,
                "uncertainty": self.status.uncertainty,
                "reproducibility": self.status.reproducibility,
                "ceec_link": self.status.ceec_link,
            },
            "payload": self.payload,
            "unknown": self.unknown,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Record:
        """Create Record from dictionary (as read from store)."""
        return cls(
            record_id=data["record_id"],
            seq=data["seq"],
            run_id=data["run_id"],
            schema_version=data["schema_version"],
            cell_key=data["cell_key"],
            measurement_key=data["measurement_key"],
            substrate=data["substrate"],
            geometry=data["geometry"],
            dynamics=data["dynamics"],
            plasticity=data["plasticity"],
            credit=data["credit"],
            update=data["update"],
            params=data["params"],
            schedule=Schedule.from_dict(data["schedule"]),
            provenance=Provenance.from_dict(data["provenance"]),
            status=Status(
                gate_verdict=GateVerdict(data["status"]["gate_verdict"]),
                defect=data["status"]["defect"],
                cause=FailureCause(data["status"]["cause"]),
                severity=Severity(data["status"]["severity"]),
                quarantine=data["status"]["quarantine"],
                maturity=Maturity(data["status"]["maturity"]),
                uncertainty=data["status"]["uncertainty"],
                reproducibility=data["status"]["reproducibility"],
                ceec_link=data["status"]["ceec_link"],
            ),
            payload=data["payload"],
            unknown=data.get("unknown"),
        )


__all__ = [
    "FailureCause",
    "GateVerdict",
    "Maturity",
    "Record",
    "Severity",
    "Status",
    "_canonical_json",
]
