"""Budget (§4.5) + Evidence (§4.6) adapter tests — content beyond the generic purity lock."""

from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING

from computronium.ui.adapters import adapt_budget, adapt_evidence
from computronium.ui.data_adapters import AdapterContext
from computronium.visualization.live_atlas import (
    EmbedCache,
    _objectives_from_heartbeat,
    render_snapshot,
    resolve_log_path,
)
from tests.ui.fixture import seed_campaign_root

if TYPE_CHECKING:
    from pathlib import Path


def _context(root: Path) -> AdapterContext:
    snapshot = render_snapshot(
        root,
        resolve_log_path(root, root / "logs" / "continuous_500.log"),
        EmbedCache(),
        objectives=_objectives_from_heartbeat(root),
        with_atlas=False,
    )
    return AdapterContext(root=root, snapshot=snapshot)


def test_budget_content(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    data = adapt_budget(_context(root).snapshot, root)
    assert data.measured == 4
    assert data.maturation.get("l0") == 4
    assert data.cells_per_hour > 0
    assert data.breakdown, "cost spread rows expected from 4 measured cells"


def test_evidence_missing_ledger(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    root.mkdir(parents=True)
    data = adapt_evidence(_context(root).snapshot, root)
    assert data.beliefs == [] and data.experiments == []
    assert data.empty_reason == "no CEEC ledger found"


def test_evidence_reads_ledger(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    ledger = root / "ledger.sqlite"
    with sqlite3.connect(ledger) as conn:
        conn.execute(
            "CREATE TABLE beliefs (id TEXT PRIMARY KEY, statement TEXT NOT NULL,"
            " type TEXT NOT NULL, scope JSON NOT NULL,"
            " posterior_method TEXT, created_at TEXT NOT NULL)"
        )
        conn.execute(
            "CREATE TABLE belief_revisions (id TEXT PRIMARY KEY, belief_id TEXT NOT NULL,"
            " probability_low REAL NOT NULL, probability_high REAL NOT NULL,"
            " probability_point REAL, probability_method TEXT, uncertainty TEXT NOT NULL,"
            " evidence_weight TEXT NOT NULL, generality TEXT NOT NULL, status TEXT NOT NULL,"
            " rationale TEXT NOT NULL, created_at TEXT NOT NULL)"
        )
        conn.execute(
            "CREATE TABLE experiments (id TEXT PRIMARY KEY, question TEXT NOT NULL,"
            " rationale TEXT NOT NULL, scope JSON NOT NULL, target_beliefs JSON NOT NULL,"
            " target_goals JSON NOT NULL, design JSON NOT NULL, prediction TEXT NOT NULL,"
            " prediction_probability JSON, controls JSON NOT NULL, metrics JSON NOT NULL,"
            " budget TEXT NOT NULL, cost_low REAL, cost_high REAL,"
            " falsification_criterion TEXT NOT NULL, overturn_criterion TEXT NOT NULL,"
            " hard_gates JSON NOT NULL, status TEXT NOT NULL, pre_registered_at TEXT,"
            " started_at TEXT, completed_at TEXT, created_at TEXT NOT NULL)"
        )
        conn.execute(
            "CREATE TABLE decisions (id TEXT PRIMARY KEY, timestamp TEXT NOT NULL,"
            " state_hash TEXT NOT NULL, candidate_experiments JSON NOT NULL,"
            " scores JSON NOT NULL, selected_experiment TEXT, overrides JSON NOT NULL,"
            " constraints_checked JSON NOT NULL, policy_version TEXT,"
            " rationale TEXT NOT NULL)"
        )
        conn.execute(
            "INSERT INTO beliefs VALUES ('b1','psi helps','empirical','{}',NULL,'t0')"
        )
        conn.execute(
            "INSERT INTO belief_revisions VALUES ('r1','b1',0.4,0.8,0.6,'m',"
            " 'u','w','g','supported','why','t1')"
        )
        conn.execute(
            "INSERT INTO experiments VALUES ('e1','does psi help?','r','{}','[]','[]',"
            " '{}','yes',NULL,'{}','{}','small',1.0,2.0,'f','o','[]',"
            " 'completed',NULL,NULL,NULL,'t2')"
        )
        conn.execute(
            "INSERT INTO decisions VALUES ('d1','t3','h','[]','{}','e1','[]','[]',NULL,'best')"
        )
    data = adapt_evidence(_context(root).snapshot, root)
    assert [(b.id, b.status, b.probability_point) for b in data.beliefs] == [
        ("b1", "supported", 0.6)
    ]
    assert [(e.id, e.status) for e in data.experiments] == [("e1", "completed")]
    assert [(d.id, d.selected_experiment) for d in data.decisions] == [("d1", "e1")]
    assert data.empty_reason == ""
