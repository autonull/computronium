"""End-to-end burst (TODO29 Phase 3): one tiny CPU burst on ``digits``
through ``build_sweep``/``run_burst`` proving resume-safety, KB rows, and
the checkpoint-on-stop contract."""

from __future__ import annotations

import json
import time
from argparse import Namespace
from typing import TYPE_CHECKING, cast

from computronium.autoscientist.broad_map import (
    ContinuousBudget,
    build_sweep,
    run_burst,
    run_l1_maturation,
)
from computronium.utils import seed_everything

if TYPE_CHECKING:
    from pathlib import Path


_SEED = 20260916


def _args(root: Path) -> Namespace:
    return Namespace(
        root=root,
        task="digits",
        epochs=1,
        seed=_SEED,
        cells_per_iter=2,
        depth=2,
        hidden_dim=16,
        param_budget=0,  # skip the rematch rescale: keep the burst tiny
        credit_trace=False,
        maturation=0,
    )


def _cell_keys(root: Path) -> set[str]:
    """Measured-cell keys only (experiment: entries — incompatible: coverage
    rows carry the same axes but are voids, not measurements)."""
    from computronium.knowledge import KnowledgeBase

    kb = KnowledgeBase(root / "kb.sqlite")
    keys: set[str] = set()
    for entry in kb.query():
        hp = entry.hyperparameters
        if not str(entry.topic).startswith("experiment:"):
            continue
        if not (hp.get("dynamics") and hp.get("credit") and hp.get("update")):
            continue
        geometry = hp.get("geometry") or {}
        if not isinstance(geometry, dict):
            continue
        keys.add(
            f"{hp['dynamics']}|{hp['credit']}|{hp['update']}"
            f"|{geometry.get('topology_type', 'feedforward')}"
        )
    return keys


def test_burst_measures_cells_and_writes_artifacts(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_everything(_SEED, deterministic=False)
    campaign, driver = build_sweep(_args(root))
    budget = ContinuousBudget(started_at=time.monotonic(), target_cells=2)
    summary = run_burst(campaign, driver, budget, max_iterations=10)

    assert summary["completed"] == 2
    assert summary["stop_reason"] == "target"
    assert summary["done"] == 2
    measured = _cell_keys(root)
    assert len(measured) == 2
    # Phase 1 instrument: every completed cell carries a walltime.
    means = cast("dict[str, float]", summary["walltime_mean_by_family"])
    assert len(means) >= 1
    assert all(v >= 0.0 for v in means.values())
    # Checkpoint written on stop (output_dir/checkpoints per the checkpointer).
    checkpoints = list((root / "campaign" / "checkpoints").glob("*.yaml"))
    assert checkpoints, "burst must checkpoint on stop"


def test_second_burst_never_remeasures_cells(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_everything(_SEED, deterministic=False)
    campaign, driver = build_sweep(_args(root))
    run_burst(
        campaign,
        driver,
        ContinuousBudget(started_at=time.monotonic(), target_cells=2),
        max_iterations=10,
    )
    first = _cell_keys(root)
    assert len(first) == 2

    # Resume from the same root: coverage seed must exclude burst-1 cells.
    campaign2, driver2 = build_sweep(_args(root))
    assert first <= driver2.seen
    summary2 = run_burst(
        campaign2,
        driver2,
        ContinuousBudget(started_at=time.monotonic(), target_cells=4),
        max_iterations=3,
    )
    second = _cell_keys(root)
    completed2 = cast("int", summary2["completed"])
    assert len(second) == len(first) + completed2
    assert completed2 <= 2 * 3  # cells-per-iter × iterations cap


def test_budget_expiry_stops_burst(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_everything(_SEED, deterministic=False)
    campaign, driver = build_sweep(_args(root))
    # Soft cap already expired: nothing may start.
    summary = run_burst(
        campaign,
        driver,
        ContinuousBudget(started_at=0.0, soft_seconds=1.0),
        max_iterations=5,
    )
    assert summary["completed"] == 0
    assert summary["stop_reason"] == "soft"


def test_l1_maturation_promotes_front_cells_once(tmp_path: Path) -> None:
    from computronium.autoscientist.broad_map import (
        promote_candidates,
    )
    from computronium.knowledge import KnowledgeBase

    root = tmp_path / "broad_map"
    seed_everything(_SEED, deterministic=False)
    campaign, driver = build_sweep(_args(root))
    run_burst(
        campaign,
        driver,
        ContinuousBudget(started_at=time.monotonic(), target_cells=2),
        max_iterations=10,
    )
    args = _args(root)
    args.maturation = 2
    written = run_l1_maturation(args, campaign, driver.burst_tag)
    assert len(written) >= 1
    assert all(row["maturity"] == "l1" and row["epochs"] == 3 for row in written)

    rows = (root / "maturation.jsonl").read_text(encoding="utf-8").splitlines()
    assert all(json.loads(r)["maturity"] == "l1" for r in rows)
    kb = KnowledgeBase(root / "kb.sqlite")
    l1_tags = [
        tag
        for entry in kb.query()
        if str(entry.topic).startswith("experiment:")
        for tag in entry.tags
        if tag == "maturity:l1"
    ]
    assert len(l1_tags) >= 1
    # Promotion is idempotent: the front cell now carries an L1 row.
    assert (
        promote_candidates(root / "kb.sqlite", root / "structural_voids.jsonl", 5) == []
    )


def _seed_synthetic_kb(root: Path) -> None:
    """Two bursts measuring a stable cell (front in both) and a volatile
    one (never on the front, spread > 0.2) — no training involved."""
    from computronium.knowledge import KnowledgeBase, KnowledgeEntry

    kb = KnowledgeBase(root / "kb.sqlite")
    cells = {
        "energy_minimization|prediction|euclidean|feedforward": (
            "energy_minimization",
            "prediction",
            "euclidean",
            (("burst:2026-09-16-1", 0.90), ("burst:2026-09-16-2", 0.92)),
        ),
        "instantaneous|null|euclidean|feedforward": (
            "instantaneous",
            "null",
            "euclidean",
            (("burst:2026-09-16-1", 0.20), ("burst:2026-09-16-2", 0.75)),
        ),
    }
    for key, (dyn, cred, upd, runs) in cells.items():
        for burst, acc in runs:
            kb.add_entry(
                KnowledgeEntry(
                    id=f"synth_{key}_{burst}",
                    topic="experiment:mnist",
                    model_family="eqprop",
                    finding="synthetic measurement",
                    details="",
                    confidence=acc,
                    tags=[
                        "experiment",
                        "mnist",
                        "broad_map",
                        "maturity:l0",
                        burst,
                        key,
                    ],
                    source="experiment",
                    metrics={"final_accuracy": acc},
                    hyperparameters={
                        "geometry": {
                            "topology_type": "feedforward",
                            "depth": 2,
                            "hidden_dim": 64,
                        },
                        "dynamics": dyn,
                        "credit": cred,
                        "update": upd,
                        "param_budget": 25000,
                    },
                    extra={},
                )
            )


def test_deep_tier_scan_flags_variance_and_dry_run(tmp_path: Path, capsys) -> None:  # noqa: ANN001
    from computronium.autoscientist.broad_map import (
        _deep_tier_candidates,
        _load_measured_cells,
        _seed_sensitivity_flags,
    )
    from computronium.cli.continuous import _deep_tier

    root = tmp_path / "broad_map"
    _seed_synthetic_kb(root)

    candidates = _deep_tier_candidates(root / "kb.sqlite", 5, None)
    assert [c.key for c in candidates] == [
        "energy_minimization|prediction|euclidean|feedforward"
    ]
    assert candidates[0].front_bursts == 2

    flags = _seed_sensitivity_flags(_load_measured_cells(root / "kb.sqlite"))
    assert len(flags) == 1
    assert flags[0]["cell"] == "instantaneous|null|euclidean|feedforward"
    assert float(flags[0]["spread"]) > 0.2  # type: ignore[arg-type]

    args = Namespace(
        root=root, task=None, top=5, epochs=10, seeds=3, seed=_SEED, dry_run=True
    )
    assert _deep_tier(args) == 0
    out = capsys.readouterr().out
    assert "energy_minimization|prediction|euclidean|feedforward" in out
    assert "3 CEEC experiments" in out
    assert not (root / "maturation.jsonl").exists()  # dry-run writes nothing
