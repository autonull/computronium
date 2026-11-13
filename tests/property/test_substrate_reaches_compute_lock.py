"""Lock: a substrate that never reaches the computation cannot be breadth.

The substrate axis is measured by composing a non-digital substrate with a
geometry and reading the cell. ``NcaGeometry`` and ``NtmGeometry`` call no
substrate operator, so off ``digital`` they run the digital arithmetic and
differ only in the energy model — the store still holds a PASS cell, but the
cell measured nothing about the substrate. TODO90 B5 found this by identical
``train_loss`` to six decimals across substrates.

The declared row ``nca_ntm_substrate_inert`` carries that verdict. This lock
fails if the row disappears, or if a geometry starts calling the substrate
without the row being deleted (a stale row voids a measurable coordinate).
"""

from __future__ import annotations

import pytest
import torch

from computronium.experiment.legality.dsl import CoordinateContext, evaluate
from computronium.experiment.legality.engine import void_rules
from computronium.experiment.schema.coordinate import Coordinate
from computronium.experiment.schema.seed_registries import seed_all_registries
from computronium.ontology.geometry import (
    FeedforwardGeometry,
    GeometryConfig,
    NcaGeometry,
    NtmGeometry,
)
from computronium.ontology.substrate import SubstrateConfig, substrate_from_config

pytestmark = pytest.mark.timeout(120)


def _substrates() -> tuple[object, object]:
    return (
        substrate_from_config(SubstrateConfig.digital()),
        substrate_from_config(SubstrateConfig.ternary()),
    )


def _refused(substrate: str, geometry: str) -> str | None:
    seed_all_registries()
    selection = {
        "substrate": substrate,
        "geometry": geometry,
        "dynamics": "instantaneous",
        "plasticity": "null",
        "credit": "gradient",
        "update": "adam",
    }
    ctx = CoordinateContext(Coordinate(**selection, params={}), task="digits")
    for rule in void_rules():
        if not evaluate(rule.predicate, ctx):
            return rule.name
    return None


def _forward(
    geometry: torch.nn.Module, x: torch.Tensor
) -> tuple[torch.Tensor, torch.Tensor]:
    """Forward on digital and on ternary, from the same RNG and buffer state.

    The geometries sample update masks and carry controller buffers, so each
    call reseeds and resets: a difference must come from the substrate, never
    from the draw or from the previous call's state.
    """
    digital, ternary = _substrates()
    reset = getattr(geometry, "_reset_buffers", None)
    with torch.no_grad():
        if reset is not None:
            reset()
        torch.manual_seed(0)
        first = geometry.forward(x, digital)
        if reset is not None:
            reset()
        torch.manual_seed(0)
        return first, geometry.forward(x, ternary)


def test_the_row_refuses_a_non_digital_nca_or_ntm_coordinate() -> None:
    assert _refused("ternary", "nca") == "nca_ntm_substrate_inert"
    assert _refused("analog", "ntm") == "nca_ntm_substrate_inert"
    assert _refused("digital", "nca") is None
    assert _refused("ternary", "conv") is None


def test_a_substrate_coupled_geometry_reads_the_substrate() -> None:
    torch.manual_seed(0)
    config = GeometryConfig.feedforward(input_dim=8, output_dim=4, hidden_dims=(16,))
    geometry = FeedforwardGeometry(config)
    digital, ternary = _forward(geometry, torch.randn(3, 8))
    assert not torch.allclose(digital, ternary)


def test_nca_and_ntm_run_the_digital_arithmetic_on_every_substrate() -> None:
    # If either geometry starts calling the substrate operator, this fails and
    # the `nca_ntm_substrate_inert` row must be deleted in the same change.
    torch.manual_seed(0)
    nca = NcaGeometry(
        GeometryConfig.nca(channels=1, hidden=8, grid_hw=(4, 4), output_dim=10)
    )
    digital, ternary = _forward(nca, torch.randn(2, 16))
    assert torch.equal(digital, ternary)

    torch.manual_seed(0)
    ntm = NtmGeometry(
        GeometryConfig.ntm(input_dim=4, output_dim=10, hidden=8, mem_slots=4)
    )
    digital, ternary = _forward(ntm, torch.randn(2, 4))
    assert torch.equal(digital, ternary)
