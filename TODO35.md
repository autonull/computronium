# TODO35: The Proveable Remainder

**Status**: **ACTIVE — open.** This document owns every open item as of
`196eb4cd`. `TODO34.md` keeps its 16 passes as the record of how the tree was
made fast, provable and ready to be presented; its "Remaining Work" section is
replaced by a pointer here, because two live open-item lists is the drift this
plan series has documented five times.

Continues `TODO34` (test velocity, correctness hardening, the presentation
layer). Where `TODO34` removed the defects, this one closes what the removal
*revealed* and takes the decisions `TODO34` deliberately deferred.

**Read this, not `TODO34`'s section numbering.** The section numbers here are
local to this document; `TODO34` §-numbers are cited only where an item was
moved from there.

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
| 1.1 | **pyright: the top modules by fan-in** | 2,079 findings repo-wide. `pre-commit` gates pyright on `computronium/ontology` only | Re-count per module before picking: `TODO34` Pass 16 took `p2p/evolution.py` from 16 → 0 *inside an unrelated extraction*, so the fan-in ranking is a guess until measured. Then drive the top 3 to zero and widen the pre-commit hook to changed files, the way ruff's already is | ~4h + ongoing | 3 modules report 0; the pre-commit pyright hook reads its filenames instead of hardcoding one directory |
| 1.2 | **Lint tranche 2** | **349** findings (was 353). By rule: `RUF105` 148, `PLW0717` **89**, `E402` 32, `SIM102` 19, `too-many-arguments` 8, `complex-structure` 5, rest ≤6 | Take `PLW0717` next: `knowledge/causal.py` holds 4 (16/39/9/29 statements) and `hyperopt/experiment.py` 3. The `p2p` extraction is the recipe and the precedent — it found a live crash. **Leave `E402` and `SIM102` alone** (see §3.4) | ~3h | count falls with no new suppression; the ratchet moves down with it |
| 1.3 | **Environment fingerprint in run records** | `computronium.utils.capture_environment()` / `deps_hash()` exist and are **unused**; the records carry `git_commit` only | Add `deps_hash()` to `emit_run_record`, then re-emit every record in the one slow pass that §1.4 also needs. Backfilling a version into an existing record is **fabricating** provenance, so this cannot be done piecemeal | ~1h + the slow pass | a drift lock can say which of code / config / environment moved |
| 1.4 | **cwd-relative defaults in `scripts/`** | `scripts/visualize_atlas.py:23` and `scripts/g1_core_sweep.py:36` both default to `Path("artifacts/ruler_table.json")` — a file that has *moved*. The repo-root `checkpoints/` was the same shape and is now deleted | One scan for `Path("<literal>")` defaults under `scripts/`, as a fast-lane lock. This is the third instance of one class; the class is what is worth locking, not the two sites | ~40min | the scan runs, with the population assertion it needs to be a lock |
| 1.5 | **`pre-commit` invokes pytest wrongly** | the hook's entry is `uv run pytest tests/property/ -q`. `AGENTS.md` says **always** `uv run python -m pytest` — bare `pytest` picks up the user-site interpreter and breaks collection on protobuf gencode skew | One-line fix. The rule is written down precisely because it was learned the expensive way, and the hook that runs most often does not follow it | ~5min | the hook entry is `uv run python -m pytest` |

### 1.6 The stale-index note, resolved

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
| 2.1 | **Re-baseline the cost table** (`TODO34` §1.6) | the recorded numbers predate the settle-horizon fix, which made every settle run its full budget. The table is therefore *known* stale, not merely old | one `./scripts/run_tiered_suite.sh --with-slow --durations=20` | ~30min machine |
| 2.2 | **Environment fingerprint** (§1.3 above) | needs every demo re-run to be honest | the same pass re-emits the records | folded in |
| 2.3 | **`docs/archive/` policy** | 5.1M across 11 dated directories; one archival pass already happened (`0c8e5a2a`); no rule recorded | decide in-tree vs cold store, write the rule in three lines, apply it | ~30min |

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
# --with-slow is required at round close: 26 slow tests, including every
# demo that emits and pins a gallery record, are excluded by default.
./scripts/run_tiered_suite.sh --with-slow

# Gates on changed files
uv run ruff format --check <changed>
uv run ruff check <changed>
uv run pyright <changed>            # strict for new/rewritten modules

# The lint ratchet is a gate too: it fails if the repo-wide count rises.
uv run python -m pytest tests/property/test_lint_count_ratchet.py -q
```

`F821` and the `TYPE_CHECKING`-import hazard are enforced in the fast lane by
`test_undefined_name_lock.py` and
`test_type_checking_imports_are_not_called_at_runtime`; the explicit
`--select F821` run is for iterating on a fix, not for the gate. Provenance
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
