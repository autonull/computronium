"""W1 credit-degradation ladder (TODO14 §7): how weak can credit get before
the optimizer stops recovering it? — the I(C,U) interaction matrix.

TODO14 §7's design: run a credit ladder (BP → FF → PEPITA → weakened
random-projection cells) under {euclid, muon, ortho_adam} on MNIST
(150 batches, 1 epoch, seeds 0-2, test accuracy) and read the
interaction A(C,U) = A(C,U) − A(C,U₀) − A(C₀,U) + A(C₀,U₀).

Ladder (weakest link = the feedback channel; hunt_cells harness reused
verbatim, credit cell rows extended):
- bp            exact credit (control, A(C₀,U₀) anchor)
- ff            layer-local goodness, no feedback channel
- pepita        fixed random feedback B at the default beta 0.5
- rp_weak       random_projections, feedback_scale 1e-3 (100× weaker B
                injection — the "noisy/degenerate" rung without inventing
                a new primitive: weaker B = lower-SNR credit direction)
- rp_ortho      random_projections with orthogonal_init (structured B)

Pre-registered predictions:
- P1 (interaction sign): muon/ortho raise the weak-credit rungs more
  than bp (positive I(C,U) concentrated on degenerate credit) — the SP2
  replication at ladder resolution. Falsified -> the optimizer rescue is
  a strong-credit-only effect.
- P2 (boundary sharpness): performance collapses sharply (to ≤ chance
  +0.05) beyond some rung under ALL optimizers -> a measurable
  credit-quality boundary. If instead rp_weak stays competitive under
  muon, "the optimizer does the learning" extends one full ladder rung.

Run: ``uv run python scripts/probes/w1_credit_ladder.py`` (~6 min CPU).
Walltime printed, never recorded.
"""

from itertools import islice

import numpy as np
import torch
from hunt_cells import BATCH_CAP

from computronium import CreditAssignmentConfig, LocalGoodnessCredit


def _credit(name: str):
    if name == "bp":
        from computronium import BackpropCredit

        return BackpropCredit()
    if name.startswith("rp_"):
        # NOTE: RandomProjectionsCredit is the FA/DFA class; handing its
        # config to LocalGoodnessCredit silently runs pure FF (audit note).
        from computronium import RandomProjectionsCredit

        scale = {
            "rp_weak": 1e-3,
            "rp_ortho": 0.01,
            "rp_vweak": 1e-4,
        }[name]
        return RandomProjectionsCredit(
            CreditAssignmentConfig.random_projections(
                beta=0.5,
                feedback_scale=scale,
                orthogonal_init=name == "rp_ortho",
            )
        )
    objective = "ff" if name == "ff" else "pepita"
    return LocalGoodnessCredit(
        CreditAssignmentConfig.local_goodness(
            feedback_scale=0.01, local_objective=objective
        )
    )


def _register_updates() -> None:
    import hunt_cells

    from computronium import OrthoAdamUpdate, ParameterUpdateConfig

    base = hunt_cells._updates
    hunt_cells._updates = lambda: {
        **base(),
        "ortho": lambda: OrthoAdamUpdate(
            ParameterUpdateConfig.ortho_adam(step_size=0.02, ortho_lr=1e-3)
        ),
    }


# Session-2 grid (euclid/muon, logs/w1_credit_ladder.log) is recorded;
# the extension grid re-measures only the ortho column + the rp_vweak
# rung (feedback_scale 1e-4 — hunting the muon recovery edge).
CELLS = [
    ("bp", "ortho"),
    ("ff", "ortho"),
    ("pepita", "ortho"),
    ("rp_weak", "ortho"),
    ("rp_ortho", "ortho"),
    ("rp_vweak", "euclid.2"),
    ("rp_vweak", "muon"),
    ("rp_vweak", "ortho"),
]
SEEDS = (0, 1, 2)

# Session-2 recorded means (euclid.2 / muon), reused for the interaction
# table instead of re-measuring (reproduction: two runs identical to 3
# decimals, logs/w1_credit_ladder.log).
_SESSION2 = {
    ("bp", "euclid.2"): 0.816,
    ("bp", "muon"): 0.919,
    ("ff", "euclid.2"): 0.825,
    ("ff", "muon"): 0.896,
    ("pepita", "euclid.2"): 0.101,
    ("pepita", "muon"): 0.306,
    ("rp_weak", "euclid.2"): 0.308,
    ("rp_weak", "muon"): 0.870,
    ("rp_ortho", "euclid.2"): 0.326,
    ("rp_ortho", "muon"): 0.873,
}


def main() -> int:
    import time

    t0 = time.time()
    from computronium import create_task

    only = None
    for a in __import__("sys").argv:
        if a.startswith("--only="):
            only = set(a.removeprefix("--only=").split(","))

    task = create_task("mnist", device="cpu", quick_mode=True, num_workers=0)
    task.setup()
    torch.manual_seed(0)  # seed BEFORE the loader draw (D8 trap)
    train_loader = task.get_dataloader("train")  # pyright: ignore[reportAttributeAccessIssue] — duck-typed task
    test_loader = task.get_dataloader("test")  # pyright: ignore[reportAttributeAccessIssue]
    train_data = [
        (xb.view(xb.size(0), -1), yb) for xb, yb in islice(train_loader, BATCH_CAP)
    ]
    test_batches = [
        (xb.view(xb.size(0), -1), yb) for xb, yb in test_loader if xb.size(0) == 32
    ]

    import hunt_cells

    hunt_cells._credit = _credit  # rebind the ladder into the harness
    _register_updates()
    results: dict[tuple[str, str], float] = {
        k: v for k, v in _SESSION2.items() if only is None or k[1] == "euclid.2"
    }
    for credit, update in CELLS:
        if only is not None and (credit, update) not in only:
            continue
        accs = [
            hunt_cells._run(credit, update, s, train_data, test_batches) for s in SEEDS
        ]
        results[credit, update] = float(np.mean(accs))
        print(
            f"{credit:>8} x {update:>8}: {np.mean(accs):.3f} ± {np.std(accs):.3f} "
            f"{accs}",
            flush=True,
        )

    for update in ("muon", "ortho"):
        a0 = results["bp", update] - results["bp", "euclid.2"]
        print(f"\n=== I(C,U) interaction ({update} vs euclid.2, anchor = bp) ===")
        for credit in ("ff", "pepita", "rp_weak", "rp_ortho", "rp_vweak"):
            if (credit, update) not in results:
                continue
            a = results[credit, update] - results[credit, "euclid.2"]
            print(f"  {credit:>8}: Δ {a:+.3f}  I(C,U) {a - a0:+.3f}", flush=True)

    print(f"\nwalltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
