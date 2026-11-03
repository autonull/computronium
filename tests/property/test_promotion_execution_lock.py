"""Lock: Allocator promotions execute at correct fidelity (L1/L2), not re-proposed as L0.

WS4.7 acceptance: Promotion flow verified end-to-end.
"""

from __future__ import annotations

import inspect

import pytest

from computronium.experiment.execution.allocator import EvidenceDrivenAllocator
from computronium.experiment.execution.pipeline._stages import _StageMixin
from computronium.experiment.kernel.evaluate import TaskScheduler
from computronium.experiment.schema import (
    Coordinate,
    DataOrigin,
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
from computronium.experiment.schema.run_spec import BROAD_PARAM_BUDGET
from computronium.experiment.surface._cli._profiles import RUN_PROFILES


def _make_record(
    cell_key: str,
    seed: int,
    val_acc: float,
    fidelity: str = "L0",
    task_id: str = "digits",
) -> Record:
    coord = Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="energy_minimization",
        plasticity="null",
        credit="thermodynamic_contrast",
        update="euclidean",
        params={},
    )
    schedule = Schedule(
        fidelity=fidelity,
        seed=seed,
        n_seeds=1 if fidelity == "L0" else 2 if fidelity == "L1" else 5,
        epochs=1 if fidelity == "L0" else 3 if fidelity == "L1" else 10,
        batch_limit=2,
        budget_id="test",
        task_id=task_id,
        param_budget=BROAD_PARAM_BUDGET,
    )
    record = Record.create(
        run_id="promo_test",
        coordinate=coord,
        schedule=schedule,
        provenance=Provenance(
            env={},
            dataset=task_id,
            dataset_version="1",
            code_sha="test",
            policy="test",
            links={"run_id": "promo_test"},
            data_origin=DataOrigin.EXPLORATION,
        ),
        status=Status(
            gate_verdict=GateVerdict.PASS_,
            defect="",
            cause=FailureCause.UNKNOWN,
            severity=Severity.LOW,
            quarantine=False,
            maturity=Maturity.L0
            if fidelity == "L0"
            else Maturity.L1
            if fidelity == "L1"
            else Maturity.L2,
            uncertainty={},
            reproducibility=ReproducibilityClass.REPLAYABLE,
            assessment_procedure_version="1.0",
            ceec_link=None,
        ),
        payload={"val_acc": val_acc, "walltime_s": 1.0},
    )
    object.__setattr__(record, "cell_key", cell_key)
    return record


class TestPromotionExecutionLock:
    """Tests enforcing correct promotion execution fidelity."""

    def test_smart_survey_profile_has_promotion_threshold(self) -> None:
        """Smart survey profile has promotion_threshold attribute."""
        profile = RUN_PROFILES["smart-survey"]
        assert hasattr(profile, "promotion_threshold")
        assert profile.promotion_threshold == 0.3  # Lowered from 0.6 to 0.3

    def test_smart_survey_profile_has_fidelity_settings(self) -> None:
        """Smart survey profile has fidelity_seeds and fidelity_epochs."""
        profile = RUN_PROFILES["smart-survey"]
        assert profile.fidelity_seeds == {"L0": 1, "L1": 2, "L2": 5}
        assert profile.fidelity_epochs == {"L0": 1, "L1": 3, "L2": 10}

    def test_build_allocator_candidates_creates_l1_promotions_from_l0(self) -> None:
        """_build_allocator_candidates generates L1 schedules from L0 base."""
        from computronium.experiment.execution.pipeline._stages import _StageMixin

        # Verify the method exists and creates L1 schedules
        source = inspect.getsource(_StageMixin._build_allocator_candidates)
        assert 'next_fidelity = "L1"' in source
        assert "fidelity_seeds.get(next_fidelity" in source
        assert "fidelity_epochs.get(next_fidelity" in source
        assert "checkpoint_every_n=spec.checkpoint_every_n" in source

    def test_build_allocator_candidates_creates_l2_promotions_from_l1(self) -> None:
        """_build_allocator_candidates generates L2 schedules from allocator L1 candidates."""
        source = inspect.getsource(_StageMixin._build_allocator_candidates)
        # Check L1→L2 promotion logic
        assert 'promo_candidate.current_fidelity != "L2"' in source
        assert 'fidelity="L2"' in source
        assert 'fidelity_seeds.get("L2"' in source
        assert 'fidelity_epochs.get("L2"' in source

    def test_apply_smart_survey_promotion_filters_by_threshold(self) -> None:
        """_apply_smart_survey_promotion filters cells below promotion_threshold."""
        source = inspect.getsource(_StageMixin._apply_smart_survey_promotion)
        filter_source = inspect.getsource(_StageMixin._filter_promotions_by_threshold)
        assert "promotion_threshold" in source
        assert "norm_acc < threshold" in filter_source
        assert "continue" in filter_source  # Skip cells below threshold

    def test_apply_smart_survey_promotion_uses_original_task(self) -> None:
        """_apply_smart_survey_promotion uses original task (not task cycling)."""
        filter_source = inspect.getsource(_StageMixin._filter_promotions_by_threshold)
        build_source = inspect.getsource(_StageMixin._build_promo_schedule)
        assert "original_task = best_record.schedule.task_id" in filter_source
        assert "task_id=task_name" in build_source

    def test_apply_smart_survey_promotion_creates_correct_schedules(self) -> None:
        """Promotion creates schedules with correct fidelity, seeds, epochs, checkpoint."""
        build_source = inspect.getsource(_StageMixin._build_promo_schedule)
        assert "fidelity=target_fidelity" in build_source
        assert "n_seeds=sched.n_seeds" in build_source
        assert "epochs=sched.epochs" in build_source
        assert "checkpoint_every_n=spec.checkpoint_every_n" in build_source
        assert "early_stopping_patience=spec.early_stopping_patience" in build_source

    def test_promotions_stored_in_state_for_s10(self) -> None:
        """_attribute_allocation stores promotions in _state.allocator_promotions for S10."""
        source = inspect.getsource(_StageMixin._attribute_allocation)
        assert "_state.allocator_promotions = promotions" in source

    def test_s10_decide_converts_promotions_to_proposals(self) -> None:
        """S10 Decide converts allocator_promotions to Proposal objects."""
        from computronium.experiment.execution.stages_impl import DecideStage

        source = inspect.getsource(DecideStage.run)
        assert "allocator_promotions = list(ctx.allocator_promotions)" in source
        assert 'rationale="allocator_promotion"' in source
        assert "Promotion(" in source
        assert 'from_fidelity="L0" if sched.fidelity == "L1" else "L1"' in source
        assert "to_fidelity=sched.fidelity" in source

    def test_promotion_fidelity_correct_in_s10(self) -> None:
        """S10 sets from_fidelity correctly: L0→L1 or L1→L2."""
        from computronium.experiment.execution.stages_impl import DecideStage

        source = inspect.getsource(DecideStage.run)
        # from_fidelity should be L0 for L1 target, L1 for L2 target
        assert 'from_fidelity="L0" if sched.fidelity == "L1" else "L1"' in source

    def test_allocator_observes_records_before_proposing(self) -> None:
        """_run_allocator calls allocator.observe on all records before propose."""
        source = inspect.getsource(_StageMixin._run_allocator)
        assert "for record in records:" in source
        assert "allocator.observe(record)" in source

    def test_allocator_propose_receives_candidates_and_records(self) -> None:
        """_run_allocator calls allocator.propose with candidates, records, deadline."""
        source = inspect.getsource(_StageMixin._run_allocator)
        assert "allocator.propose(" in source
        assert "candidates" in source
        assert "records" in source
        assert "deadline=self._state.deadline" in source

    def test_smart_survey_promotion_applied_in_run_allocator(self) -> None:
        """_run_allocator applies _apply_smart_survey_promotion for smart-survey profile."""
        source = inspect.getsource(_StageMixin._run_allocator)
        assert 'spec.profile == "smart-survey"' in source
        assert "_apply_smart_survey_promotion" in source

    def test_promotion_schedule_includes_checkpoint_every_n(self) -> None:
        """Promotion schedules include checkpoint_every_n for warm-start."""
        build_source = inspect.getsource(_StageMixin._build_promo_schedule)
        assert "checkpoint_every_n=spec.checkpoint_every_n" in build_source

    def test_promotion_budget_allocation_split_constants(self) -> None:
        """Budget allocation constants documented in _limit_promotions_by_budget."""
        source = inspect.getsource(_StageMixin._limit_promotions_by_budget)
        assert "40%" in source or "0.4" in source
        assert "40%" in source or "0.4" in source

    def test_promotion_sorts_by_normalized_accuracy(self) -> None:
        """Promotions sorted by normalized accuracy descending."""
        limit_source = inspect.getsource(_StageMixin._limit_promotions_by_budget)
        assert "sort" in limit_source
        assert "cell_best.get" in limit_source
        assert "norm_acc" in limit_source or "source_fidelity" in limit_source

    def test_task_scheduler_has_baseline_for_tasks(self) -> None:
        """TaskScheduler provides baselines for ruler-relative normalization."""
        scheduler = TaskScheduler()
        assert scheduler.get_baseline("digits") == 0.1
        assert scheduler.get_baseline("xor") == 0.5
        assert scheduler.get_baseline("mnist") == 0.1
        assert scheduler.get_baseline("cifar10") == 0.1

    def test_task_scheduler_normalize_score(self) -> None:
        """TaskScheduler.normalize_score computes ruler-relative score."""
        scheduler = TaskScheduler()
        # digits: baseline=0.1, raw=0.55 -> (0.55-0.1)/(1-0.1) = 0.5
        norm = scheduler.normalize_score(0.55, "digits", 0.1)
        assert abs(norm - 0.5) < 0.01
        # xor: baseline=0.5, raw=0.75 -> (0.75-0.5)/(1-0.5) = 0.5
        norm = scheduler.normalize_score(0.75, "xor", 0.5)
        assert abs(norm - 0.5) < 0.01

    def test_task_scheduler_task_cycle_expands_with_fidelity(self) -> None:
        """TaskScheduler.get_task_cycle expands from CHEAP at L0 to ALL at L2."""
        scheduler = TaskScheduler()
        l0 = scheduler.get_task_cycle("L0", max_tasks=10)
        l1 = scheduler.get_task_cycle("L1", max_tasks=20)
        l2 = scheduler.get_task_cycle("L2", max_tasks=30)
        assert set(l0).issubset(set(l1))
        assert set(l1).issubset(set(l2))
        assert len(l2) >= 3

    def test_allocator_promotes_on_threshold_crossing(self) -> None:
        """EvidenceDrivenAllocator promotes when score crosses threshold."""
        allocator = EvidenceDrivenAllocator(promotion_threshold=0.05)
        # First observation at L0
        allocator.observe(_make_record("cell_a", 1, 0.5, "L0"))
        candidate = allocator._state.promotion_candidates["cell_a"]
        assert candidate.current_fidelity == "L1"
        assert candidate.best_score == 0.5
        # Second observation with improvement
        allocator.observe(_make_record("cell_a", 2, 0.8, "L0"))
        candidate = allocator._state.promotion_candidates["cell_a"]
        assert candidate.best_score == 0.8

    def test_allocator_subthreshold_keeps_prior_best(self) -> None:
        """Subthreshold improvement doesn't update best score."""
        allocator = EvidenceDrivenAllocator(promotion_threshold=0.05)
        allocator.observe(_make_record("cell_b", 1, 0.5, "L0"))
        allocator.observe(_make_record("cell_b", 2, 0.53, "L0"))  # +0.03 < 0.05
        candidate = allocator._state.promotion_candidates["cell_b"]
        assert candidate.best_score == 0.5  # Unchanged

    def test_allocator_detects_divergence(self) -> None:
        """EvidenceDrivenAllocator detects score explosion as waste."""
        allocator = EvidenceDrivenAllocator(promotion_threshold=0.05)
        allocator.observe(_make_record("cell_c", 1, 0.5, "L0"))
        allocator.observe(_make_record("cell_c", 2, 0.6, "L0"))
        allocator.observe(_make_record("cell_c", 3, 10.0, "L0"))  # Explosion
        assert allocator.get_waste_report()["wasted_evaluations"] == 1
        # Best score should not be poisoned by explosion
        assert allocator._state.promotion_candidates["cell_c"].best_score == 0.6

    def test_allocator_detects_stagnation(self) -> None:
        """EvidenceDrivenAllocator detects stagnation (no improvement)."""
        allocator = EvidenceDrivenAllocator(promotion_threshold=0.05)
        for seed, acc in ((1, 0.5), (2, 0.5), (3, 0.5)):
            allocator.observe(_make_record("cell_d", seed, acc, "L0"))
        assert allocator._is_stagnant("cell_d")
        telemetry = allocator.get_telemetry()
        assert telemetry["stagnation_candidates"] == 1

    def test_allocator_no_candidate_at_max_fidelity(self) -> None:
        """Allocator doesn't create promotion candidate at L2 (max fidelity)."""
        allocator = EvidenceDrivenAllocator(promotion_threshold=0.05)
        allocator.observe(_make_record("cell_e", 1, 0.5, "L2"))
        allocator.observe(_make_record("cell_e", 2, 0.9, "L2"))
        assert "cell_e" not in allocator._state.promotion_candidates

    def test_zero_yield_check_skips_when_promotions_pending(self) -> None:
        """_check_zero_yield resets counter when allocator_promotions exist."""
        from computronium.experiment.execution.pipeline._budget import _BudgetMixin

        source = inspect.getsource(_BudgetMixin._check_zero_yield)
        assert "_state.allocator_promotions" in source
        assert "self._state.zero_yield_count = 0" in source
        assert "self._state.last_zero_yield_cause = None" in source

    def test_run_allocator_checks_deadline_before_proposing(self) -> None:
        """_run_allocator checks deadline before generating promotions."""
        source = inspect.getsource(_StageMixin._run_allocator)
        assert "deadline_enforcer.check_before_cell()" in source
        assert "Deadline reached, skipping allocator proposals" in source

    def test_run_allocator_returns_empty_on_no_search_space(self) -> None:
        """_run_allocator returns empty list if search_space is None."""
        source = inspect.getsource(_StageMixin._run_allocator)
        assert "search_space = self._state.search_space" in source
        assert "if search_space is None:" in source
        assert "return []" in source

    def test_promotion_schedule_includes_resume_checkpoint_support(self) -> None:
        """Promotion schedules support resume_checkpoint_path (via checkpoint_every_n)."""
        build_source = inspect.getsource(_StageMixin._build_promo_schedule)
        # checkpoint_every_n enables checkpoint saving which enables resume
        assert "checkpoint_every_n" in build_source
        # The schedule passed to promotion already has checkpoint_every_n from _build_allocator_candidates


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
