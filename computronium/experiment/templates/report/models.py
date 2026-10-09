"""Pydantic models for report template context (Phase A).

Structured data models that feed Jinja2 templates for publication-grade reports.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.evidence.claims import Claim


class ReportMetadata(BaseModel):
    """Campaign metadata for report header."""

    model_config = ConfigDict(extra="forbid")

    campaign_name: str
    campaign_description: str | None = None
    generated_at: datetime = Field(default_factory=datetime.now)
    git_commit: str | None = None
    git_branch: str | None = None
    environment_hash: str | None = None
    hardware: str | None = None
    device: str | None = None
    time_budget_hours: float | None = None
    actual_duration_hours: float | None = None


class AxisCoverage(BaseModel):
    """Per-axis primitive coverage counts."""

    model_config = ConfigDict(extra="forbid")

    axis: str
    primitives: dict[str, int]  # primitive_name -> count
    total_cells: int
    unique_primitives: int


class ParetoPoint(BaseModel):
    """A single Pareto-optimal configuration."""

    model_config = ConfigDict(extra="forbid")

    rank: int
    objectives: dict[str, float]
    coordinate: dict[str, str]  # axis -> primitive
    record_id: str
    cell_key: str


class StabilityMetrics(BaseModel):
    """Stability analysis summary for a dynamics family."""

    model_config = ConfigDict(extra="forbid")

    dynamics: str
    n_samples: int
    lyapunov_exponent: dict[str, float] | None = None  # mean, std, min, max
    spectral_radius: dict[str, float] | None = None
    max_singular_value: dict[str, float] | None = None
    nonnormality: dict[str, float] | None = None
    stability_margin: dict[str, float] | None = None
    settle_steps: dict[str, float] | None = None
    converged_fraction: float | None = None


class FailureTaxonomy(BaseModel):
    """Failure categorization by cause."""

    model_config = ConfigDict(extra="forbid")

    cause: str
    count: int
    examples: list[str] = Field(default_factory=list)  # sample cell_keys


class Hypothesis(BaseModel):
    """A testable hypothesis derived from data or pre-registered."""

    model_config = ConfigDict(extra="forbid")

    id: str
    question: str
    prediction: str
    test: str
    min_effect_size: float
    required_power: float
    tags: list[str] = Field(default_factory=list)
    evidence: str | None = None
    pre_registered: bool = False


class StatisticalResult(BaseModel):
    """Statistical test result for a hypothesis."""

    model_config = ConfigDict(extra="forbid")

    hypothesis_id: str
    test_name: str
    p_value: float | None = None
    effect_size: float | None = None
    effect_size_type: str | None = None  # cohens_d, cliffs_delta, bayes_factor
    confidence_interval: tuple[float, float] | None = None
    significant: bool | None = None
    power_achieved: float | None = None
    n_samples: int
    notes: str | None = None


class AblationResult(BaseModel):
    """Per-axis ablation result."""

    model_config = ConfigDict(extra="forbid")

    axis: str
    metric: str
    fixed_axes: dict[str, str]  # other axes held constant
    values: list[dict[str, Any]]  # {axis_value, mean, std, count, min, max}


class CampaignConfig(BaseModel):
    """Complete campaign configuration for reproducibility."""

    model_config = ConfigDict(extra="forbid")

    # Factor design
    factors: dict[str, list[str]]
    fixed: dict[str, str]
    blocks: list[dict[str, Any]]

    # HPO settings
    sampler: str = "nsga2"
    objectives: list[str] = Field(default_factory=list)
    n_trials: int = 10
    n_seeds: int = 3
    epochs: int = 10

    # Resource limits
    max_wall_hours: float | None = None
    max_epoch_time_sec: int = 120


class ReproducibilityInfo(BaseModel):
    """Reproducibility block for report footer."""

    model_config = ConfigDict(extra="forbid")

    repro_command: str
    environment_hash: str | None = None
    export_json_path: str | None = None
    export_parquet_path: str | None = None
    checkpoint_paths: list[str] = Field(default_factory=list)


class ReportContext(BaseModel):
    """Complete context for report template rendering."""

    model_config = ConfigDict(extra="forbid")

    metadata: ReportMetadata
    axis_coverage: list[AxisCoverage]
    pareto_points: list[ParetoPoint] = Field(default_factory=list)
    stability_metrics: list[StabilityMetrics] = Field(default_factory=list)
    failure_taxonomy: list[FailureTaxonomy] = Field(default_factory=list)
    hypotheses: list[Hypothesis] = Field(default_factory=list)
    statistical_results: list[StatisticalResult] = Field(default_factory=list)
    ablation_results: list[AblationResult] = Field(default_factory=list)
    campaign_config: CampaignConfig | None = None
    reproducibility: ReproducibilityInfo | None = None
    executive_summary: str | None = None
    key_findings: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)

    def to_template_dict(self) -> dict[str, Any]:
        """Convert to dict for Jinja2 template."""
        return self.model_dump(mode="json")


# Template inheritance: domain-specific overrides
class VisionReportContext(ReportContext):
    """Extended context for vision domain reports."""

    model_config = ConfigDict(extra="forbid")

    architecture_comparison: list[dict[str, Any]] = Field(default_factory=list)
    flops_analysis: dict[str, float] | None = None


class RLReportContext(ReportContext):
    """Extended context for RL domain reports."""

    model_config = ConfigDict(extra="forbid")

    episode_rewards: list[float] = Field(default_factory=list)
    policy_entropy: dict[str, float] | None = None


class TabularReportContext(ReportContext):
    """Extended context for tabular domain reports."""

    model_config = ConfigDict(extra="forbid")

    feature_importance: dict[str, float] = Field(default_factory=dict)
    calibration_curve: list[dict[str, float]] = Field(default_factory=list)


class GraphReportContext(ReportContext):
    """Extended context for graph domain reports."""

    model_config = ConfigDict(extra="forbid")

    homophily_analysis: dict[str, float] | None = None
    over_smoothing_metrics: dict[str, float] | None = None


class LanguageReportContext(ReportContext):
    """Extended context for language domain reports."""

    model_config = ConfigDict(extra="forbid")

    perplexity_curve: list[float] = Field(default_factory=list)
    token_accuracy: dict[str, float] = Field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class TemplateConfig:
    """Template configuration for different output formats."""

    template_dir: Path
    base_template: str = "base.html.j2"
    domain_templates: dict[str, str] = Field(default_factory=dict)

    def __post_init__(self):
        if not self.domain_templates:
            object.__setattr__(
                self,
                "domain_templates",
                {
                    "vision": "vision.html.j2",
                    "rl": "rl.html.j2",
                    "tabular": "tabular.html.j2",
                    "graph": "graph.html.j2",
                    "language": "language.html.j2",
                },
            )