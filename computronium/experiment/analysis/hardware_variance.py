"""Hardware Variance Analysis (Phase D5).

Compares performance across different hardware: CPU vs GPU, different GPU architectures,
quantifies hardware-specific variance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import numpy as np
from scipy import stats

if TYPE_CHECKING:
    from computronium.experiment.evidence.store import RecordStore


@dataclass(frozen=True, slots=True)
class HardwareVarianceResult:
    """Result of hardware variance analysis."""

    metric: str
    devices: dict[str, dict[str, float]]  # device -> {mean, std, n, ci_lower, ci_upper}
    device_effect_pvalue: float  # ANOVA p-value for device effect
    pairwise_comparisons: dict[str, float]  # device pair -> p-value
    metadata: dict[str, Any]


@dataclass(frozen=True, slots=True)
class HardwareVarianceConfig:
    """Configuration for hardware variance analysis."""

    min_seeds_per_device: int = 3
    confidence_level: float = 0.95


def compare_hardware_performance(
    records_by_device: dict[str, list[Any]],
    metric: str,
    config: HardwareVarianceConfig | None = None,
) -> HardwareVarianceResult:
    """Compare performance across different hardware devices."""
    config = config or HardwareVarianceConfig()

    device_stats = {}
    device_arrays = {}

    for device, records in records_by_device.items():
        values = []
        for r in records:
            val = r.payload.get(metric)
            if val is not None:
                values.append(float(val))

        if len(values) >= config.min_seeds_per_device:
            n = len(values)
            mean = np.mean(values)
            std = np.std(values, ddof=1) if n > 1 else 0.0
            se = std / np.sqrt(n) if n > 0 else 0.0

            alpha = 1 - config.confidence_level
            t_crit = stats.t.ppf(1 - alpha / 2, n - 1) if n > 1 else 1.96
            ci_lower = mean - t_crit * se
            ci_upper = mean + t_crit * se

            device_stats[device] = {
                "mean": float(mean),
                "std": float(std),
                "n": n,
                "ci_lower": float(ci_lower),
                "ci_upper": float(ci_upper),
            }
            device_arrays[device] = np.array(values)

    # ANOVA for device effect
    device_effect_pvalue = 1.0
    if len(device_arrays) > 1:
        arrays = list(device_arrays.values())
        try:
            _f_stat, p_val = stats.f_oneway(*arrays)
            device_effect_pvalue = float(p_val)
        except Exception:
            device_effect_pvalue = 1.0

    # Pairwise comparisons (t-tests with Bonferroni correction)
    pairwise = {}
    device_list: list[str] = list(device_arrays.keys())
    n_devices = len(device_list)
    for i, d1 in enumerate(device_list):
        for d2 in device_list[i + 1 :]:
            try:
                _t_stat, p_val = stats.ttest_ind(device_arrays[d1], device_arrays[d2])
                # Bonferroni correction
                n_comparisons = n_devices * (n_devices - 1) / 2
                corrected_p = min(1.0, p_val * float(n_comparisons))  # type: ignore[operator]
                pairwise[f"{d1}_vs_{d2}"] = float(corrected_p)
            except Exception:
                pairwise[f"{d1}_vs_{d2}"] = 1.0

    return HardwareVarianceResult(
        metric=metric,
        devices=device_stats,
        device_effect_pvalue=device_effect_pvalue,
        pairwise_comparisons=pairwise,
        metadata={
            "n_devices": len(device_arrays),
            "min_seeds_per_device": config.min_seeds_per_device,
        },
    )


class HardwareVarianceAnalyzer:
    """Analyze hardware variance from experiment records."""

    def __init__(
        self,
        store: RecordStore,
        config: HardwareVarianceConfig | None = None,
    ):
        self.store = store
        self.config = config or HardwareVarianceConfig()

    def analyze_from_runs(
        self,
        run_ids: list[str],
        metric: str = "val_acc",
        device_field: str = "device",
    ) -> HardwareVarianceResult:
        """Analyze hardware variance across multiple runs."""
        from computronium.experiment.surface.report import ReportGenerator

        records_by_device: dict[str, list[Any]] = {}

        for run_id in run_ids:
            generator = ReportGenerator(self.store)
            records = generator._store.query_records(run_id=run_id)

            for r in records:
                device = getattr(r, device_field, "unknown")
                if device not in records_by_device:
                    records_by_device[device] = []
                records_by_device[device].append(r)

        return compare_hardware_performance(records_by_device, metric, self.config)
