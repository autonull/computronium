"""Retroactive harvest audit of the LEMMA boundary (TODO15 §9.7 item 2).

TODO14's §9 doctrine: any boundary recorded from FINAL-step accuracy on
a possibly-declining trajectory is suspect — the depth-50 "collapse"
was exactly that artifact (val peaked at batch 30-70, then memorized).
LEMMA × Muon's 0.306 boundary (TODO14 §7, w1_credit_ladder, 150
batches, final-step read) is the headline closure of the local
pseudo-gradient feedback family — audit it before it carries more
weight.

Protocol: identical cell to w1_credit_ladder (hunt_cells harness, width
64×2, MNIST 150 batches, seed 0-2) plus best-snapshot harvest — val
probe every 10 batches, geometry params deep-copied at the best probe,
final eval on BOTH the final and the restored-best params.

Pre-registered reading:
- best − final < 0.03 → boundary stands as a plateau (no artifact).
- best ≥ 0.40 (the §2.1 reopen bar) → LEMMA × Muon REOPENED under
  harvesting, LEMMA's mechanism-bound closure (TODO15 §12) re-scoped.

uv run python scripts/probes/w1_lemma_harvest_audit.py
Walltime printed, never recorded.
"""

from __future__ import annotations

import copy
import time
from itertools import islice

import torch
from hunt_cells import BATCH_CAP, _credit, _updates

from computronium import (
    DigitalSubstrate,
    FeedforwardGeometry,
    GeometryConfig,
    InstantaneousDynamics,
    SubstrateConfig,
    SystemState,
    create_task,
)
from computronium.core.system_trainer.factory import compose_system

SEEDS = (0, 1, 2)
PROBE_EVERY = 10


def _eval(system, test_batches) -> float:
    ok = tot = 0
    with torch.no_grad():
        for batch_x, batch_y in test_batches:
            state = system.dynamics.settle(
                SystemState(x=batch_x), system.geometry, system.substrate, None
            )
            acts = state.activations
            out = acts[-1] if isinstance(acts, list) else acts
            ok += (out.argmax(1) == batch_y).sum().item()
            tot += batch_y.size(0)
    return ok / tot


def _run_harvest(seed: int, train_data, test_batches) -> tuple[float, float]:
    torch.manual_seed(seed)
    system = compose_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
        geometry=FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=784, output_dim=10, hidden_dims=(64, 64)
            )
        ),
        dynamics=InstantaneousDynamics(),
        credit=_credit("pepita"),
        update=_updates()["muon"](),
    )
    from computronium.core.pipeline import run_train_step

    best_val, best_params, final_val = 0.0, None, 0.0
    for step, (x, y) in enumerate(train_data):
        run_train_step(
            system.substrate,
            system.geometry,
            system.dynamics,
            system.credit,
            system.update,
            x,
            y,
        )
        if step % PROBE_EVERY == 0 or step == len(train_data) - 1:
            val = _eval(system, test_batches)
            final_val = val
            if val > best_val:
                best_val = val
                best_params = copy.deepcopy(dict(system.geometry.params))
    if best_params is not None:
        system.geometry.update_params(best_params)
    best_restored = _eval(system, test_batches)
    return final_val, max(best_val, best_restored)


def main() -> int:
    t0 = time.time()
    task = create_task("mnist", device="cpu", quick_mode=True, num_workers=0)
    task.setup()
    torch.manual_seed(0)
    train_data = [
        (xb.view(xb.size(0), -1), yb)
        for xb, yb in islice(task.get_dataloader("train"), BATCH_CAP)
    ]
    test_batches = [(xb, yb) for xb, yb in task.get_dataloader("test")][:20]

    finals, bests = [], []
    for seed in SEEDS:
        final, best = _run_harvest(seed, train_data, test_batches)
        finals.append(final)
        bests.append(best)
        print(f"seed {seed}: final {final:.3f}  best {best:.3f}", flush=True)

    mean_final = sum(finals) / len(finals)
    mean_best = sum(bests) / len(bests)
    print(
        f"\nfinal mean {mean_final:.3f} (ladder recorded 0.306)  "
        f"harvest mean {mean_best:.3f}",
        flush=True,
    )
    if mean_best >= 0.40:
        verdict = "REOPENED — LEMMA × Muon passes the 0.40 bar under harvesting"
    elif mean_best - mean_final < 0.03:
        verdict = "BOUNDARY STANDS — plateau, no peak-hiding artifact"
    else:
        verdict = "ARTIFACT — peak materially above final but below the bar"
    print(f"VERDICT: {verdict}", flush=True)
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
