"""W8 ordinary-task cell (TODO15 §17 breadth): NTM as a plain classifier.

The W8 program measured local credit only on algorithmic memory tasks
(copy, repeat-copy). This probe asks the transfer question: does the
r6 content-addressed-memory recipe do an ORDINARY supervised task —
static image classification — when the task never references memory
semantics? MNIST rows are a 28-step sequence; classification is read
off the final [h; read] state.

Arms (matched net/optimizer/budget, seeds 0-2):
  - bptt: full-graph episode, CE at the final step (gold control).
  - local: zero-history factorization — state/memory detached every
    step; the controller receives per-step label CE on a shared readout
    over [h_t; read_t] (deep supervision replaces the missing
    cross-step transport); the writer keeps the r6 position supervision
    (a_w -> slot t) so memory holds an ordered trace; NO content
    target (the task defines none — memory must earn its keep or the
    readout just ignores the read vector; the bptt-vs-local delta then
    measures what the transport itself was worth).

Pre-registered readings:
  - local within ~0.03 of bptt -> the r6 recipe transfers to ordinary
    tasks; memory-task results were not an algorithmic-task artifact.
  - local far below bptt -> the factorization needs task-shaped
    per-step targets (the copy recipe's content/KL losses) and does
    not survive their removal; that is the boundary.
  - P-axis composition (FastWeightPlasticity on the controller) is the
    QUEUED next rung, rung-paired with this baseline.

uv run python scripts/probes/w8_ordinary_task.py [--arm=...] [--steps=N]
Walltime printed, never recorded.
"""

from __future__ import annotations

import sys
import time
from itertools import islice

import torch
from torch import Tensor, nn

from computronium import create_task

HIDDEN = 64
MEM_SLOTS = 16
MEM_WIDTH = 16  # slots <= width: exact one-hot slot identities (Q4 fix)
SEQ = 28
CLASSES = 10
BATCH = 64


class BudgetError(RuntimeError):
    MSG = "training budget not honored by the data loader"
    """Training budget not honored by the data loader (§17.5 hazard)."""


def _data(task_name: str = "mnist"):
    task = create_task(task_name, device="cpu", quick_mode=True, num_workers=0)
    task.setup()
    raw = list(islice(task.get_dataloader("train"), 600))
    train = [(x.view(x.size(0), SEQ, -1), y) for x, y in raw]
    test = [(x.view(x.size(0), SEQ, -1), y) for x, y in task.get_dataloader("test")][
        :50
    ]
    # Small-dataset hazard (TODO15 §14.1): the loader caps the budget —
    # cycle so any --steps ask is honored, and assert it was.
    cycled = [train[i % len(train)] for i in range(4800)]
    if len(cycled) < 4800 or len(cycled) < len(train):
        raise BudgetError(BudgetError.MSG)
    return cycled, test


def _zero_mem(batch: int) -> Tensor:
    mem = torch.zeros(batch, MEM_SLOTS, MEM_WIDTH)
    for s in range(MEM_SLOTS):
        mem[:, s, s % MEM_WIDTH] = 0.5
    return mem


class _Heads(nn.Module):
    """r6-style heads: content addressing, erase+add write, class head."""

    def __init__(self, in_dim: int) -> None:
        super().__init__()
        self.kr = nn.Linear(HIDDEN, MEM_WIDTH)
        self.kw = nn.Linear(HIDDEN, MEM_WIDTH)
        self.add = nn.Linear(HIDDEN, MEM_WIDTH)
        self.erase = nn.Linear(HIDDEN, MEM_WIDTH)
        self.out = nn.Linear(HIDDEN + MEM_WIDTH, CLASSES)
        self.beta = nn.Parameter(torch.tensor(10.0))

    def forward(self, h: Tensor, mem: Tensor):
        cos = torch.nn.functional.cosine_similarity(
            mem, self.kr(h).unsqueeze(1).expand_as(mem), dim=-1
        )
        a_r = torch.softmax(self.beta * cos, dim=-1)
        read = torch.einsum("bs,bsw->bw", a_r, mem)
        a_w = torch.softmax(
            self.beta
            * torch.cosine_similarity(
                mem, self.kw(h).unsqueeze(1).expand_as(mem), dim=-1
            ),
            dim=-1,
        )
        add_v = torch.tanh(self.add(h))
        erase_v = torch.sigmoid(self.erase(h))
        mem_next = mem * (1 - a_w.unsqueeze(2) * erase_v.unsqueeze(1)) + (
            a_w.unsqueeze(2) * add_v.unsqueeze(1)
        )
        return read, mem_next, a_w


class _FastHeads(nn.Module):
    """§17.8 single-tensor arm: the memory is a fast-weight matrix A
    written by a FIXED Hebbian rule (A ← decay·A + outer(v, q)) through
    FIXED random projections of h — no learned write head, no learned
    addressing; the only trainable module is the final classifier. The
    controller still receives credit through the read (gradients flow
    via h), isolating exactly the write-rule variable: credit-shaped
    learned writes (bptt) vs a credit-free fixed rule at matched
    substrate and budget."""

    DK = 32

    def __init__(self) -> None:
        super().__init__()
        gen = torch.Generator().manual_seed(1234)
        self.fv = nn.Buffer(torch.randn(HIDDEN, self.DK, generator=gen) / HIDDEN**0.5)
        self.fq = nn.Buffer(torch.randn(HIDDEN, self.DK, generator=gen) / HIDDEN**0.5)
        self.out = nn.Linear(HIDDEN + self.DK, CLASSES)

    def forward(self, h: Tensor, a: Tensor):
        v = torch.tanh(h @ self.fv)  # value written
        q = torch.tanh(h @ self.fq)  # query
        read = torch.bmm(q.unsqueeze(1), a.transpose(1, 2)).squeeze(1)
        a_next = self._DECAY * a + torch.bmm(v.unsqueeze(2), q.unsqueeze(1))
        return read, a_next

    _DECAY = 0.95


def _fast_episode(controller, fast: _FastHeads, rows: Tensor):
    B = rows.size(0)
    a = torch.zeros(B, _FastHeads.DK, _FastHeads.DK)
    state = (torch.zeros(1, B, HIDDEN), torch.zeros(1, B, HIDDEN))
    prev = torch.zeros(B, _FastHeads.DK)
    for t in range(SEQ):
        x_t = torch.cat([rows[:, t], prev], dim=-1).unsqueeze(1)
        hc, state = controller(x_t, state)
        h = hc.squeeze(1)
        read, a = fast(h, a)
        prev = read
    logits = fast.out(torch.cat([h, read], dim=-1))
    return logits


def _fast_eval(controller, fast: _FastHeads, test, ablate: bool = False) -> float:
    ok = tot = 0
    with torch.no_grad():
        for rrow, ry in test:
            B = rrow.size(0)
            a = torch.zeros(B, _FastHeads.DK, _FastHeads.DK)
            state = (torch.zeros(1, B, HIDDEN), torch.zeros(1, B, HIDDEN))
            prev = torch.zeros(B, _FastHeads.DK)
            for t in range(SEQ):
                x_t = torch.cat([rrow[:, t], prev], dim=-1).unsqueeze(1)
                hc, state = controller(x_t, state)
                h = hc.squeeze(1)
                read, a = fast(h, a)
                prev = read
            read *= 0.0 if ablate else 1.0
            lg = fast.out(torch.cat([h, read], dim=-1))
            ok += (lg.argmax(1) == ry).sum().item()
            tot += ry.size(0)
    return ok / tot


def _run_hebbian(steps: int, lr: float, seed: int, train, test) -> float:
    torch.manual_seed(seed)
    controller = nn.LSTM(SEQ + _FastHeads.DK, HIDDEN, batch_first=True)
    fast = _FastHeads()
    params = [*controller.parameters(), *fast.parameters()]
    opt = torch.optim.Adam(params, lr=lr)
    best = 0.0
    for step, (rows, y) in enumerate(islice(train, steps)):
        logits = _fast_episode(controller, fast, rows)
        loss = nn.functional.cross_entropy(logits, y)
        opt.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(params, 5.0)
        opt.step()
        if step >= len(train):
            raise BudgetError(BudgetError.MSG)
        if (step + 1) % max(steps // 5, 1) == 0:
            acc = _fast_eval(controller, fast, test)
            ablated = _fast_eval(controller, fast, test, ablate=True)
            best = max(best, acc)
            print(
                f"hebbian step {step + 1}: loss {loss:.4f} acc(fresh) {acc:.3f} "
                f"[A-ablated {ablated:.3f}]",
                flush=True,
            )
    return best


def _episode(controller, heads: _Heads, rows: Tensor):
    """One episode; returns per-step (h, read) and the final logits."""
    B = rows.size(0)
    mem = _zero_mem(B)
    state = (torch.zeros(1, B, HIDDEN), torch.zeros(1, B, HIDDEN))
    hs, reads = [], []
    prev = torch.zeros(B, MEM_WIDTH)
    for t in range(SEQ):
        x_t = torch.cat([rows[:, t], prev], dim=-1).unsqueeze(1)
        hc, state = controller(x_t, state)
        h = hc.squeeze(1)
        read, mem_next, _aw = heads(h, mem)
        hs.append(h)
        reads.append(read)
        prev = read
        mem = mem_next
    logits = heads.out(torch.cat([hs[-1], reads[-1]], dim=-1))
    return hs, reads, logits


def _run_bptt(steps: int, lr: float, seed: int, train, test) -> float:
    torch.manual_seed(seed)
    controller = nn.LSTM(SEQ + MEM_WIDTH, HIDDEN, batch_first=True)
    heads = _Heads(SEQ + MEM_WIDTH)
    params = [*controller.parameters(), *heads.parameters()]
    opt = torch.optim.Adam(params, lr=lr)
    best = 0.0
    for step, (rows, y) in enumerate(islice(train, steps)):
        *_, logits = _episode(controller, heads, rows)
        loss = nn.functional.cross_entropy(logits, y)
        opt.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(params, 5.0)
        opt.step()
        if (step + 1) % max(steps // 5, 1) == 0:
            acc = _eval(controller, heads, test)
            best = max(best, acc)
            print(
                f"bptt step {step + 1}: loss {loss:.4f} acc(fresh) {acc:.3f}",
                flush=True,
            )
    return best


@torch.no_grad()
def _eval(controller, heads: _Heads, test) -> float:
    ok = tot = 0
    for rows, y in test:
        *_, logits = _episode(controller, heads, rows)
        ok += (logits.argmax(1) == y).sum().item()
        tot += y.size(0)
    return ok / tot


def _local_episode(controller, heads: _Heads, rows: Tensor, y: Tensor) -> Tensor:
    """Zero-history per-step losses: detached (h_t, read_t) -> shared
    readout CE against the episode label; writer keeps position
    supervision (a_w -> slot t). No tensor carries grad across steps."""
    B = rows.size(0)
    mem = _zero_mem(B)
    state = (torch.zeros(1, B, HIDDEN), torch.zeros(1, B, HIDDEN))
    losses = []
    prev = torch.zeros(B, MEM_WIDTH)
    for t in range(SEQ):
        x_t = torch.cat([rows[:, t], prev.detach()], dim=-1).unsqueeze(1)
        hc, state_new = controller(x_t, (state[0].detach(), state[1].detach()))
        h = hc.squeeze(1)
        read, mem_next, a_w = heads(h, mem.detach())
        logits = heads.out(torch.cat([h.detach(), read], dim=-1))
        losses.append(nn.functional.cross_entropy(logits, y))
        target_a = torch.zeros(B, MEM_SLOTS)
        target_a[:, t % MEM_SLOTS] = 1.0
        losses.append((a_w - target_a).pow(2).sum(-1).mean())
        state, mem, prev = state_new, mem_next.detach(), read.detach()
    return torch.stack(losses).mean()


def _run_local(steps: int, lr: float, seed: int, train, test) -> float:
    torch.manual_seed(seed)
    controller = nn.LSTM(SEQ + MEM_WIDTH, HIDDEN, batch_first=True)
    heads = _Heads(SEQ + MEM_WIDTH)
    params = [*controller.parameters(), *heads.parameters()]
    opt = torch.optim.Adam(params, lr=lr)
    best = 0.0
    for step, (rows, y) in enumerate(islice(train, steps)):
        loss = _local_episode(controller, heads, rows, y)
        opt.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(params, 5.0)
        opt.step()
        if step >= len(train):
            raise BudgetError(BudgetError.MSG)
        if (step + 1) % max(steps // 5, 1) == 0:
            acc = _eval(controller, heads, test)
            best = max(best, acc)
            print(
                f"local step {step + 1}: loss {loss:.4f} acc(fresh) {acc:.3f}",
                flush=True,
            )
    return best


def _run_lstm(steps: int, lr: float, seed: int, train, test) -> float:
    """No-memory control (§17.9 queue): same controller reading the row
    sequence, plain final-state classifier — isolates what the memory
    trace contributes over a plain recurrent encoder."""
    torch.manual_seed(seed)
    controller = nn.LSTM(SEQ, HIDDEN, batch_first=True)
    head = nn.Linear(HIDDEN, CLASSES)
    params = [*controller.parameters(), *head.parameters()]
    opt = torch.optim.Adam(params, lr=lr)
    best = 0.0

    def eval_fn() -> float:
        ok = tot = 0
        with torch.no_grad():
            for rrow, ry in test:
                _out, (hn, _cn) = controller(rrow)
                lg = head(hn[-1])
                ok += (lg.argmax(1) == ry).sum().item()
                tot += ry.size(0)
        return ok / tot

    for step, (rrow, y) in enumerate(islice(train, steps)):
        _out, (hn, _cn) = controller(rrow)
        loss = nn.functional.cross_entropy(head(hn[-1]), y)
        opt.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(params, 5.0)
        opt.step()
        if (step + 1) % max(steps // 5, 1) == 0:
            acc = eval_fn()
            best = max(best, acc)
            print(
                f"lstm step {step + 1}: loss {loss:.4f} acc(fresh) {acc:.3f}",
                flush=True,
            )
    return best


def main() -> int:
    t0 = time.time()
    args = sys.argv[1:]
    opt = dict(a[2:].split("=") for a in args if a.startswith("--") and "=" in a)
    steps = int(opt.get("steps", 600))
    lr = float(opt.get("lr", 1e-3))
    seeds = (int(opt["seed"]),) if "seed" in opt else (0, 1, 2)
    arms = [opt["arm"]] if "arm" in opt else ["bptt", "local"]
    train, test = _data(opt.get("task", "mnist"))
    run = {
        "bptt": _run_bptt,
        "local": _run_local,
        "hebbian": _run_hebbian,
        "lstm": _run_lstm,
    }
    results: dict[str, list[float]] = {}
    for arm in arms:
        for seed in seeds:
            print(f"=== {arm} seed {seed} ({steps} steps, lr {lr:g}) ===", flush=True)
            results.setdefault(arm, []).append(run[arm](steps, lr, seed, train, test))
    for arm, accs in results.items():
        mean = sum(accs) / len(accs)
        print(f"{arm:>6}: mean {mean:.3f}  {[f'{a:.3f}' for a in accs]}", flush=True)
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
