"""Compartment adapters (TODO24 T24.2.8): thin joins, no cross-imports.

Purity contract (verified by test): no ``ceec`` import inside
``computronium/autoscientist``, no ``autoscientist`` import inside the
evolution kernel. This module is the single place allowed to touch both
sides: AutoScientist proposes and sweeps (no CEEC dependency), CEEC
governs and records (never executes), and the evolution kernel searches
the Lab catalog.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ceec.models import Scope
    from ceec.store import CEECStore

    from computronium_lab.lab import Lab
    from computronium_lab.research.autopoiesis import CoordinateGenome
    from computronium_lab.synthesis.spec import ProblemSpec

__all__ = [
    "LabRecorder",
    "mirror_hypotheses",
    "mirror_proposals",
    "seed_genomes_from_proposals",
]


def _scope(run_id: str, extra: dict[str, object] | None = None) -> Scope:
    from ceec.models import Scope

    return Scope(
        domain="research",
        substrate=("digital",),
        budget="quick",
        extra={"run_id": run_id, **(extra or {})},
    )


def mirror_proposals(
    store: CEECStore,
    proposals: Sequence[object],
    *,
    run_id: str,
    budget: str = "quick",
) -> list[str]:
    """Pre-register AutoScientist proposals as ceec ``Experiment``s.

    Reads ``hypothesis``/``task``/``justification``/``expected_outcome``/
    ``priority`` structurally — the autoscientist package is never imported.
    """
    from ceec.models import Experiment, Probability
    from ceec.store import now

    ids: list[str] = []
    for index, proposal in enumerate(proposals):
        experiment_id = f"X-ASC-{run_id}-{index:03d}".replace(":", "")
        priority = float(getattr(proposal, "priority", 0.5))
        clamped = min(0.99, max(0.01, priority))
        experiment = Experiment(
            id=experiment_id,
            question=str(getattr(proposal, "hypothesis", "autoscientist proposal")),
            rationale=str(
                getattr(proposal, "justification", "") or "mirrored proposal"
            ),
            scope=_scope(run_id, {"source": "autoscientist"}),
            target_beliefs=[],
            target_goals=[],
            design={
                "model": str(getattr(proposal, "model", "")),
                "task": str(getattr(proposal, "task", "")),
                "tags": list(getattr(proposal, "tags", [])),
                "seed_plan": [0],
                "evaluation_policy": "proposal_screen_v1",
                "evidence_kind": "scalar",
            },
            prediction=str(getattr(proposal, "expected_outcome", "") or "uncommitted"),
            prediction_probability=Probability(
                low=round(max(0.0, clamped - 0.2), 3),
                high=round(min(1.0, clamped + 0.2), 3),
                point=round(clamped, 3),
                method="proposer_priority",
            ),
            controls=[],
            metrics=["accuracy"],
            budget=budget,  # type: ignore[typeddict-item]
            falsification_criterion="mirrored proposal: falsification on execution",
            overturn_criterion="mirrored proposal: overturn on execution",
            hard_gates=["BenchmarkReproduction"],
            created_at=now(),
        )
        store.pre_register_experiment(experiment)
        ids.append(experiment_id)
    return ids


def mirror_hypotheses(
    store: CEECStore,
    hypotheses: Sequence[object],
    *,
    run_id: str,
) -> list[str]:
    """Record AutoScientist hypothesis chains as ceec ``Belief`` drafts."""
    import json as _json

    from ceec.models import Probability

    ids: list[str] = []
    for index, hypothesis in enumerate(hypotheses):
        statement = str(getattr(hypothesis, "statement", ""))
        if not statement:
            continue
        artifact = store.ingest_artifact(
            _json.dumps(
                {
                    "statement": statement,
                    "confidence": float(getattr(hypothesis, "confidence", 0.5)),
                    "source": str(getattr(hypothesis, "source", "rule-based")),
                },
                sort_keys=True,
            ).encode(),
            "exploratory_synthesis",
            {"source": "autoscientist", "run_id": run_id},
        )
        evidence = store.record_evidence(
            kind="scalar",
            scope=_scope(run_id),
            artifact_refs=[artifact.id],
            quality={
                "proposer_confidence": float(getattr(hypothesis, "confidence", 0.5))
            },
            notes=f"hypothesis draft (index {index})",
        )
        belief = store.create_belief(
            statement,
            "generality",
            _scope(run_id, {"source": "autoscientist"}),
            posterior_method="proposer_priority",
            id_=f"B-ASC-{run_id}-{index:03d}".replace(":", ""),
            evidence_refs=[evidence.id],
        )
        store.update_belief(
            belief.id,
            Probability(low=0.0, high=1.0, method="proposer_priority"),
            "medium",
            "low",
            "narrow",
            "open",
            f"hypothesis draft from autoscientist chain {index}",
        )
        ids.append(belief.id)
    return ids


def seed_genomes_from_proposals(
    proposals: Sequence[object],
    spec: ProblemSpec,
    *,
    objective: str = "accuracy",
    limit: int = 4,
) -> tuple[list[CoordinateGenome], list[str]]:
    """Offer ``ProposalObjective``-ranked proposals as evolution seed genomes.

    Returns ``(genomes, skipped)``: proposals whose model/task text names a
    catalog row become seeds; everything else is reported as skipped with a
    reason — never force-mapped.
    """
    from computronium_lab.research.autopoiesis import CoordinateGenome
    from computronium_lab.synthesis.catalog import CATALOG

    def _priority(proposal: object) -> float:
        tags = list(getattr(proposal, "tags", []))
        if objective != "accuracy" and not any(
            str(t).startswith(f"objective:{objective}") for t in tags
        ):
            return -1.0
        return float(getattr(proposal, "priority", 0.5))

    ranked = sorted(proposals, key=_priority, reverse=True)
    genomes: list[CoordinateGenome] = []
    skipped: list[str] = []
    for proposal in ranked:
        text = (
            f"{getattr(proposal, 'model', '')} {getattr(proposal, 'task', '')}".lower()
        )
        match = next(
            (
                c.name
                for c in CATALOG
                if c.name.lower().replace("_", "")
                in text.replace("_", "").replace(" ", "")
            ),
            None,
        )
        if match is None:
            skipped.append(
                f"no catalog row for model={getattr(proposal, 'model', '')!r}"
            )
            continue
        genomes.append(CoordinateGenome.seed(match, spec))
        if len(genomes) >= limit:
            break
    return genomes, skipped


@dataclass
class LabRecorder:
    """Formalized Lab→CEEC writes (T24.2.8): one open/store/commit path."""

    lab: Lab

    def store(self) -> CEECStore | None:
        from pathlib import Path

        from ceec.store import CEECStore

        if not self.lab.record_ledger:
            return None
        db = Path(self.lab.record_ledger)
        return CEECStore(db, db.parent / "artifacts")
