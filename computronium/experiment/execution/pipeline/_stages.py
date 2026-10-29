"""Stage dispatch, batch execution and record persistence."""

from __future__ import annotations

import logging
import sys
import time
from typing import TYPE_CHECKING, Any

from computronium.experiment.execution.backends import Failure, Success
from computronium.experiment.execution.events import STAGE_ACTIONS, publish_event
from computronium.experiment.execution.stage import (
    Proposal,
    StageId,
    get_stage_spec,
)
from computronium.experiment.schema.coordinate import (
    Coordinate,
    Provenance,
    Schedule,
)

from ._base import _PipelineBase, tqdm
from ._types import _ROUND_STAGE_ORDER, _provenance_for, _resolve_tasks

if TYPE_CHECKING:
    from computronium.experiment.execution.backends import (
        EvaluationResult,
    )
    from computronium.experiment.execution.decision import Decision
    from computronium.experiment.execution.stage import (
        Fragment,
        StageContext,
    )
    from computronium.experiment.kernel.search_space import SearchSpace
    from computronium.experiment.schema.record import Record

logger = logging.getLogger(__name__)


class _StageMixin(_PipelineBase):
    def _get_all_stage_specs(self):
        from computronium.experiment.execution.stage import STAGE_SPECS

        return STAGE_SPECS

    def _build_search_space(self) -> SearchSpace:
        """Build the run's active space from its spec (TODO46 §3.3)."""
        from computronium.experiment.kernel.search_space import (
            search_space_from_spec,
        )

        return search_space_from_spec(
            self._config.run_spec, tasks=_resolve_tasks(self._config)
        )

    def _announce_stage(self, stage_id: StageId, fragment: Fragment) -> None:
        """Tell the live rail what the stage just did."""
        action = STAGE_ACTIONS.get(stage_id.value, stage_id.value)
        error = fragment.metadata.get("error")
        if error:
            publish_event(
                stage_id.value,
                f"could not {action}: {error}",
                level="error",
                run_id=self._config.run_id,
            )
            return

        counts = []
        if fragment.proposals:
            counts.append(f"{len(fragment.proposals)} proposals")
        if fragment.records:
            counts.append(f"{len(fragment.records)} records")
        refused = fragment.metadata.get("rejected_count", 0)
        refused = int(refused) if isinstance(refused, int) else 0
        if refused:
            counts.append(f"{refused} refused")
        detail = ", ".join(counts)
        publish_event(
            stage_id.value,
            f"{action}{f': {detail}' if detail else ''}",
            run_id=self._config.run_id,
            detail={
                "proposals": len(fragment.proposals),
                "records": len(fragment.records),
                # What the gate threw away: the flow view needs it, and the
                # live rail is the only place it is said while it happens.
                "refused": refused,
            },
        )

    def _create_stage_context(self, stage_id: StageId, stage_spec) -> StageContext:
        """Create StageContext for a stage."""
        from computronium.experiment.execution.stage import StageContext

        # Ensure required components are available
        deadline = self._state.deadline
        policy = self._config.policy
        backend = self._config.backend
        search_space = self._state.search_space

        if (
            deadline is None
            or policy is None
            or backend is None
            or search_space is None
        ):
            raise ValueError("Missing required pipeline components for stage context")

        # Use environment snapshot from system context (WP19)
        system_context = self._state.system_context
        if system_context is None:
            raise ValueError("SystemContext not initialized")
        env_dict = system_context.environment.to_provenance_dict()

        return StageContext(
            run_id=self._config.run_id,
            run_spec=self._config.run_spec,
            stage_id=stage_id,
            store=self._store,
            deadline=deadline,
            deadline_enforcer=self._state.deadline_enforcer,
            policy=policy,
            allocator=self._config.allocator,
            backend=backend,
            search_space=search_space,
            completed_keys=self._state.completed_measurement_keys,
            pending_proposals=self._state.pending_proposals,
            in_progress=self._state.in_progress,
            stage_params=stage_spec.params,
            provenance=self._provenance(env_dict),
            system_context=system_context,
            batch_sizer=self._state.batch_sizer,
            cell_stream=self._state.cell_stream,
            allocator_promotions=self._state.allocator_promotions,
        )

    def _provenance(self, env_dict: dict[str, Any]) -> Provenance:
        """The run's provenance: environment plus the spec's own declarations.

        The dataset and code SHA were resolved once in ``__init__`` from the
        spec (or the task/repo), so every stage's records carry the same
        contract-satisfying values.
        """
        spec = self._config.run_spec
        return Provenance(
            env=env_dict,
            dataset=self._dataset,
            dataset_version=spec.dataset_version,
            code_sha=self._code_sha,
            policy=self._config.policy.get_name() if self._config.policy else "unknown",
            links={"run_id": self._config.run_id},
        )

    def _merge_coverage(self, coverage: dict[str, Any]) -> None:
        """Merge coverage from fragment into state."""
        # Store per-stage coverage using stage key
        stage_key = coverage.get("stage", "unknown")
        self._state.coverage[stage_key] = coverage

    def _merge_classification(self, classification: dict[str, Any]) -> None:
        """Merge classification from fragment into state."""
        self._state.rejections.append(classification)

    def _classify_rejection(
        self,
        coordinate: Coordinate,
        schedule: Schedule,
        cause: str,
        message: str,
    ) -> None:
        """Classify a rejection identically for every policy (R19).

        Args:
            coordinate: The experiment coordinate that was rejected
            schedule: The execution schedule
            cause: Failure cause classification
            message: Human-readable error message
        """
        classification = {
            "stage": "train",
            "cell_key": coordinate.cell_key(),
            "coordinate": coordinate.to_dict(),
            "schedule": schedule.to_dict(),
            "cause": cause,
            "message": message,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }
        self._state.rejections.append(classification)

    def _get_decision_from_fragments(self) -> Decision:
        """The decision S10 last reached, or continue while it has said nothing.

        S10 states a real termination ("budget exhausted", a promotion gate that
        closed) and this read it back as a constant CONTINUE, so the run's only
        stopping condition was the round limit and the exhaustion heuristic —
        every reason a stage gave for stopping was a comment in a fragment.
        """
        from computronium.experiment.execution.decision import continue_round

        decision = self._state.last_decision
        return (
            decision
            if decision is not None
            else continue_round(rationale="No stage has decided yet")
        )

    def _build_allocator_candidates(
        self, search_space: SearchSpace
    ) -> list[tuple[Coordinate, Schedule]]:
        """Build candidate coordinates for allocator to consider for promotion.

        Generates structural coordinates at the next fidelity level for cells
        that have shown promise at lower fidelity.
        """
        from computronium.experiment.kernel.evaluate import task_shape
        from computronium.experiment.kernel.search_space import iter_candidates

        candidates = []
        # Generate candidates at explore fidelity (L0/L1) for promotion to exploit fidelity
        spec = self._config.run_spec
        # We need to generate candidates without modifying the original spec
        # Create a temporary spec-like object or use iter_candidates directly
        for coord, sched in iter_candidates(
            spec,
            search_space,
            deadline=self._state.deadline,
            shape=task_shape,
            max_scan=1000,  # Limit scan for allocator candidates
            check_composable=False,  # Skip composability for speed at allocation time
        ):
            # Only consider cells at explore fidelity for promotion
            if sched.fidelity in {"L0", "L1"}:
                # Create a new schedule at the next fidelity
                next_fidelity = "L1" if sched.fidelity == "L0" else "L2"
                from computronium.experiment.schema.coordinate import Schedule

                promo_sched = Schedule(
                    fidelity=next_fidelity,
                    seed=sched.seed,
                    n_seeds=sched.n_seeds,
                    epochs=sched.epochs * 2,  # More epochs at higher fidelity
                    batch_limit=sched.batch_limit,
                    budget_id="promotion",
                    task_id=sched.task_id,
                    param_budget=sched.param_budget,
                    device=sched.device,
                    deterministic=sched.deterministic,
                    num_workers=sched.num_workers,
                    precision=sched.precision,
                    checkpoint_every_n=sched.checkpoint_every_n,
                )
                candidates.append((coord, promo_sched))

                if len(candidates) >= 50:  # Limit candidates
                    break

        return candidates

    def _fresh_batch_items(
        self, proposals: list[Proposal], provenance: Provenance
    ) -> list[tuple[Coordinate, Schedule, Provenance, dict[str, Any]]]:
        """The still-unmeasured seeds of every proposal, as single-seed items.

        Identity is the store's: a record is keyed by its own ``n_seeds=1``
        schedule, so a proposal whose seeds were measured in an earlier round —
        or in an earlier launch of this ``run_id`` — is skipped seed by seed
        rather than as a whole cell. Skipping the whole cell would drop the
        seeds it has never run; re-measuring all of them spends the store's
        patience, not the run's.

        Each item carries the proposal's *own* provenance, so the data origin
        and contrast assignment S1 stamped on it reach the record. The run's
        provenance carries neither: a design that vanishes before persistence
        is a design the store cannot re-derive, and the contrast split was
        exactly that.

        Admission gate: every candidate passes through SystemConfig.validate
        (via compose_configs) at the batch boundary. Invalid cells are added
        to rejected_keys and never reach the trainer.
        """
        from computronium.experiment.kernel.compose import compose_configs
        from computronium.experiment.kernel.evaluate import task_shape

        seen: set[str] = set(self._state.completed_measurement_keys)
        rejected: set[str] = set(self._state.rejected_keys)
        skipped = 0
        rejected_this_batch = 0
        items: list[tuple[Coordinate, Schedule, Provenance, dict[str, Any]]] = []
        for proposal in proposals:
            item_provenance = _provenance_for(provenance, proposal)
            for schedule in proposal.schedule.seed_plan:
                key = proposal.coordinate.measurement_key(schedule)
                if key in seen:
                    skipped += 1
                    continue
                if key in rejected:
                    rejected_this_batch += 1
                    continue

                # ADMISSION GATE: last-mile SystemConfig.validate check
                # This is the single source of truth for legality
                try:
                    task_id = schedule.task_id or (
                        self._config.run_spec.task_names[0]
                        if self._config.run_spec.task_names
                        else "unknown"
                    )
                    task_shape_info = task_shape(task_id)
                    config = compose_configs(
                        coordinate=proposal.coordinate,
                        geometry={},
                        input_shape=task_shape_info.input_shape,
                        output_dim=task_shape_info.output_dim,
                        param_budget=schedule.param_budget,
                    )
                    # Param budget check (R25 fairness rule)
                    from computronium.experiment.kernel.compose import (
                        geometry_param_count,
                    )
                    from computronium.experiment.schema.registries import (
                        PARAM_BUDGET_TOLERANCE,
                    )

                    if schedule.param_budget > 0 and geometry_param_count(
                        config.geometry
                    ) > schedule.param_budget * (1 + PARAM_BUDGET_TOLERANCE):
                        raise ValueError(
                            f"Param budget exceeded: {geometry_param_count(config.geometry)} > {schedule.param_budget}"
                        )
                except (ValueError, TypeError, KeyError) as e:
                    # Reject this cell - add to durable rejected set
                    self._state.rejected_keys.add(key)
                    rejected_this_batch += 1
                    self._classify_rejection(
                        coordinate=proposal.coordinate,
                        schedule=schedule,
                        cause="ADMISSION_REJECTED",
                        message=str(e),
                    )
                    continue

                seen.add(key)
                items.append((proposal.coordinate, schedule, item_provenance, {}))

        if skipped:
            logger.info("Skipped %d already-measured seed(s)", skipped)
        if rejected_this_batch:
            logger.info(
                "Admission gate rejected %d invalid cell(s)", rejected_this_batch
            )
        return items

    def _persist_results(
        self,
        batch_items: list[tuple[Coordinate, Schedule, Provenance, dict[str, Any]]],
        results: list[EvaluationResult],
    ) -> list[Record]:
        """Persist successes and classify every non-success; a sibling never aborts the batch."""
        successful: list[Record] = []
        for (coord, sched, _prov, _params), result in zip(batch_items, results):
            match result:
                case Success(records=records):
                    stored_here: list[Record] = []
                    for record in records:
                        record.payload.setdefault(
                            "stage_timings", dict(self._state.stage_timings)
                        )
                        # Check for checkpoint artifact
                        artifacts = []
                        if "checkpoint_bytes_b64" in record.payload:
                            import base64

                            from computronium.experiment.evidence.artifacts import (
                                ArtifactInput,
                                ArtifactRole,
                            )

                            checkpoint_bytes = base64.b64decode(
                                record.payload["checkpoint_bytes_b64"]
                            )
                            artifacts.append(
                                ArtifactInput(
                                    bytes=checkpoint_bytes,
                                    role=ArtifactRole.MODEL_CHECKPOINT,
                                )
                            )
                            # Remove from payload to avoid duplication
                            del record.payload["checkpoint_bytes_b64"]

                        try:
                            if artifacts:
                                self._store.append_with_artifacts(record, artifacts)
                            else:
                                self._store.append(record)
                        except Exception as e:
                            logger.exception(
                                "Failed to persist record %s", coord.cell_key()
                            )
                            self._classify_rejection(
                                coordinate=coord,
                                schedule=sched,
                                cause="PERSISTENCE_ERROR",
                                message=str(e),
                            )
                            continue
                        stored_here.append(record)
                        self._state.completed_measurement_keys.add(
                            record.measurement_key
                        )
                        self._announce_cell(record)
                    self._charge_budget(stored_here)
                    successful.extend(stored_here)
                case Failure(failure_event=event):
                    logger.warning(
                        "Evaluation failed for %s: %s",
                        coord.cell_key(),
                        event.error_message,
                    )
                    self._classify_rejection(
                        coordinate=coord,
                        schedule=sched,
                        cause=getattr(event.failure_cause, "value", None)
                        or str(event.failure_cause),
                        message=event.error_message,
                    )
        return successful

    def _announce_cell(self, record: Record) -> None:
        """Report one measurement as it lands — the number, not a label."""
        accuracy = record.payload.get("val_acc")
        measured = (
            f"val_acc {float(accuracy):.3f}"
            if isinstance(accuracy, int | float)
            else "measured"
        )
        publish_event(
            "s7_measure",
            f"{record.credit}/{record.geometry}/{record.dynamics} "
            f"seed {record.schedule.seed}: {measured}",
            run_id=self._config.run_id,
            detail={
                "record_id": record.record_id,
                "val_acc": accuracy,
                # The narration names the cell and the seed it read here, so
                # the sentence needs no parsing of the message (TODO69).
                "cell": f"{record.credit}/{record.geometry}/{record.dynamics}",
                "seed": record.schedule.seed,
            },
        )

    def _observe(self, record: Record) -> None:
        """Hand a stored measurement to the policy.

        The policy is where a learning policy learns, and until this call
        existed `observe` had zero call sites outside its own module: the study
        was asked, never told (TODO46 §D3).
        """
        policy = self._config.policy
        if policy is None:
            return
        try:
            policy.observe(record)
        except Exception:
            logger.exception(
                "Policy %s failed to observe %s",
                policy.get_name(),
                record.measurement_key[:12],
            )

    def _check_gate(self, fragment: Fragment, stage_spec) -> bool:
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

    def _is_claim_eligible(self, record: Record) -> bool:
        """Check if record is claim-eligible (the one predicate, not a copy)."""
        from computronium.experiment.evidence.claims import claim_eligible

        return claim_eligible(record)

    async def _execute_round(self, all_records: list[Record]) -> None:
        """Execute a single round of S3-S10 stages."""
        self._state.current_round += 1
        logger.info("Starting round %d", self._state.current_round)

        for stage_id in _ROUND_STAGE_ORDER:
            if stage_id not in self._stages:
                continue
            fragment = await self._dispatch_stage(stage_id, get_stage_spec(stage_id))
            self._merge_coverage(fragment.coverage)
            await self._apply_round_stage(stage_id, fragment, all_records)

    async def _apply_round_stage(
        self, stage_id: StageId, fragment: Fragment, all_records: list[Record]
    ) -> None:
        """Fold one round stage's fragment into the run: proposals, records, side work.

        Every round stage dispatches and merges coverage identically; what differs
        is what the stage's fragment *means* downstream, so that is the only
        thing this names.
        """
        match stage_id:
            case StageId.S3_SCHEDULE:
                self._state.pending_proposals = fragment.proposals
            case StageId.S10_DECIDE:
                self._state.pending_proposals = fragment.proposals
                if fragment.decisions:
                    self._state.last_decision = fragment.decisions[-1]
            case StageId.S4_GATE:
                # The gate filters: its proposals replace the queued ones.
                self._state.pending_proposals = fragment.proposals
                self._merge_classification(fragment.classification)
            case StageId.S5_COMPOSE:
                self._state.pending_proposals = fragment.proposals
            case StageId.S6_TRAIN:
                await self._train_pending(fragment, all_records)
            case StageId.S7_MEASURE | StageId.S8_RECORD:
                all_records.extend(fragment.records)
                if stage_id is StageId.S7_MEASURE:
                    await self._attribute_allocation(fragment.records)
            case _:
                # S9 attributes axes and names nothing downstream.
                ...

    async def _train_pending(
        self, fragment: Fragment, all_records: list[Record]
    ) -> None:
        """Execute the round's queued cells, with failure isolation (WP19)."""
        if not self._state.pending_proposals:
            return

        limit = self._config.session_cell_limit
        if limit is not None:
            remaining = limit - len(all_records)
            if remaining <= 0:
                self._state.pending_proposals.clear()
                self._shutdown = True
                return
            self._state.pending_proposals = self._state.pending_proposals[:remaining]

        # Progress bar for proposals in this round
        pbar_proposals = (
            tqdm(
                total=len(self._state.pending_proposals),
                desc=f"Round {self._state.current_round} cells",
                unit="cell",
                leave=False,
                disable=tqdm is None or not sys.stdout.isatty(),
            )
            if tqdm
            else None
        )

        successful = await self._execute_batch_with_isolation(
            self._state.pending_proposals,
            progress_bar=pbar_proposals,
        )
        all_records.extend(successful)
        fragment.records.extend(successful)
        # Executed is not pending: leaving them queued makes S3 skip the policy
        # next round, so a run re-proposes the same cells and stops after one
        # round of a space it never entered.
        self._state.pending_proposals.clear()

        if pbar_proposals:
            pbar_proposals.close()

        if limit is not None and len(all_records) >= limit:
            self._shutdown = True

    async def _attribute_allocation(self, records: list[Record]) -> None:
        """Re-allocate after measuring, before S10 decides (R19 allocator)."""
        if self._config.allocator and self._state.deadline:
            promotions = await self._run_allocator(records)
            # Store promotions in state for S10 Decide stage
            self._state.allocator_promotions = promotions

    async def _dispatch_stage(self, stage_id: StageId, stage_spec) -> Fragment:
        """Dispatch to the concrete stage implementation."""
        from computronium.experiment.execution.stages_impl import (
            get_stage_implementation,
        )

        impl_class = get_stage_implementation(stage_id)
        if impl_class is None:
            logger.warning("No implementation for stage %s, using no-op", stage_id)
            from computronium.experiment.execution.stage import Fragment

            return Fragment(stage_id=stage_id)

        # Create stage context
        ctx = self._create_stage_context(stage_id, stage_spec)

        self._state.current_stage = stage_id.value

        # Run the stage
        stage_impl = impl_class()
        started = time.perf_counter()
        try:
            fragment = await stage_impl.run(ctx)
        except Exception as e:
            logger.exception("Stage %s failed", stage_id)
            # Return fragment with error info
            from computronium.experiment.execution.stage import Fragment

            fragment = Fragment(
                stage_id=stage_id,
                metadata={"error": str(e)},
                coverage={"stage": stage_id.value, "error": True},
            )
        finally:
            self._state.stage_timings[stage_id.value] = time.perf_counter() - started
        self._announce_stage(stage_id, fragment)
        self._publish_status()
        return fragment

    async def _run_allocator(
        self, records: list[Record]
    ) -> list[tuple[Coordinate, Schedule]]:
        """Run EvidenceDrivenAllocator between rounds (R46-R51).

        In the deadline system, allocator uses online cell timing for
        cost estimation instead of predicted cost models.

        Returns:
            List of promoted (coordinate, schedule) pairs for the next round.
        """
        if not self._config.allocator:
            return []

        logger.debug("Running allocator for run %s", self._config.run_id)

        # Use deadline enforcer and cell timing for online cost estimation
        deadline_enforcer = self._state.deadline_enforcer
        cell_timing = self._state.cell_timing
        if deadline_enforcer is None or cell_timing is None:
            return []

        # Check if we have time for more cells
        if not deadline_enforcer.check_before_cell():
            logger.info("Deadline reached, skipping allocator proposals")
            return []

        # Get candidates from search space for promotion consideration
        search_space = self._state.search_space
        if search_space is None:
            return []

        # Build candidates from search space (structural coordinates at next fidelity)
        candidates = self._build_allocator_candidates(search_space)
        if not candidates:
            return []

        # Observe records to update allocator's evidence base
        for record in records:
            self._config.allocator.observe(record)

        # Get promotion proposals from allocator
        promotions = self._config.allocator.propose(
            candidates,
            records,
            deadline=self._state.deadline,
            cost_model=None,
        )

        logger.info("Allocator proposed %d promotions", len(promotions))
        return promotions

    async def _execute_batch_with_isolation(
        self,
        proposals: list[Proposal],
        progress_bar: tqdm | None = None,  # type: ignore[reportInvalidTypeForm]
    ) -> list[Record]:
        """Execute a batch of proposals with failure isolation (WP19).

        Uses backend.submit_batch which returns per-item EvaluationResult
        (Success or Failure), allowing successful siblings to continue
        even if some evaluations fail.

        Deadline enforcement:
        - Check soft deadline before starting batch
        - Track cell timing for online learning
        - Mark QUARANTINE cells if hard deadline breached mid-execution
        """
        if not self._config.backend:
            logger.warning("No backend configured, skipping batch execution")
            return []

        # The batch boundary: a pause holds here, and a step releases exactly
        # this batch.
        await self._await_control(consumes_step=True)
        if self._shutdown:
            return []

        # Check deadline before starting batch
        deadline_enforcer = self._state.deadline_enforcer
        if deadline_enforcer and not deadline_enforcer.check_before_cell():
            logger.info("Soft deadline reached, stopping before new batch")
            self._shutdown = True
            return []

        system_context = self._state.system_context
        if system_context is None:
            raise ValueError("SystemContext not initialized")
        provenance = self._provenance(system_context.environment.to_provenance_dict())

        batch_items = self._fresh_batch_items(proposals, provenance)
        if not batch_items:
            return []

        # Start cell timing for this batch
        cell_timing = self._state.cell_timing
        if cell_timing:
            cell_timing.start_cell()

        try:
            results = await self._config.backend.submit_batch(batch_items, self._store)
        finally:
            # End cell timing
            if cell_timing:
                cell_timing.end_cell()

        stored = self._persist_results(batch_items, results)
        self._publish_status()
        if stored:
            publish_event(
                "s8_record",
                f"recorded {len(stored)} cells",
                run_id=self._config.run_id,
                detail={"records": len(stored)},
            )
        for record in stored:
            self._observe(record)

        # Check deadline after batch
        if deadline_enforcer and not deadline_enforcer.check_after_cell():
            logger.info("Soft deadline reached after batch, stopping")
            self._shutdown = True

        if progress_bar:
            progress_bar.update(len(stored))
        return stored
