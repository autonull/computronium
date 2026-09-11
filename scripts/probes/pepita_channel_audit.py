"""PEPITA inert-channel audit (TODO15 §8.3, defect-hunt before verdict):
does the fixed-B feedback channel actually modulate the pseudo-gradients
of the hunt_cells pepita rung (LocalGoodnessCredit, local_objective=
"pepita", feedback_scale 0.01)?

Prior precedent: RandomProjectionsCredit handed to LocalGoodnessCredit
silently ran pure FF (w1_credit_ladder audit note). If the pepita rung
is also channel-inert, its 0.306 boundary verdict is void and must be
re-attributed to a different mechanism.

Method: identical batch, identical init; pseudo-gradients at
feedback_scale ∈ {0.0, 0.01, 1.0}. Channel live iff grad(0.01) differs
from grad(0.0) AND scales with the B magnitude (‖g(1.0)‖ ≈ 100×
‖g(0.01)‖ modulo normalization). Also: per-layer nonzero norms (does
credit reach every weight?).

uv run python scripts/probes/pepita_channel_audit.py
Walltime printed, never recorded.
"""

from __future__ import annotations

import time

import torch


from computronium import (  # type: ignore[attr-defined]
    CreditAssignmentConfig,
    DigitalSubstrate,
    FeedforwardGeometry,
    GeometryConfig,
    InstantaneousDynamics,
    LocalGoodnessCredit,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemState,
    create_task,
)
from computronium.ontology.credit import Phase

WIDTH = 32
DEPTH = 8
SCALES = (0.0, 0.01, 1.0)


def main() -> int:
    t0 = time.time()
    task = create_task("mnist", device="cpu", quick_mode=True, num_workers=0)
    task.setup()
    torch.manual_seed(0)  # D8 trap: seed BEFORE the loader draw
    x, y = next(iter(task.get_dataloader("train")))
    x = x.view(x.size(0), -1)

    grads_by_scale: dict[float, list[torch.Tensor]] = {}
    for scale in SCALES:
        torch.manual_seed(0)
        geometry = FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=784, output_dim=10, hidden_dims=(WIDTH,) * DEPTH
            )
        )
        substrate = DigitalSubstrate(SubstrateConfig.digital(device="cpu"))
        dynamics = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
        credit = LocalGoodnessCredit(
            CreditAssignmentConfig.local_goodness(
                feedback_scale=scale, local_objective="lemma"
            )
        )
        # mirror run_train_step wiring: both phase states carry y; only
        # the settle target differs (PEPITA reads free_state.y)
        free = dynamics.settle(SystemState(x=x, y=y), geometry, substrate, None)
        nudged = dynamics.settle(SystemState(x=x, y=y), geometry, substrate, y)
        phases = {Phase.FREE: free, Phase.NUDGED: nudged}
        grads = credit.compute_pseudo_gradient(phases, None, geometry)
        grads_by_scale[scale] = grads
        norms = [f"{g.norm().item():.2e}" for g in grads]
        print(f"feedback_scale {scale}: per-weight norms {' '.join(norms)}", flush=True)

    zero, mid, full = (grads_by_scale[s] for s in SCALES)
    diff = sum((m - z).abs().sum().item() for m, z in zip(mid, zero, strict=True))
    ratio = sum(m.norm().item() for m in mid) / max(
        sum(f.norm().item() for f in full), 1e-30
    )
    print(f"‖g(0.01) − g(0.0)‖₁ {diff:.3e}", flush=True)
    print(f"norm(g(0.01))/norm(g(1.0)) {ratio:.4f}", flush=True)
    live = diff > 0 and 1e-4 < ratio < 1e4
    print(
        f"\nVERDICT: {'CHANNEL LIVE — boundary verdict stands' if live else 'CHANNEL INERT/ANOMALOUS — 0.306 verdict void, re-attribute'}",
        flush=True,
    )
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
