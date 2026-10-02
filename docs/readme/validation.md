---

## 🔬 Validation Framework: Property-Verified Hypercube

The framework enforces **correctness by construction** through a layered verification regime. The fast-CI gate validates the entire hypercube in seconds on CPU.

### Verification Status Markers

| Status | Meaning |
|--------|---------|
| **Implemented** | Code exists and runs |
| **Verified** | Property-lock tests pass (Hypothesis, numerical equivalence — Level 4 sampled numerical) |
| **Benchmarked** | Measured on tasks with reported metrics |
| **Hypothesized** | Research question; not yet empirically established |
| **Planned** | Future work; not yet implemented |

<details>
<summary><strong>Verification ≠ scientific superiority</strong> ⋯</summary>

A passing invariant or numerical-equivalence test demonstrates **implementation correctness**, not scientific superiority.
</details>

### ✅ Property Locks (L1–L7 + S/G/D/C/U/M Axes + J1–J7)

| Lock | Property | Key Assertions |
|------|----------|----------------|
| **L1** | Composed systems train & produce valid metrics | Backprop/FA/Tile systems train; loss≥0, accuracy∈[0,1] |
| **L2** | Pipeline stages pure functions of preceding axes | Geometry.forward deterministic; credit independent of update; substrate noise only effect |
| **L3** | Locality axioms: ThermodynamicContrast invariant to non-local perturb; FA feedback fixed at init & seed-independent | Layer-0 pseudo-gradient invariant; B matrices fixed; different seeds → different B |
| **L4** | Lyapunov/energy: energy non-increasing; Control-Lyapunov for PredictiveSettling | Energy monotonic (EqProp); free energy non-increasing (PredictiveCoding); convergence threshold |
| **L5** | Determinism: same seed + same device = bitwise equal params & metrics (CPU & GPU deterministic) | Parametrized over system factories |
| **L6** | Round-trip & totality: configs round-trip identity; Registry.to_system() projects all registered models | Identity on configs; protocol conformance on projected systems |
| **L7** | Distributed seam: SystemTrainer runs; fault tolerance | gRPC fault injection test captures lost workers, step, partial metrics |
| **S-axis** | Neuromorphic passivity; Quantum parameter-shift equivalence | Deterministic noise cancellation; cosine ≥ 0.999 vs FD |
| **D-axis** | SpikeIntegration Lyapunov (membrane bounded, non-diverging spike process); LazyStateDynamics | Spike counts tracked per (layer, settle step); bounded activations |
| **C-axis** | TemporalTrace STDP window (causal +, anti-causal -, antisymmetric, exponential decay); surrogate objectives | Sign matches timing; W(Δt) = -W(-Δt); FD cosine ≥ 0.95 |
| **U-axis** | Muon orthogonalizes gradient (G^T G ≈ I); SpectralConstrained SVD ≤ 1.0; Natural whitens; Elastic moves toward old params | Newton-Schulz converges; diagonal Fisher whitening; δ·(w-old_w) < 0 |
| **P-axis** | NullPlasticity Zero-Extension (`F_θ^Null = D_θ`); RoutingPlasticity gate entropy; FastWeightPlasticity decay bounds | Null ≡ 5-D; gate entropy ≥ 0; decay ∈ [0,1] |
| **J1** | NullPlasticity preserves 5-D dynamics (Zero-Extension Invariant) | $F_\theta^\text{Null} = D_\theta$ within numerical tolerance |
| **J2** | Persistent θ not mutated during intra-episode steps | θ data_ptr() unchanged during CoupledTransition.step |
| **J3** | fast_plastic variables mutate only through plasticity projection | ψ updates only via PlasticityPrimitive.step |
| **J4** | substrate_owned variables respect substrate physics constraints | σ updates only via Substrate.forward_operator |
| **J5** | consolidatable variables promoted only at episode boundaries | consolidate() only called at episode end |
| **J6** | Cross-adapters preserve joint transition shape & registry semantics | Adapter output is valid CompositeState projection |
| **J7** | Trajectory records contain full z = (x, ψ, σ) | JointTrajectory has activity, plastic, substrate at each step |

### 🧬 Biologically Motivated Property Tests (Hypothesis-based)

<details>
<summary><strong>Not established biological axioms</strong> ⋯</summary>

These are biologically motivated constraints/hypotheses encoded as property tests—not established biological axioms.
</details>

| Motivated Constraint | Test | Method | Threshold |
|------|------|--------|-----------|
| **EP Gradient Equivalence** | EqProp gradient aligns with BPTT | Cosine similarity | ≥ 0.5 |
| **Lyapunov Energy Descent** | Free energy monotonically non-increasing along relaxation | Hypothesis | Slack 1e-3; final < initial |
| **Contraction Mapping** | Relaxation operator Lipschitz < 1 | Pairwise distance ratio L < 1; directional amplification growth < 1 (`estimate_directional_amplification`) | Step sizes 0.1–0.5 |
| **Fixed-Point Reliability** | Unique attractor from random initializations | Relative diff < 1e-3; Idempotence ‖T(h*)-h*‖ < 1e-4 | |
| **Weight-Transport Freeness** | FA backward weights ≠ forward transpose; separate memory | ‖B - W^T‖ > 1e-3; data_ptr() distinct | standard_fa, adaptive_fa, DFA |
| **Adaptive-FA Alignment** | Feedback matrices align with forward weights over training | cos(B, W^T) improvement > 0.05 | biologically slow B regime |

### ✅ Integration Verification Gates (All Passing)

<details>
<summary><strong>Scope disclaimer</strong> ⋯</summary>

Scope: current CI / repository verification status — not evidence of scientific or benchmark superiority.
</details>

| Gate | Result |
|------|--------|
| Gradient equivalence (finite-difference) | CE families cos≥0.9: backprop, FA, DirectFA, StochasticFA, MEP-backprop; MSE families cos≥0.6: EqProp, MEP-EP, CHL |
| Ontology layer equivalence | ThermodynamicContrast=Backprop under InstantaneousDynamics; RiemannianOrthogonal preserves orthogonality; EnergyMinimization converges |
| Energy invariants (property-locked, Level 4) | Lyapunov descent, Control-Lyapunov, Substrate passivity, EqProp energy, Composition |
| Kernel equivalence (Triton vs PyTorch) | max_diff < 1e-5, rel_diff < 1e-4 |
| Kernel accuracy parity | FA, Backprop, PEPITA, DTP: kernel accuracy within 1% of reference on digits/synthetic |
| Kernel verified specs | 25 specs `kernel_verified` (11 primitives + 14 algorithms), promoted via ladder: parity + microbench evidence + dispatch auto-routing |
| Registry audit | 0 missing critical fields |
| Reproducibility | Models bitwise reproducible |
| Backprop parity | Runs successfully |
| Static typing | 0 errors on `computronium/ontology` (pyright elevated-standard, pre-commit gated); repo-wide basic |
| Formatting | Clean |

### 🧪 Test Commands

```bash
# Property locks (fast CI gate) — 5-D
uv run pytest tests/property/test_ontology_locks.py -q

# Property locks (fast CI gate) — 6-D Joint Architecture
uv run pytest tests/property/joint/ -q

# Registry integrity locks
uv run pytest tests/property/test_registry_completeness_lock.py -q
uv run pytest tests/property/test_kernel_verified_promotion_rule.py -q
uv run pytest tests/property/test_import_time_lock.py -q

# Core ontology unit tests
uv run pytest tests/unit/core/test_ontology.py -q

# Primitive & Algorithm test suites (now in default testpaths)
uv run pytest tests/primitives/ -q
uv run pytest tests/algorithms/ -q
uv run pytest tests/acceleration/ -q

# Integration: gradient equivalence + energy proofs
uv run pytest tests/integration/test_gradient_equivalence.py tests/integration/test_energy_invariants.py -q

# Kernel equivalence (Triton vs PyTorch)
uv run pytest tests/integration/test_kernel_equivalence.py -q

# Kernel accuracy parity (end-to-end learning)
uv run pytest tests/integration/test_kernel_accuracy_parity.py -q

# gRPC seam test
uv run pytest tests/integration/test_grpc_seam.py -q

# Demonstration suite (compose, swap credit, swap plasticity, memory wall, frozen θ) + figure lock
uv run pytest tests/integration/ -k demo
uv run pytest tests/integration/test_gallery_lock.py -q

# Joint integration tests
uv run pytest tests/integration/joint/ -q

# Full suite (now collects primitives + algorithms + acceleration + unit + property)
uv run pytest tests/ -q

# Type checking (strict)
uv run pyright .

# Formatting & linting
uv run ruff format --check . && uv run ruff check .
```