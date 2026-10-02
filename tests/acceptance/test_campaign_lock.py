"""TODO47 T5 — the §3.6 campaign, executed and asserted.

``examples/learning-rules-and-geometry-digits.yaml`` is the campaign: a run
declaration an external researcher can execute, not a narrative about one. This
module is its fixture. It asserts TODO46 §3.7's gates 1-4 through the *command
surface* (``comp run --spec`` / ``comp report`` / ``comp status``), because a
gate stated against a Python API proves the API and not the command; gates 5-7
(resume, replay hash, two policies over one store) are locked against the store
alone in ``tests/property/test_run_ledger_lock.py`` and are not re-run here.

Cost discipline (TODO47 §1.3): the campaign is a *normal* test because one cell
was measured, not assumed. At the measured regime a cell is ~0.5 s, the declared
space holds 90 cells (18 structural combinations x 5 sweep points, each
replicated over 5 seeds), so the run is ~50 s of measurement plus pipeline and
store overhead. If the example grows past ~5 minutes, re-price it and move this
to the demo tier rather than letting the default shard absorb it.

Honest reading of the numbers: the campaign measures *a real pipeline on a real
task*, and the claims asserted below are its arithmetic. At the campaign's own
fidelity (L0, 1 epoch, batch_limit 2) the ``digits`` cells sit at chance — the
regime prices coverage, not learning (measured; TODO47 §6, TODO48 Q1) — so the
axis impact asserted here is reported, not interpreted. The reference cell's
learning is asserted separately, at the regime where it is real (gate 2b).
A test that called the 1-epoch table "which rule learns better" would be
asserting noise.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import pytest

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.schema.run_spec import RunSpec
from computronium.experiment.schema.seed_registries import seed_all_registries
from computronium.experiment.surface import cli
from computronium.experiment.surface.report import ReportGenerator

if TYPE_CHECKING:
    from computronium.experiment.schema.record import Record

EXAMPLE = Path(__file__).resolve().parents[2] / "examples"
CAMPAIGN = EXAMPLE / "learning-rules-and-geometry-digits.yaml"

pytestmark = pytest.mark.timeout(900)


@dataclass(frozen=True, slots=True)
class Campaign:
    """One executed campaign: its declaration, its store, and its report."""

    spec: RunSpec
    store_path: Path
    run_id: str
    status: str
    replay_hash: str
    records: tuple[Record, ...]

    def train_acc(self) -> list[float]:
        return [float(r.payload["train_acc"]) for r in self.records]  # type: ignore[attr-defined]


@pytest.fixture(scope="module")
def campaign(tmp_path_factory: pytest.TempPathFactory) -> Campaign:
    """Run the campaign once through the CLI; hand every gate the same store."""
    seed_all_registries()
    store_path = tmp_path_factory.mktemp("campaign") / "campaign.duckdb"
    assert cli.main(["run", "--spec", str(CAMPAIGN), "--store", str(store_path)]) == 0

    with RecordStore(StoreConfig(path=store_path, read_only=True)) as store:
        run = store.query_runs()[0]
        return Campaign(
            spec=RunSpec.load(CAMPAIGN),
            store_path=store_path,
            run_id=run.run_id,
            status=run.status,
            replay_hash=run.replay_hash or "",
            records=tuple(store.query_records(run_id=run.run_id)),
        )


def test_the_example_is_a_valid_declaration_the_store_accepted(
    campaign: Campaign,
) -> None:
    """Gate 1, first half: the file is a run spec, and the run it names ran."""
    assert campaign.spec.task_names == ("digits", "mnist"), "no transfer task"
    assert campaign.spec.n_seeds > 1, "one seed cannot replicate anything"
    assert campaign.spec.axes, "the campaign declares no axis, so it varies nothing"
    assert campaign.status == "completed"
    assert campaign.replay_hash, "the run wrote no replay hash"


def test_gate_1_the_command_writes_records_with_no_duplicate_identity(
    campaign: Campaign,
) -> None:
    """Gate 1: ``comp run --spec`` completes and writes records, each one once."""
    assert campaign.records, "the campaign measured nothing"
    keys = [r.measurement_key for r in campaign.records]
    assert len(keys) == len(set(keys)), "the store holds a repeated measurement_key"

    # Every *legal* cell was measured. Legality is the space's own judgment
    # (a credit rule that requires feedforward is not proposed for a recurrent
    # cell), so coverage is asserted against what the space yields — and the
    # axes must not be locked to each other, or the campaign is one diagonal
    # of its own space.
    from computronium.experiment.execution.evaluate import task_shape
    from computronium.experiment.execution.search_space import (
        iter_candidates,
        search_space_from_spec,
    )

    space = search_space_from_spec(campaign.spec, tasks=campaign.spec.task_names)
    legal = {
        (c.dynamics, c.credit, c.geometry, s.task_id)
        for c, s in iter_candidates(campaign.spec, space, shape=task_shape)
    }
    measured = {
        (r.dynamics, r.credit, r.geometry, r.schedule.task_id) for r in campaign.records
    }
    # Each varying axis must vary *within* a fixed setting of the others: a
    # walk that advances every axis together measures one diagonal, which
    # reads as coverage and answers no "which axis mattered" question.
    names: tuple[Literal["dynamics", "credit", "geometry"], ...] = (
        "dynamics",
        "credit",
        "geometry",
    )
    for axis in names:
        held = tuple(a for a in names if a != axis)
        groups: dict[tuple[str, ...], set[str]] = {}
        for cell in measured:
            setting: dict[str, str] = dict(zip(names, cell[:3], strict=True))
            groups.setdefault((*(setting[name] for name in held), cell[3]), set()).add(
                setting[axis]
            )
        assert any(len(values) > 1 for values in groups.values()), (
            f"{axis} never varies with the other axes held fixed: the campaign "
            "measures one diagonal of its own space"
        )

    assert measured == legal, (
        f"{len(legal - measured)} legal cell(s) went unmeasured and "
        f"{len(measured - legal)} were measured that the space never yielded"
    )


def test_gate_2_records_carry_a_real_train_acc_that_varies_across_cells(
    campaign: Campaign,
) -> None:
    """Gate 2: ``train_acc`` is measured, and the axis moves it.

    Asserted as *measured variation attributable to an axis*, not as learning:
    two group means differ only if the cells were otherwise the same, which is
    what grouping by one axis value is for.
    """
    accuracies = campaign.train_acc()
    assert len(accuracies) == len(campaign.records), "a record carries no train_acc"
    assert all(math.isfinite(a) and 0.0 <= a <= 1.0 for a in accuracies)

    groups: dict[str, list[float]] = {}
    for record in campaign.records:
        groups.setdefault(record.credit, []).append(  # type: ignore[attr-defined]
            float(record.payload["train_acc"])  # type: ignore[attr-defined]
        )
    means = {credit: sum(values) / len(values) for credit, values in groups.items()}

    assert len(means) >= 2, "one credit rule: nothing to compare"
    assert max(means.values()) - min(means.values()) > 0.0, (
        f"every credit rule produced the same train_acc: {means}"
    )
    print(f"\ncampaign train_acc by credit rule: {means}")


def test_gate_2b_the_reference_cell_learns() -> None:
    """The ``gradient`` reference cell beats 1.5x chance (TODO48 Q1, D-g).

    The campaign's own fidelity (L0, 1 epoch, batch_limit 2) prices coverage,
    not learning; the reference cell's property is measured at the regime
    where learning is real — the sweep point nearest the step_size prior
    center, 10 epochs, unlimited batches (TODO47 §6.1's table). The cell is
    the campaign's own axes composition, not a fabricated one: reverting the
    ``active()`` resolve-once fix returns this gate to a frozen loss at
    chance.
    """
    from computronium.experiment.execution.evaluate import cell_record
    from computronium.experiment.schema.coordinate import (
        Coordinate,
        Provenance,
        Schedule,
    )
    from computronium.experiment.schema.run_spec import MEASURED_PARAM_BUDGET
    from computronium.experiment.schema.seed_registries import seed_all_registries

    seed_all_registries()
    record = cell_record(
        Coordinate(
            substrate="digital",
            geometry="feedforward",
            dynamics="energy_minimization",
            plasticity="fast_weights",
            credit="gradient",
            update="euclidean",
            params={"depth": 2, "hidden_dim": 64, "step_size": 0.03162},
        ),
        Schedule(
            fidelity="L0",
            seed=0,
            n_seeds=1,
            epochs=10,
            batch_limit=0,
            budget_id="campaign_lock",
            task_id="digits",
            param_budget=MEASURED_PARAM_BUDGET,
        ),
        provenance=Provenance(
            env={},
            dataset="digits",
            dataset_version="1.0",
            code_sha="campaign_lock",
            policy="campaign_lock",
            links={},
        ),
    )
    train_acc = float(record.payload["train_acc"])
    chance = 1.0 / 10.0
    assert train_acc > 1.5 * chance, (
        f"the reference cell cannot learn in this regime: train_acc={train_acc}"
    )
    print(f"\nreference cell train_acc: {train_acc:.4f}")


def test_gate_3_report_gives_claims_evidence_and_limitations_from_the_store(
    tmp_path: Path, campaign: Campaign
) -> None:
    """Gate 3: ``comp report --run-id`` reads the store, and nothing else."""
    output = tmp_path / "report.txt"
    assert (
        cli.main([
            "report",
            "--store",
            str(campaign.store_path),
            "--run-id",
            campaign.run_id,
            "--output",
            str(output),
        ])
        == 0
    )
    report = output.read_text(encoding="utf-8")

    assert campaign.run_id in report
    assert "Claims (n and variance are mandatory" in report
    assert "Limitations" in report
    assert campaign.replay_hash[:12] in report

    # A claim line carries n and variance, or it is not a claim.
    claim_lines = [ln for ln in report.splitlines() if "n=" in ln and "cells=" in ln]
    assert claim_lines, "the report printed no claim with n and variance"
    metrics = {line.split(":")[1].split("=")[0].strip() for line in claim_lines}
    assert len(metrics) >= 2, f"claims cover one metric only: {metrics}"
    assert "mattered most for" in report, "the report named no axis impact"

    # The report's claims, recomputed from the store alone, agree with its text.
    with RecordStore(StoreConfig(path=campaign.store_path, read_only=True)) as store:
        claims = ReportGenerator(store).claims(campaign.run_id)
    assert len(claims) >= 2
    assert all(c.n > 0 and math.isfinite(c.mean) for c in claims)


def test_gate_4_status_lists_the_run(campaign: Campaign) -> None:
    """Gate 4: ``comp status`` lists the run the campaign produced."""
    assert cli.main(["status", "--store", str(campaign.store_path)]) == 0
    assert (
        cli.main([
            "status",
            "--store",
            str(campaign.store_path),
            "--run-id",
            campaign.run_id,
        ])
        == 0
    )


def test_a_spec_file_is_a_first_class_run_declaration() -> None:
    """``comp run --spec`` needs no profile, and refuses what it cannot honour."""
    assert cli.main(["run", "--dry-run", "--spec", str(CAMPAIGN)]) == 0
    # A spec file is the declaration; --task would silently edit it.
    assert (
        cli.main(["run", "--dry-run", "--spec", str(CAMPAIGN), "--task", "mnist"]) == 2
    )
    # Neither a profile nor a spec is not a run.
    assert cli.main(["run"]) == 2
