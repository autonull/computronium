"""Deduplication utilities for experiment records.

Shared utilities for computing and working with the (cell_key, seed, fidelity)
composite key that identifies a unique cell measurement across runs/rounds.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from computronium.experiment.schema.record import Record


def dedup_key(record: Record) -> tuple[str, int, str]:
    """Compute the deduplication key for a record.

    The key is (cell_key, seed, fidelity) which identifies a unique
    cell measurement across runs/rounds, ignoring budget_id which differs
    across rounds.

    Args:
        record: The record to compute the key for.

    Returns:
        Tuple of (cell_key, seed, fidelity).
    """
    return (record.cell_key, record.schedule.seed, record.schedule.fidelity)


def measurement_key(record: Record) -> str:
    """Compute the replication key for a record.

    Identifies one cell's replication group: the same structural cell, task,
    fidelity and training depth. Seed is excluded (that is the replicate);
    ``task_id`` is included because two tasks are two measurements, and a key
    without it fuses four tasks' seeds into one fictional n=12 group.

    Format: ``cell_key|fidelity|n_seeds|epochs|batch_limit|task_id``, matching
    the store's ``_REPLICATION_COLUMNS`` order.
    """
    return (
        f"{record.cell_key}|"
        f"{record.schedule.fidelity}|"
        f"{record.schedule.n_seeds}|"
        f"{record.schedule.epochs}|"
        f"{record.schedule.batch_limit}|"
        f"{record.schedule.task_id}"
    )


replication_key = measurement_key  # Alias: same key identifies replication group


__all__ = [
    "dedup_key",
    "measurement_key",
    "replication_key",
]
