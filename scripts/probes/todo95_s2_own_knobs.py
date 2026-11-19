"""TODO95 S2 own-knobs pass: the update axis at its declared defaults.

Measured 2026-11-18: 18 update primitives, the viability box (each update
rule at its own config-classmethod defaults, companions at the base box). The
base box stamps every update row `inert` (a shared step size); this pass is the
other instrument whose rows can carry a number. Writes
``results/sec/own_knobs/`` -- a separate box, never merged into the base map.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from computronium.experiment.sec_census import build_census
from computronium.experiment.sec_loop import run_p0_track


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="TODO95 S2 own-knobs pass")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--out", type=Path, default=Path("results/sec/own_knobs"))
    args = parser.parse_args()

    entries = [entry for entry in build_census() if entry.axis == "update"]
    started = time.monotonic()
    result = run_p0_track(
        args.out,
        entries,
        max_primitives=len(entries),
        device=args.device,
        own_knobs=True,
    )
    walltime = time.monotonic() - started
    rows = [
        {
            "primitive": cell["primitive"],
            "status": cell["status"],
            "binding": cell.get("binding"),
            "val_acc": cell.get("val_acc"),
            "resource": cell.get("resource"),
        }
        for cell in result["cells"]
    ]
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "summary.json").write_text(
        json.dumps(
            {
                "own_knobs": True,
                "axis": "update",
                "walltime_s": walltime,
                "control_val_acc": result["control_val_acc"],
                "control_spread": result["control_spread"],
                "bar": result["bar"],
                "rows": rows,
            },
            indent=2,
            default=str,
        )
    )
    for row in rows:
        print(
            f"{row['primitive']}: {row['status']} {row['binding']} "
            f"val_acc={row['val_acc']}"
        )
    print(f"-> {args.out} ({walltime:.1f}s)")


if __name__ == "__main__":
    main()
