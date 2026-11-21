"""Gradient-estimator credits: forward-mode, score-function, zeroth-order.

Each estimator is an unbiased estimate of the exact gradient of a scalar
objective, built from forward evaluations only. The reference uses
``torch.func`` (jvp / grad / two forwards) so the estimator's sampling
variance is isolated from reverse-mode plumbing; a kernel can replace the
functional closure with a cheaper device path without changing the signal.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, cast

import torch
from torch import Tensor, nn
from torch.func import functional_call, grad, jvp

from computronium.core.identity_card import AlgorithmIdentityCard
from computronium.core.losses import cross_entropy, mean_squared_error
from computronium.ontology._utils import (
    _align_target_rows,
    _learnable_weight_names,
    apply_norm,
)
from computronium.ontology.credit._base import Phase

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

    from computronium.ontology.credit import CreditAssignmentConfig
    from computronium.ontology.dynamics._state import SettableState
    from computronium.ontology.geometry import Geometry


def _task_loss(logits: Tensor, target: Tensor) -> Tensor:
    """The declared task loss: class-index targets use CE, values use MSE.

    The geometry folds the token lane into its readout rows (``[B*T, V]``), so
    a per-token target must fold with it before the CE broadcast (the same
    one source the trainer reads: ``_align_target_rows``).
    """
    if target.is_floating_point():
        return mean_squared_error(logits, target)
    return cross_entropy(logits, _align_target_rows(logits, target))


def _functional_names(geometry: Geometry) -> tuple[list[str], list[str]]:
    """``(geometry param names, matching functional-call names)``.

    ``geometry.params`` names a layer's tensors ``0.weight`` while
    ``functional_call`` addresses the module as ``_layers.0.weight``. Match
    by parameter identity first, so a geometry with its own naming scheme
    (conv layers, transformer blocks) needs no suffix convention.
    """
    module = cast("nn.Module", geometry)
    functional = dict(module.named_parameters())
    by_identity = {id(param): name for name, param in functional.items()}
    names = list(geometry.params)
    matched = []
    for name in names:
        match = by_identity.get(id(geometry.params[name]))
        if match is None:
            suffix = f".{name}"
            match = next(
                (candidate for candidate in functional if candidate.endswith(suffix)),
                None,
            )
        if match is None:
            raise RuntimeError(
                f"estimator credit: no functional parameter name matches {name!r}"
            )
        matched.append(match)
    return names, matched


class _EstimatorCredit:
    """Shared functional evaluator for the three unbiased estimators."""

    phases: ClassVar[tuple[Phase, ...]] = (Phase.FREE,)
    error_blind: ClassVar[bool] = False
    requires_autograd: ClassVar[bool] = False

    def __init__(self, config: CreditAssignmentConfig | None = None):
        if config is None:
            raise ValueError(f"{type(self).__name__}: a config is required")
        self.config = config

    def _free(self, states: Mapping[Phase, SettableState]) -> SettableState:
        state = states.get(Phase.FREE)
        if state is None:
            raise RuntimeError(
                f"{type(self).__name__}: the FREE phase is not in the settled set"
            )
        return state

    def _x_y(self, state: SettableState) -> tuple[Tensor, Tensor]:
        x, y = state.x, state.y
        if x is None or y is None:
            raise RuntimeError(
                f"{type(self).__name__}: the FREE state carries no input/target"
            )
        return x, y

    def _closure(
        self, geometry: Geometry, x: Tensor, y: Tensor
    ) -> tuple[Callable[[Sequence[Tensor]], Tensor], list[Tensor], list[str]]:
        """``(loss(params), parameter values, parameter names)`` at ``x, y``."""
        names, functional = _functional_names(geometry)
        params = list(geometry.params.values())
        module = cast("nn.Module", geometry)

        def loss(values: Sequence[Tensor]) -> Tensor:
            env = dict(zip(functional, values, strict=True))
            logits = functional_call(module, env, (x,))
            return _task_loss(logits, y)

        return loss, params, names

    def _weight_grads(
        self,
        geometry: Geometry,
        names: list[str],
        grads: Sequence[Tensor],
    ) -> list[Tensor]:
        """Keep the learnable-weight entries in the geometry's declared order."""
        by_name = dict(zip(names, grads, strict=True))
        ordered = [by_name[name] for name in _learnable_weight_names(geometry.params)]
        return apply_norm(ordered, self.config.credit_norm)


class ForwardTangentCredit(_EstimatorCredit):
    """Pathwise gradient by random forward-mode tangents.

    ``v ~ Rademacher(θ)``; ``d = jvp(f, θ, v)``; ``ĝ = d · v``. Since
    ``E[vvᵀ] = I``, the estimate is unbiased and its variance falls as
    ``1/√n`` tangents. No reverse-mode graph is retained over the settle.
    """

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="ForwardTangentCredit",
        estimator_kind="forward_mode",
        bias_reference="unbiased_pathwise",
        reference_equations=(
            "forward-mode pathwise estimator; v ~ Rademacher(θ), "
            "d = jvp(f, θ, v), ĝ = d·v (Pearlmutter 1994)"
        ),
        deviations_from_literature=(
            "the reference evaluates the tangent with torch.func.jvp on a "
            "functional closure of the geometry; the kernel may batch tangents",
        ),
        objective_function="the task loss f(θ) at the FREE-phase input/target",
        pseudo_gradient_def="ĝ = (1/n) Σ_i (jvp(f, θ, v_i)) · v_i",
        symmetry_requirements=("none",),
        approximation_parameters=("num_tangents",),
        validated_limits=(
            "cos > 0.3 against the exact gradient at 8 tangents on the "
            "tiny fixture, and the variance falls as 1/√n",
        ),
    )

    def __init__(self, config: CreditAssignmentConfig | None = None):
        from computronium.ontology.credit import CreditAssignmentConfig

        super().__init__(config or CreditAssignmentConfig.forward_tangent())

    def compute_pseudo_gradient(
        self,
        states: Mapping[Phase, SettableState],
        loss: Tensor | None,
        geometry: Geometry,
    ) -> list[Tensor]:
        state = self._free(states)
        x, y = self._x_y(state)
        loss_fn, params, names = self._closure(geometry, x, y)
        samples = max(1, int(self.config.estimator_samples))
        grads = [torch.zeros_like(p) for p in params]
        # The fused oneDNN LSTM kernel has no forward-AD rule; a recurrent
        # geometry (NTM) would abort the tangent pass. The differentiable
        # ATen path is the tangent's contract, not a different mechanism.
        with torch.no_grad(), torch.backends.mkldnn.flags(enabled=False):
            for _ in range(samples):
                tangents = tuple(
                    torch.randint_like(p, 0, 2, dtype=p.dtype) * 2 - 1 for p in params
                )
                directional = jvp(loss_fn, (tuple(params),), (tangents,))[1]
                for i, tangent in enumerate(tangents):
                    grads[i] += directional * tangent
        return self._weight_grads(
            geometry,
            names,
            [g / samples for g in grads],
        )


class ScoreFunctionCredit(_EstimatorCredit):
    """Score-function (REINFORCE) gradient of an expected task loss.

    ``a ~ Categorical(softmax(logits))``; ``ĝ = ∇_θ log π(a) · (R(a) − b)``
    with ``R(a) = 1[a = y]`` (the finite form of ``−CE(a, y)`` up to a
    baseline-shifted constant) and ``b = mean_batch R``. The estimate is
    unbiased for the expected reward, and its variance falls as ``1/√n``.
    """

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="ScoreFunctionCredit",
        estimator_kind="score_function",
        bias_reference="unbiased_expected",
        reference_equations=(
            "score-function / REINFORCE estimator; a ~ π_θ, "
            "ĝ = ∇_θ log π_θ(a) (R(a) − b) (Williams 1992)"
        ),
        deviations_from_literature=(
            "R(a) = 1[a = y] is the finite reward; the plan's −CE(a, y) "
            "notation is its negative penalty form, and the baseline removes "
            "the constant",
            "the reference builds its own reverse-mode graph inside the "
            "credit; the settle graph stays detached",
        ),
        objective_function="expected reward E_{a~π_θ}[1[a = y]] (negative expected task loss)",
        pseudo_gradient_def="ĝ = -(1/n) Σ_i ∇_θ log π_θ(a_i) (R(a_i) − b), b = mean R",
        symmetry_requirements=("none",),
        approximation_parameters=("num_samples",),
        validated_limits=(
            "cos > 0.9 against the exact gradient of the expected loss at "
            "1024 samples on a two-action fixture",
        ),
    )

    def __init__(self, config: CreditAssignmentConfig | None = None):
        from computronium.ontology.credit import CreditAssignmentConfig

        super().__init__(config or CreditAssignmentConfig.score_function())

    def compute_pseudo_gradient(
        self,
        states: Mapping[Phase, SettableState],
        loss: Tensor | None,
        geometry: Geometry,
    ) -> list[Tensor]:
        state = self._free(states)
        x, y = self._x_y(state)
        _loss_fn, params, names = self._closure(geometry, x, y)
        samples = max(1, int(self.config.estimator_samples))

        with torch.no_grad():
            logits = functional_call(
                cast("nn.Module", geometry),
                dict(zip(_functional_names(geometry)[1], params, strict=True)),
                (x,),
            )
            actions = torch.multinomial(
                torch.softmax(logits, dim=-1),
                samples,
                replacement=True,
            )

        reward = (actions == y.reshape(-1, 1)).float()
        advantage = reward - reward.mean()

        def weighted_log_prob(values: Sequence[Tensor]) -> Tensor:
            env = dict(zip(_functional_names(geometry)[1], values, strict=True))
            logits = functional_call(cast("nn.Module", geometry), env, (x,))
            log_probs = torch.log_softmax(logits, dim=-1)
            return (log_probs.gather(1, actions) * advantage).sum()

        return self._weight_grads(
            geometry,
            names,
            [-g for g in grad(weighted_log_prob)(tuple(params))],
        )


class ZerothOrderCredit(_EstimatorCredit):
    """Gradient-free SPSA estimate from two forward evaluations.

    ``Δ ~ Rademacher(θ)``; ``ĝ = (L(θ + cΔ) − L(θ − cΔ)) / (2c) · Δ``.
    Two forwards per pair, no reverse-mode graph. The variance falls as
    ``1/√n`` pairs at a fixed ``c``.
    """

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="ZerothOrderCredit",
        estimator_kind="zeroth_order",
        bias_reference="finite_difference",
        reference_equations=(
            "SPSA / finite-difference estimator; Δ ~ Rademacher(θ), "
            "ĝ = (L(θ+cΔ) − L(θ−cΔ)) / (2c) · Δ (Spall 1992)"
        ),
        deviations_from_literature=(
            "the reference runs the two forwards through a functional "
            "closure of the geometry; the kernel may fuse the pair",
        ),
        objective_function="the task loss f(θ) at the FREE-phase input/target",
        pseudo_gradient_def="ĝ = (1/n) Σ_i (L(θ+cΔ_i) − L(θ−cΔ_i)) / (2c) · Δ_i",
        symmetry_requirements=("none",),
        approximation_parameters=("num_pairs", "fd_step"),
        validated_limits=(
            "cos > 0.9 against the exact gradient at 256 pairs on a quadratic fixture",
        ),
    )

    def __init__(self, config: CreditAssignmentConfig | None = None):
        from computronium.ontology.credit import CreditAssignmentConfig

        super().__init__(config or CreditAssignmentConfig.zeroth_order())

    @classmethod
    def reads(cls, config: CreditAssignmentConfig) -> frozenset[str] | None:
        """The SPSA pair budget and the finite-difference step are read.

        Measured 2026-11-20 (S9e probe): ``feedback_scale`` leaves the
        pseudo-gradient norm bit-identical, while ``fd_step`` moves it
        (76.8 / 79.4 / 115.9 at 0.001/0.01/0.1). The ladder therefore
        withdraws ``feedback_scale`` and sweeps ``credit.fd_step``.
        """
        del config  # the pair budget and the step are the whole config read
        return frozenset({"estimator_samples", "fd_step", "credit_norm"})

    def compute_pseudo_gradient(
        self,
        states: Mapping[Phase, SettableState],
        loss: Tensor | None,
        geometry: Geometry,
    ) -> list[Tensor]:
        state = self._free(states)
        x, y = self._x_y(state)
        loss_fn, params, names = self._closure(geometry, x, y)
        pairs = max(1, int(self.config.estimator_samples))
        step = float(self.config.fd_step)
        grads: list[Tensor] = [torch.zeros_like(p) for p in params]
        with torch.no_grad():
            for _ in range(pairs):
                directions = tuple(
                    torch.randint_like(p, 0, 2, dtype=p.dtype) * 2 - 1 for p in params
                )
                plus = loss_fn(
                    tuple(p + step * d for p, d in zip(params, directions, strict=True))
                )
                minus = loss_fn(
                    tuple(p - step * d for p, d in zip(params, directions, strict=True))
                )
                scale = float(plus - minus) / (2 * step * pairs)
                for i, direction in enumerate(directions):
                    grads[i] += scale * direction
        return self._weight_grads(geometry, names, grads)
