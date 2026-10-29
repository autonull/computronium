# Learning Theory & Guarantees Research

<div class="research-header">
  <span class="research-badge">📈 Learning Theory</span>
  <h2>Online adaptation, distribution shift, plasticity vs. no-plasticity separation</h2>
  <p class="research-lead">Regret bounds · Task interference · Memory-assisted adaptation · Resource-bounded guarantees</p>
</div>

## Scope

This research path asks: **Under what conditions does plasticity provide provable benefits for learning?** It connects the metadynamics (plasticity mechanisms) to formal learning guarantees under declared resource budgets.

> A theorem about an online predictor does not automatically transfer to a reinforcement-learning policy. The latter requires additional assumptions about environment dynamics, exploration, reward, and the relationship between policy changes and observed data.

## Key Research Projects

### F11: Formal Learning Guarantees Under Changing Environments

| Project | Question | Approach |
|---------|----------|----------|
| **F11.1** Finite-horizon online adaptation | Regret/prediction-error bound for a plasticity mechanism on a bounded task family | Define task family, prove bound |
| **F11.2** Distribution-shift response | Bound adaptation time/error after a declared shift model | Change model + adaptation bound |
| **F11.3** Task interference | When do updates for one task alter behavior on another? | Characterize interference conditions |
| **F11.4** Memory-assisted adaptation | Benefit from explicit memory for a defined task class, or lower bound showing memory requirement | Compare with/without memory |
| **F11.5** Plasticity vs. no plasticity | Separation: one learner achieves a guarantee the other cannot under same assumptions | Formal comparison on same task class |

### F10: Update Rule Correctness (Foundation)
- Closed-form ridge solution correctness (F10.1)
- Temporal recurrence exactness (F10.3)
- Decay bounds (F10.4)
- Update invariants (F10.5)
- Objective descent under explicit assumptions (F10.6)

> Do not assume that an arbitrary local learning rule decreases global training loss.

## Plasticity Mechanisms Under Study

| Mechanism | Theoretical Angle | Target Guarantee |
|-----------|-------------------|------------------|
| `ClosedFormRidgePlasticity` | Convex optimization, exact solution | Ridge objective minimization, uniqueness |
| `TemporalPsiPlasticity` | Linear dynamical systems, trace decay | Bounded retention, forgetting rates |
| `FastWeightPlasticity` | Episode-local memory, outer products | Memory capacity, interference bounds |
| `RoutingPlasticity` | Mixture-of-experts, gating dynamics | Specialization, load balancing |
| `RuleStatePlasticity` | Z3-inspired, program-as-data | Universality, expressiveness separation |
| `SubstrateCoupledPlasticity` | Physical dynamics, noise | Robustness margins, noise-aware bounds |

## Resource-Bounded Guarantees (Critical)

All learning guarantees must specify:
- **Memory budget**: Bits of ψ, external memory capacity
- **Compute budget**: Transitions per adaptation step, total episode length
- **Precision**: Finite-precision effects on guarantee
- **Task class**: Exact definition of the family of tasks/environments
- **Comparison baseline**: What "no plasticity" means in the same resource model

## Connection to Other Paths

| Path | Connection |
|------|------------|
| **Formal Proof** | F10–F11: Machine-checked update correctness, learning guarantees |
| **Metadynamics** | F7–F9: Expressiveness hierarchy informs what can be learned; lifecycle guarantees enable retention analysis |
| **Z3 Research** | F5/F15: Does RuleStatePlasticity's universality translate to learnability advantages? |
| **Substrate** | F13: Finite-precision and noise effects on learning guarantees |

## Current Status

- **Measured Objectives**: <!-- gen:measured_objective_count --> of <!-- gen:objective_count --> registered objectives actually measured
- **Experiment Pipeline**: Governed pipeline with fidelity ladder (L0→L1→L2→L3) and budget declarations
- **Fairness Contract**: <!-- gen:fairness_clause_count --> clauses making comparisons legal before they run
- **Corrections Log**: <!-- gen:corrections_count --> public entries — failed beliefs are revoked, evidence stays
- **Documentation**: `docs/hpo_protocol.md`, `docs/evaluation_fairness_contract.md`, `docs/FAIRNESS_CONTRACT.md`

## Next Steps

1. **Select** a minimal online prediction task family (e.g., linear regression with changing coefficients)
2. **Formalize** `ClosedFormRidgePlasticity` update as a dynamical system with exact solution
3. **Prove** finite-horizon regret bound for ridge plasticity vs. no-plasticity baseline (F11.1 + F11.5)
4. **Characterize** task interference for fast-weight plasticity (F11.3)
5. **Extend** to distribution-shift model with declared change budget (F11.2)
6. **Machine-check** key lemmas in Rocq (F10 → F11 pipeline)

> The objective is not to prove that more plasticity is always beneficial. It is to establish conditions under which a specified mechanism is stable, adapts, or loses previous information — with explicit resource assumptions.

<!-- notes -->
Learning theory is where the rubber meets the road: we have plasticity mechanisms (metadynamics), we have substrate constraints (hardware), we have formal semantics (proofs). Learning theory asks: *so what?* — does this machinery actually help a system learn better under real constraints? The fairness contract and governed pipeline ensure claims are proportionate to evidence.
<!-- /notes -->