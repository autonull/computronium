"""Three-tier status model for experiment evidence.

Implements WP5 deliverable: three-tier status model (feedback #4):
- Observations: loss, accuracy, runtime, seed, variance, failure_signal,
  hardware, dataset (primary fields, written by stages)
- Assessments: gate_verdict, quarantine, maturity, failure_classification
  (produced by a *named, versioned, content-addressed procedure*;
  assessment_procedure_version + assessment_procedure_hash in status)
- Derived Claims: claim_eligible, promoted, beats_baseline, robust,
  generalizes (pure queries, never stored)

This preserves Doctrine 5 while making stored assessments scientifically auditable.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

from computronium.experiment.schema.record import (
    FailureCause,
    GateVerdict,
    Maturity,
    ReproducibilityClass,
    Severity,
)


def _canonical_json(obj: Any) -> str:
    """Serialize to canonical JSON for hashing."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class AssessmentProcedureKind(StrEnum):
    """Kinds of assessment procedures."""

    GATE_VERDICT = "gate_verdict"
    MATURITY = "maturity"
    FAILURE_CLASSIFICATION = "failure_classification"
    QUARANTINE = "quarantine"
    REPRODUCIBILITY = "reproducibility"


@dataclass(frozen=True, slots=True)
class AssessmentProcedure:
    """An assessment procedure - named, versioned, content-addressed.

    Each procedure is identified by (name, version, code_hash) where
    code_hash is SHA256 of the procedure's source/bytecode. The
    content hash makes the procedure definition immutable.
    """

    name: str
    version: str
    code_hash: str
    kind: AssessmentProcedureKind
    config_schema: dict[str, Any] = field(default_factory=dict)
    description: str = ""
    frozen_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @classmethod
    def from_source(
        cls,
        name: str,
        version: str,
        source_code: str,
        kind: AssessmentProcedureKind,
        config_schema: dict[str, Any] | None = None,
        description: str = "",
    ) -> AssessmentProcedure:
        """Create procedure from source code (computes code_hash)."""
        code_hash = hashlib.sha256(source_code.encode()).hexdigest()
        return cls(
            name=name,
            version=version,
            code_hash=code_hash,
            kind=kind,
            config_schema=config_schema or {},
            description=description,
        )

    def verify_integrity(self, source_code: str) -> bool:
        """Verify that source code matches the stored code_hash."""
        return hashlib.sha256(source_code.encode()).hexdigest() == self.code_hash


@dataclass(frozen=True, slots=True)
class Observations:
    """Primary observation fields written by pipeline stages.

    These are the raw measurements from an experiment run.
    """

    loss: float | None = None
    accuracy: float | None = None
    runtime_s: float | None = None
    seed: int | None = None
    variance: float | None = None
    failure_signal: str | None = None
    hardware: dict[str, str] | None = None
    dataset: str | None = None
    epochs_completed: int | None = None
    batches_completed: int | None = None
    peak_memory_mb: float | None = None
    flops: float | None = None
    energy_j: float | None = None
    # Extensible: additional observations via extra
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "loss": self.loss,
            "accuracy": self.accuracy,
            "runtime_s": self.runtime_s,
            "seed": self.seed,
            "variance": self.variance,
            "failure_signal": self.failure_signal,
            "hardware": self.hardware,
            "dataset": self.dataset,
            "epochs_completed": self.epochs_completed,
            "batches_completed": self.batches_completed,
            "peak_memory_mb": self.peak_memory_mb,
            "flops": self.flops,
            "energy_j": self.energy_j,
            "extra": self.extra,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Observations:
        return cls(
            loss=data.get("loss"),
            accuracy=data.get("accuracy"),
            runtime_s=data.get("runtime_s"),
            seed=data.get("seed"),
            variance=data.get("variance"),
            failure_signal=data.get("failure_signal"),
            hardware=data.get("hardware"),
            dataset=data.get("dataset"),
            epochs_completed=data.get("epochs_completed"),
            batches_completed=data.get("batches_completed"),
            peak_memory_mb=data.get("peak_memory_mb"),
            flops=data.get("flops"),
            energy_j=data.get("energy_j"),
            extra=data.get("extra", {}),
        )


@dataclass(frozen=True, slots=True)
class Assessments:
    """Assessment fields produced by named, versioned procedures.

    Each assessment is linked to its procedure via procedure_name,
    procedure_version, and procedure_code_hash. This makes assessments
    scientifically auditable - you can reproduce exactly how the
    assessment was produced.
    """

    gate_verdict: GateVerdict
    quarantine: bool
    maturity: Maturity
    failure_classification: FailureCause
    reproducibility: ReproducibilityClass
    uncertainty: dict[str, Any]
    severity: Severity
    defect: str
    ceec_link: str | None

    # Procedure linkage (audit trail)
    procedure_name: str
    procedure_version: str
    procedure_code_hash: str
    assessed_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_verdict": self.gate_verdict.value,
            "quarantine": self.quarantine,
            "maturity": self.maturity.value,
            "failure_classification": self.failure_classification.value,
            "reproducibility": self.reproducibility.value,
            "uncertainty": self.uncertainty,
            "severity": self.severity.value,
            "defect": self.defect,
            "ceec_link": self.ceec_link,
            "procedure_name": self.procedure_name,
            "procedure_version": self.procedure_version,
            "procedure_code_hash": self.procedure_code_hash,
            "assessed_at": self.assessed_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Assessments:
        return cls(
            gate_verdict=GateVerdict(data["gate_verdict"]),
            quarantine=data["quarantine"],
            maturity=Maturity(data["maturity"]),
            failure_classification=FailureCause(data["failure_classification"]),
            reproducibility=ReproducibilityClass(data["reproducibility"]),
            uncertainty=data["uncertainty"],
            severity=Severity(data["severity"]),
            defect=data["defect"],
            ceec_link=data.get("ceec_link"),
            procedure_name=data["procedure_name"],
            procedure_version=data["procedure_version"],
            procedure_code_hash=data["procedure_code_hash"],
            assessed_at=data.get("assessed_at", datetime.now().isoformat()),
        )


@dataclass(frozen=True, slots=True)
class DerivedClaims:
    """Derived claims - pure queries, never stored.

    These are computed on-demand from observations and assessments.
    They represent the scientific conclusions drawn from the evidence.
    """

    claim_eligible: bool = False
    promoted: bool = False
    beats_baseline: bool = False
    robust: bool = False
    generalizes: bool = False
    # Additional claims can be added
    extra: dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim_eligible": self.claim_eligible,
            "promoted": self.promoted,
            "beats_baseline": self.beats_baseline,
            "robust": self.robust,
            "generalizes": self.generalizes,
            "extra": self.extra,
        }


@dataclass(frozen=True, slots=True)
class StatusBundle:
    """Complete three-tier status bundle.

    Combines observations (raw), assessments (procedure-produced),
    and derived claims (computed queries).
    """

    observations: Observations
    assessments: Assessments
    derived_claims: DerivedClaims

    def to_status_legacy(self) -> StatusLegacy:
        """Convert to legacy Status format for backwards compatibility with store."""
        return StatusLegacy(
            gate_verdict=self.assessments.gate_verdict,
            defect=self.assessments.defect,
            cause=self.assessments.failure_classification,
            severity=self.assessments.severity,
            quarantine=self.assessments.quarantine,
            maturity=self.assessments.maturity,
            uncertainty=self.assessments.uncertainty,
            reproducibility=self.assessments.reproducibility,
            assessment_procedure_version=self.assessments.procedure_version,
            ceec_link=self.assessments.ceec_link,
        )

    def to_payload_dict(self) -> dict[str, Any]:
        """Convert to payload dictionary for storage."""
        return {
            "observations": self.observations.to_dict(),
            "assessments": self.assessments.to_dict(),
            "derived_claims": self.derived_claims.to_dict(),
        }

    @classmethod
    def from_payload_dict(cls, data: dict[str, Any]) -> StatusBundle:
        return cls(
            observations=Observations.from_dict(data["observations"]),
            assessments=Assessments.from_dict(data["assessments"]),
            derived_claims=DerivedClaims(**data.get("derived_claims", {})),
        )


# Legacy Status type alias for compatibility with existing Record type
# This maintains the exact same interface as the current Status in schema/record.py
@dataclass(frozen=True, slots=True)
class StatusLegacy:
    """Legacy Status format for store compatibility.

    This mirrors the exact structure of computronium.experiment.schema.record.Status
    so that existing Record.create() and store operations work unchanged.
    """

    gate_verdict: GateVerdict
    defect: str
    cause: FailureCause
    severity: Severity
    quarantine: bool
    maturity: Maturity
    uncertainty: dict[str, Any]
    reproducibility: ReproducibilityClass
    assessment_procedure_version: str
    ceec_link: str | None


def build_assessments_from_legacy(
    status: StatusLegacy,
    procedure_name: str,
    procedure_version: str,
    procedure_code_hash: str,
) -> Assessments:
    """Build Assessments from legacy Status plus procedure metadata."""
    return Assessments(
        gate_verdict=status.gate_verdict,
        quarantine=status.quarantine,
        maturity=status.maturity,
        failure_classification=status.cause,
        reproducibility=status.reproducibility,
        uncertainty=status.uncertainty,
        severity=status.severity,
        defect=status.defect,
        ceec_link=status.ceec_link,
        procedure_name=procedure_name,
        procedure_version=procedure_version,
        procedure_code_hash=procedure_code_hash,
    )


def build_legacy_from_assessments(assessments: Assessments) -> StatusLegacy:
    """Build legacy Status from Assessments (drops procedure hash)."""
    return StatusLegacy(
        gate_verdict=assessments.gate_verdict,
        defect=assessments.defect,
        cause=assessments.failure_classification,
        severity=assessments.severity,
        quarantine=assessments.quarantine,
        maturity=assessments.maturity,
        uncertainty=assessments.uncertainty,
        reproducibility=assessments.reproducibility,
        assessment_procedure_version=assessments.procedure_version,
        ceec_link=assessments.ceec_link,
    )


__all__ = [
    "AssessmentProcedure",
    "AssessmentProcedureKind",
    "Assessments",
    "DerivedClaims",
    "Observations",
    "StatusBundle",
    "StatusLegacy",
    "_canonical_json",
    "build_assessments_from_legacy",
    "build_legacy_from_assessments",
]
