"""Query APIs: read-side getters and listings."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from ceec import models
from ceec.store.base import StoreBase

if TYPE_CHECKING:
    import sqlite3


class QueryMixin(StoreBase):
    """Read-only ledger queries."""

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
        sql = f"SELECT * FROM gate_outcomes {where} ORDER BY created_at, id"  # noqa: S608  clause internal
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
                policy_version=r["policy_version"],
                created_at=r["created_at"],
            )
            for r in rows
        ]
