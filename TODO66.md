# TODO66 — Conclude the Project: Make It Run, Show It, Hand It Over

**Status:** Terminal plan. This closes development.
**Predecessor:** TODO65 (wiring + repair). TODO65 §9 declared v1.0 "wired and verified"; §1 of this
document measures that declaration against the tree and finds it partly true, partly asserted.
**Scope:** **No new engine capability.** Repairs, consolidation, presentation, documentation, and one
recording. Everything here either makes an existing promise true or removes a promise we cannot keep.

---

## 0. What "finished" means

Six sentences, each testable:

1. **Runnable.** A fresh clone + `uv sync --dev --all-extras` runs every command in the demo
   screenplay (§4) with exit code 0 and no traceback, on CPU, in under ~10 minutes total.
2. **Productive.** `comp run <profile>` produces records; `comp report` produces a report containing
   **at least one governed claim with `n` and variance**, plus honest limitation lines. Today it
   produces neither (§2.1).
3. **Self-explanatory.** `README.md` alone — regenerated from `docs/readme/*.md` — takes a stranger
   from "what is this" to "I ran it and understand what came out", without opening a second document.
4. **Demonstrable.** `docs/DEMO.md` is a shot list. Every command in it is executed by
   `tests/acceptance/test_demo_script.py`, so the video cannot drift from the software.
5. **Complete.** No user-facing path raises, no lock is red for a reason we cannot state in one
   sentence, and every unimplemented capability is a **named ledger row** (§8), not a silent absence.
6. **Credible as a referee.** A reader with no stake can verify, from the tree alone, that a comparison
   here was pre-registered, that every arm got the same treatment, that each implementation published
   its deviations from its source paper, and that the project logged its own refutations (§1.3). This
   is the project's distinctive value: the algorithm zoo cannot neutrally evaluate itself, and this is
   the one thing a single author with no algorithm of their own can supply (§11.2).

**"100% runnable" is scoped to user-facing paths** — the CLI surface, the documented library API, and
the demo screenplay. It is not a claim that every experimental research programme in §8 has been run.

### 0.1 Four audiences, four falsifiable statements

The project serves four people, and each gets a test, not a paragraph.

| Audience | They must be able to… | Test |
|---|---|---|
| **ML library user** | `uv sync`, paste the README's 60-second snippet, train a 6-axis system | `test_demo_compose_6axis` — **verified green, 15.4 s** (see §1.1); snippet locked to source by `scripts/readme_snippets.json` |
| **Researcher** | point the engine at a config, get records, a report, and a verdict that says either `PASSED`, `REJECTED`, or `INSUFFICIENT` | §6.G3 + §6.G4 |
| **Contributor** | add one ontology primitive by following README alone, and see where the project wants to go next | §5.8 + §5.10 + §6.G8 |
| **Algorithm author / consortium member** | check, without trusting the author, that their rule was represented faithfully and compared under a pre-registered, unfiltered protocol | §1.3 apparatus + G11 + §5.12 |

A deliverable that only satisfies the second row is a demo, not a handover.

---

## 1. Measured starting state (evidence, not opinion)

Two full `tests/property/` runs, same machine, same interpreter, same ruff (`0.16.10`), same
`pyproject.toml`. "Before" is `699ee72b` (Oct 15, immediately before the TODO65 push), checked out in
a worktree.

| | before `699ee72b` | `HEAD` `5e4b39af` |
|---|---|---|
| passed | 1607 | **1691** |
| failed | 39 | 81 |
| errors | 40 | **21** |
| collection errors | 6 modules | 1 module |
| repo-wide ruff findings | 690 | **659** |
| `tests/acceptance/test_v1_exit.py` | absent | **passes** |
| walltime | 275 s | 350 s |

**The failure count rose because debt became visible, not because the engine regressed.** Six property
modules (`policy_generation`, `price_oracle`, `round_loop_mechanism`, `run_ledger`, `sampler`,
`stage_model`) could not be *imported* at `699ee72b`; they import now and fail on contract. Three
genuine regressions were introduced (§2.6–2.8).

### Empirical run of the product path

```
$ uv run comp run quick-verify --store demo.duckdb --overrides '{"budget_seconds": 150}'
  → 10 records in 10.6s
  → Promotion: 10 cell(s) assessed, 0 earned L2
       every cell: maturity=l1, replay=fail, stats_gates_passed=False
$ uv run comp status --store demo.duckdb
  9baf33e0... | completed | recs=10 | claim=10 | promo=0
$ uv run comp report --store demo.duckdb --format text
  Claim Eligible: 10          ← claims it has ten claims
  ...
  Claims (n and variance are mandatory; a claim line is not prose):
    (none — see Limitations)
  [no_eligible_claim] no record met the claim eligibility predicates
$ uv run comp coverage report --store demo.duckdb
  Traceback ... _duckdb.ConversionException: Unimplemented type for cast (STRUCT(...) -> BOOLEAN)
```

The report is otherwise genuinely excellent (credit-ablation table with `n`/`std`, Pareto, hypervolume,
seed-variability with CI). The engine works. **The promotion ladder and one CLI command do not.**

### 1.1 The library layer — verified, not assumed

The plan's scope is the experiment kernel, so the library was measured separately rather than trusted:

| Check | Result |
|---|---|
| `pytest tests/integration/test_demo_compose_6axis.py -m demo` | **1 passed, 15.4 s** — composes RecurrentGeometry + ThermodynamicContrast + DigitalSubstrate and trains on MNIST |
| root public surface | **142 names**, all lazy (`computronium/__init__.py::_LAZY`) |
| README snippet lock | `scripts/readme_snippets.json` maps `composition_6axis` → that exact demo test; `test_readme_build_lock` fails if they diverge |

So the library layer is *usable today* and already locked. **Nothing in this plan needs to touch it**,
and §10's anti-goal ("no new capability") applies to `computronium/` core without exception.

### 1.2 The research layer — three real results already exist and are invisible

The repository already owns three finished pieces of research. None appears in `README.md`
(`vanishing contrastive`: 0 hits; `phantom`: 0 hits):

| Result | Where | What it establishes |
|---|---|---|
| **Deep EqProp boundary** | `docs/eqprop_deep_limitation.md` | Multi-layer vanilla EqProp does not learn: vanishing contrastive signal, slope −1.19, R²=0.80 at β=0.01. DirectedEP restores the signal (slope +0.16, R²=0.85) but **not** accuracy — 9.2% at depth ≥3, chance for 10 classes, 5 epochs, 3 seeds. Gate G2 **FAILED**. 1-layer EqProp remains viable. |
| **Phantom-knob audit** | `docs/phantom_knob_audit.md` | A search-space key sampled by a sweep but silently dropped at construction poisons parity and liveness identically; detected by `computronium.core.construction.phantom_knobs`, enforced by `validate_all_rule_spaces()`. |
| **ρ(J) vs σ_max conflation** | `docs/CORRECTIONS.md` | Power iteration reported as "spectral radius" on nonnormal J ([[0.5,10],[0,0.5]]) converges to ≈0.5 while ‖J‖₂ ≈ 10.025 — caught by the repo's own `test_jacobian_amplification`, replaced by three separated estimators, old frontier numbers flagged `requires_rerun`. |

**These are the discovery output of the project so far**, and they are stronger than any result a
six-minute demo can manufacture: one falsification with a diagnosed mechanism, one methodological
audit, and one self-correction enforced by a regression lock. §4.6 surfaces them; §5.9 makes that
surface generated so it cannot drift.

### 1.3 The neutrality apparatus — the project's strongest asset, already 80% built

The system's most defensible value is not the six axes; it is that it can compare an algorithm zoo
**without the zoo's authors doing the comparing**. The machinery for that already exists, and none of
it is in `README.md`:

| Instrument | Where | What it enforces | State |
|---|---|---|---|
| **Evaluation Fairness Contract** (F-1…F-6), append-only | `docs/FAIRNESS_CONTRACT.md`, `docs/evaluation_fairness_contract.md` | identical treatment of arms on data, budget, stopping, seeds, reporting; all comparisons unfiltered or a *named* correction — "cherry-picking is a triage failure, not an editorial choice" (F-5) | written |
| **Pre-registered thresholds** | `configs/preregistrations/*.json` (**11** registrations) + `computronium/validation/preregistration.py` | declare metric, superiority margin, error rate and seed budget *before* running; `paired_comparison` returns bootstrap CI, sign-flip permutation p, Cohen's dz | built, **not wired into the claim path** (§3.20) |
| **Algorithm Identity Cards** | `docs/IDENTITY_CARDS.md` — **31 rows**, generated from `AlgorithmIdentityCard` on each primitive | every rule ships its **paper citation** and a **Deviations** column stating exactly where this implementation departs from the published algorithm | **generated, `--strict` green, drift-locked** (verified) |
| **Phantom-knob detector** | `computronium/core/construction.py::phantom_knobs` | a search key sampled but silently dropped at construction — the exact "hyperparameters are underexplored" defect | built, `validate_all_rule_spaces()` green |
| **Compute-matched HPO protocol** | `docs/hpo_protocol.md`, `biopl-hpo` | same patience tier for every family, one Optuna study per model, compute-matched | protocol + separate CLI, not an enforced kernel invariant (§3.21) |
| **Metric provenance rule** | `docs/metric_provenance.md`, `test_metric_provenance.py` | any metric computed on a nudged/target-conditioned state is excluded from learning claims | locked |
| **Corrections log** | `docs/CORRECTIONS.md` + `CorrectionRecord` | superseded measurements are recorded with the audit that invalidated them | maintained |
| **Standalone epistemic ledger** | `packages/ceec-core` | claim decisions held outside the engine that produced them | built, export wired (§2.6) |
| **Discovery/confirmation seed split** | `execution/statistical_promotion.py`, `registry/seed.py` | promotion only on seeds the search never saw | being repaired (§2.1–2.2) |

**This stack is the consortium's constitution, and it is nobody's marketing.** It is the reason a
comparison produced here is harder to dismiss than one produced by an inventor. §5.11 promotes it from
an appendix to the README's first value proposition; §11.2 states the argument and its limits.

**Verified now:** `python scripts/generate_identity_cards.py --strict` exits 0 and its output is
byte-identical to `docs/IDENTITY_CARDS.md` — i.e. *every* concrete credit/update/plasticity primitive
already declares its deviations from its source paper, with citations.

### 1.4 Feasibility measurements — the numbers the plan is sized from

Every estimate below was measured on this machine (CPU, 1 seed unless stated), not inferred. They are
what make §4.2 and §7 real rather than optimistic.

| Measurement | Result | Consequence |
|---|---|---|
| `comp run quick-verify --overrides '{"batch_limit":0,"epochs":3,"n_seeds":5}'` | **50 records in 520 s → 10.4 s/record** | The earlier "128 s projected" was priced at `batch_limit=2`. Full-batch cells cost ~10× more. |
| one cell, `digits`, full batch, 3 epochs, `hd=32`, `energy_minimization`, `gradient` | `euclidean` 22.9 s / val **0.339**; `adam` 21.5 s / val **0.861**; `muon` 21.7 s / val **0.950** | The backprop control *does* learn. `euclidean` learns slowly at the default step; it is not broken. |
| same cell, `dynamics=instantaneous` | **0.8 s** / val **0.869** | Settle dynamics are the runtime; `instantaneous` is ~27× cheaper and still learns. This is the lever that makes a ≤180 s demo possible. |
| the 50-record run's report, "Credit Ablation" | `gradient` **0.094**, `random_projections` 0.095, `thermodynamic_contrast` 0.089, `local_goodness` 0.393, `pepita` 0.528 | **The control is at chance while local rules "win".** Not a finding — a confound (§2.9). |
| `RunSpec` fields | includes `code_sha` | The replay hash changes per commit; G10 must be stated within-commit (§6). |
| `compute_run_replay_hash` | `sha256(spec, sorted(measurement_keys))`, **measured values deliberately excluded** | A stable hash proves the same *cells* were visited, **not** that a metric reproduces. §11.1 must not overclaim it. |

---

## 2. P0 — Blocking defects (the product does not currently finish its own story)

### 2.1 L1 statistical gates are structurally unreachable → no L2 → no claim
`check_superiority_gate` (`execution/statistical_promotion.py:162-193`) returns `passed=False` when
`len(cell_values) < thresholds.required_seeds_per_group`. That property
(`statistical_promotion.py:57-66`) calls `required_sample_size(effect_size=0.5, power=0.8, alpha=0.05)`,
which is **63**. Profiles budget `n_seeds` of 1 (`quick-verify`) to 10 (`claim`) —
`surface/cli.py:107-240`. The gate therefore cannot pass at any configured fidelity, so
`gate_result.all_passed` is always `False`, so `_evaluate_l2_confirmation` is never called, so
`replay_status` keeps its default `"fail"`, so **no cell ever earns L2 and no claim is ever derivable**.

This directly contradicts TODO65 §6.C1, which is the *written contract*: "thresholds from the C0 power
analysis, not fixed `2·SE`… A verdict reports `power_achieved`, so REJECTED means 'no effect', not
'underpowered'." The implementation collapses "underpowered" and "no effect" into one failure.

**Repair.** Separate the three states the plan already named: `PASSED`, `REJECTED` (power sufficient,
effect absent), `INSUFFICIENT` (power below target). Compute `power_achieved` from the observed effect
size and `n`; promote to L1 on `PASSED`, and carry `INSUFFICIENT` as a *limitation line* on the report,
never as a silent `false`. `required_seeds_per_group` becomes the number reported *for planning*, not a
gate that silently forbids the ladder. Lock it with §6.G3.

### 2.2 The CLI promotion path passes no baseline and no confirmation evaluator
`_settle_maturity` (`surface/cli.py:1940-1980`) calls
`promote_with_stats(..., baselines=None, ...)` with the comment "Baselines not yet wired", and passes
no `confirmation_evaluator` — only `registry/loop.py:1214-1238` supplies one. So the CLI falls back to
`replay_survives` (`execution/promotion.py:85-109`), which re-measures stochastically and therefore
**always** fails tolerance. TODO65 §3.W6 marked the baseline/Pareto wiring **DONE**; it is done in
`LoopDriver`, not in the path the user runs.

**Repair.** Resolve baselines through `BaselineRegistry` in `_settle_maturity` (the same call
`LoopDriver._exploit_axes` makes), and pass a confirmation evaluator built from `cell_record` +
`dataclasses.replace(schedule, seed=…)`, exactly as `LoopDriver._settle` does. Delete the "not yet
wired" comment by making it false.

### 2.3 `comp coverage report` crashes
`surface/cli.py:3010` casts the `status` STRUCT column to BOOLEAN:
`_duckdb.ConversionException: Unimplemented type for cast (STRUCT(...) -> BOOLEAN)`. Status became a
struct in the three-tier work; this query was never updated.
**Repair.** Select `status.gate_verdict`, not the struct. Add it to the demo screenplay (§4) so it can
never regress silently.

### 2.4 Two different definitions of "claim eligible" on one surface
`comp report` prints `Claim Eligible: 10` and, twelve lines later, `Claims: (none)`. The statistics
line counts a *planned* predicate; `derive_claims` requires `min_seeds=5` **achieved PASS** seeds
(`evidence/claims.py:37, 173, 486-526`) and finds none. One fact, two sources — the exact failure mode
AGENTS.md and TODO65 §1.3 forbid.
**Repair.** Delete the dishonest counter or rename it to what it measures (`claimed_by_planned_seeds`),
and derive the report's eligibility line from `count_achieved_seeds`. The report must never contradict
itself.

### 2.5 The lazy map points `Budget` at a stub with the wrong API
`execution/__init__.py:182-185` maps `Budget`/`CostModel`/`SimpleCostModel` → `budget`.
`execution/budget.py:14-34` (re-created by `b31fa557`) defines
`Budget(soft_seconds, hard_seconds, max_cells)` with `from_duration(duration)` and **no**
`started_at`/`target_cells`/`target_cost` kwargs. The real class is `kernel/resources.py:103-204`.
`f5693caa` deleted the original 216-line `execution/budget.py`, which *did* match every caller;
re-adding a smaller stub with a non-matching signature converted six import errors into **35 test
failures** across `test_policy_generation_lock` (26), `test_sampler_lock` (9),
`test_run_ledger_lock` (2).
**Repair.** Repoint the three map rows at `kernel.resources` and delete `execution/budget.py`. Verify
with `test_policy_generation_lock`, `test_sampler_lock`, `test_run_ledger_lock`, `test_stage_model_lock`.

### 2.6 `evidence/ceec_export.py` violates the kernel isolation lock
`test_kernel_isolation_lock.py:34-46` lists `"ceec"` in `FORBIDDEN_PREFIXES` (the "ceec delegation"
rule). `ceec_export.py:54,56,117,119` imports `ceec` and `ceec.store`. W3 (`9b5c6946`) added this and
the lock went red.
**Repair — decision, documented in the lock.** CEEC is now a *declared dependency* (`pyproject.toml`)
and the export is the sanctioned boundary (TODO65 §3.W3). Move innocuous `ceec` imports inside the
functions that use them (as already done at 54/117) **and** narrow the lock: `ceec` is permitted in the
one module whose purpose is the CEEC boundary, enumerated by name like `KNOWN_BLOCKED`. Do not widen
`FORBIDDEN_PREFIXES` globally.

### 2.7 Lazy export map drift
- `execution.__all__` omits submodules `compose`, `search_space`; `test_lazy_export_lock.py:66-82`
  still lists them (they moved to `kernel/`).
- `execution._symbol_to_module:260-264` holds dead rows `BatchSizer`, `CellStream`, `CellStreamState`.
- `evidence._symbol_to_module:261-262` holds dead rows `validate_record_input`,
  `validate_record_output`, dropped from `__all__` by `b31fa557`.
**Repair.** Prune the dead rows, drop the moved submodules from the lock's list, and add a
`tests/property` assertion that the map's key set equals `__all__` (the four directions the lock
already has, minus the stale fixtures).

### 2.8 Tests import moved modules from `execution`
`from computronium.experiment.execution import search_space` — `test_width_contract_lock.py:384,449`,
`test_settle_stability_lock.py:286,425`; `... import compose` —
`test_task_geometry_compat_lock.py:174`, `test_dry_run_gate_lock.py:100`. Both live in `kernel/`.
**Repair.** Repoint the six imports at `computronium.experiment.kernel.*`.

### 2.9 The report's "per-axis ablation" is a confound presented as a finding — the worst possible defect here

Measured (§1.4): on a 50-record `quick-verify` run, the report prints a **Credit Ablation** table
saying `gradient` 0.094, `random_projections` 0.095, `thermodynamic_contrast` 0.089, `local_goodness`
0.393, `pepita` 0.528. A reader concludes PEPITA beats backprop 5×. What actually happened is that each
credit value landed on a **different** `hidden_dim`, `update`, and `dynamics`, because the profile
sweeps all six axes at once:

```
gradient               euclidean  feedforward energy_minimization  val=0.097   ← hd≈8
pepita                 adam       feedforward energy_minimization  val=0.711   ← hd≈64
local_goodness         muon       feedforward lazy                 val=0.639
random_projections     adam       recurrent   instantaneous        val=0.094
```

The control arm is at chance and the "winner" is a bigger network with a better optimizer. **This is
precisely the cherry-pickable, hyperparameter-confounded comparison the project exists to prevent**,
emitted by the project's own flagship artifact. Publishing it would end the neutrality claim on day one.

Three defects, one repair each:

1. **The table does not know it is confounded.** `payload` carries no `hidden_dim`, so neither the
   table nor a reader can see the difference. The ablation must either (a) group only cells that share
   the other five axes and say so in the header, or (b) print a `confounded: arms differ on N of 5
   axes` banner naming them. Silence is not an option. **Prefer (a)**: a cell set that does not share
   five axes produces **no** ablation table, only the raw per-cell list.
2. **No chance-line floor.** `docs/FAIRNESS_CONTRACT.md` names it (E-10: "lr=0 planted control,
   chance-line floor"); the report does not apply it. Any arm at chance must be labelled `at chance`
   in its row, so a 0.094 cannot be read as "backprop is bad".
3. **No positive control.** The profile can sweep a space in which *no* arm works. A comparison is
   invalid unless a known-good arm (backprop + a competent update) clears chance by a wide margin in
   the same regime. That becomes G13 and it is the demo's precondition.

**Gate:** `test_ablation_is_not_confounded` — a run whose measured cells differ on any axis other than
the ablated one must produce no ablation table; a run with a shared-five-axes group must produce one,
and every row must carry `n`, `std`, and a `at chance` flag when applicable.

---

## 3. P1 — Repairs that make the shard truthful

Each item is one commit; each names its gate. Do them in this order — later items assume earlier ones.

| # | Defect | Evidence | Repair | Gate |
|---|---|---|---|---|
| 3.1 | `ProposalComposeError: Unknown geometry keys ['depth'] for topology 'feedforward'` at collection | 4 errors, `test_device_hygiene_gate.py` | Reconcile the geometry key vocabulary in the fixture/composer; `depth` is not a `feedforward` key | file collects; `test_geometry_wiring_lock` |
| 3.2 | `Provenance(env={})` rejected: "missing env fingerprint" | ~13 setup errors (`evidence/service`, `learning` locks) | Fixtures build the fingerprint via the store's own helper — one source, not a re-derived dict | those locks |
| 3.3 | `Namespace object has no attribute '--experiment-db'` | 7 setup errors, `test_experiment_invariants.py` | The fixture passes option strings to a parser that expects dest names; read the dest, not the flag | file green |
| 3.4 | `Proposal` used at runtime though `TYPE_CHECKING`-only | `test_state_algebra_lock.py:293`, `execution/pipeline.py` | Import at runtime (it is a dataclass, cheap) or annotate as string | lock green |
| 3.5 | duckdb imported outside the store | `test_single_writer_enforcement.py:69`, `surface/cli.py` | Route through `RecordStore` | lock green |
| 3.6 | MNIST-shaped literals in the budget planner | `test_active_space_lock.py:185`, `adaptive_budget.py:569,582` | Read the shape from the task/spec | lock green |
| 3.7 | Vacuous sole assertions | `test_assertion_quality_lock.py:120`, `test_settle_stability_lock.py:45,66,93` | Assert the value | lock green |
| 3.8 | Sampler: `test_accuracy` accepted as a measured objective; `resolve` not fail-closed | 3 failures, `test_sampler_lock.py:190,203,216` | Make `resolve_objectives` refuse an objective with no `metric_key`, raising `UnmeasuredObjectiveError` | lock green |
| 3.9 | Swept knob `substrate.sparsity` reaches no cell; per-stage timing fields absent | `test_hyperparameter_effect_lock.py:343,550` | Wire the knob through `compose_configs`; stamp the timing fields the record schema declares | lock green |
| 3.10 | Run ledger: divergent spec hashes equal; resume duplicates/gaps | `test_run_ledger_lock.py:247,279` | Include the diverging field in the replay hash | lock green |
| 3.11 | Unreachable primitive not filtered (`dynamics/instantaneous`) | `test_price_oracle_lock.py:100` | Filter at declaration, as the void constraints do | lock green |
| 3.12 | No cells measured in the budget window | `test_budget_utilization_lock.py:93` | Measure the window from `Deadline`, not a re-derived clock | lock green |
| 3.13 | `CostModel` interface absent | `test_stage_model_lock.py:360` | Point at `kernel.resources.CostModel` (fixed by 2.5) | lock green |
| 3.14 | Intent persistence / export / unknown-field rejection | 7 failures, `test_wp11_surface_lock.py` | Restore the `OperatingPoint` field validation and round-trip | lock green |
| 3.15 | Learning integration: cross-task identity, achieved-seed claims, calibration split | 4 failures, `test_wp10_learning_integration_lock.py` | Fix the split predicate and the identity key | lock green |
| 3.16 | Schema forward tolerance | 3 failures | Unknown fields survive a version bump; unsupported versions fail closed | lock green |
| 3.17 | Protocol-field prefilter | 1 failure, `test_scientific_validity_protocol_lock.py` | Prefilter reads the protocol fields it claims to | lock green |
| 3.18 | `test_schedule_device_lock::test_device_cuda_recorded_in_store` | 1 failure | Skip-with-reason on a CPU-only host, assert the record on CUDA | lock green or documented skip |
| 3.19 | Lint ratchet: 659 measured vs `BASELINE = 418` | `test_lint_count_ratchet.py:37` | **Deliberate re-baseline.** 690 was measured at `699ee72b`, so the baseline was already stale. Set `BASELINE` to the measured value in the same commit, record the count **per rule** in §8 as a Register C row, and keep the ratchet's "no increase" direction. Do not lower the number by adding `noqa`. | both ratchet tests green |
| 3.20 | **The claim path ignores pre-registration.** `ThresholdRegistration` + `paired_comparison` exist (`computronium/validation/preregistration.py`), 11 registrations sit in `configs/preregistrations/`, and **nothing under `computronium/experiment/` references either** (`grep` → 0 hits). A claim can be emitted with no pre-registered threshold, which is the exact hole a biased author would climb through. | verified by grep | **Label, do not restructure.** `Claim` is a frozen dataclass with 7 required fields and no limitation/registration slot, so adding one touches every construction site and its locks — too invasive for a close-out. Instead add a `_unpreregistered` sibling to `_no_eligible_claim` in `evidence/limitations.py` (measured: ~20 lines, the pattern is established) and emit it whenever a claim's run has no matching registration. **A claim with no registration says so, in the report, next to the claim.** | `test_claim_report_lock` + an assertion that an unregistered claim carries the limitation line |
| 3.21 | `MIN_SEEDS = 5` (`validation/preregistration.py:46`) and `DEFAULT_MIN_SEEDS = 5` (`evidence/claims.py:37`) are two constants, one fact | grep | One re-exports the other; the claim floor has a single source (TODO65 §6.C0's rule) | both import paths resolve to one object |
| 3.22 | Compute-matched HPO is a protocol document plus a separate `biopl-hpo` CLI; the kernel's per-cell search does not enforce an equal trial budget per arm | `docs/hpo_protocol.md` vs `execution/policy.py` | **Do not wire it** — that is a feature. Ledger it (§8) with the exact reason: "equal-effort HPO is a protocol, enforced by `biopl-hpo`, not by `comp run`." The README's neutrality section must say so (§5.11) | §8 row present; README does not overclaim |

**Not in scope, and said out loud:** driving 659 legacy lint findings to zero. That is a hygiene
programme with no user-visible payoff, and pretending otherwise is how the previous plans accumulated
asserted-done rows. The ratchet's job is to stop growth; it stays.

---

## 4. The demonstration: one entry point, seven beats

**Design constraint.** TODO65 §0 defines turn-key as "**one** configurable entry point". Today the
entry is a 33-command CLI where the honest answers are buried among `dashboard`, `dataset`,
`environment`, `quality`, `frozen-theta-psi`. A viewer cannot find the story. The fix is
**consolidation, not capability**: group the surface, and give the promise an actual entry.

### 4.1 One new surface (the only one), and why it is not a feature
`comp demo` — an orchestrator that calls the *same* functions `run`/`status`/`report` already call.
It adds no engine logic and no configuration the other commands lack. Its justification is textual:
TODO65 §0 promised one entry point; §9 marked the promise done; the promise is unmet. If it is
rejected, the fallback is a shell script in `docs/DEMO.md` with identical beats — decide once, in the
first commit, and record the decision.

`comp demo` prints seven beats, each with a heading, the command it is equivalent to, and the result:

| Beat | Shows | Underlying command |
|---|---|---|
| 0 | the machine is ready | `import optuna, scipy, torchvision, duckdb` + device resolve |
| 1 | **the declared space, priced** | `comp run demo --dry-run` |
| 2 | **execution**: cells, rounds, verdicts | `comp run demo --store demo.duckdb` |
| 3 | **the ledger**: what landed | `comp status --store demo.duckdb` |
| 4 | **the governed result**: verdict + limitations + the price of a real answer | `comp report --store demo.duckdb --format text` |
| 5 | **what is unreached** | `comp coverage report --store demo.duckdb` |
| 6 | **what we learned** — the results we already own | §4.6; no command |

### 4.2 The `demo` profile — sized from measurement, built as a controlled contrast

A `RunProfile` row (the config surface exists for exactly this) **plus a contrast design**, because a
profile that sweeps six axes at once cannot support an ablation (§2.9). Measured unit costs are in §1.4.

**Fixed (the contrast group — every arm identical):**

| Knob | Value | Why |
|---|---|---|
| task | `digits` | fast, offline, 10-class chance = 0.10 |
| geometry | `feedforward`, `hidden_dim=32` | measured to learn (§1.4); `hd≈8` is the degenerate case that produced the confound |
| dynamics | `instantaneous` | measured **0.8 s/cell** vs 21.5 s for `energy_minimization` — the whole reason ≤180 s is achievable |
| plasticity | `null` | not the axis under test |
| update | `adam` | the competent optimizer; fixes the confound |
| fidelity / epochs / batch | `L1` / 3 / full (`batch_limit=0`) | the measured regime |
| `n_seeds` | **5** | the claim floor, `claims.py:37` |

**Swept (the only thing that varies):** `credit` ∈ {`gradient`, `random_projections`, `pepita`,
`thermodynamic_contrast`, `local_goodness`} → 5 cells × 5 seeds = **25 records**.
Measured cost ≈ 0.8 s/record at `instantaneous`, so **~20–30 s wall**; budget `120s`, which leaves
headroom without letting the space expand.

**Positive control, mandatory.** `gradient` is arm zero and must reach ≈0.87 (measured, §1.4). If the
control is at chance, the run is **invalid** and the demo must not be recorded: that is a defect, not a
result. This is G13, and it is what separates a demonstration from a table of noise.

**Expected outcome, stated in advance.** `gradient` highest, `pepita` competitive, `thermodynamic_contrast`
and `random_projections` behind. If that ordering holds it is a *reproduction of the literature under a
shared protocol*, not a discovery — and the video must say so. If it does not hold, that is the
interesting case, and it still gets published with `n=5` and `INSUFFICIENT`.

**The payoff is not "a win".** An earlier draft of this section asked the regime to deliver "at least
one axis value measurably ahead so the video has a finding". That is selection bias with a nicer name:
choosing the cell count until a difference appears is precisely what the statistical gates exist to
prevent, and doing it in the *demonstration* would discredit every other number in the report. The
demo's payoff is instead:

1. **A controlled ablation table** — one axis varies, `n` and `std` on every row, the chance line drawn,
   no winner declared. This is the neutral comparison in miniature (§11.2): five rules from different
   traditions, one protocol, none of them the author's, and the control arm proving the apparatus works.
2. **The verdict** — `PASSED`, `REJECTED`, or `INSUFFICIENT`, with `power_achieved` printed.
3. **The price of an answer** — beat 4 multiplies the power requirement (`63` seeds/group for d=0.5,
   §2.1) by the measured per-cell cost, and states the walltime and GPU-hours an *actual* claim about
   this axis would cost, on this machine.

That third line is the most valuable sentence in the video: it tells the viewer what a real answer
costs and why the project refuses to pretend it has one.

**Fallback if §2.9's repair is not done:** the demo ships with the raw per-cell list and **no**
ablation table. A missing table is honest; a confounded one is fatal.

### 4.3 Make the plan screen legible
`comp run … --dry-run` output is already the best teaching artifact in the repo (declared 450 cells,
24 legal from a priced sample, 128 s projected, per-dynamics breakdown, "budget: never binds — the
space ends first"). Required polish only:
- one consistent section grammar (`space / price / budget / first cells`) across every profile;
- no ANSI escape or `\r` progress when stdout is not a TTY (the video is piped through a recorder);
- **accept `--profile` as an alias for the positional** — every first-time user types
  `comp run --profile quick-verify` and gets `unrecognized arguments: --profile` (verified).

### 4.4 Group the surface; do not delete it
`comp --help` shows **core** (run, report, status, demo, coverage, gallery — the six that tell the
story). Everything else stays reachable under `comp --help-all` and is unchanged. This is a
presentation change; §1 of TODO65 ("prefer wire over delete") is honoured. Re-pin
`test_cli_surface_lock` and regenerate the README's CLI table.

### 4.5 The screenplay (`docs/DEMO.md`)
Cold open on `README.md`'s first screen; narrate the motivating hypothesis in one sentence; then the
six command beats, each with: exact command, the *expected output* (pasted, locked), and **one
sentence to say**. Close on beat 6 (the research we own) and the ledger: what the engine does not yet
know. Total budget: **6 minutes**.

`tests/acceptance/test_demo_script.py` executes every command in the screenplay against a `tmp_path`
store with the recorded timings, asserting the contract of each beat:
- beat 1 exits 0 and prints a priced projection;
- beat 2 writes ≥4 records and ≥1 promotion-or-insufficiency verdict;
- beat 3 lists the run;
- beat 4 contains a claim line with `n=` and a limitations section, and contains **no** contradiction
  between its eligibility count and its claim count (locks §2.4);
- beat 5 exits 0 (**locks §2.3 forever**).

This test is the video's truth condition. If it is green, the video is honest.

### 4.6 Beat 6 — the research we already own

The screenplay closes on three slides, one per result in §1.2, each with the document, the number, and
the mechanism. Not a summary of the codebase — the *findings*. This is the beat that answers "has this
project ever discovered anything?", and the answer is yes, including a falsification the authors
accepted against their own hypothesis.

Rules for these slides:
- the number is quoted from the document, never recomputed for the video;
- the failure is named as a failure (G2 FAILED, 9.2% = chance), not softened;
- each slide names the lock or audit that makes it checkable (`test_jacobian_amplification`,
  `validate_all_rule_spaces`, the B2 autopsy slope/R²).

A project that shows its own refuted hypothesis is more credible than one that shows a 99% digits run,
and it is the only honest thing available at this budget.

---

## 5. README: the only document

`README.md` is generated from `docs/readme/*.md` by `docs/readme/build_readme.py` and locked by
`tests/property/test_readme_build_lock.py`. Edit snippets, regenerate, never hand-edit.

| # | Change | Why |
|---|---|---|
| 5.1 | New `docs/readme/start-here.md` at the **top**: six commands, each with its real output excerpt, in ≤40 lines | The current first screen is a 3-table capability pitch; §0.3 says the README must take a stranger to "I ran it". The product path exists at line ~1013, below 1000 lines of capability prose. |
| 5.2 | Demote the three overlapping capability tables into one | They restate the same six axes; "only necessary documentation" forbids duplication |
| 5.3 | Add **"What is proven / what is not"**, generated from the readiness ledger (§8) | The current "Status: active development" line is the only honesty statement in 1460 lines. A generated ledger is truthful by construction. |
| 5.4 | Fold `## 🧪 Enhanced CLI Tools`, `## 🛠️ Kernel Development Workflow`, `## 🧪 Registry Integrity Locks` into one "Developers" section | Three sections for one audience |
| 5.5 | The quickstart's Python compose snippet stays, but moves **after** the product path | Both audiences exist; the *engine* audience is the pitch |
| 5.6 | Link `docs/DEMO.md` (the video) from the first screen | Demonstrability is the deliverable |
| 5.7 | Regenerate; `test_readme_build_lock` green; every generated count reads from the registry | TODO65 §4, unchanged and still binding |
| 5.8 | **Move the "add an ontology primitive" checklist out of `AGENTS.md` into the README's developer section** (registry row → config classmethod → wiring lock → export surfaces → contract invariants → demo row) | Today README:1417 delegates to `AGENTS.md`. A contributor who is inspired has to find a second file; §0.1 row 3 says README alone must be enough. `AGENTS.md` stays the *agent* contract, not the only ramp. |
| 5.9 | New `docs/readme/findings.md`, **generated** from `docs/{eqprop_deep_limitation,phantom_knob_audit,CORRECTIONS}.md` (title + headline number + status per result) | The three real results in §1.2 are invisible (`phantom`: 0 hits). Generated, so the README cannot claim a finding the doc no longer supports. |
| 5.10 | "Good first additions" — the §8 *Designed* rows rendered as a short list with the file each would touch | Converts the ledger from a graveyard into an invitation. This is the concrete form of "inspiring others to grow the system". |
| 5.11 | **`docs/readme/neutral-evaluation.md`, placed above the capability tables.** States what the apparatus in §1.3 guarantees, in the project's own voice: pre-registered thresholds · equal treatment of arms · every rule's deviations from its paper declared with citation · a corrections log · claims held in a party outside the engine · **an ablation table only where five of six axes are held fixed, with a chance line and a positive control**. Then the one sentence that is the point: *no credit rule in this repository is the author's invention.* | This is the differentiator, and today it is invisible. It also gives the video its thesis, and it makes §2.9 a published promise rather than an internal fix. |
| 5.12 | `docs/CONSORTIUM.md` — a one-page leave-behind: what a member gets (a comparison stack they can cite, with the contract version and the corrections log), what a member must accept (pre-registration, unfiltered reporting, publication of nulls, audit of their implementation's declared deviations), and the four things we do **not** yet do (§11.2) | The video is a pitch; a pitch needs something to hand over. One page, no promises the tree cannot keep. |
| 5.13 | **Hard editorial rule, enforced by review of the diff:** the neutrality section names *our* procedure only. It never asserts that other authors cherry-pick, that other codebases are wrong, or that this project is unbiased. Both are unprovable, and the accusation makes the refutation about the accuser. | §11.2 — the moral framing is the weak one, and it is the one that gets quoted back |

**Constraint:** no claim in the README may exceed what `comp report` emits. If the report says
`INSUFFICIENT`, the README says underpowered, not "demonstrated".

---

## 6. Gates

Cheap first; each gate is named with the defect it prevents from returning.

| Gate | Prevents |
|---|---|
| **G1** `uv run python -m pytest tests/property/ -q` — 0 failed, 0 errors | §2, §3 regressing. Run **twice** total in this plan: once after §2, once at close. |
| **G2** `tests/unit/` + `tests/acceptance/test_v1_exit.py` green | the engine |
| **G3** `test_promotion_ladder_honesty` (new, in `test_seed_separation.py`): given `n` below `required_seeds_per_group`, a verdict is `INSUFFICIENT` with `power_achieved`, never `REJECTED`; given `n` at the requirement and no effect, it is `REJECTED` | §2.1 — the defect that made every claim unreachable |
| **G4** `test_demo_script.py` | §2.3, §2.4, and the video's truth |
| **G5** `test_readme_build_lock` | §5, and every hand-written count |
| **G6** `ruff format` clean; `ruff check <changed>` no **new** findings; `pyright` 0 errors on changed library files | per-commit quality |
| **G7** `comp --help` shows ≤6 core commands; `comp --help-all` shows all | §4.4 |
| **G8** every document named in README's findings section exists, and its headline number still appears in that document | §5.9 — a result can be retracted, and the README follows |
| **G9** `tests/integration/test_demo_compose_6axis.py -m demo` green and still byte-identical to the README snippet | the library quickstart (§1.1) — already true; this makes it a gate, not a fact |
| **G10** the demo run twice from a clean store, **within one commit**, produces the same sorted `measurement_key` set and therefore the same `replay_hash` | policy determinism. **Note:** the hash covers the spec (including `code_sha`) and the visited cells, and *deliberately excludes measured values* (§1.4) — so it proves the same cells were visited, never that a metric reproduces. Do not describe it as reproducibility. |
| **G13** the demo's `gradient` control arm beats chance by a wide margin (measured ≈0.87 vs 0.10); the run aborts with a diagnostic if it does not | §2.9 — a comparison with a broken control is a table of noise, and recording it would be fatal |
| **G11** `python scripts/generate_identity_cards.py --strict` exits 0 **and** its output equals `docs/IDENTITY_CARDS.md` | §1.3 — a new primitive without a declared deviation is a neutrality leak. Already green; this stops it going stale. |
| **G12** README's neutrality section is generated from `docs/FAIRNESS_CONTRACT.md` + `IDENTITY_CARDS.md` + `CORRECTIONS.md`, and names only the project's own procedure | §5.11, §5.13 — a claim about our process cannot drift from the process |

Per commit: G6 always; G4–G5 when the surface or README moves; G1 only at the two close points.
**Never** `pytest tests/`. **Never** re-run a green shard to confirm.

---

## 7. Order of work

| Phase | Work | Exit |
|---|---|---|
| **A** | §2.5 → §2.7 → §2.8 (map + imports; the 35-failure cluster) | those four locks green |
| **B** | §2.1 → §2.2 → §2.4 (the ladder; G3), then **§2.9** (the confounded ablation — see the note below) | a `comp run` that emits an honest verdict *and* an unabused ablation table |
| **C** | §2.3, §2.6 (crash + isolation decision) | `coverage report` exits 0 |
| **D** | §3.1–§3.18 (shard tail), §3.21 | G1 first run: 0 failed |
| **E** | §3.19, §3.20, §3.22 (ratchet, preregistration label, HPO ledger row) | ratchet green; claim path honest |
| **F** | §4.2 `demo` profile + contrast design; §4.3 polish; §4.4 grouping | `comp demo` in ≤180 s; **G13 green — control at ≈0.87** |
| **G** | §4.5 screenplay + `test_demo_script.py`; §4.6 research beats | G4 green; video shot |
| **H** | §5 README consolidation + §5.8–5.13 + regenerate; `docs/CONSORTIUM.md` | G5, G8, G9, G11, G12 green |
| **I** | Close: G1 second run, G2, G7, G10; tag; update this file | 0 red |

A–C are the same afternoon. D is the long tail. F–H is the presentation.

**§2.9 outranks everything after §2.5.** Measured (§1.4), the report's flagship ablation table currently
shows `gradient` at 0.094 while `pepita` sits at 0.528 — a confound caused by sweeping six axes at once.
That table is the project's single most quotable artifact and its most damaging one if wrong. Fix the
confound before polishing anything that displays it.

---

## 8. Readiness ledger — what we hand over, and what we do not

Append to TODO65 §5; it remains the durable answer to "what could this eventually be?". This table is
generated into README §5.3, so it cannot drift.

**Live (user path):** loop + 11 stages · 8 proposal policies · DoE · ICU metamodel · allocator ·
statistical promotion · multi-objective/Pareto · baselines/ruler · evidence store, three-tier status,
claims, limitations · CEEC export · provenance/seed/checkpoint · per-stage timings · reports
(text/JSON/HTML) · `comp` core commands.

**Designed, not built (intent preserved):** M1 gate calibration · M2 drift detection · M3 metric
coverage warnings · `capabilities` command · repo-wide effect lock · C12 ruler-geometry fallback · `defect revoke` re-probe · policy-aware
compatibility sampling · `SystemConfig.validate` codegen.

**Planned (intent, no code):** **fair-HPO recovery study — for each zoo algorithm, re-tune under
equal effort and publish the delta from its published number** (the "these algorithms may be better than
commonly believed" programme; needs §3.22's gap closed and real compute) · 7-domain task expansion
(cifar100, svhn, wikitext2, penn_treebank, mountain_car, lunar_lander, diabetes, california_housing,
ett_h1, PDE suites) · physical-hardware validation (memristive/neuromorphic/optical/quantum) ·
Ray/SLURM · DDP at scale · `campaign_queue` as loop driver · full CEEC integration ·
`question_first` literature store · a real TUI · **an evaluation consortium** (§11.2): the fairness
contract as a shared constitution, identity cards as the admission ticket, the corrections log as the
shared memory.

**Retired (finding kept):** E1 deep chaotic unfolding — **falsified**, mechanism boundary is
composition-error compounding · older "ρ(J)=estimator" claims (`docs/CORRECTIONS.md`) · legacy
`experiment/cli` runners · the `execution/budget.py` stub (wrong API, deleted §2.5) ·
the `step_size_override_<dynamics>_<credit>` multiplier column and its post-construction
mechanism (29 rows, every one an identity after TODO48b R4; the measurement is
`docs/CORRECTIONS.md` Correction 3) · 12 unread `step_size_*` rows and 3 unread optimizer
priors, leaving 28 rows with one reader each (§15) · Register C: legacy lint findings,
counted per rule below, ratcheted not cleaned (§3.19).

**Register C — legacy lint, ratcheted and censused (not cleaned):** 650 findings measured 2026-10-17
under ruff 0.16.10; `test_lint_count_ratchet.py` holds `BASELINE = 659`, so the direction is still
never-up. Per rule: RUF105 81 · PLW0717 62 · C901 46 · E402 36 · C408 33 · PLR0914 30 · F841 30 ·
PLR0912 26 · PLR0915 23 · PLR1702 21 · S110 18 · PLW1514 16 · PLW1510 14 · SIM102 13 · S607 13 ·
RUF059 13 · PLR0911 12 · TRY300 12 · PLR6201 10 · E741 9 · PLR6104 9 · RUF029 9 · TC001 7 ·
TRY400 6 · S603 6 · S404 6 · PLR0917 6 · PLW2901 5 · PLR0913 5 · C401 5 · TRY401 5 · 37 rules
with ≤4 findings (63 total).

**Neutrality apparatus (live, §1.3):** fairness contract F-1…F-6 (append-only) · 11 pre-registered
threshold JSONs + `paired_comparison` (bootstrap CI, sign-flip p, Cohen's dz) · 31 generated identity
cards, `--strict` green, drift-locked · phantom-knob detector · metric-provenance rule · corrections
log · CEEC ledger · discovery/confirmation seed split.

**Neutrality defects found by measurement and repaired (§2.9):** the per-axis ablation table used
to aggregate cells that differ on all other five axes (`gradient` 0.094 vs `pepita` 0.528) — now
printed only for a shared-five-axes group, with `n`/`std` and an `[at chance]` flag · the fairness
contract's chance-line floor (E-10) is applied by the report · a positive control must clear chance
before a comparison is published.

**Neutrality gaps (named, so the README cannot imply otherwise):**
1. **All credit rules are this project's re-implementations**, with deviations declared and cited — not
   the inventors' reference code, and not verified against it. The defensible claim is "independent
   re-implementation with disclosed deviations", never "verified upstream".
2. **Equal-effort HPO is a protocol, not a kernel invariant** (§3.22): `docs/hpo_protocol.md` +
   `biopl-hpo`, not `comp run`.
3. **No blinding.** The analyst sees arm identity. A blinded arm-label path is unbuilt.
4. **Pre-registration was not enforced in the claim path** (§3.20); after this plan an unregistered
   claim is *labelled*, not refused.
5. **One language, one task family so far.** Vision/classification on `digits`-class data. Cross-domain
   neutrality needs the 7-domain expansion (Planned, above).

**Results we actually own (the discovery output, to date):** three findings survived the project's own
audits — deep EqProp boundary (gate G2 FAILED), the phantom-knob defect class, and the ρ(J)/σ_max
conflation corrected by three separated estimators. [`docs/FINDINGS.md`](docs/FINDINGS.md) carries the
numbers, source documents, and the lock behind each.

**The handover claim.** What ships is a *laboratory*, not a result: a composable six-axis system, an
experiment kernel that records what it measured and refuses to overclaim, a demo that shows both, and
three findings — two negative, one methodological — that survived the project's own audits. Every
stronger claim is a ledger row with a name. That is the maximum value available without new features,
and it is worth showing.

---

## 9. Definition of done

Checked against the tree at close (see §12–§14 for the evidence).

- [x] §2.1–§2.9 repaired; each with the lock that prevents its return.
- [x] The ablation table appears **only** for a shared-five-axes contrast group, carries `n`/`std` per
      row, and flags any arm at chance (§2.9).
- [x] G13 green: the `gradient` control arm beats chance before any comparison is published
      (measured `0.4389` vs chance `0.10`; the plan's ≈0.87 estimate was stale — §14).
- [x] `comp run demo` produces an honest verdict on CPU in ≤180 s, from a clean tree (~31 s measured).
- [x] `comp coverage report` exits 0.
- [x] Every demo-script command exits 0; `test_demo_script.py` green.
- [x] Property shard: **0 failed, 0 errors**. Unit + acceptance green (§13, §14).
- [x] `test_readme_build_lock` green; README's first screen is the six-command product path.
- [x] `README.md` contains no claim the report cannot emit.
- [x] `comp --help` ≤6 core commands; all reachable under `--help-all`.
- [ ] `docs/DEMO.md` exists; **video recorded**; length ≤6 min; every command on screen is in the
      script. — Shot list and its executable lock are done; the recording is an offline artefact and
      the only open item in this plan (§14).
- [x] The video's closing beats quote the three results in §1.2, numbers unchanged from their documents
      (`docs/DEMO.md` beat 6).
- [x] README alone lets a contributor add one primitive (§5.8) and find a named next step (§5.10).
- [x] README's first value proposition is neutral comparison (§5.11), generated and gated (G12); it
      names only our procedure, never another author's motives (§5.13).
- [x] `docs/CONSORTIUM.md` exists, is one page, and promises nothing in §8's neutrality gaps.
- [x] G11 green: every concrete primitive declares its deviations from its source paper, `--strict`.
- [x] §8 ledger complete; every unimplemented capability named.
- [x] `TODO65.md` and this file carry a final progress section; no TODO67 is opened.
- [x] Tagged: `v1.0.0`.

---

## 10. Anti-goals

- **No new engine capability.** If a beat needs a feature, cut the beat.
- **No new dependency** except a recorder the user already owns. No `rich`, no `textual`.
- **Never** fake a result: no raised `batch_limit`, no seed reuse to manufacture significance, no
  claim printed when the ladder said `INSUFFICIENT`.
- **Never** hand-write a count in the README.
- **Never** delete a capability without a ledger row.
- **Never** green a lock by weakening its assertion. Fix the thing, or state the exemption by name in
  the lock with its reason (the pattern `KNOWN_BLOCKED` established).
- **Never** `pytest tests/`, `--lf`, `--ff`, or re-run a green shard.
- **Never** open TODO67.

---

## 11. Why one plan is enough — and where it would break

**Agreed, with one condition.** This is achievable in one plan *because* it is a repair-and-present
plan: the engine already runs (10 records in 10.6 s, an honest report with ablation tables and
limitations de-rivable from records, a passing exit test). Nothing here invents a capability. The
largest single item is the promotion ladder (§2.1–2.2), and it is a ~100-line change to a function
whose intended behaviour is already written down in TODO65 §6.C1.

**Condition:** success is defined as §9, not as "the property shard was green once". If a §3 item turns
out to be a design question rather than a bug, **state it in §8 as a ledger row and move on** — do not
open a plan for it. That rule, more than the item list, is what makes one plan enough.

**Where it breaks, honestly:**

0. **The confound in §2.9 is the plan's biggest risk, and it was found late.** The flagship artifact
   currently reports a 5× "win" for PEPITA over backprop that is entirely `hidden_dim` and optimizer
   (§1.4). The repair is contained (group by shared axes; draw a chance line; require a control), but it
   must land before any screenshot exists, or the project's most quotable table is its most damaging.
1. **§2.1 has a real design fork.** If `INSUFFICIENT` promotion is judged unsound (a claim from 5 seeds
   is weak), the alternative is to keep the 63-seed gate and make the `demo` profile take ~4 hours on
   CPU. That kills the video for the "one sitting" audience. Recommendation: `INSUFFICIENT` is a
   *label*, and the claim line already carries `n=5`, so the reader sees the weakness. Decide in phase
   B; if the other branch is chosen, §4.2 and §4.5 must be re-budgeted, and that is an afternoon, not
   a plan.
2. **§3's tail is bounded by measurement, not by hope.** The 60 listed failures are localized; the risk
   is that two or three hide a design question. The mitigation is the phase-D rule above.
3. **The video is the only genuinely new artefact.** Everything else is recall of work already done and
   already paid for. That is why this is 1 plan.

If, at phase D's close, more than five §3 items are still red **and** each names a design question
rather than a bug, then the honest answer is not TODO67 — it is to cut the demo to the beats that are
true and ship. The plan is sized so that outcome is still a shippable project.

### 11.1 The ceiling — what this plan cannot deliver, and must not imply

Stated here so the README cannot quietly promise it:

1. **A positive empirical discovery.** At `n≤10` on digits, with a power requirement of 63
   seeds/group, an effect large enough to claim would have to be enormous. §4.2 therefore promises a
   *verdict and a price*, not a finding. Anything stronger requires a scheduled campaign
   (`claim` profile, `--budget`), which is compute, not code.
2. **External validation.** Nobody outside this repository has run it. What G10 buys is *determinism of
   the visited cells*, not reproducibility of a number — the replay hash excludes measured values by
   design (§1.4). Metric-level reproduction is `replay_survives`, which is exactly the gate that always
   fails (§2.2). Say "you can re-run it and visit the same cells", never "you can reproduce the result".
3. **Hardware or substrate claims.** Every measurement in the tree is digital. Memristive,
   neuromorphic, optical and quantum staging are ledger rows. The README's motivating hypothesis is an
   agenda; after this plan it must still read as an agenda.
4. **Publication-grade statistics.** The `63`-seed requirement is the honest number and it is printed
   on screen in beat 4. A paper would need that campaign run, which is exactly the "next level" the
   video is meant to attract investment for.

**What is achievable, and is enough:** a stranger can install it, run it, watch it refuse to overclaim,
read three findings that survived audit, see the exact cost of a real answer, and find a named list of
where to take it next. That is the difference between an impressive repository and a project someone
else can pick up — which is the only form of "inspiring others to grow the system" that survives
contact with a stranger's afternoon.

### 11.2 Why a neutral-comparison consortium is the right ask — and how to ask for it

The claim under consideration is that this system can evaluate the algorithm zoo *without the zoo
competing with itself*, because its author has no algorithm in it. The claim is sound in structure and
**must be made procedurally, never personally.** Two formulations, one of which will be turned against
us:

- **Weak (do not use):** "other authors cherry-pick because their publication incentives reward it."
  Unprovable, adversarial, and it makes the rebuttal about the accuser's motives. It also has an
  immediate counter: this author has dogs in this hunt — a six-axis ontology, an energy-minimisation
  dynamics that `IDENTITY_CARDS` already discloses differs from canonical EqProp by batch
  normalisation, and a published *negative* result about someone else's algorithm. "I am unbiased" is
  not auditable. "These are my declared deviations" is.
- **Strong (use this):** *an honest comparison has a price, and no single participant can pay it.*
  Beat 4 computes that price on screen: `63` seeds per group for a d=0.5 effect, times the number of
  arms, times the number of axes, times the HPO trials each arm needs to be fairly tuned. An inventor
  has no incentive to fund a comparison they might lose; a critic has no access to the implementations.
  The gap is structural, not moral, and a consortium is the only institution shaped like the gap.

**What the repository can already put on the table** (§1.3): an append-only fairness contract with
pre-registered thresholds and unfiltered reporting (F-5); per-implementation deviations with citations
(`--strict` green over 31 rows); a defect class detector for silently dropped hyperparameters; a
corrections log that records its own refuted estimates; and a claim ledger held outside the engine that
produced the claim. Almost no benchmark suite has all five, and none of them is a marketing artefact —
each is a lock that fails when violated.

**What the ask must not promise** (§8 gaps 1–5): verified *upstream* code, enforced equal-effort HPO in
`comp run`, blinding, refused unregistered claims, or cross-domain coverage. A consortium recruited on
those promises would discover the gap in its first meeting, and the project would lose the only asset it
actually has — that everything it says is checkable.

**The invitation, in one sentence:** *bring your algorithm and the paper whose deviations we must
declare; we will pre-register the comparison, publish the result unfiltered including the nulls, and
log our own corrections — and neither of us gets to choose the outcome.* That sentence is defensible
because the tree already enforces four of its five clauses, and §3.20 adds a label to the fifth.

**Where this touches the plan.** Nothing above is a new feature: it is §5.11 (README positions the
existing apparatus), §5.12 (`docs/CONSORTIUM.md`, one page), §5.13 (the editorial rule that keeps the
framing procedural), §3.20 (label an unregistered claim), §3.22 (state the HPO gap rather than imply
it away), §4.6/beat 6 (show the refuted hypothesis beside the corrections log), and G11–G12 (the
artefacts cannot drift). Beat 4's printed price is what makes the ask quantitative.

**The one thing that would falsify the whole framing,** stated so a reader can hold us to it: if this
repository ever produced a comparison whose arm ordering flipped between the pre-registered threshold
and a favourable post-hoc one, the neutrality claim would be dead. The corrections log exists to make
that visible rather than fatal — but it must be read as a commitment, not a feature.

---

## 12. Implementation progress

**Session 2026-10-17 (first implementation pass).** Plan commits `5c0b23cc…` had no
code behind them at the start of this session; the list below is what now has.

### Landed, with its lock

| Plan item | Change | Evidence |
|---|---|---|
| §2.5 | `Budget`/`CostModel`/`SimpleCostModel` resolve to `kernel.resources`; `execution/budget.py` deleted; `pipeline.py` accepts only the canonical `Budget` | `test_policy_generation_lock`, `test_sampler_lock`, `test_stage_model_lock` green |
| §2.7 | Dead map rows pruned (`BatchSizer`, `CellStream*`, `validate_record_*`); moved submodules dropped from the lock; `kernel.*` targets resolve absolutely | `test_lazy_export_lock` green |
| §2.8 | Six test imports repointed at `kernel.compose` / `kernel.search_space` | those locks green |
| §3.8 | `resolve_objectives` fails closed on `metric_key is None`; `test_acc`, `test_loss`, `f1_score`, `bleu_score`, `mean_reward` no longer claim to be measured | `test_sampler_lock` green (27) |
| §2.1 | `StatisticalVerdict` (PASSED/REJECTED/INSUFFICIENT) with `power_achieved`; underpowered is never REJECTED; a missing baseline is INSUFFICIENT, not a silent pass | new `TestPromotionLadderHonesty` (G3) in `test_seed_separation.py` |
| §2.2 | CLI `_settle_maturity` resolves the baseline through `BaselineRegistry` and passes a `cell_record` confirmation evaluator; baseline metric reads `val_acc`, not the objective name | `comp run quick-verify` exercised end-to-end |
| §2.3 | `coverage report` reads `status.gate_verdict` instead of casting the struct | `comp coverage report` exits 0 on a real store |
| §2.4 | Eligibility is computed from achieved PASS seeds at `DEFAULT_MIN_SEEDS` (no fidelity filter), the same rule `derive_claims` applies; `_min_seeds` is one constant | `comp report` prints `Claim-Eligible Cells: 4` beside four credit claims; `test_claim_report_lock` green |
| §2.9 | Ablation only for a contrast group that shares the other five axes **and** the swept params; otherwise raw cells. Rows carry `n`, `std`, `[at chance]`; chance read from the task's `output_dim`. Text, HTML and the template generator share one grouping | new `test_ablation_lock.py` (3) |
| §2.6 | Kernel-isolation lock permits `ceec` only in `ceec_export.py`, enumerated by name | `test_kernel_isolation_lock` green |
| §3.20 | `UNPREREGISTERED_CLAIM` limitation emitted when a claim's metric has no `configs/preregistrations/*.json` | `test_claim_report_lock` green |
| §3.21 | `MIN_SEEDS = DEFAULT_MIN_SEEDS` (validated re-export) | both import paths resolve to one object |
| §4.1/4.2 | `comp demo` dispatches the same `run`/`status`/`report`/`coverage` handlers; `demo` profile holds five axes and params fixed and varies credit. **Four arms, not five:** `thermodynamic_contrast` is unreachable under `instantaneous` dynamics and was removed rather than declared. G13 runs the gradient control check before publishing | `comp demo` in ~31 s, 20 records |
| §4.3 (partial) | `--profile` is accepted as an alias for the positional profile | `<cli>` lock |
| §4.4 | `comp --help` lists six core commands; `comp --help-all` lists all; dispatcher lock re-pinned | `test_cli_surface_lock` green (44) |
| §4.5/4.6 | `docs/DEMO.md` is the shot list; `tests/acceptance/test_demo_script.py` executes the beats, asserts eligibility/claim consistency and coverage, and checks G10 (two clean runs visit the same cells, same replay hash) | `pytest -m demo tests/acceptance/test_demo_script.py` → 2 passed, 72 s |
| §5.1/5.8/5.9/5.11/5.12 | New `start-here`, `neutral-evaluation`, `findings` snippets; primitive checklist moved out of `AGENTS.md` into the README; `docs/CONSORTIUM.md`; README regenerated | `test_readme_build_lock`, `test_cli_readme_lock`, new `test_findings_lock` (G8) green |

### Measurements that revise the plan

- **The `demo` positive control reaches 0.4389, not ≈0.87.** Same shape as §1.4
  (hd=32, adam, instantaneous, 3 epochs, `batch_limit=0`,
  `param_budget=MEASURED_PARAM_BUDGET`), reproduced through `cell_record`
  (0.54 on one seed) and the pipeline (mean 0.44, 5 seeds). It clears chance by
  4.4×, so G13 is green under the implemented floor
  `max(3×chance, chance+0.2)`, but the §4.2/§6.G13 "≈0.87" number is stale.
  Either correct the number or raise epochs / lower `param_budget` narrowing;
  the demo budget currently spends ~31 s of 120 s.
- **`thermodynamic_contrast` is unreachable with `instantaneous` dynamics.** The
  plan's five-credit sweep cannot be run as written at the measured 0.8 s/cell
  regime; the demo uses the four legal arms.
- **`execution.Budget.target_cells` is discarded** when `Budget` is converted to
  `Deadline`, so a cell-budget interruption cannot stop mid-round.

### Still open (next pass, in plan order)

1. **§3 tail is not green.** The first property run after this pass measured
   **32 failed, 24 errors, 1752 passed** (from 81/21/1691 at HEAD, §1). The
   session-budget fix then cleared `test_a_diverged_run_hashes_differently…`,
   `test_every_policy_resumes…` and `test_three_launches…`. Still red, by
   area:
   - `test_run_ledger_lock::test_two_policies_over_one_store_measure_different_trials`
     — random and model-based visits are identical for this fixture. A design
     question: with no evidence the model-based policy proposes the head of the
     stream, which coincides with the sampled set. Decide whether the fixture
     or `ModelBasedPolicy.propose` is wrong; do not weaken the assertion.
   - §3.5 `single_writer`, §3.6 `active_space`, §3.7 `assertion_quality`,
     §3.9 `hyperparameter_effect` (+ per-stage timing), §3.11
     `price_oracle`, §3.12 `budget_utilization`, §3.14 `wp11_surface`, §3.15
     `wp10_learning`, §3.16 `schema_forward_tolerance`, §3.17
     `scientific_validity_protocol`, §3.18 `schedule_device`, plus
     `multi_axis_campaign`, `task_geometry_compat`, `state_algebra`.
2. **§3.19 lint ratchet** re-baselined from 418 to the measured **659** with
   `RUFF_VERSION` unchanged; both ratchet tests are green. Per-rule counts were
   not recorded (the plan asks for a Register C row); do that in the hygiene
   pass, not here.
3. **§4.3 polish** not done: no non-TTY progress suppression, no unified
   `space / price / budget / first cells` grammar.
4. **§5.2/5.3/5.4/5.10/5.13** not done: the three capability tables still
   overlap, the readiness ledger is not generated into the README, and the
   neutrality section is curated prose rather than generated (G12).
5. **Video** not recorded; `docs/DEMO.md` is ready to shoot.
6. **G1** was run once at the end of this pass; the summary is in the commit
   notes/session log. It is not 0-failed yet because of item 1.

### Gate state at the end of this pass

| Gate | State |
|---|---|
| G1 property shard | **32 failed, 24 errors, 1752 passed** (464 s), run before the session-budget and ratchet fixes. Those fixes closed four rows (`test_a_diverged…`, `test_every_policy_resumes…`, `test_three_launches…`, both ratchet tests); the remaining red set is listed above. |
| G2 unit + `test_v1_exit` | **550 passed, 1 xfailed** (154 s). The single `caplog` setup error only appears under `-p no:logging`, which removes the fixture provider; it is not a defect. |
| G3 promotion ladder | green: `TestPromotionLadderHonesty` (2) |
| G4 demo screenplay | green: `pytest -m demo tests/acceptance/test_demo_script.py` → 2 passed, 72 s |
| G5 README build | green |
| G7 core help | green: 6 core commands in `comp --help`, 34 under `--help-all` |
| G8 findings | green: `test_findings_lock` (4) |
| G10 same cells | green: `test_two_clean_runs_visit_the_same_cells` |
| G11 identity cards | unchanged (green at HEAD) |
| G12 generated neutrality | **not done**: the section is curated prose, not generated from the contract/cards/log |
| G13 control | green under the implemented floor (`0.4389 > max(3×0.1, 0.1+0.2)`); the plan's ≈0.87 figure is stale |

**Lint note.** The ratchet is re-baselined to 659 and green; per-rule Register C
counts remain hygiene-pass work. No new `noqa` was added to buy a green run.

---

## 13. Second implementation pass (2026-10-17, later session)

The first pass left 27 targeted failures and 21 property setup/collection errors.
All are now closed in the same tree, with the mechanism fixed rather than the
assertion weakened.

### Closed, by item

| Plan item | What was actually wrong | Fix |
|---|---|---|
| §3.2 env fingerprint | Five fixtures and `scripts/run_experiment.py` built `Provenance(env={})`; the store refuses an empty env. `record_intent` did the same, so every intent round-trip failed. | New `environment.environment_variables()` — one source from `EnvironmentCapture`; store intent records and every record-writing fixture use it. `run_experiment` also resolves the dataset/code SHA instead of persisting `"unknown"`. |
| §3.3 experiment invariants | The fixture called `config.getoption("--experiment-db")`; pytest expects the *dest* (`experiment_db`), and the option was not registered anywhere. | `--experiment-db` / `--run-id` registered in `tests/conftest.py`; fixture reads the dests; the dead module-level hooks were deleted. |
| §3.1 device hygiene | Fixture declared feedforward geometry as `{"depth": 2}`; the composer's key vocabulary is `num_layers`. | Fixture uses `num_layers`; the file collects and 60 cells run. |
| §3.4 TYPE_CHECKING call | `pipeline._deserialize_proposal` called `Proposal(...)` while `Proposal` was imported only under `TYPE_CHECKING` — a runtime `NameError` on every checkpoint restore. | `Proposal` imported at runtime; the AST lock is green without an exemption. |
| §3.5 single writer | `coverage report` opened DuckDB directly. | Rewritten through `RecordStore` (`latest_run_id`, `query_records`, record fields); `duckdb` no longer appears outside the store. |
| §3.6 MNIST literals | `create_campaign_yaml` hard-coded `784` / `10`. | Shapes resolved per task through `kernel.evaluate.task_shape`. |
| §3.7 vacuous guards | Three "NaN guard" tests asserted `isinstance(reason, str)`, which cannot fail; the EPC settle also leaked non-finite input without raising. | Tests inject a NaN batch and require `RuntimeError`; EPC gained the missing initial-activation guard. The lock now fails when the guard is removed. |
| §3.9 substrate sweep / timings | `substrate.sparsity` was never passed to the substrate factory; no stage timing reached the record. | Substrate kwargs are filtered by the declared `AxisSpec.accepted_params`; `PipelineRunner` stamps `stage_timings` into every recorded payload. The effect tests compare whole axis configs (`dataclasses.asdict`) instead of renamed fields, and generate ≤10/50 cells per case. |
| §3.11 unreachable primitive | `_filter_axes_for_validity` exempted every user-specified axis, so `instantaneous` survived beside `thermodynamic_contrast`. | Exemption removed: a declared primitive survives only if it participates in a legal combination of the declared space. User-axes locks still pass because their declared primitives are all reachable. |
| §3.12 budget utilization | `scripts/run_experiment._run_loop` could not persist any record (empty env + `unknown` dataset/SHA); the window assertion saw zero cells. | Same provenance fix as §3.2; the 3.6 s run measures cells and closes on the deadline. |
| §3.14 OperatingPoint | `from_question_first` silently ignored unknown operating-point keys. | Fail closed with `ValueError("unknown field(s) in operating point: …")`. |
| run ledger (design question) | The pipeline's S3 never called the policy at all: it consumed the cell stream directly, so a `ModelBasedPolicy` was indistinguishable from `StratifiedRandomPolicy`. | S3 now asks a `ModelBasedPolicy` for its proposals (the reserved exploit-policy path); walking policies still consume the stream. The two-policy lock passes with no assertion change. |
| §3.15/3.16/3.17/3.18 | The four remaining red files were all the same empty-`env` fixture defect. | Same helper; files green. |
| §4.3 non-TTY | Progress bars emitted escapes when stdout was piped. | Already landed at `18dee0b7`; unchanged. |
| §5.4 developers | Three developer-tooling sections lived in `acceleration.md`. | Folded into `developers.md` under one `### Kernel development, tooling, and registry locks` section; `acceleration.md` keeps only hardware acceleration. |
| G12 neutrality | The section was curated prose; its counts could drift. | New generators `identity_card_count`, `corrections_count`, `fairness_clause_count` read `IDENTITY_CARDS.md`, `CORRECTIONS.md`, `FAIRNESS_CONTRACT.md`; `neutral-evaluation.md` renders them. |
| timeout census | `test_stream_advances_lock` declared 300 s with a 60 s row; twelve acceptance/display markers were unrecorded (pre-existing drift). | Census rows updated/added; `test_timeout_marker_policy.py` is green (91). |

### Measurements / corrections to the plan

- The ablation and demo numbers from the first pass stand: control `0.4389`
  (not ≈0.87), four legal credit arms (no `thermodynamic_contrast` under
  `instantaneous`). Neither is a defect; both are measurements the plan's
  prose had estimated.
- `test_hyperparameter_effect_lock` is intrinsically expensive. The two
  effect tests now measure 135 s and 48 s (was >600 s / timeout) after
  limiting candidate pages and comparing configs instead of building full
  systems; both carry the required 600 s marker and census rows.

### Still open (honest ledger)

1. **§5.2** — the capability tables are not yet demoted to one. §5.3 is now
   generated: `docs/readme/readiness.md` renders §8 through
   `<!-- gen:readiness_ledger -->`, so the README follows the ledger.
2. **§3.19 per-rule counts** — the ratchet is green at 659 but the Register C
   per-rule breakdown is still hygiene-pass work.
3. **§4.3 grammar** — non-TTY output is fixed; the unified
   `space / price / budget / first cells` section grammar is not.
4. **§4.5 video** — `docs/DEMO.md` and `test_demo_script.py` are ready; the
   recording is an offline artefact, not a tree change.

### Gate state at the end of this pass

| Gate | State |
|---|---|
| G1 property shard | **2085 passed, 60 skipped, 25 xfailed, 1 xpassed, 0 failed, 0 errors** (442 s) — was 32 failed / 24 errors after the first pass |
| G2 unit + `test_v1_exit` | **551 passed, 1 xfailed** (149 s) |
| G3 promotion ladder | green |
| G4 demo screenplay | **2 passed** (72 s) |
| G5 README build | green after regeneration |
| G7 core help | green: 6 core / all under `--help-all` |
| G8 findings | green |
| G10 same cells | green |
| G11 identity cards | green |
| G12 generated neutrality | **green**: identity cards 31, corrections 2, contract F-1…F-6, and the §8 readiness ledger all rendered from source |
| G13 control | green under `max(3×chance, chance+0.2)`; the plan's ≈0.87 is stale (measured 0.4389) |

---

## 14. Third implementation pass (2026-10-17, close-out)

The second pass left four rows open. Three are closed here; the fourth (the
recording) is an offline artefact and is the only item this tree cannot
produce.

### Closed, by item

| Plan item | What was still wrong | Fix |
|---|---|---|
| §4.3 grammar | `--dry-run` printed metadata, then cells, then a price block whose budget line was buried inside it. | `PricePlan.render_price()` / `render_budget()` split the two facts; `_dry_run_report` now emits exactly `space / price / budget / first cells`, each as a headed section. Minutes are shown only when the total reaches a minute; a declared budget prints as `120s`. `test_dry_run_prints_a_plan_and_writes_nothing` now asserts the four sections, so the grammar is locked, not documented. |
| §5.2 overlapping tables | Three tables restated the six axes or the layer pitch: `title.md`'s Aspect table (verbatim duplicate of `what-is.md`), the cheatsheet's Quick Reference (same axes and counts as `ontology.md`), and the ML-library capability table (axis content again). | One table per job: `what-is.md` is the single capability inventory (library / kernel / program, now carrying rules, substrates, objectives and governance), `ontology.md` is the single axis table, and the cheatsheet keeps only the panel counts. The ML-library section became prose plus the instruments that are *not* axes (EMA harvest, recipe cards, I(C,U), frozen-θ, P-axis probes, distributed execution), so no unique row was lost. |
| §5.6 demo link | `docs/DEMO.md` was reachable from no README snippet, and the `#machine-learning-library` anchor pointed at a heading that did not exist. | The ml-library heading is now `## Machine learning library` (anchor resolves); `start-here.md` links the shot list and the acceptance test that executes it. |
| §3.19 Register C census | The ratchet was re-baselined but the per-rule counts were not recorded. | §8 now carries a `Register C` ledger block with all 67 rule counts (650 findings measured under ruff 0.16.10; the 31 rules ≥5 are listed, the 36-rule tail totals 63). `BASELINE` stays 659 — the census is lower than the baseline, so the ratchet direction is unchanged. |

### Evidence (this pass)

| Check | Result |
|---|---|
| `test_readme_build_lock` + `test_cli_readme_lock` + `test_findings_lock` | **29 passed** (10.2 s) after regeneration |
| `test_price_oracle_lock` + `test_ablation_lock` + `test_cli_surface_lock` | **51 passed** (28.2 s) |
| `pytest -m demo tests/acceptance/test_demo_script.py` | **2 passed** (70.8 s) |
| `ruff format` / `ruff check` on changed files | formatted; no new findings in the changed regions (pricing and the lock are clean; `surface/cli.py`'s existing Register C findings are untouched) |

### Remaining work, stated plainly

1. **The recording.** `docs/DEMO.md` is the shot list and
   `test_demo_script.py` executes every command, so the video is the only
   deliverable that can still be missing from a tree that passes its gates.
2. **The plan's demo prose vs the measured numbers.** Two figures in §4.2 and
   §6 are estimates the tree disproved and this progress record keeps visible:
   the control reaches `0.4389` (not ≈0.87) and the sweep has **four** legal
   arms (no `thermodynamic_contrast` under `instantaneous`). Neither is a
   defect; the demo prints the measured values.
3. **The demo's projected total is small against its measured walltime**
   (`projected total: 1.3s` vs ~31 s measured). The price is computed from the
   `dynamics_cost.py` regime (`hd=64`, L0, 1 epoch, `batch_limit=2`) while the
   demo runs L1 × 3 epochs full-batch; the fixed 30 s run cost is printed but
   excluded from the total. Beat 1's sentence should not claim the total is the
   demo's walltime. Re-pricing the demo regime is a probe task, not a code fix.
4. **§3.19's 650 findings remain**; the census makes the hygiene pass sized,
   not done.

### Gate state at close

| Gate | State |
|---|---|
| G1 property shard | green at the end of the second pass (2085 passed, 0 failed, 0 errors); the only code touched since is the dry-run renderer, whose locks are green above |
| G2 unit + `test_v1_exit` | green at the end of the second pass (551 passed, 1 xfailed) |
| G4 demo screenplay | **2 passed** (70.8 s) |
| G5 README build | green after regeneration |
| G7 core help | green (6 core, all under `--help-all`) |
| G8 findings | green |
| G10 same cells | green |
| G11 identity cards | green |
| G12 generated neutrality | green |
| G13 control | green (`0.4389 > 0.30`) |

No TODO67 is opened. The only unbuilt item named by §9 is the recording.

---

## 15. Fourth implementation pass (2026-10-17, priors and presentation)

The tree passed its gates at the end of §14. This pass removes one architecture
smell that measurement exposed and finishes the README's editorial restructuring.

### The prior registry: a column that did nothing

`step_size_override_<dynamics>_<credit>` was a prior family of **29 rows**, each
a multiplier applied to `ParameterUpdateConfig.step_size` *after* the factory
built the config (`ontology/update.py::_apply_step_size_overrides`). TODO48b R4
had already measured every original multiplier as an unmeasured attenuation and
re-registered the rows at `1.0`. At that point the mechanism was an identity
transform with three costs: it polluted the cheatsheet's prior count (72 rows,
44 of them dead), it bypassed the schema seam (a value changed after the
hyperparameter declaration cannot be seen by `harvest_schema` or the phantom-knob
detector), and it made 12 update factories accept `dynamics`/`credit` arguments
they never needed.

**Fixed by deletion, not annotation:**

- the 29 multiplier rows, `_apply_step_size_overrides`, the `dynamics`/`credit`
  kwargs on all 12 update factories, and the compose call site are gone;
- 12 unread `step_size_*` rows and 3 unread optimizer priors (`adam_beta1`,
  `adam_beta2`, `muon_momentum`) are gone with them;
- the one live dynamics default was renamed `dynamics_step_size_default`, joining
  the two calibrated overrides in a single `dynamics_step_size_*` family;
- `PRIORS_REGISTRY` is now **28 rows, each with exactly one reader**: 23
  `ruler_lr_*` (via `get_ruler_lr`), 3 `dynamics_step_size_*` (via the schema
  declaration and `apply_dynamics_step_size`), 2 geometry size priors (declared
  by `geometry.py`);
- the retired finding is recorded as `docs/CORRECTIONS.md` Correction 3, the
  audit-only probe was reduced to the reproducible ladder (there is no longer a
  column to audit), and `test_no_step_size_multiplier_priors` keeps the column
  from returning.

**What a prior is, after this pass:** a named hyperparameter default — a
distribution and a center — declared once in `schema/seed_registries.PRIORS`,
resolved by `harvest._resolve_value` when a sweep does not supply a value, and
serialized into `docs/generated/priors.json`. It is not a hidden post-processing
step. A per-combination correction belongs in the schema declaration or in the
primitive, where the phantom-knob detector can see it.

`docs/generated/priors.json` was regenerated; the README's prior count follows.

### README and consortium documents

- `docs/readme/neutral-evaluation.md` moved from position 3 to the middle of the
  README (after core architecture, before validation) and was rewritten as the
  referee argument: why an inventor cannot be the referee, what procedure this
  project publishes, what it does not claim, and why a consortium is the
  institution shaped like the price gap. It links `docs/CONSORTIUM.md` and keeps
  the generated counts (G12).
- "Findings we own" left the README. The content is now
  `docs/FINDINGS.md`, a standalone page that names its source documents and
  locks; the readiness section and the two inline references link it.
  `test_findings_lock.py` (G8) now asserts the page quotes its documents *and*
  that the README links the page.
- `docs/CONSORTIUM.md` was rewritten as a one-page pitch: the structural
  problem, the referee apparatus already enforced, what a member gets, what a
  member accepts, the five honest gaps, and the invitation. The moral framing is
  still excluded; the argument is price and procedure.

### Evidence (this pass)

| Check | Result |
|---|---|
| `test_schema_seam_lock` + `test_harvest_schema_gate2_lock` + `test_wp10_learning_integration_lock` | **33 passed** (9.3 s) |
| `test_experiment_registries_wiring_lock` + `test_lazy_export_lock` + `test_schema_seam_lock` | **47 passed** (9.4 s) |
| `test_readme_build_lock` + `test_cli_readme_lock` | **26 passed** in the combined run; `test_findings_lock` **5 passed** after the page links were made repo-relative |
| `uv run comp run demo --dry-run` | six sections intact; four legal cells composed with the factory signature changes |
| `pyright` on the four changed library modules | **0 errors, 0 warnings** |
| `ruff format` / `ruff check` on changed files | formatted; only the three pre-existing `_dynamics.py` complexity findings remain |

### Remaining work, stated plainly

1. **The recording** — unchanged from §14: `docs/DEMO.md` and
   `test_demo_script.py` are ready; the video is an offline artefact.
2. **The demo prose numbers** — unchanged: control `0.4389` (not ≈0.87), four
   legal credit arms, and the printed price excludes the fixed run cost.
3. **§3.19's 650 lint findings** remain; the census sizes the hygiene pass, it
   does not perform it.
4. **The consortium logo is not designed.** `docs/CONSORTIUM.md` is text-only.
   A standardized "Computronium Consortium" mark is wanted (professional,
   neutral-referee motif — no algorithm family; SVG with light/dark variants
   under `docs/assets/`, linked from the page header). This is a design task,
   not a code task, and no broken image link should precede the asset.
