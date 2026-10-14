"""Transactional cycle commit and crash recovery.

Provides checkpointing that makes "cycle N complete" durable only after
all its records commit. On crash, the loop resumes from the last
checkpoint (cycle, last_completed_cell).
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from computronium.experiment.evidence.store import RecordStore

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CycleCheckpoint:
    """Checkpoint data for a completed cycle."""

    run_id: str
    cycle_index: int
    completed_cells: tuple[str, ...]  # measurement_keys of completed cells
    last_completed_cell: str | None
    started_at: float
    completed_at: float
    budget_consumed_s: float
    records_count: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "cycle_index": self.cycle_index,
            "completed_cells": list(self.completed_cells),
            "last_completed_cell": self.last_completed_cell,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "budget_consumed_s": self.budget_consumed_s,
            "records_count": self.records_count,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CycleCheckpoint:
        return cls(
            run_id=data["run_id"],
            cycle_index=data["cycle_index"],
            completed_cells=tuple(data["completed_cells"]),
            last_completed_cell=data.get("last_completed_cell"),
            started_at=data["started_at"],
            completed_at=data["completed_at"],
            budget_consumed_s=data["budget_consumed_s"],
            records_count=data["records_count"],
            metadata=data.get("metadata", {}),
        )


@dataclass(frozen=True, slots=True)
class RunCheckpoint:
    """Full run checkpoint including all cycle checkpoints."""

    run_id: str
    spec_hash: str
    cycle_checkpoints: tuple[CycleCheckpoint, ...]
    current_cycle: int
    created_at: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "spec_hash": self.spec_hash,
            "cycle_checkpoints": [c.to_dict() for c in self.cycle_checkpoints],
            "current_cycle": self.current_cycle,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RunCheckpoint:
        return cls(
            run_id=data["run_id"],
            spec_hash=data["spec_hash"],
            cycle_checkpoints=tuple(
                CycleCheckpoint.from_dict(c) for c in data["cycle_checkpoints"]
            ),
            current_cycle=data["current_cycle"],
            created_at=data["created_at"],
            metadata=data.get("metadata", {}),
        )

    def latest_cycle(self) -> CycleCheckpoint | None:
        """Get the most recent completed cycle checkpoint."""
        if not self.cycle_checkpoints:
            return None
        return max(self.cycle_checkpoints, key=lambda c: c.cycle_index)


class CheckpointManager:
    """Manages transactional cycle checkpoints using the evidence store.

    Checkpoints are stored in the `checkpoints` table (already exists
    in RecordStore schema). A cycle is only considered complete when
    its checkpoint is written atomically with all its records.
    """

    def __init__(self, store: RecordStore, run_id: str, spec_hash: str) -> None:
        self._store = store
        self._run_id = run_id
        self._spec_hash = spec_hash
        self._cycle_start_time: float | None = None
        self._current_cycle = 0
        self._completed_cells: list[str] = []
        self._cycle_records_count = 0

    def start_cycle(self, cycle_index: int) -> None:
        """Mark the start of a new cycle."""
        self._current_cycle = cycle_index
        self._cycle_start_time = time.monotonic()
        self._completed_cells = []
        self._cycle_records_count = 0

    def record_cell_completed(self, measurement_key: str) -> None:
        """Record that a cell completed in the current cycle."""
        self._completed_cells.append(measurement_key)
        self._cycle_records_count += 1

    def commit_cycle(self, budget_consumed_s: float) -> CycleCheckpoint:
        """Commit the current cycle as a durable checkpoint.

        This writes the checkpoint to the store atomically. Only after
        this call is the cycle considered "complete" for recovery purposes.
        """
        if self._cycle_start_time is None:
            raise RuntimeError("Cannot commit cycle: no cycle started")

        completed_at = time.monotonic()
        checkpoint = CycleCheckpoint(
            run_id=self._run_id,
            cycle_index=self._current_cycle,
            completed_cells=tuple(self._completed_cells),
            last_completed_cell=self._completed_cells[-1]
            if self._completed_cells
            else None,
            started_at=self._cycle_start_time,
            completed_at=completed_at,
            budget_consumed_s=budget_consumed_s,
            records_count=self._cycle_records_count,
        )

        # Store in the checkpoints table (already exists in schema)
        run_checkpoint = self._load_run_checkpoint()
        cycle_checkpoints = (
            list(run_checkpoint.cycle_checkpoints) if run_checkpoint else []
        )
        cycle_checkpoints.append(checkpoint)

        new_run_checkpoint = RunCheckpoint(
            run_id=self._run_id,
            spec_hash=self._spec_hash,
            cycle_checkpoints=tuple(cycle_checkpoints),
            current_cycle=self._current_cycle,
            created_at=completed_at,
        )

        self._store.save_checkpoint(self._run_id, new_run_checkpoint.to_dict())
        logger.info(
            "Committed cycle %d checkpoint: %d cells, %.1fs",
            self._current_cycle,
            len(self._completed_cells),
            completed_at - self._cycle_start_time,
        )
        return checkpoint

    def _load_run_checkpoint(self) -> RunCheckpoint | None:
        """Load the full run checkpoint from store."""
        data = self._store.load_checkpoint(self._run_id)
        if data is None:
            return None
        return RunCheckpoint.from_dict(data)

    def get_resume_point(self) -> tuple[int, list[str]] | None:
        """Get the resume point: (next_cycle_index, completed_cell_keys).

        Returns None if no checkpoint exists (fresh run).
        """
        run_checkpoint = self._load_run_checkpoint()
        if run_checkpoint is None:
            return None

        latest = run_checkpoint.latest_cycle()
        if latest is None:
            return None

        # Next cycle is the one after the latest completed
        next_cycle = latest.cycle_index + 1
        return (next_cycle, list(latest.completed_cells))

    def get_completed_cells(self, cycle_index: int) -> list[str]:
        """Get all completed cells for a specific cycle."""
        run_checkpoint = self._load_run_checkpoint()
        if run_checkpoint is None:
            return []
        for cp in run_checkpoint.cycle_checkpoints:
            if cp.cycle_index == cycle_index:
                return list(cp.completed_cells)
        return []


def compute_spec_hash(spec_dict: dict[str, Any]) -> str:
    """Compute SHA256 of a RunSpec dict for checkpoint validation."""
    import hashlib

    canonical = json.dumps(spec_dict, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


__all__ = [
    "CheckpointManager",
    "CycleCheckpoint",
    "RunCheckpoint",
    "compute_spec_hash",
]
