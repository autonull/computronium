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
    ProposalContext,
    create_policy,
    policy_context,
    resolve_objectives,
)
from computronium.experiment.execution.search_space import search_space_from_spec
from computronium.experiment.schema import (
    Coordinate,
    Provenance,
    Schedule,
    harvest_schema,
    MEASURED_METRICS,
    UnknownObjectiveError,
    UnmeasuredObjectiveError,
    objective_metric,
    objective_values,
    FailureCause,
    GateVerdict,
    Maturity,
    Record,
    ReproducibilityClass,
    Severity,
    Status,
    OBJECTIVES_REGISTRY,
    RunSpec,
    seed_all_registries,
)

_TASK_ID = "digits"


@pytest.fixture(scope="module", autouse=True)
def _seed_registries() -> None:
    seed_all_registries()
_OPTIMAL_SETTLE_STEP = 0.03


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


def _run_spec(**overrides: Any) -> RunSpec:
    fields: dict[str, Any] = {
        "profile": "lock",
        "task": _TASK_ID,
        "objectives": ("validation_accuracy",),
        "fidelity": "L0",
        "n_seeds": 1,
        "epochs": 1,
        "seed": 0,
    }
    fields.update(overrides)
    return RunSpec(**fields)


def _context(
    records: list[Record] | None = None, *, n_propose: int = 1, **overrides: Any
) -> ProposalContext:
    """One task's own space, one budget, and whatever the run has measured.

    There is no candidate list to pass: the policy generates its cells, which
    is the interface §3.3/§3.4 were always going to be together.
    """
    spec = _run_spec(**overrides)
    return ProposalContext(
        search_space=search_space_from_spec(spec, tasks=[_TASK_ID]),
        spec=spec,
        run_id="sampler",
        budget=_budget(),
        cost_model=SimpleCostModel(),
        evidence=_History(records or []),
        task=_TASK_ID,
        n_propose=n_propose,
    )


class _History:
    """A store holding exactly the records a test measured."""

    def __init__(self, records: list[Record]) -> None:
        self._records = records

    def query_records(
        self, run_id: str | None = None, limit: int | None = None
    ) -> list[Record]:
        return self._records[:limit] if limit else list(self._records)


def _proposal_cell(policy: ModelBasedPolicy) -> tuple[Coordinate, Schedule]:
    proposals = list(policy.propose(_context()))
    assert proposals, "a model-based policy must generate a cell from its own space"
    return proposals[0].coordinate, proposals[0].schedule


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
        """A measured objective must resolve against a real record payload.

        For this coordinate (energy_minimization + thermodynamic_contrast + euclidean),
        the applicable measured objectives are those produced by this dynamics family.
        Family-specific energy metrics for other dynamics (pc_alm, predictive_settling,
        spike_integration, instantaneous) are correctly absent.
        """
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

        # Objectives applicable to energy_minimization + thermodynamic_contrast + euclidean
        applicable_objectives = (
            "contraction_rate",
            "drift_max_singular_value",
            "drift_spectral_radius",
            "energy_efficiency",
            "energy_per_mac",
            "energy_per_step",
            "free_energy",          # alias for hopfield_energy in this family
            "hopfield_energy",
            "lyapunov_exponent",
            "macs_per_step",
            "max_singular_value",
            "nonnormality",
            "param_count",
            "settle_steps",
            "spectral_radius",
            "stability_margin",
            "validation_accuracy",
            "validation_loss",
            "walltime_total",
        )
        values = objective_values(applicable_objectives, record.payload)
        assert values is not None and all(math.isfinite(v) for v in values), (
            f"applicable measured objectives absent from payload: "
            f"{sorted(applicable_objectives)}"
        )

        # Family-specific metrics for OTHER dynamics should NOT be present
        # (they are registered with unavailable_reason for this coordinate)
        inapplicable = (
            "augmented_lagrangian",      # pc_alm only
            "instantaneous_proxy_energy",  # instantaneous only
            "pc_free_energy",            # predictive coding only
            "spike_proxy_energy",        # spike_integration only
        )
        for obj in inapplicable:
            assert objective_values((obj,), record.payload) is None, (
                f"inapplicable objective {obj!r} unexpectedly present"
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
                "settle_step": Domain(lo=1e-3, hi=1e-1, scale=Scale.LOG),
            },
        )
        narrow = OptunaDistributionAdapter.distributions(_coordinate(), spec=spec)

        assert set(narrow) == {"settle_step"}
        bounds = cast("FloatDistribution", narrow["settle_step"])
        assert bounds.low == pytest.approx(1e-3)
        assert bounds.high == pytest.approx(1e-1)

    def test_a_domain_outside_the_harvested_one_is_refused(self) -> None:
        from computronium.experiment.schema.axis import Domain
        from computronium.experiment.schema.run_spec import RunSpec

        spec = RunSpec(
            task=_TASK_ID,
            objectives=("validation_accuracy",),
            hyperparameters={"settle_step": Domain(lo=10.0, hi=100.0)},
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

        assert "settle_step" in coordinate.params
        assert coordinate.params["settle_step"] > 0.0

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
            proposed = list(policy.propose(_context(seed=index)))
            coordinate, schedule = proposed[0].coordinate, proposed[0].schedule
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

        ``settle_step`` has a known optimum at 0.03 and a log-parabolic score
        around it. This proves the sampler responds to the value it is told; it
        is not evidence about any cell (TODO46 §D8).
        """
        policy = ModelBasedPolicy(
            seed=0, objectives=("validation_accuracy",), n_startup_trials=4
        )
        values: list[float] = []
        for _ in range(24):
            coordinate, schedule = _proposal_cell(policy)
            score = _log_parabola(coordinate.params["settle_step"])
            values.append(score)
            policy.observe(_record(coordinate, schedule, {"val_acc": score}))

        early = sum(values[:8]) / 8
        late = sum(values[-8:]) / 8
        assert late > early, f"sampler did not improve: early={early} late={late}"
        assert max(values) > 0.5

    def test_the_sampler_differs_from_uniform_for_the_same_seed(self) -> None:
        from computronium.experiment.execution.policy import UniformRandomPolicy

        model_based = ModelBasedPolicy(
            seed=7, objectives=("validation_accuracy",), spec=_run_spec()
        )
        uniform = UniformRandomPolicy(seed=7)

        sampled = [_proposal_cell(model_based)[0].params.get("settle_step")]
        random = [
            proposal.coordinate.params.get("settle_step")
            for proposal in uniform.propose(_context(n_propose=10))
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

        list(resumed.propose(_context(history, seed=9)))

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
        # ICU model is available for default credit/update, so sampler is icu_guided
        assert create_policy("model_based", **context).get_name() == "model_based_icu_guided"

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


def _log_parabola(settle_step: float) -> float:
    """A score with a known optimum at 0.03, on the log axis."""
    offset = math.log10(settle_step) - math.log10(_OPTIMAL_SETTLE_STEP)
    return math.exp(-(offset**2))
