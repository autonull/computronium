# TODO108 — Named debt after the release closure

## Scope

TODO107 closed the local release: `scripts/run_local_gates.sh` is
`local gates: PASS` on the session-6 tree (`logs/local_gates_w45.log`, one
pass ≈ 62 min), the 0.277 block is a claim at its pre-registered n_max=205,
and the experiment-ready path runs (one-cell SEC record, `comp demo`,
campaign → coverage → repro → report). Nothing in this ticket blocks a
release.

This ticket is the work TODO107 queued, plus the defects its audits
surfaced. The priorities, in the order a session takes them:

1. **P0 — the 30 xfails.** They name two shapes: bugs/test mismatches (fix
   and remove the marker) and capability boundaries (name the primitive that
   closes the gap). An xfail is a named defect, so its marker is the defect's
   record until the test passes.
2. **P1 — locks that do not cover their declared population.** 35 skips are
   either an empty population or a config the lock cannot build; two
   contracts added in session 6 have no lock at all.
3. **P2 — static debt.** ruff 499 findings (named groups below) and pyright
   3240 errors / 15 warnings, with one pending scope decision.
4. **P3 — decisions and practice.** The site-build gate, the directive
   migration, and the pre-registration commit order.

Out of scope, recorded so it is not rediscovered: GitHub Actions stays
disabled (a separate ticket re-enables it), and Rocq stays out of the local
release (90299/90300 version skew, GitHub-only job).

## State at handoff (2026-11-27, session 6)

| Gate | Command | State |
|---|---|---|
| release | `scripts/run_local_gates.sh` | **PASS**, exit 0 (`logs/local_gates_w45.log`) |
| format | `ruff format --check .` | green |
| ruff | `ruff check .` | 499 findings (ratchet `BASELINE=499`) |
| types | `python scripts/check_pyright_ratchet.py` | 3240 errors / 15 warnings, ratchet held |
| property | `pytest tests/property tests/integration/test_gallery_lock.py::test_figure_lock -q --ignore=tests/property/test_experiment_invariants.py` | 2963 passed, 37 skipped, 30 xfailed, 0 xpassed (349.14 s) |
| invariants | `pytest tests/property/test_experiment_invariants.py --experiment-db <store>` | 7 passed (13.28 s; store built in 2.5 s) |
| primitives | `pytest tests/primitives` | 780 passed, 135 skipped (863.39 s) |
| acceleration | `pytest tests/acceleration` | 440 passed, 75 skipped (26.00 s) |
| unit | `pytest tests/unit` | 955 passed, 1 xfailed (245.16 s) |
| demo | `pytest tests/integration -m demo` | 25 passed (777.29 s) |
| acceptance | serial from-scratch, campaign locks, shard | 3 / 18 / 30 passed (518/53/672 s) |
| SEC path | one-cell survey, `comp demo`, campaign/coverage/repro/report | 1 record; 7 beats; 40 records, 9 PASS cells, 40/0 mismatches |

The 37 skips at handoff are exactly: 31 composer task-arg configs (W47),
4 legality tests on an empty engine (W46), 2 declared-infeasible
`complex_substrate_real_compute` cells (no work).

## Decisions

**D1 — A bug xfail is a defect; fixing it removes the marker.** The marker
is the record, not the settlement: the pass that fixes the cause deletes the
marker in the same change, so a regression fails and an xpass cannot appear
silently (W45 removed four that had).

**D2 — A lock that skips its population is not a gate.** Build the
population the way a run does (W46, W47) or delete the test. A skip stays
legal only for an environment refusal (no CUDA) or a declared-infeasible
cell.

**D3 — Static debt is scoped by a decision, not by drift.** `docs/archive`
carries 680 of the 3240 pyright errors; excluding archived code moves the
count once, in a commit that says so. A pass that only moves files is not a
closure.

**D4 — No claim without a pre-registered box.** The registration is
committed before the first seed runs, so the commit order proves the box
(TODO107 session 5's note; W59).

**D5 — The release is the local script; a change runs its affected set.**
A library change runs its shard + locks; a test/tooling change runs the
property shard and the step it touches. One artifact per tree.

## Work batches

| # | Block | Decides | Budget |
|---|---|---|---|
| 1 | W46 + W47: build the two skipped populations (legality engine from the registry; composer configs from the canonical task shape) | the two locks check what they claim | <30 min |
| 2 | W48 + W49: lock the `input_dim` width/shape contract and the `compute_loss` branch both ways | session 6's two untested contracts are tested | <15 min |
| 3 | W50 + W51: the 15 test/impl and library bugs (adapter copy-on-write, stdp window, consolidate/Fisher, newton_schulz) | 15 xfails become passes | <2 h |
| 4 | W52 + W53: the 2 missing APIs and GATE-0 drift (4) | each is fixed or filed with the primitive that closes it | measured × rung |
| 5 | W54 + W55: the 7 capability boundaries and the 2 test-assumption xfails | each is fixed or filed with its cost | measured × rung |
| 6 | W56 + W57: two ruff groups per pass (complexity 119; E402 56 + F841 21 + PLW1514 21 + S110 20) and Register C (RUF105 43) | the lint ratchet keeps falling | <1 h per pass |
| 7 | W58 + W59: the site-build gate decision; the registration-before-launch practice | the tooling record is honest | <30 min |
| 8 | release: `scripts/run_local_gates.sh` on the final tree | one green artifact | one pass (~62 min) |

## Defect queue

| # | Rung | Symptom | Cause | Fix | Verify |
|---|---|---|---|---|---|
| W46 | 1 | 4 legality boundary tests skip `no DECLARED constraints registered yet` | `_TEST_ENGINE` is a fresh `LegalityEngine`; DECLARED constraints are created at S4 expansion from the axis registry's constraint specs, so the test's `all_constraints()` is empty | build the engine's declared constraints the way `execution/stages_impl.py` does (params-free specs) | 4 passed, or the first named violation |
| W47 | 1 | 31 composer rows skip `config requires task args` | the lock calls `GeometryConfig.<name>()` with no arguments; the claim "every registered primitive composes" covers only the rows that take none | compose each with the canonical task shape the composer derives (28×28 / 784 digits), or name the row as a capability gap | the 31 rows run; failures triaged |
| W48 | 1 | the widened `input_dim` contract has no lock | session 6 allowed `int \| tuple[int, ...]`, moved `flat_input_dim` to `domains/base`, and nothing tests the width/shape/reduction rule | lock `flat_input_dim` (width, shape, `None`, invalid) and that `resolve_task`'s width equals `math.prod` on every task family | new lock, both directions |
| W49 | 1 | the `_CustomLoss` branch has no lock | `_compute_task_loss` now enters a `runtime_checkable` protocol instead of `hasattr`; nothing asserts which branch a task takes | lock both directions with two stub tasks (one defines `compute_loss`, one does not) | new lock |
| W50 | 1 | 8 xfails are test/implementation mismatches | the Muon test expects `_newton_schulz` where `ontology/update` implements QR `_orthogonalize` (4); the lifecycle test calls `consolidate` with the old signature and a pre-computed Fisher (4) | align the test to the implemented contract (or rename the implementation's method to what it does) | 8 xfails flip; markers removed |
| W51 | 1 | 7 xfails are library bugs | `EnergyToInstantaneousAdapter` mutates a frozen config (4); `compute_stdp_window` ignores spike times, so the window is the same for every Δt (3) | copy-on-write in the adapter; read Δt (pre/post order) in the window | 7 xfails flip |
| W52 | 1 | `PlasticityConfig.initial_psi` is missing (1) and adaptive FA is not implemented (1) | `bound_backends`/`kernel_profile` guard the API with `hasattr`; `RandomProjectionsCredit` fixates B at init | implement `initial_psi` on the config, or delete the guarded branch; implement `B <- B + eta·δ·aᵀ` | 2 xfails flip; no `hasattr` on a required API |
| W53 | 2 | 4 GATE-0 xfails: EP-BPTT cosine < 0.5 in deep networks | the settle's target/error channel is not carried to the input layer | LOOP/RULE parity work on the deep path | cosine > 0.5 at the declared depth, or a recorded scope refusal |
| W54 | 2 | 7 xfails are capability boundaries | deep settle at 100 steps; vision transpose feedback (needs FA or a learned inverse); no JVP scale; primitive capability 0.122; no ladder point clears the near-chance band; ternary substrate severs the forward graph; tile mesh projects 614k params over the 150k ceiling | each names the primitive that closes it (FA arm, JVP-scale knob, input compression for the mesh, ternary gradient path) | fixed (a capability) or filed as a gap with its cost |
| W55 | 1 | 2 xfails are wrong test assumptions | Hopfield energy "can be negative" is legal; the scale-free test hits numerical precision | fix the assertion or its tolerance | 2 xfails flip |
| W56 | 3 | pyright: 3240 errors / 15 warnings, of which `docs/archive` is 680 | archived UI code imports PyQt6/pyqtgraph/bioplausible and is not shipped; the 15 warnings are 8 wildcard library imports, 4 unused expressions, 1 `docker` source, 1 single-use `TypeVar`, 1 archived `__new__` | decide the archive scope once, then fix the 15 warnings | count moves once by the decision; the 15 are gone |
| W57 | 3 | ruff 499 | E402 56, RUF105 43, complexity 119 (C901 36, PLR0912 16, PLR0915 20, PLR1702 17, PLR0914 30), PLW0717 36, F841 21, PLW1514 21, S110 20, PLW2901 14 | one pass per named group, `BASELINE` lowered and the rules named; Register C migrates the 43 `# ruff: ignore` directives and enables RUF105 | `BASELINE` < 499 per pass |
| W58 | 3 | the site build has no gate | `docs/index.html`/`index.md` are gitignored; `docs/build_site.py --check` exits 1 on a fresh clone because the artifact is absent | decide: generate on demand (no gate) and say so, or gate only when the artifact exists | decision recorded in the docs build note |
| W59 | 3 | the 0.277 registration was committed after the first seed | the mtimes prove the order; the commit does not | commit the registration before the launch on the next claim rung | the commit order proves the box |

## Efficiency rules

- Measured one-pass cost: property 349 s, primitives 863 s, demo 777 s,
  acceptance 672 s, from-scratch 518 s, unit 245 s → a full release is
  ~62 min. A session runs its affected set, not the full pass (D5).
- `ruff check .` ≈ 1.5 s; `pyright .` ≈ 79 s; run pyright once per change.
- The experiment invariants need a store: build the 40-record readiness
  campaign (2.5 s) and pass `--experiment-db`; the property shard ignores the
  file.
- Cache stays outside the tree (W36): `TORCHINDUCTOR_CACHE_DIR` under
  `~/.cache`.
- Never launch two pytest suites concurrently; a shard that contends with
  siblings is priced by host load, not by the code (W38/W40).

## Closure criteria

- [ ] `scripts/run_local_gates.sh` exits 0 once on the final tree, and the log
      is named in the closing commit.
- [ ] **0 xfails**: each flipped to a pass with its marker removed, or filed
      as a capability gap with the primitive, its cost, and the task family
      it unlocks (W50-W55).
- [ ] **2 skips** remain: the declared-infeasible complex-substrate cells.
      The 31 composer rows and the 4 legality rows run (W46, W47).
- [ ] The `input_dim` and `compute_loss` contracts are locked both ways
      (W48, W49).
- [ ] ruff < 499, with the retired rules named in the ratchet's docstring;
      Register C's 43 directives migrated and RUF105 enabled (W57).
- [ ] pyright < 3240 errors or a recorded archive-scope decision, and 0
      warnings (W56).
- [ ] The site-build and pre-registration decisions are written where the
      gate lives (W58, W59).

## Remaining work (in order)

1. **P0 — the 30 xfails** (W50-W55). Start with the 8 test/implementation
   mismatches (W50) and the 7 library bugs (W51): 15 markers removed, no new
   capability needed. Then the 2 missing APIs (W52), the 4 GATE-0 drift
   xfails (W53), the 2 wrong test assumptions (W55), and the 7 capability
   boundaries (W54) — each either fixed or filed with its primitive and cost.
2. **P1 — the two population locks** (W46, W47), then the two new contracts
   (W48, W49). This is the block that makes the property shard's numbers mean
   what they say.
3. **P2 — static debt** (W56, W57). One scope decision for `docs/archive`,
   then the 15 warnings; ruff one group per pass, Register C alongside.
4. **P3 — decisions** (W58, W59).

The 0.277 block is closed, and no further rung is mandated: a second credit
family is a **new claim**, not a confirmation of this one, and runs only with
its own pre-registered box.

## Notes

- Commit per group (locks / bugs / static / docs), never one mega-commit;
  the group's gate is the evidence in its message. Nothing is pushed.
- A number travels with its ruler: state the n, the box, and the metric's
  resolution beside it.
- W46-W59 continue W1-W45; a number is never reused.
- `docs/figures/manifest.json` and `docs/figures/run_records/*.json` are
  written only by the demo gate; the re-pin commit is the demo gate's run.
- A capability gap is a row, not a verdict: it names the primitive, its cost,
  and the task family it unlocks. A high-effort gap that a cheap arm can
  answer is a defect in the plan, not in the mechanism.
