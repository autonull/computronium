# Publication Draft (Outline)

Status: outline based only on released mechanisms. No overclaims; every
result cites its experiment and scope. Expand section by section when a
venue is chosen.

## Working title

*Composable alternative learning mechanisms under auditable governance:
frozen-backbone task switching, adaptive local feedback, and stable
transient amplification*

## Claims (scoped)

1. **ψ task switching.** On conflicting synthetic task pairs at quick
   budgets (3 seeds), a trace-decayed ridge ψ readout on a frozen backbone
   switches tasks with θ bitwise-invariant, reaching 0.66–0.74 accuracy vs
   0.25 frozen-null, with ~9× less adaptation walltime than SGD readout
   retraining at matched quick budget (X-TPC-001/002/003, X-TAC-001).
   Conflict-adaptive trace decay turns forgetting on only when label
   geometry conflicts (X-TAC-001).
2. **Adaptive local feedback.** A slow-blend feedback projection (toward
   the normalized forward weight) beats matched fixed feedback on all seeds
   for late-trajectory improvement-per-norm at 10 and 60 step horizons
   (X-ALI-001, X-ALI-002/E-000027). Mechanism: `e @ B` approaches true
   backprop through the readout as B blends toward W₂.
3. **Role-split updates.** Riemannian-orthogonal (Muon-class) updates
   confined to the readout weight beat both parent rules on the mlp task
   (X-USU-001); the same orthogonalization collapses under FF×Muon local
   credit at width 32 — a concrete boundary for heterogeneous update
   hardware claims.
4. **Stable transient amplification.** Jordan-block coordinates with
   ρ ≤ 0.95 and σ_max > 1 settle in budget and yield 4×–2600× transient
   signal retention over matched contractive coordinates; paired replay
   shows noise divergence scales identically (retention gain, not SNR gain)
   (X-STA-001, X-STA-002/E-000028).

## Governance contribution

All of the above was executed under CEEC: pre-registered questions and
predictions, gate-checked evidence, belief revision with calibration
records, and an auditable ledger (E-000018, E-000022..E-000028). The
governance engine itself is released as `ceec-core`.

## Threats to validity (to state explicitly)

- Quick synthetic tasks only; no large-scale or real-dataset results.
- CPU float32 simulation; no hardware measurements.
- Linear-coordinate analysis for the stability family (J = W exact).
- Belief intervals are heuristic, not Bayesian posteriors (method noted per
  revision).

## Non-claims

- Not "backprop replacement"; all local-learning results are relative to
  matched fixed-feedback baselines within stated scopes.
- No universal efficiency claim for any mechanism.
- No neuromorphic hardware validation (blueprint is design-level).

## Planned structure

1. Introduction — ontology framing (6 axes), governance-first methodology.
2. The CEEC protocol (released as ceec-core).
3. Mechanisms 1–4 with benchmark tables and scope statements.
4. Boundaries and falsified/deferred branches (buffered-ψ accuracy tradeoff,
   FF×Muon collapse, routing blocked by baseline defect).
5. Hardware blueprint discussion (simulation-only).
6. Reproducibility statement — packages, quick-mode commands, registered
   artifacts.