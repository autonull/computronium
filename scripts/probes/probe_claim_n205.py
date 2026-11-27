"""The n_max=205 claim rung for credit/random_projections on mnist (W41).

Decision: does tuning ``credit.feedback_scale`` on
``primitive.credit.random_projections`` raise val_acc at the mnist base with
Cohen's dz >= 0.276769? Stop rule: fixed n = 205 pairs, pre-registered in
``configs/preregistrations/sec_credit_random_projections_n205.json`` before
the first fresh seed; no peeking, no early stop. A pass is a claim; anything
else is a coordinate result. Box: L0, 1 epoch, batch 32, cpu, fp32, seeds
256..460 (fresh, never used by the pilot 0..191 or the confirm block 192..255).

Priced from the confirm block: 64 pairs took 1316 s, so 205 pairs is ~70 min.
The watchdog is 140 min (2x that measured cost).
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from pathlib import Path

os.environ.setdefault("SEC_DEVICE", "cpu")

from computronium.experiment.schema import seed_all_registries  # ruff: ignore[module-import-not-at-top-of-file]

seed_all_registries()

from computronium.experiment.sec_all_axes import run_rung2_comparison  # ruff: ignore[module-import-not-at-top-of-file]

PILOT_BEST = 0.22653156413948863
N_SEEDS = 205
SEED_OFFSET = 256
REGISTRATION = Path("configs/preregistrations/sec_credit_random_projections_n205.json")
RESULTS = Path("results/sec/claim_rp_256")


async def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    (RESULTS / "started.json").write_text(
        json.dumps(
            {
                "n_seeds": N_SEEDS,
                "seed_offset": SEED_OFFSET,
                "registration": str(REGISTRATION),
                "watchdog_s": 2 * 1316.0 * N_SEEDS / 64,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    result = await run_rung2_comparison(
        "credit",
        "random_projections",
        "mnist",
        PILOT_BEST,
        REGISTRATION,
        n_seeds=N_SEEDS,
        semaphore_limit=1,
        budget_s=600.0,
        seed_offset=SEED_OFFSET,
    )
    elapsed = time.monotonic() - started
    if result is None:
        print("no comparison: the registration or knob did not load")
        return 1

    cells, effect, verdict = result
    outcomes = [c.status for c in cells]
    payload = {
        "claim": "credit/random_projections on mnist at n_max=205",
        "registration": str(REGISTRATION),
        "box": cells[0].box if cells else {},
        "n_seeds": N_SEEDS,
        "seed_offset": SEED_OFFSET,
        "effect": effect,
        "verdict": verdict,
        "cell_status": {
            status: outcomes.count(status) for status in sorted(set(outcomes))
        },
        "walltime_s": elapsed,
        "watchdog_s": 2 * 1316.0 * N_SEEDS / 64,
    }
    (RESULTS / "claim_results.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
