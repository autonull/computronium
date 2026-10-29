# Z3 Benchmark & Plasticity Research

<div class="research-header">
  <span class="research-badge">🎯 Z3-Inspired</span>
  <h2>Frozen weights (θ), evolving fast state (ψ) — algorithm as trajectory</h2>
  <p class="research-lead">Konrad Zuse's Z3 (1941) · No conditional branching · Turing completeness via meta-dynamics</p>
</div>

## The Historical Analogy

The naming of the "Z3 Benchmark" is a precise mathematical analogy for what Computronium achieves with the Joint Architecture.

### 1. The "No Conditional Branching" Constraint

Zuse's Z3 had no conditional branching — the punched tape executed sequentially. To perform conditional logic, programmers computed **both paths and masked** the unwanted one:

```
Result = (Condition × Path_A) + ((1 − Condition) × Path_B)
```

**Computronium Parallel:** Standard deep learning uses hard `argmax` routing (Mixture of Experts), breaking gradients. The Z3 benchmark forces the network to achieve task switching via **continuous, differentiable arithmetic masking** mediated by the fast state ψ:

$$T_t = \sum_k g_k(\psi_t) T_k$$

The network computes a soft mixture of operators without altering the underlying physical substrate (θ).

### 2. Hardware vs. Tape (The θ vs. ψ Divide)

| Z3 Component | Computronium Parallel |
|--------------|----------------------|
| Physical relays (~2,600), arithmetic unit | Persistent weights **θ** (frozen, slow, energetically expensive) |
| Punched celluloid tape | Fast plasticity state **ψ** (dynamic, intra-episode memory that routes computation) |

The "algorithm" lives in ψ; the hardware (θ) is a fixed, stable attractor manifold.

### 3. Turing Completeness via Meta-Dynamics

For decades, computer scientists debated whether the Z3 was Turing-complete without conditional branches. In 1998, Raúl Rojas proved it **was** — by writing a clever looping program on the tape that simulated a Turing machine's state transitions. The "algorithm" was emergent from the tape, not the hardware.

**Computronium Parallel:** The Z3 Benchmark asks the exact same fundamental question:

> *Can a network with strictly frozen parameters (θ) achieve universal, multi-task algorithmic behavior purely through the dynamics of its fast plastic state (ψ)?*

## Why This Matters

In biological brains and neuromorphic/analog hardware:
- **Changing persistent weights (θ)** is slow, noisy, and energetically expensive (like physically rewiring relays or burning out memristors)
- **Evolving internal activation states (ψ)** is fast, cheap, and local (like reading a tape or letting an energy landscape settle)

By naming this benchmark "Z3", we explicitly state that true computational power shouldn't require constantly overwriting the hardware. The hardware should be a fixed, stable attractor manifold, and the "algorithm" should be the trajectory through that manifold.

## Research Questions

### Q1: Universality of RuleStatePlasticity
Can a fixed-θ, evolving-ψ system simulate a universal machine? Two routes:
- **Route A**: Direct simulation — encode TM tape, head, control state, transition table in ψ
- **Route B**: Transfer via Z3 — prove RuleStatePlasticity simulates the Z3 arithmetic machine, transfer universality

### Q2: Expressiveness Hierarchy
How do the plasticity primitives compare under the same resource constraints?
- `NullPlasticity` (baseline)
- `RoutingPlasticity`
- `FastWeightPlasticity`
- `SubstrateCoupledPlasticity`
- `RuleStatePlasticity` (Z3-inspired)
- `ClosedFormRidgePlasticity`
- `TemporalPsiPlasticity`

### Q3: State-Capacity Limits
- Finite ψ: eventual periodicity, memory lower bounds
- External memory: what capabilities does writable memory add?
- Precision dependency: exact arithmetic vs. finite-precision hardware

### Q4: Stability–Plasticity Tradeoffs
- Contractive dynamics → fixed points, convergence
- Perturbation bounds under plastic updates
- Retention–adaptation incompatibility in bounded memory

## Current Status

- **Formal Specification**: `docs/PROOF.md` — Projects F3–F6, F15 focus on Z3/RuleStatePlasticity
- **Implementation**: `RuleStatePlasticity` primitive in `computronium/ontology/plasticity/`
- **Z3 Analogy Document**: `docs/Z3.md` — detailed historical parallel
- **Benchmark**: Z3 Benchmark as a first-class evaluation target in the pipeline

## Connection to Other Research Paths

| Path | Connection |
|------|------------|
| **Formal Proof** | F3–F6: Z3 formalization, RuleStatePlasticity semantics, universality theorem |
| **Metadynamics** | Plasticity expressiveness hierarchy (F7), lifecycle guarantees (F8) |
| **Substrate** | Precision/noise refinement (F13), hardware deployment |
| **Learning Theory** | Online adaptation guarantees (F11), plasticity vs. no-plasticity separation |

## Next Steps

1. **Formalize** the Z3 arithmetic machine model in Rocq (F3)
2. **Specify** RuleStatePlasticity transition semantics matching implementation (F4)
3. **Attempt** universality proof or construct rigorous limitation result (F5)
4. **Characterize** finite-state limitations and external memory dependency (F6)
5. **Build** Z3 Benchmark evaluation into the governed pipeline

> This is an incredibly elegant conceptual anchor. The Z3 metaphor perfectly encapsulates the core philosophy of Computronium: the hardware should be a fixed, stable attractor manifold, and the "algorithm" should be the trajectory through that manifold.

<!-- notes -->
The Z3 analogy is not just historical flavor — it's a precise mathematical framing. The key insight: universality without conditional branching requires the "program" to be data (ψ) that the fixed machinery (θ) interprets. This is exactly what RuleStatePlasticity does. The research program in PROOF.md treats this as the central computational claim (Phase B).
<!-- /notes -->