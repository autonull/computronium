"""Jinja2-based report generator (Phase A).

Generates publication-grade HTML/PDF reports from structured Pydantic context models.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from computronium.experiment.evidence.store import RecordStore
from computronium.experiment.surface.report import (
    ReportGenerator as SurfaceReportGenerator,
)
from computronium.experiment.templates.report.models import (
    AblationResult,
    AxisCoverage,
    CampaignConfig,
    FailureTaxonomy,
    Hypothesis,
    ParetoPoint,
    ReportContext,
    ReportMetadata,
    ReproducibilityInfo,
    StabilityMetrics,
    StatisticalResult,
    TemplateConfig,
)


class JinjaReportGenerator:
    """Generate reports using Jinja2 templates with Pydantic context."""

    def __init__(
        self,
        template_dir: Path | None = None,
        template_config: TemplateConfig | None = None,
    ):
        if template_dir is None:
            template_dir = Path(__file__).parent
        if template_config is None:
            template_config = TemplateConfig(template_dir=template_dir)

        self.template_dir = template_dir
        self.template_config = template_config
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        # Add custom filters
        self.env.filters["tojson"] = json.dumps

    def build_context_from_store(
        self,
        store: RecordStore,
        run_id: str,
        campaign_name: str | None = None,
        campaign_config: CampaignConfig | None = None,
        hypotheses: list[Hypothesis] | None = None,
        statistical_results: list[StatisticalResult] | None = None,
        executive_summary: str | None = None,
        key_findings: list[str] | None = None,
        limitations: list[str] | None = None,
        reproducibility: ReproducibilityInfo | None = None,
    ) -> ReportContext:
        """Build report context from record store data."""
        generator = SurfaceReportGenerator(store)

        # Get run summary
        run_summary = generator.run_summary(run_id)
        if run_summary is None:
            raise ValueError(f"Run {run_id} not found")

        # Metadata
        metadata = ReportMetadata(
            campaign_name=campaign_name or run_id,
            generated_at=datetime.now(),
            device=str(run_summary.spec.device) if run_summary.spec else "unknown",
            time_budget_hours=run_summary.budget_consumed_s / 3600 if run_summary.budget_consumed_s else None,
            actual_duration_hours=(
                (run_summary.finished_at - run_summary.started_at).total_seconds() / 3600
                if run_summary.finished_at and run_summary.started_at
                else None
            ),
        )

        # Axis coverage
        axis_coverage_data = generator.axis_coverage(run_id)
        axis_coverage = []
        for axis_name, primitives in axis_coverage_data.items():
            total = sum(primitives.values())
            axis_coverage.append(
                AxisCoverage(
                    axis=axis_name,
                    primitives=primitives,
                    total_cells=total,
                    unique_primitives=len(primitives),
                )
            )

        # Pareto frontier
        pareto_points = []
        pareto_data = generator.pareto_frontier(run_id)
        for i, point in enumerate(pareto_data):
            pareto_points.append(
                ParetoPoint(
                    rank=i + 1,
                    objectives=point["objectives"],
                    coordinate=point["coordinate"],
                    record_id=point["record_id"],
                    cell_key=point["cell_key"],
                )
            )

        # Stability metrics
        stability_metrics = self._extract_stability_metrics(generator, run_id)

        # Failure taxonomy
        failure_data = generator.failures_by_cause(run_id)
        failure_taxonomy = [
            FailureTaxonomy(cause=cause, count=count)
            for cause, count in sorted(failure_data.items(), key=lambda x: -x[1])
        ]

        # Ablation results
        ablation_results = self._compute_ablation_results(generator, run_id)

        return ReportContext(
            metadata=metadata,
            axis_coverage=axis_coverage,
            pareto_points=pareto_points,
            stability_metrics=stability_metrics,
            failure_taxonomy=failure_taxonomy,
            hypotheses=hypotheses or [],
            statistical_results=statistical_results or [],
            ablation_results=ablation_results,
            campaign_config=campaign_config,
            reproducibility=reproducibility,
            executive_summary=executive_summary,
            key_findings=key_findings or [],
            limitations=limitations or [],
        )

    def _extract_stability_metrics(
        self, generator: SurfaceReportGenerator, run_id: str
    ) -> list[StabilityMetrics]:
        """Extract stability metrics per dynamics family."""
        import statistics
        from collections import defaultdict

        records = generator.claim_eligible_records(run_id)
        if not records:
            records = generator._store.query_records(run_id=run_id)

        by_dynamics: dict[str, list[dict[str, float | str]]] = defaultdict(list)

        for r in records:
            metrics: dict[str, float | str] = {"dynamics": r.dynamics}
            for key in [
                "lyapunov_exponent",
                "spectral_radius",
                "max_singular_value",
                "nonnormality",
                "stability_margin",
                "settle_steps",
                "settle_converged",
            ]:
                val = r.payload.get(key)
                if val is not None:
                    metrics[key] = float(val)
            if any(k in metrics for k in ["lyapunov_exponent", "spectral_radius", "settle_steps"]):
                by_dynamics[r.dynamics].append(metrics)

        results = []
        for dynamics, samples in by_dynamics.items():
            def _stat(key: str) -> dict[str, float] | None:
                vals = [float(s[key]) for s in samples if key in s]
                if not vals:
                    return None
                return {
                    "mean": statistics.mean(vals),
                    "std": statistics.stdev(vals) if len(vals) > 1 else 0.0,
                    "min": min(vals),
                    "max": max(vals),
                }

            converge_vals = [bool(s.get("settle_converged", False)) for s in samples if "settle_converged" in s]
            converged_fraction = sum(converge_vals) / len(converge_vals) if converge_vals else None

            results.append(
                StabilityMetrics(
                    dynamics=dynamics,
                    n_samples=len(samples),
                    lyapunov_exponent=_stat("lyapunov_exponent"),
                    spectral_radius=_stat("spectral_radius"),
                    max_singular_value=_stat("max_singular_value"),
                    nonnormality=_stat("nonnormality"),
                    stability_margin=_stat("stability_margin"),
                    settle_steps=_stat("settle_steps"),
                    converged_fraction=converged_fraction,
                )
            )

        return results

    def _compute_ablation_results(
        self, generator: SurfaceReportGenerator, run_id: str
    ) -> list[AblationResult]:
        """Compute per-axis ablation tables."""
        import statistics
        from collections import defaultdict

        records = list(generator._store.query_records(run_id=run_id))
        if not records:
            return []

        ablation_axes = ["credit", "substrate", "plasticity", "dynamics", "update", "geometry"]
        primary_metrics = [
            "val_acc",
            "walltime_total",
            "param_count",
            "spectral_radius",
            "psi_capacity",
        ]

        results = []
        for axis in ablation_axes:
            axis_values = sorted(set(getattr(r, axis) for r in records))
            if len(axis_values) <= 1:
                continue

            for metric in primary_metrics:
                groups: dict[str, list[float]] = defaultdict(list)
                for r in records:
                    val = r.payload.get(metric)
                    if val is not None:
                        groups[getattr(r, axis)].append(float(val))

                if not groups:
                    continue

                values = []
                for axis_val in axis_values:
                    vals = groups.get(axis_val, [])
                    if vals:
                        values.append({
                            "axis_value": axis_val,
                            "mean": statistics.mean(vals),
                            "std": statistics.stdev(vals) if len(vals) > 1 else 0.0,
                            "count": len(vals),
                            "min": min(vals),
                            "max": max(vals),
                        })

                if values:
                    results.append(
                        AblationResult(
                            axis=axis,
                            metric=metric,
                            fixed_axes={},  # Could be enhanced with conditional ablations
                            values=values,
                        )
                    )

        return results

    def render_html(
        self,
        context: ReportContext,
        output_path: Path | str,
        template_name: str | None = None,
    ) -> Path:
        """Render HTML report from context."""
        template_name = template_name or self.template_config.base_template
        template = self.env.get_template(template_name)
        html = context.to_template_dict()
        html["plotly_js"] = True  # Include Plotly.js CDN
        rendered = template.render(**html)

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(rendered, encoding="utf-8")
        return output_file

    def render_latex(
        self,
        context: ReportContext,
        output_path: Path | str,
        template_name: str = "base.tex.j2",
    ) -> Path:
        """Render LaTeX report from context."""
        template = self.env.get_template(template_name)
        rendered = template.render(**context.to_template_dict())

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(rendered, encoding="utf-8")
        return output_file

    def render_pdf(
        self,
        context: ReportContext,
        output_path: Path | str,
        keep_tex: bool = False,
    ) -> Path:
        """Render PDF via LaTeX + pandoc."""
        tex_path = Path(output_path).with_suffix(".tex")
        self.render_latex(context, tex_path)

        output_file = Path(output_path)
        try:
            result = subprocess.run(
                [
                    "pandoc",
                    str(tex_path),
                    "-o",
                    str(output_file),
                    "--pdf-engine=xelatex",
                    "-V",
                    "geometry:margin=1in",
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode != 0:
                raise RuntimeError(f"pandoc failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            raise RuntimeError("pandoc timed out after 120 seconds")
        except FileNotFoundError:
            raise RuntimeError("pandoc not found. Install pandoc to generate PDF reports.")

        if not keep_tex and tex_path.exists():
            tex_path.unlink()

        return output_file


def generate_report_from_store(
    store_path: Path | str,
    run_id: str,
    output_path: Path | str,
    format: str = "html",
    campaign_name: str | None = None,
    campaign_config: CampaignConfig | None = None,
    hypotheses: list[Hypothesis] | None = None,
    statistical_results: list[StatisticalResult] | None = None,
    **kwargs,
) -> Path:
    """Convenience function to generate report from store."""
    from computronium.experiment.evidence.store import RecordStore, StoreConfig

    # Use regular connection (not read-only) to avoid conflicts with campaign runner
    store = RecordStore(StoreConfig(path=Path(store_path)))
    try:
        store.__enter__()  # Manually enter context
        generator = JinjaReportGenerator()
        context = generator.build_context_from_store(
            store=store,
            run_id=run_id,
            campaign_name=campaign_name,
            campaign_config=campaign_config,
            hypotheses=hypotheses,
            statistical_results=statistical_results,
            **kwargs,
        )

        if format == "html":
            return generator.render_html(context, output_path)
        elif format == "latex":
            return generator.render_latex(context, output_path)
        elif format == "pdf":
            return generator.render_pdf(context, output_path)
        else:
            raise ValueError(f"Unknown format: {format}")
    finally:
        try:
            store.__exit__(None, None, None)
        except Exception:
            pass  # Ignore cleanup errors


__all__ = [
    "JinjaReportGenerator",
    "TemplateConfig",
    "generate_report_from_store",
]
