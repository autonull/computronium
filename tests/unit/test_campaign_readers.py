"""Campaign-artifact readers: daemon liveness, cost/maturation rollups, report.

These are the read-only loaders behind `comp campaign report` and the daemon's
own campaign summary — the paths that used to be exercised only through the
deleted dashboard. Coverage is ported from the retired UI smoke/liveness suites.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from computronium.autoscientist.campaign_readers import (
    DaemonClient,
    cost_stats,
    health_stats,
    liveness,
    maturation_rows,
    read_heartbeat,
)
from computronium.autoscientist.report import generate_report

if TYPE_CHECKING:
    from pathlib import Path

_CELL_HP = {
    "geometry": {"topology_type": "feedforward", "depth": 2, "hidden_dim": 64},
    "dynamics": "energy_minimization",
    "credit": "prediction",
    "update": "euclidean",
    "param_budget": 25000,
}

_CELLS = (
    ("burst:2026-09-16-1", 0.80),
    ("burst:2026-09-16-1", 0.65),
    ("burst:2026-09-16-2", 0.83),
    ("burst:2026-09-16-2", 0.60),
)


def _seed_root(root: Path) -> None:
    """Tiny KB (4 measured cells across 2 bursts) + voids + defects."""
    from computronium.knowledge import KnowledgeBase, KnowledgeEntry

    root.mkdir(parents=True, exist_ok=True)
    kb = KnowledgeBase(root / "kb.sqlite")
    for i, (burst, acc) in enumerate(_CELLS):
        kb.add_entry(
            KnowledgeEntry(
                id=f"readers_{i}",
                topic="experiment:mnist",
                model_family="eqprop",
                finding="fixture cell",
                details="",
                confidence=acc,
                tags=["experiment", "mnist", "broad_map", "maturity:l0", burst],
                source="experiment",
                metrics={
                    "final_accuracy": acc,
                    "walltime_s": 1.5 + i * 0.1,
                    "settle_horizon": 4,
                    "credit_alignment": 0.4,
                    "spectral_radius": 0.9 - i * 0.05,
                    "psi_capacity": 1.0 + i,
                    "stability_plasticity_ratio": (0.9 - i * 0.05) / (1.0 + i),
                    "credit_efficiency": (0.2, 0.35, 0.65, 0.3)[i],
                    "feedback_path_length": 2.0 + i,
                    "trace_variance": 0.1 * (i + 1),
                },
                hyperparameters=dict(_CELL_HP),
                extra={},
            )
        )
    void = {
        "timestamp": 1.0,
        "task": "mnist",
        "dynamics": "spike_integration",
        "credit": "prediction",
        "update": "euclidean",
        "topology": "recurrent",
        "category": "geometry_constraint",
        "error": "Spike integration dynamics requires temporal trace",
    }
    (root / "structural_voids.jsonl").write_text(
        json.dumps(void) + "\n", encoding="utf-8"
    )
    defect = {
        "defect_id": "a1b2c3d4e5f6",
        "timestamp": 2.0,
        "task": "mnist",
        "cell": "energy_minimization|prediction|euclidean|recurrent",
        "error_class": "RuntimeError",
        "message": "device poisoning at 0x7f00",
        "traceback_tail": "",
        "status": "open",
    }
    (root / "runtime_defects.jsonl").write_text(
        json.dumps(defect) + "\n", encoding="utf-8"
    )


def _heartbeat(root: Path, state: str, age_s: float = 0.0) -> float:
    import time

    updated = time.time() - age_s
    (root / "heartbeat.json").write_text(
        json.dumps({
            "pid": 4242,
            "state": state,
            "burst": "burst_0001",
            "cell_index": 12,
            "started_at": updated - 60.0,
            "updated_at": updated,
            "log_path": None,
        })
    )
    return updated


def test_offline_when_no_heartbeat(tmp_path: Path) -> None:
    badge = liveness(tmp_path, daemon_reachable=False)
    assert badge.label == "● OFFLINE"
    assert badge.color == "grey"


def test_connection_lost_on_stale_heartbeat(tmp_path: Path) -> None:
    _heartbeat(tmp_path, "training", age_s=30.0)
    badge = liveness(tmp_path, daemon_reachable=False)
    assert badge.label == "● CONNECTION LOST"
    assert badge.color == "red"


def test_fresh_heartbeat_drives_badge_per_state(tmp_path: Path) -> None:
    _heartbeat(tmp_path, "training")
    assert liveness(tmp_path, True).label == "● RUNNING"
    assert liveness(tmp_path, True).color == "green"
    _heartbeat(tmp_path, "sleeping")
    assert liveness(tmp_path, True).label == "● SLEEPING"
    _heartbeat(tmp_path, "paused")
    badge = liveness(tmp_path, True)
    assert badge.label == "● PAUSED" and badge.color == "amber"
    _heartbeat(tmp_path, "idle")
    assert "ready" in liveness(tmp_path, True).label


def test_unreachable_api_with_fresh_heartbeat_degrades_gracefully(
    tmp_path: Path,
) -> None:
    """Hybrid transport: artifacts survive daemon death."""
    _heartbeat(tmp_path, "training")
    badge = liveness(tmp_path, daemon_reachable=False)
    assert badge.label == "● RUNNING"
    assert "API unreachable" in badge.detail


def test_read_heartbeat_round_trips_state(tmp_path: Path) -> None:
    _heartbeat(tmp_path, "training")
    beat = read_heartbeat(tmp_path)
    assert beat is not None
    assert beat["state"] == "training"
    assert beat["pid"] == 4242


def test_health_and_maturation_rollups(tmp_path: Path) -> None:
    root = tmp_path / "root"
    _seed_root(root)

    health = health_stats(root)
    assert health["measured_cells"] == 4
    assert health["bursts"] == 2
    assert health["cells_per_burst"] == 2.0
    assert health["open_defects"] == 1
    assert isinstance(health["last_burst_walltime_s"], float)

    counts = {row["level"]: row["count"] for row in maturation_rows(root)}
    assert counts["maturity:l0"] == 4
    assert counts["maturity:l2"] == 0

    costs = cost_stats(root)
    assert costs["measured"] == 4


def test_generate_report_assembles_markdown(tmp_path: Path) -> None:
    """§7.3: the campaign summary the daemon writes at completion."""
    root = tmp_path / "root"
    _seed_root(root)

    report = generate_report(root)
    text = report.read_text(encoding="utf-8")
    for heading in (
        "# Computronium campaign summary",
        "## Totals",
        "## Final Pareto front",
        "## Maturation",
        "## Negative results",
        "## Cost breakdown",
        "maturity:l0",
        "geometry_constraint",
    ):
        assert heading in text, heading
    assert report == root / "campaign_report.md"


def test_daemon_client_unreachable_returns_none() -> None:
    client = DaemonClient("http://127.0.0.1:1", timeout=0.2)
    assert client.get_state() is None
    assert client.control("pause") is False


def test_daemon_client_round_trips_live_daemon(tmp_path: Path) -> None:
    import threading
    import time
    from argparse import Namespace

    import uvicorn

    from computronium.autoscientist.daemon import ContinuousDaemon, DaemonState

    args = Namespace(
        root=tmp_path,
        budget=None,
        target_cells=10_000,  # unreachable: the burst stays live for the round-trip
        loop=False,
        sleep=0.0,
        max_iterations=1_000,
        seed=1,
        log_path=None,
        maturation=0,
    )

    class _Driver:
        cells = 1

        def propose_batch(self, n, recent_results=None):
            return []

        def has_novel(self):
            return True

    class _Campaign:
        def __init__(self):
            self.voids_path = tmp_path / "voids.jsonl"
            self.defects_path = None
            self.step_callback = None

        def run_iteration(self, n_experiments):
            time.sleep(0.05)  # keep the burst alive across the round-trip
            return [
                {"status": "completed", "proposal": {}, "walltime_s": 0.0}
                for _ in range(n_experiments)
            ]

        def save_checkpoint(self):
            pass

    daemon = ContinuousDaemon(
        args,
        sweep_factory=lambda _a: (_Campaign(), _Driver()),  # type: ignore[arg-type]
    )
    server = uvicorn.Server(
        uvicorn.Config(daemon.build_app(), host="127.0.0.1", port=0, log_level=0)
    )
    daemon.start_worker()
    daemon.start()
    threading.Thread(target=server.run, daemon=True).start()
    try:
        deadline = time.monotonic() + 10
        port = server.servers[0].sockets[0].getsockname()[1] if server.started else None
        while port is None and time.monotonic() < deadline:
            time.sleep(0.05)
            port = (
                server.servers[0].sockets[0].getsockname()[1]
                if server.started
                else None
            )
        # 3 s timeout: the spinning burst worker holds the GIL and can
        # starve a 1 s request under pytest.
        client = DaemonClient(f"http://127.0.0.1:{port}", timeout=3.0)
        state = client.get_state()
        assert state is not None
        assert int(state["pid"]) > 0  # type: ignore[call-overload]
        assert client.control("pause") is True
        deadline = time.monotonic() + 10
        while daemon.state is not DaemonState.PAUSED and time.monotonic() < deadline:
            time.sleep(0.05)
        assert daemon.state is DaemonState.PAUSED
        assert client.control("resume") is True
    finally:
        daemon.stop()
        deadline = time.monotonic() + 10
        while daemon.state is not DaemonState.STOPPED and time.monotonic() < deadline:
            time.sleep(0.05)
