"""Hypothesis registry and testing framework (Phase B).

Type-safe hypothesis definitions with pre-registration, statistical test specifications,
and power analysis integration.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

if TYPE_CHECKING:
    from collections.abc import Callable

from computronium.experiment.templates.report.models import Hypothesis as ReportHypothesis, StatisticalResult
from computronium.experiment.evidence.significance import Significance
from computronium.experiment.schema.axis import StructuralAxis


class TestType(str, Enum):
    """Supported statistical test types."""

    PAIRED_T_TEST = "paired_t_test"
    INDEPENDENT_T_TEST = "independent_t_test"
    MANN_WHITNEY_U = "mann_whitney_u"
    WILCOXON = "wilcoxon"
    ANOVA_ONE_WAY = "anova_one_way"
    ANOVA_TWO_WAY = "anova_two_way"
    KRUSKAL_WALLIS = "kruskal_wallis"
    CHI_SQUARE = "chi_square"
    FISHER_EXACT = "fisher_exact"
    BAYES_FACTOR = "bayes_factor"
    COHENS_D = "cohens_d"
    CLIFFS_DELTA = "cliffs_delta"
    CORRELATION_PEARSON = "correlation_pearson"
    CORRELATION_SPEARMAN = "correlation_spearman"
    LINEAR_REGRESSION = "linear_regression"
    LOGISTIC_REGRESSION = "logistic_regression"


class EffectSizeType(str, Enum):
    """Effect size measure types."""

    COHENS_D = "cohens_d"
    CLIFFS_DELTA = "cliffs_delta"
    ETA_SQUARED = "eta_squared"
    OMEGA_SQUARED = "omega_squared"
    R_SQUARED = "r_squared"
    BAYES_FACTOR = "bayes_factor"
    ODDS_RATIO = "odds_ratio"
    RISK_RATIO = "risk_ratio"


class MultipleComparisonCorrection(str, Enum):
    """Multiple comparison correction methods."""

    NONE = "none"
    BONFERRONI = "bonferroni"
    HOLM = "holm"
    BENJAMINI_HOCHBERG = "benjamini_hochberg"
    BENJAMINI_YEKUTIELI = "benjamini_yekutieli"
    SIDAK = "sidak"


class HypothesisStatus(str, Enum):
    """Hypothesis lifecycle status."""

    DRAFT = "draft"
    PRE_REGISTERED = "pre_registered"
    TESTED = "tested"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    INCONCLUSIVE = "inconclusive"


class HypothesisSpec(BaseModel):
    """Complete hypothesis specification with test parameters."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    # Identity
    id: str = Field(..., description="Unique hypothesis identifier")
    version: int = 1
    status: HypothesisStatus = HypothesisStatus.DRAFT

    # Scientific content
    question: str = Field(..., description="Research question")
    prediction: str = Field(..., description="Specific prediction")
    rationale: str | None = Field(None, description="Theoretical justification")

    # Test specification
    test_type: TestType
    primary_metric: str = Field(..., description="Primary outcome metric")
    grouping_factor: str | None = Field(None, description="Factor to group by (e.g., 'credit')")
    comparison_values: list[str] | None = Field(None, description="Specific values to compare")
    covariates: list[str] = Field(default_factory=list, description="Covariates to control for")

    # Statistical parameters
    min_effect_size: float = Field(..., gt=0, description="Minimum practically significant effect")
    effect_size_type: EffectSizeType = EffectSizeType.COHENS_D
    required_power: float = Field(..., ge=0.5, le=0.99, description="Required statistical power")
    alpha: float = Field(0.05, gt=0, le=0.1, description="Significance level")
    correction: MultipleComparisonCorrection = MultipleComparisonCorrection.NONE
    n_comparisons: int = Field(1, ge=1, description="Number of comparisons for correction")

    # Design parameters
    paired: bool = Field(False, description="Whether samples are paired")
    alternative: str = Field("two-sided", pattern="^(two-sided|greater|less)$")
    min_samples_per_group: int = Field(10, ge=2, description="Minimum samples per group")

    # Metadata
    tags: list[str] = Field(default_factory=list)
    domain: str | None = None
    pre_registered_at: datetime | None = None
    tested_at: datetime | None = None
    result: "HypothesisResult | None" = None

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        if not v or not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("ID must be alphanumeric with underscores/hyphens only")
        return v

    def to_report_hypothesis(self) -> ReportHypothesis:
        """Convert to report model."""
        return ReportHypothesis(
            id=self.id,
            question=self.question,
            prediction=self.prediction,
            test=self._render_test_spec(),
            min_effect_size=self.min_effect_size,
            required_power=self.required_power,
            tags=self.tags,
            evidence=self.rationale,
        )

    def _render_test_spec(self) -> str:
        """Render human-readable test specification."""
        parts = [self.test_type.value]
        if self.grouping_factor:
            parts.append(f"grouped by {self.grouping_factor}")
        if self.comparison_values:
            parts.append(f"comparing {', '.join(self.comparison_values)}")
        if self.covariates:
            parts.append(f"controlling for {', '.join(self.covariates)}")
        if self.paired:
            parts.append("(paired)")
        return " ".join(parts)

    def required_sample_size(self) -> int:
        """Calculate required sample size per group for target power.
        
        Uses approximate formula for two-sample t-test.
        For exact calculation, use specialized power analysis libraries.
        """
        import math
        from scipy import stats

        # Cohen's d to non-centrality parameter approximation
        # For two-sample t-test: n = 2 * (z_{1-alpha/2} + z_{power})^2 / d^2
        z_alpha = stats.norm.ppf(1 - self.alpha / 2)
        z_power = stats.norm.ppf(self.required_power)
        d = self.min_effect_size

        n_per_group = 2 * (z_alpha + z_power) ** 2 / (d ** 2)
        return math.ceil(n_per_group)


class HypothesisResult(BaseModel):
    """Result of hypothesis test."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    hypothesis_id: str
    test_type: TestType
    test_statistic: float | None = None
    p_value: float | None = None
    effect_size: float | None = None
    effect_size_type: EffectSizeType
    confidence_interval: tuple[float, float] | None = None
    significant: bool | None = None
    power_achieved: float | None = None
    n_samples: int
    n_groups: int
    groups_tested: list[str] = Field(default_factory=list)
    notes: str | None = None
    tested_at: datetime = Field(default_factory=datetime.now)
    raw_output: dict[str, Any] = Field(default_factory=dict)

    def to_statistical_result(self) -> "StatisticalResult":
        """Convert to report model."""
        from computronium.experiment.templates.report.models import StatisticalResult
        return StatisticalResult(
            hypothesis_id=self.hypothesis_id,
            test_name=self.test_type.value,
            p_value=self.p_value,
            effect_size=self.effect_size,
            effect_size_type=self.effect_size_type.value,
            confidence_interval=self.confidence_interval,
            significant=self.significant,
            power_achieved=self.power_achieved,
            n_samples=self.n_samples,
            notes=self.notes,
        )


class HypothesisRegistry:
    """Registry for managing hypotheses with persistence."""

    def __init__(self, storage_path: Path | None = None):
        self._hypotheses: dict[str, HypothesisSpec] = {}
        self._storage_path = storage_path or Path("experiments/hypotheses.json")
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    def _load(self) -> None:
        """Load hypotheses from storage."""
        if self._storage_path.exists():
            try:
                with self._storage_path.open() as f:
                    data = json.load(f)
                for item in data.get("hypotheses", []):
                    spec = HypothesisSpec(**item)
                    self._hypotheses[spec.id] = spec
            except Exception:
                pass  # Start fresh on corruption

    def _save(self) -> None:
        """Save hypotheses to storage."""
        data = {
            "version": 1,
            "saved_at": datetime.now().isoformat(),
            "hypotheses": [h.model_dump(mode="json") for h in self._hypotheses.values()],
        }
        with self._storage_path.open("w") as f:
            json.dump(data, f, indent=2, default=str)

    def register(self, hypothesis: HypothesisSpec) -> HypothesisSpec:
        """Register a new hypothesis."""
        if hypothesis.id in self._hypotheses:
            raise ValueError(f"Hypothesis {hypothesis.id} already exists. Use update() to modify.")
        self._hypotheses[hypothesis.id] = hypothesis
        self._save()
        return hypothesis

    def update(self, hypothesis: HypothesisSpec) -> HypothesisSpec:
        """Update an existing hypothesis."""
        if hypothesis.id not in self._hypotheses:
            raise ValueError(f"Hypothesis {hypothesis.id} not found. Use register() to create.")
        self._hypotheses[hypothesis.id] = hypothesis
        self._save()
        return hypothesis

    def get(self, hypothesis_id: str) -> HypothesisSpec | None:
        """Get hypothesis by ID."""
        return self._hypotheses.get(hypothesis_id)

    def list_all(self, status: HypothesisStatus | None = None) -> list[HypothesisSpec]:
        """List all hypotheses, optionally filtered by status."""
        hypotheses = list(self._hypotheses.values())
        if status:
            hypotheses = [h for h in hypotheses if h.status == status]
        return sorted(hypotheses, key=lambda h: h.id)

    def pre_register(self, hypothesis_id: str) -> HypothesisSpec:
        """Mark hypothesis as pre-registered."""
        hyp = self.get(hypothesis_id)
        if not hyp:
            raise ValueError(f"Hypothesis {hypothesis_id} not found")
        hyp.status = HypothesisStatus.PRE_REGISTERED
        hyp.pre_registered_at = datetime.now()
        self._save()
        return hyp

    def record_result(self, hypothesis_id: str, result: HypothesisResult) -> HypothesisSpec:
        """Record test result for hypothesis."""
        hyp = self.get(hypothesis_id)
        if not hyp:
            raise ValueError(f"Hypothesis {hypothesis_id} not found")
        hyp.status = (
            HypothesisStatus.CONFIRMED
            if result.significant
            else HypothesisStatus.REJECTED
            if result.significant is False
            else HypothesisStatus.INCONCLUSIVE
        )
        hyp.tested_at = datetime.now()
        hyp.result = result
        self._save()
        return hyp

    def export_to_yaml(self, output_path: Path) -> None:
        """Export hypotheses to YAML for campaign DSL."""
        import yaml

        data = {
            "hypotheses": [
                {
                    "id": h.id,
                    "question": h.question,
                    "prediction": h.prediction,
                    "test": h._render_test_spec(),
                    "min_effect_size": h.min_effect_size,
                    "required_power": h.required_power,
                    "tags": h.tags,
                    "pre_registered": h.status == HypothesisStatus.PRE_REGISTERED,
                }
                for h in self._hypotheses.values()
            ]
        }
        with output_path.open("w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    @classmethod
    def from_yaml(cls, path: Path) -> "HypothesisRegistry":
        """Create registry from YAML file."""
        import yaml

        registry = cls(storage_path=None)  # Don't load default
        with path.open() as f:
            data = yaml.safe_load(f)
        for item in data.get("hypotheses", []):
            spec = HypothesisSpec(
                id=item["id"],
                question=item["question"],
                prediction=item["prediction"],
                rationale=item.get("rationale"),
                test_type=TestType(item.get("test", "paired_t_test").split()[0]),
                primary_metric=item.get("primary_metric", "val_acc"),
                grouping_factor=item.get("grouping_factor"),
                comparison_values=item.get("comparison_values"),
                covariates=item.get("covariates", []),
                min_effect_size=item.get("min_effect_size", 0.5),
                required_power=item.get("required_power", 0.8),
                alpha=item.get("alpha", 0.05),
                n_comparisons=item.get("n_comparisons", 1),
                paired=item.get("paired", False),
                alternative=item.get("alternative", "two-sided"),
                min_samples_per_group=item.get("min_samples_per_group", 10),
                tags=item.get("tags", []),
                status=HypothesisStatus.PRE_REGISTERED if item.get("pre_registered") else HypothesisStatus.DRAFT,
            )
            registry._hypotheses[spec.id] = spec
        return registry


# Pre-defined hypothesis templates for common experiment types
CREDIT_EFFICIENCY_HYPOTHESIS = HypothesisSpec(
    id="H1_credit_efficiency",
    question="Does equilibrium_prop achieve comparable accuracy to gradient with lower energy_per_step?",
    prediction="eqprop energy_per_step < gradient energy_per_step at matched val_acc",
    rationale="Equilibrium propagation uses local updates that may be more energy-efficient than backprop",
    test_type=TestType.PAIRED_T_TEST,
    primary_metric="energy_per_step",
    grouping_factor="substrate",
    comparison_values=["gradient", "equilibrium_prop"],
    min_effect_size=0.5,
    required_power=0.8,
    alpha=0.05,
    n_comparisons=1,
    paired=True,
    alternative="two-sided",
    min_samples_per_group=10,
    tags=["credit", "energy", "efficiency"],
    status=HypothesisStatus.PRE_REGISTERED,
)

DYNAMICS_STABILITY_HYPOTHESIS = HypothesisSpec(
    id="H2_dynamics_stability",
    question="Do energy-minimization dynamics have larger basins but slower settling than predictive coding?",
    prediction="energy_minimization: larger basin_radius, higher settle_steps than predictive_settling",
    rationale="Energy minimization converges to fixed points; predictive coding uses iterative inference",
    test_type=TestType.MANN_WHITNEY_U,
    primary_metric="stability_margin",
    grouping_factor="dynamics",
    comparison_values=["energy_minimization", "predictive_settling"],
    min_effect_size=0.5,
    required_power=0.8,
    alpha=0.05,
    n_comparisons=1,
    paired=False,
    alternative="two-sided",
    min_samples_per_group=10,
    tags=["dynamics", "stability", "settling"],
    status=HypothesisStatus.PRE_REGISTERED,
)

SUBSTRATE_NOISE_HYPOTHESIS = HypothesisSpec(
    id="H3_substrate_noise_robustness",
    question="Do analog/memristive substrates degrade gracefully with noise while digital is brittle?",
    prediction="analog/memristive: gradual accuracy decline; digital: sharp drop at quantization threshold",
    rationale="Analog substrates have continuous state; digital has discrete thresholds",
    test_type=TestType.ANOVA_TWO_WAY,
    primary_metric="val_acc",
    grouping_factor="substrate",
    comparison_values=["digital", "analog", "memristive"],
    covariates=["noise_level"],
    min_effect_size=0.4,
    required_power=0.8,
    alpha=0.05,
    n_comparisons=3,
    paired=False,
    alternative="two-sided",
    min_samples_per_group=10,
    tags=["substrate", "noise", "robustness"],
    status=HypothesisStatus.PRE_REGISTERED,
)

PLASTICITY_FORGETTING_HYPOTHESIS = HypothesisSpec(
    id="H4_plasticity_catastrophic_forgetting",
    question="Does conflict_adaptive plasticity reduce catastrophic forgetting vs null/ewc?",
    prediction="conflict_adaptive forgetting < ewc forgetting < null forgetting on Split MNIST",
    rationale="Conflict-adaptive plasticity modulates updates based on gradient alignment",
    test_type=TestType.ANOVA_ONE_WAY,
    primary_metric="forgetting_rate",
    grouping_factor="plasticity",
    comparison_values=["null", "ewc", "conflict_adaptive"],
    min_effect_size=0.5,
    required_power=0.8,
    alpha=0.05,
    n_comparisons=3,
    paired=False,
    alternative="two-sided",
    min_samples_per_group=10,
    tags=["plasticity", "continual_learning", "forgetting"],
    status=HypothesisStatus.PRE_REGISTERED,
)

DEFAULT_HYPOTHESES = [
    CREDIT_EFFICIENCY_HYPOTHESIS,
    DYNAMICS_STABILITY_HYPOTHESIS,
    SUBSTRATE_NOISE_HYPOTHESIS,
    PLASTICITY_FORGETTING_HYPOTHESIS,
]


def create_default_registry() -> HypothesisRegistry:
    """Create registry with default hypotheses."""
    registry = HypothesisRegistry(storage_path=None)
    for hyp in DEFAULT_HYPOTHESES:
        registry._hypotheses[hyp.id] = hyp
    return registry


__all__ = [
    "HypothesisSpec",
    "HypothesisResult",
    "HypothesisRegistry",
    "TestType",
    "EffectSizeType",
    "MultipleComparisonCorrection",
    "HypothesisStatus",
    "CREDIT_EFFICIENCY_HYPOTHESIS",
    "DYNAMICS_STABILITY_HYPOTHESIS",
    "SUBSTRATE_NOISE_HYPOTHESIS",
    "PLASTICITY_FORGETTING_HYPOTHESIS",
    "DEFAULT_HYPOTHESES",
    "create_default_registry",
]