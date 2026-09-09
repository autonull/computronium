"""TODO16 §7.1 P-axis × credit × update campaign, SUBSET driver.

Fixed: Digital ⊗ FeedforwardDAG (mupc, residual, d32, width 128) ⊗
EPC (max_steps 5). Varied: P × C × U, 3 seeds, 150 batches MNIST.

Subsets (= one P axis value each) give intermediate feedback:

  A  --p=null         4 C × 2 U × 3 seeds = 24 cells   (baseline surface)
  B  --p=routing      same grid with RoutingPlasticity(gate_dim=32)
  C  --p=fastweight   same grid with FastWeightPlasticity(dim 64)

C ∈ {bp, fa(RandomProjectionsCredit), pepita, lg(LocalGoodnessCredit)},
U ∈ {muon(0.02, m 0.9), ortho(0.02, ortho_lr 1e-3)} — recorded lr tables
(w1_credit_ladder / recipe cards), no per-cell screens.

Pre-registered (7.1 hypothesis): ψ modulates the I(C,U) surface — i.e.
some |acc(P=ψ, C, U) − acc(P=null, C, U)| ≥ 0.03 at matched budget.
Falsification: all deltas < 0.03 → P is a passenger on this surface.
FastWeight inertness is pre-declared as a WIRING outcome, not a
capability verdict: if C-subset cells are bitwise-identical to the
null subset, the joint settle harness does not route fast-weight
modulation (same failure class as the RandomProjections inertness
guard), and the cell is recorded as wiring-limited.

Run (one subset):  uv run python scripts/probes/w16_campaign.py --p=routing --seeds=0,1,2
Per-seed shards for parallelism:  --seeds=0 / --seeds=1 / --seeds=2
Walltime printed, never recorded.
"""

from __future__ import annotations

import sys
import time
from itertools import islice

import numpy as np
import torch

from computronium import (
    BackpropCredit,
    CreditAssignmentConfig,
    DigitalSubstrate,
    ErrorPredictiveCodingDynamics,
    FastWeightPlasticity,
    FeedforwardGeometry,
    GeometryConfig,
    LocalGoodnessCredit,
    NullPlasticity,
    OrthoAdamUpdate,
    ParameterUpdateConfig,
    PepitaCredit,
    RandomProjectionsCredit,
    RiemannianOrthogonalUpdate,
    RoutingPlasticity,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemState,
    SystemTrainer,
    SystemTrainerConfig,
    compose_joint_system,
    create_task,
)

BATCHES = 150
DEPTH = 32
WIDTH = 128

CREDITS = ("bp", "fa", "pepita", "lg")
UPDATES = ("muon", "ortho")
LRS = {
    "muon": float(__import__("os").environ.get("W16_MUON_LR", 0.005)),
    "ortho": 0.02,
    "euclid": 0.02,
}  # muon 0.005: d32 screen (0.02 = 0.637)


def _credit(name: str):
    match name:
        case "bp":
            return BackpropCredit()
        case "fa":
            return RandomProjectionsCredit(
                CreditAssignmentConfig.random_projections(beta=0.5, feedback_scale=1e-3)
            )
        case "pepita":
            return PepitaCredit()
        case "lg":
            return LocalGoodnessCredit(
                CreditAssignmentConfig.local_goodness(
                    feedback_scale=0.01, local_objective="lemma"
                )
            )
        case _:
            raise ValueError(name)


def _update(name: str):
    lr = float(__import__("os").environ.get("W16_" + name.upper() + "_LR", LRS[name]))
    if name == "muon":
        return RiemannianOrthogonalUpdate(
            ParameterUpdateConfig.riemannian_orthogonal(step_size=lr, momentum=0.9)
        )
    if name == "euclid":
        from computronium import EuclideanUpdate

        return EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=lr))
    return OrthoAdamUpdate(
        ParameterUpdateConfig.ortho_adam(step_size=lr, ortho_lr=1e-3)
    )


def _plasticity(p: str):
    match p:
        case "null":
            return NullPlasticity()
        case "routing":
            return RoutingPlasticity(gate_dim=32)
        case "fastweight":
            return FastWeightPlasticity(fast_weight_dim=64)
        case _:
            raise ValueError(p)


def _cell(p: str, credit: str, update: str, train, test, seed: int) -> float:
    torch.manual_seed(seed)
    system = compose_joint_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
        geometry=FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=784,
                output_dim=10,
                hidden_dims=(WIDTH,) * DEPTH,
                init_scheme="mupc",
                residual=True,
            )
        ),
        dynamics=ErrorPredictiveCodingDynamics(
            StateDynamicsConfig.error_predictive_coding(
                max_steps=5, step_size=0.5, beta=0.5
            )
        ),
        plasticity=_plasticity(p),
        credit=_credit(credit),
        update=_update(update),
    )
    SystemTrainer(
        system=system,
        config=SystemTrainerConfig(
            max_epochs=1, device="cpu", seed=seed, log_every_n_steps=10_000
        ),
        train_data=train,
    ).fit()
    system.geometry.eval()
    ok = tot = 0
    with torch.no_grad():
        for x, y in test:
            state = system.dynamics.settle(
                SystemState(x=x), system.geometry, system.substrate, None
            )
            acts = state.activations
            out = acts[-1] if isinstance(acts, list) else acts
            ok += (out.argmax(1) == y).sum().item()
            tot += y.size(0)
    return ok / tot


def main() -> int:
    t0 = time.time()
    args = sys.argv[1:]
    opt = dict(a[2:].split("=", 1) for a in args if a.startswith("--") and "=" in a)
    p = opt.get("p", "null")
    credits = (opt.get("credits") or ",".join(CREDITS)).split(",")
    updates = (opt.get("updates") or ",".join(UPDATES)).split(",")
    seeds = [int(s) for s in (opt.get("seeds") or "0,1,2").split(",")]

    task = create_task("mnist", device="cpu", quick_mode=True, num_workers=0)
    task.setup()
    torch.manual_seed(0)  # seed BEFORE the loader draw (D8 trap)
    train = [
        (x.view(x.size(0), -1), y)
        for x, y in islice(task.get_dataloader("train"), BATCHES)
    ]
    test = [
        (x.view(x.size(0), -1), y) for x, y in islice(task.get_dataloader("test"), 20)
    ]

    print(
        f"w16_campaign 7.1 subset p={p} credits={credits} updates={updates}"
        f" seeds={seeds} d{DEPTH} w{WIDTH} batches {BATCHES}",
        flush=True,
    )
    results: dict[tuple[str, str], list[float]] = {}
    for credit in credits:
        for update in updates:
            accs = []
            for seed in seeds:
                acc = _cell(p, credit, update, train, test, seed)
                accs.append(acc)
                print(
                    f"  {p:>10} x {credit:>6} x {update:>5} seed {seed}: {acc:.3f}",
                    flush=True,
                )
            results[credit, update] = accs

    print(f"\n=== 7.1 subset p={p}: mean ± std over seeds ===")
    inert = True
    for (credit, update), accs in results.items():
        m, s = np.mean(accs), np.std(accs)
        if len(set(accs)) > 1:
            inert = False
        print(f"{credit:>6} x {update:>5}: {m:.3f} ± {s:.3f}  {accs}")
    if p != "null" and inert:
        print(
            "INERTNESS SUSPECT: all cells bitwise-identical across seeds —"
            " ψ wiring may be a no-op in this harness; compare against the"
            " null subset before any capability claim."
        )
    print(f"\nwalltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
