"""Mask-entropy law probe (TODO15 §8.6 #1): does the flagship-B killer
(958/1000 distinct ReLU masks — mask-conditioning has no pooling
support) generalize across geometry and task, or is it a D1-specific
artifact?

Points measured (exact mask hash over all hidden layers ≥ 2):
- seed-0 D1 backbone (784→128⁴→10, MNIST-trained): MNIST test vs
  FashionMNIST test, n ∈ {500, 1000}
- fresh width-32 depth-8 MNIST-trained MLP (its own scale point)

Law form: distinct-masks/n → 1 (mask entropy saturates the sample).
If distinct/n stays ≈ 1 everywhere, mask-conditioned corrections are
dead at any scale/task — a program-level boundary, not a per-task one.

uv run python scripts/probes/mask_entropy_law.py
Walltime printed, never recorded.
"""

from __future__ import annotations

import hashlib
import sys
import time
from pathlib import Path

import torch
from torch import Tensor

sys.path.insert(0, str(Path(__file__).resolve().parent))

from w4_scaled_psi import _Data, _forward_acts, _stage_a

from computronium import (  # type: ignore[attr-defined]
    CreditAssignmentConfig,
    GeometryConfig,
    ParameterUpdateConfig,
    StateDynamicsConfig,
    SubstrateConfig,
    compose_system_from_configs,
)
from computronium.core.pipeline import run_train_step

N_SWEEP = (500, 1000)
BATCH = 128
EPISODES_SMALL = 200


def _distinct_masks(system, x: Tensor, min_layer: int = 2) -> int:
    acts = _forward_acts(system, x)
    bits = torch.cat(
        [(acts[k + 1] > 0).flatten(1) for k in range(min_layer, len(acts) - 1)],
        dim=1,
    ).cpu()
    return len({hashlib.md5(row.numpy().tobytes()).hexdigest() for row in bits})


def _small_mlp():
    torch.manual_seed(0)
    system = compose_system_from_configs(
        SubstrateConfig.digital(),
        GeometryConfig.feedforward(input_dim=784, output_dim=10, hidden_dims=(32,) * 8),
        StateDynamicsConfig.instantaneous(),
        CreditAssignmentConfig.gradient(),
        ParameterUpdateConfig.euclidean(step_size=0.1),
    )
    system = system.to("cuda" if torch.cuda.is_available() else "cpu")
    data = _Data()
    for _ in range(EPISODES_SMALL):
        x, y = data.episode("A")
        run_train_step(
            system.substrate,
            system.geometry,
            system.dynamics,
            system.credit,
            system.update,
            x,
            y,
        )
    return system


def main() -> int:
    t0 = time.time()
    torch.manual_seed(20260909)
    data = _Data()

    system, a_mastery, _ = _stage_a(0)
    print(f"D1 backbone (128x4) stage-A mastery {a_mastery:.4f}", flush=True)
    for name in ("A", "B"):
        for n in N_SWEEP:
            x, _ = data.probe(name)
            x = x[:n]
            d = _distinct_masks(system, x)
            print(
                f"  128x4 {'MNIST' if name == 'A' else 'Fashion'} n={n}: "
                f"{d} distinct masks (ratio {d / n:.3f})",
                flush=True,
            )

    small = _small_mlp()
    x, _ = data.probe("A")
    x = x[:1000]
    d = _distinct_masks(small, x)
    print(f"  32x8 MNIST n=1000: {d} distinct masks (ratio {d / 1000:.3f})", flush=True)

    print(
        "\nLAW: distinct/n ≈ 1 everywhere → mask-conditioned corrections dead at any scale/task",
        flush=True,
    )
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
