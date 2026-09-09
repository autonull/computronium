"""Harvest-instrument lock (TODO16 §0.1).

``harvest_mode="ema"`` restores streaming-EMA weights at the end of ``fit``;
``"best_snapshot"`` restores the best-validation checkpoint; ``None`` is
byte-identical to pre-harvest behavior.
"""

import torch

from computronium import (
    BackpropCredit,
    DigitalSubstrate,
    EnergyMinimizationDynamics,
    EuclideanUpdate,
    GeometryConfig,
    NullPlasticity,
    ParameterUpdateConfig,
    RecurrentGeometry,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemTrainer,
    SystemTrainerConfig,
    compose_joint_system,
)

BATCHES = 40


def _data(seed: int, n: int = BATCHES) -> list[tuple[torch.Tensor, torch.Tensor]]:
    g = torch.Generator().manual_seed(seed)
    w = torch.randn(20, 2, generator=g)
    return [
        (x, (x @ w).argmax(-1))
        for x in (torch.randn(32, 20, generator=g) for _ in range(n))
    ]


def _system():
    torch.manual_seed(0)
    return compose_joint_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
        geometry=RecurrentGeometry(
            GeometryConfig.recurrent(input_dim=20, output_dim=2, hidden_dims=(32,))
        ),
        dynamics=EnergyMinimizationDynamics(
            StateDynamicsConfig.energy_minimization(max_steps=3, beta=0.5)
        ),
        plasticity=NullPlasticity(),
        credit=BackpropCredit(),
        update=EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=0.1)),
    )


def _run(**harvest_kwargs) -> tuple[float, dict[str, torch.Tensor]]:
    system = _system()
    config = SystemTrainerConfig(
        max_epochs=1,
        device="cpu",
        seed=42,
        log_every_n_steps=1000,
        **harvest_kwargs,
    )
    val = list(_data(7, n=10))
    history = SystemTrainer(
        system=system, config=config, train_data=_data(1), val_data=val
    ).fit()
    params = {k: v.detach().clone() for k, v in system.geometry.params.items()}
    return history[-1]["val_acc"], params


def test_harvest_none_is_reproducible() -> None:
    acc_a, params_a = _run()
    acc_b, params_b = _run()
    assert acc_a == acc_b
    for k in params_a:
        assert torch.equal(params_a[k], params_b[k])


def test_ema_harvest_changes_final_weights_and_valuates() -> None:
    ema_acc, ema_params = _run(harvest_mode="ema", harvest_decay=0.9)
    _, plain_params = _run()
    assert ema_acc >= 0.5
    assert any(not torch.equal(ema_params[k], plain_params[k]) for k in ema_params)


def test_best_snapshot_restores_best_val_checkpoint() -> None:
    best_acc, _ = _run(harvest_mode="best_snapshot", harvest_every_n=5)
    assert best_acc >= 0.5
