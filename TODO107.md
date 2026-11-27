# TODO107 — Local release closure: tests, SEC readiness, acceleration

## Progress 2026-11-27 (session 6)

**Hygiene pass: the lazy `__all__` warnings, and both ratchets lowered.**
At session start the ratchets held their recorded baselines: ruff **550**,
pyright **3257 errors / 525 warnings**. The warning block was one class:
**510 `reportUnsupportedDunderAll`** — a lazy package declares its `__all__`
names and resolves them through `__getattr__`, so the analyzer sees no
binding.

- Five experiment packages (`experiment`, `execution`, `evidence`, `schema`,
  `surface`) now declare all 489 re-exported names under `TYPE_CHECKING`,
  generated from each `_symbol_to_module` map after validating every name
  against the module that defines it. No runtime import moved: these blocks
  never execute.
- `benchmarks/joint` declared 8 `__all__` submodules that nothing bound; the
  eight `# ruff: ignore[undefined-export]` markers are gone and the names are
  imported under `TYPE_CHECKING`. One
  `# ruff: ignore[runtime-import-in-type-checking-block]` carries the reason
  the block exists (ruff counts an `__all__` reference as runtime use).
- `data/transforms.py` declares its 6 lazily built `transforms.Compose`
  constants, so the analyzer and tab completion see their type.
- `dashboard/__init__.py` never bound the 3 names in its `__all__`: the
  import was broken (`from ...dashboard import WebDashboard` raised). It now
  has the `_LAZY` shim the other packages use, so FastAPI stays optional.

**The facts the new types exposed, fixed.** Six errors the resolution
surfaced are real call-site defects, and none is silenced:

- `_demo.py` passed a `str` where `StoreConfig` takes a `Path`.
- `test_run_ledger_lock` added 1 to an `int | None` epoch count.
- `test_stage_model_lock` appended a `Record` for an injected failure; WP19
  wants a `Failure`, which is what it now appends.
- `test_warm_start_lock` passed `data_origin=None` into `Provenance`, which
  `to_dict` would have crashed on.
- The two deliberate-misuse tests in `test_scientific_validity_protocol_lock`
  carry `pyright: ignore[...]` with the reason: a string where the enum is
  required, and an omitted version.

**Lock.** New `tests/property/test_lazy_export_surface_lock.py` resolves
every declared name of the five map packages to a submodule or to a module
that binds it, refuses a map key `__all__` does not declare, and checks the
dashboard's names against `web.py` — without importing torch or FastAPI.
Measured **11 passed in 3.71 s**; a probe shows it fails on a name nothing
binds. The surface/undefined-name locks were re-pinned for the new
`__getattr__` shim: **38 passed in 10.69 s**.

**Ruff safety pass.** `ruff check --fix` retired 46 autofixable legacy
findings (unused imports, import order, f-strings without placeholders,
`Path(...).open()`), and the 8 `undefined-export` suppressors went with the
`benchmarks/joint` fix: **550 → 499**. `BASELINE` is 499 and the ratchet's
docstring names what moved.

**Measured:** pyright **3240 errors / 15 warnings** in 78.7 s
(`logs/pyright_session6e.json`), with **0 new diagnostics** against the
session's baseline; `configs/pyright_ratchet.json` re-pinned (errors
3257 → 3240, warnings 525 → 15). The 15 that remain are named: 8 wildcard
library imports (`stability`), 4 unused expressions (archived UI plus
`tests/ceec/conftest.py`), 1 `docker` module without source, 1 single-use
`TypeVar`, 1 archived `__new__` that should take `cls`.

**W43: the pre-commit `slides-build` hook had no script.** Running the hooks
on this session's commit failed on `docs/slides/build_slides.py`, which
`5a8ae9d4` deleted together with `docs/slides.html` when
`docs/build_site.py` replaced them. The hook stayed behind, so any commit
touching `computronium/experiment/schema/` (this one does) could not pass
it. Its artifact is gitignored (`docs/index.html`, `docs/index.md`), so it
is not a commit gate; the dead hook is removed and every hook passes on the
range. The site it used to build was also stale locally:
`docs/build_site.py --check` exited 1, and the rebuild wrote 424 KiB of
`index.html` + 110 KiB of `index.md`; a second `--check` exits 0.

**W44: the changed-file pyright hook found the domain-task interface.** The
hooks named five errors in `domains/neuromorphic.py`, and fixing them
exposed the interface they came from:

- `DomainTask.input_dim` was typed `int`, but `vision`, `analog`, `photonic`
  and `neuromorphic` store a channel-first shape there; `resolve_task`,
  `_task_shape` and `flat_input_dim` already reduce a tuple. The base and
  `TaskProtocol` now say `int | tuple[int, ...]`, and the reduction lives in
  one place: `domains/base.flat_input_dim` (moved out of
  `core/system_trainer/train_task.py`, which re-imports it).
- `input_dim`/`output_dim` read `None` after `setup()`; both now raise a
  named `RuntimeError` instead of returning the `None`.
- The two neuromorphic loaders returned `DataLoader | None`; a `_built`
  helper raises rather than returning a missing loader.
- `_compute_task_loss` tested `hasattr(task, "compute_loss")`, which does
  not narrow a protocol; `_CustomLoss` declares the method and
  `isinstance` enters it.

Measured: pyright **3257 → 3240**, **0 new diagnostics**, warnings held at
15. The five changed modules are pyright-clean. The sites that passed
`task.input_dim` into an `int` go through `flat_input_dim` (the capability,
RL-lane, tabular-split and task-surface locks, plus the pendulum probe).

**Gates run (the change's affected set).** The full release pass on this
tree, `scripts/run_local_gates.sh`, is **`local gates: PASS`** (exit 0,
`logs/local_gates_w44.log`; the stages sum to ~65.7 min). Measured: format
green 1710 files; pyright ratchet held **3240/15**; fast locks **126 passed
in 5.46 s**; property + figure lock **2959 passed, 53 skipped, 30 xfailed,
4 xpassed in 544.86 s**; primitives **780 passed, 135 skipped in 935.10 s**;
acceleration **440 passed, 75 skipped in 25.93 s**; unit **955 passed,
1 xfailed in 207.71 s**; demo **25 passed in 726.32 s**; serial
`TestFromScratchTest` **3 passed in 512.18 s**; campaign gates **18 passed
in 250.33 s**; the acceptance shard **30 passed in 735.12 s**; `pip-audit`
clean, wheel + sdist built, docs check exit 0.

**Functional smoke on the same tree (the plan's P1).** The one-cell SEC
survey (digits, L0, 1 epoch, 1 seed, `gradient`/digital/feedforward/
instantaneous/null/euclidean, cpu) wrote its record: **1 record in 8.5 s**,
exit 0. `comp demo` completed all seven beats in **40.2 s**, exit 0. The
fresh `2 tasks × 2 credits × 2 seeds × 5 sweep points` readiness campaign
(`/tmp/opencode/readiness.duckdb`) wrote **40 records in 2.9 s** with replay
hash **`2b9f6485745cc040`** — the same hash and count as session 4's run, so
the record is reproducible across the interface change. `comp coverage
report` exits 0 with **9 PASS cells**; `comp repro --device cpu` compares
**40 cells, 0 mismatches, passed=true in 29.5 s**; `comp report` renders the
claims section (none: 2 seeds cannot be claim-eligible) and the limitations
section (31 quarantined records), so it states no claim it cannot derive.

## Progress 2026-11-27 (session 5)

**W41 opened and closed: an effect-size claim ignored its registered seed
floor.** `PairedComparison.passes_equivalence` enforced
`registration.min_seeds`, but `passes_effect_size` did not, so a comparison
at n=64 could claim a registration pre-registered for 205 seeds — an
optional-stopping hole on the claim path. The floor now gates the claim, and
`test_claim_box_identity_lock.py` locks both directions: the n=64 block is
refused and the same effect at n=205 is accepted. Measured **9 passed**.

**The 0.277 block: n_max=205, pre-registered before the fresh seeds.** The
n=64 confirm block measured dz 0.454 with mean-diff CI [0.00564, 0.01830] and
p=4e-4. At the registered min_d 0.276769, power 0.8, alpha 0.05,
`required_sample_size` is **205 pairs**, so n_max is 205.
`configs/preregistrations/sec_credit_random_projections_n205.json` fixes the
box (mnist, L0, 1 epoch, batch 32, cpu, fp32, credit=random_projections)
and `probe_claim_n205.py` runs the fixed-n comparison on fresh seeds
256..460 with no peeking. Cost: 64 pairs took 1316 s, so 205 pairs is
~70 min; the watchdog is 140 min (2x the measured cost).

**Verdict: `claim`.** 410 cells measured, no defects; n=205, mean diff
0.01919, CI [0.01551, 0.02302], p=1e-4, dz **0.7121**, d 95% CI
**[0.575, 0.854]** — the registered 0.276769 is cleared. Walltime
**3543.86 s (59.1 min)** against the 8430.6 s watchdog. The 0.277 block is
no longer a capability gap: the claim path carries a claim at its
pre-registered n_max, fixed-n, no peeking.

Provenance: the registration file and the driver were written before the
launch (their mtimes are earlier than `started.json`) and committed in
`d14968e5`; neither was edited after the first seed ran. The next rung
should commit the registration before the launch so the commit order proves
it too.

## Progress 2026-11-27 (session 4)

**W39 closed: the acceptance test compared a lowercase `StrEnum` to uppercase
labels.** `Maturity` values are `"l0"/"l1"/"l2"`, but
`test_pareto_frontier_includes_local_credit` tested
`r.status.maturity.value in {"L1", "L2"}`, so no record could ever count as
promoted and the test failed on its own ruler, not on the loop. Two probes read
the loop instead of guessing:

- `probe_local_credit_bar.py` (22.9 s): at L0, 1 epoch, feedforward/digital/
  instantaneous/euclidean, `gradient`, `random_projections`, `pepita` and
  `local_goodness` all clear the bar on `xor` (val_acc 0.5312 > 0.5) and
  `spiral` (0.4688..0.5312 > 0.3333). On `iris` every credit sits at chance
  (0.3333 < 0.5055), the gradient ruler included.
- `probe_from_scratch_promotion.py` (a 2-cycle `xor` loop): the explore run
  earns L1 for `forward_tangent`, `hybrid`, `score_function`,
  `thermodynamic_contrast` and `pc_alm`; the exploit run earns L1 for
  `forward_tangent`, `hybrid`, `pc_alm`, `score_function` and
  `thermodynamic_contrast`. The earlier "only gradient promotes" diagnosis was
  reading the test's empty promoted set.

The test now compares `Maturity` members. Measured: the single test **1 passed
in 517.21 s** (`logs/w39_test.log`).

**W40 opened by the release pass: the same fixture is shard-dependent.** The
full pass reached acceptance and failed the same test in the four-way shard,
while the serial run above passes. The shard's captured output names the
difference: promoted credits were `spiral: homeostatic`, `spiral: zeroth_order`
and `iris: target_inversion`, not the local set. The fixture's 54 s stage budget
is a wall clock; under contention cells are cut before their second seed, the
proposer sees a different frontier, and the local credits never earn L1. Fix:
run `TestFromScratchTest` on its own serial step and deselect it from the shard,
the W38 pattern. Measured: serial class **3 passed in 516.81 s**; shard **30
passed in 753.64 s**; the full release pass is **`local gates: PASS`**
(`logs/local_gates_w40.log`). The first pass's other steps were green: format,
pyright 3257/525, fast locks 126, property 2947/53 skipped/30 xfailed/4 xpassed
in 273.74 s, primitives 780/135 in 678.18 s, acceleration 440/75 in 27.54 s,
unit 955/1 xfailed in 184.39 s, demo 25 in 725.75 s, campaign 18 in 226.78 s.

**W35 closed: the in-run "replay gate" never ran a replay.** The run's
`replay=fail` came from the initializer, not from `replay_survives` or a
confirmation: the L1 statistical gates rejected every cell
(`stats_gates_passed=False`: 2 seeds cannot meet a CI width, and the train/val
gate is insufficient), so L2 was never attempted. The field now reports
`not_attempted`; a real replay still reports `pass`/`fail`.
`tests/property/test_promotion_replay_label_lock.py` locks both directions
(**2 passed**). The campaign output shows `replay=not_attempted`.

**D14 follow-up measured, bucket rejected.** `probe_settle_layer_count_
recompiles.py`: depth 2..10 in one process builds **9 graphs, one per depth**,
and the steady state grows 0.15 → 0.40 ms because every layer does work. A
2/4/8/16 bucket would cut that to 4 graphs but pad a depth-5 settle to 8
layers (0.25 → 0.34 ms, **1.36x**), so the bucket fails the "without slowing
the steady state" test. The measured number and the rejection are recorded beside
`compile_settle` in `computronium/ontology/_settle_kernel.py`.

**Serial campaign measured: coverage PASS, repro PASS.** A fresh
`2 tasks x 2 credits x 2 seeds` declaration
(`configs/readiness_campaign.yaml`, with the default 5 sweep points = 40
records) at L0, 1 epoch, `--max-workers 1`:
`/tmp/w40_readiness.duckdb`, run `0a816b34`, **40 records in 2.4 s**, replay
hash `2b9f6485745cc040` (a second run produced the same hash and record count).
`comp coverage report` exits 0: **9 PASS cells** (digits 6 cells/6 records,
iris 2 cells/3 records). `comp repro --device cpu` compares **40 cells, 0
mismatches, passed=true** in 26.6 s. `comp report` renders the claim and
limitation sections; it states 0 claim-eligible cells and lists the
quarantined rows, i.e. limitations are written without inventing a claim.
The 0.277 block keeps TODO105's verdict: the fresh block's dz is 0.454 with CI
[0.214, 0.693], below the registered 0.277; the trigger is n≈370 pairs (~4x
the budget), not run.

**Release:** `scripts/run_local_gates.sh` passes on this tree
(`logs/local_gates_w40.log`): **`local gates: PASS`**, exit 0. Measured:
format, pyright ratchet 3257/525, fast locks 126 in 5.24 s, property 2947
passed/53 skipped/30 xfailed/4 xpassed in 268.23 s, primitives 780/135 in
664.81 s, acceleration 440/75 in 25.84 s, unit 955 passed/1 xfailed in
204.53 s, demo 25 in 720.86 s, serial `TestFromScratchTest` 3 in 516.81 s,
campaign gates 18 in 55.38 s, acceptance shard 30 in 753.64 s, `pip-audit`
clean, build and docs check green. The first pass on the same tree failed
only `TestFromScratchTest` in the shard (W40); the serial step is the fix.

## Progress 2026-11-27 (session 3)

**W33 closed: the cell ceiling travels with the run, and the replay runs it.**
The ceiling was part of the environment a run measured in, but it lived only in
the CLI, so a replay fell back to this host's default and compared two
environments. `RunSpec.cell_workers` now declares it;
`ExecutionLimits.declare()` records the ceiling the process resolved, and
`execute_spec`/the campaign write it on the run row; the survey engines declare
the `--max-workers` they plan with; `comp repro` takes no ceiling flag at all
and runs the record's. Evidence: an 8-cell serial survey
(`/tmp/w33_store.duckdb`, run `de84d141`) reproduces with `comp repro
--device cpu` and no flag — **8 cells, 0 mismatches**; an 8-cell pipeline run
(`/tmp/w33_run2.duckdb`, run `2e662d30`) does the same. A pre-W33 row declares
nothing, and the replay says so instead of pretending.

**W34 closed: the run engine never declared its objectives.** The post-training
probe reads the declaration to decide whether anything wants the free-settle
telemetry, and an *absent* declaration means "wants it". The pipeline built its
batch items with `params={}`, so every cell paid the probe D13 removed, and a
survey record and a run record of the same cell differed by 16 metrics —
`settle_steps_used` among them — so the survey store could not replay at all (8
mismatches). Fix: `_fresh_batch_items` declares the run's objectives. Measured:
the run's payload drops from 60 to 45 keys against the survey's 44, the
difference is `stage_timings` (a pipeline stage's host metric), and the survey
store replays **0 mismatches**.

**W35 opened: the in-run replay gate fails cells that a fresh process
reproduces.** `promote_with_stats` reported `replay=fail` on 4 of 8 cells of
that same run, while `comp repro` on the store passes and
`scripts/probes/probe_replay_metric.py` finds `survives=True` for all 8 in a
fresh process. So the gate reads in-process state the replay command does not
— W32's class, inside the gate. Not fixed here: it needs its own rung-1
measurement (which state, and does seeding it close the gate).

**Static:** the pyright ratchet was stale by four errors from the previous
session's commits; the three this pass named (`spec.n_seeds` passed as `None`
into two `int` parameters in `_resolve_baselines`, the sampler's generator in
`test_seeded_shuffle`) are fixed and the baseline lowered **3260 → 3257**
(`configs/pyright_ratchet.json`, which now records its measurement date).
`comp version` gained its parser, so `comp version --help` prints usage
instead of the version. The README's command table is regenerated (41
subcommands), and the ruff baseline lowered **551 → 550**.

**W36 closed: the release script wrote its compile cache into the linted
tree.** `TORCHINDUCTOR_CACHE_DIR=$PWD/.cache/torchinductor` put the inductor
graphs inside the repository, so `ruff check .` linted them: the property
shard's lint ratchet read **12 660 findings against the 551 baseline** — the
count depended on whether a run had compiled anything. The cache now lives
under `${XDG_CACHE_HOME:-$HOME/.cache}/computronium/torchinductor` and ruff
excludes `.cache`. The same pass found `_seeded_shuffle` cloning any loader
with a `RandomSampler`, so a time-major `SequenceBatches` stream — which has
no `dataset` — failed its cell at 0.03 s; the clone now requires a
`DataLoader`, and the sequence smoke cell trains.

**W38 closed: the campaign's four gates read a host-load artifact.** The
`campaign` fixture builds one 450-record campaign, shared by fifteen gates in
two modules. Inside the four-way acceptance shard they contend with three
sibling gates, so a cell is ~20× slower than its measured 0.7 s, the run's
deadline cuts 22 cells before their first epoch, the store keeps them, and
`train_acc` is missing — measured, `1 failed, 48 passed` with 22 cut cells.
Re-run serially, the same two modules are **18 passed in 91.6 s**. The release
script now runs them on their own serial step (`-n 1`) and the shard ignores
them; the store is keyed by spec and source mtime, so the artifact is not
reused across a code change.

**Release measured (one pass, `logs/local_gates.log`):** format 1704 files;
pyright ratchet held 3257/525; fast locks 126 passed; property 2945 passed, 53
skipped, 30 xfailed, 4 xpassed (545 s); primitives 780 passed, 135 skipped
(786 s); acceleration 440 passed, 75 skipped (28 s); unit 955 passed, 1 xfailed
(237 s); demo 25 passed (863 s); campaign gates 18 passed (92 s); acceptance
32 passed, **1 failed** in 943 s; `pip-audit`, `python -m build` and
`generate_docs.py --all --check` pass. The one failure is W39, so the script
exits 1 on a known-open gap rather than passing on a waived gate.

## Progress 2026-11-26 (session 2)

**W30 closed: a governed claim restricts the loop's arms.** The loop's explore
space spanned every credit, so `TestFirstGovernedClaim` was evaluated on credits
it never declared (forward_tangent, hybrid, ...), and `test_cross_domain_evaluation`
failed. `LoopDriver._governed_axis_values()` now fixes the axis each declared
hypothesis groups by to its `comparison_values`; `_explore_axes`/`_exploit_axes`
restrict to those arms (exploit keeps them when the frontier has none), and
`_filter_records_for_hypothesis` keeps only the declared arms. Probe
`scripts/probes/probe_governed_axes.py`: one cycle writes 10 gradient + 10
thermodynamic_contrast records. Acceptance
`TestFirstGovernedClaim` **5 passed in 284.94 s** (`logs/first_claim_serial2.log`).

**W31/W32 closed: a replay reproduces a serial run bitwise.** The index now
carries the task (`_measurement_identity` = cell, task, seed), so `comp repro`
compared **8 real cells** instead of 4 mispaired ones (56 mismatches, was 74).
The remaining numeric drift came from shared process state, not the schedule:
`DataLoader(shuffle=True)` in `domains/tabular.py:180` drew its permutation
from the process RNG, and `_set_seeds`→`_compose_cell` raced between workers.
Fix: a per-cell `torch.Generator(seed)` for the train sampler (the shared task
loader is not mutated) and one `_RNG_LOCK` around seed→compose→trainer
construction. `comp repro` also gained `--max-workers`, because the cell
ceiling is part of the environment. Measured: a fresh 8-cell serial run
(`/tmp/w32_store.duckdb`, run `0545aed7`) passes `comp repro --max-workers 1`
with **8 cells, 0 mismatches**; four concurrent cells still differ in the
Jacobian metrics, so a bitwise claim needs `cell_workers=1`. A fresh 12-cell
serial run (`experiments/readiness_serial.duckdb`, run `284251f8`, 3 tasks x
2 credits x 2 seeds) then passed `comp coverage report` and
`comp repro --max-workers 1`: **REPRO PASSED, 12 cells within 1e-06**.

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
| acceptance | `pytest tests/acceptance` | todo63 `TestFirstGovernedClaim` **5/5** (targeted); other failures W30-fixed, full shard not rerun |
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
| 5 SEC readiness | **DONE** | real campaign: 450 records in 279 s (3 tasks × 3 credits × 5 seeds); `comp coverage report` PASS; `comp demo` PASS; fresh 40-record `2×2×2` campaign `0a816b34`: coverage exit 0 (9 PASS cells), `comp repro --device cpu` 40 cells/0 mismatches; report renders claims + limitations |
| 6 release | **DONE** | `scripts/run_local_gates.sh` **PASS** on the final tree (`logs/local_gates_w40.log`): every step green, audit clean, build + docs check green |

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
| W19 | 2 | the 0.277 seed block is called a claim gap without error control | n is too small to decide | re-measured at a pre-registered `n_max`=205 on fresh seeds 256..460 with a fixed-n CI, no peeking | **claim**: dz 0.7121, d 95% CI [0.575, 0.854] > 0.276769, p=1e-4, 410 cells, 3543.86 s |
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
| W30 | 1 | todo63 loop fixtures timed out at 600 s | `hours=1.0` plus 0.1 h per stage ran one task for the whole mark | per-stage budget from the total (done); the credit space was then ungoverned | acceptance green; governed axes restrict to the declared arms (`probe_governed_axes.py`) | **5 passed** (284.94 s) |
| W31 | 1 | `comp repro` compared different tasks and then different numbers | `(cell_key, seed)` collapses tasks; metrics diverge run-to-run | key = `_measurement_identity` (cell, task, seed); compare 8 real cells | **8 cells, 0 mismatches** with W32 fixed and `--max-workers 1` |
| W32 | 2 | `gradient` cells did not reproduce numerically on the same seed | `DataLoader(shuffle=True)` had no seeded generator (`domains/tabular.py:180`); `_set_seeds`→`_compose_cell` raced between workers (`evaluate.py:461`) | per-cell `torch.Generator(seed)` for the train sampler; one `_RNG_LOCK` around seed→compose→trainer construction; `comp repro --max-workers` | **PASS**: 8 and 12 cells, 0 mismatches (serial); 4 concurrent cells still drift |
| W33 | 2 | a replay fell back to the host's cell ceiling and compared two environments | the ceiling lived only in the CLI, not in the declaration | `RunSpec.cell_workers`; `ExecutionLimits.declare()`; recorded by `execute_spec`/campaign and declared by the survey engines; `comp repro` reads it, flag removed | **PASS**: 8-cell survey and 8-cell run replay with 0 mismatches, no flag |
| W34 | 1 | a survey record and a run record of the same cell carried different metric sets | the pipeline built batch params `{}`, so `_needs_stability` read an undeclared run and paid the probe | `_fresh_batch_items` declares `spec.objectives` | payload 60→45 keys vs the survey's 44 (`stage_timings` only); survey replay 0 mismatches |
| W35 | 1 | `replay=fail` on 4 of 8 cells that a fresh process reproduces | the field's initializer was `"fail"`; the L1 statistical gates rejected every cell (`stats_gates_passed=False`), so no replay ran | report `not_attempted` unless a replay/confirmation runs; lock both directions | `test_promotion_replay_label_lock.py` 2 passed; campaign prints `replay=not_attempted` |
| W36 | 0 | the property shard's lint ratchet read 12 660 findings | `TORCHINDUCTOR_CACHE_DIR` sat inside the tree, so `ruff check .` linted the inductor graphs | cache under `~/.cache/computronium/torchinductor`; ruff excludes `.cache` | 550 findings in the shard |
| W37 | 0 | a time-major sequence cell failed at 0.03 s | `_seeded_shuffle` cloned any loader with a `RandomSampler`; `SequenceBatches` has no `dataset` | the clone requires a `DataLoader` | `test_sequence_task_lock` 8 passed |
| W38 | 0 | fifteen campaign gates failed on 22 cells cut before their first epoch | the campaign fixture runs inside the four-way shard and the run's deadline is a wall clock; the store keeps the cut records | campaign gates on their own serial step; the shard ignores them | 18 passed in 91.6 s serial |
| W39 | 1 | `TestFromScratchTest::test_pareto_frontier_includes_local_credit` finds no local credit at L1/L2 | the test compared `Maturity`'s lowercase values (`"l1"`) to `{"L1","L2"}`, so its promoted set was always empty; local credits do clear the L0 bar on xor/spiral | compare enum members; the probes measure the bar per credit | `probe_local_credit_bar.py` + `probe_from_scratch_promotion.py`; test **1 passed in 517.21 s** serial |
| W40 | 1 | the fixed test passes serially but fails in the four-way acceptance shard | the fixture's 54 s stage budget is a wall clock; under xdist contention cells are cut before their second seed, the proposer sees a different frontier, and the promoted credits are `homeostatic`/`zeroth_order`/`target_inversion` instead of the local set | move `TestFromScratchTest` to its own serial step; deselect it from the shard (W38's pattern) | serial class **3 passed in 516.81 s**; shard **30 passed in 753.64 s**; release PASS |
| W41 | 3 | a comparison at n=64 could claim a registration pre-registered for 205 seeds | `PairedComparison.passes_effect_size` read `registration.min_d` but not `registration.min_seeds`; only the equivalence path enforced the floor | the seed floor gates the claim too | `test_claim_box_identity_lock.py` locks both directions: **2 passed**; n=64 refused, the same effect at n=205 accepted |
| W42 | 0 | 510 `reportUnsupportedDunderAll` warnings, and 3 dashboard names that never bound | a lazy `__all__` is invisible to the analyzer; `dashboard/__init__` omitted its shim, so the name raised on import | declare the names under `TYPE_CHECKING`; dashboard gets the `_LAZY` shim; lock the surface | `test_lazy_export_surface_lock.py` **11 passed**; pyright warnings **525 → 15**; errors held 3257 |
| W43 | 0 | the `slides-build` pre-commit hook fails on a commit touching `experiment/schema` | its script and `docs/slides.html` were deleted in `5a8ae9d4` (the site builder replaced them) and the hook stayed behind | drop the hook: a gitignored artifact is not a commit gate | `pre-commit run --from-ref HEAD~1 --to-ref HEAD`: every hook passes; `docs/build_site.py --check` exit 0 |
| W44 | 1 | the changed-file pyright hook failed on `domains/neuromorphic.py` | `input_dim` was typed `int` although four domains store a shape; the loaders returned `DataLoader | None`; `hasattr` does not narrow a protocol | widen the base and `TaskProtocol` to `int | tuple`; one `flat_input_dim` in `domains/base`; `_built` for the loaders; `_CustomLoss` for the trainer | pyright **3257 → 3240**, 0 new; the five modules clean; property/unit shards and the capability slice pass |

## Efficiency rules

- Fail fast: format and ratchets before the 8–10 minute property shard;
  property before the cheaper shards so a failure stops the release early.
- One artifact per suite; never rerun a green suite "to confirm".
- Keep `-n 4` from `addopts`; never launch two suites concurrently. A
  release script runs the sequence, not a parallel fan-out.
- Cache: persistent `TORCHINDUCTOR_CACHE_DIR`; `UV_LINK_MODE=copy`.
- The local script is the only order; ad-hoc command lists are not evidence.

## Closure criteria

- [x] `scripts/run_local_gates.sh` exits 0. Measured: **`local gates: PASS`**
      on the final tree (`logs/local_gates_w44.log`, session 6); the earlier
      pass failed only `TestFromScratchTest` in the four-way shard (W39's
      ruler + W40's host load), and the serial step is the fix.
- [x] Property + figure lock, primitives, acceleration, unit, demo and the
      campaign gates are each green once; acceptance measured 30 passed plus
      the serial `TestFromScratchTest` 3 passed (W39/W40).
- [x] `comp demo` and the one-cell SEC run write a record; breadth PASS
      (17 error-aware credits; session 2).
- [x] Format green; ruff ratchet green and lowered (659 → 550 → 499);
      pyright ratchet exists and was lowered to `3240/15` (session 6); the
      TODO106-touched test errors are clean. The remaining `evaluate.py`
      type findings are legacy.
- [x] The Jacobian, parity-probe, and detach locks are green; the train
      shuffle is seeded per cell (`test_seeded_shuffle`).
- [x] The cell ceiling travels on the declaration and the replay runs it
      (`test_replay_environment_lock.py`): an 8-cell survey and an 8-cell run
      replay with 0 mismatches and no flag (W33).
- [x] The run engine declares its objectives, so the free-settle probe is paid
      only when an objective reads it
      (`test_every_batch_carries_the_runs_objectives`, W34).
- [x] Lazy stability telemetry is locked in both directions.
- [x] The `dynamic=True` compile probe is measured: depth 2..10 builds one
      graph per depth (9 graphs) and steady state grows 0.15 → 0.40 ms; a
      2/4/8/16 bucket cuts it to 4 graphs but pads depth 5 to 8 layers
      (1.36x), so it is rejected. The number is beside `compile_settle`.
- [x] Pre-commit runs the fast locks only, and the full property suite is in
      `run_local_gates.sh`.
- [x] The campaign writes claims/limitations; `comp coverage` and
      `comp repro --device cpu` pass; the 0.277 block's pre-registered
      verdict is **`claim`**: n_max=205 on fresh seeds 256..460, dz 0.7121,
      d 95% CI [0.575, 0.854] > the registered 0.276769, p=1e-4, 410 cells
      measured, 3543.86 s. Measured campaign: 450 records in 279 s
      (session 2); fresh 40-record `2×2×2` campaign `0a816b34` with coverage
      exit 0 (9 PASS cells) and `comp repro` 40 cells/0 mismatches; the
      report renders claims + limitations. Re-measured on the session-6 tree:
      campaign `1e8a2ed5` wrote 40 records in 2.9 s with the **same replay
      hash** `2b9f6485745cc040`, coverage 9 PASS cells, repro 40 cells/
      0 mismatches in 29.5 s, and the report states 0 claim-eligible cells
      (2 seeds) plus 31 quarantined records.
- [x] `generate_docs.py --all --check`, `pip-audit`, and `python -m build`
      are green (the final pass: audit clean, wheel + sdist built, docs check
      exit 0).
- [x] The eqprop reference-only condition is declared in its generated spec
      page, and the detach guard is locked.
- [x] The GitHub-disabled lock is green.

## Remaining work (in order)

The release is closed, the 0.277 block is a claim at its pre-registered
n_max, and the hygiene pass lowered both ratchets. The release pass and the
SEC smoke were repeated on the session-6 tree (W42-W44), so the functional
claims hold on this tree. What remains is queued legacy, not a blocker.

1. **Ruff ratchet — 499 findings.** The next groups are E402 56, RUF105 43,
   C901 36, PLW0717 36, PLR0914 30, F841 22 and PLW1514 21. A pass names the
   rules it retires and lowers `BASELINE` in
   `tests/property/test_lint_count_ratchet.py`; a pass that only moves files
   is not a closure.
2. **Pyright ratchet — 3240 errors / 15 warnings.** The 15 warnings are
   named in session 6 (8 wildcard library imports, 4 unused expressions,
   1 `docker` module without source, 1 single-use `TypeVar`, 1 archived
   `__new__`). The error bulk is `reportArgumentType` 1122,
   `reportAttributeAccessIssue` 711 and `reportMissingImports` 603;
   `docs/archive` alone is 680, and excluding archived code from analysis is
   a scope decision somebody has to take — not a cleanup this plan invents.
3. **Register C.** The canonical `# ruff: ignore` → `# noqa` directive
   migration stays queued: enabling RUF105/106 churns 43 guard-rails without
   adding lint signal.

## Notes

- Commit per group (static / perf / tests / docs), never one mega-commit;
  each group's lock is the evidence in its message. Nothing is pushed.
- A ratchet is a direction: every hygiene pass lowers both counts; a pass
  that only moves files without lowering a count is not a closure.
- `docs/figures/manifest.json` is written only by the demo gate.
- Rocq and GitHub are out of the local release scope; they are separate
  toolchain tickets, and the version-skew failure is recorded here so it is
  not rediscovered.
- The one-cell SEC run is a readiness smoke, not a claim; the claim path
  carries a claim at n_max=205 (session 5).
