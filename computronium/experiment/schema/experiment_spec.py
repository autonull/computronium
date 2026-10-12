"""Unified ExperimentSpec: declarative specification for all experiment types.

A single source of truth for experiment configuration that can be loaded from
YAML/JSON and used by the CLI to run any experiment type (showcase, ablation,
scaling, comparison, replay, multi-task).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field, model_validator

from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.registries import OBJECTIVES_REGISTRY
from computronium.experiment.schema.run_spec import AxisSelection, Fidelity, RunSpec

if TYPE_CHECKING:
    from computronium.experiment.schema.coordinate import Coordinate
else:
    # For Pydantic runtime type resolution
    from computronium.experiment.schema.coordinate import Coordinate


class ExperimentType(StrEnum):
    """Type of experiment to run."""

    SHOWCASE = "showcase"  # Full production map
    ABLATION = "ablation"  # Single-axis sweep
    SCALING = "scaling"  # Depth/width/budget sweeps
    COMPARISON = "comparison"  # A/B testing
    REPLAY = "replay"  # Regression from DB
    MULTI_TASK = "multi_task"  # Multi-task coverage


class SearchStrategy(StrEnum):
    """Search strategy for exploring the space."""

    GRID = "grid"  # Full factorial grid
    ROUND_ROBIN = "round_robin"  # Round-robin across tasks
    RANDOM = "random"  # Random sampling
    BAYESIAN = "bayesian"  # Bayesian optimization (future)


class Gate(StrEnum):
    """Gates that must pass before/during/after experiment."""

    DRY_RUN = "dry_run"
    PROPERTY_LOCKS = "property_locks"
    ADMISSION = "admission"
    FAIRNESS = "fairness"


class Reporter(StrEnum):
    """Output reporters."""

    HTML = "html"
    JSON = "json"
    SQLITE = "sqlite"
    TENSORBOARD = "tensorboard"


class Budget(BaseModel):
    """Budget configuration for an experiment."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    seconds: float | None = None  # Walltime budget
    max_cells: int | None = None  # Maximum cells to evaluate
    param_budget: int = 10000  # Parameter ceiling per cell

    @classmethod
    def default(cls) -> Budget:
        return cls()


@dataclass(frozen=True, slots=True)
class AblationConfig:
    """Configuration for ablation experiment type."""

    vary: StructuralAxis
    fix: dict[StructuralAxis, str] = field(default_factory=dict)
    n_seeds: int = 5
    metric: str = "validation_accuracy"


@dataclass(frozen=True, slots=True)
class ScalingConfig:
    """Configuration for scaling experiment type."""

    vary: list[str] = field(
        default_factory=lambda: ["hidden_dims", "param_budget", "settle_horizon"]
    )
    log_scale: bool = True
    n_points_per_dim: int = 4
    base_config: Coordinate | None = None
    metric: str = "validation_accuracy"


@dataclass(frozen=True, slots=True)
class ComparisonConfig:
    """Configuration for comparison (A/B) experiment type."""

    arm_a: dict[StructuralAxis, str]
    arm_b: dict[StructuralAxis, str]
    n_seeds: int = 10
    metric: str = "validation_accuracy"
    test: str = "mann_whitney_u"


@dataclass(frozen=True, slots=True)
class ReplayConfig:
    """Configuration for replay/regression experiment type."""

    source_db: str
    check_metrics: list[str] = field(
        default_factory=lambda: ["validation_accuracy", "walltime_total"]
    )
    tolerance: float = 0.02


class ExperimentSpec(BaseModel):
    """Unified declarative specification for an experiment.

    Can be loaded from YAML/JSON and used to run any experiment type.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    # Identity
    name: str
    version: int = 1

    # Profile OR inline definition
    profile: str | None = None

    # Task configuration
    tasks: list[str] = Field(default_factory=lambda: ["digits"])

    # Experiment type and its configuration
    type: ExperimentType = ExperimentType.SHOWCASE
    ablation: AblationConfig | None = None
    scaling: ScalingConfig | None = None
    comparison: ComparisonConfig | None = None
    replay: ReplayConfig | None = None

    # Axes control (for showcase/grid types)
    vary: list[StructuralAxis] = Field(default_factory=list)
    fix: dict[StructuralAxis, str] = Field(default_factory=dict)

    # Search strategy
    search: SearchStrategy = SearchStrategy.GRID
    search_params: dict[str, Any] = Field(default_factory=dict)

    # Budget
    budget: Budget = Field(default_factory=Budget.default)

    # Gates (must pass before/during/after)
    gates: list[Gate] = Field(
        default_factory=lambda: [Gate.DRY_RUN, Gate.PROPERTY_LOCKS]
    )

    # Output
    reporters: list[Reporter] = Field(
        default_factory=lambda: [Reporter.HTML, Reporter.JSON, Reporter.SQLITE]
    )
    output_dir: str = "experiments/output"

    # Seeds
    seeds: int | list[int] = 1

    # Runtime
    fidelity: Fidelity = "L1"
    epochs: int = 1
    batch_limit: int = 2
    device: str = "auto"
    precision: str = "fp32"
    num_workers: int = 0
    deterministic: bool = False
    checkpoint_every_n: int = 0

    @model_validator(mode="after")
    def _validate_type_config(self) -> ExperimentSpec:
        """Validate that the correct config is present for the experiment type."""
        # Ensure registries are seeded for metric validation
        from computronium.experiment.schema.seed_registries import seed_all_registries

        seed_all_registries()

        if self.type == ExperimentType.ABLATION and self.ablation is None:
            raise ValueError("ablation config required for type=ablation")
        if self.type == ExperimentType.SCALING and self.scaling is None:
            raise ValueError("scaling config required for type=scaling")
        if self.type == ExperimentType.COMPARISON and self.comparison is None:
            raise ValueError("comparison config required for type=comparison")
        if self.type == ExperimentType.REPLAY and self.replay is None:
            raise ValueError("replay config required for type=replay")

        # Validate metric exists
        if self.ablation and self.ablation.metric not in OBJECTIVES_REGISTRY:
            raise ValueError(f"Unknown metric: {self.ablation.metric}")
        if self.comparison and self.comparison.metric not in OBJECTIVES_REGISTRY:
            raise ValueError(f"Unknown metric: {self.comparison.metric}")
        if self.scaling and self.scaling.metric not in OBJECTIVES_REGISTRY:
            raise ValueError(f"Unknown metric: {self.scaling.metric}")

        return self

    @classmethod
    def load(cls, path: str | Path) -> ExperimentSpec:
        """Load an ExperimentSpec from a file.

        Supports .yaml, .yml, and .json formats.
        """
        # Ensure registries are seeded for validation
        from computronium.experiment.schema.seed_registries import seed_all_registries

        seed_all_registries()

        spec_path = Path(path)
        raw = spec_path.read_text(encoding="utf-8")
        suffix = spec_path.suffix.lower()

        if suffix in {".yaml", ".yml"}:
            import yaml

            try:
                data = yaml.safe_load(raw)
            except yaml.YAMLError as exc:
                msg = f"{spec_path} is not valid YAML: {exc}"
                raise ValueError(msg) from exc
        elif suffix == ".json":
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as exc:
                msg = f"{spec_path} is not valid JSON: {exc}"
                raise ValueError(msg) from exc
        else:
            msg = (
                f"{spec_path}: unknown spec format {suffix!r}; use .json, .yaml or .yml"
            )
            raise ValueError(msg)

        return cls.model_validate(data)

    def to_run_spec(self) -> RunSpec:
        """Convert to a RunSpec for the pipeline."""
        axes: list[AxisSelection] = []

        for axis in StructuralAxis:
            if axis in self.fix:
                axes.append(AxisSelection(axis=axis, primitives=(self.fix[axis],)))
            elif axis in self.vary:
                from computronium.experiment.schema.axis import AXES_REGISTRIES

                registry = AXES_REGISTRIES[axis]
                primitives = tuple(
                    sorted(n for n, s in registry.items() if s.available)
                )
                axes.append(AxisSelection(axis=axis, primitives=primitives))
            else:
                # Not varied or fixed - use all available
                from computronium.experiment.schema.axis import AXES_REGISTRIES

                registry = AXES_REGISTRIES[axis]
                primitives = tuple(
                    sorted(n for n, s in registry.items() if s.available)
                )
                axes.append(
                    AxisSelection(
                        axis=axis, primitives=primitives if primitives else None
                    )
                )

        n_seeds = self.seeds if isinstance(self.seeds, int) else self.seeds[0]

        return RunSpec(
            profile=self.profile or f"experiment_{self.type.value}",
            task=self.tasks[0] if self.tasks else "digits",
            tasks=tuple(self.tasks[1:]) if len(self.tasks) > 1 else (),
            objectives=("validation_accuracy", "walltime_total"),
            fidelity=self.fidelity,
            n_seeds=n_seeds,
            epochs=self.epochs,
            batch_limit=self.batch_limit,
            budget_seconds=self.budget.seconds,
            param_budget=self.budget.param_budget,
            axes=tuple(axes),
            seed=0,
            device=self.device,
            precision=self.precision,
            num_workers=self.num_workers,
            deterministic=self.deterministic,
            checkpoint_every_n=self.checkpoint_every_n,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return self.model_dump(mode="json")


__all__ = [
    "AblationConfig",
    "Budget",
    "ComparisonConfig",
    "ExperimentSpec",
    "ExperimentType",
    "Gate",
    "ReplayConfig",
    "Reporter",
    "ScalingConfig",
    "SearchStrategy",
]
