"""Task Registry: Enriched task specifications for cross-domain coverage.

Extends SUPPORTED_TASKS with domain, shape, objective defaults, cost class,
and measured objectives per task. Wires F0 objective emission + F0b normalization.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from computronium.domains.registry import SUPPORTED_TASKS


class DomainType(StrEnum):
    VISION = "vision"
    LANGUAGE = "language"
    RL = "rl"
    GRAPH = "graph"
    TABULAR = "tabular"
    MEMORY = "memory"
    SCIENTIFIC = "scientific"
    UNKNOWN = "unknown"


class CostClass(StrEnum):
    CHEAP = "cheap"  # < 1 min on GPU (xor, iris, spiral)
    MEDIUM = "medium"  # 1-10 min (mnist, digits, fashion_mnist)
    EXPENSIVE = "expensive"  # > 10 min (cifar10, language, RL)


@dataclass(frozen=True, slots=True)
class TaskObjective:
    """Objective specification for a task."""

    name: str
    direction: str  # "minimize" or "maximize"
    normalizer: str | None  # "minmax", "log", "zscore", "none"
    weight: float = 1.0
    is_measured: bool = False  # Whether the evaluator emits this metric
    payload_key: str | None = None  # Key in payload dict
    axis_tag: str | None = None
    description: str = ""


@dataclass(frozen=True, slots=True)
class TaskSpecEnriched:
    """Enriched task specification with cross-domain coverage info."""

    name: str
    domain: DomainType
    input_shape: tuple[int, ...] | None = None
    output_dim: int | None = None
    cost_class: CostClass = CostClass.MEDIUM
    primary_objective: str = "validation_accuracy"
    objectives: tuple[TaskObjective, ...] = field(default_factory=tuple)
    geometry_hint: str | None = None  # Suggested geometry for this task
    typical_batch_size: int = 32
    typical_lr: float = 1e-3
    tags: tuple[str, ...] = field(default_factory=tuple)
    description: str = ""

    def measured_objectives(self) -> list[TaskObjective]:
        """Return only objectives that are actually measured."""
        return [o for o in self.objectives if o.is_measured]

    def unmeasured_objectives(self) -> list[TaskObjective]:
        """Return objectives registered but not yet measured."""
        return [o for o in self.objectives if not o.is_measured]


# Task enrichments with domain, objectives, and cost class
TASK_ENRICHMENTS: dict[str, TaskSpecEnriched] = {
    # Vision tasks
    "xor": TaskSpecEnriched(
        name="xor",
        domain=DomainType.VISION,
        input_shape=(2,),
        output_dim=2,
        cost_class=CostClass.CHEAP,
        primary_objective="validation_accuracy",
        objectives=(
            TaskObjective(
                "validation_accuracy",
                "maximize",
                "minmax",
                1.0,
                True,
                "val_acc",
                "task",
                "Binary classification accuracy",
            ),
            TaskObjective(
                "validation_loss",
                "minimize",
                "log",
                0.5,
                True,
                "val_loss",
                "task",
                "Cross-entropy loss",
            ),
            TaskObjective(
                "walltime_total",
                "minimize",
                "minmax",
                0.3,
                True,
                "walltime_s",
                "cost",
                "Total wall time",
            ),
            TaskObjective(
                "param_count",
                "minimize",
                "minmax",
                0.2,
                True,
                "param_count",
                "cost",
                "Parameter count",
            ),
        ),
        geometry_hint="feedforward",
        typical_batch_size=32,
        typical_lr=1e-2,
        tags=("vision", "toy", "binary"),
        description="XOR problem - 2D binary classification",
    ),
    "spiral": TaskSpecEnriched(
        name="spiral",
        domain=DomainType.VISION,
        input_shape=(2,),
        output_dim=3,
        cost_class=CostClass.CHEAP,
        primary_objective="validation_accuracy",
        objectives=(
            TaskObjective(
                "validation_accuracy",
                "maximize",
                "minmax",
                1.0,
                True,
                "val_acc",
                "task",
                "Multi-class accuracy",
            ),
            TaskObjective(
                "validation_loss",
                "minimize",
                "log",
                0.5,
                True,
                "val_loss",
                "task",
                "Cross-entropy loss",
            ),
            TaskObjective(
                "walltime_total",
                "minimize",
                "minmax",
                0.3,
                True,
                "walltime_s",
                "cost",
                "Total wall time",
            ),
            TaskObjective(
                "param_count",
                "minimize",
                "minmax",
                0.2,
                True,
                "param_count",
                "cost",
                "Parameter count",
            ),
        ),
        geometry_hint="feedforward",
        typical_batch_size=32,
        typical_lr=1e-2,
        tags=("vision", "toy", "spiral"),
        description="Spiral classification - 2D 3-class",
    ),
    "circles": TaskSpecEnriched(
        name="circles",
        domain=DomainType.VISION,
        input_shape=(2,),
        output_dim=2,
        cost_class=CostClass.CHEAP,
        primary_objective="validation_accuracy",
        objectives=(
            TaskObjective(
                "validation_accuracy",
                "maximize",
                "minmax",
                1.0,
                True,
                "val_acc",
                "task",
            ),
            TaskObjective(
                "validation_loss", "minimize", "log", 0.5, True, "val_loss", "task"
            ),
            TaskObjective(
                "walltime_total", "minimize", "minmax", 0.3, True, "walltime_s", "cost"
            ),
            TaskObjective(
                "param_count", "minimize", "minmax", 0.2, True, "param_count", "cost"
            ),
        ),
        geometry_hint="feedforward",
        typical_batch_size=32,
        typical_lr=1e-2,
        tags=("vision", "toy", "circles"),
        description="Concentric circles binary classification",
    ),
    "digits": TaskSpecEnriched(
        name="digits",
        domain=DomainType.VISION,
        input_shape=(64,),
        output_dim=10,
        cost_class=CostClass.CHEAP,
        primary_objective="validation_accuracy",
        objectives=(
            TaskObjective(
                "validation_accuracy",
                "maximize",
                "minmax",
                1.0,
                True,
                "val_acc",
                "task",
            ),
            TaskObjective(
                "validation_loss", "minimize", "log", 0.5, True, "val_loss", "task"
            ),
            TaskObjective(
                "f1_score",
                "maximize",
                "minmax",
                0.5,
                False,
                "f1_score",
                "task",
                "Macro F1 score",
            ),
            TaskObjective(
                "walltime_total", "minimize", "minmax", 0.3, True, "walltime_s", "cost"
            ),
            TaskObjective(
                "param_count", "minimize", "minmax", 0.2, True, "param_count", "cost"
            ),
        ),
        geometry_hint="feedforward",
        typical_batch_size=32,
        typical_lr=1e-3,
        tags=("vision", "sklearn", "digits"),
        description="Scikit-learn digits dataset (8x8 images)",
    ),
    "mnist": TaskSpecEnriched(
        name="mnist",
        domain=DomainType.VISION,
        input_shape=(1, 28, 28),
        output_dim=10,
        cost_class=CostClass.MEDIUM,
        primary_objective="validation_accuracy",
        objectives=(
            TaskObjective(
                "validation_accuracy",
                "maximize",
                "minmax",
                1.0,
                True,
                "val_acc",
                "task",
            ),
            TaskObjective(
                "validation_loss", "minimize", "log", 0.5, True, "val_loss", "task"
            ),
            TaskObjective(
                "f1_score", "maximize", "minmax", 0.5, False, "f1_score", "task"
            ),
            TaskObjective(
                "walltime_total", "minimize", "minmax", 0.3, True, "walltime_s", "cost"
            ),
            TaskObjective(
                "param_count", "minimize", "minmax", 0.2, True, "param_count", "cost"
            ),
        ),
        geometry_hint="conv",
        typical_batch_size=64,
        typical_lr=1e-3,
        tags=("vision", "mnist", "classification"),
        description="MNIST handwritten digits",
    ),
    "fashion_mnist": TaskSpecEnriched(
        name="fashion_mnist",
        domain=DomainType.VISION,
        input_shape=(1, 28, 28),
        output_dim=10,
        cost_class=CostClass.MEDIUM,
        primary_objective="validation_accuracy",
        objectives=(
            TaskObjective(
                "validation_accuracy",
                "maximize",
                "minmax",
                1.0,
                True,
                "val_acc",
                "task",
            ),
            TaskObjective(
                "validation_loss", "minimize", "log", 0.5, True, "val_loss", "task"
            ),
            TaskObjective(
                "f1_score", "maximize", "minmax", 0.5, False, "f1_score", "task"
            ),
            TaskObjective(
                "walltime_total", "minimize", "minmax", 0.3, True, "walltime_s", "cost"
            ),
            TaskObjective(
                "param_count", "minimize", "minmax", 0.2, True, "param_count", "cost"
            ),
        ),
        geometry_hint="conv",
        typical_batch_size=64,
        typical_lr=1e-3,
        tags=("vision", "fashion", "classification"),
        description="Fashion-MNIST clothing classification",
    ),
    "kmnist": TaskSpecEnriched(
        name="kmnist",
        domain=DomainType.VISION,
        input_shape=(1, 28, 28),
        output_dim=10,
        cost_class=CostClass.MEDIUM,
        primary_objective="validation_accuracy",
        objectives=(
            TaskObjective(
                "validation_accuracy",
                "maximize",
                "minmax",
                1.0,
                True,
                "val_acc",
                "task",
            ),
            TaskObjective(
                "validation_loss", "minimize", "log", 0.5, True, "val_loss", "task"
            ),
            TaskObjective(
                "walltime_total", "minimize", "minmax", 0.3, True, "walltime_s", "cost"
            ),
            TaskObjective(
                "param_count", "minimize", "minmax", 0.2, True, "param_count", "cost"
            ),
        ),
        geometry_hint="conv",
        typical_batch_size=64,
        typical_lr=1e-3,
        tags=("vision", "kana", "classification"),
        description="Kuzushiji-MNIST Japanese characters",
    ),
    "usps": TaskSpecEnriched(
        name="usps",
        domain=DomainType.VISION,
        input_shape=(1, 16, 16),
        output_dim=10,
        cost_class=CostClass.MEDIUM,
        primary_objective="validation_accuracy",
        objectives=(
            TaskObjective(
                "validation_accuracy",
                "maximize",
                "minmax",
                1.0,
                True,
                "val_acc",
                "task",
            ),
            TaskObjective(
                "validation_loss", "minimize", "log", 0.5, True, "val_loss", "task"
            ),
            TaskObjective(
                "walltime_total", "minimize", "minmax", 0.3, True, "walltime_s", "cost"
            ),
            TaskObjective(
                "param_count", "minimize", "minmax", 0.2, True, "param_count", "cost"
            ),
        ),
        geometry_hint="conv",
        typical_batch_size=64,
        typical_lr=1e-3,
        tags=("vision", "usps", "classification"),
        description="USPS handwritten digits (16x16)",
    ),
    "cifar10": TaskSpecEnriched(
        name="cifar10",
        domain=DomainType.VISION,
        input_shape=(3, 32, 32),
        output_dim=10,
        cost_class=CostClass.EXPENSIVE,
        primary_objective="validation_accuracy",
        objectives=(
            TaskObjective(
                "validation_accuracy",
                "maximize",
                "minmax",
                1.0,
                True,
                "val_acc",
                "task",
            ),
            TaskObjective(
                "validation_loss", "minimize", "log", 0.5, True, "val_loss", "task"
            ),
            TaskObjective(
                "f1_score", "maximize", "minmax", 0.5, False, "f1_score", "task"
            ),
            TaskObjective(
                "walltime_total", "minimize", "minmax", 0.3, True, "walltime_s", "cost"
            ),
            TaskObjective(
                "param_count", "minimize", "minmax", 0.2, True, "param_count", "cost"
            ),
            TaskObjective(
                "energy_per_step",
                "minimize",
                "log",
                0.3,
                True,
                "energy_per_step",
                "cost",
            ),
        ),
        geometry_hint="conv",
        typical_batch_size=128,
        typical_lr=3e-4,
        tags=("vision", "cifar", "classification"),
        description="CIFAR-10 color images",
    ),
    "sequential_mnist": TaskSpecEnriched(
        name="sequential_mnist",
        domain=DomainType.VISION,
        input_shape=(1, 28, 28),
        output_dim=10,
        cost_class=CostClass.MEDIUM,
        primary_objective="validation_accuracy",
        objectives=(
            TaskObjective(
                "validation_accuracy",
                "maximize",
                "minmax",
                1.0,
                True,
                "val_acc",
                "task",
            ),
            TaskObjective(
                "validation_loss", "minimize", "log", 0.5, True, "val_loss", "task"
            ),
            TaskObjective(
                "backward_transfer",
                "maximize",
                "minmax",
                0.5,
                False,
                "backward_transfer",
                "task",
            ),
            TaskObjective(
                "forgetting", "minimize", "minmax", 0.5, False, "forgetting", "task"
            ),
            TaskObjective(
                "walltime_total", "minimize", "minmax", 0.3, True, "walltime_s", "cost"
            ),
        ),
        geometry_hint="recurrent",
        typical_batch_size=64,
        typical_lr=1e-3,
        tags=("vision", "sequential", "continual"),
        description="Sequential MNIST for continual learning",
    ),
    "copy_task": TaskSpecEnriched(
        name="copy_task",
        domain=DomainType.MEMORY,
        input_shape=(10,),  # Sequence length, binary
        output_dim=2,
        cost_class=CostClass.CHEAP,
        primary_objective="validation_accuracy",
        objectives=(
            TaskObjective(
                "validation_accuracy",
                "maximize",
                "minmax",
                1.0,
                True,
                "val_acc",
                "task",
            ),
            TaskObjective(
                "validation_loss", "minimize", "log", 0.5, True, "val_loss", "task"
            ),
            TaskObjective(
                "walltime_total", "minimize", "minmax", 0.3, True, "walltime_s", "cost"
            ),
        ),
        geometry_hint="ntm",
        typical_batch_size=16,
        typical_lr=1e-3,
        tags=("memory", "sequence", "copy"),
        description="Neural Turing Machine copy task",
    ),
    "tiny_shakespeare": TaskSpecEnriched(
        name="tiny_shakespeare",
        domain=DomainType.LANGUAGE,
        input_shape=(100,),  # seq_len
        output_dim=65,  # character vocab
        cost_class=CostClass.EXPENSIVE,
        primary_objective="perplexity",
        objectives=(
            TaskObjective(
                "perplexity",
                "minimize",
                "log",
                1.0,
                True,
                "perplexity",
                "task",
                "Language model perplexity",
            ),
            TaskObjective(
                "validation_loss", "minimize", "log", 0.5, True, "val_loss", "task"
            ),
            TaskObjective(
                "accuracy",
                "maximize",
                "minmax",
                0.3,
                True,
                "accuracy",
                "task",
                "Token-level accuracy",
            ),
            TaskObjective(
                "bleu_score",
                "maximize",
                "minmax",
                0.2,
                False,
                "bleu_score",
                "task",
                "BLEU score",
            ),
            TaskObjective(
                "walltime_total", "minimize", "minmax", 0.3, True, "walltime_s", "cost"
            ),
            TaskObjective(
                "param_count", "minimize", "minmax", 0.2, True, "param_count", "cost"
            ),
        ),
        geometry_hint="causal_transformer",
        typical_batch_size=16,
        typical_lr=3e-4,
        tags=("language", "char_lm", "shakespeare"),
        description="Tiny Shakespeare character-level LM",
    ),
    "char_ngram": TaskSpecEnriched(
        name="char_ngram",
        domain=DomainType.LANGUAGE,
        input_shape=(50,),
        output_dim=128,
        cost_class=CostClass.MEDIUM,
        primary_objective="perplexity",
        objectives=(
            TaskObjective(
                "perplexity", "minimize", "log", 1.0, True, "perplexity", "task"
            ),
            TaskObjective(
                "validation_loss", "minimize", "log", 0.5, True, "val_loss", "task"
            ),
            TaskObjective(
                "walltime_total", "minimize", "minmax", 0.3, True, "walltime_s", "cost"
            ),
        ),
        geometry_hint="causal_transformer",
        typical_batch_size=32,
        typical_lr=1e-3,
        tags=("language", "char_ngram"),
        description="Character n-gram language model",
    ),
    "pendulum": TaskSpecEnriched(
        name="pendulum",
        domain=DomainType.RL,
        input_shape=(3,),  # cos(theta), sin(theta), theta_dot
        output_dim=1,  # torque
        cost_class=CostClass.MEDIUM,
        primary_objective="mean_reward",
        objectives=(
            TaskObjective(
                "mean_reward",
                "maximize",
                "minmax",
                1.0,
                True,
                "mean_reward",
                "task",
                "Episode return",
            ),
            TaskObjective(
                "std_reward",
                "minimize",
                "minmax",
                0.3,
                True,
                "std_reward",
                "task",
                "Reward variance",
            ),
            TaskObjective(
                "mean_length",
                "minimize",
                "minmax",
                0.2,
                True,
                "mean_length",
                "task",
                "Episode length",
            ),
            TaskObjective(
                "walltime_total", "minimize", "minmax", 0.3, True, "walltime_s", "cost"
            ),
            TaskObjective(
                "param_count", "minimize", "minmax", 0.2, True, "param_count", "cost"
            ),
        ),
        geometry_hint="feedforward",
        typical_batch_size=32,
        typical_lr=3e-4,
        tags=("rl", "continuous", "pendulum"),
        description="Pendulum swing-up (continuous control)",
    ),
    "acrobot": TaskSpecEnriched(
        name="acrobot",
        domain=DomainType.RL,
        input_shape=(6,),
        output_dim=3,
        cost_class=CostClass.MEDIUM,
        primary_objective="mean_reward",
        objectives=(
            TaskObjective(
                "mean_reward", "maximize", "minmax", 1.0, True, "mean_reward", "task"
            ),
            TaskObjective(
                "std_reward", "minimize", "minmax", 0.3, True, "std_reward", "task"
            ),
            TaskObjective(
                "walltime_total", "minimize", "minmax", 0.3, True, "walltime_s", "cost"
            ),
        ),
        geometry_hint="feedforward",
        typical_batch_size=32,
        typical_lr=3e-4,
        tags=("rl", "acrobot"),
        description="Acrobot swing-up (discrete actions)",
    ),
    "cartpole": TaskSpecEnriched(
        name="cartpole",
        domain=DomainType.RL,
        input_shape=(4,),
        output_dim=2,
        cost_class=CostClass.CHEAP,
        primary_objective="mean_reward",
        objectives=(
            TaskObjective(
                "mean_reward", "maximize", "minmax", 1.0, True, "mean_reward", "task"
            ),
            TaskObjective(
                "std_reward", "minimize", "minmax", 0.3, True, "std_reward", "task"
            ),
            TaskObjective(
                "walltime_total", "minimize", "minmax", 0.3, True, "walltime_s", "cost"
            ),
        ),
        geometry_hint="feedforward",
        typical_batch_size=32,
        typical_lr=3e-4,
        tags=("rl", "cartpole"),
        description="CartPole balancing (discrete actions)",
    ),
    "cora": TaskSpecEnriched(
        name="cora",
        domain=DomainType.GRAPH,
        input_shape=(1433,),  # Node features
        output_dim=7,  # Classes
        cost_class=CostClass.MEDIUM,
        primary_objective="validation_accuracy",
        objectives=(
            TaskObjective(
                "validation_accuracy",
                "maximize",
                "minmax",
                1.0,
                True,
                "val_acc",
                "task",
            ),
            TaskObjective(
                "validation_loss", "minimize", "log", 0.5, True, "val_loss", "task"
            ),
            TaskObjective(
                "f1_score", "maximize", "minmax", 0.5, False, "f1_score", "task"
            ),
            TaskObjective(
                "walltime_total", "minimize", "minmax", 0.3, True, "walltime_s", "cost"
            ),
        ),
        geometry_hint="graph",
        typical_batch_size=1,  # Full graph
        typical_lr=1e-3,
        tags=("graph", "node_classification", "citation"),
        description="Cora citation network node classification",
    ),
    "citeseer": TaskSpecEnriched(
        name="citeseer",
        domain=DomainType.GRAPH,
        input_shape=(3703,),
        output_dim=6,
        cost_class=CostClass.MEDIUM,
        primary_objective="validation_accuracy",
        objectives=(
            TaskObjective(
                "validation_accuracy",
                "maximize",
                "minmax",
                1.0,
                True,
                "val_acc",
                "task",
            ),
            TaskObjective(
                "validation_loss", "minimize", "log", 0.5, True, "val_loss", "task"
            ),
            TaskObjective(
                "f1_score", "maximize", "minmax", 0.5, False, "f1_score", "task"
            ),
            TaskObjective(
                "walltime_total", "minimize", "minmax", 0.3, True, "walltime_s", "cost"
            ),
        ),
        geometry_hint="graph",
        typical_batch_size=1,
        typical_lr=1e-3,
        tags=("graph", "node_classification", "citation"),
        description="CiteSeer citation network node classification",
    ),
    "pubmed": TaskSpecEnriched(
        name="pubmed",
        domain=DomainType.GRAPH,
        input_shape=(500,),
        output_dim=3,
        cost_class=CostClass.MEDIUM,
        primary_objective="validation_accuracy",
        objectives=(
            TaskObjective(
                "validation_accuracy",
                "maximize",
                "minmax",
                1.0,
                True,
                "val_acc",
                "task",
            ),
            TaskObjective(
                "validation_loss", "minimize", "log", 0.5, True, "val_loss", "task"
            ),
            TaskObjective(
                "f1_score", "maximize", "minmax", 0.5, False, "f1_score", "task"
            ),
            TaskObjective(
                "walltime_total", "minimize", "minmax", 0.3, True, "walltime_s", "cost"
            ),
        ),
        geometry_hint="graph",
        typical_batch_size=1,
        typical_lr=1e-3,
        tags=("graph", "node_classification", "citation"),
        description="PubMed citation network node classification",
    ),
    "graph_classification": TaskSpecEnriched(
        name="graph_classification",
        domain=DomainType.GRAPH,
        input_shape=None,  # Variable
        output_dim=2,
        cost_class=CostClass.MEDIUM,
        primary_objective="validation_accuracy",
        objectives=(
            TaskObjective(
                "validation_accuracy",
                "maximize",
                "minmax",
                1.0,
                True,
                "val_acc",
                "task",
            ),
            TaskObjective(
                "f1_score", "maximize", "minmax", 0.5, False, "f1_score", "task"
            ),
            TaskObjective(
                "walltime_total", "minimize", "minmax", 0.3, True, "walltime_s", "cost"
            ),
        ),
        geometry_hint="graph",
        typical_batch_size=32,
        typical_lr=1e-3,
        tags=("graph", "graph_classification"),
        description="Graph classification benchmark",
    ),
    "breast_cancer": TaskSpecEnriched(
        name="breast_cancer",
        domain=DomainType.TABULAR,
        input_shape=(30,),
        output_dim=2,
        cost_class=CostClass.CHEAP,
        primary_objective="validation_accuracy",
        objectives=(
            TaskObjective(
                "validation_accuracy",
                "maximize",
                "minmax",
                1.0,
                True,
                "val_acc",
                "task",
            ),
            TaskObjective(
                "f1_score", "maximize", "minmax", 0.5, False, "f1_score", "task"
            ),
            TaskObjective(
                "walltime_total", "minimize", "minmax", 0.3, True, "walltime_s", "cost"
            ),
        ),
        geometry_hint="feedforward",
        typical_batch_size=32,
        typical_lr=1e-3,
        tags=("tabular", "sklearn", "medical"),
        description="Breast cancer Wisconsin dataset",
    ),
    "iris": TaskSpecEnriched(
        name="iris",
        domain=DomainType.TABULAR,
        input_shape=(4,),
        output_dim=3,
        cost_class=CostClass.CHEAP,
        primary_objective="validation_accuracy",
        objectives=(
            TaskObjective(
                "validation_accuracy",
                "maximize",
                "minmax",
                1.0,
                True,
                "val_acc",
                "task",
            ),
            TaskObjective(
                "f1_score", "maximize", "minmax", 0.5, False, "f1_score", "task"
            ),
            TaskObjective(
                "walltime_total", "minimize", "minmax", 0.3, True, "walltime_s", "cost"
            ),
        ),
        geometry_hint="feedforward",
        typical_batch_size=32,
        typical_lr=1e-3,
        tags=("tabular", "sklearn", "iris"),
        description="Iris flower classification",
    ),
    "wine": TaskSpecEnriched(
        name="wine",
        domain=DomainType.TABULAR,
        input_shape=(13,),
        output_dim=3,
        cost_class=CostClass.CHEAP,
        primary_objective="validation_accuracy",
        objectives=(
            TaskObjective(
                "validation_accuracy",
                "maximize",
                "minmax",
                1.0,
                True,
                "val_acc",
                "task",
            ),
            TaskObjective(
                "f1_score", "maximize", "minmax", 0.5, False, "f1_score", "task"
            ),
            TaskObjective(
                "walltime_total", "minimize", "minmax", 0.3, True, "walltime_s", "cost"
            ),
        ),
        geometry_hint="feedforward",
        typical_batch_size=32,
        typical_lr=1e-3,
        tags=("tabular", "sklearn", "wine"),
        description="Wine classification dataset",
    ),
}


class TaskRegistry:
    """Registry of enriched task specifications for cross-domain coverage."""

    def __init__(self) -> None:
        self._enrichments = TASK_ENRICHMENTS
        # Verify all supported tasks have enrichments
        missing = set(SUPPORTED_TASKS) - set(self._enrichments.keys())
        if missing:
            # Create default enrichments for missing tasks
            for task in missing:
                self._enrichments[task] = self._default_enrichment(task)

    def _default_enrichment(self, name: str) -> TaskSpecEnriched:
        """Create default enrichment for unknown tasks."""
        return TaskSpecEnriched(
            name=name,
            domain=DomainType.UNKNOWN,
            cost_class=CostClass.MEDIUM,
            primary_objective="validation_accuracy",
            objectives=(
                TaskObjective(
                    "validation_accuracy",
                    "maximize",
                    "minmax",
                    1.0,
                    False,
                    "val_acc",
                    "task",
                ),
                TaskObjective(
                    "validation_loss", "minimize", "log", 0.5, False, "val_loss", "task"
                ),
            ),
            description=f"Auto-generated enrichment for {name}",
        )

    def get(self, name: str) -> TaskSpecEnriched:
        """Get enriched task spec."""
        return self._enrichments.get(name, self._default_enrichment(name))

    def __contains__(self, name: str) -> bool:
        return name in self._enrichments

    def __iter__(self):
        return iter(self._enrichments.values())

    def by_domain(self, domain: DomainType) -> list[TaskSpecEnriched]:
        """Get all tasks for a domain."""
        return [t for t in self._enrichments.values() if t.domain == domain]

    def by_cost_class(self, cost: CostClass) -> list[TaskSpecEnriched]:
        """Get all tasks for a cost class."""
        return [t for t in self._enrichments.values() if t.cost_class == cost]

    def all_domains(self) -> set[DomainType]:
        """Get all domains present in the registry."""
        return {t.domain for t in self._enrichments.values()}

    def coverage_matrix(self) -> dict[DomainType, int]:
        """Count tasks per domain."""
        counts: dict[DomainType, int] = {}
        for task in self._enrichments.values():
            counts[task.domain] = counts.get(task.domain, 0) + 1
        return counts

    def unmeasured_objectives_report(self) -> dict[str, list[str]]:
        """Report unmeasured objectives per task."""
        report = {}
        for name, task in self._enrichments.items():
            unmeasured = [o.name for o in task.unmeasured_objectives()]
            if unmeasured:
                report[name] = unmeasured
        return report


def normalize_per_task_baseline(
    raw_values: dict[str, float],
    task_name: str,
    baseline_values: dict[str, float] | None = None,
) -> dict[str, float]:
    """Normalize raw values per task against baseline (ruler-relative).

    This implements F0b: raw values across vision/language/RL/graph are not
    comparable, so normalize against that task's online baseline.

    Args:
        raw_values: Raw objective values {objective_name: value}
        task_name: Task name for task-specific normalization
        baseline_values: Baseline values for the same objectives

    Returns:
        Normalized values where 0 = baseline, <0 = better than baseline
    """
    from computronium.experiment.optimization.multi_objective import (
        normalize_value,
    )
    from computronium.experiment.registry.task_registry import TaskRegistry

    registry = TaskRegistry()
    task_spec = registry.get(task_name)
    objectives = task_spec.measured_objectives()

    normalized = {}
    for obj in objectives:
        raw = raw_values.get(obj.name)
        if raw is None:
            continue

        baseline = baseline_values.get(obj.name) if baseline_values else None

        if baseline is not None:
            # Ruler-relative: (value - baseline) / baseline for ratios, or value - baseline for differences
            if obj.direction == "maximize":
                # For accuracy: (value - baseline) / baseline
                normalized[obj.name] = (raw - baseline) / max(abs(baseline), 1e-12)
            else:
                # For loss/perplexity/time: (baseline - value) / baseline
                normalized[obj.name] = (baseline - raw) / max(abs(baseline), 1e-12)
        else:
            # Fallback: use minmax normalization
            normalized[obj.name] = normalize_value(raw, obj.normalizer, obj.direction)

    return normalized


def get_task_registry() -> TaskRegistry:
    """Get the global task registry."""
    return TaskRegistry()


__all__ = [
    "TASK_ENRICHMENTS",
    "CostClass",
    "DomainType",
    "TaskObjective",
    "TaskRegistry",
    "TaskSpecEnriched",
    "get_task_registry",
    "normalize_per_task_baseline",
]
