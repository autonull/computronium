"""The demo screenplay's truth condition: every beat runs, none contradicts.

TODO66 §4.5. The video is only honest if this test is green: the commands in
``docs/DEMO.md`` are the commands executed here, and each beat's contract is
asserted from their real output — a priced space, measured records, a ledger
entry, a governed report with a claim line and limitations, and a coverage
report that exits 0 (§2.3).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from computronium.cli.__main__ import main as comp
from computronium.experiment.evidence import RecordStore, StoreConfig

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.demo


@pytest.mark.timeout(300)
def test_the_seven_beats_run_and_do_not_contradict(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = tmp_path / "demo.duckdb"

    assert comp(["run", "demo", "--store", str(store), "--dry-run"]) == 0
    dry_run = capsys.readouterr().out
    assert "declared cells:" in dry_run
    assert "legal:" in dry_run

    assert comp(["demo", "--store", str(store)]) == 0
    output = capsys.readouterr().out
    assert "[0]" in output and "[6]" in output

    with RecordStore(StoreConfig(path=store, read_only=True)) as records:
        runs = records.query_runs()
        assert runs, "the demo wrote no run"
        measured = records.query_records(run_id=runs[0].run_id)

    assert len(measured) >= 4, "beat 2 must measure the declared arms"
    assert all(record.status.gate_verdict.value == "PASS" for record in measured)

    # Beat 2: the controlled contrast — one axis varies, the rest are fixed.
    assert "Credit Ablation [group 1, fixed:" in output
    # Beat 3: the ledger lists the run.
    assert "Records" in output or "recs=" in output
    # Beat 4: a governed claim line, limitations, and no eligibility/claim split.
    assert "n=" in output
    assert "Limitations" in output
    if "(none — see Limitations)" in output:
        assert "Claim-Eligible Cells: 0" in output
    else:
        assert "Claim-Eligible Cells: 0" not in output
    # Beat 5: coverage exits 0 (locks §2.3 forever).
    assert "Coverage Report" in output
    # Beat 6: the results we own, with their numbers unchanged.
    assert "-1.19" in output and "10.025" in output


@pytest.mark.timeout(300)
def test_two_clean_runs_visit_the_same_cells(tmp_path: Path) -> None:
    """G10: the replay hash covers the visited cells, not the measured values.

    Two clean stores, same declaration: the sorted ``measurement_key`` sets and
    therefore the replay hashes must match. This is determinism of the plan,
    never reproducibility of a number.
    """
    hashes: list[str] = []
    keys: list[set[str]] = []
    for name in ("first.duckdb", "second.duckdb"):
        store = tmp_path / name
        assert comp(["run", "demo", "--store", str(store)]) == 0
        with RecordStore(StoreConfig(path=store, read_only=True)) as records:
            run = records.query_runs()[0]
            hashes.append(run.replay_hash or "")
            keys.append({r.measurement_key for r in records.query_records()})

    assert hashes[0] and hashes[0] == hashes[1]
    assert keys[0] == keys[1]
