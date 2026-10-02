"""Lock: the sampler learns, and only over measurements that exist.

TODO46 §3.4's gate. Two claims were false before:

* ``study.ask()`` was called with no distributions, ``study.tell()`` was called
  nowhere, and ``Policy.observe`` had no call site at all — so TPE and NSGA-II
  were constructed, asked, and never learned (§D3).
* ``OBJECTIVES`` advertised 36 objectives and the evaluator measured four of
  them. Nothing said so, so ``study.tell`` had no value to tell and the
  profiles' objectives were aspirational.

The learning test at the end uses a constructed landscape on purpose: it proves
the sampler responds to a value, and says nothing about the science. §D8 is the
reason that distinction is stated rather than assumed.
"""

from __future__ import annotations

import math
from typing import Any, cast

import pytest
from optuna.distributions import CategoricalDistribution, FloatDistribution

from computronium.experiment.execution.budget import Budget, SimpleCostModel
from computronium.experiment.execution.optuna_adapter import OptunaDistributionAdapter
from computronium.experiment.execution.policy import (
    ModelBasedPolicy,
    create_policy,
    policy_context,
    resolve_objectives,
)
from computronium.experiment.schema.coordinate import Coordinate, Provenance, Schedule
from computronium.experiment.schema.harvest import harvest_schema
from computronium.experiment.schema.metrics import (
    MEASURED_METRICS,
    MEASURED_OBJECTIVES,
    UnknownObjectiveError,
    UnmeasuredObjectiveError,
    objective_metric,
    objective_values,
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
from computronium.experiment.schema.registries import OBJECTIVES_REGISTRY

_TASK_ID = "digits"
_OPTIMAL_STEP_SIZE = 1e-2


def _coordinate(credit: str = "thermodynamic_contrast", **params: Any) -> Coordinate:
    return Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="energy_minimization",
        plasticity="fast_weights",
        credit=credit,
        update="euclidean",
        params=params,
    )


def _schedule(seed: int = 0) -> Schedule:
    return Schedule(
        fidelity="L0",
        seed=seed,
        n_seeds=1,
        epochs=1,
        batch_limit=2,
        budget_id="lock",
        task_id=_TASK_ID,
    )


def _record(
    coordinate: Coordinate,
    schedule: Schedule,
    payload: dict[str, Any],
    verdict: GateVerdict = GateVerdict.PASS_,
) -> Record:
    return Record.create(
        run_id="sampler",
        coordinate=coordinate,
        schedule=schedule,
        provenance=Provenance(
            env={},
            dataset=_TASK_ID,
            dataset_version="1.0",
            code_sha="test",
            policy="test",
            links={"run_id": "sampler"},
        ),
        status=Status(
            gate_verdict=verdict,
            defect="",
            cause=FailureCause.UNKNOWN,
            severity=Severity.LOW,
            quarantine=False,
            maturity=Maturity.L0,
            uncertainty={},
            reproducibility=ReproducibilityClass.REPLAYABLE,
            assessment_procedure_version="1.0",
            ceec_link=None,
        ),
        payload=dict(payload),
    )


def _budget() -> Budget:
    return Budget(started_at=0.0, target_cells=None, target_cost=None)


def _proposal_cell(
    policy: ModelBasedPolicy, **params: Any
) -> tuple[Coordinate, Schedule]:
    schedule = _schedule()
    proposed = policy.propose(
        [(_coordinate(**params), schedule)], [], _budget(), SimpleCostModel()
    )
    assert proposed, "a model-based policy must propose from an affordable candidate"
    return proposed[0]


class TestObjectivesAreMeasurements:
    def test_every_objective_is_measured_or_records_why(self) -> None:
        for name, spec in OBJECTIVES_REGISTRY.items():
            if spec.metric_key is None:
                assert spec.unavailable_reason, f"{name} is unmeasured and silent"
            else:
                assert spec.metric_key in MEASURED_METRICS, name

    def test_a_declared_objective_maps_onto_a_measured_key(self) -> None:
        assert objective_metric("validation_accuracy") == "val_acc"
        assert objective_metric("validation_loss") == "val_loss"
        assert objective_metric("walltime_total") == "walltime_s"
        assert objective_metric("param_count") == "param_count"

    def test_an_unregistered_objective_is_refused(self) -> None:
        with pytest.raises(UnknownObjectiveError, match="unknown objective"):
            objective_metric("accuracy")

    def test_a_registered_but_unmeasured_objective_is_refused(self) -> None:
        with pytest.raises(UnmeasuredObjectiveError, match="registered but unmeasured"):
            objective_metric("flops")

    def test_an_unmeasured_payload_yields_no_value(self) -> None:
        assert objective_values(("validation_accuracy",), {}) is None
        assert objective_values(("validation_accuracy",), {"val_acc": "n/a"}) is None
        assert objective_values(("validation_accuracy",), {"val_acc": 0.5}) == (0.5,)

    def test_resolve_is_fail_closed(self) -> None:
        assert resolve_objectives(("validation_accuracy", "walltime_total")) == (
            ("validation_accuracy", "walltime_total"),
            ("maximize", "minimize"),
        )
        with pytest.raises(UnmeasuredObjectiveError):
            resolve_objectives(("flops",))

    def test_the_evaluator_writes_every_measured_objective(self) -> None:
        """A measured objective must resolve against a real record payload."""
        from computronium.experiment.execution.evaluate import cell_record

        record = cell_record(
            _coordinate(),
            _schedule(),
            Provenance(
                env={},
                dataset=_TASK_ID,
                dataset_version="1.0",
                code_sha="test",
                policy="test",
                links={"run_id": "sampler"},
            ),
        )
        assert record.status.gate_verdict is GateVerdict.PASS_
        values = objective_values(tuple(MEASURED_OBJECTIVES), record.payload)
        assert values is not None and all(math.isfinite(v) for v in values), (
            f"declared measured but absent from the payload: "
            f"{sorted(MEASURED_OBJECTIVES)}"
        )

    def test_every_profile_searches_only_measured_objectives(self) -> None:
        from computronium.experiment.surface.cli import RUN_PROFILES

        for name, profile in RUN_PROFILES.items():
            objective_values(
                profile.objectives,
                {objective_metric(o): 0.0 for o in profile.objectives},
            )
            assert profile.policy in {"model_based", "evolution", "round_robin_grid"}, (
                name
            )


class TestDistributionsComeFromTheHarvest:
    def test_the_sampled_names_are_the_active_ones(self) -> None:
        coordinate = _coordinate()
        distributions = OptunaDistributionAdapter.distributions(coordinate)
        active = harvest_schema().active(coordinate)

        assert distributions, "a digits cell has continuous hyperparameters"
        assert set(distributions) <= {spec.name for spec in active.specs}
        for name, value in coordinate.params.items():
            if name in distributions:
                assert _within(distributions[name], value)

    def test_availability_decides_what_is_sampled(self) -> None:
        """A credit-gated knob is sampled only where its predicate holds.

        ``ema_beta`` is declared for one credit primitive and ``train_biases``
        for another, so swapping the credit axis changes the dimensions: that is
        availability doing the work, not a name comparison.
        """
        contrastive = OptunaDistributionAdapter.distributions(
            _coordinate("local_contrastive")
        )
        gradient = OptunaDistributionAdapter.distributions(_coordinate("gradient"))

        assert "ema_beta" in contrastive
        assert "train_biases" in gradient
        assert "ema_beta" not in gradient
        assert "train_biases" not in contrastive

    def test_a_spec_narrows_and_never_widens(self) -> None:
        from computronium.experiment.schema.axis import Domain, Scale
        from computronium.experiment.schema.run_spec import RunSpec

        spec = RunSpec(
            task=_TASK_ID,
            objectives=("validation_accuracy",),
            hyperparameters={
                "step_size": Domain(lo=1e-3, hi=1e-1, scale=Scale.LOG),
            },
        )
        narrow = OptunaDistributionAdapter.distributions(_coordinate(), spec=spec)

        assert set(narrow) == {"step_size"}
        bounds = cast("FloatDistribution", narrow["step_size"])
        assert bounds.low == pytest.approx(1e-3)
        assert bounds.high == pytest.approx(1e-1)

    def test_a_domain_outside_the_harvested_one_is_refused(self) -> None:
        from computronium.experiment.schema.axis import Domain
        from computronium.experiment.schema.run_spec import RunSpec

        spec = RunSpec(
            task=_TASK_ID,
            objectives=("validation_accuracy",),
            hyperparameters={"step_size": Domain(lo=10.0, hi=100.0)},
        )
        with pytest.raises(ValueError, match="outside the harvested"):
            OptunaDistributionAdapter.distributions(_coordinate(), spec=spec)


class TestStructuralKnobsAreNotDimensions:
    def test_the_tasks_own_shape_is_not_sampled(self) -> None:
        """Shape is derived from the task (TODO46 §3.0), never searched."""
        distributions = OptunaDistributionAdapter.distributions(_coordinate())

        assert "input_dim" not in distributions
        assert "output_dim" not in distributions
        assert "device" not in distributions

    def test_a_spec_may_not_sweep_a_structural_knob(self) -> None:
        from computronium.experiment.schema.axis import Domain
        from computronium.experiment.schema.run_spec import RunSpec

        with pytest.raises(ValueError, match="structural"):
            RunSpec(
                task=_TASK_ID,
                objectives=("validation_accuracy",),
                hyperparameters={"input_dim": Domain(lo=8, hi=64)},
            )


class TestTheStudyLearns:
    def test_the_study_is_asked_with_distributions(self) -> None:
        """`suggest_*` runs: the proposal carries a value the candidate lacked."""
        policy = ModelBasedPolicy(seed=0, objectives=("validation_accuracy",))
        coordinate, _ = _proposal_cell(policy)

        assert "step_size" in coordinate.params
        assert coordinate.params["step_size"] > 0.0

    def test_asked_values_stay_inside_the_declared_domains(self) -> None:
        policy = ModelBasedPolicy(seed=3, objectives=("validation_accuracy",))
        distributions = OptunaDistributionAdapter.distributions(_coordinate())

        for _ in range(5):
            coordinate, _ = _proposal_cell(policy)
            for name, value in coordinate.params.items():
                if name in distributions:
                    assert _within(distributions[name], value), (
                        f"{name}={value} is outside {distributions[name]}"
                    )

    def test_observed_records_are_told_to_the_study(self) -> None:
        policy = ModelBasedPolicy(seed=0, objectives=("validation_accuracy",))
        told: list[tuple[Coordinate, Schedule]] = []

        for index, accuracy in enumerate((0.10, 0.40, 0.25)):
            proposed = policy.propose(
                [(_coordinate(), _schedule(seed=index))],
                [],
                _budget(),
                SimpleCostModel(),
            )
            coordinate, schedule = proposed[0]
            told.append((coordinate, schedule))
            policy.observe(_record(coordinate, schedule, {"val_acc": accuracy}))

        assert policy.completed_trials() == len(told)
        assert policy._study is not None
        assert policy._study.best_value == pytest.approx(0.40)
        assert len(policy._study.best_trials) == 1

    def test_a_record_that_measured_nothing_is_not_told_a_value(self) -> None:
        policy = ModelBasedPolicy(seed=0, objectives=("validation_accuracy",))
        coordinate, schedule = _proposal_cell(policy)
        policy.observe(_record(coordinate, schedule, {"status": "failed"}))

        assert policy._study is not None
        assert policy._study.trials[0].state.name == "FAIL"

    def test_a_quarantined_record_does_not_steer_the_study(self) -> None:
        policy = ModelBasedPolicy(seed=0, objectives=("validation_accuracy",))
        coordinate, schedule = _proposal_cell(policy)
        policy.observe(
            _record(coordinate, schedule, {"val_acc": 0.99}, verdict=GateVerdict.FAIL)
        )

        assert policy._study is not None
        assert policy._study.trials[0].state.name == "FAIL"

    def test_a_record_the_policy_did_not_propose_is_ignored(self) -> None:
        """Only a measurement this policy asked for is told to the study."""
        policy = ModelBasedPolicy(seed=0, objectives=("validation_accuracy",))
        _proposal_cell(policy)
        policy.observe(_record(_coordinate(), _schedule(), {"val_acc": 0.9}))

        assert policy.completed_trials() == 0
        assert policy._study is not None
        assert policy._study.trials[0].state.name == "RUNNING"

    def test_the_sampler_moves_toward_the_optimum(self) -> None:
        """The machinery learns — on a constructed landscape, deliberately.

        ``step_size`` has a known optimum at 1e-2 and a log-parabolic score
        around it. This proves the sampler responds to the value it is told; it
        is not evidence about any cell (TODO46 §D8).
        """
        policy = ModelBasedPolicy(
            seed=0, objectives=("validation_accuracy",), n_startup_trials=4
        )
        values: list[float] = []
        for _ in range(24):
            coordinate, schedule = _proposal_cell(policy)
            score = _log_parabola(coordinate.params["step_size"])
            values.append(score)
            policy.observe(_record(coordinate, schedule, {"val_acc": score}))

        early = sum(values[:8]) / 8
        late = sum(values[-8:]) / 8
        assert late > early, f"sampler did not improve: early={early} late={late}"
        assert max(values) > 0.5

    def test_the_sampler_differs_from_uniform_for_the_same_seed(self) -> None:
        from computronium.experiment.execution.policy import UniformRandomPolicy

        model_based = ModelBasedPolicy(seed=7, objectives=("validation_accuracy",))
        uniform = UniformRandomPolicy(seed=7)
        candidates = [(_coordinate(), _schedule())]

        sampled = [_proposal_cell(model_based)[0].params.get("step_size")]
        random = [
            coord.params.get("step_size")
            for coord, _ in uniform.propose(
                candidates, [], _budget(), SimpleCostModel()
            )
        ]

        assert sampled != random

    def test_the_store_is_the_only_study_source(self) -> None:
        """A resumed run's history is its records (R71)."""
        policy = ModelBasedPolicy(seed=0, objectives=("validation_accuracy",))
        history = [
            _record(_coordinate(), _schedule(seed=seed), {"val_acc": accuracy})
            for seed, accuracy in enumerate((0.1, 0.2, 0.9))
        ]
        resumed = ModelBasedPolicy(seed=0, objectives=("validation_accuracy",))

        resumed.propose(
            [(_coordinate(), _schedule(seed=9))],
            history,
            _budget(),
            SimpleCostModel(),
        )

        assert resumed.completed_trials() == len(history)
        assert policy.completed_trials() == 0


class TestTheRunReachesThePolicy:
    def test_the_spec_reaches_a_learning_policy(self) -> None:
        from computronium.experiment.schema.run_spec import RunSpec

        spec = RunSpec(
            task=_TASK_ID,
            objectives=("validation_accuracy",),
            policy="model_based",
            seed=11,
        )
        context = policy_context(spec, "model_based")

        assert context["objectives"] == ("validation_accuracy",)
        assert context["seed"] == 11
        assert context["spec"] is spec
        assert create_policy("model_based", **context).get_name() == "model_based_tpe"

    def test_a_policy_that_declares_no_objectives_receives_none(self) -> None:
        from computronium.experiment.schema.run_spec import RunSpec

        spec = RunSpec(task=_TASK_ID, objectives=("validation_accuracy",))
        context = policy_context(spec, "round_robin_grid")

        assert "objectives" not in context
        assert "spec" not in context

    def test_an_unsupported_argument_is_refused_not_dropped(self) -> None:
        with pytest.raises(ValueError, match="does not accept"):
            create_policy("round_robin_grid", objectives=("validation_accuracy",))

    def test_the_pipeline_hands_a_stored_record_to_the_policy(self) -> None:
        import ast
        from pathlib import Path

        source = (
            Path(__file__).resolve().parents[2]
            / "computronium/experiment/execution/pipeline.py"
        )
        tree = ast.parse(source.read_text())
        observer = next(
            node
            for cls in tree.body
            if isinstance(cls, ast.ClassDef)
            for node in cls.body
            if isinstance(node, ast.FunctionDef) and node.name == "_observe"
        )
        assert any(
            isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "observe"
            for n in ast.walk(observer)
        ), "the policy is never told what was measured"

        executor = next(
            node
            for cls in tree.body
            if isinstance(cls, ast.ClassDef)
            for node in cls.body
            if isinstance(node, ast.AsyncFunctionDef)
            and node.name == "_execute_batch_with_isolation"
        )
        assert any(
            isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "_observe"
            for n in ast.walk(executor)
        ), "a stored record is never handed to the policy"


def _within(distribution: object, value: object) -> bool:
    """Whether a sampled value is legal for its distribution.

    Optuna's categorical ``_contains`` speaks its internal index
    representation, so a categorical is checked against its own choices.
    """
    if isinstance(distribution, CategoricalDistribution):
        return value in distribution.choices
    return bool(distribution._contains(value))  # type: ignore[attr-defined]


def _log_parabola(step_size: float) -> float:
    """A score with a known optimum at 1e-2, on the log axis."""
    offset = math.log10(step_size) - math.log10(_OPTIMAL_STEP_SIZE)
    return math.exp(-(offset**2))
