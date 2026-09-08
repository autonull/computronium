"""W4.1 probe: hidden-layer closed-form ψ — the overturned seam (TODO14 §10).

W3's verdict: a closed-form ridge ψ on settled activity is an instant,
forget-free READOUT adaptation that recovers exactly the frozen-feature
linear-probe ceiling (0.699) — no more. The pre-registered overturn lever
(TODO14 §10, Session 9): apply the same ridge machinery to the HIDDEN
stream BEFORE the next layer's nonlinearity, so downstream features
reorganize nonlinearly:

    settled h_i → ψ_i correction → ReLU(L_{i+1}) sees the CORRECTED stream

Mechanism (per §10, unchanged): ψ_i = (G_i + λI)⁻¹C_i with the
ClosedFormRidgePlasticity sufficient statistics (bias-augmented G =
Σ X_iᵀX_i, scale-free λ), accumulated per stage-B episode on the NUDGED
settle (the D22 ψ seam — the supervision term must be shown), with input
X_i = hidden stream i. Local target T_i: the readout error
R = onehot − softmax(nudged post) propagated BACKWARD through the FROZEN
θ weights — T_i = R @ W_L @ … @ W_{i+1} (closed-form FA: frozen weights
ARE the feedback matrix, exact by construction, no derivative masks —
solving W1's FA-realizability critique on stacks). Δθ = 0 bitwise
(SHA-256 asserted per arm). Seam: probe-local re-drive of the MLP stack
with corrections injected between layers (the pre-registered seam;
ontology promotion of a modulate_mid_stream contract only if alive).

Design necessity recorded BEFORE measurement: with ONE hidden layer a
linear correction on the last hidden stream before a LINEAR readout
spans the same function class as the W3 readout ψ (post + h@M@Wᵀ ≡
post + h@M′) — the mechanism is degenerate there. The pre-registered
mechanism sentence requires the correction to cross a nonlinearity, so:
cell mlp1 = the W3 cell, hidden (32,) — a DEGENERACY CONTROL
(hidden ψ must ≈ readout ψ there; material excess = seam-defect signal);
cell mlp2 = hidden (32, 32) — the MECHANISM cell (the stream-1
correction crosses ReLU(W₁·)).

Arms (all stage-A matched: same seed, same 300 episodes, θ SHA asserted
identical across arms within a cell):

  mlp1: null | readout (W3 replay: ClosedFormRidgePlasticity through the
        real pipeline) | hidden_raw (stream 1, raw targets)
        | readout_q (post-hoc: readout ridge @ Q)
  mlp2: null | readout | hidden_raw (streams 1+2, raw targets)
        | hidden_norm (streams 1+2, per-batch RMS-matched targets)
        | hidden_first (stream 1 only, RMS-matched — the only correction
          that crosses a nonlinearity)
        | hidden_second (stream 2 only, post-hoc)
        | readout_q (post-hoc)
        | finetune (θ fine-tune control, w3 protocol, criterion 0.984)
  mlp4: null | readout | hidden_raw (streams 1-4) | hidden_first4 /
        hidden_near4 (post-hoc single-stream attribution) | finetune

Pre-registered predictions (written BEFORE any measurement):
- P1 (degeneracy control): mlp1 hidden_raw ≈ readout (both are
  post + linear(h1)). Excess > +0.02 = seam/leak defect signal.
- P2 (overturn criterion, §10 unchanged): mlp2 hidden ψ Task-B exceeds
  the in-run readout ψ ceiling by ≥ +0.02. Falsified → the ceiling is
  the composition depth, not the injection point — a second boundary
  for the closed-form family ("closed-form ψ cannot reorganize
  features even when injected mid-stream at probe depth").
- P3 (scale integrity): raw propagated targets are chain-scaled
  (‖T_i‖ tracks the frozen weight chain); hidden_norm ≥ hidden_raw.
  If equal, the chain is scale-neutral at this depth.
- P4 (attribution): if any hidden arm beats readout, hidden_first
  (the non-degenerate correction) carries it; hidden_norm ≈
  hidden_first would mean the stream-2 correction (linear-readout
  degenerate class) is inert redundancy.
- P5 (§17 sanity): every ψ arm theta_invariant (SHA bitwise); θ SHA
  identical across arms after matched stage A; per-stream target RMS
  and correction norms logged (the channel is measured, not assumed).

Leak controls: probes never see training batches (fresh seeded draws);
null and readout arms re-measured in-run; targets derive ONLY from the
readout error + frozen weights. Eval: 16 batches × 32 = 512 fresh
samples per read (w3 used 256; the in-run re-measurement supersedes the
w3 numbers as the anchor).

Walltime printed, never recorded.

VERDICT (2026-09-08, 3-seed §20 round; seeds 0/1/2, ~19-35 s/seed):

mlp2 (mechanism cell), b_best / b_final:

| arm            | seed 0         | seed 1         | seed 2         |
| -------------- | -------------- | -------------- | -------------- |
| null           | 0.678 / 0.662  | 0.641 / 0.645  | 0.689 / 0.678  |
| readout        | 0.723 / 0.688  | 0.711 / 0.660  | 0.738 / 0.672  |
| hidden_first   | 0.816 / 0.793  | 0.809 / 0.750  | 0.838 / 0.824  |
| hidden_raw     | 0.816 / 0.807  | 0.813 / 0.740  | 0.838 / 0.834  |
| hidden_second  | 0.734 / 0.701  | 0.734 / 0.686  | 0.740 / 0.703  |
| readout_q      | 0.734 / 0.701  | 0.734 / 0.686  | 0.740 / 0.703  |
| finetune       | 0.965 / 0.965  | 0.975 / 0.975  | 0.969 / 0.969  |

- P2 OVERTURN MET, seed-robust: hidden ψ exceeds the in-run readout
  ceiling by +0.093/+0.098/+0.100 (b_best, spread 0.007) on all 3
  seeds; b_final +0.105/+0.090/+0.152. §22 success condition #2 is MET
  at probe scale: gradient-free adaptation that MODIFIES
  REPRESENTATIONS rather than merely re-reads them (θ bitwise frozen,
  SHA-verified per arm; a_retained for ψ arms above).
- MECHANISM DECOMPOSITION (the attribution is bit-exact):
  hidden_second ≡ readout_q BYTE-IDENTICAL on every seed — a stream
  correction before a LINEAR readout is EXACTLY the readout ridge
  solution composed with Q = W_L W_Lᵀ (the frozen readout's gram,
  post-stage-A cond ≈ 52; algebra identity also verified to 7.5e-6
  numerically). So the gain decomposes as: frozen-metric effect
  (readout → readout_q) +0.012-0.014, and the NONLINEAR
  REORGANIZATION effect (readout_q → hidden_first, the correction
  crossing ReLU(W₁·)) +0.082-0.098 — the dominant, class-expanding
  component. P4 CONFIRMED: hidden_first ≈ hidden_raw (the stream-2
  correction is pure Q-class redundancy).
- P1 FALSIFIED with explanation: mlp1's hidden_raw (0.813/0.814/0.842
  best) beats readout there too — but mlp1 readout_q ≡ mlp1
  hidden_raw BYTE-IDENTICAL on every seed: at one hidden layer the
  "hidden" correction is entirely the Q-metric effect (same affine
  class, better regression target), NOT feature reorganization. The
  degeneracy control's real finding: the backward-propagated target
  (closed-form FA through frozen weights) is a better regression
  target than the raw readout residual for the SAME correction class.
- P3: raw ≥ norm (hidden_norm below hidden_raw) — the depth-2 frozen
  chain is scale-neutral (rms_t1 ≈ rms_r); RMS-matched targets add
  nothing and mildly hurt. Raw propagated targets are the recipe.
- Retention cost (honest, 3-seed): a_retained null ~0.96 > readout
  class 0.92-0.97 > hidden_first 0.773/0.785/0.801 (mean 0.786) >
  finetune 0.691. Feature reorganization is NOT forget-free — the
  task-B correction steers the shared hidden stream and misapplies to
  task A — but it retains +0.10 over fine-tune. W4.3's "low retention
  cost" requirement is the open surface, not the acquisition.

W4.2 FIRST RUNG (depth 4, seed 0; post-hoc single-stream attribution
arms labeled as such): the §10 W4.2 claim "local closed-form adaptation
composes across depth" is FALSIFIED at probe scale — by CORRECTION
STACKING, not by depth:

| mlp4 arm        | b_best/b_final | a_retained |
| --------------- | -------------- | ---------- |
| null            | 0.693 / 0.662  | 0.945      |
| readout         | 0.719 / 0.680  | 0.951      |
| hidden_raw (1-4)| 0.762 / 0.707  | 0.494      |
| hidden_first4   | 0.826 / 0.746  | 0.598      |
| hidden_near4    | 0.721 / 0.682  | 0.941      |
| finetune        | 0.967 / 0.967  | 0.660      |

- Stacking all four corrections DEGRADES acquisition below the single
  deep correction (0.762 < 0.826) and destroys retention (0.494, below
  chance): each Δ is fit on uncorrected-stream statistics but applied
  downstream of the other corrections — the mismatch compounds.
- A SINGLE early-stream correction at depth 4 (hidden_first4, crossing
  three ReLUs) KEEPS the full reorganization gain (0.826 ≈ mlp2's
  0.816) — the gain lives in one well-placed deep-reach correction,
  not in count of corrected streams. Depth itself is not the enemy.
- Retention cost scales with the correction's REACH (how early it
  acts): last-hidden/Q-class 0.94 > stream-1-at-depth-2 0.79 >
  stream-1-at-depth-4 0.60 > all-streams 0.49. Deeper reach steers
  more shared representation toward task B.
- Status: single-seed first rung — OPEN (3-seed + §17 before any
  boundary claim), but the mlp2 3-seed round anchors the depth-2
  anchor numbers. Boundary candidate: closed-form hidden ψ is a
  ONE-CORRECTION mechanism (early stream, matched reach), not a
  depth-composable one.

- Gates: ruff clean, pyright 0 errors. Ontology promotion decision
  (modulate_mid_stream plasticity contract) deferred per §10: "only if
  the cell is alive" — the cell is alive.
"""

from __future__ import annotations

import argparse
import time
from collections.abc import Callable

import torch
from torch import Tensor, nn
from w3_closed_form_psi import (
    _batch,
    _Context,
    _settled_acts,
    _theta_sha256,
    _train_stage_a,
)

from computronium import (
    BackpropCredit,
    ClosedFormRidgePlasticity,
    CreditAssignmentConfig,
    EuclideanUpdate,
    GeometryConfig,
    ParameterUpdateConfig,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemState,
    compose_system_from_configs,
)
from computronium.core.pipeline import forward_pass, run_train_step
from computronium.core.plasticity.closed_form import ClosedFormRidgeConfig

SEED = 0
STAGE_A_EPISODES = 300
STAGE_B_EPISODES = 200
CRITERION = 0.984
BATCH = 32
LR = 0.05
PROBE_BATCHES = 16
RIDGE_LAMBDA = ClosedFormRidgeConfig().ridge_lambda

type ArmFn = Callable[[object], dict[str, object]]


def _rms(x: Tensor) -> float:
    return float(x.detach().float().norm() / x.numel() ** 0.5)


def _drive(system, x: Tensor, corrections: dict[int, tuple[Tensor, Tensor]]) -> Tensor:
    """Re-drive the MLP stack with per-stream corrections injected between
    layers (the §10 seam). corrections: stream index → (M, b); the
    correction is added to the stream BEFORE its consuming Linear, so the
    following ReLU sees the corrected pre-activation."""
    h = x.reshape(x.shape[0], -1)
    stream = 0
    for module in system.geometry._layers:
        if isinstance(module, nn.Linear):
            corr = corrections.get(stream)
            if corr is not None:
                m, b = corr
                h = h + h @ m + b
            h = h @ module.weight.T + module.bias
            stream += 1
        else:
            h = module(h)
    return h


def _probe(
    system,
    task: str,
    corrections: dict[int, tuple[Tensor, Tensor]] | None = None,
    plasticity: ClosedFormRidgePlasticity | None = None,
    psi: dict[str, Tensor] | None = None,
    post_corr: tuple[Tensor, Tensor] | None = None,
) -> float:
    correct = total = 0
    with torch.no_grad():
        for _ in range(PROBE_BATCHES):
            x, y = _batch(task)
            if plasticity is not None and psi:
                acts = plasticity.modulate(_settled_acts(system, x), psi)
                logits = acts[-1]
            elif corrections:
                logits = _drive(system, x, corrections)
            else:
                acts = _settled_acts(system, x)
                logits = acts[-1]
                if post_corr is not None:
                    m, b = post_corr
                    logits = logits + acts[-2] @ m + b
            correct += (logits.argmax(-1) == y).sum().item()
            total += len(y)
    return correct / total


def _nudged_acts(system, x: Tensor, y: Tensor) -> list[Tensor]:
    state = SystemState(x=x, y=y)
    state.activations = forward_pass(system.substrate, system.geometry, x)
    settled = system.dynamics.settle(state, system.geometry, system.substrate, target=y)
    acts = settled.activations
    return list(acts) if isinstance(acts, list) else [acts]


def _readout_residual(post: Tensor, y: Tensor) -> Tensor:
    onehot = torch.nn.functional.one_hot(y, post.shape[-1]).float()
    return onehot - torch.softmax(post.detach().float(), dim=-1)


def _propagate_targets(system, residual: Tensor) -> dict[int, Tensor]:
    """T_i = R propagated backward through frozen θ weights (closed-form
    FA). Stream i feeds Linear i; its target crosses Linears i..L-1."""
    weights = [m.weight for m in system.geometry._layers if isinstance(m, nn.Linear)]
    error = residual
    targets: dict[int, Tensor] = {}
    for s in range(len(weights) - 1, 0, -1):
        error @= weights[s]
        targets[s] = error
    return targets


class _LayerRidge:
    """ClosedFormRidgePlasticity's ridge statistics, per hidden stream."""

    def __init__(self) -> None:
        self._gram: Tensor | None = None
        self._cross: Tensor | None = None

    def update(self, stream: Tensor, target: Tensor) -> None:
        x = stream.detach().float()
        ones = torch.ones(x.shape[0], 1, device=x.device, dtype=x.dtype)
        xa = torch.cat((x, ones), dim=-1)
        g = xa.T @ xa
        c = xa.T @ target.detach().float()
        self._gram = g if self._gram is None else self._gram + g
        self._cross = c if self._cross is None else self._cross + c

    def solve(self) -> tuple[Tensor, Tensor] | None:
        if self._gram is None or self._cross is None:
            return None
        d = self._gram.shape[0]
        lam = RIDGE_LAMBDA * self._gram.diagonal().mean().clamp_min(1e-12)
        m_aug = torch.linalg.solve(
            self._gram + lam * torch.eye(d, device=self._gram.device), self._cross
        )
        return m_aug[:-1], m_aug[-1]


def _stage_b_null(system) -> dict[str, object]:
    return {
        "b_best": _probe(system, "B"),
        "b_final": _probe(system, "B"),
        "a_retained": _probe(system, "A"),
        "episodes": 0,
    }


def _stage_b_readout(system, *, compose_q: bool = False) -> dict[str, object]:
    plasticity = ClosedFormRidgePlasticity()
    psi: dict[str, Tensor] = plasticity.initial_psi(None, BATCH)
    context = _Context(system.geometry.params)  # type: ignore[arg-type]
    sha_before = _theta_sha256(system)
    metric: Tensor | None = None
    if compose_q:
        readout = [m for m in system.geometry._layers if isinstance(m, nn.Linear)][-1]
        metric = readout.weight @ readout.weight.T
    b_start = _probe(system, "B")
    frozen_update = EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=0.0))
    best = final = b_start

    def eval_with(task: str) -> float:
        if compose_q and metric is not None:
            m = psi.get("readout_m")
            b = psi.get("readout_b")
            if not isinstance(m, Tensor) or not isinstance(b, Tensor):
                return _probe(system, task)
            return _probe(system, task, post_corr=(m @ metric, b @ metric))
        return _probe(system, task, plasticity=plasticity, psi=psi)

    for _ in range(STAGE_B_EPISODES):
        x, y = _batch("B")
        run_train_step(
            system.substrate,
            system.geometry,
            system.dynamics,
            system.credit,
            frozen_update,
            x,
            y,
            plasticity=plasticity,
            psi=psi,
            context=context,
        )
        final = eval_with("B")
        best = max(best, final)
    return {
        "b_start": b_start,
        "b_best": best,
        "b_final": final,
        "a_retained": eval_with("A"),
        "theta_invariant": sha_before == _theta_sha256(system),
        "episodes": STAGE_B_EPISODES,
    }


def _stage_b_hidden(
    system, streams: list[int], *, normalize: bool
) -> dict[str, object]:
    sha_before = _theta_sha256(system)
    b_start = _probe(system, "B")
    ridges = {s: _LayerRidge() for s in streams}
    signal: dict[str, float] = {}
    best = final = b_start
    corrections: dict[int, tuple[Tensor, Tensor]] = {}
    for episode in range(1, STAGE_B_EPISODES + 1):
        x, y = _batch("B")
        acts = _nudged_acts(system, x, y)
        residual = _readout_residual(acts[-1], y)
        targets = _propagate_targets(system, residual)
        for s in streams:
            if episode == 1:
                signal["rms_r"] = _rms(residual)
                signal[f"rms_t{s}"] = _rms(targets[s])
            if normalize:
                t = targets[s] * (_rms(residual) / max(_rms(targets[s]), 1e-12))
            else:
                t = targets[s]
            ridges[s].update(acts[s], t)
        corrections = {s: m for s in streams if (m := ridges[s].solve()) is not None}
        final = _probe(system, "B", corrections=corrections)
        best = max(best, final)
    return {
        "b_start": b_start,
        "b_best": best,
        "b_final": final,
        "a_retained": _probe(system, "A", corrections=corrections),
        "theta_invariant": sha_before == _theta_sha256(system),
        "episodes": STAGE_B_EPISODES,
        "corr_norms": {s: float(m[0].norm()) for s, m in corrections.items()},
        **signal,
    }


def _stage_b_finetune(system) -> dict[str, object]:
    b_start = _probe(system, "B")
    credit = BackpropCredit(CreditAssignmentConfig.gradient())
    euclid = EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=LR / 2))
    episodes = 0
    acc = b_start
    for episodes in range(1, STAGE_B_EPISODES + 1):
        x, y = _batch("B")
        run_train_step(
            system.substrate,
            system.geometry,
            system.dynamics,
            credit,
            euclid,
            x,
            y,
        )
        acc = _probe(system, "B")
        if acc >= CRITERION:
            break
    return {
        "b_start": b_start,
        "b_best": acc,
        "b_final": acc,
        "a_retained": _probe(system, "A"),
        "episodes": episodes,
    }


def _compose(hidden_dims: tuple[int, ...]):
    return compose_system_from_configs(
        SubstrateConfig.digital(),
        GeometryConfig.feedforward(
            input_dim=4 * 8, output_dim=2, hidden_dims=hidden_dims
        ),
        StateDynamicsConfig.instantaneous(),
        CreditAssignmentConfig.gradient(),
        ParameterUpdateConfig.euclidean(step_size=LR),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    seed = args.seed
    torch.manual_seed(seed)
    t0 = time.time()
    parity_system = _compose((32,))
    x, _ = _batch("B")
    settled_post = _settled_acts(parity_system, x)[-1]
    driven_post = _drive(parity_system, x, {})
    if not torch.allclose(settled_post, driven_post, atol=1e-6):
        raise RuntimeError(  # ruff: ignore[raise-vanilla-args] - probe gate
            "seam parity: _drive must reproduce the settle forward exactly"
        )
    del parity_system

    cells: dict[str, tuple[tuple[int, ...], dict[str, ArmFn]]] = {
        "mlp1": (
            (32,),
            {
                "null": _stage_b_null,
                "readout": _stage_b_readout,
                "hidden_raw": lambda s: _stage_b_hidden(s, [1], normalize=False),
                "readout_q": lambda s: _stage_b_readout(s, compose_q=True),
            },
        ),
        "mlp4": (
            (32, 32, 32, 32),
            {
                "null": _stage_b_null,
                "readout": _stage_b_readout,
                "hidden_raw": lambda s: _stage_b_hidden(
                    s, [1, 2, 3, 4], normalize=False
                ),
                "hidden_first4": lambda s: _stage_b_hidden(s, [1], normalize=False),
                "hidden_near4": lambda s: _stage_b_hidden(s, [4], normalize=False),
                "finetune": _stage_b_finetune,
            },
        ),
        "mlp2": (
            (32, 32),
            {
                "null": _stage_b_null,
                "readout": _stage_b_readout,
                "hidden_raw": lambda s: _stage_b_hidden(s, [1, 2], normalize=False),
                "hidden_norm": lambda s: _stage_b_hidden(s, [1, 2], normalize=True),
                "hidden_first": lambda s: _stage_b_hidden(s, [1], normalize=True),
                "hidden_second": lambda s: _stage_b_hidden(s, [2], normalize=False),
                "readout_q": lambda s: _stage_b_readout(s, compose_q=True),
                "finetune": _stage_b_finetune,
            },
        ),
    }
    for cell, (hidden_dims, arms) in cells.items():
        print(f"\n=== cell {cell} hidden={hidden_dims} ===", flush=True)
        shas: set[str] = set()
        for arm, stage_b in arms.items():
            torch.manual_seed(seed)
            system = _compose(hidden_dims)
            a_mastery = _train_stage_a(system)
            shas.add(_theta_sha256(system))
            result = stage_b(system)
            print(
                f"{arm}: stage A {a_mastery:.4f}  {result}",
                flush=True,
            )
        if len(shas) != 1:
            raise RuntimeError(  # ruff: ignore[raise-vanilla-args] - probe gate
                f"stage-A theta mismatch across arms: {shas}"
            )
        print("stage-A theta matched across arms: True", flush=True)

    print(f"\nwalltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
