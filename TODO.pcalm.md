# PC-ALM Integration into Computronium — Research & Development Plan

**Objective:** Fully absorb "Augmented Lagrangian Predictive Coding" (PC-ALM, Sakana AI, 2026, arXiv:2605.31022) into Computronium's 6-D ontology (S ⊗ G ⊗ D ⊗ M ⊗ C ⊗ U). This plan maps PC-ALM's algorithmic primitives to existing Computronium components, identifies extension points, and defines a concrete implementation path leveraging the stack's acceleration, validation, and experiment infrastructure.

---

## 1. Algorithmic Absorption: Mapping PC-ALM to the 6-D Ontology

PC-ALM replaces global backprop with **layer-local primal–dual dynamical systems**. Each layer `l` maintains:
- **Primal state** `h_l` (activations)
- **Dual state** `λ_l` (Lagrange multipliers / PI controller state)

The augmented Lagrangian for layer `l`:
```
L_ρ = Σ_l [ ½‖h_l - f_θ_l(h_{l-1})‖² ] + Σ_l ⟨λ_l, h_l - f_θ_l(h_{l-1})⟩ + (ρ/2) Σ_l ‖h_l - f_θ_l(h_{l-1})‖²
```

**Dynamics (continuous time):**
```
ḣ_l = -∂L_ρ/∂h_l  = -(h_l - f_θ_l(h_{l-1})) - λ_l - ρ(h_l - f_θ_l(h_{l-1})) + (J_f^{l+1})^T [h_{l+1} - f_{l+1}(h_l) + λ_{l+1} + ρ(h_{l+1} - f_{l+1}(h_l))]
λ̇_l =  h_l - f_θ_l(h_{l-1})       # PI controller: integral of constraint violation
```

**Weight update (local Hebbian):**
```
ΔW_l ∝ -λ_l h_{l-1}^T
```

### 1.1 Ontology Mapping

| PC-ALM Primitive | Computronium Axis | Existing Component | Extension Required |
|------------------|-------------------|-------------------|-------------------|
| Primal states `h_l` | **D** (StateDynamics) | `StateDynamics.settle` returns `activations` list | Add dual state `λ` tracking alongside `h` |
| Dual states `λ_l` | **D** + **M** (Plasticity) | `PlasticityConfig.fast_weights` / `routing` | New `PCALMDynamics` with persistent `λ` buffer |
| PI controller (λ̇ = constraint) | **D** | `StateDynamics` step loop | Implement in `settle` iteration |
| Local weight update `ΔW ∝ -λ h^T` | **C** (CreditAssignment) | `CreditAssignment.compute_pseudo_gradient` | New `PCALMCredit` using `λ` from dynamics |
| Penalty parameter `ρ` | **D** config | `StateDynamicsConfig.step_size` / `beta` | Add `rho` to `StateDynamicsConfig` |
| Inference budget `T` | **D** config | `StateDynamicsConfig.max_steps` | Reuse; add adaptive stopping |
| Layer-local settlement | **G** (Geometry) | `FeedforwardGeometry` / `layer_stack` | Requires layered geometry (already supported) |

**Key insight:** PC-ALM fits naturally as a **new `StateDynamics` variant** (`PCALMDynamics`) paired with a **new `CreditAssignment` variant** (`PCALMCredit`). The dual variables `λ` are persistent state across the relaxation phase — exactly what the `Plasticity` axis (`M`) or dynamics-internal buffers are designed for.

---

## 2. Component Integration: Concrete Extension Points

### 2.1 New `PCALMDynamics` in `computronium/ontology/dynamics/_dynamics.py`

```python
# Add to StateDynamicsConfig classmethods
@classmethod
def pc_alm(
    cls,
    *,
    max_steps: int = 30,
    convergence_threshold: float = 1e-4,
    convergence_start: int = 5,
    step_size: float = 0.1,
    beta: float = 0.5,
    rho: float = 1.0,           # Augmented Lagrangian penalty
    momentum: float = 0.0,
    track_free_energy_per_iter: bool = False,
    compiled: bool = False,
) -> StateDynamicsConfig:
    return cls(
        dynamics_type="pc_alm",
        max_steps=max_steps,
        convergence_threshold=convergence_threshold,
        convergence_start=convergence_start,
        step_size=step_size,
        beta=beta,
        momentum=momentum,
        track_free_energy_per_iter=track_free_energy_per_iter,
        compiled=compiled,
        # Store rho in a new field or repurpose momentum for rho
    )
```

**Registry entry** in `computronium/ontology/dynamics/__init__.py`:
```python
DYNAMICS_REGISTRY: Final[dict[str, type[StateDynamics]]] = {
    ...
    "pc_alm": PCALMDynamics,
    ...
}
```

**`PCALMDynamics` class structure** (extends `StateDynamics` Protocol):
- **State buffer**: `self._dual_vars: list[Tensor]` — persistent `λ` across `settle` calls (reset each train step)
- **`settle`**: Runs the primal–dual loop for `max_steps` iterations:
  1. Initialize `h` from feedforward pass (or cached)
  2. Initialize `λ = 0` (or warm-start from previous step)
  3. For `t in range(max_steps)`:
     - Compute constraint violations `c_l = h_l - f_θ_l(h_{l-1})`
     - Update dual: `λ_l ← λ_l + step_size * c_l`
     - Update primal: `h_l ← h_l - step_size * (c_l + λ_l + ρ * c_l - J^T * (c_{l+1} + λ_{l+1} + ρ * c_{l+1}))`
  4. Return settled state with `activations = h_list`, store `λ` for credit
- **`compute_energy`**: Augmented Lagrangian value at settled state

**Integration with `SubstrateSettleKernel`**: The existing kernel (`computronium/ontology/_settle_kernel.py`) handles layered Jacobi updates. PC-ALM needs a **custom kernel** (or extended `SubstrateSettleKernel`) that:
- Maintains dual variables `λ` per layer
- Computes Jacobian-transpose-vector products for the backward coupling term `(J_f^{l+1})^T * ...`
- Fuses the entire `T`-step loop into one kernel launch (see §3)

### 2.2 New `PCALMCredit` in `computronium/ontology/credit.py`

```python
class PCALMCredit:
    """PC-ALM local credit assignment: ΔW_l = -η * λ_l @ h_{l-1}^T / B."""
    
    phases: ClassVar[tuple[Phase, ...]] = (Phase.FREE, Phase.NUDGED)
    requires_autograd: ClassVar[bool] = False  # Local rule, no autograd through settle
    
    IDENTITY_CARD = AlgorithmIdentityCard(
        name="PCALMCredit",
        reference_equations=(
            "Augmented Lagrangian Predictive Coding; Seely & Gould (2026), "
            "arXiv:2605.31022: ΔW_l ∝ -λ_l h_{l-1}^T"
        ),
        deviations_from_literature=(
            "dual variables λ carried by dynamics, not recomputed here",
            "optional credit_norm normalization (relative/rms/spectral)",
        ),
        objective_function="Augmented Lagrangian L_ρ at settled state",
        pseudo_gradient_def="ΔW_l = -λ_l @ h_{l-1}^T / (batch * β_dual)",
        symmetry_requirements=("none (local rule)",),
        approximation_parameters=("rho", "beta_dual"),
        validated_limits=(
            "gradient-equivalence vs BP cosine ≥ 0.8 at depth 100 (paper claim)",
            "depth-1000 trainable with proper initialization (Innocenti et al. 2026)",
        ),
    )
    
    def __init__(self, config: CreditAssignmentConfig | None = None):
        self.config = config or CreditAssignmentConfig.thermodynamic_contrast()
        # Reuse beta as dual learning rate scale
    
    def compute_pseudo_gradient(
        self,
        states: Mapping[Phase, SystemState],
        loss: Tensor | None,
        geometry: Geometry,
    ) -> list[Tensor]:
        # λ is stored in dynamics instance after settle; access via a side channel
        # or require dynamics to write λ into state.metrics["dual_vars"]
        free_state = states.get(Phase.FREE)
        nudged_state = states.get(Phase.NUDGED)
        
        # PC-ALM uses the FREE phase dual variables for weight updates
        # (nudged phase only used for energy/loss computation)
        if free_state is None or not hasattr(free_state, "dual_vars"):
            return []
        
        dual_vars = free_state.metrics.get("dual_vars")  # list[Tensor] per layer
        acts = free_state.activations if isinstance(free_state.activations, list) else [free_state.activations]
        
        weight_names = _learnable_weight_names(geometry.params)
        grads = []
        for i, name in enumerate(weight_names):
            if i < len(dual_vars) and i < len(acts) - 1:
                lam = dual_vars[i]           # [B, D_l]
                h_pre = acts[i]              # [B, D_{l-1}]
                # ΔW = -λ^T @ h_pre / B
                grad = -(lam.T @ h_pre) / h_pre.shape[0]
                grads.append(grad)
            else:
                grads.append(torch.zeros_like(geometry.params[name]))
        
        return _apply_credit_norm(grads, self.config.credit_norm)
```

**Data flow**: `PCALMDynamics.settle` writes `dual_vars` into `state.metrics["dual_vars"]` (or a dedicated field in `SystemState` / `CompositeState`). `PCALMCredit` reads it. This avoids tight coupling while preserving the protocol.

### 2.3 SystemConfig Validation (`computronium/ontology/system.py`)

Add validation rules in `SystemConfig.validate()`:

```python
# PC-ALM dynamics requires PCALMCredit (or thermodynamic_contrast as proxy)
if self.dynamics.dynamics_type == "pc_alm":
    if self.credit.credit_type not in ("pc_alm", "thermodynamic_contrast"):
        raise ValueError(
            f"PC-ALM dynamics requires pc_alm or thermodynamic_contrast credit, "
            f"got {self.credit.credit_type!r}"
        )
    # PC-ALM requires layered geometry
    if self.geometry.topology_type not in ("feedforward", "recurrent", "tile_mesh"):
        raise ValueError(
            f"PC-ALM dynamics requires layered geometry, "
            f"got {self.geometry.topology_type!r}"
        )
    # Beta matching: dynamics.beta ≈ credit.beta (dual LR scale)
    if abs(self.dynamics.beta - self.credit.beta) > 1e-6:
        warnings.warn(
            f"PC-ALM beta mismatch: dynamics.beta={self.dynamics.beta} "
            f"!= credit.beta={self.credit.beta}. Dual LR scaling may be incorrect.",
            UserWarning, stacklevel=2
        )
```

### 2.4 Wiring Lockstep Test (`tests/property/test_dynamics_wiring_lock.py`)

The existing wiring lock test ensures registry ↔ config classmethods ↔ root exports stay in sync. Adding PC-ALM requires:
1. `StateDynamicsConfig.pc_alm()` classmethod
2. `PCALMDynamics` class in `_dynamics.py`
3. Registry entry `"pc_alm": PCALMDynamics` in `__init__.py`
4. Root `__all__` + `_LAZY` + `TYPE_CHECKING` imports in `ontology/__init__.py`
5. `CreditAssignmentConfig.pc_alm()` classmethod (or reuse `thermodynamic_contrast`)
6. `PCALMCredit` class in `credit.py`
7. Validation rule in `SystemConfig.validate()`

---

## 3. Implementation Efficiency: Computronium Stack vs. JAX Reference

The Sakana AI reference uses JAX (`jax.lax.scan` for the relaxation loop). Computronium's stack offers **three decisive advantages**:

| Aspect | JAX Reference | Computronium Strategy |
|--------|---------------|----------------------|
| **Relaxation loop** | `lax.scan` compiles to sequential HBM reads/writes per step `t` | **Fused Triton kernel**: entire `T`-step primal–dual loop in one kernel; `h`, `λ` stay in SRAM/registers |
| **Jacobian-transpose products** | `jax.vjp` per layer per step (expensive) | **Analytical J^T** for Linear layers: `W^T @ v` — no autograd overhead; for non-linear activations, `diag(act') @ (W^T @ v)` |
| **Dynamic early stopping** | `lax.while_loop` — recompilation on condition change | **Hardware-native termination**: Triton `device_assert` or host-check with `cudaStreamSynchronize`; no recompile |
| **Memory layout** | AoS (list of arrays) | **SoA**: `H = [B, L, D]`, `Lambda = [B, L, D]` — coalesced access, SIMD-friendly |
| **Mixed precision** | Manual `jax.numpy` dtype management | **Substrate-aware**: `DigitalSubstrate` / `NeuromorphicSubstrate` inject noise/precision per op |
| **Distributed** | `jax.pmap` / `pjit` — global sync | **P2P layer-local**: PC-ALM only needs neighbor `h`/`λ`; map to `computronium.p2p` for async cluster training |

### 3.1 Fused Primal–Dual Kernel (Triton)

Target: `computronium/acceleration/pcalm_kernels.py` (new file)

```python
# Pseudocode for fused kernel
@triton.jit
def pc_alm_primal_dual_step(
    H_ptr, Lambda_ptr, W_ptrs, b_ptrs,  # SoA: [B, L, D]
    rho, step_size, T, activation_type,
    B, L, D_max,  # D_max = max layer width (pad)
):
    # Each thread block handles one layer l
    # Shared memory: H_l, Lambda_l, H_{l-1}, H_{l+1}, W_l, W_{l+1}
    for t in range(T):
        # 1. Constraint c_l = h_l - act(h_{l-1} @ W_{l-1}^T + b_{l-1})
        # 2. Dual update: λ_l += step_size * c_l
        # 3. Primal update: h_l -= step_size * (c_l + λ_l + rho*c_l - W_l^T @ (c_{l+1} + λ_{l+1} + rho*c_{l+1}) * act'(h_l))
        # 4. Barrier sync across layer blocks (or sequential layer sweep)
    # Write back final H, Lambda
```

**Why this wins**: The JAX reference must materialize intermediate `c_l`, `λ_l` to HBM at every step. Fused kernel keeps them in shared memory / registers for the entire `T`-step relaxation. At `T=2L=2000` (depth 1000), this is **~100× less HBM traffic**.

### 3.2 Analytical Jacobian-Transpose for Linear Layers

For `f_θ_l(h) = act(h @ W_l^T + b_l)`:
- `J_l = diag(act'(z_l)) @ W_l` where `z_l = h_{l-1} @ W_l^T + b_l`
- `J_l^T @ v = W_l^T @ (act'(z_l) * v)` — single matmul + elementwise

No autograd needed. The `Substrate.get_forward_operator()` already provides the linear matmul; we add a `get_transpose_operator()` or compute directly in the kernel.

### 3.3 Adaptive Relaxation (Addressing Fixed Budget Defect)

The reference uses fixed `T = 2L`. Computronium's `StateDynamics` already has `convergence_threshold` and `convergence_start`. Extend `PCALMDynamics`:

```python
def settle(self, state, geometry, substrate, target=None):
    ...
    for step in range(self.config.max_steps):
        # ... primal-dual step ...
        
        if step >= self.config.convergence_start:
            # Constraint violation norm
            constraint_norm = max(c.abs().max().item() for c in constraints)
            if constraint_norm < self.config.convergence_threshold:
                self._settle_steps_used = step + 1
                break
    ...
```

**Adaptive budget** eliminates waste on shallow networks / easy inputs. The `convergence_threshold` becomes a meaningful hyperparameter (tunable via Optuna in `computronium/hyperopt`).

---

## 4. Defect Resolution & Porting Improvements

| PC-ALM Defect (Paper / Reference) | Computronium Fix | Integration Point |
|-----------------------------------|------------------|-------------------|
| **Loss of Prospective Configuration** (strict BP alignment) | Hybrid Dynamics: `λ̇ = α * (h - f) + (1-α) * λ` with `α ∈ [0,1]`. `α=0` = PC-ALM; `α→1` recovers prospective config. | Add `prospective_leak: float` to `StateDynamicsConfig.pc_alm()` |
| **Fixed inference budget `T`** | Adaptive relaxation via constraint violation norm (see §3.3) | `convergence_threshold` in `StateDynamicsConfig` |
| **Static hyperparameter grids** (`eta_best_by_cell.csv`) | Meta-learned `ρ`, `η_h`, `η_λ` via `computronium/hyperopt` — Optuna search over dynamics config space | `hyperopt/search_space.py` add `pc_alm` subspace |
| **No gradient checkpointing for deep nets** | `gradient_checkpointing` flag in `StateDynamicsConfig` (already in `EnergyMinimizationDynamics`) | Reuse pattern; checkpoint per `k` steps of relaxation |
| **Single substrate (digital)** | Substrate polymorphism: `NeuromorphicSubstrate` for event-driven PI controller; `MemristiveSubstrate` for analog dual integration | `SubstrateConfig` selects backend; kernel dispatches via `KernelRegistry` |
| **No energy monitoring** | `track_free_energy_per_iter` → record `L_ρ` per iteration for Control-Lyapunov analysis | Already in `StateDynamicsConfig`; `PCALMDynamics` implements |

### 4.1 Prospective Configuration Hybrid

Add to `StateDynamicsConfig.pc_alm()`:
```python
@classmethod
def pc_alm(
    cls,
    *,
    max_steps: int = 30,
    convergence_threshold: float = 1e-4,
    convergence_start: int = 5,
    step_size: float = 0.1,
    beta: float = 0.5,
    rho: float = 1.0,
    prospective_leak: float = 0.0,  # 0.0 = PC-ALM, >0 recovers prospective config
    momentum: float = 0.0,
    track_free_energy_per_iter: bool = False,
    compiled: bool = False,
) -> StateDynamicsConfig:
    return cls(
        dynamics_type="pc_alm",
        max_steps=max_steps,
        convergence_threshold=convergence_threshold,
        convergence_start=convergence_start,
        step_size=step_size,
        beta=beta,
        momentum=momentum,
        track_free_energy_per_iter=track_free_energy_per_iter,
        compiled=compiled,
        # Store rho, prospective_leak in extra dict or add fields
    )
```

In dynamics: `λ_l ← λ_l + step_size * (c_l + prospective_leak * λ_l)` — leaky integration interpolates between pure integral (PC-ALM) and proportional-only (prospective).

### 4.2 Meta-Learned Hyperparameters

Extend `computronium/hyperopt/search_space.py`:
```python
def pc_alm_search_space() -> dict[str, Any]:
    return {
        "dynamics.step_size": optuna.distributions.FloatDistribution(1e-3, 1.0, log=True),
        "dynamics.rho": optuna.distributions.FloatDistribution(0.1, 10.0, log=True),
        "dynamics.prospective_leak": optuna.distributions.FloatDistribution(0.0, 1.0),
        "dynamics.max_steps": optuna.distributions.IntDistribution(10, 200),
        "credit.beta": optuna.distributions.FloatDistribution(0.1, 2.0),
        "update.step_size": optuna.distributions.FloatDistribution(1e-4, 0.1, log=True),
    }
```

---

## 5. New Algorithms Enabled by PC-ALM Integration

With PC-ALM as a first-class `StateDynamics` + `CreditAssignment` pair, Computronium can pioneer:

### 5.1 Local Learning Transformers
- **Mechanism**: Derive augmented Lagrangian for Self-Attention. Dual variables for `Q`, `K`, `V` projections enforce local constraints `Q = X W_Q`, `K = X W_K`, `V = X W_V`.
- **Computronium path**: New `TransformerGeometry` variant with `PCALMDynamics` + `PCALMCredit`. The `layer_stack` abstraction already exposes per-block transitions; extend to attention heads.

### 5.2 Asynchronous Distributed PC-ALM (Neuromorphic Cluster)
- **Mechanism**: PC-ALM only requires neighbor-to-neighbor `h`/`λ` exchange. No global All-Reduce.
- **Computronium path**: Map layers to `computronium.p2p` nodes. Each node runs `PCALMDynamics.settle` locally, communicates `h_l`, `λ_l` with adjacent nodes via gRPC. `p2p/grpc_service.py` + `p2p/evolution.py` for async coordination.

### 5.3 Spiking PC-ALM (SNNs)
- **Mechanism**: Discretize PI controller: `λ_l[t] = λ_l[t-1] + η * (spike_count - target_rate)`. STDP modulated by `λ`: `ΔW ∝ λ_l * (pre_trace @ post_spikes)`.
- **Computronium path**: Combine `SpikeIntegrationDynamics` with dual-variable buffer. New `SpikingPCALMDynamics` + `SpikingPCALMCredit` (extends `TemporalTraceCredit`).

### 5.4 Equilibrium Propagation / Target Prop / Forward-Forward Absorption
PC-ALM's integration creates a unified framework to **benchmark all local learning rules** on identical infrastructure:
- `EnergyMinimizationDynamics` + `ThermodynamicContrast` = EqProp
- `PredictiveSettlingDynamics` + `LocalGoodnessCredit` = PC / FF
- `PCALMDynamics` + `PCALMCredit` = PC-ALM
- `InstantaneousDynamics` + `GradientCredit` = Backprop (baseline)

Run all on `computronium/cli/gallery.py` demo grid with identical `SystemConfig` coordinates.

---

## 6. Referenced Algorithms to Absorb

PC-ALM cites / builds on these — absorb into Computronium for fair comparison:

| Algorithm | Reference | Computronium Status | Action |
|-----------|-----------|---------------------|--------|
| **Equilibrium Propagation** | Scellier & Bengio (2017) | ✅ `EnergyMinimizationDynamics` + `ThermodynamicContrast` | Already implemented; extend to deep nets with `InnocentiInit` |
| **Predictive Coding (sPC)** | Rao & Ballard / Whittington & Bogacz | ✅ `PredictiveSettlingDynamics` | Add `prospective_leak` for fair PC-ALM comparison |
| **Error Predictive Coding (ePC)** | Goemaere et al. (2025, ICML 2026) | ✅ `ErrorPredictiveCodingDynamics` | Benchmark vs PC-ALM on depth scaling |
| **Target Propagation** | LeCun, Bengio (2014) | ✅ `TargetInversionCredit` | Add invertible layer support in `Geometry` |
| **Forward-Forward** | Hinton (2022) | ✅ `LocalGoodnessCredit` + `LocalContrastiveCredit` | Already O(1) memory; compare depth limits |
| **Residual MLP Init (1000-layer)** | Innocenti et al. (2026) | ❌ | Add `InnocentiInit` to `GeometryConfig` / weight init |
| **PI Controller for Credit** | Sacramento et al. (2018) | ❌ | Core of PC-ALM; implement in `PCALMDynamics` |

**Priority**: `InnocentiInit` (residual initialization for 1000-layer stability) is a prerequisite for PC-ALM depth claims. Add to `computronium/ontology/geometry.py` as `GeometryConfig.residual_init = "innocenti"`.

---

## 7. Attribution & Compliance

**License**: MIT (permissive — use, modify, distribute, commercial OK with notice)

**Required Attribution** (in all derivative code / docs):
```python
# Portions of this module are derived from PC-ALM.
# Copyright (c) 2026 Sakana AI
# Original Authors: Jeffrey Seely, Julian Gould
# License: MIT
# Paper: https://arxiv.org/abs/2605.31022
```

**BibTeX** (include in `docs/references.bib`):
```bibtex
@misc{seely2026pc-alm,
  title         = {Augmented Lagrangian Predictive Coding},
  author        = {Jeffrey Seely and Julian Gould},
  year          = {2026},
  eprint        = {2605.31022},
  archivePrefix = {arXiv},
  primaryClass  = {cs.LG},
  url           = {https://arxiv.org/abs/2605.31022},
}
```

**Compliance checklist**:
- [ ] Add copyright header to `PCALMDynamics`, `PCALMCredit`, `pcalm_kernels.py`
- [ ] Add citation to `docs/references.bib`
- [ ] Update `README.md` "Related Work" section
- [ ] Include license notice in `LICENSES/` directory (MIT)

---

## 8. Implementation Phases & Milestones

### Phase 0: Prerequisites (Week 1)
- [x] Add `InnocentiInit` weight initialization to `GeometryConfig`
- [x] Add `rho`, `prospective_leak` fields to `StateDynamicsConfig` (dataclass)
- [x] Extend `SystemState` / `CompositeState` with optional `dual_vars: list[Tensor]` field

### Phase 1: Core Dynamics (Week 2–3)
- [x] Implement `PCALMDynamics` in `_dynamics.py` (eager path first)
- [x] Register in `DYNAMICS_REGISTRY`
- [x] Add `StateDynamicsConfig.pc_alm()` classmethod
- [x] Add validation rules in `SystemConfig.validate()`
- [x] Unit test: depth-10 MLP on MNIST matches reference dynamics trajectory

### Phase 2: Credit Assignment (Week 3)
- [x] Implement `PCALMCredit` in `credit.py`
- [x] Add `CreditAssignmentConfig.pc_alm()` (or reuse `thermodynamic_contrast` with docs)
- [x] Integration test: full train step with `PCALMDynamics` + `PCALMCredit`

### Phase 3: Fused Kernel (Week 4–5)
- [x] Implement `pcalm_kernels.py` with Triton fused primal–dual loop
- [ ] Register in `KernelRegistry` for `AlgorithmFamily.PCALM` (new family) — deferred (legacy adapter surface)
- [x] Add `compiled=True` fast path in `PCALMDynamics.settle` (torch.compile whole-loop, guarded parity lock)
- [ ] Benchmark: kernel vs eager at depth 100, 500, 1000 — remaining (probes)

### Phase 4: Adaptive & Hybrid Features (Week 5)
- [x] Implement adaptive relaxation (constraint-norm early stop)
- [x] Implement `prospective_leak` hybrid mode
- [x] Add `track_free_energy_per_iter` for `L_ρ` tracking

### Phase 5: Hyperopt & Demo (Week 6)
- [ ] Add `pc_alm_search_space` to `hyperopt/search_space.py`
- [ ] Add demo to `computronium/cli/gallery.py` (`DEMOS["pc_alm_mnist"]`)
- [ ] Run hyperopt sweep; pin best config in `docs/figures/manifest.json`

### Phase 6: New Algorithm Prototypes (Week 7+)
- [ ] `SpikingPCALMDynamics` + `SpikingPCALMCredit`
- [ ] `TransformerPCALMDynamics` for attention blocks
- [ ] Async distributed prototype using `p2p` layer

---

## 9. Testing & Validation Strategy

| Test | Location | Purpose |
|------|----------|---------|
| `test_pc_alm_wiring_lock` | `tests/property/test_dynamics_wiring_lock.py` | Registry/config/exports sync |
| `test_pc_alm_settle_contract` | `tests/property/test_settle_caller_census.py` | Mutation contract compliance |
| `test_pc_alm_credit_contract` | `tests/unit/test_credit_protocol.py` | CreditAssignment protocol compliance |
| `test_pc_alm_gradient_equivalence` | `tests/integration/test_gradient_equivalence.py` | Cosine similarity vs BP ≥ 0.8 at depth 50 |
| `test_pc_alm_depth_scaling` | `tests/integration/test_depth_scaling.py` | Train depth 100, 500, 1000 on synthetic |
| `test_pc_alm_prospective_hybrid` | `tests/integration/test_prospective_hybrid.py` | Sweep `prospective_leak ∈ [0, 1]` |
| `test_pc_alm_adaptive_budget` | `tests/integration/test_adaptive_budget.py` | Convergence steps vs fixed `T=2L` |
| `test_pc_alm_kernel_parity` | `tests/kernels/test_pcalm_kernel.py` | Triton kernel bitwise match eager |

**Property-based tests** (Hypothesis):
- Primal–dual dynamics preserve `L_ρ` non-increase (Lyapunov)
- Weight update `ΔW = -λ h^T` matches analytical gradient at convergence
- Dual variables `λ` converge to KKT multipliers

---

## 10. Files to Create / Modify

### New Files
1. `computronium/acceleration/pcalm_kernels.py` — Fused Triton kernel ✅
2. `tests/integration/test_pc_alm_*.py` — Integration test suite (parity locks added to `test_compiled_settle.py` ✅)
3. `scripts/probes/pc_alm_depth_sweep.py` — Depth scaling probe (remaining)

### Modified Files
1. `computronium/ontology/dynamics/_dynamics.py` — `PCALMDynamics` class, `StateDynamicsConfig.pc_alm()`
2. `computronium/ontology/dynamics/__init__.py` — Registry entry, exports
3. `computronium/ontology/credit.py` — `PCALMCredit` class, `CreditAssignmentConfig.pc_alm()`
4. `computronium/ontology/system.py` — Validation rules in `SystemConfig.validate()`
5. `computronium/ontology/geometry.py` — `InnocentiInit` weight initialization
6. `computronium/state/composite.py` — Add `dual_vars` to `CompositeState` (or use `metrics` dict)
7. `computronium/hyperopt/search_space.py` — `pc_alm_search_space()`
8. `computronium/cli/gallery.py` — Demo registration
9. `docs/references.bib` — BibTeX entry
10. `computronium/ontology/__init__.py` — Export new classes

---

## 11. Risk Assessment & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Jacobian-transpose products too slow for non-linear activations | Medium | High | Restrict initial implementation to Linear + ReLU/Tanh (analytical `act'`); add `jax`-style VJP fallback later |
| Dual variables `λ` explode without proper `ρ` scheduling | High | Medium | Add `rho_schedule` config; warm-start `λ` from previous train step; gradient clipping on `λ` |
| Kernel fusion fails for variable layer widths | Medium | Medium | Pad to `D_max` in kernel; mask inactive neurons; benchmark overhead |
| Gradient equivalence vs BP lower than claimed | Medium | High | Run `test_pc_alm_gradient_equivalence` early; if < 0.5, debug constraint formulation |
| `prospective_leak` breaks convergence guarantees | Low | Medium | Theoretical analysis in PR; empirical sweep in `test_prospective_hybrid` |

---

## 12. Success Criteria

1. **Functional**: `PCALMDynamics` + `PCALMCredit` trains depth-100 MLP on MNIST to >97% accuracy (matching paper)
2. **Efficiency**: Fused kernel achieves ≥5× speedup over eager at depth 500, `T=1000`
3. **Depth scaling**: Trains depth-1000 Residual MLP (with `InnocentiInit`) without gradient explosion
4. **Adaptive**: `convergence_threshold=1e-3` reduces average settle steps by ≥40% vs fixed `T=2L`
5. **Hybrid**: `prospective_leak=0.1` improves sample efficiency on CIFAR-10 vs pure PC-ALM
6. **Integration**: All wiring locks pass; `SystemConfig.validate()` accepts `pc_alm` coordinates
7. **Reproducibility**: Demo in gallery reproduces paper's depth-scaling figure

---

## Progress Summary (2026-09-15)

### Completed Phases 0-2 (Core Implementation)
All Phase 0, 1, and 2 tasks completed successfully:

**Phase 0 - Prerequisites:**
- Added `InnocentiInit` weight initialization scheme to `GeometryConfig.init_scheme` with proper residual init scaling (1/N for input/output, 1/√(N·L) for hidden)
- Added `rho` (augmented Lagrangian penalty) and `prospective_leak` (hybrid PC/prospective config) fields to `StateDynamicsConfig`
- Extended `SystemState` with `dual_vars: list[Tensor] | None` field; `CompositeState` uses activity dict for same purpose

**Phase 1 - Core Dynamics:**
- Implemented `PCALMDynamics` class with full primal–dual relaxation loop:
  - Constraint violation computation: `c_l = h_l - f_θ_l(h_{l-1})`
  - Dual update (PI controller): `λ_l ← λ_l + step_size * (c_l + α*λ_l)` with `prospective_leak` = α
  - Primal update with top-down coupling: `J_{l+1}^T @ v` using analytical Jacobian transpose for ReLU
  - Adaptive early stopping on constraint violation norm
  - Augmented Lagrangian energy tracking per iteration
- Registered `PCALMDynamics` in `DYNAMICS_REGISTRY` with key `"pc_alm"`
- Added `StateDynamicsConfig.pc_alm()` classmethod with full documentation
- Added cross-axis validation in `SystemConfig.validate()`:
  - PC-ALM requires `pc_alm` or `thermodynamic_contrast` credit
  - PC-ALM requires layered geometry (feedforward, recurrent, tile_mesh)
  - Beta matching warning for dynamics.beta vs credit.beta
  - Thermodynamic contrast credit now allows pc_alm dynamics

**Phase 2 - Credit Assignment:**
- Implemented `PCALMCredit` class with local Hebbian update: `ΔW_l = -λ_l @ h_{l-1}^T / batch`
- Reads dual variables from `free_state.metrics["dual_vars"]` (set by PCALMDynamics)
- No autograd through settle loop required
- Added `CreditAssignmentConfig.pc_alm()` classmethod
- Full `AlgorithmIdentityCard` with reference to Seely & Gould 2026

**Wiring Lock Compliance:**
- All 4 wiring lock tests pass:
  - Registry ↔ config classmethods sync
  - Registry classes round-trip to_spec/from_spec
  - Registry classes exported in root __all__ and _LAZY
  - Root __all__ names have TYPE_CHECKING imports

**Integration Verified:**
- PCALMDynamics + PCALMCredit + NullPlasticity trains on MNIST (1 epoch, CPU)
- SystemConfig validation correctly accepts/rejects PC-ALM coordinates

### Remaining Work
- Phase 5: Hyperopt search space and gallery demo
- Phase 6: Spiking/Transformer/Async variants

### Phase 3 Completed (2026-09-15)
- Created `computronium/acceleration/pcalm_kernels.py` with:
  - `pcalm_settle_loop` / `_compiled_pcalm_settle = torch.compile(...)` — whole T-step primal–dual relaxation as one graph (repo R11.2.25 pattern)
  - `fused_dual_primal_update` — device-agnostic Triton fused elementwise kernel (CUDA via stock Triton, CPU via triton-cpu `set_active_to_cpu()` / `TRITON_DEFAULT_BACKEND=cpu`); eager fallback exact parity
- Added guarded `compiled=True` fast path in `PCALMDynamics.settle` with parity lock
- Parity lock tests appended to `tests/integration/test_compiled_settle.py`:
  - `test_compiled_pcalm_settle_matches_eager` (free + nudged phases, dual vars)
  - `test_compiled_pcalm_config_falls_back_cleanly` (recurrent geometry)
  - `test_compiled_pcalm_config_round_trip`
  - `test_pcalm_triton_fused_update_matches_eager` (CUDA Triton vs eager ~1e-7 fp32 parity)
  - `test_pcalm_triton_fused_update_cpu_fallback_exact` (CPU bitwise fallback)
- All wiring lock tests pass (`test_dynamics_wiring_lock.py`)

### New Improvement Opportunities Discovered
1. **KernelRegistry Family Registration**: Legacy kernel backend (`KernelRegistry` in `acceleration/kernel_backend.py`) used by model adapters is a separate surface. Adding `AlgorithmFamily.PCALM` registration there is deferred — the ontology fast path (torch.compile) is the primary acceleration path for PC-ALM.
2. **Depth-100/500/1000 Benchmarks**: Phase 3 planned benchmark at depth 100/500/1000 remains as probe scripts (`scripts/probes/pc_alm_depth_sweep.py`), not CI tests.
3. **Dual Variable Warm-start**: Currently dual variables reset to zero each train step. Warm-starting from previous step's `λ` could accelerate convergence.
4. **ρ Scheduling**: Fixed `rho` may benefit from scheduling (increase over training to tighten constraints).
5. **Gradient Checkpointing**: For very deep networks, add gradient checkpointing support during primal–dual loop.
6. **Prospective Leak Theory**: `prospective_leak` (α) interpolates between PC-ALM (α=0) and prospective configuration (α→1). Convergence guarantees for α>0 need analysis.
7. **Validation Test Suite**: Need dedicated integration tests:
   - `test_pc_alm_gradient_equivalence` (cosine vs BP ≥ 0.8)
   - `test_pc_alm_depth_scaling` (depth 100, 500, 1000)
   - `test_pc_alm_prospective_hybrid` (sweep α ∈ [0,1])
   - `test_pc_alm_adaptive_budget` (convergence steps vs fixed T)

---

*This plan is a living document. Update as implementation reveals new constraints or opportunities.*