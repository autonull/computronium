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
   record until the test passes. DONE: 16 retired in session 7, the remaining
   11 markers in session 8 (W53, W54); 0 markers remain.
2. **P1 — locks that do not cover their declared population.** DONE in
   session 7 (W46-W49); the 35 skips are retired and both contracts are
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
| unit | `pytest tests/unit` | 955 passed, 1 xfailed (220.38 s); a later run OOM'd when a foreign `cml codec` job held 9.4 GiB of the 10 GiB device |
| xfails | AST scan of `tests/**/test_*.py` | **11** (4 GATE-0, 7 capability) |

The 9 property skips are 2 declared-infeasible complex-substrate cells and
7 experiment-invariant rows that run against the readiness store.

The primitives shard was not re-run this session: a foreign `cml codec`
job held 9.4 GiB of the 10 GiB device. Run `pytest tests/primitives`
(863 s at handoff) when the device is idle, before the release gate.

## Progress 2026-11-28 (session 8)

**P0a/P0b — all 11 xfail markers retired. 0 markers remain.**

| # | Block | State | Evidence |
|---|---|---|---|
| W53a | EP-BPTT parity (2 markers) | **DONE** | The two tests zipped differently filtered parameter lists and read `.grad` after `train_step` (the BPTT baseline); the EP loop is `local_update` and writes a parameter delta. Replaced with one measured boundary: aggregate cosine **0.132** at β=0.5 (< 0.5), mixed per-parameter signs. Boundary named: a soft β-scaled nudge with the readout inside the energy (deep EqProp credit). |
| W53b | deep gradient flow | **DONE** | `.grad` is None on every composed parameter by design; the credit applies a delta. First-layer delta **6.7e-5** at depths 50 and 100. The test now tracks the delta. |
| W53c | deep-settle accuracy | **DONE** | The in-body xfail became a live near-chance boundary lock (accuracy ≤ 0.3 at 3 train steps; measured chance-level). |
| W53d | Control-Lyapunov | **DONE (bug)** | `_eager_layered_steps` appended one energy per layer per step, so consecutive history entries compared different layers. It now appends the total V once per step; monotone non-increase holds. |
| W54a | grpc tile-mesh output | **DONE** | `_tile_mesh_settle` returned per-tile acts; the credit laws read the block layout `[x, z0..zL, out]`. It assembles blocks (remote tiles fetched), and loss/accuracy read the output block. Test metric contract updated to `free_accuracy` + finite energy. |
| W54b | Triton shared memory (2) | **DONE** | Both fp32 kernels materialized the full H×K tile (294,912 / 557,056 B over the 101,376 B limit at H=512). Both now loop over H in `BLOCK_H=32` chunks and accumulate the second dot; equivalence holds. |
| W54c | CuPy zero-copy | **FILED** | `tests/conftest.py` replaces `cupy` with a MagicMock, so the zero-copy path cannot return real storage. The test skips when `cupy` is mocked (environment refusal, D2); the real path needs a GPU job without the mock. |
| W54d | ternary reference | **DONE** | The reference quantized top-down/recurrent weights too; the kernel routes only bottom-up/output through the substrate operator. The reference now mirrors that split; max diff < 1e-5. |
| W54e | tile-mesh 614k | **FILED** | The xfail duplicated the boundary lock `test_a_box_that_cannot_shrink_is_unimplemented`; the lock now records **628,280 vs 150,000** at the L0 vision box and the input-compression primitive. |
| W54f | PredictiveSettling stub | **DONE** | The W53d tracking fix made `test_prediction_error_decreases` pass; marker removed. |
| W54g | ladder records (7 strict) | **DONE** | One lock now asserts each record's verdict agrees with its measured best (unimplemented stays in the near-chance band and names its close condition; tuned clears it). |
| body | backend arm; ternary+backprop | **DONE** | An unattached arm is a hard assertion; ternary+BackpropCredit asserts the fail-loud `no gradient reached` raise (category fact, not a defect). |

**Gates this session.**

| Gate | Command | State |
|---|---|---|
| property | `pytest tests/property -q` | **3035 passed, 9 skipped** (317.97 s; the one failure was the lint ratchet, caused by the new probe files and fixed) |
| fast | `scripts/run_fast_gates.sh` | **2553 passed, 75 skipped** (138.01 s) |
| affected | kernel/substrate/energy/biology/ladder/pilot/dynamics | 116 passed, 1 skipped |
| ruff | `ruff check .` | **496 findings** (baseline 499; the new probes lint clean) |
| pyright | changed files | legacy noise only; no new class beyond Triton `constexpr` annotations |
| xfails | marker scan | **0**; one body `pytest.xfail` remains in `test_primitive_capability.py` (fires only when composition fails) |
| grpc | full file | 43 passed; 3 subprocess tests fail with `gRPC proto not available` (pre-existing environment) |
| primitives | `pytest tests/primitives` | **780 passed, 135 skipped** (1035.84 s; the handoff row was 863.39 s) |

The fast wall is 138 s with 2553 tests: the 6 formerly-xfailed tests now run,
and the GPU kernel tests add a few seconds. The 82.43 s record was measured
before those tests ran.

## Progress 2026-11-28 (session 9)

**P2/W64 — the uncovered rules now have locks. Three modules, 32 tests.**

| # | Block | State | Evidence |
|---|---|---|---|
| W64a | `experiment/runners` 0% → imported | **DONE** | `test_runner_contracts.py`, 12 tests: the scaling grid is the declared cartesian product (9 cells, integer narrowing, endpoints), a log axis keeps its ratio, one point per dimension is the low end, a scaled coordinate keeps the axes it did not sweep, an ablation variant pins only the varied axis, a replay classifies by its worst metric and skips a metric with no baseline or a zero baseline, a missing arm is "no evidence" (p = 1), an unknown test is refused by name, and the bootstrap separates a shift from an empty difference. |
| W64b | `experiment/wave.py` 37.7% | **PARTIAL** | `test_wave_pricing_lock.py`, 9 tests: a box price wins over its task price, a wave is priced by the boxes it plans, a budget pays startup once and keeps one cell, a serial wave admits only with 1.05x headroom over the last cell, a first cell needs no history, a passed deadline refuses, replicates expand to one cell per seed with distinct measurement keys, and the rejection summary names the top reasons. The planner's mutation/exploration path is still uncovered. |
| W64c | `experiment/surface/report.py` 44.4% | **PARTIAL** | `test_report_front_lock.py`, 11 tests: a two-axis and a six-axis front, a tie is not dominance, mismatched arity is refused by name, a record missing or carrying a non-numeric objective is not a zero, an unclaimed metric is a cost, a coordinate key drops unnamed axes, a measured cell is its structural axes, a registration is dated by its moment or its day (or before any run), and the chance line is read from the task's output dimension (digits → 0.1). Rendering and export paths are still uncovered. |

Measured with the new files alone: `runners` 0% → **45-56%** (ablation 52,
comparison 56, replay 38, scaling 45); `wave.py` **21%** from the pricing lock
alone (the release adds its other tests); `report.py` **15%**.

Fixes the locks forced:

- `_spaced_values` is now one function for both spacings, and a single point
  per dimension returns the low end instead of dividing by `n - 1` (a
  `ZeroDivisionError` before).
- `classify_changes` is one function for the replay split; `_replay_cell` reads
  it, so the policy the tests assert is the policy the runner applies.

**P3/W57 — the `PLW1514` group retired; `BASELINE` 499 → 473.**

All 21 `unspecified-encoding` findings now name `encoding="utf-8"`: two
library sites (`monitoring/alerts.py`, `sec_watch.py`), one notebook cell, and
18 script sites. The other two findings left with W64's refactor
(`replay.py`'s `Mapping`/`Sequence` imports moved into `TYPE_CHECKING`). No
rule was suppressed. `tests/property/test_lint_count_ratchet.py` carries the
pass in its body.

**P4/W58 — the site build is on demand, and `--check` says so.**

`docs/index.html` and `docs/index.md` are gitignored, so a fresh clone has no
artifact and `--check` exited 1 on "staleness" no one could have caused. The
decision: `--check` reports drift only for an artifact that exists; a missing
one prints "not built" and exits 0. Recorded in the builder's docstring.

**Session 9 end state.**

| Gate | Command | State |
|---|---|---|
| property | `pytest tests/property -q` | **3067 passed, 9 skipped, 0 xfailed** (268.02 s) |
| fast | `scripts/run_fast_gates.sh` | **2585 passed, 75 skipped**, 89.45 s (93 s wall); 138.01 s was not reproduced on this host with the same list plus three files |
| ruff | `ruff check .` | **473 findings** (baseline 473, lowered this session) |
| format | `ruff format --check .` | green (1723 files) |
| pyright | changed files | the six new/changed files clean; `docs/build_site.py` and `comparison.py` legacy lines only |
| new locks | the three files | 32 passed |
| site | `docs/build_site.py --check` | 0 with the artifact, 0 with "not built", 1 only on real drift |

## Progress 2026-11-28 (session 10)

**P2/W64 — the credit rules and the render surface are locked; one bug fixed.**

| # | Block | State | Evidence |
|---|---|---|---|
| W64d | `core/local_learning` 45.1% | **PARTIAL** | `test_local_learning_contracts.py`, 20 tests: the Hebbian update scales with `learning_rate` and returns the negated correlation the builder's `w -= w_up` potentiates; a missing free state is a zero update; the contrastive update scales with `importance`, is transposed to the weight layout, and a missing nudged phase is zero; an EP/Hebbian activity rule without settled state is refused by name, a Hebbian rule settles to its prediction, a spiking rule zeroes a fired neuron; the task gradient is the per-sample residual of its own mean loss; the registry round-trips metadata, refuses an unknown variant by name, and lists a copy; a local update writes a delta and leaves `.grad` alone, an autograd step writes the gradient it optimizes. Measured with this file alone: registry 100%, activity 95%, builder 59%, package 40%. The `settling.py` step path stays uncovered. |
| W64e | `surface/report` 44.4% | **PARTIAL** | `test_report_render_lock.py`, 9 tests: the run named, the record count, the axes stratified, an export that round-trips the run's records (and the whole store without a run id), an HTML page that names the run, refuses an empty run by name, the narrative, and each objective's declared direction. Measured with the two report locks alone: **49%** (the front lock alone was 15%). The LaTeX/PDF and stability-analysis paths stay uncovered. |
| W66 | report raised `KeyError` on an empty run | **DONE (bug)** | `_maximizes` read `optimizes`, which indexes `OBJECTIVES_REGISTRY`; that registry is seeded only as a side effect of appending a record, so a read-only store (dashboard, CLI) reported with an empty registry and `claim_metrics` silently dropped every objective. `_ensure_objective_registry` seeds once, guarded by a lock and a module flag; `_maximizes` and `claim_metrics` call it. An empty run now renders a report that names the run and counts zero records. |

One convention the lock records rather than changes: `TaskHandler.compute_loss_and_grad`
returns **per-sample** residuals against a **batch-mean** loss, so the batch
size is the factor between them. No caller in the library uses it.

**Session 10 end state.**

| Gate | Command | State |
|---|---|---|
| property | `pytest tests/property -q` | **3096 passed, 9 skipped, 0 xfailed** (262.66 s) |
| fast | `scripts/run_fast_gates.sh` | **2614 passed, 75 skipped**, 89.91 s (92 s wall) |
| ruff | `ruff check .` | **473** (baseline 473; no new finding) |
| format | `ruff format --check .` | green |
| pyright | the four new lock files | clean (`report.py` keeps its legacy 43) |
| report | two locks alone | `surface/report.py` 49% |
| local learning | one lock alone | package 40%, registry 100% |

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
| W57 | 3 | ruff 473 (was 499) | PLW1514 retired this session (21 sites named their encoding); next groups: E402 56, RUF105 43, complexity 119 (C901 36, PLR0912 16, PLR0915 20, PLR1702 17, PLR0914 29), PLW0717 36, F841 20, S110 20, PLW2901 14 | one pass per named group, `BASELINE` lowered and the rules named; Register C migrates the 43 `# ruff: ignore` directives and enables RUF105 | `BASELINE` < 473 per pass |
| W58 | 3 | the site build has no gate | **DONE** (session 9): the outputs are gitignored, so `--check` exited 1 on a fresh clone for an artifact that cannot exist | `--check` compares only an artifact that exists; a missing one prints "not built" and exits 0 | 0 with the artifact, 0 without it, 1 on real drift; recorded in the builder's docstring |
| W59 | 3 | the 0.277 registration was committed after the first seed | the mtimes prove the order; the commit does not | commit the registration before the launch on the next claim rung | the commit order proves the box |
| W60 | 2 | the release pays ~62 min for 63.65% coverage and nothing ranks a test by the lines it buys | suite order was never measured; 113 of 342 files cover no line another file does not | per-test attribution (`--cov-context=test` + durations) and a greedy `new lines / second` selection; `configs/fast_suite.txt` + `scripts/run_fast_gates.sh` | fast suite **2509 passed / 110 skipped / 12 xfailed in 133.19 s**, 34,756 statements = **90.7%** of the release's covered statements |
| W61 | 1 | `test_trainer_async_dataloading` failed ~1 run in 8; the first batch was read mid-copy | the wait was enqueued on the default stream, but `train_step` runs under `with torch.cuda.stream(compute_stream)`, so the reader never awaited the load stream | `compute_stream.wait_stream(load_stream)` before consuming the buffer | **12/12 runs pass**; the spy sees batch 0 again |
| W62 | 2 | coverage was a snapshot, not a direction | no ratchet, and no single population | `COVERAGE=1` adds the flags to the release's own pytest calls; `check_coverage_ratchet.py` holds 38,318 with slack 150 and names the files that lost lines | baseline recorded; a drop fails the step |
| W63 | 2 | one test sets the fast suite's and the unit shard's wall (178.3 s) | the cosine-similarity test trains two MLPs at a budget larger than its assertion needs | trim its epochs/batches to the smallest that still fails on a broken claim; measure before/after | fast suite wall < 60 s; the assertion still fails when the claim breaks |
| W64 | 2 | 63.65% overall: surface 44.4%, local_learning 45.1%, wave 37.7%, runners **0%**, deployments 49.1%, documentation 38.0% | the uncovered mass is CLI/report branches and two modules no test imports | contract tests on public behavior (a report from a record, a wave decision, a refusal by name), no copied outputs (D6) | **PARTIAL** (sessions 9-10): runners 0% → 45-56%, report 49% and local_learning 40% measured alone, 61 new tests in five files; the report's LaTeX/PDF and stability paths, the surface CLI branches, `settling.py`, `deployments` and `documentation` still lack contract tests |
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
- [x] **0 xfails**: 16 retired in session 7 (W50-W52, W55); the remaining
      11 markers retired in session 8. One body `pytest.xfail` stays in
      `test_primitive_capability.py` (composition failure only).
- [x] The property skips are the declared-infeasible complex-substrate
      cells and the experiment-invariant rows (9 skips). The fast suite's
      75 skips are its declared tier split. The CuPy zero-copy test skips
      because the suite mocks CuPy (environment refusal, D2).
- [x] The `input_dim` and `compute_loss` contracts are locked both ways
      (W48, W49).
- [ ] ruff < 473, with the retired rules named in the ratchet's docstring;
      Register C's 43 directives migrated and RUF105 enabled (W57). The
      measured count is **473** (baseline 473; session 9 retired PLW1514's
      21 sites).
- [ ] pyright < 3240 errors or a recorded archive-scope decision, and 0
      warnings (W56).
- [x] The site-build decision is written where the gate lives (W58: a
      missing artifact is "not built", not stale). The pre-registration
      order (W59) is proved on the next claim rung.
- [x] The fast suite is green in **≤ 2.5 min** (**89.91 s** with 2614
      passed / 75 skipped; session 10 re-measured the list plus five files),
      reaches **≥ 90%** of the release's covered statements (90.7%), and a
      moved test file does not fail it (W60). The 138.01 s session-8 figure
      was not reproduced on this host.
- [ ] `COVERAGE=1` holds 38,318 covered statements (63.65%) or rises with a
      re-baseline in the same commit (W62). Not re-measured this session.
- [ ] The 178 s long pole is trimmed (**8.07 s** standalone), but the fast
      suite's wall is **89.91 s**, not **< 60 s** (W63). The remaining
      wall is the schedule of 2614 tests, not one test.
- [ ] The named coverage gaps (surface/report, wave, runners,
      local_learning) have contract tests, each named in its change (W64).
      **Runners, wave pricing, the report front and render surface, and
      the local-learning credit/task rules are locked** (sessions 9-10, 61
      tests); the CLI-branch, `settling.py`, LaTeX/PDF, `deployments` and
      `documentation` paths remain.

## Remaining work (in order)

1. **P2 — coverage and test time** (W64, W65). Session 9 locked the runner,
   wave-pricing and report-front rules (32 tests, `runners` 0% → 45-56%).
   Session 10 locked the local-learning credit/task rules and the report's
   render surface (29 more tests; `report.py` 49% and the
   `local_learning` package 40% measured alone), and fixed the report's
   unseeded objective registry (W66). Still open, in the order they buy
   lines: the report's LaTeX/PDF and stability-analysis paths,
   `experiment/surface/cli.py`'s command branches, `core/local_learning`'s
   `settling.py` step path, `deployments` (537) and `documentation`
   (499). Re-measure the coverage ratchet with
   `COVERAGE=1` before the next re-baseline; the fast wall is 89.91 s, so
   the `< 60 s` clause in W63 stays open (the 2500-test schedule, not one
   test).
2. **P3 — static debt** (W56, W57). Ruff is 473 with the baseline at 473:
   the next pass retires a named group (E402 56, complexity 119, RUF105 43
   via Register C, PLW0717 36, F841 20, S110 20) and lowers `BASELINE` in
   the same commit. W56 still owes the one-time `docs/archive` scope
   decision for pyright (680 of its 3240 errors) and the 15 warnings.
3. **P4 — decisions** (W59): W58 is closed; the registration-before-launch
   order is proved on the next claim rung (commit the registration before
   the first seed runs).
4. **Release** — re-run `scripts/run_local_gates.sh` on the final tree
   (the primitives shard is the outstanding shard; queued on the idle
   device).
5. **CuPy row** — run the zero-copy test in a GPU job whose conftest does
   not mock `cupy`; the skip is the environment, not the path.

The 0.277 block is closed, and no further rung is mandated: a second credit
family is a **new claim**, not a confirmation of this one, and runs only with
its own pre-registered box.

## Notes

- Commit per group (locks / bugs / static / docs), never one mega-commit;
  the group's gate is the evidence in its message. Nothing is pushed.
- A number travels with its ruler: state the n, the box, and the metric's
  resolution beside it.
- W46-W59 continue W1-W45; a number is never reused.
- A composed system's local credit writes a **parameter delta**, not
  `.grad`; a parity test must track the delta it applies (W53b). A tracked
  energy history must hold **one total sample per step**, not one per layer
  per step (W53d).
- The suite's conftest replaces `cupy` with a MagicMock; a CuPy-path test
  skips on a mocked module rather than reading empty zero-copy tensors (D2
  environment refusal, W54c).
- `docs/figures/manifest.json` and `docs/figures/run_records/*.json` are
  written only by the demo gate; the re-pin commit is the demo gate's run.
- A capability gap is a row, not a verdict: it names the primitive, its cost,
  and the task family it unlocks. A high-effort gap that a cheap arm can
  answer is a defect in the plan, not in the mechanism.
