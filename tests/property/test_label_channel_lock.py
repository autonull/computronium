"""Lock: the label channel ``local_contrastive`` reads its target from (N7).

``LocalContrastiveCredit`` slices the last ``label_dim`` input features as the
one-hot target. Before N7 the kernel gave it the task's own width, so it
sliced the last ten pixels as its "label" and trained a contrast against noise
(mnist 0.11-0.12 for 10 epochs, loss 17 -> 3459 — G11). The channel now exists
in one place:

1. composition widens the input layer by the task's class count,
2. every training batch is ``[x | one_hot(y)]``,
3. inference sweeps the candidates and scores each with the readout's own
   logit — the true label never reaches the sweep.

Falsified by reverting any of the three: the geometry is 10 features too narrow,
the credit mis-slices pixels as labels, or ``forward`` needs the answer it is
supposed to predict.
"""

from __future__ import annotations

import torch

from computronium.core.label_channel import (
    LabelChannelSystem,
    augmented_input_shape,
    label_augmented,
    probe_input,
)
from computronium.experiment.kernel.compose import compose_cell_system
from computronium.experiment.schema.coordinate import Coordinate


def _coordinate(credit: str = "local_contrastive") -> Coordinate:
    return Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="instantaneous",
        plasticity="null",
        credit=credit,
        update="adam",
        params={},
    )


def _compose(output_dim: int, input_shape: tuple[int, ...], credit="local_contrastive"):
    return compose_cell_system(
        coordinate=_coordinate(credit),
        geometry={"hidden_dim": 16, "num_layers": 1},
        input_shape=input_shape,
        output_dim=output_dim,
    )


class _Recorder:
    """A composed-system stand-in that records the rows it is handed."""

    def __init__(self, classes: int, data_width: int = 8) -> None:
        self.classes = classes
        self.data_width = data_width
        self.rows: list[torch.Tensor] = []
        self.geometry = object()

    def train_step(self, x: torch.Tensor, y: torch.Tensor, **_: object) -> dict:
        self.rows.append(x.detach().clone())
        return {"loss": 0.0}

    def forward(self, x: torch.Tensor, *_: object) -> torch.Tensor:
        """Endorse the class the *data* columns name, ignoring the channel."""
        self.rows.append(x.detach().clone())
        secret = x[:, : self.data_width].argmax(-1, keepdim=True)
        k = torch.arange(self.classes, device=x.device)
        return (k == secret).to(x.dtype)


def test_composition_widens_the_input_by_the_class_count() -> None:
    """MNIST's 784 rows become 794; a three-class task gets three, not ten."""
    mnist = _compose(10, (1, 28, 28))
    assert mnist.system.geometry.config.input_dim == 784 + 10
    assert mnist.system.label_dim == 10
    wine = _compose(3, (13,))
    assert wine.system.geometry.config.input_dim == 13 + 3


def test_a_credit_without_a_channel_is_left_alone() -> None:
    """Gradient credit reads no label channel: same width, no proxy."""
    cell = _compose(10, (1, 28, 28), credit="gradient")
    assert cell.system.geometry.config.input_dim == 784
    assert not isinstance(cell.system, LabelChannelSystem)


def test_training_batch_carries_the_one_hot_target() -> None:
    """The rows the pipeline sees are ``[x | one_hot(y)]``, in that order."""
    inner = _Recorder(classes=3)
    system = LabelChannelSystem(inner, output_dim=3, label_dim=3)
    x = torch.randn(5, 13)
    y = torch.tensor([0, 1, 2, 1, 0])
    system.train_step(x, y)
    (rows,) = inner.rows
    assert rows.shape == (5, 16)
    assert torch.equal(rows[:, :13], x)
    assert torch.equal(rows[:, 13:], torch.nn.functional.one_hot(y, 3).float())


def test_the_sweep_never_reads_the_true_label() -> None:
    """Inference scores every candidate from the input alone."""
    inner = _Recorder(classes=4, data_width=4)
    system = LabelChannelSystem(inner, output_dim=4, label_dim=4)
    x = torch.randn(6, 8)
    scores = system.forward(x)  # no y is available at inference
    assert scores.shape == (6, 4)
    # The stand-in endorses the class its data columns name; the sweep must
    # find it through block c's column c, so a wrong row/column pairing shows.
    assert torch.equal(scores.argmax(-1), x[:, :4].argmax(-1))
    # One pass of C·B rows, not C passes.
    assert len(inner.rows) == 1
    assert inner.rows[0].shape == (4 * 6, 12)


def test_the_proxy_is_callable_like_the_system_it_wraps() -> None:
    """Tasks call ``system(x)``; special methods are not reached by __getattr__."""
    inner = _Recorder(classes=4, data_width=4)
    system = LabelChannelSystem(inner, output_dim=4, label_dim=4)
    x = torch.randn(3, 8)
    assert torch.equal(system(x), system.forward(x))
    # ...and everything else still resolves through the composed system.
    assert system.geometry is inner.geometry
    system.marker = 7
    assert inner.marker == 7


def test_label_augmented_refuses_labels_outside_the_channel() -> None:
    """A class count mismatch is named, not one-hot encoded out of range."""
    x = torch.randn(2, 5)
    for labels in (torch.tensor([0, 7]), torch.tensor([-1, 0])):
        try:
            label_augmented(x, labels, 3)
        except ValueError as exc:
            assert "label channel is 3 wide" in str(exc)
        else:  # pragma: no cover - the refusal is the lock
            raise AssertionError(f"accepted out-of-range labels {labels.tolist()}")


def test_augmented_shape_is_flat() -> None:
    """A 3-D task shape flattens into the channel width, not a wider image."""
    assert augmented_input_shape((1, 28, 28), 10) == (794,)
    assert augmented_input_shape((1, 28, 28), 0) == (1, 28, 28)


def test_probe_input_carries_no_label_information() -> None:
    """Settle telemetry runs on a zero channel, not on a guessed class."""
    inner = _Recorder(classes=3)
    system = LabelChannelSystem(inner, output_dim=3, label_dim=3)
    x = torch.randn(4, 13)
    rows = probe_input(system, x)
    assert rows.shape == (4, 16)
    assert torch.equal(rows[:, 13:], torch.zeros(4, 3))
    assert probe_input(inner, x) is x


def test_a_stream_normalizing_credit_gets_a_normalizing_geometry() -> None:
    """The credit's recompute and the pipeline must normalize the same stream.

    Without this the head is trained on unit-scale features and applied to
    unbounded ones: free CE grew 223 -> 1121 over ten epochs while accuracy
    stalled at 0.52 (G20).
    """
    cell = _compose(10, (1, 28, 28))
    assert cell.system.geometry.config.stream_norm is True


def test_every_post_activation_has_length_sqrt_width() -> None:
    """Stream normalization is a geometry property, not a credit one."""
    from computronium.ontology.geometry import GeometryConfig, geometry_from_config

    normalizing = geometry_from_config(
        GeometryConfig.feedforward(
            input_dim=8, output_dim=4, hidden_dims=(16, 16), stream_norm=True
        )
    )
    plain = geometry_from_config(
        GeometryConfig.feedforward(input_dim=8, output_dim=4, hidden_dims=(16, 16))
    )
    x = torch.randn(5, 8) * 5.0
    for acts in (normalizing, plain):
        hidden = acts.forward_with_intermediates(x)[1:-1]
        assert len(hidden) == 2
    for h in normalizing.forward_with_intermediates(x)[1:-1]:
        expected = torch.full((5,), h.shape[-1] ** 0.5)
        assert torch.allclose(h.norm(dim=-1), expected, atol=1e-5)
    plain_hidden = plain.forward_with_intermediates(x)[1]
    assert not torch.allclose(
        plain_hidden.norm(dim=-1), torch.full((5,), plain_hidden.shape[-1] ** 0.5)
    )
