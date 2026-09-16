"""``SystemTrainerConfig.limit_train_batches``: the shorter-cells lever
(TODO29 session 3) — an epoch stops after N batches instead of the full
dataset, trading per-cell fidelity for L0 coverage throughput."""

import torch

from computronium.core.system_trainer import (
    SystemTrainer,
    SystemTrainerConfig,
    compose_system,
)
from computronium.ontology import (
    DigitalSubstrate,
    EnergyMinimizationDynamics,
    EuclideanUpdate,
    GeometryConfig,
    ParameterUpdateConfig,
    StateDynamicsConfig,
    TargetInversionCredit,
    TileGeometry,
)

_INPUT_DIM = 8
_OUTPUT_DIM = 2
_BATCHES = 10


class _BatchProvider:
    def __init__(self) -> None:
        g = torch.Generator().manual_seed(0)
        self.x = torch.randn(_BATCHES, _INPUT_DIM, generator=g)
        self.y = torch.randint(0, _OUTPUT_DIM, (_BATCHES,), generator=g)

    def __iter__(self):
        for i in range(_BATCHES):
            yield self.x[i : i + 1], self.y[i : i + 1]

    def __len__(self) -> int:
        return _BATCHES


def _trainer(limit: int | None) -> SystemTrainer:
    geometry = TileGeometry(
        GeometryConfig(
            input_dim=_INPUT_DIM,
            output_dim=_OUTPUT_DIM,
            num_layers=2,
            topology_type="tile_mesh",
            hidden_dims=(),
            connectivity=None,
            recurrent_weight=None,
        ),
        neurons_per_tile=4,
        tiles_per_layer=2,
    )
    system = compose_system(
        DigitalSubstrate(),
        geometry,
        EnergyMinimizationDynamics(
            StateDynamicsConfig.energy_minimization(max_steps=2)
        ),
        TargetInversionCredit(),
        EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=0.01)),
    )
    return SystemTrainer(
        system,
        SystemTrainerConfig(
            max_epochs=1,
            batch_size=1,
            device="cpu",
            track_energy=False,
            track_flops=False,
            track_memory=False,
            limit_train_batches=limit,
        ),
        _BatchProvider(),
        _BatchProvider(),
    )


def test_limit_train_batches_caps_the_epoch() -> None:
    with _trainer(3) as trainer:
        trainer.fit()
        assert trainer.global_step == 3


def test_no_limit_runs_every_batch() -> None:
    with _trainer(None) as trainer:
        trainer.fit()
        assert trainer.global_step == _BATCHES
