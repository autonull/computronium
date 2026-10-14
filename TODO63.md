# TODO63: Realize Computronium — Autonomous, Rigorous, Hands-Free Experimentation

**Status:** DRAFT — adaptive; workstreams are decoupled and may be reprioritized live.
**Predecessors:** TODO60 (kernel move), TODO61 (bug fixes, hyperparameter flow, quick maturation).
**One-line goal:** Turn a capable ontology + kernel into a **closed-loop scientific engine** that tests the *whole* system across *all* domains, learns from every defect, and surfaces only statistically grounded, multi-objective discoveries — with no human babysitting.

---

## 0. Why this document exists

We have an engine that can compose 6 axes of learning mechanisms, verify stability, run
experiments, and store evidence. Recent work proved both the power and the gap:

- The autonomous loop **did** discover a genuine 98.06% config (never seeded).
- But the maturation run **missed that config** (subspace mismatch), the ablation was
  **noise** (1 epoch), and there was **no baseline** to say whether 98% was good.
- We spent a session writing **ad-hoc `run_*.sh` scripts** instead of using the CLI that
  already exists.
- The **26-task, 6-domain registry** (`computronium/domains/registry.py`) was never swept.
- `defects.jsonl` accumulated but **never constrained the search**.

The system optimizes **activity** (cells measured) instead of **knowledge** (validated
discoveries). TODO63 fixes that.

---

## 1. Operating Principles (the rules this TODO enforces)

> These are the non-negotiables. Every workstream is judged against them.

1. **No mystery.** A slow run, a parameter that does nothing, a silent filter, an
   unexplained failure — each is a **defect** to be rooted out, not tolerated.
2. **No hardcoding.** Axes, budgets, sweep steps, task names, baselines, promotion
   thresholds, and "known good" seeds must be **discovered or configured**, never baked in.
3. **Everything is measured against a live baseline.** "98%" is meaningless without a
   same-budget, same-seed reference discovered **online** (we do not ship a fixed suite).
4. **Multi-objective by default.** Accuracy alone is not a result. Pareto frontier over
   `(val_acc, -params, -walltime, -ρ, -energy, train/val gap, …)`.
5. **Fidelity ladder, not fidelity guess.** L0→L1→L2 promotion is decided by **statistical
   gates in code**, not by a human reading HTML.
6. **Every failure is data.** Defects feed constraints, validation updates, and process
   fixes. Nothing is thrown away.
7. **The whole system is the subject.** All 6 domains and all implemented tasks are in
   scope — a vision-only result is a coverage defect.
8. **Adaptive by construction.** Interfaces are pluggable; the loop is data-driven; adding
   a primitive/task/policy/substrate is a **registry row**, not a refactor.
9. **Hypotheses are first-class but not mandatory.** A run may be exploratory; it still
   registers *what it did* and *what it found*.
10. **The system knows its own validation ability.** It reports what it cannot yet measure
    (missing metrics, uncalibrated gates, drift) rather than silently pretending.

---

## 2. Defect Register (observed, to fix first)

| # | Defect | Root cause | Fix workstream |
|---|--------|-----------|----------------|
| **C1** | Maturation subspace ≠ discover subspace; best config never re-tested | Human-picked axes in `run_*.sh` | §4 auto-promotion + §3 registry |
| **C2** | L0 screens are noise (max 37% at 1 epoch) | Wrong fidelity for the question asked | §5 fidelity ladder + gates |
| **C3** | No baseline → "98%" uninterpretable | No online baseline machinery | §6 online baselines |
| **C4** | Single-objective loop (`best_acc` only) | `merge_top` sorts by acc | §7 MOBO proposer |
| **C5** | `defects.jsonl` written, never read | No consumer | §8 defect→constraint loop |
| **C6** | Only `digits` ever run | Scripts never set `--tasks`; profiles single-task | §9 multi-domain sweep |
| **C7** | Ad-hoc `run_*.sh` bypass the real CLI | Rushed workflow | §10 CLI tree consolidation + delete scripts |
| **C8** | No live monitor; `tail -f` required | No TUI | §11 TUI |
| **C9** | Silent drops / no-effect params (history: `params={}`, alias drift) | Declaration vs consumption drift | §12 parameter-effect audit |
| **C10** | Evidence stack disconnected from the loop | Manual publish only | §13 evidence auto-population |
| **C11** | Loop has no idea whether its gates are any good | No calibration | §14 self-validation |

**Fix ordering is by dependency, not severity — see §15.**

---

## 3. Workstream A — Experiment Registry (source of truth)

**Problem:** Runs leave artifacts scattered across `experiments/*.duckdb`, `logs/*.log`,
`state.json`, `ledger.jsonl`, HTML reports; there is no single queryable record of *what
question a run answered* or *what it found*.

**Deliverable:** `computronium/experiment/registry/` with:

- `ExperimentRecord` — `run_id`, `hypothesis` (optional), `config` (full resolved `RunSpec`
  incl. axis values + **effective** hyperparameters), `fidelity`, `seeds`, `parent_run_ids`,
  `gate_results`, `metrics`, `defects`, `baseline_comparison`, `artifacts`.
- `ExperimentRegistry` — append-only, DuckDB-backed, queryable by tag/parent/metric.
- **Auto-registration**: `run_experiment.py` writes a record for **every** run; no manual step.
- **Lineage**: a maturation/ablation run records the L0 run that promoted it.
- **Coverage query**: "which (task × primitive) pairs have never been measured?" — drives §9.

**Acceptance:** given a `run_id`, one query returns its question, config, metrics, gates,
defects, and artifact paths. Given no `run_id`, coverage gaps are enumerable.

---

## 4. Workstream B — Auto-Promotion (fixes C1)

**Problem:** A human decides what to mature. The winning config can be *skipped*.

**Deliverable:** the orchestrator queries the registry for configs that **passed the L0
gate** but have no L1 descendant, and queues them automatically. Symmetrically, L1→L2.

- No hand-picked subspaces. The **promotion queue is derived**, not authored.
- A `--pin` flag exists for deliberate manual study, but is never required.
- Deduplication by `(task, axis-tuple, effective-hyperparams)`.

**Acceptance:** after an L0 sweep, the top-N gate-passing configs appear in the L1 queue
without any human edit. Reproduce the "missed 98%" scenario and confirm it is now caught.

---

## 5. Workstream C — Fidelity Ladder & Statistical Gates (fixes C2)

**Problem:** Screening at the wrong fidelity produces noise; promotion has no statistics.

**Deliverable:** `computronium/experiment/gates/`:

| Rung | Epochs | Seeds | Promotion gate (all must hold) |
|------|--------|-------|-------------------------------|
| **L0** screen | 1 | 1 | beats baseline by margin **and** `ρ ∈ [0.8,1.2]` **and** curve non-degenerate **and** no fatal defect |
| **L1** validate | as configured | ≥3 | `mean > baseline + 2·SE` **and** `CI_width < δ` **and** `train/val gap < g` |
| **L2** confirm | as configured | ≥5 | `mean > baseline + 3·SE` **and** `CI_width < δ'` **and** every seed beats baseline |

- Thresholds (`margin, δ, g`) are **config-driven** with sane defaults, not constants in code.
- Gates return a structured `GateResult(passed, statistic, threshold, reason)` — so failures
  are explainable and the registry records *why* a config stopped.
- **No gate → no promotion.** Humans may override, and the override is recorded as such.

**Acceptance:** removing a gate's mechanism makes a lock test fail (per AGENTS.md: a lock
whose fixture cannot fail is a comment). A config that fails L1 names the failed statistic.

---

## 6. Workstream D — Online Baselines (fixes C3)

**Problem:** No reference. We cannot claim any config is good. Hardware varies, so a shipped
baseline suite would be wrong anyway.

**Deliverable:** baseline discovery as a **first-class run type**:

- Standard optimizers/architectures (`sgd`, `adam`, `adamw`; MLP / small CNN / small
  transformer as applicable per domain) run on **the same tasks, seeds, and budget** as the
  candidate sweep, on the **current hardware**.
- Results stored as `BaselineRecord`s tagged by `(task, hardware-fingerprint, budget)`.
- `BaselineGate` looks up the matching baseline for the candidate's `(task, hardware, budget)`
  — if none exists, it **runs one** (or blocks promotion with an explicit reason).
- Never a fixed list: the baseline set is a **config**, extensible per domain.

**Acceptance:** every promoted config has a same-budget baseline from the same hardware, and
the report shows `Δ = candidate − baseline` with a confidence interval.

---

## 7. Workstream E — Multi-Objective Proposer (fixes C4)

**Problem:** The loop maximizes one number by grid-unioning axes.

**Deliverable:** `computronium/experiment/policy/` with a **pluggable proposer interface**:

- `Proposer` Protocol: `propose(history, constraints, budget) -> list[Coordinate]`.
- **At least one reliable implementation ships now**: wrap the existing Optuna stack with a
  multi-objective study (TPE or NSGA-II) over the objective vector. (Enable now, abstract now.)
- **MOBO path (enabled when deps allow)**: GP surrogate (BoTorch/GPyTorch) + qEHVI/qNEHVI
  acquisition; graceful fallback to the Optuna wrapper.
- **Objectives are declared, not assumed**: the proposer reads the active objective set
  (`val_acc`, `param_count`, `walltime_total`, `ρ`, `energy`, `flops`, `latency`, …) from
  config. Adding an objective is a registry row.
- Acquisition honors **defect constraints** (§8) as a feasibility mask.

**Acceptance:** swapping proposers requires no change to the orchestrator or the registry.
A lock proves the objective set flows from config through to the proposal.

---

## 8. Workstream F — Defect → Constraint Loop (fixes C5)

**Problem:** `defects.jsonl` and `FIX_HINTS` are write-only. The search repeats known-bad regions.

**Deliverable:** `computronium/experiment/registry/defect_registry.py`:

- **Signature taxonomy** (extendable): shape mismatch, empty space, NaN/Inf, spectral-radius
  explosion, convergence failure, catastrophic forgetting, grad explosion/vanishing, OOM,
  mode collapse, no-effect parameter, silent drop.
- **Consumers** (this is the point — a defect must *do* something):
  1. **Negative constraints** for the proposer (rule out axis regions).
  2. **Config validation** updates: a repeated defect is a candidate `SystemConfig.validate`
     rule (proposed as a patch for human review).
  3. **Compatibility matrix** updates used by policy-aware sampling.
  4. **Triage export**: a human-reviewable digest (`defect list --cluster`) for fixes we
     supply — the loop *collects*, we *decide*, the result is *applied* and *locked*.
- **No silent new defect class**: unknown failures are parsed and surfaced, never dropped.

**Acceptance:** injecting a known defect into a sweep measurably prunes the next proposal
(acquisition feasibility shrinks); a lock proves the constraint is applied.

---

## 9. Workstream G — Full-Domain Task Sweep (fixes C6)

**Problem:** We only ever run `digits`. The README promises six domains; the registry has 26
tasks; `RunSpec.tasks` already supports tuples — none of it is used.

**Deliverable:**

- `TaskRegistry` over `computronium.domains.registry.SUPPORTED_TASKS`, enriched with per-task
  metadata (domain, shape, metric, cost class, quick-mode availability).
- `RunSpec.tasks` actually **populated** by the orchestrator — the proposer sweeps
  `task × config`, discovering cross-domain generalizations.
- **Coverage-driven scheduling**: the orchestrator prioritizes un-measured
  `(task × primitive)` pairs (§3 coverage query), so breadth is guaranteed, not hoped for.
- Per-domain objective defaults (e.g., RL success vs. vision accuracy vs. LM perplexity) are
  **declared in the task registry**, not hardcoded in the loop.
- Cost awareness: cheap tasks (xor, iris, spiral) get more cycles; expensive ones (cifar10)
  are budgeted — based on measured walltime, not guesses.

**Acceptance:** within the first budget window, **every domain** appears in a completed L0
cycle; the report shows a coverage matrix `domain × primitive` with gaps highlighted.

---

## 10. Workstream H — CLI Consolidation (fixes C7)

**Problem:** We wrote `run_continuous.sh`, `run_autonomous.sh`, `run_discovery_pipeline.sh`,
`run_maturation.sh`, `run_ablation.sh` — all bypassing the real CLI
(`computronium/experiment/surface/cli.py`), which already has a large command tree.

**Deliverable:** one entry point, extended not rewritten:

```
computronium experiment create|run|monitor|promote|kill|list|analyze|publish|replay
computronium experiment loop      # the autonomous orchestrator (was continuous_experiment.py)
computronium baseline run         # online baseline discovery
computronium defect list|approve  # triage + apply fixes
computronium registry coverage    # what has / hasn't been measured
```

- **Delete every ad-hoc `run_*.sh`.** The CLI is the interface.
- Backwards compatibility is explicitly **not** required (AGENTS.md).
- Subcommands reuse existing `surface/`, `evidence/`, `cli/hypothesis_campaign.py` machinery
  rather than duplicating it.

**Acceptance:** every workflow we performed this session is expressible as a CLI invocation;
a smoke test runs the full pipeline via CLI only.

---

## 11. Workstream I — TUI Monitor (fixes C8)

**Problem:** Watching `tail -f` on a log is the current UX.

**Deliverable:** `computronium/experiment/surface/tui.py` (Textual), launched by
`computronium experiment monitor`:

- Live: current cycle/fidelity, budget elapsed, **live Pareto frontier**
  (acc × params × walltime × ρ), per-cell progress, gate status.
- **Defect pane**: defects this cycle + constraints added.
- **Coverage pane**: domain × primitive matrix, gaps highlighted.
- Read-only, resumable, multi-store (view several runs). Web UI deferred.

**Acceptance:** a full run is monitorable with zero log-tailing; the TUI reflects registry
state within one poll interval.

---

## 12. Workstream J — Parameter-Effect Audit (fixes C9)

**Problem:** History: `params={}` silently dropped swept knobs; alias drift; no-effect
parameters. "No mystery" means every declared knob is proven to reach the computation.

**Deliverable:**

- **Effect lock** (property test): for each declared hyperparameter, vary it and assert the
  measured output changes (or assert it is *documented as structurally inactive* for that
  primitive). This generalizes the existing hyperparameter-flow lock repo-wide.
- **Silent-drop detector**: any swept value dropped by composition raises a recorded defect
  (never a silent filter).
- **Slow-path audit**: instrument the cell pipeline; publish per-stage timings; any stage
  above a configurable threshold becomes a defect with a suggested fix.

**Acceptance:** a lock fails if a swept knob has no effect and is not explicitly declared
inert. Per-stage timings are queryable from the registry.

---

## 13. Workstream K — Evidence Auto-Population (fixes C10)

**Problem:** The `evidence/` stack (claims, significance, protocol, procedures, status,
limitations, failure, statistics, artifacts, model_registry) exists but is disconnected.

**Deliverable:**

- Every `ExperimentRecord` materializes an evidence entry: procedures = resolved config;
  statistics = gate results; artifacts = stores/logs/curves; status = gate outcome;
  limitations = what fidelity has *not* established.
- **Evidence is raw material, not a self-fulfilling prophecy**: nothing is marked
  "validated" merely because it was run; status reflects *gates passed*, and limitations
  always state the un-tested regime (e.g., "L1 only; no seed-variance at L2 yet").
- Publishing (LaTeX/PDF) stays a deliberate human act; the loop only **prepares**.

**Acceptance:** a run produces a complete, honest evidence entry with no manual authoring;
limitations are always populated.

---

## 14. Workstream L — Self-Validation Awareness (fixes C11)

**Problem:** The loop cannot tell whether its *gates* are calibrated or its *environment* has
drifted.

**Deliverable:**

- **Gate calibration**: track L0→L1→L2 promotion rates; flag when a rung is
  non-discriminative (e.g., >90% promote ⇒ L0 too loose; <5% ⇒ too strict) and surface a
  suggested threshold adjustment.
- **Drift detection**: periodically re-run top configs; if a metric shifts beyond its seed
  band on unchanged hardware, raise an environment-drift defect.
- **Metric-coverage warnings**: report any primitive lacking stability/energy/parity metrics.
- **Capability self-report**: `computronium experiment capabilities` lists what the system
  can currently *validate* and what it *cannot*.

**Acceptance:** an intentionally mis-calibrated gate is detected and reported; a simulated
drift raises the correct defect.

---

## 15. Execution Order (dependency-aware, not waterfall)

Each workstream is independently shippable and **decoupled**; the order below is the critical
path to a meaningful 24h run, and items may be reordered as findings dictate.

1. **A — Experiment Registry** (everything else records into it)
2. **D — Online Baselines** (needed before any gate can mean anything)
3. **C — Fidelity Ladder + Gates** (turns runs into verdicts)
4. **B — Auto-Promotion** (removes the human; fixes C1)
5. **G — Full-Domain Sweep** (breadth; fixes C6)
6. **H — CLI Consolidation** (write once, delete scripts)
7. **J — Parameter-Effect Audit** (no mystery; no-effect knobs)
8. **F — Defect → Constraint Loop** (learn from failures)
9. **E — Multi-Objective Proposer** (Optuna+MO first; GP+EHVI later)
10. **I — TUI** (UX)
11. **K — Evidence Auto-Population** (publication prep)
12. **L — Self-Validation Awareness** (the system grades itself)

---

## 16. Acceptance Criteria (Definition of Done)

A single `computronium experiment loop --budget 24h` run, **with no human intervention**:

1. [ ] Sweeps **all 6 domains** — coverage matrix shows zero un-touched domains/primitive-pairs.
2. [ ] Runs **online baselines** on current hardware; every promoted config has a same-budget Δ.
3. [ ] Applies the **fidelity ladder** with **statistical gates**; every promotion is justified.
4. [ ] **Auto-promotes** gate-passers (the "missed 98%" scenario cannot recur).
5. [ ] Optimizes a **declared objective set** (≥3; includes accuracy × params × walltime).
6. [ ] **Learns from defects**: known-bad regions pruned; defect digest produced for review.
7. [ ] Emits a **live TUI**; no `tail -f` anywhere in the workflow.
8. [ ] Registers every run; full **lineage** and **coverage** queryable.
9. [ ] Produces an **evidence entry per run** with honest limitations.
10. [ ] Reports its **own validation ability** (calibration, drift, metric gaps).
11. [ ] Is driven **entirely through the CLI**; zero `run_*.sh` scripts remain.

---

## 17. Anti-Goals / No-Tolerance List

- ❌ Hardcoded axes, budgets, sweep steps, task names, "known good" seeds, or baselines.
- ❌ A parameter that is swept but has no effect (must be locked or declared inert).
- ❌ Silent drops, silent filters, silent failures.
- ❌ Promotion by human eyeball; promotion without a statistic.
- ❌ Vision-only results presented as system-wide.
- ❌ Evidence marked "validated" without a gate having passed.
- ❌ Ad-hoc shell scripts that duplicate the CLI.
- ❌ Repeating a known-bad region because the defect was recorded but ignored.
- ❌ Slow paths left un-instrumented.

---

## 18. Adaptive-Design Notes (how this stays agile)

- **Interfaces over implementations**: `Proposer`, `Runner` (Local → Ray → SLURM), `Gate`,
  `BaselineSet` are Protocols. First implementation ships; better ones drop in.
- **Registry-row extensibility**: new task, primitive, objective, gate, or defect class is a
  registry entry — no `if/elif` edits in the loop.
- **Config-driven thresholds**: gates, budgets, and objective sets live in config, so policy
  changes are data changes.
- **Fail-open visibility**: anything the system cannot yet do is *reported*, never hidden —
  so the map of the work is always current.
- **Workstreams are decoupled**: any may be paused, reordered, or split without blocking the
  others. This document is a living backlog, not a contract.

---

**Next action:** begin at §15 step 1 (Experiment Registry) and step 2 (Online Baselines) —
they unblock every downstream verdict. Verify with the CLI smoke test at each step; delete
the ad-hoc scripts when Workstream H lands.
