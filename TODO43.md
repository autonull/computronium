# TODO43 — Unified Search & Evidence Requirements

**Date**: 2026-09-28 · **Rev**: 3 (Rev 2 refined after full-surface audit; Rev 3
adds §13–§15 + Appendix C — completeness gaps and consolidation candidates,
pending review)
**Status**: REQUIREMENTS ONLY. No design, no decomposition, no sequencing.
Those follow review of this document (§12 "Deferred to Design").
**Origin**: Campaign Iterations 4–5b (`CAMPAIGN_LOG.md`) for the problem
statements; a flag-, axis-, and module-level audit of the repo (2026-09-28) for
the capability inventory. Audit completeness is stated per appendix.

**How to read**: §2 states observed problems (facts, no fixes). §3 inventories
every capability that exists today, organized by lifecycle stage — this is the
union that must not be lost. §5 states requirements, each with a trace to
problems/capabilities and a behavioral verification. Appendices A–B are the
preservation artifacts: the flag inventory and the axis enumerations.
§13–§15 and Appendix C (Rev 3 addendum) are an unreviewed layer — completeness
gaps and consolidation candidates, not accepted requirements.

---

## 1. Purpose and Scope

### 1.1 Purpose
Four partially-overlapping search/coverage implementations exist, each with its
own space, policy, and store, plus governance split across two of them. The
requirement set describes one coherent experiment framework that **achieves or
exceeds the union** of inventoried capabilities (§3), structurally prevents the
observed failure classes (§2), and adds the capabilities the current design
makes impossible or uneconomic.

### 1.2 In scope
The experiment lifecycle end to end: framing (objectives, hypotheses, prior
art), space definition, scheduling/fidelity, gating, composition, training,
measurement, recording, attribution, decision/promotion, reporting, live
operation, and the governance of the framework's own capabilities.

### 1.3 Out of scope (non-goals)
- Reimplementing Optuna's samplers/pruners/storage internals.
- Changing the ontology, credit/update/dynamics primitives, or substrate physics.
- Better search *algorithms* per se — expressiveness, allocation, integrity, and
  preservation are required; algorithm choice is a policy downstream of this.
- Re-measuring existing artifacts for their own sake; historical records are
  read and labeled (R79).
- Preserving CLI verbs or module paths as API contracts (AGENTS.md: no backwards
  compatibility). Records on disk, the capability registry, and the flag
  inventory (Appendix A) are the compatibility surfaces.
- Deciding scientific validity — the system must make validity *checkable* and
  evidence *traceable*, not render verdicts.

### 1.4 Terminology
| Term | Meaning |
|---|---|
| **Search** | Deciding what to evaluate next |
| **Evaluation** | Composing, training, and measuring one configuration |
| **Record** | Durable, queryable trace of one evaluation |
| **Coordinate** | The full set of choices defining one evaluation |
| **Stage** | A lifecycle phase (§3.0) |
| **Policy** | How search chooses coordinates, allocates compute, or stops |
| **Evidence status** | Derived record properties: gate verdict, defect status, fidelity tier, reproducibility, uncertainty |
| **Tier (L0/L1/L2)** | Existing measurement-fidelity levels (CAMPAIGN_PLAN §7) |
| **Capability** | A behavior some part of the system implements today (§3) |
| **Prior** | Recorded data that biases a search before it runs (distinct from hardcoded defaults) |

---

## 2. Problem Statements (evidence, not conclusions)

### P1 — Four overlapping search implementations
| Implementation | Space it expresses | Proposal policy | Store |
|---|---|---|---|
| `autoscientist/broad_map.py` (`StratifiedRandomDriver`) | dynamics, credit, update, topology/geometry | stratified random, objective-binned | `kb.sqlite` + `campaign.db` + `ledger.sqlite` |
| `core/campaign/stack.py` (`grid_sampler`, `_space_sampler`) | substrates, geometries, dynamics, plasticity, credits, updates | round-robin grid, or uniform random | `CampaignStore` (SQLite) |
| `hyperopt/` (`_finder.py`, `optuna_bridge.py`) | continuous per-rule/per-model spaces | TPE, NSGA-II, pruners | Optuna RDB (own `*.db`) |
| `execution/_state.py::get_optuna_study` | Optuna study over model/task | TPE | its own sqlite |

The same experiment class is describable in one implementation and inexpressible
in another. Nothing enforces agreement.

### P2 — Learning rate is not a searched coordinate
`broad_map.py:632` and `:1749` set `hyperparams={"epochs","param_budget"}` only;
`_execute_proposal_with_substrate` (`:797`) falls through to `_ruler_lr(task,
topology)` (`campaign.py:200`). Every cell trains at one lr per (task, topology).

Measured (`scripts/probes/iter5_em_gradient_epochs.py`; mnist,
`energy_minimization|gradient|riemannian_orthogonal`, depth 4, hidden 20):

| lr | Epoch 1 | Epoch 2 | Epoch 3 | Clamps |
|---|---|---|---|---|
| 0.01 (ruler) | loss 3.7e-06, acc 0.125 | loss 5.2e-05, acc 0.031 | loss 0, acc 0.125, energy −2.8e5 | 182 |
| 0.001 | acc 0.812 | acc 0.812 | acc 0.656 | 0 |

### P3 — Record identity does not disambiguate measurements
`cell_key(dynamics, credit, update, topology)` (`proposer.py:77`) omits lr,
seed, epoch count, batch limit, substrate, device/precision. Consequences: the
Pareto front mixes lrs; `energy_minimization|gradient|riemannian_orthogonal|
feedforward` scored 0.211 at L0 (30 batches) and 0.0973 at L2 (3 full epochs)
with no record of what differed; L1 re-runs inherit the parent burst tag
(`:1735-1738`).

### P4 — Hand-maintained per-combination prior tables
`ontology/update.py:53-76`: 30+ `(dynamics, credit) → multiplier` entries;
`compose.py:44`: per-dynamics step sizes. These encode tuning no search
performs, accumulate per combination that happened to run (the plan's
"step_size positive feedback" bias), and are contradicted in practice: a
suspected clamp cause (57 clamps) did not reproduce under test while an
unrelated coordinate was the real divergence (P2).

### P5 — Budget and time concepts are not unified
`ContinuousBudget` (soft/hard expiry, `:93`), `max_epoch_time`,
`eval_tiers.py` patience tiers with `estimate_total_time` (`:67,153`), and
per-iteration caps in `stack.py` are four independent notions of duration.
Cross-system walltime/throughput comparisons are not well defined.

### P6 — Governance is split and partly optional
Two independent paths: dry-run gate + defect quarantine + maturity tiers
(`broad_map.py:753,1003,1757,1810`) and power pre-registration + replication
gate + counterfactual attribution (`validation/`, `stack.py`, `replication.py:95`).
Governance is a property of the code path, not of the record.

### P7 — Four stores, no single source of truth
`kb.sqlite` (richest: rows + vector store + surrogates + causal), `campaign.db`
(2 tables), `ledger.sqlite`, Optuna's own DBs. Four reporting paths:
`scripts/campaign_analyze.py`, `core/campaign/kb_report.py`,
`core/campaign/report.py`, `hyperopt/comparator.py`. Two disagreed within one
session (kb_report counted experiments unfiltered while its front was
task-filtered).

### P8 — Resume semantics differ and are unasserted
`stack.py:66-79` requires stateless coordinate proposal so `(campaign_id,
iteration)` replays identically and resume skips recorded rows; `broad_map`
resumes by KB coverage seeding. Both are valuable; neither is stated as a
requirement of the other; replay fidelity is nowhere asserted.

### P9 — Store analytics are unused by search
Vector store, `SurrogateManager`, `CausalAnalyzer`, conditional queries, and
`hyperparameter_metamodel.py` exist; no search policy consumes them, and the
metamodel models trials held outside the KB.

### P10 — Objective definitions are not one registry
`objectives.py::Objective` (~39 with directions/weights/normalizers/axis tags),
`stack.py:138` `("task_loss","stability_score","energy")`, and
`hyperopt/frontier.py::RulePoint` are three notions. The same word can denote
different quantities in different reports.

### P11 — CLI/report duplication and documentation drift
`comp` exposes `run show list status report export hypothesis benchmark
checkpoint compare pareto search verify train core-train` plus `continuous`
(with `unquarantine`, `deep-tier`), `campaign` (`kb-report`, `diff`),
`frontier`, `repro`, `portfolio`, `daemon`, and `scripts/campaign_analyze.py`.
Root/task/scope conventions are re-implemented per entry point. Three documented
invocations in CAMPAIGN_PLAN were wrong in one session (`--task` defaults,
`comp frontier` flags, `deep-tier --root` semantics).

### P12 — Compute is allocated by a fixed ladder, not by evidence
Fidelity is chosen by tier promotion, so cost lands on whichever cells were near
a front at a cheap tier. Observed: one cifar10 L1 re-run consumed 930 s to reach
0.1002 (no gain over L0); one mnist L2 re-run consumed 1357 s to reach 0.0973
with 1457 clamp events. Neither decision was revisited on evidence of waste.

### P13 — Failures are detected late and diagnosed by hand
Clamp storms, NaN, and loss explosions are logged; nothing interrupts the run.
`GuardKillError`/`DEFAULT_GUARD_TAU` (`evaluation.py:62,90`) exist but are not
part of the burst path. Void classification is manual to extend; the
"unclassified" bucket is audited by a hand-run SQL snippet (CAMPAIGN_PLAN §10).

### P14 — Capabilities have no registry, so preservation is unenforceable
Nothing states in one place which behaviors the system should have. Deprecation
is a matter of memory — which is how one-off tables, flags, and report paths
accumulated.

### P15 — Execution-environment nondeterminism is unmanaged
`create_task` defaults `num_workers=0` under `quick_mode` citing "forkserver
race mitigation (D7 precedent)" (`domains/factory.py:147-151`); worker-based
loaders intermittently fail (`ConnectionResetError` observed in-session);
`test_daemon_client_round_trips_live_daemon` carries a known race (Future Work
#6). These are worked around ad hoc, never recorded as run properties.

### P16 — Compiled-kernel acceleration escapes the run model
`core/campaign/kernel_cache.py` keeps a global singleton cache
(`get_kernel_cache()`), keyed by coordinate hash + shapes + dtype + device +
adapter stack, persisting pickled artifacts to `~/.cache`. The cache is not
scoped to a run or record, has no provenance, and pickled code artifacts are a
correctness/portability hazard — acceleration exists but is not reproducible or
attributable.

### P17 — Hypothesis/reasoning/literature subsystems are disconnected from records
`reasoner.py` (five reasoning templates), `local_llm.py`, and `literature.py`
(arXiv retrieval + semantic search) generate hypotheses and prior art, but their
outputs are not records with provenance and are not linked to the experiments
they motivated; the loop cannot learn from its own reasoning history.

---

## 3. Capability Inventory (the union that must not be lost)

Every capability below is a requirement on the unified system. "Today" names
where it lives. Capability IDs are stable and are referenced by the preservation
requirements (R76–R78). Audit completeness: command-level for all `comp`
subcommands; flag-level where noted (Appendix A).

### 3.0 Stage model
| Stage | Purpose |
|---|---|
| S1 Frame | State the question/hypothesis, objectives, and the bar for a claim |
| S2 Space | Define what may be evaluated (axes, ranges, constraints, infeasibility) |
| S3 Schedule | Decide fidelity, budget, and order |
| S4 Gate | Reject infeasible/quarantined coordinates before spending compute |
| S5 Compose | Build the system (config, validation, auto-sizing, substrate) |
| S6 Train | Settle/train, with guards, telemetry, resumability |
| S7 Measure | Metrics, objectives, probes, latency/resource accounting |
| S8 Record | Persist the full trace: coordinate, config, metrics, provenance |
| S9 Attribute | Explain the result: attribution, contrasts, diagnostics |
| S10 Decide | Promote, retire, continue, claim-eligibility |
| S11 Report | Fronts, diffs, figures, manifests, narrative, alerts |

### 3.1 S1 Frame
| # | Capability | Today |
|---|---|---|
| C1 | Objective registry: ~39 objectives with per-objective direction, weight, normalizer, axis tag (Appendix B.4) | `autoscientist/objectives.py` |
| C2 | Objective parsing from comma specs with availability validation | `parse_objectives` |
| C3 | Hypothesis generation: rule-based reasoner with five templates (failure analysis, transfer, composition, refinement, experimental design) producing chains with steps/conclusion/confidence/evidence/assumptions | `autoscientist/reasoner.py` |
| C4 | LLM-assisted hypothesis generation | `autoscientist/local_llm.py` |
| C5 | Prior-art retrieval: arXiv API + semantic search over papers | `autoscientist/literature.py` |
| C6 | Proposal-objective selection (accuracy/memory/energy/stability/…) | `proposer.ProposalObjective` |
| C7 | Task-family selection and cycling | `--task`/`--tasks`; `stack.task_for_visit` |
| C8 | Task compatibility fencing with reasons (fenced lanes fail with a reason instead of silently degrading) | `compose.TASK_COMPAT` |

### 3.2 S2 Space
| # | Capability | Today |
|---|---|---|
| C9 | Stratified coverage over ontology axes so no axis starves | `StratifiedRandomDriver` |
| C10 | Novelty suppression: no re-measurement of known coordinates | coverage set seeded from KB |
| C11 | Full-grid enumeration with pre-classification of infeasible cells as voids | `enumerate_constraint_voids` |
| C12 | Rejection classification: ontology void vs runtime defect, with categories | `classify_void`, `_VOID_CATEGORIES`, `_record_defect` |
| C13 | Deterministic round-robin grid traversal (controlled ablation) | `grid_sampler` |
| C14 | Space-sampler binding from an axis table; custom grids | `_space_sampler`, `space["_custom_grid"]` |
| C15 | Continuous parameter spaces with ranges and discrete choices | `search_space.py`, `get_rule_space` |
| C16 | Geometry auto-sizing from param budget for all topologies | `build_geometry_config`, `_auto_size_geometry` |
| C17 | Geometry sampling strategy (`full_range` / `max_only`) | `--geometry-sampling` |
| C18 | Per-combination step-size priors | `_STEP_SIZE_OVERRIDES`, `_DYNAMICS_STEP_SIZE_OVERRIDES` |
| C19 | Per-(task, topology) lr table (ruler) | `_ruler_lr`, `ruler_table.json` |
| C20 | Model-based search over continuous/mixed spaces (TPE, NSGA-II) with pruners | `hyperopt/_finder.py`, `optuna_bridge.py` |
| C21 | Compute-matched HPO scoped to a credit type | `comp search` |

### 3.3 S3 Schedule
| # | Capability | Today |
|---|---|---|
| C22 | Budget strings with soft/hard expiry and target-cell caps | `ContinuousBudget.parse` (`5m`, `90s`, `1h`) |
| C23 | Loop mode with inter-burst sleep | `--loop`, `--sleep` |
| C24 | Bounded-batch fidelity and epoch counts | `--limit-batches`, `--epochs` |
| C25 | Multi-seed re-runs at higher fidelity | `--seeds`, `run_l1_maturation`, `comp verify` |
| C26 | Maturity tiers L0→L1→L2 with promotion criteria | `promote_candidates`, `run_deep_tier` |
| C27 | Pre-run time estimation | `eval_tiers.estimate_total_time` |
| C28 | Patience-tiered evaluation configs | `EVALUATION_TIERS`, `PatientLevel` |
| C29 | Max-epoch-time guard inside training | `max_epoch_time` |
| C30 | Multi-task bursts with sequential per-task execution | `--tasks` |
| C31 | Iteration/cell pacing (`--max-iterations`, `--cells-per-iter`) | `continuous` flags |

### 3.4 S4 Gate
| # | Capability | Today |
|---|---|---|
| C32 | Dry-run gate rejecting coordinates before execution; space-diversity preview | `--dry-run` |
| C33 | Cross-axis config validation as single source of truth (~30 rules incl. substrate/dynamics/credit/geometry) | `SystemConfig.validate` |
| C34 | Defect recording and quarantine | `runtime_defects.jsonl` |
| C35 | Defect auto-release when the error pattern disappears from the codebase | `unquarantine --unquarantine-fixed` |
| C36 | Unclassified-void audit affordance | CAMPAIGN_PLAN §10 SQL recipe |

### 3.5 S5 Compose
| # | Capability | Today |
|---|---|---|
| C37 | Single composition path with auto-propagated beta/step coupling | `compose_cell_system` |
| C38 | Per-dynamics substrate auto-configuration (noise/precision) | `_build_substrate_config` |
| C39 | Substrate families (digital, analog, memristive, neuromorphic, optical, quantum, complex, sparse, ternary) with noise_level and precision | `SubstrateConfig.*`, `--substrate` |
| C40 | Param-budget rematch/fairness enforcement (25% tolerance, 3 iterations) | budget rematch in `_execute_proposal_with_substrate` |
| C41 | Per-topology geometry parameters (Appendix B.2) | `_TOPOLOGY_KEYS` |
| C42 | Optional per-cell BP-gradient-alignment trace | `--credit-trace` |
| C43 | Device selection and dtype/precision handling | `get_device`, `SubstrateConfig(precision=…)` |
| C44 | Warm-start state handling across settles and batch sizes | `_dual_vars` warm start |
| C45 | Adapter stacks over the joint architecture | adapter composition in kernel cache keys |

### 3.6 S6 Train
| # | Capability | Today |
|---|---|---|
| C46 | Settle phases (free/nudged) with per-phase state | `settle` |
| C47 | Settle telemetry: energy clamps, steps used, free-energy history, spike/event rates | `_SettleTelemetry` |
| C48 | Guard-kill concept with tau threshold | `GuardKillError`, `DEFAULT_GUARD_TAU` |
| C49 | Deterministic seeding incl. per-(epoch, batch) fold-in | `seed_everything`, `fold_in` |
| C50 | Campaign and run checkpoint/restore | `CheckpointManager`, `JointCheckpoint`, snapshot/restore |
| C51 | Compiled-kernel caching (transition step, plasticity update, stability estimator, adapter projection) with LRU + disk persistence | `JointKernelCache` |
| C52 | Per-epoch resource accounting with over-budget stops | `EpochResources`, `max_epoch_time` |

### 3.7 S7 Measure
| # | Capability | Today |
|---|---|---|
| C53 | Per-epoch and final metrics (loss/accuracy/energy) | `final_metrics`, trainer |
| C54 | Spectral-radius probe | `probe_spectral_radius` |
| C55 | Inference benchmark: latency (mean/p50/p95/p99), throughput | `benchmark_inference`, `InferenceMetrics` |
| C56 | Full objective set computable per record (Appendix B.4) | objectives + settle telemetry + substrate objectives |
| C57 | Seed-sensitivity flags on repeated measurements | `_seed_sensitivity_flags` |

### 3.8 S8 Record
| # | Capability | Today |
|---|---|---|
| C58 | Durable record per evaluation: config, metrics, tags, source, confidence, finding | KB `knowledge` table |
| C59 | Vector/semantic retrieval over records | `knowledge/vector_store.py` |
| C60 | Surrogate models over records | `SurrogateManager` |
| C61 | Causal analysis over records | `CausalAnalyzer` |
| C62 | Conditional/structured query engine | `query.py`, `ConditionalQuery` |
| C63 | KB-level caching and metamodeling | `kb_cache.py`, `knowledge/metamodel.py`, `hyperparameter_metamodel.py` |
| C64 | CEEC pre-registration per experiment | ledger, `ceec/` |
| C65 | Maturation/promotion append-log | `maturation.jsonl` |
| C66 | Burst tagging and next-tag derivation | `next_burst_tag` |
| C67 | Scaling-law fitting and FLOPs extrapolation | `scaling_law.py` |

### 3.9 S9 Attribute
| # | Capability | Today |
|---|---|---|
| C68 | Counterfactual axis attribution (which axis caused the delta) | `analysis/counterfactual.py`, `attribute_axis_effects` |
| C69 | Rule-frontier and ideal-backprop frontiers; frontier comparison | `rule_frontier.py`, `ideal_backprop.py`, `comparator.py` |
| C70 | Operating-point matching and resource ratios | `OperatingPointMatch`, `resource_ratios` |
| C71 | Regime-advantage labels and portfolio decisions | `portfolio.py` |
| C72 | Config flattening/encoding/classification for analysis | `hyperopt/analysis.py` |

### 3.10 S10 Decide
| # | Capability | Today |
|---|---|---|
| C73 | Power pre-registration and embedded-control verification | `validation/power_preregistration.py` |
| C74 | Replication gate (min seeds, min task families) and manifests | `replication.py` |
| C75 | Reproducibility verification of a stored experiment | `comp repro` |
| C76 | Top-k re-run verification of a study | `comp verify` |
| C77 | Pareto fronts under explicit per-objective directions | `pareto.py`, `objectives.py` |

### 3.11 S11 Report
| # | Capability | Today |
|---|---|---|
| C78 | Cross-run campaign diff | `comp campaign diff` |
| C79 | HTML + JSON campaign report (clamps, walltimes, maturation, defects, Pareto) | `kb_report.py` |
| C80 | Markdown campaign summary | `report.py::generate_report` |
| C81 | Sweep-level analysis (clamp rates, spectral outliers, param blowups, spread, worst combos, numerical defects) | `scripts/campaign_analyze.py` |
| C82 | Pareto plots (html/png/json) for a study | `comp pareto` |
| C83 | Figures/gallery with manifest pinning | `visualization/gallery.py`, `docs/figures/manifest.json` |
| C84 | Dashboard rendering; event-stream toasts | dashboard modules, `stream_protocol.py` |
| C85 | Alerts: breakthrough (≥2% margin), cascade (>30% failures), completion — webhook dispatch, human decides run/stop | `autoscientist/alerts.py` |
| C86 | Study/config export | `comp export` |
| C87 | Live daemon status/control (pause/resume/state) | `comp daemon`, `DaemonClient` |
| C88 | Void/negative-result reference documentation | `CAMPAIGN_REFERENCE.md`, `COORDINATE_VOIDS.md` |

---

## 4. Traceability Conventions

- Requirements cite problems as `P#` and capabilities as `C#`.
- Every capability C1–C88 is cited by at least one requirement (preservation
  proof, R76–R78 enforce this mechanically).
- Every problem P1–P17 is addressed by at least one requirement group (§7).
- Verification statements are behavioral ("what is observed"), never
  architectural ("how it is built").

---

## 5. Requirements

Priorities: **MUST** (acceptance-blocking) and **SHOULD** (required unless
waived with a recorded reason).

### 5.1 Expressiveness and space

- **R1 (MUST)** — One coordinate namespace MUST express the union of all axes
  any implementation expresses today: dynamics, credit, update,
  geometry/topology (with per-topology parameters), substrate (with
  noise/precision), plasticity, learning rate, update step size, and seeds/
  epochs/batch limits as evaluation parameters (Appendix B).
  Trace: P1, P3 · C9, C14, C15, C39, C41, C45.
  Verify: the union of axis names in Appendix B is representable in one schema,
  and a coordinate instance names a value for each axis it constrains.
- **R2 (MUST)** — Learning rate MUST be expressible as a searched coordinate,
  not only as a per-(task, topology) constant.
  Trace: P2, P4 · C19. Verify: one run yields records at >1 lr; lr is part of
  record identity (R7).
- **R3 (MUST)** — Substrate and its parameters (noise, precision) MUST be
  comparable within a single search, not only as a run-level switch.
  Trace: P1 · C38, C39. Verify: records from two substrates appear in one
  comparable set.
- **R4 (MUST)** — Continuous and discrete parameters MUST share one
  representation so a mixed space needs no separate mechanism.
  Trace: P1 · C15, C20. Verify: a mixed space is described by one object.
- **R5 (MUST)** — Every axis's legal values MUST be discoverable at runtime
  from a registry (not only from source reading).
  Trace: P14 · C1, C39, C41, App. B. Verify: a registry query enumerates legal
  values per axis and matches Appendix B.
- **R6 (MUST)** — Every numeric default that influences an evaluation (lr,
  step size, momentum, beta, rho, budgets, batch size) MUST be overridable per
  run and per coordinate, and the effective value MUST be recorded.
  Trace: P2, P4 · C18, C19. Verify: two runs identical except one override
  differ in exactly that recorded field.

### 5.2 Record identity and integrity

- **R7 (MUST)** — Every record MUST identify the exact configuration that
  produced it: all R1 axes, seeds, epochs, batch limits, dataset/split identity
  and version, device, dtype/precision, code version, and environment
  provenance.
  Trace: P3, P15 · C58. Verify: records differing only in lr, seed, or fidelity
  are distinguishable and separately queryable.
- **R8 (MUST)** — Measurement fidelity MUST be a first-class record property;
  records of different fidelity MUST NOT be silently compared as equivalent.
  Trace: P3, P12 · C24, C25, C26. Verify: every front/average/ranking either
  stratifies by fidelity or labels the mixture.
- **R9 (MUST)** — Repeated measurement of one coordinate MUST be stored as
  distinct records retaining shared coordinate identity.
  Trace: P3 · C58, C65. Verify: promotion re-runs count as repeats of their
  coordinate.
- **R10 (MUST)** — No record may be presented as a result while carrying an
  open defect or a failed gate, and this MUST hold regardless of which
  implementation wrote the record.
  Trace: P6 · C34, C35. Verify: the property is computable from the record
  alone, with no run-time context.
- **R11 (MUST)** — Environment provenance (library versions, device, dtype,
  worker/dataloader policy) MUST be recorded so environment-induced
  nondeterminism is attributable rather than mysterious.
  Trace: P15 · C43, C49. Verify: a record names the worker policy and versions
  under which it was produced.
- **R12 (MUST)** — Store writes MUST be crash-safe and atomic: an abrupt kill
  mid-write MUST never corrupt prior records.
  Trace: P8, P15 · C58, C50. Verify: kill -9 during a write leaves the store
  queryable and consistent (WAL or equivalent).

### 5.3 Single source of truth

- **R13 (MUST)** — All systems MUST read and write one record store.
  Trace: P7 · C58–C67. Verify: no implementation owns a private store; any
  record is queryable by all.
- **R14 (MUST)** — Reporting and analysis MUST be derivable from the store
  alone, with one implementation per report.
  Trace: P7, P11 · C78–C86. Verify: one command answers a question that today
  requires different tools per subsystem.
- **R15 (SHOULD)** — Vector search, surrogates, causal analysis, and the query
  engine SHOULD be reachable from every search implementation and every report.
  Trace: P9 · C59–C63. Verify: each is exercised by at least one search and one
  report.

### 5.4 Policy substitutability

- **R16 (MUST)** — The choice of the next coordinate MUST be substitutable
  without changing evaluation, record, or governance behavior.
  Trace: P1 · C9, C13, C20. Verify: one space traversed by three policies
  yields identically-shaped records.
- **R17 (MUST)** — At least the union of today's policies MUST be available:
  stratified random, round-robin grid, uniform random, and model-based
  (TPE/NSGA-II) with pruners.
  Trace: P1 · C9, C13, C14, C20. Verify: each is selectable in one run spec.
- **R18 (MUST)** — Coverage/stratification guarantees MUST NOT be lost when a
  model-based policy is used; axis-coverage statistics MUST be reported for
  every run regardless of policy.
  Trace: P1, P12 · C9. Verify: coverage report emitted for every policy.
- **R19 (MUST)** — Void pre-classification (C11) and defect classification
  (C12) MUST apply to every policy's proposals.
  Trace: P1 · C11, C12. Verify: a model-based run's rejected coordinates are
  classified identically to a driver's.
- **R20 (SHOULD)** — A policy's proposals MUST be traceable to the policy state
  that produced them (why this coordinate now), recorded per proposal.
  Trace: P1, P14 · C9, C20. Verify: a proposal record names its policy and the
  state/evidence it acted on.

### 5.5 Budget, fairness, and time

- **R21 (MUST)** — One time/resource budget concept MUST govern every search,
  with soft and hard stop semantics defined once.
  Trace: P5 · C22, C23, C29, C31, C52. Verify: consumed/remaining budget is
  exposed through one interface for every policy.
- **R22 (MUST)** — Comparisons of walltime, throughput, or cost MUST be valid
  only between records of comparable fidelity and budget.
  Trace: P3, P5 · C53, C55. Verify: such comparisons enforce or refuse the
  comparison.
- **R23 (SHOULD)** — A search MUST be able to estimate its own total cost
  before running, from the space and a per-evaluation cost model, with stated
  uncertainty.
  Trace: P5, P12 · C27, C28. Verify: a dry-run reports a cost estimate.
- **R24 (SHOULD)** — The cost model SHOULD be learned from recorded per-stage
  walltime breakdowns, not only statically estimated.
  Trace: P5, P12 · C52, C58. Verify: estimates improve as records accumulate.
- **R25 (MUST)** — Fairness constraints (param budget, FLOPs, walltime
  matching) MUST be enforceable as first-class search constraints, not only as
  post-hoc filters.
  Trace: P12 · C16, C40. Verify: a search with a fairness constraint rejects or
  re-sizes non-conforming coordinates.

### 5.6 Determinism and resumability

- **R26 (MUST)** — A run MUST replay: same inputs and seed ⇒ same coordinates;
  resume MUST NOT duplicate recorded work.
  Trace: P8 · C13, C49, C50. Verify: kill/resume yields no duplicate and no
  reordered coverage.
- **R27 (SHOULD)** — Replay determinism MUST be assertable per run (replay
  hash), not assumed from global seeding.
  Trace: P8 · C49. Verify: a run records and re-checks its replay hash.
- **R28 (MUST)** — Execution-environment nondeterminism MUST be controlled or
  detected: dataloader worker policy, daemon concurrency, and device
  nondeterminism MUST be explicit run properties with recorded fallbacks.
  Trace: P15 · C43, C49, C87. Verify: a run with workers enabled records the
  policy and its failure/retry behavior.
- **R29 (MUST)** — A failing evaluation MUST be isolated: it MUST NOT corrupt
  the run, the store, or sibling evaluations, and MUST be recorded with cause.
  Trace: P13, P15 · C34, C52. Verify: an injected failure mid-run leaves other
  records intact.
- **R30 (MUST)** — Checkpoint/restore MUST exist at run and evaluation
  granularity, preserving budget state and evidence.
  Trace: P8 · C50. Verify: restore resumes with identical remaining budget.

### 5.7 Objective semantics

- **R31 (MUST)** — Objective definitions and directions MUST come from one
  registry (including weight/normalizer/axis metadata), and every stored metric
  MUST resolve to it.
  Trace: P10 · C1, C2, C77. Verify: one definition and direction per metric
  name across all reports.
- **R32 (MUST)** — Multi-objective selections (fronts, portfolios, operating
  points) MUST be computed from records, so any policy's results are comparable.
  Trace: P10 · C70, C71, C77. Verify: fronts from different policies are
  computed by the same code.
- **R33 (SHOULD)** — New objectives MUST be addable through an extension point
  without modifying the core.
  Trace: P14 · C1. Verify: an out-of-tree objective participates in a run and
  report.

### 5.8 Evidence lifecycle

- **R34 (MUST)** — The full governance chain (dry-run gate, validation, defect
  quarantine/release, CEEC pre-registration, power pre-registration,
  replication gate, reproducibility) MUST be available, and its outputs MUST be
  record properties rather than side files only the producing path understands.
  Trace: P6 · C32–C36, C64, C73–C75. Verify: defect release, promotion, and
  claim eligibility are each computable from stored records.
- **R35 (MUST)** — A claim MUST be derived from a record predicate, never
  asserted by the run that produced it.
  Trace: P6 · C73, C74, C75. Verify: CAMPAIGN_PLAN §7 is expressible as one
  filter over records.
- **R36 (SHOULD)** — Promotion MUST be expressible as "select records by
  predicate, re-evaluate at higher fidelity", applying to any policy's output.
  Trace: P12 · C26, C76. Verify: promotion over a model-based run's records is
  possible.
- **R37 (MUST)** — Task compatibility fencing MUST be a first-class space
  constraint with a recorded reason, not a hardcoded dictionary.
  Trace: P14, P11 · C8. Verify: a fenced task appears as constrained in the
  space, with its reason queryable.
- **R38 (MUST)** — Negative results (voids, defects, regressions) MUST be
  first-class, globally suppressive, and queryable.
  Trace: P13 · C11, C12, C88. Verify: a known-infeasible coordinate is not
  re-proposed by any policy.

### 5.9 Stage completeness and uniformity

- **R39 (MUST)** — Every stage in §3.0 MUST exist in the unified system, even
  where a stage is a no-op for a given policy (e.g. a policy with no attribution
  still emits an attribution record).
  Trace: P14 · all C. Verify: a stage-coverage report shows every stage per run.
- **R40 (MUST)** — Stage behavior MUST be substitutable and composable without
  changing the record schema.
  Trace: P14 · all C. Verify: swapping a measurement or attribution
  implementation leaves records queryable.
- **R41 (MUST)** — A run MUST be fully described by a single versioned,
  serializable, diffable specification (space, policy, schedule, evaluator,
  governance, budget, seed, provenance) from which it can be reproduced.
  Trace: P11, P8 · C50, C58. Verify: two runs' specs can be diffed; a run is
  reproduced from its spec alone.
- **R42 (MUST)** — Infeasibility discovered by any stage MUST propagate
  identically to all downstream accounting (coverage, reports, reference docs).
  Trace: P13 · C11, C12, C88. Verify: a void found at S4 and one found at S6
  appear identically in coverage and reports.
- **R43 (SHOULD)** — A "question-first" entry MUST exist: state an objective
  and a target operating point, and derive an appropriate space, policy, and
  budget.
  Trace: P14 · C3, C6, C71. Verify: question + operating point yields a run
  spec.
- **R44 (SHOULD)** — Heterogeneous task families (vision, tabular, synthetic,
  sequence, RL) MUST be expressible in one run with per-task space/policy
  adaptation.
  Trace: P1 · C7, C30. Verify: one run spans ≥2 task families.
- **R45 (SHOULD)** — Space and evaluator MUST be declarable independently of
  the store so a spec can be re-run against a different store or code version
  and diffed (portability).
  Trace: P5, P11 · C86. Verify: a spec re-run elsewhere yields records
  comparable by identity.

### 5.10 Multi-fidelity compute allocation

- **R46 (MUST)** — The system MUST support allocating compute non-uniformly
  across a coordinate population with early termination of clearly inferior
  members, such that cost-to-rank is lower than uniform evaluation at equal
  ranking quality.
  Trace: P12 · C24, C25, C27. Verify: measured cost-to-rank beats the uniform
  baseline.
- **R47 (MUST)** — Fidelity allocation MUST be driven by recorded evidence
  (interim metrics, uncertainty, cost), not by a fixed ladder alone.
  Trace: P12 · C47, C57. Verify: promotion decisions reference interim evidence
  in the record.
- **R48 (MUST)** — Compute spent on a coordinate before abandonment MUST be
  recorded and attributable; repeated waste MUST be detectable.
  Trace: P12 · C52, C58. Verify: a waste report identifies repeatedly
  measured-to-no-gain coordinates.
- **R49 (SHOULD)** — Compute MUST be appendable to a coordinate across sessions
  (resume a promising cell at higher fidelity) without losing prior evidence.
  Trace: P12 · C50, C58. Verify: an appended measurement is a new record of the
  same coordinate.
- **R50 (MUST)** — Divergence and stagnation MUST be detectable during a run
  from telemetry (clamp storms, NaN, loss explosion, spectral radius,
  no-improvement) and exposed as a first-class signal.
  Trace: P13, P12 · C47, C54. Verify: the 1357 s / 1457-clamp run is flagged as
  divergence within a bounded fraction of its cost.
- **R51 (SHOULD)** — Guard-kill/early-stop decisions MUST be attributable: the
  record states which signal fired, at what value, and what was saved.
  Trace: P13 · C48, C47. Verify: a killed run's record names the signal and
  value.

### 5.11 Learning from history

- **R52 (MUST)** — Existing per-combination priors (step-size tables, ruler lr)
  MUST be representable as data a search can start from and improve on, not as
  code that silently biases runs.
  Trace: P4 · C18, C19. Verify: priors are records/settings; a search can
  exceed them.
- **R53 (SHOULD)** — New runs SHOULD warm-start space and policy from prior
  runs' records (including cross-task and cross-topology transfer), with the
  transfer's provenance recorded.
  Trace: P9, P2 · C58, C59. Verify: a new run's first proposals are informed by
  prior records; provenance is in the spec.
- **R54 (SHOULD)** — Surrogate models over records SHOULD drive proposals
  (expected improvement / expected hypervolume improvement), not only analyze
  after the fact.
  Trace: P9 · C60, C63, C67. Verify: a run logs surrogate-guided proposals and
  beats random on a held-out task.
- **R55 (SHOULD)** — Learned quantities (per-task lr, per-combo stability)
  SHOULD be transferable priors with uncertainty estimates, applied only within
  that uncertainty and overridable.
  Trace: P2, P4 · C19, C63. Verify: a prior is applied with stated confidence
  and can be overridden.
- **R56 (SHOULD)** — Knowledge gained by a run SHOULD be queryable as lessons
  (what was learned, which change mattered), tied to code versions.
  Trace: P6, P14 · C61, C88. Verify: a lessons query returns findings linked to
  versions.
- **R57 (MUST)** — Hypothesis, reasoning, and prior-art outputs (reasoner
  chains, LLM proposals, retrieved literature) MUST be records with provenance,
  linked to the experiments they motivated.
  Trace: P17 · C3, C4, C5, C58. Verify: an experiment record links back to the
  hypothesis chain and literature that motivated it.

### 5.12 Failure intelligence

- **R58 (MUST)** — Every failed or abandoned evaluation MUST carry a
  machine-readable cause (infeasible-by-construction, gate-rejected,
  guard-killed, defect, timeout, non-finite, user-stopped) and a severity.
  Trace: P13 · C12, C34. Verify: cause and severity are fields, not log text.
- **R59 (MUST)** — Failures MUST be classifiable automatically, with an
  explicit "unclassified" bucket that is itself a monitored signal.
  Trace: P13 · C12, C36. Verify: the unclassified bucket has a count and an
  owner.
- **R60 (SHOULD)** — From a defect record, the system SHOULD emit a minimal
  reproducer and, where the defect is an implementation fault, a candidate
  regression test.
  Trace: P13 · C34. Verify: a seeded synthetic defect produces a reproducer
  artifact.
- **R61 (SHOULD)** — Failure patterns SHOULD be clusterable across runs so a
  systemic cause is found once, not per-cell.
  Trace: P13 · C58, C59. Verify: a clustering report over defects is actionable.
- **R62 (SHOULD)** — A fix SHOULD be linkable to the failures it resolves, so
  post-fix verification is a query ("which defects does this change close?").
  Trace: P13 · C35, C53. Verify: linking a code change to closed defect records.
- **R63 (SHOULD)** — The ontology compatibility matrix MUST be generated from
  validation (single source), not hand-maintained, so reference docs cannot
  drift from `validate()`.
  Trace: P13, P11 · C33, C88. Verify: generated matrix matches validate()
  behavior by test.

### 5.13 Claim strength, matched comparison, data integrity

- **R64 (MUST)** — Any claim MUST carry an uncertainty statement (seed variance
  or confidence interval) and the number of seeds behind it.
  Trace: P6, P12 · C25, C57. Verify: no record-based claim is expressible
  without n and variance.
- **R65 (MUST)** — Matched comparison against a reference control (e.g.
  backprop) MUST be supported at matched resource budgets (params, FLOPs,
  walltime, batches), so "better" always means "better at equal cost".
  Trace: P12 · C40, C69, C70. Verify: a comparison report refuses unmatched
  pairs.
- **R66 (SHOULD)** — Operating-point constraints (max latency, max memory, min
  accuracy) MUST be expressible as search constraints, not only post-hoc
  filters.
  Trace: P12 · C56, C71. Verify: a constrained search returns only feasible
  points for the stated operating point.
- **R67 (MUST)** — Dataset/split identity and version MUST be part of the
  record; comparisons across data versions MUST be labeled or refused.
  Trace: P3 · C7, C58. Verify: a cross-version comparison is refused or labeled.
- **R68 (SHOULD)** — Train/evaluation leakage and overlap risk MUST be
  checkable for the tasks in use.
  Trace: P3 · C7. Verify: a leakage check is available and reported in the
  record.
- **R69 (SHOULD)** — Robustness (noise, quantization, distribution shift) MUST
  be measurable as a first-class property rather than a one-off experiment.
  Trace: P3 · C39, C47. Verify: a robustness dimension appears in a run spec
  and in the record.

### 5.14 Extensibility and interoperability

- **R70 (MUST)** — New spaces, policies, evaluators, metrics, and stages MUST
  be addable through documented extension points without modifying the core.
  Trace: P14 · all C. Verify: an out-of-tree policy runs end-to-end.
- **R71 (SHOULD)** — Third-party search libraries MUST be usable as policies
  without forking the system.
  Trace: P1 · C20. Verify: at least one external policy runs from a run spec.
- **R72 (SHOULD)** — Execution backends (local, multi-process, cluster) MUST be
  substitutable behind the evaluator with the same record shape.
  Trace: P5 · C50. Verify: a run on a different backend produces comparable
  records.
- **R73 (SHOULD)** — Runs MUST be exportable/importable in a self-describing
  format (spec + records + provenance) so a study can move between machines and
  versions.
  Trace: P11 · C86, C58. Verify: export→import round-trips.
- **R74 (MUST)** — Concurrency (parallel evaluations) MUST be a policy/schedule
  parameter, with store writes consistent under concurrency.
  Trace: P5, P15 · C58. Verify: a parallel run produces the same records as a
  serial one.
- **R75 (MUST)** — Compiled-kernel caching MUST be scoped to run/record
  identity, carry provenance, and invalidate safely; run-scoped state MUST NOT
  live in global singletons.
  Trace: P16 · C51. Verify: two runs with different specs never share a stale
  kernel; the cache is inspectable as records.

### 5.15 Capability preservation and deprecation governance

- **R76 (MUST)** — The capability inventory (§3) MUST be maintained as a
  machine-readable registry (id, stage, description, owner, verifying test)
  that is the reference for "what the system can do".
  Trace: P14 · C1–C88. Verify: the registry exists, parses, and matches §3.
- **R77 (MUST)** — A conformance suite MUST assert every registered capability
  still works; a capability may not be removed or silently degraded without an
  explicit registry change and a recorded rationale.
  Trace: P14 · C1–C88. Verify: CI fails if a registered capability loses its
  test.
- **R78 (MUST)** — Every one-off flag, per-combination table, and
  subsystem-specific report path MUST map to a registered capability or an
  explicit retirement record with migration note (Appendix A is the seed
  inventory and MUST be kept current).
  Trace: P11, P14 · C18, C19, C78–C88. Verify: an inventory audit maps each
  flag/table/report to a capability or retirement.
- **R79 (MUST)** — Schema and spec versions MUST be explicit; readers for prior
  versions MUST exist for the life of the artifacts; unknown fields MUST be
  labeled as unknown, never silently defaulted.
  Trace: P7, P3 · C58, C86. Verify: historical artifacts load with explicit
  unknown-field markers.
- **R80 (SHOULD)** — A generated "what we can do" listing, documented-command
  conformance tests, and standard run profiles (e.g. quick-verify,
  production-map, maturation, claim) as data SHOULD exist, each
  conformance-tested.
  Trace: P11, P14 · C78–C88. Verify: a docs/CLI conformance test fails when a
  documented invocation drifts; profiles are data, not prose.

### 5.16 Human control and live operation

- **R81 (SHOULD)** — A run MUST be pausable, steerable, and resumable
  mid-flight (change budget, add/remove constraints, pin or ban coordinates)
  without corrupting records.
  Trace: P14 · C87. Verify: a steering action mid-run is recorded and takes
  effect.
- **R82 (SHOULD)** — Long-running discovery SHOULD run as a service that
  re-plans as evidence accumulates, rather than a fixed script.
  Trace: P12 · C87, C22, C23. Verify: a service run changes policy/schedule in
  response to new records.
- **R83 (MUST)** — Alerts MUST be defined over record predicates
  (breakthrough, cascade, completion) and MUST notify only — the run/stop
  decision stays with the human.
  Trace: P13 · C85. Verify: an alert fires for a synthetic defect spike; no
  auto stop occurs.
- **R84 (SHOULD)** — Operator intent (why a run was started/stopped/steered)
  MUST be recorded as first-class data.
  Trace: P6, P14 · C64, C58. Verify: intent appears in the run's records.

### 5.17 Outputs and explanation

- **R85 (MUST)** — Every run MUST emit, from the store alone, a report
  covering: objectives and fronts (by fidelity), axis coverage, budget
  consumed, failures by cause, promotion history, and claim-eligible records.
  Trace: P7, P10, P12 · C78–C82. Verify: one command produces all sections.
- **R86 (SHOULD)** — Axis attribution MUST be available for every run and
  comparable across runs, so "which axis matters" is answerable without
  re-running.
  Trace: P1 · C68. Verify: attribution over stored records reproduces a known
  axis effect.
- **R87 (SHOULD)** — Automatic figures/manifests SHOULD be produced for fronts,
  coverage, and fidelity ladders, pinned so regressions are visible.
  Trace: P11 · C83. Verify: a manifest lock exists and updates on change.
- **R88 (SHOULD)** — Narrative handoff summaries (what was tried, learned,
  next) SHOULD be derivable from records.
  Trace: P11, P14 · C80, C88. Verify: a handoff summary is generated from a
  run.

---

## 6. Constraints Any Solution Must Respect

| # | Constraint |
|---|---|
| K1 | Python 3.14+, uv-managed deps, single `uv.lock`; no new mandatory runtime dependency without an explicit decision (optuna and torch already required). |
| K2 | Ruff format/lint; pyright strict on new/rewritten modules; no `Any`; Protocol over ABC. |
| K3 | No blocking I/O inside async paths; existing concurrency model unchanged unless a requirement forces it. |
| K4 | Existing artifacts remain readable; schema changes need old-shape readers (R79). |
| K5 | The KB's vector/surrogate/causal capabilities are assets, not casualties (P9, R15). |
| K6 | Governance fails closed: a record that cannot be validated is not a result. |
| K7 | Performance: a search must not become materially slower per evaluation than today's burst path; record overhead must be measured, not assumed. |
| K8 | Parallelism must not weaken R9/R26 (no duplicate or reordered records under concurrency). |
| K9 | Governance/evidence metadata must be cheap enough to be always-on; if recording costs are significant, that is a design defect, not a reason to make governance optional. |
| K10 | Run-scoped state MUST NOT live in module-level global singletons (P16 is the cautionary example). |

---

## 7. Traceability

### 7.1 Problem → requirement groups
| Problem | Addressed by |
|---|---|
| P1 four implementations | R1, R4, R16–R19, R44, R71 |
| P2 lr unsearched | R2, R6, R52, R55 |
| P3 identity/fidelity | R7–R9, R22, R67 |
| P4 prior tables | R6, R52, R55 |
| P5 budget fragmentation | R21–R24, R45, R72 |
| P6 governance split | R10, R34–R37, R64, R83, R84 |
| P7 four stores | R13, R14, R79 |
| P8 resume semantics | R26–R30, R41 |
| P9 unused analytics | R15, R53, R54 |
| P10 objective registries | R31–R33 |
| P11 CLI/report drift | R14, R20, R63, R78, R80 |
| P12 ladder allocation | R8, R23–R25, R36, R46–R51, R64–R66 |
| P13 late/manual failure handling | R29, R38, R42, R50, R51, R58–R63, R83 |
| P14 no capability registry | R5, R20, R33, R37, R39, R70, R76–R80 |
| P15 env nondeterminism | R11, R12, R28, R74 |
| P16 kernel cache singleton | R75, K10 |
| P17 reasoning disconnected | R57 |

### 7.2 Capability coverage
Every capability C1–C88 is cited by at least one requirement in §5 (group-level
coverage: S1→R5, R33, R37, R43, R57; S2→R1, R4–R6, R16–R19, R25, R38, R52;
S3→R8, R21–R24, R46–R49; S4→R10, R19, R29, R34, R42, R58, R59; S5→R1, R3, R6,
R11, R25, R69, R75; S6→R11, R27–R30, R46, R50, R51, R75; S7→R22, R31, R50, R64,
R66, R69; S8→R7, R9, R12–R15, R41, R48, R53, R57, R67, R73–R75, R79; S9→R32,
R54, R65, R86; S10→R34–R36, R64, R65; S11→R14, R38, R63, R80, R83–R88).
R76–R78 make this coverage mechanically enforced.

---

## 8. Acceptance at the Requirement-Set Level

The set is satisfied when a system exists in which:

1. One coordinate schema expresses the Appendix-B union; a single run yields
   records at more than one lr, substrate, and fidelity (R1–R3, R8).
2. Records differing only in lr/seed/fidelity are distinguishable, separately
   queryable, and never averaged unlabeled (R7–R9).
3. A record written by any policy is queryable, reportable, and
   claim-evaluable by the same code from the same store (R13, R14, R34, R35).
4. Round-robin, stratified, random, and model-based policies traverse the same
   space, produce comparable records, and report coverage (R16–R18).
5. Compute allocation is non-uniform, evidence-driven, and its waste is recorded
   and detectable (R46–R48).
6. Failure causes are machine-readable, clustered, and convertible to
   reproducers; known-bad coordinates are never re-paid (R58, R59, R61, R38).
7. Kill/resume produces no duplicate or reordered coverage under every policy,
   including parallel (R26, R74, K8).
8. Every claim carries n, variance, and a matched-cost reference; CAMPAIGN_PLAN
   §7 is one filter excluding quarantined/gate-failed cells (R64, R65, R35, R10).
9. Every capability in §3 has a registry entry and a passing conformance test;
   no registered capability is lost (R76, R77).
10. A run is fully described by a versioned, diffable, portable spec; stages are
    uniformly present, pluggable, and recorded (R39–R41, R45).
11. Hypotheses, reasoning chains, and retrieved prior art are records linked to
    the experiments they motivated (R57).
12. Kernel caching and all acceleration are scoped to run identity with
    provenance (R75).

---

## 9. Open Questions

Blocking (answers change requirements):

- **Q1** — Is a coordinate required to include *seeds* and *fidelity* (R7, R8),
  or are those properties of the evaluation rather than the coordinate? Decides
  whether "the same cell" means the same identity across tiers.
- **Q2** — Should void pre-classification (C11) be part of the space definition
  (declared infeasible) or of evaluation (discovered infeasible)? Changes when
  cost is paid and what resume must remember.
- **Q3** — For R2, is the default lr search a log grid or model-based seeded
  from the ruler table (C19)? Affects K7 and expected sample cost.
- **Q4** — Is the ruler table an input *prior* to the search or a *default* for
  unspecified coordinates (R52, Q3)? Decides whether its values stay
  authoritative anywhere (P4).
- **Q5** — Does R77's conformance suite gate merges, or is it advisory with a
  waiver path? Affects R78's enforceability and the deprecation process.
- **Q6** — Are parallel evaluations (R74) in scope for the first unified
  release, or deferred? Changes K8 and the store's concurrency design.

Non-blocking (answer before design):

- **Q7** — Is `plasticity` a first-class coordinate axis (R1) or a
  credit/update concern?
- **Q8** — How do the reporting surfaces collapse: one command with scope
  arguments, or one library with thin front-ends (R14, R80)?
- **Q9** — Is the CEEC ledger a record property or a separate artifact
  referenced by records (R34)?
- **Q10** — Do surrogate/causal capabilities enter the search loop (R54) or
  stay analysis-only (R15)?
- **Q11** — Are robustness (R69) and matched-cost comparison (R65) mandatory
  for every claim, or opt-in per study?
- **Q12** — What is the migration story for the ~30 override-table entries
  (R52, R78): retire all, convert to priors, or keep as fallbacks?
- **Q13** — What granularity of kernel-cache scoping is required for R75 —
  per run, per record, or per (run, device, dtype)?
- **Q14** — What is the alert-routing model (webhook targets, severity
  routing, dedup) for R83?
- **Q15** — How deep should literature/LLM integration go in S1 (R57):
  provenance-only linkage, or active hypothesis generation inside the loop?
- **Q16** — Should fenced tasks (R37) be excludable per run via space
  constraints, and should the fence reason be user-visible in proposals?

---

## 10. Risks to Watch During Design

| Risk | Why it matters |
|---|---|
| Custom policy objects may not satisfy third-party sampler contracts | A stratified policy behind a model-based interface can silently lose coverage guarantees (R18). |
| Non-uniform allocation (R46) can bias toward easy-to-evaluate coordinates | Mitigated by recorded allocation rationale (R47) and coverage reporting (R18). |
| Conformance (R77) can become ceremony bypassed under deadline | Mitigation: retirement only via explicit registry change (R78); the registry, not the test, is the enforcement point. |
| One store (R13) could tempt dropping KB analytic features to simplify | K5 and R15 exist to prevent exactly this. |
| Serializable run spec (R41) may fossilize today's assumptions | Keep the spec minimal and versioned (R79); it is a contract, not a schema freeze. |
| Registry/conformance runtime cost could contradict K7 | Evidence metadata must be cheap enough to be always-on (K9); measure, don't assume. |
| Global-singleton habits recreate P16 elsewhere | K10 names the pattern; design must show where run-scoped state lives. |

---

## 11. Audit Completeness

Stated honestly, so the preservation claim is calibrated:

- **Fully audited (flags and behavior)**: `comp continuous` (+`unquarantine`,
  `deep-tier`), `comp campaign` (`kb-report`, `diff`), `comp frontier`,
  `comp search`, `comp verify`, `comp pareto`, `comp train`/`core-train`,
  `comp portfolio` (flag-level).
- **Command-level only (flag-level audit pending)**: `comp run`, `show`, `list`,
  `status`, `report`, `export`, `hypothesis`, `benchmark`, `checkpoint`,
  `compare`, `repro`, `daemon`.
- **Module-level**: all modules listed in §3 "Today" columns were read at the
  API level; deep behavioral audit pending for `execution/_state.py`,
  `lightning_/nas.py`, `stream_protocol.py`.

R78 requires closing these gaps as part of the registry work.

---

## 12. Deferred to Design

Decisions explicitly **not** made here. Each lists the inputs a designer needs
from this document, not a recommendation.

| Decision | Inputs needed |
|---|---|
| Whether the unified system is one process, one module, or one protocol across several | R13, R16, K7 |
| How policy substitutability is expressed, and whether external policies can satisfy stratification | R17, R18, R71 |
| How record identity is represented and how old records are labeled | R7–R9, R79, K4 |
| Whether the store is a new module, an evolution of the KB, or a view over it | R13, R15, K5 |
| How the stage model maps onto the existing call graph, and what a stage's record looks like | R39, R40, R41 |
| How non-uniform allocation is expressed and how it interacts with pruners and fidelity ladders | R46–R49 |
| How governance is represented as always-on record properties versus gates | R10, R34, R35, K6, K9 |
| How the CLIs collapse and what is documented/tested | R78, R80 |
| How per-combination priors are represented so search can supersede them | R52, Q3, Q4, Q12 |
| How the capability registry and conformance suite are structured | R76–R78 |
| Where run-scoped state (including compiled kernels) lives | R75, K10, Q13 |

---

## Appendix A — Flag Inventory (preservation seed; R78)

Commands and flags verified in this audit. Each maps to a capability (C#) and
is protected by the conformance requirement (R77). Commands marked
"command-level only" in §11 are listed without flags pending audit.

**comp continuous** — `--budget` (C22), `--target-cells` (C22), `--objectives`
(C1, C2), `--maturation` (C26), `--loop` (C23), `--sleep` (C23), `--root`,
`--log-path` (C80), `--max-iterations` (C31), `--cells-per-iter` (C31),
`--epochs` (C24), `--task` (C7), `--tasks` (C30), `--seed` (C49),
`--hidden-dim` (C41), `--depth` (C41), `--param-budget` (C16, C40),
`--geometry-sampling` (C17), `--limit-batches` (C24), `--credit-trace` (C42),
`--substrate` (C39), `--dry-run` (C32); subcommand `unquarantine`
(`--defect`, `--unquarantine-fixed` → C34, C35); subcommand `deep-tier`
(`--top`, `--seeds`, `--dry-run` → C26, C25).
**comp campaign** — `kb-report` (`--root`, `--task`, `--objectives`,
`--output-dir` → C79); `diff` (`--root-a`, `--root-b`, `--task` → C78).
**comp frontier** — `--report`, `--backprop`, `--json` (C69, C70).
**comp search** — `--credit`/`--model`, `--portfolio-csv`, `--task`,
`--trials`, `--tier`, `--seeds`, `--seed`, `--sampler`, `--device`, `--output`,
`--db` (C21, C20, C28).
**comp verify** — `--study`, `--top-k`, `--seeds`, `--seed`, `--epochs`,
`--task`, `--output`, `--db` (C76).
**comp pareto** — `--study`, `--output-dir`, `--format`, `--db` (C82).
**comp train / core-train** — `--config`, `--model`, `--task`, `--dataset`,
`--epochs`, `--batch-size`, `--lr`, `--optimizer`, `--hidden-dim`, `--device`,
`--no-track-energy` (C37, C43, C52).
**comp portfolio** — `--tasks` (C71).
**Command-level only (pending flag audit)** — `run`, `show`, `list`, `status`,
`report`, `export`, `hypothesis`, `benchmark`, `checkpoint`, `compare`,
`repro`, `daemon` (C50, C58, C73–C76, C78–C87).
**Scripts** — `scripts/campaign_analyze.py` (C81); probe conventions under
`scripts/probes/` (measurement provenance, C58).

## Appendix B — Axis Enumerations (audit-verified; R1, R5)

**B.1 Dynamics (8)** — `energy_minimization`, `predictive_settling`,
`error_predictive_coding`, `pc_alm`, `spike_integration`, `instantaneous`,
`diffusion`, `lazy`.

**B.2 Geometry/topology (10)** — `feedforward` (+`residual`), `recurrent`,
`tile_mesh` (`neurons_per_tile`, `tiles_per_layer`), `attention`
(`num_heads`, `head_dim`), `spatial_lattice` (`lattice_dims`,
`connectivity_radius`), `nca`, `ntm`, `conv`, `graph`,
`causal_transformer`. Common keys: `input_dim`, `output_dim`, `hidden_dims`,
`num_layers`, `init_scale`, `init_scheme` (`default`/`mupc`/`innocenti`).
Grid-parameterizable subset today: feedforward, recurrent, tile_mesh,
attention, spatial_lattice, ntm (conv/graph/nca/causal_transformer excluded for
task-shape reasons — a fact the unified space must preserve as constraints,
not lose).

**B.3 Credit (10)** — `gradient`, `homeostatic`, `local_contrastive`,
`local_goodness`, `pc_alm`, `pepita`, `random_projections`, `target_inversion`,
`temporal_trace`, `thermodynamic_contrast`.

**B.4 Update (13+)** — `adam`, `local_adam`, `ortho_adam`, `euclidean`,
`mean_norm`, `unit_rms`, `muon`, `lion`, `riemannian_orthogonal`,
`spectral_constrained`, `elastic_consolidation`, `natural_gradient`,
`role_split` (+ sub-rule pairing).

**B.5 Substrate (9 families)** — `digital`, `analog`, `memristive`,
`neuromorphic`, `optical`, `quantum`, `complex`, `sparse`, `ternary`; parameters
include `noise_level` and `precision` (e.g. `int8`).

**B.6 Tasks (15+)** — `mnist`, `kmnist`/`kuzushiji`, `cifar10`, `fashion`,
`digits`, `usps`, `svhn`, `char_ngram`, `shakespeare`/`tiny_shakespeare`
(fenced, C8/R37), `pendulum`, `acrobot`, `cartpole`/`rl`, `xor`, `spiral`,
`circles`. Splits: TRAIN/VAL/TEST/TRAIN_VAL. `quick_mode` reduces data and
forces `num_workers=0` (P15).

**B.7 Objectives (~39)** — task: `accuracy`; cost: `walltime_s`,
`param_count`, `flops`, `memory_mb`, `energy_per_step`, `latency_ms`;
substrate: `energy_per_op`, `ir_drop_variance`, `write_energy_pj`,
`endurance_cycles`, `spike_rate`, `event_density`, `synaptic_ops_per_sample`,
`spike_energy_pj`, `phase_noise`, `optical_power_mw`, `insertion_loss_db`,
`phase_shifter_energy_pj`, `gate_fidelity`, `coherence_time_us`, `shot_noise`,
`qubit_count`, `thermal_noise_variance`, `nonlinearity_error`, `drift_rate`,
`precision_bits`; ruler-relative: `bp_deficit`, `ruler_walltime_ratio`,
`ruler_energy_ratio`; stability: `spectral_radius`, `lyapunov_exponent`,
`max_singular_value`; plasticity: `psi_capacity`, `consolidation_cost`,
`rewrite_rate`, `credit_alignment`, `feedback_path_length`, `trace_variance`.

**B.8 Hand-maintained prior tables (to be superseded per R52)** —
`_STEP_SIZE_OVERRIDES` (30+ `(dynamics, credit)` entries),
`_DYNAMICS_STEP_SIZE_OVERRIDES` (`diffusion` 0.001, `predictive_settling`
0.01), `_ruler_lr` (per-task; non-feedforward topologies default 1e-2),
`TASK_COMPAT` fence (char_ngram, shakespeare, tiny_shakespeare, wikitext2,
penn_treebank).

---

## 13. Addendum (Rev 3) — Completeness Audit: Gaps in the Union

**Status**: CANDIDATES, pending review. Produced 2026-09-29 from a code-level
pass over `hyperopt/search_space.py::RULE_SPACES`, `packages/computronium-lab`,
`computronium/lightning_/`, `computronium/execution/`, `computronium/analysis/`,
and the platform packages. Items below would extend §2/§3 and Appendices A–B
before design; nothing here is accepted until reviewed.

### 13.1 P1 undercounts the implementations (four → six)
| Implementation | Space it expresses | Policy | Store | Status here |
|---|---|---|---|---|
| `packages/computronium-lab` research layer (`synthesis/`, `research/`, `campaign.py`, `sequential.py`, `adaptation.py`) | spec→coordinate synthesis (`Lab.specify/synthesize/explore`), budgeted evolution (`plan_evolution`/`run_evolution`), certified corpus (`MeasurementRunner`, 8 problem classes), continual + substrate-transfer benchmarks | evolution (population/generations), synthesis with constraint screening | own `record_ledger` sqlite + CEEC per generation | absent from P1 and §3 |
| `computronium/lightning_/` (`nas.py`, `hpo.py`, `experiment.py`, `strategies.py`) | NAS + Lightning HPO loop | trainer-driven search | trainer/Lightning state | §11 audit-pending; zero §3 rows |
| `computronium/execution/` (`engine.py`, `strategy.py`, `candidate_gen.py`, `synthesizer.py`, `criteria.py`, `task_weights.py`) | candidate generation / strategy progression | strategy progression | execution state | §11 audit-pending; zero §3 rows |

Consequence: the §3 union — and therefore R76's seed registry and R78's
inventory — is incomplete until these are audited and rowed. Candidate action:
extend the P1 table, add §3 capability rows, close the §11 gaps.

### 13.2 The continuous-space hyperparameter union is missing from Appendix B
`hyperopt/search_space.py::RULE_SPACES` holds **10 rules / 70 slots / 37 unique
parameters** (enumerated in Appendix C). None appear in R1's axis list or
Appendix B — the same "describable here, inexpressible there" class P1
condemns. Also missing:

- `SearchSpace.apply_constraints` (`max_hidden`/`max_layers`/`max_steps`) — a
  fourth constraint mechanism (input to consolidation C, §14).
- Batch size as a schedule axis; per-update optimizer parameters (adam betas,
  muon momentum).

Candidate fix: add **B.9** (per-rule continuous union), or declare per-rule
spaces registry data under R5 with Appendix C as the audit baseline.

### 13.3 Collectable results not inventoried (§3 candidate rows)
| Collectable | Source | Stage |
|---|---|---|
| EMA-harvest metrics (`harvest_mode`; depth-50 0.784→0.917) | `SystemTrainerConfig` | S7 |
| I(C,U) model outputs; `icu_measurements.csv` rows | `fit_icu_model.py`, `harvest_icu_table.py` | S8/S9 |
| Recipe-card registry state (credit×update → canonical constructor) | `recipe_cards.py` | S5/S8 |
| Frozen-θ ψ benchmark results (adaptation/recovery/migration; bitwise θ audits) | TODO16 §5 suite | S6/S10 |
| Mechanistic-study + stability×memory claim records (factorial 648-cell) | `results/*/claim_record.json` | S8/S10 |
| ANOVA/Sobol indices; genealogy fingerprints/phylogeny; failure manifestos; energy-landscape/Hessian; interpretability outputs | `analysis/{ablation,genealogy,failure_manifesto,energy_landscape,interpretability}.py` | S9 |
| Microbench JSONL artifacts (git-SHA-tagged parity/microbench evidence) | `acceleration/microbench` | S8 |
| Distributed fault records (lost workers, step, partial metrics); distributed topology provenance | `DistributedTrainingError`, `p2p/` | S6/S8 |

Note: R75 scopes the kernel *cache*; the kernel ladder's *evidence trail* is a
distinct record type this inventory does not yet carry.

### 13.4 Experiment procedures not inventoried (§3 candidate rows)
- The 5-level joint benchmark suites' *procedures* (phase-A/B task switching,
  matched-compute comparison, zeroed-weight damage, A₀→A₁ migration, frozen-θ
  operator battery) — `comp benchmark` is command-level-only in Appendix A.
- MEP tournament (factorized ablation + ANOVA/Sobol); cross-domain transfer.
- Evolution campaigns (CEEC pre-registered per generation); corpus
  certification (`MeasurementRunner`, certified tier); continual and
  substrate-transfer benchmarks; synthesis pipeline
  (`specify→synthesize→build→train→explore`).
- Kernel ladder promotion procedure (reference → torch.compile → Triton, with
  parity + microbench evidence) — a governed procedure deserving a row.
- Proposer modes declared in `proposer.py` but never rowed:
  one-parameter-at-a-time ablation; curriculum progression.

### 13.5 Minor gaps
- **B.6** omits three domains: graph (`cora`/`citeseer`/`pubmed`), tabular
  (`breast_cancer`/`iris`/`wine`), time-series/scientific
  (`synthetic_forecast`, `lorenz`) — README claims ~25 tasks / 7 domains vs
  B.6's 15+.
- Package capabilities uncounted: `stability` (the calibrated τ=1.029 guard is
  C48's implementation), `psi_peft`, `local_feedback` (X-ALI-001/002).
- Model export (ONNX/TorchScript/INT8/ternary) is a post-promotion artifact
  path distinct from C86 study export.

---

## 14. Addendum (Rev 3) — Consolidation Candidates

**Status**: PROPOSALS, pending review. Each abstraction below subsumes a
cluster of §5 requirements without dropping any verification clause. They are
inputs to the §12 design decisions, not decisions.

| # | Abstraction | Subsumes | Notes |
|---|---|---|---|
| A | **One registry pattern** — spec dataclass + integrity locks + doc codegen; instances: axis registry (R5), objective registry (R31), capability registry (R76), flag inventory as a registry *view* (R78), constraint registry, prior store, extension points (R33, R70) | R5, R31, R33, R70, R76–R78, R80 | matches existing doctrine: 64-spec `ImplementationSpec` registry, `test_dynamics_wiring_lock`, registry completeness locks; one conformance harness over all instances |
| B | **One record schema, four identity sections** — identity = coordinate ∪ schedule(fidelity/seed/epochs/batches) ∪ provenance(env/data/code) ∪ status(governance) | R7, R8, R9, R11, R67, R79; R22/R67 become derived comparison guards | resolves Q1: "same cell" = coordinate key; "same measurement" = full identity |
| C | **One legality/constraint engine** — predicates over coordinates with recorded reasons; enforced at S4, re-checkable at S6, queryable, globally suppressive | R19, R25, R37, R38, R66; absorbs Q2 and `SearchSpace.apply_constraints` | dry-run (C32) is the preview of the same engine; R42 propagation falls out by construction |
| D | **Obligations on the pipeline, not the plugins** — policies/stages/evaluators/backends implement small Protocols; the wrapper emits coverage stats, void/defect classification, traceability, stage fragments for *any* plugin | R16–R18, R39–R40, R70–R72 | R17 becomes the shipped-plugin catalog — the preservation proof |
| E | **Governance as stored predicates** — statuses/causes/verdicts are record fields written by their producing stage; claims, promotion, alerts, reports are pure queries over them | R10, R34–R36, R58–R59, R64, R83 (+K6 unchanged) | settles Q9: ledger status is a record field with provenance link, not a side artifact |

### 14.1 Requirement merges (88 → ~60)
| Merge | Survives as | Verifications preserved |
|---|---|---|
| R7+R8+R9+R11+R67 | identity schema (B) | distinguishability, labeled mixtures, repeats-as-distinct-records, provenance fields, version guards |
| R26+R27 | replay determinism | replay hash is the assertion mechanism |
| R21–R24 | budget + cost model | one interface; R23/R24 remain SHOULD clauses on it |
| R34+R35+R36 | evidence lifecycle (E) | predicate-computable promotion/release/claims |
| R46–R49 | allocation policy | "measured cost-to-rank beats uniform" kept verbatim |
| R50+R51+R58+R59 | failure telemetry schema | signal+value+cause+severity as fields; unclassified bucket monitored |
| R60+R61+R62 | failure learning loop | reproducer → cluster → fix-linkage (SHOULD cluster) |
| R52+R53+R55+R56 | priors/lessons as records | R54 = the surrogate instantiation of the same mechanism |
| R31+R33 | objective registry + extension point | out-of-tree objective participates |
| R1+R5 | registry-driven coordinate schema (A) | Appendix B union discoverable at runtime |
| R76+R77+R78+R80 | registry + conformance harness (A) | Appendix A becomes a view of the registry |
| R85+R86 | one report | attribution as a report section; R87/R88 stay SHOULD add-ons |
| R39+R40 | stage plugin contract (D) | no-op stages emit explicit fragments |

R74/K8 stay separate (concurrency is genuinely distinct).

### 14.2 Pillar restructure of §5 (candidate)
1. Schema — coordinate, record identity, registries
2. Execution — stages, policies, budget, determinism
3. Legality — constraint engine, voids/defects
4. Evidence — governance predicates, allocation, failure intelligence
5. Learning — priors, surrogates, lessons, reasoning records
6. Surface — store, reports, CLI, conformance, operations

Traceability (§7) simplifies to problem → pillar → requirement; acceptance (§8)
is unchanged in substance; Q1/Q2/Q9 are resolved by the abstractions rather
than answered separately.

### 14.3 Guard rails (what consolidation must not do)
- No MUST→SHOULD demotion: every verification clause survives its merge.
- R17 stays a catalog — the policy union *is* the preservation proof.
- Global suppression (R38) stays distinct from per-run constraint scoping.
- K5/K6/K9/K10 are design invariants, not mergeable requirements.

## 15. Addendum (Rev 3) — Recommended Order (candidate)
1. Fix the union first (§13.1–§13.5): audit lab/lightning/execution, add B.9
   and the missing domain rows. Consolidating on an incomplete union bakes the
   gaps into the registry permanently.
2. Adopt abstractions A–E as §12 design inputs (they answer the "how policy
   substitutability is expressed", "how governance is represented", and "how
   the CLIs collapse" rows directly).
3. Renumber §5 under the pillar structure after review.

## Appendix C — Per-rule continuous hyperparameter union (audit-verified 2026-09-29; B.9 candidate)

Source: `computronium/hyperopt/search_space.py::RULE_SPACES`. 10 rules, 70
parameter slots, 37 unique parameters. Authoritative ranges/scales live in the
source table; this appendix proves the union exists and is counted (R1, R5).

| Rule | Parameters |
|---|---|
| backprop (4) | learning_rate, weight_decay, hidden_dim, num_layers |
| eqprop (18) | learning_rate, weight_decay, hidden_dim, num_layers, beta, max_steps, damping, tol, convergence_threshold, convergence_start, sparse_ratio, momentum, update_scale, update_scale_by_depth, w_rec_init, w_rec_gain, feedback_gain, feedback_init_gain |
| neural_cube (4) | learning_rate, weight_decay, cube_size, max_steps |
| pepita (3) | learning_rate, hidden_dim, num_layers |
| forward_forward (6) | learning_rate, hidden_dim, num_layers, threshold, layer_lr, classifier_lr |
| feedback_alignment (6) | learning_rate, hidden_dim, num_layers, alpha, feedback_mode, use_spectral_norm |
| target_prop (4) | learning_rate, target_lr, hidden_dim, num_layers |
| pc_alm (11) | learning_rate, weight_decay, hidden_dim, num_layers, step_size, rho, prospective_leak, max_steps, beta, convergence_threshold, convergence_start |
| hebbian (4) | learning_rate, hidden_dim, num_layers, use_oja |
| spiking (10) | learning_rate, hidden_dim, num_layers, num_steps, tau_mem, tau_syn, spike_threshold, refractory_period, dt, spike_grad |

Unique set (37): alpha, beta, classifier_lr, convergence_start,
convergence_threshold, cube_size, damping, dt, feedback_gain,
feedback_init_gain, feedback_mode, hidden_dim, layer_lr, learning_rate,
max_steps, momentum, num_layers, num_steps, prospective_leak,
refractory_period, rho, sparse_ratio, spike_grad, spike_threshold, step_size,
target_lr, tau_mem, tau_syn, threshold, tol, update_scale,
update_scale_by_depth, use_oja, use_spectral_norm, w_rec_gain, w_rec_init,
weight_decay.

---

*Ends at requirements. §13–§15 and Appendix C are an unreviewed addendum
(audit + consolidation candidates). Design, decomposition, and sequencing
follow a review of both layers; nothing in §5–§8 or §13–§15 presumes a
particular solution shape.*