"""D1 dashboard metrics — stdlib counters + reservoir histograms → Prometheus text.

No heavy observability deps (structlog/OpenTelemetry deferred): thread-safe
registry rendering ``text/plain`` exposition for a ``/metrics`` endpoint.
"""

from __future__ import annotations

import random
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

_RESERVOIR_SIZE = 1024
_QUANTILES = (0.5, 0.95, 0.99)


def _format_labels(items: tuple[tuple[str, str], ...]) -> str:
    if not items:
        return ""
    inner = ",".join(f'{key}="{value}"' for key, value in items)
    return "{" + inner + "}"


class MetricsRegistry:
    """Thread-safe counters and reservoir-sampled latency summaries."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counters: dict[tuple[str, tuple[tuple[str, str], ...]], float] = {}
        self._reservoirs: dict[str, list[float]] = {}
        self._observed: dict[str, int] = {}
        self._rng = random.Random(0)  # ruff: ignore[suspicious-non-cryptographic-random-usage] (reservoir sampling, not crypto)

    def inc(
        self,
        name: str,
        value: float = 1.0,
        *,
        labels: Mapping[str, str] | None = None,
    ) -> None:
        """Increment a labeled counter."""
        key = (name, tuple(sorted((labels or {}).items())))
        with self._lock:
            self._counters[key] = self._counters.get(key, 0.0) + value

    def observe(self, name: str, value: float) -> None:
        """Record one sample into the named reservoir (Vitter algorithm R)."""
        with self._lock:
            seen = self._observed.get(name, 0) + 1
            self._observed[name] = seen
            bucket = self._reservoirs.setdefault(name, [])
            if len(bucket) < _RESERVOIR_SIZE:
                bucket.append(value)
            else:
                slot = self._rng.randrange(seen)
                if slot < _RESERVOIR_SIZE:
                    bucket[slot] = value

    def observe_seconds(self, name: str, seconds: float) -> None:
        """Record a duration under ``<name>_seconds``."""
        self.observe(name if name.endswith("_seconds") else f"{name}_seconds", seconds)

    def render_prometheus(self) -> str:
        """Render counters and latency summaries as Prometheus exposition text."""
        lines: list[str] = []
        with self._lock:
            for (name, label_items), value in sorted(self._counters.items()):
                lines.append(f"{name}{_format_labels(label_items)} {value:g}")
            for name in sorted(self._reservoirs):
                samples = self._reservoirs[name]
                total = self._observed.get(name, len(samples))
                lines.append(f"{name}_count {total}")
                if not samples:
                    continue
                lines.append(f"{name}_sum {sum(samples):g}")
                ordered = sorted(samples)
                for quantile in _QUANTILES:
                    index = min(len(ordered) - 1, int(quantile * len(ordered)))
                    lines.append(
                        f'{name}{{quantile="{quantile:g}"}} {ordered[index]:g}'
                    )
        return "\n".join(lines) + ("\n" if lines else "")


# Global registry (dashboard instruments via this instance)
metrics = MetricsRegistry()
