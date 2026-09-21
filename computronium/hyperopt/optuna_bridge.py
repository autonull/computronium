"""
Optuna Bridge for Bioplausible

Maps model views and SearchSpace definitions to Optuna suggest_* calls.
Replaces custom evolution code with Optuna's proven algorithms.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

import optuna
from optuna.pruners import HyperbandPruner, MedianPruner
from optuna.samplers import NSGAIISampler, TPESampler

if TYPE_CHECKING:
    from collections.abc import Callable
    from .hyperparameter_metamodel import HyperparamSpec, ModelSpecProtocol, HyperparameterMetamodel


class EvaluationConfigProtocol(Protocol):
    """Protocol for evaluation configuration objects."""

    max_hidden_dim: int | None
    max_layers: int | None
    epochs: int | None
    use_pruning: bool | None
    n_startup_trials: int | None


__all__ = [
    "create_optuna_space",
    "create_study",
    "get_pareto_trials",
    "optimize_with_callback",
    "scalarize_objectives",
    "trial_to_metrics",
]


class _ModelView:
    """Duck-typed view of a model for the hyperparameter metamodel."""

    __slots__ = ("_name", "_family", "_model_type", "_credit_assignment_type")

    def __init__(
        self,
        name: str,
        family: str,
        model_type: str = "",
        credit_assignment_type: str = "",
    ) -> None:
        self._name = name
        self._family = family
        self._model_type = model_type
        self._credit_assignment_type = credit_assignment_type

    @property
    def name(self) -> str:
        return self._name

    @property
    def family(self) -> str:
        return self._family

    @property
    def model_type(self) -> str:
        return self._model_type

    @property
    def credit_assignment_type(self) -> str:
        return self._credit_assignment_type


_FAMILY_KEYWORDS: tuple[tuple[str, str], ...] = (
    ("eqprop", "eqprop"),
    ("backprop", "backprop"),
    ("feedback_alignment", "fa"),
    ("forward", "mep"),
    ("hebbian", "hebbian"),
    ("target_prop", "target_prop"),
    ("spiking", "spiking"),
    ("predictive", "predictive_coding"),
    ("tile", "tile"),
)


def _model_view(model_name: str) -> _ModelView:
    """Infer the metamodel's model view from the model name."""
    lowered = model_name.lower()
    family = next((fam for key, fam in _FAMILY_KEYWORDS if key in lowered), "baseline")
    return _ModelView(name=model_name, family=family)


def scalarize_objectives(
    accuracy: float, param_count: float, iteration_time: float
) -> float:
    """
    Scalarize multi-objectives into single score with priorities:
    #1 Maximize accuracy (weight: 1.0)
    #2 Minimize param count (weight: 0.01)
    #3 Minimize iteration time (weight: 0.001)

    Args:
        accuracy: Test accuracy (0-1)
        param_count: Model parameters in millions
        iteration_time: Time per iteration in seconds

    Returns:
        Scalar score (higher is better)
    """
    score = (
        accuracy * 1.0  # Primary: maximize accuracy
        - param_count * 0.01  # Secondary: minimize params
        - iteration_time * 0.001  # Tertiary: minimize time
    )
    return score


def create_optuna_space(
    trial: optuna.Trial,
    model_name: str,
    constraints: dict[str, float | int | None] | None = None,
    evaluation_config: EvaluationConfigProtocol | None = None,
    task_name: str | None = None,
    search_space: dict[str, list[int | float | str] | list[float] | None] | None = None,
) -> dict[str, object]:
    """
    Create Optuna hyperparameter space using Hyperparameter Metamodel.

    Args:
        trial: Optuna trial object
        model_name: Name of model from ModelRegistry
        constraints: Optional constraints (max_layers, max_hidden, etc.)
        evaluation_config: Optional EvaluationConfig for patience-based constraints
        task_name: Name of the task (e.g., 'mnist', 'digits')
        search_space: Optional experiment-owned overrides for the search space
            (e.g. ``{"hidden_dim": [16, 32, 64, 128, 256], "num_layers": [1, 4]}``).
            Keys are param names; values either a full list of choices or a
            ``[min, max]`` range. These override the metamodel's defaults so the
            experiment controls its own bounds instead of relying on hardcoded
            constants in computronium's HPO components.

    Returns:
        Config dictionary with sampled hyperparameters
    """
    config = {}

    constraints = _merge_evaluation_constraints(constraints, evaluation_config, config)

    from .hyperparameter_metamodel import HYPERPARAM_METAMODEL

    model_spec = _model_view(model_name)
    space: dict[str, HyperparamSpec] = HYPERPARAM_METAMODEL.get_search_space_for_model(
        model_spec, task_name=task_name
    )

    if search_space:
        space = _apply_search_space_overrides(space, search_space)

    for param_name, original_spec in space.items():
        if param_name in config:
            continue

        spec = _prepare_spec_for_sampling(original_spec)
        min_val = spec.range_min
        max_val = spec.range_max

        if constraints:
            min_val, max_val = _apply_parameter_constraints(
                param_name, spec, constraints, min_val, max_val
            )

        config[param_name] = _sample_parameter(trial, param_name, spec, min_val, max_val)

    _validate_config(HYPERPARAM_METAMODEL, model_spec, config)

    return config


def _merge_evaluation_constraints(
    constraints: dict[str, float | int | None] | None,
    evaluation_config: EvaluationConfigProtocol | None,
    config: dict[str, object],
) -> dict[str, float | int | None]:
    """Merge constraints from evaluation_config into constraints dict."""
    if evaluation_config:
        if constraints is None:
            constraints = {}
        if evaluation_config.max_hidden_dim is not None:
            constraints["max_hidden"] = evaluation_config.max_hidden_dim
        if evaluation_config.max_layers is not None:
            constraints["max_layers"] = evaluation_config.max_layers
        if evaluation_config.epochs is not None:
            config["epochs"] = evaluation_config.epochs
    return constraints or {}


def _apply_search_space_overrides(
    space: dict[str, HyperparamSpec],
    search_space: dict[str, list[int | float | str] | list[float] | None] | None,
) -> dict[str, HyperparamSpec]:
    """Apply experiment-owned search_space overrides to the parameter space."""
    if not search_space:
        return space

    import copy

    for param_name, override in search_space.items():
        if param_name not in space or override is None:
            continue
        spec = space[param_name]
        spec = copy.deepcopy(spec)
        override_is_list = isinstance(override, (list, tuple))
        has_choices = bool(spec.choices)
        is_range = (
            override_is_list
            and len(override) == 2
            and all(isinstance(v, (int, float)) for v in override)
            and not has_choices
        )
        if is_range and spec.param_type in ("continuous", "discrete"):  # ruff: ignore[literal-membership]
            min_v, max_v = override
            spec.range_min = float(min_v)
            spec.range_max = float(max_v)
        elif override_is_list:
            spec.choices = [c for c in override]  # ruff: ignore[unnecessary-comprehension]
            if has_choices and spec.param_type == "categorical":
                spec.default = spec.choices[0]
        space[param_name] = spec
    return space


def _prepare_spec_for_sampling(spec: HyperparamSpec) -> HyperparamSpec:
    """Create a shallow copy of spec to avoid modifying global state."""
    import copy

    spec = copy.copy(spec)
    if spec.choices:
        spec.choices = list(spec.choices)
    return spec


def _apply_parameter_constraints(
    param_name: str,
    spec: HyperparamSpec,
    constraints: dict[str, float | int | None],
    min_val: float | None,
    max_val: float | None,
) -> tuple[float | None, float | None]:
    """Apply tier/algorithm constraints to parameter ranges."""
    if param_name == "hidden_dim":
        min_val, max_val = _constrain_hidden_dim(spec, constraints, min_val, max_val)
    elif param_name == "num_layers":
        min_val, max_val = _constrain_num_layers(spec, constraints, min_val, max_val)
    elif param_name == "steps":
        min_val, max_val = _constrain_steps(spec, constraints, min_val, max_val)

    # Intelligent constraints using a mapping for cleaner code
    constraint_map = {
        "lr": ("min_lr", "max_lr"),
        "beta": ("min_beta", "max_beta"),
        "weight_decay": ("min_weight_decay", "max_weight_decay"),
        "dropout": ("min_dropout", "max_dropout"),
    }
    if param_name in constraint_map:
        min_key, max_key = constraint_map[param_name]
        if max_key in constraints and max_val is not None:
            constraint_val = constraints[max_key]
            if constraint_val is not None:
                max_val = min(max_val, constraint_val)
        if min_key in constraints and min_val is not None:
            constraint_val = constraints[min_key]
            if constraint_val is not None:
                min_val = max(min_val, constraint_val)

    return min_val, max_val


def _constrain_hidden_dim(
    spec: HyperparamSpec,
    constraints: dict[str, float | int | None],
    min_val: float | None,
    max_val: float | None,
) -> tuple[float | None, float | None]:
    """Apply max_hidden constraint to hidden_dim."""
    if "max_hidden" in constraints and spec.choices:
        max_hidden = constraints["max_hidden"]
        if max_hidden is not None:
            # Filter to numeric choices only
            numeric_choices = [c for c in spec.choices if isinstance(c, (int, float))]
            spec.choices = [c for c in numeric_choices if c <= max_hidden]
            if not spec.choices:
                spec.choices = [max_hidden]
    return min_val, max_val


def _constrain_num_layers(
    spec: HyperparamSpec,
    constraints: dict[str, float | int | None],
    min_val: float | None,
    max_val: float | None,
) -> tuple[float | None, float | None]:
    """Apply max_layers constraint to num_layers."""
    if "max_layers" in constraints:
        max_layers = constraints["max_layers"]
        if max_layers is not None:
            if spec.range_max is not None and max_val is not None:
                max_val = min(max_val, float(max_layers))
            elif spec.choices:
                # Filter to numeric choices only
                numeric_choices = [c for c in spec.choices if isinstance(c, (int, float))]
                spec.choices = [c for c in numeric_choices if c <= max_layers]
    return min_val, max_val


def _constrain_steps(
    spec: HyperparamSpec,
    constraints: dict[str, float | int | None],
    min_val: float | None,
    max_val: float | None,
) -> tuple[float | None, float | None]:
    """Apply max_steps constraint to steps."""
    if "max_steps" in constraints and spec.range_max is not None:  # ruff: ignore[collapsible-if]
        max_steps = constraints["max_steps"]
        if max_steps is not None and max_val is not None:
            max_val = min(max_val, float(max_steps))
    return min_val, max_val


def _sample_parameter(
    trial: optuna.Trial,
    param_name: str,
    spec: HyperparamSpec,
    min_val: float | None,
    max_val: float | None,
) -> object:
    """Sample a parameter value based on its type."""
    if spec.param_type == "continuous":
        if min_val is not None and max_val is not None:
            lo = min(min_val, max_val)
            return trial.suggest_float(param_name, lo, max_val, log=(spec.scale == "log"))

    elif spec.param_type == "discrete":
        if spec.choices:
            # choices are list[int | float | str] for discrete
            return trial.suggest_categorical(param_name, spec.choices)
        if min_val is not None and max_val is not None:
            return trial.suggest_int(param_name, int(min_val), int(max_val))

    elif spec.param_type == "categorical" and spec.choices:
        return trial.suggest_categorical(param_name, spec.choices)

    # Fallback - should not reach here if all param types are handled
    return spec.default


def _validate_config(
    metamodel: HyperparameterMetamodel, model_spec: ModelSpecProtocol, config: dict[str, object]
) -> None:
    """Validate final config and log warnings for errors."""
    errors = metamodel.validate_config(model_spec, config)
    if errors:
        # Just log/warn for now, don't crash unless critical
        pass


def create_study(
    model_names: list[str],
    n_objectives: int = 2,
    storage: str | None = None,
    study_name: str | None = None,
    use_pruning: bool = True,
    sampler_name: str = "tpe",
    evaluation_config: EvaluationConfigProtocol | None = None,
    mode: str = "pareto",  # "pareto" or "scalarized"
    seed: int | None = None,
) -> optuna.Study:
    """
    Create an Optuna study for hyperparameter optimization.

    Args:
        model_names: List of model names to optimize
        n_objectives: Number of objectives (1=single, 2=multi like accuracy+loss)
        storage: Storage URL (e.g., "sqlite:///optuna.db"). None for in-memory.
        study_name: Name for the study
        use_pruning: Whether to use automatic pruning
        sampler_name: "tpe", "nsga2", or "random"
        evaluation_config: Optional EvaluationConfig for patience-based settings
        mode: "pareto" for multi-objective Pareto frontier, "scalarized" for weighted
            single objective

    Returns:
        Optuna study object
    """
    # Override pruning from evaluation_config if provided
    if evaluation_config and evaluation_config.use_pruning is not None:
        use_pruning = evaluation_config.use_pruning

    # Direction: maximize accuracy, minimize loss/params/time
    # For scalarized mode, force n_objectives=1
    if mode == "scalarized":
        directions = ["maximize"]  # Maximize scalarized score
        n_objectives = 1
    elif n_objectives == 1:
        directions = ["maximize"]
    elif n_objectives == 2:
        directions = ["maximize", "minimize"]  # accuracy, loss
    elif n_objectives == 3:
        directions = ["maximize", "minimize", "minimize"]  # accuracy, params, time
    else:
        directions = ["maximize"] + ["minimize"] * (n_objectives - 1)

    # Sampler selection with config
    n_startup = 10  # default
    if evaluation_config and evaluation_config.n_startup_trials is not None:
        n_startup = evaluation_config.n_startup_trials

    if sampler_name == "nsga2":
        sampler = NSGAIISampler(seed=seed)
    elif sampler_name == "random":
        sampler = optuna.samplers.RandomSampler(seed=seed)
    else:  # TPE
        sampler = TPESampler(multivariate=True, n_startup_trials=n_startup, seed=seed)

    # Pruner selection
    if use_pruning:
        pruner = HyperbandPruner(min_resource=3, reduction_factor=3)
    else:
        pruner = MedianPruner()

    study = optuna.create_study(
        directions=directions,
        sampler=sampler,
        pruner=pruner,
        storage=storage,
        study_name=study_name,
        load_if_exists=True,
    )

    # Store mode metadata
    study.set_user_attr("mode", mode)

    return study


def get_pareto_trials(study: optuna.Study) -> list[optuna.trial.FrozenTrial]:
    """
    Get Pareto frontier trials from a multi-objective study.

    Args:
        study: Optuna study

    Returns:
        List of trials on the Pareto frontier
    """
    if len(study.directions) == 1:
        # Single objective - just return best trial
        return [study.best_trial]

    # Multi-objective - get Pareto front
    return study.best_trials


def trial_to_metrics(trial: optuna.trial.FrozenTrial) -> dict[str, object]:
    """
    Convert Optuna trial to metrics format compatible with existing code.

    Args:
        trial: Optuna trial

    Returns:
        Metrics dictionary
    """
    metrics = {
        "config": trial.params,
        "trial_id": trial.number,
        "state": trial.state.name,
    }

    if trial.values:
        if len(trial.values) == 2:
            metrics["accuracy"] = trial.values[0]
            metrics["loss"] = trial.values[1]
        else:
            metrics["score"] = trial.values[0]

    return metrics


def optimize_with_callback(
    study: optuna.Study,
    objective: Callable,
    n_trials: int,
    callbacks: list[Callable] | None = None,
) -> None:
    """
    Run optimization with custom callbacks (for UI updates).

    Args:
        study: Optuna study
        objective: Objective function
        n_trials: Number of trials to run
        callbacks: List of callback functions
    """
    study.optimize(
        objective,
        n_trials=n_trials,
        callbacks=callbacks,
        show_progress_bar=True,
    )
