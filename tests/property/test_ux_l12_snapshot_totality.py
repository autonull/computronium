"""UX-L12: `render_snapshot` is total — never raises for any artifact-dir state."""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from computronium.knowledge import KnowledgeBase, KnowledgeEntry
from computronium.visualization.live_atlas import EmbedCache, render_snapshot

_CELL_HP = {
    "geometry": {"topology_type": "feedforward", "depth": 2, "hidden_dim": 64},
    "dynamics": "energy_minimization",
    "credit": "prediction",
    "update": "euclidean",
    "param_budget": 25000,
}

_MALFORMED = st.sampled_from(["", "\n", "not json", '{"truncated": ', "[1, 2,", "null"])


@settings(max_examples=25, deadline=None)
@given(
    n_cells=st.integers(min_value=0, max_value=6),
    defects=st.lists(_MALFORMED, max_size=4),
    with_voids=st.booleans(),
    heartbeat=st.sampled_from([None, "valid", "malformed"]),
)
def test_ux_l12_render_snapshot_never_raises(
    tmp_path_factory, n_cells: int, defects: list[str], with_voids: bool, heartbeat
) -> None:
    root = tmp_path_factory.mktemp("broad_map")
    (root / "logs").mkdir(exist_ok=True)

    if n_cells:
        kb = KnowledgeBase(root / "kb.sqlite")
        for i in range(n_cells):
            kb.add_entry(
                KnowledgeEntry(
                    id=f"l12_{i}",
                    topic="experiment:mnist",
                    model_family="eqprop",
                    finding="cell",
                    details="",
                    confidence=0.5 + i * 0.01,
                    tags=["experiment", "mnist", "broad_map", "maturity:l0"],
                    source="experiment",
                    metrics={
                        "final_accuracy": 0.5 + i * 0.05,
                        "walltime_s": 1.0 + i,
                        "settle_horizon": 4,
                        "credit_alignment": 0.4,
                    },
                    hyperparameters=dict(_CELL_HP),
                    extra={},
                )
            )

    if defects:
        (root / "runtime_defects.jsonl").write_text(
            "\n".join(defects) + "\n", encoding="utf-8"
        )
    if with_voids:
        (root / "structural_voids.jsonl").write_text(
            '{"category": "x"}\ngarbage\n', encoding="utf-8"
        )
    if heartbeat == "valid":
        (root / "heartbeat.json").write_text(
            '{"pid": 1, "state": "idle", "burst": null, "cell_index": null, '
            '"started_at": 0.0, "updated_at": 0.0, "log_path": null, '
            '"target_cells": null, "loop": false}',
            encoding="utf-8",
        )
    elif heartbeat == "malformed":
        (root / "heartbeat.json").write_text("{nope", encoding="utf-8")

    snapshot = render_snapshot(root, cache=EmbedCache(), with_atlas=False)
    assert snapshot is not None
    assert isinstance(snapshot.health, dict)
