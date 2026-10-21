"""The surface CLI's statistics, Pareto, and diff commands."""

from __future__ import annotations

import json
import math
import statistics
from pathlib import Path
from typing import TYPE_CHECKING

from computronium.core.logging import get_logger
from computronium.experiment.surface.report import (
    ReportGenerator,
)

from ._execution import _open_store

if TYPE_CHECKING:
    import argparse

logger = get_logger()


def _cmd_stats(args: argparse.Namespace) -> int:  # ruff: ignore[complex-structure, too-many-branches, too-many-locals, too-many-statements]
    """Compute summary statistics for run metrics."""
    import statistics
    from collections import defaultdict

    store = _open_store(args.store)
    if store is None:
        return 1
    with store:
        run_id = args.run_id or store.latest_run_id()
        if run_id is None:
            logger.error("No runs found in store")
            return 1

        records = list(store.query_records(run_id=run_id))
        if not records:
            logger.error(f"No records for run {run_id}")
            return 1

        metrics = [m.strip() for m in args.metrics.split(",")]
        aggs = [a.strip() for a in args.agg.split(",")]
        group_by = (
            [g.strip() for g in args.group_by.split(",")] if args.group_by else []
        )

        # Group records
        groups: dict[tuple, list] = defaultdict(list)
        for r in records:
            key = tuple(getattr(r, axis) for axis in group_by) if group_by else ("all",)
            groups[key].append(r)

        # Compute statistics per group
        results = []
        group_keys = list(groups.keys())
        for key, group_records in groups.items():
            row = {}
            if group_by:
                for axis, val in zip(group_by, key):
                    row[axis] = val
            row["count"] = len(group_records)

            for metric in metrics:
                vals = [
                    r.payload.get(metric)
                    for r in group_records
                    if r.payload.get(metric) is not None
                ]
                if not vals:
                    continue
                vals = [float(v) for v in vals]
                row[f"{metric}_count"] = len(vals)
                if "mean" in aggs:
                    row[f"{metric}_mean"] = statistics.mean(vals)
                if "std" in aggs and len(vals) > 1:
                    row[f"{metric}_std"] = statistics.stdev(vals)
                if "min" in aggs:
                    row[f"{metric}_min"] = min(vals)
                if "max" in aggs:
                    row[f"{metric}_max"] = max(vals)
                if "median" in aggs:
                    row[f"{metric}_median"] = statistics.median(vals)
                if "ci95" in aggs and len(vals) > 1:
                    # 95% CI using t-distribution approximation
                    import math

                    se = statistics.stdev(vals) / math.sqrt(len(vals))
                    t_val = 1.96  # Approximate for large n
                    row[f"{metric}_ci95_low"] = statistics.mean(vals) - t_val * se
                    row[f"{metric}_ci95_high"] = statistics.mean(vals) + t_val * se

            results.append(row)

        # Compute effect sizes between groups when group_by is specified
        if group_by and len(group_keys) >= 2:
            from computronium.core.statistics import cliffs_delta, cohens_d

            # Compare first group (reference) against all others
            reference_key = group_keys[0]
            reference_records = groups[reference_key]
            for metric in metrics:
                ref_vals = [
                    r.payload.get(metric)
                    for r in reference_records
                    if r.payload.get(metric) is not None
                ]
                if not ref_vals:
                    continue
                ref_vals = [float(v) for v in ref_vals]

                for other_key in group_keys[1:]:
                    other_records = groups[other_key]
                    other_vals = [
                        r.payload.get(metric)
                        for r in other_records
                        if r.payload.get(metric) is not None
                    ]
                    if not other_vals:
                        continue
                    other_vals = [float(v) for v in other_vals]

                    # Compute effect sizes
                    try:
                        d = cohens_d(ref_vals, other_vals)
                        row_key = f"{metric}_cohens_d_vs_{'_'.join(str(v) for v in other_key)}"
                        for r in results:
                            if all(
                                r.get(axis) == val
                                for axis, val in zip(group_by, other_key)
                            ):
                                r[row_key] = d
                                break
                    except ValueError:
                        pass

                    try:
                        delta = cliffs_delta(ref_vals, other_vals)
                        row_key = f"{metric}_cliffs_delta_vs_{'_'.join(str(v) for v in other_key)}"
                        for r in results:
                            if all(
                                r.get(axis) == val
                                for axis, val in zip(group_by, other_key)
                            ):
                                r[row_key] = delta
                                break
                    except ValueError:
                        pass

        # Output
        if args.format == "json":
            output = json.dumps(results, indent=2, default=str)
        elif args.format == "csv":
            import csv
            import io

            output_io = io.StringIO()
            if results:
                writer = csv.DictWriter(output_io, fieldnames=sorted(results[0].keys()))
                writer.writeheader()
                writer.writerows(results)
            output = output_io.getvalue()
        elif results:
            headers = sorted(results[0].keys())
            col_widths = {
                h: max([len(h), *(len(str(r.get(h, ""))) for r in results)])
                for h in headers
            }
            header_line = " | ".join(h.ljust(col_widths[h]) for h in headers)
            sep_line = "-+-".join("-" * col_widths[h] for h in headers)
            lines = [header_line, sep_line]
            for r in results:
                lines.append(
                    " | ".join(str(r.get(h, "")).ljust(col_widths[h]) for h in headers)
                )
            output = "\n".join(lines)
        else:
            output = "(no data)"

        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            logger.info(f"Stats written to {args.output}")
        else:
            print(output)
        return 0


def _cmd_pareto(args: argparse.Namespace) -> int:  # ruff: ignore[complex-structure, too-many-branches, too-many-locals, too-many-nested-blocks, too-many-return-statements, too-many-statements]
    """Export Pareto frontier points for plotting."""
    store = _open_store(args.store)
    if store is None:
        return 1
    with store:
        run_id = args.run_id or store.latest_run_id()
        if run_id is None:
            logger.error("No runs found in store")
            return 1

        generator = ReportGenerator(store)
        objectives = tuple(o.strip() for o in args.objectives.split(","))
        if len(objectives) < 2:
            logger.error("Need at least 2 objectives for Pareto frontier")
            return 1

        maximize = None
        if args.maximize:
            maximize = tuple(
                m.strip().lower() == "true" for m in args.maximize.split(",")
            )
            if len(maximize) != len(objectives):
                logger.error("Maximize flags must match objectives count")
                return 1

        weights = None
        if args.weights:
            weights = tuple(float(w.strip()) for w in args.weights.split(","))
            if len(weights) != len(objectives):
                logger.error("Weights count must match objectives count")
                return 1

        # Use all records for Pareto frontier (not just claim-eligible)
        records = list(store.query_records(run_id=run_id))
        from computronium.experiment.surface.report import _directions

        maximize = maximize or _directions(objectives)
        pareto_points = generator._pareto_subset(records, objectives, maximize)
        if not pareto_points:
            logger.warning("No Pareto points found")
            pareto_points = []

        # Convert to flat rows
        rows = []
        for p in pareto_points:
            row = {
                "record_id": p["record_id"],
                "cell_key": p["cell_key"],
                **p["objectives"],
                **p["coordinate"],
            }
            rows.append(row)

        # Add weighted scalarization if requested
        if args.scalarize:
            if weights is None:
                logger.error("--scalarize requires --weights")
                return 1
            import math

            # Normalize objectives and compute weighted scores for ALL records
            all_records = list(store.query_records(run_id=run_id))
            if not all_records:
                logger.warning("No records to scalarize")
            else:
                # Extract objective values
                obj_values = {obj: [] for obj in objectives}
                for r in all_records:
                    for obj in objectives:
                        val = r.payload.get(obj)
                        if val is not None:
                            obj_values[obj].append(float(val))
                        else:
                            obj_values[obj].append(float("nan"))

                # Compute min/max for normalization
                obj_min = {}
                obj_max = {}
                for obj in objectives:
                    vals = [v for v in obj_values[obj] if not math.isnan(v)]
                    if vals:
                        obj_min[obj] = min(vals)
                        obj_max[obj] = max(vals)
                    else:
                        obj_min[obj] = 0.0
                        obj_max[obj] = 1.0

                # Compute scalarized scores
                scores = []
                for i, r in enumerate(all_records):
                    score = 0.0
                    for obj, weight in zip(objectives, weights):
                        val = r.payload.get(obj)
                        if val is None or math.isnan(float(val)):
                            score = float("nan")
                            break
                        v = float(val)
                        # Normalize to [0, 1] based on direction
                        if maximize[objectives.index(obj)]:
                            # Maximize: higher is better
                            if obj_max[obj] > obj_min[obj]:
                                norm = (v - obj_min[obj]) / (
                                    obj_max[obj] - obj_min[obj]
                                )
                            else:
                                norm = 0.5
                        # Minimize: lower is better
                        elif obj_max[obj] > obj_min[obj]:
                            norm = (obj_max[obj] - v) / (obj_max[obj] - obj_min[obj])
                        else:
                            norm = 0.5
                        score += weight * norm
                    scores.append(score)

                # Add scores to pareto rows (by matching record_id)
                score_by_id = {r.record_id: s for r, s in zip(all_records, scores)}
                for row in rows:
                    row["scalarized_score"] = score_by_id.get(
                        row["record_id"], float("nan")
                    )

                # Sort pareto points by scalarized score (descending = better)
                rows.sort(
                    key=lambda x: x.get("scalarized_score", float("-inf")), reverse=True
                )
                for i, row in enumerate(rows):
                    row["scalarized_rank"] = i + 1

        if args.format == "json":
            output = json.dumps(rows, indent=2, default=str)
        else:  # csv
            import csv
            import io

            output_io = io.StringIO()
            if rows:
                writer = csv.DictWriter(output_io, fieldnames=sorted(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)
            output = output_io.getvalue()

        Path(args.output).write_text(output, encoding="utf-8")
        logger.info(f"Pareto frontier ({len(rows)} points) written to {args.output}")
        return 0


def _cmd_diff(args: argparse.Namespace) -> int:  # ruff: ignore[complex-structure, too-many-branches, too-many-locals, too-many-statements]
    """Compare two runs statistically."""
    from scipy import stats

    store = _open_store(args.store)
    if store is None:
        return 1
    with store:
        generator = ReportGenerator(store)

        for run_id in [args.run_id_a, args.run_id_b]:
            if not generator.run_summary(run_id):
                logger.error(f"Run {run_id} not found")
                return 1

        metrics = [m.strip() for m in args.metrics.split(",")]

        # Get claim-eligible records for both runs
        records_a = generator.claim_eligible_records(args.run_id_a)
        records_b = generator.claim_eligible_records(args.run_id_b)

        if not records_a or not records_b:
            logger.warning(
                "One or both runs have no claim-eligible records, using all records"
            )
            records_a = generator._store.query_records(run_id=args.run_id_a)
            records_b = generator._store.query_records(run_id=args.run_id_b)

        results = {}
        for metric in metrics:
            vals_a: list[float] = [
                float(r.payload[metric])
                for r in records_a
                if metric in r.payload and r.payload[metric] is not None
            ]
            vals_b: list[float] = [
                float(r.payload[metric])
                for r in records_b
                if metric in r.payload and r.payload[metric] is not None
            ]

            # Compute statistics
            mean_a, mean_b = statistics.mean(vals_a), statistics.mean(vals_b)
            std_a = statistics.stdev(vals_a) if len(vals_a) > 1 else 0
            std_b = statistics.stdev(vals_b) if len(vals_b) > 1 else 0

            # Statistical test
            p_value = None
            effect_size = None
            try:  # ruff: ignore[too-many-statements-in-try-clause]
                if args.test == "ttest":
                    _stat, p_value = stats.ttest_ind(vals_a, vals_b, equal_var=False)
                    # Cohen's d
                    pooled_std = (
                        math.sqrt((std_a**2 + std_b**2) / 2)
                        if (std_a > 0 or std_b > 0)
                        else 1
                    )
                    effect_size = (mean_a - mean_b) / pooled_std
                elif args.test == "wilcoxon":
                    if len(vals_a) == len(vals_b):
                        _stat, p_value = stats.wilcoxon(vals_a, vals_b)
                    else:
                        p_value = None
                elif args.test == "mannwhitney":
                    _stat, p_value = stats.mannwhitneyu(
                        vals_a, vals_b, alternative="two-sided"
                    )
                    # Cliff's delta
                    n_a, n_b = len(vals_a), len(vals_b)
                    pairs = [(a, b) for a in vals_a for b in vals_b]
                    greater = sum(1 for a, b in pairs if a > b)
                    less = sum(1 for a, b in pairs if a < b)
                    effect_size = (greater - less) / (n_a * n_b) if n_a * n_b > 0 else 0
            except Exception as e:
                logger.warning(f"Statistical test failed for {metric}: {e}")

            # Extract p-value from tuple if needed
            p_val: float | None = (
                float(p_value[1])  # type: ignore[arg-type]
                if isinstance(p_value, tuple)
                else (float(p_value) if p_value is not None else None)  # type: ignore[arg-type]
            )

            results[metric] = {
                "run_a": {"mean": mean_a, "std": std_a, "count": len(vals_a)},
                "run_b": {"mean": mean_b, "std": std_b, "count": len(vals_b)},
                "mean_diff": mean_a - mean_b,
                "p_value": p_val,
                "effect_size": effect_size,
                "test": args.test,
                "significant": p_val is not None and p_val < 0.05,
            }

        output_data = {
            "run_a": args.run_id_a,
            "run_b": args.run_id_b,
            "comparisons": results,
        }

        if args.format == "json":
            output = json.dumps(output_data, indent=2, default=str)
        else:  # table
            lines = [f"Diff: {args.run_id_a} vs {args.run_id_b}"]
            for metric, comp in results.items():
                if "error" in comp:
                    lines.append(f"  {metric}: {comp['error']}")
                    continue
                lines.append(
                    f"  {metric}: A={comp['run_a']['mean']:.4g}±{comp['run_a']['std']:.4g} "
                    f"B={comp['run_b']['mean']:.4g}±{comp['run_b']['std']:.4g} "
                    f"Δ={comp['mean_diff']:.4g} p={comp['p_value']} d={comp['effect_size']} "
                    f"{'*' if comp['significant'] else ''}"
                )
            output = "\n".join(lines)

        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            logger.info(f"Diff written to {args.output}")
        else:
            print(output)
        return 0
