"""Family depth grid — FF and EqProp under the harvest instrument
(TODO15 §13.7 breadth extension: "do not forget FF and EqProp").

Both families predate the depth×task grid (§14) and its two instruments
(best-snapshot harvest, EMA weights); this cell puts them under the
SAME protocol as the ePC grid, so the depth-frontier law gets a
three-family test. One instrument, three families.

Arms (MNIST, 150 batches, width 128, μPC init, residual, seed 0,
best-snapshot + EMA probes every 10 batches):
  - ff d32 / ff d50   — LocalContrastiveCredit (the W2 flagship recipe
                        of record: ema_beta 0.99, lr 0.3, sequential_lr
                        0.3, ro_scale 1/3, Euclidean; label-augmented
                        input, label_dim=10)
  - eqprop d20 / d32  — EnergyMinimizationDynamics (max_steps 30, β 0.5)
                        + ThermodynamicContrast + Euclidean 0.1 (the
                        classic pairing; β credit-matched to dynamics)

Pre-registered reading: a family whose depth curve peaks-then-memorizes
like ePC's extends the §14 law to three families; a family that degrades
monotonically with depth (no peak) carries a DIFFERENT depth mechanism —
the distinction is the datum, not either outcome alone.

uv run python scripts/probes/w9_family_depth_grid.py          # the 6-arm grid
uv run python scripts/probes/w9_family_depth_grid.py --family=ff --depth=8 --lr=0.5 --raw
Walltime printed, never recorded.
"""

from __future__ import annotations

import copy
import sys
import time
from itertools import islice
from typing import TYPE_CHECKING

import torch
from torch import Tensor, nn

if TYPE_CHECKING:
    from computronium.ontology import StateDynamics

sys.path.insert(0, "scripts/probes")

from computronium import (
    CreditAssignmentConfig,
    DigitalSubstrate,
    EnergyMinimizationDynamics,
    EuclideanUpdate,
    FeedforwardGeometry,
    GeometryConfig,
    InstantaneousDynamics,
    LocalContrastiveCredit,
    ParameterUpdateConfig,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemState,
    ThermodynamicContrast,
    create_task,
)
from computronium.core.pipeline import run_train_step

BATCHES = 150
PROBE_EVERY = 10
WIDTH = 128
LABEL_DIM = 10


def _data(task_name: str):
    task = create_task(task_name, device="cpu", quick_mode=True, num_workers=0)
    task.setup()
    torch.manual_seed(0)
    train = [
        (x.view(x.size(0), -1), y)
        for x, y in islice(task.get_dataloader("train"), BATCHES)
    ]
    test = [(x.view(x.size(0), -1), y) for x, y in task.get_dataloader("test")][:20]
    return train, test


def _geometry(depth: int, in_dim: int, family: str) -> FeedforwardGeometry:
    """Per-family constructors of record, copied verbatim:
    - FF (w2_library_parity): manual nn.Linear default-init stack.
    - EqProp (energy_minimization contract): config default init_scale
      0.1 — the EqProp small-init convention; scale 1.0 collapses it.
    Shared: no residual, no μPC — those are ePC-grid geometry choices;
    applying them here collapsed both families (ff d4 0.402 vs 0.757
    recorded; eqprop d2 chance)."""
    if family == "ff":
        layers: list[nn.Module] = [nn.Linear(in_dim, WIDTH), nn.ReLU()]
        for _ in range(depth - 2):
            layers += [nn.Linear(WIDTH, WIDTH), nn.ReLU()]
        layers.append(nn.Linear(WIDTH, 10))
        geo = FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=in_dim, hidden_dims=(WIDTH,) * (depth - 1), output_dim=10
            ),
            layers=layers,
        )
        geo._set_param_names()
        return geo
    return FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=in_dim, hidden_dims=(WIDTH,) * (depth - 1), output_dim=10
        )
    )


def _ff_augment(x: Tensor, y: Tensor, good: bool) -> Tensor:
    onehot = torch.nn.functional.one_hot(y, LABEL_DIM).float()
    if not good:
        onehot = onehot.roll(1, 0)
    return torch.cat([x, onehot], dim=-1)


def _run(  # ruff: ignore[complex-structure]
    family: str, depth: int, train, test, lr: float | None = None, raw: bool = False
) -> dict[str, float]:
    torch.manual_seed(0)
    substrate = DigitalSubstrate(SubstrateConfig.digital(device="cpu"))
    if family == "ff":
        geometry = _geometry(depth, 784 + LABEL_DIM, family)
        credit = LocalContrastiveCredit(
            CreditAssignmentConfig.local_contrastive(
                label_dim=LABEL_DIM,
                ema_beta=0.99,
                sequential_lr=0.3,
                readout_scale=1 / 3,
            )
        )
        update = EuclideanUpdate(
            ParameterUpdateConfig.euclidean(step_size=lr or 0.3, grad_clip=0.0)
        )
        dynamics: StateDynamics = InstantaneousDynamics()

        def evaluate() -> float:
            ok = tot = 0
            with torch.no_grad():
                for x, y in test:
                    logits = geometry(_ff_augment(x, y, True), substrate)
                    ok += (logits.argmax(1) == y).sum().item()
                    tot += y.size(0)
            return ok / tot

    else:
        geometry = _geometry(depth, 784, family)
        credit = ThermodynamicContrast(
            CreditAssignmentConfig.thermodynamic_contrast(beta=0.5)
        )
        update = EuclideanUpdate(
            ParameterUpdateConfig.euclidean(step_size=lr or 0.1, grad_clip=0.0)
        )
        dynamics = EnergyMinimizationDynamics(
            StateDynamicsConfig.energy_minimization(max_steps=30, beta=0.5)
        )

        def evaluate() -> float:
            ok = tot = 0
            with torch.no_grad():
                for x, y in test:
                    state = dynamics.settle(SystemState(x=x), geometry, substrate, None)
                    acts = state.activations
                    out = acts[-1] if isinstance(acts, list) else acts
                    ok += (out.argmax(1) == y).sum().item()
                    tot += y.size(0)
            return ok / tot

    weights = list(geometry.parameters())
    ema = [w.detach().clone() for w in weights]
    best_val, best_params, best_step = 0.0, None, 0
    for step, (x, y) in enumerate(train):
        xin = _ff_augment(x, y, True) if family == "ff" else x
        run_train_step(substrate, geometry, dynamics, credit, update, xin, y)
        if raw:
            continue
        with torch.no_grad():
            for w, e in zip(weights, ema, strict=True):
                e.mul_(0.99).add_(w.detach(), alpha=0.01)
        if step % PROBE_EVERY == 0 or step == len(train) - 1:
            val = evaluate()
            if val > best_val:
                best_val, best_params, best_step = (
                    val,
                    copy.deepcopy(weights),
                    step,
                )
    if raw:
        return {
            "best": evaluate(),
            "best_step": len(train),
            "restored": 0.0,
            "ema": 0.0,
        }
    if best_params is not None:
        with torch.no_grad():
            for w, p in zip(weights, best_params, strict=True):
                w.copy_(p)
    best_restored = evaluate()
    with torch.no_grad():
        for w, e in zip(weights, ema, strict=True):
            w.copy_(e)
    ema_final = evaluate()
    return {
        "best": best_val,
        "best_step": best_step,
        "restored": best_restored,
        "ema": ema_final,
    }


def main() -> int:
    t0 = time.time()
    args = sys.argv[1:]
    opt = dict(a[2:].split("=") for a in args if a.startswith("--") and "=" in a)
    flags = {a.lstrip("-") for a in args}
    raw = "raw" in flags
    if opt:
        family = opt.get("family", "ff")
        depth = int(opt.get("depth", 8))
        lr = float(opt["lr"]) if "lr" in opt else None
        train, test = _data(opt.get("task", "mnist"))
        r = _run(family, depth, train, test, lr=lr, raw=raw)
        print(
            f"{family:>6} d{depth:>3}{(' raw' if raw else '')}: best {r['best']:.3f} "
            f"@ {r['best_step']:>3}  restored {r['restored']:.3f}  EMA {r['ema']:.3f}",
            flush=True,
        )
        print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
        return 0
    train, test = _data("mnist")
    for family, depth in (
        ("ff", 2),
        ("ff", 4),
        ("ff", 32),
        ("eqprop", 2),
        ("eqprop", 4),
        ("eqprop", 32),
    ):
        r = _run(family, depth, train, test)
        print(
            f"{family:>6} d{depth:>3}: best {r['best']:.3f} @ {r['best_step']:>3}  "
            f"restored {r['restored']:.3f}  EMA {r['ema']:.3f}",
            flush=True,
        )
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
