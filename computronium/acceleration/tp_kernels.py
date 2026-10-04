"""Target Propagation Kernel Backend.

Inverse network forward + target propagation kernels.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch
from torch import Tensor

from computronium.acceleration.contrastive_primitives import (
    batched_outer_product,
)
from computronium.acceleration.kernel_backend import (
    AlgorithmFamily,
    HardwareTarget,
    KernelConfig,
    LinearView,
    LocalityLevel,
    linear_views,
)

if TYPE_CHECKING:
    from computronium.ontology import System


def _transposed_inverse(layers: list[LinearView]) -> list[torch.nn.Linear]:
    """The inverse network: each forward layer transposed, in reverse order.

    A copy, deliberately. Target propagation updates the forward network *and* the
    inverse network by different learning rates, and sharing storage would make
    the two updates land on the same tensor.
    """
    inverse = []
    for layer in reversed(layers):
        mirror = torch.nn.Linear(layer.out_features, layer.in_features, bias=False)
        with torch.no_grad():
            mirror.weight.copy_(layer.weight.T)
        inverse.append(mirror)
    return inverse


class TPKernelBackend:
    """Target Propagation kernel backend with transpose feedback.

    Implements Target Propagation with transpose feedback (TargetInversionCredit):
    - Predictive settling dynamics for free/nudged phases
    - Transpose feedback target propagation: t_l = t_{l+1} @ W_l
    - Pseudo-gradients: (post - target).T @ pre / batch
    - Euclidean (SGD) weight updates

    Matches the reference pipeline: PredictiveSettlingDynamics + TargetInversionCredit + EuclideanUpdate
    """

    name = AlgorithmFamily.TP
    supported_dtypes = (torch.float32, torch.float16, torch.bfloat16)
    supports_autograd = False
    requires_settle = True
    memory_complexity = "O(1)"
    locality_level = LocalityLevel.LAYERWISE

    def __init__(self) -> None:
        self._config: KernelConfig | None = None
        self._forward_layers: list[torch.nn.Linear] = []
        self._lr: float = 1e-3
        self._device: torch.device = torch.device("cpu")
        self._dtype: torch.dtype = torch.float32
        self._activation: torch.nn.Module = torch.nn.Tanh()
        self._beta: float = 0.1
        self._max_steps: int = 10
        self._step_size: float = 0.1
        self._convergence_threshold: float = 1e-4
        self._convergence_start: int = 5

    def initialize(self, config: KernelConfig) -> None:
        """Initialize backend with configuration."""
        self._config = config
        self._device = torch.device(
            "cuda"
            if config.hardware in (HardwareTarget.CUDA, HardwareTarget.TRITON)  # ruff: ignore[literal-membership]
            else "cpu"
        )
        self._dtype = config.dtype

        extra = config.extra
        self._lr = extra.get("lr", 1e-3)
        self._activation = _get_activation(extra.get("activation", "tanh"))
        self._beta = extra.get("beta", 0.1)
        self._max_steps = extra.get("max_steps", 10)
        self._step_size = extra.get("step_size", 0.1)
        self._convergence_threshold = extra.get("convergence_threshold", 1e-4)
        self._convergence_start = extra.get("convergence_start", 5)

    def set_model_ref(
        self,
        forward_layers: list[torch.nn.Linear],
        activation: torch.nn.Module | None = None,
    ) -> None:
        """Set reference to forward network layers."""
        self._forward_layers = forward_layers
        if activation is not None:
            self._activation = activation

    def bind_system(self, system: System) -> None:
        """Bind the kernel to a System's geometry."""
        layers = self._extract_layers(system.geometry)
        if layers:
            self.set_model_ref(layers)

    def _extract_layers(self, geometry) -> list[LinearView]:
        return linear_views(geometry)

    def _settle_layered(
        self,
        x: Tensor,
        target: Tensor | None = None,
        beta: float = 0.5,
        max_steps: int = 10,
        step_size: float = 0.1,
        convergence_threshold: float = 1e-4,
        convergence_start: int = 5,
    ) -> list[Tensor]:
        """Layer-wise predictive coding settle over the forward network layers.

        Each layer minimizes its prediction error against the layer below.
        The input layer is clamped to x; each subsequent layer predicts the
        previous layer's activity. Returns activations for all layers.

        This matches PredictiveSettlingDynamics._eager_layered_steps exactly:
        - Initial activations from feedforward pass (post-activation)
        - Settling loop: top-down prediction (no bias), bottom-up error correction (no bias)
        - No activation during settling (operates in post-activation space)
        - Runs ALL max_steps iterations (no early stopping, matching reference)
        - Nudge applied after settling loop

        Args:
            x: Input tensor [B, D_in]
            target: Optional target for nudged phase (one-hot labels)
            beta: Nudge strength for output layer
            max_steps: Maximum settling iterations (all steps executed)
            step_size: Learning rate for state updates
            convergence_threshold: Unused (kept for API compatibility)
            convergence_start: Unused (kept for API compatibility)

        Returns:
            List of activations [x, h1, h2, ..., output] after settling
        """
        # Initialize layer states from a feedforward pass (post-activation)
        acts: list[Tensor] = [x]
        h = x
        for i, layer in enumerate(self._forward_layers):
            h = layer(h)
            if i < len(self._forward_layers) - 1:
                h = self._activation(h)
            acts.append(h)

        # Run ALL max_steps iterations (matching PredictiveSettlingDynamics._eager_layered_steps)
        for step in range(max_steps):
            new_acts = [acts[0]]  # Input layer is clamped

            for i, layer in enumerate(self._forward_layers):
                weight = layer.weight

                # acts[i] is the lower layer activity (input to this layer)
                # weight maps from acts[i] to acts[i+1]: post = pre @ weight.T
                # Top-down prediction: h_upper @ weight (since forward op is x @ w.T)
                # h_upper [batch, out] @ weight [out, in] = [batch, in] -> predicts lower layer
                h_upper = acts[i + 1]
                prediction = h_upper @ weight
                error = acts[i] - prediction
                # Bottom-up correction: error @ weight.T
                # error [batch, in] @ weight.T [in, out] = [batch, out] -> corrects upper layer
                h_upper_new = h_upper + step_size * (error @ weight.T)

                new_acts.append(h_upper_new)

            acts = new_acts

        # Apply nudge to output layer if target provided (after settling)
        if target is not None:
            if target.dim() == 1:
                target_one_hot = (
                    torch.nn.functional.one_hot(target, num_classes=acts[-1].shape[1])
                    .float()
                    .to(device=acts[-1].device, dtype=acts[-1].dtype)
                )
            else:
                target_one_hot = target.to(device=acts[-1].device, dtype=acts[-1].dtype)
            acts[-1] = acts[-1] + beta * (target_one_hot - acts[-1])

        return acts

    def train_step(self, x: Tensor, y: Tensor) -> dict[str, float]:
        """Execute one training step using Target Propagation with transpose feedback.

        Matches the reference pipeline: PredictiveSettlingDynamics + TargetInversionCredit + EuclideanUpdate
        """
        # Move inputs to device
        x = x.to(device=self._device, dtype=self._dtype)
        if x.dim() > 2:
            x = x.view(x.size(0), -1)
        y = y.to(device=self._device)

        # Get config values
        beta = self._beta
        max_steps = self._max_steps
        step_size = self._step_size
        convergence_threshold = self._convergence_threshold
        convergence_start = self._convergence_start
        lr = self._lr

        # Phase 1: FREE phase (no target) - settling
        free_activations = self._settle_layered(
            x,
            target=None,
            beta=beta,
            max_steps=max_steps,
            step_size=step_size,
            convergence_threshold=convergence_threshold,
            convergence_start=convergence_start,
        )
        free_output = free_activations[-1]

        # Phase 2: NUDGED phase (with target) - settling with beta nudge
        nudged_activations = self._settle_layered(
            x,
            target=y,
            beta=beta,
            max_steps=max_steps,
            step_size=step_size,
            convergence_threshold=convergence_threshold,
            convergence_start=convergence_start,
        )
        nudged_output = nudged_activations[-1]

        # Compute transpose feedback targets from nudged activations
        targets = self._propagate_targets_transpose(nudged_activations, y)

        # Compute pseudo-gradients (transpose feedback TP)
        pseudo_grads = self._compute_pseudo_gradients(nudged_activations, targets)

        # Apply Euclidean (SGD) updates
        self._apply_updates(pseudo_grads, lr)

        # Post-update: FREE phase for honest metrics
        post_activations = self._settle_layered(
            x,
            target=None,
            beta=beta,
            max_steps=max_steps,
            step_size=step_size,
            convergence_threshold=convergence_threshold,
            convergence_start=convergence_start,
        )
        post_output = post_activations[-1]

        with torch.no_grad():
            # Nudged phase metrics (target-conditioned)
            nudged_loss = torch.nn.functional.cross_entropy(nudged_output, y).item()
            nudged_acc = (nudged_output.argmax(-1) == y).float().mean().item()

            # Post-update free phase metrics
            free_loss = torch.nn.functional.cross_entropy(post_output, y).item()
            free_acc = (post_output.argmax(-1) == y).float().mean().item()

            # Energy computation: sum of squared output activations (matching PredictiveSettlingDynamics.compute_energy)
            energy = nudged_output.pow(2).sum().item()
            free_energy = post_output.pow(2).sum().item()

        return {
            "loss": nudged_loss,
            "energy": energy,
            "nudged_fit_accuracy": nudged_acc,
            "free_loss": free_loss,
            "free_energy": free_energy,
            "free_accuracy": free_acc,
        }

    def _propagate_targets_transpose(
        self,
        activations: list[Tensor],
        y: Tensor,
    ) -> list[Tensor]:
        """Transpose-feedback target propagation: t_L = one-hot(y), t_l = t_{l+1} @ W_l.

        Matches TargetInversionCredit._propagate_targets exactly.

        Args:
            activations: [x, h1, h2, ..., output] from nudged phase
            y: Target labels [batch]

        Returns:
            List of targets [t_0, t_1, ..., t_L] where t_L = one-hot(y)
            and t_l is target for activation l (same shape as activations[l])
        """
        out_dim = activations[-1].shape[-1]
        targets: list[Tensor | None] = [None] * len(activations)
        targets[-1] = torch.nn.functional.one_hot(y, num_classes=out_dim).float().to(
            device=activations[-1].device, dtype=activations[-1].dtype
        )

        # Get weight names in order (layer_0_weight, layer_1_weight, ...)
        # The forward_layers list is already in order
        for l in range(len(self._forward_layers) - 1, -1, -1):
            nxt = targets[l + 1]
            if nxt is None:
                break
            w = self._forward_layers[l].weight  # shape [out, in]
            if nxt.shape[-1] != w.shape[0]:
                # Shape mismatch - stop propagating
                break
            # t_l = t_{l+1} @ W_l (W_l has shape [out, in], so this gives [batch, in])
            targets[l] = nxt @ w

        # Filter out None values (shouldn't happen for well-formed networks)
        return [t for t in targets if t is not None]  # type: ignore[return-value]

    def _compute_pseudo_gradients(
        self,
        activations: list[Tensor],
        targets: list[Tensor],
    ) -> list[Tensor]:
        """Compute pseudo-gradients: (post - target).T @ pre / batch.

        Matches TargetInversionCredit pseudo-gradient computation.

        Args:
            activations: [x, h1, h2, ..., output] from nudged phase
            targets: [t_0, t_1, ..., t_L] from _propagate_targets_transpose

        Returns:
            List of pseudo-gradients [grad_0, grad_1, ..., grad_{L-1}] for each weight
        """
        n_trans = len(activations) - 1  # number of weight matrices
        pseudo_grads: list[Tensor] = []

        for i in range(n_trans):
            pre = activations[i]      # [batch, in]
            post = activations[i + 1]  # [batch, out]
            tgt = targets[i + 1]       # [batch, out] - target for this layer's output

            if tgt is None:
                # No target for this layer - zero gradient
                pseudo_grads.append(
                    torch.zeros_like(self._forward_layers[i].weight)
                )
                continue

            # delta = post - tgt [batch, out]
            delta = post - tgt
            # pseudo_grad = delta.T @ pre / batch [out, in]
            batch_size = pre.shape[0]
            grad = (delta.T @ pre) / batch_size
            pseudo_grads.append(grad)

        return pseudo_grads

    def _apply_updates(self, pseudo_grads: list[Tensor], lr: float) -> None:
        """Apply Euclidean (SGD) updates: W -= lr * pseudo_grad.

        Note: TargetInversionCredit doesn't provide bias gradients, so biases
        are not updated (matching reference behavior).
        """
        with torch.no_grad():
            for i, grad in enumerate(pseudo_grads):
                layer = self._forward_layers[i]
                layer.weight.sub_(lr * grad)
                # Biases are not updated (reference doesn't provide bias_grads)

    def _prepare_inputs(self, x: Tensor, y: Tensor) -> tuple[Tensor, Tensor]:
        """Prepare and move inputs to device."""
        if x.dim() > 2:
            x = x.view(x.size(0), -1)
        return (
            x.to(device=self._device, dtype=self._dtype),
            y.to(device=self._device),
        )

    def _get_dtp_config(self, model) -> tuple:
        """Extract DTP-specific config from model."""
        layers = getattr(model, "layers", None)
        out_layer = getattr(model, "out_layer", None)
        out_opt = getattr(model, "out_opt", None)
        criterion = getattr(model, "criterion", None) or torch.nn.CrossEntropyLoss()
        target_lr = float(getattr(model, "target_lr", self._target_lr))
        return layers, out_layer, out_opt, criterion, target_lr

    def _forward_pass(self, layers, x: Tensor) -> tuple[list[Tensor], Tensor]:
        """Run forward pass and collect hidden states."""
        hs: list[Tensor] = [x]
        h = x
        for layer in layers:
            h = layer.forward_net(h)
            hs.append(h)
        return hs, h

    def _update_output_layer(self, out_layer, h: Tensor, y: Tensor, out_opt, criterion):
        """Update output layer via its own optimizer."""
        out = out_layer(h)
        loss = criterion(out, y)
        if out_opt is not None:
            out_opt.zero_grad()
            loss.backward()
            out_opt.step()
        return out, loss

    def _compute_target(
        self, h: Tensor, out_layer, y: Tensor, criterion, target_lr: float
    ) -> Tensor:
        """Compute difference target for output layer."""
        t = h.clone().detach().requires_grad_(True)
        with torch.enable_grad():
            out_t = out_layer(t)
            loss_t = criterion(out_t, y)
            grad_t = torch.autograd.grad(loss_t, t)[0]
        with torch.no_grad():
            return h - target_lr * grad_t

    def _propagate_targets(
        self, layers, hs: list[Tensor], t_target: Tensor
    ) -> list[Tensor]:
        """Propagate targets backward through inverse nets."""
        targets: list[Tensor] = [t_target]
        for i in reversed(range(len(layers))):
            layer = layers[i]
            if i > 0:
                h_prev = hs[i].detach()
                h_curr = hs[i + 1].detach()
                t_curr = targets[-1]
                with torch.no_grad():
                    t_prev = (
                        h_prev - layer.inverse_net(h_curr) + layer.inverse_net(t_curr)
                    )
                    targets.append(t_prev)
        return targets

    def _fit_forward_inverse(self, layers, hs: list[Tensor], targets: list[Tensor]):
        """Fit forward and inverse networks."""
        for i in reversed(range(len(layers))):
            layer = layers[i]
            t_curr = targets[-len(targets)]
            h_prev_det = hs[i].detach()
            layer.opt_f.zero_grad()
            pred_h = layer.forward_net(h_prev_det)
            loss_f = torch.nn.functional.mse_loss(pred_h, t_curr)
            loss_f.backward()

            if i > 0:
                layer.opt_g.zero_grad()
                inv_out = layer.inverse_net(pred_h.detach())
                loss_g = torch.nn.functional.mse_loss(inv_out, h_prev_det)
                loss_g.backward()
                layer.opt_g.step()

            layer.opt_f.step()

    def kernel_train_step(
        self,
        model: torch.nn.Module,
        config: KernelConfig | None,
        x: Tensor,
        y: Tensor,
        optimizer: object | None = None,
    ) -> dict[str, object] | None:
        """Bespoke Difference-Target-Propagation step (REFACTOR7 bespoke seam).

        DTP's dynamics (per-layer output-layer autograd update, target
        propagation through the trained inverse nets, then forward/inverse
        net fitting) don't fit the uniform ``forward → backward(acts, error)
        → update_weights`` contract, so the dispatch seam delegates here when
        present. It mirrors the reference ``DifferenceTargetProp.train_step``
        exactly: the output layer is updated first via its own Adam, a
        difference target ``h - target_lr * dL/dh`` is built from the output
        layer, then propagated backward through the inverse nets while each
        forward (and inverse, for cycle consistency) net is fitted with its
        own Adam.

        Args:
            model: The bound ``DifferenceTargetProp`` model (``layers``
                ModuleList of ``DTPLayer`` with ``forward_net``/``inverse_net``
                Sequentials + per-net ``opt_f``/``opt_g``, plus ``out_layer``,
                ``out_opt``, ``criterion``, ``target_lr``).
            config: KernelConfig (kept for seam parity with other bespoke
                backends; the reference dynamics read the model).
            x: Input batch.
            y: Target labels.
            optimizer: Ignored — DTP owns per-layer optimizers on the model.

        Returns:
            ``{"loss", "accuracy", "logits"}`` or ``None`` when the model does
            not expose the DTP surface (caller falls through to ``train_step``).
        """
        layers, out_layer, out_opt, criterion, target_lr = self._get_dtp_config(model)
        if not layers or out_layer is None:
            return None

        self._forward_layers = [layer.forward_net[0] for layer in layers]
        self._inverse_layers = [layer.inverse_net[0] for layer in layers]

        x, y = self._prepare_inputs(x, y)
        hs, h = self._forward_pass(layers, x)
        out, loss = self._update_output_layer(out_layer, h, y, out_opt, criterion)
        t_target = self._compute_target(h, out_layer, y, criterion, target_lr)
        targets = self._propagate_targets(layers, hs, t_target)
        self._fit_forward_inverse(layers, hs, targets)

        accuracy = (out.argmax(dim=1) == y).float().mean().item()
        return {
            "loss": loss.item(),
            "accuracy": accuracy,
            "logits": out.detach(),
        }

    def get_memory_stats(self) -> dict[str, float]:
        fwd_params = sum(
            p.numel() for layer in self._forward_layers for p in layer.parameters()
        )
        return {
            "forward_params_mb": fwd_params * 4 / 1e6,
            "activations_mb": 0.0,
        }

    def get_settle_telemetry(self) -> dict[str, object] | None:
        return {
            "max_steps": self._max_steps,
            "step_size": self._step_size,
            "convergence_threshold": self._convergence_threshold,
        }


def _get_activation(name: str) -> torch.nn.Module:
    activations = {
        "relu": torch.nn.ReLU(),
        "silu": torch.nn.SiLU(),
        "tanh": torch.nn.Tanh(),
        "gelu": torch.nn.GELU(),
    }
    return activations.get(name.lower(), torch.nn.Tanh())


# Register backend for all HardwareTargets


__all__ = ["TPKernelBackend"]


# Triton kernels for fused TP operations
try:  # noqa: PLR0915
    import math
    import triton
    import triton.language as tl

    from computronium.acceleration import grid
    from computronium.acceleration.grid import grid_2d

    @triton.jit
    def _tp_transpose_feedback_kernel(
        target_ptr,
        weight_ptr,
        out_ptr,
        B,
        D_in,
        D_out,
        BLOCK_B: tl.constexpr,
        BLOCK_D: tl.constexpr,
    ):
        """Fused transpose feedback projection: target @ W^T.

        Weight matrix has shape [D_out, D_in] (row-major).
        Computes target @ W^T where target: [B, D_out], weight: [D_out, D_in].
        This is equivalent to target @ weight.T -> [B, D_in]
        """
        pid_b = tl.program_id(0)
        pid_d = tl.program_id(1)

        offs_b = pid_b * BLOCK_B + tl.arange(0, BLOCK_B)
        offs_d = pid_d * BLOCK_D + tl.arange(0, BLOCK_D)

        mask_b = offs_b < B
        mask_d = offs_d < D_in

        acc = tl.zeros((BLOCK_B, BLOCK_D), dtype=tl.float32)
        for k in range(0, D_out, BLOCK_D):
            offs_k = k + tl.arange(0, BLOCK_D)
            mask_k = offs_k < D_out

            target_tile = tl.load(
                target_ptr + offs_b[:, None] * D_out + offs_k[None, :],
                mask=mask_b[:, None] & mask_k[None, :],
                other=0.0,
            )

            w_tile = tl.load(
                weight_ptr + offs_k[:, None] * D_in + offs_d[None, :],
                mask=mask_k[:, None] & mask_d[None, :],
                other=0.0,
            )

            acc += tl.dot(target_tile, w_tile, input_precision="ieee")

        tl.store(
            out_ptr + offs_b[:, None] * D_in + offs_d[None, :],
            acc,
            mask=mask_b[:, None] & mask_d[None, :],
        )

    @triton.jit
    def _tp_batched_outer_kernel(
        pre_ptr,
        post_ptr,
        grad_ptr,
        B,
        D_in,
        D_out,
        BLOCK_IN: tl.constexpr,
        BLOCK_OUT: tl.constexpr,
    ):
        """Fused batched outer product for weight gradients."""
        offs_out, offs_in, mask_out, mask_in = grid.tile_2d(
            D_out, D_in, BLOCK_OUT, BLOCK_IN
        )

        acc = tl.zeros((BLOCK_OUT, BLOCK_IN), dtype=tl.float32)

        for b in range(B):
            pre = tl.load(
                pre_ptr + b * D_in + offs_in[None, :],
                mask=mask_in[None, :],
                other=0.0,
            )
            post = tl.load(
                post_ptr + b * D_out + offs_out[:, None],
                mask=mask_out[:, None],
                other=0.0,
            )
            acc += post * pre

        acc /= B
        grid.store_2d(grad_ptr, acc, D_in, offs_out, offs_in, mask_out, mask_in)

    TRITON_IMPORTED_TP = True
except ImportError:
    TRITON_IMPORTED_TP = False


def tp_transpose_feedback_triton(
    target: torch.Tensor,
    weight: torch.Tensor,
) -> torch.Tensor:
    """Compute target @ W^T using Triton.

    Args:
        target: [B, D_out]
        weight: [D_out, D_in] (forward weight matrix)

    Returns:
        [B, D_in]
    """
    if not TRITON_IMPORTED_TP or not target.is_cuda:
        return target @ weight.T

    B, D_out = target.shape
    D_in = weight.shape[1]
    if weight.shape[0] != D_out:
        raise ValueError(
            f"weight projection must map D_out={D_out}, got {weight.shape[0]}"
        )

    out = torch.empty(B, D_in, device=target.device, dtype=target.dtype)

    BLOCK_B = 32
    BLOCK_D = 64
    grid = (math.ceil(B / BLOCK_B), math.ceil(D_in / BLOCK_D))

    _tp_transpose_feedback_kernel[grid](
        target,
        weight,
        out,
        B,
        D_in,
        D_out,
        BLOCK_B=32,
        BLOCK_D=64,
    )
    return out


def tp_batched_outer_triton(
    pre: torch.Tensor,
    post: torch.Tensor,
) -> torch.Tensor:
    """Compute batched outer product using Triton.

    Args:
        pre: [B, D_in]
        post: [B, D_out]

    Returns:
        [D_out, D_in] (averaged over batch)
    """
    if not TRITON_IMPORTED_TP or not pre.is_cuda:
        return (post.T @ pre) / pre.shape[0]

    B, D_in = pre.shape
    D_out = post.shape[1]
    if post.shape[0] != B:
        raise ValueError(f"post-activation must have B={B} rows, got {post.shape[0]}")

    out = torch.empty(D_out, D_in, device=pre.device, dtype=pre.dtype)

    BLOCK_IN = 64
    BLOCK_OUT = 64
    grid = grid_2d(D_out, D_in, BLOCK_OUT, BLOCK_IN)

    _tp_batched_outer_kernel[grid](
        pre,
        post,
        out,
        B,
        D_in,
        D_out,
        BLOCK_IN=64,
        BLOCK_OUT=64,
    )
    return out


__all__ += [
    "TRITON_IMPORTED_TP",
    "tp_transpose_feedback_triton",
    "tp_batched_outer_triton",
]
