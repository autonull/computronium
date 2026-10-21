"""The surface CLI's campaign, loop, baseline, and coverage commands."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import TYPE_CHECKING

from computronium.core.logging import get_logger
from computronium.experiment.evidence.store import RecordStore, StoreConfig

from ._execution import _CELL_WORKERS
from ._profiles import RUN_PROFILES

if TYPE_CHECKING:
    import argparse

logger = get_logger()


def _cmd_campaign(args: argparse.Namespace) -> int:  # ruff: ignore[complex-structure, too-many-branches, too-many-statements]
    """Execute a declarative multi-run campaign from YAML."""

    from computronium.experiment.execution.campaign import load_campaign, run_campaign

    campaign_path = Path(args.campaign_file)
    if not campaign_path.exists():
        logger.error(f"Campaign file not found: {campaign_path}")
        return 1

    try:
        spec = load_campaign(campaign_path)
    except Exception as e:
        logger.error(f"Failed to load campaign: {e}")  # ruff: ignore[error-instead-of-exception]
        return 1

    if args.dry_run:
        # Print execution plan
        if args.format == "json":
            plan = {
                "command": "campaign",
                "campaign": spec.name,
                "store": spec.store,
                "parallel": args.parallel or spec.parallel,
                "device": args.device or "auto",
                "webhook_url": args.webhook_url or spec.webhook_url,
                "runs": [
                    {
                        "index": i,
                        "name": run.name,
                        "profile": run.profile,
                        "spec_file": run.spec_file,
                        "depends_on": run.depends_on,
                        "overrides": run.overrides,
                    }
                    for i, run in enumerate(spec.runs)
                ],
            }
            output = json.dumps(plan, indent=2)
            if args.output:
                Path(args.output).write_text(output, encoding="utf-8")
                logger.info(f"Dry run plan written to {args.output}")
            else:
                print(output)
        else:
            print(f"Campaign: {spec.name}")
            print(f"Store: {spec.store}")
            print(f"Parallel: {args.parallel or spec.parallel}")
            print(f"Device: {args.device or 'auto'}")
            print(f"Webhook: {args.webhook_url or spec.webhook_url or 'none'}")
            print(f"Runs ({len(spec.runs)}):")
            for i, run in enumerate(spec.runs):
                deps = f" (depends on: {run.depends_on})" if run.depends_on else ""
                profile_or_spec = run.profile or run.spec_file
                print(f"  [{i}] {run.name}: {profile_or_spec}{deps}")
        return 0

    try:
        result = asyncio.run(
            run_campaign(
                campaign_path,
                parallel=args.parallel,
                device=args.device,
                webhook_url=args.webhook_url,
            )
        )
    except Exception:
        logger.exception("Campaign execution failed")
        return 1

    # Print summary
    if args.format == "json":
        if args.output:
            Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
            logger.info(f"Results written to {args.output}")
        else:
            print(json.dumps(result, indent=2))
    else:
        print(f"\nCampaign '{result['campaign']}' completed")
        print(f"  Total runs: {result['total_runs']}")
        print(f"  Completed: {result['completed']}")
        print(f"  Failed: {result['failed']}")
        for idx, run_result in result["run_results"].items():
            status = "OK" if run_result["success"] else "FAILED"
            if run_result.get("skipped"):
                status = "SKIPPED"
            run_name = spec.runs[idx].name
            elapsed = run_result.get("elapsed_s", 0)
            print(f"  [{idx}] {run_name}: {status} ({elapsed:.1f}s)")
            if not run_result["success"] and not run_result.get("skipped"):
                print(f"       Error: {run_result.get('error', 'unknown')}")

        if args.output:
            Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
            logger.info(f"Results written to {args.output}")

    return 0 if result["failed"] == 0 else 1


def _cmd_loop(args: argparse.Namespace) -> int:
    """Continuous autonomous experiment loop: explore/exploit cycles with a
    time budget.

    A thin wrapper: :class:`LoopDriver` composes the engine (registry, pipeline,
    policy, statistical promotion, baselines, multi-objective frontier). No
    proposal, promotion, or reporting is re-implemented here.
    """
    from computronium.experiment.registry.loop import LoopConfig, LoopDriver
    from computronium.experiment.schema import _ensure_registries_seeded

    _ensure_registries_seeded()
    profile = RUN_PROFILES[args.profile]
    hypothesis_ids = tuple(
        h.strip() for h in args.hypothesis_ids.split(",") if h.strip()
    )
    hypothesis_registry_path = (
        Path(args.hypothesis_registry) if args.hypothesis_registry else None
    )
    # Use CLI --n-seeds if provided, otherwise fall back to profile default
    n_seeds = args.n_seeds if args.n_seeds is not None else profile.n_seeds
    config = LoopConfig(
        store_path=Path(args.store),
        state_dir=Path(args.state_dir),
        stages=tuple(profile.stages),
        param_budget=profile.param_budget,
        policy=profile.policy,
        hyperparameters=dict(profile.hyperparameters),
        checkpoint_every_n=profile.checkpoint_every_n,
        device=args.device,
        master_seed=args.seed,
        hours=args.hours,
        cycles=args.cycles,
        n_seeds=n_seeds,
        explore_fidelity=args.explore_fidelity,
        exploit_fidelity=args.exploit_fidelity,
        explore_hours=args.explore_hours,
        exploit_hours=args.exploit_hours,
        explore_sweep_steps=args.explore_sweep_steps,
        exploit_sweep_steps=args.exploit_sweep_steps,
        cell_workers=_CELL_WORKERS,
        hypothesis_ids=hypothesis_ids,
        hypothesis_registry_path=hypothesis_registry_path,
        use_icu_guided=args.use_icu_guided,
    )
    return LoopDriver(config).run(dry_run=args.dry_run)


def _cmd_baseline(args: argparse.Namespace) -> int:
    """Online baseline discovery and registry commands."""
    import json
    from pathlib import Path

    from computronium.experiment.registry.baseline import BaselineRegistry

    # Ensure registries are seeded
    from computronium.experiment.schema import _ensure_registries_seeded

    _ensure_registries_seeded()

    if args.baseline_command == "list":
        registry = BaselineRegistry()
        baselines = (
            registry.get_baselines_for_task(args.task)
            if args.task
            else registry.STANDARD_BASELINES
        )

        if args.format == "json":
            output = json.dumps(
                [
                    {
                        "name": b.name,
                        "description": b.description,
                        "domain": b.domain,
                        "optimizer": b.optimizer,
                        "architecture": b.architecture,
                        "geometry": b.geometry,
                        "credit": b.credit,
                        "dynamics": b.dynamics,
                        "update": b.update,
                        "plasticity": b.plasticity,
                        "substrate": b.substrate,
                        "hyperparameters": b.hyperparameters,
                        "applicable_tasks": b.applicable_tasks,
                    }
                    for b in baselines
                ],
                indent=2,
            )
            print(output)
        else:
            print("Available Baseline Configurations")
            print("=" * 70)
            for b in baselines:
                print(f"\n{b.name}")
                print(f"  Domain: {b.domain}")
                print(f"  Description: {b.description}")
                print(f"  Optimizer: {b.optimizer}")
                print(f"  Architecture: {b.architecture}")
                print(f"  Geometry: {b.geometry}")
                print(f"  Credit: {b.credit}")
                print(f"  Dynamics: {b.dynamics}")
                print(f"  Update: {b.update}")
                print(f"  Plasticity: {b.plasticity}")
                print(f"  Substrate: {b.substrate}")
                print(f"  Hyperparameters: {b.hyperparameters}")
                print(f"  Applicable Tasks: {b.applicable_tasks}")
        return 0

    elif args.baseline_command == "check":
        # Check if baseline exists
        store_path = Path(args.store)
        if not store_path.exists():
            print(f"Store not found: {store_path}")
            return 1

        # Would need to query store for baseline table
        print(
            f"Baseline check for task={args.task}, budget={args.budget_seconds}s, seeds={args.seeds}"
        )
        print("Not yet implemented - requires baseline table in store")
        return 0

    elif args.baseline_command == "run":
        return asyncio.run(_run_baselines_async(args))

    return 0


async def _run_baselines_async(args: argparse.Namespace) -> int:
    """Run baseline discovery asynchronously."""
    import json
    from pathlib import Path

    from computronium.experiment.evidence.store import RecordStore, StoreConfig
    from computronium.experiment.registry.baseline import BaselineRegistry
    from computronium.experiment.registry.seed import SeedContext, SeedContextManager

    store_path = Path(args.store)
    store_path.parent.mkdir(parents=True, exist_ok=True)

    # Initialize seed context
    seed_manager = SeedContextManager(master_seed=args.seed)

    # Create registry with store
    with RecordStore(StoreConfig(path=store_path)) as store:
        registry = BaselineRegistry(store=store)

        # Run discovery
        baselines = await registry.discover_baseline(
            task=args.task,
            budget_seconds=args.budget_seconds,
            n_seeds=args.seeds,
            seed_context=SeedContext(master_seed=seed_manager.master_seed),
        )

        if args.format == "json":
            output = json.dumps([b.to_dict() for b in baselines], indent=2)
            print(output)
        else:
            print(f"Baseline Discovery for {args.task}")
            print(f"  Store: {store_path}")
            print(f"  Budget: {args.budget_seconds}s, Seeds: {args.seeds}")
            print(f"  Master seed: {seed_manager.master_seed}")
            print("=" * 70)
            for b in baselines:
                print(f"\n{b.optimizer}/{b.architecture} on {b.geometry}")
                print(f"  Task metrics: {b.metrics}")
                print(f"  Cost metrics: {b.cost_metrics}")
                print(f"  Ruler metrics: {b.ruler_metrics}")
                print(f"  Run ID: {b.run_id[:8]}")

    return 0


def _cmd_coverage(args: argparse.Namespace) -> int:  # ruff: ignore[complex-structure, too-many-branches, too-many-return-statements, too-many-statements]
    """Cross-domain coverage report commands."""
    import json
    from pathlib import Path

    from computronium.experiment.registry.task_registry import (
        DomainType,
        TaskRegistry,
    )

    if args.coverage_command == "tasks":
        registry = TaskRegistry()
        filter_domain = None
        if args.domain:
            try:
                filter_domain = DomainType(args.domain)
            except ValueError:
                print(f"Unknown domain: {args.domain}")
                print(f"Valid domains: {[d.value for d in DomainType]}")
                return 1

        if args.format == "json":
            tasks = []
            for task in registry:
                if filter_domain and task.domain != filter_domain:
                    continue
                tasks.append({
                    "name": task.name,
                    "domain": task.domain.value,
                    "cost_class": task.cost_class.value,
                    "primary_objective": task.primary_objective,
                    "measured_objectives": [o.name for o in task.measured_objectives()],
                    "unmeasured_objectives": [
                        o.name for o in task.unmeasured_objectives()
                    ],
                    "geometry_hint": task.geometry_hint,
                    "input_shape": task.input_shape,
                    "output_dim": task.output_dim,
                    "tags": list(task.tags),
                })
            print(json.dumps(tasks, indent=2))
        else:
            print("Cross-Domain Task Registry")
            print("=" * 80)
            for task in registry:
                if filter_domain and task.domain != filter_domain:
                    continue
                print(f"\n{task.name} ({task.domain.value})")
                print(f"  Cost: {task.cost_class.value}")
                print(f"  Primary: {task.primary_objective}")
                print(
                    f"  Measured: {', '.join(o.name for o in task.measured_objectives())}"
                )
                if task.unmeasured_objectives():
                    print(
                        f"  Unmeasured: {', '.join(o.name for o in task.unmeasured_objectives())}"
                    )
                print(f"  Geometry hint: {task.geometry_hint}")
                print(f"  Shape: {task.input_shape} -> {task.output_dim}")
        return 0

    elif args.coverage_command == "unmeasured":
        registry = TaskRegistry()
        report = registry.unmeasured_objectives_report()

        if args.format == "json":
            print(json.dumps(report, indent=2))
        else:
            print("Unmeasured Objectives (registered but not emitted)")
            print("=" * 70)
            total_unmeasured = 0
            for task_name, objs in sorted(report.items()):
                print(f"\n{task_name}: {', '.join(objs)}")
                total_unmeasured += len(objs)
            print(
                f"\nTotal: {total_unmeasured} unmeasured objectives across {len(report)} tasks"
            )
        return 0

    elif args.coverage_command == "report":
        store_path = Path(args.store)
        if not store_path.exists():
            print(f"Store not found: {store_path}")
            return 1

        with RecordStore(StoreConfig(path=store_path, read_only=True)) as store:
            run_id = args.run_id or store.latest_run_id()
            if run_id is None:
                print("No runs found in store")
                return 0

            print(f"Coverage Report for run {run_id[:12]}")
            print("=" * 80)

            records = [
                record
                for record in store.query_records(run_id=run_id)
                if record.status.gate_verdict.value == "PASS"
            ]
            if not records:
                print("No PASS records found")
                return 0

            primitives_seen: dict[str, set[str]] = {
                "substrate": set(),
                "geometry": set(),
                "dynamics": set(),
                "plasticity": set(),
                "credit": set(),
                "update": set(),
            }
            for record in records:
                for axis in primitives_seen:
                    primitives_seen[axis].add(getattr(record, axis))

            print(f"Total PASS cells: {len(records)}")
            for axis, names in primitives_seen.items():
                print(f"{axis.title()}: {sorted(names)}")

            registry = TaskRegistry()
            print("\nNote: Full domain×primitive matrix requires task-aware scheduling")
            print(
                f"Registry has {len(registry._enrichments)} tasks across "
                f"{len(registry.all_domains())} domains"
            )

        return 0

    return 0
