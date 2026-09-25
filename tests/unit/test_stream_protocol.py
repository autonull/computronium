"""Single-topic stream protocol + hash navigation helpers (GAME.todo7 Phase 2)."""

from __future__ import annotations

from computronium.autoscientist.stream_protocol import (
    STREAM_PROTOCOL_VERSION,
    STREAM_TOPIC,
    events_envelope,
    is_supported,
    parse_envelope,
    telemetry_envelope,
)
from computronium.ui.navigation import format_hash, parse_hash


def test_stream_topic_and_version() -> None:
    assert STREAM_TOPIC == "stream"
    assert STREAM_PROTOCOL_VERSION == 1


def test_envelope_round_trip() -> None:
    raw = {"kind": "alert", "title": "boom"}
    envelope = parse_envelope(events_envelope(raw))
    assert envelope is not None
    assert envelope.kind == "events"
    assert envelope.payload["title"] == "boom"
    assert is_supported(envelope)

    tele = parse_envelope(telemetry_envelope({"train_loss": 0.5}))
    assert tele is not None
    assert tele.kind == "telemetry"
    assert tele.payload["train_loss"] == 0.5


def test_parse_envelope_rejects_garbage() -> None:
    assert parse_envelope(None) is None
    assert parse_envelope("stream") is None
    assert parse_envelope({"nope": True}) is None
    assert parse_envelope({"v": 1, "kind": "bogus", "payload": {}}) is None


def test_unsupported_version_detected() -> None:
    envelope = parse_envelope({"v": 999, "kind": "events", "payload": {}})
    assert envelope is not None
    assert not is_supported(envelope)


def test_hash_round_trip() -> None:
    assert parse_hash("#atlas/preview") == ("atlas", "preview")
    assert parse_hash("monitor") == ("monitor", None)
    assert format_hash("atlas", "preview") == "#atlas/preview"
    assert format_hash("monitor") == "#monitor"


def test_parse_hash_edge_cases() -> None:
    assert parse_hash(None) == (None, None)
    assert parse_hash("") == (None, None)
    assert parse_hash("#") == (None, None)
    assert parse_hash("#/") == (None, None)
    assert parse_hash("#atlas/") == ("atlas", None)
    assert parse_hash("  #defects/episodes  ") == ("defects", "episodes")
