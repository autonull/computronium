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

1. **P0 — the xfails.** They name two shapes: bugs/test mismatches (fix
   and remove the marker) and capability boundaries (name the primitive that
   closes the gap). An xfail is a named defect, so its marker is the defect's
   record until the test passes. 16 retired in session 7; 11 remain (W53 4,
   W54 7).
2. **P1 — locks that do not cover their declared population.** DONE in
   session 7 (W46-W48); the 35 skips are retired and both contracts are
   locked.
3. **P2 — coverage and test time.** 63.65% of statements, four tiers, and a
   fast suite whose 178 s long pole is trimmed to 8.07 s (wall 82.43 s); the
   map and the brittleness rule are in the strategy section.
4. **P3 — static debt.** ruff 499 findings (named groups below) and pyright
   3240 errors / 15 warnings, with one pending scope decision.
5. **P4 — decisions and practice.** The site-build gate, the directive
   migration, and the pre-registration commit order.

The four tiers (affected / fast / release / coverage) are in the strategy
section below; a session takes the cheapest tier that can decide its question.

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

## Progress 2026-11-27 (session 7)

**P0 — 16 xfails retired; 11 remain (4 GATE-0, 7 capability).**

| # | Block | State | Evidence |
|---|---|---|---|
| W50 | test/implementation mismatches | **DONE** | 8 cases. The Muon test calls `_orthogonalize` and certifies the exact SVD polar factor (`ortho_steps=0`, `‖GᵀG−I‖_F < 1e-4`) plus the Newton–Schulz condition-number drop; the EWC test calls `consolidate(params, old_params)` and derives Fisher from the anchor drift. 14 passed in the U-axis group. |
| W51 | library bugs | **DONE** | 7 cases. The adapter no longer mutates the frozen config: distillation and the single-step fallback build a `dataclasses.replace` copy (4); `compute_stdp_window` reads the pair lag Δt = post − pre (3: sign, antisymmetry up to a₊/a₋, decay). |
| W52 | missing APIs | **DONE** | 2 cases. The joint test composes `NullPlasticity`, not a config; Adaptive FA is implemented as `B_i ← B_i + feedback_lr·δ_{i+1}ᵀ a_i`, gated by `config.adaptive_feedback` and exposed by `create_native_fa_adaptive`. |
| W55 | wrong test assumptions | **DONE** | 2 cases. The scale-free property is checked normwise + directionally (per-entry relative bounds are unstable at float32 noise); the Hopfield energy is unbounded below, so the nudged-phase row asserts finiteness and the overall trend. |
| W53 | 4 GATE-0 xfails | **OPEN** | biology EP (2) raise a 200-vs-205 tensor-size mismatch inside TileEP; scaling deep-settle and Control-Lyapunov monotonicity fail on the semantics their markers name. Primitive: LOOP/RULE parity on the deep path. Family: deep EqProp credit. |
| W54 | 7 capability boundaries | **OPEN** | grpc tile-mesh output width (target out of bounds); Triton eqprop shared memory 294912/557056 B over the 101376 B limit (2); CuPy zero-copy empty tensor; ternary kernel-vs-reference 9.9e-3; tile-mesh 614k params; `PredictiveSettlingDynamics` stub. Primitives: output-width projection, smaller Triton block, non-empty copy, one quantization boundary, input-compression projection, predictive-coding loop. |

**P1 — both populations and both contracts are locked.**

| # | Block | State | Evidence |
|---|---|---|---|
| W46 | legality population | **DONE** | `engine_from_registry` is the one builder; `ConstraintSpec.proof_kind` is the proof, so the parallel proof table is deleted. 8 passed, no skips. |
| W47 | composer population | **DONE** | the hand-maintained skip sets are gone; every row composes from the canonical `(1, 28, 28)` task shape, with graph/lattice args only where that family supplies them. 75 passed (31 formerly skipped). |
| W48 | `input_dim` contract | **DONE** | `test_input_dim_contract_lock.py`: width/shape/list reductions, refusals, and `resolve_task` width = `math.prod` on 6 families. 9 passed. |
| W49 | `compute_loss` branch | **DONE** | `test_loss_dispatch_lock.py`: the custom-protocol branch, CE, and MSE with stub tasks. 3 passed. |

**P2 — the long pole is trimmed; the wall fell 38%.**

- W63: `test_cosine_similarity_reasonable` 20 → 5 seeded batches (mean cosine 0.7093 ≥ 0.62, sign 0.7203 ≥ 0.65; 8.07 s standalone vs 25.32 s). Fast suite 133.19 s → **82.43 s** (2548 passed / 75 skipped / 6 xfailed). The `< 60 s` clause is not met; the remaining wall is the 2500-test schedule, not one test.
- W60/W62 unchanged from `c677afea` (90.7% of covered statements; ratchet 38,318).

**Session 7 end state.**

| Gate | Command | State |
|---|---|---|
| property | `pytest tests/property -q` | **3026 passed, 9 skipped, 11 xfailed** (282.87 s) |
| invariants | readiness store + `--experiment-db` | 7 passed (11.71 s) |
| composer/legality locks | the two lock files | 75 + 8 passed |
| fast | `scripts/run_fast_gates.sh` | **82.43 s**, 2548 passed / 75 skipped / 6 xfailed |
| xfails | AST scan of `tests/**/test_*.py` | **11** (4 GATE-0, 7 capability) |

The 9 property skips are 2 declared-infeasible complex-substrate cells and
7 experiment-invariant rows that run against the readiness store.

## Coverage and test-time strategy (session 7)

The release population measured once with `--cov-context=test`: **38,318 of
60,203 statements = 63.65%**. Line hits split into **31,446 executed by a
test** and **29,215 executed only at import** — importing a module already
"covers" half its body, so the per-test population is the honest signal and
the import-only lines are not.

**Four tiers, each answering one question.**

| tier | command | measured | coverage | question |
|---|---|---|---|---|
| affected | `uv run python scripts/select_affected_tests.py` then `pytest <files>` | 122 files for the domain change | the changed module's reach | did my change break its own contracts? |
| fast | `scripts/run_fast_gates.sh` | **82.43 s**, 2548 passed / 75 skipped / 6 xfailed | 34,756 statements = **90.7% of the release's covered statements** | is the machine still coherent? |
| release | `scripts/run_local_gates.sh` | ~62 min | 63.65% | may this tree be released? |
| coverage | `COVERAGE=1 scripts/run_local_gates.sh` | release + ~40% | ratchet | did coverage fall? |

**Where coverage lacks** (missing statements): `experiment/surface` 3,121
(44.4%), `core/local_learning` 880 (45.1%), `experiment/wave.py` 595 (37.7%),
`experiment/runners` 555 (**0%**), `models/deployments` 537 (49.1%),
`experiment/documentation` 499 (38.0%), `sec_loop.py` 470 (58.7%),
`legality` 360 (64.2%). The surface/report/CLI and `wave.py` are the mass;
`runners` is never imported by a test at all.

**Where we over-test** (lines vs seconds, per file): 113 of 342 files cover
no line another file does not. Worst: demo `depth_harvest` 439 s / 16 lines /
**0 unique**, `uaxis_depth_frontier` 432 s / 145 / 0, `jpc_faithful_depth`
269 s / 95 / 0; `test_primitive_capability` 525 s / 849 lines / 122 unique.
The demos are artifact producers, not checks — their value is the figures,
not the lines, so they stay out of the fast suite and stay in the release.

**The fast suite's wall is one test, not the worker count.** Measured:
`-n 4` 133.19 s, `-n 8` 161.03 s, `OMP_NUM_THREADS=1` 179.31 s. The long pole
is `test_credit.py::...::test_cosine_similarity_reasonable` at **178.3 s**
(under coverage), then `test_ntm_geometry` 78.3 s, `test_legality_compile_lock`
33.4 s, `test_transformer_geometry` 30.4 s. The unit shard's 245 s wall is the
same 178 s test. Tuning workers or threads cannot beat a single long test; the
fix is to trim that test's budget to the smallest its assertion needs (W63).

**Brittleness.** A test asserts a **contract** — an invariant, a
round-trip, a refusal by name, a monotone ordering — not a copied measurement
(a param count, an exact walltime, a population size). A number is legitimate
when the number *is* the policy (a declared budget, a family ceiling) or a
provenance record. A lock that enumerates a population keeps a named list and
fails loudly when the population moves; it is reviewed, never auto-derived
from today's tree. The three new pieces follow that rule: the fast list is
tolerant of a move, the affected selection over-approximates instead of
pinning node ids, and the coverage ratchet is a floor with a re-baseline note,
not an exact target.

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

**D6 — A test asserts a contract, not a measurement copy.** An invariant, a
round-trip, a refusal by name, a monotone ordering — never a param count, an
exact walltime, or today's population size. A number is legitimate when it
*is* the policy (a declared budget or ceiling) or a provenance record; a
population lock keeps a named list and is reviewed when the population moves.
The fast list tolerates a moved file, the affected selection over-approximates
instead of pinning node ids, and the coverage ratchet is a floor with a
re-baseline note, not an exact target.

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
| W60 | 2 | the release pays ~62 min for 63.65% coverage and nothing ranks a test by the lines it buys | suite order was never measured; 113 of 342 files cover no line another file does not | per-test attribution (`--cov-context=test` + durations) and a greedy `new lines / second` selection; `configs/fast_suite.txt` + `scripts/run_fast_gates.sh` | fast suite **2509 passed / 110 skipped / 12 xfailed in 133.19 s**, 34,756 statements = **90.7%** of the release's covered statements |
| W61 | 1 | `test_trainer_async_dataloading` failed ~1 run in 8; the first batch was read mid-copy | the wait was enqueued on the default stream, but `train_step` runs under `with torch.cuda.stream(compute_stream)`, so the reader never awaited the load stream | `compute_stream.wait_stream(load_stream)` before consuming the buffer | **12/12 runs pass**; the spy sees batch 0 again |
| W62 | 2 | coverage was a snapshot, not a direction | no ratchet, and no single population | `COVERAGE=1` adds the flags to the release's own pytest calls; `check_coverage_ratchet.py` holds 38,318 with slack 150 and names the files that lost lines | baseline recorded; a drop fails the step |
| W63 | 2 | one test sets the fast suite's and the unit shard's wall (178.3 s) | the cosine-similarity test trains two MLPs at a budget larger than its assertion needs | trim its epochs/batches to the smallest that still fails on a broken claim; measure before/after | fast suite wall < 60 s; the assertion still fails when the claim breaks |
| W64 | 2 | 63.65% overall: surface 44.4%, local_learning 45.1%, wave 37.7%, runners **0%**, deployments 49.1%, documentation 38.0% | the uncovered mass is CLI/report branches and two modules no test imports | contract tests on public behavior (a report from a record, a wave decision, a refusal by name), no copied outputs (D6) | each named area rises; the ratchet moves |
| W65 | 1 | 113 of 342 files cover no unique line; the demo shard is 777-817 s | demos are artifact producers; capability tests certify floors | keep both out of the fast suite and in the release; do not delete — they answer a different question than coverage | fast suite unchanged; the release keeps the artifacts |

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
- [ ] **0 xfails**: 16 retired in session 7 (W50-W52, W55); 11 remain.
      W53's 4 GATE-0 rows name the deep-path parity primitive; W54's 7
      capability rows are in the progress table with primitive and family.
- [x] **2 skips** remain: the declared-infeasible complex-substrate cells.
      The 31 composer rows and the 4 legality rows run (W46, W47). The
      other 7 property skips are the experiment-invariant rows, which run
      against the readiness store (7 passed).
- [x] The `input_dim` and `compute_loss` contracts are locked both ways
      (W48, W49).
- [ ] ruff < 499, with the retired rules named in the ratchet's docstring;
      Register C's 43 directives migrated and RUF105 enabled (W57).
- [ ] pyright < 3240 errors or a recorded archive-scope decision, and 0
      warnings (W56).
- [ ] The site-build and pre-registration decisions are written where the
      gate lives (W58, W59).
- [x] The fast suite is green in **≤ 2.5 min** (**82.43 s**), reaches
      **≥ 90%** of the release's covered statements (90.7%), and a moved
      test file does not fail it (W60).
- [ ] `COVERAGE=1` holds 38,318 covered statements (63.65%) or rises with a
      re-baseline in the same commit (W62). Not re-measured this session.
- [ ] The 178 s long pole is trimmed (**8.07 s** standalone), but the fast
      suite's wall is **82.43 s**, not **< 60 s** (W63). The remaining wall
      is the schedule of 2500 tests, not one test.
- [ ] The named coverage gaps (surface/report, wave, runners, local_learning)
      have contract tests, each named in its change (W64).

## Remaining work (in order)

1. **P0a — W53's 4 GATE-0 rows.** First the TileEP 200-vs-205 tensor-size
   mismatch: align the BPTT and EP parameter sets in the test (or in
   TileEP), then re-check the deep-settle cosine. The deep-settle and
   Control-Lyapunov rows need the tracked quantity and the claim to agree;
   a scope refusal is legal only with that disagreement named.
2. **P0b — W54's 7 capability rows.** Start with the cheapest: the grpc
   tile-mesh output width (one projection) and the ternary kernel boundary
   (one quantization). The Triton shared-memory rows are a GPU-only ceiling,
   not a CPU defect: record the block-size limit or pick a smaller launch.
3. **P2 — coverage and test time** (W63, W64, W65). The 178 s pole is
   trimmed; the fast wall is 82.43 s. The named gaps (surface/report, wave,
   runners, local_learning) are still contract-test work.
4. **P3 — static debt** (W56, W57). One scope decision for `docs/archive`,
   then the 15 warnings; ruff one group per pass, Register C alongside.
5. **P4 — decisions** (W58, W59).

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
