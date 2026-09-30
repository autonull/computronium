"""Assessment procedure registry for experiment evidence.

Implements WP5 deliverable: AssessmentProcedure registry (new):
- Each procedure is a frozen dataclass with name, version, code_hash (SHA256 of
  the procedure's source/bytecode), config_schema, and frozen_at timestamp.
- The registry is append-only; a procedure version is identified by
  (name, version, code_hash).
- assessment_procedure_hash in status is the content address, making the
  procedure definition immutable. Version alone is not trusted.
"""

from __future__ import annotations

from dataclasses import replace

from computronium.experiment.evidence.status import (
    AssessmentProcedure,
    AssessmentProcedureKind,
)
from computronium.experiment.schema.registry import Registry

# Global assessment procedure registry
# Key format: "name@version#code_hash_prefix"
ASSESSMENT_PROCEDURES: Registry[AssessmentProcedure] = Registry[AssessmentProcedure]()


def _make_registry_key(name: str, version: str, code_hash: str) -> str:
    """Create a unique registry key from name, version, and code hash."""
    return f"{name}@{version}#{code_hash[:8]}"


def register_assessment_procedure(procedure: AssessmentProcedure) -> None:
    """Register an assessment procedure.

    The procedure is keyed by (name, version, code_hash) to ensure
    content-addressed immutability. Two procedures with the same name
    and version but different code_hash are treated as distinct.
    """
    # Create a copy with the registry key as the name field
    key = _make_registry_key(procedure.name, procedure.version, procedure.code_hash)
    proc_with_key = replace(procedure, name=key)
    ASSESSMENT_PROCEDURES.register(proc_with_key)


def get_assessment_procedure(
    name: str, version: str, code_hash: str | None = None
) -> AssessmentProcedure | None:
    """Get an assessment procedure by name, version, and optional code_hash.

    If code_hash is provided, exact match is required. If not provided,
    returns the latest registered version (by registration order).
    """
    if code_hash:
        key = _make_registry_key(name, version, code_hash)
        proc = ASSESSMENT_PROCEDURES.get(key)
        if proc:
            # Restore original name for the returned procedure
            return replace(proc, name=name)
        return None
    # Find any procedure matching name and version
    prefix = f"{name}@{version}#"
    for key in ASSESSMENT_PROCEDURES.keys():  # noqa: SIM118 - need keys, not values
        if key.startswith(prefix):
            proc = ASSESSMENT_PROCEDURES[key]
            return replace(proc, name=name)
    return None


def list_assessment_procedures(
    kind: AssessmentProcedureKind | None = None,
) -> list[AssessmentProcedure]:
    """List all registered assessment procedures, optionally filtered by kind."""
    procedures = []
    for key in ASSESSMENT_PROCEDURES.keys():  # noqa: SIM118 - need keys, not values
        proc = ASSESSMENT_PROCEDURES[key]
        # Extract original name from key
        original_name = key.split("@")[0]
        proc = replace(proc, name=original_name)
        if kind is None or proc.kind == kind:
            procedures.append(proc)
    return procedures


# =============================================================================
# Built-in assessment procedures (registered at module import)
# =============================================================================

# Gate verdict assessment procedure
_GATE_VERDICT_SOURCE = """
def assess_gate_verdict(record: Record, config: dict) -> GateVerdict:
    '''Assess gate verdict from record observations and assessments.

    Gate verdict logic:
    - PASS: No hard defects, gate criteria met
    - FAIL: Hard defects present or gate criteria not met
    - QUARANTINE: Soft defects present, needs review
    - PENDING: Assessment not yet run
    '''
    if record.status.has_void or record.status.has_hard:
        return GateVerdict.FAIL
    if record.status.soft_defects:
        return GateVerdict.QUARANTINE
    # Check gate-specific criteria from config
    if config.get("require_min_seeds", 0) > 0:
        if record.schedule.n_seeds < config["require_min_seeds"]:
            return GateVerdict.FAIL
    return GateVerdict.PASS_
"""

register_assessment_procedure(
    AssessmentProcedure.from_source(
        name="gate_verdict",
        version="1.0",
        source_code=_GATE_VERDICT_SOURCE,
        kind=AssessmentProcedureKind.GATE_VERDICT,
        config_schema={
            "type": "object",
            "properties": {"require_min_seeds": {"type": "integer", "minimum": 1}},
        },
        description="Assess gate verdict from record defects and schedule",
    )
)

# Maturity assessment procedure
_MATURITY_SOURCE = """
def assess_maturity(record: Record, config: dict) -> Maturity:
    '''Assess maturity level from record provenance and history.

    Maturity levels:
    - L0: Initial mapping (first observation)
    - L1: Verified (reproduced at least once)
    - L2: Claim-grade (meets claim eligibility criteria)
    '''
    n_replications = config.get("n_replications", 1)
    if n_replications >= 3 and record.status.gate_verdict == GateVerdict.PASS_:
        return Maturity.L2
    if n_replications >= 2:
        return Maturity.L1
    return Maturity.L0
"""

register_assessment_procedure(
    AssessmentProcedure.from_source(
        name="maturity",
        version="1.0",
        source_code=_MATURITY_SOURCE,
        kind=AssessmentProcedureKind.MATURITY,
        config_schema={
            "type": "object",
            "properties": {"n_replications": {"type": "integer", "minimum": 1}},
        },
        description="Assess maturity level from replication count and gate verdict",
    )
)

# Failure classification assessment procedure
_FAILURE_CLASSIFICATION_SOURCE = """
def assess_failure_classification(record: Record, config: dict) -> FailureCause:
    '''Classify failure cause from record defects and error signals.

    Maps defect classifications to FailureCause taxonomy.
    '''
    if record.status.has_void:
        return FailureCause.INVALID_CONFIG
    if record.status.has_hard:
        # Map first hard defect to failure cause
        for defect in record.status.hard_defects:
            cause = _map_defect_to_cause(defect.defect_class)
            if cause != FailureCause.UNKNOWN:
                return cause
    if record.status.soft_defects:
        for defect in record.status.soft_defects:
            cause = _map_defect_to_cause(defect.defect_class)
            if cause != FailureCause.UNKNOWN:
                return cause
    return FailureCause.UNKNOWN

def _map_defect_to_cause(defect_class: DefectClass) -> FailureCause:
    mapping = {
        DefectClass.HARD_NUMERICAL: FailureCause.NUMERICAL,
        DefectClass.HARD_TIMEOUT: FailureCause.TIMEOUT,
        DefectClass.HARD_OOM: FailureCause.OOM,
        DefectClass.HARD_INVALID_CONFIG: FailureCause.INVALID_CONFIG,
        DefectClass.HARD_RUNTIME_ERROR: FailureCause.RUNTIME_ERROR,
        DefectClass.HARD_CONSTRAINT_VIOLATION: FailureCause.CONSTRAINT_VIOLATION,
        DefectClass.HARD_DIVERGENCE: FailureCause.DIVERGENCE,
    }
    return mapping.get(defect_class, FailureCause.UNKNOWN)
"""

register_assessment_procedure(
    AssessmentProcedure.from_source(
        name="failure_classification",
        version="1.0",
        source_code=_FAILURE_CLASSIFICATION_SOURCE,
        kind=AssessmentProcedureKind.FAILURE_CLASSIFICATION,
        config_schema={},
        description="Classify failure cause from defect taxonomy",
    )
)

# Quarantine assessment procedure
_QUARANTINE_SOURCE = """
def assess_quarantine(record: Record, config: dict) -> bool:
    '''Determine if a record should be quarantined.

    Quarantine criteria:
    - Soft defects present (warning conditions)
    - Gate verdict is QUARANTINE
    - Explicit quarantine flag in config
    '''
    if record.status.quarantine:
        return True
    if record.status.gate_verdict == GateVerdict.QUARANTINE:
        return True
    if config.get("quarantine_on_soft_defects", True):
        return len(record.status.soft_defects) > 0
    return False
"""

register_assessment_procedure(
    AssessmentProcedure.from_source(
        name="quarantine",
        version="1.0",
        source_code=_QUARANTINE_SOURCE,
        kind=AssessmentProcedureKind.QUARANTINE,
        config_schema={
            "type": "object",
            "properties": {
                "quarantine_on_soft_defects": {"type": "boolean", "default": True}
            },
        },
        description="Determine quarantine status from defects and gate verdict",
    )
)

# Reproducibility assessment procedure
_REPRODUCIBILITY_SOURCE = """
def assess_reproducibility(record: Record, config: dict) -> ReproducibilityClass:
    '''Assess reproducibility class from record provenance.

    Three classes (WP1.5):
    - REPLAYABLE: Same code + seed + schedule -> same execution request
    - COMPUTATIONALLY_REPRODUCIBLE: Same env reproduces numerics within tolerance
    - SCIENTIFICALLY_REPRODUCIBLE: Independent experiment reproduces reported effect
    '''
    # Check provenance for reproducibility evidence
    repro_level = record.provenance.extra.get("reproducibility_level", "replayable")
    return ReproducibilityClass(repro_level)
"""

register_assessment_procedure(
    AssessmentProcedure.from_source(
        name="reproducibility",
        version="1.0",
        source_code=_REPRODUCIBILITY_SOURCE,
        kind=AssessmentProcedureKind.REPRODUCIBILITY,
        config_schema={},
        description="Assess reproducibility class from provenance metadata",
    )
)


__all__ = [
    "ASSESSMENT_PROCEDURES",
    "get_assessment_procedure",
    "list_assessment_procedures",
    "register_assessment_procedure",
]
