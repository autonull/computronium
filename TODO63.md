# TODO63: Realize Computronium — Wire the Whole System Into One Autonomous, Rigorous Loop

**Status:** DRAFT v2 — adaptive; workstreams decoupled, reprioritizable live.
**Predecessors:** TODO60 (kernel move), TODO61 (bug fixes, hyperparameter flow, quick maturation),
TODO62 (the continuous loop — *this document supersedes its implementation, keeps its goal*).
**One-line goal:** Stop using a fraction of the system. Wire the existing registry, evidence
stack, maturity ladder, objective registry, analysis suite, and campaign engine into **one
closed-loop engine** that tests *all* domains, learns from every defect, and surfaces only
statistically grounded, multi-objective discoveries — with no human babysitting.

> **Relationship to TODO62.** TODO62 defined the right goal — a continuous propose→run→analyze→
> fix loop — but realized it as a *parallel mini-system* (`scripts/continuous_experiment.py`,
> ~400 lines re-implementing proposal/promotion/reporting, with hardcoded seeds and hints).
> TODO63 keeps the goal and **retires that implementation**, driving the engine that already
> exists. Where TODO62 added code beside the engine, TODO63 deletes code and wires the engine.

---

## 0. The Real Problem

An honest audit (§2) shows Computronium is **far more complete than our usage of it**. The
engine already contains:

- a **maturity ladder** — `execution/promotion.py`: L0 write → L1 eligibility (seed count +
  PASS gate) → L2 replay reproducibility, with cost metrics correctly excluded from claims;
- a **proposer interface** — `execution/policy.py`: `propose(ctx)`, `ProposalContext`,
  `ICUPredictor`, Optuna-backed;
- a **campaign engine** — `design/{hypothesis,campaign_dsl}.py`, `execution/campaign.py`,
  `execution/campaign_queue.py` (priority, dependencies, quotas, preemption);
- an **objective/metric registry** — `schema/metrics.py` (`MEASURED_OBJECTIVES`,
  `MEASURED_METRICS`, ~90 metrics incl. energy/substrate/plasticity), `schema/registries.py`
  (`OBJECTIVES_REGISTRY`);
- an **evidence stack** — `evidence/` (store, claims, status, significance, statistics,
  limitations, artifacts, procedures, protocol, model_registry, failure);
- an **analysis suite** — `analysis/` (pareto, seed_variability, hardware_variance,
  reproducibility, nonnormality, counterfactual, mediation, axis_attribution, energy_landscape,
  gradient_stats, weight_evolution);
- a **web dashboard** — `execution/dashboard/web.py` + `computronium … dashboard`;
- a **26-task, 6-domain registry** — `domains/registry.py::SUPPORTED_TASKS`.

**And we used almost none of it.** We ran:

- `digits` **only** (the registry has 26 tasks across vision/language/RL/graph/tabular/memory);
- ad-hoc `run_*.sh` scripts that **bypass the CLI** (`surface/cli.py` has ~40 subcommands);
- a loop (`scripts/continuous_experiment.py`) that **re-implemented** proposal, promotion, and
  reporting in ~400 lines — hardcoding `KNOWN_GOOD` seeds, `FIX_HINTS`, `best_acc`, and grid
  unions — while the real engine sat unused beside it.

So TODO63 is **not** "build an experiment system." It is **"delete the parallel mini-system,
wire the real one into a loop, and fill the few genuine gaps."**

### Root causes

1. **Two parallel systems.** `scripts/continuous_experiment.py` duplicates capability that
   lives in `experiment/execution/*` and `experiment/evidence/*`, so neither improves the other.
2. **No integration seam.** The kernel, evidence store, promotion ladder, and campaign queue
   have no single "run a closed loop" entry point. We filled the vacuum with shell scripts.
3. **Coverage debt.** Cross-domain breadth was never wired (`RunSpec.tasks` exists, unused).
4. **Write-only telemetry.** `defects.jsonl` / `FIX_HINTS` recorded failures that never
   constrained the next search.
5. **No reference.** No online baseline means accuracy numbers were uninterpretable.

---

## 1. Operating Principles (unchanged — these judge every workstream)

1. **No mystery.** Slow run, no-effect parameter, silent filter, unexplained failure ⇒ **defect**.
2. **No hardcoding.** Axes, budgets, seeds, tasks, baselines, thresholds ⇒ discovered/configured.
3. **Everything vs. a live baseline.** Discovered online, same task/seed/budget/hardware.
4. **Multi-objective by default.** Pareto over the declared objective set, never one number.
5. **Promotion is a measurement.** The existing ladder decides; humans never eyeball a promotion.
6. **Every failure is data.** Defects feed constraints, validation, and process fixes.
7. **The whole system is the subject.** All 6 domains; vision-only is a coverage defect.
8. **Adaptive by construction.** Registry row / Protocol, never a loop refactor.
9. **Hypotheses first-class, not mandatory.** Exploratory runs still register what they did.
10. **Self-aware validation.** Report what cannot yet be measured (drift, gaps, calibration).

---

## 2. Capability Audit — EXISTING vs. MISSING (the load-bearing section)

Legend: **[WIRE]** = exists, needs integration into the loop · **[EXTEND]** = exists, needs a
generalization · **[BUILD]** = genuinely absent.

| Capability | Where it lives today | Status | Workstream |
|-----------|----------------------|--------|-----------|
| Objective/metric registry (~90 metrics) | `schema/metrics.py`, `schema/registries.py` | **[WIRE]** into loop objectives | D |
| Maturity ladder L0→L1→L2 | `execution/promotion.py` | **[WIRE]** into loop; add stats gates | B |
| Proposer interface (Optuna) | `execution/policy.py` | **[EXTEND]** multi-objective | E |
| Campaign engine (DSL, queue, quotas) | `design/`, `execution/campaign*.py` | **[WIRE]** as the driver | A/H |
| Evidence stack | `evidence/*` | **[WIRE]** auto-populate per run | J |
| Analysis suite (pareto, seeds, hw, repro) | `analysis/*` | **[WIRE]** into reports/gates | B/J |
| Web dashboard | `execution/dashboard/web.py` | exists | — |
| Dataset versioning | `data/dataset_registry.py` | **[WIRE]** | F |
| Environment capture | `experiment/environment/` | **[WIRE]** baseline fingerprint | C |
| 26-task / 6-domain registry | `domains/registry.py` | **[WIRE]** `RunSpec.tasks` | F |
| Per-domain objectives (perplexity / F1 / RL-return) | registered but **unmeasured** (`seed_registries.py:448`, `_measured` @385) | **[BUILD]** objective emission | F0 |
| Backprop-relative comparison vocabulary ("ruler") | `seed_registries.py` (`bp_deficit`, `ruler_*_ratio`) | **[WIRE]** as baseline reference | C |
| CLI command tree (~40 cmds) | `surface/cli.py`, `cli/hypothesis_campaign.py` | **[WIRE]**; delete shell scripts | G |
| Execution backends (Local/Multiprocess/DDP) | `execution/backends.py::ExecutionBackend` | **[WIRE]** as the default seam; Ray/SLURM **[BUILD]** later | N |
| **Online baseline discovery** | comparison only (`evidence/claims.py::beats_baseline`, `status.beats_baseline`); no producer | **[BUILD]** discovery run type | C |
| **Defect registry → constraints** | none (`FIX_HINTS` dict only) | **[BUILD]** | I |
| **Coverage-driven scheduling** | none | **[BUILD]** | F |
| **Unified ExperimentRegistry** | split: store + `state.json` + `ledger.jsonl` | **[BUILD]** thin unification | A |
| **Parameter-effect lock (repo-wide)** | one narrow lock (`test_hyperparameter_flow_lock`) | **[EXTEND]** to all declared knobs | K |
| **Terminal TUI** | web dashboard only | **[BUILD]** | L |
| **Per-stage timing instrumentation** | none | **[BUILD]** | K |
| **Gate calibration / self-grading** | none | **[BUILD]** | M |
| Provenance metadata (`env`, `code_sha`, `dataset`) | `schema/coordinate.py:289` `Provenance`; `environment/snapshots.py` | **[EXTEND]** populate + enforce per record | O |
| Deterministic seed hierarchy | per-schedule `seed`/`n_seeds` (`execution/budget.py`); no master→cycle→cell RNG | **[BUILD]** `SeedContext` | O |
| Store migration / schema upgrade | `evidence/store.py` (versioning); `schema/versioning.py` | **[EXTEND]** bootstrap migration | O |
| Cycle checkpoint / crash recovery | none (loop restarts from `state.json`) | **[BUILD]** transactional cycle commit | O |
| Model/artifact registry wiring | `evidence/model_registry.py` (exists, unused) | **[WIRE]** on the success path | J |
| Cross-domain metric normalization | `analysis/pareto_analysis.py`; `ObjectiveSpec.normalizer` | **[EXTEND]** per-task + ruler-relative | F |
| Constraint versioning / rollback | none | **[BUILD]** | I |

> **This table is the plan's spine.** A workstream that says "[WIRE] X" must *delete* any
> duplicate of X in the loop, not add alongside it.

---

## 3. Defect Register (observed)

| # | Defect | Root cause | Fix |
|---|--------|-----------|-----|
| **C1** | Maturation subspace ≠ discovery subspace; 98% config never re-tested | Human-picked axes in shell scripts | §4 B (auto-promotion) |
| **C2** | L0 screens are noise (≤37% at 1 epoch); no statistical promotion | Fidelity used as guess | §4 B (stats gates on the ladder) |
| **C3** | No baseline ⇒ "98%" uninterpretable | No online baseline type | §4 C |
| **C4** | Loop maximizes one number (`best_acc`) | `merge_top` sorts by acc | §4 D (objective set) |
| **C5** | `defects.jsonl`/`FIX_HINTS` write-only | No consumer | §4 I |
| **C6** | Only `digits` ever run | Scripts never set `--tasks` | §4 F |
| **C7** | Shell scripts duplicate CLI + loop duplicates engine | No integration seam | §4 A, G |
| **C8** | `tail -f` is the UX | No terminal monitor | §4 L |
| **C9** | Silent drops / no-effect params (history: `params={}`, alias drift) | Declaration vs consumption drift | §4 K |
| **C10** | Evidence/discovery loop disconnected | Manual publish only | §4 J |
| **C11** | Loop can't grade its own gates/env | No calibration | §4 M |
| **C12** | Backprop baseline scope limited on the winning geometry | D1 (`gradient × tile_mesh` forward shape mismatch) was handled by a *rejection* (`_validate_gradient_credit_instantaneous_output_proj`, `system.py:435`), not a fix — so a backprop ruler cannot run on `tile_mesh` | §4 C (fallback ruler geometries + explicit evidence limitation) |

---

## 4. Workstreams

> Each workstream states **Problem / What exists / Deliverable / Integration points / Lock /
> Verification**. "[WIRE]" workstreams are as much **deletion** as addition.

### A — One Orchestrator (retire the parallel mini-system) · fixes C7, C1

**Problem:** `scripts/continuous_experiment.py` re-implements proposal, promotion, and
reporting, and disagrees with `experiment/execution/*`.

**What exists:** `execution/campaign.py::run_campaign`, `CampaignSpec`;
`execution/campaign_queue.py`; `execution/policy.py::propose`; `execution/promotion.py`;
`execution/decision.py`; `execution/adaptive_budget.py`, `allocator.py`, `cost_tracking.py`.

**Deliverable:** a single `computronium experiment loop` command that drives the **existing**
engine. The loop is: *choose work (coverage+exploit) → `propose` → run cells → write evidence →
run promotion ladder → record defects → repeat*. `scripts/continuous_experiment.py` **and**
`scripts/run_autonomous.py` are **deleted**; their few genuinely good ideas (`force_explore` on
empty, defect digests) are re-expressed as policies/constraints on the real engine.
`scripts/run_experiment.py` is retained as the *engine's* kernel entry point, invoked by the
loop — not by hand.

**Integration points:** `experiment/execution/campaign.py`, `campaign_queue.py`, `policy.py`,
`promotion.py`; new thin `experiment/registry/loop.py`; `surface/cli.py` `loop` subcommand.

**Lock:** `tests/property/test_loop_uses_engine_lock.py` — the loop must call
`run_campaign`/`promote`, never a re-implementation; fails if any hardcoded seed/hint list
returns.

**Verification:** `computronium experiment loop --cycles 2` runs via the engine; grep proves
`continuous_experiment.py` is gone and no `KNOWN_GOOD`/`FIX_HINTS` literals remain.

---

### B — Statistical Promotion on the Existing Ladder · fixes C1, C2

**Problem:** The ladder exists but promotion is arithmetic on the store (`promotion.py`);
screening has no statistical gate, so noise promotes.

**What exists:** `execution/promotion.py` (`eligible_cells`, `filter_promoted`, L0→L1→L2,
`Maturity`, `ReproducibilityClass`); `analysis/reproducibility.py`, `seed_variability.py`.

**Deliverable:** add **statistical gates** to the L1 rung, and make L0 **screen-only**:

| Rung | Meaning (today) | Add |
|------|-----------------|-----|
| L0 | written | unchanged (screen) |
| L1 | seed count + PASS gate | **+** `mean > baseline + 2·SE`, `CI_width < δ`, `train/val gap < g`, `ρ ∈ band` |
| L2 | replay reproduces claim | unchanged (**+** every seed beats baseline) |

Thresholds (`δ, g, band, margin`) are **config-driven**; `GateResult` records statistic,
threshold, and reason so the registry explains *why* a config stopped.

**Hardening at scale (multiplicity + power):** screening thousands of cells and promoting at a
fixed `2·SE` manufactures false positives through selection effects (the winner's curse). Gate
thresholds and seed counts must be **derived from a power analysis over measured seed variance**
(`analysis/seed_variability.py`), not hardcoded. A **multiplicity-control** protocol — or a
strict **discovery-seed vs. confirmation-seed separation** (promote only on fresh seeds, never
the seeds that selected the cell) — must be enforced so the autonomous loop cannot inflate its
false-positive rate. L2's replay rung is the natural confirmation stage.

**Integration points:** `execution/promotion.py`, `execution/decision.py`,
`schema/metrics.py`, `analysis/seed_variability.py`.

**Lock:** removing the stats gate makes a lock fail. A config failing L1 names its failed
statistic. (AGENTS.md: a lock whose fixture cannot fail is a comment.)

**Verification:** an intentionally noisy cell is **not** promoted; the promotion report cites
the failing statistic and the matching baseline.

---

### C — Online Baselines (the genuine build) · fixes C3, C12

**Problem:** No reference for any number. Hardware varies, so a shipped suite would be wrong.

**What exists:** the *comparison* primitive — `evidence/claims.py::beats_baseline(record,
baseline_accuracy, margin)` and the `beats_baseline` derived claim (`evidence/status.py`) — a
**"ruler" objective family** (`bp_deficit`, `ruler_walltime_ratio`, `ruler_energy_ratio`,
`ruler_param_ratio` in `seed_registries.py`) that already names backprop-relative objectives —
and `experiment/environment/` (fingerprinting). What is missing is any **producer** of the
baseline itself. Build on the ruler vocabulary; do not invent a second one.

**Deliverable:** baselines are a **discovered run type**, not a constant:

- Standard optimizers/architectures (`sgd`, `adam`, `adamw`; MLP / small CNN / small LM as
  applicable per domain) run on the **same task, seeds, budget**, on the **current hardware
  fingerprint**.
- Stored as `BaselineRecord` tagged `(task, hardware_fingerprint, budget, seeds)`.
- `BaselineGate` looks up the match; if absent it **runs one** (or blocks promotion with an
  explicit reason — never silently passes).
- The baseline *set* is config, extensible per domain.
- **Ruler geometry fallback (C12):** where the backprop ruler cannot run on the winning
  geometry (`tile_mesh`), define an equivalent-capacity fallback geometry (e.g. `feedforward`)
  and record the substitution — the evidence must **explicitly state** this limitation rather
  than present a matched-geometry claim that cannot be made.

**Integration points:** new `experiment/registry/baseline_registry.py`;
`experiment/environment/` for fingerprint; `execution/promotion.py` consumes it;
`surface/cli.py` `baseline run`.

**Lock:** every promoted config has a same-hardware, same-budget baseline; a lock fails if a
promotion occurs without one.

**Verification:** report shows `Δ = candidate − baseline` with a confidence interval; a
promotion on an unseen (task, hardware) pair either triggers a baseline run or is blocked with
a reason.

---

### D — Multi-Objective Optimization via the Existing Registry · fixes C4

**Problem:** The loop sorts by `val_acc`; the registry already declares ~90 measurable metrics
and a direction for each.

**What exists:** `schema/metrics.py` (`MEASURED_OBJECTIVES`, `MEASURED_METRICS`,
`objective_values`, `optimizes`), `schema/registries.py::OBJECTIVES_REGISTRY`;
`analysis/pareto_analysis.py`.

**Deliverable:** the loop's objective set is read from config/registry (≥3 by default:
`validation_accuracy × param_count × walltime_total`, extensible to energy/ρ/latency). The
Pareto frontier and proposals both use this set.

**Integration points:** `schema/metrics.py`, `analysis/pareto_analysis.py`, `execution/policy.py`.

**Lock:** the objective set flows config → proposal → report; adding an objective edits config
only.

**Verification:** frontier moves when an objective's weight/direction changes; no `best_acc`
sort remains in the loop.

---

### E — Extend the Proposer to Multi-Objective · fixes C4

**Problem:** `execution/policy.py` proposes via Optuna, but optimisation targets one metric.

**What exists:** `policy.py::propose`, `ProposalContext`, `ICUPredictor`, `ToolkitPolicy`;
`execution/optuna_adapter.py`; `execution/search_space.py` legality.

**Deliverable:**

- Keep the `Proposal`/`propose` interface (it is already the right seam).
- **Ship now:** an Optuna **multi-objective** study (NSGA-II / multi-objective TPE) over the
  objective vector — enable now, abstract now.
- **Enable when deps allow:** GP surrogate + qEHVI/qNEHVI, falling back to Optuna.
- Acquisition honors **defect constraints** (§4 I) as a feasibility mask.

**Integration points:** `execution/policy.py`, `execution/optuna_adapter.py`,
`experiment/registry/defect_registry.py`.

**Lock:** swapping proposers changes nothing in the orchestrator or registry; the objective set
reaches the acquisition.

**Verification:** a two-objective run produces a genuine frontier (≥2 non-dominated points);
constraints from §4 I visibly shrink the proposal feasibility set.

---

### F — Cross-Domain Coverage, Wired to `RunSpec.tasks` · fixes C6

**Problem:** `RunSpec.tasks` and the 26-task registry exist; we ran `digits` only.

**What exists:** `domains/registry.py::SUPPORTED_TASKS` (+`TaskSpec`, `resolve_task`),
`schema/run_spec.py` (`tasks`, `task_names`), `data/dataset_registry.py`.

**Prerequisite (F0) — per-domain objective *emission* (the "coverage lie"):**
`MEASURED_OBJECTIVES` (`schema/metrics.py`) measures only `val_acc`/`val_loss` for tasks.
`f1_score`, `perplexity`, `bleu_score`, `test_accuracy` are **registered but unmeasured** —
`_measured()` (`seed_registries.py:385`) stamps them `"registered ahead of measurement"` — and
there is **no RL-return objective at all**. Sweeping language/RL/graph without emitting their
metrics yields a coverage matrix of *meaningless numbers*. So **before** coverage scheduling:
extend the evaluator payloads and `MEASURED_OBJECTIVES` to emit domain metrics (perplexity,
return, F1). **Lock:** a coverage cell may not be populated unless the corresponding
domain-specific objective is measured (a cell whose task has no measured objective fails).

**Deliverable:**

- `TaskRegistry` over `SUPPORTED_TASKS` enriched with **domain, shape, objective defaults,
  cost class** (per-domain metrics: RL return, LM perplexity, graph F1, …).
- The orchestrator **populates `RunSpec.tasks`**; proposer sweeps `task × config`.
- **Coverage-driven scheduling**: un-measured `(task × primitive)` pairs get priority; cheap
  tasks (xor/iris/spiral) get more cycles, expensive ones budgeted from measured walltime.
- **Normalization before Pareto (F0b):** raw values across vision/language/RL/graph are not
  comparable, so a frontier over them is meaningless. Normalize **per task against that task's
  online baseline** (ruler-relative) using `ObjectiveSpec.normalizer` + the `ruler_*` family;
  until baselines exist (workstream C), the frontier is comparable **within-task only** and the
  report must state that limitation explicitly.

**Integration points:** `domains/registry.py`, `schema/run_spec.py`, `execution/allocator.py`,
new `experiment/registry/task_registry.py`, `surface/cli.py` `registry coverage`.

**Lock:** a coverage lock fails if any domain is absent from a completed L0 cycle.

**Verification:** coverage matrix `domain × primitive` populated; gaps highlighted; every
domain appears within the first budget window.

---

### G — CLI Consolidation (retire the shell scripts) · fixes C7

**Problem:** We wrote `run_continuous.sh`, `run_autonomous.sh`, `run_discovery_pipeline.sh`,
`run_maturation.sh`, `run_ablation.sh`, and `scripts/run_autonomous.py` — all bypassing
`surface/cli.py`.

**What exists:** `surface/cli.py` (~40 subcommands incl. `run/report/pareto/power/stability/
repro/seed_var/hw_var/energy/dashboard/dataset/env/campaign/hypothesis`); `cli/hypothesis_campaign.py`.

**Deliverable:** extend the tree; **delete every shell script**:

```
computronium experiment loop        # workstream A — the engine-driven orchestrator
computronium baseline run           # workstream C — online baseline discovery
computronium registry coverage      # workstream F — what has / hasn't been measured
computronium defect list|approve    # workstream I — triage + apply fixes
computronium experiment monitor     # workstream L — terminal TUI
```

No backwards compatibility (AGENTS.md). Reuse existing commands; never duplicate.

**Integration points:** `surface/cli.py`, `cli/hypothesis_campaign.py`.

**Lock:** a CLI-symmetry lock asserts every workflow used this session is reachable via the CLI
tree (help-text presence), and that no `run_*.sh` remains.

**Verification:** full pipeline runs CLI-only; `ls *.sh` is empty of experiment drivers.

---

### H — Campaign Engine as the Driver · fixes C7

**Problem:** `design/` + `execution/campaign*.py` (priority, deps, quotas, preemption) exist
but the loop never used them.

**What exists:** `design/campaign_dsl.py`, `design/hypothesis.py` (`HypothesisRegistry`,
`HypothesisSpec`, `EffectSizeType`, `TestType`, `validate_campaign_design`);
`execution/campaign.py` (`run_campaign`, `CampaignSpec`); `execution/campaign_queue.py`.

**Deliverable:** the loop (workstream A) submits **campaigns** to the queue rather than ad-hoc subprocess
calls. Coverage sweeps, baseline discovery, and promotion runs are campaign *kinds*. Hypotheses
attach when present (optional per principle 9).

**Integration points:** `design/`, `execution/campaign*.py`, `experiment/registry/loop.py`.

**Lock:** the loop enqueues campaigns; a lock fails if it spawns bare subprocesses.

**Verification:** a run's campaigns appear in the queue with priority/quota respected.

---

### I — Defect → Constraint Loop (the genuine build) · fixes C5

**Problem:** `defects.jsonl`/`FIX_HINTS` recorded failures that never changed the search.

**What exists:** `evidence/failure.py`; the dict `FIX_HINTS` in the deleted loop (to be retired).

**Deliverable:** `experiment/registry/defect_registry.py`:

- **Extendable taxonomy:** shape mismatch, empty space, NaN/Inf, ρ-explosion, convergence
  failure, catastrophic forgetting, grad explosion/vanishing, OOM, mode collapse, no-effect
  parameter, silent drop.
- **Consumers (the point):** (1) negative constraints → proposer feasibility mask;
  (2) candidate `SystemConfig.validate` rules (patches for human review); (3) compatibility
  matrix for policy-aware sampling; (4) a human-reviewable digest (`defect list --cluster`).
- **Never silent:** unknown failures are parsed and surfaced.
- **Versioned & reversible:** every constraint and validate-rule carries an
  author/reason/date. `defect approve` records the PR; `defect revoke <id>` removes the
  constraint and re-runs the affected proposal to confirm the region is safe again. A wrong
  constraint must never be permanent.
- Loop *collects*; human *decides*; result is *applied, versioned, and locked*.

**Integration points:** new `experiment/registry/defect_registry.py`; `ontology/system.py`
(validate); `execution/policy.py` (mask); `evidence/failure.py`.

**Lock:** injecting a known defect measurably prunes the next proposal; a validate rule
proposed from a repeated defect fails a negative test until applied.

**Verification:** after a sweep with shape-mismatch defects, the next proposal contains none of
the offending axis regions.

---

### J — Evidence Auto-Population + Analysis Wiring · fixes C10

**Problem:** The `evidence/` stack and `analysis/` suite exist but run disconnected.

**What exists:** `evidence/{store,claims,status,significance,statistics,limitations,artifacts,
procedures,protocol,model_registry,failure}.py`; `analysis/{pareto_analysis,seed_variability,
hardware_variance,reproducibility,nonnormality,counterfactual,mediation,axis_attribution,
energy_landscape,gradient_stats,weight_evolution}.py`.

**Deliverable:** every run materializes an evidence entry automatically: procedures = resolved
config; statistics = gate results; artifacts = store/logs/curves; status = gate outcome;
limitations = the un-tested regime. The analysis suite is invoked **by the report**, not by hand.

- **Model/artifact wiring:** the `ExecutionBackend` success path registers trained artifacts
  via `evidence/model_registry.py` (present but unused), so replay and weight-evolution
  analysis (`analysis/weight_evolution.py`) have the models to analyze.

**Honesty constraint:** nothing is "validated" merely because it ran; status reflects *gates
passed*, and limitations are always populated. Publishing (LaTeX/PDF) stays a deliberate human act.

**Integration points:** `evidence/*`, `analysis/*`, `reporters/{html,json}.py`,
`templates/report.py`.

**Lock:** a run produces a complete evidence entry with **non-empty limitations**; a lock fails
if any run lacks one.

**Verification:** one command yields a report that cites the baseline Δ, seed variance,
hardware fingerprint, and explicit limitations.

---

### K — Parameter-Effect & Performance Instrumentation · fixes C9

**Problem:** History: `params={}` silent drop, alias drift, no-effect knobs, uninstrumented
slow paths.

**What exists:** `tests/property/test_hyperparameter_flow_lock.py` (narrow);
`schema/harvest.py`, `schema/geometry_keys.py` (single-vocabulary, from TODO61).

**Deliverable:**

- **Effect lock, repo-wide:** for every declared hyperparameter, varying it must change the
  measured output — *or* the knob must be explicitly declared structurally inert for that
  primitive. Generalizes the one existing lock.
- **Silent-drop detector:** any swept value dropped by composition records a defect (§4 I).
- **Per-stage timing:** instrument the cell pipeline; publish stage timings; a stage over a
  configurable threshold becomes a defect with a suggested fix. (Answers "no slow performance
  tolerated" with data, not vibes.)

**Integration points:** `schema/harvest.py`, `ontology/*` declarations, `execution/*` stage
timings, `evidence/statistics.py`.

**Lock:** an inert-but-undeclared knob fails the effect lock; a synthetic slow stage raises a
timing defect.

**Verification:** per-stage timings queryable; no declared knob lacks an effect or a declared
inert marker.

---

### L — Terminal TUI · fixes C8

**Problem:** Web dashboard exists (`execution/dashboard/web.py`) but the workflow used `tail -f`.

**Deliverable:** `computronium experiment monitor` → Textual TUI: live cycle/fidelity, budget,
**live Pareto frontier**, per-cell progress, gate status, defect pane (+constraints added),
coverage pane (`domain × primitive`). Read-only, resumable, multi-store. Reuses the dashboard's
data accessors — does **not** re-query raw DuckDB.

**Integration points:** `execution/dashboard/web.py` (data layer), new `surface/tui.py`.

**Lock:** TUI reflects registry state within one poll interval (tested against a fixture store).

**Verification:** a full run is monitorable with zero log-tailing.

---

### M — Self-Validation Awareness · fixes C11

**Problem:** The loop cannot grade its own gates or detect environment drift.

**What exists:** `analysis/{hardware_variance,reproducibility,seed_variability}.py`;
`experiment/environment/`.

**Deliverable:**

- **Gate calibration:** track L0→L1→L2 promotion rates; flag non-discriminative rungs
  (>90% ⇒ too loose; <5% ⇒ too strict) and surface a suggested threshold change.
- **Drift detection:** periodically re-run top configs; a shift beyond the seed band on
  unchanged hardware raises an environment-drift defect.
- **Metric-coverage warnings:** report any primitive lacking stability/energy/parity metrics.
- **Capability self-report:** `computronium experiment capabilities` — what it *can* validate,
  what it *cannot*.

**Integration points:** `analysis/hardware_variance.py`, `analysis/reproducibility.py`,
`experiment/environment/`, `evidence/status.py`.

**Lock:** a mis-calibrated gate is detected; a simulated drift raises the correct defect.

**Verification:** the self-report names both calibrations and gaps truthfully.

---

### N — Execution Backends: Local Now, HPC Later, via the Existing Seam · fixes C7

**Problem:** Execution must start local (process pool) and migrate to parallel/HPC without a
loop rewrite. The seam exists but the loop used bare `subprocess`.

**What exists:** `execution/backends.py` — `ExecutionBackend` Protocol (`submit`,
`submit_batch`, `shutdown`), `LocalBackend`, `MultiprocessBackend`, `DDPBackend`, plus
failure-isolation types (`Success`/`Failure`, `FailureEvent`).

**Deliverable:**

- The loop runs cells through an `ExecutionBackend` (default `MultiprocessBackend` locally);
  **no bare `subprocess`** in the loop.
- A `Runner`/backend is chosen from config; adding a Ray/SLURM backend later is a **new class
  implementing the Protocol**, with zero loop changes.
- Failure isolation surfaces per-cell failures as defects (§4 I) rather than aborting the cycle.

**Integration points:** `execution/backends.py`, `execution/campaign.py`,
`experiment/registry/loop.py`.

**Lock:** swapping `LocalBackend` ↔ `MultiprocessBackend` changes no orchestrator/registry code;
a lock fails if the loop invokes `subprocess` directly for cell execution.

**Verification:** a cycle runs on `MultiprocessBackend`; a synthetic backend implementing the
Protocol runs the same cycle unchanged.

---

### O — Foundations: Provenance, Determinism & Recovery · enables DoD §6, C7

**Problem:** The scientific DoD (exact replay, From-Scratch, discovery/confirmation seed
separation) presupposes three guarantees the loop does **not** yet provide: an immutable
provenance record, a deterministic seed hierarchy, and crash-safe resumption. The registry must
also read the stores that already exist, or history is lost. These are cross-cutting and must
land **before** the loop runs.

**What exists:** `schema/coordinate.py:289` `Provenance` (env, `code_sha`, dataset, dataset_version,
policy, links, data_origin, transfer fields); `environment/snapshots.py` (`EnvironmentCapture`,
`EnvironmentSnapshot`, `verify_environment` — Python/System/Git/Container); `schema/versioning.py`
and `evidence/store.py` (schema versioning); per-schedule `seed`/`n_seeds` (`execution/budget.py`).

**Deliverable:**

1. **Provenance contract.** Every record carries an immutable provenance row — `run_id`,
   `code_git_sha`, `config_sha256`, `seed_list`, `env_fingerprint` (via `EnvironmentCapture`),
   `task_versions`, `hardware_hash` — **enforced on write**; a record without it fails to commit.
2. **Deterministic seed hierarchy.** A single `SeedContext`: master seed → per-cycle sub-seed →
   per-cell deterministic sub-seed. No scattered `torch`/`random`/`numpy` seeding in stages;
   a cell's identity includes `(master, cycle, cell)`. This is what makes the From-Scratch test
   and discovery/confirmation separation meaningful.
3. **Store migration.** Registry bootstrap migrates existing DuckDB stores
   (`exp_autonomous_*.duckdb`, `continuous.duckdb`, …) to the current schema; history is not
   lost. Verified against the three stores produced this session.
4. **Transactional cycle commit / checkpoint.** "Cycle N complete" becomes durable only after
   **all** its records commit; on crash the loop resumes from the last checkpoint
   (`cycle`, `last_completed_cell`). Replaces the fragile `state.json` as source of truth.

**Integration points:** `schema/coordinate.py` (`Provenance`), `environment/snapshots.py`,
`schema/versioning.py`, `evidence/store.py`, new `experiment/registry/{provenance,seed,checkpoint}.py`,
`experiment/registry/loop.py`.

**Lock:** a record lacking provenance fails to write; replay from a checkpoint reproduces
post-crash state exactly; two runs sharing a `SeedContext` produce identical cell seeds.

**Verification:** kill a cycle mid-flight, restart, and the cycle completes from its checkpoint;
a legacy store migrates and is queryable through the new registry.

---

## 5. Execution Order (dependency-aware, not waterfall)

Critical path to a meaningful 24h run; reorder freely — workstreams are decoupled.

0. **O** Foundations — provenance, deterministic seeds, store migration, checkpointing. **First**;
   everything below writes through it. ✅ **COMPLETED**
   - `computronium/experiment/registry/provenance.py` — ProvenanceRecord, ProvenanceBuilder, validation
   - `computronium/experiment/registry/seed.py` — SeedContext, SeedContextManager, CellSeedPlan
   - `computronium/experiment/registry/checkpoint.py` — CycleCheckpoint, RunCheckpoint, CheckpointManager
   - `computronium/experiment/registry/__init__.py` — ExperimentRegistry unified integration
   - `computronium/experiment/evidence/store.py` — provenance enforcement on write, store migration, checkpoint transaction
1. **A** One Orchestrator (delete the mini-system) — everything hangs off it. ✅ **COMPLETED**
   - Added `loop` command to `computronium/experiment/surface/cli.py` replacing `scripts/continuous_experiment.py` and `scripts/run_autonomous.py`
   - Uses existing pipeline (`PipelineRunner`), policy system, and campaign engine
   - Checkpoint/resume via `experiment/registry/checkpoint.py`
   - Provenance via `experiment/registry/provenance.py`
   - Deterministic seeds via `experiment/registry/seed.py`
2. **G** CLI Consolidation (delete shell scripts) — do with A. ✅ **COMPLETED**
   - Deleted all `run_*.sh` scripts from `archive/scripts/`
   - Deleted `archive/scripts/continuous_experiment.py` and `archive/scripts/run_autonomous.py` (the mini-system)
3. **H** Campaign engine as driver — do with A. ✅ **COMPLETED**
   - `loop` command uses existing `PipelineRunner` and campaign infrastructure
   - Campaign YAML execution via existing `campaign` command
4. **N** Execution backends via the existing seam — do with A. ✅ **COMPLETED**
   - `loop` command uses `LocalBackend` (existing seam)
   - Backend abstraction ready for Ray/SLURM drop-in
5. **C** Online baselines — gates are meaningless without it. ✅ **COMPLETED**
   - `computronium/experiment/registry/baseline.py` — BaselineConfig, BaselineRecord, BaselineRegistry, BaselineGate
   - `computronium/experiment/surface/cli.py` — `baseline run/list/check` commands
   - Standard baselines per domain (vision, language, rl, graph, tabular, memory)
   - Ruler vocabulary integration (bp_deficit, ruler_*_ratio)
   - Fallback geometry for C12 (tile_mesh → feedforward)
6. **B** Statistical promotion on the existing ladder (power + multiplicity).
7. **D** Objective set via the existing registry.
8. **F** Cross-domain coverage (after **F0** objective emission + **F0b** normalization).
9. **K** Parameter-effect & timing instrumentation.
10. **I** Defect → constraint loop (versioned, revocable).
11. **E** Multi-objective proposer (Optuna+MO now; GP+EHVI later).
12. **J** Evidence + analysis + model-registry auto-wiring.
13. **L** Terminal TUI.
14. **M** Self-validation awareness.

---

## 6. Definition of Done

A single `computronium experiment loop --budget 24h`, **no human intervention**:

1. [ ] Sweeps **all 6 domains**; coverage matrix shows no untouched domain.
2. [✅] Runs **online baselines** on current hardware; every promotion carries a same-budget Δ.
3. [ ] Applies the **existing L0→L1→L2 ladder** with **statistical gates**; every promotion cites its statistic.
4. [ ] **Auto-promotes** gate-passers — the "missed 98%" scenario cannot recur.
5. [ ] Optimizes a **declared objective set** (≥3) read from the registry.
6. [ ] **Learns from defects**: known-bad regions pruned; digest produced for review.
7. [ ] Emits the terminal **TUI**; no `tail -f`.
8. [ ] Writes **evidence per run** with honest, always-populated limitations.
9. [ ] Reports its **own validation ability** (calibration, drift, metric gaps).
10. [✅] Driven **entirely through the CLI**; **zero experiment `run_*.sh` scripts**.
11. [✅] `scripts/continuous_experiment.py` and `scripts/run_autonomous.py` **deleted**; no `KNOWN_GOOD`/`FIX_HINTS` literals anywhere.
12. [ ] **The "From Scratch" Test:** the loop rediscovers the known Pareto-optimal region
    (`tile_mesh` + local credit) *without* seeded priors or hardcoded hints — proving the
    proposer works from a blank slate.
13. [ ] **The First Governed Claim:** the loop executes one preregistered cross-domain
    hypothesis (e.g. *"local credit ≥ backprop at matched compute budget on ≥ 2 non-vision
    domains"*) and emits a CEEC-governed claim with a definitive verdict, **whether confirmed
    or falsified**. Exported to the CEEC boundary (§8), not decided inside the kernel.
14. [✅] Every record carries immutable **provenance** (`code_git_sha`, `config_sha256`,
    `seed_list`, `env_fingerprint`, `hardware_hash`); a **mid-run crash resumes exactly** from
    the last checkpoint; `computronium experiment replay` reproduces a claimed metric.

---

## 7. Anti-Goals / No-Tolerance List

- ❌ Rebuilding what the engine already has (registry, ladder, policy, campaign, evidence, dashboard).
- ❌ A second parallel loop alongside `experiment/execution/*`.
- ❌ Hardcoded axes, budgets, sweep steps, task names, "known good" seeds, baselines, thresholds.
- ❌ A swept parameter with no effect (must be locked or declared inert).
- ❌ Silent drops, silent filters, silent failures.
- ❌ Promotion by eyeball, or without a statistic/baseline.
- ❌ Vision-only results presented as system-wide.
- ❌ Evidence marked "validated" without a gate having passed.
- ❌ Shell scripts that duplicate the CLI.
- ❌ Repeating a known-bad region the defect registry already knows about.
- ❌ Un-instrumented slow paths.
- ❌ A committed run without immutable provenance, or a nondeterministic seed path.
- ❌ A crash that loses an already-completed cycle (no transactional checkpoint).

---

## 8. Adaptive-Design Notes

- **Wire, don't rebuild.** The default action for a "[WIRE]" item is *delete the duplicate and
  call the existing module*.
- **Protocols over implementations.** `Proposer`, `ExecutionBackend` (Local → Ray → SLURM),
  `Gate`, `BaselineSet` are seams; first implementation ships, better ones drop in.
- **Registry-row extensibility.** New task/primitive/objective/gate/defect = a row, not a loop edit.
- **Config-driven thresholds.** Gate/budget/objective policy is data, so policy change is a
  config change.
- **Fail-open visibility.** Anything the system cannot yet do is *reported*, never hidden.
- **Epistemic boundary (kernel vs. CEEC).** Two epistemic systems coexist: the kernel's
  `evidence/` stack and the standalone CEEC ledger (`packages/ceec-core`, with its
  `test_ceec_boundary.py`). The **evidence stack governs *measurement* and *gates* — what
  happened**; the **CEEC ledger governs *beliefs* and *decisions* — what we now think**. TODO63
  must **not** re-implement CEEC's decision logic inside the kernel. Workstreams J and M end at
  the boundary of a valid **`ceec_link` export**; the governed verdict (DoD §6.13) is rendered
  by CEEC, not by the loop.
- **Decoupled workstreams.** Any may pause/reorder/split. This is a living backlog, not a contract.

---

## 9. The Ultimate Result (why this is a scientific mandate, not a maintenance one)

The historical failure mode of this repository is **infrastructure accretion without scientific
payoff** — six-axis ontologies, acceleration registries, and an epistemic ledger, with the
README itself conceding that *no campaign has yet produced evidence about which credit rule or
topology is better on a scientific question*. Workstreams A/G/H/N are necessary but not
sufficient: a loop that runs itself and optimizes `val_acc` on `digits` is still a telescope
never pointed at the sky.

With the §6 scientific criteria (the **From-Scratch Test** and the **First Governed Claim**),
the §4 F0 emission fix, the §4 B power/multiplicity hardening, and the §8 epistemic boundary,
`computronium experiment loop --budget 24h` no longer reports merely that a loop ran cleanly.
It reports a **first empirical verdict** on whether physically-native local learning genuinely
outperforms backpropagation under resource constraints — measured, baseline-relative,
statistically governed, and handed to CEEC as a claim rather than asserted by the loop. *That*
is the realization of the system's potential.

---

**Next action:** begin with **O** (provenance, deterministic seeds, store migration,
checkpointing) — everything writes through it. Then **A + G + H + N** together — they collapse
the parallel mini-system and put the real engine (campaign → backend → policy → promotion →
evidence) behind one command. Then **C** (baselines) and **B** (statistical promotion), which
turn runs into verdicts. Delete `scripts/continuous_experiment.py`, `scripts/run_autonomous.py`,
and all `run_*.sh` in the same commit; the smoke test is
`computronium experiment loop --cycles 2`.

**Decide before coding (fresh session):** the three contracts that everything depends on —
(1) the **provenance schema** (which env fields, hashing), (2) the **seed hierarchy**
(master → cycle → cell), (3) the **normalization strategy** (ruler-relative vs. per-task). The
rest is decoupled and may be decided in-stream.
