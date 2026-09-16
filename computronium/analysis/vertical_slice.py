"""Vertical-slice measurement panel (TODO18 3.2) + claim records (3.3).

Auditable measurement pipeline for a single, well-understood coordinate
(EqProp + RecurrentGeometry + DigitalSubstrate + ThermodynamicContrast +
EuclideanUpdate). Every metric states its verification level — Level 4
sampled numerical / Level 5 empirical. Nothing here is a proof.

Metrics:
- Energy trajectory: free energy per training step, summarized by a
  non-increasing fraction (empirical; consistent-with-descent, not proof).
- Gradient alignment, strict sign convention: Δθ = θ_after − θ_before;
  directional derivative ∇L·Δθ estimated by central finite differences of
  the coordinate's own free loss along Δθ.
- Resource accounting: FLOPs and parameter count per train step.

``ClaimRecord`` (3.3) aggregates per-seed runs into mean ± std metrics
with the commit hash; ``to_json`` emits the CI-gated baseline artifact.
"""

from __future__ import annotations

import hashlib
import json
import subprocess  # ruff: ignore[suspicious-subprocess-import] - reads the repo's own commit hash
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from itertools import pairwise
from typing import TYPE_CHECKING

import torch
from torch import Tensor

from computronium.core.pipeline import SystemState, forward_pass, task_loss
from computronium.core.profiling import estimate_train_step_flops

if TYPE_CHECKING:
    from computronium.ontology.system import System

__all__ = [
    "SCHEMA_VERSION",
    "BatchProvider",
    "ClaimRecord",
    "SliceMetrics",
    "fixed_dataset_batch_provider",
    "free_loss",
    "measure_energy_trajectory",
    "measure_gradient_alignment",
    "measure_resources",
    "run_slice",
    "synthetic_batch_provider",
]

SCHEMA_VERSION = "1.0.0"
_FD_EPS = 1e-3


def free_loss(
    system: System,
    x: Tensor,
    y: Tensor,
) -> float:
    """Target-free loss at the coordinate's current θ (post-settle)."""
    with torch.no_grad():
        state = SystemState(x=x, y=y)
        state.activations = forward_pass(system.substrate, system.geometry, x)
        settled = system.dynamics.settle(state, system.geometry, system.substrate)
        return float(task_loss(settled, y))


def measure_energy_trajectory(steps: list[dict[str, float]]) -> dict[str, float]:
    """Summarize the free-energy trajectory of already-run train steps.

    The non-increasing fraction is the empirical (Level 5) companion to a
    Lyapunov descent check — rising trends flag a broken coordinate; a
    non-rising trend is *consistent with* descent, never proof (Level 4
    bound).
    """
    energies = [float(s.get("free_energy", s.get("energy", 0.0))) for s in steps]
    if len(energies) < 2:
        return {
            "energy_initial": energies[0] if energies else 0.0,
            "energy_final": energies[-1] if energies else 0.0,
            "energy_mean": energies[0] if energies else 0.0,
            "energy_nonincreasing_fraction": 1.0,
        }
    non_increasing = sum(1 for a, b in pairwise(energies) if b <= a + 1e-12)
    return {
        "energy_initial": energies[0],
        "energy_final": energies[-1],
        "energy_mean": sum(energies) / len(energies),
        "energy_nonincreasing_fraction": non_increasing / (len(energies) - 1),
    }


def measure_gradient_alignment(
    system: System,
    x: Tensor,
    y: Tensor,
) -> dict[str, float]:
    """Measure ∇L·Δθ for one train step with the strict sign convention.

    Δθ = θ_after − θ_before; the directional derivative is a central finite
    difference of the coordinate's free loss along Δθ (Level 4 estimate).
    Returns the restored-θ invariant system — θ equals θ_after on exit.
    """
    before = {n: t.detach().clone() for n, t in system.geometry.params.items()}

    loss_before = free_loss(system, x, y)
    system.train_step(x, y)
    after = {n: t.detach().clone() for n, t in system.geometry.params.items()}
    loss_after = free_loss(system, x, y)

    displacement = {n: after[n] - before[n] for n in before}

    # Central difference along Δθ, probing from θ_before.
    for n, t in system.geometry.params.items():
        t.detach().copy_(before[n])
    for n, t in system.geometry.params.items():
        t.detach().add_(displacement[n], alpha=_FD_EPS)
    loss_plus = free_loss(system, x, y)
    for n, t in system.geometry.params.items():
        t.detach().add_(displacement[n], alpha=-2 * _FD_EPS)
    loss_minus = free_loss(system, x, y)
    for n, t in system.geometry.params.items():
        t.detach().copy_(after[n])

    dd = (loss_plus - loss_minus) / (2 * _FD_EPS)
    disp_sq = sum(float(d.norm() ** 2) for d in displacement.values())
    return {
        "directional_derivative": dd,
        "loss_delta": loss_after - loss_before,
        "displacement_norm": disp_sq**0.5,
    }


def measure_resources(system: System, batch_size: int = 8) -> dict[str, int]:
    """FLOPs/parameter accounting for one train step (Level 4 estimate)."""
    return {
        "train_step_flops": estimate_train_step_flops(system, batch_size),
        "param_count": sum(p.numel() for p in system.geometry.params.values()),
    }


def git_commit_hash() -> str:
    """Short commit hash; "unknown" outside a repository."""
    try:
        out = subprocess.run(
            ["/usr/bin/env", "git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
    except OSError, subprocess.SubprocessError:
        return "unknown"
    return out.stdout.strip()


@dataclass(slots=True)
class SliceMetrics:
    """Raw per-seed measurements from one vertical-slice run."""

    seed: int
    steps: list[dict[str, float]] = field(default_factory=list)
    walltime_s: float = 0.0
    config: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ClaimRecord:
    """Structured claim artifact (TODO18 3.3) — the CI-gated baseline.

    Attributes:
        coordinate: Six-axis coordinate string.
        config: Configuration (dims, lr, steps, task).
        seeds: Seeds actually run.
        metrics: metric name -> {mean, std, n} over all steps/seeds.
        verification_level: Strongest level the recorded claims meet.
        commit_hash: Commit the measurement was taken at.
        walltime_s: Total measurement walltime.
        schema_version: Claim-record schema version.
    """

    coordinate: str
    config: dict[str, object]
    seeds: tuple[int, ...]
    metrics: dict[str, dict[str, float]]
    verification_level: str = "4"
    commit_hash: str = ""
    walltime_s: float = 0.0
    schema_version: str = SCHEMA_VERSION

    @classmethod
    def from_runs(
        cls,
        coordinate: str,
        config: dict[str, object],
        runs: list[SliceMetrics],
    ) -> ClaimRecord:
        """Aggregate per-seed runs into mean ± std (n) per metric."""
        keys = sorted({k for run in runs for step in run.steps for k in step})
        metrics: dict[str, dict[str, float]] = {}
        for key in keys:
            values = [step[key] for run in runs for step in run.steps if key in step]
            if not values:
                continue
            mean = sum(values) / len(values)
            var = sum((v - mean) ** 2 for v in values) / max(len(values) - 1, 1)
            metrics[key] = {"mean": mean, "std": var**0.5, "n": float(len(values))}
        return cls(
            coordinate=coordinate,
            config=config,
            seeds=tuple(run.seed for run in runs),
            metrics=metrics,
            walltime_s=sum(run.walltime_s for run in runs),
            commit_hash=git_commit_hash(),
        )

    def to_json(self) -> str:
        """Serialize to the JSON baseline artifact."""
        return json.dumps(
            {
                "schema_version": self.schema_version,
                "coordinate": self.coordinate,
                "config": self.config,
                "seeds": list(self.seeds),
                "metrics": self.metrics,
                "verification_level": self.verification_level,
                "commit_hash": self.commit_hash,
                "walltime_s": self.walltime_s,
            },
            sort_keys=True,
            indent=2,
        )

    @classmethod
    def from_json(cls, raw: str) -> ClaimRecord:
        """Rehydrate from its JSON artifact."""
        data = json.loads(raw)
        return cls(
            coordinate=data["coordinate"],
            config=data["config"],
            seeds=tuple(data["seeds"]),
            metrics=data["metrics"],
            verification_level=data["verification_level"],
            commit_hash=data["commit_hash"],
            walltime_s=data["walltime_s"],
        )

    def config_digest(self) -> str:
        """Stable digest of coordinate + config (baseline identity)."""
        payload = json.dumps(
            {"coordinate": self.coordinate, "config": self.config}, sort_keys=True
        )
        return hashlib.sha256(payload.encode()).hexdigest()[:16]


_EQPROP_COORD = "digital/recurrent/energy_min/none/thermodynamic_contrast/euclidean"


type BatchProvider = Callable[[int], tuple[Tensor, Tensor]]
"""Per-step batch source: ``step index → (inputs, targets)``."""


def synthetic_batch_provider(
    batch_size: int, input_dim: int, output_dim: int
) -> BatchProvider:
    """The default single-fixed-batch source (baseline-pinned behavior).

    Returns the same tensors every step — matches the pinned
    ``results/vertical_slice/claim_record.json`` exactly.
    """

    def provide(_step: int) -> tuple[Tensor, Tensor]:
        return xs, ys

    xs = torch.randn(batch_size, input_dim)
    ys = torch.randint(0, output_dim, (batch_size,))
    return provide


def fixed_dataset_batch_provider(
    xs: Tensor, ys: Tensor, *, batch_size: int, seed: int
) -> BatchProvider:
    """Deterministic shuffled-epoch provider over a fixed dataset.

    Successive steps walk shuffled minibatches (batch reshuffled at
    epoch end); fully determined by ``(xs, ys, batch_size, seed)``. Use
    for real-data variants (e.g. MNIST tensors loaded by the caller) —
    the slice code is batch-source agnostic.
    """
    g = torch.Generator().manual_seed(seed)
    order = torch.randperm(len(xs), generator=g)
    state = {"cursor": 0}

    def provide(_step: int) -> tuple[Tensor, Tensor]:
        nonlocal order
        if state["cursor"] + batch_size > len(xs):
            order = torch.randperm(len(xs), generator=g)
            state["cursor"] = 0
        idx = order[state["cursor"] : state["cursor"] + batch_size]
        state["cursor"] += batch_size
        return xs[idx], ys[idx]

    return provide


def run_slice(
    seed: int,
    n_steps: int,
    input_dim: int = 16,
    hidden_dim: int = 24,
    output_dim: int = 4,
    batch_size: int = 16,
    lr: float = 0.05,
    batch_provider: BatchProvider | None = None,
) -> SliceMetrics:
    """Run one seed of the auditable vertical slice (TODO18 3.1).

    Coordinate: EqProp + RecurrentGeometry + DigitalSubstrate +
    ThermodynamicContrast + EuclideanUpdate. ``batch_provider=None``
    uses the baseline-pinned synthetic fixed batch; a real-data variant
    (e.g. MNIST tensors via ``fixed_dataset_batch_provider``) swaps the
    batch source only and is recorded as task "custom" in the config.

    Returns:
        Raw per-step metrics for ClaimRecord aggregation.
    """
    from computronium.core.system_trainer.factory import create_eqprop_system

    torch.manual_seed(seed)
    system = create_eqprop_system(
        input_dim=input_dim,
        hidden_dim=hidden_dim,
        output_dim=output_dim,
        num_layers=1,
        settle_steps=10,
        lr=lr,
    )
    if batch_provider is None:
        batch_provider = synthetic_batch_provider(batch_size, input_dim, output_dim)
        task = "synthetic"
    else:
        task = "custom"

    start = time.perf_counter()
    steps: list[dict[str, float]] = []
    for t in range(n_steps):
        xs, ys = batch_provider(t)
        steps.append(system.train_step(xs, ys))
    walltime = time.perf_counter() - start
    config: dict[str, object] = {
        "input_dim": input_dim,
        "hidden_dim": hidden_dim,
        "output_dim": output_dim,
        "batch_size": batch_size,
        "lr": lr,
        "n_steps": n_steps,
        "settle_steps": 10,
        "task": task,
    }
    return SliceMetrics(seed=seed, steps=steps, walltime_s=walltime, config=config)
