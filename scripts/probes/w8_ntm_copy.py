"""W8.5 minimal NTM copy probe (TODO.ntm_nca.md §6): the memory stress
test, first cell.

NOTE (scope): §6 gates NTM on a W8.1-W8.3 result; this cell opens early
by explicit user directive (2026-09-07). The first decisive fact is
whether the gold-standard BPTT control learns copy at CPU probe budget
— §9 requires that control at every cell, and the local factorization
is meaningless until it exists.

Architecture (deliberately small):
  input char -> LSTM controller (hidden 32) -> {read head, write head}
  -> external memory (N x W, content-addressed cosine softmax) -> output
  head on [h; r]. Write = erase+add with sigmoid erase. No controller
  fancy addressing (no shifts/frees) — the minimal thing that can copy.

Task: present L random bits, one blank step, then L output steps
(CE on output steps only; alphabet {0,1}). Copy is the first serious
"can local credit learn an algorithm?" challenge.

Arms:
  1 bptt x adam   (gold control)
  2 local x adam  (per-module local targets, ZERO history-backprop:
                   LSTM state and memory are detached every timestep,
                   so no gradient ever crosses a timestep boundary;
                   each module trains on its own per-step loss —
                   controller+read+out on the step CE, writer on a
                   write-local surrogate: content code(c) MSE plus
                   addressing KL toward the slot most dissimilar to
                   the code (empty/old slots), all inputs detached)

Pre-registered questions (§6):
- Q1: does the BPTT control learn copy within budget? (the notorious
  NTM-from-scratch problem, at probe scale)
- Q2: how much of copy does the zero-history local factorization get?
  Bit-level accuracy on the output window is the headline metric.

Run: ``uv run python scripts/probes/w8_ntm_copy.py [--steps=N]``
Walltime printed, never recorded.
"""

import time

import torch
from torch import Tensor, nn

REV = "2026-09-07-r2"  # fresh-draw eval + length generalization + flags

MEM_SLOTS = 16
MEM_WIDTH = 8
HIDDEN = 32
SEQ_LEN = 6
COPY_BATCH = 16

INPUT_STEPS = SEQ_LEN + 1
TOTAL_STEPS = SEQ_LEN * 2 + 1


def _batch(gen: torch.Generator, L: int = SEQ_LEN) -> Tensor:
    """Random bit sequences (B, L) for one copy episode."""
    return torch.randint(0, 2, (COPY_BATCH, L), generator=gen)


def _total_steps(L: int) -> int:
    return L * 2 + 1


class _Heads(nn.Module):
    """Read/write heads + output head over [h; r]."""

    def __init__(self) -> None:
        super().__init__()
        self.kr = nn.Linear(HIDDEN, MEM_WIDTH)
        self.kw = nn.Linear(HIDDEN, MEM_WIDTH)
        self.add = nn.Linear(HIDDEN, MEM_WIDTH)
        self.erase = nn.Linear(HIDDEN, MEM_WIDTH)
        self.out = nn.Linear(HIDDEN + MEM_WIDTH, 2)
        self.beta = nn.Parameter(torch.tensor(10.0))

    def forward(self, h: Tensor, mem: Tensor):
        r_key = self.kr(h)
        w_key = self.kw(h)
        cos = torch.nn.functional.cosine_similarity(
            mem, r_key.unsqueeze(1).expand_as(mem), dim=-1
        )
        a_r = torch.softmax(self.beta * cos, dim=-1)
        read = torch.einsum("bs,bsw->bw", a_r, mem)
        a_w = torch.softmax(
            self.beta
            * torch.cosine_similarity(mem, w_key.unsqueeze(1).expand_as(mem), dim=-1),
            dim=-1,
        )
        add_v = torch.tanh(self.add(h))
        erase_v = torch.sigmoid(self.erase(h))
        mem_next = mem * (1 - a_w.unsqueeze(2) * erase_v.unsqueeze(1)) + (
            a_w.unsqueeze(2) * add_v.unsqueeze(1)
        )
        logits = self.out(torch.cat([h, read], dim=-1))
        return logits, read, mem_next, a_w, a_r


def _zero_mem(batch: int) -> Tensor:
    return torch.full((batch, MEM_SLOTS, MEM_WIDTH), 1e-6)


def _episode_targets(bits: Tensor, L: int) -> Tensor:
    targets = torch.full((bits.size(0), _total_steps(L)), -100, dtype=torch.long)
    targets[:, L + 1 :] = bits
    return targets


def _bptt_episode(controller: nn.Module, heads: nn.Module, bits: Tensor):
    """One full-graph teacher-forced episode; returns (logits, targets)."""
    L = bits.size(1)
    inputs = torch.zeros(bits.size(0), _total_steps(L), 1 + MEM_WIDTH)
    inputs[:, :L, 0] = bits.float()
    mem = _zero_mem(bits.size(0))
    state = (
        torch.zeros(1, bits.size(0), HIDDEN),
        torch.zeros(1, bits.size(0), HIDDEN),
    )
    out_logits = []
    for t in range(_total_steps(L)):
        hc, state = controller(inputs[:, t : t + 1], state)
        logits, _read, mem, _aw, _ar = heads(hc.squeeze(1), mem)
        out_logits.append(logits)
    return torch.stack(out_logits, dim=1), _episode_targets(bits, L)


def _eval_batch(seed: int = 999, L: int = SEQ_LEN) -> Tensor:
    """Fixed fresh-draw eval batch, independent of the training generator."""
    return _batch(torch.Generator().manual_seed(seed), L)


def _run_bptt(steps: int, lr: float, seed: int = 0):
    torch.manual_seed(seed)
    controller = nn.LSTM(1 + MEM_WIDTH, HIDDEN, batch_first=True)
    heads = _Heads()
    params = list(controller.parameters()) + list(heads.parameters())
    opt = torch.optim.Adam(params, lr=lr)
    gen = torch.Generator().manual_seed(7)
    best_fg = 0.0
    for step in range(steps):
        bits = _batch(gen)
        logits_seq, targets = _bptt_episode(controller, heads, bits)
        loss = nn.functional.cross_entropy(
            logits_seq.reshape(-1, 2), targets.reshape(-1), ignore_index=-100
        )
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(params, 5.0)
        opt.step()
        if (step + 1) % max(steps // 5, 1) == 0:
            fg = _greedy_copy_acc(controller, heads, _eval_batch())
            best_fg = max(best_fg, fg)
            print(
                f"bptt step {step + 1}: loss {float(loss):.4f} "
                f"copy-acc(fresh) {fg:.3f}",
                flush=True,
            )
    return controller, heads, best_fg


def _greedy_copy_acc(controller, heads, bits: Tensor) -> float:
    """Greedy rollout copy accuracy (works for any L; L inferred from bits)."""
    B, L = bits.shape
    mem = _zero_mem(B)
    st = (torch.zeros(1, B, HIDDEN), torch.zeros(1, B, HIDDEN))
    outs = []
    with torch.no_grad():
        for t in range(_total_steps(L)):
            x_t = torch.zeros(B, 1, 1 + MEM_WIDTH)
            if t < L:
                x_t[:, 0, 0] = bits[:, t].float()
            hc, st = controller(x_t, st)
            logits, _read, mem, _aw, _ar = heads(hc.squeeze(1), mem)
            outs.append(logits)
    pred = torch.stack(outs, 1).argmax(-1)
    tg = _episode_targets(bits, L)
    mask = tg != -100
    return float((pred == tg)[mask].float().mean())


def _local_step(controller, heads, mem, state, x_t, t, bits, code):
    """One timestep's local losses — every cross-module input detached;
    no tensor carries grad across the timestep boundary."""
    hc, state_new = controller(x_t, (state[0].detach(), state[1].detach()))
    logits, read, mem_next, a_w, _a_r = heads(hc.squeeze(1), mem.detach())
    L = bits.size(1)
    losses = []
    if t >= L + 1:
        losses.append(nn.functional.cross_entropy(logits, bits[:, t - L - 1]))
        # read head: the same CE with h detached — the read vector itself
        # carries the gradient into (kr, beta) only.
        losses.append(
            nn.functional.cross_entropy(
                heads.out(torch.cat([hc.detach().squeeze(1), read], dim=-1)),
                bits[:, t - L - 1],
            )
        )
    elif t < L:
        # writer: content code MSE + addressing KL toward the slot most
        # dissimilar to the new code (empty/old slots).
        h = hc.detach().squeeze(1)
        full_code = torch.zeros(bits.size(0), MEM_WIDTH)
        full_code[:, :2] = code[bits[:, t]]
        losses.append((torch.tanh(heads.add(h)) - full_code).pow(2).mean())
        cos_w = nn.functional.cosine_similarity(
            mem.detach(), full_code.unsqueeze(1).expand_as(mem), dim=-1
        )
        target_a = torch.softmax(-cos_w, dim=-1)
        losses.append(
            (a_w * (a_w.clamp(min=1e-8).log() - target_a.clamp(min=1e-8).log()))
            .sum(-1)
            .mean()
        )
    return losses, state_new, mem_next


def _local_episode(controller, heads, bits, code):
    """One episode of zero-history local losses (state/memory detached
    per timestep; no gradient crosses a timestep boundary)."""
    losses = []
    L = bits.size(1)
    mem = _zero_mem(bits.size(0))
    state = (
        torch.zeros(1, bits.size(0), HIDDEN),
        torch.zeros(1, bits.size(0), HIDDEN),
    )
    for t in range(_total_steps(L)):
        x_t = torch.zeros(bits.size(0), 1, 1 + MEM_WIDTH)
        if t < L:
            x_t[:, 0, 0] = bits[:, t].float()
        step_losses, state, mem_next = _local_step(
            controller, heads, mem, state, x_t, t, bits, code
        )
        losses.extend(step_losses)
        mem = mem_next.detach()
    return torch.stack(losses).mean()


def _run_local(steps: int, lr: float, seed: int = 0):
    torch.manual_seed(seed)
    controller = nn.LSTM(1 + MEM_WIDTH, HIDDEN, batch_first=True)
    heads = _Heads()
    params = list(controller.parameters()) + list(heads.parameters())
    opt = torch.optim.Adam(params, lr=lr)
    gen = torch.Generator().manual_seed(7)
    code = torch.tensor([[1.0, 0.0], [0.0, 1.0]])
    best_fg = 0.0
    for step in range(steps):
        bits = _batch(gen)
        loss = _local_episode(controller, heads, bits, code)
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(params, 5.0)
        opt.step()
        if (step + 1) % max(steps // 5, 1) == 0:
            fg = _greedy_copy_acc(controller, heads, _eval_batch())
            best_fg = max(best_fg, fg)
            print(
                f"local step {step + 1}: loss {float(loss):.4f} "
                f"copy-acc(fresh) {fg:.3f}",
                flush=True,
            )
    return controller, heads, best_fg


def main() -> int:

    t0 = time.time()
    args = __import__("sys").argv[1:]
    opt = dict(a[2:].split("=") for a in args if a.startswith("--") and "=" in a)
    steps = int(opt.get("steps", 3000))
    seed = int(opt.get("seed", 0))
    arms = [opt["arm"]] if "arm" in opt else ["bptt", "local"]
    print(f"w8_ntm_copy {REV}; steps {steps} seed {seed} arms {arms}")
    run = {"bptt": _run_bptt, "local": _run_local}
    trained = None
    for arm in arms:
        print(f"=== W8.5 {arm} (adam 1e-3), {steps} steps ===")
        trained = run[arm](steps, 1e-3, seed)
    if trained is not None and "--len-eval" in args:
        controller, heads, _ = trained
        for L in (SEQ_LEN, 12, 18, 24):
            acc = _greedy_copy_acc(controller, heads, _eval_batch(L=L))
            print(f"len-eval L={L}: copy-acc(fresh) {acc:.3f}", flush=True)
    print(f"\nwalltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
