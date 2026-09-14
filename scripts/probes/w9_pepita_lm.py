"""PEPITA on a causal LM (TODO15 §13.7 queue item 2).

PEPITA is validated on MNIST-MLP only (TODO15 §11.2). This cell asks
whether the input-modulation family transfers to the LM cell where the
local_contrastive family was boundary-locked (W0: best 0.190 top-1 /
3.225 CE at 600 steps, val unigram CE reference 3.30 / top-1 0.153).

Design necessity: the transformer input is DISCRETE token ids — the
modulation x̃ = x + γδBᵀ is meaningless there. The faithful adaptation
modulates the EMBEDDING OUTPUT: x̃_emb = emb(x) + γ·(δ @ B) with ONE
fixed random B (V, d_model) drawn per seed; the update stays the exact
autograd gradient of CE(f(x̃_emb), y). Everything else mirrors
pepita_faithful_replication.py (plain torch, identical budget per arm).

Arms (identical net: emb 65→128, 2-layer causal transformer, d128,
4 heads, ctx 32; batch 32; 600 steps; seeds 0-2):
  - bp/adam          (reference: w0 recorded 0.219 top-1 / 2.936 CE @3000;
                      at 600 steps expect ~0.15-0.19 / ~3.2)
  - pepita/adam γ=0.05
  - pepita/adam γ=0.1 (γ sensitivity spot-check)

Pre-registered reading: pepita within 0.03 top-1 of bp → family
transfers to LM (open); pepita at/below unigram (0.153) → the
modulation family is MLP-bound (boundary, mechanism unknown — audit
before closure).

uv run python scripts/probes/w9_pepita_lm.py
Walltime printed, never recorded.
"""

from __future__ import annotations

import argparse
import time

import torch
from torch import nn

from computronium.data.lm import get_lm_dataset

VOCAB = 65
CTX = 32
BATCH = 32
D_MODEL = 128
N_LAYERS = 2
N_HEADS = 4
STEPS = 600
LR = 1e-3
SEEDS = (0, 1, 2)
DEVICE = "cpu"


class TinyCausalTransformer(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.emb = nn.Embedding(VOCAB, D_MODEL)
        self.pos = nn.Parameter(torch.zeros(CTX, D_MODEL))
        layer = nn.TransformerEncoderLayer(
            d_model=D_MODEL,
            nhead=N_HEADS,
            dim_feedforward=D_MODEL * 4,
            batch_first=True,
            norm_first=True,
        )
        self.blocks = nn.TransformerEncoder(layer, num_layers=N_LAYERS)
        self.head = nn.Linear(D_MODEL, VOCAB)

    def forward(
        self, x: torch.Tensor, emb_noise: torch.Tensor | None = None
    ) -> torch.Tensor:
        h = self.emb(x) + self.pos[: x.size(1)]
        h = h if emb_noise is None else h + emb_noise
        mask = nn.Transformer.generate_square_subsequent_mask(x.size(1))
        h = self.blocks(h, mask=mask, is_causal=True)
        return self.head(h)


def _evaluate(net: TinyCausalTransformer, val) -> tuple[float, float]:
    """CLEAN forward — no modulation at eval. The training modulation
    consumes the target (that IS the PEPITA rule); reusing it at eval
    would inject the answer into the input (the 0.988 leak)."""
    correct = total = 0
    ce_sum = ce_n = 0.0
    with torch.no_grad():
        for x, y in val:
            flat = net(x).reshape(-1, VOCAB)
            correct += (flat.argmax(-1) == y).sum().item()
            total += y.numel()
            ce_sum += nn.functional.cross_entropy(flat, y, reduction="sum").item()
            ce_n += y.numel()
    return correct / total, ce_sum / ce_n


def _train(
    rule: str, seed: int, train_t: torch.Tensor, val, gamma: float, steps: int
) -> tuple[float, float]:
    torch.manual_seed(seed)
    net = TinyCausalTransformer()
    opt = torch.optim.Adam(net.parameters(), lr=LR)
    gen = torch.Generator().manual_seed(seed)
    b_fixed = torch.randn(VOCAB, D_MODEL, generator=gen)
    for _ in range(steps):
        idx = torch.randint(0, len(train_t) - CTX - 1, (BATCH,), generator=gen)
        wins = torch.stack([train_t[i : i + CTX + 1] for i in idx])
        x, y = wins[:, :-1], wins[:, 1:].reshape(-1)
        if rule == "bp":
            loss = nn.functional.cross_entropy(net(x).reshape(-1, VOCAB), y)
        else:
            with torch.no_grad():
                logits1 = net(x).reshape(-1, VOCAB)
                delta = nn.functional.one_hot(y, VOCAB).float() - torch.softmax(
                    logits1, dim=-1
                )
            emb_noise = gamma * (delta @ b_fixed).reshape(x.size(0), CTX, D_MODEL)
            loss = nn.functional.cross_entropy(net(x, emb_noise).reshape(-1, VOCAB), y)
        opt.zero_grad()
        loss.backward()
        opt.step()
    return _evaluate(net, val)


def main() -> int:  # noqa: PLR0914
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=STEPS)
    args = parser.parse_args()
    steps = args.steps
    t0 = time.time()
    train_ds = get_lm_dataset("tiny_shakespeare", seq_len=CTX + 1, split="train")
    val_ds = get_lm_dataset("tiny_shakespeare", seq_len=CTX + 1, split="validation")
    train_t = train_ds.data.long()
    stoi = {c: i for i, c in enumerate(sorted(set(train_ds.idx_to_char.values())))}
    val_t = torch.tensor([stoi[c] for c in val_ds.decode(val_ds.data)])
    gen = torch.Generator().manual_seed(0)
    idx = torch.randint(0, len(val_t) - CTX - 1, (512,), generator=gen)
    wins = torch.stack([val_t[i : i + CTX + 1] for i in idx])
    val = [(w[:, :-1], w[:, 1:].reshape(-1)) for w in wins.split(64)]

    accs: dict[str, list[float]] = {}
    ces: dict[str, list[float]] = {}
    for seed in SEEDS:
        for rule, gamma in (("bp", 0.0), ("pepita", 0.05), ("pepita", 0.1)):
            name = f"{rule}/adam" + ("" if rule == "bp" else f" γ={gamma}")
            acc, ce = _train(rule, seed, train_t, val, gamma, steps)
            accs.setdefault(name, []).append(acc)
            ces.setdefault(name, []).append(ce)
            print(f"seed {seed} {name:>18}: top-1 {acc:.3f}  CE {ce:.3f}", flush=True)

    print()
    for name in accs:
        m_acc = sum(accs[name]) / len(accs[name])
        m_ce = sum(ces[name]) / len(ces[name])
        print(f"{name:>18}: top-1 {m_acc:.3f}  CE {m_ce:.3f}", flush=True)
    print(
        "\nreference (w0 @600): bp 0.219/2.936 @3000, ~0.15/3.2 @600; "
        "unigram 0.153/3.30",
        flush=True,
    )
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
