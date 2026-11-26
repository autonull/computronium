"""Lock: a declared-legal settling cell can reach the settle kernel.

Every settling dynamic raises ``TypeError: ... requires a layered geometry``
when ``extract_layered_params`` returns ``None`` (TODO94 R2). Every geometry
``SystemConfig.validate`` admits for a settling dynamic must therefore be seen
as layered by the kernel. The pair *is* the declaration: the geometry table
(``NONLAYERED_GEOMETRIES``) and the kernel must agree.

The test fails when a geometry is added to the space without a layer stack the
settle kernel can iterate (or is added to the wrong side of the table).
"""

from __future__ import annotations

import pytest

from computronium.experiment.schema.seed_registries import seed_all_registries
from computronium.ontology._settle_kernel import extract_layered_params
from computronium.ontology.credit import CreditAssignmentConfig
from computronium.ontology.dynamics import StateDynamicsConfig
from computronium.ontology.geometry import GeometryConfig, geometry_from_config
from computronium.ontology.substrate import SubstrateConfig
from computronium.ontology.system import SETTLING_DYNAMICS, SystemConfig
from computronium.ontology.update import ParameterUpdateConfig
from computronium.state import PlasticityConfig

_GEOMETRIES = {
    "feedforward": lambda: GeometryConfig.feedforward(
        input_dim=16, output_dim=4, hidden_dims=(8,)
    ),
    "recurrent": lambda: GeometryConfig.recurrent(
        input_dim=16, output_dim=4, hidden_dims=(8,)
    ),
    "conv": lambda: GeometryConfig.conv(
        input_dim=64,
        output_dim=4,
        conv_channels=(8,),
        in_channels=1,
        input_hw=(8, 8),
        pool_hw=(2, 2),
    ),
    "attention": lambda: GeometryConfig.attention(
        input_dim=16, output_dim=4, hidden_dim=8, num_layers=1, num_heads=2
    ),
    "tile": lambda: GeometryConfig.tile(input_dim=16, output_dim=4, num_layers=2),
    "tile_mesh": lambda: GeometryConfig.tile_mesh(
        input_dim=16, output_dim=4, num_layers=2
    ),
    "spatial_lattice": lambda: GeometryConfig.spatial_lattice(
        input_dim=16, output_dim=4
    ),
    "nca": lambda: GeometryConfig.nca(
        channels=1, hidden=8, grid_hw=(4, 4), output_dim=4
    ),
    "ntm": lambda: GeometryConfig.ntm(input_dim=16, output_dim=4),
    "graph": lambda: GeometryConfig.graph(
        input_dim=16, output_dim=4, edge_index=[[0, 1], [1, 0]]
    ),
    "routing": lambda: GeometryConfig.routing(
        input_dim=16, output_dim=4, hidden_dims=(8,)
    ),
}

_CREDITS = (
    "homeostatic",
    "thermodynamic_contrast",
    "local_goodness",
    "target_inversion",
    "pc_alm",
    "temporal_trace",
)


def _system(geometry: GeometryConfig, dynamics: str, credit: str) -> SystemConfig:
    return SystemConfig(
        substrate=SubstrateConfig.digital(),
        geometry=geometry,
        dynamics=getattr(StateDynamicsConfig, dynamics)(),
        plasticity=PlasticityConfig.null(),
        credit=getattr(CreditAssignmentConfig, credit)(),
        update=ParameterUpdateConfig.euclidean(),
    )


def test_every_admitted_settling_cell_reaches_the_settle_kernel() -> None:
    seed_all_registries()
    admitted = 0
    for geometry_name, make in _GEOMETRIES.items():
        geometry = make()
        for dynamics in sorted(SETTLING_DYNAMICS):
            for credit in _CREDITS:
                try:
                    _system(geometry, dynamics, credit).validate()
                except ValueError, UserWarning:
                    continue
                admitted += 1
                builder = geometry_from_config(make())
                assert extract_layered_params(builder) is not None, (
                    f"validate() admits geometry={geometry_name!r} "
                    f"dynamics={dynamics!r} credit={credit!r}, but the settle "
                    "kernel sees no layer stack and raises"
                )
    assert admitted >= 6, "the sweep admitted too few cells to mean anything"


@pytest.mark.parametrize("dynamics", ["energy_minimization", "pc_alm"])
def test_a_non_layered_geometry_is_refused_by_name(dynamics: str) -> None:
    """The refusal direction: a geometry the kernel cannot layer is declared."""
    seed_all_registries()
    attention = _GEOMETRIES["attention"]()
    credit = "thermodynamic_contrast" if dynamics == "energy_minimization" else "pc_alm"
    with pytest.raises(ValueError, match="cannot host settling dynamics"):
        _system(attention, dynamics, credit).validate()
