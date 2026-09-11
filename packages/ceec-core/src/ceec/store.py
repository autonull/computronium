"""Append-only SQLite ledger for CEEC objects.

Append-only tables are enforced with database triggers; the public API exposes
no mutation path for artifacts, evidence, derived objects, decisions, gate
outcomes, status changes, or calibration records.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import shutil
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Self

from ceec import models
from ceec.ids import prefix_for

logger = logging.getLogger(__name__)

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
    created_at TEXT NOT NULL
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


def _dump(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, default=str)


class CEECStore:  # ruff: ignore[too-many-public-methods] - ledger API is intentionally broad
    """Transactional, append-only CEEC ledger."""

    def __init__(self, db_path: Path | str, artifacts_dir: Path | str) -> None:
        self.db_path = Path(db_path)
        self.artifacts_dir = Path(artifacts_dir)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.executescript(_SCHEMA)
        for table in _APPEND_ONLY:
            for action in ("UPDATE", "DELETE"):
                self._conn.execute(
                    f"CREATE TRIGGER IF NOT EXISTS {table}_no_{action.lower()} "
                    f"BEFORE {action} ON {table} BEGIN "
                    f"SELECT RAISE(ABORT, '{table} is append-only'); END"
                )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_) -> None:
        self.close()

    if TYPE_CHECKING:
        from collections.abc import Iterator

    @contextmanager
    def _tx(self) -> Iterator[sqlite3.Connection]:
        try:
            yield self._conn
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

    def _next_id(self, kind: str, table: str, explicit: str | None) -> str:
        if explicit is not None:
            return explicit
        sql = f"SELECT COUNT(*) AS n FROM {table}"  # ruff: ignore[hardcoded-sql-expression]  internal prefix map
        row = self._conn.execute(sql).fetchone()
        return f"{prefix_for(kind)}-{row['n'] + 1:06d}"

    # -- artifacts ---------------------------------------------------------

    def ingest_artifact(
        self,
        source: Path | str | bytes,
        type_: str,
        provenance: dict[str, Any] | None = None,
        id_: str | None = None,
    ) -> models.Artifact:
        data = source if isinstance(source, bytes) else Path(source).read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        existing = self._conn.execute(
            "SELECT * FROM artifacts WHERE sha256 = ?", (digest,)
        ).fetchone()
        if existing is not None:
            logger.debug("artifact %s already ingested", existing["id"])
            return self.get_artifact(existing["id"])
        uri_dir = self.artifacts_dir / digest[:2]
        uri_dir.mkdir(parents=True, exist_ok=True)
        uri = uri_dir / digest
        if uri.exists():
            raise StoreError(f"artifact file collision at {uri}")
        uri.write_bytes(data)
        artifact = models.Artifact(
            id=self._next_id("artifact", "artifacts", id_),
            sha256=digest,
            uri=str(uri),
            type=type_,
            provenance=provenance or {},
            created_at=now(),
        )
        with self._tx() as conn:
            conn.execute(
                "INSERT INTO artifacts VALUES (?, ?, ?, ?, ?, ?)",
                (
                    artifact.id,
                    artifact.sha256,
                    artifact.uri,
                    artifact.type,
                    _dump(artifact.provenance),
                    artifact.created_at,
                ),
            )
        return artifact

    def get_artifact(self, id_: str) -> models.Artifact:
        row = self._fetch("artifacts", id_)
        return models.Artifact(
            id=row["id"],
            sha256=row["sha256"],
            uri=row["uri"],
            type=row["type"],
            provenance=json.loads(row["provenance"]),
            created_at=row["created_at"],
        )

    # -- evidence ----------------------------------------------------------

    def record_evidence(  # ruff: ignore[too-many-arguments, too-many-positional-arguments] - mirrors evidence fields
        self,
        kind: str,
        scope: models.Scope,
        artifact_refs: list[str] | None = None,
        quality: dict[str, Any] | None = None,
        axes: list[str] | None = None,
        values_ref: str | None = None,
        uncertainties: dict[str, Any] | None = None,
        defects: list[str] | None = None,
        notes: str | None = None,
        no_artifact_justification: str | None = None,
        id_: str | None = None,
    ) -> models.Evidence:
        artifact_refs = artifact_refs or []
        for ref in artifact_refs:
            self._require("artifacts", ref)
        if not artifact_refs and not no_artifact_justification:
            raise StoreError(
                "evidence requires at least one artifact ref or an explicit "
                "no_artifact_justification"
            )
        evidence = models.Evidence(
            id=self._next_id("evidence", "evidence", id_),
            kind=kind,  # type: ignore[arg-type]
            scope=scope,
            axes=axes,
            values_ref=values_ref,
            uncertainties=uncertainties,
            quality=quality or {},
            defects=defects or [],
            notes=notes,
            no_artifact_justification=no_artifact_justification,
            created_at=now(),
        )
        with self._tx() as conn:
            conn.execute(
                "INSERT INTO evidence VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    evidence.id,
                    evidence.kind,
                    _dump(evidence.scope.model_dump()),
                    _dump(evidence.axes),
                    evidence.values_ref,
                    _dump(evidence.uncertainties),
                    _dump(evidence.quality),
                    _dump(evidence.defects),
                    evidence.no_artifact_justification,
                    evidence.notes,
                    evidence.created_at,
                ),
            )
            conn.executemany(
                "INSERT INTO evidence_artifacts VALUES (?, ?)",
                [(evidence.id, ref) for ref in artifact_refs],
            )
        return evidence

    def get_evidence(self, id_: str) -> models.Evidence:
        row = self._fetch("evidence", id_)
        return models.Evidence(
            id=row["id"],
            kind=row["kind"],  # type: ignore[arg-type]
            scope=models.Scope(**json.loads(row["scope"])),
            axes=json.loads(row["axes"]),
            values_ref=row["values_ref"],
            uncertainties=json.loads(row["uncertainties"]),
            quality=json.loads(row["quality"]),
            defects=json.loads(row["defects"]),
            no_artifact_justification=row["no_artifact_justification"],
            notes=row["notes"],
            created_at=row["created_at"],
        )

    def evidence_artifacts(self, evidence_id: str) -> list[str]:
        rows = self._conn.execute(
            "SELECT artifact_id FROM evidence_artifacts WHERE evidence_id = ?",
            (evidence_id,),
        ).fetchall()
        return [r["artifact_id"] for r in rows]

    # -- derived -----------------------------------------------------------

    def record_derived(  # ruff: ignore[too-many-arguments, too-many-positional-arguments] - mirrors derived fields
        self,
        type_: str,
        operator: str,
        inputs: dict[str, list[str]],
        scope: models.Scope,
        value: Any = None,
        left: str | None = None,
        right: str | None = None,
        parameters: dict[str, Any] | None = None,
        probability_positive: models.Probability | None = None,
        probability_material: models.Probability | None = None,
        assumptions: list[str] | None = None,
        checks: list[str] | None = None,
        provenance: dict[str, Any] | None = None,
        id_: str | None = None,
    ) -> models.Derived:
        for refs in inputs.values():
            for ref in refs:
                prefix = ref.split("-", 1)[0].lower()
                table = _INPUT_NAMESPACE.get(prefix)
                if table is None:
                    raise StoreError(f"unknown input namespace for ref {ref!r}")
                self._require(table, ref)
        derived = models.Derived(
            id=self._next_id("derived", "derived", id_),
            type=type_,
            operator=operator,
            inputs=inputs,
            left=left,
            right=right,
            parameters=parameters,
            value=value,
            probability_positive=probability_positive,
            probability_material=probability_material,
            assumptions=assumptions or [],
            checks=checks or [],
            scope=scope,
            provenance=provenance,
            created_at=now(),
        )
        with self._tx() as conn:
            conn.execute(
                "INSERT INTO derived VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    derived.id,
                    derived.type,
                    derived.operator,
                    _dump(derived.inputs),
                    derived.left,
                    derived.right,
                    _dump(derived.parameters),
                    _dump(derived.value),
                    _dump(probability_positive.model_dump())
                    if probability_positive
                    else None,
                    _dump(probability_material.model_dump())
                    if probability_material
                    else None,
                    _dump(derived.assumptions),
                    _dump(derived.checks),
                    _dump(derived.scope.model_dump()),
                    _dump(derived.provenance),
                    derived.created_at,
                ),
            )
        return derived

    def get_derived(self, id_: str) -> models.Derived:
        row = self._fetch("derived", id_)
        return models.Derived(
            id=row["id"],
            type=row["type"],
            operator=row["operator"],
            inputs=json.loads(row["inputs"]),
            left=row["left"],
            right=row["right"],
            parameters=json.loads(row["parameters"]),
            value=json.loads(row["value"]),
            probability_positive=(
                models.Probability(**json.loads(row["probability_positive"]))
                if row["probability_positive"]
                else None
            ),
            probability_material=(
                models.Probability(**json.loads(row["probability_material"]))
                if row["probability_material"]
                else None
            ),
            assumptions=json.loads(row["assumptions"]),
            checks=json.loads(row["checks"]),
            scope=models.Scope(**json.loads(row["scope"])),
            provenance=json.loads(row["provenance"]),
            created_at=row["created_at"],
        )

    # -- beliefs -----------------------------------------------------------

    def create_belief(
        self,
        statement: str,
        type_: str,
        scope: models.Scope,
        posterior_method: str | None = None,
        id_: str | None = None,
        evidence_refs: list[str] | None = None,
        derived_refs: list[str] | None = None,
        depends_on: list[str] | None = None,
    ) -> models.Belief:
        for ref in evidence_refs or []:
            self._require("evidence", ref)
        for ref in derived_refs or []:
            self._require("derived", ref)
        for ref in depends_on or []:
            self._require("beliefs", ref)
        belief = models.Belief(
            id=self._next_id("belief", "beliefs", id_),
            statement=statement,
            type=type_,  # type: ignore[arg-type]
            scope=scope,
            posterior_method=posterior_method,
            created_at=now(),
        )
        with self._tx() as conn:
            conn.execute(
                "INSERT INTO beliefs VALUES (?, ?, ?, ?, ?, ?)",
                (
                    belief.id,
                    belief.statement,
                    belief.type,
                    _dump(belief.scope.model_dump()),
                    belief.posterior_method,
                    belief.created_at,
                ),
            )
            self._link(
                conn,
                "belief_evidence",
                "belief_id",
                belief.id,
                "evidence_id",
                evidence_refs,
            )
            self._link(
                conn,
                "belief_derived",
                "belief_id",
                belief.id,
                "derived_id",
                derived_refs,
            )
            self._link(
                conn,
                "belief_dependencies",
                "belief_id",
                belief.id,
                "depends_on_belief_id",
                depends_on,
            )
        return belief

    def update_belief(
        self,
        belief_id: str,
        probability: models.Probability,
        uncertainty: str,
        evidence_weight: str,
        generality: str,
        status: str,
        rationale: str,
        id_: str | None = None,
    ) -> models.BeliefRevision:
        if not rationale:
            raise StoreError("belief revision requires rationale")
        if status != "open":
            raise StoreError(
                "gated statuses are set via change_status; update_belief only records open revisions"
            )
        self._require("beliefs", belief_id)
        if not self._has_links(
            belief_id,
            ("belief_evidence", "evidence_id"),
            ("belief_derived", "derived_id"),
        ):
            raise StoreError(
                f"belief {belief_id} has no evidence or derived refs; open revision refused"
            )
        revision = models.BeliefRevision(
            id=self._next_id("belief_revision", "belief_revisions", id_),
            belief_id=belief_id,
            probability=probability,
            uncertainty=uncertainty,  # type: ignore[arg-type]
            evidence_weight=evidence_weight,  # type: ignore[arg-type]
            generality=generality,  # type: ignore[arg-type]
            status=status,  # type: ignore[arg-type]
            rationale=rationale,
            created_at=now(),
        )
        with self._tx() as conn:
            conn.execute(
                "INSERT INTO belief_revisions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    revision.id,
                    belief_id,
                    probability.low,
                    probability.high,
                    probability.point,
                    probability.method,
                    uncertainty,
                    evidence_weight,
                    generality,
                    status,
                    rationale,
                    revision.created_at,
                ),
            )
        return revision

    def get_belief(self, id_: str) -> models.Belief:
        row = self._fetch("beliefs", id_)
        return models.Belief(
            id=row["id"],
            statement=row["statement"],
            type=row["type"],  # type: ignore[arg-type]
            scope=models.Scope(**json.loads(row["scope"])),
            posterior_method=row["posterior_method"],
            created_at=row["created_at"],
        )

    def latest_revision(self, belief_id: str) -> models.BeliefRevision | None:
        self._require("beliefs", belief_id)
        row = self._conn.execute(
            "SELECT * FROM belief_revisions WHERE belief_id = ? "
            "ORDER BY created_at DESC, id DESC LIMIT 1",
            (belief_id,),
        ).fetchone()
        if row is None:
            return None
        return models.BeliefRevision(
            id=row["id"],
            belief_id=row["belief_id"],
            probability=models.Probability(
                low=row["probability_low"],
                high=row["probability_high"],
                point=row["probability_point"],
                method=row["probability_method"],
            ),
            uncertainty=row["uncertainty"],  # type: ignore[arg-type]
            evidence_weight=row["evidence_weight"],  # type: ignore[arg-type]
            generality=row["generality"],  # type: ignore[arg-type]
            status=row["status"],  # type: ignore[arg-type]
            rationale=row["rationale"],
            created_at=row["created_at"],
        )

    def revisions(self, belief_id: str) -> list[models.BeliefRevision]:
        rows = self._conn.execute(
            "SELECT id FROM belief_revisions WHERE belief_id = ? ORDER BY created_at, id",
            (belief_id,),
        ).fetchall()
        out = []
        for r in rows:
            row = self._conn.execute(
                "SELECT * FROM belief_revisions WHERE id = ?", (r["id"],)
            ).fetchone()
            out.append(
                models.BeliefRevision(
                    id=row["id"],
                    belief_id=row["belief_id"],
                    probability=models.Probability(
                        low=row["probability_low"],
                        high=row["probability_high"],
                        point=row["probability_point"],
                        method=row["probability_method"],
                    ),
                    uncertainty=row["uncertainty"],  # type: ignore[arg-type]
                    evidence_weight=row["evidence_weight"],  # type: ignore[arg-type]
                    generality=row["generality"],  # type: ignore[arg-type]
                    status=row["status"],  # type: ignore[arg-type]
                    rationale=row["rationale"],
                    created_at=row["created_at"],
                )
            )
        return out

    def belief_dependencies(self, belief_id: str) -> list[str]:
        rows = self._conn.execute(
            "SELECT depends_on_belief_id FROM belief_dependencies WHERE belief_id = ?",
            (belief_id,),
        ).fetchall()
        return [r["depends_on_belief_id"] for r in rows]

    def dependents_of(self, belief_id: str) -> list[str]:
        rows = self._conn.execute(
            "SELECT belief_id FROM belief_dependencies WHERE depends_on_belief_id = ?",
            (belief_id,),
        ).fetchall()
        return [r["belief_id"] for r in rows]

    def beliefs_by_status(self, status: str) -> list[str]:
        rows = self._conn.execute(
            "SELECT belief_id FROM ("
            " SELECT belief_id, status, ROW_NUMBER() OVER "
            " (PARTITION BY belief_id ORDER BY created_at DESC, id DESC) AS rn"
            " FROM belief_revisions)"
            " WHERE rn = 1 AND status = ?",
            (status,),
        ).fetchall()
        return [r["belief_id"] for r in rows]

    # -- goals -------------------------------------------------------------

    def create_goal(
        self,
        statement: str,
        kind: str,
        id_: str | None = None,
        belief_refs: list[str] | None = None,
    ) -> models.Goal:
        for ref in belief_refs or []:
            self._require("beliefs", ref)
        goal = models.Goal(
            id=self._next_id("goal", "goals", id_),
            statement=statement,
            kind=kind,  # type: ignore[arg-type]
            created_at=now(),
        )
        with self._tx() as conn:
            conn.execute(
                "INSERT INTO goals VALUES (?, ?, ?, ?)",
                (goal.id, goal.statement, goal.kind, goal.created_at),
            )
            self._link(
                conn, "goal_beliefs", "goal_id", goal.id, "belief_id", belief_refs
            )
        return goal

    def revise_goal(
        self,
        goal_id: str,
        utility: dict[str, float],
        status: str = "active",
        scalar_utility: float | None = None,
        cost_low: float | None = None,
        cost_high: float | None = None,
        priority: float | None = None,
        rationale: str | None = None,
        id_: str | None = None,
    ) -> models.GoalRevision:
        self._require("goals", goal_id)
        revision = models.GoalRevision(
            id=self._next_id("goal_revision", "goal_revisions", id_),
            goal_id=goal_id,
            utility=utility,
            scalar_utility=scalar_utility,
            cost_low=cost_low,
            cost_high=cost_high,
            priority=priority,
            status=status,  # type: ignore[arg-type]
            rationale=rationale,
            created_at=now(),
        )
        with self._tx() as conn:
            conn.execute(
                "INSERT INTO goal_revisions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    revision.id,
                    goal_id,
                    _dump(utility),
                    scalar_utility,
                    cost_low,
                    cost_high,
                    priority,
                    status,
                    rationale,
                    revision.created_at,
                ),
            )
        return revision

    def latest_goal_revision(self, goal_id: str) -> models.GoalRevision | None:
        self._require("goals", goal_id)
        row = self._conn.execute(
            "SELECT * FROM goal_revisions WHERE goal_id = ? "
            "ORDER BY created_at DESC, id DESC LIMIT 1",
            (goal_id,),
        ).fetchone()
        if row is None:
            return None
        return models.GoalRevision(
            id=row["id"],
            goal_id=row["goal_id"],
            utility=json.loads(row["utility"]),
            scalar_utility=row["scalar_utility"],
            cost_low=row["cost_low"],
            cost_high=row["cost_high"],
            priority=row["priority"],
            status=row["status"],  # type: ignore[arg-type]
            rationale=row["rationale"],
            created_at=row["created_at"],
        )

    # -- experiments -------------------------------------------------------

    def pre_register_experiment(
        self, experiment: models.Experiment
    ) -> models.Experiment:
        if self._conn.execute(
            "SELECT 1 FROM experiments WHERE id = ?", (experiment.id,)
        ).fetchone():
            raise StoreError(f"experiment {experiment.id} already registered")
        for ref in experiment.target_beliefs:
            self._require("beliefs", ref)
        for ref in experiment.target_goals:
            self._require("goals", ref)
        missing = [
            f
            for f in (
                "question",
                "rationale",
                "prediction",
                "falsification_criterion",
                "overturn_criterion",
            )
            if not getattr(experiment, f)
        ]
        if missing:
            raise StoreError(f"pre-registration incomplete, missing: {missing}")
        if not experiment.metrics or not experiment.hard_gates:
            raise StoreError("pre-registration requires metrics and hard gates")
        if experiment.status != "draft":
            raise StoreError(
                f"experiment {experiment.id} must have status='draft' to "
                f"pre-register (got {experiment.status!r})"
            )
        registered = experiment.model_copy(
            update={"status": "pre_registered", "created_at": experiment.created_at}
        )
        with self._tx() as conn:
            conn.execute(
                "INSERT INTO experiments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    registered.id,
                    registered.question,
                    registered.rationale,
                    _dump(registered.scope.model_dump()),
                    _dump(registered.target_beliefs),
                    _dump(registered.target_goals),
                    _dump(registered.design),
                    registered.prediction,
                    _dump(registered.prediction_probability.model_dump())
                    if registered.prediction_probability
                    else None,
                    _dump(registered.controls),
                    _dump(registered.metrics),
                    registered.budget,
                    registered.cost_low,
                    registered.cost_high,
                    registered.falsification_criterion,
                    registered.overturn_criterion,
                    _dump(registered.hard_gates),
                    registered.status,
                    now(),
                    None,
                    None,
                    registered.created_at,
                ),
            )
        return registered

    def set_experiment_status(self, id_: str, status: str) -> None:
        self._require("experiments", id_)
        ts_col = {
            "running": "started_at",
            "completed": "completed_at",
            "failed": "completed_at",
        }.get(status)
        with self._tx() as conn:
            if ts_col:
                sql = f"UPDATE experiments SET status = ?, {ts_col} = ? WHERE id = ?"  # ruff: ignore[hardcoded-sql-expression]  ts_col internal
                conn.execute(sql, (status, now(), id_))
            else:
                conn.execute(
                    "UPDATE experiments SET status = ? WHERE id = ?", (status, id_)
                )

    def get_experiment(self, id_: str) -> models.Experiment:
        row = self._fetch("experiments", id_)
        return self._experiment_from_row(row)

    def experiments_by_status(self, status: str) -> list[models.Experiment]:
        rows = self._conn.execute(
            "SELECT * FROM experiments WHERE status = ? ORDER BY created_at", (status,)
        ).fetchall()
        return [self._experiment_from_row(r) for r in rows]

    def all_experiments(self) -> list[models.Experiment]:
        rows = self._conn.execute(
            "SELECT * FROM experiments ORDER BY created_at"
        ).fetchall()
        return [self._experiment_from_row(r) for r in rows]

    def _experiment_from_row(self, row: sqlite3.Row) -> models.Experiment:
        pp = (
            json.loads(row["prediction_probability"])
            if row["prediction_probability"]
            else None
        )
        return models.Experiment(
            id=row["id"],
            question=row["question"],
            rationale=row["rationale"],
            scope=models.Scope(**json.loads(row["scope"])),
            target_beliefs=json.loads(row["target_beliefs"]),
            target_goals=json.loads(row["target_goals"]),
            design=json.loads(row["design"]),
            prediction=row["prediction"],
            prediction_probability=models.Probability(**pp) if pp else None,
            controls=json.loads(row["controls"]),
            metrics=json.loads(row["metrics"]),
            budget=row["budget"],  # type: ignore[arg-type]
            cost_low=row["cost_low"],
            cost_high=row["cost_high"],
            falsification_criterion=row["falsification_criterion"],
            overturn_criterion=row["overturn_criterion"],
            hard_gates=json.loads(row["hard_gates"]),
            status=row["status"],  # type: ignore[arg-type]
            created_at=row["created_at"],
        )

    # -- decisions, gates, statuses, calibration ---------------------------

    def record_decision(
        self,
        state_hash: str,
        candidate_experiments: list[str],
        scores: dict[str, float],
        rationale: str,
        selected_experiment: str | None = None,
        overrides: list[dict[str, Any]] | None = None,
        constraints_checked: dict[str, Any] | None = None,
        id_: str | None = None,
    ) -> models.Decision:
        decision = models.Decision(
            id=self._next_id("decision", "decisions", id_),
            timestamp=now(),
            state_hash=state_hash,
            candidate_experiments=candidate_experiments,
            scores=scores,
            selected_experiment=selected_experiment,
            overrides=overrides or [],
            constraints_checked=constraints_checked or {},
            rationale=rationale,
        )
        with self._tx() as conn:
            conn.execute(
                "INSERT INTO decisions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    decision.id,
                    decision.timestamp,
                    decision.state_hash,
                    _dump(decision.candidate_experiments),
                    _dump(decision.scores),
                    decision.selected_experiment,
                    _dump(decision.overrides),
                    _dump(decision.constraints_checked),
                    decision.rationale,
                ),
            )
        return decision

    def record_gate_outcome(
        self,
        gate: str,
        status: str,
        rationale: str,
        evidence_refs: list[str] | None = None,
        derived_refs: list[str] | None = None,
        belief_id: str | None = None,
        experiment_id: str | None = None,
        id_: str | None = None,
    ) -> models.GateOutcome:
        if belief_id:
            self._require("beliefs", belief_id)
        if experiment_id:
            self._require("experiments", experiment_id)
        for ref in evidence_refs or []:
            self._require("evidence", ref)
        for ref in derived_refs or []:
            self._require("derived", ref)
        outcome = models.GateOutcome(
            id=self._next_id("gate_outcome", "gate_outcomes", id_),
            gate=gate,
            status=status,  # type: ignore[arg-type]
            evidence_refs=evidence_refs or [],
            derived_refs=derived_refs or [],
            rationale=rationale,
            belief_id=belief_id,
            experiment_id=experiment_id,
            created_at=now(),
        )
        with self._tx() as conn:
            conn.execute(
                "INSERT INTO gate_outcomes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    outcome.id,
                    outcome.gate,
                    outcome.belief_id,
                    outcome.experiment_id,
                    outcome.status,
                    _dump(outcome.evidence_refs),
                    _dump(outcome.derived_refs),
                    outcome.rationale,
                    outcome.created_at,
                ),
            )
        return outcome

    def gate_outcomes_for(
        self, belief_id: str | None = None, experiment_id: str | None = None
    ) -> list[models.GateOutcome]:
        clause, params = [], []
        if belief_id:
            clause.append("belief_id = ?")
            params.append(belief_id)
        if experiment_id:
            clause.append("experiment_id = ?")
            params.append(experiment_id)
        where = f"WHERE {' AND '.join(clause)}" if clause else ""
        sql = f"SELECT * FROM gate_outcomes {where} ORDER BY created_at, id"  # ruff: ignore[hardcoded-sql-expression]  clause internal
        rows = self._conn.execute(sql, params).fetchall()
        return [
            models.GateOutcome(
                id=r["id"],
                gate=r["gate"],
                status=r["status"],  # type: ignore[arg-type]
                evidence_refs=json.loads(r["evidence_refs"]),
                derived_refs=json.loads(r["derived_refs"]),
                rationale=r["rationale"],
                belief_id=r["belief_id"],
                experiment_id=r["experiment_id"],
                created_at=r["created_at"],
            )
            for r in rows
        ]

    def change_status(
        self,
        belief_id: str,
        to_status: str,
        reason: str,
        trigger: str | None = None,
        gate_refs: list[str] | None = None,
        evidence_refs: list[str] | None = None,
        derived_refs: list[str] | None = None,
        actor: str | None = None,
        id_: str | None = None,
    ) -> models.StatusChange:
        self._require("beliefs", belief_id)
        for ref in gate_refs or []:
            self._require("gate_outcomes", ref)
        for ref in evidence_refs or []:
            self._require("evidence", ref)
        for ref in derived_refs or []:
            self._require("derived", ref)
        current = self.current_status(belief_id)
        if current == to_status:
            raise StoreError(f"belief {belief_id} already {to_status}")
        if to_status == "open" and current == "boundary" and not trigger:
            raise StoreError("reopening requires a trigger")
        if current == "quarantined" and to_status not in {"quarantined", "open"}:
            raise StoreError("quarantined beliefs may only move to open (unquarantine)")
        if to_status in {"promoted", "boundary"} and not gate_refs:
            raise StoreError(f"{to_status} requires gate outcome refs")
        latest = self.latest_revision(belief_id)
        revision_id = self._next_id("belief_revision", "belief_revisions", None)
        change = models.StatusChange(
            id=self._next_id("status_change", "status_changes", id_),
            belief_id=belief_id,
            from_status=current,  # type: ignore[arg-type]
            to_status=to_status,  # type: ignore[arg-type]
            reason=reason,
            trigger=trigger,
            gate_refs=gate_refs or [],
            evidence_refs=evidence_refs or [],
            derived_refs=derived_refs or [],
            actor=actor,
            created_at=now(),
        )
        latest = self.latest_revision(belief_id)
        with self._tx() as conn:
            conn.execute(
                "INSERT INTO status_changes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    change.id,
                    belief_id,
                    change.from_status,
                    to_status,
                    reason,
                    trigger,
                    _dump(change.gate_refs),
                    _dump(change.evidence_refs),
                    _dump(change.derived_refs),
                    actor,
                    change.created_at,
                ),
            )
            baseline_inserted = latest is None
            if baseline_inserted:
                conn.execute(
                    "INSERT INTO belief_revisions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        revision_id,
                        belief_id,
                        0.0,
                        1.0,
                        None,
                        None,
                        "high",
                        "none",
                        "narrow",
                        "open",
                        "baseline revision created at first status change",
                        change.created_at,
                    ),
                )
            status_revision_id = self._next_id(
                "belief_revision", "belief_revisions", None
            )
            if baseline_inserted:
                low, high, point, method, unc, weight, gen = (
                    0.0,
                    1.0,
                    None,
                    None,
                    "high",
                    "none",
                    "narrow",
                )
            else:
                low = latest.probability.low
                high = latest.probability.high
                point = latest.probability.point
                method = latest.probability.method
                unc = latest.uncertainty
                weight = latest.evidence_weight
                gen = latest.generality
            conn.execute(
                "INSERT INTO belief_revisions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    status_revision_id,
                    belief_id,
                    low,
                    high,
                    point,
                    method,
                    unc,
                    weight,
                    gen,
                    to_status,
                    reason,
                    change.created_at,
                ),
            )
        return change

    def current_status(self, belief_id: str) -> str:
        self._require("beliefs", belief_id)
        row = self._conn.execute(
            "SELECT to_status FROM status_changes WHERE belief_id = ? "
            "ORDER BY created_at DESC, id DESC LIMIT 1",
            (belief_id,),
        ).fetchone()
        if row is not None:
            return row["to_status"]
        rev = self.latest_revision(belief_id)
        return rev.status if rev else "open"

    def record_calibration(
        self,
        prediction: str,
        experiment_id: str | None = None,
        belief_id: str | None = None,
        predicted_probability: models.Probability | None = None,
        outcome: str | None = None,
        outcome_boolean: bool | None = None,
        scope: models.Scope | None = None,
        notes: str | None = None,
        id_: str | None = None,
    ) -> models.CalibrationRecord:
        if experiment_id:
            self._require("experiments", experiment_id)
        if belief_id:
            self._require("beliefs", belief_id)
        brier = log_score = None
        point = predicted_probability.point if predicted_probability else None
        if point is not None and outcome_boolean is not None:
            brier = (point - float(outcome_boolean)) ** 2
            p = min(max(point, 1e-12), 1 - 1e-12)
            y = float(outcome_boolean)
            log_score = y * math.log(p) + (1 - y) * math.log(1 - p)
        record = models.CalibrationRecord(
            id=self._next_id("calibration_record", "calibration_records", id_),
            experiment_id=experiment_id,
            belief_id=belief_id,
            prediction=prediction,
            predicted_probability=predicted_probability,
            outcome=outcome,
            outcome_boolean=outcome_boolean,
            brier_score=brier,
            log_score=log_score,
            scope=scope,
            notes=notes,
            created_at=now(),
        )
        with self._tx() as conn:
            conn.execute(
                "INSERT INTO calibration_records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    record.id,
                    experiment_id,
                    belief_id,
                    prediction,
                    _dump(predicted_probability.model_dump())
                    if predicted_probability
                    else None,
                    outcome,
                    outcome_boolean,
                    brier,
                    log_score,
                    _dump(scope.model_dump()) if scope else None,
                    notes,
                    record.created_at,
                ),
            )
        return record

    def calibration_records(self) -> list[models.CalibrationRecord]:
        rows = self._conn.execute(
            "SELECT * FROM calibration_records ORDER BY created_at"
        ).fetchall()
        return [
            models.CalibrationRecord(
                id=r["id"],
                experiment_id=r["experiment_id"],
                belief_id=r["belief_id"],
                prediction=r["prediction"],
                predicted_probability=(
                    models.Probability(**json.loads(r["predicted_probability"]))
                    if r["predicted_probability"]
                    else None
                ),
                outcome=r["outcome"],
                outcome_boolean=bool(r["outcome_boolean"])
                if r["outcome_boolean"] is not None
                else None,
                brier_score=r["brier_score"],
                log_score=r["log_score"],
                scope=models.Scope(**json.loads(r["scope"])) if r["scope"] else None,
                notes=r["notes"],
                created_at=r["created_at"],
            )
            for r in rows
        ]

    def record_instrument_note(
        self,
        belief_id: str,
        note: str,
        kind: str = "observation",
        id_: str | None = None,
    ) -> models.InstrumentNote:
        self._require("beliefs", belief_id)
        obj = models.InstrumentNote(
            id=self._next_id("instrument_note", "instrument_notes", id_),
            belief_id=belief_id,
            note=note,
            kind=kind,  # type: ignore[arg-type]
            created_at=now(),
        )
        with self._tx() as conn:
            conn.execute(
                "INSERT INTO instrument_notes VALUES (?, ?, ?, ?, ?)",
                (obj.id, belief_id, note, kind, obj.created_at),
            )
        return obj

    # -- internals ---------------------------------------------------------

    def _fetch(self, table: str, id_: str) -> sqlite3.Row:
        row = self._conn.execute(
            f"SELECT * FROM {table} WHERE id = ?",  # ruff: ignore[hardcoded-sql-expression] - internal
            (id_,),
        ).fetchone()
        if row is None:
            raise StoreError(
                f"{table[:-1] if table.endswith('s') else table} {id_!r} not found"
            )
        return row

    def _require(self, table: str, id_: str | None) -> None:
        if id_ is None:
            raise StoreError(f"missing required reference into {table}")
        row = self._conn.execute(
            f"SELECT 1 FROM {table} WHERE id = ?",  # ruff: ignore[hardcoded-sql-expression] - internal
            (id_,),
        ).fetchone()
        if row is None:
            raise StoreError(f"referenced row missing in {table}: {id_!r}")

    def _has_links(self, belief_id: str, *link_tables: tuple[str, str]) -> bool:
        for table, col in link_tables:
            row = self._conn.execute(
                f"SELECT 1 FROM {table} WHERE belief_id = ? LIMIT 1",  # ruff: ignore[hardcoded-sql-expression]
                (belief_id,),
            ).fetchone()
            if row is not None:
                return True
        return False

    @staticmethod
    def _link(
        conn: sqlite3.Connection,
        table: str,
        left_col: str,
        left_id: str,
        right_col: str,
        right_ids: list[str] | None,
    ) -> None:
        if not right_ids:
            return
        sql = f"INSERT OR IGNORE INTO {table} ({left_col}, {right_col}) VALUES (?, ?)"  # ruff: ignore[hardcoded-sql-expression]  internal
        conn.executemany(sql, [(left_id, rid) for rid in right_ids])


def artifact_file_bytes(path: Path) -> bytes:
    return path.read_bytes()


def copy_artifact_into_place(source: Path, target: Path) -> None:
    shutil.copy2(source, target)
