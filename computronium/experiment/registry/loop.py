"""LoopDriver — the engine-driven closed experiment loop (TODO63 Phase 1-5).

One driver composes the pieces the engine already exposes:

- :class:`ExperimentRegistry` — store + provenance + deterministic seeds +
  transactional cycle commits (per cycle).
- :class:`PipelineRunner` — the run kernel, unchanged.
- ``create_policy`` / ``policy_context`` — proposal over the declared space.
- ``promote_with_stats`` — the L0→L1→L2 ladder with statistical gates.
- :class:`BaselineRegistry` — the same-hardware, same-budget ruler.
- ``compute_pareto_frontier`` — multi-objective, not one ``best_acc``.
- ``generate_run_report`` — the per-run report path.
- :class:`DefectRegistry` — turns failures into LegalityEngine constraints.
- :class:`HypothesisRegistry` — governed claims lifecycle (Phase 5).
- :class:`ICUModel` — guided search via I(C,U) metamodel (Phase 5).
- :class:`SurrogatePolicy` — model-based optimization wrapper (Phase 5).

Nothing here re-implements proposal, promotion, or reporting: ``cli._cmd_loop``
is a thin argparse wrapper that builds :class:`LoopConfig` and calls
:meth:`LoopDriver.run`.
"""

from __future__ import annotations

import logging
import signal
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
from scipy import stats

from computronium.experiment.design.hypothesis import (
    HypothesisRegistry,
    HypothesisResult,
    HypothesisSpec,
    HypothesisStatus,
    TestType,
    create_default_registry,
)
from computronium.experiment.evidence.model_registry import ModelRegistry
from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.execution.backends import ExecutionBackend, LocalBackend
from computronium.experiment.execution.deadline import Deadline
from computronium.experiment.execution.pipeline import PipelineConfig, PipelineRunner
from computronium.experiment.execution.policy import create_policy, policy_context
from computronium.experiment.execution.statistical_promotion import (
    GateThresholds,
    promote_with_stats,
)
from computronium.experiment.kernel.evaluate import task_shape
from computronium.experiment.learning.icu import ICUModel
from computronium.experiment.legality.engine import LegalityEngine
from computronium.experiment.optimization.multi_objective import (
    compute_pareto_frontier,
)
from computronium.experiment.registry import ExperimentConfig, ExperimentRegistry
from computronium.experiment.registry.baseline import (
    BaselineGate,
    BaselineRecord,
    BaselineRegistry,
)
from computronium.experiment.registry.defect_registry import (
    create_defect_registry,
)
from computronium.experiment.registry.seed import SeedContext
from computronium.experiment.registry.task_registry import get_task_registry
from computronium.experiment.schema.axis import AXES_REGISTRIES, Domain, StructuralAxis
from computronium.experiment.schema.metrics import measured_objectives, objective_metric
from computronium.experiment.schema.record import GateVerdict, Maturity, Record
from computronium.experiment.schema.registries import REPLAY_METRIC_TOLERANCE
from computronium.experiment.schema.run_spec import AxisSelection, Fidelity, RunSpec

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

logger = logging.getLogger(__name__)


# The cheap multi-domain walk: vision, tabular, RL, memory. Language and graph
# are expensive; the fast path proves the loop on cheap tasks before ``--hours``
# scales to them. Coverage across every domain remains a Phase F goal.
DEFAULT_TASK_SCHEDULE: tuple[str, ...] = (
    "xor",
    "iris",
    "spiral",
    "digits",
    "breast_cancer",
    "wine",
    "cartpole",
    "copy_task",
)


@dataclass(frozen=True, slots=True)
class LoopConfig:
    """Configuration for the closed loop."""

    store_path: Path
    state_dir: Path
    # From the run profile (single source of truth in the CLI's ``RUN_PROFILES``)
    stages: tuple[str, ...]
    param_budget: int
    policy: str
    hyperparameters: Mapping[str, Domain] = field(default_factory=dict)
    checkpoint_every_n: int = 0
    device: str = "auto"
    master_seed: int | None = None
    hours: float = 8.0
    cycles: int = 0
    n_seeds: int = 2
    explore_fidelity: Fidelity = "L0"
    exploit_fidelity: Fidelity = "L1"
    explore_hours: float = 0.5
    exploit_hours: float = 0.5
    explore_sweep_steps: int = 30
    exploit_sweep_steps: int = 15
    epochs_explore: int = 1
    epochs_exploit: int = 3
    cell_workers: int = 4
    task_schedule: tuple[str, ...] = DEFAULT_TASK_SCHEDULE
    # Phase 5: Hypothesis governance
    hypothesis_ids: tuple[str, ...] = field(default_factory=tuple)
    hypothesis_registry_path: Path | None = None
    # Phase 5: Guided search
    use_icu_guided: bool = False


@dataclass(frozen=True, slots=True)
class CycleResult:
    """The outcome of one cycle, for the ledger."""

    cycle: int
    task: str
    kind: str
    fidelity: Fidelity
    run_id: str
    n_records: int
    n_pass: int
    n_failures: int
    n_l1: int
    n_l2: int
    baseline_present: bool
    duration_s: float
    # Phase 5: Hypothesis evaluation results
    hypothesis_results: dict[str, str] = field(
        default_factory=dict
    )  # hypothesis_id -> status


def _objectives_for(task: str) -> tuple[str, ...]:
    """The task's declared, measured objective set read from the registry.

    A task that registers fewer than three measured objectives (iris, wine, …)
    is completed with the shared cost objectives, so every proposal carries a
    genuine multi-objective vector (TODO63 principle 4).
    """
    available = set(measured_objectives())
    task_spec = get_task_registry().get(task)
    names = [o.name for o in task_spec.measured_objectives() if o.name in available]
    for extra in ("param_count", "walltime_total", "validation_loss"):
        if len(names) >= 3:
            break
        if extra in available and extra not in names:
            names.append(extra)
    if not names:
        names = [task_spec.primary_objective]
    return tuple(names)


class LoopDriver:
    """The engine-driven closed loop.

    Choose work (explore/exploit) → run one ``PipelineRunner`` over the
    registry's store → settle maturity with statistical gates and a discovered
    baseline → record defects → update constraints → repeat. No hardcoded seeds,
    hints, or ``best_acc`` sorts.
    """

    def __init__(self, config: LoopConfig) -> None:
        self._config = config
        self._abort = False
        self._hardware_fp: str | None = None
        self._git_sha = self._resolve_git_sha()
        self._legality = LegalityEngine()
        self._defect_registry = create_defect_registry(self._legality, config.state_dir)
        self._baseline_gate = BaselineGate(BaselineRegistry())
        # Model registry for checkpoint tracking
        self._model_registry: ModelRegistry | None = None
        # Phase 5: Hypothesis registry for governed claims
        hypothesis_registry_path = config.hypothesis_registry_path or (
            config.state_dir / "hypotheses.json"
        )
        self._hypothesis_registry = HypothesisRegistry(hypothesis_registry_path)
        # Register any default hypotheses not already present
        default_registry = create_default_registry()
        for hyp_id, hyp in default_registry._hypotheses.items():
            if hyp_id not in self._hypothesis_registry._hypotheses:
                self._hypothesis_registry._hypotheses[hyp_id] = hyp
        # Phase 5: ICU model for guided search
        self._icu_model = ICUModel() if config.use_icu_guided else None

    # ------------------------------------------------------------------ public

    def run(self, *, dry_run: bool = False) -> int:
        """Run the loop until the cycle limit or time budget is exhausted.

        With ``dry_run=True`` the plan is computed through the same builders and
        printed, spending no cells.
        """
        cfg = self._config
        self._init_directories(cfg)

        checkpoint = self._load_checkpoint()
        cycle, master_seed = self._init_state(checkpoint)

        if dry_run:
            return self._dry_run(cycle, master_seed)

        start_cycle = cycle
        deadline_time = time.time() + cfg.hours * 3600
        history: list[CycleResult] = []

        self._setup_signals()
        self._print_loop_header(cfg, master_seed, cycle)

        while not self._abort:
            if self._should_stop(cfg, cycle, start_cycle, deadline_time):
                break

            result = self._execute_cycle(cycle, master_seed)
            cycle = self._process_cycle_result(
                cycle, master_seed, result, history, checkpoint
            )

        self._write_loop_report(history)
        self._print_loop_footer(cfg, cycle)
        return 0

    def _init_directories(self, cfg: LoopConfig) -> None:
        cfg.state_dir.mkdir(parents=True, exist_ok=True)
        cfg.store_path.parent.mkdir(parents=True, exist_ok=True)

    def _init_state(self, checkpoint: dict[str, Any]) -> tuple[int, int]:
        saved_cycle = checkpoint.get("cycle")
        cycle = saved_cycle if isinstance(saved_cycle, int) else 0
        master_seed = self._resolve_master_seed(checkpoint)
        return cycle, master_seed

    def _setup_signals(self) -> None:
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def _print_loop_header(self, cfg: LoopConfig, master_seed: int, cycle: int) -> None:
        print("=" * 70, flush=True)
        print("COMPUTRONIUM EXPERIMENT LOOP (engine-driven)", flush=True)
        print(f"  Store:   {cfg.store_path}", flush=True)
        print(f"  State:   {cfg.state_dir}", flush=True)
        print(f"  Seed:    {master_seed}", flush=True)
        print(f"  Tasks:   {', '.join(cfg.task_schedule)}", flush=True)
        print(f"  Resume:  cycle {cycle}", flush=True)
        print("=" * 70, flush=True)

    def _should_stop(
        self, cfg: LoopConfig, cycle: int, start_cycle: int, deadline_time: float
    ) -> bool:
        if cfg.cycles and (cycle - start_cycle) >= cfg.cycles:
            print("Cycle limit reached.", flush=True)
            return True
        if time.time() >= deadline_time:
            print("Budget exhausted.", flush=True)
            return True
        return False

    def _execute_cycle(self, cycle: int, master_seed: int) -> CycleResult:
        checkpoint = self._load_checkpoint_typed()
        cycle_status = checkpoint.get("cycle_status", {})
        if cycle_status.get(str(cycle)) == "in_progress":
            print(f"  Resuming interrupted cycle {cycle}...", flush=True)
            return self._resume_cycle(cycle, master_seed, checkpoint)
        return self._run_cycle(cycle, master_seed, checkpoint)

    def _process_cycle_result(
        self,
        cycle: int,
        master_seed: int,
        result: CycleResult,
        history: list[CycleResult],
        checkpoint: dict[str, Any],
    ) -> int:
        history.append(result)
        cycle_run_ids: dict[str, str] = checkpoint.get("cycle_run_ids", {})
        cycle_run_ids[str(cycle)] = result.run_id
        checkpoint["cycle_run_ids"] = cycle_run_ids
        cycle_status = checkpoint.get("cycle_status", {})
        cycle_status[str(cycle)] = "complete"
        checkpoint["cycle_status"] = cycle_status
        cycle += 1
        checkpoint.update({"cycle": cycle, "master_seed": master_seed})
        self._save_checkpoint(checkpoint)
        self._write_loop_report(history)
        self._print_cycle_summary(result)
        return cycle

    def _print_cycle_summary(self, result: CycleResult) -> None:
        print(
            f"  → task={result.task} kind={result.kind} "
            f"records={result.n_records} pass={result.n_pass} "
            f"L1={result.n_l1} L2={result.n_l2} "
            f"baseline={'yes' if result.baseline_present else 'no'} "
            f"({result.duration_s:.1f}s)",
            flush=True,
        )

    def _print_loop_footer(self, cfg: LoopConfig, cycle: int) -> None:
        print("\n" + "=" * 70, flush=True)
        print(f"LOOP STOPPED at cycle {cycle}", flush=True)
        print(f"Report: {cfg.state_dir / 'report.md'}", flush=True)
        print("=" * 70, flush=True)

    def plan(
        self, cycles: int, start: int = 0, seed: int | None = None
    ) -> list[RunSpec]:
        """The specs the next ``cycles`` cycles would run (dry-run evidence)."""
        master_seed = seed if seed is not None else self._resolve_master_seed({})
        specs: list[RunSpec] = []
        for offset in range(cycles):
            cycle = start + offset
            task = self._config.task_schedule[cycle % len(self._config.task_schedule)]
            kind = "explore" if cycle % 2 == 0 else "exploit"
            axes = self._axes_for(kind, task, self._probe_store())
            specs.append(self._build_spec(task, kind, cycle, axes, master_seed))
        return specs

    def _dry_run(self, start: int, seed: int) -> int:
        n = self._config.cycles or 2
        print("DRY RUN: no cells spent\n")
        for cycle, spec in enumerate(self.plan(n, start, seed), start=start):
            kind = spec.profile.removeprefix("loop-")
            axes = ", ".join(
                f"{a.axis.value}={list(a.primitives or ())}" for a in spec.axes
            )
            print(
                f"[cycle {cycle}] {kind} task={spec.task} fidelity={spec.fidelity} "
                f"n_seeds={spec.n_seeds} epochs={spec.epochs}\n"
                f"    objectives: {list(spec.objectives)}\n"
                f"    axes: {axes}"
            )
        return 0

    # ----------------------------------------------------------------- cycles

    def _run_cycle(
        self, cycle: int, master_seed: int, checkpoint: dict[str, Any]
    ) -> CycleResult:
        cfg = self._config
        task = cfg.task_schedule[cycle % len(cfg.task_schedule)]
        kind = "explore" if cycle % 2 == 0 else "exploit"
        started = time.time()

        axes = self._axes_for(kind, task, self._probe_store())
        spec = self._build_spec(task, kind, cycle, axes, master_seed)
        print(
            f"\n[cycle {cycle}] {kind} task={task} "
            f"fidelity={spec.fidelity} objectives={list(spec.objectives)}",
            flush=True,
        )

        # Mark cycle as in_progress before starting
        cycle_status: dict[str, str] = checkpoint.get("cycle_status", {})
        cycle_status[str(cycle)] = "in_progress"
        checkpoint["cycle_status"] = cycle_status
        self._save_checkpoint(checkpoint)

        import asyncio

        try:
            result = asyncio.run(self._execute(cycle, spec, task, checkpoint))
            print(
                f"DEBUG: _execute returned n_records={result.n_records}, run_id={result.run_id}",
                flush=True,
            )
        except KeyboardInterrupt:
            raise
        except Exception as exc:  # ruff: ignore[blind-except] - one bad cycle must not kill the loop
            logger.error("Cycle %d (%s) failed: %s", cycle, task, exc, exc_info=True)
            print(f"DEBUG: Exception caught in _run_cycle: {exc}", flush=True)
            result = CycleResult(
                cycle=cycle,
                task=task,
                kind=kind,
                fidelity=spec.fidelity,
                run_id="",
                n_records=0,
                n_pass=0,
                n_failures=1,
                n_l1=0,
                n_l2=0,
                baseline_present=False,
                duration_s=0.0,
            )

        # Phase 5: Evaluate hypotheses after cycle completes
        hypothesis_results = {}
        if result.run_id:
            hypothesis_results = self._evaluate_hypotheses(result.run_id, task)

        return CycleResult(
            cycle=cycle,
            task=task,
            kind=kind,
            fidelity=spec.fidelity,
            run_id=result.run_id,
            n_records=result.n_records,
            n_pass=result.n_pass,
            n_failures=result.n_failures,
            n_l1=result.n_l1,
            n_l2=result.n_l2,
            baseline_present=result.baseline_present,
            duration_s=time.time() - started,
            hypothesis_results=hypothesis_results,
        )

    def _resume_cycle(
        self, cycle: int, master_seed: int, checkpoint: dict[str, Any]
    ) -> CycleResult:
        """Resume an interrupted cycle from its checkpoint."""
        cfg = self._config
        task = cfg.task_schedule[cycle % len(cfg.task_schedule)]
        kind = "explore" if cycle % 2 == 0 else "exploit"
        started = time.time()

        axes = self._axes_for(kind, task, self._probe_store())
        spec = self._build_spec(task, kind, cycle, axes, master_seed)

        # Get the run_id from the checkpoint
        cycle_run_ids: dict[str, str] = checkpoint.get("cycle_run_ids", {})
        run_id = cycle_run_ids.get(str(cycle))
        if not run_id:
            logger.warning("No run_id found for cycle %d, starting fresh", cycle)
            return self._run_cycle(cycle, master_seed, checkpoint)

        print(
            f"\n[cycle {cycle}] {kind} task={task} "
            f"fidelity={spec.fidelity} objectives={list(spec.objectives)} (RESUMING run_id={run_id[:8]})",
            flush=True,
        )

        import asyncio

        try:
            result = asyncio.run(self._execute_resume(cycle, spec, task, run_id))
            print(
                f"DEBUG: _execute_resume returned n_records={result.n_records}, run_id={result.run_id}",
                flush=True,
            )
        except KeyboardInterrupt:
            raise
        except Exception as exc:  # ruff: ignore[blind-except] - one bad cycle must not kill the loop
            logger.error(
                "Cycle %d (%s) resume failed: %s", cycle, task, exc, exc_info=True
            )
            print(f"DEBUG: Exception caught in _resume_cycle: {exc}", flush=True)
            result = CycleResult(
                cycle=cycle,
                task=task,
                kind=kind,
                fidelity=spec.fidelity,
                run_id=run_id,
                n_records=0,
                n_pass=0,
                n_failures=1,
                n_l1=0,
                n_l2=0,
                baseline_present=False,
                duration_s=0.0,
            )

        # Phase 5: Evaluate hypotheses after cycle completes
        hypothesis_results = {}
        if result.run_id:
            hypothesis_results = self._evaluate_hypotheses(result.run_id, task)

        return CycleResult(
            cycle=cycle,
            task=task,
            kind=kind,
            fidelity=spec.fidelity,
            run_id=result.run_id,
            n_records=result.n_records,
            n_pass=result.n_pass,
            n_failures=result.n_failures,
            n_l1=result.n_l1,
            n_l2=result.n_l2,
            baseline_present=result.baseline_present,
            duration_s=time.time() - started,
            hypothesis_results=hypothesis_results,
        )

    async def _execute_resume(
        self, cycle: int, spec: RunSpec, task: str, run_id: str
    ) -> CycleResult:
        """Execute a resumed cycle using the existing run_id."""
        cfg = self._config
        started = time.time()
        with ExperimentRegistry(
            ExperimentConfig(
                store_path=cfg.store_path,
                spec=spec,
                master_seed=cfg.master_seed,
                run_id=run_id,
            )
        ) as registry:
            store = registry.store
            registry.start_cycle(cycle)

            deadline = (
                Deadline.from_seconds(spec.budget_seconds)
                if spec.budget_seconds
                else None
            )
            policy_name = spec.policy or "round_robin_grid"

            # Phase 5: Ingest measurements into ICU model for guided search
            if self._icu_model is not None:
                self._icu_model.ingest_measurements(store, run_id)

            policy = create_policy(
                policy_name,
                **policy_context(
                    spec,
                    policy_name,
                    shape=task_shape,
                    deadline=deadline,
                    legality_engine=self._legality,
                    icu_model=self._icu_model,
                ),
            )

            max_rounds = None
            if spec.stages and "s10_decide" not in spec.stages:
                max_rounds = 1

            # Resume PipelineRunner from checkpoint
            runner = PipelineRunner.from_checkpoint(
                run_id=run_id,
                config=PipelineConfig(
                    run_id=run_id,
                    run_spec=spec,
                    deadline=deadline,
                    cost_model=None,
                    policy=policy,
                    backend=self._backend(),
                    seed=spec.seed,
                    max_rounds=max_rounds,
                ),
                store=store,
            )

            outcomes = await runner.run()
            for outcome in outcomes:
                registry.complete_cell(outcome.measurement_key)

            baselines = await self._baselines(store, run_id, spec, task)
            self._settle(store, run_id, spec, baselines)

            from computronium.experiment.surface.report import generate_run_report

            self._write_cycle_report(cycle, generate_run_report(store, run_id))

            records = store.query_records(run_id=run_id)

            # Initialize model registry and register checkpoints for PASS records
            if self._model_registry is None and store._conn is not None:
                self._model_registry = ModelRegistry(
                    store._conn, store._write_lock, store.artifacts
                )
            if self._model_registry is not None:
                self._register_model_checkpoints(records, store)

            budget = self._elapsed(deadline)
            registry.commit_cycle(budget)

            # Record defects from failed/quarantined records into the LegalityEngine
            self._record_cycle_defects(records)

        return CycleResult(
            cycle=cycle,
            task=task,
            kind=spec.profile.removeprefix("loop-"),
            fidelity=spec.fidelity,
            run_id=run_id,
            n_records=len(records),
            n_pass=sum(
                1
                for r in records
                if r.status.gate_verdict is GateVerdict.PASS_
                and not r.status.quarantine
            ),
            n_failures=sum(
                1 for r in records if r.status.gate_verdict is not GateVerdict.PASS_
            ),
            n_l1=sum(1 for r in records if r.status.maturity is Maturity.L1),
            n_l2=sum(1 for r in records if r.status.maturity is Maturity.L2),
            baseline_present=bool(baselines),
            duration_s=time.time() - started,
        )

    async def _execute(
        self, cycle: int, spec: RunSpec, task: str, checkpoint: dict[str, Any]
    ) -> CycleResult:
        cfg = self._config
        started = time.time()
        with ExperimentRegistry(
            ExperimentConfig(
                store_path=cfg.store_path,
                spec=spec,
                master_seed=cfg.master_seed,
            )
        ) as registry:
            store = registry.store
            run_id = registry.run_id
            # Save run_id to checkpoint immediately for resume capability
            cycle_run_ids: dict[str, str] = checkpoint.get("cycle_run_ids", {})
            cycle_run_ids[str(cycle)] = run_id
            checkpoint["cycle_run_ids"] = cycle_run_ids
            self._save_checkpoint(checkpoint)

            registry.start_cycle(cycle)

            deadline = (
                Deadline.from_seconds(spec.budget_seconds)
                if spec.budget_seconds
                else None
            )
            policy_name = spec.policy or "round_robin_grid"

            # Phase 5: Ingest measurements into ICU model for guided search
            if self._icu_model is not None:
                self._icu_model.ingest_measurements(store, run_id)

            policy = create_policy(
                policy_name,
                **policy_context(
                    spec,
                    policy_name,
                    shape=task_shape,
                    deadline=deadline,
                    legality_engine=self._legality,
                    icu_model=self._icu_model,
                ),
            )

            max_rounds = None
            if spec.stages and "s10_decide" not in spec.stages:
                max_rounds = 1

            runner = PipelineRunner(
                PipelineConfig(
                    run_id=run_id,
                    run_spec=spec,
                    deadline=deadline,
                    cost_model=None,
                    policy=policy,
                    backend=self._backend(),
                    seed=spec.seed,
                    max_rounds=max_rounds,
                ),
                store,
            )

            outcomes = await runner.run()
            for outcome in outcomes:
                registry.complete_cell(outcome.measurement_key)

            baselines = await self._baselines(store, run_id, spec, task)
            self._settle(store, run_id, spec, baselines)

            from computronium.experiment.surface.report import generate_run_report

            self._write_cycle_report(cycle, generate_run_report(store, run_id))

            records = store.query_records(run_id=run_id)

            # Initialize model registry and register checkpoints for PASS records
            if self._model_registry is None and store._conn is not None:
                self._model_registry = ModelRegistry(
                    store._conn, store._write_lock, store.artifacts
                )
            if self._model_registry is not None:
                self._register_model_checkpoints(records, store)

            budget = self._elapsed(deadline)
            registry.commit_cycle(budget)

            # Record defects from failed/quarantined records into the LegalityEngine
            self._record_cycle_defects(records)

        return CycleResult(
            cycle=cycle,
            task=task,
            kind=spec.profile.removeprefix("loop-"),
            fidelity=spec.fidelity,
            run_id=run_id,
            n_records=len(records),
            n_pass=sum(
                1
                for r in records
                if r.status.gate_verdict is GateVerdict.PASS_
                and not r.status.quarantine
            ),
            n_failures=sum(
                1 for r in records if r.status.gate_verdict is not GateVerdict.PASS_
            ),
            n_l1=sum(1 for r in records if r.status.maturity is Maturity.L1),
            n_l2=sum(1 for r in records if r.status.maturity is Maturity.L2),
            baseline_present=bool(baselines),
            duration_s=time.time() - started,
        )

    def _register_model_checkpoints(self, records: list, store: RecordStore) -> None:
        """Register model checkpoints for PASS records."""
        if self._model_registry is None:
            return
        for record in records:
            if (
                record.status.gate_verdict is GateVerdict.PASS_
                and not record.status.quarantine
            ):
                # Check if record has a checkpoint artifact
                artifacts = store.artifacts.get_for_record(record.record_id)
                has_checkpoint = any(
                    a.role.value == "model_checkpoint" for a in artifacts
                )
                if has_checkpoint:
                    try:
                        model_id = f"{record.task}_{record.dynamics}_{record.credit}_{record.update}"
                        version = f"v{record.seq}"
                        self._model_registry.register_from_record(
                            record,
                            model_id=model_id,
                            version=version,
                            stage="development",
                            description=f"Cycle {record.cycle if hasattr(record, 'cycle') else 'unknown'} PASS",
                        )
                    except Exception as exc:  # ruff: ignore[blind-except] - best effort
                        logger.warning(
                            "Failed to register model checkpoint for %s: %s",
                            record.record_id,
                            exc,
                        )

    def _record_cycle_defects(self, records: list) -> None:
        """Process failed/quarantined records into LegalityEngine constraints."""
        defect_count = 0
        for record in records:
            if (
                record.status.gate_verdict is not GateVerdict.PASS_
                or record.status.quarantine
            ):
                new_constraints = self._defect_registry.record_defect(record)
                defect_count += len(new_constraints)
        if defect_count:
            logger.info(
                "Cycle recorded %d new defect constraints (engine now has %d active)",
                defect_count,
                len(self._defect_registry.engine.all_constraints()),
            )

    def _evaluate_hypotheses(self, run_id: str, task: str) -> dict[str, str]:
        """Evaluate registered hypotheses against accumulated records.

        For cross-domain hypotheses (domain=None), evaluates across all tasks
        and all cycles. For domain-specific hypotheses, filters to relevant tasks.
        """
        results: dict[str, str] = {}
        if not self._config.hypothesis_ids:
            return results

        store = RecordStore(StoreConfig(path=self._config.store_path, read_only=True))
        with store:
            all_records = store.query_records()
        if not all_records:
            return results

        for hyp_id in self._config.hypothesis_ids:
            self._evaluate_single_hypothesis(hyp_id, all_records, results)

        return results

    def _evaluate_single_hypothesis(
        self, hyp_id: str, all_records: list[Record], results: dict[str, str]
    ) -> None:
        hyp = self._hypothesis_registry.get(hyp_id)
        if hyp is None:
            logger.warning("Hypothesis %s not found in registry", hyp_id)
            return

        hyp_records = self._filter_records_for_hypothesis(hyp, all_records)
        if not hyp_records:
            logger.info("No records for hypothesis %s", hyp_id)
            return

        try:
            result = self._test_hypothesis(hyp, hyp_records)
            self._hypothesis_registry.record_result(hyp_id, result)
            status = (
                hyp.status.value if hyp.status else HypothesisStatus.INCONCLUSIVE.value
            )
            results[hyp_id] = status
            logger.info(
                "Hypothesis %s evaluated: %s (p=%.4f, effect=%.3f, power=%.2f)",
                hyp_id,
                status,
                result.p_value or -1,
                result.effect_size or -1,
                result.power_achieved or -1,
            )
        except Exception:  # ruff: ignore[blind-except] - continue evaluating other hypotheses
            logger.exception("Failed to evaluate hypothesis %s", hyp_id)

    def _filter_records_for_hypothesis(
        self, hyp: HypothesisSpec, all_records: list[Record]
    ) -> list[Record]:
        if hyp.domain is None:
            return all_records
        task_registry = get_task_registry()
        domain_tasks = {
            t
            for t in self._config.task_schedule
            if task_registry.get(t).domain == hyp.domain
        }
        return [r for r in all_records if r.schedule.task_id in domain_tasks]

    def _calculate_power_achieved(
        self,
        p_value: float | None,
        effect_size: float | None,
        n_a: int,
        n_b: int,
        alpha: float,
    ) -> float | None:
        if p_value is None or effect_size is None:
            return None
        try:
            from scipy import stats
            from scipy.stats import nct

            return self._compute_power(n_a, n_b, alpha, effect_size, stats, nct)
        except Exception:
            return None

    def _compute_power(
        self,
        n_a: int,
        n_b: int,
        alpha: float,
        effect_size: float,
        stats: Any,
        nct: Any,
    ) -> float | None:
        df = n_a + n_b - 2
        if df <= 0:
            return None
        ncp = effect_size * np.sqrt(n_a * n_b / (n_a + n_b))
        t_crit = stats.t.ppf(1 - alpha / 2, df)
        return float(nct.sf(t_crit, df, ncp) + nct.cdf(-t_crit, df, ncp))

    def _test_hypothesis(  # ruff: ignore[complex-structure, too-many-return-statements, too-many-branches, too-many-locals, too-many-statements]
        self, hyp: HypothesisSpec, records: list[Record]
    ) -> HypothesisResult:
        """Run a statistical test for a hypothesis on the given records.

        This is a simplified implementation that tests the primary metric
        grouped by the grouping_factor (e.g., credit assignment).
        The records passed are already filtered for the hypothesis's domain.
        """

        if not records:
            return HypothesisResult(
                hypothesis_id=hyp.id,
                test_type=hyp.test_type,
                effect_size_type=hyp.effect_size_type,
                n_samples=0,
                n_groups=0,
                notes="No records for hypothesis",
            )

        # Extract values for the primary metric grouped by the grouping factor
        # Resolve objective name to payload key via MEASURED_OBJECTIVES
        metric_key = objective_metric(hyp.primary_metric)
        if metric_key is None:
            return HypothesisResult(
                hypothesis_id=hyp.id,
                test_type=hyp.test_type,
                effect_size_type=hyp.effect_size_type,
                n_samples=0,
                n_groups=0,
                notes=f"Primary metric {hyp.primary_metric} not measured",
            )

        groups: dict[str, list[float]] = {}
        for r in records:
            # Skip non-PASS records
            if r.status.gate_verdict is not GateVerdict.PASS_ or r.status.quarantine:
                continue
            val = r.payload.get(metric_key)
            if val is None:
                continue
            group_key = (
                getattr(r, hyp.grouping_factor, "all") if hyp.grouping_factor else "all"
            )
            groups.setdefault(group_key, []).append(float(val))

        if len(groups) < 2:
            return HypothesisResult(
                hypothesis_id=hyp.id,
                test_type=hyp.test_type,
                effect_size_type=hyp.effect_size_type,
                n_samples=sum(len(v) for v in groups.values()),
                n_groups=len(groups),
                notes="Insufficient groups for comparison",
            )

        # Run the specified test
        comparison_values = hyp.comparison_values or sorted(groups.keys())
        if len(comparison_values) < 2:
            return HypothesisResult(
                hypothesis_id=hyp.id,
                test_type=hyp.test_type,
                effect_size_type=hyp.effect_size_type,
                n_samples=sum(len(v) for v in groups.values()),
                n_groups=len(groups),
                notes="Not enough comparison values",
            )

        # Get the two groups to compare
        group_a = groups.get(comparison_values[0], [])
        group_b = groups.get(comparison_values[1], [])

        if not group_a or not group_b:
            return HypothesisResult(
                hypothesis_id=hyp.id,
                test_type=hyp.test_type,
                effect_size_type=hyp.effect_size_type,
                n_samples=sum(len(v) for v in groups.values()),
                n_groups=len(groups),
                notes="One or both comparison groups empty",
            )

        test_statistic: float | None = None
        p_value: float | None = None
        effect_size: float | None = None
        confidence_interval: tuple[float, float] | None = None

        if hyp.test_type == TestType.PAIRED_T_TEST:
            # For paired, we need matched samples - fallback to independent
            if len(group_a) == len(group_b) and hyp.paired:
                stat, p_value = stats.ttest_rel(group_a, group_b)  # type: ignore[misc]
                test_statistic = float(stat)  # type: ignore[arg-type]
            else:
                stat, p_value = stats.ttest_ind(group_a, group_b, equal_var=False)  # type: ignore[misc]
                test_statistic = float(stat)  # type: ignore[arg-type]
            # Cohen's d
            pooled_std = np.sqrt((np.var(group_a) + np.var(group_b)) / 2)
            if pooled_std > 0:
                effect_size = (np.mean(group_a) - np.mean(group_b)) / pooled_std

        elif hyp.test_type == TestType.INDEPENDENT_T_TEST:
            stat, p_value = stats.ttest_ind(group_a, group_b, equal_var=False)  # type: ignore[misc]
            test_statistic = float(stat)  # type: ignore[arg-type]
            pooled_std = np.sqrt((np.var(group_a) + np.var(group_b)) / 2)
            if pooled_std > 0:
                effect_size = (np.mean(group_a) - np.mean(group_b)) / pooled_std

        elif hyp.test_type == TestType.MANN_WHITNEY_U:
            stat, p_value = stats.mannwhitneyu(  # type: ignore[misc]
                group_a, group_b, alternative=hyp.alternative
            )
            test_statistic = float(stat)  # type: ignore[arg-type]
            # Cliff's delta
            n_a, n_b = len(group_a), len(group_b)
            pairs = [(a, b) for a in group_a for b in group_b]
            greater = sum(1 for a, b in pairs if a > b)
            less = sum(1 for a, b in pairs if a < b)
            effect_size = (greater - less) / (n_a * n_b) if n_a * n_b > 0 else 0

        elif hyp.test_type == TestType.WILCOXON:
            if len(group_a) == len(group_b):
                stat, p_value = stats.wilcoxon(  # type: ignore[misc]
                    group_a, group_b, alternative=hyp.alternative
                )
                test_statistic = float(stat)  # type: ignore[arg-type]
            else:
                p_value = 1.0

        elif hyp.test_type == TestType.ANOVA_ONE_WAY:
            if len(groups) >= 2:
                group_values = [groups[k] for k in comparison_values if k in groups]
                if all(len(g) > 0 for g in group_values):
                    stat, p_value = stats.f_oneway(*group_values)  # type: ignore[misc]
                    test_statistic = float(stat)
                    # Eta-squared as effect size
                    all_vals = np.concatenate(group_values)
                    grand_mean = np.mean(all_vals)
                    ss_between = sum(
                        len(g) * (np.mean(g) - grand_mean) ** 2 for g in group_values
                    )
                    ss_total = sum(
                        (v - grand_mean) ** 2 for g in group_values for v in g
                    )
                    if ss_total > 0:
                        effect_size = ss_between / ss_total

        # Confidence interval for mean difference (approximate)
        if effect_size is not None and p_value is not None:
            mean_diff = np.mean(group_a) - np.mean(group_b)
            se = np.sqrt(
                np.var(group_a) / len(group_a) + np.var(group_b) / len(group_b)
            )
            ci_half = 1.96 * se
            confidence_interval = (mean_diff - ci_half, mean_diff + ci_half)

        # Calculate achieved power
        power_achieved = self._calculate_power_achieved(
            p_value, effect_size, len(group_a), len(group_b), hyp.alpha
        )

        return HypothesisResult(
            hypothesis_id=hyp.id,
            test_type=hyp.test_type,
            test_statistic=test_statistic,
            p_value=float(p_value) if p_value is not None else None,
            effect_size=effect_size,
            effect_size_type=hyp.effect_size_type,
            confidence_interval=confidence_interval,
            significant=(p_value is not None and p_value < hyp.alpha),
            power_achieved=power_achieved,
            n_samples=len(group_a) + len(group_b),
            n_groups=2,
            groups_tested=[comparison_values[0], comparison_values[1]],
            notes="",
        )

    # --------------------------------------------------------------- strategy

    def _probe_store(self) -> RecordStore | None:
        """A read-only store handle for strategy, or ``None`` before cycle one."""
        if not self._config.store_path.exists():
            return None
        return RecordStore(StoreConfig(path=self._config.store_path, read_only=True))

    def _axes_for(
        self,
        kind: str,
        task: str,
        store: RecordStore | None,
    ) -> tuple[AxisSelection, ...]:
        if kind == "explore" or store is None:
            return self._explore_axes()
        with store:
            return self._exploit_axes(store, task)

    def _explore_axes(self) -> tuple[AxisSelection, ...]:
        selections = []
        for axis in StructuralAxis:
            primitives = sorted(
                name for name, spec in AXES_REGISTRIES[axis].items() if spec.available
            )
            if primitives:
                selections.append(
                    AxisSelection(axis=axis, primitives=tuple(primitives))
                )
        return tuple(selections)

    def _exploit_axes(
        self,
        store: RecordStore,
        task: str,
    ) -> tuple[AxisSelection, ...]:
        records = [
            r
            for r in store.query_records()
            if r.schedule.task_id == task
            and r.status.gate_verdict is GateVerdict.PASS_
            and not r.status.quarantine
        ]
        if not records:
            return self._explore_axes()

        objective_names = list(_objectives_for(task))

        # Get baselines for ruler-relative normalization (F0b)
        baselines = None
        if self._baseline_gate and self._config.store_path:
            from computronium.experiment.evidence.store import RecordStore, StoreConfig

            store = RecordStore(
                StoreConfig(path=self._config.store_path, read_only=True)
            )
            with store:
                baselines = self._get_baselines_for_pareto(store, task)

        frontier = compute_pareto_frontier(
            records, objective_names, baselines=baselines
        )
        front_points = frontier.front()
        if not front_points:
            return self._explore_axes()

        # Select diverse top-k from frontier using crowding distance
        # This prevents "exploit" from being the full space when all cells are non-dominated
        k = min(5, len(front_points))
        selected_points = frontier.select_diverse(k)

        # Map cell_key back to records
        front_keys = {p.cell_key for p in selected_points}
        selected_records = [r for r in records if r.cell_key in front_keys]

        union: dict[StructuralAxis, set[str]] = {axis: set() for axis in StructuralAxis}
        for record in selected_records:
            for axis, value in (
                (StructuralAxis.SUBSTRATE, record.substrate),
                (StructuralAxis.GEOMETRY, record.geometry),
                (StructuralAxis.DYNAMICS, record.dynamics),
                (StructuralAxis.PLASTICITY, record.plasticity),
                (StructuralAxis.CREDIT, record.credit),
                (StructuralAxis.UPDATE, record.update),
            ):
                if value:
                    union[axis].add(value)
        selections = [
            AxisSelection(axis=axis, primitives=tuple(sorted(values)))
            for axis, values in union.items()
            if values
        ]
        return tuple(selections) or self._explore_axes()

    # ------------------------------------------------------------------ spec

    def _build_spec(
        self,
        task: str,
        kind: str,
        cycle: int,
        axes: tuple[AxisSelection, ...],
        master_seed: int,
    ) -> RunSpec:
        cfg = self._config
        explore = kind == "explore"
        cycle_seed = SeedContext(master_seed).cycle_seed(cycle)
        return RunSpec(
            profile=f"loop-{kind}",
            task=task,
            objectives=_objectives_for(task),
            stages=tuple(cfg.stages),
            fidelity=cfg.explore_fidelity if explore else cfg.exploit_fidelity,
            n_seeds=cfg.n_seeds,
            epochs=cfg.epochs_explore if explore else cfg.epochs_exploit,
            batch_limit=0,
            budget_seconds=(cfg.explore_hours if explore else cfg.exploit_hours)
            * 3600.0,
            param_budget=cfg.param_budget,
            policy=cfg.policy,
            axes=axes,
            hyperparameters=dict(cfg.hyperparameters),
            checkpoint_every_n=cfg.checkpoint_every_n,
            seed=cycle_seed,
            device=self._device(),
            sweep_steps=cfg.explore_sweep_steps if explore else cfg.exploit_sweep_steps,
            code_sha=self._git_sha,
            dataset=task,
            dataset_version="1.0",
        )

    # -------------------------------------------------------------- promotion

    def _settle(
        self,
        store: RecordStore,
        run_id: str,
        spec: RunSpec,
        baselines: dict[str, BaselineRecord] | None,
    ) -> list[dict[str, object]]:
        min_seeds = max(spec.n_seeds, 5) if spec.n_seeds >= 3 else spec.n_seeds
        thresholds = GateThresholds(
            min_seeds_for_stats=min_seeds,
            superiority_margin_sigma=1.0 if spec.n_seeds < 5 else 2.0,
            ci_width_threshold=0.1 if spec.n_seeds < 5 else 0.05,
        )
        history = promote_with_stats(
            store,
            run_id,
            spec,
            tolerance=REPLAY_METRIC_TOLERANCE,
            thresholds=thresholds,
            baselines=baselines,
        )
        logger.info(
            "Promotion: %d cell(s) assessed, %d earned L2",
            len(history),
            sum(1 for entry in history if entry["maturity"] == Maturity.L2.value),
        )
        return history

    async def _baselines(
        self,
        store: RecordStore,
        run_id: str,
        spec: RunSpec,
        task: str,
    ) -> dict[str, BaselineRecord] | None:
        """The same-task backprop ruler for this cycle's cells, if measurable.

        The loop's own axis sweep measures ``gradient × instantaneous`` cells;
        those *are* the backprop baseline for that task/budget, so the ruler is
        read from the store rather than re-run (TODO63 Phase 2). If absent, run
        discovery via ``BaselineGate.check_or_run``.
        """
        from computronium.experiment.execution.promotion import eligible_cells
        from computronium.experiment.registry.seed import SeedContext

        if spec.budget_seconds is None:
            return None
        registry = BaselineRegistry(store=store)
        baseline = registry.get_baseline(
            task, self._fingerprint(registry), spec.budget_seconds, spec.n_seeds
        )
        if baseline is None:
            logger.info(
                "No backprop baseline in store for task %s; running discovery",
                task,
            )
            # Use the cycle's seed context for deterministic discovery
            seed_ctx = SeedContext(spec.seed)
            baseline, reason = await self._baseline_gate.check_or_run(
                task, spec.budget_seconds, spec.n_seeds, seed_ctx
            )
            if baseline is None:
                logger.warning("Baseline discovery failed for %s: %s", task, reason)
                return None
            # Cache the discovered baseline in the registry for subsequent cycles
            registry._cache[baseline.key()] = baseline
        keys = eligible_cells(store.query_records(run_id=run_id), spec.n_seeds).keys()
        return dict.fromkeys(keys, baseline)

    def _fingerprint(self, registry: BaselineRegistry) -> str:
        if self._hardware_fp is None:
            try:
                self._hardware_fp = registry.compute_hardware_fingerprint()
            except Exception as exc:  # ruff: ignore[blind-except] - fingerprint is best-effort
                logger.warning("Hardware fingerprint unavailable: %s", exc)
                self._hardware_fp = "unknown"
        return self._hardware_fp

    def _get_baselines_for_pareto(
        self,
        store: RecordStore,
        task: str,
    ) -> dict[str, dict[str, float]] | None:
        """Get baseline metrics for ruler-relative Pareto normalization (F0b).

        Returns dict mapping task_name -> {objective: baseline_value} for tasks
        that have discovered baselines.
        """
        from computronium.experiment.registry.baseline import BaselineRegistry

        registry = BaselineRegistry(store=store)
        hardware_fp = self._fingerprint(registry)

        # Get baselines for all tasks in the task schedule
        baselines = {}
        for t in self._config.task_schedule:
            baseline = registry.get_baseline(
                t, hardware_fp, self._config.hours * 3600, self._config.n_seeds
            )
            if baseline:
                baselines[t] = baseline.metrics | baseline.cost_metrics

        return baselines if baselines else None

    # --------------------------------------------------------------- support

    def _backend(self) -> ExecutionBackend:
        return LocalBackend(max_workers=self._config.cell_workers)

    def _device(self) -> str:
        cfg = self._config
        if cfg.device != "auto":
            return cfg.device
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"

    def _resolve_git_sha(self) -> str:
        import subprocess  # ruff: ignore[suspicious-subprocess-import] - resolved git sha

        try:
            return subprocess.run(
                ["git", "rev-parse", "HEAD"],  # ruff: ignore[start-process-with-partial-path]
                capture_output=True,
                text=True,
                check=True,
                timeout=5,
            ).stdout.strip()
        except Exception:  # ruff: ignore[blind-except] - provenance degrades to "unknown"
            return "unknown"

    def _resolve_master_seed(self, checkpoint: dict[str, object]) -> int:
        saved = checkpoint.get("master_seed")
        if isinstance(saved, int):
            return saved
        if self._config.master_seed is not None:
            return self._config.master_seed
        import random

        return random.SystemRandom().randint(0, 2**31 - 1)

    @staticmethod
    def _elapsed(deadline: Deadline | None) -> float:
        return deadline.elapsed_seconds() if deadline is not None else 0.0

    def _handle_signal(self, _signum: int, _frame: object) -> None:
        self._abort = True

    # ------------------------------------------------------------- artifacts

    def _load_checkpoint(self) -> dict[str, object]:
        import json

        path = self._config.state_dir / "checkpoint.json"
        if path.exists():
            data = json.loads(path.read_text())
            if isinstance(data, dict):
                return data
        return {"cycle_run_ids": {}, "cycle_status": {}}

    def _load_checkpoint_typed(self) -> dict[str, Any]:
        """Load checkpoint with proper typing for mutation."""

        raw = self._load_checkpoint()
        # Ensure nested dicts are mutable Mapping
        if "cycle_run_ids" not in raw:
            raw["cycle_run_ids"] = {}
        if "cycle_status" not in raw:
            raw["cycle_status"] = {}
        return raw  # type: ignore[return-value]

    def _save_checkpoint(self, state: dict[str, object]) -> None:
        import json

        (self._config.state_dir / "checkpoint.json").write_text(
            json.dumps(state, indent=2)
        )

    def _write_cycle_report(self, cycle: int, report: str) -> None:
        reports_dir = self._config.state_dir / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        (reports_dir / f"cycle_{cycle:03d}.md").write_text(report + "\n")

    def _write_loop_report(self, history: list[CycleResult]) -> None:
        objectives = sorted({
            name
            for task in self._config.task_schedule
            for name in _objectives_for(task)
        })

        # Compute gate calibration counts across all cycles
        total_l0 = sum(r.n_records for r in history)
        total_l1 = sum(r.n_l1 for r in history)
        total_l2 = sum(r.n_l2 for r in history)
        l0_to_l1_rate = (total_l1 / total_l0 * 100) if total_l0 > 0 else 0
        l1_to_l2_rate = (total_l2 / total_l1 * 100) if total_l1 > 0 else 0

        # Compute metric gaps (unmeasured objectives per task)
        measured_set = set(measured_objectives())
        task_registry = get_task_registry()
        metric_gaps = []
        for task_name in self._config.task_schedule:
            task_spec = task_registry.get(task_name)
            declared = {o.name for o in task_spec.measured_objectives()}
            unmeasured = declared - measured_set
            if unmeasured:
                metric_gaps.append(f"{task_name}: {', '.join(sorted(unmeasured))}")

        lines = [
            "# Computronium Experiment Loop",
            "",
            f"- cycles: {len(history)}",
            f"- tasks: {', '.join(self._config.task_schedule)}",
            f"- objective set: {', '.join(objectives)}",
            "",
            "| cycle | task | kind | records | pass | L1 | L2 | baseline |",
            "|------:|------|------|--------:|-----:|---:|---:|----------|",
        ]
        for r in history:
            lines.append(
                f"| {r.cycle} | {r.task} | {r.kind} | {r.n_records} | {r.n_pass} "
                f"| {r.n_l1} | {r.n_l2} | {'yes' if r.baseline_present else 'no'} |"
            )
        lines += [
            "",
            "## Gate Calibration",
            "",
            f"- L0→L1 promotion rate: {l0_to_l1_rate:.1f}% ({total_l1}/{total_l0})",
            f"- L1→L2 promotion rate: {l1_to_l2_rate:.1f}% ({total_l2}/{total_l1})",
            "- Threshold guidance: >90% ⇒ too loose; <5% ⇒ too strict",
            "",
            "## Metric Gaps (Unmeasured Objectives)",
            "",
        ]
        if metric_gaps:
            for gap in metric_gaps:
                lines.append(f"- {gap}")
        else:
            lines.append("- (all declared objectives are measured)")
        lines += [
            "",
            "## Limitations",
            "",
            "- Coverage is the cheap multi-domain set; language and graph tasks are "
            "not yet in the fast path.",
            "- The frontier is comparable within-task only until every task has an "
            "online baseline (TODO63 Phase 2).",
        ]
        (self._config.state_dir / "report.md").write_text("\n".join(lines) + "\n")


__all__ = [
    "DEFAULT_TASK_SCHEDULE",
    "CycleResult",
    "LoopConfig",
    "LoopDriver",
]
