"""D23 — PC-ALM: Augmented Lagrangian Predictive Coding.

Demonstrates PC-ALM (Seely & Gould 2026, arXiv:2605.31022) training on MNIST.
PC-ALM replaces global backprop with layer-local primal–dual dynamics:

    c_l = h_l - f_θ_l(h_{l-1})                  # constraint violation
    λ_l ← λ_l + step_size * c_l                  # dual update (PI controller)
    h_l ← h_l - step_size * (c_l + λ_l + ρ*c_l - J_{l+1}^T * (c_{l+1} + λ_{l+1} + ρ*c_{l+1}))

Weight update (local Hebbian): ΔW_l ∝ -λ_l @ h_{l-1}^T

Demonstrated regime (re-pinned 2026-09-25): MNIST quick-mode, 1 epoch over capped
stream, hidden (128, 128), PCALMDynamics(max_steps=60, step_size=0.2, rho=1.0,
prospective_leak=0.0, beta=0.5, compiled=True), PCALMCredit(beta=0.5),
EuclideanUpdate(step_size=0.02) -> accuracy ≈ 49% (chance 0.1).

The stream cap was halved (600 -> 300 batches) on 2026-09-25: it runs 1.8x
faster *and* reaches higher train accuracy, because the settle loop now
actually relaxes (it used to stop after one step, which also made this
test marginal against the 120s timeout under ``pytest -n``). The 0.25
floor went from a 0.26-vs-0.25 sliver to a 0.49-vs-0.25 margin.
"""

from itertools import islice

import torch

from computronium import (
    CreditAssignmentConfig,
    DigitalSubstrate,
    EuclideanUpdate,
    FeedforwardGeometry,
    GeometryConfig,
    NullPlasticity,
    ParameterUpdateConfig,
    PCALMCredit,
    PCALMDynamics,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemTrainer,
    SystemTrainerConfig,
    compose_joint_system,
    create_task,
)
from computronium.visualization import bars_panel, figure_spec

BATCH_CAP = 300  # loader cap (Register C): suite walltime


def _flatten(loader, cap=BATCH_CAP):
    for x, y in islice(loader, cap):
        yield x.view(x.size(0), -1), y


def test_demo_pc_alm(emit_run_record) -> None:
    task = create_task("mnist", device="cpu", quick_mode=True)
    task.setup()
    train_loader = task.get_dataloader("train")
    config = SystemTrainerConfig(max_epochs=1, device="cpu", seed=42)

    torch.manual_seed(0)
    system = compose_joint_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
        geometry=FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=784, output_dim=10, hidden_dims=(128, 128)
            )
        ),
        dynamics=PCALMDynamics(
            StateDynamicsConfig.pc_alm(
                max_steps=60,
                step_size=0.2,
                rho=1.0,
                prospective_leak=0.0,
                beta=0.5,
                convergence_threshold=1e-4,
                convergence_start=5,
                compiled=True,
            )
        ),
        plasticity=NullPlasticity(),
        credit=PCALMCredit(CreditAssignmentConfig.pc_alm(beta=0.5)),
        update=EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=0.02)),
    )
    metrics = SystemTrainer(
        system=system, config=config, train_data=_flatten(train_loader)
    ).fit()[-1]

    train_acc = metrics["train_acc"]
    print(f"pc_alm: {train_acc:.1%}")
    assert train_acc > 0.25, f"PC-ALM must learn above 2.5x chance, got {train_acc:.1%}"

    record = {"arms": {"pc_alm": {"train_acc": train_acc}}}
    record["figure"] = figure_spec(
        "D23 — PC-ALM: Augmented Lagrangian Predictive Coding on MNIST",
        bars_panel(
            {"pc_alm": {"train_acc": train_acc}},
            chance=1 / 10,
            chance_label="chance (0.1)",
            ylabel="train accuracy",
            ylim=(0, 1),
        ),
        figsize=[6, 4],
    )

    emit_run_record("D23", "pc_alm", record)
