"""S6 truth-table probe: which axis pairs actually compose on this tree.

TODO91 S6 found cells the declared void constraints admit but composition
refuses. That means >=2 tables state the same rule (the declared constraints,
``SystemConfig.validate``, and ``search_space``'s defense checks) and disagree.
This probe measures the mechanism truth — attempt a compose for every value of
one axis against every value of another, over a few randomized fillers — so the
declared table can be corrected from evidence rather than from any of the
copies.
"""

from __future__ import annotations

import random
from collections import defaultdict

from computronium.experiment.schema.seed_registries import seed_all_registries

seed_all_registries()

from computronium.domains.factory import create_task  # ruff: ignore[module-import-not-at-top-of-file]
from computronium.experiment.kernel.compose import compose_cell_system  # ruff: ignore[module-import-not-at-top-of-file]
from computronium.experiment.kernel.evaluate import task_shape  # ruff: ignore[module-import-not-at-top-of-file]
from computronium.experiment.schema.axis import AXES_REGISTRIES, StructuralAxis  # ruff: ignore[module-import-not-at-top-of-file]
from computronium.experiment.schema.coordinate import Coordinate  # ruff: ignore[module-import-not-at-top-of-file]

AXES = ("substrate", "geometry", "dynamics", "plasticity", "credit", "update")
NAMES = {
    axis: list(AXES_REGISTRIES[StructuralAxis[axis.upper()]].keys()) for axis in AXES
}


def attempt(task, shape, selection: dict[str, str]) -> str:
    try:
        compose_cell_system(
            coordinate=Coordinate(**selection, params={}),
            geometry={},
            input_shape=shape.input_shape,
            output_dim=shape.output_dim,
            param_budget=50_000,
            task=task,
        )
        return "ok"  # ruff: ignore[try-consider-else]
    except Exception as exc:  # measurement: the exception text is the finding
        return f"{type(exc).__name__}: {exc}"


def pair_table(task_id: str, left: str, right: str, fillers: int = 6) -> None:
    task = create_task(task_id, device="cpu", quick_mode=True)
    task.setup()
    shape = task_shape(task_id, "cpu")
    rng = random.Random(0)  # ruff: ignore[suspicious-non-cryptographic-random-usage]
    outcomes: dict[tuple[str, str], set[str]] = defaultdict(set)
    for lval in NAMES[left]:
        for rval in NAMES[right]:
            for _ in range(fillers):
                selection = {axis: rng.choice(NAMES[axis]) for axis in AXES}
                selection[left] = lval
                selection[right] = rval
                outcomes[lval, rval].add(attempt(task, shape, selection))
    print(f"\n### {left} x {right} on {task_id}")
    for lval in NAMES[left]:
        refused: dict[str, list[str]] = defaultdict(list)
        for rval in NAMES[right]:
            results = outcomes[lval, rval]
            if not any(r == "ok" for r in results):
                refused[next(iter(results))].append(rval)
        for reason, rvals in refused.items():
            print(f"{lval}: never composes with {rvals}")
            print(f"    {reason[:150]}")


if __name__ == "__main__":
    pair_table("iris", "geometry", "dynamics")
    pair_table("iris", "substrate", "dynamics")
