"""W1 lattice cell (TODO14 §7): the I(C,U) interaction table on a SECOND
geometry — the Tier D qualification for the credit-optimizer law.

Session-2/3 established on the MLP geometry (logs/w1_credit_ladder*.log)
an OPTIMIZER-SPECIFIC RECOVERY PROFILE: muon thresholdlessly rescues
degenerate credit (rp rungs I ≈ +0.46, even at feedback_scale 1e-4),
ortho_adam has a sharp rescue boundary between 1e-4 and 1e-3, and sign
rules (lion) are blind to sub-dominant credit. The prediction to test
here is that this PROFILE — not just "some rescue" — replicates on
SpatialLattice3DGeometry (4,3,3), the hunt_hybrid second geometry.

Probe rules (§19):
- question: does the I(C,U) recovery profile predict across geometry?
- mechanism: same credit ladder {bp, ff, pepita, rp_weak, rp_ortho,
  rp_vweak} x {euclid.2, muon, ortho} on lattice3d, MNIST 150 batches,
  seeds 0-2, test accuracy; hunt_cells harness reused verbatim with a
  lattice `_run` (credit ladder + update registry imported from
  w1_credit_ladder / hunt_cells).
- prediction (pre-registered): muon rescues the rp rungs on lattice
  (I > +0.3) and ortho shows the same 1e-4-vs-1e-3 sharp boundary
  (rp_vweak x ortho collapses relative to rp_weak x ortho).
- falsification: if the lattice interaction pattern disagrees (rp rungs
  NOT rescued under muon, or ortho rescuing rp_vweak where muon's
  profile is the thresholdless one), the recovery profile is
  geometry-specific and Tier D's "predictive" claim narrows.
- budget: 18 cells x 3 seeds (~lattice settle cost, est. <15 min CPU).

MEASURED RESULT (2026-09-07, logs/w1_lattice_ladder.log): the rp rungs
(rp_weak / rp_ortho / rp_vweak) are CONTRACT-INERT on lattice — the
layered FA/DFA walk cannot chain over a settle stream that omits the
raw input and per-site weights, so the credit returns all-zeros and
those rows are byte-identical no-training runs at chance (0.102 across
all three feedback scales AND both B structures — the inertness
signature). They must be read as a no-op control, not credit evidence.
The realizable ladder on lattice is {bp, ff, pepita}; pepita needed the
covariate-pairing fix in _pepita_gradient (input prepended when the
settle stream omits it; reproduces the shipped acts[k] pairing on
stack geometries).

Run: ``uv run python scripts/probes/w1_lattice_ladder.py``
Optional ``--only=credit,update`` filter. Walltime printed, never recorded.
"""

from itertools import islice

import numpy as np
import torch
from hunt_cells import BATCH_CAP
from w1_credit_ladder import _credit, _register_updates

from computronium import (
    GeometryConfig,
    SpatialLattice3DGeometry,
    SystemState,
    SystemTrainer,
    SystemTrainerConfig,
    compose_system,
    create_task,
)

SEEDS = (0, 1, 2)

CELLS = [
    (credit, update)
    for update in ("euclid.2", "muon", "ortho")
    for credit in ("bp", "ff", "pepita", "rp_weak", "rp_ortho", "rp_vweak")
]


def _run(credit: str, update: str, seed: int, train_data, test_batches) -> float:
    import hunt_cells

    from computronium import (
        DigitalSubstrate,
        InstantaneousDynamics,
        StateDynamicsConfig,
        SubstrateConfig,
    )

    torch.manual_seed(seed)
    system = compose_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
        geometry=SpatialLattice3DGeometry(
            GeometryConfig.spatial_lattice(
                input_dim=784,
                output_dim=10,
                lattice_dims=(4, 3, 3),
                hidden_dims=(2,),
                connectivity_radius=1,
            )
        ),
        dynamics=InstantaneousDynamics(StateDynamicsConfig.instantaneous()),
        credit=_credit(credit),
        update=hunt_cells._updates()[update](),
    )
    SystemTrainer(
        system=system,
        config=SystemTrainerConfig(max_epochs=1, device="cpu", seed=42),
        train_data=train_data,
    ).fit()
    ok = tot = 0
    with torch.no_grad():
        for batch_x, batch_y in test_batches:
            # SystemState is duck-typed for CompositeState (hunt_cells pattern).
            state = system.dynamics.settle(
                SystemState(x=batch_x),  # pyright: ignore[reportArgumentType]
                system.geometry,
                system.substrate,
                None,
            )
            acts = state.activations
            out = acts[-1] if isinstance(acts, list) else acts
            assert out is not None  # settle always emits activations here
            ok += (out.argmax(1) == batch_y).sum().item()
            tot += batch_y.size(0)
    return ok / tot


def main() -> int:
    import time

    t0 = time.time()
    only = None
    for a in __import__("sys").argv:
        if a.startswith("--only="):
            credit, update = a.removeprefix("--only=").split(",")
            only = {(credit, update)}

    task = create_task("mnist", device="cpu", quick_mode=True, num_workers=0)
    task.setup()
    torch.manual_seed(0)  # seed BEFORE the loader draw (D8 trap)
    train_loader = task.get_dataloader("train")  # pyright: ignore[reportAttributeAccessIssue]
    test_loader = task.get_dataloader("test")  # pyright: ignore[reportAttributeAccessIssue]
    train_data = [
        (xb.view(xb.size(0), -1), yb) for xb, yb in islice(train_loader, BATCH_CAP)
    ]
    test_batches = [
        (xb.view(xb.size(0), -1), yb) for xb, yb in test_loader if xb.size(0) == 32
    ]

    _register_updates()
    results: dict[tuple[str, str], float] = {}
    for credit, update in CELLS:
        if only is not None and (credit, update) not in only:
            continue
        accs = [_run(credit, update, s, train_data, test_batches) for s in SEEDS]
        results[credit, update] = float(np.mean(accs))
        print(
            f"{credit:>8} x {update:>8}: {np.mean(accs):.3f} ± {np.std(accs):.3f} "
            f"{accs}",
            flush=True,
        )

    if ("bp", "euclid.2") in results:
        for update in ("muon", "ortho"):
            if ("bp", update) not in results:
                continue
            a0 = results["bp", update] - results["bp", "euclid.2"]
            print(f"\n=== I(C,U) on lattice ({update} vs euclid.2, anchor = bp) ===")
            for credit in ("ff", "pepita", "rp_weak", "rp_ortho", "rp_vweak"):
                if (credit, update) not in results:
                    continue
                a = results[credit, update] - results[credit, "euclid.2"]
                print(f"  {credit:>8}: Δ {a:+.3f}  I(C,U) {a - a0:+.3f}", flush=True)

    print(f"\nwalltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
