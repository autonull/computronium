"""Quick overturn probes: FF/EqProp × {ortho_adam, μPC+residual} under harvest.

Tests 4 high-value combos that could overturn "FF/EqProp don't scale":
1. FF + ortho_adam (d32, d50)
2. FF + μPC init + residual (d32)
3. EqProp + ortho_adam (d20, d32)
4. EqProp + μPC init + residual + max_steps (d20)

All: MNIST, 150 batches, width 128, probe-free EMA + best-snapshot harvest,
seed 0, width 128.

uv run python scripts/probes/w9_overturn_probes.py
Walltime printed, never recorded.
"""

from __future__ import annotations

import copy
import time
from itertools import islice

import torch
from torch import nn


from computronium import (
    CreditAssignmentConfig,
    DigitalSubstrate,
    EnergyMinimizationDynamics,
    FeedforwardGeometry,
    GeometryConfig,
    InstantaneousDynamics,
    LocalContrastiveCredit,
    OrthoAdamUpdate,
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


def _data():
    task = create_task("mnist", device="cpu", quick_mode=True, num_workers=0)
    task.setup()
    torch.manual_seed(0)
    train = [
        (x.view(x.size(0), -1), y)
        for x, y in islice(task.get_dataloader("train"), BATCHES)
    ]
    test = [(x.view(x.size(0), -1), y) for x, y in task.get_dataloader("test")][:20]
    return train, test


def _ff_augment(x: torch.Tensor, y: torch.Tensor, good: bool) -> torch.Tensor:
    onehot = torch.nn.functional.one_hot(y, LABEL_DIM).float()
    if not good:
        onehot = onehot.roll(1, 0)
    return torch.cat([x, onehot], dim=-1)


def _geometry_ff(depth: int) -> FeedforwardGeometry:
    layers: list[nn.Module] = [nn.Linear(784 + LABEL_DIM, WIDTH), nn.ReLU()]
    for _ in range(depth - 2):
        layers += [nn.Linear(WIDTH, WIDTH), nn.ReLU()]
    layers.append(nn.Linear(WIDTH, 10))
    geo = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=784 + LABEL_DIM,
            hidden_dims=(WIDTH,) * (depth - 1),
            output_dim=10,
        ),
        layers=layers,
    )
    geo._set_param_names()
    return geo


def _geometry_eqprop_mupc(depth: int) -> FeedforwardGeometry:
    return FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=784,
            output_dim=10,
            hidden_dims=(WIDTH,) * (depth - 1),
            init_scheme="mupc",
            residual=True,
        )
    )


def _geometry_plain(depth: int, in_dim: int) -> FeedforwardGeometry:
    return FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=in_dim,
            output_dim=10,
            hidden_dims=(WIDTH,) * (depth - 1),
        )
    )


def _eval_ff(geometry, substrate, test):
    ok = tot = 0
    with torch.no_grad():
        for x, y in test:
            logits = geometry(_ff_augment(x, y, True), substrate)
            ok += (logits.argmax(1) == y).sum().item()
            tot += y.size(0)
    return ok / tot


def _eval_settle(dynamics, geometry, substrate, test):
    ok = tot = 0
    with torch.no_grad():
        for x, y in test:
            state = dynamics.settle(SystemState(x=x), geometry, substrate, None)
            acts = state.activations
            out = acts[-1] if isinstance(acts, list) else acts
            ok += (out.argmax(1) == y).sum().item()
            tot += y.size(0)
    return ok / tot


def _run_cell(
    name: str,
    geometry,
    credit,
    update,
    dynamics,
    eval_fn,
    train,
    test,
    input_transform=None,
) -> dict:
    torch.manual_seed(0)
    substrate = DigitalSubstrate(SubstrateConfig.digital(device="cpu"))
    weights = list(geometry.parameters())
    ema = [w.detach().clone() for w in weights]
    best_val, best_params, best_step = 0.0, None, 0
    for step, (x, y) in enumerate(train):
        xin = input_transform(x, y) if input_transform else x
        run_train_step(substrate, geometry, dynamics, credit, update, xin, y)
        with torch.no_grad():
            for w, e in zip(weights, ema, strict=True):
                e.mul_(0.99).add_(w.detach(), alpha=0.01)
        if step % PROBE_EVERY == 0 or step == len(train) - 1:
            val = eval_fn()
            if val > best_val:
                best_val, best_params, best_step = (
                    val,
                    copy.deepcopy(weights),
                    step,
                )
    if best_params is not None:
        with torch.no_grad():
            for w, p in zip(weights, best_params, strict=True):
                w.copy_(p)
    best_restored = eval_fn()
    with torch.no_grad():
        for w, e in zip(weights, ema, strict=True):
            w.copy_(e)
    ema_final = eval_fn()
    return {
        "name": name,
        "best": best_val,
        "best_step": best_step,
        "restored": best_restored,
        "ema": ema_final,
    }


def main() -> int:
    t0 = time.time()
    train, test = _data()
    substrate = DigitalSubstrate(SubstrateConfig.digital(device="cpu"))

    print("=" * 60)
    print("OVERTURN PROBES: FF/EqProp × {ortho_adam, μPC+residual}")
    print("=" * 60)

    # Cell 1: FF + ortho_adam (d32, d50)
    for depth in (32, 50):
        geo = _geometry_ff(depth)
        credit = LocalContrastiveCredit(
            CreditAssignmentConfig.local_contrastive(
                label_dim=LABEL_DIM,
                ema_beta=0.99,
                sequential_lr=0.3,
                readout_scale=1 / 3,
            )
        )
        update = OrthoAdamUpdate(
            ParameterUpdateConfig.ortho_adam(step_size=1e-3, momentum=0.9)
        )
        dynamics = InstantaneousDynamics()

        def eval_fn(geo=geo, sub=substrate):
            return _eval_ff(geo, sub, test)

        def inp_trans(x, y):
            return _ff_augment(x, y, True)

        r = _run_cell(
            f"ff_ortho_d{depth}",
            geo,
            credit,
            update,
            dynamics,
            eval_fn,
            train,
            test,
            inp_trans,
        )
        print(
            f"ff_ortho_d{depth}: best {r['best']:.3f} @ {r['best_step']}  "
            f"restored {r['restored']:.3f}  EMA {r['ema']:.3f}"
        )

    # Cell 2: FF + μPC init + residual (d32)
    def _geometry_ff_mupc(depth: int) -> FeedforwardGeometry:
        return FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=784 + LABEL_DIM,
                output_dim=10,
                hidden_dims=(WIDTH,) * (depth - 1),
                init_scheme="mupc",
                residual=True,
            )
        )

    geo = _geometry_ff_mupc(32)
    credit = LocalContrastiveCredit(
        CreditAssignmentConfig.local_contrastive(
            label_dim=LABEL_DIM, ema_beta=0.99, sequential_lr=0.3, readout_scale=1 / 3
        )
    )
    update = OrthoAdamUpdate(
        ParameterUpdateConfig.ortho_adam(step_size=1e-3, momentum=0.9)
    )
    dynamics = InstantaneousDynamics()

    def eval_fn(geo=geo, sub=substrate):
        return _eval_ff(geo, sub, test)

    def inp_trans(x, y):
        return _ff_augment(x, y, True)

    r = _run_cell(
        "ff_mupc_d32", geo, credit, update, dynamics, eval_fn, train, test, inp_trans
    )
    print(
        f"ff_mupc_d32: best {r['best']:.3f} @ {r['best_step']}  "
        f"restored {r['restored']:.3f}  EMA {r['ema']:.3f}"
    )

    # Cell 3: EqProp + ortho_adam (d20, d32)
    for depth in (20, 32):
        geo = _geometry_plain(depth, 784)
        credit = ThermodynamicContrast(
            CreditAssignmentConfig.thermodynamic_contrast(beta=0.5)
        )
        update = OrthoAdamUpdate(
            ParameterUpdateConfig.ortho_adam(step_size=1e-3, momentum=0.9)
        )
        dynamics = EnergyMinimizationDynamics(
            StateDynamicsConfig.energy_minimization(max_steps=30, beta=0.5)
        )

        def eval_fn(geo=geo, dyn=dynamics, sub=substrate):
            return _eval_settle(dyn, geo, sub, test)

        r = _run_cell(
            f"eqprop_ortho_d{depth}",
            geo,
            credit,
            update,
            dynamics,
            eval_fn,
            train,
            test,
            None,
        )
        print(
            f"eqprop_ortho_d{depth}: best {r['best']:.3f} @ {r['best_step']}  "
            f"restored {r['restored']:.3f}  EMA {r['ema']:.3f}"
        )

    # Cell 4: EqProp + μPC init + residual + max_steps (d20)
    geo = _geometry_eqprop_mupc(20)
    credit = ThermodynamicContrast(
        CreditAssignmentConfig.thermodynamic_contrast(beta=0.5)
    )
    update = OrthoAdamUpdate(
        ParameterUpdateConfig.ortho_adam(step_size=1e-3, momentum=0.9)
    )
    dynamics = EnergyMinimizationDynamics(
        StateDynamicsConfig.energy_minimization(
            max_steps=100, beta=0.5, convergence_threshold=0.0
        )
    )

    def eval_fn(geo=geo, dyn=dynamics, sub=substrate):
        return _eval_settle(dyn, geo, sub, test)

    r = _run_cell(
        "eqprop_mupc_d20", geo, credit, update, dynamics, eval_fn, train, test, None
    )
    print(
        f"eqprop_mupc_d20: best {r['best']:.3f} @ {r['best_step']}  "
        f"restored {r['restored']:.3f}  EMA {r['ema']:.3f}"
    )

    print(f"\nTotal walltime {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
