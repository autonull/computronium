"""Price every dynamics primitive on the campaign's own regime (TODO48 D3).

A cell is one measurement of one coordinate at L0/1 epoch/batch_limit 2 on
`digits`, feedforward x fast_weights x gradient x euclidean. The campaign's
economics are decided by which dynamics it sweeps, so the cost belongs in a
registry, not in a session's memory. Measured 2026-10-03 on 16 CPU cores.
"""

from __future__ import annotations

import asyncio
import time
from pathlib import Path

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.execution.backends import LocalBackend
from computronium.experiment.execution.budget import Budget, SimpleCostModel
from computronium.experiment.execution.pipeline import PipelineConfig, PipelineRunner
from computronium.experiment.execution.policy import StratifiedRandomPolicy
from computronium.experiment.schema.axis import Domain, StructuralAxis
from computronium.experiment.schema.run_spec import (
    MEASURED_BATCH_LIMIT,
    MEASURED_PARAM_BUDGET,
    AxisSelection,
    RunSpec,
)
from computronium.experiment.schema.seed_registries import seed_all_registries

CELLS = 3


def _spec(dynamics: str) -> RunSpec:
    return RunSpec(
        profile=f"cost-{dynamics}",
        task="digits",
        objectives=("validation_accuracy",),
        fidelity="L0",
        n_seeds=1,
        epochs=1,
        budget_seconds=600.0,
        param_budget=MEASURED_PARAM_BUDGET,
        batch_limit=MEASURED_BATCH_LIMIT,
        # Five sweep points: one cell per dynamics would amortize the pipeline's
        # fixed cost over a single measurement and price startup, not dynamics.
        hyperparameters={"update_lr": Domain(lo=0.001, hi=0.01)},
        axes=(
            AxisSelection(axis=StructuralAxis.SUBSTRATE, primitives=("digital",)),
            AxisSelection(axis=StructuralAxis.GEOMETRY, primitives=("feedforward",)),
            AxisSelection(axis=StructuralAxis.DYNAMICS, primitives=(dynamics,)),
            AxisSelection(axis=StructuralAxis.PLASTICITY, primitives=("fast_weights",)),
            AxisSelection(axis=StructuralAxis.CREDIT, primitives=("gradient",)),
            AxisSelection(axis=StructuralAxis.UPDATE, primitives=("euclidean",)),
        ),
    )


def price(dynamics: str, tmp: Path) -> tuple[int, float, str]:
    path = tmp / f"{dynamics}.duckdb"
    spec = _spec(dynamics)
    with RecordStore(StoreConfig(path=path)) as store:
        run_id = store.create_run(spec=spec)
        config = PipelineConfig(
            run_id=run_id,
            run_spec=spec,
            budget=Budget.from_duration("10m", target_cells=CELLS),
            cost_model=SimpleCostModel(),
            backend=LocalBackend(),
            policy=StratifiedRandomPolicy(seed=42),
            seed=spec.seed,
            max_rounds=3,
            min_rounds=1,
        )
        runner = PipelineRunner(config, store)
        start = time.perf_counter()
        asyncio.run(runner.run())
        elapsed = time.perf_counter() - start
        measured = store.count_records(run_id=run_id)
        causes = sorted({str(r.get("cause")) for r in runner.rejections})
    return measured, elapsed, ",".join(causes) or "-"


def main() -> None:
    import tempfile

    seed_all_registries()
    primitives = (
        "energy_minimization",
        "lazy",
        "instantaneous",
        "predictive_settling",
        "error_predictive_coding",
        "pc_alm",
        "diffusion",
        "spike_integration",
    )
    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        print(f"{'dynamics':26s} {'cells':>5s} {'s/cell':>8s}  rejected")
        for dynamics in primitives:
            measured, elapsed, causes = price(dynamics, tmp)
            per_cell = elapsed / measured if measured else float("nan")
            print(f"{dynamics:26s} {measured:5d} {per_cell:8.3f}  {causes}")


if __name__ == "__main__":
    main()
