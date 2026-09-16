"""W2 defect-hunt: close the library-vs-probe gradient discrepancy, then map
the class's depth frontier through the real pipeline.

RESOLUTION (2026-09-07, full bisection trail — three stacked findings):

1. **EMA recipe drift** (``LocalContrastiveCredit._ema_normalize``): scalar
   EMA of mean(gw^2), ones warm-start, no bias correction, eps outside the
   sqrt. Fixed to the element-wise, zeros-warm-start, bias-corrected form
   with eps INSIDE the sqrt (outside-eps re-amplifies satisfied-gate ~0
   gradients into full-size steps — the collapse the rung exists to fix).
2. **Ordering semantics**: the reference probes (b4, w2_ema_rung) update
   each hidden layer INSIDE the batch loop, so layer i+1's input stream is
   formed against layer i's post-update weights. Jacobi (simultaneous)
   ordering collapses the recipe: probe d4 0.76 → 0.27, d8 0.51 → 0.14.
   Landed as ``sequential_lr`` — measured as the load-bearing depth
   mechanism, not a nicety.
3. **The old "probe references" (d2 0.824 / d4 0.757 / d8 0.512 @ EMA
   lr 0.3) are NOT reproducible from committed code** — the committed
   w2_ema_rung.train_acc at lr 0.3 gives 0.507 (beta 0.99) / 0.542
   (0.999). Chasing them was the defect hunt's red herring. The
   reproducible frontier is b4's RAW recipe (raw grads, lr 0.5,
   sequential): d2 0.827 / d4 0.764, d8 unmeasured.

TWO-REGIME VERDICT (this probe, through the real pipeline, seeds 0-2,
150-step MNIST-quick):

- **raw (ema_beta=0) lr 0.5 sequential** — d2 0.853, d4 0.789: BEATS the
  b4 raw frontier at both depths. The d2/d4 operating point.
- **EMA (beta 0.99) lr 0.3 sequential** — d2 0.751, d4 0.349, **d8 0.220
  where raw collapses to chance (0.106)**. P3-in-library confirmed in its
  true form: the EMA rung is the depth-8 repair, not a d2/d4 parity tool.
- Readout bias is load-bearing in the probe harness (freezing collapses
  d2 0.82 → 0.52 there); in-library it rides ``compute_bias_pseudo_gradients``
  through the U-axis. Note: the pipeline library is markedly LESS
  init-sensitive than the probe harness (0.75 vs 0.52 spread) — the
  composed pipeline is the more stable instrument.

Harness (consumer contract, do not re-derive): euclid grad_clip=0 (global-
norm clip crushes EMA-normalized grads ~1000x), momentum=0 (probe is plain
SGD), RAW data + one-hot label appended (never pre-normalized input),
readout rides raw CE x readout_scale under the single update-axis lr,
``sequential_lr`` must equal the update step_size.
"""

import itertools
import time
from typing import TYPE_CHECKING, cast

import torch
import torch.nn.functional as F  # ruff: ignore[lowercase-imported-as-non-lowercase]
from torch import nn

from computronium.core.pipeline import run_train_step
from computronium.domains.factory import create_task

if TYPE_CHECKING:
    from computronium.domains.base import DomainTask
from computronium.ontology.credit import CreditAssignmentConfig, LocalContrastiveCredit
from computronium.ontology.dynamics import InstantaneousDynamics, StateDynamicsConfig
from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
from computronium.ontology.substrate._substrate import DigitalSubstrate
from computronium.ontology.update import EuclideanUpdate, ParameterUpdateConfig

STEPS = 150
N_CLASSES = 10
LABEL_DIM = 10


def _data():
    task = cast("DomainTask", create_task("mnist", device="cpu", quick_mode=True))
    task.setup()
    torch.manual_seed(0)  # seed BEFORE the loader draw (D8 trap)
    train = [
        (xb.view(xb.size(0), -1), yb)
        for xb, yb in itertools.islice(task.get_dataloader("train"), STEPS)
    ]
    test = [
        (xb.view(xb.size(0), -1), yb)
        for xb, yb in task.get_dataloader("test")
        if xb.size(0) == 32
    ]
    return train, test


def _augment(x: torch.Tensor, y: torch.Tensor, good: bool) -> torch.Tensor:
    """RAW data + one-hot label — the credit Hinton-normalizes internally
    (verified bit-identical grads to the probe on this contract; feeding a
    pre-normalized stream double-normalizes and perturbs the label cols)."""
    onehot = F.one_hot(y, N_CLASSES).float()
    if not good:
        onehot = onehot.roll(1, 0)  # wrong-label negative (Hinton/b4 recipe)
    return torch.cat([x, onehot], dim=-1)


def _build_geometry(depth: int, seed: int) -> FeedforwardGeometry:
    torch.manual_seed(seed)
    layers: list[nn.Module] = [nn.Linear(784 + LABEL_DIM, 128), nn.ReLU()]
    for _ in range(depth - 2):
        layers += [nn.Linear(128, 128), nn.ReLU()]
    layers.append(nn.Linear(128, N_CLASSES))
    cfg = GeometryConfig.feedforward(
        input_dim=784 + LABEL_DIM,
        hidden_dims=(128,) * (depth - 1),
        output_dim=N_CLASSES,
    )
    geo = FeedforwardGeometry(cfg, layers=layers)
    geo._set_param_names()
    return geo


def run_arm(
    depth: int,
    seed: int,
    lr: float,
    train,
    test,
    *,
    ema_beta: float = 0.99,
    seq: float | None = None,
    ro_scale: float = 1 / 3,
) -> float:
    geo = _build_geometry(depth, seed)
    credit = LocalContrastiveCredit(
        CreditAssignmentConfig.local_contrastive(
            label_dim=LABEL_DIM,
            ema_beta=ema_beta,
            stream_norm=True,
            readout_scale=ro_scale,
            sequential_lr=lr if seq is None else seq,
        )
    )
    update = EuclideanUpdate(
        ParameterUpdateConfig.euclidean(step_size=lr, momentum=0.0, grad_clip=0.0)
    )
    dyn = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
    substrate = DigitalSubstrate()
    for x, y in train[:STEPS]:
        x_pos = _augment(x, y, True)
        run_train_step(
            substrate,
            geo,
            dyn,
            credit,
            update,
            x_pos,
            y,
        )
    correct = total = 0
    with torch.no_grad():
        for x, y in test:
            logits = geo.forward(_augment(x, y, True), substrate)
            correct += (logits.argmax(1) == y).sum().item()
            total += y.size(0)
    return correct / total


def main() -> int:
    t0 = time.perf_counter()
    train, test = _data()
    print(
        "=== W2 library operating-point sweep (b4 raw frontier: d2 0.827 / "
        "d4 0.764 @ raw lr 0.5 sequential) ===",
        flush=True,
    )
    arms = [
        ("raw lr0.5 seq", {"ema_beta": 0.0, "seq": 0.5, "ro_scale": 0.2}, 0.5),
        ("ema0.99 lr0.3 seq", {"ema_beta": 0.99, "seq": 0.3, "ro_scale": 1 / 3}, 0.3),
        ("ema0.999 lr0.3 seq", {"ema_beta": 0.999, "seq": 0.3, "ro_scale": 1 / 3}, 0.3),
    ]
    for depth in (2, 4):
        for name, kw, lr in arms:
            accs = [run_arm(depth, s, lr, train, test, **kw) for s in (0, 1, 2)]
            mean = sum(accs) / 3
            print(
                f"d{depth} {name}: mean {mean:.3f} seeds {[round(a, 3) for a in accs]}",
                flush=True,
            )
    print(f"walltime {time.perf_counter() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
