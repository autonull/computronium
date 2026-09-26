"""Tile Substrate Kernel Backend.

Tile-parallel contrastive kernels extending core/tile/kernels.py.
"""

from __future__ import annotations

import torch
from torch import Tensor

from computronium.acceleration.kernel_backend import (
    AlgorithmFamily,
    HardwareTarget,
    KernelConfig,
    KernelRegistry,
    LocalityLevel,
)

# ──────────────────────────────────────────────
# Triton Kernels for Tile Substrate
# ──────────────────────────────────────────────

try:
    from computronium.acceleration._tile_triton import (
        HAS_TRITON_TILE,
        _tile_activity_update_kernel,
        _tile_contrastive_update_kernel,
        _tile_hebbian_update_kernel,
        _tile_learned_routing_kernel,
        _tile_prediction_kernel,
        _tile_random_routing_kernel,
        _tile_topk_routing_kernel,
    )
except ImportError:
    HAS_TRITON_TILE = False


# ──────────────────────────────────────────────
# Multi-GPU Tile Sharding (NCCL)
# ──────────────────────────────────────────────


class TileShardedBackend:
    """Multi-GPU tile sharding via NCCL.

    Distributes tiles across GPUs, each GPU computes local updates,
    then all-reduces gradients.
    """

    def __init__(self, world_size: int, rank: int, device: torch.device) -> None:
        self.world_size = world_size
        self.rank = rank
        self.device = device
        self._process_group = None
        self._init_nccl()

    def _init_nccl(self) -> None:
        if not torch.distributed.is_initialized():
            # Single-GPU or non-distributed
            return
        self._process_group = torch.distributed.group.WORLD

    def all_reduce_gradients(self, gradients: dict[str, Tensor]) -> dict[str, Tensor]:
        """All-reduce weight gradients across GPUs."""
        if self.world_size <= 1 or self._process_group is None:
            return gradients

        reduced = {}
        for name, grad in gradients.items():
            if grad.is_cuda:
                torch.distributed.all_reduce(
                    grad, op=torch.distributed.ReduceOp.SUM, group=self._process_group
                )
                grad = grad / self.world_size  # ruff: ignore[non-augmented-assignment, redefined-loop-name]
            reduced[name] = grad
        return reduced

    def broadcast_params(self, params: dict[str, Tensor]) -> dict[str, Tensor]:
        """Broadcast parameters from rank 0 to all."""
        if self.world_size <= 1 or self._process_group is None:
            return params

        broadcast = {}
        for name, param in params.items():
            if param.is_cuda:
                torch.distributed.broadcast(param, src=0, group=self._process_group)
            broadcast[name] = param
        return broadcast


# ──────────────────────────────────────────────
# Tile Kernel Backend with Triton Acceleration
# ──────────────────────────────────────────────


class TileKernelBackend:
    """Tile substrate kernel backend.

    Implements tile-parallel contrastive learning:
    - Each tile is a local compute unit
    - Tiles communicate via message passing
    - Contrastive Hebbian updates per tile
    - Triton-accelerated kernels for GPU
    """

    name = AlgorithmFamily.TILE
    supported_dtypes = (torch.float32, torch.float16, torch.bfloat16)
    supports_autograd = False
    requires_settle = True
    memory_complexity = "O(1)"  # Per-tile O(1), global O(tiles)
    locality_level = LocalityLevel.LOCAL

    def __init__(self) -> None:
        self._config: KernelConfig | None = None
        self._num_tiles: int = 0
        self._neurons_per_tile: int = 0
        self._tiles_per_layer: int = 0
        self._num_hidden_layers: int = 0
        self._beta: float = 0.5
        self._lr: float = 0.01
        self._device: torch.device = torch.device("cpu")
        self._dtype: torch.dtype = torch.float32
        self._last_settle_telemetry: dict[str, object] | None = None
        self._sharded: TileShardedBackend | None = None

    def initialize(self, config: KernelConfig) -> None:
        self._config = config
        self._device = torch.device(
            "cuda"
            if config.hardware in (HardwareTarget.CUDA, HardwareTarget.TRITON)  # ruff: ignore[literal-membership]
            else "cpu"
        )
        self._dtype = config.dtype

        extra = config.extra
        self._neurons_per_tile = extra.get("neurons_per_tile", 32)
        self._tiles_per_layer = extra.get("tiles_per_layer", 8)
        self._num_hidden_layers = extra.get("num_hidden_layers", 3)
        self._beta = config.beta
        self._lr = config.extra.get("learning_rate", 0.01)

        self._num_tiles = self._tiles_per_layer * self._num_hidden_layers

        # Multi-GPU sharding
        if config.hardware in (HardwareTarget.CUDA, HardwareTarget.TRITON):  # ruff: ignore[literal-membership]
            world_size = extra.get("world_size", 1)
            rank = extra.get("rank", 0)
            if world_size > 1 and torch.distributed.is_initialized():
                self._sharded = TileShardedBackend(world_size, rank, self._device)

    def set_model_ref(self, tile_algorithm) -> None:
        """Set reference to TileAlgorithm instance."""
        self._tile_algo = tile_algorithm

    def _launch_activity_update(
        self,
        activity: Tensor,
        error: Tensor,
        feedback: list[Tensor],
        step_size: float,
        importance: float,
        lambda_error: float,
        clamp_min: float,
        clamp_max: float,
        clamp: bool,
    ) -> Tensor:
        """Launch fused activity update kernel."""
        B, N = activity.shape

        if HAS_TRITON_TILE and self._device.type == "cuda":
            # Stack feedback tensors
            if feedback:
                num_fb = len(feedback)
                fb_stack = torch.stack(feedback, dim=0)  # [num_fb, B, N]
                fb_ptr = fb_stack.data_ptr()
                fb_strides = torch.tensor(
                    [fb_stack.stride(0), fb_stack.stride(1), fb_stack.stride(2)],
                    device="cpu",
                    dtype=torch.int64,
                )
            else:
                num_fb = 0
                fb_ptr = 0
                fb_strides = torch.zeros(3, dtype=torch.int64)

            out = torch.empty_like(activity)
            BLOCK_B = 16
            BLOCK_N = 32
            grid = ((B + BLOCK_B - 1) // BLOCK_B, (N + BLOCK_N - 1) // BLOCK_N)

            _tile_activity_update_kernel[grid](
                activity.data_ptr(),
                error.data_ptr(),
                fb_ptr,
                fb_strides.data_ptr() if num_fb > 0 else 0,
                num_fb,
                out.data_ptr(),
                step_size,
                importance,
                lambda_error,
                clamp_min,
                clamp_max,
                clamp,
                B,
                N,
                BLOCK_B=BLOCK_B,
                BLOCK_N=BLOCK_N,
            )
            return out

        # PyTorch fallback: runs on same device as inputs (CUDA or CPU)
        from computronium.core.tile.kernels import compute_activity_update

        return compute_activity_update(
            activity=activity,
            error=error,
            fwd_feedback=feedback,
            importance=importance,
            step_size=step_size,
            lambda_error=lambda_error,
            clamp_min=clamp_min,
            clamp_max=clamp_max,
            clamp=clamp,
        )

    def _launch_prediction(
        self,
        inputs: list[Tensor],
        bias: Tensor | None,
    ) -> Tensor:
        """Launch fused prediction kernel."""
        if not inputs:
            if bias is not None:
                return (
                    bias.unsqueeze(0).expand(inputs[0].shape[0], -1)
                    if inputs
                    else bias.unsqueeze(0)
                )
            return torch.zeros(
                1, self._neurons_per_tile, device=self._device, dtype=self._dtype
            )

        B, N = inputs[0].shape

        if HAS_TRITON_TILE and self._device.type == "cuda":
            num_inputs = len(inputs)
            input_ptrs = torch.tensor(
                [inp.data_ptr() for inp in inputs], dtype=torch.int64, device="cuda"
            )
            input_strides = torch.tensor(
                [[inp.stride(0), inp.stride(1)] for inp in inputs],
                dtype=torch.int64,
                device="cuda",
            )
            bias_ptr = bias.data_ptr() if bias is not None else 0
            out = torch.empty_like(inputs[0])

            BLOCK_B = 16
            BLOCK_N = 32
            grid = ((B + BLOCK_B - 1) // BLOCK_B, (N + BLOCK_N - 1) // BLOCK_N)

            _tile_prediction_kernel[grid](
                input_ptrs,
                input_strides,
                num_inputs,
                bias_ptr,
                out.data_ptr(),
                B,
                N,
                BLOCK_B=BLOCK_B,
                BLOCK_N=BLOCK_N,
            )
            return out

        # PyTorch fallback
        from computronium.core.tile.kernels import compute_tile_prediction

        return compute_tile_prediction(inputs, bias)

    def _launch_contrastive_update(
        self,
        src_free: Tensor,
        dst_free: Tensor,
        src_nudged: Tensor,
        dst_nudged: Tensor,
        lr: float,
        beta: float,
    ) -> Tensor:
        """Launch fused contrastive Hebbian update kernel.

        Returns only the weight delta (not bias) for compatibility with the
        test harness which expects dict[str, Tensor] for grads.
        """
        B, D_in = src_free.shape
        _, D_out = dst_free.shape

        if HAS_TRITON_TILE and self._device.type == "cuda":
            delta = torch.empty(D_out, D_in, device=self._device, dtype=self._dtype)
            BLOCK_IN = 32
            BLOCK_OUT = 32
            grid = (
                (D_in + BLOCK_IN - 1) // BLOCK_IN,
                (D_out + BLOCK_OUT - 1) // BLOCK_OUT,
            )

            _tile_contrastive_update_kernel[grid](
                src_free.data_ptr(),
                dst_free.data_ptr(),
                src_nudged.data_ptr(),
                dst_nudged.data_ptr(),
                delta.data_ptr(),
                lr,
                beta,
                B,
                D_in,
                D_out,
                BLOCK_IN=BLOCK_IN,
                BLOCK_OUT=BLOCK_OUT,
            )
            return delta

        # PyTorch fallback: compute_contrastive_hebbian_update returns (weight, bias)
        # We only need the weight delta for the test harness
        from computronium.core.tile.kernels import compute_contrastive_hebbian_update

        weight_delta, _ = compute_contrastive_hebbian_update(
            src_free=src_free,
            dst_free=dst_free,
            src_nudged=src_nudged,
            dst_nudged=dst_nudged,
            learning_rate=lr,
            beta=beta,
            batch_size=B,
        )
        return weight_delta

    def _launch_hebbian_update(
        self,
        src: Tensor,
        dst: Tensor,
        weight: Tensor | None,
        importance: float,
        use_oja: bool,
    ) -> Tensor:
        """Launch fused Hebbian update kernel."""
        B, D_in = src.shape
        _, D_out = dst.shape

        if HAS_TRITON_TILE and self._device.type == "cuda":
            delta = torch.empty(D_out, D_in, device=self._device, dtype=self._dtype)
            BLOCK_IN = 32
            BLOCK_OUT = 32
            grid = (
                (D_in + BLOCK_IN - 1) // BLOCK_IN,
                (D_out + BLOCK_OUT - 1) // BLOCK_OUT,
            )

            _tile_hebbian_update_kernel[grid](
                src.data_ptr(),
                dst.data_ptr(),
                weight.data_ptr() if weight is not None and use_oja else 0,
                delta.data_ptr(),
                importance,
                B,
                D_in,
                D_out,
                BLOCK_IN=BLOCK_IN,
                BLOCK_OUT=BLOCK_OUT,
            )
            return delta

        # PyTorch fallback
        from computronium.core.tile.kernels import compute_hebbian_update

        return compute_hebbian_update(
            src_act=src, dst_err=dst, importance=importance, batch_size=B
        )

    def route_tiles(
        self,
        logits: Tensor,
        num_routes: int,
        strategy: str = "topk",
        router_weights: Tensor | None = None,
        router_bias: Tensor | None = None,
        seed: int = 42,
    ) -> tuple[Tensor, Tensor]:
        """Route tiles using specified strategy.

        Args:
            logits: Routing logits [B, num_tiles]
            num_routes: Number of tiles to route to (K)
            strategy: "topk" | "random" | "learned"
            router_weights: Optional learned router weights
            router_bias: Optional learned router bias
            seed: Random seed for stochastic routing

        Returns:
            (indices [B, K], values [B, K])
        """
        B, N = logits.shape
        device = logits.device

        indices = torch.empty(B, num_routes, dtype=torch.int64, device=device)
        values = torch.empty(B, num_routes, dtype=logits.dtype, device=device)

        if HAS_TRITON_TILE and device.type == "cuda":
            BLOCK_B = 16
            grid = ((B + BLOCK_B - 1) // BLOCK_B,)

            if strategy == "topk":
                _tile_topk_routing_kernel[grid](
                    logits.data_ptr(),
                    indices.data_ptr(),
                    values.data_ptr(),
                    B,
                    N,
                    num_routes,
                    BLOCK_B=BLOCK_B,
                )
            elif strategy == "random":
                _tile_random_routing_kernel[grid](
                    logits.data_ptr(),
                    indices.data_ptr(),
                    values.data_ptr(),
                    B,
                    N,
                    num_routes,
                    seed,
                    BLOCK_B=BLOCK_B,
                )
            elif strategy == "learned":
                router_w_ptr = (
                    router_weights.data_ptr() if router_weights is not None else 0
                )
                router_b_ptr = router_bias.data_ptr() if router_bias is not None else 0
                router_dim = (
                    router_weights.shape[0] if router_weights is not None else N
                )
                _tile_learned_routing_kernel[grid](
                    logits.data_ptr(),
                    router_w_ptr,
                    router_b_ptr,
                    indices.data_ptr(),
                    values.data_ptr(),
                    B,
                    N,
                    num_routes,
                    router_dim,
                    BLOCK_B=BLOCK_B,
                )
        # PyTorch fallback
        elif strategy == "topk":
            values, indices = torch.topk(logits, num_routes, dim=1)
        elif strategy == "random":
            gen = torch.Generator(device=device).manual_seed(seed)
            indices = torch.multinomial(
                torch.softmax(logits, dim=1), num_routes, generator=gen
            )
            values = torch.gather(logits, 1, indices)
        elif strategy == "learned":
            if router_weights is not None:
                logits = logits @ router_weights.t()  # ruff: ignore[non-augmented-assignment]
            if router_bias is not None:
                logits = logits + router_bias  # ruff: ignore[non-augmented-assignment]
            probs = torch.softmax(logits, dim=1)
            values, indices = torch.topk(probs, num_routes, dim=1)

        return indices, values

    def tile_forward(
        self,
        x: Tensor,
        tile_states: list[Tensor] | None = None,
    ) -> tuple[Tensor, list[Tensor]]:
        """Forward pass through tile substrate."""
        x = x.to(device=self._device, dtype=self._dtype)
        if x.dim() > 2:
            x = x.view(x.size(0), -1)

        batch_size = x.shape[0]

        if tile_states is None:
            tile_states = [
                torch.zeros(
                    batch_size,
                    self._neurons_per_tile,
                    device=self._device,
                    dtype=self._dtype,
                )
                for _ in range(self._num_tiles)
            ]

        current_acts = x

        for layer_idx in range(self._num_hidden_layers):
            layer_tiles = tile_states[
                layer_idx * self._tiles_per_layer : (layer_idx + 1)
                * self._tiles_per_layer
            ]

            new_tile_states = []
            for tile_idx, tile_state in enumerate(layer_tiles):
                new_state = self._tile_local_update(
                    tile_state, current_acts, layer_idx, tile_idx
                )
                new_tile_states.append(new_state)

            tile_states[
                layer_idx * self._tiles_per_layer : (layer_idx + 1)
                * self._tiles_per_layer
            ] = new_tile_states

            current_acts = torch.cat(new_tile_states, dim=1)

        return current_acts, tile_states

    def _tile_local_update(
        self,
        tile_state: Tensor,
        input_acts: Tensor,
        layer_idx: int,
        tile_idx: int,
    ) -> Tensor:
        """Single tile local update (simplified)."""
        return torch.tanh(tile_state + input_acts.mean(dim=1, keepdim=True))

    def settle(
        self,
        x: Tensor,
        beta: float = 0.0,
        steps: int = 10,
    ) -> tuple[list[Tensor], dict[str, float]]:
        """Settle tile substrate to equilibrium."""
        tile_states = None
        telemetry = {"steps": steps, "converged": False, "final_delta": 0.0}
        prev_tile_states: list[Tensor] | None = None

        for step in range(steps):
            _output, tile_states = self.tile_forward(x, tile_states)

            if step > 0 and prev_tile_states is not None:
                delta = sum(
                    (s - prev_s).abs().max().item()
                    for s, prev_s in zip(tile_states, prev_tile_states)
                )
                telemetry["final_delta"] = delta
                if delta < 1e-4:
                    telemetry["converged"] = True
                    telemetry["steps"] = step + 1
                    break

            prev_tile_states = [s.clone() for s in tile_states]

        self._last_settle_telemetry = telemetry
        return tile_states, telemetry

    def backward_contrastive(
        self,
        free_states: list[Tensor],
        nudged_states: list[Tensor],
    ) -> dict[str, Tensor]:
        """Contrastive Hebbian update for tile substrate.

        Uses Triton-accelerated kernels when available.
        """
        weight_deltas: dict[str, Tensor] = {}

        for layer_idx in range(self._num_hidden_layers):
            for tile_idx in range(self._tiles_per_layer):
                idx = layer_idx * self._tiles_per_layer + tile_idx

                free_pre = (
                    free_states[idx] if idx < len(free_states) else free_states[-1]
                )
                free_post = free_states[idx]
                nudged_pre = (
                    nudged_states[idx]
                    if idx < len(nudged_states)
                    else nudged_states[-1]
                )
                nudged_post = nudged_states[idx]

                # Use Triton-accelerated contrastive update
                delta = self._launch_contrastive_update(
                    free_pre, free_post, nudged_pre, nudged_post, self._lr, self._beta
                )

                weight_deltas[f"tiles.layer{layer_idx}.tile{tile_idx}.weight"] = delta

        # Multi-GPU all-reduce
        if self._sharded is not None:
            weight_deltas = self._sharded.all_reduce_gradients(weight_deltas)

        return weight_deltas

    def backward_hebbian(
        self,
        activations: list[Tensor],
        importance: float = 1.0,
        use_oja: bool = True,
    ) -> dict[str, Tensor]:
        """Pure Hebbian update for all tile edges."""
        weight_deltas: dict[str, Tensor] = {}

        for layer_idx in range(self._num_hidden_layers):
            for tile_idx in range(self._tiles_per_layer):
                idx = layer_idx * self._tiles_per_layer + tile_idx

                src = activations[idx] if idx < len(activations) else activations[-1]
                dst = (
                    activations[idx + 1]
                    if idx + 1 < len(activations)
                    else activations[-1]
                )

                weight = None
                if hasattr(self, "_tile_algo") and self._tile_algo is not None:
                    # Get weight from tile algorithm
                    src_id = (
                        layer_idx * self._tiles_per_layer
                        + tile_idx
                        - self._tiles_per_layer
                    )
                    dst_id = idx
                    if src_id >= 0 and hasattr(self._tile_algo, "_weight_lookup"):
                        weight = self._tile_algo._weight_lookup(src_id, dst_id)

                delta = self._launch_hebbian_update(
                    src, dst, weight, importance, use_oja
                )
                weight_deltas[f"tiles.layer{layer_idx}.tile{tile_idx}.weight"] = delta

        if self._sharded is not None:
            weight_deltas = self._sharded.all_reduce_gradients(weight_deltas)

        return weight_deltas

    def update_weights(self, gradients: dict[str, Tensor], lr: float = 1.0) -> None:
        """Apply weight updates to tile algorithm."""
        if hasattr(self, "_tile_algo") and self._tile_algo is not None:
            self._tile_algo.apply_weight_updates(gradients, lr)

    def get_memory_stats(self) -> dict[str, float]:
        tile_params = self._num_tiles * self._neurons_per_tile * self._neurons_per_tile
        state_mb = self._num_tiles * self._neurons_per_tile * 4 / 1e6

        return {
            "tile_params_mb": tile_params * 4 / 1e6,
            "tile_states_mb": state_mb,
            "activations_mb": 0.0,
        }

    def get_settle_telemetry(self) -> dict[str, object] | None:
        return self._last_settle_telemetry


# Register backend for all HardwareTargets
for hw in HardwareTarget:
    KernelRegistry.register(AlgorithmFamily.TILE, hw, TileKernelBackend)


__all__ = [
    "HAS_TRITON_TILE",
    "TileKernelBackend",
    "TileShardedBackend",
]
