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

W8.4 (``--unshared``, plan §5): per-site weight copies — the weight-
sharing axis, never touched by I(C,U) anywhere in the repo. Unshared
weights are stored flat as (SITES*out, in) 2-D matrices: the site dimension
folds into the row space, so (a) the ontology update-rule contract
("weight"-substring, 2-D) holds unchanged, (b) EuclidUpdate — elementwise —
is EXACTLY per-site descent (each site's rows only receive that site's
cells' gradient contributions), and (c) the grouped forward unifies both
modes (shared weights broadcast over sites, unshared weights view to
(SITES, out, in)). Muon-on-unshared is DEFERRED: orthogonalizing the
(SITES*out, in) matrix mixes sites — it is a different rule, not the
per-site muon; record before ever running it.

Pre-registered (W8.4, written before execution):
- P-shared-match: unshared x local x euclid solves (fg >= 0.95, 3 seeds)
  — each site's problem is independently solvable (distill gives every
  site its own proportional controller) and per-site credit volume is
  unchanged. Falsified -> weight-sharing is LOAD-BEARING for local
  credit at this scale (a new I(C,U)-adjacent finding).
- P-bptt-fragile: unshared x bptt x euclid inherits the shared arm's
  fragility (seed-level divergence at lr 0.03). Falsified -> per-site
  parameters stabilize 32-step backprop.

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
from computronium.ontology.update import (
    EuclideanUpdate,
    OrthoAdamUpdate,
    RiemannianOrthogonalUpdate,
)

REV = "2026-09-08-r10"  # W8.4 unshared per-site weights

GRID = 16
CHANNELS = 4
HIDDEN = 32
IN_DIM = CHANNELS * 9 + 1
IN_DIM_LABEL_FREE = CHANNELS * 9
SITES = GRID * GRID
ROLLOUT = 32
EPISODES = 400
EVAL_EVERY = 40
BATCH = 8
DELTA_SCALE = 0.5  # P-A: |delta| <= 0.5/step; state is UNBOUNDED (no clamp)
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


def _params(
    seed: int, in_dim: int = IN_DIM, unshared: bool = False, routing: bool = False
) -> dict[str, Tensor]:
    """Shared: one cell MLP. Unshared (W8.4): per-site weights stored flat
    (SITES*out, in) — the site dimension folds into the row space so the
    update-rule contract and per-site euclid both hold exactly.
    Routing (TODO16 §2.4): adds a per-site growth gate g = sigmoid(W_g h);
    effective delta = g * delta (gated growth)."""
    g = torch.Generator().manual_seed(seed)
    rows = SITES if unshared else 1
    p = {
        "weight1": torch.randn(rows * HIDDEN, in_dim, generator=g) * in_dim**-0.5,
        "weight2": torch.randn(rows * CHANNELS, HIDDEN, generator=g) * HIDDEN**-0.5,
        "weight_readout": torch.randn(rows * CHANNELS, HIDDEN, generator=g)
        * HIDDEN**-0.5,
        "bias1": torch.zeros(rows * HIDDEN),
        "bias2": torch.zeros(rows * CHANNELS),
        "bias_readout": torch.zeros(rows * CHANNELS),
    }
    if routing:
        p["weight_gate"] = torch.randn(rows, in_dim, generator=g) * in_dim**-0.5
        p["bias_gate"] = torch.zeros(rows)
    return {k: v.requires_grad_(True) for k, v in p.items()}


def _perceive(states: Tensor, labels: Tensor | None) -> Tensor:
    """(B, C, H, W) states + (B, H, W) labels | None -> (B*H*W, in_dim)."""
    _B, _C, H, W = states.shape
    pad = F.pad(states, (1, 1, 1, 1))
    nb = torch.cat(
        [pad[:, :, y : y + H, x : x + W] for y in range(3) for x in range(3)], dim=1
    )
    feats = nb if labels is None else torch.cat([nb, labels.unsqueeze(1)], dim=1)
    return feats.permute(0, 2, 3, 1).reshape(-1, feats.size(1))


def _grouped_forward(p: dict[str, Tensor], x: Tensor) -> tuple[Tensor, Tensor, Tensor]:
    """(G, S, in) grouped cell rows -> (G, S, H)/(G, S, C) streams.
    Shared weights broadcast over groups (g=1); unshared weights view to
    (SITES, out, in) — one weight set per site (W8.4)."""
    uns = p["weight1"].size(0) != HIDDEN
    w1 = (
        p["weight1"].view(SITES, HIDDEN, x.size(-1))
        if uns
        else p["weight1"].view(1, HIDDEN, x.size(-1))
    )
    b1 = p["bias1"].view(SITES, HIDDEN) if uns else p["bias1"].view(1, HIDDEN)
    h = F.relu(torch.einsum("gsi,soi->gso", x, w1) + b1)
    wc = (
        p["weight2"].view(SITES, CHANNELS, HIDDEN)
        if uns
        else p["weight2"].view(1, CHANNELS, HIDDEN)
    )
    bc = p["bias2"].view(SITES, CHANNELS) if uns else p["bias2"].view(1, CHANNELS)
    delta = DELTA_SCALE * torch.tanh(torch.einsum("gso,sco->gsc", h, wc) + bc)
    if "weight_gate" in p:
        rows_g = p["weight_gate"].size(0)
        wg = p["weight_gate"].view(rows_g, 1, x.size(-1))
        bg = p["bias_gate"].view(rows_g, 1)
        gate = torch.sigmoid(torch.einsum("gsi,ghi->gsh", x, wg) + bg)
        delta = gate * delta
    wr = (
        p["weight_readout"].view(SITES, CHANNELS, HIDDEN)
        if uns
        else p["weight_readout"].view(1, CHANNELS, HIDDEN)
    )
    br = (
        p["bias_readout"].view(SITES, CHANNELS)
        if uns
        else p["bias_readout"].view(1, CHANNELS)
    )
    logits = torch.einsum("gso,sco->gsc", h, wr) + br
    return h, delta, logits


def _cell_forward(p: dict[str, Tensor], states: Tensor, labels: Tensor | None):
    x = _perceive(states, labels)
    g = states.size(0)
    h, delta, logits = _grouped_forward(p, x.view(g, SITES, x.size(-1)))
    return (
        h.reshape(-1, HIDDEN),
        delta.reshape(-1, CHANNELS),
        logits.reshape(-1, CHANNELS),
    )


def _seed_states(targets: Tensor, gen: torch.Generator, center: bool = False) -> Tensor:
    B, H, W = targets.shape
    states = torch.zeros(B, CHANNELS, H, W)
    if center:
        y = x = GRID // 2
    else:
        y = int(torch.randint(4, 8, (1,), generator=gen))
        x = int(torch.randint(4, 8, (1,), generator=gen))
    states[:, :, y, x] = torch.eye(CHANNELS)[targets[0, y, x]]
    return states


def _rollout_states(
    p: dict[str, Tensor],
    targets: Tensor,
    steps: int,
    gen: torch.Generator,
    grad: bool,
    labels: Tensor | None = None,
    states: Tensor | None = None,
) -> tuple[Tensor, list[Tensor]]:
    """P-A dynamics (§11.3): unbounded additive state, tanh-bounded small
    deltas, per-step state-space MSE credit (the clamp + CE-on-states
    design produced the clamped-integrator saturation attractor). With
    grad=True, also returns the per-step MSE terms. ``labels=None`` is
    the label-free regime (W8.3); ``states`` continues an existing
    rollout (damage regeneration)."""
    target_states = _target_states(targets)
    if states is None:
        states = _seed_states(targets, gen, center=labels is None)
    step_losses: list[Tensor] = []
    for _ in range(steps):
        mask = (torch.rand(targets.shape, generator=gen) < 0.5).float()
        ctx = torch.enable_grad() if grad else torch.no_grad()
        with ctx:
            _, delta, _logits = _cell_forward(p, states, labels)
        delta_grid = _unflatten(delta, targets.size(0), *targets.shape[1:])
        # non-augmented: states enters the autograd graph mid-rollout
        states = states + delta_grid * mask.unsqueeze(1)  # ruff: ignore[non-augmented-assignment]
        if grad:
            step_losses.append((states - target_states).pow(2).mean())
    return states, step_losses


def _target_states(targets: Tensor) -> Tensor:
    """One-hot state-space target (bg cells: channel 0 = 1)."""
    return F.one_hot(targets, CHANNELS).permute(0, 3, 1, 2).float()


def _distill_init(  # ruff: ignore[too-many-locals] - probe harness; locals are orthogonal modes
    p: dict[str, Tensor],
    targets: Tensor,
    n_mixes: int = 10,
    steps: int = 1500,
    lr: float = 1e-2,
    label_free: bool = False,
    regen: bool = False,
) -> float:
    """Supervised distillation of the ideal proportional controller
    delta* = clamp(target - state, +/-DELTA_SCALE) into the cell MLP
    (§11.4: BPTT-from-scratch cannot find a stable growth field from a
    seed; a distilled field has the target as an exact fixed point and
    seeds the four-arm comparison). Returns the final distillation MSE.

    Label-free (W8.3): training states come from TEACHER rollouts (ideal
    controller with labels, mask on) — the label-free-reachable manifold.
    Regen mode: states are the TARGET with random k x k holes (k in
    {2,4,6,8,10,12}), inputs label-free; the distill fit quality IS the
    feasibility rung (§13.1-2)."""
    target_states = _target_states(targets)
    X: list[Tensor] = []
    if regen:
        rng = torch.Generator().manual_seed(7)
        for _ in range(2 * n_mixes):
            k = int(
                torch.tensor([2, 4, 6, 8, 10, 12])[
                    torch.randint(0, 6, (1,), generator=rng)
                ]
            )
            st = target_states.clone()
            y = int(torch.randint(0, GRID - k + 1, (1,), generator=rng))
            x = int(torch.randint(0, GRID - k + 1, (1,), generator=rng))
            st[:, :, y : y + k, x : x + k] = 0.0
            X.append(st)
    elif label_free:
        gen = torch.Generator().manual_seed(7)
        teacher = target_states.clone()
        for t in range(33):
            if t in {0, 1, 2, 4, 8, 16, 24, 32}:
                X.append(teacher)
            mask = (torch.rand(targets.shape, generator=gen) < 0.5).float()
            # non-augmented: teacher enters the autograd-free distill set
            teacher = teacher + (target_states - teacher).clamp(  # ruff: ignore[non-augmented-assignment]
                -DELTA_SCALE, DELTA_SCALE
            ) * mask.unsqueeze(1)
    else:
        for _ in range(n_mixes):
            m1 = torch.rand(1).item()
            m3 = torch.rand(1).item()
            st = (
                m1 * target_states
                + (1 - m1) * m3 * torch.rand_like(target_states) * 0.5
                + (1 - m1) * (1 - m3) * _seed_states(targets, torch.Generator())
            )
            X.append(st)
    x_labels = None if label_free or regen else torch.cat([targets] * len(X))
    Y = [(target_states - st).clamp(-DELTA_SCALE, DELTA_SCALE) for st in X]
    x = _perceive(torch.cat(X), x_labels)
    yd = torch.cat(Y).permute(0, 2, 3, 1).reshape(-1, CHANNELS)
    n_batches = yd.size(0) // SITES
    xg = x.view(n_batches, SITES, x.size(-1))
    yg = yd.view(n_batches, SITES, CHANNELS)
    opt = torch.optim.Adam(list(p.values()), lr=lr)
    loss = torch.zeros(())
    for _ in range(steps):
        _h, pred, _logits = _grouped_forward(p, xg)
        loss = (pred - yg).pow(2).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
    return float(loss.detach())


def _unflatten(cells: Tensor, B: int, H: int, W: int) -> Tensor:
    """(B*H*W, C) per-cell rows -> (B, C, H, W) state layout."""
    return cells.view(B, H, W, CHANNELS).permute(0, 3, 1, 2)


def _local_episode(
    p: dict[str, Tensor],
    targets: Tensor,
    gen: torch.Generator,
    labels: Tensor | None = None,
    init_states: Tensor | None = None,
) -> tuple[dict[str, Tensor], dict[str, Tensor], dict[str, float]]:
    """Zero-history local credit (§11.4): per-step state-space MSE with
    the state DETACHED — no gradient crosses a timestep (the NCA
    analogue of the NTM zero-history factorization). Pseudo-grads are
    summed over the rollout; the readout (wr) is outside the dynamics
    and receives zero gradient. ``labels=None`` = label-free;
    ``init_states`` = regeneration start (W8.3)."""
    target_states = _target_states(targets)
    states = (
        init_states
        if init_states is not None
        else _seed_states(targets, gen, center=labels is None)
    )
    weight_grads: dict[str, Tensor] = {}
    bias_grads: dict[str, Tensor] = {}
    for _ in range(ROLLOUT):
        mask = (torch.rand(targets.shape, generator=gen) < 0.5).float()
        with torch.enable_grad():
            _h, delta, _logits = _cell_forward(p, states.detach(), labels)
        next_states = states.detach() + _unflatten(
            delta, targets.size(0), *targets.shape[1:]
        ) * mask.unsqueeze(1)
        loss = (next_states - target_states).pow(2).mean()
        grads = torch.autograd.grad(loss, list(p.values()), allow_unused=True)
        for name, g in zip(p, grads, strict=True):
            out = weight_grads if name.startswith("weight") else bias_grads
            out[name] = torch.zeros_like(p[name]) if g is None else g.detach()
        states = next_states.detach()
    stats = {"inversion_rate": 0.0, "inject_r": 0.0}
    return weight_grads, bias_grads, stats


def _apply(update, p: dict[str, Tensor], grads: dict[str, Tensor]) -> None:
    weights = [n for n in p if n.startswith("weight")]
    biases = {n: grads[n] for n in p if n.startswith("bias") and n in grads}
    # geometry=None: the update rules only read param shapes (probe-local use).
    new = update.step(
        p,
        [grads[n] for n in weights],
        None,
        biases,  # pyright: ignore[reportArgumentType]
    )
    p.update({k: v.detach().requires_grad_(True) for k, v in new.items()})


def _eval(
    p: dict[str, Tensor], targets: Tensor, steps: int, label_free: bool = False
) -> tuple[float, float, float]:
    gen = torch.Generator().manual_seed(123)
    final = _rollout_states(
        p, targets, steps, gen, grad=False, labels=None if label_free else targets
    )[0]
    mse = (final - _target_states(targets)).pow(2).mean()
    hit = final.argmax(1) == targets
    return float(mse), float(hit.float().mean()), float(hit[targets > 0].float().mean())


def _hole_states(
    targets: Tensor, target_states: Tensor, k: int, gen: torch.Generator
) -> Tensor:
    """W8.3 regeneration task: the TARGET organism with a random k x k
    fully-zeroed hole (label-free pattern completion)."""
    states = target_states.clone()
    y = int(torch.randint(0, GRID - k + 1, (1,), generator=gen))
    x = int(torch.randint(0, GRID - k + 1, (1,), generator=gen))
    states[:, :, y : y + k, x : x + k] = 0.0
    return states


def _regen_eval(
    p: dict[str, Tensor], targets: Tensor, k: int, steps: int = 48
) -> float:
    """Post-regeneration fg accuracy after filling a k x k hole (label-free)."""
    gen = torch.Generator().manual_seed(123)
    target_states = _target_states(targets)
    states = _hole_states(targets, target_states, k, gen)
    final = _rollout_states(
        p, targets, steps, gen, grad=False, labels=None, states=states
    )[0]
    hit = final.argmax(1) == targets
    return float(hit.float().mean())


def _damage_eval(
    p: dict[str, Tensor],
    targets: Tensor,
    k: int,
    grow: int = 48,
    regen: int = 48,
    label_free_regen: bool = True,
) -> float:
    """W8.3: grow (labels on), zero a random k x k patch of the FULL
    state, regenerate (labels off when label_free_regen), return
    post-regeneration fg accuracy."""
    gen = torch.Generator().manual_seed(123)
    states = _rollout_states(p, targets, grow, gen, grad=False, labels=targets)[0]
    states = _hole_states(targets, states, k, gen)
    final = _rollout_states(
        p,
        targets,
        regen,
        gen,
        grad=False,
        labels=None if label_free_regen else targets,
        states=states,
    )[0]
    hit = final.argmax(1) == targets
    return float(hit[targets > 0].float().mean())


def _episode_grads(
    p: dict[str, Tensor],
    arm: str,
    targets: Tensor,
    gen: torch.Generator,
    labels: Tensor | None,
    init: Tensor | None,
) -> tuple[dict[str, Tensor], dict[str, float]]:
    if arm == "bptt":
        return _bptt_grads(p, targets, gen, labels, init), {}
    w_grads, b_grads, stats = _local_episode(p, targets, gen, labels, init)
    return {**w_grads, **b_grads}, stats


def _train(  # ruff: ignore[too-many-locals, too-many-arguments, too-many-positional-arguments] - probe harness
    arm: str,
    update_name: str,
    seed: int,
    lr: float,
    episodes: int = EPISODES,
    eval_every: int = EVAL_EVERY,
    label_free: bool = False,
    regen: bool = False,
    damage: bool = False,
    unshared: bool = False,
    routing: bool = False,
    gate_lr_scale: float = 1.0,
) -> float:
    torch.manual_seed(seed)
    sprites = _sprites()
    gen = torch.Generator().manual_seed(seed)
    batch_idx = torch.randint(0, len(sprites), (BATCH,), generator=gen)
    targets0 = sprites[batch_idx]
    in_dim = IN_DIM_LABEL_FREE if label_free or regen else IN_DIM
    p = _params(seed, in_dim, unshared, routing=routing)
    _distill_init(p, targets0, label_free=label_free, regen=regen)
    update = _updates(lr)[update_name]
    stats_last = {"inversion_rate": 0.0, "inject_r": 0.0}
    curve: list[tuple[int, float]] = []
    hole_ks = (4, 6, 8, 10)
    for ep in range(episodes):
        targets = targets0
        labels = None if label_free or regen else targets
        init = None
        if regen:
            k = hole_ks[ep % len(hole_ks)]
            init = _hole_states(targets, _target_states(targets), k, gen)
        grads, stats_last = _episode_grads(p, arm, targets, gen, labels, init)
        if gate_lr_scale < 1.0:
            grads = {
                n: g * gate_lr_scale if "gate" in n else g for n, g in grads.items()
            }
        _apply(update, p, grads)
        if (ep + 1) % eval_every == 0:
            acc = (
                _regen_eval(p, targets, 8)
                if regen
                else _eval(p, targets, 48, label_free)[1]
            )
            curve.append((ep + 1, acc))
    _report(
        (arm, update_name, seed, lr),
        p,
        targets0,
        curve,
        stats_last,
        label_free,
        damage,
        regen,
    )
    if "weight_gate" in p:
        print(
            f"    gate activity {(_gate_activity(p, targets0, label_free)):.3f}",
            flush=True,
        )
    return (
        _regen_eval(p, targets0, 8) if regen else _eval(p, targets0, 48, label_free)[1]
    )


def _bptt_grads(
    p: dict[str, Tensor],
    targets: Tensor,
    gen: torch.Generator,
    labels: Tensor | None = None,
    init_states: Tensor | None = None,
):
    _final, step_losses = _rollout_states(
        p, targets, ROLLOUT, gen, grad=True, labels=labels, states=init_states
    )
    loss = torch.stack(step_losses).mean()
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
        "ortho_adam": OrthoAdamUpdate(
            _no_clip(
                ParameterUpdateConfig.ortho_adam(
                    step_size=lr, ortho_lr=lr, momentum=0.9
                )
            )
        ),
    }


def _gate_activity(p: dict[str, Tensor], targets: Tensor, label_free: bool) -> float:
    """Fraction of site-steps with an open growth gate (compute proxy,
    TODO16 §2.4): 1.0 = ungated baseline, lower = sparser compute."""
    gen = torch.Generator().manual_seed(123)
    states = _seed_states(targets, gen, center=not label_free)
    open_frac = 0.0
    wg = p["weight_gate"].view(1, 1, -1)
    bg = p["bias_gate"].view(1, 1)
    for _ in range(ROLLOUT):
        x = _perceive(states, None if label_free else targets)
        gate = torch.sigmoid(
            torch.einsum("gsi,ghi->gsh", x.view(-1, SITES, x.size(-1)), wg) + bg
        )
        open_frac += (gate > 0.5).float().mean().item()
        with torch.no_grad():
            _h, delta, _l = _cell_forward(p, states, None if label_free else targets)
        states = states + _unflatten(delta, targets.size(0), *targets.shape[1:])
    return open_frac / ROLLOUT


def _report(
    cell: tuple[str, str, int, float],
    p: dict[str, Tensor],
    targets: Tensor,
    curve: list[tuple[int, float]],
    stats: dict[str, float],
    label_free: bool = False,
    damage: bool = False,
    regen: bool = False,
    show_stats: bool = False,
) -> None:
    arm, update_name, seed, lr = cell
    tag = " [label-free]" if label_free else (" [regen]" if regen else "")
    finals = (
        {}
        if regen
        else {steps: _eval(p, targets, steps, label_free) for steps in EVAL_ROLLOUTS}
    )
    accs = " ".join(f"{a:.3f}" for _, a in curve)
    extra = (
        f"  inv {stats['inversion_rate']:.3f} inject_r {stats['inject_r']:.3f}"
        if show_stats
        else ""
    )
    if regen:
        head = f"regen-k8 acc {curve[-1][1]:.3f}" if curve else "regen-k8 acc ?"
        print(
            f"{arm:>5} x {update_name:>6} (lr {lr:g}) seed {seed}{tag}: "
            f"{head}  curve {accs}",
            flush=True,
        )
    else:
        print(
            f"{arm:>5} x {update_name:>6} (lr {lr:g}) seed {seed}{tag}: "
            f"MSE {finals[48][0]:.3f} fg-acc {finals[48][2]:.3f}  curve {accs}{extra}",
            flush=True,
        )
        horizons = "  ".join(f"h{s}: {finals[s][2]:.3f}" for s in EVAL_ROLLOUTS)
        print(f"    P1 horizons: {horizons}", flush=True)
    if damage or regen:
        ks = (2, 4, 6, 8, 10, 12, 14, 16) if regen else (4, 8, 12, 16)
        sweep = "  ".join(
            f"k{k}: {_regen_eval(p, targets, k):.3f}"
            if regen
            else f"k{k}: {_damage_eval(p, targets, k):.3f}"
            for k in ks
        )
        label = "regen holes (acc)" if regen else "damage sweep (fg-acc post-regen)"
        print(f"    {label}: {sweep}", flush=True)


def _screen() -> dict[str, float]:
    """Tune bptt-euclid once, bptt-muon screened; frozen for the main cells."""
    best: dict[str, float] = {}
    for update_name, lrs in (
        ("euclid", (0.001, 0.003, 0.01)),
        ("muon", (0.003, 0.01, 0.03)),
    ):
        results = {
            lr: _train("bptt", update_name, 0, lr, episodes=120, eval_every=60)
            for lr in lrs
        }
        best_lr = max(results, key=lambda k: results[k])
        best[update_name] = best_lr
        print(f"screen: bptt x {update_name} -> lr {best_lr:g}", flush=True)
    return best


def main() -> int:  # ruff: ignore[too-many-locals] - probe harness
    t0 = time.time()
    args = __import__("sys").argv[1:]
    opt = dict(a[2:].split("=") for a in args if a.startswith("--") and "=" in a)
    seed = int(opt["seed"]) if "seed" in opt else None
    seeds = (seed,) if seed is not None else SEEDS
    arm = opt.get("arm")
    update_name = opt.get("update")
    lr = float(opt["lr"]) if "lr" in opt else None
    episodes = int(opt.get("episodes", EPISODES))
    flags = {a.lstrip("-") for a in args}
    label_free = "label-free" in flags
    regen = "regen" in flags
    damage = "damage" in flags
    unshared = "unshared" in flags
    routing = "routing" in flags
    gate_lr_scale = float(opt.get("gate-lr-scale", 1.0))
    print(
        f"w8_nca_local {REV}; arm {arm or 'all'} seeds {seeds}"
        f"{' [label-free]' if label_free else ''}{' [regen]' if regen else ''}"
        f"{' [damage]' if damage else ''}{' [unshared]' if unshared else ''}"
        f"{' [routing]' if routing else ''}"
        f"{' [gate-lr x0.1]' if gate_lr_scale < 1.0 else ''}"
    )
    if arm is None:
        lrs = _screen()
        cells = [
            ("bptt", "euclid", lrs["euclid"]),
            ("bptt", "muon", lrs["muon"]),
            ("local", "euclid", 0.1),
            ("local", "muon", 0.1),
        ]
    else:
        if update_name is None or lr is None:
            print("usage: --arm requires --update= and --lr=")
            return 2
        cells = [(arm, update_name, lr)]
    for cell_arm, u, cell_lr in cells:
        for s_ in seeds:
            _train(
                cell_arm,
                u,
                s_,
                cell_lr,
                episodes=episodes,
                label_free=label_free,
                regen=regen,
                damage=damage,
                unshared=unshared,
                routing=routing,
                gate_lr_scale=gate_lr_scale,
            )
    print(f"\nwalltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
