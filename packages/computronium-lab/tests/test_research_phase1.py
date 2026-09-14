"""Phase 1 tests: autopoiesis kernel conformance, safety, selection."""

from __future__ import annotations

import random

import pytest
from computronium_lab import Constraints, Lab
from computronium_lab.research import (
    BUDGET_CAPS,
    BudgetTier,
    CampaignFitness,
    CoordinateGenome,
    ParetoSelection,
    ResearchConstitution,
    ResearchStagnationDetector,
    SafeMutationOperator,
    SurrogateFitness,
    crowding_distance,
    hypervolume,
    nondominated_sort,
)

from computronium.autopoiesis.protocols import (
    Constitution,
    FitnessMetric,
    MutationOperator,
    OperatorGenome,
    SelectionPolicy,
    StagnationDetector,
)


def _spec(constraints: Constraints | None = None):
    lab = Lab(seed=0)
    return lab.specify("flat_classification", "gaussian_blob", constraints=constraints)


def _seed_genome() -> CoordinateGenome:
    return CoordinateGenome.seed("backprop_mlp", _spec())


def test_protocol_conformance() -> None:
    spec = _spec()
    budget = BUDGET_CAPS[BudgetTier.SMOKE]
    assert isinstance(_seed_genome(), OperatorGenome)
    assert isinstance(SafeMutationOperator(), MutationOperator)
    assert isinstance(SurrogateFitness(spec), FitnessMetric)
    assert isinstance(ParetoSelection(), SelectionPolicy)
    assert isinstance(ResearchStagnationDetector(), StagnationDetector)
    assert isinstance(ResearchConstitution(spec, budget), Constitution)


def test_genome_roundtrip() -> None:
    genome = _seed_genome()
    clone = CoordinateGenome.from_payload(genome.genome())
    assert clone.digest == genome.digest
    assert clone.effective_spec.key() == genome.effective_spec.key()
    override = CoordinateGenome(
        mechanism="backprop_mlp",
        spec=genome.spec,
        substrate="memristive",
        lineage=("backprop_mlp",),
        mutations=("substrate_swap:digital->memristive",),
    )
    assert override.effective_spec.constraints.substrate == "memristive"
    assert CoordinateGenome.from_payload(override.genome()).digest == override.digest


def test_genome_instantiate_fresh() -> None:
    first = _seed_genome().instantiate()
    second = _seed_genome().instantiate()
    assert first is not second


def test_mutation_deterministic() -> None:
    operator = SafeMutationOperator()
    payload = _seed_genome().genome()
    first = operator.mutate(payload, random.Random(7))  # noqa: S311 - deterministic test seeds
    second = operator.mutate(payload, random.Random(7))  # noqa: S311 - deterministic test seeds
    assert first == second
    lineage = first["lineage"]
    assert isinstance(lineage, list)
    assert lineage[-1] == "backprop_mlp"
    mutations = first["mutations"]
    assert isinstance(mutations, list) and len(mutations) == 1


def test_mutation_stays_on_catalog() -> None:
    from computronium_lab.synthesis.catalog import CATALOG

    names = {c.name for c in CATALOG}
    operator = SafeMutationOperator()
    payload = _seed_genome().genome()
    for seed in range(20):
        mutant = operator.mutate(payload, random.Random(seed))  # noqa: S311 - deterministic test seeds
        assert mutant["mechanism"] in names


def test_constitution_admits_seed_rejects_invalid() -> None:
    spec = _spec()
    constitution = ResearchConstitution(spec, BUDGET_CAPS[BudgetTier.SMOKE])
    assert constitution.admits(_seed_genome().genome())
    bad = dict(_seed_genome().genome())
    bad["mechanism"] = "no_such_row"
    assert not constitution.admits(bad)
    impossible = dict(_seed_genome().genome())
    impossible["size_scale"] = 99.0
    assert not constitution.admits(impossible)


def test_constitution_rejects_unsupported_substrate_and_tight_budget() -> None:
    constitution = ResearchConstitution(_spec(), BUDGET_CAPS[BudgetTier.SMOKE])
    payload = _seed_genome().genome()
    payload["substrate_override"] = "quantum"
    assert not constitution.admits(payload)
    tight = _spec(constraints=Constraints(substrate="digital", latency_ms=0.001))
    tight_constitution = ResearchConstitution(tight, BUDGET_CAPS[BudgetTier.SMOKE])
    tight_genome = CoordinateGenome.seed("backprop_mlp", tight)
    assert not tight_constitution.admits(tight_genome.genome())


def test_surrogate_scores() -> None:
    fitness = SurrogateFitness(_spec())
    genome = _seed_genome()
    score = fitness.score(genome, None)
    assert 0.0 <= score <= 1.5
    vector = fitness.score_vector(genome)
    assert set(vector) == {
        "accuracy",
        "adaptation_speed",
        "stability",
        "latency",
        "memory",
    }


def test_nondominated_sort_and_crowding() -> None:
    objectives = (("accuracy", True), ("latency", False))
    vectors = [
        {"accuracy": 0.9, "latency": 5.0},
        {"accuracy": 0.8, "latency": 5.0},
        {"accuracy": 0.9, "latency": 8.0},
    ]
    fronts = nondominated_sort(vectors, objectives)
    assert fronts[0] == [0]
    assert set(fronts[1]) == {1, 2}
    distances = crowding_distance([vectors[1], vectors[2]], objectives)
    assert all(d == float("inf") for d in distances)


def test_pareto_select_topk() -> None:
    selection = ParetoSelection()
    population: list[tuple[object, float]] = [("a", 0.9), ("b", 0.5), ("c", 0.7)]
    assert selection.select(population, 2) == ["a", "c"]


def test_hypervolume_grows_with_frontier() -> None:
    objectives = (("accuracy", True), ("latency", False))
    reference = {"accuracy": 0.0, "latency": 10.0}
    single = hypervolume([{"accuracy": 0.9, "latency": 5.0}], objectives, reference)
    assert single == pytest.approx(0.9 * 5.0)
    grown = hypervolume(
        [
            {"accuracy": 0.9, "latency": 5.0},
            {"accuracy": 0.8, "latency": 3.0},
        ],
        objectives,
        reference,
    )
    assert grown > single


def test_stagnation_detector() -> None:
    detector = ResearchStagnationDetector(patience=2)
    assert detector.update(0.5) is False
    assert detector.update(0.5) is False
    assert detector.update(0.5) is True
    assert detector.update(0.9) is False
    assert detector.exhausted(2, 2) is True
    assert detector.exhausted(1, 2) is False


def test_campaign_fitness_smoke() -> None:
    lab = Lab(seed=0)
    spec = lab.specify("flat_classification", "gaussian_blob")
    fitness = CampaignFitness(spec)
    evaluation = fitness.evaluate(
        CoordinateGenome.seed("backprop_mlp", spec), lab, seeds=(0,), epochs=1
    )
    assert 0.0 <= evaluation.objectives["accuracy"] <= 1.0
    assert evaluation.metric_sources["accuracy"] in {
        "val_accuracy",
        "train_accuracy",
    }
    assert set(evaluation.gate_outcomes) == {
        "BenchmarkReproduction",
        "StabilityCertificate",
        "DeployabilityCheck",
    }
    assert evaluation.seeds == (0,)
