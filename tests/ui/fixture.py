"""Shared dashboard test fixtures: tiny synthetic campaign root."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

_CELL_HP = {
    "geometry": {"topology_type": "feedforward", "depth": 2, "hidden_dim": 64},
    "dynamics": "energy_minimization",
    "credit": "prediction",
    "update": "euclidean",
    "param_budget": 25000,
}


def seed_campaign_root(root: Path) -> None:
    """Tiny KB (4 measured cells across 2 bursts) + voids + defects + log."""
    from computronium.knowledge import KnowledgeBase, KnowledgeEntry

    (root / "logs").mkdir(parents=True, exist_ok=True)
    kb = KnowledgeBase(root / "kb.sqlite")
    for i, (burst, acc) in enumerate((
        ("burst:2026-09-16-1", 0.80),
        ("burst:2026-09-16-1", 0.65),
        ("burst:2026-09-16-2", 0.83),
        ("burst:2026-09-16-2", 0.60),
    )):
        kb.add_entry(
            KnowledgeEntry(
                id=f"dash_{i}",
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
                },
                hyperparameters=dict(_CELL_HP),
                extra={},
            )
        )
    row = {
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
        json.dumps(row) + "\n", encoding="utf-8"
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
    (root / "logs" / "continuous_500.log").write_text(
        "\n".join(f"line {i}" for i in range(40)) + "\n", encoding="utf-8"
    )
