"""Evolutionary Lab surface (TODO24 Phase 2): budgeted mechanism search.

``plan_evolution`` dry-runs (no training); ``run_evolution`` executes
generations of surrogate screen → constitutional filter → §22-selected
campaign evaluation → Pareto selection → mutation. Every generation and
every campaign-evaluated candidate pre-registers as a ceec ``Experiment``;
candidate selection runs the CEEC §22 loop scoped to the generation's
experiments so concurrent runs in a shared ledger cannot hijack selection.
"""

from __future__ import annotations

import json
import random
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, cast

from computronium_lab.research.autopoiesis import (
    CampaignFitness,
    CandidateEvaluation,
    CoordinateGenome,
    ParetoSelection,
    ResearchConstitution,
    ResearchStagnationDetector,
    SafeMutationOperator,
    SurrogateFitness,
    hypervolume,
    nondominated_sort,
    objective_names,
)
from computronium_lab.research.paths import corpus_root
from computronium_lab.research.schema import BUDGET_CAPS, BudgetTier

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from ceec.models import Decision, Scope
    from ceec.store import CEECStore

    from computronium_lab.lab import Lab
    from computronium_lab.synthesis.spec import ProblemSpec

__all__ = [
    "EvolutionBudget",
    "EvolutionPlan",
    "EvolutionReport",
    "EvolutionSpec",
    "FrontierArchive",
    "FrontierPoint",
    "GenerationSummary",
    "plan_evolution",
    "run_evolution",
]

_CERTIFIED_EPOCHS: dict[str, int] = {
    "flat_classification": 20,
    "sequence_last_symbol": 120,
    "sequence_threshold": 120,
    "sequence_parity": 120,
    "nca_state_prediction": 100,
}

_CEEC_BUDGET: dict[str, str] = {
    BudgetTier.SMOKE: "quick",
    BudgetTier.QUICK: "standard",
    BudgetTier.CERTIFIED: "nightly",
}

_SIZE_MAX = 4.0


@dataclass(frozen=True, slots=True)
class EvolutionBudget:
    """Hard caps for one evolution run (TODO24 §10)."""

    max_campaigns: int = 8
    max_epochs_per_campaign: int | None = 20
    max_seeds: int = 3

    @classmethod
    def smoke(cls) -> EvolutionBudget:
        cap = BUDGET_CAPS[BudgetTier.SMOKE]
        return cls(cap.max_campaigns, cap.max_epochs_per_campaign, cap.max_seeds)

    @classmethod
    def quick(cls) -> EvolutionBudget:
        cap = BUDGET_CAPS[BudgetTier.QUICK]
        return cls(cap.max_campaigns, cap.max_epochs_per_campaign, cap.max_seeds)

    @classmethod
    def certified(cls) -> EvolutionBudget:
        cap = BUDGET_CAPS[BudgetTier.CERTIFIED]
        return cls(cap.max_campaigns, cap.max_epochs_per_campaign, cap.max_seeds)


@dataclass(frozen=True, slots=True)
class EvolutionSpec:
    """Population, generations, objectives, budgets, seed candidates."""

    population: int = 6
    generations: int = 3
    seed_candidates: tuple[str, ...] = ("backprop_mlp",)
    objectives: tuple[str, ...] = ("accuracy", "adaptation_speed", "stability")
    budget: EvolutionBudget = field(default_factory=EvolutionBudget.quick)
    tier: BudgetTier = BudgetTier.QUICK
    seed: int = 0
    stagnation_patience: int = 2
    run_id: str | None = None
    start_generation: int = 0


@dataclass(frozen=True, slots=True)
class EvolutionPlan:
    """Dry-run plan: candidate genomes, checks, expected budgets."""

    spec: ProblemSpec
    evolution: EvolutionSpec
    genomes: tuple[CoordinateGenome, ...]
    admission: tuple[tuple[str, bool, str], ...]
    expected_campaigns: int
    expected_epochs: int
    run_id: str


@dataclass(frozen=True, slots=True)
class FrontierPoint:
    """One measured Pareto point (campaign evidence, never speculation)."""

    spec_key: str
    genome_digest: str
    mechanism: str
    objectives: dict[str, float]
    seeds: tuple[int, ...]
    tier: str
    run_id: str
    timestamp: str

    def to_dict(self) -> dict[str, object]:
        return {
            "spec_key": self.spec_key,
            "genome_digest": self.genome_digest,
            "mechanism": self.mechanism,
            "objectives": dict(self.objectives),
            "seeds": list(self.seeds),
            "tier": self.tier,
            "run_id": self.run_id,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, object]) -> FrontierPoint:
        return cls(
            spec_key=str(raw["spec_key"]),
            genome_digest=str(raw["genome_digest"]),
            mechanism=str(raw["mechanism"]),
            objectives=dict(cast("dict[str, float]", raw["objectives"])),
            seeds=tuple(cast("list[int]", raw["seeds"])),
            tier=str(raw["tier"]),
            run_id=str(raw["run_id"]),
            timestamp=str(raw["timestamp"]),
        )


def _archive_path(spec: ProblemSpec) -> Path:
    safe = "".join(c if c.isalnum() or c in {"-", "_"} else "_" for c in spec.key())
    return corpus_root() / "frontier" / f"{safe}.json"


def _reference_point() -> dict[str, float]:
    from computronium_lab.synthesis.catalog import CATALOG

    latency = max(c.pareto.latency_ms for c in CATALOG) * _SIZE_MAX
    memory = max(c.pareto.memory_gb for c in CATALOG) * _SIZE_MAX
    return {
        "accuracy": 0.0,
        "adaptation_speed": 0.0,
        "stability": 0.0,
        "latency": latency,
        "memory": memory,
    }


class FrontierArchive:
    """Persistent Pareto frontiers reusable by synthesis (T24.2.5)."""

    def __init__(self, spec: ProblemSpec) -> None:
        self.spec = spec
        self.path = _archive_path(spec)
        self.points: list[FrontierPoint] = []
        if self.path.exists():
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            self.points = [FrontierPoint.from_dict(p) for p in raw.get("points", [])]

    def add(
        self,
        evaluations: Sequence[CandidateEvaluation],
        *,
        tier: str,
        run_id: str,
    ) -> None:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        known = {p.genome_digest for p in self.points}
        for evaluation in evaluations:
            if evaluation.genome_digest in known:
                continue
            known.add(evaluation.genome_digest)
            self.points.append(
                FrontierPoint(
                    spec_key=self.spec.key(),
                    genome_digest=evaluation.genome_digest,
                    mechanism=evaluation.mechanism,
                    objectives=dict(evaluation.objectives),
                    seeds=evaluation.seeds,
                    tier=tier,
                    run_id=run_id,
                    timestamp=stamp,
                )
            )
        self._persist()

    def _persist(self) -> None:
        from computronium_lab.synthesis.engine import OBJECTIVE_FIELDS

        objectives = [(name, OBJECTIVE_FIELDS[name][1]) for name in objective_names()]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(
                {
                    "spec_key": self.spec.key(),
                    "hypervolume": self.hypervolume(objectives),
                    "points": [p.to_dict() for p in self.points],
                },
                sort_keys=True,
                indent=2,
            ),
            encoding="utf-8",
        )

    def pareto(self, objectives: Sequence[tuple[str, bool]]) -> list[FrontierPoint]:
        vectors = [p.objectives for p in self.points]
        if not vectors:
            return []
        fronts = nondominated_sort(vectors, objectives)
        return [self.points[i] for i in fronts[0]]

    def hypervolume(self, objectives: Sequence[tuple[str, bool]]) -> float:
        reference = _reference_point()
        vectors = [
            {name: p.objectives[name] for name, _ in objectives}
            for p in self.points
            if all(name in p.objectives for name, _ in objectives)
        ]
        return hypervolume(
            vectors,
            objectives,
            {name: reference[name] for name, _ in objectives},
        )

    def measured_accuracy(self) -> dict[str, float]:
        """Best measured accuracy per mechanism (synthesis integration)."""
        best: dict[str, float] = {}
        for point in self.points:
            accuracy = point.objectives.get("accuracy", 0.0)
            if accuracy > best.get(point.mechanism, 0.0):
                best[point.mechanism] = accuracy
        return best


def _objectives(evolution: EvolutionSpec) -> list[tuple[str, bool]]:
    from computronium_lab.synthesis.engine import OBJECTIVE_FIELDS

    fields = []
    for name in evolution.objectives:
        if name not in OBJECTIVE_FIELDS:
            raise ValueError(f"unknown objective {name!r}")
        _, maximize = OBJECTIVE_FIELDS[name]
        fields.append((name, maximize))
    return fields


def plan_evolution(spec: ProblemSpec, evolution: EvolutionSpec) -> EvolutionPlan:
    """Dry-run planner: genomes, constitutional checks, budgets. No training."""
    from computronium_lab.synthesis.catalog import CATALOG

    run_id = evolution.run_id or datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    known = {c.name for c in CATALOG}
    for name in evolution.seed_candidates:
        if name not in known:
            raise ValueError(f"seed candidate {name!r} is not cataloged")
    constitution = ResearchConstitution(spec, BUDGET_CAPS[evolution.tier])
    genomes: list[CoordinateGenome] = []
    admission: list[tuple[str, bool, str]] = []
    for name in evolution.seed_candidates:
        genome = CoordinateGenome.seed(name, spec)
        admitted, reason = constitution.evaluate(genome.genome())
        admission.append((name, admitted, reason))
        if admitted:
            genomes.append(genome)
    if not genomes:
        raise ValueError("no seed candidate admitted by the constitution")
    campaigns_per_generation = min(evolution.population, evolution.budget.max_campaigns)
    expected_campaigns = campaigns_per_generation * evolution.generations
    epochs_each = evolution.budget.max_epochs_per_campaign or _CERTIFIED_EPOCHS.get(
        spec.task, 20
    )
    return EvolutionPlan(
        spec=spec,
        evolution=evolution,
        genomes=tuple(genomes),
        admission=tuple(admission),
        expected_campaigns=expected_campaigns,
        expected_epochs=expected_campaigns * epochs_each,
        run_id=run_id,
    )


@dataclass(frozen=True, slots=True)
class GenerationSummary:
    """One executed generation (JSON-serializable)."""

    generation: int
    evaluated: tuple[dict[str, object], ...]
    survivors: tuple[str, ...]
    hypervolume: float
    grew: bool
    campaigns_used: int
    experiment_id: str | None = None
    decision_id: str | None = None


@dataclass(frozen=True, slots=True)
class EvolutionReport:
    """Best candidates, frontier, lineage, negatives, ledger references."""

    spec_key: str
    run_id: str
    tier: str
    initial_population: tuple[dict[str, object], ...]
    generation_summaries: tuple[GenerationSummary, ...]
    best_candidates: tuple[CandidateEvaluation, ...]
    frontier_points: tuple[FrontierPoint, ...]
    lineage: dict[str, tuple[str, ...]]
    negative_results: tuple[dict[str, object], ...]
    cookbook_entries: tuple[dict[str, object], ...]
    ledger: dict[str, object]
    calibration: tuple[dict[str, object], ...]

    def to_dict(self) -> dict[str, object]:
        import dataclasses

        return {
            "spec_key": self.spec_key,
            "run_id": self.run_id,
            "tier": self.tier,
            "initial_population": list(self.initial_population),
            "generation_summaries": [
                dataclasses.asdict(summary) for summary in self.generation_summaries
            ],
            "best_candidates": [
                dataclasses.asdict(candidate) for candidate in self.best_candidates
            ],
            "frontier_points": [p.to_dict() for p in self.frontier_points],
            "lineage": {k: list(v) for k, v in self.lineage.items()},
            "negative_results": list(self.negative_results),
            "cookbook_entries": list(self.cookbook_entries),
            "ledger": dict(self.ledger),
            "calibration": list(self.calibration),
        }


def _scope_for(spec: ProblemSpec, tier: BudgetTier, run_id: str) -> Scope:
    from ceec.models import Scope

    return Scope(
        domain="research",
        substrate=(spec.constraints.substrate,),
        budget=tier.value,
        extra={"run_id": run_id, "spec_key": spec.key()},
    )


def _open_store(lab: Lab) -> CEECStore | None:
    from computronium_lab.research.adapters import LabRecorder

    return LabRecorder(lab).store()


def _pre_register(
    store: CEECStore,
    *,
    experiment_id: str,
    question: str,
    prediction: str,
    point: float,
    design: dict[str, object],
    scope: Scope,
    tier: BudgetTier,
) -> str:
    from ceec.models import Experiment, Probability
    from ceec.store import now

    clamped = min(0.99, max(0.01, point))
    experiment = Experiment(
        id=experiment_id,
        question=question,
        rationale=f"evolution generation measurement at tier {tier.value}",
        scope=scope,
        target_beliefs=[],
        target_goals=[],
        design=design,
        prediction=prediction,
        prediction_probability=Probability(
            low=round(max(0.0, clamped - 0.2), 3),
            high=round(min(1.0, clamped + 0.2), 3),
            point=round(clamped, 3),
            method="surrogate_screen",
        ),
        controls=["seed_catalog_baseline"],
        metrics=["accuracy"],
        budget=_CEEC_BUDGET[tier],  # type: ignore[typeddict-item]
        falsification_criterion=(
            "seed catalog baseline matches or beats the evolved candidate"
        ),
        overturn_criterion="a seed-paired permutation test finds no advantage",
        hard_gates=["BenchmarkReproduction", "StabilityCertificate"],
        created_at=now(),
    )
    store.pre_register_experiment(experiment)
    store.set_experiment_status(experiment_id, "running")
    return experiment_id


def _coordinate_validator(candidate: object) -> None:
    from computronium_lab.synthesis.catalog import CATALOG

    if not isinstance(candidate, dict):
        raise TypeError("coordinate must be a genome payload mapping")
    names = {c.name for c in CATALOG}
    if str(candidate.get("mechanism", "")) not in names:
        raise ValueError("genome points outside the catalog")


def _scoped_decision(
    store: CEECStore,
    experiment_ids: Sequence[str],
    *,
    rationale: str,
    focus_id: str,
) -> Decision:
    """§22 loop scoped to one generation's experiments (ceec ``decide``).

    ``candidate_ids`` restricts the pool to this generation so unrelated
    pre-registered experiments in a shared ledger cannot hijack selection;
    the override records the surrogate-ranked measurement focus
    transparently.
    """
    from ceec.selection import decide
    from ceec.store import StoreError

    eligible_override = (
        [
            {
                "rationale": (
                    "surrogate-ranked measurement focus within the "
                    "eligible set; hard constraints already enforced"
                ),
                "select_experiment": focus_id,
            }
        ]
        if experiment_ids
        else []
    )
    try:
        return decide(
            store,
            {},
            rationale,
            coordinate_validator=_coordinate_validator,
            overrides=eligible_override,
            candidate_ids=experiment_ids,
        )
    except StoreError:
        # Focus candidate failed hard constraints: fall back to the §22
        # default (highest expected-value-per-cost among eligible).
        return decide(
            store,
            {},
            rationale,
            coordinate_validator=_coordinate_validator,
            candidate_ids=experiment_ids,
        )


def _record_candidate(
    store: CEECStore,
    scope: Scope,
    evaluation: CandidateEvaluation,
    genome: CoordinateGenome,
    *,
    tier: str,
    run_id: str,
    epochs: int,
) -> dict[str, str]:
    from computronium_lab.research.evidence import vector_evidence
    from computronium_lab.research.schema import StatisticalSummary

    candidate_artifact = store.ingest_artifact(
        json.dumps(genome.genome(), sort_keys=True, default=str).encode(),
        "evolution_candidate",
        {
            "mechanism": evaluation.mechanism,
            "genome_digest": evaluation.genome_digest,
            "run_id": run_id,
        },
    )
    evidence_id = vector_evidence(
        store,
        scope,
        axes=["seed"],
        values=list(evaluation.per_seed_accuracy),
        values_ref=f"evolution/{run_id}/{evaluation.genome_digest}",
        quality={
            "seeds": len(evaluation.seeds),
            "matched_control": False,
            "evaluation_policy": "seed_mean_campaign_v1",
            "reproduction": evaluation.reproduction,
            "tier": tier,
        },
        notes=f"candidate {evaluation.mechanism} ({evaluation.genome_digest})",
    )
    summary = StatisticalSummary.from_samples(
        "accuracy", list(evaluation.per_seed_accuracy)
    )
    derived = store.record_derived(
        type_="seed_statistics",
        operator="bootstrap_ci_percentile",
        inputs={"e": [evidence_id]},
        scope=scope,
        value={
            "mean": summary.mean,
            "std": summary.std,
            "ci_low": summary.ci_low,
            "ci_high": summary.ci_high,
            "n": summary.n,
        },
    )
    resource = store.record_derived(
        type_="resource_rollup",
        operator="evolution_generation_rollup",
        inputs={"e": [evidence_id]},
        scope=scope,
        value={
            "compute_epochs": epochs * len(evaluation.seeds),
            "memory_gb_est": evaluation.objectives.get("memory", 0.0),
            "latency_ms_est": evaluation.objectives.get("latency", 0.0),
            "energy_j": None,
            "note": "energy estimated at transfer tier only (Phase 5)",
        },
    )
    return {
        "artifact": candidate_artifact.id,
        "evidence": evidence_id,
        "derived": derived.id,
        "resource": resource.id,
    }


def _ref_list(refs: dict[str, object], key: str) -> list[str]:
    """Ledger reference list (experiments/decisions/artifacts)."""
    items = refs.get(key, [])
    if not isinstance(items, list):
        raise TypeError(f"ledger refs must list {key!r}")
    return cast("list[str]", items)


def _constraints_of(node: Mapping[str, object]) -> Mapping[str, object]:
    """Nested spec/constraints mapping of a genome payload ({} if absent)."""
    spec = node.get("spec", {})
    if not isinstance(spec, Mapping):
        return {}
    constraints = spec.get("constraints", {})
    return constraints if isinstance(constraints, Mapping) else {}


def _config_diff(
    parent: Mapping[str, object], child: Mapping[str, object]
) -> dict[str, list[object]]:
    diff: dict[str, list[object]] = {}
    for key in (
        "mechanism",
        "size_scale",
        "precision",
        "quantization",
        "substrate_override",
    ):
        if parent.get(key) != child.get(key):
            diff[key] = [parent.get(key), child.get(key)]
    parent_constraints = _constraints_of(parent)
    child_constraints = _constraints_of(child)
    for key, old in parent_constraints.items():
        if child_constraints.get(key) != old:
            diff[f"spec.constraints.{key}"] = [old, child_constraints.get(key)]
    return diff


@dataclass
class _RunState:
    """Mutable generation-loop state (keeps each step small)."""

    lab: Lab
    plan: EvolutionPlan
    store: CEECStore | None
    scope: Scope | None
    archive: FrontierArchive
    rng: random.Random
    objectives: list[tuple[str, bool]]
    surrogate: SurrogateFitness
    fitness: CampaignFitness
    selection: ParetoSelection
    mutator: SafeMutationOperator
    constitution: ResearchConstitution
    stagnation: ResearchStagnationDetector
    population: list[CoordinateGenome]
    evaluated: dict[str, CandidateEvaluation]
    genome_by_digest: dict[str, CoordinateGenome]
    lineage: dict[str, tuple[str, ...]]
    negatives: list[dict[str, object]]
    summaries: list[GenerationSummary]
    ledger_refs: dict[str, object]
    calibrations: list[dict[str, object]]
    campaigns_used: int = 0
    previous_hypervolume: float = 0.0
    scalar_stagnant: bool = False
    hv_stagnant: bool = False

    @property
    def evolution(self) -> EvolutionSpec:
        return self.plan.evolution

    @property
    def spec(self) -> ProblemSpec:
        return self.plan.spec

    def epochs(self) -> int:
        budget = self.evolution.budget
        return budget.max_epochs_per_campaign or _CERTIFIED_EPOCHS.get(
            self.spec.task, 20
        )

    def seeds(self) -> tuple[int, ...]:
        return tuple(range(self.evolution.budget.max_seeds))


def run_evolution(lab: Lab, plan: EvolutionPlan) -> EvolutionReport:
    """Execute generations; fork fresh systems; record audited artifacts."""
    evolution = plan.evolution
    archive = FrontierArchive(plan.spec)
    state = _RunState(
        lab=lab,
        plan=plan,
        store=_open_store(lab),
        scope=(
            _scope_for(plan.spec, evolution.tier, plan.run_id)
            if lab.record_ledger
            else None
        ),
        archive=archive,
        rng=random.Random(evolution.seed),  # ruff: ignore[suspicious-non-cryptographic-random-usage] - seeded deterministic evolution
        objectives=_objectives(evolution),
        surrogate=SurrogateFitness(plan.spec),
        fitness=CampaignFitness(plan.spec),
        selection=ParetoSelection(),
        mutator=SafeMutationOperator(),
        constitution=ResearchConstitution(plan.spec, BUDGET_CAPS[evolution.tier]),
        stagnation=ResearchStagnationDetector(patience=evolution.stagnation_patience),
        population=list(plan.genomes),
        evaluated={},
        genome_by_digest={g.digest: g for g in plan.genomes},
        lineage={g.digest: tuple(g.lineage) for g in plan.genomes},
        negatives=[],
        summaries=[],
        ledger_refs={
            "ledger": lab.record_ledger,
            "experiments": [],
            "decisions": [],
            "artifacts": [],
        },
        calibrations=[],
        previous_hypervolume=archive.hypervolume(_objectives(evolution)),
    )
    try:
        for generation in range(evolution.start_generation, evolution.generations):
            if not _run_generation(state, generation):
                break
        return _finalize(state)
    finally:
        if state.store is not None:
            state.store._conn.commit()
            state.store.close()


def _run_generation(state: _RunState, generation: int) -> bool:
    """Execute one generation; False stops the loop."""
    contenders = _contenders(state, generation)
    if not contenders:
        return False
    experiment_id, decision_id = _pre_register_generation(state, generation, contenders)
    round_evaluations = _evaluate_round(state, contenders)
    grew = _close_round(state, generation, round_evaluations, experiment_id)
    survivors = _select_survivors(state, round_evaluations)
    _breed(state, generation, survivors, contenders)
    _summarize(
        state,
        generation,
        round_evaluations,
        survivors,
        grew,
        experiment_id,
        decision_id,
    )
    _record_outcome(state, generation, experiment_id, grew)
    return _should_continue(state, generation)


def _contenders(state: _RunState, generation: int) -> list[CoordinateGenome]:
    ranked = sorted(state.population, key=state.surrogate.screen, reverse=True)
    slots = min(
        len(ranked), state.evolution.budget.max_campaigns - state.campaigns_used
    )
    if slots <= 0:
        state.negatives.append({
            "kind": "budget_exhausted",
            "generation": generation,
            "detail": (
                f"{state.campaigns_used}/"
                f"{state.evolution.budget.max_campaigns} campaigns used"
            ),
        })
        return []
    return ranked[:slots]


def _pre_register_generation(
    state: _RunState, generation: int, contenders: list[CoordinateGenome]
) -> tuple[str | None, str | None]:
    if state.store is None or state.scope is None:
        return None, None
    run_id = state.plan.run_id
    experiment_id = f"X-EVOL-{run_id}-{generation:02d}".replace(":", "")
    seeds = state.seeds()
    _pre_register(
        state.store,
        experiment_id=experiment_id,
        question=(
            f"can generation {generation} of evolution over "
            f"{state.spec.task}/{state.spec.dataset} extend the measured frontier?"
        ),
        prediction=f"surrogate-top {contenders[0].mechanism} extends the frontier",
        point=state.surrogate.screen(contenders[0]),
        design={
            "seeds": list(seeds),
            "seed_plan": list(seeds),
            "epochs": state.epochs(),
            "equal_compute": True,
            "controls": ["seed_catalog_baseline"],
            "evaluation_policy": "seed_mean_campaign_v1",
            "evidence_kind": "vector",
            "run_id": run_id,
            "generation": generation,
        },
        scope=state.scope,
        tier=state.evolution.tier,
    )
    _ref_list(state.ledger_refs, "experiments").append(experiment_id)
    candidate_experiments = [
        _pre_register_candidate(state, generation, contender)
        for contender in contenders
    ]
    decision = _scoped_decision(
        state.store,
        candidate_experiments,
        rationale=(
            f"generation {generation}: eligible candidates measured "
            "within budget; focus is the surrogate-top eligible genome"
        ),
        focus_id=candidate_experiments[0],
    )
    _ref_list(state.ledger_refs, "decisions").append(decision.id)
    return experiment_id, decision.id


def _pre_register_candidate(
    state: _RunState, generation: int, contender: CoordinateGenome
) -> str:
    if state.store is None or state.scope is None:
        raise TypeError("candidate pre-registration requires an open ledger")
    run_id = state.plan.run_id
    candidate_id = f"X-EVOL-{run_id}-{generation:02d}-{contender.digest[:8]}".replace(
        ":", ""
    )
    seeds = state.seeds()
    _pre_register(
        state.store,
        experiment_id=candidate_id,
        question=f"does {contender.mechanism} certify on {state.spec.key()}?",
        prediction=f"{contender.mechanism} reproduces its catalog Pareto",
        point=state.surrogate.screen(contender),
        design={
            "coordinate": contender.genome(),
            "genome_digest": contender.digest,
            "seeds": list(seeds),
            "seed_plan": list(seeds),
            "epochs": state.epochs(),
            "equal_compute": True,
            "controls": ["seed_catalog_baseline"],
            "evaluation_policy": "seed_mean_campaign_v1",
            "evidence_kind": "vector",
        },
        scope=state.scope,
        tier=state.evolution.tier,
    )
    return candidate_id


def _evaluate_round(
    state: _RunState, contenders: list[CoordinateGenome]
) -> list[CandidateEvaluation]:
    from computronium_lab.research.autopoiesis import NotTrainableError

    round_evaluations = []
    for genome in contenders:
        try:
            evaluation = state.fitness.evaluate(
                genome, state.lab, seeds=state.seeds(), epochs=state.epochs()
            )
        except NotTrainableError as exc:
            state.negatives.append({
                "kind": "not_trainable",
                "mechanism": genome.mechanism,
                "digest": genome.digest,
                "detail": str(exc),
            })
            continue
        state.evaluated[genome.digest] = evaluation
        round_evaluations.append(evaluation)
        state.campaigns_used += 1
        if state.store is not None and state.scope is not None:
            refs = _record_candidate(
                state.store,
                state.scope,
                evaluation,
                genome,
                tier=state.evolution.tier.value,
                run_id=state.plan.run_id,
                epochs=state.epochs(),
            )
            _ref_list(state.ledger_refs, "artifacts").append(refs["artifact"])
    return round_evaluations


def _close_round(
    state: _RunState,
    generation: int,
    round_evaluations: list[CandidateEvaluation],
    experiment_id: str | None,
) -> bool:
    for evaluation in round_evaluations:
        if not evaluation.reproduction:
            state.negatives.append({
                "kind": "reproduction_miss",
                "generation": generation,
                "mechanism": evaluation.mechanism,
                "digest": evaluation.genome_digest,
                "detail": (
                    f"mean {evaluation.objectives['accuracy']:.3f} "
                    "below catalog Pareto tolerance"
                ),
            })
        if evaluation.stability is False:
            state.negatives.append({
                "kind": "stability_kill",
                "generation": generation,
                "mechanism": evaluation.mechanism,
                "digest": evaluation.genome_digest,
                "detail": "stability guard killed or failed",
            })
    state.archive.add(
        round_evaluations,
        tier=state.evolution.tier.value,
        run_id=state.plan.run_id,
    )
    current = state.archive.hypervolume(state.objectives)
    grew = current > state.previous_hypervolume + 1e-12
    scalar_best = max(e.objectives["accuracy"] for e in state.evaluated.values())
    state.scalar_stagnant = state.stagnation.update(scalar_best)
    state.hv_stagnant = state.stagnation.update_hypervolume(current)
    if not grew:
        state.negatives.append({
            "kind": "no_frontier_growth",
            "generation": generation,
            "detail": f"hypervolume {current:.6f} unchanged",
        })
    state.previous_hypervolume = current
    return grew


def _select_survivors(
    state: _RunState, round_evaluations: list[CandidateEvaluation]
) -> list[CoordinateGenome]:
    pairs = [
        (state.genome_by_digest[e.genome_digest], e.objectives)
        for e in round_evaluations
    ]
    return state.selection.select_pareto(
        pairs, state.objectives, state.evolution.population
    )


def _breed(
    state: _RunState,
    generation: int,
    survivors: list[CoordinateGenome],
    contenders: list[CoordinateGenome],
) -> None:
    state.population = list(survivors)
    target = state.evolution.population
    attempts = 0
    while len(state.population) < target and attempts < 10 * target:
        attempts += 1
        pool = survivors or contenders
        parent = state.rng.choice(pool)
        child_payload = state.mutator.mutate(parent.genome(), state.rng)
        admitted, reason = state.constitution.evaluate(child_payload)
        if not admitted:
            state.negatives.append({
                "kind": "constitution_rejection",
                "generation": generation,
                "detail": reason,
                "diff": _config_diff(parent.genome(), child_payload),
            })
            continue
        child = CoordinateGenome.from_payload(child_payload)
        child.lineage = (*parent.lineage, parent.digest)
        if child.digest in state.genome_by_digest:
            continue
        state.genome_by_digest[child.digest] = child
        state.lineage[child.digest] = tuple(child.lineage)
        state.population.append(child)


def _summarize(
    state: _RunState,
    generation: int,
    round_evaluations: list[CandidateEvaluation],
    survivors: list[CoordinateGenome],
    grew: bool,
    experiment_id: str | None,
    decision_id: str | None,
) -> None:
    state.summaries.append(
        GenerationSummary(
            generation=generation,
            evaluated=tuple(
                {
                    "mechanism": e.mechanism,
                    "digest": e.genome_digest,
                    "objectives": dict(e.objectives),
                    "reproduction": e.reproduction,
                    "stability": e.stability,
                    "certified": e.certified,
                }
                for e in round_evaluations
            ),
            survivors=tuple(g.digest for g in survivors),
            hypervolume=state.previous_hypervolume,
            grew=grew,
            campaigns_used=state.campaigns_used,
            experiment_id=experiment_id,
            decision_id=decision_id,
        )
    )


def _record_outcome(
    state: _RunState, generation: int, experiment_id: str | None, grew: bool
) -> None:
    if state.store is None or experiment_id is None:
        return
    from ceec.calibration import record_experiment_outcome

    state.store.set_experiment_status(experiment_id, "completed")
    record = record_experiment_outcome(
        state.store,
        experiment_id,
        outcome="frontier_grew" if grew else "no_growth",
        outcome_boolean=grew,
        notes=(f"generation {generation} hypervolume {state.previous_hypervolume:.6f}"),
    )
    if record is not None:
        state.calibrations.append({
            "experiment_id": experiment_id,
            "outcome": "frontier_grew" if grew else "no_growth",
            "brier_score": record.brier_score,
            "log_score": record.log_score,
        })


def _should_continue(state: _RunState, generation: int) -> bool:
    if (state.scalar_stagnant or state.hv_stagnant) and (
        generation + 1 < state.evolution.generations
    ):
        state.negatives.append({
            "kind": "stagnation_stop",
            "generation": generation,
            "detail": "no scalar or hypervolume improvement within patience",
        })
        return False
    return not state.stagnation.exhausted(
        state.campaigns_used, state.evolution.budget.max_campaigns
    )


def _finalize(state: _RunState) -> EvolutionReport:
    all_vectors = [(e, e.objectives) for e in state.evaluated.values()]
    best: list[CandidateEvaluation] = []
    if all_vectors:
        fronts = nondominated_sort([v for _, v in all_vectors], state.objectives)
        best = [all_vectors[i][0] for i in fronts[0][:3]]
    if state.store is not None and state.scope is not None:
        generation_artifact = state.store.ingest_artifact(
            json.dumps(
                {
                    "run_id": state.plan.run_id,
                    "spec_key": state.spec.key(),
                    "generations": len(state.summaries),
                    "campaigns_used": state.campaigns_used,
                    "hypervolume": state.previous_hypervolume,
                },
                sort_keys=True,
            ).encode(),
            "evolution_generation",
            {"run_id": state.plan.run_id, "spec_key": state.spec.key()},
        )
        _ref_list(state.ledger_refs, "artifacts").append(generation_artifact.id)
    return EvolutionReport(
        spec_key=state.spec.key(),
        run_id=state.plan.run_id,
        tier=state.evolution.tier.value,
        initial_population=tuple(g.genome() for g in state.plan.genomes),
        generation_summaries=tuple(state.summaries),
        best_candidates=tuple(best),
        frontier_points=tuple(state.archive.pareto(state.objectives)),
        lineage=dict(state.lineage),
        negative_results=tuple(state.negatives),
        cookbook_entries=(),
        ledger=dict(state.ledger_refs),
        calibration=tuple(state.calibrations),
    )
