"""Effect-size benchmark runner for learning policies.

Implements WP10 deliverable: run_acquisition_benchmark() for E2/E3 protocol.

Synthetic evaluation is a closed loop: each policy proposes coordinates in
small batches, the fixture scores them, and policies supporting
``observe_score`` learn between batches. The treatment/control contrast is
therefore a real policy effect, not a fixed draw.
"""

from __future__ import annotations

import hashlib
import math
import statistics
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

import numpy as np

from computronium.experiment.evidence.protocol import (
    CostBudget,
    CostBudgetKind,
    EffectSizeResult,
    compute_effect_size,
)

if TYPE_CHECKING:
    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.schema.axis import HyperparameterSpec
    from computronium.experiment.schema.coordinate import Coordinate


@runtime_checkable
class BenchmarkPolicy(Protocol):
    """Minimal policy surface the benchmark harness drives.

    Matches ``ProposalPolicy`` (surrogate.py); execution ``Policy`` objects
    need an adapter (their ``propose`` takes candidates/records/budget).
    """

    def propose(self, n: int, context: dict) -> list[Coordinate]: ...

    def get_name(self) -> str: ...


type PolicyFactory = Callable[[], BenchmarkPolicy]
"""Factory producing a fresh policy instance per task/seed.

Surrogate policies must not share training data across independent
task/seed combinations; this protocol ensures isolation.
"""


@dataclass(frozen=True, slots=True)
class BenchmarkTask:
    """A benchmark task with known or measurable ground truth.

    For synthetic tasks, the ground truth is known analytically.
    For real tasks, the ground truth is estimated from extensive prior runs.
    """

    task_id: str
    name: str
    # For synthetic tasks: the synthetic fixture
    synthetic_fixture: Any | None = None
    # For real tasks: the dataset/environment specification
    dataset_spec: dict[str, Any] | None = None
    # Expected effect size range (for power analysis)
    expected_effect_range: tuple[float, float] = (0.2, 1.0)


@dataclass(frozen=True, slots=True)
class BenchmarkConfig:
    """Configuration for an acquisition benchmark."""

    # Number of independent tasks (must be >= 10 per protocol)
    n_tasks: int = 10
    # Number of independent seeds per task (must be >= 5 per protocol)
    n_seeds: int = 5
    # Cost budget for each policy-task-seed combination
    budget: CostBudget = field(default_factory=lambda: CostBudget.eval_count(100))
    # Primary metric to optimize
    primary_metric: str = "validation_accuracy"
    # Whether to use paired design (same seeds for treatment and control)
    paired: bool = True
    # Whether to use Wilcoxon instead of paired t-test
    use_wilcoxon: bool = False


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    """Result of an acquisition benchmark."""

    # Effect size result (primary output)
    effect_size: EffectSizeResult
    # Per-task results
    task_results: dict[str, dict[str, list[float]]]
    # Raw scores for each policy on each task
    treatment_scores: dict[str, list[float]]  # task_id -> list of scores
    control_scores: dict[str, list[float]]  # task_id -> list of scores
    # Configuration used
    config: BenchmarkConfig
    # Metadata
    metadata: dict[str, Any] | None = None


def _generate_task_id(task_name: str, seed: int) -> str:
    """Generate a unique task ID for a task-seed combination."""
    return hashlib.sha256(f"{task_name}|{seed}".encode()).hexdigest()[:16]


def embedding_dims(dimension: int) -> list[HyperparameterSpec]:
    """First ``dimension`` Range specs in harvest order (fixed embedding dims)."""
    from computronium.experiment.schema.harvest import harvest_schema

    dims = [
        s
        for s in harvest_schema().hyperparameters
        if s.domain.lo is not None and s.domain.hi is not None
    ][:dimension]
    return dims


def coordinate_to_vector(
    coord: Coordinate,
    dimension: int,
    dims: list[HyperparameterSpec] | None = None,
) -> tuple[float, ...]:
    """Encode a coordinate as a locality-preserving [0,1)^dimension vector.

    Numeric params are min-max normalized against their registry Range
    (LOG scale in log space); missing/non-numeric entries map to 0.5.
    Structural axes are held fixed by the task — the synthetic benchmark
    measures continuous-param acquisition, not structural search.
    """
    if dims is None:
        dims = embedding_dims(dimension)
    vec: list[float] = []
    for i in range(dimension):
        if i < len(dims):
            spec = dims[i]
            lo = spec.domain.lo or 0.0
            hi = spec.domain.hi or 1.0
            raw = coord.params.get(spec.name, (lo + hi) / 2)
            try:
                v = float(raw)  # type: ignore[arg-type]
            except TypeError, ValueError:
                v = (lo + hi) / 2
            if hi <= lo:
                vec.append(0.5)
            elif spec.domain.scale.name == "LOG" and lo > 0 and v > 0:
                vec.append(
                    min(
                        1.0,
                        max(
                            0.0,
                            (math.log(v) - math.log(lo))
                            / (math.log(hi) - math.log(lo)),
                        ),
                    )
                )
            else:
                vec.append(min(1.0, max(0.0, (v - lo) / (hi - lo))))
        else:
            vec.append(0.5)
    return tuple(vec)


def _evaluate_policy_on_task(
    policy: BenchmarkPolicy,
    task: BenchmarkTask,
    seed: int,
    budget: CostBudget,
    primary_metric: str,
    store: RecordStore | None = None,
) -> float:
    """Evaluate a policy on a single task with a single seed.

    Closed loop: propose a batch, score it on the fixture, feed scores back
    via ``observe_score`` when supported, repeat until the budget is spent.
    Returns the best score seen (lower is better). Noise indices are
    eval-order based, so paired policies share the noise sequence prefix.
    """
    del primary_metric, store
    if task.synthetic_fixture is None:
        task_seed = int.from_bytes(
            hashlib.sha256(task.name.encode()).digest()[:8], "big"
        ) % (2**31)
        rng = np.random.RandomState(seed + task_seed)
        return float(rng.rand())

    fixture = task.synthetic_fixture
    total = int(budget.limit) if budget.kind == CostBudgetKind.EVAL_COUNT else 20
    batch = min(5, total)
    dims = embedding_dims(fixture.dimension)
    observe = getattr(policy, "observe_score", None)

    best = float("inf")
    done = 0
    round_idx = 0
    while done < total:
        m = min(batch, total - done)
        context = {
            "task_id": task.task_id,
            "seed": seed,
            "budget_limit": total,
            "round": round_idx,
            "history_best": best,
        }
        candidates = policy.propose(m, context)
        if not candidates:
            raise TypeError(
                f"Policy {policy.get_name()!r} returned no candidates; "
                "benchmark policies must implement propose(n, context)."
            )
        for j, coord in enumerate(candidates[:m]):
            score = fixture.evaluate(
                coordinate_to_vector(coord, fixture.dimension, dims),
                seed + round_idx * batch + j,
            )
            best = min(best, score)
            if observe is not None:
                observe(coord, score)
        done += m
        round_idx += 1
    return best


def run_acquisition_benchmark(  # ruff: ignore[too-many-locals]
    treatment_factory: PolicyFactory,
    control_factory: PolicyFactory,
    tasks: list[BenchmarkTask],
    config: BenchmarkConfig | None = None,
    store: RecordStore | None = None,
) -> BenchmarkResult:
    """Run an acquisition benchmark comparing two policies.

    Implements the E2/E3 effect-size protocol:
    - N_tasks >= 10 independent tasks
    - N_seeds >= 5 independent seeds per task
    - Fixed evaluation budget with explicit CostBudgetTier
    - Primary inference unit: task-level effect size
    - Reports Cohen's d, 95% CI, p-value (paired t-test or Wilcoxon)

    Args:
        treatment_factory: Factory producing fresh treatment policy per task/seed.
        control_factory: Factory producing fresh control policy per task/seed.
        tasks: List of benchmark tasks (must be >= 10).
        config: Benchmark configuration.
        store: Optional record store for persistence.

    Returns:
        BenchmarkResult with effect size and detailed results.

    Raises:
        ValueError: If protocol requirements not met (N_tasks < 10, N_seeds < 5).
    """
    if config is None:
        config = BenchmarkConfig()

    if len(tasks) < 10:
        raise ValueError(
            f"Protocol requires N_tasks >= 10, got {len(tasks)}. "
            "Provide at least 10 independent tasks."
        )
    if config.n_seeds < 5:
        raise ValueError(f"Protocol requires N_seeds >= 5, got {config.n_seeds}.")

    # Ensure we have enough tasks
    if len(tasks) > config.n_tasks:
        tasks = tasks[: config.n_tasks]

    treatment_scores: dict[str, list[float]] = {}
    control_scores: dict[str, list[float]] = {}
    task_results: dict[str, dict[str, list[float]]] = {}

    # Run each policy on each task with each seed
    for task in tasks:
        task_id = task.task_id
        treatment_scores[task_id] = []
        control_scores[task_id] = []
        task_results[task_id] = {"treatment": [], "control": []}

        for seed in range(config.n_seeds):
            # Fresh policy instances per task/seed (critical for surrogate isolation)
            treatment_policy = treatment_factory()
            control_policy = control_factory()

            # Evaluate treatment policy
            treatment_score = _evaluate_policy_on_task(
                treatment_policy,
                task,
                seed,
                config.budget,
                config.primary_metric,
                store,
            )
            treatment_scores[task_id].append(treatment_score)
            task_results[task_id]["treatment"].append(treatment_score)

            # Evaluate control policy (paired: same seed)
            control_seed = seed if config.paired else seed + 1000
            control_score = _evaluate_policy_on_task(
                control_policy,
                task,
                control_seed,
                config.budget,
                config.primary_metric,
                store,
            )
            control_scores[task_id].append(control_score)
            task_results[task_id]["control"].append(control_score)
            control_scores[task_id].append(control_score)
            task_results[task_id]["control"].append(control_score)

    # Aggregate per-task: compute mean score per task for each policy
    treatment_task_means = {
        task_id: statistics.mean(scores) for task_id, scores in treatment_scores.items()
    }
    control_task_means = {
        task_id: statistics.mean(scores) for task_id, scores in control_scores.items()
    }

    # Build paired task-level arrays
    paired_treatment = [treatment_task_means[task.task_id] for task in tasks]
    paired_control = [control_task_means[task.task_id] for task in tasks]

    # Compute effect size using the protocol function
    effect_size = compute_effect_size(
        treatment=paired_treatment,
        control=paired_control,
        primary_metric=config.primary_metric,
        budget=config.budget,
        n_tasks=len(tasks),
        n_seeds=config.n_seeds,
        paired=config.paired,
        use_wilcoxon=config.use_wilcoxon,
    )

    # Build metadata
    metadata = {
        "treatment_policy": treatment_policy.get_name()
        if hasattr(treatment_policy, "get_name")
        else "unknown",
        "control_policy": control_policy.get_name()
        if hasattr(control_policy, "get_name")
        else "unknown",
        "n_tasks": len(tasks),
        "n_seeds": config.n_seeds,
        "budget_kind": config.budget.kind.value,
        "budget_limit": config.budget.limit,
        "primary_metric": config.primary_metric,
        "paired": config.paired,
        "test_used": effect_size.test_used,
    }

    return BenchmarkResult(
        effect_size=effect_size,
        task_results=task_results,
        treatment_scores=treatment_scores,
        control_scores=control_scores,
        config=config,
        metadata=metadata,
    )


def create_synthetic_benchmark_tasks(
    n_tasks: int = 10,
    dimension: int = 6,
    noise_std: float = 0.1,
    interaction_strength: float = 0.3,
) -> list[BenchmarkTask]:
    """Create synthetic benchmark tasks from the synthetic fixture.

    Uses the SyntheticGroundTruth fixture from evidence.protocol
    to create tasks with known analytical ground truth.

    Args:
        n_tasks: Number of tasks to create (must be >= 10).
        dimension: Dimension of the synthetic problem.
        noise_std: Noise standard deviation.
        interaction_strength: Interaction strength for axis interactions.

    Returns:
        List of BenchmarkTask objects with synthetic fixtures.
    """
    from computronium.experiment.evidence.protocol import SyntheticGroundTruth

    if n_tasks < 10:
        raise ValueError("Protocol requires at least 10 tasks")

    tasks = []
    for i in range(n_tasks):
        # Optimum uniform in [0,1)^dimension: matches the encoder output range
        # so every task is solvable by acquisition (seeded per task index).
        task_rng = np.random.RandomState(0xBEAC0000 + i)
        optimum = tuple(float(v) for v in task_rng.rand(dimension))

        interaction_matrix = []
        for j in range(dimension):
            row = []
            for k in range(dimension):
                if j == k:
                    row.append(1.0)
                else:
                    row.append(interaction_strength)
            interaction_matrix.append(tuple(row))

        fixture = SyntheticGroundTruth(
            dimension=dimension,
            optimum=optimum,
            interaction_matrix=tuple(interaction_matrix),
            noise_std=noise_std,
        )

        task = BenchmarkTask(
            task_id=f"synthetic_{i}",
            name=f"Synthetic Task {i}",
            synthetic_fixture=fixture,
            expected_effect_range=(0.5, 2.0),
        )
        tasks.append(task)

    return tasks


__all__ = [
    "BenchmarkConfig",
    "BenchmarkPolicy",
    "BenchmarkResult",
    "BenchmarkTask",
    "PolicyFactory",
    "create_synthetic_benchmark_tasks",
    "run_acquisition_benchmark",
]
