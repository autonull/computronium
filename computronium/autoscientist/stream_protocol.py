"""Single-topic stream protocol.

One WebSocket topic (``stream``) with a typed envelope; the daemon
handshake negotiates the protocol version via ``?v=``. Shared by the
daemon (producer) and any stream client — one data path.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

STREAM_TOPIC = "stream"
STREAM_PROTOCOL_VERSION = 1
STREAM_CLOSE_VERSION_MISMATCH = 4400

type StreamKind = Literal["telemetry", "events"]


class StreamEnvelope(BaseModel, frozen=True):
    """Typed envelope for every record on the ``stream`` topic."""

    model_config = ConfigDict(extra="forbid")

    v: int = STREAM_PROTOCOL_VERSION
    kind: StreamKind = "events"
    payload: dict[str, Any] = Field(default_factory=dict[str, Any])


def telemetry_envelope(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Wrap a raw telemetry record in the stream envelope."""
    return StreamEnvelope(kind="telemetry", payload=dict(payload)).model_dump()


def events_envelope(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Wrap a raw lifecycle-event record in the stream envelope."""
    return StreamEnvelope(kind="events", payload=dict(payload)).model_dump()


def parse_envelope(raw: object) -> StreamEnvelope | None:
    """Parse an enveloped record; ``None`` when malformed."""
    if not isinstance(raw, Mapping):
        return None
    try:
        return StreamEnvelope.model_validate(dict(raw))
    except ValidationError:
        return None


def is_supported(envelope: StreamEnvelope) -> bool:
    """Whether the envelope speaks the negotiated protocol version."""
    return envelope.v == STREAM_PROTOCOL_VERSION
