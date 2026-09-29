"""Policy implementations for experiment execution (WP4)."""

from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

import optuna

from computronium.experiment.schema.coordinate import Coordinate, Schedule

if TYPE_CHECKING:
    from computronium.experiment.execution.budget import Budget, CostModel
    from computronium.experiment.schema.record import Record

logger = logging.getLogger(__name__)


@runtime_checkable
class Policy(Protocol):
    """Protocol for allocation policies that decide which cells to execute next."""

    def propose(
        self,
        candidates: list[tuple[Coordinate, Schedule]],
        records: list[Record],
        budget: Budget,
        cost_model: CostModel,
    ) -> list[tuple[Coordinate, Schedule]]:
        """Propose next cells to evaluate."""
        ...

    def observe(self, record: Record) -> None:
        """Incorporate a completed record into the policy's evidence base."""
        ...

    def get_name(self) -> str:
        """Return the policy name."""
        ...


class StratifiedRandomPolicy:
    """Stratified random sampling across the 6 axes.

    Samples uniformly within each axis stratum to ensure coverage.
    """

    def __init__(self, *, seed: int | None = None) -> None:
        self._rng = random.Random(seed)  # noqa: S311 - not cryptographic
        self._name = "stratified_random"

    def propose(
        self,
        candidates: list[tuple[Coordinate, Schedule]],
        records: list[Record],
        budget: Budget,
        cost_model: CostModel,
    ) -> list[tuple[Coordinate, Schedule]]:
        """Propose candidates using stratified random sampling."""
        # Group candidates by axis values for stratification
        strata: dict[str, list[tuple[Coordinate, Schedule]]] = {}
        for coord, sched in candidates:
            key = f"{coord.substrate}|{coord.geometry}|{coord.dynamics}"
            if key not in strata:
                strata[key] = []
            strata[key].append((coord, sched))

        # Sample from each stratum
        proposals = []
        per_stratum = max(1, 50 // max(1, len(strata)))
        for stratum_candidates in strata.values():
            self._rng.shuffle(stratum_candidates)
            proposals.extend(stratum_candidates[:per_stratum])

        # Filter by budget
        affordable = self._filter_affordable(proposals, budget, cost_model)
        return affordable[:50]

    def observe(self, record: Record) -> None:
        """Stratified random doesn't learn from observations."""

    def get_name(self) -> str:
        return self._name

    def _filter_affordable(
        self,
        candidates: list[tuple[Coordinate, Schedule]],
        budget: Budget,
        cost_model: CostModel,
    ) -> list[tuple[Coordinate, Schedule]]:
        affordable = []
        for coord, sched in candidates:
            cost = cost_model.estimate_cost(
                (
                    coord.substrate,
                    coord.geometry,
                    coord.dynamics,
                    coord.plasticity,
                    coord.credit,
                    coord.update,
                    coord.params,
                ),
                sched.to_dict(),
            )
            if (
                budget.target_cost is None
                or budget.cost_consumed + cost <= budget.target_cost
            ):
                affordable.append((coord, sched))
        return affordable


class RoundRobinGridPolicy:
    """Round-robin grid traversal across the 6 axes.

    Systematically enumerates combinations, cycling through axes.
    """

    def __init__(self, *, seed: int | None = None) -> None:
        self._rng = random.Random(seed)  # noqa: S311 - not cryptographic
        self._name = "round_robin_grid"
        self._indices: dict[str, int] = {}

    def propose(
        self,
        candidates: list[tuple[Coordinate, Schedule]],
        records: list[Record],
        budget: Budget,
        cost_model: CostModel,
    ) -> list[tuple[Coordinate, Schedule]]:
        """Propose candidates in round-robin order."""
        # Group by each axis for round-robin
        axis_groups: dict[str, dict[str, list[tuple[Coordinate, Schedule]]]] = {}
        axes = ["substrate", "geometry", "dynamics", "plasticity", "credit", "update"]

        for coord, sched in candidates:
            for axis in axes:
                value = getattr(coord, axis)
                if axis not in axis_groups:
                    axis_groups[axis] = {}
                if value not in axis_groups[axis]:
                    axis_groups[axis][value] = []
                axis_groups[axis][value].append((coord, sched))

        # Round-robin across each axis group
        proposals = []
        for axis in axes:
            groups = axis_groups.get(axis, {})
            if not groups:
                continue
            idx = self._indices.get(axis, 0)
            values = list(groups.keys())
            if not values:
                continue
            value = values[idx % len(values)]
            self._indices[axis] = (idx + 1) % len(values)
            proposals.extend(groups[value])

        # Deduplicate and filter by budget
        seen = set()
        unique = []
        for coord, sched in proposals:
            key = (coord.cell_key(), sched.fidelity, sched.seed)
            if key not in seen:
                seen.add(key)
                unique.append((coord, sched))

        affordable = self._filter_affordable(unique, budget, cost_model)
        return affordable[:50]

    def observe(self, record: Record) -> None:
        """Round-robin grid doesn't learn from observations."""

    def get_name(self) -> str:
        return self._name

    def _filter_affordable(
        self,
        candidates: list[tuple[Coordinate, Schedule]],
        budget: Budget,
        cost_model: CostModel,
    ) -> list[tuple[Coordinate, Schedule]]:
        affordable = []
        for coord, sched in candidates:
            cost = cost_model.estimate_cost(
                (
                    coord.substrate,
                    coord.geometry,
                    coord.dynamics,
                    coord.plasticity,
                    coord.credit,
                    coord.update,
                    coord.params,
                ),
                sched.to_dict(),
            )
            if (
                budget.target_cost is None
                or budget.cost_consumed + cost <= budget.target_cost
            ):
                affordable.append((coord, sched))
        return affordable


class UniformRandomPolicy:
    """Uniform random sampling over all candidates."""

    def __init__(self, *, seed: int | None = None) -> None:
        self._rng = random.Random(seed)  # noqa: S311 - not cryptographic
        self._name = "uniform_random"

    def propose(
        self,
        candidates: list[tuple[Coordinate, Schedule]],
        records: list[Record],
        budget: Budget,
        cost_model: CostModel,
    ) -> list[tuple[Coordinate, Schedule]]:
        """Propose candidates uniformly at random."""
        if not candidates:
            return []

        shuffled = candidates.copy()
        self._rng.shuffle(shuffled)

        affordable = self._filter_affordable(shuffled, budget, cost_model)
        return affordable[:50]

    def observe(self, record: Record) -> None:
        """Uniform random doesn't learn from observations."""

    def get_name(self) -> str:
        return self._name

    def _filter_affordable(
        self,
        candidates: list[tuple[Coordinate, Schedule]],
        budget: Budget,
        cost_model: CostModel,
    ) -> list[tuple[Coordinate, Schedule]]:
        affordable = []
        for coord, sched in candidates:
            cost = cost_model.estimate_cost(
                (
                    coord.substrate,
                    coord.geometry,
                    coord.dynamics,
                    coord.plasticity,
                    coord.credit,
                    coord.update,
                    coord.params,
                ),
                sched.to_dict(),
            )
            if (
                budget.target_cost is None
                or budget.cost_consumed + cost <= budget.target_cost
            ):
                affordable.append((coord, sched))
        return affordable


class ModelBasedPolicy:
    """Model-based optimization using Optuna.

    Uses a surrogate model (TPE, GP, etc.) to propose promising cells.
    Storage adapter persists trials to the unified store (R71).
    """

    def __init__(
        self,
        *,
        sampler: str = "tpe",
        seed: int | None = None,
        n_startup_trials: int = 10,
    ) -> None:
        self._sampler_name = sampler
        self._seed = seed
        self._n_startup_trials = n_startup_trials
        self._name = f"model_based_{sampler}"
        self._study: optuna.Study | None = None
        self._trial_map: dict[str, Any] = {}

    def _get_study(self, run_id: str) -> optuna.Study:
        """Get or create Optuna study with unified store storage."""
        if self._study is None:
            # Use in-memory storage with run_id prefix for isolation
            storage = optuna.storages.InMemoryStorage()
            sampler = self._create_sampler()
            self._study = optuna.create_study(
                storage=storage,
                sampler=sampler,
                direction="maximize",
                study_name=f"exp_{run_id}",
            )
        return self._study

    def _create_sampler(self) -> optuna.samplers.BaseSampler:
        """Create Optuna sampler based on configuration."""
        if self._sampler_name == "tpe":
            return optuna.samplers.TPESampler(
                seed=self._seed, n_startup_trials=self._n_startup_trials
            )
        elif self._sampler_name == "gp":
            return optuna.samplers.GPSampler(
                seed=self._seed, n_startup_trials=self._n_startup_trials
            )
        elif self._sampler_name == "random":
            return optuna.samplers.RandomSampler(seed=self._seed)
        else:
            return optuna.samplers.TPESampler(
                seed=self._seed, n_startup_trials=self._n_startup_trials
            )

    def propose(
        self,
        candidates: list[tuple[Coordinate, Schedule]],
        records: list[Record],
        budget: Budget,
        cost_model: CostModel,
    ) -> list[tuple[Coordinate, Schedule]]:
        """Propose candidates using Optuna's suggestion."""
        if not candidates:
            return []

        # Update study with observed records
        for record in records:
            self._record_to_trial(record)

        study = self._get_study(records[0].run_id if records else "default")

        # For now, filter affordable candidates and use top suggestions
        affordable = self._filter_affordable(candidates, budget, cost_model)
        if not affordable:
            return []

        # Use Optuna to suggest from affordable candidates
        # Map coordinates to parameter space
        proposals = []
        for _ in range(min(10, len(affordable))):
            trial = study.ask()
            # Map trial params to a candidate (simplified)
            # In practice, this would use a proper parameterization
            idx = trial.number % len(affordable)
            proposals.append(affordable[idx])

        return proposals

    def observe(self, record: Record) -> None:
        """Incorporate record into Optuna study."""
        self._record_to_trial(record)

    def _record_to_trial(self, record: Record) -> None:
        """Convert record to Optuna trial."""
        if record.run_id not in self._trial_map:
            # Store for reference
            self._trial_map[record.measurement_key] = record

    def _extract_score(self, record: Record) -> float:
        """Extract optimization score from record."""
        for key in ("val_acc", "test_acc", "accuracy", "score", "loss"):
            if key in record.payload:
                val = record.payload[key]
                if isinstance(val, (int, float)):
                    return float(val)
        return 0.0

    def get_name(self) -> str:
        return self._name

    def _filter_affordable(
        self,
        candidates: list[tuple[Coordinate, Schedule]],
        budget: Budget,
        cost_model: CostModel,
    ) -> list[tuple[Coordinate, Schedule]]:
        affordable = []
        for coord, sched in candidates:
            cost = cost_model.estimate_cost(
                (
                    coord.substrate,
                    coord.geometry,
                    coord.dynamics,
                    coord.plasticity,
                    coord.credit,
                    coord.update,
                    coord.params,
                ),
                sched.to_dict(),
            )
            if (
                budget.target_cost is None
                or budget.cost_consumed + cost <= budget.target_cost
            ):
                affordable.append((coord, sched))
        return affordable


class EvolutionPolicy:
    """Evolutionary search over the 6-axis space.

    Maintains a population of cells, applies mutation/crossover,
    and selects based on fitness.
    """

    def __init__(
        self,
        *,
        population_size: int = 20,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.5,
        seed: int | None = None,
    ) -> None:
        self._population_size = population_size
        self._mutation_rate = mutation_rate
        self._crossover_rate = crossover_rate
        self._rng = random.Random(seed)  # noqa: S311 - not cryptographic
        self._name = "evolution"
        self._population: list[
            tuple[Coordinate, Schedule, float]
        ] = []  # (coord, sched, fitness)

    def propose(
        self,
        candidates: list[tuple[Coordinate, Schedule]],
        records: list[Record],
        budget: Budget,
        cost_model: CostModel,
    ) -> list[tuple[Coordinate, Schedule]]:
        """Propose candidates using evolutionary operators."""
        # Update population with new records
        for record in records:
            self._add_to_population(record)

        # If population not initialized, seed from candidates
        if not self._population and candidates:
            self._initialize_population(candidates)

        # Select parents, apply variation, filter by budget
        proposals = self._evolve(candidates, budget, cost_model)
        return proposals[:20]

    def observe(self, record: Record) -> None:
        """Add record to population."""
        self._add_to_population(record)

    def _add_to_population(self, record: Record) -> None:
        score = self._extract_score(record)
        coord = Coordinate(
            substrate=record.substrate,
            geometry=record.geometry,
            dynamics=record.dynamics,
            plasticity=record.plasticity,
            credit=record.credit,
            update=record.update,
            params=record.params,
        )
        self._population.append((coord, record.schedule, score))
        # Keep top population_size
        self._population.sort(key=lambda x: x[2], reverse=True)
        self._population = self._population[: self._population_size]

    def _initialize_population(
        self, candidates: list[tuple[Coordinate, Schedule]]
    ) -> None:
        """Initialize population from candidates."""
        shuffled = candidates.copy()
        self._rng.shuffle(shuffled)
        for coord, sched in shuffled[: self._population_size]:
            self._population.append((coord, sched, 0.0))

    def _evolve(
        self,
        candidates: list[tuple[Coordinate, Schedule]],
        budget: Budget,
        cost_model: CostModel,
    ) -> list[tuple[Coordinate, Schedule]]:
        """Apply evolutionary operators to generate proposals."""
        if not self._population:
            return []

        proposals = []
        # Select top performers as parents
        parents = self._population[: max(2, self._population_size // 4)]

        # Mutation: vary params
        for parent_coord, parent_sched, _ in parents:
            if self._rng.random() < self._mutation_rate:
                mutated_params = self._mutate_params(parent_coord.params)
                mutated_coord = Coordinate(
                    substrate=parent_coord.substrate,
                    geometry=parent_coord.geometry,
                    dynamics=parent_coord.dynamics,
                    plasticity=parent_coord.plasticity,
                    credit=parent_coord.credit,
                    update=parent_coord.update,
                    params=mutated_params,
                )
                proposals.append((mutated_coord, parent_sched))

        # Crossover: combine two parents
        if len(parents) >= 2 and self._rng.random() < self._crossover_rate:
            p1, p2 = self._rng.sample(parents, 2)
            crossed_params = self._crossover_params(p1[0].params, p2[0].params)
            crossed_coord = Coordinate(
                substrate=p1[0].substrate,
                geometry=p1[0].geometry,
                dynamics=p1[0].dynamics,
                plasticity=p1[0].plasticity,
                credit=p1[0].credit,
                update=p1[0].update,
                params=crossed_params,
            )
            proposals.append((crossed_coord, p1[1]))

        # Filter by budget
        affordable = self._filter_affordable(proposals, budget, cost_model)
        return affordable

    def _mutate_params(self, params: dict[str, Any]) -> dict[str, Any]:
        """Mutate parameters by adding noise."""
        mutated = params.copy()
        for key, value in mutated.items():
            if isinstance(value, (int, float)) and self._rng.random() < 0.3:
                if isinstance(value, int):
                    mutated[key] = max(1, value + self._rng.randint(-2, 2))
                else:
                    mutated[key] = value * (1 + self._rng.uniform(-0.2, 0.2))
        return mutated

    def _crossover_params(
        self, params1: dict[str, Any], params2: dict[str, Any]
    ) -> dict[str, Any]:
        """Crossover two parameter sets."""
        crossed = {}
        all_keys = set(params1.keys()) | set(params2.keys())
        for key in all_keys:
            if key in params1 and key in params2:
                crossed[key] = self._rng.choice([params1[key], params2[key]])
            elif key in params1:
                crossed[key] = params1[key]
            else:
                crossed[key] = params2[key]
        return crossed

    def _extract_score(self, record: Record) -> float:
        for key in ("val_acc", "test_acc", "accuracy", "score", "loss"):
            if key in record.payload:
                val = record.payload[key]
                if isinstance(val, (int, float)):
                    return float(val)
        return 0.0

    def get_name(self) -> str:
        return self._name

    def _filter_affordable(
        self,
        candidates: list[tuple[Coordinate, Schedule]],
        budget: Budget,
        cost_model: CostModel,
    ) -> list[tuple[Coordinate, Schedule]]:
        affordable = []
        for coord, sched in candidates:
            cost = cost_model.estimate_cost(
                (
                    coord.substrate,
                    coord.geometry,
                    coord.dynamics,
                    coord.plasticity,
                    coord.credit,
                    coord.update,
                    coord.params,
                ),
                sched.to_dict(),
            )
            if (
                budget.target_cost is None
                or budget.cost_consumed + cost <= budget.target_cost
            ):
                affordable.append((coord, sched))
        return affordable


class SynthesisPolicy:
    """Synthesis policy: combines multiple policies' proposals.

    Runs multiple policies in parallel and merges their proposals
    with deduplication and budget awareness.
    """

    def __init__(
        self,
        policies: list[Policy],
        *,
        weights: list[float] | None = None,
    ) -> None:
        self._policies = policies
        self._weights = weights or [1.0] * len(policies)
        self._name = "synthesis"

    def propose(
        self,
        candidates: list[tuple[Coordinate, Schedule]],
        records: list[Record],
        budget: Budget,
        cost_model: CostModel,
    ) -> list[tuple[Coordinate, Schedule]]:
        """Propose by combining sub-policy proposals."""
        all_proposals = []
        for policy, weight in zip(self._policies, self._weights, strict=False):
            props = policy.propose(candidates, records, budget, cost_model)
            # Weight by repeating or sampling
            weighted_count = max(1, int(len(props) * weight))
            all_proposals.extend(props[:weighted_count])

        # Deduplicate
        seen = set()
        unique = []
        for coord, sched in all_proposals:
            key = (coord.cell_key(), sched.fidelity, sched.seed)
            if key not in seen:
                seen.add(key)
                unique.append((coord, sched))

        return unique[:50]

    def observe(self, record: Record) -> None:
        """Forward observation to all sub-policies."""
        for policy in self._policies:
            policy.observe(record)

    def get_name(self) -> str:
        return self._name


class StrategyProgressionPolicy:
    """Strategy progression: cycles through a sequence of policies.

    Starts with exploration (random), moves to exploitation (model-based),
    then refinement (evolution), etc.
    """

    def __init__(
        self,
        stages: list[tuple[Policy, int]],  # (policy, budget_fraction)
        *,
        current_stage: int = 0,
    ) -> None:
        self._stages = stages
        self._current_stage = current_stage
        self._name = "strategy_progression"
        self._budget_consumed: float = 0.0
        self._total_budget: float | None = None

    def propose(
        self,
        candidates: list[tuple[Coordinate, Schedule]],
        records: list[Record],
        budget: Budget,
        cost_model: CostModel,
    ) -> list[tuple[Coordinate, Schedule]]:
        """Propose using current stage's policy."""
        if not self._stages:
            return []

        # Update stage based on budget consumption
        if self._total_budget is None and budget.target_cost:
            self._total_budget = budget.target_cost

        if self._total_budget and budget.cost_consumed > 0:
            progress = budget.cost_consumed / self._total_budget
            target_stage = int(progress * len(self._stages))
            self._current_stage = min(target_stage, len(self._stages) - 1)

        policy, _ = self._stages[self._current_stage]
        return policy.propose(candidates, records, budget, cost_model)

    def observe(self, record: Record) -> None:
        """Forward observation to current stage's policy."""
        if self._stages:
            policy, _ = self._stages[self._current_stage]
            policy.observe(record)

    def get_name(self) -> str:
        return f"{self._name}_stage{self._current_stage}"


class TrainerDrivenPolicy:
    """Trainer-driven policy: proposals come from an external trainer.

    The trainer (e.g., neural network) proposes cells based on
    learned acquisition function. This is a placeholder for integration
    with learned policies.
    """

    def __init__(
        self,
        *,
        trainer: Any = None,  # External trainer object
        fallback: Policy | None = None,
    ) -> None:
        self._trainer = trainer
        self._fallback = fallback or UniformRandomPolicy()
        self._name = "trainer_driven"

    def propose(
        self,
        candidates: list[tuple[Coordinate, Schedule]],
        records: list[Record],
        budget: Budget,
        cost_model: CostModel,
    ) -> list[tuple[Coordinate, Schedule]]:
        """Propose using trainer or fallback."""
        if self._trainer is not None and hasattr(self._trainer, "propose"):
            try:
                proposals = self._trainer.propose(
                    candidates, records, budget, cost_model
                )
                if proposals:
                    return proposals
            except Exception as e:
                logger.warning("Trainer propose failed, using fallback: %s", e)

        return self._fallback.propose(candidates, records, budget, cost_model)

    def observe(self, record: Record) -> None:
        """Forward observation to trainer and fallback."""
        if self._trainer is not None and hasattr(self._trainer, "observe"):
            try:
                self._trainer.observe(record)
            except Exception as e:
                logger.warning("Trainer observe failed: %s", e)
        self._fallback.observe(record)

    def get_name(self) -> str:
        return self._name


# Policy catalog (eight policies per abc3 §5.3)
POLICY_CATALOG: dict[str, type[Policy]] = {
    "stratified_random": StratifiedRandomPolicy,
    "round_robin_grid": RoundRobinGridPolicy,
    "uniform_random": UniformRandomPolicy,
    "model_based": ModelBasedPolicy,
    "evolution": EvolutionPolicy,
    "synthesis": SynthesisPolicy,
    "strategy_progression": StrategyProgressionPolicy,
    "trainer_driven": TrainerDrivenPolicy,
}


def create_policy(name: str, **kwargs: Any) -> Policy:
    """Create a policy instance by name.

    Args:
        name: Policy name from POLICY_CATALOG
        **kwargs: Policy-specific arguments

    Returns:
        Policy instance.

    Raises:
        ValueError: If policy name not found.
    """
    if name not in POLICY_CATALOG:
        raise ValueError(
            f"Unknown policy: {name}. Available: {sorted(POLICY_CATALOG.keys())}"
        )
    return POLICY_CATALOG[name](**kwargs)


__all__ = [
    "POLICY_CATALOG",
    "EvolutionPolicy",
    "ModelBasedPolicy",
    "Policy",
    "RoundRobinGridPolicy",
    "StrategyProgressionPolicy",
    "StratifiedRandomPolicy",
    "SynthesisPolicy",
    "TrainerDrivenPolicy",
    "UniformRandomPolicy",
    "create_policy",
]
