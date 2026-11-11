"""MUTAG graph-geometry expressivity probe (TODO88 next-step 2).

Question: is the 60-63% MUTAG ceiling a limit of the task/model size, or an
implementation defect? The TODO88 claim was "fundamental limitation of MUTAG
with this model size"; the suspicious signatures were

- 20-epoch runs sat *below* the majority-class baseline of their own split
  (25/38 = 0.658), and
- train accuracy plateaued at ~0.77, i.e. the model could not fit 150 graphs.

Recorded pre-fix (2026-11-11, MUTAG 188 graphs / 7 atom features / 2 classes,
deterministic stratified 80/20 split, 3 x 64 hidden, batch 64, Adam 1e-2,
200 epochs, seed 0, plain autograd around the geometry, no self connection in
aggregation):

    self_loops=False                train 0.780  val 0.711  val_loss 0.6308
    self_loops=True                 train 0.807  val 0.737  val_loss 0.5535
    self_loops=True hidden=128      train 0.827  val 0.737  val_loss 0.6042
    self_loops=True pool=sum        train 0.867  val 0.737  val_loss 0.5667
    self_loops=True h=128 L=4 sum   train 0.867  val 0.737  val_loss 0.6483

Verdict: the ceiling was an implementation defect (a bare neighbour mean has no
self connection, so ``h[i]`` never contains ``x[i]`` and source-only nodes
collapse to zero). With the shipped ``(A + I)`` aggregation MUTAG clears the
0.70 target on the 38-graph held-out split. Walltime is ~0.05 s/epoch, so the
L0 "too slow / budget-limited" note on this task was also stale.

This script re-measures the shipped geometry (``GraphGeometry.forward``, mean
pooling, mean aggregation with self connection) so the numbers above can be
checked against the current code:

    uv run python scripts/probes/mutag_geometry_probe.py
"""

from __future__ import annotations

import collections

import torch
from torch_geometric.datasets import TUDataset
from torch_geometric.loader import DataLoader

from computronium.domains.factory import _stratified_split
from computronium.ontology.geometry import GeometryConfig, GraphGeometry

EPOCHS = 200
BATCH_SIZE = 64
LR = 1e-2
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def _load() -> tuple[TUDataset, torch.Tensor, torch.Tensor, torch.Tensor]:
    dataset = TUDataset(root="./data", name="MUTAG")
    labels = torch.cat([data.y.view(-1) for data in dataset])
    train_idx, val_idx = _stratified_split(labels)
    return dataset, labels, train_idx, val_idx


def _train(*, hidden: int = 64, layers: int = 3, seed: int = 0) -> dict[str, float]:
    dataset, _labels, train_idx, val_idx = _load()
    geometry = GraphGeometry(
        GeometryConfig.graph(
            input_dim=int(dataset.num_features),
            output_dim=int(dataset.num_classes),
            edge_index=dataset[0].edge_index.tolist(),
            hidden_dims=(hidden,) * layers,
        )
    ).to(DEVICE)
    optim = torch.optim.Adam(geometry.parameters(), lr=LR)
    train_loader = DataLoader(dataset[train_idx], batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(dataset[val_idx], batch_size=BATCH_SIZE, shuffle=False)

    def _epoch(loader: DataLoader, *, train: bool) -> tuple[float, float]:
        total_loss = total_correct = total = 0
        for data in loader:
            data = data.to(DEVICE)
            out = geometry.forward(data.x, edge_index=data.edge_index, batch=data.batch)
            loss = torch.nn.functional.cross_entropy(out, data.y)
            if train:
                optim.zero_grad()
                loss.backward()
                optim.step()
            with torch.no_grad():
                total_correct += int((out.argmax(1) == data.y).sum())
                total_loss += float(loss) * data.num_graphs
                total += data.num_graphs
        return total_loss / total, total_correct / total

    for _ in range(EPOCHS):
        _epoch(train_loader, train=True)
    with torch.no_grad():
        _, train_acc = _epoch(train_loader, train=False)
        val_loss, val_acc = _epoch(val_loader, train=False)
    return {"train_acc": train_acc, "val_acc": val_acc, "val_loss": val_loss}


def main() -> None:
    _dataset, labels, _train_idx, val_idx = _load()
    majority = max(collections.Counter(labels[val_idx].tolist()).values()) / len(
        val_idx
    )
    print(f"majority-class val baseline = {majority:.3f}  (val n={len(val_idx)})")
    for seed in (0, 1, 2, 3, 4):
        torch.manual_seed(seed)
        result = _train(seed=seed)
        print(
            f"seed={seed} train_acc={result['train_acc']:.3f} "
            f"val_acc={result['val_acc']:.3f} val_loss={result['val_loss']:.4f}"
        )


if __name__ == "__main__":
    main()
