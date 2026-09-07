"""H7 probe (TODO12b): D22's routing-mode flip — did the EVAL branch run?

Verdict (2026-09-06): REFUTED (flip did not matter) — D22's miss stands,
now defect-audited.

Code-read: RoutingPlasticity.step picks hard top-k when no theta param
requires grad (routing.py: is_training = any(p.requires_grad ...)).
With theta frozen in D22's psi-only training, the Gumbel path never
ran. BUT the branch only changes `active_routes`; `modulate` reads
`gate_logits` ONLY (sigmoid(gate_logits @ U_l)) — the pipeline consumes
modulate's output, never active_routes, and the gate_logits update
itself is branch-independent (decay + lr * x @ G).

Measured (CPU, seed 0, 200 steps, batch 4, gate_dim 16, frozen theta
context): gate_logits trajectories under the eval branch vs the forced
training branch are BITWISE IDENTICAL (max abs diff = 0.0 over all 200
steps), because the logits update never touches the branch and
modulate ignores active_routes. B-side accuracy is therefore unchanged
by construction — no re-run of D22 needed.
"""

import time

import torch

from computronium.core.plasticity.routing import RoutingPlasticity
from computronium.state import CompositeState


class _FrozenContext:
    """Duck-typed SystemContext with frozen theta (D22's psi-only setup).

    SystemContext.__post_init__ REQUIRES theta.requires_grad=True, so a
    frozen-theta episode can only arise through a duck-typed context —
    exactly how the D22 harness ran.
    """

    def __init__(self) -> None:
        self.theta = {"0.weight": torch.zeros(1, 1)}
        self.device = torch.device("cpu")


def main() -> None:
    t0 = time.perf_counter()
    torch.manual_seed(0)
    plasticity = RoutingPlasticity(gate_dim=16)
    ctx = _FrozenContext()
    x = torch.randn(4, 32)
    psi_eval = plasticity.initial_psi(ctx, batch_size=4)
    psi_train = plasticity.initial_psi(ctx, batch_size=4)
    max_diff = 0.0
    for _ in range(200):
        z = CompositeState(activity={"x": x}, plastic={}, substrate={})
        psi_eval = plasticity.step(psi_eval, z, ctx)
        # Force the training branch: temporarily mark theta as trainable.
        for p in ctx.theta.values():
            p.requires_grad_(True)
        psi_train = plasticity.step(psi_train, z, ctx)
        for p in ctx.theta.values():
            p.requires_grad_(False)
        max_diff = max(
            max_diff,
            (psi_eval["gate_logits"] - psi_train["gate_logits"]).abs().max().item(),
        )
    mod_eval = plasticity.modulate([x], psi_eval)
    mod_train = plasticity.modulate([x], psi_train)
    mod_diff = (mod_eval[0] - mod_train[0]).abs().max().item()
    print(
        f"gate_logits max|diff| over 200 steps: {max_diff}\n"
        f"modulate output max|diff|: {mod_diff}\n"
        f"walltime: {time.perf_counter() - t0:.1f}s"
    )


if __name__ == "__main__":
    main()
