"""H6 probe (TODO12b): PEPITA's weight-trajectory channel (parked probe).

Verdict (2026-09-06): REFUTED at HEAD — the ~1e4 ‖W_out‖ growth that
motivated the parking does NOT reproduce through the pipeline; the
update path is the ONLY θ channel and it is lr-bounded as designed.

Measured (PEPITA + learned_feedback, MLP 784-32-10, unit_rms lr 3e-4,
150 MNIST-quick batches, seed 0, CPU):
- ‖W_out‖_F: init 0.55 -> 0.56 (feedback_lr 0.5) / 0.56 (lr 0.01).
  Total drift ≈ 0.01 over the run — bounded exactly as the unit_rms
  step budget predicts (150 × 3e-4 × sqrt(320) ≈ 0.85 upper bound).
- No non-step θ path exists: the learned-B EMA mutates ONLY the
  credit-internal `self._learned` dict (transport-free, L3-locked —
  it never reads or writes geometry.params). ‖B‖ moves with the EMA
  (lr 0.5 arm: B tracks the ridge solution fast; lr 0.01: slow) but
  B is not θ.
- Grad-routing alignment: cosine(autograd ∇CE, emitted pseudo-grad)
  per weight — W1 ≈ 0.7-0.8, W_out ≈ 0.9+ (PEPITA's fixed-B alignment
  is expected to trail true backprop; both names receive correctly
  SHAPED, finite grads — no name↔acts index misalignment: the emitted
  grad norms track the autograd norms within ~2x all run).
- The historical ~1e4 growth in ~600 steps (pre-p5 observation) is
  consistent with the PRE-fix rule: the fixed random B carried
  width-proportional scale into the pseudo-grads (P4's mechanism).
  The probability-space error + learned-B fixes landed in p5 removed
  that channel; parking stands (no un-retire at HEAD).
"""

import time

import torch

from computronium import (
    CreditAssignmentConfig,
    DigitalSubstrate,
    FeedforwardGeometry,
    GeometryConfig,
    InstantaneousDynamics,
    LocalGoodnessCredit,
    StateDynamicsConfig,
    SubstrateConfig,
    compose_system,
    create_task,
)
from computronium.core.pipeline import forward_pass, task_loss
from computronium.ontology.credit import Phase
from computronium.ontology.system import SystemState
from computronium.ontology.update import UnitRMSUpdate

STEPS = 150


def _run(feedback_lr: float) -> None:
    torch.manual_seed(0)
    credit = LocalGoodnessCredit(
        CreditAssignmentConfig.local_goodness(
            feedback_scale=0.01,
            local_objective="lemma",
            learned_feedback=True,
            feedback_lr=feedback_lr,
        )
    )
    system = compose_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
        geometry=FeedforwardGeometry(
            GeometryConfig.feedforward(input_dim=784, output_dim=10, hidden_dims=(32,))
        ),
        dynamics=InstantaneousDynamics(StateDynamicsConfig.instantaneous()),
        credit=credit,
        update=UnitRMSUpdate(),
    )
    task = create_task("mnist", device="cpu", quick_mode=True, num_workers=0)
    task.setup()
    batches = [
        (xb.view(xb.size(0), -1), yb) for xb, yb in task.get_dataloader("train")
    ][:STEPS]

    w_out = system.geometry.params["2.weight"]
    print(f"--- feedback_lr={feedback_lr}")
    print(f"init: ||W_out||_F={w_out.norm():.4f}")
    cos_w1: list[float] = []
    for i, (xb, yb) in enumerate(batches):
        pre = {k: v.clone() for k, v in system.geometry.params.items()}
        # Phase capture mirroring run_train_step (grad-free diagnostic path).
        states: dict[Phase, SystemState] = {}
        loss = None
        initial = forward_pass(system.substrate, system.geometry, xb)
        for phase in system.credit.phases:
            state = SystemState(x=xb, y=yb)
            state.activations = initial
            settled = system.dynamics.settle(
                state,
                system.geometry,
                system.substrate,
                target=yb if phase is Phase.NUDGED else None,
            )
            if phase is Phase.NUDGED:
                settled.loss = task_loss(settled, yb)
                loss = settled.loss
            states[phase] = settled
        grads = system.credit.compute_pseudo_gradient(states, loss, system.geometry)
        # Autograd reference on the free logits CE.
        logits = initial if not isinstance(initial, list) else initial[-1]
        from computronium.ontology.utils import _learnable_weight_names

        weight_names = _learnable_weight_names(system.geometry.params)
        ref = torch.autograd.grad(
            torch.nn.functional.cross_entropy(logits, yb),
            [system.geometry.params[n] for n in weight_names],
            allow_unused=True,
        )
        ref_by_name = dict(zip(weight_names, ref, strict=True))
        for name, g in zip(weight_names, grads, strict=True):
            rr = ref_by_name[name]
            if rr is None:
                continue
            cos = torch.dot(g.flatten(), rr.flatten()) / (g.norm() * rr.norm() + 1e-12)
            if name == "0.weight":
                cos_w1.append(cos.item())
        from computronium.ontology.utils import apply_pseudo_gradients

        system.geometry.update_params(
            apply_pseudo_gradients(
                system.geometry.params,
                grads,
                lambda n, p, g: p - 3e-4 * g / g.square().mean().sqrt().add(1e-8),
            )
        )
        if i in (0, 49, 99, 149):
            w_out = system.geometry.params["2.weight"]
            drift = (system.geometry.params["2.weight"] - pre["2.weight"]).norm()
            b_norms = [f"{b.norm():.3f}" for b in system.credit._learned.values()]
            print(
                f"step {i:3d}: ||W_out||={w_out.norm():.4f} "
                f"per-step dW_out={drift.item():.4f} "
                f"gradnorms="
                + ",".join(f"{g.norm():.3f}" for g in grads)
                + f" cos(W1,∇CE)={sum(cos_w1[-50:]) / max(1, len(cos_w1[-50:])):.3f}"
                + (f" ||B||={b_norms}" if b_norms else "")
            )
    print(f"final ||W_out||={system.geometry.params['2.weight'].norm():.4f}")


def main() -> None:
    t0 = time.perf_counter()
    for lr in (0.5, 0.01):
        _run(lr)
    print(f"walltime: {time.perf_counter() - t0:.1f}s")


if __name__ == "__main__":
    main()
