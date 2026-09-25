# TODO34: Test Velocity, Correctness Hardening, and the Presentation Layer

**Status**: **ACTIVE** — items 0.1–0.9 completed (post-web-UI-removal repair pass); §1–§5 open.

Continues the series after `TODO33` (deprecated/legacy cleanup). Where `TODO33`
removed code, this one makes what remains *fast, provable, and ready to be
presented* — the three things the next development push (CLI equivalents, and
whatever UI comes after) will lean on.

§5 (architectural refactors) is the highest-leverage section and the longest
sounding; it is sequenced **last** on purpose. See its own risk notes before
starting it.

---

## Summary of Completed Work

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

### 1.1 Fix the `ntm_local` oscillation BEFORE optimizing it — P0

`test_demo_ntm_local.py:12` documents the metric as *"oscillates 0.79–0.87
(assert floor 0.80)"*. An assertion floor set **inside** an observed
oscillation band is a flake waiting for a busy machine: the same class of
defect as 0.4 and 0.8 above.

- Decide the claim: if the claim is "the NTM arm learns the copy task", assert
  on a monotone summary (final-N mean, or a plateau detector), not a raw
  last-iterate accuracy.
- If the raw iterate must be asserted, the floor belongs below the observed
  minimum (0.79) with a comment recording the measured band.
- **Verify by running it 5× on a loaded machine** before touching `STEPS`.
- Effort: ~30 min. Do this first — every other number in this section is only
  trustworthy once this is deterministic.

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

- Move `scripts/run_tiered_suite.sh` into the documented workflow
  (`AGENTS.md` §Testing) as **the** full-suite command, with the OOM rationale
  in a comment.
- Add `-n auto` guidance: `-n 4` is what was measured; `auto` is untested here.
- Add a per-tier `logs/tiers/<tier>.log` convention to `.gitignore` (already
  untracked — confirm) and a one-line "how to read a tier failure" note.
- Consider a `make test-fast` / `uv run pytest -m "not integration"` shortcut
  that completes in ~2.5 min for the inner loop, with the full tiered run as
  the pre-commit/round-close gate (this is the tiering `AGENTS.md` already
  describes, just made concrete).
- Effort: ~30 min.

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

### 2.1 Undefined names — 11 sites, 6 of them live crashes — P0

`pyright --outputjson` reports 11 `reportUndefinedVariable`; ruff `F821`
reports 4. These are latent `NameError`s on untested paths — the highest
severity-per-minute work in this document.

| File:line | Name | Status |
|-----------|------|--------|
| `acceleration/fa_kernels.py:538,577,609,643` | `HAS_TRITON` | **real NameError (reproduced).** Module defines `HAS_TRITON_FA`; the four `fa_*_triton` helpers branch on an undefined name. GPU FA path only — untested, so it has never run. |
| `execution/candidate_gen.py:756,757` | `TASK_GROUPS` | **real NameError (reproduced).** `TASK_GROUPS` lives in `execution/task_weights.py` and is exported there; `CandidateGenerator._matches_filter` does not import it, so any `task_filter` crashes. |
| `core/system_trainer/joint.py:236,294,373,377` | `SystemContext` | annotation-only (`from __future__ import annotations` present); `SystemContext` is defined in `state/context.py`. Fix the import for type correctness. |
| `core/profiling.py:474` | `SystemConfig` | annotation-only; verify whether the module resolves it under `TYPE_CHECKING`. |

Both real crashes reproduce today, in one line each:

```python
>>> from computronium.acceleration.fa_kernels import fa_batched_outer_triton
>>> fa_batched_outer_triton(torch.randn(4, 8), torch.randn(4, 3))
NameError: name 'HAS_TRITON' is not defined

>>> from computronium.execution.candidate_gen import CandidateGenerator, ExecutionStrategyConfig
>>> g = CandidateGenerator(ExecutionStrategyConfig(torch.device("cpu"))); g.task_filter = "vision"
>>> g._matches_filter("mnist")
NameError: name 'TASK_GROUPS' is not defined
```

- Fix all 11; add `F821` + `reportUndefinedVariable` to the **blocking** gate.
- Each of the two real ones gets a regression test that *calls* the function —
  the reason they survived is that no test reached them.
- Effort: ~2h including tests.

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

| Phase | Items | Effort | Gate |
|-------|-------|--------|------|
| **A — determinism** | 1.1, 2.1, 1.4 | ~3h | fast lane green 5× in a row |
| **B — contract** | 2.2, 2.5, 4.1 lint check | ~3h | `F821` blocking; settle-horizon lock extended to all dynamics |
| **C — velocity** | 1.2, 1.3, 1.5, 1.6 | ~4h | integration tier < 300s, re-baselined cost table |
| **D — structure** | 3.1, 2.3 (mechanical), 2.4 (top 3 modules) | ~1d | repo-wide lint trend down; pyright ratchet active |
| **E — presentation** | 4.2, 4.3, 4.4 | ~1d | `comp watch` streams a live run headfully |
| **F — architecture** | 5.1 → 5.2 → 5.3 → 5.4 | ~1w | 11 settle loops → 1 driver; Pareto in one layer; registries derived |

Phases A and B are strictly first: every number in C is untrustworthy until the
`ntm_local` assertion is sound (1.1), and the 11 undefined names (2.1) are live
crash risks on GPU and CLI paths that the next development push will exercise.

Phase F is deliberately last. It is the highest-leverage work in this document
(5.1 alone deletes ten copies of a control loop and one bug class), but it is
also the only phase whose mistakes are expensive to unwind — a badly
parameterized settle driver would relocate complexity rather than remove it.
Do it against a green, deterministic suite, not to rescue a flaky one.

---

## Verification After Each Phase

```bash
# Fast lane (~2.5 min) — inner loop
uv run python -m pytest tests/unit tests/property tests/primitives \
    tests/algorithms tests/acceleration -q -n 4

# Full suite, per tier, one process each (the monolith is OOM-killed)
./scripts/run_tiered_suite.sh

# Gates on changed files
uv run ruff format --check <changed>
uv run ruff check <changed>          # now includes F821
uv run pyright <changed>             # strict for new/rewritten modules
uv run python -c "import optuna, scipy, torchvision, pytest"
```

Re-pin `docs/figures/manifest.json` via the gallery lock whenever demo numerics
move, and say so in the commit body.

---

## Notes

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
