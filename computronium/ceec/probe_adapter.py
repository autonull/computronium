"""Adapter converting probe outputs into CEEC artifacts, evidence, and derived.

Probe output contract (E.1):

    {
        "status": "ok" | "inert" | "missing",   # inert=invalid coordinate,
                                                # missing=infrastructure failure
        "kind": <evidence kind>,                # structured kinds preserved
        "scope": {...},                         # Scope fields
        "axes": [...],                          # required for structured kinds
        "values": <json-serializable data>,     # structured payload
        "quality": {...},                       # seeds, matched_control, ...
        "defects": [...],
        "notes": str,
        "summary": {...},                       # optional scalar summary -> derived
        "summary_operator": str,                # default "scalar_summary"
    }
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from computronium.ceec import models
from computronium.ceec.store import CEECStore, StoreError

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True, slots=True)
class ProbeEvidence:
    artifact: models.Artifact
    evidence: models.Evidence
    derived: models.Derived | None


def probe_scope(probe_output: dict[str, Any]) -> models.Scope:
    scope = probe_output.get("scope", {})
    return models.Scope(
        domain=scope.get("domain", "probe"),
        substrate=tuple(scope.get("substrate", ())),
        geometry=tuple(scope.get("geometry", ())),
        credit=tuple(scope.get("credit", ())),
        budget=scope.get("budget"),
        code_commit=scope.get("code_commit"),
        extra={
            k: v
            for k, v in scope.items()
            if k
            not in {
                "domain",
                "substrate",
                "geometry",
                "credit",
                "budget",
                "code_commit",
            }
        },
    )


def _evidence_kind(probe_output: dict[str, Any]) -> str:
    status = probe_output.get("status", "ok")
    if status == "inert":
        return "inert"
    if status == "missing":
        return "missing"
    kind = probe_output.get("kind", "scalar")
    if kind not in models.STRUCTURED_KINDS and kind not in {"scalar", "interval"}:
        raise StoreError(f"unknown probe evidence kind {kind!r}")
    return kind


def record_probe_result(
    store: CEECStore,
    probe_output: dict[str, Any],
    probe_name: str,
    id_: str | None = None,
) -> ProbeEvidence:
    kind = _evidence_kind(probe_output)
    scope = probe_scope(probe_output)
    payload = json.dumps(
        {"probe": probe_name, "values": probe_output.get("values")},
        sort_keys=True,
    ).encode()
    artifact = store.ingest_artifact(
        payload,
        "probe_result",
        {"probe": probe_name, "status": probe_output.get("status")},
    )
    status = probe_output.get("status", "ok")
    notes = probe_output.get("notes")
    if status in {"inert", "missing"} and not notes:
        notes = f"probe {probe_name} returned {status}"
    evidence = store.record_evidence(
        kind=kind,
        scope=scope,
        artifact_refs=[artifact.id],
        axes=probe_output.get("axes") if kind in models.STRUCTURED_KINDS else None,
        values_ref=artifact.uri,
        quality=dict(probe_output.get("quality", {})),
        defects=list(probe_output.get("defects", [])),
        notes=notes,
        id_=id_,
    )
    derived = None
    if probe_output.get("summary") is not None:
        derived = store.record_derived(
            type_="scalar_summary",
            operator=probe_output.get("summary_operator", "aggregate"),
            inputs={"evidence": [evidence.id]},
            scope=scope,
            value=probe_output["summary"],
            checks=["derived from structured primary evidence"],
        )
    return ProbeEvidence(artifact, evidence, derived)


def load_probe_output(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
