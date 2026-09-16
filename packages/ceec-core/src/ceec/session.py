"""Session façade over the CEEC ledger (TODO26 T26.D.1/D.3).

One object binds a ledger file, a :class:`~ceec.profile.Profile`, and a
:class:`~ceec.profile.LedgerRole`; every kernel operation is a method.
Probes and domain adapters construct sessions via :func:`ledger` instead
of hand-assembling payloads around the store record API.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Self

from ceec.audit import Finding, run_audit
from ceec.builders import experiment as _experiment_builder
from ceec.gates import Evaluation, declare_boundary, promote
from ceec.profile import DEFAULT_PROFILE, LedgerRole, Profile
from ceec.report import render_ledger
from ceec.run import ExperimentRun, ProbeResult, record_result, run_experiment
from ceec.selection import check_hard_constraints, decide
from ceec.store import CEECStore

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

    from ceec import models

__all__ = ["CloseReport", "Session", "ledger"]


def ledger(
    path: Path | str,
    profile: Profile,
    *,
    role: LedgerRole | str = LedgerRole.CAMPAIGN,
) -> Session:
    """Open a :class:`Session` over a ledger file."""
    db = Path(path)
    store = CEECStore(db, db.parent / "artifacts", role=role, profile=profile)
    return Session(store=store, profile=profile, role=LedgerRole(role))


@dataclass(frozen=True, slots=True)
class CloseReport:
    """Round close: rollup render + audit + drift flags (T26.D.3)."""

    markdown: str
    data: dict[str, object]
    findings: tuple[Finding, ...]
    violations: tuple[str, ...]

    @property
    def clean(self) -> bool:
        return not self.violations


class Session:
    """Profile-bound façade over :class:`ceec.store.CEECStore`."""

    def __init__(self, *, store: CEECStore, profile: Profile, role: LedgerRole) -> None:
        self.store = store
        self.profile = profile
        self.role = role
        self._experiment_seq = len(store.all_experiments())

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_) -> None:
        self.store.close()

    # -- construction ------------------------------------------------------

    def experiment(  # ruff: ignore[too-many-arguments]  mirrors the Experiment field surface
        self,
        *,
        question: str,
        prediction: str,
        scope: models.Scope,
        rationale: str = "session-constructed experiment",
        targets: Sequence[str] = (),
        goals: Sequence[str] = (),
        design: Mapping[str, Any] | None = None,
        tier: str | None = None,
        budget: str | None = None,
        prediction_probability: object = None,
        controls: Sequence[str] = ("seed_catalog_baseline",),
        metrics: Sequence[str] = ("accuracy",),
        falsification_criterion: str | None = None,
        overturn_criterion: str | None = None,
        hard_gates: Sequence[str] | None = None,
    ) -> models.Experiment:
        """Build a draft experiment; ``tier`` resolves through the profile."""
        tier_budget = self.profile.tier_budget or {}
        resolved_budget = (
            budget
            or (tier_budget.get(tier) if tier else None)
            or (tier if tier in self.profile.budget_tiers else None)
            or "quick"
        )
        self._experiment_seq += 1
        return _experiment_builder(
            id_=f"X-{self._experiment_seq:06d}",
            question=question,
            prediction=prediction,
            scope=scope,
            rationale=rationale,
            design=dict(design or {}),
            tier=resolved_budget,
            budget=resolved_budget,
            prediction_probability=prediction_probability,  # type: ignore[arg-type]
            target_beliefs=targets,
            target_goals=goals,
            controls=controls,
            metrics=metrics,
            falsification_criterion=falsification_criterion,
            overturn_criterion=overturn_criterion,
            hard_gates=hard_gates,
        )

    def artifact(
        self,
        payload: bytes,
        type_: str,
        provenance: Mapping[str, Any] | None = None,
    ) -> models.Artifact:
        return self.store.ingest_artifact(payload, type_, dict(provenance or {}))

    def evidence(
        self,
        scope: models.Scope,
        *,
        artifact_refs: Sequence[str] = (),
        axes: Sequence[str] = (),
        values: Sequence[float] = (),
        values_ref: str = "",
        quality: Mapping[str, Any] | None = None,
        notes: str | None = None,
        **flags: Any,
    ) -> models.Evidence:
        """Gate-ready evidence; quality validated against the profile schema."""
        from ceec.builders import gate_evidence

        merged = {**(dict(quality) if quality else {}), **flags}
        (self.profile or DEFAULT_PROFILE).quality.validate(merged)
        if values or (axes and values_ref):
            return gate_evidence(
                self.store,
                scope,
                axes=tuple(axes),
                values=tuple(values),
                values_ref=values_ref or None,
                artifact_refs=tuple(artifact_refs),
                notes=notes,
                **merged,
            )
        if not artifact_refs:
            from ceec.store import StoreError

            raise StoreError("evidence requires artifact_refs or values")
        return self.store.record_evidence(
            "scalar",
            scope,
            artifact_refs=list(artifact_refs),
            quality=merged,
            notes=notes,
        )

    # -- selection / closed loop -------------------------------------------

    def decide(
        self,
        *,
        rationale: str,
        candidate_ids: Sequence[str] | None = None,
        focus_id: str | None = None,
        overrides: Sequence[Mapping[str, Any]] = (),
        validator: Callable[[Any], None] | None = None,
    ) -> models.Decision:
        """§22 loop with native focus fallback (replaces the StoreError hack).

        ``focus_id`` pre-checks the focus candidate's hard constraints; the
        selection override is recorded only when the focus is eligible,
        otherwise selection falls back to the highest-EV eligible candidate.
        """
        recorded = [dict(o) for o in overrides]
        if focus_id is not None and focus_id in set(candidate_ids or ()):
            experiment = self.store.get_experiment(focus_id)
            failed = [
                c
                for c in check_hard_constraints(
                    self.store, experiment, validator, self.profile
                )
                if not c.passed
            ]
            if not failed:
                recorded.append({
                    "rationale": (
                        "surrogate-ranked measurement focus within the "
                        "eligible set; hard constraints already enforced"
                    ),
                    "select_experiment": focus_id,
                })
            else:
                rationale += (
                    f" focus {focus_id} fell back to default selection "
                    f"(failed: {', '.join(c.name for c in failed)})"
                )
        return decide(
            self.store,
            self.profile,
            rationale,
            coordinate_validator=validator,
            overrides=recorded,
            candidate_ids=list(candidate_ids) if candidate_ids is not None else None,
        )

    def run(
        self,
        exp: models.Experiment | str,
        probe: Callable[[models.Experiment], ProbeResult],
        *,
        evaluate: str | None = None,
        decision_rationale: str | None = None,
    ) -> ExperimentRun:
        """Closed-loop run: pre-register → decide → probe → ingest → gates."""
        return run_experiment(
            self.store,
            exp,
            probe,
            evaluate=evaluate,  # type: ignore[arg-type]
            decision_rationale=decision_rationale,
        )

    def record_result(
        self,
        exp: models.Experiment | str,
        result: ProbeResult,
        *,
        evaluate: str | None = None,
    ) -> ExperimentRun:
        """Manual-control closed loop: the caller executes the probe."""
        from ceec.store import StoreError

        experiment = self._ensure_registered(exp)
        failed = [
            c
            for c in check_hard_constraints(self.store, experiment, None, self.profile)
            if not c.passed
        ]
        if failed:
            raise StoreError(
                f"experiment {experiment.id} failed hard constraints: "
                + "; ".join(f"{c.name} ({c.detail})" for c in failed)
            )
        decision = self.decide(
            rationale=f"record_result: single pre-registered candidate {experiment.id}",
            candidate_ids=[experiment.id],
            overrides=[
                {
                    "rationale": (
                        "closed-loop run: the pre-registered experiment is the "
                        "only candidate in this decision's pool"
                    ),
                    "select_experiment": experiment.id,
                }
            ],
        )
        self.store.set_experiment_status(experiment.id, "running")
        try:
            artifact_id, evidence_id, calibration_id = record_result(
                self.store, experiment, result
            )
        except Exception:
            self.store.set_experiment_status(experiment.id, "failed")
            raise
        self.store.set_experiment_status(experiment.id, "completed")
        evaluation = self._evaluate(experiment, evaluate)
        return ExperimentRun(
            experiment_id=experiment.id,
            status="completed",
            decision_id=decision.id,
            artifact_id=artifact_id,
            evidence_id=evidence_id,
            calibration_id=calibration_id,
            evaluation=evaluation,
            outcome=result.label,
        )

    def _ensure_registered(self, exp: models.Experiment | str) -> models.Experiment:
        if isinstance(exp, str):
            registered = self.store.get_experiment(exp)
            if registered.status != "pre_registered":
                from ceec.store import StoreError

                raise StoreError(
                    f"experiment {exp} is {registered.status!r}; "
                    "a pre_registered experiment is required"
                )
            return registered
        if exp.status != "draft":
            from ceec.store import StoreError

            raise StoreError(f"experiment {exp.id} is {exp.status!r}; drafts only")
        return self.store.pre_register_experiment(exp)

    def _evaluate(
        self, experiment: models.Experiment, evaluate: str | None
    ) -> Evaluation | None:
        if evaluate is None:
            return None
        if not experiment.target_beliefs:
            from ceec.store import StoreError

            raise StoreError(
                f"evaluate={evaluate!r} requires target_beliefs on {experiment.id}"
            )
        belief_id = experiment.target_beliefs[0]
        if evaluate == "boundary":
            return declare_boundary(
                self.store, belief_id, f"session {experiment.id}", self.profile
            )
        return promote(self.store, belief_id, f"session {experiment.id}", self.profile)

    # -- reporting ----------------------------------------------------------

    def render(self, path: Path | str | None = None) -> tuple[str, dict[str, object]]:
        markdown, data = render_ledger(self.store)
        if path is not None:
            out = Path(path)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.with_suffix(".md").write_text(markdown, encoding="utf-8")
            out.with_suffix(".json").write_text(
                json.dumps(data, indent=2, default=str), encoding="utf-8"
            )
        return markdown, data

    def audit(self) -> list[Finding]:
        return run_audit(self.store)

    def calibration_report(self) -> dict[str, object]:
        from ceec.calibration import calibration_report as _report

        return _report(self.store)

    def close_round(self, *, fail_on_trigger: bool = False) -> CloseReport:
        """Render + audit + drift flags in one report (TODO25 #10c)."""
        from ceec.calibration import review_flags

        markdown, data = self.render()
        findings = self.audit()
        flags = review_flags(self.calibration_report())
        violations = tuple(
            f.check for f in findings if f.severity == "violation"
        ) + tuple(flags)
        report = CloseReport(
            markdown=markdown,
            data=data,
            findings=tuple(findings),
            violations=violations,
        )
        if fail_on_trigger and violations:
            raise SystemExit(
                "close_round triggers: " + ", ".join(sorted(set(violations)))
            )
        return report
