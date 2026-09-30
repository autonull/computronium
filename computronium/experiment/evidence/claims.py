"""Full predicate suite for experiment claims and governance.

Implements WP5 deliverable: evidence/claims.py — full predicate suite:
- Claims (R35): claim_eligible predicate
- Promotion (R36): promotion predicate
- Alerts as record-stream predicates (R83/Q14)
- Matched-cost comparison guard (R65)
- Stratification guards (R8/R22/R67)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from computronium.experiment.schema.coordinate import DataOrigin

if TYPE_CHECKING:
    from computronium.experiment.evidence.protocol import ComparisonGuard, CostBudget
    from computronium.experiment.schema.record import Record


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


def claim_eligible_strict(record: Record, min_seeds: int = 5) -> bool:
    """Strict claim eligibility with configurable minimum seeds."""
    return (
        record.status.gate_verdict.value == "PASS"
        and not record.status.quarantine
        and record.schedule.fidelity == "L2"
        and record.schedule.n_seeds >= min_seeds
    )


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
        # Replication key excludes seed
        rep_key = f"{r.cell_key}|{r.schedule.fidelity}|{r.schedule.n_seeds}|{r.schedule.epochs}|{r.schedule.batch_limit}|{r.schedule.budget_id}"
        groups.setdefault(rep_key, []).append(r)
    return groups


__all__ = [
    "Alert",
    "alert_on_constraint_violation",
    "alert_on_divergence",
    "alert_on_resource_exhaustion",
    "alert_on_stagnation",
    "beats_baseline",
    "check_all_alerts",
    "check_leakage",
    "claim_eligible",
    "claim_eligible_strict",
    "compare_matched_cost",
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
    "robust",
    "same_budget_tier",
    "same_data_origin",
    "same_hardware_class",
    "training_data_allowed",
    "valid_comparison",
]
