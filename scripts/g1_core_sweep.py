"""G1 core sweep (TODO27 Phase 3) — background AutoScientist campaign.

Fresh KB (no prior-operator seeding beyond quarantine tags), ruler-eligible
tasks only (``artifacts/ruler_table.json``), CEEC-governed execution, the
coverage proposer driving every iteration, and the surrogate retrained each
iteration with a predicted-vs-measured reliability log.

Usage:
    nohup uv run python scripts/g1_core_sweep.py \
        --iterations 20 --cells-per-iter 5 \
        --root artifacts/g1 > logs/g1_sweep.log 2>&1 &

Stop rules (plan §3/G1): the coverage proposer returning no novel cells
ends the campaign; ``--max-iterations`` caps spend.
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from pathlib import Path
from typing import TYPE_CHECKING

from computronium.autoscientist.campaign import AutoScientistCampaign
from computronium.autoscientist.proposer import ExperimentProposer, cell_key
from computronium.knowledge import KnowledgeBase
from computronium.utils import seed_everything

if TYPE_CHECKING:
    from computronium.autoscientist.bridge import ExperimentProposal

logger = logging.getLogger("g1_sweep")

RULER_TABLE = Path("artifacts/ruler_table.json")


def ruler_eligible_tasks() -> list[str]:
    rows = json.loads(RULER_TABLE.read_text(encoding="utf-8"))["rows"]
    return [r["task"] for r in rows if r.get("eligible") and r.get("beats_chance")]


class CoverageDriver:
    """Wraps the coverage proposer in the campaign's ``propose_batch`` contract,
    rotating the task across the ruler-eligible catalog each call."""

    def __init__(
        self,
        proposer: ExperimentProposer,
        tasks: list[str],
        cells: int,
        *,
        epochs: int = 5,
        skip_dynamics: frozenset[str] = frozenset(),
    ) -> None:
        self.proposer = proposer
        self.tasks = tasks
        self.cells = cells
        self.epochs = epochs
        self.skip_dynamics = skip_dynamics
        from computronium.autoscientist.proposer import GRID_DYNAMICS

        order = tuple(d for d in GRID_DYNAMICS if d not in skip_dynamics)
        self.dynamics_order = order or GRID_DYNAMICS
        self._visit = 0

    def has_novel(self) -> bool:
        """True if any coverage-novel coordinate remains for the next task.

        Gate-skipped proposals record their cell as covered but produce no
        result rows, so "no results" must not stop the campaign (rev 8:
        the em slice's next 6 product-order cells were all structurally
        impossible, and the sweep halted after one iteration while
        coverage was still advancing). The campaign ends only when the
        proposer has nothing novel left at all.
        """
        task = self.tasks[self._visit % len(self.tasks)]
        return bool(self.proposer.propose_coverage_cells(1, task=task))

    def propose_batch(
        self, n_proposals: int, recent_results: list[dict[str, object]] | None = None
    ) -> list[ExperimentProposal]:
        task = self.tasks[self._visit % len(self.tasks)]
        self._visit += 1
        proposals = self.proposer.propose_coverage_cells(
            min(n_proposals, self.cells),
            task=task,
            hyperparams={"epochs": self.epochs},
            dynamics_order=self.dynamics_order,
        )
        logger.info(
            "Coverage driver: %d novel cells on %s (visit %d)",
            len(proposals),
            task,
            self._visit,
        )
        return proposals


def log_reliability(
    kb: KnowledgeBase, results: list[dict[str, object]], path: Path
) -> None:
    """Surrogate reliability curve: predicted vs measured, one row per cell."""
    if not results:
        return
    rows = []
    for result in results:
        if result.get("status") != "completed":
            continue
        proposal = result.get("proposal")
        if not isinstance(proposal, dict):
            continue
        config: dict[str, object] = {
            "geometry": proposal.get("geometry") or {},
            "dynamics": proposal.get("dynamics"),
            "credit": proposal.get("credit"),
            "update": proposal.get("update"),
        }
        predicted = kb.predict_outcome(config)
        rows.append({
            "cell": cell_key(
                str(proposal.get("dynamics")),
                str(proposal.get("credit")),
                str(proposal.get("update")),
                str((proposal.get("geometry") or {}).get("topology_type")),
            ),
            "task": proposal.get("task"),
            "predicted": predicted,
            "measured": result.get("final_accuracy"),
        })
    if rows:
        with path.open("a", encoding="utf-8") as fh:
            fh.write("\n".join(json.dumps(r) for r in rows) + "\n")
        logger.info("Reliability: %d predicted-vs-measured rows appended", len(rows))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--cells-per-iter", type=int, default=5)
    parser.add_argument("--root", type=Path, default=Path("artifacts/g1"))
    parser.add_argument("--seed", type=int, default=20260914)
    parser.add_argument(
        "--epochs",
        type=int,
        default=5,
        help="Training epochs per cell — use 1-2 for rapid shallow breadth "
        "(many datapoints, high-dimensional analysis), 5 for depth",
    )
    parser.add_argument(
        "--skip-dynamics",
        type=str,
        default="",
        help="Comma-separated dynamics to exclude from this run's order",
    )
    parser.add_argument(
        "--tasks",
        type=str,
        default="",
        help="Comma-separated override; default is the ruler-eligible catalog",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    args.root.mkdir(parents=True, exist_ok=True)

    tasks = (
        [t.strip() for t in args.tasks.split(",") if t.strip()]
        if args.tasks
        else ruler_eligible_tasks()
    )
    logger.info("Ruler-eligible tasks: %s", tasks)

    seed_everything(args.seed, deterministic=False)
    kb = KnowledgeBase(args.root / "kb.sqlite")
    campaign = AutoScientistCampaign(
        knowledge_base=kb,
        output_dir=str(args.root / "campaign"),
        db_path=args.root / "campaign" / "campaign.db",
        branch_name="g1_core_sweep",
        ceec_ledger_path=args.root / "ledger.sqlite",
    )
    driver = CoverageDriver(
        ExperimentProposer(kb),
        tasks,
        args.cells_per_iter,
        epochs=args.epochs,
        skip_dynamics=frozenset(
            d.strip() for d in args.skip_dynamics.split(",") if d.strip()
        ),
    )
    campaign.proposer = driver  # type: ignore[assignment]

    reliability_path = args.root / "surrogate_reliability.jsonl"
    for iteration in range(1, args.iterations + 1):
        started = time.time()
        results = campaign.run_iteration(n_experiments=args.cells_per_iter)
        completed = sum(1 for r in results if r.get("status") == "completed")
        logger.info(
            "Iteration %d: %d completed / %d proposed (%.0fs)",
            iteration,
            completed,
            len(results),
            time.time() - started,
        )
        log_reliability(kb, results, reliability_path)
        kb.train_surrogate()
        if not driver.has_novel():
            logger.info("Stop rule hit: no novel cells proposed. Campaign ends.")
            break

    logger.info("G1 sweep finished after %d iterations requested", args.iterations)


if __name__ == "__main__":
    main()
