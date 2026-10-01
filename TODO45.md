# TODO45.md — Usability First: Removals, Critical Path, Then Refinement

**Follows:** TODO44 (core gates green; Register C hygiene remain)
**Binding:** AGENTS.md in full
**Supersedes:** the Phase A–G sequencing of the previous TODO45 draft.

**Goal:** A system an external researcher can install and use — one command produces
reproducible evidence. Type hygiene is explicitly *not* on the critical path: the 1095
pyright errors live in modules that have never blocked kernel work, and they block a
downstream consumer's LSP only. Fixing them before the product works is refinement
before substance.

---

## 0. Re-sequencing rationale (why this order changed)

The previous draft ran **type hygiene (A) → flakes (B) → CLI (C) → benchmarks (D) →
evidence (E) → docs (F) → release (G)**. Three findings from the first working session
invalidate that order:

1. **The error count wildly overstates the work.** Measured: `kernels.py` produces 90
   errors from **7** annotations of `xp: object`. `rule_state.py` produces 56 errors
   from **1** field annotation. 150 errors across 18 files are one `object`→scalar
   coercion pattern. Phase A as written ("8 files, ~200 errors, new shared helpers")
   was ~10 edits of real work buried in a week of per-line churn.

2. **A1's prescribed helpers already exist, under different names.**
   `acceleration/eqprop_kernel_backend.py:27` already defines an `_ArrayNamespace`
   Protocol and local `_num`/`_flag` helpers. An attempt to recreate them in a new
   `acceleration/_typing.py` produced a conflicting second definition with a different
   signature and **zero importers**; it was deleted unreviewed-in. numpy ships
   `py.typed`, so a hand-rolled 150-line protocol duplicating the numpy surface was the
   wrong tool regardless. A1's premise — that `constexpr` parameters can be coerced by a
   helper — does not survive contact with pyright.

3. **Deletion and ground-truth are cheaper than any refinement, and they shrink
   everything after them.** Deleting dead files cannot break the critical path once
   you've checked nothing references them. Guessing at a failure list from a stale
   snapshot can.

**New order:** ground truth → removals → critical path → honesty/docs → type hygiene.

| # | Phase | Why here |
|---|-------|----------|
| 0 | Ground truth | Cannot plan against an unverified snapshot; Phase B was written from a stale one |
| 1 | Removals | Cheap, safe, shrinks every later phase's surface |
| 2 | Critical path | The one capability that makes the repo worth anything |
| 3 | Honesty & docs | Depends on Phase 2 actually producing evidence |
| 4 | Flakes on the critical path only | Vision fixture vendoring is only worth it if vision is *used* |
| 5 | Type hygiene | Blocks nothing; do it root-cause-first with the measured table |
| 6 | Release | Last, and only over a green critical path |

---

## 1. Definition of "Done"

```
computronium/
├── ontology/ core/ algorithms/ models/ nn/ state/ training/     # 6-axis library
├── acceleration/ verification.py visualization/ stability/ domains/
├── experiment/                                                   # Unified Kernel
├── cli/                                                          # Thin `comp` adapters
└── scripts/demos/
packages/     ceec-core psi-peft local-feedback stability computronium-lab
tests/        property/ acceptance/ integration/ unit/ primitives/ algorithms/
docs/         curated reference + generated (manifest locked)   # no archive/
```

**Non-negotiables, in priority order:**

1. **One command works.** `comp run` takes a question or a spec, writes a record, and
   `comp report --run-id` renders claim/evidence/limitation from it.
2. **Zero flaky tests** on a clean `uv run python -m pytest`.
3. **Every README claim is runnable** and matches a locked test.
4. **Benchmark verdicts honest** — no smoke numbers presented as full-rigor.
5. ~~Type-clean~~ — *deferred to Phase 5; explicitly not a release blocker.*

---

## Phase 0 — Ground Truth (do first; everything else depends on it)

- [ ] **G0.1** Full suite on a clean tree; record the *actual* pass/fail/skip counts.
      The appendix figure (3539/10/108) predates the `tests/slow/` and `tests/graph/`
      removals and is known stale.
- [ ] **G0.2** Per-test walltime for the 20 slowest; feeds Phase 4's flake triage.
- [ ] **G0.3** Reconcile the CLI inventory. The draft claimed 7 surviving commands
      (including `gallery`); the dispatcher registers **6** and `comp --help` is a bare
      usage string (`comp <report|parity|repro|validate|joint-validate|benchmark>`) that
      exits 1 on a bare invocation. Decide: real argparse help tree, or document as-is.
- [ ] **G0.4** Confirm the demo/manifest invariant still holds (measured: 21 `DEMOS`,
      21 `docs/figures/manifest.json` figures — currently satisfied).

**Gate:** a committed snapshot table of real numbers, replacing §11.

---

## Phase 1 — Removals (before any feature work)

Deletion first: it cannot regress the critical path once references are checked, and it
reduces the surface every later phase touches.

- [ ] **R1.1** `tests/slow/` — superseded by kernel demos/benchmarks. **Already deleted**
      in the working tree; `tests/test_timeout_marker_policy.py` `KNOWN_LONG` updated
      to match. Needs a test run to confirm the timeout-marker lock still passes.
- [ ] **R1.2** `tests/graph/` — deleted in the working tree. Confirm no suite depends on
      the graph geometry it covered; if one does, that is a real coverage gap to record,
      not a reason to restore the directory.
- [ ] **R1.3** `docs/archive/` — 467 files, 8.7 MB. Git history is the archive. Requires
      touching `pyproject.toml:222` (ruff `exclude`) and `README.md:361` (research-program
      paragraph that points at it).
- [ ] **R1.4** Exclude generated protobuf from pyright. 61 errors sit in `p2p/`, of which
      35 are in generated `p2p/proto/tile_mesh_pb2_grpc.py`. Hand-fixing generated output
      is waste; add to pyright `exclude` alongside the existing `*_pb2*.py` ruff excludes.
- [ ] **R1.5** Revert formatting-only churn in `docs/figures/run_records/*.json` (16 files
      were re-serialized compactly — byte-different, value-identical). Left uncommitted by
      a prior session; it inflates diffs and risks the manifest drift lock.
- [ ] **R1.6** Delete any subsystem that G0 shows is untested *and* unreferenced.

**Gate:** tree is smaller, `ruff`/`pyright`/`pytest` all still resolve, no dangling refs.

---

## Phase 2 — Critical Path: `comp run` end-to-end

One capability, done properly, beats twelve half-wired ones. Scope deliberately narrow:
**`--spec-file` only.** Natural-language composition is a later, optional extra.

- [ ] **C1.1** `comp run --spec-file spec.yaml` — RunSpec → `SearchSpace` →
      `ProposalPolicy` → `PipelineRunner` (S1–S11) → `RecordStore` → Claims. Reuse the
      existing kernel surface; this is a thin adapter, not new machinery.
- [ ] **C1.2** `--policy synthesis|stratified_random|uniform_random|round_robin_grid` —
      the four that need no surrogate. `model_based` (TPE/NSGA-II) and `evolution` are
      deferred until the path is proven.
- [ ] **C1.3** `--rounds N` with `--run-id` pause/resume, single-writer `RecordStore`
      append, atomic writes. (U3 is already locked in
      `tests/acceptance/test_unified_kernel.py`; this exposes it, not reimplements it.)
- [ ] **C1.4** `comp report --run-id <id>` renders Claim/Evidence/Limitation for any run.
- [ ] **C1.5** Ship one worked example (`examples/eqprop-vs-backprop-mnist.yaml`) whose
      output is asserted by a test, so the README can point at a runnable artifact.

**Deliberately deferred from the old Phase C:** `comp search` (C2), `comp export` (C4),
`comp status` (C5), `comp migrate` (C6), and the 12-command gate. These are conveniences
over a store that must first exist and be correct. `comp report` already exposes
run/report/export/conformance/status as subcommands — check whether C4/C5 are *already
satisfied* through it before writing new adapters.

**Gate:** a new user runs the example and gets a record + claim. Nothing else matters yet.

---

## Phase 3 — Honesty, Docs, Demos

- [ ] **H3.1** Benchmark results manifest (`benchmark_results/manifest.json`) with git
      SHA, date, hardware, seeds, verdicts, effect sizes, 95% CIs, walltime. README links
      the latest.
- [ ] **H3.2** `z3_fixed_weights` epoch threshold: run 10→20→50→100, document the
      PASS/FAIL transition, set `--epochs` to the first PASS value.
- [ ] **H3.3** Nightly full-rigor CI (`benchmark-full.yml`), pinned runner, artifacts
      uploaded. (No `--quick`.)
- [ ] **H3.4** README code blocks locked to tests via the existing `<!-- lock: name -->`
      mechanism; each block asserts the numbers it prints.
- [ ] **H3.5** `scripts/demos/` — each has a docstring (purpose, expected numbers), prints
      results, exits 0. Re-pin `docs/figures/manifest.json` only when a demo is added.
- [ ] **H3.6** Delete `RELEASE_NOTES_v3.0.0.md` into the archive-free convention; write
      v3.1 notes last.

**Gate:** every README number traces to a locked test or a manifest entry.

---

## Phase 4 — Flakes (critical path only)

Scope this phase by G0.2, not by assumption.

- [ ] **F4.1** Triage G0 failures into *critical-path* vs *peripheral*. Only the former
      block the release.
- [ ] **F4.2** Vision smoke fixtures — vendor 10 samples/task under
      `tests/fixtures/vision/`, no network — **only if** vision is on the critical path
      or a peripheral failure is otherwise unexplainable.
- [ ] **F4.3** Local-feedback parity: bisect projection math vs seed variance; fix the
      math or justify a tightened `atol` in the test docstring.
- [ ] **F4.4** Every `xfail` carries `# issue: <url>`. No silent skips.

**Gate:** `uv run python -m pytest tests/ -q` → 0 failures, 0 errors, 0 unexpected xpasses.

---

## Phase 5 — Type Hygiene (deferred; root-cause-first)

Do **not** work file-by-file. Work the table below in ratio order. Each row is a
*root cause*, not a file.

| # | Root cause | Errors | Fix | Files |
|---|-----------|--------|-----|-------|
| A1 | `get_backend() -> object`; 7× `xp: object` | **71** | annotate as a namespace Protocol | `acceleration/kernels.py` (90 total) |
| A2 | `object` → typed params in deploy model ctors | **187** | one `DeployableModel` Protocol + typed `__init__` | `models/deployments/{rl,vision,timeseries,graph}.py` |
| A3 | `object` → `int`/`float`/`bool`/`str` coercion | **150** | **one shared coercion-helper family**, then call sites | 18 files; 97 `extra.get()` sites |
| A4 | `z.activity` union `list[Tensor] \| float \| dict[str,float]` | **45** | one field annotation | `core/plasticity/rule_state.py` (56 total) |
| A5 | `System` vs `nn.Module` in trainer signatures | **~50** | `TrainableModel` protocol | `core/continual/system.py`, `validation/tracks/*` |
| A6 | `set_model_ref` override arity (Liskov) | **~25** | one kernel-side binding contract | `contrastive_kernels.py`, `fa_/tp_/backprop_kernels.py` |
| A7 | `list[LinearView]` vs `list[Linear]` invariance | **~10** | `Sequence` (covariant) | `kernel_backend.py` + callers |
| A8 | Triton `constexpr` vs `Literal` | ~30 | **scoped suppression, once, documented** | `*_kernels.py` |

**Rules for this phase (learned the hard way):**

- **Extract, don't reinvent.** `eqprop_kernel_backend.py` already has `_ArrayNamespace`
  and `_num`/`_flag`. Move them to one shared module; do not write a second copy with a
  different signature.
- **numpy ships `py.typed`.** Prefer its types over a hand-rolled protocol.
- **A coercion helper must be *typed*, not `float(x)`.** `float(object)` fails pyright
  with `ConvertibleToFloat` — it relocates the error, it does not fix it. A real helper
  narrows via `isinstance`.
- **`tl.constexpr` cannot be coerced.** `Literal[32]` → `constexpr` is inherent to
  `@triton.jit`. Suppress it in one deliberate, commented decision per file — do not
  hand-place `# pyright: ignore` at 12 call sites and call it a fix.
- **Verify per root cause**, not per file: `uv run pyright <the one file>` and confirm
  the row's error count actually dropped before moving on.

**Gate:** `uv run pyright computronium/` → 0 errors. Expected ~8 commits, not ~20.

---

## Phase 6 — Release

- [ ] **V6.1** `Dockerfile.dev` → `uv sync --dev --all-extras` → `pytest` → `comp run` smoke.
- [ ] **V6.2** `pip-audit` clean.
- [ ] **V6.3** Version bump to `3.1.0`; release notes.
- [ ] **V6.4** Tag, publish wheel + GHCR image.

---

## 9. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Ground truth (G0) reveals a much larger failure set than the stale 10 | That is the point of doing it first; re-scope Phase 4 from measured walltime |
| `comp run` expands into a re-implementation of the kernel | U1–U5 are already locked; C1 is an adapter. If it needs new pipeline stages, stop and re-plan |
| Type hygiene reorders itself under refactors | Anchored to the root-cause table, not to file lists |
| Generated-code exclusions hide real errors in hand-written `p2p/` | Exclude only `*_pb2*.py`; `grpc_service.py` stays checked |
| Benchmark walltimes vary by hardware | Pin CI runner; publish hardware + seeds + SHA in the manifest |

---

## 10. What Comes After (TODO46+)

| Area | Next Step |
|------|-----------|
| Natural-language entry | `comp run --question` via an `llm_composer` extra, over the C1 spec path |
| Scalability | Distributed `PipelineRunner` (Ray/Dask) for >100 parallel proposals |
| Extensibility | Plugin system for custom axes/policies/objectives (entry points) |
| Governance | CEEC claim registry with cryptographic signing; audit trail |
| Publication | `comp publish --run-id` → auto-generate paper draft |

---

## 11. Session Log

### Session 1 — A1 attempted, reverted, plan re-sequenced

**Outcome: net zero code change. The value is this file.**

A1 ("Triton import ladder helpers") was attempted and **fully reverted**. Findings:

1. **Created `acceleration/_typing.py`** with a hand-written `_ArrayNamespace` Protocol
   plus `_num`/`_flag` helpers. It had **zero importers** and was deleted. Two reasons it
   was wrong: `eqprop_kernel_backend.py:27` already defines both names (with a different,
   better signature — `_num("key", default)` reads a config dict rather than coercing a
   bare value), and numpy ships `py.typed`.
2. **`_num` was a no-op.** `def _num(x): return x  # type: ignore` cannot resolve
   `constexpr` vs `Literal`. It was replaced with hand-placed `# pyright: ignore` at 12
   call sites in `triton_kernels.py` — high churn, and it duplicated a module-level
   `TRITON_IMPORTED` that already lives in `backends.py`. Reverted. The honest fix is
   one scoped suppression policy (A8), not 12 inline ignores.
3. **`float()`/`int()` coercion is not a fix.** Applied across
   `contrastive_kernels.py`'s eight `initialize()` methods: it cleared 5 errors and
   *relocated* 17 into `ConvertibleToFloat`/`ConvertibleToInt`, because `float(object)`
   is itself ill-typed. Reverted; became root cause A3.
4. Baseline restored and verified: **1095 errors**, `tests/slow/` + `tests/graph/`
   deleted, `KNOWN_LONG` reconciled, no stale references to the removed dirs.

**Also discovered (uncommitted, from a prior session):** 16 `docs/figures/run_records/*.json`
were re-serialized compactly — value-identical, byte-different. Formatting-only churn
that will fight the manifest drift lock → R1.5.

**Next session starts at G0.1** (full suite, real counts). Do not start Phase 5.

---

### Measured snapshot (2026-10-01, verified this session)

| Metric | Value | Note |
|--------|-------|------|
| Repo-wide pyright errors | **1095** | confirmed baseline after revert |
| — in `p2p/` (61, incl. 35 generated) | 61 | → R1.4 exclusion, not a fix |
| Top file | `acceleration/kernels.py` | 90 errors / **7** annotations |
| `object`→scalar coercion family | **150** errors, 18 files | → A3 |
| CLI commands registered | **6** | draft claimed 7 incl. `gallery`; → G0.3 |
| `comp --help` | bare usage string, exits 1 bare | → G0.3 |
| Demos / manifest figures | 21 / 21 | F2 currently satisfied |
| `docs/archive/` | 467 files, 8.7 MB | → R1.3 |
| Test files by dir | primitives 145, property 133, algorithms 84, integration 56, unit 51, acceleration 15, ceec 14, platform 6, acceptance 1 | |
| pytest totals | *unverified* | appendix figure is stale → G0.1 |
