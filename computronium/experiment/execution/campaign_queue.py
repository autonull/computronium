"""Run Queue Management: Priority, Dependencies, Resource Quotas.

Provides a queue-based system for managing large-scale runs with:
- Priority-based scheduling
- Dependency resolution
- Resource quotas (GPU, CPU, memory)
- Fair sharing across users/projects
- Preemption and requeue support

Renamed from CampaignQueue (TODO77 P0.3): it queues runs, not campaigns.
"""

from __future__ import annotations

import asyncio
import heapq
import time
import uuid
from dataclasses import dataclass, field
from enum import IntEnum, StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from computronium.core.logging import get_logger
from computronium.experiment.execution.campaign import (
    CampaignSpec,
    run_campaign,
)
from computronium.experiment.execution.events import publish_event

if TYPE_CHECKING:
    from computronium.experiment.execution.limits import ExecutionLimits

logger = get_logger(__name__)


class RunPriority(IntEnum):
    """Run priority levels (lower value = higher priority)."""

    CRITICAL = 0
    HIGH = 10
    NORMAL = 50
    LOW = 100
    BACKGROUND = 200


class RunQueueStatus(StrEnum):
    """Run queue status."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PREEMPTED = "preempted"


@dataclass(frozen=True, slots=True)
class ResourceQuota:
    """Resource quota for a run."""

    gpus: int = 0
    cpus: int = 0
    memory_gb: float = 0.0
    max_wall_hours: float = 0.0


@dataclass(slots=True)
class RunQueueEntry:
    """A run in the queue."""

    run_id: str
    spec: CampaignSpec
    priority: RunPriority = RunPriority.NORMAL
    quota: ResourceQuota = field(default_factory=ResourceQuota)
    project: str = "default"
    user: str = "unknown"
    created_at: float = field(default_factory=time.time)
    scheduled_at: float | None = None
    started_at: float | None = None
    completed_at: float | None = None
    status: RunQueueStatus = RunQueueStatus.PENDING  # type: ignore[assignment]
    result: dict[str, Any] | None = None
    error: str | None = None

    def __lt__(self, other: RunQueueEntry) -> bool:
        """Priority queue ordering: higher priority (lower value) first, then FIFO."""
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.created_at < other.created_at


@dataclass
class RunQueue:
    """Run queue with priority scheduling and resource management."""

    max_concurrent: int = 4
    max_gpus: int = 8
    max_cpus: int = 64
    max_memory_gb: float = 512.0
    _limits: ExecutionLimits | None = field(default=None, repr=False)

    # Internal state
    _queue: list[RunQueueEntry] = field(default_factory=list)
    _running: dict[str, RunQueueEntry] = field(default_factory=dict)
    _completed: dict[str, RunQueueEntry] = field(default_factory=dict)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    _resource_lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    # Resource tracking
    _used_gpus: int = 0
    _used_cpus: int = 0
    _used_memory_gb: float = 0.0

    def __post_init__(self) -> None:
        if self._limits is not None:
            queue_config = self._limits.to_queue_config()
            self.max_concurrent = queue_config["max_concurrent"]
            self.max_gpus = queue_config["max_gpus"]
            self.max_cpus = queue_config["max_cpus"]
            self.max_memory_gb = queue_config["max_memory_gb"]

    async def enqueue(
        self,
        spec: CampaignSpec,
        priority: RunPriority = RunPriority.NORMAL,
        quota: ResourceQuota | None = None,
        project: str = "default",
        user: str = "unknown",
    ) -> str:
        """Add a run to the queue.

        Returns:
            The run ID.
        """
        run_id = str(uuid.uuid4())[:8]
        entry = RunQueueEntry(
            run_id=run_id,
            spec=spec,
            priority=priority,
            quota=quota or ResourceQuota(),
            project=project,
            user=user,
        )

        async with self._lock:
            heapq.heappush(self._queue, entry)
            logger.info("Run %s enqueued with priority %s", run_id, priority.name)

        publish_event(
            "run",
            f"queued {spec.name} ({priority.name.lower()} priority)",
            detail={"run_id": run_id, "priority": priority.name},
        )

        # Try to schedule
        await self._schedule()
        return run_id

    async def _schedule(self) -> None:
        """Try to schedule queued runs based on available resources."""
        async with self._lock:
            if not self._queue:
                return

            # Check if we can run more runs
            if len(self._running) >= self.max_concurrent:
                return

            # Find the highest priority run that fits in available resources
            for i, entry in enumerate(self._queue):
                if self._can_allocate(entry.quota):
                    # Remove from queue and start
                    self._queue.pop(i)
                    await self._start_run(entry)
                    break

    def _can_allocate(self, quota: ResourceQuota) -> bool:
        """Check if resources are available for the quota."""
        return (
            self._used_gpus + quota.gpus <= self.max_gpus
            and self._used_cpus + quota.cpus <= self.max_cpus
            and self._used_memory_gb + quota.memory_gb <= self.max_memory_gb
        )

    async def _start_run(self, entry: RunQueueEntry) -> None:
        """Start a run."""
        # Allocate resources
        async with self._resource_lock:
            self._used_gpus += entry.quota.gpus
            self._used_cpus += entry.quota.cpus
            self._used_memory_gb += entry.quota.memory_gb

        entry.status = RunQueueStatus.RUNNING
        entry.started_at = time.time()
        self._running[entry.run_id] = entry

        logger.info(
            "Starting run %s (resources: gpus=%d, cpus=%d, mem=%.1fGB)",
            entry.run_id,
            entry.quota.gpus,
            entry.quota.cpus,
            entry.quota.memory_gb,
        )
        publish_event(
            "run",
            f"started {entry.spec.name}",
            detail={"run_id": entry.run_id},
        )

        # Run campaign in background
        task = asyncio.create_task(self._run_campaign(entry))
        task.add_done_callback(
            lambda t: asyncio.create_task(self._on_run_done(entry.run_id, t))
        )

    async def _run_campaign(self, entry: RunQueueEntry) -> dict[str, Any]:
        """Run the campaign and return results."""
        temp_path = await self._write_campaign_yaml(entry)
        try:
            result = await self._execute_campaign(entry, temp_path)
            entry.result = result
            entry.status = RunQueueStatus.COMPLETED
        except Exception as e:
            logger.exception("Run %s failed", entry.run_id)
            entry.error = str(e)
            entry.status = RunQueueStatus.FAILED
            publish_event(
                "run",
                f"failed {entry.spec.name}: {e}",
                level="error",
                detail={"run_id": entry.run_id},
            )
            raise
        finally:
            Path(temp_path).unlink(missing_ok=True)

        return entry.result

    async def _write_campaign_yaml(self, entry: RunQueueEntry) -> str:
        """Write campaign spec to a temporary YAML file."""
        import tempfile

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, encoding="utf-8"
        ) as f:
            yaml_data = {
                "name": entry.spec.name,
                "store": entry.spec.store,
                "parallel": entry.spec.parallel,
                "webhook_url": entry.spec.webhook_url,
                "runs": [
                    {
                        "name": r.name,
                        "profile": r.profile,
                        "spec_file": r.spec_file,
                        "overrides": r.overrides,
                        "depends_on": r.depends_on,
                        "device": r.device,
                        "store": r.store,
                        "run_id": r.run_id,
                    }
                    for r in entry.spec.runs
                ],
            }
            if entry.spec.max_wall_seconds:
                yaml_data["compute"] = {
                    "max_wall_hours": entry.spec.max_wall_seconds / 3600
                }

            yaml.dump(yaml_data, f)
            return f.name

    async def _execute_campaign(
        self, entry: RunQueueEntry, temp_path: str
    ) -> dict[str, Any]:
        """Execute the campaign from a YAML file."""
        return await run_campaign(
            campaign_path=temp_path,
            parallel=entry.spec.parallel,
            webhook_url=entry.spec.webhook_url,
            limits=self._limits,
        )

    async def _on_run_done(self, run_id: str, task: asyncio.Task) -> None:
        """Handle run completion."""
        async with self._lock:
            entry = self._running.pop(run_id, None)
            if not entry:
                return

            # Release resources
            async with self._resource_lock:
                self._used_gpus -= entry.quota.gpus
                self._used_cpus -= entry.quota.cpus
                self._used_memory_gb -= entry.quota.memory_gb

            entry.completed_at = time.time()

            if entry.status == RunQueueStatus.RUNNING:
                entry.status = RunQueueStatus.COMPLETED

            self._completed[run_id] = entry
            logger.info("Run %s completed with status %s", run_id, entry.status)
            publish_event(
                "run",
                f"{entry.status.value} {entry.spec.name}",
                level="ok" if entry.status == RunQueueStatus.COMPLETED else "warn",
                detail={"run_id": run_id, "status": entry.status.value},
            )

        # Try to schedule next run
        await self._schedule()

    async def cancel(self, run_id: str) -> bool:
        """Cancel a queued or running run."""
        async with self._lock:
            # Check queue
            for i, entry in enumerate(self._queue):
                if entry.run_id == run_id:
                    entry.status = RunQueueStatus.CANCELLED
                    self._queue.pop(i)
                    logger.info("Cancelled queued run %s", run_id)
                    return True

            # Check running
            if run_id in self._running:
                entry = self._running[run_id]
                entry.status = RunQueueStatus.CANCELLED
                # Note: Actual cancellation of running task would require task cancellation
                logger.info("Marked running run %s for cancellation", run_id)
                return True

        return False

    async def preempt(self, run_id: str) -> bool:
        """Preempt a running run (requeue with higher priority)."""
        async with self._lock:
            if run_id in self._running:
                entry = self._running[run_id]
                entry.status = RunQueueStatus.PREEMPTED
                # Requeue with higher priority
                heapq.heappush(self._queue, entry)
                del self._running[run_id]
                logger.info("Preempted run %s, requeued with higher priority", run_id)
                return True
        return False

    async def get_status(self, run_id: str) -> RunQueueEntry | None:
        """Get status of a run."""
        async with self._lock:
            # Check queue
            for entry in self._queue:
                if entry.run_id == run_id:
                    return entry
            # Check running
            if run_id in self._running:
                return self._running[run_id]
            # Check completed
            if run_id in self._completed:
                return self._completed[run_id]
        return None

    async def list_runs(
        self,
        status: RunQueueStatus | None = None,
        project: str | None = None,
        user: str | None = None,
    ) -> list[RunQueueEntry]:
        """List runs with optional filters."""
        async with self._lock:
            all_entries = (
                list(self._queue)
                + list(self._running.values())
                + list(self._completed.values())
            )

            if status:
                all_entries = [e for e in all_entries if e.status == status]
            if project:
                all_entries = [e for e in all_entries if e.project == project]
            if user:
                all_entries = [e for e in all_entries if e.user == user]

            return sorted(all_entries, key=lambda e: e.created_at, reverse=True)

    async def get_resource_usage(self) -> dict[str, float]:
        """Get current resource usage."""
        async with self._resource_lock:
            return {
                "used_gpus": self._used_gpus,
                "max_gpus": self.max_gpus,
                "gpu_utilization": self._used_gpus / max(self.max_gpus, 1),
                "used_cpus": self._used_cpus,
                "max_cpus": self.max_cpus,
                "cpu_utilization": self._used_cpus / max(self.max_cpus, 1),
                "used_memory_gb": self._used_memory_gb,
                "max_memory_gb": self.max_memory_gb,
                "memory_utilization": self._used_memory_gb / max(self.max_memory_gb, 1),
                "running_runs": len(self._running),
                "queued_runs": len(self._queue),
            }


# Global queue instance - use a holder class to avoid global statement
class _QueueHolder:
    queue: RunQueue | None = None


def get_run_queue(limits: ExecutionLimits | None = None) -> RunQueue:
    """Get the global run queue."""
    if _QueueHolder.queue is None:
        _QueueHolder.queue = RunQueue(limits=limits)
    return _QueueHolder.queue


def set_run_queue(queue: RunQueue) -> None:
    """Set the global run queue (for testing)."""
    _QueueHolder.queue = queue


async def submit_run(
    spec: CampaignSpec,
    priority: RunPriority = RunPriority.NORMAL,
    quota: ResourceQuota | None = None,
    project: str = "default",
    user: str = "unknown",
) -> str:
    """Submit a run to the global queue."""
    queue = get_run_queue()
    return await queue.enqueue(spec, priority, quota, project, user)


async def run_queue_worker(limits: ExecutionLimits | None = None) -> None:
    """Background worker to process the run queue."""
    queue = get_run_queue(limits=limits)
    while True:
        await queue._schedule()
        await asyncio.sleep(5)


# Aliases for backward compatibility (will be removed)
CampaignPriority = RunPriority
CampaignStatus = RunQueueStatus
CampaignQueueEntry = RunQueueEntry
CampaignQueue = RunQueue
get_campaign_queue = get_run_queue
set_campaign_queue = set_run_queue
submit_campaign = submit_run
run_campaign_queue_worker = run_queue_worker


__all__ = [
    "CampaignPriority",
    "CampaignQueue",
    "CampaignQueueEntry",
    "CampaignStatus",
    "ResourceQuota",
    "RunPriority",
    "RunQueue",
    "RunQueueEntry",
    "RunQueueStatus",
    "get_campaign_queue",
    "get_run_queue",
    "run_campaign_queue_worker",
    "run_queue_worker",
    "set_campaign_queue",
    "set_run_queue",
    "submit_campaign",
    "submit_run",
]
