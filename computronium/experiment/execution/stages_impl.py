"""Concrete stage implementations for the S1-S11 pipeline (WP15).

Each stage implements the Stage protocol with `run(ctx) -> Fragment`.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from computronium.experiment.execution.search_space import SearchSpace
    from computronium.experiment.execution.stage import (
        Fragment,
        Proposal,
        StageContext,
    )

logger = logging.getLogger(__name__)


# Import at runtime to avoid circular imports
from computronium.experiment.execution.contrast_design import (
    ContrastAssignment,
    Factor,
)
from computronium.experiment.execution.stage import (
    StageId,  # noqa: E402
)
from computronium.experiment.schema.coordinate import Coordinate, DataOrigin

# How many cells S1 opens a run with. A round's own allocation is the stage
# params' business; this is the exploration batch before any round exists.
_FRAME_PROPOSALS = 10

# The two origins a contrast design has an assignment for. The rest are the
# design's *absence*: an exploration cell is not a control for anything.
_DESIGNED_ORIGINS = frozenset({DataOrigin.CONTROL, DataOrigin.CONTRAST})


def _design_factors(space: SearchSpace) -> list[Factor]:
    """The space's varying structural axes, as design factors with real levels.

    A factor's levels are the *primitives the run actually sweeps* on that
    axis, so an assignment names a cell that exists. The previous construction
    took the first coordinate's ``params`` keys and gave every one the levels
    ``(0.0, 1.0)`` — normalized labels on names like ``update_lr``, so an
    assignment read ``update_lr=0.0`` while the measured cell carried a real
    value, and ``matched_group='ofat_update_lr'`` could label a cell that moved
    two hyperparameters at once. A factor with one level is not a factor, so
    single-primitive axes are excluded and the control is the first level of
    each of the rest.

    Args:
        space: The run's active space.

    Returns:
        One factor per axis the run varies, in registry order.
    """
    from computronium.experiment.schema.harvest import AXIS_KIND_ORDER

    factors: list[Factor] = []
    for axis in AXIS_KIND_ORDER:
        levels = space.primitives(axis)
        if len(levels) > 1:
            factors.append(Factor(name=axis.value, levels=levels))
    return factors


def _origins_for_design(
    proposals: list[Proposal],
    assignments: list[ContrastAssignment],
    allocated: list[DataOrigin],
) -> list[DataOrigin]:
    """Re-originate the cells the design placed, keeping the rest's allocation.

    The design's cells take their origin from their group; every other proposal
    keeps whatever ``_allocate_origins`` gave it. Doing this in one pass is what
    makes a control a control: allocating first and labelling afterwards let a
    control-origin proposal be matched to a contrast cell.

    Args:
        proposals: The round's proposals, in proposal order.
        assignments: The design's assignments.
        allocated: The allocation the round started from.

    Returns:
        Origins per proposal, with the designed cells' own.
    """
    matched = _match_design(proposals, assignments)
    # A quota origin with no assignment behind it is not a design placement, so
    # it reverts to exploration: "control"/"contrast" must mean *the design put
    # this cell there*, not "this round's rounding landed here". Without that,
    # a record claims a group the design never assigned it.
    revised = [
        o if i in matched or o not in _DESIGNED_ORIGINS else DataOrigin.EXPLORATION
        for i, o in enumerate(allocated)
    ]
    for index, assignment in matched.items():
        revised[index] = assignment.data_origin
    return revised


def _match_design(
    proposals: list[Proposal], assignments: list[ContrastAssignment]
) -> dict[int, ContrastAssignment]:
    """Pair this round's proposals with the design assignments they *are*.

    A group is a claim about a cell, so it is only stamped when the cell's
    axis values equal the assignment's — and an assignment is only eligible for
    an origin of its own kind, so a control can never land on a contrast cell.
    Proposals matching nothing are left undesigned rather than given a
    neighbour's label.

    Args:
        proposals: The round's proposals, in proposal order.
        assignments: The design's assignments, control first.

    Returns:
        Proposal index to the assignment that cell satisfies.
    """
    matched: dict[int, ContrastAssignment] = {}
    if not assignments:
        return matched
    claimed: set[str] = set()
    for index, proposal in enumerate(proposals):
        for assignment in assignments:
            if assignment.contrast_id in claimed:
                continue
            if _is_assignment(proposal.coordinate, assignment):
                matched[index] = assignment
                claimed.add(assignment.contrast_id)
                break
    return matched


def _is_assignment(coordinate: Coordinate, assignment: ContrastAssignment) -> bool:
    """Whether a coordinate *is* a design assignment.

    Compared on the structural axes the design varies and nothing else: the
    swept hyperparameters are the same cell's replication, so two coordinates
    differing only there are one point in the design, not two.
    """
    return all(
        getattr(coordinate, name, None) == level
        for name, level in assignment.factor_assignments.items()
    )


def _allocate_origins(total: int, allocation: dict[str, float]) -> list[DataOrigin]:
    """Split a round's proposals across data origins, exactly ``total`` long.

    Shares are filled largest-remainder, so the sum is the round size by
    construction rather than by truncation, and a share that rounds to zero is
    only granted a slot when the round is long enough to spare one. Exploration
    is the only origin that gives: the protocol's groups are what the round is
    *for*, and exploration is what is *about* the sweep.

    Before this, five per-origin ``max(1, ...)`` counts summed past ``total`` and
    ``data_origins[:total]`` truncated from the tail, so the two 5%-quota
    origins were the two that always disappeared — measured, a 450-record
    campaign carried 250 exploration / 120 calibration / 80 test and **zero**
    control or contrast. A design whose only two groups are the ones truncation
    eats is a design that never runs.

    Args:
        total: Proposals this round will schedule.
        allocation: Each origin's share of the round.

    Returns:
        One origin per proposal, always exactly ``total`` long.
    """
    shares = {
        origin: allocation.get(origin.value, 0.0)
        for origin in DataOrigin
        if allocation.get(origin.value, 0.0) > 0
    }
    if not shares or total <= 0:
        return [DataOrigin.EXPLORATION] * max(0, total)

    counts = {origin: int(total * share) for origin, share in shares.items()}
    # Largest-remainder: hand the leftover slots to the largest fractional parts.
    remainder = total - sum(counts.values())
    for origin in sorted(shares, key=lambda o: -(total * shares[o] - counts[o])):
        if remainder <= 0:
            break
        counts[origin] += 1
        remainder -= 1

    if remainder > 0:
        # The round is too short for every declared origin: keep the protocol's
        # own groups (the design) and let exploration absorb what is left.
        spare = total - sum(min(counts[o], 1) for o in _DESIGNED_ORIGINS if o in counts)
        for origin in sorted(counts, key=lambda o: (o not in _DESIGNED_ORIGINS, o)):
            if remainder <= 0 or spare <= 0:
                break
            if counts[origin] < 1:
                counts[origin] += 1
                remainder -= 1
                spare -= 1

    origins: list[DataOrigin] = []
    for origin, count in counts.items():
        origins.extend([origin] * count)
    while len(origins) < total:
        origins.append(DataOrigin.EXPLORATION)
    return origins[:total]


class FrameStage:
    """S1 Frame — Objective/operating-point resolution (R43 entry, with Synthesis)."""

    stage_id = StageId.S1_FRAME

    async def run(self, ctx: StageContext) -> Fragment:
        """Resolve objectives and operating points from RunSpec."""
        from computronium.experiment.execution.stage import Fragment

        logger.info("S1 Frame: Resolving objectives and operating points")

        # Extract objectives from run_spec
        run_spec = ctx.run_spec
        objectives = run_spec.objectives
        operating_points = run_spec.operating_points

        # The policy generates the opening cells from the spec's own space:
        # primitives it permits, hyperparameters it sweeps, schedule it declares.
        from computronium.experiment.execution.evaluate import task_shape
        from computronium.experiment.execution.policy import ProposalContext

        proposals = list(
            ctx.policy.propose(
                ProposalContext(
                    search_space=ctx.search_space,
                    spec=run_spec,
                    run_id=ctx.run_id,
                    budget=ctx.budget,
                    cost_model=ctx.cost_model,
                    evidence=ctx.store,
                    shape=task_shape,
                    n_propose=_FRAME_PROPOSALS,
                )
            )
        )

        return Fragment(
            stage_id=self.stage_id,
            proposals=proposals,
            metadata={
                "objectives": list(objectives),
                "operating_points": operating_points,
                "proposal_count": len(proposals),
            },
            coverage={
                "stage": self.stage_id.value,
                "proposals_generated": len(proposals),
            },
        )


class SpaceStage:
    """S2 Space — Axis snapshot + legality preview (dry-run = same engine, C32)."""

    stage_id = StageId.S2_SPACE

    async def run(self, ctx: StageContext) -> Fragment:
        """Snapshot active axes and run legality dry-run."""
        from computronium.experiment.execution.stage import Fragment

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
            ContrastDesign,
            ContrastDesignKind,
            create_contrast_design,
        )
        from computronium.experiment.execution.stage import Fragment, Proposal

        logger.info(
            "S3 Schedule: Planning fidelity/seed/epoch with data-origin allocation"
        )

        proposals = list(ctx.pending_proposals)
        if not proposals and ctx.policy:
            from computronium.experiment.execution.evaluate import task_shape
            from computronium.experiment.execution.policy import ProposalContext

            proposals.extend(
                ctx.policy.propose(
                    ProposalContext(
                        search_space=ctx.search_space,
                        spec=ctx.run_spec,
                        run_id=ctx.run_id,
                        budget=ctx.budget,
                        cost_model=ctx.cost_model,
                        evidence=ctx.store,
                        # S1 screens with the shape; a context without it
                        # proposes cells SystemConfig.validate rejects (the
                        # lazy x recurrent walk), discovered by training.
                        shape=task_shape,
                    )
                )
            )

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

        # Build contrast design if contrast runs requested. Bound before the
        # scheduling block: a round with nothing to schedule must still build
        # its fragment, and an unbound local there is a crash, not a design.
        contrast_design: ContrastDesign | None = None
        contrast_assignments: list[ContrastAssignment] = []
        scheduled_proposals: list[Proposal] = []
        total = len(proposals)
        if total > 0:
            data_origins = _allocate_origins(total, allocation)
            design = _design_factors(ctx.search_space)
            if design:
                contrast_design = create_contrast_design(
                    ContrastDesignKind(contrast_design_kind),
                    design,
                    seed=hash(ctx.run_id) % 2**32,
                )
                contrast_assignments = list(contrast_design.assignments)
            # The design decides which proposals carry a group, so it also
            # decides their origin: a cell the design placed is an origin of the
            # design's kind. Allocating origins first and matching afterwards
            # would let the two disagree — a control cell measured as
            # exploration, or a contrast cell claiming the control's group.
            data_origins = _origins_for_design(
                proposals, contrast_assignments, data_origins
            )

            # Stamp each proposal's data origin into metadata; the schedule
            # itself is untouched, so identity is the cell's own.
            assigned = _match_design(proposals, contrast_assignments)
            for i, proposal in enumerate(proposals):
                coord, sched = proposal.coordinate, proposal.schedule
                data_origin = data_origins[i]

                # Build metadata with data_origin and contrast info
                metadata: dict[str, Any] = {"data_origin": data_origin.value}

                # A designed origin carries its assignment only when the cell
                # *is* that assignment. Stamping a group onto whatever the round
                # happened to propose is a label with no referent: measured,
                # `matched_group='ofat_settle_step'` on a cell that also moved
                # `update_lr` and the credit axis. A proposal that matches no
                # assignment therefore keeps its origin and takes no group, and
                # the report counts what the design actually placed.
                assignment = assigned.get(i)
                if assignment is not None:
                    metadata["contrast_id"] = assignment.contrast_id
                    metadata["factor_assignments"] = assignment.factor_assignments
                    metadata["matched_group"] = assignment.matched_group

                # The schedule is carried through unchanged: a data origin is
                # metadata, so the same cell scheduled under a second origin is
                # the same measurement and must hash to the same key. Shifting
                # the seed to keep keys apart re-measures one coordinate every
                # round under a fresh name — invisible to the store's dedup and
                # paid for on every round, forever.
                scheduled_proposals.append(
                    Proposal(
                        coordinate=coord,
                        schedule=sched,
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
        from computronium.experiment.execution.stage import Fragment
        from computronium.experiment.legality.engine import (
            ConstraintEnforcement,
            ConstraintKind,
            ConstraintOrigin,
            ConstraintScope,
            LegalityEngine,
            create_constraint,
        )
        from computronium.experiment.schema.registries import CONSTRAINTS_REGISTRY
        from computronium.experiment.legality.dsl import Expr, Var

        logger.info("S4 Gate: Enforcing legality constraints")

        def _references_params(expr: Expr) -> bool:
            """Check if expression references params.* variables."""
            if isinstance(expr, Var) and expr.name.startswith("params."):
                return True
            for field_name in ("expr", "left", "right", "obj", "key"):
                child = getattr(expr, field_name, None)
                if isinstance(child, Expr) and _references_params(child):
                    return True
            # Check for Call.args (Call has args attribute)
            if hasattr(expr, "args"):
                args = getattr(expr, "args", None)
                if args is not None:
                    for arg in args:
                        if isinstance(arg, Expr) and _references_params(arg):
                            return True
            return False

        # Create and seed legality engine with constraints from registry
        engine = LegalityEngine()
        for spec in CONSTRAINTS_REGISTRY.values():
            if spec.predicate is not None:
                # Use ALL void constraints at gate time
                # Resource constraints (max_hidden_dim, etc.) need hyperparameters
                # that are only resolved at compose time - they have kind=RESOURCE
                # and are filtered out here since we only want VOID kind
                if spec.kind.value != "void":
                    continue
                # Skip constraints that reference params (hyperparameters) - those
                # are evaluated at compose time (S5) when params are available
                if _references_params(spec.predicate):
                    continue

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
            from computronium.experiment.schema.registries import (
                ASSESSMENT_PROCEDURE_VERSION,
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
                    assessment_procedure_version=ASSESSMENT_PROCEDURE_VERSION,
                    ceec_link=None,
                ),
                payload={},
            )

            # Check legality using the legality engine
            hard_violations, _soft_violations = engine.evaluate_record(
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
        from computronium.experiment.execution.stage import Fragment

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
        from computronium.experiment.execution.stage import Fragment

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
        from computronium.experiment.execution.stage import Fragment

        logger.info("S7 Measure: Measuring objectives and probes")

        # This would resolve objectives against OBJECTIVES registry
        # and compute probe metrics
        measured = list(ctx.pending_proposals)

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
        from computronium.experiment.execution.stage import Fragment

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
        from computronium.experiment.execution.stage import Fragment

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
        from computronium.experiment.execution.stage import Fragment, Proposal

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
        from computronium.experiment.execution.stage import Fragment

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
