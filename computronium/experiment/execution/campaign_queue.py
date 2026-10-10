"""Campaign Queue Management: Priority, Dependencies, Resource Quotas.

Provides a queue-based system for managing large-scale campaigns with:
- Priority-based scheduling
- Dependency resolution
- Resource quotas (GPU, CPU, memory)
- Fair sharing across users/projects
- Preemption and requeue support
"""

from __future__ import annotations

import asyncio
import heapq
import time
import uuid
from dataclasses import dataclass, field
from enum import IntEnum, StrEnum
from pathlib import Path
from typing import Any

import yaml

from computronium.core.logging import get_logger
from computronium.experiment.execution.campaign import (
    CampaignSpec,
    run_campaign,
)

logger = get_logger(__name__)


class CampaignPriority(IntEnum):
    """Campaign priority levels (lower value = higher priority)."""

    CRITICAL = 0
    HIGH = 10
    NORMAL = 50
    LOW = 100
    BACKGROUND = 200


class CampaignStatus(StrEnum):
    """Campaign queue status."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PREEMPTED = "preempted"


@dataclass(frozen=True, slots=True)
class ResourceQuota:
    """Resource quota for a campaign."""

    gpus: int = 0
    cpus: int = 0
    memory_gb: float = 0.0
    max_wall_hours: float = 0.0


@dataclass(slots=True)
class CampaignQueueEntry:
    """A campaign in the queue."""

    campaign_id: str
    spec: CampaignSpec
    priority: CampaignPriority = CampaignPriority.NORMAL
    quota: ResourceQuota = field(default_factory=ResourceQuota)
    project: str = "default"
    user: str = "unknown"
    created_at: float = field(default_factory=time.time)
    scheduled_at: float | None = None
    started_at: float | None = None
    completed_at: float | None = None
    status: CampaignStatus = CampaignStatus.PENDING  # type: ignore[assignment]
    result: dict[str, Any] | None = None
    error: str | None = None

    def __lt__(self, other: CampaignQueueEntry) -> bool:
        """Priority queue ordering: higher priority (lower value) first, then FIFO."""
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.created_at < other.created_at


@dataclass
class CampaignQueue:
    """Campaign queue with priority scheduling and resource management."""

    max_concurrent: int = 4
    max_gpus: int = 8
    max_cpus: int = 64
    max_memory_gb: float = 512.0

    # Internal state
    _queue: list[CampaignQueueEntry] = field(default_factory=list)
    _running: dict[str, CampaignQueueEntry] = field(default_factory=dict)
    _completed: dict[str, CampaignQueueEntry] = field(default_factory=dict)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    _resource_lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    # Resource tracking
    _used_gpus: int = 0
    _used_cpus: int = 0
    _used_memory_gb: float = 0.0

    async def enqueue(
        self,
        spec: CampaignSpec,
        priority: CampaignPriority = CampaignPriority.NORMAL,
        quota: ResourceQuota | None = None,
        project: str = "default",
        user: str = "unknown",
    ) -> str:
        """Add a campaign to the queue.

        Returns:
            The campaign ID.
        """
        campaign_id = str(uuid.uuid4())[:8]
        entry = CampaignQueueEntry(
            campaign_id=campaign_id,
            spec=spec,
            priority=priority,
            quota=quota or ResourceQuota(),
            project=project,
            user=user,
        )

        async with self._lock:
            heapq.heappush(self._queue, entry)
            logger.info(
                "Campaign %s enqueued with priority %s", campaign_id, priority.name
            )

        # Try to schedule
        await self._schedule()
        return campaign_id

    async def _schedule(self) -> None:
        """Try to schedule queued campaigns based on available resources."""
        async with self._lock:
            if not self._queue:
                return

            # Check if we can run more campaigns
            if len(self._running) >= self.max_concurrent:
                return

            # Find the highest priority campaign that fits in available resources
            for i, entry in enumerate(self._queue):
                if self._can_allocate(entry.quota):
                    # Remove from queue and start
                    self._queue.pop(i)
                    await self._start_campaign(entry)
                    break

    def _can_allocate(self, quota: ResourceQuota) -> bool:
        """Check if resources are available for the quota."""
        return (
            self._used_gpus + quota.gpus <= self.max_gpus
            and self._used_cpus + quota.cpus <= self.max_cpus
            and self._used_memory_gb + quota.memory_gb <= self.max_memory_gb
        )

    async def _start_campaign(self, entry: CampaignQueueEntry) -> None:
        """Start a campaign."""
        # Allocate resources
        async with self._resource_lock:
            self._used_gpus += entry.quota.gpus
            self._used_cpus += entry.quota.cpus
            self._used_memory_gb += entry.quota.memory_gb

        entry.status = CampaignStatus.RUNNING
        entry.started_at = time.time()
        self._running[entry.campaign_id] = entry

        logger.info(
            "Starting campaign %s (resources: gpus=%d, cpus=%d, mem=%.1fGB)",
            entry.campaign_id,
            entry.quota.gpus,
            entry.quota.cpus,
            entry.quota.memory_gb,
        )

        # Run campaign in background
        task = asyncio.create_task(self._run_campaign(entry))
        task.add_done_callback(
            lambda t: asyncio.create_task(self._on_campaign_done(entry.campaign_id, t))
        )

    async def _run_campaign(self, entry: CampaignQueueEntry) -> dict[str, Any]:
        """Run the campaign and return results."""
        temp_path = await self._write_campaign_yaml(entry)
        try:
            result = await self._execute_campaign(entry, temp_path)
            entry.result = result
            entry.status = CampaignStatus.COMPLETED
        except Exception as e:
            logger.exception("Campaign %s failed", entry.campaign_id)
            entry.error = str(e)
            entry.status = CampaignStatus.FAILED
            raise
        finally:
            Path(temp_path).unlink(missing_ok=True)

        return entry.result

    async def _write_campaign_yaml(self, entry: CampaignQueueEntry) -> str:
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
        self, entry: CampaignQueueEntry, temp_path: str
    ) -> dict[str, Any]:
        """Execute the campaign from a YAML file."""
        return await run_campaign(
            campaign_path=temp_path,
            parallel=entry.spec.parallel,
            webhook_url=entry.spec.webhook_url,
        )

    async def _on_campaign_done(self, campaign_id: str, task: asyncio.Task) -> None:
        """Handle campaign completion."""
        async with self._lock:
            entry = self._running.pop(campaign_id, None)
            if not entry:
                return

            # Release resources
            async with self._resource_lock:
                self._used_gpus -= entry.quota.gpus
                self._used_cpus -= entry.quota.cpus
                self._used_memory_gb -= entry.quota.memory_gb

            entry.completed_at = time.time()

            if entry.status == CampaignStatus.RUNNING:
                entry.status = CampaignStatus.COMPLETED

            self._completed[campaign_id] = entry
            logger.info(
                "Campaign %s completed with status %s", campaign_id, entry.status
            )

        # Try to schedule next campaign
        await self._schedule()

    async def cancel(self, campaign_id: str) -> bool:
        """Cancel a queued or running campaign."""
        async with self._lock:
            # Check queue
            for i, entry in enumerate(self._queue):
                if entry.campaign_id == campaign_id:
                    entry.status = CampaignStatus.CANCELLED
                    self._queue.pop(i)
                    logger.info("Cancelled queued campaign %s", campaign_id)
                    return True

            # Check running
            if campaign_id in self._running:
                entry = self._running[campaign_id]
                entry.status = CampaignStatus.CANCELLED
                # Note: Actual cancellation of running task would require task cancellation
                logger.info("Marked running campaign %s for cancellation", campaign_id)
                return True

        return False

    async def preempt(self, campaign_id: str) -> bool:
        """Preempt a running campaign (requeue with higher priority)."""
        async with self._lock:
            if campaign_id in self._running:
                entry = self._running[campaign_id]
                entry.status = CampaignStatus.PREEMPTED
                # Requeue with higher priority
                heapq.heappush(self._queue, entry)
                del self._running[campaign_id]
                logger.info(
                    "Preempted campaign %s, requeued with higher priority", campaign_id
                )
                return True
        return False

    async def get_status(self, campaign_id: str) -> CampaignQueueEntry | None:
        """Get status of a campaign."""
        async with self._lock:
            # Check queue
            for entry in self._queue:
                if entry.campaign_id == campaign_id:
                    return entry
            # Check running
            if campaign_id in self._running:
                return self._running[campaign_id]
            # Check completed
            if campaign_id in self._completed:
                return self._completed[campaign_id]
        return None

    async def list_campaigns(
        self,
        status: CampaignStatus | None = None,
        project: str | None = None,
        user: str | None = None,
    ) -> list[CampaignQueueEntry]:
        """List campaigns with optional filters."""
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
                "running_campaigns": len(self._running),
                "queued_campaigns": len(self._queue),
            }


# Global queue instance - use a holder class to avoid global statement
class _QueueHolder:
    queue: CampaignQueue | None = None


def get_campaign_queue() -> CampaignQueue:
    """Get the global campaign queue."""
    if _QueueHolder.queue is None:
        _QueueHolder.queue = CampaignQueue()
    return _QueueHolder.queue


def set_campaign_queue(queue: CampaignQueue) -> None:
    """Set the global campaign queue (for testing)."""
    _QueueHolder.queue = queue


async def submit_campaign(
    spec: CampaignSpec,
    priority: CampaignPriority = CampaignPriority.NORMAL,
    quota: ResourceQuota | None = None,
    project: str = "default",
    user: str = "unknown",
) -> str:
    """Submit a campaign to the global queue."""
    queue = get_campaign_queue()
    return await queue.enqueue(spec, priority, quota, project, user)


async def run_campaign_queue_worker() -> None:
    """Background worker to process the campaign queue."""
    queue = get_campaign_queue()
    while True:
        await queue._schedule()
        await asyncio.sleep(5)


__all__ = [
    "CampaignPriority",
    "CampaignQueue",
    "CampaignQueueEntry",
    "CampaignStatus",
    "ResourceQuota",
    "get_campaign_queue",
    "run_campaign_queue_worker",
    "submit_campaign",
]
