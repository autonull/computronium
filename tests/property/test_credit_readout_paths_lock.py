"""Credit readout-path locks (TODO88 R3/R4).

Two credit families broke on act stacks whose readout is not layer-aligned:

- ``target_inversion`` and ``temporal_trace`` on a pooled graph readout
  (node-sized hidden acts, graph-sized logits) raised shape errors, so two
  advertised credits died at runtime on every graph-classification task.
- ``homeostatic`` on the causal transformer emitted zeros for the fused QKV
  projection: no act in the chain carries its 3d width, so ``_weight_acts``
  returned None and the credit skipped the weight.

Each test drives a real ``train_step`` and asserts every 2-D weight moves.
Removing the pooled-readout / transformer-aware path makes the fixture raise
or leaves the weight frozen.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import torch
from torch import Tensor

from computronium.core.system_trainer.spec import compose_system_from_configs
from computronium.ontology.credit import CreditAssignmentConfig
from computronium.ontology.dynamics import StateDynamicsConfig
from computronium.ontology.geometry import GeometryConfig
from computronium.ontology.substrate import SubstrateConfig
from computronium.ontology.update import ParameterUpdateConfig

if TYPE_CHECKING:
    from torch_geometric.data import Batch
    from torch_geometric.data.data import BaseData

INPUT_DIM, OUTPUT_DIM = 8, 3


def _batch() -> Batch:
    from torch_geometric.data import Batch, Data

    generator = torch.Generator().manual_seed(3)
    graphs: list[BaseData] = [
        Data(
            x=torch.randn(5, INPUT_DIM, generator=generator),
            y=torch.randint(0, OUTPUT_DIM, (1,), generator=generator),
            edge_index=torch.tensor([
                list(range(5)),
                [(i + 1) % 5 for i in range(5)],
            ]),
        )
        for _ in range(4)
    ]
    return Batch.from_data_list(graphs)


def _graph_system(credit: str):
    data = _batch()
    torch.manual_seed(0)
    return compose_system_from_configs(
        SubstrateConfig.digital(),
        GeometryConfig.graph(
            input_dim=INPUT_DIM,
            output_dim=OUTPUT_DIM,
            edge_index=data.edge_index.tolist(),
            hidden_dims=(16,),
        ),
        StateDynamicsConfig.instantaneous(),
        getattr(CreditAssignmentConfig, credit)(),
        ParameterUpdateConfig.adam(step_size=1e-2),
    )


def _moved_weights(system, before: dict[str, Tensor]) -> dict[str, bool]:
    return {
        name: (system.geometry.params[name] - before[name]).abs().max().item() > 0
        for name in before
    }


@pytest.mark.timeout(120)
@pytest.mark.parametrize("credit", ["target_inversion", "temporal_trace"])
def test_pooled_readout_credits_update_every_weight(credit: str) -> None:
    """Both credits clear a pooled graph readout and move every weight."""
    data = _batch()
    system = _graph_system(credit)
    before = {
        name: t.detach().clone()
        for name, t in system.geometry.params.items()
        if t.ndim == 2
    }
    metrics = system.train_step(
        data.x, data.y, edge_index=data.edge_index, batch=data.batch
    )
    assert torch.isfinite(torch.tensor(metrics["loss"]))
    moved = _moved_weights(system, before)
    assert all(moved.values()), f"{credit} froze weights on a pooled readout: {moved}"


@pytest.mark.timeout(120)
def test_homeostatic_updates_transformer_fused_qkv() -> None:
    """The fused QKV projection receives a norm-regulating update (R4)."""
    torch.manual_seed(0)
    system = compose_system_from_configs(
        SubstrateConfig.digital(),
        GeometryConfig.causal_transformer(
            vocab_size=4,
            d_model=16,
            n_layers=1,
            n_heads=2,
            seq_len=4,
            patch_size=4,
            image_hw=(8, 8),
            in_channels=1,
        ),
        StateDynamicsConfig.instantaneous(),
        CreditAssignmentConfig.homeostatic(),
        ParameterUpdateConfig.adam(step_size=1e-2),
    )
    before = {
        name: t.detach().clone()
        for name, t in system.geometry.params.items()
        if t.ndim == 2
    }
    x = torch.randn(4, 1, 8, 8)
    y = torch.randint(0, 4, (4,))
    metrics = system.train_step(x, y)
    assert torch.isfinite(torch.tensor(metrics["loss"]))
    moved = _moved_weights(system, before)
    assert moved.get("blocks.0.in_proj.weight"), moved
    assert all(moved.values()), f"homeostatic froze transformer weights: {moved}"
