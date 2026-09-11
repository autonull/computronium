"""Credit × Update mechanistic study (TODO18 5.1).

Two experiments over a C × U grid, held on a fixed coordinate
(DigitalSubstrate + RecurrentGeometry + EnergyMinimizationDynamics):

- **One-Step Reset-State**: fresh θ + fresh optimizer state per run,
  one C × U step, measure ‖Δθ‖ and L(θ+Δθ) − L(θ). This isolates the
  *immediate transformation quality* of the (C, U) pair — no trajectory
  effects, no state carryover.
- **Trajectory-Trained**: full training runs with matched first-step
  update norms and equal tuning budgets (same step count). This measures
  the *deployed mechanism performance*.

The two are reported separately and never conflated: a cell may lower
L in one step yet lose over a trajectory, and vice versa.

All metrics are Level 4 (sampled numerical) / Level 5 (empirical).
Positive `loss_delta` means L rose (worse); negative means descent.
`improvement_per_norm` = −ΔL / ‖Δθ‖ (descent quality per unit
displacement). Step sizes are calibrated so each cell's first-step mean
‖Δθ‖ matches the euclidean reference cell — norm is controlled, so
ΔL differences reflect the credit/update rule, not raw step magnitude.

PEPITA is excluded from the grid: it is memory-backprop-class and
requires InstantaneousDynamics + FeedforwardGeometry (different S/G/D);
running it under the settle-based coordinate would measure a broken
composition, not the mechanism.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import torch
from local_feedback.metrics import improvement_per_norm

from computronium.analysis.vertical_slice import (
    ClaimRecord,
    SliceMetrics,
    free_loss,
    git_commit_hash,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from computronium.ontology.credit import CreditAssignmentConfig
    from computronium.ontology.system import System
    from computronium.ontology.update import ParameterUpdateConfig

__all__ = [
    "MechanisticStudyRecord",
    "run_mechanistic_study",
    "run_one_step_reset",
    "run_trajectory",
]

STUDY_COORDINATE = "digital/recurrent/energy_min/<credit>/<none>/<update>"

_INPUT_DIM = 16
_HIDDEN_DIM = 24
_OUTPUT_DIM = 4
_BATCH_SIZE = 16


def _credit_configs() -> dict[str, Callable[[], CreditAssignmentConfig]]:
    from computronium.ontology.credit import CreditAssignmentConfig

    return {
        "eqprop": lambda: CreditAssignmentConfig.thermodynamic_contrast(beta=0.5),
        "fa": lambda: CreditAssignmentConfig.random_projections(feedback_scale=0.05),
        "lemma": lambda: CreditAssignmentConfig.local_goodness(
            local_objective="lemma",
            readout_error=True,
            credit_norm="rms",
        ),
        "bp": lambda: CreditAssignmentConfig.gradient(train_biases=False),
    }


def _update_configs() -> dict[str, Callable[[float], ParameterUpdateConfig]]:
    from computronium.ontology.update import ParameterUpdateConfig

    return {
        "euclidean": lambda lr: ParameterUpdateConfig.euclidean(
            step_size=lr, momentum=0.0
        ),
        "adam": lambda lr: ParameterUpdateConfig.adam(step_size=lr, momentum=0.0),
        "muon": lambda lr: ParameterUpdateConfig.riemannian_orthogonal(
            step_size=lr, momentum=0.0
        ),
    }


def _build_system(
    credit_cfg: CreditAssignmentConfig,
    update_cfg: ParameterUpdateConfig,
    *,
    seed: int,
    settle_steps: int = 10,
) -> System:
    """Build one study cell: fixed S/G/D, cell-specific C and U."""
    from computronium.core.system_trainer.factory import compose_system_from_configs
    from computronium.ontology.dynamics import StateDynamicsConfig
    from computronium.ontology.geometry import GeometryConfig
    from computronium.ontology.substrate import SubstrateConfig

    torch.manual_seed(seed)
    return compose_system_from_configs(
        substrate=SubstrateConfig(
            precision="float32",
            noise_level=0.0,
            weight_bounds=None,
            sparsity=0.0,
            device="cpu",
        ),
        geometry=GeometryConfig.recurrent(
            input_dim=_INPUT_DIM,
            output_dim=_OUTPUT_DIM,
            hidden_dims=(_HIDDEN_DIM,),
            init_scale=0.1,
        ),
        dynamics=StateDynamicsConfig.energy_minimization(
            max_steps=settle_steps,
            convergence_threshold=1e-4,
            convergence_start=5,
            step_size=0.1,
            beta=0.5,
            track_free_energy_per_iter=False,
        ),
        credit=credit_cfg,
        update=update_cfg,
    )


def _displacement_norm(system: System, x: torch.Tensor, y: torch.Tensor) -> float:
    """One train step's total ‖Δθ‖ (L2 across all parameters)."""
    before = {n: t.detach().clone() for n, t in system.geometry.params.items()}
    system.train_step(x, y)
    sq = 0.0
    for n, t in system.geometry.params.items():
        d = t.detach() - before[n]
        sq += float(d.norm() ** 2)
    return sq**0.5


def _calibrated_lr(
    credit_cfg: CreditAssignmentConfig,
    update_cfg_fn: Callable[[float], ParameterUpdateConfig],
    reference_norm: float,
    xs: torch.Tensor,
    ys: torch.Tensor,
    *,
    seed: int,
    probe_lr: float = 0.01,
) -> float:
    """Rescale step_size so the first-step ‖Δθ‖ ≈ reference_norm.

    First-step displacement is proportional to step_size for both step
    semantics (momentum 0, one step), so a single proportional rescale
    suffices. Dead cells (zero displacement at any lr) return 0.0 and
    are reported as inert rather than silently mis-calibrated.
    """
    system = _build_system(credit_cfg, update_cfg_fn(probe_lr), seed=seed)
    norm = _displacement_norm(system, xs, ys)
    if norm <= 0.0 or reference_norm <= 0.0:
        return 0.0
    return probe_lr * reference_norm / norm


def run_one_step_reset(
    system: System,
    x: torch.Tensor,
    y: torch.Tensor,
) -> dict[str, float]:
    """One C × U step from a reset (fresh-θ) state: Δθ and ΔL.

    Assumes ``system`` was just constructed (fresh optimizer state);
    θ is snapshotted, one ``train_step`` applied, and L measured
    before/after via the coordinate's own free loss.
    """
    before = {n: t.detach().clone() for n, t in system.geometry.params.items()}
    loss_before = free_loss(system, x, y)
    system.train_step(x, y)
    loss_after = free_loss(system, x, y)
    sq = 0.0
    for n, t in system.geometry.params.items():
        d = t.detach() - before[n]
        sq += float(d.norm() ** 2)
    disp = sq**0.5
    loss_delta = loss_after - loss_before
    return {
        "loss_before": loss_before,
        "loss_delta": loss_delta,
        "displacement_norm": disp,
        "improvement_per_norm": improvement_per_norm(loss_before, loss_after, disp),
    }


def run_trajectory(
    system: System,
    x: torch.Tensor,
    y: torch.Tensor,
    n_steps: int,
) -> dict[str, float]:
    """Train one cell for ``n_steps`` and summarize deployment behavior.

    Returns final/mean/best free loss, mean per-step ‖Δθ‖, and the
    tuning budget (steps × params) for budget-matched comparison.
    """
    param_count = sum(t.numel() for t in system.geometry.params.values())
    losses: list[float] = []
    norms: list[float] = []
    for _ in range(n_steps):
        pre = {n: t.detach().clone() for n, t in system.geometry.params.items()}
        losses.append(free_loss(system, x, y))
        sq = 0.0
        system.train_step(x, y)
        for n, t in system.geometry.params.items():
            d = t.detach() - pre[n]
            sq += float(d.norm() ** 2)
        norms.append(sq**0.5)
    return {
        "loss_initial": losses[0],
        "loss_final": losses[-1],
        "loss_mean": sum(losses) / len(losses),
        "loss_best": min(losses),
        "displacement_norm_mean": sum(norms) / len(norms),
        "tuning_budget_params_steps": float(n_steps * param_count),
    }


@dataclass(frozen=True, slots=True)
class MechanisticStudyRecord:
    """Claim artifact for the C × U mechanistic study (TODO18 5.1).

    Attributes:
        coordinate: Study coordinate template.
        config: Study configuration (dims, steps, seeds, calibration).
        cells: cell name -> {experiment -> ClaimRecord}; each ClaimRecord
            aggregates mean ± std (n) over seeds.
        verification_level: Strongest level the recorded claims meet.
        commit_hash: Commit the measurement was taken at.
        walltime_s: Total measurement walltime.
        schema_version: Record schema version.
    """

    coordinate: str
    config: dict[str, object]
    cells: dict[str, dict[str, ClaimRecord]] = field(default_factory=dict)
    verification_level: str = "4"
    commit_hash: str = ""
    walltime_s: float = 0.0
    schema_version: str = "1.0.0"

    def to_json(self) -> str:
        """Serialize the full study record."""
        return json.dumps(
            {
                "schema_version": self.schema_version,
                "coordinate": self.coordinate,
                "config": self.config,
                "cells": {
                    cell: {exp: rec.to_json() for exp, rec in exps.items()}
                    for cell, exps in self.cells.items()
                },
                "verification_level": self.verification_level,
                "commit_hash": self.commit_hash,
                "walltime_s": self.walltime_s,
            },
            sort_keys=True,
            indent=2,
        )

    @classmethod
    def from_json(cls, raw: str) -> MechanisticStudyRecord:
        """Rehydrate from its JSON artifact."""
        data = json.loads(raw)
        return cls(
            coordinate=data["coordinate"],
            config=data["config"],
            cells={
                cell: {exp: ClaimRecord.from_json(rec) for exp, rec in exps.items()}
                for cell, exps in data["cells"].items()
            },
            verification_level=data["verification_level"],
            commit_hash=data["commit_hash"],
            walltime_s=data["walltime_s"],
        )


def run_mechanistic_study(
    seeds: tuple[int, ...] = (0, 1, 2),
    n_traj_steps: int = 30,
) -> MechanisticStudyRecord:
    """Run the full C × U study: one-step reset-state + trajectory arms.

    Norm matching: each cell's step size is calibrated on seed 0's batch
    so its first-step mean ‖Δθ‖ matches the euclidean reference cell.
    Dead cells (zero first-step displacement) skip calibration and are
    reported with zero norms — an inert channel is a finding, not an
    error.
    """
    credits = _credit_configs()
    updates = _update_configs()
    start = time.perf_counter()

    torch.manual_seed(0)
    xs = torch.randn(_BATCH_SIZE, _INPUT_DIM)
    ys = torch.randint(0, _OUTPUT_DIM, (_BATCH_SIZE,))

    cells: dict[str, dict[str, ClaimRecord]] = {}
    config: dict[str, object] = {
        "input_dim": _INPUT_DIM,
        "hidden_dim": _HIDDEN_DIM,
        "output_dim": _OUTPUT_DIM,
        "batch_size": _BATCH_SIZE,
        "n_traj_steps": n_traj_steps,
        "seeds": list(seeds),
        "task": "synthetic_iid_classification",
        "norm_reference_update": "euclidean",
    }

    reference_lr = 0.05
    for credit_name, credit_fn in credits.items():
        for update_name, update_fn in updates.items():
            cell = f"{credit_name}x{update_name}"
            lr = reference_lr
            if update_name != "euclidean":
                lr = _calibrated_lr(
                    credit_fn(),
                    update_fn,
                    _reference_norm(credit_fn(), reference_lr, xs, ys),
                    xs,
                    ys,
                    seed=seeds[0],
                )
            one_step_runs: list[SliceMetrics] = []
            traj_runs: list[SliceMetrics] = []
            for seed in seeds:
                system = _build_system(credit_fn(), update_fn(lr), seed=seed)
                reset = run_one_step_reset(system, xs, ys)
                traj = run_trajectory(system, xs, ys, n_traj_steps)
                one_step_runs.append(
                    SliceMetrics(seed=seed, steps=[reset], config={"cell": cell})
                )
                traj_runs.append(
                    SliceMetrics(seed=seed, steps=[traj], config={"cell": cell})
                )
            cells[cell] = {
                "one_step_reset": ClaimRecord.from_runs(
                    f"{STUDY_COORDINATE}#{cell}",
                    {"arm": "one_step_reset", "lr": lr},
                    one_step_runs,
                ),
                "trajectory": ClaimRecord.from_runs(
                    f"{STUDY_COORDINATE}#{cell}",
                    {"arm": "trajectory", "lr": lr, "n_steps": n_traj_steps},
                    traj_runs,
                ),
            }

    return MechanisticStudyRecord(
        coordinate=STUDY_COORDINATE,
        config=config,
        cells=cells,
        commit_hash=git_commit_hash(),
        walltime_s=time.perf_counter() - start,
    )


def _reference_norm(
    credit_cfg: CreditAssignmentConfig,
    lr: float,
    xs: torch.Tensor,
    ys: torch.Tensor,
) -> float:
    """First-step ‖Δθ‖ of the euclidean reference cell at ``lr``."""
    system = _build_system(credit_cfg, _update_configs()["euclidean"](lr), seed=0)
    return _displacement_norm(system, xs, ys)


def save_study_record(record: MechanisticStudyRecord, path: Path) -> None:
    """Persist the study record to ``path`` (parents created)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(record.to_json(), encoding="utf-8")
