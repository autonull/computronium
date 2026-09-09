"""E4 — Sequential composition on a counter machine (TODO17 §4.4).

Pre-registered. Question: can ψ implement a multi-step algorithm by
COMPOSING primitive operations over a tape — solving an O(N)-step task
at O(1) architectural depth?

Substrate (θ, fixed): a 7-primitive counter machine over a float tape —
LOAD, STORE, ADD, SUB, NEGFLAG, conditional BRanch-if-flag, BRA. Each
primitive is a fixed depth-1 operation; NO single primitive (or single
application) computes any task. The tape is external memory: the
plastic register (acc, flag) is 2 scalars — the O(N) intermediate state
lives on the tape.

Task set: max of an N-element list, sum of an N-element list, median of
3. N ∈ {4, 8, 16}.

Arms:
  single_op   — ψ applies exactly ONE primitive once (Z3-toy regime)
  composed_ops— ψ = a full primitive SEQUENCE (the program)

ψ acquisition: WRITTEN, closed-form (recorded per §4.4 — the
"closed-form solve" option; the Z3-toy ridge machinery analog). The
programs are unrolled per N (constant addressing, no indirect mode):
length O(N), architectural depth O(1), steps O(N).

Prediction: composed_ops solves all tasks at every N; single_op fails
everywhere. Falsification: composed_ops fails on any task requiring
intermediate state.

Known-trap check: value binding is exact (scalar tape writes, no
cosine-softmax addressing); the signed-content and slot-collision traps
are avoided by construction.

uv run python scripts/probes/w17_e4_composition.py
Walltime printed, never recorded.
"""

from __future__ import annotations

import sys
import time

N_GA = (4, 8, 16)


# --- substrate (θ): fixed primitive set over (tape, acc, flag, pc) ---


def op_load(tape, acc, flag, pc, a, b):
    return tape, tape[a % len(tape)], flag, pc + 1


def op_store(tape, acc, flag, pc, a, b):
    t = list(tape)
    t[a % len(t)] = acc
    return t, acc, flag, pc + 1


def op_add(tape, acc, flag, pc, a, b):
    return tape, acc + tape[a % len(tape)], flag, pc + 1


def op_sub(tape, acc, flag, pc, a, b):
    return tape, acc - tape[a % len(tape)], flag, pc + 1


def op_negflag(tape, acc, flag, pc, a, b):
    return tape, acc, acc < 0, pc + 1


def op_br(tape, acc, flag, pc, a, b):
    return tape, acc, flag, pc + a if flag else pc + 1


def op_bra(tape, acc, flag, pc, a, b):
    return tape, acc, flag, pc + a


def op_negacc(tape, acc, flag, pc, a, b):
    return tape, -acc, flag, pc + 1


OPS = {
    "load": op_load,
    "store": op_store,
    "add": op_add,
    "sub": op_sub,
    "negflag": op_negflag,
    "br": op_br,
    "bra": op_bra,
    "negacc": op_negacc,
}


def run(program: list[tuple[str, int, int]], tape: list[float], cap: int = 4096):
    acc, flag, pc, steps = 0.0, False, 0, 0
    while 0 <= pc < len(program) and steps < cap:
        name, a, b = program[pc]
        tape, acc, flag, pc = OPS[name](tape, acc, flag, pc, a, b)
        steps += 1
    return tape, acc, flag


def _task_input(task: str, n: int, rng) -> tuple[list[float], float, int]:
    xs = [float(rng.randint(1, 9)) for _ in range(n)]
    if task == "max":
        return [*xs, 0.0], max(xs), n
    if task == "sum":
        return [*xs, 0.0], sum(xs), n
    if task == "median3":
        xs = xs[:3] + [0.0] * (n - 3)
        scratch = [0.0] * 7  # slots: sum, max, min, output, -x0, -x1, -x2
        return xs + scratch, sorted(xs[:3])[1], n
    raise ValueError(task)


# --- ψ acquisition: WRITTEN (closed-form) ---


def _fold_block(task: str, k: int) -> list[tuple[str, int, int]]:
    """One comparison step: keep the larger (max) or smaller (min) of acc
    and tape[k], restoring acc exactly in the taken branch."""
    if task == "max":
        # flag (t[k]>acc) → br lands on load(k); else restore then bra
        # skips the load
        return [
            ("sub", k, 0),
            ("negflag", 0, 0),
            ("br", 3, 0),
            ("add", k, 0),
            ("bra", 2, 0),
            ("load", k, 0),
        ]
    raise ValueError(task)


def write_program(task: str, n: int) -> list[tuple[str, int, int]]:
    if task == "max":
        prog = [("load", 0, 0)]
        for k in range(1, n):
            prog += _fold_block("max", k)
        return [*prog, ("store", n, 0)]
    if task == "sum":
        prog = [("load", 0, 0)]
        prog += [("add", k, 0) for k in range(1, n)]
        return [*prog, ("store", n, 0)]
    if task == "median3":
        # med = sum - max - min; min = -max(-x) over negated copies
        # sum
        prog = [("load", 0, 0), ("add", 1, 0), ("add", 2, 0), ("store", n + 1, 0)]
        # max
        prog += [("load", 0, 0)]
        for k in (1, 2):
            prog += _fold_block("max", k)
        prog += [("store", n + 2, 0)]  # max
        # min over negated copies in slots n+4..n+6
        for k in (0, 1, 2):
            prog += [("load", k, 0), ("negacc", 0, 0), ("store", n + 4 + k, 0)]
        prog += [("load", n + 4, 0)]
        for k in (n + 5, n + 6):
            prog += _fold_block("max", k)
        prog += [("negacc", 0, 0), ("store", n + 3, 0)]  # min
        # combine
        prog += [("load", n + 1, 0), ("sub", n + 2, 0), ("sub", n + 3, 0)]
        return [*prog, ("store", n, 0)]
    raise ValueError(task)


def main() -> int:  # ruff: ignore[too-many-locals] - probe harness
    t0 = time.time()
    ok_all = True
    print("ψ acquisition: WRITTEN (closed-form; recorded per §4.4)")
    for task in ("max", "sum", "median3"):
        for n in N_GA:
            rng = __import__("random").Random(2)
            composed_hits = single_hits = 0
            trials = 16
            program = write_program(task, n)
            single = [(program[0][0], 0, 0)]
            for _ in range(trials):
                tape, target, out_slot = _task_input(task, n, rng)
                tape_c, _acc_c, _ = run(program, tape)
                tape_s, _acc_s, _ = run(single, tape)
                composed_hits += abs(tape_c[out_slot] - target) <= 1e-9
                single_hits += abs(tape_s[out_slot] - target) <= 1e-9
            ok_all &= composed_hits == trials and single_hits == 0
            print(
                f"{task:>8} N={n:>2}: composed {composed_hits}/{trials}  "
                f"single_op {single_hits}/{trials}  "
                f"(program length {len(program)} = O(N), depth O(1), "
                f"θ training steps 0)"
            )
    print(
        f"\nVERDICT: {'E4 ALIVE — ψ sequences primitives over memory' if ok_all else 'E4 falsified'}"
    )
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
