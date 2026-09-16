"""Local-training adapter — adaptive feedback plugged into a local-credit loop.

A two-layer MLP trained WITHOUT backprop across the output layer: the output
error is projected back to the hidden space through the feedback matrix ``B``
(pseudo-gradient), and each layer updates from its own local signals. This is
the loop the X-ALI-001 probe measured on Computronium systems, reduced to a
standalone torch form.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import torch
import torch.nn.functional as F  # ruff: ignore[lowercase-imported-as-non-lowercase]  (torch-idiomatic alias)
from torch import Tensor, nn

from local_feedback.metrics import improvement_per_norm

if TYPE_CHECKING:
    from local_feedback.adaptive import AdaptiveFeedback


@dataclass(frozen=True, slots=True)
class StepStats:
    """One local training step's measured quantities."""

    loss_before: float
    loss_after: float
    displacement_norm: float
    improvement_per_norm: float


class LocalFeedbackTrainer:
    """Local-credit training loop for a fixed ``nn.Linear`` stack.

    The model must be a sequence ending in ``nn.Linear``; the last layer is
    the readout. Hidden-layer credit comes from ``feedback.project(error)``
    instead of a backward pass through the readout weight.
    """

    def __init__(
        self,
        model: nn.Module,
        feedback: AdaptiveFeedback,
        lr: float,
    ) -> None:
        layers = [m for m in model.modules() if isinstance(m, nn.Linear)]
        if len(layers) < 2:
            raise ValueError("model needs at least two Linear layers")
        self.readout = layers[-1]
        self.hidden = layers[-2]
        self.model = model
        self.feedback = feedback
        self.lr = lr

    def forward(self, x: Tensor) -> Tensor:
        h = F.relu(x @ self.hidden.weight.T + self.hidden.bias)
        return h @ self.readout.weight.T + self.readout.bias

    def train_step(self, x: Tensor, y: Tensor) -> StepStats:
        """One local step: feedback-projected hidden credit + readout grad."""
        h = F.relu(x @ self.hidden.weight.T + self.hidden.bias)
        logits = h @ self.readout.weight.T + self.readout.bias
        loss_before = float(F.cross_entropy(logits, y).item())
        error = F.softmax(logits, dim=-1) - F.one_hot(y, logits.shape[-1]).to(
            logits.dtype
        )

        g_readout = error.T @ h
        dh = self.feedback.project(error)
        g_hidden = dh.T @ x

        params = {
            "hidden.weight": self.hidden.weight,
            "hidden.bias": self.hidden.bias,
            "readout.weight": self.readout.weight,
            "readout.bias": self.readout.bias,
        }
        grads = {
            "hidden.weight": g_hidden,
            "hidden.bias": dh.sum(0),
            "readout.weight": g_readout,
            "readout.bias": error.sum(0),
        }
        before = {k: param.detach().clone() for k, param in params.items()}
        with torch.no_grad():
            for k, param in params.items():
                param -= self.lr * grads[k]  # ruff: ignore[redefined-loop-name]  in-place tensor update
        displacement = (
            sum(
                float((params[k].detach() - before[k]).norm().item()) ** 2
                for k in params
            )
            ** 0.5
        )

        with torch.no_grad():
            loss_after = float(F.cross_entropy(self.forward(x), y).item())
        self.feedback.update(self.readout.weight.detach(), h.detach())
        return StepStats(
            loss_before=loss_before,
            loss_after=loss_after,
            displacement_norm=displacement,
            improvement_per_norm=improvement_per_norm(
                loss_before, loss_after, displacement
            ),
        )
