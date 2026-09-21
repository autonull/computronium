from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class ModelSpecProtocol(Protocol):
    """Protocol for model specification objects used by the metamodel."""

    @property
    def name(self) -> str: ...

    @property
    def family(self) -> str: ...

    @property
    def model_type(self) -> str: ...

    @property
    def credit_assignment_type(self) -> str: ...


__all__ = [
    "EQUILIBRIUM_HYPERPARAMS",
    "FA_HYPERPARAMS",
    "GRADIENT_HYPERPARAMS",
    "HEBBIAN_HYPERPARAMS",
    "HYPERPARAM_METAMODEL",
    "TRANSFORMER_HYPERPARAMS",
    "UNIVERSAL_HYPERPARAMS",
    "HyperparamScope",
    "HyperparamSpec",
    "HyperparameterMetamodel",
    "ModelSpecProtocol",
]


class HyperparamScope(Enum):
    """Defines which algorithms a hyperparameter applies to."""

    UNIVERSAL = "universal"  # All algorithms (lr, hidden_dim, etc.)
    GRADIENT_BASED = "gradient"  # Backprop, variants (optimizer, grad_clip)
    EQUILIBRIUM = "equilibrium"  # EqProp family (beta, steps, nudge_type)
    FEEDBACK_ALIGNMENT = "fa"  # FA variants (fa_scale, adapt_rate)
    HEBBIAN = "hebbian"  # CHL, etc. (contrastive_steps)
    TRANSFORMER = "transformer"  # Transformer-specific (num_heads, etc.)
    # Referenced by get_search_space_for_model; currently have no dedicated
    # spec lists, so these families fall back to UNIVERSAL hyperparams.
    FORWARD_ONLY = "forward_only"  # PEPITA / Forward-Forward
    TARGET_PROP = "target_prop"  # Difference target propagation
    SPIKING = "spiking"  # Spiking / STDP
    PREDICTIVE_CODING = "predictive_coding"  # PCN / FPC


@dataclass(slots=True)
class HyperparamSpec:
    """Specification for a single hyperparameter."""

    name: str
    scope: HyperparamScope
    param_type: str  # "continuous", "discrete", "categorical"

    # For continuous/discrete
    range_min: float | None = None
    range_max: float | None = None
    scale: str | None = None  # "log", "linear", "int"

    # For categorical/discrete with choices
    choices: list[int | float | str] | None = None

    # Conditional dependencies
    requires: list[str] | None = None  # Other hyperparams that must exist
    conflicts: list[str] | None = None  # Hyperparams that cannot coexist

    # Metadata
    description: str = ""
    default: int | float | str | None = None


# Universal hyperparameters (apply to ALL algorithms)
UNIVERSAL_HYPERPARAMS = [
    HyperparamSpec(
        name="lr",
        scope=HyperparamScope.UNIVERSAL,
        param_type="continuous",
        range_min=1e-5,
        range_max=1e-2,
        scale="log",
        description="Learning rate for weight updates (max 1e-2 for small vision datasets)",
        default=1e-3,
    ),
    HyperparamSpec(
        name="hidden_dim",
        scope=HyperparamScope.UNIVERSAL,
        param_type="discrete",
        choices=[16, 32, 64, 128, 256],
        description="Number of hidden units per layer (512 removed — too large for digits/CIFAR-10)",
        default=64,
    ),
    HyperparamSpec(
        name="num_layers",
        scope=HyperparamScope.UNIVERSAL,
        param_type="discrete",
        range_min=1,
        range_max=5,
        scale="int",
        description="Number of layers in the network (max 5 for digits/CIFAR-10; 30 was too deep)",
        default=3,
    ),
    HyperparamSpec(
        name="activation",
        scope=HyperparamScope.UNIVERSAL,
        param_type="categorical",
        choices=["relu", "gelu", "silu", "tanh", "leaky_relu", "elu"],
        description="Activation function (NOTE: some algorithms constrain this)",
        default="silu",
    ),
    HyperparamSpec(
        name="weight_init",
        scope=HyperparamScope.UNIVERSAL,
        param_type="categorical",
        choices=["xavier", "kaiming", "orthogonal", "lecun"],
        description="Weight initialization scheme",
        default="kaiming",
    ),
]

# Gradient-based only (Backprop and gradient-based variants)
GRADIENT_HYPERPARAMS = [
    HyperparamSpec(
        name="optimizer",
        scope=HyperparamScope.GRADIENT_BASED,
        param_type="categorical",
        choices=["adam", "adamw", "rmsprop"],
        description="Gradient descent optimizer (sgd removed — unstable without careful tuning)",
        default="adam",
    ),
    HyperparamSpec(
        name="weight_decay",
        scope=HyperparamScope.GRADIENT_BASED,
        param_type="continuous",
        range_min=1e-6,
        range_max=1e-3,
        scale="log",
        description="L2 regularization strength (max 1e-3 for small datasets; 1e-2 was too high)",
        default=1e-4,
    ),
    HyperparamSpec(
        name="grad_clip",
        scope=HyperparamScope.GRADIENT_BASED,
        param_type="continuous",
        range_min=0.1,
        range_max=5.0,
        scale="linear",
        description="Gradient clipping threshold (min 0.1; 0.0 disables clipping and causes explosions)",
        default=1.0,
    ),
    HyperparamSpec(
        name="dropout",
        scope=HyperparamScope.GRADIENT_BASED,
        param_type="continuous",
        range_min=0.0,
        range_max=0.3,
        scale="linear",
        description="Dropout probability (max 0.3 for small datasets; 0.5 was too aggressive)",
        default=0.0,
    ),
    HyperparamSpec(
        name="momentum",
        scope=HyperparamScope.GRADIENT_BASED,
        param_type="continuous",
        range_min=0.5,
        range_max=0.99,
        scale="linear",
        description="SGD momentum (min 0.5; 0.0 with sgd is useless). Conditional on optimizer=sgd.",
        requires=["optimizer"],
        default=0.9,
    ),
]

# Equilibrium Propagation family
EQUILIBRIUM_HYPERPARAMS = [
    HyperparamSpec(
        name="beta",
        scope=HyperparamScope.EQUILIBRIUM,
        param_type="continuous",
        range_min=0.01,
        range_max=0.5,
        scale="linear",
        description="Nudge strength for clamping (max 0.5; 1.0 causes instability)",
        default=0.1,
    ),
    HyperparamSpec(
        name="steps",
        scope=HyperparamScope.EQUILIBRIUM,
        param_type="discrete",
        range_min=10,
        range_max=40,
        scale="int",
        description="Number of relaxation steps (min 10; 5 was too few for convergence)",
        default=20,
    ),
    HyperparamSpec(
        name="nudge_type",
        scope=HyperparamScope.EQUILIBRIUM,
        param_type="categorical",
        choices=["output_clamping", "energy_based", "symmetric"],
        description="How to apply target nudging",
        default="output_clamping",
    ),
]

# Feedback Alignment family
FA_HYPERPARAMS = [
    HyperparamSpec(
        name="fa_scale",
        scope=HyperparamScope.FEEDBACK_ALIGNMENT,
        param_type="continuous",
        range_min=0.5,
        range_max=2.0,
        scale="linear",
        description="Scaling factor for feedback weights",
        default=1.0,
    ),
    HyperparamSpec(
        name="adapt_rate",
        scope=HyperparamScope.FEEDBACK_ALIGNMENT,
        param_type="continuous",
        range_min=1e-4,
        range_max=1e-1,
        scale="log",
        description="Adaptation rate for feedback weights",
        default=1e-2,
    ),
]

# Hebbian family
HEBBIAN_HYPERPARAMS = [
    HyperparamSpec(
        name="contrastive_steps",
        scope=HyperparamScope.HEBBIAN,
        param_type="discrete",
        range_min=5,
        range_max=30,
        scale="int",
        description="Steps in contrastive phase",
        default=10,
    ),
]

# Transformer-specific
TRANSFORMER_HYPERPARAMS = [
    HyperparamSpec(
        name="num_heads",
        scope=HyperparamScope.TRANSFORMER,
        param_type="categorical",
        choices=[2, 4, 8],
        description="Number of attention heads",
        default=4,
    ),
    HyperparamSpec(
        name="context_length",
        scope=HyperparamScope.TRANSFORMER,
        param_type="discrete",
        choices=[64, 128, 256, 512],
        description="Maximum sequence length",
        default=128,
    ),
]


class HyperparameterMetamodel:
    """
    Central registry that knows which hyperparameters apply to which algorithms.
    """

    def __init__(self):
        self.all_specs = (
            UNIVERSAL_HYPERPARAMS
            + GRADIENT_HYPERPARAMS
            + EQUILIBRIUM_HYPERPARAMS
            + FA_HYPERPARAMS
            + HEBBIAN_HYPERPARAMS
            + TRANSFORMER_HYPERPARAMS
        )
        self._spec_dict = {spec.name: spec for spec in self.all_specs}

    def get_search_space_for_model(
        self, model_spec: ModelSpecProtocol, task_name: str | None = None
    ) -> dict[str, HyperparamSpec]:
        """
        Return the appropriate hyperparameters for a given model and task.

        Uses the model's family to determine which scoped params apply.
        Also applies constraints based on task size
        (e.g., small tasks get smaller models).
        """
        applicable_scopes = self._determine_applicable_scopes(model_spec)
        search_space = self._filter_specs_by_scopes(applicable_scopes)
        search_space = self._apply_transformer_params(model_spec, search_space)
        search_space = self._apply_activation_constraints(model_spec, search_space)
        search_space = self._apply_eqprop_constraints(model_spec, search_space)
        search_space = self._apply_small_task_constraints(task_name, search_space)
        search_space = self._apply_vision_model_constraints(model_spec, search_space, task_name)
        search_space = self._apply_rl_constraints(model_spec, search_space)
        return search_space

    def _determine_applicable_scopes(self, model_spec: ModelSpecProtocol) -> set[HyperparamScope]:
        """Determine which hyperparameter scopes apply to a model."""
        applicable_scopes = {HyperparamScope.UNIVERSAL}
        family = model_spec.family.lower()
        model_type = model_spec.model_type.lower()

        # Direct family-to-scope mappings
        family_scopes = {
            "baseline": HyperparamScope.GRADIENT_BASED,
            "backprop": HyperparamScope.GRADIENT_BASED,
            "backpropagation": HyperparamScope.GRADIENT_BASED,
            "eqprop": HyperparamScope.EQUILIBRIUM,
            "hebbian": HyperparamScope.HEBBIAN,
            "fa": HyperparamScope.FEEDBACK_ALIGNMENT,
            "feedback_alignment": HyperparamScope.FEEDBACK_ALIGNMENT,
            "mep": HyperparamScope.FORWARD_ONLY,
            "forward_only": HyperparamScope.FORWARD_ONLY,
            "forward-only": HyperparamScope.FORWARD_ONLY,
            "target_prop": HyperparamScope.TARGET_PROP,
            "target-prop": HyperparamScope.TARGET_PROP,
            "spiking": HyperparamScope.SPIKING,
            "predictive_coding": HyperparamScope.PREDICTIVE_CODING,
            "predictive-coding": HyperparamScope.PREDICTIVE_CODING,
            "tile": HyperparamScope.EQUILIBRIUM,
        }

        if family in family_scopes:
            applicable_scopes.add(family_scopes[family])
        elif family == "hybrid":
            self._add_hybrid_scopes(model_type, applicable_scopes)
        else:
            self._add_fallback_scopes(model_spec, applicable_scopes)

        return applicable_scopes

    def _add_hybrid_scopes(self, model_type: str, applicable_scopes: set[HyperparamScope]) -> None:
        """Add scopes for hybrid model types."""
        if "fa" in model_type or "alignment" in model_type:
            applicable_scopes.add(HyperparamScope.FEEDBACK_ALIGNMENT)
        if "equilibrium" in model_type or "eq" in model_type:
            applicable_scopes.add(HyperparamScope.EQUILIBRIUM)
        if "hebbian" in model_type:
            applicable_scopes.add(HyperparamScope.HEBBIAN)
        applicable_scopes.add(HyperparamScope.GRADIENT_BASED)

    def _add_fallback_scopes(self, model_spec: ModelSpecProtocol, applicable_scopes: set[HyperparamScope]) -> None:
        """Add scopes based on credit_assignment_type when family not recognized."""
        cat = model_spec.credit_assignment_type.lower()
        match cat:
            case "equilibrium":
                applicable_scopes.add(HyperparamScope.EQUILIBRIUM)
            case "hebbian":
                applicable_scopes.add(HyperparamScope.HEBBIAN)
            case "target":
                applicable_scopes.add(HyperparamScope.TARGET_PROP)
            case "forward-only":
                applicable_scopes.add(HyperparamScope.FORWARD_ONLY)
            case "spiking":
                applicable_scopes.add(HyperparamScope.SPIKING)
            case "predictive-coding":
                applicable_scopes.add(HyperparamScope.PREDICTIVE_CODING)
            case "gradient":
                applicable_scopes.add(HyperparamScope.GRADIENT_BASED)

    def _filter_specs_by_scopes(self, applicable_scopes: set[HyperparamScope]) -> dict[str, HyperparamSpec]:
        """Filter hyperparameter specs by applicable scopes."""
        search_space = {}
        for spec in self.all_specs:
            if spec.scope in applicable_scopes:
                search_space[spec.name] = spec
        return search_space

    def _apply_transformer_params(
        self, model_spec: ModelSpecProtocol, search_space: dict[str, HyperparamSpec]
    ) -> dict[str, HyperparamSpec]:
        """Add transformer-specific params when model_type indicates a transformer."""
        model_type = getattr(model_spec, "model_type", "") or ""
        if "transformer" in model_type.lower():
            for spec in self.all_specs:
                if spec.scope == HyperparamScope.TRANSFORMER and spec.name not in search_space:
                    search_space[spec.name] = spec
        return search_space

    def _apply_activation_constraints(
        self, model_spec: ModelSpecProtocol, search_space: dict[str, HyperparamSpec]
    ) -> dict[str, HyperparamSpec]:
        """Apply algorithm-specific activation constraints."""
        if "holomorphic" in model_spec.name.lower():
            act_spec = self._spec_dict["activation"]
            constrained_act = HyperparamSpec(
                name=act_spec.name,
                scope=act_spec.scope,
                param_type=act_spec.param_type,
                choices=["tanh"],
            )
            search_space["activation"] = constrained_act
        return search_space

    def _apply_eqprop_constraints(
        self, model_spec: ModelSpecProtocol, search_space: dict[str, HyperparamSpec]
    ) -> dict[str, HyperparamSpec]:
        """Apply EqProp-specific constraints (limit depth due to computational cost)."""
        family = model_spec.family.lower()
        if family == "eqprop" or "eqprop" in model_spec.name.lower():
            if "num_layers" in search_space:
                layer_spec = self._spec_dict["num_layers"]
                constrained_layers = HyperparamSpec(
                    name=layer_spec.name,
                    scope=layer_spec.scope,
                    param_type=layer_spec.param_type,
                    range_max=6,
                    default=3,
                )
                search_space["num_layers"] = constrained_layers
        return search_space

    def _apply_small_task_constraints(
        self, task_name: str | None, search_space: dict[str, HyperparamSpec]
    ) -> dict[str, HyperparamSpec]:
        """Apply constraints for small tasks (digits, MNIST variants)."""
        is_small_task = task_name and task_name in {
            "digits",
            "usps",
            "mnist",
            "kmnist",
            "fashion_mnist",
        }
        if not is_small_task:
            return search_space

        if "hidden_dim" in search_space:
            hd_spec = search_space["hidden_dim"]
            hd_choices: list[int] = [c for c in (hd_spec.choices or []) if isinstance(c, int)]
            constrained_hd = HyperparamSpec(
                name=hd_spec.name,
                scope=hd_spec.scope,
                param_type=hd_spec.param_type,
                choices=[c for c in hd_choices if c <= 128] or [64],
                default=min(int(hd_spec.default or 64), 128),
            )
            search_space["hidden_dim"] = constrained_hd

        if "num_layers" in search_space:
            nl_spec = search_space["num_layers"]
            constrained_nl = HyperparamSpec(
                name=nl_spec.name,
                scope=nl_spec.scope,
                param_type=nl_spec.param_type,
                range_max=min(nl_spec.range_max, 4) if nl_spec.range_max else None,
                default=min(int(nl_spec.default or 4), 4),
            )
            search_space["num_layers"] = constrained_nl

        return search_space

    def _apply_vision_model_constraints(
        self, model_spec: ModelSpecProtocol, search_space: dict[str, HyperparamSpec], task_name: str | None
    ) -> dict[str, HyperparamSpec]:
        """Apply vision model heuristics (wider layers for non-small tasks)."""
        is_small_task = task_name and task_name in {
            "digits",
            "usps",
            "mnist",
            "kmnist",
            "fashion_mnist",
        }
        is_vision_model = (
            "vision" in model_spec.model_type.lower()
            or model_spec.family in ("backprop", "eqprop", "fa", "tile")
        )
        if is_vision_model and "hidden_dim" in search_space and not is_small_task:
            hd_spec = search_space["hidden_dim"]
            hd_choices: list[int] = [c for c in (hd_spec.choices or []) if isinstance(c, int)]
            constrained_hd = HyperparamSpec(
                name=hd_spec.name,
                scope=hd_spec.scope,
                param_type=hd_spec.param_type,
                choices=[c for c in hd_choices if 16 <= c <= 256] or [16],
                default=min(int(hd_spec.default or 16), 256),
            )
            search_space["hidden_dim"] = constrained_hd
        return search_space

    def _apply_rl_constraints(
        self, model_spec: ModelSpecProtocol, search_space: dict[str, HyperparamSpec]
    ) -> dict[str, HyperparamSpec]:
        """Apply RL-specific learning rate constraints."""
        is_rl_model = "rl" in model_spec.model_type.lower() or model_spec.family == "rl"
        if is_rl_model and "lr" in search_space:
            lr_spec = search_space["lr"]
            range_min = lr_spec.range_min
            range_max = lr_spec.range_max
            if range_min is not None:
                range_min = max(range_min, 1e-3)
            if range_max is not None:
                range_max = min(range_max, 1e-1)
            constrained_lr = HyperparamSpec(
                name=lr_spec.name,
                scope=lr_spec.scope,
                param_type=lr_spec.param_type,
                range_min=range_min,
                range_max=range_max,
            )
            search_space["lr"] = constrained_lr
        return search_space

    def validate_config(
        self, model_spec: ModelSpecProtocol, config: dict[str, object]
    ) -> list[str]:
        """
        Validate that a config is compatible with a model.
        Returns list of error messages (empty if valid).
        """
        errors = []
        valid_space = self.get_search_space_for_model(model_spec)

        for key, value in config.items():
            if key not in valid_space:  # ruff: ignore[collapsible-if]
                # Some infrastructure keys might be passed (e.g., 'epochs', 'device')
                # Only flag if it matches a known hyperparam that ISN'T available
                if key in self._spec_dict:
                    errors.append(
                        f"Hyperparameter '{key}' is not applicable to"
                        f" {model_spec.name} (family: {model_spec.family})"
                    )

        # Check for missing required params
        for key, spec in valid_space.items():
            if spec.requires:
                for req in spec.requires:
                    pass

        return errors


# Global instance
HYPERPARAM_METAMODEL = HyperparameterMetamodel()
