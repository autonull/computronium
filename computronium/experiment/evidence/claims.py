"""Full predicate suite for experiment claims and governance.

Implements WP5 deliverable: evidence/claims.py — full predicate suite:
- Claims (R35): claim_eligible predicate
- Promotion (R36): promotion predicate
- Alerts as record-stream predicates (R83/Q14)
- Matched-cost comparison guard (R65)
- Stratification guards (R8/R22/R67)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.coordinate import DataOrigin
from computronium.experiment.schema.record import GateVerdict, Record

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from computronium.experiment.evidence.protocol import ComparisonGuard, CostBudget
    from computronium.experiment.evidence.store import RecordStore


# =============================================================================
# Claim Predicates (R35)
# =============================================================================


def claim_eligible(record: Record) -> bool:
    """Check if a record is eligible for claim consideration.

    Claim prefilter (plain SQL, per plan §2):
    WHERE status.gate_verdict = 'PASS'
    AND NOT status.quarantine
    AND schedule.fidelity = 'L2'
    AND schedule.n_seeds >= 5

    This is the pure Python predicate; the SQL prefilter lives in
    RecordStore.claim_eligible_prefilter().
    """
    return (
        record.status.gate_verdict.value == "PASS"
        and not record.status.quarantine
        and record.schedule.fidelity == "L2"
        and record.schedule.n_seeds >= 5
    )


def replication_key(record: Record) -> str:
    """The record's replication key: coordinate + schedule, without seed.

    One definition of measurement identity, read by claim eligibility, the
    achieved-seed count, the claim table and the limitations.
    """
    return (
        f"{record.cell_key}|"
        f"{record.schedule.fidelity}|"
        f"{record.schedule.n_seeds}|"
        f"{record.schedule.epochs}|"
        f"{record.schedule.batch_limit}|"
        f"{record.schedule.budget_id}"
    )


def claim_eligible_by_achieved_seeds(
    record: Record,
    store: "RecordStore",  # ruff: ignore[quoted-annotation] - forward reference for type-checking import
    min_seeds: int = 5,
    run_id: str | None = None,
) -> bool:
    """Check if a record is eligible for claim based on *achieved* seeds.

    Unlike claim_eligible(), which reads the *planned* ``schedule.n_seeds``,
    this queries the store for the seeds that actually completed with a PASS
    gate verdict for this replication key, so a run that died mid-replication
    is not claim-eligible (L20 remediation).

    Args:
        record: The record to check.
        store: The RecordStore to query for achieved seeds.
        min_seeds: Minimum required achieved seeds (default 5 per protocol).
        run_id: Optional run ID to scope the query.

    Returns:
        True if achieved seeds >= min_seeds and other criteria met.
    """
    if not (
        record.status.gate_verdict.value == "PASS"
        and not record.status.quarantine
        and record.schedule.fidelity == "L2"
    ):
        return False

    achieved = store.count_achieved_seeds(
        replication_key=replication_key(record),
        run_id=run_id or record.run_id,
        gate_verdict=GateVerdict.PASS_,
    )

    return achieved >= min_seeds


def claim_eligible_strict(record: Record, min_seeds: int = 5) -> bool:
    """Strict claim eligibility with configurable minimum seeds."""
    return (
        record.status.gate_verdict.value == "PASS"
        and not record.status.quarantine
        and record.schedule.fidelity == "L2"
        and record.schedule.n_seeds >= min_seeds
    )


# =============================================================================
# Claim Derivation (R35/R64) — claims, with n and variance or not at all
# =============================================================================


@dataclass(frozen=True, slots=True)
class Claim:
    """One claim a run makes about one axis value, with its evidence attached.

    R64: a claim carries n and variance. Both are required fields, so a claim
    without them is not expressible rather than merely discouraged.

    Attributes:
        metric: The payload key the claim is about.
        axis: The structural axis the claim varies.
        value: The axis value the claim is about.
        n: Measurements behind the claim (seeds across cells).
        mean: Mean of the metric over those measurements.
        variance: Sample variance of the metric over those measurements.
        cells: Distinct cells (replication keys) contributing.
    """

    metric: str
    axis: str
    value: str
    n: int
    mean: float
    variance: float
    cells: int

    def __post_init__(self) -> None:
        if self.n < 1:
            msg = f"Claim.n must be at least 1, got {self.n}"
            raise ValueError(msg)
        if not math.isfinite(self.mean) or not math.isfinite(self.variance):
            msg = f"Claim metrics must be finite: mean={self.mean} variance={self.variance}"
            raise ValueError(msg)
        if self.variance < 0.0:
            msg = f"Claim.variance must be non-negative, got {self.variance}"
            raise ValueError(msg)

    def render(self) -> str:
        """The claim as one report line, evidence included."""
        return (
            f"{self.axis}={self.value}: {self.metric}={self.mean:.4f} "
            f"±{math.sqrt(self.variance):.4f} (n={self.n}, cells={self.cells})"
        )


@dataclass(frozen=True, slots=True)
class AxisImpact:
    """Which axis moved the metric most, and by how much.

    Attributes:
        axis: The axis with the widest spread between its values' means.
        metric: The metric the spread was measured on.
        best_value: The axis value with the highest mean.
        worst_value: The axis value with the lowest mean.
        spread: Absolute difference between the two means.
    """

    axis: str
    metric: str
    best_value: str
    worst_value: str
    spread: float

    def render(self) -> str:
        """The impact as one report line."""
        return (
            f"{self.axis} mattered most for {self.metric}: "
            f"{self.best_value} vs {self.worst_value} by {self.spread:.4f}"
        )


def derive_claims(
    records: Sequence[Record],
    *,
    metric: str,
    achieved: Mapping[str, int] | None = None,
    min_seeds: int = 5,
) -> tuple[Claim, ...]:
    """Group claim-eligible records by axis value and summarise each group.

    Eligibility is a filter the run does not apply to itself: a record
    contributes only when it passed its gate, is not quarantined, and its
    replication key reached ``min_seeds`` passing seeds. The achieved-seed
    count is the honest one — ``claim_eligible`` reads the *planned*
    ``schedule.n_seeds``, which the per-seed executor stamps as 1.

    Args:
        records: The run's records (or any slice of them).
        metric: The payload key to claim about.
        achieved: Achieved PASS seeds per replication key, as
            ``RecordStore.count_achieved_seeds`` reports them. Without it, a
            record's own gate verdict is the only filter.
        min_seeds: Seeds a cell must have reached to contribute.

    Returns:
        One claim per axis value that reached ``min_seeds`` measurements,
        ordered by axis then by descending mean.
    """
    grouped: dict[tuple[str, str], list[Record]] = {}
    for record in records:
        if not _contributes(record, achieved=achieved, min_seeds=min_seeds):
            continue
        value = record.payload.get(metric)
        if isinstance(value, bool) or not isinstance(value, int | float):
            continue
        for axis in StructuralAxis:
            grouped.setdefault((axis.value, getattr(record, axis.value)), []).append(
                record
            )

    claims: list[Claim] = []
    for (axis, value), group in grouped.items():
        if len(group) < min_seeds:
            continue
        values = [float(r.payload[metric]) for r in group]
        mean = sum(values) / len(values)
        variance = (
            sum((v - mean) ** 2 for v in values) / (len(values) - 1)
            if len(values) > 1
            else 0.0
        )
        claims.append(
            Claim(
                metric=metric,
                axis=axis,
                value=value,
                n=len(values),
                mean=mean,
                variance=variance,
                cells=len({replication_key(r) for r in group}),
            )
        )
    return tuple(sorted(claims, key=lambda c: (c.axis, -c.mean, c.value)))


def strongest_axis(claims: Sequence[Claim]) -> AxisImpact | None:
    """The axis whose values' means spread widest on the claimed metric.

    Args:
        claims: Claims from one run, possibly over several metrics.

    Returns:
        The widest axis, or ``None`` when every axis has a single value.
    """
    by_axis: dict[tuple[str, str], dict[str, float]] = {}
    for claim in claims:
        by_axis.setdefault((claim.metric, claim.axis), {})[claim.value] = claim.mean
    if not by_axis:
        return None
    (metric, axis), means = max(
        by_axis.items(),
        key=lambda item: (max(item[1].values()) - min(item[1].values()), item[0][1]),
    )
    if len(means) < 2:
        return None
    spread = (
        means[best := max(means, key=lambda value: (means[value], value))]
        - means[min(means, key=lambda value: (means[value], value))]
    )
    if spread <= 0.0:
        return None
    worst = min(means, key=lambda value: (means[value], value))
    return AxisImpact(
        axis=axis,
        metric=metric,
        best_value=best,
        worst_value=worst,
        spread=spread,
    )


def _contributes(
    record: Record,
    *,
    achieved: Mapping[str, int] | None,
    min_seeds: int,
) -> bool:
    """Whether one record may back a claim (R35/R64 filter, never an assertion)."""
    if record.status.gate_verdict.value != "PASS" or record.status.quarantine:
        return False
    if achieved is None:
        return True
    return achieved.get(replication_key(record), 0) >= min_seeds


# =============================================================================
# Promotion Predicates (R36)
# =============================================================================


def promoted(record: Record) -> bool:
    """Check if a record has been promoted (matured to claim-grade).

    Promotion requires:
    - Claim eligible
    - Maturity L2 (claim-grade)
    - Computationally reproducible or better
    """
    return (
        claim_eligible(record)
        and record.status.maturity.value == "l2"
        and record.status.reproducibility.value
        in {"computationally_reproducible", "scientifically_reproducible"}
    )


def promotable(record: Record, target_maturity: str = "l2") -> bool:
    """Check if a record can be promoted to target maturity.

    A record is promotable if it meets the criteria for the target level.
    """
    maturity_order = {"l0": 0, "l1": 1, "l2": 2}
    current = maturity_order.get(record.status.maturity.value, 0)
    target = maturity_order.get(target_maturity, 2)
    return current >= target and claim_eligible(record)


# =============================================================================
# Derived Claim Predicates (pure queries, never stored - Doctrine 5)
# =============================================================================


def beats_baseline(
    record: Record,
    baseline_accuracy: float,
    metric: str = "accuracy",
    margin: float = 0.0,
) -> bool:
    """Check if record beats a baseline by at least margin."""
    value = record.payload.get(metric)
    if value is None:
        return False
    return value >= baseline_accuracy + margin


def robust(record: Record, min_seeds: int = 5, cv_threshold: float = 0.1) -> bool:
    """Check if record shows robust performance across seeds.

    Robustness: coefficient of variation across seeds < threshold.
    Requires payload to contain per-seed metrics.
    """
    seed_metrics = record.payload.get("seed_metrics")
    if not seed_metrics or not isinstance(seed_metrics, list):
        # Fallback: check if n_seeds is sufficient
        return record.schedule.n_seeds >= min_seeds

    values = [m.get("accuracy", 0) for m in seed_metrics if isinstance(m, dict)]
    if len(values) < 2:
        return False

    import statistics

    mean_val = statistics.mean(values)
    if mean_val == 0:
        return False
    cv = statistics.stdev(values) / mean_val
    return cv <= cv_threshold


def generalizes(
    record: Record,
    heldout_tasks: list[str],
    min_tasks: int = 3,
) -> bool:
    """Check if record generalizes to held-out tasks.

    Requires payload to contain per-task metrics.
    """
    task_metrics = record.payload.get("task_metrics")
    if not task_metrics or not isinstance(task_metrics, dict):
        return False

    passing_tasks = 0
    for task in heldout_tasks:
        if task in task_metrics:
            metric = task_metrics[task]
            if (isinstance(metric, dict) and metric.get("accuracy", 0) > 0.5) or (
                isinstance(metric, (int, float)) and metric > 0.5
            ):
                passing_tasks += 1

    return passing_tasks >= min_tasks


# =============================================================================
# Alert Predicates (R83/Q14) - Record Stream Predicates
# =============================================================================


@dataclass(frozen=True, slots=True)
class Alert:
    """An alert emitted from the record stream."""

    alert_id: str
    alert_type: str
    severity: str
    message: str
    record_id: str
    cell_key: str
    metadata: dict[str, Any]


def alert_on_divergence(record: Record) -> Alert | None:
    """Alert if record shows divergence (NaN loss, exploding gradients)."""
    loss = record.payload.get("loss")
    if loss is not None:
        import math

        if math.isnan(loss) or math.isinf(loss) or loss > 1e6:
            return Alert(
                alert_id=f"divergence_{record.record_id[:8]}",
                alert_type="divergence",
                severity="critical",
                message=f"Divergence detected: loss={loss}",
                record_id=record.record_id,
                cell_key=record.cell_key,
                metadata={"loss": loss},
            )
    return None


def alert_on_stagnation(
    record: Record,
    patience: int = 10,
    min_improvement: float = 1e-4,
) -> Alert | None:
    """Alert if record shows stagnation (no improvement for patience epochs)."""
    history = record.payload.get("history")
    if not history or not isinstance(history, list):
        return None

    accuracies = [h.get("val_accuracy", 0) for h in history if isinstance(h, dict)]
    if len(accuracies) < patience:
        return None

    recent = accuracies[-patience:]
    best_recent = max(recent)
    best_overall = max(accuracies)

    if best_overall - best_recent < min_improvement:
        return Alert(
            alert_id=f"stagnation_{record.record_id[:8]}",
            alert_type="stagnation",
            severity="warning",
            message=f"No improvement for {patience} epochs",
            record_id=record.record_id,
            cell_key=record.cell_key,
            metadata={"patience": patience, "best_overall": best_overall},
        )
    return None


def alert_on_resource_exhaustion(record: Record) -> Alert | None:
    """Alert if record hit resource limits (OOM, timeout)."""
    failure_signal = record.payload.get("failure_signal")
    if failure_signal in {"oom", "timeout", "memory_error"}:
        return Alert(
            alert_id=f"resource_{record.record_id[:8]}",
            alert_type="resource_exhaustion",
            severity="critical",
            message=f"Resource exhaustion: {failure_signal}",
            record_id=record.record_id,
            cell_key=record.cell_key,
            metadata={"failure_signal": failure_signal},
        )
    return None


def alert_on_constraint_violation(record: Record) -> Alert | None:
    """Alert if record has hard constraint violations."""
    # This would need access to the classification result
    # For now, check if status indicates constraint violation
    if record.status.cause.value == "constraint_violation":
        return Alert(
            alert_id=f"constraint_{record.record_id[:8]}",
            alert_type="constraint_violation",
            severity="high",
            message="Hard constraint violation detected",
            record_id=record.record_id,
            cell_key=record.cell_key,
            metadata={"cause": record.status.cause.value},
        )
    return None


def check_all_alerts(record: Record) -> list[Alert]:
    """Run all alert predicates on a record."""
    alerts = []
    for alert_fn in (
        alert_on_divergence,
        alert_on_stagnation,
        alert_on_resource_exhaustion,
        alert_on_constraint_violation,
    ):
        alert = alert_fn(record)
        if alert:
            alerts.append(alert)
    return alerts


# =============================================================================
# Matched-Cost Comparison Guard (R65)
# =============================================================================


def compare_matched_cost(
    record_a: Record,
    record_b: Record,
    guard: ComparisonGuard,
    metric: str = "accuracy",
) -> tuple[bool, str | None]:
    """Compare two records under matched-cost protocol.

    Returns (comparison_valid, label_or_none).
    If budgets match, returns (True, None).
    If budgets don't match, returns (False, label) per guard config.
    """
    # Extract budgets from records
    budget_a = _extract_budget(record_a)
    budget_b = _extract_budget(record_b)

    if budget_a is None or budget_b is None:
        return False, "MISSING_BUDGET"

    return guard.check_or_label(budget_b, label_unmatched=True)


def _extract_budget(record: Record) -> CostBudget | None:
    """Extract cost budget from record payload/provenance."""
    # Budget info should be in payload or provenance.links (as JSON string)
    budget_info = record.payload.get("cost_budget")
    if budget_info is None:
        budget_str = record.provenance.links.get("cost_budget")
        if budget_str:
            try:
                import json

                budget_info = json.loads(budget_str)
            except json.JSONDecodeError:
                budget_info = None
    if not budget_info:
        return None

    from computronium.experiment.evidence.protocol import CostBudget, CostBudgetKind

    kind_str = budget_info.get("kind", "eval_count")
    try:
        kind = CostBudgetKind(kind_str)
    except ValueError:
        kind = CostBudgetKind.EVAL_COUNT

    limit = budget_info.get("limit", 0)
    if limit <= 0:
        return None

    return CostBudget(kind=kind, limit=float(limit))


# =============================================================================
# Stratification Guards (R8/R22/R67)
# =============================================================================


def same_hardware_class(record_a: Record, record_b: Record) -> bool:
    """Check if two records ran on the same hardware class.

    Required for valid WALLTIME budget comparisons.
    """
    hw_a = record_a.provenance.env.get("hardware_class", "unknown")
    hw_b = record_b.provenance.env.get("hardware_class", "unknown")
    return hw_a == hw_b


def same_data_origin(record_a: Record, record_b: Record) -> bool:
    """Check if two records have the same data origin."""
    return record_a.provenance.data_origin == record_b.provenance.data_origin


def same_budget_tier(record_a: Record, record_b: Record) -> bool:
    """Check if two records use the same budget tier."""
    budget_a = _extract_budget(record_a)
    budget_b = _extract_budget(record_b)
    if budget_a is None or budget_b is None:
        return False
    return budget_a.kind == budget_b.kind


def valid_comparison(
    record_a: Record,
    record_b: Record,
    require_same_hardware: bool = True,
    require_same_data_origin: bool = True,
) -> tuple[bool, list[str]]:
    """Comprehensive comparison validity check.

    Returns (is_valid, list_of_violations).
    """
    violations = []

    if require_same_hardware and not same_hardware_class(record_a, record_b):
        violations.append("HARDWARE_CLASS_MISMATCH")

    if require_same_data_origin and not same_data_origin(record_a, record_b):
        violations.append("DATA_ORIGIN_MISMATCH")

    if not same_budget_tier(record_a, record_b):
        violations.append("BUDGET_TIER_MISMATCH")

    # Check that both are claim-eligible
    if not claim_eligible(record_a):
        violations.append("RECORD_A_NOT_CLAIM_ELIGIBLE")
    if not claim_eligible(record_b):
        violations.append("RECORD_B_NOT_CLAIM_ELIGIBLE")

    return len(violations) == 0, violations


# =============================================================================
# Data Split Guards (I(C,U) Leakage Protocol - WP5.5)
# =============================================================================


def is_exploration_data(record: Record) -> bool:
    """Check if record is from policy-independent exploration."""
    return record.provenance.data_origin == DataOrigin.EXPLORATION


def is_policy_selected_data(record: Record) -> bool:
    """Check if record is from policy-dependent selection."""
    return record.provenance.data_origin == DataOrigin.POLICY_SELECTED


def is_calibration_data(record: Record) -> bool:
    """Check if record is from calibration set (frozen, never used for policy tuning)."""
    return record.provenance.data_origin == DataOrigin.CALIBRATION


def is_test_data(record: Record) -> bool:
    """Check if record is from test set (held-out tasks, policy-independent)."""
    return record.provenance.data_origin == DataOrigin.TEST


def training_data_allowed(record: Record) -> bool:
    """Check if record can be used for surrogate training.

    Training data = exploration ∪ policy_selected
    """
    return is_exploration_data(record) or is_policy_selected_data(record)


def evaluation_data_allowed(record: Record) -> bool:
    """Check if record can be used for calibration/evaluation.

    Calibration/evaluation data = calibration ∪ test (policy-independent)
    """
    return is_calibration_data(record) or is_test_data(record)


def check_leakage(
    training_records: list[Record],
    evaluation_records: list[Record],
) -> tuple[bool, list[str]]:
    """Check for I(C,U) leakage between training and evaluation sets.

    Returns (no_leakage, list_of_violations).
    """
    violations = []

    # No test data in training
    for r in training_records:
        if is_test_data(r):
            violations.append(f"TEST_DATA_IN_TRAINING: {r.record_id}")

    # No calibration data in training (if policy-dependent)
    for r in training_records:
        if is_calibration_data(r):
            violations.append(f"CALIBRATION_DATA_IN_TRAINING: {r.record_id}")

    # Check for overlapping cell_keys (same coordinate measured differently)
    train_cells = {r.cell_key for r in training_records}
    eval_cells = {r.cell_key for r in evaluation_records}
    overlap = train_cells & eval_cells
    for cell in overlap:
        violations.append(f"CELL_KEY_OVERLAP: {cell}")

    return len(violations) == 0, violations


# =============================================================================
# Batch Predicates (for record stream processing)
# =============================================================================


def filter_claim_eligible(records: list[Record]) -> list[Record]:
    """Filter records to only claim-eligible ones."""
    return [r for r in records if claim_eligible(r)]


def filter_promoted(records: list[Record]) -> list[Record]:
    """Filter records to only promoted ones."""
    return [r for r in records if promoted(r)]


def filter_by_data_origin(records: list[Record], origin: DataOrigin) -> list[Record]:
    """Filter records by data origin."""
    return [r for r in records if r.provenance.data_origin == origin]


def filter_by_maturity(records: list[Record], maturity: str) -> list[Record]:
    """Filter records by maturity level."""
    return [r for r in records if r.status.maturity.value == maturity]


def group_by_cell_key(records: list[Record]) -> dict[str, list[Record]]:
    """Group records by cell_key (groups replications)."""
    groups: dict[str, list[Record]] = {}
    for r in records:
        groups.setdefault(r.cell_key, []).append(r)
    return groups


def group_by_replication_key(records: list[Record]) -> dict[str, list[Record]]:
    """Group records by replication_key (coordinate + schedule without seed)."""
    groups: dict[str, list[Record]] = {}
    for r in records:
        groups.setdefault(replication_key(r), []).append(r)
    return groups


__all__ = [
    "Alert",
    "AxisImpact",
    "Claim",
    "alert_on_constraint_violation",
    "alert_on_divergence",
    "alert_on_resource_exhaustion",
    "alert_on_stagnation",
    "beats_baseline",
    "check_all_alerts",
    "check_leakage",
    "claim_eligible",
    "claim_eligible_by_achieved_seeds",
    "claim_eligible_strict",
    "compare_matched_cost",
    "derive_claims",
    "evaluation_data_allowed",
    "filter_by_data_origin",
    "filter_by_maturity",
    "filter_claim_eligible",
    "filter_promoted",
    "generalizes",
    "group_by_cell_key",
    "group_by_replication_key",
    "is_calibration_data",
    "is_exploration_data",
    "is_policy_selected_data",
    "is_test_data",
    "promotable",
    "promoted",
    "replication_key",
    "robust",
    "same_budget_tier",
    "same_data_origin",
    "same_hardware_class",
    "strongest_axis",
    "training_data_allowed",
    "valid_comparison",
]
