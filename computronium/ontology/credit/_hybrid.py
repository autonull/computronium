"""Hybrid credit: lockstep-local trunk with an exact-gradient head (TODO93 T3b).

The hybrid is the composition the memory frontier's lead arm needs. The trunk
is a two-pass local rule whose working set is one layer's two chains; the head
is a 2-layer backprop segment whose autograd graph is the only stored
activation set. ``System.credit`` stays one protocol object, so no schema
changed: the wrapper dispatches by layer index.

**The four-step semantics (fixed before the code).**

1. **Standard pass.** The trunk runs under ``torch.no_grad()``; at the boundary
   ``h = h.detach().requires_grad_(True)``; the head forward records the graph
   through to the logits and the task loss.
2. **Head backward.** ``autograd.grad`` on the standard pass gives the head's
   true gradients and the boundary error ``δ = ∂L/∂h``.
3. **Trunk error-modulated pass.** Under ``torch.no_grad()`` with
   ``e_out = δ``: ``x̃ = x + γ·δBᵀ`` with one fixed random
   ``B`` (boundary × input), and the trunk's standard and modulated chains
   advance layer by layer, forming each layer's contrast before the next layer
   is produced (the T3 lockstep rung).
4. **Same pre-update weights.** Trunk and head gradients are formed before
   any weight moves; the pipeline applies them in one update.

The ``no_grad`` trunk and the ``detach`` boundary are what make the memory
claim true: without them the trunk graph is retained and the hybrid is just
backprop. The trunk's working set is O(B·W) per layer; the head's activation
set is O(head·B·W), bounded by its 2 layers.

The **store-all hybrid** (two-pass PEPITA trunk + backprop head, no lockstep)
is the reference fixture; the lockstep trunk is checked against it at
``atol=0`` in ``tests/property/test_hybrid_parity.py``. "Composes" is not
acceptance; parity is.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

import torch
from torch import Tensor, nn

from computronium.core.identity_card import AlgorithmIdentityCard
from computronium.core.losses import cross_entropy, mean_squared_error
from computronium.ontology._utils import _learnable_weight_names, output_target
from computronium.ontology.credit._base import Phase

if TYPE_CHECKING:
    from collections.abc import Mapping

    from computronium.ontology.credit import CreditAssignmentConfig, GradientCredit
    from computronium.ontology.dynamics._state import SettableState
    from computronium.ontology.geometry import FeedforwardGeometry, Geometry
    from computronium.ontology.substrate import Substrate


@runtime_checkable
class TrunkContrast(Protocol):
    """The trunk half's local rule: one layer's two pass pairs -> update direction."""

    def contrast(
        self,
        pre_standard: Tensor,
        post_standard: Tensor,
        pre_modulated: Tensor,
        post_modulated: Tensor,
    ) -> tuple[Tensor, Tensor]:
        """Return ``(weight gradient, bias gradient)`` for one Linear layer."""
        ...


class PepitaTrunk:
    """PEPITA's trunk contrast: the modulated correlation minus the standard.

    The update rule subtracts the returned gradient, so
    ``W -= lr·(mod − std)`` is the PEPITA store-all schedule's direction
    (``tests/property/test_hybrid_parity.py`` writes the reference from
    the equations).
    """

    def contrast(
        self,
        pre_standard: Tensor,
        post_standard: Tensor,
        pre_modulated: Tensor,
        post_modulated: Tensor,
    ) -> tuple[Tensor, Tensor]:
        batch = post_standard.shape[0]
        weight = (
            post_modulated.T @ pre_modulated - post_standard.T @ pre_standard
        ) / batch
        bias = post_modulated.mean(dim=0) - post_standard.mean(dim=0)
        return weight, bias


class HybridCredit:
    """Lockstep-local trunk + exact-gradient head, dispatched by layer index.

    ``trunk_credit`` supplies the local contrast (the PEPITA trunk by
    default); ``head_credit`` supplies the exact autograd path
    (``GradientCredit``/``BackpropCredit``). ``split_layer`` is an index into
    the geometry's layer stack and must land on a Linear: the head's first
    layer reads the detached boundary, and a residual activation after that
    Linear would have lost its skip input if the split landed between them.
    ``-1`` places the head on the last two Linears (the readout and the last
    hidden layer), clamped so the trunk keeps at least one Linear.
    """

    phases: tuple[Phase, ...] = (Phase.FREE,)
    error_blind: bool = False
    requires_autograd: bool = False

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="HybridCredit",
        estimator_kind="hybrid",
        bias_reference="none",
        reference_equations=(
            "PEPITA trunk (Dellaferrera & Kreiman 2022, arXiv 2201.11665) and "
            "backpropagation head (Rumelhart, Hinton & Williams 1986)"
        ),
        deviations_from_literature=(
            "the trunk's error is the head's input gradient δ = ∂L/∂h, not "
            "the output-layer target error",
            "trunk and head gradients are formed from the same pre-update "
            "weights and applied in one update",
            "trunk is lockstep (one layer's two chains live); memory, not math",
        ),
        objective_function=(
            "head task loss on the standard pass plus the trunk's local "
            "contrastive objective; no single global objective"
        ),
        pseudo_gradient_def=(
            "head: exact autograd ∂L/∂W_head; trunk: "
            "(mod_postᵀ mod_pre − std_postᵀ std_pre)/B per layer"
        ),
        symmetry_requirements=("fixed random trunk B (boundary × input)",),
        approximation_parameters=(
            "feedback_scale γ",
            "split_layer",
            "feedback_matrix",
        ),
        validated_limits=(
            "lockstep trunk ≡ store-all hybrid at atol=0 on a seeded fixture",
            "trunk activation set flat in depth (measured, TODO93 §4)",
        ),
    )

    def __init__(
        self,
        config: CreditAssignmentConfig | None = None,
        *,
        trunk_credit: TrunkContrast | None = None,
        head_credit: GradientCredit | None = None,
        split_layer: int | None = None,
    ) -> None:
        from computronium.ontology.credit import BackpropCredit, CreditAssignmentConfig

        self.config = config or CreditAssignmentConfig.hybrid()
        self.trunk_credit = trunk_credit or PepitaTrunk()
        self.head_credit = head_credit or BackpropCredit()
        self.split_layer = (
            self.config.split_layer if split_layer is None else split_layer
        )
        self._substrate: Substrate | None = None
        self._trunk_feedback: Tensor | None = None
        self._bias_cache: dict[str, Tensor] | None = None

    def set_substrate(self, substrate: Substrate) -> None:
        """Register the system's substrate (wired by ``compose_system``)."""
        self._substrate = substrate

    def _resolved_substrate(self) -> Substrate:
        """The wired substrate, or the documented digital default when unset."""
        if self._substrate is None:
            from computronium.ontology.substrate import DigitalSubstrate

            self._substrate = DigitalSubstrate()
        return self._substrate

    def _stack(self, geometry: Geometry) -> FeedforwardGeometry:
        """Narrow the protocol to the dense stack this credit dispatches over."""
        from computronium.ontology.geometry import FeedforwardGeometry

        if not isinstance(geometry, FeedforwardGeometry):
            raise TypeError(
                "HybridCredit requires a FeedforwardGeometry layer stack; "
                f"got {type(geometry).__name__}"
            )
        return geometry

    def _split(
        self, geometry: FeedforwardGeometry
    ) -> tuple[list[nn.Module], list[nn.Module], int]:
        """Trunk layers, head layers, and the split index into the stack."""
        layers = list(geometry._layers)
        starts = [i for i, layer in enumerate(layers) if isinstance(layer, nn.Linear)]
        if len(starts) < 2:
            raise RuntimeError(
                "HybridCredit needs at least a trunk Linear and a head Linear; "
                f"got {len(starts)} Linear layer(s)"
            )
        if self.split_layer >= 0:
            split = self.split_layer
        else:
            # Head on the last two Linears; a 2-Linear case keeps the
            # readout as the head so the trunk still has a layer.
            split = starts[-1] if len(starts) <= 2 else starts[-2]
        if not 0 < split < len(layers) or not isinstance(layers[split], nn.Linear):
            raise RuntimeError(
                "HybridCredit: split_layer must index a Linear that starts "
                f"the head (so a residual skip is not split); got {split!r} "
                f"with Linears at {starts}"
            )
        return layers[:split], layers[split:], split

    def free_activations(
        self, substrate: Substrate, geometry: Geometry, x: Tensor
    ) -> Tensor:
        """The credit's own free pass: the logits, never the stored stack.

        The head recomputes its layers from ``x`` at its recorded boundary and
        the trunk's contrast is lockstep, so a store-all activation set is a
        tensor the rule never reads (TODO93 T6b). One readout activation is
        the whole free-phase set, so the composed path is flat in depth.
        """
        stack = self._stack(geometry)
        with torch.no_grad():
            return stack.forward(x, substrate)

    def _feedback_matrix(self, delta: Tensor, x: Tensor) -> Tensor:
        """The fixed random trunk B (boundary × input), drawn lazily once."""
        shape = (delta.shape[1], x.shape[1])
        configured = self.config.feedback_matrix
        if configured is not None:
            if tuple(configured.shape) != shape:
                raise ValueError(
                    "HybridCredit: feedback_matrix shape "
                    f"{tuple(configured.shape)} does not match (boundary "
                    f"{shape[0]}, input {shape[1]})"
                )
            return configured
        if self._trunk_feedback is None or tuple(self._trunk_feedback.shape) != shape:
            self._trunk_feedback = torch.randn(*shape, device=x.device, dtype=x.dtype)
        return self._trunk_feedback

    def _head_loss(self, y: Tensor, logits: Tensor) -> Tensor:
        """The head's committed loss: CE for a class index, MSE otherwise."""
        target = output_target(y, logits)
        if target.shape == logits.shape and y.is_floating_point():
            return mean_squared_error(logits, target)
        return cross_entropy(logits, y)

    def _head_bias_names(self, geometry: FeedforwardGeometry, split: int) -> list[str]:
        """Head bias parameter names, in the geometry's declaration order."""
        params = geometry.params
        return sorted(
            (
                name
                for name, tensor in params.items()
                if name.endswith(".bias")
                and tensor.ndim == 1
                and _stack_index(name) >= split
            ),
            key=_stack_index,
        )

    def _trunk_contrasts(
        self,
        geometry: FeedforwardGeometry,
        trunk_layers: list[nn.Module],
        x: Tensor,
        modulated: Tensor,
        op,
    ) -> tuple[dict[str, Tensor], dict[str, Tensor]]:
        """Advance both chains layer by layer, one contrast per Linear.

        A Linear's contrast pairs its input with the output of the activation
        that follows it (the T3 lockstep convention); a Linear with no
        following activation uses its own output. ``pending`` carries that
        Linear across an activation so a residual geometry does not add the
        wrong skip tensor.
        """
        weights: dict[str, Tensor] = {}
        biases: dict[str, Tensor] = {}
        h_std, h_mod = x, modulated
        h_in_std, h_in_mod = x, modulated
        pending: tuple[int, Tensor, Tensor] | None = None

        def flush(
            unit: tuple[int, Tensor, Tensor], post_std: Tensor, post_mod: Tensor
        ) -> None:
            index, pre_std, pre_mod = unit
            weight, bias = self.trunk_credit.contrast(
                pre_std, post_std, pre_mod, post_mod
            )
            weights[f"{index}.weight"] = _clip(weight, self.config.grad_clip)
            if self.config.train_biases:
                biases[f"{index}.bias"] = _clip(bias, self.config.grad_clip)

        # No graph may survive the second pass: an un-wrapped contrast keeps
        # the activation chain alive through its grad_fn and the peak grows
        # with depth (the measured 101→577 MB negative control).
        with torch.no_grad():
            for index, layer in enumerate(trunk_layers):
                pre_std, pre_mod = h_std, h_mod
                h_std, h_in_std = geometry.step_layer(h_std, layer, h_in_std, op)
                h_mod, h_in_mod = geometry.step_layer(h_mod, layer, h_in_mod, op)
                if isinstance(layer, nn.Linear):
                    if pending is not None:
                        # Consecutive Linears: the first has no activation
                        # after it, so its post is the second's input.
                        flush(pending, pre_std, pre_mod)
                    pending = (index, pre_std, pre_mod)
                elif pending is not None:
                    flush(pending, h_std, h_mod)
                    pending = None
            if pending is not None:
                flush(pending, h_std, h_mod)
        return weights, biases

    def _head_pass(
        self,
        geometry: FeedforwardGeometry,
        x: Tensor,
        y: Tensor,
        parts: tuple[list[nn.Module], list[nn.Module], int],
    ) -> tuple[dict[str, Tensor], dict[str, Tensor], Tensor]:
        """Steps 1-2: the no-grad trunk, the recorded head, and δ."""
        trunk_layers, head_layers, split = parts
        op = self._resolved_substrate().get_forward_operator()
        with torch.no_grad():
            boundary = geometry._apply_layers(x, tuple(trunk_layers), op)
        boundary = boundary.detach().requires_grad_(True)
        logits = geometry._apply_layers(boundary, tuple(head_layers), op)
        head_loss = self._head_loss(y, logits)
        weight_names = _learnable_weight_names(geometry.params)
        head_names = [n for n in weight_names if _stack_index(n) >= split]
        head_params = [geometry.params[n] for n in head_names]
        head_biases = (
            self._head_bias_names(geometry, split) if self.config.train_biases else []
        )
        targets = [boundary, *head_params, *[geometry.params[n] for n in head_biases]]
        grads = self.head_credit.gradient_of(head_loss, targets)
        return (
            dict(zip(head_names, grads[1 : 1 + len(head_params)])),
            dict(zip(head_biases, grads[1 + len(head_params) :])),
            grads[0],
        )

    def _trunk_pass(
        self,
        geometry: FeedforwardGeometry,
        parts: tuple[list[nn.Module], list[nn.Module], int],
        x: Tensor,
        delta: Tensor,
    ) -> tuple[dict[str, Tensor], dict[str, Tensor]]:
        """Step 3: modulate the input and form every trunk contrast lockstep."""
        trunk_layers = parts[0]
        op = self._resolved_substrate().get_forward_operator()
        with torch.no_grad():
            modulated = x + self.config.feedback_scale * (
                delta @ self._feedback_matrix(delta, x)
            )
        return self._trunk_contrasts(geometry, trunk_layers, x, modulated, op)

    def compute_pseudo_gradient(
        self,
        states: Mapping[Phase, SettableState],
        loss: Tensor | None,
        geometry: Geometry,
    ) -> list[Tensor]:
        """The four-step hybrid pass; returns one gradient per weight, in order."""
        free = states.get(Phase.FREE)
        if free is None or free.x is None or free.y is None:
            return []
        stack = self._stack(geometry)
        parts = self._split(stack)
        head_grads, head_bias_grads, delta = self._head_pass(
            stack, free.x, free.y, parts
        )
        trunk_grads, trunk_bias_grads = self._trunk_pass(stack, parts, free.x, delta)
        weight_names = _learnable_weight_names(stack.params)
        self._bias_cache = (
            {**trunk_bias_grads, **head_bias_grads}
            if self.config.train_biases
            else None
        )
        by_name = {**trunk_grads, **head_grads}
        missing = [name for name in weight_names if name not in by_name]
        if missing:
            raise RuntimeError(
                f"HybridCredit: no gradient reached {missing} "
                "(the split must cover every stack weight)"
            )
        return [by_name[name] for name in weight_names]

    def compute_bias_pseudo_gradients(
        self,
        states: Mapping[Phase, SettableState],
        loss: Tensor | None,
        geometry: Geometry,
    ) -> dict[str, Tensor]:
        """Bias gradients from the weight pass's pre-update cache.

        The cache is filled by ``compute_pseudo_gradient`` before the update
        rule runs, so both halves read the same pre-update weights. The
        pipeline calls the two in that order; an empty cache means the caller
        skipped the weight pass, and a silent zero-fill would hide it.
        """
        if not self.config.train_biases:
            return {}
        if self._bias_cache is None:
            raise RuntimeError(
                "HybridCredit: bias gradients requested before the weight "
                "pass; the cache holds the same pre-update weights."
            )
        return self._bias_cache


def _stack_index(name: str) -> int:
    """The layer-stack index a parameter name encodes (``3.weight`` -> 3)."""
    prefix, _, role = name.rpartition(".")
    if role not in {"weight", "bias"}:
        raise RuntimeError(f"HybridCredit: {name!r} is not a stack weight or bias")
    try:
        return int(prefix)
    except ValueError as exc:
        raise RuntimeError(
            f"HybridCredit: {name!r} does not name a stack layer"
        ) from exc


def _clip(grad: Tensor, limit: float | None) -> Tensor:
    """Per-parameter clip on a trunk contrast (the head stays exact)."""
    if limit is None or limit <= 0:
        return grad
    norm = grad.norm()
    if norm > limit:
        return grad * (limit / (norm + 1e-8))
    return grad
