"""Seed Variability Analysis (Phase D5).

Analyzes variability across seeds: violin plots, confidence intervals,
and statistical significance of seed effects.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
from scipy import stats

if TYPE_CHECKING:
    from computronium.experiment.evidence.store import RecordStore


@dataclass(frozen=True, slots=True)
class SeedVariabilityResult:
    """Result of seed variability analysis."""

    metric: str
    axis: str | None  # Grouping axis
    groups: dict[
        str, dict[str, float]
    ]  # group -> {mean, std, ci_lower, ci_upper, n_seeds}
    overall_mean: float
    overall_std: float
    seed_effect_pvalue: float  # ANOVA p-value for seed effect
    coefficient_of_variation: float
    metadata: dict[str, Any]


@dataclass(frozen=True, slots=True)
class SeedVariabilityConfig:
    """Configuration for seed variability analysis."""

    min_seeds_per_group: int = 3
    confidence_level: float = 0.95
    group_by_axis: str | None = None


def compute_seed_variability(
    records: list[Any],
    metric: str,
    config: SeedVariabilityConfig | None = None,
) -> SeedVariabilityResult:
    """Compute seed variability statistics."""
    config = config or SeedVariabilityConfig()

    # Group by axis if specified
    groups = {}
    all_values = []

    if config.group_by_axis:
        axis = config.group_by_axis
        for r in records:
            group_val = getattr(r, axis)
            metric_val = r.payload.get(metric)
            if metric_val is not None:
                if group_val not in groups:
                    groups[group_val] = []
                groups[group_val].append(float(metric_val))
                all_values.append(float(metric_val))
    else:
        # No grouping - just collect all values
        for r in records:
            metric_val = r.payload.get(metric)
            if metric_val is not None:
                all_values.append(float(metric_val))
        groups["all"] = all_values

    # Filter groups with sufficient seeds
    filtered_groups = {
        k: v for k, v in groups.items() if len(v) >= config.min_seeds_per_group
    }

    # Compute statistics per group
    group_stats = {}
    for group_name, values in filtered_groups.items():
        n = len(values)
        mean = np.mean(values)
        std = np.std(values, ddof=1) if n > 1 else 0.0
        se = std / np.sqrt(n) if n > 0 else 0.0

        # Confidence interval
        alpha = 1 - config.confidence_level
        t_crit = stats.t.ppf(1 - alpha / 2, n - 1) if n > 1 else 1.96
        ci_lower = mean - t_crit * se
        ci_upper = mean + t_crit * se

        group_stats[group_name] = {
            "mean": float(mean),
            "std": float(std),
            "ci_lower": float(ci_lower),
            "ci_upper": float(ci_upper),
            "n_seeds": n,
            "values": values,
        }

    # Overall statistics
    if all_values:
        overall_mean = float(np.mean(all_values))
        overall_std = float(np.std(all_values, ddof=1)) if len(all_values) > 1 else 0.0
        cv = overall_std / overall_mean if overall_mean != 0 else float("inf")
    else:
        overall_mean = overall_std = cv = 0.0

    # ANOVA for seed effect (if multiple groups)
    seed_effect_pvalue = 1.0
    if len(filtered_groups) > 1:
        group_arrays = [np.array(v) for v in filtered_groups.values()]
        try:
            _f_stat, p_val = stats.f_oneway(*group_arrays)
            seed_effect_pvalue = float(p_val)
        except Exception:
            seed_effect_pvalue = 1.0

    return SeedVariabilityResult(
        metric=metric,
        axis=config.group_by_axis,
        groups=group_stats,
        overall_mean=overall_mean,
        overall_std=overall_std,
        seed_effect_pvalue=seed_effect_pvalue,
        coefficient_of_variation=cv,
        metadata={
            "n_records": len(records),
            "n_groups": len(filtered_groups),
            "min_seeds_per_group": config.min_seeds_per_group,
            "confidence_level": config.confidence_level,
        },
    )


def plot_violin_plots(
    result: SeedVariabilityResult,
    output_path: Path | str,
    title: str | None = None,
) -> Path:
    """Generate violin plot for seed variability."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 6))

    if not result.groups:
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return Path(output_path)

    # Prepare data for violin plot
    group_names = list(result.groups.keys())
    group_data = [result.groups[name]["values"] for name in group_names]

    parts = ax.violinplot(group_data, positions=range(len(group_names)), showmeans=True)
    for pc in parts["bodies"]:  # type: ignore[attr-defined]
        pc.set_facecolor("#4C72B0")
        pc.set_alpha(0.7)
    parts["cmeans"].set_color("red")

    ax.set_xticks(range(len(group_names)))
    ax.set_xticklabels(group_names, rotation=45, ha="right")
    ax.set_ylabel(result.metric)
    ax.set_title(title or f"Seed Variability: {result.metric}")
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_file, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return output_file


class SeedVariabilityAnalyzer:
    """Analyze seed variability from experiment records."""

    def __init__(
        self,
        store: RecordStore,
        run_id: str,
        config: SeedVariabilityConfig | None = None,
    ):
        self.store = store
        self.run_id = run_id
        self.config = config or SeedVariabilityConfig()

    def analyze(
        self,
        metric: str = "val_acc",
        group_by_axis: str | None = None,
    ) -> SeedVariabilityResult:
        """Run seed variability analysis."""
        from computronium.experiment.surface.report import ReportGenerator

        generator = ReportGenerator(self.store)
        records = generator._store.query_records(run_id=self.run_id)

        config = SeedVariabilityConfig(
            min_seeds_per_group=self.config.min_seeds_per_group,
            confidence_level=self.config.confidence_level,
            group_by_axis=group_by_axis or self.config.group_by_axis,
        )

        return compute_seed_variability(records, metric, config)

    def analyze_all_metrics(
        self,
        metrics: list[str] = [
            "val_acc",
            "energy_per_step",
            "walltime_total",
            "param_count",
        ],
    ) -> dict[str, SeedVariabilityResult]:
        """Analyze variability for multiple metrics."""
        results = {}
        for metric in metrics:
            results[metric] = self.analyze(metric)
        return results
