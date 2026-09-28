"""Joint Campaign CLI (``comp campaign``).

Runs and manages 6-D joint architecture campaigns with:
- Campaign persistence (SQLite + YAML)
- Kernel caching
- Fault tolerance checkpointing
- AutoScientist integration
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="comp campaign",
        description="Run and manage 6-D joint architecture campaigns",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Campaign subcommand")

    # run
    run_parser = subparsers.add_parser("run", help="Run a campaign")
    run_parser.add_argument(
        "--space",
        required=True,
        help="Search space name (e.g., joint_smoke, joint_full)",
    )
    run_parser.add_argument(
        "--objective",
        required=True,
        help="Objective to optimize (e.g., adaptation_efficiency, stability, pareto)",
    )
    run_parser.add_argument("--branch", default="main", help="Branch name")
    run_parser.add_argument(
        "--campaign-id", help="Campaign ID (auto-generated if not provided)"
    )
    run_parser.add_argument(
        "--iterations", type=int, default=10, help="Number of iterations"
    )
    run_parser.add_argument(
        "--experiments-per-iter", type=int, default=5, help="Experiments per iteration"
    )
    run_parser.add_argument(
        "--output-dir", default="campaigns", help="Output directory"
    )
    run_parser.add_argument("--db", help="SQLite database path")
    run_parser.add_argument(
        "--checkpoint-interval",
        type=int,
        default=5,
        help="Checkpoint interval (episodes)",
    )
    run_parser.add_argument(
        "--device",
        default="auto",
        help="Episode execution device ('auto' = best available backend)",
    )
    run_parser.add_argument("--seed", type=int, default=0, help="Base RNG seed")
    run_parser.add_argument(
        "--layout",
        choices=["random", "grid"],
        default="random",
        help="Coordinate proposal: random sampling from the space, or a "
        "deterministic round-robin traversal of its full grid (multi-seed "
        "replication runs share the identical grid)",
    )
    run_parser.add_argument(
        "--tasks",
        default="synthetic",
        help="Comma-separated task-family labels rotated across episodes "
        "(drives replication grouping; supported batch families: "
        "synthetic, parity)",
    )
    run_parser.add_argument(
        "--resume", action="store_true", help="Resume from latest checkpoint"
    )
    run_parser.add_argument(
        "--dry-run", action="store_true", help="Propose without executing"
    )

    # status
    status_parser = subparsers.add_parser("status", help="Show campaign status")
    status_parser.add_argument("--campaign-id", required=True, help="Campaign ID")
    status_parser.add_argument("--db", help="SQLite database path")

    # list
    list_parser = subparsers.add_parser("list", help="List campaigns")
    list_parser.add_argument("--branch", help="Filter by branch")
    list_parser.add_argument("--db", help="SQLite database path")

    # compare
    compare_parser = subparsers.add_parser("compare", help="Compare campaigns")
    compare_parser.add_argument("--campaign-a", required=True, help="First campaign ID")
    compare_parser.add_argument(
        "--campaign-b", required=True, help="Second campaign ID"
    )
    compare_parser.add_argument("--db", help="SQLite database path")

    # checkpoint
    checkpoint_parser = subparsers.add_parser("checkpoint", help="Manage checkpoints")
    checkpoint_subparsers = checkpoint_parser.add_subparsers(
        dest="checkpoint_action", help="Checkpoint action"
    )

    checkpoint_list = checkpoint_subparsers.add_parser("list", help="List checkpoints")
    checkpoint_list.add_argument("--campaign-id", required=True, help="Campaign ID")
    checkpoint_list.add_argument(
        "--checkpoint-dir", default="campaigns/checkpoints", help="Checkpoint directory"
    )

    checkpoint_show = checkpoint_subparsers.add_parser(
        "show", help="Show checkpoint details"
    )
    checkpoint_show.add_argument(
        "--checkpoint", required=True, help="Checkpoint file path"
    )

    checkpoint_resume = checkpoint_subparsers.add_parser(
        "resume", help="Generate resume script"
    )
    checkpoint_resume.add_argument(
        "--checkpoint", required=True, help="Checkpoint file path"
    )
    checkpoint_resume.add_argument("--output", help="Output script path")

    # export
    export_parser = subparsers.add_parser("export", help="Export campaign data")
    export_parser.add_argument("--campaign-id", required=True, help="Campaign ID")
    export_parser.add_argument(
        "--format", choices=["json", "csv", "yaml"], default="json"
    )
    export_parser.add_argument("--output", help="Output file path")
    export_parser.add_argument("--db", help="SQLite database path")

    # report (commissioned campaigns - R5b-F Stage 1)
    report_parser = subparsers.add_parser(
        "report",
        help="Render the static discovery report (HTML + JSON, R5b-F Stage 1)",
    )
    report_parser.add_argument(
        "--campaign-dir",
        required=True,
        help="Commissioned campaign directory containing records/episodes.json",
    )
    report_parser.add_argument(
        "--metric", default="task_accuracy", help="Attribution metric"
    )
    report_parser.add_argument(
        "--output-dir",
        help="Output directory (default: <campaign-dir>/records)",
    )

    # kb-report (continuous discovery campaigns - TODO40 P1.1)
    kb_report_parser = subparsers.add_parser(
        "kb-report",
        help="Render KB-based campaign report from continuous discovery (HTML + JSON)",
    )
    kb_report_parser.add_argument(
        "--root",
        type=Path,
        required=True,
        help="Continuous campaign root directory (contains kb.sqlite)",
    )
    kb_report_parser.add_argument(
        "--task", default="mnist", help="Task to filter (default: mnist)"
    )
    kb_report_parser.add_argument(
        "--objectives",
        default="accuracy,walltime_s,param_count",
        help="Comma-separated objectives for Pareto front",
    )
    kb_report_parser.add_argument(
        "--output-dir",
        help="Output directory (default: <root>/report)",
    )

    # diff (continuous discovery campaigns - TODO40 P1.3)
    diff_parser = subparsers.add_parser(
        "diff",
        help="Compare two continuous discovery campaign runs (KB roots)",
    )
    diff_parser.add_argument(
        "--root-a",
        type=Path,
        required=True,
        help="First campaign root directory",
    )
    diff_parser.add_argument(
        "--root-b",
        type=Path,
        required=True,
        help="Second campaign root directory",
    )
    diff_parser.add_argument(
        "--task", default="mnist", help="Task to filter (default: mnist)"
    )
    diff_parser.add_argument(
        "--objectives",
        default="accuracy,walltime_s,param_count",
        help="Comma-separated objectives for Pareto front",
    )
    diff_parser.add_argument(
        "--output",
        help="Output file (default: stdout)",
    )

    return parser


def _get_search_space(space_name: str) -> dict:
    """Get search space configuration."""
    spaces = {
        "joint_smoke": {
            "substrates": ["digital"],
            "geometries": ["feedforward", "recurrent"],
            "dynamics": ["energy_minimization", "instantaneous"],
            "plasticity": ["null", "routing", "fast_weights"],
            # thermodynamic_contrast excluded: contrastive settling credit x
            # instantaneous is R3.9-fenced; local_goodness composes on both
            # dynamics (its instantaneous pairings are quarantined by the
            # fidelity gate at attribution, not here).
            "credits": ["random_projections", "local_goodness"],
            "updates": ["euclidean"],
        },
        # 72-coordinate grid for commissioned replication campaigns (R5.1c):
        # all-digital, C/U-axis breadth, sized so a full two-pass traversal
        # (2 x len/epi iterations at epi=8) covers both task families per
        # coordinate per seed.
        "joint_grid": {
            "substrates": ["digital"],
            "geometries": ["feedforward", "recurrent"],
            "dynamics": ["energy_minimization", "instantaneous"],
            "plasticity": ["null", "routing", "fast_weights"],
            "credits": [
                "thermodynamic_contrast",
                "random_projections",
                "local_goodness",
            ],
            "updates": ["euclidean", "spectral_constrained"],
        },
        "joint_full": {
            "substrates": [
                "digital",
                "analog",
                "memristive",
                "neuromorphic",
                "ternary",
                "sparse",
            ],
            "geometries": ["feedforward", "recurrent", "tile_mesh"],
            "dynamics": [
                "energy_minimization",
                "instantaneous",
                "predictive_settling",
                "spike_integration",
                "diffusion",
            ],
            "plasticity": [
                "null",
                "routing",
                "fast_weights",
                "substrate_coupled",
                "rule_state",
            ],
            "credits": [
                "thermodynamic_contrast",
                "random_projections",
                "local_goodness",
                "temporal_trace",
                "target_inversion",
                "gradient",
            ],
            "updates": [
                "euclidean",
                "riemannian_orthogonal",
                "spectral_constrained",
                "mean_norm",
                "elastic_consolidation",
            ],
        },
    }
    # R5b-B: 48 fidelity-passing coordinates from R5.1c fidelity manifest
    if space_name == "joint_fidelity_48":
        coords_json = os.environ.get("R5B_B_FIDELITY_COORDS_JSON")
        if coords_json:
            coords = json.loads(coords_json)
            return {"_custom_grid": coords}
        # Fallback: return the full joint_grid (will be filtered by fidelity gate at attribution)
        return spaces["joint_grid"]
    return spaces.get(space_name, spaces["joint_smoke"])


def _space_sampler(space: dict):
    """Bind the CLI search-space table into a seeded coordinate sampler."""
    from computronium.core.campaign.stack import _space_sampler

    return _space_sampler(space)


def _layout_sampler(space: dict, layout: str, experiments_per_iter: int):
    """Resolve the --layout flag into a coordinate sampler."""
    if layout == "grid":
        from computronium.core.campaign.stack import grid_sampler, space_grid

        return grid_sampler(space_grid(space), experiments_per_iter)
    return _space_sampler(space)


def _run_campaign(args) -> int:
    """Run (or resume) a campaign via the shared CampaignStack engine."""
    from computronium.core.campaign.evaluation import (
        DEFAULT_INPUT_DIM,
        DEFAULT_NUM_CLASSES,
    )
    from computronium.core.campaign.stack import CampaignStack

    stack = CampaignStack(
        args.output_dir,
        branch=args.branch,
        checkpoint_interval=args.checkpoint_interval,
        db_path=args.db,
        seed=args.seed,
        device=args.device,
        on_event=print,
    )
    space = _get_search_space(args.space)
    result = stack.run_campaign(
        iterations=args.iterations,
        experiments_per_iter=args.experiments_per_iter,
        tasks=tuple(t.strip() for t in args.tasks.split(",") if t.strip()),
        sampler=_layout_sampler(space, args.layout, args.experiments_per_iter),
        campaign_id=args.campaign_id,
        resume=args.resume,
        dry_run=args.dry_run,
        build_kwargs={
            "input_dim": DEFAULT_INPUT_DIM,
            "output_dim": DEFAULT_NUM_CLASSES,
            "hidden_dims": (16,),
        },
        objective=args.objective,
    )

    print(f"\nCampaign {result.campaign_id} completed!")
    print(f"Results stored in: {result.db_path}")
    return 0


def _show_status(args) -> int:
    """Show campaign status."""
    from computronium.core.campaign import CampaignStore

    db_path = args.db or "campaigns/campaign.db"
    store = CampaignStore(db_path)

    campaign = store.get_campaign(args.campaign_id)
    if not campaign:
        print(f"Campaign {args.campaign_id} not found")
        return 1

    print(f"Campaign: {campaign.campaign_id}")
    print(f"Branch: {campaign.branch_name}")
    print(f"Parent: {campaign.parent_branch or 'None'}")
    print(f"Iteration: {campaign.iteration}")
    print(f"Created: {campaign.created_at}")
    print(f"Updated: {campaign.updated_at}")
    print(f"Config: {campaign.config}")
    print(f"Metadata: {campaign.metadata}")

    episodes = store.get_episodes(args.campaign_id)
    print(f"\nEpisodes: {len(episodes)}")
    for ep in episodes[-5:]:  # Show last 5
        fr = ep.frontier_record
        acc = fr.get("task_accuracy", 0)
        print(f"  Iter {ep.iteration}: {ep.coordinate} -> acc={acc:.4f}")

    return 0


def _list_campaigns(args) -> int:
    """List all campaigns."""
    from computronium.core.campaign import CampaignStore

    db_path = args.db or "campaigns/campaign.db"
    store = CampaignStore(db_path)

    campaigns = store.list_campaigns(args.branch)
    if not campaigns:
        print("No campaigns found")
        return 0

    print(f"{'Campaign ID':<15} {'Branch':<15} {'Iter':<6} {'Created':<20} {'Parent'}")
    print("-" * 80)
    for c in campaigns:
        parent = c.parent_branch or "-"
        print(
            f"{c.campaign_id:<15} {c.branch_name:<15} {c.iteration:<6} "
            f"{c.created_at:<20} {parent}"
        )

    return 0


def _compare_campaigns(args) -> int:
    """Compare two campaigns."""
    from computronium.core.campaign import CampaignStore

    db_path = args.db or "campaigns/campaign.db"
    store = CampaignStore(db_path)

    camp_a = store.get_campaign(args.campaign_a)
    camp_b = store.get_campaign(args.campaign_b)

    if not camp_a or not camp_b:
        print("One or both campaigns not found")
        return 1

    eps_a = store.get_episodes(args.campaign_a)
    eps_b = store.get_episodes(args.campaign_b)

    print(f"Campaign A: {camp_a.campaign_id} ({len(eps_a)} episodes)")
    print(f"Campaign B: {camp_b.campaign_id} ({len(eps_b)} episodes)")

    # Compare best results
    if eps_a and eps_b:
        best_a = max(eps_a, key=lambda e: e.frontier_record.get("task_accuracy", 0))
        best_b = max(eps_b, key=lambda e: e.frontier_record.get("task_accuracy", 0))

        fr_a = best_a.frontier_record
        fr_b = best_b.frontier_record

        print(
            f"\nBest A: {fr_a.get('task_accuracy', 0):.4f} acc, "
            f"{fr_a.get('task_loss', 0):.4f} loss"
        )
        print(
            f"Best B: {fr_b.get('task_accuracy', 0):.4f} acc, "
            f"{fr_b.get('task_loss', 0):.4f} loss"
        )

    return 0


def _manage_checkpoints(args) -> int:
    """Manage checkpoints."""
    from computronium.core.campaign.checkpoint import (
        CheckpointManager,
        create_resume_script,
    )

    checkpoint_dir = Path(args.checkpoint_dir)
    mgr = CheckpointManager(checkpoint_dir)

    if args.checkpoint_action == "list":
        checkpoints = mgr.list_checkpoints(args.campaign_id)
        if not checkpoints:
            print(f"No checkpoints found for campaign {args.campaign_id}")
            return 0

        print(f"Checkpoints for {args.campaign_id}:")
        for cp in checkpoints:
            print(f"  {cp.name} ({cp.stat().st_size} bytes)")

    elif args.checkpoint_action == "show":
        checkpoint = mgr.load_checkpoint(args.checkpoint)
        print(f"Checkpoint: {checkpoint.campaign_id}")
        print(f"  Episode: {checkpoint.episode_index}")
        print(f"  Branch: {checkpoint.branch_name}")
        print(f"  Timestamp: {checkpoint.timestamp}")
        print(f"  Coordinate: {checkpoint.coordinate}")
        print(f"  Task: {checkpoint.task_name}")
        print(f"  Composite state keys: {list(checkpoint.composite_state.keys())}")
        print(f"  Theta keys: {list(checkpoint.theta.keys())}")

    elif args.checkpoint_action == "resume":
        output = args.output or f"resume_{Path(args.checkpoint).stem}.sh"
        created = create_resume_script(args.checkpoint, output)
        print(f"Resume script created: {created}")

    return 0


def _export_campaign(args) -> int:
    """Export campaign data."""
    import csv
    import json

    from computronium.core.campaign import CampaignStore

    db_path = args.db or "campaigns/campaign.db"
    store = CampaignStore(db_path)

    campaign = store.get_campaign(args.campaign_id)
    if not campaign:
        print(f"Campaign {args.campaign_id} not found")
        return 1

    episodes = store.get_episodes(args.campaign_id)

    data = {
        "campaign": {
            "campaign_id": campaign.campaign_id,
            "branch_name": campaign.branch_name,
            "parent_branch": campaign.parent_branch,
            "iteration": campaign.iteration,
            "created_at": campaign.created_at,
            "updated_at": campaign.updated_at,
            "config": campaign.config,
            "metadata": campaign.metadata,
        },
        "episodes": [
            {
                "iteration": ep.iteration,
                "timestamp": ep.timestamp,
                "coordinate": ep.coordinate,
                "task_name": ep.task_name,
                "frontier_record": ep.frontier_record,
            }
            for ep in episodes
        ],
    }

    if args.format == "json":
        output = json.dumps(data, indent=2)
    elif args.format == "yaml":
        import yaml

        output = yaml.dump(data, default_flow_style=False)
    else:  # csv
        import io

        output_io = io.StringIO()
        if episodes:
            fieldnames = ["iteration", "timestamp", "coordinate", "task_name"]
            # Add frontier record fields
            sample_fr = episodes[0].frontier_record
            for key in sample_fr:
                fieldnames.append(f"fr_{key}")

            writer = csv.DictWriter(output_io, fieldnames=fieldnames)
            writer.writeheader()
            for ep in episodes:
                row = {
                    "iteration": ep.iteration,
                    "timestamp": ep.timestamp,
                    "coordinate": ep.coordinate,
                    "task_name": ep.task_name,
                }
                for k, v in ep.frontier_record.items():
                    row[f"fr_{k}"] = v
                writer.writerow(row)
        output = output_io.getvalue()

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Exported to {args.output}")
    else:
        print(output)

    return 0


def _render_discovery_report(args) -> int:
    """Render the static discovery report from a commissioned campaign."""
    from computronium.core.campaign.report import (
        build_discovery_report,
        load_campaign_records,
    )

    records, fidelity = load_campaign_records(args.campaign_dir)
    report = build_discovery_report(records, metric=args.metric, fidelity=fidelity)
    out_dir = Path(args.output_dir or (Path(args.campaign_dir) / "records"))
    json_path, html_path = report.write(out_dir)
    print(
        f"discovery report over {report.n_records} records "
        f"({report.n_coordinates} coordinates) -> {json_path} + {html_path}"
    )
    return 0


def _render_kb_report(args) -> int:
    """Render the KB-based campaign report from continuous discovery."""
    from computronium.core.campaign.kb_report import build_kb_report

    objectives = [o.strip() for o in args.objectives.split(",") if o.strip()]
    report = build_kb_report(args.root, task=args.task, objectives=objectives)
    out_dir = Path(args.output_dir or (args.root / "report"))
    json_path, html_path = report.write(out_dir)
    print(
        f"KB campaign report: {len(report.pareto_front)} Pareto points, "
        f"{report.kb_stats.get('total_experiments', 0)} experiments, "
        f"{report.kb_stats.get('total_voids', 0)} voids -> {json_path} + {html_path}"
    )
    return 0


# --- Diff helpers --------------------------------------------------------------


def _get_all_cell_keys(root: Path, task: str) -> set[str]:
    """Get all viable cell keys from KB experiments."""
    import sqlite3

    from computronium.core.campaign.kb_report import _build_per_cell_best

    kb_path = root / "kb.sqlite"
    if not kb_path.exists():
        return set()
    conn = sqlite3.connect(kb_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM knowledge WHERE topic LIKE ? AND source = 'experiment'",
        (f"experiment:{task}",),
    ).fetchall()
    conn.close()
    cells = _build_per_cell_best(rows)
    return {c["key"] for c in cells}


def _diff_summary_stats(report_a, report_b) -> list[str]:
    """Diff summary statistics."""
    lines = ["1. SUMMARY STATS", "-" * 40]
    stats_a = report_a.kb_stats
    stats_b = report_b.kb_stats
    for key in ["total_entries", "total_experiments", "total_voids"]:
        val_a = stats_a.get(key, 0)
        val_b = stats_b.get(key, 0)
        delta = val_b - val_a
        sign = "+" if delta > 0 else ""
        lines.append(f"  {key}: {val_a} -> {val_b} ({sign}{delta})")
    lines.append(
        f"  Pareto front size: {len(report_a.pareto_front)} -> {len(report_b.pareto_front)} "
        f"({'+' if len(report_b.pareto_front) > len(report_a.pareto_front) else ''}"
        f"{len(report_b.pareto_front) - len(report_a.pareto_front)})"
    )
    lines.append("")
    return lines


def _diff_viable_cells(report_a, report_b, args) -> list[str]:
    """Diff viable cells."""
    lines = ["2. NEW VIABLE CELLS (in B, not in A)", "-" * 40]
    cells_a = _get_all_cell_keys(args.root_a, args.task)
    cells_b = _get_all_cell_keys(args.root_b, args.task)
    new_cells = cells_b - cells_a
    removed_cells = cells_a - cells_b

    if new_cells:
        lines.append(f"  New cells in B: {len(new_cells)}")
        for key in sorted(new_cells)[:10]:
            lines.append(f"    + {key}")
        if len(new_cells) > 10:
            lines.append(f"    ... and {len(new_cells) - 10} more")
    else:
        lines.append("  No new cells")

    if removed_cells:
        lines.append(f"  Cells removed: {len(removed_cells)}")
        for key in sorted(removed_cells)[:5]:
            lines.append(f"    - {key}")
    lines.append("")
    return lines


def _diff_pareto_front(report_a, report_b) -> list[str]:
    """Diff Pareto front changes."""
    keys_a = {p.key for p in report_a.pareto_front}
    keys_b = {p.key for p in report_b.pareto_front}
    front_new = keys_b - keys_a
    front_lost = keys_a - keys_b
    front_common = keys_a & keys_b

    lines = ["3. PARETO FRONT CHANGES", "-" * 40]
    lines.extend(
        _format_front_section("New on front", front_new, report_b.pareto_front, "+")
    )
    lines.extend(
        _format_front_section("Lost from front", front_lost, report_a.pareto_front, "-")
    )
    lines.extend(_format_common_front_changes(front_common, report_a, report_b))
    lines.append("")
    return lines


def _format_front_section(
    title: str, keys: set[str], front: list, prefix: str
) -> list[str]:
    """Format a front section (new/lost)."""
    lines = []
    if keys:
        lines.append(f"  {title}: {len(keys)}")
        for key in sorted(keys):
            pt = next((p for p in front if p.key == key), None)
            if pt:
                lines.append(
                    f"    {prefix} {key} (acc={pt.accuracy:.3f}, walltime={pt.walltime_s:.1f}s, params={pt.param_count:,})"
                )
    else:
        lines.append(f"  No {title.lower()}")
    return lines


def _format_common_front_changes(keys: set[str], report_a, report_b) -> list[str]:
    """Format changes for common front cells."""
    lines = []
    if not keys:
        return lines
    lines.append(f"  Common front cells: {len(keys)}")
    for key in sorted(keys):
        pt_a = next((p for p in report_a.pareto_front if p.key == key), None)
        pt_b = next((p for p in report_b.pareto_front if p.key == key), None)
        if pt_a and pt_b:
            acc_diff = pt_b.accuracy - pt_a.accuracy
            wt_diff = pt_b.walltime_s - pt_a.walltime_s
            if abs(acc_diff) > 0.001 or abs(wt_diff) > 0.1:
                lines.append(
                    f"    ~ {key}: acc {pt_a.accuracy:.3f}->{pt_b.accuracy:.3f} ({acc_diff:+.3f}), "
                    f"walltime {pt_a.walltime_s:.1f}->{pt_b.walltime_s:.1f}s ({wt_diff:+.1f}s)"
                )
    return lines


def _diff_voids(report_a, report_b) -> list[str]:
    """Diff structural voids."""
    lines = ["4. STRUCTURAL VOIDS", "-" * 40]
    void_cats_a = {v.category: v.count for v in report_a.voids}
    void_cats_b = {v.category: v.count for v in report_b.voids}
    all_cats = set(void_cats_a.keys()) | set(void_cats_b.keys())
    for cat in sorted(all_cats):
        count_a = void_cats_a.get(cat, 0)
        count_b = void_cats_b.get(cat, 0)
        delta = count_b - count_a
        if delta != 0:
            sign = "+" if delta > 0 else ""
            lines.append(f"  {cat}: {count_a} -> {count_b} ({sign}{delta})")
    lines.append("")
    return lines


def _diff_clamps(report_a, report_b) -> list[str]:
    """Diff energy clamp frequency."""
    lines = ["5. ENERGY CLAMP FREQUENCY CHANGES", "-" * 40]
    clamps_a = {(c.dynamics, c.credit, c.update): c for c in report_a.clamps}
    clamps_b = {(c.dynamics, c.credit, c.update): c for c in report_b.clamps}
    all_triples = set(clamps_a.keys()) | set(clamps_b.keys())

    clamp_changes = []
    for triple in sorted(all_triples):
        ca = clamps_a.get(triple)
        cb = clamps_b.get(triple)
        if ca and cb:
            rate_diff = cb.clamp_rate - ca.clamp_rate
            if abs(rate_diff) > 0.01:
                clamp_changes.append((triple, ca, cb, rate_diff))
        elif cb and not ca:
            clamp_changes.append((triple, None, cb, cb.clamp_rate))

    if clamp_changes:
        for triple, ca, cb, rate_diff in sorted(
            clamp_changes, key=lambda x: -abs(x[3])
        )[:10]:
            dynamics, credit, update = triple
            if ca:
                lines.append(
                    f"  {dynamics}|{credit}|{update}: {ca.clamp_rate:.1%} -> {cb.clamp_rate:.1%} "
                    f"({rate_diff:+.1%}) [{ca.total_cells}->{cb.total_cells} cells]"
                )
            else:
                lines.append(
                    f"  {dynamics}|{credit}|{update}: NEW - {cb.clamp_rate:.1%} "
                    f"[{cb.total_cells} cells]"
                )
    else:
        lines.append("  No significant clamp frequency changes")
    lines.append("")
    return lines


def _diff_walltimes(report_a, report_b) -> list[str]:
    """Diff walltime by dynamics family."""
    lines = ["6. WALLTIME CHANGES BY DYNAMICS FAMILY", "-" * 40]
    wt_a = {w.dynamics: w for w in report_a.walltimes}
    wt_b = {w.dynamics: w for w in report_b.walltimes}
    all_dyn = set(wt_a.keys()) | set(wt_b.keys())

    for dyn in sorted(all_dyn):
        wa = wt_a.get(dyn)
        wb = wt_b.get(dyn)
        if wa and wb:
            mean_diff = wb.mean_walltime_s - wa.mean_walltime_s
            if abs(mean_diff) > 0.5:
                sign = "+" if mean_diff > 0 else ""
                lines.append(
                    f"  {dyn}: {wa.mean_walltime_s:.1f}s -> {wb.mean_walltime_s:.1f}s "
                    f"({sign}{mean_diff:.1f}s) [{wa.cells}->{wb.cells} cells]"
                )
        elif wb and not wa:
            lines.append(f"  {dyn}: NEW - {wb.mean_walltime_s:.1f}s [{wb.cells} cells]")
    lines.append("")
    return lines


def _diff_maturation(report_a, report_b) -> list[str]:
    """Diff maturation pipeline."""
    lines = ["7. MATURATION PIPELINE", "-" * 40]
    m_a, m_b = report_a.maturation, report_b.maturation
    lines.append(
        f"  L0: {m_a.l0_cells} -> {m_b.l0_cells} ({m_b.l0_cells - m_a.l0_cells:+d})"
    )
    lines.append(
        f"  L1: {m_a.l1_cells} -> {m_b.l1_cells} ({m_b.l1_cells - m_a.l1_cells:+d})"
    )
    lines.append(
        f"  L2: {m_a.l2_cells} -> {m_b.l2_cells} ({m_b.l2_cells - m_a.l2_cells:+d})"
    )
    new_l1 = set(m_b.l1_keys) - set(m_a.l1_keys)
    new_l2 = set(m_b.l2_keys) - set(m_a.l2_keys)
    if new_l1:
        lines.append(f"  New L1 cells: {', '.join(sorted(new_l1)[:5])}")
    if new_l2:
        lines.append(f"  New L2 cells: {', '.join(sorted(new_l2)[:5])}")
    lines.append("")
    return lines


def _diff_defects(report_a, report_b) -> list[str]:
    """Diff defect quarantine."""
    lines = ["8. DEFECT QUARANTINE CHANGES", "-" * 40]
    d_a, d_b = report_a.defects, report_b.defects
    lines.append(
        f"  Open defects: {d_a.open_defects} -> {d_b.open_defects} "
        f"({d_b.open_defects - d_a.open_defects:+d})"
    )
    lines.append(
        f"  Resolved defects: {d_a.resolved_defects} -> {d_b.resolved_defects} "
        f"({d_b.resolved_defects - d_a.resolved_defects:+d})"
    )
    lines.append(
        f"  Quarantined cells: {d_a.quarantined_cells} -> {d_b.quarantined_cells} "
        f"({d_b.quarantined_cells - d_a.quarantined_cells:+d})"
    )

    all_defect_types = set(d_a.defect_types.keys()) | set(d_b.defect_types.keys())
    fixed_types = []
    new_types = []
    for dtype in sorted(all_defect_types):
        count_a = d_a.defect_types.get(dtype, 0)
        count_b = d_b.defect_types.get(dtype, 0)
        if count_b < count_a:
            fixed_types.append((dtype, count_a, count_b))
        elif count_b > count_a:
            new_types.append((dtype, count_a, count_b))

    if fixed_types:
        lines.append("  Fixed defect types:")
        for dtype, count_a, count_b in fixed_types:
            lines.append(f"    - {dtype}: {count_a} -> {count_b} (resolved)")
    if new_types:
        lines.append("  New/increased defect types:")
        for dtype, count_a, count_b in new_types:
            lines.append(f"    + {dtype}: {count_a} -> {count_b}")
    return lines


def _diff_kb_campaigns(args) -> int:
    """Compare two continuous discovery KB campaigns."""
    from computronium.core.campaign.kb_report import build_kb_report

    objectives = [o.strip() for o in args.objectives.split(",") if o.strip()]

    print("Comparing campaigns:")
    print(f"  A: {args.root_a}")
    print(f"  B: {args.root_b}")
    print(f"  Task: {args.task}")
    print(f"  Objectives: {objectives}")
    print()

    report_a = build_kb_report(args.root_a, task=args.task, objectives=objectives)
    report_b = build_kb_report(args.root_b, task=args.task, objectives=objectives)

    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append(f"CAMPAIGN DIFF: {args.root_a} -> {args.root_b}")
    output_lines.append("=" * 80)
    output_lines.append("")

    output_lines.extend(_diff_summary_stats(report_a, report_b))
    output_lines.extend(_diff_viable_cells(report_a, report_b, args))
    output_lines.extend(_diff_pareto_front(report_a, report_b))
    output_lines.extend(_diff_voids(report_a, report_b))
    output_lines.extend(_diff_clamps(report_a, report_b))
    output_lines.extend(_diff_walltimes(report_a, report_b))
    output_lines.extend(_diff_maturation(report_a, report_b))
    output_lines.extend(_diff_defects(report_a, report_b))

    result = "\n".join(output_lines)

    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"Diff written to {args.output}")
    else:
        print(result)

    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Console-script entry point for ``comp campaign``."""
    args = _build_parser().parse_args(argv)

    if not args.subcommand:
        _build_parser().print_help()
        return 1

    handlers = {
        "run": _run_campaign,
        "status": _show_status,
        "list": _list_campaigns,
        "compare": _compare_campaigns,
        "checkpoint": _manage_checkpoints,
        "export": _export_campaign,
        "report": _render_discovery_report,
        "kb-report": _render_kb_report,
        "diff": _diff_kb_campaigns,
    }
    handler = handlers.get(args.subcommand)
    if handler is None:
        print(f"Unknown subcommand: {args.subcommand}")
        return 1
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
