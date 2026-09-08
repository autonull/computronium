"""W4 scaled probe: Flagship B D1 (scaled overturn cell) + D3 (stacking
repair) + the reach dial (TODO14 §24).

VERDICT (2026-09-08, Session 12, 3 seeds, GPU, ~5-18 min/seed): the
overturn FAILS at scale — the flagship earns its BOUNDARY (§24.3
stop-loss). b_best:

| arm          | seed 0 | seed 1 | seed 2 | mean  |
| ------------ | ------ | ------ | ------ | ----- |
| null         | 0.096  | 0.097  | 0.101  | 0.098 |
| readout      | 0.667  | 0.676  | 0.679  | 0.674 |
| finetune     | 0.783  | 0.782  | 0.783  | 0.783 |
| hidden_s1    | 0.227  | 0.166  | 0.259  | 0.217 |
| hidden_s2    | 0.365  | 0.322  | 0.188  | 0.292 |
| hidden_s3    | 0.525  | 0.316  | 0.318  | 0.387 |
| hidden_s4    | 0.656  | 0.679  | 0.675  | 0.670 |
| hidden_raw   | 0.138  | 0.102  | 0.048  | 0.096 |
| hidden_boost | 0.410  | 0.326  | 0.429  | 0.388 |

- P-A FALSIFIED, seed-robust: NO hidden arm beats the readout ceiling on
  any seed. hidden_s4 (last hidden stream, Q-class, crosses NO ReLU)
  ≈ ceiling (0.670 vs 0.674 — the same Q-identity as probe scale);
  deeper streams DEGRADE MONOTONICALLY with reach (s3 0.387, s2 0.292,
  s1 0.217). The probe-scale +0.08-0.10 ReLU-crossing reorganization
  gain does NOT transfer to MNIST→FashionMNIST scale. P-D INVERTED:
  at probe scale deeper reach = bigger gain; at scale deeper reach =
  worse (the first-order correction across more mask patterns is
  increasingly invalid).
- P-C (boosting) FALSIFIED as the full repair: fit-on-corrected
  (0.388) repairs stacking vs stacked-raw (0.096 — at/below null,
  catastrophic) but does NOT recover the single-correction level
  (0.670). Boosting is a real but bounded repair.
- §17 findings en route (each invalidates the naive construction):
  (1) the probe-scale residual R = onehot − softmax(post) is
  CALIBRATION-POISONED at scale — the frozen backbone is confidently
  wrong on FashionMNIST (post RMS ~1.9), swamping the ±1 onehot signal
  even IN-SAMPLE (0.088 train-fit; the onehot ridge on the same
  features: 0.66). Fix: solve the ceiling readout (h_last → onehot,
  applied as readout replacement) and use R* = ceiling − post.
  (2) T = R @ W-chain (the W Wᵀ ≈ I per-hop approximation) is invalid
  for trained weights — corrections died crossing ReLUs. Fix: exact
  mask-aware Jacobian targets, T_s = R @ pinv(J_s) with J_s built
  batched through the ReLU masks (mask = post-ReLU stream > 0).
  (3) Retention at scale is LOW for every closed-form arm (readout
  replacement 0.07-0.10 on task A — intrinsic to replacement; hidden
  arms 0.06-0.44, noisy) — retention at scale is a STATE-MANAGEMENT
  property, not a correction property: the D2 multi-ψ library demo
  (swap, don't overwrite) is the shipped resolution.
- Status: §24 D1 = Boundary at scale (the open question is retired
  either way); D3 = falsified-as-repair; D2 = shipped
  (tests/integration/test_demo_multi_psi_swap.py, gallery D17).

The W4.1 probe-scale construction (frozen θ + per-stream closed-form ridge
ψ, targets propagated backward through the frozen weights) moves to
MNIST-class scale: backbone MLP 784 → (128, 128, 128, 128) → 10, task
A = MNIST (stage A, backprop via the ontology pipeline), task
B = FashionMNIST (stage B, gradient-free adaptation, θ bitwise frozen).
All five §24.2 pre-registrations, written BEFORE execution:

- P-A (scale transfer / D1 overturn criterion): the pre-registered
  placement — the DEEPEST-REACH stream (stream 1, crossing four ReLUs,
  the Session-11 attribution rule) — beats the in-run readout ψ ceiling
  by ≥ +0.02 on all 3 seeds. Falsified after the §17 protocol → the
  flagship earns a boundary at scale (stop-loss, §24.3).
- P-D (reach dial): a_retained varies MONOTONICALLY with injection
  depth (later streams retain more, reach less) — the probe-scale
  "retention cost scales with reach" claim must replicate or break.
- P-C (boosting fixes stacking / D3): fitting deeper corrections on the
  CORRECTED stream (re-drive between solves, residual on the corrected
  post) recovers stacked acquisition to ≥ the single-correction level
  and retention toward it. Falsified → the one-correction boundary is
  confirmed with the fix tested.
- P-E (matched-θ control): stage A runs once per seed; the snapshot is
  restored per arm (bitwise — SHA asserted identical across arms).
- P-F (§17 sanity): every ψ arm theta_invariant (SHA bitwise over stage
  B); per-arm eval on fresh draws from the HELD-OUT test split only.

§17 FINDING (scale, found at first execution, fixes the target
construction): the probe-scale residual R = onehot − softmax(post) is
CALIBRATION-POISONED at MNIST scale — the frozen backbone's logits on
FashionMNIST are confidently wrong (post RMS ~1.9), so the ±1 onehot
signal is swamped even IN-SAMPLE (softmax-residual readout ridge:
0.088 train-fit acc; direct onehot ridge on the same features: 0.66).
The scale-faithful construction: solve the readout ridge to the
CEILING (h_last → onehot, applied as a readout replacement — the same
affine class as post + affine since the readout itself is affine in
h_last), then use R* = ceiling_readout(h) − post as the readout-level
residual for backward propagation. R* carries the post's own scale,
which is what a correction must cancel.

Arms: null / readout (ridge on the last hidden stream, target R, applied
post — the readout ψ class) / hidden_s1..s4 (single-stream, pre-registered
placement s1 = deepest reach) / hidden_raw (streams 1-4 stacked,
fit-on-uncorrected — the D3 baseline) / hidden_boost (streams 1-4 stacked,
fit-on-CORRECTED — the D3 repair) / finetune (θ fine-tune control).

Walltime printed, never recorded.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import time
from collections.abc import Callable

import torch
from torch import Tensor, nn
from w4_hidden_psi import _drive, _LayerRidge

from computronium import (  # type: ignore[attr-defined]
    BackpropCredit,
    CreditAssignmentConfig,
    EuclideanUpdate,
    GeometryConfig,
    ParameterUpdateConfig,
    StateDynamicsConfig,
    SubstrateConfig,
    System,
    compose_system_from_configs,
)
from computronium.core.pipeline import run_train_step

BATCH = 128
EVAL_EVERY = 10
PROBE_BATCHES = 8
LR = 0.1
FT_LR = 0.02
STAGE_A_EPISODES = 800
STAGE_B_EPISODES = 200
HIDDEN: tuple[int, ...] = (128, 128, 128, 128)
STREAMS = (1, 2, 3, 4)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

type ArmFn = Callable[..., dict[str, object]]


def _theta_sha256(system) -> str:
    raw = b"".join(
        p.detach().cpu().contiguous().view(-1).view(torch.uint8).numpy().tobytes()
        for p in system.geometry.params.values()
    )
    return hashlib.sha256(raw).hexdigest()


def _dataset(name: str, train: bool) -> tuple[Tensor, Tensor]:
    import torchvision

    cls = getattr(torchvision.datasets, name)
    ds = cls(root="data", train=train, download=False)
    x = ds.data.float().reshape(-1, 784) / 255.0
    return x, ds.targets.long()


class _Data:
    def __init__(self) -> None:
        self.a_train = _dataset("MNIST", True)
        self.a_test = _dataset("MNIST", False)
        self.b_train = _dataset("FashionMNIST", True)
        self.b_test = _dataset("FashionMNIST", False)
        self._gen = torch.Generator().manual_seed(20260908)
        self._perm: dict[str, Tensor] = {}
        self._cursor: dict[str, int] = {}

    def episode(self, which: str) -> tuple[Tensor, Tensor]:
        x, y = self.a_train if which == "A" else self.b_train
        if which not in self._perm or self._cursor[which] + BATCH > len(x):
            self._perm[which] = torch.randperm(len(x), generator=self._gen)
            self._cursor[which] = 0
        idx = self._perm[which][self._cursor[which] : self._cursor[which] + BATCH]
        self._cursor[which] += BATCH
        return x[idx].to(DEVICE), y[idx].to(DEVICE)

    def probe(self, which: str) -> tuple[Tensor, Tensor]:
        x, y = self.a_test if which == "A" else self.b_test
        idx = torch.randint(len(x), (PROBE_BATCHES * BATCH,), generator=self._gen)
        return x[idx].to(DEVICE), y[idx].to(DEVICE)


@functools.cache
def _data() -> _Data:
    return _Data()


def _batch(task: str) -> tuple[Tensor, Tensor]:
    return _data().episode(task)


def _forward_acts(system, x: Tensor) -> list[Tensor]:
    h = x
    acts: list[Tensor] = []
    for module in system.geometry._layers:
        if isinstance(module, nn.Linear):
            acts.append(h)
            h = h @ module.weight.T + module.bias
        else:
            h = module(h)
    acts.append(h)
    return acts


def _probe(
    system,
    task: str,
    corrections: dict[int, tuple[Tensor, Tensor]] | None = None,
    post_corr: tuple[Tensor, Tensor] | None = None,
) -> float:
    x, y = _data().probe(task)
    with torch.no_grad():
        acts = _forward_acts(system, x)
        logits = acts[-1]
        if corrections:
            logits = _drive(system, x, corrections)
        if post_corr is not None:
            m, b = post_corr
            logits = acts[-2] @ m + b
    return (logits.argmax(-1) == y).float().mean().item()


def _onehot(y: Tensor, n: int) -> Tensor:
    return torch.nn.functional.one_hot(y, n).float()


def _exact_targets(
    system, residual: Tensor, streams: list[Tensor]
) -> dict[int, Tensor]:
    """T_s = R @ pinv(J_s) with J_s the stream-s → logits Jacobian of the
    frozen chain INCLUDING the ReLU masks (mask_k = stream k+1 > 0,
    readable directly from the post-ReLU activations). The probe-scale
    construction (T_s = R @ W_L … W_{s+1}) assumes W Wᵀ ≈ I per hop and
    open ReLUs; MNIST-trained weights violate both by orders of
    magnitude — corrections died crossing ReLUs (seed-0 first run)."""
    weights = [m.weight for m in system.geometry._layers if isinstance(m, nn.Linear)]
    n = len(weights)
    batch = residual.shape[0]
    targets: dict[int, Tensor] = {}
    for s in range(n - 1, 0, -1):
        jacobian = weights[s].T.unsqueeze(0).expand(batch, -1, -1)
        for k in range(s, n - 1):
            masks = torch.diag_embed((streams[k + 1] > 0).float())
            jacobian = jacobian @ masks @ weights[k + 1].T
        pinv_j = torch.linalg.pinv(jacobian.detach().float())
        targets[s] = (residual.unsqueeze(1) @ pinv_j).squeeze(1)
    return targets


class _ReadoutCeiling:
    """Ridge h_last -> onehot, applied as a readout REPLACEMENT (the
    frozen-feature linear-probe ceiling; same affine class as
    post + affine(h) because the readout is itself affine in h_last)."""

    def __init__(self) -> None:
        self._ridge = _LayerRidge()

    def update(self, h: Tensor, y: Tensor) -> None:
        self._ridge.update(h, _onehot(y, 10))

    def solve(self) -> tuple[Tensor, Tensor] | None:
        return self._ridge.solve()

    @staticmethod
    def apply(h: Tensor, mr: Tensor, br: Tensor) -> Tensor:
        return h @ mr + br


def _stage_a(seed: int) -> tuple[System, float, str]:
    torch.manual_seed(seed)
    system = compose_system_from_configs(
        SubstrateConfig.digital(),
        GeometryConfig.feedforward(input_dim=784, output_dim=10, hidden_dims=HIDDEN),
        StateDynamicsConfig.instantaneous(),
        CreditAssignmentConfig.gradient(),
        ParameterUpdateConfig.euclidean(step_size=LR),
    )
    system = system.to(DEVICE)  # type: ignore[attr-defined]
    for _ in range(STAGE_A_EPISODES):
        x, y = _batch("A")
        run_train_step(
            system.substrate,
            system.geometry,
            system.dynamics,
            system.credit,
            system.update,
            x,
            y,
        )
    return system, _probe(system, "A"), _theta_sha256(system)


def _eval_trajectory(
    system,
    corrections: dict[int, tuple[Tensor, Tensor]] | None = None,
    post_corr: tuple[Tensor, Tensor] | None = None,
) -> dict[str, object]:
    best = final = _probe(system, "B", corrections, post_corr)
    for episode in range(2, STAGE_B_EPISODES + 1):
        if episode % EVAL_EVERY == 0:
            final = _probe(system, "B", corrections, post_corr)
            best = max(best, final)
    return {
        "b_best": best,
        "b_final": final,
        "a_retained": _probe(system, "A", corrections, post_corr),
    }


def _drive_corrected(
    system, x: Tensor, live: dict[int, tuple[Tensor, Tensor]]
) -> tuple[list[Tensor], Tensor, Tensor]:
    h = x
    stream = 0
    streams: list[Tensor] = []
    for module in system.geometry._layers:
        if isinstance(module, nn.Linear):
            corr = live.get(stream)
            if corr is not None:
                m, b = corr
                h = h + h @ m + b
            streams.append(h)
            h = h @ module.weight.T + module.bias
            stream += 1
        else:
            h = module(h)
    return streams, h, streams[-1]


def _fit_streams(
    ridges: dict[int, _LayerRidge],
    streams: list[int],
    sources: list[Tensor],
    targets: dict[int, Tensor],
) -> dict[int, tuple[Tensor, Tensor]]:
    for s in streams:
        ridges[s].update(sources[s], targets[s])
    live: dict[int, tuple[Tensor, Tensor]] = {}
    for s in streams:
        solved = ridges[s].solve()
        if solved is not None:
            live[s] = solved
    return live


def _stage_b_null(system, corrections) -> dict[str, object]:
    return _eval_trajectory(system)


def _stage_b_hidden(
    system,
    corrections,
    *,
    streams: list[int],
    boost: bool,
) -> dict[str, object]:
    sha_before = _theta_sha256(system)
    ridges = {s: _LayerRidge() for s in streams}
    ceiling = _ReadoutCeiling()
    live: dict[int, tuple[Tensor, Tensor]] = {}
    for _ in range(STAGE_B_EPISODES):
        x, y = _batch("B")
        if boost and live:
            sources, post, h_last = _drive_corrected(system, x, live)
        else:
            acts = _forward_acts(system, x)
            sources, post, h_last = acts, acts[-1], acts[-2]
        ceiling.update(h_last, y)
        solved = ceiling.solve()
        if solved is None:
            continue
        residual = _ReadoutCeiling.apply(h_last, *solved) - post
        targets = _exact_targets(system, residual, sources)
        live = _fit_streams(ridges, streams, sources, targets)
    return {
        **_eval_trajectory(system, live),
        "theta_invariant": sha_before == _theta_sha256(system),
        "corr_norms": {s: float(m[0].norm()) for s, m in live.items()},
    }


def _stage_b_readout(system, corrections) -> dict[str, object]:
    sha_before = _theta_sha256(system)
    ceiling = _ReadoutCeiling()
    m = b = None
    for _ in range(STAGE_B_EPISODES):
        x, y = _batch("B")
        acts = _forward_acts(system, x)
        ceiling.update(acts[-2], y)
        solved = ceiling.solve()
        if solved is not None:
            m, b = solved
    post_corr = (m, b) if m is not None and b is not None else None
    return {
        **_eval_trajectory(system, post_corr=post_corr),
        "theta_invariant": sha_before == _theta_sha256(system),
        "ceiling_replacement": True,
    }


def _stage_b_finetune(system, corrections) -> dict[str, object]:
    credit = BackpropCredit(CreditAssignmentConfig.gradient())
    euclid = EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=FT_LR))
    best = _probe(system, "B")
    final = best
    for episode in range(1, STAGE_B_EPISODES + 1):
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
        if episode % EVAL_EVERY == 0:
            final = _probe(system, "B")
            best = max(best, final)
    return {
        "b_best": best,
        "b_final": final,
        "a_retained": _probe(system, "A"),
    }


def _arms() -> dict[str, ArmFn]:
    arms: dict[str, ArmFn] = {
        "null": _stage_b_null,
        "readout": _stage_b_readout,
        "finetune": _stage_b_finetune,
    }
    for s in STREAMS:
        arms[f"hidden_s{s}"] = lambda system, corrections, s=s: _stage_b_hidden(
            system, corrections, streams=[s], boost=False
        )
    arms["hidden_raw"] = lambda system, corrections: _stage_b_hidden(
        system, corrections, streams=list(STREAMS), boost=False
    )
    arms["hidden_boost"] = lambda system, corrections: _stage_b_hidden(
        system, corrections, streams=list(STREAMS), boost=True
    )
    return arms


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--stage-a-episodes", type=int, default=800)
    parser.add_argument("--stage-b-episodes", type=int, default=200)
    parser.add_argument("--only-arms", type=str, default="")
    args = parser.parse_args()
    seed = args.seed
    globals()["STAGE_A_EPISODES"] = args.stage_a_episodes
    globals()["STAGE_B_EPISODES"] = args.stage_b_episodes
    t0 = time.time()

    system, a_mastery, sha_stage_a = _stage_a(seed)
    print(f"stage A mastery {a_mastery:.4f}  sha {sha_stage_a[:12]}", flush=True)
    snapshot = {k: v.detach().clone() for k, v in system.geometry.params.items()}
    null_check = _probe(system, "B")
    print(f"b_start (null transfer) {null_check:.4f}", flush=True)

    only = {a for a in args.only_arms.split(",") if a}
    for arm, stage_b in _arms().items():
        if only and arm not in only:
            continue
        for k, v in system.geometry.params.items():
            v.data.copy_(snapshot[k])
        if _theta_sha256(system) != sha_stage_a:
            raise RuntimeError(  # ruff: ignore[raise-vanilla-args] - probe gate
                "stage-A snapshot restore drifted"
            )
        result = stage_b(system, {})
        print(f"{arm}: {result}", flush=True)

    print(f"\nwalltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
