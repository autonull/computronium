"""Policy implementations for experiment execution (WP4/9).

A policy *generates* cells: ``propose(ctx)`` is handed the run's active space,
its constraints, its task and its budget — never a list of candidates to choose
between (TODO46 §3.3, plan3 WP14). The generator in
:mod:`computronium.experiment.execution.search_space` is the one that walks the
space, and :class:`ProposalContext` is the single place legality is applied.
"""

from __future__ import annotations

import inspect
import logging
import random
from dataclasses import dataclass, replace
from itertools import islice
from typing import TYPE_CHECKING, Any, Final, Protocol, runtime_checkable

import optuna
from optuna.distributions import (
    BaseDistribution,
    FloatDistribution,
    IntDistribution,
)
from optuna.study import StudyDirection

from computronium.experiment.execution.optuna_adapter import OptunaDistributionAdapter
from computronium.experiment.execution.search_space import (
    ShapeResolver,
    iter_candidates,
)
from computronium.experiment.execution.stage import Proposal
from computronium.experiment.schema.coordinate import Coordinate, Schedule
from computronium.experiment.schema.metrics import objective_metric, objective_values
from computronium.experiment.schema.registries import OBJECTIVES_REGISTRY

if TYPE_CHECKING:
    from collections.abc import Iterator

    from computronium.experiment.execution.budget import Budget, CostModel
    from computronium.experiment.execution.search_space import SearchSpace
    from computronium.experiment.schema.record import Record
    from computronium.experiment.schema.run_spec import RunSpec

logger = logging.getLogger(__name__)

# How many legal cells a policy draws before it chooses among them. A sampling
# policy needs a pool to sample from; the pool is the run's own space, never a
# list the caller enumerated.
_POOL: Final = 50


def resolve_objectives(
    objective_names: tuple[str, ...],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Resolve objective names and directions from the OBJECTIVES registry.

    Args:
        objective_names: Objective names from the run spec.

    Returns:
        The registry's names and, per objective, its direction.

    Raises:
        UnknownObjectiveError: A name is not a registered objective.
        UnmeasuredObjectiveError: A name is registered but no measurement
            produces it. A study told an objective nobody measured would
            optimize a number that does not exist, which is the silent maximize
            this replaces.
    """
    for name in objective_names:
        objective_metric(name)
    specs = [OBJECTIVES_REGISTRY[name] for name in objective_names]
    return tuple(spec.name for spec in specs), tuple(spec.direction for spec in specs)


def _cost(coord: Coordinate, sched: Schedule, cost_model: CostModel) -> float:
    """What the cost model charges one cell."""
    return cost_model.estimate_cost(
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


def _affordable(
    candidates: list[tuple[Coordinate, Schedule]],
    budget: Budget,
    cost_model: CostModel,
) -> list[tuple[Coordinate, Schedule]]:
    """The candidates this budget can still pay for.

    One implementation for every policy: five copies of this loop differed only
    in their risk of drifting apart.
    """
    return [
        (coord, sched)
        for coord, sched in candidates
        if budget.target_cost is None
        or budget.cost_consumed + _cost(coord, sched, cost_model) <= budget.target_cost
    ]


def _sampled_value(value: Any, distribution: BaseDistribution) -> Any:
    """A coordinate's value in the type its distribution samples."""
    if isinstance(distribution, FloatDistribution):
        return float(value)
    if isinstance(distribution, IntDistribution):
        return int(value)
    return value


@runtime_checkable
class RecordSource(Protocol):
    """The slice of the record store a policy reads.

    The unified store is the only history (R71); naming the one method a policy
    needs keeps that a structural fact rather than a convention.
    """

    def query_records(
        self, run_id: str | None = None, limit: int | None = None
    ) -> list[Record]:
        """This run's completed measurements."""
        ...


@dataclass(frozen=True, slots=True)
class ProposalContext:
    """Everything a policy is given in place of a candidate list.

    The axes snapshot and constraints are what the run's own space holds; the
    store is the run's own history (R71). Nothing here is a cell, so a policy
    cannot propose a cell the run did not declare — it has to generate one.
    """

    search_space: SearchSpace
    spec: RunSpec
    run_id: str
    budget: Budget
    cost_model: CostModel
    evidence: RecordSource | None = None
    task: str | None = None
    shape: ShapeResolver | None = None
    n_propose: int = 10

    @property
    def _scoped_space(self) -> SearchSpace:
        """The space narrowed to this context's task, when it names one."""
        if self.task is None or self.search_space.tasks == (self.task,):
            return self.search_space
        return replace(self.search_space, tasks=(self.task,))

    def records(self, limit: int = 1000) -> list[Record]:
        """This run's completed measurements. The store is the only history."""
        if self.evidence is None:
            return []
        return self.evidence.query_records(run_id=self.run_id, limit=limit)

    def cells(self, limit: int | None = None) -> Iterator[tuple[Coordinate, Schedule]]:
        """Legal cells from the run's own space, in a deterministic order.

        Args:
            limit: Stop after this many cells; unbounded when ``None``.

        Yields:
            ``(coordinate, schedule)`` pairs the run may execute.
        """
        stream = iter_candidates(
            self.spec,
            self._scoped_space,
            budget=self.budget,
            cost_model=self.cost_model,
            shape=self.shape,
        )
        yield from islice(stream, limit)

    def pool(self) -> list[tuple[Coordinate, Schedule]]:
        """The cells a sampling policy chooses among."""
        return list(self.cells(limit=_POOL))

    def legal(self, coordinate: Coordinate, schedule: Schedule) -> bool:
        """Whether a cell this policy *constructed* is one the run may execute.

        The generator screens the cells it walks, so this exists for the
        policies that build their own — a mutated cell is a cell nobody has
        composed yet, and an uncompposable cell is discovered by training.
        """
        from computronium.experiment.execution.search_space import _composable

        if self.shape is not None and not _composable(
            coordinate, schedule.task_id, self.shape, schedule.param_budget
        ):
            return False
        return bool(_affordable([(coordinate, schedule)], self.budget, self.cost_model))


def _dedupe(
    proposals: Iterator[Proposal] | list[Proposal], limit: int
) -> list[Proposal]:
    """Drop a repeated cell, keeping the first rationale that reached it."""
    seen: set[tuple[str, str, int]] = set()
    unique: list[Proposal] = []
    for proposal in proposals:
        key = (
            proposal.coordinate.cell_key(),
            proposal.schedule.fidelity,
            proposal.schedule.seed,
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(proposal)
        if len(unique) >= limit:
            break
    return unique


@runtime_checkable
class Policy(Protocol):
    """Protocol for allocation policies that generate the cells to execute next."""

    def propose(self, ctx: ProposalContext) -> Iterator[Proposal]:
        """Generate the next cells to evaluate from the run's own space."""
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
        self._rng = random.Random(seed)  # ruff: ignore[suspicious-non-cryptographic-random-usage] - not cryptographic
        self._name = "stratified_random"

    def propose(self, ctx: ProposalContext) -> Iterator[Proposal]:
        """Propose cells by sampling uniformly within each structural stratum."""
        strata: dict[str, list[tuple[Coordinate, Schedule]]] = {}
        for coord, sched in ctx.pool():
            strata.setdefault(
                f"{coord.substrate}|{coord.geometry}|{coord.dynamics}", []
            ).append((coord, sched))

        per_stratum = max(1, ctx.n_propose // max(1, len(strata)))
        proposed = 0
        for cells in strata.values():
            self._rng.shuffle(cells)
            for coord, sched in cells[:per_stratum]:
                if not ctx.legal(coord, sched):
                    continue
                yield Proposal(coord, sched, self._name)
                proposed += 1
                if proposed >= ctx.n_propose:
                    return

    def observe(self, record: Record) -> None:
        """Stratified random doesn't learn from observations."""

    def get_name(self) -> str:
        return self._name


class RoundRobinGridPolicy:
    """Round-robin grid traversal across the 6 axes.

    Systematically enumerates combinations, cycling through axes.
    """

    _AXES: Final = (
        "substrate",
        "geometry",
        "dynamics",
        "plasticity",
        "credit",
        "update",
    )

    def __init__(self, *, seed: int | None = None) -> None:
        self._rng = random.Random(seed)  # ruff: ignore[suspicious-non-cryptographic-random-usage] - not cryptographic
        self._name = "round_robin_grid"
        self._indices: dict[str, int] = {}

    def propose(self, ctx: ProposalContext) -> Iterator[Proposal]:
        """Propose cells in round-robin order over each axis's values."""
        pool = ctx.pool()
        axis_groups: dict[str, dict[str, list[tuple[Coordinate, Schedule]]]] = {
            axis: {} for axis in self._AXES
        }
        for cell in pool:
            coord, sched = cell
            for axis in self._AXES:
                axis_groups[axis].setdefault(getattr(coord, axis), []).append(cell)

        chosen: list[tuple[Coordinate, Schedule]] = []
        for axis in self._AXES:
            values = list(axis_groups[axis])
            if not values:
                continue
            idx = self._indices.get(axis, 0)
            chosen.extend(axis_groups[axis][values[idx % len(values)]])
            self._indices[axis] = (idx + 1) % len(values)

        proposed = 0
        for coord, sched in chosen:
            if not ctx.legal(coord, sched):
                continue
            yield Proposal(coord, sched, self._name)
            proposed += 1
            if proposed >= ctx.n_propose:
                return

    def observe(self, record: Record) -> None:
        """Round-robin grid doesn't learn from observations."""

    def get_name(self) -> str:
        return self._name


class UniformRandomPolicy:
    """Uniform random sampling over the run's active space."""

    def __init__(self, *, seed: int | None = None) -> None:
        self._rng = random.Random(seed)  # ruff: ignore[suspicious-non-cryptographic-random-usage] - not cryptographic
        self._name = "uniform_random"

    def propose(self, ctx: ProposalContext) -> Iterator[Proposal]:
        """Propose cells drawn uniformly from the run's own space."""
        pool = ctx.pool()
        self._rng.shuffle(pool)
        for coord, sched in islice(pool, ctx.n_propose):
            if ctx.legal(coord, sched):
                yield Proposal(coord, sched, self._name)

    def observe(self, record: Record) -> None:
        """Uniform random doesn't learn from observations."""

    def get_name(self) -> str:
        return self._name


class ModelBasedPolicy:
    """Model-based optimization using Optuna.

    The study is *asked* with distributions derived from the harvested active
    space and *told* the objective values the evaluator measured, so TPE and
    NSGA-II can learn. Before, the study was created with no distributions and
    never told anything: `trial.params` was always empty and every proposal
    fell through to indexing a list (TODO46 §D3).

    Trials are the store's records, not a private Optuna database (R71): the
    study is rebuilt from the run's records on first use, so an interrupted run
    resumes with the history it actually measured.
    """

    def __init__(
        self,
        *,
        sampler: str = "tpe",  # "tpe", "nsga2", "gp", "random"
        pruner: str | None = None,  # "median", "hyperband", None
        seed: int | None = None,
        n_startup_trials: int = 10,
        objectives: tuple[str, ...] = ("validation_accuracy",),
        spec: RunSpec | None = None,
    ) -> None:
        """Declare the study.

        Args:
            sampler: Optuna sampler name.
            pruner: Optuna pruner name, or ``None``.
            seed: Sampler seed; the same seed must reproduce a trial sequence.
            n_startup_trials: Random trials before the sampler models.
            objectives: Objective names from ``OBJECTIVES``; each must name a
                measurement.
            spec: The run declaration, so the study samples the spec's own
                narrowed hyperparameter domains and no others. How many cells a
                call asks for is the context's ``n_propose``, not a second knob.

        Raises:
            UnknownObjectiveError: An objective is not registered.
            UnmeasuredObjectiveError: An objective has no measurement behind it.
        """
        self._sampler_name = sampler
        self._pruner_name = pruner
        self._seed = seed
        self._n_startup_trials = n_startup_trials
        self._spec = spec
        self._objectives, self._directions = resolve_objectives(objectives)
        self._name = f"model_based_{sampler}"
        self._study: optuna.Study | None = None
        self._run_id: str | None = None
        self._pending: dict[str, int] = {}

    def _create_sampler(self) -> optuna.samplers.BaseSampler:
        """The declared sampler. An unknown name is a typo, not a silent TPE."""
        match self._sampler_name:
            case "tpe":
                return optuna.samplers.TPESampler(
                    seed=self._seed, n_startup_trials=self._n_startup_trials
                )
            case "nsga2":
                return optuna.samplers.NSGAIISampler(
                    seed=self._seed, population_size=50
                )
            case "gp":
                return optuna.samplers.GPSampler(
                    seed=self._seed, n_startup_trials=self._n_startup_trials
                )
            case "random":
                return optuna.samplers.RandomSampler(seed=self._seed)
            case name:
                msg = f"unknown sampler {name!r}; available: tpe, nsga2, gp, random"
                raise ValueError(msg)

    def _create_pruner(self) -> optuna.pruners.BasePruner | None:
        """The declared pruner, or ``None``."""
        match self._pruner_name:
            case "median":
                return optuna.pruners.MedianPruner(
                    n_startup_trials=self._n_startup_trials,
                    n_warmup_steps=5,
                    interval_steps=1,
                )
            case "hyperband":
                return optuna.pruners.HyperbandPruner(
                    min_resource=1, max_resource=50, reduction_factor=3
                )
            case None:
                return None
            case name:
                msg = f"unknown pruner {name!r}; available: median, hyperband, None"
                raise ValueError(msg)

    def _create_study(self, run_id: str) -> optuna.Study:
        """A study with the declared directions — one or many."""
        directions = [
            StudyDirection.MINIMIZE if d == "minimize" else StudyDirection.MAXIMIZE
            for d in self._directions
        ]
        return optuna.create_study(
            sampler=self._create_sampler(),
            pruner=self._create_pruner(),
            direction=directions[0],
            directions=directions if len(directions) > 1 else None,
            study_name=f"exp_{run_id}",
        )

    def _distributions(self, coordinate: Coordinate) -> dict[str, BaseDistribution]:
        """The samplable dimensions for one coordinate.

        Availability, domain and scale are the harvested ones, narrowed only by
        the spec. Nothing is sampled for a hyperparameter the coordinate's own
        selection cannot use.
        """
        return OptunaDistributionAdapter.distributions(coordinate, spec=self._spec)

    def _rebuild_study_from_records(
        self, run_id: str, records: list[Record]
    ) -> optuna.Study:
        """Rebuild the study from the store's records (R71).

        No private Optuna database: the unified store stays the only store, and a
        resumed run resumes from the measurements it actually made.
        """
        study = self._create_study(run_id)
        for record in records:
            trial = self._record_to_trial_obj(record)
            if trial is not None:
                study.add_trial(trial)
        return study

    def _get_or_rebuild_study(self, run_id: str, records: list[Record]) -> optuna.Study:
        """The study for this run, rebuilt from records the first time."""
        if self._study is None or self._run_id != run_id:
            self._run_id = run_id
            self._study = self._rebuild_study_from_records(run_id, records)
            self._pending.clear()
        return self._study

    def _record_to_trial_obj(self, record: Record) -> optuna.trial.FrozenTrial | None:
        """One record as a completed trial, or ``None``.

        A record whose gate did not pass, or whose payload did not measure
        every objective, is not history the study may fit.
        """
        if record.status.gate_verdict.value != "PASS":
            return None
        values = objective_values(self._objectives, record.payload)
        if values is None:
            return None
        coordinate = Coordinate.from_record(record)
        distributions = self._distributions(coordinate)
        params = {
            name: _sampled_value(value, distributions[name])
            for name, value in coordinate.params.items()
            if name in distributions
        }
        sampled = {name: distributions[name] for name in params}
        try:
            return optuna.trial.create_trial(
                params=params,
                distributions=sampled,
                values=list(values),
                state=optuna.trial.TrialState.COMPLETE,
            )
        except (TypeError, ValueError) as exc:
            logger.warning(
                "record %s is not representable as a trial: %s",
                record.measurement_key[:12],
                exc,
            )
            return None

    def _with_params(self, coord: Coordinate, suggested: dict[str, Any]) -> Coordinate:
        """A coordinate carrying the trial's suggested hyperparameters."""
        if not suggested:
            return coord
        return Coordinate(
            substrate=coord.substrate,
            geometry=coord.geometry,
            dynamics=coord.dynamics,
            plasticity=coord.plasticity,
            credit=coord.credit,
            update=coord.update,
            params={**coord.params, **suggested},
        )

    def propose(self, ctx: ProposalContext) -> Iterator[Proposal]:
        """Ask the study for the next cells' hyperparameters.

        The cells come from the run's own space and each is asked with the
        distributions its own active space declares, so `suggest_*` runs against
        harvested domains narrowed by the spec. A coordinate with no samplable
        dimension is proposed as it stands: that is a fact about the cell, not an
        error.

        Yields:
            The proposed cells, each paired with the trial its measurement will
            be told to.
        """
        study = self._get_or_rebuild_study(ctx.run_id, ctx.records())
        for coord, sched in islice(ctx.cells(), ctx.n_propose):
            distributions = self._distributions(coord)
            if not distributions:
                yield Proposal(coord, sched, self._name)
                continue
            trial = study.ask(distributions)
            proposed = self._with_params(coord, trial.params)
            if not ctx.legal(proposed, sched):
                # A value the harvest refuses for this selection is a cell
                # nobody may train; asking again is cheaper than proposing it.
                study.tell(trial.number, state=optuna.trial.TrialState.FAIL)
                continue
            self._pending[proposed.measurement_key(sched)] = trial.number
            yield Proposal(proposed, sched, self._name)

    def observe(self, record: Record) -> None:
        """Tell the study what the evaluator measured for a proposed cell.

        A record this policy did not propose, or one whose payload measured
        none of its objectives, leaves no value to tell: inventing one is the
        silent maximize §3.4 names.
        """
        study = self._study
        if study is None:
            return
        trial_number = self._pending.pop(record.measurement_key, None)
        if trial_number is None:
            return
        values = (
            objective_values(self._objectives, record.payload)
            if record.status.gate_verdict.value == "PASS"
            else None
        )
        if values is None:
            study.tell(trial_number, state=optuna.trial.TrialState.FAIL)
            return
        study.tell(trial_number, list(values))

    def completed_trials(self) -> int:
        """How many measurements the study has learned from."""
        if self._study is None:
            return 0
        return sum(
            1
            for trial in self._study.trials
            if trial.state is optuna.trial.TrialState.COMPLETE
        )

    def get_name(self) -> str:
        return self._name


class EvolutionPolicy:
    """Evolutionary search over the active space.

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
        objectives: tuple[str, ...] = ("validation_accuracy",),
    ) -> None:
        self._population_size = population_size
        self._mutation_rate = mutation_rate
        self._crossover_rate = crossover_rate
        self._objectives, _ = resolve_objectives(objectives)
        self._rng = random.Random(seed)  # ruff: ignore[suspicious-non-cryptographic-random-usage] - not cryptographic
        self._name = "evolution"
        self._population: list[
            tuple[Coordinate, Schedule, float]
        ] = []  # (coord, sched, fitness)

    def propose(self, ctx: ProposalContext) -> Iterator[Proposal]:
        """Propose children of the fittest cells the run has measured.

        A population that has measured nothing is seeded from the run's own
        space, so an evolution policy needs no candidate list to start either.
        """
        for record in ctx.records():
            self._add_to_population(record)

        proposals = list(self._evolve(ctx))
        if not self._population:
            proposals.extend(
                Proposal(coord, sched, self._name)
                for coord, sched in islice(ctx.pool(), self._population_size)
            )
        return iter(proposals[: ctx.n_propose])

    def observe(self, record: Record) -> None:
        """Add record to population."""
        self._add_to_population(record)

    def _add_to_population(self, record: Record) -> None:
        coord = Coordinate.from_record(record)
        self._population.append((coord, record.schedule, self._extract_score(record)))
        self._population.sort(key=lambda member: member[2], reverse=True)
        self._population = self._population[: self._population_size]

    def _evolve(self, ctx: ProposalContext) -> Iterator[Proposal]:
        """Apply evolutionary operators, keeping only cells the run may execute."""
        if not self._population:
            return

        parents = self._population[: max(2, self._population_size // 4)]
        for parent_coord, parent_sched, _ in parents:
            if self._rng.random() >= self._mutation_rate:
                continue
            child = self._with_params(
                parent_coord, self._mutate_params(parent_coord.params)
            )
            if ctx.legal(child, parent_sched):
                yield Proposal(child, parent_sched, self._name)

        if len(parents) >= 2 and self._rng.random() < self._crossover_rate:
            first, second = self._rng.sample(parents, 2)
            child = self._with_params(
                first[0], self._crossover_params(first[0].params, second[0].params)
            )
            if ctx.legal(child, first[1]):
                yield Proposal(child, first[1], self._name)

    def _with_params(self, coord: Coordinate, params: dict[str, Any]) -> Coordinate:
        """A coordinate carrying evolved hyperparameters."""
        return Coordinate(
            substrate=coord.substrate,
            geometry=coord.geometry,
            dynamics=coord.dynamics,
            plasticity=coord.plasticity,
            credit=coord.credit,
            update=coord.update,
            params={**coord.params, **params},
        )

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
        """A record's measured score, or zero when it measured none."""
        values = objective_values(self._objectives, record.payload)
        return float(values[0]) if values is not None else 0.0

    def get_name(self) -> str:
        return self._name


class SynthesisPolicy:
    """Synthesis policy: combines multiple policies' proposals.

    Runs multiple policies and merges their proposals with deduplication and
    budget awareness.
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

    def propose(self, ctx: ProposalContext) -> Iterator[Proposal]:
        """Propose by combining sub-policy proposals, each weighted."""
        merged: list[Proposal] = []
        for policy, weight in zip(self._policies, self._weights, strict=False):
            weighted = replace(ctx, n_propose=max(1, int(ctx.n_propose * weight)))
            merged.extend(list(islice(policy.propose(weighted), ctx.n_propose)))
        return iter(_dedupe(merged, ctx.n_propose))

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
        stages: list[tuple[Policy, float]],  # (policy, budget_fraction)
        *,
        current_stage: int = 0,
    ) -> None:
        self._stages = stages
        self._current_stage = current_stage
        self._name = "strategy_progression"
        self._budget_consumed: float = 0.0
        self._total_budget: float | None = None

    def propose(self, ctx: ProposalContext) -> Iterator[Proposal]:
        """Propose using the current stage's policy."""
        if not self._stages:
            return iter(())

        if self._total_budget is None and ctx.budget.target_cost:
            self._total_budget = ctx.budget.target_cost

        if self._total_budget and ctx.budget.cost_consumed > 0:
            progress = ctx.budget.cost_consumed / self._total_budget
            self._current_stage = min(
                int(progress * len(self._stages)), len(self._stages) - 1
            )

        policy, _ = self._stages[self._current_stage]
        return policy.propose(ctx)

    def observe(self, record: Record) -> None:
        """Forward observation to current stage's policy."""
        if self._stages:
            policy, _ = self._stages[self._current_stage]
            policy.observe(record)

    def get_name(self) -> str:
        return f"{self._name}_stage{self._current_stage}"


class TrainerDrivenPolicy:
    """Trainer-driven policy: proposals come from an external trainer.

    The trainer proposes cells from the same space this run declared; a trainer
    that fails or stays silent hands the context to the fallback, which is how
    a learned policy that has nothing to say does not end the run.
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

    def propose(self, ctx: ProposalContext) -> Iterator[Proposal]:
        """Propose using the trainer, or the fallback when it has nothing."""
        if self._trainer is not None and hasattr(self._trainer, "propose"):
            try:
                proposals = list(self._trainer.propose(ctx))
                if proposals:
                    return iter(proposals)
            except Exception as e:
                logger.warning("Trainer propose failed, using fallback: %s", e)

        return self._fallback.propose(ctx)

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
    """Create a policy by name.

    Args:
        name: A key of :data:`POLICY_CATALOG`.
        **kwargs: Constructor arguments for that policy.

    Returns:
        The policy instance.

    Raises:
        ValueError: The name is unknown, or the policy does not accept one of
            the arguments. A silently dropped argument is dead config, and a
            run that believes it declared a search dimension has not.
    """
    if name not in POLICY_CATALOG:
        msg = f"unknown policy {name!r}; available: {sorted(POLICY_CATALOG)}"
        raise ValueError(msg)
    policy_cls = POLICY_CATALOG[name]
    accepted = _accepted_kwargs(policy_cls)
    unsupported = sorted(set(kwargs) - accepted)
    if unsupported:
        msg = (
            f"policy {name!r} does not accept {unsupported}; "
            f"it accepts {sorted(accepted)}"
        )
        raise ValueError(msg)
    return policy_cls(**kwargs)


def policy_context(spec: RunSpec, name: str) -> dict[str, Any]:
    """The run arguments one policy is offered.

    A signature is not evidence of which knobs a primitive reads (TODO46 §D13),
    but it is evidence of which keyword names a call may carry, so it is
    harvested here rather than re-declared per policy. A policy that declares
    none of these is not a learner; that is a fact about it, not an error.

    Args:
        spec: The run declaration.
        name: The chosen policy's catalog key.

    Returns:
        The subset of ``seed``, ``objectives`` and ``spec`` that this policy
        accepts. Objectives are a tuple, defaulting to the measured primary
        when a spec names none.

    Raises:
        ValueError: The policy name is unknown.
    """
    if name not in POLICY_CATALOG:
        msg = f"unknown policy {name!r}; available: {sorted(POLICY_CATALOG)}"
        raise ValueError(msg)
    accepted = _accepted_kwargs(POLICY_CATALOG[name])
    context = {
        "seed": spec.seed,
        "objectives": spec.objectives or ("validation_accuracy",),
        "spec": spec,
    }
    return {key: value for key, value in context.items() if key in accepted}


def _accepted_kwargs(policy_cls: type[Policy]) -> set[str]:
    """The keyword names one policy's constructor may carry."""
    return set(inspect.signature(policy_cls).parameters) - {"self"}


__all__ = [
    "POLICY_CATALOG",
    "EvolutionPolicy",
    "ModelBasedPolicy",
    "Policy",
    "ProposalContext",
    "RecordSource",
    "RoundRobinGridPolicy",
    "StrategyProgressionPolicy",
    "StratifiedRandomPolicy",
    "SynthesisPolicy",
    "TrainerDrivenPolicy",
    "UniformRandomPolicy",
    "create_policy",
    "policy_context",
    "resolve_objectives",
]
