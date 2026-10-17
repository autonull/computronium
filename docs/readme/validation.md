
## 🔬 Validation Framework: Property-Verified Hypercube

The framework enforces **correctness by construction** through a layered verification regime. The fast-CI gate validates the entire hypercube in seconds on CPU.

### ⚠️ Notation Disambiguation

This document uses three distinct "L" numbering schemes — **do not confuse them**:

| Scheme | Range | Meaning | Prefix Used Here |
|--------|-------|---------|------------------|
| **Verification Levels** | VL1–VL5 | Evidential strength of a claim (analytical → empirical) | **VL** |
| **Property Locks** | PL1–PL7 | Core CI-locked invariants (composition, purity, determinism, etc.) | **PL** |
| **Fidelity Levels** | FL0–FL2 | Schedule fidelity tier for a run (quick → full) | **FL** |

- **VL1–VL5** are defined in `computronium.verification` and label *claims*.
- **PL1–PL7** are the property-lock test suites in `tests/property/` and label *invariants*.
- **FL0–FL2** appear in `Schedule.fidelity` and label *evaluation depth*.

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

### ✅ Property Locks (PL1–PL7 + S/G/D/C/U/M Axes + J1–J7)

> **Notation:** "PL" = Property Lock (not to be confused with Verification Levels VL1–VL5
> or Fidelity Levels FL0–FL2). This table uses PL1–PL7 for the core property locks.

| Lock | Property | Key Assertions |
|------|----------|----------------|
| **PL1** | Composed systems train & produce valid metrics | Backprop/FA/Tile systems train; loss≥0, accuracy∈[0,1] |
| **PL2** | Pipeline stages pure functions of preceding axes | Geometry.forward deterministic; credit independent of update; substrate noise only effect |
| **PL3** | Locality axioms: ThermodynamicContrast invariant to non-local perturb; FA feedback fixed at init & seed-independent | Layer-0 pseudo-gradient invariant; B matrices fixed; different seeds → different B |
| **PL4** | Lyapunov/energy: energy non-increasing; Control-Lyapunov for PredictiveSettling | Energy monotonic (EqProp); free energy non-increasing (PredictiveCoding); convergence threshold |
| **PL5** | Determinism: same seed + same device = bitwise equal params & metrics (CPU & GPU deterministic) | Parametrized over system factories |
| **PL6** | Round-trip & totality: configs round-trip identity; Registry.to_system() projects all registered models | Identity on configs; protocol conformance on projected systems |
| **PL7** | Distributed seam: SystemTrainer runs; fault tolerance | gRPC fault injection test captures lost workers, step, partial metrics |
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

### Running the verification

The fast CI gate is `uv run python -m pytest tests/property/ -q`. The testing
tiers, the never-bypassed lock list and the per-commit checklist are in [For
developers](#for-developers); `uv run comp conformance` runs the conformance
audit.