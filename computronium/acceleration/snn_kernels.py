"""Spiking STDP Kernel Backend.

LIF dynamics + 3-factor STDP kernels for neuromorphic acceleration.
"""

from __future__ import annotations

import torch
from torch import Tensor

from computronium.acceleration.contrastive_primitives import (
    contrastive_delta,
    lif_step,
    stdp_update,
)
from computronium.acceleration.kernel_backend import (
    AlgorithmFamily,
    HardwareTarget,
    KernelConfig,
    LocalityLevel,
)


class SNNKernelBackend:
    """Spiking STDP kernel backend.

    Implements:
    - LIF neuron dynamics
    - 3-factor STDP (pre * post * modulator)
    - Event-driven contrastive updates
    """

    name = AlgorithmFamily.SNN
    supported_dtypes = (torch.float32, torch.float16, torch.bfloat16)
    supports_autograd = False
    requires_settle = True  # Time-stepped simulation
    memory_complexity = "O(T)"  # T time steps
    locality_level = LocalityLevel.LOCAL

    def __init__(self) -> None:
        self._config: KernelConfig | None = None
        self._layers: list[torch.nn.Linear] = []
        self._num_steps: int = 100
        self._tau_mem: float = 20.0
        self._tau_syn: float = 5.0
        self._threshold: float = 1.0
        self._refractory: float = 2.0
        self._dt: float = 1.0
        self._device: torch.device = torch.device("cpu")
        self._dtype: torch.dtype = torch.float32
        self._spike_grad: str = "surrogate"
        self._last_settle_telemetry: dict[str, object] | None = None

    def initialize(self, config: KernelConfig) -> None:
        self._config = config
        self._device = torch.device(
            "cuda"
            if config.hardware in (HardwareTarget.CUDA, HardwareTarget.TRITON)  # ruff: ignore[literal-membership]
            else "cpu"
        )
        self._dtype = config.dtype

        extra = config.extra
        self._num_steps = extra.get("num_steps", 100)
        self._tau_mem = extra.get("tau_mem", 20.0)
        self._tau_syn = extra.get("tau_syn", 5.0)
        self._threshold = extra.get("spike_threshold", 1.0)
        self._refractory = extra.get("refractory_period", 2.0)
        self._dt = extra.get("dt", 1.0)
        self._spike_grad = extra.get("spike_grad", "surrogate")

    def set_model_ref(self, layers: list[torch.nn.Linear]) -> None:
        self._layers = layers

    def simulate(  # ruff: ignore[too-many-locals]
        self,
        x: Tensor,
        y: Tensor | None = None,
        neuromodulator: Tensor | None = None,
    ) -> tuple[list[Tensor], list[Tensor], dict[str, float]]:
        """Run SNN simulation for num_steps.

        Args:
            x: Input [B, D_in] (spike rates or continuous)
            y: Target labels [B]
            neuromodulator: 3rd factor signal [B, D_out] (for supervised STDP)

        Returns:
            (spike_trains, voltage_traces, telemetry)
            spike_trains: List of [B, N, T] per layer
            voltage_traces: List of [B, N, T] per layer
        """
        x = x.to(device=self._device, dtype=self._dtype)
        if x.dim() > 2:
            x = x.view(x.size(0), -1)

        batch_size = x.shape[0]
        num_layers = len(self._layers)

        # Initialize state variables per layer
        v_list = []  # Membrane potential [B, N]
        i_syn_list = []  # Synaptic current [B, N]
        spike_trains = []  # List of [B, N, T]
        voltage_traces = []

        # Layer 0: input encoding (Poisson or rate)
        # For simplicity, treat input as spike rate
        v = torch.zeros(
            batch_size,
            self._layers[0].in_features,
            device=self._device,
            dtype=self._dtype,
        )
        i_syn = torch.zeros_like(v)
        v_list.append(v)
        i_syn_list.append(i_syn)

        # Hidden/output layers
        for layer in self._layers:
            v = torch.zeros(
                batch_size, layer.out_features, device=self._device, dtype=self._dtype
            )
            i_syn = torch.zeros_like(v)
            v_list.append(v)
            i_syn_list.append(i_syn)

        # Storage (per-layer width: layer 0 is the input layer, layers 1..N
        # use each Linear layer's out_features).
        widths = [v_list[0].shape[1]] + [layer.out_features for layer in self._layers]
        for width in widths:
            spike_trains.append(
                torch.zeros(
                    batch_size,
                    width,
                    self._num_steps,
                    device=self._device,
                    dtype=self._dtype,
                )
            )
            voltage_traces.append(
                torch.zeros(
                    batch_size,
                    width,
                    self._num_steps,
                    device=self._device,
                    dtype=self._dtype,
                )
            )

        # Refractory state
        refractory_count = [torch.zeros_like(v) for v in v_list]

        # Simulation loop
        for t in range(self._num_steps):
            # Input layer: generate spikes from input rate
            input_spikes = (
                torch.bernoulli(x * self._dt) if x.max() <= 1.0 else (x > 0).float()
            )
            spike_trains[0][:, :, t] = input_spikes

            # Current injection to first layer
            i_syn_list[1] += input_spikes @ self._layers[0].weight.data.T * self._dt
            if self._layers[0].bias is not None:
                i_syn_list[1] += self._layers[0].bias.data * self._dt

            # Process each layer
            for layer_idx in range(1, num_layers + 1):
                v = v_list[layer_idx]
                i_syn = i_syn_list[layer_idx]

                # Refractory handling
                v = torch.where(refractory_count[layer_idx] > 0, torch.zeros_like(v), v)

                # LIF step
                v_new, i_syn_new, spikes = lif_step(
                    v, i_syn, self._tau_mem, self._tau_syn, self._threshold, self._dt
                )

                # Update refractory
                refractory_count[layer_idx] = torch.where(
                    spikes > 0,
                    torch.full_like(
                        refractory_count[layer_idx], self._refractory / self._dt
                    ),
                    torch.clamp(refractory_count[layer_idx] - 1, min=0),
                )

                # Store
                spike_trains[layer_idx][:, :, t] = spikes
                voltage_traces[layer_idx][:, :, t] = v_new

                v_list[layer_idx] = v_new
                i_syn_list[layer_idx] = i_syn_new

                # Propagate to next layer
                if layer_idx < num_layers:
                    i_syn_list[layer_idx + 1] += (
                        spikes @ self._layers[layer_idx].weight.data.T * self._dt
                    )
                    if self._layers[layer_idx].bias is not None:
                        i_syn_list[layer_idx + 1] += (
                            self._layers[layer_idx].bias.data * self._dt
                        )

        telemetry = {
            "num_steps": self._num_steps,
            "mean_firing_rate": sum(s.mean().item() for s in spike_trains)
            / len(spike_trains),
            "total_spikes": sum(s.sum().item() for s in spike_trains),
        }
        self._last_settle_telemetry = telemetry

        return spike_trains, voltage_traces, telemetry

    def stdp_update(
        self,
        pre_spikes: Tensor,
        post_spikes: Tensor,
        modulator: Tensor | None = None,
        layer_idx: int = 0,
    ) -> dict[str, Tensor]:
        """Compute STDP weight update for one layer.

        Args:
            pre_spikes: Pre-synaptic spikes [B, N_pre, T]
            post_spikes: Post-synaptic spikes [B, N_post, T]
            modulator: Optional 3rd factor [B, N_post] (broadcast over time)
            layer_idx: Layer index

        Returns:
            Weight delta dict
        """
        # STDP correlation
        delta = stdp_update(
            pre_spikes,
            post_spikes,
            tau_plus=20.0,
            tau_minus=20.0,
            A_plus=0.01,
            A_minus=0.01,
        )

        # Apply 3-factor modulation if provided
        if modulator is not None:
            # Modulator per post-synaptic neuron, broadcast to pre
            mod_expanded = modulator.mean(dim=0).unsqueeze(1)  # [N_post, 1]
            delta = delta * mod_expanded  # ruff: ignore[non-augmented-assignment]

        return {f"layers.{layer_idx}.weight": delta}

    def backward_contrastive(
        self,
        free_spikes: list[Tensor],
        nudged_spikes: list[Tensor],
        beta: float,
    ) -> dict[str, Tensor]:
        """Contrastive STDP: free vs nudged phase spike trains.

        Args:
            free_spikes: List of spike trains from free phase
            nudged_spikes: List of spike trains from nudged phase (with target)
            beta: Nudge strength

        Returns:
            Contrastive weight deltas
        """
        weight_deltas: dict[str, Tensor] = {}

        for i in range(len(self._layers)):
            pre_free = free_spikes[i]
            post_free = free_spikes[i + 1]
            pre_nudged = nudged_spikes[i]
            post_nudged = nudged_spikes[i + 1]

            # STDP on free phase
            free_delta = stdp_update(pre_free, post_free)

            # STDP on nudged phase
            nudged_delta = stdp_update(pre_nudged, post_nudged)

            # Contrastive delta
            delta = contrastive_delta(free_delta, nudged_delta, beta)
            weight_deltas[f"layers.{i}.weight"] = delta

        return weight_deltas

    def update_weights(self, gradients: dict[str, Tensor], lr: float) -> None:
        with torch.no_grad():
            for name, grad in gradients.items():
                if "weight" in name:
                    layer_idx = int(name.split(".")[1])
                    self._layers[layer_idx].weight.add_(lr * grad)

    def get_memory_stats(self) -> dict[str, float]:
        total_params = sum(
            p.numel() for layer in self._layers for p in layer.parameters()
        )
        # Spike train memory: B * N * T * 1 byte (bool) per layer
        spike_mb = 0.0
        if self._config is not None:
            extra = self._config.extra
            batch_size = extra.get("batch_size", 64)
            hidden_dim = extra.get("hidden_dim", 256)
            spike_mb = (
                batch_size
                * hidden_dim
                * self._num_steps
                * (len(self._layers) + 1)
                / 1e6
            )

        return {
            "params_mb": total_params * 4 / 1e6,
            "spike_trains_mb": spike_mb,
            "activations_mb": 0.0,
        }

    def get_settle_telemetry(self) -> dict[str, object] | None:
        """Return the most recent SNN simulation's telemetry, if any."""
        return self._last_settle_telemetry


# Register backend for all HardwareTargets


# Triton kernels for fused SNN operations
try:  # noqa: PLR0915
    import triton
    import triton.language as tl

    from computronium.acceleration import grid

    @triton.jit
    def _lif_step_kernel(  # ruff: ignore[too-many-arguments, too-many-positional-arguments]
        v_ptr,
        i_syn_ptr,
        spikes_ptr,
        tau_mem,
        tau_syn,
        threshold,
        dt,
        B,
        N,
        BLOCK_B: tl.constexpr,
        BLOCK_N: tl.constexpr,
    ):
        """Fused LIF neuron step."""
        pid_b = tl.program_id(0)
        pid_n = tl.program_id(1)

        offs_b = pid_b * BLOCK_B + tl.arange(0, BLOCK_B)
        offs_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)

        mask_b = offs_b < B
        mask_n = offs_n < N

        v = tl.load(
            v_ptr + offs_b[:, None] * N + offs_n[None, :],
            mask=mask_b[:, None] & mask_n[None, :],
            other=0.0,
        )
        i_syn = tl.load(
            i_syn_ptr + offs_b[:, None] * N + offs_n[None, :],
            mask=mask_b[:, None] & mask_n[None, :],
            other=0.0,
        )

        # dv/dt = -v/tau_mem + I_syn
        v_new = v + dt * (-v / tau_mem + i_syn)

        # dI/dt = -I/tau_syn
        i_syn_new = i_syn * (1.0 - dt / tau_syn)

        # Spike generation
        spikes = (v_new > threshold).to(tl.float32)

        # Reset membrane potential after spike
        v_new = tl.where(spikes > 0, 0.0, v_new)

        # Add spikes to synaptic current
        i_syn_new = i_syn_new + spikes  # ruff: ignore[non-augmented-assignment]

        tl.store(
            v_ptr + offs_b[:, None] * N + offs_n[None, :],
            v_new,
            mask=mask_b[:, None] & mask_n[None, :],
        )
        tl.store(
            i_syn_ptr + offs_b[:, None] * N + offs_n[None, :],
            i_syn_new,
            mask=mask_b[:, None] & mask_n[None, :],
        )
        tl.store(
            spikes_ptr + offs_b[:, None] * N + offs_n[None, :],
            spikes,
            mask=mask_b[:, None] & mask_n[None, :],
        )

    @triton.jit
    def _stdp_phase_delta(  # ruff: ignore[too-many-arguments, too-many-positional-arguments]
        pre_ptr,
        post_ptr,
        B,
        N_pre,
        N_post,
        T,
        A_plus,
        A_minus,
        offs_pre,
        offs_post,
        mask_pre,
        mask_post,
        offs_t,
        mask_t,
        BLOCK_PRE: tl.constexpr,
        BLOCK_POST: tl.constexpr,
        BLOCK_T: tl.constexpr,
    ):
        """One phase's spike-timing correlation, as a ``[BLOCK_POST, BLOCK_PRE]`` tile.

        The time axis is a tile rather than a loop: each operand is loaded once
        as ``[N, BLOCK_T]`` and the correlation is a reduction over that axis.

        A loop over ``t`` with a ``[BLOCK_POST, 1]`` by ``[1, BLOCK_PRE]``
        broadcast is the obvious formulation and it is **wrong on triton 3.8**:
        the compiled kernel leaks values across both tile axes, so an
        all-but-one-silent train produces a non-zero block where the reference
        produces one element. Broadcasting the two operands to explicit 2-D tiles
        is exact, and it is also the faster form because the dynamic inner loop
        is gone.
        """
        acc = tl.zeros((BLOCK_POST, BLOCK_PRE), dtype=tl.float32)
        mask_post_t = mask_post[:, None] & mask_t[None, :]
        mask_pre_t = mask_pre[:, None] & mask_t[None, :]
        for b in range(B):
            pre_row = pre_ptr + b * N_pre * T + offs_pre[:, None] * T
            post_row = post_ptr + b * N_post * T + offs_post[:, None] * T
            # LTP: post fires at t+1, pre at t.  LTD: post at t, pre at t+1.
            ltp = tl.sum(
                tl.load(post_row + (offs_t + 1)[None, :], mask=mask_post_t, other=0.0)[
                    :, None, :
                ]
                * tl.load(pre_row + offs_t[None, :], mask=mask_pre_t, other=0.0)[
                    None, :, :
                ],
                axis=2,
            )
            ltd = tl.sum(
                tl.load(post_row + offs_t[None, :], mask=mask_post_t, other=0.0)[
                    :, None, :
                ]
                * tl.load(pre_row + (offs_t + 1)[None, :], mask=mask_pre_t, other=0.0)[
                    None, :, :
                ],
                axis=2,
            )
            acc += A_plus * ltp - A_minus * ltd  # ruff: ignore[non-augmented-assignment]
        return acc

    @triton.jit
    def _stdp_update_kernel(  # ruff: ignore[too-many-arguments, too-many-positional-arguments]
        pre_spikes_ptr,
        post_spikes_ptr,
        delta_ptr,
        B,
        N_pre,
        N_post,
        T,
        A_plus,
        A_minus,
        BLOCK_PRE: tl.constexpr,
        BLOCK_POST: tl.constexpr,
        BLOCK_T: tl.constexpr,
    ):
        """Spike-timing correlation: dW = A_plus * ltp - A_minus * ltd.

        Equal to `contrastive_primitives.stdp_update`, which is the specification
        (TODO36 §4.5). Two things this kernel got wrong for its whole life, both
        recorded here because the fixed form is the one that looks obvious:

        * it read **no batch** — the loads address ``offs * T + t`` with no batch
          stride, so one sample's correlation was returned for the whole batch;
        * its two branches loaded **each other's** time step, so ``A_plus`` and
          ``A_minus`` landed on the wrong terms and every weight delta had the
          sign of a depression rather than a potentiation.

        There is no ``tl.dot`` here and there never should have been: the
        correlation is a rank-1 product accumulated over time, and ``tl.dot``
        refuses a contraction of length 1 — which is why this kernel did not
        compile until its specification existed.

        Launch with ``grid = (cdiv(N_pre, BLOCK_PRE), cdiv(N_post, BLOCK_POST))``:
        the grid is row-major over ``delta``'s own ``[N_post, N_pre]`` layout.
        """
        offs_post, offs_pre, mask_post, mask_pre = grid.tile_2d(
            N_post, N_pre, BLOCK_POST, BLOCK_PRE
        )
        offs_t = tl.arange(0, BLOCK_T)

        delta = _stdp_phase_delta(
            pre_spikes_ptr,
            post_spikes_ptr,
            B,
            N_pre,
            N_post,
            T,
            A_plus,
            A_minus,
            offs_pre,
            offs_post,
            offs_pre < N_pre,
            offs_post < N_post,
            offs_t,
            offs_t < T - 1,
            BLOCK_PRE,
            BLOCK_POST,
            BLOCK_T,
        )

        grid.store_2d(delta_ptr, delta, N_pre, offs_post, offs_pre, mask_post, mask_pre)

    @triton.jit
    def _contrastive_stdp_kernel(  # ruff: ignore[too-many-arguments, too-many-positional-arguments]
        pre_free_ptr,
        post_free_ptr,
        pre_nudged_ptr,
        post_nudged_ptr,
        delta_ptr,
        B,
        N_pre,
        N_post,
        T,
        A_plus,
        A_minus,
        beta,
        BLOCK_PRE: tl.constexpr,
        BLOCK_POST: tl.constexpr,
        BLOCK_T: tl.constexpr,
    ):
        """Contrastive STDP: dW = (stdp(nudged) - stdp(free)) / beta.

        The same composition as `contrastive_hebbian_update` — a phase term,
        differenced, divided by the nudge strength — with a spike-timing
        correlation as the phase term instead of a batched outer product
        (TODO36 §4.5).

        ``A_plus``/``A_minus`` were not parameters of this kernel and it summed
        both orderings into one unsigned term. A contrastive rule whose phase term
        is not the rule it contrasts is a different rule, so the amplitudes are
        here and the two orderings keep their signs.

        Launch with ``grid = (cdiv(N_pre, BLOCK_PRE), cdiv(N_post, BLOCK_POST))``:
        the grid is row-major over ``delta``'s own ``[N_post, N_pre]`` layout.
        """
        offs_post, offs_pre, mask_post, mask_pre = grid.tile_2d(
            N_post, N_pre, BLOCK_POST, BLOCK_PRE
        )
        offs_t = tl.arange(0, BLOCK_T)
        mask_t = offs_t < T - 1

        free = _stdp_phase_delta(
            pre_free_ptr,
            post_free_ptr,
            B,
            N_pre,
            N_post,
            T,
            A_plus,
            A_minus,
            offs_pre,
            offs_post,
            mask_pre,
            mask_post,
            offs_t,
            mask_t,
            BLOCK_PRE,
            BLOCK_POST,
            BLOCK_T,
        )
        nudged = _stdp_phase_delta(
            pre_nudged_ptr,
            post_nudged_ptr,
            B,
            N_pre,
            N_post,
            T,
            A_plus,
            A_minus,
            offs_pre,
            offs_post,
            mask_pre,
            mask_post,
            offs_t,
            mask_t,
            BLOCK_PRE,
            BLOCK_POST,
            BLOCK_T,
        )

        grid.store_2d(
            delta_ptr,
            (nudged - free) / beta,
            N_pre,
            offs_post,
            offs_pre,
            mask_post,
            mask_pre,
        )


except ImportError:
    pass


__all__ = ["SNNKernelBackend"]
