"""Substrate-operator-native settle kernel (EqProp family).

P4 kernel port: the settle family executes its relaxation loop through the
Substrate operator API (forward operator, weight quantization, state noise,
weight update operator) instead of raw nn.Linear / legacy NumPy kernels.

Only the true forward passes (bottom-up and output layer) route through the
substrate's forward operator. The top-down and recurrent passes are
mathematical transpose operations, not physical substrate processes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

import torch
from torch import Tensor

if TYPE_CHECKING:
    from computronium.ontology.geometry import Geometry
    from computronium.ontology.substrate import Substrate


@dataclass(frozen=True, slots=True)
class LayeredParams:
    """Extracted linear layer parameters from a geometry.

    Used by the settle kernel to route forward passes through the
    substrate's forward operator. ``transitions`` is the interleaved
    ``(weight, bias, activation chain)`` schedule (R3.1) — populated only
    when the geometry exposes its raw module stack; assembled block views
    (tile meshes) leave it empty.
    """

    weights: tuple[Tensor, ...]
    biases: tuple[Tensor | None, ...]
    activations: tuple[torch.nn.Module, ...]
    recurrent_weight: Tensor | None
    transitions: tuple[
        tuple[Tensor, Tensor | None, tuple[torch.nn.Module, ...]], ...
    ] = ()
    residual: bool = False


def group_transitions(
    modules: list[torch.nn.Module],
) -> tuple[tuple[Tensor, Tensor | None, tuple[torch.nn.Module, ...]], ...]:
    """Group a module stack into ``(weight, bias, activations)`` transitions.

    Each ``nn.Linear`` opens a transition; consecutive non-Linear modules
    close it as the transition's activation chain. Deep-linear stacks yield
    empty activation chains — error injection still applies (R3.1, moved
    from ePC's private ``_transitions``).
    """
    transitions: list[tuple[Tensor, Tensor | None, tuple[torch.nn.Module, ...]]] = []
    current: tuple[Tensor, Tensor | None, tuple[torch.nn.Module, ...]] | None = None
    for module in modules:
        if isinstance(module, torch.nn.Linear):
            if current is not None:
                transitions.append(current)
            current = (module.weight, module.bias, ())
        elif current is not None:
            current = (current[0], current[1], (*current[2], module))
    if current is not None:
        transitions.append(current)
    return tuple(transitions)


def extract_layered_params(geometry: Geometry) -> LayeredParams | None:
    """Extract linear layer stack from a layered geometry.

    Returns None if the geometry is not layer-structured. TileGeometry
    answers through its assembled block view (R11.1.4).
    """
    layers = getattr(geometry, "_layers", None)
    if isinstance(layers, torch.nn.ModuleList):
        modules = list(layers)
        linears = [m for m in modules if isinstance(m, torch.nn.Linear)]
        activations = [m for m in modules if not isinstance(m, torch.nn.Linear)]
        recurrent = getattr(geometry, "_recurrent_weight", None)

        return LayeredParams(
            weights=tuple(layer.weight for layer in linears),
            biases=tuple(layer.bias for layer in linears),
            activations=tuple(activations),
            recurrent_weight=recurrent if isinstance(recurrent, Tensor) else None,
            transitions=group_transitions(modules),
            residual=bool(getattr(geometry, "residual", False)),
        )
    # Check for layered_params property or callable
    assembler = getattr(geometry, "layered_params", None)
    if isinstance(assembler, LayeredParams):
        return assembler
    if callable(assembler):
        result = assembler()
        if isinstance(result, LayeredParams):
            return result
    return None


IGNORE_INDEX: Final = -100


def _one_hot(target: Tensor, like: Tensor) -> Tensor:
    """Convert class indices to one-hot matching 'like' tensor.

    ``like.shape[:-1]`` is the target's expected index layout (``[B]``,
    ``[B, T]``, ``[N]``); ``like.shape[-1]`` is the class dimension. A
    float target of the same element count is not a class index — it is the
    value itself (a regression target or soft labels), so it only needs the
    shape match.
    """
    if target.shape == like.shape:
        return target
    if target.numel() == like.numel():
        return target.reshape(like.shape)
    if target.dim() == 1:
        out = torch.zeros_like(like)
        out.scatter_(1, target.unsqueeze(1), 1.0)
        return out
    flat = target.reshape(-1)
    out = torch.zeros(
        (flat.numel(), like.shape[-1]), dtype=like.dtype, device=like.device
    )
    out.scatter_(1, flat.unsqueeze(1), 1.0)
    return out.view(*target.shape, like.shape[-1])


def nudged_output(out: Tensor, target: Tensor, beta: float) -> Tensor:
    """β-nudge output activities toward the target.

    Two target kinds share this nudge, separated by *value* semantics, not by
    guessing: an integer target is a class index (one-hot it), a float target
    of the logits' own element count is the value itself (a regression target
    or soft labels — nudge straight toward it).

    Sequence-shaped token targets ``[B, T]`` fold to the logits' rows
    ``[B*T, V]`` before the nudge (R8). Entries carrying the CE
    ignore-index sentinel (``y < 0``) stay free: the task loss ignores
    them, so their activity must not enter the nudge — a raw ``scatter``
    on a negative index would also fail.
    """
    from computronium.ontology._utils import _align_target_rows

    target = _align_target_rows(out, target)
    if target.shape != out.shape and target.numel() == out.numel():
        target = target.reshape(out.shape)
    if target.shape == out.shape:
        return out + beta * (target - out)
    if target.is_floating_point():
        msg = (
            f"float target {tuple(target.shape)} is neither the logits' shape "
            f"{tuple(out.shape)} nor their element count; a regression target "
            "must match the output"
        )
        raise ValueError(msg)
    onehot = _one_hot(target.clamp_min(0), out)
    valid = (target >= 0).unsqueeze(-1).to(out.dtype)
    return out + beta * valid * (onehot - out)


class SubstrateSettleKernel:
    """EqProp settle kernel executing through the Substrate operator API.

    True forward passes (bottom-up, output) route through
    ``Substrate.get_forward_operator()``; weight synchronization quantizes
    through ``Substrate.quantize_weights()``; the contrastive consolidation
    applies ``Substrate.get_weight_update_operator()``.

    Top-down and recurrent passes use raw matmul (mathematical transposes,
    not physical substrate processes).
    """

    def __init__(
        self,
        substrate: Substrate,
        params: LayeredParams,
        step_size: float,
        momentum: float = 0.0,
        residual: bool = False,
    ) -> None:
        self.substrate = substrate
        self._op = substrate.get_forward_operator()
        self._update_op = substrate.get_weight_update_operator()
        self.params = params
        self.step_size = step_size
        self.momentum = momentum
        self.residual = residual

    def _bottom_up(self, x: Tensor, idx: int) -> Tensor:
        """Bottom-up pass: x @ W.T + b (substrate forward operator + bias)."""
        out = self._op(x, self.params.weights[idx])
        b = self.params.biases[idx]
        return out if b is None else out + b

    def _top_down(self, x: Tensor, w: Tensor) -> Tensor:
        """Top-down pass: x @ W (raw matmul, mathematical transpose)."""
        return x @ w

    def _recurrent(self, x: Tensor, w: Tensor) -> Tensor:
        """Recurrent pass: x @ W.T (raw matmul)."""
        return x @ w.T

    def step(
        self,
        all_acts: list[Tensor],
        beta: float,
        target: Tensor | None,
        velocity: list[Tensor] | None,
    ) -> tuple[list[Tensor], list[Tensor] | None]:
        """One relaxation step; mirrors legacy `_settle_step` exactly."""
        p = self.params
        num_hidden = len(all_acts) - 2
        new_acts = [all_acts[0]]
        new_velocity: list[Tensor] | None = (
            [] if self.momentum > 0 and velocity is not None else None
        )

        for i in range(num_hidden):
            pre = self._bottom_up(all_acts[i], i)

            if p.recurrent_weight is not None and i == num_hidden - 1:
                pre += self._recurrent(all_acts[i + 1], p.recurrent_weight)

            top_down = self._top_down(all_acts[i + 2], p.weights[i + 1])

            total = pre + top_down
            if self.residual and i > 0 and all_acts[i].shape == all_acts[i + 1].shape:
                total = total + all_acts[i]

            if new_velocity is not None and velocity is not None:
                total = self.momentum * velocity[i] + total
                new_velocity.append(total.detach().clone())

            target_h = p.activations[i](total) if i < len(p.activations) else total
            h_new = all_acts[i + 1] + self.step_size * (target_h - all_acts[i + 1])

            new_acts.append(h_new)

        out = self._bottom_up(new_acts[-1], len(p.weights) - 1)

        if beta > 0 and target is not None:
            out += beta * (_one_hot(target, out) - out)

        new_acts.append(out)

        return new_acts, new_velocity

    def pseudo_gradient(
        self,
        free_acts: list[Tensor],
        nudged_acts: list[Tensor],
        beta: float,
    ) -> list[Tensor]:
        """Contrastive Hebbian pseudo-gradients: (free - nudged) / (beta * N).

        Matches ThermodynamicContrast.compute_pseudo_gradient math exactly.
        """
        if beta <= 0:
            return []

        batch = free_acts[0].shape[0]
        n_layers = len(free_acts) - 1
        grads = []

        for layer_idx in range(n_layers):
            if layer_idx < len(self.params.weights):
                free_pre = free_acts[layer_idx]
                free_post = free_acts[layer_idx + 1]
                free_corr = free_pre.T @ free_post

                nudged_pre = nudged_acts[layer_idx]
                nudged_post = nudged_acts[layer_idx + 1]
                nudged_corr = nudged_pre.T @ nudged_post

                contrast = (free_corr - nudged_corr) / beta / batch
                grads.append(contrast.T)

        return grads

    def apply_weight_update(self, grads: list[Tensor], lr: float) -> None:
        """Consolidate ΔW through the substrate's physical update operator.

        For each layer: ΔW = update_op(-lr * grad, current_W); W += ΔW
        """
        for g, w in zip(grads, self.params.weights):
            delta = self._update_op(-lr * g, w)
            with torch.no_grad():
                w.add_(delta)

    def effective_weights(self) -> tuple[Tensor, ...]:
        """Return substrate-quantized view of current weights (for inspection)."""
        return tuple(self.substrate.quantize_weights(w) for w in self.params.weights)


def _eqprop_settle_loop(
    acts: list[Tensor],
    weights: tuple[Tensor, ...],
    biases: tuple[Tensor | None, ...],
    activations: tuple[torch.nn.Module, ...],
    step_size: float,
    beta: float,
    target: Tensor | None,
    n_steps: int,
    residual: bool = False,
) -> list[Tensor]:
    """Functional replica of the kernel relaxation loop (digital substrate).

    Mirrors ``SubstrateSettleKernel.step`` exactly for the common case —
    no recurrent weight, no momentum, digital forward operator
    (``op(x, w) == x @ w.T + b``) — including the per-step output nudge
    and the residual skip (``residual``). Compiled whole (one graph per
    settle) by ``_compiled_eqprop_settle``.
    """
    for _ in range(n_steps):
        new_acts: list[Tensor] = [acts[0]]
        num_hidden = len(acts) - 2
        for i in range(num_hidden):
            out = acts[i] @ weights[i].T
            b = biases[i]
            if b is not None:
                out = out + b
            total = out + acts[i + 2] @ weights[i + 1]
            if residual and i > 0 and acts[i].shape == acts[i + 1].shape:
                total = total + acts[i]
            target_h = activations[i](total) if i < len(activations) else total
            new_acts.append(acts[i + 1] + step_size * (target_h - acts[i + 1]))
        out = new_acts[-1] @ weights[len(weights) - 1].T
        b = biases[len(weights) - 1]
        if b is not None:
            out = out + b
        if beta > 0 and target is not None:
            out = out + beta * (_one_hot(target, out) - out)
        new_acts.append(out)
        acts = new_acts
    return acts


# ============================================================
# Chunked compiled settle for energy_minimization with early stopping
# ============================================================


def _eqprop_settle_chunk(
    acts: list[Tensor],
    weights: tuple[Tensor, ...],
    biases: tuple[Tensor | None, ...],
    activations: tuple[torch.nn.Module, ...],
    step_size: float,
    beta: float,
    target: Tensor | None,
    n_steps: int,
    residual: bool = False,
) -> list[Tensor]:
    """Functional replica of the kernel relaxation loop for a fixed chunk of steps.

    Mirrors ``SubstrateSettleKernel.step`` exactly for the common case —
    no recurrent weight, no momentum, digital forward operator
    (``op(x, w) == x @ w.T + b``) — including the per-step output nudge
    and the residual skip (``residual``). Compiled whole (one graph per
    chunk) by ``_compiled_eqprop_settle_chunk``.
    """
    for _ in range(n_steps):
        new_acts: list[Tensor] = [acts[0]]
        num_hidden = len(acts) - 2
        for i in range(num_hidden):
            out = acts[i] @ weights[i].T
            b = biases[i]
            if b is not None:
                out = out + b
            total = out + acts[i + 2] @ weights[i + 1]
            if residual and i > 0 and acts[i].shape == acts[i + 1].shape:
                total = total + acts[i]
            target_h = activations[i](total) if i < len(activations) else total
            new_acts.append(acts[i + 1] + step_size * (target_h - acts[i + 1]))
        out = new_acts[-1] @ weights[len(weights) - 1].T
        b = biases[len(weights) - 1]
        if b is not None:
            out = out + b
        if beta > 0 and target is not None:
            out = out + beta * (_one_hot(target, out) - out)
        new_acts.append(out)
        acts = new_acts
    return acts


_compiled_eqprop_settle_chunk = torch.compile(_eqprop_settle_chunk, dynamic=False)

# Legacy full-horizon compiled settle (kept for parity tests)
_compiled_eqprop_settle = torch.compile(_eqprop_settle_loop, dynamic=False)


# ============================================================
# Substrate-specific compiled settle loops
# ============================================================


def _eqprop_settle_chunk_analog(  # ruff: ignore[too-many-arguments, too-many-positional-arguments, too-many-statements, complex-structure]
    acts: list[Tensor],
    weights: tuple[Tensor, ...],
    biases: tuple[Tensor | None, ...],
    activations: tuple[torch.nn.Module, ...],
    step_size: float,
    beta: float,
    target: Tensor | None,
    n_steps: int,
    noise_level: float,
    weight_bounds: tuple[float, float] | None,
    residual: bool = False,
) -> list[Tensor]:
    """Compiled settle chunk for AnalogSubstrate.

    Inlines the analog forward operator: noise injection + weight clamping + matmul.
    """
    for _ in range(n_steps):
        new_acts: list[Tensor] = [acts[0]]
        num_hidden = len(acts) - 2
        for i in range(num_hidden):
            # Analog forward: noise injection on input
            x = acts[i]
            if noise_level > 0:
                x = x + torch.randn_like(x) * noise_level
            # Weight clamping
            w = weights[i]
            if weight_bounds is not None:
                w = w.clamp(*weight_bounds)
            out = x @ w.T
            b = biases[i]
            if b is not None:
                out = out + b
            # Top-down pass (no noise, no clamping - mathematical transpose)
            total = out + acts[i + 2] @ weights[i + 1]
            if residual and i > 0 and acts[i].shape == acts[i + 1].shape:
                total = total + acts[i]
            target_h = activations[i](total) if i < len(activations) else total
            new_acts.append(acts[i + 1] + step_size * (target_h - acts[i + 1]))
        # Output layer
        x = new_acts[-1]
        if noise_level > 0:
            x = x + torch.randn_like(x) * noise_level
        w = weights[len(weights) - 1]
        if weight_bounds is not None:
            w = w.clamp(*weight_bounds)
        out = x @ w.T
        b = biases[len(weights) - 1]
        if b is not None:
            out = out + b
        if beta > 0 and target is not None:
            out = out + beta * (_one_hot(target, out) - out)
        new_acts.append(out)
        acts = new_acts
    return acts


_compiled_eqprop_settle_chunk_analog = torch.compile(
    _eqprop_settle_chunk_analog, dynamic=False
)


def _eqprop_settle_chunk_simple_noise(  # ruff: ignore[too-many-arguments, too-many-positional-arguments, too-many-statements, complex-structure]
    acts: list[Tensor],
    weights: tuple[Tensor, ...],
    biases: tuple[Tensor | None, ...],
    activations: tuple[torch.nn.Module, ...],
    step_size: float,
    beta: float,
    target: Tensor | None,
    n_steps: int,
    noise_level: float,
    residual: bool = False,
) -> list[Tensor]:
    """Compiled settle chunk for substrates with simple noise injection only.

    Covers: NeuromorphicSubstrate, OpticalSubstrate, SparseSubstrate (no weight clamping).
    """
    for _ in range(n_steps):
        new_acts: list[Tensor] = [acts[0]]
        num_hidden = len(acts) - 2
        for i in range(num_hidden):
            x = acts[i]
            if noise_level > 0:
                x = x + torch.randn_like(x) * noise_level
            out = x @ weights[i].T
            b = biases[i]
            if b is not None:
                out = out + b
            total = out + acts[i + 2] @ weights[i + 1]
            if residual and i > 0 and acts[i].shape == acts[i + 1].shape:
                total = total + acts[i]
            target_h = activations[i](total) if i < len(activations) else total
            new_acts.append(acts[i + 1] + step_size * (target_h - acts[i + 1]))
        x = new_acts[-1]
        if noise_level > 0:
            x = x + torch.randn_like(x) * noise_level
        out = x @ weights[len(weights) - 1].T
        b = biases[len(weights) - 1]
        if b is not None:
            out = out + b
        if beta > 0 and target is not None:
            out = out + beta * (_one_hot(target, out) - out)
        new_acts.append(out)
        acts = new_acts
    return acts


_compiled_eqprop_settle_chunk_simple_noise = torch.compile(
    _eqprop_settle_chunk_simple_noise, dynamic=False
)


# ============================================================
# Substrate-specific compiled settle loops for PredictiveSettlingDynamics
# ============================================================


def _layered_settle_loop_digital(
    acts: list[Tensor],
    weights: tuple[Tensor, ...],
    step_size: float,
    n_steps: int,
) -> list[Tensor]:
    """Digital substrate predictive settling: raw matmul (x @ w.T)."""
    for _ in range(n_steps):
        new_acts: list[Tensor] = [acts[0]]
        for i, w in enumerate(weights):
            h_upper = acts[i + 1]
            error = acts[i] - h_upper @ w
            new_acts.append(h_upper + step_size * (error @ w.T))
        acts = new_acts
    return acts


_compiled_layered_settle_digital = torch.compile(
    _layered_settle_loop_digital, dynamic=False
)


def _layered_settle_loop_analog(
    acts: list[Tensor],
    weights: tuple[Tensor, ...],
    step_size: float,
    n_steps: int,
    noise_level: float,
    weight_bounds: tuple[float, float] | None,
) -> list[Tensor]:
    """Analog substrate predictive settling: noise injection + weight clamping."""
    for _ in range(n_steps):
        new_acts: list[Tensor] = [acts[0]]
        for i, w in enumerate(weights):
            h_upper = acts[i + 1]
            # Analog forward: noise injection on input
            x = acts[i]
            if noise_level > 0:
                x = x + torch.randn_like(x) * noise_level
            # Weight clamping
            w_eff = w
            if weight_bounds is not None:
                w_eff = w_eff.clamp(*weight_bounds)
            error = x - h_upper @ w_eff
            # Top-down: mathematical transpose (no noise, no clamping)
            new_acts.append(h_upper + step_size * (error @ w_eff.T))
        acts = new_acts
    return acts


_compiled_layered_settle_analog = torch.compile(
    _layered_settle_loop_analog, dynamic=False
)


def _layered_settle_loop_simple_noise(
    acts: list[Tensor],
    weights: tuple[Tensor, ...],
    step_size: float,
    n_steps: int,
    noise_level: float,
) -> list[Tensor]:
    """Substrates with simple noise injection only: Neuromorphic, Optical, Sparse."""
    for _ in range(n_steps):
        new_acts: list[Tensor] = [acts[0]]
        for i, w in enumerate(weights):
            h_upper = acts[i + 1]
            x = acts[i]
            if noise_level > 0:
                x = x + torch.randn_like(x) * noise_level
            error = x - h_upper @ w
            new_acts.append(h_upper + step_size * (error @ w.T))
        acts = new_acts
    return acts


_compiled_layered_settle_simple_noise = torch.compile(
    _layered_settle_loop_simple_noise, dynamic=False
)


def _layered_settle_loop_memristive(
    acts: list[Tensor],
    weights: tuple[Tensor, ...],
    step_size: float,
    n_steps: int,
    noise_level: float,
    weight_bounds: tuple[float, float] | None,
) -> list[Tensor]:
    """Memristive substrate predictive settling: differential conductance pair + noise."""
    for _ in range(n_steps):
        new_acts: list[Tensor] = [acts[0]]
        for i, w in enumerate(weights):
            h_upper = acts[i + 1]
            x = acts[i]
            if noise_level > 0:
                x = x + torch.randn_like(x) * noise_level
            # Memristive: differential pair (g+, g-) with quantization
            if weight_bounds is not None:
                w = w.clamp(*weight_bounds)
            g_plus = w.clamp(min=0)
            g_minus = (-w).clamp(min=0)
            w_eff = g_plus - g_minus
            error = x - h_upper @ w_eff
            # Top-down uses effective weight transpose
            new_acts.append(h_upper + step_size * (error @ w_eff.T))
        acts = new_acts
    return acts


_compiled_layered_settle_memristive = torch.compile(
    _layered_settle_loop_memristive, dynamic=False
)


def _layered_settle_loop_ternary(
    acts: list[Tensor],
    weights: tuple[Tensor, ...],
    step_size: float,
    n_steps: int,
    weight_bits: int = 2,
) -> list[Tensor]:
    """Ternary substrate predictive settling: TWN-style weight quantization."""
    threshold = 0.7  # TWN ternary threshold factor
    for _ in range(n_steps):
        new_acts: list[Tensor] = [acts[0]]
        for i, w in enumerate(weights):
            h_upper = acts[i + 1]
            # TWN ternary quantization: w_q = sign(w) * E[|w|] * threshold
            scale = w.abs().mean() * threshold
            w_q = torch.sign(w) * scale
            error = acts[i] - h_upper @ w_q
            new_acts.append(h_upper + step_size * (error @ w_q.T))
        acts = new_acts
    return acts


_compiled_layered_settle_ternary = torch.compile(
    _layered_settle_loop_ternary, dynamic=False
)


def _layered_settle_loop_complex(
    acts: list[Tensor],
    weights: tuple[Tensor, ...],
    step_size: float,
    n_steps: int,
) -> list[Tensor]:
    """Complex substrate predictive settling: complex-valued matmul."""
    for _ in range(n_steps):
        new_acts: list[Tensor] = [acts[0]]
        for i, w in enumerate(weights):
            h_upper = acts[i + 1]
            # Complex forward: conjugate transpose for top-down
            error = acts[i] - h_upper @ w
            new_acts.append(h_upper + step_size * (error @ w.conj().T))
        acts = new_acts
    return acts


_compiled_layered_settle_complex = torch.compile(
    _layered_settle_loop_complex, dynamic=False
)


def _layered_settle_loop_quantum(
    acts: list[Tensor],
    weights: tuple[Tensor, ...],
    step_size: float,
    n_steps: int,
    noise_level: float = 0.0,
) -> list[Tensor]:
    """Quantum substrate predictive settling: amplitude encoding with shot noise."""
    for _ in range(n_steps):
        new_acts: list[Tensor] = [acts[0]]
        for i, w in enumerate(weights):
            h_upper = acts[i + 1]
            x = acts[i]
            # Quantum: shot noise on measurement
            if noise_level > 0:
                x = x + torch.randn_like(x) * noise_level
            error = x - h_upper @ w
            new_acts.append(h_upper + step_size * (error @ w.conj().T))
        acts = new_acts
    return acts


_compiled_layered_settle_quantum = torch.compile(
    _layered_settle_loop_quantum, dynamic=False
)
