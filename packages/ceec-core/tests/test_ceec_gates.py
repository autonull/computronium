"""Gate semantics: promotion/boundary/quarantine via effective_status."""

from __future__ import annotations

import pytest
from ceec.gates import effective_status

from ceec import CEECStore, StoreError, models


@pytest.fixture()
def store():
    import tempfile
    from pathlib import Path

    with (
        tempfile.TemporaryDirectory() as tmp,
        CEECStore(Path(tmp) / "ceec.sqlite3", Path(tmp) / "artifacts") as s,
    ):
        yield s


def _belief_with_evidence(store: CEECStore):
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
    return store.create_belief(
        statement="s", type_="mechanism", scope=scope, evidence_refs=[evidence.id]
    )


def test_effective_status_of_open_belief(store: CEECStore) -> None:
    belief = _belief_with_evidence(store)
    status = effective_status(store, belief.id)
    assert status.primary == "open"
    assert status.quarantined_by == ()


def test_promotion_requires_gate_outcome(store: CEECStore) -> None:
    belief = _belief_with_evidence(store)
    with pytest.raises(StoreError, match="gate outcome"):
        store.change_status(belief.id, to_status="promoted", reason="because")


def test_promotion_flow(store: CEECStore) -> None:
    belief = _belief_with_evidence(store)
    outcome = store.record_gate_outcome(
        gate="promotion",
        status="pass",
        rationale="multi-seed replication",
        belief_id=belief.id,
    )
    store.change_status(
        belief.id,
        to_status="promoted",
        reason="promotion gate passed",
        gate_refs=[outcome.id],
    )
    assert effective_status(store, belief.id).primary == "promoted"


def test_boundary_then_reopen_requires_trigger(store: CEECStore) -> None:
    belief = _belief_with_evidence(store)
    outcome = store.record_gate_outcome(
        gate="boundary",
        status="pass",
        rationale="scope limit found",
        belief_id=belief.id,
    )
    store.change_status(
        belief.id,
        to_status="boundary",
        reason="scoped out",
        gate_refs=[outcome.id],
    )
    with pytest.raises(StoreError, match="trigger"):
        store.change_status(belief.id, to_status="open", reason="retry")
