"""Routing × depth (TODO16 §2.2): does per-unit routing gate prevent
late-layer memorization / depth collapse?

Arms (capacity-matched within depth): Null×d32, Routing(gate_dim=32)×d32,
Routing×d50. Joint systems: Digital ⊗ FeedforwardDAG (mupc, residual) ⊗
EPC (max_steps 5) ⊗ {Null, Routing} ⊗ BackpropCredit ⊗ OrthoAdam.
MNIST quick, 150 batches, 1 seed (screen; promotion adds seeds 1-2).

Pre-registered: Routing×d50 ≥ Null×d32 × 0.90 (≥ ~0.83 given the d32
frontier) → depth boundary is compute-limited. Falsification:
Routing×d50 < 0.83 → the boundary is representation-limited; routing
does not solve peak-then-memorize.

uv run python scripts/probes/w16_routing_depth.py [--seed=0] [--batches=150]
Walltime printed, never recorded.
"""

from __future__ import annotations

import sys
import time
from itertools import islice

import torch

from computronium import (
    BackpropCredit,
    DigitalSubstrate,
    ErrorPredictiveCodingDynamics,
    FeedforwardGeometry,
    GeometryConfig,
    NullPlasticity,
    OrthoAdamUpdate,
    ParameterUpdateConfig,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemState,
    SystemTrainer,
    SystemTrainerConfig,
    compose_joint_system,
    create_task,
)
from computronium.core.plasticity import RoutingPlasticity

BATCHES = 150
WIDTH = 128
SEED = 0
CHANCE = 0.1


def _run(depth: int, routing: bool, train, test, seed: int) -> float:
    torch.manual_seed(seed)
    plasticity = RoutingPlasticity(gate_dim=32) if routing else NullPlasticity()
    system = compose_joint_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
        geometry=FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=784,
                output_dim=10,
                hidden_dims=(WIDTH,) * depth,
                init_scheme="mupc",
                residual=True,
            )
        ),
        dynamics=ErrorPredictiveCodingDynamics(
            StateDynamicsConfig.error_predictive_coding(
                max_steps=5, step_size=0.5, beta=0.5
            )
        ),
        plasticity=plasticity,
        credit=BackpropCredit(),
        update=OrthoAdamUpdate(ParameterUpdateConfig.ortho_adam(step_size=1e-3)),
    )
    config = SystemTrainerConfig(
        max_epochs=1, device="cpu", seed=seed, log_every_n_steps=10_000
    )
    SystemTrainer(system=system, config=config, train_data=train).fit()
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


def main() -> int:  # ruff: ignore[too-many-locals] - probe harness
    t0 = time.time()
    args = sys.argv[1:]
    opt = dict(a[2:].split("=") for a in args if a.startswith("--") and "=" in a)
    seed = int(opt.get("seed", SEED))
    batches = int(opt.get("batches", BATCHES))
    task = create_task("mnist", device="cpu", quick_mode=True, num_workers=0)
    task.setup()
    torch.manual_seed(0)  # seed BEFORE the loader draw (D8 trap)
    train = list(islice(task.get_dataloader("train"), batches))
    test = [
        (x.view(x.size(0), -1), y) for x, y in islice(task.get_dataloader("test"), 20)
    ]
    train = [(x.view(x.size(0), -1), y) for x, y in train]

    arms_available = {
        "null_d32": (32, False),
        "routing_d32": (32, True),
        "routing_d50": (50, True),
        "routing_d64": (64, True),
        "routing_d100": (100, True),
    }
    requested = opt.get("arms")
    arms = (
        {name: arms_available[name] for name in requested.split(",") if name}
        if requested
        else arms_available
    )
    results = {}
    for name, (depth, routing) in arms.items():
        results[name] = _run(depth, routing, train, test, seed)
        print(f"{name:>12}: {results[name]:.3f}", flush=True)
    null32 = results["null_d32"]
    routed = {k: v for k, v in results.items() if k != "null_d32"}
    best_name = max(routed, key=routed.get)
    gate = 0.90 * null32
    print(
        f"\nfrontier Null×d32 {null32:.3f}; gate {gate:.3f}; "
        f"best routed {best_name} {routed[best_name]:.3f}"
    )
    verdict = (
        "COMPUTE-LIMITED (routing holds the depth frontier)"
        if routed[best_name] >= gate
        else "REPRESENTATION-LIMITED — routing does not solve peak-then-memorize"
    )
    print(f"VERDICT: {verdict}")
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
