"""Defect funnel (TODO29 Phase 2): ID stability, replay semantics,
quarantine suppression, and the failure-branch emission contract."""

from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING

from hypothesis import given
from hypothesis import strategies as st

import computronium.autoscientist.broad_map as bm
from computronium.autoscientist.bridge import ExperimentProposal
from computronium.autoscientist.broad_map import BroadMappingCampaign
from computronium.autoscientist.campaign import AutoScientistCampaign
from computronium.autoscientist.defects import (
    DefectRecord,
    append_defect,
    defect_id,
    quarantined_cells,
    read_defects,
    resolve_defect,
)

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

_HEX = st.integers(min_value=0, max_value=2**48)
_TMP = st.text(alphabet="abc0123_/-", min_size=1, max_size=12)


def _proposal(hypothesis: str, **axes: str) -> ExperimentProposal:
    return ExperimentProposal(
        hypothesis=hypothesis,
        model="eqprop",
        task="digits",
        geometry={"topology_type": "feedforward", "depth": 2, "hidden_dim": 32},
        dynamics=axes.get("dynamics", "energy_minimization"),
        credit=axes.get("credit", "prediction"),
        update=axes.get("update", "euclidean"),
    )


class _FakeProposer:
    def __init__(self, proposals: list[ExperimentProposal]) -> None:
        self._proposals = proposals

    def propose_batch(
        self, n_proposals: int, recent_results: list[dict[str, object]] | None = None
    ) -> list[ExperimentProposal]:
        return self._proposals


def _campaign(tmp_path: Path) -> BroadMappingCampaign:
    (tmp_path / "campaign").mkdir(parents=True, exist_ok=True)
    return BroadMappingCampaign(
        knowledge_base=None,
        output_dir=str(tmp_path / "campaign"),
        db_path=tmp_path / "campaign" / "campaign.db",
        branch_name="defect_test",
        ceec_ledger_path=tmp_path / "ledger.sqlite",
        voids_path=tmp_path / "structural_voids.jsonl",
        defects_path=tmp_path / "runtime_defects.jsonl",
    )


@given(addr_a=_HEX, addr_b=_HEX, tmp_a=_TMP, tmp_b=_TMP)
def test_defect_id_stable_under_address_and_path_noise(
    addr_a: int, addr_b: int, tmp_a: str, tmp_b: str
) -> None:
    msg_a = f"expected 2D input at 0x{addr_a:x} in /tmp/{tmp_a}.pt"
    msg_b = f"expected 2D input at 0x{addr_b:x} in /tmp/{tmp_b}.pt"
    assert defect_id("RuntimeError", msg_a) == defect_id("RuntimeError", msg_b)


def test_defect_id_discriminates_shapes_and_classes() -> None:
    a = defect_id("RuntimeError", "expected [2, 3] in layer conv1")
    b = defect_id("RuntimeError", "expected [2, 4] in layer conv1")
    c = defect_id("ValueError", "expected [2, 3] in layer conv1")
    assert len({a, b, c}) == 3
    assert len(a) == 12


def test_replay_last_status_wins(tmp_path: Path) -> None:
    path = tmp_path / "runtime_defects.jsonl"

    def row(ts: float, cell: str, status: str) -> DefectRecord:
        return DefectRecord(
            defect_id="aaaaaaaaaaaa",
            timestamp=ts,
            task="digits",
            cell=cell,
            error_class="RuntimeError",
            message="boom",
            traceback_tail="",
            status=status,  # type: ignore[arg-type]
        )

    append_defect(path, row(1.0, "d|c|u|t", "open"))
    assert quarantined_cells(read_defects(path)) == {"d|c|u|t"}
    assert [r.timestamp for r in read_defects(path)] == [1.0]
    append_defect(path, row(2.0, "d|c|u|t", "resolved"))
    assert quarantined_cells(read_defects(path)) == frozenset()
    # Re-opened after a fix regressed: cell quarantined again.
    append_defect(path, row(3.0, "d|c|u|t", "open"))
    assert quarantined_cells(read_defects(path)) == {"d|c|u|t"}


def test_one_bug_quarantines_all_affected_cells(tmp_path: Path) -> None:
    path = tmp_path / "runtime_defects.jsonl"
    cells = [f"dyn|cred|upd|top{i}" for i in range(3)]
    for i, cell in enumerate(cells):
        append_defect(
            path,
            DefectRecord(
                defect_id="bbbbbbbbbbbb",
                timestamp=float(i),
                task="digits",
                cell=cell,
                error_class="RuntimeError",
                message="device poisoning",
                traceback_tail="",
                status="open",
            ),
        )
    assert quarantined_cells(read_defects(path)) == frozenset(cells)
    assert resolve_defect(path, "bbbbbbbbbbbb") == 1
    assert quarantined_cells(read_defects(path)) == frozenset()
    assert resolve_defect(path, "bbbbbbbbbbbb") == 0  # idempotent


def test_unknown_defect_resolve_is_noop(tmp_path: Path) -> None:
    assert resolve_defect(tmp_path / "none.jsonl", "deadbeefcafe") == 0


def test_driver_suppresses_quarantined_cell_until_resolved(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(bm, "GRID_DYNAMICS", ("energy_minimization", "instantaneous"))
    monkeypatch.setattr(bm, "GRID_CREDITS", ("prediction", "null"))
    monkeypatch.setattr(bm, "GRID_UPDATES", ("euclidean",))
    monkeypatch.setattr(bm, "GRID_TOPOLOGIES", ("feedforward",))
    defects_path = tmp_path / "runtime_defects.jsonl"
    quarantined_key = "energy_minimization|prediction|euclidean|feedforward"
    append_defect(
        defects_path,
        DefectRecord(
            defect_id="cccccccccccc",
            timestamp=1.0,
            task="digits",
            cell=quarantined_key,
            error_class="RuntimeError",
            message="boom",
            traceback_tail="",
            status="open",
        ),
    )
    kb_path = tmp_path / "kb.sqlite"  # absent: seen-set stays empty

    def proposed_keys(seed: int) -> set[str]:
        driver = bm.StratifiedRandomDriver(
            kb_path,
            task="digits",
            cells=10,
            epochs=1,
            seed=seed,
            defects_path=defects_path,
        )
        return {p.tags[-1] for p in driver.propose_batch(10)}

    keys = proposed_keys(0)
    assert len(keys) == 3
    assert quarantined_key not in keys

    assert resolve_defect(defects_path, "cccccccccccc") == 1
    keys_after = proposed_keys(0)
    assert len(keys_after) == 4
    assert quarantined_key in keys_after


def test_failure_burst_emits_defect_closes_ledger_and_continues(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    campaign = _campaign(tmp_path)
    broken = _proposal("broken cell", dynamics="instantaneous")
    healthy = _proposal("healthy cell")
    campaign.proposer = _FakeProposer([broken, healthy])  # type: ignore[assignment]

    def fake_execute(
        self: AutoScientistCampaign, proposal: ExperimentProposal, dry_run: bool = False
    ) -> dict[str, object]:
        if dry_run:
            return {
                "proposal": {"task": proposal.task},
                "status": "dry_run_ok",
                "lr": 0.01,
            }
        if proposal.hypothesis == "broken cell":
            msg = "expected 2D input at 0x7f12ab in /tmp/tmpdefect/x.pt"
            raise RuntimeError(msg)
        return {
            "proposal": {"task": proposal.task},
            "status": "completed",
            "final_accuracy": 0.5,
            "final_loss": 0.7,
            "epochs_completed": 1,
            "lr": 0.01,
        }

    monkeypatch.setattr(AutoScientistCampaign, "_execute_proposal", fake_execute)
    results = campaign.run_iteration(n_experiments=2)
    assert [r["status"] for r in results] == ["failed", "completed"]

    records = read_defects(tmp_path / "runtime_defects.jsonl")
    assert len(records) == 1
    row = records[0]
    assert row.status == "open"
    assert row.error_class == "RuntimeError"
    # Addresses/tmp paths are preserved in the record, normalized in the ID.
    assert "0x7f12ab" in row.message
    assert row.defect_id == defect_id("RuntimeError", row.message)
    assert row.cell == "instantaneous|prediction|euclidean|feedforward"
    assert "fake_execute" in row.traceback_tail

    with sqlite3.connect(tmp_path / "ledger.sqlite") as conn:
        statuses = {row[0] for row in conn.execute("SELECT status FROM experiments")}
        missing = conn.execute(
            "SELECT COUNT(*) FROM evidence WHERE kind = 'missing'"
        ).fetchone()[0]
    assert statuses == {"failed", "completed"}
    assert missing == 1


def test_proposal_rationale_names_stratum_count(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TODO30 §3.1: each proposal carries a per-cell reason string that
    reports the stratum count *before* the proposal (least-sampled first)."""
    monkeypatch.setattr(bm, "GRID_DYNAMICS", ("energy_minimization", "instantaneous"))
    monkeypatch.setattr(bm, "GRID_CREDITS", ("prediction",))
    monkeypatch.setattr(bm, "GRID_UPDATES", ("euclidean",))
    monkeypatch.setattr(bm, "GRID_TOPOLOGIES", ("feedforward",))
    driver = bm.StratifiedRandomDriver(
        tmp_path / "kb.sqlite", task="digits", cells=4, epochs=1, seed=0
    )
    proposals = driver.propose_batch(4)
    seen: dict[str, int] = {}
    for proposal in proposals:
        assert str(proposal.dynamics) in proposal.justification
        assert proposal.justification.startswith("Balancing under-sampled triple")
        count = int(proposal.justification.split("stratum count ")[1].split(" ")[0])
        assert count == seen.get(str(proposal.dynamics), 0)
        seen[str(proposal.dynamics)] = count + 1
