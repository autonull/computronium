"""W7.1 last rung — learned-B PEPITA × Muon 0.02 (TODO15 §9.7 #4).

The fixed-B rung is boundary-locked twice (0.306 width-32, 0.214 depth-8
lattice). The only untested PEPITA cell: credit-internal learned B
(ridge-regression inverse projections, RESEARCH4 Fix 1a) under the
Muon-class optimizer. hunt_cells harness reused verbatim (width-64×2 MLP,
150 batches, seeds 0-2, test acc).

Pre-registered (TODO15 §2.1 bar): mean ≥ 0.65 → Reopened; < 0.40 →
Boundary closes the whole PEPITA family.

uv run python scripts/probes/w7_pepita_learned_b.py
Walltime printed, never recorded.
"""

from __future__ import annotations

import sys
import time
from itertools import islice

import numpy as np
import torch

sys.path.insert(0, "scripts/probes")

from hunt_cells import BATCH_CAP, SEEDS  # noqa: E402

from computronium import (  # type: ignore[attr-defined]  # noqa: E402
    CreditAssignmentConfig,
    DigitalSubstrate,
    FeedforwardGeometry,
    GeometryConfig,
    InstantaneousDynamics,
    LocalGoodnessCredit,
    ParameterUpdateConfig,
    RiemannianOrthogonalUpdate,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemState,
    SystemTrainer,
    SystemTrainerConfig,
    compose_system,
    create_task,
)

LR = 0.02


def _run_learned(seed: int, train_data, test_batches) -> float:
    torch.manual_seed(seed)
    system = compose_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
        geometry=FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=784, output_dim=10, hidden_dims=(64, 64)
            )
        ),
        dynamics=InstantaneousDynamics(StateDynamicsConfig.instantaneous()),
        credit=LocalGoodnessCredit(
            CreditAssignmentConfig.local_goodness(
                feedback_scale=0.01,
                local_objective="pepita",
                learned_feedback=True,
            )
        ),
        update=RiemannianOrthogonalUpdate(
            ParameterUpdateConfig.riemannian_orthogonal(step_size=LR, momentum=0.9)
        ),
    )
    SystemTrainer(
        system=system,
        config=SystemTrainerConfig(max_epochs=1, device="cpu", seed=42),
        train_data=train_data,
    ).fit()
    ok = tot = 0
    with torch.no_grad():
        for bx, by in test_batches:
            state = system.dynamics.settle(
                SystemState(x=bx), system.geometry, system.substrate, None
            )
            acts = state.activations
            out = acts[-1] if isinstance(acts, list) else acts
            ok += (out.argmax(1) == by).sum().item()
            tot += by.size(0)
    return ok / tot


def main() -> int:
    t0 = time.time()
    task = create_task("mnist", device="cpu", quick_mode=True, num_workers=0)
    task.setup()
    torch.manual_seed(0)  # D8 trap: seed BEFORE the loader draw
    train_data = [
        (xb.view(xb.size(0), -1), yb)
        for xb, yb in islice(task.get_dataloader("train"), BATCH_CAP)
    ]
    test_batches = [
        (xb.view(xb.size(0), -1), yb)
        for xb, yb in task.get_dataloader("test")
        if xb.size(0) == 32
    ]

    accs = [_run_learned(s, train_data, test_batches) for s in SEEDS]
    print(
        f"learned-B pepita x muon {LR}: {np.mean(accs):.3f} ± {np.std(accs):.3f} {accs}",
        flush=True,
    )
    mean = float(np.mean(accs))
    if mean >= 0.65:
        verdict = "REOPENED"
    elif mean < 0.40:
        verdict = "BOUNDARY — the PEPITA family closes"
    else:
        verdict = "INTERMEDIATE — below reopen bar, above fixed-B"
    print(f"\nVERDICT: {verdict}", flush=True)
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
