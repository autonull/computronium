"""Shared attribute surface for the pipeline runner's concern modules."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from computronium.experiment.execution.deadline import (
        DeadlineEnforcer,
        SignalHandler,
    )
    from computronium.experiment.execution.decision import Decision
    from computronium.experiment.execution.stage import Fragment, StageId
    from computronium.experiment.kernel.search_space import SearchSpace
    from computronium.experiment.schema.record import Record

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None  # type: ignore[assignment]


class _PipelineBase:
    _ceiling: Any
    _code_sha: Any
    _config: Any
    _control: Any
    _dataset: Any
    _heartbeat_task: Any
    _shutdown: Any
    _stages: Any
    _state: Any
    _steps_taken: Any
    _store: Any
    budget: Any
    cause: Any
    count: Any
    deadline: Any

    # Cross-mixin contract: each is implemented by one concern module.
    async def _apply_ceiling(self, max_workers: int | None) -> None:
        raise NotImplementedError

    async def _await_control(self, *, consumes_step: bool) -> None:
        raise NotImplementedError

    def _build_search_space(self) -> SearchSpace:
        raise NotImplementedError

    def _charge_budget(self, records: list[Record]) -> None:
        raise NotImplementedError

    def _check_gate(self, fragment: Fragment, stage_spec) -> bool:
        raise NotImplementedError

    def _check_post_round_deadline(
        self, deadline_enforcer: DeadlineEnforcer | None
    ) -> None:
        raise NotImplementedError

    def _check_zero_yield(self) -> None:
        raise NotImplementedError

    def _checkpoint(self) -> None:
        raise NotImplementedError

    async def _dispatch_stage(self, stage_id: StageId, stage_spec) -> Fragment:
        raise NotImplementedError

    async def _execute_round(self, all_records: list[Record]) -> None:
        raise NotImplementedError

    def _get_decision_from_fragments(self) -> Decision:
        raise NotImplementedError

    def _merge_coverage(self, coverage: dict[str, Any]) -> None:
        raise NotImplementedError

    def _publish_status(self) -> None:
        raise NotImplementedError

    def _should_stop_round_loop(
        self,
        deadline_enforcer: DeadlineEnforcer | None,
        signal_handler: SignalHandler | None,
    ) -> bool:
        raise NotImplementedError

    def _stream_is_spent(self, records_before_round: int, records_now: int) -> bool:
        raise NotImplementedError
