"""Diagnose L1 maturation idempotency.

Informed the fix for
tests/integration/test_continuous_burst.py::test_l1_maturation_promotes_front_cells_once:
promote_candidates returned an already-promoted cell, so the maturity:l1
marker never reached the ``levels`` gate. Prints every experiment: KB entry
with its cell key, tags and maturity levels, plus both promotion calls.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from tempfile import mkdtemp

from computronium.autoscientist.broad_map import (
    ContinuousBudget,
    promote_candidates,
    run_burst,
    run_l1_maturation,
)
from computronium.knowledge import KnowledgeBase
from computronium.utils import seed_everything
from tests.integration.test_continuous_burst import _SEED, _args, build_sweep


def main() -> None:
    root = Path(mkdtemp()) / "broad_map"
    seed_everything(_SEED, deterministic=False)
    campaign, driver = build_sweep(_args(root))
    run_burst(
        campaign,
        driver,
        ContinuousBudget(started_at=time.monotonic(), target_cells=2),
        max_iterations=10,
    )

    def dump(label: str) -> None:
        print(f"\n=== {label} ===")
        for entry in KnowledgeBase(root / "kb.sqlite", auto_embed=False).query(
            limit=10_000
        ):
            topic = str(entry.topic)
            if not topic.startswith("experiment:"):
                continue
            hp = entry.hyperparameters
            geo = hp.get("geometry") or {}
            key = "|".join([
                str(hp.get("dynamics")),
                str(hp.get("credit")),
                str(hp.get("update")),
                str(geo.get("topology_type", "feedforward")),
            ])
            print(f"  key={key}")
            print(f"    topic={topic}  tags={sorted(str(t) for t in entry.tags)}")

    dump("after burst")
    args = _args(root)
    args.maturation = 2
    written = run_l1_maturation(args, campaign, driver.burst_tag)
    print("\nwritten:", json.dumps(written, indent=2)[:400])
    dump("after maturation")

    again = promote_candidates(root / "kb.sqlite", root / "structural_voids.jsonl", 5)
    print("\nsecond promote_candidates ->", [c.key for c in again])


if __name__ == "__main__":
    main()
