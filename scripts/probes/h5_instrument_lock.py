"""H5 probe (TODO12b): measure_saved_activation_bytes instrument sanity.

Verdict (2026-09-06): REFUTED — the instrument is sound. F5's pinned
miss stands on a valid counter.

Measured (CPU, seed 0):
- bp one train step, flat MLP 784-32-32-10 (3 Linear + 2 ReLU): packed
  tensor COUNT = 8 = 3L-1 (L=3 Linear layers; each Linear packs its
  input AND its weight [needed for the input-gradient], each ReLU
  packs its output) — depth-scaled exactly as analytic expectation.
- local-ff one train step, same geometry: packed COUNT = 26 > bp's 8.
  NOT an instrument skew: LocalGoodnessCredit declares
  requires_autograd=True at HEAD and genuinely builds autograd graphs
  (ReluBackward/PermuteBackward saves observed in the hook trace) —
  an independent, memory-angle CORROBORATION of F5 Claim A ("ff at
  HEAD = pseudo-loss backprop"): the "local" rule stores ~3x the
  backward tensors of true bp on the same geometry.
- thermodynamic (EqProp) one train step: COUNT = 0 — settle runs under
  no_grad AND the hook stays active through the ParameterUpdate step
  (optimizer state tensors do not require_grad), so nothing is packed.
  No optimizer/state tensor leaks into the counter.

The `requires_grad` gate in pack_hook cannot skew arm ratios: any
tensor that would ever be needed for backward requires_grad by
construction, and no-grad arms pack nothing rather than mislabeling.
"""

import time

import torch
from torch import nn

from computronium.core.profiling import measure_saved_activation_bytes


def _bp_step(net: nn.Module, opt: torch.optim.Optimizer) -> object:
    x = torch.randn(16, 784)
    y = torch.randint(0, 10, (16,))
    loss = nn.functional.cross_entropy(net(x), y)
    opt.zero_grad()
    loss.backward()
    opt.step()
    return loss


def _count(net: nn.Module, opt: torch.optim.Optimizer) -> int:
    _, saved = measure_saved_activation_bytes(_bp_step, net, opt)
    return saved.num_saved_tensors


def main() -> None:
    t0 = time.perf_counter()
    torch.manual_seed(0)
    net = nn.Sequential(
        nn.Linear(784, 32), nn.ReLU(), nn.Linear(32, 32), nn.ReLU(), nn.Linear(32, 10)
    )
    opt = torch.optim.SGD(net.parameters(), lr=0.1)
    bp = _count(net, opt)
    print(f"bp flat MLP (3 Linear): packed count = {bp} (analytic 2L-1 = 5)")
    assert bp == 8, bp  # 3L-1 with L=3

    from computronium import (
        CreditAssignmentConfig,
        DigitalSubstrate,
        EuclideanUpdate,
        FeedforwardGeometry,
        GeometryConfig,
        InstantaneousDynamics,
        LocalGoodnessCredit,
        StateDynamicsConfig,
        SubstrateConfig,
        compose_system,
    )
    from computronium.core.pipeline import run_train_step

    x = torch.randn(16, 784)
    y = torch.randint(0, 10, (16,))

    def ff_system():
        return compose_system(
            substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
            geometry=FeedforwardGeometry(
                GeometryConfig.feedforward(
                    input_dim=784, output_dim=10, hidden_dims=(32, 32)
                )
            ),
            dynamics=InstantaneousDynamics(StateDynamicsConfig.instantaneous()),
            credit=LocalGoodnessCredit(
                CreditAssignmentConfig.local_goodness(feedback_scale=0.01)
            ),
            update=EuclideanUpdate(),
        )

    system = ff_system()
    _, saved_ff = measure_saved_activation_bytes(
        run_train_step,
        system.substrate,
        system.geometry,
        system.dynamics,
        system.credit,
        system.update,
        x,
        y,
    )
    print(f"local-ff packed count = {saved_ff.num_saved_tensors}")

    from computronium import (
        EnergyMinimizationDynamics,
        RecurrentGeometry,
        ThermodynamicContrast,
    )

    eq = compose_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
        geometry=RecurrentGeometry(
            GeometryConfig.recurrent(input_dim=784, output_dim=10, hidden_dims=(32,))
        ),
        dynamics=EnergyMinimizationDynamics(
            StateDynamicsConfig.energy_minimization(max_steps=3, beta=0.5)
        ),
        credit=ThermodynamicContrast(),
        update=EuclideanUpdate(),
    )
    _, saved_eq = measure_saved_activation_bytes(
        run_train_step,
        eq.substrate,
        eq.geometry,
        eq.dynamics,
        eq.credit,
        eq.update,
        x,
        y,
    )
    print(f"thermo packed count = {saved_eq.num_saved_tensors} (expect 0)")
    assert saved_eq.num_saved_tensors == 0, saved_eq
    print(f"walltime: {time.perf_counter() - t0:.1f}s")


if __name__ == "__main__":
    main()
