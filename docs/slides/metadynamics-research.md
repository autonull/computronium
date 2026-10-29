# Metadynamics & Credit Research

<div class="research-header">
  <span class="research-badge">🌀 Metadynamics</span>
  <h2>State-dependent credit, coupled dynamics, plasticity expressiveness</h2>
  <p class="research-lead">Routing · Fast weights · Rule-state · Temporal plasticity · Credit assignment</p>
</div>

## Scope

This research path covers the **plasticity axis (P)** and **credit axis (C)** of the ontology — the mechanisms that determine *what changes during an episode* and *how error is routed*.

## Plasticity Primitives (Expressiveness Hierarchy — F7)

| Primitive | Mechanism | Key Question |
|-----------|-----------|--------------|
| `NullPlasticity` | No within-episode state change | Baseline embedding (F7.1) |
| `RoutingPlasticity` | State-dependent routing/gating | What routing behaviors can fixed architecture + explicit routing state represent? (F7.2) |
| `FastWeightPlasticity` | Episode-local fast weights | Equivalence to explicit memory? Parameterization restrictions? (F7.3) |
| `SubstrateCoupledPlasticity` | Substrate-mediated plasticity | Coupling effects on stability (F12.5) |
| `RuleStatePlasticity` | Rule selection via ψ (Z3-inspired) | Separation from restricted routing/memory? (F7.4) |
| `ClosedFormRidgePlasticity` | Analytic ridge regression update | Exact solution correctness (F10.1) |
| `TemporalPsiPlasticity` | Trace-decayed plasticity | Retention/forgetting bounds (F8.3, F10.3) |

> Do not assume these form a simple linear hierarchy. Different mechanisms may be incomparable.

## Credit Assignment Primitives

| Primitive | Pseudo-Gradient | Symmetry |
|-----------|-----------------|----------|
| `EquilibriumPropagation` | Free/nudged phase difference | Symmetric |
| `BackpropThroughTime` | Autograd through settle | Asymmetric |
| `ForwardForward` | Local goodness objectives | Layer-wise |
| `DirectFeedbackAlignment` | Random feedback weights | Asymmetric |
| `SignSymmetry` | Sign-preserving feedback | Partial symmetry |

## Key Research Projects

### F7: Expressiveness Hierarchy
- Pairwise simulation matrix across primitives
- Zero-plasticity embedding (F7.1)
- Routing simulation (F7.2)
- Fast-weight equivalence/separation (F7.3)
- Rule-state separation (F7.4)
- Temporal plasticity characterization (F7.5)

### F8: Plastic-State Lifecycle Guarantees
- Episode isolation (F8.1)
- Exact reset (F8.2)
- Bounded retention (F8.3)
- Forgetting bounds (F8.4)
- Persistence conditions (F8.5)
- Consolidation separation (F8.6)

### F9: Stability–Plasticity Tradeoffs
- Contractive dynamics (F9.1)
- Perturbation bounds (F9.2)
- Stability under plastic updates (F9.3)
- Instability counterexamples (F9.4)
- Retention–adaptation incompatibility (F9.5)
- Stability–expressiveness frontier (F9.6)

### F10: Update Rule Correctness
- Closed-form ridge solution (F10.1)
- Uniqueness (F10.2)
- Temporal recurrence (F10.3)
- Decay bounds (F10.4)
- Update invariants (F10.5)
- Objective descent (F10.6)

### F12: Coupled Dynamics Stability
- Lyapunov decrease (F12.1)
- Equilibrium convergence (F12.2)
- Discrete-time stability (F12.3)
- Jacobian bounds (F12.4)
- Coupling effects (F12.5)
- Noise robustness (F12.6)

## Connection to Other Paths

| Path | Connection |
|------|------------|
| **Formal Proof** | F7–F10, F12: Formal semantics, theorems, guarantees |
| **Z3 Research** | RuleStatePlasticity expressiveness (F7.4), universality (F5) |
| **Substrate** | Substrate-coupled plasticity, noise robustness (F12.6, F13) |
| **Learning Theory** | Online adaptation (F11), plasticity vs. no-plasticity (F11.5) |

## Current Status

- **Implementation**: All primitives in `computronium/ontology/plasticity/` and `computronium/ontology/credit/`
- **Validation**: `SystemConfig.validate()` whitelists legal P×C combinations
- **Experiments**: Plasticity expressiveness probes in `scripts/probes/`
- **Documentation**: `docs/eqprop_deep_limitation.md`, `docs/metric_provenance.md`

<!-- notes -->
This slide covers the metadynamics (plasticity + credit) research surface. The expressiveness hierarchy (F7) is the central organizing question — not a linear ladder but a matrix of simulation/separation results. The lifecycle guarantees (F8) ensure the ψ machinery behaves as specified. The stability-plasticity tradeoffs (F9) are the deep theoretical question.
<!-- /notes -->