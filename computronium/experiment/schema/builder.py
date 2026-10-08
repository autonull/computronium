"""RunSpec Builder API for programmatic experiment construction.

Provides a fluent Python API for building RunSpec objects without YAML/JSON files.
"""

from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING, Any, Literal, Self

if TYPE_CHECKING:
    from collections.abc import Sequence

from computronium.experiment.schema.run_spec import (
    BROAD_PARAM_BUDGET,
    MEASURED_BATCH_LIMIT,
    MEASURED_PARAM_BUDGET,
    AxisSelection,
    Domain,
    Fidelity,
    RunSpec,
    Scale,
    StructuralAxis,
)


class RunSpecBuilder:  # ruff: ignore[too-many-public-methods]
    """Fluent builder for RunSpec objects.

    Example:
        spec = (RunSpecBuilder()
            .task("mnist")
            .fidelity("L1")
            .seeds(3)
            .epochs(10)
            .objectives("validation_accuracy", "walltime_total")
            .axis("credit", ["gradient", "thermodynamic_contrast", "random_projections"])
            .axis("plasticity", ["null", "routing"])
            .build())
        spec.to_file("my_run.yaml")
    """

    def __init__(self) -> None:
        self._profile = "custom"
        self._task: str | None = None
        self._tasks: tuple[str, ...] = ()
        self._objectives: list[str] = []
        self._stages: list[str] | None = None
        self._fidelity: Fidelity = "L0"
        self._n_seeds: int = 1
        self._epochs: int = 1
        self._batch_limit: int = 0
        self._seed: int = 0
        self._budget_seconds: float | None = None
        self._param_budget: int = 0
        self._policy: str | None = None
        self._axes: list[AxisSelection] = []
        self._hyperparameters: dict[str, Domain] = {}
        self._operating_points: dict[str, Any] = {}
        self._dataset: str = "unknown"
        self._dataset_version: str = "1.0"
        self._code_sha: str = "unknown"
        self._device: Literal["auto", "cpu", "cuda"] = "auto"
        self._deterministic: bool = False
        self._num_workers: int = 0
        self._precision: Literal["fp32", "fp16", "bf16"] = "fp32"
        self._checkpoint_every_n: int = 0
        self._axis_objectives: dict[str, tuple[str, ...]] = {}
        self._sweep_steps: int = 5

    def profile(self, name: str) -> Self:
        """Set a named run profile (quick-verify, production-map, maturation, claim)."""
        self._profile = name
        # Apply profile defaults
        if name == "quick-verify":
            self._fidelity = "L1"
            self._n_seeds = 1
            self._epochs = 3
            self._batch_limit = MEASURED_BATCH_LIMIT
            self._budget_seconds = 300.0
            self._task = "digits"
            self._policy = "round_robin_grid"
            self._param_budget = MEASURED_PARAM_BUDGET
            self._objectives = ["validation_accuracy", "walltime_total"]
            self._checkpoint_every_n = 1
        elif name == "production-map":
            self._fidelity = "L0"
            self._n_seeds = 1
            self._epochs = 1
            self._batch_limit = MEASURED_BATCH_LIMIT
            self._budget_seconds = 3600.0
            self._task = "digits"
            self._policy = "model_based"
            self._param_budget = BROAD_PARAM_BUDGET
            self._objectives = ["validation_accuracy", "walltime_total", "param_count"]
        elif name == "maturation":
            self._fidelity = "L2"
            self._n_seeds = 5
            self._epochs = 10
            self._batch_limit = 0
            self._budget_seconds = 7200.0
            self._task = "digits"
            self._policy = "evolution"
            self._param_budget = BROAD_PARAM_BUDGET
            self._objectives = ["validation_accuracy", "walltime_total", "param_count"]
        elif name == "claim":
            self._fidelity = "L2"
            self._n_seeds = 10
            self._epochs = 20
            self._batch_limit = 0
            self._budget_seconds = 86400.0
            self._task = "digits"
            self._policy = "evolution"
            self._param_budget = BROAD_PARAM_BUDGET
            self._objectives = ["validation_accuracy", "walltime_total", "param_count"]
        return self

    def task(self, name: str) -> Self:
        """Set the task name (e.g., 'mnist', 'cifar10', 'digits')."""
        self._task = name
        return self

    def tasks(self, *names: str) -> Self:
        """Set multiple tasks."""
        self._tasks = tuple(names)
        self._task = names[0] if names else None
        return self

    def fidelity(self, level: Fidelity) -> Self:
        """Set fidelity level (L0, L1, L2)."""
        self._fidelity = level
        return self

    def seeds(self, n: int) -> Self:
        """Set number of seeds per coordinate."""
        self._n_seeds = n
        return self

    def epochs(self, n: int) -> Self:
        """Set number of epochs per run."""
        self._epochs = n
        return self

    def batch_limit(self, n: int) -> Self:
        """Limit batches per epoch (0 = full training)."""
        self._batch_limit = n
        return self

    def seed(self, value: int) -> Self:
        """Set base seed for reproducibility."""
        self._seed = value
        return self

    def budget(self, seconds: float) -> Self:
        """Set time budget in seconds."""
        self._budget_seconds = seconds
        return self

    def param_budget(self, n: int) -> Self:
        """Set parameter ceiling for geometry sizing (0 = unconstrained)."""
        self._param_budget = n
        return self

    def policy(self, name: str) -> Self:
        """Set policy name (round_robin_grid, model_based, evolution)."""
        self._policy = name
        return self

    def objectives(self, *names: str) -> Self:
        """Set objectives to measure (must be registered in OBJECTIVES_REGISTRY)."""
        self._objectives = list(names)
        return self

    def add_objective(self, name: str) -> Self:
        """Add a single objective to the list."""
        self._objectives.append(name)
        return self

    def stages(self, *stage_ids: str) -> Self:
        """Set explicit stage sequence (e.g., 's1_frame', 's2_space', ...)."""
        self._stages = list(stage_ids)
        return self

    def axis(self, axis_name: str | StructuralAxis, primitives: Sequence[str]) -> Self:
        """Restrict an axis to specific primitives.

        Args:
            axis_name: Axis name (e.g., 'substrate', 'geometry', 'credit') or StructuralAxis enum.
            primitives: Tuple/list of primitive names to include.
        """
        axis = StructuralAxis(axis_name) if isinstance(axis_name, str) else axis_name
        self._axes.append(AxisSelection(axis=axis, primitives=tuple(primitives)))
        return self

    def axis_all(self, axis_name: str | StructuralAxis) -> Self:
        """Include all available primitives for an axis (default behavior)."""
        axis = StructuralAxis(axis_name) if isinstance(axis_name, str) else axis_name
        self._axes.append(AxisSelection(axis=axis, primitives=None))
        return self

    def hyperparameter(self, name: str, domain: Domain) -> Self:
        """Add a hyperparameter sweep domain."""
        self._hyperparameters[name] = domain
        return self

    def hyperparameter_range(
        self,
        name: str,
        lo: float,
        hi: float,
        scale: Scale = Scale.LINEAR,
    ) -> Self:
        """Add a hyperparameter with a continuous range domain."""
        self._hyperparameters[name] = Domain(lo=lo, hi=hi, scale=scale)
        return self

    def hyperparameter_categorical(self, name: str, *values: str | float) -> Self:
        """Add a hyperparameter with categorical values."""
        self._hyperparameters[name] = Domain(members=tuple(values))
        return self

    def hyperparameter_int_range(
        self, name: str, lo: int, hi: int, scale: Scale = Scale.LINEAR
    ) -> Self:
        """Add an integer hyperparameter with a range domain."""
        self._hyperparameters[name] = Domain(lo=float(lo), hi=float(hi), scale=scale)
        return self

    def operating_point(self, name: str, value: Any) -> Self:
        """Add an operating point (reference value for hyperparameters)."""
        self._operating_points[name] = value
        return self

    def dataset(self, name: str, version: str = "1.0") -> Self:
        """Set dataset name and version."""
        self._dataset = name
        self._dataset_version = version
        return self

    def code_sha(self, sha: str) -> Self:
        """Set code SHA for reproducibility."""
        self._code_sha = sha
        return self

    def device(self, device: Literal["auto", "cpu", "cuda"]) -> Self:
        """Set compute device."""
        self._device = device
        return self

    def deterministic(self, value: bool = True) -> Self:
        """Enable/disable deterministic algorithms."""
        self._deterministic = value
        return self

    def num_workers(self, n: int) -> Self:
        """Set DataLoader num_workers."""
        self._num_workers = n
        return self

    def precision(self, precision: Literal["fp32", "fp16", "bf16"]) -> Self:
        """Set numerical precision."""
        self._precision = precision
        return self

    def checkpoint_every(self, n: int) -> Self:
        """Save checkpoint every N epochs (0 = disabled)."""
        self._checkpoint_every_n = n
        return self

    def axis_objectives(self, axis_name: str, *objectives: str) -> Self:
        """Set axis-aligned objectives for multi-objective optimization."""
        self._axis_objectives[axis_name] = tuple(objectives)
        return self

    def sweep_steps(self, n: int) -> Self:
        """Set number of diagonal steps through hyperparameter space."""
        self._sweep_steps = n
        return self

    def build(self) -> RunSpec:
        """Build and validate the RunSpec."""
        return RunSpec(
            version=2,
            profile=self._profile,
            task=self._task,
            tasks=self._tasks,
            objectives=tuple(self._objectives),
            stages=tuple(self._stages) if self._stages else None,
            fidelity=self._fidelity,
            n_seeds=self._n_seeds,
            epochs=self._epochs,
            batch_limit=self._batch_limit,
            seed=self._seed,
            budget_seconds=self._budget_seconds,
            param_budget=self._param_budget,
            policy=self._policy,
            axes=tuple(self._axes),
            hyperparameters=self._hyperparameters,
            operating_points=self._operating_points,
            dataset=self._dataset,
            dataset_version=self._dataset_version,
            code_sha=self._code_sha,
            device=self._device,
            deterministic=self._deterministic,
            num_workers=self._num_workers,
            precision=self._precision,
            checkpoint_every_n=self._checkpoint_every_n,
            axis_objectives=self._axis_objectives,
            sweep_steps=self._sweep_steps,
        )

    def to_file(self, path: str) -> Self:
        """Build and save to JSON file."""
        spec = self.build()
        import json

        with pathlib.Path(path).open("w", encoding="utf-8") as f:
            json.dump(spec.to_dict(), f, indent=2)
        return self

    def to_yaml(self, path: str) -> Self:
        """Build and save to YAML file."""
        spec = self.build()
        import yaml

        with pathlib.Path(path).open("w", encoding="utf-8") as f:
            yaml.dump(spec.to_dict(), f, sort_keys=False)
        return self
