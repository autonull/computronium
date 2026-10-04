"""Direct Feedback Alignment Kernel Backend.

Fused kernels for DFA:
- Direct feedback projection: output error @ feedback_matrix (per layer)
- Batched outer product for weight gradients
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import torch
from torch import Tensor

from computronium.acceleration.contrastive_primitives import batched_outer_product
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


class DFAKernelBackend:
    """Direct Feedback Alignment kernel backend.

    Implements DFA backward loop with direct feedback from output to all layers.
    Unlike FA, DFA uses a single feedback projection per layer from the output
    error directly (not chained through intermediate layers).
    """

    name = AlgorithmFamily.FA
    supported_dtypes = (torch.float32, torch.float16, torch.bfloat16)
    supports_autograd = False
    requires_settle = False
    memory_complexity = "O(1)"
    locality_level = LocalityLevel.LAYERWISE

    def __init__(self) -> None:
        self._config: KernelConfig | None = None
        self._layers: list[LinearView] = []
        self._feedback_weights: list[Tensor] = []
        self._activation: torch.nn.Module = torch.nn.ReLU()
        self._num_layers: int = 0
        self._device: torch.device = torch.device("cpu")
        self._dtype: torch.dtype = torch.float32
        self._pre_activations: list[Tensor] = []
        self._lr: float = 0.01

    def initialize(self, config: KernelConfig) -> None:
        """Initialize backend with configuration."""
        self._config = config
        is_cuda = config.hardware in {HardwareTarget.CUDA, HardwareTarget.TRITON}
        self._device = torch.device("cuda" if is_cuda else "cpu")
        self._dtype = config.dtype

        extra = config.extra
        self._num_layers = int(extra.get("num_layers", 3))
        self._lr = float(extra.get("lr", 0.01))
        self._activation = _get_activation(str(extra.get("activation", "relu")))
        self._beta = float(extra.get("beta", 0.5))

        # Don't create feedback weights here - do it lazily in _init_feedback_weights
        # to match reference RNG state progression
        self._feedback_weights = []

    def set_model_ref(
        self,
        layers: list[LinearView],
        activation: torch.nn.Module | None = None,
        feedback_scale: float = 0.01,
    ) -> None:
        """Set reference to model layers for weight updates.

        Feedback weights are built from the bound layers' actual shapes.
        They are initialized lazily during the first train_step to match
        the reference's RNG state progression.
        """
        self._layers = layers
        self._feedback_scale = feedback_scale
        if activation is not None:
            self._activation = activation
        # Don't initialize feedback weights here - do it lazily in train_step
        self._feedback_weights = []

    def _init_feedback_weights(self) -> None:
        """Lazily initialize feedback weights to match reference RNG state."""
        if self._feedback_weights:
            return
        if not self._layers:
            return
        device = self._layers[0].weight.device
        dtype = self._layers[0].weight.dtype
        self._feedback_weights = [
            torch.randn_like(layer.weight) * self._feedback_scale
            for layer in self._layers
        ]

    def bind_system(self, system: System) -> None:
        """Bind the kernel to a System's geometry."""
        layers = self._extract_layers(system.geometry)
        if layers:
            self.set_model_ref(layers)

    def _extract_layers(self, geometry) -> list[LinearView]:
        return linear_views(geometry)

    def train_step(self, x: Tensor, y: Tensor) -> dict[str, float]:
        """Execute one training step using DFA.

        Matches the pipeline output format with free/nudged phases.
        """
        # Get beta from config (default 0.5 for FA/DFA)
        beta = getattr(self, "_beta", 0.5)

        # Phase 1: FREE phase (no target) - forward pass
        _, free_activations = self.forward(x)
        free_output = free_activations[-1]

        # Phase 2: NUDGED phase (with target) - forward + beta nudge
        _, nudged_activations = self.forward(x)
        nudged_output = nudged_activations[-1]

        # Apply beta nudge to output (matching InstantaneousDynamics)
        if y.dim() == 1:
            target_vec = (
                torch.nn.functional
                .one_hot(y, num_classes=nudged_output.shape[1])
                .float()
                .to(device=nudged_output.device, dtype=nudged_output.dtype)
            )
        else:
            target_vec = y.to(device=nudged_output.device, dtype=nudged_output.dtype)

        # Nudge: output + beta * (target - output)
        nudged_output_nudged = nudged_output + beta * (target_vec - nudged_output)

        # Replace the last activation with the nudged output for backward pass
        nudged_activations_nudged = nudged_activations[:-1] + [nudged_output_nudged]

        # Cross-entropy gradient: (softmax - one_hot) / batch
        batch_size = nudged_output_nudged.shape[0]
        probs = torch.softmax(nudged_output_nudged, dim=-1)
        error = (probs - target_vec) / batch_size

        # Initialize feedback weights lazily (matches reference timing)
        self._init_feedback_weights()

        # Run DFA backward using nudged phase error and NUDGED activations
        gradients = self.backward(nudged_activations_nudged, error)
        # Apply updates
        self.update_weights(gradients, self._lr)

        # Post-update: FREE phase for honest metrics
        _, post_activations = self.forward(x)
        post_output = post_activations[-1]

        with torch.no_grad():
            # Nudged phase metrics (target-conditioned, using nudged output)
            nudged_loss = torch.nn.functional.cross_entropy(
                nudged_output_nudged, y
            ).item()
            nudged_acc = (nudged_output_nudged.argmax(-1) == y).float().mean().item()

            # Post-update free phase metrics
            free_loss = torch.nn.functional.cross_entropy(post_output, y).item()
            free_acc = (post_output.argmax(-1) == y).float().mean().item()

            # For instantaneous dynamics, energy = loss for nudged phase
            # Free phase energy is 0.0 (no loss set on free state)
            energy = nudged_loss
            free_energy = 0.0

        return {
            "loss": nudged_loss,
            "energy": energy,
            "nudged_fit_accuracy": nudged_acc,
            "free_loss": free_loss,
            "free_energy": free_energy,
            "free_accuracy": free_acc,
        }

    def forward(self, x: Tensor) -> tuple[Tensor, list[Tensor]]:
        """Forward pass returning output and per-layer activations.

        Returns:
            (output, activations) where activations = [x, h1, h2, ..., output]
        """
        x = x.to(device=self._device, dtype=self._dtype)
        if x.dim() > 2:
            x = x.view(x.size(0), -1)

        activations: list[Tensor] = [x]
        pre_activations: list[Tensor] = []
        h = x

        for i, layer in enumerate(self._layers):
            h = layer(h)
            pre_activations.append(h)
            if i < len(self._layers) - 1:
                h = self._activation(h)
            activations.append(h)

        self._pre_activations = pre_activations

        return activations[-1], activations

    def backward(
        self,
        activations: list[Tensor],
        error: Tensor,
    ) -> dict[str, Tensor]:
        """DFA backward loop: compute weight and bias gradients.

        DFA difference from FA: Each hidden layer receives feedback DIRECTLY
        from the output error, not through a chain of feedback weights.

        Args:
            activations: [x, h1, h2, ..., output] from forward
            error: Output error (target - output) [B, D_out]

        Returns:
            Dict mapping parameter names to gradients
        """
        num_layers = len(self._layers)

        weight_grads: dict[str, Tensor] = {}
        bias_grads: dict[str, Tensor] = {}

        for i in reversed(range(num_layers)):
            h_prev = activations[i]

            if i < num_layers - 1:
                # DFA: Direct feedback from output error to this layer
                # feedback_weights[i] has shape [D_{i+1}, D_i] for layer i
                B = self._feedback_weights[i]

                # Project error directly: error @ B  [B, D_out] @ [D_out, D_i] -> [B, D_i]
                grad_h = error @ B

                grad_h = _apply_activation_derivative(
                    grad_h, self._pre_activation(i), self._activation
                )
            else:
                grad_h = error

            # Weight gradient: grad_h.T @ h_prev / batch_size
            wgrad = batched_outer_product(h_prev, grad_h)
            weight_grads[f"layers.{i}.weight"] = wgrad

            # Bias gradient: mean over batch
            bgrad = grad_h.mean(dim=0)
            if self._layers[i].bias is not None:
                bias_grads[f"layers.{i}.bias"] = bgrad

        result = {}
        result.update(weight_grads)
        result.update(bias_grads)
        return result

    def _pre_activation(self, layer_index: int) -> Tensor:
        """Pre-activation of ``layer_index``, as recorded by :meth:`forward`."""
        if len(self._pre_activations) != len(self._layers):
            raise RuntimeError(
                "DFA backward requires the pre-activations recorded by forward(); "
                f"got {len(self._pre_activations)} for {len(self._layers)} layers"
            )
        return self._pre_activations[layer_index]

    def update_weights(self, gradients: dict[str, Tensor], lr: float) -> None:
        """Apply weight updates in-place."""
        with torch.no_grad():
            for name, grad in gradients.items():
                if "weight" in name:
                    layer_idx = int(name.split(".")[1])
                    self._layers[layer_idx].weight.sub_(lr * grad)
                elif "bias" in name:
                    layer_idx = int(name.split(".")[1])
                    bias = self._layers[layer_idx].bias
                    if bias is not None:
                        bias.sub_(lr * grad)

    def get_memory_stats(self) -> dict[str, float]:
        """Return memory usage stats."""
        total_params = sum(
            p.numel() for layer in self._layers for p in layer.parameters()
        )
        feedback_params = sum(w.numel() for w in self._feedback_weights)
        return {
            "params_mb": total_params * 4 / 1e6,
            "activations_mb": 0.0,
            "feedback_weights_mb": feedback_params * 4 / 1e6,
        }

    def get_settle_telemetry(self) -> dict[str, object] | None:
        """DFA doesn't have settling dynamics."""
        return None


def _get_activation(name: str) -> torch.nn.Module:
    """Get activation module by name."""
    activations = {
        "relu": torch.nn.ReLU(),
        "silu": torch.nn.SiLU(),
        "tanh": torch.nn.Tanh(),
        "gelu": torch.nn.GELU(),
    }
    return activations.get(name.lower(), torch.nn.ReLU())


def _apply_activation_derivative(
    grad_h: Tensor,
    pre_activation: Tensor,
    activation: torch.nn.Module,
) -> Tensor:
    """Multiply ``grad_h`` by f'(x), the derivative at the **pre**-activation.

    ``pre_activation`` must be the layer's input to the activation module, not
    its output: every branch below is a function of x, and the SiLU and GELU
    branches have no closed form in terms of f(x).
    """
    x = pre_activation
    if isinstance(activation, torch.nn.SiLU):
        sig = torch.sigmoid(x)
        return grad_h * sig * (1 + x * (1 - sig))
    if isinstance(activation, torch.nn.ReLU):
        return grad_h * (x > 0).to(grad_h.dtype)
    if isinstance(activation, torch.nn.Tanh):
        return grad_h * (1 - torch.tanh(x) ** 2)
    if isinstance(activation, torch.nn.GELU):
        cdf = 0.5 * (1 + torch.erf(x / math.sqrt(2)))
        pdf = torch.exp(-(x**2) / 2) / math.sqrt(2 * math.pi)
        return grad_h * (cdf + x * pdf)
    return grad_h * (x > 0).to(grad_h.dtype)


# Triton kernels for fused DFA operations
try:  # noqa: PLR0915
    import triton
    import triton.language as tl

    from computronium.acceleration import grid
    from computronium.acceleration.grid import grid_2d

    @triton.jit
    def _dfa_feedback_projection_kernel(
        error_ptr,
        feedback_ptr,
        out_ptr,
        B,
        D_in,
        D_out,
        BLOCK_B: tl.constexpr,
        BLOCK_D: tl.constexpr,
    ):
        """Fused direct feedback projection: error @ feedback.

        Feedback matrix has shape [D_out, D_in] (row-major, stride D_in).
        Computes error @ feedback where error: [B, D_out], feedback: [D_out, D_in].
        Output: [B, D_in]
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

            error_tile = tl.load(
                error_ptr + offs_b[:, None] * D_out + offs_k[None, :],
                mask=mask_b[:, None] & mask_k[None, :],
                other=0.0,
            )

            fb_tile = tl.load(
                feedback_ptr + offs_k[:, None] * D_in + offs_d[None, :],
                mask=mask_k[:, None] & mask_d[None, :],
                other=0.0,
            )

            acc += tl.dot(error_tile, fb_tile, input_precision="ieee")

        tl.store(
            out_ptr + offs_b[:, None] * D_in + offs_d[None, :],
            acc,
            mask=mask_b[:, None] & mask_d[None, :],
        )

    @triton.jit
    def _dfa_batched_outer_kernel(
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

    TRITON_IMPORTED_DFA = True
except ImportError:
    TRITON_IMPORTED_DFA = False


def dfa_feedback_projection_triton(
    error: torch.Tensor,
    feedback: torch.Tensor,
) -> torch.Tensor:
    """Compute error @ feedback using Triton.

    Args:
        error: [B, D_out]
        feedback: [D_out, D_in]

    Returns:
        [B, D_in]
    """
    if not TRITON_IMPORTED_DFA or not error.is_cuda:
        return error @ feedback

    B, D_out = error.shape
    D_in = feedback.shape[1]
    if feedback.shape[0] != D_out:
        raise ValueError(
            f"feedback projection must map D_out={D_out}, got {feedback.shape[0]}"
        )

    out = torch.empty(B, D_in, device=error.device, dtype=error.dtype)

    BLOCK_B = 32
    BLOCK_D = 64
    grid = (math.ceil(B / BLOCK_B), math.ceil(D_in / BLOCK_D))

    _dfa_feedback_projection_kernel[grid](
        error,
        feedback,
        out,
        B,
        D_in,
        D_out,
        BLOCK_B=32,
        BLOCK_D=64,
    )
    return out


def dfa_batched_outer_triton(
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
    if not TRITON_IMPORTED_DFA or not pre.is_cuda:
        return (post.T @ pre) / pre.shape[0]

    B, D_in = pre.shape
    D_out = post.shape[1]
    if post.shape[0] != B:
        raise ValueError(f"post-activation must have B={B} rows, got {post.shape[0]}")

    out = torch.empty(D_out, D_in, device=pre.device, dtype=pre.dtype)

    BLOCK_IN = 64
    BLOCK_OUT = 64
    grid = grid_2d(D_out, D_in, BLOCK_OUT, BLOCK_IN)

    _dfa_batched_outer_kernel[grid](
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


__all__ = [
    "TRITON_IMPORTED_DFA",
    "DFAKernelBackend",
    "dfa_batched_outer_triton",
    "dfa_feedback_projection_triton",
]
