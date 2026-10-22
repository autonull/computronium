#!/usr/bin/env python
"""Enhanced Showcase Campaign — Single Time-Boxed Loop with Advanced Reporting.

This is a thin wrapper around the canonical runner (run_experiment.py) that
adds advanced reporting: coverage matrix, Pareto gallery, stability atlas,
failure taxonomy, bias detection, and hypothesis generation.

Usage:
    uv run scripts/showcase.py --hours N --device auto|cpu|cuda \
        --store results/showcase.db [--profile quick|balanced|thorough|deep]
        [--bias-check] [--export-notebook PATH] [--interactive]

Profiles (presets combining strategy + depth):
    quick      → broad_shallow, 1 epoch, 1 seed (max diversity, min depth)
    balanced   → balanced, 5 epochs, 3 seeds (default)
    thorough   → balanced, 10 epochs, 5 seeds (more depth)
    deep       → narrow_deep, 20 epochs, 5 seeds (max depth on core models)
"""

import argparse
import asyncio
import importlib.util
import json
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch

from computronium.experiment.execution.deadline import Deadline

# Optional imports for interactive mode
TEXTUAL_AVAILABLE = importlib.util.find_spec("textual") is not None
FASTAPI_AVAILABLE = importlib.util.find_spec("fastapi") is not None


def _signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print(f"\nReceived signal {signum}, finishing current run...")
    sys.exit(1)


@dataclass(frozen=True, slots=True)
class ShowcaseConfig:
    """Configuration for showcase campaign."""

    time_budget_hours: float
    strategy: str  # "broad_shallow" | "balanced" | "narrow_deep"
    device: str  # "cpu" | "cuda"
    epochs: int
    seeds: int
    # Component selection (ontology axes) - populated from registries at runtime
    substrates: list[str] = None  # type: ignore[assignment]
    geometries: list[str] = None  # type: ignore[assignment]
    dynamics: list[str] = None  # type: ignore[assignment]
    credits: list[str] = None  # type: ignore[assignment]
    updates: list[str] = None  # type: ignore[assignment]
    plasticities: list[str] = None  # type: ignore[assignment]
    tasks: list[str] = None  # type: ignore[assignment]

    def __post_init__(self):
        if self.substrates is None:
            object.__setattr__(self, "substrates", [])
        if self.geometries is None:
            object.__setattr__(self, "geometries", [])
        if self.dynamics is None:
            object.__setattr__(self, "dynamics", [])
        if self.credits is None:
            object.__setattr__(self, "credits", [])
        if self.updates is None:
            object.__setattr__(self, "updates", [])
        if self.plasticities is None:
            object.__setattr__(self, "plasticities", [])
        if self.tasks is None:
            object.__setattr__(self, "tasks", [])


@dataclass(frozen=True, slots=True)
class BiasAuditResult:
    """Result of bias detection audit."""

    policy_comparison: dict[str, dict[str, float]]
    marginal_distributions: dict[str, dict[str, int]]
    subspace_coverage: float
    failure_taxonomy: dict[str, int]
    overrepresented: list[str]
    underrepresented: list[str]


@dataclass(frozen=True, slots=True)
class ShowcaseReportData:
    """All data needed for the showcase report."""

    campaign_name: str
    start_time: float
    end_time: float
    total_budget_hours: float
    device: str
    strategy: str
    profile: str
    tiers_executed: list[str]
    total_cells_evaluated: int
    total_records: int
    axis_coverage: dict[str, dict[str, int]]
    pareto_points: list[dict[str, Any]]
    stability_summary: dict[str, Any]
    failure_taxonomy: dict[str, int]
    bias_audit: BiasAuditResult | None
    hypotheses: list[dict[str, Any]]
    environment_hash: str
    repro_command: str
    export_json_path: str | None
    budget_utilization: float
    termination_reason: str


# Profile presets
PROFILES = {
    "quick": {"strategy": "broad_shallow", "epochs": 1, "seeds": 1},
    "balanced": {"strategy": "balanced", "epochs": 5, "seeds": 3},
    "thorough": {"strategy": "balanced", "epochs": 10, "seeds": 5},
    "deep": {"strategy": "narrow_deep", "epochs": 20, "seeds": 5},
}


async def run_showcase(
    store: str = "results/showcase.db",
    device: str = "auto",
    dry_run: bool = False,
    strategy: str = "balanced",
    hours: float = 1.0,
    profile: str | None = None,
    bias_check: bool = False,
    export_notebook: str | None = None,
    interactive: bool = False,
) -> int:
    """Run the showcase campaign with deadline enforcement and enhanced reporting."""
    from computronium.experiment.execution.adaptive_budget import (
        BudgetStrategy,
        _build_component_sets,
        _discover_components,
    )
    from computronium.experiment.execution.deadline import Deadline

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    # Resolve profile preset
    if profile:
        if profile not in PROFILES:
            print(f"Unknown profile: {profile}. Choose from: {list(PROFILES.keys())}")
            return 1
        profile_config = PROFILES[profile]
        strategy = profile_config["strategy"]
        target_epochs = profile_config["epochs"]
        target_seeds = profile_config["seeds"]
    else:
        target_epochs = None
        target_seeds = None

    # Resolve device
    if device == "auto":
        resolved_device = "cuda" if torch.cuda.is_available() else "cpu"
    elif device == "cuda":
        resolved_device = "cuda"
    else:
        resolved_device = "cpu"

    print("=" * 70)
    print("COMPUTRONIUM ENHANCED SHOWCASE CAMPAIGN")
    print("=" * 70)
    print(f"Time budget: {hours}h (hard deadline enforcement)")
    print(f"Profile: {profile or 'custom'}")
    print(f"Strategy: {strategy}")
    print(f"Device: {device} ({resolved_device})")
    print(f"Store: {store}")
    print(f"Dry run: {dry_run}")
    print(f"Bias check: {bias_check}")
    print(f"Export notebook: {export_notebook or 'disabled'}")
    print(f"Interactive: {interactive}")
    print()

    if interactive:
        if not TEXTUAL_AVAILABLE:
            print("Interactive mode requires 'textual'. Install with: uv add textual")
            return 1
        return await _run_interactive_mode(
            store=store,
            device=resolved_device,
            hours=hours,
            strategy=strategy,
            profile=profile,
            bias_check=bias_check,
            export_notebook=export_notebook,
        )

    # Build component sets from registries (no historical cache)
    component_sets = _build_component_sets()
    component_set = component_sets[BudgetStrategy(strategy.lower())]

    # Create showcase config with deadline (no prediction!)
    config = ShowcaseConfig(
        time_budget_hours=hours,
        strategy=strategy,
        device=resolved_device,
        epochs=target_epochs if target_epochs is not None else 5,
        seeds=target_seeds if target_seeds is not None else 3,
        substrates=component_set.substrates,
        geometries=component_set.geometries,
        dynamics=component_set.dynamics,
        credits=component_set.credits,
        updates=component_set.updates,
        plasticities=component_set.plasticities,
        tasks=component_set.tasks,
    )

    # Create hard deadline - USE FULL DEADLINE, NO 0.8 FACTOR
    deadline = Deadline.from_hours(hours)
    print(f"Hard deadline: {deadline.remaining_soft_seconds() / 3600:.2f}h from now")
    print(f"Strategy: {config.strategy}")
    print(f"Epochs: {config.epochs}, Seeds: {config.seeds}")
    print(f"Substrates ({len(config.substrates)}): {', '.join(config.substrates)}")
    print(f"Geometries ({len(config.geometries)}): {', '.join(config.geometries)}")
    print(f"Credits ({len(config.credits)}): {', '.join(config.credits)}")
    print(f"Dynamics ({len(config.dynamics)}): {', '.join(config.dynamics)}")
    print(f"Updates ({len(config.updates)}): {', '.join(config.updates)}")
    print(
        f"Plasticities ({len(config.plasticities)}): {', '.join(config.plasticities)}"
    )
    print(
        f"Tasks ({len(config.tasks)}): {', '.join(config.tasks[:10])}{'...' if len(config.tasks) > 10 else ''}"
    )
    print()

    # Generate campaign YAML using deadline (no prediction, no 0.8 factor)
    campaign_file = f"campaign_showcase_{config.strategy}_{hours}h.yaml"
    yaml_path = _create_deadline_campaign_yaml(config, deadline, Path(campaign_file))
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
            "command": "showcase",
            "campaign": config.strategy,
            "profile": profile,
            "store": actual_store,
            "parallel": 1,
            "device": resolved_device,
            "hours": hours,
            "bias_check": bias_check,
            "export_notebook": export_notebook,
            "deadline_ts": deadline.deadline_ts,
            "components": {
                "substrates": config.substrates,
                "geometries": config.geometries,
                "dynamics": config.dynamics,
                "credits": config.credits,
                "updates": config.updates,
                "plasticities": config.plasticities,
                "tasks": config.tasks,
            },
        }
        print(json.dumps(plan_dict, indent=2))
        return 0

    # Ensure results directory exists
    Path("results").mkdir(exist_ok=True)
    Path("artifacts").mkdir(exist_ok=True)

    print(f"Starting campaign execution at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    start_time = time.time()

    # SINGLE CAMPAIGN RUN - no tiers, run until deadline
    result = await _run_simple_campaign(
        campaign_file=campaign_file,
        device=resolved_device,
        actual_store=actual_store,
    )

    elapsed = time.time() - start_time
    print(f"\nCampaign completed in {elapsed:.1f}s ({elapsed / 3600:.2f}h)")

    # Post-campaign analysis and reporting
    report_data = await _generate_showcase_report(
        actual_store=actual_store,
        campaign_data=campaign_data,
        config=config,
        result=result,
        start_time=start_time,
        end_time=time.time(),
        device=resolved_device,
        profile=profile,
        bias_check=bias_check,
        export_notebook=export_notebook,
    )

    # Generate HTML report
    report_path = f"{Path(actual_store).with_suffix('')}_showcase_report.html"
    _generate_enhanced_html_report(report_data, report_path)

    # Generate bias audit report if requested
    if bias_check and report_data.bias_audit:
        bias_report_path = f"{Path(actual_store).with_suffix('')}_bias_audit.json"
        with Path(bias_report_path).open("w", encoding="utf-8") as f:
            json.dump(_bias_audit_to_dict(report_data.bias_audit), f, indent=2)
        print(f"Bias audit report written to: {bias_report_path}")

    # Export notebook if requested
    if export_notebook:
        _export_notebook(report_data, export_notebook, actual_store)

    # Print final summary
    _print_final_summary(report_data, report_path, actual_store)

    return 0


def _create_deadline_campaign_yaml(
    config: ShowcaseConfig, deadline: Deadline, output_path: Path
) -> str:
    """Generate campaign YAML using deadline (no prediction, no 0.8 factor)."""
    import yaml

    store_path = f"results/showcase_{config.strategy}_{config.time_budget_hours}h.db"

    # Use FULL deadline for execution (no 0.8 factor)
    deadline_seconds = deadline.remaining_soft_seconds()

    data = {
        "meta": {
            "name": f"showcase_{config.strategy}_{config.time_budget_hours}h",
            "description": f"Showcase: {config.strategy}, {config.time_budget_hours}h deadline, {config.device}",
            "strategy": config.strategy,
            "time_budget_hours": config.time_budget_hours,
            "device": config.device,
        },
        "compute": {
            "device": config.device,
            "max_parallel": 1,
            "max_wall_hours": config.time_budget_hours * 1.1,  # 10% buffer
        },
        "store": store_path,
        "search_space": {
            "base": {
                "hidden_dim": [64, 128, 256],
                "num_layers": [2, 3, 4],
                "lr": [1e-4, 1e-3, 1e-2, "log"],
                "batch_size": [128, 256],
            }
        },
        "constraints": ["estimate(config) <= 500000"],
        "protocols": {
            "default": "end2end",
            "overrides": {
                "fa_mlp": "layerwise",
                "three_factor_hebbian": "layerwise",
            },
        },
        "arms": {
            "adaptive": {
                "input_dim": 784,
                "num_classes": 10,
                "flatten": True,
                "max_params": 500000,
                "substrates": config.substrates,
                "geometries": config.geometries,
                "dynamics": config.dynamics,
                "credits": config.credits,
                "updates": config.updates,
                "plasticities": config.plasticities,
            }
        },
        "tasks": [
            {"name": t, "epochs": config.epochs, "input_dim": 784, "num_classes": 10}
            for t in config.tasks
        ],
        "hpo": {
            "sampler": "nsga2",
            "objectives": ["accuracy", "param_count", "epoch_time_s"],
            "n_trials": 50,
            "n_startup_trials": 10,
            "n_seeds": config.seeds,
        },
        "resources": {
            "max_wall_hours": config.time_budget_hours * 1.1,
            "max_epoch_time_sec": 120,
            "early_stop_patience": 10,
        },
        "output": {
            "db": store_path,
            "artifacts_dir": f"artifacts/showcase_{config.strategy}_{config.time_budget_hours}h",
            "log_level": "INFO",
            "emit_every": 5,
        },
        "reproducibility": {
            "seed": 42,
            "capture_env": True,
            "artifact_hash": True,
        },
        "runs": [
            {
                "name": "main",
                "profile": "production-map",
                "overrides": {
                    "substrates": config.substrates,
                    "geometries": config.geometries,
                    "dynamics": config.dynamics,
                    "credits": config.credits,
                    "updates": config.updates,
                    "plasticities": config.plasticities,
                    "tasks": config.tasks,
                    "hpo": {"n_trials": 50, "n_seeds": config.seeds},
                    "epochs": config.epochs,
                    "budget_seconds": deadline_seconds,
                },
                "depends_on": [],
            }
        ],
    }

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    return str(output_path)


async def _run_simple_campaign(
    campaign_file: str,
    device: str,
    actual_store: str,
) -> dict[str, Any]:
    """Run a simple single-phase campaign."""
    from computronium.experiment.execution.campaign import run_campaign

    result = await run_campaign(
        Path(campaign_file),
        parallel=1,
        device=device,
    )
    return result


async def _run_bias_check(
    config: ShowcaseConfig,
    campaign_file: str,
    actual_store: str,
    device: str,
    hours: float,
) -> BiasAuditResult:
    """Run bias detection by comparing policies (Phase 0.3)."""
    from computronium.experiment.execution.campaign import run_campaign
    from computronium.experiment.execution.deadline import Deadline

    print("\n" + "=" * 70)
    print("BIAS DETECTION: Policy Comparison")
    print("=" * 70)

    policies = ["round_robin_grid", "stratified_random", "model_based"]
    policy_results = {}

    for policy_name in policies:
        print(f"  Running with policy: {policy_name}...")
        # Create a mini-campaign for this policy using deadline-aware approach

        mini_config = ShowcaseConfig(
            time_budget_hours=hours * 0.1,  # 10% of budget for bias check
            strategy=config.strategy,
            device=device,
            epochs=1,
            seeds=1,
            substrates=config.substrates,
            geometries=config.geometries,
            dynamics=config.dynamics,
            credits=config.credits,
            updates=config.updates,
            plasticities=config.plasticities,
            tasks=config.tasks,
        )
        mini_deadline = Deadline.from_hours(hours * 0.1)
        mini_campaign_file = f"campaign_bias_{policy_name}_{hours}h.yaml"
        _create_deadline_campaign_yaml(
            mini_config, mini_deadline, Path(mini_campaign_file)
        )

        # Modify YAML to use specific policy
        import yaml

        with Path(mini_campaign_file).open(encoding="utf-8") as f:
            campaign_yaml = yaml.safe_load(f)
        campaign_yaml["arms"]["adaptive"]["policy"] = policy_name
        with Path(mini_campaign_file).open("w", encoding="utf-8") as f:
            yaml.dump(campaign_yaml, f, default_flow_style=False, sort_keys=False)

        mini_store = f"{Path(actual_store).stem}_{policy_name}.db"
        campaign_yaml["store"] = mini_store
        campaign_yaml["runs"][0]["store"] = mini_store
        with Path(mini_campaign_file).open("w", encoding="utf-8") as f:
            yaml.dump(campaign_yaml, f, default_flow_style=False, sort_keys=False)

        result = await run_campaign(
            Path(mini_campaign_file),
            parallel=1,
            device=device,
        )
        policy_results[policy_name] = result

    # Analyze results for bias
    return _analyze_bias(policy_results, actual_store)


def _analyze_bias(policy_results: dict, reference_store: str) -> BiasAuditResult:
    """Analyze bias across policy runs."""
    from computronium.experiment.evidence.store import RecordStore, StoreConfig
    from computronium.experiment.surface.report import ReportGenerator

    policy_comparison = {}
    marginal_distributions = {}
    failure_taxonomy = {}

    for policy_name, result in policy_results.items():
        # Get the main run
        runs = result.get("run_results", {})
        if not runs:
            continue

        policy_comparison[policy_name] = {
            "completed": result.get("completed", 0),
            "failed": result.get("failed", 0),
            "total_runs": result.get("total_runs", 0),
        }

    # Compute marginal distributions from reference store
    if Path(reference_store).exists():
        store = RecordStore(StoreConfig(Path(reference_store)))
        with store:
            runs = store.query_runs()
            if runs:
                main_run = max(
                    reversed(runs),
                    key=lambda r: len(store.query_records(run_id=r.run_id)),
                )
                generator = ReportGenerator(store)
                axis_cov = generator.axis_coverage(main_run.run_id)
                marginal_distributions = axis_cov

    return BiasAuditResult(
        policy_comparison=policy_comparison,
        marginal_distributions=marginal_distributions,
        subspace_coverage=0.0,  # TODO: compute hypervolume
        failure_taxonomy=failure_taxonomy,
        overrepresented=[],
        underrepresented=[],
    )


def _bias_audit_to_dict(audit: BiasAuditResult) -> dict:
    """Convert BiasAuditResult to dict for JSON serialization."""
    return {
        "policy_comparison": audit.policy_comparison,
        "marginal_distributions": audit.marginal_distributions,
        "subspace_coverage": audit.subspace_coverage,
        "failure_taxonomy": audit.failure_taxonomy,
        "overrepresented": audit.overrepresented,
        "underrepresented": audit.underrepresented,
    }


async def _generate_showcase_report(
    actual_store: str,
    campaign_data: dict,
    config: ShowcaseConfig,
    result: dict,
    start_time: float,
    end_time: float,
    device: str,
    profile: str | None,
    bias_check: bool,
    export_notebook: str | None,
) -> ShowcaseReportData:
    """Generate comprehensive showcase report data."""

    # Get environment hash
    try:
        env_hash = subprocess.check_output(
            ["uv", "lock", "--hash"], text=True, stderr=subprocess.DEVNULL
        ).strip()[:16]
    except Exception:
        env_hash = "unknown"

    # Build repro command
    repro_parts = ["uv run scripts/showcase.py"]
    if profile:
        repro_parts.append(f"--profile {profile}")
    else:
        repro_parts.append(f"--strategy {config.strategy}")
    repro_parts.append(f"--hours {config.time_budget_hours}")
    repro_parts.append(f"--device {device}")
    repro_command = " ".join(repro_parts)

    # Extract data from store
    axis_coverage = {}
    pareto_points = []
    stability_summary = {}
    failure_taxonomy = {}
    bias_audit = None
    hypotheses = []
    export_json_path = None

    if Path(actual_store).exists():
        from computronium.experiment.evidence.store import RecordStore, StoreConfig
        from computronium.experiment.surface.report import ReportGenerator

        store = RecordStore(StoreConfig(Path(actual_store)))
        with store:
            runs = store.query_runs()
            if runs:
                main_run = max(
                    reversed(runs),
                    key=lambda r: len(store.query_records(run_id=r.run_id)),
                )
                generator = ReportGenerator(store)

                # Axis coverage
                axis_coverage = generator.axis_coverage(main_run.run_id)

                # Pareto frontier
                pareto = generator.pareto_frontier(main_run.run_id)
                pareto_points = pareto[:20]  # Top 20

                # Stability summary (if available)
                try:
                    import io
                    import sys

                    from computronium.experiment.surface.cli import main as surface_main

                    # Capture stability analysis output
                    old_stdout = sys.stdout
                    sys.stdout = io.StringIO()
                    try:
                        surface_main([
                            "stability-analysis",
                            "--store",
                            actual_store,
                            "--run-id",
                            main_run.run_id,
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
                            "json",
                        ])
                        stability_output = sys.stdout.getvalue()
                    finally:
                        sys.stdout = old_stdout
                    if stability_output:
                        stability_summary = json.loads(stability_output)
                except Exception:
                    # Stability analysis optional; continue without it
                    pass

                # Failure taxonomy
                failure_taxonomy = generator.failures_by_cause(main_run.run_id)

                # Generate hypotheses from results
                hypotheses = _generate_hypotheses(generator, main_run.run_id)

                # Export JSON for downstream analysis
                export_json_path = f"{Path(actual_store).with_suffix('')}_export.json"
                _export_json_data(store, main_run.run_id, export_json_path)

    # Run bias check if requested
    if bias_check:
        bias_audit = await _run_bias_check(
            config,
            campaign_data.get("meta", {}).get("name", "showcase"),
            actual_store,
            device,
            config.time_budget_hours,
        )

    # Calculate budget utilization
    budget_s = config.time_budget_hours * 3600
    elapsed_s = end_time - start_time
    budget_utilization = elapsed_s / budget_s if budget_s > 0 else 0.0

    # Determine termination reason
    if budget_utilization >= 0.90 and elapsed_s <= budget_s + 30:
        termination_reason = "deadline"
    elif elapsed_s > budget_s + 30:
        termination_reason = "overshoot"
    else:
        termination_reason = "early_stop"

    return ShowcaseReportData(
        campaign_name=campaign_data.get("meta", {}).get("name", "showcase"),
        start_time=start_time,
        end_time=end_time,
        total_budget_hours=config.time_budget_hours,
        device=device,
        strategy=config.strategy,
        profile=profile or "custom",
        tiers_executed=["single_phase"],  # No tiers in new architecture
        total_cells_evaluated=result.get("completed", 0),
        total_records=result.get("completed", 0),
        axis_coverage=axis_coverage,
        pareto_points=pareto_points,
        stability_summary=stability_summary,
        failure_taxonomy=failure_taxonomy,
        bias_audit=bias_audit,
        hypotheses=hypotheses,
        environment_hash=env_hash,
        repro_command=repro_command,
        export_json_path=export_json_path,
        budget_utilization=budget_utilization,
        termination_reason=termination_reason,
    )


def _generate_hypotheses(generator, run_id: str) -> list[dict]:
    """Generate testable hypotheses from showcase data (Phase 0.6)."""
    from computronium.experiment.schema.axis import StructuralAxis

    hypotheses = []
    claims = generator.claims(run_id)

    for claim in claims:
        if claim.axis == StructuralAxis.CREDIT.value:
            hypotheses.append({
                "id": f"H_credit_{claim.value}_vs_{claim.metric}",
                "question": f"Does {claim.value} credit achieve different {claim.metric} than other credits?",
                "prediction": f"{claim.value} has {claim.mean:.3f} {claim.metric}",
                "test": f"paired_t_test({claim.metric}) grouped by credit",
                "min_effect_size": 0.5,
                "required_power": 0.8,
                "tags": ["credit", claim.metric],
                "evidence": claim.render(),
            })
        elif claim.axis == StructuralAxis.DYNAMICS.value:
            hypotheses.append({
                "id": f"H_dynamics_{claim.value}_stability",
                "question": f"How does {claim.value} dynamics affect stability?",
                "prediction": f"{claim.value} shows stability margin {claim.mean:.3f}",
                "test": "lyapunov_exponent comparison across dynamics",
                "min_effect_size": 0.5,
                "required_power": 0.8,
                "tags": ["dynamics", "stability"],
                "evidence": claim.render(),
            })
        elif claim.axis == StructuralAxis.SUBSTRATE.value:
            hypotheses.append({
                "id": f"H_substrate_{claim.value}_efficiency",
                "question": f"Does {claim.value} substrate improve energy efficiency?",
                "prediction": f"{claim.value} achieves {claim.mean:.3f} val_acc",
                "test": "val_acc vs energy_per_step Pareto grouped by substrate",
                "min_effect_size": 0.5,
                "required_power": 0.8,
                "tags": ["substrate", "energy"],
                "evidence": claim.render(),
            })

    # Add cross-axis hypotheses
    if len(claims) >= 2:
        hypotheses.append({
            "id": "H_credit_dynamics_interaction",
            "question": "Do credit assignment and dynamics interact on validation accuracy?",
            "prediction": "Specific credit×dynamics pairs outperform marginal effects",
            "test": "two_way_anova(val_acc ~ credit * dynamics)",
            "min_effect_size": 0.3,
            "required_power": 0.8,
            "tags": ["credit", "dynamics", "interaction"],
            "evidence": "Cross-axis claim analysis needed",
        })

    return hypotheses


def _export_json_data(store, run_id: str, output_path: str):
    """Export run data to JSON for downstream analysis."""
    from computronium.experiment.surface.report import export_to_json

    export_to_json(store, run_id, output_path)


def _generate_enhanced_html_report(
    report_data: ShowcaseReportData, output_path: str
) -> None:
    """Generate enhanced HTML report with all sections."""
    html = _build_enhanced_html(report_data)
    Path(output_path).write_text(html, encoding="utf-8")
    print(f"Enhanced HTML report written to: {output_path}")


def _build_enhanced_html(data: ShowcaseReportData) -> str:
    """Build the complete enhanced HTML report."""
    from datetime import datetime

    duration_hours = (data.end_time - data.start_time) / 3600
    start_str = datetime.fromtimestamp(data.start_time).strftime("%Y-%m-%d %H:%M:%S")
    end_str = datetime.fromtimestamp(data.end_time).strftime("%Y-%m-%d %H:%M:%S")

    # Coverage matrix HTML
    coverage_html = _build_coverage_matrix_html(data.axis_coverage)

    # Pareto gallery HTML
    pareto_html = _build_pareto_gallery_html(data.pareto_points)

    # Stability atlas HTML
    stability_html = _build_stability_atlas_html(data.stability_summary)

    # Failure taxonomy HTML
    failure_html = _build_failure_taxonomy_html(data.failure_taxonomy)

    # Bias audit HTML
    bias_html = ""
    if data.bias_audit:
        bias_html = _build_bias_audit_html(data.bias_audit)

    # Hypotheses HTML
    hypotheses_html = _build_hypotheses_html(data.hypotheses)

    # Budget utilization status
    util_status = "✅ PASS" if data.budget_utilization >= 0.90 else "❌ FAIL"
    term_reason = data.termination_reason

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Computronium Showcase Report: {data.campaign_name}</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 1200px; margin: 0 auto; padding: 20px; background: #fafafa; color: #1a1a2e; }}
        h1 {{ color: #1a1a2e; border-bottom: 3px solid #2563eb; padding-bottom: 10px; }}
        h2 {{ color: #1e40af; margin-top: 40px; border-bottom: 1px solid #d1d5db; padding-bottom: 5px; }}
        h3 {{ color: #374151; }}
        h4 {{ color: #4b5563; }}
        .meta-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .meta-item {{ padding: 10px; }}
        .meta-label {{ font-size: 0.875rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; }}
        .meta-value {{ font-size: 1.125rem; font-weight: 600; color: #1a1a2e; }}
        .section {{ background: white; margin: 20px 0; padding: 25px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .executive-summary {{ background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border-left: 4px solid #2563eb; }}
        .coverage-table {{ width: 100%; border-collapse: collapse; font-size: 0.875rem; }}
        .coverage-table th, .coverage-table td {{ border: 1px solid #e5e7eb; padding: 8px 12px; text-align: left; }}
        .coverage-table th {{ background: #f3f4f6; font-weight: 600; }}
        .coverage-table tr:nth-child(even) {{ background: #f9fafb; }}
        .coverage-cell {{ text-align: center; }}
        .coverage-high {{ background: #dcfce7; }}
        .coverage-medium {{ background: #fef9c3; }}
        .coverage-low {{ background: #fee2e2; }}
        .pareto-table {{ width: 100%; border-collapse: collapse; font-size: 0.875rem; }}
        .pareto-table th, .pareto-table td {{ border: 1px solid #e5e7eb; padding: 8px 12px; }}
        .pareto-table th {{ background: #f3f4f6; }}
        .stability-metric {{ display: inline-block; padding: 8px 16px; margin: 5px; background: #f3f4f6; border-radius: 6px; font-family: monospace; }}
        .failure-row {{ display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid #e5e7eb; }}
        .failure-cause {{ font-weight: 500; }}
        .failure-count {{ color: #ef4444; font-family: monospace; }}
        .hypothesis-card {{ border: 1px solid #e5e7eb; border-radius: 8px; padding: 15px; margin: 10px 0; background: white; }}
        .hypothesis-id {{ font-family: monospace; background: #eef2ff; padding: 2px 8px; border-radius: 4px; font-size: 0.875rem; }}
        .hypothesis-tags {{ margin-top: 8px; }}
        .tag {{ display: inline-block; background: #dbeafe; color: #1e40af; padding: 2px 8px; border-radius: 999px; font-size: 0.75rem; margin-right: 5px; }}
        .repro-block {{ background: #1a1a2e; color: #e5e7eb; padding: 20px; border-radius: 8px; font-family: monospace; font-size: 0.875rem; overflow-x: auto; }}
        .alert {{ padding: 12px; border-radius: 6px; margin: 10px 0; }}
        .alert-warning {{ background: #fef3c7; border: 1px solid #fcd34d; color: #92400e; }}
        .alert-info {{ background: #dbeafe; border: 1px solid #93c5fd; color: #1e40af; }}
        .toc {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .toc ul {{ list-style: none; padding-left: 0; }}
        .toc li {{ margin: 8px 0; }}
        .toc a {{ color: #2563eb; text-decoration: none; }}
        .toc a:hover {{ text-decoration: underline; }}
        .util-badge {{ display: inline-block; padding: 4px 12px; border-radius: 999px; font-weight: 600; font-size: 0.875rem; }}
        .util-pass {{ background: #dcfce7; color: #166534; }}
        .util-fail {{ background: #fee2e2; color: #991b1b; }}
        .term-badge {{ display: inline-block; padding: 4px 12px; border-radius: 999px; font-weight: 600; font-size: 0.875rem; background: #e0e7ff; color: #3730a3; }}
    </style>
</head>
<body>
    <h1>🌌 Computronium Showcase Report</h1>
    <p><strong>Campaign:</strong> {data.campaign_name} | <strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

    <div class="toc">
        <h2>📋 Table of Contents</h2>
        <ul>
            <li><a href="#executive-summary">Executive Summary</a></li>
            <li><a href="#campaign-configuration">Campaign Configuration</a></li>
            <li><a href="#budget-utilization">Budget Utilization</a></li>
            <li><a href="#coverage-matrix">Coverage Matrix</a></li>
            <li><a href="#pareto-gallery">Pareto Gallery</a></li>
            <li><a href="#stability-atlas">Stability Atlas</a></li>
            <li><a href="#failure-taxonomy">Failure Taxonomy</a></li>
            {'<li><a href="#bias-audit">Bias Audit</a></li>' if data.bias_audit else ""}
            <li><a href="#hypotheses">Generated Hypotheses</a></li>
            <li><a href="#reproducibility">Reproducibility</a></li>
        </ul>
    </div>

    <div id="executive-summary" class="section executive-summary">
        <h2>📊 Executive Summary</h2>
        <p>In <strong>{duration_hours:.2f} hours</strong>, we explored <strong>{data.total_cells_evaluated}</strong> valid combinations across <strong>{len(data.axis_coverage)}</strong> ontology axes. The campaign executed a <strong>single phase</strong> (no tiers).</p>
        <p><strong>Key Findings:</strong></p>
        <ul>
            <li>Coverage across {sum(len(v) for v in data.axis_coverage.values())} unique primitives</li>
            <li>{len(data.pareto_points)} Pareto-optimal configurations identified</li>
            <li>{sum(data.failure_taxonomy.values())} failures categorized into {len(data.failure_taxonomy)} types</li>
            <li>{len(data.hypotheses)} testable hypotheses generated for follow-up campaigns</li>
        </ul>
    </div>

    <div id="campaign-configuration" class="section">
        <h2>⚙️ Campaign Configuration</h2>
        <div class="meta-grid">
            <div class="meta-item"><div class="meta-label">Campaign</div><div class="meta-value">{data.campaign_name}</div></div>
            <div class="meta-item"><div class="meta-label">Profile</div><div class="meta-value">{data.profile}</div></div>
            <div class="meta-item"><div class="meta-label">Strategy</div><div class="meta-value">{data.strategy}</div></div>
            <div class="meta-item"><div class="meta-label">Time Budget</div><div class="meta-value">{data.total_budget_hours:.2f}h</div></div>
            <div class="meta-item"><div class="meta-label">Actual Duration</div><div class="meta-value">{duration_hours:.2f}h</div></div>
            <div class="meta-item"><div class="meta-label">Device</div><div class="meta-value">{data.device}</div></div>
            <div class="meta-item"><div class="meta-label">Phases Executed</div><div class="meta-value">{len(data.tiers_executed)}</div></div>
            <div class="meta-item"><div class="meta-label">Cells Evaluated</div><div class="meta-value">{data.total_cells_evaluated}</div></div>
            <div class="meta-item"><div class="meta-label">Total Records</div><div class="meta-value">{data.total_records}</div></div>
            <div class="meta-item"><div class="meta-label">Start Time</div><div class="meta-value">{start_str}</div></div>
            <div class="meta-item"><div class="meta-label">End Time</div><div class="meta-value">{end_str}</div></div>
            <div class="meta-item"><div class="meta-label">Environment Hash</div><div class="meta-value">{data.environment_hash}</div></div>
        </div>
    </div>

    <div id="budget-utilization" class="section">
        <h2>⏱️ Budget Utilization</h2>
        <div class="meta-grid">
            <div class="meta-item"><div class="meta-label">Budget</div><div class="meta-value">{data.total_budget_hours:.2f}h</div></div>
            <div class="meta-item"><div class="meta-label">Elapsed</div><div class="meta-value">{duration_hours:.2f}h</div></div>
            <div class="meta-item"><div class="meta-label">Utilization</div><div class="meta-value">{data.budget_utilization:.1%}</div></div>
            <div class="meta-item"><div class="meta-label">Status</div><div class="meta-value"><span class="util-badge {"util-pass" if data.budget_utilization >= 0.90 else "util-fail"}">{util_status}</span></div></div>
            <div class="meta-item"><div class="meta-label">Termination Reason</div><div class="meta-value"><span class="term-badge">{term_reason}</span></div></div>
        </div>
    </div>

    <div id="coverage-matrix" class="section">
        <h2>📈 Coverage Matrix</h2>
        <p>Heatmap of (axis × primitive) with cell count, success rate, and mean validation accuracy.</p>
        {coverage_html}
    </div>

    <div id="pareto-gallery" class="section">
        <h2>🎯 Pareto Gallery</h2>
        <p>Pareto-optimal configurations across objective pairs. Each point represents a unique (substrate, geometry, dynamics, plasticity, credit, update) combination.</p>
        {pareto_html}
    </div>

    <div id="stability-atlas" class="section">
        <h2>🔬 Stability Atlas</h2>
        <p>Lyapunov, basin, and settling summaries per dynamics family.</p>
        {stability_html}
    </div>

    <div id="failure-taxonomy" class="section">
        <h2>⚠️ Failure Taxonomy</h2>
        <p>Failure modes categorized by axis combination with counts.</p>
        {failure_html}
    </div>

    {bias_html}

    <div id="hypotheses" class="section">
        <h2>💡 Generated Hypotheses</h2>
        <p>Testable hypotheses derived from showcase results, ready for focused follow-up campaigns.</p>
        {hypotheses_html}
    </div>

    <div id="reproducibility" class="section">
        <h2>🔁 Reproducibility</h2>
        <div class="repro-block">{data.repro_command}</div>
        <p><strong>Environment Hash:</strong> <code>{data.environment_hash}</code></p>
        {f'<p><strong>Export JSON:</strong> <a href="{data.export_json_path}">{data.export_json_path}</a></p>' if data.export_json_path else ""}
    </div>

    <footer style="margin-top: 40px; padding: 20px; text-align: center; color: #6b7280; font-size: 0.875rem;">
        Generated by Computronium Enhanced Showcase | {datetime.now().isoformat()}
    </footer>
</body>
</html>"""


def _build_coverage_matrix_html(axis_coverage: dict[str, dict[str, int]]) -> str:
    """Build coverage matrix HTML table."""
    if not axis_coverage:
        return "<p>No coverage data available.</p>"

    html = [
        "<table class='coverage-table'><thead><tr><th>Axis</th><th>Primitives</th><th>Total Cells</th>"
    ]
    # Add column for each primitive
    all_primitives = set()
    for primitives in axis_coverage.values():
        all_primitives.update(primitives.keys())
    for prim in sorted(all_primitives):
        html.append(f"<th class='coverage-cell'>{prim}</th>")
    html.append("</tr></thead><tbody>")

    for axis, primitives in sorted(axis_coverage.items()):
        total = sum(primitives.values())
        html.append(
            f"<tr><td><strong>{axis}</strong></td><td>{len(primitives)}</td><td>{total}</td>"
        )
        for prim in sorted(all_primitives):
            count = primitives.get(prim, 0)
            if count == 0:
                cls = "coverage-low"
            elif count < total * 0.1:
                cls = "coverage-medium"
            else:
                cls = "coverage-high"
            html.append(f"<td class='coverage-cell {cls}'>{count}</td>")
        html.append("</tr>")

    html.append("</tbody></table>")
    return "\n".join(html)


def _build_pareto_gallery_html(pareto_points: list[dict]) -> str:
    """Build Pareto gallery HTML."""
    if not pareto_points:
        return "<p>No Pareto points available.</p>"

    html = ["<table class='pareto-table'><thead><tr>"]
    # Determine columns from first point
    if pareto_points:
        first = pareto_points[0]
        html.append("<th>Rank</th>")
        for key in first.get("objectives", {}):
            html.append(f"<th>{key}</th>")
        for key in first.get("coordinate", {}):
            html.append(f"<th>{key}</th>")
        html.append("</tr></thead><tbody>")

        for i, point in enumerate(pareto_points[:20]):
            html.append(f"<tr><td>{i + 1}</td>")
            for val in point.get("objectives", {}).values():
                html.append(f"<td>{val:.4g}</td>")
            for val in point.get("coordinate", {}).values():
                html.append(f"<td>{val}</td>")
            html.append("</tr>")
    html.append("</tbody></table>")
    return "\n".join(html)


def _build_stability_atlas_html(stability_summary: dict) -> str:
    """Build stability atlas HTML."""
    if not stability_summary:
        return "<div class='alert alert-info'>Stability analysis not available. Run with --bias-check or ensure stability metrics are collected.</div>"

    html = ["<div>"]
    for key, value in stability_summary.items():
        if isinstance(value, dict):
            html.append(f"<h4>{key}</h4>")
            for k, v in value.items():
                html.append(f"<span class='stability-metric'>{k}: {v}</span>")
        else:
            html.append(f"<span class='stability-metric'>{key}: {value}</span>")
    html.append("</div>")
    return "\n".join(html)


def _build_failure_taxonomy_html(failure_taxonomy: dict[str, int]) -> str:
    """Build failure taxonomy HTML."""
    if not failure_taxonomy:
        return "<div class='alert alert-info'>No failures recorded.</div>"

    html = ["<div>"]
    for cause, count in sorted(failure_taxonomy.items(), key=lambda x: -x[1]):
        html.append(
            f"<div class='failure-row'><span class='failure-cause'>{cause}</span><span class='failure-count'>{count}</span></div>"
        )
    html.append("</div>")
    return "\n".join(html)


def _build_bias_audit_html(audit: BiasAuditResult) -> str:
    """Build bias audit HTML section."""
    html = [
        "<div id='bias-audit' class='section'>",
        "<h2>⚖️ Bias Audit</h2>",
        "<p>Comparison of sampling policies to detect implicit bias in component selection.</p>",
        "<h3>Policy Comparison</h3>",
        "<table class='pareto-table'><thead><tr><th>Policy</th><th>Completed</th><th>Failed</th><th>Total Runs</th></tr></thead><tbody>",
    ]
    for policy, metrics in audit.policy_comparison.items():
        html.append(
            f"<tr><td>{policy}</td><td>{metrics.get('completed', 0)}</td><td>{metrics.get('failed', 0)}</td><td>{metrics.get('total_runs', 0)}</td></tr>"
        )
    html.append("</tbody></table>")

    html.append("<h3>Marginal Distributions</h3>")
    for axis, dist in audit.marginal_distributions.items():
        html.append(f"<h4>{axis}</h4>")
        html.append("<ul>")
        for prim, count in sorted(dist.items(), key=lambda x: -x[1]):
            html.append(f"<li>{prim}: {count}</li>")
        html.append("</ul>")

    if audit.overrepresented:
        html.append("<h3>Over-represented</h3><ul>")
        for item in audit.overrepresented:
            html.append(f"<li>{item}</li>")
        html.append("</ul>")

    if audit.underrepresented:
        html.append("<h3>Under-represented</h3><ul>")
        for item in audit.underrepresented:
            html.append(f"<li>{item}</li>")
        html.append("</ul>")

    html.append(
        f"<p><strong>Subspace Coverage:</strong> {audit.subspace_coverage:.2%}</p>"
    )
    html.append("</div>")
    return "\n".join(html)


def _build_hypotheses_html(hypotheses: list[dict]) -> str:
    """Build hypotheses HTML."""
    if not hypotheses:
        return "<div class='alert alert-info'>No hypotheses generated. Run with more data.</div>"

    html = []
    for h in hypotheses:
        html.append(f"""
        <div class='hypothesis-card'>
            <div class='hypothesis-id'>{h["id"]}</div>
            <p><strong>Question:</strong> {h["question"]}</p>
            <p><strong>Prediction:</strong> {h["prediction"]}</p>
            <p><strong>Test:</strong> <code>{h["test"]}</code></p>
            <p><strong>Min Effect Size:</strong> {h["min_effect_size"]} | <strong>Required Power:</strong> {h["required_power"]}</p>
            <div class='hypothesis-tags'>
                {"".join(f'<span class="tag">{tag}</span>' for tag in h.get("tags", []))}
            </div>
        </div>
        """)
    return "\n".join(html)


def _print_final_summary(
    report_data: ShowcaseReportData, report_path: str, store_path: str
):
    """Print final summary to console."""
    duration_hours = (report_data.end_time - report_data.start_time) / 3600

    print("\n" + "=" * 70)
    print("SHOWCASE CAMPAIGN COMPLETE")
    print("=" * 70)
    print(f"Campaign: {report_data.campaign_name}")
    print(
        f"Duration: {duration_hours:.2f}h (budget: {report_data.total_budget_hours:.2f}h)"
    )
    print(
        f"Utilization: {report_data.budget_utilization:.1%} {'✅' if report_data.budget_utilization >= 0.90 else '❌'}"
    )
    print(f"Termination: {report_data.termination_reason}")
    print(f"Cells evaluated: {report_data.total_cells_evaluated}")
    print(f"Pareto points: {len(report_data.pareto_points)}")
    print(f"Failure types: {len(report_data.failure_taxonomy)}")
    print(f"Hypotheses generated: {len(report_data.hypotheses)}")
    print(f"Report: {report_path}")
    print(f"Store: {store_path}")
    print("=" * 70)


async def _run_interactive_mode(
    store: str,
    device: str,
    hours: float,
    strategy: str,
    profile: str | None,
    bias_check: bool,
    export_notebook: str | None,
) -> int:
    """Run interactive TUI mode."""
    print("Interactive mode not yet implemented for single-loop architecture.")
    print("Run without --interactive for standard execution.")
    return 1


def _export_notebook(
    report_data: ShowcaseReportData, output_path: str, store_path: str
) -> None:
    """Export Jupyter notebook with all results and analysis cells (Phase 0.8)."""
    notebook = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.11"},
        },
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Computronium Showcase Analysis\n",
                    "\n",
                    f"**Campaign:** {report_data.campaign_name}\n",
                    f"**Profile:** {report_data.profile}\n",
                    f"**Duration:** {(report_data.end_time - report_data.start_time) / 3600:.2f}h\n",
                    f"**Device:** {report_data.device}\n",
                    f"**Store:** {store_path}\n",
                    "\n",
                    "This notebook was auto-generated from the showcase campaign. "
                    "Run cells to explore results interactively.",
                ],
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": [
                    "import json\n",
                    "import pandas as pd\n",
                    "import matplotlib.pyplot as plt\n",
                    "import seaborn as sns\n",
                    "\n",
                    "# Load exported data\n",
                    f"with open('{report_data.export_json_path}', 'r') as f:\n",
                    "    data = json.load(f)\n",
                    "\n",
                    "records = data['records']\n",
                    "print(f'Loaded {len(records)} records')",
                ],
                "outputs": [],
                "execution_count": None,
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": [
                    "# Convert to DataFrame\n",
                    "df = pd.DataFrame([{\n",
                    "    'substrate': r.get('substrate'),\n",
                    "    'geometry': r.get('geometry'),\n",
                    "    'dynamics': r.get('dynamics'),\n",
                    "    'plasticity': r.get('plasticity'),\n",
                    "    'credit': r.get('credit'),\n",
                    "    'update': r.get('update'),\n",
                    "    **r.get('payload', {})\n",
                    "} for r in records])\n",
                    "\n",
                    "print(df.shape)\n",
                    "print(df.columns.tolist())\n",
                    "df.head()",
                ],
                "outputs": [],
                "execution_count": None,
            },
            {"cell_type": "markdown", "metadata": {}, "source": ["## Axis Coverage"]},
            {
                "cell_type": "code",
                "metadata": {},
                "source": [
                    "# Axis coverage\n",
                    "coverage_data = {}\n",
                    "for axis in ['substrate', 'geometry', 'dynamics', 'plasticity', 'credit', 'update']:\n",
                    "    if axis in df.columns:\n",
                    "        coverage_data[axis] = df[axis].value_counts().to_dict()\n",
                    "\n",
                    "for axis, counts in coverage_data.items():\n",
                    "    print(f'\\n{axis} ({len(counts)} primitives):')\n",
                    "    for k, v in sorted(counts.items(), key=lambda x: -x[1]):\n",
                    "        print(f'  {k}: {v}')",
                ],
                "outputs": [],
                "execution_count": None,
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["## Pareto Frontiers"],
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": [
                    "# Pareto frontier: val_acc vs walltime_total\n",
                    "if 'val_acc' in df.columns and 'walltime_total' in df.columns:\n",
                    "    pareto_df = df.dropna(subset=['val_acc', 'walltime_total'])\n",
                    "    \n",
                    "    def is_pareto(row):\n",
                    "        return not ((pareto_df['val_acc'] >= row['val_acc']) &\n",
                    "                    (pareto_df['walltime_total'] <= row['walltime_total']) &\n",
                    "                    ((pareto_df['val_acc'] > row['val_acc']) |\n",
                    "                     (pareto_df['walltime_total'] < row['walltime_total']))).any()\n",
                    "    \n",
                    "    pareto_df['is_pareto'] = pareto_df.apply(is_pareto, axis=1)\n",
                    "    pareto_front = pareto_df[pareto_df['is_pareto']]\n",
                    "    \n",
                    "    plt.figure(figsize=(10, 6))\n",
                    "    plt.scatter(pareto_df['walltime_total'], pareto_df['val_acc'], alpha=0.3, label='All')\n",
                    "    plt.scatter(pareto_front['walltime_total'], pareto_front['val_acc'], color='red', label='Pareto')\n",
                    "    plt.xlabel('Walltime (s)')\n",
                    "    plt.ylabel('Validation Accuracy')\n",
                    "    plt.title('Pareto Frontier: Accuracy vs Walltime')\n",
                    "    plt.legend()\n",
                    "    plt.xscale('log')\n",
                    "    plt.grid(True, alpha=0.3)\n",
                    "    plt.show()\n",
                    "    \n",
                    "    print(f'Pareto front size: {len(pareto_front)}')\n",
                    "    print(pareto_front[['substrate', 'geometry', 'dynamics', 'credit', 'update', 'val_acc', 'walltime_total']].to_string())",
                ],
                "outputs": [],
                "execution_count": None,
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["## Credit Assignment Comparison"],
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": [
                    "# Compare credit assignments\n",
                    "if 'credit' in df.columns and 'val_acc' in df.columns:\n",
                    "    credit_stats = df.groupby('credit')['val_acc'].agg(['mean', 'std', 'count']).sort_values('mean', ascending=False)\n",
                    "    print(credit_stats.to_string())\n",
                    "    \n",
                    "    plt.figure(figsize=(10, 6))\n",
                    "    credit_stats['mean'].plot(kind='bar', yerr=credit_stats['std'], capsize=4)\n",
                    "    plt.title('Validation Accuracy by Credit Assignment')\n",
                    "    plt.ylabel('Mean Val Acc')\n",
                    "    plt.xticks(rotation=45)\n",
                    "    plt.tight_layout()\n",
                    "    plt.show()",
                ],
                "outputs": [],
                "execution_count": None,
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["## Dynamics Family Comparison"],
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": [
                    "# Compare dynamics families\n",
                    "if 'dynamics' in df.columns and 'val_acc' in df.columns:\n",
                    "    dyn_stats = df.groupby('dynamics')['val_acc'].agg(['mean', 'std', 'count']).sort_values('mean', ascending=False)\n",
                    "    print(dyn_stats.to_string())\n",
                    "    \n",
                    "    if 'settle_steps' in df.columns:\n",
                    "        dyn_settle = df.groupby('dynamics')['settle_steps'].agg(['mean', 'std']).sort_values('mean')\n",
                    "        print('\\nSettling Steps:')\n",
                    "        print(dyn_settle.to_string())",
                ],
                "outputs": [],
                "execution_count": None,
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["## Substrate Comparison"],
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": [
                    "# Compare substrates\n",
                    "if 'substrate' in df.columns and 'val_acc' in df.columns:\n",
                    "    sub_stats = df.groupby('substrate')['val_acc'].agg(['mean', 'std', 'count']).sort_values('mean', ascending=False)\n",
                    "    print(sub_stats.to_string())\n",
                    "    \n",
                    "    if 'energy_per_step' in df.columns:\n",
                    "        sub_energy = df.groupby('substrate')['energy_per_step'].agg(['mean', 'std'])\n",
                    "        print('\\nEnergy per Step:')\n",
                    "        print(sub_energy.to_string())",
                ],
                "outputs": [],
                "execution_count": None,
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["## Generated Hypotheses"],
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": [
                    "import json\n",
                    "hypotheses = " + repr(report_data.hypotheses) + "\n",
                    "\n",
                    "for h in hypotheses:\n",
                    "    print(f\"\\n{h['id']}\")\n",
                    "    print(f\"  Q: {h['question']}\")\n",
                    "    print(f\"  Prediction: {h['prediction']}\")\n",
                    "    print(f\"  Test: {h['test']}\")\n",
                    "    print(f\"  Tags: {', '.join(h['tags'])}\")",
                ],
                "outputs": [],
                "execution_count": None,
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["## Export to Campaign YAML"],
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": [
                    "# Convert hypotheses to campaign DSL (Phase B2)\n",
                    "import yaml\n",
                    "\n",
                    "campaign = {\n",
                    "    'meta': {\n",
                    "        'name': 'followup_from_showcase',\n",
                    "        'hypotheses': [h['id'] for h in hypotheses],\n",
                    "        'description': 'Follow-up campaign from showcase auto-hypotheses'\n",
                    "    },\n",
                    "    'design': {\n",
                    "        'factors': {\n",
                    "            'credit': ['gradient', 'equilibrium_prop', 'feedback_alignment', 'pepita'],\n",
                    "            'substrate': ['digital', 'analog', 'memristive'],\n",
                    "            'dynamics': ['energy_minimization', 'predictive_settling']\n",
                    "        },\n",
                    "        'fixed': {\n",
                    "            'geometry': 'feedforward',\n",
                    "            'update': 'adam',\n",
                    "            'plasticity': 'null'\n",
                    "        },\n",
                    "        'blocks': [\n",
                    "            {'task': 'mnist', 'epochs': 50, 'seeds': 10}\n",
                    "        ]\n",
                    "    },\n",
                    "    'analysis': {\n",
                    "        'primary': 'val_acc vs energy_per_step Pareto',\n",
                    "        'secondary': ['stability_margin', 'settle_steps'],\n",
                    "        'stats': ['cohens_d', 'cliffs_delta', 'bayes_factor']\n",
                    "    }\n",
                    "}\n",
                    "\n",
                    "with open('campaign_followup.yaml', 'w') as f:\n",
                    "    yaml.dump(campaign, f, default_flow_style=False, sort_keys=False)\n",
                    "\n",
                    "print('Campaign YAML written to campaign_followup.yaml')\n",
                    "print(yaml.dump(campaign, default_flow_style=False, sort_keys=False))",
                ],
                "outputs": [],
                "execution_count": None,
            },
        ],
    }

    import json

    Path(output_path).write_text(json.dumps(notebook, indent=2), encoding="utf-8")
    print(f"Notebook exported to: {output_path}")


def _print_final_summary(
    report_data: ShowcaseReportData, report_path: str, store_path: str
):
    """Print final summary to console."""
    duration_hours = (report_data.end_time - report_data.start_time) / 3600

    print("\n" + "=" * 70)
    print("SHOWCASE CAMPAIGN COMPLETE")
    print("=" * 70)
    print(f"Campaign: {report_data.campaign_name}")
    print(
        f"Duration: {duration_hours:.2f}h (budget: {report_data.total_budget_hours:.2f}h)"
    )
    print(
        f"Utilization: {report_data.budget_utilization:.1%} {'✅' if report_data.budget_utilization >= 0.90 else '❌'}"
    )
    print(f"Termination: {report_data.termination_reason}")
    print(f"Cells evaluated: {report_data.total_cells_evaluated}")
    print(f"Pareto points: {len(report_data.pareto_points)}")
    print(f"Failure types: {len(report_data.failure_taxonomy)}")
    print(f"Hypotheses generated: {len(report_data.hypotheses)}")
    print(f"Report: {report_path}")
    print(f"Store: {store_path}")
    print("=" * 70)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Enhanced Showcase Campaign — Single Time-Boxed Loop with Advanced Reporting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run 1-hour experiment on GPU
  uv run scripts/showcase.py --hours 1 --device cuda --store results/showcase_1h.db

  # Run 30-minute experiment on CPU with quick profile
  uv run scripts/showcase.py --hours 0.5 --device cpu --profile quick --store results/showcase_30m.db

  # Run with bias detection
  uv run scripts/showcase.py --hours 1 --device cuda --bias-check --store results/showcase.db

  # Export Jupyter notebook for interactive analysis
  uv run scripts/showcase.py --hours 1 --export-notebook showcase.ipynb --store results/showcase.db
        """,
    )

    parser.add_argument(
        "--hours",
        type=float,
        default=1.0,
        help="Time budget in hours (hard deadline enforcement)",
    )
    parser.add_argument(
        "--device",
        choices=["auto", "cpu", "cuda"],
        default="auto",
        help="Device to run on (default: auto)",
    )
    parser.add_argument(
        "--store",
        type=str,
        default="results/showcase.db",
        help="DuckDB store path (default: results/showcase.db)",
    )
    parser.add_argument(
        "--strategy",
        type=str,
        default="balanced",
        choices=["broad_shallow", "balanced", "narrow_deep"],
        help="Search strategy (default: balanced)",
    )
    parser.add_argument(
        "--profile",
        type=str,
        choices=["quick", "balanced", "thorough", "deep"],
        help="Profile preset (overrides strategy/epochs/seeds)",
    )
    parser.add_argument(
        "--bias-check",
        action="store_true",
        help="Run bias detection by comparing policies",
    )
    parser.add_argument(
        "--export-notebook",
        type=str,
        help="Export Jupyter notebook for interactive analysis",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive TUI mode (requires textual)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate campaign YAML and exit",
    )

    args = parser.parse_args()

    return asyncio.run(
        run_showcase(
            store=args.store,
            device=args.device,
            dry_run=args.dry_run,
            strategy=args.strategy,
            hours=args.hours,
            profile=args.profile,
            bias_check=args.bias_check,
            export_notebook=args.export_notebook,
            interactive=args.interactive,
        )
    )


if __name__ == "__main__":
    sys.exit(main())
