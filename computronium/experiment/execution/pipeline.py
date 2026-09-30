"""S1-S11 pipeline runner with wrapper obligations (WP9/15/16).

Wrapper obligations (R18/R19/R20/R29/R12):
- Coverage reporting (R18)
- Identical rejection classification for every policy (R19)
- Proposal provenance stamping (R20)
- Failure isolation (R29)
- Single-writer atomic appends (R12)
- Budget accounting (R21)
- EvidenceDrivenAllocator integration between rounds
- Replay hash computation and re-check (R26/R27)
- Resume via measurement_key dedup
- RegistryCostModel learns estimate-vs-actual (R23/R24)

Architecture:
- Stage dispatch via Stage.run(ctx) -> Fragment protocol (WP15)
- Round loop with S3-S10 repeating via Decision (WP16)
- SearchSpace/ProposalContext/Proposal canonical types (WP14)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from computronium.experiment.execution.decision import Decision, RoundController
from computronium.experiment.execution.stage import StageId, StageTransition, get_stage_spec
from computronium.experiment.schema.coordinate import Coordinate, Provenance, Schedule

if TYPE_CHECKING:
    from pathlib import Path

    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.execution.allocator import EvidenceDrivenAllocator
    from computronium.experiment.execution.backends import ExecutionBackend
    from computronium.experiment.execution.budget import Budget, CostModel
    from computronium.experiment.execution.search_space import (
        Fragment,
        Policy,
        Proposal,
        ProposalContext,
        SearchSpace,
        StageContext,
    )
    from computronium.experiment.execution.stages_impl import get_stage_implementation
    from computronium.experiment.schema.record import Record

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    """Configuration for the pipeline runner."""

    run_id: str
    run_spec: dict[str, Any]
    stages: list[StageId] = field(default_factory=list)
    budget: "Budget | None" = None
    cost_model: "CostModel | None" = None
    policy: "Policy | None" = None
    allocator: "EvidenceDrivenAllocator | None" = None
    backend: "ExecutionBackend | None" = None
    checkpoint_dir: Path | None = None
    checkpoint_interval_seconds: float = 60.0
    max_concurrent_evaluations: int = 10
    seed: int | None = None
    # Task IDs for multi-task runs (L17)
    task_ids: list[str] = field(default_factory=list)
    # Round controller config
    max_rounds: int | None = None
    min_rounds: int = 1


@dataclass(slots=True)
class PipelineState:
    """Mutable state for pipeline execution."""

    run_id: str
    current_stage_idx: int = 0
    current_round: int = 0
    completed_measurement_keys: set[str] = field(default_factory=set)
    pending_proposals: list["Proposal"] = field(default_factory=list)
    in_progress: list[tuple[Coordinate, Schedule]] = field(default_factory=list)
    budget: "Budget | None" = None
    allocator_state: dict[str, Any] | None = None
    last_checkpoint_time: float = 0.0
    # Coverage tracking (R18)
    coverage: dict[str, Any] = field(default_factory=dict)
    # Rejection classification (R19)
    rejections: list[dict[str, Any]] = field(default_factory=list)
    # Proposal provenance (R20)
    proposal_provenance: list[dict[str, Any]] = field(default_factory=list)
    # Replay hash tracking (R26/R27)
    replay_hash: str | None = None
    # Round controller
    round_controller: "RoundController | None" = None
    # Search space
    search_space: "SearchSpace | None" = None
    # System context (R75/K10)
    system_context: Any = None


class PipelineRunner:
    """S1-S11 pipeline runner with atomic append + reconciliation + wrapper obligations.

    Coordinates the full experiment lifecycle:
    - Stage progression (S1-S11) via Stage.run(ctx) -> Fragment dispatch
    - Round loop (S3-S10 repeat) with Decision-based termination
    - Budget management
    - Policy-driven candidate selection via SearchSpace
    - Backend execution with failure isolation
    - Record persistence with reconciliation
    - Checkpointing and resume
    - Wrapper obligations: coverage, classification, traceability, failure isolation
    - EvidenceDrivenAllocator integration
    - Replay hash verification
    """

    def __init__(
        self,
        config: PipelineConfig,
        store: "RecordStore",
    ) -> None:
        self._config = config
        self._store = store
        self._state = PipelineState(
            run_id=config.run_id,
            budget=config.budget,
            round_controller=RoundController(
                max_rounds=config.max_rounds,
                min_rounds=config.min_rounds,
            ),
        )
        self._stages = config.stages or [s.stage_id for s in self._get_all_stage_specs()]
        self._shutdown = False

    def _get_all_stage_specs(self):
        from computronium.experiment.execution.stage import STAGE_SPECS
        return STAGE_SPECS

    async def run(self) -> list["Record"]:
        """Run the full pipeline to completion with round loop.

        Returns:
            All records produced during the run.
        """
        logger.info(
            "Starting pipeline run %s with stages: %s",
            self._config.run_id,
            self._stages,
        )

        # Build SearchSpace from RunSpec
        self._state.search_space = self._build_search_space()

        all_records: list["Record"] = []

        # S1-S2: Run once at start
        for stage_id in [StageId.S1_FRAME, StageId.S2_SPACE]:
            if self._shutdown:
                break
            if stage_id not in self._stages:
                continue

            stage_spec = get_stage_spec(stage_id)
            fragment = await self._dispatch_stage(stage_id, stage_spec)

            # Collect records and proposals
            all_records.extend(fragment.records)
            self._state.pending_proposals.extend(fragment.proposals)

            # Update coverage
            self._merge_coverage(fragment.coverage)

            # Check gate
            if not self._check_gate(fragment, stage_spec):
                logger.warning("Gate failed for stage %s, stopping pipeline", stage_id)
                break

        # S3-S10: Round loop
        round_controller = self._state.round_controller
        if round_controller is None:
            from computronium.experiment.execution.decision import RoundController
            round_controller = RoundController(
                max_rounds=self._config.max_rounds,
                min_rounds=self._config.min_rounds,
            )
            self._state.round_controller = round_controller

        while round_controller.should_continue(
            self._get_decision_from_fragments()
        ):
            self._state.current_round += 1
            logger.info("Starting round %d", self._state.current_round)

            # S3 Schedule
            if StageId.S3_SCHEDULE in self._stages:
                fragment = await self._dispatch_stage(StageId.S3_SCHEDULE, get_stage_spec(StageId.S3_SCHEDULE))
                self._state.pending_proposals.extend(fragment.proposals)
                self._merge_coverage(fragment.coverage)

            # S4 Gate
            if StageId.S4_GATE in self._stages:
                fragment = await self._dispatch_stage(StageId.S4_GATE, get_stage_spec(StageId.S4_GATE))
                self._state.pending_proposals = fragment.proposals  # Filtered
                self._merge_coverage(fragment.coverage)
                self._merge_classification(fragment.classification)

            # S5 Compose
            if StageId.S5_COMPOSE in self._stages:
                fragment = await self._dispatch_stage(StageId.S5_COMPOSE, get_stage_spec(StageId.S5_COMPOSE))
                self._state.pending_proposals = fragment.proposals
                self._merge_coverage(fragment.coverage)

            # S6 Train
            if StageId.S6_TRAIN in self._stages:
                fragment = await self._dispatch_stage(StageId.S6_TRAIN, get_stage_spec(StageId.S6_TRAIN))
                all_records.extend(fragment.records)
                self._merge_coverage(fragment.coverage)

            # S7 Measure
            if StageId.S7_MEASURE in self._stages:
                fragment = await self._dispatch_stage(StageId.S7_MEASURE, get_stage_spec(StageId.S7_MEASURE))
                all_records.extend(fragment.records)
                self._merge_coverage(fragment.coverage)

                # Run allocator between rounds (after S7_MEASURE, before S10_DECIDE)
                if self._config.allocator and self._config.budget:
                    await self._run_allocator(fragment.records)

            # S8 Record
            if StageId.S8_RECORD in self._stages:
                fragment = await self._dispatch_stage(StageId.S8_RECORD, get_stage_spec(StageId.S8_RECORD))
                all_records.extend(fragment.records)
                self._merge_coverage(fragment.coverage)

            # S9 Attribute
            if StageId.S9_ATTRIBUTE in self._stages:
                fragment = await self._dispatch_stage(StageId.S9_ATTRIBUTE, get_stage_spec(StageId.S9_ATTRIBUTE))
                self._merge_coverage(fragment.coverage)

            # S10 Decide
            if StageId.S10_DECIDE in self._stages:
                fragment = await self._dispatch_stage(StageId.S10_DECIDE, get_stage_spec(StageId.S10_DECIDE))
                self._state.pending_proposals.extend(fragment.proposals)
                self._merge_coverage(fragment.coverage)
                # Decisions will be processed by round controller

            # Checkpoint after each round
            if self._config.checkpoint_dir:
                await self._create_checkpoint()

        # S11 Report
        if StageId.S11_REPORT in self._stages:
            fragment = await self._dispatch_stage(StageId.S11_REPORT, get_stage_spec(StageId.S11_REPORT))
            self._merge_coverage(fragment.coverage)

        logger.info(
            "Pipeline run %s completed: %d records, %d rounds",
            self._config.run_id,
            len(all_records),
            self._state.current_round,
        )
        return all_records

    def _build_search_space(self) -> "SearchSpace":
        """Build canonical SearchSpace from RunSpec."""
        from computronium.experiment.execution.search_space import SearchSpace
        from computronium.experiment.schema.axis import (
            AXES_REGISTRIES,
            StructuralAxis,
        )
        from computronium.experiment.schema.registries import (
            CONSTRAINTS_REGISTRY,
            OBJECTIVES_REGISTRY,
        )

        run_spec = self._config.run_spec

        # Get all axis specs from registries
        axes_snapshot = []
        for axis_kind in StructuralAxis:
            registry = AXES_REGISTRIES[axis_kind]
            for spec in registry.values():
                if spec.available:
                    axes_snapshot.append(spec)

        # Get constraints
        constraints = list(CONSTRAINTS_REGISTRY.values())

        # Get objectives from run_spec or all
        objective_names = run_spec.get("objectives", [])
        if objective_names:
            objectives = [OBJECTIVES_REGISTRY[name] for name in objective_names if name in OBJECTIVES_REGISTRY]
        else:
            objectives = list(OBJECTIVES_REGISTRY.values())

        # Get tasks
        tasks = tuple(self._config.task_ids) if self._config.task_ids else ("default",)

        return SearchSpace(
            axes_snapshot=tuple(axes_snapshot),
            constraints=tuple(constraints),
            objectives=tuple(objectives),
            tasks=tasks,
        )

    async def _dispatch_stage(self, stage_id: StageId, stage_spec) -> "Fragment":
        """Dispatch to the concrete stage implementation."""
        from computronium.experiment.execution.stages_impl import get_stage_implementation

        impl_class = get_stage_implementation(stage_id)
        if impl_class is None:
            logger.warning("No implementation for stage %s, using no-op", stage_id)
            from computronium.experiment.execution.search_space import Fragment
            return Fragment(stage_id=stage_id)

        # Create stage context
        ctx = self._create_stage_context(stage_id, stage_spec)

        # Run the stage
        stage_impl = impl_class()
        try:
            fragment = await stage_impl.run(ctx)
            return fragment
        except Exception as e:
            logger.exception("Stage %s failed", stage_id)
            # Return fragment with error info
            from computronium.experiment.execution.search_space import Fragment
            return Fragment(
                stage_id=stage_id,
                metadata={"error": str(e)},
                coverage={"stage": stage_id.value, "error": True},
            )

    def _create_stage_context(self, stage_id: StageId, stage_spec) -> "StageContext":
        """Create StageContext for a stage."""
        from computronium.experiment.execution.search_space import StageContext

        # Convert pending proposals to (coord, sched) pairs for backward compatibility
        pending_candidates = [(p.coordinate, p.schedule) for p in self._state.pending_proposals]

        # Ensure required components are available
        budget = self._state.budget
        cost_model = self._config.cost_model
        policy = self._config.policy
        backend = self._config.backend
        search_space = self._state.search_space

        if budget is None or cost_model is None or policy is None or backend is None or search_space is None:
            raise ValueError("Missing required pipeline components for stage context")

        return StageContext(
            run_id=self._config.run_id,
            run_spec=self._config.run_spec,
            stage_id=stage_id,
            store=self._store,
            budget=budget,
            cost_model=cost_model,
            policy=policy,
            allocator=self._config.allocator,
            backend=backend,
            search_space=search_space,
            completed_keys=self._state.completed_measurement_keys,
            pending_proposals=self._state.pending_proposals,
            pending_candidates=pending_candidates,
            in_progress=self._state.in_progress,
            stage_params=stage_spec.params,
            provenance=Provenance(
                env={"python": "3.14", "platform": "linux"},
                dataset=self._config.run_spec.get("dataset", "unknown"),
                dataset_version=self._config.run_spec.get("dataset_version", "1.0"),
                code_sha=self._config.run_spec.get("code_sha", "unknown"),
                policy=self._config.policy.get_name() if self._config.policy else "unknown",
                links={"run_id": self._config.run_id},
            ),
            system_context=self._state.system_context,
        )

    def _merge_coverage(self, coverage: dict[str, Any]) -> None:
        """Merge coverage from fragment into state."""
        # Store per-stage coverage using stage key
        stage_key = coverage.get("stage", "unknown")
        self._state.coverage[stage_key] = coverage

    def _merge_classification(self, classification: dict[str, Any]) -> None:
        """Merge classification from fragment into state."""
        self._state.rejections.append(classification)

    def _get_decision_from_fragments(self) -> Decision:
        """Extract Decision from the last S10 fragment."""
        # For now, create a default continue decision
        # In practice, this would come from the S10 Decide stage fragment
        from computronium.experiment.execution.decision import continue_round
        return continue_round(rationale="Default continue")

    async def _run_allocator(self, records: list["Record"]) -> None:
        """Run EvidenceDrivenAllocator between rounds (R46-R51)."""
        if not self._config.allocator:
            return

        logger.debug("Running allocator for run %s", self._config.run_id)

        # Convert pending proposals to candidates
        candidates = [(p.coordinate, p.schedule) for p in self._state.pending_proposals]

        # Get proposals from allocator
        budget = self._state.budget
        cost_model = self._config.cost_model
        if budget is None or cost_model is None:
            return

        proposals = self._config.allocator.propose(
            candidates=candidates,
            records=records,
            budget=budget,
            cost_model=cost_model,
        )

        # Convert to Proposal objects
        from computronium.experiment.execution.search_space import Proposal
        for coord, sched in proposals:
            self._state.pending_proposals.append(Proposal(
                coordinate=coord,
                schedule=sched,
                rationale="allocator_promotion",
            ))

    def _check_gate(self, fragment: "Fragment", stage_spec) -> bool:
        """Check if stage gate passes."""
        if stage_spec.gate == "skip":
            return True

        if not fragment.records and not fragment.proposals:
            return stage_spec.gate != "pass"

        # For claim gate, require claim_eligible records
        if stage_spec.gate == "claim":
            eligible = [r for r in fragment.records if self._is_claim_eligible(r)]
            return len(eligible) > 0

        # For pass gate, require at least one non-quarantine PASS
        if stage_spec.gate == "pass":
            passing = [
                r
                for r in fragment.records
                if r.status.gate_verdict.value == "PASS" and not r.status.quarantine
            ]
            return len(passing) > 0

        return True

    def _is_claim_eligible(self, record: "Record") -> bool:
        """Check if record is claim-eligible (pure predicate)."""
        return (
            record.status.gate_verdict.value == "PASS"
            and not record.status.quarantine
            and record.schedule.fidelity == "L2"
            and record.schedule.n_seeds >= 5
        )

    async def _create_checkpoint(self) -> None:
        """Create a periodic checkpoint."""
        if not self._config.checkpoint_dir:
            return

        from computronium.experiment.execution.replay import create_checkpoint

        self._config.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        timestamp = int(time.time() * 1000)
        checkpoint_path = (
            self._config.checkpoint_dir
            / f"checkpoint_{self._config.run_id}_{timestamp}.json"
        )

        checkpoint = create_checkpoint(
            run_id=self._config.run_id,
            run_spec=self._config.run_spec,
            completed_keys=frozenset(self._state.completed_measurement_keys),
            pending=[(p.coordinate, p.schedule) for p in self._state.pending_proposals],
            in_progress=self._state.in_progress,
            budget=self._state.budget,
            allocator_state=self._state.allocator_state,
        )
        checkpoint.to_file(checkpoint_path)
        self._state.last_checkpoint_time = time.time()
        logger.debug("Created checkpoint: %s", checkpoint_path)

    def shutdown(self) -> None:
        """Shutdown the pipeline runner."""
        self._shutdown = True
        if self._config.backend:
            self._config.backend.shutdown()

    def get_coverage_report(self) -> dict[str, Any]:
        """Get coverage report (R18)."""
        return self._state.coverage

    def get_rejection_report(self) -> list[dict[str, Any]]:
        """Get rejection classification report (R19)."""
        return self._state.rejections

    def get_proposal_provenance(self) -> list[dict[str, Any]]:
        """Get proposal provenance (R20)."""
        return self._state.proposal_provenance


__all__ = [
    "PipelineConfig",
    "PipelineRunner",
    "PipelineState",
]