# TODO24 — Autopoietic Mechanism Discovery and Certified Research Corpus

**Status:** PLANNED — ready to execute.  
**Created:** 2026-09-13  
**Aligned:** 2026-09-13 (codebase + CEEC verification pass; all referenced identifiers verified against implementations).  
**Builds on:** TODO23 (Generative Learning Mechanism Platform), TODO12–22 primitives, CEEC-Core governance (`packages/ceec-core`), and synthesis assets.  
**Explicit exclusion:** PyPI publishing is out of scope for TODO24. Publishing remains the final release pass after TODO24 is complete.

---

## 0. The Next Synthesis

**Program goal:** run the H24.1–H24.6 experiments and obtain measured answers. CEEC work in TODO24 is instrument improvement serving those experiments and their successors — never an end in itself. Compartments stay pure (CEEC governs and records; the AutoScientist proposes and sweeps; the evolution kernel searches) and join only through thin adapters (T24.2.8).

TODO23 turned Computronium into a generative platform:

```text
ProblemSpec → Synthesis Engine → Mechanism Coordinate → Validation Campaign → Certified Mechanism → Artifact
```

That synthesis layer works over a **static catalog** of known mechanisms. It is already a major product-level advance. But the next stage is not merely adding more catalog rows by hand.

TODO24 turns the platform into a **self-improving, budgeted, campaign-governed research engine**:

1. **Autopoiesis Kernel** — implement the TODO23 autopoiesis protocols as an evolutionary search over existing 6-axis mechanism coordinates.
2. **Certified Research Corpus** — create a persistent, statistically disciplined corpus of problem classes, campaigns, controls, frontiers, and measurement blocks.
3. **User-Facing Research Products** — ship evolution reports, continual-learning benchmarks, substrate-transfer reports, cookbook entries, and gallery demos.

The core rule remains:

> **Evolution proposes. Campaigns dispose. Only certified mechanisms become recommendations.**

TODO24 is valuable even if evolutionary search does not discover a superior mechanism. The corpus, benchmark harness, statistical protocol, measurement-block ledger, and cookbook are durable products independent of any single research hypothesis.

---

## 1. What TODO23 Gives Us

| Asset | What It Provides | How TODO24 Uses It |
|---|---|---|
| **6-axis ontology** | S × G × D × P × C × U primitives, compatibility validation, factories | Mutation space is constrained to existing valid coordinates. No new axes. |
| **Lab synthesis layer** | `ProblemSpec`, `synthesize`, `explore`, catalog, viability predictor | Evolution operates on the same problem specs and candidate builders. |
| **Campaign governance** | `run_campaign`, `ledger_audit`, `promote_mechanism`; ceec-core already implements the full CEEC-Core object model (Experiment, Derived, Decision, GateOutcome, StatusChange, Goal, CalibrationRecord) plus the §22 selection loop (`ceec.selection`) — the Lab currently exercises only Artifact + scalar Evidence + GateOutcome + Belief + Decision | Fitness and certification use campaign evidence, not probe anecdotes; TODO24 grows the usage surface to the full object model and lands targeted CEEC instrument improvements (T24.0.6, T24.6.6). |
| **Training certificates** | Stability guard, harvest, determinism seal, CEEC logging | Evolution candidates inherit the same training guarantees. |
| **Continual ψ runtime** | ψ-only adaptation, θ bitwise invariance, ψ programs | Continual-learning benchmark compares ψ modes against matched controls. |
| **Deployment layer** | Substrate compilation, export, quantization, energy estimates | Substrate-transfer campaigns measure robustness and deployment cost. |
| **Autopoiesis protocols** | `computronium.autopoiesis.protocols`: `OperatorGenome`, `MutationOperator`, `FitnessMetric`, `SelectionPolicy`, `StagnationDetector`, `Constitution` (runtime-checkable, zero implementation) | TODO24 provides concrete, tested implementations. |

---

## 2. The Gap TODO24 Closes

| Gap | Consequence Without TODO24 | TODO24 Fix |
|---|---|---|
| Static mechanism catalog | Synthesis can only choose known rows; growth is manual | Budgeted evolutionary search over valid coordinate variants |
| Campaigns exist but are not a corpus | Results are isolated; hard to compare across problem classes | Persistent Research Corpus v1 with protocols, stats, and archives |
| ψ adaptation is implemented but not benchmarked | Continual benefits remain anecdotal | Standardized curriculum benchmark with matched controls |
| Substrate export exists but transfer robustness is not measured | Deployment claims remain qualitative | Substrate-transfer campaigns with fidelity, accuracy delta, energy estimates |
| Negative results and known limitations are scattered | Future work loses institutional memory | Measurement-block ledger and failure manifest as first-class outputs |
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
| **Mechanism Cookbook v1** | Certified entries with constraints, evidence, known limitations, and deployment notes |
| **Measurement-block ledger** | Explicit record of what cannot yet be measured and why |
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
    Constraints,
    EvolutionBudget,
    EvolutionSpec,
    Lab,
    ProblemSpec,
)

lab = Lab(record_ledger="scratch/todo24.sqlite3")

spec = lab.specify(
    task="flat_classification",
    dataset="gaussian_blob",  # the TODO23 calibrated quick tier
    constraints=Constraints(
        compute_budget="cpu_quick",
        latency_ms=50,
        memory_gb=2,
        continual=True,
        local_credit=False,
        precision="float32",
        substrate="digital",
    ),
    objectives=("accuracy", "adaptation_speed", "stability"),
)

plan = lab.plan_evolution(
    spec,
    evolution=EvolutionSpec(
        population=6,
        generations=3,
        seed_candidates=(
            "backprop_mlp",
            "temporal_psi_task_switcher",
            "role_split_muon_readout",
            "ntm_classifier",
        ),
        objectives=("accuracy", "adaptation_speed", "stability"),
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
    modes=("temporal", "role_split", "conflict_adaptive"),
    controls=("frozen_no_psi", "theta_finetune_matched_compute"),
    seeds=(0, 1, 2),
)
```

Substrate-transfer target:

```python
transfer_report = lab.benchmark_substrate_transfer(
    mechanism="backprop_mlp",
    source_substrate="digital",
    target_constraints=("int8", "ternary", "memristive"),
    seeds=(0, 1, 2),
)
```

**Existing-surface alignment.** Everything above exists today except `EvolutionBudget`, `EvolutionSpec`, `plan_evolution`, `run_evolution`, `benchmark_continual`, and `benchmark_substrate_transfer`. `Constraints`/`ProblemSpec` are exported at the `computronium_lab` root; `lab.specify` validates `Constraints` fields and the `KNOWN_OBJECTIVES` set (`accuracy`, `adaptation_speed`, `stability`, `latency`, `memory`). Seed candidates are catalog rows (`role_split_mlp` does not exist; the row is `role_split_muon_readout`). Continual `modes` are the `AdaptationMode` values (`temporal`, `role_split`, `conflict_adaptive`). Transfer targets map onto existing deployment surfaces: `int8`/`ternary` are the `Quantization` paths, `memristive` is a device model via `compile_substrate` + `apply_substrate_constraints`, with `substrate_report` and `estimate_energy` (simulated/estimated tiers) supplying fidelity and energy.

---

## 6. Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│  RESEARCH & AUTOPOIESIS LAYER (TODO24)                      │
│  EvolutionSpec → Genome → Mutation → Fitness → Selection    │
│  Research Corpus → Campaigns → Statistics → Frontier Archive│
│  Cookbook / Measurement-Block / Reports                     │
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

Compartments stay pure: CEEC governs and records (never executes), the AutoScientist proposes and sweeps (no CEEC dependency), the evolution kernel searches the Lab catalog — joined only by thin adapters (T24.2.8, §14).

---

## 7. Scope and Non-Goals

### In Scope

- Concrete implementations of the autopoiesis protocols.
- Evolutionary search constrained to existing ontology primitives and Lab construction paths.
- Persistent research corpus for synthetic and already-implemented task tiers.
- Continual-learning curriculum benchmark.
- Substrate-transfer benchmark using existing simulated substrate constraints.
- Statistical summaries, frontier archives, measurement blocks, and cookbook generation.
- Gallery/demo integration.
- Ledger-audited campaign records for evolution and corpus work.

### Out of Scope

- PyPI publishing.
- New ontology axes.
- CEEC-Core changes beyond the instrument improvements in T24.0.6/T24.6.6.
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
| **T24.0.1 Baseline Freeze** | `docs/research/todo24_baseline.md`: catalog hash, predictor corpus hash, calibrated task parameters, known campaign budgets, known limitations | TODO23 |
| **T24.0.2 Research Schema** | `computronium_lab.research`: `CorpusSpec`, `ProblemClassProtocol`, `MeasurementProtocol`, `StatisticalSummary`, `MeasurementBlock` — mapped onto ceec-core objects already implemented: `MeasurementProtocol` → `Experiment` pre-registration (`ceec.bootstrap.experiment_from_config`), `StatisticalSummary` → `Derived` (`record_derived`), `MeasurementBlock` → artifact + `inert`/`missing` evidence (notes mandatory) | T24.0.1 |
| **T24.0.3 Budget Tiers** | `smoke`, `quick`, `certified` budget definitions (RESEARCH3 E-1 ladder mapping: smoke→smoke, quick→pilot, certified→full); only `certified` can support cookbook or belief promotion; `certified` is shorthand for 'campaign gates passed', never a belief status | T24.0.2 |
| **T24.0.4 Ledger Record Types** | Lab-level artifact types: `evolution_generation`, `evolution_candidate`, `research_corpus_summary`, `measurement_block` (Artifact.type strings; `PREFIX_BY_KIND` untouched); update `ledger_audit` allowlist; new records use structured evidence kinds (vector/curve/frontier with axes+values_ref — enforced by `ceec.models`), never scalar-only | T24.0.2 |
| **T24.0.5 Corpus Directories** | Stable data/result paths: `data/research/todo24/`, `results/todo24/<problem_class>/<seed>/<timestamp>/` with `manifest.json` (RESEARCH3 E-3 layout), docs output | T24.0.2 |
| **T24.0.6 CEEC Instrument Improvements** | Structured-evidence emission helpers (curve/vector/frontier from run history); `ledger_audit` delegates to `ceec.audit` + the lab allowlist; `GateStatus` reconciled to the spec vocabulary (`passed`/`failed`/`unknown`/`waived_with_justification`), lab writers updated | T24.0.2 |

**Success criterion:** baseline document exists; schema tests pass; T24.0.6 lands without regressing `ledger_audit` (still rejects `X-*` probe codes; structured-kind checks active).

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

**Protocol reality (TODO23 T23.1.8).** The shipped protocols are scalar and minimal: `OperatorGenome.genome()/instantiate()`, `MutationOperator.mutate(genome, rng)`, `FitnessMetric.score(operator, batch) -> float`, `SelectionPolicy.select(population, k)`, `StagnationDetector.update(best_fitness) -> bool`, `Constitution.admits(genome) -> bool`. Multi-objective Pareto selection and frontier-growth stagnation are **research-layer extensions** in `computronium_lab.research` (vector fitness, crowding, hypervolume); the TODO23 protocols are not widened. Scalar conformance is preserved where a scalar view exists (surrogate screens, single-objective fallbacks). `CoordinateGenome` wraps a catalog `MechanismCandidate` (build path `preset`/`recipe` with `build_name` or `config_builder`) as its `genome()` payload.

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
| **T24.2.7 CEEC Experiment Lifecycle** | Each generation/campaign pre-registers as a ceec `Experiment` (draft → pre_registered → running → completed/failed); candidate selection runs the CEEC §22 loop (`ceec.selection.generate_candidates` → `check_hard_constraints` → `decide`); the evolution kernel keeps its own archive — no `CampaignDatabase` coupling (compartments stay pure); `stability.resources.ResourceUsage` rollups recorded as resource-vector `Derived` via the adapter | T24.2.3 |
| **T24.2.8 Compartment Adapters** | Thin adapters, no cross-imports: AutoScientist→CEEC (proposals/campaigns pre-register as `Experiment`s, record Evidence/`Derived`), AutoScientist→evolution (`ProposalObjective`-ranked candidates offered as seed genomes), Lab→CEEC recorder formalized | T24.2.7 |

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
| **T24.3.3 Statistical Summary Module** | Means, stds, confidence intervals, paired tests, effect sizes, one-sided promotion-compatible bounds — implemented on the RESEARCH3 PR-4 statistics kit (bootstrap CI + paired-comparison harness), not a parallel stack | T24.3.2 |
| **T24.3.4 Catalog Re-Measurement Pass** | Re-measure applicable catalog rows on corpus tasks using Lab construction paths | T24.3.2 |
| **T24.3.5 Frontier Archive Integration** | Corpus results append to the same frontier archive used by evolution | T24.3.3 |
| **T24.3.6 Measurement-Block Ledger** | Record rows/problem classes that cannot be measured yet and why | T24.3.1 |

**Initial problem classes:**

| Problem Class | Existing Basis | Notes |
|---|---|---|
| `flat_classification` | calibrated gaussian-blob quick tier | Primary classification corpus; strong mechanisms saturate at 1.0 by 10–20 epochs |
| `sequence_last_symbol` | `sequence_task("last_symbol")` | NTM sequence tier; 0.918–0.922 @ 120 ep recorded |
| `sequence_threshold` | `sequence_task("threshold")` | NTM sequence tier; ~0.65 ceiling recorded |
| `sequence_parity` | `sequence_task("parity")` | At chance at the recorded budget — inherited TODO23 limitation; the corpus records it, never forces it |
| `nca_state_prediction` | `grid_transition_task` | k-step rollout task; avoids one-step degeneracy |
| `continual_switch` | `Lab.adapt` ψ runtime | Synthetic task stream with boundary |
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

**Invariance proof + state inventory:** ψ-arm θ invariance is proven with the existing `FrozenThetaAudit` (`computronium.core.frozen_theta`) plus a mutable-state inventory (optimizer moments, buffers, dataloader order) so "ψ-only" claims cannot hide mutable state elsewhere (TODO.rigor §28).

**Capacity-matched control:** where constructible, include an equal-writable-state recurrent baseline (TODO.rigor §9) among the controls; otherwise record a measurement block stating why not.

**Success criterion:** `lab.benchmark_continual` returns a report with per-mode metrics, control metrics, statistical summary, θ invariance proofs, and ledger references.

---

### Phase 5: Substrate Robustness and Deployment Corpus

**Goal:** make deployment robustness measurable rather than descriptive.

| Task | Deliverable | Depends On |
|---|---|---|
| **T24.5.1 Transfer Campaign** | Train on digital substrate; apply/export INT8, ternary, memristive-simulated constraints; evaluate val accuracy and fidelity | Phase 3 |
| **T24.5.2 Robustness Score** | Composite record: accuracy delta, fidelity max-abs-diff, export success, energy estimate, constraint preservation | T24.5.1 |
| **T24.5.3 Evolutionary Substrate Mutation** | Optional genome mutations over substrate constraints where construction/export exists | Phase 1, T24.5.1 |
| **T24.5.4 Deployment Cookbook Entries** | Certified deployment recommendations or boundary beliefs | T24.5.2 |

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
| **T24.6.6 Prediction Calibration** | H24.1–H24.6 pre-registered predictions scored on outcome via `ceec.calibration` / `record_calibration` (Brier/log score); calibration drift reviewed per CEEC §24 | T24.6.1 |

**Cookbook v1 entry format:**

```text
Mechanism:
Problem class:
Constraints:
Coordinate:
Evidence:
Certificates:
Known limitations:
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
| **T24.7.3 Practitioner Documentation** | Evolution quickstart, research corpus guide, cookbook guide, measurement-block ledger guide | Phase 6 |
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
- Determinism seal is optional at smoke/quick tiers and required for certified-tier promotion attempts (TODO23's `seal_determinism` localizes the first diverging epoch).

### 9.2 Controls

Every claim-bearing campaign must have an appropriate control:

| Campaign Type | Control |
|---|---|
| Classification | Label-permuted training, evaluated on unpermuted val split |
| Sequence | Episode label-shuffled training, evaluated on unpermuted val episodes |
| State prediction | Label-shuffled or rollout-target-shuffled control |
| Continual ψ | Frozen no-ψ control and/or θ fine-tune matched-compute control |
| Substrate transfer | Unconstrained digital baseline |

ψ claims additionally require a capacity-matched control where constructible (Phase 4) — otherwise a measurement block records why not.

### 9.3 Equal Compute

Comparisons must normalize compute and writable state:

- same number of epochs or same number of optimizer steps,
- same batch count where applicable,
- ψ adaptation episodes counted explicitly,
- control arms receive equal training budget,
- plastic-state capacity (ψ / fast weights / optimizer state) reported per arm and matched or bounded — budget-normalized reporting per TODO.rigor §5 (writable bits, FLOPs/step, latency).

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

Energy values carry their tier label (`simulated` | `estimated`) — never presented as hardware-measured (TODO.rigor §18).

### 9.5 Statistics

- Report mean and standard deviation across seeds.
- Use paired tests when comparing matched arms.
- Promotion maps onto the CEEC-Core §18 gate family (τ_promote = 0.95, MultiSeed ≥ 3, MatchedControl, EvaluationPolicyValid, DefectAudit, Reproduction, ScopeExplicit) as already enforced by `promote_mechanism` (one-sided t-bound, reproduction tolerance).
- Certified negative results map onto the CEEC-Core §19 boundary gates (defect hunt, levers exhausted); do not confuse them with lab `measurement_block` artifacts (blocked measurements).
- Do not promote on smoke-tier results.
- Do not weaken gates to fit a budget; lengthen the budget or record a measurement block (the recorded TODO23 calibration finding).

### 9.6 Evidence Structure

- Per-seed metric tables → `vector` evidence; training/adaptation histories → `curve`; Pareto frontiers → `frontier`; blocked measurements → `inert`/`missing` with explanatory notes.
- Structured kinds carry `axes` + `values_ref` (enforced by `ceec.models`); scalar-only primary evidence is the CEEC §27 anti-pattern TODO24 retires — the lab's current `kind="scalar"` campaign records are the debt being paid.
- `ceec.audit` structured-kind checks run alongside `ledger_audit`.

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
    max_epochs_per_campaign=None,  # None = inherit the task's certified operating point
    max_seeds=3,
)
```

Task-specific certified epoch budgets inherit the stable operating points recorded in TODO23:

- flat classification: 20 epochs (reproduction 0.896 @ 20 ep; 10-epoch runs are cross-process nondeterministic and honestly refuse promotion),
- sequence last_symbol: 120 epochs (0.918–0.922; raw-LSTM control 0.953 @ 60 ep),
- sequence threshold: ~0.65 recorded ceiling; parity: at chance at the recorded budget — a recorded limitation, not a budget problem,
- NCA state prediction: 100–300 epochs (certifies at 100; 300 is the recorded default),
- continual adaptation: fixed episode budget, not open-ended training.

---

## 11. CEEC and Ledger Integration

CEEC-Core is the governance compartment: it records and decides, it never executes experiments. ceec-core already ships the full CEEC-Core object model and the §22 selection loop; TODO24 grows the Lab's usage from the current slice (Artifact + scalar Evidence + GateOutcome + Belief + Decision) to the complete loop and lands targeted instrument improvements (T24.0.6, T24.6.6) without moving execution logic into CEEC:

| ceec object (implemented) | TODO24 usage |
|---|---|
| `Experiment` (+ pre-registration via `ceec.bootstrap.experiment_from_config`) | Pre-registered campaigns, evolution generations, corpus measurements |
| `Derived` (`record_derived`) | Statistical summaries, frontier/hypervolume rollups, resource-vector rollups |
| `GateOutcome` / `StatusChange` | Promotion and boundary attempts with full status history |
| `Goal` / `GoalRevision` | Corpus- and hypothesis-level research goals |
| `CalibrationRecord` (`ceec.calibration`) | H24 pre-registered predictions scored after outcome (Brier/log) |

Implemented `GateStatus` vocabulary is `pass | fail | not_evaluated` (`ceec.models`); T24.0.6 reconciles it to the METHODOLOGY §15 spec vocabulary (`passed`/`failed`/`unknown`/`waived_with_justification`).

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
| `measurement_block` | Explicit record of a blocked or impossible measurement |

The allowlist lives lab-side (`computronium_lab.campaign._ALLOWED_ARTIFACT_TYPES`, currently `validation_campaign`, `exploratory_synthesis`, `lab_comparison`, `mechanism_belief`); extending it with the four new types is a Lab change, not a CEEC-Core change. Campaign gates already enforced by the Lab: `BenchmarkReproduction`, `StabilityCertificate`, `DeployabilityCheck`.

**Terminology:** a `measurement_block` is a blocked or impossible *measurement* (lab artifact); a CEEC `boundary` *belief* is a negative claim that passed the §19 boundary gates. "Certified" is shorthand for "campaign gates passed" — never a status; belief statuses are only CEEC's `open`/`promoted`/`boundary`/`quarantined`. Cookbook "certified negative result" means a `boundary` belief.

### Ledger rules

- No `X-*` probe codes.
- No belief without campaign evidence.
- No cookbook entry without certified campaign or certified negative result.
- Failed campaigns are retained as evidence.
- Every certified-tier measurement and every evolution generation is a pre-registered `Experiment` with a recorded `Decision`; selection uses the CEEC §22 loop, not ad-hoc choices.
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
| Negative results get lost | Measurement-block ledger and failure manifesto are required outputs |
| New task classes destabilize core | Problem classes implemented through protocols, not core edits |
| Substrate results overclaim | Simulated/estimated labels mandatory; no hardware-measured claims |
| Evolution fails to improve catalog | TODO24 still ships corpus, benchmark, cookbook, and recorded limitations |

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
- [ ] Measurement-block ledger records blocked items with reasons.
- [ ] Ledger audit passes with zero `X-*` codes; certified-tier work is pre-registered as CEEC `Experiment`s with `Decision` records and calibration scores.
- [ ] CEEC instrument improvements landed (T24.0.6): structured-evidence helpers, unified audit, spec `GateStatus` vocabulary.
- [ ] Compartment purity verified (T24.2.8): no CEEC import inside `computronium/autoscientist`, no AutoScientist import inside the evolution kernel.
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

Provide a catalog row:

```text
MechanismCandidate
  - build_kind "preset" | "recipe" with build_name or config_builder
  - coordinate fields (credit, update, geometry, plasticity, substrates)
  - measured Pareto metadata + provenance (never speculative)
  - SystemConfig.validate() compatibility via the build path
```

No manual metadata without campaign evidence.

### Add a new objective

Provide:

```text
FitnessMetric component
  - objective name (extend KNOWN_OBJECTIVES and the objective→field/direction
    map in synthesis/engine.py)
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

### Wire an AutoScientist surface (adapter only)

The AutoScientist stays a pure compartment — no CEEC import inside `computronium/autoscientist`. The T24.2.8 adapter mirrors `ExperimentProposer` proposals and `HypothesisReasoner` hypothesis chains into CEEC `Experiment` pre-registrations / `Belief` drafts through the research schema (`AutoScientistBridge` packages execution; CEEC packages governance) and offers `ProposalObjective`-ranked candidates to the evolution kernel as seed genomes. No parallel proposal ledger.

---

## 15. Anti-Bureaucracy Clause

```text
No PyPI publishing in TODO24.
No new ontology axes.
No experiment-execution logic in CEEC-Core (governance only; instrument improvements ride T24.0.6).
No probe-level beliefs.
No cookbook entry without campaign evidence or certified negative result.
No catalog metadata without a construction path and campaign evidence.
No evolved candidate becomes a recommendation solely because it was mutated.
No task class is forced into an incompatible geometry.
No substrate result is described as hardware-measured unless physical validation exists.
No internal metric ships without a user-facing report or measurement block.
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
- [ ] T24.0.6 CEEC Instrument Improvements

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
- [ ] T24.2.7 CEEC Experiment Lifecycle
- [ ] T24.2.8 Compartment Adapters

### Session YYYY-MM-DD — Phase 3: Certified Research Corpus v1
- [ ] T24.3.1 Problem Classes
- [ ] T24.3.2 Measurement Protocol Runner
- [ ] T24.3.3 Statistical Summary Module
- [ ] T24.3.4 Catalog Re-Measurement Pass
- [ ] T24.3.5 Frontier Archive Integration
- [ ] T24.3.6 Measurement-Block Ledger

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
- [ ] T24.6.6 Prediction Calibration

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
- [ ] CEEC Experiment lifecycle validated end-to-end (pre-registration → selection → Decision)
- [ ] Compartment purity verified (no cross-imports)
- [ ] Gallery/demo locks green

