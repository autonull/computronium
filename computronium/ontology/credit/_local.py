"""Local supervision credit: each hidden layer's own supervised head.

Greedy layerwise training (Belilovsky et al. 2019, arXiv 1901.11107) and deep
local supervision (InfoPro, arXiv 2102.06566) train every hidden layer against
its own auxiliary head, so no boundary bottleneck sits between a layer and its
learning signal.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, cast

import torch
from torch import Tensor, nn

from computronium.core.identity_card import AlgorithmIdentityCard
from computronium.ontology._utils import (
    _learnable_weight_names,
    output_target,
)
from computronium.ontology.credit._base import Phase

if TYPE_CHECKING:
    from collections.abc import Mapping

    from computronium.ontology.credit import CreditAssignmentConfig
    from computronium.ontology.dynamics._state import SettableState
    from computronium.ontology.geometry import FeedforwardGeometry, Geometry


def _loss(logits: Tensor, target: Tensor) -> Tensor:
    """CE for a class index, MSE for a value target (the task's contract)."""
    from computronium.core.losses import cross_entropy, mean_squared_error

    projected = output_target(target, logits)
    if projected.shape == logits.shape and target.is_floating_point():
        return mean_squared_error(logits, projected)
    return cross_entropy(logits, target)


class LocalSupervisionCredit:
    """Deep local credit: one supervised head per hidden Linear.

    Every hidden layer's weight receives the gradient of its own auxiliary loss
    through one fixed projection of that layer's activation; the readout keeps
    the exact task gradient of its own input. No gradient crosses a layer
    boundary, so the peak activation set is O(1) layers.
    """

    phases: ClassVar[tuple[Phase, ...]] = (Phase.FREE,)
    error_blind: ClassVar[bool] = False
    requires_autograd: ClassVar[bool] = True
    IDENTITY_CARD = AlgorithmIdentityCard(
        name="LocalSupervisionCredit",
        estimator_kind="local_supervised",
        bias_reference="none",
        reference_equations=(
            "greedy layerwise / deep local supervision; Belilovsky et al. "
            "(2019) arXiv 1901.11107, InfoPro (2021) arXiv 2102.06566"
        ),
        deviations_from_literature=(
            "the auxiliary head is one fixed orthonormalized projection of "
            "the layer's activation onto the task's classes",
            "the readout keeps the exact task gradient; every hidden layer "
            "reads only its own auxiliary loss",
            "biases are not trained: the axis contract is one gradient per 2-D weight",
        ),
        objective_function=("Σ_ℓ CE(s·A_ℓ φ(W_ℓ x_{ℓ−1}), y) + CE(readout φ(h))"),
        pseudo_gradient_def="ĝ_ℓ = ∇_{W_ℓ} CE(s·A_ℓ φ(W_ℓ x_{ℓ−1}), y)",
        symmetry_requirements=("none",),
        approximation_parameters=("aux_head_scale",),
        validated_limits=(
            "each hidden layer's auxiliary loss falls on a separable fixture",
            "the auxiliary head's gradient equals the layer's exact gradient "
            "through the identical projection",
        ),
    )

    def __init__(self, config: CreditAssignmentConfig | None = None):
        from computronium.ontology.credit import CreditAssignmentConfig

        self.config = config or CreditAssignmentConfig.local_supervision()
        self._aux_heads: dict[int, Tensor] = {}

    def _aux_head(self, position: int, like: Tensor, classes: int) -> Tensor:
        """The layer's fixed projection (classes × width), drawn once."""
        width = like.shape[-1]
        head = self._aux_heads.get(position)
        if head is None:
            head = torch.empty((classes, width), device=like.device, dtype=like.dtype)
            torch.nn.init.orthogonal_(head)
            head *= self.config.aux_head_scale
            self._aux_heads[position] = head
        return head

    def _stack(self, geometry: Geometry) -> FeedforwardGeometry:
        from computronium.ontology.geometry import FeedforwardGeometry

        if not isinstance(geometry, FeedforwardGeometry):
            raise TypeError(
                "LocalSupervisionCredit requires a FeedforwardGeometry layer "
                f"stack; got {type(geometry).__name__}"
            )
        return geometry

    def _inputs(
        self, stack: FeedforwardGeometry, x: Tensor
    ) -> tuple[list[Tensor], list[int]]:
        """Every Linear's input activity, in stack order (a detached chain)."""
        inputs: list[Tensor] = []
        linears: list[int] = []
        h = x
        with torch.no_grad():
            for index, layer in enumerate(stack._layers):
                if isinstance(layer, nn.Linear):
                    inputs.append(h)
                    linears.append(index)
                    h @= layer.weight.T
                    if layer.bias is not None:
                        h += layer.bias
                else:
                    h = layer(h)
        return inputs, linears

    def _weight_grad(
        self,
        layer: nn.Linear,
        pre: Tensor,
        y: Tensor,
        head: Tensor | None,
        activation: nn.Module | None,
    ) -> Tensor:
        """One layer's own gradient, through its own head only."""
        with torch.enable_grad():
            weight = layer.weight.detach().requires_grad_(True)
            h = pre.detach() @ weight.T
            if layer.bias is not None:
                # Out-of-place: in-place adds pin the settle graph
                h = h + layer.bias.detach()  # ruff: ignore[non-augmented-assignment]
            if activation is not None:
                h = activation(h)
            logits = h if head is None else h @ head.T
            (grad,) = torch.autograd.grad(_loss(logits, y), weight)
        return grad

    def compute_pseudo_gradient(
        self,
        states: Mapping[Phase, SettableState],
        loss: Tensor | None,
        geometry: Geometry,
    ) -> list[Tensor]:
        state = states.get(Phase.FREE)
        if state is None or state.x is None or state.y is None:
            return []
        stack = self._stack(geometry)
        inputs, linears = self._inputs(stack, state.x)
        classes = cast("nn.Linear", stack._layers[linears[-1]]).out_features
        grads: dict[str, Tensor] = {}
        for order, (position, pre) in enumerate(
            zip(linears[:-1], inputs[:-1], strict=True)
        ):
            layer = cast("nn.Linear", stack._layers[position])
            aux = self._aux_head(position, inputs[order + 1], classes)
            grads[f"{position}.weight"] = self._weight_grad(
                layer,
                pre,
                state.y,
                aux,
                stack._layers[position + 1]
                if position + 1 < len(stack._layers)
                else None,
            )
        readout = linears[-1]
        grads[f"{readout}.weight"] = self._weight_grad(
            cast("nn.Linear", stack._layers[readout]),
            inputs[-1],
            state.y,
            None,
            None,
        )
        return [
            grads[name]
            for name in _learnable_weight_names(stack.params)
            if name in grads
        ]
