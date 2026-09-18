"""Reference implementation for TileNet algorithm.

Composes Tile training step with TileGeometry.
"""

from dataclasses import dataclass
from typing import Any

import torch

from computronium.core.system_trainer import compose_system
from computronium.ontology.credit import BackpropCredit, CreditAssignmentConfig
from computronium.ontology.dynamics import InstantaneousDynamics, StateDynamicsConfig
from computronium.ontology.geometry import GeometryConfig, TileGeometry
from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig
from computronium.ontology.update import EuclideanUpdate, ParameterUpdateConfig


@dataclass(frozen=True, slots=True)
class _SystemConfig:
    input_dim: int = 4
    output_dim: int = 4
    hidden_dims: tuple[int, ...] = ()
    lr: float = 1e-3
    neurons_per_tile: int = 8
    tiles_per_layer: int = 2
    device: str = "cpu"


def _make_tile_system(config: _SystemConfig) -> Any:
    """Create a Tile system for testing."""
    substrate = DigitalSubstrate(SubstrateConfig.digital(device=config.device))
    tile_cfg = GeometryConfig(
        input_dim=config.input_dim,
        output_dim=config.output_dim,
        hidden_dims=config.hidden_dims,
        num_layers=len(config.hidden_dims) + 1,
        topology_type="tile_mesh",
        connectivity=None,
        recurrent_weight=None,
        init_scale=0.1,
        neurons_per_tile=config.neurons_per_tile,
        tiles_per_layer=config.tiles_per_layer,
    )
    geometry = TileGeometry(
        tile_cfg,
        neurons_per_tile=config.neurons_per_tile,
        tiles_per_layer=config.tiles_per_layer,
    )
    dynamics = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
    credit = BackpropCredit(CreditAssignmentConfig.gradient())
    update = EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=config.lr))

    return compose_system(
        substrate=substrate,
        geometry=geometry,
        dynamics=dynamics,
        credit=credit,
        update=update,
    )


def step(case: Any) -> Any:
    """Execute one reference training step using the opaque case object."""
    rng_state = torch.get_rng_state()
    torch.manual_seed(case.config.get("seed", 0))
    try:
        system_config = _SystemConfig(
            input_dim=case.state.shape[1],
            output_dim=case.config.get("output_dim", case.state.shape[1]),
            lr=case.config.get("lr", 1e-3),
            neurons_per_tile=case.config.get("neurons_per_tile", 8),
            tiles_per_layer=case.config.get("tiles_per_layer", 2),
            device=case.state.device,
        )
        system = _make_tile_system(system_config)
        result = system.train_step(case.state, case.target)
    finally:
        torch.set_rng_state(rng_state)

    return result
