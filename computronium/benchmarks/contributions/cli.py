"""Benchmark Contributions CLI (``comp benchmark-contrib``)."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

from computronium.benchmarks.contributions import (
    BenchmarkContribution,
    BenchmarkTask,
    contribution_registry,
)
from computronium.benchmarks.contributions.core.registry import Leaderboard


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="comp benchmark-contrib",
        description="Benchmark Contributions — Standard tasks, reference results, leaderboards",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Subcommand")

    # list-tasks
    list_tasks_parser = subparsers.add_parser(
        "list-tasks", help="List available benchmark tasks"
    )
    list_tasks_parser.add_argument("--domain", help="Filter by domain")
    list_tasks_parser.add_argument("--tags", nargs="+", help="Filter by tags")
    list_tasks_parser.add_argument("--format", choices=["text", "json"], default="text")

    # show-task
    show_task_parser = subparsers.add_parser("show-task", help="Show task details")
    show_task_parser.add_argument("task_id", help="Task ID")
    show_task_parser.add_argument("--format", choices=["text", "json"], default="text")

    # list-references
    list_refs_parser = subparsers.add_parser(
        "list-references", help="List reference results for a task"
    )
    list_refs_parser.add_argument("task_id", help="Task ID")
    list_refs_parser.add_argument("--model", help="Filter by model name")
    list_refs_parser.add_argument("--format", choices=["text", "json"], default="text")

    # list-contributions
    list_contribs_parser = subparsers.add_parser(
        "list-contributions", help="List community contributions for a task"
    )
    list_contribs_parser.add_argument("task_id", help="Task ID")
    list_contribs_parser.add_argument("--model", help="Filter by model name")
    list_contribs_parser.add_argument(
        "--verified-only", action="store_true", help="Show only verified contributions"
    )
    list_contribs_parser.add_argument(
        "--format", choices=["text", "json"], default="text"
    )

    # submit-contribution
    submit_parser = subparsers.add_parser("submit", help="Submit a new contribution")
    submit_parser.add_argument("task_id", help="Task ID")
    submit_parser.add_argument("model_name", help="Model name")
    submit_parser.add_argument(
        "--model-config", type=json.loads, default="{}", help="Model config as JSON"
    )
    submit_parser.add_argument(
        "--metrics",
        type=json.loads,
        required=True,
        help="Metrics as JSON (e.g., '{\"validation_accuracy\": 0.95}')",
    )
    submit_parser.add_argument(
        "--contributor", default="anonymous", help="Contributor name"
    )
    submit_parser.add_argument("--seeds", type=int, default=3, help="Number of seeds")
    submit_parser.add_argument(
        "--seed-values", type=int, nargs="+", default=[42, 123, 456], help="Seed values"
    )
    submit_parser.add_argument("--hardware", help="Hardware description")
    submit_parser.add_argument("--runtime", type=float, help="Runtime in seconds")
    submit_parser.add_argument("--output", help="Output file for contribution record")

    # verify-contribution
    verify_parser = subparsers.add_parser(
        "verify", help="Verify a contribution against reference"
    )
    verify_parser.add_argument("task_id", help="Task ID")
    verify_parser.add_argument(
        "--model", help="Specific model to verify (default: all)"
    )
    verify_parser.add_argument(
        "--regression-tolerance", type=float, default=0.05, help="Regression tolerance"
    )

    # leaderboard
    lb_parser = subparsers.add_parser("leaderboard", help="Show leaderboard for a task")
    lb_parser.add_argument("task_id", help="Task ID")
    lb_parser.add_argument(
        "--metric", default="validation_accuracy", help="Primary metric"
    )
    lb_parser.add_argument(
        "--lower-better",
        action="store_true",
        help="Lower values are better for primary metric",
    )
    lb_parser.add_argument("--top", type=int, help="Show top K entries")
    lb_parser.add_argument(
        "--no-references", action="store_true", help="Exclude reference results"
    )
    lb_parser.add_argument(
        "--no-contributions",
        action="store_true",
        help="Exclude community contributions",
    )
    lb_parser.add_argument(
        "--unverified", action="store_true", help="Include unverified contributions"
    )
    lb_parser.add_argument("--format", choices=["text", "json", "html"], default="text")
    lb_parser.add_argument("--output", help="Output file")

    # export
    export_parser = subparsers.add_parser("export", help="Export all data to JSON")
    export_parser.add_argument("output", help="Output file")
    export_parser.add_argument("--task", help="Specific task ID (default: all)")

    return parser


def _list_tasks(args) -> int:
    tasks = contribution_registry.list_tasks(
        domain=args.domain, tags=tuple(args.tags) if args.tags else ()
    )

    if args.format == "json":
        output = [
            {
                "task_id": t.task_id,
                "name": t.name,
                "description": t.description,
                "domain": t.domain,
                "difficulty": t.difficulty,
                "tags": list(t.tags),
                "reference_metrics": t.reference_metrics,
                "regression_tolerance": t.regression_tolerance,
                "min_performance": t.min_performance,
            }
            for t in tasks
        ]
        print(json.dumps(output, indent=2))
    else:
        if not tasks:
            print("No tasks found")
            return 0

        print(
            f"{'Task ID':<35} {'Name':<30} {'Domain':<12} {'Difficulty':<10} {'Tags'}"
        )
        print("-" * 100)
        for t in tasks:
            tags_str = ", ".join(t.tags) if t.tags else "—"
            print(
                f"{t.task_id:<35} {t.name:<30} {t.domain:<12} {t.difficulty:<10} {tags_str}"
            )

    return 0


def _show_task(args) -> int:
    task = contribution_registry.get_task(args.task_id)
    if not task:
        print(f"Task not found: {args.task_id}")
        return 1

    if args.format == "json":
        output = {
            "task_id": task.task_id,
            "name": task.name,
            "description": task.description,
            "domain": task.domain,
            "difficulty": task.difficulty,
            "tags": list(task.tags),
            "reference_metrics": task.reference_metrics,
            "regression_tolerance": task.regression_tolerance,
            "min_performance": task.min_performance,
            "reference_env": task.reference_env,
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"Task: {task.name} ({task.task_id})")
        print(f"Domain: {task.domain}")
        print(f"Difficulty: {task.difficulty}")
        print(f"Tags: {', '.join(task.tags) if task.tags else '—'}")
        print(f"Description: {task.description}")
        print()
        print("Reference Metrics:")
        for k, v in task.reference_metrics.items():
            print(f"  {k}: {v}")
        print(f"Regression Tolerance: {task.regression_tolerance}")
        if task.min_performance:
            print("Minimum Performance:")
            for k, v in task.min_performance.items():
                print(f"  {k}: {v}")

    return 0


def _list_references(args) -> int:
    results = contribution_registry.get_reference_results(
        args.task_id, model_name=args.model
    )

    if args.format == "json":
        output = [
            {
                "task_id": r.task_id,
                "model_name": r.model_name,
                "model_config": r.model_config,
                "metrics": r.metrics,
                "n_seeds": r.n_seeds,
                "seed_values": list(r.seed_values),
                "commit_sha": r.commit_sha,
                "timestamp": r.timestamp,
                "hardware": r.hardware,
                "runtime_seconds": r.runtime_seconds,
            }
            for r in results
        ]
        print(json.dumps(output, indent=2))
    else:
        if not results:
            print(f"No reference results for task: {args.task_id}")
            return 0

        print(f"Reference Results for {args.task_id}:")
        print("=" * 80)
        for r in results:
            print(f"Model: {r.model_name}")
            print(f"  Config: {r.model_config}")
            print(f"  Metrics: {r.metrics}")
            print(f"  Seeds: {r.n_seeds} ({', '.join(map(str, r.seed_values))})")
            if r.commit_sha:
                print(f"  Commit: {r.commit_sha}")
            if r.hardware:
                print(f"  Hardware: {r.hardware}")
            if r.runtime_seconds:
                print(f"  Runtime: {r.runtime_seconds:.1f}s")
            print()

    return 0


def _list_contributions(args) -> int:
    contribs = contribution_registry.get_contributions(
        args.task_id, model_name=args.model, verified_only=args.verified_only
    )

    if args.format == "json":
        output = [
            {
                "contribution_id": c.contribution_id,
                "task_id": c.task_id,
                "model_name": c.model_name,
                "model_config": c.model_config,
                "metrics": c.metrics,
                "reference_comparison": c.reference_comparison,
                "n_seeds": c.n_seeds,
                "seed_values": list(c.seed_values),
                "contributor": c.contributor,
                "commit_sha": c.commit_sha,
                "timestamp": c.timestamp,
                "hardware": c.hardware,
                "runtime_seconds": c.runtime_seconds,
                "verified": c.verified,
                "verification_notes": c.verification_notes,
            }
            for c in contribs
        ]
        print(json.dumps(output, indent=2))
    else:
        if not contribs:
            print(f"No contributions for task: {args.task_id}")
            return 0

        print(f"Contributions for {args.task_id}:")
        print("=" * 80)
        for c in contribs:
            status = "✓ VERIFIED" if c.verified else "⟳ PENDING"
            print(f"{status} {c.model_name} by {c.contributor}")
            print(f"  ID: {c.contribution_id}")
            print(f"  Config: {c.model_config}")
            print(f"  Metrics: {c.metrics}")
            if c.reference_comparison:
                print("  vs Reference:")
                for k, v in c.reference_comparison.items():
                    direction = "↑" if v > 0 else "↓"
                    print(f"    {k}: {v:+.2%} {direction}")
            print(f"  Seeds: {c.n_seeds} ({', '.join(map(str, c.seed_values))})")
            if c.commit_sha:
                print(f"  Commit: {c.commit_sha}")
            if c.hardware:
                print(f"  Hardware: {c.hardware}")
            if c.runtime_seconds:
                print(f"  Runtime: {c.runtime_seconds:.1f}s")
            if c.verification_notes:
                print(f"  Notes: {c.verification_notes}")
            print()

    return 0


def _submit_contribution(args) -> int:
    task = contribution_registry.get_task(args.task_id)
    if not task:
        print(f"Task not found: {args.task_id}")
        return 1

    # Compare against reference
    comparison = contribution_registry.compare_against_reference(
        args.task_id, args.model_name, args.metrics
    )

    contribution = BenchmarkContribution(
        contribution_id=f"{args.task_id}_{args.model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        task_id=args.task_id,
        model_name=args.model_name,
        model_config=args.model_config,
        metrics=args.metrics,
        reference_comparison=comparison,
        n_seeds=args.seeds,
        seed_values=tuple(args.seed_values),
        contributor=args.contributor,
        hardware=args.hardware,
        runtime_seconds=args.runtime,
        verified=False,
    )

    contribution_registry.add_contribution(contribution)
    contribution_registry._save_async()

    if args.output:
        Path(args.output).write_text(
            json.dumps(
                {
                    "contribution_id": contribution.contribution_id,
                    "task_id": contribution.task_id,
                    "model_name": contribution.model_name,
                    "model_config": contribution.model_config,
                    "metrics": contribution.metrics,
                    "reference_comparison": contribution.reference_comparison,
                    "n_seeds": contribution.n_seeds,
                    "seed_values": list(contribution.seed_values),
                    "contributor": contribution.contributor,
                    "commit_sha": contribution.commit_sha,
                    "timestamp": contribution.timestamp,
                    "hardware": contribution.hardware,
                    "runtime_seconds": contribution.runtime_seconds,
                    "verified": contribution.verified,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"Contribution saved to {args.output}")

    print(f"Contribution submitted: {contribution.contribution_id}")
    if comparison:
        print("Comparison against reference:")
        for k, v in comparison.items():
            direction = "↑" if v > 0 else "↓"
            print(f"  {k}: {v:+.2%} {direction}")

    return 0


def _is_lower_is_better(metric: str) -> bool:
    """Determine if lower values are better for a metric."""
    return any(
        keyword in metric.lower()
        for keyword in [
            "loss",
            "error",
            "time",
            "latency",
            "energy",
            "flops",
            "memory",
        ]
    )


def _check_minimum_performance(
    task: BenchmarkTask, contrib: BenchmarkContribution
) -> list[str]:
    """Check minimum performance requirements. Returns list of issues."""
    issues = []
    if task.min_performance:
        for metric, min_val in task.min_performance.items():
            val = contrib.metrics.get(metric)
            if val is not None and val < min_val:
                issues.append(f"{metric}={val:.4f} < minimum {min_val:.4f}")
    return issues


def _check_regression_against_reference(
    contrib: BenchmarkContribution, tolerance: float
) -> list[str]:
    """Check for regression against reference. Returns list of issues."""
    issues = []
    if contrib.reference_comparison:
        for metric, diff in contrib.reference_comparison.items():
            lower_is_better = _is_lower_is_better(metric)
            if lower_is_better:
                if diff > tolerance:
                    issues.append(
                        f"{metric} regressed by {diff:.2%} (tolerance: {tolerance:.1%})"
                    )
            elif diff < -tolerance:
                issues.append(
                    f"{metric} regressed by {diff:.2%} (tolerance: {tolerance:.1%})"
                )
    return issues


def _create_verified_contribution(
    contrib: BenchmarkContribution, timestamp: datetime
) -> BenchmarkContribution:
    """Create a verified version of a contribution."""
    return BenchmarkContribution(
        contribution_id=contrib.contribution_id,
        task_id=contrib.task_id,
        model_name=contrib.model_name,
        model_config=contrib.model_config,
        metrics=contrib.metrics,
        reference_comparison=contrib.reference_comparison,
        n_seeds=contrib.n_seeds,
        seed_values=contrib.seed_values,
        contributor=contrib.contributor,
        commit_sha=contrib.commit_sha,
        timestamp=contrib.timestamp,
        hardware=contrib.hardware,
        runtime_seconds=contrib.runtime_seconds,
        verified=True,
        verification_notes=f"Verified on {timestamp.isoformat()}",
    )


def _verify_contributions(args) -> int:
    contribs = contribution_registry.get_contributions(
        args.task_id, model_name=args.model
    )

    if not contribs:
        print(f"No contributions to verify for task: {args.task_id}")
        return 0

    task = contribution_registry.get_task(args.task_id)
    if not task:
        print(f"Task not found: {args.task_id}")
        return 1

    print(
        f"Verifying contributions for {args.task_id} (tolerance: {args.regression_tolerance:.1%})"
    )
    print("=" * 80)

    all_passed = True
    now = datetime.now()

    for c in contribs:
        if c.verified:
            print(f"✓ {c.model_name}: Already verified")
            continue

        issues: list[str] = []
        issues.extend(_check_minimum_performance(task, c))
        issues.extend(_check_regression_against_reference(c, args.regression_tolerance))

        if not issues:
            verified_contrib = _create_verified_contribution(c, now)
            contribution_registry.add_contribution(verified_contrib)
            contribution_registry._save_async()
            print(f"✓ {c.model_name}: PASSED (verified)")
        else:
            all_passed = False
            print(f"✗ {c.model_name}: FAILED")
            for issue in issues:
                print(f"    - {issue}")

    return 0 if all_passed else 1


def _leaderboard(args) -> int:
    lb = Leaderboard(
        args.task_id,
        primary_metric=args.metric,
        higher_is_better=not args.lower_better,
        registry=contribution_registry,
    )

    entries = lb.build(
        include_references=not args.no_references,
        include_contributions=not args.no_contributions,
        verified_only=not args.unverified,
    )

    if args.format == "json":
        output = [
            {
                "rank": e.rank,
                "model_name": e.model_name,
                "model_config": e.model_config,
                "primary_metric": e.primary_metric,
                "primary_value": e.primary_value,
                "all_metrics": e.all_metrics,
                "source": "reference"
                if e.reference
                else (
                    "verified"
                    if e.contribution and e.contribution.verified
                    else "contribution"
                ),
            }
            for e in entries
        ]
        result = {
            "task_id": args.task_id,
            "primary_metric": args.metric,
            "entries": output,
        }
        if args.output:
            Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
            print(f"Leaderboard saved to {args.output}")
        else:
            print(json.dumps(result, indent=2))
    elif args.format == "html":
        html = lb.to_html(entries, top_k=args.top)
        if args.output:
            Path(args.output).write_text(html, encoding="utf-8")
            print(f"Leaderboard saved to {args.output}")
        else:
            print(html)
    else:
        table = lb.to_table(entries, top_k=args.top)
        if args.output:
            Path(args.output).write_text(table, encoding="utf-8")
            print(f"Leaderboard saved to {args.output}")
        else:
            print(table)

    return 0


def _export(args) -> int:
    if args.task:
        tasks = [contribution_registry.get_task(args.task)]
        if not tasks[0]:
            print(f"Task not found: {args.task}")
            return 1
    else:
        tasks = contribution_registry.list_tasks()

    output = {}
    for task in tasks:
        if not task:
            continue
        refs = contribution_registry.get_reference_results(task.task_id)
        contribs = contribution_registry.get_contributions(task.task_id)

        output[task.task_id] = {
            "task": {
                "task_id": task.task_id,
                "name": task.name,
                "description": task.description,
                "domain": task.domain,
                "difficulty": task.difficulty,
                "tags": list(task.tags),
                "reference_metrics": task.reference_metrics,
                "regression_tolerance": task.regression_tolerance,
                "min_performance": task.min_performance,
            },
            "references": [
                {
                    "model_name": r.model_name,
                    "model_config": r.model_config,
                    "metrics": r.metrics,
                    "n_seeds": r.n_seeds,
                    "seed_values": list(r.seed_values),
                    "commit_sha": r.commit_sha,
                    "timestamp": r.timestamp,
                    "hardware": r.hardware,
                    "runtime_seconds": r.runtime_seconds,
                }
                for r in refs
            ],
            "contributions": [
                {
                    "contribution_id": c.contribution_id,
                    "model_name": c.model_name,
                    "model_config": c.model_config,
                    "metrics": c.metrics,
                    "reference_comparison": c.reference_comparison,
                    "n_seeds": c.n_seeds,
                    "seed_values": list(c.seed_values),
                    "contributor": c.contributor,
                    "commit_sha": c.commit_sha,
                    "timestamp": c.timestamp,
                    "hardware": c.hardware,
                    "runtime_seconds": c.runtime_seconds,
                    "verified": c.verified,
                    "verification_notes": c.verification_notes,
                }
                for c in contribs
            ],
        }

    Path(args.output).write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Exported {len(output)} tasks to {args.output}")
    return 0


def _dispatch_command(args, parser: argparse.ArgumentParser) -> int:
    commands = {
        "list-tasks": _list_tasks,
        "show-task": _show_task,
        "list-references": _list_references,
        "list-contributions": _list_contributions,
        "submit": _submit_contribution,
        "verify": _verify_contributions,
        "leaderboard": _leaderboard,
        "export": _export,
    }

    handler = commands.get(args.subcommand)
    if handler is None:
        print(f"Unknown subcommand: {args.subcommand}")
        parser.print_help()
        return 1

    return handler(args)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.subcommand:
        parser.print_help()
        return 1

    return _dispatch_command(args, parser)


if __name__ == "__main__":
    raise SystemExit(main())
