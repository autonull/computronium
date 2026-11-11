"""Graph pipeline-path lock (TODO88 G1/G2).

Every GraphSystemTrainer epoch must route through the canonical
``system.train_step`` pipeline (dynamics settle → credit → update axis) —
the pre-G1 trainer ran plain ``loss.backward()`` + an external Adam,
measuring GNN autograd instead of the coordinate's primitives, which made
every graph-domain credit/update attribution bit-identical. The lock:

1. a spy asserts the trainer drives epochs through ``train_step``;
2. geometry parameters actually move through the pipeline;
3. gradient vs random_projections credit produce *different* parameter
   deltas on the same graph task (the exact G1 symptom was bit-identity);
4. graph kwargs are geometry-conditional: a feedforward system tolerates
   ``edge_index``/``batch`` kwargs (dropped), a graph system consumes them.
"""

from typing import Any, Literal

import pytest
import torch
from torch import Tensor

from computronium.core.pipeline import run_train_step
from computronium.core.system_trainer.config import SystemTrainerConfig
from computronium.core.system_trainer.graph_trainer import GraphSystemTrainer
from computronium.core.system_trainer.spec import compose_system_from_configs
from computronium.ontology.credit import CreditAssignmentConfig
from computronium.ontology.dynamics import StateDynamicsConfig
from computronium.ontology.geometry import GeometryConfig
from computronium.ontology.substrate import SubstrateConfig
from computronium.ontology.update import ParameterUpdateConfig

INPUT_DIM, OUTPUT_DIM, NUM_NODES = 8, 3, 24
HIDDEN_DIMS = (16,)
EDGE_INDEX = [
    [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
    ],
    [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        0,
    ],
]


def _graph_geometry_config() -> GeometryConfig:
    return GeometryConfig.graph(
        input_dim=INPUT_DIM,
        output_dim=OUTPUT_DIM,
        edge_index=EDGE_INDEX,
        hidden_dims=HIDDEN_DIMS,
    )


def _compose(credit: str):
    torch.manual_seed(0)
    return compose_system_from_configs(
        SubstrateConfig.digital(),
        _graph_geometry_config(),
        StateDynamicsConfig.instantaneous(),
        _credit_config(credit),
        ParameterUpdateConfig.adam(step_size=1e-2),
    )


def _credit_config(credit: str) -> CreditAssignmentConfig:
    match credit:
        case "gradient":
            return CreditAssignmentConfig.gradient()
        case "random_projections":
            return CreditAssignmentConfig.random_projections()
        case _:
            raise ValueError(credit)


class _NodeClassificationTask:
    """Minimal Planetoid-shaped task: single graph with train/val masks."""

    _setup_done = True

    def __init__(self) -> None:
        from torch_geometric.data import Data

        generator = torch.Generator().manual_seed(7)
        x = torch.randn(NUM_NODES, INPUT_DIM, generator=generator)
        y = torch.randint(0, OUTPUT_DIM, (NUM_NODES,), generator=generator)
        train_mask = torch.zeros(NUM_NODES, dtype=torch.bool)
        train_mask[::3] = True
        val_mask = torch.zeros(NUM_NODES, dtype=torch.bool)
        val_mask[1::3] = True
        self._data = Data(
            x=x,
            y=y,
            edge_index=torch.tensor(EDGE_INDEX, dtype=torch.long),
            train_mask=train_mask,
            val_mask=val_mask,
        )


class _TrainStepSpy:
    """Forward every attribute to the system, recording train_step calls."""

    def __init__(self, system: object) -> None:
        object.__setattr__(self, "_system", system)
        object.__setattr__(self, "train_step_calls", [])

    def train_step(
        self, x: Tensor, y: Tensor, **graph_kwargs: Tensor
    ) -> dict[str, float]:
        object.__getattribute__(self, "train_step_calls").append((
            x.shape,
            tuple(graph_kwargs),
        ))
        return object.__getattribute__(self, "_system").train_step(x, y, **graph_kwargs)  # type: ignore[attr-defined]

    def __getattr__(self, name: str):
        return getattr(object.__getattribute__(self, "_system"), name)


def _train_one_epoch(system: object) -> tuple[GraphSystemTrainer, dict[str, float]]:
    trainer = GraphSystemTrainer(
        system,  # type: ignore[arg-type]
        SystemTrainerConfig(
            max_epochs=1,
            device="cpu",
            seed=0,
            log_every_n_steps=0,
            log_every_n_epochs=0,
        ),
        train_data=_NodeClassificationTask(),
    )
    metrics = trainer.train_epoch()
    return trainer, metrics


def _param_snapshot(trainer: GraphSystemTrainer) -> dict[str, Tensor]:
    return {
        name: t.detach().clone() for name, t in trainer.system.geometry.params.items()
    }


@pytest.mark.timeout(120)
def test_graph_trainer_routes_through_train_step() -> None:
    system = _compose("gradient")
    spy = _TrainStepSpy(system)
    _trainer, metrics = _train_one_epoch(spy)
    calls = spy.train_step_calls
    assert len(calls) == 1, calls
    (x_shape, kwargs) = calls[0]
    assert x_shape == (NUM_NODES, INPUT_DIM)
    assert kwargs == (), kwargs
    assert torch.isfinite(torch.tensor(metrics["train_loss"]))


@pytest.mark.timeout(120)
def test_graph_trainer_moves_params_through_pipeline() -> None:
    system = _compose("gradient")
    before = {name: t.detach().clone() for name, t in system.geometry.params.items()}
    trainer, _ = _train_one_epoch(system)
    after = _param_snapshot(trainer)
    deltas = {name: (after[name] - before[name]).abs().max().item() for name in before}
    assert any(d > 0.0 for d in deltas.values()), deltas


@pytest.mark.timeout(180)
def test_graph_credits_produce_different_updates() -> None:
    snapshots: dict[str, dict[str, Tensor]] = {}
    for credit in ("gradient", "random_projections"):
        system = _compose(credit)
        before = {
            name: t.detach().clone() for name, t in system.geometry.params.items()
        }
        trainer, _ = _train_one_epoch(system)
        after = _param_snapshot(trainer)
        snapshots[credit] = {name: after[name] - before[name] for name in before}
    gradient_deltas = snapshots["gradient"]
    rp_deltas = snapshots["random_projections"]
    differing = [
        name
        for name in gradient_deltas
        if (gradient_deltas[name] - rp_deltas[name]).abs().max().item() > 1e-9
    ]
    assert differing, "credits produced bit-identical updates (G1 regression)"


@pytest.mark.timeout(120)
def test_graph_classification_routes_graph_kwargs() -> None:
    """Batched graphs reach the pipeline with edge_index/batch (G2)."""
    from torch_geometric.data import Batch, Data

    def _batch(num_graphs: int = 4) -> Batch:
        graphs = []
        for _ in range(num_graphs):
            nodes = 5
            graphs.append(
                Data(
                    x=torch.randn(nodes, INPUT_DIM),
                    y=torch.randint(0, OUTPUT_DIM, (1,)),
                    edge_index=torch.tensor([
                        list(range(nodes)),
                        [(i + 1) % nodes for i in range(nodes)],
                    ]),
                )
            )
        return Batch.from_data_list(graphs)

    class _GraphClassificationTask:
        _setup_done = True

        def get_dataloader(self, _split: str) -> list[Batch]:
            return [_batch(), _batch()]

    system = _compose("gradient")
    spy = _TrainStepSpy(system)
    before = {name: t.detach().clone() for name, t in system.geometry.params.items()}
    trainer = GraphSystemTrainer(
        spy,  # type: ignore[arg-type]
        SystemTrainerConfig(
            max_epochs=1,
            device="cpu",
            seed=0,
            log_every_n_steps=0,
            log_every_n_epochs=0,
        ),
        train_data=_GraphClassificationTask(),
    )
    metrics = trainer.train_epoch()
    assert len(spy.train_step_calls) == 2
    assert all(call[1] == ("edge_index", "batch") for call in spy.train_step_calls)
    assert torch.isfinite(torch.tensor(metrics["train_loss"]))
    after = _param_snapshot(trainer)
    assert any((after[name] - before[name]).abs().max().item() > 0.0 for name in before)


@pytest.mark.parametrize("pooling", ["mean", "sum"])
@pytest.mark.timeout(180)
def test_pooled_readout_credit_trains_and_differs_from_gradient(
    pooling: Literal["mean", "sum"],
) -> None:
    """A pooled graph readout keeps FA's error chain intact (G5).

    Node acts are pooled per graph before the head, so a credit that walks the
    error back through weight-shaped feedback matrices meets a node-sized act
    stack with a batch-sized error. The fix routes it through the geometry's
    pooling map; removing that path reproduces the shape crash. The sum arm
    also proves the transpose is the pooling mode's, not a mean in disguise.
    """
    from torch_geometric.data import Batch, Data

    def _batch() -> Batch:
        generator = torch.Generator().manual_seed(3)
        graphs = [
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

    data = _batch()
    deltas: dict[str, dict[str, Tensor]] = {}
    for credit in ("gradient", "random_projections"):
        torch.manual_seed(0)
        system = compose_system_from_configs(
            SubstrateConfig.digital(),
            GeometryConfig.graph(
                input_dim=INPUT_DIM,
                output_dim=OUTPUT_DIM,
                edge_index=data.edge_index.tolist(),
                hidden_dims=HIDDEN_DIMS,
                pooling=pooling,
            ),
            StateDynamicsConfig.instantaneous(),
            _credit_config(credit),
            ParameterUpdateConfig.adam(step_size=1e-2),
        )
        before = {
            name: t.detach().clone() for name, t in system.geometry.params.items()
        }
        metrics = system.train_step(
            data.x, data.y, edge_index=data.edge_index, batch=data.batch
        )
        assert torch.isfinite(torch.tensor(metrics["loss"]))
        deltas[credit] = {
            name: system.geometry.params[name] - before[name] for name in before
        }

    moved = [
        name
        for name, delta in deltas["random_projections"].items()
        if delta.abs().max() > 0
    ]
    assert moved, "random_projections moved no parameter through a pooled readout"
    assert any(
        (deltas["gradient"][name] - deltas["random_projections"][name]).abs().max()
        > 1e-9
        for name in moved
    ), "pooled-readout FA produced gradient-identical deltas"


@pytest.mark.timeout(60)
def test_sum_pooling_readout_matches_add_pool() -> None:
    """Sum pooling reduces the node stack by addition, not by node-count mean."""
    from dataclasses import replace

    from torch_geometric.data import Batch, Data
    from torch_geometric.nn import global_add_pool

    from computronium.ontology.geometry import GraphGeometry

    data: Any = Batch.from_data_list([
        Data(
            x=torch.randn(nodes, INPUT_DIM),
            y=torch.zeros(1, dtype=torch.long),
            edge_index=torch.tensor([
                list(range(nodes)),
                [(i + 1) % nodes for i in range(nodes)],
            ]),
        )
        for nodes in (4, 6)
    ])
    geometry = GraphGeometry(
        GeometryConfig.graph(
            input_dim=INPUT_DIM,
            output_dim=OUTPUT_DIM,
            edge_index=data.edge_index.tolist(),
            hidden_dims=HIDDEN_DIMS,
        )
    )
    with torch.no_grad():
        mean_acts = geometry.forward_with_intermediates(
            data.x, edge_index=data.edge_index, batch=data.batch
        )
        mean_out = mean_acts[-1]
        assert geometry.pool_context() is not None
        mean_context = geometry.pool_context()
        assert mean_context is not None and mean_context.mean
        geometry.config = replace(geometry.config, pooling="sum")
        sum_acts = geometry.forward_with_intermediates(
            data.x, edge_index=data.edge_index, batch=data.batch
        )
        sum_out = sum_acts[-1]
        sum_context = geometry.pool_context()
        assert sum_context is not None and not sum_context.mean
        expected = (
            global_add_pool(sum_acts[-2], data.batch) @ geometry._head.weight.T
            + geometry._head.bias
        )
    torch.testing.assert_close(sum_out, expected)
    assert not torch.allclose(mean_out, sum_out)


@pytest.mark.timeout(120)
def test_graph_kwargs_are_geometry_conditional() -> None:
    from computronium.ontology.geometry import FeedforwardGeometry

    torch.manual_seed(0)
    feedforward = compose_system_from_configs(
        SubstrateConfig.digital(),
        GeometryConfig.feedforward(
            input_dim=INPUT_DIM, output_dim=OUTPUT_DIM, hidden_dims=HIDDEN_DIMS
        ),
        StateDynamicsConfig.instantaneous(),
        CreditAssignmentConfig.gradient(),
        ParameterUpdateConfig.adam(step_size=1e-2),
    )
    geometry = feedforward.geometry
    assert isinstance(geometry, FeedforwardGeometry)
    assert not getattr(geometry, "accepts_graph_kwargs", False)
    x = torch.randn(4, INPUT_DIM)
    y = torch.randint(0, OUTPUT_DIM, (4,))
    edge_index = torch.tensor([[0, 1, 2, 3], [1, 2, 3, 0]], dtype=torch.long)
    batch = torch.arange(4)
    # A non-graph geometry must tolerate graph kwargs (dropped), not raise
    # the TypeError that forced every graph cell onto the G1 bypass.
    metrics = run_train_step(
        feedforward.substrate,
        geometry,
        feedforward.dynamics,
        feedforward.credit,
        feedforward.update,
        x,
        y,
        edge_index=edge_index,
        batch=batch,
    )
    assert torch.isfinite(torch.tensor(metrics["free_loss"]))
