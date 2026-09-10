"""Stability × Memory campaign (TODO18 5.2).

Block-structured memory dynamics:

    x_{t+1} = tanh(W_x x_t + W_in u_t + W_fb m_t + ξ_t)   (state block)
    m_{t+1} = (1 − g·w_t) m_t + g·w_t u_t                 (gated memory block)

with write signal ``w_t`` fired on the cue only (selective
preservation) or on every step (ungated — memory rewritten toward the
*current* input each step). The write payload is the input itself.
``W_fb`` is nonzero only in ``coupled`` mode: memory feeds back into
the state block, so write-time noise and precision degradation reach
the state arm (``open`` keeps the state block autonomous, decoupled
from m). After a ``delay`` of distractor steps, a fixed readout must
recover the pattern stored at the cue.

Hypothesis under test (not assumed): useful adaptation needs selective
preservation of state, not global instability. Concretely: retention
should survive high contraction rates under selective gating, while
ungated memory is overwritten by the distractor stream regardless of
contraction. Retention is reported against the *measured* contraction
rate of the state block (perturbation decay over the delay), not the
nominal spectral radius.

Swept axes: contraction rate, gate mode, feedback coupling
(open/coupled), precision, noise, readout constraint (full / low-rank
/ quantized), memory delay. All metrics Level 4 (sampled numerical) /
Level 5 (empirical).
"""

from __future__ import annotations

import itertools
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

import torch

from computronium.analysis.vertical_slice import (
    ClaimRecord,
    SliceMetrics,
    git_commit_hash,
)

if TYPE_CHECKING:
    from pathlib import Path

    from computronium.analysis.mechanistic_study import MechanisticStudyRecord

__all__ = [
    "retention_contraction_scatter",
    "run_memory_trial",
    "run_stability_memory_campaign",
    "save_memory_record",
]

STUDY_COORDINATE = "block_memory/<gate>/<precision>/<readout>/rho<nominal>"

_D_X = 16
_D_M = 16
_PRECISIONS = ("float32", "float16", "bfloat16")
_DTYPES: dict[str, torch.dtype] = {
    "float32": torch.float32,
    "float16": torch.float16,
    "bfloat16": torch.bfloat16,
}


def _contracting_map(contraction: float, *, seed: int) -> torch.Tensor:
    """Random map rescaled to (asymptotically) spectral radius ``contraction``."""
    g = torch.Generator().manual_seed(seed)
    w = torch.randn(_D_X, _D_X, generator=g)
    rho = float(torch.linalg.eigvals(w).abs().max())
    return w * (contraction / max(rho, 1e-12))


def _readout(constraint: str, *, seed: int) -> torch.Tensor:
    """Fixed decode map ``R: memory → pattern space``, optionally constrained."""
    g = torch.Generator().manual_seed(seed)
    r = torch.randn(_D_M, _D_M, generator=g) / _D_M**0.5
    if constraint == "low_rank":
        u, s, vh = torch.linalg.svd(r)
        s = torch.where(torch.arange(len(s)) < 4, s, torch.zeros_like(s))
        return u @ torch.diag(s) @ vh
    return r


def _quantize(m: torch.Tensor, levels: int = 16) -> torch.Tensor:
    """Symmetric min-max quantization to ``levels`` levels (4-bit)."""
    scale = m.abs().max().clamp(min=1e-12)
    return (
        torch.round(m / scale * (levels // 2)).clamp(-(levels // 2), levels // 2)
        * scale
        / (levels // 2)
    )


@dataclass(frozen=True, slots=True)
class _TrialRig:
    """Fixed per-trial maps and layout knobs (built once per trial config)."""

    w_x: torch.Tensor
    w_in: torch.Tensor
    w_fb: torch.Tensor | None
    coupled: bool
    readout: torch.Tensor
    dtype: torch.dtype
    gate: float
    gate_mode: str
    readout_constraint: str


def _episode(
    rig: _TrialRig, delay: int, noise_level: float
) -> tuple[float, float, torch.Tensor]:
    """One store–delay–recall episode: (retention, post-write drift, x_final).

    ``delay`` counts distractor steps *after* the cue. Retention is
    normalized against the gate-scaled cue payload (the g·target floor),
    so precision/quantization/readout degradation stays visible instead
    of being masked by the (1−g) write-scale artifact.
    """
    pattern = torch.randn(_D_M, dtype=rig.dtype)
    x = torch.zeros(_D_X, dtype=rig.dtype)
    m = torch.zeros(_D_M, dtype=rig.dtype)
    distractors = torch.randn(delay, _D_X, dtype=rig.dtype) * 0.3
    noise = torch.randn(delay + 1, _D_X, dtype=rig.dtype) * noise_level
    write_noise = torch.randn(delay + 1, _D_M, dtype=rig.dtype) * noise_level

    for t in range(delay + 1):
        u = pattern if t == 0 else distractors[t - 1]
        drive = rig.w_in @ u
        if rig.coupled:
            drive += rig.w_fb @ m
        x = torch.tanh(rig.w_x @ x + drive + noise[t])
        if rig.gate_mode == "ungated" or t == 0:
            m = (1 - rig.gate) * m + rig.gate * (u + write_noise[t])
    m_final = _quantize(m) if rig.readout_constraint == "quantized" else m
    target = rig.gate * (rig.readout @ pattern)
    energy = max(float(target.norm() ** 2), 1e-12)
    retention = 1.0 - min(
        float((rig.readout @ m_final - target).norm() ** 2) / energy, 1.0
    )
    return (
        retention,
        float((m_final - rig.gate * pattern).norm()),
        x,
    )


def _measured_contraction(rig: _TrialRig, delay: int) -> float:
    """Linearized state-block perturbation decay over ``delay`` steps.

    Replays a zero-noise store–delay episode on the rig's own maps
    (including the memory feedback term in coupled mode), then
    propagates a unit perturbation through the linearized state
    dynamics. The memory perturbation δm is identically zero (m is
    driven by inputs, not by x), so the linearized decay remains the
    tanh-Jacobian product ``∏ (1 − x_t²) W_x`` even in coupled mode;
    coupling shifts the trajectory ``x_t`` the Jacobian is evaluated
    along, not its structure.
    """
    dtype = rig.dtype
    g = torch.Generator().manual_seed(1234)
    u_cue = torch.randn(_D_X, generator=g, dtype=dtype) * 0.3
    u_rest = torch.randn(_D_X, generator=g, dtype=dtype) * 0.3
    x = torch.zeros(_D_X, dtype=dtype)
    m = torch.zeros(_D_M, dtype=dtype)
    delta = torch.randn(_D_X, generator=g, dtype=dtype)
    delta /= delta.norm()
    for t in range(delay):
        u = u_cue if t == 0 else u_rest
        drive = rig.w_in @ u
        if rig.coupled:
            drive += rig.w_fb @ m
        delta = (1.0 - x * x) * (rig.w_x @ delta)
        x = torch.tanh(rig.w_x @ x + drive)
        if rig.gate_mode == "ungated" or t == 0:
            m = (1 - rig.gate) * m + rig.gate * u
    return float(delta.norm() ** (1.0 / max(delay, 1)))


def run_memory_trial(  # ruff: ignore[too-many-arguments] — swept axes are the parameterization
    *,
    seed: int,
    contraction: float,
    gate_mode: Literal["selective", "ungated"],
    coupling: Literal["open", "coupled"],
    precision: Literal["float32", "float16", "bfloat16"],
    noise_level: float,
    readout_constraint: Literal["full", "low_rank", "quantized"],
    delay: int,
    gate_strength: float = 0.7,
    n_trials: int = 8,
) -> dict[str, float]:
    """Run ``n_trials`` store–delay–recall episodes; return mean metrics.

    Each episode stores a random pattern at the cue step, runs ``delay``
    distractor steps, then decodes via the fixed readout. In
    ``coupled`` mode memory feeds back into the state block through a
    random fixed map. Retention is 1 − normalized recall MSE;
    ``measured_contraction`` is the linearized perturbation-decay rate
    of the state block over the episode; ``memory_drift`` is post-write
    memory displacement; ``state_noise_divergence`` is the mean
    final-state distance between each episode and a paired zero-noise
    replay (same input + noise realization), i.e. how much episode
    noise the state arm absorbs.
    """
    dtype = _DTYPES[precision]
    torch.manual_seed(seed)
    coupled = coupling == "coupled"
    rig = _TrialRig(
        w_x=_contracting_map(contraction, seed=seed).to(dtype),
        w_in=torch.randn(
            _D_X, _D_X, generator=torch.Generator().manual_seed(seed + 1)
        ).to(dtype)
        * 0.3,
        w_fb=torch.randn(
            _D_X, _D_M, generator=torch.Generator().manual_seed(seed + 2)
        ).to(dtype)
        * 0.3
        if coupled
        else None,
        coupled=coupled,
        readout=_readout(readout_constraint, seed=seed + 3).to(dtype),
        dtype=dtype,
        gate=gate_strength,
        gate_mode=gate_mode,
        readout_constraint=readout_constraint,
    )
    retention_sum = 0.0
    drift_sum = 0.0
    state_div_sum = 0.0
    for trial in range(n_trials):
        torch.manual_seed(seed * 1000 + trial)
        retention, drift, x_noisy = _episode(rig, delay, noise_level)
        # Paired zero-noise replay (same input + noise realization) to
        # isolate how much episode noise reaches the state arm.
        torch.manual_seed(seed * 1000 + trial)
        _, _, x_quiet = _episode(rig, delay, 0.0)
        retention_sum += retention
        drift_sum += drift
        state_div_sum += float((x_noisy - x_quiet).norm())

    measured = _measured_contraction(rig, delay)

    return {
        "retention": retention_sum / n_trials,
        "memory_drift": drift_sum / n_trials,
        "state_noise_divergence": state_div_sum / n_trials,
        "measured_contraction": measured,
        "nominal_contraction": contraction,
    }


def run_stability_memory_campaign(
    seeds: tuple[int, ...] = (0, 1, 2),
    n_trials: int = 8,
    *,
    contractions: tuple[float, ...] = (0.5, 0.9, 1.05),
    noises: tuple[float, ...] = (0.0, 0.1),
    delays: tuple[int, ...] = (1, 8, 32),
) -> MechanisticStudyRecord:
    """Sweep the Stability × Memory grid and aggregate per-cell records.

    Cells: gate_mode × coupling × precision × readout_constraint ×
    contraction {0.5, 0.9, 1.05} × noise {0.0, 0.1} × delay {1, 8, 32}.
    Each cell's ClaimRecord aggregates mean ± std (n) over seeds × trials.
    """
    from computronium.analysis.mechanistic_study import MechanisticStudyRecord

    start = time.perf_counter()

    cells: dict[str, dict[str, ClaimRecord]] = {}
    for (
        gate,
        coupling,
        precision,
        readout,
        contraction,
        noise,
        delay,
    ) in itertools.product(
        ("selective", "ungated"),
        ("open", "coupled"),
        _PRECISIONS,
        ("full", "low_rank", "quantized"),
        contractions,
        noises,
        delays,
    ):
        cell = (
            f"{gate}/{coupling}/{precision}/{readout}"
            f"/rho{contraction}/noise{noise}/delay{delay}"
        )
        runs = [
            SliceMetrics(
                seed=seed,
                steps=[
                    run_memory_trial(
                        seed=seed,
                        contraction=contraction,
                        gate_mode=gate,
                        coupling=coupling,
                        precision=precision,
                        noise_level=noise,
                        readout_constraint=readout,
                        delay=delay,
                        n_trials=n_trials,
                    )
                ],
                config={"cell": cell},
            )
            for seed in seeds
        ]
        cells[cell] = {
            "retention": ClaimRecord.from_runs(
                f"{STUDY_COORDINATE}#{cell}",
                {"arm": "retention", "n_trials": n_trials},
                runs,
            )
        }

    config: dict[str, object] = {
        "state_dim": _D_X,
        "memory_dim": _D_M,
        "contractions": list(contractions),
        "noises": list(noises),
        "delays": list(delays),
        "n_trials": n_trials,
        "seeds": list(seeds),
        "gate_strength": 0.7,
        "couplings": ["open", "coupled"],
        "task": "store-delay-recall (random fixed patterns)",
    }
    return MechanisticStudyRecord(
        coordinate=STUDY_COORDINATE,
        config=config,
        cells=cells,
        commit_hash=git_commit_hash(),
        walltime_s=time.perf_counter() - start,
    )


def retention_contraction_scatter(
    record: MechanisticStudyRecord,
) -> list[dict[str, float | str]]:
    """Extract the retention-vs-measured-contraction scatter points.

    One point per cell (mean over seeds × trials): nominal + measured
    contraction, mean retention, and the swept categorical axes.
    Consumers (plots, correlation probes) read this instead of
    re-parsing cell names.
    """
    points: list[dict[str, float | str]] = []
    for cell, exps in record.cells.items():
        gate, coupling, precision, readout, rho, noise, delay = cell.split("/")
        claim = exps["retention"]
        points.append({
            "gate_mode": gate,
            "coupling": coupling,
            "precision": precision,
            "readout": readout,
            "noise": float(noise.removeprefix("noise")),
            "delay": int(delay.removeprefix("delay")),
            "nominal_contraction": float(rho.removeprefix("rho")),
            "measured_contraction": claim.metrics["measured_contraction"]["mean"],
            "retention": claim.metrics["retention"]["mean"],
        })
    return points


def save_memory_record(record: MechanisticStudyRecord, path: Path) -> None:
    """Persist the campaign record to ``path`` (parents created)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(record.to_json(), encoding="utf-8")
