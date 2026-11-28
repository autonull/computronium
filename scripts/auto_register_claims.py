#!/usr/bin/env python
"""Auto-register claims from Rung 3 results.

Reads best ladder points from rung3 summary files and writes
pre-registration JSON files to configs/preregistrations/.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from computronium.experiment.sec_loop import _box_summary, _coordinate, base_schedule
from computronium.experiment.sec_pilot import BASE_BOXES, base_family
from computronium.validation.preregistration import (
    EffectSizeRegistration,
)


def create_registration_from_rung3(
    rung3_result: dict,
    task_id: str,
    device: str = "cuda",
) -> EffectSizeRegistration | None:
    """Create an EffectSizeRegistration from a successful Rung 3 claim."""

    if "deep_dive" not in rung3_result:
        return None

    deep_dive = rung3_result["deep_dive"]
    verdict = deep_dive.get("verdict")
    if verdict != "claim":
        return None

    candidate = deep_dive["candidate"]
    primitive = candidate["primitive"]
    axis = candidate["axis"]
    level = candidate["level"]
    knob = candidate["knob"]
    default = candidate["default"]

    # Compute best_rung from ladder if not present
    ladder = deep_dive.get("ladder", [])
    if not ladder:
        return None

    # Find best measured rung
    measured_rungs = [
        r
        for r in ladder
        if r.get("status") == "measured" and r.get("val_acc") is not None
    ]
    if not measured_rungs:
        return None

    best_rung = max(measured_rungs, key=lambda r: r["val_acc"])
    best_factor = best_rung["factor"]
    best_val_acc = best_rung["val_acc"]

    # Get the family and base box
    family = base_family(task_id)
    if family is None:
        return None

    base = BASE_BOXES.get(family)
    if base is None:
        return None

    # Build the base coordinate using family's base
    base_axes = base.base_coordinate.copy() if base.base_coordinate else {}
    default_axes = {
        "substrate": "digital",
        "geometry": "feedforward",
        "dynamics": "instantaneous",
        "plasticity": "null",
        "credit": "gradient",
        "update": "euclidean",
    }
    for k, v in default_axes.items():
        if k not in base_axes:
            base_axes[k] = v
    base_axes[axis] = level

    schedule = base_schedule(task_id, device)
    if schedule is None:
        return None

    base_coord = _coordinate(base_axes)
    base_box = _box_summary(base_coord, schedule)

    # Determine minimum effect size for this task family
    from computronium.validation.preregistration import (
        MIN_EFFECT_SIZE_BY_FAMILY,
        _family_from_task,
    )

    family_key = _family_from_task(task_id)
    min_d = MIN_EFFECT_SIZE_BY_FAMILY.get(family_key, 0.5)

    # Create claim statement
    claim = f"{primitive} improves {task_id} with knob {knob} (factor={best_factor})"

    registration = EffectSizeRegistration(
        claim=claim,
        metric="val_acc",
        min_d=min_d,
        alpha=0.05,
        min_seeds=5,
        created=date.today().isoformat(),
        box=base_box,
    )

    return registration


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Auto-register claims from Rung 3 results"
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        required=True,
        help="Directory with rung3 result files",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("configs/preregistrations"),
        help="Output directory for registrations",
    )
    parser.add_argument("--device", default="cuda", help="Device used for runs")
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)

    # Find all individual rung3 result files (not summary)
    result_files = list(args.results_dir.glob("primitive_*_rung3.json"))
    print(f"Found {len(result_files)} result files")

    total_claims = 0
    for result_file in result_files:
        print(f"\nProcessing {result_file.name}...")
        with Path(result_file).open(encoding="utf-8") as f:
            result = json.load(f)

        # Extract task_id from filename
        # Format: primitive_<primitive>_<task>_rung3.json
        parts = result_file.stem.split("_")
        if len(parts) >= 4:
            task_id = parts[-2]
        else:
            print("  ⚠️  Could not parse task from filename")
            continue

        registration = create_registration_from_rung3(result, task_id, args.device)
        if registration:
            # Generate filename
            primitive = result["deep_dive"]["candidate"]["primitive"]
            safe_name = primitive.replace(".", "_")
            out_file = args.out_dir / f"sec_{safe_name}_{task_id}.json"

            out_file.write_text(json.dumps(registration.to_dict(), indent=2))
            print(
                f"  ✅ Registered claim: {out_file.name} (min_d={registration.min_d})"
            )
            total_claims += 1
        else:
            verdict = result.get("deep_dive", {}).get("verdict", "no_claim")
            print(f"  ⏭️  Skipped: {verdict}")

    print(f"\nTotal claims registered: {total_claims}")


if __name__ == "__main__":
    main()
