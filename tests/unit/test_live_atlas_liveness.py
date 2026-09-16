"""Mission Control liveness + lifecycle logic (TODO30 8.3) — headless."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from computronium.visualization.live_atlas import (
    DaemonClient,
    lifecycle_buttons,
    liveness,
)

if TYPE_CHECKING:
    from pathlib import Path


def _heartbeat(root: Path, state: str, age_s: float = 0.0) -> float:
    import time

    updated = time.time() - age_s
    (root / "heartbeat.json").write_text(
        json.dumps({
            "pid": 4242,
            "state": state,
            "burst": "burst_0001",
            "cell_index": 12,
            "started_at": updated - 60.0,
            "updated_at": updated,
            "log_path": None,
        })
    )
    return updated


def test_offline_when_no_heartbeat(tmp_path: Path) -> None:
    badge = liveness(tmp_path, daemon_reachable=False)
    assert badge.label == "● OFFLINE"
    assert badge.color == "grey"


def test_connection_lost_on_stale_heartbeat(tmp_path: Path) -> None:
    _heartbeat(tmp_path, "training", age_s=30.0)
    badge = liveness(tmp_path, daemon_reachable=False)
    assert badge.label == "● CONNECTION LOST"
    assert badge.color == "red"


def test_fresh_heartbeat_drives_badge_per_state(tmp_path: Path) -> None:
    _heartbeat(tmp_path, "training")
    assert liveness(tmp_path, True).label == "● RUNNING"
    assert liveness(tmp_path, True).color == "green"
    _heartbeat(tmp_path, "sleeping")
    assert liveness(tmp_path, True).label == "● SLEEPING"
    _heartbeat(tmp_path, "paused")
    badge = liveness(tmp_path, True)
    assert badge.label == "● PAUSED" and badge.color == "amber"
    _heartbeat(tmp_path, "idle")
    assert "ready" in liveness(tmp_path, True).label


def test_unreachable_api_with_fresh_heartbeat_degrades_gracefully(
    tmp_path: Path,
) -> None:
    """Hybrid transport: landscape survives daemon death via artifacts."""
    _heartbeat(tmp_path, "training")
    badge = liveness(tmp_path, daemon_reachable=False)
    assert badge.label == "● RUNNING"
    assert "API unreachable" in badge.detail


def test_lifecycle_buttons_match_daemon_state() -> None:
    assert lifecycle_buttons(None) == ("start",)
    assert lifecycle_buttons("idle") == ("start",)
    assert lifecycle_buttons("stopped") == ("start",)
    assert lifecycle_buttons("training") == ("pause", "stop")
    assert lifecycle_buttons("sleeping") == ("pause", "stop")
    assert lifecycle_buttons("paused") == ("resume", "stop")


def test_daemon_client_unreachable_returns_none(tmp_path: Path) -> None:
    client = DaemonClient("http://127.0.0.1:1", timeout=0.2)
    assert client.get_state() is None
    assert client.control("pause") is False


def test_daemon_client_round_trips_live_daemon(tmp_path: Path) -> None:
    import threading
    from argparse import Namespace

    import uvicorn

    from computronium.autoscientist.daemon import ContinuousDaemon, DaemonState

    args = Namespace(
        root=tmp_path,
        budget=None,
        target_cells=10_000,  # unreachable: the burst stays live for the round-trip
        loop=False,
        sleep=0.0,
        max_iterations=1_000,
        seed=1,
        log_path=None,
        maturation=0,
    )

    class _Driver:
        cells = 1

        def propose_batch(self, n, recent_results=None):
            return []

        def has_novel(self):
            return True

    class _Campaign:
        def __init__(self):
            self.voids_path = tmp_path / "voids.jsonl"
            self.defects_path = None
            self.step_callback = None

        def run_iteration(self, n_experiments):
            import time

            time.sleep(0.05)  # keep the burst alive across the round-trip
            return [
                {"status": "completed", "proposal": {}, "walltime_s": 0.0}
                for _ in range(n_experiments)
            ]

        def save_checkpoint(self):
            pass

    daemon = ContinuousDaemon(
        args,
        sweep_factory=lambda _a: (_Campaign(), _Driver()),  # type: ignore[arg-type]
    )
    server = uvicorn.Server(
        uvicorn.Config(daemon.build_app(), host="127.0.0.1", port=0, log_level=0)
    )
    daemon.start_worker()
    daemon.start()
    threading.Thread(target=server.run, daemon=True).start()
    try:
        import time

        deadline = time.monotonic() + 10
        port = server.servers[0].sockets[0].getsockname()[1] if server.started else None
        while port is None and time.monotonic() < deadline:
            time.sleep(0.05)
            port = (
                server.servers[0].sockets[0].getsockname()[1]
                if server.started
                else None
            )
        # 3 s timeout: the spinning burst worker holds the GIL and can
        # starve a 1 s request under pytest.
        client = DaemonClient(f"http://127.0.0.1:{port}", timeout=3.0)
        state = client.get_state()
        assert state is not None
        assert int(state["pid"]) > 0  # type: ignore[call-overload]
        assert client.control("pause") is True
        deadline = time.monotonic() + 10
        while daemon.state is not DaemonState.PAUSED and time.monotonic() < deadline:
            time.sleep(0.05)
        assert daemon.state is DaemonState.PAUSED
        assert client.control("resume") is True
    finally:
        daemon.stop()
        import time

        deadline = time.monotonic() + 10
        while daemon.state is not DaemonState.STOPPED and time.monotonic() < deadline:
            time.sleep(0.05)


def test_telemetry_drain_extracts_loss() -> None:
    """§3.1: the WS consumer appends only numeric train_loss records."""
    import asyncio
    import json as _json
    from collections import deque

    from computronium.visualization.live_atlas import _drain

    class _FakeWS:
        def __init__(self, messages: list[str]) -> None:
            self._messages = iter(messages)

        def __aiter__(self):
            return self

        async def __anext__(self) -> str:
            try:
                return next(self._messages)
            except StopIteration as e:
                raise StopAsyncIteration from e

    async def _run() -> deque[float]:
        history: deque[float] = deque(maxlen=10)
        calls: list[int] = []
        await _drain(
            _FakeWS([
                _json.dumps({"loss": 1.5}),
                _json.dumps({"loss": "nan"}),  # non-numeric dropped
                _json.dumps({"other": 1.0}),
                _json.dumps({"loss": 0.8}),
            ]),
            history,
            lambda: calls.append(1),
        )
        assert len(calls) == 2
        return history

    history = asyncio.run(_run())
    assert list(history) == [1.5, 0.8]
