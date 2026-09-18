"""ContinuousDaemon — headless discovery engine with a lifecycle API (TODO30 8.1).

Wraps the budgeted burst loop (``run_burst``) in a state machine with a
heartbeat artifact, an exclusive root lockfile, and a FastAPI surface:

- lifecycle: POST ``/control/{start,pause,resume,stop,skip_sleep}``
- state:     GET ``/state``
- streams:   WS ``/ws/telemetry`` (per-batch trainer metrics, drop-oldest)
             WS ``/ws/events``   (structured lifecycle events)

Boundary-based stop semantics (TODO30 §1.2): pause/stop take effect at
iteration boundaries only — a soft stop loses at most the in-flight cell's
compute, never corrupts state. The heartbeat is the only new artifact; the
KB/ledger/voids/defects streams are untouched (TODO30 §12.4–12.6).
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from collections import deque
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import psutil
from fastapi import FastAPI, HTTPException

from computronium.autoscientist.alerts import (
    Alert,
    WebhookDispatcher,
    cascade_alert,
    completion_alert,
)
from computronium.autoscientist.broad_map import (
    BroadMappingCampaign,
    BurstDriver,
    budget_from_args,
    build_sweep,
    run_burst,
    run_l1_maturation,
)
from computronium.autoscientist.objectives import (
    ObjectiveSpec,
    parse_objectives,
)
from computronium.autoscientist.report import generate_report
from computronium.utils import seed_everything

if TYPE_CHECKING:
    import argparse
    from collections.abc import AsyncIterator, Callable, Mapping

    from fastapi import WebSocket

logger = logging.getLogger("daemon")

_HEARTBEAT_INTERVAL_S = 2.0
_HEARTBEAT_NAME = "heartbeat.json"
_LOCKFILE_NAME = "continuous.lock"


class DaemonState(StrEnum):
    """TODO30 §1.2 state machine. No HALTED: stops are boundary-based."""

    IDLE = "idle"
    PROPOSING = "proposing"
    TRAINING = "training"
    SLEEPING = "sleeping"
    PAUSED = "paused"
    STOPPED = "stopped"


class DaemonAlreadyRunningError(RuntimeError):
    """A second daemon tried to own an already-locked campaign root."""


class TelemetryBridge:
    """Thread→asyncio drop-oldest bridge for best-effort streams (§3.1).

    ``publish`` never blocks or errors the producer (the training hot path);
    a slow or absent consumer loses events, never data (the KB is the record
    of truth — §12.6). Each ``stream`` is an independent consumer with its
    own drain point.
    """

    def __init__(self, maxlen: int = 256) -> None:
        self._buf: deque[dict[str, Any]] = deque(maxlen=maxlen)
        self._events: list[Any] = []  # asyncio.Event per attached consumer
        self._loop: Any = None  # asyncio.AbstractEventLoop, set on first attach

    def publish(self, record: Mapping[str, object]) -> None:
        item: dict[str, Any] = {
            k: (float(v) if isinstance(v, int | float) else v)
            for k, v in record.items()
        }
        self._buf.append(item)
        loop, events = self._loop, list(self._events)
        if loop is not None:
            for ev in events:
                loop.call_soon_threadsafe(ev.set)

    async def stream(self) -> AsyncIterator[dict[str, Any]]:
        import asyncio

        loop = asyncio.get_running_loop()
        wake = asyncio.Event()
        self._loop = loop
        self._events.append(wake)
        if self._buf:
            wake.set()  # events published before this consumer attached
        try:
            while True:
                await wake.wait()
                wake.clear()
                while self._buf:
                    yield self._buf.popleft()
        finally:
            self._events.remove(wake)


class PhaseTrackingDriver:
    """Wraps the stratified driver, flipping PROPOSING→TRAINING around the
    propose phase (training dominates walltime; proposal is sub-second)."""

    cells: int

    def __init__(
        self,
        inner: BurstDriver,
        on_phase: Callable[[DaemonState], None],
        on_proposals: Callable[[list[Any]], None] | None = None,
    ):
        self._inner = inner
        self._on_phase = on_phase
        self._on_proposals = on_proposals
        self.cells = inner.cells

    def has_novel(self) -> bool:
        return self._inner.has_novel()

    def propose_batch(
        self, n_proposals: int, recent_results: list[dict[str, object]] | None = None
    ) -> list[Any]:
        self._on_phase(DaemonState.PROPOSING)
        try:
            proposals = self._inner.propose_batch(n_proposals, recent_results)
            if self._on_proposals is not None:
                self._on_proposals(proposals)
            return proposals
        finally:
            self._on_phase(DaemonState.TRAINING)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)


class ContinuousDaemon:
    """Headless burst engine: state machine + heartbeat + lockfile + API."""

    def __init__(
        self,
        args: argparse.Namespace,
        *,
        port: int = 8940,
        sweep_factory: Callable[
            [argparse.Namespace], tuple[Any, BurstDriver]
        ] = build_sweep,
    ) -> None:
        self.args = args
        self.port = port
        self.root = Path(args.root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._lock_path = self.root / _LOCKFILE_NAME
        self._acquire_lockfile()
        self._sweep_factory = sweep_factory
        self.telemetry = TelemetryBridge()
        self.events = TelemetryBridge()
        self._state = DaemonState.IDLE
        self._state_lock = threading.Lock()
        self._started_at = time.time()
        self._burst: str | None = None
        self._cells_done = 0
        self._current_cell: str | None = None
        self._last_summary: dict[str, object] | None = None
        self._start = threading.Event()
        self._pause = threading.Event()
        self._stop = threading.Event()
        self._skip_sleep = threading.Event()
        self._worker: threading.Thread | None = None
        self._heartbeat_thread: threading.Thread | None = None
        self._campaign: BroadMappingCampaign | None = None
        self._dispatcher = WebhookDispatcher(getattr(args, "alert_webhook", None))
        self._best_accuracy: float | None = None
        # Multi-objective configuration (TODO31 Phase 1)
        obj_spec = getattr(args, "objectives", "accuracy,walltime_s")
        self._objectives: tuple[ObjectiveSpec, ...] = parse_objectives(obj_spec)

    # --- lifecycle commands (idempotent; wake every wait path) ---

    def start(self) -> None:
        if self.state is DaemonState.IDLE:
            self._start.set()

    def pause(self) -> None:
        self._pause.set()

    def resume(self) -> None:
        self._pause.clear()

    def skip_sleep(self) -> None:
        self._skip_sleep.set()

    def stop(self) -> None:
        self._stop.set()
        self._start.set()
        self._pause.clear()
        self._skip_sleep.set()

    @property
    def state(self) -> DaemonState:
        with self._state_lock:
            return self._state

    def _set_state(self, state: DaemonState) -> None:
        with self._state_lock:
            self._state = state
        self._write_heartbeat()
        self.events.publish({"kind": "state", "state": str(state.value)})

    # --- exclusive root ownership (TODO29 §12.5 absorbed) ---

    def _acquire_lockfile(self) -> None:
        try:
            fd = os.open(self._lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as e:
            msg = (
                f"{self._lock_path} already exists — a daemon already owns "
                f"{self.root} (delete the stale lockfile if the owner is dead)"
            )
            raise DaemonAlreadyRunningError(msg) from e
        with os.fdopen(fd, "w") as fh:
            fh.write(str(os.getpid()))

    def _release_lockfile(self) -> None:
        self._lock_path.unlink(missing_ok=True)

    # --- heartbeat (§2.2 liveness beacon) ---

    def _gpu_vram_mb(self) -> float | None:
        """Try to get GPU VRAM usage via pynvml."""
        try:
            import pynvml

            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            return info.used / (1024 * 1024)
        except ImportError, Exception:
            return None

    def _resource_metrics(self) -> dict[str, float] | None:
        """Collect CPU, RAM, and GPU VRAM usage for the daemon process."""
        try:
            proc = psutil.Process(os.getpid())
        except psutil.NoSuchProcess, psutil.AccessDenied:
            return None
        cpu_pct = proc.cpu_percent(interval=None)
        mem = proc.memory_info()
        ram_mb = mem.rss / (1024 * 1024)
        metrics = {"cpu_pct": round(cpu_pct, 1), "ram_mb": round(ram_mb, 1)}
        gpu_vram_mb = self._gpu_vram_mb()
        if gpu_vram_mb is not None:
            metrics["gpu_vram_mb"] = round(gpu_vram_mb, 1)
        return metrics

    def _heartbeat_payload(self) -> dict[str, object]:
        log_path = getattr(self.args, "log_path", None)
        resources = self._resource_metrics()
        payload: dict[str, object] = {
            "pid": os.getpid(),
            "state": str(self.state.value),
            "burst": self._burst,
            "cell_index": self._cells_done,
            "started_at": self._started_at,
            "updated_at": time.time(),
            "log_path": str(log_path) if log_path is not None else None,
            "current_cell": self._current_cell,
            "target_cells": getattr(self.args, "target_cells", None),
            "loop": bool(getattr(self.args, "loop", False)),
            "objectives": ",".join(o.name.value for o in self._objectives),
        }
        if resources:
            payload["resources"] = resources
        return payload

    def _write_heartbeat(self) -> None:
        path = self.root / _HEARTBEAT_NAME
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._heartbeat_payload()))
        tmp.replace(path)

    def _heartbeat_loop(self) -> None:
        while not self._stop.is_set() or self.state is DaemonState.STOPPED:
            self._write_heartbeat()
            self._stop.wait(_HEARTBEAT_INTERVAL_S)

    # --- burst worker ---

    def _gate(self) -> str | None:
        if self._stop.is_set():
            return "stopped"
        return "paused" if self._pause.is_set() else None

    def _sleep(self, seconds: float) -> None:
        """Interruptible inter-burst cooldown; Stop and Skip-Sleep both wake."""
        self._skip_sleep.clear()
        deadline = time.monotonic() + seconds
        while (
            time.monotonic() < deadline
            and not self._stop.is_set()
            and not self._skip_sleep.is_set()
        ):
            time.sleep(min(0.2, max(0.0, deadline - time.monotonic())))

    def _hold_paused(self) -> bool:
        """Hold after a boundary pause. Returns True when Stop was pressed."""
        self._set_state(DaemonState.PAUSED)
        while not self._stop.is_set():
            if not self._pause.is_set():
                return False
            time.sleep(0.2)
        return True

    def _run_worker(self) -> None:
        args = self.args
        seed_everything(args.seed, deterministic=False)
        campaign, driver = self._sweep_factory(args)
        campaign.step_callback = self.telemetry.publish
        self._campaign = campaign
        self.events.publish({"kind": "daemon_started", "root": str(self.root)})
        self._start.wait()
        while not self._stop.is_set():
            budget = budget_from_args(args)
            self._set_state(DaemonState.TRAINING)
            summary = run_burst(
                campaign,
                PhaseTrackingDriver(
                    driver, self._set_state, on_proposals=self._set_current_cell
                ),
                budget,
                max_iterations=args.max_iterations,
                gate=self._gate,
                on_cell_complete=self._on_cell_complete,
            )
            self._last_summary = summary
            self._cells_done = int(cast("int", summary["done"]))
            reason = str(summary["stop_reason"])
            self.events.publish({"kind": "burst_finished", "stop_reason": reason})
            try:
                self._check_alerts(summary, time.monotonic() - self._started_at)
            except Exception:  # noqa: BLE001 (alerts never kill the loop, §12.6)
                logger.exception("alert check failed")
            if reason == "paused" and not self._hold_paused():
                continue
            if reason == "target":
                self.events.publish({"kind": "campaign_complete"})
                break
            if reason == "exhausted":
                logger.info("Grid exhausted: continuous loop ends.")
                break
            if not args.loop or reason == "stopped":
                break
            self._set_state(DaemonState.SLEEPING)
            self._sleep(args.sleep)
        if args.maturation and not args.loop:
            run_l1_maturation(args, campaign, getattr(driver, "burst_tag", None))
        last = self._last_summary
        if last is not None and str(last.get("stop_reason")) == "target":
            report = generate_report(self.root)
            self.events.publish({"kind": "report", "path": str(report)})
        self._set_state(DaemonState.STOPPED)
        self._release_lockfile()
        self.events.publish({"kind": "daemon_stopped"})

    def _set_current_cell(self, proposals: list[Any]) -> None:
        """§3.1 coordinate card: the first proposal of the in-flight batch."""
        for proposal in proposals:
            axes = [
                str(getattr(proposal, field, None))
                for field in ("dynamics", "credit", "update")
            ]
            topology = str(
                (getattr(proposal, "geometry", None) or {}).get("topology_type", "")
            )
            self._current_cell = " × ".join([*axes, topology])
            return

    def _on_cell_complete(self, cell_index: int) -> None:
        """Update per-cell progress and write heartbeat for live tracking."""
        self._cells_done = cell_index
        self._write_heartbeat()

    def _check_alerts(self, summary: dict[str, object], elapsed_s: float) -> None:
        """§6: breakthrough / cascade / completion — daemon-side so they
        fire with no browser attached; toasts replay from the event log."""
        alerts: list[Alert] = []

        # Multi-objective breakthrough detection (TODO31 Phase 2)
        best_values = self._best_objectives_from_kb()
        if best_values:
            for obj_spec in self._objectives:
                obj_name = obj_spec.name.value
                if obj_name in best_values:
                    current_best = best_values[obj_name]
                    previous_best = getattr(self, f"_best_{obj_name}", None)
                    if previous_best is not None and self._is_improvement(
                        obj_spec.direction, current_best, previous_best
                    ):
                        margin = abs(current_best - previous_best)
                        # Configurable margin per objective (default 2% for accuracy)
                        threshold = (
                            0.02
                            if obj_name == "accuracy"
                            else (0.05 if obj_spec.direction == "minimize" else 0.02)
                        )
                        if margin >= threshold:
                            alert = Alert(
                                "breakthrough",
                                f"★ Breakthrough on {obj_name}: {current_best:.3f}",
                                f"{obj_name} improved from {previous_best:.3f} to {current_best:.3f} (margin={margin:.1%})",
                            )
                            alerts.append(alert)
                    setattr(self, f"_best_{obj_name}", current_best)

        for alert in (cascade_alert(summary), completion_alert(summary, elapsed_s)):
            if alert is not None:
                alerts.append(alert)
        for alert in alerts:
            self.events.publish({
                "kind": "alert",
                "alert_kind": alert.kind,
                "title": alert.title,
                "body": alert.body,
            })
            self._dispatcher.dispatch(alert)

    def _best_accuracy_from_kb(self) -> float | None:
        campaign = self._campaign
        kb = getattr(campaign, "knowledge_base", None) if campaign else None
        if kb is None:
            return None
        try:
            accuracies = [
                float(entry.metrics.get("final_accuracy", 0.0))
                for entry in kb.query()
                if str(entry.topic).startswith("experiment:")
            ]
        except Exception:  # noqa: BLE001 (telemetry must never kill the loop)
            return None
        return max(accuracies) if accuracies else None

    def _best_objectives_from_kb(self) -> dict[str, float] | None:
        """Query KB for best values of each configured objective."""
        campaign = self._campaign
        kb = getattr(campaign, "knowledge_base", None) if campaign else None
        if kb is None:
            return None
        try:
            # Collect all metrics for each objective
            obj_values: dict[str, list[float]] = {
                o.name.value: [] for o in self._objectives
            }
            for entry in kb.query():
                if not str(entry.topic).startswith("experiment:"):
                    continue
                metrics = entry.metrics
                for obj_spec in self._objectives:
                    name = obj_spec.name.value
                    if name in metrics:
                        val = metrics[name]
                        if isinstance(val, int | float):
                            obj_values[name].append(float(val))
            # Compute best per objective
            best: dict[str, float] = {}
            for obj_spec in self._objectives:
                name = obj_spec.name.value
                vals = obj_values[name]
                if vals:
                    best[name] = (
                        max(vals) if obj_spec.direction == "maximize" else min(vals)
                    )
            return best if best else None
        except Exception:  # noqa: BLE001
            return None

    @staticmethod
    def _is_improvement(direction: str, current: float, previous: float) -> bool:
        return current > previous if direction == "maximize" else current < previous

    def start_worker(self) -> None:
        if self._worker is not None:
            return
        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop, name="daemon-heartbeat", daemon=True
        )
        self._worker = threading.Thread(
            target=self._run_worker, name="daemon", daemon=True
        )
        self._heartbeat_thread.start()
        self._worker.start()

    def join_worker(self, timeout: float | None = None) -> bool:
        if self._worker is None:
            return True
        self._worker.join(timeout)
        return not self._worker.is_alive()

    # --- API surface (§1.3) ---

    def _control_post(self, app: FastAPI) -> None:
        daemon = self

        def _reject_if_stopped() -> None:
            if daemon.state is DaemonState.STOPPED:
                raise HTTPException(status_code=409, detail="daemon is stopped")

        @app.post("/control/start")
        def control_start() -> dict[str, str]:
            _reject_if_stopped()
            daemon.start()
            return {"state": str(daemon.state.value)}

        @app.post("/control/pause")
        def control_pause() -> dict[str, str]:
            _reject_if_stopped()
            daemon.pause()
            return {"state": str(daemon.state.value)}

        @app.post("/control/resume")
        def control_resume() -> dict[str, str]:
            _reject_if_stopped()
            daemon.resume()
            return {"state": str(daemon.state.value)}

        @app.post("/control/stop")
        def control_stop() -> dict[str, str]:
            daemon.stop()
            return {"state": str(daemon.state.value)}

        @app.post("/control/skip_sleep")
        def control_skip_sleep() -> dict[str, str]:
            _reject_if_stopped()
            daemon.skip_sleep()
            return {"state": str(daemon.state.value)}

    def build_app(self) -> FastAPI:
        daemon = self
        app = FastAPI(title="computronium daemon", version="TODO30")
        self._control_post(app)

        @app.get("/state")
        def state() -> dict[str, object]:
            return {
                **daemon._heartbeat_payload(),
                "uptime_s": round(time.time() - daemon._started_at, 1),
                "last_summary": daemon._last_summary,
            }

        @app.websocket("/ws/telemetry")
        async def ws_telemetry(websocket: WebSocket) -> None:
            await websocket.accept()
            async for record in daemon.telemetry.stream():
                await websocket.send_json(record)

        @app.websocket("/ws/events")
        async def ws_events(websocket: WebSocket) -> None:
            await websocket.accept()
            async for record in daemon.events.stream():
                await websocket.send_json(record)

        return app

    def serve(self) -> None:
        """Run the API server on the calling (main) thread until the worker
        finishes; SIGTERM routes through ``stop()`` for graceful shutdown."""
        import uvicorn

        self._install_sigterm()
        self.start_worker()
        server = uvicorn.Server(
            uvicorn.Config(
                self.build_app(),
                host="127.0.0.1",
                port=self.port,
                log_level="warning",
            )
        )

        def _watchdog() -> None:
            if self._worker is not None:
                self._worker.join()
            server.should_exit = True

        threading.Thread(target=_watchdog, name="daemon-watchdog", daemon=True).start()
        server.run()

    def _install_sigterm(self) -> None:
        import signal

        signal.signal(signal.SIGTERM, lambda *_: self.stop())
