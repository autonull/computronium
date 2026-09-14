"""Ledger schema: DDL, append-only triggers, additive migrations."""

from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import sqlite3
    from pathlib import Path

_APPEND_ONLY = (
    "artifacts",
    "evidence",
    "evidence_artifacts",
    "derived",
    "beliefs",
    "belief_revisions",
    "belief_evidence",
    "belief_derived",
    "belief_dependencies",
    "goals",
    "goal_revisions",
    "goal_beliefs",
    "decisions",
    "gate_outcomes",
    "status_changes",
    "calibration_records",
    "instrument_notes",
)

_INPUT_NAMESPACE = {
    "e": "evidence",
    "d": "derived",
    "a": "artifacts",
    "ir": "instrument_notes",
}

_SCHEMA = """
CREATE TABLE IF NOT EXISTS artifacts (
    id TEXT PRIMARY KEY,
    sha256 TEXT UNIQUE NOT NULL,
    uri TEXT NOT NULL,
    type TEXT NOT NULL,
    provenance JSON NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS evidence (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    scope JSON NOT NULL,
    axes JSON,
    values_ref TEXT,
    uncertainties JSON,
    quality JSON,
    defects JSON,
    no_artifact_justification TEXT,
    notes TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS evidence_artifacts (
    evidence_id TEXT NOT NULL REFERENCES evidence(id),
    artifact_id TEXT NOT NULL REFERENCES artifacts(id),
    PRIMARY KEY (evidence_id, artifact_id)
);
CREATE TABLE IF NOT EXISTS derived (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    operator TEXT NOT NULL,
    inputs JSON NOT NULL,
    left TEXT,
    right TEXT,
    parameters JSON,
    value JSON,
    probability_positive JSON,
    probability_material JSON,
    assumptions JSON,
    checks JSON,
    scope JSON NOT NULL,
    provenance JSON,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS beliefs (
    id TEXT PRIMARY KEY,
    statement TEXT NOT NULL,
    type TEXT NOT NULL,
    scope JSON NOT NULL,
    posterior_method TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS belief_revisions (
    id TEXT PRIMARY KEY,
    belief_id TEXT NOT NULL REFERENCES beliefs(id),
    probability_low REAL NOT NULL,
    probability_high REAL NOT NULL,
    probability_point REAL,
    probability_method TEXT,
    uncertainty TEXT NOT NULL,
    evidence_weight TEXT NOT NULL,
    generality TEXT NOT NULL,
    status TEXT NOT NULL,
    rationale TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS belief_evidence (
    belief_id TEXT NOT NULL REFERENCES beliefs(id),
    evidence_id TEXT NOT NULL REFERENCES evidence(id),
    PRIMARY KEY (belief_id, evidence_id)
);
CREATE TABLE IF NOT EXISTS belief_derived (
    belief_id TEXT NOT NULL REFERENCES beliefs(id),
    derived_id TEXT NOT NULL REFERENCES derived(id),
    PRIMARY KEY (belief_id, derived_id)
);
CREATE TABLE IF NOT EXISTS belief_dependencies (
    belief_id TEXT NOT NULL REFERENCES beliefs(id),
    depends_on_belief_id TEXT NOT NULL REFERENCES beliefs(id),
    PRIMARY KEY (belief_id, depends_on_belief_id)
);
CREATE TABLE IF NOT EXISTS goals (
    id TEXT PRIMARY KEY,
    statement TEXT NOT NULL,
    kind TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS goal_revisions (
    id TEXT PRIMARY KEY,
    goal_id TEXT NOT NULL REFERENCES goals(id),
    utility JSON NOT NULL,
    scalar_utility REAL,
    cost_low REAL,
    cost_high REAL,
    priority REAL,
    status TEXT NOT NULL,
    rationale TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS goal_beliefs (
    goal_id TEXT NOT NULL REFERENCES goals(id),
    belief_id TEXT NOT NULL REFERENCES beliefs(id),
    PRIMARY KEY (goal_id, belief_id)
);
CREATE TABLE IF NOT EXISTS experiments (
    id TEXT PRIMARY KEY,
    question TEXT NOT NULL,
    rationale TEXT NOT NULL,
    scope JSON NOT NULL,
    target_beliefs JSON NOT NULL,
    target_goals JSON NOT NULL,
    design JSON NOT NULL,
    prediction TEXT NOT NULL,
    prediction_probability JSON,
    controls JSON NOT NULL,
    metrics JSON NOT NULL,
    budget TEXT NOT NULL,
    cost_low REAL,
    cost_high REAL,
    falsification_criterion TEXT NOT NULL,
    overturn_criterion TEXT NOT NULL,
    hard_gates JSON NOT NULL,
    status TEXT NOT NULL,
    pre_registered_at TEXT,
    started_at TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS decisions (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    state_hash TEXT NOT NULL,
    candidate_experiments JSON NOT NULL,
    scores JSON NOT NULL,
    selected_experiment TEXT,
    overrides JSON NOT NULL,
    constraints_checked JSON NOT NULL,
    policy_version TEXT,
    rationale TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS gate_outcomes (
    id TEXT PRIMARY KEY,
    gate TEXT NOT NULL,
    belief_id TEXT REFERENCES beliefs(id),
    experiment_id TEXT REFERENCES experiments(id),
    status TEXT NOT NULL,
    evidence_refs JSON NOT NULL,
    derived_refs JSON NOT NULL,
    rationale TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS status_changes (
    id TEXT PRIMARY KEY,
    belief_id TEXT NOT NULL REFERENCES beliefs(id),
    from_status TEXT NOT NULL,
    to_status TEXT NOT NULL,
    reason TEXT NOT NULL,
    trigger TEXT,
    gate_refs JSON NOT NULL,
    evidence_refs JSON NOT NULL,
    derived_refs JSON NOT NULL,
    actor TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS calibration_records (
    id TEXT PRIMARY KEY,
    experiment_id TEXT REFERENCES experiments(id),
    belief_id TEXT REFERENCES beliefs(id),
    prediction TEXT NOT NULL,
    predicted_probability JSON,
    outcome TEXT,
    outcome_boolean INTEGER,
    brier_score REAL,
    log_score REAL,
    scope JSON,
    notes TEXT,
    policy_version TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ledger_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS instrument_notes (
    id TEXT PRIMARY KEY,
    belief_id TEXT NOT NULL REFERENCES beliefs(id),
    note TEXT NOT NULL,
    kind TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_evidence_kind ON evidence(kind);
CREATE INDEX IF NOT EXISTS idx_belief_revisions_belief ON belief_revisions(belief_id, created_at);
CREATE INDEX IF NOT EXISTS idx_status_changes_belief ON status_changes(belief_id, created_at);
CREATE INDEX IF NOT EXISTS idx_gate_outcomes_belief ON gate_outcomes(belief_id);
CREATE INDEX IF NOT EXISTS idx_gate_outcomes_experiment ON gate_outcomes(experiment_id);
CREATE INDEX IF NOT EXISTS idx_experiments_status ON experiments(status);
CREATE INDEX IF NOT EXISTS idx_cal_experiment ON calibration_records(experiment_id);
"""


class CEECError(Exception):
    """Base class for CEEC ledger errors."""


class StoreError(CEECError):
    """Ledger storage or integrity violation."""


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds")


_POLICY_COLUMNS = {
    "decisions": "policy_version",
    "calibration_records": "policy_version",
}


def _additive_migrate(conn: sqlite3.Connection) -> None:
    """Append-only additive migration: stamp columns on pre-T26 ledgers."""
    for table, column in _POLICY_COLUMNS.items():
        cols = {
            r["name"]
            for r in conn.execute(f"PRAGMA table_info({table})").fetchall()  # noqa: S608  internal table map
        }
        if column not in cols:
            conn.execute(
                f"ALTER TABLE {table} ADD COLUMN {column} TEXT"  # noqa: S608  internal table map
            )


def _dump(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, default=str)


def artifact_file_bytes(path: Path) -> bytes:
    return path.read_bytes()


def copy_artifact_into_place(source: Path, target: Path) -> None:
    shutil.copy2(source, target)
