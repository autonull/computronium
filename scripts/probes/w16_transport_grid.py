"""TODO16 §6.1 reduced transport-graph grid: fixed-write memory types on
the associative-recall rung (explicit keys), matched to the recorded
sparse-addressed (NTM) datapoint.

Question (§6.1): at what retrieval demand does learned addressing
reassert itself over fixed writes? The sparse-addressed arm is ALREADY
measured — w8_ntm_copy local3 recall 3-seed acc_given_hit 0.625-0.646
(§5.4, logs/w16_recall_levers_s*.log) and bptt recall is the recorded
control. This probe supplies the three fixed-write cells:

  hebbian_dense   decayed outer-product trace, FIXED random +/-1 key
                  projections (dense addressing), linear read r = M k
  slot_capped     one-hot slot addressing (exact), direct value slot
                  read
  linear_read     non-decaying key/value sum, normalized linear
                  attention read r = M k / (1 + |k|^2) (linear-transformer
                  read with fixed projections)

Task: identical to w8_ntm_copy recall — L=6, input step t carries
(value bit, one-hot key perm[t]); output step k is cued on key k and
must emit the value bound to it. One perm per episode (batch-wide).

Training: zero-history local CE on out([h; r]) — state and memory
detached at every timestep boundary (same factorization discipline as
the local arms); the write rules are FIXED (parameter-free), so the
only trained modules are the controller LSTM and the output head.

Pre-registered:
- All three fixed-write types >= 0.90 bit-accuracy on explicit-key
  recall: with explicit keys the transport graph suffices and learned
  addressing is unnecessary at this retrieval demand (predicts fixed
  writes STRICTLY DOMINATE the recorded NTM 0.63).
- Falsification: any fixed-write type < 0.85 -> the fixed graph is
  insufficient even with explicit keys; learned addressing carries
  irreplaceable capacity.

Run: uv run python scripts/probes/w16_transport_grid.py [--types=...] [--steps=N] [--seeds=K]
Walltime printed, never recorded.
"""

import argparse

import torch
from torch import Tensor, nn

L = 6
HIDDEN = 32
BATCH = 16
IN_DIM = 1 + L

KEY_VECS = torch.randn(L, L)  # fixed random +/--ish dense key projections
KEY_VECS = KEY_VECS.sign()  # ±1 dense keys, fixed for the whole probe


def _draw_perm(batch: int, gen: torch.Generator) -> Tensor:
    return torch.randperm(L, generator=gen).unsqueeze(0).expand(batch, L)


def _episode_inputs(bits: Tensor, perm: Tensor) -> tuple[Tensor, Tensor]:
    """Input sequence [B, T, IN_DIM] + output targets [B, T]."""
    B = bits.size(0)
    T = 2 * L + 1
    x = torch.zeros(B, T, IN_DIM)
    tg = torch.full((B, T), -100, dtype=torch.long)
    x[:, :L, 0] = bits.float()
    for t in range(L):
        x[:, t, 1 + perm[0, t]] = 1.0
    for k in range(L):
        x[:, L + 1 + k, 1 + k] = 1.0
        inv = perm.argsort(1)
        tg[:, L + 1 + k] = bits.gather(1, inv[:, k : k + 1]).squeeze(1)
    return x, tg


def _key_vec(slot: int) -> Tensor:
    """One-hot base key for slot ``slot`` (cue k = key k = slot k)."""
    k = torch.zeros(1, L)
    k[0, slot] = 1.0
    return k


class _DenseMemory:
    """Shared fixed-write memory interface: write(h, kv, bit), read(kv)."""

    def reset(self, batch: int) -> None: ...

    def write(self, h: Tensor, kv: Tensor, bit: Tensor) -> None: ...

    def read(self, kv: Tensor) -> Tensor:
        raise NotImplementedError


class _HebbianDense(_DenseMemory):
    """M [B, HIDDEN, L]: decayed outer-product trace of h onto FIXED ±1
    dense projections of the one-hot keys (dense addressing)."""

    def __init__(self, decay: float = 0.9) -> None:
        self.decay = decay
        self.M = torch.zeros(1)

    def reset(self, batch: int) -> None:
        self.M = torch.zeros(batch, HIDDEN, L)

    def _dense(self, kv: Tensor) -> Tensor:
        return kv @ KEY_VECS

    def write(self, h: Tensor, kv: Tensor, bit: Tensor) -> None:
        self.M = self.decay * self.M + torch.einsum(
            "bh,bl->bhl", h.detach(), self._dense(kv).detach()
        )

    def read(self, kv: Tensor) -> Tensor:
        return torch.einsum("bhl,bl->bh", self.M, self._dense(kv).detach())


class _SlotCapped(_DenseMemory):
    """Exact slot table: mem[b, slot, 2] = (bit, 1). Read = slot lookup."""

    def __init__(self) -> None:
        self.mem = torch.zeros(1)

    def reset(self, batch: int) -> None:
        self.mem = torch.zeros(batch, L, 2)

    def write(self, h: Tensor, kv: Tensor, bit: Tensor) -> None:
        slot = int(kv.argmax())
        self.mem[:, slot, 0] = bit.detach().float()
        self.mem[:, slot, 1] = 1.0

    def read(self, kv: Tensor) -> Tensor:
        slot = int(kv.argmax())
        return self.mem[:, slot, :].reshape(-1, 2)


class _LinearRead(_DenseMemory):
    """M [B, 2, L]: non-decaying (value, count) sum; normalized linear
    attention read r = M k / (1 + k.k)."""

    def __init__(self) -> None:
        self.M = torch.zeros(1)

    def reset(self, batch: int) -> None:
        self.M = torch.zeros(batch, 2, L)

    def write(self, h: Tensor, kv: Tensor, bit: Tensor) -> None:
        self.M += torch.einsum(
            "bv,bl->bvl",
            torch.stack([bit.detach().float(), torch.ones_like(bit).float()], 1),
            kv.detach(),
        )

    def read(self, kv: Tensor) -> Tensor:
        k = kv.detach()
        return torch.einsum("bvl,bl->bv", self.M, k) / (
            1.0 + k.pow(2).sum(-1, keepdim=True)
        )


def _episode(controller, out_head, memory, bits, perm):
    """Zero-history local episode: per output step CE on out([h; r])."""
    x, tg = _episode_inputs(bits, perm)
    B = bits.size(0)
    state = (torch.zeros(1, B, HIDDEN), torch.zeros(1, B, HIDDEN))
    losses = []
    memory.reset(B)
    for t in range(2 * L + 1):
        hc, state = controller(x[:, t : t + 1], (state[0].detach(), state[1].detach()))
        h = hc.squeeze(1)
        if t < L:
            memory.write(h, _key_vec(int(perm[0, t])), bits[:, t])
        elif t >= L + 1:
            r = memory.read(_key_vec(t - L - 1))
            logits = out_head(torch.cat([h.detach(), r.detach()], dim=-1))
            losses.append(nn.functional.cross_entropy(logits, tg[:, t]))
    return torch.stack(losses).mean()


@torch.no_grad()
def _eval_acc(controller, out_head, memory, bits, perm) -> float:
    B = bits.size(0)
    state = (torch.zeros(1, B, HIDDEN), torch.zeros(1, B, HIDDEN))
    memory.reset(B)
    x, tg = _episode_inputs(bits, perm)
    correct = total = 0
    for t in range(2 * L + 1):
        hc, state = controller(x[:, t : t + 1], state)
        h = hc.squeeze(1)
        if t < L:
            memory.write(h, _key_vec(int(perm[0, t])), bits[:, t])
        elif t >= L + 1:
            r = memory.read(_key_vec(t - L - 1))
            pred = out_head(torch.cat([h, r], dim=-1)).argmax(-1)
            correct += (pred == tg[:, t]).sum().item()
            total += B
    return correct / total


MEMORIES = {
    "hebbian_dense": _HebbianDense,
    "slot_capped": _SlotCapped,
    "linear_read": _LinearRead,
}


def _run_type(name: str, steps: int, lr: float, seed: int, decay: float = 0.9) -> float:
    torch.manual_seed(seed)
    controller = nn.LSTM(IN_DIM, HIDDEN, batch_first=True)
    read_dim = 2 if name != "hebbian_dense" else HIDDEN
    out_head = nn.Linear(HIDDEN + read_dim, 2)
    params = list(controller.parameters()) + list(out_head.parameters())
    opt = torch.optim.Adam(params, lr=lr)
    gen = torch.Generator().manual_seed(7)
    eval_bits = torch.randint(
        0, 2, (BATCH, L), generator=torch.Generator().manual_seed(999)
    )
    eval_perm = _draw_perm(BATCH, torch.Generator().manual_seed(999))
    best = 0.0
    for step in range(steps):
        bits = torch.randint(0, 2, (BATCH, L), generator=gen)
        perm = _draw_perm(BATCH, gen)
        memory = (
            MEMORIES[name](decay=decay) if name == "hebbian_dense" else MEMORIES[name]()
        )
        loss = _episode(controller, out_head, memory, bits, perm)
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(params, 5.0)
        opt.step()
        if (step + 1) % max(steps // 4, 1) == 0:
            best = max(
                best,
                _eval_acc(controller, out_head, MEMORIES[name](), eval_bits, eval_perm),
            )
            print(
                f"{name} seed {seed} step {step + 1}: loss {float(loss):.4f} acc(fresh) {best:.3f}",
                flush=True,
            )
    return best


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--types", nargs="+", default=list(MEMORIES))
    ap.add_argument("--steps", type=int, default=1200)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--decay", type=float, default=0.9)
    args = ap.parse_args()

    results: dict[str, list[float]] = {}
    for name in args.types:
        results[name] = [
            _run_type(name, args.steps, args.lr, s) for s in range(args.seeds)
        ]
    print("\n=== §6.1 fixed-write recall grid (bit-acc, fresh eval) ===")
    for name, accs in results.items():
        mean = sum(accs) / len(accs)
        print(f"{name:>14}: {'/'.join(f'{a:.3f}' for a in accs)} mean {mean:.3f}")
    print(
        "reference (recorded): NTM local3 recall acc_given_hit 0.625-0.646; bptt recall control in logs/w16_recall_levers_s*.log"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
