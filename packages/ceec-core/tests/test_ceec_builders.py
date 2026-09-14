"""TODO25 C.1: ceec.builders — experiment/gate-evidence construction and
the chance-verdict statistics, validated against the gate readers."""

from __future__ import annotations

import math

import pytest
from ceec.gates import declare_boundary
from ceec.store import CEECStore

from ceec import builders, models


@pytest.fixture()
def store(tmp_path):
    s = CEECStore(tmp_path / "ledger.sqlite3", tmp_path / "artifacts")
    yield s
    s.close()


SCOPE = models.Scope.of(domain="test", substrate=("digital",), budget="quick")


def _experiment(store: CEECStore, **overrides: object) -> models.Experiment:
    kwargs: dict[str, object] = {
        "id_": "X-BUILDER-001",
        "question": "does the mechanism learn?",
        "prediction": "accuracy clears chance",
        "scope": SCOPE,
        "tier": "nightly",
        "prediction_probability": (0.4, 0.8, 0.6),
    }
    kwargs.update(overrides)
    return builders.experiment(**kwargs)  # type: ignore[arg-type]


def test_experiment_defaults_satisfy_hard_constraints(store: CEECStore) -> None:
    from ceec.selection import check_hard_constraints

    draft = _experiment(store)
    assert draft.budget == "nightly"
    assert draft.status == "draft"
    registered = store.pre_register_experiment(draft)
    failed = [c for c in check_hard_constraints(store, registered) if not c.passed]
    assert failed == []


def test_experiment_budget_pass_through() -> None:
    assert (
        builders.experiment(
            id_="X-B-2", question="q", prediction="p", scope=SCOPE, tier="nightly"
        ).budget
        == "nightly"
    )
    # domain vocabulary passes through; the profile validates at the
    # store boundary (Phase E)
    assert (
        builders.experiment(
            id_="X-B-3", question="q", prediction="p", scope=SCOPE, tier="sweep"
        ).budget
        == "sweep"
    )


def test_gate_evidence_flags_validate_against_gate_readers(store: CEECStore) -> None:
    artifact = store.ingest_artifact(b"payload", "test_payload", {})
    evidence = builders.gate_evidence(
        store,
        SCOPE,
        axes=["seed"],
        values=[0.49, 0.51, 0.50],
        values_ref="test/accs",
        artifact_refs=[artifact.id],
        seeds=3,
        matched_control=True,
        evaluation_policy="certified_operating_point",
        known_levers_exhausted=True,
        notes="boundary-quality evidence",
    )
    assert evidence.kind == "vector"
    assert evidence.quality["known_levers_exhausted"] is True

    belief = store.create_belief(
        "mechanism is at chance", "mechanism", SCOPE, evidence_refs=[evidence.id]
    )
    store.update_belief(
        belief.id,
        models.Probability(low=0.0, high=0.05, method="certified_chance_boundary"),
        "low",
        "high",
        "narrow",
        "open",
        "rescue probability at the boundary threshold",
    )
    evaluation = declare_boundary(store, belief.id, "test boundary")
    assert evaluation.all_passed, [r.rationale for r in evaluation.results]


def test_gate_evidence_rejects_bad_flags_and_missing_payload(store: CEECStore) -> None:
    artifact = store.ingest_artifact(b"payload", "evidence_payload")
    with pytest.raises(ValueError, match="defect_audit"):
        builders.gate_evidence(
            store,
            SCOPE,
            artifact_refs=[artifact.id],
            axes=("probe",),
            values_ref=f"artifact:{artifact.id}",
            defect_audit="ok",
        )
    with pytest.raises(ValueError, match="axes and values_ref"):
        builders.gate_evidence(store, SCOPE, seeds=1, values=[1.0])
    with pytest.raises(ValueError, match="artifact_refs, axes, and values_ref"):
        builders.gate_evidence(store, SCOPE, seeds=1)


def test_chance_verdict_reproduces_parity_boundary_b1() -> None:
    verdict = builders.chance_verdict([0.469, 0.539, 0.531], n_eval=32)
    assert verdict.mean == pytest.approx(0.513)
    assert verdict.per_seed_band == pytest.approx(2 * math.sqrt(0.25 / 32), rel=1e-12)
    assert all(verdict.per_seed_in_band)
    assert verdict.at_chance


def test_chance_verdict_rejects_signal() -> None:
    verdict = builders.chance_verdict([0.9, 0.88, 0.91], n_eval=32)
    assert not verdict.at_chance
    assert not any(verdict.per_seed_in_band)
    with pytest.raises(ValueError, match="at least one accuracy"):
        builders.chance_verdict([], n_eval=32)
