"""EqProp KernelBackend Adapter.

Thin adapter wrapping the existing EqPropKernel for the KernelRegistry,
enabling unified benchmark/export/dispatch for EQPROP.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import numpy as np
import torch
from torch import Tensor

from computronium.acceleration.kernel_backend import (
    AlgorithmFamily,
    HardwareTarget,
    KernelConfig,
    KernelRegistry,
    LocalityLevel,
)
from computronium.acceleration.kernels import EqPropKernel

if TYPE_CHECKING:
    from computronium.acceleration.kernels import EqPropKernel as EqPropKernelType


class EqPropKernelBackend:
    """Thin adapter wrapping EqPropKernel for KernelRegistry."""

    name = AlgorithmFamily.EQPROP
    supported_dtypes = (torch.float32, torch.float16, torch.bfloat16)
    supports_autograd = False
    requires_settle = True
    memory_complexity = "O(1)"
    locality_level = LocalityLevel.EQUILIBRIUM

    def __init__(self) -> None:
        self._kernel: EqPropKernelType | None = None
        self._config: KernelConfig | None = None
        self._layers: list[torch.nn.Linear] = []
        self._device: torch.device = torch.device("cpu")
        self._dtype: torch.dtype = torch.float32
        self._beta: float = 0.5
        self._lr: float = 0.01
        self._settle_steps: int = 30
        self._gamma: float = 1.0
        self._last_settle_telemetry: dict[str, object] | None = None

    def initialize(self, config: KernelConfig) -> None:
        """Initialize backend with configuration."""
        self._config = config
        is_cuda = config.hardware in (HardwareTarget.CUDA, HardwareTarget.TRITON)  # ruff: ignore[literal-membership]
        self._device = torch.device("cuda" if is_cuda else "cpu")
        self._dtype = config.dtype

        extra = config.extra
        input_dim = extra.get("input_dim", 784)
        hidden_dim = extra.get("hidden_dim", 256)
        output_dim = extra.get("output_dim", 10)
        architecture = extra.get("architecture", "layered")
        use_spectral_norm = extra.get("use_spectral_norm", True)
        adaptive_epsilon = extra.get("adaptive_epsilon", True)
        epsilon = extra.get("epsilon", 1e-3)
        gamma = extra.get("gamma", 1.0)
        beta = extra.get("beta", 0.5)
        lr = extra.get("lr", extra.get("learning_rate", 0.01))
        max_steps = extra.get("max_steps", config.settle_steps)

        # Flatten input_dim if it's a tuple (spatial format like (C, H, W))
        if isinstance(input_dim, tuple):
            input_dim = math.prod(input_dim)

        self._beta = beta
        self._lr = lr
        self._settle_steps = max_steps
        self._gamma = gamma

        self._kernel = EqPropKernel(
            input_dim=input_dim,
            hidden_dim=hidden_dim,
            output_dim=output_dim,
            gamma=gamma,
            beta=beta,
            max_steps=max_steps,
            epsilon=epsilon,
            lr=lr,
            use_spectral_norm=use_spectral_norm,
            use_gpu=is_cuda,
            adaptive_epsilon=adaptive_epsilon,
            architecture=architecture,
        )

    def set_model_ref(
        self,
        layers: list[torch.nn.Linear],
        activation: torch.nn.Module | None = None,
    ) -> None:
        """Bind the kernel to model's layer stack for weight sync.

        This allows the kernel to use the model's actual weights instead of
        its own initialized weights. We sync the kernel's weights from the
        model's layers on initialization and back after training.
        """
        self._layers = layers
        if layers:
            self._device = layers[0].weight.device
            self._dtype = layers[0].weight.dtype

    def _sync_weights_to_kernel(self) -> None:
        """Sync PyTorch layer weights to EqPropKernel's internal weights."""
        if self._kernel is None or not self._layers:
            return

        kernel = self._kernel
        xp = kernel.xp

        if kernel.architecture == "layered" and len(self._layers) >= 2:
            self._sync_layer_to_kernel(self._layers[0], "embed", xp, kernel)
            self._sync_layer_to_kernel(self._layers[-1], "head", xp, kernel)
        elif kernel.architecture == "rnn" and len(self._layers) >= 3:
            self._sync_layer_to_kernel(self._layers[0], "W_in", xp, kernel)
            self._sync_layer_to_kernel(self._layers[1], "W_rec", xp, kernel)
            self._sync_layer_to_kernel(self._layers[-1], "W_out", xp, kernel)

    def _sync_layer_to_kernel(self, layer, key: str, xp, kernel) -> None:
        """Sync a single layer's weight and bias to kernel."""
        kernel.weights[key] = xp.asarray(layer.weight.detach().cpu().numpy())
        if layer.bias is not None:
            kernel.biases[key] = xp.asarray(layer.bias.detach().cpu().numpy())

    def _sync_weights_from_kernel(self) -> None:
        """Sync EqPropKernel's weights back to PyTorch layers."""
        if self._kernel is None or not self._layers:
            return

        kernel = self._kernel

        def to_torch(arr):
            if hasattr(arr, "get"):  # CuPy array
                arr = arr.get()
            elif hasattr(arr, "__array__"):
                arr = np.asarray(arr)
            return torch.from_numpy(arr).to(device=self._device, dtype=self._dtype)

        if kernel.architecture == "layered" and len(self._layers) >= 2:
            self._sync_layer_from_kernel(self._layers[0], "embed", to_torch, kernel)
            self._sync_layer_from_kernel(self._layers[-1], "head", to_torch, kernel)
        elif kernel.architecture == "rnn" and len(self._layers) >= 3:
            self._sync_layer_from_kernel(self._layers[0], "W_in", to_torch, kernel)
            self._sync_layer_from_kernel(self._layers[1], "W_rec", to_torch, kernel)
            self._sync_layer_from_kernel(self._layers[-1], "W_out", to_torch, kernel)

    def _numpy_to_tensor(self, arr, device=None, dtype=None):
        """Convert numpy/CuPy array to torch tensor."""
        device = device or self._device
        dtype = dtype or self._dtype
        if hasattr(arr, "get"):  # CuPy array
            arr = arr.get()
        elif hasattr(arr, "__array__"):
            arr = np.asarray(arr)
        return torch.from_numpy(arr).to(device=device, dtype=dtype)

    def _extract_activation(self, act_log, key):
        """Extract and convert activation from act_log."""
        if not act_log or key not in act_log[-1]:
            return None
        return self._numpy_to_tensor(act_log[-1][key])

    def forward(self, x: Tensor) -> tuple[Tensor, list[Tensor]]:
        """Forward pass returning output and activations (for uniform interface).

        Runs free phase equilibrium and returns logits + intermediate activations.
        """
        if self._kernel is None:
            raise RuntimeError("Backend not initialized")

        # Sync weights from model to kernel before forward
        self._sync_weights_to_kernel()

        kernel = self._kernel
        xp = kernel.xp

        # Prepare input
        x_np = x.detach().cpu().numpy()
        if kernel.use_gpu:
            x_np = xp.asarray(x_np)

        # Run free phase equilibrium
        h_free, act_log, info = kernel.solve_equilibrium(x_np)
        logits_np = kernel.compute_output(h_free)

        # Convert logits to torch
        logits = self._numpy_to_tensor(logits_np)

        # Build activations list for compatibility
        activations = [x]
        if (h := self._extract_activation(act_log, "h")) is not None:
            activations.append(h)
        if (h_next := self._extract_activation(act_log, "h_next")) is not None:
            activations.append(h_next)
        activations.append(logits)

        # Record telemetry
        self._last_settle_telemetry = {
            "free_steps": info.get("steps", 0),
            "converged": info.get("converged", False),
        }

        return logits, activations

    def backward(self, activations: list[Tensor], error: Tensor) -> dict[str, Tensor]:
        """Not used for EqProp - uses contrastive_step instead."""
        # EqProp uses contrastive Hebbian updates, not standard backward
        # This is a placeholder for the uniform interface
        return {}

    def contrastive_step(self, x: Tensor, target: Tensor) -> dict[str, float]:
        """Run full EqProp training step: free phase + nudged phase + weight update."""
        if self._kernel is None:
            raise RuntimeError("Backend not initialized")

        # Sync weights from model to kernel
        self._sync_weights_to_kernel()

        kernel = self._kernel
        xp = kernel.xp

        # Prepare inputs
        x_np = x.detach().cpu().numpy()
        y_np = target.detach().cpu().numpy()
        if kernel.use_gpu:
            x_np = xp.asarray(x_np)
            y_np = xp.asarray(y_np)

        # Run full training step (free + nudged + update)
        metrics = kernel.train_step(x_np, y_np)

        # Sync weights back to model
        self._sync_weights_from_kernel()

        # Record telemetry
        self._last_settle_telemetry = {
            "free_steps": metrics.get("free_steps", 0),
            "nudged_steps": metrics.get("nudged_steps", 0),
            "converged": True,
        }

        return {
            "loss": metrics.get("loss", 0.0),
            "accuracy": metrics.get("accuracy", 0.0),
        }

    def predict(self, x: Tensor) -> Tensor:
        """Inference: run free phase equilibrium and return logits."""
        if self._kernel is None:
            raise RuntimeError("Backend not initialized")

        self._sync_weights_to_kernel()

        kernel = self._kernel
        xp = kernel.xp

        x_np = x.detach().cpu().numpy()
        if kernel.use_gpu:
            x_np = xp.asarray(x_np)

        h_star, _, _ = kernel.solve_equilibrium(x_np)
        logits_np = kernel.compute_output(h_star)

        if hasattr(logits_np, "get"):
            logits_np = logits_np.get()
        elif hasattr(logits_np, "__array__"):
            logits_np = np.asarray(logits_np)
        logits = torch.from_numpy(logits_np).to(device=self._device, dtype=self._dtype)

        return logits

    def update_weights(self, gradients: dict[str, Tensor], lr: float) -> None:
        """Not used for EqProp - weights updated in contrastive_step."""

    def get_memory_stats(self) -> dict[str, float]:
        """Return memory usage stats."""
        if self._kernel is None:
            return {"params_mb": 0.0, "activations_mb": 0.0}

        kernel = self._kernel
        total_params = sum(w.size for w in kernel.weights.values())
        total_params += sum(b.size for b in kernel.biases.values())

        return {
            "params_mb": total_params * 4 / 1e6,
            "activations_mb": 0.0,  # O(1) memory
        }

    def get_settle_telemetry(self) -> dict[str, object] | None:
        """Return settling dynamics telemetry."""
        return self._last_settle_telemetry


# Register the backend for all HardwareTargets
for hw in HardwareTarget:
    KernelRegistry.register(AlgorithmFamily.EQPROP, hw, EqPropKernelBackend)


__all__ = ["EqPropKernelBackend"]
