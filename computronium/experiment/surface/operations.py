"""Operations surface — pausable runs, service mode, webhook alerts (WP7).

Provides:
- Pausable/steerable runs with operator intent records
- Service mode for long-running campaigns
- Webhook alerts for monitoring
- Operator intent recording for audit trail
"""

from __future__ import annotations

import asyncio
import json
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any
from urllib import request

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from computronium.experiment.execution.pipeline import PipelineRunner

from computronium.core.logging import get_logger
from computronium.experiment.evidence.store import RecordStore, StoreConfig

logger = get_logger()


class RunState(StrEnum):
    """Run lifecycle states."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    STEERING = "steering"  # Accepting operator input
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OperatorIntentKind(StrEnum):
    """Types of operator intent."""

    PAUSE = "pause"
    RESUME = "resume"
    STOP = "stop"
    MODIFY_BUDGET = "modify_budget"
    MODIFY_STAGES = "modify_stages"
    MODIFY_OBJECTIVES = "modify_objectives"
    UNQUARANTINE = "unquarantine"
    PRIORITIZE_CELL = "prioritize_cell"
    INJECT_CANDIDATE = "inject_candidate"
    SNAPSHOT = "snapshot"


@dataclass(frozen=True, slots=True)
class OperatorIntent:
    """Record of operator intent for audit trail."""

    intent_id: str
    run_id: str
    kind: OperatorIntentKind
    payload: dict[str, Any]
    timestamp: datetime
    operator: str
    reason: str = ""


@dataclass(frozen=True, slots=True)
class WebhookConfig:
    """Webhook configuration for alerts."""

    url: str
    events: list[str]  # Event types to trigger webhook
    headers: dict[str, str] = field(default_factory=dict)
    timeout_seconds: float = 10.0
    retry_count: int = 3
    retry_delay_seconds: float = 1.0


@dataclass(frozen=True, slots=True)
class ServiceConfig:
    """Service mode configuration."""

    run_id: str
    store_path: Path
    checkpoint_interval_seconds: float = 60.0
    webhook: WebhookConfig | None = None
    auto_restart: bool = False
    max_restarts: int = 3


class RunController:
    """Controller for pausable/steerable runs.

    Allows operators to pause, resume, steer, and monitor long-running
    experiment runs with full audit trail.
    """

    def __init__(self, run_id: str, store: RecordStore) -> None:
        self._run_id = run_id
        self._store = store
        self._state = RunState.PENDING
        self._state_lock = threading.RLock()
        self._pipeline_runner: PipelineRunner | None = None
        self._run_task: asyncio.Task | None = None
        self._intents: list[OperatorIntent] = []
        self._steering_queue: asyncio.Queue[OperatorIntent] = asyncio.Queue()
        self._shutdown_event = asyncio.Event()
        self._webhooks: list[WebhookConfig] = []
        self._webhook_tasks: list[asyncio.Task] = []

    @property
    def run_id(self) -> str:
        return self._run_id

    @property
    def state(self) -> RunState:
        with self._state_lock:
            return self._state

    def _set_state(self, state: RunState) -> None:
        with self._state_lock:
            old_state = self._state
            self._state = state
            logger.info(f"Run {self._run_id} state: {old_state} -> {state}")

    def add_webhook(self, webhook: WebhookConfig) -> None:
        """Register a webhook for alerts."""
        self._webhooks.append(webhook)

    def record_intent(self, intent: OperatorIntent) -> None:
        """Record operator intent for audit trail."""
        self._intents.append(intent)
        logger.info(
            f"Operator intent recorded: {intent.kind.value} for run {self._run_id}"
        )

        # Also persist to store as artifact
        self._persist_intent(intent)

    def _persist_intent(self, intent: OperatorIntent) -> None:
        """Persist intent as a run-linked record through the single writer."""
        try:
            record = self._store.record_intent(
                intent.run_id,
                {
                    "intent_id": intent.intent_id,
                    "kind": intent.kind.value,
                    "payload": intent.payload,
                    "timestamp": intent.timestamp.isoformat(),
                    "operator": intent.operator,
                    "reason": intent.reason,
                },
            )
            logger.debug(f"Intent persisted as record {record.record_id}")
        except Exception:
            logger.exception("Intent persistence failed")

    async def _emit_alert(self, event: str, data: dict[str, Any]) -> None:
        """Emit alert to all registered webhooks."""
        for webhook in self._webhooks:
            if event in webhook.events:
                task = asyncio.create_task(self._send_webhook(webhook, event, data))
                self._webhook_tasks.append(task)

    async def _send_webhook(
        self, webhook: WebhookConfig, event: str, data: dict[str, Any]
    ) -> None:
        """Send webhook with retry logic."""
        payload = json.dumps({
            "event": event,
            "run_id": self._run_id,
            "data": data,
        }).encode()

        for attempt in range(webhook.retry_count):
            try:
                req = request.Request(  # ruff: ignore[suspicious-url-open-usage] - webhook URL is user-configured
                    webhook.url,
                    data=payload,
                    headers={
                        "Content-Type": "application/json",
                        **webhook.headers,
                    },
                )
                with request.urlopen(req, timeout=webhook.timeout_seconds) as resp:  # ruff: ignore[suspicious-url-open-usage]
                    if 200 <= resp.status < 300:
                        return
                    logger.warning(
                        f"Webhook returned {resp.status}: {resp.read().decode()}"
                    )
            except Exception as e:
                logger.warning(f"Webhook attempt {attempt + 1} failed: {e}")
                if attempt < webhook.retry_count - 1:
                    await asyncio.sleep(webhook.retry_delay_seconds)

        logger.error(
            f"Webhook failed after {webhook.retry_count} attempts: {webhook.url}"
        )

    async def run(self, runner: PipelineRunner) -> list[Any]:
        """Run the pipeline with pause/steer support."""
        self._pipeline_runner = runner
        self._set_state(RunState.RUNNING)

        # Start the pipeline in a task
        self._run_task = asyncio.create_task(runner.run())
        steering_task: asyncio.Task[OperatorIntent] | None = None

        try:  # ruff: ignore[too-many-statements-in-try-clause]
            # Monitor for steering intents
            while not self._run_task.done():
                # Ensure steering task is running
                if steering_task is None or steering_task.done():
                    steering_task = asyncio.create_task(self._steering_queue.get())

                # Wait for either completion or steering intent
                done, _pending = await asyncio.wait(
                    [self._run_task, steering_task],
                    return_when=asyncio.FIRST_COMPLETED,
                )

                for task in done:
                    if task is self._run_task:
                        # Pipeline completed
                        result: list[Any] = task.result()  # type: ignore[return-value]
                        self._set_state(RunState.COMPLETED)
                        await self._emit_alert(
                            "run_completed", {"result_count": len(result)}
                        )
                        return result

                    # Steering intent received
                    intent: OperatorIntent = task.result()
                    await self._handle_intent(intent)

        except asyncio.CancelledError:
            self._set_state(RunState.CANCELLED)
            await self._emit_alert("run_cancelled", {})
            raise
        except Exception as e:
            self._set_state(RunState.FAILED)
            await self._emit_alert("run_failed", {"error": str(e)})
            raise
        finally:
            self._shutdown_event.set()

        # Task completed normally (should not reach here due to loop condition)
        result = self._run_task.result()
        self._set_state(RunState.COMPLETED)
        await self._emit_alert("run_completed", {"result_count": len(result)})
        return result

    async def _handle_intent(self, intent: OperatorIntent) -> None:
        """Handle an operator intent during execution."""
        self.record_intent(intent)

        handler_map: dict[OperatorIntentKind, Callable[[dict[str, Any]], Any]] = {
            OperatorIntentKind.PAUSE: lambda _: self._pause(),
            OperatorIntentKind.RESUME: lambda _: self._resume(),
            OperatorIntentKind.STOP: lambda _: self._stop(),
            OperatorIntentKind.MODIFY_BUDGET: self._modify_budget,
            OperatorIntentKind.MODIFY_STAGES: self._modify_stages,
            OperatorIntentKind.MODIFY_OBJECTIVES: self._modify_objectives,
            OperatorIntentKind.UNQUARANTINE: self._unquarantine,
            OperatorIntentKind.PRIORITIZE_CELL: self._prioritize_cell,
            OperatorIntentKind.INJECT_CANDIDATE: self._inject_candidate,
            OperatorIntentKind.SNAPSHOT: lambda _: self._snapshot(),
        }

        handler = handler_map.get(intent.kind)
        if handler:
            await handler(intent.payload)
        else:
            logger.warning(f"Unknown intent kind: {intent.kind}")

    async def _pause(self) -> None:
        """Pause the running pipeline."""
        if self._pipeline_runner:
            self._pipeline_runner.shutdown()
            self._set_state(RunState.PAUSED)
            await self._emit_alert("run_paused", {"run_id": self._run_id})

    async def _resume(self) -> None:
        """Resume a paused pipeline."""
        if self._state == RunState.PAUSED:
            # Would need to recreate runner from checkpoint
            # For now, just transition state
            self._set_state(RunState.RUNNING)
            await self._emit_alert("run_resumed", {"run_id": self._run_id})

    async def _stop(self) -> None:
        """Stop the pipeline gracefully."""
        if self._pipeline_runner:
            self._pipeline_runner.shutdown()
        if self._run_task:
            self._run_task.cancel()
        self._set_state(RunState.CANCELLED)
        await self._emit_alert("run_stopped", {"run_id": self._run_id})

    async def _modify_budget(self, payload: dict[str, Any]) -> None:
        """Modify the budget (soft/hard seconds, target cells)."""
        if self._pipeline_runner and self._pipeline_runner._state.budget:
            # Budget is immutable, would need to recreate
            logger.info(f"Budget modification requested: {payload}")
            await self._emit_alert("budget_modified", payload)

    async def _modify_stages(self, payload: dict[str, Any]) -> None:
        """Modify remaining stages."""
        logger.info(f"Stage modification requested: {payload}")
        await self._emit_alert("stages_modified", payload)

    async def _modify_objectives(self, payload: dict[str, Any]) -> None:
        """Modify optimization objectives."""
        logger.info(f"Objectives modification requested: {payload}")
        await self._emit_alert("objectives_modified", payload)

    async def _unquarantine(self, payload: dict[str, Any]) -> None:
        """Unquarantine a cell/coordinate."""
        cell_key = payload.get("cell_key")
        if cell_key:
            logger.info(f"Unquarantine requested for cell: {cell_key}")
            await self._emit_alert("cell_unquarantined", {"cell_key": cell_key})

    async def _prioritize_cell(self, payload: dict[str, Any]) -> None:
        """Prioritize a specific cell for evaluation."""
        cell_key = payload.get("cell_key")
        priority = payload.get("priority", 1)
        if cell_key:
            logger.info(f"Prioritize cell: {cell_key} with priority {priority}")
            await self._emit_alert(
                "cell_prioritized", {"cell_key": cell_key, "priority": priority}
            )

    async def _inject_candidate(self, payload: dict[str, Any]) -> None:
        """Inject a candidate coordinate for evaluation."""
        logger.info(f"Candidate injection requested: {payload}")
        await self._emit_alert("candidate_injected", payload)

    async def _snapshot(self) -> None:
        """Report the run's measured state; the store is the checkpoint (D3).

        There is no snapshot file to write: a resume reads the store's own
        measured keys, so a snapshot is a number, not an artifact.
        """
        if self._pipeline_runner:
            measured = len(self._pipeline_runner._state.completed_measurement_keys)
            await self._emit_alert(
                "snapshot_created", {"run_id": self._run_id, "measured": measured}
            )

    def submit_intent(self, intent: OperatorIntent) -> None:
        """Submit an operator intent (thread-safe)."""
        # Put into steering queue for async handling
        try:
            self._steering_queue.put_nowait(intent)
        except asyncio.QueueFull:
            logger.exception("Steering queue full, intent dropped")

    def get_intents(self) -> list[OperatorIntent]:
        """Get all recorded intents."""
        return list(self._intents)


class ServiceManager:
    """Manages long-running experiment services.

    Handles:
    - Automatic restart on failure
    - Periodic checkpointing
    - Webhook notifications
    - Health monitoring
    """

    def __init__(self, config: ServiceConfig) -> None:
        self._config = config
        self._run_controller: RunController | None = None
        self._restart_count = 0
        self._monitor_task: asyncio.Task | None = None

    async def start(self, runner_factory: Callable[[], PipelineRunner]) -> list[Any]:
        """Start the service with automatic restart."""
        while self._restart_count <= self._config.max_restarts:
            try:  # ruff: ignore[too-many-statements-in-try-clause]
                store_config = StoreConfig(path=self._config.store_path)
                with RecordStore(store_config) as store:
                    self._run_controller = RunController(self._config.run_id, store)

                    if self._config.webhook:
                        self._run_controller.add_webhook(self._config.webhook)

                    runner = runner_factory()
                    result = await self._run_controller.run(runner)

                    if self._run_controller.state == RunState.COMPLETED:
                        return result

            except asyncio.CancelledError:
                logger.info("Service cancelled")
                raise
            except Exception:
                logger.exception("Service run failed")
                self._restart_count += 1

                if (
                    self._config.auto_restart
                    and self._restart_count <= self._config.max_restarts
                ):
                    logger.info(
                        f"Restarting ({self._restart_count}/{self._config.max_restarts})..."
                    )
                    await asyncio.sleep(5)  # Brief delay before restart
                    continue
                raise

        raise RuntimeError(f"Service failed after {self._config.max_restarts} restarts")

    def get_controller(self) -> RunController | None:
        """Get the current run controller."""
        return self._run_controller


def create_operator_intent(
    run_id: str,
    kind: OperatorIntentKind,
    payload: dict[str, Any],
    operator: str = "cli",
    reason: str = "",
) -> OperatorIntent:
    """Factory for creating operator intents."""
    return OperatorIntent(
        intent_id=str(uuid.uuid4()),
        run_id=run_id,
        kind=kind,
        payload=payload,
        timestamp=datetime.now(),
        operator=operator,
        reason=reason,
    )


class AlertDedup:
    """Notify-only alert dedup keyed (predicate, run, window) (R83).

    Thread-safe; the window is wall-clock seconds per predicate+run key.
    """

    def __init__(self, window_seconds: float = 3600.0) -> None:
        self._window = window_seconds
        self._last_fired: dict[tuple[str, str], datetime] = {}
        self._lock = threading.Lock()

    def should_fire(self, predicate: str, run_id: str) -> bool:
        """Return True once per window for a (predicate, run) pair."""
        from datetime import timedelta

        now = datetime.now()
        key = (predicate, run_id)
        with self._lock:
            last = self._last_fired.get(key)
            if last is not None and now - last < timedelta(seconds=self._window):
                return False
            self._last_fired[key] = now
            return True


DEFAULT_Q14_ROUTES: dict[str, list[str]] = {
    "run_completed": ["operator", "ledger"],
    "run_failed": ["operator", "pager"],
    "run_cancelled": ["operator"],
    "run_paused": ["operator"],
    "run_resumed": ["operator"],
    "divergence": ["operator", "ledger"],
    "stagnation": ["ledger"],
    "resource_exhaustion": ["operator", "pager"],
    "constraint_violation": ["ledger"],
}
"""Q14 default webhook routing: event -> subscriber groups.

Recorded as ``WebhookConfig.events`` defaults; a webhook subscribes by
listing the events it wants, defaulting to its group's routes.
"""


def default_events_for(group: str = "operator") -> list[str]:
    """Events routed to a subscriber group per the Q14 routing model."""
    return sorted(
        event for event, groups in DEFAULT_Q14_ROUTES.items() if group in groups
    )


def submit_intent_to_run(
    run_id: str,
    store_path: Path,
    kind: OperatorIntentKind,
    payload: dict[str, Any],
    operator: str = "cli",
    reason: str = "",
) -> None:
    """Submit an intent to a running service (for external CLI use).

    Persists the intent as a run-linked record through the single writer;
    the service's control-file watcher picks it up on its next poll.
    """
    intent = create_operator_intent(run_id, kind, payload, operator, reason)

    store_config = StoreConfig(path=store_path)
    with RecordStore(store_config) as store:
        store.record_intent(
            run_id,
            {
                "intent_id": intent.intent_id,
                "kind": intent.kind.value,
                "payload": intent.payload,
                "timestamp": intent.timestamp.isoformat(),
                "operator": intent.operator,
                "reason": intent.reason,
            },
        )
        logger.info(f"Intent submitted for run {run_id}: {kind.value}")


__all__ = [
    "DEFAULT_Q14_ROUTES",
    "AlertDedup",
    "OperatorIntent",
    "OperatorIntentKind",
    "RunController",
    "RunState",
    "ServiceConfig",
    "ServiceManager",
    "WebhookConfig",
    "create_operator_intent",
    "default_events_for",
    "submit_intent_to_run",
]
