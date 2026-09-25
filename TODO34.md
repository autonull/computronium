# TODO34: Test Velocity, Correctness Hardening, and the Presentation Layer

**Status**: **ACTIVE** — items 0.1–0.9 completed and committed (`ff6528fb`);
§2.1 completed and committed (`59d13f47`); §1.1 partially landed. §1.2–§1.6,
§2.2–§2.6, §3–§5 open.

Continues the series after `TODO33` (deprecated/legacy cleanup). Where `TODO33`
removed code, this one makes what remains *fast, provable, and ready to be
presented* — the three things the next development push (CLI equivalents, and
whatever UI comes after) will lean on.

§5 (architectural refactors) is the highest-leverage section and the longest
sounding; it is sequenced **last** on purpose. See its own risk notes before
starting it.

---

## Summary of Completed Work

### Pass 2 — §2.1 (undefined names), `59d13f47`

All 11 sites fixed. The reason `ruff check` had stayed green is now a lock:
**every one of the 11 carried a `# ruff: ignore[undefined-name]`
directive**, so the F821 gate was silenced at each site it ever flagged. The
gate now bans the suppression as well as the finding.

| # | Site | What it was |
|---|------|-------------|
| 2.1a | `acceleration/fa_kernels.py` (4 sites) | branched on `HAS_TRITON`; module defines `HAS_TRITON_FA`. Live `NameError` on the GPU FA path |
| 2.1b | `execution/candidate_gen.py` | `_matches_filter` used `TASK_GROUPS` unimported — **every** `--task-filter` call raised `NameError` |
| 2.1c | `core/system_trainer/joint.py` (4), `core/profiling.py`, `tests/` (2) | annotation-only |

**Calling the two crashed functions exposed two more defects in the same
untested path.** Both are fixed; both are locked by tests that *call* them:

* `_fa_batched_outer_kernel` used `tl.dot` where the contraction is an outer
  product. It failed to compile. The obvious repair (`post * tl.trans(pre)`)
  was **also wrong** — it broadcast the transposed index against the
  untransposed one and returned a tensor constant along one axis, which a
  shape-only test would have accepted. `post * pre` is correct, verified
  numerically on CUDA against the eager path.
* A duplicate "with transpose" feedback projection whose Triton kernel and
  eager fallback disagreed with each other *and* with their only callers: the
  eager path raised `RuntimeError` on any non-square feedback matrix, and the
  kernel stored a `[B, D_out]` contraction into a `[B, D_in]` buffer. Zero
  callers — deleted.

Dead code with zero in-tree callers, deleted: `fa_backward_triton` and the
activation-derivative cluster (`fa_activation_derivative_triton`,
`_activation_type_from_module`). `fa_backward_triton`'s eager path carried the
same transposed-projection shape bug, so it could never have run.

**Correction.** I claimed `err @= B` in the `random_projections` kernel was a
silent no-op. It is not: `Tensor` has no `__imatmul__`, so augmented
assignment rebinds the name and the statement is exactly `err = err @ B`. The
explicit form is kept for clarity; no behaviour changed there. The test built
on the false claim was removed. **Recorded because the reasoning error is the
kind that survives into a commit message** — a matmul looks in-place and
isn't, but the interpreter's fallback makes it work.

Suite after: fast lane **3147 passed, 119 skipped, 26 xfailed, 1 xpassed in
106s**. No full-suite run — the changes are confined to `tests/acceleration`
and `tests/primitives`, both inside the fast lane, and the §0 pass already
carries a recorded 3516-passed full-suite result.

### Pass 1 — §0 (post-UI-removal repair), `ff6528fb`

The NiceGUI dashboard removal (`947d33cd`, `0c8e5a2d`) left the tree in a state
where the suite could not even start, and then surfaced three systemic defects
that the whole scientific stack sat on top of. All fixed, each with a
mutation-tested lock (the defect was reintroduced to prove the test fails).

| # | Defect | Root cause | Lock |
|---|--------|-----------|------|
| 0.1 | Suite could not start at all | root `conftest.py` registered `nicegui.testing.plugin` after nicegui was dropped | startup itself |
| 0.2 | **Every settle loop stopped after 1 step** (6 of 9 failures) | `_note_settle_start()` seeded `_settle_steps_used = max_steps`; loops then tested `if self._settle_steps_used > 0: break` — true before the body ran | `TestSettleHorizonTelemetry` (7 tests) |
| 0.3 | EqProp/thermo gradient cosine 0.39 (floor 0.62) | consequence of 0.2: the free phase never reached its fixed point, so the energy gap the thermo credit reads was noise | `test_credit.py::TestThermodynamicVsBackpropMLP` |
| 0.4 | `on_step` was a silent no-op | callback nested inside the `track_free_energy_per_iter` guard, which is **off by default**; `SpikeIntegrationDynamics` and `PCALMDynamics` dropped the argument entirely | `TestOnStepCallback` (was vacuous: `assert isinstance(x, list)`) |
| 0.5 | L1 promotion re-promoted matured cells | `kb_load_cached` keyed on `(mtime_ns, size)` of the main SQLite file; in **WAL mode** both are byte-identical across commits (measured) — long-lived readers never saw new cells | `test_kb_load_cache.py` (4 tests) |
| 0.6 | Geometry wiring lock resolved **0 of 10** classes | the lock regexed `geometry_from_config`'s *source text* for alias literals; dispatch had become table-driven | lock rewritten to read the dispatch tables |
| 0.7 | PC-ALM: `_note_settle_start()` never called | each phase (free, nudged) inherited the other's stop flag | `test_pc_alm_validation.py` (28 tests) |
| 0.8 | `test_dual_vars_initialized_to_zero` asserted the opposite of its name | asserted non-zero duals on a system whose constraint residual is exactly `0.0` at every step — could only hold while the loop under-ran | test rewritten to the true invariant |
| 0.9 | Stale `mechanism_recipes_demo.py` | `temporal_psi` now composes a full System; the demo still drove a bare readout and called a non-callable attribute | `test_lab_smoke.py` |

**Test velocity banked in the same pass** (all reductions measured, not guessed):

| Test | Before | After | Basis |
|------|--------|-------|-------|
| `test_geometry_execution_is_bit_for_bit_reproducible` | 42.3s | 8.8s | claim is "two seeded runs agree", not "it learned" — 5 epochs → 1 |
| `test_bptt_learns_copy_mechanics` | 23.8s | 11.7s | measured curve 0.88@200, 0.95@400, **1.00@600**, flat after → 1200 → 600 steps |
| `test_demo_pc_alm` | 42s | 24s | 600 → 300 batches *raised* train acc 0.26 → 0.49 and turned a 0.26-vs-0.25 sliver into a real margin |
| `unit` tier walltime | 70s | 38s | |

**Suite state at handoff**: `3516 passed, 0 failed` across 8 tiers
(unit 825, primitives 419, algorithms 258, graph 55, ceec 125, platform 17,
property 1491, integration 326).

**Process note that must not be lost**: a single-process full-suite run is
OOM-killed (twice, silently, at ~44%). `scripts/run_tiered_suite.sh` — one
process per tier, `-n 4` — is stable and is now the reference runner.

---

## 1. Test Velocity

### Cost profile (measured, `--durations=20`)

| Tier | Walltime | Dominant tests |
|------|----------|-----------------|
| integration | **528s** | `test_demo_update_ladder` 182s, `test_demo_ntm_local` 155s |
| property | 72s | spread thin |
| unit | 38s | thermo cosine 14.3s, NTM copy 11.7s |
| primitives / algorithms / graph / ceec / platform | 17/13/11/7/13s | — |

**Two tests are 64% of the slowest tier.** Integration is 75% of total suite
time, so this is the only optimization that matters right now.

### 1.1 Fix the `ntm_local` oscillation BEFORE optimizing it — P0 — **partially landed**

`test_demo_ntm_local.py:12` documents the metric as *"oscillates 0.79–0.87
(assert floor 0.80)"*. An assertion floor set **inside** an observed
oscillation band is a flake waiting for a busy machine: the same class of
defect as 0.4 and 0.8 above.

- **Done**: the floor is now `0.78`, below the band's observed minimum, with
  the band recorded in the docstring and the reasoning inline. This part needs
  no measurement — the band is in the docstring already, and a threshold
  *inside* a measured range is wrong regardless of what the range is.
- **Not done**: the monotone-summary rewrite. `_run_local`/`_run_bptt` already
  evaluate fresh-batch copy accuracy at 5 checkpoints and return `best_fg`,
  which the demo test discards in favour of a final-iterate recompute — so the
  curve is *already being computed* and thrown away. Returning the curve
  instead of `best_fg` and asserting on the last-two-checkpoint mean is a
  small, clean change, but choosing its floor needs a measurement.
- **Blocked on measurement.** The bptt arm was measured (600/1200/1800/2400/
  3000 → 0.781/0.896/0.906/0.969/0.979); the local3 arm did not finish. See
  §2.7. The plan's instruction to "verify by running it 5× on a loaded
  machine" is not currently affordable.
- Effort: ~30 min once a machine is available.

### 1.2 `test_demo_update_ladder` (182s) — P1

Knobs: `STEPS=600`, `SEEDS=(0,1,2)`, `DEPTH=4`, `CTX=32`, `VOCAB=65`, two
widths. The claim is a **seed-averaged perplexity ordering** (Muon vs euclid
at lr 0.01) with a ± range across seeds.

- The `SEEDS` tuple is the honest lever: 3 → 2 seeds cuts ~33% but weakens the
  ± range that the H4 re-pin depends on. **Measure the per-seed spread first**;
  if the ordering holds with non-overlapping ranges on 2 seeds, take it.
- `STEPS` is *not* a free lever: the pinned perplexity numbers (28.1/28.4/28.5
  at w64, ~35 at w32) are the deliverable. Any reduction is a re-pin, not a
  speedup.
- Alternative that preserves the claim: this is a **language-model** demo on
  CPU. If the suite has a GPU, running it on `cuda` is likely a larger win
  than any parameter cut — measure before cutting science.
- Effort: ~1h including the re-pin.

### 1.3 `test_demo_ntm_local` (155s) — P1, after 1.1

`STEPS=3000`, two arms. Once 1.1 makes the assertion sound, re-measure the
accuracy-vs-steps curve (the same technique used for the NTM copy gate in 0.9)
and cut to the knee. Record the curve in the docstring, as was done there.

### 1.4 Make the fast lane the default lane — P0

Note: this item was **not** written into `AGENTS.md` (rejected — the file
should stay a standing policy, not a running log of this plan). It is recorded
here instead; promote it to `AGENTS.md` §Testing only if it stays true.

- `scripts/run_tiered_suite.sh` is the full-suite command: one process per
  tier, `-n 4`, logs at `logs/tiers/<tier>.log` (`logs/` is gitignored, so no
  ignore change is needed). The OOM rationale belongs in the script's header
  comment — it is there.
- `-n 4` is what every recorded walltime was measured at. `-n auto` is
  untested here; do not quote its speedups.
- **The inner loop needs no new command.** `pyproject.toml`'s `testpaths` is
  already `unit property primitives algorithms acceleration`, so a bare
  `uv run python -m pytest -q` *is* the fast lane. Measured 106s. A
  `make test-fast` target would be a second name for the same thing.
- Reading a tier failure: the `FAILED`/`ERROR` lines at the end of that
  tier's log, or the `=== TIER <name> exit=N walltime=Ns ===` banners.
- **A full-suite run is not a per-commit gate here.** The fast lane covers
  `tests/acceleration` and `tests/primitives`, which is where §2.1's changes
  landed; the integration tier is ~528s of demo tests. Run it at round close.
- Effort: ~15 min, most of it deciding what *not* to add.

### 1.5 Determinism hygiene so timings mean something — P1

Two of the three flakes found (0.4, 0.8) surfaced only because settle work
changed and shifted the global RNG stream. Under `-n 4` each worker has its own
stream, so an unseeded test is not merely flaky, it is *unreproducible*.

- `tests/conftest.py` already sets `OMP_NUM_THREADS=1`; add `torch.use_deterministic_algorithms`
  guidance or an opt-in marker, and document that numeric assertions in tests
  must seed locally.
- Add a lint/convention check (see §2.5) banning bare `torch.randn` in tests
  that assert on values.
- Effort: ~1h.

### 1.6 Re-baseline after the first real optimization — P2

The fix in 0.2 made settles run their full horizon, so **the suite got
intrinsically heavier** — that is why the monolith now OOMs. Re-record the cost
table in this document after §1.1–§1.3 land, and keep it honest.

---

## 2. Correctness Hardening

### 2.1 Undefined names — 11 sites, 6 of them live crashes — **DONE** (`59d13f47`)

See the pass-2 table above. Two notes worth keeping:

- The F821 gate was **not merely incomplete, it was silenced**: all 11 sites
  carried a `# ruff: ignore[undefined-name]` directive. `tests/property/
  test_undefined_name_lock.py` therefore bans the suppression string, not just
  the finding — otherwise the next undefined name walks straight back in.
- `reportUndefinedVariable` cannot be made blocking repo-wide without also
  inheriting the other 2068 pyright findings, so the lock shells out to
  `ruff check --select F821` instead. Same signal, one process, no
  configuration change.

### 2.2 Document the contract that bug 0.2 violated — P0

The settle loop could break on a pre-seeded counter because **the protocol
docstring never said what `_settle_steps_used` meant**. Amend the
`StateDynamics` protocol docstring (and `CompositeState`/telemetry docs) to
state, normatively:

1. `settle` iterates until the convergence criterion or `max_steps`.
2. `_settle_steps_used` counts steps **actually executed** (truth telemetry,
   consumed by `analysis/instruments.py` and `autoscientist/campaign.py`).
3. The early-stop signal is a **separate** flag, reset at the start of every
   `settle` — including each phase of a free/nudged pair.
4. `on_step(step, energy)` fires **once per executed step**, independent of
   whether `track_free_energy_per_iter` is set.

Then add a wiring lock that fails if a new dynamics class reintroduces a
break-on-horizon pattern (grep-level check is sufficient; see §2.5).

**§5.1 supersedes the enforcement half of this item**: once the settle loops
share one driver, the contract is enforced by construction rather than by a
lock watching for a bad pattern. Do the docstring now (it is the specification
the migration is written against), and let §5.1 make it structural.

### 2.3 Lint debt: 684 findings — P2 (Register C scope, per `AGENTS.md`)

Mechanical, high-count, low-risk first:

| Count | Rule | Note |
|---|---|---|
| 222 | `N803` invalid-argument-name | math-notation args (`I_syn`, `W`, `G`) — sanctioned; add to the ignore list with the reason rather than renaming |
| 151 | `RUF105` noqa-comments | the repo's `# ruff: ignore[...]` directive family; canonical-form migration is the known Register C project |
| 94 | `PLW0717` too-many-statements-in-try-clause | needs extraction, not suppression |
| 45 | `PLR6104` non-augmented-assignment | inside `torch.no_grad()` / autograd blocks where `+=` changes semantics — **suppress with reason, do not "fix"** |
| 34 | `E402` | deliberate local imports (circular-import breaks); suppress per-site |

Do **not** enable `RUF105/106/103` until the directive migration is done as one
change — `AGENTS.md` already records that enabling them individually only
churns guard-rails.

### 2.4 pyright: 2079 findings — P2

| Count | Rule |
|---|---|
| 772 | `reportAttributeAccessIssue` |
| 766 | `reportArgumentType` |
| 139 | `reportCallIssue` |
| 85 | `reportOptionalMemberAccess` |
| 82 | `reportReturnType` |

`AGENTS.md` already says repo-wide checking stays basic until the hygiene
pass. This document scopes that pass: pick the **top 3 modules by fan-in**
(`ontology/`, `core/system_trainer/`, `autoscientist/`) and drive those to zero
first, then ratchet — a CI check that fails only on *changed* files, as
`pre-commit` already does for ruff.

### 2.5 Test-quality ratchets — P1

Every defect in §0 was caught by a human, not by the suite. Cheap structural
guards that would have caught them:

- **Ban vacuous assertions.** `assert isinstance(x, list)` proves nothing.
  Add a check for `assert isinstance(...)` / `assert x is not None` as the
  *sole* assertion in a test function.
- **Ban unseeded RNG in value-asserting tests** (§1.5).
- **Ban environment-dependent rendering asserts.** A Rich/terminal-width
  assertion must pin the width (0.4's sibling: the dashboard test failed only
  under `pytest -n`).
- **Ban asserting the opposite of a test's name** — cheap to check by eye, and
  it happened (0.8).
- **Lock the demo gallery** — already exists (`test_gallery_lock.py`); keep
  re-pinning deliberate, as done in this pass.

### 2.7 New: the activation-derivative contract is undefined — P2

Found by §2.1. `_apply_activation_derivative` (in
`computronium/acceleration/fa_kernels.py`, retained for `FAKernelBackend`)
branches on the activation module, and its branches **disagree about what
`h_curr` is**:

- Tanh: `grad * (1 - h**2)` — correct iff `h` is the **post**-activation output.
- GELU: `grad * (cdf(h/√2) + h·pdf)` — correct iff `h` is the **pre**-activation input.
- ReLU (`h > 0`) and SiLU (`σ(h)(1 + h(1-σ(h)))`) are correct either way, which
  is why the inconsistency never showed.

Neither convention is wrong on its own; having both in one function means at
least one branch is. **Do not guess.** The cluster is unreachable from
production (zero callers after §2.1) and untested, so nothing is currently
wrong in a run — but the function is a trap for whoever wires it up, and it is
the last remaining undefined in the FA kernel module.

Decision needed: is `activations[i+1]` in the credit kernels the pre- or
post-activation value? Answer it from the producer, then fix or delete.

### 2.8 New: measurement capacity — P1, process

The §0 pass recorded that a single-process full-suite run is OOM-killed. That
is not the only limit: **`test_demo_ntm_local` was also killed mid-run** while
measuring the §1.1 curve, on a box at load average 8.4 shared with other
users. The bptt arm completed (0.781/0.896/0.906/0.969/0.979 at
600/1200/1800/2400/3000); the local3 arm died after its 600-step checkpoint.

Two consequences for the rest of this document:

1. **Integration-tier numbers here are not reproducible on demand.** §1.2,
  §1.3 and §1.6 all rest on re-measuring demos that may not survive a run.
  Budget for retries, or defer them to a quiet window.
2. **A backgrounded run that dies leaves no trace.** The log ended mid-curve
   with no pytest summary and no traceback. A killed process is
   indistinguishable from a hung one unless you check for the summary line —
   `pgrep -f <testname>` is not a substitute, because it matches the polling
   command itself. Check for the summary, or run in the foreground under
   `timeout`.

### 2.6 Keep the science honest when the numbers move — P2

0.3 changed every energy-based result in the repo, and the demo records had to
be re-pinned (`docs/figures/run_records/*.json` + `manifest.json`). That is
correct behaviour, but it is manual and easy to skip.

- When a fix changes numerics, the PR description should state which pinned
  artifacts moved and why.
- Consider recording the settle horizon in the run record so a future drift
  lock can distinguish "the algorithm changed" from "the environment changed".

---

## 3. Structure and Maintainability

### 3.1 `computronium/deployment.py` shadows `computronium/deployment/` — P1

Both exist (3,408 lines total). A module and a package with the same name in
one parent directory is an import-resolution footgun that no linter in the
current set flags. Either fold the module into the package or rename it
(`deployment_service.py`); decide by what the CLI actually imports.

### 3.2 Repository hygiene — P2

- Repo is **7.9G**: `.venv` 6.7G (ignored), `data/` 878M, `logs/` 60M,
  `artifacts/` 50M, `checkpoints/` 24M, `docs/` 8.0M. Git pack is 20.7M.
- Ignore status verified: `data/`, `logs/`, `artifacts/`, `checkpoints/` are all
  ignored; `docs/figures/` is **tracked** (correct — it is the pinned gallery,
  re-pinned deliberately in this pass).
- The open question is not tracking but **reproducibility**: a research artifact
  nobody can regenerate is a finding. Confirm the `data/` and `artifacts/`
  contents are re-derivable from a seed + task id, and document the command.
- `docs/archive/` is 5.1M of superseded plans. The web-UI era already had one
  archival pass (`0c8e5a2a`); decide whether archive lives in-tree or in a
  cold store, and record the decision.

### 3.3 Finish `TODO33`'s open item — P3

`TODO33` §11 "Duplicate Strategy Files (INVESTIGATE)" was left open. With the
settle/credit contract now pinned (§2.2), a duplicate-strategy sweep can be
judged on behaviour rather than guesswork.

---

## 4. Preparing for the Presentation Layer (CLI first, UI later)

The removed dashboard failed for a structural reason worth not repeating: its
logic lived *inside* the view. This section is the contract that prevents a
recurrence, and it is deliberately render-agnostic — the CLI is the first
consumer, not the only one.

### 4.1 The layering rule — P0

```
domain core (no I/O, no network, no render imports)
   └── presenters (pure: state -> view-model)
          └── renderers (text/rich, static image, notebook, future UI)
```

- **No renderer may contain science.** Every number a view shows must be
  produced by a core/presenter function that has its own test. This is exactly
  what the surviving `figure_spec` / `bars_panel` construction already does,
  and it is why the gallery manifest lock was a viable drift guard.
- **No core module may import a renderer.** The tree violates this today
  (`autoscientist` → `visualization`, §5.2): fix those violations *before*
  adding the lint check, or it fails on day one. §5.2 also leaves a clean
  baseline for the check in §2.5.
- Rendering deps (`plotly`, `matplotlib`, `rich`) stay **optional extras** and
  must not be import-time requirements of `import computronium`. Verify with a
  bare-env import test, which the `deploy`/`plot` extras make possible.

### 4.2 Live telemetry is now a real channel — P1

0.4 fixed `on_step` so it fires every settle step regardless of tracking
settings. That is precisely the primitive a live view needs, and it was
silently dead until now.

- Thread `on_step` from the trainer/campaign into the existing
  `autoscientist/stream_protocol.py` events, and from there into the daemon's
  retained `/ws/stream`.
- Contract: progress events carry `(step, energy, phase)`; the consumer decides
  presentation. Test the protocol with a recording sink — no socket required.
- This is the substrate for both a `comp watch` CLI and any future UI, and it
  is why fixing 0.4 mattered beyond the test suite.

### 4.3 A stable read surface for every view — P1

`campaign_readers.py` (the read-only artifact loaders that survived the
dashboard removal) is the correct shape: views read artifacts, they do not
recompute them. Before adding any view:

- Give it a completeness contract (what a reader guarantees when a run was
  interrupted — the interrupted-run case is where a UI lies to the user).
- Make the WAL-cache correctness (0.5) part of that contract: a reader that
  can serve stale rows is worse than no reader.

### 4.4 Renderer registry, mirroring the dispatch tables — P2

0.6's lesson: a source-text-scraping lock silently degraded when dispatch
became table-driven. When the renderer set grows, register backends in a table
(`_RENDERERS: dict[str, Callable[[ViewModel], None]]`) and write the lock
against the **table**, not the source text. The same applies to the
`_GEOMETRY_DISPATCH` / `_GEOMETRY_FACTORIES` pattern already in the codebase —
it is the pattern to copy, and the geometry wiring lock is now the reference
test for how to lock it.

### 4.5 Non-goals, written down so they survive — P0

- No network/websocket dependency in the domain core.
- No view-layer state that cannot be rebuilt from a run artifact.
- No new top-level dependency without a decision recorded here.
- No UI work starts before §4.1's layering rule has a lint check behind it.

---

## 5. Architectural Refactors

Four structural changes, each justified by duplication that has already caused
damage rather than by aesthetic preference. Ranked by leverage.

### 5.1 Collapse the 11 hand-written settle loops into one driver — P0

**Evidence.** `for step in range(self.config.max_steps)` appears **11 times
across 6 dynamics classes** — Diffusion 2, EnergyMinimization 2, PC-ALM 2,
PredictiveSettling 3, ErrorPredictiveCoding 1, Lazy 1 — with **24 distinct
convergence-check sites**.

That count is the argument. The dead-early-stop defect of §0.2 existed in **4
of those copies simultaneously**: not four independent mistakes, but one
copy-paste and a flaw that travelled with it. The repair had to be applied by
hand at 8 sites. The duplication is the bug factory.

**Target shape.** One driver owns the control flow and the semantics §2.2
specifies — horizon accounting, convergence latch, checkpointing cadence,
per-step telemetry emission, early stop:

```
_settle_loop(step_fn, config, *, telemetry, on_step, use_checkpointing)
```

Each dynamics supplies a `step_fn` (advance one iteration) and a `telemetry`
extractor (the scalar a progress consumer should see). Eleven loops become
eleven three-line declarations, and the invariant has one implementation
instead of eleven.

**Delivers.** §2.2's contract stops being a document and becomes code; the
horizon-telemetry lock (§2.5) gets a single choke point to guard.

**Risk — state this before starting.** This is not free. The 11 loops carry
per-class quirks: compiled fast paths that cannot early-stop, PC-ALM dual
variables and augmented-Lagrangian telemetry, LIF reset semantics, per-layer
drive in `SpikeIntegrationDynamics`. A "one driver" that grows 11 flag
combinations relocates the complexity rather than removing it, and hides it
behind parameterisation.

**Sequencing (incremental, each step green).**
1. Driver + migrate the two `EnergyMinimizationDynamics` paths (eager,
   checkpointed) — these are the paths the §0.2 lock already covers, so
   correctness is directly comparable.
2. Migrate `PCALMDynamics` (the other dual-variable case).
3. Migrate the rest; retire the duplicated convergence checks.
4. Keep compiled fast paths *outside* the driver until the eager paths are
   proven — they are a genuinely different execution mode, not a flag.

**Definition of done.** `grep -c "for step in range(self.config.max_steps)"`
returns 0 outside the driver, and the full suite plus the §0.2 mutation test
(does the lock still catch a reintroduced break-on-horizon?) are green.

### 5.2 Break the domain → presentation inversion — P0

**Evidence.** Domain/orchestration code importing the view layer:

```
autoscientist/broad_map.py        → visualization.atlas: pareto_top, kb_load_cached, UNBOUNDED_ROWS
autoscientist/campaign_readers.py → visualization.atlas: pareto_top
```

Pareto dominance is implemented **three times**: `analysis/pareto.py`,
`hyperopt/metrics.py` (`non_dominated_indices`, `non_dominated_sort`), and
`visualization/atlas.py::pareto_top` — and the domain imports the
*visualization* copy.

This already caused harm: the KB read cache lives in `visualization/atlas.py`,
so the WAL-correctness fix of §0.5 landed **in the presentation layer**,
because that is where the function happened to live. A correctness invariant
for long-lived readers now lives in a module named for charts.

**Target shape.**
- Pareto math → `computronium/analysis/` as the single implementation;
  `hyperopt/metrics.py` and `visualization/atlas.py` become consumers.
- KB read cache and the `UNBOUNDED_ROWS` sentinel → `computronium/knowledge/`
  (the layer that owns persistence and already knows about WAL).
- `visualization/` depends on `analysis/` + `knowledge/`; never the reverse.
- `cli/gallery.py` importing `visualization.gallery` is **correct** and stays.

**Delivers.** §4.1's layering rule with a real precedent in-tree, and §2.5's
"no renderer imports in core" check stops being hypothetical.

**Sequencing.** Move the cache and the Pareto function first (small, testable,
and §0.5's lock already covers the cache), then re-point the three importers.
Effort: ~4h.

### 5.3 Reconcile the two state algebras — P1

**Evidence.** `SystemState` (flat pipeline record: `x, y, activations,
free_state, nudged_state, metrics, dual_vars, spike_rasters`) versus
`CompositeState` (`activity` / `plastic` / `substrate` — the x_t / ψ_t / σ_t
view). The protocol declares `settle(state: CompositeState)`, but the working
path passes `SystemState`; pyright rejects it, and 11 classes carry an
annotation that contradicts runtime.

These are not duplicates — they are two deliberate views (5-layer pipeline
versus 3 dynamical axes) — but the *type contract names the model the code
does not use*, which is a standing source of annotation debt and a trap for
the next contributor.

**Target shape.** A decision, not a merge: either `CompositeState` becomes the
canonical record with an explicit flat adapter, or the protocol annotations
move to `SystemState` and `CompositeState` is reserved for the substrate/
plasticity layers that actually use it. Whichever is chosen, add a
`TypeIs`-based narrowing helper so callers can go between views without
`isinstance` chains.

**Sequencing.** Write the decision down before touching code; then land it
annotation-first (no behaviour change), then migrate. Effort: ~1d including
the decision. **Do not start before §5.1 lands** — the driver is where the
state type is passed most, so doing them together multiplies the diff.

### 5.4 Derive the registries; stop hand-synchronizing exports — P2

**Evidence.** Adding one geometry primitive touches **seven** surfaces:
`GeometryConfig.<factory>()`, `_GEOMETRY_DISPATCH`, `_GEOMETRY_FACTORIES`,
ontology `__all__`, root `__all__`, root `_LAZY`, and the root `TYPE_CHECKING`
import block. The existence of a wiring-lock test **and** an eight-step
checklist in `AGENTS.md` is itself the smell — both exist only because the
surfaces are hand-kept in sync. §0.6 is what that costs: a lock that silently
degraded to "0 of 10 classes" for an unknown number of commits.

**Target shape.** Dispatch tables derived from the config factories (one
source of truth), and `__all__` / `_LAZY` generated rather than maintained.
The existing wiring locks then assert *derived* invariants instead of
re-encoding a hand-written list.

**Sequencing.** Same treatment as `ontology/dynamics` and the state
primitives; reuse the corrected lock shape from §0.6 (assert against the
table, never against source text). Effort: ~1d per layer.

### 5.5 Sequencing summary

| Order | Item | Why here |
|-------|------|----------|
| 1st | 5.1 | Deletes duplication *and* a bug class; §2.2's contract lands as code |
| 2nd | 5.2 | Small, testable, unblocks §4.1's precedent |
| 3rd | 5.3 | Needs a decision, and wants §5.1 settled first |
| 4th | 5.4 | Mechanical, benefits from 5.1–5.3 having reduced the surface count |

---

## Execution Order

Phase A is **done except §1.1's measurement**, which is blocked by §2.8.

| Phase | Items | Effort | Gate | State |
|-------|-------|--------|------|-------|
| **A — determinism** | 1.1, 2.1, 1.4 | ~3h | fast lane green 5× in a row | 2.1 **done**; 1.1 floor **done**, curve blocked; 1.4 open |
| **B — contract** | 2.2, 2.5, 4.1 lint check | ~3h | `F821` blocking; settle-horizon lock extended to all dynamics | open (`F821` blocking **done**, via §2.1) |
| **C — velocity** | 1.2, 1.3, 1.5, 1.6 | ~4h | integration tier < 300s, re-baselined cost table | open — **re-measurement needed, see §2.8** |
| **D — structure** | 3.1, 2.3 (mechanical), 2.4 (top 3 modules) | ~1d | repo-wide lint trend down; pyright ratchet active | open |
| **E — presentation** | 4.2, 4.3, 4.4 | ~1d | `comp watch` streams a live run headfully | open |
| **F — architecture** | 5.1 → 5.2 → 5.3 → 5.4 | ~1w | 11 settle loops → 1 driver; Pareto in one layer; registries derived | open |

**Recommended next step** (cheapest, unblocked, high value): **§2.2**, the
settle-contract docstring. It is pure documentation, needs no measurement, and
it is the specification §5.1 is written against — so writing it now is what
makes Phase F cheaper later, not a detour from it.

The standing rule from §0 still holds: Phase F is last because a badly
parameterized settle driver relocates complexity rather than removing it. Do it
against a green, deterministic suite, not to rescue a flaky one.

---

## Verification After Each Phase

```bash
# Fast lane (measured 106s, 3147 passed) — the inner loop and the per-commit gate.
# A bare `uv run python -m pytest -q` runs exactly this (pyproject testpaths).
uv run python -m pytest tests/unit tests/property tests/primitives \
    tests/algorithms tests/acceleration -q -n 4

# Full suite, per tier, one process each — round close only.
# The single-process monolith is OOM-killed at ~44%; see also §2.8.
./scripts/run_tiered_suite.sh

# Gates on changed files
uv run ruff format --check <changed>
uv run ruff check <changed>
uv run ruff check --select F821 computronium tests scripts packages
uv run pyright <changed>             # strict for new/rewritten modules
uv run python -c "import optuna, scipy, torchvision, pytest"
```

`F821` is enforced by `tests/property/test_undefined_name_lock.py` in the
fast lane, so the explicit `--select F821` run above is for iterating on a
fix, not for the gate.

Re-pin `docs/figures/manifest.json` via the gallery lock whenever demo numerics
move, and say so in the commit body.

---

## Notes

- **A defect found by making a path callable is a defect class of its own.**
  §2.1's two `NameError`s were not the only thing on the FA credit path: the
  first call into it produced a compile error, then a silently wrong tensor,
  then a shape error. Four defects, one untested function, zero of them
  visible from the outside. §2.5's ratchets are worth more than they look.
- **Shape-only assertions are not assertions.** The first repair of
  `_fa_batched_outer_kernel` (`post * tl.trans(pre)`) produced a tensor of
  exactly the right shape that was constant along an entire axis, and would
  have passed any test written from the signature. Compare against the eager
  path; do not assert on shape.

- **Backwards compatibility: NONE** (per `AGENTS.md`) — when a lock disagrees
  with the code, the lock is wrong until proven otherwise; 0.6 and 0.8 were
  both stale locks, not code defects.
- **Few comments; rely on self-documenting code** — but the *measured numbers*
  behind a threshold (learning curves, cost tables, oscillation bands) belong in
  docstrings, or the next person re-inflates them blind. Every reduction in
  §0.9 and §1 carries its measurement for exactly that reason.
- The web-UI removal also left a stale language-server index pointing at deleted
  `computronium/ui/**` files; a clean LSP restart clears it. Nothing in the tree
  references them.
