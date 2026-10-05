"""Shared support for kernel demos (TODO44 Phase F).

Every demo composes the kernel exactly as ``tests/acceptance/test_unified_kernel.py``
does: RunSpec → SearchSpace → ProposalPolicy → PipelineRunner → RecordStore.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.execution.allocator import EvidenceDrivenAllocator
from computronium.experiment.execution.backends import LocalBackend
from computronium.experiment.execution.budget import Budget, SimpleCostModel
from computronium.experiment.execution.pipeline import PipelineConfig, PipelineRunner
from computronium.experiment.execution.policy import (
    EvolutionPolicy,
    ModelBasedPolicy,
    StratifiedRandomPolicy,
    SynthesisPolicy,
    UniformRandomPolicy,
)
from computronium.experiment.execution.stage import StageId
from computronium.experiment.schema.record import Record
from computronium.experiment.schema.run_spec import RunSpec
from computronium.experiment.schema.seed_registries import seed_all_registries

STAGES = tuple(s.value for s in StageId)


def make_run_spec(task: str = "digits") -> RunSpec:
    return RunSpec(
        profile="acceptance",
        task=task,
        objectives=("validation_accuracy", "walltime_total"),
        stages=STAGES,
        fidelity="L0",
        n_seeds=1,
        epochs=1,
        budget_seconds=60.0,
    )


def make_policy(name: str):
    catalog: dict[str, Any] = {
        "stratified_random": StratifiedRandomPolicy(seed=42),
        "uniform_random": UniformRandomPolicy(seed=42),
        "model_based_tpe": ModelBasedPolicy(sampler="tpe", seed=42, n_startup_trials=5),
        "evolution": EvolutionPolicy(population_size=10, seed=42),
        "synthesis": SynthesisPolicy(
            policies=[StratifiedRandomPolicy(seed=42), UniformRandomPolicy(seed=43)],
            weights=[1.0, 1.0],
        ),
    }
    return catalog[name]


def make_pipeline_config(
    run_id: str,
    run_spec: RunSpec,
    policy_name: str,
    max_rounds: int,
) -> PipelineConfig:
    return PipelineConfig(
        run_id=run_id,
        run_spec=run_spec,
        budget=Budget.from_duration(f"{int(run_spec.budget_seconds or 0)}s"),
        cost_model=SimpleCostModel(),
        policy=make_policy(policy_name),
        allocator=EvidenceDrivenAllocator(promotion_threshold=0.05),
        backend=LocalBackend(),
        seed=run_spec.seed,
        max_rounds=max_rounds,
        min_rounds=1,
    )


def run_pipeline(config: PipelineConfig, store: RecordStore) -> list[Record]:
    return asyncio.run(PipelineRunner(config, store).run())


def open_store(store_path: Path) -> RecordStore:
    return RecordStore(StoreConfig(path=store_path))


def fresh_store(tmp_root: Path, name: str) -> tuple[RecordStore, Path]:
    tmp_root.mkdir(parents=True, exist_ok=True)
    path = tmp_root / f"{name}.duckdb"
    if path.exists():
        path.unlink()
    seed_all_registries()
    return open_store(path), path
