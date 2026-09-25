"""Alert threshold logic + best-effort webhook."""

from __future__ import annotations

from typing import TYPE_CHECKING

from computronium.autoscientist.alerts import (
    Alert,
    WebhookDispatcher,
    breakthrough_alert,
    cascade_alert,
    completion_alert,
)

if TYPE_CHECKING:
    import pytest


def test_breakthrough_fires_on_margin_and_suppresses_small_gains() -> None:
    assert breakthrough_alert(None, 0.95, "cell") is None
    assert breakthrough_alert(0.94, 0.95, "cell") is None  # 1% < 2% margin
    alert = breakthrough_alert(0.90, 0.95, "S:Digital × D:EnergyMin")
    assert alert is not None
    assert alert.kind == "breakthrough"
    assert "0.950" in alert.body and "0.900" in alert.body
    assert breakthrough_alert(0.96, 0.95, "cell") is None  # regression


def test_breakthrough_alert_carries_ceec_id() -> None:
    alert = breakthrough_alert(0.90, 0.95, "cell", experiment_id="exp_42")
    assert alert is not None and "exp_42" in alert.body


def test_cascade_alert_fires_above_30pct_and_suggests_never_halts() -> None:
    assert cascade_alert({"completed": 47, "failed": 3}) is None
    assert cascade_alert({"completed": 0, "failed": 0}) is None
    alert = cascade_alert({"completed": 32, "failed": 18})
    assert alert is not None
    assert alert.kind == "cascade"
    assert "18/50" in alert.body
    assert "human decides" in alert.body  # no auto-halt, ever


def test_completion_alert_only_on_target() -> None:
    assert completion_alert({"stop_reason": "soft"}, 3600.0) is None
    alert = completion_alert({"stop_reason": "target", "completed": 500}, 22320.0)
    assert alert is not None
    assert alert.kind == "completion"
    assert "500" in alert.body and "6h 12m" in alert.body


def test_webhook_dispatcher_no_url_is_noop() -> None:
    dispatcher = WebhookDispatcher(None)
    assert dispatcher.dispatch(Alert("cascade", "t", "b")) is False


def test_webhook_dispatcher_posts_json_and_swallows_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import urllib.request

    captured: dict[str, object] = {}

    class _Response:
        def read(self) -> bytes:
            return b"ok"

    def fake_urlopen(request: object, timeout: float) -> _Response:
        captured["url"] = getattr(request, "full_url", None)
        captured["data"] = getattr(request, "data", None)
        return _Response()

    def failing_urlopen(request: object, timeout: float) -> object:
        raise OSError("connection refused")

    dispatcher = WebhookDispatcher("https://hooks.example/x")
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    assert dispatcher.dispatch(Alert("breakthrough", "★ t", "b")) is True
    assert captured["url"] == "https://hooks.example/x"
    payload = captured["data"]
    assert isinstance(payload, bytes) and b"t" in payload and b"b" in payload

    monkeypatch.setattr(urllib.request, "urlopen", failing_urlopen)
    assert dispatcher.dispatch(Alert("cascade", "t", "b")) is False
