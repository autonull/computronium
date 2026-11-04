"""Smart-survey promotion logic.

Handles multi-fidelity promotion (L0→L1→L2) with:
- Ruler-relative normalization for cross-task comparison
- Promotion threshold filtering
- Budget allocation fractions (40/40/20)
- Seed/epoch progression (1→2→5, 1→3→10)
- Original task preservation (avoids task cycling rejections)

Budget allocation constants are imported from _budget_constants for single-source-of-truth
sharing with experiment_shallow.sh preview and pipeline budgeting.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from computronium.experiment.kernel.evaluate import TaskScheduler
from computronium.experiment.schema.coordinate import Coordinate, Schedule

if TYPE_CHECKING:
    from collections.abc import Sequence

    from computronium.experiment.schema.record import Record
    from computronium.experiment.schema.run_spec import RunSpec

from ._budget_constants import (
    DEFAULT_PROMOTION_FRACTION,
    FIDELITY_ORDER,
    MIN_PROMOTIONS_PER_TIER,
)


def _source_fidelity_for(target_fidelity: str) -> str | None:
    """Map target fidelity to its source fidelity."""
    return {"L1": "L0", "L2": "L1"}.get(target_fidelity)


def build_promotion_schedule(
    sched: Schedule,
    target_fidelity: str,
    task_name: str,
    spec: RunSpec,
) -> Schedule:
    """Build a promotion schedule with the target fidelity and task.

    Args:
        sched: The source schedule.
        target_fidelity: Target fidelity (L1 or L2).
        task_name: The task name to use.
        spec: The run spec containing fidelity_seeds/fidelity_epochs.

    Returns:
        A new Schedule for the promotion.
    """
    fidelity_seeds = spec.fidelity_seeds or {"L0": 1, "L1": 2, "L2": 5}
    fidelity_epochs = spec.fidelity_epochs or {"L0": 1, "L1": 3, "L2": 10}

    return Schedule(
        fidelity=target_fidelity,
        seed=sched.seed,
        n_seeds=fidelity_seeds.get(target_fidelity, sched.n_seeds),
        epochs=fidelity_epochs.get(target_fidelity, sched.epochs),
        batch_limit=sched.batch_limit,
        budget_id=f"promotion_{target_fidelity}",
        task_id=task_name,
        param_budget=sched.param_budget,
        device=sched.device,
        deterministic=sched.deterministic,
        num_workers=sched.num_workers,
        precision=sched.precision,
        checkpoint_every_n=spec.checkpoint_every_n,
        early_stopping_patience=spec.early_stopping_patience,
        distributed_backend=sched.distributed_backend,
        ddp_backend=sched.ddp_backend,
        fsdp_sharding_strategy=sched.fsdp_sharding_strategy,
        fsdp_min_params=sched.fsdp_min_params,
        fsdp_cpu_offload=sched.fsdp_cpu_offload,
        fsdp_mixed_precision=sched.fsdp_mixed_precision,
    )


@dataclass(frozen=True, slots=True)
class _CellBestEntry:
    """Best normalized accuracy and record for a cell at a fidelity."""

    norm_acc: float
    record: Record | None = None


def _build_cell_best_map(
    records: Sequence[Record], scheduler: TaskScheduler
) -> dict[str, _CellBestEntry]:
    """Build map of best normalized accuracy per cell per fidelity."""
    cell_best: dict[str, _CellBestEntry] = {}
    for record in records:
        if record.status.gate_verdict.value != "PASS" or record.status.quarantine:
            continue
        cell_key = record.cell_key
        fidelity = record.schedule.fidelity
        val_acc = record.payload.get("val_acc", 0.0)
        task_name = record.schedule.task_id or "digits"

        baseline = scheduler.get_baseline(task_name)
        norm_acc = scheduler.normalize_score(val_acc, task_name, baseline)

        key = f"{cell_key}|{fidelity}"
        if key not in cell_best or norm_acc > cell_best[key].norm_acc:
            cell_best[key] = _CellBestEntry(norm_acc=norm_acc, record=record)
    return cell_best


def _filter_promotions_by_threshold(
    promotions: Sequence[tuple[Coordinate, Schedule]],
    cell_best: dict[str, _CellBestEntry],
    threshold: float,
    spec: RunSpec,
) -> list[tuple[Coordinate, Schedule]]:
    """Filter promotions whose source fidelity record meets the threshold.

    Returns promotions with corrected schedules (target fidelity, original task).
    """
    eligible: list[tuple[Coordinate, Schedule]] = []
    for coord, sched in promotions:
        cell_key = coord.cell_key()
        target_fidelity = sched.fidelity

        source_fidelity = _source_fidelity_for(target_fidelity)
        if source_fidelity is None:
            continue

        best_key = f"{cell_key}|{source_fidelity}"
        if best_key not in cell_best:
            continue

        entry = cell_best[best_key]
        if entry.norm_acc < threshold:
            continue

        # Use the original task from the source fidelity schedule
        # Task cycling to incompatible tasks causes admission gate rejections
        # entry.record is guaranteed non-None here since cell_best only contains real records
        original_task = entry.record.schedule.task_id or "digits"  # type: ignore[union-attr]
        promo_sched = build_promotion_schedule(
            sched=sched,
            target_fidelity=target_fidelity,
            task_name=original_task,
            spec=spec,
        )
        eligible.append((coord, promo_sched))
    return eligible


def _limit_promotions_by_budget(
    eligible: Sequence[tuple[Coordinate, Schedule]],
    cell_best: dict[str, _CellBestEntry],
    spec: RunSpec,
) -> list[tuple[Coordinate, Schedule]]:
    """Limit promotions according to smart-survey budget allocation.

    Budget split: 40% for L0→L1 promotions, 40% for L1→L2 promotions,
    20% reserved for L2 deepening (handled by allocator, not here).
    """
    if not eligible:
        return list(eligible)

    # Convert to list for sorting
    eligible_list = list(eligible)

    # Sort by normalized accuracy descending (source fidelity score)
    eligible_list.sort(
        key=lambda x: (
            -cell_best.get(
                f"{x[0].cell_key()}|{_source_fidelity_for(x[1].fidelity)}",
                _CellBestEntry(norm_acc=0.0),
            ).norm_acc
        )
    )

    promo_fraction = getattr(spec, "promotion_fraction", DEFAULT_PROMOTION_FRACTION)

    # Count promotions per fidelity transition
    l0_l1_count = sum(1 for _, s in eligible if s.fidelity == "L1")
    l1_l2_count = sum(1 for _, s in eligible if s.fidelity == "L2")

    # Apply budget fractions (minimum 1 promotion per tier if any eligible)
    max_l0_l1 = max(MIN_PROMOTIONS_PER_TIER, int(l0_l1_count * promo_fraction))
    max_l1_l2 = max(MIN_PROMOTIONS_PER_TIER, int(l1_l2_count * promo_fraction))

    limited: list[tuple[Coordinate, Schedule]] = []
    l0_l1_seen = 0
    l1_l2_seen = 0
    for coord, sched in eligible:
        if sched.fidelity == "L1":
            if l0_l1_seen < max_l0_l1:
                limited.append((coord, sched))
                l0_l1_seen += 1
        elif sched.fidelity == "L2" and l1_l2_seen < max_l1_l2:
            limited.append((coord, sched))
            l1_l2_seen += 1
    return limited


def apply_smart_survey_promotion(
    promotions: Sequence[tuple[Coordinate, Schedule]],
    records: Sequence[Record],
    spec: RunSpec,
) -> list[tuple[Coordinate, Schedule]]:
    """Apply smart-survey multi-fidelity promotion rules.

    The incoming promotions already have the TARGET fidelity (L1 for L0→L1,
    L2 for L1→L2) with correct seed/epoch counts from
    _build_allocator_candidates. This function:
    - Filters by ruler-relative normalized validation_accuracy
    - Applies promotion threshold
    - Uses original task from source fidelity (avoids task cycling rejections)
    - Limits promotions to budget allocation fractions
    """
    if not records or not promotions:
        return list(promotions)

    promotion_threshold = getattr(spec, "promotion_threshold", 0.1)
    scheduler = TaskScheduler()

    cell_best = _build_cell_best_map(records, scheduler)

    eligible = _filter_promotions_by_threshold(
        promotions, cell_best, promotion_threshold, spec
    )

    return _limit_promotions_by_budget(eligible, cell_best, spec)


__all__ = [
    "DEFAULT_PROMOTION_FRACTION",
    "FIDELITY_ORDER",
    "MIN_PROMOTIONS_PER_TIER",
    "_build_cell_best_map",
    "build_promotion_schedule",
    "_filter_promotions_by_threshold",
    "_limit_promotions_by_budget",
    "_source_fidelity_for",
    "apply_smart_survey_promotion",
]
