"""``comp continuous`` — the budgeted burst runner (TODO29 Phase 3).

Continuous discovery in time-boxed bursts: each burst samples viable grid
cells through the stratified driver, harvests gate rejections as structural
voids and runtime crashes as quarantined defects, and flushes the KB per
cell — every burst is resume-safe by construction.

Single-daemon assumption: do not point two bursts at one ``--root``
(SQLite write contention).

Usage::

    comp continuous --budget 5m --root artifacts/broad_map --credit-trace
    comp continuous --target-cells 100 --loop --sleep 10
    comp continuous unquarantine --defect a1b2c3d4e5f6 --root artifacts/broad_map
"""

from __future__ import annotations

import argparse
import logging
import signal
import time
from pathlib import Path
from typing import TYPE_CHECKING

from computronium.autoscientist.broad_map import (
    BroadMappingCampaign,
    budget_from_args,
    build_sweep,
    driver_seeded_kb,
    run_burst,
    run_deep_tier,
    run_l1_maturation,
)
from computronium.autoscientist.defects import (
    DefectRecord,
    append_defect,
    read_defects,
    resolve_defect,
)
from computronium.utils import seed_everything

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger("continuous")

_DEFECTS_NAME = "runtime_defects.jsonl"


def _grep_error_pattern(pattern: str, root: Path) -> bool:
    """Search codebase for error pattern. Returns True if pattern found."""
    import subprocess  # ruff: ignore[suspicious-subprocess-import] (grep fixed string, no shell)

    try:
        result = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true,start-process-with-partial-path] (fixed command, no shell)
            [
                "/usr/bin/grep",
                "-r",
                "-F",
                "--include=*.py",
                pattern,
                str(root / "computronium"),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        return result.returncode == 0 and result.stdout.strip() != ""
    except subprocess.TimeoutExpired, FileNotFoundError, OSError:
        # If grep fails or times out, assume pattern might exist (conservative)
        return True


def _unquarantine_fixed(root: Path) -> int:
    """Auto-release all defects whose error pattern no longer exists in codebase."""
    import time

    defects_path = root / _DEFECTS_NAME
    records = read_defects(defects_path)

    # Get all open defects (latest status per defect_id)
    open_defects: dict[str, DefectRecord] = {}
    for record in records:
        if record.status == "open":
            open_defects[record.defect_id] = record
        elif record.status == "resolved" and record.defect_id in open_defects:
            del open_defects[record.defect_id]

    if not open_defects:
        print("No open defects to check.", flush=True)
        return 0

    released = 0
    for defect_id, record in open_defects.items():
        # Search for the error message in the codebase
        search_pattern = record.message[:200]  # First 200 chars of error message
        if not search_pattern.strip():
            search_pattern = record.error_class

        logger.info("Checking defect %s: %s", defect_id, search_pattern[:80])
        if not _grep_error_pattern(search_pattern, root):
            # Pattern not found - defect likely fixed
            append_defect(
                defects_path,
                DefectRecord(
                    defect_id=defect_id,
                    timestamp=time.time(),
                    task=record.task,
                    cell=record.cell,
                    error_class=record.error_class,
                    message=record.message,
                    traceback_tail="",
                    status="resolved",
                ),
            )
            logger.info(
                "Defect %s auto-resolved (pattern not found in codebase)", defect_id
            )
            released += 1
        else:
            logger.info("Defect %s still present in codebase", defect_id)

    if released:
        print(
            f"Auto-released {released} defect(s) whose error pattern no longer exists in codebase"
        )
    else:
        print("No defects auto-released (all patterns still found in codebase)")

    return released


def _add_common_flags(parser: argparse.ArgumentParser) -> None:
    """Flags shared by ``comp continuous`` and ``comp daemon``."""
    parser.add_argument(
        "--budget",
        type=str,
        default=None,
        help="soft time cap per burst (e.g. 5m, 90s, 1h)",
    )
    parser.add_argument(
        "--target-cells", type=int, default=None, help="hard cap on completed cells"
    )
    parser.add_argument(
        "--objectives",
        type=str,
        default="accuracy,walltime_s",
        help="comma-separated objectives for multi-objective optimization "
        "(e.g. accuracy,walltime_s,param_count). "
        "Available: accuracy, walltime_s, param_count, flops, memory_mb, "
        "energy_per_step, latency_ms, bp_deficit, ruler_walltime_ratio, "
        "ruler_energy_ratio, spectral_radius, lyapunov_exponent, "
        "max_singular_value, psi_capacity, consolidation_cost, rewrite_rate, "
        "credit_alignment, feedback_path_length, trace_variance",
    )
    parser.add_argument(
        "--maturation",
        type=int,
        default=0,
        help="reserve up to N cells of each burst for an epochs=3 promotion re-run (maturity:l1)",
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        help="run bursts forever (fresh budget per burst) instead of one burst",
    )
    parser.add_argument(
        "--sleep", type=float, default=10.0, help="seconds between --loop bursts"
    )
    parser.add_argument("--root", type=Path, default=Path("artifacts/broad_map"))
    parser.add_argument(
        "--log-path",
        type=Path,
        default=None,
        help="also tee the burst log here (full burst transcript on disk)",
    )
    parser.add_argument("--max-iterations", type=int, default=200)
    parser.add_argument("--cells-per-iter", type=int, default=10)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument(
        "--task", default="mnist", help="single task name (use --tasks for multi-task)"
    )
    parser.add_argument(
        "--tasks",
        type=str,
        default=None,
        help="comma-separated task names for multi-task bursts (e.g., mnist,cifar10,spiral)",
    )
    parser.add_argument("--seed", type=int, default=20260915)
    parser.add_argument("--hidden-dim", type=int, default=64)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--param-budget", type=int, default=25000)
    parser.add_argument(
        "--geometry-sampling",
        type=str,
        default="full_range",
        choices=["full_range", "max_only"],
        help="geometry size sampling strategy: full_range explores all sizes up to param_budget (default), max_only uses only max-size configs",
    )
    parser.add_argument(
        "--limit-batches",
        type=int,
        default=0,
        help="cap training batches per epoch (0 = full epoch); shorter cells "
        "trade per-cell fidelity for coverage — right for L0 mapping",
    )
    parser.add_argument(
        "--credit-trace",
        action="store_true",
        help="capture per-cell BP-gradient alignment (adds settle overhead per cell)",
    )
    parser.add_argument(
        "--substrate",
        type=str,
        default="digital",
        choices=[
            "digital",
            "analog",
            "memristive",
            "neuromorphic",
            "optical",
            "quantum",
            "sparse",
            "ternary",
            "complex",
        ],
        help="substrate type for the campaign (affects auto-populated objectives)",
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="comp continuous", description=__doc__)
    _add_common_flags(parser)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="only propose cells without executing (shows experiment space diversity)",
    )
    sub = parser.add_subparsers(dest="command")
    unquarantine = sub.add_parser(
        "unquarantine", help="release cells quarantined by a resolved defect"
    )
    _add_common_flags(unquarantine)
    unquarantine.add_argument("--defect", help="defect id (sha256[:12])")
    unquarantine.add_argument(
        "--unquarantine-fixed",
        action="store_true",
        help="auto-release all defects whose error pattern no longer exists in codebase",
    )
    deep_tier = sub.add_parser(
        "deep-tier",
        help="promote front-stable cells to claim-grade L2 re-runs (seeds × epochs)",
    )
    _add_common_flags(deep_tier)
    deep_tier.add_argument(
        "--top", type=int, default=5, help="max cells to promote (legacy L2-only)"
    )
    deep_tier.add_argument("--seeds", type=int, default=3, help="fresh seeds per cell")
    deep_tier.add_argument(
        "--dry-run",
        action="store_true",
        help="show the promotion plan without executing",
    )
    return parser


def _burst_once(args: argparse.Namespace, campaign, driver) -> str:
    summary = run_burst(
        campaign,
        driver,
        budget_from_args(args),
        max_iterations=args.max_iterations,
    )
    return str(summary["stop_reason"])


def _loop_bursts(args: argparse.Namespace, campaign, driver) -> None:
    while True:
        summary = _burst_once(args, campaign, driver)
        if summary == "exhausted":
            logger.info("Grid exhausted: continuous loop ends.")
            return
        logger.info("Sleeping %.0fs until the next burst", args.sleep)
        time.sleep(args.sleep)


def _install_sigterm(handler: Callable[[], object] | None = None) -> None:
    def _terminate(signum: int, frame: object) -> None:
        if handler is not None:
            handler()
            return
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, _terminate)


def _run_forever(args: argparse.Namespace, campaign, driver) -> int:  # ruff: ignore[missing-type-function-argument] (internal, typed by build_sweep)
    _install_sigterm()
    try:
        _loop_bursts(args, campaign, driver)
    except KeyboardInterrupt, SystemExit:
        # Graceful flush path — never a finally block (PEP 765). The KB is
        # flushed per cell and the last burst checkpointed on stop.
        logger.info("Interrupted: state flushed; resume with the same --root.")
    return 0


def _tee_log(log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    )
    # Root handler: modules log under computronium.* names; named
    # loggers ("broad_map") would never see them.
    logging.getLogger().addHandler(handler)


def _parse_tasks(args: argparse.Namespace) -> list[str]:
    """Parse task(s) from args, supporting both --task and --tasks."""
    tasks_attr = getattr(args, "tasks", None)
    if tasks_attr is not None:
        return [t.strip() for t in tasks_attr.split(",") if t.strip()]
    task_attr = getattr(args, "task", None)
    if task_attr is not None:
        return [task_attr]
    return ["mnist"]


def _burst(args: argparse.Namespace) -> int:
    logging.basicConfig(level=logging.INFO)
    _install_sigterm()
    if args.log_path is not None:
        _tee_log(args.log_path)
    try:
        _run_burst(args)
    except KeyboardInterrupt, SystemExit:
        logger.info("Interrupted: state flushed; resume with the same --root.")
    return 0


def _run_burst(args: argparse.Namespace) -> None:
    tasks = _parse_tasks(args)
    for task in tasks:
        task_root = args.root / task
        (task_root / "campaign").mkdir(parents=True, exist_ok=True)
    seed_everything(args.seed, deterministic=False)

    for task in tasks:
        task_root = args.root / task
        task_args = argparse.Namespace(**vars(args))
        task_args.task = task
        task_args.root = task_root
        campaign, driver = build_sweep(task_args)
        if args.loop:
            _run_forever(task_args, campaign, driver)
            return
        if getattr(args, "dry_run", False):
            # Dry run: just propose and show what would be run
            print(f"\n=== Dry run for task: {task} ===")
            target_cells = args.target_cells or args.cells_per_iter
            proposed = 0
            for iteration in range(1, args.max_iterations + 1):
                n_proposals = min(args.cells_per_iter, target_cells - proposed)
                if n_proposals <= 0:
                    break
                proposals = driver.propose_batch(n_proposals=n_proposals)
                if not proposals:
                    print("No more novel cells to propose.")
                    break
                proposed += len(proposals)
                print(
                    f"\nIteration {iteration}: {len(proposals)} proposals (total: {proposed})"
                )
                for i, p in enumerate(proposals):
                    geo = p.geometry or {}
                    dyn = p.dynamics or "?"
                    credit = p.credit or "?"
                    update = p.update or "?"
                    topo = geo.get("topology_type", "?")
                    depth = geo.get("depth", "?")
                    hidden = geo.get("hidden_dim", "?")
                    print(
                        f"  {i + 1}. dyn={dyn} credit={credit} update={update} | topo={topo} depth={depth} hidden={hidden}"
                    )
            print(f"\nTotal proposed: {proposed} cells")
            return
        run_burst(
            campaign,
            driver,
            budget_from_args(task_args),
            max_iterations=args.max_iterations,
        )
        if args.maturation:
            run_l1_maturation(task_args, campaign, driver.burst_tag)


def _deep_tier(args: argparse.Namespace) -> int:
    logging.basicConfig(level=logging.INFO)
    from computronium.autoscientist.objectives import parse_objectives

    obj_spec = getattr(args, "objectives", "accuracy,walltime_s")
    objectives = parse_objectives(obj_spec)

    tasks = _parse_tasks(args)
    if len(tasks) > 1:
        logger.warning("deep-tier with multiple tasks: running on each task separately")

    for task in tasks:
        task_root = args.root / task
        logger.info("Running deep-tier for task: %s", task)
        _deep_tier_single(task, task_root, args, objectives)
    return 0


def _deep_tier_single(
    task: str, root: Path, args: argparse.Namespace, objectives
) -> int:
    # ``--root`` is the campaign root and each task subdir hangs off it, so a
    # task dir passed here resolves to a KB that does not exist. Fail loudly
    # instead of reporting an empty promotion plan.
    kb_path = root / "kb.sqlite"
    if not kb_path.exists():
        msg = (
            f"No KB at {kb_path}. Pass the campaign root (the parent of the "
            f"task directories), not the task directory itself."
        )
        raise FileNotFoundError(msg)
    maturation = getattr(args, "maturation", 0)
    if maturation > 0:
        from computronium.autoscientist.broad_map import (
            promote_candidates,
            run_l1_maturation,
        )

        candidates = promote_candidates(
            root / "kb.sqlite",
            task,
            maturation,
            objectives=objectives,
        )
        if not candidates:
            logger.info(
                "Deep tier (L1→L2): no promotion candidates on the burst front."
            )
            return 0
        if getattr(args, "dry_run", False):
            for c in candidates:
                print(
                    f"{c.key}  acc={c.accuracy:.3f}  "
                    f"planned: L1 epochs=3 → L2 {getattr(args, 'seeds', 3)} seeds × {getattr(args, 'epochs', 10)} epochs"
                )
            print(
                f"{len(candidates)} candidate(s); {len(candidates) * (1 + getattr(args, 'seeds', 3))} CEEC experiments"
            )
            return 0

        # Build campaign for L1
        l1_campaign = BroadMappingCampaign(
            knowledge_base=None,
            output_dir=str(root / "campaign"),
            db_path=root / "campaign" / "campaign.db",
            branch_name="deep_tier_l1",
            ceec_ledger_path=root / "ledger.sqlite",
            kb_path=root / "kb.sqlite",
            defects_path=root / "runtime_defects.jsonl",
        )
        l1_campaign.knowledge_base = driver_seeded_kb(root / "kb.sqlite")
        (root / "campaign").mkdir(parents=True, exist_ok=True)

        # L1: epochs=3 (reuse run_l1_maturation with modified args)
        l1_args = argparse.Namespace(
            root=root,
            task=task,
            maturation=len(candidates),
            epochs=3,
            objectives=getattr(args, "objectives", "accuracy,walltime_s"),
            seed=getattr(args, "seed", 20260915),
        )
        l1_results = run_l1_maturation(l1_args, l1_campaign, burst_tag="l1_promotion")

        if not l1_results:
            logger.info("Deep tier: no L1 re-runs completed.")
            return 0

        # L2: full epochs, seeds=3
        l2_campaign = BroadMappingCampaign(
            knowledge_base=None,
            output_dir=str(root / "campaign"),
            db_path=root / "campaign" / "campaign.db",
            branch_name="deep_tier_l2",
            ceec_ledger_path=root / "ledger.sqlite",
            kb_path=root / "kb.sqlite",
            defects_path=root / "runtime_defects.jsonl",
        )
        l2_campaign.knowledge_base = driver_seeded_kb(root / "kb.sqlite")
        from computronium.autoscientist.broad_map import (
            run_deep_tier as run_deep_tier_fn,
        )

        l2_rows = run_deep_tier_fn(
            root,
            l2_campaign,
            task=task,
            top=len(l1_results),
            epochs=getattr(args, "epochs", 10),
            seeds=getattr(args, "seeds", 3),
            seed=getattr(args, "seed", 20260915),
            objectives=objectives,
        )
        print(
            f"deep-tier (L1→L2): {len(l2_rows)} claim-grade L2 row(s) in {root / 'maturation.jsonl'}"
        )
        return 0

    # Legacy L2-only path (front-stable across ≥2 bursts)
    if getattr(args, "dry_run", False):
        from computronium.autoscientist.broad_map import _deep_tier_candidates

        plan = _deep_tier_candidates(
            root / "kb.sqlite", getattr(args, "top", 5), task, objectives=objectives
        )
        for candidate in plan:
            print(
                f"{candidate.key}  acc={candidate.accuracy:.3f}  "
                f"bursts={candidate.front_bursts} "
                f"evidence={candidate.stability_evidence}  "
                f"planned: {getattr(args, 'seeds', 3)} seeds × {getattr(args, 'epochs', 10)} epochs"
            )
        print(
            f"{len(plan)} candidate(s); {len(plan) * getattr(args, 'seeds', 3)} CEEC experiments"
        )
        return 0
    campaign = BroadMappingCampaign(
        knowledge_base=None,
        output_dir=str(root / "campaign"),
        db_path=root / "campaign" / "campaign.db",
        branch_name="deep_tier",
        ceec_ledger_path=root / "ledger.sqlite",
        kb_path=root / "kb.sqlite",
        defects_path=root / "runtime_defects.jsonl",
    )
    campaign.knowledge_base = driver_seeded_kb(root / "kb.sqlite")
    (root / "campaign").mkdir(parents=True, exist_ok=True)
    rows = run_deep_tier(
        root,
        campaign,
        task=task,
        top=getattr(args, "top", 5),
        epochs=getattr(args, "epochs", 10),
        seeds=getattr(args, "seeds", 3),
        seed=getattr(args, "seed", 20260915),
        objectives=objectives,
    )
    print(f"deep-tier: {len(rows)} claim-grade row(s) in {root / 'maturation.jsonl'}")
    return 0


def _unquarantine(args: argparse.Namespace) -> int:
    logging.basicConfig(level=logging.INFO)
    tasks = _parse_tasks(args)
    total_released = 0
    for task in tasks:
        task_root = args.root / task
        if args.unquarantine_fixed:
            released = _unquarantine_fixed(task_root)
            total_released += released
            logger.info("Task %s: auto-released %d defect(s)", task, released)
        else:
            if not args.defect:
                print(
                    "Error: --defect is required unless --unquarantine-fixed is used",
                    flush=True,
                )
                return 1
            resolved = resolve_defect(task_root / _DEFECTS_NAME, args.defect)
            if resolved == 0:
                print(
                    f"defect {args.defect} not found (or already resolved) in task {task}",
                    flush=True,
                )
                continue
            print(
                f"defect {args.defect} resolved in task {task}; affected cells re-open for the next burst"
            )
            total_released += resolved
    if args.unquarantine_fixed:
        print(f"Total auto-released across {len(tasks)} task(s): {total_released}")
    return 0


def main() -> int:
    args = _build_parser().parse_args()
    if args.command == "unquarantine":
        return _unquarantine(args)
    if args.command == "deep-tier":
        return _deep_tier(args)
    return _burst(args)


if __name__ == "__main__":
    raise SystemExit(main())
