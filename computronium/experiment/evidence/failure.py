"""Failure analysis: taxonomy, clustering, and reproducer emission.

Implements WP5 deliverable: evidence/failure.py — FailureCause taxonomy,
clustering, reproducer emission, fix-linkage queries (R58–R62).
"""

from __future__ import annotations

import hashlib
import json
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from computronium.experiment.schema.record import FailureCause, Record

if TYPE_CHECKING:
    from computronium.experiment.evidence.store import RecordStore


# =============================================================================
# Failure Cluster Analysis
# =============================================================================


@dataclass(frozen=True, slots=True)
class FailureCluster:
    """A cluster of similar failures."""

    cluster_id: str
    failure_cause: FailureCause
    count: int
    cell_keys: tuple[str, ...]
    record_ids: tuple[str, ...]
    common_params: dict[str, Any]
    first_seen: str
    last_seen: str
    severity: str  # "low", "medium", "high", "critical"
    description: str


@dataclass(frozen=True, slots=True)
class FailurePattern:
    """A detected failure pattern with statistical significance."""

    pattern_id: str
    name: str
    failure_cause: FailureCause
    affected_coordinates: tuple[str, ...]  # coordinate signatures
    frequency: int
    confidence: float  # 0-1
    suggested_fix: str | None
    linked_fixes: tuple[str, ...]  # fix commit hashes or PR numbers


def cluster_failures(
    records: list[Record],
    min_cluster_size: int = 2,
) -> list[FailureCluster]:
    """Cluster failures by cause and coordinate similarity.

    Groups records with the same FailureCause and similar coordinates
    to identify systematic failure patterns.
    """
    # Group by failure cause
    by_cause: dict[FailureCause, list[Record]] = defaultdict(list)
    for r in records:
        if r.status.cause != FailureCause.UNKNOWN:
            by_cause[r.status.cause].append(r)

    clusters = []
    for cause, cause_records in by_cause.items():
        # Further cluster by coordinate similarity
        coord_groups = _group_by_coordinate_similarity(cause_records)

        for coord_sig, group in coord_groups.items():
            if len(group) >= min_cluster_size:
                cell_keys = tuple(r.cell_key for r in group)
                record_ids = tuple(r.record_id for r in group)

                # Extract common params
                common_params = _find_common_params(group)

                # Determine severity
                severity = _determine_severity(cause, len(group))

                # Generate cluster ID
                cluster_data = f"{cause.value}|{coord_sig}|{len(group)}"
                cluster_id = hashlib.sha256(cluster_data.encode()).hexdigest()[:12]

                timestamps = [
                    r.provenance.code_sha for r in group
                ]  # Using code_sha as proxy
                first_seen = (
                    min(timestamps) if timestamps else datetime.now().isoformat()
                )
                last_seen = (
                    max(timestamps) if timestamps else datetime.now().isoformat()
                )

                clusters.append(
                    FailureCluster(
                        cluster_id=cluster_id,
                        failure_cause=cause,
                        count=len(group),
                        cell_keys=cell_keys,
                        record_ids=record_ids,
                        common_params=common_params,
                        first_seen=first_seen,
                        last_seen=last_seen,
                        severity=severity,
                        description=_generate_cluster_description(
                            cause, group, common_params
                        ),
                    )
                )

    return sorted(clusters, key=lambda c: c.count, reverse=True)


def _group_by_coordinate_similarity(records: list[Record]) -> dict[str, list[Record]]:
    """Group records by coordinate signature (substrate, geometry, dynamics, plasticity, credit, update)."""
    groups: dict[str, list[Record]] = defaultdict(list)
    for r in records:
        coord_sig = f"{r.substrate}|{r.geometry}|{r.dynamics}|{r.plasticity}|{r.credit}|{r.update}"
        groups[coord_sig].append(r)
    return groups


def _find_common_params(records: list[Record]) -> dict[str, Any]:
    """Find parameter values common across all records in a group."""
    if not records:
        return {}

    # Start with first record's params
    common = dict(records[0].params)

    # Intersect with all other records
    for r in records[1:]:
        for key in list(common.keys()):
            if key not in r.params or r.params[key] != common[key]:
                del common[key]

    return common


def _determine_severity(cause: FailureCause, count: int) -> str:
    """Determine cluster severity based on cause and frequency."""
    critical_causes = {
        FailureCause.OOM,
        FailureCause.DIVERGENCE,
        FailureCause.NUMERICAL,
    }
    high_causes = {
        FailureCause.TIMEOUT,
        FailureCause.RUNTIME_ERROR,
        FailureCause.CONSTRAINT_VIOLATION,
    }

    if cause in critical_causes:
        return "critical" if count >= 3 else "high"
    if cause in high_causes:
        return "high" if count >= 5 else "medium"
    return "medium" if count >= 10 else "low"


def _generate_cluster_description(
    cause: FailureCause,
    records: list[Record],
    common_params: dict[str, Any],
) -> str:
    """Generate human-readable description of a failure cluster."""
    coord = records[0]
    param_str = (
        ", ".join(f"{k}={v}" for k, v in common_params.items())
        if common_params
        else "no common params"
    )
    return (
        f"{cause.value} in {coord.substrate}/{coord.geometry}/{coord.dynamics}/"
        f"{coord.plasticity}/{coord.credit}/{coord.update} "
        f"({len(records)} occurrences, common params: {param_str})"
    )


# =============================================================================
# Failure Pattern Detection (R58-R62)
# =============================================================================


def detect_failure_patterns(
    records: list[Record],
    min_frequency: int = 3,
    min_confidence: float = 0.7,
) -> list[FailurePattern]:
    """Detect statistically significant failure patterns.

    Analyzes failure clusters to find patterns that suggest
    systematic issues with specific coordinate combinations.
    """
    clusters = cluster_failures(records, min_cluster_size=min_frequency)
    patterns = []

    for cluster in clusters:
        # Calculate confidence based on cluster purity
        confidence = _calculate_pattern_confidence(cluster, records)

        if confidence >= min_confidence:
            # Generate pattern ID
            pattern_data = f"{cluster.failure_cause.value}|{cluster.cluster_id}"
            pattern_id = hashlib.sha256(pattern_data.encode()).hexdigest()[:12]

            # Get affected coordinate signatures
            affected_coords = tuple(
                f"{r.substrate}|{r.geometry}|{r.dynamics}|{r.plasticity}|{r.credit}|{r.update}"
                for r in records
                if r.cell_key in cluster.cell_keys
            )

            # Suggest fix based on cause
            suggested_fix = _suggest_fix(cluster.failure_cause, cluster.common_params)

            patterns.append(
                FailurePattern(
                    pattern_id=pattern_id,
                    name=f"{cluster.failure_cause.value}_pattern_{pattern_id[:6]}",
                    failure_cause=cluster.failure_cause,
                    affected_coordinates=affected_coords,
                    frequency=cluster.count,
                    confidence=confidence,
                    suggested_fix=suggested_fix,
                    linked_fixes=(),
                )
            )

    return sorted(patterns, key=lambda p: p.confidence * p.frequency, reverse=True)


def _calculate_pattern_confidence(
    cluster: FailureCluster, all_records: list[Record]
) -> float:
    """Calculate confidence that this is a real pattern, not random noise."""
    if not all_records:
        return 0.0

    # Proportion of records with this cause that are in this cluster
    cause_records = [r for r in all_records if r.status.cause == cluster.failure_cause]
    if not cause_records:
        return 0.0

    cluster_ratio = cluster.count / len(cause_records)

    # Boost confidence for larger clusters
    size_boost = min(cluster.count / 10.0, 0.3)

    return min(cluster_ratio + size_boost, 1.0)


def _suggest_fix(cause: FailureCause, common_params: dict[str, Any]) -> str | None:
    """Suggest a fix based on failure cause and common parameters."""
    suggestions = {
        FailureCause.OOM: "Reduce batch size, model size, or use gradient checkpointing",
        FailureCause.TIMEOUT: "Reduce max_epochs, batch_limit, or increase timeout budget",
        FailureCause.NUMERICAL: "Add gradient clipping, reduce learning rate, or use mixed precision",
        FailureCause.DIVERGENCE: "Reduce learning rate, add gradient clipping, or check initialization",
        FailureCause.INVALID_CONFIG: "Validate config against constraints before execution",
        FailureCause.CONSTRAINT_VIOLATION: "Adjust coordinate to satisfy constraints",
        FailureCause.RUNTIME_ERROR: "Check error logs for specific runtime issue",
    }
    return suggestions.get(cause)


# =============================================================================
# Reproducer Emission
# =============================================================================


@dataclass(frozen=True, slots=True)
class Reproducer:
    """A minimal reproducer for a failure."""

    reproducer_id: str
    record_id: str
    cell_key: str
    coordinate: dict[str, Any]
    schedule: dict[str, Any]
    params: dict[str, Any]
    failure_cause: FailureCause
    error_message: str
    minimal_config: dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_script(self) -> str:
        """Generate a standalone Python script to reproduce the failure."""
        lines = [
            "# Auto-generated failure reproducer",
            f"# Failure: {self.failure_cause.value}",
            f"# Record: {self.record_id}",
            f"# Cell: {self.cell_key}",
            f"# Generated: {self.created_at}",
            "",
            "import torch",
            "from computronium import (",
            "    compose_joint_system,",
            "    SystemTrainer,",
            "    SystemTrainerConfig,",
            "    create_task,",
            ")",
            "",
            "# Recreate the exact coordinate",
            f"coordinate = {json.dumps(self.coordinate, indent=2)}",
            f"schedule = {json.dumps(self.schedule, indent=2)}",
            f"params = {json.dumps(self.params, indent=2)}",
            "",
            "def main():",
            "    torch.manual_seed(schedule.get('seed', 42))",
            "    ",
            "    # Build system from coordinate",
            "    system = compose_joint_system(",
        ]

        # Add coordinate components
        lines.extend([
            "        substrate=coordinate['substrate'],",
            "        geometry=coordinate['geometry'],",
            "        dynamics=coordinate['dynamics'],",
            "        plasticity=coordinate['plasticity'],",
            "        credit=coordinate['credit'],",
            "        update=coordinate['update'],",
            "        params=params,",
            "    )",
            "",
            "    config = SystemTrainerConfig(",
            "        max_epochs=schedule.get('epochs', 10),",
            "        device='cpu',",
            "        seed=schedule.get('seed', 42),",
            "    )",
            "",
            "    task = create_task('mnist', device='cpu', quick_mode=True)",
            "    task.setup()",
            "    train_loader = task.get_dataloader('train')",
            "",
            "    def flatten(loader):",
            "        for x, y in loader:",
            "            yield x.view(x.size(0), -1), y",
            "",
            "    trainer = SystemTrainer(system=system, config=config, train_data=flatten(train_loader))",
            "    trainer.fit()",
            "",
            "if __name__ == '__main__':",
            "    main()",
        ])

        return "\n".join(lines)


def emit_reproducer(record: Record, error_message: str = "") -> Reproducer:
    """Emit a minimal reproducer for a failed record."""
    reproducer_data = (
        f"{record.record_id}|{record.cell_key}|{record.status.cause.value}"
    )
    reproducer_id = hashlib.sha256(reproducer_data.encode()).hexdigest()[:12]

    coordinate = {
        "substrate": record.substrate,
        "geometry": record.geometry,
        "dynamics": record.dynamics,
        "plasticity": record.plasticity,
        "credit": record.credit,
        "update": record.update,
    }

    schedule = record.schedule.to_dict()
    params = record.params

    # Create minimal config (only essential params)
    essential_params = {
        "lr",
        "learning_rate",
        "step_size",
        "beta",
        "hidden_dims",
        "input_dim",
        "output_dim",
    }
    minimal_config = {k: v for k, v in params.items() if k in essential_params}

    return Reproducer(
        reproducer_id=reproducer_id,
        record_id=record.record_id,
        cell_key=record.cell_key,
        coordinate=coordinate,
        schedule=schedule,
        params=params,
        failure_cause=record.status.cause,
        error_message=error_message or record.status.defect or "Unknown error",
        minimal_config=minimal_config,
    )


def save_reproducer(reproducer: Reproducer, output_dir: str) -> str:
    """Save reproducer as a Python script."""
    from pathlib import Path

    Path(output_dir).mkdir(exist_ok=True, parents=True)
    filename = f"reproducer_{reproducer.reproducer_id}.py"
    filepath = Path(output_dir) / filename

    with filepath.open("w", encoding="utf-8") as f:
        f.write(reproducer.to_script())

    return str(filepath)


# =============================================================================
# Fix Linkage Queries (R58-R62)
# =============================================================================


@dataclass(frozen=True, slots=True)
class FixLinkage:
    """Links a failure pattern to a fix."""

    pattern_id: str
    fix_commit: str
    fix_description: str
    fixed_at: str
    verified: bool = False
    verification_records: tuple[str, ...] = ()


class FixLinkageStore:
    """Run-scoped store for failure-pattern fix linkages (K10).

    Replaces the former module-global linkage dict; callers own the
    instance lifetime and inject it where linkage queries are needed.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._linkages: dict[str, list[FixLinkage]] = defaultdict(list)

    def link_fix(
        self, pattern_id: str, fix_commit: str, fix_description: str
    ) -> FixLinkage:
        """Link a fix (commit/PR) to a failure pattern."""
        linkage = FixLinkage(
            pattern_id=pattern_id,
            fix_commit=fix_commit,
            fix_description=fix_description,
            fixed_at=datetime.now().isoformat(),
        )
        with self._lock:
            self._linkages[pattern_id].append(linkage)
        return linkage

    def fixes_for_pattern(self, pattern_id: str) -> list[FixLinkage]:
        """Get all fixes linked to a failure pattern."""
        with self._lock:
            return list(self._linkages.get(pattern_id, []))

    def verify_fix(
        self, pattern_id: str, fix_commit: str, verification_record_ids: list[str]
    ) -> bool:
        """Mark a fix as verified with supporting record IDs."""
        with self._lock:
            for linkage in self._linkages.get(pattern_id, []):
                if linkage.fix_commit != fix_commit:
                    continue
                verified = FixLinkage(
                    pattern_id=linkage.pattern_id,
                    fix_commit=linkage.fix_commit,
                    fix_description=linkage.fix_description,
                    fixed_at=linkage.fixed_at,
                    verified=True,
                    verification_records=tuple(verification_record_ids),
                )
                idx = self._linkages[pattern_id].index(linkage)
                self._linkages[pattern_id][idx] = verified
                return True
            return False

    def unfixed_patterns(self, patterns: list[FailurePattern]) -> list[FailurePattern]:
        """Get patterns that have no linked fixes."""
        with self._lock:
            linked = set(self._linkages)
        return [p for p in patterns if p.pattern_id not in linked]


# =============================================================================
# Store Integration
# =============================================================================


def analyze_store_failures(
    store: RecordStore, fix_store: FixLinkageStore | None = None
) -> dict[str, Any]:
    """Run full failure analysis on a store."""
    # Get all failed records
    all_records = store.query_records()
    failed_records = [
        r
        for r in all_records
        if r.status.gate_verdict.value == "FAIL"
        or r.status.cause != FailureCause.UNKNOWN
    ]

    clusters = cluster_failures(failed_records)
    patterns = detect_failure_patterns(failed_records)

    # Generate reproducers for each cluster
    reproducers = []
    for cluster in clusters:
        # Get first record in cluster
        record = store.get_record_by_measurement_key(cluster.record_ids[0])
        if record:
            reproducer = emit_reproducer(record)
            reproducers.append(reproducer)

    return {
        "total_failures": len(failed_records),
        "clusters": [c.__dict__ for c in clusters],
        "patterns": [p.__dict__ for p in patterns],
        "reproducers": [r.__dict__ for r in reproducers],
        "unfixed_patterns": len(
            (fix_store or FixLinkageStore()).unfixed_patterns(patterns)
        ),
    }


__all__ = [
    "FailureCluster",
    "FailurePattern",
    "FixLinkage",
    "FixLinkageStore",
    "Reproducer",
    "analyze_store_failures",
    "cluster_failures",
    "detect_failure_patterns",
    "emit_reproducer",
    "save_reproducer",
]
