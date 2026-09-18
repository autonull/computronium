"""
AutoScientistCampaign: Orchestrates multi-day autonomous campaigns.

Combines the Scientist (execution) with AutoScientist (reasoning/proposal)
into a continuous discovery loop with:
  - Hypothesis generation
  - Experiment proposal
  - Execution via SystemTrainer over ontology-composed systems
  - Result analysis
  - KnowledgeBase update

Features:
  - YAML + SQLite persistence for campaign state
  - Git-like branching for experimental lineages
  - Resume from checkpoints
"""

import contextlib
import json
import math
import os
import sqlite3
import sys
import time
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, cast

import yaml

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping
    from typing import Protocol

    from ceec.models import Experiment

    from computronium.autoscientist.bridge import ExperimentProposal
    from computronium.autoscientist.ceec_link import CEECLink
    from computronium.knowledge import KnowledgeBase
    from computronium.ontology import (
        CreditAssignment,
        Geometry,
        StateDynamics,
        Substrate,
    )

    class ProbeSystem(Protocol):
        """Minimal settle-capable system surface for the probes."""

        dynamics: StateDynamics
        geometry: Geometry
        substrate: Substrate
        credit: CreditAssignment


from computronium.autoscientist.proposer import ExperimentProposer, cell_key
from computronium.autoscientist.reasoner import HypothesisReasoner
from computronium.core.exceptions import KnowledgeBaseError
from computronium.core.logging import get_logger
from computronium.core.profiling import estimate_train_step_flops, get_gpu_memory_mb

logger = get_logger(__name__)


def _metric(value: object) -> float:
    """Coerce a possibly-missing result metric to float (zeros stay zeros)."""
    return float(value) if isinstance(value, int | float) else 0.0


_RULER_LR: dict[str, float] = {}


def _probe_credit_alignment(
    system: ProbeSystem, proposal: ExperimentProposal, task: object
) -> float:
    """Cosine alignment of the cell's credit signal against the BP ruler.

    Opt-in (``hyperparams["credit_trace"]``): one batch, settle phases +
    split-half + BP reference from ``analysis.instruments.credit_trace``.
    Returns the min per-layer BP cosine (0.0 when the read fails — some
    credit families reach no learnable weight on a given geometry).
    """
    if not proposal.hyperparams.get("credit_trace"):
        return 0.0
    try:
        from computronium.analysis.instruments import credit_trace

        return _credit_alignment_read(system, task, credit_trace)
    except (RuntimeError, TypeError, ValueError, StopIteration) as e:
        logger.warning("credit_trace probe failed: %s", e)
        return 0.0


def _credit_alignment_read(system: ProbeSystem, task: object, read) -> float:
    """One-batch BP-alignment read on the system's device."""
    x, y = next(iter(task.get_dataloader("train")))  # type: ignore[union-attr, attr-defined]
    # Canonical flat input on the system's device — the read must see
    # exactly what the trainer sees, or families that initialize state on
    # first contact (e.g. FA feedback matrices) poison themselves with a
    # CPU batch.
    device = getattr(system, "device", x.device)
    x = x.reshape(x.size(0), -1).to(device)
    y = y.to(device)
    trace = read(system, x, y, bp_reference=True)
    return float(trace["bp_min_cosine"])  # type: ignore[arg-type]


def probe_spectral_radius(
    system: ProbeSystem, input_dim: int, *, batch: int = 8, directions: int = 3
) -> float:
    """Sampled directional amplification ‖Jv‖ of the free-settle map.

    Mean ‖Jv‖ over random unit perturbation directions (the
    ``stability.spectral_radius`` fast-proxy semantics, applied at the
    composed 5-axis cell at init). The settle map input→output is
    dimension-changing, so ρ(J) is undefined; this is a lower-bound
    instrument on σ_max(J) — not a certified radius. Returns 0.0 on any
    settle failure (the failure itself is a gate/void signal).
    """
    import torch

    from computronium.state import CompositeState

    x_base = torch.randn(batch, input_dim, generator=torch.Generator().manual_seed(0))
    device = getattr(system, "device", None)
    if device is not None:
        x_base = x_base.to(device)

    def activity(x: torch.Tensor) -> torch.Tensor:
        state = CompositeState(activity={"x": x}, plastic={}, substrate={})
        settled = system.dynamics.settle(
            state, system.geometry, system.substrate, target=None
        )
        acts = settled.activations
        out = x if acts is None else (acts[-1] if isinstance(acts, list) else acts)
        return out.reshape(x.shape[0], -1)

    eps = 1e-4
    rng = torch.Generator().manual_seed(0)
    amps: list[float] = []
    try:
        base = activity(x_base)
        for _ in range(directions):
            v = torch.randn(x_base.shape, generator=rng)
            v /= v.norm() + 1e-8
            jv = (activity(x_base + eps * v) - base) / eps
            amps.append(jv.norm().item())
        return sum(amps) / len(amps)
    except (RuntimeError, TypeError, ValueError) as e:
        logger.warning("Spectral probe failed: %s", e)
        return 0.0


def _ruler_lr(task: str | None, topology: str | None = None) -> float:
    """Per-task best lr from the committed ruler table (P0.3 protocol).

    A proposal without its own ``lr`` trains at the task's calibrated
    ceiling lr — but only for ``feedforward``, the topology the ruler
    actually measured. Other topologies default to 1e-2 per the
    topology-lr calibration probe (``scripts/probes/
    d28_topology_lr_probe.py``, digits @ 1 epoch, 1 seed): the old flat
    1e-3 starved every non-feedforward cell (recurrent em 0.161 vs 0.856
    at 1e-2), while no topology preferred a smaller lr.
    """
    if topology not in {None, "feedforward"}:
        return 1e-2
    if not _RULER_LR:
        path = Path(__file__).parents[2] / "artifacts/ruler_table.json"
        try:
            rows = json.loads(path.read_text(encoding="utf-8"))["rows"]
            for row in rows:
                lr = row.get("lr")
                if isinstance(lr, int | float):
                    _RULER_LR[str(row["task"])] = float(lr)
        except OSError, ValueError, KeyError:
            logger.warning("Ruler table missing at %s; defaulting lr 1e-2", path)
        _RULER_LR.setdefault("*", 1e-2)
    return _RULER_LR.get(task or "*", _RULER_LR["*"])


@dataclass(frozen=True, slots=True)
class CampaignState:
    """Immutable campaign state snapshot."""

    campaign_id: str
    branch_name: str
    parent_branch: str | None
    iteration: int
    created_at: str
    updated_at: str
    config: dict[str, object]
    metadata: dict[str, object]


@dataclass(frozen=True, slots=True)
class IterationRecord:
    """Single iteration record."""

    iteration: int
    timestamp: str
    branch_name: str
    n_proposals: int
    n_completed: int
    n_failed: int
    proposals: list[dict[str, object]]
    results: list[dict[str, object]]
    insights: list[str]


class CampaignDatabase:
    """SQLite-backed campaign persistence with branch support."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS campaigns (
                    campaign_id TEXT PRIMARY KEY,
                    branch_name TEXT NOT NULL,
                    parent_branch TEXT,
                    iteration INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    config TEXT NOT NULL,  -- JSON
                    metadata TEXT NOT NULL  -- JSON
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_campaign_branch ON campaigns(branch_name)
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS iterations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id TEXT NOT NULL,
                    branch_name TEXT NOT NULL,
                    iteration INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    n_proposals INTEGER,
                    n_completed INTEGER,
                    n_failed INTEGER,
                    proposals TEXT NOT NULL,  -- JSON
                    results TEXT NOT NULL,    -- JSON
                    insights TEXT NOT NULL,   -- JSON
                    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_iter_campaign ON iterations(campaign_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_iter_branch ON iterations(branch_name)
            """)
            conn.commit()

    def create_campaign(
        self,
        campaign_id: str,
        branch_name: str,
        parent_branch: str | None,
        config: dict[str, object],
        metadata: dict[str, object] | None = None,
    ) -> CampaignState:
        """Create a new campaign or branch."""
        now = datetime.now().isoformat()
        state = CampaignState(
            campaign_id=campaign_id,
            branch_name=branch_name,
            parent_branch=parent_branch,
            iteration=0,
            created_at=now,
            updated_at=now,
            config=config,
            metadata=metadata or {},
        )

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO campaigns
                (campaign_id, branch_name, parent_branch, iteration, created_at, updated_at, config, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    state.campaign_id,
                    state.branch_name,
                    state.parent_branch,
                    state.iteration,
                    state.created_at,
                    state.updated_at,
                    json.dumps(state.config),
                    json.dumps(state.metadata),
                ),
            )
            conn.commit()

        return state

    def get_campaign(self, campaign_id: str) -> CampaignState | None:
        """Get campaign by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM campaigns WHERE campaign_id = ?", (campaign_id,)
            )
            row = cursor.fetchone()

        if not row:
            return None

        return CampaignState(
            campaign_id=row["campaign_id"],
            branch_name=row["branch_name"],
            parent_branch=row["parent_branch"],
            iteration=row["iteration"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            config=json.loads(row["config"]),
            metadata=json.loads(row["metadata"]),
        )

    def get_latest_on_branch(self, branch_name: str) -> CampaignState | None:
        """Get the most recent campaign state on a branch."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM campaigns
                WHERE branch_name = ?
                ORDER BY iteration DESC, updated_at DESC
                LIMIT 1
                """,
                (branch_name,),
            )
            row = cursor.fetchone()

        if not row:
            return None

        return CampaignState(
            campaign_id=row["campaign_id"],
            branch_name=row["branch_name"],
            parent_branch=row["parent_branch"],
            iteration=row["iteration"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            config=json.loads(row["config"]),
            metadata=json.loads(row["metadata"]),
        )

    def update_iteration(
        self,
        campaign_id: str,
        iteration: int,
        metadata: dict[str, object] | None = None,
    ) -> None:
        """Update campaign iteration counter."""
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            if metadata:
                conn.execute(
                    "UPDATE campaigns SET iteration = ?, updated_at = ?, metadata = ? WHERE campaign_id = ?",
                    (iteration, now, json.dumps(metadata), campaign_id),
                )
            else:
                conn.execute(
                    "UPDATE campaigns SET iteration = ?, updated_at = ? WHERE campaign_id = ?",
                    (iteration, now, campaign_id),
                )
            conn.commit()

    def add_iteration_record(self, record: IterationRecord) -> int:
        """Add an iteration record."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO iterations
                (campaign_id, branch_name, iteration, timestamp, n_proposals, n_completed, n_failed,
                 proposals, results, insights)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.iteration,  # campaign_id reused as iteration for now
                    record.branch_name,
                    record.iteration,
                    record.timestamp,
                    record.n_proposals,
                    record.n_completed,
                    record.n_failed,
                    json.dumps(record.proposals),
                    json.dumps(record.results),
                    json.dumps(record.insights),
                ),
            )
            conn.commit()
            return int(cursor.lastrowid or 0)

    def get_iteration_history(self, branch_name: str) -> list[IterationRecord]:
        """Get all iterations for a branch."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM iterations
                WHERE branch_name = ?
                ORDER BY iteration ASC
                """,
                (branch_name,),
            )
            rows = cursor.fetchall()

        return [
            IterationRecord(
                iteration=row["iteration"],
                timestamp=row["timestamp"],
                branch_name=row["branch_name"],
                n_proposals=row["n_proposals"],
                n_completed=row["n_completed"],
                n_failed=row["n_failed"],
                proposals=json.loads(row["proposals"]),
                results=json.loads(row["results"]),
                insights=json.loads(row["insights"]),
            )
            for row in rows
        ]

    def list_branches(self) -> list[str]:
        """List all branch names."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT DISTINCT branch_name FROM campaigns ORDER BY branch_name"
            )
            return [row[0] for row in cursor.fetchall()]

    def list_campaigns(self, branch_name: str | None = None) -> list[CampaignState]:
        """List campaigns, optionally filtered by branch."""
        query = "SELECT * FROM campaigns"
        params: tuple = ()
        if branch_name:
            query += " WHERE branch_name = ?"
            params = (branch_name,)
        query += " ORDER BY updated_at DESC"

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

        return [
            CampaignState(
                campaign_id=row["campaign_id"],
                branch_name=row["branch_name"],
                parent_branch=row["parent_branch"],
                iteration=row["iteration"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                config=json.loads(row["config"]),
                metadata=json.loads(row["metadata"]),
            )
            for row in rows
        ]


class CampaignCheckpointer:
    """Handles YAML checkpoint serialization for human-readable campaign state."""

    def __init__(self, checkpoint_dir: str | Path):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def save_checkpoint(
        self,
        campaign_state: CampaignState,
        iteration_history: list[IterationRecord],
        filename: str | None = None,
    ) -> Path:
        """Save campaign state as human-readable YAML."""
        if filename is None:
            filename = (
                f"{campaign_state.branch_name}_iter{campaign_state.iteration:04d}.yaml"
            )

        filepath = self.checkpoint_dir / filename

        data = {
            "campaign": asdict(campaign_state),
            "history": [asdict(r) for r in iteration_history],
        }

        with filepath.open("w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

        logger.info("Checkpoint saved: %s", filepath)
        return filepath

    def load_checkpoint(
        self, filepath: str | Path
    ) -> tuple[CampaignState, list[IterationRecord]]:
        """Load campaign state from YAML checkpoint."""
        with Path(filepath).open(encoding="utf-8") as f:
            data = yaml.safe_load(f)

        campaign = CampaignState(**data["campaign"])
        history = [IterationRecord(**r) for r in data.get("history", [])]

        return campaign, history

    def list_checkpoints(self, branch_name: str | None = None) -> list[Path]:
        """List available checkpoints."""
        pattern = f"{branch_name}_*.yaml" if branch_name else "*.yaml"
        return sorted(self.checkpoint_dir.glob(pattern))


class AutoScientistCampaign:
    """
    Autonomous research campaign manager with persistence and branching.

    Runs continuous discovery loops:
        1. Reason: Generate hypotheses from KnowledgeBase
        2. Propose: Convert hypotheses to experiment proposals
        3. Execute: Run experiments via SystemTrainer
        4. Learn: Update KnowledgeBase with results

    Features:
        - SQLite + YAML persistence
        - Git-like branching (create_branch, checkout, merge)
        - Resume from any checkpoint
        - Human approval gates
    """

    def __init__(  # noqa: PLR0913, PLR0917 (mirrors the sweep's CLI axes)
        self,
        knowledge_base: KnowledgeBase | None = None,
        output_dir: str = "autoscientist_campaigns",
        db_path: str | Path | None = None,
        branch_name: str = "main",
        parent_branch: str | None = None,
        campaign_id: str | None = None,
        resume: bool = False,
        max_concurrent: int = 1,
        human_approval_gate: bool = False,
        ceec_ledger_path: str | Path | None = None,
    ):
        self.knowledge_base = knowledge_base
        self.proposer = (
            ExperimentProposer(self.knowledge_base) if self.knowledge_base else None
        )
        self.reasoner = (
            HypothesisReasoner(self.knowledge_base) if self.knowledge_base else None
        )

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Persistence layer
        self.db_path = db_path or (self.output_dir / "campaign.db")
        self.db = CampaignDatabase(self.db_path)
        self.checkpointer = CampaignCheckpointer(self.output_dir / "checkpoints")

        # Campaign identity
        self.branch_name = branch_name
        self.parent_branch = parent_branch
        self.campaign_id = campaign_id or f"camp_{uuid.uuid4().hex[:8]}"
        self.max_concurrent = max_concurrent
        self.human_approval_gate = human_approval_gate

        # P2.1/P2.4: when a ledger path is given, every proposal runs as a
        # CEEC pre-registration → ProbeResult trace (one shared format).
        self.ceec: CEECLink | None = None
        if ceec_ledger_path is not None:
            from computronium.autoscientist.ceec_link import CEECLink

            self.ceec = CEECLink(str(ceec_ledger_path))

        # Runtime state
        self._iteration = 0
        self._campaign_state: CampaignState | None = None
        self._config: dict[str, object] = {}
        # Optional per-batch telemetry sink forwarded to every SystemTrainer
        # this campaign builds (TODO30 8.2). Side-channel only — never a
        # second record path; the KB stays the sole record of truth.
        self.step_callback: Callable[[Mapping[str, float]], None] | None = None

        # Resume or initialize
        if resume:
            self._resume()
        else:
            self._initialize()

    def _initialize(self) -> None:
        """Initialize a new campaign or branch."""
        self._config = {
            "max_concurrent": self.max_concurrent,
            "human_approval_gate": self.human_approval_gate,
            "knowledge_base_path": str(self.knowledge_base.config.db_path)
            if self.knowledge_base
            else None,
        }

        # Check if branch exists
        existing = self.db.get_latest_on_branch(self.branch_name)
        if existing:
            # Branch exists, continue from latest
            self._campaign_state = existing
            self.campaign_id = existing.campaign_id
            self._iteration = existing.iteration
            logger.info(
                "Resuming branch '%s' at iteration %d (campaign %s)",
                self.branch_name,
                self._iteration,
                self.campaign_id,
            )
        else:
            # Create new campaign
            self._campaign_state = self.db.create_campaign(
                campaign_id=self.campaign_id,
                branch_name=self.branch_name,
                parent_branch=self.parent_branch,
                config=self._config,
                metadata={"created_by": "AutoScientistCampaign", "version": "1.0"},
            )
            self._iteration = 0
            logger.info(
                "Created new campaign %s on branch '%s'",
                self.campaign_id,
                self.branch_name,
            )

    def _resume(self) -> None:
        """Resume from latest checkpoint on current branch."""
        state = self.db.get_latest_on_branch(self.branch_name)
        if not state:
            raise ValueError(
                f"No campaign found on branch '{self.branch_name}' to resume"
            )

        self._campaign_state = state
        self.campaign_id = state.campaign_id
        self._iteration = state.iteration
        self._config = state.config

        logger.info(
            "Resumed campaign %s on branch '%s' at iteration %d",
            self.campaign_id,
            self.branch_name,
            self._iteration,
        )

    @classmethod
    def create_branch(
        cls,
        source_branch: str,
        new_branch: str,
        db_path: str | Path,
        knowledge_base: KnowledgeBase | None = None,
        output_dir: str = "autoscientist_campaigns",
    ) -> AutoScientistCampaign:
        """
        Create a new branch from an existing branch (git-like).

        The new branch starts from the latest state of the source branch.
        """
        db = CampaignDatabase(db_path)
        source_state = db.get_latest_on_branch(source_branch)
        if not source_state:
            raise ValueError(f"Source branch '{source_branch}' not found")

        # Create new campaign on new branch, inheriting from source
        new_campaign_id = f"camp_{uuid.uuid4().hex[:8]}"
        new_state = db.create_campaign(  # noqa: F841 (branch row persisted by create_campaign)
            campaign_id=new_campaign_id,
            branch_name=new_branch,
            parent_branch=source_branch,
            config=source_state.config,
            metadata={
                "forked_from": source_state.campaign_id,
                "forked_at_iteration": source_state.iteration,
                "created_by": "branch",
            },
        )

        return cls(
            knowledge_base=knowledge_base,
            output_dir=output_dir,
            db_path=db_path,
            branch_name=new_branch,
            parent_branch=source_branch,
            campaign_id=new_campaign_id,
            resume=True,
        )

    def checkout(self, branch_name: str) -> None:
        """Switch to a different branch (like git checkout)."""
        state = self.db.get_latest_on_branch(branch_name)
        if not state:
            raise ValueError(f"Branch '{branch_name}' not found")

        self.branch_name = branch_name
        self._campaign_state = state
        self.campaign_id = state.campaign_id
        self._iteration = state.iteration
        self._config = state.config

        logger.info(
            "Checked out branch '%s' at iteration %d", branch_name, self._iteration
        )

    def merge_from(self, source_branch: str, strategy: str = "latest") -> None:
        """
        Merge insights from another branch.

        Strategies:
            - 'latest': Take the latest iteration from source branch
            - 'best': Take the best performing iteration from source branch
        """
        source_state = self.db.get_latest_on_branch(source_branch)
        if not source_state:
            raise ValueError(f"Source branch '{source_branch}' not found")

        # Get best iteration from source
        history = self.db.get_iteration_history(source_branch)
        if not history:
            logger.warning(
                "Source branch '%s' has no iterations to merge", source_branch
            )
            return

        if strategy == "best":
            best_iter = max(
                history,
                key=lambda r: max(
                    (_metric(res.get("final_accuracy")) for res in r.results),
                    default=0.0,
                ),
            )
            logger.info(
                "Merging best iteration %d from branch '%s'",
                best_iter.iteration,
                source_branch,
            )
        else:
            best_iter = history[-1]
            logger.info(
                "Merging latest iteration %d from branch '%s'",
                best_iter.iteration,
                source_branch,
            )

        # Add merged insights to current campaign metadata
        if self._campaign_state:
            merged_meta = dict(self._campaign_state.metadata)
            merged: list[dict[str, object]] = []
            raw_merged = merged_meta.get("merged_from")
            if isinstance(raw_merged, list):
                merged = [m for m in raw_merged if isinstance(m, dict)]
            merged.append({
                "branch": source_branch,
                "iteration": best_iter.iteration,
                "timestamp": datetime.now().isoformat(),
                "strategy": strategy,
            })
            merged_meta["merged_from"] = merged
            self.db.update_iteration(self.campaign_id, self._iteration, merged_meta)

    @staticmethod
    def _load_jsonish(value: object) -> dict[str, object]:
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except ValueError:
                return {}
            return parsed if isinstance(parsed, dict) else {}
        return {}

    def _recent_kb_results(self) -> list[dict[str, object]]:
        """Read the loop's own history back from the KnowledgeBase.

        The rule-based hypothesis generators are inert without recent
        experiment records (defect: generate_hypotheses() was always
        called with recent_results=None, so a campaign could never
        propose anything from its own history).
        """
        if not self.knowledge_base:
            return []
        recent: list[dict[str, object]] = []
        for rec in self.knowledge_base.list_experiments(limit=20):
            # list_experiments returns metrics/config as JSON strings
            metrics = self._load_jsonish(rec.get("metrics"))
            recent.append({
                "model": rec.get("model_family", "unknown"),
                "task": rec.get("task", "unknown"),
                "val_accuracy": metrics.get("val_accuracy", 0),
                "bio_score": metrics.get("bio_score", 0),
                "config": self._load_jsonish(rec.get("config")),
            })
        return recent

    def run_iteration(  # noqa: C901, PLR0912 (proposal lifecycle branches are linear)
        self,
        n_experiments: int = 5,
        dry_run: bool = False,
    ) -> list[dict[str, object]]:
        """
        Run one iteration of the discovery loop.

        Args:
            n_experiments: Number of experiments to propose and run.
            dry_run: If True, only propose without executing.

        Returns:
            List of experiment results.
        """
        self._iteration += 1
        logger.info(
            "=== Campaign %s Iteration %d ===", self.campaign_id, self._iteration
        )

        insights = []
        if self.reasoner:
            insights = self.reasoner.analyze_knowledge_base()
            if insights:
                logger.info("KnowledgeBase insights (%d):", len(insights))
                for insight in insights[:3]:
                    logger.info("  - %s", insight)

        proposals = []
        if self.proposer:
            proposals = self.proposer.propose_batch(
                n_proposals=n_experiments,
                recent_results=self._recent_kb_results(),
            )

        if not proposals:
            logger.warning("No proposals generated. Skipping iteration.")
            self._record_iteration(proposals, [], insights)
            return []

        logger.info("Proposed %d experiments", len(proposals))

        # Human approval gate
        if self.human_approval_gate:
            approved = self._human_approval(proposals)
            proposals = [p for i, p in enumerate(proposals) if i in approved]
            if not proposals:
                logger.info("No proposals approved. Skipping.")
                self._record_iteration(proposals, [], insights)
                return []

        # Execute experiments
        results = []
        if not dry_run:
            for i, proposal in enumerate(proposals):
                logger.info(
                    "Executing proposal %d/%d: %s on %s",
                    i + 1,
                    len(proposals),
                    proposal.model,
                    proposal.task,
                )
                if self.ceec is not None and not self._dry_run_gate(proposal):
                    # Dry-run gate rejected the proposal: no pre-registration,
                    # no ledger row (TODO27 rev 4, improvement 1).
                    continue
                experiment = self._pre_register(proposal)
                try:
                    result = self._execute_proposal(proposal)
                    results.append(result)
                    self._post_ledger(experiment, proposal, result)
                    if self.knowledge_base:
                        self._update_knowledge_base(proposal, result)
                except (
                    Exception
                ) as e:  # broad: a failing trial must not stop the campaign
                    logger.error("Proposal %d failed: %s", i, e, exc_info=True)
                    self._fail_ledger(experiment, proposal, str(e))
                    results.append({
                        "proposal": {
                            "model": proposal.model,
                            "task": proposal.task,
                            "hypothesis": proposal.hypothesis,
                        },
                        "status": "failed",
                        "error": str(e),
                    })

        # Record and persist
        self._record_iteration(proposals, results, insights)

        # Update campaign state in DB
        if self._campaign_state:
            self.db.update_iteration(self.campaign_id, self._iteration)

        return results

    def _pre_register(self, proposal: ExperimentProposal) -> Experiment | None:
        """P2.1: governed proposals are pre-registered before execution."""
        if self.ceec is None:
            return None
        experiment = self.ceec.pre_register(proposal)
        logger.info("Pre-registered %s in CEEC ledger", experiment.id)
        return experiment

    def _post_ledger(
        self,
        experiment: Experiment | None,
        proposal: ExperimentProposal,
        result: dict[str, object],
    ) -> object | None:
        if experiment is not None and self.ceec is not None:
            return self.ceec.record(experiment, proposal, result)
        return None

    def _fail_ledger(
        self,
        experiment: Experiment | None,
        proposal: ExperimentProposal,
        error: str,
    ) -> None:
        if experiment is not None and self.ceec is not None:
            self.ceec.record_failure(experiment, proposal, error)

    def _dry_run_gate(self, proposal: ExperimentProposal) -> bool:
        """Constructor probe before pre-registration (TODO27 rev 4, imp. 1).

        Runs one synthetic ``train_step`` through the composed system. An
        incompatible cell (credit × topology shape crash, bad geometry)
        is rejected here without burning a governed ledger row — but it
        *is* recorded as covered (``_record_incompatible``), so the
        coverage proposer never re-proposes a structurally impossible
        cell (rev 5 fix: the first sweep stalled re-proposing 4 rejected
        cells forever).
        """
        try:
            self._execute_proposal(proposal, dry_run=True)
        except Exception as e:  # broad: any compose/settle crash rejects
            logger.exception("Dry-run gate rejected proposal on %s", proposal.task)
            self._record_incompatible(proposal, str(e))
            return False
        return True

    def _record_incompatible(self, proposal: ExperimentProposal, error: str) -> None:
        """Mark a dry-run-rejected cell covered in the KB (not the ledger).

        The KnowledgeEntry carries the full cell key, so
        ``ExperimentProposer._covered_cells`` treats the coordinate as
        measured (verdict: cannot execute). No ``add_experiment`` row —
        a zero-accuracy row would poison the surrogate.
        """
        kb = self.knowledge_base
        if kb is None:
            return
        if not (proposal.dynamics and proposal.credit and proposal.update):
            return
        from computronium.knowledge import KnowledgeEntry

        entry = KnowledgeEntry(
            id=(
                f"incompatible_{self.campaign_id}_{self._iteration}_"
                f"{int(time.time() * 1000)}"
            ),
            topic=f"incompatible:{proposal.task}",
            model_family=proposal.model,
            finding=f"cell cannot execute: {error[:160]}",
            details=str(proposal.geometry),
            confidence=0.0,
            tags=[
                "experiment",
                "structurally_incompatible",
                f"campaign:{self.campaign_id}",
            ],
            source="experiment",
            metrics={},
            hyperparameters={
                "geometry": proposal.geometry or {},
                "dynamics": proposal.dynamics,
                "credit": proposal.credit,
                "update": proposal.update,
            },
            extra={"campaign_id": self.campaign_id},
        )
        try:
            kb.add_entry(entry)
        except (KnowledgeBaseError, OSError, ValueError) as e:
            logger.warning("Failed to record incompatible cell: %s", e)

    def _execute_proposal(  # noqa: PLR0914 (single compose→fit→measure pipeline)
        self, proposal: ExperimentProposal, dry_run: bool = False
    ) -> dict[str, object]:
        """Execute a proposal: 5-D system -> SystemTrainer.

        Geometry overrides compose through the single round-trip path
        (``compose_proposal_system``); the task fence runs before any
        budget is spent (P1.4 — no proposal silently targets an
        unrunnable task).
        """
        from computronium.autoscientist.compose import (
            assert_task_runnable,
            compose_proposal_system,
        )
        from computronium.core.system_trainer import SystemTrainer, SystemTrainerConfig
        from computronium.core.utils.device import get_device
        from computronium.domains.factory import create_task

        assert_task_runnable(proposal.task)
        task = create_task(
            proposal.task or "mnist",
            device=str(get_device()),
            quick_mode=True,
            num_workers=0,  # campaign trials are small; workers cost more than they save
        )
        task.setup()
        # Vision tasks expose (C, H, W); factories want flat dims (see
        # construction.construct_model for the same canonicalization).
        input_dim = task.input_dim
        assert input_dim is not None  # noqa: S101 (task contract)
        if isinstance(input_dim, tuple | list):
            input_dim = int(math.prod(input_dim))
        lr_raw = proposal.hyperparams.get("lr")
        lr = (
            float(lr_raw)
            if isinstance(lr_raw, int | float)
            else _ruler_lr(
                proposal.task,
                str((proposal.geometry or {}).get("topology_type", "feedforward")),
            )
        )
        geometry = dict(proposal.geometry or {})
        system = compose_proposal_system(
            proposal.model,
            input_dim=int(input_dim),
            output_dim=int(task.output_dim or 1),
            lr=lr,
            geometry=geometry,
            dynamics=proposal.dynamics,
            credit=proposal.credit,
            update=proposal.update,
        )

        # Parameter-budget rematch (TODO28 fairness): fixed depth/hidden
        # spans a ~400x parameter spread across topologies (conv 3.8K vs
        # spatial_lattice 1.63M). One hidden_dim rescale per cell brings
        # geometry capacity within ~25% of the budget so mechanisms — not
        # capacity — dominate the comparison.
        budget_raw = proposal.hyperparams.get("param_budget")
        if isinstance(budget_raw, int | float) and budget_raw > 0:
            for _ in range(3):
                n_params = sum(p.numel() for p in system.geometry.parameters())
                if n_params <= 0 or abs(n_params - budget_raw) / budget_raw <= 0.25:
                    break
                scale = math.sqrt(float(budget_raw) / n_params)
                current = float(cast("int | float", geometry.get("hidden_dim", 64)))
                geometry["hidden_dim"] = max(8, int(current * scale))
                if geometry["hidden_dim"] == int(current):
                    break
                system = compose_proposal_system(
                    proposal.model,
                    input_dim=int(input_dim),
                    output_dim=int(task.output_dim or 1),
                    lr=lr,
                    geometry=geometry,
                    dynamics=proposal.dynamics,
                    credit=proposal.credit,
                    update=proposal.update,
                )
        param_count = sum(p.numel() for p in system.geometry.parameters())

        spectral_radius = (
            probe_spectral_radius(system, int(input_dim)) if param_count > 0 else 0.0
        )

        if dry_run:
            from computronium.autoscientist.compose import dry_run_system

            dry_run_system(system)
            return {
                "proposal": {"task": proposal.task},
                "status": "dry_run_ok",
                "lr": lr,
            }

        credit_alignment = _probe_credit_alignment(system, proposal, task)

        epochs_raw = proposal.hyperparams.get("epochs")
        max_epochs = (
            int(epochs_raw) if isinstance(epochs_raw, int | float) and epochs_raw else 5
        )
        limit_raw = proposal.hyperparams.get("limit_batches")
        config = SystemTrainerConfig(
            max_epochs=max_epochs,
            batch_size=64,
            track_energy=True,
            limit_train_batches=(
                int(limit_raw)
                if isinstance(limit_raw, int | float) and limit_raw
                else None
            ),
        )

        with SystemTrainer(
            system,
            config,
            task.get_dataloader("train"),  # type: ignore[attr-defined]
            task.get_dataloader("val"),  # type: ignore[attr-defined]
            step_callback=self.step_callback,
        ) as trainer:
            fit_started = time.monotonic()
            history = trainer.fit()
            walltime_s = round(time.monotonic() - fit_started, 3)
            last = history[-1] if history else {}

        # Multi-objective metrics (TODO31 Phase 1.3)
        flops = 0.0
        memory_mb = 0.0
        with contextlib.suppress(Exception):
            flops = float(estimate_train_step_flops(system, 64))
        with contextlib.suppress(Exception):
            memory_mb = get_gpu_memory_mb()

        # Settle-phase energy from telemetry (if available)
        energy_per_step = 0.0
        settle_steps_used = int(getattr(system.dynamics, "_settle_steps_used", 0) or 0)
        free_energy_final = 0.0
        if (
            hasattr(system.dynamics, "_free_energy_trace")
            and system.dynamics._free_energy_trace
        ):
            free_energy_final = float(system.dynamics._free_energy_trace[-1])
            if settle_steps_used > 0:
                energy_per_step = free_energy_final / settle_steps_used

        # Psi capacity from plasticity state (TODO31 Phase 3.7)
        psi_capacity = 0.0
        stability_plasticity_ratio = 0.0
        credit_efficiency = 0.0
        with contextlib.suppress(Exception):
            from computronium.core.plasticity.closed_form import (
                ClosedFormRidgePlasticity,
            )
            from computronium.core.plasticity.temporal_psi import TemporalPsiPlasticity

            # Get ψ state from the system's dynamics or credit
            psi_state = getattr(system.dynamics, "_psi_state", None)
            if psi_state is None:
                # Try to get from credit assignment
                psi_state = getattr(system.credit, "_psi_state", None)
            if psi_state:
                # Effective capacity: log2 of ridge effective rank + 1
                # For ridge: capacity ≈ log2(det(G + λI) / det(λI))
                # Simplified: sum of log(1 + eigenvalue/λ)
                if "G" in psi_state and "lambda" in psi_state:
                    import torch

                    G = psi_state["G"]
                    lam = psi_state["lambda"]
                    if isinstance(G, torch.Tensor) and G.dim() == 2:
                        eigvals = torch.linalg.eigvalsh(G).clamp(min=0)
                        capacity = (torch.log(1 + eigvals / lam)).sum().item()
                        psi_capacity = float(capacity)
                    elif "readout_m" in psi_state:
                        # For role-split: capacity from readout matrix
                        m = psi_state["readout_m"]
                        if isinstance(m, torch.Tensor):
                            psi_capacity = float(m.numel())
                elif "trace" in psi_state:
                    # Temporal ψ: trace of covariance
                    import torch

                    trace = psi_state["trace"]
                    if isinstance(trace, torch.Tensor):
                        psi_capacity = float(trace.log().sum().item())

        # Stability/Plasticity trade-off ratio
        if psi_capacity > 0 and spectral_radius > 0:
            stability_plasticity_ratio = float(spectral_radius / psi_capacity)

        # Credit efficiency objectives (TODO31 Phase 3.8)
        if credit_alignment != 0.0 and flops > 0:
            credit_efficiency = float(
                credit_alignment / (flops / 1e9)
            )  # alignment per GFLOP
        elif credit_alignment != 0.0 and param_count > 0:
            credit_efficiency = float(
                credit_alignment / (param_count / 1e6)
            )  # alignment per M param

        # Substrate-aware objectives (TODO31 Phase 3.6)
        substrate_objectives: dict[str, float] = {}
        with contextlib.suppress(Exception):
            from computronium.ontology.substrate.spec import (
                SubstrateSpec,
                compute_substrate_objectives,
            )

            substrate_spec = SubstrateSpec.from_config(system.substrate.config)
            runtime_stats = {
                "walltime_s": walltime_s,
                "memory_mb": memory_mb,
                "flops": flops,
                "latency_ms": 0.0,
            }
            settle_telemetry = {
                "energy_per_step": energy_per_step,
                "settle_steps_used": float(settle_steps_used),
                "free_energy_final": free_energy_final,
                "spike_rate": getattr(system.dynamics, "_spike_rate", 0.0),
                "event_density": getattr(system.dynamics, "_event_density", 0.0),
            }
            substrate_objectives = compute_substrate_objectives(
                substrate_spec, settle_telemetry, runtime_stats
            )

        return {
            "proposal": {
                "hypothesis": proposal.hypothesis,
                "model": proposal.model,
                "task": proposal.task,
                "propagator": proposal.propagator,
                "optimizer": proposal.optimizer,
                "geometry": proposal.geometry,
                "dynamics": proposal.dynamics,
                "credit": proposal.credit,
                "update": proposal.update,
                "justification": proposal.justification,
            },
            "status": "completed",
            "metrics": history,
            "final_accuracy": last.get("val_acc", 0.0),
            "final_loss": last.get("val_loss", 0.0),
            "train_accuracy": last.get("train_acc", 0.0),
            "epochs_completed": len(history),
            "param_count": param_count,
            "spectral_radius": spectral_radius,
            "settle_horizon": settle_steps_used,
            "credit_alignment": credit_alignment,
            "walltime_s": walltime_s,
            "lr": lr,
            # Multi-objective fields (TODO31)
            "flops": flops,
            "memory_mb": memory_mb,
            "energy_per_step": energy_per_step,
            "latency_ms": 0.0,  # populated on L1+ promotion
            "bp_deficit": 0.0,  # populated by atlas.apply_bp_deficit
            "ruler_walltime_ratio": 0.0,  # populated by atlas.apply_bp_deficit
            "ruler_energy_ratio": 0.0,  # populated by atlas.apply_bp_deficit
            "lyapunov_exponent": 0.0,
            "max_singular_value": 0.0,
            "psi_capacity": psi_capacity,
            "consolidation_cost": 0.0,
            "rewrite_rate": 0.0,
            "feedback_path_length": 0.0,
            "trace_variance": 0.0,
            "free_energy_final": free_energy_final,
            # Stability/Plasticity trade-off (TODO31 Phase 3.7)
            "stability_plasticity_ratio": stability_plasticity_ratio,
            # Credit efficiency (TODO31 Phase 3.8)
            "credit_efficiency": credit_efficiency,
            # Substrate-aware objectives
            **substrate_objectives,
            # Silent-divergence flag (TODO29 session 3): the funnel only
            # sees crashes; NaN loss/accuracy at "completed" status is the
            # quiet failure mode. Rides the numeric passthrough.
            "nan_loss": 1.0
            if not (
                math.isfinite(float(last.get("val_loss", 0.0)))
                and math.isfinite(float(last.get("val_acc", 0.0)))
            )
            else 0.0,
        }

    def _update_knowledge_base(
        self, proposal: ExperimentProposal, result: dict[str, object]
    ) -> None:
        """Store experiment result in KnowledgeBase with schema validation."""
        kb = self.knowledge_base
        if kb is None:
            return
        from computronium.knowledge import KnowledgeEntry

        # Cell-unique entry id: the second-resolution timestamp collided
        # whenever two cells completed in the same wall-clock second, and
        # INSERT OR REPLACE silently dropped the earlier result (rev 7
        # defect class, knowledge-entry half).
        cell_tag = (
            cell_key(
                str(proposal.dynamics),
                str(proposal.credit),
                str(proposal.update),
                str((proposal.geometry or {}).get("topology_type", "feedforward")),
            )
            if proposal.dynamics and proposal.credit and proposal.update
            else f"{int(time.time() * 1000)}_{proposal.model}|{proposal.task}"
        )
        entry = KnowledgeEntry(
            id=f"campaign_{self.campaign_id}_iter{self._iteration}_{cell_tag}",
            topic=f"experiment:{proposal.task}",
            model_family=proposal.model,
            finding=(
                f"Accuracy: {result.get('final_accuracy', 'N/A'):.4f}, "
                f"Loss: {result.get('final_loss', 'N/A'):.4f}"
            ),
            details=(
                f"Hypothesis: {proposal.hypothesis}\n"
                f"Propagator: {proposal.propagator}\n"
                f"Optimizer: {proposal.optimizer}\n"
                f"Config: {proposal.hyperparams}\n"
                f"Epochs: {result.get('epochs_completed', 'N/A')}"
            ),
            confidence=_metric(result.get("final_accuracy")),
            tags=[
                "experiment",
                proposal.task,
                proposal.model,
                f"campaign:{self.campaign_id}",
                *proposal.tags,
                *(["nan_loss"] if result.get("nan_loss") else []),
            ],
            source="experiment",
            metrics={
                k: v
                for k, v in result.items()
                if isinstance(v, (int, float)) and v is not None
            },
            hyperparameters={
                **(
                    proposal.hyperparams
                    if isinstance(proposal.hyperparams, dict)
                    else {"raw": str(proposal.hyperparams)}
                ),
                "geometry": proposal.geometry or {},
                "dynamics": proposal.dynamics,
                "credit": proposal.credit,
                "update": proposal.update,
            },
            extra={
                "campaign_id": self.campaign_id,
                "campaign_iteration": self._iteration,
                "branch": self.branch_name,
            },
        )
        try:
            kb.add_entry(entry)
        except (KnowledgeBaseError, OSError, ValueError) as e:
            logger.warning("Failed to update KnowledgeBase: %s", e)
        # Experiments-table row: the surrogate's and coverage matrix's
        # read path (P1.2b) — config carries the full grid axes.
        metrics: dict[str, float] = {
            k: float(v)
            for k, v in result.items()
            if isinstance(v, (int, float)) and v is not None
        }
        # The surrogate's default target is val_accuracy; the executor
        # reports final_accuracy. Record both names or the surrogate
        # never sees a target (rev 7 defect: 0 valid records).
        if "final_accuracy" in metrics:
            metrics.setdefault("val_accuracy", metrics["final_accuracy"])
        try:
            kb.add_experiment(
                name=f"campaign_iter{self._iteration}_{cell_tag}",
                model_family=proposal.model,
                task=proposal.task or "unknown",
                config={
                    **(
                        proposal.hyperparams
                        if isinstance(proposal.hyperparams, dict)
                        else {}
                    ),
                    "geometry": proposal.geometry or {},
                    "dynamics": proposal.dynamics,
                    "credit": proposal.credit,
                    "update": proposal.update,
                },
                metrics=metrics,
                experiment_id=f"camp_{self.campaign_id}_iter{self._iteration}_{cell_tag}",
            )
        except (KnowledgeBaseError, OSError, ValueError) as e:
            logger.warning("Failed to update KnowledgeBase: %s", e)

    def _record_iteration(
        self,
        proposals: list,
        results: list[dict[str, object]],
        insights: list[str],
    ) -> None:
        """Record iteration to database and checkpoint."""
        record = IterationRecord(
            iteration=self._iteration,
            timestamp=datetime.now().isoformat(),
            branch_name=self.branch_name,
            n_proposals=len(proposals),
            n_completed=sum(1 for r in results if r.get("status") == "completed"),
            n_failed=sum(1 for r in results if r.get("status") == "failed"),
            proposals=[
                {
                    "model": p.model,
                    "task": p.task,
                    "hypothesis": p.hypothesis[:100],
                    "propagator": p.propagator,
                    "priority": p.priority,
                }
                for p in proposals
            ],
            results=[
                {
                    "status": r.get("status"),
                    "final_accuracy": r.get("final_accuracy"),
                    "final_loss": r.get("final_loss"),
                }
                for r in results
            ],
            insights=insights,
        )

        self.db.add_iteration_record(record)

        # Save checkpoint every 5 iterations
        if self._iteration % 5 == 0 and self._campaign_state:
            updated_state = CampaignState(
                campaign_id=self._campaign_state.campaign_id,
                branch_name=self._campaign_state.branch_name,
                parent_branch=self._campaign_state.parent_branch,
                iteration=self._iteration,
                created_at=self._campaign_state.created_at,
                updated_at=datetime.now().isoformat(),
                config=self._campaign_state.config,
                metadata=self._campaign_state.metadata,
            )
            self.checkpointer.save_checkpoint(
                updated_state, self.db.get_iteration_history(self.branch_name)
            )

        # Also save JSON log (backward compatible)
        log_path = self.output_dir / f"iteration_{self._iteration:04d}.json"
        with log_path.open("w") as f:
            json.dump(asdict(record), f, indent=2, default=str)

        logger.info(
            "Iteration %d logged (completed: %d, failed: %d)",
            self._iteration,
            record.n_completed,
            record.n_failed,
        )

    def _human_approval(self, proposals: list) -> list[int]:
        """Gate for human approval of expensive runs."""
        logger.info("Human approval gate: %d proposals pending", len(proposals))
        if not proposals:
            return []
        if not sys.stdin.isatty():
            auto_msg = (
                "stdin is not a TTY; auto-approving all proposals. "
                "Provide BIOPL_AUTO_APPROVE=0 to deny."
            )
            if os.environ.get("BIOPL_AUTO_APPROVE", "1") == "0":
                logger.warning(auto_msg + " Denying all (BIOPL_AUTO_APPROVE=0).")
                return []
            logger.info(auto_msg)
            return list(range(len(proposals)))
        approved: list[int] = []
        for idx, proposal in enumerate(proposals):
            label = (
                getattr(proposal, "name", None) or f"{proposal.model}/{proposal.task}"
            )
            try:
                answer = (
                    input(f"Approve proposal {idx} ({label})? [y/N] ").strip().lower()
                )
            except EOFError:
                logger.warning("EOF on stdin; auto-approving remaining proposals")
                approved.extend(range(idx, len(proposals)))
                return approved
            if answer == "y":
                approved.append(idx)
        return approved

    def save_checkpoint(self, filename: str | None = None) -> Path:
        """Manually save a checkpoint."""
        if not self._campaign_state:
            raise RuntimeError("No campaign state to save")

        updated_state = CampaignState(
            campaign_id=self._campaign_state.campaign_id,
            branch_name=self._campaign_state.branch_name,
            parent_branch=self._campaign_state.parent_branch,
            iteration=self._iteration,
            created_at=self._campaign_state.created_at,
            updated_at=datetime.now().isoformat(),
            config=self._campaign_state.config,
            metadata=self._campaign_state.metadata,
        )
        return self.checkpointer.save_checkpoint(
            updated_state,
            self.db.get_iteration_history(self.branch_name),
            filename,
        )

    def load_checkpoint(self, filepath: str | Path) -> None:
        """Load campaign state from a checkpoint file."""
        campaign, _history = self.checkpointer.load_checkpoint(filepath)
        self._campaign_state = campaign
        self.campaign_id = campaign.campaign_id
        self.branch_name = campaign.branch_name
        self.parent_branch = campaign.parent_branch
        self._iteration = campaign.iteration
        self._config = campaign.config
        logger.info(
            "Loaded checkpoint: iteration %d, branch %s",
            self._iteration,
            self.branch_name,
        )

    def get_summary(self) -> dict[str, object]:
        """Get campaign summary statistics."""
        history = self.db.get_iteration_history(self.branch_name)

        completed = []
        for entry in history:
            for r in entry.results:
                if r.get("status") == "completed":
                    completed.append(r)

        total_experiments = sum(entry.n_proposals for entry in history)
        best_accuracy = 0.0
        if completed:
            best_accuracy = max(r.get("final_accuracy", 0) for r in completed)

        return {
            "campaign_id": self.campaign_id,
            "branch_name": self.branch_name,
            "parent_branch": self.parent_branch,
            "iterations": self._iteration,
            "total_experiments": total_experiments,
            "completed": len(completed),
            "best_accuracy": best_accuracy,
            "output_dir": str(self.output_dir),
            "db_path": str(self.db_path),
        }

    def get_history(self) -> list[IterationRecord]:
        """Get full iteration history for current branch."""
        return self.db.get_iteration_history(self.branch_name)

    @contextmanager
    def run_campaign(
        self,
        n_iterations: int = 10,
        n_experiments_per_iter: int = 5,
        checkpoint_interval: int = 5,
    ):
        """
        Context manager for running a multi-iteration campaign.

        Usage:
            with campaign.run_campaign(n_iterations=20) as results:
                # results is a list of all iteration results
                pass
        """
        all_results = []
        try:
            for i in range(n_iterations):
                results = self.run_iteration(
                    n_experiments=n_experiments_per_iter,
                )
                all_results.extend(results)

                if (i + 1) % checkpoint_interval == 0:
                    self.save_checkpoint()

            yield all_results
        finally:
            # Always save final checkpoint
            self.save_checkpoint()
            logger.info(
                "Campaign %s completed. Final summary: %s",
                self.campaign_id,
                self.get_summary(),
            )


def create_campaign(
    knowledge_base: KnowledgeBase | None = None,
    output_dir: str = "autoscientist_campaigns",
    branch: str = "main",
    resume: bool = False,
    **kwargs,
) -> AutoScientistCampaign:
    """Factory function to create or resume a campaign."""
    return AutoScientistCampaign(
        knowledge_base=knowledge_base,
        output_dir=output_dir,
        branch_name=branch,
        resume=resume,
        **kwargs,
    )


def list_campaigns(db_path: str | Path) -> list[CampaignState]:
    """List all campaigns in a database."""
    db = CampaignDatabase(db_path)
    return db.list_campaigns()


def list_branches(db_path: str | Path) -> list[str]:
    """List all branches in a database."""
    db = CampaignDatabase(db_path)
    return db.list_branches()


__all__ = [
    "AutoScientistCampaign",
    "CampaignCheckpointer",
    "CampaignDatabase",
    "CampaignState",
    "IterationRecord",
    "create_campaign",
    "list_branches",
    "list_campaigns",
    "logger",
]
