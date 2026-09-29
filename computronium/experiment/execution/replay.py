"""Replay, resume, and checkpoint functionality for experiment execution (WP4)."""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.schema.coordinate import Coordinate, Schedule
    from computronium.experiment.schema.record import Record


logger = logging.getLogger(__name__)


def _canonical_json(obj: Any) -> str:
    """Serialize to canonical JSON for hashing."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_replay_hash(
    coordinate: Coordinate,
    schedule: Schedule,
    provenance: dict[str, Any],
    params: dict[str, Any],
) -> str:
    """Compute a deterministic replay hash for an experiment cell.

    The replay hash uniquely identifies an experiment configuration and
    enables exact reproduction. It includes:
    - Structural coordinate (6 axes + params)
    - Schedule (fidelity, seed, n_seeds, epochs, batch_limit, budget_id)
    - Provenance (env, dataset, code_sha, policy, links)
    - Parameters

    Args:
        coordinate: The 6-axis experiment coordinate
        schedule: Execution schedule
        provenance: Provenance metadata
        params: Experiment parameters

    Returns:
        SHA256 hash as hex string (64 chars).
    """
    replay_data = {
        "coordinate": coordinate.to_dict(),
        "schedule": schedule.to_dict(),
        "provenance": provenance,
        "params": params,
    }
    return hashlib.sha256(_canonical_json(replay_data).encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class Checkpoint:
    """Checkpoint for experiment resumption.

    Contains all information needed to resume an interrupted experiment run.
    """

    run_id: str
    run_spec: dict[str, Any]  # RunSpec as dict
    completed_measurement_keys: frozenset[str]
    pending_candidates: list[tuple[Coordinate, Schedule]]  # Not yet started
    in_progress: list[tuple[Coordinate, Schedule]]  # Started but not completed
    budget_state: dict[str, Any]  # Budget serialization
    allocator_state: dict[str, Any] | None = None  # AllocationState serialization
    timestamp: float = 0.0  # time.monotonic()

    def to_file(self, path: Path) -> None:
        """Write checkpoint to JSON file."""
        data = {
            "run_id": self.run_id,
            "run_spec": self.run_spec,
            "completed_measurement_keys": list(self.completed_measurement_keys),
            "pending_candidates": [
                {"coordinate": c.to_dict(), "schedule": s.to_dict()}
                for c, s in self.pending_candidates
            ],
            "in_progress": [
                {"coordinate": c.to_dict(), "schedule": s.to_dict()}
                for c, s in self.in_progress
            ],
            "budget_state": self.budget_state,
            "allocator_state": self.allocator_state,
            "timestamp": self.timestamp,
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def from_file(cls, path: Path) -> Checkpoint:
        """Load checkpoint from JSON file."""
        from computronium.experiment.schema.coordinate import Coordinate, Schedule

        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            run_id=data["run_id"],
            run_spec=data["run_spec"],
            completed_measurement_keys=frozenset(data["completed_measurement_keys"]),
            pending_candidates=[
                (
                    Coordinate.from_dict(c["coordinate"]),
                    Schedule.from_dict(c["schedule"]),
                )
                for c in data["pending_candidates"]
            ],
            in_progress=[
                (
                    Coordinate.from_dict(c["coordinate"]),
                    Schedule.from_dict(c["schedule"]),
                )
                for c in data["in_progress"]
            ],
            budget_state=data["budget_state"],
            allocator_state=data.get("allocator_state"),
            timestamp=data.get("timestamp", 0.0),
        )


def resume_from_store(
    store: RecordStore,
    run_id: str,
    all_candidates: list[tuple[Coordinate, Schedule]],
) -> tuple[list[tuple[Coordinate, Schedule]], list[tuple[Coordinate, Schedule]]]:
    """Determine which candidates to resume and which are already done.

    Uses measurement_key deduplication to find already-completed cells.

    Args:
        store: RecordStore to query
        run_id: Run ID to resume
        all_candidates: All candidate (coordinate, schedule) pairs for this run

    Returns:
        Tuple of (completed_candidates, remaining_candidates)
    """
    # Get all records for this run
    existing_records = store.query_records(run_id=run_id)
    completed_keys = {r.measurement_key for r in existing_records}

    completed = []
    remaining = []

    for coord, sched in all_candidates:
        measurement_key = coord.measurement_key(sched)
        if measurement_key in completed_keys:
            completed.append((coord, sched))
        else:
            remaining.append((coord, sched))

    logger.info(
        "Resume run %s: %d completed, %d remaining",
        run_id,
        len(completed),
        len(remaining),
    )
    return completed, remaining


def find_existing_record(
    store: RecordStore,
    coordinate: Coordinate,
    schedule: Schedule,
) -> Record | None:
    """Find an existing record by measurement_key (for exact resume).

    Args:
        store: RecordStore to query
        coordinate: Experiment coordinate
        schedule: Execution schedule

    Returns:
        Existing Record if found, None otherwise.
    """
    measurement_key = coordinate.measurement_key(schedule)
    return store.get_record_by_measurement_key(measurement_key)


@dataclass(frozen=True, slots=True)
class ResumeResult:
    """Result of a resume operation."""

    skipped: int
    resumed: int
    total: int


def resume_run(
    store: RecordStore,
    run_id: str,
    coordinate: Coordinate,
    schedule: Schedule,
    provenance: dict[str, Any],
    params: dict[str, Any],
    force_new: bool = False,
) -> tuple[Record | None, bool]:
    """Attempt to resume a specific cell from the store.

    If a record with the same measurement_key exists and force_new is False,
    returns the existing record and True (skipped). Otherwise returns (None, False).

    Args:
        store: RecordStore to query
        run_id: Run ID
        coordinate: Experiment coordinate
        schedule: Execution schedule
        provenance: Provenance metadata
        params: Experiment parameters
        force_new: If True, ignore existing records and force new execution

    Returns:
        Tuple of (existing_record_or_None, was_skipped)
    """
    if force_new:
        return None, False

    measurement_key = coordinate.measurement_key(schedule)
    existing = store.get_record_by_measurement_key(measurement_key)

    if existing is not None:
        # Verify it belongs to the same run
        if existing.run_id == run_id:
            logger.info(
                "Resuming cell %s from store (measurement_key=%s)",
                coordinate.cell_key(),
                measurement_key[:16],
            )
            return existing, True
        else:
            logger.warning(
                "Measurement key collision: %s exists in run %s, not %s",
                measurement_key[:16],
                existing.run_id,
                run_id,
            )

    return None, False


def create_checkpoint(
    run_id: str,
    run_spec: dict[str, Any],
    completed_keys: frozenset[str],
    pending: list[tuple[Coordinate, Schedule]],
    in_progress: list[tuple[Coordinate, Schedule]],
    budget: Any,  # Budget object with to_dict method
    allocator_state: dict[str, Any] | None = None,
) -> Checkpoint:
    """Create a checkpoint from current execution state."""
    import time

    budget_state = budget.to_dict() if hasattr(budget, "to_dict") else {}

    return Checkpoint(
        run_id=run_id,
        run_spec=run_spec,
        completed_measurement_keys=completed_keys,
        pending_candidates=pending,
        in_progress=in_progress,
        budget_state=budget_state,
        allocator_state=allocator_state,
        timestamp=time.monotonic(),
    )


def periodic_checkpoint(
    store: RecordStore,
    run_id: str,
    checkpoint_dir: Path,
    interval_seconds: float = 60.0,
) -> Path:
    """Create a periodic checkpoint file.

    Args:
        store: RecordStore to query
        run_id: Run ID
        checkpoint_dir: Directory for checkpoint files
        interval_seconds: Minimum interval between checkpoints (not enforced here)

    Returns:
        Path to created checkpoint file.
    """
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    timestamp = int(time.time() * 1000)
    checkpoint_path = checkpoint_dir / f"checkpoint_{run_id}_{timestamp}.json"

    records = store.query_records(run_id=run_id)
    completed_keys = frozenset(r.measurement_key for r in records)

    checkpoint = Checkpoint(
        run_id=run_id,
        run_spec={},  # Would need to be passed in
        completed_measurement_keys=completed_keys,
        pending_candidates=[],
        in_progress=[],
        budget_state={},
        timestamp=time.monotonic(),
    )
    checkpoint.to_file(checkpoint_path)
    logger.debug("Created checkpoint: %s", checkpoint_path)
    return checkpoint_path


__all__ = [
    "Checkpoint",
    "ResumeResult",
    "compute_replay_hash",
    "create_checkpoint",
    "find_existing_record",
    "periodic_checkpoint",
    "resume_from_store",
    "resume_run",
]
