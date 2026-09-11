"""TODO23 Phase 1 synthesis-layer tests."""

from __future__ import annotations

import pytest
from computronium_lab import Lab
from computronium_lab.synthesis import (
    Constraints,
    ExplorationBudgetExhausted,
    ProblemSpec,
    explore,
    filter_catalog,
    synthesize,
)
from computronium_lab.synthesis.catalog import CATALOG
from computronium_lab.synthesis.predictor import ViabilityModel
from computronium_lab.synthesis.spec import KNOWN_OBJECTIVES

DIGITAL = Constraints(substrate="digital")
MEMRISTIVE = Constraints(substrate="memristive")
LOCAL_ONLY = Constraints(substrate="digital", local_credit=True)


def _spec(**kw: object) -> ProblemSpec:
    return ProblemSpec(
        task="image_classification",
        dataset="cifar100",
        **kw,  # type: ignore[arg-type]
    )


def test_spec_validation() -> None:
    spec = _spec(constraints=DIGITAL, objectives=("accuracy", "stability"))
    assert "stability" in KNOWN_OBJECTIVES
    assert spec.key().startswith("image_classification/cifar100")
    with pytest.raises(ValueError, match="unknown substrate"):
        Constraints(substrate="biological")
    with pytest.raises(ValueError, match="unknown objectives"):
        _spec(objectives=("profit",))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="exploration_budget"):
        _spec(exploration_budget=0)


def test_constraint_filter() -> None:
    memristive = {c.name for c in filter_catalog(_spec(constraints=MEMRISTIVE))}
    assert memristive == {"backprop_mlp"}
    local = {c.name for c in filter_catalog(_spec(constraints=LOCAL_ONLY))}
    assert local == {"ff_mlp"}
    tight = {
        c.name
        for c in filter_catalog(
            _spec(constraints=Constraints(latency_ms=4.5, memory_gb=0.5))
        )
    }
    assert tight == {"ff_mlp"}
    with pytest.raises(ValueError, match="no catalog mechanism"):
        synthesize(_spec(constraints=Constraints(substrate="quantum")))


def test_synthesize_validated_coordinate_with_provenance() -> None:
    result = synthesize(_spec(constraints=DIGITAL))
    assert set(result.coordinate) == {
        "substrate",
        "geometry",
        "dynamics",
        "plasticity",
        "credit",
        "update",
    }
    assert result.provenance and all(result.provenance)
    assert "predicted viability" in result.provenance[2]
    assert result.candidate.config_builder is not None
    system = result.build(_spec(constraints=DIGITAL))
    assert system is not None


def test_continual_prefers_psi_runtime() -> None:
    result = synthesize(_spec(constraints=Constraints(continual=True)))
    assert result.name == "temporal_psi_task_switcher"


class _LowConfidenceModel:
    """Stub predictor forcing the exploratory branch (DI over mocking)."""

    cv_accuracy = 0.9
    holdout_geometry_accuracy = 0.9

    def predict(self, features: object) -> float:
        return 0.3

    def rationale(self, features: object) -> str:
        return "stub"


def test_exploration_budget_gate() -> None:
    spec = _spec(
        constraints=MEMRISTIVE,
        exploration_budget=1,
    )
    campaigns: dict[str, int] = {}
    first = synthesize(spec, model=_LowConfidenceModel(), campaigns_run=campaigns)  # type: ignore[arg-type]
    assert first.exploratory and first.confidence < 0.7
    assert campaigns.get(spec.key()) == 1
    with pytest.raises(ExplorationBudgetExhausted, match="budget"):
        synthesize(spec, model=_LowConfidenceModel(), campaigns_run=campaigns)  # type: ignore[arg-type]


def test_explore_pareto_frontier() -> None:
    options = explore(_spec(constraints=DIGITAL, objectives=("accuracy", "memory")))
    names = {o.name for o in options}
    assert names and names <= {c.name for c in CATALOG}
    for o in options:
        for other in options:
            if other.name == o.name:
                continue
            assert not (
                other.metrics["accuracy"] >= o.metrics["accuracy"]
                and other.metrics["memory_gb"] <= o.metrics["memory_gb"]
                and (
                    other.metrics["accuracy"] > o.metrics["accuracy"]
                    or other.metrics["memory_gb"] < o.metrics["memory_gb"]
                )
            ), f"{other.name} dominates {o.name}"


def test_predictor_depth_matched_fit() -> None:
    model = ViabilityModel().fit()
    assert model.cv_accuracy >= 0.85
    assert model.holdout_geometry_accuracy >= 0.90


def test_lab_wire_end_to_end() -> None:
    lab = Lab()
    spec = lab.specify(
        "image_classification",
        "cifar100",
        constraints=DIGITAL,
        objectives=("accuracy", "stability"),
    )
    result = lab.synthesize(spec)
    assert result.confidence > 0.7 and not result.exploratory
    metrics = lab.train(result.build(spec), epochs=1)
    assert metrics["accuracy"] > 0.0
    frontier = lab.explore(spec)
    assert frontier
