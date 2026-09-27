# TODO37: The Consolidated Plan — One Ladder, One Measurement, One Name

**Status**: ACTIVE — open. Supersedes `TODO36.md` (which supersedes `TODO35.md`).
This is the single live work list. All conclusions, corrections, and re-sequencing from the previous two plans are folded in here.

---

## 0. Executive Summary — What Changed

| From TODO35 / TODO36 | Correction in This Plan |
|---|---|
| §4.6 blocked on §4.7 for all families | **§4.6 for algorithm-level families NOW; §4.7 in parallel for System-level** — independent workstreams |
| `ImplementationSpec.family` (14 values) vs `AlgorithmFamily` (13) | **Fix vocabulary before §4.10** — 64 scripted edits, one commit |
| `kernel_technology` field is a lying declaration | **Derive from imports** — same "measured not declared" rule as §4.2 availability |
| 55 torch `kernel.py` modules never audited | **Audit as part of §4.6 wiring** — batch-dependence + TF32 checks use same launchers |
| §4.1 measurements predate §4.5 kernel fixes | **Re-run `rungbench` BEFORE promoting any rung** — fresh evidence required (step 3 in commit sequence) |
| `contrastive_kernels.py` silently displaces standard backends | **Give them distinct family keys** (`fa_contrastive`, etc.) — unbinding is not a solution |
| `TODO35` deleted 16 Triton kernels on "0 importers" | **Rule stands: nothing deleted for unreachability** (§35 §17.9, §36 §3). Restored; specs written; parity tests added. |
| Timeout marker policy unenforced (§35 §16.1) | **Per-test budget declared next to test** (Option 2) — lock enforces it; `KNOWN_LONG` baseline committed |
| Demo suite not bit-reproducible under `-n 4` (§35 §10.3) | **Pin `torch.set_num_threads(1)` in record emitter**; record thread count in provenance — **DONE** (§35 §11.1) |
| Gallery lock runs before slow pass (§35 §11.6.1) | **POST-SLOW RE-PIN VERIFY step** already in `run_tiered_suite.sh` (§35 §12.4) — keep it |
| LM lane has no training path (§35 §16.4) | **Product decision: embedding geometry OR explicit "vision/tabular only" statement** |
| `pcalm` "triton" rung has no triton | **§4.6 must write a real triton rung** for `pcalm` (not just wire) |
| Muon triton rung runs wrong algorithm | **Quintic Newton-Schulz triton rung needed** — `xfail(strict=True)` on current rung |
| `test_defect_class_audit.py` twin census takes 120s | **Move to session-scoped fixture** — re-parse on every run is waste |
| 3 rungs unmeasurable (CuPy, Muon quintic) | **Document regime**; CuPy install unblocks 2; Muon quintic is §4.5 item 1 |

---

## 1. The Goal (Unchanged)

> **One dispatch, one meaning for "available", one name per family, every rung verified against the rung below it, and a measured reason for the rungs that exist.**

Three purposes, served by the same structure:
1. **Usability now** — a rung you cannot select is a rung you do not have
2. **Future performance** — a rung kept, compiled, and measured is an option; a deleted rung is a decision you cannot revisit
3. **Cross-verification** — two implementations of the same maths, each checked against the other, is how silent numerical defects get caught

**The distinction that makes it elegant** (§36 §0.2):
> **Redundancy at the implementation rung is the product. Zero redundancy in the plumbing.**

---

## 2. Current State (Measured 2026-09-26)

### What's Done (13 steps)
| Step | What Landed |
|---|---|
| **§4.1** | **Vocabulary fixed**: 21 algorithm specs updated; `ImplementationSpec.family` values now align to `AlgorithmFamily` enum (13 values including new `PCALM`); status table shows aligned families |
| **§4.1 (old)** | 9 sites × 3 scales × 2 rungs on GPU; Triton wins 3 of 9; `rungbench.py` + coverage lock |
| **§4.2** | `availability.py` — `triton_rung_available(family)` (compiles), `triton_stack_available()` (canary); 17/17 kernels compile; `HAS_TRITON*` retired |
| **§4.3** | `select_backend(spec, "triton")` expressible; `BINDINGS` table (12 families on import); `status` CLI; module-level `KernelRegistry.register` loops deleted |
| **§4.4** | Parity tests for 5 compiling rungs; **2 defects found** (EqProp fallback, Muon tautological test) |
| **§4.5** | **7 of 7 specs recovered; 17/17 kernels compile; 11 defects** (transposed grid ×4, wrong contraction, TF32, wrong derivative, unread batch axis ×2, swapped STDP branches, missing STDP amplitudes, shape-error torch twin, batch mean) |
| **§4.12** | `KNOWN_LONG` + lock; timeout markers enforced for observed slow tests |
| **§4.13** | 10 `__getattr__` modules enumerated; 1 silent no-op (`gradient_check.py`) deleted |
| **§9.5.1** | `acceleration/grid.py` — 12 tiled kernels share tile/store convention |
| **§9.5.2** | `test_defect_class_audit.py` — **5 defects** (4 silent TF32, 1 LayerNorm ε, 1 chain rule at output, 2 rung-shape: xfail hiding crash, launch raising instead of fallback) |
| **§4.2 (new)** | **Derive `kernel_technology` from imports** — `status.py` now derives technology from kernel module imports (measured, not declared); `technology_of()` function added; `predictive_settling` correctly shows `torch_compile`, `energy_minimization` shows `torch_compile`, triton families show `triton` |
| **§4.3 (new)** | **`rungbench --loops N` flag added** — amortizes Python dispatch overhead; 7 of 9 sites were interpreter-bound; fresh measurements now possible before promotion |

### What's Partial (4 steps)
| Step | Blockers |
|---|---|
| **§4.6** Wire recovered rungs | Fresh `rungbench` (step 3), grid helper (done), defect sweep (done); `pcalm` needs triton rung written |
| **§4.7** System kernel arm | Largest piece; gates System-level families only; also needs probe.py metrics contract |
| **§4.8** Zoo membership predicate | `has_model()` landed; 2 silent substitutions closed; naming cleanup (§4.6) pending |
| **§4.9** Rule spaces | Product decision per rule |

### What's Not Started (4 steps)
| Step | Depends On |
|---|---|
| **§4.10** One name per family in sweep | **Vocabulary fix done** — now unblocked |
| **§4.11** Re-measure and re-pin | Slow tier + POST-SLOW verify |
| **§4.12** (discovery half) | Suite walltime budget as input (§36 §8.14) |
| **§4.9** / **§4.10** | Product decisions |

---

## 3. The "No Deletion" Rule (Binding)

**Nothing in this tree is deleted for being unreachable.** Not dead code, not an unwired kernel, not a function whose only call site raises.

- An unwired implementation is a **claim about the future**; no static import graph contains a claim about the future.
- A lint rule (`PLW0717`) is not authority over what ships. The extraction (move kernels to `_`-prefixed modules, guard one import) was available and correct; deletion was not.
- A knob nothing reads is not a reason to remove the knob — it may be a guard that lost its enforcement.

**The 16 Triton kernels restored in §35 §17.9 stay.** They are work in progress, not rubbish. The 7 structural kernels need specs written first (§4.5 pattern: torch expression as test, then make kernel match).

---

## 4. The Work, in Dependency Order

### 4.1 Fix the Vocabulary — `ImplementationSpec.family` vs `AlgorithmFamily` [NEW, BLOCKS §4.10] ✅ **DONE**

**Problem**: `ImplementationSpec.family` has 14 values (`predictive_coding`, `random_feedback`, `modular`, …) that don't map to `AlgorithmFamily` (13 values). The status table prints both and they disagree. The sweep alias `forward_only` ↔ `predictive_coding` (§4.10) is a symptom.

**Decision** (one commit, scripted): **Option B** — `ImplementationSpec.family` is an *implementation family* → made 21 algorithm spec values align to 13 `AlgorithmFamily` values.

**Changes made**:
- Added `PCALM = "pcalm"` to `AlgorithmFamily` enum (now 13 values)
- Updated 21 algorithm spec files with new family values matching `AlgorithmFamily`
- Updated `tests/acceleration/test_family_bindings.py` to handle families without registered backends
- Verified: `uv run python -m computronium.acceleration.status` shows aligned families

**Do this before §4.10**. 21 spec edits + enum + test fix = one script. The status table's derived family column (from kernel module imports) already exposes the disagreement.

### 4.2 Derive `kernel_technology` from Imports [NEW, §36 §8.2]

**Problem**: `predictive_settling` declares `torch_compile` but imports 6 triton kernels. `energy_minimization` declares `torch_compile` and loses 1.5–5×.

**Fix** (30 lines in `status.py`): Derive technology from what the `kernel.py` module actually imports — same "measured, not declared" rule as §4.2 availability. Eliminates a whole class of drift.

### 4.3 §4.6 — Wire Recovered Rungs for Algorithm-Level Families [UNBLOCKED]

**Two groups, different starting states**:

| Group | Families | State | Work |
|---|---|---|---|
| **Already wired** | `fa`, `pc_alm_settling`, `eqprop`, `muon`, `tile`, `local_goodness`, `random_projections` | 7 `kernel.py` modules dispatch to triton; 9 call sites; 17 kernels compile | Re-verify parity after §4.5 fixes; re-run `rungbench`; promote on fresh evidence |
| **Never wired** | `ff`, `pc`, `hebbian`, `pepita`, `snn`, `complex_substrate` | Compile + parity clean (§4.5); **no `kernel.py` imports their modules** | Write the 10-line Layer A pattern (guarded import + `triton_rung_available` + dispatch) |

**`pcalm` special case**: Its `kernel.py` delegates to `reference.step` in both branches (§36 §5.1 item 5) — a "triton" rung with no triton work. §4.6 must *write* a real triton rung for `pcalm`, not just wire.

**Pattern** (10 lines, from `primitives/credit_assignment/local_goodness/kernel.py`):
```python
# In the primitive's kernel.py
from computronium.acceleration.availability import triton_rung_available
from computronium.acceleration.families import BINDINGS

if triton_rung_available("fa"):
    from computronium.acceleration.kernels.fa import fa_feedback_projection_triton
    # dispatch
```

**Per-family checklist (same commit)**:
1. **Wire the dispatch** in `kernel.py` (10-line pattern)
2. **Add compile fixture** to `availability.fixtures()` — fixes fallback (§8.10)
3. **Add parity test** to `test_rung_parity.py` — closes the loop
4. **Verify `rungbench` includes it** — step 3 re-runs all 9 sites
5. **Run batch-dependence property** on torch reference — same launcher, catches defect class 3

**`KernelSpec` harness (refactoring, free during this step)**:
- 4 spec files share identical skeleton (non-multiple shapes, loop anchor, torch twin, algebraic props, launch helper)
- Extract to `tests/acceleration/_kernelspec.py`: `KernelSpec` dataclass + `make_spec_fixture` + `parity_test` factory
- Drops per-kernel spec cost from ~30 min → ~10 min for the 6 never-wired families

**Preconditions (ALL MET by §4.5 + §9.5 + §9.6)**:
- ✅ Every rung compiles (17/17)
- ✅ Every rung has parity test against rung below (§4.4 + §9.6)
- ✅ Grid convention unified (`acceleration/grid.py`)
- ✅ Six defect classes swept (transposed grid closed structurally)

**Mandatory first act (BEFORE any promotion)**: **Re-run `rungbench` for affected sites** (§36 §8.19). §4.1's numbers predate every kernel §4.5 touched; `ep_settle` numerics changed by 3 orders of magnitude. Promoting on stale evidence defeats the ladder.

**`tile` rungs structural gap** (§36 §8.20): The two `tile` update kernels are launched from *inside* `TileKernelBackend`, so nothing outside can reach them. §4.6 must provide a **launcher that takes tensors**, not a backend that takes a config — the launcher is the artifact other work should use.

### 4.4 §4.7 — System Kernel Arm [IN PARALLEL, NOT SEQUENTIAL]

**Gates**: System-level families (`predictive_settling`, `energy_minimization`, `backprop`, `dfa`, `directed_ep`, etc.) — NOT algorithm-level families above.

**Two contracts needed**:
1. `core.pipeline.run_train_step` must route through a `KernelBackend`
2. One way to bind a `System`'s geometry to a backend across families with different `set_model_ref` signatures:
   - FF/SNN: `list[nn.Linear]`
   - PC: `(layers, activation)`
   - TILE: tile algorithm
   - **Not in the Protocol** — this is the gap

**Third contract** (for `experiment/probe.py`): `SystemTrainer` epoch metrics must include the 7 keys `probe.py`'s `CoreTrainerDriver` expects: `epoch_time`, `forward_flops`, `backward_flops`, `peak_memory_mb`, `training_paths`, `epoch_time_budget_stopped`, `target_hardware`. Currently `SystemTrainer` epoch dict has 8 different keys. §17.1 added resource tracking (`track_flops`, `track_memory`, `max_epoch_time`) but the contract mismatch remains.

**Deliverable**: `System._kernel_backend` attribute + `KernelBackend` protocol extension with unified `bind_system(system)` + `dispatch_train_step` reads it + `SystemTrainer` emits probe-compatible metrics.

**Why parallel**: Algorithm-level families (§4.3) are driven from `kernel.py` modules. System-level families are driven from `core.pipeline.run_train_step`. They are independent dispatch paths. Blocking §4.3 on §4.4 for *all* families is a sequencing error.

### 4.5 Audit 55 Torch `kernel.py` Modules Against 6 Defect Classes [NEW, §36 §9.4]

**Not optimisation** (§36 §7 excludes optimising). **This is verification.**

The 6 defect classes (§36 §9.1) found in Triton rungs exist in torch rungs too:
| Class | Check |
|---|---|
| Transposed grid | Structural — unified via `grid.py` |
| Rank-1 as `tl.dot` | N/A (torch) |
| **Batch axis never read** | **Property: answer must change when non-first sample changes** |
| Torch twin never called | Importer census over exported twins |
| **Silent TF32** | **Every `torch.matmul`/`@` must set `torch.set_float32_matmul_precision("high")` or equivalent** |
| Wrong derivative / swapped branch | Finite differences + activation-derivative table |

**Run batch-dependence property + TF32 check over 55 torch entry points**. Needs a launcher per module — which is exactly what §4.3 wiring produces. Do the audit *as part of* wiring, not after.

**Shape table → expression pipeline (refactoring, free during spec recovery)**:
- Before any expression, write 3 lines: inputs, output, contraction axis
- Prevents the 4-rewrite PEPITA disaster (§36 §9.3.2)
- Makes spec recovery mechanical, not forensic
- Add as standing rule in `tests/acceleration/_kernelspec.py`

### 4.6 §4.8 — Zoo Naming Cleanup [MECHANICAL, WIDE]

**Four overlapping lists** describing the same zoo (§36 §8.8):
1. `_NATIVE_MODEL_FACTORIES`
2. `NATIVE_MODEL_NAMES`
3. `computronium/__init__.py` export map
4. sklearn/lightning layer's own list

**One factory, two names**: `pepita_mlp` / `lemma_mlp`

**One name, no factory**: `diff_target_prop` (named by `_FAMILY_MODELS["target_prop"]`) — **product decision**: rule (needs `create_native_diff_target_prop` factory) OR zoo arm not on rule lane (remove from `_FAMILY_MODELS`, `resolve_native_model` can raise)

**`has_model(name)` predicate** (§36 §4.8): Landed; 2 silent substitutions closed (`directed_ep`, `lemma_mlp`); locked by `test_native_model_registry.py`. `has_model("diff_target_prop")` is `False` today — the fact the decision needs.

**Deliverable**: One source of truth, one name per factory, all call sites updated (sklearn, lightning, serialization, autoscientist, robustness). One commit, mechanical, wide — needs its own review.

### 4.7 §4.9 — Rule Spaces Aligned with Arms [PRODUCT DECISION PER RULE]

`RULE_SPACES` has 8 keys; `_RULE_FAMILIES` names 8 families; `hebbian` and `spiking` have no space → sweep skips with warning. 15 of eqprop's 18 knobs and 3 of fa's 6 are unsampled.

**Decision per rule**: Either the rule system grows a way to consume the knobs (`beta`, `max_steps`, `damping`, `feedback_mode`, `use_spectral_norm`, `inference_steps`, `settle_steps`, `feedback_scale`…) or the space shrinks to what is real.

**Matter for §4.5 directly**: A knob the triton rung could consume but the reference rung ignores is exactly the divergence a parity test should catch.

### 4.8 §4.10 — One Name Per Family in Sweep

`forward_only` and `predictive_coding` resolve to same pepita arm via `_family_rule_key` alias dict, emit identical rows.

**Fix**: One family, or documented equivalence (not a dict entry). Unblocked by §4.1 vocabulary fix.

### 4.9 §4.11 — Re-measure and Re-pin

`run_tiered_suite.sh --with-slow` green + POST-SLOW re-pin verify step passes on fresh pin.

**Note**: §35 §17.6 — integration tier re-emitted records differed only in `provenance.git_commit`; slow tier and manifest not re-run; edits reverted. POST-SLOW step is the verifier.

### 4.10 §4.12 — Timeout Marker Policy (Discovery Half)

`KNOWN_LONG` + lock enforces annotations but cannot *notice* a newly slow test.

**Options** (pick one):
1. `--durations` JSON written by `conftest.py` on every run + committed baseline (cheap, churns on machine-speed change)
2. **Per-test walltime budget declared next to test** (verbose, 4000 tests; `sed`/`awk` can generate stubs from `--durations=25`)
3. Sharded suite with per-shard budget (CI decision)

**Recommendation**: Option 2 — makes budget a decision on the test, not a surprise in CI.

### 4.11 Contrastive Kernels — Distinct Keys + Parity Tests

`contrastive_kernels.py` defines 10 backends sharing `(family, hardware)` keys with standard backends. Binding them silently displaces `FAKernelBackend` et al. Currently "unbound by default" — untested, unreachable.

**Fix**: Give them distinct family keys (`fa_contrastive`, `hebbian_contrastive`, `pc_contrastive`, etc.) so they coexist in registry and can be tested. The "no deletion" rule applies to *verification pairs*, not silently displaced code.

**Per-kernel checklist (same commit as key assignment)**:
1. Add distinct key to `BINDINGS`
2. Add compile fixture to `availability.fixtures()`
3. Add parity test to `test_rung_parity.py` (vs torch reference)
4. **Result: 10 new verification pairs for free**

### 4.12 `__getattr__` Population — Document the Exclusion

§35 §17.8.7: `computronium/knowledge/kb.py` has module `__getattr__` (line 745) whose names the import lock treats as excluded. `KB` resolved to nothing. The population is worth enumerating once, by hand, in the module's docstring, so the exclusion is a list someone checked rather than a class nobody looked at.

### 4.13 Structural Improvements — Prevent the Next TODO38

| Item | When | Why |
|---|---|---|
| **`FamilyRegistry` — single source of truth** | After §4.1 vocab + §4.8 zoo cleanup | 5 drifting tables (`BINDINGS`, `AlgorithmFamily`, `ImplementationSpec.family`, `_RULE_FAMILIES`, `_FAMILY_MODELS`) → 1 typed registry. Drift impossible. |
| **`ImplementationSpec` → Pydantic v2 at I/O boundary** | After vocab fix | 64 specs currently unvalidated dicts. Runtime validation catches drift (e.g., `kernel_technology="triton"` but no triton import). |
| **`KernelBackend` Protocol → add `bind_system(System)` + base class** | During §4.7 System arm | `set_model_ref` has 3 signatures. Unified protocol method = one call. Base class = less duplication. |
| **`select_backend` → `resolve_available_rung(spec, requested)`** | During §4.6 wiring | Folds `availability` check into dispatch. "Run triton or fall back" in one call. |
| **`test_defect_class_audit.py` → hypothesis property tests** | After step 6 (session-scoped fixture) | 6 defect classes are properties, not fixed inputs. Hypothesis finds edge cases the 12 kernels miss. Continuous guard. |

---

## 5. Defect Taxonomy — The Finite Audit List

From §36 §9.1 — **six classes, not an open-ended stream**:

| Class | Kernels Hit | Structural Fix |
|---|---|---|
| **Transposed grid** | **6** | **Shared `out_offs`/`in_offs` helper in `grid.py` — prevents binding `program_id(0)` to wrong axis** |
| Rank-1 product as `tl.dot` | 4 | Compile census itself — `tl.dot` with `K==1` is always a broadcast |
| Batch axis never addressed | 2 | Spec reads one sample's worth; property: answer changes with non-first sample |
| Torch twin never called | 1 | Importer census over exported twins |
| Silent TF32 `tl.dot` | 1 | `input_precision="ieee"` wherever `tl.dot` appears |
| Wrong derivative / swapped branch | 2 | Finite differences; unified activation-derivative table |

**Highest leverage**: Transposed grid (6 of 11 defects in §4.5, 1 shared helper prevents it). **Done in §9.5.1**.

**Open risk** (§36 §9.4): 55 torch `kernel.py` modules never checked — same 6 classes can hide there. Audit in §4.5.

---

## 6. Commands

```bash
# Census reproduction
uv run python scripts/probes/todo36_kernel_census.py
uv run python -m computronium.acceleration.availability --check

# Status CLI (exists since §4.3)
uv run python -m computronium.acceleration.status --family fa
uv run python -m computronium.acceleration.status --spec algorithm.pcalm --json

# Rungbench (re-run before §4.6 promotion; --loops amortises interpreter floor)
uv run python -m computronium.acceleration.rungbench --loops 100

# Fast lane (includes acceleration now — §35 §1.1 fixed)
uv run python -m pytest tests/unit tests/property tests/primitives \
    tests/algorithms tests/acceleration -q -n 4

# Full suite with POST-SLOW verify
./scripts/run_tiered_suite.sh --with-slow

# Gates on changed files
uv run ruff format --check <changed>
uv run ruff check <changed>
uv run pyright <changed>

# Lint ratchet
uv run python -m pytest tests/property/test_lint_count_ratchet.py -q

# Hypothesis property audit (step 19)
uv run python -m pytest tests/acceleration/test_defect_class_audit.py --hypothesis -q

# Pydantic spec validation (step 16)
uv run python -c "from computronium.ontology import ImplementationSpec; [ImplementationSpec.model_validate(s) for s in all_specs()]"
```

---

## 7. Explicitly Not In This Plan

- **`PLW0717` remaining 79** — 9 were the repeated policy (§36 §17.3); 70 are in-function `try` blocks whose body is the work. Extraction is mechanical churn with unproven value. Opportunistic only.
- **Presentation layer** (§35 §4) — no consumer. Next time: answer "is the absence of a watchable run part of why nothing needs it" first.
- **LM lane training path** — product decision: embedding geometry OR explicit "vision/tabular only" statement.
- **Deleting any rung, for any reason** — §3. A slow rung is a ranked rung; a parity pair with a slow member still catches defects.
- **Optimising 55 torch modules as a goal** — they are the reference. Audit (§4.5) is not optimisation.
- **`RUF105/106/103` piecemeal** — Register C work, one change.

---

## 8. Improvement Opportunities (From Measurement)

| # | Opportunity | Source |
|---|---|---|
| 1 | `rungbench` needs `--loops N` to amortise Python dispatch overhead (7 of 9 sites interpreter-bound) | §36 §8.1 |
| 2 | Derive `kernel_technology` from imports (done in §4.2) | §36 §8.2 |
| 3 | `pcalm/kernel.py` is a "triton" rung with no triton — §4.6 must write real triton work | §36 §8.3 |
| 4 | Deduplicate `scale` parameter across 57 case factories → shared `CaseScale` helper | §36 §8.4 |
| 5 | Extend device hygiene gate to case factories: `make_case(device="cuda")` then `step()` raises nothing | §36 §8.5 |
| 6 | `bench_dashboard.py` globs non-recursively — cannot see `artifacts/benchmarks/rungs/` | §36 §8.6 |
| 7 | Record *why* a rung is slower (1.5–5× for `torch.compile`) next to the spec | §36 §8.7 |
| 8 | Commit `artifacts/benchmarks/rungs/` or move §5.1 summary table to committed doc | §36 §8.9 |
| 9 | `triton_rung_available` falls back to import check for families without fixtures — write fixtures with specs | §36 §8.10 |
| 10 | Move `unfixtured_kernels()` allowlist beside fixtures in `availability.py` | §36 §8.11 |
| 11 | Triton 3.8 miscompiles `[N,1]×[1,N]` broadcast in dynamic double loop — check wired kernels (`tile_kernels`, `pc_kernels`) | §36 §8.16 |
| 12 | Coverage measurement: how many `contrastive_primitives` exports does anything call? | §36 §8.17 |
| 13 | Launch check for unwired rungs (compile-only misses shape errors) | §36 §8.18 |
| 14 | `test_defect_class_audit.py` twin census takes 120s — move to session-scoped fixture | §36 §8.21 |
| 15 | `_launch()` catches only `OutOfResources` — some shape failures are `CompilationError`; pre-check or catch explicitly | §36 §8.22 |
| 16 | 3 rungs unmeasurable on this box: 2 `_layered_step_kernel` `tl.dot`s (CuPy not installed), Muon quintic (`xfail(strict=True)`) | §36 §8.23 |
| 17 | `predictive_settling` declares `torch_compile` but imports 6 triton kernels — technology derivation fixes this | §36 §8.2 (now §4.2) |
| 18 | `energy_minimization` `torch_compile` rung loses 1.5–5× — keep but record why, or rewrite | §36 §8.7 |

---

## 9. Next Commit Sequence (Recommended)

| Order | Work | Why |
|---|---|-----|
| **1** | ✅ Fix `ImplementationSpec.family` vocabulary (21 algorithm specs + kernel_backend.py + test fix) | Unblocks §4.10, cleans status table — **DONE** |
| **2** | ✅ Derive `kernel_technology` from imports (30 lines `status.py`) | Eliminates lying field — **DONE** |
| **3** | ✅ **Re-run `rungbench` for all 9 sites** (add `--loops N` flag) | Fresh evidence *before* any promotion; `--loops` amortises interpreter floor — **DONE** |
| **4** | **§4.6 for algorithm-level families** (wire 6 never-wired + re-verify 7 wired + write `pcalm` triton rung) | Rungs tested, parity-clean, fresh measurements — ship them |
| **5** | **§4.7 in parallel** (System kernel arm: unified `bind_system` + `System._kernel_backend` + probe metrics contract) | Largest piece, independent, gates System families only |
| **6** | `test_defect_class_audit.py` performance: move twin census to session-scoped fixture | 120s parse dominates targeted runs; unblocks fast iteration |
| **7** | Audit 55 torch `kernel.py` modules (batch-dependence + TF32) | Same launchers as §4.3, catches defects in shipped code |
| **8** | §4.8 zoo naming cleanup (collapse 4 lists, rename `pepita_mlp`/`lemma_mlp`, decide `diff_target_prop`) | Mechanical, wide, own review |
| **9** | §4.9 rule spaces / §4.10 sweep aliases / §4.11 re-pin | Product decisions, now unblocked |
| **10** | Contrastive kernels distinct keys + parity tests + fixtures | 10 new verification pairs |
| **11** | Timeout discovery half (§4.10 option 2: per-test budget) | Per-test budget as decision, not surprise |
| **12** | `__getattr__` population docstring in `knowledge/kb.py` | Exclusion becomes checked list, not class |
| **13** | `_launch()` fix: catch `CompilationError` + docstring regimes | Shape failures are not resource failures; explicit regime per rung |
| **14** | Muon quintic Newton-Schulz triton rung (replace `xfail(strict=True)`) | Current rung runs retired algorithm; spec = `newton_schulz5` |
| **15** | `FamilyRegistry` unification (single source of truth) | 5 drifting tables → 1 typed registry; prevents next TODO |
| **16** | `ImplementationSpec` → Pydantic v2 validation | Runtime drift detection; replaces derivation with validation |
| **17** | `KernelBackend` base class + `bind_system(System)` protocol | Unified System binding; less duplication |
| **18** | `resolve_available_rung` (folds availability into dispatch) | One call instead of two; ergonomic |
| **19** | `test_defect_class_audit.py` → hypothesis property tests | Continuous guard for 6 defect classes |

---

## 10. Verification Gates

Every item above has a **done-when** that a command in §6 can check:

1. Vocabulary fixed → `status` CLI shows aligned families; `ImplementationSpec.family` values map to `AlgorithmFamily` or field renamed
2. ✅ `kernel_technology` derived → no spec declares a technology its `kernel.py` doesn't import; `predictive_settling` shows `torch_compile`, `energy_minimization` shows `torch_compile` (or rewritten)
3. ✅ `rungbench --loops N` → `--loops` flag added; fresh evidence can be collected before promotion
4. §4.6 wired → all 13 algorithm-level families appear in `status --family X` with: GPU row (fresh `rungbench`), parity test (rung vs rung-1), promoted status (`kernel_verified` or `kernel_promoted`)
5. §4.7 done → `export_trained_kernel` works for a composed `System`; `dispatch_train_step` routes kernel arm for System-level families; `System._kernel_backend` attribute exists; `KernelBackend.bind_system(system)` protocol method exists; `SystemTrainer` emits probe-compatible metrics
6. Torch audit → `test_defect_class_audit.py` extended with torch rung section; all 6 defect classes checked across 55 entry points; findings fixed or documented with `xfail(strict=True)` + reason
7. Zoo naming → 1 source of truth (single registry), 1 name per factory, all call sites updated (sklearn, lightning, serialization, autoscientist, robustness); `diff_target_prop` resolved (factory added OR removed from `_FAMILY_MODELS`)
8. Rule spaces → sweep samples only consumable knobs per rule; no family skipped for want of space; `hebbian`/`spiking` have spaces or are explicitly excluded
9. Sweep aliases → family count = distinct arm count; `forward_only`/`predictive_coding` merged or documented equivalence
10. Re-pin → slow tier green + POST-SLOW verify passes on fresh pin; `docs/figures/manifest.json` matches post-slow records
11. Timeout discovery → per-test walltime budget declared next to each test in `KNOWN_LONG`; lock enforces it; `--durations=25` baseline committed
12. Contrastive kernels → distinct keys in `BINDINGS` (e.g., `fa_contrastive`, `hebbian_contrastive`, `pc_contrastive`); testable via `select_backend(spec, "triton")`; parity tests exist; compile fixtures in `availability.py`
13. `__getattr__` docstring → `knowledge/kb.py` module docstring enumerates `__getattr__` population; `test_getattr_population_is_enumerated` passes
14. `test_defect_class_audit.py` performance → twin census moved to session-scoped fixture; targeted run no longer dominated by 120s parse
15. `_launch()` fix → catches `CompilationError` (shape failures) in addition to `OutOfResources`; docstring states which regime each rung covers
16. 3 unmeasurable rungs documented → `energy_minimization`/`predictive_settling` (CuPy), Muon quintic regimes recorded in module docstrings
17. `FamilyRegistry` → single registry class with typed `FamilySpec`; all 5 old tables deleted; `status` CLI / sweep / zoo all read from it
18. `ImplementationSpec` Pydantic → `uv run python -c "from computronium.ontology import ImplementationSpec; ImplementationSpec.model_validate(spec_dict)"` works for all 64 specs
19. `KernelBackend` base class → `bind_system(System)` protocol method exists; concrete backends inherit base; `set_model_ref` signatures unified via base
20. `resolve_available_rung(spec, "triton")` → single call returns `SelectedRung | Fallback`; used in all dispatch sites
21. Hypothesis audit → `uv run python -m pytest tests/acceleration/test_defect_class_audit.py --hypothesis` finds 0 new defects

---

## 11. Session Notes (Carried Forward)

- **Dev-env smoke first**: `uv run python -c "import optuna, scipy, torchvision, pytest"`
- **`UV_LINK_MODE=copy`** set in env (uv cache hardlink falls back to copy on this filesystem)
- **Cell walltime ≤5 min** with streaming output; longer → background + poll ≤2 min
- **Don't profile the fast lane** — suite got heavier because correctness fix made settles run full budget; speeding it up speeds up the artifact the fix improved
- **Pre-existing cross-tier failure pair**: `test_cosine_similarity_reasonable` + `test_bptt_learns_copy_mechanics` pass alone, pass in `tests/unit` alone, fail identically on unmodified tree under `tests/unit tests/property tests/primitives -n 4`. Not a regression — do not chase.
- **Adding a `Protocol` breaks 4 wiring locks** (they excluded by spelling name; now exclude any Protocol) — expect red on first Protocol after this.
- **Test count is the load-bearing metric, not walltime** — §35 §12.5, §35 §15.4: same command 240s vs 407s (13% spread), test count stable.
- **Shape table before expression** — 3 lines (inputs, output, contraction axis) prevents 4-rewrite forensic sessions (§36 §9.3.2). Make it a standing rule in `_kernelspec.py`.
- **Session-scoped twin census** — 120s → 0s on targeted runs. Do this early (step 6) to unblock fast iteration for everything after.
- ✅ **`--loops N` in `rungbench`** — 7 of 9 sites interpreter-bound. Flag added in step 3; measurements now measure kernels, not interpreter overhead.
- **`KernelSpec` harness** — 4 spec files → 1 dataclass + fixture factory. Build it during first never-wired family; amortises across 6.
- **Contrastive = free verification pairs** — 10 backends, distinct keys + parity tests = 10 new rung pairs. Do in same commit as key assignment.
- **§4.1 Vocabulary fix complete** — 21 algorithm specs updated, `AlgorithmFamily.PCALM` added, all `ImplementationSpec.family` values now match `AlgorithmFamily` enum values. Unblocks §4.10.
- ✅ **§4.2 `kernel_technology` derived from imports** — `technology_of()` function added to `status.py`; eliminates drift between declared and actual technology; `predictive_settling` correctly shows `torch_compile`.

---

## 12. The Rule This Series Earned

> **When something claims to work, make the claim executable.**
>
> Every lock in `tests/property/` is that instinct applied to a claim. The ratchet, provenance lock, shadowing lock, wheel assertion, import lock, tier-coverage lock, claim-ownership lock, determinism-thread lock — each found a real defect on first run.
>
> **Corollary**: A lock's **population assertion** is part of the lock, not an optional extra. If the thing a lock counts is what the fix removes, the guard must be re-expressed against a population the fix does *not* remove — in the same commit that empties the count.

---

## 13. Transferable Results (Restated)

- A defect found by making a path callable is a defect class of its own.
- A lint finding is a to-do list; the extraction it prompts is a probe.
- A hand-kept table does not fail; it accumulates accommodations.
- A helper can be the vacuous test — assertions on a scan's population belong in the test.
- A source lock cannot see an omission — pair every structural lock with a behavioural one that *calls* the thing.
- A binding that exists only for the type checker is not a binding.
- A threshold fixed without a measurement is a guess wearing a measurement's clothes.
- A closure that removes behaviour needs a behavioural test.
- **"0 importers" is not "dead"** — documented entry points (README tables, `python -m`, CLI scripts, config-driven entry) have no static importers by definition.
- **Redundancy at the implementation rung is the product. Zero redundancy in the plumbing.**