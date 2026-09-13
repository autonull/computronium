"""Honest val-split re-measurement for the legacy catalog rows (TODO23 §12).

The quick-tier campaign metric (train_acc) is teacher-forced for some
mechanisms (FF's label-injected classifier pass; pepita's free-phase
settle that carries the error-modulation pass). The uniform honest
protocol: train via Lab.train, score via ``system.forward`` on the
unpermuted val split (val_acc). backprop_mlp runs as the control that
must track its known 0.896@20ep operating point.

uv run python scripts/probes/remeasure_val_split.py
Walltime printed, never recorded.
"""

from __future__ import annotations

import time

from computronium_lab.lab import Lab, synthetic_task
from computronium_lab.synthesis.catalog import CATALOG
from computronium_lab.synthesis.spec import Constraints, ProblemSpec
from computronium_lab.training import TrainOptions
from torch.utils.data import DataLoader, TensorDataset

spec = ProblemSpec(
    task="classification",
    dataset="gaussian_blobs",
    constraints=Constraints(substrate="digital"),
    objectives=("accuracy",),
    input_dim=32,
    num_classes=4,
)

lab = Lab(device="cpu")


def val_loader(seed: int):
    _, val = synthetic_task(seed=seed, input_dim=32, num_classes=4)
    ds = val.dataset
    if not isinstance(ds, TensorDataset):
        raise TypeError
    return DataLoader(TensorDataset(*ds.tensors), batch_size=256)


for name in ("backprop_mlp", "ff_mlp", "fa_mlp", "pepita_mlp"):
    cand = next(c for c in CATALOG if c.name == name)
    for epochs in (10, 20):
        t0 = time.perf_counter()
        train_accs, val_accs = [], []
        for seed in (0, 1, 2):
            lab.seed = seed
            system = cand.build(spec)
            result = lab.train(
                system,
                epochs=epochs,
                spec=spec,
                options=TrainOptions(val_data=val_loader(seed)),
            )
            train_accs.append(float(result.metrics["accuracy"]))
            val_accs.append(float(result.metrics["val_acc"]))
        print(
            f"{name} @ {epochs}ep: train={[round(a, 3) for a in train_accs]} "
            f"val={[round(a, 3) for a in val_accs]} "
            f"val_mean={sum(val_accs) / len(val_accs):.3f} "
            f"({time.perf_counter() - t0:.1f}s)"
        )
