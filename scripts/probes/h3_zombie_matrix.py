"""H3 probe (TODO12b): credit × dynamics zero-term (zombie) matrix.

Verdict (2026-09-06): PARTIALLY CONFIRMED — one structural zombie
pattern, already characterized as F5 Claim A; no NEW zombie cell.

Per-weight-layer pseudo-gradient nonzero-ness after one phase capture
(2-layer feedforward 20-16-8, batch 4, seed 0, CPU; `z` = zero tensor):

credit × instantaneous:
    gradient:            [live, live]
    thermodynamic:       [z, live]     <- hidden layer exact zero:
        free hidden acts == nudged hidden acts under instantaneous
        settle (f5b structural fact; the nudge touches the output
        layer only). Hidden weights receive no signal; the credit
        degrades to output-pseudo-loss backprop. F5 Claim A stands.
    random_projections:  [live, live]  (per-layer error bus via fixed B)
    local_goodness:      [live, live]
    target_inversion:    [live, live]
    homeostatic:         [live, live]  (free-state norms only — never
        consumes nudged terms, immune to the f5b zeroing)
    temporal_trace:      [live, live]

credit × error_predictive_coding / energy_minimization:
    thermodynamic:       [live, live]  (settle propagates the nudge)
    homeostatic:         [live, live]
    (autograd/contrastive credits run under their declared contracts;
     ePC exposes only error-bus-compatible credits per the validate()
     whitelist)

Cross-check vs SystemConfig.validate(): the matrix agrees — no
combination in the whitelist produces an all-zero pseudo-gradient list,
i.e. no registered cell is fully dead. The thermodynamic×instantaneous
hidden-zero column is exactly the already-registered F5/Claim-A scope,
not a new discovery.
"""

import time

import torch
from torch import Tensor

from computronium import (
    CreditAssignmentConfig,
    DigitalSubstrate,
    EuclideanUpdate,
    FeedforwardGeometry,
    GeometryConfig,
    StateDynamicsConfig,
    SubstrateConfig,
    compose_system,
)
from computronium.core.pipeline import forward_pass, task_loss
from computronium.ontology.credit import (
    GradientCredit,
    HomeostaticCredit,
    LocalGoodnessCredit,
    Phase,
    RandomProjectionsCredit,
    TargetInversionCredit,
    TemporalTraceCredit,
    ThermodynamicContrast,
)


def _credit(name: str):
    if name == "gradient":
        return GradientCredit()
    if name == "thermodynamic":
        return ThermodynamicContrast()
    if name == "random_projections":
        return RandomProjectionsCredit()
    if name == "local_goodness":
        return LocalGoodnessCredit(
            CreditAssignmentConfig.local_goodness(feedback_scale=0.01)
        )
    if name == "target_inversion":
        return TargetInversionCredit()
    if name == "homeostatic":
        return HomeostaticCredit()
    return TemporalTraceCredit()


def main() -> None:
    t0 = time.perf_counter()
    torch.manual_seed(0)
    names = (
        "gradient",
        "thermodynamic",
        "random_projections",
        "local_goodness",
        "target_inversion",
        "homeostatic",
        "temporal_trace",
    )
    x = torch.randn(4, 20)
    y = torch.randint(0, 8, (4,))
    for dyn_name, dyn_cfg in (
        ("instantaneous", StateDynamicsConfig.instantaneous()),
        ("epc", StateDynamicsConfig.error_predictive_coding(max_steps=5)),
        ("energy_minimization", StateDynamicsConfig.energy_minimization(max_steps=3)),
    ):
        for name in names:
            try:
                from computronium import (
                    EnergyMinimizationDynamics,
                    InstantaneousDynamics,
                )

                dynamics = {
                    "instantaneous": lambda: InstantaneousDynamics(dyn_cfg),
                    "epc": lambda: _epc(dyn_cfg),
                    "energy_minimization": lambda: EnergyMinimizationDynamics(dyn_cfg),
                }[dyn_name]()
                system = compose_system(
                    substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
                    geometry=FeedforwardGeometry(
                        GeometryConfig.feedforward(
                            input_dim=20, output_dim=8, hidden_dims=(16,)
                        )
                    ),
                    dynamics=dynamics,
                    credit=_credit(name),  # type: ignore[arg-type]
                    update=EuclideanUpdate(),
                )
                grads = _pseudo_grads(system, x, y)
                print(f"{name:18s} × {dyn_name:22s} {_pattern(grads)}")
            except Exception as exc:
                print(f"{name:18s} × {dyn_name:22s} ERROR: {type(exc).__name__}: {exc}")
    print(f"walltime: {time.perf_counter() - t0:.1f}s")


def _epc(cfg):
    from computronium import ErrorPredictiveCodingDynamics

    return ErrorPredictiveCodingDynamics(cfg)


def _pseudo_grads(system, x: Tensor, y: Tensor) -> list[Tensor]:
    from computronium.ontology.system import SystemState

    states: dict[Phase, SystemState] = {}
    loss: Tensor | None = None
    initial = forward_pass(system.substrate, system.geometry, x)
    for phase in system.credit.phases:
        state = SystemState(x=x, y=y)
        state.activations = initial
        settled = system.dynamics.settle(
            state,
            system.geometry,
            system.substrate,
            target=y if phase is Phase.NUDGED else None,
        )
        if phase is Phase.NUDGED:
            settled.loss = task_loss(settled, y)
            loss = settled.loss
        states[phase] = settled
    return system.credit.compute_pseudo_gradient(states, loss, system.geometry)


def _pattern(vals: list[Tensor]) -> str:
    cells = ", ".join("ZERO" if g.abs().max().item() == 0 else "live" for g in vals)
    return f"[{cells}]"


if __name__ == "__main__":
    main()
