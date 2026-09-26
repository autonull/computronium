"""Do the 16 restored Triton kernels still compile against triton 3.8?

TODO35 §17.3 deleted them on a "0 importers" inference; the deletion was
reverted in 5b3ba3b6. The question the revert left open is whether they are
*unwired* or *broken*, because those call for opposite responses -- an unwired
kernel is work in progress, a kernel that no longer compiles is a migration
nobody finished, and only one of those is worth keeping work on.

Method: build arguments per kernel from its own signature (the names and arities
below were read off the source, not guessed) and ``.warmup`` it, which compiles
without launching. A kernel that fails to compile cannot work, whatever the
call graph says about it.

Measured on an RTX 3080, triton 3.8.0, torch with CUDA, 2026-09-26. No test in
the tree exercises any of these paths, so this probe is currently the only
evidence either way.
"""

from __future__ import annotations

import sys

import torch
import triton

DEV = "cuda"
B, D, D_IN, D_OUT, PRE, POST, T = 32, 48, 64, 48, 32, 32, 8


def _t(*shape: int) -> torch.Tensor:
    return torch.randn(*shape, device=DEV)


def _b(*shape: int) -> torch.Tensor:
    return torch.randint(0, 2, shape, device=DEV, dtype=torch.float32)


def _o(*shape: int) -> torch.Tensor:
    return torch.zeros(*shape, device=DEV)


BB = {"BLOCK_B": 16, "BLOCK_N": 16}
BD = {"BLOCK_B": 16, "BLOCK_D": 16}
IO = {"BLOCK_IN": 16, "BLOCK_OUT": 16}
SP = {"BLOCK_PRE": 16, "BLOCK_POST": 16}


def cases() -> list[tuple[str, object, tuple, dict]]:
    from computronium.acceleration import (
        ff_kernels,
        hebbian_kernels,
        pc_kernels,
        snn_kernels,
    )
    from computronium.core.substrates import complex_substrate as cplx

    return [
        (
            "pc._pc_prediction_kernel",
            pc_kernels._pc_prediction_kernel,
            (_t(B, D_IN), _t(D_OUT, D_IN), _t(D_OUT), _o(B, D_OUT), B, D_IN, D_OUT, 3),
            BD,
        ),
        (
            "pc._pc_error_update_kernel",
            pc_kernels._pc_error_update_kernel,
            (_t(B, D), _t(B, D), _o(B, D), 0.1, 3, B, D),
            BD,
        ),
        (
            "pc._pc_contrastive_update_kernel",
            pc_kernels._pc_contrastive_update_kernel,
            (
                *[_t(B, D_OUT) for _ in range(4)],
                _o(D_OUT, D_IN),
                B,
                D_IN,
                D_OUT,
                0.1,
                0.01,
            ),
            IO,
        ),
        (
            "snn._lif_step_kernel",
            snn_kernels._lif_step_kernel,
            (_t(B, D), _t(B, D), _o(B, D), 20.0, 5.0, 1.0, 0.01, B, D),
            BB,
        ),
        (
            "snn._stdp_update_kernel",
            snn_kernels._stdp_update_kernel,
            (
                _b(B, PRE, T),
                _b(B, POST, T),
                _o(B, PRE, POST),
                20.0,
                20.0,
                0.01,
                0.01,
                PRE,
                POST,
                T,
            ),
            SP,
        ),
        (
            "snn._contrastive_stdp_kernel",
            snn_kernels._contrastive_stdp_kernel,
            (*[_b(B, PRE, T) for _ in range(4)], _o(B, PRE, POST), PRE, POST, T, 1.0),
            SP,
        ),
        (
            "ff._ff_goodness_kernel",
            ff_kernels._ff_goodness_kernel,
            (_t(B, D), _t(B, D), _o(B), 0.5, B, D),
            BD,
        ),
        (
            "ff._ff_contrastive_update_kernel",
            ff_kernels._ff_contrastive_update_kernel,
            (*[_t(B, D_OUT) for _ in range(4)], _o(D_OUT, D_IN), B, D_IN, D_OUT, 0.01),
            IO,
        ),
        (
            "ff._pepita_error_modulation_kernel",
            ff_kernels._pepita_error_modulation_kernel,
            (_t(B, D_IN), _t(B, D_OUT), _o(D_OUT, D_IN), 0.5, B, D_IN, D_OUT),
            IO,
        ),
        (
            "ff._pepita_contrastive_update_kernel",
            ff_kernels._pepita_contrastive_update_kernel,
            (*[_t(B, D_OUT) for _ in range(4)], _o(D_OUT, D_IN), B, D_IN, D_OUT, 0.01),
            IO,
        ),
        (
            "hebbian._hebbian_update_kernel",
            hebbian_kernels._hebbian_update_kernel,
            (
                _b(B, PRE, T),
                _b(B, POST, T),
                _t(D_OUT, PRE),
                _o(B, D_OUT, PRE),
                B,
                D_IN,
                D_OUT,
                0.01,
                0,
            ),
            {"BLOCK_IN": 16, "BLOCK_OUT": 16},
        ),
        (
            "hebbian._three_factor_hebbian_kernel",
            hebbian_kernels._three_factor_hebbian_kernel,
            (
                _b(B, PRE, T),
                _b(B, POST, T),
                _t(B, POST),
                _o(D_OUT, PRE),
                B,
                D_IN,
                D_OUT,
                0.01,
            ),
            IO,
        ),
        (
            "hebbian._contrastive_hebbian_kernel",
            hebbian_kernels._contrastive_hebbian_kernel,
            (
                *[_b(B, PRE, T) for _ in range(4)],
                _o(B, PRE, POST),
                B,
                D_IN,
                D_OUT,
                0.01,
                1.0,
            ),
            {"BLOCK_IN": 16, "BLOCK_OUT": 16},
        ),
        (
            "cplx._complex_tanh_kernel",
            cplx._complex_tanh_kernel,
            (_t(256), _t(256), _o(256), _o(256), 256),
            {"BLOCK_SIZE": 64},
        ),
    ]


def main() -> int:
    if not torch.cuda.is_available():
        print("no CUDA: this probe is the only thing that can answer the question")
        return 1
    rows: list[tuple[str, bool, str]] = []
    for name, kernel, args, consts in cases():
        try:
            kernel.warmup(*args, grid=(1,), **consts)
        except Exception as exc:
            lines = [ln for ln in str(exc).splitlines() if ln.strip()]
            cause = lines[-1] if lines else str(exc)
            rows.append((name, False, f"{type(exc).__name__}: {cause[:88]}"))
        else:
            rows.append((name, True, ""))
    width = max(len(n) for n, _, _ in rows)
    for name, ok, detail in rows:
        print(f"{name:{width}}  {'COMPILES' if ok else 'FAILS':9} {detail}")
    good = sum(1 for _, ok, _ in rows if ok)
    print(f"\n{good}/{len(rows)} compile against triton {triton.__version__}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
