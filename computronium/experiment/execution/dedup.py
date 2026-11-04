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
    """Compute the measurement key for a record.

    The measurement key includes all schedule parameters except seed,
    used for grouping records by measurement configuration.

    Args:
        record: The record to compute the key for.

    Returns:
        String key in format "cell_key|fidelity|n_seeds|epochs|batch_limit|budget_id".
    """
    return (
        f"{record.cell_key}|"
        f"{record.schedule.fidelity}|"
        f"{record.schedule.n_seeds}|"
        f"{record.schedule.epochs}|"
        f"{record.schedule.batch_limit}|"
        f"{record.schedule.budget_id}"
    )


replication_key = measurement_key  # Alias: same key identifies replication group


__all__ = [
    "dedup_key",
    "measurement_key",
    "replication_key",
]
