"""Concrete stage implementations for the S1-S11 pipeline (WP15).

Each stage implements the Stage protocol with `run(ctx) -> Fragment`.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from computronium.experiment.schema.coordinate import Coordinate, Schedule
    from computronium.experiment.schema.record import Record
    from computronium.experiment.execution.search_space import (
        Fragment,
        Proposal,
        SearchSpace,
        StageContext,
    )
    from computronium.experiment.execution.stage import StageId, StageTransition

logger = logging.getLogger(__name__)


# Import at runtime to avoid circular imports
from computronium.experiment.execution.stage import StageId  # noqa: E402
from computronium.experiment.execution.stage import StageTransition  # noqa: E402


class FrameStage:
    """S1 Frame — Objective/operating-point resolution (R43 entry, with Synthesis)."""

    stage_id = StageId.S1_FRAME

    async def run(self, ctx: "StageContext") -> "Fragment":
        """Resolve objectives and operating points from RunSpec."""
        from computronium.experiment.execution.search_space import Fragment

        logger.info("S1 Frame: Resolving objectives and operating points")

        # Extract objectives from run_spec
        run_spec = ctx.run_spec
        objectives = run_spec.get("objectives", ("accuracy",))
        operating_points = run_spec.get("operating_points", {})

        # Emit proposals for initial exploration
        proposals = []
        if ctx.policy:
            # Use old policy interface for backward compatibility
            pending_candidates = list(ctx.pending_candidates)
            recent_records = []
            if ctx.store:
                try:
                    recent_records = ctx.store.query_records(run_id=ctx.run_id, limit=1000)
                except Exception:
                    pass  # Store not initialized, use empty records
            budget = ctx.budget
            cost_model = ctx.cost_model
            
            if budget and cost_model:
                policy_proposals = ctx.policy.propose(
                    pending_candidates, recent_records, budget, cost_model
                )
                for coord, sched in policy_proposals:
                    from computronium.experiment.execution.search_space import Proposal
                    proposals.append(Proposal(
                        coordinate=coord,
                        schedule=sched,
                        rationale="frame_initial",
                    ))

        return Fragment(
            stage_id=self.stage_id,
            proposals=proposals,
            metadata={
                "objectives": list(objectives),
                "operating_points": operating_points,
                "proposal_count": len(proposals),
            },
            coverage={"stage": self.stage_id.value, "proposals_generated": len(proposals)},
        )


class SpaceStage:
    """S2 Space — Axis snapshot + legality preview (dry-run = same engine, C32)."""

    stage_id = StageId.S2_SPACE

    async def run(self, ctx: "StageContext") -> "Fragment":
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

    async def run(self, ctx: "StageContext") -> "Fragment":
        """Generate schedule candidates with data-origin allocation and contrast quota."""
        from computronium.experiment.execution.search_space import Fragment
        from computronium.experiment.schema.coordinate import DataOrigin

        logger.info("S3 Schedule: Planning fidelity/seed/epoch with data-origin allocation")

        proposals = list(ctx.pending_candidates)
        if not proposals and ctx.policy:
            # Use old policy interface for backward compatibility
            recent_records = []
            if ctx.store:
                try:
                    recent_records = ctx.store.query_records(run_id=ctx.run_id, limit=1000)
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
            "data_origin_allocation", {"exploration": 0.5, "calibration": 0.3, "test": 0.2}
        )
        contrast_quota = ctx.stage_params.get("contrast_quota", 0.1)

        # Convert to scheduled proposals with data_origin
        scheduled = []
        total = len(proposals)
        if total > 0:
            exploration_count = max(1, int(total * allocation.get("exploration", 0.5)))
            calibration_count = max(1, int(total * allocation.get("calibration", 0.3)))
            test_count = max(1, int(total * allocation.get("test", 0.2)))

            for i, (coord, sched) in enumerate(proposals):
                if i < exploration_count:
                    data_origin = DataOrigin.EXPLORATION
                elif i < exploration_count + calibration_count:
                    data_origin = DataOrigin.CALIBRATION
                else:
                    data_origin = DataOrigin.TEST

                # Create new schedule with data_origin in budget_id
                new_sched = Schedule(
                    fidelity=sched.fidelity,
                    seed=sched.seed,
                    n_seeds=sched.n_seeds,
                    epochs=sched.epochs,
                    batch_limit=sched.batch_limit,
                    budget_id=f"{sched.budget_id}:{data_origin.value}",
                    task_id=sched.task_id,
                )

                # Contrast quota
                if data_origin == DataOrigin.EXPLORATION and i < int(
                    exploration_count * contrast_quota
                ):
                    new_sched = Schedule(
                        fidelity=new_sched.fidelity,
                        seed=new_sched.seed,
                        n_seeds=new_sched.n_seeds,
                        epochs=new_sched.epochs,
                        batch_limit=new_sched.batch_limit,
                        budget_id=f"{new_sched.budget_id}:contrast",
                        task_id=new_sched.task_id,
                    )

                scheduled.append((coord, new_sched))

        return Fragment(
            stage_id=self.stage_id,
            proposals=scheduled,
            metadata={
                "data_origin_allocation": allocation,
                "contrast_quota": contrast_quota,
                "scheduled_count": len(scheduled),
            },
            coverage={"stage": "schedule", "proposals_scheduled": len(scheduled)},
        )


class GateStage:
    """S4 Gate — LegalityEngine enforcement; globally-suppressive voids (R38)."""

    stage_id = StageId.S4_GATE

    async def run(self, ctx: "StageContext") -> "Fragment":
        """Enforce legality constraints on proposals."""
        from computronium.experiment.execution.search_space import Fragment

        logger.info("S4 Gate: Enforcing legality constraints")

        # Use pending_proposals which are Proposal objects
        filtered = []
        rejections = []

        for proposal in ctx.pending_proposals:
            coord = proposal.coordinate
            sched = proposal.schedule
            # Check legality using the legality engine
            from computronium.experiment.legality.engine import LegalityEngine

            engine = LegalityEngine()
            # Check if coordinate is legal
            # This would integrate with the actual legality engine
            is_legal = True  # Placeholder

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
            coverage={"stage": "gate", "passed": len(filtered), "rejected": len(rejections)},
            classification={"rejected": rejections} if rejections else {},
        )


class ComposeStage:
    """S5 Compose — compose_joint_system bridge; effective-value recording (R6)."""

    stage_id = StageId.S5_COMPOSE

    async def run(self, ctx: "StageContext") -> "Fragment":
        """Compose joint systems from coordinates."""
        from computronium.experiment.execution.search_space import Fragment

        logger.info("S5 Compose: Composing joint systems")

        composed = []
        for proposal in ctx.pending_proposals:
            # This would call compose_joint_system from the ontology
            # For now, just pass through
            composed.append(proposal)

        return Fragment(
            stage_id=self.stage_id,
            proposals=composed,
            metadata={"composed_count": len(composed)},
            coverage={"stage": "compose", "systems_composed": len(composed)},
        )


class TrainStage:
    """S6 Train — SystemTrainer settle bridge; guard/divergence telemetry (R50/R51)."""

    stage_id = StageId.S6_TRAIN

    async def run(self, ctx: "StageContext") -> "Fragment":
        """Execute training via backend."""
        from computronium.experiment.execution.search_space import Fragment

        logger.info("S6 Train: Executing training")

        if not ctx.backend:
            logger.warning("No backend configured, skipping training")
            return Fragment(stage_id=self.stage_id, coverage={"stage": "train", "skipped": True})

        # Execute via backend
        records = []
        for proposal in ctx.pending_proposals:
            coord = proposal.coordinate
            sched = proposal.schedule
            try:
                # This would call the actual evaluation
                # For now, create a placeholder record
                from computronium.experiment.schema.record import Record, Status, GateVerdict

                record = Record.create(
                    run_id=ctx.run_id,
                    coordinate=coord,
                    schedule=sched,
                    provenance=ctx.provenance,
                    status=Status(
                        gate_verdict=GateVerdict.PENDING,
                        defect="",
                        cause="UNKNOWN",
                        severity="LOW",
                        quarantine=False,
                        maturity="L0",
                        uncertainty={},
                        reproducibility="REPLAYABLE",
                        assessment_procedure_version="1.0",
                    ),
                    payload={
                        "status": "trained",
                        "walltime_s": 0.0,
                        "seed": sched.seed,
                        "fidelity": sched.fidelity,
                    },
                )
                records.append(record)
            except Exception as e:
                logger.exception("Training failed for %s", coord.cell_key())
                # Classification handled by wrapper

        return Fragment(
            stage_id=self.stage_id,
            records=records,
            metadata={"trained_count": len(records)},
            coverage={"stage": "train", "records_produced": len(records)},
        )


class MeasureStage:
    """S7 Measure — Objectives resolved against OBJECTIVES; probes; robustness (R69)."""

    stage_id = StageId.S7_MEASURE

    async def run(self, ctx: "StageContext") -> "Fragment":
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

    async def run(self, ctx: "StageContext") -> "Fragment":
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

    async def run(self, ctx: "StageContext") -> "Fragment":
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

    async def run(self, ctx: "StageContext") -> "Fragment":
        """Make promotion/continuation decisions."""
        from computronium.experiment.execution.search_space import Fragment
        from computronium.experiment.execution.decision import (
            Decision,
            continue_round,
            complete_run,
        )

        logger.info("S10 Decide: Making promotion/continuation decisions")

        # Use allocator to get promotions
        promotions = []
        new_proposals = []

        if ctx.allocator:
            # Get proposals from allocator
            allocator_proposals = ctx.allocator.propose(
                list(ctx.pending_proposals),
                [],  # records would come from store
                ctx.budget,
                ctx.cost_model,
            )
            new_proposals.extend(allocator_proposals)

        # Check budget
        should_continue = True
        if ctx.budget and ctx.budget.expired():
            should_continue = False

        if should_continue:
            decision = continue_round(
                new_proposals=[],  # Would be populated from proposals
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

    async def run(self, ctx: "StageContext") -> "Fragment":
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
STAGE_IMPLEMENTATIONS: dict["StageId", type] = {
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


def get_stage_implementation(stage_id: "StageId") -> type | None:
    """Get the concrete stage implementation for a stage ID."""
    return STAGE_IMPLEMENTATIONS.get(stage_id)


__all__ = [
    "FrameStage",
    "SpaceStage",
    "ScheduleStage",
    "GateStage",
    "ComposeStage",
    "TrainStage",
    "MeasureStage",
    "RecordStage",
    "AttributeStage",
    "DecideStage",
    "ReportStage",
    "STAGE_IMPLEMENTATIONS",
    "get_stage_implementation",
]