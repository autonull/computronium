"""Backprop Baseline Kernel Backend.

Fused BPTT kernel for the standard autograd family. Unlike the other
bio-plausible backends this is the *reference* the parity gates compare
against — it computes exact backpropagation gradients through the layer
stack (manual chain rule, no autograd graph) so a fused/settled kernel can be
verified to match within tolerance.

Memory complexity is O(L) because backprop stores an activation per layer.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch
from torch import Tensor, nn

from computronium.acceleration.activations import (
    activation_derivative,
    activation_from_name,
)
from computronium.acceleration.contrastive_primitives import batched_outer_product
from computronium.acceleration.kernel_backend import (
    AlgorithmFamily,
    HardwareTarget,
    KernelConfig,
    LocalityLevel,
)

if TYPE_CHECKING:
    from computronium.ontology import System


class BackpropKernelBackend:
    """Fused backpropagation kernel backend (BPTT/reference baseline).

    Implements an explicit forward/backward chain-rule pass over a stack of
    ``nn.Linear`` layers. The backward pass computes each layer's weight and
    bias gradients from the back-propagated error and the cached activations,
    matching ``torch.autograd`` exactly (up to floating-point order).
    """

    name = AlgorithmFamily.BACKPROP
    supported_dtypes = (torch.float32, torch.float16, torch.bfloat16)
    supports_autograd = True
    requires_settle = False
    memory_complexity = "O(L)"
    locality_level = LocalityLevel.GLOBAL

    def __init__(self) -> None:
        self._config: KernelConfig | None = None
        self._layers: list[nn.Linear] = []
        self._activation_name: str = "relu"
        self._device: torch.device = torch.device("cpu")
        self._dtype: torch.dtype = torch.float32

    def initialize(self, config: KernelConfig) -> None:
        """Initialize backend with configuration."""
        self._config = config
        is_cuda = config.hardware in (HardwareTarget.CUDA, HardwareTarget.TRITON)  # ruff: ignore[literal-membership]
        self._device = torch.device("cuda" if is_cuda else "cpu")
        self._dtype = config.dtype
        self._activation_name = str(config.extra.get("activation", "relu"))

    def set_model_ref(self, layers: list[nn.Linear]) -> None:
        """Set reference to the model's linear layer stack."""
        self._layers = layers

    def bind_system(self, system: System) -> None:
        """Bind the kernel to a System's geometry."""
        layers = self._extract_layers(system.geometry)
        if layers:
            self.set_model_ref(layers)

    def _extract_layers(self, geometry) -> list[nn.Linear]:
        """Extract linear layers from geometry."""
        if hasattr(geometry, "params"):
            layers = []
            for name, param in geometry.params.items():
                if "weight" in name and hasattr(geometry, name.replace(".weight", "")):
                    layer = getattr(geometry, name.replace(".weight", ""))
                    if isinstance(layer, nn.Linear):
                        layers.append(layer)
            if layers:
                return layers
        if hasattr(geometry, "layers") and isinstance(geometry.layers, list):
            return geometry.layers
        return []

    def train_step(self, x: Tensor, y: Tensor) -> dict[str, float]:
        """Execute one training step using backpropagation."""
        # Forward pass
        output, activations = self.forward(x)
        # Compute error
        error = torch.nn.functional.one_hot(y, num_classes=output.shape[1]).float().to(
            device=output.device, dtype=output.dtype
        ) - torch.softmax(output, dim=-1)
        # Backward pass
        gradients = self.backward(activations, error)
        # Apply updates
        self.update_weights(gradients, 1.0)
        # Return metrics
        with torch.no_grad():
            loss = torch.nn.functional.cross_entropy(output, y).item()
            acc = (output.argmax(-1) == y).float().mean().item()
        return {"loss": loss, "accuracy": acc}

    def forward(self, x: Tensor) -> tuple[Tensor, tuple[list[Tensor], list[Tensor]]]:
        """Forward pass returning output and per-layer pre/post activations.

        Returns:
            ``(output, (pre_activations, post_activations))`` where:
            - ``pre_activations[i]`` is the pre-activation input to layer i's activation (or layer output for last layer)
            - ``post_activations[i]`` is the post-activation output of layer i
            - ``post_activations[0] == x`` (input)
        """
        x = x.to(device=self._device, dtype=self._dtype)
        if x.dim() > 2:
            x = x.view(x.size(0), -1)

        pre_activations: list[Tensor] = []
        post_activations: list[Tensor] = [x]
        h = x
        activation = activation_from_name(self._activation_name)

        for i, layer in enumerate(self._layers):
            pre = layer(h)
            pre_activations.append(pre)
            h = activation(pre) if i < len(self._layers) - 1 else pre
            post_activations.append(h)

        return post_activations[-1], (pre_activations, post_activations)

    def backward(
        self,
        activations: tuple[list[Tensor], list[Tensor]],
        error: Tensor,
    ) -> dict[str, Tensor]:
        """Manual backprop: compute weight and bias gradients.

        Args:
            activations: ``(pre_activations, post_activations)`` from :meth:`forward`.
            error: Output error (``output - target``) ``[B, D_out]``.

        Returns:
            Dict mapping ``layers.<i>.weight`` / ``layers.<i>.bias`` to gradients.
        """
        pre_activations, post_activations = activations
        weight_grads: dict[str, Tensor] = {}
        bias_grads: dict[str, Tensor] = {}
        propagated = error

        for i in reversed(range(len(self._layers))):
            h_prev = post_activations[i]

            if i < len(self._layers) - 1:
                # Use PRE-activation for derivative (input to activation function)
                pre = pre_activations[i]
                propagated *= activation_derivative(pre, self._activation_name)

            weight_grads[f"layers.{i}.weight"] = batched_outer_product(
                h_prev, propagated
            )
            if self._layers[i].bias is not None:
                bias_grads[f"layers.{i}.bias"] = propagated.mean(dim=0)

            propagated = propagated @ self._layers[i].weight.data  # ruff: ignore[non-augmented-assignment]

        result = dict(weight_grads)
        result.update(bias_grads)
        return result

    def update_weights(self, gradients: dict[str, Tensor], lr: float) -> None:
        """Apply weight updates in-place."""
        with torch.no_grad():
            for name, grad in gradients.items():
                layer_idx = int(name.split(".")[1])
                if "weight" in name:
                    self._layers[layer_idx].weight.sub_(lr * grad)
                elif "bias" in name and self._layers[layer_idx].bias is not None:
                    self._layers[layer_idx].bias.sub_(lr * grad)

    def get_memory_stats(self) -> dict[str, float]:
        """Return memory usage stats (activations stored per layer: O(L))."""
        total_params = sum(
            p.numel() for layer in self._layers for p in layer.parameters()
        )
        return {
            "params_mb": total_params * 4 / 1e6,
            "activations_mb": 0.0,
        }

    def get_settle_telemetry(self) -> dict[str, object] | None:
        """Backprop has no settling dynamics."""
        return None


# Register backend for all HardwareTargets

__all__ = ["BackpropKernelBackend"]
