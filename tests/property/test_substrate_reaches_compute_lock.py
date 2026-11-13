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


def test_the_row_refuses_a_non_digital_ntm_coordinate_only() -> None:
    # NCA routes its cell MLP and readout through the substrate (B10), so the
    # old NCA refusal is gone; NTM keeps its named row.
    assert _refused("ternary", "nca") is None
    assert _refused("analog", "ntm") == "ntm_substrate_inert"
    assert _refused("digital", "ntm") is None
    assert _refused("ternary", "conv") is None


def test_a_substrate_coupled_geometry_reads_the_substrate() -> None:
    torch.manual_seed(0)
    config = GeometryConfig.feedforward(input_dim=8, output_dim=4, hidden_dims=(16,))
    geometry = FeedforwardGeometry(config)
    digital, ternary = _forward(geometry, torch.randn(3, 8))
    assert not torch.allclose(digital, ternary)


def test_complex_substrate_is_real_arithmetic_and_the_row_names_it() -> None:
    # ``(a+bi)(c+di)`` with real weights is ``ac``: the complex operator is the
    # digital matmul. The row declines those cells; if the operator ever gains
    # a real-valued phase/noise term, this test and the row flip together.
    assert _refused("complex", "feedforward") == "complex_substrate_real_compute"
    assert _refused("complex", "nca") == "complex_substrate_real_compute"
    assert _refused("digital", "feedforward") is None

    torch.manual_seed(0)
    config = GeometryConfig.feedforward(input_dim=8, output_dim=4, hidden_dims=(16,))
    geometry = FeedforwardGeometry(config)
    digital = substrate_from_config(SubstrateConfig.digital())
    complex_substrate = substrate_from_config(SubstrateConfig.complex())
    x = torch.randn(3, 8)
    with torch.no_grad():
        torch.manual_seed(0)
        first = geometry.forward(x, digital)
        torch.manual_seed(0)
        second = geometry.forward(x, complex_substrate)
    assert torch.equal(first, second)


def test_nca_reads_the_substrate_and_ntm_still_does_not() -> None:
    # NCA wired: the substrate changes the state delta. If this fails, the
    # NCA half of the pair verdict must return as a declared row.
    torch.manual_seed(0)
    nca = NcaGeometry(
        GeometryConfig.nca(channels=1, hidden=8, grid_hw=(4, 4), output_dim=10)
    )
    digital, ternary = _forward(nca, torch.randn(2, 16))
    assert not torch.equal(digital, ternary)

    # NTM's stock LSTM controller has no single-operator form, so it keeps the
    # declared row. If this starts differing, delete `ntm_substrate_inert`.
    torch.manual_seed(0)
    ntm = NtmGeometry(
        GeometryConfig.ntm(input_dim=4, output_dim=10, hidden=8, mem_slots=4)
    )
    digital, ternary = _forward(ntm, torch.randn(2, 4))
    assert torch.equal(digital, ternary)
