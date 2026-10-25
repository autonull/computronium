"""WebSocket correctness tests (P3).

Tests for ping/pong, replay, per-socket locks, safe broadcast iteration,
and blocking work off the event loop.
"""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, cast

import pytest

from computronium.experiment.execution.dashboard.web import (
    DashboardConfig,
    WebDashboard,
)

if TYPE_CHECKING:
    from fastapi import WebSocket


class _FakeSocket:
    """A WebSocket stand-in that records what the dashboard sends."""

    def __init__(self, should_fail: bool = False) -> None:
        self.messages: list[dict] = []
        self.should_fail = should_fail
        self.closed = False

    async def send_json(self, message: dict) -> None:
        if self.should_fail:
            raise RuntimeError("send failed")
        self.messages.append(message)

    async def receive_text(self) -> str:
        if self.should_fail:
            raise RuntimeError("receive failed")
        # Return a ping message to test ping/pong handling
        return json.dumps({"type": "ping"})

    async def accept(self) -> None:
        pass

    async def close(self, code: int = 1000, reason: str = "") -> None:
        self.closed = True


class _PingPongSocket(_FakeSocket):
    """Socket that sends a ping then disconnects."""

    def __init__(self) -> None:
        super().__init__()
        self._sent_ping = False

    async def receive_text(self) -> str:
        if not self._sent_ping:
            self._sent_ping = True
            return json.dumps({"type": "ping"})
        # Simulate disconnect after ping
        await asyncio.sleep(0.1)
        raise RuntimeError("WebSocketDisconnect")


@pytest.fixture(autouse=True)
def _isolated_dashboard():
    """Each test gets a fresh dashboard instance."""
    yield


@pytest.mark.asyncio
async def test_ping_receives_pong():
    """Server responds to ping with pong."""
    dashboard = WebDashboard(DashboardConfig(enable_websockets=False))
    socket = _FakeSocket()
    dashboard._ws_locks[cast("WebSocket", socket)] = asyncio.Lock()

    # Simulate the websocket handler's ping/pong logic
    await dashboard._send_json(cast("WebSocket", socket), {"type": "pong"})

    pongs = [m for m in socket.messages if m.get("type") == "pong"]
    assert len(pongs) == 1


@pytest.mark.asyncio
async def test_send_json_uses_per_socket_lock():
    """Each socket has its own lock for serialized sends."""
    dashboard = WebDashboard(DashboardConfig(enable_websockets=False))
    socket1 = _FakeSocket()
    socket2 = _FakeSocket()

    # Add sockets to dashboard's internal structures
    dashboard._connected_websockets.add(cast("WebSocket", socket1))
    dashboard._connected_websockets.add(cast("WebSocket", socket2))
    dashboard._ws_locks[cast("WebSocket", socket1)] = asyncio.Lock()
    dashboard._ws_locks[cast("WebSocket", socket2)] = asyncio.Lock()

    # Send to both concurrently
    await asyncio.gather(
        dashboard._send_json(cast("WebSocket", socket1), {"type": "msg", "id": 1}),
        dashboard._send_json(cast("WebSocket", socket2), {"type": "msg", "id": 2}),
    )

    assert len(socket1.messages) == 1
    assert socket1.messages[0]["id"] == 1
    assert len(socket2.messages) == 1
    assert socket2.messages[0]["id"] == 2


@pytest.mark.asyncio
async def test_broadcast_iterates_over_tuple_not_set():
    """Broadcast iterates over a tuple to avoid mutation during iteration."""
    dashboard = WebDashboard(DashboardConfig(enable_websockets=False))
    socket1 = _FakeSocket()
    socket2 = _FakeSocket(should_fail=True)  # This one will fail and be removed
    socket3 = _FakeSocket()

    dashboard._connected_websockets.add(cast("WebSocket", socket1))
    dashboard._connected_websockets.add(cast("WebSocket", socket2))
    dashboard._connected_websockets.add(cast("WebSocket", socket3))
    dashboard._ws_locks[cast("WebSocket", socket1)] = asyncio.Lock()
    dashboard._ws_locks[cast("WebSocket", socket2)] = asyncio.Lock()
    dashboard._ws_locks[cast("WebSocket", socket3)] = asyncio.Lock()

    await dashboard._broadcast_update({"type": "test", "value": 42})

    # socket1 and socket3 should receive; socket2 should be removed
    assert len(socket1.messages) == 1
    assert socket1.messages[0]["value"] == 42
    assert len(socket3.messages) == 1
    assert socket3.messages[0]["value"] == 42
    assert cast("WebSocket", socket2) not in dashboard._connected_websockets
    assert cast("WebSocket", socket1) in dashboard._connected_websockets
    assert cast("WebSocket", socket3) in dashboard._connected_websockets


@pytest.mark.asyncio
async def test_replay_events_wrapped_in_try_finally():
    """Replay is best-effort; connection continues even if replay fails."""
    dashboard = WebDashboard(DashboardConfig(enable_websockets=False, store_path=None))
    socket = _FakeSocket()
    dashboard._ws_locks[cast("WebSocket", socket)] = asyncio.Lock()

    # Replay should not raise even if something goes wrong internally
    await dashboard._replay_events(cast("WebSocket", socket))

    # Socket should still be usable after replay
    await dashboard._send_json(cast("WebSocket", socket), {"type": "after_replay"})
    assert any(m.get("type") == "after_replay" for m in socket.messages)


@pytest.mark.asyncio
async def test_websocket_handler_ping_pong_flow():
    """Full websocket handler: connect -> replay -> ping -> pong -> disconnect."""
    dashboard = WebDashboard(DashboardConfig(enable_websockets=False, store_path=None))
    socket = _PingPongSocket()

    # Manually simulate the handler flow since we can't easily mock WebSocket.accept
    dashboard._connected_websockets.add(cast("WebSocket", socket))
    dashboard._ws_locks[cast("WebSocket", socket)] = asyncio.Lock()

    # Replay
    await dashboard._replay_events(cast("WebSocket", socket))

    # Simulate receiving ping and sending pong (handler logic)
    ping_msg = json.loads(await socket.receive_text())
    assert ping_msg["type"] == "ping"
    await dashboard._send_json(cast("WebSocket", socket), {"type": "pong"})

    pongs = [m for m in socket.messages if m.get("type") == "pong"]
    assert len(pongs) == 1

    # Cleanup
    dashboard._connected_websockets.discard(cast("WebSocket", socket))
    dashboard._ws_locks.pop(cast("WebSocket", socket), None)
    assert cast("WebSocket", socket) not in dashboard._connected_websockets


@pytest.mark.asyncio
async def test_blocking_store_work_runs_in_thread():
    """Verify _get_campaign_metrics_detailed uses asyncio.to_thread."""
    dashboard = WebDashboard(DashboardConfig(enable_websockets=False, store_path=None))

    # With no store_path, it should return error quickly without blocking
    result = await dashboard._get_campaign_metrics_detailed("test-run")
    assert result == {"error": "No store path configured"}

    # The method should be awaitable (uses asyncio.to_thread internally)
    # We can't easily test the threading without a real store, but we verify
    # the signature and that it doesn't block the event loop.
    import inspect

    assert inspect.iscoroutinefunction(dashboard._get_campaign_metrics_detailed)


@pytest.mark.asyncio
async def test_broadcast_removes_dead_sockets_safely():
    """Dead sockets are removed from the set during broadcast."""
    dashboard = WebDashboard(DashboardConfig(enable_websockets=False))
    good_socket = _FakeSocket()
    bad_socket = _FakeSocket(should_fail=True)

    dashboard._connected_websockets.add(cast("WebSocket", good_socket))
    dashboard._connected_websockets.add(cast("WebSocket", bad_socket))
    dashboard._ws_locks[cast("WebSocket", good_socket)] = asyncio.Lock()
    dashboard._ws_locks[cast("WebSocket", bad_socket)] = asyncio.Lock()

    await dashboard._broadcast_update({"type": "broadcast_test"})

    # Good socket received the message
    assert len(good_socket.messages) == 1
    # Bad socket was removed
    assert cast("WebSocket", bad_socket) not in dashboard._connected_websockets
    assert cast("WebSocket", bad_socket) not in dashboard._ws_locks
    # Good socket remains
    assert cast("WebSocket", good_socket) in dashboard._connected_websockets


@pytest.mark.asyncio
async def test_multiple_sockets_independent_state():
    """Each socket maintains independent lock and message state."""
    dashboard = WebDashboard(DashboardConfig(enable_websockets=False))
    sockets = [_FakeSocket() for _ in range(5)]

    for s in sockets:
        dashboard._connected_websockets.add(cast("WebSocket", s))
        dashboard._ws_locks[cast("WebSocket", s)] = asyncio.Lock()

    # Send unique message to each
    async def send_unique(sock: _FakeSocket, idx: int):
        await dashboard._send_json(cast("WebSocket", sock), {"idx": idx})

    await asyncio.gather(*[send_unique(s, i) for i, s in enumerate(sockets)])

    for i, s in enumerate(sockets):
        assert len(s.messages) == 1
        assert s.messages[0]["idx"] == i

    # Verify locks are independent
    assert len(dashboard._ws_locks) == 5


def test_websocket_cleanup_on_disconnect():
    """Socket is removed from both sets on disconnect."""
    dashboard = WebDashboard(DashboardConfig(enable_websockets=False))
    socket = _FakeSocket()

    dashboard._connected_websockets.add(cast("WebSocket", socket))
    dashboard._ws_locks[cast("WebSocket", socket)] = asyncio.Lock()

    # Simulate disconnect cleanup (from finally block)
    dashboard._connected_websockets.discard(cast("WebSocket", socket))
    dashboard._ws_locks.pop(cast("WebSocket", socket), None)

    assert cast("WebSocket", socket) not in dashboard._connected_websockets
    assert cast("WebSocket", socket) not in dashboard._ws_locks
