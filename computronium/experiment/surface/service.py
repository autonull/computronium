"""Headless service loop with control-file steering (WP11.4, R81-R84).

While a service-mode run holds the store (exclusive writer), live
reporting and steering route through this loop: an external CLI writes
intent JSON lines to the control file; the loop polls it, persists each
intent as a run-linked record through the single writer, and applies it
to the run controller.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from computronium.core.logging import get_logger
from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.surface.operations import (
    AlertDedup,
    OperatorIntentKind,
    RunController,
    create_operator_intent,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from computronium.experiment.execution.pipeline import PipelineRunner

logger = get_logger()

__all__ = [
    "ServiceLoop",
    "ServiceLoopConfig",
    "poll_control_file",
    "write_control_intent",
]


@dataclass(frozen=True, slots=True)
class ServiceLoopConfig:
    """Configuration for the headless service loop."""

    run_id: str
    store_path: Path
    control_path: Path
    poll_interval_seconds: float = 2.0
    alert_window_seconds: float = 3600.0


def write_control_intent(
    control_path: str | Path,
    kind: OperatorIntentKind,
    payload: dict[str, Any],
    operator: str = "cli",
    reason: str = "",
) -> None:
    """Append one intent JSON line to the control file (external CLI side)."""
    line = json.dumps({
        "kind": kind.value,
        "payload": payload,
        "operator": operator,
        "reason": reason,
        "written_at": datetime.now().isoformat(),
    })
    with Path(control_path).open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def poll_control_file(
    control_path: str | Path, run_id: str, operator: str = "cli"
) -> list[Any]:
    """Read and consume pending intent lines from the control file."""
    path = Path(control_path)
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("", encoding="utf-8")
    intents = []
    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            continue
        try:
            data = json.loads(stripped)
            intents.append(
                create_operator_intent(
                    run_id,
                    OperatorIntentKind(data["kind"]),
                    data.get("payload", {}),
                    data.get("operator", operator),
                    data.get("reason", ""),
                )
            )
        except json.JSONDecodeError, KeyError, ValueError:
            logger.warning(f"Skipping malformed control line: {stripped[:80]}")
    return intents


class ServiceLoop:
    """Headless run loop: pipeline execution + control-file steering."""

    def __init__(self, config: ServiceLoopConfig) -> None:
        self._config = config
        self._dedup = AlertDedup(config.alert_window_seconds)
        self._controller: RunController | None = None

    @property
    def controller(self) -> RunController | None:
        """Current run controller, if the loop has started."""
        return self._controller

    async def serve(self, runner_factory: Callable[[], PipelineRunner]) -> list[Any]:
        """Run the pipeline to completion, polling the control file."""
        store_config = StoreConfig(path=self._config.store_path)
        with RecordStore(store_config) as store:
            self._controller = RunController(self._config.run_id, store)
            runner = runner_factory()
            run_task = asyncio.create_task(self._controller.run(runner))
            try:
                while not run_task.done():
                    await asyncio.sleep(self._config.poll_interval_seconds)
                    for intent in poll_control_file(
                        self._config.control_path, self._config.run_id
                    ):
                        if self._dedup.should_fire(
                            f"intent:{intent.kind.value}", self._config.run_id
                        ):
                            self._controller.submit_intent(intent)
            except asyncio.CancelledError:
                run_task.cancel()
                raise
            return await run_task
