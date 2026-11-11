"""Lock: graph-classification cells report the majority baseline (R1).

The MUTAG held-out split is 38 graphs (25/13), so one graph is 0.026 and the
majority-class rate is 0.658 — a val_acc of 0.63 is *below* chance, which the
raw number hides. ``GraphClassificationTask.evaluate`` now reports the
measured majority rate and the signed margin beside accuracy, and the kernel
copies every task metric into the cell payload.

The fixture is a fake PyG-shaped batch, so the test measures the protocol
wiring, not torch_geometric.
"""

from __future__ import annotations

import torch
from torch import nn

from computronium.domains.base import Metrics, TaskSplit
from computronium.domains.factory import GraphClassificationTask


class _Batch:
    """The subset of a PyG ``Data`` batch that ``evaluate`` reads."""

    def __init__(self, y: torch.Tensor) -> None:
        self.num_graphs = int(y.numel())
        self.x = torch.zeros(self.num_graphs, 3)
        self.edge_index = torch.zeros(2, 0, dtype=torch.long)
        self.batch = torch.arange(self.num_graphs)
        self.y = y

    def to(self, device: torch.device) -> _Batch:
        return self


class _ConstantModel(nn.Module):
    """Predicts class 0 for every graph."""

    def __init__(self, num_classes: int = 2) -> None:
        super().__init__()
        self.anchor = nn.Parameter(torch.zeros(1))
        self.num_classes = num_classes

    def forward(self, x, edge_index, batch):  # ruff: ignore[missing-type-function-argument, missing-return-type-undocumented-public-function]
        rows = int(batch.max()) + 1
        logits = torch.zeros(rows, self.num_classes, device=x.device)
        logits[:, 0] = 1.0
        return logits + 0.0 * self.anchor


def _task(batches: list[_Batch]) -> GraphClassificationTask:
    task = GraphClassificationTask(name="graph_classification", device="cpu")
    task._val_loader = batches
    task._setup_done = True
    return task


def test_evaluate_reports_majority_baseline() -> None:
    # 6 graphs, class 0 is the majority (4/6 = 0.667); the model gets 4 right.
    batches = [_Batch(torch.tensor([0, 1, 0])), _Batch(torch.tensor([0, 0, 1]))]
    metrics = _task(batches).evaluate(_ConstantModel(), split=TaskSplit.VAL)

    assert isinstance(metrics, Metrics)
    assert metrics.custom["majority_baseline"] == 4 / 6
    assert metrics.accuracy == 4 / 6
    assert metrics.custom["val_acc_over_majority"] == 0.0
    payload = metrics.to_dict()
    assert payload["majority_baseline"] == 4 / 6
    assert payload["val_acc_over_majority"] == 0.0


def test_evaluate_reports_negative_margin_below_chance() -> None:
    # Class 1 is the majority (3/4 = 0.75); the model predicts class 0.
    batches = [_Batch(torch.tensor([1, 1, 1, 0]))]
    metrics = _task(batches).evaluate(_ConstantModel(), split=TaskSplit.VAL)

    assert metrics.custom["majority_baseline"] == 0.75
    assert metrics.custom["val_acc_over_majority"] == -0.5
