"""N7 probe: the regime the label-channel cell actually trains in.

TODO88 N7 wired ``local_contrastive``'s label channel (input widened by the
task's class count, ``[x | one_hot(y)]`` per batch, label-sweep inference).
The first live cell measured val_acc 0.52 -> 0.59 over 10 epochs while its
reported free loss grew 223 -> 1121. Two questions:

1. Is 0.52 the credit's *measured* slow regime? ``scripts/probes/w2_ema_rung.py``
   says the EMA-normalized rung needs lr 0.1-0.3 and that "at 1e-3-0.01
   normalized rungs are just slow (~0.5 d2)". The harness cell runs at
   ``update.step_size=0.001``, so yes by that record.
2. Why does the loss grow? Hypothesis: the credit recomputes a
   **stream-normalized** prefix (``stream_norm``: every layer output is
   rescaled to length sqrt(width)), but the geometry's own forward does not
   normalize, so the head is trained on unit-scale features and then applied
   to unnormalized ones. Growing ``‖h‖`` under the goodness contrast would
   then inflate logits and CE without changing argmax much.

Measured (2026-11-12, CPU, mnist quick, hidden 64 x 2, 300 steps, adam 1e-3):

    step   ‖h1‖    ‖h2‖   ‖W_head‖F     CE    val_acc
       0   1.02    1.05       4.9      2.30     0.09
     100   1.09    2.66      12.4     22.1      0.30
     200   1.15    5.38      27.9     88.4      0.45
     300   1.19    8.03      46.2    183.0      0.52

``‖h2‖`` and the head norm grow together and CE follows them; accuracy keeps
climbing, so the cell trains — it is the *scale* that runs away. This informs
TODO88 N7: the channel works, the stream normalization is internal to the
credit, and the head sees unnormalized features.
"""

from __future__ import annotations

import itertools
import time

import torch
import torch.nn.functional as F  # ruff: ignore[lowercase-imported-as-non-lowercase]

from computronium.core.label_channel import label_augmented
from computronium.domains.factory import create_task
from computronium.experiment.kernel.compose import compose_cell_system
from computronium.experiment.schema.coordinate import Coordinate

STEPS = 300
BATCH = 32


def _coordinate(step_size: float) -> Coordinate:
    return Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="instantaneous",
        plasticity="null",
        credit="local_contrastive",
        update="adam",
        params={"update.step_size": step_size},
    )


def _report(system, batches, step: int) -> None:
    x, y = batches[0]
    z = label_augmented(x, y, system.label_dim)
    acts = system.geometry.forward_with_intermediates(z, system.substrate)
    norms = [float(a.detach().pow(2).mean(dim=-1).sqrt().mean()) for a in acts[1:]]
    head = system.geometry.params["4.weight"]
    with torch.no_grad():
        logits = system.forward(x)
    ce = float(F.cross_entropy(logits, y))
    acc = float((logits.argmax(-1) == y).float().mean())
    print(
        f"{step:5d}  "
        + "  ".join(f"{n:6.2f}" for n in norms)
        + f"  {float(head.detach().norm()):8.1f}  {ce:7.2f}  {acc:6.2f}",
        flush=True,
    )


def main() -> int:
    started = time.perf_counter()
    task = create_task("mnist", device="cpu", quick_mode=True)
    task.setup()
    batches = [
        (xb.reshape(xb.size(0), -1), yb)
        for xb, yb in itertools.islice(task.get_dataloader("train"), 40)
    ]
    cell = compose_cell_system(
        coordinate=_coordinate(1e-3),
        geometry={"hidden_dim": 64, "num_layers": 2},
        input_shape=(1, 28, 28),
        output_dim=10,
    )
    system = cell.system
    print("  step   ‖h1‖    ‖h2‖   ‖W_head‖F     CE   val_acc", flush=True)
    _report(system, batches, 0)
    for step, (x, y) in enumerate(itertools.islice(itertools.cycle(batches), STEPS), 1):
        system.train_step(x, y)
        if step % 100 == 0:
            _report(system, batches, step)
    print(f"walltime {time.perf_counter() - started:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
