"""Sequence-ψ statistics A/B campaign (TODO23 §12, the last #3 slice).

Variant A (default): ψ steps ONCE per episode on the final timestep.
Variant B (psi_step="every_timestep"): ψ steps at every sequence step —
the primitive's own decayed sufficient statistics carry across the
recurrence, so the ridge readout is fit on the full sequence trace
instead of the final step. Equal compute (same episodes); B takes T×
more ψ steps (ridge update O(d²), negligible vs the pipeline pass).

Trained ntm_sequence (last_symbol), 3 seeds × 20 episodes on the task's
own stream; both variants must keep θ bitwise frozen.

uv run python scripts/probes/sequence_psi_stats_ab.py
Walltime printed, never recorded.
"""

from __future__ import annotations

import time

import torch
from computronium_lab.adaptation import adapt, theta_digest
from computronium_lab.recipes import build_ntm_sequence
from computronium_lab.sequential import sequence_task, train_sequence

for seed in (0, 1, 2):
    for psi_step in ("final", "every_timestep"):
        t0 = time.perf_counter()
        torch.manual_seed(seed)
        system = build_ntm_sequence()
        train_sequence(system, "last_symbol", epochs=120, lr=0.1, seed=seed)
        sha_before = theta_digest(system)

        def stream(seed: int = seed):
            for i in range(4):
                x, y = sequence_task("last_symbol", seed=seed * 100 + i)
                yield x, y

        result = adapt(system, stream(), "temporal", episodes=20, psi_step=psi_step)
        print(
            f"seed={seed} {psi_step:14s} "
            f"psi_acc={result.metrics['psi_accuracy']:.3f} "
            f"free_acc={result.metrics['free_accuracy']:.3f} "
            f"theta_ok={result.theta.bitwise_invariant} "
            f"({time.perf_counter() - t0:.1f}s)"
        )
