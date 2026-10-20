"""The demo run's events, as the dashboard sees them (TODO69).

The flow view draws the run's cells through the stages, so it needs to know
what the stages actually report: the counts each one carries, and how many
events each one leaves. This runs the demo campaign and prints the events.

Usage:
    uv run python scripts/probes/probe_demo_events.py
"""

from __future__ import annotations

import json
import logging
import tempfile
from pathlib import Path

from computronium.experiment.execution.events import PipelineEventBus, set_event_bus

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def main() -> int:
    """Run the demo campaign and print the events it left."""
    from computronium.experiment.surface.cli import (
        RUN_PROFILES,
        execute_spec,
        spec_from_profile,
    )

    frames: list[dict] = []
    bus = PipelineEventBus()
    bus.subscribe(lambda event: frames.append(event.to_message()))
    set_event_bus(bus)

    scratch = Path(tempfile.mkdtemp(prefix="computronium-probe-"))
    store = scratch / "probe.duckdb"
    spec = spec_from_profile(RUN_PROFILES["demo"])
    execute_spec(spec, store_path=str(store))

    print(f"\n{len(frames)} events\n")
    for frame in frames:
        print(
            json.dumps({
                "stage": frame["stage"],
                "message": frame["message"],
                "detail": frame["detail"],
            })
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
