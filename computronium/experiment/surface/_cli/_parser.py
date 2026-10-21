"""The surface CLI's argument parser."""

from __future__ import annotations

import argparse
from typing import Any

from ._profiles import CORE_COMMANDS, RUN_PROFILES


def _limit_help(sub: Any) -> None:
    """Keep non-core commands out of ``comp --help`` but fully usable."""
    for action in sub._actions:
        if isinstance(action, argparse._SubParsersAction):
            for choice in action._choices_actions:
                if choice.dest not in CORE_COMMANDS:
                    choice.help = argparse.SUPPRESS


def _build_parser(  # ruff: ignore[too-many-statements, too-many-locals]
    *, full: bool = False
) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="comp-surface",
        description="Computronium Surface CLI — experiment orchestration and reporting",
    )
    parser.add_argument(
        "--help-all",
        action="store_true",
        help="Show every command, including the non-core ones",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # Demo command
    p_demo = sub.add_parser("demo", help="Run the seven-beat demonstration")
    p_demo.add_argument("--store", default="demo.duckdb", help="DuckDB store path")
    p_demo.add_argument(
        "--run-id", default=None, help="Report on this run (latest if omitted)"
    )

    # Run command
    p_run = sub.add_parser("run", help="Execute a run profile or a spec file")
    p_run.add_argument(
        "profile",
        nargs="?",
        choices=list(RUN_PROFILES.keys()),
        help="Run profile to execute (omit when --spec names the run)",
    )
    p_run.add_argument(
        "--profile",
        dest="profile_flag",
        choices=list(RUN_PROFILES.keys()),
        help="Alias for the positional profile",
    )
    p_run.add_argument("--store", default="experiment.duckdb", help="DuckDB store path")
    p_run.add_argument(
        "--device",
        default="auto",
        choices=["auto", "cpu", "cuda"],
        help="Device to run on: auto (CUDA if available), cpu, cuda",
    )
    p_run.add_argument(
        "--run-id",
        default=None,
        help=(
            "Resume this run: the store is the checkpoint, so a relaunch "
            "measures only what the run has not"
        ),
    )
    p_run.add_argument("--spec", default=None, help="RunSpec JSON file")
    p_run.add_argument(
        "--task", default=None, help="Override the profile's task (ignored with --spec)"
    )
    p_run.add_argument(
        "--overrides", default=None, help="JSON overrides for profile parameters"
    )
    p_run.add_argument(
        "--dry-run", action="store_true", help="Print plan without executing"
    )
    p_run.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )
    p_run.add_argument("--output", default=None, help="Output file path")

    # Report command
    p_report = sub.add_parser("report", help="Generate report from store")
    p_report.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_report.add_argument(
        "--run-id", default=None, help="Run ID to report on (latest if omitted)"
    )
    p_report.add_argument(
        "--format",
        choices=["text", "json", "parquet", "html", "latex", "pdf"],
        default="text",
        help="Output format",
    )
    p_report.add_argument("--output", default=None, help="Output file path")
    p_report.add_argument(
        "--axis-coverage",
        action="store_true",
        help="Show per-axis stratification of records (R18 axis-coverage section)",
    )
    p_report.add_argument(
        "--keep-tex",
        action="store_true",
        help="Keep intermediate .tex file when generating PDF",
    )

    # Export command
    p_export = sub.add_parser("export", help="Export store data for round-trip")
    p_export.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_export.add_argument(
        "--run-id", default=None, help="Run ID to export (all if omitted)"
    )
    p_export.add_argument(
        "--format", choices=["json", "parquet"], default="json", help="Export format"
    )
    p_export.add_argument("--output", required=True, help="Output file/directory path")
    p_export.add_argument(
        "--docker",
        action="store_true",
        help="Generate Dockerfile for reproducible environment",
    )

    # Import command
    p_import = sub.add_parser(
        "import", help="Import store data from export (round-trip)"
    )
    p_import.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_import.add_argument("--input", required=True, help="Input JSON export file")
    p_import.add_argument(
        "--dry-run", action="store_true", help="Show plan without executing"
    )
    p_import.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )
    p_import.add_argument("--output", default=None, help="Output file path")

    # Conformance command
    p_conformance = sub.add_parser("conformance", help="Check capability conformance")
    p_conformance.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_conformance.add_argument("--run-id", default=None, help="Run ID to check")
    p_conformance.add_argument(
        "--list-only", action="store_true", help="List capabilities without checking"
    )
    p_conformance.add_argument(
        "--dry-run", action="store_true", help="Show plan without executing"
    )
    p_conformance.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )
    p_conformance.add_argument("--output", default=None, help="Output file path")

    # Status command
    p_status = sub.add_parser("status", help="Show run/store status")
    p_status.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_status.add_argument(
        "--run-id", default=None, help="Run ID to check (all if omitted)"
    )
    p_status.add_argument(
        "--detailed",
        action="store_true",
        help="Show campaign economics: cost per record, projected completion",
    )
    p_status.add_argument(
        "--dry-run", action="store_true", help="Show plan without executing"
    )
    p_status.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )
    p_status.add_argument("--output", default=None, help="Output file path")

    # Gallery command
    p_gallery = sub.add_parser(
        "gallery", help="Render gallery figures from demo records"
    )
    p_gallery.add_argument(
        "--records-dir",
        default="docs/figures/run_records",
        help="Directory containing demo run records",
    )
    p_gallery.add_argument(
        "--output-dir",
        default="docs/figures/gallery",
        help="Output directory for gallery figures",
    )
    p_gallery.add_argument(
        "--dry-run", action="store_true", help="Show plan without executing"
    )
    p_gallery.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )
    p_gallery.add_argument("--output", default=None, help="Output file path")

    # Campaign command
    p_campaign = sub.add_parser(
        "campaign",
        help="Execute declarative multi-run campaigns from YAML (with dependencies, parallelism, webhooks)",
    )
    p_campaign.add_argument(
        "campaign_file",
        help="Path to campaign YAML file",
    )
    p_campaign.add_argument(
        "--store",
        default="experiment.duckdb",
        help="DuckDB store path (overrides campaign file)",
    )
    p_campaign.add_argument(
        "--parallel",
        type=int,
        default=None,
        help="Number of parallel runs (overrides campaign file)",
    )
    p_campaign.add_argument(
        "--device",
        default=None,
        help="Device for all runs: auto, cpu, cuda (overrides campaign file)",
    )
    p_campaign.add_argument(
        "--webhook-url",
        default=None,
        help="Webhook URL for progress notifications (overrides campaign file)",
    )
    p_campaign.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate campaign file and print execution plan without running",
    )
    p_campaign.add_argument(
        "--output",
        default=None,
        help="Output file for campaign results (JSON)",
    )
    p_campaign.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )

    # Loop command — continuous autonomous experiment controller
    p_loop = sub.add_parser(
        "loop",
        help="Continuous autonomous experiment loop: explore→exploit cycles with time budget (replaces scripts/continuous_experiment.py and scripts/run_autonomous.py)",
    )
    p_loop.add_argument(
        "--hours",
        type=float,
        default=8.0,
        help="Total time budget in hours (default: 8)",
    )
    p_loop.add_argument(
        "--cycles",
        type=int,
        default=0,
        help="Stop after N cycles (0 = run until time budget exhausted)",
    )
    p_loop.add_argument(
        "--device",
        choices=["auto", "cpu", "cuda"],
        default="auto",
        help="Device: auto (CUDA if available), cpu, cuda",
    )
    p_loop.add_argument(
        "--store",
        default="experiments/loop/loop.duckdb",
        help="DuckDB store path",
    )
    p_loop.add_argument(
        "--state-dir",
        default="experiments/loop",
        help="Directory for loop state (ledger, defects, report, checkpoints)",
    )
    p_loop.add_argument(
        "--profile",
        default="production-map",
        help="Run profile for individual cycles (default: production-map)",
    )
    p_loop.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Master seed for deterministic seed hierarchy (random if omitted)",
    )
    p_loop.add_argument(
        "--explore-fidelity",
        choices=["L0", "L1"],
        default="L0",
        help="Fidelity for explore cycles (default: L0)",
    )
    p_loop.add_argument(
        "--exploit-fidelity",
        choices=["L1", "L2"],
        default="L1",
        help="Fidelity for exploit cycles (default: L1)",
    )
    p_loop.add_argument(
        "--explore-hours",
        type=float,
        default=0.5,
        help="Hours per explore cycle (default: 0.5)",
    )
    p_loop.add_argument(
        "--exploit-hours",
        type=float,
        default=0.5,
        help="Hours per exploit cycle (default: 0.5)",
    )
    p_loop.add_argument(
        "--explore-sweep-steps",
        type=int,
        default=30,
        help="Sweep steps for explore cycles (default: 30)",
    )
    p_loop.add_argument(
        "--exploit-sweep-steps",
        type=int,
        default=15,
        help="Sweep steps for exploit cycles (default: 15)",
    )
    p_loop.add_argument(
        "--n-seeds",
        type=int,
        default=None,
        help="Number of seeds per cycle (default: profile default or 2)",
    )
    p_loop.add_argument(
        "--dry-run",
        action="store_true",
        help="Show plan without executing",
    )
    p_loop.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )
    # Phase 5: Hypothesis governance
    p_loop.add_argument(
        "--hypothesis-ids",
        default="",
        help="Comma-separated hypothesis IDs to evaluate (e.g., H1_credit_efficiency,H2_dynamics_stability)",
    )
    p_loop.add_argument(
        "--hypothesis-registry",
        default=None,
        help="Path to hypothesis registry JSON (default: state-dir/hypotheses.json)",
    )
    # Phase 5: Guided search
    p_loop.add_argument(
        "--use-icu-guided",
        action="store_true",
        help="Enable I(C,U) guided search by ingesting measurements into ICU model",
    )

    # Baseline command — online baseline discovery and registry
    p_baseline = sub.add_parser(
        "baseline",
        help="Online baseline discovery: run standard optimizers on current hardware for comparison",
    )
    p_baseline_sub = p_baseline.add_subparsers(dest="baseline_command", required=True)

    p_baseline_run = p_baseline_sub.add_parser(
        "run",
        help="Run baseline discovery for a task on current hardware",
    )
    p_baseline_run.add_argument(
        "--task", required=True, help="Task name (e.g., digits, cifar10, wikitext2)"
    )
    p_baseline_run.add_argument(
        "--budget-seconds",
        type=float,
        default=3600.0,
        help="Budget per baseline in seconds",
    )
    p_baseline_run.add_argument(
        "--seeds", type=int, default=3, help="Number of seeds per baseline"
    )
    p_baseline_run.add_argument(
        "--store",
        default="experiments/baseline/baseline.duckdb",
        help="DuckDB store path",
    )
    p_baseline_run.add_argument(
        "--seed", type=int, default=None, help="Master seed for deterministic runs"
    )
    p_baseline_run.add_argument(
        "--optimizer",
        default=None,
        help="Specific optimizer to run (default: all applicable)",
    )
    p_baseline_run.add_argument(
        "--dry-run", action="store_true", help="Show plan without executing"
    )
    p_baseline_run.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )

    p_baseline_list = p_baseline_sub.add_parser(
        "list",
        help="List available baseline configurations",
    )
    p_baseline_list.add_argument("--task", default=None, help="Filter by task")
    p_baseline_list.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )

    p_baseline_check = p_baseline_sub.add_parser(
        "check",
        help="Check if baseline exists for task/hardware/budget/seeds",
    )
    p_baseline_check.add_argument("--task", required=True, help="Task name")
    p_baseline_check.add_argument(
        "--budget-seconds", type=float, default=3600.0, help="Budget in seconds"
    )
    p_baseline_check.add_argument(
        "--seeds", type=int, default=3, help="Number of seeds"
    )
    p_baseline_check.add_argument(
        "--store", default="experiments/baseline/baseline.duckdb", help="Store path"
    )
    p_baseline_check.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )

    # Coverage command — cross-domain coverage report
    p_coverage = sub.add_parser(
        "coverage",
        help="Cross-domain coverage report: shows task×primitive matrix and gaps",
    )
    p_coverage_sub = p_coverage.add_subparsers(dest="coverage_command", required=True)

    p_coverage_report = p_coverage_sub.add_parser(
        "report",
        help="Generate coverage report showing all domains and gaps",
    )
    p_coverage_report.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_coverage_report.add_argument(
        "--run-id", default=None, help="Specific run ID (latest if omitted)"
    )
    p_coverage_report.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )

    p_coverage_tasks = p_coverage_sub.add_parser(
        "tasks",
        help="List all tasks with their domains, cost classes, and objectives",
    )
    p_coverage_tasks.add_argument(
        "--domain",
        default=None,
        help="Filter by domain (vision, language, rl, graph, tabular, memory)",
    )
    p_coverage_tasks.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )

    p_coverage_unmeasured = p_coverage_sub.add_parser(
        "unmeasured",
        help="Show objectives that are registered but not yet measured per task",
    )
    p_coverage_unmeasured.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )

    # Defect command — failure constraint registry (TODO63 Phase 3)
    p_defect = sub.add_parser(
        "defect",
        help="Defect constraint registry: list, cluster, and revoke defect-derived constraints",
    )
    p_defect_sub = p_defect.add_subparsers(dest="defect_command", required=True)

    p_defect_list = p_defect_sub.add_parser(
        "list",
        help="List active defect constraints",
    )
    p_defect_list.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_defect_list.add_argument(
        "--state-dir", default="experiments/loop", help="Loop state directory"
    )
    p_defect_list.add_argument(
        "--include-revoked", action="store_true", help="Include revoked constraints"
    )
    p_defect_list.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )
    p_defect_list.add_argument("--output", default=None, help="Output file path")

    p_defect_cluster = p_defect_sub.add_parser(
        "cluster",
        help="Cluster failures and show patterns (uses evidence/failure.py)",
    )
    p_defect_cluster.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_defect_cluster.add_argument(
        "--run-id", default=None, help="Run ID to analyze (latest if omitted)"
    )
    p_defect_cluster.add_argument(
        "--min-cluster-size", type=int, default=2, help="Minimum cluster size"
    )
    p_defect_cluster.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )
    p_defect_cluster.add_argument("--output", default=None, help="Output file path")

    p_defect_revoke = p_defect_sub.add_parser(
        "revoke",
        help="Revoke a defect constraint by ID",
    )
    p_defect_revoke.add_argument("constraint_id", help="Constraint ID to revoke")
    p_defect_revoke.add_argument(
        "--state-dir", default="experiments/loop", help="Loop state directory"
    )
    p_defect_revoke.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )

    # Hypothesis campaign command
    p_hypothesis = sub.add_parser(
        "hypothesis-campaign",
        help="Run hypothesis templates over campaign records (population-level assertions)",
    )
    p_hypothesis.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_hypothesis.add_argument(
        "--run-id", default=None, help="Run ID to evaluate (latest if omitted)"
    )
    p_hypothesis.add_argument(
        "--templates", required=True, help="JSON file with hypothesis templates"
    )
    p_hypothesis.add_argument(
        "--output", default=None, help="Output file for results (JSON)"
    )
    p_hypothesis.add_argument(
        "--format", choices=["json", "text"], default="json", help="Output format"
    )
    p_hypothesis.add_argument(
        "--dry-run", action="store_true", help="Show plan without executing"
    )
    p_hypothesis.add_argument(
        "--bind",
        action="append",
        default=[],
        help="Parameter bindings for templates (format: template_name:param=value)",
    )

    # Stability-plasticity campaign command
    p_sta = sub.add_parser(
        "stability-plasticity",
        help="Generate and run stability-plasticity frontier campaign",
    )
    p_sta.add_argument("--store", default="sta.duckdb", help="DuckDB store path")
    p_sta.add_argument(
        "--output-spec", default=None, help="Output path for generated RunSpec (JSON)"
    )
    p_sta.add_argument(
        "--rho",
        default="0.5,0.9,1.05",
        help="Rho (contraction) values (comma-separated)",
    )
    p_sta.add_argument(
        "--feedback-scale",
        default="0.1,0.5,1.0",
        help="Feedback scale (coupling) values (comma-separated)",
    )
    p_sta.add_argument(
        "--precision",
        default="float32,float16,bfloat16",
        help="Precision levels (comma-separated)",
    )
    p_sta.add_argument(
        "--noise-level",
        default="0.0,0.01,0.1",
        help="Noise level values (comma-separated)",
    )
    p_sta.add_argument(
        "--convergence-start",
        default="1,5,10",
        help="Convergence start (delay proxy) values (comma-separated)",
    )
    p_sta.add_argument("--seeds", type=int, default=3, help="Seeds per coordinate")
    p_sta.add_argument(
        "--epochs", type=int, default=3, help="Epochs per run (L1 fidelity)"
    )
    p_sta.add_argument(
        "--budget-seconds", type=float, default=3600.0, help="Budget in seconds"
    )
    p_sta.add_argument(
        "--run", action="store_true", help="Run the campaign after generating spec"
    )
    p_sta.add_argument(
        "--dry-run", action="store_true", help="Show plan without running"
    )
    p_sta.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )
    p_sta.add_argument("--output", default=None, help="Output file path")
    p_sta.add_argument(
        "--run-id",
        default=None,
        help="Resume an existing run instead of starting a new one",
    )
    # Axis selection overrides (optional; defaults to stability-plasticity subset)
    p_sta.add_argument(
        "--axis-substrate",
        default=None,
        help="Substrate primitives (comma-separated; default: digital)",
    )
    p_sta.add_argument(
        "--axis-geometry",
        default=None,
        help="Geometry primitives (comma-separated; default: recurrent)",
    )
    p_sta.add_argument(
        "--axis-dynamics",
        default=None,
        help="Dynamics primitives (comma-separated; default: energy_minimization)",
    )
    p_sta.add_argument(
        "--axis-plasticity",
        default=None,
        help="Plasticity primitives (comma-separated; default: null)",
    )
    p_sta.add_argument(
        "--axis-credit",
        default=None,
        help="Credit primitives (comma-separated; default: thermodynamic_contrast)",
    )
    p_sta.add_argument(
        "--axis-update",
        default=None,
        help="Update primitives (comma-separated; default: euclidean)",
    )

    # Frozen-θ ψ benchmark command
    p_frozen = sub.add_parser(
        "frozen-theta-psi",
        help="Run frozen-θ ψ benchmarks at scale (multi-substrate, multi-plasticity)",
    )
    p_frozen.add_argument(
        "--store", default="frozen_psi.duckdb", help="DuckDB store path"
    )
    p_frozen.add_argument(
        "--output-dir",
        default="benchmark_results/frozen_theta_psi",
        help="Output directory for results",
    )
    p_frozen.add_argument(
        "--substrates",
        default="digital,memristive,neuromorphic,photonic,complex,analog,quantum",
        help="Substrates to test (comma-separated)",
    )
    p_frozen.add_argument(
        "--plasticity-types",
        default="null,routing,fast_weights,substrate_coupled",
        help="Plasticity types to test (comma-separated)",
    )
    p_frozen.add_argument(
        "--geometry",
        default="recurrent",
        help="Geometry primitive",
    )
    p_frozen.add_argument(
        "--dynamics",
        default="energy_minimization",
        help="Dynamics primitive",
    )
    p_frozen.add_argument(
        "--credit",
        default="thermodynamic_contrast",
        help="Credit primitive",
    )
    p_frozen.add_argument(
        "--update",
        default="euclidean",
        help="Update primitive",
    )
    p_frozen.add_argument(
        "--epochs", type=int, default=10, help="Pre-training epochs (L2 fidelity)"
    )
    p_frozen.add_argument(
        "--recovery-steps", type=int, default=20, help="Recovery training steps"
    )
    p_frozen.add_argument(
        "--damage-severity", type=float, default=0.3, help="Damage severity (0-1)"
    )
    p_frozen.add_argument("--seeds", type=int, default=3, help="Number of seeds")
    p_frozen.add_argument("--device", default="auto", help="Device (auto, cpu, cuda)")
    p_frozen.add_argument("--run", action="store_true", help="Run the benchmark")
    p_frozen.add_argument(
        "--dry-run", action="store_true", help="Show plan without running"
    )
    p_frozen.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )
    p_frozen.add_argument("--output", default=None, help="Output file path")

    # Stats command - machine-readable summary statistics
    p_stats = sub.add_parser(
        "stats", help="Compute summary statistics for run metrics (machine-readable)"
    )
    p_stats.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_stats.add_argument(
        "--run-id", default=None, help="Run ID to analyze (latest if omitted)"
    )
    p_stats.add_argument(
        "--metrics",
        default="val_acc,walltime_s,flops,param_count,memory_usage,energy_per_step",
        help="Comma-separated metrics to compute statistics for",
    )
    p_stats.add_argument(
        "--agg",
        default="mean,std,min,max,median,ci95",
        help="Comma-separated aggregations: mean,std,min,max,median,ci95,count",
    )
    p_stats.add_argument(
        "--group-by",
        default=None,
        help="Comma-separated axes to group by (e.g., credit,update,substrate)",
    )
    p_stats.add_argument(
        "--format",
        choices=["json", "csv", "table"],
        default="json",
        help="Output format",
    )
    p_stats.add_argument("--output", default=None, help="Output file path")

    # Pareto command - frontier export
    p_pareto = sub.add_parser(
        "pareto", help="Export Pareto frontier points for plotting (machine-readable)"
    )
    p_pareto.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_pareto.add_argument(
        "--run-id", default=None, help="Run ID to analyze (latest if omitted)"
    )
    p_pareto.add_argument(
        "--objectives",
        default="val_acc,energy_per_step",
        help="Comma-separated objectives for frontier (2+ objectives)",
    )
    p_pareto.add_argument(
        "--maximize",
        default=None,
        help="Comma-separated maximize flags (true/false per objective, auto-detected if omitted)",
    )
    p_pareto.add_argument(
        "--weights",
        default=None,
        help="Comma-separated weights for weighted scalarization (enables single-objective ranking)",
    )
    p_pareto.add_argument(
        "--scalarize",
        action="store_true",
        help="Compute weighted scalarization scores and rank all records (requires --weights)",
    )
    p_pareto.add_argument(
        "--format", choices=["json", "csv"], default="csv", help="Output format"
    )
    p_pareto.add_argument("--output", required=True, help="Output file path")

    # Diff command - run comparison
    p_diff = sub.add_parser(
        "diff", help="Compare two runs statistically (machine-readable)"
    )
    p_diff.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_diff.add_argument("--run-id-a", required=True, help="First run ID")
    p_diff.add_argument("--run-id-b", required=True, help="Second run ID")
    p_diff.add_argument(
        "--metrics",
        default="val_acc,walltime_s,flops,param_count",
        help="Comma-separated metrics to compare",
    )
    p_diff.add_argument(
        "--test",
        choices=["ttest", "wilcoxon", "mannwhitney"],
        default="mannwhitney",
        help="Statistical test",
    )
    p_diff.add_argument(
        "--format", choices=["json", "table"], default="json", help="Output format"
    )
    p_diff.add_argument("--output", default=None, help="Output file path")

    # Repro command - reproducibility gate
    p_repro = sub.add_parser(
        "repro", help="Replay a run and verify bitwise reproducibility (CI gate)"
    )
    p_repro.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_repro.add_argument("--run-id", required=True, help="Run ID to reproduce")
    p_repro.add_argument(
        "--tolerance",
        type=float,
        default=1e-6,
        help="Numerical tolerance for bitwise match",
    )
    p_repro.add_argument(
        "--metrics",
        default=None,
        help="Comma-separated metrics to verify (all measured if omitted)",
    )
    p_repro.add_argument(
        "--seeds", type=int, default=None, help="Override seed count for repro run"
    )
    p_repro.add_argument(
        "--device", default="auto", help="Device for repro run (auto, cpu, cuda)"
    )
    p_repro.add_argument(
        "--format", choices=["json", "text"], default="json", help="Output format"
    )
    p_repro.add_argument("--output", default=None, help="Output file path")
    p_repro.add_argument(
        "--docker", action="store_true", help="Run reproduction in Docker container"
    )

    # Power analysis command - experiment design helper
    p_power = sub.add_parser(
        "power-analysis",
        help="Compute statistical power for experiment design (machine-readable)",
    )
    p_power.add_argument(
        "--effect-size",
        type=float,
        required=True,
        help="Expected effect size (Cohen's d)",
    )
    p_power.add_argument(
        "--n-per-group",
        type=int,
        default=None,
        help="Sample size per group (required when --solve-for power)",
    )
    p_power.add_argument(
        "--alpha", type=float, default=0.05, help="Significance level (default 0.05)"
    )
    p_power.add_argument(
        "--target-power",
        type=float,
        default=0.8,
        help="Target power for sample size calculation",
    )
    p_power.add_argument(
        "--solve-for",
        choices=["power", "n"],
        default="power",
        help="What to solve for: 'power' (given n) or 'n' (given target power)",
    )
    p_power.add_argument(
        "--format", choices=["json", "text"], default="json", help="Output format"
    )
    p_power.add_argument("--output", default=None, help="Output file path")

    # Stability analysis command - dynamical systems analysis
    p_stability = sub.add_parser(
        "stability-analysis",
        help="Run dynamical stability analysis (Lyapunov spectra, basin stability, settling trajectories)",
    )
    p_stability.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_stability.add_argument(
        "--run-id", default=None, help="Run ID to analyze (latest if omitted)"
    )
    p_stability.add_argument(
        "--record-id",
        default=None,
        help="Specific record ID to analyze (overrides run-id)",
    )
    p_stability.add_argument(
        "--lyapunov",
        action="store_true",
        help="Compute Lyapunov spectrum over trajectory",
    )
    p_stability.add_argument(
        "--lyapunov-vectors",
        type=int,
        default=5,
        help="Number of Lyapunov vectors to compute (default: 5)",
    )
    p_stability.add_argument(
        "--lyapunov-steps",
        type=int,
        default=100,
        help="Number of steps for Lyapunov estimation (default: 100)",
    )
    p_stability.add_argument(
        "--basin",
        action="store_true",
        help="Compute basin stability via Monte Carlo",
    )
    p_stability.add_argument(
        "--basin-samples",
        type=int,
        default=100,
        help="Number of perturbation samples for basin stability (default: 100)",
    )
    p_stability.add_argument(
        "--basin-radii",
        default="0.1,0.5,1.0,2.0,5.0",
        help="Comma-separated perturbation radii for basin profile (default: 0.1,0.5,1.0,2.0,5.0)",
    )
    p_stability.add_argument(
        "--basin-steps",
        type=int,
        default=200,
        help="Max steps per basin sample (default: 200)",
    )
    p_stability.add_argument(
        "--settling",
        action="store_true",
        help="Compute settling time trajectory with norms history",
    )
    p_stability.add_argument(
        "--settling-steps",
        type=int,
        default=1000,
        help="Max settling steps (default: 1000)",
    )
    p_stability.add_argument(
        "--settling-tolerance",
        type=float,
        default=1e-4,
        help="Settling convergence tolerance (default: 1e-4)",
    )
    p_stability.add_argument(
        "--device",
        default="auto",
        choices=["auto", "cpu", "cuda"],
        help="Device to run analysis on (default: auto)",
    )
    p_stability.add_argument(
        "--format", choices=["json", "text"], default="json", help="Output format"
    )
    p_stability.add_argument("--output", default=None, help="Output file path")
    p_stability.add_argument(
        "--dry-run", action="store_true", help="Show plan without executing"
    )

    # Schema command - dump JSON schemas for RunSpec, Coordinate, Schedule, Objectives
    p_schema = sub.add_parser(
        "schema", help="Dump JSON schemas for experiment models (agent-friendly)"
    )
    p_schema.add_argument(
        "--model",
        choices=["runspec", "coordinate", "schedule", "objectives", "all"],
        default="all",
        help="Which schema to dump",
    )
    p_schema.add_argument(
        "--output", default=None, help="Output file path (stdout if omitted)"
    )
    p_schema.add_argument(
        "--format", choices=["json", "yaml"], default="json", help="Output format"
    )

    # Advanced analysis commands (Phase D)
    # Energy landscape analysis
    p_energy = sub.add_parser(
        "energy-landscape",
        help="Compute 2D energy landscape via PCA of activation space (Phase D1)",
    )
    p_energy.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_energy.add_argument(
        "--run-id", default=None, help="Run ID to analyze (latest if omitted)"
    )
    p_energy.add_argument(
        "--record-id", default=None, help="Specific record ID to analyze"
    )
    p_energy.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    p_energy.add_argument(
        "--grid-resolution", type=int, default=30, help="Grid resolution"
    )
    p_energy.add_argument(
        "--grid-range", type=float, default=3.0, help="Grid range around attractor"
    )
    p_energy.add_argument(
        "--num-trajectories",
        type=int,
        default=20,
        help="Number of trajectories for PCA",
    )
    p_energy.add_argument(
        "--trajectory-length", type=int, default=50, help="Steps per trajectory"
    )
    p_energy.add_argument("--output", default=None, help="Output file path")
    p_energy.add_argument(
        "--format", choices=["json", "text"], default="json", help="Output format"
    )
    p_energy.add_argument(
        "--dry-run", action="store_true", help="Show plan without executing"
    )

    # Nonnormality analysis
    p_nonnormal = sub.add_parser(
        "nonnormality",
        help="Compute pseudospectra and transient amplification bounds (Phase D1)",
    )
    p_nonnormal.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_nonnormal.add_argument(
        "--run-id", default=None, help="Run ID to analyze (latest if omitted)"
    )
    p_nonnormal.add_argument(
        "--record-id", default=None, help="Specific record ID to analyze"
    )
    p_nonnormal.add_argument(
        "--device", default="auto", choices=["auto", "cpu", "cuda"]
    )
    p_nonnormal.add_argument(
        "--max-time", type=int, default=100, help="Max time for transient bounds"
    )
    p_nonnormal.add_argument("--output", default=None, help="Output file path")
    p_nonnormal.add_argument(
        "--format", choices=["json", "text"], default="json", help="Output format"
    )
    p_nonnormal.add_argument(
        "--dry-run", action="store_true", help="Show plan without executing"
    )

    # Axis attribution analysis
    p_attribution = sub.add_parser(
        "axis-attribution",
        help="Compute SHAP/ICE attribution for ontology axes on objectives (Phase D2)",
    )
    p_attribution.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_attribution.add_argument(
        "--run-id", default=None, help="Run ID to analyze (latest if omitted)"
    )
    p_attribution.add_argument(
        "--metric", default="val_acc", help="Metric to attribute"
    )
    p_attribution.add_argument(
        "--axes", default=None, help="Comma-separated axes to analyze"
    )
    p_attribution.add_argument("--output", default=None, help="Output file path")
    p_attribution.add_argument(
        "--format", choices=["json", "text"], default="json", help="Output format"
    )
    p_attribution.add_argument(
        "--dry-run", action="store_true", help="Show plan without executing"
    )

    # Counterfactual analysis
    p_counterfactual = sub.add_parser(
        "counterfactual",
        help="Compute counterfactual trajectories: what if axis was different? (Phase D2)",
    )
    p_counterfactual.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_counterfactual.add_argument(
        "--run-id", default=None, help="Run ID to analyze (latest if omitted)"
    )
    p_counterfactual.add_argument(
        "--metric", default="val_acc", help="Metric to analyze"
    )
    p_counterfactual.add_argument(
        "--axes", default=None, help="Comma-separated axes to swap"
    )
    p_counterfactual.add_argument(
        "--n-targets",
        type=int,
        default=10,
        help="Number of target records (top performers)",
    )
    p_counterfactual.add_argument("--output", default=None, help="Output file path")
    p_counterfactual.add_argument(
        "--format", choices=["json", "text"], default="json", help="Output format"
    )
    p_counterfactual.add_argument(
        "--dry-run", action="store_true", help="Show plan without executing"
    )

    # Mediation analysis
    p_mediation = sub.add_parser(
        "mediation",
        help="Test if stability mediates credit->accuracy relationship (Phase D2)",
    )
    p_mediation.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_mediation.add_argument(
        "--run-id", default=None, help="Run ID to analyze (latest if omitted)"
    )
    p_mediation.add_argument(
        "--independent", default="credit", help="Independent variable axis"
    )
    p_mediation.add_argument(
        "--mediator", default="stability_margin", help="Mediator variable (payload key)"
    )
    p_mediation.add_argument(
        "--dependent", default="val_acc", help="Dependent variable (payload key)"
    )
    p_mediation.add_argument(
        "--all-mediators", action="store_true", help="Test all stability mediators"
    )
    p_mediation.add_argument("--output", default=None, help="Output file path")
    p_mediation.add_argument(
        "--format", choices=["json", "text"], default="json", help="Output format"
    )
    p_mediation.add_argument(
        "--dry-run", action="store_true", help="Show plan without executing"
    )

    # Pareto analysis
    p_pareto_adv = sub.add_parser(
        "pareto-advanced",
        help="Advanced Pareto analysis: hypervolume, scalarization sweeps (Phase D4)",
    )
    p_pareto_adv.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_pareto_adv.add_argument(
        "--run-id", default=None, help="Run ID to analyze (latest if omitted)"
    )
    p_pareto_adv.add_argument(
        "--objectives",
        default="val_acc,energy_per_step",
        help="Comma-separated objectives",
    )
    p_pareto_adv.add_argument(
        "--maximize", default="true,false", help="Comma-separated maximize flags"
    )
    p_pareto_adv.add_argument(
        "--n-weights",
        type=int,
        default=20,
        help="Number of weight samples for scalarization",
    )
    p_pareto_adv.add_argument("--output", default=None, help="Output file path")
    p_pareto_adv.add_argument(
        "--format", choices=["json", "text"], default="json", help="Output format"
    )
    p_pareto_adv.add_argument(
        "--dry-run", action="store_true", help="Show plan without executing"
    )

    # Seed variability analysis
    p_seed_var = sub.add_parser(
        "seed-variability",
        help="Analyze variability across seeds: violin plots, ANOVA (Phase D5)",
    )
    p_seed_var.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_seed_var.add_argument(
        "--run-id", default=None, help="Run ID to analyze (latest if omitted)"
    )
    p_seed_var.add_argument("--metric", default="val_acc", help="Metric to analyze")
    p_seed_var.add_argument(
        "--group-by", default=None, help="Axis to group by (e.g., credit, dynamics)"
    )
    p_seed_var.add_argument("--output", default=None, help="Output file path")
    p_seed_var.add_argument(
        "--format", choices=["json", "text"], default="json", help="Output format"
    )
    p_seed_var.add_argument("--plot", action="store_true", help="Generate violin plot")
    p_seed_var.add_argument(
        "--dry-run", action="store_true", help="Show plan without executing"
    )

    # Hardware variance analysis
    p_hw_var = sub.add_parser(
        "hardware-variance",
        help="Compare performance across hardware devices: CPU vs GPU (Phase D5)",
    )
    p_hw_var.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_hw_var.add_argument(
        "--run-ids", required=True, help="Comma-separated run IDs to compare"
    )
    p_hw_var.add_argument("--metric", default="val_acc", help="Metric to compare")
    p_hw_var.add_argument(
        "--device-field", default="device", help="Record field for device"
    )
    p_hw_var.add_argument("--output", default=None, help="Output file path")
    p_hw_var.add_argument(
        "--format", choices=["json", "text"], default="json", help="Output format"
    )
    p_hw_var.add_argument(
        "--dry-run", action="store_true", help="Show plan without executing"
    )

    # Reproducibility verification
    p_repro_adv = sub.add_parser(
        "repro-advanced",
        help="Verify checkpoint replay and bitwise reproducibility (Phase D5)",
    )
    p_repro_adv.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_repro_adv.add_argument("--run-id", required=True, help="Run ID to verify")
    p_repro_adv.add_argument(
        "--tolerance", type=float, default=1e-6, help="Numerical tolerance"
    )
    p_repro_adv.add_argument("--output", default=None, help="Output file path")
    p_repro_adv.add_argument(
        "--format", choices=["json", "text"], default="json", help="Output format"
    )
    p_repro_adv.add_argument(
        "--dry-run", action="store_true", help="Show plan without executing"
    )

    # Dashboard command
    p_dashboard = sub.add_parser(
        "dashboard",
        help="Launch live monitoring web dashboard (Phase E5)",
    )
    p_dashboard.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_dashboard.add_argument("--host", default="0.0.0.0", help="Host to bind to")  # ruff: ignore[hardcoded-bind-all-interfaces]
    p_dashboard.add_argument("--port", type=int, default=8080, help="Port to bind to")
    p_dashboard.add_argument(
        "--no-websockets", action="store_true", help="Disable WebSocket updates"
    )
    p_dashboard.add_argument(
        "--console",
        action="store_true",
        help="Run console-based dashboard instead of web (no browser needed)",
    )
    p_dashboard.add_argument(
        "--update-interval",
        type=float,
        default=2.0,
        help="Update interval in seconds (console mode)",
    )

    # Dataset registry command
    p_dataset = sub.add_parser(
        "dataset",
        help="Dataset registry: versioned datasets with hash-verified splits (Phase E6)",
    )
    dataset_sub = p_dataset.add_subparsers(dest="dataset_command", required=True)

    # dataset register
    p_ds_register = dataset_sub.add_parser(
        "register", help="Register a dataset version"
    )
    p_ds_register.add_argument("dataset_id", help="Dataset identifier")
    p_ds_register.add_argument("version", help="Semantic version (e.g., 1.0.0)")
    p_ds_register.add_argument("path", help="Path to dataset directory")
    p_ds_register.add_argument("--description", default="", help="Dataset description")
    p_ds_register.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_ds_register.add_argument(
        "--data-root", default="data/datasets", help="Data root directory"
    )
    p_ds_register.add_argument("--source-url", help="Source URL for provenance")
    p_ds_register.add_argument("--source-hash", help="Source hash for provenance")
    p_ds_register.add_argument("--tags", help="Comma-separated key=value tags")

    # dataset get
    p_ds_get = dataset_sub.add_parser("get", help="Get dataset version info")
    p_ds_get.add_argument("dataset_id", help="Dataset identifier")
    p_ds_get.add_argument("version", nargs="?", help="Version (latest if omitted)")
    p_ds_get.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_ds_get.add_argument(
        "--data-root", default="data/datasets", help="Data root directory"
    )
    p_ds_get.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )

    # dataset list
    p_ds_list = dataset_sub.add_parser("list", help="List dataset versions")
    p_ds_list.add_argument(
        "dataset_id", nargs="?", help="Dataset identifier (all if omitted)"
    )
    p_ds_list.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_ds_list.add_argument(
        "--data-root", default="data/datasets", help="Data root directory"
    )
    p_ds_list.add_argument("--tag", help="Filter by tag (key=value)")
    p_ds_list.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )

    # dataset verify
    p_ds_verify = dataset_sub.add_parser("verify", help="Verify dataset integrity")
    p_ds_verify.add_argument("dataset_id", help="Dataset identifier")
    p_ds_verify.add_argument("version", help="Version to verify")
    p_ds_verify.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_ds_verify.add_argument(
        "--data-root", default="data/datasets", help="Data root directory"
    )
    p_ds_verify.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )

    # dataset export
    p_ds_export = dataset_sub.add_parser("export", help="Export dataset metadata")
    p_ds_export.add_argument("dataset_id", help="Dataset identifier")
    p_ds_export.add_argument("version", help="Version to export")
    p_ds_export.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_ds_export.add_argument(
        "--data-root", default="data/datasets", help="Data root directory"
    )
    p_ds_export.add_argument(
        "-o", "--output", required=True, help="Output JSON file path"
    )

    # Environment snapshot command
    p_env = sub.add_parser(
        "environment",
        help="Environment snapshots: capture uv lockfiles, container images (Phase E7)",
    )
    env_sub = p_env.add_subparsers(dest="env_command", required=True)

    # environment capture
    p_env_capture = env_sub.add_parser(
        "capture", help="Capture current environment snapshot"
    )
    p_env_capture.add_argument(
        "-o", "--output", required=True, help="Output JSON file path"
    )
    p_env_capture.add_argument(
        "--no-env-vars", action="store_true", help="Exclude environment variables"
    )
    p_env_capture.add_argument("--no-git", action="store_true", help="Exclude git info")
    p_env_capture.add_argument("--container-image", help="Docker image name to include")

    # environment verify
    p_env_verify = env_sub.add_parser(
        "verify", help="Verify environment against snapshot"
    )
    p_env_verify.add_argument("snapshot", help="Snapshot JSON file path")
    p_env_verify.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )

    # environment docker-build
    p_env_docker = env_sub.add_parser(
        "docker-build", help="Build Docker image from Dockerfile"
    )
    p_env_docker.add_argument("dockerfile", help="Path to Dockerfile")
    p_env_docker.add_argument("image_name", help="Name for the built image")
    p_env_docker.add_argument("--tag", default="latest", help="Image tag")
    p_env_docker.add_argument(
        "--build-arg", action="append", help="Build argument (KEY=VALUE)"
    )

    # environment docker-save
    p_env_docker_save = env_sub.add_parser(
        "docker-save", help="Save Docker image to tar archive"
    )
    p_env_docker_save.add_argument("image_name", help="Image name to save")
    p_env_docker_save.add_argument(
        "-o", "--output", required=True, help="Output tar file path"
    )

    # environment docker-load
    p_env_docker_load = env_sub.add_parser(
        "docker-load", help="Load Docker image from tar archive"
    )
    p_env_docker_load.add_argument("input", help="Input tar file path")

    # Quality gates command
    p_quality = sub.add_parser(
        "quality",
        help="Automated quality gates for reports and data (Phase F1)",
    )
    quality_sub = p_quality.add_subparsers(dest="quality_command", required=True)

    # quality check-report
    p_q_report = quality_sub.add_parser("check-report", help="Validate report quality")
    p_q_report.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_q_report.add_argument("--run-id", required=True, help="Run ID to validate")
    p_q_report.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )
    p_q_report.add_argument("-o", "--output", help="Output file path")

    # quality check-store
    p_q_store = quality_sub.add_parser(
        "check-store", help="Validate store data integrity"
    )
    p_q_store.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_q_store.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )
    p_q_store.add_argument("-o", "--output", help="Output file path")

    # quality check-all
    p_q_all = quality_sub.add_parser("check-all", help="Run all quality gates")
    p_q_all.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_q_all.add_argument("--run-id", required=True, help="Run ID to validate")
    p_q_all.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )
    p_q_all.add_argument("-o", "--output", help="Output file path")

    return parser
