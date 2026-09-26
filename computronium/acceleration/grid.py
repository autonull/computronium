"""One grid convention for every tiled triton kernel (TODO36 §9.3.1).

**Why this module exists.** Binding ``tl.program_id(0)`` to a kernel's *input*
axis while the store walks its *output* axis is the single most common defect in
this tree: six of the eleven defects §4.5 found, across FF, PC, Hebbian and
PEPITA. Nothing about it is loud — no error, no partial result, correct shapes
and dtypes — and when the offending dimension is a multiple of its block it is
invisible even to a parity test. The convention was therefore written into six
docstrings, which is documentation, not prevention.

Here it is *code*. A 2-D kernel takes its tile from `tile_2d` and writes through
`store_2d`, so ``program_id`` is read in exactly one place and the store address
is computed in exactly one place. A kernel that wants the transposed grid cannot
express it; it would have to pass its arguments in the wrong roles, and the
launch site in the same commit has to agree with it.

**The convention.** For an output of shape ``[n_rows, n_cols]``,
``program_id(0)`` walks the rows and ``program_id(1)`` the columns — row-major
over the output's own layout. Launch sites use `grid_2d`, which returns exactly
that tuple, so a kernel and its launcher cannot disagree about which axis is
which.

Non-tiled kernels (per-sample reductions, single-axis sweeps) do not use this
module: there is no second axis to confuse.
"""

from __future__ import annotations

import triton
import triton.language as tl

__all__ = ["cdiv", "grid_2d", "load_2d", "store_2d", "tile_2d"]


def cdiv(n: int, block: int) -> int:
    """Ceiling division, the block-count half of every launch."""
    return -(-n // block)


def grid_2d(
    n_rows: int, n_cols: int, block_rows: int, block_cols: int
) -> tuple[int, int]:
    """Launch grid for a ``[n_rows, n_cols]`` output, row-major.

    Pass the same four extents to `tile_2d` inside the kernel; that pairing is
    the whole contract.
    """
    return (cdiv(n_rows, block_rows), cdiv(n_cols, block_cols))


@triton.jit
def tile_2d(
    n_rows: int,
    n_cols: int,
    BLOCK_ROWS: tl.constexpr,  # ruff: ignore[invalid-argument-name]
    BLOCK_COLS: tl.constexpr,  # ruff: ignore[invalid-argument-name]
):
    """The row-major ``[n_rows, n_cols]`` tile for this program.

    Returns ``(offs_row, offs_col, mask_row, mask_col)``. The only place in the
    tree that reads ``tl.program_id`` for a 2-D output.
    """
    pid_row = tl.program_id(0)
    pid_col = tl.program_id(1)
    offs_row = pid_row * BLOCK_ROWS + tl.arange(0, BLOCK_ROWS)
    offs_col = pid_col * BLOCK_COLS + tl.arange(0, BLOCK_COLS)
    return offs_row, offs_col, offs_row < n_rows, offs_col < n_cols


@triton.jit
def load_2d(
    in_ptr,
    n_cols,
    offs_row,
    offs_col,
    mask_row,
    mask_col,
):
    """Load a row-major ``[n_rows, n_cols]`` tile, zero outside the mask."""
    return tl.load(
        in_ptr + offs_row[:, None] * n_cols + offs_col[None, :],
        mask=mask_row[:, None] & mask_col[None, :],
        other=0.0,
    )


@triton.jit
def store_2d(
    out_ptr,
    value,
    n_cols,
    offs_row,
    offs_col,
    mask_row,
    mask_col,
):
    """Store a row-major ``[n_rows, n_cols]`` tile.

    The address expression lives here so that a load and a store of the same
    tile cannot disagree about its orientation, which is the defect class this
    module exists to delete.
    """
    tl.store(
        out_ptr + offs_row[:, None] * n_cols + offs_col[None, :],
        value,
        mask=mask_row[:, None] & mask_col[None, :],
    )
