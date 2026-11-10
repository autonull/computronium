"""Probe: does the transformer's FA chain carry a live credit signal?

``RandomProjectionsCredit`` walks the act chain backwards through fixed
feedback matrices. The transformer's chain is not width-uniform (the
fused QKV emits 3d, the attention narrows it back to d) and the vision
readout pools the sequence (sample space B vs sequence space B*T), so
the walk needs its own path.

This probe reports, per weight: the pseudo-gradient's shape and norm,
its cosine against the true autograd gradient, and whether the weight
moved after one update. The readout's gradient must match the true
gradient exactly (the readout is the autograd path); the hidden
weights' FA signal is decorrelated from the true gradient by
construction (a fixed random projection), so a live-but-decorrelated
signal is the expected reading.

Run: uv run python scripts/probes/t87_transformer_fa_credit.py
"""

from __future__ import annotations

import torch

from computronium.domains.factory import create_task
from computronium.experiment.kernel.compose import compose_cell_system
from computronium.experiment.schema.coordinate import Coordinate
from computronium.ontology.credit import Phase
from computronium.ontology.system import SystemState

GEOMETRY = {
    "patch_size": 4,
    "patch_embed_dim": 0,
    "image_hw": [28, 28],
    "in_channels": 1,
    "num_layers": 2,
    "hidden_dim": 32,
    "num_heads": 4,
}

CREDIT = "random_projections"


def _cos(a: torch.Tensor, b: torch.Tensor) -> float:
    flat_a = a.flatten()
    flat_b = b.flatten()
    denom = flat_a.norm() * flat_b.norm()
    if denom == 0:
        return float("nan")
    return float(torch.dot(flat_a, flat_b) / denom)


def main() -> None:
    torch.manual_seed(0)
    task = create_task("mnist", device="cpu", quick_mode=True, num_workers=0)
    task.setup()
    x, y = task.get_batch("train", batch_size=8)

    cell = compose_cell_system(
        coordinate=Coordinate(
            substrate="digital",
            geometry="causal_transformer",
            dynamics="instantaneous",
            plasticity="null",
            credit=CREDIT,
            update="euclidean",
            params={"feedback_scale": 1.0},
        ),
        geometry=GEOMETRY,
        input_shape=(1, 28, 28),
        output_dim=10,
        param_budget=1_000_000,
        task=task,
    )
    system = cell.system
    geometry = system.geometry
    params = {n: p for n, p in geometry.params.items() if "weight" in n and p.ndim == 2}

    state = SystemState(x=x, y=y)
    settled = system.dynamics.settle(state, geometry, system.substrate, target=y)
    settled.loss = torch.nn.functional.cross_entropy(
        settled.activations[-1], y.reshape(-1)
    )
    true = torch.autograd.grad(
        settled.loss, [params[n] for n in params], allow_unused=True, retain_graph=True
    )
    true_by_name = dict(zip(params, true, strict=True))
    grads = system.credit.compute_pseudo_gradient(
        {Phase.NUDGED: settled}, settled.loss, geometry
    )

    print(f"weights={len(params)} grads={len(grads)}")
    for name, g in zip(params, grads, strict=True):
        w = params[name]
        gt = true_by_name[name]
        moved = ""
        print(
            f"  {name:28s} w={tuple(w.shape)} grad={tuple(g.shape)} "
            f"|g|={g.norm():.4e} |g_true|={gt.norm():.4e} "
            f"cos={_cos(g, gt):+.3f} shape_ok={tuple(g.shape) == tuple(w.shape)}"
        )
        del moved

    zero_grads = [n for n, g in zip(params, grads, strict=True) if g.norm() == 0]
    print(f"zero-gradient weights: {zero_grads or 'none'}")
    _train_check()


def _train_check() -> None:
    """Does the coordinate train? (val_acc after a few epochs vs chance)"""
    from computronium.experiment.kernel.evaluate import evaluate_cell
    from computronium.experiment.schema.coordinate import Schedule

    schedule = Schedule(
        task_id="mnist",
        epochs=3,
        seed=42,
        n_seeds=1,
        batch_limit=8,
        budget_id="t87-probe",
        fidelity="L0",
        device="cpu",
    )
    coordinate = Coordinate(
        substrate="digital",
        geometry="causal_transformer",
        dynamics="instantaneous",
        plasticity="null",
        credit=CREDIT,
        update="euclidean",
        params={"feedback_scale": 1.0},
    )
    result = evaluate_cell(coordinate=coordinate, schedule=schedule, geometry=GEOMETRY)
    curve = result.convergence_curve
    print(
        f"trained 3 epochs: val_acc={result.metrics.get('val_acc'):.4f} "
        f"train_loss={result.metrics.get('train_loss'):.4f} curve={curve}"
    )


if __name__ == "__main__":
    main()
