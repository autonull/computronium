"""P4: SEC ladders on 17 error-aware credits × 2 families (34 cells).

Pre-register n_max=5 per credit/family; run ladders; first claims.

Run:
    uv run python scripts/probes/p4_sec_ladders.py --credit local_contrastive --family vision --out results/p4
"""

from __future__ import annotations

import json
import logging
from dataclasses import replace
from datetime import date
from pathlib import Path
from typing import Any

from computronium.experiment.kernel.evaluate import (
    task_shape,
)
from computronium.experiment.schema.coordinate import Schedule
from computronium.experiment.sec_census import build_census
from computronium.experiment.sec_deep_dive import (
    CLAIM_SEEDS,
    DeepDiveCandidate,
    LadderRung,
    PairedCell,
    best_rung,
    candidate_box,
    claim_verdict,
    ladder_points,
)
from computronium.experiment.sec_loop import (
    _AXIS_DEFAULTS,
    _deep_dive_coordinate,
    _is_legal,
    _measure,
    _task_bar,
    screen_coordinate,
)
from computronium.experiment.sec_pilot import BASE_BOXES, base_schedule, refusal_for
from computronium.validation.preregistration import (
    DEFAULT_ALPHA,
    ThresholdRegistration,
    paired_comparison,
)

logger = logging.getLogger(__name__)

MARGIN = 0.01

# Primary knobs for each credit (knob_name, default_value)
# Based on credit implementations and their actual effective knobs
CREDIT_PRIMARY_KNOBS = {
    "eligibility_prop": ("credit.trace_decay", 0.9),  # credit axis parameter
    "forward_tangent": ("credit.estimator_samples", 8),
    "gradient": (
        "update.step_size",
        0.01,
    ),  # gradient uses update step_size, not credit knob
    "hybrid": ("credit.feedback_scale", 0.05),  # gamma
    "local_contrastive": ("credit.readout_scale", 1.0),
    "local_goodness": ("credit.feedback_scale", 0.01),  # needs readout_error=True
    "local_supervision": ("credit.aux_head_scale", 0.1),
    "pc_alm": ("credit.beta", 0.5),  # dual learning rate (beta_dual)
    "pepita": ("credit.feedback_scale", 0.05),  # gamma
    "random_projections": ("credit.feedback_scale", 0.01),
    "rtrl_reference": ("credit.credit_norm", "none"),  # categorical, no numeric knob
    "score_function": ("credit.estimator_samples", 32),
    "surrogate": ("credit.credit_norm", "none"),  # categorical, no numeric knob
    "target_inversion": ("credit.feedback_scale", 0.01),
    "thermodynamic_contrast": ("credit.beta", 0.5),
    "unbiased_rtrl": ("credit.uoro_seed", 0),  # integer seed, not continuous
    "zeroth_order": ("credit.fd_step", 0.01),
}

# Credits with meaningful numeric primary knobs for ladder runs
LADDERABLE_CREDITS = (
    "eligibility_prop",
    "forward_tangent",
    "gradient",
    "hybrid",
    "local_contrastive",
    "local_goodness",
    "local_supervision",
    "pc_alm",
    "pepita",
    "random_projections",
    "score_function",
    "target_inversion",
    "thermodynamic_contrast",
    "zeroth_order",
)

# All error-aware credits (including those without numeric knobs)
ERROR_AWARE_CREDITS = tuple(CREDIT_PRIMARY_KNOBS.keys())

# Legal families from breadth gate (comp gate breadth)
CREDIT_FAMILIES = {
    "eligibility_prop": ["continual", "sequence"],
    "forward_tangent": ["lm", "sequence", "vision"],
    "gradient": ["continual", "graph", "sequence", "tabular", "vision"],
    "hybrid": ["lm", "sequence", "vision"],
    "local_contrastive": ["tabular", "vision"],
    "local_goodness": ["tabular", "vision"],
    "local_supervision": ["continual", "sequence", "vision"],
    "pc_alm": ["tabular", "vision"],
    "pepita": ["continual", "sequence", "tabular", "vision"],
    "random_projections": ["graph", "tabular"],
    "rtrl_reference": ["continual", "sequence"],
    "score_function": ["tabular", "vision"],
    "surrogate": ["tabular", "vision"],
    "target_inversion": ["tabular", "vision"],
    "thermodynamic_contrast": ["tabular", "vision"],
    "unbiased_rtrl": ["continual", "sequence"],
    "zeroth_order": ["continual", "lm", "sequence", "vision"],
}


def _get_primary_knob(credit: str) -> tuple[str, float] | None:
    """Get the primary knob for a credit from the manual mapping."""
    knob_info = CREDIT_PRIMARY_KNOBS.get(credit)
    if knob_info is None:
        return None
    knob_name, default_value = knob_info
    if not isinstance(default_value, (int, float)):
        # Non-numeric knob (e.g., credit_norm="none") - not suitable for ladder
        return None
    return knob_name, float(default_value)


def _get_primary_knob_axis(credit: str) -> str | None:
    """Get the axis for the primary knob (credit, plasticity, update, etc.)."""
    knob_info = CREDIT_PRIMARY_KNOBS.get(credit)
    if knob_info is None:
        return None
    knob_name, _ = knob_info
    return knob_name.split(".")[0] if "." in knob_name else "credit"


def _build_box_for_family(
    credit: str, family: str, schedule: Schedule
) -> dict[str, Any]:
    """Build a box for the given credit and family using screened box from map.json."""
    base_box = BASE_BOXES[family]
    base_coord = base_box.base_coordinate or {}

    # Start with defaults
    box: dict[str, Any] = {
        "substrate": "digital",
        "geometry": "feedforward",
        "dynamics": "instantaneous",
        "plasticity": "null",
        "credit": credit,
        "update": "euclidean",
    }
    # Override with family's base coordinate
    box.update(base_coord)

    # Get full screened box from map.json (screened on vision)
    map_path = Path("results/sec/map.json")
    if map_path.exists():
        map_data = json.loads(map_path.read_text(encoding="utf-8"))
        primitive_key = f"primitive.credit_assignment.{credit}"
        prim_data = map_data.get("primitives", {}).get(primitive_key)
        if prim_data and "box" in prim_data:
            screened_box = prim_data["box"]
            # Use the full screened box (axes + params) for compatibility
            # This ensures credits get their required dynamics, geometry, etc.
            box.update(screened_box)
            # But keep the current family's task_id and schedule
            box["task_id"] = base_box.task_id

    # Credit-specific fixes
    if credit == "local_goodness":
        # local_goodness needs readout_error=True to read the label (FF hybrid mode)
        box["credit.readout_error"] = True
    if credit == "eligibility_prop":
        # eligibility_prop's trace_decay is a credit parameter (credit.trace_decay)
        box["credit.trace_decay"] = 0.9

    # Add schedule params
    box.update({
        "fidelity": "L0",
        "seed": 0,
        "n_seeds": 1,
        "epochs": schedule.epochs,
        "batch_limit": schedule.batch_limit,
        "batch_size": schedule.batch_size,
        "task_id": base_box.task_id,
        "budget_id": f"base-{family}",
        "param_budget": base_box.param_budget,
        "device": "cpu",
        "deterministic": True,
        "num_workers": 0,
        "precision": "fp32",
        "checkpoint_every_n": 0,
        "early_stopping_patience": 0,
        "distributed_backend": "none",
        "ddp_backend": "nccl",
        "fsdp_sharding_strategy": "FULL_SHARD",
        "fsdp_min_params": 1000000,
        "fsdp_cpu_offload": False,
        "fsdp_mixed_precision": True,
    })
    return box


def run_credit_ladder(  # ruff: ignore[complex-structure] - probe script, complexity acceptable
    credit: str,
    family: str,
    out_dir: Path,
    device: str = "auto",
) -> dict[str, Any]:
    """Run SEC ladder + paired comparison for one (credit, family) pair."""
    task_id = BASE_BOXES[family].task_id
    schedule = base_schedule(task_id, device)
    if schedule is None:
        raise ValueError(f"No base schedule for {family} ({task_id})")

    box = _build_box_for_family(credit, family, schedule)
    coordinate = screen_coordinate(box, "credit", credit)
    legal, why = _is_legal(coordinate, task_id, task_shape(task_id, device))
    reason = refusal_for(
        next(
            e for e in build_census() if e.id == f"primitive.credit_assignment.{credit}"
        ),
        task_id,
    )
    if not legal or reason:
        raise ValueError(
            f"{credit} on {family} ({task_id}) is illegal: {reason or why}"
        )

    # Get primary knob
    knob_info = _get_primary_knob(credit)
    if knob_info is None:
        raise ValueError(f"{credit} has no primary knob for ladder")
    knob_name, knob_default = knob_info

    # Get the axis for the primary knob (credit, plasticity, update, etc.)
    knob_axis = _get_primary_knob_axis(credit)
    if knob_axis is None:
        knob_axis = "credit"

    # The level for screen_coordinate should be the current axis value in the box
    axis_level = box.get(knob_axis, _AXIS_DEFAULTS.get(knob_axis, credit))

    # Create candidate
    candidate = DeepDiveCandidate(
        primitive=f"primitive.credit_assignment.{credit}",
        axis=knob_axis,
        level=axis_level,
        val_acc=0.0,  # placeholder
        margin=0.0,
        knob=knob_name,
        default=knob_default,
        box=box,
        walltime_s=None,
    )

    # Run ladder
    logger.info(
        f"Running ladder for {credit} on {family} ({task_id}), knob={knob_name} default={knob_default}"
    )
    rungs = []
    for factor, value in ladder_points(candidate):
        logger.info(f"  Rung factor={factor}, value={value}")
        measured = _measure(
            _deep_dive_coordinate(candidate, factor),
            replace(schedule, seed=0, n_seeds=1),
        )
        rung = LadderRung(
            factor=factor,
            value=value,
            status=measured["status"],
            val_acc=measured["val_acc"],
            walltime_s=measured["walltime_s"],
            replay_hash=measured["replay_hash"],
            box=measured["box"],
            reason=measured["reason"],
        )
        rungs.append(rung)
        logger.info(f"    status={rung.status}, val_acc={rung.val_acc}")

    best = best_rung(tuple(rungs))
    if best is None:
        logger.warning(f"No measured rungs for {credit} on {family}")
        return {
            "credit": credit,
            "family": family,
            "verdict": "defect",
            "reason": "no measured rungs",
        }

    bar = _task_bar(task_id)
    if bar is not None and (best.val_acc or 0.0) <= bar.value:
        logger.warning(
            f"Best rung {best.factor} (val_acc={best.val_acc}) does not clear bar {bar.value}"
        )
        return {
            "credit": credit,
            "family": family,
            "verdict": "coordinate",
            "reason": "no rung clears bar",
            "ladder": [r.to_dict() for r in rungs],
        }

    # Pre-register claim
    registration = ThresholdRegistration(
        claim=f"tuning {knob_name} on {credit} moves val_acc by at least {MARGIN:.2f} at the {task_id} base",
        metric="val_acc",
        threshold=MARGIN,
        alpha=DEFAULT_ALPHA,
        min_seeds=CLAIM_SEEDS,
        created=date.today().isoformat(),
        box=candidate_box(candidate, 1.0, schedule),
    )

    reg_path = out_dir / f"prereg_{credit}_{family}.json"
    reg_path.parent.mkdir(parents=True, exist_ok=True)
    reg_path.write_text(json.dumps(registration.to_dict(), indent=2))
    logger.info(f"Registered claim: {registration.claim}")

    # Run paired comparison
    logger.info(f"Running paired comparison at best factor={best.factor}")
    cells = []
    for seed in range(CLAIM_SEEDS):
        for arm, factor in (("control", 1.0), ("treatment", best.factor)):
            measured = _measure(
                _deep_dive_coordinate(candidate, factor),
                replace(schedule, seed=seed, n_seeds=1),
            )
            cell = PairedCell(
                arm=arm,
                factor=factor,
                seed=seed,
                status=measured["status"],
                val_acc=measured["val_acc"],
                loss=measured.get("loss"),
                walltime_s=measured["walltime_s"],
                replay_hash=measured["replay_hash"],
                box=measured["box"],
                reason=measured["reason"],
            )
            cells.append(cell)

    # Check for defects
    failed = next((cell for cell in cells if cell.status == "defect"), None)
    if failed is not None:
        return {
            "credit": credit,
            "family": family,
            "verdict": "defect",
            "reason": f"{failed.arm} arm at seed {failed.seed}: {failed.reason}",
            "ladder": [r.to_dict() for r in rungs],
            "cells": [c.to_dict() for c in cells],
        }

    # Check for identical arms (happens when best rung is the default factor=1.0)
    treatments = [c for c in cells if c.arm == "treatment"]
    controls = [c for c in cells if c.arm == "control"]
    identical = all(
        t.val_acc == c.val_acc
        for t, c in zip(treatments, controls, strict=True)
        if t.val_acc is not None and c.val_acc is not None
    )
    if identical or best.factor == 1.0:
        reason = (
            "best rung is the default (factor=1.0); no improvement over baseline"
            if best.factor == 1.0
            else "arms identical at every seed"
        )
        return {
            "credit": credit,
            "family": family,
            "verdict": "coordinate",
            "reason": reason,
            "ladder": [r.to_dict() for r in rungs],
            "best_rung": best.to_dict(),
            "cells": [c.to_dict() for c in cells],
        }

    # Evaluate claim
    paired = paired_comparison(
        [float(c.val_acc or 0.0) for c in treatments],
        [float(c.val_acc or 0.0) for c in controls],
        seed=schedule.seed,
    )

    box_for_verdict = candidate_box(candidate, 1.0, schedule)
    verdict = claim_verdict(paired, registration, box_for_verdict)

    logger.info(
        f"P4 complete: {credit} on {family} best={best.factor} effect={paired.mean_diff:.4f} verdict={verdict}"
    )

    return {
        "credit": credit,
        "family": family,
        "verdict": verdict,
        "ladder": [r.to_dict() for r in rungs],
        "best_rung": best.to_dict(),
        "cells": [c.to_dict() for c in cells],
        "paired": {
            "mean_diff": paired.mean_diff,
            "ci_lower": paired.ci_lower,
            "ci_upper": paired.ci_upper,
            "p_value": paired.p_value,
            "cohens_dz": paired.cohens_dz,
            "n": paired.n,
        },
        "claim": registration.to_dict(),
        "stop_reason": (
            "rung 4: five paired seeds at the base box; the CI clears the registered margin"
            if verdict == "claim"
            else "rung 4: five paired seeds at the base box; the effect sits inside the registered margin"
        ),
    }


def main() -> None:  # ruff: ignore[complex-structure] - probe script, complexity acceptable
    import argparse

    parser = argparse.ArgumentParser(
        description="P4: SEC ladders on 17 credits × 2 families"
    )
    parser.add_argument("--credit", help="Single credit to run (default: all 17)")
    parser.add_argument(
        "--family", help="Single family to run (default: first 2 from CREDIT_FAMILIES)"
    )
    parser.add_argument(
        "--out", type=Path, default=Path("results/p4"), help="Output directory"
    )
    parser.add_argument("--device", default="auto", help="Device (auto, cpu, cuda)")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print plan without running"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )

    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    credits_to_run = [args.credit] if args.credit else list(LADDERABLE_CREDITS)
    all_results = []

    for credit in credits_to_run:
        families = CREDIT_FAMILIES.get(credit, [])
        if args.family:
            families = [args.family] if args.family in families else []
        else:
            families = families[:2]  # first 2 families

        if not families:
            logger.warning(
                f"{credit}: no families to run (legal families: {CREDIT_FAMILIES.get(credit, [])})"
            )
            continue

        for family in families:
            if args.dry_run:
                logger.info(f"DRY RUN: {credit} on {family}")
                continue

            try:
                result = run_credit_ladder(credit, family, out_dir, args.device)
                all_results.append(result)

                # Save individual result
                result_path = out_dir / f"result_{credit}_{family}.json"
                result_path.write_text(json.dumps(result, indent=2, default=str))
                logger.info(f"Saved result to {result_path}")

            except Exception as e:
                logger.exception("Failed %s on %s", credit, family)
                all_results.append({
                    "credit": credit,
                    "family": family,
                    "verdict": "error",
                    "reason": str(e),
                })

    # Save summary (append to existing)
    summary_path = out_dir / "summary.json"
    existing = []
    if summary_path.exists():
        try:
            existing = json.loads(summary_path.read_text())
        except Exception:
            existing = []
    # Remove duplicates (same credit+family)
    seen = set()
    for r in existing:
        seen.add((r["credit"], r["family"]))
    for r in all_results:
        key = (r["credit"], r["family"])
        if key not in seen:
            existing.append(r)
            seen.add(key)
    summary_path.write_text(json.dumps(existing, indent=2, default=str))
    logger.info(f"Summary saved to {summary_path}")

    # Print summary table
    print("\n=== P4 Summary ===")
    for r in all_results:
        print(
            f"  {r['credit']} on {r['family']}: {r['verdict']} ({r.get('reason', '')})"
        )


if __name__ == "__main__":
    main()
