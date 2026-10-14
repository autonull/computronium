"""LoopDriver — the engine-driven closed experiment loop (TODO63 Phase 1).

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

Nothing here re-implements proposal, promotion, or reporting: ``cli._cmd_loop``
is a thin argparse wrapper that builds :class:`LoopConfig` and calls
:meth:`LoopDriver.run`.
"""

from __future__ import annotations

import logging
import signal
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

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
from computronium.experiment.schema.metrics import measured_objectives
from computronium.experiment.schema.record import GateVerdict, Maturity
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

    # ------------------------------------------------------------------ public

    def run(self, *, dry_run: bool = False) -> int:
        """Run the loop until the cycle limit or time budget is exhausted.

        With ``dry_run=True`` the plan is computed through the same builders and
        printed, spending no cells.
        """
        cfg = self._config
        cfg.state_dir.mkdir(parents=True, exist_ok=True)
        cfg.store_path.parent.mkdir(parents=True, exist_ok=True)

        checkpoint = self._load_checkpoint()
        saved_cycle = checkpoint.get("cycle")
        cycle = saved_cycle if isinstance(saved_cycle, int) else 0
        master_seed = self._resolve_master_seed(checkpoint)

        start_cycle = cycle
        deadline_time = time.time() + cfg.hours * 3600
        history: list[CycleResult] = []

        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

        print("=" * 70, flush=True)
        print("COMPUTRONIUM EXPERIMENT LOOP (engine-driven)", flush=True)
        print(f"  Store:   {cfg.store_path}", flush=True)
        print(f"  State:   {cfg.state_dir}", flush=True)
        print(f"  Seed:    {master_seed}", flush=True)
        print(f"  Tasks:   {', '.join(cfg.task_schedule)}", flush=True)
        print(f"  Resume:  cycle {cycle}", flush=True)
        print("=" * 70, flush=True)

        if dry_run:
            return self._dry_run(cycle, master_seed)

        while not self._abort:
            if cfg.cycles and (cycle - start_cycle) >= cfg.cycles:
                print("Cycle limit reached.", flush=True)
                break
            if time.time() >= deadline_time:
                print("Budget exhausted.", flush=True)
                break

            result = self._run_cycle(cycle, master_seed)
            history.append(result)
            cycle += 1
            checkpoint.update({"cycle": cycle, "master_seed": master_seed})
            self._save_checkpoint(checkpoint)
            self._write_loop_report(history)

            print(
                f"  → task={result.task} kind={result.kind} "
                f"records={result.n_records} pass={result.n_pass} "
                f"L1={result.n_l1} L2={result.n_l2} "
                f"baseline={'yes' if result.baseline_present else 'no'} "
                f"({result.duration_s:.1f}s)",
                flush=True,
            )

        self._write_loop_report(history)
        print("\n" + "=" * 70, flush=True)
        print(f"LOOP STOPPED at cycle {cycle}", flush=True)
        print(f"Report: {cfg.state_dir / 'report.md'}", flush=True)
        print("=" * 70, flush=True)
        return 0

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

    def _run_cycle(self, cycle: int, master_seed: int) -> CycleResult:
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

        import asyncio

        try:
            result = asyncio.run(self._execute(cycle, spec, task))
        except KeyboardInterrupt:
            raise
        except Exception as exc:  # ruff: ignore[blind-except] - one bad cycle must not kill the loop
            logger.error("Cycle %d (%s) failed: %s", cycle, task, exc, exc_info=True)
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
        )

    async def _execute(self, cycle: int, spec: RunSpec, task: str) -> CycleResult:
        cfg = self._config
        with ExperimentRegistry(
            ExperimentConfig(
                store_path=cfg.store_path,
                spec=spec,
                master_seed=cfg.master_seed,
            )
        ) as registry:
            store = registry.store
            run_id = registry.run_id
            registry.start_cycle(cycle)

            deadline = (
                Deadline.from_seconds(spec.budget_seconds)
                if spec.budget_seconds
                else None
            )
            policy_name = spec.policy or "round_robin_grid"
            policy = create_policy(
                policy_name,
                **policy_context(
                    spec, policy_name, shape=task_shape, deadline=deadline
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
            duration_s=0.0,
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
        try:
            return self._exploit_axes(store, task)
        finally:
            store.__exit__(None, None, None)

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

        frontier = compute_pareto_frontier(records, list(_objectives_for(task)))
        front_keys = {point.cell_key for point in frontier.front()}
        front_records = [r for r in records if r.cell_key in front_keys]
        if not front_records:
            return self._explore_axes()

        union: dict[StructuralAxis, set[str]] = {axis: set() for axis in StructuralAxis}
        for record in front_records:
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
        return {}

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
