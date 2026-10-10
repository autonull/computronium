"""Cost Tracking: GPU-hours, Energy (J), Carbon Estimates.

Tracks resource consumption for experiment campaigns:
- GPU-hours (per GPU type)
- Energy consumption (Joules via NVML)
- Carbon estimates (based on grid intensity)
- Cost estimates (cloud pricing)
"""

from __future__ import annotations

import json
import logging
import threading
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


# Carbon intensity by region (gCO2/kWh) - approximate values
CARBON_INTENSITY = {
    "global_average": 475,
    "us": 380,
    "eu": 230,
    "cn": 550,
    "aws_us_east_1": 350,
    "aws_eu_west_1": 180,
    "gcp_us_central1": 350,
    "gcp_europe_west1": 150,
    "azure_eastus": 350,
    "azure_westeurope": 180,
}


# GPU power consumption (Watts) - typical max values
GPU_POWER_WATTS = {
    "A100": 400,
    "A100_80GB": 400,
    "H100": 700,
    "V100": 300,
    "T4": 70,
    "RTX_3090": 350,
    "RTX_4090": 450,
    "RTX_A6000": 300,
    "default": 250,
}


# Cloud GPU pricing (USD/hour) - approximate on-demand prices
GPU_PRICING_USD_PER_HOUR = {
    "A100": 3.50,
    "A100_80GB": 4.50,
    "H100": 8.00,
    "V100": 2.50,
    "T4": 0.50,
    "RTX_3090": 1.00,
    "RTX_4090": 1.50,
    "RTX_A6000": 2.00,
    "default": 1.00,
}


@dataclass(frozen=True, slots=True)
class ResourceUsage:
    """Resource usage for a single component."""

    gpu_type: str = "unknown"
    gpu_count: int = 0
    gpu_hours: float = 0.0
    cpu_hours: float = 0.0
    memory_gb_hours: float = 0.0
    energy_joules: float = 0.0
    carbon_gco2: float = 0.0
    cost_usd: float = 0.0

    def __add__(self, other: ResourceUsage) -> ResourceUsage:
        return ResourceUsage(
            gpu_type=self.gpu_type if self.gpu_count > 0 else other.gpu_type,
            gpu_count=max(self.gpu_count, other.gpu_count),
            gpu_hours=self.gpu_hours + other.gpu_hours,
            cpu_hours=self.cpu_hours + other.cpu_hours,
            memory_gb_hours=self.memory_gb_hours + other.memory_gb_hours,
            energy_joules=self.energy_joules + other.energy_joules,
            carbon_gco2=self.carbon_gco2 + other.carbon_gco2,
            cost_usd=self.cost_usd + other.cost_usd,
        )


@dataclass
class CostTracker:
    """Tracks resource usage and costs for a campaign or run."""

    campaign_id: str
    region: str = "global_average"
    gpu_type: str | None = None  # Auto-detect if None
    _start_time: float = field(default_factory=time.time, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)
    _usage: ResourceUsage = field(default_factory=ResourceUsage, init=False)
    _gpu_samples: list[tuple[float, float]] = field(
        default_factory=list, init=False
    )  # (timestamp, watts)
    _nvml_available: bool = field(default=False, init=False)
    _nvml_handle: Any = field(default=None, init=False)

    def __post_init__(self) -> None:
        self._init_nvml()
        if self.gpu_type is None:
            self.gpu_type = self._detect_gpu_type()

    def _init_nvml(self) -> None:
        """Initialize NVML for energy tracking."""
        import pynvml  # ruff: ignore[import-outside-toplevel]

        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            if device_count > 0:
                self._nvml_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                self._nvml_available = True
                logger.debug("NVML initialized for energy tracking")
        except Exception:
            logger.debug("NVML not available for energy tracking")
            self._nvml_available = False

    def _detect_gpu_type(self) -> str:
        """Auto-detect GPU type."""
        try:
            import torch

            if torch.cuda.is_available():
                name = torch.cuda.get_device_name(0)
                for known in GPU_POWER_WATTS:
                    if known.lower() in name.lower():
                        return known
                return "default"
        except Exception as e:
            logger.debug("GPU detection failed: %s", e)
        return "default"

    def _get_gpu_type(self) -> str:
        """Get GPU type with fallback."""
        return self.gpu_type or "default"

    def _sample_power(self) -> float:
        """Sample current GPU power in watts."""
        if not self._nvml_available or self._nvml_handle is None:
            return GPU_POWER_WATTS.get(self._get_gpu_type(), GPU_POWER_WATTS["default"])

        try:
            import pynvml

            power_mw = pynvml.nvmlDeviceGetPowerUsage(self._nvml_handle)
            return power_mw / 1000.0  # Convert mW to W
        except Exception:
            return GPU_POWER_WATTS.get(self._get_gpu_type(), GPU_POWER_WATTS["default"])

    def start(self) -> None:
        """Start tracking."""
        with self._lock:
            self._start_time = time.time()
            self._gpu_samples.clear()

    def sample(self) -> None:
        """Record a power sample."""
        if not self._nvml_available:
            return
        with self._lock:
            watts = self._sample_power()
            self._gpu_samples.append((time.time(), watts))

    def stop(self) -> ResourceUsage:  # ruff: ignore[too-many-locals]
        """Stop tracking and return final usage."""
        with self._lock:
            elapsed = time.time() - self._start_time
            gpu_hours = elapsed / 3600.0 * max(self._usage.gpu_count, 1)
            cpu_hours = elapsed / 3600.0

            # Calculate energy from samples
            energy_joules = 0.0
            if self._gpu_samples:
                for i in range(1, len(self._gpu_samples)):
                    t1, w1 = self._gpu_samples[i - 1]
                    t2, w2 = self._gpu_samples[i]
                    dt = t2 - t1
                    avg_w = (w1 + w2) / 2
                    energy_joules += avg_w * dt
            else:
                # Estimate from GPU power rating
                watts = GPU_POWER_WATTS.get(
                    self._get_gpu_type(), GPU_POWER_WATTS["default"]
                )
                energy_joules = watts * elapsed * max(self._usage.gpu_count, 1)

            # Carbon estimate
            kwh = energy_joules / 3_600_000
            carbon_intensity = CARBON_INTENSITY.get(
                self.region, CARBON_INTENSITY["global_average"]
            )
            carbon_gco2 = kwh * carbon_intensity

            # Cost estimate
            price = GPU_PRICING_USD_PER_HOUR.get(
                self._get_gpu_type(), GPU_PRICING_USD_PER_HOUR["default"]
            )
            cost_usd = gpu_hours * price

            self._usage = ResourceUsage(
                gpu_type=self.gpu_type or "unknown",
                gpu_count=self._usage.gpu_count,
                gpu_hours=gpu_hours,
                cpu_hours=cpu_hours,
                memory_gb_hours=self._usage.memory_gb_hours,
                energy_joules=energy_joules,
                carbon_gco2=carbon_gco2,
                cost_usd=cost_usd,
            )

        return self._usage

    def set_gpu_count(self, count: int) -> None:
        """Set the number of GPUs being used."""
        with self._lock:
            self._usage = ResourceUsage(
                gpu_type=self._usage.gpu_type,
                gpu_count=count,
                gpu_hours=self._usage.gpu_hours,
                cpu_hours=self._usage.cpu_hours,
                memory_gb_hours=self._usage.memory_gb_hours,
                energy_joules=self._usage.energy_joules,
                carbon_gco2=self._usage.carbon_gco2,
                cost_usd=self._usage.cost_usd,
            )

    def add_memory_usage(self, gb_hours: float) -> None:
        """Add memory usage."""
        with self._lock:
            self._usage = ResourceUsage(
                gpu_type=self._usage.gpu_type,
                gpu_count=self._usage.gpu_count,
                gpu_hours=self._usage.gpu_hours,
                cpu_hours=self._usage.cpu_hours,
                memory_gb_hours=self._usage.memory_gb_hours + gb_hours,
                energy_joules=self._usage.energy_joules,
                carbon_gco2=self._usage.carbon_gco2,
                cost_usd=self._usage.cost_usd,
            )

    def get_usage(self) -> ResourceUsage:
        """Get current usage estimate (without stopping)."""
        with self._lock:
            elapsed = time.time() - self._start_time
            gpu_hours = elapsed / 3600.0 * max(self._usage.gpu_count, 1)

            energy_joules = 0.0
            if self._gpu_samples:
                for i in range(1, len(self._gpu_samples)):
                    t1, w1 = self._gpu_samples[i - 1]
                    t2, w2 = self._gpu_samples[i]
                    dt = t2 - t1
                    avg_w = (w1 + w2) / 2
                    energy_joules += avg_w * dt
            else:
                watts = GPU_POWER_WATTS.get(
                    self._get_gpu_type(), GPU_POWER_WATTS["default"]
                )
                energy_joules = watts * elapsed * max(self._usage.gpu_count, 1)

            kwh = energy_joules / 3_600_000
            carbon_intensity = CARBON_INTENSITY.get(
                self.region, CARBON_INTENSITY["global_average"]
            )
            carbon_gco2 = kwh * carbon_intensity

            price = GPU_PRICING_USD_PER_HOUR.get(
                self._get_gpu_type(), GPU_PRICING_USD_PER_HOUR["default"]
            )
            cost_usd = gpu_hours * price

            return ResourceUsage(
                gpu_type=self._usage.gpu_type,
                gpu_count=self._usage.gpu_count,
                gpu_hours=gpu_hours,
                cpu_hours=elapsed / 3600.0,
                memory_gb_hours=self._usage.memory_gb_hours,
                energy_joules=energy_joules,
                carbon_gco2=carbon_gco2,
                cost_usd=cost_usd,
            )


class CampaignCostTracker:
    """Aggregates cost tracking across multiple runs in a campaign."""

    def __init__(self, campaign_id: str, region: str = "global_average") -> None:
        self.campaign_id = campaign_id
        self.region = region
        self._run_trackers: dict[str, CostTracker] = {}
        self._lock = threading.Lock()

    def start_run(
        self, run_id: str, gpu_type: str | None = None, gpu_count: int = 1
    ) -> CostTracker:
        """Start tracking a run."""
        tracker = CostTracker(
            campaign_id=self.campaign_id, region=self.region, gpu_type=gpu_type
        )
        tracker.set_gpu_count(gpu_count)
        tracker.start()
        with self._lock:
            self._run_trackers[run_id] = tracker
        return tracker

    def sample_run(self, run_id: str) -> None:
        """Sample power for a run."""
        with self._lock:
            tracker = self._run_trackers.get(run_id)
        if tracker:
            tracker.sample()

    def stop_run(self, run_id: str) -> ResourceUsage | None:
        """Stop tracking a run and return its usage."""
        with self._lock:
            tracker = self._run_trackers.pop(run_id, None)
        if tracker:
            return tracker.stop()
        return None

    def get_total_usage(self) -> ResourceUsage:
        """Get total usage across all runs."""
        total = ResourceUsage()
        with self._lock:
            for tracker in self._run_trackers.values():
                usage = tracker.get_usage()
                total += usage
            # Note: completed runs are popped, so this only gets running ones
        return total

    def export_json(self, path: Path) -> None:
        """Export cost data to JSON."""
        with self._lock:
            data = {
                "campaign_id": self.campaign_id,
                "region": self.region,
                "total_usage": asdict(self.get_total_usage()),
                "runs": {
                    run_id: asdict(tracker.get_usage())
                    for run_id, tracker in self._run_trackers.items()
                },
                "exported_at": datetime.now().isoformat(),
            }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def estimate_campaign_cost(
    gpu_type: str,
    gpu_count: int,
    estimated_hours: float,
    region: str = "global_average",
) -> dict[str, float]:
    """Estimate cost for a planned campaign."""
    price = GPU_PRICING_USD_PER_HOUR.get(gpu_type, GPU_PRICING_USD_PER_HOUR["default"])
    watts = GPU_POWER_WATTS.get(gpu_type, GPU_POWER_WATTS["default"])

    gpu_hours = estimated_hours * gpu_count
    cost_usd = gpu_hours * price

    energy_joules = watts * estimated_hours * 3600 * gpu_count
    kwh = energy_joules / 3_600_000
    carbon_intensity = CARBON_INTENSITY.get(region, CARBON_INTENSITY["global_average"])
    carbon_gco2 = kwh * carbon_intensity

    return {
        "gpu_hours": gpu_hours,
        "energy_kwh": kwh,
        "carbon_kgco2": carbon_gco2 / 1000,
        "cost_usd": cost_usd,
    }


__all__ = [
    "CARBON_INTENSITY",
    "GPU_POWER_WATTS",
    "GPU_PRICING_USD_PER_HOUR",
    "CampaignCostTracker",
    "CostTracker",
    "ResourceUsage",
    "estimate_campaign_cost",
]
