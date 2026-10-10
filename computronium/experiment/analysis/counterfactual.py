"""Counterfactual Analysis (Phase D2).

Generates counterfactual trajectories: "What if this cell used energy_minimization
instead of instantaneous?" by swapping axes and comparing outcomes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.schema.record import Record


@dataclass(frozen=True, slots=True)
class CounterfactualResult:
    """Result of counterfactual analysis."""

    original_record: Record
    counterfactual_axis: str
    counterfactual_value: str
    predicted_metric: float
    actual_metric: float | None
    difference: float
    confidence: float
    metadata: dict[str, Any]


@dataclass(frozen=True, slots=True)
class CounterfactualConfig:
    """Configuration for counterfactual analysis."""

    n_neighbors: int = 5
    metric: str = "val_acc"
    random_state: int = 42


def _find_matching_records(
    records: list[Record],
    target_record: Record,
    axis_to_swap: str,
    target_value: str,
    other_axes: list[str],
) -> list[Record]:
    """Find records that match on all axes except the one being swapped."""
    matches = []
    for r in records:
        if getattr(r, axis_to_swap) != target_value:
            continue
        # Check other axes match
        match = True
        for axis in other_axes:
            if getattr(r, axis) != getattr(target_record, axis):
                match = False
                break
        if match:
            matches.append(r)
    return matches


def compute_counterfactual_trajectory(
    records: list[Record],
    target_record: Record,
    axis_to_swap: str,
    target_value: str,
    metric: str = "val_acc",
    config: CounterfactualConfig | None = None,
) -> CounterfactualResult:
    """Compute counterfactual: what if target_record used target_value for

    axis_to_swap?
    """
    config = config or CounterfactualConfig()

    other_axes = [
        a
        for a in ["substrate", "geometry", "dynamics", "plasticity", "credit", "update"]
        if a != axis_to_swap
    ]

    # Find matching records with the counterfactual value
    matches = _find_matching_records(
        records, target_record, axis_to_swap, target_value, other_axes
    )

    if not matches:
        return CounterfactualResult(
            original_record=target_record,
            counterfactual_axis=axis_to_swap,
            counterfactual_value=target_value,
            predicted_metric=0.0,
            actual_metric=None,
            difference=0.0,
            confidence=0.0,
            metadata={"error": "No matching records found"},
        )

    # Predict metric using mean of matches
    predicted = np.mean([m.payload.get(metric, 0.0) for m in matches])
    actual = target_record.payload.get(metric, 0.0)

    return CounterfactualResult(
        original_record=target_record,
        counterfactual_axis=axis_to_swap,
        counterfactual_value=target_value,
        predicted_metric=float(predicted),
        actual_metric=float(actual) if actual is not None else None,
        difference=float(predicted - actual) if actual is not None else 0.0,
        confidence=min(1.0, len(matches) / config.n_neighbors),
        metadata={
            "n_matches": len(matches),
            "metric": metric,
            "original_value": getattr(target_record, axis_to_swap),
        },
    )


def analyze_counterfactuals(
    records: list[Record],
    target_records: list[Record] | None = None,
    axes_to_swap: list[str] | None = None,
    metric: str = "val_acc",
    config: CounterfactualConfig | None = None,
) -> list[CounterfactualResult]:
    """Run counterfactual analysis on multiple records."""
    config = config or CounterfactualConfig()

    if target_records is None:
        target_records = records

    if axes_to_swap is None:
        axes_to_swap = [
            "substrate",
            "geometry",
            "dynamics",
            "plasticity",
            "credit",
            "update",
        ]

    results = []
    for target in target_records:
        for axis in axes_to_swap:
            original_value = getattr(target, axis)
            # Get all possible values for this axis
            possible_values = list({getattr(r, axis) for r in records})
            for value in possible_values:
                if value != original_value:
                    result = compute_counterfactual_trajectory(
                        records, target, axis, value, metric, config
                    )
                    results.append(result)

    return results


class CounterfactualAnalyzer:
    """Analyze counterfactual trajectories."""

    def __init__(
        self,
        store: RecordStore,
        run_id: str,
        config: CounterfactualConfig | None = None,
    ):
        self.store = store
        self.run_id = run_id
        self.config = config or CounterfactualConfig()

    def analyze(
        self,
        axes: list[str] | None = None,
        metric: str = "val_acc",
        n_targets: int = 10,
    ) -> list[CounterfactualResult]:
        """Run counterfactual analysis."""
        from computronium.experiment.surface.report import ReportGenerator

        generator = ReportGenerator(self.store)
        records = generator._store.query_records(run_id=self.run_id)

        if not records:
            return []

        # Select target records (e.g., top performing)
        target_records = sorted(
            records,
            key=lambda r: r.payload.get(metric, 0.0),
            reverse=True,
        )[:n_targets]

        return analyze_counterfactuals(
            records, target_records, axes, metric, self.config
        )
