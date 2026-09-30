"""Run-scoped system context (R75/K10).

Provides run-scoped kernel cache keyed by (run_id, cell_key, device, dtype),
device/dtype context, and injected learning state. The legacy global kernel
cache never enters the kernel — all state is run-scoped and context-injected.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from computronium.experiment.learning.icu import ICUModel
    from computronium.experiment.learning.reasoning import ReasoningStore

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class DeviceContext:
    """Device and dtype context for a run."""

    device: str  # e.g., "cuda:0", "cpu"
    dtype: str  # e.g., "float32", "float16", "bfloat16"
    compile_mode: str | None = None  # e.g., "reduce-overhead", "max-autotune"


@dataclass(slots=True)
class KernelCacheEntry:
    """Entry in the run-scoped kernel cache."""

    run_id: str
    cell_key: str
    device: str
    dtype: str
    kernel: Any  # Compiled kernel object
    timestamp: float
    hit_count: int = 0


@dataclass(slots=True)
class SystemContext:
    """Run-scoped system context carrying all mutable state for a run.

    This replaces module-level singletons (K10). All state is keyed by run_id
    and injected through the pipeline context.
    """

    run_id: str
    device_context: DeviceContext
    # Run-scoped kernel cache: (cell_key, device, dtype) -> KernelCacheEntry
    _kernel_cache: dict[tuple[str, str, str], KernelCacheEntry] = field(
        default_factory=dict
    )
    _cache_lock: threading.Lock = field(default_factory=threading.Lock)

    # Injected learning state (no module-level singletons)
    icu_model: ICUModel | None = None
    reasoning_store: ReasoningStore | None = None

    # Evidence-driven allocator state
    allocator_state: dict[str, Any] | None = None

    # Kernel-ladder evidence (parity/microbench, git-SHA tagged)
    kernel_ladder_evidence: list[dict[str, Any]] = field(default_factory=list)

    def get_kernel(
        self, cell_key: str, device: str | None = None, dtype: str | None = None
    ) -> Any | None:
        """Get a cached kernel for the given cell and device/dtype."""
        dev = device or self.device_context.device
        dt = dtype or self.device_context.dtype
        key = (cell_key, dev, dt)

        with self._cache_lock:
            entry = self._kernel_cache.get(key)
            if entry is not None:
                entry.hit_count += 1
                return entry.kernel
        return None

    def set_kernel(
        self,
        cell_key: str,
        kernel: Any,
        device: str | None = None,
        dtype: str | None = None,
    ) -> None:
        """Cache a kernel for the given cell and device/dtype."""
        dev = device or self.device_context.device
        dt = dtype or self.device_context.dtype
        key = (cell_key, dev, dt)

        import time

        with self._cache_lock:
            self._kernel_cache[key] = KernelCacheEntry(
                run_id=self.run_id,
                cell_key=cell_key,
                device=dev,
                dtype=dt,
                kernel=kernel,
                timestamp=time.monotonic(),
            )

    def record_kernel_ladder_evidence(
        self,
        kernel_name: str,
        parity_result: dict[str, Any],
        git_sha: str,
        microbench_result: dict[str, Any] | None = None,
    ) -> None:
        """Record kernel-ladder evidence for auditability."""
        self.kernel_ladder_evidence.append({
            "kernel_name": kernel_name,
            "parity": parity_result,
            "microbench": microbench_result,
            "git_sha": git_sha,
            "timestamp": time.monotonic(),
        })

    def get_kernel_cache_stats(self) -> dict[str, Any]:
        """Get kernel cache statistics."""
        with self._cache_lock:
            total_entries = len(self._kernel_cache)
            total_hits = sum(e.hit_count for e in self._kernel_cache.values())
            return {
                "total_entries": total_entries,
                "total_hits": total_hits,
                "entries": [
                    {
                        "cell_key": e.cell_key[:16],
                        "device": e.device,
                        "dtype": e.dtype,
                        "hit_count": e.hit_count,
                    }
                    for e in self._kernel_cache.values()
                ],
            }


def create_system_context(
    run_id: str,
    device: str = "cuda:0",
    dtype: str = "float32",
    compile_mode: str | None = None,
    icu_model: Any | None = None,
    reasoning_store: Any | None = None,
) -> SystemContext:
    """Factory function to create a SystemContext for a run."""
    device_ctx = DeviceContext(device=device, dtype=dtype, compile_mode=compile_mode)
    return SystemContext(
        run_id=run_id,
        device_context=device_ctx,
        icu_model=icu_model,
        reasoning_store=reasoning_store,
    )


__all__ = [
    "DeviceContext",
    "KernelCacheEntry",
    "SystemContext",
    "create_system_context",
]
