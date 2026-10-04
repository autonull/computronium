"""One grid convention, and the lock that keeps it (TODO36 §9.3.1).

The transposed grid is the most common defect this tree has produced: six of
the eleven defects §4.5 found, in FF, PC, Hebbian and PEPITA. It hides because
nothing about it is loud, and it survives a parity test whenever the offending
extent is a multiple of its block.

The convention now lives in `computronium.acceleration.grid`, so this file
checks three things:

1. `grid_2d` is the row-major grid for the output it is given, and no other.
2. **A transposed grid is detected**, not merely discouraged — the lock below is
   only worth having if the class it forbids is real, so it is demonstrated.
3. No 2-D tiled triton kernel in the tree reads `tl.program_id` or builds a
   2-D `tl.store` address by hand. That is the AST census; a new kernel that
   wants the old freedom has to delete this assertion rather than write past it.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
import torch

from computronium.acceleration.grid import cdiv, grid_2d

CUDA = pytest.mark.skipif(
    not torch.cuda.is_available(), reason="a triton kernel needs a device tensor"
)

KERNEL_ROOT = Path(__file__).resolve().parents[2] / "computronium" / "acceleration"

_TILED_BLOCK_NAMES = {"BLOCK_IN", "BLOCK_OUT", "BLOCK_PRE", "BLOCK_POST"}


def _triton_functions() -> list[tuple[Path, ast.FunctionDef]]:
    found: list[tuple[Path, ast.FunctionDef]] = []
    for path in sorted(KERNEL_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text())
        found += [
            (path, node)
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and _is_jit(node)
        ]
    return found


def _is_jit(node: ast.FunctionDef) -> bool:
    return any("triton.jit" in ast.unparse(d) for d in node.decorator_list)


def _device_helpers() -> set[str]:
    """Jit functions called *by name* from inside another jit function.

    A device helper is not a launch surface — it inherits its tile from the
    kernel that calls it, so the grid convention is not its business. The
    distinction is structural: helpers appear as bare calls, kernels are
    subscripted.
    """
    helpers: set[str] = set()
    for _, node in _triton_functions():
        if not _is_jit(node):
            continue
        for inner in ast.walk(node):
            if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name):
                helpers.add(inner.func.id)
    return helpers


def _param_names(node: ast.FunctionDef) -> set[str]:
    return {a.arg for a in (*node.args.args, *node.args.kwonlyargs)}


def _calls(node: ast.FunctionDef) -> set[str]:
    return {ast.unparse(n.func) for n in ast.walk(node) if isinstance(n, ast.Call)}


TILED_KERNELS = [
    (path, node)
    for path, node in _triton_functions()
    if _is_jit(node)
    and node.name not in _device_helpers()
    and _param_names(node) & _TILED_BLOCK_NAMES
]


def test_the_census_is_not_empty() -> None:
    """A census that finds nothing would pass every assertion below."""
    assert len(TILED_KERNELS) == 14, [n.name for _, n in TILED_KERNELS]


def test_grid_2d_is_row_major_over_the_output() -> None:
    assert grid_2d(7, 5, 4, 2) == (cdiv(7, 4), cdiv(5, 2)) == (2, 3)


@pytest.mark.parametrize(("kernel",), [(n.name,) for _, n in TILED_KERNELS])
def test_a_tiled_kernel_takes_its_tile_from_the_helper(kernel: str) -> None:
    """The pid binding is in `grid.py` and nowhere else."""
    node = next(n for _, n in TILED_KERNELS if n.name == kernel)
    assert "grid.tile_2d" in _calls(node), f"{kernel} builds its own tile"
    assert not [call for call in _calls(node) if call.endswith("program_id")], (
        f"{kernel} reads tl.program_id itself"
    )


@pytest.mark.parametrize(("kernel",), [(n.name,) for _, n in TILED_KERNELS])
def test_a_tiled_kernel_stores_through_the_helper(kernel: str) -> None:
    """A 2-D store address is computed once, in `grid.store_2d`."""
    node = next(n for _, n in TILED_KERNELS if n.name == kernel)
    assert "grid.store_2d" in _calls(node), f"{kernel} builds its own store address"
    for call in ast.walk(node):
        if (
            isinstance(call, ast.Call)
            and ast.unparse(call.func) == "tl.store"
            and len(call.args) > 1
        ):
            storee = ast.unparse(call.args[1])
            assert not storee.endswith("[:, None]"), (
                f"{kernel} stores a 2-D tile at a hand-built address"
            )


@CUDA
def test_a_transposed_grid_is_detected_not_tolerated() -> None:
    """The class the lock forbids is real: it leaves part of the output unwritten.

    Launched with the transposed grid, a tiled kernel raises nothing and returns
    a plausible tensor with a region of it still at its initial value — which is
    why the convention is code and every one of the six spec files uses extents
    that are not multiples of their block.
    """
    torch.manual_seed(0)
    pytest.importorskip("triton")

    from computronium.acceleration.hebbian_kernels import _hebbian_update_kernel

    if _hebbian_update_kernel is False:
        pytest.skip("triton is unavailable, so the kernel was never defined")

    b, d_in, d_out, block = 4, 20, 40, 16
    pre = torch.randn(b, d_in, device="cuda")
    post = torch.randn(b, d_out, device="cuda")
    weight = torch.randn(d_out, d_in, device="cuda")

    def launch(grid: tuple[int, int]) -> torch.Tensor:
        delta = torch.empty(d_out, d_in, device="cuda")
        _hebbian_update_kernel[grid](
            pre,
            post,
            weight,
            delta,
            b,
            d_in,
            d_out,
            0.01,
            False,
            BLOCK_IN=block,
            BLOCK_OUT=block,
        )
        return delta

    correct = launch(grid_2d(d_out, d_in, block, block))
    transposed = launch(grid_2d(d_in, d_out, block, block))

    expected = 0.01 * (post.T @ pre) / b
    torch.testing.assert_close(correct, expected, atol=1e-5, rtol=1e-4)
    assert not torch.allclose(transposed, expected, atol=1e-3)
