"""W8.1 minimal NCA probe (TODO.ntm_nca.md §2): local credit on iterative
local dynamics — the four-cell adversarial testbed for I(C,U).

Task: pattern regeneration, Mordvintsev-minimal. 16x16 grid, 4 state
channels, shared cell MLP (3x3 neighborhood + label channel -> hidden 32
-> delta-state), stochastic per-cell update mask, seed cell -> grow ->
hold. State channels are bounded to [0, STATE_MAX] — a bounded-substrate
constraint applied identically in every arm; the ceiling sits ABOVE the
target one-hot range so no channel can saturate the bound (a ceiling at
the target max created an all-saturated attractor: every channel pinned,
argmax tie-broken to channel 0, CE floored at ln 4). Target sprites: ring / cross / diagonal / hollow-square (class id
per cell in {0..3}, channel logits at the readout).

Arms (exactly four; update rules are the ONTOLOGY rules — the U axis is
real, not re-implemented):
  1 bptt  x euclid  (control, lr tuned once on an 80-episode screen)
  2 bptt  x muon    (control, screened {0.005, 0.02})
  3 local x euclid  0.2 (D16 MLP-calibrated; local pseudo-grads are
                      EMA-RMS-normalized per the W0 recipe)
  4 local x muon    0.02

Local arm construction (per-cell = per-sample reshaping, plan §1): the
target id is injected as a label channel appended to each cell's
perception vector; the negative pass rolls the label across cells (the
local_contrastive _augment convention). Per-layer goodness contrast
G+ - G- on the hidden (w1) and delta (w2) layers, softplus gate
theta=2.0, EMA-RMS normalization on the gated pseudo-grads; the label
readout (wr) trains on RAW local CE (the W0 readout finding). Pseudo-
grads are summed over the rollout and applied once per episode
(O(1)-memory credit; plan §1 shared-weight aggregation).

Pre-registered predictions (plan §2, written before execution):
- P1 (rollout-length law): BPTT quality degrades with rollout length;
  local is rollout-flat but possibly lower-ceilinged. Measured here as
  eval accuracy at rollout {24, 48, 96} per arm (the full damage curve
  is W8.3).
- P2 (I(C,U) replication): local x muon > local x euclid by MORE than
  bptt x muon > bptt x euclid (the SP2/W1 signature in a new regime).
  Falsified -> the law is geometry-bound.
- P3 (inversion generality): per-site contrast sign inversions
  (dG < -theta) appear in the NCA as in the transformer. The per-step
  inversion RATE is logged; failure-locus correlation is deferred to
  W8.3.
- P4 (signal integrity): the label-channel injection contrast is
  MEASURED per step (r = ||x+ - x-|| / ||x+||), not assumed.

Budget: 240 train episodes (80 for screens), rollout 32 train, batch 8,
seeds 0-2, CPU minutes per cell. Walltime printed, never recorded.

Run: ``uv run python scripts/probes/w8_nca_local.py``
``--seed=N`` restricts to a single seed (smoke).
"""

import time
from dataclasses import replace

import torch
import torch.nn.functional as F  # ruff: ignore[lowercase-imported-as-non-lowercase]
from torch import Tensor

from computronium import ParameterUpdateConfig
from computronium.ontology.update import EuclideanUpdate, RiemannianOrthogonalUpdate

REV = "2026-09-07-r2"  # per-step BPTT credit + arm/seed flags

GRID = 16
CHANNELS = 4
HIDDEN = 32
IN_DIM = CHANNELS * 9 + 1
ROLLOUT = 32
EPISODES = 400
EVAL_EVERY = 40
BATCH = 8
GATE_THETA = 2.0
STATE_MAX = 10.0  # above the target range so no channel saturates the clamp
EVAL_ROLLOUTS = (24, 48, 96)
SEEDS = (0, 1, 2)


def _sprites() -> Tensor:
    """Procedural target sprites (P, GRID, GRID) of class ids 0..3."""
    i = torch.arange(GRID).view(-1, 1)
    j = torch.arange(GRID).view(1, -1)
    c = (GRID - 1) / 2
    ring = (((i - c).abs() - 3).abs() <= 1) & (((j - c).abs() - 3).abs() <= 1)
    cross = ((i - c).abs() <= 1) | ((j - c).abs() <= 1)
    diag = ((i - j).abs() <= 1) & (i + j > 3) & (i + j < 2 * GRID - 5)
    hollow = (((i - c).abs() == 4) | ((j - c).abs() == 4)) & (
        ((i - c).abs() <= 4) & ((j - c).abs() <= 4)
    )
    ids = torch.stack([
        ring.float() + hollow.float() * 2,
        cross.float() + (ring & cross).float() * 2,
        diag.float() + ((i - c).abs() <= 1).float() * ((j - c).abs() <= 1) * 3,
        hollow.float() + ring.float() * 2,
    ]).long()
    return ids.clamp(0, 3)


def _params(seed: int) -> dict[str, Tensor]:
    g = torch.Generator().manual_seed(seed)
    p = {
        "w1": torch.randn(HIDDEN, IN_DIM, generator=g) * IN_DIM**-0.5,
        "w2": torch.randn(CHANNELS, HIDDEN, generator=g) * HIDDEN**-0.5,
        "wr": torch.randn(CHANNELS, HIDDEN, generator=g) * HIDDEN**-0.5,
        "b1": torch.zeros(HIDDEN),
        "b2": torch.zeros(CHANNELS),
        "br": torch.zeros(CHANNELS),
    }
    return {k: v.requires_grad_(True) for k, v in p.items()}


def _perceive(states: Tensor, labels: Tensor) -> Tensor:
    """(B, C, H, W) states + (B, H, W) labels -> (B*H*W, IN_DIM)."""
    B, _C, H, W = states.shape
    pad = F.pad(states, (1, 1, 1, 1))
    nb = torch.cat(
        [pad[:, :, y : y + H, x : x + W] for y in range(3) for x in range(3)], dim=1
    )
    feats = torch.cat([nb, labels.unsqueeze(1)], dim=1)
    return feats.permute(0, 2, 3, 1).reshape(B * H * W, IN_DIM)


def _cell_forward(p: dict[str, Tensor], states: Tensor, labels: Tensor):
    x = _perceive(states, labels)
    h = F.relu(F.linear(x, p["w1"], p["b1"]))
    delta = F.linear(h, p["w2"], p["b2"])
    logits = F.linear(h, p["wr"], p["br"])
    return h, delta, logits


def _seed_states(targets: Tensor, gen: torch.Generator) -> Tensor:
    B, H, W = targets.shape
    states = torch.zeros(B, CHANNELS, H, W)
    y = int(torch.randint(4, 8, (1,), generator=gen))
    x = int(torch.randint(4, 8, (1,), generator=gen))
    states[:, :, y, x] = torch.eye(CHANNELS)[targets[0, y, x]]
    return states


def _rollout_states(
    p: dict[str, Tensor], targets: Tensor, steps: int, gen: torch.Generator, grad: bool
) -> Tensor:
    """Runs `steps` updates; labels are the true target ids (the target
    is part of the regeneration environment)."""
    states = _seed_states(targets, gen)
    for _ in range(steps):
        mask = (torch.rand(targets.shape, generator=gen) < 0.5).float()
        ctx = torch.enable_grad() if grad else torch.no_grad()
        with ctx:
            _, delta, _ = _cell_forward(p, states, targets)
        delta_grid = _unflatten(delta, targets.size(0), *targets.shape[1:])
        states = (states + delta_grid * mask.unsqueeze(1)).clamp(0.0, STATE_MAX)
    return states


def _nca_step_terms(
    p: dict[str, Tensor], states: Tensor, targets: Tensor, neg_labels: Tensor
) -> tuple[list[tuple[str, Tensor]], Tensor, dict[str, float]]:
    """Per-step local-credit loss terms (readout CE + gated goodness per
    layer), the positive-pass delta, and P3/P4 diagnostics (per-site
    inversion counts, label-injection contrast r)."""
    xp = torch.cat([states, targets.unsqueeze(1).float()], dim=1)
    xn = torch.cat([states, neg_labels.unsqueeze(1).float()], dim=1)
    inject_r = float(((xp - xn).norm() / (xp.norm() + 1e-8)).item())
    h_p, d_p, logits = _cell_forward(p, xp[:, :-1], xp[:, -1])
    h_n, d_n, _ = _cell_forward(p, xn[:, :-1], xn[:, -1])
    ce = _weighted_ce(logits, targets)
    gate_terms, inversions, sites = _goodness_terms((
        ("w1", h_p, h_n),
        ("w2", d_p, d_n),
    ))
    return (
        [("wr", ce), *gate_terms],
        d_p,
        {
            "inversions": inversions,
            "sites": sites,
            "inject_r": inject_r,
        },
    )


def _accumulate(
    terms: list[tuple[str, Tensor]],
    p: dict[str, Tensor],
    weight_grads: dict[str, Tensor],
    bias_grads: dict[str, Tensor],
) -> None:
    """Sums per-term weight/bias gradients into the episode accumulators."""
    for i, (name, loss) in enumerate(terms):
        params = [p[name], p["b" + name[1]]]
        grads = torch.autograd.grad(loss, params, retain_graph=i < len(terms) - 1)
        for key, g in zip((name, "b" + name[1]), grads, strict=True):
            out = weight_grads if key.startswith("w") else bias_grads
            out[key] = out.get(key, 0) + g.detach()


def _weighted_ce(logits: Tensor, targets: Tensor) -> Tensor:
    """Inverse-frequency-weighted CE (the sprites are ~87% bg — unweighted
    CE has a trivial all-background attractor)."""
    flat = targets.reshape(-1)
    counts = torch.bincount(flat, minlength=CHANNELS).float().clamp(min=1)
    w = (1.0 / counts)[flat]
    w *= flat.numel() / w.sum()
    return (F.cross_entropy(logits, flat, reduction="none") * w).mean()


def _unflatten(cells: Tensor, B: int, H: int, W: int) -> Tensor:
    """(B*H*W, C) per-cell rows -> (B, C, H, W) state layout."""
    return cells.view(B, H, W, CHANNELS).permute(0, 3, 1, 2)


def _goodness_terms(act_pairs):
    """Gated goodness loss terms plus the P3 per-site inversion counts."""
    terms: list[tuple[str, Tensor]] = []
    inversions = 0
    sites = 0
    for name, act_p, act_n in act_pairs:
        d_g = (act_p.pow(2).sum(1) - act_n.pow(2).sum(1)).flatten()
        inversions += int((d_g < -GATE_THETA).sum())
        sites += d_g.numel()
        terms.append((
            name,
            F.softplus(GATE_THETA - (act_p.pow(2).mean() - act_n.pow(2).mean())),
        ))
    return terms, inversions, sites


def _local_episode(
    p: dict[str, Tensor], targets: Tensor, gen: torch.Generator
) -> tuple[dict[str, Tensor], dict[str, Tensor], dict[str, float]]:
    """Per-step gated goodness credit, summed over the rollout."""
    states = _seed_states(targets, gen)
    neg_labels = targets.flatten(1).roll(1, dims=1).view_as(targets)
    weight_grads: dict[str, Tensor] = {}
    bias_grads: dict[str, Tensor] = {}
    inversions = 0
    sites = 0
    inject_r = 0.0
    for _ in range(ROLLOUT):
        mask = (torch.rand(targets.shape, generator=gen) < 0.5).float()
        terms, d_p, step_stats = _nca_step_terms(p, states, targets, neg_labels)
        inversions += step_stats["inversions"]
        sites += step_stats["sites"]
        inject_r += step_stats["inject_r"]
        _accumulate(terms, p, weight_grads, bias_grads)
        with torch.no_grad():
            d_grid = _unflatten(d_p, targets.size(0), *targets.shape[1:])
            states = (states + d_grid * mask.unsqueeze(1)).clamp(0.0, STATE_MAX)
    stats = {
        "inversion_rate": inversions / max(sites, 1),
        "inject_r": inject_r / ROLLOUT,
    }
    return weight_grads, bias_grads, stats


def _ema_normalize(
    grads: dict[str, Tensor], ema: dict[str, float]
) -> dict[str, Tensor]:
    out = {}
    for name, g in grads.items():
        rms = float(g.norm() / (g.numel() ** 0.5 + 1e-12))
        prev = ema.get(name, rms)
        ema[name] = 0.99 * prev + 0.01 * rms
        out[name] = g / (ema[name] + 1e-8)
    return out


def _apply(update, p: dict[str, Tensor], grads: dict[str, Tensor]) -> None:
    weights = [n for n in p if n.startswith("w")]
    biases = {n: grads[n] for n in p if n.startswith("b") and n in grads}
    # geometry=None: the update rules only read param shapes (probe-local use).
    new = update.step(
        p,
        [grads[n] for n in weights],
        None,
        biases,  # pyright: ignore[reportArgumentType]
    )
    p.update({k: v.detach().requires_grad_(True) for k, v in new.items()})


def _eval(
    p: dict[str, Tensor], targets: Tensor, steps: int
) -> tuple[float, float, float]:
    gen = torch.Generator().manual_seed(123)
    final = _rollout_states(p, targets, steps, gen, grad=False)
    ce = _weighted_ce(final.permute(0, 2, 3, 1).reshape(-1, CHANNELS), targets)
    hit = final.argmax(1) == targets
    return float(ce), float(hit.float().mean()), float(hit[targets > 0].float().mean())


def _train(
    arm: str,
    update_name: str,
    seed: int,
    lr: float,
    episodes: int = EPISODES,
    eval_every: int = EVAL_EVERY,
) -> float:
    torch.manual_seed(seed)
    sprites = _sprites()
    gen = torch.Generator().manual_seed(seed)
    batch_idx = torch.randint(0, len(sprites), (BATCH,), generator=gen)
    p = _params(seed)
    update = _updates(lr)[update_name]
    ema: dict[str, float] = {}
    stats_last = {"inversion_rate": 0.0, "inject_r": 0.0}
    curve: list[tuple[int, float]] = []
    for ep in range(episodes):
        targets = sprites[batch_idx]
        if arm == "bptt":
            grads = _bptt_grads(p, targets, gen)
        else:
            w_grads, b_grads, stats_last = _local_episode(p, targets, gen)
            grads = _ema_normalize(w_grads, ema)
            grads.update(b_grads)
        _apply(update, p, grads)
        if (ep + 1) % eval_every == 0:
            curve.append((ep + 1, _eval(p, sprites[batch_idx], 48)[1]))
    _report(
        arm,
        update_name,
        seed,
        lr,
        p,
        sprites[batch_idx],
        curve,
        stats_last,
        arm == "local",
    )
    return _eval(p, sprites[batch_idx], 48)[1]


def _bptt_grads(p: dict[str, Tensor], targets: Tensor, gen: torch.Generator):
    final = _rollout_states(p, targets, ROLLOUT, gen, grad=True)
    loss = _weighted_ce(final.permute(0, 2, 3, 1).reshape(-1, CHANNELS), targets)
    grads_all = torch.autograd.grad(loss, list(p.values()), allow_unused=True)
    return {
        n: g if g is not None else torch.zeros_like(p[n])
        for n, g in zip(p, grads_all, strict=True)
    }


def _no_clip(cfg):
    return replace(cfg, grad_clip=0.0)


def _updates(lr: float) -> dict[str, object]:
    # grad_clip 0 (disabled): the global-clip default made every BPTT step a
    # fixed-norm jump — the lr-invariant screens were the §17 signature. The
    # substrate state bound (clamp) replaces the explosion guard, identically
    # in all arms.
    return {
        "euclid": EuclideanUpdate(
            _no_clip(ParameterUpdateConfig.euclidean(step_size=lr))
        ),
        "muon": RiemannianOrthogonalUpdate(
            _no_clip(
                ParameterUpdateConfig.riemannian_orthogonal(step_size=lr, momentum=0.9)
            )
        ),
    }


def _report(
    arm: str,
    update_name: str,
    seed: int,
    lr: float,
    p: dict[str, Tensor],
    targets: Tensor,
    curve: list[tuple[int, float]],
    stats: dict[str, float],
    show_stats: bool,
) -> None:
    finals = {steps: _eval(p, targets, steps) for steps in EVAL_ROLLOUTS}
    accs = " ".join(f"{a:.3f}" for _, a in curve)
    extra = (
        f"  inv {stats['inversion_rate']:.3f} inject_r {stats['inject_r']:.3f}"
        if show_stats
        else ""
    )
    print(
        f"{arm:>5} x {update_name:>6} (lr {lr:g}) seed {seed}: "
        f"CE {finals[48][0]:.3f} fg-acc {finals[48][2]:.3f}  curve {accs}{extra}",
        flush=True,
    )
    horizons = "  ".join(f"h{s}: {finals[s][2]:.3f}" for s in EVAL_ROLLOUTS)
    print(f"    P1 horizons: {horizons}", flush=True)


def _screen() -> dict[str, float]:
    """Tune bptt-euclid once, bptt-muon screened; frozen for the main cells."""
    best: dict[str, float] = {}
    for update_name, lrs in (("euclid", (0.1, 0.3, 1.0)), ("muon", (0.02, 0.05, 0.1))):
        results = {
            lr: _train("bptt", update_name, 0, lr, episodes=120, eval_every=60)
            for lr in lrs
        }
        best_lr = max(results, key=lambda k: results[k])
        best[update_name] = best_lr
        print(f"screen: bptt x {update_name} -> lr {best_lr:g}", flush=True)
    return best


def main() -> int:
    t0 = time.time()
    args = __import__("sys").argv[1:]
    opt = dict(a[2:].split("=") for a in args if a.startswith("--") and "=" in a)
    seed = int(opt["seed"]) if "seed" in opt else None
    seeds = (seed,) if seed is not None else SEEDS
    arm = opt.get("arm")
    print(f"w8_nca_local {REV}; arm {arm or 'all'} seeds {seeds}")
    if arm is None:
        lrs = _screen()
        cells = [
            ("bptt", "euclid", lrs["euclid"]),
            ("bptt", "muon", lrs["muon"]),
            ("local", "euclid", 0.2),
            ("local", "muon", 0.02),
        ]
    else:
        cells = [(arm, u, lr) for u, lr in (("euclid", 0.1), ("muon", 0.02))]
    for cell_arm, update_name, lr in cells:
        for s_ in seeds:
            _train(cell_arm, update_name, s_, lr)
    print(f"\nwalltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
