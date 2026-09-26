# TODO35: The Proveable Remainder

**Status**: **ACTIVE — open.** This document owns every open item as of
**A new session works from the Round 4 brief in §0 below, and stops there.**
made fast, provable and ready to be presented; its "Remaining Work" section is
replaced by a pointer here, because two live open-item lists is the drift this
plan series has documented five times.

**Round 3 closed**: §1.2 (the three highest-fan-in modules are at 0 — and
the third of them held an `ImportError` on a live branch that no test had
ever taken), §11.6-1, and two wiring locks whose guard against a second
Protocol was a spelled-out name. The round's output is a defect *class*, not
a count: **F821 cannot see an import of a name the module does not define**,
and the scan that can see it found six more in eight modules that no gate
was looking at. §12.5 also records that the fast-lane walltime this series
has been quoting is not reproducible, and should stop being quoted.

**Round 2 closed**: §10.8-1 (with its mechanism *corrected* — the suite was
never nondeterministic, it was environment-dependent, and the pin that claimed
otherwise sat below the `import torch` that made it a no-op), §10.8-2,
§10.8-3, §10.8-4, §1.2's measurement, and a `pre-commit` config that had never
parsed. §1.2's three modules to zero is untouched. The finding of Round 2
matches Round 1's: claims in this tree drift from the code silently, and the
two that were wrong *about a defect* were wrong in the direction that made the
defect look like bad luck.

**Round 1 closed**: §1.1, §1.4, §1.6, §1.7, §1.8, §1.3 (PLW0717 89 → 81),
§1.5 + §2.2, §2.1, §2.3 (decided, not moved), §3.1, §3.2, §3.3. Four new
items were found by doing them and are in §10. The short version: the cheap
tier was as full of holes as the plan claimed, and **three of the four new
items are claims that had been silently wrong since a commit three weeks
old** — the pattern this series exists to end keeps reproducing itself.

Continues `TODO34` (test velocity, correctness hardening, the presentation
layer). Where `TODO34` removed the defects, this one closes what the removal
*revealed* and takes the decisions `TODO34` deliberately deferred.

**Read this, not `TODO34`'s section numbering.** The section numbers here are
local to this document; `TODO34` §-numbers are cited only where an item was
moved from there.

---

## 0. Round 4 brief — read this; everything below is history, not the work list

State: tree clean at `88e21d1f`. Round 3 closed (§12).

### 0.1 The rule

**The code is its own correctness guard.** A guard in a test protects one
test run; a guard in the code protects every caller, including the ones
nobody wrote a test for. In order:

1. Fix the cause in library code.
2. Make the library fail fast at its own boundary (import-time or
   construction-time), so the defect is caught by *every* existing test.
3. A test or lock only for what genuinely cannot live in code.

Never the reverse. Adding a lock is not a fix, and a falling count is not
progress (§14.2 has the arithmetic behind that).

**Two rules from §14.6.** A static import graph does not contain README
tables, `python -m` invocations or CLI scripts, so "0 importers" is the
expected shape of a *live* entry point and is never a reason to delete.
And run the fast lane after a change, not before the next one.

### 0.2 The work, in order — causes, not counts

| # | Cause | Done when |
|---|---|---|
| **1** | The package never checks its own public surface, so five documented entry points raise `ImportError` and no gate sees it | An **import-time surface assertion** in `computronium/__init__.py`: every name in `__all__` and every README-documented module resolves. In the code, so every test importing the package inherits it. First because it is both the health number and the guard for 2–3 |
| **2** | `CoreTrainer`/`TrainerConfig` were replaced in Sprint 7.6.10 and 10 call sites were never repointed — they rotted together because the shared entry point was never extracted | `train_task(model_factory, task, epochs)` in `core/system_trainer/`, then all 10 repointed. One site proven with a test before the other nine. `python -m computronium.experiments.cross_domain_transfer` (`README.md:1253`) runs |
| **3** | 81 `PLW0717` long functions: `acceleration/triton_kernels.py` (5), `execution/synthesizer.py` (4), `execution/_state.py` (3), `execution/robustness.py` (3), `autoscientist/local_llm.py` (3) | Taken in bulk as **extraction**, never suppression. The `p2p` precedent: extraction finds live crashes |
| **4** | Global per-test `timeout = 120` (`pyproject.toml:190`); the slowest test has ~30s margin and no marker of its own | Per-test margins measured, then a marker or a raise. May close §6 |
| **5** | §7 quotes a fast-lane walltime that does not reproduce on this machine | Three back-to-back runs, record a **spread**, quote a range. Test count is the metric, not walltime |
| **6** | Two pre-existing failures that pass alone and fail in a 3-tier `-n 4` run | Cause named, or filed as environmental. Not a regression — do not re-chase per run |
| **7** | `test_undefined_name_lock.py` covers 2 of 15 layers because 13 files fail it | Full-tree scope, or a written blocker. Arrives free with 1 and 2 |

### 0.3 Not this round

`§4` presentation layer — no consumer; but the honest question is whether
the absence of a watchable run is *why* nothing needs it. First question
here a lock cannot answer. `§1.9`'s two test-quality rules — **decision:
leave unwritten.** `p2p/` tests, `TODO34` §5.4's export half, repo-root
scratch, `E402`/`SIM102` — reasons in §3.4 and §5.

### 0.4 Reporting

One number per item as it lands. No interim narration. If an item is
bigger than it looks, say so once and move on.

---

## 0. The rule this document is built on

`TODO34`'s through-line, after sixteen passes, is one sentence: **when
something claims to work, make the claim executable.** Every lock in
`tests/property/` is that instinct applied to a claim, and the ratchet, the
provenance lock, the shadowing lock and the wheel assertion each found a real
defect on their first run. The corollary, which cost `TODO34` two of its own
passes, is the standing instruction for anything below:

> A lock's **population assertion** is part of the lock, not an optional
> extra. If the thing a lock counts is what the fix removes, the guard must be
> re-expressed against a population the fix does *not* remove — in the same
> commit that empties the count.

`TODO34` §1.5 is the worked example: closing 116 unseeded tests destroyed the
assertion that proved the scan was still working, and the guard had to move
from "≥100 flagged" to "≥2,773 test functions scanned, 463 drawing from the
global RNG".

---

## 1. Tier 1 — cheap, and each closes a hole that is already open

Ordered by what it costs to be wrong, not by section number.

| # | Item | State (measured 2026-09-26) | First move | Effort | Done when |
|---|---|---|---|---|---|
| 1.1 | **The reference "full suite" silently omits `tests/acceleration`** | `scripts/run_tiered_suite.sh` runs `TIERS="unit primitives algorithms graph ceec platform property integration"` — **`acceleration` is not in the list**, so the 210 tests under it never run in the full-suite pass or in the slow pass (no `slow` marker). That is the whole Triton/FA kernel suite and §2.7's activation-contract lock. The *fast lane* catches them (`testpaths` includes it), which is why this has survived: the inner loop is complete and the round-close figure is short | Add `acceleration` to `TIERS`, and add the §0 population assertion to the runner: a tier that is not in the list is a silent skip, which is exactly what `TODO34` §1.2b fixed for the 26 (now **34**) slow tests one pass ago. Same defect class, one pass later | ~15min | `TIERS` covers every directory under `tests/` that is not `slow`, and a lock fails if a new test directory is not in the list |
| 1.2 | **pyright: the top modules by fan-in** | **CLOSED in Round 3 (§12.1)** — the three named modules are at 0. Originally 2,079 findings repo-wide. `pre-commit` gates pyright on `computronium/ontology` only | Re-count per module before picking: `TODO34` Pass 16 took `p2p/evolution.py` from 16 → 0 *inside an unrelated extraction*, so the fan-in ranking is a guess until measured. Then drive the top 3 to zero and widen the pre-commit hook to changed files, the way ruff's already is | ~4h + ongoing | 3 modules report 0; the pre-commit pyright hook reads its filenames instead of hardcoding one directory |
| 1.3 | **Lint tranche 2** | **349** findings (ratchet baseline 353, ruff 0.16.6). By rule: `RUF105` 148, `PLW0717` **89**, `E402` 32, `SIM102` 19, `PLR0913` 8, `C901` 5, rest ≤6 | Take `PLW0717` next: `knowledge/causal.py` holds 4 (16/39/9/29 statements) and `hyperopt/experiment.py` 3. The `p2p` extraction is the recipe and the precedent — it found a live crash. **Leave `E402` and `SIM102` alone** (see §3.4) | ~3h | count falls with no new suppression; the ratchet moves down with it |
| 1.4 | **`rich` is a declared hard dependency and three library modules import it** | `pyproject.toml` lists `rich` in `[project] dependencies`; `hyperopt/_dashboard.py`, `execution/dashboard/_rich.py` and a third module import it at module scope. `TODO34` §2.9 deferred this "until something uses it" — that condition is now **met**, and the layering lock still shows no renderer on `import computronium`, so the declaration is louder than the behaviour *and* the deferral's condition is gone | Move `rich` to an extra (`pyproject.toml` only — no code change), and let `test_layering_lock.py::test_import_computronium_pulls_no_renderer` keep proving the property holds. This is the cheap half of a decision that has been open for two plans because its own precondition never got re-checked | ~15min | `rich` is not in `[project] dependencies`; the import lock still passes |
| 1.5 | **Environment fingerprint in run records** | `capture_environment()` / `deps_hash()` exist and are **used** — `cli/repro.py` writes `deps_hash` into its own repro record, and `z3_fixed_weights.py` calls `capture_environment()`. The gap is narrower and sharper: the **run-record emitter** does not. `emit_run_record` is the fixture at `tests/integration/conftest.py:58`, and its `provenance` carries exactly two keys, `git_commit` and `config_sha256` | Add a third key from `deps_hash(capture_environment())`, then re-emit every record in the one slow pass that §2.1 also needs — backfilling a version into an existing record is **fabricating** provenance, so it cannot be done piecemeal. **Sequencing note**: `test_provenance_keys_are_exactly_the_emitter_contract` asserts the key set is exactly two, so the lock and the emitter must move in the same commit, and the lock is the *right* thing to update here — it is encoding the old contract, not defending it | ~1h + the slow pass | a drift lock can say which of code / config / environment moved |
| 1.6 | **`pre-commit` invokes pytest wrongly** | the hook's entry is `uv run pytest tests/property/ -q`. `AGENTS.md` says **always** `uv run python -m pytest` — bare `pytest` picks up the user-site interpreter and breaks collection on protobuf gencode skew | One-line fix. The rule is written down precisely because it was learned the expensive way, and the hook that runs most often does not follow it | ~5min | the hook entry is `uv run python -m pytest` |
| 1.7 | **cwd-relative defaults in `scripts/`** | `scripts/visualize_atlas.py:23` and `scripts/g1_core_sweep.py:36` both default to `Path("artifacts/ruler_table.json")`. **The sharper fact**: `artifacts/` is gitignored and that file is untracked — it is a *stale local copy* left from before the table moved into the package. The defaults resolve on this machine only because of that leftover; a fresh clone has no `artifacts/` at all, so both scripts break there | One scan for `Path("<literal>")` defaults under `scripts/`, as a fast-lane lock, and point the two sites at the packaged table via the existing `campaign._ruler_table_path()`. This is the third instance of one class; the class is what is worth locking, not the two sites | ~40min | the scan runs, with the population assertion it needs to be a lock |

### 1.8 Two of `TODO34`'s demo items never closed

Both are `TODO34` §1.2/§1.3 sub-items that were folded into "demoted to slow"
and then not carried forward. They are open work, not finished work:

- **`test_demo_update_ladder`'s `SEEDS` lever is unmeasured.** `SEEDS = (0, 1, 2)`
  is still 3. `TODO34` concluded that `STEPS` is *not* a free lever (any cut is
  a re-pin, not a speedup) and that the one honest lever is `SEEDS 3 → 2` — but
  that weakens the ± range the H4 re-pin depends on, so it needs the **per-seed
  spread measured first**. One run of the existing three seeds prints it; the
  decision is then a number rather than a preference. Do not change `SEEDS`
  before the spread is in hand.
- **The ladder and `ntm_local` are `slow`-marked, so the default profile no
  longer verifies the manifest pin** they exist to verify. That is an accepted
  trade only because `./scripts/run_tiered_suite.sh --with-slow` exists — and
  §1.1 is about that same runner. Fix the runner, then run it.

### 1.9 The last two test-quality rules from `TODO34` §2.5

`TODO34` landed two of the four and left two unwritten; both were closed as
"needs dataflow" / "cheap by eye" at the time, and neither has been revisited:

- **Environment-dependent rendering asserts.** A terminal-width or
  Rich-rendering assertion must pin its width, because it failed under `pytest -n`
  and nowhere else. The dashboard that had that failure is gone, so there is
  nothing left to fix — but nothing now *prevents* the next one.
- **A test that asserts the opposite of its name.** `TODO34` fixed one such test
  by hand. It remains the cheapest defect class in the document to write a
  detector for, and the detector is the only version that generalises.

Both are honest Tier-1 candidates **if** a consumer wants them: neither has a
failure attached to it today, and this plan's own rule is that a lock with no
defect behind it is a lock that gets switched off. `TODO34` §2.5's own log
records that rule being applied against a proposed rule with 14 false positives.
**Recommendation: leave both unwritten, and record that as the decision** rather
than leaving them as an omission.

### A note, not an item: the stale language-server index

`TODO34` recorded that the NiceGUI removal left a language-server index
pointing at deleted `computronium/ui/**` files. That is an editor cache, not a
repo defect — a clean LSP restart clears it and `git ls-files computronium/ui`
is empty. It is listed here only so the next reader does not "fix" it in the
tree.

---

## 2. Tier 2 — needs one quiet window, and one pass to amortise

These three share a single expensive run. Take them together or not at all;
sequencing them separately costs two quiet windows for no extra signal.

| # | Item | State | What the shared pass does | Effort |
|---|---|---|---|---|
| 2.1 | **Re-baseline the cost table** (`TODO34` §1.6) | the recorded numbers predate the settle-horizon fix, which made every settle run its full budget. The table is therefore *known* stale, not merely old | one `./scripts/run_tiered_suite.sh --with-slow`. The runner already passes `--durations=20` itself and **ignores any second argument** — `--with-slow --durations=20` would run and silently drop the flag, which is why this is written as the command that is actually read | ~30min machine |
| 2.2 | **Environment fingerprint** (§1.5 above) | needs every demo re-run to be honest | the same pass re-emits the records | folded in |
| 2.3 | **`docs/archive/` policy, and the plans at the repo root** | 5.1M across 11 dated directories; one archival pass already happened (`0c8e5a2a`); no rule recorded | decide in-tree vs cold store, write the rule in three lines, apply it | ~30min |

**The rule, once written, should cover the plans at the repo root too.**
There are **43 `TODO*.md` files (2.4M) sitting beside the code**, of which
roughly 40 are finished series, and the newest archival pass moved superseded
*docs* without touching them. A plan series is a document like any other: the
root is for the live one. Proposal, to be accepted or rejected in three lines
— **exactly one `TODO*.md` at the root; everything finished moves to
`docs/archive/TODO/` by round, with the series number preserved.** This is the
`checkpoints/` decision applied to a directory that is tracked: the question is
not "is it big" but "does a reader know which one is live".

**On measurement capacity** (`TODO34` §2.8, still binding): individual
commands over ~15s are not affordable on this box. A single-process full-suite
run is OOM-killed; a 200s demo run was killed three times. Background long
runs to `logs/<name>.log` and poll at ≤2min, and **check for the pytest summary
line, not the process** — a killed background run leaves no trace, and
`pgrep -f <testname>` matches the polling command itself.

---

## 3. Tier 3 — decisions, not work

Each of these is a question that the code can answer cheaply and that no
amount of reading will answer. They are grouped because taking two together
pays the audit once.

### 3.1 Does `StateDynamicsConfig.max_steps` apply to *model* settling?

`computronium/core/local_learning/settling.py` carries its own settle loops at
~397 and ~439 — model-level fixed-point settling with its own `steps_taken`,
`convergence_start` and a custom `_check_converged` hook. These are the same
contract `TODO34` §2.2 states normatively, re-implemented for a layer the
protocol does not cover. (The third loop, ~1150, is an adjoint sweep for
implicit differentiation and is genuinely a different thing — leave it.)

They are **not** migrated blindly: `local_learning` settles user-supplied
models whose `_step` is `object`-typed and may checkpoint internally, so only
the driver's `SettleIterate` box would transfer unchanged.

**The question**: should the two share one contract? If yes, the driver is
free. If no, write that down in the module docstring, so the next reader does
not assume they are the same thing and "fix" one to match the other.

### 3.2 The LIF horizon counts layers, not steps

`SpikeIntegrationDynamics._settle_layered` integrates each layer against its
own already-settled drive, so a settle executes `max_steps` **per layer**: a
3-layer network reports `_settle_steps_used = 90` at `max_steps=30`. That is
true against `TODO34` §2.2's rule 2 ("counts steps actually executed") and
false against how every consumer reads it — `analysis/instruments.py` and
`autoscientist/campaign.py` both treat it as *a horizon*. A number three
times the configured horizon is a lie to a log reader even when the code is
right, and `test_settle_driver_lock.py` deliberately declines to assert
`horizon <= max_steps` rather than lock in the ambiguity.

**The question**: per-layer sum (today), per-layer max, or separate
`steps_used` / `layers` fields — then make the lock assert the choice.

### 3.3 Three `getattr` state accessors are now redundant

`_get_state_x` / `_get_state_activations` / `_get_state_free_state` in
`_dynamics.py` tolerate a state that might not carry the field. `StateLike` is
now `SettableState`, so the field is *guaranteed* and the accessor hides a type
error instead of surfacing one. Replacing them with direct reads is a small
diff **after one audit**: the lazy and compiled whole-graph paths pass
duck-typed records from outside the protocol's coverage, which is exactly the
assumption a mechanical sweep gets wrong. (`_get_state_dual_vars` was already
deleted — zero callers.)

### 3.4 `SIM102` (19) — a decision to *not* act, recorded so it is one

13 of the 19 are the `_validate_*` chains in `ontology/system.py`, where
collapsing `if a: if b: raise` into `if a and b:` keeps behaviour and loses
the one-branch-per-message structure the validators are read for. `E402` (32)
is the same shape: 32 hand-written per-site suppressions would be worse than 32
honest findings, and the imports are deliberate circular-import breaks. **Leave
both.** `TODO34`'s rule applies — a lock that needs a special case, the
special case is the finding.

---

## 4. Tier 4 — the presentation layer, and why it still has no consumer

`TODO34` §4 (4.2 live telemetry, 4.3 the read surface, 4.4 the renderer
registry) is unstarted and stays that way until something needs it. The
preconditions are now genuinely met — `on_step` fires every settle step
(§0.4 of `TODO34`), the layering rule has a lock behind it (`test_layering_lock.py`
enforces it over the AST including function-local imports), and rendering deps
are not import-time requirements. What is missing is not readiness, it is a
**consumer**: nothing in the tree is asking for a watchable run.

**Do not start these because they are ready.** They are ready, and ready is
not a reason. When a requirement arrives, move §4 plus §4.5's non-goals here
whole rather than re-deriving them, and take 4.2 first — it is the only item
whose substrate is a primitive that already exists.

---

## 5. Deferred, and why that is not the same as dropped

| Item | Why it is not being done | What would change it |
|---|---|---|
| **`p2p/` has no tests** | `P2PEvolution._evolution_loop` is a daemon whose only handler is `except Exception` + `sleep`. `TODO34` Pass 16 found a `TypeError` there that had been raising on every iteration since the signature was written — swallowed, with a log line as the only signal. The failure mode is silent *by construction*, and `p2p` has no consumer | the refactor made `_fetch_global_best` / `_build_model` / `_evaluate` separately callable, so a stub-DHT test is now cheap. When the mesh gets a consumer, this is a half-day, not a project |
| **`TODO33` §11 duplicate-strategy sweep** | the settle and credit contracts are pinned now, so the sweep *can* be judged on behaviour — but it needs the behaviour questions in §3 answered first, or it becomes another reading exercise | after §3 |
| **`TODO34` §5.4's export half** (generate `__all__` / `_LAZY` / `TYPE_CHECKING`) | these are *publication* surfaces, not registries. The dispatch tables were worth deriving because the information lives on the class; the export lists are what a user can import, the `TYPE_CHECKING` block is deliberately literal so pyright sees real imports, and the lazy map's per-name module attribution is not derivable from the subpackage `__all__`s. Generating them means generating-and-committing a file whose purpose is human/tool signal | a reader who wants the public API **smaller**. That is a product decision, not a refactor |
| **Repo-root scratch** (`build/` 7.5M, `dummy.db`, `execution_state.db`, `scientist.log`) | all four are correctly gitignored and all four are leftovers. Nothing is wrong with them and nothing depends on them | a disk-pressure pass. Low value, listed so the decision is recorded rather than re-made each time `du` is run |

---

## 6. The flake with no mechanism

`tests/property/test_deep_credit_trial.py::TestContrasts::test_contrasts_cover_deep_tier`
failed **once** during `TODO34` Pass 17, in a property-tier run that took
**217s** against a normal 75–95s. It then passed alone (132s), under `-n 4`
(46s), and in a clean full-tier run (81s). Its assertion is a *key-presence*
check — `_contrasts_vs_gradient` returns an empty dict only when
`len(config.seeds) < _MIN_CONTRAST_SEEDS`, and the test passes `seeds=(0, 1)` —
so on the face of it cannot fail from numerics, and it draws nothing unseeded,
so it is not in the §1.5 population. **The failure message was not captured.**

**Do not "fix" it without the message.** A threshold changed to accommodate an
unexplained failure is the exact mistake `TODO34` §1.1 made with a 0.78 floor
inside a measured oscillation band. When it recurs, capture it with
`-x --tb=long` and the run's walltime beside the assertion. If it does not
recur, it is a data point, not a task.

> **§13.1 supersedes the "if it does not recur" half of this.** It recurred
> in Round 3, and there is a candidate mechanism that was never checked
> because this section assumed — without the message — that the failure was
> an *assertion* failure. A global per-test `timeout = 120`
> (`pyproject.toml:190-192`) reports as `Timeout`, the offending test holds
> half the property tier, and it has been measured at 37.36s in-tier and
> 90.08s isolated. Read §13.1 item 1 before touching anything here.

---

## 7. Verification

Unchanged from `TODO34`, and still the shape every item here is gated by.

```bash
# Dev-env smoke — a stripped env fails here in seconds instead of mid-gate.
uv run python -c "import optuna, scipy, torchvision, pytest"

# Fast lane: the inner loop and the per-commit gate (pyproject testpaths).
# Measured 93s, 3323 passed, 119 skipped, 26 xfailed, 1 xpassed at 196eb4cd.
uv run python -m pytest tests/unit tests/property tests/primitives \
    tests/algorithms tests/acceleration -q -n 4

# Full suite, one process per tier, `-n 4`, logs at logs/tiers/<tier>.log.
# --with-slow is required at round close: 34 slow tests (measured 2026-09-26),
# including every demo that emits and pins a gallery record, are excluded by
# default. Pass ONLY this one flag -- the script reads $1 and ignores anything
# after it. NOTE: this command is currently short 210 tests, because
# `acceleration` is missing from the runner's tier list -- see TODO35 §1.1.
./scripts/run_tiered_suite.sh --with-slow

# Gates on changed files
uv run ruff format --check <changed>
uv run ruff check <changed>
uv run pyright <changed>            # strict for new/rewritten modules

# The lint ratchet is a gate too: it fails if the repo-wide count rises.
uv run python -m pytest tests/property/test_lint_count_ratchet.py -q
```

`F821` and the `TYPE_CHECKING`-import hazard are enforced in the fast lane by
`tests/property/test_undefined_name_lock.py` and by
`test_type_checking_imports_are_not_called_at_runtime` inside
`tests/property/test_state_algebra_lock.py` (a *test*, not a file — the two
have confused at least one reader already). The explicit `--select F821` run is
for iterating on a fix, not for the gate. Provenance
has its own fast-lane lock over the *committed* records
(`test_gallery_provenance_lock.py`), separate from the round-close gallery
lock, because provenance that decays between round closes needs a per-commit
gate.

**Re-pin `docs/figures/manifest.json` whenever demo numerics move, and say so
in the commit body — including when the answer is "none", which is the claim
worth making.**

---

## 8. What this plan is deliberately not

- **Not optimisation.** The fast lane is ~93s and the two 200s+ demos are
  `slow`-marked. The suite got *heavier* because a correctness fix made settles
  run their full horizon; optimising that would optimise the artifact the fix
  improved.
- **Not more structure.** Three of `TODO34`'s last four passes were config and
  dead code, not architecture. `TODO35` opens with a lint tranche, not a
  refactor, and that is the same judgement.
- **Not `RUF105/106/103` enabled piecemeal.** The 148 `# ruff: ignore` →
  canonical-form migration is Register C work, as **one** change; enabling
  individual rules only churns guard-rails.

## 9. Notes carried forward

The transferable results of `TODO34`, restated in one line each, because the
pattern is worth more than any single fix in it.

- **A defect found by making a path callable is a defect class of its own.**
  Four defects, one untested function, zero visible from outside.
- **A lint finding is a to-do list; the extraction it prompts is a probe.** The
  worst `try:` in the tree held a `TypeError` that had never once surfaced.
- **A hand-kept table does not fail; it accumulates accommodations.** The
  missing dispatch key was found by a *test* that had grown a special case
  routing around it — the special case was the finding.
- **A helper can be the vacuous test.** A `getmembers` scan resolved zero of
  thirteen classmethods and its caller asserted over the empty dict
  indefinitely. Assertions on a scan's population belong in the test.
- **A source lock cannot see an omission.** Four settle paths never wrote the
  field the source lock proved they must write. Pair every structural lock with
  a behavioural one that *calls* the thing.
- **A binding that exists only for the type checker is not a binding.** Linters
  check names; only a test can check *when* a name exists.
- **A threshold fixed without a measurement is a guess wearing a
  measurement's clothes.** Re-derive thresholds from curves, never from a
  docstring that describes a curve.
- **A closure that removes behaviour needs a behavioural test.** A
  seed-folding performance fix that changed results was caught by a golden-file
  regression test, not by the benchmark that motivated it.


---

## 10. Round 1 — what closed, and what closing it found

Closed at `31be91a0`. The tables above stay as written: they are the audit,
and an audit edited after the fact is a press release. This section is the
receipt.

### Closed

| Item | What landed |
|---|---|
| §1.1 | `run_tiered_suite.sh` derives its tiers from `tests/` instead of a hand list, resolves the repo root from `$0`, and `tests/property/test_tier_coverage_lock.py` keeps the derivation honest — including the population assertion and a recursive (not top-level) test-file check, because `algorithms` and `primitives` hold subpackage suites |
| §1.3 | PLW0717 **89 → 81**, no new suppressions. `knowledge/causal.py` 4 → 0, `hyperopt/experiment.py` 3 → 0. Ratchet baseline 353 → 334; pyright on `causal.py` 46 → 35 |
| §1.4 | `rich` moved to a new `console` extra (and into `full`); dev carries it. The layering lock still passes |
| §1.5 + §2.2 | `env_sha256` added to the run-record emitter and **read** by the provenance lock against the current environment. All 29 records re-emitted in the one slow pass, manifest re-pinned |
| §1.6 | the pre-commit hook is `uv run python -m pytest` |
| §1.7 | both ruler-table defaults point at `campaign._ruler_table_path()`; `test_script_path_defaults_lock.py` locks the *class* (a default shadowing a tracked file), scoped to shadowing precisely so that `results/foo` is not flagged |
| §1.8 | spread measured from the committed record's own per-seed values — see below. **SEEDS stays 3** |
| §2.1 | cost table re-baselined — see below |
| §2.3 | decided: in-tree, no cold store; the 42-file move is **rejected** — see below |
| §3.1 | decision written down: `local_learning/settling.py`'s docstring now says its duplication of the ontology settle contract is deliberate and why the driver's `SettleIterate` box would not transfer |
| §3.2 | `_settle_steps_used` stays the total; `_settle_horizon` (a property over the config, so `InstantaneousDynamics` reports 1 and not a stale 0) and `_settle_layers` are reported beside it, campaign records carry them, and the driver lock asserts the bound the two imply |
| §3.3 | the three `getattr` accessors are deleted; `SettableState` guarantees the fields, pyright on `_dynamics.py` is 0 |

Plus, found by doing the above: **`cpu_only` was a declared marker read by
nothing**, and the `device` fixture ignored it. It now forces CPU — see §10.2.

### 10.1 §1.8's measurement, and the decision it forces

Per-seed spread, read off the committed D18 record rather than a fresh run:

| arm | mean | seeds | spread | rel |
|---|---|---|---|---|
| `epc_w32_muon` | 45.25 | 46.21 / 44.31 / 45.24 | 1.90 | 4.2% |
| `epc_w32_unit_rms` | 42.48 | 41.67 / 41.91 / 43.85 | 2.18 | 5.1% |
| `epc_w64_muon` | 37.14 | 35.89 / 36.58 / 38.94 | 3.05 | 8.2% |
| `epc_w64_unit_rms` | 33.80 | 36.49 / 34.25 / 30.67 | 5.82 | **17.2%** |

**The margin is inside the noise.** UnitRMS beats Muon by 9% at w64 (33.80 vs
37.14) against a 17.2% per-seed spread on the UnitRMS arm itself, and by 6% at
w32 against 5.1%. So `SEEDS 3 → 2` — the one lever `TODO34` identified — would
make the claim *worse*, not cheaper: the band does not shrink with fewer
samples, and the point estimate is unchanged. The lever is rejected on the
measurement, and `SEEDS` stays 3.

What the demo now asserts alongside the verdict is the band, not a stronger
verdict: `max(seeds) - min(seeds) < 0.25 * muon_mean`, so if the UnitRMS arm's
own spread grows past a quarter of the comparison it fails as *no longer the
same measurement* rather than silently reporting a margin that means nothing.
The honest statement of D18's H4 re-pin is "UnitRMS trains ePC at both widths
and does not exceed Muon in 3 seeds", not "UnitRMS beats Muon".

### 10.2 Three claims that had been wrong for weeks

This is the finding of the round, and it is the §0 rule recurring in a new
shape: the *test* was fine, the *claim it guarded* had been retired by a
different commit and nobody carried the guard with it.

- **`test_demo_credit_channel_map`'s ratchets were stale**, and had been
  failing for every `slow` run since `2927ef33` — nineteen days. Two of its
  three record assertions guarded claims their owning demos had already
  retired: D16's claim was *inverted* (UnitRMS moved from a mislabelled
  euclid-grid lr to its per-element-displacement lr, where it now learns on
  every geometry — the old assertion demanded the "crutch stays dead"), and
  D14's absolute 0.8 floor predates both the OrthoAdam cells at `77f689ce`
  and the re-emit below. Both legs now assert the owning demo's current
  claim. **A demo test asserting on *other demos' committed records* is a
  cross-claim lock with no invalidation path** — the single sharpest new
  defect class this round produced.
- **`pc_alm`'s manifest pin was stale**, deliberately deferred by `3319f232`
  ("needs a slow re-pin") and never done. The round-close gallery lock has
  been red on that figure since.
- **`D14`'s `mupc × Adam` cell moved 0.828 → 0.65**, which is the settle-horizon
  fix finally reaching a record that had not been re-emitted since before it.
  D14's own claims are relative and both still hold, so the claim survived the
  numerics moving under it.

All three were invisible because the demos that carry them are `slow`-marked,
and §1.8's own text says the default profile no longer verifies the manifest
pin they exist to verify. That is now measured, not suspected.

### 10.3 The demo suite is not bit-reproducible under `-n 4` — NEW, open

`d16` emitted under the tiered runner's `-n 4` differed from a single-process
emit of the *same commit* on **15 of 36 arms**, by up to 2e-2 (e.g.
`graph_grid8x4/muon` 0.4335 → 0.4229). The demo seeds every arm, so this is
not RNG: it is thread-count-dependent float reduction.

**It did not reproduce on the second `-n 4` run** — the re-verification pass
at the end of this round left every record's data untouched. So what is
established is weaker than "the suite is not reproducible" and stronger than
"nothing is wrong": *some* runs produce different data for the same commit and
seed, and nothing in the tree can tell which. The re-pinned manifest is built
from single-process emits for that reason, and the second run agreeing with it
is luck, not a guarantee.

This is the gallery lock's own docstring's second branch — "or the demo became
nondeterministic (a bug — fix it)" — arriving as an open question rather than a
surprise at the next pin. It is a real project (pin torch's thread count in
the emitter, or record it in the provenance so a mismatch is diagnosable) and
it is not taken here.

### 10.4 `test_grpc_seam_subprocess` poisons the CUDA context — NEW, open

`test_various_geometries` is marked `cpu_only` and passed to `cuda` anyway,
because the marker was declared and read by nothing. Fixing the `device`
fixture (§1 extra) is necessary and **not sufficient**: the six tests pass in
isolation and fail after the rest of their file, in every arrangement tried,
with a sticky `cudaErrorAssert` reported 76 times downstream. Something in
that file's worker poisons the context and no single test reproduces it.

The scale is now measured: in the verification pass **all 37 slow-tier
failures are one poisoned CUDA context**. `test_various_geometries` is the
first casualty in its worker, and every later failure — 21 in
`test_ontology_parity`, 8 in `test_continual_learning`, 2 in
`test_mnist_smoke`, `test_quickstart`, and
`test_evaluate_z3_persists_gate_histories_all_arms` — is an
`AcceleratorError` raised by a perfectly innocent test that never touched
TileGeometry. The poison is upstream, in a test that *passes*.

Pre-existing (fails identically at `196eb4cd`), not caused by anything in this
round, and left open rather than half-fixed: the honest state is that a
single sticky CUDA assert costs the slow tier 37 of its tests, and the file
that reports it cannot be trusted to report its own failures — it reports
other tests' failures instead. The cheap half of a real fix is to run the
slow tier with the GPU disabled, which would trade 37 false failures for
slower runs; that is a decision for the next round, not a silent default.

### 10.5 §2.1's re-baselined cost table (2026-09-26, `--with-slow`)

Measured on the first pass; the two rows marked "re-verified" are the
confirmation run after the fixes.

| tier | walltime | result |
|---|---|---|
| acceleration | 17s | 139 passed, 71 skipped |
| algorithms | 13s | 258 passed |
| ceec | 7s | 125 passed |
| graph | 10s | 55 passed |
| integration | 193s → **285s** | 324 passed, 12 skipped, 5 xfailed, 1 xpassed. Re-verified green; the +92s is the `cpu_only` fix, which takes six geometry tests off the GPU — paid deliberately, since the alternative was 37 false failures |
| platform | 14s | 17 passed |
| primitives | 17s | 419 passed |
| property | 77s | 1700 passed, 12 skipped, 25 xfailed, 1 xpassed (14 failed on the first pass = the two-key records, since re-emitted) |
| unit | 37s | 844 passed, 36 skipped |
| **fast total** | **~385s** | |
| slow | 969s → 876s | 34 slow tests. First pass: 39 failed (F4's stale ratchets + the CUDA cascade). Re-verified: **37 failed, all of them one poisoned CUDA context** — see §10.4 |

Fast lane (`testpaths`, `-n 4`): **96s, 3360 passed, 119 skipped, 26 xfailed,
1 xpassed**. The suite is heavier than the plan's 93s/3323 figure and lighter
than the pre-fix numbers, which is the expected direction: correctness fixes
that make settles run their full budget buy walltime.

### 10.6 §2.3, decided

**`docs/archive/` is in-tree, dated directories, no cold store.** One
archival pass has already happened (`0c8e5a2a`); the rule is now written
rather than implied.

**The 42-file `TODO*.md` move is rejected for this round.** The proposal's own
question is "does a reader know which one is live", and the answer is already
yes: exactly one file's Status line says ACTIVE, the series is sequential, and
`TODO35.md` says it owns every open item. The move costs **128 cross-references**
— including one in library code (`ontology/dynamics/_settle_driver.py`) and two
in `docs/platform/` — for a tidiness gain the Status line already delivers.
Re-open it if the root ever holds two ACTIVE plans; that is the moment the
answer changes.

### 10.7 Still open from the original tables

- **§1.2** (pyright fan-in) — **closed in Round 3, §12.1.** The measurement
  came first (§11.5) and the ranking held; the three modules are at 0 and
  repo-wide is 1,936. The pyright half of the pre-commit hook was widened in
  Round 2, so the two halves of the item are both done.
- **§1.9** — the two unwritten test-quality rules. Recommendation unchanged:
  leave them unwritten and record that as the decision. But note §10.3: the
  determinism rule this section declined to write is the one that would have
  caught the xdist drift.
- **§4** (presentation layer) — still unstarted, still without a consumer.
- **§5, §6** — unchanged.

### 10.8 New items, for whoever takes the next round

1. **Make the demo suite bit-reproducible** (§10.3). Until then, a manifest
   pin is only valid for the sharding it was emitted under, and the round-close
   gate cannot tell the difference from real drift.
2. **Stop asserting on other demos' records** (§10.2). Either each demo owns
   its own claims in its own test, or a record carries a claim id and a lock
   checks claim ↔ assertion. Nineteen days of red was the cost of the first
   option being skipped.
3. **Find what poisons CUDA in `test_grpc_seam_subprocess`** (§10.4).
4. **Re-baseline the plan's own numbers.** §7's fast-lane figure and §2.5's
   "34 slow tests" are now measured (§10.5); §5.4's 2,079 pyright findings
   and §1.3's lint tallies in the tables above are the ones that went stale.

---

## 11. Round 2 — the mechanism, the owners, and the poisoned worker

Round 2 took §10.8's four items and §1.2's measurement. Three are closed, one
is measured and partly closed, and the round's real output is not a fix but a
correction: **§10.3's mechanism was wrong, and it was wrong in the direction
that mattered.** The demo suite was never nondeterministic. It was
*environment-dependent*, and the difference is a fact about the machine, not
about the code.

### 11.1 §10.8-1 closed, and the mechanism corrected

§10.3 said "thread-count-dependent float reduction" and read the second
`-n 4` run's agreement as luck. It was neither luck nor nondeterminism.
`scripts/probes/todo35_d16_determinism.py`, on one seeded arm of D16:

| configuration | result |
|---|---|
| 2 calls in one process, 8 threads | bit-identical |
| 2 separate processes, 8 threads | bit-identical |
| 2 separate processes, 1 thread | bit-identical, and **≠ the 8-thread value** |
| `mlp/adam` at 8 vs 1 thread | identical |
| `mlp/muon` at 8 vs 1 thread | 0.92408 vs 0.92268 |
| `attention/adam` at 8 vs 1 thread | 0.90054 vs 0.90034 |

So the emit is a deterministic function of *(commit, seed, thread count)*, and
the third factor was unpinned and unrecorded. The clincher is in the committed
record itself: `d16`'s `attention/adam.seeds[0]` was `0.90034`, which is the
**1-thread** value, while the suite it was emitted from ran at 8. A record
emitted at a thread count the suite does not run at is internally valid and
externally wrong, and nothing in the tree could say so.

The pin existed. `tests/conftest.py` had carried
`os.environ.setdefault("OMP_NUM_THREADS", "1")` for months — *below* its own
`import torch`, where it is a no-op, because OpenMP reads the variable once at
import. The suite has been running at 8 threads the whole time.

Landed:

- `tests/integration/conftest.py` pins it where it is needed, with a runtime
  `torch.set_num_threads(PINNED_THREADS)` autouse session fixture. **Scoped to
  the record-emitting tier on purpose**: an `OMP_NUM_THREADS=1` at the root
  conftest was measured first and cost the fast lane **96s → 186s** for a
  guarantee only the records need. The scoped pin leaves the fast lane out of
  it (the pin lives in a directory `testpaths` does not include).
- `torch_threads` is a fourth provenance key in every record, and
  `test_determinism_thread_lock.py` reads it: 26 records, one assertion each,
  plus a structural check that exactly one module pins the reduction order and
  that it does so with a runtime call (the shape that cannot be a no-op).
- All 29 records re-emitted under the pin, manifest re-pinned.

**Cost of the whole item, measured:** slow tier 1351s, integration tier 222s,
fast lane unaffected by the pin. The three figures whose data moved are
`uaxis_coverage`, `uaxis_depth_frontier` and `depth_harvest`.

### 11.2 The manifest was stale for a fourth figure set, and nobody noticed

Re-pinning surfaced something §10.2 did not: at `4a90b238` the committed
`manifest.json` did not match three of its own committed records
(`uaxis_coverage`, `uaxis_depth_frontier`, `depth_harvest`). Round 1 re-pinned
from a state no run held — the manifest was written before the slow pass that
re-emitted those three records. The gallery lock could not have caught it,
because the default profile's `integration` tier runs *before* the `slow` tier
in `run_tiered_suite.sh`, so the lock always compares pre-slow-pass records
against a post-slow-pass pin. Same class as the `pc_alm` pin: a claim retired
by a commit that did not carry its guard.

### 11.3 §10.8-2 closed: the cross-claims were all duplicates

F4's eight ratchets against five other demos' records turned out to be
*weaker or equal copies* of assertions the owning demos already make on their
own fresh data — D14's own margins are 0.3 and 0.05 against F4's 0.2 and 0.2;
D16's own `unit_rms` claims are the ones F4 was asserting. So the fix was
deletion, not migration: F4 lost `_assert_record_ratchets` and its
record-reading machinery, and each owning demo grew

```python
CAPABILITY = "d18_update_ladder"
def assert_claims(record: dict) -> None: ...
```

called on the fresh record by the demo, and on the **committed** record by
`tests/property/test_claim_ownership_lock.py` in the fast lane. Five claim
families that were previously only reachable behind a `slow` marker nobody
runs are now checked in 9s. The same file forbids a test from naming a record
it does not own — the class, as a source scan over string literals with
docstrings excluded (prose naming a record is not a read of it).

Verified non-vacuous: swapping two arm means in a copy of D18's committed
record fails the owner's own assertion, with its own message.

### 11.4 §10.8-3 closed: one shadowed fixture, 37 failures

`test_grpc_seam_subprocess.py`'s test class defined its own class-scoped
`device` fixture, shadowing the shared one in `tests/conftest.py` that reads
`cpu_only`. So `test_distributed_train_step_parity` — marked `cpu_only` *and*
`xfail` — ran on CUDA, tripped TileGeometry's device-side assert, and left the
context poisoned for every later CUDA call in that worker. Bisected to a
single test by running each predecessor plus one victim; the CUDA assert is
confirmed at `torch.manual_seed` → `torch.cuda.manual_seed_all` with
`CUDA_ERROR_ASSERT`, i.e. the context was already dead on arrival.

The shadow is deleted, which forced the class-scoped `system` / `test_batch`
fixtures to function scope (a class-scoped fixture cannot depend on a
function-scoped one). `tests/property/test_device_fixture_lock.py` keeps the
class from coming back, scoped to `tests/integration/**` because that is the
tier whose workers share a CUDA context with the demos and the gRPC workers.

Result: **37 slow-tier failures → 0.** Verified per file, not in aggregate:
the gRPC file is 12 passed / 1 xfailed, and the 33 downstream failures pass
(`test_ontology_parity` 21, `test_continual_learning` 8, `test_mnist_smoke` 2,
`test_quickstart`, `test_z3_redesign`).

### 11.5 §10.8-4: the numbers, re-measured

| quantity | §10.5 said | measured 2026-09-26 (this round) |
|---|---|---|
| pyright findings, repo-wide | 2,079 | **1,975** (210 files) |
| ruff findings, repo-wide | 334 | **334** — at the ratchet baseline, no re-baseline needed |
| fast lane | 96s / 3360 passed | **127s / 3397 passed** (+3 new lock files, ~10s of it the claim lock) |
| integration tier | 285s | **222s** (1 failure at the time: the stale manifest) |
| slow tier | 876s, 37 failed | **1351s, 37 failed** — all one poisoned context, now 0 |

Lint by rule, repo-wide: `RUF105` 143, `PLW0717` 81, `E402` 32, `SIM102` 19,
`PLR0913` 8, `TRY300` 6, the rest ≤5. §1.3's table said `RUF105` 148 /
`PLW0717` 81 / `E402` 32 / `SIM102` 19 — the `RUF105` count was measured on
`computronium/` only, and the repo-wide figure is 143.

**§1.2's ranking, measured** (import fan-in × pyright findings, the two
things the plan asked for):

| module | fan-in | pyright |
|---|---|---|
| `ontology/credit.py` | 43 | 21 |
| `core/pipeline.py` | 18 | 11 |
| `core/trainer.py` | 22 | 7 |
| `core/campaign/evaluation.py` | 16 | 6 |
| `utils.py` | 35 | 7 |

Fan-in alone is a bad sort key: the ten most-imported modules in the tree
(`core/logging`, `acceleration/registry`, `ontology/geometry`, …) are all at
zero findings, and the whole top of the table is modules nobody imports
(`acceleration/kernels.py` 90, `models/deployments/rl.py` 80,
`models/deployments/vision.py` 67). The three modules the plan names are the
right three to fix and are untouched by this round.

**The pre-commit hook was never running.** `.pre-commit-config.yaml` has
carried `name: identity cards (C.1: every concrete primitive carded)` since it
was written, and a plain YAML scalar cannot contain `": "` — the file does not
parse. `pre-commit validate-config` failed; every hook in `AGENTS.md`'s gate
section was inert. The name is quoted now, and the pyright hook is widened
from one hardcoded directory (`computronium/ontology`) to changed files under
`computronium/`, which is the second half of §1.2. Tests stay out of the hook:
297 findings live in the legacy property suite, and a gate that fires on files
you only opened is a gate people switch off.

### 11.6 New items, for the next round

1. **The gallery lock runs before the pass that changes what it locks.**
   `run_tiered_suite.sh` runs `integration` (which holds the lock) before
   `slow` (which re-emits seven of the records). Any re-pin therefore has to be
   taken *after* the slow pass, by hand, and nothing records that the order
   matters. The fix is a re-pin step in the runner, or moving the lock after
   the slow pass.
2. **`d15`, `d16`, `d19` are the demos whose data moves with the thread
   count; the other 23 did not move at all** when re-emitted at 1 thread. That
   is worth knowing before anyone re-litigates the pin's cost: only three
   figures are thread-sensitive.
3. **§6's flake has not recurred**, but the mechanism §10.3 blamed for it was
   wrong, so the explanation is still missing. With the thread count now
   recorded and the integration tier pinned, a recurrence has one fewer
   variable in it.
4. **The 8 remaining `device` fixtures** (in `tests/unit/**` and
   `tests/slow/`) are outside the lock's scope and are unexamined. They cannot
   currently poison anything — the fast and slow lanes are green — but the
   lock's scope was drawn from one failure, not from a survey.
5. **The claim-ownership lock imports five demo modules to run their claims**,
   which costs 8.3s of the fast lane and executes their module-level data
   loading. If the claim set grows, that cost grows with it; the alternative is
   moving the claim functions into an importable module, at the cost of the
   owner relationship being declared rather than structural.

---

## 12. Round 3 — a dead branch, and the type checker that found it

Round 3 took §1.2 (pyright on the three highest-fan-in modules) and
§11.6-1 (the gallery lock's ordering). **§1.2 is closed, and it paid for
itself before it was closed**: the third module's findings included an
`ImportError` on a live branch that no test had ever taken.

### 12.1 §1.2 closed: 39 findings, and one that was a crash

The §11.5 ranking was measured, so this was three named modules rather than
a guess: `ontology/credit.py` 21, `core/pipeline.py` 11, `core/trainer.py`
7. All three are at **0**. The fixes were not 39 suppressions; they were
five type gaps, each of which had a name:

| gap | sites | what it was |
|---|---|---|
| `Geometry` does not declare the tile-block view | 9 | `credit.py` called `assemble_blocks` / `scatter_block_grads` behind a repeated `getattr` on a Protocol that never declared them. `TileBlockGeometry` + `is_tile_block_geometry` (a `TypeIs`) now carry it, and the guard **returns the narrowed geometry** instead of a bool — which is what deleted the `getattr`s |
| `settle` returns the read-only `SettableState`; the pipeline wrote to it | 7 | `pipeline.py` assigned `settled.activations/loss/energy` on a read-only Protocol. Routed through the `set_state_field` / `state_energy` helpers that already existed for exactly this |
| `TransformerGeometry.blocks` is an untyped `nn.ModuleList` | 10 | every `block.ln1` / `block.in_proj` read as `Tensor | Module`. One narrow in `tf_blocks` instead of four casts |
| `PepitaCredit` passed `None` as a `Substrate` | 4 | **the docstring said "a DigitalSubstrate is assumed when unset" and the code passed `None`.** `FeedforwardGeometry` resolves `None` itself; a backend that does not would have crashed. Resolved once, in `_resolved_substrate` |
| `ParameterUpdate` cannot satisfy `_StatefulUpdate` | 1 | see below |

The 39 were not equal: **one of them was a crash.** `dispatch_train_step`'s
kernel-backend path imported `_run_contrastive_kernel_step` and
`_run_kernel_train_step` from `computronium.core.trainer`. Neither name is
defined in that module, and `grep -rn "def _run_.*_kernel_step"` over the
tree returns nothing. The `elif` and `else` branches were guaranteed
`ImportError` the first time a backend exposed `contrastive_step` and
nothing else — a whole class of backend, with the signatures the deleted
helpers were thin wrappers around sitting on the objects themselves. The
fix routes to `backend.contrastive_step` / `backend.kernel_train_step`
directly; the `else` branch was unreachable by construction (it called
`kernel_train_step` in the arm that had already found `kernel_train_step` to
be `None`) and is gone. `tests/unit/core/test_trainer_kernel_dispatch.py`
asserts all three arms, because a green bespoke-arm test says nothing about
its sibling.

**The last finding is the interesting one.** `credit.py` held a
`ParameterUpdate` and passed it to `actual_parameter_displacement`, which
takes the private `_StatefulUpdate` — a Protocol requiring
`get_state`/`load_state` that `ParameterUpdate` never declared. Both are
true: every rule implements the snapshot protocol, and the Protocol that
says so was unreachable from outside. `_StatefulUpdate` is now the public
`StatefulUpdate`, with the requirement written down where a caller sees it
(register a rule for a within-batch recompute view and it must be
replayable). The *replay obligation* was previously unstated, which is the
same class as the `None` substrate: a contract the type did not carry and
the code did not state.

### 12.2 Two wiring locks were guarding a name, not a property

Adding the two Protocols turned four locks red — and every one of them was
right to be. `_geometry_classes()` excluded `Geometry` from the backend
registry by spelling `"Geometry"`, and the update lock excluded
`ParameterUpdate` the same way. Both now exclude **any** Protocol
(`getattr(member, "_is_protocol", False)`), so the population is expressed
as a property of the class rather than as a growing list of names, and the
special case that would have been the next failure is gone.

### 12.3 New: the import lock, and six stale imports outside its scope

F821 cannot see this defect class: `from computronium.core.trainer import
_name_that_does_not_exist` is a *valid* import to the linter and an
`ImportError` at runtime. `test_undefined_name_lock.py` now carries a third
lock — every runtime `from computronium.<module> import <name>` must name a
symbol the target module defines. It is scoped to `computronium/core` and
`computronium/ontology`, with the three excluded populations named in the
docstring: package `__init__` re-export surfaces (they have their own
locks), star-import shims (not statically derivable), and
`TYPE_CHECKING`-block imports (pyright's population, and §1.2's widened
pre-commit hook is its per-commit gate). Verified non-vacuous: injecting
`from computronium.core.ebm import EnergyModel, EnergyModelX` fails it
with the offending line.

The scan found **six genuinely dead imports in eight modules outside that
scope** — every one confirmed by `hasattr` on the imported module, not by
reading:

| consumer | stale import from |
|---|---|
| `core/trainer.py` (the defect above), `cli/export_trained_kernel.py`, `config/experiment.py`, `evaluation/base.py`, `evaluation/cross_domain.py`, `experiment/probe.py`, `experiments/{cross_domain_transfer,fa_depth_scaling,mep_tournament,mot_ablation,tile_algorithm_comparison,tile_scaling}.py` | `CoreTrainer`, `TrainerConfig` — **removed from `core/trainer.py`**, whose own docstring says so |
| `analysis/ablation.py` | `run_from_runconfig` |
| `cli/commands/verify.py`, `cli/shared.py` | `run_single_trial` |
| `validation/gradient_check.py` | `KB` |
| `execution/engine.py` | `ReportOrchestrator` |
| `experiments/eqprop_vision_parity.py` | `_BASELINE_MODELS` |

`from computronium.core.trainer import CoreTrainer` appears in **13
modules**, and `core/trainer.py` has said "Legacy `CoreTrainer` and
`TrainerConfig` have been removed" in its first paragraph the whole time.
So the question is not "is this a lock worth having" — it is *which of those
13 modules are live*, and the answer decides whether the fix is 13
one-line repoints or 13 deletions. Not taken here; see §12.6.

### 12.4 §11.6-1 closed: the record locks are re-read after the pass that moves them

`run_tiered_suite.sh` now runs a `POST-SLOW RE-PIN VERIFY` step after the
slow tier: the gallery lock, the provenance lock, the claim-ownership lock
and the determinism-thread lock, all four re-read against post-slow-pass
records. The step does not re-pin — backfilling a pin is fabricating one —
it **fails and says which file to re-pin**, which is the only honest
response. `test_tier_coverage_lock.py` asserts the step exists, names all
four locks, and sits *after* the slow tier in the script; the tier-order
result it replaces was structurally incapable of catching §11.2's
staleness.

### 12.5 Numbers, re-measured

| quantity | §11.5 | measured 2026-09-26 (this round) |
|---|---|---|
| pyright, repo-wide | 1,975 (210 files) | **1,936** — the 39 findings above, and nothing else moved |
| ruff, repo-wide | 334 | **334** — at the ratchet baseline, no re-baseline |
| fast lane | 127s / 3397 passed | **240s / 3403 passed, 119 skipped, 26 xfailed, 1 xpassed** |
| new lock cost | — | cross-module import lock 4.2s; post-slow ordering assertion 0.0s |

The fast lane's walltime is 240s against 127s, and **this paragraph is a
guess, not a measurement** — the only thing established is that the diff
adds ~4s of locks. The samples that exist contradict the "quieter box"
story rather than confirm it: the same three-tier command took 279.82s at
baseline and 269.96s with this round's diff, a 3.5% spread, so this box is
*stable*, and the gap is **between sessions**. So the sharper claim is that
**§11.5's 127s is not reproducible on this machine and is not a number
anyone should regress against**. Corrected and given a first move in
§13.1 item 3: three back-to-back runs, and the *test count* is the
load-bearing metric rather than the walltime.

### 12.6 New items, for the next round

1. **Resolve the 13 `CoreTrainer` / `TrainerConfig` importers and the five
   other stale-import clusters** (§12.3). The lock is scoped away from them
   precisely because they are not yet resolved, and scoping a lock to dodge
   known failures is the arrangement §0 warns about. Answer one question
   first: which of those modules are still imported by anything live? The
   dead ones are deletions, not repoints.
2. **Re-scope the cross-module import lock once (1) closes.** It is scoped to
   two layers because the other 13 files fail it. A lock that covers half the
   tree is worth having; a lock that covers half the tree *by choice* needs
   the choice revisited.
3. **§6's flake has now recurred once** (this round, in a three-tier `-n 4`
   run; the failure message was again not captured). More usefully: that run
   also produced a **new, reproducible pair** —
   `test_credit.py::test_cosine_similarity_reasonable` and
   `test_ntm_geometry.py::test_bptt_learns_copy_mechanics` — which **pass in
   isolation and in `tests/unit` alone, and fail identically on the
   unmodified tree** when `tests/unit tests/property tests/primitives` run
   together under `-n 4`. Confirmed pre-existing by stashing the diff and
   re-running. That is a cross-tier ordering/seed interaction, not a
   defect in either test, and it is a better lead than §6's flake: it
   reproduces.
4. **§1.3's PLW0717 tranche is still open** at 81, untouched by this round
   for the same reason it was untouched by the last two: the pyright work
   in `credit.py` and `pipeline.py` removed the findings, not the
   complexity.
5. **§4, §5, §1.9** — unchanged; §1.9's recommendation still stands, and
   note that the two unwritten rules would not have caught any of this
   round's findings.

---

## 13. Start here — Round 4 handoff

State at `4be5eb6d`, working tree clean. Round 3 (§12) is closed and
committed; nothing below has been started.

### 13.1 The next three moves, in order

**1. §6 has a mechanism, and it is the one thing never checked.**
Cheapest item on the list, and it may close a two-round-old open item.
`pyproject.toml:190-192` sets a **global per-test `timeout = 120`** with
`timeout_method = "signal"`, enforced by `pytest-timeout` (a hard
dependency, not aspirational). Long tests are expected to opt out with an
explicit marker — `@pytest.mark.timeout(600)` / `(900)` appears on
`tests/slow/**` and on `test_demo_uaxis_depth_frontier`. Measured margins
on this box:

| test | tier log | isolated | explicit marker | margin vs the 120s kill |
|---|---|---|---|---|
| `property/test_deep_credit_trial.py::TestContrasts::test_contrasts_cover_deep_tier` | **37.36s** | **90.08s** | **none** | **~30s, and it varies 2.4× in one session** |
| `integration` tier slowest | 87.00s | — | — | ~33s |
| fast-lane slowest | 38.12s | — | — | ~82s |

This is §6's occurrence: the failure came in a property-tier run that took
**217s** against a normal 75–95s, and this one test is **half the tier**
(37.36s of 74.24s). **§6 assumed the failure was an assertion failure and
reasoned from the assertion's shape** — but §6 also records that the
failure message was never captured. A SIGALRM kill reports as `Timeout`,
not as a failed assert, and if that is what happened then the "key-presence
check cannot fail from numerics" argument was answering a question nobody
had asked. The two hypotheses are distinguishable: re-run that test to
**≥120s** and the exit reason says which.

Do this first because it is one command and it may delete an open item:
`uv run python -m pytest tests/property/test_deep_credit_trial.py -q -n 4
--timeout=120 --timeout-method=signal` under load, or read
`faulthandler_timeout`'s traceback out of `logs/tiers/property.log` if a
future run trips it. Whatever the answer, **the finding that survives
either way is that the fastest lane's slowest test has a 30s margin against
a hard kill and no marker of its own** — a per-test duration lock (assert
the slowest N tests hold ≥2× margin, or that any test over 60s carries an
explicit marker) is the lock this class wants.

**2. The 13 `CoreTrainer` / `TrainerConfig` importers (§12.3).** This is
what unblocks the cross-module import lock's scope. First move is a graph
question, not a reading exercise: for each of the 13 consumers, is
anything live importing *it*? Dead consumer → delete; live consumer →
repoint at `SystemTrainerConfig` / `compose_system`. The five other
clusters (`run_from_runconfig`, `run_single_trial`, `KB`,
`ReportOrchestrator`, `_BASELINE_MODELS`) are single-site and can ride
along. Then re-scope `test_undefined_name_lock.py` to the whole tree —
a lock covering half the tree *by choice* is the arrangement §0 warns
about, and this is the item that removes the choice.

**3. Replace §7's single fast-lane figure with a spread.** §12.5 attributed
a 240s-vs-127s gap to "machine noise" without measuring it. The samples
that *do* exist contradict the story rather than confirm it: the same
three-tier command took **279.82s at baseline and 269.96s with Round 3's
diff** (3.5% spread, so this box is stable) while §11.5 recorded 127s for
the *larger* five-path lane. The gap is between sessions, not within one,
which means **§11.5's 127s is not reproducible on this machine and should
not be a figure anyone regresses against.** Three back-to-back fast-lane
runs give the distribution; the test *count* is the load-bearing metric,
not the walltime.

### 13.2 What is deliberately still open

`§1.3` PLW0717 at 81 — untouched three rounds running, for the honest
reason that the pyright work in `credit.py` and `pipeline.py` removed
*findings*, not complexity. `§1.9`'s two unwritten test-quality rules —
recommendation unchanged (leave unwritten, record the decision), and note
that neither would have caught anything in Rounds 1–3. `§4` presentation
layer — still no consumer, still not to be started because it is ready.
`§5`, `§6` — §6 per §13.1 above.

### 13.3 Session notes (things that cost time this round)

- **Dev-env smoke first**, per `AGENTS.md`: `uv run python -c "import
  optuna, scipy, torchvision, pytest"`. `UV_LINK_MODE=copy` is set in the
  env. No `py-spy`, no `yappi` installed; **no profiler was needed** — every
  question in §13.1 is answered by `--durations` output, `pyproject.toml`
  config, or a re-run.
- **The pre-existing cross-tier failure pair** (§12.6-3) will reappear in
  `tests/unit tests/property tests/primitives -n 4` and is *not* a
  regression: `test_credit.py::test_cosine_similarity_reasonable` and
  `test_ntm_geometry.py::test_bptt_learns_copy_mechanics` pass alone, pass
  in `tests/unit` alone, and fail identically on an unmodified tree.
  Confirmed by stashing the diff. Do not chase it as a Round-4 regression.
- **Adding a `Protocol` breaks four wiring locks**, by design:
  `test_geometry_wiring_lock.py` and `test_registry_completeness_lock.py`
  enumerate "classes whose name ends in `Geometry`/`Update`" and used to
  exclude their Protocol *by spelling its name*. They now exclude any
  Protocol, so a second Protocol is free — but expect the red on the first
  one after this.
- **Do not profile the fast lane.** §8 is right: the suite got heavier
  because a correctness fix made settles run their full budget, so
  speeding it up speeds up the artifact the fix improved. Item 3 above is a
  *measurement* of a claim already in the document, which is a different
  thing.

---

## 14. Round 4's operating rule — stop auditing, start extracting

Written after an honest mid-series assessment, not a round close. The
assessment is recorded here because the conclusion is a **rule change**,
and a rule that lives only in someone's judgement does not bind the next
session.

### 14.1 What three rounds actually bought

Trustworthiness, not capability. Concretely: three live defects no test
caught (a branch that raised `ImportError` on first execution, a
CUDA-poisoned worker costing 37 slow-tier tests, `cpu_only` declared and
read by nothing), plus the thread pin that made the record set
reproducible. Every demo claim is the same claim it was three rounds ago.

That trade was correct, and the evidence is that the tree was not
trustworthy enough: six modules cannot be imported at all, and one live
branch would have crashed. But it is a *precondition*, and three rounds
of it is enough.

### 14.2 The three numbers that say the series is not converging

- **The false-claim rate is flat.** Round 2 found three stale claims,
  Round 3 found six dead imports, two wiring locks guarding spelled-out
  names, one non-reproducible walltime, and one open item (§6) whose
  reasoning rested on an assumption nobody checked — including this
  document's own §12.5, wrong in the session that wrote it. The pattern
  the series exists to end is reproducing at the rate it started. A
  process whose output is "the last round's claims were wrong" is
  auditing at a fixed cadence, not converging. **n=3 is too few to call
  a trend, and it is also too many to keep calling it progress.**
- **The main thread's arithmetic.** Repo-wide pyright 1,975 → 1,936:
  39 findings in a round whose stated cost was ~4h. Clearing the
  remainder at that rate is ~50 rounds. `PLW0717` has moved 89 → 81
  across three rounds and been declined three times running, each
  decline reading as principled and functioning as a deferral.
- **Marginal lock value is falling.** Round 3 spent most of its time
  writing locks *about* locks, and the import lock's population
  assertion took three iterations to become non-vacuous. §0 is a good
  rule; it stops paying at some point, and Round 3 was past it for the
  later items.

### 14.3 The self-indictment, recorded so it cannot be quietly dropped

`§12.3`'s handoff note says resolving the 13 `CoreTrainer` /
`TrainerConfig` importers needs "a graph question, not a reading
exercise" — and that graph question is five minutes of `git grep`. So
Round 3's own #2 handoff item is a deferral wearing a prerequisite's
clothes. Worse: the cross-module import lock was scoped to
`computronium/core` + `computronium/ontology` **because 13 files fail
it**, and it was landed in the same commit that quotes §0. That is the
§0 violation the section is named after, committed deliberately and
flagged rather than hidden. Naming it is not discharging it.

### 14.4 The rule, effective this round

1. **No new locks in Round 4.** A lock may be *widened* or *unscoped*
   (the import lock's real scope is the whole tree and it is currently
   dodging 13 failures). A lock may not be added. If a change needs a
   new guard, the change waits for Round 5.
2. **The deferred work is the work.** `PLW0717` (81) is taken this
   round, in bulk, not declined a fourth time. It is the one item where
   doing it is unambiguously *doing* rather than *measuring*, and the
   `p2p` extraction precedent is that it finds live crashes.
3. **The `CoreTrainer` cluster gets the five minutes**, in this round,
   and the import lock goes to full-tree scope or the reason is written
   down as a blocker.
4. **Stop at one new lock per round, and only if it guards a defect
   found in that same round.** Everything else is a bug fix, an
   extraction, or a doc correction.
5. **Round 4 closes with a capability statement or it does not close.**
   If Round 4 produces findings and no code that is better, the series
   is auditing rather than building and the right response is to stop and
   change what the series is for — not to open Round 5.

### 14.5 What is explicitly not being done, and why it is now a decision

`§4`'s presentation layer has been deferred across three rounds on the
grounds that it has "no consumer." If the tree's capability is not
growing, that is a statement about the *series*, not about the timing.
It stays deferred — but the next time it is raised, the question to
answer first is not "is it ready" (it is) or "does anything need it" but
**"is the absence of a watchable run part of why nothing needs it."**
That is a product question, and it is the first one in this document
that a lock cannot answer.

### 14.6 The graph that says "unreachable" was measuring the wrong graph

Round 4 nearly deleted five modules on a `0 static importers` inference.
All five are **documented capabilities** — `README.md:1189/1190/1193` list
`eqprop_vision_parity`, `mep_tournament` and `cross_domain_transfer` in the
experiment catalogue, `README.md:1253` gives one of them a runnable
`python -m` command, and `README.md:1351` documents `ablation.py` as the
home of leave-one-out and Sobol sensitivity reporting. `ablation.py` was
nearly written off as a duplicate of `tile_research.py` because
`create_ablation_study` appears in both — it uniquely holds
`LeaveOneOutResult`, `SobolIndices` and `create_ablation_report`.

**The rule: this repo's public surface includes documented entry points —
README tables, `python -m` invocations, CLI scripts, config-driven
entry — and no static import graph contains any of them.** "0 importers"
is not deadness. It is the *expected shape* of a documented entry point.

This is the same shape as `TODO34` Pass 16's swallowed `TypeError` in
`p2p/evolution.py` and as the daemon in §5 that is silent by
construction. Three instances now, and the common error is always the
same: treating an absence of *code-level* evidence as evidence of
absence. The reachability check that does not lie is "does the tree
document it, and does it run?" — which is why the five-file deletion is
recorded here as **reverted, not merely declined**.

Corollary for the locks: `test_undefined_name_lock.py` finds these
imports by static analysis, and its *scope* argument in §13 is "13 files
fail it" — which is the right reason to fix them and the wrong reason to
leave them. Round 4 fixes them by extraction, per §14.4 rule 2.
