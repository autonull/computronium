"""Mechanism-schema emission (TODO19 Phase H.5 / open-work item 2).

A mechanism schema is a ``derived`` object of type ``mechanism_schema``
consolidating the gated evidence behind a belief: supporting scopes,
evidence refs, failure boundaries, and verification levels. Emission is
idempotent per (belief, evidence set) — re-running with the same inputs
re-derives the same schema row (new derived ID, no mutation).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ceec.store import StoreError

if TYPE_CHECKING:
    from ceec.models import Derived
    from ceec.store import CEECStore


def belief_evidence_ids(store: CEECStore, belief_id: str) -> list[str]:
    """Evidence currently linked to a belief (ledger order)."""
    rows = store._conn.execute(
        "SELECT evidence_id FROM belief_evidence WHERE belief_id = ? ORDER BY rowid",
        (belief_id,),
    ).fetchall()
    return [row["evidence_id"] for row in rows]


def emit_mechanism_schema(
    store: CEECStore,
    belief_id: str,
    *,
    statement: str,
    supporting_evidence: list[str] | None = None,
    failure_boundaries: list[str],
    verification_levels: dict[str, int],
    checks: list[str] | None = None,
) -> Derived:
    """Consolidate a belief's evidence into a ``mechanism_schema`` derived.

    Requires the belief to have at least one open revision and every
    supporting evidence ref to exist in the ledger.
    """
    revision = store.latest_revision(belief_id)
    if revision is None:
        raise StoreError(f"belief {belief_id!r} has no revision to schema")
    evidence = (
        supporting_evidence
        if supporting_evidence is not None
        else belief_evidence_ids(store, belief_id)
    )
    inputs: dict[str, list[str]] = {"evidence": evidence}
    value: dict[str, Any] = {
        "statement": statement,
        "probability": revision.probability.model_dump(),
        "supporting_evidence": evidence,
        "failure_boundaries": failure_boundaries,
        "verification_levels": verification_levels,
    }
    derived = store.record_derived(
        "mechanism_schema",
        operator="consolidate_gated_evidence",
        inputs=inputs,
        scope=store.get_belief(belief_id).scope,
        value=value,
        assumptions=[
            "schema reflects only evidence present in the ledger at emission",
        ],
        checks=checks or [],
        provenance={"belief": belief_id, "belief_revision": revision.id},
    )
    store._link(
        store._conn,
        "belief_derived",
        "belief_id",
        belief_id,
        "derived_id",
        [derived.id],
    )
    store._conn.commit()
    return derived
