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
| 0 | format 13; fix stream async; add the pyright ratchet; write `scripts/run_local_gates.sh`; record ruff/pyright counts | static baseline and the release command exist | <15 min |
| 1 | parity-probe cache + Jacobian count lock + eqprop detach lock; targeted stability/cell/acceleration files | runtime guard is cheap and locked | <15 min |
| 2 | `pytest tests/property tests/integration/test_gallery_lock.py::test_figure_lock -q -rf --tb=line > logs/property_release.log`; then profile the top test and try the claim fixture at 3 and 2 epochs on one seed | property is one green artifact; the top cost and the bar-clearing claim box are named | measured ×1 |
| 3 | `pytest tests/primitives`, then `tests/algorithms tests/acceleration`, then `tests/unit`, each once | the remaining P0 shards are green | measured ×1 each |
| 4 | `pytest tests/integration -m demo`; then `pytest tests/acceptance` | demo and acceptance are green | measured ×1 each |
| 5 | SEC smoke: one `survey_cli` cell + `comp demo`; profile the cell | experiments are ready; runtime top cost is named | measured ×1 |
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
| D1 | 0 | GitHub Actions is disabled | the repository does not use CI | workflows archived; a lock keeps the active path empty | lock passed |
| D2 | 0 | format fails on 13 files | legacy files predate ruff | format once (Batch 0) | format check |
| D3 | 1 | `ruff check .` exits 1 at 640 | legacy findings | ratchet as the gate; lower the count each hygiene pass | ratchet 2 passed |
| D4 | 1 | `pyright .` exits 1 at 3269/525 | legacy type debt | add a pyright count ratchet; touched modules clean | new ratchet |
| D5 | 1 | property is not one artifact | the last full run predates the size edits | Batch 2 once | log |
| D6 | 1 | demo is partial | `test_demo_ntm_local` under two workers | serial run; record | demo gate |
| D7 | 1 | primitives/algorithms/unit unverified | the Jacobian change touches every cell | Batch 3 | logs |
| D8 | 1 | acceptance unverified | not run after the repairs | Batch 4 | log |
| D9 | 1 | eqprop kernel never attaches on a composed cell | tanh vs relu; guard detaches | declare reference-only in the matrix/card; lock the detach | parity + cell |
| D10 | 1 | parity probe costs one forward per cell | decision per cell, probe per seed | cache by cell key; count lock | new lock |
| D11 | 1 | a second Jacobian can return unnoticed | no count lock | add `test_jacobian_call_count_lock` | new lock |
| D12 | 0 | stream test is `async` with no await | sync body | make it sync | ruff finding gone |
| D13 | 2 | claim fixture trains 5 epochs | the bar-clearing minimum is unmeasured | 5→3→2 ladder, one seed; keep the smallest | val_acc clears bar |
| D14 | 2 | the top property/one-cell cost is unnamed | no profile after the size edits | cProfile the shard and one SEC cell | top 5 named |
| D15 | 0 | `docs/generated/` may be stale | gitignored artifact | `generate_docs.py --all --check` in release | check |

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
- [ ] Format green; ruff ratchet green and lowered; pyright ratchet exists
      and the TODO106-touched modules are clean.
- [ ] The Jacobian, parity-probe, and detach locks are green.
- [ ] `generate_docs.py --all --check`, `pip-audit`, and `python -m build`
      are green.
- [ ] The eqprop gap is declared in the matrix/card with a failing-today
      lock, and its runtime value is measured.
- [ ] The GitHub-disabled lock is green.

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
