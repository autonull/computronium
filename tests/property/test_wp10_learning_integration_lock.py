"""WP10 learning-integration locks: identity, achieved seeds, prior source.

L17 (cross-task identity): task_id joins the schedule struct, so the same
coordinate+seed on two tasks yields distinct measurement_keys and both
records persist (no false duplicate).
L20 (claim integrity): claim_eligible_by_achieved_seeds counts achieved
seeds per replication key; a run dying mid-replication is not eligible.
L11 (priors single-source): every ruler-LR task and every override in the
legacy tables resolves through the PRIORS registry via prior_value().
L7/L9 (surrogate wiring): training split excludes calibration/test; effect
size runs the closed-loop benchmark and returns a protocol result.
Harness: closed-loop mechanics, encoder locality, unit-cube task optima.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import numpy.typing as npt
import pytest

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

    from computronium.experiment.learning.surrogate import SurrogateTrainingData

from computronium.experiment.evidence.claims import claim_eligible_by_achieved_seeds
from computronium.experiment.evidence.protocol import CostBudget, EffectSizeResult
from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.learning.benchmark import (
    _coordinate_to_vector,
    _embedding_dims,
    create_synthetic_benchmark_tasks,
    run_acquisition_benchmark,
)
from computronium.experiment.learning.prior import (
    _DYNAMICS_STEP_SIZE_OVERRIDES_DATA,
    _RULER_LR_DATA,
    _STEP_SIZE_OVERRIDES_DATA,
    get_ruler_lr,
)
from computronium.experiment.schema.coordinate import (
    Coordinate,
    DataOrigin,
    Provenance,
    Schedule,
)
from computronium.experiment.schema.record import (
    FailureCause,
    GateVerdict,
    Maturity,
    Record,
    ReproducibilityClass,
    Severity,
    Status,
)
from computronium.experiment.schema.registries import prior_value
from computronium.experiment.schema.seed_registries import seed_all_registries


@pytest.fixture(autouse=True)
def _seed() -> None:
    seed_all_registries()


@pytest.fixture
def _store(tmp_path: Path) -> Iterator[RecordStore]:
    store = RecordStore(StoreConfig(path=tmp_path / "wp10.duckdb"))
    store.__enter__()
    try:
        yield store
    finally:
        store.__exit__(None, None, None)


def _coord() -> Coordinate:
    return Coordinate(
        substrate="Digital",
        geometry="Feedforward",
        dynamics="Instantaneous",
        plasticity="NullPlasticity",
        credit="Backprop",
        update="Euclidean",
        params={},
    )


def _sched(seed: int, task_id: str = "", n_seeds: int = 5) -> Schedule:
    return Schedule(
        fidelity="L2",
        seed=seed,
        n_seeds=n_seeds,
        epochs=10,
        batch_limit=100,
        budget_id="lock",
        task_id=task_id,
    )


def _status() -> Status:
    return Status(
        gate_verdict=GateVerdict.PASS_,
        defect="",
        cause=FailureCause.UNKNOWN,
        severity=Severity.LOW,
        quarantine=False,
        maturity=Maturity.L2,
        uncertainty={},
        reproducibility=ReproducibilityClass.COMPUTATIONALLY_REPRODUCIBLE,
        assessment_procedure_version="1.0",
        ceec_link=None,
    )


def _prov(origin: DataOrigin = DataOrigin.EXPLORATION) -> Provenance:
    return Provenance(
        env={},
        dataset="test",
        dataset_version="1.0",
        code_sha="sha",
        policy="policy",
        links={},
        data_origin=origin,
    )


def _record(
    run_id: str,
    seed: int,
    task_id: str = "",
    record_idx: int = 0,
    origin: DataOrigin = DataOrigin.EXPLORATION,
) -> Record:
    return Record.create(
        run_id=run_id,
        coordinate=_coord(),
        schedule=_sched(seed, task_id),
        provenance=_prov(origin),
        status=_status(),
        payload={"accuracy": 0.9, "lock_idx": record_idx},
    )


class TestCrossTaskIdentity:
    def test_same_coordinate_seed_distinct_keys_across_tasks(self) -> None:
        """L17: measurement_key spans task_id."""
        coord = _coord()
        first = coord.measurement_key(_sched(seed=7, task_id="task-a"))
        second = coord.measurement_key(_sched(seed=7, task_id="task-b"))
        assert first != second

    def test_same_task_same_seed_same_key(self) -> None:
        coord = _coord()
        assert coord.measurement_key(
            _sched(seed=7, task_id="task-a")
        ) == coord.measurement_key(_sched(seed=7, task_id="task-a"))

    def test_both_tasks_persist(self, _store: RecordStore) -> None:
        """L17: cross-task records coexist; no false duplicate rejection."""
        run_id = _store.create_run(spec={"kind": "lock"})
        _store.append(_record(run_id, seed=7, task_id="task-a", record_idx=0))
        _store.append(_record(run_id, seed=7, task_id="task-b", record_idx=1))
        assert len(_store.query_records(run_id=run_id)) == 2


class TestAchievedSeedClaims:
    def test_mid_replication_run_not_eligible(self, _store: RecordStore) -> None:
        """L20: 2 achieved seeds of planned 5 → not claim-eligible."""
        run_id = _store.create_run(spec={"kind": "lock"})
        first = _record(run_id, seed=1)
        _store.append(first)
        _store.append(_record(run_id, seed=2))
        assert not claim_eligible_by_achieved_seeds(first, _store, min_seeds=5)

    def test_full_replication_eligible(self, _store: RecordStore) -> None:
        """L20: 5 achieved seeds → eligible."""
        run_id = _store.create_run(spec={"kind": "lock"})
        first = _record(run_id, seed=1)
        _store.append(first)
        for seed in (2, 3, 4, 5):
            _store.append(_record(run_id, seed=seed))
        assert claim_eligible_by_achieved_seeds(first, _store, min_seeds=5)


class TestPriorSingleSource:
    def test_ruler_tasks_resolve_via_registry(self) -> None:
        """L11: every ruler-LR task resolves through prior_value()."""
        missing: list[str] = []
        for task in _RULER_LR_DATA:
            if task in {"*", "non_feedforward_default"}:
                continue
            if prior_value(f"ruler_lr_{task}") is None:
                missing.append(task)
        assert not missing, f"ruler tasks missing from PRIORS: {missing}"

    def test_ruler_accessors_match_registry(self) -> None:
        """L11: get_ruler_lr agrees with the registry center value."""
        center, _, _ = prior_value("ruler_lr_mnist") or (None, None, None)
        assert center is not None
        assert get_ruler_lr("mnist") == pytest.approx(center)

    def test_override_tables_resolve_via_registry(self) -> None:
        """L11: every step-size override resolves through prior_value()."""
        missing: list[str] = []
        for dynamics, credit in _STEP_SIZE_OVERRIDES_DATA:
            if prior_value(f"step_size_override_{dynamics}_{credit}") is None:
                missing.append(f"{dynamics}/{credit}")
        for dynamics in _DYNAMICS_STEP_SIZE_OVERRIDES_DATA:
            if prior_value(f"dynamics_step_size_{dynamics}") is None:
                missing.append(dynamics)
        assert not missing, f"overrides missing from PRIORS: {missing}"


class _StubModel:
    def fit(self, data: SurrogateTrainingData) -> None:
        pass

    def predict(
        self, coords: list[Coordinate]
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        n = len(coords)
        return np.zeros(n), np.ones(n)

    def predict_with_grad(
        self, coords: list[Coordinate]
    ) -> tuple[
        npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64]
    ]:
        n = len(coords)
        return np.zeros(n), np.ones(n), np.zeros(n)


class _StubPolicy:
    def propose(self, n: int, context: dict) -> list[Coordinate]:
        return [_coord() for _ in range(n)]

    def observe(self, record: Record) -> None:
        pass

    def get_name(self) -> str:
        return "stub"


def _surrogate(store: RecordStore | None = None):  # type: ignore[no-untyped-def]
    from computronium.experiment.learning.surrogate import (
        SurrogateConfig,
        SurrogatePolicy,
    )

    return SurrogatePolicy(_StubPolicy(), _StubModel(), SurrogateConfig(), store)


class TestSurrogateStoreWiring:
    def test_training_split_excludes_calibration_test(
        self, _store: RecordStore
    ) -> None:
        """L7: surrogate trains on exploration ∪ policy_selected only."""
        run_id = _store.create_run(spec={"kind": "lock"})
        _store.append(_record(run_id, 1, origin=DataOrigin.EXPLORATION))
        _store.append(_record(run_id, 2, origin=DataOrigin.POLICY_SELECTED))
        _store.append(_record(run_id, 3, origin=DataOrigin.CALIBRATION))
        _store.append(_record(run_id, 4, origin=DataOrigin.TEST))
        pol = _surrogate(_store)
        pol._load_training_data()
        assert pol._training_data is not None
        assert sorted(o.value for o in pol._training_data.data_origins) == [
            "exploration",
            "policy_selected",
        ]

    def test_effect_size_guards(self) -> None:
        """L9: protocol minimums enforced before any benchmark runs."""
        pol = _surrogate()
        with pytest.raises(ValueError, match="N_tasks >= 10"):
            pol.evaluate_effect_size(
                _StubPolicy(), CostBudget.eval_count(10), n_tasks=4
            )
        with pytest.raises(ValueError, match="N_seeds >= 5"):
            pol.evaluate_effect_size(
                _StubPolicy(), CostBudget.eval_count(10), n_seeds=2
            )

    def test_effect_size_returns_protocol_result(self) -> None:
        """L9: effect size runs on the synthetic task batch via the runner."""
        pol = _surrogate()
        result = pol.evaluate_effect_size(_StubPolicy(), CostBudget.eval_count(10))
        assert isinstance(result, EffectSizeResult)
        assert result.n_tasks >= 10
        assert result.n_seeds >= 5


class _RecordingPolicy:
    def __init__(self) -> None:
        self.batch_sizes: list[int] = []
        self.rounds: list[int] = []
        self.best_at_round_start: list[float] = []
        self.n_observed = 0

    def propose(self, n: int, context: dict) -> list[Coordinate]:
        self.batch_sizes.append(n)
        self.rounds.append(int(context["round"]))
        self.best_at_round_start.append(float(context["history_best"]))
        return [_coord() for _ in range(n)]

    def observe_score(self, coordinate: Coordinate, score: float) -> None:
        self.n_observed += 1

    def get_name(self) -> str:
        return "recording"


class TestBenchmarkHarness:
    def test_closed_loop_mechanics(self) -> None:
        """Harness drives propose→score→observe_score in budget-sized rounds."""
        treatment, control = _RecordingPolicy(), _RecordingPolicy()
        tasks = create_synthetic_benchmark_tasks(n_tasks=10)
        run_acquisition_benchmark(
            treatment,
            control,
            tasks,
            None,
        )
        for pol in (treatment, control):
            assert pol.n_observed == 10 * 5 * 100
            assert set(pol.rounds) == set(range(20))
            assert all(n == 5 for n in pol.batch_sizes)
            assert all(
                b == float("inf")
                for r, b in zip(pol.rounds, pol.best_at_round_start, strict=True)
                if r == 0
            )

    def test_encoder_deterministic_and_local(self) -> None:
        """Encoder is deterministic; a 1%-range nudge moves one dim slightly."""
        dims = _embedding_dims(6)
        assert dims
        base = _coordinate_to_vector(_coord(), 6, dims)
        assert base == _coordinate_to_vector(_coord(), 6, dims)
        spec = dims[0]
        lo = spec.domain.lo or 0.0
        hi = spec.domain.hi or 1.0
        nudged = Coordinate(
            substrate="Digital",
            geometry="Feedforward",
            dynamics="Instantaneous",
            plasticity="NullPlasticity",
            credit="Backprop",
            update="Euclidean",
            params={spec.name: (lo + hi) / 2 + 0.01 * (hi - lo)},
        )
        vec = _coordinate_to_vector(nudged, 6, dims)
        dist = float(np.linalg.norm(np.subtract(vec, base)))
        assert 0.0 < dist < 0.05

    def test_task_optima_in_unit_cube(self) -> None:
        """Benchmark optima match the encoder output range [0,1)^6."""
        for task in create_synthetic_benchmark_tasks(n_tasks=10):
            assert task.synthetic_fixture is not None
            assert len(task.synthetic_fixture.optimum) == 6
            assert all(0.0 <= v < 1.0 for v in task.synthetic_fixture.optimum)
