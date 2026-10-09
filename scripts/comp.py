#!/usr/bin/env python
"""Unified CLI for Computronium Experiment Platform (comp command)."""

from __future__ import annotations

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="comp",
        description="Computronium Experiment Platform CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available subcommands:
  showcase         Run enhanced showcase campaign
  hypothesis       Hypothesis-driven campaign management
  report           Generate reports from experiment stores
  analyze          Analyze experiment results

Examples:
  comp showcase --hours 1 --profile balanced
  comp hypothesis run-campaign --template credit_efficiency --hours 2 --seeds 10
  comp hypothesis list-templates
  comp report --store results/showcase.db --run-id <run_id> --format html
        """,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # showcase subcommand
    showcase_parser = subparsers.add_parser(
        "showcase", help="Run enhanced showcase campaign"
    )
    showcase_parser.add_argument(
        "--store", default="results/showcase.db", help="DuckDB store path"
    )
    showcase_parser.add_argument(
        "--device", choices=["auto", "cpu", "cuda"], default="auto"
    )
    showcase_parser.add_argument("--dry-run", action="store_true")
    showcase_parser.add_argument(
        "--strategy", choices=["broad_shallow", "balanced", "narrow_deep"], default="balanced"
    )
    showcase_parser.add_argument("--hours", type=float, default=1.0)
    showcase_parser.add_argument(
        "--profile", choices=["quick", "balanced", "thorough", "deep"]
    )
    showcase_parser.add_argument("--bias-check", action="store_true")
    showcase_parser.add_argument("--export-notebook", type=str)
    showcase_parser.add_argument("--interactive", action="store_true")

    # hypothesis subcommand
    hypothesis_parser = subparsers.add_parser(
        "hypothesis", help="Hypothesis-driven campaign management"
    )
    hypothesis_subparsers = hypothesis_parser.add_subparsers(dest="hyp_command", required=True)

    # hypothesis list-templates
    hypothesis_subparsers.add_parser("list-templates", help="List campaign templates")

    # hypothesis create-campaign
    create_parser = hypothesis_subparsers.add_parser("create-campaign", help="Create campaign from template")
    create_parser.add_argument("template", choices=["credit_efficiency", "dynamics_stability", "substrate_noise", "plasticity_forgetting"])
    create_parser.add_argument("--name")
    create_parser.add_argument("--hours", type=float, default=2.0)
    create_parser.add_argument("--seeds", type=int, default=10)
    create_parser.add_argument("--epochs", type=int, default=50)
    create_parser.add_argument("-o", "--output")

    # hypothesis validate-campaign
    validate_parser = hypothesis_subparsers.add_parser("validate-campaign", help="Validate campaign YAML")
    validate_parser.add_argument("campaign", help="Campaign YAML file")

    # hypothesis run-campaign
    run_parser = hypothesis_subparsers.add_parser("run-campaign", help="Run hypothesis-driven campaign")
    run_parser.add_argument("--campaign", help="Campaign YAML file")
    run_parser.add_argument("--template", choices=["credit_efficiency", "dynamics_stability", "substrate_noise", "plasticity_forgetting"])
    run_parser.add_argument("--name")
    run_parser.add_argument("--hours", type=float, default=2.0)
    run_parser.add_argument("--seeds", type=int, default=10)
    run_parser.add_argument("--epochs", type=int, default=50)
    run_parser.add_argument("--parallel", type=int, default=1)
    run_parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    run_parser.add_argument("--report")
    run_parser.add_argument("--report-format", choices=["html", "latex", "pdf"], default="html")
    run_parser.add_argument("--test-hypotheses")

    # hypothesis register-hypothesis
    reg_parser = hypothesis_subparsers.add_parser("register-hypothesis", help="Register new hypothesis")
    reg_parser.add_argument("--id", required=True)
    reg_parser.add_argument("--question", required=True)
    reg_parser.add_argument("--prediction", required=True)
    reg_parser.add_argument("--rationale")
    reg_parser.add_argument("--test-type", required=True, choices=["paired_t_test", "independent_t_test", "mann_whitney_u", "wilcoxon", "anova_one_way", "anova_two_way", "kruskal_wallis", "chi_square", "fisher_exact", "bayes_factor", "cohens_d", "cliffs_delta", "correlation_pearson", "correlation_spearman", "linear_regression", "logistic_regression"])
    reg_parser.add_argument("--metric", required=True)
    reg_parser.add_argument("--grouping")
    reg_parser.add_argument("--compare")
    reg_parser.add_argument("--covariates")
    reg_parser.add_argument("--effect-size", type=float, default=0.5)
    reg_parser.add_argument("--power", type=float, default=0.8)
    reg_parser.add_argument("--alpha", type=float, default=0.05)
    reg_parser.add_argument("--tags")
    reg_parser.add_argument("--pre-register", action="store_true")
    reg_parser.add_argument("--registry")

    # hypothesis list-hypotheses
    list_parser = hypothesis_subparsers.add_parser("list-hypotheses", help="List hypotheses")
    list_parser.add_argument("--status", choices=["draft", "pre_registered", "tested", "confirmed", "rejected", "inconclusive"])
    list_parser.add_argument("--registry")

    # hypothesis export-hypotheses
    export_parser = hypothesis_subparsers.add_parser("export-hypotheses", help="Export hypotheses to YAML")
    export_parser.add_argument("-o", "--output")
    export_parser.add_argument("--registry")

    # report subcommand
    report_parser = subparsers.add_parser("report", help="Generate reports from experiment stores")
    report_parser.add_argument("--store", required=True, help="DuckDB store path")
    report_parser.add_argument("--run-id", required=True, help="Run ID")
    report_parser.add_argument("-o", "--output", required=True, help="Output file path")
    report_parser.add_argument("--format", choices=["html", "latex", "pdf"], default="html")
    report_parser.add_argument("--campaign-name")

    args = parser.parse_args()

    if args.command == "showcase":
        from computronium.experiment.surface.cli import main as showcase_main
        # Forward to showcase main
        sys.argv = ["showcase"] + sys.argv[2:]
        return showcase_main()
    elif args.command == "hypothesis":
        from computronium.experiment.cli.hypothesis_campaign import main as hypothesis_main
        sys.argv = ["hypothesis"] + sys.argv[2:]
        return hypothesis_main()
    elif args.command == "report":
        return cmd_report(args)
    else:
        parser.print_help()
        return 1


def cmd_report(args: argparse.Namespace) -> int:
    """Generate report from store."""
    from computronium.experiment.templates.report import generate_report_from_store

    try:
        path = generate_report_from_store(
            store_path=args.store,
            run_id=args.run_id,
            output_path=args.output,
            format=args.format,
            campaign_name=args.campaign_name,
        )
        print(f"Report generated: {path}")
        return 0
    except Exception as e:
        print(f"Error generating report: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())