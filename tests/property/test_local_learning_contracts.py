"""W64: the local-learning rules, locked on what each one decides.

``core/local_learning`` was 45.1% covered, and the uncovered part is the
credit rules themselves: a Hebbian update that ignores ``learning_rate``, a
contrastive rule that forgets ``importance``, an activity rule that settles
from a missing state, or a task handler whose gradient disagrees with its own
loss. Each is a decision, so each is asserted directly (D6):

* **The two credit rules differ in sign and scale.** The builder applies
  ``w -= w_up``, so a pure Hebbian rule returns a *negated* correlation that
  potentiates (the legacy ``addmm_`` convention), and the learning rate must
  scale it — omitting the factor made ``learning_rate`` a no-op at depth.
* **A missing phase statistic is a zero update, not a crash.**
* **A tile without settled state is refused by name.**
* **The task handler's gradient is its loss's gradient**: softmax minus the
  one-hot target for CE, the residual for MSE.
* **A local rule writes a parameter delta; an autograd rule writes ``.grad``.**
  The two paths share parameters and must not be confused (W53b).
"""

from __future__ import annotations

import pytest
import torch
import torch.nn.functional as F  # ruff: ignore[lowercase-imported-as-non-lowercase]

from computronium.core.local_learning.activity import (
    ep_activity_update,
    hebbian_activity_update,
    spiking_activity_update,
)
from computronium.core.local_learning.builder import TileAlgorithm, TileAlgorithmConfig
from computronium.core.local_learning.registry import (
    _TILE_ALGORITHM_FACTORIES,
    _TILE_ALGORITHM_REGISTRY,
    get_tile_algorithm_factory,
    get_tile_algorithm_metadata,
    list_tile_algorithms,
    list_tile_algorithms_with_metadata,
    tile_algorithm,
)
from computronium.core.local_learning.task import TaskHandler
from computronium.core.local_learning.weight_update import (
    contrastive_weight_update,
    hebbian_weight_update,
)
from computronium.core.tile.topology import TileState

_STATS = {"src_neurons": 3, "dst_neurons": 2, "batch_size": 4}


def _tile(
    *,
    activity: torch.Tensor | None = None,
    prediction: torch.Tensor | None = None,
    error: torch.Tensor | None = None,
) -> TileState:
    return TileState(
        id=0,
        neurons=3,
        layer_id=0,
        activity=activity,
        prediction=prediction,
        error=error,
    )


def _model() -> TileAlgorithm:
    return TileAlgorithm(
        TileAlgorithmConfig(
            input_dim=8,
            output_dim=4,
            neurons_per_tile=8,
            tiles_per_layer=2,
            num_hidden_layers=2,
            algorithm="ep",
            mode="ep",
            free_steps=5,
            nudged_steps=5,
            learning_rate=0.01,
            beta=0.5,
        )
    )


def test_a_hebbian_update_is_scaled_by_the_learning_rate() -> None:
    """Doubling ``learning_rate`` doubles the update: the factor is not a no-op."""
    slow, _ = hebbian_weight_update(
        **_STATS,
        src_free=torch.ones(4, 3),
        dst_free=torch.ones(4, 2),
        src_nudged=None,
        dst_nudged=None,
        learning_rate=0.1,
        beta=0.5,
        importance=1.0,
    )
    fast, _ = hebbian_weight_update(
        **_STATS,
        src_free=torch.ones(4, 3),
        dst_free=torch.ones(4, 2),
        src_nudged=None,
        dst_nudged=None,
        learning_rate=0.2,
        beta=0.5,
        importance=1.0,
    )

    torch.testing.assert_close(fast, 2 * slow)


def test_a_hebbian_update_is_negated_for_the_builders_descent() -> None:
    """The builder applies ``w -= w_up``, so a positive correlation raises w."""
    weights, _ = hebbian_weight_update(
        **_STATS,
        src_free=torch.ones(4, 3),
        dst_free=torch.ones(4, 2),
        src_nudged=None,
        dst_nudged=None,
        learning_rate=0.1,
        beta=0.5,
        importance=1.0,
    )

    assert weights.shape == (2, 3)
    assert (weights < 0).all()


def test_a_hebbian_update_without_both_free_states_is_zero() -> None:
    weights, biases = hebbian_weight_update(
        **_STATS,
        src_free=torch.ones(4, 3),
        dst_free=None,
        src_nudged=None,
        dst_nudged=None,
        learning_rate=0.1,
        beta=0.5,
        importance=1.0,
    )

    assert torch.count_nonzero(weights) == 0
    assert torch.count_nonzero(biases) == 0


def test_a_contrastive_update_is_scaled_by_importance() -> None:
    stats = {
        **_STATS,
        "src_free": torch.ones(4, 3),
        "dst_free": torch.ones(4, 2) * 2.0,
        "src_nudged": torch.ones(4, 3) * 0.5,
        "dst_nudged": torch.ones(4, 2) * 2.0,
    }

    plain, _ = contrastive_weight_update(
        **stats, learning_rate=0.1, beta=0.5, importance=1.0
    )
    halved, _ = contrastive_weight_update(
        **stats, learning_rate=0.1, beta=0.5, importance=0.5
    )

    assert plain.shape == (2, 3)
    torch.testing.assert_close(halved, plain / 2)


def test_a_contrastive_update_without_a_nudged_phase_is_zero() -> None:
    weights, biases = contrastive_weight_update(
        **_STATS,
        src_free=torch.ones(4, 3),
        dst_free=torch.ones(4, 2),
        src_nudged=None,
        dst_nudged=torch.ones(4, 2),
        learning_rate=0.1,
        beta=0.5,
        importance=1.0,
    )

    assert torch.count_nonzero(weights) == 0
    assert torch.count_nonzero(biases) == 0


def test_an_ep_activity_update_needs_settled_activity() -> None:
    with pytest.raises(ValueError, match="_ep_activity_update"):
        ep_activity_update(
            _tile(error=torch.zeros(3)),
            feedback=[],
            importance=1.0,
            step_size=0.1,
            lambda_error=0.0,
            clamp_min=-1.0,
            clamp_max=1.0,
            clamp=False,
        )


def test_an_ep_activity_update_moves_against_the_error() -> None:
    relaxed = ep_activity_update(
        _tile(activity=torch.zeros(3), error=torch.ones(3)),
        feedback=[],
        importance=1.0,
        step_size=0.5,
        lambda_error=0.0,
        clamp_min=-1.0,
        clamp_max=1.0,
        clamp=False,
    )

    torch.testing.assert_close(relaxed, torch.full((3,), -0.5))


def test_a_hebbian_activity_update_is_the_computed_prediction() -> None:
    prediction = torch.tensor([0.25, 0.5, 0.75])
    settled = hebbian_activity_update(
        _tile(prediction=prediction),
        feedback=[],
        importance=1.0,
        step_size=0.1,
        lambda_error=0.0,
        clamp_min=-1.0,
        clamp_max=1.0,
        clamp=False,
    )

    torch.testing.assert_close(settled, prediction)


def test_a_hebbian_activity_update_needs_a_prediction() -> None:
    with pytest.raises(ValueError, match="_hebbian_activity_update"):
        hebbian_activity_update(
            _tile(activity=torch.zeros(3)),
            feedback=[],
            importance=1.0,
            step_size=0.1,
            lambda_error=0.0,
            clamp_min=-1.0,
            clamp_max=1.0,
            clamp=False,
        )


def test_a_spiking_activity_update_zeroes_a_fired_neuron() -> None:
    """A neuron above the spike threshold resets to zero; the rest keeps its value."""
    # Unclamped relaxation: activity - step·(error + λ·activity) = 5 - (−10) = 15.
    spiking = spiking_activity_update(
        _tile(activity=torch.tensor([5.0, -5.0]), error=torch.tensor([-10.0, 0.0])),
        feedback=[],
        importance=1.0,
        step_size=1.0,
        lambda_error=0.0,
        clamp_min=-100.0,
        clamp_max=100.0,
        clamp=False,
    )

    torch.testing.assert_close(spiking, torch.tensor([0.0, -5.0]))


def test_a_classification_gradient_is_the_softmax_residual() -> None:
    """The gradient is the per-sample residual, against a batch-mean loss.

    The convention is a sum of per-sample residuals (the EP output error),
    so the batch size is the factor between it and the mean loss's gradient.
    """
    handler = TaskHandler("classification", output_dim=3)
    logits = torch.tensor([[0.5, 1.0, -0.5], [2.0, 0.0, 0.0]], requires_grad=True)
    y = torch.tensor([1, 0])

    loss, grad = handler.compute_loss_and_grad(logits, y)
    loss.backward()
    loss_grad = logits.grad
    assert loss_grad is not None

    torch.testing.assert_close(grad, loss_grad * len(y))


def test_a_regression_gradient_is_the_residual() -> None:
    """The residual, not the mean squared error's 2/N-scaled gradient."""
    handler = TaskHandler("regression", output_dim=1)
    logits = torch.tensor([[0.5], [1.5]], requires_grad=True)
    y = torch.tensor([0.0, 2.0])

    loss, grad = handler.compute_loss_and_grad(logits, y)
    loss.backward()
    loss_grad = logits.grad
    assert loss_grad is not None

    torch.testing.assert_close(grad, loss_grad * len(y) / 2)


def test_a_perfect_regression_scores_one() -> None:
    handler = TaskHandler("regression", output_dim=1)

    accuracy = handler.compute_metrics(
        torch.tensor([[1.0], [2.0]]), torch.tensor([1.0, 2.0])
    )

    assert accuracy == pytest.approx(1.0)


def test_a_nan_prediction_scores_zero_not_nan() -> None:
    handler = TaskHandler("classification", output_dim=3)

    accuracy = handler.compute_metrics(
        torch.tensor([[float("nan"), 0.0, 0.0]]), torch.tensor([0])
    )

    assert accuracy == 0.0


def test_a_binary_gradient_is_the_sigmoid_residual() -> None:
    handler = TaskHandler("binary", output_dim=1)
    logits = torch.tensor([[0.0], [2.0]], requires_grad=True)
    y = torch.tensor([[0.0], [1.0]])

    loss, grad = handler.compute_loss_and_grad(logits, y)
    loss.backward()

    assert loss.item() == pytest.approx(
        F.binary_cross_entropy_with_logits(logits, y).item()
    )
    loss_grad = logits.grad
    assert loss_grad is not None
    torch.testing.assert_close(grad, loss_grad * len(y))


@pytest.fixture
def _isolated_registry():
    registry = dict(_TILE_ALGORITHM_REGISTRY)
    factories = dict(_TILE_ALGORITHM_FACTORIES)
    yield
    _TILE_ALGORITHM_REGISTRY.clear()
    _TILE_ALGORITHM_REGISTRY.update(registry)
    _TILE_ALGORITHM_FACTORIES.clear()
    _TILE_ALGORITHM_FACTORIES.update(factories)


def test_a_registered_factory_returns_its_metadata(_isolated_registry: None) -> None:
    @tile_algorithm(
        "w64_variant",
        algorithm="ep",
        mode="ep",
        description="a test variant",
        default_beta=0.5,
        tags=["test"],
    )
    def factory() -> str:
        return "built"

    metadata = get_tile_algorithm_metadata("w64_variant")

    assert metadata.name == "w64_variant"
    assert metadata.default_beta == 0.5
    assert metadata.tags == ["test"]
    assert get_tile_algorithm_factory("w64_variant") is factory
    assert "w64_variant" in list_tile_algorithms()


def test_an_unknown_variant_is_refused_with_the_available_list(
    _isolated_registry: None,
) -> None:
    with pytest.raises(ValueError, match="Unknown TileAlgorithm variant: w64_missing"):
        get_tile_algorithm_metadata("w64_missing")
    with pytest.raises(ValueError, match="Available:"):
        get_tile_algorithm_factory("w64_missing")


def test_a_listed_variant_is_a_copy_of_the_registry(_isolated_registry: None) -> None:
    listed = list_tile_algorithms_with_metadata()
    listed.clear()

    assert len(_TILE_ALGORITHM_REGISTRY) == len(list_tile_algorithms())
    assert len(list_tile_algorithms()) > 0


def test_a_local_update_writes_a_delta_and_leaves_grad_alone() -> None:
    """The local credit is ``w -= delta``; ``.grad`` is the autograd path's."""
    torch.manual_seed(0)
    model = _model()
    src_id, dst_id = model.graph.edges[0]
    weights = model._tile_weights[model._weight_key(src_id, dst_id)]
    before = weights.detach().clone()

    metrics = model.local_update(torch.randn(4, 8), torch.tensor([0, 1, 2, 3]))

    assert weights.grad is None
    assert not torch.equal(weights, before)
    assert metrics["loss"] == pytest.approx(metrics["loss"])  # not NaN


def test_an_autograd_step_writes_the_gradient_it_optimizes() -> None:
    """The BPTT baseline reads ``.grad``; the same parameters take both paths."""
    torch.manual_seed(0)
    model = _model()

    metrics = model.train_step(torch.randn(4, 8), torch.tensor([0, 1, 2, 3]))

    assert model.W_out.weight.grad is not None
    assert metrics["loss"] > 0.0
    assert 0.0 <= metrics["accuracy"] <= 1.0
