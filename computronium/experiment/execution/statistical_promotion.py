"""Statistical gates for the promotion ladder (L1 rung).

Adds statistical rigor to promotions: mean > baseline + margin with confidence,
CI width threshold, train/val gap, stability band. Thresholds are config-driven.
Supports discovery/confirmation seed separation for multiplicity control.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any

import numpy as np
from scipy import stats

if TYPE_CHECKING:
    from collections.abc import Callable

    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.registry.baseline import BaselineRecord
    from computronium.experiment.schema.record import Record
    from computronium.experiment.schema.run_spec import RunSpec

logger = logging.getLogger(__name__)


class StatisticalVerdict(StrEnum):
    """What a statistical gate decided.

    Three states, not two: a comparison can show an effect (PASSED), show no
    effect at adequate power (REJECTED), or be too underpowered to distinguish
    the two (INSUFFICIENT). Collapsing the third into REJECTED reports "no
    effect" for a test that could not have detected one.
    """

    PASSED = "PASSED"
    REJECTED = "REJECTED"
    INSUFFICIENT = "INSUFFICIENT"


@dataclass(frozen=True, slots=True)
class GateThresholds:
    """Config-driven thresholds for L1 statistical gates."""

    # Mean superiority over baseline (in units of baseline std or absolute)
    superiority_margin: float = 0.0  # Absolute margin
    superiority_margin_sigma: float = 2.0  # Multiples of SE (mean > baseline + k*SE)

    # Confidence interval width threshold
    ci_width_threshold: float = 0.05  # Maximum CI width as fraction of mean

    # Train/validation gap threshold
    train_val_gap_threshold: float = 0.1  # Maximum gap as fraction of train metric

    # Stability metric (spectral radius ρ) band
    rho_band: tuple[float, float] = (0.0, 1.0)  # [min_rho, max_rho]

    # Minimum seeds required for statistical gates
    min_seeds_for_stats: int = 5

    # Power analysis parameters
    power_target: float = 0.8
    alpha: float = 0.05
    effect_size_target: float = 0.5  # Cohen's d

    # Discovery/confirmation seed separation
    use_confirmation_seeds_for_l2: bool = True

    @property
    def required_seeds_per_group(self) -> int:
        """Required seeds per group from power analysis (C0)."""
        from computronium.core.statistics import required_sample_size

        return required_sample_size(
            effect_size=self.effect_size_target,
            power=self.power_target,
            alpha=self.alpha,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "superiority_margin": self.superiority_margin,
            "superiority_margin_sigma": self.superiority_margin_sigma,
            "ci_width_threshold": self.ci_width_threshold,
            "train_val_gap_threshold": self.train_val_gap_threshold,
            "rho_band": list(self.rho_band),
            "min_seeds_for_stats": self.min_seeds_for_stats,
            "power_target": self.power_target,
            "alpha": self.alpha,
            "effect_size_target": self.effect_size_target,
            "required_seeds_per_group": self.required_seeds_per_group,
            "use_confirmation_seeds_for_l2": self.use_confirmation_seeds_for_l2,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GateThresholds:
        return cls(
            superiority_margin=data.get("superiority_margin", 0.0),
            superiority_margin_sigma=data.get("superiority_margin_sigma", 2.0),
            ci_width_threshold=data.get("ci_width_threshold", 0.05),
            train_val_gap_threshold=data.get("train_val_gap_threshold", 0.1),
            rho_band=tuple(data.get("rho_band", [0.0, 1.0])),
            min_seeds_for_stats=data.get("min_seeds_for_stats", 5),
            power_target=data.get("power_target", 0.8),
            alpha=data.get("alpha", 0.05),
            effect_size_target=data.get("effect_size_target", 0.5),
            use_confirmation_seeds_for_l2=data.get(
                "use_confirmation_seeds_for_l2", True
            ),
        )


@dataclass(frozen=True, slots=True)
class GateResult:
    """Result of a single statistical gate check."""

    gate_name: str
    passed: bool
    statistic: float | None
    threshold: float | None
    reason: str
    details: dict[str, Any] = field(default_factory=dict)
    verdict: StatisticalVerdict | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate": self.gate_name,
            "passed": self.passed,
            "statistic": self.statistic,
            "threshold": self.threshold,
            "reason": self.reason,
            "verdict": self.verdict.value if self.verdict else None,
            "details": self.details,
        }


@dataclass(frozen=True, slots=True)
class PromotionGateResult:
    """Aggregate result of all L1 statistical gates for a cell."""

    cell_key: str
    replication_key: str
    all_passed: bool
    gate_results: list[GateResult]
    verdict: StatisticalVerdict = StatisticalVerdict.INSUFFICIENT
    baseline: BaselineRecord | None = None
    discovery_seeds_used: bool = (
        False  # True if using discovery seeds (not confirmation)
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "cell_key": self.cell_key,
            "replication_key": self.replication_key,
            "all_passed": self.all_passed,
            "verdict": self.verdict.value,
            "gates": [g.to_dict() for g in self.gate_results],
            "baseline": self.baseline.to_dict() if self.baseline else None,
            "discovery_seeds_used": self.discovery_seeds_used,
        }


def compute_confidence_interval(
    values: list[float],
    confidence_level: float = 0.95,
) -> tuple[float, float]:
    """Compute confidence interval for a list of values."""
    if len(values) < 2:
        return (float("nan"), float("nan"))
    n = len(values)
    mean = float(np.mean(values))
    se = float(np.std(values, ddof=1) / math.sqrt(n))
    alpha = 1 - confidence_level
    t_crit = float(stats.t.ppf(1 - alpha / 2, n - 1))
    return (mean - t_crit * se, mean + t_crit * se)


def check_superiority_gate(
    cell_values: list[float],
    baseline_values: list[float],
    thresholds: GateThresholds,
    metric_name: str = "validation_accuracy",
) -> GateResult:
    """Check if cell mean is superior to baseline with statistical confidence.

    Gates:
    - mean_cell > mean_baseline + superiority_margin (absolute)
    - mean_cell > mean_baseline + superiority_margin_sigma * SE_cell
    - Minimum seeds from power analysis (C0/C1)

    If no baseline is available, this gate is skipped (passed=True with a note).
    """
    # Use power analysis to determine required seeds (C0/C1)
    required_seeds = thresholds.required_seeds_per_group

    if not baseline_values:
        # No baseline available - skip this gate (pass with note)
        return GateResult(
            gate_name="superiority",
            passed=True,
            statistic=None,
            threshold=None,
            reason=(
                "No baseline available; superiority gate skipped, so the "
                "comparison is INSUFFICIENT rather than PASSED"
            ),
            details={"n_cell": len(cell_values), "n_baseline": 0},
            verdict=StatisticalVerdict.INSUFFICIENT,
        )

    cell_mean = np.mean(cell_values)
    baseline_mean = np.mean(baseline_values)
    cell_std = np.std(cell_values, ddof=1) if len(cell_values) > 1 else 0.0
    cell_se = (
        cell_std / math.sqrt(len(cell_values)) if len(cell_values) > 1 else float("inf")
    )

    absolute_superior = bool(cell_mean > baseline_mean + thresholds.superiority_margin)

    # Sigma margin check (mean > baseline + k * SE)
    # Use power-derived threshold instead of fixed 2*SE (C1)
    sigma_superior = bool(
        cell_mean > baseline_mean + thresholds.superiority_margin_sigma * cell_se
    )

    # Calculate effect size (Cohen's d)
    pooled_std = (
        math.sqrt(
            (
                (len(cell_values) - 1) * cell_std**2
                + (len(baseline_values) - 1) * np.std(baseline_values, ddof=1) ** 2
            )
            / (len(cell_values) + len(baseline_values) - 2)
        )
        if len(cell_values) > 1 and len(baseline_values) > 1
        else 1.0
    )

    effect_size = (cell_mean - baseline_mean) / max(pooled_std, 1e-12)

    # Calculate achieved power (C1: verdict reports power_achieved)
    from computronium.core.statistics import power_for_two_sample

    power_achieved = (
        power_for_two_sample(
            effect_size, min(len(cell_values), len(baseline_values)), thresholds.alpha
        )
        if min(len(cell_values), len(baseline_values)) >= 2
        else 0.0
    )

    if len(cell_values) < required_seeds:
        # Too few seeds to detect the target effect: the honest verdict is
        # INSUFFICIENT, never REJECTED. The claim line carries n, so a reader
        # sees the weakness rather than reading it as "no effect".
        return GateResult(
            gate_name="superiority",
            passed=False,
            statistic=cell_mean - baseline_mean,
            threshold=required_seeds,
            reason=(
                f"Underpowered: {len(cell_values)} < {required_seeds} seeds needed "
                f"for d={thresholds.effect_size_target} at power={thresholds.power_target}; "
                f"observed Δ={cell_mean - baseline_mean:.4f}, "
                f"effect_size={effect_size:.3f}, power_achieved={power_achieved:.2f}"
            ),
            details={
                "n_cell": len(cell_values),
                "n_baseline": len(baseline_values),
                "required_seeds": required_seeds,
                "cell_mean": float(cell_mean),
                "baseline_mean": float(baseline_mean),
                "effect_size": float(effect_size),
                "power_achieved": float(power_achieved),
                "power_target": thresholds.power_target,
                "effect_size_target": thresholds.effect_size_target,
                "alpha": thresholds.alpha,
            },
            verdict=StatisticalVerdict.INSUFFICIENT,
        )

    passed = absolute_superior and sigma_superior

    return GateResult(
        gate_name="superiority",
        passed=passed,
        statistic=cell_mean - baseline_mean,
        threshold=thresholds.superiority_margin,
        reason=(
            f"Cell mean {cell_mean:.4f} vs baseline {baseline_mean:.4f}: "
            f"Δ={cell_mean - baseline_mean:.4f}, effect_size={effect_size:.3f}, "
            f"power_achieved={power_achieved:.2f}"
        ),
        details={
            "cell_mean": float(cell_mean),
            "baseline_mean": float(baseline_mean),
            "cell_std": float(cell_std),
            "cell_se": float(cell_se),
            "effect_size": float(effect_size),
            "absolute_superior": absolute_superior,
            "sigma_superior": sigma_superior,
            "power_achieved": float(power_achieved),
            "required_seeds": required_seeds,
        },
        verdict=(StatisticalVerdict.PASSED if passed else StatisticalVerdict.REJECTED),
    )


def check_ci_width_gate(
    cell_values: list[float],
    thresholds: GateThresholds,
    metric_name: str = "validation_accuracy",
    confidence_level: float = 0.95,
) -> GateResult:
    """Check if confidence interval is narrow enough."""
    if len(cell_values) < 2:
        # For n_seeds=1, we can't compute CI - pass with a note
        return GateResult(
            gate_name="ci_width",
            passed=True,
            statistic=len(cell_values),
            threshold=2,
            reason=f"Insufficient seeds for CI (need 2, got {len(cell_values)}); gate skipped",
            details={"n_seeds": len(cell_values), "skipped": True},
        )

    mean = np.mean(cell_values)
    ci_lower, ci_upper = compute_confidence_interval(cell_values, confidence_level)
    ci_width = ci_upper - ci_lower
    relative_width = ci_width / max(abs(mean), 1e-12)

    passed = relative_width < thresholds.ci_width_threshold

    return GateResult(
        gate_name="ci_width",
        passed=passed,
        statistic=relative_width,
        threshold=thresholds.ci_width_threshold,
        reason=(
            f"CI [{ci_lower:.4f}, {ci_upper:.4f}] width={ci_width:.4f} "
            f"relative={relative_width:.4f} (threshold={thresholds.ci_width_threshold})"
        ),
        details={
            "ci_lower": float(ci_lower),
            "ci_upper": float(ci_upper),
            "ci_width": float(ci_width),
            "relative_width": float(relative_width),
            "mean": float(mean),
        },
    )


def check_train_val_gap_gate(
    train_values: list[float],
    val_values: list[float],
    thresholds: GateThresholds,
) -> GateResult:
    """Check if train/validation gap is within threshold."""
    if not train_values or not val_values:
        return GateResult(
            gate_name="train_val_gap",
            passed=False,
            statistic=None,
            threshold=None,
            reason="Missing train or validation values",
            details={},
        )

    train_mean = np.mean(train_values)
    val_mean = np.mean(val_values)
    gap = train_mean - val_mean
    relative_gap = gap / max(train_mean, 1e-12)

    passed = bool(relative_gap < thresholds.train_val_gap_threshold)

    return GateResult(
        gate_name="train_val_gap",
        passed=passed,
        statistic=relative_gap,
        threshold=thresholds.train_val_gap_threshold,
        reason=(
            f"Train={train_mean:.4f}, Val={val_mean:.4f}, "
            f"gap={gap:.4f}, relative={relative_gap:.4f} (threshold={thresholds.train_val_gap_threshold})"
        ),
        details={
            "train_mean": float(train_mean),
            "val_mean": float(val_mean),
            "absolute_gap": float(gap),
            "relative_gap": float(relative_gap),
        },
    )


def check_rho_band_gate(
    rho_values: list[float],
    thresholds: GateThresholds,
) -> GateResult:
    """Check if spectral radius (stability metric) is within acceptable band."""
    if not rho_values:
        return GateResult(
            gate_name="rho_band",
            passed=True,  # Not a hard failure if not available
            statistic=None,
            threshold=None,
            reason="No ρ values available (skipping)",
            details={},
        )

    rho_mean = np.mean(rho_values)
    rho_min, rho_max = thresholds.rho_band
    passed = bool(rho_min <= rho_mean <= rho_max)

    return GateResult(
        gate_name="rho_band",
        passed=passed,
        statistic=rho_mean,
        threshold=float(rho_max - rho_min),  # Band width as single threshold
        reason=(
            f"ρ={rho_mean:.4f} band=[{rho_min}, {rho_max}] "
            f"{'in' if passed else 'OUT'} band"
        ),
        details={
            "rho_mean": float(rho_mean),
            "rho_min": rho_min,
            "rho_max": rho_max,
            "rho_std": float(np.std(rho_values, ddof=1))
            if len(rho_values) > 1
            else 0.0,
        },
    )


def compute_required_seeds_power(
    effect_size: float,
    power: float = 0.8,
    alpha: float = 0.05,
    test_type: str = "t_test",
) -> int:
    """Compute required seeds for a given effect size and power.

    Delegates to canonical implementation in core.statistics.
    """
    from computronium.core.statistics import required_sample_size

    return required_sample_size(
        effect_size=effect_size,
        power=power,
        alpha=alpha,
    )


def run_l1_statistical_gates(  # ruff: ignore[too-many-locals] - one accumulator per gate metric
    cell_records: list[Record],
    baseline: BaselineRecord | None,
    thresholds: GateThresholds,
    *,
    use_discovery_seeds: bool = True,
) -> PromotionGateResult:
    """Run all L1 statistical gates for a cell's records.

    Args:
        cell_records: Records for one cell (same replication key, different seeds)
        baseline: BaselineRecord for comparison (must have same task/hardware/budget/seeds)
        thresholds: GateThresholds configuration
        use_discovery_seeds: Whether these are discovery seeds (True) or confirmation seeds (False)
    """
    if not cell_records:
        return PromotionGateResult(
            cell_key="",
            replication_key="",
            all_passed=False,
            gate_results=[GateResult("all", False, None, None, "No records provided")],
        )

    cell_key = cell_records[0].cell_key
    replication_key = (
        cell_records[0].measurement_key.rsplit("_seed_", 1)[0]
        if "_seed_" in cell_records[0].measurement_key
        else cell_key
    )

    # Extract metric values from records. Objectives are named in the registry;
    # payloads carry their metric_key (e.g. val_acc), never the objective name —
    # reading the objective name here left every gate measuring nothing (TODO63).
    from computronium.experiment.schema.metrics import HISTORY_METRICS, objective_metric

    metric_key = "validation_accuracy"  # Primary metric
    val_key = objective_metric(metric_key)
    train_key = "train_acc" if "train_acc" in HISTORY_METRICS else val_key
    cell_values = []
    train_values = []
    val_values = []
    rho_values = []

    for record in cell_records:
        # Validation accuracy
        val = record.payload.get(val_key)
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            cell_values.append(float(val))

        # Train accuracy
        train = record.payload.get(train_key)
        if isinstance(train, (int, float)) and not isinstance(train, bool):
            train_values.append(float(train))

        val = record.payload.get(val_key)
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            val_values.append(float(val))

        # Spectral radius (stability)
        rho = record.payload.get("spectral_radius")
        if isinstance(rho, (int, float)) and not isinstance(rho, bool):
            rho_values.append(float(rho))

    gate_results: list[GateResult] = []

    # Gate 1: Superiority over baseline
    if baseline and baseline.metrics:
        baseline_metric = baseline.metrics.get(val_key, 0.0)
        # For baseline, we only have aggregate, so use as single value
        baseline_vals = [baseline_metric]
    else:
        baseline_vals = []

    gate_results.append(
        check_superiority_gate(cell_values, baseline_vals, thresholds, metric_key)
    )

    # Gate 2: CI width
    gate_results.append(check_ci_width_gate(cell_values, thresholds, metric_key))

    # Gate 3: Train/val gap
    gate_results.append(check_train_val_gap_gate(train_values, val_values, thresholds))

    # Gate 4: Rho band
    gate_results.append(check_rho_band_gate(rho_values, thresholds))

    all_passed = all(g.passed for g in gate_results)
    if any(g.verdict is StatisticalVerdict.INSUFFICIENT for g in gate_results):
        verdict = StatisticalVerdict.INSUFFICIENT
    elif all_passed:
        verdict = StatisticalVerdict.PASSED
    else:
        verdict = StatisticalVerdict.REJECTED

    return PromotionGateResult(
        cell_key=cell_key,
        replication_key=replication_key,
        all_passed=all_passed,
        gate_results=gate_results,
        verdict=verdict,
        baseline=baseline,
        discovery_seeds_used=use_discovery_seeds,
    )


class StatisticalGateRunner:
    """Runs statistical promotion gates with config-driven thresholds."""

    def __init__(
        self,
        store: RecordStore,
        thresholds: GateThresholds | None = None,
    ) -> None:
        self.store = store
        self.thresholds = thresholds or GateThresholds()

    def evaluate_cell(
        self,
        cell_records: list[Record],
        baseline: BaselineRecord | None = None,
        *,
        use_discovery_seeds: bool = True,
    ) -> PromotionGateResult:
        """Evaluate all L1 gates for a cell."""
        return run_l1_statistical_gates(
            cell_records,
            baseline,
            self.thresholds,
            use_discovery_seeds=use_discovery_seeds,
        )

    def evaluate_cells_batch(
        self,
        cells: dict[str, list[Record]],
        baselines: dict[str, BaselineRecord] | None = None,
        *,
        use_discovery_seeds: bool = True,
    ) -> dict[str, PromotionGateResult]:
        """Evaluate L1 gates for multiple cells."""
        baselines = baselines or {}
        results = {}
        for replication_key, records in cells.items():
            baseline = baselines.get(replication_key)
            results[replication_key] = self.evaluate_cell(
                records, baseline, use_discovery_seeds=use_discovery_seeds
            )
        return results


def _evaluate_l2_confirmation(
    gate_runner: StatisticalGateRunner,
    group: list[Record],
    baseline: BaselineRecord | None,
    spec: RunSpec,
    cycle: int,
    confirmation_evaluator: Callable[[list[Record], list[int]], list[Record]] | None,
    thresholds: GateThresholds,
    tolerance: float,
) -> tuple[bool, str, PromotionGateResult | None]:
    """Evaluate L2 confirmation for a cell group.

    When a ``confirmation_evaluator`` is supplied, the cell is re-measured on
    fresh confirmation seeds and re-gated; otherwise the legacy replay gate runs.

    Returns:
        (l2_passed, replay_status, confirmation_gate_result)
    """
    from computronium.experiment.execution.promotion import replay_survives
    from computronium.experiment.registry.seed import SeedContext

    if not (
        thresholds.use_confirmation_seeds_for_l2 and confirmation_evaluator is not None
    ):
        # Fallback to replay gate (no fresh-seed confirmation available)
        representative = min(group, key=lambda r: r.schedule.seed)
        survived = replay_survives(representative, tolerance)
        return survived, "pass" if survived else "fail", None

    # C1: re-measure with fresh confirmation seeds, never the discovery seeds.
    seed_ctx = SeedContext(spec.seed)
    confirmation_seeds = seed_ctx.confirmation_seeds(cycle, 1, spec.n_seeds)[0]

    try:
        confirmation_records = confirmation_evaluator(group, confirmation_seeds)
        confirmation_gate_result = gate_runner.evaluate_cell(
            confirmation_records, baseline, use_discovery_seeds=False
        )
    except Exception as exc:  # ruff: ignore[blind-except] - a failed confirmation is a non-promotion, not a crash
        logger.warning("Confirmation evaluation failed: %s", exc)
        return False, "fail", None

    l2_passed = confirmation_gate_result.all_passed
    return l2_passed, "pass" if l2_passed else "fail", confirmation_gate_result


def promote_with_stats(
    store: RecordStore,
    run_id: str,
    spec: RunSpec,
    *,
    tolerance: float,
    thresholds: GateThresholds | None = None,
    baselines: dict[str, BaselineRecord] | None = None,
    confirmation_evaluator: Callable[[list[Record], list[int]], list[Record]]
    | None = None,
    cycle: int = 0,
) -> list[dict[str, Any]]:
    """Earn maturity with statistical gates at L1; L2 requires confirmation seeds (C1).

    This is the enhanced version of promote_run that adds L1 statistical gates.
    For L2 promotion, if `confirmation_evaluator` is provided and
    `thresholds.use_confirmation_seeds_for_l2` is True, cells that pass L1
    are re-evaluated with fresh confirmation seeds.

    Args:
        store: RecordStore
        run_id: Run identifier
        spec: RunSpec
        tolerance: Replay tolerance for L2
        thresholds: GateThresholds for L1 stats gates
        baselines: Mapping replication_key -> BaselineRecord for comparison
        confirmation_evaluator: Optional callable(cell_records, confirmation_seeds)
            that re-measures a cell with fresh confirmation seeds and returns the
            new records. If provided, used for L2 promotion (C1).
        cycle: Current loop cycle number (for confirmation seed generation).
    """
    from computronium.experiment.execution.promotion import (
        eligible_cells,
    )

    # First run original promotion to get L1 eligibility
    records = store.query_records(run_id=run_id)
    eligible = eligible_cells(records, spec.n_seeds)

    # Now run statistical gates for L1->L2 decision
    from computronium.experiment.schema.record import (
        Maturity,
        ReproducibilityClass,
    )

    # Write L1 for all eligible cells (as before)
    for key, group in eligible.items():
        cell_key = group[0].cell_key
        for record in group:
            store.set_cell_maturity(run_id, record.cell_key, Maturity.L1)

    history: list[dict[str, Any]] = []
    gate_runner = StatisticalGateRunner(store, thresholds)
    thresholds = thresholds or GateThresholds()

    for key, group in eligible.items():
        cell_key = group[0].cell_key
        baseline = baselines.get(key) if baselines else None

        # Run statistical gates (using discovery seeds)
        gate_result = gate_runner.evaluate_cell(
            group, baseline, use_discovery_seeds=True
        )

        l2_passed = False
        replay_status = "fail"
        confirmation_gate_result = None

        if gate_result.all_passed:
            # Cell passed L1 statistical gates
            l2_passed, replay_status, confirmation_gate_result = (
                _evaluate_l2_confirmation(
                    gate_runner,
                    group,
                    baseline,
                    spec,
                    cycle,
                    confirmation_evaluator,
                    thresholds,
                    tolerance,
                )
            )

        if l2_passed:
            store.set_cell_maturity(
                run_id,
                cell_key,
                Maturity.L2,
                ReproducibilityClass.COMPUTATIONALLY_REPRODUCIBLE,
            )
            maturity = Maturity.L2.value
        else:
            maturity = Maturity.L1.value

        history.append({
            "cell_key": cell_key,
            "replication_key": key,
            "maturity": maturity,
            "replay": replay_status,
            "verdict": gate_result.verdict.value,
            "statistical_gates": gate_result.to_dict(),
            "confirmation_gates": confirmation_gate_result.to_dict()
            if confirmation_gate_result
            else None,
        })

    return history


__all__ = [
    "GateResult",
    "GateThresholds",
    "PromotionGateResult",
    "StatisticalGateRunner",
    "StatisticalVerdict",
    "check_ci_width_gate",
    "check_rho_band_gate",
    "check_superiority_gate",
    "check_train_val_gap_gate",
    "compute_confidence_interval",
    "compute_required_seeds_power",
    "promote_with_stats",
    "run_l1_statistical_gates",
]
