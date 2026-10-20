#!/usr/bin/env python3
"""Generate the dashboard's axis metadata from the primitive registries.

The registries are the single source. A primitive's name, its description and
whether it is available are read from the registry the run itself reads, so
the frontend cannot end up calling a primitive something the system does not
call it — the last hand-written list here called ``photonic`` ``optical`` and
``stdp`` ``temporal_psi``.

What the registry does not carry is how an axis is *named* for a reader, so
the six labels live here, in the one place that generates them.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from computronium.experiment.schema.axis import AXES_REGISTRIES, StructuralAxis
from computronium.experiment.schema.harvest import AXIS_KIND_ORDER

# How each axis is named for a reader, and what it is for.
AXIS_LABELS: dict[StructuralAxis, tuple[str, str]] = {
    StructuralAxis.SUBSTRATE: ("Substrate", "Physical or computational substrate"),
    StructuralAxis.GEOMETRY: ("Geometry", "Network architecture and connectivity"),
    StructuralAxis.DYNAMICS: ("Dynamics", "State evolution and settling"),
    StructuralAxis.PLASTICITY: ("Plasticity", "Local learning and adaptation"),
    StructuralAxis.CREDIT: (
        "Credit Assignment",
        "How learning signals reach parameters",
    ),
    StructuralAxis.UPDATE: ("Update Rule", "How parameters are updated"),
}


def primitive_to_dict(spec: Any) -> dict[str, Any]:
    """One primitive, as the dashboard reads it."""
    return {
        "name": spec.name,
        "summary": spec.description,
        "available": spec.available,
    }


def build_metadata() -> dict[str, Any]:
    """The metadata, read from the registries."""
    axes: dict[str, Any] = {}
    for axis in AXIS_KIND_ORDER:
        display_name, description = AXIS_LABELS[axis]
        axes[axis.value] = {
            "display_name": display_name,
            "description": description,
            "primitives": [
                primitive_to_dict(spec) for spec in AXES_REGISTRIES[axis].values()
            ],
        }
    return {
        "axes": axes,
        "axis_order": [axis.value for axis in AXIS_KIND_ORDER],
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out_path = (
        root
        / "computronium"
        / "experiment"
        / "execution"
        / "dashboard"
        / "src"
        / "axis-metadata.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(build_metadata(), indent=2), encoding="utf-8")
    print(f"✓ Generated {out_path}")


if __name__ == "__main__":
    main()
