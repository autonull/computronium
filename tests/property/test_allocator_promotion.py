"""Evidence-driven allocation lock (C10).

The allocator promotes cells on threshold-crossing improvement, detects
divergence (score explosion wastes the evaluation), and detects stagnation
(no improvement across the patience window). Replaces the deleted pillar
verifying test for capability C10 (TODO44 Phase F2).
"""

from __future__ import annotations

import pytest

from computronium.experiment.execution import EvidenceDrivenAllocator
from computronium.experiment.schema import (
    Coordinate,
    FailureCause,
    GateVerdict,
    Maturity,
    Provenance,
    Record,
    ReproducibilityClass,
    Schedule,
    Severity,
    Status,
)


def _record(cell_key: str, seed: int, accuracy: float, fidelity: str = "L0") -> Record:
    coord = Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="instantaneous",
        plasticity="null",
        credit="gradient",
        update="euclidean",
        params={},
    )
    schedule = Schedule(
        fidelity=fidelity,
        seed=seed,
        n_seeds=1,
        epochs=1,
        batch_limit=0,
        budget_id="test",
    )
    record = Record.create(
        run_id="c10",
        coordinate=coord,
        schedule=schedule,
        provenance=Provenance(
            env={}, dataset="t", dataset_version="1", code_sha="s", policy="p", links={}
        ),
        status=Status(
            gate_verdict=GateVerdict.PASS_,
            defect="",
            cause=FailureCause.UNKNOWN,
            severity=Severity.LOW,
            quarantine=False,
            maturity=Maturity.L0,
            uncertainty={},
            reproducibility=ReproducibilityClass.REPLAYABLE,
            assessment_procedure_version="1.0",
            ceec_link=None,
        ),
        payload={"accuracy": accuracy},
    )
    object.__setattr__(record, "cell_key", cell_key)
    return record


@pytest.fixture()
def allocator() -> EvidenceDrivenAllocator:
    return EvidenceDrivenAllocator(promotion_threshold=0.05)


class TestEvidenceDrivenAllocation:
    def test_first_observation_nominates_next_fidelity(self, allocator) -> None:
        allocator.observe(_record("cell_a", 1, 0.5))
        candidate = allocator._state.promotion_candidates["cell_a"]
        assert candidate.current_fidelity == "L1"
        assert candidate.best_score == 0.5
        allocator.observe(_record("cell_a", 2, 0.8))
        candidate = allocator._state.promotion_candidates["cell_a"]
        assert candidate.best_score == 0.8
        assert candidate.n_seeds_completed == 2

    def test_subthreshold_improvement_keeps_prior_best(self, allocator) -> None:
        allocator.observe(_record("cell_b", 1, 0.5))
        allocator.observe(_record("cell_b", 2, 0.53))
        candidate = allocator._state.promotion_candidates["cell_b"]
        assert candidate.best_score == 0.5

    def test_divergence_is_wasted(self, allocator) -> None:
        allocator.observe(_record("cell_c", 1, 0.5))
        allocator.observe(_record("cell_c", 2, 0.6))
        allocator.observe(_record("cell_c", 3, 10.0))
        assert allocator.get_waste_report()["wasted_evaluations"] == 1
        # The exploded score must not poison the promotion candidate.
        assert allocator._state.promotion_candidates["cell_c"].best_score == 0.6
        telemetry = allocator.get_telemetry()
        assert telemetry["divergence_candidates"] == 1

    def test_stagnation_detected(self, allocator) -> None:
        for seed, acc in ((1, 0.5), (2, 0.5), (3, 0.5)):
            allocator.observe(_record("cell_d", seed, acc))
        assert allocator._is_stagnant("cell_d")
        telemetry = allocator.get_telemetry()
        assert telemetry["stagnation_candidates"] == 1
        assert allocator._state.stagnation_score == 0.5

    def test_at_max_fidelity_no_candidate(self, allocator) -> None:
        allocator.observe(_record("cell_e", 1, 0.5, fidelity="L2"))
        allocator.observe(_record("cell_e", 2, 0.9, fidelity="L2"))
        assert "cell_e" not in allocator._state.promotion_candidates
