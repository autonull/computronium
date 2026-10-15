"""Online baseline discovery and registry.

Baselines are discovered run types, not constants. Standard optimizers/
architectures run on the same task, seeds, budget, and hardware fingerprint.
Stored as BaselineRecord tagged (task, hardware_fingerprint, budget, seeds).

Ruler vocabulary (bp_deficit, ruler_*_ratio) provides the comparison framework.
Where the backprop ruler cannot run on the winning geometry (tile_mesh), an
equivalent-capacity fallback geometry is used and the substitution is recorded
as an explicit evidence limitation.
"""

from __future__ import annotations

import hashlib
import json
import logging
import subprocess  # ruff: ignore[suspicious-subprocess-import] -- controlled git call
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from computronium.experiment.environment.snapshots import EnvironmentCapture
from computronium.experiment.registry.provenance import compute_config_sha256
from computronium.experiment.schema.axis import Domain  # ruff: ignore[typing-only-first-party-import] -- used at runtime for Domain(members=...)
from computronium.experiment.schema.run_spec import RunSpec

if TYPE_CHECKING:
    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.registry.seed import SeedContext

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class BaselineConfig:
    """Configuration for a baseline optimizer/architecture."""

    name: str
    description: str
    domain: str  # vision, language, rl, graph, tabular, memory
    optimizer: str  # sgd, adam, adamw, etc.
    architecture: str  # mlp, cnn, small_lm, etc.
    geometry: str  # feedforward, recurrent, etc.
    credit: str  # gradient (backprop)
    dynamics: str  # instantaneous
    update: str  # euclidean, adam
    plasticity: str  # null
    substrate: str  # digital
    hyperparameters: dict[str, Any] = field(default_factory=dict)
    applicable_tasks: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class BaselineRecord:
    """A discovered baseline result for a (task, hardware, budget, seeds) tuple."""

    task: str
    hardware_fingerprint: str
    budget_seconds: float
    n_seeds: int
    optimizer: str
    architecture: str
    geometry: str
    metrics: dict[str, float]  # task metrics (accuracy, perplexity, etc.)
    cost_metrics: dict[str, float]  # walltime, energy, param_count, etc.
    ruler_metrics: dict[str, float]  # bp_deficit=0, ruler_*_ratio=1.0
    run_id: str
    config_sha256: str
    created_at: float = field(default_factory=time.time)
    git_sha: str = "unknown"
    fallback_geometry: str | None = None  # for C12: tile_mesh -> feedforward

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaselineRecord:
        return cls(**data)

    def key(self) -> tuple[str, str, float, int]:
        """Unique lookup key: (task, hardware_fingerprint, budget, seeds)."""
        return (self.task, self.hardware_fingerprint, self.budget_seconds, self.n_seeds)


class BaselineRegistry:
    """Registry of baseline configurations and discovered baseline records."""

    # Standard baseline configurations per domain
    STANDARD_BASELINES: tuple[BaselineConfig, ...] = (
        # Vision baselines
        BaselineConfig(
            name="vision_sgd_mlp",
            description="SGD on feedforward MLP (vision)",
            domain="vision",
            optimizer="sgd",
            architecture="mlp",
            geometry="feedforward",
            credit="gradient",
            dynamics="instantaneous",
            update="euclidean",
            plasticity="null",
            substrate="digital",
            hyperparameters={"dynamics.step_size": Domain(members=(0.01,))},
            applicable_tasks=("digits", "mnist", "fashion_mnist", "cifar10"),
        ),
        BaselineConfig(
            name="vision_adam_mlp",
            description="Adam on feedforward MLP (vision)",
            domain="vision",
            optimizer="adam",
            architecture="mlp",
            geometry="feedforward",
            credit="gradient",
            dynamics="instantaneous",
            update="adam",
            plasticity="null",
            substrate="digital",
            hyperparameters={
                "dynamics.step_size": Domain(members=(1e-3,)),
                "update.beta2": Domain(members=(0.999,)),
                "update.eps": Domain(members=(1e-8,)),
            },
            applicable_tasks=("digits", "mnist", "fashion_mnist", "cifar10"),
        ),
        BaselineConfig(
            name="vision_adamw_cnn",
            description="AdamW on small CNN (vision)",
            domain="vision",
            optimizer="adamw",
            architecture="cnn",
            geometry="conv",
            credit="gradient",
            dynamics="instantaneous",
            update="adam",
            plasticity="null",
            substrate="digital",
            hyperparameters={
                "dynamics.step_size": Domain(members=(3e-4,)),
                "update.beta2": Domain(members=(0.999,)),
                "update.eps": Domain(members=(1e-8,)),
            },
            applicable_tasks=("cifar10", "cifar100"),
        ),
        # Language baselines
        BaselineConfig(
            name="language_adamw_small_lm",
            description="AdamW on small causal transformer (language)",
            domain="language",
            optimizer="adamw",
            architecture="small_lm",
            geometry="causal_transformer",
            credit="gradient",
            dynamics="instantaneous",
            update="adam",
            plasticity="null",
            substrate="digital",
            hyperparameters={
                "dynamics.step_size": Domain(members=(3e-4,)),
                "update.beta2": Domain(members=(0.999,)),
                "update.eps": Domain(members=(1e-8,)),
            },
            applicable_tasks=("wikitext2", "ptb", "copyshake"),
        ),
        # Tabular baselines
        BaselineConfig(
            name="tabular_adam_mlp",
            description="Adam on feedforward MLP (tabular)",
            domain="tabular",
            optimizer="adam",
            architecture="mlp",
            geometry="feedforward",
            credit="gradient",
            dynamics="instantaneous",
            update="adam",
            plasticity="null",
            substrate="digital",
            hyperparameters={
                "dynamics.step_size": Domain(members=(1e-3,)),
                "update.beta2": Domain(members=(0.999,)),
                "update.eps": Domain(members=(1e-8,)),
            },
            applicable_tasks=("iris", "xor", "spiral"),
        ),
        # RL baselines
        BaselineConfig(
            name="rl_ppo_mlp",
            description="PPO on feedforward MLP (RL)",
            domain="rl",
            optimizer="adam",
            architecture="mlp",
            geometry="feedforward",
            credit="gradient",
            dynamics="instantaneous",
            update="adam",
            plasticity="null",
            substrate="digital",
            hyperparameters={
                "dynamics.step_size": Domain(members=(3e-4,)),
                "update.beta2": Domain(members=(0.999,)),
                "update.eps": Domain(members=(1e-8,)),
            },
            applicable_tasks=("cartpole", "mountaincar"),
        ),
        # Graph baselines
        BaselineConfig(
            name="graph_adam_gnn",
            description="Adam on graph neural network (graph)",
            domain="graph",
            optimizer="adam",
            architecture="gnn",
            geometry="graph",
            credit="gradient",
            dynamics="instantaneous",
            update="adam",
            plasticity="null",
            substrate="digital",
            hyperparameters={
                "dynamics.step_size": Domain(members=(1e-3,)),
                "update.beta2": Domain(members=(0.999,)),
                "update.eps": Domain(members=(1e-8,)),
            },
            applicable_tasks=("cora", "citeseer", "pubmed"),
        ),
        # Memory baselines
        BaselineConfig(
            name="memory_adam_ntm",
            description="Adam on Neural Turing Machine (memory)",
            domain="memory",
            optimizer="adam",
            architecture="ntm",
            geometry="ntm",
            credit="gradient",
            dynamics="instantaneous",
            update="adam",
            plasticity="null",
            substrate="digital",
            hyperparameters={
                "dynamics.step_size": Domain(members=(1e-3,)),
                "update.beta2": Domain(members=(0.999,)),
                "update.eps": Domain(members=(1e-8,)),
                "geometry.mem_slots": Domain(members=(20,)),
                "geometry.mem_width": Domain(members=(20,)),
            },
            applicable_tasks=("copy_task", "associative_recall"),
        ),
    )

    def __init__(self, store: RecordStore | None = None) -> None:
        self._store = store
        self._cache: dict[tuple, BaselineRecord] = {}

    @property
    def store(self) -> RecordStore | None:
        return self._store

    @store.setter
    def store(self, value: RecordStore) -> None:
        self._store = value

    def get_baselines_for_task(self, task: str) -> list[BaselineConfig]:
        """Get applicable baseline configurations for a task."""
        return [b for b in self.STANDARD_BASELINES if task in b.applicable_tasks]

    def get_fallback_geometry(self, geometry: str) -> str | None:
        """Get fallback geometry for ruler-incompatible geometries (C12).

        Returns the fallback geometry if the given geometry cannot run
        the backprop ruler, otherwise None.
        """
        fallbacks = {
            "tile_mesh": "feedforward",
            "tile": "feedforward",
            "recurrent": "feedforward",
            "causal_transformer": "feedforward",
            "attention": "feedforward",
            "graph": "feedforward",
            "nca": "feedforward",
            "ntm": "feedforward",
            "spatial_lattice": "feedforward",
        }
        return fallbacks.get(geometry)

    def compute_hardware_fingerprint(self) -> str:
        """Compute hardware fingerprint from environment snapshot."""
        capture = EnvironmentCapture()
        snapshot = capture.capture()
        # Use system info for fingerprint
        hw_data = {
            "platform": snapshot.system.platform,
            "architecture": snapshot.system.architecture,
            "cpu_count": snapshot.system.cpu_count,
            "memory_gb": snapshot.system.memory_gb,
            "gpu_info": snapshot.system.gpu_info,
            "cuda_version": snapshot.system.cuda_version,
        }
        hw_json = json.dumps(hw_data, sort_keys=True)
        return hashlib.sha256(hw_json.encode()).hexdigest()[:16]

    def make_baseline_run_spec(
        self,
        task: str,
        baseline: BaselineConfig,
        budget_seconds: float,
        n_seeds: int,
        seed_context: SeedContext,
        sweep_steps: int = 30,
    ) -> RunSpec:
        """Create a RunSpec for running a baseline."""
        from computronium.experiment.schema.axis import StructuralAxis
        from computronium.experiment.schema.registries import StageId
        from computronium.experiment.schema.run_spec import AxisSelection

        # Use the baseline's structural choices
        axes = (
            AxisSelection(
                axis=StructuralAxis.SUBSTRATE, primitives=(baseline.substrate,)
            ),
            AxisSelection(
                axis=StructuralAxis.GEOMETRY, primitives=(baseline.geometry,)
            ),
            AxisSelection(
                axis=StructuralAxis.DYNAMICS, primitives=(baseline.dynamics,)
            ),
            AxisSelection(
                axis=StructuralAxis.PLASTICITY, primitives=(baseline.plasticity,)
            ),
            AxisSelection(axis=StructuralAxis.CREDIT, primitives=(baseline.credit,)),
            AxisSelection(axis=StructuralAxis.UPDATE, primitives=(baseline.update,)),
        )

        return RunSpec(
            profile=f"baseline_{baseline.name}",
            task=task,
            objectives=("validation_accuracy", "walltime_total", "param_count"),
            stages=(
                StageId.S1_FRAME,
                StageId.S2_SPACE,
                StageId.S3_SCHEDULE,
                StageId.S4_GATE,
                StageId.S5_COMPOSE,
                StageId.S6_TRAIN,
                StageId.S7_MEASURE,
                StageId.S8_RECORD,
                StageId.S9_ATTRIBUTE,
                StageId.S10_DECIDE,
                StageId.S11_REPORT,
            ),
            fidelity="L1",
            n_seeds=n_seeds,
            epochs=10,  # Sufficient for baseline convergence
            batch_limit=0,
            budget_seconds=budget_seconds,
            param_budget=1_000_000,
            policy="round_robin_grid",
            axes=axes,
            hyperparameters=baseline.hyperparameters,
            checkpoint_every_n=100,
            seed=seed_context.master_seed,
            device="auto",
            sweep_steps=sweep_steps,
            code_sha=self._get_git_sha(),
            dataset=task,
            dataset_version="1.0",
        )

    async def discover_baseline(
        self,
        task: str,
        budget_seconds: float,
        n_seeds: int,
        seed_context: SeedContext,
    ) -> list[BaselineRecord]:
        """Discover baselines for a task on current hardware.

        Runs all applicable standard baselines and stores results.
        """
        from computronium.experiment.evidence.store import RecordStore, StoreConfig
        from computronium.experiment.execution.backends import LocalBackend
        from computronium.experiment.execution.deadline import Deadline
        from computronium.experiment.execution.pipeline import (
            PipelineConfig,
            PipelineRunner,
        )
        from computronium.experiment.kernel.evaluate import task_shape
        from computronium.experiment.surface.cli import create_policy, policy_context

        hardware_fp = self.compute_hardware_fingerprint()
        baselines = self.get_baselines_for_task(task)

        if not baselines:
            logger.warning("No standard baselines for task %s", task)
            return []

        results = []

        for baseline in baselines:
            # Check if baseline already exists
            existing = self.get_baseline(
                task, hardware_fp, budget_seconds, n_seeds, baseline.name
            )
            if existing:
                logger.info(
                    "Baseline %s for %s already exists, skipping", baseline.name, task
                )
                results.append(existing)
                continue

            logger.info("Discovering baseline: %s on %s", baseline.name, task)

            # Create run spec
            spec = self.make_baseline_run_spec(
                task, baseline, budget_seconds, n_seeds, seed_context
            )

            # Run baseline
            with tempfile.TemporaryDirectory() as tmpdir:
                store_path = Path(tmpdir) / "baseline.duckdb"
                store = RecordStore(StoreConfig(path=store_path))
                store.__enter__()

                try:
                    run_id = store.create_run(spec=spec)
                    deadline = (
                        Deadline.from_seconds(spec.budget_seconds)
                        if spec.budget_seconds
                        else None
                    )

                    policy = create_policy(
                        spec.policy or "round_robin_grid",
                        **policy_context(
                            spec,
                            spec.policy or "round_robin_grid",
                            shape=task_shape,
                            deadline=deadline,
                        ),
                    )

                    runner = PipelineRunner(
                        PipelineConfig(
                            run_id=run_id,
                            run_spec=spec,
                            deadline=deadline,
                            cost_model=None,
                            policy=policy,
                            backend=LocalBackend(max_workers=1),
                            seed=spec.seed,
                            max_rounds=None,
                        ),
                        store,
                    )

                    await runner.run()

                    # Extract metrics from store
                    records = store.query_records(run_id=run_id)
                    pass_records = [
                        r for r in records if r.status.gate_verdict.value == "PASS"
                    ]

                    if not pass_records:
                        logger.warning(
                            "Baseline %s produced no PASS records", baseline.name
                        )
                        continue

                    # Aggregate metrics across seeds
                    metrics = self._aggregate_metrics(pass_records)

                    # Create baseline record
                    baseline_record = BaselineRecord(
                        task=task,
                        hardware_fingerprint=hardware_fp,
                        budget_seconds=budget_seconds,
                        n_seeds=n_seeds,
                        optimizer=baseline.optimizer,
                        architecture=baseline.architecture,
                        geometry=baseline.geometry,
                        metrics=metrics.get("task", {}),
                        cost_metrics=metrics.get("cost", {}),
                        ruler_metrics={
                            "bp_deficit": 0.0,
                            "ruler_walltime_ratio": 1.0,
                            "ruler_energy_ratio": 1.0,
                            "ruler_param_ratio": 1.0,
                        },
                        run_id=run_id,
                        config_sha256=compute_config_sha256(spec.to_dict()),
                        git_sha=self._get_git_sha(),
                    )

                    # Store in cache
                    self._cache[baseline_record.key()] = baseline_record
                    results.append(baseline_record)

                    logger.info("Baseline %s completed: %s", baseline.name, metrics)

                finally:
                    store.__exit__(None, None, None)

        return results

    def _aggregate_metrics(self, records: list) -> dict[str, dict[str, float]]:
        """Aggregate metrics across seeds for baseline."""
        import statistics

        task_metrics = {}
        cost_metrics = {}

        # Task metric payload keys (values from MEASURED_OBJECTIVES for task-tagged objectives)
        task_metric_keys = {
            "val_acc",
            "test_acc",
            "f1_score",
            "test_loss",
            "val_loss",
            "val_ppl",
            "bleu_score",
            "mean_reward",
        }

        # Group by metric name
        metric_values: dict[str, list[float]] = {}
        for record in records:
            for key, value in record.payload.items():
                if isinstance(value, bool) or not isinstance(value, int | float):
                    continue
                if key in {
                    "epochs_completed",
                    "epochs_requested",
                    "seed",
                    "fidelity",
                    "param_count",
                    "param_budget",
                }:
                    continue
                metric_values.setdefault(key, []).append(float(value))

        for metric, values in metric_values.items():
            mean_val = statistics.mean(values)
            if metric in task_metric_keys:
                task_metrics[metric] = mean_val
            else:
                cost_metrics[metric] = mean_val

        return {"task": task_metrics, "cost": cost_metrics}

    def get_baseline(
        self,
        task: str,
        hardware_fp: str,
        budget_seconds: float,
        n_seeds: int,
        optimizer: str | None = None,
    ) -> BaselineRecord | None:
        """Get baseline record, running discovery if needed."""
        key = (task, hardware_fp, budget_seconds, n_seeds)
        if key in self._cache:
            record = self._cache[key]
            if optimizer is None or record.optimizer == optimizer:
                return record

        # Try to load from store if available
        if self._store:
            record = self._lookup_store_baseline(
                task, hardware_fp, budget_seconds, n_seeds, optimizer
            )
            if record is not None:
                self._cache[key] = record
                return record

        return None

    def _lookup_store_baseline(
        self,
        task: str,
        hardware_fp: str,
        budget_seconds: float,
        n_seeds: int,
        optimizer: str | None,
    ) -> BaselineRecord | None:
        """Derive the backprop ruler from the store's own gradient×instantaneous cells.

        The loop's axis sweep already measures ``credit=gradient`` with
        ``dynamics=instantaneous`` cells on the same task and hardware; those
        *are* the backprop baseline, so no separate discovery run is needed when
        they exist (TODO63 Phase 2). Costs carry through as the ruler's own
        cost metrics; the ruler-relative metrics are 1.0 by construction.
        """
        from computronium.experiment.schema.metrics import objective_metric
        from computronium.experiment.schema.record import GateVerdict

        store = self._store
        if store is None:
            return None
        records = [
            r
            for r in store.query_records()
            if r.schedule.task_id == task
            and r.credit == "gradient"
            and r.dynamics == "instantaneous"
            and r.status.gate_verdict is GateVerdict.PASS_
            and not r.status.quarantine
        ]
        if not records:
            return None

        val_key = objective_metric("validation_accuracy")
        scored = [
            (float(r.payload[val_key]), r)
            for r in records
            if isinstance(r.payload.get(val_key), int | float)
            and not isinstance(r.payload.get(val_key), bool)
        ]
        if not scored:
            return None
        _, best = max(scored, key=lambda pair: pair[0])
        task_metrics = {
            key: float(best.payload[key])
            for key in (
                val_key,
                objective_metric("validation_loss"),
                objective_metric("walltime_total"),
                objective_metric("param_count"),
            )
            if isinstance(best.payload.get(key), int | float)
            and not isinstance(best.payload.get(key), bool)
        }
        return BaselineRecord(
            task=task,
            hardware_fingerprint=hardware_fp,
            budget_seconds=budget_seconds,
            n_seeds=n_seeds,
            optimizer=optimizer or "sgd",
            architecture="mlp",
            geometry=best.geometry,
            metrics={val_key: task_metrics[val_key]},
            cost_metrics={
                key: value for key, value in task_metrics.items() if key != val_key
            },
            ruler_metrics={
                "bp_deficit": 0.0,
                "ruler_walltime_ratio": 1.0,
                "ruler_energy_ratio": 1.0,
                "ruler_param_ratio": 1.0,
            },
            run_id=best.run_id,
            config_sha256=compute_config_sha256({"source": "store", "task": task}),
            git_sha=self._get_git_sha(),
        )

    def _get_git_sha(self) -> str:
        """Get current git commit SHA."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],  # ruff: ignore[start-process-with-partial-path]
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            logger.debug("Failed to get git SHA: %s", e)
        return "unknown"


class BaselineGate:
    """Gate that enforces baseline comparison for promotions.

    A promotion requires a same-hardware, same-budget baseline.
    If absent, either runs one or blocks with explicit reason.
    """

    def __init__(self, registry: BaselineRegistry) -> None:
        self.registry = registry

    async def check_or_run(
        self,
        task: str,
        budget_seconds: float,
        n_seeds: int,
        seed_context: SeedContext,
    ) -> tuple[BaselineRecord | None, str | None]:
        """Check for baseline; run discovery if missing.

        Returns (baseline_record, reason_if_blocked).
        """
        hardware_fp = self.registry.compute_hardware_fingerprint()
        baseline = self.registry.get_baseline(
            task, hardware_fp, budget_seconds, n_seeds
        )

        if baseline:
            return baseline, None

        # No baseline exists - run discovery
        logger.info("No baseline for %s on %s, running discovery", task, hardware_fp)
        baselines = await self.registry.discover_baseline(
            task, budget_seconds, n_seeds, seed_context
        )

        if baselines:
            return baselines[0], None

        return (
            None,
            f"No baseline could be discovered for {task} on {hardware_fp} with budget {budget_seconds}s",
        )


def compute_ruler_metrics(
    cell_metrics: dict[str, float],
    baseline_metrics: dict[str, float],
    cell_cost: dict[str, float],
    baseline_cost: dict[str, float],
) -> dict[str, float]:
    """Compute ruler-relative metrics (bp_deficit, ruler_*_ratio).

    Args:
        cell_metrics: Payload metrics from the cell (keys like "val_acc", "val_ppl").
        baseline_metrics: Payload metrics from the baseline (same key space).
        cell_cost: Cost metrics from the cell.
        baseline_cost: Cost metrics from the baseline.
    """
    from computronium.experiment.schema.metrics import objective_metric

    val_acc_key = objective_metric("validation_accuracy")
    # bp_deficit = baseline_accuracy - cell_accuracy (lower = closer to ruler)
    bp_deficit = baseline_metrics.get(val_acc_key, 0.0) - cell_metrics.get(
        val_acc_key, 0.0
    )

    # Ratios: cell / baseline (lower = better than ruler)
    ruler_walltime_ratio = cell_cost.get("walltime_s", 1.0) / max(
        baseline_cost.get("walltime_s", 1.0), 1e-12
    )
    ruler_energy_ratio = cell_cost.get("energy_per_step", 1.0) / max(
        baseline_cost.get("energy_per_step", 1.0), 1e-12
    )
    ruler_param_ratio = cell_cost.get("param_count", 1.0) / max(
        baseline_cost.get("param_count", 1.0), 1e-12
    )

    return {
        "bp_deficit": bp_deficit,
        "ruler_walltime_ratio": ruler_walltime_ratio,
        "ruler_energy_ratio": ruler_energy_ratio,
        "ruler_param_ratio": ruler_param_ratio,
    }


__all__ = [
    "BaselineConfig",
    "BaselineGate",
    "BaselineRecord",
    "BaselineRegistry",
    "compute_ruler_metrics",
]
