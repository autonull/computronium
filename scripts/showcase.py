#!/usr/bin/env python
"""1-Hour Comprehensive Showcase Campaign (Adaptive)

Runs a full experimental campaign demonstrating the system's capabilities:
- Multi-substrate (digital, analog, memristive, optical, quantum, sparse, ternary, complex, neuromorphic)
- Multi-credit (gradient, equilibrium_prop, feedback_alignment, hebbian, pepita, local_contrastive, random_projections, temporal_trace, target_inversion, homeostatic, pcalm, lemma, local_goodness)
- Multi-dynamics (energy_minimization, predictive_settling, error_predictive_coding, pc_alm, spike_integration, instantaneous, diffusion, lazy)
- Multi-plasticity (null, routing, fast_weights, substrate_coupled, rule_state, temporal_psi, conflict_adaptive)
- Multi-task domains (vision: MNIST/Fashion-MNIST/digits/USPS/KMNIST/CIFAR10, tabular: breast_cancer/wine/iris, RL: cartpole/pendulum/acrobot, graph: cora/citeseer/pubmed, language: tiny_shakespeare/char_ngram)
- Rigorous HPO with NSGA-II multi-objective optimization
- Statistical validation (multiple seeds, effect sizes, power analysis)
- Dynamical stability analysis (Lyapunov, basin, settling)
- Checkpoint/resume for efficient re-execution
- Full export/import/repro round-trip
- Publication-ready HTML reports with stability analysis

Usage:
    uv run scripts/showcase.py [--dry-run] [--store PATH] [--device auto|cpu|cuda] [--strategy broad_shallow|balanced|narrow_deep] [--hours N]

Expected runtime: ~1 hour on RTX 3080 (GPU) or ~2-3 hours on CPU
"""

import argparse
import asyncio
import json
import signal
import sys
import time
from pathlib import Path

import torch


def _signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print(f"\nReceived signal {signum}, finishing current run...")
    sys.exit(1)


async def run_showcase(
    store: str = "results/showcase_1hr.db",
    device: str = "auto",
    dry_run: bool = False,
    strategy: str = "balanced",
    hours: float = 1.0,
) -> int:
    """Run the showcase campaign using adaptive budget planner."""
    from computronium.experiment.execution.adaptive_budget import (
        BudgetPlanner,
        BudgetStrategy,
        DeviceClass,
        create_campaign_yaml,
    )
    from computronium.experiment.execution.campaign import run_campaign

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    # Parse strategy
    try:
        budget_strategy = BudgetStrategy(strategy.lower())
    except ValueError:
        print(
            f"Invalid strategy: {strategy}. Choose from: broad_shallow, balanced, narrow_deep"
        )
        return 1

    # Resolve device class for planner
    if device == "auto":
        device_class = DeviceClass.GPU if torch.cuda.is_available() else DeviceClass.CPU
    elif device == "cuda":
        device_class = DeviceClass.GPU
    else:
        device_class = DeviceClass.CPU

    print("=" * 70)
    print("COMPUTRONIUM ADAPTIVE SHOWCASE CAMPAIGN")
    print("=" * 70)
    print(f"Time budget: {hours}h")
    print(f"Strategy: {budget_strategy.value}")
    print(f"Device: {device} ({device_class.value})")
    print(f"Store: {store}")
    print(f"Dry run: {dry_run}")
    print()

    # Generate adaptive plan
    planner = BudgetPlanner()
    plan = planner.plan(
        time_budget_hours=hours,
        strategy=budget_strategy,
        device_class=device_class,
    )

    print(f"Campaign: {plan.strategy.value}_{hours}h")
    print(f"Estimated time: {plan.estimated_hours:.2f}h")
    print(f"Rounds: {plan.n_rounds}")
    print(f"Cells/round: {plan.cells_per_round}")
    print(f"Trials: {plan.n_trials}")
    print(f"Seeds: {plan.n_seeds}")
    print(f"Epochs: {plan.epochs}")
    print(f"Substrates ({len(plan.substrates)}): {', '.join(plan.substrates)}")
    print(f"Geometries ({len(plan.geometries)}): {', '.join(plan.geometries)}")
    print(f"Credits ({len(plan.credits)}): {', '.join(plan.credits)}")
    print(f"Dynamics ({len(plan.dynamics)}): {', '.join(plan.dynamics)}")
    print(f"Updates ({len(plan.updates)}): {', '.join(plan.updates)}")
    print(f"Plasticities ({len(plan.plasticities)}): {', '.join(plan.plasticities)}")
    print(
        f"Tasks ({len(plan.tasks)}): {', '.join(plan.tasks[:10])}{'...' if len(plan.tasks) > 10 else ''}"
    )
    print(f"\nRuns ({len(plan.runs)}):")
    for i, run in enumerate(plan.runs):
        deps = f" (depends on: {run['depends_on']})" if run["depends_on"] else ""
        print(f"  [{i}] {run['name']}: {run['profile']}{deps}")
    print()

    # Generate campaign YAML
    campaign_file = f"campaign_showcase_{budget_strategy.value}_{hours}h.yaml"
    yaml_path = create_campaign_yaml(plan, campaign_file)
    print(f"YAML written to: {yaml_path}")

    # Read the store path from the generated YAML
    import yaml

    with Path(yaml_path).open(encoding="utf-8") as f:
        campaign_data = yaml.safe_load(f)
    actual_store = campaign_data.get("store", store)
    print(f"Using store: {actual_store}")

    if dry_run:
        print("\nDRY RUN - would execute the above campaign")
        plan_dict = {
            "command": "showcase_1hr",
            "campaign": plan.strategy.value,
            "store": actual_store,
            "parallel": 1,
            "device": device,
            "runs": plan.runs,
        }
        print(json.dumps(plan_dict, indent=2))
        return 0

    # Ensure results directory exists
    Path("results").mkdir(exist_ok=True)
    Path("artifacts").mkdir(exist_ok=True)

    print(f"Starting campaign execution at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    start_time = time.time()

    try:
        result = await run_campaign(
            Path(campaign_file),
            parallel=1,
            device=device,
        )
    except KeyboardInterrupt:
        print("\nCampaign interrupted by user")
        return 130
    except Exception as e:
        print(f"\nCampaign execution failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    elapsed = time.time() - start_time
    print(f"\nCampaign completed in {elapsed:.1f}s ({elapsed / 3600:.2f}h)")

    # Print summary
    if result.get("run_results"):
        print(f"\nCampaign '{result['campaign']}' completed")
        print(f"  Total runs: {result['total_runs']}")
        print(f"  Completed: {result['completed']}")
        print(f"  Failed: {result['failed']}")
        for idx, run_result in result["run_results"].items():
            status = "OK" if run_result["success"] else "FAILED"
            if run_result.get("skipped"):
                status = "SKIPPED"
            run_name = plan.runs[idx]["name"]
            elapsed_s = run_result.get("elapsed_s", 0)
            print(f"  [{idx}] {run_name}: {status} ({elapsed_s:.1f}s)")
            if not run_result["success"] and not run_result.get("skipped"):
                print(f"       Error: {run_result.get('error', 'unknown')}")

    # Generate final report
    print("\n" + "=" * 70)
    print("POST-CAMPAIGN ANALYSIS")
    print("=" * 70)

    # Import here to avoid circular imports
    from computronium.experiment.evidence.store import RecordStore, StoreConfig
    from computronium.experiment.surface.report import generate_html_report

    report_path = f"{Path(actual_store).with_suffix('')}_report.html"
    main_run_id = None

    if Path(actual_store).exists():
        store_obj = RecordStore(StoreConfig(actual_store))
        with store_obj:
            runs = store_obj.query_runs()
            if runs:
                # Report the run carrying the most records: the comprehensive
                # campaign run, never an individual task run. Reversed (oldest
                # first) so the earliest run wins a record-count tie.
                main_run = max(
                    reversed(runs),
                    key=lambda r: len(store_obj.query_records(run_id=r.run_id)),
                )
                main_run_id = main_run.run_id
                print(f"\nGenerating report for run: {main_run_id}")
                try:
                    report_file = generate_html_report(
                        store_obj, run_id=main_run_id, output_path=Path(report_path)
                    )
                    print(f"HTML report written to: {report_file}")
                except Exception as e:
                    print(f"Report generation failed: {e}")

    # Stability and statistics open their own store connection; DuckDB refuses a
    # second configuration on the same file, so they run after reporting closes.
    # Both go through the real surface parser so their Namespace stays in step.
    if main_run_id is not None:
        from computronium.experiment.surface.cli import main as surface_main

        print("\nRunning stability analysis on claim-eligible cells...")
        try:
            surface_main([
                "stability-analysis",
                "--store",
                actual_store,
                "--run-id",
                main_run_id,
                "--lyapunov",
                "--basin",
                "--basin-samples",
                "50",
                "--settling",
                "--settling-steps",
                "500",
                "--device",
                device,
                "--format",
                "text",
            ])
        except Exception as e:
            print(f"Stability analysis failed: {e}")

        print("\nRunning statistical analysis...")
        try:
            surface_main([
                "stats",
                "--store",
                actual_store,
                "--run-id",
                main_run_id,
                "--group-by",
                "dynamics,credit,substrate",
                "--format",
                "json",
            ])
        except Exception as e:
            print(f"Statistics failed: {e}")

    artifacts_dir = campaign_data.get("output", {}).get(
        "artifacts_dir", "artifacts/showcase"
    )
    print("\n" + "=" * 70)
    print("SHOWCASE COMPLETE")
    print("=" * 70)
    print(f"\nResults stored in: {actual_store}")
    print(f"Artifacts in: {artifacts_dir}/")
    print(f"Report in: {report_path}")
    print("\nNext steps:")
    print(f"  1. View HTML report: open {report_path}")
    print(
        f"  2. Run Pareto analysis: uv run comp pareto --store {actual_store} --objectives validation_accuracy,walltime_total --weights 0.7,0.3 --scalarize --output pareto.csv"
    )
    print(
        f"  3. Export data: uv run comp export --store {actual_store} --format json --output export.json"
    )
    print(
        f"  4. Run hypothesis tests: uv run comp hypothesis-campaign --store {actual_store} --templates templates/hypotheses.json"
    )

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Run adaptive showcase campaign (time budget + strategy)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Strategies:
  broad_shallow  - All components, few epochs/seeds (max diversity)
  balanced       - All components, moderate epochs/seeds (default)
  narrow_deep    - Core models only, many epochs/seeds (max depth)

Examples:
    uv run scripts/showcase_1hr.py                           # 1h balanced on auto device
    uv run scripts/showcase_1hr.py --hours 2 --strategy broad_shallow
    uv run scripts/showcase_1hr.py --hours 0.5 --strategy narrow_deep --device cpu
    uv run scripts/showcase_1hr.py --dry-run                 # Preview plan
        """,
    )
    parser.add_argument(
        "--store",
        default="results/showcase_1hr.db",
        help="DuckDB store path (default: results/showcase_1hr.db)",
    )
    parser.add_argument(
        "--device",
        choices=["auto", "cpu", "cuda"],
        default="auto",
        help="Device to run on (default: auto)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate campaign and print plan without running",
    )
    parser.add_argument(
        "--strategy",
        choices=["broad_shallow", "balanced", "narrow_deep"],
        default="balanced",
        help="Campaign strategy (default: balanced)",
    )
    parser.add_argument(
        "--hours",
        type=float,
        default=1.0,
        help="Time budget in hours (default: 1.0)",
    )

    args = parser.parse_args()

    # Resolve device
    if args.device == "auto":
        resolved_device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        resolved_device = args.device

    print(
        f"Resolved device: {resolved_device} (CUDA available: {torch.cuda.is_available()})"
    )

    return asyncio.run(
        run_showcase(
            store=args.store,
            device=resolved_device,
            dry_run=args.dry_run,
            strategy=args.strategy,
            hours=args.hours,
        )
    )


if __name__ == "__main__":
    sys.exit(main())
