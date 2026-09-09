"""Paper-claim lock (TODO17 §3.1).

Every claim in every ``active_draft`` paper must resolve to an existing
artifact: a figure run record with a live demo test, a log file that
exists, or a data table that exists. A claim without a backing artifact
fails this test — claims without artifacts do not ship (§10 stop-loss 4).
"""

import json
from pathlib import Path

from computronium.papers.registry import FOLDS, PAPERS

REPO_ROOT = Path(__file__).resolve().parents[2]
RECORDS_DIR = REPO_ROOT / "docs" / "figures" / "run_records"


def test_active_draft_claims_resolve_to_artifacts() -> None:
    for paper_id, paper in PAPERS.items():
        if paper["status"] != "active_draft":
            continue
        for fig in paper["evidence"].get("figures", []):
            record = RECORDS_DIR / f"{fig}.json"
            assert record.exists(), f"{paper_id}: figure record {fig} missing"
            demo_test = REPO_ROOT / json.loads(record.read_text())["demo_test"]
            assert demo_test.exists(), f"{paper_id}: demo test for {fig} deleted"
        for path in paper["evidence"].get("run_records", []):
            assert (REPO_ROOT / path).exists(), f"{paper_id}: evidence {path} missing"


def test_held_out_metric_is_reproducible() -> None:
    """The cited held-out number must appear in the cited data table's
    provenance chain (the fit output log regenerates from the CSV)."""
    paper = PAPERS["icu_law"]
    cited = paper["evidence"]["held_out_validation"]
    log = REPO_ROOT / "logs" / "w16_icu_fit.log"
    assert log.exists(), "icu_law: held-out fit log missing — rerun fit_icu_model"
    assert f"{cited:.3f}" in log.read_text(), (
        f"icu_law: cited held-out {cited} not reproducible from the fit log"
    )


def test_fold_decisions_are_recorded() -> None:
    folded = {pid for pid, p in PAPERS.items() if p.get("folded_into") is not None}
    assert folded == set(FOLDS), "every fold decision must be recorded in FOLDS"
