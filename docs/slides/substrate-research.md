# Substrate & Hardware Research

<div class="research-header">
  <span class="research-badge">⚡ Substrate</span>
  <h2>Quantization, noise, neuromorphic, photonic, memristive refinement</h2>
  <p class="research-lead">Precision bounds · Error accumulation · Resource-aware complexity · Physical deployment</p>
</div>

## Scope

The **substrate axis (S)** defines the physical state space: precision, noise, sparsity, and device physics. This research path connects abstract computation to constrained implementations.

## Substrate Primitives (<!-- gen:substrate_count --> available)

| Primitive | Precision | Noise Model | Sparsity | Target Hardware |
|-----------|-----------|-------------|----------|-----------------|
| `Float32` | 32-bit FP | None | Dense | CPU/GPU (reference) |
| `Float16` | 16-bit FP | None | Dense | GPU Tensor Cores |
| `BFloat16` | 16-bit BF | None | Dense | TPU/GPU |
| `Int8` | 8-bit int | Quantization | Structured | Edge accelerators |
| `Int4` | 4-bit int | Quantization | Structured | Ultra-low-power |
| `Ternary` | {-1,0,1} | None | High | Neuromorphic |
| `Binary` | {-1,1} | None | High | In-memory compute |
| `Stochastic` | Analog | Gaussian/Poisson | Configurable | Memristive/photonic |
| `Spiking` | Event-based | Shot noise | Sparse | Neuromorphic (Loihi, SpiNNaker) |

> Substrates available today: <!-- gen:substrate_list -->.

## Key Research Projects

### F13: Precision, Noise, and Substrate Refinement
- **F13.1**: Quantization error bounds — discrepancy between ideal and quantized transition
- **F13.2**: Error accumulation — propagation of local numerical errors over repeated transitions
- **F13.3**: Robustness margins — bounded perturbations cannot change discrete decisions with sufficient margin
- **F13.4**: Noisy-state probability bounds — deviation from ideal behavior under stochastic model
- **F13.5**: Resource-aware refinement — abstract machine cost vs. concrete implementation cost model

### F12: Coupled Dynamics Stability (Substrate-Aware)
- **F12.5**: Coupling effects — when adding plasticity preserves/invalidates stability
- **F13.6**: Substrate-specific stability — Lyapunov analysis under quantization/noise

### F16: Complexity of Simulation & Execution
- **F16.1**: Step simulation bounds — target transitions per simulated source transition
- **F16.2**: Space bounds — source-machine space vs. target-machine state/memory
- **F16.3**: Encoding overhead — representation size of source program/configuration
- **F16.4**: Restricted-access overhead — cost of indirect addressing/conditional selection with available ops
- **F16.5**: Lower bounds — under explicitly defined machine models

## Substrate-Specific Research Questions

### Digital Finite-Precision (Int8, Int4, Float16)
- Quantization-aware training vs. post-training quantization
- Accumulator precision requirements for credit computation
- Kernel parity verification at each precision level

### Neuromorphic / Spiking
- Event-driven settle vs. frame-based settle
- Spike-based credit assignment (surrogate gradients)
- Latency-energy-accuracy Pareto frontiers

### Memristive / Analog In-Memory Compute
- Conductance drift and programming noise models
- Analog settling dynamics as StateDynamics primitive
- Endurance-aware plasticity (write cycling in ψ vs. θ)

### Photonic
- Phase/amplitude noise models
- Thermal crosstalk as structured noise
- Latency advantages for specific StateDynamics (e.g., energy minimization)

## Connection to Other Paths

| Path | Connection |
|------|------------|
| **Formal Proof** | F13: Refinement theorems, error bounds, resource-aware complexity |
| **Z3 Research** | Finite-precision universality (F5 variant 4), hardware Z3 benchmark |
| **Metadynamics** | Substrate-coupled plasticity, noise robustness (F12.5, F12.6) |
| **Learning Theory** | Quantization-aware adaptation, noisy credit guarantees |

## Current Status

- **Kernel Ladder**: Verified kernels at each rung (`reference_only`, `kernel_unverified`, `kernel_verified`)
- **Implementation Matrix**: <!-- gen:kernel_verified_count --> verified, <!-- gen:kernel_unverified_count --> unverified, <!-- gen:reference_only_count --> reference-only
- **Export Targets**: Loihi (neuromorphic), FPGA (digital), ONNX (portable)
- **Documentation**: `docs/kernel_backend_guide.md`, `docs/tutorials/export_loihi.md`, `docs/tutorials/export_fpga.md`, `docs/hardware_targets.md`

## Next Steps

1. **Formalize** quantization error model for a reference StateDynamics (F13.1)
2. **Verify** kernel parity for Int8/Int4 substrates (move to `kernel_verified`)
3. **Characterize** neuromorphic settle dynamics as StateDynamics primitive
4. **Build** resource-aware cost model linking abstract transitions to hardware cycles/energy
5. **Extend** Z3 benchmark to run on physical neuromorphic hardware

> No physical-hardware superiority is claimed. Neuromorphic, memristive, and photonic paths are validated in simulation until they run on silicon.

<!-- notes -->
The substrate axis is where physical constraints become first-class. The kernel ladder ensures we don't claim acceleration without verification. The research here is about refinement theorems: connecting the abstract six-axis machine to concrete hardware with explicit error and cost bounds.
<!-- /notes -->