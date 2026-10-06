"""Runtime provenance snapshot and system context (WP19).

Captures the actual runtime environment once per run for reproducible provenance.
Replaces hardcoded values in pipeline provenance construction.

SystemContext carries run-scoped kernel cache and injected learning state (R75/K10).
"""

from __future__ import annotations

import platform
import sys
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from computronium.experiment.learning.icu import ICUModel
    from computronium.experiment.learning.reasoning import ReasoningStore


@dataclass(frozen=True, slots=True)
class EnvironmentSnapshot:
    """Immutable snapshot of the runtime environment captured once per run.

    Provides actual runtime provenance instead of hardcoded values.
    Referenced by records for reproducibility.
    """

    python_version: str
    python_implementation: str
    platform: str
    platform_version: str
    architecture: str
    pytorch_version: str
    cuda_version: str | None
    gpu_devices: list[str]
    dtype: str
    worker_config: dict[str, Any]
    code_sha: str
    relevant_deps: dict[str, str]
    captured_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_provenance_dict(self) -> dict[str, Any]:
        """Convert to provenance-compatible dictionary."""
        return {
            "python_version": self.python_version,
            "python_implementation": self.python_implementation,
            "platform": self.platform,
            "platform_version": self.platform_version,
            "architecture": self.architecture,
            "pytorch_version": self.pytorch_version,
            "cuda_version": self.cuda_version,
            "gpu_devices": self.gpu_devices,
            "dtype": self.dtype,
            "worker_config": self.worker_config,
            "code_sha": self.code_sha,
            "relevant_deps": self.relevant_deps,
            "captured_at": self.captured_at,
        }


def capture_environment_snapshot(
    *,
    dtype: str = "float32",
    worker_config: dict[str, Any] | None = None,
    code_sha: str = "unknown",
) -> EnvironmentSnapshot:
    """Capture the current runtime environment.

    Args:
        dtype: Default tensor dtype
        worker_config: Worker configuration dict
        code_sha: Git commit SHA of the running code

    Returns:
        EnvironmentSnapshot with actual runtime information.
    """
    # Python info
    python_version = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    python_implementation = platform.python_implementation()

    # Platform info
    platform_name = platform.system().lower()
    platform_version = platform.release()
    architecture = platform.machine()

    # PyTorch info
    try:  # ruff: ignore[too-many-statements-in-try-clause]
        import torch

        pytorch_version = torch.__version__
        cuda_version = torch.version.cuda if torch.cuda.is_available() else None
        gpu_devices = []
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                gpu_devices.append(torch.cuda.get_device_name(i))
    except ImportError:
        pytorch_version = "not_installed"
        cuda_version = None
        gpu_devices = []

    # Relevant dependencies
    relevant_deps = {}
    for pkg in ["numpy", "optuna", "scipy", "duckdb", "hypothesis", "pytest"]:
        try:
            module = __import__(pkg)
            relevant_deps[pkg] = getattr(module, "__version__", "unknown")
        except ImportError:
            relevant_deps[pkg] = "not_installed"

    return EnvironmentSnapshot(
        python_version=python_version,
        python_implementation=python_implementation,
        platform=platform_name,
        platform_version=platform_version,
        architecture=architecture,
        pytorch_version=pytorch_version,
        cuda_version=cuda_version,
        gpu_devices=gpu_devices,
        dtype=dtype,
        worker_config=worker_config or {},
        code_sha=code_sha,
        relevant_deps=relevant_deps,
    )


# =============================================================================
# SystemContext (R75/K10) - Run-scoped kernel state
# =============================================================================


@dataclass(slots=True)
class SystemContext:
    """Run-scoped kernel context carrying cache and injected learning state.

    Replaces module-level singletons with explicit injection (K10).
    Keyed by (run_id, cell_key, device, dtype) for kernel-ladder evidence.
    """

    run_id: str
    environment: EnvironmentSnapshot
    kernel_cache: dict[tuple[str, str, str, str], Any] = field(default_factory=dict)
    icu_model: ICUModel | None = None
    reasoning_store: ReasoningStore | None = None
    _cache_lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def get_kernel_cache(self, cell_key: str, device: str, dtype: str) -> Any | None:
        """Get cached kernel for a cell/device/dtype combination."""
        key = (self.run_id, cell_key, device, dtype)
        with self._cache_lock:
            return self.kernel_cache.get(key)

    def set_kernel_cache(
        self, cell_key: str, device: str, dtype: str, kernel: Any
    ) -> None:
        """Cache a kernel for a cell/device/dtype combination."""
        key = (self.run_id, cell_key, device, dtype)
        with self._cache_lock:
            self.kernel_cache[key] = kernel

    def record_kernel_evidence(
        self, cell_key: str, device: str, dtype: str, evidence: dict[str, Any]
    ) -> None:
        """Record kernel-ladder evidence (parity/microbench, git-SHA tagged)."""
        # In a full implementation, this would persist to the store
        # For now, we just log it
        logger = __import__("logging").getLogger(__name__)
        logger.debug(
            "Kernel evidence for %s/%s/%s: %s", cell_key, device, dtype, evidence
        )


__all__ = [
    "EnvironmentSnapshot",
    "SystemContext",
    "capture_environment_snapshot",
]
