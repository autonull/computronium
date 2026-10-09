"""Campaign Design DSL with Pydantic validation (Phase B).

YAML-based campaign specification with full validation, factor design support,
power analysis integration, and automatic campaign YAML generation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class FactorType(str, Enum):
    """Types of experimental factors."""

    BETWEEN_SUBJECTS = "between_subjects"
    WITHIN_SUBJECTS = "within_subjects"
    COVARIATE = "covariate"
    BLOCKING = "blocking"


class DesignType(str, Enum):
    """Experimental design types."""

    FULL_FACTORIAL = "full_factorial"
    FRACTIONAL_FACTORIAL = "fractional_factorial"
    RESPONSE_SURFACE = "response_surface"
    PLACKETT_BURMAN = "plackett_burman"
    TAGUCHI = "taguchi"
    RANDOMIZED_BLOCK = "randomized_block"
    LATIN_SQUARE = "latin_square"
    ADAPTIVE = "adaptive"


class SamplerType(str, Enum):
    """HPO sampler types."""

    NSGA2 = "nsga2"
    TPE = "tpe"
    RANDOM = "random"
    GRID = "grid"
    SOBOL = "sobol"
    CMAES = "cmaes"


class ObjectiveDirection(str, Enum):
    """Objective optimization direction."""

    MAXIMIZE = "maximize"
    MINIMIZE = "minimize"


class ObjectiveSpec(BaseModel):
    """Single objective specification."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    name: str
    direction: ObjectiveDirection = ObjectiveDirection.MAXIMIZE
    weight: float = Field(1.0, gt=0)
    threshold: float | None = None


class FactorSpec(BaseModel):
    """Experimental factor specification."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    name: str
    type: FactorType = FactorType.BETWEEN_SUBJECTS
    values: list[Any] = Field(..., min_length=1)
    levels: int | None = None
    description: str | None = None

    @model_validator(mode="after")
    def validate_levels(self) -> "FactorSpec":
        if self.levels is not None and len(self.values) > 0:
            if len(self.values) == 2 and isinstance(self.values[0], int | float):
                pass
            elif len(self.values) != self.levels:
                raise ValueError(f"Factor {self.name}: {len(self.values)} values but {self.levels} levels specified")
        return self


class FixedFactorSpec(BaseModel):
    """Fixed factor (held constant across experiment)."""

    model_config = ConfigDict(extra="forbid")

    name: str
    value: Any
    description: str | None = None


class BlockSpec(BaseModel):
    """Experimental block specification."""

    model_config = ConfigDict(extra="forbid")

    task: str
    epochs: int = Field(..., gt=0)
    seeds: int = Field(..., gt=0)
    fidelity: str = "L0"
    budget_seconds: float | None = None
    description: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class PowerAnalysisSpec(BaseModel):
    """Power analysis configuration."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    min_effect_size: float = Field(0.5, gt=0)
    required_power: float = Field(0.8, ge=0.5, le=0.99)
    alpha: float = Field(0.05, gt=0, le=0.1)
    test_type: str = "paired_t_test"
    adaptive: bool = False
    futility_bound: float | None = None
    efficacy_bound: float | None = None
    interim_analyses: int = Field(0, ge=0)


class AnalysisSpec(BaseModel):
    """Analysis specification for campaign."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    primary: str = ""
    secondary: list[str] = Field(default_factory=list)
    stats: list[str] = Field(default_factory=lambda: ["cohens_d", "cliffs_delta", "bayes_factor"])
    visualizations: list[str] = Field(default_factory=lambda: ["pareto", "ablation", "convergence", "stability"])
    multiple_comparison_correction: str = "benjamini_hochberg"
    exploratory: bool = False


class CampaignMeta(BaseModel):
    """Campaign metadata."""

    model_config = ConfigDict(extra="forbid")

    name: str
    description: str = ""
    hypotheses: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: str | None = None
    version: str = "1.0"


class ResourceSpec(BaseModel):
    """Resource specification."""

    model_config = ConfigDict(extra="forbid")

    device: str = "auto"
    max_parallel: int = 1
    max_wall_hours: float | None = None
    max_epoch_time_sec: int = 120
    early_stop_patience: int = 10
    memory_limit_gb: float | None = None
    gpu_memory_fraction: float = 0.9


class SearchSpaceSpec(BaseModel):
    """Hyperparameter search space."""

    model_config = ConfigDict(extra="forbid")

    base: dict[str, list[Any] | dict[str, Any]] = Field(default_factory=dict)
    constraints: list[str] = Field(default_factory=list)


class ArmsSpec(BaseModel):
    """Arms specification for adaptive campaigns."""

    model_config = ConfigDict(extra="forbid")

    adaptive: dict[str, Any] = Field(default_factory=dict)


class HPOSpec(BaseModel):
    """Hyperparameter optimization specification."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    sampler: SamplerType = SamplerType.NSGA2
    objectives: list[ObjectiveSpec] = Field(default_factory=list)
    n_trials: int = Field(20, gt=0)
    n_startup_trials: int = Field(5, ge=0)
    n_seeds: int = Field(3, gt=0)
    seed: int = 42


class OutputSpec(BaseModel):
    """Output specification."""

    model_config = ConfigDict(extra="forbid")

    db: str = "experiment.db"
    artifacts_dir: str = "artifacts"
    log_level: str = "INFO"
    emit_every: int = 5
    export_formats: list[str] = Field(default_factory=lambda: ["json", "parquet"])


class ReproducibilitySpec(BaseModel):
    """Reproducibility specification."""

    model_config = ConfigDict(extra="forbid")

    seed: int = 42
    capture_env: bool = True
    artifact_hash: bool = True
    lock_file: str | None = None


class DesignSpec(BaseModel):
    """Experimental design specification."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    design_type: DesignType = DesignType.FULL_FACTORIAL
    factors: dict[str, FactorSpec] = Field(default_factory=dict)
    fixed: dict[str, FixedFactorSpec] = Field(default_factory=dict)
    blocks: list[BlockSpec] = Field(default_factory=list)
    power_analysis: PowerAnalysisSpec = Field(default_factory=lambda: PowerAnalysisSpec(min_effect_size=0.5, required_power=0.8, alpha=0.05, interim_analyses=0))
    fraction: int | None = None
    generators: list[str] = Field(default_factory=list)

    def required_sample_size(self) -> int:
        """Get required sample size from power analysis."""
        if self.power_analysis.enabled:
            from scipy import stats
            import math

            z_alpha = stats.norm.ppf(1 - self.power_analysis.alpha / 2)
            z_power = stats.norm.ppf(self.power_analysis.required_power)
            d = self.power_analysis.min_effect_size
            n = 2 * (z_alpha + z_power) ** 2 / (d ** 2)
            return math.ceil(n)
        return 10

    def generate_design_matrix(self) -> list[dict[str, Any]]:
        """Generate the design matrix (all factor combinations)."""
        import itertools

        factor_names = list(self.factors.keys())
        factor_values = [self.factors[name].values for name in factor_names]

        if self.design_type == DesignType.FULL_FACTORIAL:
            combinations = list(itertools.product(*factor_values))
        elif self.design_type == DesignType.FRACTIONAL_FACTORIAL:
            all_combinations = list(itertools.product(*factor_values))
            fraction = self.fraction or 2
            combinations = all_combinations[::fraction]
        else:
            combinations = list(itertools.product(*factor_values))

        design_matrix = []
        for combo in combinations:
            row = dict(zip(factor_names, combo))
            for name, fixed in self.fixed.items():
                row[name] = fixed.value
            design_matrix.append(row)

        return design_matrix


class CampaignDSL(BaseModel):
    """Complete campaign specification (DSL)."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    meta: CampaignMeta
    design: DesignSpec
    analysis: AnalysisSpec = Field(default_factory=lambda: AnalysisSpec())
    resources: ResourceSpec = Field(default_factory=lambda: ResourceSpec())
    search_space: SearchSpaceSpec = Field(default_factory=lambda: SearchSpaceSpec())
    arms: ArmsSpec = Field(default_factory=lambda: ArmsSpec())
    hpo: HPOSpec = Field(default_factory=lambda: HPOSpec(n_trials=20, n_startup_trials=5, n_seeds=3))
    output: OutputSpec = Field(default_factory=lambda: OutputSpec())
    reproducibility: ReproducibilitySpec = Field(default_factory=lambda: ReproducibilitySpec())

    def to_campaign_yaml(self, output_path: Path | str) -> Path:
        """Export to campaign YAML format for execution."""
        import yaml

        data = self.model_dump(mode="json", exclude_none=True)

        # Helper to get factor values
        def get_factor_values(axis_name: str) -> list[str]:
            factor = self.design.factors.get(axis_name)
            if factor:
                return factor.values
            fixed = self.design.fixed.get(axis_name)
            if fixed:
                return [fixed.value]
            return []

        # Filter invalid combinations: instantaneous dynamics + recurrent geometry + gradient credit
        def is_valid_geometry(geom: str, dyn: str, cred: str) -> bool:
            if dyn == "instantaneous" and geom in {"recurrent", "recurrent_attractor"}:
                if cred in {"gradient", "backprop"}:
                    return False
            return True

        # Generate runs from design blocks
        runs = []
        for i, block in enumerate(self.design.blocks):
            # Get factor values for each axis
            geometries = get_factor_values("geometry")
            dynamics = get_factor_values("dynamics")
            credits = get_factor_values("credit")

            # Filter geometries based on dynamics/credit compatibility
            # Check if any dynamic/credit combination would invalidate a geometry
            valid_geometries = []
            for geom in geometries:
                valid = True
                for dyn in dynamics:
                    for cred in credits:
                        if not is_valid_geometry(geom, dyn, cred):
                            valid = False
                            break
                    if not valid:
                        break
                if valid:
                    valid_geometries.append(geom)

            # Build overrides for this block
            overrides = {
                "substrates": get_factor_values("substrate"),
                "geometries": valid_geometries,
                "dynamics": get_factor_values("dynamics"),
                "credits": get_factor_values("credit"),
                "updates": get_factor_values("update"),
                "plasticities": get_factor_values("plasticity"),
                "tasks": [block.task],
                "hpo": {"n_trials": self.hpo.n_trials, "n_seeds": self.hpo.n_seeds},
                "epochs": block.epochs,
                "budget_seconds": block.budget_seconds or (self.resources.max_wall_hours * 3600 / max(1, len(self.design.blocks))) if self.resources.max_wall_hours else None,
            }
            # Add fixed factors to overrides (they override the factor values)
            for name, fixed in self.design.fixed.items():
                overrides[name] = fixed.value

            runs.append({
                "name": f"task_{block.task}" if i > 0 else "main",
                "profile": "production-map",
                "overrides": overrides,
                "depends_on": [0] if i > 0 else [],
                "device": self.resources.device,
                "store": self.output.db,
            })

        data["runs"] = runs
        data["store"] = self.output.db
        data["parallel"] = self.resources.max_parallel
        data["compute"] = {"device": self.resources.device, "max_parallel": self.resources.max_parallel}
        if self.resources.max_wall_hours:
            data["resources"] = {"max_wall_hours": self.resources.max_wall_hours}

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open("w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        return output_file

    def to_adaptive_budget_plan(self):
        """Convert to adaptive budget planner format."""
        from computronium.experiment.execution.adaptive_budget import (
            BudgetPlanner,
            BudgetStrategy,
            DeviceClass,
            plan_from_args,
        )

        strategy_map = {
            DesignType.FULL_FACTORIAL: BudgetStrategy.BALANCED,
            DesignType.FRACTIONAL_FACTORIAL: BudgetStrategy.BROAD_SHALLOW,
            DesignType.RESPONSE_SURFACE: BudgetStrategy.NARROW_DEEP,
            DesignType.ADAPTIVE: BudgetStrategy.BALANCED,
        }

        budget_hours = self.resources.max_wall_hours or 1.0
        device = DeviceClass.GPU if self.resources.device in ("auto", "cuda") else DeviceClass.CPU

        plan = plan_from_args(
            time_hours=budget_hours,
            strategy=strategy_map.get(self.design.design_type, BudgetStrategy.BALANCED).value,
            device=self.resources.device,
        )

        # Return a new plan with overridden parameters
        from dataclasses import replace
        return replace(
            plan,
            epochs=max(b.epochs for b in self.design.blocks) if self.design.blocks else 10,
            n_seeds=max(b.seeds for b in self.design.blocks) if self.design.blocks else 3,
            n_trials=self.hpo.n_trials,
        )

    @classmethod
    def from_yaml(cls, path: Path | str) -> "CampaignDSL":
        """Load campaign from YAML file."""
        import yaml

        with Path(path).open() as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def validate_design(self) -> list[str]:
        """Validate design and return warnings."""
        warnings = []

        if self.design.design_type == DesignType.FULL_FACTORIAL:
            n_combinations = 1
            for factor in self.design.factors.values():
                n_combinations *= len(factor.values)
            if n_combinations > 1000:
                warnings.append(f"Full factorial has {n_combinations} combinations - consider fractional factorial")

        if self.analysis.primary and self.design.power_analysis.enabled:
            required_n = self.design.required_sample_size()
            actual_n = min(b.seeds for b in self.design.blocks) if self.design.blocks else 1
            if actual_n < required_n:
                warnings.append(f"Power analysis requires {required_n} seeds per group, but design has {actual_n}")

        if self.resources.max_wall_hours:
            n_cells = 1
            for factor in self.design.factors.values():
                n_cells *= len(factor.values)
            est_hours = n_cells * self.hpo.n_trials * self.hpo.n_seeds * 0.01
            if est_hours > self.resources.max_wall_hours * 2:
                warnings.append(f"Estimated runtime ({est_hours:.1f}h) may exceed budget ({self.resources.max_wall_hours}h)")

        return warnings


def create_credit_efficiency_campaign(
    name: str = "credit_efficiency_comparison",
    time_budget_hours: float = 2.0,
    n_seeds: int = 10,
    epochs: int = 50,
) -> CampaignDSL:
    """Create the credit efficiency comparison campaign (Priority 1)."""
    return CampaignDSL(
        meta=CampaignMeta(
            name=name,
            description="Compare energy efficiency across credit assignments",
            hypotheses=["H1_credit_efficiency"],
            tags=["credit", "energy", "flagship"],
        ),
        design=DesignSpec(
            design_type=DesignType.FULL_FACTORIAL,
            factors={
                "credit": FactorSpec(
                    name="credit",
                    values=["gradient", "equilibrium_prop", "feedback_alignment", "pepita"],
                    type=FactorType.BETWEEN_SUBJECTS,
                ),
                "substrate": FactorSpec(
                    name="substrate",
                    values=["digital", "analog", "memristive"],
                    type=FactorType.BETWEEN_SUBJECTS,
                ),
                "dynamics": FactorSpec(
                    name="dynamics",
                    values=["energy_minimization", "predictive_settling"],
                    type=FactorType.BETWEEN_SUBJECTS,
                ),
            },
            fixed={
                "geometry": FixedFactorSpec(name="geometry", value="feedforward"),
                "update": FixedFactorSpec(name="update", value="adam"),
                "plasticity": FixedFactorSpec(name="plasticity", value="null"),
            },
            blocks=[
                BlockSpec(task="mnist", epochs=epochs, seeds=n_seeds),
                BlockSpec(task="fashion_mnist", epochs=epochs, seeds=n_seeds),
            ],
            power_analysis=PowerAnalysisSpec(
                enabled=True,
                min_effect_size=0.5,
                required_power=0.8,
                alpha=0.05,
                interim_analyses=0,
                adaptive=True,
                futility_bound=0.1,
            ),
        ),
        analysis=AnalysisSpec(
            primary="val_acc vs energy_per_step Pareto per substrate",
            secondary=["stability_margin", "settle_steps", "walltime_total"],
            stats=["cohens_d", "cliffs_delta", "bayes_factor"],
        ),
        resources=ResourceSpec(max_wall_hours=time_budget_hours, max_parallel=1),
        hpo=HPOSpec(
            n_trials=30,
            n_startup_trials=8,
            n_seeds=n_seeds,
            objectives=[
                ObjectiveSpec(name="val_acc", direction=ObjectiveDirection.MAXIMIZE, weight=1.0),
                ObjectiveSpec(name="energy_per_step", direction=ObjectiveDirection.MINIMIZE, weight=1.0),
                ObjectiveSpec(name="walltime_total", direction=ObjectiveDirection.MINIMIZE, weight=1.0),
            ],
        ),
    )


def create_dynamics_stability_campaign(
    name: str = "dynamics_stability_landscape",
    time_budget_hours: float = 3.0,
    n_seeds: int = 10,
    epochs: int = 50,
) -> CampaignDSL:
    """Create the dynamics stability landscape campaign (Priority 2)."""
    return CampaignDSL(
        meta=CampaignMeta(
            name=name,
            description="Characterize stability landscape across dynamics families",
            hypotheses=["H2_dynamics_stability"],
            tags=["dynamics", "stability", "flagship"],
        ),
        design=DesignSpec(
            design_type=DesignType.FULL_FACTORIAL,
            factors={
                "dynamics": FactorSpec(
                    name="dynamics",
                    values=["energy_minimization", "predictive_settling", "instantaneous", "equilibrium_prop"],
                    type=FactorType.BETWEEN_SUBJECTS,
                ),
                "credit": FactorSpec(
                    name="credit",
                    values=["gradient", "equilibrium_prop", "feedback_alignment"],
                    type=FactorType.BETWEEN_SUBJECTS,
                ),
                "substrate": FactorSpec(
                    name="substrate",
                    values=["digital"],
                    type=FactorType.BETWEEN_SUBJECTS,
                ),
            },
            fixed={
                "geometry": FixedFactorSpec(name="geometry", value="feedforward"),
                "update": FixedFactorSpec(name="update", value="adam"),
                "plasticity": FixedFactorSpec(name="plasticity", value="null"),
            },
            blocks=[BlockSpec(task="mnist", epochs=epochs, seeds=n_seeds)],
            power_analysis=PowerAnalysisSpec(enabled=True, min_effect_size=0.5, required_power=0.8, alpha=0.05, interim_analyses=0),
        ),
        analysis=AnalysisSpec(
            primary="Basin radius profiles, Lyapunov spectra, settling time distributions per dynamics",
            secondary=["spectral_radius", "max_singular_value", "nonnormality", "stability_margin"],
            stats=["cohens_d", "cliffs_delta", "bayes_factor"],
            visualizations=["stability", "pareto", "ablation", "trajectories"],
        ),
        resources=ResourceSpec(max_wall_hours=time_budget_hours),
        hpo=HPOSpec(
            n_trials=40,
            n_startup_trials=10,
            n_seeds=n_seeds,
            objectives=[
                ObjectiveSpec(name="val_acc", direction=ObjectiveDirection.MAXIMIZE, weight=1.0),
                ObjectiveSpec(name="stability_margin", direction=ObjectiveDirection.MAXIMIZE, weight=1.0),
                ObjectiveSpec(name="settle_steps", direction=ObjectiveDirection.MINIMIZE, weight=1.0),
            ],
        ),
    )


def create_substrate_noise_campaign(
    name: str = "substrate_noise_sensitivity",
    time_budget_hours: float = 4.0,
    n_seeds: int = 10,
    epochs: int = 50,
) -> CampaignDSL:
    """Create the substrate noise sensitivity campaign (Priority 3)."""
    return CampaignDSL(
        meta=CampaignMeta(
            name=name,
            description="Accuracy vs noise for analog/memristive/optical substrates",
            hypotheses=["H3_substrate_noise_robustness"],
            tags=["substrate", "noise", "robustness", "flagship"],
        ),
        design=DesignSpec(
            design_type=DesignType.FULL_FACTORIAL,
            factors={
                "substrate": FactorSpec(
                    name="substrate",
                    values=["digital", "analog", "memristive", "optical"],
                    type=FactorType.BETWEEN_SUBJECTS,
                ),
                "noise_level": FactorSpec(
                    name="noise_level",
                    values=[0.0, 0.01, 0.05, 0.1, 0.2],
                    type=FactorType.WITHIN_SUBJECTS,
                ),
                "credit": FactorSpec(
                    name="credit",
                    values=["gradient", "equilibrium_prop"],
                    type=FactorType.BETWEEN_SUBJECTS,
                ),
            },
            fixed={
                "geometry": FixedFactorSpec(name="geometry", value="feedforward"),
                "dynamics": FixedFactorSpec(name="dynamics", value="energy_minimization"),
                "update": FixedFactorSpec(name="update", value="adam"),
                "plasticity": FixedFactorSpec(name="plasticity", value="null"),
            },
            blocks=[BlockSpec(task="mnist", epochs=epochs, seeds=n_seeds)],
            power_analysis=PowerAnalysisSpec(enabled=True, min_effect_size=0.4, required_power=0.8, alpha=0.05, interim_analyses=0),
        ),
        analysis=AnalysisSpec(
            primary="Accuracy vs noise curves with error bars per substrate",
            secondary=["energy_per_step", "walltime_total", "stability_margin"],
            stats=["anova_two_way", "cohens_d", "cliffs_delta"],
            visualizations=["noise_curves", "substrate_comparison", "pareto"],
        ),
        resources=ResourceSpec(max_wall_hours=time_budget_hours),
        hpo=HPOSpec(
            n_trials=20,
            n_startup_trials=5,
            n_seeds=n_seeds,
            objectives=[
                ObjectiveSpec(name="val_acc", direction=ObjectiveDirection.MAXIMIZE, weight=1.0),
                ObjectiveSpec(name="robustness_slope", direction=ObjectiveDirection.MAXIMIZE, weight=1.0),
            ],
        ),
    )


def create_plasticity_forgetting_campaign(
    name: str = "plasticity_catastrophic_forgetting",
    time_budget_hours: float = 6.0,
    n_seeds: int = 10,
    epochs: int = 100,
) -> CampaignDSL:
    """Create the plasticity catastrophic forgetting campaign (Priority 4)."""
    return CampaignDSL(
        meta=CampaignMeta(
            name=name,
            description="Continual learning: Split MNIST, Permuted MNIST with plasticity variants",
            hypotheses=["H4_plasticity_catastrophic_forgetting"],
            tags=["plasticity", "continual_learning", "forgetting", "flagship"],
        ),
        design=DesignSpec(
            design_type=DesignType.FULL_FACTORIAL,
            factors={
                "plasticity": FactorSpec(
                    name="plasticity",
                    values=["null", "ewc", "synaptic_intelligence", "conflict_adaptive", "routing", "fast_weights"],
                    type=FactorType.BETWEEN_SUBJECTS,
                ),
                "task_sequence": FactorSpec(
                    name="task_sequence",
                    values=["split_mnist", "permuted_mnist", "rotated_mnist"],
                    type=FactorType.BETWEEN_SUBJECTS,
                ),
            },
            fixed={
                "substrate": FixedFactorSpec(name="substrate", value="digital"),
                "geometry": FixedFactorSpec(name="geometry", value="feedforward"),
                "dynamics": FixedFactorSpec(name="dynamics", value="instantaneous"),
                "credit": FixedFactorSpec(name="credit", value="gradient"),
                "update": FixedFactorSpec(name="update", value="adam"),
            },
            blocks=[
                BlockSpec(task="split_mnist", epochs=epochs, seeds=n_seeds),
                BlockSpec(task="permuted_mnist", epochs=epochs, seeds=n_seeds),
            ],
            power_analysis=PowerAnalysisSpec(enabled=True, min_effect_size=0.5, required_power=0.8, alpha=0.05, interim_analyses=0),
        ),
        analysis=AnalysisSpec(
            primary="Forgetting curves, forward/backward transfer metrics",
            secondary=["final_accuracy", "learning_speed", "parameter_efficiency"],
            stats=["anova_one_way", "cohens_d", "cliffs_delta", "bayes_factor"],
            visualizations=["forgetting_curves", "transfer_matrix", "pareto"],
        ),
        resources=ResourceSpec(max_wall_hours=time_budget_hours),
        hpo=HPOSpec(
            n_trials=15,
            n_startup_trials=4,
            n_seeds=n_seeds,
            objectives=[
                ObjectiveSpec(name="avg_final_acc", direction=ObjectiveDirection.MAXIMIZE, weight=1.0),
                ObjectiveSpec(name="forgetting_rate", direction=ObjectiveDirection.MINIMIZE, weight=1.0),
                ObjectiveSpec(name="forward_transfer", direction=ObjectiveDirection.MAXIMIZE, weight=1.0),
            ],
        ),
    )


CAMPAIGN_FACTORIES = {
    "credit_efficiency": create_credit_efficiency_campaign,
    "dynamics_stability": create_dynamics_stability_campaign,
    "substrate_noise": create_substrate_noise_campaign,
    "plasticity_forgetting": create_plasticity_forgetting_campaign,
}


def list_campaign_templates() -> list[str]:
    return list(CAMPAIGN_FACTORIES.keys())


def create_campaign(template_name: str, **kwargs) -> CampaignDSL:
    if template_name not in CAMPAIGN_FACTORIES:
        raise ValueError(f"Unknown template: {template_name}. Available: {list_campaign_templates()}")
    return CAMPAIGN_FACTORIES[template_name](**kwargs)


@dataclass(frozen=True, slots=True)
class DesignValidationResult:
    valid: bool
    errors: list[str]
    warnings: list[str]
    design_matrix_size: int
    estimated_runtime_hours: float
    required_seeds_per_group: int
    actual_seeds_per_group: int


def validate_campaign_design(campaign: CampaignDSL) -> DesignValidationResult:
    """Comprehensive design validation."""
    from computronium.experiment.execution.adaptive_budget import _is_valid_combination

    errors = []
    warnings = campaign.validate_design()

    design_matrix = campaign.design.generate_design_matrix()
    design_matrix_size = len(design_matrix)

    invalid_combos = []
    for row in design_matrix:
        if not _is_valid_combination(
            substrate=row.get("substrate", "digital"),
            geometry=row.get("geometry", "feedforward"),
            dynamics=row.get("dynamics", "energy_minimization"),
            credit=row.get("credit", "gradient"),
            update=row.get("update", "adam"),
            plasticity=row.get("plasticity", "null"),
        ):
            invalid_combos.append(row)

    if invalid_combos:
        warnings.append(f"{len(invalid_combos)} invalid combinations will be filtered at runtime")

    n_cells = design_matrix_size - len(invalid_combos)
    n_trials = campaign.hpo.n_trials
    n_seeds = campaign.hpo.n_seeds
    epochs = max(b.epochs for b in campaign.design.blocks) if campaign.design.blocks else 10

    estimated_hours = n_cells * n_trials * n_seeds * epochs * 0.0001

    required_seeds = campaign.design.required_sample_size()
    actual_seeds = min(b.seeds for b in campaign.design.blocks) if campaign.design.blocks else 1

    return DesignValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        design_matrix_size=design_matrix_size,
        estimated_runtime_hours=estimated_hours,
        required_seeds_per_group=required_seeds,
        actual_seeds_per_group=actual_seeds,
    )


__all__ = [
    "CampaignDSL",
    "CampaignMeta",
    "DesignSpec",
    "FactorSpec",
    "FixedFactorSpec",
    "BlockSpec",
    "PowerAnalysisSpec",
    "AnalysisSpec",
    "ResourceSpec",
    "SearchSpaceSpec",
    "ArmsSpec",
    "HPOSpec",
    "OutputSpec",
    "ReproducibilitySpec",
    "ObjectiveSpec",
    "FactorType",
    "DesignType",
    "SamplerType",
    "ObjectiveDirection",
    "DesignValidationResult",
    "validate_campaign_design",
    "CAMPAIGN_FACTORIES",
    "list_campaign_templates",
    "create_campaign",
    "create_credit_efficiency_campaign",
    "create_dynamics_stability_campaign",
    "create_substrate_noise_campaign",
    "create_plasticity_forgetting_campaign",
]