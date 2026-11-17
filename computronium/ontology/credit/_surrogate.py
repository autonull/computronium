"""Straight-through surrogate credit for hard top-k routing.

A hard top-k gate has no useful derivative: its selection is piecewise
constant, so the exact gradient of the task loss is zero almost everywhere.
The surrogate replaces the selection's derivative with the derivative of a
temperature-smoothed softmax while keeping the hard forward, so the gate
receives the direction that lowers the loss at its own selection.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import torch
from torch import Tensor, nn
from torch.func import functional_call, grad

from computronium.core.identity_card import AlgorithmIdentityCard
from computronium.ontology.credit._estimators import (
    _EstimatorCredit,
    _functional_names,
    _task_loss,
)

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from computronium.ontology.credit import CreditAssignmentConfig
    from computronium.ontology.credit._base import Phase
    from computronium.ontology.dynamics._state import SettableState
    from computronium.ontology.geometry import Geometry


class SurrogateCredit(_EstimatorCredit):
    """Gradient of a hard top-k selection through its straight-through surrogate.

    ``g = gate(h)``; ``w = topk(softmax(g/τ))`` (hard, renormalized);
    ``w̃ = w + softmax(g/τ) − softmax(g/τ).detach()``; ``ĝ = ∇_θ L(θ; w̃)``.
    The forward selection stays hard at eval, so the estimate is the derivative
    of the surrogate, not of the hard gate (which is zero almost everywhere).
    """

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="SurrogateCredit",
        estimator_kind="surrogate",
        bias_reference="smoothed_objective",
        reference_equations=(
            "straight-through / Gumbel-softmax surrogate for a hard top-k "
            "selection; g = gate(h), w = topk(softmax(g/τ)), "
            "w̃ = w + softmax(g/τ) − softmax(g/τ).detach(), ĝ = ∇_θ L(θ; w̃) "
            "(Bengio et al. 2013; Jang et al. 2017)"
        ),
        deviations_from_literature=(
            "the reference builds the surrogate pass inside the credit and "
            "reads the geometry's declared temperature; the hard forward is "
            "unchanged at eval",
            "the reference reads a routing geometry's gate as its target; a "
            "geometry without a top-k gate is refused, not approximated",
        ),
        objective_function="the task loss at the hard-selected expert mixture",
        pseudo_gradient_def="ĝ = ∇_θ L(θ; w = topk + soft − soft.detach())",
        symmetry_requirements=("none",),
        approximation_parameters=("top_k", "routing_temperature"),
        validated_limits=(
            "cos = 1.0 against autograd of the same straight-through forward",
            "cos > 0.9 against the temperature-smoothed reference",
        ),
    )

    def __init__(self, config: CreditAssignmentConfig | None = None):
        from computronium.ontology.credit import CreditAssignmentConfig

        super().__init__(config or CreditAssignmentConfig.surrogate())

    def _surrogate_closure(
        self,
        geometry: Geometry,
        x: Tensor,
        y: Tensor,
        surrogate: str,
    ):
        """``(loss(params), parameter values, parameter names)`` through the gate."""
        names, functional = _functional_names(geometry)
        params = list(geometry.params.values())
        module = cast("nn.Module", geometry)

        def loss(values: Sequence[Tensor]) -> Tensor:
            env = dict(zip(functional, values, strict=True))
            logits = functional_call(module, env, (x,), {"surrogate": surrogate})
            return _task_loss(logits, y)

        return loss, params, names

    def compute_pseudo_gradient(
        self,
        states: Mapping[Phase, SettableState],
        loss: Tensor | None,
        geometry: Geometry,
    ) -> list[Tensor]:
        state = self._free(states)
        x, y = self._x_y(state)
        if not callable(getattr(geometry, "selection_weights", None)):
            raise TypeError(
                "SurrogateCredit: the geometry carries no hard top-k gate; "
                "a surrogate without a selection is not an estimator of one"
            )
        loss_fn, params, names = self._surrogate_closure(geometry, x, y, "ste")
        with torch.no_grad():
            return self._weight_grads(
                geometry,
                names,
                grad(loss_fn)(tuple(params)),
            )
