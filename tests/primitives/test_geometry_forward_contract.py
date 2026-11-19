"""Geometry forward contract (TODO91 S2).

One parameterized contract covers every runtime geometry coordinate: build the
geometry from its ``GeometryConfig``, forward a batch through a digital
substrate, take one ``route`` step, and read the logits off the intermediate
stack. The case table is the smoke path, so a coordinate with no case fails
coverage and a case whose forward breaks fails the contract.

Activation layout and batch mode (sample/cell/sequence) are asserted for the
same 11 coordinates by ``test_width_contract_lock.py``; this module owns the
execution path, not the layout schema.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest
import torch

from computronium.experiment.schema.axis import AXES_REGISTRIES, StructuralAxis
from computronium.ontology.geometry import GeometryConfig, geometry_from_config
from computronium.ontology.substrate import DigitalSubstrate

BATCH = 4


@dataclass(frozen=True, slots=True)
class GeometryCase:
    """One runtime geometry's declared smoke: inputs and the shapes it must emit."""

    config: GeometryConfig
    forward_input: torch.Tensor
    forward_shape: tuple[int, ...]
    route_input: torch.Tensor
    route_shape: tuple[int, ...]
    edge_index: torch.Tensor | None = None
    batch: torch.Tensor | None = None


def _build_cases() -> dict[str, GeometryCase]:
    generator = torch.Generator().manual_seed(91)

    def sample(*shape: int) -> torch.Tensor:
        return torch.randn(*shape, generator=generator)

    return {
        "feedforward": GeometryCase(
            config=GeometryConfig.feedforward(
                input_dim=10, output_dim=5, hidden_dims=(16,)
            ),
            forward_input=sample(BATCH, 10),
            forward_shape=(BATCH, 5),
            route_input=sample(BATCH, 10),
            route_shape=(BATCH, 5),
        ),
        "recurrent": GeometryCase(
            config=GeometryConfig.recurrent(
                input_dim=10, output_dim=5, hidden_dims=(16,)
            ),
            forward_input=sample(BATCH, 10),
            forward_shape=(BATCH, 5),
            route_input=sample(BATCH, 16),
            route_shape=(BATCH, 16),
        ),
        "tile": GeometryCase(
            config=GeometryConfig.tile(
                input_dim=10,
                output_dim=5,
                num_layers=3,
                neurons_per_tile=8,
                tiles_per_layer=2,
            ),
            forward_input=sample(BATCH, 10),
            forward_shape=(BATCH, 5),
            route_input=sample(BATCH, 10),
            route_shape=(BATCH, 31),
        ),
        "tile_mesh": GeometryCase(
            config=GeometryConfig.tile_mesh(
                input_dim=10,
                output_dim=5,
                num_layers=3,
                neurons_per_tile=8,
                tiles_per_layer=2,
            ),
            forward_input=sample(BATCH, 10),
            forward_shape=(BATCH, 5),
            route_input=sample(BATCH, 10),
            route_shape=(BATCH, 53),
        ),
        "conv": GeometryCase(
            config=GeometryConfig.conv(
                input_dim=784,
                output_dim=10,
                conv_channels=(8, 16),
                kernel_size=3,
                in_channels=1,
                input_hw=(28, 28),
                pool_hw=(4, 4),
            ),
            forward_input=sample(BATCH, 1, 28, 28),
            forward_shape=(BATCH, 10),
            route_input=sample(BATCH, 1, 28, 28),
            route_shape=(BATCH, 10),
        ),
        "graph": GeometryCase(
            config=GeometryConfig.graph(
                input_dim=16,
                output_dim=5,
                edge_index=[[0, 1, 2, 3], [1, 2, 3, 0]],
                hidden_dims=(32,),
                pooling="mean",
            ),
            forward_input=sample(4, 16),
            forward_shape=(2, 5),
            route_input=sample(4, 16),
            route_shape=(4, 5),
            edge_index=torch.tensor([[0, 1, 2, 3], [1, 2, 3, 0]], dtype=torch.long),
            batch=torch.tensor([0, 0, 1, 1], dtype=torch.long),
        ),
        "attention": GeometryCase(
            config=GeometryConfig.attention(
                input_dim=64, output_dim=10, hidden_dim=64, num_layers=2, num_heads=4
            ),
            forward_input=sample(BATCH, 64),
            forward_shape=(BATCH, 10),
            route_input=sample(BATCH, 64),
            route_shape=(BATCH, 10),
        ),
        "spatial_lattice": GeometryCase(
            config=GeometryConfig.spatial_lattice(
                input_dim=64,
                output_dim=10,
                lattice_dims=(4, 4, 4),
                hidden_dims=(32, 32),
            ),
            forward_input=sample(BATCH, 64),
            forward_shape=(BATCH, 10),
            route_input=sample(BATCH, 64, 32),
            route_shape=(BATCH, 10),
        ),
        "nca": GeometryCase(
            config=GeometryConfig.nca(
                channels=8, hidden=16, grid_hw=(8, 8), output_dim=10
            ),
            forward_input=sample(BATCH, 8, 8, 8),
            forward_shape=(BATCH, 8, 8, 8),
            route_input=sample(BATCH, 8, 8, 8),
            route_shape=(BATCH, 8, 8, 8),
        ),
        "ntm": GeometryCase(
            config=GeometryConfig.ntm(
                input_dim=16, output_dim=10, hidden=32, mem_slots=16, mem_width=8
            ),
            forward_input=sample(BATCH, 16),
            forward_shape=(BATCH, 10),
            route_input=sample(BATCH, 16),
            route_shape=(BATCH, 10),
        ),
        "causal_transformer": GeometryCase(
            config=GeometryConfig.causal_transformer(
                vocab_size=32, d_model=64, n_layers=2, n_heads=4, seq_len=16
            ),
            forward_input=torch.randint(0, 32, (BATCH, 16), generator=generator),
            forward_shape=(BATCH * 16, 32),
            route_input=torch.randint(0, 32, (BATCH, 16), generator=generator),
            route_shape=(BATCH * 16, 32),
        ),
        "routing": GeometryCase(
            config=GeometryConfig.routing(
                input_dim=16, output_dim=5, hidden_dims=(32,), num_experts=4, top_k=2
            ),
            forward_input=sample(BATCH, 16),
            forward_shape=(BATCH, 5),
            route_input=sample(BATCH, 16),
            route_shape=(BATCH, 5),
        ),
    }


CASES = _build_cases()


def test_every_runtime_geometry_has_a_case() -> None:
    """The case table and the geometry axis registry are the same set."""
    coordinates = {spec.name for spec in AXES_REGISTRIES[StructuralAxis.GEOMETRY]}
    assert coordinates == set(CASES), (
        f"geometry coordinates without a forward case: {sorted(coordinates - set(CASES))}; "
        f"cases without a coordinate: {sorted(set(CASES) - coordinates)}"
    )


@pytest.mark.parametrize("coordinate", sorted(CASES))
def test_geometry_forward_route_and_logits(coordinate: str) -> None:
    """Forward a batch, route one step, and read logits off the act stack."""
    case = CASES[coordinate]
    geometry = geometry_from_config(case.config)
    substrate = DigitalSubstrate()

    params = geometry.params
    param_count = sum(p.numel() for p in params.values())
    assert param_count > 0, f"{coordinate}: geometry exposes no parameters"

    # Route first: it takes settling-space input on a fresh state. The stateful
    # geometries (tile, nca, ntm) keep tile/grid buffers from a forward, so a
    # forward-then-route call measures leftover activity, not the routing path.
    routed = geometry.route(case.route_input)
    assert tuple(routed.shape) == case.route_shape, (
        f"{coordinate}: route emitted {tuple(routed.shape)}, "
        f"declared {case.route_shape}"
    )
    assert torch.isfinite(routed.float()).all(), f"{coordinate}: non-finite route"

    # Graph classification mode needs edge_index and batch
    if coordinate == "graph":
        output = geometry.forward(
            case.forward_input,
            substrate,
            edge_index=case.edge_index,
            batch=case.batch,
        )
        acts = geometry.forward_with_intermediates(
            case.forward_input,
            substrate,
            edge_index=case.edge_index,
            batch=case.batch,
        )
    else:
        output = geometry.forward(case.forward_input, substrate)
        acts = geometry.forward_with_intermediates(case.forward_input, substrate)
    assert tuple(output.shape) == case.forward_shape, (
        f"{coordinate}: forward emitted {tuple(output.shape)}, "
        f"declared {case.forward_shape}"
    )
    assert torch.isfinite(output.float()).all(), f"{coordinate}: non-finite forward"

    assert acts, f"{coordinate}: forward_with_intermediates returned no acts"
    logits = acts[-1]
    assert logits.shape[-1] == case.config.output_dim, (
        f"{coordinate}: last act {tuple(logits.shape)} is not the "
        f"{case.config.output_dim}-wide readout"
    )

    output.float().pow(2).mean().backward()
    grads = [p for p in geometry.parameters() if p.grad is not None]
    assert grads, f"{coordinate}: forward produced no gradient"
    assert all(torch.isfinite(g.float()).all() for g in grads), (
        f"{coordinate}: non-finite gradient"
    )

    print(
        f"{coordinate}: {param_count} params, forward {tuple(output.shape)}, "
        f"route {tuple(routed.shape)}, logits {tuple(logits.shape)}"
    )
