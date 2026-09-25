"""ContinuousDaemon state machine (TODO30 8.1): boundary-based lifecycle,
heartbeat, exclusive root lockfile, and the REST surface — all with fake
sweeps, no training."""

from __future__ import annotations

import time
from argparse import Namespace
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient

from computronium.autoscientist.daemon import (
    ContinuousDaemon,
    DaemonAlreadyRunningError,
    DaemonState,
)

if TYPE_CHECKING:
    from collections.abc import Callable


def _wait_until(pred: Callable[[], bool], timeout: float = 10.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if pred():
            return
        time.sleep(0.05)
    pytest.fail("condition not met within timeout")


class _FakeDriver:
    cells = 2

    def propose_batch(self, n_proposals, recent_results=None):  # noqa: ANN001, ARG002
        return []

    def has_novel(self) -> bool:
        return True


class _FakeCampaign:
    def __init__(self, root: Path) -> None:
        self.voids_path = root / "structural_voids.jsonl"
        self.defects_path = None
        self.step_callback = None

    def run_iteration(self, n_experiments: int) -> list[dict[str, object]]:
        return [
            {
                "status": "completed",
                "proposal": {"dynamics": "Fake"},
                "walltime_s": 0.01,
            }
            for _ in range(n_experiments)
        ]

    def save_checkpoint(self) -> None:
        pass


def _args(root: Path, **overrides: object) -> Namespace:
    defaults: dict[str, object] = {
        "root": root,
        "budget": None,
        "target_cells": 2,
        "maturation": 0,
        "loop": True,
        "sleep": 0.05,
        "max_iterations": 10,
        "seed": 1,
        "log_path": None,
    }
    defaults.update(overrides)
    return Namespace(**defaults)


def _make(root: Path, **overrides: object) -> ContinuousDaemon:
    args = _args(root, **overrides)
    return ContinuousDaemon(
        args,
        sweep_factory=lambda a: (_FakeCampaign(Path(a.root)), _FakeDriver()),
    )


def _final_state(daemon: ContinuousDaemon) -> None:
    _wait_until(lambda: daemon.state is DaemonState.STOPPED)
    daemon.join_worker(timeout=5)


def test_full_lifecycle_target_to_stopped(tmp_path: Path) -> None:
    daemon = _make(tmp_path)
    assert daemon.state is DaemonState.IDLE
    daemon.start_worker()
    daemon.start()
    _final_state(daemon)
    assert daemon._last_summary is not None
    assert daemon._last_summary["stop_reason"] == "target"
    assert daemon._cells_done == 2
    assert not (tmp_path / "continuous.lock").exists()


def test_pause_holds_at_boundary_then_resume_completes(tmp_path: Path) -> None:
    daemon = _make(tmp_path)
    daemon.pause()  # set before start: the first boundary gate fires "paused"
    daemon.start_worker()
    daemon.start()
    _wait_until(lambda: daemon.state is DaemonState.PAUSED)
    heartbeat = (tmp_path / "heartbeat.json").read_text()
    assert '"paused"' in heartbeat
    daemon.resume()
    _final_state(daemon)
    assert daemon._last_summary is not None
    assert daemon._last_summary["stop_reason"] == "target"


def test_stop_from_paused_is_graceful(tmp_path: Path) -> None:
    daemon = _make(tmp_path)
    daemon.pause()
    daemon.start_worker()
    daemon.start()
    _wait_until(lambda: daemon.state is DaemonState.PAUSED)
    daemon.stop()
    _final_state(daemon)
    assert not (tmp_path / "continuous.lock").exists()


def test_heartbeat_written_throughout(tmp_path: Path) -> None:
    daemon = _make(tmp_path)
    daemon.start_worker()
    heartbeat = tmp_path / "heartbeat.json"
    _wait_until(heartbeat.exists)
    daemon.stop()
    _final_state(daemon)


def test_second_daemon_on_same_root_refused(tmp_path: Path) -> None:
    daemon = _make(tmp_path)
    with pytest.raises(DaemonAlreadyRunningError):
        _make(tmp_path)
    daemon.stop()
    daemon.start_worker()
    _final_state(daemon)
    # lock released after a graceful stop: a fresh daemon can own the root
    second = _make(tmp_path)
    second.stop()


def test_api_state_and_controls(tmp_path: Path) -> None:
    daemon = _make(tmp_path)
    daemon.start_worker()
    try:
        client = TestClient(daemon.build_app())
        state = client.get("/state").json()
        assert state["state"] == DaemonState.IDLE.value
        assert state["pid"] > 0
        assert client.post("/control/pause").status_code == 200
        assert client.post("/control/start").status_code == 200
        _wait_until(lambda: daemon.state is DaemonState.PAUSED)
        assert client.post("/control/resume").status_code == 200
        assert client.post("/control/skip_sleep").status_code == 200
        assert client.post("/control/stop").status_code == 200
    finally:
        _final_state(daemon)


def test_events_stream_publishes_lifecycle(tmp_path: Path) -> None:
    daemon = _make(tmp_path)
    daemon.start_worker()
    daemon.start()
    _final_state(daemon)
    kinds = [r["kind"] for r in daemon.events._buf]
    assert "daemon_started" in kinds
    assert "burst_finished" in kinds
    assert "campaign_complete" in kinds
    assert "daemon_stopped" in kinds


def test_telemetry_bridge_drop_oldest_and_threadsafe() -> None:
    import asyncio

    from computronium.autoscientist.daemon import TelemetryBridge

    async def _run() -> list[dict[str, object]]:
        bridge = TelemetryBridge(maxlen=3)
        for i in range(5):
            bridge.publish({"loss": float(i)})
        gen = bridge.stream()
        assert await gen.__anext__() == {"loss": 2.0}  # two oldest dropped
        assert await gen.__anext__() == {"loss": 3.0}
        assert await gen.__anext__() == {"loss": 4.0}
        bridge.publish({"loss": 5.0})
        assert await gen.__anext__() == {"loss": 5.0}
        return []

    asyncio.run(_run())


def test_trainer_step_callback_is_optional_and_observed(tmp_path: Path) -> None:
    """8.2 hook contract: no callback → identical behavior; with callback →
    one call per batch, never blocking."""
    import torch

    torch.set_num_threads(1)
    from computronium import (
        BackpropCredit,
        DigitalSubstrate,
        EuclideanUpdate,
        FeedforwardGeometry,
        GeometryConfig,
        InstantaneousDynamics,
        ParameterUpdateConfig,
        StateDynamicsConfig,
        SubstrateConfig,
        SystemTrainer,
        SystemTrainerConfig,
        compose_system,
    )

    def _system():
        torch.manual_seed(7)  # weights init from the global RNG pre-trainer-seed
        return compose_system(
            substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
            geometry=FeedforwardGeometry(
                GeometryConfig.feedforward(input_dim=8, output_dim=3, hidden_dims=(8,))
            ),
            dynamics=InstantaneousDynamics(StateDynamicsConfig.instantaneous()),
            credit=BackpropCredit(),
            update=EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=0.05)),
        )

    from computronium.utils import seed_everything

    seed_everything(7, deterministic=False)
    g = torch.Generator().manual_seed(7)
    batches = [
        (torch.randn(4, 8, generator=g), torch.randint(0, 3, (4,), generator=g))
        for _ in range(3)
    ]

    def _train(
        callback: object,
    ) -> tuple[list[dict[str, float]], list[dict[str, float]]]:
        seen: list[dict[str, float]] = []
        trainer = SystemTrainer(
            _system(),
            SystemTrainerConfig(max_epochs=1, batch_size=4, limit_train_batches=3),
            batches,
            step_callback=(lambda m: seen.append(dict(m))) if callback else None,
        )
        history = trainer.fit()
        trainer.close()
        return history, seen

    bare_history, bare_seen = _train(None)
    hooked_history, hooked_seen = _train(True)
    assert bare_seen == []
    assert len(hooked_seen) == 3
    assert all("loss" in m for m in hooked_seen)
    assert bare_history[-1]["train_loss"] == pytest.approx(
        hooked_history[-1]["train_loss"], rel=1e-6
    )


# Thread-safety smoke: publish from a non-event-loop thread must not raise.
def test_telemetry_publish_without_consumer_never_raises() -> None:
    from computronium.autoscientist.daemon import TelemetryBridge

    bridge = TelemetryBridge()
    bridge.publish({"loss": 1.0})  # no loop attached: buffered only
    time.sleep(0.01)
    assert bridge._buf[0] == {"loss": 1.0}


def test_ws_stream_multiplexes_telemetry_and_events(tmp_path: Path) -> None:
    """Single ``/ws/stream`` topic carries both kinds in typed envelopes."""
    from computronium.autoscientist.stream_protocol import parse_envelope

    daemon = _make(tmp_path)
    daemon.telemetry.publish({"train_loss": 0.5})
    daemon.events.publish({"kind": "daemon_started"})
    try:
        client = TestClient(daemon.build_app())
        with client.websocket_connect("/ws/stream?v=1") as ws:
            first = parse_envelope(ws.receive_json())
            second = parse_envelope(ws.receive_json())
        assert first is not None and second is not None
        assert {first.kind, second.kind} == {"telemetry", "events"}
    finally:
        daemon.stop()


def test_ws_stream_rejects_unknown_version(tmp_path: Path) -> None:
    from starlette.websockets import WebSocketDisconnect

    from computronium.autoscientist.stream_protocol import (
        STREAM_CLOSE_VERSION_MISMATCH,
    )

    daemon = _make(tmp_path)
    try:
        client = TestClient(daemon.build_app())
        with (
            client.websocket_connect("/ws/stream?v=999") as ws,
            pytest.raises(WebSocketDisconnect) as exc,
        ):
            ws.receive_json()
        assert exc.value.code == STREAM_CLOSE_VERSION_MISMATCH
    finally:
        daemon.stop()
