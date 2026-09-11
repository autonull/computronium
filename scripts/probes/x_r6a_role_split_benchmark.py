"""R6-A benchmark — RoleSplitUpdate (wired component) vs uniform arms.

Confirms the X-USU-001 result on the CONFIG-SURFACE primitive
(``ParameterUpdateConfig.role_split`` → ``RoleSplitUpdate``), not the
probe's inline dispatcher: muon-on-readout + euclid-elsewhere beats
uniform euclid on one-step improvement_per_norm on all 3 seeds
(norm-matched per arm; measurement path mirrors ``x_usu_001.run_arm``
exactly — random_projections credit at feedback_scale=0.1, euclid-based
per-arm lr calibration, readout auto-detected from the geometry).

Measured (2026-09-10, CPU): ipn role_split_muon_out {0.597, 0.568,
0.520} vs uniform_euclid {0.542, 0.521, 0.446} — bit-identical to
x_usu_001's hybrid_muon_out/uniform_euclid arms; walltime ~0.35 s.
Governs B-H5 via X-USU-001 evidence; this probe is the component
wiring regression.

Run:
    uv run python scripts/probes/x_r6a_role_split_benchmark.py
"""

from __future__ import annotations

import time
from pathlib import Path

import torch

REPO_ROOT = Path(__file__).resolve().parents[2]

from computronium.analysis.mechanistic_study import (
    _INPUT_DIM,
    _OUTPUT_DIM,
    _build_system,
    _calibrated_lr,
)
from computronium.analysis.vertical_slice import free_loss
from computronium.ontology.credit import CreditAssignmentConfig
from computronium.ontology.update import ParameterUpdateConfig

N_SEEDS = 3


def _task(seed: int) -> tuple:
    torch.manual_seed(seed + 777)
    return torch.randn(8, _INPUT_DIM), torch.randint(0, _OUTPUT_DIM, (8,))


def _euclid_cfg(lr: float) -> ParameterUpdateConfig:
    return ParameterUpdateConfig.euclidean(step_size=lr, momentum=0.0)


def _role_split_cfg(lr: float, readout: str) -> ParameterUpdateConfig:
    return ParameterUpdateConfig.role_split(
        role_names=(readout,),
        on_role=ParameterUpdateConfig.riemannian_orthogonal(step_size=lr, momentum=0.0),
        other=_euclid_cfg(lr),
    )


def _readout_name(params: dict) -> str:
    for name, p in params.items():
        if p.ndim == 2 and p.shape[0] == _OUTPUT_DIM:
            return name
    raise ValueError(f"no readout weight among {sorted(params)}")


def _displacement(system, xs, ys) -> float:
    before = {n: t.detach().clone() for n, t in system.geometry.params.items()}
    system.train_step(xs, ys)
    return (
        sum(
            float((system.geometry.params[n].detach() - before[n]).norm() ** 2)
            for n in before
        )
        ** 0.5
    )


def _ipn(arm: str, seed: int) -> float:
    credit_cfg = CreditAssignmentConfig.random_projections(feedback_scale=0.1)
    xs, ys = _task(seed)
    ref = _build_system(credit_cfg, _euclid_cfg(0.05), seed=seed)
    readout = _readout_name(ref.geometry.params)
    ref_norm = _displacement(ref, xs, ys)
    # x_usu_001 calibrates hybrid arms with the euclid cfg as well.
    lr = _calibrated_lr(credit_cfg, _euclid_cfg, ref_norm, xs, ys, seed=seed)
    cfg_fn = (
        (lambda lr_: _role_split_cfg(lr_, readout))
        if arm == "role_split_muon_out"
        else _euclid_cfg
    )
    system = _build_system(credit_cfg, cfg_fn(lr), seed=seed)
    before = {n: t.detach().clone() for n, t in system.geometry.params.items()}
    loss_before = free_loss(system, xs, ys)
    system.train_step(xs, ys)
    loss_after = free_loss(system, xs, ys)
    disp = (
        sum(
            float((system.geometry.params[n].detach() - before[n]).norm() ** 2)
            for n in before
        )
        ** 0.5
    )
    return (loss_before - loss_after) / disp if disp > 0 else 0.0


def main() -> int:
    t0 = time.perf_counter()
    arms = ("uniform_euclid", "role_split_muon_out")
    results = {arm: [_ipn(arm, s) for s in range(N_SEEDS)] for arm in arms}
    wins = sum(
        results["role_split_muon_out"][s] > results["uniform_euclid"][s]
        for s in range(N_SEEDS)
    )
    for arm in arms:
        vals = ", ".join(f"{v:.3f}" for v in results[arm])
        print(f"{arm:22s} ipn [{vals}]")
    print(
        f"role_split wins {wins}/{N_SEEDS} seeds; walltime {time.perf_counter() - t0:.2f}s"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
