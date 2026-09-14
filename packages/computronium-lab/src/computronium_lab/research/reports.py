"""Research reports, belief promotion, and calibration (TODO24 Phase 6).

Converts corpus and evolution artifacts into durable outputs: registered
hypothesis reports (H24.1–H24.6), markdown/JSON reports, promotion attempts
through the existing ``promote_mechanism`` pipeline (honest refusal when
campaigns do not pass), the failure manifesto, and pre-registered
prediction calibration via ``ceec.calibration``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from ceec.store import CEECStore

    from computronium_lab.campaign import MechanismBelief
    from computronium_lab.lab import Lab
    from computronium_lab.research.continual import ContinualReport
    from computronium_lab.research.corpus import CorpusReport
    from computronium_lab.research.evolution import EvolutionReport
    from computronium_lab.research.substrate import TransferReport
    from computronium_lab.synthesis.spec import ProblemSpec

__all__ = [
    "HYPOTHESES",
    "HypothesisSpec",
    "attempt_promotion",
    "build_failure_manifesto",
    "preregister_hypotheses",
    "render_continual",
    "render_corpus",
    "render_evolution",
    "render_ledger",
    "render_manifesto",
    "render_transfer",
    "score_hypotheses",
    "write_hypothesis_reports",
]


@dataclass(frozen=True, slots=True)
class HypothesisSpec:
    """One registered H24 hypothesis with its protocol and prior."""

    id: str
    statement: str
    protocol: str
    prior: float
    status: str = "open"
    evidence_refs: str = ""


HYPOTHESES: tuple[HypothesisSpec, ...] = (
    HypothesisSpec(
        id="H24.1",
        statement=(
            "Evolutionary search over valid 6-axis coordinates produces "
            "non-dominated candidates not present in the initial catalog "
            "for at least one problem class."
        ),
        protocol="frontier archive comparison: initial catalog frontier vs post-evolution frontier",
        prior=0.6,
    ),
    HypothesisSpec(
        id="H24.2",
        statement=(
            "Campaign-backed fitness prevents quick-task overfitting better "
            "than predictor-only search."
        ),
        protocol="surrogate-ranked candidates vs campaign-validated outcomes (rank agreement)",
        prior=0.7,
    ),
    HypothesisSpec(
        id="H24.3",
        statement=(
            "ψ-only adaptation improves task-switch speed relative to θ "
            "fine-tuning under matched compute on at least one synthetic "
            "curriculum."
        ),
        protocol="paired statistical test across seeds with equal episode/compute budgets",
        prior=0.6,
    ),
    HypothesisSpec(
        id="H24.4",
        statement=(
            "Substrate-transfer robustness is mechanism-dependent and can be "
            "ranked by fidelity, accuracy delta, and export success."
        ),
        protocol="transfer campaign across mechanisms and substrate constraints",
        prior=0.75,
    ),
    HypothesisSpec(
        id="H24.5",
        statement=(
            "Stability and resource constraints can be used as hard search "
            "constraints without collapsing the candidate space."
        ),
        protocol="constitution rejection report plus surviving certified candidates",
        prior=0.7,
    ),
    HypothesisSpec(
        id="H24.6",
        statement=(
            "Corpus-driven refit improves or honestly bounds the I(C,U,P) "
            "viability model."
        ),
        protocol="held-out evaluation before/after corpus expansion, or recorded sampling boundary",
        prior=0.5,
    ),
)


def write_hypothesis_reports(
    out_dir: str | Path, statuses: Mapping[str, HypothesisSpec] | None = None
) -> list[Path]:
    """Write ``hypotheses/H24.*.md`` (T24.6.1); returns written paths."""
    directory = Path(out_dir)
    directory.mkdir(parents=True, exist_ok=True)
    resolved = statuses or {h.id: h for h in HYPOTHESES}
    written: list[Path] = []
    for hypothesis in HYPOTHESES:
        current = resolved.get(hypothesis.id, hypothesis)
        path = directory / f"{hypothesis.id}.md"
        path.write_text(
            "\n".join([
                f"# {hypothesis.id} — Registered Hypothesis",
                "",
                f"**Status:** {current.status}",
                "",
                "## Statement",
                "",
                hypothesis.statement,
                "",
                "## Protocol",
                "",
                hypothesis.protocol,
                "",
                "## Prior",
                "",
                f"Pre-registered prediction probability point: {hypothesis.prior}",
                "",
                "## Evidence",
                "",
                current.evidence_refs or "No campaign evidence recorded yet.",
                "",
            ]),
            encoding="utf-8",
        )
        written.append(path)
    return written


def preregister_hypotheses(store: CEECStore, run_id: str) -> dict[str, str]:
    """Pre-register H24 predictions as ceec Experiments (T24.6.6 setup).

    Returns a mapping of hypothesis id → experiment id. Priors are the
    session's honest starting beliefs, recorded before outcomes.
    """
    from ceec.models import Experiment, Probability, Scope
    from ceec.store import now

    ids: dict[str, str] = {}
    for hypothesis in HYPOTHESES:
        experiment_id = f"X-H24-{hypothesis.id.replace('.', '')}-{run_id}".replace(
            ":", ""
        )
        experiment = Experiment(
            id=experiment_id,
            question=hypothesis.statement,
            rationale=f"TODO24 registered hypothesis {hypothesis.id}",
            scope=Scope(
                domain="research",
                substrate=("digital",),
                budget="quick",
                extra={"hypothesis": hypothesis.id, "run_id": run_id},
            ),
            target_beliefs=[],
            target_goals=[],
            design={
                "seed_plan": [0, 1, 2],
                "evaluation_policy": "hypothesis_protocol_v1",
                "evidence_kind": "vector",
                "protocol": hypothesis.protocol,
            },
            prediction=hypothesis.statement,
            prediction_probability=Probability(
                low=round(max(0.0, hypothesis.prior - 0.2), 3),
                high=round(min(1.0, hypothesis.prior + 0.2), 3),
                point=hypothesis.prior,
                method="session_prior",
            ),
            controls=[],
            metrics=["accuracy"],
            budget="quick",
            falsification_criterion=f"{hypothesis.id} protocol finds no effect",
            overturn_criterion=f"{hypothesis.id} protocol overturns on replication",
            hard_gates=["BenchmarkReproduction"],
            created_at=now(),
        )
        store.pre_register_experiment(experiment)
        ids[hypothesis.id] = experiment_id
    return ids


def score_hypotheses(
    store: CEECStore,
    experiment_ids: Mapping[str, str],
    outcomes: Mapping[str, tuple[str, bool]],
) -> dict[str, object]:
    """Score pre-registered H24 predictions on outcome (T24.6.6).

    ``outcomes`` maps hypothesis id → (outcome label, success boolean).
    Returns the ceec calibration report plus per-hypothesis scores.
    """
    from ceec.calibration import calibration_report, record_experiment_outcome

    scored: dict[str, object] = {}
    for hypothesis_id, experiment_id in experiment_ids.items():
        if hypothesis_id not in outcomes:
            continue
        label, success = outcomes[hypothesis_id]
        store.set_experiment_status(experiment_id, "completed")
        record = record_experiment_outcome(
            store, experiment_id, outcome=label, outcome_boolean=success
        )
        if record is not None:
            scored[hypothesis_id] = {
                "outcome": label,
                "brier_score": record.brier_score,
                "log_score": record.log_score,
            }
    return {"scored": scored, "report": calibration_report(store)}


def attempt_promotion(
    lab: Lab,
    mechanism: str,
    specs: Sequence[ProblemSpec],
    *,
    seeds: tuple[int, ...] = (0, 1, 2),
    epochs: int = 20,
    belief_id: str | None = None,
) -> tuple[MechanismBelief | None, str]:
    """Promote through ``promote_mechanism`` or refuse honestly (T24.6.3).

    Returns ``(belief, "")`` on promotion, ``(None, reason)`` on refusal.
    Requires ``lab.record_ledger``; smoke/quick tiers refuse (no campaign
    evidence at certified operating points).
    """
    if not lab.record_ledger:
        return None, "refused: promotion requires a ledger-backed Lab"
    from computronium_lab.campaign import promote_mechanism

    try:
        belief = promote_mechanism(
            lab,
            mechanism,
            list(specs),
            seeds=seeds,
            epochs=epochs,
            belief_id=belief_id,
        )
    except Exception as exc:
        return None, f"refused: promotion pipeline failed: {exc}"
    if not belief.promoted:
        return None, (
            f"refused: belief {belief.belief_id} not promoted "
            f"(violations: {list(belief.violations)})"
        )
    return belief, ""


def render_evolution(report: EvolutionReport) -> str:
    """Markdown evolution report: lineage, frontier, negatives."""
    lines = [
        f"# Evolution Report `{report.run_id}`",
        "",
        f"Spec: `{report.spec_key}` — tier: {report.tier}",
        "",
        "## Best candidates",
        "",
    ]
    for candidate in report.best_candidates:
        lines.append(
            f"- {candidate.mechanism} (`{candidate.genome_digest}`): "
            + ", ".join(
                f"{name}={value:.3f}" for name, value in candidate.objectives.items()
            )
            + f" — certified={candidate.certified}"
        )
    lines.extend(["", "## Generations", ""])
    for summary in report.generation_summaries:
        lines.append(
            f"### Generation {summary.generation} "
            f"(hypervolume {summary.hypervolume:.4f}, grew={summary.grew})"
        )
        for evaluated in summary.evaluated:
            objectives = cast("Mapping[str, object]", evaluated["objectives"])
            lines.append(
                f"- {evaluated['mechanism']}: "
                f"accuracy={float(cast('float', objectives['accuracy'])):.3f} "
                f"reproduction={evaluated['reproduction']}"
            )
        lines.append("")
    lines.extend(["## Lineage", ""])
    for digest, parents in report.lineage.items():
        lines.append(f"- `{digest}` ← {', '.join(parents) or 'seed'}")
    lines.extend(["", "## Calibration", ""])
    for calibration in report.calibration:
        lines.append(
            f"- {calibration['experiment_id']}: {calibration['outcome']} "
            f"(brier={calibration['brier_score']:.3f})"
        )
    lines.append("")
    return "\n".join(lines)


def render_corpus(report: CorpusReport) -> str:
    """Markdown corpus report: per-arm statistics and blocks."""
    lines = [
        f"# Corpus Report — {report.problem_class}",
        "",
        f"Spec: `{report.spec_key}` — tier: {report.tier} — run: {report.run_id}",
        "",
    ]
    for arm in report.arms:
        lines.append(f"## Arm `{arm.arm}`")
        for metric, summary in arm.summaries.items():
            paired = (
                f", paired_p={summary.paired_p:.3f}"
                if summary.paired_p is not None
                else ""
            )
            lines.append(
                f"- {metric}: mean={summary.mean:.3f} std={summary.std:.3f} "
                f"ci=[{summary.ci_low:.3f}, {summary.ci_high:.3f}]{paired}"
            )
        lines.append("")
    if report.blocks:
        lines.extend(["## Measurement blocks", ""])
        for block in report.blocks:
            lines.append(f"- {block.mechanism}: {block.reason}")
        lines.append("")
    return "\n".join(lines)


def render_continual(report: ContinualReport) -> str:
    """Markdown continual benchmark report."""
    lines = [
        f"# Continual Benchmark — {report.mechanism} / {report.curriculum}",
        "",
        "## Mode vs control (paired)",
        "",
    ]
    for comparison in report.comparisons:
        lines.append(
            f"- {comparison.mode} vs {comparison.control}: "
            f"mean_diff={comparison.mean_diff:+.3f} paired_p={comparison.paired_p}"
        )
    lines.extend(["", "## θ invariance", ""])
    for arm, proofs in report.invariance_proofs.items():
        latest: Mapping[str, object] = proofs[-1] if proofs else {}
        lines.append(
            f"- {arm}: invariant={latest.get('invariant')} "
            f"psi_changed={latest.get('psi_changed')}"
        )
    lines.extend(["", "## State inventory", ""])
    lines.extend(f"- {item}" for item in report.state_inventory)
    lines.append("")
    return "\n".join(lines)


def render_transfer(report: TransferReport) -> str:
    """Markdown substrate-transfer report."""
    lines = [
        f"# Substrate Transfer — {report.mechanism} "
        f"(source: {report.source_substrate})",
        "",
        f"Robustness ranking: {' > '.join(report.ranking)}",
        "",
    ]
    for target in report.targets:
        rows = [s for s in report.scores if s.target == target]
        if not rows:
            continue
        mean_delta = sum(s.accuracy_delta for s in rows) / len(rows)
        mean_fidelity = sum(s.fidelity for s in rows) / len(rows)
        exports = sum(1 for s in rows if s.export_success)
        lines.append(
            f"## {target}: Δacc={mean_delta:+.3f} "
            f"fidelity={mean_fidelity:.4f} exports={exports}/{len(rows)} "
            "(energy: simulated tier)"
        )
    lines.append("")
    return "\n".join(lines)


def render_ledger(store: CEECStore) -> tuple[str, dict[str, object]]:
    """Ledger rollup — experiments, beliefs, calibration, decisions (T25.C.3).

    Returns ``(markdown, data)``; the calibration section carries the §24
    ``review_flags`` and per-belief Brier drift, the decisions section the
    ``audit_decisions`` findings. Read-only: no Derived is recorded.
    """
    from ceec.audit import audit_decisions
    from ceec.calibration import belief_drift, calibration_report, review_flags

    experiments: dict[str, list[str]] = {}
    for experiment in store.all_experiments():
        experiments.setdefault(experiment.status, []).append(experiment.id)
    beliefs: dict[str, list[str]] = {}
    belief_rows = store._conn.execute("SELECT id FROM beliefs").fetchall()
    for row in belief_rows:
        beliefs.setdefault(store.current_status(row["id"]), []).append(row["id"])
    calibration = dict(calibration_report(store))
    flags = review_flags(calibration)
    calibration["review_flags"] = flags
    drift = {
        belief_id: {"drift": entry["drift"], "flagged": entry["flagged"]}
        for belief_id, entry in belief_drift(store).items()
        if entry["flagged"]
    }
    findings, audit_summary = audit_decisions(store)
    decision_rows = store._conn.execute(
        "SELECT id, selected_experiment, rationale FROM decisions ORDER BY timestamp"
    ).fetchall()
    data: dict[str, object] = {
        "experiments": experiments,
        "beliefs": beliefs,
        "calibration": calibration,
        "belief_drift": drift,
        "decisions": {
            "count": len(decision_rows),
            "audit": audit_summary,
            "findings": [
                {"check": f.check, "severity": f.severity, "detail": f.detail}
                for f in findings
            ],
        },
    }
    lines = ["# Ledger Report", ""]
    lines.append("## Experiments")
    lines.append("")
    for status in sorted(experiments):
        lines.append(
            f"- **{status}** ({len(experiments[status])}): "
            + ", ".join(experiments[status])
        )
    lines.extend(["", "## Beliefs", ""])
    for status in sorted(beliefs):
        lines.append(
            f"- **{status}** ({len(beliefs[status])}): " + ", ".join(beliefs[status])
        )
    lines.extend(["", "## Calibration", ""])
    lines.append(
        f"- records: {calibration['calibration_records']} "
        f"(scored {calibration['scored_records']}), "
        f"mean Brier {calibration['mean_brier']}"
    )
    lines.append(
        f"- promotions {calibration['promotions']}, boundaries "
        f"{calibration['boundaries']}, quarantines {calibration['quarantines']}, "
        f"override rate {calibration['override_rate']:.2f}"
    )
    lines.append(f"- review flags: {flags or 'none'}")
    lines.append(
        "- Brier drift > tau: "
        + (
            ", ".join(f"{b} ({e['drift']:.2f})" for b, e in drift.items())
            if drift
            else "none"
        )
    )
    lines.extend(["", "## Decisions", ""])
    lines.append(
        f"- {audit_summary['decisions']} decisions; audit findings: "
        f"{audit_summary['findings']}"
    )
    for finding in data["decisions"]["findings"]:  # type: ignore[index]
        lines.append(
            f"  - [{finding['severity']}] {finding['check']}: {finding['detail']}"
        )
    lines.append("")
    return "\n".join(lines), data


def _evolution_negatives(
    evolution_reports: Sequence[EvolutionReport],
    failed_candidates: list[dict[str, object]],
    failed_mutations: list[dict[str, object]],
) -> None:
    for report in evolution_reports:
        for negative in report.negative_results:
            bucket = (
                failed_mutations
                if negative.get("kind") == "constitution_rejection"
                else failed_candidates
            )
            bucket.append({**negative, "run_id": report.run_id})


def _corpus_mismatches(
    corpus_reports: Sequence[CorpusReport],
    mismatches: list[dict[str, object]],
) -> None:
    for report in corpus_reports:
        for block in report.blocks:
            mismatches.append({
                "problem_class": block.problem_class,
                "mechanism": block.mechanism,
                "reason": block.reason,
                "run_id": report.run_id,
            })


def _transfer_failures(
    transfer_reports: Sequence[TransferReport],
    failed_transfers: list[dict[str, object]],
) -> None:
    for report in transfer_reports:
        for block in report.blocks:
            failed_transfers.append({
                "target": block.mechanism,
                "reason": block.reason,
                "run_id": "transfer",
            })
        for score in report.scores:
            if not score.export_success or score.accuracy_delta < -0.2:
                failed_transfers.append({
                    "target": f"{score.target}/seed{score.seed}",
                    "reason": (
                        f"export_success={score.export_success} "
                        f"Δacc={score.accuracy_delta:+.3f}"
                    ),
                    "run_id": "transfer",
                })


def _continual_mismatches(
    continual_reports: Sequence[ContinualReport],
    mismatches: list[dict[str, object]],
) -> None:
    for report in continual_reports:
        for block in report.blocks:
            mismatches.append({
                "problem_class": "continual_switch",
                "mechanism": block.mechanism,
                "reason": block.reason,
                "run_id": "continual",
            })


def build_failure_manifesto(
    evolution_reports: Sequence[EvolutionReport] = (),
    corpus_reports: Sequence[CorpusReport] = (),
    transfer_reports: Sequence[TransferReport] = (),
    continual_reports: Sequence[ContinualReport] = (),
) -> dict[str, object]:
    """Structured negative results across all TODO24 products (T24.6.4)."""
    failed_candidates: list[dict[str, object]] = []
    failed_mutations: list[dict[str, object]] = []
    failed_transfers: list[dict[str, object]] = []
    mismatches: list[dict[str, object]] = []
    _evolution_negatives(evolution_reports, failed_candidates, failed_mutations)
    _corpus_mismatches(corpus_reports, mismatches)
    _transfer_failures(transfer_reports, failed_transfers)
    _continual_mismatches(continual_reports, mismatches)
    return {
        "failed_candidates": failed_candidates,
        "failed_mutations": failed_mutations,
        "failed_transfers": failed_transfers,
        "task_class_mismatches": mismatches,
    }


def render_manifesto(manifesto: Mapping[str, object]) -> str:
    """Markdown failure manifesto."""
    lines = ["# Failure Manifesto (TODO24 negative results)", ""]
    for section in (
        "failed_candidates",
        "failed_mutations",
        "failed_transfers",
        "task_class_mismatches",
    ):
        items = cast("Sequence[object]", manifesto.get(section, []))
        lines.append(f"## {section} ({len(items)})")
        lines.append("")
        for item in items[:50]:
            lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines)
