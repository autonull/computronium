# TODO23 — Generative Learning Mechanism Platform

**Status:** PLANNED (2026-09-11). Supersedes TODO22.
**Created:** 2026-09-11
**Synthesizes:** TODO12–22 (all prior work redeemed here)

---

## 0. The Synthesis: What We Actually Built

After 11 TODO cycles, Computronium has **four production-grade assets** that no other ML library has:

| Asset | What It Is | Provenance |
|-------|------------|------------|
| **6-axis composition engine** | S×G×D×P×C×U as orthogonal, type-checked, swappable primitives — 13 factories, 6-D joint, single trainer | TODO16–18 |
| **Frozen-θ ψ runtime** | Task switching, compression, reconfiguration, composition *without weight changes* — verified at probe scale (E2/E3/E4) | TODO17 |
| **I(C,U) predictive model** | 0.944 held-out accuracy predicting *which credit×update×geometry works* before training | TODO16 §4 |
| **Substrate-aware compilation** | Memristive (IR-drop), Neuromorphic (spikes), Photonic (phase), Quantum (unitary) — hardware constraints as first-class types | TODO18, TODO20 |

**The gap:** These are *components*. The *product* is a **generative API**: given a problem specification, it *synthesizes the optimal learning mechanism*, trains it with guarantees, and deploys it to hardware.

---

## 1. CEEC Assessment: Sufficient but Misapplied

**METHODOLOGY.SCHEMA.md is architecturally sound.** Its invariants (evidence before belief, scope before generality, hard gates, separation of belief/goal) are correct.

**The failure mode:** We applied CEEC to *probe-level experiments* (X-ALI-001, X-TPC-003, w16_routing_depth) instead of *mechanism synthesis decisions*. This produced:
- An opaque ledger of 50+ experiment codes
- Beliefs about narrow probe configurations (B-H1, B-H2, B-H3...)
- No pathway from "B-H2 promoted" to "here's a better algorithm for your problem"

**The fix:** CEEC stays as the **governance layer**. We add a **Synthesis Layer** above it that:
1. Takes *problem specifications* (not experiment codes) as input
2. Uses I(C,U,P) model + recipe cards + AutoScientist to *propose mechanism coordinates*
3. Runs *validation campaigns* (not probes) governed by CEEC
4. Outputs *validated mechanisms with certificates* — not belief IDs

```text
User Problem Spec → Synthesis Engine → Mechanism Coordinate → Validation Campaign (CEEC-governed) → Certified Mechanism → User
```

---

## 2. The Generative API (Target)

```python
from computronium import Lab

lab = Lab(device="cuda")

# 1. Specify the PROBLEM, not the algorithm
spec = lab.specify(
    task="image_classification",
    dataset="cifar100",
    constraints=dict(
        compute_budget="1xA100-40GB",
        latency_ms=50,           # inference
        memory_gb=8,             # training
        continual=True,          # task stream expected
        local_credit=False,      # backprop allowed
        precision="bf16",
        substrate="digital",     # or "memristive", "neuromorphic", "photonic"
    ),
    objectives=["accuracy", "adaptation_speed", "stability"],
)

# 2. Automatic mechanism synthesis (the brain)
system = lab.synthesize(spec)  
# → searches 6-D space using I(C,U,P) model + recipe cards + constraint solver
# → returns composed System with provenance: why this coordinate?

# 3. Train with all guarantees (the engine)
result = lab.train(system, spec,
                   stability_guard=True,      # calibrated kill switch
                   harvest=True,              # EMA resurrection (depth-50: 0.784→0.917)
                   ceec_logging=True,         # full evidence trail
                   frozen_theta_audit=True)   # ψ-only adaptation audit

# 4. Continual learning runtime (the memory)
for task_id, task_data in task_stream:
    result = lab.adapt(result.system, task_data,
                       mode="psi_only",       # frozen θ, ψ adaptation
                       stability_check=True)

# 5. Deploy to hardware (the body)
lab.export(result.system, target="onnx", quantization="int8", substrate="memristive")
```

**This is what makes Computronium indispensable:** It's the only system that maps *constraints → mechanism → certified result → deployed artifact* automatically.

---

## 3. Architecture: Three Layers

```
┌─────────────────────────────────────────────────────────────────┐
│  SYNTHESIS LAYER (TODO23)                                       │
│  Lab.specify() → Lab.synthesize() → Lab.train() → Lab.adapt()  │
│  Problem spec → Mechanism coordinate → Certified result → Deploy│
├─────────────────────────────────────────────────────────────────┤
│  GOVERNANCE LAYER (CEEC-Core — KEEP, already working)           │
│  Evidence → Derived → Belief → Gates → Decision → Audit        │
│  Validates campaigns, certifies mechanisms, tracks calibration │
├─────────────────────────────────────────────────────────────────┤
│  PRIMITIVE LAYER (6-axis ontology — KEEP, already working)      │
│  Substrate × Geometry × StateDynamics × Plasticity × Credit × Update │
│  13 factories, joint systems, FrozenΘAudit, EMA harvest        │
└─────────────────────────────────────────────────────────────────┘
```

**TODO23 builds the Synthesis Layer.** The other two are done.

---

## 4. TODO23 Phases

### Phase 1: Problem→Mechanism Compiler (The Brain)

| Task | Deliverable | Depends On |
|------|-------------|------------|
| **T23.1.1 Spec DSL** | `ProblemSpec` dataclass: task, dataset, constraints, objectives, substrate prefs | — |
| **T23.1.2 I(C,U,P) Model v2** | Depth-matched, ψ-conditional, geometry-aware predictor; held-out ≥0.90 | TODO16 §4, TODO17 §5.1 |
| **T23.1.3 Constraint Solver** | `SystemConfig.validate()` as hard filter + soft preference ranking | TODO18 |
| **T23.1.4 Recipe Registry** | Family→optimizer/geometry/config with Pareto metadata (accuracy, latency, memory, stability) | TODO16 §0.3 |
| **T23.1.5 Synthesis Engine** | `lab.synthesize(spec) → System` with provenance trace (why this coordinate?) | 1.1–1.4 |
| **T23.1.6 Interactive Explorer** | `lab.explore(spec) → Pareto frontier` of mechanism options with predictions | 1.5 |
| **T23.1.7 Exploration Budget** | `spec.exploration_budget: int` — max campaigns if synthesis confidence < 0.7; AutoScientist fallback grid; CEEC gate `ExplorationBudgetExhausted`; Cookbook Entry marked "exploratory" | 1.2, 1.5 |
| **T23.1.8 Autopoiesis-Ready Primitives** | Expose protocols in `computronium.autopoiesis.protocols`: `OperatorGenome`, `MutationOperator`, `FitnessMetric`, `SelectionPolicy`, `StagnationDetector`, `Constitution` — interfaces only, zero implementation; enables TODO24 | 1.1, 1.3 |

**Success criterion:** `lab.synthesize(spec)` returns a valid 6-axis coordinate that `SystemConfig.validate()` accepts, with a human-readable rationale trace. Exploration budget triggers governed campaigns when confidence low.

### Phase 2: Unified Training Surface (The Engine)

| Task | Deliverable | Depends On |
|------|-------------|------------|
| **T23.2.1 Lab.train()** | Single entry point; all guarantees opt-in via flags | Phase 1 |
| **T23.2.2 StabilityGuard Integration** | `attach(system)` → `StabilityVerdict` in training loop; auto-kill on divergence | `packages/stability` |
| **T23.2.3 EMA Harvest** | `harvest_mode` in `SystemTrainerConfig` wired to `Lab.train()` | TODO16 §0.1 |
| **T23.2.4 FrozenΘAudit Automation** | Automatic ψ-only audit when `spec.continual=True` | TODO18 |
| **T23.2.5 CEEC Campaign Logging** | Automatic evidence capture per epoch/batch; campaign → belief pipeline | `ceec-core` |
| **T23.2.6 Determinism Seal** | `seed → bitwise reproducible params + metrics` certificate in result | TODO18 |

**Success criterion:** `lab.train()` produces a `TrainingResult` with: metrics, stability certificate, harvest weights, CEEC evidence refs, determinism proof.

### Phase 3: Continual Learning Runtime (The Memory)

| Task | Deliverable | Depends On |
|------|-------------|------------|
| **T23.3.1 ψ-Adaptation Modes** | `temporal`, `conflict_adaptive`, `closed_form`, `role_split` as first-class `AdaptationMode` enum | TODO17, TODO16 |
| **T23.3.2 Task Boundary Detection** | Automatic (gradient conflict, loss plateau) + manual triggers | TODO17 |
| **T23.3.3 ψ-Composition** | Sequence/compose ψ-programs over NTM/NCA (E4 machinery) | TODO17 E4 |
| **T23.3.4 Z3 Rule Selection** | Operator library + closed-form selection for ψ | TODO16 §2.3 |
| **T23.3.5 Bitwise θ Invariance** | `ThetaInvarianceAudit` + SHA proof in `AdaptationResult` | TODO18 |
| **T23.3.6 Probe Hygiene for Synthesis Validation** | Validation campaigns use **forked copies** (parent state isolated); probe batches **never touch production training** (held-out buffer); slope measured with **paired statistical test**; equal-compute normalization across credit families | 3.1, 2.2 |

**Success criterion:** `lab.adapt(system, task_data, mode="psi_only")` returns adapted system with θ bitwise-identical, ψ updated, stability certificate. Validation campaigns obey probe hygiene.

### Phase 4: Hardware-Aware Deployment (The Body)

| Task | Deliverable | Depends On |
|------|-------------|------------|
| **T23.4.1 SubstrateSpec Compilation** | Digital → Memristive/Neuromorphic/Photonic/Quantum with constraint preservation | TODO18, TODO20 |
| **T23.4.2 Kernel Export** | Triton/ONNX/TorchScript with substrate constraints (IR-drop, spike sparsity, phase wrapping) | TODO20 |
| **T23.4.3 Quantization Pipeline** | INT8/ternary with STE + substrate noise injection + calibration | TODO20 |
| **T23.4.4 Edge Runtime** | P2P (gRPC/Kademlia) + FastAPI server (already exists, harden) | TODO20 |
| **T23.4.5 Energy/Cost Estimation** | Simulated + estimated + hardware-measured tiers with clear labeling | TODO20 |

**Success criterion:** `lab.export(system, target="onnx", substrate="memristive")` produces runnable artifact with substrate constraint report.

### Phase 5: Ecosystem & Adoption (The Reach)

| Task | Deliverable | Depends On |
|------|-------------|------------|
| **T23.5.1 HuggingFace Integration** | `AutoModel.from_pretrained("computronium/...")` + `Trainer` callback | Phase 2 |
| **T23.5.2 Lightning Callback** | `ComputroniumCallback` for standard `Trainer` workflows | Phase 2 |
| **T23.5.3 Benchmark Suite** | Standard tasks: vision, NLP, tabular, continual, neuromorphic — with published Pareto frontiers | All phases |
| **T23.5.4 Practitioner Documentation** | Mechanism cookbook, migration guides, "from PyTorch to Computronium" | All phases |
| **T23.5.5 Gallery 2.0** | Interactive mechanism explorer: constraints → live Pareto frontier → one-click synthesis | Phase 1.6 |

**Success criterion:** External user can `pip install computronium-lab` and run the quickstart in <5 minutes with a real result.

---

## 5. Tangible Results This Produces (Not Experiment Codes)

| Output | What It Is | Who Uses It |
|--------|------------|-------------|
| **Certified Mechanism** | `(S,G,D,P,C,U)` coordinate + predicted metrics + stability certificate + training log + CEEC evidence chain | Researchers, engineers |
| **Mechanism Cookbook Entry** | "For continual vision on 1×A100: `Digital × NCA × PredictiveSettling × TemporalPsi × LocalGoodness × Muon` — 92% acc, 15ms latency, 6GB mem" | Practitioners |
| **Pareto Frontier Report** | Interactive HTML: accuracy vs latency vs memory vs adaptation_speed across 6-D space | Architects |
| **Deployed Artifact** | ONNX/INT8/Triton kernel + substrate constraint report + energy estimate | Deployment engineers |
| **Continual Learning Session** | Task stream → adapted ψ sequence → θ invariance proof → per-task metrics | Continual learning researchers |

**No more X-ALI-001, B-H3, w16_routing_depth.** The ledger stores *campaigns that certify mechanisms*, not probes that test hypotheses.

---

## 6. CEEC Integration: Campaign-Governed, Not Probe-Governed

| Old (TODO12–21) | New (TODO23) |
|-----------------|--------------|
| Pre-register probe `X-TPC-003` | Pre-register **validation campaign** for synthesized mechanism |
| Belief `B-H2: temporal psi helps` | Belief `B-SYNTH-001: synthesized mechanism M achieves 92% on CIFAR100 under constraints C` |
| Gate: `MultiSeed`, `DefectHunt` | Gate: `BenchmarkReproduction`, `StabilityCertificate`, `DeployabilityCheck` |
| Evidence: probe log | Evidence: campaign record + benchmark suite + deployment test |
| Decision: "run X-USU-002" | Decision: "certify mechanism M for problem class P" |

**CEEC governs the *validation campaigns* for synthesized mechanisms.** This is its correct level of abstraction.

---

## 7. Redeeming All Prior Work

| Prior TODO | What It Gave Us | How TODO23 Uses It |
|------------|-----------------|-------------------|
| TODO12–15 | Mechanisms (PEPITA, LEMMA, STDP, FA, TP, PC, Hebbian, SNN, TileNet) | Primitive layer — all available in synthesis |
| TODO16 | 6-axis composition, I(C,U) model, recipe cards, EMA harvest, benchmarks L1/L3/L3.5 | Synthesis engine data + training guarantees |
| TODO17 | Frozen-θ ψ: temporal, conflict_adaptive, E2/E3/E4 probes, Z3 machinery | Continual runtime (Phase 3) |
| TODO18 | Vertical slice, Jacobian/ρ/σ_max separation, FrozenΘAudit, verification taxonomy, SubstrateSpec | Stability guard, determinism, substrate compilation |
| TODO19 | CEEC-Core implementation | Governance layer (keep) |
| TODO20 | 5 standalone packages (ceec-core, psi-peft, local-feedback, stability, computronium-lab) | Distribution + integration points |
| TODO21 | Publication, hygiene, boundary-gated science | Credibility + clean slate |
| TODO22 | (Skipped — subsumed by TODO23 Phase 1.2) | — |

**Nothing is discarded. Everything is reorganized into the synthesis stack.**

---

## 8. Risk Mitigation: Avoiding the "Opaque Experiment Code" Trap

| Trap | Prevention |
|------|------------|
| Synthesis produces uninterpretable coordinates | **Provenance trace mandatory**: every coordinate has a human-readable rationale (I(C,U,P) prediction + constraint filter + recipe match) |
| Validation campaigns become probe farms | **Campaign = one mechanism × problem class × constraints**; CEEC gates require `BenchmarkReproduction` + `StabilityCertificate` + `DeployabilityCheck` |
| Ledger grows without user-facing output | **Every campaign must produce a Certified Mechanism or a Cookbook Entry**; otherwise it's hygiene, not science |
| I(C,U,P) model becomes a black box | **Model is interpretable** (decision tree + logistic); features are credit/update/geometry/plasticity/depth — all human-meaningful |
| Platform only works for our niches | **Benchmark suite (Phase 5.3) covers standard tasks**; if synthesis fails on standard tasks, it's a bug, not a scope limit |

---

## 9. Execution Order (Big but Sequenced)

```
Week 1–2:  Phase 1.1–1.3  (Spec DSL + I(C,U,P)v2 + Constraint Solver)
Week 3–4:  Phase 1.4–1.6  (Recipe Registry + Synthesis Engine + Explorer)
Week 5–6:  Phase 2.1–2.4  (Lab.train + StabilityGuard + Harvest + FrozenΘAudit)
Week 7:    Phase 2.5–2.6  (CEEC Logging + Determinism Seal)
Week 8–9:  Phase 3.1–3.5  (Continual Runtime — ψ modes, boundaries, composition, Z3, audit)
Week 10–11: Phase 4.1–4.5 (Substrate Compilation + Export + Quantization + Runtime + Energy)
Week 12–13: Phase 5.1–5.5 (HF + Lightning + Benchmarks + Docs + Gallery 2.0)
Week 14:   Integration test: full loop spec→synthesize→train→adapt→export on 5 problem classes
```

**Total: ~14 weeks to a generative platform.** Each phase ships a usable increment.

---

## 10. Definition of Done (Tangible)

- [ ] `lab = Lab(); spec = lab.specify(...); system = lab.synthesize(spec)` works for 5 problem classes
- [ ] `result = lab.train(system, spec)` produces `TrainingResult` with all certificates
- [ ] `result = lab.adapt(system, task_stream)` runs continual learning with θ invariance proof
- [ ] `lab.export(system, target="onnx", substrate="memristive")` produces runnable artifact
- [ ] Benchmark suite runs on vision/NLP/tabular/continual/neuromorphic with published Pareto frontiers
- [ ] External user quickstart: `pip install computronium-lab` → result in <5 min
- [ ] CEEC ledger contains *campaign records for certified mechanisms*, not probe codes
- [ ] Zero "X-*" experiment codes in new ledger entries

---

## 11. Anti-Bureaucracy Clause (Enforced)

```text
No new CEEC features. The governance layer is complete.
No new ontology axes. The 6-axis space is complete.
No probe-level experiments. Only mechanism validation campaigns.
No beliefs without a Certified Mechanism or Cookbook Entry as payoff.
No internal metrics without a user-facing report.
```

**The measure of TODO23:**
> Can an ML engineer specify a problem, get a synthesized mechanism with a certificate, train it, adapt it continually, and deploy it — without reading our research ledger?

---

## 12. Progress Log

### Session YYYY-MM-DD — Phase 1: Problem→Mechanism Compiler
- [ ] T23.1.1 Spec DSL
- [ ] T23.1.2 I(C,U,P) Model v2
- [ ] T23.1.3 Constraint Solver
- [ ] T23.1.4 Recipe Registry
- [ ] T23.1.5 Synthesis Engine
- [ ] T23.1.6 Interactive Explorer
- [ ] T23.1.7 Exploration Budget
- [ ] T23.1.8 Autopoiesis-Ready Primitives

### Session YYYY-MM-DD — Phase 2: Unified Training Surface
- [ ] T23.2.1 Lab.train()
- [ ] T23.2.2 StabilityGuard Integration
- [ ] T23.2.3 EMA Harvest
- [ ] T23.2.4 FrozenΘAudit Automation
- [ ] T23.2.5 CEEC Campaign Logging
- [ ] T23.2.6 Determinism Seal

### Session YYYY-MM-DD — Phase 3: Continual Learning Runtime
- [ ] T23.3.1 ψ-Adaptation Modes
- [ ] T23.3.2 Task Boundary Detection
- [ ] T23.3.3 ψ-Composition
- [ ] T23.3.4 Z3 Rule Selection
- [ ] T23.3.5 Bitwise θ Invariance
- [ ] T23.3.6 Probe Hygiene for Synthesis Validation

### Session YYYY-MM-DD — Phase 4: Hardware-Aware Deployment
- [ ] T23.4.1 SubstrateSpec Compilation
- [ ] T23.4.2 Kernel Export
- [ ] T23.4.3 Quantization Pipeline
- [ ] T23.4.4 Edge Runtime
- [ ] T23.4.5 Energy/Cost Estimation

### Session YYYY-MM-DD — Phase 5: Ecosystem & Adoption
- [ ] T23.5.1 HuggingFace Integration
- [ ] T23.5.2 Lightning Callback
- [ ] T23.5.3 Benchmark Suite
- [ ] T23.5.4 Practitioner Documentation
- [ ] T23.5.5 Gallery 2.0

### Session YYYY-MM-DD — Integration Validation
- [ ] Full loop on 5 problem classes
- [ ] External quickstart verified
- [ ] CEEC ledger audit: only campaign records

---

**This redeems everything. The primitive layer is done. The governance layer is done. TODO23 builds the synthesis layer that makes them generative.**