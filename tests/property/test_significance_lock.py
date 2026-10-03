"""Lock: a claim's difference is tested, and the report names the test (E2).

TODO48b R5. A claim used to state a difference and stop there — ``n`` and
variance were mandatory (R64), but nothing asked whether the difference was
distinguishable from the spread. A run whose two arms differ by luck printed
the same two lines as a run whose arms differ by three sigma, and the reader
had no way to tell.

Three claims are locked here, and they are different in kind:

* a **real** difference prints its test, its p-value and its verdict
* a **flat** difference prints the honest null (p≈1, "not significant") rather
  than the same confident line
* a **thin** coverage prints "insufficient coverage" — a finding, not a
  failure, and not a p-value invented to fill the slot

No cell is trained. Every record is written through the mechanism tier's
``synthetic_record``, which is the point: a significance claim is about
*arithmetic over a store*, so the fixture is a store, and the assertions cost
milliseconds instead of a campaign run. Falsifiable by construction — deleting
the pairing key makes the arms unmatchable and every test here reads
"insufficient coverage"; pairing on the whole cell instead of the cell minus
one axis makes the fixture's pairs impossible to find.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

import pytest

from computronium.experiment.evidence.claims import (
    DEFAULT_MIN_SEEDS,
    CellMetrics,
    cell_metrics_by_axis_value,
    pairing_key,
)
from computronium.experiment.evidence.significance import (
    MIN_SHARED_CELLS,
    SIGNIFICANCE_TEST,
    Significance,
    paired_significance,
)
from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.coordinate import Coordinate, Provenance, Schedule
from computronium.experiment.schema.run_spec import MEASURED_PARAM_BUDGET, RunSpec
from computronium.experiment.surface.report import ReportGenerator, generate_run_report

from ._fake_backend import synthetic_record

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

    from computronium.experiment.schema.record import Record

_METRIC = "val_acc"
_ARMS = ("non_euclidean", "euclidean")
_PAIR_DELTA = 0.12


def _coordinate(update: str, pair: int) -> Coordinate:
    """One cell of one arm: the arm differs only in ``update``."""
    return Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="instantaneous",
        plasticity="fast_weights",
        credit="local_contrastive",
        update=update,
        params={"learning_rate": 0.01 * (pair + 1)},
    )


def _schedule(seed: int) -> Schedule:
    return Schedule(
        fidelity="L2",
        seed=seed,
        n_seeds=1,
        epochs=1,
        batch_limit=2,
        budget_id="significance",
        task_id="digits",
        param_budget=MEASURED_PARAM_BUDGET,
    )


def _spec() -> RunSpec:
    return RunSpec(
        task="digits",
        objectives=("validation_accuracy",),
        fidelity="L2",
        n_seeds=DEFAULT_MIN_SEEDS,
        epochs=1,
        batch_limit=2,
        param_budget=MEASURED_PARAM_BUDGET,
    )


def _arm_value(pair: int, *, delta: float) -> float:
    """The metric one arm's cell reports: a per-pair spread plus the delta."""
    return 0.40 + 0.02 * pair + (delta if delta > 0.0 else 0.0)


def _store_run(
    path: Path,
    *,
    pairs: int,
    delta: float,
) -> str:
    """A store holding ``pairs`` matched cells per arm, five seeds each.

    Args:
        path: Where the store is written.
        pairs: Matched cells per arm — the coverage the test has to work with.
        delta: The advantage ``euclidean`` holds over ``non_euclidean`` on
            every pair; ``0.0`` is a run where the axis does not matter.

    Returns:
        The run id.
    """
    with RecordStore(StoreConfig(path=path)) as store:
        run_id = store.create_run(spec=_spec())
        provenance = Provenance(
            env={},
            dataset="digits",
            dataset_version="1.0",
            code_sha="test",
            policy="test",
            links={"run_id": run_id},
        )
        for update in _ARMS:
            arm_delta = delta if update == _ARMS[1] else 0.0
            for pair in range(pairs):
                for seed in range(DEFAULT_MIN_SEEDS):
                    store.append(
                        synthetic_record(
                            _coordinate(update, pair),
                            _schedule(seed),
                            provenance,
                            metric=_arm_value(pair, delta=arm_delta),
                        )
                    )
    return run_id


def _fixture(path: Path, *, pairs: int, delta: float) -> tuple[str, Path]:
    return _store_run(path, pairs=pairs, delta=delta), path


@pytest.fixture(scope="module")
def winning_run(tmp_path_factory: pytest.TempPathFactory) -> tuple[str, Path]:
    """A store where one axis value beats the other on every matched cell."""
    path = tmp_path_factory.mktemp("significance") / "winning.duckdb"
    return _fixture(path, pairs=5, delta=_PAIR_DELTA)


@pytest.fixture(scope="module")
def flat_run(tmp_path_factory: pytest.TempPathFactory) -> tuple[str, Path]:
    """A store where both axis values report the same number."""
    path = tmp_path_factory.mktemp("significance") / "flat.duckdb"
    return _fixture(path, pairs=5, delta=0.0)


@pytest.fixture(scope="module")
def thin_run(tmp_path_factory: pytest.TempPathFactory) -> tuple[str, Path]:
    """A store with a real difference on a single matched cell."""
    path = tmp_path_factory.mktemp("significance") / "thin.duckdb"
    return _fixture(path, pairs=1, delta=_PAIR_DELTA)


def _significance_line(report: str) -> str:
    lines = [
        ln for ln in report.splitlines() if SIGNIFICANCE_TEST in ln or "coverage" in ln
    ]
    assert len(lines) == 1, f"expected one significance line, got {lines}"
    return lines[0]


class TestSignificanceIsTested:
    """A difference is printed with the test that judged it."""

    def test_a_real_difference_prints_its_test_p_value_and_verdict(
        self, winning_run: tuple[str, Path]
    ) -> None:
        run_id, path = winning_run
        with _report(path, run_id) as report:
            line = _significance_line(report)

        assert SIGNIFICANCE_TEST in line
        assert "shared_cells=5" in line
        assert line.rstrip().endswith("— significant"), line

        with RecordStore(StoreConfig(path=path)) as store:
            significance = ReportGenerator(store).significance(run_id)
        assert significance is not None
        assert significance.tested
        assert significance.p_value is not None
        assert significance.p_value < significance.alpha
        assert f"p={significance.p_value:.4f}" in line

    def test_the_p_value_follows_from_the_evidence_not_from_the_arm_names(
        self, winning_run: tuple[str, Path]
    ) -> None:
        """Relabelling the arms flips the sign of the difference, not the verdict."""
        run_id, path = winning_run
        with RecordStore(StoreConfig(path=path)) as store:
            records = store.query_records(run_id=run_id)
        by_value = cell_metrics_by_axis_value(
            records, axis=StructuralAxis.UPDATE, metric=_METRIC
        )
        flipped = paired_significance(
            by_value[_ARMS[0]],
            by_value[_ARMS[1]],
            axis="update",
            metric=_METRIC,
            best_value=_ARMS[0],
            worst_value=_ARMS[1],
        )
        assert flipped.p_value is not None
        assert flipped.p_value < flipped.alpha
        assert flipped.mean_diff < 0.0


class TestSignificanceIsHonest:
    """The null and the thin case are findings, not failures."""

    def test_a_flat_difference_is_reported_as_the_honest_null(
        self, flat_run: tuple[str, Path]
    ) -> None:
        run_id, path = flat_run
        with RecordStore(StoreConfig(path=path)) as store:
            significance = ReportGenerator(store).significance(run_id)
        assert significance is not None
        assert significance.tested
        assert significance.mean_diff == 0.0
        assert significance.p_value == pytest.approx(1.0)
        assert not significance.significant
        assert significance.render().endswith("— not significant")

    def test_one_shared_cell_is_insufficient_coverage(
        self, thin_run: tuple[str, Path]
    ) -> None:
        run_id, path = thin_run
        with _report(path, run_id) as report:
            line = _significance_line(report)
        assert "insufficient coverage (1 shared cell(s)" in line

        with RecordStore(StoreConfig(path=path)) as store:
            significance = ReportGenerator(store).significance(run_id)
        assert significance is not None
        assert not significance.tested
        assert significance.p_value is None
        assert not significance.significant

    def test_a_p_value_below_the_coverage_floor_is_refused(self) -> None:
        """The floor is enforced by the model, so no caller can skip it."""
        with pytest.raises(ValueError, match="shared"):
            Significance(
                axis="update",
                metric=_METRIC,
                best_value=_ARMS[1],
                worst_value=_ARMS[0],
                shared_cells=MIN_SHARED_CELLS - 1,
                mean_diff=0.1,
                ci_lower=0.0,
                ci_upper=0.2,
                cohens_dz=2.0,
                p_value=0.001,
            )


class TestPairing:
    """Only cells differing in the tested axis may be paired."""

    def _records(self) -> list[Record]:
        provenance = Provenance(
            env={},
            dataset="digits",
            dataset_version="1.0",
            code_sha="test",
            policy="test",
            links={"run_id": "pairing"},
        )
        return [
            synthetic_record(_coordinate(update, pair), _schedule(0), provenance)
            for update in _ARMS
            for pair in range(2)
        ]

    def test_a_pair_shares_everything_but_the_axis_under_test(self) -> None:
        keys = {
            (record.update, pairing_key(record, StructuralAxis.UPDATE))
            for record in self._records()
        }
        by_arm: dict[str, set[str]] = {}
        for update, key in keys:
            by_arm.setdefault(update, set()).add(key)
        assert by_arm[_ARMS[0]] == by_arm[_ARMS[1]], by_arm

    def test_cells_unshared_by_the_other_arm_do_not_move_the_difference(
        self, winning_run: tuple[str, Path]
    ) -> None:
        """An extra cell in one arm is evidence about that arm, not about the delta."""
        run_id, path = winning_run
        with RecordStore(StoreConfig(path=path)) as store:
            records = store.query_records(run_id=run_id)
        by_value = cell_metrics_by_axis_value(
            records, axis=StructuralAxis.UPDATE, metric=_METRIC
        )
        unpadded = paired_significance(
            by_value[_ARMS[1]],
            by_value[_ARMS[0]],
            axis="update",
            metric=_METRIC,
            best_value=_ARMS[1],
            worst_value=_ARMS[0],
        )
        unpadded = paired_significance(
            by_value[_ARMS[1]],
            by_value[_ARMS[0]],
            axis="update",
            metric=_METRIC,
            best_value=_ARMS[1],
            worst_value=_ARMS[0],
        )
        by_value[_ARMS[1]] |= {"cell the other arm never ran": _cell(0.99)}
        padded = paired_significance(
            by_value[_ARMS[1]],
            by_value[_ARMS[0]],
            axis="update",
            metric=_METRIC,
            best_value=_ARMS[1],
            worst_value=_ARMS[0],
        )
        assert padded.shared_cells == unpadded.shared_cells
        assert padded.mean_diff == pytest.approx(unpadded.mean_diff)


def _cell(mean: float) -> CellMetrics:
    return CellMetrics(mean=mean, variance=0.0, n=DEFAULT_MIN_SEEDS)


@contextmanager
def _report(path: Path, run_id: str) -> Generator[str]:
    """The rendered report, read from the store alone."""
    with RecordStore(StoreConfig(path=path, read_only=True)) as store:
        yield generate_run_report(store, run_id)
