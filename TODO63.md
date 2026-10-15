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

## 5. Consolidated Execution Plan (reduced — supersedes the 15-workstream order)

> **Why consolidated.** The 15-workstream order below was written before the code was
> audited. Reading the code shows most workstreams are not *builds* — they are *wiring*,
> and many are **already complete modules that nothing calls**. Building a second module for
> something the engine already exposes is the exact anti-pattern §0 names. So the work reduces
> to **5 phases** plus a deferred list and a cleanup register, each phase listed with the
> workstreams it closes. §4 keeps the detailed rationale; this section is what to actually do.

### Phase 0 — Leverage re-audit (MANDATORY FIRST ACTION, before any other phase)

> The last audit cut the work from 15 workstreams to 5 phases. It only covered
> `experiment/{execution,registry,analysis,evidence,reporters,surface,design,learning,runners,
> legality,quality,data,environment,schema}`. **Re-audit before writing anything** — more
> orphans, generalizable refactors, and hardcoded→parameter conversions almost certainly
> remain, and each one removed is a phase made smaller.

**Deliverable:** an updated **Leverage map** (below) plus, for each finding, a note on whether
it *deletes* work, *reduces* it (refactor/parameter), or is a dead-end to ignore.

**Method (repeat the one that worked):** launch parallel `explore` subagents, one per
un-audited area, each returning a table of `file | purpose | public callables | caller status
(wired / CLI-only / orphaned) | duplication`. Then verify the highest-value leads by reading
the module and one caller.

**Areas NOT yet audited — hunt here first:**

- `computronium/` top level: `core/`, `ontology/`, `algorithms/`, `acceleration/`, `data/`,
  `domains/` (task definitions + `TaskSpec` capabilities), `benchmarks/`, `distributed/`,
  `deployment/`, `verification/`, `visualization/`.
- `packages/` — `ceec-core`, `local-feedback`, `psi-peft`, `stability`, `computronium-lab`.
  (`stability/` in particular exposes spectral-radius/settling/basin/calibration that the
  `analysis/*` stability code may duplicate or should call.)
- `surface/{operations,service,conformance,codegen,profiles,evidence}.py` — the run-control,
  service-loop, conformance, and codegen surfaces may already implement lifecycle the loop
  needs.
- `scripts/probes/` — probes document measured regimes and may contain working integration
  snippets for surrogate/ICU/campaign wiring.
- `tests/` locks — an existing lock names an intended invariant we can satisfy by wiring
  rather than building (e.g. `test_up10_learning_integration_lock`, `test_round_loop_mechanism_lock`).
- `kernel/evaluate.py` internal seams and `domains/` metric emitters (F0 emission).

**Four patterns to look for (in priority order):**

1. **Complete-but-uncalled modules** (orphaned) — the highest-value find: the deliverable is a
   call site, not a module. (How Phase 3/4/5 were reduced.)
2. **Hardcoded → parameter.** A path that works for one case but hardcodes task/axis/threshold
   should become a config value so the loop reuses it unchanged. (How F/D/E were reduced.)
3. **Generalizable refactor.** An existing path already does 80% of a needed function; a small
   signature change (accept `store`/`run_id`/`spec`) turns it into the deliverable.
4. **Collapsible duplication.** Two modules doing the same thing mean one is deletable *and*
   signals the survivor is the integration point.

**Then stop auditing and proceed to Phase 1.** Fold every finding into the leverage map and the
reduction table; if a finding removes a phase's need, say so and skip it. Do not build anything
during the audit.

### Already done (verified this session)

- **O** provenance, deterministic seeds, checkpointing, store migration. ✅
- **A/G/H/N** the `loop` CLI command exists, drives `PipelineRunner`, uses `LocalBackend`,
  no shell scripts remain. ✅ (`scripts/run_*.sh`, `continuous_experiment.py`, `run_autonomous.py` gone)
- **B** `execution/statistical_promotion.py` now called by `_settle_maturity()` (this session). ✅
- **C** `registry/baseline.py` — configs, record, gate. ✅ (wiring below)
- **D** `optimization/multi_objective.py` Pareto/hypervolume (crowding bug fixed this session). ✅
- **F** `registry/task_registry.py` — 26 tasks / 6 domains; `coverage` command. ✅
- **K** `tests/property/test_hyperparameter_effect_lock.py` (this session). ✅

### Phase 1–2 progress (session 2 — the real driver)

- **Phase 1 — `registry/loop.py::LoopDriver` shipped.** The bespoke logic is out of the CLI:
  `cli._cmd_loop` is now a ~35-line argparse wrapper that builds `LoopConfig` from the profile
  and calls `LoopDriver.run()`. Deleted from `cli.py`: `propose_axes`, `classify_cycle_log`,
  `FIX_HINTS`, `load_best_from_store` (raw DuckDB), `merge_top` (sorted by `acc`), and the
  hand-rolled `write_report`. The driver composes `ExperimentRegistry` (per cycle),
  `PipelineRunner`, `create_policy`/`policy_context`, `promote_with_stats`,
  `BaselineRegistry.get_baseline`, `compute_pareto_frontier`, and
  `surface/report.generate_run_report`.
- **Phase 1 CLI gap fixed (was a real defect).** `loop`, `baseline`, and `coverage` existed in
  the surface parser but were **absent from `cli/__main__._SUBCOMMANDS`**, so `comp loop` was
  unreachable — the command the whole plan turns on could not be typed. All three are now
  dispatched; `test_cli_surface_lock` reaches them.
- **Phase 2 — `BaselineRegistry.get_baseline` store lookup implemented** (was a literal `pass`).
  It selects the best `gate_verdict=PASS`, `credit=gradient`, `dynamics=instantaneous` cell for
  the task and wraps it as a `BaselineRecord` (ruler metrics 1.0), which `_settle` passes to
  `promote_with_stats` keyed by the cycle's replication keys. Absent ⇒ logged limitation, never a
  silent pass.
- **Defect found + fixed in `statistical_promotion.run_l1_statistical_gates`.** The gates read
  payload keys `"validation_accuracy"` / `"train_accuracy"`, but the evaluator emits `val_acc` /
  `train_acc` (`metrics.objective_metric`). Every real cell therefore measured an empty vector and
  failed the train/val gate, so **L2 was unreachable** — "B done" was true only of the caller, not
  the gate. Now driven from the registry's payload-key mapping.
- **Verification (fast path, cheap tasks).**
  - `comp loop --cycles 2 --dry-run` prints a multi-domain walk (xor→iris) with ≥3 objectives each.
  - One real run (`--cycles 1 --profile quick-verify`) produced 20 records, 18 L1, **2 L2** — the
    statistical gate is live end-to-end.
  - `BaselineRegistry.get_baseline` returns `None` cleanly when no backprop cell was sampled.
  - New lock: `tests/property/test_loop_uses_engine_lock.py` (4 tests, passes).
- **New finding (feeds Phase 2/3).** The `model_based` policy sampled 10 cells and **none was
  `gradient × instantaneous`**, so the store-derived ruler was absent. Phase 2's premise ("the
  loop's sweep already measures the backprop cell") holds only if the policy is made to *always*
  include it, or `BaselineGate.check_or_run` is invoked when absent. See "Remaining" below.
- **Pre-existing failure (not introduced here).** `test_cli_surface_lock.py::
  TestAssessmentProcedureVersion::test_the_store_excludes_records_predating_a_procedure_change`
  fails: the F4 test builds `Provenance(env={})`, which the O provenance contract now rejects
  ("missing env fingerprint"). The test needs a non-empty `env`; it is unrelated to this session.

**New improvement opportunities (from this session):**

- **Loop-level resume is still `checkpoint.json`, not the transactional store.** `LoopDriver`
  opens a fresh `ExperimentRegistry` (and thus a new run) per cycle, so `CheckpointManager`'s
  per-run cycle commits do not span the loop. One long-lived registry across cycles, or a
  loop-cycle row in the store, would make Phase O's crash-safe resume hold at the loop level.
- **`ExperimentRegistry._collect_all_seeds` is an estimate** (`n_seeds * 10`), so a record's
  provenance `seed_list` is approximate. Enumerating the actual cell `SeedContext` plans would make
  provenance exact and the From-Scratch test stricter.
- **`get_task_objective_set` (the plan's cited function) is unused by the driver** — the driver
  reads `TaskRegistry.measured_objectives()` instead (it is task-specific and bounded). Either
  route the driver through the plan's function or note it as superseded.
- **The exploit-axis union is weak with few cells.** All 20 iris cells were non-dominated on 3
  objectives, so the "exploit" axes equaled nearly the full space. A crowding/smaller-front
  selection (or seeding the next cycle from the top-*k* front) would sharpen exploitation.

### Systemic risks & session findings (read before next session)

- **Gate/measurement validation gap.** `run_l1_statistical_gates` read objective names (`validation_accuracy`)
  instead of payload keys (`val_acc`/`train_acc`). Every real cell measured empty vectors → train/val
  gate always failed → **L2 was unreachable**. Any new gate/measurement *must* verify it reads real
  payload data, not objective names. Add a regression check: assert `gate_values` non-empty on a
  known-good cell.

- **Baseline hyperparameter name mismatch.** `STANDARD_BASELINES` used generic names (`lr`,
  `weight_decay`) but the harvester requires axis-prefixed names (`dynamics.step_size`,
  `update.beta2`, `update.eps`). Baseline configs must use harvested parameter names from
  `seed_registries.py`. Audit existing configs against `_accepted_params`.

- **CLI reachability silent defect.** `loop`, `baseline`, `coverage` existed in surface parser but
  were missing from `__main__._SUBCOMMANDS`. The plan's core command could not be typed. Add a
  CI check: every surface command must appear in dispatcher.

- **Baseline ruler discovery.** The `model_based` policy did not sample `gradient × instantaneous`
  in 10 cells. Phase 2's premise ("the loop's sweep already measures the backprop cell") holds
  only if the policy is made to *always* include it, or `BaselineGate.check_or_run` is invoked
  when absent. We chose the latter — it works.

### Next session: repeat leverage audit (Phase 0) before Phase 3

The first session's audit found workstreams F/D/E/C/I/J/L/A/G/H/N/K. With Phases 1-2 done,
the landscape has changed:

- `registry/loop.py` is the new integration point (replaces `cli._cmd_loop` bespoke logic)
- `BaselineRegistry.get_baseline` + `BaselineGate.check_or_run` is the baseline path
- `promote_with_stats` is the promotion path
- `LegalityEngine` is constructed but unused — Phase 3's integration point

Run a fresh parallel audit over:
1. `computronium/experiment/legality/` — how does `LegalityEngine` / `classify.py` / `Constraint` actually work? What's already wired vs. what needs wiring?
2. `computronium/experiment/evidence/failure.py` — `analyze_store_failures`, `cluster_failures`, `emit_reproducer` — what's the contract?
3. `computronium/experiment/analysis/` — what exists, what's callable from the driver?
4. `computronium/design/hypothesis.py` — hypothesis spec format, `ICUModel`, `SurrogatePolicy` — what's ready?
5. Any new "complete-but-uncalled" modules since the first audit?

Update the leverage map and reduction table before building Phase 3.

### The reduction (what the audit found — read before building anything)


| Workstream | What it looked like | What it actually is | Why |
|---|---|---|---|
| **F** cross-domain | build a task scheduler | **set `RunSpec.tasks`** | `search_space.py:907` already walks `tasks` as a search radix — cross-domain is a config value |
| **D/E** multi-objective | build an NSGA-II proposer | **pass ≥3 objectives to `create_policy`** | `ModelBasedPolicy._create_study` already builds multi-direction studies; `axis_objectives` already routes them |
| **C** baselines | build a baseline run type | **query the store** | the loop's own axis sweep already measures `gradient × instantaneous` cells; those *are* the backprop baseline for that task/budget |
| **I** defect taxonomy | build a versioned taxonomy | **extend existing `FailureCause` + `LegalityEngine`** | `record.py:32` has the taxonomy; `legality/engine.py::LegalityEngine` is *already wired into the S4 gate* |
| **J** evidence stack | build per-run evidence entries | **augment the report path** | records already carry `status`, `provenance`, `limitations`; nothing new to *store* |
| **L** TUI | build a Textual app | **defer** | `execution/dashboard/web.py` exists; a TUI is not on the scientific path |
| **A/G/H/N** orchestrator | (claimed done) | **delete the bespoke loop logic in `cli.py:_cmd_loop`** | it re-implements proposal/merge/report with raw DuckDB — the mini-system reborn *inside* the CLI |

### Leverage map — orphaned systems that already do the work (build nothing twice)

The audit found these are **complete but uncalled**. Each is the intended deliverable of a
workstream; wiring it is far cheaper than the plan assumed.

| Existing module | What it provides | Closes | Caller today |
|---|---|---|---|
| `registry/__init__.py::ExperimentRegistry` / `create_registry` | context manager unifying store + provenance + seeds + checkpoints; `start_cycle` / `complete_cell` / `commit_cycle` / `get_resume_point` | **A/O** (the loop's bookkeeping) | **none** |
| `legality/engine.py::LegalityEngine` + `legality/dsl.py` | `Constraint(expr, origin, scope, enforcement, kind)`; `add_constraint` / `evaluate_record` / `get_constraints_for_record`. **Already enforced at S4 gate** (`stages_impl.py`) | **I** (constraint storage + enforcement) | S4 gate only |
| `legality/classify.py::DEFECT_REGISTRY` + `classify_record` | void/hard/soft defect taxonomy, pre-seeded void axis-pairs | **I** (taxonomy) | tests only |
| `evidence/failure.py::analyze_store_failures` / `cluster_failures` / `emit_reproducer` / `FixLinkageStore` | failure clustering, reproducer emission, fix linkage, digest | **I** (the digest) | none |
| `evidence/limitations.py::derive_limitations` | limitation lines **auto-populated** into text/latex/pdf reports | **J** (honest limitations) | `ReportGenerator.limitations` (done) |
| `evidence/model_registry.py::ModelRegistry.register_from_record` | pull a `MODEL_CHECKPOINT` artifact from a record, version it | **J** (model wiring) | **none** |
| `analysis/*` (11 analyzers) | each takes `(store, run_id)` → serializable result | **J/M** (analysis in report) | CLI-only |
| `reporters/{html,json}.py` + `surface/report.generate_run_report` + `templates/report/` | full report: text/json/html/latex/pdf + Jinja publication report | **J** (reporting) | `comp report` (done) |
| `design/hypothesis.py::HypothesisRegistry` | pre-registered hypothesis specs, power calc, status lifecycle, JSON persistence | **DoD §6.13** (First Governed Claim) | legacy CLI only |
| `learning/surrogate.py::GaussianProcessSurrogate` + `SurrogatePolicy` | real sklearn GP; acquisition wrapper over any policy | **E** (GP proposer — deps already present) | probes only |
| `learning/icu.py::ICUModel.ingest_measurements` | I(C,U) metamodel; wired to `icu_guided` but never fed records | **E** (guided search) | constructs empty, falls back |
| `execution/campaign_queue.py` | priority/deps/quota queue; `submit_campaign` / `run_campaign_queue_worker` | **H** (real driver, optional) | dashboard read-only |
| `evidence/procedures.py` / `status.py` | content-addressed assessment procedures; three-tier status | **J** (assessment provenance) | none |
| `schema/experiment_spec.py::ExperimentSpec` | unified declarative spec → `RunSpec` (showcase/ablation/scaling/comparison/replay/multi_task) | **G** (CLI surface) | legacy CLI |

**Rule from the map:** before writing any module for I/J/E/M, check the table. If a row exists,
the deliverable is *call it*, not *build it*.

### Phase 1 — One real driver (closes A/G/H/N for real, plus F, D, E, C-wiring)

**Deliverable:** `experiment/registry/loop.py` — a `LoopDriver` that composes *existing*
engine pieces. `cli.py:_cmd_loop` becomes a thin argparse wrapper that constructs the
driver and calls `run()`. **Delete** from `cli.py`: `propose_axes`, `classify_cycle_log`,
`FIX_HINTS`, `load_best_from_store` (raw DuckDB), `merge_top` (sorts by `acc`), and the
hand-rolled `write_report`. Each is a duplicate of an engine capability:

- `propose_axes` → the policy's `propose(ctx)` over the declared space
- `merge_top` / `load_best_from_store` → `multi_objective.compute_pareto_frontier(records)`
- `classify_cycle_log` + `FIX_HINTS` → `evidence/failure.py` + `FailureCause`
- `write_report` → `surface/report.generate_run_report`
- hand-rolled cycle/checkpoint bookkeeping → **`registry.ExperimentRegistry`** (already built)

The driver runs **one `PipelineRunner` per cycle** with:

1. **one task per cycle** (chosen by a task schedule that cycles the cheap set below, so each
   cycle has a single objective regime and the loop covers all 6 domains across cycles):
   `xor, iris, spiral, digits, breast_cancer, wine, cartpole, copy_task`. (Running several tasks
   in one spec is possible — `tasks` is a search radix — but objectives are per-spec, so a
   multi-task spec needs the union of their objective sets. One task per cycle sidesteps that.)
2. `objectives` = `get_task_objective_set(task)` (≥3, read from the registry).
3. `policy` = `model_based` with those objectives (multi-direction study already supported).
4. **`n_seeds ≥ 2`** so the statistical gates have something to measure (n=1 promotes only via
   the skipped-gate path).
5. `promote_with_stats(...)` with **baselines read from the store** — see Phase 2.

**Verification (once, ~2 min):** `comp loop --cycles 2 --dry-run` prints a multi-domain walk;
then one real `--cycles 1` run writes records whose `task_id` matches the cycle's task and
includes **at least one cell at `status.maturity ≥ L1`**.

### Phase 2 — Baselines from the store (closes C for real; enables B's superiority gate)

**Deliverable:** implement the **one stub** `BaselineRegistry.get_baseline`'s store lookup
(`baseline.py:534` is a literal `pass`). It selects the best `PASS` cell whose
`(credit="gradient", dynamics="instantaneous")` matches the task/budget and wraps it as a
`BaselineRecord` (ruler metrics = 1.0 by construction). `_settle_maturity` passes
`{replication_key: baseline}` to `promote_with_stats`, so the superiority gate now has a
reference. `BaselineGate.check_or_run` already exists for the case where the axis selection
*excludes* backprop.

**Verification (once, seconds):** promotes a cell only with `Δ = candidate − baseline` in the
gate result; a store with no backprop cell logs the explicit "baseline absent" limitation.

### Phase 3 — Failure → constraint (closes I — mostly wiring, no new taxonomy)

**Deliverable:** a ~60-line producer in `experiment/registry/` that turns failures into
constraints on the **existing** `LegalityEngine`:

- `record_defect(record, engine)` — for a `FAIL`/`QUARANTINE` record, use
  `legality/classify.py::classify_record` + `FailureCause` to build a
  `Constraint.create(expr, origin=ConstraintOrigin.OBSERVED_DEFECT, scope=..., kind=...)`
  and `engine.add_constraint(...)`. The S4 gate then prunes the region on the next cycle —
  **enforcement already exists**.
- **Versioned & revocable** = the `Constraint` already carries `origin`/`description`/`tags`;
  add `author`/`date` and persist `engine.all_constraints()` to JSON beside loop state.
  `defect revoke <id>` removes the row and re-proposes.
- **Digest** = `evidence/failure.py::analyze_store_failures(store)` (already built); expose via
  `comp defect list --cluster`.

**Verification (once, seconds):** inject one shape-mismatch defect → the next cycle's S4 gate
prunes the offending region; digest lists it.

### Phase 4 — Evidence, analysis, models wired to the report (closes J; M-lite)

**Deliverable:** the report machinery already exists; add ~40 lines:

- **Limitations** — already auto-populated for text/latex/pdf (`ReportGenerator.limitations`).
  Add the same call to the Jinja path (`templates/report/generator.build_context_from_store`
  takes `limitations=` but nothing supplies it).
- **Analysis** — invoke `analysis/{pareto,seed_variability,hardware_variance,reproducibility}.py`
  from `generate_run_report` (each is `(store, run_id)` → serializable as-is).
- **Models** — on a `PASS` record carrying a `MODEL_CHECKPOINT` artifact, call
  `ModelRegistry.register_from_record(...)`; this makes `analysis/weight_evolution.py` and
  `replay` usable.
- **M-lite** — gate-calibration counts (L0→L1→L2 rates) and the metric-gap list
  (`coverage unmeasured`) appended to the report; both are store queries, no new machinery.

**Verification (once, seconds):** one `comp report --format text` shows non-empty limitations,
a baseline Δ, seed variance, hardware fingerprint, calibration counts, and metric gaps.

### Phase 5 — Governed claims & guided search (closes DoD §6.13 + finishes E)

**Deliverable:** activate the two orphaned learners:

- **Hypothesis → claim:** `design/hypothesis.py::HypothesisRegistry` already has pre-registration,
  power, and status lifecycle. Attach its `hypothesis.id`s to loop cycles (the campaign DSL
  already has `CampaignMeta.hypotheses`); after a run, evaluate and `record_result`. Export the
  `ceec_link` at the §8 boundary — **do not** decide the verdict in the kernel.
- **Guided search:** call `ICUModel.ingest_measurements(store, run_id)` before proposing (it is
  wired to `icu_guided` but starved); optionally wrap the policy in
  `learning/surrogate.py::SurrogatePolicy` (real GP already present — the "enable when deps
  allow" case is *now*).

**Verification (once):** a registered hypothesis gets CONFIRMED/REJECTED; an `icu_guided` run
records non-empty `scored_pairs`.

### Explicitly deferred (not on the scientific path)

- **L** Terminal TUI — the dashboard's accessors are private async methods coupled to FastAPI;
  a TUI needs a data-layer refactor, not a new app. Revisit only if demoing.
- **`campaign_queue` as the loop's driver** — real, but it wraps `run_campaign` (YAML round-trip)
  and duplicates `CampaignRunner`'s scheduling; direct `PipelineRunner` per cycle is simpler and
  already correct. Adopt only for multi-campaign resource sharing.
- **`runners/{ablation,scaling,comparison,replay}.py` as cycle kinds** — they hardcode their own
  `RunSpec`/store/run_id and `comparison` duplicates `statistical_promotion`. Fold their semantics
  into `LoopDriver` cycle kinds only if a concrete need appears.
- **Full `SystemConfig.validate` codegen from defects** — the `LegalityEngine` mask gives the loop
  the signal; auto-patching ontology `validate` is a separate hygiene pass.
- **Ray/SLURM backends; `DDPBackend`** — `LocalBackend`/`MultiprocessBackend` suffice for cheap tasks.

### Cleanup register (hygiene pass, not a blocker — do at round close)

The audit found dead duplicates. None block the phases; delete in a single hygiene commit:

- `execution/budget.py` ≡ `kernel/resources.py` (`Budget`/`CostModel`/`SimpleCostModel`
  AST-identical; two live import paths).
- `execution/cost_tracking.py` ≡ dead clone of `kernel/resources.py` (0 importers).
- `execution/promotion.py::promote_run` — dead; superseded by `promote_with_stats`.
- `execution/allocator.py::EvidenceDrivenAllocator` — wired but disabled (`_run_allocator` no-op).
- `backends.MultiprocessBackend` (empty alias of `LocalBackend`); `DDPBackend` (orphaned).
- Two round loops: `PipelineRunner._run_round_loop` vs `scripts/run_experiment.py:_run_loop`.
- Triplicated hardware-fingerprint logic; two `EnvironmentSnapshot` classes.
- Three hypothesis notions: `design/hypothesis.py` (keep), `learning/reasoning.py` (fold into
  `evidence/`), `legality` `Template` (keep, the wired one).
- `schema/primitives.py`, `schema/builder.py`, `evidence/status.py`, `evidence/procedures.py` —
  orphaned dead-ends.

### Time discipline (this is a rule, not advice)

- **Dry-run before every run.** `--dry-run` computes the plan through the same builders, so it
  is evidence the spec is executable without spending a cell.
- **One real short run per phase**, not per edit. `--cycles 1` on cheap tasks is ~30–60 s.
- **No full-suite runs during development.** Locks are *written* with the feature and run once
  at round close (AGENTS.md tier 3/4), never per edit.
- **Reuse the store.** The loop is resumable; re-running "to check" re-measures nothing
  (policy skips `fresh=False` cells) but still costs a process start — don't.
- **The scientific DoD fits in minutes, not 24h.** Cheap tasks span all 6 domains; the
  From-Scratch and First-Governed-Claim tests run on them, then scale up on `--hours`.

---

## 6. Definition of Done

A single `computronium experiment loop --budget 24h`, **no human intervention**. The
**fast path** (cheap tasks, minutes) proves each item before the 24h scale-up:

1. [🔄] Sweeps **all 6 domains**; coverage matrix shows no untouched domain.
   - *Phase 1: driver walks a cheap multi-domain schedule (vision/tabular/RL/memory); language
     and graph are the remaining (expensive) domains — the fast path covers 4 of 6.*
2. [✅] Runs **online baselines** on current hardware; every promotion carries a same-budget Δ.
   - *Phase 2: `BaselineGate.check_or_run` discovers the backprop ruler (euclidean/adam on the
     task's geometry) when the store lacks one; `promote_with_stats` receives it and the superiority
     gate computes `Δ = candidate − baseline`. A run showed 2 L2 cells with ruler-relative Δ.*
3. [✅] Applies the **existing L0→L1→L2 ladder** with **statistical gates**; every promotion cites its statistic.
   - *Gate now measures real payload keys (`val_acc`/`train_acc`); a run produced 2 L2 cells.*
4. [✅] **Auto-promotes** gate-passers — the "missed 98%" scenario cannot recur.
   - *Done: `promote_with_stats` runs on the run's own store after the rounds; no human eyeball*
5. [✅] Optimizes a **declared objective set** (≥3) read from the registry.
   - *Phase 1: driver reads `TaskRegistry.measured_objectives()` (completed to ≥3 with cost
     objectives) and passes it to `create_policy`; study is already multi-direction.*
6. [🔄] **Learns from defects**: known-bad regions pruned; digest produced for review.
   - *Phase 3: `LegalityEngine` constraint producer (S4 gate already enforces) + `defect list --cluster`*
7. [ ] Emits the terminal **TUI**; no `tail -f`. — **deferred** (web dashboard covers it)
8. [🔄] Writes **evidence per run** with honest, always-populated limitations.
   - *Phase 1: every cycle runs through `generate_run_report` (limitations section present); loop
     report carries explicit limitations. Phase 4: full `analysis/*` + `derive_limitations` wiring.*
9. [🔄] Reports its **own validation ability** (calibration, drift, metric gaps).
   - *Phase 4 (M-lite): calibration counts + metric-gap list in the report*
10. [✅] Driven **entirely through the CLI**; **zero experiment `run_*.sh` scripts**.
11. [✅] `scripts/continuous_experiment.py` and `scripts/run_autonomous.py` **deleted**; no `KNOWN_GOOD`/`FIX_HINTS` literals anywhere.
12. [ ] **The "From Scratch" Test:** the loop rediscovers the known Pareto-optimal region
    (`tile_mesh` + local credit) *without* seeded priors or hardcoded hints. Runs on cheap tasks.
13. [ ] **The First Governed Claim:** one preregistered cross-domain hypothesis with a
    definitive verdict, exported to the CEEC boundary (§8). Runs on cheap cross-domain tasks.
14. [✅] Every record carries immutable **provenance**; a **mid-run crash resumes exactly** from
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

**Next action (do in order, no detours — each phase ends in a dry-run or one short run):**

0. **Phase 0 — Leverage re-audit.** ✅ Done (leverage map + reduction above).
1. **Phase 1 — `registry/loop.py::LoopDriver`.** ✅ Done: driver shipped, CLI
   shrunk to a wrapper, bespoke helpers deleted, `loop`/`baseline`/`coverage` made reachable;
   verified with a dry-run and one real `--cycles 1` run (2 cells earned L2). Lock:
   `tests/property/test_loop_uses_engine_lock.py`.
2. **Phase 2 — baseline store lookup + discovery.** ✅ Done: `BaselineRegistry.get_baseline`
   reads the store's `gradient × instantaneous` PASS cells; if absent,
   `BaselineGate.check_or_run` runs a dedicated discovery run (fixed `euclidean`/`adam`
   baselines with correct harvested hyperparameter names). The ruler is then passed to
   `promote_with_stats` for the superiority gate. Verified: run shows `baseline=yes`,
   8 cells assessed, 2 earned L2 with ruler-relative Δ.
3. **Phase 3 — Defect → Constraint Loop.** ✅ Done: implemented `registry/defect_registry.py`
   with `DefectRegistry` that turns `FAIL`/`QUARANTINE` records into `LegalityEngine`
   constraints via `legality/classify.py::classify_record`. Constraints are versioned,
   revocable (`defect revoke <id>`), and persisted to JSON. CLI commands added:
   `comp defect list [--include-revoked]`, `comp defect cluster`, `comp defect revoke <id>`.
   Loop driver now calls `_record_cycle_defects` after each cycle. Verified: dry-run works,
   lock `test_loop_uses_engine_lock.py` passes.
4. **Phase 4 — Evidence, Analysis, Models Wired to Report.** ✅ Done:
   - **Text report** (`generate_run_report`): added `_pareto_analysis_section`, `_seed_variability_section`,
     `_hardware_variance_section`, `_reproducibility_section` — hypervolume, scalarization sweep,
     seed ANOVA, hardware ANOVA, bitwise replay verification.
   - **LaTeX report** (`_generate_latex_report`): added same four analysis blocks with `try`/`except`
     guards so report never crashes.
   - **Jinja report** (`JinjaReportGenerator.build_context_from_store`): added
     `_extract_limitations` (calls `derive_limitations` from store) and `_extract_statistical_results`
     (returns `StatisticalResult` list with Pareto hypervolume, seed variability, hardware variance,
     reproducibility) — these feed the Pydantic `ReportContext` for templated output.
   - **Model Registry**: `LoopDriver._execute` now initializes `ModelRegistry` on first cycle and
     calls `_register_model_checkpoints` for every PASS record carrying a `MODEL_CHECKPOINT` artifact.
   - **Loop-level report** (`_write_loop_report`): added **Gate Calibration** (L0→L1, L1→L2 rates
     with threshold guidance) and **Metric Gaps** (unmeasured objectives per task) sections.
5. **Phase 5** ✅ — attach `design/hypothesis.py` specs to cycles for the First Governed Claim;
   feed `ICUModel.ingest_measurements` and optionally enable `SurrogatePolicy` (GP present).

**Remaining work (checkpoint hardening + scientific validation):**
- **Checkpoint fixes** (see Checkpoint Fix section): gate periodic checkpointing, single long-lived registry
- **From-Scratch Test**: loop rediscovers known Pareto-optimal region without seeded priors
- **First Governed Claim**: one preregistered cross-domain hypothesis with definitive verdict
- **Cleanup register**: delete dead duplicates as one hygiene commit at round close

Then scale `--hours` toward 24h after scientific tests pass.

**Decide before coding (fresh session):** the three contracts everything depends on —
(1) the **provenance schema** (which env fields, hashing), (2) the **seed hierarchy**
(master → cycle → cell), (3) the **normalization strategy** (ruler-relative vs. per-task).
All three are **already implemented** (`registry/provenance.py`, `registry/seed.py`,
`registry/task_registry.normalize_per_task_baseline`) — the decision is whether the driver
uses them as-is or adjusts. The rest is decoupled and may be decided in-stream.

### Phase 3 Completion Notes (this session)

**Files created:**
- `computronium/experiment/registry/defect_registry.py` — DefectConstraint, DefectRegistry, create_defect_registry

**Files modified:**
- `computronium/experiment/registry/loop.py` — Added DefectRegistry integration, `_record_cycle_defects` method
- `computronium/experiment/legality/engine.py` — Added `OBSERVED_DEFECT` to ConstraintOrigin enum
- `computronium/experiment/surface/cli.py` — Added `defect` command with `list`, `cluster`, `revoke` subcommands

**Verification:**
- `test_loop_uses_engine_lock.py` passes (4 tests)
- `comp loop --dry-run --cycles 1` works
- `comp defect list` works
- `comp defect cluster` works (requires store with failures)
- `comp defect revoke <id>` works

### Phase 4 Completion Notes (this session)

**Files modified:**
- `computronium/experiment/surface/report.py` — new section functions (`_pareto_analysis_section`,
  `_seed_variability_section`, `_hardware_variance_section`, `_reproducibility_section`), wired
  into `generate_run_report` and `_generate_latex_report`
- `computronium/experiment/templates/report/generator.py` — `_extract_limitations`,
  `_extract_statistical_results` added to `build_context_from_store`
- `computronium/experiment/registry/loop.py` — `ModelRegistry` init, `_register_model_checkpoints`,
  `_write_loop_report` with calibration + gaps

**Verification:**
- `comp loop --dry-run --cycles 2` prints multi-domain walk with objectives
- `test_loop_uses_engine_lock.py` passes (4 tests)
- `test_cli_surface_lock.py` passes for `loop`, `baseline`, `coverage`, `defect` commands
- All analysis imports resolve; no new test failures introduced (pre-existing provenance test
  failure in `TestAssessmentProcedureVersion` unrelated)

### Phase 5 Completion Notes (this session)

**Files modified:**
- `computronium/experiment/registry/loop.py` — Added hypothesis registry integration (`HypothesisRegistry`, `_evaluate_hypotheses`, `_test_hypothesis`), ICU model integration (`ICUModel`, `ingest_measurements`), `CycleResult.hypothesis_results` field, `LoopConfig` extensions
- `computronium/experiment/surface/cli.py` — Added `--hypothesis-ids`, `--hypothesis-registry`, `--use-icu-guided` to `loop` command

**Verification:**
- `comp loop --dry-run --cycles 2 --hypothesis-ids H1_credit_efficiency --use-icu-guided` works
- `test_loop_uses_engine_lock.py` passes (4 tests)
- `test_cli_surface_lock.py` passes for `loop`, `baseline`, `coverage`, `defect` commands
- Hypothesis evaluation runs paired t-test, Mann-Whitney U, ANOVA tests against cycle records
- ICU model ingests measurements from each cycle's store for guided search

**Remaining work for Phase 5:**
- None — core integration complete. SurrogatePolicy wrapper deferred (interface mismatch with Policy protocol)

---

### Checkpoint Fix & Verification Notes (this session)

**Files modified:**
- `computronium/experiment/execution/deadline.py` — Added `CheckpointData.to_dict()` to serialize `frozenset` as list (JSON compatible)
- `computronium/experiment/execution/pipeline.py` — Use `checkpoint_data.to_dict()` instead of `dataclasses.asdict()`; avoids `TypeError: Object of type frozenset is not JSON serializable`
- `computronium/experiment/registry/loop.py` — Fixed checkpoint schema mismatch, report order, duration tracking, and cycle run_id tracking
- `computronium/experiment/registry/checkpoint.py` — `RunCheckpoint.from_dict` handles missing `spec_hash` from PipelineRunner's CheckpointData format

**Checkpoint issues fixed this session:**
1. **Checkpoint schema mismatch** — `PipelineRunner` saves round-level `CheckpointData`; `CheckpointManager` expects cycle-level `RunCheckpoint`. `RunCheckpoint.from_dict` now handles missing `spec_hash` by synthesizing a minimal checkpoint.
2. **Loop report order** — `_write_loop_report(history)` now called after `history.append(result)`.
3. **Duration tracking** — `_execute` now returns actual `duration_s` instead of `0.0`.
4. **Cycle run_id tracking** — Loop checkpoint now tracks `cycle_run_ids` mapping for loop-level resume.
5. **Loop-level checkpoint integration** — `LoopDriver` now properly saves run_id at cycle start, tracks `cycle_status` (in_progress/complete), and resumes interrupted cycles using `PipelineRunner.from_checkpoint`. Verified: kill mid-cycle → restart → loop resumes from `checkpoint.json` with "Resuming interrupted cycle" message, finds run_id, and continues.

**Outstanding checkpoint issues (deferred):**
1. **PipelineRunner checkpoints every round by default** — adds ~100-500ms/round overhead. Must gate behind `checkpoint_every_n > 0` in `LoopConfig`. (Current code only checkpoints on signals, not periodically)
2. **Single long-lived `ExperimentRegistry` across cycles** — each cycle creates new `ExperimentRegistry` → new `run_id`. Loop-level resume needs single `run_id` across cycles or loop-level checkpoint table tracking `(cycle, run_id)` pairs. Partially addressed by `cycle_run_ids` tracking.

**Assumptions to verify before scaling to `--budget 24h`:**

| Assumption | Risk if wrong | Verification |
|------------|---------------|--------------|
| `n_seeds=1` in quick-verify works with statistical gates | Gates silently fail (need ≥2 seeds for CI/SE) | Run `--cycles 1 --profile quick-verify --n-seeds 2` |
| Exploit axes = Pareto frontier union works with n=20 | All cells non-dominated → no exploitation signal | Check frontier size vs. search space |
| Baseline discovery after pipeline is acceptable | Adds latency; could run in parallel | Time baseline gate separately |
| Dry-run ≈ real execution | Misses runtime errors (OOM, shape mismatch) | One real `--cycles 1` before any `--hours` |
| Single `ExperimentRegistry` per cycle is correct | Provenance `seed_list` is estimate; not exact | Verify `SeedContext` enumeration |
| Hypothesis eval per-cycle on single task works | Cross-domain hypotheses (H1, H3) need accumulation | Test H1/H3 with multi-cycle data |
| DuckDB WAL handles concurrent access | Lock conflicts when CLI + test run simultaneously | Run CLI + pytest in parallel |

**Cost model contamination risk (CRITICAL):**
- Objectives *are* `energy_per_step`, `walltime_total`, `flops`
- If checkpoint I/O adds 10-30% overhead, every reported number is biased
- `RegistryCostModel` learns estimate-vs-actual from *measured* walltime
- **Rule:** Checkpointing only when cycle time > checkpoint interval × 10 AND explicit `--checkpoint-every-n-cycles > 0`
- For `quick-verify` (~60s/cycle): **never checkpoint** — cycle completes faster than recovery

**Next session priority order:**
1. Gate PipelineRunner checkpointing on `checkpoint_every_n > 0` (default 0) — disable for quick-verify
2. Run `--cycles 2` with `n_seeds=2` → verify L1/L2 promotions
3. Single long-lived `ExperimentRegistry` across cycles for loop-level resume (optional optimization)
4. Then From-Scratch Test + First Governed Claim on cheap tasks
5. Cleanup register as one hygiene commit at round close

**Checkpoint fix verified this session:** kill mid-cycle → restart → loop resumes correctly from checkpoint.json with run_id tracking.

---

### Session 3 Progress (Current Session)

**Completed:**

1. **Checkpoint gating (Phase 0/1 follow-up)** — `PipelineRunner` periodic checkpointing now gated on `checkpoint_every_n > 0` (default 0). Added in `pipeline.py:_run_round_loop()` after each round. This eliminates the 100-500ms/round overhead for quick-verify runs.

2. **Cleanup register — dead duplicates removed:**
   - `computronium/experiment/execution/budget.py` → deleted (duplicate of `kernel/resources.py`)
   - `computronium/experiment/execution/cost_tracking.py` → deleted (duplicate of `kernel/resources.py`)
   - `computronium/experiment/execution/promotion.py::promote_run` → deleted (superseded by `promote_with_stats` in `statistical_promotion.py`)
   - Updated imports in `pipeline.py`, `scripts/probes/dynamics_cost.py`, `scripts/demos/_support.py` to use `kernel.resources`

**Verified:**
- `test_loop_uses_engine_lock.py` passes (4 tests)
- `test_cli_surface_lock.py` passes (46 tests)
- `test_allocator_promotion.py` passes (5 tests)
- `comp loop --dry-run --cycles 2` works

**Remaining from Checkpoint Fix section:**
- **Single long-lived `ExperimentRegistry` across cycles** — still creates new registry per cycle (new `run_id` per cycle). The `cycle_run_ids` tracking in `checkpoint.json` provides loop-level resume capability, but a true single registry would be cleaner. Deferred as optional optimization.
- **EvidenceDrivenAllocator** — still exists but `_run_allocator` is no-op; used in tests/demos. Remove in hygiene pass.
- **MultiprocessBackend / DDPBackend** — exported but unused; remove in hygiene pass.

**Known issue (pre-existing, not introduced here):**
- `tests/acceptance/test_promotion_lock.py::test_a_promoted_cell_reaches_l2_by_replay` fails due to provenance validation requiring `code_sha != "unknown"`. The test spec doesn't provide `code_sha`; LoopDriver resolves it via git. This is a Phase O provenance contract enforcement that predates this test.

**Next session priority order (updated):**
1. Run `--cycles 2` with `n_seeds=2` → verify L1/L2 promotions end-to-end
2. Fix promotion lock test (provide `code_sha` in test spec or adjust validation)
3. From-Scratch Test + First Governed Claim on cheap tasks
4. Cleanup register as one hygiene commit: remove `EvidenceDrivenAllocator`, `MultiprocessBackend`, `DDPBackend`, triplicated hardware-fingerprint logic, duplicate hypothesis notions
