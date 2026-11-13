"""S6 pricing probe: what a legality check and one composed step actually cost.

Measured 2026-11-13 for TODO91 S6. The plan's §4 quote (~75 ms/candidate,
~5 % legal) came from the paged candidate walk, which also composes each cell
to decide legality. This probe separates the three costs so the combinations
command can price its own scan:

1. void-constraint evaluation on a fixed 6-tuple,
2. a full composed step (compose_cell_system + forward/backward/step),
3. the paged `iter_candidates` walk (the number §4 quotes).
"""

from __future__ import annotations

import time
from itertools import product

import torch

from computronium.experiment.kernel.evaluate import task_shape
from computronium.experiment.kernel.search_space import (
    _compiled_void_constraints,
    _void_pass,
)
from computronium.experiment.schema.axis import AXES_REGISTRIES, StructuralAxis

AXES = (
    StructuralAxis.SUBSTRATE,
    StructuralAxis.GEOMETRY,
    StructuralAxis.DYNAMICS,
    StructuralAxis.PLASTICITY,
    StructuralAxis.CREDIT,
    StructuralAxis.UPDATE,
)


def main() -> None:
    indep, dep = _compiled_void_constraints()
    values = [list(AXES_REGISTRIES[axis].keys()) for axis in AXES]
    n = 2000
    combos = list(product(*values))[:n]
    start = time.perf_counter()
    legal = sum(_void_pass(indep, dep, combo, "iris") for combo in combos)
    void_s = time.perf_counter() - start
    print(
        f"void checks: {n} in {void_s:.3f}s = {1000 * void_s / n:.4f} ms/candidate; "
        f"legal {legal}/{n} ({100 * legal / n:.1f}%)"
    )

    from computronium.domains.factory import create_task
    from computronium.experiment.kernel.compose import compose_cell_system
    from computronium.experiment.schema.coordinate import Coordinate

    task = create_task("iris", device="cpu", quick_mode=True)
    task.setup()
    shape = task_shape("iris", "cpu")
    coordinate = Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="instantaneous",
        plasticity="null",
        credit="gradient",
        update="adam",
        params={},
    )
    start = time.perf_counter()
    cell = compose_cell_system(
        coordinate=coordinate,
        geometry={},
        input_shape=shape.input_shape,
        output_dim=shape.output_dim,
        param_budget=50_000,
        task=task,
    )
    compose_s = time.perf_counter() - start

    x, y = next(iter(task.get_dataloader("train")))
    start = time.perf_counter()
    out = cell.system(x)
    loss = torch.nn.functional.cross_entropy(out, y)
    loss.backward()
    for param in cell.system.parameters():
        if param.grad is not None:
            param.data -= 1e-3 * param.grad
    step_s = time.perf_counter() - start
    print(
        f"compose {compose_s * 1000:.1f} ms; one fwd/bwd/step {step_s * 1000:.1f} ms; "
        f"params {cell.param_count}"
    )


if __name__ == "__main__":
    main()
