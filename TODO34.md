# TODO34: Test Velocity, Correctness Hardening, and the Presentation Layer

**Status**: **ACTIVE** — §0 (`ff6528fb`), §2.1 (`59d13f47`), §2.2 (`f06f7629`),
§2.5 (`0faecede`), §4.1 + §5.2 (`5ad96f85`), §1.1 + §1.5, §5.1, and now
**§5.3 (the state-algebra decision)** complete. §1.2–§1.4, §1.6, §2.3–§2.4,
§2.6–§2.7, §3, §4.2–§4.4, §5.4 open. §5.4 is the only item left in Phase F.
(§1.4's substance landed in `fb6bb0f7`, which also found §1.2b.)

Continues the series after `TODO33` (deprecated/legacy cleanup). Where `TODO33`
removed code, this one makes what remains *fast, provable, and ready to be
presented* — the three things the next development push (CLI equivalents, and
whatever UI comes after) will lean on.

§5 (architectural refactors) is the highest-leverage section and the longest
sounding; it is sequenced **last** on purpose. See its own risk notes before
starting it.

---

## Summary of Completed Work

### Pass 8 — §5.3 the state-algebra decision

**The decision** (written into `computronium/ontology/dynamics/_state.py`
before any code changed, per §5.3's sequencing): *neither algebra is
canonical, and the settle contract is the surface they share.* `SystemState`
(flat 5-layer pipeline record) and `CompositeState`
(z_t = activity/plastic/substrate) are both live — the pipeline constructs
one, every `primitives/**/kernel.py` reference and the joint/plasticity
paths construct the other. What was wrong was not their coexistence: it was
that `StateDynamics.settle` **named one of them** while the runtime passed
the other, so 11 dynamics classes carried an annotation pyright rejects and
every implementation `cast` its own return value to satisfy it.

- `SettableState` — a `runtime_checkable` Protocol declaring the seven
  fields both algebras expose (`x, y, activations, free_state, nudged_state,
  loss, metrics`). All 26 `state: CompositeState` annotations and 18
  `-> CompositeState` returns across `_dynamics.py` now name the surface.
- `set_state_field(state, name, value)` — the write side, at the 14 sites
  that write settle output. The Protocol's members are **read-only
  properties** because pyright treats mutable protocol members as invariant,
  and `CompositeState` exposes these fields as properties over its
  `activity` mapping while `SystemState` uses plain fields. Read-only is
  what makes both satisfy the same surface; the setter is real, a read-only
  Protocol just cannot prove it. That is the one concession the decision
  cost, and it is recorded in the module docstring.
- `is_system_state` / `is_composite_state` — `TypeIs` narrowing, replacing
  the package-private `hasattr` duck check and its three `cast`s. The
  composite test is **structural**, not `isinstance`: `computronium.state`
  and `computronium.core.joint.state` are two import paths to one record,
  and duck-typed callers must not care which they hold.
- Fields outside the surface (`energy`, `dual_vars`, `spike_counts`,
  `spike_rasters`) are `SystemState`-only and stay on the `getattr`/`setattr`
  accessors — that asymmetry is now the *documented* encoding of "optional,
  absent on the z_t view" rather than an unexplained one. A test asserts
  the asymmetry, so it cannot quietly change.

**Rejected alternative, with the reason recorded**: making `CompositeState`
canonical behind a flat adapter. The compat properties on `CompositeState`
(`x`/`activations`/`free_state`/`nudged_state`) are read by the pipeline,
the distributed trainer *and* the reference kernels, so the "adapter" would
have had to be the default representation — a much larger diff for a naming
preference.

`pyright computronium/ontology/dynamics/` is **0 errors** (was 3 after the
first cut, which is how the invariance and read-only facts above were
found — the type checker is what made the decision concrete).

`tests/property/test_state_algebra_lock.py` (23 tests, 2.8s): the surface
is satisfied by both real classes; narrowing is mutually exclusive; the
optional fields are system-only; a **source lock** over the package AST that
fails if a settle signature names an algebra again (with `_state.py`
exempt, as the module that *defines* the contract); and the **behavioural**
half a source lock cannot see — every registered dynamics class settles
from both algebras and returns the algebra it was given (16 parametrised
cases). Probe-the-probe included, per §0.6.

Fast lane after: **3196 passed, 119 skipped, 26 xfailed, 1 xpassed in
91s**. No numerics moved; no demo re-pin owed.

### Pass 7 — §1.1's curve and §1.5's ratchet

The machine was quiet for the first time in three passes, so the one
measurement §2.8 had blocked was taken (§1.1's table above), and the
cheapest no-measurement item in Phase C was landed behind it (§1.5's
ratchet). Both are recorded in their own sections; the transferable
result is in Notes: **a defect fixed without a measurement is a defect
whose threshold was guessed**, and the guess here would have been the
0.78 floor the previous pass shipped — which the curve shows is *inside*
the band, exactly as §1.1's own diagnosis said it was.

### Pass 6 — §5.1 the settle driver (flagship)

`computronium/ontology/dynamics/_settle_driver.py` — `run_settle_loop`,
`SettleIterate`, `checkpointed`, `checkpointed_every`. **Ten** hand-written
`for step in range(self.config.max_steps)` loops across six dynamics classes
are now ten three-line declarations; `grep -c "for step in
range(self.config.max_steps)" computronium/ontology/dynamics/` returns 0
outside the driver, which is the plan's definition of done.

**The driver owns the control flow, not the science.** It runs the horizon,
returns the executed-step count, and enforces the ordering that made the 0.2
defect possible — *advance first, observer second* — so no flag can be
consulted in place of the step itself. The convergence predicate and the
telemetry scalar stay with each dynamics class, because §5.1's own risk note
predicted exactly what happens if they move: a driver with eleven flag
combinations relocates complexity instead of removing it. Checkpointing is
carried by the two wrappers rather than a `use_checkpointing` parameter, for
the same reason.

**Three latent telemetry gaps closed for free.** `_settle_recurrent`,
`_eager_layered_steps` and both `DiffusionDynamics` paths ran steps and
**never set `_settle_steps_used` at all** — rule 2 of §2.2's contract, which
no test could see, because §2.2's lock is a *source* lock. They now report
what they execute, and
`TestDriverUniquenessLock::test_every_dynamics_class_reports_its_horizon`
walks every registered dynamics class and asserts it.

**One behaviour fix, found by the ratchet rather than by reading.** The
per-layer LIF loop emitted `on_step` with a constant step index and
incremented the counter only after the layer finished. The §0.4 lock's
`indices == list(range(len(indices)))` caught it immediately — first test
failure, one fix, and the reason that lock was worth writing.

`tests/property/test_settle_driver_lock.py`: driver semantics (horizon, early
stop, step-before-observe, zero horizon), `checkpointed_every` cadence, an AST
**uniqueness** lock over the dynamics package, and a probe-the-probe asserting
the scan still sees the driver's own loop — the §0.6 lesson (a lock that
silently resolved zero of ten classes) applied forward rather than after the
fact.

`TestSettleHorizonSourceLock` (from `f06f7629`) is now redundant for its
original purpose and is kept as a second, independent signal; the driver makes
the invariant unrepresentable, which is what §2.2 predicted §5.1 would allow.

### Pass 5 — §2.5 test-quality ratchets, `0faecede`

`tests/property/test_assertion_quality_lock.py` bans a test whose only
assertion is `isinstance(x, <builtin>)`. Domain types are exempt — "the
registry factory returns an instance of the class the registry claims" is a
real claim no annotation makes.

**The plan's proposed `assert x is not None` clause was tried and dropped.**
14 false positives on first run: `assert selected_experiment is None` is how
a dozen tests state "this lookup finds nothing", which is *more* specific
than a type check, not less. Separating "restates a non-optional annotation"
from "asserts a sentinel" needs return-type analysis — §2.4's job. A lock
with false positives gets switched off, so the narrower rule is the useful
one; the docstring records this so it is not re-attempted blind.

Nine real vacuous assertions strengthened, each to the claim its own comment
*said* it was making. One immediately failed: the kernel-registry test
asserted the registry "is functional" and MEP had no CPU backend, because
registration is import-order-dependent and the test never imported the module
that registers it.

Two §2.5 rules deliberately **not** implemented, with reasons in the module
docstring: unseeded-RNG detection (needs dataflow, not a regex) and
asserting-the-opposite-of-the-name (the plan itself says "cheap to check by
eye"; a regex would be theatre).

### Pass 4 — §4.1 + §5.2 layering inversion, `5ad96f85`

`broad_map.py` and `campaign_readers.py` imported from
`visualization/atlas.py` — not to draw, but for Pareto front selection and a
WAL-aware cache key. That second one is the argument: the cache key is
correct only because it covers SQLite's `-wal` sidecar, so a *persistence*
invariant was living in a charting module. That is exactly how §0.5's fix
came to be applied in the wrong layer.

- `computronium/analysis/dominance.py` — `pareto_top` + its two kernels.
  Deliberately **not** folded into the existing `analysis/pareto.py`, which
  imports plotly: putting domain code there would weaken the rule being
  established.
- `computronium/knowledge/kb_cache.py` — the cache, its fingerprint,
  `UNBOUNDED_ROWS`. Persistence invariant now sits in the persistence layer.

`test_layering_lock.py` enforces the rule over the AST **including
function-local imports** — all 5 violations were function-local, which is
how they survived. Exemptions require a reason and must name a real
directory. §4.1's operative claim is tested directly: a subprocess imports
`computronium` and asserts no renderer reaches `sys.modules` (it loads none).

### Pass 3 — §2.2 settle contract, `f06f7629`

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
| integration | **670s** | `test_demo_ntm_local` 231s, `test_demo_update_ladder` 183s |
| property | 74s | spread thin |
| unit | 34s | — |
| primitives / algorithms / graph / ceec / platform | 14/11/8/5/11s | — |

Re-measured 2026-09-25 after §5.1 (the numbers §0 recorded were from before
the settle-horizon fix made every settle run its full budget, so the suite got
intrinsically heavier — §1.6's prediction, confirmed). Two tests are 62% of
the slowest tier; both are now `slow` (§1.2, §1.3), leaving integration at
≈256s of real work.


### 1.1 Fix the `ntm_local` oscillation BEFORE optimizing it — P0 — **DONE**

`test_demo_ntm_local.py:12` documented the metric as *"oscillates 0.79–0.87
(assert floor 0.80)"*. An assertion floor set **inside** an observed
oscillation band is a flake waiting for a busy machine: the same class of
defect as 0.4 and 0.8 above.

**The curve is now measured (200-step eval cadence, seed 0,
`logs/todo34_s11_{bptt,local3}.log`, 83s / 93s per arm).**

| step | 200 | 600 | 1000 | 1400 | 1600 | 1800 | 2000 | 2200 | 2400 | 2600 | 2800 | 3000 |
|------|-----|-----|------|------|------|------|------|------|------|------|------|------|
| bptt | 0.729 | 0.781 | 0.833 | 0.938 | 0.917 | 0.906 | 0.958 | 0.969 | 0.969 | 0.990 | 0.979 | 0.979 |
| local3 | 0.500 | 0.521 | 0.573 | 0.812 | 0.865 | 0.844 | 0.729 | 0.708 | 0.750 | 0.854 | **0.594** | 0.833 |

- **The tail-3 mean, not a checkpoint, is the claim.** local3's last three
  200-step checkpoints are 0.854/0.594/0.833 — a floor on any single one of
  them is a coin flip. At the test's 600-step cadence the tail-3 means are
  bptt **0.918** and local3 **0.809**; the floors are 0.88 and 0.72, below
  both. The runners now return the whole curve (`_FreshCurve` in
  `scripts/probes/w8_ntm_copy.py`, `--eval-every` on the probe CLI), and the
  test asserts the tail mean plus the arm ordering.
- **`STEPS` is not a free lever, and this measurement says so.** local3
  reaches its plateau at ~1600, but bptt is 0.906 at 1800 and 0.969 at 2400,
  so the 0.88 bptt floor pins `STEPS >= 2400`. Cutting 3000 would be a
  re-pin that buys ~40s, not a speedup — the same conclusion §1.2 reached
  for the ladder. `STEPS` stays.
- **The pinned figure did not move.** The record and its `figure_spec` keep
  the final-iterate values (0.979 / 0.833, byte-identical to before), so
  `manifest.json` is untouched and no re-pin is owed. The cost is recorded
  as a known gap: the *figure* shows a noisier statistic than the *test*
  claims. Closing it means emitting the tail mean in the record, which
  re-pins the manifest and needs one quiet 200s demo run.

### 1.2 `test_demo_update_ladder` (183s) — P1 — **demoted to `slow`**

`@pytest.mark.slow`. The claim is a seed-averaged perplexity ordering whose
pinned numbers (28.1/28.4/28.5 at w64, ~35 at w32) are the deliverable, and
the plan's own analysis says `STEPS` is *not* a free lever — any reduction is
a re-pin, not a speedup. The honest lever remains `SEEDS` 3 → 2, and that
weakens the ± range the H4 re-pin depends on, so it needs the per-seed spread
measured first.

### 1.3 `test_demo_ntm_local` (231s) — P1 — **demoted to `slow`**

`@pytest.mark.slow`. §1.1's monotone-summary rewrite is still open and still
needs a measurement; demoting the test is not the same as fixing it, and the
curve is still unmeasured (the bptt arm reads 0.781/0.896/0.906/0.969/0.979 at
600/1200/1800/2400/3000, so the 0.97 bptt floor pins that arm near the full
budget; the local3 arm is the one worth measuring).

**What demotion actually bought** (measured 2026-09-25, integration tier
670s): the two demos are 414s of it — 62% — and the marker moves them out of
the profile the runner and every bare `pytest` executes. Remaining
integration ≈ 256s by arithmetic on the tier's `--durations=20`; not
re-measured, because re-measuring to confirm a subtraction is the kind of
wait this section exists to remove.

**The honest cost, stated.** These tests are the gallery's run records, so
the manifest pin is no longer verified by the default profile. That is only
acceptable because the runner now has a pass that runs them:
`./scripts/run_tiered_suite.sh --with-slow`.

### 1.2b New: the reference runner silently skipped every `slow` test — P1, fixed

`pyproject.toml`'s `addopts` carries `-m 'not slow and not benchmark and not
llm'`. `scripts/run_tiered_suite.sh` inherited it, so **26 slow tests — every
heavy demo in the tree — never ran under the documented full-suite command**,
including the ones that emit and pin the gallery records. A "full suite,
3516 passed" figure could not have included them.

The runner now takes `--with-slow` and runs a final `slow` pass
(`logs/tiers/slow.log`). Round close: always pass the flag. Inner loop: never.
This is §1.4's real content — the profile split was already there, it was just
undocumented and unenforceable.

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

### 1.5 Determinism hygiene so timings mean something — P1 — **ratchet landed**

Two of the three flakes found (0.4, 0.8) surfaced only because settle work
changed and shifted the global RNG stream. Under `-n 4` each worker has its own
stream, so an unseeded test is not merely flaky, it is *unreproducible*.

- `tests/conftest.py`'s module docstring now states the rule (numeric
  assertions must seed locally; shape-only asserts are exempt because a
  draw's values cannot change its shape) and points at the lock.
- `tests/property/test_rng_seed_lock.py` ratchets it. A test is flagged only
  when it calls a global `torch.<rand*|randint|randperm|normal>` directly,
  nothing in the function or module seeds a generator, **and** it asserts on a
  number (ordered comparison, `allclose`, `isclose`, `approx`). Measured
  population: **334 unseeded tests, 116 flagged, across 42 files** — the
  shape-only exemption is the difference between a useful rule and one that
  gets switched off (§2.5's lesson).
- It is a **ratchet, not a ban**: `_BASELINE` records what exists, new
  entries fail, a shrunken baseline fails as stale, and a
  `test_baseline_is_non_trivial` guard asserts the scan still sees ≥30
  files / ≥100 tests — §0.6's lesson applied forward.
- **The probe-the-probe earned its keep immediately.** The first version
  detected module-level seeding only for bare `ast.Call` statements, missing
  that `torch.manual_seed(0)` at module scope is an `ast.Expr`. The lock
  would have flagged seeded modules as violations. Caught by a parametrised
  case, not by reading.
- **Not done**: `torch.use_deterministic_algorithms`. It is not opt-in here —
  it is a global switch, and turning it on repo-wide will raise on any op
  without a deterministic kernel, which is a different (and larger)
  investigation than a ratchet. No numeric assertion in the suite needs it;
  the seeding rule is the part that pays.
- Remaining: seeding the 116. That is mechanical and safe to delegate in
  batches — each is one `torch.manual_seed(0)` and a baseline-line delete.
- Effort: ~1h, of which the ratchet is done.

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

### 2.2 Document the contract that bug 0.2 violated — **DONE** (`f06f7629`)

The `StateDynamics` protocol docstring now states the four rules
normatively: settle runs to convergence or `max_steps`; `_settle_steps_used`
counts steps *actually executed*; the stop signal is the separate `_converged`
flag reset by `_note_settle_start()` on every settle including each phase of
a free/nudged pair; `on_step` fires per executed step regardless of
`track_free_energy_per_iter`.

It also records the one **legitimate** exception — whole-graph paths
(`_settle_compiled`, PC-ALM's full-horizon sweep) seed
`_settle_steps_used = max_steps`, which is the truth for a path that cannot
early-stop. Without that note, the exception reads as the bug and the next
person deletes correct code.

`TestSettleHorizonSourceLock` walks the AST for `_settle_steps_used` in any
boolean position, so the prohibition *in the docstring* does not trip it, and
a second test asserts the four rule markers survive docstring edits.
Mutation-checked by injecting the defect into a live loop.

The behavioural half of the original item — "a wiring lock that fails if a new
dynamics class reintroduces break-on-horizon" — is what the AST check is.
**§5.1 supersedes it structurally**: one driver makes the invariant
unrepresentable rather than policed.

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

### 2.5 Test-quality ratchets — **PARTLY DONE** (`0faecede`)

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

### 2.9 New: `rich` is a hard dependency — P3

`pyproject.toml` lists `rich` in `[project] dependencies`. §4.1 names `rich`
as a rendering dep that should be an optional extra.

**Measured: nothing on `import computronium`'s path reaches it** — a
subprocess probe confirms no renderer (rich, plotly, matplotlib, altair,
bokeh, dash) lands in `sys.modules`. So §4.1's operative requirement holds
today, and `test_layering_lock.py::test_import_computronium_pulls_no_renderer`
now guards it. The declaration is simply louder than the behaviour.

Move `rich` to an extra when something in `computronium.core.logging`
actually uses it; until then the lock is what protects the invariant, and
that is the cheaper arrangement. Recorded so nobody "discovers" the
hard-dependency later and re-breaks a property that currently holds.

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

### 4.1 The layering rule — **DONE** (`5ad96f85`)

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

### 5.1 Collapse the hand-written settle loops into one driver — **DONE**

**Evidence (measured).** `for step in range(self.config.max_steps)` appeared
**10 times** across the dynamics module — Diffusion 2, EnergyMinimization 2,
PC-ALM 2, PredictiveSettling 3, ErrorPredictiveCoding 1, Lazy 1 — plus two
per-layer LIF loops over the same horizon, with **24 distinct
convergence-check sites**. (The plan's count of 11 was one high; the two
PC-ALM copies were counted separately at one site each.)

That count was the argument. The dead-early-stop defect of §0.2 existed in
**4 of those copies simultaneously**: not four independent mistakes, but one
copy-paste and a flaw that travelled with it.

**Landed as described in Pass 6 above.** Driver + checkpointing wrappers in
`computronium/ontology/dynamics/_settle_driver.py`; all ten loops migrated;
`tests/property/test_settle_driver_lock.py` guards both the driver's semantics
and its uniqueness in the package.

**Residual risk, stated honestly.** The driver did not remove the per-class
quirks — PC-ALM's augmented-Lagrangian telemetry, the LIF drive-per-layer
structure, the compiled whole-graph paths — because those are science, not
control flow. What it removed is the part that broke: horizon accounting and
early-stop ordering now have one implementation. The plan's own warning
against a driver grown by parameterisation was the design constraint, and it
is met: the driver has two parameters (`max_steps`, `after_step`).

### 5.2 Break the domain → presentation inversion — **DONE** (`5ad96f85`)

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

### 5.3 Reconcile the two state algebras — P1 — **DONE**

**Decision taken** (recorded in `computronium/ontology/dynamics/_state.py`):
neither algebra is canonical; the settle contract is the **surface** both
expose (`SettableState`), with `TypeIs` narrowing for callers that need a
concrete view. See Pass 8 for what landed and why the "make
`CompositeState` canonical" alternative was rejected on measurement.

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

### 5.6 New: three more hand-written settle loops outside `StateDynamics` — P2

Found by §5.1's uniqueness lock, which is scoped to
`computronium/ontology/dynamics/` and so cannot see them.
`computronium/core/local_learning/settling.py` carries its own settle loops —
lines ~397, ~439 (model-level fixed-point settling with its own
`steps_taken`, `convergence_start` and custom `_check_converged` hook) and
~1150 (adjoint iteration for implicit differentiation). The first two are the
same contract §2.2 states, re-implemented for a layer the protocol does not
cover; the third is a backward sweep and is genuinely a different thing.

They are *not* migrated blindly. `local_learning` settles user-supplied
models whose `_step` is `object`-typed and may checkpoint internally, so the
driver's `SettleIterate` box is the only part that would transfer unchanged.
Decide whether `StateDynamicsConfig.max_steps` and `convergence_*` should
apply to model settling at all; if yes, the driver is free, if no, write down
that the two are separate contracts so the next reader does not assume
otherwise.

### 5.7 New: the LIF horizon counts layers, not steps — P3, needs a decision

`SpikeIntegrationDynamics._settle_layered` integrates each layer against its
own (already-settled) drive, so a settle executes `max_steps` **per layer**:
a 3-layer network reports `_settle_steps_used = 90` at `max_steps=30`. §2.2
rule 2 says the field "counts steps actually executed", which is true, but
every consumer of the field (`analysis/instruments.py`,
`autoscientist/campaign.py`) reads it as *a horizon*, and a number three
times the configured horizon is a lie to a log reader even when the code is
correct. `TestDriverUniquenessLock` deliberately does **not** assert
`horizon <= max_steps` — the ambiguity is recorded rather than locked in.
Decide: per-layer count summed (today), per-layer max, or separate
`steps_used` / `layers` fields — and then make the lock assert it.

### 5.8 New: the credit layer has §5.3's defect, suppressed — P2

Found while landing §5.3. `ontology/credit.py` annotates **17** signatures
`SystemState` (`compute_pseudo_gradient(states: Mapping[Phase, SystemState])`,
every `free_state: SystemState` helper) — the *mirror image* of the settle
contract's error, and equally wrong at runtime: every
`primitives/credit_assignment/*/{kernel,reference}.py` builds
`CompositeState` per phase and calls the credit with it, silencing the
mismatch at the call site with `# type: ignore[arg-type]`. There are **120**
such directives repo-wide, so this is the same debt class one layer down,
and the settle surface is the right contract to extend rather than a
`SystemState`/`CompositeState` pair to choose between.

**Sequencing.** Annotation-first, exactly as §5.3: `SettableState` already
covers what the credit reads, so the 17 sites are a mechanical retype and
the `# type: ignore[arg-type]` at those call sites can be deleted
afterwards — *those* deletions are the proof, because each one either
disappears or becomes a real error to fix. Do it with §5.4: both jobs are
"stop hand-maintaining a surface that a table or a Protocol can state once."

### 5.9 New: three `getattr` accessors are now redundant — P3

`_get_state_x` / `_get_state_activations` / `_get_state_free_state` in
`_dynamics.py` exist to tolerate a state that might not carry the field.
`StateLike` is now `SettableState`, so the field is guaranteed and the
accessor hides a type error instead of surfacing one. Replacing them with
direct reads is a small diff, but it needs one audit first: the lazy and
compiled whole-graph paths pass duck-typed records from outside the
protocol's coverage, and that is exactly the kind of assumption a
mechanical sweep gets wrong. `_get_state_dual_vars` was **deleted** in this
pass (zero callers; its `CompositeState` branch is inlined by PC-ALM and its
"backwards compat" alias had no users in-tree — `AGENTS.md` grants no
backwards compatibility).

### 5.5 Sequencing summary

| Order | Item | Why here | State |
|-------|------|----------|-------|
| 1st | 5.1 | Deletes duplication *and* a bug class; §2.2's contract lands as code | **done** |
| 2nd | 5.2 | Small, testable, unblocks §4.1's precedent | **done** (`5ad96f85`) |
| 3rd | 5.3 | Needs a decision, and wanted §5.1 settled first | **done** (Pass 8) |
| 4th | 5.4 | Mechanical, benefits from 5.1–5.3 having reduced the surface count | open |
| 5th | 5.6, 5.7 | Both are decisions the driver exposed, not new work | open |
| — | 5.8, 5.9 | Found by 5.3's own retype; annotation-first like 5.3 | open |

5.2 was pulled forward because §4.1's lint check fails on day one otherwise —
the plan says so explicitly, and it was right. 5.1 then followed, and the
§5 risk note ("a driver that grows flag combinations relocates complexity")
turned out to be the binding design constraint rather than a formality: the
driver shipped with **two** parameters.

5.3 landed as *a decision first* (Pass 8) and the sequencing logic held: the
driver really is where the state type is passed most, and rewriting the ten
loops' call sites in the same change would have multiplied the diff for no
extra signal. The one thing the plan did not anticipate is that the decision
could not be expressed as a plain annotation — pyright's invariance rule for
mutable protocol members forced the surface read-only, with an explicit
`set_state_field` write path. That is a TypeScript-style variance fact, not a
modelling one, and it is now written down where the next reader will hit it.

**Next in §5 is 5.4** (derive the registries). §5.6 and §5.7 stay open —
they are decisions, not work, and 5.7 in particular should be taken with
5.4's evidence about how much of the export surface is hand-kept.

---

## Execution Order

Phase A is **done**. Phase C is half done (1.2, 1.3 landed; 1.5's ratchet
landed, its 116 seeds open; 1.6 still wants a re-measurement).
Phase F is **three-quarters done**: 5.1, 5.2 and 5.3 landed; 5.4 remains
(5.6/5.7 are the two decisions the driver exposed).

| Phase | Items | Effort | Gate | State |
|-------|-------|--------|------|-------|
| **A — determinism** | 1.1, 2.1, 1.4 | ~3h | fast lane green 5× in a row | **done** — 2.1, 1.4, 1.1 (curve measured, floors re-derived) |
| **B — contract** | 2.2, 2.5, 4.1 lint check | ~3h | `F821` blocking; settle-horizon lock extended to all dynamics | **done** — 2.2 `f06f7629`, 2.5 `0faecede`, 4.1 `5ad96f85` |
| **C — velocity** | 1.2, 1.3, 1.5, 1.6 | ~4h | integration tier < 300s, re-baselined cost table | 1.2, 1.3 **done**; 1.5 ratchet **done**; 1.6 open |
| **D — structure** | 3.1, 2.3 (mechanical), 2.4 (top 3 modules) | ~1d | repo-wide lint trend down; pyright ratchet active | open |
| **E — presentation** | 4.2, 4.3, 4.4 | ~1d | `comp watch` streams a live run headfully | open |
| **F — architecture** | 5.1 → 5.2 → 5.3 → 5.4 | ~1w | 10 settle loops → 1 driver; Pareto in one layer; registries derived | 5.1, 5.2, 5.3 **done**; 5.4 open |

**Recommended next step** (cheapest, unblocked, high value): **§5.4** — derive
the registries, i.e. generate `_GEOMETRY_DISPATCH` /
`_GEOMETRY_FACTORIES` / `__all__` / `_LAZY` from the config factories so the
`AGENTS.md` eight-step checklist and the wiring locks both become assertions
rather than maintenance. §5.3 is landed; §5.4 is the last item in Phase F and
it needs no measurement, only a decision about which surface becomes
single-sourced first (recommendation: geometry, because it is the layer with
both a lock *and* the checklist).

**A hard constraint discovered in this pass, and it is a process rule, not a
plan item: individual commands over ~15s are not affordable on this box.**
Two demo probes (~85s each) were affordable exactly once, and the 200s demo
run was killed three times — twice by the harness and once by OOM (§2.8).
Everything measurable inside 15s is still cheap and safe: the fast lane
excepted, use targeted `-k` runs and treat the tiered suite as a
round-close, background-and-forget gate. **Design changes should therefore
prefer a *pre-measured* threshold from a probe log over a re-run to confirm
it** — §1.1's floors came from the 200-step probe curve, so the demo itself
never had to be re-executed to land them.

Phase C's remaining item is §1.6 (re-baseline the cost table), which is
arithmetic on `--durations=20` plus one slow pass, not a design question.

The standing rule from §0 held: 5.1 was done against a green suite, not to
rescue a flaky one, and the driver kept the per-class science rather than
absorbing it.

---

## Verification After Each Phase

```bash
# Fast lane (measured 91s, 3167 passed) — the inner loop and the per-commit gate.
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
- **A refactor that records what its predecessors silently dropped is a
  refactor with a second payload.** Moving ten loops into one driver was
  supposed to be pure structure. It also surfaced four settles that ran
  steps and never reported a horizon (§2.2 rule 2) and one that reported
  `on_step` a step index it never incremented. None of those were visible
  to a suite that only asserted *outputs*; all four were caught the moment
  the duplicated code had to be re-expressed as a shared contract. The
  duplication was hiding defects, not just code.

- **A source lock cannot see an omission.** `TestSettleHorizonSourceLock`
  proved §2.2's rule 2 across the whole module and stayed green through
  four paths that never wrote the field it guards. Structural locks must
  be paired with a behavioural one that *calls* the thing — which is what
  `test_every_dynamics_class_reports_its_horizon` now does, one line per
  registered dynamics class.

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
- **A probe-the-probe is cheaper than the fix it guards.** The RNG lock's
  module-seeding detector was wrong on its first version (bare `ast.Call`
  vs `ast.Expr`) and the parametrised classifier test caught it in 3s. The
  same shape as §0.6, at 1/100th the cost, because the scan is pure AST over
  a temp file — no fixture, no GPU, no settle loop.
- **A type checker will tell you when a decision is not yet a decision.**
  §5.3's contract could not be written as a plain annotation: pyright
  rejects a Protocol with *mutable* members for two classes that spell the
  same field differently, so the first cut came back with three errors and
  the shape of the answer (read-only surface + explicit `set_state_field`
  write path) in them. The alternative — silencing three errors and moving
  on — would have shipped a contract that reads as complete and is not.

- **A suppressed mismatch is a deferred defect, and its suppression is the
  evidence.** §5.3 found 17 credit signatures naming `SystemState` that
  every reference kernel violates, each silenced with
  `# type: ignore[arg-type]` at the call site. Nothing about that is a
  finding about the credit layer alone: it is the settle defect again, one
  layer down, and the *count* (120 directives repo-wide) is what makes
  §2.4's pyright ratchet worth running before any of it is fixed by hand.

- **A threshold fixed without a measurement is a guess wearing a
  measurement's clothes.** §1.1 shipped a 0.78 floor last pass, justified
  by reasoning from a docstring. The curve shows local3 at 0.594 two
  checkpoints before the end: the floor was inside the band the plan had
  already diagnosed. The reasoning was sound and the number was still
  wrong, because only a measurement knows where a band ends.
- **The web-UI removal also left a stale language-server index** pointing at
  `computronium/ui/**` files that no longer exist (`git ls-files
  computronium/ui` is empty); it still reports `nicegui` import errors from
  them. A clean LSP restart clears it. Nothing in the tree references them.
