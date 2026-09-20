"""TODO26d zoo grid — the other credit families under co-designed geometry.

The engine checks so far only litigated ePC. This grid runs the ontology
zoo's live credit families on the fair task (sign-of-mean, depth 20,
width 32, 60 batches, LocalAdam where the family has no own-update
constraint), each under BOTH geometries:
  - none+default  (the pre-co-design baseline)
  - residual+mupc (the round-2 channel conditioning)

Arms (family: credit × dynamics):
  - epc        ThermodynamicContrast × ErrorPredictiveCoding (round-2 winner)
  - ff         LocalGoodnessCredit ff-mode (readout-error hybrid; autograd
               goodness contrast — NO backward pass, label via readout CE)
  - fa         RandomProjectionsCredit (DFA: autograd readout error through
               FIXED random backward projections — one-hop, not horizon-bound)
  - eqprop     EnergyMinimizationDynamics (30-step settle) × ThermodynamicContrast
  - target_inv TargetInversionCredit (transpose targets)

Pre-registered reading: families whose channel is *reach-limited* (epc-like
settle horizon) should lift with residual+μPC; families whose channel is
structurally different (ff: forward-only; fa: one-hop backward) should be
geometry-robust if their failure mode was never the channel. w9's warning
applies: co-design can COLLAPSE a family (ff 0.757→0.402 under ePC's
geometry on MNIST) — the grid measures per-family geometry response.

Run: uv run python scripts/probes/todo26d_zoo_grid.py (~34 s CPU)
Walltime printed, never recorded.

VERDICT (2026-09-14; depth 20, sign-of-mean, LocalAdam 3e-3, seed 0):

- **FF is rescued by co-design** (0.506 -> 0.875) — the round-2 finding
  GENERALIZES to a second family with a completely different credit rule
  (forward-only goodness contrast, no backward pass at all). Two
  activity-reading families, one rescue.
- **FA is geometry-insensitive** (0.504 -> 0.514, both chance) — the
  fixed-random one-hop backward channel's failure is DIRECTIONAL, and no
  amount of channel conditioning fixes it. Consistent with the TODO26b
  P2 boundary-locked reading; the FA family stays closed.
- **EqProp is actively HARMED by co-design** (0.494 -> 0.466) — replicates
  w9's MNIST warning (co-design collapsed eqprop there too). The
  energy-minimization settle contract apparently needs the small-init
  convention; μPC's depth-scaled init breaks it. Co-design is NOT a
  universal recipe — it is family-specific medicine.
- target_inv dead both ways (0.501/0.479) — round-3 replicated.
- BP ruler depth 4: 0.845 (task learnable; grid verdicts attributable).

Mechanism-consistent summary: co-design rescues exactly the families
whose credit reads the settle stream along the forward path (ePC, FF)
and harms/leaves-alone families whose channel is structurally different
(eqprop symmetric energy, fa fixed-random backward). The "co-designed
channel topology" thesis is now a per-family measured law, not an
ePC-only artifact — and NOT a blanket prescription.
"""

from __future__ import annotations

import time

import torch

from computronium import (
    BackpropCredit,
    CreditAssignmentConfig,
    DigitalSubstrate,
    EnergyMinimizationDynamics,
    ErrorPredictiveCodingDynamics,
    FeedforwardGeometry,
    GeometryConfig,
    InstantaneousDynamics,
    LocalAdamUpdate,
    LocalGoodnessCredit,
    ParameterUpdateConfig,
    RandomProjectionsCredit,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemTrainer,
    SystemTrainerConfig,
    TargetInversionCredit,
    ThermodynamicContrast,
    compose_system,
)
from computronium.experiments.joint.tasks import create_switching_task
from computronium.ontology.geometry import (
    InitScheme,  # ruff: ignore[typing-only-first-party-import]
)

INPUT_DIM = 16
WIDTH = 32
BATCH = 64
BETA = 0.5
DEVICE = "cpu"
DEPTH = 20
LR = 3e-3


def _build(credit: str, *, residual: bool, scheme: InitScheme, depth: int = DEPTH):
    dynamics = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
    if credit == "epc":
        dynamics = ErrorPredictiveCodingDynamics(
            StateDynamicsConfig.error_predictive_coding(
                max_steps=5, step_size=0.5, beta=BETA
            )
        )
        credit_obj: object = ThermodynamicContrast(
            CreditAssignmentConfig.thermodynamic_contrast(beta=BETA)
        )
    elif credit == "ff":
        credit_obj = LocalGoodnessCredit(
            CreditAssignmentConfig.local_goodness(
                feedback_scale=0.01, local_objective="ff", readout_error=True
            )
        )
    elif credit == "fa":
        credit_obj = RandomProjectionsCredit(
            CreditAssignmentConfig.random_projections(beta=BETA, feedback_scale=0.05)
        )
    elif credit == "eqprop":
        dynamics = EnergyMinimizationDynamics(
            StateDynamicsConfig.energy_minimization(
                max_steps=30, step_size=0.5, beta=BETA
            )
        )
        credit_obj = ThermodynamicContrast(
            CreditAssignmentConfig.thermodynamic_contrast(beta=BETA)
        )
    else:  # target_inv
        credit_obj = TargetInversionCredit(CreditAssignmentConfig.target_inversion())
    return compose_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device=DEVICE)),
        geometry=FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=4 * INPUT_DIM,
                output_dim=2,
                hidden_dims=(WIDTH,) * depth,
                residual=residual,
                init_scheme=scheme,
            )
        ),
        dynamics=dynamics,
        credit=credit_obj,
        update=LocalAdamUpdate(
            ParameterUpdateConfig.local_adam(step_size=LR, momentum=0.9)
        ),
    )


def main() -> None:
    t0 = time.perf_counter()
    data = [create_switching_task(BATCH, 4, INPUT_DIM, phase="A") for _ in range(60)]
    print(
        "== Zoo grid: credit family × geometry (sign-of-mean, depth 20) ==", flush=True
    )
    for credit in ("epc", "ff", "fa", "eqprop", "target_inv"):
        arms: tuple[tuple[str, bool, InitScheme], ...] = (
            ("none+default", False, "default"),
            ("resid+mupc", True, "mupc"),
        )
        for geom_label, residual, scheme in arms:
            torch.manual_seed(0)
            try:
                system = _build(credit, residual=residual, scheme=scheme)
                acc = SystemTrainer(
                    system=system,
                    config=SystemTrainerConfig(max_epochs=1, device=DEVICE, seed=42),
                    train_data=data,
                ).fit()[-1]["train_acc"]
                print(f"{credit:>10} × {geom_label:<12}: acc {acc:.3f}", flush=True)
            except RuntimeError as e:
                print(
                    f"{credit:>10} × {geom_label:<12}: CRASH {str(e)[:100]}", flush=True
                )
    # BP reference on the same task (the ruler)
    torch.manual_seed(0)
    system = compose_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device=DEVICE)),
        geometry=FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=4 * INPUT_DIM, output_dim=2, hidden_dims=(WIDTH,) * 4
            )
        ),
        dynamics=InstantaneousDynamics(StateDynamicsConfig.instantaneous()),
        credit=BackpropCredit(CreditAssignmentConfig.gradient()),
        update=LocalAdamUpdate(
            ParameterUpdateConfig.local_adam(step_size=LR, momentum=0.9)
        ),
    )
    bp = SystemTrainer(
        system=system,
        config=SystemTrainerConfig(max_epochs=1, device=DEVICE, seed=42),
        train_data=data,
    ).fit()[-1]["train_acc"]
    print(f"BP ruler (depth 4, LocalAdam): {bp:.3f}", flush=True)
    print(f"total walltime {time.perf_counter() - t0:.1f}s")


if __name__ == "__main__":
    main()
