"""Record APIs: append-only writes into the ledger."""

from __future__ import annotations

import hashlib
import logging
import math
from pathlib import Path
from typing import Any

from ceec import models
from ceec.profile import DEFAULT_PROFILE
from ceec.store.query import QueryMixin
from ceec.store.schema import _INPUT_NAMESPACE, StoreError, _dump, now

logger = logging.getLogger(__name__)


class RecordsMixin(QueryMixin):
    """Append-only record surface; connection state lives on CEECStore."""

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
            # content-addressed store: an existing file with the digest's
            # name IS the artifact (e.g. a fresh ledger over a shared
            # artifacts dir); only a mismatched payload is a collision
            if hashlib.sha256(uri.read_bytes()).hexdigest() != digest:
                raise StoreError(f"artifact file collision at {uri}")
        else:
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

    def record_evidence(  # noqa: PLR0913  mirrors evidence fields
        self,
        kind: str,
        scope: models.Scope,
        *,
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
        (self.profile or DEFAULT_PROFILE).quality.validate(quality or {})
        self._validate_scope(scope)
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

    def link_belief_evidence(self, belief_id: str, evidence_ids: list[str]) -> None:
        """Attach evidence to a belief and flush (public ingest surface)."""
        self._require("beliefs", belief_id)
        self._link(
            self._conn,
            "belief_evidence",
            "belief_id",
            belief_id,
            "evidence_id",
            evidence_ids,
        )
        self._conn.commit()

    def record_derived(  # noqa: PLR0913  mirrors derived fields
        self,
        type_: str,
        operator: str,
        inputs: dict[str, list[str]],
        scope: models.Scope,
        *,
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
        profile = self.profile or DEFAULT_PROFILE
        if experiment.budget not in profile.budget_tiers:
            raise StoreError(
                f"budget {experiment.budget!r} not in profile tiers "
                f"{profile.budget_tiers}"
            )
        self._validate_scope(experiment.scope)
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
                sql = f"UPDATE experiments SET status = ?, {ts_col} = ? WHERE id = ?"  # noqa: S608  ts_col internal
                conn.execute(sql, (status, now(), id_))
            else:
                conn.execute(
                    "UPDATE experiments SET status = ? WHERE id = ?", (status, id_)
                )

    def record_decision(
        self,
        state_hash: str,
        candidate_experiments: list[str],
        scores: dict[str, float],
        rationale: str,
        *,
        selected_experiment: str | None = None,
        overrides: list[dict[str, Any]] | None = None,
        constraints_checked: dict[str, Any] | None = None,
        policy_version: str | None = None,
        id_: str | None = None,
    ) -> models.Decision:
        policy_version = policy_version or (
            self.profile.policy_version if self.profile else None
        )
        decision = models.Decision(
            id=self._next_id("decision", "decisions", id_),
            timestamp=now(),
            state_hash=state_hash,
            candidate_experiments=candidate_experiments,
            scores=scores,
            selected_experiment=selected_experiment,
            overrides=overrides or [],
            constraints_checked=constraints_checked or {},
            policy_version=policy_version,
            rationale=rationale,
        )
        with self._tx() as conn:
            conn.execute(
                "INSERT INTO decisions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    decision.id,
                    decision.timestamp,
                    decision.state_hash,
                    _dump(decision.candidate_experiments),
                    _dump(decision.scores),
                    decision.selected_experiment,
                    _dump(decision.overrides),
                    _dump(decision.constraints_checked),
                    decision.policy_version,
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
            policy_version=self.profile.policy_version if self.profile else None,
            created_at=now(),
        )
        with self._tx() as conn:
            conn.execute(
                "INSERT INTO calibration_records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
                    record.policy_version,
                    record.created_at,
                ),
            )
        return record

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

    def _validate_scope(self, scope: models.Scope) -> None:
        """Declared scope dims are type-checked; unknown dims stay open (§6)."""
        for dim, expected in (self.profile or DEFAULT_PROFILE).scope_dimensions.items():
            value = scope.dims.get(dim)
            if value is not None and not isinstance(value, expected):
                raise StoreError(
                    f"scope dim {dim}={value!r} is not {expected.__name__}"
                )
