"""Domain-enablement proof (TODO26 T26.H.1): a sentiment-eval profile runs
the full loop — experiment → decide → run → boundary → calibration →
close_round — with zero core changes, onboarding in ~60 lines.
"""

from __future__ import annotations

import pytest
from ceec.models import Probability, Scope
from ceec.profile import CORE_CONSTRAINTS, CORE_QUALITY, Profile, Thresholds
from ceec.run import ProbeResult
from ceec.session import ledger

SENTIMENT = Profile(
    name="sentiment-eval",
    policy_version="1.0",
    scope_dimensions={"model": str, "benchmark": str, "prompt_version": str},
    budget_tiers=("cheap", "standard", "sweep"),
    default_cost={"cheap": 1.0, "standard": 4.0, "sweep": 16.0},
    constraints=CORE_CONSTRAINTS,
    quality=CORE_QUALITY,
    thresholds=Thresholds(),
)


def _probe(experiment):
    return ProbeResult(
        label="passed",
        outcome_boolean=True,
        payload={"accuracy": 0.62},
        axes=("seed",),
        values=(0.61, 0.62, 0.63),
        values_ref="accuracy",
        quality={
            "seeds": 3,
            "matched_control": True,
            "evaluation_policy": "held_out_f1",
            "defect_audit": "pass",
            "integrity_checks": "pass",
            "reproduction": True,
        },
    )


@pytest.fixture
def sess(tmp_path):
    with ledger(tmp_path / "sentiment.sqlite3", SENTIMENT) as session:
        yield session


def test_sentiment_domain_full_loop(sess):
    scope = Scope.of(
        domain="sentiment-eval",
        model="toy-bow",
        benchmark="sst2-mini",
        prompt_version="v1",
    )
    artifact = sess.artifact(b"prior", "prior")
    ev = sess.store.record_evidence(
        "vector",
        scope,
        artifact_refs=[artifact.id],
        axes=["seed"],
        values_ref="accuracy",
        quality={
            "seeds": 3,
            "matched_control": True,
            "evaluation_policy": "held_out_f1",
            "defect_audit": "pass",
            "integrity_checks": "pass",
            "reproduction": True,
        },
    )
    sess.store.create_belief(
        "model beats majority", "mechanism", scope, id_="B-SENT", evidence_refs=[ev.id]
    )
    sess.store.update_belief(
        "B-SENT",
        Probability(low=0.96, high=0.99, point=0.97),
        "low",
        "high",
        "broad",
        "open",
        "prior round",
    )
    draft = sess.experiment(
        question="does the model beat majority on sst2-mini?",
        prediction="accuracy > majority",
        scope=scope,
        targets=["B-SENT"],
        design={
            "seed_plan": [0, 1, 2],
            "evaluation_policy": "held_out_f1",
            "evidence_kind": "vector",
        },
        tier="sweep",
    )
    assert draft.budget == "sweep"
    run = sess.run(draft, _probe, evaluate="promotion")
    assert run.status == "completed"
    assert run.evaluation is not None and run.evaluation.all_passed
    assert sess.store.current_status("B-SENT") == "promoted"
    report = sess.close_round()
    assert report.clean
