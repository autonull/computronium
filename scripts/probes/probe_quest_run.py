#!/usr/bin/env python3
"""Does the quest's run answer the question? (TODO68)

The quest verb used to write a file and stop: the question was on disk and
nothing was going to measure the cell. This probe runs the whole loop — the
registration, the queued campaign, the run it writes into — and reads what
the store says afterwards: the new run's status, the records it measured,
and what the measurement actually cost against the budget the quest asked
for.

Usage:
    uv run python scripts/probes/probe_quest_run.py
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import tempfile
import time
from pathlib import Path

from dashboard_probe import build_store

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# The cell the quest asks about: legal, and nobody measured it.
QUEST_CELL = {
    "substrate": "digital",
    "geometry": "feedforward",
    "dynamics": "instantaneous",
    "plasticity": "null",
    "credit": "pepita",
    "update": "adam",
}


async def _quest(store_path: Path, registry: Path, run_id: str, seeds: int) -> dict:
    """Register the question and queue the run that would answer it."""
    from computronium.experiment.execution.campaign_queue import CampaignQueue
    from computronium.experiment.execution.dashboard.web import (
        CellAction,
        DashboardConfig,
        WebDashboard,
    )

    queue = CampaignQueue(max_concurrent=1)
    dashboard = WebDashboard(
        DashboardConfig(
            store_path=str(store_path),
            registration_dir=registry,
            campaign_queue=queue,
        )
    )
    body = CellAction(coordinate=QUEST_CELL, min_seeds=seeds)
    result = await dashboard._adopt_quest(run_id, body)
    return {"result": result, "queue": queue}


async def _await_campaign(queue, timeout: float = 300.0) -> list:
    """Wait for every campaign to finish."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        entries = await queue.list_campaigns()
        if entries and all(
            entry.status.value in {"completed", "failed", "cancelled"}
            for entry in entries
        ):
            return entries
        await asyncio.sleep(1.0)
    return await queue.list_campaigns()


def _read_store(store_path: Path) -> list[dict]:
    """What the store holds, run by run."""
    from computronium.experiment.evidence.store import RecordStore, StoreConfig

    with RecordStore(StoreConfig(path=store_path)) as store:
        runs = []
        for run in store.query_runs():
            records = list(store.query_records(run_id=run.run_id))
            walltimes = [
                float(r.payload["walltime_s"])
                for r in records
                if isinstance(r.payload.get("walltime_s"), int | float)
            ]
            elapsed = None
            if run.started_at and run.finished_at:
                elapsed = (run.finished_at - run.started_at).total_seconds()
            runs.append({
                "run_id": run.run_id,
                "status": run.status,
                "records": len(records),
                "measured_s": sum(walltimes),
                "walltime_s": elapsed,
                "launch_overhead_s": (
                    round(elapsed - sum(walltimes), 2) if elapsed is not None else None
                ),
                "credits": sorted({r.credit for r in records}),
            })
        return runs


async def probe(
    store_path: Path,
    registry: Path,
    run_id: str,
    seeds: int,
) -> dict[str, object]:
    """Run the quest, and read what the store says afterwards."""
    started = time.time()
    quest = await _quest(store_path, registry, run_id, seeds)
    result = quest["result"]
    payload = {
        key: value for key, value in result.payload.items() if key != "registration"
    }
    logger.info("quest answered: %s", json.dumps(payload, default=str))

    entries = await _await_campaign(quest["queue"])
    campaigns = [
        {"name": e.spec.name, "status": e.status.value, "error": e.error}
        for e in entries
    ]
    runs = _read_store(store_path)
    elapsed = time.time() - started

    return {
        "quest": payload,
        "registration": result.payload.get("registration"),
        "campaigns": campaigns,
        "runs": runs,
        "elapsed_s": round(elapsed, 2),
        "budget_s": payload.get("budget_seconds"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=2)
    args = parser.parse_args()

    work = Path(tempfile.mkdtemp(prefix="computronium-quest-run-"))
    store_path = work / "probe.duckdb"
    registry = work / "preregistrations"
    run_id = build_store(store_path)
    logger.info("store %s holds run %s", store_path, run_id)

    result = asyncio.run(probe(store_path, registry, run_id, args.seeds))
    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
