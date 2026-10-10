"""Automated Quality Gates (Phase F1).

Validates report quality, data integrity, and narrative coherence.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from computronium.experiment.templates.report.models import ReportContext

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class QualityIssue:
    """A quality issue found during validation."""

    severity: str  # error, warning, info
    category: str  # report, data, narrative, statistics, accessibility
    message: str
    location: str | None = None
    suggestion: str | None = None


@dataclass(frozen=True, slots=True)
class QualityReport:
    """Complete quality validation report."""

    passed: bool
    timestamp: str
    issues: list[QualityIssue] = field(default_factory=list)
    summary: dict[str, int] = field(default_factory=dict)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")

    @property
    def info_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "info")

    def to_json(self) -> str:
        return json.dumps(
            {
                "passed": self.passed,
                "timestamp": self.timestamp,
                "issues": [
                    {
                        "severity": i.severity,
                        "category": i.category,
                        "message": i.message,
                        "location": i.location,
                        "suggestion": i.suggestion,
                    }
                    for i in self.issues
                ],
                "summary": self.summary,
            },
            indent=2,
        )


class ReportQualityGate:
    """Validates report quality against publication standards."""

    def __init__(self) -> None:
        self.required_sections = [
            "abstract",
            "hypotheses",
            "methods",
            "results",
            "discussion",
            "limitations",
            "reproducibility",
        ]

    def validate(self, context: ReportContext) -> QualityReport:
        """Validate a report context."""
        issues: list[QualityIssue] = []

        # Check required sections
        issues.extend(self._check_required_sections(context))

        # Check metadata completeness
        issues.extend(self._check_metadata(context))

        # Check axis coverage
        issues.extend(self._check_axis_coverage(context))

        # Check Pareto points
        issues.extend(self._check_pareto_points(context))

        # Check stability metrics
        issues.extend(self._check_stability_metrics(context))

        # Check hypotheses
        issues.extend(self._check_hypotheses(context))

        # Check statistical results
        issues.extend(self._check_statistical_results(context))

        # Check reproducibility info
        issues.extend(self._check_reproducibility(context))

        # Check figures/tables
        issues.extend(self._check_figures_tables(context))

        # Check accessibility
        issues.extend(self._check_accessibility(context))

        # Build summary
        summary = {
            "total": len(issues),
            "errors": sum(1 for i in issues if i.severity == "error"),
            "warnings": sum(1 for i in issues if i.severity == "warning"),
            "info": sum(1 for i in issues if i.severity == "info"),
        }

        passed = summary["errors"] == 0

        return QualityReport(
            passed=passed,
            timestamp=datetime.now().isoformat(),
            issues=issues,
            summary=summary,
        )

    def _check_required_sections(self, context: ReportContext) -> list[QualityIssue]:
        issues = []
        for section in self.required_sections:
            if not getattr(context, section, None) and section != "limitations":
                issues.append(
                    QualityIssue(
                        severity="error",
                        category="report",
                        message=f"Missing required section: {section}",
                        location=section,
                        suggestion=f"Add {section} section to report context",
                    )
                )
        return issues

    def _check_metadata(self, context: ReportContext) -> list[QualityIssue]:
        issues = []
        meta = context.metadata

        required_meta = [
            "campaign_name",
            "generated_at",
            "device",
        ]

        for field in required_meta:
            if not getattr(meta, field, None):
                issues.append(
                    QualityIssue(
                        severity="warning",
                        category="report",
                        message=f"Missing metadata field: {field}",
                        location=f"metadata.{field}",
                        suggestion=f"Populate {field} in ReportMetadata",
                    )
                )

        if not meta.git_commit:
            issues.append(
                QualityIssue(
                    severity="warning",
                    category="report",
                    message="Missing git commit hash for reproducibility",
                    location="metadata.git_commit",
                    suggestion="Set git_commit in ReportMetadata",
                )
            )

        return issues

    def _check_axis_coverage(self, context: ReportContext) -> list[QualityIssue]:
        issues = []
        if not context.axis_coverage:
            issues.append(
                QualityIssue(
                    severity="error",
                    category="data",
                    message="No axis coverage data in report",
                    location="axis_coverage",
                    suggestion="Run axis_coverage() on store before generating report",
                )
            )
            return issues

        for axis in context.axis_coverage:
            if axis.unique_primitives == 0:
                issues.append(
                    QualityIssue(
                        severity="warning",
                        category="data",
                        message=f"No primitives exercised for axis: {axis.axis}",
                        location=f"axis_coverage.{axis.axis}",
                        suggestion="Check campaign design for missing axis values",
                    )
                )
            elif axis.unique_primitives == 1:
                issues.append(
                    QualityIssue(
                        severity="info",
                        category="data",
                        message=f"Only one primitive exercised for axis: {axis.axis}",
                        location=f"axis_coverage.{axis.axis}",
                        suggestion="Consider expanding axis values in campaign design",
                    )
                )

        return issues

    def _check_pareto_points(self, context: ReportContext) -> list[QualityIssue]:
        issues = []
        if not context.pareto_points:
            issues.append(
                QualityIssue(
                    severity="warning",
                    category="report",
                    message="No Pareto points in report",
                    location="pareto_points",
                    suggestion="Ensure campaign has completed runs with valid objectives",
                )
            )
        elif len(context.pareto_points) < 3:
            issues.append(
                QualityIssue(
                    severity="info",
                    category="report",
                    message=f"Few Pareto points ({len(context.pareto_points)})",
                    location="pareto_points",
                    suggestion="Run more diverse configurations for better Pareto front",
                )
            )

        for point in context.pareto_points:
            if not point.objectives:
                issues.append(
                    QualityIssue(
                        severity="error",
                        category="data",
                        message=f"Pareto point {point.rank} has no objectives",
                        location=f"pareto_points[{point.rank}]",
                    )
                )
            if not point.coordinate:
                issues.append(
                    QualityIssue(
                        severity="error",
                        category="data",
                        message=f"Pareto point {point.rank} has no coordinate",
                        location=f"pareto_points[{point.rank}]",
                    )
                )

        return issues

    def _check_stability_metrics(self, context: ReportContext) -> list[QualityIssue]:
        issues = []
        if not context.stability_metrics:
            issues.append(
                QualityIssue(
                    severity="info",
                    category="data",
                    message="No stability metrics in report",
                    location="stability_metrics",
                    suggestion="Run stability analysis if using non-instantaneous dynamics",
                )
            )
            return issues

        for metric in context.stability_metrics:
            if metric.n_samples < 5:
                issues.append(
                    QualityIssue(
                        severity="warning",
                        category="statistics",
                        message=f"Low sample count for {metric.dynamics} stability: {metric.n_samples}",
                        location=f"stability_metrics.{metric.dynamics}",
                        suggestion="Increase seeds or trials for statistical power",
                    )
                )

        return issues

    def _check_hypotheses(self, context: ReportContext) -> list[QualityIssue]:
        issues = []
        if not context.hypotheses:
            issues.append(
                QualityIssue(
                    severity="warning",
                    category="narrative",
                    message="No hypotheses in report",
                    location="hypotheses",
                    suggestion="Add pre-registered hypotheses from hypothesis registry",
                )
            )
            return issues

        for hyp in context.hypotheses:
            if not hyp.pre_registered:
                issues.append(
                    QualityIssue(
                        severity="info",
                        category="narrative",
                        message=f"Hypothesis {hyp.id} not pre-registered",
                        location=f"hypotheses.{hyp.id}",
                        suggestion="Pre-register hypotheses before campaign execution",
                    )
                )
            if not hyp.evidence:
                issues.append(
                    QualityIssue(
                        severity="warning",
                        category="narrative",
                        message=f"Hypothesis {hyp.id} has no evidence",
                        location=f"hypotheses.{hyp.id}",
                        suggestion="Link hypothesis to statistical results",
                    )
                )

        return issues

    def _check_statistical_results(self, context: ReportContext) -> list[QualityIssue]:
        issues = []
        if not context.statistical_results:
            issues.append(
                QualityIssue(
                    severity="warning",
                    category="statistics",
                    message="No statistical results in report",
                    location="statistical_results",
                    suggestion="Run hypothesis tests and add results",
                )
            )
            return issues

        for result in context.statistical_results:
            if result.p_value is None:
                issues.append(
                    QualityIssue(
                        severity="error",
                        category="statistics",
                        message=f"Missing p-value for {result.hypothesis_id}",
                        location=f"statistical_results.{result.hypothesis_id}",
                    )
                )
            elif result.p_value > 0.05 and result.significant:
                issues.append(
                    QualityIssue(
                        severity="error",
                        category="statistics",
                        message=f"Inconsistent significance for {result.hypothesis_id}: p={result.p_value} but marked significant",
                        location=f"statistical_results.{result.hypothesis_id}",
                    )
                )

            if (
                result.confidence_interval
                and result.confidence_interval[0] > result.confidence_interval[1]
            ):
                issues.append(
                    QualityIssue(
                        severity="error",
                        category="statistics",
                        message=f"Invalid confidence interval for {result.hypothesis_id}",
                        location=f"statistical_results.{result.hypothesis_id}",
                    )
                )

            if result.effect_size is not None and abs(result.effect_size) < 0.1:
                issues.append(
                    QualityIssue(
                        severity="info",
                        category="statistics",
                        message=f"Very small effect size for {result.hypothesis_id}: {result.effect_size}",
                        location=f"statistical_results.{result.hypothesis_id}",
                        suggestion="Consider if effect is practically significant",
                    )
                )

        return issues

    def _check_reproducibility(self, context: ReportContext) -> list[QualityIssue]:
        issues = []
        if not context.reproducibility:
            issues.append(
                QualityIssue(
                    severity="error",
                    category="reproducibility",
                    message="Missing reproducibility information",
                    location="reproducibility",
                    suggestion="Add ReproducibilityInfo with repro_command and export_json_path",
                )
            )
            return issues

        repro = context.reproducibility
        if not repro.repro_command:
            issues.append(
                QualityIssue(
                    severity="error",
                    category="reproducibility",
                    message="Missing reproducibility command",
                    location="reproducibility.repro_command",
                )
            )

        if not repro.export_json_path:
            issues.append(
                QualityIssue(
                    severity="warning",
                    category="reproducibility",
                    message="Missing export JSON path",
                    location="reproducibility.export_json_path",
                )
            )

        if not repro.environment_hash:
            issues.append(
                QualityIssue(
                    severity="warning",
                    category="reproducibility",
                    message="Missing environment hash",
                    location="reproducibility.environment_hash",
                )
            )

        return issues

    def _check_figures_tables(self, context: ReportContext) -> list[QualityIssue]:
        issues = []
        # Check if we have ablation results (which generate tables)
        if not context.ablation_results:
            issues.append(
                QualityIssue(
                    severity="info",
                    category="report",
                    message="No ablation results for tables",
                    location="ablation_results",
                )
            )

        # Check Pareto points for figure generation
        if context.pareto_points and len(context.pareto_points) > 1:
            pass  # Good for Pareto figures

        return issues

    def _check_accessibility(self, context: ReportContext) -> list[QualityIssue]:
        issues = []
        # Check for colorblind-safe color usage (would need template inspection)
        # This is a placeholder for template-level checks
        issues.append(
            QualityIssue(
                severity="info",
                category="accessibility",
                message="Verify colorblind-safe palette in HTML template",
                location="template",
                suggestion="Use colorblind-safe colors (viridis, plasma, etc.)",
            )
        )
        return issues


class DataIntegrityGate:
    """Validates data integrity in experiment stores."""

    def __init__(self, store_path: Path) -> None:
        self.store_path = store_path

    def validate(self) -> QualityReport:
        """Validate store data integrity."""
        issues: list[QualityIssue] = []

        try:
            from computronium.experiment.evidence.store import RecordStore, StoreConfig

            store = RecordStore(StoreConfig(path=self.store_path))
            with store:
                runs = store.query_runs()
                if not runs:
                    issues.append(
                        QualityIssue(
                            severity="error",
                            category="data",
                            message="No runs found in store",
                            location="store",
                        )
                    )
                    return QualityReport(
                        passed=False,
                        timestamp=datetime.now().isoformat(),
                        issues=issues,
                        summary={"total": 1, "errors": 1, "warnings": 0, "info": 0},
                    )

                for run in runs:
                    issues.extend(self._validate_run(store, run))

        except Exception as e:
            issues.append(
                QualityIssue(
                    severity="error",
                    category="data",
                    message=f"Failed to open store: {e}",
                    location="store",
                )
            )

        summary = {
            "total": len(issues),
            "errors": sum(1 for i in issues if i.severity == "error"),
            "warnings": sum(1 for i in issues if i.severity == "warning"),
            "info": sum(1 for i in issues if i.severity == "info"),
        }

        passed = summary["errors"] == 0

        return QualityReport(
            passed=passed,
            timestamp=datetime.now().isoformat(),
            issues=issues,
            summary=summary,
        )

    def _validate_run(self, store: Any, run: Any) -> list[QualityIssue]:
        issues = []
        records = list(store.query_records(run_id=run.run_id))

        if not records:
            issues.append(
                QualityIssue(
                    severity="warning",
                    category="data",
                    message=f"Run {run.run_id} has no records",
                    location=f"runs.{run.run_id}",
                )
            )
            return issues

        # Check for required fields
        for record in records:
            if not record.record_id:
                issues.append(
                    QualityIssue(
                        severity="error",
                        category="data",
                        message="Record missing record_id",
                        location=f"runs.{run.run_id}",
                    )
                )

            if not record.coordinate:
                issues.append(
                    QualityIssue(
                        severity="warning",
                        category="data",
                        message="Record missing coordinate",
                        location=f"runs.{run.run_id}.{record.record_id}",
                    )
                )

            # Check payload has expected metrics
            expected_metrics = ["val_acc", "walltime_total", "param_count"]
            for metric in expected_metrics:
                if metric not in record.payload:
                    issues.append(
                        QualityIssue(
                            severity="info",
                            category="data",
                            message=f"Record missing metric: {metric}",
                            location=f"runs.{run.run_id}.{record.record_id}",
                        )
                    )

        # Check for monotonicity (epoch progression)
        epochs = [
            r.payload.get("epoch")
            for r in records
            if r.payload.get("epoch") is not None
        ]
        if epochs and sorted(epochs) != epochs:
            issues.append(
                QualityIssue(
                    severity="warning",
                    category="data",
                    message="Non-monotonic epoch progression",
                    location=f"runs.{run.run_id}",
                )
            )

        return issues


class NarrativeCoherenceGate:
    """Validates narrative coherence: hypothesis -> result traceability."""

    def validate(self, context: ReportContext) -> QualityReport:
        issues: list[QualityIssue] = []

        if not context.hypotheses:
            issues.append(
                QualityIssue(
                    severity="warning",
                    category="narrative",
                    message="No hypotheses to trace",
                    location="hypotheses",
                )
            )
            return QualityReport(
                passed=True,
                timestamp=datetime.now().isoformat(),
                issues=issues,
                summary={
                    "total": len(issues),
                    "errors": 0,
                    "warnings": len(issues),
                    "info": 0,
                },
            )

        if not context.statistical_results:
            issues.append(
                QualityIssue(
                    severity="error",
                    category="narrative",
                    message="Has hypotheses but no statistical results",
                    location="statistical_results",
                    suggestion="Run hypothesis tests to close the loop",
                )
            )

        # Check each hypothesis has a result
        hyp_ids = {h.id for h in context.hypotheses}
        result_ids = {r.hypothesis_id for r in context.statistical_results}

        for hyp_id in hyp_ids:
            if hyp_id not in result_ids:
                issues.append(
                    QualityIssue(
                        severity="error",
                        category="narrative",
                        message=f"Hypothesis {hyp_id} has no corresponding statistical result",
                        location=f"hypotheses.{hyp_id}",
                    )
                )

        for result_id in result_ids:
            if result_id not in hyp_ids:
                issues.append(
                    QualityIssue(
                        severity="warning",
                        category="narrative",
                        message=f"Statistical result {result_id} has no corresponding hypothesis",
                        location=f"statistical_results.{result_id}",
                    )
                )

        summary = {
            "total": len(issues),
            "errors": sum(1 for i in issues if i.severity == "error"),
            "warnings": sum(1 for i in issues if i.severity == "warning"),
            "info": sum(1 for i in issues if i.severity == "info"),
        }

        passed = summary["errors"] == 0

        return QualityReport(
            passed=passed,
            timestamp=datetime.now().isoformat(),
            issues=issues,
            summary=summary,
        )


def run_all_quality_gates(
    report_context: ReportContext | None = None,
    store_path: Path | None = None,
) -> QualityReport:
    """Run all quality gates and aggregate results."""
    all_issues: list[QualityIssue] = []

    if report_context:
        report_gate = ReportQualityGate()
        report_result = report_gate.validate(report_context)
        all_issues.extend(report_result.issues)

        narrative_gate = NarrativeCoherenceGate()
        narrative_result = narrative_gate.validate(report_context)
        all_issues.extend(narrative_result.issues)

    if store_path:
        data_gate = DataIntegrityGate(store_path)
        data_result = data_gate.validate()
        all_issues.extend(data_result.issues)

    summary = {
        "total": len(all_issues),
        "errors": sum(1 for i in all_issues if i.severity == "error"),
        "warnings": sum(1 for i in all_issues if i.severity == "warning"),
        "info": sum(1 for i in all_issues if i.severity == "info"),
    }

    passed = summary["errors"] == 0

    return QualityReport(
        passed=passed,
        timestamp=datetime.now().isoformat(),
        issues=all_issues,
        summary=summary,
    )


__all__ = [
    "DataIntegrityGate",
    "NarrativeCoherenceGate",
    "QualityIssue",
    "QualityReport",
    "ReportQualityGate",
    "run_all_quality_gates",
]
