"""Alerting (TODO30 8.7) — daemon-side significance detection + webhook
dispatch. Fires when no browser is attached; the dashboard replays toasts
from the event stream. Alerts are notifications only — the dashboard and
the daemon both leave the run/stop decision to the human (§9)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from collections.abc import Mapping

logger = logging.getLogger("alerts")

type AlertKind = Literal["breakthrough", "cascade", "completion"]

BREAKTHROUGH_MARGIN = 0.02  # ≥2% accuracy gain over the previous best
CASCADE_FAILURE_SHARE = 0.30  # >30% of a burst failed/diverged


@dataclass(frozen=True, slots=True)
class Alert:
    kind: AlertKind
    title: str
    body: str


def breakthrough_alert(
    previous_best: float | None,
    cell_accuracy: float,
    cell_key: str,
    experiment_id: str | None = None,
) -> Alert | None:
    """§6.1 — a cell expanded the front beyond the configurable margin."""
    if previous_best is None or cell_accuracy <= previous_best:
        return None
    if cell_accuracy - previous_best < BREAKTHROUGH_MARGIN:
        return None
    gain = f"{cell_accuracy:.3f} vs previous best {previous_best:.3f}"
    tail = f" (CEEC experiment {experiment_id})" if experiment_id else ""
    return Alert(
        "breakthrough",
        f"★ Breakthrough: {cell_key}",
        f"val_acc {gain}; front expanded by {cell_accuracy - previous_best:.1%}{tail}",
    )


def cascade_alert(summary: Mapping[str, object]) -> Alert | None:
    """§6.2 — >30% of a burst's executed cells failed (defects/divergence).
    The alert suggests, never auto-halts."""
    completed = summary.get("completed", 0)
    failed = summary.get("failed", 0)
    if not isinstance(completed, int | float) or not isinstance(failed, int | float):
        return None
    executed = int(completed) + int(failed)
    if executed == 0 or failed / executed <= CASCADE_FAILURE_SHARE:
        return None
    return Alert(
        "cascade",
        "Cascade failure risk",
        f"{int(failed)}/{executed} cells in the last burst failed. "
        "Consider halting (Stop) — the human decides.",
    )


def completion_alert(summary: Mapping[str, object], walltime_s: float) -> Alert | None:
    """§6.3 — target reached or budget expired."""
    stop_reason = summary.get("stop_reason")
    if stop_reason != "target":
        return None
    completed = summary.get("completed", 0)
    minutes, seconds = divmod(int(walltime_s), 60)
    hours, minutes = divmod(minutes, 60)
    elapsed = f"{hours}h {minutes:02d}m" if hours else f"{minutes}m {seconds:02d}s"
    return Alert(
        "completion",
        "🏁 Campaign complete",
        f"{completed} cells measured in {elapsed}. Report ready for generation (§7.3).",
    )


class WebhookDispatcher:
    """Best-effort JSON webhook (Slack/Discord-style). Never raises: a
    webhook is telemetry, not a control path."""

    def __init__(self, url: str | None, timeout: float = 5.0) -> None:
        self._url = url
        self._timeout = timeout

    def dispatch(self, alert: Alert) -> bool:
        import json
        import urllib.request

        if self._url is None:
            return False
        payload = json.dumps({
            "content": f"{alert.title}\n{alert.body}",  # Discord-style
            "text": f"{alert.title}\n{alert.body}",  # Slack-style
        }).encode()
        request = urllib.request.Request(  # ruff: ignore[suspicious-url-open-usage] (operator-supplied URL)
            self._url,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        try:
            urllib.request.urlopen(  # ruff: ignore[suspicious-url-open-usage] (operator-supplied URL)
                request, timeout=self._timeout
            ).read()
        except OSError as e:
            logger.warning("alert webhook failed: %s", e)
            return False
        return True
