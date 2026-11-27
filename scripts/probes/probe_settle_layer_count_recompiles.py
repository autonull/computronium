"""D14 follow-up: settle recompiles under a layer-count sweep.

`compile_settle` traces with `dynamic=True`, so a hidden width reuses one
graph. A layer-count change (the number of weights in the settle loop) is a
Python loop bound, not a tensor shape. This counts the graphs Dynamo builds
for depth 2..10 in one process and times the steady state, so a shape bucket
or padding is adopted only if it removes the recompiles without slowing it.

Informs TODO107 D14 follow-up.
"""

from __future__ import annotations

import time

import torch

from computronium.ontology._settle_kernel import (
    _compiled_layered_settle_digital,
)

DEPTHS = tuple(range(2, 11))
WIDTH = 16
STEPS = 5


def graphs() -> int:
    stats = torch._dynamo.utils.counters.get("stats", {})
    return int(stats.get("unique_graphs", 0))


def settle_once(depth: int) -> float:
    generator = torch.Generator().manual_seed(depth)
    weights = tuple(
        torch.randn(WIDTH, WIDTH, generator=generator) for _ in range(depth)
    )
    acts = [torch.randn(WIDTH, WIDTH, generator=generator) for _ in range(depth + 1)]
    start = time.perf_counter()
    _compiled_layered_settle_digital(acts, weights, 0.1, STEPS)
    return time.perf_counter() - start


def main() -> None:
    torch._dynamo.reset()
    torch._dynamo.config.cache_size_limit = 64
    torch._dynamo.config.suppress_errors = True

    before = graphs()
    for depth in DEPTHS:
        settle_once(depth)  # compile
        steady = min(settle_once(depth) for _ in range(3))
        print(
            f"depth={depth:2d} graphs={graphs() - before:2d} "
            f"steady={steady * 1e3:.2f} ms"
        )
    print(f"total graphs: {graphs() - before} for {len(DEPTHS)} depths")


if __name__ == "__main__":
    main()
