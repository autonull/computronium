"""TODO26d — AutoScientist readiness test: a real campaign iteration.

Question: is the AutoScientist ready to explore the ontology space
beyond hand-picked slices? Test empirically — seed the KnowledgeBase
with the engine-check findings, run one live campaign iteration, and
grade what it proposes AND executes.

Run: uv run python scripts/probes/todo26d_autoscientist_ready.py
Walltime printed, never recorded.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path

from computronium.autoscientist import create_campaign
from computronium.knowledge.entries import KnowledgeEntry
from computronium.knowledge.kb import KnowledgeBase

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

KB_SEED = [
    # (observation, context) — the engine-check findings, round 1-3b
    {
        "observation": "ePC + residual + mupc + LocalAdam trains depth 20-30 "
        "(sign-of-mean, 0.82-0.88); default-init or no-residual is chance",
        "context": "architecture co-design",
    },
    {
        "observation": "FF rescued by residual+mupc (0.506->0.875) at depth 20; "
        "FA geometry-insensitive (0.504/0.514); EqProp HARMED by co-design "
        "(0.494->0.466)",
        "context": "zoo grid, family-specific co-design law",
    },
    {
        "observation": "credit_norm=rms lifts hidden-layer credit magnitude but "
        "input-weight layer stays exactly zero at depth 20 (settle horizon); "
        "normalization amplifies noise (split-half cosine 0.000)",
        "context": "trapped-channel mechanism",
    },
    {
        "observation": "supervised psi (TemporalPsi) plateaus at 0.73 = ridge "
        "ceiling of frozen penultimate features (0.721); 0.95 flagship bar is "
        "a feature-quality problem",
        "context": "P-axis ceiling",
    },
    {
        "observation": "lr 1e-2 unstable at every depth; lr 3e-3 robust across "
        "5 seeds, depth 30 mean 0.823",
        "context": "stability boundary",
    },
]


def main() -> None:
    t0 = time.perf_counter()
    kb = KnowledgeBase()
    for i, rec in enumerate(KB_SEED):
        kb.add_entry(
            KnowledgeEntry(
                id=f"TODO26D-{i}",
                topic="EngineCheck",
                model_family="mixed",
                finding=rec["observation"],
                details=rec["observation"],
                confidence=0.9,
                tags=["engine_check", str(rec["context"])],
                source="manual",
            )
        )

    # Experiment-shaped records: the reasoner's rule generators consume
    # these (val_accuracy/model/task) — narrative entries alone yield 0
    # hypotheses (measured above in iteration 1).
    for fam, acc in (
        ("eqprop_mlp", 0.88),
        ("fa_mlp", 0.51),
        ("pepita_mlp", 0.50),
        ("backprop_mlp", 0.85),
    ):
        kb.add_experiment(
            name=f"todo26_zoo_{fam}",
            model_family=fam,
            task="mnist",
            config={"geometry": "residual+mupc", "depth": 20, "lr": 3e-3},
            metrics={
                "val_accuracy": acc,
                "bio_score": 0.9 if fam != "backprop_mlp" else 0.3,
            },
        )

    campaign = create_campaign(
        knowledge_base=kb,
        output_dir="scratch/todo26d_autoscientist",
        branch="main",
    )
    print("== Dry run: what does it propose? ==", flush=True)
    proposals = campaign.run_iteration(n_experiments=6, dry_run=True)
    for p in proposals:
        raw: object = p.get("proposal", p) if isinstance(p, dict) else {}
        info = raw if isinstance(raw, dict) else {}
        print(
            f"- {info.get('model', '?')} on {info.get('task', '?')} :: "
            f"{str(info.get('hypothesis', ''))[:110]}",
            flush=True,
        )

    print("== Live iteration: execute the proposals ==", flush=True)
    results = campaign.run_iteration(n_experiments=6, dry_run=False)
    for r in results:
        status = r.get("status", "?")
        if status == "failed":
            err = str(r.get("error", ""))[:140]
            print(f"FAILED: {err}", flush=True)
        else:
            metrics: object = r.get("metrics", r)
            print(f"OK: {json.dumps(metrics, default=str)[:220]}", flush=True)
    out = Path("scratch/todo26d_autoscientist")
    print(f"campaign artifacts: {out} (db + iterations persisted)", flush=True)
    print(f"total walltime {time.perf_counter() - t0:.1f}s")


if __name__ == "__main__":
    main()
