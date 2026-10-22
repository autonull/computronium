"""Jinja2-based report generator (Phase A).

Generates publication-grade HTML/PDF reports from structured Pydantic context models.
"""

from __future__ import annotations

import contextlib
import json
import subprocess
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from computronium.experiment.analysis import (
    SeedVariabilityConfig,
    compare_hardware_performance,
    compute_hypervolume,
    compute_scalarization_sweep,
    compute_seed_variability,
    verify_bitwise_reproducibility,
)
from computronium.experiment.analysis import (
    compute_pareto_frontier as analysis_compute_pareto_frontier,
)
from computronium.experiment.analysis.hardware_variance import HardwareVarianceConfig
from computronium.experiment.evidence.limitations import derive_limitations
from computronium.experiment.evidence.store import RecordStore
from computronium.experiment.surface.report import (
    ReportGenerator as SurfaceReportGenerator,
)
from computronium.experiment.surface.report import (
    _maximizes,
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
            time_budget_hours=run_summary.budget_consumed_s / 3600
            if run_summary.budget_consumed_s
            else None,
            actual_duration_hours=(
                (run_summary.finished_at - run_summary.started_at).total_seconds()
                / 3600
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

        # Advanced Analysis (Phase 4)
        statistical_results = self._extract_statistical_results(generator, run_id)
        limitations = self._extract_limitations(generator, run_id)

        return ReportContext(
            metadata=metadata,
            axis_coverage=axis_coverage,
            pareto_points=pareto_points,
            stability_metrics=stability_metrics,
            failure_taxonomy=failure_taxonomy,
            hypotheses=hypotheses or [],
            statistical_results=statistical_results,
            ablation_results=ablation_results,
            campaign_config=campaign_config,
            reproducibility=reproducibility,
            executive_summary=executive_summary,
            key_findings=key_findings or [],
            limitations=limitations,
        )

    def _extract_limitations(
        self, generator: SurfaceReportGenerator, run_id: str
    ) -> list[str]:
        """Extract limitations from the run records."""

        records = generator._store.query_records(run_id=run_id)
        if not records:
            return []

        spec = generator._spec(run_id)
        achieved = generator.achieved_seeds(run_id)
        claims = generator.claims(run_id)

        limitations = derive_limitations(
            records,
            achieved=achieved,
            n_seeds=spec.n_seeds if spec else None,
            fidelity=spec.fidelity if spec else None,
            objectives=spec.objectives if spec else (),
            claim_count=len(claims),
        )
        return [f"[{lim.kind}] {lim.detail}" for lim in limitations]

    def _extract_statistical_results(
        self, generator: SurfaceReportGenerator, run_id: str
    ) -> list[StatisticalResult]:
        """Extract statistical analysis results from the run."""

        records = generator.claim_eligible_records(run_id)
        if not records:
            return []

        results = []

        # Pareto Analysis with Hypervolume
        spec = generator._spec(run_id)
        if spec and spec.objectives:
            objectives = list(spec.objectives[:3])
            maximize = tuple(_maximizes(obj) for obj in objectives)
            try:
                pareto_points, dominated = analysis_compute_pareto_frontier(
                    records, objectives, list(maximize)
                )
                if pareto_points:
                    hv = compute_hypervolume(pareto_points, objectives, list(maximize))
                    scalarization = compute_scalarization_sweep(
                        records, objectives, list(maximize), n_weight_samples=10
                    )
                    results.append(
                        StatisticalResult(
                            hypothesis_id="pareto_analysis",
                            test_name="hypervolume",
                            p_value=None,
                            effect_size=float(hv),
                            effect_size_type="hypervolume",
                            confidence_interval=None,
                            significant=hv > 0,
                            power_achieved=None,
                            n_samples=len(records),
                            notes=f"Pareto points: {len(pareto_points)}/{len(pareto_points) + len(dominated)}; Scalarization sweeps: {len(scalarization)}",
                        )
                    )
            except Exception:
                pass

        # Seed Variability
        try:
            for metric in ["val_acc", "walltime_total"]:
                if any(metric in r.payload for r in records):
                    sv_result = compute_seed_variability(
                        records,
                        metric,
                        SeedVariabilityConfig(
                            min_seeds_per_group=2, confidence_level=0.95
                        ),
                    )
                    results.append(
                        StatisticalResult(
                            hypothesis_id=f"seed_variability_{metric}",
                            test_name="anova_seed_effect",
                            p_value=sv_result.seed_effect_pvalue,
                            effect_size=sv_result.coefficient_of_variation,
                            effect_size_type="coefficient_of_variation",
                            confidence_interval=(
                                sv_result.overall_mean - 1.96 * sv_result.overall_std,
                                sv_result.overall_mean + 1.96 * sv_result.overall_std,
                            ),
                            significant=sv_result.seed_effect_pvalue < 0.05,
                            power_achieved=None,
                            n_samples=len(records),
                            notes=f"Groups: {sv_result.metadata.get('n_groups', 0)}",
                        )
                    )
        except Exception:
            pass

        # Hardware Variance
        try:
            device_field = "device"
            records_by_device: dict[str, list] = {}
            for r in records:
                device = getattr(r, device_field, "unknown")
                records_by_device.setdefault(device, []).append(r)
            if len(records_by_device) > 1:
                hv_result = compare_hardware_performance(
                    records_by_device,
                    "val_acc",
                    HardwareVarianceConfig(
                        min_seeds_per_device=2, confidence_level=0.95
                    ),
                )
                results.append(
                    StatisticalResult(
                        hypothesis_id="hardware_variance",
                        test_name="anova_device_effect",
                        p_value=hv_result.device_effect_pvalue,
                        effect_size=None,
                        effect_size_type=None,
                        confidence_interval=None,
                        significant=hv_result.device_effect_pvalue < 0.05,
                        power_achieved=None,
                        n_samples=len(records),
                        notes=f"Devices: {len(hv_result.devices)}",
                    )
                )
        except Exception:
            pass

        # Reproducibility
        try:
            rep_result = verify_bitwise_reproducibility(run_id, generator._store)
            results.append(
                StatisticalResult(
                    hypothesis_id="reproducibility",
                    test_name="bitwise_replay",
                    p_value=None,
                    effect_size=1.0 if rep_result.metrics_match else 0.0,
                    effect_size_type="match_rate",
                    confidence_interval=None,
                    significant=rep_result.metrics_match,
                    power_achieved=None,
                    n_samples=1,
                    notes=f"Replay hash: {rep_result.metadata.get('has_replay_hash', False)}; Bitwise: {rep_result.bitwise_match}",
                )
            )
        except Exception:
            pass

        return results

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
            if any(
                k in metrics
                for k in ["lyapunov_exponent", "spectral_radius", "settle_steps"]
            ):
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

            converge_vals = [
                bool(s.get("settle_converged", False))
                for s in samples
                if "settle_converged" in s
            ]
            converged_fraction = (
                sum(converge_vals) / len(converge_vals) if converge_vals else None
            )

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
        """Per-axis ablation tables, only for shared-five-axes contrast groups."""
        from computronium.experiment.surface.report import (
            _ABLATION_AXES,
            _ABLATION_METRICS,
            _STRUCTURAL_AXES,
            _row_stats,
            chance_level,
            contrast_groups,
        )

        records = list(generator._store.query_records(run_id=run_id))
        if not records:
            return []

        results = []
        for axis in _ABLATION_AXES:
            for group in contrast_groups(records, axis):
                representative = next(iter(group.values()))[0]
                task_id = representative.schedule.task_id
                fixed_axes = {
                    name: getattr(representative, name)
                    for name in _STRUCTURAL_AXES
                    if name != axis
                }
                for metric in _ABLATION_METRICS:
                    present = {
                        value: arm
                        for value, arm in group.items()
                        if any(metric in record.payload for record in arm)
                    }
                    if not present:
                        continue
                    chance = chance_level(task_id, metric)
                    values = []
                    for axis_value, arm in sorted(present.items()):
                        mean, std, n, at_chance = _row_stats(arm, metric, chance)
                        values.append({
                            "axis_value": axis_value,
                            "mean": mean,
                            "std": std,
                            "count": n,
                            "at_chance": at_chance,
                        })
                    if values:
                        results.append(
                            AblationResult(
                                axis=axis,
                                metric=metric,
                                fixed_axes=fixed_axes,
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
            raise RuntimeError(
                "pandoc not found. Install pandoc to generate PDF reports."
            )

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
        with contextlib.suppress(Exception):
            store.__exit__(None, None, None)


__all__ = [
    "JinjaReportGenerator",
    "TemplateConfig",
    "generate_report_from_store",
]
