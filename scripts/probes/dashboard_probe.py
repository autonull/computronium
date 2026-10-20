"""What every dashboard probe needs: a browser, a store, a server (TODO68).

Six probes drove the same dashboard the same way, each with its own copy of
the same three pieces: the Chromium flags that make WebGL work without a GPU,
the wait for the server to answer, and the store the probe reads. One copy of
each lives here, so a probe says what it is measuring and nothing else.
"""

from __future__ import annotations

import logging
import tempfile
import threading
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator

logger = logging.getLogger(__name__)

SHOT_DIR = Path(tempfile.gettempdir()) / "computronium"

# WebGL without a GPU: the software rasterizer draws the scene, slowly, and
# the page still runs.
CHROMIUM_ARGS = [
    "--use-gl=angle",
    "--use-angle=swiftshader",
    "--enable-unsafe-swiftshader",
    "--enable-webgl",
    "--ignore-gpu-blocklist",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--force-device-scale-factor=1",
]

# The cell the probes measure: the demo's, at its declared values.
COORDINATE = {
    "substrate": "digital",
    "geometry": "feedforward",
    "dynamics": "instantaneous",
    "plasticity": "null",
    "credit": "gradient",
    "update": "adam",
}


def wait_for_http(port: int, timeout: float = 60.0) -> bool:
    """Wait for the dashboard HTTP server to answer."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(
                f"http://localhost:{port}/api/status", timeout=2
            ) as response:
                if response.status == 200:
                    return True
        except urllib.error.URLError, OSError:
            pass
        time.sleep(0.5)
    return False


def build_store(path: Path) -> str:
    """A store holding one run with five measured seeds of one cell.

    Args:
        path: Where the store is written.

    Returns:
        The run's id.
    """
    from computronium.experiment.evidence.store import RecordStore, StoreConfig
    from computronium.experiment.schema.coordinate import (
        Coordinate,
        Provenance,
        Schedule,
    )
    from computronium.experiment.schema.record import (
        FailureCause,
        GateVerdict,
        Maturity,
        Record,
        ReproducibilityClass,
        Severity,
        Status,
    )
    from computronium.experiment.schema.run_spec import RunSpec
    from computronium.experiment.schema.seed_registries import seed_all_registries

    seed_all_registries()
    spec = RunSpec(
        profile="demo",
        task="digits",
        objectives=("validation_accuracy",),
        fidelity="L1",
        n_seeds=5,
        epochs=1,
        budget_seconds=120.0,
    )

    with RecordStore(StoreConfig(path=path)) as store:
        run_id = store.create_run(spec=spec)
        for seed in range(5):
            store.append(
                Record.create(
                    run_id=run_id,
                    coordinate=Coordinate(**COORDINATE, params={}),
                    schedule=Schedule(
                        fidelity="L1",
                        seed=seed,
                        n_seeds=1,
                        epochs=1,
                        batch_limit=0,
                        budget_id="probe",
                        task_id="digits",
                        param_budget=0,
                    ),
                    provenance=Provenance(
                        env={"python": "3.14", "platform": "linux"},
                        dataset="digits",
                        dataset_version="1.0",
                        code_sha="probe",
                        policy="probe",
                        links={"run_id": run_id},
                    ),
                    status=Status(
                        gate_verdict=GateVerdict.PASS_,
                        defect="",
                        cause=FailureCause.UNKNOWN,
                        severity=Severity.LOW,
                        quarantine=False,
                        maturity=Maturity.L1,
                        uncertainty={},
                        reproducibility=ReproducibilityClass.REPLAYABLE,
                        assessment_procedure_version="1.0",
                        ceec_link=None,
                    ),
                    payload={
                        "val_acc": 0.40 + 0.02 * seed,
                        "walltime_s": 3.0,
                        "param_count": 1024,
                    },
                )
            )
    return run_id


@contextmanager
def serving_dashboard(
    store_path: Path,
    port: int,
    registration_dir: Path | None = None,
) -> Generator[None]:
    """Serve the dashboard on ``port`` while the block runs.

    Args:
        store_path: The store the dashboard reads.
        port: The port to serve on.
        registration_dir: Where the dashboard writes registrations.

    Yields:
        Nothing: the block is the probe.
    """
    from computronium.experiment.execution.dashboard.web import (
        DashboardConfig,
        WebDashboard,
    )

    dashboard = WebDashboard(
        DashboardConfig(
            host="127.0.0.1",
            port=port,
            store_path=str(store_path),
            registration_dir=registration_dir,
        )
    )

    def serve() -> None:
        import asyncio

        asyncio.run(dashboard.run())

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    if not wait_for_http(port):
        msg = f"the dashboard did not start on port {port}"
        raise RuntimeError(msg)
    yield
