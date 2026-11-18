"""SEC Census: Read primitive specs and write census.json.

The census is the source of truth for what primitives exist, their metadata,
and their screening status. It replaces hardcoded primitive lists.

Run:
    uv run python -m computronium.experiment.sec_census --out results/sec
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from computronium.acceleration.spec import ImplementationSpec
from computronium.experiment.schema.primitives import ALL_PRIMITIVES

if TYPE_CHECKING:
    from collections.abc import Mapping


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
    screen_status: str | None = None  # PASS, DEFECT, UNAVAILABLE, COORDINATE, unscreened
    screen_box: dict | None = None
    screen_result: dict | None = None


def load_all_primitive_specs() -> list[ImplementationSpec]:
    """Load all primitive specs from the registry."""
    specs: list[ImplementationSpec] = []

    # Map axis names to directory names
    axis_to_dir = {
        "substrate": "substrate",
        "geometry": "geometry",
        "dynamics": "state_dynamics",
        "plasticity": "plasticity",
        "credit": "credit_assignment",
        "update": "parameter_update",
    }

    for axis, primitives in ALL_PRIMITIVES.items():
        dir_name = axis_to_dir.get(axis, axis)
        for primitive_name, config_class in primitives.items():
            # Import the spec module dynamically
            module_path = f"computronium.primitives.{dir_name}.{primitive_name}.spec"
            try:
                module = __import__(module_path, fromlist=["SPEC"])
                spec = getattr(module, "SPEC", None)
                if spec is not None:
                    specs.append(spec)
            except ImportError as e:
                # Some primitives may not have a spec.py yet
                logger.debug(f"Could not load spec for {axis}.{primitive_name}: {e}")
    return specs


def build_census() -> list[PrimitiveCensusEntry]:
    """Build the complete primitive census from specs."""
    specs = load_all_primitive_specs()
    entries: list[PrimitiveCensusEntry] = []

    for spec in specs:
        # Extract axis from spec id: primitive.<axis>.<name>
        parts = spec.id.split(".")
        axis = parts[1] if len(parts) == 3 else "unknown"

        entry = PrimitiveCensusEntry(
            id=spec.id,
            axis=axis,
            name=spec.name,
            task_families=spec.task_families,
            available=spec.available,
            capability_card=spec.capability_card,
            status=spec.status,
            reference_entrypoint=spec.reference_entrypoint,
            kernel_entrypoint=spec.kernel_entrypoint,
            supported_backends=spec.supported_backends,
            last_screened=None,
            screen_status="unscreened",
            screen_box=None,
            screen_result=None,
        )
        entries.append(entry)

    return entries


def write_census(out_dir: Path, entries: list[PrimitiveCensusEntry]) -> None:
    """Write census to JSON file."""
    out_dir.mkdir(parents=True, exist_ok=True)
    census_path = out_dir / "census.json"

    data = {
        "generated_at": datetime.now().isoformat(),
        "version": "SEC-v2",
        "total_primitives": len(entries),
        "by_axis": {},
        "primitives": [asdict(e) for e in entries],
    }

    # Group by axis
    for entry in entries:
        axis = entry.axis
        if axis not in data["by_axis"]:
            data["by_axis"][axis] = {"total": 0, "available": 0, "unscreened": 0}
        data["by_axis"][axis]["total"] += 1
        if entry.available:
            data["by_axis"][axis]["available"] += 1
        if entry.screen_status == "unscreened":
            data["by_axis"][axis]["unscreened"] += 1

    census_path.write_text(json.dumps(data, indent=2, default=str))
    print(f"Census written to {census_path} ({len(entries)} primitives)")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="SEC Census - build primitive census")
    parser.add_argument("--out", type=Path, required=True, help="Output directory")
    args = parser.parse_args()

    entries = build_census()
    write_census(args.out, entries)


if __name__ == "__main__":
    main()