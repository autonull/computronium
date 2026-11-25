"""Durable per-primitive SEC evidence (TODO104 A9).

An axis result is a reduce over its parts, never the only copy: a process that
dies mid-axis must not discard the axis' measurements. Parts are keyed by
primitive, so a re-run of a subset keeps the outcomes it did not re-measure.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Final, Literal

if TYPE_CHECKING:
    from pathlib import Path

__all__ = ["PART_STATUSES", "parts_dir", "reduce_parts", "write_part"]

PartStatus = Literal["measured", "error", "skipped"]
PART_STATUSES: Final[frozenset[str]] = frozenset({"measured", "error", "skipped"})


def parts_dir(root: Path) -> Path:
    """The parts directory under a results root, created on demand."""
    path = root / "parts"
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_part(
    root: Path, axis: str, primitive: str, status: PartStatus, payload: dict[str, Any]
) -> Path:
    """Persist one primitive's outcome as soon as it exists."""
    if status not in PART_STATUSES:
        raise ValueError(f"unknown part status {status!r}")
    path = parts_dir(root) / f"{axis}__{primitive}.json"
    part = {"axis": axis, "primitive": primitive, "status": status, "payload": payload}
    path.write_text(json.dumps(part, indent=2), encoding="utf-8")
    return path


def reduce_parts(root: Path, axis: str) -> dict[str, Any]:
    """Reduce an axis' parts into its result record."""
    results: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    skipped: list[str] = []
    for path in sorted(parts_dir(root).glob(f"{axis}__*.json")):
        part = json.loads(path.read_text(encoding="utf-8"))
        match part["status"]:
            case "measured":
                results.append(part["payload"])
            case "error":
                errors.append(part["payload"])
            case "skipped":
                skipped.append(part["primitive"])
    return {
        "axis": axis,
        "results": results,
        "errors": errors,
        "skipped": skipped,
        "summary": {
            "total_primitives": len(results) + len(errors) + len(skipped),
            "completed": len(results),
            "errors": len(errors),
            "skipped": len(skipped),
            "viable": sum(1 for r in results if r["rung1_verdict"] == "viable"),
            "claims": sum(1 for r in results if r["rung2_verdict"] == "claim"),
            "coordinates": sum(
                1 for r in results if r["rung2_verdict"] == "coordinate"
            ),
            "defects": sum(1 for r in results if r["rung2_verdict"] == "defect"),
        },
    }
