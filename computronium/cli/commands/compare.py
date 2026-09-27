"""Compare commands for the CLI."""

import csv
from pathlib import Path
from typing import TYPE_CHECKING

from computronium.cli.shared import logger

if TYPE_CHECKING:
    import argparse

__all__ = ["add_compare_subparsers", "run_compare"]


def add_compare_subparsers(subparsers: argparse._SubParsersAction) -> None:
    """Add compare subparser."""
    compare_parser = subparsers.add_parser(
        "compare", help="Rank credit types from completed HPO studies into a CSV"
    )
    compare_parser.add_argument(
        "--studies",
        required=False,
        default="",
        help="Comma-separated study names (e.g. thermodynamic_contrast_digits_eqprop_mlp,random_projections_digits_fa_mlp). "
        "If empty, --credit/--task are used to discover studies.",
    )
    compare_parser.add_argument(
        "--credit",
        help="Glob studies for this credit assignment type (used when --studies omitted)",
    )
    compare_parser.add_argument(
        "--task",
        help="Task suffix to match when globbing via --credit",
    )
    compare_parser.add_argument(
        "--metric",
        default="accuracy",
        choices=["accuracy", "loss", "param_efficiency"],
        help="Ranking metric",
    )
    compare_parser.add_argument("--output", required=True, help="Output CSV path")
    compare_parser.add_argument(
        "--db",
        dest="db",
        help="SQLite DB file containing the studies (default: computronium.db)",
    )


def run_compare(args: argparse.Namespace) -> None:
    """Rank credit types from completed HPO studies into a CSV."""
    from computronium.cli.shared import _DB_PATH, _STORAGE_URL, _set_storage
    from computronium.hyperopt.comparison import compute_algorithm_rankings

    if getattr(args, "db", None):
        _DB_PATH, _STORAGE_URL = _set_storage(args.db)  # ruff: ignore[used-dummy-variable]

    study_names = []
    if args.studies:
        study_names = [s.strip() for s in args.studies.split(",") if s.strip()]
    else:
        # Discover studies from storage
        from computronium.hyperopt.storage import list_studies

        all_studies = list_studies(_STORAGE_URL)
        if args.credit:
            all_studies = [s for s in all_studies if args.credit in s]
        if args.task:
            all_studies = [s for s in all_studies if args.task in s]
        study_names = all_studies

    if not study_names:
        logger.warning("No studies found to compare")
        return

    logger.info("Comparing %d studies", len(study_names))
    rankings = compute_algorithm_rankings(
        study_names, metric=args.metric, storage=_STORAGE_URL
    )

    # Write CSV
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.output).open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "rank",
            "study",
            "model",
            "credit_type",
            "task",
            "value",
            "n_trials",
        ])
        for i, row in enumerate(rankings, 1):
            writer.writerow([
                i,
                row["study"],
                row["model"],
                row.get("credit_type", row.get("family", "")),
                row["task"],
                row["value"],
                row["n_trials"],
            ])

    logger.info("Comparison written to %s", args.output)
