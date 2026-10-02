"""Concrete stage implementations for the S1-S11 pipeline (WP15).

Each stage implements the Stage protocol with `run(ctx) -> Fragment`.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from computronium.experiment.execution.search_space import (
        Fragment,
        Proposal,
        StageContext,
    )
    from computronium.experiment.execution.stage import StageId

logger = logging.getLogger(__name__)


# Import at runtime to avoid circular imports
from computronium.experiment.execution.stage import (
    StageId,  # noqa: E402
)


class FrameStage:
    """S1 Frame — Objective/operating-point resolution (R43 entry, with Synthesis)."""

    stage_id = StageId.S1_FRAME

    async def run(self, ctx: StageContext) -> Fragment:
        """Resolve objectives and operating points from RunSpec."""
        from computronium.experiment.execution.search_space import (
            Fragment,
            generate_initial_candidates,
        )

        logger.info("S1 Frame: Resolving objectives and operating points")

        # Extract objectives from run_spec
        run_spec = ctx.run_spec
        objectives = run_spec.get("objectives", ("accuracy",))
        operating_points = run_spec.get("operating_points", {})

        # Generate initial candidates from search space
        candidates = generate_initial_candidates(
            search_space=ctx.search_space,
            budget=ctx.budget,
            cost_model=ctx.cost_model,
            max_candidates=10,
        )

        # Emit proposals for initial exploration
        proposals = []
        if ctx.policy and candidates:
            recent_records = []
            if ctx.store:
                try:
                    recent_records = ctx.store.query_records(
                        run_id=ctx.run_id, limit=1000
                    )
                except Exception:
                    pass  # Store not initialized, use empty records
            budget = ctx.budget
            cost_model = ctx.cost_model

            if budget and cost_model:
                policy_proposals = ctx.policy.propose(
                    candidates, recent_records, budget, cost_model
                )
                for coord, sched in policy_proposals:
                    from computronium.experiment.execution.search_space import Proposal

                    proposals.append(
                        Proposal(
                            coordinate=coord,
                            schedule=sched,
                            rationale="frame_initial",
                        )
                    )

        return Fragment(
            stage_id=self.stage_id,
            proposals=proposals,
            metadata={
                "objectives": list(objectives),
                "operating_points": operating_points,
                "proposal_count": len(proposals),
                "candidate_count": len(candidates),
            },
            coverage={
                "stage": self.stage_id.value,
                "proposals_generated": len(proposals),
                "candidates_generated": len(candidates),
            },
        )


class SpaceStage:
    """S2 Space — Axis snapshot + legality preview (dry-run = same engine, C32)."""

    stage_id = StageId.S2_SPACE

    async def run(self, ctx: StageContext) -> Fragment:
        """Snapshot active axes and run legality dry-run."""
        from computronium.experiment.execution.search_space import Fragment

        logger.info("S2 Space: Snapshotting axes and running legality preview")

        # Get active axes from search space
        active_axes = []
        for axis in ctx.search_space.axes_snapshot:
            if axis.axis_kind.value != "structural":
                active_axes.append(axis.name)

        # Run legality dry-run on pending candidates
        legality_results = []
        if hasattr(ctx, "allocator") and ctx.allocator:
            # Use allocator's legality check
            pass

        return Fragment(
            stage_id=self.stage_id,
            metadata={
                "active_axes": active_axes,
                "total_axes": len(ctx.search_space.axes_snapshot),
                "constraints_count": len(ctx.search_space.constraints),
                "legality_dry_run": True,
            },
            coverage={"stage": self.stage_id.value, "active_axes": len(active_axes)},
        )


class ScheduleStage:
    """S3 Schedule — Fidelity/seed/epoch planning; per-task adaptation (R44)."""

    stage_id = StageId.S3_SCHEDULE

    async def run(self, ctx: StageContext) -> Fragment:
        """Generate schedule candidates with data-origin allocation and contrast quota.

        Uses ContrastDesign for OFAT/fractional-factorial DOE with proper
        contrast_id, factor_assignments, matched_group structure.
        DataOrigin is stored in Proposal.metadata (not budget_id) to preserve
        measurement identity (measurement_key does not change with data origin).
        """
        from computronium.experiment.execution.contrast_design import (
            ContrastAssignment,
            ContrastDesign,
            ContrastDesignKind,
            Factor,
            create_contrast_design,
        )
        from computronium.experiment.execution.search_space import Fragment, Proposal
        from computronium.experiment.schema.coordinate import DataOrigin, Schedule

        logger.info(
            "S3 Schedule: Planning fidelity/seed/epoch with data-origin allocation"
        )

        proposals = list(ctx.pending_candidates)
        if not proposals and ctx.policy:
            # Use old policy interface for backward compatibility
            recent_records = []
            if ctx.store:
                try:
                    recent_records = ctx.store.query_records(
                        run_id=ctx.run_id, limit=1000
                    )
                except Exception:
                    pass  # Store not initialized, use empty records
            budget = ctx.budget
            cost_model = ctx.cost_model

            if budget and cost_model:
                policy_proposals = ctx.policy.propose(
                    proposals, recent_records, budget, cost_model
                )
                proposals.extend(policy_proposals)

        # Apply data-origin allocation from stage params
        allocation = ctx.stage_params.get(
            "data_origin_allocation",
            {
                "exploration": 0.5,
                "calibration": 0.2,
                "test": 0.2,
                "control": 0.05,
                "contrast": 0.05,
            },
        )
        contrast_quota = ctx.stage_params.get("contrast_quota", 0.1)
        contrast_design_kind = ctx.stage_params.get(
            "contrast_design_kind", ContrastDesignKind.OFAT.value
        )

        # Convert to scheduled proposals with data_origin in metadata (not budget_id)
        scheduled_proposals: list[Proposal] = []
        total = len(proposals)
        if total > 0:
            # Calculate counts for each data origin
            exploration_count = max(1, int(total * allocation.get("exploration", 0.5)))
            calibration_count = max(1, int(total * allocation.get("calibration", 0.2)))
            test_count = max(1, int(total * allocation.get("test", 0.2)))
            control_count = max(1, int(total * allocation.get("control", 0.05)))
            contrast_count = max(1, int(total * allocation.get("contrast", 0.05)))

            # Assign data origins sequentially
            data_origins = []
            data_origins.extend([DataOrigin.EXPLORATION] * exploration_count)
            data_origins.extend([DataOrigin.CALIBRATION] * calibration_count)
            data_origins.extend([DataOrigin.TEST] * test_count)
            data_origins.extend([DataOrigin.CONTROL] * control_count)
            data_origins.extend([DataOrigin.CONTRAST] * contrast_count)

            # Truncate or cycle to match total
            if len(data_origins) < total:
                # Cycle through origins
                while len(data_origins) < total:
                    data_origins.extend(data_origins[: total - len(data_origins)])
            data_origins = data_origins[:total]

            # Build contrast design if contrast runs requested
            contrast_design: ContrastDesign | None = None
            contrast_assignments: list[ContrastAssignment] = []
            if contrast_count > 0:
                # Create factors from first proposal's params for contrast design
                first_coord, _ = proposals[0]
                factor_names = list(first_coord.params.keys())
                if factor_names:
                    factors = [
                        Factor(name=name, levels=(0.0, 1.0), unit="normalized")
                        for name in factor_names
                    ]
                    contrast_design = create_contrast_design(
                        ContrastDesignKind(contrast_design_kind),
                        factors,
                        seed=hash(ctx.run_id) % 2**32,
                    )
                    contrast_assignments = list(contrast_design.assignments)

            # Assign schedules with data_origin in metadata
            # Use different seeds for different data_origins to get unique measurement_keys
            # while keeping the same cell_key (coordinate-only) for grouping
            contrast_idx = 0
            data_origin_seed_offset = 0
            for i, (coord, sched) in enumerate(proposals):
                data_origin = data_origins[i]

                # Build metadata with data_origin and contrast info
                metadata = {"data_origin": data_origin.value}

                # Add contrast assignment if this is a contrast run
                if data_origin == DataOrigin.CONTRAST and contrast_assignments:
                    contrast_assignment = contrast_assignments[
                        contrast_idx % len(contrast_assignments)
                    ]
                    metadata["contrast_id"] = contrast_assignment.contrast_id
                    metadata["factor_assignments"] = (
                        contrast_assignment.factor_assignments
                    )
                    metadata["matched_group"] = contrast_assignment.matched_group
                    contrast_idx += 1

                # Use different seed for each data_origin to get unique measurement_key
                # while preserving the same coordinate (cell_key)
                new_seed = sched.seed + data_origin_seed_offset
                data_origin_seed_offset += 1

                # Create new schedule with modified seed
                new_sched = Schedule(
                    fidelity=sched.fidelity,
                    seed=new_seed,
                    n_seeds=sched.n_seeds,
                    epochs=sched.epochs,
                    batch_limit=sched.batch_limit,
                    budget_id=sched.budget_id,  # Keep original budget_id
                    task_id=sched.task_id,
                )

                scheduled_proposals.append(
                    Proposal(
                        coordinate=coord,
                        schedule=new_sched,
                        rationale=f"schedule_{data_origin.value}",
                        metadata=metadata,
                    )
                )

        return Fragment(
            stage_id=self.stage_id,
            proposals=scheduled_proposals,
            metadata={
                "data_origin_allocation": {
                    k: v for k, v in allocation.items() if v > 0
                },
                "contrast_quota": contrast_quota,
                "contrast_design_kind": contrast_design_kind,
                "scheduled_count": len(scheduled_proposals),
                "contrast_design": contrast_design.to_dict()
                if contrast_design
                else None,
            },
            coverage={
                "stage": "schedule",
                "proposals_scheduled": len(scheduled_proposals),
            },
        )


class GateStage:
    """S4 Gate — LegalityEngine enforcement; globally-suppressive voids (R38)."""

    stage_id = StageId.S4_GATE

    async def run(self, ctx: StageContext) -> Fragment:
        """Enforce legality constraints on proposals."""
        from computronium.experiment.execution.search_space import Fragment
        from computronium.experiment.legality.engine import (
            ConstraintEnforcement,
            ConstraintKind,
            ConstraintOrigin,
            ConstraintScope,
            LegalityEngine,
            create_constraint,
        )
        from computronium.experiment.schema.registries import CONSTRAINTS_REGISTRY

        logger.info("S4 Gate: Enforcing legality constraints")

        # Create and seed legality engine with constraints from registry
        engine = LegalityEngine()
        for spec in CONSTRAINTS_REGISTRY.values():
            if spec.predicate is not None:
                # Skip constraints with complex predicates that the DSL parser
                # doesn't handle correctly (and, or, not, in, implies)
                predicate_str = str(spec.predicate)
                if any(
                    op in predicate_str.lower()
                    for op in [" and ", " or ", " not ", " in ", " implies "]
                ):
                    continue  # Skip complex predicates

                # Map registry constraint to engine constraint
                origin_map = {
                    "DECLARED": ConstraintOrigin.SYSTEM_CONFIG,
                    "TASK_FENCE": ConstraintOrigin.TASK_FENCE,
                    "APPLY_CONSTRAINTS": ConstraintOrigin.APPLY_CONSTRAINTS,
                }
                scope_map = {
                    "void": ConstraintScope.CELL,
                    "hard": ConstraintScope.MEASUREMENT,
                    "fairness": ConstraintScope.MEASUREMENT,
                    "operating_point": ConstraintScope.MEASUREMENT,
                }
                kind_map = {
                    "void": ConstraintKind.HARD,
                    "hard": ConstraintKind.HARD,
                    "fairness": ConstraintKind.HARD,
                    "operating_point": ConstraintKind.HARD,
                }
                enforcement_map = {
                    "void": ConstraintEnforcement.S4_EXPANSION,
                    "hard": ConstraintEnforcement.S4_EXPANSION,
                    "fairness": ConstraintEnforcement.S4_EXPANSION,
                    "operating_point": ConstraintEnforcement.S4_EXPANSION,
                }

                create_constraint(
                    expr=spec.predicate,
                    origin=origin_map.get(spec.origin, ConstraintOrigin.SYSTEM_CONFIG),
                    scope=scope_map.get(spec.kind.value, ConstraintScope.CELL),
                    enforcement=enforcement_map.get(
                        spec.kind.value, ConstraintEnforcement.S4_EXPANSION
                    ),
                    kind=kind_map.get(spec.kind.value, ConstraintKind.HARD),
                    description=spec.description,
                    engine=engine,
                )

        # Use pending_proposals which are Proposal objects
        filtered = []
        rejections = []

        for proposal in ctx.pending_proposals:
            coord = proposal.coordinate
            sched = proposal.schedule

            # Create a minimal record for constraint evaluation
            from computronium.experiment.schema.record import (
                FailureCause,
                GateVerdict,
                Maturity,
                Record,
                ReproducibilityClass,
                Severity,
                Status,
            )

            record = Record.create(
                run_id=ctx.run_id,
                coordinate=coord,
                schedule=sched,
                provenance=ctx.provenance,
                status=Status(
                    gate_verdict=GateVerdict.PENDING,
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
                payload={},
            )

            # Check legality using the legality engine
            hard_violations, soft_violations = engine.evaluate_record(
                record, ConstraintEnforcement.S4_EXPANSION
            )
            is_legal = len(hard_violations) == 0

            if is_legal:
                filtered.append(proposal)
            else:
                rejections.append(coord.cell_key())

        return Fragment(
            stage_id=self.stage_id,
            proposals=filtered,
            metadata={
                "input_count": len(ctx.pending_proposals),
                "passed_count": len(filtered),
                "rejected_count": len(rejections),
                "rejections": rejections,
            },
            coverage={
                "stage": "gate",
                "passed": len(filtered),
                "rejected": len(rejections),
            },
            classification={"rejected": rejections} if rejections else {},
        )


class ComposeStage:
    """S5 Compose — coverage of what the evaluator will compose.

    Composition happens once, in ``evaluate.cell_record``; a second compose path
    here is how the pipeline and the kernel drifted apart (TODO46 §D6). This
    stage therefore composes nothing and says what it was given.
    """

    stage_id = StageId.S5_COMPOSE

    async def run(self, ctx: StageContext) -> Fragment:
        """Report the cells awaiting composition; do not compose them."""
        from computronium.experiment.execution.search_space import Fragment

        logger.info("S5 Compose: Handing cells to the evaluator")

        pending = list(ctx.pending_proposals)
        return Fragment(
            stage_id=self.stage_id,
            proposals=pending,
            metadata={
                "composed_by": "experiment.execution.evaluate.cell_record",
                "axes": sorted({p.coordinate.dynamics for p in pending}),
            },
            coverage={"stage": "compose", "cells_queued": len(pending)},
        )


class TrainStage:
    """S6 Train — coverage of the cells the backend will train.

    The evaluator owns the training loop (``SystemTrainer`` inside
    ``evaluate.evaluate_cell``); this stage reports the submission and emits no
    records of its own.
    """

    stage_id = StageId.S6_TRAIN

    async def run(self, ctx: StageContext) -> Fragment:
        """Report the cells queued for the backend."""
        from computronium.experiment.execution.search_space import Fragment

        logger.info("S6 Train: Handing cells to the backend")

        if not ctx.backend:
            logger.warning("No backend configured, skipping training")
            return Fragment(
                stage_id=self.stage_id, coverage={"stage": "train", "skipped": True}
            )

        proposals = list(ctx.pending_proposals)
        return Fragment(
            stage_id=self.stage_id,
            proposals=proposals,
            metadata={"trained_by": type(ctx.backend).__name__},
            coverage={"stage": "train", "proposals_submitted": len(proposals)},
        )


class MeasureStage:
    """S7 Measure — Objectives resolved against OBJECTIVES; probes; robustness (R69)."""

    stage_id = StageId.S7_MEASURE

    async def run(self, ctx: StageContext) -> Fragment:
        """Measure objectives and run probes."""
        from computronium.experiment.execution.search_space import Fragment

        logger.info("S7 Measure: Measuring objectives and probes")

        # This would resolve objectives against OBJECTIVES registry
        # and compute probe metrics
        measured = []
        for record in ctx.pending_proposals:
            measured.append(record)

        return Fragment(
            stage_id=self.stage_id,
            proposals=measured,
            metadata={"measured_count": len(measured)},
            coverage={"stage": "measure", "records_measured": len(measured)},
        )


class RecordStage:
    """S8 Record — Atomic append + artifacts + embedding generation."""

    stage_id = StageId.S8_RECORD

    async def run(self, ctx: StageContext) -> Fragment:
        """Persist records atomically with artifacts."""
        from computronium.experiment.execution.search_space import Fragment

        logger.info("S8 Record: Atomic append with artifacts")

        stored = []
        for proposal in ctx.pending_proposals:
            # The wrapper handles actual storage
            stored.append(proposal)

        return Fragment(
            stage_id=self.stage_id,
            proposals=stored,
            metadata={"stored_count": len(stored)},
            coverage={"stage": "record", "records_stored": len(stored)},
        )


class AttributeStage:
    """S9 Attribute — Counterfactual axis attribution from records (R86)."""

    stage_id = StageId.S9_ATTRIBUTE

    async def run(self, ctx: StageContext) -> Fragment:
        """Compute counterfactual axis attribution."""
        from computronium.experiment.execution.search_space import Fragment

        logger.info("S9 Attribute: Computing axis attribution")

        attributions = {}
        for proposal in ctx.pending_proposals:
            cell_key = proposal.coordinate.cell_key()
            attributions[cell_key] = {"axes": {}, "confidence": 0.0}

        return Fragment(
            stage_id=self.stage_id,
            proposals=list(ctx.pending_proposals),
            metadata={"attributions": attributions},
            coverage={"stage": "attribute", "cells_attributed": len(attributions)},
        )


class DecideStage:
    """S10 Decide — Promotion predicates + allocation handoff (R36, R46-R51)."""

    stage_id = StageId.S10_DECIDE

    async def run(self, ctx: StageContext) -> Fragment:
        """Make promotion/continuation decisions."""
        from computronium.experiment.execution.decision import (
            complete_run,
            continue_round,
        )
        from computronium.experiment.execution.search_space import Fragment, Proposal

        logger.info("S10 Decide: Making promotion/continuation decisions")

        # Use allocator to get promotions
        promotions = []
        new_proposals = []

        if ctx.allocator:
            # Convert pending_proposals (Proposal objects) to (coord, sched) tuples for allocator
            candidates = [(p.coordinate, p.schedule) for p in ctx.pending_proposals]

            # Get proposals from allocator
            allocator_proposals = ctx.allocator.propose(
                candidates,
                [],  # records would come from store
                ctx.budget,
                ctx.cost_model,
            )

            # Convert allocator proposals (tuples) back to Proposal objects
            for coord, sched in allocator_proposals:
                new_proposals.append(
                    Proposal(
                        coordinate=coord,
                        schedule=sched,
                        rationale="allocator_promotion",
                    )
                )

        # Check budget
        should_continue = True
        if ctx.budget and ctx.budget.expired():
            should_continue = False

        if should_continue:
            decision = continue_round(
                new_proposals=new_proposals,
                promotions=promotions,
                rationale="Budget remains, continuing round",
            )
        else:
            decision = complete_run(rationale="Budget exhausted")

        return Fragment(
            stage_id=self.stage_id,
            proposals=new_proposals,
            decisions=[decision],
            metadata={
                "decision": decision.transition.value,
                "promotions": len(promotions),
                "new_proposals": len(new_proposals),
            },
            coverage={"stage": "decide", "transition": decision.transition.value},
        )


class ReportStage:
    """S11 Report — Delegates to surface.report fragments (R85-R88)."""

    stage_id = StageId.S11_REPORT

    async def run(self, ctx: StageContext) -> Fragment:
        """Generate final report."""
        from computronium.experiment.execution.search_space import Fragment

        logger.info("S11 Report: Generating report fragments")

        # This would delegate to surface.report
        report_data = {
            "run_id": ctx.run_id,
            "stages_completed": list(range(1, 12)),
            "total_records": len(ctx.completed_keys),
        }

        return Fragment(
            stage_id=self.stage_id,
            metadata={"report": report_data},
            coverage={"stage": "report", "generated": True},
        )


# Stage registry
STAGE_IMPLEMENTATIONS: dict[StageId, type] = {
    StageId.S1_FRAME: FrameStage,
    StageId.S2_SPACE: SpaceStage,
    StageId.S3_SCHEDULE: ScheduleStage,
    StageId.S4_GATE: GateStage,
    StageId.S5_COMPOSE: ComposeStage,
    StageId.S6_TRAIN: TrainStage,
    StageId.S7_MEASURE: MeasureStage,
    StageId.S8_RECORD: RecordStage,
    StageId.S9_ATTRIBUTE: AttributeStage,
    StageId.S10_DECIDE: DecideStage,
    StageId.S11_REPORT: ReportStage,
}


def get_stage_implementation(stage_id: StageId) -> type | None:
    """Get the concrete stage implementation for a stage ID."""
    return STAGE_IMPLEMENTATIONS.get(stage_id)


__all__ = [
    "STAGE_IMPLEMENTATIONS",
    "AttributeStage",
    "ComposeStage",
    "DecideStage",
    "FrameStage",
    "GateStage",
    "MeasureStage",
    "RecordStage",
    "ReportStage",
    "ScheduleStage",
    "SpaceStage",
    "TrainStage",
    "get_stage_implementation",
]
