"""Unified CLI entry point for all experiment types.

Usage:
    uv run python -m computronium.experiment.cli run \
      --spec experiment_specs/ablation_update.yaml \
      --device auto

    uv run python -m computronium.experiment.cli run \
      --type ablation --vary update --fix geometry=feedforward dynamics=instantaneous \
      --budget 1h --seeds 5
"""

from __future__ import annotations

import argparse
import asyncio
import time
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from computronium.experiment.schema.experiment_spec import ExperimentSpec


def _parse_axis_value(s: str) -> tuple[str, str]:
    """Parse axis=value pair."""
    if "=" not in s:
        raise ValueError(f"Expected axis=value, got {s}")
    axis, value = s.split("=", 1)
    return axis.strip(), value.strip()


def _parse_time_budget(s: str) -> float:
    """Parse time budget string (e.g., '1h', '30m', '3600')."""
    s = s.strip().lower()
    if s.endswith("h"):
        return float(s[:-1]) * 3600
    if s.endswith("m"):
        return float(s[:-1]) * 60
    if s.endswith("s"):
        return float(s[:-1])
    return float(s)


async def _run_from_spec(
    spec: ExperimentSpec, device: str = "auto", output_dir: str | None = None
) -> None:
    """Run an experiment from an ExperimentSpec."""
    from computronium.experiment.evidence.store import RecordStore, StoreConfig
    from computronium.experiment.execution.backends import LocalBackend
    from computronium.experiment.execution.deadline import Deadline
    from computronium.experiment.execution.pipeline import (
        PipelineConfig,
        PipelineRunner,
    )
    from computronium.experiment.runners.ablation import AblationRunner, AblationSpec
    from computronium.experiment.runners.comparison import (
        ComparisonRunner,
        ComparisonSpec,
    )
    from computronium.experiment.runners.replay import ReplayRunner, ReplaySpec
    from computronium.experiment.runners.scaling import ScalingRunner, ScalingSpec

    # Create output directory
    out_dir = Path(output_dir or spec.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Create store
    db_path = out_dir / f"{spec.name}.db"
    store = RecordStore(StoreConfig(path=db_path))
    backend = LocalBackend(max_workers=4)

    match spec.type:
        case "ablation":
            if spec.ablation is None:
                raise ValueError("ablation config required")
            ablation_spec = AblationSpec(
                vary=spec.ablation.vary,
                fix=spec.ablation.fix,
                n_seeds=spec.ablation.n_seeds,
                budget_seconds=spec.budget.seconds or 3600,
                metric=spec.ablation.metric,
                task=spec.tasks[0] if spec.tasks else "digits",
            )
            runner = AblationRunner(ablation_spec, store=store, backend=backend)
            result = await runner.run()
            runner.print_results(result)

        case "comparison":
            if spec.comparison is None:
                raise ValueError("comparison config required")
            comparison_spec = ComparisonSpec(
                arm_a=spec.comparison.arm_a,
                arm_b=spec.comparison.arm_b,
                n_seeds=spec.comparison.n_seeds,
                budget_seconds=spec.budget.seconds or 3600,
                metric=spec.comparison.metric,
                test=spec.comparison.test,
                task=spec.tasks[0] if spec.tasks else "digits",
            )
            runner = ComparisonRunner(comparison_spec, store=store, backend=backend)
            result = await runner.run()
            runner.print_results(result)

        case "replay":
            if spec.replay is None:
                raise ValueError("replay config required")
            replay_spec = ReplaySpec(
                source_db=spec.replay.source_db,
                check_metrics=spec.replay.check_metrics,
                tolerance=spec.replay.tolerance,
                budget_seconds=spec.budget.seconds or 3600,
                task=spec.tasks[0] if spec.tasks else None,
            )
            runner = ReplayRunner(replay_spec, store=store, backend=backend)
            result = await runner.run()
            runner.print_results(result)

        case "scaling":
            if spec.scaling is None:
                raise ValueError("scaling config required")
            base_coord = None
            if spec.scaling.base_config:
                base_coord = spec.scaling.base_config
            scaling_spec = ScalingSpec(
                vary=spec.scaling.vary,
                log_scale=spec.scaling.log_scale,
                n_points_per_dim=spec.scaling.n_points_per_dim,
                base_config=base_coord,
                n_seeds=spec.seeds if isinstance(spec.seeds, int) else spec.seeds[0],
                budget_seconds=spec.budget.seconds or 3600,
                metric=spec.scaling.metric,
                task=spec.tasks[0] if spec.tasks else "digits",
            )
            runner = ScalingRunner(scaling_spec, store=store, backend=backend)
            result = await runner.run()
            runner.print_results(result)

        case "showcase" | "grid" | "multi_task":
            # Use the standard pipeline
            run_spec = spec.to_run_spec()
            run_id = f"{spec.name}_{int(time.time())}"

            pipeline = PipelineRunner(
                config=PipelineConfig(
                    run_id=run_id,
                    run_spec=run_spec,
                    deadline=Deadline.from_seconds(spec.budget.seconds or 3600),
                    backend=backend,
                ),
                store=store,
            )
            records = await pipeline.run()
            print(f"Completed {len(records)} cells")

        case _:
            raise ValueError(f"Unknown experiment type: {spec.type}")


async def _run_inline(
    type: str,
    vary: list[str],
    fix: dict[str, str],
    budget: float,
    seeds: int,
    metric: str,
    task: str | None,
    device: str,
) -> None:
    """Run an experiment from inline CLI arguments."""
    from pathlib import Path

    from computronium.experiment.evidence.store import RecordStore, StoreConfig
    from computronium.experiment.execution.backends import LocalBackend
    from computronium.experiment.runners.ablation import AblationRunner, AblationSpec
    from computronium.experiment.runners.comparison import (
        ComparisonRunner,
        ComparisonSpec,
    )
    from computronium.experiment.runners.scaling import ScalingRunner, ScalingSpec
    from computronium.experiment.schema.axis import StructuralAxis
    from computronium.experiment.schema.coordinate import Coordinate

    store = RecordStore(StoreConfig(path=Path(":memory:")))
    backend = LocalBackend(max_workers=4)

    if type == "ablation":
        if len(vary) != 1:
            raise ValueError("ablation requires exactly one --vary axis")
        vary_axis = StructuralAxis(vary[0])
        fix_axes = {StructuralAxis(k): v for k, v in fix.items()}

        spec = AblationSpec(
            vary=vary_axis,
            fix=fix_axes,
            n_seeds=seeds,
            budget_seconds=budget,
            metric=metric,
            task=task,
        )
        runner = AblationRunner(spec, store=store, backend=backend)
        result = await runner.run()
        runner.print_results(result)

    elif type == "comparison":
        # Parse arm_a and arm_b from fix (they should be prefixed)
        arm_a = {}
        arm_b = {}
        for k, v in fix.items():
            if k.startswith("arm_a."):
                arm_a[StructuralAxis(k[6:])] = v
            elif k.startswith("arm_b."):
                arm_b[StructuralAxis(k[6:])] = v

        if not arm_a or not arm_b:
            raise ValueError("comparison requires arm_a.* and arm_b.* fix parameters")

        spec = ComparisonSpec(
            arm_a=arm_a,
            arm_b=arm_b,
            n_seeds=seeds,
            budget_seconds=budget,
            metric=metric,
            task=task,
        )
        runner = ComparisonRunner(spec, store=store, backend=backend)
        result = await runner.run()
        runner.print_results(result)

    elif type == "scaling":
        # Parse base_config from fix (without arm_a/arm_b prefixes)
        base_config = {}
        for k, v in fix.items():
            if not k.startswith("arm_a.") and not k.startswith("arm_b."):
                base_config[k] = v

        base_coord = None
        if base_config:
            base_coord = Coordinate(
                substrate=base_config.get("substrate", "digital"),
                geometry=base_config.get("geometry", "feedforward"),
                dynamics=base_config.get("dynamics", "instantaneous"),
                plasticity=base_config.get("plasticity", "null"),
                credit=base_config.get("credit", "gradient"),
                update=base_config.get("update", "euclidean"),
                params={},
            )

        vary_params = (
            vary if vary else ["hidden_dims", "param_budget", "settle_horizon"]
        )

        spec = ScalingSpec(
            vary=vary_params,
            log_scale=True,
            n_points_per_dim=4,
            base_config=base_coord,
            n_seeds=seeds,
            budget_seconds=budget,
            metric=metric,
            task=task,
        )
        runner = ScalingRunner(spec, store=store, backend=backend)
        result = await runner.run()
        runner.print_results(result)

    else:
        raise ValueError(f"Inline mode not supported for type: {type}")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Unified experiment CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run from spec file
  uv run python -m computronium.experiment.cli run --spec experiment_specs/ablation.yaml

  # Run ablation inline
  uv run python -m computronium.experiment.cli run \\
    --type ablation --vary update \\
    --fix geometry=feedforward --fix dynamics=instantaneous \\
    --budget 1h --seeds 5

  # Run comparison inline
  uv run python -m computronium.experiment.cli run \\
    --type comparison \\
    --fix arm_a.geometry=feedforward --fix arm_a.dynamics=instantaneous --fix arm_a.credit=gradient \\
    --fix arm_b.geometry=recurrent --fix arm_b.dynamics=energy_minimization --fix arm_b.credit=thermodynamic_contrast \\
    --seeds 10 --budget 2h

  # Run scaling inline
  uv run python -m computronium.experiment.cli run \\
    --type scaling --vary hidden_dims --vary param_budget \\
    --fix geometry=feedforward --fix dynamics=instantaneous --fix credit=gradient --fix update=euclidean \\
    --budget 1h --seeds 5
        """,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # run command
    run_parser = subparsers.add_parser("run", help="Run an experiment")
    run_parser.add_argument("--spec", help="Path to ExperimentSpec YAML/JSON file")
    run_parser.add_argument(
        "--type",
        choices=[
            "showcase",
            "ablation",
            "scaling",
            "comparison",
            "replay",
            "multi_task",
        ],
        help="Experiment type (for inline mode)",
    )
    run_parser.add_argument(
        "--vary", action="append", default=[], help="Axis to vary (ablation)"
    )
    run_parser.add_argument(
        "--fix", action="append", default=[], help="Fixed axis=value pairs"
    )
    run_parser.add_argument(
        "--budget",
        type=_parse_time_budget,
        default=3600,
        help="Time budget (e.g., 1h, 30m, 3600)",
    )
    run_parser.add_argument("--seeds", type=int, default=1, help="Number of seeds")
    run_parser.add_argument(
        "--metric", default="validation_accuracy", help="Primary metric"
    )
    run_parser.add_argument("--task", help="Task name")
    run_parser.add_argument(
        "--device", default="auto", choices=["auto", "cpu", "cuda"], help="Device"
    )
    run_parser.add_argument(
        "--output", default="experiments/output", help="Output directory"
    )

    args = parser.parse_args()

    if args.command == "run":
        if args.spec:
            # Load from spec file
            from computronium.experiment.schema.experiment_spec import ExperimentSpec

            spec = ExperimentSpec.load(args.spec)
            asyncio.run(_run_from_spec(spec, args.device, args.output))
        elif args.type:
            # Inline mode
            fix_dict = {}
            for pair in args.fix:
                axis, value = _parse_axis_value(pair)
                fix_dict[axis] = value

            asyncio.run(
                _run_inline(
                    type=args.type,
                    vary=args.vary,
                    fix=fix_dict,
                    budget=args.budget,
                    seeds=args.seeds,
                    metric=args.metric,
                    task=args.task,
                    device=args.device,
                )
            )
        else:
            parser.error("Either --spec or --type is required")


if __name__ == "__main__":
    main()
