"""Temporal credits: e-prop, UORO, and the exact RTRL reference (TODO93 §19).

Every temporal credit reads one contract: the FREE state's ``x`` is a sequence
``(time, batch, input)``, its ``y`` is ``(time, batch)``, and the geometry is a
``RecurrentGeometry`` with one hidden layer. The cell is
``h_t = tanh(W_in x_t + W_rec h_{t-1} + b)`` and the readout is
``logits_t = W_out h_t + b_out``. The trio shares one unroll, one readout-only
learning signal ``L_t = ∂L/∂h_t``, and one loss, so the rules differ only in
how they carry ``∂h_t/∂θ``:

- ``EligibilityPropCredit``: a decaying per-sample trace (e-prop);
- ``UnbiasedOnlineRTRLCredit``: a rank-1 factor pair with the sign trick (UORO);
- ``RTRLReference``: the exact per-step Jacobian, the parity reference.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, cast

import torch
from torch import Tensor, nn

from computronium.core.identity_card import AlgorithmIdentityCard
from computronium.core.losses import cross_entropy
from computronium.ontology._utils import _learnable_weight_names
from computronium.ontology.credit._base import Phase

if TYPE_CHECKING:
    from collections.abc import Mapping

    from computronium.ontology.credit import CreditAssignmentConfig
    from computronium.ontology.dynamics._state import SettableState
    from computronium.ontology.geometry import Geometry, RecurrentGeometry

_IN, _OUT, _REC = "0.weight", "1.weight", "recurrent_weight"
_TWO_LINEARS = 2


def _recurrent(geometry: Geometry) -> tuple[nn.Linear, nn.Linear, Tensor]:
    """``(input Linear, readout Linear, recurrent weight)`` or a clear refusal."""
    from computronium.ontology.geometry import RecurrentGeometry

    if not isinstance(geometry, RecurrentGeometry):
        raise TypeError(
            "temporal credit requires a RecurrentGeometry with one hidden "
            f"layer; got {type(geometry).__name__}"
        )
    linears = [layer for layer in geometry._layers if isinstance(layer, nn.Linear)]
    recurrent = geometry._recurrent_weight
    if recurrent is None or len(linears) != _TWO_LINEARS:
        raise RuntimeError(
            "temporal credit needs two Linears and a recurrent weight; got "
            f"{len(linears)} Linear(s) and {recurrent!r}"
        )
    return linears[0], linears[1], recurrent


def _sequence(state: SettableState) -> tuple[Tensor, Tensor]:
    """The sequence contract: ``x`` ``(time, batch, input)``, ``y`` ``(time, batch)``."""
    x, y = state.x, state.y
    if x is None or y is None or x.dim() != 3 or y.dim() != 2:
        raise RuntimeError(
            "temporal credit reads a sequence state: x (time, batch, input) "
            "and y (time, batch); a 2-D state has no time axis"
        )
    return x, y


def _shift(states: Tensor) -> Tensor:
    """``h_{t-1}`` with ``h_{-1} = 0`` — the recurrent input of each step."""
    return torch.cat([torch.zeros_like(states[:1]), states[:-1]])


class _TemporalCredit:
    """Shared unroll, readout signal, and loss for the temporal credit family."""

    phases: ClassVar[tuple[Phase, ...]] = (Phase.FREE,)
    error_blind: ClassVar[bool] = False
    requires_autograd: ClassVar[bool] = False

    def __init__(self, config: CreditAssignmentConfig | None = None):
        if config is None:
            raise ValueError(f"{type(self).__name__}: a config is required")
        self.config = config

    def _unroll(self, geometry: RecurrentGeometry, x: Tensor) -> Tensor:
        """The hidden states of one detached chain, ``(time, batch, hidden)``.

        The geometry owns the unroll (``RecurrentGeometry.sequence_states``):
        the credit and the forward are one implementation of the equations,
        so the parity lock cannot drift from a second copy (TODO93 §19).
        """
        with torch.no_grad():
            return geometry.sequence_states(x)[0]

    def _readout(
        self, states: Tensor, linear_out: nn.Linear, y: Tensor
    ) -> tuple[Tensor, Tensor]:
        """The readout-only signal ``L_t`` and the readout weight gradient.

        One graph sits on a detached copy of the hidden states, so the signal
        never opens the recurrence (both the reference and the estimator rules
        unroll under ``no_grad``).
        """
        detached = states.detach().requires_grad_(True)
        weight = linear_out.weight
        logits = detached @ weight.T
        if linear_out.bias is not None:
            # Out-of-place: in-place adds pin the settle graph
            logits = logits + linear_out.bias  # ruff: ignore[non-augmented-assignment]
        loss = cross_entropy(logits.reshape(-1, logits.shape[-1]), y.reshape(-1))
        (signal, out_grad) = torch.autograd.grad(loss, (detached, weight))
        return signal, out_grad

    def compute_pseudo_gradient(
        self,
        states: Mapping[Phase, SettableState],
        loss: Tensor | None,
        geometry: Geometry,
    ) -> list[Tensor]:
        state = states.get(Phase.FREE)
        if state is None:
            return []
        x, y = _sequence(state)
        _, linear_out, recurrent = _recurrent(geometry)
        stack = cast("RecurrentGeometry", geometry)
        hidden = self._unroll(stack, x)
        signal, out_grad = self._readout(hidden, linear_out, y)
        grads = self._gradients(hidden, x, signal, recurrent)

        positions = [
            index
            for index, layer in enumerate(stack._layers)
            if isinstance(layer, nn.Linear)
        ]
        by_name = {
            f"{positions[0]}.weight": grads[_IN],
            f"{positions[1]}.weight": out_grad,
            _REC: grads[_REC],
        }
        names = _learnable_weight_names(stack.params)
        return [by_name[name] for name in names]

    def _gradients(
        self, hidden: Tensor, x: Tensor, signal: Tensor, recurrent: Tensor
    ) -> dict[str, Tensor]:
        raise NotImplementedError


class EligibilityPropCredit(_TemporalCredit):
    """e-prop: a decaying per-sample eligibility trace, then the signal.

    ``e_t^θ = α e_{t-1}^θ + ψ_t^θ`` with ``ψ_t^W_in = D_t x_t``,
    ``ψ_t^W_rec = D_t h_{t-1}`` and ``ψ_t^b = D_t`` (``D_t = 1 − h_t²``);
    ``ĝ = Σ_t Σ_b L_t e_t``. The recurrent Jacobian's off-diagonal
    propagation is replaced by the scalar trace decay ``α`` — the literature's
    e-prop approximation, documented on the card.
    """

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="EligibilityPropCredit",
        estimator_kind="temporal_local",
        bias_reference="none",
        reference_equations=(
            "e-prop (Bellec et al. 2020, Nature Communications 11:5477); "
            "eligibility trace times a readout learning signal"
        ),
        deviations_from_literature=(
            "the recurrent Jacobian's off-diagonal path is replaced by the "
            "scalar trace decay α (the paper's random-feedback form)",
            "the learning signal comes from the readout Linear alone; no "
            "reverse-mode graph crosses the recurrence",
        ),
        objective_function="Σ_t CE(W_out h_t + b_out, y_t)",
        pseudo_gradient_def=("e_t = α e_{t-1} + D_t ψ_t; ĝ = Σ_t Σ_b L_t e_t"),
        symmetry_requirements=("none",),
        approximation_parameters=("trace_decay",),
        validated_limits=(
            "the trace rule's gradient matches the exact RTRL reference on a "
            "one-step fixture (the recurrent path is exact there)",
        ),
    )

    def __init__(self, config: CreditAssignmentConfig | None = None):
        from computronium.ontology.credit import CreditAssignmentConfig

        super().__init__(config or CreditAssignmentConfig.eligibility_prop())

    def _gradients(
        self, hidden: Tensor, x: Tensor, signal: Tensor, recurrent: Tensor
    ) -> dict[str, Tensor]:
        time, batch, width = hidden.shape
        inputs = x.shape[-1]
        decay = self.config.trace_decay
        states = 1 - hidden**2
        previous = _shift(hidden)
        trace_in = torch.zeros((batch, width, inputs), device=x.device, dtype=x.dtype)
        trace_rec = torch.zeros((batch, width, width), device=x.device, dtype=x.dtype)
        # The gradients are summed over time and batch: the per-sample trace's
        # shape is the accumulator of the trace, not of its gradient.
        grad_in = torch.zeros((width, inputs), device=x.device, dtype=x.dtype)
        grad_rec = torch.zeros((width, width), device=x.device, dtype=x.dtype)
        for step in range(time):
            trace_in = decay * trace_in + states[step][:, :, None] * x[step][:, None, :]
            trace_rec = (
                decay * trace_rec
                + states[step][:, :, None] * previous[step][:, None, :]
            )
            grad_in += torch.einsum("bh,bhf->hf", signal[step], trace_in)
            grad_rec += torch.einsum("bh,bhi->hi", signal[step], trace_rec)
        return {_IN: grad_in, _REC: grad_rec}


class UnbiasedOnlineRTRLCredit(_TemporalCredit):
    """UORO: a rank-1 factor pair with the sign trick (Tallec & Ollivier 2017).

    ``Ĥ_t ≈ θ̃_t ρ̃_tᵀ``; each step draws a sign ``ν_t`` and a hidden row
    ``i_t``:

    ``θ̃_t = D_t (W_rec θ̃_{t-1}) + ν_t D_t u_t``,
    ``ρ̃_t = ρ̃_{t-1} + (1/ν_t) v_t``.

    With ``E[u uᵀ] = Γ`` the cross terms have zero mean and the estimate is
    unbiased, so a mean over draws matches the exact RTRL reference.
    """

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="UnbiasedOnlineRTRLCredit",
        estimator_kind="temporal_local",
        bias_reference="unbiased_pathwise",
        reference_equations=(
            "UORO (Tallec & Ollivier 2017, arXiv 1704.03194); rank-1 "
            "factored Jacobian with the unbiased sign trick"
        ),
        deviations_from_literature=(
            "the parameter factor is sampled per hidden row at one step, "
            "not per synapse",
            "the learning signal comes from the readout Linear alone",
        ),
        objective_function="Σ_t CE(W_out h_t + b_out, y_t)",
        pseudo_gradient_def=("Ĥ_t ≈ θ̃_t ρ̃_tᵀ; dθ = Σ_t Σ_b L_t ⊙ θ̃_t ρ̃_t"),
        symmetry_requirements=("none",),
        approximation_parameters=("uoro_seed",),
        validated_limits=(
            "cos > 0.9 against the exact RTRL reference over 128 draws on "
            "a three-step fixture",
        ),
    )

    def __init__(self, config: CreditAssignmentConfig | None = None):
        from computronium.ontology.credit import CreditAssignmentConfig

        super().__init__(config or CreditAssignmentConfig.unbiased_rtrl())

    def _gradients(  # ruff: ignore[too-many-locals]
        self, hidden: Tensor, x: Tensor, signal: Tensor, recurrent: Tensor
    ) -> dict[str, Tensor]:
        time, batch, width = hidden.shape
        inputs = x.shape[-1]
        states = 1 - hidden**2
        previous = _shift(hidden)
        generator = torch.Generator(device=hidden.device)
        generator.manual_seed(self.config.uoro_seed)
        theta_in = torch.zeros((batch, width), device=hidden.device, dtype=hidden.dtype)
        theta_rec = torch.zeros_like(theta_in)
        rho_in = torch.zeros(
            (batch, width * inputs), device=hidden.device, dtype=hidden.dtype
        )
        rho_rec = torch.zeros(
            (batch, width * width), device=hidden.device, dtype=hidden.dtype
        )
        grad_in = torch.zeros((width, inputs), device=hidden.device, dtype=hidden.dtype)
        grad_rec = torch.zeros((width, width), device=hidden.device, dtype=hidden.dtype)
        for step in range(time):
            row = int(torch.randint(0, width, (1,), generator=generator).item())
            sign = (
                1.0
                if int(torch.randint(0, 2, (1,), generator=generator).item())
                else -1.0
            )
            u = torch.zeros_like(theta_in)
            u[:, row] = states[step][:, row] * width
            theta_in = states[step] * (theta_in @ recurrent.T) + sign * u
            theta_rec = states[step] * (theta_rec @ recurrent.T) + sign * u
            v_in = torch.zeros_like(rho_in)
            v_in[:, row * inputs : (row + 1) * inputs] = x[step]
            v_rec = torch.zeros_like(rho_rec)
            v_rec[:, row * width : (row + 1) * width] = previous[step]
            rho_in += v_in / sign
            rho_rec += v_rec / sign
            grad_in += torch.einsum("bh,bh,bp->p", signal[step], theta_in, rho_in).view(
                width, inputs
            )
            grad_rec += torch.einsum(
                "bh,bh,bp->p", signal[step], theta_rec, rho_rec
            ).view(width, width)
        return {_IN: grad_in, _REC: grad_rec}


class RTRLReference(_TemporalCredit):
    """Exact real-time recurrent learning — the parity reference.

    ``J_t = D_t (W_rec J_{t-1}) + D_t Γ_t`` per parameter, with
    ``Γ^{W_in}_{i,jk} = δ_ij x_k``, ``Γ^{W_rec}_{i,jk} = δ_ij h_{k,t-1}`` and
    ``Γ^b = D_t``; ``ĝ = Σ_t Σ_b L_t J_t``. The exact Jacobian is retained
    for every step, so this rule is a fixture, not an arm.
    """

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="RTRLReference",
        estimator_kind="temporal_local",
        bias_reference="none",
        reference_equations=(
            "real-time recurrent learning (Williams & Zipser 1989); exact "
            "per-step Jacobian of the recurrent cell"
        ),
        deviations_from_literature=(
            "the reference retains every step's Jacobian (O(time·batch·"
            "hidden·params)); it is a fixture, never an arm",
        ),
        objective_function="Σ_t CE(W_out h_t + b_out, y_t)",
        pseudo_gradient_def="J_t = D_t (W_rec J_{t-1} + Γ_t); ĝ = Σ_t Σ_b L_t J_t",
        symmetry_requirements=("none",),
        approximation_parameters=(),
        validated_limits=(
            "cos = 1.0 against the analytical Jacobian of a one-step fixture",
        ),
    )

    def __init__(self, config: CreditAssignmentConfig | None = None):
        from computronium.ontology.credit import CreditAssignmentConfig

        super().__init__(config or CreditAssignmentConfig.rtrl_reference())

    def _gradients(
        self, hidden: Tensor, x: Tensor, signal: Tensor, recurrent: Tensor
    ) -> dict[str, Tensor]:
        time, batch, width = hidden.shape
        inputs = x.shape[-1]
        states = 1 - hidden**2
        previous = _shift(hidden)
        rows = torch.arange(width, device=hidden.device)
        jacobian_in = torch.zeros(
            (batch, width, width * inputs), device=hidden.device, dtype=hidden.dtype
        )
        jacobian_rec = torch.zeros(
            (batch, width, width * width), device=hidden.device, dtype=hidden.dtype
        )
        grad_in = torch.zeros((width, inputs), device=hidden.device, dtype=hidden.dtype)
        grad_rec = torch.zeros((width, width), device=hidden.device, dtype=hidden.dtype)
        for step in range(time):
            input_term = torch.zeros_like(jacobian_in).view(batch, width, width, inputs)
            input_term[:, rows, rows, :] = x[step].unsqueeze(1)
            recurrent_term = torch.zeros_like(jacobian_rec).view(
                batch, width, width, width
            )
            recurrent_term[:, rows, rows, :] = previous[step].unsqueeze(1)
            jacobian_in = states[step][:, :, None] * (
                torch.einsum("ik,bkp->bip", recurrent, jacobian_in)
                + input_term.view(batch, width, -1)
            )
            jacobian_rec = states[step][:, :, None] * (
                torch.einsum("ik,bkp->bip", recurrent, jacobian_rec)
                + recurrent_term.view(batch, width, -1)
            )
            grad_in += torch.einsum("bh,bhp->p", signal[step], jacobian_in).view(
                width, inputs
            )
            grad_rec += torch.einsum("bh,bhp->p", signal[step], jacobian_rec).view(
                width, width
            )
        return {_IN: grad_in, _REC: grad_rec}
