# TODO107 — Release closure: CI, capability, and experiment readiness

## Scope

TODO106 closed the property-shard repair and accelerated its slow locks.
TODO107 makes the repository **CI-green and experiment-ready**: every gate
in `.github/workflows/ci.yml` either runs a command that exists and passes,
or is removed with a reason; the SEC loop runs one real cell and one real
campaign smoke; and the performance wins the profiler found are locked.

The release target is one `scripts/run_ci_gates.sh` run in the `ci.yml`
order, not a per-session survey.

## CI gate map (measured 2026-11-26)

| # | CI step | Actual command | State |
|---|---|---|---|
| 1 | Install | `uv sync --dev` (CI) | **DRIFT**: AGENTS requires `--dev --all-extras` |
| 2 | Format | `ruff format --check .` | **FAIL**: 13 files |
| 3 | Lint | `ruff check .` | **FAIL**: 640 findings; ratchet 640 (2 passed) |
| 4 | Types | `pyright .` | **FAIL**: 3269 errors, 525 warnings |
| 5 | Property | `pytest tests/property/ -q` | **UNVERIFIED** after the size edits; locks green |
| 6 | Demo | `pytest tests/integration/ -m demo -q` | **PARTIAL**: `test_demo_ntm_local` 131 s serial |
| 7 | Vertical slice | `tests/integration/test_vertical_slice_gate.py` | **MISSING FILE**; replacements named below |
| 8 | Version | `tests/unit/test_version_consistency.py` | **PASS** (5 passed with drift) |
| 9 | Drift | README snippets + root exports | **PASS** (same 5) |
| 10 | Presets | inline `_build_system_from_flat_config` loop | **UNVERIFIED** |
| 11 | Registry audit | `comp audit --metadata` | **MISSING COMMAND** (`comp` has no `audit`) |
| 12 | Composition | `scripts/validate_composition.py` | **MISSING FILE** (only `scripts/archive/`) |
| 13 | Repro | `comp repro --device cpu` | **UNVERIFIED** |
| 14 | Audit | `pip-audit` | **PASS** |
| 15 | Parity | `tests/acceleration/test_all_implementations.py` | **PASS** (150 passed, 75 skipped) |
| 16 | Primitives | `pytest tests/primitives/ -q` | **UNVERIFIED** after the Jacobian change |
| 17 | Algorithms | `pytest tests/algorithms/ -q` | **UNVERIFIED** |
| 18 | Matrix | `python -m computronium.acceleration.matrix` | **PASS** (JSON written) |
| 19 | Microbench | `... microbench --all` with `|| true` | **NOT A GATE**; make it a smoke |
| 20 | Rocq | `make -C rocq all` | **FAIL**: `Utils.vo` version 90299 vs expected 90300; real target is `rocq/Makefile` |
| 21 | Build | `python -m build` | **PASS** (sdist + wheel) |
| 22 | Acceptance | not in CI | **UNVERIFIED** |

`comp gate breadth` **PASS** (17 error-aware credits). The one-Jacobian
change is committed (`20dc2daa`); the test-size reductions are committed
(`8eb31717`).

## Decisions

**D1 — First fix CI itself; a gate that names a missing file is not a gate.**
Four CI steps cannot run (rows 7, 11, 12, 20). Replace or remove each with
a real command, and add `tests/test_ci_references_lock.py`: it parses
`.github/workflows/ci.yml`, then asserts every `pytest` path exists, every
`python` script/module exists, and every `comp <command>` exists in
`comp --help-all`. Batch 0 also writes `scripts/run_ci_gates.sh` with
`set -e` in the corrected CI order; CI and the local release run that one
script. Error cost of not doing it: every release spends a session
rediscovering that CI is fiction.

**D2 — Format is a gate; lint and types are count ratchets.**
Format the 13 files once. Lint stays at the ruff ratchet; types get a new
pyright count ratchet (`BASELINE=3269`, `WARNINGS=525`), with both counts
lowered in every hygiene pass. The raw `ruff check .`/`pyright .` steps
become reported counts, not pass/fail, until the counts reach zero. This
is the only honest option that does not mix 3,900 legacy findings with a
release; the ratchet is a direction with a deadline, not a waiver.

**D3 — The eqprop kernel is reference-only on a composed relu cell.**
The tanh kernel cannot reproduce a relu geometry; the attach guard detaches
to the reference, and that is correct. Declare it in the acceleration
matrix and capability card, and lock the detach. Closing the gap needs one
activation contract for both rungs; that is a capability ticket, and its
runtime value is measured before it is scheduled (D9).

**D4 — Cache the attach parity probe per composed cell.**
The guard runs one forward + one kernel equilibrium per `evaluate_cell`;
the decision depends on the cell, not the seed. Cache it by
`(algorithm id, coordinate.cell_key(), geometry params)`. This is the
largest avoidable runtime cost the repair added. Verify with a call-count
lock: one probe per unique cell, never per seed.

**D5 — One Jacobian per cell is a permanent lock.**
The 3→1 change is a correctness-neutral runtime win. A count test must
fail if a second `_full_jacobian_tensor` returns per
`compute_stability_metrics`.

**D6 — Walltime is an outcome; counts and profiles are the ruler.**
This host runs other processes. cProfile call counts (Jacobians, probes,
cells, proposals) decide; a pytest duration is recorded, not compared.

**D7 — Test acceleration is measured, not guessed.**
The final property shard is profiled once after the size edits. Apply only
the top named cost:
- persistent `TORCHINDUCTOR_CACHE_DIR` in CI (the compiled settle graphs
  repeat across jobs);
- the claim fixture's 5-epoch regime lowered to the smallest epoch count
  that still clears the digits bar (a 3-point ladder, one seed each);
- `cell_config` composition profiled in the generated suite; cache a second
  composition only if the profile names it.
No test is weakened; the assertion stays, the box shrinks.

**D8 — Test-passing includes experiments, not only pytest.**
A release runs one real SEC cell and one campaign smoke:
`survey_cli` L0, one task, one seed, one axis; then `comp demo`. A record
must reach the store and a claim/limitation report must render. Breadth is
already PASS.

**D9 — Quantify the eqprop gap before scheduling the fix.**
Benchmark the eqprop kernel on its own case vs the composed-cell reference.
If the kernel is materially faster, closing D3 is a high-value capability
ticket; if not, the gap is a declaration, not a priority.

**D10 — One release command.**
`scripts/run_ci_gates.sh` runs the `ci.yml` order with `set -e`: static
first, then Python gates, then audit. CI and the local release call the
same script; a second order cannot drift.

## Verification rules

1. One run per unresolved question; a green gate is evidence, not a rerun.
2. Select by symbol; a `testpaths` shard is a round-close artifact.
3. A cached failure is not a verdict; collect with `--co` first.
4. Long runs use `nohup ... > logs/<name>.log 2>&1 &`, `-rf --tb=line`,
   and ≤2-minute polling. Never two pytest suites concurrently.
5. A long test gets a marker and a `KNOWN_LONG` row together.
6. Every number carries its ruler: cells/proposals/Jacobians for work,
   walltime only as an outcome.

## Work batches

| # | One command / block | Decides | Budget |
|---|---|---|---|
| 0 | format 13; fix stream async; fix/remove stale CI steps; add CI reference lock; write `scripts/run_ci_gates.sh`; record ruff/pyright counts | CI is runnable and its static baseline is recorded | <10 min |
| 1 | add the pyright ratchet + lower the ruff count; fix the pyright errors owned by the TODO106-touched modules (per-line ignore only where a fix is disproportionate) | static debt is measured and the touched modules are clean | one pass, then ratchet |
| 2 | parity-probe cache + Jacobian count lock + eqprop detach lock; targeted stability/cell/acceleration tests | runtime guard is cheap and locked | <15 min |
| 3 | `pytest tests/property tests/integration/test_gallery_lock.py::test_figure_lock -q -rf --tb=line -n 2 > logs/property_release.log` | one green property artifact; profile top cost | measured ×1 |
| 4 | `run_ci_gates.sh`: parity, primitives, algorithms, demo, presets, registry, composition, repro, version/drift | CI Python gates are green | measured ×1 each |
| 5 | `pytest tests/acceptance -q -rf --tb=line > logs/acceptance_release.log` | acceptance is green | measured ×1 |
| 6 | SEC smoke: one `survey_cli` cell + `comp demo`; profile the cell | experiments are ready; runtime top cost is named | measured ×1 |
| 7 | release: `run_ci_gates.sh`, `pip-audit`, `make -C rocq all`, docs check | the release is one green artifact | one pass |

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

Batch 6 SEC smoke (fill the axis list to one cell):

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
| D1 | 0 | 4 CI steps name missing files/commands | CI predates the archive/move | replace with real tests; add the CI reference lock | new lock |
| D2 | 0 | format fails on 13 files | legacy files predate ruff | format once | format check |
| D3 | 1 | `ruff check .` exits 1 at 640 | legacy findings | ratchet as the gate; lower the count in D2 hygiene | ratchet 2 passed |
| D4 | 1 | `pyright .` exits 1 at 3269/525 | legacy type debt | add a pyright count ratchet; fix the TODO106-touched modules | new ratchet |
| D5 | 1 | property shard not one artifact | last full run predates the size edits | Batch 3 once | log |
| D6 | 1 | demo gate partial | `test_demo_ntm_local` under two workers | serial run; record | demo gate |
| D7 | 2 | eqprop kernel never attaches on a composed cell | tanh vs relu; guard detaches | declare reference-only in the matrix/card; add the detach lock; measure the gap | parity + cell |
| D8 | 2 | parity probe costs one forward per cell | the decision is per cell, probe per seed | cache by cell key; count lock | new lock |
| D9 | 1 | a second Jacobian can return unnoticed | no count lock | `test_jacobian_call_count_lock` | new lock |
| D10 | 0 | `comp audit` missing | command was removed | replace with the real metadata test(s) or `comp test` | CI |
| D11 | 0 | `validate_composition.py` missing | moved to archive | replace with `tests/property/joint/test_composability.py` | CI |
| D12 | 0 | `test_vertical_slice_gate.py` missing | no such test | replace with `tests/integration/test_energy_invariants.py` + `tests/property/joint/test_lifecycle_locks.py` | CI |
| D13 | 0 | `make -C rocq all` fails at `Utils.vo` | version skew 90299 vs 90300; stale artifact | clean generated `.vo` and recompile under the pinned Rocq; if the toolchain is the cause, pin it in CI | `make -C rocq all` |
| D14 | 0 | `uv sync --dev` strips extras | CI predates AGENTS | `uv sync --dev --all-extras` | CI |
| D15 | 0 | acceptance is not in CI | workflow only lists the slice | add `pytest tests/acceptance -q` | CI |
| D16 | 0 | microbench step is `|| true` | it cannot fail | make the smoke fail on a broken import | CI |
| D17 | 0 | `docs/generated/` may be stale | gitignored artifact | `generate_docs.py --all --check` in release | check |

## Efficiency rules

- Fail fast: format, lint count, pyright count, then tests; a missing file
  is found before a 25-minute shard.
- One artifact per suite: the property shard once, the demo gate once, the
  acceptance suite once. Never rerun a green suite "to confirm".
- Workers: keep `-n 4` from `addopts`; never launch two suites concurrently.
- Cache: `TORCHINDUCTOR_CACHE_DIR` and `UV_LINK_MODE=copy` in CI; a build
  cache keyed by `uv.lock`.
- The release script is the only order; per-session command lists are
  forbidden.

## Closure criteria

- [ ] `run_ci_gates.sh` exits 0, and `tests/test_ci_references_lock.py`
      proves every CI path/command exists.
- [ ] Format green; ruff ratchet green and lowered; pyright ratchet exists
      and the TODO106-touched modules are at 0 errors.
- [ ] Property + figure lock is one green artifact.
- [ ] Parity, primitives, algorithms, Demo, presets, registry, composition,
      repro, version/drift, vertical-slice replacements, and matrix are
      green in one pass; `comp demo` and the one-cell SEC run write a
      record and a claim/limitation.
- [ ] Acceptance green; `pip-audit` clean; `make -C rocq all` green.
- [ ] The Jacobian, parity-probe, and detach locks are green.
- [ ] `generate_docs.py --all --check` green.
- [ ] The eqprop gap is declared in the matrix/card with a failing-today
      lock, and its runtime value is measured.

## Notes

- Commit per group (CI / static / perf / tests / docs), never one mega-commit;
  each group's lock is the evidence in its message. Nothing is pushed.
- A ratchet is a direction: every hygiene pass lowers both counts; a pass
  that only moves files without lowering a count is not a closure.
- `docs/figures/manifest.json` is written only by the demo gate.
- The one-cell SEC run is a readiness smoke, not a claim; the claim path is
  already locked by `test_claim_report_lock` and breadth is PASS.
- The eqprop gap is a capability ticket, not a release blocker: the guard
  already prevents a wrong measurement.
