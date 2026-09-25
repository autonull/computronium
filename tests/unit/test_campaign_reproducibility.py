"""P1.1 acceptance + rev-4 improvements: bit-for-bit reproducibility of a
geometry proposal through ``AutoScientistCampaign._execute_proposal``, and
the dry-run constructor gate that rejects incompatible cells before a
governed ledger row is written (TODO27 §5 entry point, items 1–2)."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import replace
from typing import TYPE_CHECKING

from computronium.autoscientist.bridge import ExperimentProposal
from computronium.autoscientist.campaign import AutoScientistCampaign
from computronium.utils import seed_everything

if TYPE_CHECKING:
    from pathlib import Path

PROPOSAL = ExperimentProposal(
    hypothesis="geometry override survives the executor round-trip",
    model="eqprop",
    task="digits",
    geometry={
        "topology_type": "recurrent",
        "depth": 4,
        "hidden_dim": 32,
        "init_scheme": "mupc",
    },
)


def make_campaign(tmp_path: Path, **kwargs: object) -> AutoScientistCampaign:
    return AutoScientistCampaign(
        output_dir=str(tmp_path / "out"),
        db_path=tmp_path / "campaign.db",
        **kwargs,  # type: ignore[arg-type]
    )


class _FakeProposer:
    def __init__(self, proposals: list[ExperimentProposal]) -> None:
        self._proposals = proposals

    def propose_batch(
        self, n_proposals: int, recent_results: list[dict[str, object]] | None = None
    ) -> list[ExperimentProposal]:
        return self._proposals


def test_geometry_execution_is_bit_for_bit_reproducible(tmp_path: Path) -> None:
    # One epoch is enough to prove the property: the claim is that two
    # identically-seeded executions emit identical metrics, not that the
    # cell learned anything. The default 5-epoch budget made this the
    # single most expensive test in the suite (~42s) for no extra signal.
    proposal = replace(PROPOSAL, hyperparams={**PROPOSAL.hyperparams, "epochs": 1})
    campaign = make_campaign(tmp_path)
    histories = []
    for _ in range(2):
        seed_everything(1234, deterministic=True)
        result = campaign._execute_proposal(proposal)
        assert result["status"] == "completed"
        assert int(str(result["epochs_completed"])) > 0
        histories.append(json.dumps(result["metrics"], sort_keys=True))
    assert histories[0] == histories[1]


def test_dry_run_flags_composed_system(tmp_path: Path) -> None:
    campaign = make_campaign(tmp_path)
    result = campaign._execute_proposal(PROPOSAL, dry_run=True)
    assert result["status"] == "dry_run_ok"


def test_dry_run_gate_rejects_fenced_proposal(tmp_path: Path) -> None:
    campaign = make_campaign(tmp_path, ceec_ledger_path=tmp_path / "ledger.sqlite")
    proposal = ExperimentProposal(
        hypothesis="fenced LM lane", model="eqprop", task="char_ngram"
    )
    assert campaign._dry_run_gate(proposal) is False
    with sqlite3.connect(tmp_path / "ledger.sqlite") as conn:
        n = conn.execute("SELECT COUNT(*) FROM experiments").fetchone()[0]
    assert n == 0


def test_dry_run_gate_accepts_runnable_proposal(tmp_path: Path) -> None:
    campaign = make_campaign(tmp_path, ceec_ledger_path=tmp_path / "ledger.sqlite")
    assert campaign._dry_run_gate(PROPOSAL) is True


def test_gated_proposal_never_reaches_pre_registration(tmp_path: Path) -> None:
    campaign = make_campaign(tmp_path, ceec_ledger_path=tmp_path / "ledger.sqlite")
    fenced = ExperimentProposal(hypothesis="fenced", model="eqprop", task="char_ngram")
    campaign.proposer = _FakeProposer([fenced])  # type: ignore[assignment]
    pre_registered: list[ExperimentProposal] = []
    campaign._pre_register = pre_registered.append  # type: ignore[method-assign]
    results = campaign.run_iteration(n_experiments=1)
    assert results == []
    assert pre_registered == []


def test_incompatible_cell_is_recorded_covered(tmp_path: Path) -> None:
    """Rev-5 fix: a dry-run-rejected cell enters the coverage matrix, so the
    proposer never re-proposes a structurally impossible coordinate."""
    from computronium.autoscientist.proposer import ExperimentProposer
    from computronium.knowledge import KnowledgeBase

    kb = KnowledgeBase(tmp_path / "kb.sqlite")
    campaign = make_campaign(
        tmp_path, knowledge_base=kb, ceec_ledger_path=tmp_path / "ledger.sqlite"
    )
    # energy_minimization × attention is structurally impossible
    # ("Energy-based settling requires a layered geometry" — observed in
    # G1 sweep run 1 as 18 identical rejections).
    bad = ExperimentProposal(
        hypothesis="structurally impossible cell",
        model="eqprop",
        task="digits",
        geometry={"topology_type": "attention", "depth": 2, "hidden_dim": 32},
        dynamics="energy_minimization",
        credit="thermodynamic_contrast",
        update="euclidean",
    )
    assert campaign._dry_run_gate(bad) is False
    proposer = ExperimentProposer(kb)
    key = "energy_minimization|thermodynamic_contrast|euclidean|attention"
    assert key in proposer._covered_cells()
    fresh = [p.tags[-1] for p in proposer.propose_coverage_cells(6, task="digits")]
    assert key not in fresh


def test_ruler_lr_scoping() -> None:
    """The calibrated ceiling lr applies to the measured topology only.

    Non-feedforward default is 1e-2 per the topology-lr calibration
    probe (scripts/probes/d28_topology_lr_probe.py): the old flat 1e-3
    starved every non-feedforward cell (recurrent em 0.161 vs 0.856).
    """
    from computronium.autoscientist.campaign import _ruler_lr

    assert _ruler_lr("digits", "feedforward") == 0.01
    assert _ruler_lr("digits", "recurrent") == 1e-2
    assert _ruler_lr("not_a_ruler_task", "feedforward") == 1e-2


def test_explicit_lr_beats_ruler_default(tmp_path: Path) -> None:
    campaign = make_campaign(tmp_path)
    explicit = ExperimentProposal(
        hypothesis="explicit lr wins",
        model="eqprop",
        task="digits",
        geometry={"topology_type": "feedforward", "depth": 2, "hidden_dim": 64},
        hyperparams={"lr": 1e-4},
    )
    result = campaign._execute_proposal(explicit, dry_run=True)
    assert result["status"] == "dry_run_ok"
    assert result["lr"] == 1e-4
