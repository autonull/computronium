"""Records — personal bests on objectives (M2.5).

Derived from Pareto front + CEEC gates. No XP.
Breakthrough alerts on any objective improvement, scoped
(e.g., "New best correctness among similar size").
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


@dataclass(frozen=True, slots=True)
class Record:
    """A personal best record for an objective."""

    id: str
    objective: str  # e.g., "accuracy", "walltime_s", "param_count"
    value: float
    cell_key: str
    timestamp: float
    scope: str  # e.g., "among similar size", "global", "per substrate"
    register_explorer: str
    register_lab: str


# Objective categories for scoping records
OBJECTIVE_CATEGORIES = {
    "accuracy": "higher_is_better",
    "walltime_s": "lower_is_better",
    "param_count": "lower_is_better",
    "flops": "lower_is_better",
    "memory_mb": "lower_is_better",
    "energy_per_step": "lower_is_better",
    "latency_ms": "lower_is_better",
    "spectral_radius": "lower_is_better",
    "lyapunov_exponent": "lower_is_better",
    "max_singular_value": "lower_is_better",
    "psi_capacity": "higher_is_better",
    "consolidation_cost": "lower_is_better",
    "rewrite_rate": "lower_is_better",
    "credit_alignment": "higher_is_better",
    "feedback_path_length": "lower_is_better",
    "trace_variance": "lower_is_better",
    "bp_deficit": "lower_is_better",
    "ruler_walltime_ratio": "lower_is_better",
    "ruler_energy_ratio": "lower_is_better",
}


def _is_better(
    objective: str,
    new_value: float,
    old_value: float,
    new_cell_key: str = "",
    old_cell_key: str = "",
) -> bool:
    """Check if new_value is better than old_value for the objective.

    If values are equal, use cell_key as deterministic tiebreaker
    (lexicographically smaller wins) for order-independence.
    """
    direction = OBJECTIVE_CATEGORIES.get(objective, "higher_is_better")
    if direction == "higher_is_better":
        if new_value != old_value:
            return new_value > old_value
    elif new_value != old_value:
        return new_value < old_value
    # Values are equal - use cell_key as tiebreaker
    return new_cell_key < old_cell_key


def _format_record_message(
    objective: str, value: float, scope: str, register: str
) -> str:
    """Format a breakthrough message for the given register."""
    # Simplified formatting
    obj_name = objective.replace("_", " ")
    if register == "explorer":
        return f"New best {obj_name} {scope}: {value:.3f}"
    return f"Record {objective}={value:.6f} ({scope})"


def update_records(  # noqa: C901, PLR0912
    event_kind: str, payload: dict, existing_records: Iterable[Record]
) -> Iterable[Record]:
    """Update personal best records based on an event.

    Pure function — returns updated records (new instances).
    """
    records_list = list(existing_records)
    records_dict = {r.id: r for r in records_list}
    yielded_ids: set[str] = set()

    if event_kind == "cell_completed":
        objectives = payload.get("objectives", {})
        cell_key = payload.get("cell_key", "")
        timestamp = payload.get("timestamp", 0.0)
        substrate = payload.get("substrate", "unknown")
        topology = payload.get("topology", "unknown")

        for obj_name, value in objectives.items():
            if obj_name not in OBJECTIVE_CATEGORIES:
                continue

            record_id = f"record_{obj_name}"
            existing = records_dict.get(record_id)

            is_new_record = False
            if existing is None or _is_better(
                obj_name, value, existing.value, cell_key, existing.cell_key
            ):
                is_new_record = True

            if is_new_record:
                # Determine scope
                if substrate != "unknown" and topology != "unknown":
                    scope = f"among {substrate}×{topology}"
                else:
                    scope = "global"

                yield Record(
                    id=record_id,
                    objective=obj_name,
                    value=value,
                    cell_key=cell_key,
                    timestamp=timestamp,
                    scope=scope,
                    register_explorer=_format_record_message(
                        obj_name, value, scope, "explorer"
                    ),
                    register_lab=_format_record_message(obj_name, value, scope, "lab"),
                )
                yielded_ids.add(record_id)
            elif existing:
                yield existing
                yielded_ids.add(record_id)

    elif event_kind == "pareto_front_expanded":
        # Could also update records from Pareto front changes
        objectives = payload.get("objectives", {})
        cell_key = payload.get("cell_key", "")
        timestamp = payload.get("timestamp", 0.0)

        for obj_name, value in objectives.items():
            if obj_name not in OBJECTIVE_CATEGORIES:
                continue

            record_id = f"record_{obj_name}"
            existing = records_dict.get(record_id)

            is_new_record = False
            if existing is None or _is_better(
                obj_name, value, existing.value, cell_key, existing.cell_key
            ):
                is_new_record = True

            if is_new_record:
                scope = "Pareto front"
                yield Record(
                    id=record_id,
                    objective=obj_name,
                    value=value,
                    cell_key=cell_key,
                    timestamp=timestamp,
                    scope=scope,
                    register_explorer=_format_record_message(
                        obj_name, value, scope, "explorer"
                    ),
                    register_lab=_format_record_message(obj_name, value, scope, "lab"),
                )
                yielded_ids.add(record_id)
            elif existing:
                yield existing
                yielded_ids.add(record_id)

    # Yield unchanged records (those not processed above)
    for record in records_list:
        if record.id not in yielded_ids:
            yield record


def get_all_records(records: Iterable[Record]) -> list[Record]:
    """Get all records sorted by timestamp (newest first)."""
    return sorted(records, key=lambda r: r.timestamp, reverse=True)


def get_records_by_objective(records: Iterable[Record], objective: str) -> list[Record]:
    """Get records for a specific objective."""
    return [r for r in records if r.objective == objective]
