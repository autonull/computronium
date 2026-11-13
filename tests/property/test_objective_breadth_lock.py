"""Lock: objective breadth is a measurement or a named reason (TODO90 B8).

Two surfaces used to name different sets. ``MEASURED_OBJECTIVES`` mapped 51
objective names; ``OBJECTIVES_REGISTRY`` registered 48 rows, 15 of which no
mapping entry backed, so ``objective_metric`` raised for names the mapping
claimed. Tasks also declared ``f1_score`` and ``bleu_score`` that no evaluator
path emitted.

The rule now: every measured name has a registry row with the same payload
key, every payload key is a declared metric, and every retired row says what
would have to exist. Four measurements are derived from numbers the cell
already measured (``convergence_steps``, ``generalization_gap``,
``training_time``, ``stability_plasticity_ratio``).

Each test fails if its mechanism is removed: delete a row, drop a derived
metric, or let a task declare an unmeasured payload key.
"""

from __future__ import annotations

from computronium.experiment.kernel._metrics import derived_metrics
from computronium.experiment.registry.task_registry import get_task_registry
from computronium.experiment.schema.metrics import (
    MEASURED_METRICS,
    MEASURED_OBJECTIVES,
    objective_metric,
)
from computronium.experiment.schema.registries import OBJECTIVES_REGISTRY
from computronium.experiment.schema.seed_registries import seed_all_registries

_RETIRED = {
    "test_accuracy",
    "test_loss",
    "f1_score",
    "bleu_score",
    "bp_deficit",
    "ruler_walltime_ratio",
    "ruler_energy_ratio",
    "ruler_param_ratio",
    "credit_efficiency",
}


def _rows() -> dict:
    seed_all_registries()
    return {spec.name: spec for spec in OBJECTIVES_REGISTRY}


def test_the_mapping_and_the_registry_name_the_same_measured_set() -> None:
    rows = _rows()
    measured = {name for name, spec in rows.items() if spec.metric_key}
    assert set(MEASURED_OBJECTIVES) == measured
    for name, spec in rows.items():
        if spec.metric_key is None:
            assert spec.unavailable_reason
            continue
        assert spec.metric_key == MEASURED_OBJECTIVES[name]
        assert spec.metric_key in MEASURED_METRICS
        assert objective_metric(name) == spec.metric_key


def test_every_retired_objective_names_its_missing_measurement() -> None:
    rows = _rows()
    retired = {name for name, spec in rows.items() if spec.metric_key is None}
    assert retired == _RETIRED
    for name in retired:
        reason = rows[name].unavailable_reason or ""
        assert len(reason) > 40, name
        assert reason.lower().startswith(("needs", "no ", "every ")), (name, reason)


def test_no_task_declares_a_payload_key_that_is_not_measured() -> None:
    _rows()
    for task in get_task_registry():
        for objective in task.objectives:
            if objective.is_measured:
                assert objective.payload_key in MEASURED_METRICS, (
                    task.name,
                    objective.name,
                )
        unmeasured = {o.name for o in task.unmeasured_objectives()}
        assert unmeasured <= _RETIRED | {"forgetting", "backward_transfer"}, task.name


def test_derived_metrics_are_derivations() -> None:
    history = [
        {"train_loss": 1.0, "val_loss": 1.2, "global_step": 10},
        {"train_loss": 0.5, "val_loss": 0.9, "global_step": 20},
        {"train_loss": 0.4, "val_loss": 0.8, "global_step": 30},
    ]
    derived = derived_metrics(history, walltime_s=6.0, metrics={})
    assert derived["training_time"] == 2.0
    assert derived["convergence_steps"] == 30.0
    assert derived["generalization_gap"] == 0.4
    assert "stability_plasticity_ratio" not in derived

    with_probes = derived_metrics(
        history,
        walltime_s=6.0,
        metrics={"spectral_radius": 0.9, "psi_capacity": 3.0},
    )
    assert with_probes["stability_plasticity_ratio"] == 0.3

    without_capacity = derived_metrics(
        history, walltime_s=6.0, metrics={"spectral_radius": 0.9, "psi_capacity": 0.0}
    )
    assert "stability_plasticity_ratio" not in without_capacity


def test_a_real_cell_payload_carries_the_derived_measurements() -> None:
    from computronium.experiment.kernel import evaluate_cell
    from computronium.experiment.schema import Coordinate, Schedule

    _rows()
    metrics = evaluate_cell(
        Coordinate(
            substrate="digital",
            geometry="feedforward",
            dynamics="instantaneous",
            plasticity="null",
            credit="gradient",
            update="euclidean",
            params={},
        ),
        Schedule(
            fidelity="L0",
            seed=0,
            n_seeds=1,
            epochs=2,
            batch_limit=4,
            budget_id="b8",
            task_id="digits",
            device="cpu",
        ),
    ).metrics
    assert metrics["training_time"] > 0.0
    assert metrics["convergence_steps"] > 0.0
    assert "generalization_gap" in metrics
