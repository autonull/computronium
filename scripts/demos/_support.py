"""Shared support for kernel demos (TODO44 Phase F).

Every demo composes the kernel exactly as ``tests/acceptance/unified_kernel.py``
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
from computronium.experiment.execution.search_space import SearchSpace
from computronium.experiment.execution.stage import StageId
from computronium.experiment.schema.record import Record
from computronium.experiment.schema.seed_registries import seed_all_registries

STAGES = (
    "s1_frame",
    "s2_space",
    "s3_schedule",
    "s4_gate",
    "s5_compose",
    "s6_train",
    "s7_measure",
    "s8_record",
    "s9_attribute",
    "s10_decide",
    "s11_report",
)


def make_run_spec(task: str = "digits") -> dict[str, Any]:
    return {
        "profile": "acceptance",
        "task": task,
        "objectives": ["accuracy", "walltime_s"],
        "stages": list(STAGES),
        "fidelity": "L0",
        "seeds": 1,
        "epochs": 1,
        "budget_seconds": 60.0,
    }


def make_search_space() -> SearchSpace:
    from computronium.experiment.schema.axis import AXES_REGISTRIES, StructuralAxis
    from computronium.experiment.schema.registries import (
        CONSTRAINTS_REGISTRY,
        OBJECTIVES_REGISTRY,
    )

    axes_snapshot = [
        spec
        for axis_kind in StructuralAxis
        for spec in AXES_REGISTRIES[axis_kind].values()
        if spec.available
    ]
    return SearchSpace(
        axes_snapshot=tuple(axes_snapshot),
        constraints=tuple(CONSTRAINTS_REGISTRY.values()),
        objectives=tuple(OBJECTIVES_REGISTRY.values()),
        tasks=("default",),
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
    run_spec: dict[str, Any],
    policy_name: str,
    max_rounds: int,
    checkpoint_root: Path | None,
) -> PipelineConfig:
    return PipelineConfig(
        run_id=run_id,
        run_spec=run_spec,
        stages=[StageId(s) for s in run_spec["stages"]],
        budget=Budget.from_duration(f"{int(run_spec['budget_seconds'])}s"),
        cost_model=SimpleCostModel(),
        policy=make_policy(policy_name),
        allocator=EvidenceDrivenAllocator(promotion_threshold=0.05),
        backend=LocalBackend(),
        checkpoint_dir=checkpoint_root / run_id if checkpoint_root else None,
        seed=42,
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
