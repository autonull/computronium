# TODO24 — Autopoietic Mechanism Discovery and Certified Research Corpus

**Status:** PLANNED (2026-09-14).  
**Created:** 2026-09-14  
**Builds on:** TODO23 (Generative Learning Mechanism Platform), TODO12–22 primitives, governance, and synthesis assets.  
**Explicit exclusion:** PyPI publishing is out of scope for TODO24. Publishing remains the final release pass after TODO24 is complete.

---

## 0. The Next Synthesis

TODO23 turned Computronium into a generative platform:

```text
ProblemSpec → Synthesis Engine → Mechanism Coordinate → Validation Campaign → Certified Mechanism → Artifact
```

That synthesis layer works over a **static catalog** of known mechanisms. It is already a major product-level advance. But the next stage is not merely adding more catalog rows by hand.

TODO24 turns the platform into a **self-improving, budgeted, campaign-governed research engine**:

1. **Autopoiesis Kernel** — implement the TODO23 autopoiesis protocols as an evolutionary search over existing 6-axis mechanism coordinates.
2. **Certified Research Corpus** — create a persistent, statistically disciplined corpus of problem classes, campaigns, controls, frontiers, and boundary records.
3. **User-Facing Research Products** — ship evolution reports, continual-learning benchmarks, substrate-transfer reports, cookbook entries, and gallery demos.

The core rule remains:

> **Evolution proposes. Campaigns dispose. Only certified mechanisms become recommendations.**

TODO24 is valuable even if evolutionary search does not discover a superior mechanism. The corpus, benchmark harness, statistical protocol, boundary ledger, and cookbook are durable products independent of any single research hypothesis.

---

## 1. What TODO23 Gives Us

| Asset | What It Provides | How TODO24 Uses It |
|---|---|---|
| **6-axis ontology** | S × G × D × P × C × U primitives, compatibility validation, factories | Mutation space is constrained to existing valid coordinates. No new axes. |
| **Lab synthesis layer** | `ProblemSpec`, `synthesize`, `explore`, catalog, viability predictor | Evolution operates on the same problem specs and candidate builders. |
| **Campaign governance** | `run_campaign`, `ledger_audit`, `promote_mechanism` | Fitness and certification use campaign evidence, not probe anecdotes. |
| **Training certificates** | Stability guard, harvest, determinism seal, CEEC logging | Evolution candidates inherit the same training guarantees. |
| **Continual ψ runtime** | ψ-only adaptation, θ bitwise invariance, ψ programs | Continual-learning benchmark compares ψ modes against matched controls. |
| **Deployment layer** | Substrate compilation, export, quantization, energy estimates | Substrate-transfer campaigns measure robustness and deployment cost. |
| **Autopoiesis protocols** | `OperatorGenome`, `MutationOperator`, `FitnessMetric`, `SelectionPolicy`, `StagnationDetector`, `Constitution` | TODO24 provides concrete, tested implementations. |

---

## 2. The Gap TODO24 Closes

| Gap | Consequence Without TODO24 | TODO24 Fix |
|---|---|---|
| Static mechanism catalog | Synthesis can only choose known rows; growth is manual | Budgeted evolutionary search over valid coordinate variants |
| Campaigns exist but are not a corpus | Results are isolated; hard to compare across problem classes | Persistent Research Corpus v1 with protocols, stats, and archives |
| ψ adaptation is implemented but not benchmarked | Continual benefits remain anecdotal | Standardized curriculum benchmark with matched controls |
| Substrate export exists but transfer robustness is not measured | Deployment claims remain qualitative | Substrate-transfer campaigns with fidelity, accuracy delta, energy estimates |
| Negative results and boundaries are scattered | Future work loses institutional memory | Boundary ledger and failure manifest as first-class outputs |
| Predictor corpus can drift | `I(C,U,P)` model becomes stale or overfit | Corpus-driven refit/revalidation loop with recorded boundaries |

---

## 3. Tangible Benefits

TODO24 must produce concrete user-facing value, not only research infrastructure.

| Benefit | What the User Gets |
|---|---|
| **`lab.plan_evolution` / `lab.run_evolution`** | Budgeted evolutionary mechanism search over existing 6-axis coordinates |
| **Evolution reports** | Lineage, mutation trace, provenance, frontier growth, negative results |
| **Certified Research Corpus v1** | Reproducible task classes, measurement protocols, statistical summaries |
| **Frontier archive** | Persistent Pareto frontiers that synthesis and explorer can reuse |
| **Continual benchmark report** | ψ-only adaptation compared against frozen and θ-update controls |
| **Substrate-transfer report** | Digital → INT8 / ternary / memristive-simulated robustness metrics |
| **Mechanism Cookbook v1** | Certified entries with constraints, evidence, boundaries, and deployment notes |
| **Boundary ledger** | Explicit record of what cannot yet be measured and why |
| **Gallery 3.0 / D24 demo** | Visible, locked demonstration of evolutionary search and corpus reports |

Even if no evolved mechanism beats the existing catalog, TODO24 still ships:

- a measurement corpus,
- benchmark harnesses,
- statistical reports,
- deployment transfer reports,
- cookbook entries,
- negative-result records,
- and a clean extension path for future research.

---

## 4. Research Hypotheses

These are hypotheses to be tested, not claims.

| ID | Hypothesis | Evidence Required |
|---|---|---|
| **H24.1** | Evolutionary search over valid 6-axis coordinates can produce non-dominated candidates not present in the initial catalog for at least one problem class. | Frontier archive comparison: initial catalog frontier vs post-evolution frontier. |
| **H24.2** | Campaign-backed fitness prevents quick-task overfitting better than predictor-only search. | Compare surrogate-ranked candidates against campaign-validated outcomes. |
| **H24.3** | ψ-only adaptation improves task-switch speed relative to θ fine-tuning under matched compute on at least one synthetic curriculum. | Paired statistical test across seeds with equal episode/compute budgets. |
| **H24.4** | Substrate-transfer robustness is mechanism-dependent and can be ranked by fidelity, accuracy delta, and export success. | Transfer campaign across mechanisms and substrate constraints. |
| **H24.5** | Stability and resource constraints can be used as hard search constraints without collapsing the candidate space. | Constitution rejection report plus surviving certified candidates. |
| **H24.6** | Corpus-driven refit improves or honestly bounds the `I(C,U,P)` viability model. | Held-out evaluation before/after corpus expansion, or recorded sampling boundary. |

---

## 5. Target API

The target API is additive and must not break TODO23.

```python
from computronium_lab import (
    Lab,
    ProblemSpec,
    EvolutionBudget,
    EvolutionSpec,
)

lab = Lab(record_ledger="ceec/todo24.sqlite3")

spec = lab.specify(
    task="flat_classification",
    dataset="synthetic_calibrated",
    constraints=dict(
        compute_budget="cpu_quick",
        latency_ms=50,
        memory_gb=2,
        continual=True,
        local_credit=False,
        precision="float32",
        substrate="digital",
    ),
    objectives=["accuracy", "adaptation_speed", "stability"],
)

plan = lab.plan_evolution(
    spec,
    evolution=EvolutionSpec(
        population=6,
        generations=3,
        seed_candidates=[
            "backprop_mlp",
            "temporal_psi_task_switcher",
            "role_split_mlp",
            "ntm_classifier",
        ],
        objectives=["accuracy", "adaptation_speed", "stability"],
        budget=EvolutionBudget(
            max_campaigns=12,
            max_epochs_per_campaign=20,
            max_seeds=3,
        ),
    ),
)

report = lab.run_evolution(plan)

report.best_candidates
report.frontier_archive
report.lineage
report.negative_results
report.cookbook_entries
```

Continual benchmark target:

```python
continual_report = lab.benchmark_continual(
    mechanism="temporal_psi_task_switcher",
    curriculum="two_task_switch",
    modes=["temporal", "role_split", "conflict_adaptive"],
    controls=["frozen_no_psi", "theta_finetune_matched_compute"],
    seeds=(0, 1, 2),
)
```

Substrate-transfer target:

```python
transfer_report = lab.benchmark_substrate_transfer(
    mechanism="backprop_mlp",
    source_substrate="digital",
    target_constraints=["int8", "ternary", "memristive"],
    seeds=(0, 1, 2),
)
```

---

## 6. Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│  RESEARCH & AUTOPOIESIS LAYER (TODO24)                      │
│  EvolutionSpec → Genome → Mutation → Fitness → Selection    │
│  Research Corpus → Campaigns → Statistics → Frontier Archive│
│  Cookbook / Boundary Ledger / Reports                       │
├─────────────────────────────────────────────────────────────┤
│  SYNTHESIS LAYER (TODO23)                                   │
│  ProblemSpec → synthesize/explore → train/adapt/export      │
├─────────────────────────────────────────────────────────────┤
│  GOVERNANCE LAYER (CEEC-Core)                               │
│  Campaign artifacts, gates, beliefs, audits                 │
├─────────────────────────────────────────────────────────────┤
│  PRIMITIVE LAYER (TODO12–22)                                │
│  6-axis ontology, substrates, joint systems, audits         │
└─────────────────────────────────────────────────────────────┘
```

TODO24 does **not** replace TODO23. It adds a research and discovery layer above it.

---

## 7. Scope and Non-Goals

### In Scope

- Concrete implementations of the autopoiesis protocols.
- Evolutionary search constrained to existing ontology primitives and Lab construction paths.
- Persistent research corpus for synthetic and already-implemented task tiers.
- Continual-learning curriculum benchmark.
- Substrate-transfer benchmark using existing simulated substrate constraints.
- Statistical summaries, frontier archives, boundary records, and cookbook generation.
- Gallery/demo integration.
- Ledger-audited campaign records for evolution and corpus work.

### Out of Scope

- PyPI publishing.
- New ontology axes.
- New CEEC-Core features.
- Physical hardware validation.
- Large external dataset campaigns.
- New biological or physical claims.
- Manual addition of exotic mechanisms unless they already have a valid Lab construction path and campaign evidence.

---

## 8. Phases

### Phase 0: Research Baseline and Corpus Schema

**Goal:** freeze the TODO23 operating point and create durable research abstractions.

| Task | Deliverable | Depends On |
|---|---|---|
| **T24.0.1 Baseline Freeze** | `docs/research/todo24_baseline.md`: catalog hash, predictor corpus hash, calibrated task parameters, known campaign budgets, known boundaries | TODO23 |
| **T24.0.2 Research Schema** | `computronium_lab.research`: `CorpusSpec`, `ProblemClassProtocol`, `MeasurementProtocol`, `StatisticalSummary`, `BoundaryRecord` | T24.0.1 |
| **T24.0.3 Budget Tiers** | `smoke`, `quick`, `certified` budget definitions; only `certified` can support cookbook or belief promotion | T24.0.2 |
| **T24.0.4 Ledger Record Types** | Lab-level artifact types: `evolution_generation`, `evolution_candidate`, `research_corpus_summary`, `boundary_record`; update `ledger_audit` allowlist | T24.0.2 |
| **T24.0.5 Corpus Directories** | Stable data/result paths: `data/research/todo24/`, `results/todo24/`, docs output | T24.0.2 |

**Success criterion:** baseline document exists; schema tests pass; ledger audit still rejects `X-*` probe codes.

---

### Phase 1: Autopoiesis Kernel

**Goal:** implement the TODO23 autopoiesis protocols as concrete, testable components.

| Task | Deliverable | Depends On |
|---|---|---|
| **T24.1.1 CoordinateGenome** | Implements `OperatorGenome`; contains mechanism name, 6-axis coordinate, recipe parameters, training options, lineage, hash | Phase 0 |
| **T24.1.2 SafeMutationOperator** | Implements `MutationOperator`; mutates only through valid Lab construction paths | T24.1.1 |
| **T24.1.3 Constitution** | Implements `Constitution`; enforces `ProblemSpec` constraints, budgets, compatibility, and no-unsupported-construction rules | T24.1.1 |
| **T24.1.4 SurrogateFitness** | Implements `FitnessMetric`; cheap predictor + recipe-prior + resource-estimate screen | T24.1.1 |
| **T24.1.5 CampaignFitness** | Wraps existing campaign runners; returns standardized objective vector and gate outcomes | T24.1.4 |
| **T24.1.6 ParetoSelection** | Implements `SelectionPolicy`; non-dominated sorting, crowding, diversity preservation | T24.1.5 |
| **T24.1.7 StagnationDetector** | Implements `StagnationDetector`; detects no frontier growth, no new certified entries, or exhausted budget | T24.1.6 |

**Mutation operators must be safe by construction.**

Examples:

| Mutation | Allowed When |
|---|---|
| Credit swap: backprop ↔ FA ↔ FF ↔ PEPITA | Constraint policy permits; geometry supports; catalog/builder exists |
| Update swap: Euclidean ↔ Muon/orthogonal ↔ spectral/natural | Update primitive compatible with credit and geometry |
| Plasticity swap: Null ↔ temporal ↔ role_split ↔ routing/fast-weight | Geometry supports; task class supports; adaptation mode is constructible |
| Depth/width adjustment | Memory/latency estimates remain within constraints |
| Precision/quantization mutation | Export/substrate constraint path exists |
| Substrate constraint mutation | `compile_substrate` / `apply_substrate_constraints` supports target |

**Success criterion:** protocol conformance tests pass; deterministic seeded mutation works; invalid candidates are rejected before training.

---

### Phase 2: Evolutionary Lab Surface

**Goal:** expose evolution as a first-class Lab capability.

| Task | Deliverable | Depends On |
|---|---|---|
| **T24.2.1 EvolutionSpec / EvolutionBudget** | Dataclasses for population, generations, objectives, budgets, seed candidates | Phase 1 |
| **T24.2.2 `lab.plan_evolution`** | Dry-run planner returning candidate genomes, expected budgets, and constitutional checks | T24.2.1 |
| **T24.2.3 `lab.run_evolution`** | Executes generations; forks systems; records artifacts; supports resume | T24.2.2 |
| **T24.2.4 EvolutionReport** | Best candidates, frontier, lineage, mutation trace, negative results, ledger references | T24.2.3 |
| **T24.2.5 Frontier Archive** | Persistent JSON/SQLite archive of measured Pareto points and hypervolume summaries | T24.2.3 |
| **T24.2.6 Synthesis Integration** | Optional `synthesize(..., include_evolved=True)` uses archived frontier candidates | T24.2.5 |

**Evolution report must include:**

- initial population,
- generation summaries,
- candidate genome hashes,
- parent lineage,
- mutation operations,
- config diffs,
- predictor viability,
- campaign outcomes,
- gate outcomes,
- frontier deltas,
- negative results.

**Success criterion:** a smoke evolution (`population=2`, `generations=1`) runs end-to-end on CPU, produces an audited report, and does not mutate parent systems in place.

---

### Phase 3: Certified Research Corpus v1

**Goal:** create a persistent research basis that can grow without rewriting the platform.

| Task | Deliverable | Depends On |
|---|---|---|
| **T24.3.1 Problem Classes** | Standardized runners for: flat classification, sequence tasks, NCA state prediction, continual switch, substrate transfer | Phase 0 |
| **T24.3.2 Measurement Protocol Runner** | Multi-seed, equal-compute, val-split, matched-control execution | T24.3.1 |
| **T24.3.3 Statistical Summary Module** | Means, stds, confidence intervals, paired tests, effect sizes, one-sided promotion-compatible bounds | T24.3.2 |
| **T24.3.4 Catalog Re-Measurement Pass** | Re-measure applicable catalog rows on corpus tasks using Lab construction paths | T24.3.2 |
| **T24.3.5 Frontier Archive Integration** | Corpus results append to the same frontier archive used by evolution | T24.3.3 |
| **T24.3.6 Boundary Ledger** | Record rows/problem classes that cannot be measured yet and why | T24.3.1 |

**Initial problem classes:**

| Problem Class | Existing Basis | Notes |
|---|---|---|
| `flat_classification` | calibrated synthetic task | Primary quick-tier classification corpus |
| `sequence_last_symbol` | `sequence_task` | NTM sequence tier |
| `sequence_threshold` | `sequence_task` | NTM sequence tier |
| `nca_state_prediction` | `grid_transition_task` | k-step rollout task; avoids one-step degeneracy |
| `continual_switch` | ψ adaptation runtime | Synthetic task stream with boundary |
| `substrate_transfer` | deployment layer | Digital-trained model evaluated under substrate constraints |

**Success criterion:** corpus report can be regenerated from raw campaign artifacts; statistical summaries are deterministic; catalog metadata updates only come from campaign evidence.

---

### Phase 4: Continual Adaptation Benchmark

**Goal:** turn ψ-only adaptation from a capability into a measured, comparable benchmark.

| Task | Deliverable | Depends On |
|---|---|---|
| **T24.4.1 CurriculumSpec** | Task-stream generator: task A → task B, optional distractors, deterministic seeds | Phase 3 |
| **T24.4.2 Baselines and Controls** | ψ modes, frozen no-ψ control, θ fine-tune matched-compute control | T24.4.1 |
| **T24.4.3 Adaptation Metrics** | Episodes to threshold, final accuracy, stability verdicts, θ invariance proofs, ψ digest changes | T24.4.2 |
| **T24.4.4 A/B Campaign** | Paired statistical comparison across seeds and modes | T24.4.3 |
| **T24.4.5 Continual Cookbook Entries** | Certified entries or honest negative results | T24.4.4 |

**ψ arms must preserve bitwise θ invariance.**  
**θ fine-tune control must not be compared as if it were ψ-only.** It exists to measure trade-offs under matched compute.

**Success criterion:** `lab.benchmark_continual` returns a report with per-mode metrics, control metrics, statistical summary, θ invariance proofs, and ledger references.

---

### Phase 5: Substrate Robustness and Deployment Corpus

**Goal:** make deployment robustness measurable rather than descriptive.

| Task | Deliverable | Depends On |
|---|---|---|
| **T24.5.1 Transfer Campaign** | Train on digital substrate; apply/export INT8, ternary, memristive-simulated constraints; evaluate val accuracy and fidelity | Phase 3 |
| **T24.5.2 Robustness Score** | Composite record: accuracy delta, fidelity max-abs-diff, export success, energy estimate, constraint preservation | T24.5.1 |
| **T24.5.3 Evolutionary Substrate Mutation** | Optional genome mutations over substrate constraints where construction/export exists | Phase 1, T24.5.1 |
| **T24.5.4 Deployment Cookbook Entries** | Certified deployment recommendations or boundary records | T24.5.2 |

**Important honesty constraint:** substrate models remain simulated unless physical hardware validation is later added. TODO24 must not imply hardware-measured results.

**Success criterion:** for at least three mechanisms and three target constraint sets, the platform produces transfer reports with manifest, fidelity, accuracy delta, and energy estimate.

---

### Phase 6: Research Reports, Beliefs, and Cookbook v1

**Goal:** convert corpus and evolution artifacts into durable scientific and practitioner outputs.

| Task | Deliverable | Depends On |
|---|---|---|
| **T24.6.1 Registered Hypothesis Reports** | `docs/research/todo24/hypotheses/*.md`: hypothesis, protocol, status, evidence refs | Phase 3 |
| **T24.6.2 Automated Report Generator** | Markdown/HTML/JSON reports from corpus, evolution, campaign, and frontier artifacts | Phase 3–5 |
| **T24.6.3 Belief Promotion for Evolved Mechanisms** | Use existing `promote_mechanism` pipeline where campaigns pass; honest refusal otherwise | Phase 3–5 |
| **T24.6.4 Failure Manifesto** | Structured negative results: failed candidates, failed mutations, failed transfers, task-class mismatches | Phase 2–5 |
| **T24.6.5 Ledger Audit** | All TODO24 artifacts pass `ledger_audit`; zero `X-*` probe codes | All phases |

**Cookbook v1 entry format:**

```text
Mechanism:
Problem class:
Constraints:
Coordinate:
Evidence:
Certificates:
Known boundaries:
Deployment notes:
```

**Success criterion:** at least one cookbook entry or one certified negative result exists per completed problem class; belief promotion either succeeds with evidence or fails with a recorded reason.

---

### Phase 7: Demo, Gallery, and Documentation

**Goal:** make TODO24 visible, locked, and reproducible.

| Task | Deliverable | Depends On |
|---|---|---|
| **T24.7.1 D24 Evolution Demo** | Locked integration demo test showing plan → evolve → campaign → frontier/report | Phase 2 |
| **T24.7.2 Gallery 3.0 Figures** | Frontier growth, lineage, continual adaptation curves, substrate transfer plots | Phase 3–6 |
| **T24.7.3 Practitioner Documentation** | Evolution quickstart, research corpus guide, cookbook guide, boundary ledger guide | Phase 6 |
| **T24.7.4 Demo Lock and Manifest** | Gallery manifest re-pinned and demo lock green | T24.7.1–T24.7.3 |

**Success criterion:** `pytest -k demo` and gallery lock pass; documentation snippets smoke-verify.

---

## 9. Measurement Protocol

All TODO24 measurements must follow this protocol.

### 9.1 Seeds and Determinism

- Minimum seeds for `quick`: 2, but preferably 3.
- Minimum seeds for `certified`: 3.
- Deterministic task generators per seed.
- Record seed, config hash, genome hash, and campaign hash.
- Determinism seal is optional for expensive campaigns but required for promoted mechanisms when affordable.

### 9.2 Controls

Every claim-bearing campaign must have an appropriate control:

| Campaign Type | Control |
|---|---|
| Classification | Label-permuted training, evaluated on unpermuted val split |
| Sequence | Episode label-shuffled training, evaluated on unpermuted val episodes |
| State prediction | Label-shuffled or rollout-target-shuffled control |
| Continual ψ | Frozen no-ψ control and/or θ fine-tune matched-compute control |
| Substrate transfer | Unconstrained digital baseline |

### 9.3 Equal Compute

Comparisons must normalize compute:

- same number of epochs or same number of optimizer steps,
- same batch count where applicable,
- ψ adaptation episodes counted explicitly,
- control arms receive equal training budget.

### 9.4 Metrics

Core objective vector:

```text
accuracy / val_accuracy          maximize
adaptation_episodes_to_threshold minimize
stability_guard_pass             boolean
stability_margin                 context-dependent
latency_estimate                 minimize
memory_estimate                  minimize
energy_estimate                  minimize
substrate_fidelity_delta         minimize
theta_invariance                 boolean for ψ arms
export_success                   boolean
```

### 9.5 Statistics

- Report mean and standard deviation across seeds.
- Use paired tests when comparing matched arms.
- Use confidence intervals or one-sided lower bounds for promotion.
- Do not promote on smoke-tier results.
- Do not weaken gates to fit a budget; lengthen the budget or record a boundary.

---

## 10. Budget Tiers

| Tier | Purpose | Allowed Outcomes |
|---|---|---|
| **smoke** | CI, wiring, regression | Pass/fail only; no beliefs, no cookbook |
| **quick** | local iteration, candidate screening | Frontier hints, exploratory notes; no promotion |
| **certified** | campaign evidence | Cookbook entries, belief promotion attempts, publication-grade internal reports |

Example budget caps:

```python
smoke = EvolutionBudget(
    max_campaigns=2,
    max_epochs_per_campaign=1,
    max_seeds=1,
)

quick = EvolutionBudget(
    max_campaigns=8,
    max_epochs_per_campaign=20,
    max_seeds=3,
)

certified = EvolutionBudget(
    max_campaigns=24,
    max_epochs_per_campaign=task_specific,
    max_seeds=3,
)
```

Task-specific certified epoch budgets should inherit the stable operating points discovered in TODO23, for example:

- flat classification: 20 epochs where stable,
- sequence last_symbol: campaign-defined, often >60 epochs,
- NCA state prediction: 100–300 epochs depending on certification need,
- continual adaptation: fixed episode budget, not open-ended training.

---

## 11. CEEC and Ledger Integration

TODO24 does not modify CEEC-Core. It uses the existing governance layer at the campaign level.

### Allowed TODO24 artifact types

| Artifact Type | Meaning |
|---|---|
| `validation_campaign` | Existing campaign record |
| `mechanism_belief` | Existing promoted belief record |
| `exploratory_synthesis` | Existing exploratory synthesis record |
| `lab_comparison` | Existing comparison record |
| `evolution_generation` | Generation-level summary: population, frontier, stagnation, budget |
| `evolution_candidate` | Candidate genome, mutation trace, fitness/campaign references |
| `research_corpus_summary` | Corpus-level statistical summary |
| `boundary_record` | Explicit record of a blocked or impossible measurement |

### Ledger rules

- No `X-*` probe codes.
- No belief without campaign evidence.
- No cookbook entry without certified campaign or certified negative result.
- Failed campaigns are retained as evidence.
- Evolution candidates that never pass screening may appear in generation summaries, but they do not become beliefs.

---

## 12. Risk Mitigation

| Risk | Mitigation |
|---|---|
| Evolution becomes a compute sink | Hard budgets, smoke/quick/certified tiers, surrogate screens, stagnation detector |
| Search overfits the quick task | Val splits, controls, multi-task corpus, certified tier for claims |
| Evolved coordinates are opaque | Mandatory lineage, mutation trace, config diff, human-readable rationale |
| Ledger becomes noisy | Only campaign-like artifacts; audit rejects probe codes |
| Invalid coordinates waste campaigns | `SystemConfig.validate()` and constitution checks before training |
| False positives from seed variance | Multi-seed campaigns, paired statistics, promotion thresholds |
| Negative results get lost | Boundary ledger and failure manifesto are required outputs |
| New task classes destabilize core | Problem classes implemented through protocols, not core edits |
| Substrate results overclaim | Simulated/estimated labels mandatory; no hardware-measured claims |
| Evolution fails to improve catalog | TODO24 still ships corpus, benchmark, cookbook, and boundaries |

---

## 13. Definition of Done

- [ ] `computronium_lab.research` schema exists and is tested.
- [ ] Autopoiesis protocol implementations exist and pass conformance tests.
- [ ] `lab.plan_evolution` returns a dry-run plan without training.
- [ ] `lab.run_evolution` runs a smoke evolution end-to-end.
- [ ] Evolution reports include lineage, mutation trace, frontier, and negative results.
- [ ] Frontier archive persists measured Pareto points and hypervolume summaries.
- [ ] Research Corpus v1 includes at least three runnable problem classes.
- [ ] Statistical summaries include seeds, controls, and paired comparisons where applicable.
- [ ] Continual benchmark compares ψ modes against controls with θ invariance proofs for ψ arms.
- [ ] Substrate-transfer report covers at least three mechanisms and three constraint sets.
- [ ] Cookbook v1 contains certified entries or certified negative results.
- [ ] Boundary ledger records blocked items with reasons.
- [ ] Ledger audit passes with zero `X-*` codes.
- [ ] D24 demo and gallery lock are green.
- [ ] New modules pass ruff format/check and strict pyright.
- [ ] Full test suite remains green or legacy failures are explicitly recorded.
- [ ] No PyPI publishing work is included.

---

## 14. Extension Model: How TODO24 Keeps Growing

TODO24 establishes stable extension points so future work can grow without destabilizing the platform.

### Add a new problem class

Implement:

```text
ProblemClassProtocol
  - name
  - deterministic task generator
  - default metrics
  - campaign runner
  - control generator
```

No core evolution changes required.

### Add a new mechanism

Provide:

```text
MechanismCandidate
  - catalog row
  - config builder or recipe builder
  - SystemConfig.validate() compatibility
  - measured campaign evidence
```

No manual metadata without campaign evidence.

### Add a new objective

Provide:

```text
FitnessMetric component
  - objective name
  - direction
  - normalization
  - campaign source field
```

Selection and frontier archive consume it generically.

### Add a new mutation

Provide:

```text
MutationOperator
  - genome transform
  - constitutional checks
  - provenance description
```

No mutation may bypass compatibility validation.

### Add a new substrate constraint

Provide:

```text
compile/export path
  - constraint application
  - fidelity measurement
  - energy estimate label
  - transfer campaign support
```

No physical-hardware claims without hardware validation.

---

## 15. Anti-Bureaucracy Clause

```text
No PyPI publishing in TODO24.
No new ontology axes.
No new CEEC-Core features.
No probe-level beliefs.
No cookbook entry without campaign evidence or certified negative result.
No catalog metadata without a construction path and campaign evidence.
No evolved candidate becomes a recommendation solely because it was mutated.
No task class is forced into an incompatible geometry.
No substrate result is described as hardware-measured unless physical validation exists.
No internal metric ships without a user-facing report or boundary record.
```

---

## 16. The Measure of TODO24

> **Can a practitioner specify a problem class and budget, receive catalog or evolved mechanisms with campaign certificates, compare them on a persistent research corpus, benchmark continual adaptation and substrate transfer, and extend the corpus without reading the internal research ledger?**

If yes, TODO24 is complete.

---

## 17. Progress Log

### Session YYYY-MM-DD — Phase 0: Research Baseline and Corpus Schema
- [ ] T24.0.1 Baseline Freeze
- [ ] T24.0.2 Research Schema
- [ ] T24.0.3 Budget Tiers
- [ ] T24.0.4 Ledger Record Types
- [ ] T24.0.5 Corpus Directories

### Session YYYY-MM-DD — Phase 1: Autopoiesis Kernel
- [ ] T24.1.1 CoordinateGenome
- [ ] T24.1.2 SafeMutationOperator
- [ ] T24.1.3 Constitution
- [ ] T24.1.4 SurrogateFitness
- [ ] T24.1.5 CampaignFitness
- [ ] T24.1.6 ParetoSelection
- [ ] T24.1.7 StagnationDetector

### Session YYYY-MM-DD — Phase 2: Evolutionary Lab Surface
- [ ] T24.2.1 EvolutionSpec / EvolutionBudget
- [ ] T24.2.2 lab.plan_evolution
- [ ] T24.2.3 lab.run_evolution
- [ ] T24.2.4 EvolutionReport
- [ ] T24.2.5 Frontier Archive
- [ ] T24.2.6 Synthesis Integration

### Session YYYY-MM-DD — Phase 3: Certified Research Corpus v1
- [ ] T24.3.1 Problem Classes
- [ ] T24.3.2 Measurement Protocol Runner
- [ ] T24.3.3 Statistical Summary Module
- [ ] T24.3.4 Catalog Re-Measurement Pass
- [ ] T24.3.5 Frontier Archive Integration
- [ ] T24.3.6 Boundary Ledger

### Session YYYY-MM-DD — Phase 4: Continual Adaptation Benchmark
- [ ] T24.4.1 CurriculumSpec
- [ ] T24.4.2 Baselines and Controls
- [ ] T24.4.3 Adaptation Metrics
- [ ] T24.4.4 A/B Campaign
- [ ] T24.4.5 Continual Cookbook Entries

### Session YYYY-MM-DD — Phase 5: Substrate Robustness and Deployment Corpus
- [ ] T24.5.1 Transfer Campaign
- [ ] T24.5.2 Robustness Score
- [ ] T24.5.3 Evolutionary Substrate Mutation
- [ ] T24.5.4 Deployment Cookbook Entries

### Session YYYY-MM-DD — Phase 6: Research Reports, Beliefs, and Cookbook v1
- [ ] T24.6.1 Registered Hypothesis Reports
- [ ] T24.6.2 Automated Report Generator
- [ ] T24.6.3 Belief Promotion for Evolved Mechanisms
- [ ] T24.6.4 Failure Manifesto
- [ ] T24.6.5 Ledger Audit

### Session YYYY-MM-DD — Phase 7: Demo, Gallery, and Documentation
- [ ] T24.7.1 D24 Evolution Demo
- [ ] T24.7.2 Gallery 3.0 Figures
- [ ] T24.7.3 Practitioner Documentation
- [ ] T24.7.4 Demo Lock and Manifest

### Session YYYY-MM-DD — Integration Validation
- [ ] Smoke evolution end-to-end
- [ ] Corpus report regenerated from artifacts
- [ ] Continual benchmark report validated
- [ ] Substrate transfer report validated
- [ ] Ledger audit clean
- [ ] Gallery/demo locks green

