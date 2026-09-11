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

Run: ``uv run python scripts/probes/w8_ntm_copy.py [--steps=N] [--arm=...]``
Walltime printed, never recorded.

Q3 (r5, the §10-item-2 redesign; pre-registered): the r3 task-shaped
writer surrogate plateaued local copy at ~0.7 (§11.2) — the 2-bit
content code cannot encode WRITE ORDER, so the reader cannot
disambiguate same-bit slots. The `local2` arm replaces it with
expected-content MSE under the writer's own addressing distribution
(a_w detached): order-carrying content (bit sign on basis channel t)
+ overwrite (erase→1 where written) + the addressing KL. Prediction:
local2 breaks the plateau toward the ≥0.85 promotion bar; falsified
if it stalls at ~0.7 → the plateau is NOT writer-expressivity-limited
and the lever moves to the read/controller side. (RESOLVED §11.10: the
signed content was unreadable by cosine softmax; the r6 recipe broke
the plateau to 0.865.)

Q4 (r7, the §11.14 slot-identity collision; pre-registered): with
mem_slots 16 > mem_width 8 the static slot embeddings COLLIDE (slots s
and s+8 share one-hot e_{s%8}), so a read key for slot k ties cos=1.0
with the pristine slot k+8 — the tie-split read halves content magnitude
and plausibly explains the residual decode gap (acc_given_hit 0.78-0.86,
§11.11). ``--width=16`` gives mem_slots <= mem_width: exact orthogonal
one-hot identities, no ties, content/key channels unchanged (L=6 uses
channels 0-5). Prediction: acc_given_hit 0.78-0.86 -> >=0.9 and local
copy-acc mean 0.816 -> >=0.85 at the same budget; falsified if decode
precision is unchanged (the gap is content-precision or beta sharpness,
not identity collision).
"""

import time

import torch
from torch import Tensor, nn

from computronium.core.optimization.strategies.update import newton_schulz5

REV = "2026-09-08-r7"  # Q4: --width (slot-identity collision fix, pre-registered)

MEM_SLOTS = 16
MEM_WIDTH = 8
HIDDEN = 32
SEQ_LEN = 6
COPY_BATCH = 16

INPUT_STEPS = SEQ_LEN + 1
TOTAL_STEPS = SEQ_LEN * 2 + 1

# Task-ladder rung (TODO15 §17): REPEATS=1 is the validated copy task;
# REPEATS=R emits the sequence R times after the delimiter (fixed R, not
# flag-conditioned — the algorithmic step up is output-phase counting
# under detached state, which R directly stresses). Set via --repeats=R.
REPEATS = 1

# Task flag (TODO15 §17.10): "copy" = validated sequential task. "recall"
# = associative recall with EXPLICIT keys (the first pass hid the key→slot
# binding probe-side, making it unsupervisable for BPTT — the control must
# never depend on information it cannot observe). Input layout: input step
# t presents (value=bit on ch0, key=one-hot perm[t] on ch1..); output step
# k presents one-hot key k as the cue (ch1..) and must emit the value
# paired with that key. perm = identity reduces recall to copy exactly.
TASK = "copy"


def _draw_perm(batch: int, L: int, gen: torch.Generator) -> Tensor | None:
    if TASK == "copy":
        return None
    # ONE permutation per episode batch — the writer supervision targets
    # are batch-wide (a per-row perm would need per-row targets; the first
    # recall pass supervised every row onto row 0's slots: diversity 0.188).
    return torch.randperm(L, generator=gen).unsqueeze(0).expand(batch, L)


def _batch(gen: torch.Generator, L: int = SEQ_LEN) -> Tensor:
    """Random bit sequences (B, L) for one copy episode."""
    return torch.randint(0, 2, (COPY_BATCH, L), generator=gen)


def _total_steps(L: int) -> int:
    return L + 1 + REPEATS * L


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
    """Slot embeddings instead of ~0 init (r6): pure content addressing
    cannot target an empty slot — every ~0 slot has cos ~ 0 with any key,
    so position is unobservable and writes collapse to one slot (the r5/r6
    diagnostic). Static per-slot identity vectors make position retrievable;
    erase+add overwrites them on the first write."""
    mem = torch.zeros(batch, MEM_SLOTS, MEM_WIDTH)
    for s in range(MEM_SLOTS):
        mem[:, s, s % MEM_WIDTH] = 0.5
    return mem


def _identity_perm(L: int, batch: int) -> Tensor:
    return torch.arange(L).unsqueeze(0).expand(batch, L)


def _episode_targets(bits: Tensor, L: int, perm: Tensor | None = None) -> Tensor:
    """Output-phase targets. copy: bit k at step L+1+k. recall: slots were
    written in permuted order (perm[t] = slot of input t); output step k is
    cued on slot k and must emit the value written there (bits[:, inv_k])."""
    targets = torch.full((bits.size(0), _total_steps(L)), -100, dtype=torch.long)
    out = bits.repeat(1, REPEATS)
    if perm is not None:
        inv = perm.argsort(1)
        out = bits.gather(1, inv).repeat(1, REPEATS)
    targets[:, L + 1 :] = out
    return targets


def _bptt_episode(
    controller: nn.Module, heads: nn.Module, bits: Tensor, perm: Tensor | None = None
):
    """One full-graph teacher-forced episode; returns (logits, targets)."""
    L = bits.size(1)
    B = bits.size(0)
    inputs = torch.zeros(B, _total_steps(L), 1 + MEM_WIDTH)
    inputs[:, :L, 0] = bits.float()
    if perm is not None:
        for t in range(L):
            inputs[:, t, 1 + perm[0, t]] = 1.0  # explicit key
        for k in range(L):
            inputs[:, L + 1 + k, 1 + k] = 1.0  # cue = key
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
    return torch.stack(out_logits, dim=1), _episode_targets(bits, L, perm)


def _eval_batch(seed: int = 999, L: int = SEQ_LEN) -> Tensor:
    """Fixed fresh-draw eval batch, independent of the training generator."""
    return _batch(torch.Generator().manual_seed(seed), L)


def _eval_perm(seed: int = 999, L: int = SEQ_LEN) -> Tensor | None:
    """Fixed eval permutation for recall (matched to _eval_batch's draw)."""
    if TASK == "copy":
        return None
    return _draw_perm(
        _eval_batch(seed, L).size(0), L, torch.Generator().manual_seed(seed)
    )


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
        perm = _draw_perm(bits.size(0), bits.size(1), gen)
        logits_seq, targets = _bptt_episode(controller, heads, bits, perm)
        loss = nn.functional.cross_entropy(
            logits_seq.reshape(-1, 2), targets.reshape(-1), ignore_index=-100
        )
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(params, 5.0)
        opt.step()
        if (step + 1) % max(steps // 5, 1) == 0:
            fg = _greedy_copy_acc(controller, heads, _eval_batch(), _eval_perm())
            best_fg = max(best_fg, fg)
            print(
                f"bptt step {step + 1}: loss {float(loss.detach()):.4f} "
                f"copy-acc(fresh) {fg:.3f}",
                flush=True,
            )
    return controller, heads, best_fg


def _greedy_copy_acc(controller, heads, bits: Tensor, perm: Tensor | None = None):
    """Greedy rollout accuracy (works for any L; L inferred from bits)."""
    B, L = bits.shape
    mem = _zero_mem(B)
    st = (torch.zeros(1, B, HIDDEN), torch.zeros(1, B, HIDDEN))
    outs = []
    with torch.no_grad():
        for t in range(_total_steps(L)):
            x_t = torch.zeros(B, 1, 1 + MEM_WIDTH)
            if t < L:
                x_t[:, 0, 0] = bits[:, t].float()
                if perm is not None:
                    x_t[:, 0, 1 + perm[0, t]] = 1.0
            elif perm is not None and t >= L + 1:
                x_t[:, 0, 1 + (t - L - 1) % L] = 1.0
            hc, st = controller(x_t, st)
            logits, _read, mem, _aw, _ar = heads(hc.squeeze(1), mem)
            outs.append(logits)
    pred = torch.stack(outs, 1).argmax(-1)
    tg = _episode_targets(bits, L, perm)
    mask = tg != -100
    return float((pred == tg)[mask].float().mean())


def _writer_target(bits: Tensor, t: int) -> Tensor:
    """Order-carrying write content for input step t, COSINE-RETRIEVABLE:
    content = (0.5 + 0.5*bit) * e_t. Position = which basis channel,
    bit = magnitude. Non-negative is required — a signed content (+/-e_t)
    is unretrievable by beta*cosine softmax (cos = -1 sorts LAST; the
    r5 mechanics test measured exactly chance), and a shared 2-bit code
    cannot encode write order (the r3 plateau)."""
    c = torch.zeros(bits.size(0), MEM_WIDTH)
    c[:, t % MEM_WIDTH] = 0.5 + 0.5 * bits[:, t].float()
    return c


def _local_step(  # ruff: ignore[too-many-arguments, too-many-locals, too-many-positional-arguments] - probe harness
    controller,
    heads,
    mem,
    state,
    x_t,
    t,
    bits,
    code,
    writer: str = "code",
    credit_controller: bool = False,
    perm: Tensor | None = None,
    writer_weight: float = 1.0,
    credit_read: bool = False,
):
    """One timestep's local losses — no tensor carries grad across the
    timestep boundary (state/memory inputs detached).

    writer="code": the r3 task-shaped surrogate (content-code MSE +
    addressing KL). writer="expected": the §10-item-2 redesign —
    expected-content MSE under the writer's OWN addressing distribution
    (a_w detached, order-carrying content target) plus an overwrite
    (erase→1 where written) target; the addressing KL is kept for kw.

    credit_controller: route the writer losses through hc (NOT detached).
    Still zero-history — the LSTM state INPUT is detached, so only this
    step's transition is in the graph — but the controller now receives
    per-step local credit for its input-phase emissions, which it never
    got in r3/r5 (output CE touches output steps only)."""
    hc, state_new = controller(x_t, (state[0].detach(), state[1].detach()))
    logits, read, mem_next, a_w, _a_r = heads(hc.squeeze(1), mem.detach())
    L = bits.size(1)
    losses = []
    if t >= L + 1:
        k = (t - L - 1) % L
        v_idx = bits[:, k]
        if perm is not None:
            inv = perm.argsort(1)
            v_idx = bits.gather(1, inv[:, k : k + 1]).squeeze(1)
        losses.append(nn.functional.cross_entropy(logits, v_idx))
        # read head: the same CE with h detached — the read vector itself
        # carries the gradient into (kr, beta) only. §5.4 lever (b):
        # credit_read routes it through the LIVE hc (value-channel
        # supervision at the cued-read step).
        h_read = hc.squeeze(1) if credit_read else hc.detach().squeeze(1)
        losses.append(
            nn.functional.cross_entropy(
                heads.out(torch.cat([h_read, read], dim=-1)),
                v_idx,
            )
        )
        if (
            writer == "expected"
        ):  # r6: supervise the READ KEY onto e_{k mod L} (the slot written
            # for bit k is k mod L by construction). Through the softmax
            # addressing alone the key sequence learns ~2x slower than the
            # 30 s cell budget allows (hit rate 0.083 -> 0.167 over 1200
            # steps); the direct local target teaches the controller's
            # output-step counting in the same pass.
            k_idx = k % MEM_WIDTH
            key_target = torch.zeros(bits.size(0), MEM_WIDTH)
            key_target[:, k_idx] = 1.0
            losses.append(10.0 * (heads.kr(hc.squeeze(1)) - key_target).pow(2).mean())
    elif t < L:
        # writer losses; h_detached feeds every loss unless
        # credit_controller routes them through the live hc.
        n_writer = len(losses)
        h_live = hc.squeeze(1)
        h = h_live if credit_controller else h_live.detach()
        w = a_w.detach() if writer == "expected" else a_w
        if writer == "expected":
            w_slot = t if perm is None else int(perm[0, t])
            c = _writer_target(bits, w_slot)
            add_v = torch.tanh(heads.add(h))
            erase_v = torch.sigmoid(heads.erase(h))
            # expected-content MSE: E_{s~a_w} ||add_v - c||^2 — the write
            # carries the content where the writer actually writes.
            losses.append(
                (w.unsqueeze(2) * (add_v.unsqueeze(1) - c.unsqueeze(1)).pow(2))
                .sum(dim=(1, 2))
                .mean()
            )
            # overwrite target: erase -> 1 where the write lands
            # (expected over the addressing distribution).
            losses.append(
                (w.unsqueeze(2) * (1.0 - erase_v).unsqueeze(1).pow(2))
                .sum(dim=(1, 2))
                .mean()
            )
            # addressing: r6 mechanics finding — the KL toward the
            # least-similar slot NEVER spread writes (one-slot collapse,
            # span 1.0). Supervise a_w onto slot t directly (a local
            # target, same status as the content target c).
            target_a = (
                torch.nn.functional
                .one_hot(torch.tensor(w_slot % MEM_SLOTS), MEM_SLOTS)
                .float()
                .expand_as(a_w)
            )
            losses.append(
                (a_w * (a_w.clamp(min=1e-8).log() - target_a.clamp(min=1e-8).log()))
                .sum(-1)
                .mean()
            )
        else:
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
        # §5.4 lever (a): writer loss re-weighting relative to step CE.
        losses[n_writer:] = [writer_weight * l for l in losses[n_writer:]]
    return losses, state_new, mem_next


def _local_episode(
    controller,
    heads,
    bits,
    code,
    writer: str = "code",
    credit_controller: bool = False,
    perm: Tensor | None = None,
    writer_weight: float = 1.0,
    credit_read: bool = False,
):
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
            if perm is not None:
                x_t[:, 0, 1 + perm[0, t]] = 1.0
        elif perm is not None and t >= L + 1:
            x_t[:, 0, 1 + (t - L - 1) % L] = 1.0
        step_losses, state, mem_next = _local_step(
            controller,
            heads,
            mem,
            state,
            x_t,
            t,
            bits,
            code,
            writer,
            credit_controller,
            perm,
            writer_weight,
            credit_read,
        )
        losses.extend(step_losses)
        mem = mem_next.detach()
    return torch.stack(losses).mean()


def _diagnose(  # ruff: ignore[too-many-locals] - probe harness
    controller, heads, bits: Tensor, perm: Tensor | None = None
) -> dict[str, float]:
    """Read hit-rate diagnostic (§11.9 finding 3, the decisive split):
    at output step t, does the read addressing a_r place its mass on the
    slot that was written for bit t-L-1? High hit-rate -> the read head
    and memory are fine and the bottleneck is the controller's key
    sequence; low -> the read-local rule is the weak link. Also reports
    write-slot diversity and output accuracy conditioned on a hit."""
    B, L = bits.shape
    if perm is None:
        perm = _identity_perm(L, B)
    mem = _zero_mem(B)
    state = (
        torch.zeros(1, B, HIDDEN),
        torch.zeros(1, B, HIDDEN),
    )
    write_slot: dict[int, Tensor] = {}
    hits, accs, hit_accs = [], [], []
    accs_zero_read: list[Tensor] = []
    with torch.no_grad():
        for t in range(_total_steps(L)):
            x_t = torch.zeros(B, 1, 1 + MEM_WIDTH)
            if t < L:
                x_t[:, 0, 0] = bits[:, t].float()
                if TASK == "recall":
                    x_t[:, 0, 1 + perm[0, t]] = 1.0
            elif TASK == "recall" and t >= L + 1:
                x_t[:, 0, 1 + (t - L - 1) % L] = 1.0
            hc, state = controller(x_t, state)
            logits, read, mem_next, a_w, a_r = heads(hc.squeeze(1), mem)
            if t < L:
                write_slot[t] = a_w.argmax(-1)
            elif t >= L + 1:
                k = t - L - 1
                hit = a_r.argmax(-1) == (
                    k % L if TASK == "recall" else write_slot[k % L]
                )
                correct = logits.argmax(-1) == bits[:, k % L]
                hits.append(hit.float())
                accs.append(correct.float())
                hit_accs.append(correct[hit].float())
                # memory-ablation control: does the output depend on the
                # read at all? Zero the read vector and re-decode.
                logits0 = heads.out(torch.cat([hc.squeeze(1), read * 0.0], dim=-1))
                accs_zero_read.append((logits0.argmax(-1) == bits[:, k % L]).float())
            mem = mem_next
    slot_seq = torch.stack([write_slot[k] for k in range(L)], 1)  # (B, L)
    diversity = torch.tensor([
        float(len(set(row.tolist()))) / MEM_SLOTS for row in slot_seq
    ]).mean()
    return {
        "read_hit_rate": float(torch.cat(hits).mean()) if hits else 0.0,
        "output_acc": float(torch.cat(accs).mean()) if accs else 0.0,
        "acc_given_hit": float(torch.cat(hit_accs).mean()) if hit_accs else 0.0,
        "acc_read_zeroed": float(torch.cat(accs_zero_read).mean()),
        "write_slot_diversity": float(diversity),
    }


def _run_local(
    steps: int,
    lr: float,
    seed: int = 0,
    writer: str = "code",
    label: str = "local",
    credit_controller: bool = False,
    writer_weight: float = 1.0,
    credit_read: bool = False,
):
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
        perm = _draw_perm(bits.size(0), bits.size(1), gen)
        loss = _local_episode(
            controller,
            heads,
            bits,
            code,
            writer,
            credit_controller,
            perm,
            writer_weight,
            credit_read,
        )
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(params, 5.0)
        opt.step()
        if (step + 1) % max(steps // 5, 1) == 0:
            fg = _greedy_copy_acc(controller, heads, _eval_batch(), _eval_perm())
            best_fg = max(best_fg, fg)
            print(
                f"{label} step {step + 1}: loss {float(loss.detach()):.4f} "
                f"copy-acc(fresh) {fg:.3f}",
                flush=True,
            )
    return controller, heads, best_fg


class _Muon(torch.optim.Optimizer):
    """Orthogonalized-SGD (Muon) on 2D params; plain SGD on the rest.

    Uses the ontology's shipped Newton-Schulz kernel as the U axis.
    """

    def __init__(self, params, lr: float, momentum: float = 0.95):
        super().__init__(list(params), {"lr": lr, "momentum": momentum})

    @torch.no_grad()
    def step(self) -> None:
        for group in self.param_groups:
            lr, mom = group["lr"], group["momentum"]
            for p in group["params"]:
                if p.grad is None:
                    continue
                g = p.grad
                st = self.state[p]
                if g.ndim == 2:
                    buf = st.get("m")
                    buf = g.clone() if buf is None else buf.mul(mom).add(g)
                    st["m"] = buf
                    p.add_(newton_schulz5(buf), alpha=-lr)
                else:
                    p.add_(g, alpha=-lr)


def _run_local_muon(steps: int, lr: float, seed: int = 0):
    torch.manual_seed(seed)
    controller = nn.LSTM(1 + MEM_WIDTH, HIDDEN, batch_first=True)
    heads = _Heads()
    params = list(controller.parameters()) + list(heads.parameters())
    opt = _Muon(params, lr)
    gen = torch.Generator().manual_seed(7)
    code = torch.tensor([[1.0, 0.0], [0.0, 1.0]])
    best_fg = 0.0
    for step in range(steps):
        bits = _batch(gen)
        perm = _draw_perm(bits.size(0), bits.size(1), gen)
        loss = _local_episode(controller, heads, bits, code, "code", False, perm)
        opt.zero_grad()
        loss.backward()
        opt.step()
        if (step + 1) % max(steps // 5, 1) == 0:
            fg = _greedy_copy_acc(controller, heads, _eval_batch(), _eval_perm())
            best_fg = max(best_fg, fg)
            print(
                f"local-muon step {step + 1}: loss {float(loss.detach()):.4f} "
                f"copy-acc(fresh) {fg:.3f}",
                flush=True,
            )
    return controller, heads, best_fg


def main() -> int:  # ruff: ignore[too-many-locals] - probe harness

    t0 = time.time()
    args = __import__("sys").argv[1:]
    opt = dict(a[2:].split("=") for a in args if a.startswith("--") and "=" in a)
    steps = int(opt.get("steps", 3000))
    seed = int(opt.get("seed", 0))
    lr = float(opt.get("lr", 1e-3))
    # Q4 slot-identity fix: mem_slots <= mem_width gives exact one-hot
    # slot embeddings (default 8 = the validated r6 config).
    global MEM_WIDTH, REPEATS  # ruff: ignore[global-statement] - probe CLI overrides module constants
    MEM_WIDTH = int(opt.get("width", 8))
    REPEATS = int(opt.get("repeats", 1))
    globals()["TASK"] = opt.get("task", "copy")

    arms = [opt["arm"]] if "arm" in opt else ["bptt", "local"]
    print(
        f"w8_ntm_copy {REV}; steps {steps} seed {seed} lr {lr:g} "
        f"width {MEM_WIDTH} repeats {REPEATS} task {TASK} arms {arms}"
    )
    run = {
        "bptt": _run_bptt,
        "local": _run_local,
        "local2": lambda steps, lr, seed: _run_local(
            steps, lr, seed, writer="expected", label="local2"
        ),
        "local3": lambda steps, lr, seed: _run_local(
            steps,
            lr,
            seed,
            writer="expected",
            label="local3",
            credit_controller=True,
        ),
        "local-muon": _run_local_muon,
        # §5.4 combined levers: (a) writer-loss re-weight x3 + (b) live-hc
        # value-channel supervision at the cued-read step.
        "local4": lambda steps, lr, seed: _run_local(
            steps,
            lr,
            seed,
            writer="expected",
            label="local4",
            credit_controller=True,
            writer_weight=3.0,
            credit_read=True,
        ),
    }
    trained = None
    if "load" in opt:
        ckpt = torch.load(opt["load"], weights_only=True)
        controller = nn.LSTM(1 + MEM_WIDTH, HIDDEN, batch_first=True)
        controller.load_state_dict(ckpt["controller"])
        heads = _Heads()
        heads.load_state_dict(ckpt["heads"])
        arms = []
        trained = (controller, heads, None)
    for arm in arms:
        print(f"=== W8.5 {arm} (lr {lr:g}), {steps} steps ===")
        trained = run[arm](steps, lr, seed)
    if trained is not None and "--diagnose" in args:
        controller, heads, _ = trained
        torch.save(
            {
                "controller": controller.state_dict(),
                "heads": heads.state_dict(),
            },
            "logs/w8_ntm_local3.pt",
        )
        stats = _diagnose(controller, heads, _eval_batch(), _eval_perm())
        print("read diagnostic:", {k: round(v, 3) for k, v in stats.items()})
    if trained is not None and "--len-eval" in args:
        controller, heads, _ = trained
        for L in (SEQ_LEN, 12, 18, 24):
            acc = _greedy_copy_acc(controller, heads, _eval_batch(L=L))
            print(f"len-eval L={L}: copy-acc(fresh) {acc:.3f}", flush=True)
    print(f"\nwalltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
