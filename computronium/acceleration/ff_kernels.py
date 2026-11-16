"""Forward-Forward / PEPITA Kernel Backend.

Fused kernels for Forward-Forward goodness and PEPITA error-modulated updates.

Two rungs per family. The **store-all** rung (``forward_positive``,
``forward_negative``, ``forward_standard``, ``forward_error_modulated``,
``backward``) collects one activation list per pass and locks with it. The
**lockstep** rung (``lockstep_contrasts``) is the one ``train_step`` and
``kernel_train_step`` run: pass 1 keeps only the output, and pass 2 recomputes
both chains layer-by-layer, updating ``W_l`` before the next layer is produced.
Only the current layer's activations are live, so peak is O(B·W), flat in depth,
and the update is exact against the store-all rung because each ``W_l`` is used
once per pass before its update — the lock in
``tests/property/test_lockstep_parity.py`` holds it at ``atol=0``.

Measured on an RTX 3080 10 GiB (2026-11-16), Linear+ReLU fp32, W=512, B=4096,
L=4/8/16/32: lockstep peak is flat at 66.3 MB (Forward-Forward) and 58.5 MB
(PEPITA) — the two chains' working set — while a retained stream reaches 576.4
and 568.5 MB at L=32. ``complexity_verified`` is True for both families on that
ladder; ``activations_mb`` stays ``None`` per instance because a kernel does not
self-measure.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

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
from computronium.core.utils.activations import get_activation

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

    from computronium.ontology import System


class WeightedLayer(Protocol):
    """A dense layer the lockstep reads: callable, with weight and bias."""

    @property
    def weight(self) -> Tensor: ...

    @property
    def bias(self) -> Tensor | None: ...

    def __call__(self, x: Tensor) -> Tensor: ...


@dataclass(frozen=True, slots=True)
class LayerContrast:
    """One layer's two-pass contrast and the weight increase it implies.

    ``post_a`` is the activation of the pass the rule increases (Forward-Forward's
    positive pass, PEPITA's standard pass); ``post_b`` the pass it decreases.
    ``weight`` and ``bias`` are batch-normalized increases, so a caller applies
    ``W += lr·weight``.
    """

    layer: WeightedLayer
    post_a: Tensor
    post_b: Tensor
    weight: Tensor
    bias: Tensor


def contrast_delta(
    pre_a: Tensor, post_a: Tensor, pre_b: Tensor, post_b: Tensor
) -> Tensor:
    """Increase direction of a two-pass contrastive update.

    Forward-Forward's ``(pos − neg)`` correlation and PEPITA's
    ``(standard − error-modulated)`` correlation are the same expression on
    different chains, which is why the two families share one kernel.
    """
    return batched_outer_product(pre_a, post_a) - batched_outer_product(pre_b, post_b)


def lockstep_contrasts(
    layers: Sequence[WeightedLayer],
    chain_a: Tensor,
    chain_b: Tensor,
    activation: torch.nn.Module,
    *,
    final_activation: bool = False,
) -> Iterator[LayerContrast]:
    """Yield each layer's contrast with only the current layer's tensors live.

    The two chains advance together, so a layer's inputs exist before its
    contrast is yielded and the caller's in-place update cannot reach them. No
    activation is retained after the next layer is produced: that is the whole
    difference from the store-all rung, and the reason peak memory does not grow
    with depth.

    Args:
        layers: The dense stack, in forward order.
        chain_a: Input of the pass the rule increases.
        chain_b: Input of the pass the rule decreases.
        activation: Elementwise activation, applied to every layer but the last
            unless ``final_activation`` says a readout follows.
        final_activation: Apply ``activation`` to the last layer too. True when
            ``layers`` stops before a separate readout (PEPITA's bespoke surface).

    Yields:
        One :class:`LayerContrast` per layer, in forward order.
    """
    last = len(layers) - 1
    a, b = chain_a, chain_b
    for index, layer in enumerate(layers):
        pre_a, pre_b = a, b
        a, b = layer(pre_a), layer(pre_b)
        if index < last or final_activation:
            a, b = activation(a), activation(b)
        yield LayerContrast(
            layer=layer,
            post_a=a,
            post_b=b,
            weight=contrast_delta(pre_a, a, pre_b, b),
            bias=a.mean(dim=0) - b.mean(dim=0),
        )


def apply_contrast(contrast: LayerContrast, lr: float) -> None:
    """Apply one layer's increase immediately, before the next layer is produced."""
    with torch.no_grad():
        contrast.layer.weight.add_(lr * contrast.weight)
        if contrast.layer.bias is not None:
            contrast.layer.bias.add_(lr * contrast.bias)


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
    available = True
    complexity_verified = (
        True  # measured flat in depth on the lockstep ladder (docs/BENCHMARKS.md)
    )
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
        is_cuda = config.hardware in {HardwareTarget.CUDA, HardwareTarget.TRITON}
        self._device = torch.device("cuda" if is_cuda else "cpu")
        self._dtype = config.dtype

        extra = config.extra
        self._threshold = extra.get("threshold", 1.0)
        self._num_layers = extra.get("num_layers", 3)
        self._input_dim = extra.get("input_dim", 784)
        self._output_dim = extra.get("output_dim", 10)
        self._activation = get_activation(extra.get("activation", "relu"))

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
        """Execute one training step on the lockstep two-pass path."""
        x = self._flatten(x)
        with torch.no_grad():
            last = self._lockstep(x, y, lr=1.0)
            pos_goodness = last.post_a.pow(2).sum(dim=1).mean().item()
            neg_goodness = last.post_b.pow(2).sum(dim=1).mean().item()
            loss = neg_goodness - pos_goodness + self._threshold
            acc = (last.post_a.argmax(-1) == y).float().mean().item()
        return {"loss": loss, "accuracy": acc}

    def _flatten(self, x: Tensor) -> Tensor:
        x = x.to(device=self._device, dtype=self._dtype)
        return x.view(x.size(0), -1) if x.dim() > 2 else x

    def _labelled_inputs(self, x: Tensor, y: Tensor) -> tuple[Tensor, Tensor]:
        """Inputs with the true label and with a decoy label appended."""
        one_hot = torch.nn.functional.one_hot(y, num_classes=self._output_dim)
        one_hot = one_hot.to(device=self._device, dtype=self._dtype)
        decoy = torch.nn.functional.one_hot(
            (y + 1) % self._output_dim, num_classes=self._output_dim
        ).to(device=self._device, dtype=self._dtype)
        return torch.cat([x, one_hot], dim=1), torch.cat([x, decoy], dim=1)

    def _lockstep(self, x: Tensor, y: Tensor, lr: float) -> LayerContrast:
        """Run both passes layer-by-layer, updating each layer in place."""
        y = y.to(device=self._device)
        chain_a, chain_b = self._labelled_inputs(x, y)
        last: LayerContrast | None = None
        for contrast in lockstep_contrasts(
            self._layers, chain_a, chain_b, self._activation
        ):
            apply_contrast(contrast, lr)
            last = contrast
        if last is None:
            raise ValueError("the Forward-Forward stack binds no layers")
        return last

    def forward_positive(self, x: Tensor, y: Tensor) -> tuple[Tensor, list[Tensor]]:
        """Store-all reference: positive pass with label information.

        Args:
            x: Input [B, D_in]
            y: Labels [B]

        Returns:
            (output, activations) with label information embedded
        """
        x, _ = self._labelled_inputs(self._flatten(x), y.to(self._device))
        return self._forward_layers(x)

    def forward_negative(self, x: Tensor, y: Tensor) -> tuple[Tensor, list[Tensor]]:
        """Store-all reference: negative pass with wrong label information."""
        _, x = self._labelled_inputs(self._flatten(x), y.to(self._device))
        return self._forward_layers(x)

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

    def backward(
        self,
        pos_activations: list[Tensor],
        neg_activations: list[Tensor],
    ) -> dict[str, Tensor]:
        """Store-all reference: contrastive update from the retained passes.

        The same expression ``lockstep_contrasts`` yields, computed from
        activation lists so the two rungs can be locked against each other.

        Returns:
            Weight deltas for all layers
        """
        weight_deltas: dict[str, Tensor] = {}

        for i in range(len(self._layers)):
            pos_pre, pos_post = pos_activations[i], pos_activations[i + 1]
            neg_pre, neg_post = neg_activations[i], neg_activations[i + 1]

            weight_deltas[f"layers.{i}.weight"] = contrast_delta(
                pos_pre, pos_post, neg_pre, neg_post
            )

            if self._layers[i].bias is not None:
                weight_deltas[f"layers.{i}.bias"] = pos_post.mean(
                    dim=0
                ) - neg_post.mean(dim=0)

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

    def get_memory_stats(self) -> dict[str, float | None]:
        total_params = sum(
            p.numel() for layer in self._layers for p in layer.parameters()
        )
        return {
            "params_mb": total_params * 4 / 1e6,
            "activations_mb": None,
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

        goodness: list[float] = []
        last: LayerContrast | None = None
        with torch.no_grad():
            for contrast in lockstep_contrasts(
                self._layers, *self._labelled_inputs(x, y), self._activation
            ):
                apply_contrast(contrast, lr)
                goodness.append(
                    float(
                        (
                            contrast.post_a.pow(2).sum(dim=1)
                            - contrast.post_b.pow(2).sum(dim=1)
                            - self._threshold
                        ).mean()
                    )
                )
                last = contrast
        if last is None:
            return None

        # Forward-Forward has no single forward output for a loss; report the
        # good-versus-bad contrast so the trainer's health gate has a scalar.
        loss = -sum(goodness) / len(goodness)
        accuracy = (last.post_a.argmax(dim=1) == y).float().mean().item()
        return {"loss": loss, "accuracy": accuracy, "logits": last.post_a}

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
    available = True
    complexity_verified = (
        True  # measured flat in depth on the lockstep ladder (docs/BENCHMARKS.md)
    )
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
        is_cuda = config.hardware in {HardwareTarget.CUDA, HardwareTarget.TRITON}
        self._device = torch.device("cuda" if is_cuda else "cpu")
        self._dtype = config.dtype

        extra = config.extra
        self._scale = extra.get("feedback_matrix_scale", 1.0)
        self._activation = get_activation(extra.get("activation", "relu"))
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
        """Execute one training step on the lockstep two-pass path.

        Pass 1 keeps the standard output only (it forms the error). Pass 2
        recomputes the standard chain alongside the error-modulated one and
        updates each layer as soon as both of that layer's activations exist.
        """
        x = self._flatten(x)
        with torch.no_grad():
            standard = self._forward_last(x)
            target = self._target(y, standard)
            last = self._lockstep(x, target - standard, final_activation=False, lr=1.0)
            return {
                "loss": (standard - last.post_b).pow(2).mean().item(),
                "accuracy": (standard.argmax(-1) == y).float().mean().item(),
            }

    def _flatten(self, x: Tensor) -> Tensor:
        x = x.to(device=self._device, dtype=self._dtype)
        return x.view(x.size(0), -1) if x.dim() > 2 else x

    def _target(self, y: Tensor, output: Tensor) -> Tensor:
        if y.dim() != 1:
            return y
        one_hot = torch.nn.functional.one_hot(y, num_classes=output.shape[1])
        return one_hot.to(device=output.device, dtype=output.dtype)

    def _modulated_input(self, x: Tensor, error: Tensor) -> Tensor:
        """Backproject the output error through the fixed feedback matrix."""
        if self._feedback_matrix is None:
            raise RuntimeError("PEPITA kernel used before initialize()")
        return x + error @ self._feedback_matrix.T * self._scale

    def _forward_last(self, x: Tensor, *, final_activation: bool = False) -> Tensor:
        last = len(self._layers) - 1
        h = x
        for i, layer in enumerate(self._layers):
            h = layer(h)
            if i < last or final_activation:
                h = self._activation(h)
        return h

    def _lockstep(
        self, x: Tensor, error: Tensor, *, final_activation: bool, lr: float
    ) -> LayerContrast:
        """Run the standard and modulated chains layer-by-layer, updating in place."""
        last: LayerContrast | None = None
        for contrast in lockstep_contrasts(
            self._layers,
            x,
            self._modulated_input(x, error),
            self._activation,
            final_activation=final_activation,
        ):
            apply_contrast(contrast, lr)
            last = contrast
        if last is None:
            raise ValueError("the PEPITA stack binds no layers")
        return last

    def forward_standard(self, x: Tensor) -> tuple[Tensor, list[Tensor]]:
        """Store-all reference: standard forward pass."""
        return self._forward_layers(self._flatten(x))

    def forward_error_modulated(
        self, x: Tensor, error: Tensor
    ) -> tuple[Tensor, list[Tensor]]:
        """Store-all reference: error-modulated forward pass (PEPITA)."""
        return self._forward_layers(self._modulated_input(self._flatten(x), error))

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
    ) -> dict[str, Tensor]:
        """Store-all reference: error-modulated contrastive update.

        Each layer's increase is ``(a_std^T a_std_pre − a_mod^T a_mod_pre)/B``
        — the same expression ``lockstep_contrasts`` yields, computed from
        retained activation lists so the two rungs can be locked against each
        other. ``feedback_matrix_scale`` is not applied here: it belongs to the
        input modulation, which ``forward_error_modulated`` already carries.
        """
        weight_deltas: dict[str, Tensor] = {}

        for i in range(len(self._layers)):
            std_pre = standard_activations[i]
            std_post = standard_activations[i + 1]
            mod_pre = error_activations[i]
            mod_post = error_activations[i + 1]

            weight_deltas[f"layers.{i}.weight"] = contrast_delta(
                std_pre, std_post, mod_pre, mod_post
            )

            if self._layers[i].bias is not None:
                weight_deltas[f"layers.{i}.bias"] = std_post.mean(
                    dim=0
                ) - mod_post.mean(dim=0)

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
        It runs the lockstep rung: pass 1 keeps the output only, pass 2
        recomputes both chains and moves each layer by
        ``-lr·(a_mod − a_std)ᵀ a_pre / B`` before the next layer is produced.
        No torch optimizer and no retained activation lists.

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
        self._feedback_matrix = feedback.to(device=self._device, dtype=self._dtype)
        lr = float(getattr(model, "lr", 0.01))
        output_dim = int(getattr(model, "output_dim", self._output_dim))

        x = self._flatten(x)
        y = y.to(device=self._device)
        batch = x.shape[0]

        with torch.no_grad():
            out_s = out_layer(self._forward_last(x, final_activation=True))
            target = torch.zeros(batch, output_dim, device=x.device, dtype=self._dtype)
            target.scatter_(1, y.unsqueeze(1), 1.0)
            error = out_s - target
            last = self._lockstep(x, error, final_activation=True, lr=lr)

            out_layer.weight.sub_(lr * (error.T @ last.post_a) / batch)
            if out_layer.bias is not None:
                out_layer.bias.sub_(lr * error.mean(dim=0))

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

    def get_memory_stats(self) -> dict[str, float | None]:
        total_params = sum(
            p.numel() for layer in self._layers for p in layer.parameters()
        )
        fb_mb = 0.0
        if self._feedback_matrix is not None:
            fb_mb = self._feedback_matrix.numel() * 4 / 1e6
        return {
            "params_mb": total_params * 4 / 1e6,
            "feedback_mb": fb_mb,
            "activations_mb": None,
        }

    def get_settle_telemetry(self) -> dict[str, object] | None:
        return None


# Register backends for all HardwareTargets


# Triton kernels for fused FF/PEPITA operations
try:  # ruff: ignore[too-many-statements, too-many-statements-in-try-clause]
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

        offs_b = pid_b * BLOCK_B + tl.arange(0, BLOCK_B)

        mask_b = offs_b < B

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

        acc_pos /= B
        acc_neg /= B

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

        acc_std /= B
        acc_err /= B

        delta = lr * (acc_std - acc_err)

        grid.store_2d(delta_ptr, delta, D_in, offs_out, offs_in, mask_out, mask_in)

    HAS_TRITON_FF = True
except ImportError:
    HAS_TRITON_FF = False


__all__ = [
    "HAS_TRITON_FF",
    "FFKernelBackend",
    "LayerContrast",
    "PEPITAKernelBackend",
    "apply_contrast",
    "contrast_delta",
    "lockstep_contrasts",
]
