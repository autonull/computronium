"""TODO48 Q2 + E4 — promotion is a measurement, and L2 is earned by replay.

One tiny spec (one cell, L2, 5 seeds, 1 epoch) runs through the command
surface; the promotion stage that ``comp run`` now executes writes the
maturity the store earned:

- no record keeps the default maturity: L1 was earned per eligible cell,
  and at least one cell's replay survived, reaching ``maturity=L2`` *and*
  ``reproducibility=computationally_reproducible`` — the class the replay
  verdict measures — so ``promoted()`` and the report's ``Promoted:`` count
  become non-zero measurements;
- the report's promotion-history section lists the cell.

Falsifiable: removing the ``promote_run`` call from ``_cmd_run`` turns every
assertion red (records stay L0); removing the replay gate (E4) turns the
reproducibility assertions red. Cost discipline: one cell × 5 seeds at
1 epoch, measured ~0.5 s per record plus one replay measurement.
"""

from __future__ import annotations

import math
from pathlib import Path
from tempfile import mkdtemp

import pytest
import yaml

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.schema.record import (
    Maturity,
    ReproducibilityClass,
)
from computronium.experiment.surface import cli
from computronium.experiment.surface.report import ReportGenerator

pytestmark = pytest.mark.timeout(600)

_SPEC = {
    "version": 2,
    "profile": "campaign",
    "task": "digits",
    "fidelity": "L2",
    "n_seeds": 5,
    "epochs": 1,
    "batch_limit": 2,
    "seed": 0,
    "param_budget": 10000,
    "budget_seconds": 60,
    "policy": "round_robin_grid",
    "axes": [
        {"axis": "substrate", "primitives": ["digital"]},
        {"axis": "plasticity", "primitives": ["fast_weights"]},
        {"axis": "update", "primitives": ["euclidean"]},
        {"axis": "dynamics", "primitives": ["energy_minimization"]},
        {"axis": "credit", "primitives": ["gradient"]},
        {"axis": "geometry", "primitives": ["feedforward"]},
    ],
    "hyperparameters": {
        "hidden_dim": {"lo": 64, "hi": 64.9},
        "step_size": {"lo": 0.0316, "hi": 0.0317, "scale": "log"},
    },
}


@pytest.fixture(scope="module")
def run(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, str]:
    """One tiny measured run through the command surface, promotion included."""
    from computronium.experiment.schema.seed_registries import seed_all_registries

    seed_all_registries()
    store_path = tmp_path_factory.mktemp("promotion") / "promotion.duckdb"
    spec_path = Path(mkdtemp()) / "promotion.yaml"
    spec_path.write_text(yaml.dump(_SPEC), encoding="utf-8")
    assert cli.main(["run", "--spec", str(spec_path), "--store", str(store_path)]) == 0
    with RecordStore(StoreConfig(path=store_path, read_only=True)) as store:
        run_id = store.query_runs()[0].run_id
    return store_path, run_id


def test_a_promoted_cell_reaches_l2_by_replay(run: tuple[Path, str]) -> None:
    """L2 is written only where the replay gate passed — and it passed here."""
    store_path, run_id = run
    with RecordStore(StoreConfig(path=store_path, read_only=True)) as store:
        records = store.query_records(run_id=run_id)
        assert records, "the run measured nothing"
        earned = {r.status.maturity for r in records}
        assert Maturity.L0 not in earned, (
            "a record kept the default maturity: promotion never ran"
        )
        promoted_records = [r for r in records if r.status.maturity is Maturity.L2]
        assert promoted_records, (
            f"no cell's replay survived: {[r.status.maturity.value for r in records]}"
        )
        assert all(
            r.status.reproducibility
            is ReproducibilityClass.COMPUTATIONALLY_REPRODUCIBLE
            for r in promoted_records
        )
        history = ReportGenerator(store).promotion_history(run_id)
        assert history, "no promoted cell in the report's promotion history"
        assert all(entry["maturity"] == "l2" for entry in history)


def test_the_report_counts_the_promotion(run: tuple[Path, str]) -> None:
    """The report's ``Promoted:`` count and history are measurements now."""
    store_path, run_id = run
    output = Path(mkdtemp()) / "report.txt"
    assert (
        cli.main([
            "report",
            "--store",
            str(store_path),
            "--run-id",
            run_id,
            "--output",
            str(output),
        ])
        == 0
    )
    report = output.read_text(encoding="utf-8")
    promoted_line = next((ln for ln in report.splitlines() if "Promoted:" in ln), "")
    assert promoted_line, "the report printed no promotion summary"
    assert not promoted_line.rstrip().endswith("0"), (
        f"the promotion history is empty on a measured run: {promoted_line!r}"
    )
    with RecordStore(StoreConfig(path=store_path, read_only=True)) as store:
        claims = ReportGenerator(store).claims(run_id)
    assert all(math.isfinite(c.mean) for c in claims)
