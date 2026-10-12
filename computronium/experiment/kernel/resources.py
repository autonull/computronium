"""Resource tracking and budgeting for experiment execution (Kernel).

Combines budget management, cost modeling, and resource tracking
(GPU-hours, energy, carbon, cloud cost estimates).
"""

from __future__ import annotations

import json
import logging
import re
import threading
import time
from dataclasses import asdict, dataclass, field, replace
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from computronium.experiment.schema.record import Record

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


@runtime_checkable
class CostModel(Protocol):
    """Protocol for cost estimation models.

    Implementations estimate the computational cost of executing an
    experiment cell, enabling budget-aware allocation policies.
    """

    def estimate_cost(
        self,
        coordinate: tuple[str, str, str, str, str, str, dict],
        schedule: dict[str, int | str | float | None],
    ) -> float:
        """Estimate cost in abstract units (e.g., GPU-seconds).

        Args:
            coordinate: 6-axis coordinate (substrate, geometry, dynamics,
                plasticity, credit, update, params)
            schedule: Execution schedule (fidelity, seed, n_seeds, epochs,
                batch_limit, budget_id)

        Returns:
            Estimated cost in cost units.
        """
        ...

    def actual_cost(self, record: Record) -> float:
        """Compute actual cost from a completed record.

        Args:
            record: Completed experiment record.

        Returns:
            Actual cost incurred.
        """
        ...


@dataclass(frozen=True, slots=True)
class Budget:
    """Execution budget with time and cell limits.

    Frozen value object: ``advance``/``advance_by`` return fresh instances.
    ``target_cells`` is a hard cap on completed cells; ``soft_seconds`` stops
    *starting* new cells past the anchor; ``hard_seconds`` is the stricter
    between-cells ceiling for loop drivers.
    """

    started_at: float  # time.monotonic() anchor
    soft_seconds: float | None = None
    hard_seconds: float | None = None
    target_cells: int | None = None
    target_cost: float | None = None
    done: int = 0
    cost_consumed: float = 0.0

    @classmethod
    def from_duration(
        cls,
        duration: str,
        *,
        target_cells: int | None = None,
        target_cost: float | None = None,
        started_at: float | None = None,
    ) -> Budget:
        """Parse duration string into a Budget.

        Args:
            duration: Duration string like "5m", "90s", "1h", "3600"
            target_cells: Optional hard cap on completed cells
            target_cost: Optional hard cap on total cost
            started_at: Optional monotonic time anchor (default: now)

        Returns:
            Budget instance.
        """
        DURATION_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*([smh]?)\s*$", re.IGNORECASE)
        DURATION_SCALES: dict[str, float] = {"": 1.0, "s": 1.0, "m": 60.0, "h": 3600.0}

        match = DURATION_RE.match(duration)
        if match is None:
            raise ValueError(
                f"invalid budget {duration!r}: expected '<n><s|m|h>' (e.g. 5m, 90s, 1h)"
            )
        seconds = float(match.group(1)) * DURATION_SCALES[match.group(2).lower()]
        return cls(
            started_at=time.monotonic() if started_at is None else started_at,
            soft_seconds=seconds,
            hard_seconds=seconds,
            target_cells=target_cells,
            target_cost=target_cost,
        )

    def soft_expired(self, now: float | None = None) -> bool:
        """Check if soft time limit has expired."""
        now = time.monotonic() if now is None else now
        return (
            self.soft_seconds is not None and now - self.started_at >= self.soft_seconds
        )

    def hard_expired(self, now: float | None = None) -> bool:
        """Check if hard time limit has expired."""
        now = time.monotonic() if now is None else now
        return (
            self.hard_seconds is not None and now - self.started_at >= self.hard_seconds
        )

    def target_reached(self) -> bool:
        """Check if cell target has been reached."""
        return (self.target_cells is not None and self.done >= self.target_cells) or (
            self.target_cost is not None and self.cost_consumed >= self.target_cost
        )

    def expired(self, now: float | None = None) -> bool:
        """Check if budget is exhausted (hard limit or target reached)."""
        return self.hard_expired(now) or self.target_reached()

    def advance(self) -> Budget:
        """Return new Budget with done incremented by 1."""
        return self.advance_by(1)

    def advance_by(self, n: int) -> Budget:
        """Return new Budget with done incremented by n."""
        return replace(self, done=self.done + n)

    def add_cost(self, cost: float) -> Budget:
        """Return new Budget with cost_consumed increased."""
        return replace(self, cost_consumed=self.cost_consumed + cost)

    def elapsed_seconds(self, now: float | None = None) -> float:
        """Return elapsed time in seconds."""
        now = time.monotonic() if now is None else now
        return now - self.started_at

    def remaining_seconds(self, now: float | None = None) -> float | None:
        """Return remaining soft seconds, or None if unlimited."""
        if self.soft_seconds is None:
            return None
        remaining = self.soft_seconds - self.elapsed_seconds(now)
        return max(0.0, remaining)


@dataclass(frozen=True, slots=True)
class SimpleCostModel:
    """Simple cost model based on schedule parameters.

    Estimates cost proportional to epochs * n_seeds * batch_factor.
    """

    base_cost_per_epoch: float = 1.0
    seed_multiplier: float = 1.0
    fidelity_multipliers: dict[str, float] | None = None

    def __post_init__(self) -> None:
        if self.fidelity_multipliers is None:
            object.__setattr__(
                self,
                "fidelity_multipliers",
                {"L0": 0.1, "L1": 0.5, "L2": 1.0},
            )

    def estimate_cost(
        self,
        coordinate: tuple[str, str, str, str, str, str, dict],
        schedule: dict[str, int | str | float | None],
    ) -> float:
        """Estimate cost based on schedule parameters."""
        epochs = int(schedule.get("epochs", 1) or 1)
        n_seeds = int(schedule.get("n_seeds", 1) or 1)
        fidelity = str(schedule.get("fidelity", "L1") or "L1")

        base = self.base_cost_per_epoch * epochs
        seed_factor = n_seeds * self.seed_multiplier
        multipliers = self.fidelity_multipliers or {"L0": 0.1, "L1": 0.5, "L2": 1.0}
        fidelity_factor = multipliers.get(fidelity, 1.0)

        return base * seed_factor * fidelity_factor

    def actual_cost(self, record: Record) -> float:
        """Compute actual cost from record payload (walltime)."""
        walltime = record.payload.get("walltime_s")
        if isinstance(walltime, (int, float)):
            return float(walltime)
        return self.estimate_cost(
            (
                record.substrate,
                record.geometry,
                record.dynamics,
                record.plasticity,
                record.credit,
                record.update,
                record.params,
            ),
            record.schedule.to_dict(),
        )


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


class CostTracker:
    """Tracks resource usage and costs for a campaign or run."""

    def __init__(
        self,
        campaign_id: str,
        region: str = "global_average",
        gpu_type: str | None = None,
    ) -> None:
        self.campaign_id = campaign_id
        self.region = region
        self.gpu_type = gpu_type
        self._start_time = time.time()
        self._lock = threading.Lock()
        self._usage = ResourceUsage()
        self._gpu_samples: list[tuple[float, float]] = []
        self._nvml_available: bool = False
        self._nvml_handle: Any = None
        self._init_nvml()
        if self.gpu_type is None:
            self.gpu_type = self._detect_gpu_type()

    def _init_nvml(self) -> None:
        """Initialize NVML for energy tracking."""
        try:
            import pynvml

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
            return power_mw / 1000.0
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

    def stop(self) -> ResourceUsage:
        """Stop tracking and return final usage."""
        with self._lock:
            elapsed = time.time() - self._start_time
            gpu_hours = elapsed / 3600.0 * max(self._usage.gpu_count, 1)
            cpu_hours = elapsed / 3600.0

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
    "Budget",
    "CostModel",
    "SimpleCostModel",
    "ResourceUsage",
    "CostTracker",
    "CampaignCostTracker",
    "estimate_campaign_cost",
    "CARBON_INTENSITY",
    "GPU_POWER_WATTS",
    "GPU_PRICING_USD_PER_HOUR",
]
