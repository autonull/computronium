"""Full-regime acceptance evidence — one U1 run over the whole ``digits`` split.

The gate in ``test_unified_kernel.py`` runs at the measured regime
(``MEASURED_BATCH_LIMIT`` batches, TODO46 §6.1): it locks orchestration and
measurement identity, and neither needs 45 batches. This module runs the same
pipeline *unbounded* — every training batch and every validation batch — so the
claim "the evaluator measures real training" has one expensive-but-optional
witness. Filename stamps ``pytest.mark.demo`` (``tests/conftest.py``), so it
stays out of the default gate and runs only under ``pytest -m demo``.
"""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING

import pytest

from computronium.experiment.evidence import RecordStore, StoreConfig
from computronium.experiment.execution import (
    Budget,
    LocalBackend,
    PipelineConfig,
    PipelineRunner,
    SimpleCostModel,
    StratifiedRandomPolicy,
)
from computronium.experiment.schema import (
    MEASURED_PARAM_BUDGET,
    RunSpec,
    seed_all_registries,
)

if TYPE_CHECKING:
    from pathlib import Path

FULL_REGIME_BATCH_LIMIT = 0


@pytest.fixture(scope="module", autouse=True)
def _seed_registries() -> None:
    seed_all_registries()


def _full_regime_spec() -> RunSpec:
    return RunSpec(
        profile="acceptance",
        task="digits",
        objectives=("validation_accuracy", "walltime_total"),
        fidelity="L0",
        n_seeds=1,
        epochs=1,
        budget_seconds=600.0,
        param_budget=MEASURED_PARAM_BUDGET,
        batch_limit=FULL_REGIME_BATCH_LIMIT,
    )


@pytest.mark.timeout(1800)
def test_u1_full_regime_produces_real_measurements(tmp_path: Path) -> None:
    """One unbounded run: records carry real accuracy, and it clears chance."""
    spec = _full_regime_spec()
    with RecordStore(StoreConfig(path=tmp_path / "full_regime.duckdb")) as store:
        run_id = store.create_run(spec=spec)
        config = PipelineConfig(
            run_id=run_id,
            run_spec=spec,
            budget=Budget.from_duration("600s"),
            cost_model=SimpleCostModel(),
            policy=StratifiedRandomPolicy(seed=42),
            backend=LocalBackend(),
            seed=spec.seed,
            max_rounds=2,
            min_rounds=1,
        )
        started = time.monotonic()
        records = asyncio.run(PipelineRunner(config, store).run())
        elapsed = time.monotonic() - started

        measured = [r for r in records if r.payload.get("train_acc") is not None]
        assert measured, "full-regime run produced no measured record"
        accuracies = [float(r.payload["train_acc"]) for r in measured]
        print(
            f"\nfull regime: {len(measured)}/{len(records)} records measured, "
            f"train_acc {min(accuracies):.3f}-{max(accuracies):.3f}, "
            f"{elapsed:.1f}s total, {elapsed / len(records):.2f}s/cell"
        )
        assert all(0.0 <= a <= 1.0 for a in accuracies)
        assert max(accuracies) > 0.1, "no cell beat chance on a full digits epoch"
        store.finish_run(run_id, "completed")
