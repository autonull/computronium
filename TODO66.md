# TODO66 — Conclude the Project: Make It Run, Show It, Hand It Over

**Status:** Terminal plan. This closes development.
**Predecessor:** TODO65 (wiring + repair). TODO65 §9 declared v1.0 "wired and verified"; §1 of this
document measures that declaration against the tree and finds it partly true, partly asserted.
**Scope:** **No new engine capability.** Repairs, consolidation, presentation, documentation, and one
recording. Everything here either makes an existing promise true or removes a promise we cannot keep.

---

## 0. What "finished" means

Five sentences, each testable:

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

**"100% runnable" is scoped to user-facing paths** — the CLI surface, the documented library API, and
the demo screenplay. It is not a claim that every experimental research programme in §8 has been run.

### 0.1 Three audiences, three falsifiable statements

The project serves three people, and each gets a test, not a paragraph.

| Audience | They must be able to… | Test |
|---|---|---|
| **ML library user** | `uv sync`, paste the README's 60-second snippet, train a 6-axis system | `test_demo_compose_6axis` — **verified green, 15.4 s** (see §1.1); snippet locked to source by `scripts/readme_snippets.json` |
| **Researcher** | point the engine at a config, get records, a report, and a verdict that says either `PASSED`, `REJECTED`, or `INSUFFICIENT` | §6.G3 + §6.G4 |
| **Contributor** | add one ontology primitive by following README alone, and see where the project wants to go next | §5.8 + §6.G8 |

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

### 4.2 The `demo` profile (data, not code)
A `RunProfile` row — the config surface exists for exactly this. Regime chosen so beat 4 produces an
*discriminating* verdict and the whole run fits a video:

- task `digits`, full batches (`batch_limit=0`), `epochs=3`, **`n_seeds=5`** (the claim floor,
  `claims.py:37`);
- credit ∈ {`gradient`, `random_projections`, `pepita`} × update ∈ {`adam`, `muon`} → 6 cells;
- objectives `("validation_accuracy", "walltime_total")`;
- `budget_seconds` sized from the dry-run's own projection, not a guess.

Target: **≤180 s on CPU** and ≥1 honest verdict per cell. If 180 s is not achievable, reduce to 4
cells — never raise `batch_limit` to fake speed.

**The payoff is not "a win".** An earlier draft of this section asked the regime to deliver "at least
one axis value measurably ahead so the video has a finding". That is selection bias with a nicer name:
choosing the cell count until a difference appears is precisely what the project's statistical gates
exist to prevent, and doing it in the *demonstration* would discredit every other number in the report.
The demo's payoff is instead:

1. **The ablation table** — every credit rule measured, with `n` and `std`, no winner declared.
2. **The verdict** — `PASSED`, `REJECTED`, or `INSUFFICIENT`, with `power_achieved` printed.
3. **The price of an answer** — beat 4 multiplies the power requirement (`63` seeds/group for d=0.5,
   §2.1) by the dry-run's priced cell, and states the walltime and GPU-hours an *actual* claim about
   this axis would cost, on this machine.

That third line is the most valuable sentence in the video: it tells the viewer what a real answer
costs and why the project refuses to pretend it has one.

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
| **G10** the demo run twice from a clean store produces the same `replay_hash` | determinism, i.e. the only basis for "you can reproduce my result" (§11 ceiling) |

Per commit: G6 always; G4–G5 when the surface or README moves; G1 only at the two close points.
**Never** `pytest tests/`. **Never** re-run a green shard to confirm.

---

## 7. Order of work

| Phase | Work | Exit |
|---|---|---|
| **A** | §2.5 → §2.7 → §2.8 (map + imports; the 35-failure cluster) | those four locks green |
| **B** | §2.1 → §2.2 → §2.4 (the ladder; G3) | a `comp run` that emits an honest verdict |
| **C** | §2.3, §2.6 (crash + isolation decision) | `coverage report` exits 0 |
| **D** | §3.1–§3.18 (shard tail) | G1 first run: 0 failed |
| **E** | §3.19 (deliberate re-baseline + §8 row) | ratchet green |
| **F** | §4.2 `demo` profile; §4.3 polish; §4.4 grouping | `comp demo` runs in ≤180 s, G10 green |
| **G** | §4.5 screenplay + `test_demo_script.py`; §4.6 research beats | G4 green; video shot |
| **H** | §5 README consolidation + §5.8–5.10 + regenerate | G5, G8, G9 green |
| **I** | Close: G1 second run, G2, G7; tag; update this file | 0 red |

A–C are the same afternoon. D is the long tail. F–H is the presentation.

---

## 8. Readiness ledger — what we hand over, and what we do not

Append to TODO65 §5; it remains the durable answer to "what could this eventually be?". This table is
generated into README §5.3, so it cannot drift.

**Live (user path):** loop + 11 stages · 8 proposal policies · DoE · ICU metamodel · allocator ·
statistical promotion · multi-objective/Pareto · baselines/ruler · evidence store, three-tier status,
claims, limitations · CEEC export · provenance/seed/checkpoint · reports (text/JSON/HTML) · `comp`
core commands.

**Designed, not built (intent preserved):** M1 gate calibration · M2 drift detection · M3 metric
coverage warnings · `capabilities` command · per-stage timing defects · repo-wide effect lock ·
silent-drop detector · C12 ruler-geometry fallback · `defect revoke` re-probe · policy-aware
compatibility sampling · `SystemConfig.validate` codegen.

**Planned (intent, no code):** 7-domain task expansion (cifar100, svhn, wikitext2, penn_treebank,
mountain_car, lunar_lander, diabetes, california_housing, ett_h1, PDE suites) · physical-hardware
validation (memristive/neuromorphic/optical/quantum) · Ray/SLURM · DDP at scale · `campaign_queue` as
loop driver · full CEEC integration · `question_first` literature store · a real TUI.

**Retired (finding kept):** E1 deep chaotic unfolding — **falsified**, mechanism boundary is
composition-error compounding · older "ρ(J)=estimator" claims (`docs/CORRECTIONS.md`) · legacy
`experiment/cli` runners · the `execution/budget.py` stub (wrong API, deleted §2.5) · Register C: 659
legacy lint findings, counted per rule, ratcheted not cleaned (§3.19).

**Results we actually own (the discovery output, to date):** deep EqProp boundary — multi-layer vanilla
EqProp does not learn (vanishing contrastive signal, slope −1.19, R²=0.80); DirectedEP restores the
signal without restoring accuracy (9.2% at depth ≥3, gate G2 FAILED); 1-layer EqProp viable
(`docs/eqprop_deep_limitation.md`) · phantom-knob class + detector (`docs/phantom_knob_audit.md`) ·
ρ(J)/σ_max conflation caught and corrected, three separated estimators, pre-correction frontier numbers
flagged `requires_rerun` (`docs/CORRECTIONS.md`, `test_jacobian_amplification`).

**The handover claim.** What ships is a *laboratory*, not a result: a composable six-axis system, an
experiment kernel that records what it measured and refuses to overclaim, a demo that shows both, and
three findings — two negative, one methodological — that survived the project's own audits. Every
stronger claim is a ledger row with a name. That is the maximum value available without new features,
and it is worth showing.

---

## 9. Definition of done

- [ ] §2.1–§2.8 repaired; each with the lock that prevents its return.
- [ ] `comp run demo` produces ≥1 claim with `n` and variance on CPU in ≤180 s, from a clean tree.
- [ ] `comp coverage report` exits 0.
- [ ] Every demo-script command exits 0; `test_demo_script.py` green.
- [ ] Property shard: **0 failed, 0 errors**. Unit + acceptance green.
- [ ] `test_readme_build_lock` green; README's first screen is the six-command product path.
- [ ] `README.md` contains no claim the report cannot emit.
- [ ] `comp --help` ≤6 core commands; all reachable under `--help-all`.
- [ ] `docs/DEMO.md` exists; video recorded; length ≤6 min; every command on screen is in the script.
- [ ] The video's closing beats quote the three results in §1.2, numbers unchanged from their documents.
- [ ] README alone lets a contributor add one primitive (§5.8) and find a named next step (§5.10).
- [ ] §8 ledger complete; every unimplemented capability named.
- [ ] `TODO65.md` and this file carry a final progress section; no TODO67 is opened.
- [ ] Tagged.

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
2. **External validation.** Nobody outside this repository has run it. The deliverable is
   *reproducibility in principle* — G10's replay hash and the demo script — not evidence that anyone
   reproduced it.
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
