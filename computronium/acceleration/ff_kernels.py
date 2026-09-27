"""Forward-Forward / PEPITA Kernel Backend.

Fused kernels for Forward-Forward goodness and PEPITA error-modulated updates.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch
from torch import Tensor

from computronium.acceleration.contrastive_primitives import (
    batched_outer_product,
    contrastive_delta,
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


class FFKernelBackend:
    """Forward-Forward kernel backend.

    Implements the Forward-Forward algorithm with positive/negative passes
    and goodness-based contrastive updates.
    """

    name = AlgorithmFamily.FF
    supported_dtypes = (torch.float32, torch.float16, torch.bfloat16)
    supports_autograd = False
    requires_settle = False
    memory_complexity = "O(1)"
    locality_level = LocalityLevel.FORWARD_ONLY

    def __init__(self) -> None:
        self._config: KernelConfig | None = None
        self._layers: list[torch.nn.Linear] = []
        self._threshold: float = 1.0
        self._num_layers: int = 0
        self._device: torch.device = torch.device("cpu")
        self._dtype: torch.dtype = torch.float32
        self._activation: torch.nn.Module = torch.nn.ReLU()

    def initialize(self, config: KernelConfig) -> None:
        """Initialize backend with configuration."""
        self._config = config
        is_cuda = config.hardware in (HardwareTarget.CUDA, HardwareTarget.TRITON)  # ruff: ignore[literal-membership]
        self._device = torch.device("cuda" if is_cuda else "cpu")
        self._dtype = config.dtype

        extra = config.extra
        self._threshold = extra.get("threshold", 1.0)
        self._num_layers = extra.get("num_layers", 3)
        self._input_dim = extra.get("input_dim", 784)
        self._output_dim = extra.get("output_dim", 10)
        self._activation = _get_activation(extra.get("activation", "relu"))

    def set_model_ref(
        self,
        layers: list[LinearView],
        activation: torch.nn.Module | None = None,
    ) -> None:
        """Set reference to model layers."""
        self._layers = layers
        if activation is not None:
            self._activation = activation

    def bind_system(self, system: System) -> None:
        """Bind the kernel to a System's geometry."""
        layers = self._extract_layers(system.geometry)
        if layers:
            self.set_model_ref(layers)

    def _extract_layers(self, geometry) -> list[LinearView]:
        return linear_views(geometry)

    def train_step(self, x: Tensor, y: Tensor) -> dict[str, float]:
        """Execute one training step using FF positive/negative passes."""
        # Positive pass
        pos_output, pos_acts = self.forward_positive(x, y)
        # Negative pass
        neg_output, neg_acts = self.forward_negative(x, y)
        # Compute updates
        gradients = self.backward_contrastive(pos_acts, neg_acts, self._threshold)
        # Apply updates
        self.update_weights(gradients, 1.0)
        # Return metrics
        with torch.no_grad():
            pos_goodness = (pos_output**2).sum(dim=1).mean().item()
            neg_goodness = (neg_output**2).sum(dim=1).mean().item()
            loss = neg_goodness - pos_goodness + self._threshold
            acc = (pos_output.argmax(-1) == y).float().mean().item()
        return {"loss": loss, "accuracy": acc}

    def forward_positive(self, x: Tensor, y: Tensor) -> tuple[Tensor, list[Tensor]]:
        """Positive pass with label information.

        Args:
            x: Input [B, D_in]
            y: Labels [B]

        Returns:
            (output, activations) with label information embedded
        """
        x = x.to(device=self._device, dtype=self._dtype)
        if x.dim() > 2:
            x = x.view(x.size(0), -1)

        # Embed label into input (concatenate or add)
        # Standard FF: concatenate one-hot label to input (output_dim classes)
        y_onehot = (
            torch.nn.functional
            .one_hot(y, num_classes=self._output_dim)
            .float()
            .to(device=self._device, dtype=self._dtype)
        )
        x_pos = torch.cat([x, y_onehot], dim=1)

        return self._forward_layers(x_pos)

    def forward_negative(self, x: Tensor, y: Tensor) -> tuple[Tensor, list[Tensor]]:
        """Negative pass with wrong label information."""
        x = x.to(device=self._device, dtype=self._dtype)
        if x.dim() > 2:
            x = x.view(x.size(0), -1)

        # Use incorrect label (shift by 1)
        y_wrong = (y + 1) % self._output_dim
        y_onehot = (
            torch.nn.functional
            .one_hot(y_wrong, num_classes=self._output_dim)
            .float()
            .to(device=self._device, dtype=self._dtype)
        )
        x_neg = torch.cat([x, y_onehot], dim=1)

        return self._forward_layers(x_neg)

    def _forward_layers(self, x: Tensor) -> tuple[Tensor, list[Tensor]]:
        """Forward through all layers."""
        activations: list[Tensor] = [x]
        h = x

        for i, layer in enumerate(self._layers):
            h = layer(h)
            if i < len(self._layers) - 1:
                h = self._activation(h)
            activations.append(h)

        return activations[-1], activations

    def forward(self, x: Tensor) -> tuple[Tensor, list[Tensor]]:
        """Standard forward (for inference)."""
        x = x.to(device=self._device, dtype=self._dtype)
        if x.dim() > 2:
            x = x.view(x.size(0), -1)
        return self._forward_layers(x)

    def compute_goodness(
        self,
        pos_acts: list[Tensor],
        neg_acts: list[Tensor],
    ) -> dict[int, Tensor]:
        """Compute goodness per layer.

        Goodness = ||pos||^2 - ||neg||^2 - threshold

        Returns:
            Dict mapping layer_idx -> goodness per sample [B]
        """
        goodness: dict[int, Tensor] = {}
        for i in range(1, len(pos_acts)):  # Skip input layer
            pos_norm = pos_acts[i].pow(2).sum(dim=1)
            neg_norm = neg_acts[i].pow(2).sum(dim=1)
            goodness[i - 1] = pos_norm - neg_norm - self._threshold
        return goodness

    def backward(
        self,
        pos_activations: list[Tensor],
        neg_activations: list[Tensor],
    ) -> dict[str, Tensor]:
        """FF backward: contrastive update based on goodness.

        Layer update: Delta W = lr * (pos_acts.T @ pos_acts - neg_acts.T @ neg_acts) / B

        Returns:
            Weight deltas for all layers
        """
        weight_deltas: dict[str, Tensor] = {}

        for i in range(len(self._layers)):
            pos_pre = pos_activations[i]
            pos_post = pos_activations[i + 1]
            neg_pre = neg_activations[i]
            neg_post = neg_activations[i + 1]

            # FF contrastive update
            pos_grad = batched_outer_product(pos_pre, pos_post)
            neg_grad = batched_outer_product(neg_pre, neg_post)
            delta = contrastive_delta(neg_grad, pos_grad, beta=1.0)  # pos - neg

            weight_deltas[f"layers.{i}.weight"] = delta

            if self._layers[i].bias is not None:
                pos_bias = pos_post.mean(dim=0)
                neg_bias = neg_post.mean(dim=0)
                weight_deltas[f"layers.{i}.bias"] = pos_bias - neg_bias

        return weight_deltas

    def update_weights(self, gradients: dict[str, Tensor], lr: float) -> None:
        """Apply weight updates."""
        with torch.no_grad():
            for name, grad in gradients.items():
                if "weight" in name:
                    layer_idx = int(name.split(".")[1])
                    self._layers[layer_idx].weight.add_(lr * grad)
                elif "bias" in name:
                    layer_idx = int(name.split(".")[1])
                    if self._layers[layer_idx].bias is not None:
                        self._layers[layer_idx].bias.add_(lr * grad)

    def get_memory_stats(self) -> dict[str, float]:
        total_params = sum(
            p.numel() for layer in self._layers for p in layer.parameters()
        )
        return {
            "params_mb": total_params * 4 / 1e6,
            "activations_mb": 0.0,
        }

    def kernel_train_step(
        self,
        model: torch.nn.Module,
        config: KernelConfig | None,
        x: Tensor,
        y: Tensor,
        optimizer: object | None = None,
    ) -> dict[str, object] | None:
        """Bespoke Forward-Forward training step (REFACTOR7 consumption).

        Forward-Forward's two-pass dynamics (positive pass with the true label
        embedded, negative pass with a decoy label, contrastive goodness
        update) don't fit the uniform ``forward → backward(acts, error) →
        update_weights`` contract — its ``backward`` takes ``(pos, neg)``
        activations, not ``(acts, error)``. The dispatch seam delegates to this
        method when present, using the kernel's fused two-pass path.

        Args:
            model: The bound ``ForwardForwardNet`` model (its ``layers`` are
                ``FFLayer``s — plain ``nn.Linear`` subclasses with a per-layer
                Adam — so the reference's ``train_step`` is a valid fallback).
            config: KernelConfig (used for LR / dimensions).
            x: Input batch.
            y: Target labels.
            optimizer: Ignored — FF applies per-layer in-place updates.

        Returns:
            ``{"loss", "accuracy", "logits"}`` or ``None`` when the model does
            not expose the FF surface (caller falls through to its train_step).
        """
        layers = getattr(model, "layers", None)
        if not layers:
            return None

        self._layers = list(layers)
        if x.dim() > 2:
            x = x.view(x.size(0), -1)
        x = x.to(device=self._device, dtype=self._dtype)
        y = y.to(device=self._device)

        # The kernel's FF forward concatenates the one-hot label to the input,
        # so the first layer must accept ``input_dim + output_dim``. The
        # reference ``ForwardForwardNet`` embeds the label in the input's first
        # columns instead (its ``FFLayer`` accepts ``input_dim``) — those
        # dynamics don't match the kernel convention, so decline and fall
        # through to the model's own ``train_step``.
        output_dim = int(getattr(model, "output_dim", self._output_dim))
        if self._layers[0].in_features != x.shape[1] + output_dim:
            return None

        lr = float(getattr(model, "layer_lr", getattr(model, "lr", 0.03)))

        pos_out, pos_acts = self.forward_positive(x, y.to("cpu"))
        _neg_out, neg_acts = self.forward_negative(x, y.to("cpu"))
        grads = self.backward(pos_acts, neg_acts)
        self.update_weights(grads, lr)

        # Forward-Forward has no single forward output for a loss; report the
        # good-versus-bad contrast so the trainer's health gate has a scalar.
        goodness = self.compute_goodness(pos_acts, neg_acts)
        loss = -torch.stack(list(goodness.values())).mean().item()
        accuracy = (pos_out.argmax(dim=1) == y).float().mean().item()
        return {"loss": loss, "accuracy": accuracy, "logits": pos_out}

    def get_settle_telemetry(self) -> dict[str, object] | None:
        return None


class PEPITAKernelBackend:
    """PEPITA kernel backend.

    Error-modulated forward-forward with fixed feedback matrix.
    """

    name = AlgorithmFamily.PEPITA
    supported_dtypes = (torch.float32, torch.float16, torch.bfloat16)
    supports_autograd = False
    requires_settle = False
    memory_complexity = "O(1)"
    locality_level = LocalityLevel.FORWARD_ONLY

    def __init__(self) -> None:
        self._config: KernelConfig | None = None
        self._layers: list[torch.nn.Linear] = []
        self._feedback_matrix: Tensor | None = None
        self._scale: float = 1.0
        self._device: torch.device = torch.device("cpu")
        self._dtype: torch.dtype = torch.float32
        self._activation: torch.nn.Module = torch.nn.ReLU()

    def initialize(self, config: KernelConfig) -> None:
        """Initialize backend with configuration."""
        self._config = config
        is_cuda = config.hardware in (HardwareTarget.CUDA, HardwareTarget.TRITON)  # ruff: ignore[literal-membership]
        self._device = torch.device("cuda" if is_cuda else "cpu")
        self._dtype = config.dtype

        extra = config.extra
        self._scale = extra.get("feedback_matrix_scale", 1.0)
        self._activation = _get_activation(extra.get("activation", "relu"))
        self._output_dim = int(extra.get("output_dim", 10))

        # Create fixed random feedback matrix
        input_dim = extra.get("input_dim", 784)
        output_dim = self._output_dim
        self._feedback_matrix = (
            torch.randn(input_dim, output_dim, device=self._device, dtype=self._dtype)
            * 0.1
        )

    def set_model_ref(
        self,
        layers: list[LinearView],
        activation: torch.nn.Module | None = None,
    ) -> None:
        self._layers = layers
        if activation is not None:
            self._activation = activation

    def bind_system(self, system: System) -> None:
        """Bind the kernel to a System's geometry."""
        layers = self._extract_layers(system.geometry)
        if layers:
            self.set_model_ref(layers)

    def _extract_layers(self, geometry) -> list[LinearView]:
        return linear_views(geometry)

    def train_step(self, x: Tensor, y: Tensor) -> dict[str, float]:
        """Execute one training step using PEPITA standard/error-modulated passes."""
        std_output, std_acts = self.forward_standard(x)
        target = (
            torch.nn.functional
            .one_hot(y, num_classes=std_output.shape[1])
            .float()
            .to(device=std_output.device, dtype=std_output.dtype)
            if y.dim() == 1
            else y
        )
        err_output, err_acts = self.forward_error_modulated(x, target - std_output)
        # Compute updates
        gradients = self.backward(std_acts, err_acts)
        # Apply updates
        self.update_weights(gradients, 1.0)
        # Return metrics
        with torch.no_grad():
            loss = (std_output - err_output).pow(2).mean().item()
            acc = (std_output.argmax(-1) == y).float().mean().item()
        return {"loss": loss, "accuracy": acc}

    def forward_standard(self, x: Tensor) -> tuple[Tensor, list[Tensor]]:
        """Standard forward pass."""
        x = x.to(device=self._device, dtype=self._dtype)
        if x.dim() > 2:
            x = x.view(x.size(0), -1)

        activations: list[Tensor] = [x]
        h = x

        for i, layer in enumerate(self._layers):
            h = layer(h)
            if i < len(self._layers) - 1:
                h = self._activation(h)
            activations.append(h)

        return activations[-1], activations

    def forward_error_modulated(
        self, x: Tensor, error: Tensor
    ) -> tuple[Tensor, list[Tensor]]:
        """Error-modulated forward pass (PEPITA).

        Error is backprojected through fixed feedback matrix and added to input.
        """
        x = x.to(device=self._device, dtype=self._dtype)
        if x.dim() > 2:
            x = x.view(x.size(0), -1)

        # Backproject error to input space
        error_input = error @ self._feedback_matrix.T * self._scale
        x_modulated = x + error_input

        return self._forward_layers(x_modulated)

    def _forward_layers(self, x: Tensor) -> tuple[Tensor, list[Tensor]]:
        activations: list[Tensor] = [x]
        h = x

        for i, layer in enumerate(self._layers):
            h = layer(h)
            if i < len(self._layers) - 1:
                h = self._activation(h)
            activations.append(h)

        return activations[-1], activations

    def backward(
        self,
        standard_activations: list[Tensor],
        error_activations: list[Tensor],
        error: Tensor,
    ) -> dict[str, Tensor]:
        """PEPITA backward: error-modulated contrastive update.

        For every layer, Delta W = scale * (a_std.T @ pre - a_err.T @ pre) / B
        (the *standard minus error-modulated* correlation), so the downstream
        ``update_weights`` ``add_`` reproduces the reference's ``W -= lr *
        (a_err - a_std).T @ inp / B`` (the reference subtracts the positive
        error-modulated correlation).
        """
        weight_deltas: dict[str, Tensor] = {}

        for i in range(len(self._layers)):
            std_pre = standard_activations[i]
            std_post = standard_activations[i + 1]
            err_pre = error_activations[i]
            err_post = error_activations[i + 1]

            std_grad = batched_outer_product(std_pre, std_post)
            err_grad = batched_outer_product(err_pre, err_post)
            delta = self._scale * contrastive_delta(err_grad, std_grad, beta=1.0)

            weight_deltas[f"layers.{i}.weight"] = delta

            if self._layers[i].bias is not None:
                weight_deltas[f"layers.{i}.bias"] = self._scale * (
                    std_post.mean(dim=0) - err_post.mean(dim=0)
                )

        return weight_deltas

    def kernel_train_step(  # ruff: ignore[too-many-locals]
        self,
        model: torch.nn.Module,
        config: KernelConfig | None,
        x: Tensor,
        y: Tensor,
        optimizer: object | None = None,
    ) -> dict[str, object] | None:
        """Bespoke PEPITA training step (REFACTOR7 bespoke-family consumption).

        PEPITA's two-pass dynamics (standard forward → input perturbation via
        the fixed feedback matrix → error-modulated forward) don't fit the
        uniform ``forward → backward(activations, error) → update_weights``
        contract, so the dispatch seam delegates to this method when present.
        It mirrors the reference ``PEPITA.train_step`` exactly: each layer's
        weight moves by ``-lr * (a_err - a_std).T @ inp / B`` (the reference
        applies updates in-place, no torch optimizer).

        Args:
            model: The bound ``PEPITA`` model (``layers`` ModuleList of
                ``nn.Linear`` + ``out_layer`` + ``feedback_matrix`` + ``lr``).
            config: KernelConfig (unused by the reference dynamics; kept for
                seam parity with other bespoke backends).
            x: Input batch.
            y: Target labels.
            optimizer: Ignored — PEPITA is a forward-only local learner that
                updates weights in-place (no optimizer).

        Returns:
            ``{"loss", "accuracy", "logits"}`` or ``None`` when the model does
            not expose the PEPITA surface (caller falls through).
        """
        layers = getattr(model, "layers", None)
        out_layer = getattr(model, "out_layer", None)
        feedback = getattr(model, "feedback_matrix", None)
        if not layers or out_layer is None or feedback is None:
            return None

        self._layers = list(layers)
        lr = float(getattr(model, "lr", 0.01))
        output_dim = int(getattr(model, "output_dim", self._output_dim))

        if x.dim() > 2:
            x = x.view(x.size(0), -1)
        x = x.to(device=self._device, dtype=self._dtype)
        y = y.to(device=self._device)
        batch = x.shape[0]

        y_onehot = torch.zeros(batch, output_dim, device=x.device, dtype=self._dtype)
        y_onehot.scatter_(1, y.unsqueeze(1), 1.0)

        def _two_pass(x_in: Tensor) -> tuple[Tensor, list[Tensor]]:
            acts: list[Tensor] = []
            h = x_in
            for layer in self._layers:
                h = self._activation(layer(h))
                acts.append(h)
            out = out_layer(h)
            return out, acts

        with torch.no_grad():
            out_s, act_s = _two_pass(x)
            error = out_s - y_onehot
            x_mod = x + torch.mm(error, feedback.to(x.device).T)
            _out_m, act_m = _two_pass(x_mod)

            inputs = [x] + act_s[:-1]  # ruff: ignore[collection-literal-concatenation]
            for layer, a_s, a_m, inp in zip(self._layers, act_s, act_m, inputs):
                delta_a = a_m - a_s
                layer.weight.data -= lr * torch.mm(delta_a.T, inp) / batch
                if layer.bias is not None:
                    layer.bias.data -= lr * delta_a.mean(dim=0)

            out_layer.weight.data -= lr * torch.mm(error.T, act_s[-1]) / batch
            if out_layer.bias is not None:
                out_layer.bias.data -= lr * error.mean(dim=0)

        loss = (error**2).sum(dim=1).mean().item()
        accuracy = (out_s.argmax(dim=1) == y).float().mean().item()
        return {"loss": loss, "accuracy": accuracy, "logits": out_s}

    def update_weights(self, gradients: dict[str, Tensor], lr: float) -> None:
        with torch.no_grad():
            for name, grad in gradients.items():
                if "weight" in name:
                    layer_idx = int(name.split(".")[1])
                    self._layers[layer_idx].weight.add_(lr * grad)
                elif "bias" in name:
                    layer_idx = int(name.split(".")[1])
                    if self._layers[layer_idx].bias is not None:
                        self._layers[layer_idx].bias.add_(lr * grad)

    def get_memory_stats(self) -> dict[str, float]:
        total_params = sum(
            p.numel() for layer in self._layers for p in layer.parameters()
        )
        fb_mb = 0.0
        if self._feedback_matrix is not None:
            fb_mb = self._feedback_matrix.numel() * 4 / 1e6
        return {
            "params_mb": total_params * 4 / 1e6,
            "feedback_mb": fb_mb,
            "activations_mb": 0.0,
        }

    def get_settle_telemetry(self) -> dict[str, object] | None:
        return None


def _get_activation(name: str) -> torch.nn.Module:
    activations = {
        "relu": torch.nn.ReLU(),
        "silu": torch.nn.SiLU(),
        "tanh": torch.nn.Tanh(),
        "gelu": torch.nn.GELU(),
    }
    return activations.get(name.lower(), torch.nn.ReLU())


# Register backends for all HardwareTargets


# Triton kernels for fused FF/PEPITA operations
try:  # noqa: PLR0915
    import triton
    import triton.language as tl

    from computronium.acceleration import grid

    @triton.jit
    def _ff_goodness_kernel(
        pos_acts_ptr,
        neg_acts_ptr,
        goodness_ptr,
        threshold,
        B,
        D,
        BLOCK_B: tl.constexpr,
        BLOCK_D: tl.constexpr,
    ):
        """Compute FF goodness: ||pos||^2 - ||neg||^2 - threshold"""
        pid_b = tl.program_id(0)
        pid_d = tl.program_id(1)

        offs_b = pid_b * BLOCK_B + tl.arange(0, BLOCK_B)
        offs_d = pid_d * BLOCK_D + tl.arange(0, BLOCK_D)

        mask_b = offs_b < B
        mask_d = offs_d < D  # ruff: ignore[unused-variable]

        pos_norm = tl.zeros((BLOCK_B,), dtype=tl.float32)
        neg_norm = tl.zeros((BLOCK_B,), dtype=tl.float32)

        for i in range(D):
            offs_i = i
            if offs_i < D:
                pos = tl.load(
                    pos_acts_ptr + offs_b * D + offs_i, mask=mask_b, other=0.0
                )
                neg = tl.load(
                    neg_acts_ptr + offs_b * D + offs_i, mask=mask_b, other=0.0
                )
                pos_norm += pos * pos
                neg_norm += neg * neg

        goodness = pos_norm - neg_norm - threshold

        tl.store(goodness_ptr + offs_b, goodness, mask=mask_b)

    @triton.jit
    def _ff_contrastive_update_kernel(  # ruff: ignore[too-many-arguments, too-many-positional-arguments]
        pre_pos_ptr,
        post_pos_ptr,
        pre_neg_ptr,
        post_neg_ptr,
        delta_ptr,
        B,
        D_in,
        D_out,
        lr,
        BLOCK_IN: tl.constexpr,
        BLOCK_OUT: tl.constexpr,
    ):
        """FF contrastive weight update: dW = lr * (post_pos.T @ pre_pos - post_neg.T @ pre_neg) / B

        Launch with ``grid = (cdiv(D_out, BLOCK_OUT), cdiv(D_in, BLOCK_IN))``:
        the grid is row-major over ``delta``'s own ``[D_out, D_in]`` layout, so
        program 0 walks the output axis. The transposed order looks plausible and
        silently writes nothing when ``D_in`` is not a multiple of ``BLOCK_IN``.
        """
        offs_out, offs_in, mask_out, mask_in = grid.tile_2d(
            D_out, D_in, BLOCK_OUT, BLOCK_IN
        )

        acc_pos = tl.zeros((BLOCK_OUT, BLOCK_IN), dtype=tl.float32)
        acc_neg = tl.zeros((BLOCK_OUT, BLOCK_IN), dtype=tl.float32)

        for b in range(B):
            pre_p = tl.load(
                pre_pos_ptr + b * D_in + offs_in[None, :],
                mask=mask_in[None, :],
                other=0.0,
            )
            post_p = tl.load(
                post_pos_ptr + b * D_out + offs_out[:, None],
                mask=mask_out[:, None],
                other=0.0,
            )
            acc_pos += post_p * pre_p

            pre_n = tl.load(
                pre_neg_ptr + b * D_in + offs_in[None, :],
                mask=mask_in[None, :],
                other=0.0,
            )
            post_n = tl.load(
                post_neg_ptr + b * D_out + offs_out[:, None],
                mask=mask_out[:, None],
                other=0.0,
            )
            acc_neg += post_n * pre_n

        acc_pos = acc_pos / B  # ruff: ignore[non-augmented-assignment]
        acc_neg = acc_neg / B  # ruff: ignore[non-augmented-assignment]

        delta = lr * (acc_pos - acc_neg)

        grid.store_2d(delta_ptr, delta, D_in, offs_out, offs_in, mask_out, mask_in)

    @triton.jit
    def _pepita_error_modulation_kernel(
        error_ptr,
        feedback_ptr,
        delta_ptr,
        scale,
        B,
        D_in,
        D_out,
        BLOCK_IN: tl.constexpr,
        BLOCK_OUT: tl.constexpr,
    ):
        """PEPITA error modulation: Delta W = scale * colsum(error) rows of feedback.T.

        Equal to `contrastive_primitives.pepita_error_modulation`, which is the
        specification (TODO36 §4.5). Output unit ``o`` gates the feedback column
        it belongs to, so the batch is reduced per output unit first and the
        product is a row scaling of the transposed feedback. There is no
        ``tl.dot`` here and that is deliberate: this is a broadcast, not a
        contraction, and the first version of this kernel had a GEMM with a
        contraction of length 1 — which is why it did not compile for its whole
        life.

        Launch with ``grid = (cdiv(D_out, BLOCK_OUT), cdiv(D_in, BLOCK_IN))``:
        the grid is row-major over ``delta``'s own ``[D_out, D_in]`` layout. The
        transposed order looks plausible and silently writes nothing when
        ``D_in`` is not a multiple of ``BLOCK_IN``.
        """
        offs_out, offs_in, mask_out, mask_in = grid.tile_2d(
            D_out, D_in, BLOCK_OUT, BLOCK_IN
        )

        err = tl.zeros((BLOCK_OUT,), dtype=tl.float32)
        for b in range(B):
            err += tl.load(error_ptr + b * D_out + offs_out, mask=mask_out, other=0.0)

        fb = tl.load(
            feedback_ptr + offs_in[:, None] * D_out + offs_out[None, :],
            mask=mask_in[:, None] & mask_out[None, :],
            other=0.0,
        )
        acc = err[:, None] * tl.trans(fb)
        delta = scale * acc  # ruff: ignore[non-augmented-assignment]

        grid.store_2d(delta_ptr, delta, D_in, offs_out, offs_in, mask_out, mask_in)

    @triton.jit
    def _pepita_contrastive_update_kernel(  # ruff: ignore[too-many-arguments, too-many-positional-arguments]
        pre_std_ptr,
        post_std_ptr,
        pre_err_ptr,
        post_err_ptr,
        delta_ptr,
        B,
        D_in,
        D_out,
        lr,
        BLOCK_IN: tl.constexpr,
        BLOCK_OUT: tl.constexpr,
    ):
        """PEPITA contrastive update: Delta W = lr * (std_post.T @ std_pre - err_post.T @ err_pre) / B"""
        offs_out, offs_in, mask_out, mask_in = grid.tile_2d(
            D_out, D_in, BLOCK_OUT, BLOCK_IN
        )

        acc_std = tl.zeros((BLOCK_OUT, BLOCK_IN), dtype=tl.float32)
        acc_err = tl.zeros((BLOCK_OUT, BLOCK_IN), dtype=tl.float32)

        for b in range(B):
            pre_s = tl.load(
                pre_std_ptr + b * D_in + offs_in[None, :],
                mask=mask_in[None, :],
                other=0.0,
            )
            post_s = tl.load(
                post_std_ptr + b * D_out + offs_out[:, None],
                mask=mask_out[:, None],
                other=0.0,
            )
            acc_std += post_s * pre_s

            pre_e = tl.load(
                pre_err_ptr + b * D_in + offs_in[None, :],
                mask=mask_in[None, :],
                other=0.0,
            )
            post_e = tl.load(
                post_err_ptr + b * D_out + offs_out[:, None],
                mask=mask_out[:, None],
                other=0.0,
            )
            acc_err += post_e * pre_e

        acc_std = acc_std / B  # ruff: ignore[non-augmented-assignment]
        acc_err = acc_err / B  # ruff: ignore[non-augmented-assignment]

        delta = lr * (acc_std - acc_err)

        grid.store_2d(delta_ptr, delta, D_in, offs_out, offs_in, mask_out, mask_in)

    HAS_TRITON_FF = True
except ImportError:
    HAS_TRITON_FF = False


__all__ = ["HAS_TRITON_FF", "FFKernelBackend", "PEPITAKernelBackend"]
