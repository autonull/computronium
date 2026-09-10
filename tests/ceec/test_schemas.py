"""Mechanism-schema emission tests (TODO19 Phase H.5)."""

from __future__ import annotations

import pytest

from computronium.ceec import StoreError, models
from computronium.ceec.schemas import emit_mechanism_schema


@pytest.fixture
def schema_args():
    return {
        "statement": "temporal credit beats blended accumulation under conflict",
        "failure_boundaries": ["quick budget, 2-class toy switch"],
        "verification_levels": {},
        "checks": ["frozen_theta_audit pass"],
    }


def test_schema_requires_revision(store, scope, evidence, schema_args):
    store.create_belief(
        "unrevised hypothesis", "mechanism", scope, id_="B-NS", evidence_refs=[]
    )
    with pytest.raises(StoreError, match="no revision"):
        emit_mechanism_schema(store, "B-NS", **schema_args)


def test_schema_links_evidence_and_belief(store, scope, evidence, schema_args):
    store.create_belief(
        "hypothesis", "mechanism", scope, id_="B-S1", evidence_refs=[evidence.id]
    )
    store.update_belief(
        "B-S1",
        models.Probability(low=0.35, high=0.55),
        "medium",
        "medium",
        "narrow",
        "open",
        "bootstrap",
    )
    derived = emit_mechanism_schema(store, "B-S1", **schema_args)
    assert derived.type == "mechanism_schema"
    assert derived.inputs == {"evidence": [evidence.id]}
    assert derived.value["probability"]["low"] == 0.35
    row = store._conn.execute(
        "SELECT 1 FROM belief_derived WHERE belief_id = 'B-S1' AND derived_id = ?",
        (derived.id,),
    ).fetchone()
    assert row is not None
