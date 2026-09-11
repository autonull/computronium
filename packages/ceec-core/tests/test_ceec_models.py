"""Unit tests for ceec-core ledger primitives."""

from __future__ import annotations

import pytest
from ceec.ids import validate_id
from ceec.store import now

from ceec import CEECStore, StoreError, models


@pytest.fixture()
def store(tmp_path: pytest.TempPathFactory | None = None):
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        root = __import__("pathlib").Path(tmp)
        with CEECStore(root / "ceec.sqlite3", root / "artifacts") as store:
            yield store


def test_id_validation_roundtrip() -> None:
    validate_id("E-000001", "E")
    with pytest.raises(ValueError, match="id"):
        validate_id("E-000001", "B")


def test_artifact_dedupe_by_sha256(store: CEECStore) -> None:
    a = store.ingest_artifact(b"same-bytes", "blob")
    b = store.ingest_artifact(b"same-bytes", "blob")
    assert a.id == b.id


def test_record_evidence_requires_artifact_or_justification(store: CEECStore) -> None:
    scope = models.Scope(domain="credit", credit=("gradient",))
    with pytest.raises(StoreError, match="no_artifact_justification"):
        store.record_evidence(kind="vector", scope=scope)


def test_belief_requires_existing_evidence(store: CEECStore) -> None:
    scope = models.Scope(domain="credit", credit=("gradient",))
    with pytest.raises(StoreError, match="evidence"):
        store.create_belief(
            statement="s", type_="mechanism", scope=scope, evidence_refs=["E-999999"]
        )


def test_experiment_lifecycle(store: CEECStore) -> None:
    scope = models.Scope(domain="credit", credit=("gradient",))
    artifact = store.ingest_artifact(b"x", "blob")
    evidence = store.record_evidence(
        kind="vector",
        scope=scope,
        artifact_refs=[artifact.id],
        axes=["m"],
        values_ref=artifact.id,
        notes="n",
    )
    belief = store.create_belief(
        statement="s", type_="mechanism", scope=scope, evidence_refs=[evidence.id]
    )
    exp = store.pre_register_experiment(
        models.Experiment(
            id="X-T-001",
            question="q",
            rationale="r",
            scope=scope,
            target_beliefs=[belief.id],
            target_goals=[],
            design={},
            prediction="p",
            controls=[],
            metrics=["m"],
            budget="quick",
            falsification_criterion="f",
            overturn_criterion="o",
            hard_gates=["g"],
            created_at=now(),
        )
    )
    assert exp.status == "pre_registered"
    store.set_experiment_status(exp.id, "completed")
    assert store.get_experiment(exp.id).status == "completed"
    assert store.experiments_by_status("completed") != []
