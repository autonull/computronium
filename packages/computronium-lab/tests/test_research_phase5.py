"""Phase 5 tests: substrate transfer benchmark and ranking."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from computronium_lab import Lab
from computronium_lab.research import (
    BUDGET_CAPS,
    BudgetTier,
    CoordinateGenome,
    ResearchConstitution,
    SafeMutationOperator,
)

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_benchmark_transfer_smoke(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    lab = Lab(seed=0)
    report = lab.benchmark_substrate_transfer(
        mechanism="backprop_mlp",
        source_substrate="digital",
        target_constraints=("int8", "ternary"),
        seeds=(0,),
    )
    assert report.mechanism == "backprop_mlp"
    assert set(report.ranking) == {"int8", "ternary"}
    for score in report.scores:
        assert score.energy_tier == "simulated"
        assert isinstance(score.export_success, bool)
    assert report.manifest_paths
    assert report.cookbook_drafts


def test_benchmark_transfer_memristive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    lab = Lab(seed=0)
    report = lab.benchmark_substrate_transfer(
        mechanism="backprop_mlp",
        target_constraints=("memristive",),
        seeds=(0,),
    )
    assert len(report.scores) == 1
    assert report.scores[0].target == "memristive"


def test_benchmark_unknown_target() -> None:
    lab = Lab(seed=0)
    try:
        lab.benchmark_substrate_transfer(target_constraints=("quantum",), seeds=(0,))
    except ValueError as exc:
        assert "unknown transfer target" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_substrate_mutation_admitted() -> None:
    """T24.5.3: evolutionary substrate mutation over supported paths."""
    lab = Lab(seed=0)
    spec = lab.specify("flat_classification", "gaussian_blob")
    constitution = ResearchConstitution(spec, BUDGET_CAPS[BudgetTier.QUICK])
    operator = SafeMutationOperator()
    seen_substrate = False
    genome = CoordinateGenome.seed("backprop_mlp", spec)
    for trial in range(60):
        mutant = operator.mutate(genome.genome(), random.Random(trial))  # ruff: ignore[suspicious-non-cryptographic-random-usage] - deterministic test seeds
        mutations = mutant["mutations"]
        assert isinstance(mutations, list)
        if any(str(m).startswith("substrate_swap") for m in mutations):
            seen_substrate = True
            assert mutant["substrate_override"] != "neuromorphic"
            assert constitution.admits(mutant)
    assert seen_substrate
