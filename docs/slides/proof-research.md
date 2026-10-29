# Formal Proof Research

<div class="research-header">
  <span class="research-badge">📐 Formal Verification</span>
  <h2>Machine-checked theorems for Computronium's architecture</h2>
  <p class="research-lead">Rocq proof assistant · Computational theory · Architecture and plasticity</p>
</div>

## Mission

Develop a machine-checked mathematical foundation that establishes:
1. What the six-axis architecture means mathematically
2. What computational capabilities arise from each axis and their interactions
3. Whether RuleStatePlasticity supports universal computation under explicit assumptions
4. What the separation between persistent parameters (θ) and evolving plastic state (ψ) actually guarantees
5. Which capabilities require plasticity, which can be implemented without it, and which require additional resources
6. Whether useful guarantees can be proved for adaptation, retention, stability, precision, and learning
7. Which claims are false, underspecified, redundant, or dependent on unrealistic assumptions

> The objective is a reusable Rocq development, not merely a collection of isolated proofs.

## Research Phases

### Phase A — Establish the Proof Baseline (F0–F2)
- **F0**: Inventory existing Rocq proofs, admitted lemmas, and dependencies
- **F1**: Formal semantics of the six-axis ontology — compositional model with totality, composition correctness, interface compatibility
- **F2**: Frozen-θ, evolving-ψ semantics — parameter invariance, state-update correctness, lifecycle separation, reset isolation

### Phase B — Prove the Central Computational Claim (F3–F6)
- **F3**: Reconstruct and formalize the Z3 simulation argument (Rojas 1998)
- **F4**: Formalize RuleStatePlasticity — rule selection, state representation, frozen-machinery invariant
- **F5**: Prove or refute universality of RuleStatePlasticity — direct simulation or transfer via Z3
- **F6**: State-capacity and impossibility theorems — finite-state limitations, external memory dependency, precision dependency

### Phase C — Determine What Plasticity Contributes (F7–F9, F14–F15)
- **F7**: Expressiveness hierarchy across plasticity primitives
- **F8**: Plastic-state lifecycle guarantees — episode isolation, exact reset, bounded retention, consolidation separation
- **F9**: Stability–plasticity tradeoffs — contractive dynamics, perturbation bounds, retention–adaptation incompatibility
- **F14**: Formal compositionality of the six axes
- **F15**: Distinguish architectural novelty from new computational power

### Phase D — Learning & Dynamical Guarantees (F10–F13)
- **F10**: Correctness of plasticity update rules — closed-form ridge, temporal trace-decay, fast weights
- **F11**: Formal learning guarantees under changing environments
- **F12**: Stability and convergence of coupled dynamics
- **F13**: Precision, noise, and substrate refinement

### Phase E — Resource Costs & Infrastructure (F16–F17)
- **F16**: Complexity of simulation and execution
- **F17**: Verify the ontology and experiment specifications

## Key Distinctions

| Claim Type | What It Means | Status |
|------------|---------------|--------|
| **Computability** | Can the architecture compute a specified function? | Open |
| **Expressiveness** | What family of functions/state transitions can it represent? | Open |
| **Efficiency** | How many operations, memory cells, bits, or updates? | Open |
| **Learnability** | Can a learning process discover a useful configuration within budget? | Open |

> Proving one does not establish the others.

## Current Status

- **Repository**: <https://github.com/autonull/computronium>
- **Proof Assistant**: Rocq (Coq)
- **Full Specification**: `docs/PROOF.md` — complete research program with 17 formal projects (F0–F17)
- **Prioritization**: Phased gates (A→B→C→D→E) with explicit acceptance criteria

## Next Steps

1. **Inventory** existing `.v` files and admitted lemmas (F0)
2. **Build** clean Rocq environment with CI gate
3. **Formalize** the six-axis ontology semantics (F1)
4. **Formalize** frozen-θ, evolving-ψ semantics (F2)
5. **Reconstruct** Z3 simulation argument in Rocq (F3)

<!-- notes -->
This slide summarizes the full PROOF.md specification. The research program is designed to be usable as a standalone document. Each phase has a gate — do not proceed on the assumption that universality must hold. Negative results (impossibility theorems) are successful outcomes.
<!-- /notes -->