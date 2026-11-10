"""Tests for task-aware objectives: validator uses per-task primary metric.

This test ensures the fix for the validator metric mismatch:
- Vision tasks (mnist, fashion_mnist, digits): primary metric = val_acc
- RL tasks (cartpole, pendulum, acrobot): primary metric = mean_reward
- Graph tasks (cora, citeseer, pubmed): primary metric = accuracy
"""

from computronium.experiment.kernel.evaluate import (
    _core_metric_keys,
    _primary_metric_key,
    _validate_metrics_finite,
)
from computronium.experiment.registry.task_registry import get_task_registry
from computronium.experiment.schema import Coordinate


class TestTaskAwareObjectives:
    """Test that each task domain uses its correct primary metric."""

    def test_vision_tasks_use_val_acc(self):
        """Vision tasks should use val_acc as primary metric."""
        for task_id in ("mnist", "fashion_mnist", "digits", "xor", "spiral"):
            key = _primary_metric_key(task_id)
            assert key == "val_acc", f"{task_id}: expected val_acc, got {key}"

    def test_rl_tasks_use_mean_reward(self):
        """RL tasks should use mean_reward as primary metric."""
        for task_id in ("cartpole", "pendulum", "acrobot"):
            key = _primary_metric_key(task_id)
            assert key == "mean_reward", f"{task_id}: expected mean_reward, got {key}"

    def test_graph_tasks_use_accuracy(self):
        """Graph node classification tasks should use accuracy as primary metric."""
        for task_id in ("cora", "citeseer", "pubmed", "graph_classification"):
            key = _primary_metric_key(task_id)
            assert key == "accuracy", f"{task_id}: expected accuracy, got {key}"

    def test_core_metric_keys_include_primary(self):
        """Core metrics for each task should include its primary metric key."""
        registry = get_task_registry()

        # Vision task
        vision_keys = _core_metric_keys("mnist")
        assert "val_acc" in vision_keys
        assert "loss" in vision_keys

        # RL task
        rl_keys = _core_metric_keys("cartpole")
        assert "mean_reward" in rl_keys
        assert "loss" in rl_keys

        # Graph task
        graph_keys = _core_metric_keys("cora")
        assert "accuracy" in graph_keys
        assert "loss" in graph_keys

    def test_validate_metrics_finite_uses_task_specific_core(self):
        """_validate_metrics_finite should only fail on task-specific core metrics."""
        from computronium.experiment.schema import Schedule

        # Create a dummy coordinate for each task
        vision_coord = Coordinate(
            substrate="digital",
            geometry="feedforward",
            dynamics="instantaneous",
            plasticity="null",
            credit="gradient",
            update="euclidean",
            params={},
        )
        vision_schedule = Schedule(
            fidelity="L0",
            seed=0,
            n_seeds=1,
            epochs=1,
            batch_limit=0,
            budget_id="test",
            task_id="mnist",
        )

        rl_coord = Coordinate(
            substrate="digital",
            geometry="feedforward",
            dynamics="instantaneous",
            plasticity="null",
            credit="gradient",
            update="euclidean",
            params={},
        )
        rl_schedule = Schedule(
            fidelity="L0",
            seed=0,
            n_seeds=1,
            epochs=1,
            batch_limit=0,
            budget_id="test",
            task_id="cartpole",
        )

        # NaN in vision primary metric should fail
        vision_metrics = {"val_acc": float("nan"), "loss": 0.5, "train_loss": 0.3}
        try:
            _validate_metrics_finite(
                vision_metrics, vision_coord, vision_schedule.task_id
            )
            assert False, "Should have raised EvaluationError for NaN val_acc"
        except Exception as e:
            assert "non-finite training metrics" in str(e)
            assert "val_acc" in str(e)

        # NaN in RL primary metric should fail
        rl_metrics = {"mean_reward": float("nan"), "loss": -10.0, "std_reward": 1.0}
        try:
            _validate_metrics_finite(rl_metrics, rl_coord, rl_schedule.task_id)
            assert False, "Should have raised EvaluationError for NaN mean_reward"
        except Exception as e:
            assert "non-finite training metrics" in str(e)
            assert "mean_reward" in str(e)

        # NaN in auxiliary metric should NOT fail (just warning)

        aux_metrics = {"val_acc": 0.95, "loss": 0.1, "free_energy": float("nan")}
        # This should not raise, just log warning
        _validate_metrics_finite(aux_metrics, vision_coord, vision_schedule.task_id)
        assert "free_energy" not in aux_metrics, "Auxiliary NaN should be dropped"

    def test_registry_payload_keys_match_task_implementation(self):
        """Verify registry payload keys match what task implementations return."""
        registry = get_task_registry()

        # Vision tasks return val_acc
        for task_id in ("mnist", "fashion_mnist", "digits"):
            spec = registry.get(task_id)
            primary_obj = next(
                o for o in spec.objectives if o.name == spec.primary_objective
            )
            assert primary_obj.payload_key == "val_acc"

        # RL tasks return mean_reward
        for task_id in ("cartpole", "pendulum", "acrobot"):
            spec = registry.get(task_id)
            primary_obj = next(
                o for o in spec.objectives if o.name == spec.primary_objective
            )
            assert primary_obj.payload_key == "mean_reward"

        # Graph tasks return accuracy
        for task_id in ("cora", "citeseer", "pubmed", "graph_classification"):
            spec = registry.get(task_id)
            primary_obj = next(
                o for o in spec.objectives if o.name == spec.primary_objective
            )
            assert primary_obj.payload_key == "accuracy"

    def test_unknown_task_fallbacks_to_val_acc(self):
        """Unknown task should fallback to val_acc for backward compatibility."""
        key = _primary_metric_key("nonexistent_task")
        assert key == "val_acc"

        keys = _core_metric_keys("nonexistent_task")
        assert "val_acc" in keys
        assert "loss" in keys
