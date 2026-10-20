#!/usr/bin/env python3
"""What does a run say while it happens? (TODO69)

The stage draws the run as a process — a timeline of its stages and the flow
through them — and both are drawn from the events the pipeline publishes.
This probe runs the demo campaign with a subscriber on the bus and prints
every event it saw: the stage, the verb, the counts the event carried and the
time it arrived.

The measured regime: the ``demo`` profile, digits, four credit arms and five
seeds per arm, on this machine. One round, forty events over 35.4 s: the six
opening stages speak in the first 0.02 s, the twenty measurements land in a
burst at 35.3 s, and the stages that ran a second round speak again at the
end. The 34.3 s between the training and the first measurement is what the
timeline view shades and names.

It informed the timeline view (``dashboard/src/stage/timeline.ts``) and the
``GET /api/events`` endpoint that feeds it.

Usage:
    uv run python scripts/probes/probe_dashboard_stages.py
"""

from __future__ import annotations

import argparse
import json
import logging
import tempfile
import time
from pathlib import Path

from computronium.experiment.execution.events import (
    STAGE_ACTIONS,
    PipelineEvent,
    get_event_bus,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def run_demo(store_path: Path) -> tuple[int, list[dict[str, object]]]:
    """Run the demo campaign, and return what the bus saw while it ran."""
    from computronium.experiment.surface.cli import (
        RUN_PROFILES,
        execute_spec,
        spec_from_profile,
    )

    seen: list[dict[str, object]] = []
    started = time.time()

    def record(event: PipelineEvent) -> None:
        seen.append({
            "at": round(time.time() - started, 3),
            "stage": event.stage,
            "action": STAGE_ACTIONS.get(event.stage, event.stage),
            "level": event.level,
            "message": event.message,
            "detail": dict(event.detail),
        })

    get_event_bus().subscribe(record)
    spec = spec_from_profile(RUN_PROFILES["demo"])
    code = execute_spec(spec, store_path=str(store_path))
    return code, seen


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--store",
        type=Path,
        default=None,
        help="Where the demo writes. A temporary store by default.",
    )
    args = parser.parse_args()

    store_path = (
        args.store or Path(tempfile.mkdtemp(prefix="probe-stages-")) / "demo.duckdb"
    )
    code, events = run_demo(store_path)

    print(f"exit={code} events={len(events)}")
    for event in events:
        print(json.dumps(event, sort_keys=True))

    stages: dict[str, int] = {}
    for event in events:
        stage = str(event["stage"])
        stages[stage] = stages.get(stage, 0) + 1
    print(json.dumps({"per_stage": stages}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
