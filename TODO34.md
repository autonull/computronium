# TODO34: Test Velocity, Correctness Hardening, and the Presentation Layer

**Status**: **ACTIVE — 16 passes landed.** Complete: §0, §1.1–§1.5, §2.1, §2.2,
§2.5, §2.7, §3.1, §4.1, §5.1, §5.2, §5.3, §5.8, §5.4's dispatch half, and all
**116** of §1.5's unseeded tests. Partly: §2.3 (tranche 2 opened: 671 → 349,
ratchet live), §2.6 (provenance repaired; the environment fingerprint needs a
re-emission pass), §3.2 (the reproducibility question answered per class;
`checkpoints/` needs one word from the user and `docs/archive/` a policy).
**The prioritised forward plan is in [Remaining Work](#remaining-work)
— read that, not the section numbering.** §4 is unstarted and is the seed for a
`TODO35.md`; the argument for and against splitting is recorded there, and the
recommendation is to keep one document until §4 has a named consumer.

Continues the series after `TODO33` (deprecated/legacy cleanup). Where `TODO33`
removed code, this one makes what remains *fast, provable, and ready to be
presented* — the three things the next development push (CLI equivalents, and
whatever UI comes after) will lean on.

§5 (architectural refactors) is the highest-leverage section and the longest
sounding; it is sequenced **last** on purpose. See its own risk notes before
starting it.

---

## Summary of Completed Work

### Pass 16 — §1.5 closed (the 116), §2.3 tranche 2 opened, and a mesh loop that never ran

**§1.5 is no longer a ratchet; it is a ban.** All **116** flagged tests across 42
files now call `torch.manual_seed(0)` as their first statement, and
`_BASELINE` is `{}`. The plan's estimate was right that it is mechanical
(~2h, delegable) — and the interesting part is the *guard*, not the seeds:

- **A zero baseline makes the §0.6 population assertion vacuous.** The old
  `test_baseline_is_non_trivial` asserted "≥30 files and ≥100 flagged tests",
  which is precisely what emptying the baseline destroys: the lock would now
  pass for the reason §0.6 warns about — because the scan resolved nothing,
  not because nothing is wrong. `test_scan_population_is_non_trivial`
  re-expresses it against the population the *classifier* runs over
  (2,773 test functions, 463 drawing from the global RNG), and the existing
  `test_scan_classifiers` probe-the-probe pins the classifier itself.
- **The seeding moved numerics, and the first two failures were the
  interesting ones.** `test_free_accuracy_is_not_supervision_leaked` and
  `test_every_dynamics_class_reports_its_horizon` had been passing on a
  *particular* draw; both now pass on seed 0, which is the point. Neither
  needed its threshold moved — the fix belonged in the test.
- Two files needed `import torch` to be module-level rather than function-local
  to satisfy the F821 lock, and `ruff`'s autofix then had a redefinition to
  clean up: **the lock that §2.1 spent a pass strengthening caught the change
  this pass made.** Repo-wide ruff count is unchanged at 353 across the whole
  seeding sweep.

**§2.3 tranche 2, the three worst try-clauses.** 353 → **349**.

| File | Before | After | Note |
|---|---|---|---|
| `p2p/evolution.py` | 2 | **0** | 216-line `try:` (123 statements) split into six `_`-prefixed steps; pyright 16 → **0** |
| `knowledge/causal.py` | 14 | **11** | `map_failure_manifold`'s 54-statement `try:` body extracted; its complexity `ruff: ignore` moved with it |
| `execution/robustness.py` | 7 | 7 | `run()`'s 39-statement `try:` split into `_build_model` + a `_run_vision_probes` table; the try-clause finding drops 39 → 10 and three complexity findings move onto the extract, so the *count* is flat |

**And extraction found a defect that reading would not have.**
`P2PEvolution._evaluate` called `run_single_trial_task(..., job_id=...)`, and
`job_id` **is not a parameter of that function** — it has not been since the
signature was written. So every evaluation in the mesh loop raised
`TypeError`, the broad `except Exception` logged it and slept, and the loop
re-ran. §2.1's pattern in its purest form: an unexercised path whose only
handler is the one that hides it, with zero tests on `p2p/`. Fixed by
deleting the argument; the `job_id` value it computed was never read by
anything.

**The honest note on `robustness.py`**: that extraction is worth having and
did not move the number. A ratchet counts, and a count cannot tell a
readability win from a no-op — which is why the plan's rule is that the
extraction is the deliverable and the count is the check. Two of three moved.

Fast lane **3323 passed, 119 skipped, 26 xfailed, 1 xpassed in 99s**. The
touched integration files (108 tests) pass; `test_continual_learning.py` is
`slow` and is verified by `--with-slow` at round close.

### Pass 15 — §3.2: a calibration table that library code read from a gitignored directory

`campaign._ruler_lr` decides the learning rate for every campaign that does not
carry its own, and it read `artifacts/ruler_table.json` through a hardcoded
`parents[2]`. Its own docstring called it "the **committed** ruler table". Two
silent failures: the path does not exist in an installed wheel, and the
`except` branch falls back to a flat `1e-2` — which is **10x** the calibrated
value for the 4 of 11 tasks that measure `1e-3`. A fresh clone trained them
wrong, with a log line as the only signal.

**The find that generalises.** The first fix — move the table beside
`campaign.py`, read it from `__file__` — was correct in the source tree and
would still have shipped a wheel with no table: `include-package-data = true`
resolves through `MANIFEST.in` or a VCS plugin and this project has neither.
Built a wheel to check, found **zero** `.json` files in it, added
`[tool.setuptools.package-data]`, rebuilt, confirmed. I asserted the packaging
worked; measuring it is what found out it didn't.

**And the lock was wrong first.** `test_ruler_table_lock.py` reconstructs the
path from `campaign.__file__` — so it passed while the code pointed back at
`artifacts/`, because the artifacts copy still existed on this machine.
`_ruler_table_path()` now exists so the lock reads the path the code opens.
Three mutations are checked; the first two were missed by the first version.

Also answered §3.2's actual question per class: `data/` (878M) is entirely
public datasets fetched by the loaders, so "re-derivable from a seed + task id"
is the wrong question for it; `checkpoints/` (24M) has **no** provenance and
**no** referrers, and is now the open item rather than a footnote.

Fast lane **3323 passed**. The `data/` half of the question is closed by
measurement rather than by a document nobody would read.

### Pass 14 — §2.6: provenance that was shaped like provenance and wasn't

`emit_run_record` ran `git rev-parse HEAD` with no `cwd`. Every demo that
`monkeypatch.chdir`s into a tmp_path before emitting therefore ran git outside
a work tree, the handler swallowed the failure, and the record was written with
`"unknown"` where its commit should be — **shaped like it had provenance and
carrying none**. `d24_evolution_search.json` had been that way since
`b5a1ff1b`; 28 of 29 records had a real commit, and the one that didn't is
what made it findable.

Two lessons worth more than the fix:

* **A handler with a fallback is not a value that is right.** `"unknown"` is a
  string, so the record validated, the figure rendered, and the lock passed.
  The failure mode was silent *by construction* — the fallback existed to avoid
  a crash and in doing so removed the only signal that anything went wrong.
* **A misleading key name is a latent API.** `config_sha256` hashes the
  **data**. The next drift lock written against §2.6's original suggestion
  would reach for it to answer "did the config change?" and get a digest that
  only moves when the numbers move — and a second emitter in the repo already
  uses the same name for a real config hash.

Locked in the fast lane (88 tests, 0.8s) over the *committed* records, because
`test_gallery_lock.py` only runs at round close and provenance that decays
between round closes needs a per-commit gate. Fast lane **3306 passed**.


### Pass 13 — §2.7: the item's own premises were wrong, and it was a live bug

§2.7 asked which convention `activations[i+1]` followed and warned that the
answer was not to be guessed. Answering it found that **the item itself was
misdescribed twice over**: the function was *not* unreachable (it backs the
public `FAKernelBackend`, one call site, zero tests), and **ReLU and SiLU are
not "correct either way"** — only ReLU is. SiLU and GELU were silently
computing the wrong gradient.

The uncomfortable part is the repair. Fixing the call site — passing the
pre-activation, as the weight-gradient algebra requires — *broke Tanh*, whose
`1 - x**2` was quietly the post-activation form. The reasoning had been sound
at every step and the answer was still wrong at one of them; the numerical
test against autograd is what caught it. Fast lane **3218 passed** (10 new).

Written up in §2.7.

### Pass 12 — §2.3 tranche 1: the ignore lists were lying, and a ratchet

`ruff check .` reported **671** findings. **353** remain. The tranche is written up in §2.3
under "Tranche 1"; the two things worth carrying out of it:

**The config was the defect, and it hid 34 findings.** Two per-file-ignore
entries for the settle graph-safety idiom were keyed `too-many-statements`
while their own comment described `non-augmented-assignment`. The suppression
was doing nothing, in the two files where the idiom is most load-bearing, and
a third global entry (`comparison-of-constant`) suppressed nothing at all
because the rule has no findings in this tree. Counting findings is not
auditing a config: a *mis-keyed* suppression is invisible from the count,
because a count only moves when someone looks.

**A count can gate, if the check is cheap enough.** `ruff check .` runs in
0.2s, which makes `tests/property/test_lint_count_ratchet.py` affordable in the
92s fast lane — a repo-wide lint ratchet for the price of two property tests.
It carries a staleness guard (baseline must be within 10 of the measurement),
because a ratchet whose baseline has drifted out of reach is a ratchet that
has been switched off without anyone deciding to.

Net: **671 → 353**, fast lane **3208 passed, 119 skipped, 26 xfailed, 1 xpassed
in 92s**, no pyright regression on the touched modules (49 and 59 pre-existing
findings, unchanged either side).

### Pass 11 — §3.1 the shadowed module, and a name that survived the split

`computronium/deployment.py` and `computronium/deployment/` both existed. The
package wins import resolution unconditionally — verified, not assumed, via
`importlib.util.find_spec` — so the 1,633-line module was **unreachable from
every import statement in the tree** while reading as a live part of the
package.

The decision the plan deferred ("fold the module into the package or rename it")
did not need making: an AST sweep of the module's 29 top-level definitions
against the package namespace resolved **27 of 29**, and the two exceptions are
both non-defects. `_AppState` is private and independently reimplemented at
`deployment/serialization.py:930`. `InferenceRequest` exists at
`deployment/serialization.py:36` with **zero callers repo-wide** — dead in both
copies, deleted. The module had been superseded by the split and then left
behind; nothing imported it, nothing tested it, nothing noticed.

Lock: `tests/property/test_module_shadowing_lock.py`, mutation-checked by
dropping an empty `analysis/analysis.py` beside `analysis/` and watching it
fail. It scans `computronium/` **and** every `packages/*/src/` tree (the
workspace is a uv workspace, so the hazard is not confined to the main
package), and carries the scan-population assertion §0.6 and §5.4 both earned.

Fast lane: **3206 passed, 119 skipped, 26 xfailed, 1 xpassed in 99s**.

### Pass 10 — §5.8 the credit layer, and a NameError class ruff cannot see

`ontology/credit.py` named `SystemState` on **17** signatures while every
`primitives/credit_assignment/*/{kernel,reference}.py` builds `CompositeState`
per phase and silenced the mismatch with `# type: ignore[arg-type]`. All 37
annotations now name `SettableState`; the two SystemState-only fields the
credit reads (`energy` in `surrogate_objective`, `dual_vars` in the PC-ALM
path) go through the new `state_energy` / `state_dual_vars` readers in
`_state.py`, which return `None` on the z_t view instead of raising.

**All four credit suppressions are deleted**, and two kernels needed a real
fix rather than a deletion: `target_inversion/{kernel,reference}.py` and
`reverse_mode/kernel.py` keyed their phase dicts with bare strings
(`{"free": ..., "nudged": ...}`), which works at runtime only because
`Phase` is a `StrEnum`. They now key with `Phase.FREE` / `Phase.NUDGED`.
`pyright computronium/primitives/credit_assignment/`: **0 errors**, with no
suppressions. A dead `free_state` local in the PC-ALM credit (flagged by
`F841` in every repo-wide run) is gone.

**The defect worth remembering.** The optional-field readers were first
written as `TYPE_CHECKING` imports in `credit.py`, because the annotations
were. Every PC-ALM run then raised `NameError: name 'state_dual_vars' is not
defined` — 18 fast-lane failures. **`ruff`'s F821 cannot see this**: the
binding exists as far as the linter is concerned, it is simply absent at
runtime. The same trap fired one line earlier in `_state.py` itself
(`Tensor` imported for typing, used in an `isinstance`), where the only thing
that caught it was a behavioural test.

New lock, `test_type_checking_imports_are_not_called_at_runtime` (scans all
of `computronium/**` in ~3s): a name bound under `if TYPE_CHECKING:` and then
*called* — or used as an `isinstance`/`issubclass` argument — is a finding.
Two false-positive classes had to be excluded for it to be usable, and both
exclusions are in the helper's docstring: attribute bases (`pd.DataFrame` in
a string annotation is fine) and names re-imported at runtime inside a
function. It is the general form of the 11-site `F821` silences in §2.1,
which were the same mistake at module scope.

Fast lane: **3204 passed, 119 skipped, 26 xfailed, 1 xpassed in 91s**.

### Pass 9 — §5.4 the registries are derived, and the first defect it found

§5.4's claim was that hand-kept dispatch tables cost more than they look,
because a wiring lock *and* an eight-step checklist exist only to police
them. Three layers had the shape, and the estimate was wrong in the
interesting direction: the tables were not just redundant, one of them was
**wrong**.

| Layer | Before | After |
|-------|--------|-------|
| Geometry | two tables (`_GEOMETRY_DISPATCH` + a factories-first overlay consulted in that order), 12 aliases | `@geometry_backend(*aliases, ctor=…)` on the class; one derived `GeometryBackend(cls, build)` registry |
| Dynamics | `DYNAMICS_REGISTRY` dict in `__init__.py` | `@dynamics_backend(*keys)` on the class; `DYNAMICS_REGISTRY` built as classes are declared (`_registry.py`) |
| Update | `_UPDATE_CLASSES` dict, 14 keys / 11 classes | `@update_backend(*keys)`; derived registry — **and one key added** |

**The defect.** `NaturalGradientUpdate` shipped with a
`ParameterUpdateConfig.natural_gradient()` factory, a registered primitive
spec, an identity card and **no dispatch entry**: `update_from_config` raised
`Unknown update_type: 'natural_gradient'` for a documented update type. It
was invisible because the primitives' kernels call the class directly, and
because `test_update_primitives_have_ontology_classes` had grown a special
case that said so in a comment — *"natural_gradient is not in _UPDATE_CLASSES
dispatch (gap in dispatch)"* — and instantiated the class around it. A
hand-kept table's omission had been accommodated by the test meant to police
it. Deriving the registry makes that state unrepresentable; the special case
is deleted, and its deletion is the proof (per the plan's own rule: each
suppression either disappears or becomes a real error to fix).

**A second defect, in a test helper.** `_update_config_classmethods()` used
`inspect.getmembers`, which yields *bound* methods, so its
`isinstance(member, classmethod)` filter matched nothing and it returned `{}`
— making `test_update_config_classmethods_cover_primitives` assert over an
empty dict. A vacuous test that has been passing for as long as it has
existed, in the one file whose job is registry completeness. Fixed by reading
`vars()`; it now resolves **13** factories and is a real assertion. This is
§0.6 and §2.5 restated for helpers: *a scan that resolves zero of N is worse
than no scan*, and the population assertion that catches it (`assert
classmethods`) belongs in the helper's own callers.

Three new locks, all in the existing files (no new lock file — the invariants
are the same ones, now provable against a derived source):
`test_every_geometry_class_is_registered`, `test_registry_entries_come_from_this_module`,
`test_every_dynamics_class_is_registered`, `test_every_update_class_is_registered`,
`test_every_update_config_factory_dispatches`.

**Deliberately not done — the export half of §5.4.** Root `__all__`, root
`_LAZY` and the root `TYPE_CHECKING` block are still hand-written, and the
wiring locks still police them. Deriving them is a different trade: the
`TYPE_CHECKING` block exists *for pyright signal*, so a generated version
would have to be generated-and-committed anyway, and the root lazy map's
per-name module attribution is information the subpackage `__all__`s do not
carry. The dispatch tables were worth deriving because the information
genuinely lives on the class; the export lists are a publication surface, not
a registry. Recorded as §5.4's open half with the reasoning, rather than
attempted as a single risky change to `computronium/__init__.py`.

`pyright` on all three touched modules: 0 errors. Fast lane: **3201 passed,
119 skipped, 26 xfailed, 1 xpassed in 84s**.

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
- **DONE (Pass 16)**: the 116 are seeded and `_BASELINE` is empty. The
  population guard was re-expressed for that (see Pass 16), because the old
  one asserted a property the fix destroys.
- Effort: ~1h spent, of which the ratchet was the cheap half.

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

### 2.3 Lint debt: 353 findings (was 684) — P2 (Register C scope, per `AGENTS.md`)

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

#### Tranche 1 — **DONE** (Pass 12): 671 → 353, and a ratchet

**The config was the defect.** Before touching a single finding, the ignore
lists were audited for truth, because §5.4's lesson is that a hand-kept table
does not fail — it accumulates accommodations, and a *comment* that no longer
matches its key is the cheapest possible form of that. Three were wrong:

| Finding | Evidence |
|---|---|
| `comparison-of-constant` (PLR0133) was globally ignored and **suppressed nothing** — zero findings repo-wide. Dead config. Deleted. |
| `computronium/ontology/dynamics/_dynamics.py` and `ontology/_settle_kernel.py` ignored **`too-many-statements`**, while their comment said *"out-of-place adds are the settle graph-safety idiom"* — i.e. `non-augmented-assignment`. The key was wrong, so **34 of that file's 43 findings were never actually suppressed**; they were simply not being looked at. |
| `N803` (216) was the largest unlisted class. Globally ignored with the reason the plan specified — math notation (`W`, `G`, `X`, `I_syn`) *and* Triton's DSL-mandated kernel params (`BLOCK_*`, `*_ptr`), which renaming would make wrong. |

Then the classes that were **real** rather than sanctioned:

| Class | Before | Action |
|---|---|---|
| `N803` | 216 | ignored, with reason (sanctioned) |
| `PLW0717` try-clause statements | 92 | untouched — needs extraction, not suppression (as the plan said) |
| `PLR6201` literal-membership | 23 | **fixed** — `in ("a","b")` → `in {"a","b"}`; all string literals, so hashing is safe |
| `PLR6104` non-augmented-assignment | 43 | **all** suppressed with reason: the two ontology files' intended per-file ignore (now keyed correctly), the probe/audit-script block, and 1 per-site in `random_projections/kernel.py`. None **fixed** — see the correction below. |
| `RUF012` mutable-class-default | 6 | **fixed** — six read-only class tables in `execution/{strategy,synthesizer}.py` annotated `ClassVar`, which also tells pyright they are not instance state |
| `S101` assert in library code | 4 | **converted to raises** — a Triton shape precondition that vanishes under `python -O` is precisely the silent-corruption path Pass 2 documented |
| `F841` unused local | 3 | **deleted** — three `backprop_credit` constructions in `audit_credit_assignment.py` whose value was never read; `_create_credits()` collapsed to `_create_thermo_credit()` |

**A correction, made the same day.** The tranche initially "fixed" three
`PLR6104` sites in `scripts/audit_credit_assignment.py` by rewriting
`hidden_error = hidden_error * mask` as `hidden_error *= mask`. Measured
afterwards: `Tensor.__imul__` **is** in-place — the probe showed the operand's
storage mutated, not rebound. The results were identical only because
`hidden_error` was a freshly-created matmul result that nothing aliased, and
that script has **zero test coverage**. Three findings in an untested
diagnostic are worth less than the in-place/rebind distinction being
unambiguous, so the edits were reverted and the `scripts/audit_*.py`
throwaway exemption widened instead (the same category `scripts/probes/**`
already had, with the reason written down). This is Pass 2's correction applied
forward: a matmul looks in-place and isn't, a masked multiply looks like a
rebind and isn't, and a lint rule cannot tell the difference from the text.

**Repo-wide: 671 → 353 findings.**

**The ratchet is the part that outlasts the tranche.**
`tests/property/test_lint_count_ratchet.py` asserts the count against a
measured baseline (353, ruff 0.16.6 recorded alongside it) in **0.2s** — the
`ruff check .` subprocess is far cheaper than any test that would police it in
Python. Two tests, not one: the ratchet, plus a staleness guard that fails if
the baseline drifts more than 10 above the measurement, so the next
suppression cannot quietly push the ratchet out of reach (§0.6's lesson, a
third application). Mutation-checked by dropping a file with three real
violations into `computronium/` and watching the ratchet fail.

**And the honest bottom line on the deletions: none of them removed
functionality.** Every removal in this pass was either *unreachable code*
(`deployment.py`, provably — the import system never resolved to it, and the
one `pkgutil.walk_packages` discovery pass in the tree is scoped to
`computronium.primitives`/`computronium.algorithms`, so it never saw it
either), *dead code with a provably pure constructor* (the three
`BackpropCredit(...)` builds: `__init__` is one line assigning `config`), or
*config that suppressed nothing*. The one item that did change behaviour is
recorded as a correction above and was reverted.

**Two classes deliberately not touched.** `E402` (32) stays: the plan's own
instruction is to suppress per-site, and 32 hand-written site suppressions are
worse than 32 honest findings. `SIM102` collapsible-if (19) is a *decision*, not
a chore — 13 of the 19 are the `_validate_*` chains in `ontology/system.py`,
where collapsing `if a: if b: raise` into `if a and b:` keeps behaviour and
loses the one-branch-per-message structure the validators are read for.

#### Tranche 2 — **opened (Pass 16)**: 353 → 349, and a mesh loop that never ran

The three worst try-clauses, as the plan ordered. Full write-up in Pass 16;
the transferable result is that **extracting the body is what surfaced a live
crash** (`run_single_trial_task(job_id=…)`, a parameter that does not exist,
swallowed by a broad `except` in a loop with no tests). A lint finding is a
to-do list; the extraction it prompts is a probe.

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

### 2.7 The activation-derivative contract — P2 — **DONE** (Pass 13): a live bug, not a trap

**The item's own premises were both wrong**, which is why it sat at P2 for a
pass. Answering the question it posed ("is `activations[i+1]` the pre- or
post-activation value?") exposed both:

1. **It was not unreachable.** The note claimed "zero callers after §2.1".
   `fa_kernels.py:177` calls it, inside `FAKernelBackend`, reachable through
   the public `get_algorithm_kernels()` (`acceleration/__init__.py:112`). No
   in-tree code drives `forward`/`backward` on it, so no run was corrupted —
   but it is a public API returning wrong gradients, with zero tests.
2. **ReLU and SiLU are not "correct either way".** Only ReLU is. Tanh's
   `1 - h**2` is the *post*-activation form; SiLU's `σ(h)(1 + h(1-σ(h)))` is
   strictly a function of the **pre**-activation. Three of four branches were
   pre-activation formulas and one was post, and the surviving caller passed
   post — so **SiLU and GELU were silently wrong** and Tanh was right *by
   accident*, not by construction.

**Answered from the producer, as the item instructed.** `forward` returns
`activations = [x, act(L0(x)), …]`, so `activations[i]` is layer i's **input**
and `activations[i + 1]` its **post**-activation output. The weight gradient
`batched_outer_product(h_prev, grad_h)` pairs `grad_h` with `activations[i]`,
so `grad_h` must be d(loss)/d(**pre**-activation of layer i).

**The trap had a second half.** `backward_contrastive` read the same list with
the opposite naming (`free_pre = activations[i]`, `free_post = activations[i+1]`)
— the file asserted two incompatible contracts for one value and neither
matched `forward`. Renamed to `free_in` / `free_out`.

**Landed.** `forward` records each layer's pre-activation; `backward` raises
`RuntimeError` rather than synthesising one (synthesising is the defect);
Tanh became `1 - tanh(x)**2`; GELU's `1.4142` / `2.5066` magic constants became
`math.sqrt(2)` / `math.sqrt(2*pi)`.

**The part that would have been missed by reasoning.** Fixing the call site
alone would have swapped a two-branch bug for a one-branch bug: Tanh's
`1 - x**2` is correct *only* for a post-activation argument, so the moment the
caller was fixed, Tanh broke too. The test caught it. This is the strongest
argument in the plan for pinning against autograd rather than against a
reasoning chain — the reasoning was sound at every step and the answer was
still wrong at one of them.

`tests/acceleration/test_fa_activation_contract.py` — 10 tests, all four
activations, CPU-only, 3s. One test pins the `activations` layout, one asserts
**only ReLU's derivative is a function of its own output** (so the "why it went
unnoticed" explanation is checked, not folklore), one asserts `backward` refuses
to run without `forward`. Mutation-checked: reintroducing the old argument
fails 4 of the 10.

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

### 2.6 Keep the science honest when the numbers move — P2 — **partly DONE** (Pass 14)

0.3 changed every energy-based result in the repo, and the demo records had to
be re-pinned (`docs/figures/run_records/*.json` + `manifest.json`). That is
correct behaviour, but it is manual and easy to skip.

- When a fix changes numerics, the PR description should state which pinned
  artifacts moved and why. **Held to from here on**: the last two passes that
  touched numerics (§2.7, this one) each say in the commit body exactly which
  artifacts moved — and §2.7's says *none*, which is the claim worth making.
- ~~Consider recording the settle horizon in the run record so a future drift
  lock can distinguish "the algorithm changed" from "the environment
  changed".~~ **Re-scoped by measurement.** The records already carry
  `provenance`, and reading it found two things the item did not anticipate:

**The provenance that existed was not working.** `emit_run_record` shells out
to `git rev-parse HEAD` with **no `cwd`**, and any demo that
`monkeypatch.chdir`s into a tmp_path before emitting runs git outside a work
tree. The handler catches it and records the string `"unknown"`, so the record
is *shaped* like it has provenance and carries none.
`d24_evolution_search.json` had been that way since `b5a1ff1b` — and it was
only visible because 28 of 29 records had a real commit and one did not. `cwd`
is now pinned to the repo root; only `d24`'s provenance moved, its data
payload byte-identical, so no manifest re-pin was owed.

**`config_sha256` is a hash of the data, not of the config.** The name promises
exactly what this item asks for, so the drift lock it anticipates would reach
for it to answer "did the configuration change?" and get a digest that moves
only when the numbers move. Worse, `experiments/joint/z3_fixed_weights.py`
uses the same key name for a *genuine* config hash, so two conventions already
collide. Renaming it is not free (every record, and the emitter's docstring),
so it is **pinned as-is** with a test that states what the field is, which is
the cheap half and stops the next reader building on the name.

**Lock.** `tests/property/test_gallery_provenance_lock.py` — 88 tests, 0.8s, in
the **fast lane** and reading the *committed* records.
`tests/integration/test_gallery_lock.py` validates freshly-emitted records
after the demos run, which is a round-close concern; provenance that decays
between round closes needs a per-commit gate. Three invariants: every
`git_commit` is a real commit and an **ancestor of HEAD** (catches a record
emitted from another clone or branch), provenance is *exactly* the emitter's
two keys (a field the lock does not read is a field nobody checks), and
`config_sha256` still hashes the canonicalised data. Mutation-checked by
restoring `"unknown"` into `d24` and by the ancestor check.

**Still open — the environment fingerprint.** `torch` / `CUDA` / `python`
versions, so a drift lock can tell "the environment changed" from "the code
changed". The machinery already exists and is unused here:
`computronium.utils.capture_environment()` and `deps_hash()`. It is *not* done
because backfilling a version string into an existing record would be
**fabricating provenance** rather than recording it — it needs every record
re-emitted, i.e. every demo re-run. That is §1.6's slow pass, and the two
should be taken together.

---

## 3. Structure and Maintainability

### 3.1 `computronium/deployment.py` shadows `computronium/deployment/` — P1 — **DONE** (Pass 11)

Both existed (3,408 lines total). **Measured, not assumed**: the package wins
import resolution unconditionally (`importlib.util.find_spec` resolves to
`computronium/deployment/__init__.py`), so the module was unreachable from
every import statement in the tree. An AST sweep of its 29 top-level
definitions against the package namespace resolved **27 of 29** — the two
exceptions are `_AppState` (private, and reimplemented inside
`serialization.py:930`) and `InferenceRequest`, which exists in
`serialization.py:36` with zero callers in the whole repo. Both the module and
the dead `InferenceRequest` dataclass are deleted. No caller, in
`computronium/`, `tests/`, `scripts/`, `packages/` or the CLI, referenced
anything the module alone provided.

Lock: `tests/property/test_module_shadowing_lock.py` — no `X.py` may coexist
with `X/` in the same parent directory, with the scan-population assertion
(§0.6 / §5.4's lesson) so a scan that resolves nothing cannot pass.

### 3.2 Repository hygiene — P2 — **partly DONE** (Pass 15)

- Repo is **7.9G**: `.venv` 6.7G (ignored), `data/` 878M, `logs/` 60M,
  `artifacts/` 50M, `checkpoints/` 24M, `docs/` 8.0M. Git pack is 20.7M.
- Ignore status verified: `data/`, `logs/`, `artifacts/`, `checkpoints/` are all
  ignored; `docs/figures/` is **tracked** (correct — it is the pinned gallery,
  re-pinned deliberately in this pass).
- `docs/archive/` is 5.1M of superseded plans. The web-UI era already had one
  archival pass (`0c8e5a2a`); decide whether archive lives in-tree or in a
  cold store, and record the decision. **Still open.**

#### The reproducibility question, answered by measurement

The item asked to "confirm the `data/` and `artifacts/` contents are
re-derivable from a seed + task id, and document the command". Asked per
class, because the answer differs sharply:

| Class | Size | Re-derivable? | Command |
|---|---|---|---|
| `data/` | 878M | **Yes, by construction** — every entry is a public dataset (CIFAR-10/100, SVHN, MNIST/Fashion/KMNIST, USPS, Citeseer, Cora) loaded through `domains/vision.py` with `download=` on the loader. Nothing here is *generated*, so the item's "seed + task id" framing is the wrong question for 878M of the repo. | implicit: any loader that names the dataset fetches it |
| `artifacts/ruler_table.json` | 2.9K | **Yes, and it has to be — library code depends on it.** See below. | `scripts/probes/ruler_calibration.py` |
| `artifacts/broad_map*` | 50M | Yes — campaign outputs, each from a `comp broad-map` / `comp continuous` invocation. | the run's own command |
| `checkpoints/` | 24M | **No provenance at all** — `epoch_0_val_0.3416.pt`, no seed, no config, no manifest, and **no code or doc references them**. | nothing |

#### The finding: a gitignored calibration table that library code reads

`autoscientist/campaign.py::_ruler_lr` — which decides the learning rate for
every campaign that does not carry its own — read
`Path(__file__).parents[2] / "artifacts/ruler_table.json"`. Two independent
problems, both silent:

1. **The path does not exist in an installed wheel.** `parents[2]` is the repo
   root, so this only ever worked from a source checkout. Its own docstring
   called it "the **committed** ruler table".
2. **The `except` branch degrades the numbers.** A missing or unreadable table
   logs a warning and falls back to a flat `1e-2`. Measured over the table's
   11 tasks, **4 calibrate to `1e-3`** (xor, iris, wine, and one more) — so a
   fresh clone trained those at **10x** the calibrated learning rate, and a log
   line is not a gate.

The table now ships beside `campaign.py` and resolves from `__file__`. No task's
resolved lr changed on this machine; what changed is that a clone and a wheel
now get the calibrated values instead of the fallback.

**The packaging half was the second-order find, and it is the part worth
remembering.** `include-package-data = true` resolves through `MANIFEST.in` or
a VCS plugin, and this project has **neither**. The first fix therefore looked
correct in the source tree and would still have shipped a wheel with no table
at all — the same silent fallback, one level down. Measured rather than
assumed: built a wheel, found **zero** `.json` files in it, added
`[tool.setuptools.package-data]`, rebuilt, and confirmed the table is present.

`tests/property/test_ruler_table_lock.py` (17 tests) asserts the file is
tracked by git, that every task's resolved lr equals the shipped table, that the
path resolves inside the package, and that a `package-data` pattern covers it.
Three mutations checked — untracked file, hardcoded `artifacts/` path, emptied
declaration — each caught. **The first version of the lock passed the first
two**, because it reconstructed the path from `campaign.__file__` instead of
asking the code. `_ruler_table_path()` now exists so the lock reads the path
the code opens; that is §0.6's lesson, and the cheapest possible instance of it.

**Still open in this item**: `checkpoints/` (24M, zero provenance, zero
referrers — either give them a manifest or delete them), and the `docs/archive/`
decision above.

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

### 5.4 Derive the registries; stop hand-synchronizing exports — P2 — **dispatch half DONE**

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

**Landed (Pass 9)** for the three layers whose dispatch information lives on
the class: geometry, dynamics, update — each now registers itself with
`@geometry_backend` / `@dynamics_backend` / `@update_backend`, and the
hand-kept dicts are gone. Substrate needed nothing: it dispatches on a
`SubstrateType` StrEnum through an exhaustive `match`, so the enum is already
the single source.

**Still open — the export half.** Root `__all__`, root `_LAZY`, root
`TYPE_CHECKING` block and `ontology/__init__.py`'s lists. The wiring locks
still police them, and that is the right interim state: they are *publication*
surfaces (what a user can import) rather than registries (what the code can
dispatch to), the `TYPE_CHECKING` block is deliberately literal so pyright
sees real imports, and the root lazy map's per-name module attribution is
not derivable from the subpackage `__all__`s. Generating them would mean
generating-and-committing a file whose purpose is human/tool signal — a
trade to be decided with a reader who wants the public API to be smaller,
not by a refactor pass. **Do not start it before §5.8** (the credit layer's
retyping) lands: both touch `ontology/**` annotations, and one diff is
cheaper to review than two.

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

### 5.8 New: the credit layer has §5.3's defect, suppressed — P2 — **DONE** (Pass 10)

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

**Landed (Pass 10).** All 37 annotations retyped, all four suppressions
deleted, two kernels' string-keyed phase dicts fixed to `Phase.*`, and the
resulting `TYPE_CHECKING`-import hazard locked. The sequencing note stands:
this had to land before §5.4's export half, and did.

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
| 4th | 5.4 | Mechanical, benefits from 5.1–5.3 having reduced the surface count | **dispatch half done** (Pass 9); export half open |
| 5th | 5.6, 5.7 | Both are decisions the driver exposed, not new work | open |
| — | 5.8 | Found by 5.3's own retype; annotation-first like 5.3 | **done** (Pass 10) |
| — | 5.9 | Accessor cleanup exposed by 5.3 | open |

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

Phases A, B and the deterministic half of C are done; D is half done; E has not
started and should not until it has a consumer. The current phase table:

| Phase | Items | State |
|-------|-------|-------|
| **A — determinism** | 1.1, 2.1, 1.4 | **done** — 2.1 `59d13f47`, 1.4 `fb6bb0f7`, 1.1 (curve measured, floors re-derived) |
| **B — contract** | 2.2, 2.5, 4.1 | **done** — 2.2 `f06f7629`, 2.5 `0faecede`, 4.1 + 5.2 `5ad96f85` |
| **C — velocity** | 1.2, 1.3, 1.5, 1.6 | 1.2, 1.3, 1.5 **done** (1.5 fully: baseline empty, guard re-expressed); **1.6 open** |
| **D — structure** | 3.1, 3.2, 2.3, 2.4 | 3.1 **done** `b6151076`; 3.2 **partly done** `ceb4865a`; 2.3 tranche 1 **done** `09f73936` (671→353), tranche 2 opened in Pass 16 (→349); **2.4 open** |
| **E — presentation** | 4.2, 4.3, 4.4 | open; the TODO35 seed, see Remaining Work |
| **F — architecture** | 5.1 → 5.2 → 5.3 → 5.4 | 5.1, 5.2, 5.3 **done**; 5.4 dispatch half **done**, export half deferred; 5.6–5.9 are decisions |

**A hard constraint on this box, and it is a process rule rather than a plan
item: individual commands over ~15s are not affordable.** Two demo probes
(~85s each) were affordable exactly once, and a 200s demo run was killed three
times — twice by the harness, once by OOM (§2.8). Everything inside 15s is
cheap and safe; the fast lane excepted, use targeted `-k` runs and treat the
tiered suite as a round-close, background-and-forget gate. **Design changes
should prefer a *pre-measured* threshold from a probe log over a re-run to
confirm it** — §1.1's floors came from the 200-step probe curve, so the demo
never had to be re-executed to land them. The one exception this round was
`uv build --wheel` (~30s), which bought a packaging defect no amount of
reading would have found.

The standing rule from §0 held throughout: every item was done against a green
suite, not to rescue a flaky one, and each pass that moved numerics said so in
its commit body.

---

## Remaining Work

Everything still open, ordered by *what it costs to be wrong*, not by section
number. Effort is a first estimate, not a commitment; "first move" is the
concrete next action, so no item here needs re-planning before starting.

### Tier 1 — cheap, and each closes a hole that is already open

| # | Item | State | First move | Effort | Done when |
|---|---|---|---|---|---|
| 1 | **§2.4 pyright, top 3 modules by fan-in** | 2079 findings repo-wide; `AGENTS.md` keeps checking basic until a ratchet exists | count findings per module, pick the top 3, drive one to zero, add a *changed-files* pyright check to `pre-commit` next to ruff's. **Pass 16 shows the per-file method**: `p2p/evolution.py` went 16 → 0 inside an unrelated extraction, so the fan-in ranking is worth re-measuring rather than assuming | ~4h + ongoing | 3 modules report 0; pre-commit fails on a new error in a changed file |
| 2 | **§3.2 `checkpoints/`** (24M) | no manifest, no seed, no config, **zero referrers**. Pass 16 dated them: 7–21 Aug, `epoch_N_val_*.pt` plus one `final_model.pt` + `metrics.json` from an LM demo | **delete** — it is a cwd-relative default dump (live code writes `<output_dir>/checkpoints/`), gitignored, and §2.6's own rule says a hand-written manifest for an unknown run is *fabricated* provenance, not recorded provenance. **Awaiting the user's word: it is 24M of undeletable-if-wrong data** | ~5min once decided | directory gone |
| 3 | **§2.6 environment fingerprint** | `capture_environment()` / `deps_hash()` exist and are unused here | add `deps_hash()` to the record emitter, then re-emit every record in one slow pass (fold into §1.6) | ~1h + the slow pass | a drift lock can name which of code / config / environment moved |
| 4 | **§2.3 tranche 2** (`PLW0717` 90, `E402` 32) | 3 of the worst done (Pass 16); the ratchet is live so the list is trustworthy | `knowledge/causal.py` still holds 4 (16/39/9/29 statements) and `hyperopt/experiment.py` 3 — the same extraction recipe, and `p2p` is the precedent for it finding a live bug | ~3h | count falls under the ratchet without a new suppression |

### Tier 2 — needs a quiet window, and one pass to amortise

| # | Item | State | First move | Effort | Done when |
|---|---|---|---|---|---|
| 6 | **§1.6 re-baseline the cost table** | the numbers in §1 are pre-§0.2; the suite got heavier when settles started running their full horizon | one `--with-slow` pass, `--durations=20`, rewrite the §1 table | ~30min of machine | the table matches a recorded run |
| 7 | **§5.4's export half** | deliberately deferred: `__all__` / `_LAZY` / `TYPE_CHECKING` are a *publication* surface, not a registry | **do not start** without a reader who wants the public API smaller | ~1d | — |
| 8 | **`docs/archive/` cold-store decision** (5.1M) | one archival pass already happened (`0c8e5a2a`); no policy recorded | write the policy in three lines and apply it | ~30min | the rule exists |

### Tier 3 — decisions, not work. Take them with the code that can answer them.

| # | Item | The question only that code can answer cheaply |
|---|---|---|
| 9 | **§5.6** `local_learning/settling.py`'s two hand-written loops | should `StateDynamicsConfig.max_steps` / `convergence_*` apply to model settling at all? If yes the driver is free; if no, write down that they are separate contracts |
| 10 | **§5.7** the LIF horizon counts layers, not steps | per-layer sum (today), per-layer max, or separate `steps_used` / `layers` — then make the lock assert the choice |
| 11 | **§5.9** three redundant `getattr` state accessors | audit the lazy and compiled whole-graph paths first; they pass duck-typed records from outside the protocol |
| 12 | **§2.3 `SIM102`** (19 collapsible-ifs) | 13 are the `_validate_*` chains in `ontology/system.py`, where collapsing costs the one-branch-per-message structure. Probably **leave alone** — recorded so it is a decision, not an omission |

### Tier 4 — the phase that has not started, and should not without a consumer

**§4 (presentation layer): 4.2 live telemetry, 4.3 the read surface, 4.4 the
renderer registry.** Deliberately last. 4.2 has a real substrate now (§0.4
fixed `on_step`; §2.7's test proved an untested public path can be simply
*wrong*), and §4.1's layering rule has a lock behind it. But every item needs a
consumer, and the plan's own §4.5 forbids starting UI work before the layering
check exists — it now does.

**This is the seed for `TODO35.md`, and the split is recorded here so the
decision is made once rather than drifted into.** The argument for splitting:
§4 is feature work with a different success condition (a run you can watch),
while everything above is hygiene with a different one (a claim you can prove).
The argument against, and the reason it has not been done: two documents with
overlapping open-item lists is the exact drift this plan has documented four
times — a hand-kept table that accumulates accommodations. **Recommendation:
keep one document until §4 has a named consumer.** If that consumer arrives
with a requirement, split then, and move §4 plus §4.5's non-goals across whole
rather than re-deriving them.

### New items surfaced by passes 12–16, not yet in the numbered sections

| Item | Finding | Where it belongs |
|---|---|---|
| **`p2p/` has no tests** | the loop's only handler is `except Exception` + `sleep`, and a `TypeError` from a non-existent kwarg ran for the life of the module with nothing but a log line. The mesh feature is untested *and* its failure mode is silent by construction | a Tier-1 item: a stub-DHT test that drives `_evolution_loop` one iteration. `_build_model`/`_fetch_global_best`/`_evaluate` are now separately callable, which is what such a test needs |
| cwd-relative defaults in scripts | `scripts/visualize_atlas.py:23` and `scripts/g1_core_sweep.py:36` default to `Path("artifacts/ruler_table.json")` — cwd-relative, the same shape as the `d24` provenance defect, and both now read a file that has moved. `checkpoints/` at the repo root is the same shape: a cwd-relative default dump | a lock, or a one-line default change, when either script is next touched. A single scan for `Path("<name>")` defaults in `scripts/` would cover the class |
| `except OSError, subprocess.SubprocessError:` in `computronium/utils.py` | valid only on **Python 3.14+** (PEP 758, unparenthesised multiple exception types). The repo targets 3.14 and both ruff and pyright accept it — but the module will not *parse* on 3.13 | a note, not a defect: the target-version is declared and correct |
| the lint ratchet's own version pin | first version **skipped** on a ruff mismatch, i.e. it switched itself off invisibly — the exact failure mode this plan warns about, committed by this plan. Now it fails with the remedy in the message | fixed, and the episode is the argument for the "make the claim executable" note below |

### What was deliberately not done, and why

- **Not optimisation.** The fast lane is ~95s; the two 200s+ demos are already
  `slow`; and the suite got *heavier* because §0.2 made settles run their full
  budget. Optimising walltime now would optimise the artifact a correctness
  fix improved.
- **Not more structure.** §5's remaining items are decisions (Tier 3). Three of
  the last four passes were config and dead code, not architecture.
- **Not `RUF105/106/103`.** Enabling them one at a time churns guard-rails;
  the canonical directive migration is Register C work, as one change.
- **Not `E402` per-site suppression.** 32 hand-written suppressions are worse
  than 32 honest findings.

### The through-line of the last four passes

Three of them turned on a claim that was **asserted rather than measured**, and
in every case the measurement was cheap next to the claim: a wheel build (~30s)
proved the packaging dropped the ruler table; `find_spec` (0.1s) proved
`deployment.py` was unreachable; a per-rule count (0.2s) proved an ignore
suppressed nothing. Two of the three fixes would have shipped looking correct
in the source tree.

The general form, and the reason the ratchet and the wheel assertion are the
same kind of object: **when something claims to work, make the claim
executable.** The ratchet is that instinct applied to a count; the wheel
assertion is it applied to packaging; `test_ruler_table_lock.py` is it applied
to a path. Each is cheap, and each one of them found a real defect on its first
run.


---

## Verification After Each Phase

```bash
# Fast lane (measured 95s, 3323 passed) — the inner loop and the per-commit gate.
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

# The lint ratchet is a gate too: it fails if the repo-wide ruff count rises.
uv run python -m pytest tests/property/test_lint_count_ratchet.py -q

Re-pin `docs/figures/manifest.json` via the gallery lock whenever demo numerics
move, and say so in the commit body. The last three passes that touched pinned
artifacts each stated the movement explicitly, including "none" — which is the
claim worth making.

Provenance has its own fast-lane lock over the *committed* records
(`test_gallery_provenance_lock.py`), separate from the round-close gallery lock,
because provenance that decays between round closes needs a per-commit gate.

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
- **A binding that exists only for the type checker is not a binding.**
  §5.8's first cut put the new readers in `TYPE_CHECKING` (they were used
  in annotations) and every PC-ALM run raised `NameError`. `ruff` F821 — the
  gate §2.1 spent a pass strengthening — is structurally incapable of
  seeing it. The general rule took one small AST test to encode, and it
  subsumes the 11 suppressed `F821`s of §2.1, which were the same mistake
  at module scope. Linters check names; only a test can check *when* a name
  exists.

- **A hand-kept table does not fail; it accumulates accommodations.** The
  clearest evidence in this plan is not the missing `natural_gradient` key
  but what grew around it: a comment in a test saying "gap in dispatch" and
  a branch that instantiated the class directly to route around it. A test
  that works around the defect it exists to catch is a *louder* signal than
  the defect, and nobody read it. When a lock needs a special case, the
  special case is the finding.

- **A helper can be the vacuous test.** `_update_config_classmethods()`
  returned `{}` because `inspect.getmembers` yields bound methods — and its
  caller asserted over that empty dict indefinitely. §0.6's lesson was
  recorded about a lock that resolved 0 of 10 classes; the same class of bug
  sat in a helper one level down, and the only thing that found it was
  *fixing an unrelated table and asking why the numbers moved*. Assertions
  on a scan's population belong in the test, not only in the scan.

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

- **A mis-keyed suppression is invisible to a count.** §2.3's tranche 1 found
  two per-file ignores keyed `too-many-statements` whose own comment said
  `non-augmented-assignment`: 34 findings in the two settle files were being
  *neither* reported *nor* suppressed, and no total ever moved. A count answers
  "how much is left"; only reading the key against the finding answers "is the
  thing that is making it quiet actually doing anything". §5.4's argument about
  hand-kept tables applies to config tables with the same force — and the tell
  is always the same, a comment that has drifted from its key.

- **This plan committed its own version of the failure it documents.** Pass 12's
  lint ratchet *skipped* on a ruff-version mismatch — a gate that switches
  itself off, invisibly, because the skip lands in a summary line shared with
  119 others. It is the same defect as §5.4's special-cased test, written by
  the same author that wrote down the rule. It now fails with the remedy in the
  message, on the reasoning that a ruff upgrade legitimately moves the count and
  should therefore be a **deliberate re-baseline** (both constants, one commit,
  the body saying which rules changed) rather than an exemption. Worth more than
  the fix: a rule you have just written is the one most likely to be written
  from the shape of the rule rather than from the failure it prevents.

- **An unreachable module is worse than a missing one.** §3.1's
  `deployment.py` was 1,633 lines of plausible-looking deployment code that
  no import statement in the tree could reach, because a package of the same
  name won resolution. It carried no test, so nothing in CI could object, and
  its `__all__` read as the package's public surface. The duplicated names it
  had drifted on (a dead `InferenceRequest` in both copies) are the tell: dead
  code that *compiles and greps* is indistinguishable from live code until
  something resolves what actually loads. The lock is a filesystem comparison,
  not a type check, because that is the only question being asked.

- **A lint finding is a to-do list; the extraction it prompts is a probe.**
  §2.3's tranche 2 opened by splitting a 123-statement `try:` because ruff said
  `PLW0717`, and the split revealed that the loop's only evaluation call passed
  a keyword that does not exist — swallowed, every iteration, by the broad
  `except` the finding was sitting inside. The rule was the vehicle, not the
  payload. Cheapest possible instance of "a refactor that records what its
  predecessors silently dropped", and it was found by *moving* code rather
  than by reading it, which is the cheapest form of the plan's own theme.

- **Closing a ratchet can delete the guard that made it trustworthy.** §1.5's
  population assertion ("≥30 files, ≥100 flagged tests") existed precisely to
  stop a lock that resolves nothing from passing. Emptying the baseline is the
  *correct* end state, and it is also the exact state the guard was defending
  against — so the guard had to be re-expressed against the population the
  classifier runs over rather than the population it rejects. A ratchet's
  termination condition is also a change to its meaning, and the two have to be
  written in the same commit.

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
