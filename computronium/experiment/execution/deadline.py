"""Hard deadline propagation for experiment execution.

Replaces prediction-based budgeting with real-time deadline enforcement.
No historical profiling, no cost models — only measured walltime.

Contract: `--hours N` means process stops at N hours ± 30 seconds, period.
"""

from __future__ import annotations

import dataclasses
import signal
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class Deadline:
    """Hard deadline for experiment execution.

    Propagated from CLI → CampaignRunner → PipelineRunner → cell evaluation.
    No prediction, no cost model — only walltime enforcement.
    """

    deadline_ts: float  # Absolute monotonic timestamp when budget expires
    grace_seconds: float = 30.0  # Hard stop grace period
    started_at: float = 0.0  # When this deadline was created (monotonic)

    @classmethod
    def from_hours(cls, hours: float, *, grace_seconds: float = 30.0) -> Deadline:
        """Create deadline from hours budget."""
        now = time.monotonic()
        return cls(
            deadline_ts=now + hours * 3600.0,
            grace_seconds=grace_seconds,
            started_at=now,
        )

    @classmethod
    def from_seconds(cls, seconds: float, *, grace_seconds: float = 30.0) -> Deadline:
        """Create deadline from seconds budget."""
        now = time.monotonic()
        return cls(
            deadline_ts=now + seconds,
            grace_seconds=grace_seconds,
            started_at=now,
        )

    def expired(self, now: float | None = None) -> bool:
        """Check if hard deadline (including grace) has passed."""
        now = time.monotonic() if now is None else now
        return now >= self.deadline_ts + self.grace_seconds

    def soft_expired(self, now: float | None = None) -> bool:
        """Check if soft deadline (without grace) has passed.

        Use this to stop STARTING new cells.
        """
        now = time.monotonic() if now is None else now
        return now >= self.deadline_ts

    def remaining_seconds(self, now: float | None = None) -> float:
        """Seconds until hard deadline (negative if past grace)."""
        now = time.monotonic() if now is None else now
        return self.deadline_ts + self.grace_seconds - now

    def remaining_soft_seconds(self, now: float | None = None) -> float:
        """Seconds until soft deadline (negative if past soft deadline)."""
        now = time.monotonic() if now is None else now
        return self.deadline_ts - now

    def elapsed_seconds(self, now: float | None = None) -> float:
        """Seconds elapsed since deadline creation."""
        now = time.monotonic() if now is None else now
        return max(0.0, now - self.started_at)


@dataclass(slots=True)
class CellTiming:
    """Tracks walltime for individual cell evaluations.

    Used for online learning: strategy adapts based on MEASURED
    cell times in THIS run, not historical cache.
    """

    cell_count: int = 0
    total_walltime_s: float = 0.0
    cell_times: list[float] = dataclasses.field(default_factory=list)
    current_cell_start: float | None = None

    def start_cell(self) -> None:
        """Mark start of cell evaluation."""
        self.current_cell_start = time.monotonic()

    def end_cell(self) -> float:
        """Mark end of cell evaluation, return elapsed."""
        if self.current_cell_start is None:
            return 0.0
        elapsed = time.monotonic() - self.current_cell_start
        self.cell_times.append(elapsed)
        self.total_walltime_s += elapsed
        self.cell_count += 1
        self.current_cell_start = None
        return elapsed

    def median_cell_time(self) -> float | None:
        """Median walltime of completed cells in this run."""
        if not self.cell_times:
            return None
        sorted_times = sorted(self.cell_times)
        n = len(sorted_times)
        if n % 2 == 0:
            return (sorted_times[n // 2 - 1] + sorted_times[n // 2]) / 2
        return sorted_times[n // 2]

    def mean_cell_time(self) -> float | None:
        """Mean walltime of completed cells in this run."""
        if not self.cell_times:
            return None
        return self.total_walltime_s / self.cell_count

    def should_skip_slow_dynamics(
        self, deadline: Deadline, threshold: float = 2.0
    ) -> bool:
        """Check if remaining time is too short for slow cells.

        Uses ONLINE median — skip if remaining < threshold * median_cell_time.
        """
        median = self.median_cell_time()
        if median is None:
            return False
        remaining = deadline.remaining_soft_seconds()
        return remaining < threshold * median


@dataclass(frozen=True, slots=True)
class CheckpointData:
    """Serializable checkpoint for SIGTERM-aware resume.

    Captures everything needed to resume from the last completed cell.
    """

    run_id: str
    completed_measurement_keys: frozenset[str]
    pending_proposals: list[dict[str, Any]]  # Serialized proposals
    in_progress: list[dict[str, Any]]  # Serialized in-progress cells
    current_round: int
    round_controller_state: dict[str, Any]
    policy_state: dict[str, Any]  # Policy-specific state
    allocator_state: dict[str, Any] | None
    system_context_snapshot: dict[str, Any] | None
    cell_timing: dict[str, Any]  # Serialized CellTiming (mixed types)
    timestamp: float


@dataclass(frozen=True, slots=True)
class _PipelineStateSnapshot:
    """Internal snapshot of pipeline state for checkpoint creation."""

    run_id: str
    completed_keys: frozenset[str]
    pending_proposals: list
    in_progress: list
    current_round: int
    round_controller_state: dict[str, Any]
    policy_state: dict[str, Any]
    allocator_state: dict[str, Any] | None
    system_context_snapshot: dict[str, Any] | None
    cell_timing: CellTiming


def _create_checkpoint_data(snapshot: _PipelineStateSnapshot) -> CheckpointData:
    """Create CheckpointData from pipeline state snapshot."""
    return CheckpointData(
        run_id=snapshot.run_id,
        completed_measurement_keys=snapshot.completed_keys,
        pending_proposals=[_serialize_proposal(p) for p in snapshot.pending_proposals],
        in_progress=[_serialize_in_progress(ip) for ip in snapshot.in_progress],
        current_round=snapshot.current_round,
        round_controller_state=snapshot.round_controller_state,
        policy_state=snapshot.policy_state,
        allocator_state=snapshot.allocator_state,
        system_context_snapshot=snapshot.system_context_snapshot,
        cell_timing={
            "cell_count": snapshot.cell_timing.cell_count,
            "total_walltime_s": snapshot.cell_timing.total_walltime_s,
            "cell_times": snapshot.cell_timing.cell_times,
        },
        timestamp=time.monotonic(),
    )


def _serialize_proposal(proposal) -> dict[str, Any]:
    """Serialize a Proposal for checkpoint."""

    if hasattr(proposal, "coordinate") and hasattr(proposal, "schedule"):
        coord = proposal.coordinate
        sched = proposal.schedule
        return {
            "coordinate": {
                "substrate": coord.substrate,
                "geometry": coord.geometry,
                "dynamics": coord.dynamics,
                "plasticity": coord.plasticity,
                "credit": coord.credit,
                "update": coord.update,
                "params": coord.params,
            },
            "schedule": sched.to_dict() if hasattr(sched, "to_dict") else {},
            "rationale": getattr(proposal, "rationale", ""),
            "metadata": getattr(proposal, "metadata", {}),
        }
    return {}


def _serialize_in_progress(item: tuple) -> dict[str, Any]:
    """Serialize an in-progress cell for checkpoint."""
    coord, sched = item
    return {
        "coordinate": {
            "substrate": coord.substrate,
            "geometry": coord.geometry,
            "dynamics": coord.dynamics,
            "plasticity": coord.plasticity,
            "credit": coord.credit,
            "update": coord.update,
            "params": coord.params,
        },
        "schedule": sched.to_dict() if hasattr(sched, "to_dict") else {},
    }


class SignalHandler:
    """SIGTERM/SIGINT handler with checkpoint callback.

    Installed at PipelineRunner level. On signal:
    1. Sets shutdown flag
    2. Calls checkpoint callback (saves state to store)
    3. Allows current cell to complete or marks it QUARANTINE
    """

    def __init__(
        self,
        checkpoint_callback: Callable[[], None] | None = None,
        shutdown_callback: Callable[[], None] | None = None,
    ) -> None:
        self._checkpoint_callback = checkpoint_callback
        self._shutdown_callback = shutdown_callback
        self._shutdown_requested = False
        self._old_sigint: Any = None
        self._old_sigterm: Any = None
        self._installed = False

    def install(self) -> None:
        """Install signal handlers."""
        if self._installed:
            return
        try:
            self._old_sigint = signal.signal(signal.SIGINT, self._handle_signal)
            self._old_sigterm = signal.signal(signal.SIGTERM, self._handle_signal)
            self._installed = True
        except ValueError, OSError:
            # Signal handling not available (e.g., non-main thread)
            pass

    def uninstall(self) -> None:
        """Restore original signal handlers."""
        if not self._installed:
            return
        try:
            if self._old_sigint is not None:
                signal.signal(signal.SIGINT, self._old_sigint)
            if self._old_sigterm is not None:
                signal.signal(signal.SIGTERM, self._old_sigterm)
        except ValueError, OSError, AttributeError:
            pass
        self._installed = False

    def _handle_signal(self, signum: int, frame: Any) -> None:
        """Handle shutdown signal."""
        import logging

        logger = logging.getLogger(__name__)
        logger.info("Received signal %s; initiating graceful shutdown", signum)
        self._shutdown_requested = True

        # Checkpoint first (save state)
        if self._checkpoint_callback:
            try:
                self._checkpoint_callback()
            except Exception:
                logger.exception("Checkpoint failed during shutdown")

        # Then shutdown (stop accepting new work)
        if self._shutdown_callback:
            try:
                self._shutdown_callback()
            except Exception:
                logger.exception("Shutdown callback failed")

    @property
    def shutdown_requested(self) -> bool:
        """Whether a shutdown signal was received."""
        return self._shutdown_requested


class DeadlineEnforcer:
    """Enforces deadline at multiple levels with graceful degradation.

    - Before starting cell: check soft deadline
    - During long operations: periodic deadline check (via callback)
    - On hard deadline breach mid-cell: checkpoint, mark QUARANTINE, exit
    """

    def __init__(self, deadline: Deadline) -> None:
        self._deadline = deadline
        self._quarantined_cells: list[str] = []

    def check_before_cell(self) -> bool:
        """Check if we can start a new cell. Returns True if OK."""
        return not self._deadline.soft_expired()

    def check_during_cell(self) -> bool:
        """Check if cell should be aborted (hard deadline exceeded).

        Called periodically during long-running operations (settling, HPO).
        Returns True to continue, False to abort.
        """
        return not self._deadline.expired()

    def check_after_cell(self) -> bool:
        """Check if we can continue to next cell after one completes."""
        return not self._deadline.soft_expired()

    def mark_quarantine(self, cell_key: str) -> None:
        """Mark a cell as QUARANTINE (deadline breached mid-execution)."""
        self._quarantined_cells.append(cell_key)

    @property
    def quarantined_cells(self) -> tuple[str, ...]:
        """Cells that were interrupted by deadline."""
        return tuple(self._quarantined_cells)

    @property
    def deadline(self) -> Deadline:
        """Access the underlying deadline."""
        return self._deadline


def create_deadline_from_cli(
    hours: float | None = None,
    seconds: float | None = None,
    grace_seconds: float = 30.0,
) -> Deadline | None:
    """Create deadline from CLI arguments.

    Exactly one of hours or seconds must be provided.
    """
    if hours is not None and seconds is not None:
        raise ValueError("Provide either hours or seconds, not both")
    if hours is not None:
        return Deadline.from_hours(hours, grace_seconds=grace_seconds)
    if seconds is not None:
        return Deadline.from_seconds(seconds, grace_seconds=grace_seconds)
    return None


__all__ = [
    "CellTiming",
    "CheckpointData",
    "Deadline",
    "DeadlineEnforcer",
    "SignalHandler",
    "create_deadline_from_cli",
]
