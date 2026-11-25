"""Settle compile lock: shape-dynamic tracing (TODO104 A2).

A ``dynamic=False`` settle graph re-traced per shape and hit
``config.recompile_limit`` on non-vision tasks, killing the cell with a leaked
semaphore. Removing ``dynamic=True`` must make this lock fail.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import torch

from computronium.ontology._settle_kernel import compile_settle

_SETTLE_MODULES = (
    "computronium/ontology/_settle_kernel.py",
    "computronium/ontology/dynamics/_dynamics.py",
)
_STATIC_COMPILE = re.compile(r"torch\.compile\(\s*[A-Za-z_]\w*\s*,\s*dynamic=False")


@pytest.mark.parametrize("module", _SETTLE_MODULES)
def test_no_static_compiled_settle(module: str) -> None:
    """Every settle kernel is compiled shape-dynamically."""
    root = Path(__file__).resolve().parents[2]
    source = (root / module).read_text(encoding="utf-8")
    offenders = _STATIC_COMPILE.findall(source)
    assert not offenders, (
        f"{module} compiles a settle kernel with dynamic=False "
        f"({len(offenders)} sites): use compile_settle"
    )


@pytest.mark.parametrize("module", _SETTLE_MODULES)
def test_settle_compiles_through_helper(module: str) -> None:
    """A direct ``torch.compile`` call in a settle module bypasses the helper."""
    root = Path(__file__).resolve().parents[2]
    source = (root / module).read_text(encoding="utf-8")
    direct = [
        line
        for line in source.splitlines()
        if "torch.compile(" in line and "return torch.compile" not in line
    ]
    assert not direct, f"{module} compiles directly: {direct}"


def _loop(acts: list[torch.Tensor], weights: tuple[torch.Tensor, ...]) -> torch.Tensor:
    for _ in range(2):
        new_acts = [acts[0]]
        for i, w in enumerate(weights):
            upper = acts[i + 1]
            error = acts[i] - upper @ w
            new_acts.append(upper + 0.1 * (error @ w.T))
        acts = new_acts
    return acts[-1]


@pytest.mark.timeout(300)
def test_one_graph_serves_two_shapes() -> None:
    """One traced graph serves two widths: no recompile per geometry."""
    compiled = compile_settle(_loop)
    with torch._dynamo.config.patch(recompile_limit=1):
        narrow = compiled(
            [torch.randn(2, 4), torch.randn(2, 4), torch.randn(2, 4)],
            (torch.randn(4, 4), torch.randn(4, 4)),
        )
        wide = compiled(
            [torch.randn(2, 8), torch.randn(2, 8), torch.randn(2, 8)],
            (torch.randn(8, 8), torch.randn(8, 8)),
        )
    assert narrow.shape == (2, 4)
    assert wide.shape == (2, 8)
    assert torch.isfinite(narrow).all()
    assert torch.isfinite(wide).all()
