"""Public values, errors and replication helpers for the evidence store."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Final, Literal

from ._validation import (  # ruff: ignore[unused-import]
    ProvenanceModel,
    RecordInputModel,
    RecordOutputModel,
    ScheduleModel,
    StatusModel,
    validate_record_input,
    validate_record_output,
)

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime
    from pathlib import Path

    from computronium.experiment.schema.run_spec import RunSpec


class DuplicateMeasurementError(Exception):
    """Raised when a measurement_key already exists (UNIQUE constraint violation)."""

    def __init__(self, measurement_key: str) -> None:
        self.measurement_key = measurement_key
        super().__init__(f"Duplicate measurement_key: {measurement_key}")


class StoreError(Exception):
    """Base exception for store errors."""


class UnsupportedSchemaVersionError(StoreError):
    """Raised when a row carries an unknown schema_version (fail-closed, Directive 2)."""


type TableName = Literal["records", "artifacts", "runs", "vector_index"]


@dataclass(frozen=True, slots=True)
class RunInfo:
    """Public read-model row for the runs table."""

    run_id: str
    spec: RunSpec | None
    spec_version: int
    status: str
    budget_consumed_s: float | None
    replay_hash: str | None
    started_at: datetime
    finished_at: datetime | None
    last_heartbeat: datetime | None


@dataclass(frozen=True, slots=True)
class TableSlice:
    """Column-typed result of a public table read."""

    columns: tuple[str, ...]
    rows: tuple[tuple[Any, ...], ...]


@dataclass(frozen=True, slots=True)
class StoreConfig:
    """Configuration for RecordStore."""

    path: Path
    read_only: bool = False
    artifact_inline_threshold_mb: float = 10.0
    artifact_external_path: Path | None = None
    # Where a copy of the store is published for readers in other processes.
    mirror_path: Path | None = None
    # How often the mirror may be published, at most.
    mirror_interval: float = 2.0


_REPLICATION_COLUMNS: Final[str] = (
    "cell_key, schedule.fidelity, schedule.n_seeds, schedule.epochs, "
    "schedule.batch_limit, schedule.budget_id"
)
_REPLICATION_CONDITIONS: Final[tuple[str, ...]] = (
    "cell_key = ?",
    "schedule.fidelity = ?",
    "schedule.n_seeds = ?",
    "schedule.epochs = ?",
    "schedule.batch_limit = ?",
    "schedule.budget_id = ?",
)


def format_replication_key(parts: Sequence[object]) -> str:
    """Format a replication key from its six parts, in the canonical order."""
    return "|".join(str(part) for part in parts)


def _replication_predicate(replication_key: str) -> tuple[list[str], list[Any]]:
    """Split a replication key into its SQL conditions and bound parameters."""
    parts = replication_key.split("|")
    if len(parts) != 6:
        msg = f"malformed replication key: {replication_key!r}"
        raise StoreError(msg)
    return [*_REPLICATION_CONDITIONS], [
        parts[0],
        parts[1],
        int(parts[2]),
        int(parts[3]),
        int(parts[4]),
        parts[5],
    ]


__all__ = [
    "DuplicateMeasurementError",
    "ProvenanceModel",
    "RecordInputModel",
    "RecordOutputModel",
    "RunInfo",
    "ScheduleModel",
    "StatusModel",
    "StoreConfig",
    "StoreError",
    "TableName",
    "TableSlice",
    "UnsupportedSchemaVersionError",
    "format_replication_key",
    "validate_record_input",
    "validate_record_output",
]
