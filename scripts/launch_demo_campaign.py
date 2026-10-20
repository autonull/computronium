#!/usr/bin/env python3
"""Launch a demo campaign in the background for dashboard screenshot capture.

This script:
1. Starts a campaign queue in a background subprocess
2. Submits a demo campaign (4 credit arms, 5 seeds)
3. Waits for first records to land
4. Returns the campaign ID and store path
"""

from __future__ import annotations

import asyncio
import logging
import subprocess
import sys
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def wait_for_records(
    store_path: Path, run_id: str, min_records: int = 1, timeout: float = 120.0
) -> bool:
    """Poll the store until at least min_records exist for the run."""
    from computronium.experiment.evidence.store import RecordStore, StoreConfig

    start = time.time()
    while time.time() - start < timeout:
        try:
            store = RecordStore(StoreConfig(path=store_path, read_only=True))
            with store:
                records = list(store.query_records(run_id=run_id))
                if len(records) >= min_records:
                    logger.info(f"Found {len(records)} records for {run_id}")
                    return True
        except Exception as e:
            logger.debug(f"Store not ready yet: {e}")

        await asyncio.sleep(1.0)

    logger.error(f"Timeout waiting for {min_records} records in {run_id}")
    return False


async def main() -> int:
    """Launch demo campaign and return when records are available."""
    repo_root = Path(__file__).resolve().parents[1]
    store_path = repo_root / "experiment.duckdb"

    # Clean up any existing store
    if store_path.exists():
        store_path.unlink()
        logger.info(f"Removed existing store: {store_path}")

    # Launch campaign queue in background
    logger.info("Starting campaign queue...")
    queue_proc = subprocess.Popen(
        [sys.executable, "-m", "computronium.experiment.execution.campaign_queue"],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Give queue time to start
    await asyncio.sleep(2.0)

    # Submit demo campaign
    logger.info("Submitting demo campaign...")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "computronium.cli.__main__",
            "run",
            "demo",
            "--store",
            str(store_path),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        logger.error(f"Campaign submission failed: {result.stderr}")
        queue_proc.terminate()
        return 1

    # Extract run_id from output
    run_id = None
    for line in result.stdout.splitlines():
        if "run_id" in line.lower() or "Run" in line:
            # Try to find a UUID-like pattern
            import re

            match = re.search(
                r"([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})", line
            )
            if match:
                run_id = match.group(1)
                break

    if not run_id:
        # Fallback: query the store for the latest run
        from computronium.experiment.evidence.store import RecordStore, StoreConfig

        store = RecordStore(StoreConfig(path=store_path, read_only=True))
        with store:
            runs = list(store.query_runs())
            if runs:
                run_id = runs[-1].run_id

    if not run_id:
        logger.error("Could not determine run_id")
        queue_proc.terminate()
        return 1

    logger.info(f"Campaign submitted: {run_id}")

    # Wait for first records to land
    logger.info("Waiting for first records...")
    if await wait_for_records(store_path, run_id, min_records=1, timeout=180.0):
        logger.info("✓ Demo campaign has records ready for dashboard")
        print(f"RUN_ID={run_id}")
        print(f"STORE_PATH={store_path}")
        return 0
    else:
        logger.error("No records appeared in time")
        queue_proc.terminate()
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Interrupted")
        sys.exit(130)
