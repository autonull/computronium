"""SEC census: every primitive spec joined to its runtime axis row.

The axis registries are the inventory (one composable row per primitive). The
acceleration spec registry is the implementation list; the join between them is
checked here. A spec without an axis row is a gap — and a gap has exactly one
home, ``schema.gaps.GAPS`` (TODO95 D1/D9). ``build_census`` is the only place a
primitive is enumerated; the map, the screen and the README project it.

Run:
    uv run python -m computronium.experiment.sec_census --out results/sec
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Final

from computronium.acceleration.registry import primitives as primitive_specs
from computronium.acceleration.spec import coordinate_of_id
from computronium.experiment.schema.axis import AXES_REGISTRIES, AxisSpec
from computronium.experiment.schema.gaps import gap_for

#: The one version stamp of the SEC record. The census, the map and every
#: reader compare this value; a second literal is how two artifacts drift.
MAP_VERSION: Final[str] = "SEC-v3"


@dataclass(frozen=True, slots=True)
class PrimitiveCensusEntry:
    """One row in the primitive census."""

    id: str
    axis: str
    name: str
    task_families: tuple[str, ...]
    available: bool
    capability_card: str
    status: str
    reference_entrypoint: str
    kernel_entrypoint: str | None
    supported_backends: tuple[str, ...]
    last_screened: str | None = None
    screen_status: str | None = None  # MEASURED, DEFECT, refused, unscreened
    screen_box: dict | None = None
    screen_result: dict | None = None
    unavailable_reason: str | None = None
    unavailable_trigger: str | None = None


def _axis_row(spec_id: str) -> tuple[str, str, AxisSpec | None]:
    """The ``(runtime axis, coordinate, axis row)`` a spec ID names."""
    parsed = coordinate_of_id(spec_id)
    if parsed is None:
        msg = f"primitive spec {spec_id!r} is not primitive.<axis>.<name>"
        raise ValueError(msg)
    axis, runtime = parsed
    return axis, runtime, AXES_REGISTRIES[axis].get(runtime)


def build_census() -> list[PrimitiveCensusEntry]:
    """Every primitive spec, with its axis row's availability and its gap."""
    entries: list[PrimitiveCensusEntry] = []
    for spec in sorted(primitive_specs(), key=lambda item: item.id):
        axis, runtime, row = _axis_row(spec.id)
        gap = gap_for(spec.id)
        row_available = row is not None and row.available
        if gap is None and not row_available:
            msg = (
                f"primitive {spec.id!r} has no axis row or an unavailable one, "
                "and no schema.gaps.GAPS entry"
            )
            raise ValueError(msg)
        if gap is not None and row_available:
            msg = (
                f"schema.gaps.GAPS declares {spec.id!r} a gap, but its row is available"
            )
            raise ValueError(msg)
        available = gap is None
        entries.append(
            PrimitiveCensusEntry(
                id=spec.id,
                axis=axis,
                name=runtime,
                task_families=spec.task_families,
                available=available,
                capability_card=spec.capability_card,
                status=spec.status,
                reference_entrypoint=spec.reference_entrypoint,
                kernel_entrypoint=spec.kernel_entrypoint,
                supported_backends=spec.supported_backends,
                screen_status="unscreened" if available else "refused",
                unavailable_reason=None if gap is None else gap.reason,
                unavailable_trigger=None if gap is None else gap.trigger,
            )
        )
    return entries


def write_census(out_dir: Path, entries: list[PrimitiveCensusEntry]) -> None:
    """Write census.json and print the inventory total and its gaps."""
    out_dir.mkdir(parents=True, exist_ok=True)
    census_path = out_dir / "census.json"
    gaps = [entry for entry in entries if entry.unavailable_reason]

    by_axis: dict[str, dict[str, int]] = {}
    for entry in entries:
        row = by_axis.setdefault(
            entry.axis, {"total": 0, "available": 0, "unscreened": 0}
        )
        row["total"] += 1
        row["available"] += int(entry.available)
        row["unscreened"] += int(entry.screen_status == "unscreened")

    data = {
        "generated_at": datetime.now().isoformat(),
        "version": MAP_VERSION,
        "total_primitives": len(entries),
        "available": len(entries) - len(gaps),
        "by_axis": by_axis,
        "gaps": [
            {
                "id": entry.id,
                "reason": entry.unavailable_reason,
                "trigger": entry.unavailable_trigger,
            }
            for entry in gaps
        ],
        "primitives": [asdict(entry) for entry in entries],
    }
    census_path.write_text(json.dumps(data, indent=2, default=str))
    print(
        f"Census: {len(entries)} primitives "
        f"({data['available']} available, {len(gaps)} gaps) -> {census_path}"
    )
    for entry in gaps:
        print(f"  gap: {entry.id} — {entry.unavailable_reason}")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="SEC Census - build primitive census")
    parser.add_argument("--out", type=Path, required=True, help="Output directory")
    args = parser.parse_args()

    write_census(args.out, build_census())


if __name__ == "__main__":
    main()
