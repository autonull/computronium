# TODO107 — Local release closure: tests, SEC readiness, acceleration

## Scope

GitHub Actions is disabled: the five workflows are in
`.github/workflows.disabled/`, and
`tests/unit/test_github_workflows_disabled.py` fails if a YAML file returns
to `.github/workflows/`. The release target is therefore
`scripts/run_local_gates.sh`, a local sequence, not a CI workflow.

The goal, in this order:

1. **P0 — every pytest shard green:** property + figure lock, primitives,
   algorithms + acceleration, unit, integration demo, acceptance.
2. **P1 — experiment-ready:** one real SEC cell writes a record, `comp demo`
   completes, breadth stays PASS.
3. **P2 — performance and test acceleration:** the profiled wins are locked;
   the next named cost is measured, not guessed.
4. **P3 — static hygiene:** format green; ruff and pyright are ratchets with
   a direction, not release blockers.

## State at handoff (2026-11-26)

| Gate | Command | State |
|---|---|---|
| GitHub | `ls .github/workflows` | **DISABLED** (moved; lock passes) |
| format | `ruff format --check .` | **FAIL**: 13 files |
| lint | `ruff check .` | 640 findings; ratchet 640 (2 passed) |
| types | `pyright .` | 3269 errors, 525 warnings (hygiene, not a release gate) |
| property | `pytest tests/property` | per-file locks green; one artifact not run since the size edits |
| primitives | `pytest tests/primitives` | **UNVERIFIED** |
| algorithms | `pytest tests/algorithms` | **UNVERIFIED** |
| acceleration | `pytest tests/acceleration` | parity 150 passed / 75 skipped (targeted) |
| unit | `pytest tests/unit` | **UNVERIFIED** |
| demo | `pytest tests/integration -m demo` | **PARTIAL**: `test_demo_ntm_local` 131 s serial |
| acceptance | `pytest tests/acceptance` | **UNVERIFIED** |
| breadth | `comp gate breadth` | **PASS** (17 error-aware credits) |
| build | `python -m build` | **PASS** (sdist + wheel) |
| audit | `pip-audit` | **PASS** (local packages skipped) |
| Rocq | `make -C rocq all` | **OUT OF SCOPE**: 90299/90300 version skew; GitHub-only job |

The one-Jacobian fix (`20dc2daa`) and the test-size reductions
(`8eb31717`) are committed. The workflow move is `bfc553d4`.

## Progress 2026-11-26

| Batch | State | Evidence |
|---|---|---|
| 0 static baseline | **DONE** | format green (13 files formatted); stream lock sync; pyright ratchet `configs/pyright_ratchet.json` + `scripts/check_pyright_ratchet.py` (measured 3260/525); `scripts/run_local_gates.sh` written; pre-commit fast locks |
| 1 runtime guards | **DONE** | parity decision cached per cell (`test_attach_parity_lock.py`); one-Jacobian count lock; eqprop reference-only note + detach lock; lazy stability gate both directions (`test_stability_energy_metrics_lock.py`) |
| 2 property shard | **PARTIAL** | one run: 2936 passed, 53 skipped, 30 xfailed, 2 failed; both failures fixed and re-passed targeted (`test_lint_count_ratchet`, sampler objectives). Claim fixture 5→3 epochs: 27 passed in 117 s |
| 3 remaining shards | **PARTIAL** | primitives 780 passed / 135 skipped (12:28); acceleration 440 passed / 75 skipped (22 s); unit 2 failures fixed and re-passed targeted; `tests/algorithms` no longer exists (removed from `testpaths` + script) |
| 4 demo + acceptance | **PARTIAL** | demo 24 passed; figure lock re-pinned (7 stale hashes) and now passes; acceptance 46 passed / 5 failed (todo63); after the W30 fixes `TestFirstGovernedClaim` is 4/5, `test_cross_domain_evaluation` still sees one task |
| 5 SEC readiness | **PARTIAL** | real campaign: 450 records in 279 s at the 300 s budget (3 tasks × 3 credits × 5 seeds); `comp coverage report` PASS (digits 45 cells/152 records, mnist 45/98); `comp demo` PASS; one-cell survey wrote 1 completed record; `comp repro` FAILED (W31) |
| 6 release | **OPEN** | `pip-audit` PASS, `python -m build` PASS, `generate_docs.py --all --check` PASS; `scripts/run_local_gates.sh` not yet run because acceptance and replay are red |

Session commits: `b21988c5` (readiness code/tests/ratchets), `7996dc77`
(docs figures re-pin). This TODO commit records the open acceptance and
replay work.

Measured this session:

- `ruff check . --no-cache`: 551 findings (baseline lowered 659 → 551).
- `pyright .`: 3260 errors, 525 warnings (baseline 3269/525 → 3260/525).
- Property shard: 444.67 s; primitives: 748.67 s; acceleration: 22.08 s; unit: 156.33 s; demo: 511.86 s.
- Claim fixture: 117.01 s at 3 epochs (was 5); thermodynamic_contrast clears the
  digits bar on all five seeds at 3 epochs, local_contrastive does not.

## Decisions

**D1 — The local gate is the release.** GitHub is disabled; do not spend a
session repairing a CI that does not run. Re-enabling GitHub is a deliberate
move with its own ticket. The workflows archive is the record, not a queue.

**D2 — Consolidate the plan around four priorities.** The old plan treated
22 CI steps as equal. This ticket orders by what makes an experiment
possible: tests, SEC readiness, performance, static hygiene. A gate that
does not block an experiment moves to P3 or out.

**D3 — P0 is the whole pytest surface, once.** Each suite runs once, in one
sequence, with its own log. A green suite is not rerun. The property shard
is the largest, so it runs first in the test batch; a failure stops the
release before the cheaper suites re-pay its cost.

**D4 — Format is a gate; lint and types are ratchets.**
Format the 13 files once. `ruff check .` stays at the ratchet; pyright gets
a count ratchet (`3269 errors, 525 warnings`) and is **not** a release gate
while the count is legacy. The ratchet is a direction with a deadline, not a
waiver; new modules stay strict.

**D5 — The eqprop kernel is reference-only on a composed relu cell.**
The tanh kernel cannot reproduce a relu geometry; the attach guard detaches
to the reference, and that is correct. Declare it in the acceleration matrix
and capability card, and lock the detach. Closing it needs one activation
contract for both rungs; its runtime value is measured before scheduling.

**D6 — Cache the attach parity probe per composed cell.**
The guard currently runs one forward + one kernel equilibrium per
`evaluate_cell`; the decision depends on the cell, not the seed. Cache it by
`(algorithm id, coordinate.cell_key(), geometry params)`. This is the largest
avoidable runtime cost the repair added. Lock: one probe per unique cell.

**D7 — One Jacobian per cell is a permanent lock.**
The 3→1 change is correctness-neutral. A count test must fail if a second
`_full_jacobian_tensor` returns per `compute_stability_metrics`.

**D8 — Walltime is an outcome; counts and profiles are the ruler.**
This host runs other processes. cProfile call counts (Jacobians, probes,
cells, proposals) decide; a pytest duration is recorded, not compared.

**D9 — Test acceleration is measured, not guessed.**
Profile the final property shard once. Apply only the top named cost:
- persistent `TORCHINDUCTOR_CACHE_DIR` in the local gate (compiled settle
  graphs repeat);
- the claim fixture's 5-epoch regime tried at 3 and 2 epochs on one seed;
  keep the smallest that clears the digits bar (the assertion stays);
- `cell_config` composition profiled in the generated suite; cache a second
  composition only if the profile names it.
No assertion is weakened; the box shrinks.

**D10 — Experiment readiness is a smoke, not a claim.**
One `survey_cli` cell at L0, one task, one seed, one axis, plus
`comp demo`. A record must reach the store; breadth is already PASS. The
claim path stays locked by `test_claim_report_lock`.

**D11 — One local release command.**
`scripts/run_local_gates.sh` runs the corrected order with `set -e`:
static ratchet, property, primitives, algorithms + acceleration, unit,
integration demo, acceptance, audit, build. The release calls that one
script; no per-session command list.

**D12 — Pre-commit runs fast gates only.** The hook currently runs the whole
property suite on every commit, which contradicts the AGENTS rule and costs
the shard's full walltime per commit. Replace it with the fast static locks
(ratchet, marker census, workflows-disabled, the changed-file smoke) and
move the property shard to `run_local_gates.sh`. A hook that costs minutes
is a hook people disable.

**D13 — Stability telemetry is lazy.** After the one-Jacobian fix, the
Jacobian is still ~28% of a cell's profiled CPU. It is only needed when a
run's objectives or report name a stability metric. Gate it on the declared
objectives/report: a cell with `validation_accuracy` only must not compute
it; a cell with a stability objective must. Lock both directions.

**D14 — Compile reuse is measured before it is adopted.**
The settle graph recompiles per shape; the profile names
`torch._dynamo.convert_frame` warnings. Try `dynamic=True` (or a shape
bucket) on the settle kernel and count recompiles and steady-state cost.
Adopt only if it removes recompiles without slowing the steady state.

**D15 — A campaign smoke, coverage, and repro are part of readiness.**
One cell is a smoke, not a campaign. Run a 2-task × 2-credit × 2-seed
campaign, `comp coverage`, and `comp repro --device cpu` on its store. The
claim/limitation path must render; the 0.277 seed block is re-measured with
a pre-registered `n_max` (fixed-n CI, no peeking) before it is called a gap.

## Verification rules

1. One run per unresolved question; a green suite is evidence, not a rerun.
2. Select by symbol; a `testpaths` shard is a release artifact.
3. A cached failure is not a verdict; collect with `--co` first.
4. Long runs use `nohup ... > logs/<name>.log 2>&1 &`, `-rf --tb=line`,
   and ≤2-minute polling. Never two pytest suites concurrently.
5. A long test gets a marker and a `KNOWN_LONG` row together.
6. Every number carries its ruler: work counts for the decision, walltime
   as the outcome.

## Work batches

| # | One shell block | Decides | Budget |
|---|---|---|---|
| 0 | format 13; fix stream async; add the pyright ratchet; edit `.pre-commit-config.yaml` to drop the full property suite; write `scripts/run_local_gates.sh`; record ruff/pyright counts | static baseline and the fast hook exist | <15 min |
| 1 | parity-probe cache + Jacobian count lock + eqprop detach lock; probe lazy stability telemetry and `dynamic=True` settle compile; targeted stability/cell/acceleration files | runtime guard is cheap and locked; the next runtime win is measured | <30 min |
| 2 | `pytest tests/property tests/integration/test_gallery_lock.py::test_figure_lock -q -rf --tb=line > logs/property_release.log`; then profile the top test and try the claim fixture at 3 and 2 epochs on one seed | property is one green artifact; the top cost and the bar-clearing claim box are named | measured ×1 |
| 3 | `pytest tests/primitives`, then `tests/algorithms tests/acceleration`, then `tests/unit`, each once | the remaining P0 shards are green | measured ×1 each |
| 4 | `pytest tests/integration -m demo`; then `pytest tests/acceptance` | demo and acceptance are green | measured ×1 each |
| 5 | SEC smoke: one `survey_cli` cell + `comp demo`; then a 2×2×2 campaign, `comp coverage`, and `comp repro --device cpu` on its store; profile the cell | experiments are ready; the runtime top cost and the claim gap are named | measured ×1 |
| 6 | release: `scripts/run_local_gates.sh`, `pip-audit`, `python -m build`, docs check | one local green artifact | one pass |

Batch 0 commands:

```bash
uv run ruff format computronium/core/system_trainer/rl_trainer.py \
  computronium/domains/analog.py computronium/domains/graph.py \
  computronium/domains/neuromorphic.py computronium/domains/photonic.py \
  computronium/domains/quantum.py \
  computronium/experiment/execution/backends.py \
  computronium/experiment/sec_deep_dive.py configs/void_rules_learned.py \
  scripts/auto_register_claims.py scripts/fit_cost_model.py \
  scripts/probes/todo104_a2_settle_recompile.py scripts/run_rung3_claims.py
uv run ruff format --check .
uv run ruff check . --no-cache
uv run pyright .
uv run python -m pytest tests/test_timeout_marker_policy.py -q
```

Batch 5 SEC smoke:

```bash
uv run python -m computronium.experiment.survey_cli 0.1 --mode learn \
  --policy random --device cuda --tasks digits --fidelity L0 \
  --axes '{"substrate":["digital"],"geometry":["feedforward"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient"],"update":["euclidean"]}' \
  --epochs 1 --n-seeds 1
uv run comp demo
```

## Defect queue

| # | Rung | Symptom | Cause | Fix | Verify |
|---|---|---|---|---|---|
| W1 | 0 | GitHub Actions is disabled | the repository does not use CI | workflows archived; a lock keeps the active path empty | lock passed |
| W2 | 0 | format fails on 13 files | legacy files predate ruff | format once (Batch 0) | format check |
| W3 | 1 | `ruff check .` exits 1 at 640 | legacy findings | ratchet as the gate; lower the count each hygiene pass | ratchet 2 passed |
| W4 | 1 | `pyright .` exits 1 at 3269/525 | legacy type debt | add a pyright count ratchet; touched modules clean | new ratchet |
| W5 | 1 | property is not one artifact | the last full run predates the size edits | Batch 2 once | log |
| W6 | 1 | demo is partial | `test_demo_ntm_local` under two workers | serial run; record | demo gate |
| W7 | 1 | primitives/algorithms/unit unverified | the Jacobian change touches every cell | Batch 3 | logs |
| W8 | 1 | acceptance unverified | not run after the repairs | Batch 4 | log |
| W9 | 1 | eqprop kernel never attaches on a composed cell | tanh vs relu; guard detaches | declare reference-only in the matrix/card; lock the detach | parity + cell |
| W10 | 1 | parity probe costs one forward per cell | decision per cell, probe per seed | cache by cell key; count lock | new lock |
| W11 | 1 | a second Jacobian can return unnoticed | no count lock | add `test_jacobian_call_count_lock` | new lock |
| W12 | 0 | stream test is `async` with no await | sync body | make it sync | ruff finding gone |
| W13 | 2 | claim fixture trains 5 epochs | the bar-clearing minimum is unmeasured | 5→3→2 ladder, one seed; keep the smallest | val_acc clears bar |
| W14 | 2 | the top property/one-cell cost is unnamed | no profile after the size edits | cProfile the shard and one SEC cell | top 5 named |
| W15 | 0 | `docs/generated/` may be stale | gitignored artifact | `generate_docs.py --all --check` in release | check |
| W16 | 2 | every commit pays the full property suite | the pre-commit hook runs `tests/property/` | drop it; keep fast static locks; the suite belongs to the release script | hook <30 s |
| W17 | 2 | the Jacobian is ~28% of cell CPU even when no objective needs it | `_post_training_metrics` computes stability unconditionally | gate on the declared objectives/report; a test for both directions | new lock |
| W18 | 2 | the settle graph recompiles per shape | `torch.compile` without a dynamic/shape policy | probe `dynamic=True`/shape bucket; count recompiles; adopt only if steady state holds | probe |
| W19 | 2 | the 0.277 seed block is called a claim gap without error control | n is too small to decide | re-measure with a pre-registered `n_max` and fixed-n CI; file the mechanism if it still fails | claim or gap |
| W20 | 1 | a changed-file pyright hook blocks on legacy errors | 26 errors in the touched modules | fix them, or per-line ignore with a reason; then the hook is honest | changed-file hook |
| W21 | 1 | `pytest tests/algorithms` collected 0 tests | TODO97 deleted the directory but `testpaths` and the release plan kept it | remove it from `pyproject.toml` and `run_local_gates.sh` | collect |
| W22 | 1 | the figure lock did not run in the property shard | `-m 'not demo'` deselects the demo-marked lock even with an explicit node id | run it in the demo gate; re-pin the stale manifest | `-m demo` green |
| W23 | 1 | the latency-proxy walltime test flipped under xdist | walltime is an outcome, not a ruler (D8) | mark it `benchmark`; the structural ordering stays the gate | unit green |
| W24 | 1 | NCA rejection test raised `grid_hw` missing | signature change predates the test | pass `grid_hw=(GRID, GRID)` | unit green |
| W25 | 1 | promotion lock expected every record to leave L0 | a PASS seed with a failed sibling is ineligible and legitimately stays L0 | assert no eligible pair stays L0; use a credit that clears the bar | acceptance green |
| W26 | 1 | CEEC export found no claim-eligible cell | `local_contrastive` dips below the digits bar | use `thermodynamic_contrast` at 3 epochs | acceptance green |
| W27 | 1 | the loop did not write `defect_constraints.json` on a clean run | `DefectRegistry` persisted only when a failure was recorded | persist the empty list at construction | acceptance green |
| W28 | 1 | unified-kernel tests expected schedule fidelity L0 after promotion | promotion may raise a single-seed schedule to L1 | assert `{"L0","L1"}`; the schema is the lock | acceptance green |
| W29 | 1 | S10 proposed no promotions | the 120 s run ceiling was spent in round 1; the allocator skipped | raise the test's budget to 600 s (a ceiling, not a duration) | acceptance green |
| W30 | 1 | todo63 loop fixtures timed out at 600 s | `hours=1.0` plus 0.1 h per stage ran one task for the whole mark | per-stage budget from the total, 900 s watchdog, one loop worker; serial run removed the libtorch segfault | 4/5 first-claim tests green; cross-domain still one task |
| W31 | 1 | `comp repro` compared different seeds and host metrics | it matched by `cell_key` (no seed) and checked RSS/latency/device energy; `deterministic=True` also changes the measurement key | match `(cell_key, seed)`, exclude host metrics from the default diff; `--metrics` opts in | still 74 mismatches on a CPU survey: `epochs_run`/`flops` differ, so replay composes another cell |

## Efficiency rules

- Fail fast: format and ratchets before the 8–10 minute property shard;
  property before the cheaper shards so a failure stops the release early.
- One artifact per suite; never rerun a green suite "to confirm".
- Keep `-n 4` from `addopts`; never launch two suites concurrently. A
  release script runs the sequence, not a parallel fan-out.
- Cache: persistent `TORCHINDUCTOR_CACHE_DIR`; `UV_LINK_MODE=copy`.
- The local script is the only order; ad-hoc command lists are not evidence.

## Closure criteria

- [ ] `scripts/run_local_gates.sh` exits 0.
- [ ] Property + figure lock, primitives, algorithms + acceleration, unit,
      demo, acceptance are each green once.
- [ ] `comp demo` and the one-cell SEC run write a record; breadth PASS.
- [x] Format green; ruff ratchet green and lowered (659 → 551); pyright
      ratchet exists (`3260/525`) and the TODO106-touched test errors are
      clean. The remaining `evaluate.py` type findings are legacy.
- [x] The Jacobian, parity-probe, and detach locks are green.
- [x] Lazy stability telemetry is locked in both directions.
- [ ] The `dynamic=True` compile probe is measured and either adopted or
      rejected. It is adopted and the TODO104 A2 probe exists, but the
      promotion run still logs `recompile_limit (8)` for a changing layer
      count: the next cost is a shape bucket/padding, not a silent pass.
- [x] Pre-commit runs the fast locks only, and the full property suite is in
      `run_local_gates.sh`.
- [ ] The campaign writes claims/limitations; `comp coverage` and
      `comp repro --device cpu` pass; the 0.277 block has a pre-registered
      `n_max` verdict. Measured campaign: 450 records in 279 s.
- [ ] `generate_docs.py --all --check`, `pip-audit`, and `python -m build`
      are green.
- [x] The eqprop reference-only condition is declared in its generated spec
      page, and the detach guard is locked.
- [x] The GitHub-disabled lock is green.

## Remaining work (in order)

1. **Acceptance / todo63 (W30).** The `TestFromScratchTest` and
   `TestFirstGovernedClaim` class fixtures are wall-clock loops. Under
   `-n 4` they lose throughput and fail their domain/frontier assertions; a
   serial run segfaulted in `libtorch_cpu.so` with two loop workers, which
   `cell_workers=1` removed. `TestFirstGovernedClaim` is now 4/5; the
   remaining failure is `test_cross_domain_evaluation` (the loop still
   records one task). Decide one: replace the loop's wall-clock budget with
   a deterministic cell count, or move the two classes to the `slow` tier
   with a measured watchdog. The failing command is
   `uv run python -m pytest tests/acceptance/test_todo63_scientific_validation.py -n 0 -q -rf --tb=line`.
2. **Replay (W31).** `comp repro` still mismatches a CPU survey: matched by
   `(cell_key, seed)` and host metrics excluded, the replay's `epochs_run`
   and `flops` differ, so it composes another cell. Find the schedule or
   spec field that differs between the original and replay before the
   readiness claim. Command:
   `uv run comp repro --store experiments/readiness_cpu.duckdb --run-id 08d5c47e --device cpu`.
3. **Batch 5 readiness (done except replay).** `comp demo`, the one-cell
   survey (`experiments/one_cell_smoke.duckdb`, run `dd49fb82`), and
   `comp coverage report` all pass; only W31 (replay) remains.
4. **Release.** `scripts/run_local_gates.sh` once, with
   `TORCHINDUCTOR_CACHE_DIR` persistent. Acceptance and replay are the only
   open gates; the other shards have their measured logs above.
5. **D14 follow-up.** Count recompiles for a layer-count sweep and adopt a
   shape bucket/padding only if it removes them without slowing the steady
   state. Record the measured number beside `compile_settle`.

## Notes

- Commit per group (static / perf / tests / docs), never one mega-commit;
  each group's lock is the evidence in its message. Nothing is pushed.
- A ratchet is a direction: every hygiene pass lowers both counts; a pass
  that only moves files without lowering a count is not a closure.
- `docs/figures/manifest.json` is written only by the demo gate.
- Rocq and GitHub are out of the local release scope; they are separate
  toolchain tickets, and the version-skew failure is recorded here so it is
  not rediscovered.
- The one-cell SEC run is a readiness smoke, not a claim; the claim path is
  already locked.
