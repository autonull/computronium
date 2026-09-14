"""CEEC instrument improvements (TODO24 T24.0.6): structured-evidence
emission helpers and the unified ledger audit.

The lab's historical campaign records are scalar-only evidence — the CEEC
§27 anti-pattern TODO24 retires. These helpers emit ``vector``/``curve``/
``frontier`` kinds with the ``axes`` + ``values_ref`` pair ``ceec.models``
enforces, and ``run_ledger_audit`` delegates to ``ceec.audit`` while keeping
the lab's campaign-only allowlist and ``X-*`` probe-code rejection.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import TYPE_CHECKING

from ceec.audit import Finding, run_audit

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from ceec.models import Evidence, Scope
    from ceec.store import CEECStore

__all__ = [
    "STRUCTURED_KIND_HELPERS",
    "curve_evidence",
    "frontier_evidence",
    "run_ledger_audit",
    "vector_evidence",
]

_X_CODE = re.compile(r"X-[A-Z]+-\d+")


def _payload(
    store: CEECStore,
    scope: Scope,
    kind: str,
    axes: list[str],
    data: Sequence[Mapping[str, object]],
    values_ref: str,
    provenance: Mapping[str, object],
) -> str:
    artifact = store.ingest_artifact(
        json.dumps(list(data), sort_keys=True, default=str).encode(),
        "evidence_payload",
        dict(provenance) or {"axes": axes, "values_ref": values_ref},
    )
    return artifact.id


def vector_evidence(
    store: CEECStore,
    scope: Scope,
    *,
    axes: list[str],
    values: Sequence[float],
    values_ref: str,
    quality: Mapping[str, object] | None = None,
    notes: str | None = None,
    provenance: Mapping[str, object] | None = None,
) -> str:
    """Record per-seed (or per-point) ``vector`` evidence."""
    rows = [dict(zip(axes, row, strict=False)) for row in _rows(axes, values)]
    artifact_id = _payload(
        store, scope, "vector", axes, rows, values_ref, provenance or {}
    )
    evidence = store.record_evidence(
        kind="vector",
        scope=scope,
        artifact_refs=[artifact_id],
        quality=dict(quality or {}),
        axes=axes,
        values_ref=values_ref,
        notes=notes,
    )
    return evidence.id


def curve_evidence(
    store: CEECStore,
    scope: Scope,
    *,
    history: Sequence[Mapping[str, float]],
    x_axis: str = "epoch",
    y_axis: str = "accuracy",
    values_ref: str,
    quality: Mapping[str, object] | None = None,
    notes: str | None = None,
    provenance: Mapping[str, object] | None = None,
) -> str:
    """Record a training/adaptation history as ``curve`` evidence."""
    axes = [x_axis, y_axis]
    rows = [
        {x_axis: row.get(x_axis, i), y_axis: row.get(y_axis, 0.0)}
        for i, row in enumerate(history)
    ]
    artifact_id = _payload(
        store, scope, "curve", axes, rows, values_ref, provenance or {}
    )
    evidence = store.record_evidence(
        kind="curve",
        scope=scope,
        artifact_refs=[artifact_id],
        quality=dict(quality or {}),
        axes=axes,
        values_ref=values_ref,
        notes=notes,
    )
    return evidence.id


def frontier_evidence(
    store: CEECStore,
    scope: Scope,
    *,
    points: Sequence[Mapping[str, float]],
    axes: Sequence[str],
    values_ref: str,
    quality: Mapping[str, object] | None = None,
    notes: str | None = None,
    provenance: Mapping[str, object] | None = None,
) -> str:
    """Record a Pareto frontier as ``frontier`` evidence (axes + points)."""
    axis_list = list(axes)
    rows = [{a: point.get(a, 0.0) for a in axis_list} for point in points]
    artifact_id = _payload(
        store, scope, "frontier", axis_list, rows, values_ref, provenance or {}
    )
    evidence = store.record_evidence(
        kind="frontier",
        scope=scope,
        artifact_refs=[artifact_id],
        quality=dict(quality or {}),
        axes=axis_list,
        values_ref=values_ref,
        notes=notes,
    )
    return evidence.id


def _rows(axes: list[str], values: Sequence[float]) -> Sequence[Sequence[float]]:
    if not axes:
        raise ValueError("vector evidence requires at least one axis")
    if len(values) % len(axes) != 0:
        raise ValueError(
            f"values length {len(values)} is not a multiple of {len(axes)} axes"
        )
    stride = len(axes)
    return [values[i : i + stride] for i in range(0, len(values), stride)]


STRUCTURED_KIND_HELPERS: Mapping[str, object] = {
    "vector": vector_evidence,
    "curve": curve_evidence,
    "frontier": frontier_evidence,
}


def record_block(
    store: CEECStore,
    scope: Scope,
    *,
    artifact_refs: list[str],
    notes: str,
) -> Evidence:
    """Record ``missing`` evidence for a measurement block (notes mandatory)."""
    if not notes:
        raise ValueError("measurement-block evidence requires explanatory notes")
    return store.record_evidence(
        kind="missing",
        scope=scope,
        artifact_refs=artifact_refs,
        notes=notes,
    )


def run_ledger_audit(
    db_path: str | Path,
    *,
    artifacts_dir: str | Path | None = None,
) -> dict[str, object]:
    """Unified audit: ceec structural findings + lab campaign-only allowlist.

    Returns the historical lab audit shape plus a ``findings`` list of
    ceec ``Finding`` check names and severities.
    """
    db = Path(db_path)
    art = Path(artifacts_dir) if artifacts_dir else db.parent / "artifacts"
    findings: list[Finding] = []
    store: CEECStore | None = None
    if db.exists():
        from ceec.store import CEECStore

        store = CEECStore(db, art)
        try:
            findings = run_audit(store)
        finally:
            store.close()

    types: list[str] = []
    x_codes: set[str] = set()
    if db.exists():
        import sqlite3

        conn = sqlite3.connect(db)
        try:
            rows = conn.execute("SELECT type, provenance FROM artifacts").fetchall()
            types = sorted({str(t) for t, _ in rows})
            notes_rows = conn.execute("SELECT notes FROM evidence").fetchall()
        finally:
            conn.close()
        for _, provenance in rows:
            x_codes.update(_X_CODE.findall(str(provenance)))
        for (notes,) in notes_rows:
            x_codes.update(_X_CODE.findall(str(notes)))

    from computronium_lab.campaign import _ALLOWED_ARTIFACT_TYPES

    campaign_only = all(t in _ALLOWED_ARTIFACT_TYPES for t in types)
    violations = [f.check for f in findings if f.severity == "violation"]
    return {
        "artifact_types": types,
        "campaign_only": campaign_only,
        "x_codes": sorted(x_codes),
        "findings": [
            {"check": f.check, "severity": f.severity, "detail": f.detail}
            for f in findings
        ],
        "violations": violations,
        "clean": campaign_only and not x_codes and not violations,
    }
