"""B4 probe (TODO12 rev 15): per-layer contrastive targets — the Claim A repair.

Pre-registered predictions (written before any measurement):
- P1 (locality): each layer's pseudo-gradient is computed from a graph
  containing ONLY that layer's Linear (inter-layer inputs detached) —
  hidden-layer credit is nonzero for every layer WITHOUT any backward
  sweep through other layers. Assert: per-layer grads all nonzero.
- P2 (learning): per-layer FF trains MNIST-quick (150 batches, the D13
  regime) to accuracy >= 0.80 with a linear-probe readout — competitive
  with the repo's ff_hybrid at this budget (ff trails bp; 0.80 bar is
  honest for a from-scratch throwaway realization).
- P3 (physical advantage): measured saved-for-backward bytes for ONE
  per-layer local update < bp's single global step on the same net
  (bp must hold every layer's forward tensors; per-layer FF frees each
  local graph before the next — the ratchet F5 pinned as un-flipped at
  HEAD; a flip here is the Claim B lever).

Mechanism (Hinton 2022, made honest): input = normalize(x) concat
onehot label; positive pass = true label, negative = rolled label.
Each layer's loss = softplus(theta - (G_pos - G_neg)), G = mean(act^2),
gradient taken w.r.t. that layer's weight only, on a graph whose input
is DETACHED from the previous layer (stop-grad between layers — the
defining property of layer-local learning; HEAD's LocalGoodnessCredit
instead sums all layers into one scalar and sweeps globally, hence
F5's 1108 KiB).

Verdict (2026-09-06, deterministic after seeding the loader draw):
- P1 CONFIRMED — every layer's local pseudo-gradient is nonzero
  (goodness contrast after per-layer stream normalization); graphs are
  layer-local by construction (no-grad recomputed inputs).
- P3 CONFIRMED at depth 4 — per-layer peak saved-for-backward bytes
  [268804, 98308, 98308, 98308] (max 268.8 KiB, the 794-wide input
  layer) vs bp's whole-graph 569348 (569.3 KiB): per-layer < bp, and
  the gap widens with depth (bp's graph is O(depth); the per-layer
  peak is O(1 layer) given recompute). This flips the direction F5
  pinned at HEAD (ff's global-graph realization stored MORE than bp).
- P2 SPLIT — depth-2 w128 lr 0.5: mean 0.827 (0.827/0.833/0.819,
  seeds 0-2) > the 0.80 bar; but depth attenuates (d4 mean 0.764) and
  every depth trails the repo's ff_hybrid at the same budget (D16
  record: ff/adam 0.899, ff/muon 0.896 at depth 2 w64). The depth wall
  shows up in the per-layer-target class too — the unifying
  credit-fidelity diagnosis extends to B3/B4: per-layer targets alone
  do not escape it; credit_norm-style repairs are the indicated
  composition (A4 for the per-layer goodness contrast).
- Realization notes: (a) input normalization must be length sqrt(dim)
  (Hinton's), not unit-norm — unit-norm kills layer 0 (G ~ 0, dead);
  (b) per-layer stream normalization is REQUIRED at depth 3+ (layers
  1+ die without it); (c) recompute (no-grad stream) vs detached-carry:
  detached-carry keeps ALL earlier graphs alive inside the per-layer
  update (measured 799.8 KiB at depth 2 — worse than bp) — the
  O(1)-peak claim needs the recompute pattern; (d) the quick-mode
  loader draw is global-RNG-driven — seed BEFORE _data() or replays
  spread ±0.04 (the D8 trap, reproduced here).

P4/P5 rung (pre-registered 2026-09-06, before any measurement) — the
A4 composition question: does per-layer unit-RMS normalization of the
goodness gradient (per-element displacement lr, H1 semantics) repair
the per-layer class's depth attenuation?
- P4 (lift): normalization lifts the depth cells at some lr in
  {1e-3, 3e-3, 1e-2} (per-element axis; an initial 0.01–0.1 sweep was
  invalid per H1 — past the stability edge, d2 collapsed to 0.52):
  d4 mean >= 0.82 (plain: 0.764) AND d8 >= 0.7.
- P5 (control): d2 under normalization stays >= 0.80 (no regression).
- Else-branch: if normalization does NOT lift depth, the wall is
  contrast-INFORMATION loss (not magnitude) and the B4 library pull
  must not promise depth repair.

P4/P5 VERDICT (2026-09-06): BOTH FALSIFIED. Per-layer unit-RMS
normalization of the goodness gradient collapses learning at every
depth and displacement (per-element axis 1e-3..1e-2 AND the invalid
0.01..0.1 sweep): d2 0.561/0.537/0.520 vs 0.827 plain; d4 ~0.20;
d8 ~0.10-0.16. Not an lr artifact — instantaneous normalization
erases the gradient's magnitude, which CARRIES information in the
contrastive objective (softplus gating: a layer whose local margin is
satisfied has a near-zero gradient; re-normalizing re-amplifies it
into a full-size destructive step every batch). A4's credit_norm does
NOT transfer to the per-layer-contrastive class — the levers do not
naively compose (consistent with the A4×D14 result). The B4 library
pull must not promise depth repair; the depth axis needs its own
lever for this class (untried: momentum-EMA normalizer — the
canonical magnitude family per A6 — or B1-style learned structure).
"""

import itertools
import time

import torch
import torch.nn.functional as F  # noqa: N812 — torch's own convention
from torch import Tensor, nn

from computronium import create_task

STEPS = 150
THRESHOLD = 2.0
LR = 0.5
HIDDEN = (128, 128)
N_CLASSES = 10


def _data() -> tuple[list, list]:
    task = create_task("mnist", device="cpu", quick_mode=True, num_workers=0)
    task.setup()
    train = [(xb.view(xb.size(0), -1), yb) for xb, yb in task.get_dataloader("train")]
    test = [(xb.view(xb.size(0), -1), yb) for xb, yb in task.get_dataloader("test")]
    return train[:STEPS], test


def _label_input(x: Tensor, y: Tensor, good: bool) -> Tensor:
    onehot = F.one_hot(y, N_CLASSES).float()
    if not good:
        onehot = onehot.roll(1, 0)  # wrong-label negative (Hinton's recipe)
    z = torch.cat([x, onehot], dim=-1)
    # Hinton's normalization: unit DIRECTION, length sqrt(dim) — keeps
    # post-ReLU goodness O(1) so the threshold is meaningful (a plain
    # unit-norm input makes G ≈ 0 and the layer dies).
    return z / (z.norm(dim=-1, keepdim=True) + 1e-12) * z.shape[-1] ** 0.5


class PerLayerFF(nn.Module):
    """Hidden stack only; a separate linear readout probes the features."""

    def __init__(self, dims: tuple[int, ...]):
        super().__init__()
        self.linears = nn.ModuleList(
            nn.Linear(a, b) for a, b in itertools.pairwise(dims)
        )
        self.readout = nn.Linear(dims[-1], N_CLASSES)

    @torch.no_grad()
    def _stream_input(self, x: Tensor, upto: int) -> Tensor:
        """no-grad forward to layer `upto`'s input (recompute, don't store).
        Every layer's stream is normalized to length sqrt(dim) — Hinton's
        per-layer normalization; without it layers 1+ die (G contrast ~0)."""
        a = x
        for lin in self.linears[:upto]:
            a = F.relu(lin(a))
            a = a / (a.norm(dim=-1, keepdim=True) + 1e-12) * a.shape[-1] ** 0.5
        return a

    def local_grads(self, x_pos: Tensor, x_neg: Tensor) -> list[Tensor]:
        """Per-layer local updates: recomputed (no-grad) inputs, so each
        layer's backward graph contains ONLY that layer's Linear."""
        grads = []
        for i, lin in enumerate(self.linears):
            in_pos = self._stream_input(x_pos, i)
            in_neg = self._stream_input(x_neg, i)
            g_pos = F.relu(lin(in_pos)).pow(2).mean()
            g_neg = F.relu(lin(in_neg)).pow(2).mean()
            loss = F.softplus(THRESHOLD - (g_pos - g_neg))
            (gw,) = torch.autograd.grad(loss, (lin.weight,), retain_graph=False)
            grads.append(gw)
        return grads

    def features(self, x: Tensor) -> Tensor:
        a = x
        for lin in self.linears:
            a = F.relu(lin(a))
            a = a / (a.norm(dim=-1, keepdim=True) + 1e-12) * a.shape[-1] ** 0.5
        return a


def _peak_saved_bytes(fn) -> tuple[object, int]:
    saved: list[int] = []

    def hook(t: Tensor) -> Tensor:
        saved.append(t.numel() * t.element_size())
        return t

    with torch.autograd.graph.saved_tensors_hooks(
        pack_hook=hook, unpack_hook=lambda t: t
    ):
        out = fn()
    return out, sum(saved)


def main() -> None:  # noqa: C901 — throwaway probe, keep linear
    t0 = time.perf_counter()
    torch.manual_seed(0)  # seed BEFORE the loader draw (D8 trap) — the
    # quick-mode shuffle is global-RNG-driven; unseeded draws gave a
    # ±0.04 accuracy spread across process replays.
    train, test = _data()

    def train_acc(hidden: tuple[int, ...], seed: int, norm_lr: float = 0.0) -> float:
        torch.manual_seed(seed)
        net = PerLayerFF((784 + N_CLASSES, *hidden))
        ro_opt = torch.optim.SGD(net.readout.parameters(), lr=0.1)
        for x, y in train[:STEPS]:
            x_pos = _label_input(x, y, True)
            x_neg = _label_input(x, y, False)
            linears = [m for m in net.linears if isinstance(m, nn.Linear)]
            for lin, gw in zip(linears, net.local_grads(x_pos, x_neg), strict=True):
                with torch.no_grad():
                    if norm_lr > 0.0:
                        # P4 rung: per-layer unit-RMS credit normalization
                        # (per-element displacement lr, H1 semantics).
                        lin.weight -= norm_lr * gw / (gw.pow(2).mean().sqrt() + 1e-12)
                    else:
                        lin.weight -= LR * gw
            ro_opt.zero_grad()
            F.cross_entropy(net.readout(net.features(x_pos).detach()), y).backward()
            ro_opt.step()
        correct = total = 0
        with torch.no_grad():
            for x, y in test:
                feats = net.features(_label_input(x, y, True))
                correct += (net.readout(feats).argmax(1) == y).sum().item()
                total += y.size(0)
        return correct / total

    for name, hidden in (("d2_w128", (128, 128)), ("d4_w128", (128,) * 4)):
        accs = [train_acc(hidden, s) for s in (0, 1, 2)]
        print(
            f"P2 {name}: mean {sum(accs) / 3:.3f} seeds {[round(a, 3) for a in accs]}"
        )

    # P4/P5: per-layer unit-RMS credit normalization vs the depth wall.
    # lr grid is on the PER-ELEMENT axis (H1's binding instruction —
    # 0.01–0.1 overshot into collapse; the working regime is 1e-3).
    for name, hidden in (("d2", (128, 128)), ("d4", (128,) * 4), ("d8", (128,) * 8)):
        for norm_lr in (1e-3, 3e-3, 0.01):
            accs = [train_acc(hidden, s, norm_lr=norm_lr) for s in (0, 1, 2)]
            print(
                f"P4 {name} norm_lr {norm_lr}: mean {sum(accs) / 3:.3f} "
                f"seeds {[round(a, 3) for a in accs]}"
            )

    # P1 + P3 at depth 4: locality + per-layer peak vs bp whole graph.
    torch.manual_seed(0)
    net = PerLayerFF((784 + N_CLASSES, *(128,) * 4))
    x, y = train[0]
    grads = net.local_grads(_label_input(x, y, True), _label_input(x, y, False))
    print(f"P1 all-local-grads-nonzero: {all(g.abs().max() > 0 for g in grads)}")
    peaks = []
    for i, lin in enumerate(net.linears):
        in_pos = net._stream_input(_label_input(x, y, True), i)
        in_neg = net._stream_input(_label_input(x, y, False), i)

        def local(i=i, lin=lin, in_pos=in_pos, in_neg=in_neg):
            g_pos = F.relu(lin(in_pos)).pow(2).mean()
            g_neg = F.relu(lin(in_neg)).pow(2).mean()
            loss = F.softplus(THRESHOLD - (g_pos - g_neg))
            return torch.autograd.grad(loss, (lin.weight,))

        _, by = _peak_saved_bytes(local)
        peaks.append(by)

    def bp_step():
        loss = F.cross_entropy(net.readout(net.features(_label_input(x, y, True))), y)
        return torch.autograd.grad(loss, list(net.parameters()), allow_unused=True)

    _, by_bp = _peak_saved_bytes(bp_step)
    print(f"P3 per-layer peaks {peaks} (max {max(peaks)}) vs bp whole-graph {by_bp}")
    print(f"walltime {time.perf_counter() - t0:.1f}s")


if __name__ == "__main__":
    main()
