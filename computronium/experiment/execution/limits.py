"""Unified concurrency and resource limits derived from hardware."""

from __future__ import annotations

import os
from dataclasses import dataclass

try:
    import psutil
except ImportError:
    psutil = None

try:
    import torch
except ImportError:
    torch = None


@dataclass(frozen=True, slots=True)
class ExecutionLimits:
    """Unified execution limits for a run, campaign, or loop.

    All defaults are hardware-derived: no hardcoded literals in execution paths.

    Attributes:
        cell_workers: Max concurrent cells training (concurrency ceiling).
        cpu_threads_per_cell: Torch CPU threads per cell worker, or None for default.
        gpu_memory_fraction: Fraction of GPU memory per process, or None for default.
        queue_max_concurrent: Max concurrent runs in the queue.
        queue_max_gpus: Max GPUs the queue may allocate.
        queue_max_cpus: Max CPUs the queue may allocate.
        queue_max_memory_gb: Max memory (GB) the queue may allocate.
    """

    cell_workers: int
    cpu_threads_per_cell: int | None
    gpu_memory_fraction: float | None
    queue_max_concurrent: int
    queue_max_gpus: int
    queue_max_cpus: int
    queue_max_memory_gb: float

    @classmethod
    def from_cli(cls, **kwargs) -> ExecutionLimits:
        """Create limits from CLI overrides with hardware-derived defaults.

        Args:
            **kwargs: CLI overrides (cell_workers, cpu_threads, gpu_memory_fraction,
                     queue_max_concurrent, queue_max_gpus, queue_max_cpus, queue_max_memory_gb)

        Returns:
            ExecutionLimits with hardware-derived defaults and CLI overrides applied.
        """
        cpu_count = os.cpu_count() or 1
        gpu_count = torch.cuda.device_count() if torch else 0
        mem_gb = psutil.virtual_memory().total / (1024**3) if psutil else 1.0

        cell_workers = kwargs.get("cell_workers")
        queue_max_concurrent = kwargs.get("queue_max_concurrent")
        queue_max_gpus = kwargs.get("queue_max_gpus")
        queue_max_cpus = kwargs.get("queue_max_cpus")
        queue_max_memory_gb = kwargs.get("queue_max_memory_gb")

        return cls(
            cell_workers=cell_workers if cell_workers is not None else min(4, cpu_count),
            cpu_threads_per_cell=kwargs.get("cpu_threads_per_cell"),
            gpu_memory_fraction=kwargs.get("gpu_memory_fraction"),
            queue_max_concurrent=queue_max_concurrent if queue_max_concurrent is not None else min(4, cpu_count),
            queue_max_gpus=queue_max_gpus if queue_max_gpus is not None else max(1, gpu_count),
            queue_max_cpus=queue_max_cpus if queue_max_cpus is not None else cpu_count,
            queue_max_memory_gb=queue_max_memory_gb if queue_max_memory_gb is not None else mem_gb * 0.8,
        )

    def apply_torch_settings(self) -> None:
        """Apply CPU/GPU thread settings to the current process."""
        if self.cpu_threads_per_cell is not None and torch:
            torch.set_num_threads(self.cpu_threads_per_cell)
        if self.gpu_memory_fraction is not None and torch and torch.cuda.is_available():
            torch.cuda.set_per_process_memory_fraction(self.gpu_memory_fraction)

    def to_queue_config(self) -> dict[str, int | float]:
        """Convert to CampaignQueue resource limits."""
        return {
            "max_concurrent": self.queue_max_concurrent,
            "max_gpus": self.queue_max_gpus,
            "max_cpus": self.queue_max_cpus,
            "max_memory_gb": self.queue_max_memory_gb,
        }


__all__ = ["ExecutionLimits"]
