"""Migration of TODO18 records into the CEEC ledger.

Existing campaign claim records become Artifact + Evidence + Derived — never
beliefs (TODO19 §17). Corrections become defect evidence and potential
quarantine/reopen triggers.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from computronium.ceec import models

if TYPE_CHECKING:
    from computronium.ceec.store import CEECStore

TODO18_CLAIM_RECORDS = [
    ("results/vertical_slice/claim_record.json", "vertical_slice"),
    ("results/mechanistic_study/claim_record.json", "mechanistic_study"),
    ("results/memory_stability/claim_record.json", "memory_stability"),
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def migrate_claim_records(store: CEECStore) -> list[str]:
    evidence_ids = []
    for relative, campaign in TODO18_CLAIM_RECORDS:
        path = _repo_root() / relative
        if not path.exists():
            continue
        evidence_ids.append(_migrate_claim_record(store, path, campaign))
    return evidence_ids


def _migrate_claim_record(store: CEECStore, path: Path, campaign: str) -> str:
    record: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    artifact = store.ingest_artifact(
        path.read_bytes(), "claim_record", {"campaign": campaign, "source": str(path)}
    )
    scope = models.Scope(
        domain=campaign,
        substrate=("digital",),
        extra={"migrated_from": str(path)},
    )
    evidence = store.record_evidence(
        kind="frontier",
        scope=scope,
        artifact_refs=[artifact.id],
        axes=["claim"],
        values_ref=artifact.uri,
        quality={
            "verification_level": record.get("verification_level", 4),
            "migrated": True,
        },
        notes=f"migrated TODO18 {campaign} claim record",
        no_artifact_justification=None,
    )
    summary = {
        k: v
        for k, v in record.items()
        if k in {"claim", "status", "verification_level", "metrics"}
    }
    store.record_derived(
        type_="claim_summary",
        operator="extract",
        inputs={"evidence": [evidence.id]},
        scope=scope,
        value=summary,
        checks=["extraction over migrated artifact"],
    )
    return evidence.id


def migrate_corrections_log(store: CEECStore) -> str | None:
    path = _repo_root() / "docs" / "CORRECTIONS.md"
    if not path.exists():
        return None
    artifact = store.ingest_artifact(
        path.read_bytes(), "corrections_log", {"source": str(path)}
    )
    evidence = store.record_evidence(
        kind="event",
        scope=models.Scope(domain="corrections", extra={"migrated_from": str(path)}),
        artifact_refs=[artifact.id],
        axes=["correction"],
        values_ref=artifact.uri,
        quality={"verification_level": 5, "migrated": True},
        notes="migrated corrections log; potential quarantine/reopen triggers",
    )
    return evidence.id


def migrate_all(store: CEECStore) -> dict[str, list[str] | str | None]:
    return {
        "claim_records": migrate_claim_records(store),
        "corrections": migrate_corrections_log(store),
    }
