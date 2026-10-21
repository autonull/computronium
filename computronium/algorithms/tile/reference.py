"""Reference implementation for TileNet algorithm.

Composes Tile training step with TileGeometry.
"""

from typing import Any

from computronium.harness import (
    make_reference_system,
    reference_config,
    run_reference_step,
)
from computronium.ontology.credit import BackpropCredit, CreditAssignmentConfig
from computronium.ontology.geometry import GeometryConfig, TileGeometry


def build_system(case: Any) -> Any:
    """Create the system the reference step runs on."""
    config = reference_config(case)
    neurons_per_tile = case.config.get("neurons_per_tile", 8)
    tiles_per_layer = case.config.get("tiles_per_layer", 2)
    geometry = TileGeometry(
        GeometryConfig(
            input_dim=config.input_dim,
            output_dim=config.output_dim,
            hidden_dims=config.hidden_dims,
            num_layers=len(config.hidden_dims) + 1,
            topology_type="tile_mesh",
            connectivity=None,
            recurrent_weight=None,
            init_scale=0.1,
            neurons_per_tile=neurons_per_tile,
            tiles_per_layer=tiles_per_layer,
        ),
        neurons_per_tile=neurons_per_tile,
        tiles_per_layer=tiles_per_layer,
    )
    return make_reference_system(
        config,
        BackpropCredit(CreditAssignmentConfig.gradient()),
        geometry=geometry,
    )


def step(case: Any) -> Any:
    """Execute one reference training step using the opaque case object."""
    return run_reference_step(case, build=build_system)
