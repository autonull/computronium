"""SEC census: every primitive spec joined to its runtime axis row.

The axis registries are the inventory (73 composable rows). The acceleration
spec registry adds the rows that ship as specs yet have no runtime coordinate;
their absence is a capability gap, named here, not a silently dropped row
(TODO95 P0a). ``build_census`` is the only place a primitive is enumerated;
the map, the screen and the README project it.

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

#: The reason a spec row with no runtime coordinate cannot be screened. The
#: config classmethod the axis composes through is what is missing; the code
#: path may still exist behind a factory (see ``surface.inventory``).
GAP_REASON: Final[str] = "no config classmethod — a capability gap"


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


def _axis_row(spec_id: str) -> tuple[str, str, AxisSpec | None]:
    """The ``(runtime axis, coordinate, axis row)`` a spec ID names."""
    parsed = coordinate_of_id(spec_id)
    if parsed is None:
        msg = f"primitive spec {spec_id!r} is not primitive.<axis>.<name>"
        raise ValueError(msg)
    axis, runtime = parsed
    return axis, runtime, AXES_REGISTRIES[axis].get(runtime)


def build_census() -> list[PrimitiveCensusEntry]:
    """Every primitive spec, with its axis row's availability."""
    entries: list[PrimitiveCensusEntry] = []
    for spec in sorted(primitive_specs(), key=lambda item: item.id):
        axis, runtime, row = _axis_row(spec.id)
        reason = GAP_REASON if row is None else row.unavailable_reason
        available = row is not None and row.available
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
                unavailable_reason=None if available else reason,
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
        "version": "SEC-v3",
        "total_primitives": len(entries),
        "available": len(entries) - len(gaps),
        "by_axis": by_axis,
        "gaps": [
            {"id": entry.id, "reason": entry.unavailable_reason} for entry in gaps
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
