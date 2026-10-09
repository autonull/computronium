"""Campaign execution: declarative multi-run campaigns with dependencies and parallelism."""

from __future__ import annotations

import asyncio
import json
import signal
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from computronium.core.logging import get_logger
from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.execution.backends import LocalBackend
from computronium.experiment.execution.budget import Budget, SimpleCostModel
from computronium.experiment.execution.evaluate import task_shape
from computronium.experiment.execution.pipeline import PipelineConfig, PipelineRunner
from computronium.experiment.schema import RunSpec, StageId
from computronium.experiment.surface.cli import (
    _CELL_WORKERS,
    _consumed,
    _duration_str,
    _resolve_spec,
    _settle_maturity,
    create_policy,
    policy_context,
)

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class CampaignRun:
    """A single run within a campaign."""

    name: str
    profile: str | None = None
    spec_file: str | None = None
    overrides: dict[str, Any] = field(default_factory=dict)
    depends_on: list[int] = field(default_factory=list)
    device: str = "auto"
    store: str = "experiment.duckdb"


@dataclass(frozen=True, slots=True)
class CampaignSpec:
    """Full campaign specification."""

    name: str
    runs: list[CampaignRun]
    store: str = "experiment.duckdb"
    parallel: int = 1
    webhook_url: str | None = None
    # Global time budget for the entire campaign (seconds)
    max_wall_seconds: float | None = None


class CampaignRunner:
    """Executes a campaign with dependency resolution and parallelism."""

    def __init__(
        self,
        spec: CampaignSpec,
        webhook_url: str | None = None,
    ):
        self.spec = spec
        self.webhook_url = webhook_url or spec.webhook_url
        self.results: dict[int, dict[str, Any]] = {}
        self.running: dict[int, asyncio.Task] = {}
        self._run_id_map: dict[int, str] = {}
        self._store_lock = asyncio.Lock()
        # Global campaign time tracking
        self._campaign_start_time: float = time.monotonic()
        self._campaign_budget_seconds: float | None = spec.max_wall_seconds
        self._shutdown_requested: bool = False

    async def _send_webhook(
        self, event: str, run_idx: int, data: dict[str, Any]
    ) -> None:
        """Send progress webhook if configured."""
        if not self.webhook_url:
            return
        payload = {
            "event": event,
            "campaign": self.spec.name,
            "run_index": run_idx,
            "run_name": self.spec.runs[run_idx].name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            **data,
        }
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                await session.post(
                    self.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                )
        except Exception:  # Webhooks are best-effort
            logger.debug("Webhook delivery failed", exc_info=True)

    def _build_run_spec(self, run: CampaignRun) -> RunSpec:
        """Build a RunSpec from a campaign run."""
        import argparse

        # Create a mock args namespace for _resolve_spec
        args = argparse.Namespace()
        args.profile = run.profile
        args.spec = run.spec_file
        args.overrides = json.dumps(run.overrides) if run.overrides else None
        args.task = run.overrides.get("task") if run.overrides else None
        args.dry_run = False
        args.device = run.device
        args.store = self.spec.store
        args.run_id = None

        return _resolve_spec(args)

    async def _execute_run(self, run_idx: int) -> dict[str, Any]:
        """Execute a single run in-process and return its result."""
        run = self.spec.runs[run_idx]
        await self._send_webhook("started", run_idx, {})

        start_time = time.time()

        spec = self._build_run_spec(run)
        exit_code = await self._run_pipeline_with_lock(spec)
        elapsed = time.time() - start_time

        return self._make_result(run_idx, exit_code, elapsed)

    async def _run_pipeline_with_lock(self, spec: RunSpec) -> int:
        """Run pipeline with store lock."""
        async with self._store_lock:
            return await self._run_pipeline(spec)

    def _make_result(
        self, run_idx: int, exit_code: int, elapsed: float
    ) -> dict[str, Any]:
        """Create result dict from exit code."""
        if exit_code == 0:
            return {"success": True, "run_id": None, "elapsed_s": elapsed}
        return {
            "success": False,
            "error": f"Pipeline exited with code {exit_code}",
            "elapsed_s": elapsed,
        }

    async def _run_pipeline(self, spec: RunSpec) -> int:
        """Run the pipeline for a spec directly."""

        policy_name = spec.policy or "round_robin_grid"

        with RecordStore(StoreConfig(path=Path(self.spec.store))) as store:
            run_id = store.create_run(spec=spec)
            logger.info("Run ID: %s", run_id)

            budget = (
                Budget.from_duration(_duration_str(spec.budget_seconds))
                if spec.budget_seconds is not None
                else None
            )

            policy = create_policy(
                policy_name, **policy_context(spec, policy_name, shape=task_shape)
            )

            max_rounds = None
            if spec.stages and StageId.S10_DECIDE not in spec.stages:
                max_rounds = 1

            runner = PipelineRunner(
                PipelineConfig(
                    run_id=run_id,
                    run_spec=spec,
                    budget=budget,
                    cost_model=SimpleCostModel(),
                    policy=policy,
                    backend=LocalBackend(max_workers=_CELL_WORKERS),
                    seed=spec.seed,
                    max_rounds=max_rounds,
                ),
                store,
            )

            interrupted = {"flag": False}

            def _signal_handler(signum, _frame):
                logger.info("Received signal %s; finishing run %s", signum, run_id)
                interrupted["flag"] = True
                runner.shutdown()

            old_sigint = signal.signal(signal.SIGINT, _signal_handler)
            old_sigterm = signal.signal(signal.SIGTERM, _signal_handler)

            try:
                outcomes = await runner.run()
            except KeyboardInterrupt:
                logger.info("Interrupted; resume with --run-id %s", run_id)
                store.finish_run(
                    run_id, "interrupted", budget_consumed_s=_consumed(runner)
                )
                return 130
            except Exception as exc:
                logger.error("Pipeline failed: %s", exc, exc_info=True)
                store.finish_run(run_id, "failed", budget_consumed_s=_consumed(runner))
                return 1
            finally:
                signal.signal(signal.SIGINT, old_sigint)
                signal.signal(signal.SIGTERM, old_sigterm)

            if interrupted["flag"]:
                logger.info(
                    "Run interrupted by signal; resume with --run-id %s", run_id
                )
                store.finish_run(
                    run_id, "interrupted", budget_consumed_s=_consumed(runner)
                )
                return 130

            _settle_maturity(store, run_id, spec)

            budget_consumed = _consumed(runner)
            store.finish_run(run_id, "completed", budget_consumed_s=budget_consumed)
            logger.info(
                "Run %s completed with %d records in %s",
                run_id,
                len(outcomes),
                store._config.path,
            )
            return 0

    async def execute(self) -> dict[str, Any]:
        """Execute the full campaign with dependency resolution and global time budget."""
        self._validate_dependencies()
        self._setup_signal_handlers()

        semaphore = asyncio.Semaphore(self.spec.parallel)

        async def run_with_semaphore(idx: int) -> dict[str, Any]:
            async with semaphore:
                return await self._execute_run(idx)

        while self._has_work_pending():
            # Check global campaign time budget
            if self._is_campaign_budget_exhausted():
                logger.info("Campaign time budget exhausted; stopping")
                self._shutdown_requested = True
                # Cancel all running tasks
                for task in self.running.values():
                    task.cancel()
                # Wait for cancellations
                if self.running:
                    await asyncio.gather(*self.running.values(), return_exceptions=True)
                break

            self._start_ready_runs(run_with_semaphore)

            if not self.running:
                if self.pending:
                    raise RuntimeError(
                        "Campaign deadlock: remaining runs have unmet dependencies"
                    )
                break

            done, pending_tasks = await asyncio.wait(
                self.running.values(),
                return_when=asyncio.FIRST_COMPLETED,
            )

            # Map tasks to indices before updating running dict
            task_to_idx = {task: idx for idx, task in self.running.items()}

            self._update_running_tasks(pending_tasks)
            await self._process_completed_tasks(done, task_to_idx)

        return self._build_result()

    def _is_campaign_budget_exhausted(self) -> bool:
        """Check if the global campaign time budget has been exhausted."""
        if self._campaign_budget_seconds is None:
            return False
        elapsed = time.monotonic() - self._campaign_start_time
        return elapsed >= self._campaign_budget_seconds

    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful campaign shutdown."""
        if self._shutdown_requested:
            return

        def _signal_handler(signum, _frame):
            logger.info("Campaign received signal %s; initiating graceful shutdown", signum)
            self._shutdown_requested = True

        try:
            self._old_sigint = signal.signal(signal.SIGINT, _signal_handler)
            self._old_sigterm = signal.signal(signal.SIGTERM, _signal_handler)
        except (ValueError, OSError):
            # Signal handling not available in this context (e.g., non-main thread)
            pass

    def _restore_signal_handlers(self) -> None:
        """Restore original signal handlers."""
        try:
            signal.signal(signal.SIGINT, self._old_sigint)
            signal.signal(signal.SIGTERM, self._old_sigterm)
        except (AttributeError, ValueError, OSError):
            pass

    def _validate_dependencies(self) -> None:
        """Validate campaign dependencies."""
        n_runs = len(self.spec.runs)
        self.pending = set(range(n_runs))
        self.completed: set[int] = set()
        self.failed: set[int] = set()

        for i, run in enumerate(self.spec.runs):
            for dep in run.depends_on:
                if dep < 0 or dep >= n_runs:
                    raise ValueError(f"Run {i} depends on invalid index {dep}")
                if dep >= i:
                    raise ValueError(f"Run {i} depends on future run {dep}")

    def _has_work_pending(self) -> bool:
        """Check if there's work to do."""
        return bool(self.pending or self.running)

    def _start_ready_runs(self, run_with_semaphore) -> None:
        """Start runs whose dependencies are met."""
        ready = [
            i
            for i in self.pending
            if all(dep in self.completed for dep in self.spec.runs[i].depends_on)
        ]

        for idx in ready:
            if len(self.running) >= self.spec.parallel:
                break
            self.pending.remove(idx)
            task = asyncio.create_task(run_with_semaphore(idx))
            self.running[idx] = task

    def _update_running_tasks(self, pending_tasks: set) -> None:
        """Update running tasks dict to keep only pending tasks."""
        new_running = {}
        for idx, task in self.running.items():
            if task in pending_tasks:
                new_running[idx] = task
        self.running = new_running

    async def _process_completed_tasks(self, done: set, task_to_idx: dict) -> None:
        """Process completed tasks and handle failures."""

        for task in done:
            idx = task_to_idx[task]
            result = task.result()
            self.results[idx] = result

            if result["success"]:
                self.completed.add(idx)
            else:
                self.failed.add(idx)
                await self._cancel_dependent_runs(idx)

    async def _cancel_dependent_runs(self, failed_idx: int) -> None:
        """Cancel runs that depend on a failed run."""
        to_remove = []
        for j in self.pending:
            if failed_idx in self.spec.runs[j].depends_on:
                await self._send_webhook(
                    "skipped", j, {"reason": f"dependency {failed_idx} failed"}
                )
                self.results[j] = {
                    "success": False,
                    "skipped": True,
                    "reason": f"dependency {failed_idx} failed",
                }
                self.failed.add(j)
                to_remove.append(j)
        for j in to_remove:
            self.pending.remove(j)

    def _build_result(self) -> dict[str, Any]:
        """Build the final campaign result."""
        self._restore_signal_handlers()
        campaign_elapsed = time.monotonic() - self._campaign_start_time
        return {
            "campaign": self.spec.name,
            "total_runs": len(self.spec.runs),
            "completed": len(self.completed),
            "failed": len(self.failed),
            "run_results": self.results,
            "run_ids": self._run_id_map,
            "campaign_elapsed_seconds": campaign_elapsed,
            "campaign_budget_seconds": self._campaign_budget_seconds,
            "budget_exhausted": self._is_campaign_budget_exhausted(),
        }


def load_campaign(path: str | Path) -> CampaignSpec:
    """Load a campaign specification from a YAML file."""
    with Path(path).open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise TypeError("Campaign file must be a YAML mapping")

    runs_data = data.get("runs", [])
    if not runs_data:
        raise ValueError("Campaign must have at least one run")

    runs = []
    for i, run_data in enumerate(runs_data):
        if not isinstance(run_data, dict):
            raise TypeError(f"Run {i} must be a mapping")
        runs.append(
            CampaignRun(
                name=run_data.get("name", f"run_{i}"),
                profile=run_data.get("profile"),
                spec_file=run_data.get("spec_file"),
                overrides=run_data.get("overrides", {}),
                depends_on=run_data.get("depends_on", []),
                device=run_data.get("device", "auto"),
                store=run_data.get("store", data.get("store", "experiment.duckdb")),
            )
        )

    # Parse global time budget from compute.max_wall_hours or resources.max_wall_hours
    max_wall_seconds = None
    compute = data.get("compute", {})
    resources = data.get("resources", {})
    if "max_wall_hours" in compute:
        max_wall_seconds = compute["max_wall_hours"] * 3600
    elif "max_wall_hours" in resources:
        max_wall_seconds = resources["max_wall_hours"] * 3600

    return CampaignSpec(
        name=data.get("name", Path(path).stem),
        runs=runs,
        store=data.get("store", "experiment.duckdb"),
        parallel=data.get("parallel", 1),
        webhook_url=data.get("webhook_url"),
        max_wall_seconds=max_wall_seconds,
    )


async def run_campaign(
    campaign_path: str | Path,
    parallel: int | None = None,
    device: str | None = None,
    webhook_url: str | None = None,
) -> dict[str, Any]:
    """Run a campaign from a YAML file."""
    spec = load_campaign(campaign_path)

    if parallel is not None:
        spec = CampaignSpec(
            name=spec.name,
            runs=spec.runs,
            store=spec.store,
            parallel=parallel,
            webhook_url=webhook_url or spec.webhook_url,
            max_wall_seconds=spec.max_wall_seconds,
        )
    elif device is not None or webhook_url is not None:
        # Override device for all runs if specified
        new_runs = []
        for run in spec.runs:
            new_runs.append(
                CampaignRun(
                    name=run.name,
                    profile=run.profile,
                    spec_file=run.spec_file,
                    overrides=run.overrides,
                    depends_on=run.depends_on,
                    device=device or run.device,
                    store=run.store,
                )
            )
        spec = CampaignSpec(
            name=spec.name,
            runs=new_runs,
            store=spec.store,
            parallel=spec.parallel,
            webhook_url=webhook_url or spec.webhook_url,
            max_wall_seconds=spec.max_wall_seconds,
        )

    runner = CampaignRunner(spec)
    return await runner.execute()
