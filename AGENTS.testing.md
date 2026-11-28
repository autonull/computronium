# Testing methodology

This is the single source for testing in this repository: the tiers, the
binding rules (moved out of `AGENTS.md`), the per-commit and round-close
duties, the coverage ratchet, the test-writing rules, and the primitive
testing requirements. `AGENTS.md` carries one reference to this file.

**Rules and procedures live here; numbers do not.** A value that changes per
run — a duration, a coverage percentage, a statement count — goes stale the
moment it is written in an instruction. Measurements belong in the plan (with
their date), in a run's log, or in a config that a check reads
(`configs/coverage_ratchet.json`). Where a rule needs a number, it names the
file that holds it.

Not every rule that mentions a test is a testing rule. The CI gate order, the
dev-env smoke, the SEC validation methodology and the testability design
principle stay in `AGENTS.md`: they are environment, CI, experiment or
architecture policy, and moving them would scatter unrelated rules.

## The four tiers

Run the cheapest tier that can decide the question.

| Tier | Command | Question | Where its number lives |
|---|---|---|---|
| affected | `scripts/run_affected_tests.sh` | Did my change break its own contracts? | the run's log |
| fast | `scripts/run_fast_gates.sh` | Is the machine still coherent? | the run's log; the coverage share in the plan |
| release | `scripts/run_local_gates.sh` | May this tree be released? | the run's log |
| coverage | `COVERAGE=1 scripts/run_local_gates.sh` | Did coverage fall? | `configs/coverage_ratchet.json` |

- **Affected** maps a change to the test files that import the changed module
  or its parent package, then bounds the run by the fast suite's own prices; a
  reached file outside that list is a long learnability test, named and left
  to the next tier. `--rev <rev>` selects a commit instead of the working tree.
- **Fast** is `configs/fast_suite.txt`, chosen from per-test coverage and
  durations by greedy new-lines-per-second. It is a measurement, not a rule:
  regenerate it with `scripts/probes/probe_fast_suite.py` when the population
  moves, and a file that has been renamed is dropped with a warning rather
  than failing the gate.
- **Release** is the only gate that answers "may this be released".
- **Coverage** adds the flags to the release's own pytest calls, so there is
  one population and the suites cannot drift from the one the ratchet is
  defined over.

## Invocation

*   **Test invocation**: always `uv run python -m pytest` — never bare `pytest`
    (user-site pytest shadowing breaks collection on protobuf gencode skew).

## Rules (binding)

*   **pytest + pytest-cov**: Coverage is opt-in; it is measured by
  `COVERAGE=1 scripts/run_local_gates.sh` and held by the ratchet in
  `configs/coverage_ratchet.json`.
*   **Test execution tiers** — run the cheapest tier that can catch your
  change; the four tiers and their measured costs are the table above.
  Always show output + walltime (never truncate failures).
*   **Never `pytest tests/`.** It bypasses `testpaths` and pulls in every demo;
  two attempts hard-killed at test 873/3699 with no traceback (TODO45 §12.1).
*   **`-n 4` is already in `addopts`**; do not add `-n` by hand, and do not
  override it downward for small selections without reason: worker startup is
  not free, and it can exceed a small shard's whole runtime.
*   **Demos are artifact producers, not checks.** The `demo` marker is stamped in
  `tests/conftest.py` by filename; `pytest -m demo` is the only way to run them.
*   **Select tests by symbol, not by directory.** `grep -rn <symbol> tests/
  --include=*.py`, then run the 2-4 files it names. A whole `testpaths`
  directory is a round-close artifact, never a feature gate: it costs ~5x, is
  the only tier that gets hard-killed, and its cost is quoted stale.
*   **A run that may be interrupted writes `-rf --tb=line` to a log.** pytest
  writes its summary at session end, so a hard kill takes the run's only
  artifact — and recovering it means re-running it.
*   **A killed run yields no verdict: collect, do not re-run.**
  `pytest <dir> --co -q > ids.txt` runs no test body and locates a failure
  from the progress line. **Never `--lf`/`--ff` here**:
  `.pytest_cache/v/cache/lastfailed` holds 520 entries, most with node ids that
  no longer collect.
*   **A lock's fixture must contain the case the lock exists for.** If removing
  the mechanism cannot fail the fixture, the lock is a comment (TODO46 D25).
*   **One shard run per round close, never per commit** — and never a re-run of
  a shard already green "to confirm".
*   **hypothesis**: Use for property-based tests on pure logic.
*   **Mocking**: Prefer Dependency Injection over `unittest.mock`. Use `pytest-mock` when strictly required.
*   **Fixtures**: Use fixtures over setup/teardown; `@pytest.mark.parametrize` over duplicated tests.

## Coverage

- **Working functionality outranks coverage and cosmetic lint.** The ratchet
  exists to stop a regression, not as a score to maximise for its own sake; a
  test that only raises the number buys nothing.
- **Measure behavioral coverage, not collection.** A line executed by a test
  is evidence; a line executed only by importing its module is the cost of
  collecting it. The report does not separate the two — read the split from
  the coverage store's contexts (`--cov-context=test`), which is also what the
  fast-suite selection uses.
- **The ratchet is a floor, and the floor lives in
  `configs/coverage_ratchet.json`.** `COVERAGE=1 scripts/run_local_gates.sh`
  measures the release population and `scripts/check_coverage_ratchet.py`
  holds it: covered statements may not fall; a rise beyond the slack
  re-baselines in the same commit that covered more; a fall names the files
  that lost the most lines.
- **Coverage is measured on the release's own population.** The flags go on
  the release script's pytest calls, so there is no second test list to drift
  from the one the floor is defined over.
- **Where it lacks is a plan artifact.** The measured map — which area misses
  how much — is recorded in the plan with its date and regenerated by a
  coverage run. A rule here says how to measure, not what today's number is.

## Brittleness — the test-writing rule

A test asserts a **contract**, never a copied measurement.

- A contract is an invariant, a round-trip, an identity, a refusal by name, a
  monotone ordering. A copied measurement is a param count, an exact walltime,
  or today's population size.
- A number is legitimate only when the number **is** the policy (a declared
  budget or ceiling) or a **provenance record** (a figure's run record).
- A population lock keeps a named list, fails loudly when the population moves,
  and is reviewed; it is never auto-derived from today's tree. A selector or
  test list tolerates a moved file instead of failing a commit.
- A test that fails because a file moved, a module was renamed, or the host was
  busier is a defect in the test, not a signal about the code.

## Time

- **The wall is the long pole.** One slow test sets a shard's wall whatever
  the worker count: measure with `--durations` before tuning anything.
- **Trim a long test's budget** to the smallest its assertion needs; the test
  must still fail when the claim it guards is broken.
- **Worker and thread counts are not the lever** until the long pole is
  trimmed. A higher `-n` on one device adds contention and wasted CPU, and
  pinning torch threads can be slower than letting torch use them.
- `-n 4` stays in `addopts`; an override downward needs a reason (worker
  startup costs more than some shards' whole runtime).
- **Collection is a real cost**: every test file pays for its module-scope
  imports, and every tier pays it. A new heavy import at module scope in a
  test is a tax on the whole suite.
- A test that needs more than about ten seconds declares why and lives outside
  the fast tier; a typical assertion is under a second.

## Flakiness and contention

- **A flaky test is a defect, not noise.** Reproduce it (N runs), find the
  ordering bug, fix the ordering; never retry-mask it.
- A test that passes alone and fails inside a shard is a host-load artifact:
  name it and run it on its own serial step (the W38/W40 pattern), never
  weaken its assertion.
- **One GPU is a shared ruler.** A memory-heavy subset runs with fewer
  workers than the release; workers that overflow the device show up as test
  failures that are really an OOM. A CUDA context that already holds memory at
  suite start is foreign — a killed run's leftover, or another user: the
  suites warn, and the owner frees it.
- A fixture that builds a shared artifact is session-scoped and keyed by spec
  and source mtime.
- A causal claim about a flake names the mechanism and a failing test; "it is
  just flaky" is not a triage.

## Skips and xfails

- A **skip** needs a reason: an environment refusal (no CUDA) or a
  declared-infeasible cell. An empty population is a defect: build the
  population the way a run does, or delete the test. A skip that would run
  nothing is not coverage.
- An **xfail** names its blocker, the fix, and the verify. The pass that fixes
  the cause removes the marker in the same change, so a regression fails and a
  stale xpass cannot appear silently.
- A non-strict xfail that passes is a stale marker, not a pass.

## Adding a test

1. Pick the tier; the test must answer the question that tier asks.
2. Assert the contract, not the measurement (above).
3. Keep it under ~1 s; if it needs more, say why and put it outside the fast
   tier.
4. One family per primitive is a unit gate; the family matrix belongs to SEC
   (`AGENTS.experimenting.md`), not to the fast suite.
5. A demo's figures and manifest are its deliverable, not coverage; a
   capability test certifies a floor. Neither is a coverage test.
6. Prefer a fixture over setup/teardown, and `parametrize` over a copied test.

## Duties

The pre-commit hook runs no test suite: the tiers below are the agent's
duty, not the hook's.

**Per commit** (scoped and fast): the affected tier
(`scripts/run_affected_tests.sh`); `ruff format` and `ruff check --fix` on the
changed files; `pyright` on the changed files (strict for new modules); the
dev-env smoke from `AGENTS.md`'s Environment section.

**Round close** (never per commit): the release pass
(`scripts/run_local_gates.sh`) once, `COVERAGE=1` for the ratchet, and the
repo-wide ruff/pyright hygiene pass.

## Evidence

- Report the command, the walltime and the result; never truncate failures.
- A commit message carries the tier's measured result, and the log it came
  from.
- A number travels with its ruler: the n, the device, the fidelity, and the
  metric's resolution.

## Primitive testing requirements

**Every primitive must have passing unit tests before SEC optimization runs.**

### 1. Minimum Capability Tests (Rung 0–1)
- **One-step wiring (Rung 0)**: `compute_pseudo_gradient` produces finite, non-zero gradients for error-aware credits; `settle` converges for non-instantaneous dynamics
- **1 epoch / 1 seed on minimum viable task (Rung 1)**: above chance (error-aware) or non-zero update (error-blind)
- **Fast task selection**: `digits` (1797×64) before `mnist` (70000×784), `iris` (150×4) before larger tabular, `cora` for graph, `cartpole` for RL
- **Run time target**: ≤30 seconds per primitive at minimum config

### 2. Error-Blind vs Error-Aware Criteria
| Credit Type | Pass Criterion | Examples |
|---|---|---|
| Error-aware (reads label) | `val_acc > bar` (task's primary pass bar) | `gradient`, `target_inversion`, `pc_alm`, `random_projections` |
| Error-blind (no label) | Non-zero parameter update, finite loss | `homeostatic`, `temporal_trace` |

### 3. No "Capability Gaps" Without a Failing Test
- If a primitive doesn't train, it's a **defect** (fixable) until proven otherwise
- A "gap" requires a NEW primitive/feature that doesn't exist yet
- Document defects with a test that **fails today, passes when fixed**
- NEVER skip a test with "gap" — fix the primitive or file the defect with test

### 4. Per-Axis Contract Tests (Already in `tests/primitives/`)
- `test_primitive_contract.py`: case determinism, seed variation, device placement, reference follows seed
- `test_<axis>_contract.py`: axis-specific output contracts (pseudo-gradient count/shape, settle convergence, etc.)
- `test_primitive_capability.py`: end-to-end 1-epoch capability on declared families

### 5. SEC Only Runs After Rungs 0–2 Pass
- **No SEC screen on a primitive that hasn't cleared its unit tests**
- SEC = Rungs 2–4 (ladder, paired CI, competitiveness)
- Unit tests = Rungs 0–1 (wiring, 1-epoch viability)
- A primitive with no unit test coverage is "not wired" — SEC refuses it

### 6. Task Family Coverage
- Test at least **one declared family** per primitive in CI
- Full family matrix runs in SEC (S5 Screens), not unit tests
- Refused families (per `task_families` declaration) are skipped with reason

### 7. The Test Is The Ultimate Authority
- If a test fails, the primitive is broken — period
- "It works in literature" is not a defense; the test reveals the defect
- Fix the code until the test passes; never weaken the test
- Every "gap" claimed without a failing test is an assumption, not evidence
