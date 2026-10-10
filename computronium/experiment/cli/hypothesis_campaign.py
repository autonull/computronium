"""CLI for hypothesis-driven campaigns (Phase B).

Run campaigns from DSL specifications, test hypotheses, generate reports.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path

from computronium.experiment.design import (
    CampaignDSL,
    EffectSizeType,
    HypothesisRegistry,
    HypothesisResult,
    HypothesisSpec,
    HypothesisStatus,
    TestType,
    create_campaign,
    list_campaign_templates,
    validate_campaign_design,
)
from computronium.experiment.evidence.limitations import replication_keys_of
from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.execution.campaign import run_campaign
from computronium.experiment.templates.report import (
    CampaignConfig,
    ReproducibilityInfo,
    generate_report_from_store,
)


def cmd_list_templates(args: argparse.Namespace) -> int:
    """List available campaign templates."""
    templates = list_campaign_templates()
    print("Available campaign templates:")
    for t in templates:
        print(f"  {t}")
    return 0


def cmd_create_campaign(args: argparse.Namespace) -> int:
    """Create a campaign from template."""
    try:
        campaign = create_campaign(
            args.template,
            name=args.name,
            time_budget_hours=args.hours,
            n_seeds=args.seeds,
            epochs=args.epochs,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    output_path = Path(args.output) if args.output else Path(f"{campaign.meta.name}.yaml")
    campaign.to_campaign_yaml(output_path)

    # Validate
    validation = validate_campaign_design(campaign)
    print(f"Campaign written to: {output_path}")
    print(f"Design matrix size: {validation.design_matrix_size}")
    print(f"Estimated runtime: {validation.estimated_runtime_hours:.2f}h")
    print(f"Required seeds/group: {validation.required_seeds_per_group}")
    print(f"Actual seeds/group: {validation.actual_seeds_per_group}")
    if validation.warnings:
        print("Warnings:")
        for w in validation.warnings:
            print(f"  - {w}")
    if validation.errors:
        print("Errors:")
        for e in validation.errors:
            print(f"  - {e}")
        return 1
    return 0


def cmd_validate_campaign(args: argparse.Namespace) -> int:
    """Validate a campaign YAML file."""
    try:
        campaign = CampaignDSL.from_yaml(args.campaign)
    except Exception as e:
        print(f"Error loading campaign: {e}", file=sys.stderr)
        return 1

    validation = validate_campaign_design(campaign)
    print(f"Campaign: {campaign.meta.name}")
    print(f"Valid: {validation.valid}")
    print(f"Design matrix size: {validation.design_matrix_size}")
    print(f"Estimated runtime: {validation.estimated_runtime_hours:.2f}h")
    print(f"Required seeds/group: {validation.required_seeds_per_group}")
    print(f"Actual seeds/group: {validation.actual_seeds_per_group}")
    if validation.warnings:
        print("Warnings:")
        for w in validation.warnings:
            print(f"  - {w}")
    if validation.errors:
        print("Errors:")
        for e in validation.errors:
            print(f"  - {e}")
    return 0 if validation.valid else 1


async def cmd_run_campaign(args: argparse.Namespace) -> int:
    """Run a hypothesis-driven campaign."""
    # Load or create campaign
    if args.campaign:
        try:
            campaign = CampaignDSL.from_yaml(args.campaign)
        except Exception as e:
            print(f"Error loading campaign: {e}", file=sys.stderr)
            return 1
    else:
        # Create from template
        try:
            campaign = create_campaign(
                args.template or "credit_efficiency",
                name=args.name,
                time_budget_hours=args.hours,
                n_seeds=args.seeds,
                epochs=args.epochs,
            )
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    # Validate first
    validation = validate_campaign_design(campaign)
    if validation.errors:
        print("Design errors:")
        for e in validation.errors:
            print(f"  - {e}")
        return 1
    if validation.warnings:
        print("Design warnings:")
        for w in validation.warnings:
            print(f"  - {w}")

    # Export to campaign YAML for execution
    campaign_yaml = f"{campaign.meta.name}_execution.yaml"
    campaign.to_campaign_yaml(campaign_yaml)

    print(f"Running campaign: {campaign.meta.name}")
    print(f"Store: {campaign.output.db}")

    # Run campaign
    try:
        result = await run_campaign(
            campaign_path=campaign_yaml,
            parallel=args.parallel,
            device=args.device,
        )
    except Exception as e:
        print(f"Campaign execution failed: {e}", file=sys.stderr)
        return 1

    print(f"Campaign completed: {result['completed']}/{result['total_runs']} runs successful")

    # Generate report if requested
    if args.report:
        # Need to wait for store to be fully closed by campaign runner
        import asyncio
        await asyncio.sleep(1.0)
        await _generate_campaign_report(campaign, args.report, args.report_format)

    # Test hypotheses if requested
    if args.test_hypotheses:
        await _test_hypotheses(campaign, args.test_hypotheses)

    return 0


async def _generate_campaign_report(
    campaign: CampaignDSL,
    output_path: str,
    format: str = "html",
) -> None:
    """Generate report from campaign results."""
    store_path = Path(campaign.output.db)
    if not store_path.exists():
        print(f"Store not found: {store_path}")
        return

    # Find the main run
    store = RecordStore(StoreConfig(path=store_path))
    with store:
        runs = store.query_runs()
        if not runs:
            print("No runs found in store")
            return
        # Get the run with most records
        main_run = max(runs, key=lambda r: store.count_records(r.run_id))

        # Load hypotheses
        hypotheses = []
        registry = HypothesisRegistry()
        for hyp_id in campaign.meta.hypotheses:
            hyp = registry.get(hyp_id)
            if hyp:
                hypotheses.append(hyp.to_report_hypothesis())

        # Build campaign config for report
        campaign_config = CampaignConfig(
            factors={name: [str(v) for v in f.values] for name, f in campaign.design.factors.items()},
            fixed={name: str(f.value) for name, f in campaign.design.fixed.items()},
            blocks=[{"task": b.task, "epochs": b.epochs, "seeds": b.seeds} for b in campaign.design.blocks],
            sampler=campaign.hpo.sampler.value,
            objectives=[o.name for o in campaign.hpo.objectives],
            n_trials=campaign.hpo.n_trials,
            n_seeds=campaign.hpo.n_seeds,
            epochs=max(b.epochs for b in campaign.design.blocks),
            max_wall_hours=campaign.resources.max_wall_hours,
            max_epoch_time_sec=campaign.resources.max_epoch_time_sec,
        )

        # Reproducibility info
        reproducibility = ReproducibilityInfo(
            repro_command=f"uv run comp hypothesis-campaign --campaign {campaign.meta.name}.yaml",
            export_json_path=f"{store_path.with_suffix('')}_export.json",
        )

        # Generate report
        report_path = generate_report_from_store(
            store_path=store_path,
            run_id=main_run.run_id,
            output_path=output_path,
            format=format,
            campaign_name=campaign.meta.name,
            campaign_config=campaign_config,
            hypotheses=hypotheses,
            reproducibility=reproducibility,
        )
        print(f"Report generated: {report_path}")


async def _test_hypotheses(campaign: CampaignDSL, hypotheses_file: str) -> None:
    """Test hypotheses against campaign results."""
    store_path = Path(campaign.output.db)
    if not store_path.exists():
        print(f"Store not found: {store_path}")
        return

    # Load hypotheses using registry's from_yaml method
    try:
        registry = HypothesisRegistry.from_yaml(Path(hypotheses_file))
    except Exception as e:
        print(f"Error loading hypotheses: {e}")
        return

    # Run statistical tests
    store = RecordStore(StoreConfig(path=store_path))
    with store:
        runs = store.query_runs()
        if not runs:
            print("No runs found")
            return
        main_run = max(runs, key=lambda r: store.count_records(r.run_id))

        from computronium.experiment.surface.report import ReportGenerator
        generator = ReportGenerator(store)

        print(f"\nTesting hypotheses for run {main_run.run_id}:")
        for hyp_id in campaign.meta.hypotheses:
            hyp = registry.get(hyp_id)
            if not hyp:
                print(f"  {hyp_id}: NOT FOUND in registry")
                continue

            print(f"\n  {hyp.id}: {hyp.question}")
            print(f"    Prediction: {hyp.prediction}")
            print(f"    Test: {hyp._render_test_spec()}")

            # Run appropriate test based on type
            try:
                result = await _run_hypothesis_test(generator, main_run.run_id, hyp)
                if result:
                    registry.record_result(hyp_id, result)
                    print(f"    Result: p={result.p_value:.4g}, effect={result.effect_size:.3f} ({result.effect_size_type.value})")
                    print(f"    Significant: {result.significant}, Power: {result.power_achieved:.2f}")
                else:
                    print("    Result: INSUFFICIENT DATA")
            except Exception as e:
                print(f"    Error: {e}")

    print("\nHypothesis results saved to registry")


async def _run_hypothesis_test(
    generator,
    run_id: str,
    hypothesis: HypothesisSpec,
) -> HypothesisResult | None:
    """Run a single hypothesis test."""
    from computronium.experiment.evidence.claims import (
        cell_metrics_by_axis_value,
        replication_key,
    )
    from computronium.experiment.evidence.significance import (
        Resampling,
        paired_significance,
    )
    from computronium.experiment.schema.axis import StructuralAxis

    records = generator._store.query_records(run_id=run_id)
    if not records:
        return None

    # Get achieved seeds per cell
    keys = replication_keys_of(records)
    achieved = {key: generator._store.count_achieved_seeds(replication_key=key, run_id=run_id) for key in keys}

    # Filter to claim-eligible
    min_seeds = hypothesis.min_samples_per_group
    eligible_keys = {k for k, v in achieved.items() if v >= min_seeds}
    eligible_records = [r for r in records if replication_key(r) in eligible_keys]

    if not eligible_records:
        return None

    # Get metric values grouped by axis
    axis = StructuralAxis(hypothesis.grouping_factor) if hypothesis.grouping_factor else None
    if not axis:
        return None

    metric = hypothesis.primary_metric
    by_value = cell_metrics_by_axis_value(
        eligible_records,
        axis=axis,
        metric=metric,
        achieved=achieved,
        min_seeds=min_seeds,
    )

    if hypothesis.comparison_values:
        values_to_compare = hypothesis.comparison_values
    else:
        values_to_compare = list(by_value.keys())[:2]

    if len(values_to_compare) < 2:
        return None

    best_val, worst_val = values_to_compare[0], values_to_compare[1]
    best_data = by_value.get(best_val, {})
    worst_data = by_value.get(worst_val, {})

    if not best_data or not worst_data:
        return None

    # Run paired significance test
    sig_result = paired_significance(
        best_data,
        worst_data,
        axis=hypothesis.grouping_factor or "unknown",
        metric=metric,
        best_value=best_val,
        worst_value=worst_val,
        resampling=Resampling(alpha=hypothesis.alpha),
    )

    if not sig_result.tested:
        return None

    return HypothesisResult(
        hypothesis_id=hypothesis.id,
        test_type=hypothesis.test_type,
        test_statistic=sig_result.cohens_dz,
        p_value=sig_result.p_value,
        effect_size=sig_result.cohens_dz,
        effect_size_type=EffectSizeType.COHENS_D,
        confidence_interval=(sig_result.ci_lower, sig_result.ci_upper),
        significant=sig_result.significant,
        power_achieved=None,  # Not computed by current test
        n_samples=sig_result.shared_cells * 2,  # paired
        n_groups=2,
        groups_tested=[best_val, worst_val],
        notes=f"Paired sign-flip permutation: {best_val} vs {worst_val} on {metric} (shared_cells={sig_result.shared_cells})",
    )


def cmd_register_hypothesis(args: argparse.Namespace) -> int:
    """Register a new hypothesis."""
    registry = HypothesisRegistry(Path(args.registry) if args.registry else None)

    n_comparisons = len(args.compare.split(",")) - 1 if args.compare else 1
    spec = HypothesisSpec(
        id=args.id,
        question=args.question,
        prediction=args.prediction,
        rationale=args.rationale,
        test_type=TestType(args.test_type),
        primary_metric=args.metric,
        grouping_factor=args.grouping,
        comparison_values=args.compare.split(",") if args.compare else None,
        covariates=args.covariates.split(",") if args.covariates else [],
        min_effect_size=args.effect_size,
        required_power=args.power,
        alpha=args.alpha,
        tags=args.tags.split(",") if args.tags else [],
        n_comparisons=max(1, n_comparisons),
        paired=False,
        alternative="two-sided",
        min_samples_per_group=10,
    )

    if args.pre_register:
        spec.status = spec.status.PRE_REGISTERED
        spec.pre_registered_at = datetime.now()

    registry.register(spec)
    print(f"Registered hypothesis: {spec.id}")
    return 0


def cmd_list_hypotheses(args: argparse.Namespace) -> int:
    """List registered hypotheses."""
    registry = HypothesisRegistry(Path(args.registry) if args.registry else None)

    hypotheses = registry.list_all(
        HypothesisStatus(args.status) if args.status else None
    )

    if not hypotheses:
        print("No hypotheses registered")
        return 0

    for hyp in hypotheses:
        print(f"{hyp.id} [{hyp.status.value}]")
        print(f"  Q: {hyp.question}")
        print(f"  Test: {hyp._render_test_spec()}")
        print(f"  Effect size: {hyp.min_effect_size}, Power: {hyp.required_power}")
        print(f"  Tags: {', '.join(hyp.tags)}")
        print()
    return 0


def cmd_export_hypotheses(args: argparse.Namespace) -> int:
    """Export hypotheses to YAML for campaign DSL."""
    registry = HypothesisRegistry(Path(args.registry) if args.registry else None)
    output_path = Path(args.output) if args.output else Path("hypotheses.yaml")
    registry.export_to_yaml(output_path)
    print(f"Exported {len(registry._hypotheses)} hypotheses to {output_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        description="Hypothesis-driven campaign management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list-templates
    subparsers.add_parser("list-templates", help="List available campaign templates")

    # create-campaign
    p_create = subparsers.add_parser("create-campaign", help="Create campaign from template")
    p_create.add_argument("template", choices=list_campaign_templates())
    p_create.add_argument("--name", help="Campaign name")
    p_create.add_argument("--hours", type=float, default=2.0, help="Time budget in hours")
    p_create.add_argument("--seeds", type=int, default=10, help="Seeds per cell")
    p_create.add_argument("--epochs", type=int, default=50, help="Epochs per trial")
    p_create.add_argument("-o", "--output", help="Output YAML path")

    # validate-campaign
    p_validate = subparsers.add_parser("validate-campaign", help="Validate campaign YAML")
    p_validate.add_argument("campaign", help="Campaign YAML file")

    # run-campaign
    p_run = subparsers.add_parser("run-campaign", help="Run hypothesis-driven campaign")
    p_run.add_argument("--campaign", help="Campaign YAML file")
    p_run.add_argument("--template", choices=list_campaign_templates(), help="Use template instead")
    p_run.add_argument("--name", help="Campaign name")
    p_run.add_argument("--hours", type=float, default=2.0)
    p_run.add_argument("--seeds", type=int, default=10)
    p_run.add_argument("--epochs", type=int, default=50)
    p_run.add_argument("--parallel", type=int, default=1)
    p_run.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    p_run.add_argument("--report", help="Generate report at path")
    p_run.add_argument("--report-format", choices=["html", "latex", "pdf"], default="html")
    p_run.add_argument("--test-hypotheses", help="Hypotheses JSON file to test")

    # register-hypothesis
    p_reg = subparsers.add_parser("register-hypothesis", help="Register new hypothesis")
    p_reg.add_argument("--id", required=True)
    p_reg.add_argument("--question", required=True)
    p_reg.add_argument("--prediction", required=True)
    p_reg.add_argument("--rationale")
    p_reg.add_argument("--test-type", required=True, choices=[t.value for t in TestType])
    p_reg.add_argument("--metric", required=True)
    p_reg.add_argument("--grouping")
    p_reg.add_argument("--compare", help="Comma-separated values to compare")
    p_reg.add_argument("--covariates", help="Comma-separated covariates")
    p_reg.add_argument("--effect-size", type=float, default=0.5)
    p_reg.add_argument("--power", type=float, default=0.8)
    p_reg.add_argument("--alpha", type=float, default=0.05)
    p_reg.add_argument("--tags", help="Comma-separated tags")
    p_reg.add_argument("--pre-register", action="store_true")
    p_reg.add_argument("--registry", help="Registry file path")

    # list-hypotheses
    p_list = subparsers.add_parser("list-hypotheses", help="List registered hypotheses")
    p_list.add_argument("--status", choices=[s.value for s in HypothesisStatus])
    p_list.add_argument("--registry", help="Registry file path")

    # export-hypotheses
    p_export = subparsers.add_parser("export-hypotheses", help="Export hypotheses to YAML")
    p_export.add_argument("-o", "--output", help="Output YAML path")
    p_export.add_argument("--registry", help="Registry file path")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "list-templates":
        return cmd_list_templates(args)
    elif args.command == "create-campaign":
        return cmd_create_campaign(args)
    elif args.command == "validate-campaign":
        return cmd_validate_campaign(args)
    elif args.command == "run-campaign":
        return asyncio.run(cmd_run_campaign(args))
    elif args.command == "register-hypothesis":
        return cmd_register_hypothesis(args)
    elif args.command == "list-hypotheses":
        return cmd_list_hypotheses(args)
    elif args.command == "export-hypotheses":
        return cmd_export_hypotheses(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
