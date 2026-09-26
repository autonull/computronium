# TODO36: One Acceleration Ladder

**Status**: ACTIVE — open. This is the plan series' single live work list. It
absorbs the acceleration unification and everything `TODO35.md` still owed;
`TODO35.md` is closed and its §17 is the record of why the decisions below were
made.

This is a **build** plan, not an audit. `TODO34.md` made the tree fast, provable
and ready to be presented; `TODO35.md` spent four rounds making claims
executable and produced a rule about deletion the hard way. This one completes a
*system* that already exists and is half-built.

---

## 0. Start here

### 0.1 The goal, and the three purposes it serves

The repo already declares the architecture. `README.md:1427`:

> The kernel ladder promotes through `reference → torch.compile → Triton`

and the machinery is real: `ImplementationSpec` carries a `reference_entrypoint`,
a `kernel_entrypoint`, a `kernel_technology`, a `ParityTolerance` and a
seven-state `ImplementationStatus`; `select_backend(spec, "auto")` promotes to
the kernel rung only once the status says `kernel_verified` or better; and
`assert_parity` + `test_kernel_parity` verify the kernel rung against the
reference rung for all 64 specs.

**The goal is that ladder, complete: one dispatch, one meaning for "available",
one name per family, every rung verified against the rung below it, and a
measured reason for the rungs that exist.**

Three purposes, all of them served by the same structure:

1. **Usability now.** A rung you cannot select is a rung you do not have.
2. **Future performance.** Triton may beat torch on a future card, a future
   triton release, or a future dtype. A rung that is kept, compiled and
   measured is an option; a rung that is deleted is a decision you cannot
   revisit.
3. **Cross-verification.** Two implementations of the same maths, each checked
   against the other, is how a silent numerical defect gets caught. This is
   already the repo's doctrine — `ParityTolerance` is a field on the spec — and
   it is the strongest argument for keeping every rung.

### 0.2 The distinction that makes the architecture elegant

**Redundancy at the implementation rung is the point. Zero redundancy in the
plumbing.**

Having a torch implementation and a triton implementation of the same
computation is *not* duplication — it is a verification pair, and the ladder
exists to hold pairs like it. What is genuinely duplicated, and what this plan
removes, is the plumbing: two registries, three population mechanisms for one of
them, four answers to "is the fast path available", ten family names that mean
two things, and a second dispatch that no caller reaches.

So the census's "two layers" are not two systems to be merged by deletion.
**Layer A is the ladder — dispatch, promotion, parity. Layer B is a set of rungs
that were built outside the ladder.** The work is bringing the rungs inside:
same registry, same promotion, same parity gate, same name. Nothing is deleted;
twelve kernels that currently cannot compile become a recoverable triton rung
for families that lack one.

### 0.3 What "finished" means

Every item is a property of the tree that a command in §6 can check:

1. One dispatch answers "which rung for *spec*", and it can name the technology.
2. One function answers "is the *triton* rung for *family* available on this
   box", and its answer covers compilation, not just CUDA.
3. Every family name appears in exactly one registry.
4. Every rung a spec declares is either verified against the rung below it, or
   its status says it is not promoted.
5. `artifacts/benchmarks/` has at least one **GPU** row per reachable triton
   rung, with the reference number beside it.
6. "The kernel for X" has exactly one referent in the codebase.
7. `scripts/broad_sweep.py` samples only knobs an arm can consume, and no
   family is skipped for want of a rule space.

---

## 1. The census

Reproduce with `uv run python scripts/probes/todo36_kernel_census.py` (§6.1).
Measured 2026-09-26, RTX 3080, triton 3.8.0, torch with CUDA. Every number is a
count; the probe is the source of truth and the numbers below are its output.

### 1.1 The two layers, restated as ladder and stray rungs

| | **Layer A — the ladder** | **Layer B — rungs outside it** |
|---|---|---|
| dispatch | `acceleration/registry.py` → `select_backend(spec, "auto")` | `acceleration/kernel_backend.py` → `KernelRegistry.get_best(family, hw)` |
| unit of work | a free function in a triton module | a `*KernelBackend` class |
| declared by | 64 `ImplementationSpec`s, all `("reference", "kernel")` | 12 `AlgorithmFamily` members |
| promotion | 7-state `ImplementationStatus`, gated | none — presence is the only test |
| parity | `ParityTolerance` + `assert_parity`, 64 specs | none |
| reached by | every training run | the two export CLIs, and nothing else |
| tested | 19 GPU tests pass here | none |
| compiles | yes, for the 17 kernels it reaches | 2 of 14 sampled (§2) |

The `KernelBackend` Protocol declares `initialize`, `forward`, `backward`,
`update_weights`, `get_memory_stats`, `get_settle_telemetry`. It does **not**
declare `set_model_ref`, `settle` or `compute_energy` — the three methods every
concrete backend adds and the three a caller actually needs. So the protocol
describes a shape no family satisfies, which is §1.5's flag defect in protocol
form: an interface that reports what it would like to be true.

### 1.2 What actually reaches a triton rung

64 modules named `kernel.py` live under `algorithms/` and `primitives/`. **7 of
them reach a triton module**, behind **17 kernels**, all compiling:

```
algorithms/pcalm/kernel.py                          pcalm_kernels (1)
primitives/credit_assignment/local_goodness         fa_kernels (2)
primitives/credit_assignment/random_projections     fa_kernels (2)
primitives/geometry/tile_mesh                       tile_kernels (7)
primitives/state_dynamics/energy_minimization       compile (1)
primitives/state_dynamics/pc_alm_settling           pcalm_kernels (1)
primitives/state_dynamics/predictive_settling       triton_kernels (6)
```

Two further sites reach triton from outside the `kernel.py` convention:
`acceleration/kernels.py` (`EqPropKernel`) and
`mep/optimizers/strategies/update.py` (Muon) — 9 call sites in total.

The other 55 are torch or `torch.compile`. That is the reference rung doing its
job, not a gap.

### 1.3 Layer B has no consumer, and its registry is populated as a side effect

- **13 concrete `*KernelBackend` classes, 0 with a consumer.** Each is
  referenced only by its own `KernelRegistry.register(...)` line and its own
  `__all__`.
- **`KernelRegistry` holds 1 family after `import computronium`** — `eqprop`,
  because `acceleration/__init__.py` imports `eqprop_kernel_backend` for its
  side effect, with a comment saying so.
- **The other families register inside a `for hw in HardwareTarget:` loop** at
  the bottom of their module, so they exist only once that module is imported.
- **Three population mechanisms, none of them a registration call a reader can
  find in one place:**
  1. `acceleration/__init__.py` imports `eqprop_kernel_backend` for its side
     effect → 1 family.
  2. `get_algorithm_kernels()` imports the other ten for their side effect;
     both call sites discard its return value, with the comment *"populate the
     registry (lazy import side effect)"*. Its only callers are
     `cli/export_kernel.py` and `cli/export_trained_kernel.py`.
  3. `contrastive_kernels.py` defines 10 more backends and registers them at
     *its* import — and **nothing imports that module**, so those 10 have never
     been registered anywhere.
- **And the sharpest one: Layer B's population is an emergent property of
  Layer A's import graph.** Ask Layer A a question — `all_specs()`, which walks
  the primitives package for `SPEC` attributes — and the walk imports
  `local_goodness/kernel.py`, which imports `fa_kernels`, which registers FA.
  So `KernelRegistry` holds 1 family before you ask and 2 after. **The second
  system's contents change when you query the first.** The census probe reports
  which of the two happened (`population came from Layer A's spec walk`).

### 1.4 The specs declare triton 54 times and deliver it 7

| query | answer |
|---|---|
| specs total | 64 |
| `status == "kernel_verified"` | 25 (39 `reference_only`) |
| `kernel_technology == "triton"` | **54** (10 declare `torch_compile`) |
| both triton-declared *and* kernel_verified | 22 |
| `kernel.py` modules that import a triton kernel | **7** (9 call sites) |

**54 specs declare triton; 7 modules deliver it.** The reason is structural and
it is the single most useful fact in this census: `Backend` is
`Literal["reference", "kernel"]`, so the ladder has **two rungs**, and the
technology of the kernel rung lives in a separate string field. You cannot
write `select_backend(spec, "triton")`. A spec's `kernel_technology="triton"`
is therefore a label on a rung it cannot select, and `kernel_verified` means
"the kernel rung is correct" for a rung that is mostly torch.

`README.md:1427` reports the 25 faithfully. What it does not say is that the
third rung its own sentence promises exists as a label and not as a rung.

### 1.5 Four ways the tree says "the fast path is available", none agreeing

| source | what it actually reports |
|---|---|
| `kernel_available("triton")` | `torch.cuda.is_available()` — a GPU, not triton |
| `HAS_TRITON_PC` / `_FF` / `_SNN` / `_HEBBIAN` / `_HAS_TRITON` | triton imported — on this box all five are `True` while 12 of the 16 kernels they guard cannot be launched — **retired in §4.2; the last one is now `TRITON_IMPORTED`, and the four are gone** |
| `KERNEL_TECHNOLOGY` on 41 primitives, `kernel_technology` on 54 specs | a string. Most never import a triton kernel |
| `spec.supported_backends` containing `"kernel"` | a torch implementation exists |

Four names, one question, four answers, and the two that claim the most are the
two that know least. This is the `cpu_only` defect (`TODO35.md` §11.4), the
`HAS_TRITON_*` defect (§17.10) and the `KERNEL_TECHNOLOGY` defect — the same
class three times, and §0.1's rule says the fix belongs in the code, once, at
the boundary.

### 1.6 No speedup has ever been measured

`artifacts/benchmarks/*.jsonl` holds **75 rows**. Every one is
`"backend": "kernel", "device": "cpu"`. There is no GPU row and no row
comparing a triton rung against the rung below it. The speedup claims in
`docs/archive/20260722/` (17.9x over NanoGPT, 200x MoT) are about the
*algorithms*, not these kernels, and are not evidence for this system.

**This is the first task in §4, not a footnote** — but read §4.1's framing
before assuming what it is for. It ranks. It does not delete.

**Superseded by §4.1 (2026-09-26).** The rows now exist —
`artifacts/benchmarks/rungs/` — and §5.1 has the numbers. The 75 CPU rows
described above are historical; nothing was deleted to make room.

---

## 2. The 16 unwired kernels: the triton rung five families do not have yet

`TODO35.md` §17.3 deleted them on a "0 importers" inference; §17.9 reverted
that; §17.10 measured them with
`scripts/probes/todo35_r17_kernels_compile.py`. Summary, because §4.5 depends
on it:

| group | count | failure | fix |
|---|---|---|---|
| triton API renames (`libdevice.sigmoid`, `tl.cosh`) | 3 | moved since they were written | mechanical |
| launch shape `tl.dot` refuses (K ≥ 8/16) | 2 | block config vs the contraction | mechanical |
| index / orientation / contraction disagree with a reference | 7 | **the intended maths exists only as this code** | spec first |
| correct today | 2 | `_lif_step_kernel`; `_ff_goodness_kernel` (matches its docstring to 1.9e-5) | — |

The seven are the interesting ones. The cheap fix was tried on
`_pepita_error_modulation_kernel` — `tl.dot` → `tl.sum(err[:, None] * fb,
axis=0)`, the textbook outer product — and it compiled, ran, and was still
**1.76 off** the torch reference, because the operands load in opposite
orientations and only one carries a batch stride. Three things had to be
reconciled at once, with no oracle to check against.

Read them as **the triton rung for PC, FF, PEPITA, SNN, HEBBIAN and the complex
substrate, written before the rung existed to hold them.** That is why they have
no caller: there was nothing to call them *from*. §4.5 builds the thing to call
them from, and §4.4 supplies the oracle they were written without.

---

## 3. Why this plan deletes nothing

Recorded once, prominently, because Round 5 got it wrong in public:

- **"0 importers" is not "dead."** `TODO35.md` §14.6 established this for
  documented entry points; §17.9 generalised it. An unwired implementation is a
  claim about the future, and no static import graph contains one.
- **A lint rule is not authority over what ships.** The deletion was motivated
  by `PLW0717` counting a `try` block. Removing the *policy duplication* (six
  modules each guarding their whole body with `try: import triton`) is free and
  worth doing; removing the contents was not, and the extraction is available
  without the deletion.
- **Two implementations of the same maths is the product, not the problem.**
  §0.2. The reference rung and the triton rung are a verification pair; the
  torch rung and the triton rung are a second one. Removing either halves the
  number of defects the pair can catch.
- **A kernel that does not compile is a specification nobody wrote down.** The
  seven in §2 are the only record of an intent nobody wrote down anywhere else.
  Recovering the intent is the work; the code is where it lives.

---

## 4. The work, in ladder order

Each step states what is true when it is done, in a form a command in §6 can
check. Do not start step *n+1* before step *n* is verified. Steps 4.1–4.7 are
the ladder; 4.8–4.12 are carried over from `TODO35.md` and ordered by what they
unblock here.

### 4.1 Measure the rungs against each other — to rank, not to prune

**DONE 2026-09-26.** Because §1.6 says nobody has. For each of the 9 call sites, on
a GPU, at three input sizes: wall time of the triton rung, wall time of the rung
below it, and peak memory. Write the rows into `artifacts/benchmarks/` in the
existing schema with `device: "cuda"` and a field that names the technology.

- **Landed as** `computronium/acceleration/rungbench.py`, run as
  `uv run python -m computronium.acceleration.rungbench`. Rows land in
  `artifacts/benchmarks/rungs/<spec id>.jsonl` — a subdirectory, so the
  `artifacts/benchmarks/*.jsonl` glob in `test_all_implementations` keeps meaning
  what it meant.
- **Schema amendment (recorded, deliberate):** a row carries `rung`/`backend`
  (`reference` | `kernel`) *and* a separate `technology` (`torch` |
  `torch_compile` | `triton`). The plan text said "a `backend` that names the
  technology"; overloading one field would have broken
  `scripts/bench_dashboard.py`, which selects `backend == "kernel"`, for no gain —
  two fields record both facts and neither lies.
- **Three input sizes** come from a new keyword-only `scale: int = 1` on the seven
  `cases.make_case` functions (default 1 ⇒ byte-identical to today's cases, so
  parity and smoke tests are unaffected).
- **The measurement could not be taken until this step, and that is the answer to
  §1.6.** Every geometry-bearing `make_case` built its `nn.Linear` stack on CPU
  and never moved it, so *any* `device="cuda"` run raised
  `mat2 is on cpu, different from other tensors on cuda:0` — in the reference rung
  as well as the kernel rung. `algorithms/pcalm/reference.py` had the same defect
  in `_make_pc_alm_system`. Fixed by `.to(device)` at construction. 75 rows, all
  CPU, was not a measurement gap; it was a broken GPU path nobody could reach.
- **Locked by** `tests/acceleration/test_rung_bench_coverage.py`: every available
  rung of every site must have a `status: "ok"`, `device: "cuda"` row, at three
  scales, with a reference number at the same scale. Read-only, so it runs on a
  CPU box. `artifacts/` is gitignored, so the lock *skips* when no rows have been
  recorded (same policy as the microbench-evidence check in
  `test_all_implementations.py`) and fails when rows exist but a rung lost
  coverage. **The rows are therefore local evidence, not committed artefacts** —
  the one thing §0.3 item 5 wants that this repo's `.gitignore` does not yet
  allow. See §8.8.
- **Done when** `artifacts/benchmarks/` has GPU rows for all 9, each beside its
  reference number, and §5 records the result honestly — including any site
  where triton is *slower*, which is a result and not a failure. **Met**; see §5.
- **What the numbers are for:** ranking *where triton is closest to winning*,
  so §4.5 and §4.6 spend effort on the families that will benefit first. A rung
  that loses today keeps its parity pair and its place in the ladder; it moves
  down the priority list. **No measurement in this plan is an argument for
  deleting a rung** — §0.2 and §3.
- This step also settles a question §4.4 needs: whether a rung that is slower
  but bit-identical is worth promoting for verification value alone. That is a
  real trade and it deserves a recorded answer per family rather than a global
  rule. **§5 records the per-family answer this step produced.**

### 4.2 One meaning for "available"

**DONE 2026-09-26.** A single function, in `acceleration/`, that answers *"can
the triton rung for this family run, here, now?"* and means it: the kernel imports
**and compiles**. Triton's `.warmup()` compiles without launching, so the honest
flag is "compiled once, cached", not "CUDA is present".

- **Landed as** `computronium/acceleration/availability.py`:
  - `triton_rung_available(family)` — the family answer. Every kernel in the
    family must compile. This is what the four triton `kernel.py` dispatch sites
    (`local_goodness`, `random_projections`, `pc_alm_settling`, `algorithms/pcalm`)
    now call.
  - `triton_stack_available()` — the box-wide answer: a known-good kernel from the
    baseline is compiled here. This is what `kernel_available("triton")` reports,
    so all ~60 `is_available()` implementations that call it are fixed in one
    place, which is §0.1's rule (the fix belongs at the boundary, once).
  - `compile_state` / `compile_report` / `regressions` / `record_baseline` and the
    CLI `python -m computronium.acceleration.availability [--check|--record]`.
- **The four names are gone, not aliased.** `HAS_TRITON_PC`, `HAS_TRITON_SNN` and
  `HAS_TRITON_HEBBIAN` are deleted (no consumer but their own `__all__`);
  `HAS_TRITON_FA` / `_TILE` / `_PCALM` are renamed `TRITON_IMPORTED_*`, because
  that is the only thing they ever measured; `backends.HAS_TRITON` becomes
  `TRITON_IMPORTED`. `kernel_available("cupy")` used to `return True` from a `try`
  block that could not fail — it now returns `HAS_CUPY`, which is itself measured
  by allocating on the device. **No `HAS_TRITON` name remains in the tree.**
- **Standing compile check, promoted out of the probe.** The 14 hand-written
  fixtures of `scripts/probes/todo35_r17_kernels_compile.py` moved into
  `availability.fixtures()`, joined by fixtures for the two *wired* families a
  dispatch site actually asks about (`fa`, `pcalm`) so their answer is a
  measurement. **The probe is deleted** — one census, in the tree, with a
  baseline. Baseline: `computronium/acceleration/triton_compile_baseline.json`,
  `--record`ed, 5 of 17 compile and 12 do not.
- **Regression-only, as §4.2 requires.** `regressions()` compares measured state
  to the baseline and reports a problem only when a kernel that compiled stops
  compiling. A kernel that newly compiles is progress and is not reported. The 12
  uncompilable kernels are named, recorded states — §2's classification, now
  machine-readable.
- **Done when** `HAS_TRITON_PC` and its siblings report what they say, and a test
  asserts a flag is `False` for a kernel that does not compile. **Met:**
  `tests/acceleration/test_triton_availability.py` asserts
  `triton_stack_available() is True` *and* `triton_rung_available("pc") is False`
  in the same breath — §2's finding as an executable fixture, 5 flags that used to
  say `True` while 12 kernels could not launch.
- **The census is closed.** `discover_kernels()` enumerates every module-level
  `@triton.jit` in the acceleration package; `unfixtured_kernels()` must equal the
  test's `GPU_TESTED` allowlist, so a new kernel cannot join without either a
  fixture or a named test that compiles it. Adding a row is the fix — deleting a
  kernel is not one (§3).
- **A synthesiser was tried and rejected, with the measurement recorded.** Building
  fixture arguments from each kernel's parameter names and annotations produced
  **13 false failures out of 18** on kernels that demonstrably work, because a
  wrong-but-well-typed argument is a compile error, not a no-op (`tl.dot`'s `K >= 8`,
  equal reduction dimensions). Fixtures are hand-written from the signature; that
  is the cost of a truthful answer.
- **Family labels are not all `AlgorithmFamily` members.** The complex substrate's
  `tanh` kernel is labelled `complex_substrate`, not `pcalm` — it is not part of
  pcalm's rung, and folding it in would have made `pc_alm_settling`'s rung report
  unavailable for someone else's broken kernel.
- **Why the baseline is load-bearing** (restated, because it now has a file):
  a check that simply failed on those 12 would be red on arrival, and the fastest
  way to green it is deletion. `--check` exits 0 today with 12 known failures
  recorded, and non-zero the moment one of the 5 stops compiling.

### 4.3 Make the technology a selectable rung

**DONE 2026-09-26.** This is the unification, and it is smaller than the census
makes it look.

1. **A rung can be named.** `dispatch.select_backend(spec, "triton")` is now
   expressible, as is any other technology in `KernelTechnology` (which gained
   `"torch"`, which is what the reference rung has always been). Asking for a
   technology a spec does not use raises a `ValueError` that names what it *does*
   have — *"has no triton rung: supported backends are reference, kernel, kernel
   technology is torch_compile, status is kernel_verified"* — because "not
   available" without that is the defect §4.2 removed.
   `resolve_rung(spec, requested) -> SelectedRung` is the same decision with the
   technology, entrypoint, status and promotion flag attached; `select_backend` is
   its `rung` field, so there is one implementation of the policy, not two that
   can disagree. `select_backend` keeps its old signature and its 19 tests.
2. **`KernelRegistry` is documented as the binding layer**, in its own module
   docstring: rungs that need `initialize`, `set_model_ref` and export
   serialisation. It is not the training dispatch, and now says so where a reader
   arrives.
3. **Population is out of the side effects, all three of them (§1.3).**
   `accelerator/families.py` holds `BINDINGS` — one row per family, naming the
   module and the class — and `register_all()`. The ten
   `for hw in HardwareTarget: KernelRegistry.register(...)` loops at the bottoms
   of the kernel modules are **deleted**; the
   `import ... eqprop_kernel_backend  # for its side effect` line in
   `acceleration/__init__.py` is deleted; and `get_algorithm_kernels()` now
   derives its keys from `BINDINGS` instead of keeping a second, differently-keyed
   list. The two export CLIs no longer call it to "populate the registry".
   **`import computronium.acceleration` now binds 12 families (was 1), and
   `all_specs()` no longer changes that number** — the emergent property of §1.3 is
   gone, and `tests/acceleration/test_family_bindings.py` pins it, including an
   AST census that fails if any module calls `KernelRegistry.register` at module
   level again.
   - **The contrastive kernels stay unbound by default.** Ten classes share a
     `(family, hardware)` key with the standard backends, so binding them would
     silently displace `FAKernelBackend` and friends. `register_contrastive_kernels()`
     remains, explicitly callable, and its import-time call is gone. That is
     §1.3's mechanism 3 resolved by *naming* the choice, not by deleting the code.
   - **A family has at most one binding**, because the registry keys on
     `(family, hardware)`. `ThreeFactorKernelBackend` is a Hebbian variant and is
     therefore reachable by direct import only — registering it would replace
     `HebbianKernelBackend` for the whole family. Recorded rather than silently
     changed.
4. **One name per family, mostly.** `AlgorithmFamily` (13 values) is the binding
   layer's namespace; spec ids are the ladder's; and the *third* vocabulary —
   `ImplementationSpec.family` (14 values like `predictive_coding`,
   `random_feedback`) — is the one §4.3 could not reconcile without renaming
   64 specs, so it stays and is now joined by a **derived** family in
   `status.family_of()`, read off the kernel module's own imports. The status
   table prints both, and they disagree in exactly the places that are defects:
   `algorithm.fa` declares `kernel_technology="triton"` and derives **no** family,
   because its `kernel.py` imports no acceleration kernel module at all.
5. **Layer A keeps `select_backend`**, as §4.3 requires.

- **Done when** §0.3 items 1–3 hold, and §6.2 prints one unambiguous answer per
  family. **Met.** §6.2 exists:
  `uv run python -m computronium.acceleration.status --family fa` prints one line
  per rung — `spec, family, rung, technology, compiles, parity, gpu, status` —
  with `none` meaning *not recorded here*, never *absent*.

### 4.4 Cross-verification as a product: parity between adjacent rungs

**DONE for every rung that compiles, 2026-09-26 — and it found two defects on
first run, one of them a test that certified the wrong thing.**

`test_all_implementations.test_kernel_parity` already checks rung 1 against rung 0
for all 64 specs at the level of `step(case)`. This step checks the level below
that: the kernel entry points themselves, triton against the torch expression
they replace, with the tolerance the owning spec already carries.

- **Landed as** `tests/acceleration/test_rung_parity.py`: parity for
  `fa_feedback_projection_triton` (vs `error @ feedback`),
  `fa_batched_outer_triton` (vs the batched outer product),
  `fused_dual_primal_update` (vs `_eager_dual_primal_update`), `muon_orthogonalize`
  (vs `newton_schulz5`) and `TritonEqPropOps.step` (vs the Euler–tanh step).
  Membership is decided by `availability.compile_state`, so this file cannot
  quietly pass a family whose rung is not running.
- **Where the two rungs cannot be made bit-identical** (different reduction
  order), the tolerance is the owning spec's, per family — not a global loosening.

**Two defects, both found by the new tests and both real:**

1. **`TritonEqPropOps.step`'s eager fallback disagreed with its own triton kernel.**
   The kernel indexes the bias as `offsets % bias_n`, so a 16-element bias serves a
   256-element state; the fallback did `pre_act + bias`, which either broadcasts
   wrongly or raises `RuntimeError: The size of tensor a (256) must match the size
   of tensor b (16)`. **Fixed** — the fallback now indexes the bias the way the
   kernel does, so the two rungs agree on any bias width. This is the whole
   argument for §4.4 in one defect: two implementations of one maths, one of
   which was wrong, and no test that could see it.
2. **The triton Muon rung is a different algorithm from the torch rung, and its
   test was comparing it to a copy of itself.** `MEP_TritonOps.muon_orthogonalize`
   runs the naive `0.5·X(3I − XᵀX)` iteration and its docstring claims "~1e-7
   parity with the PyTorch reference". The torch rung is
   `newton_schulz5` — the *quintic* `(3.4445, −4.7750, 2.0315)` schedule — whose
   own docstring records why the naive form was replaced: "under-converges from
   Frobenius normalization and measured orthonormality error ~0.85 on Gaussian
   matrices". Meanwhile `test_muon_orthogonalize_equivalence` re-implemented the
   naive iteration *as its "PyTorch reference"* and asserted 1e-4 agreement, so it
   passed while proving nothing.
   **Not fixed here; recorded.** Both tests now compare against `newton_schulz5`
   and are marked `xfail(strict=True)` with the reason: a strict xfail fails the
   moment someone fixes the rung, so the divergence cannot be forgotten. Measured
   divergence on a random 64×48 input: `max_abs_diff` 0.22, cosine 0.91.
   **This is the first item of §4.5** — the fix is a quintic triton rung (the
   kernel already has the tiled Gram GEMM; it needs `A²` as well), and the
   specification — "equal to `newton_schulz5`" — was written down by the reference
   all along, which is §4.5's own instruction *write the torch expression first*.

- **Done when** every reachable triton rung has a parity test against the rung
  below it, recorded with the same `ParityTolerance` the spec already carries,
  and §0.3 item 4 holds. **Met for the 5 rungs that compile.** The other 12 have no
  rung to compare — they are §4.5's work, and `compile_state` is the switch that
  will move them here.
- **A third finding, recorded rather than fixed:** `ff` and `snn` have compiling
  kernels (`_ff_goodness_kernel`, `_lif_step_kernel`) that **no spec reaches** —
  no `kernel.py` imports `ff_kernels` or `snn_kernels`, so nothing verifies them
  and nothing dispatches them. `test_rung_parity.UNWIRED_BUT_COMPILING` records
  them by name; a third one appearing fails the test. The fix is §4.5/§4.6, and
  the remedy is never deletion (§3).

### 4.5 Recover the specifications for the seven

For each of the 7 kernels whose intent is unrecoverable: **write the torch
expression it is meant to equal, first, as a test.** Then either make the kernel
match that expression or record that the expression is unimplementable in
triton and why. Do not port from the kernel to the test — the kernel is what is
in question.

- **Done when** each of the 7 has a named torch reference in the test suite, and
  the kernel either matches it or has a written reason it cannot.
- **FF is the pilot**: `_ff_goodness_kernel` already compiles and is correct to
  1.9e-5, so only its contrastive update is in question, and FF has a real
  reference in `algorithms/ff/`.

### 4.6 Then, and only then, wire the recovered rungs into the ladder

A recovered spec becomes a selectable rung through the Layer A pattern, which
`primitives/credit_assignment/local_goodness/kernel.py` demonstrates in about
ten lines: a guarded import, an `is_available()` that means it (§4.2's), and a
branch at the one hot site.

- **Done when** the family appears in §0.3 item 5 with a GPU row, a parity test
  against the rung below it, and a status promoted through the existing ladder
  — not by editing the status by hand.

### 4.7 A kernel arm on the System pipeline

`TODO35.md` §17.8-1. A `System` trains through
`core.pipeline.run_train_step`, which has **no kernel arm**;
`dispatch_train_step` reaches a backend by reading `model._kernel_backend` off
an `nn.Module`, and a `System` has no such attribute. Separately,
`KernelBackend.set_model_ref` is per-family — a `list[nn.Linear]` for FF and
SNN, `(layers, activation)` for PC, a tile algorithm for TILE — and is **not in
the Protocol**, so "bind a System's geometry" is not one call and there is no
interface that says what binding means.

Until both exist, `cli/export_trained_kernel.py` is a documented refusal (named
in `test_undefined_name_lock.py`'s `KNOWN_BLOCKED`) and no family can be
accelerated *through a composed System*. This is the largest piece of work here
and it gates §4.6 for every family except those driven at the algorithm level.

### 4.8 A membership predicate for the zoo registry

**PARTIAL 2026-09-26 — the predicate landed; the rename behind it did not.**
`TODO35.md` §17.8-2. `backprop_parity._FAMILY_MODELS` names `standard_fa`,
`dfa_deep`, `diff_target_prop`, `fabricpc_graph_pcn`, `directed_ep` — real zoo
arms that are not learning rules, and whose comparison is meaningless on the rule
lane (it would compare one MLP against itself). `resolve_native_model` "falls back
to the EqProp composition" for any unknown name, a silent substitution in the one
place that must not make one.

- **`has_model(name)` exists**, on the registry, matching by exactly the fragments
  `resolve_native_model` matches — so the two cannot disagree. Locked by
  `tests/unit/test_native_model_registry.py`, which also asserts membership and
  resolution never contradict each other.
- **The registry was found to be *incomplete*, which is the actual bug.** It
  registered 9 fragments while `models.native` exports 18 factories, so two names
  were being silently substituted today: **`directed_ep` ran as EqProp** despite
  having `create_native_directed_ep`, and **`lemma_mlp` ran as EqProp** despite
  having `create_native_lemma_mlp`. Both now reach their own factory. That is two
  live silent substitutions closed by adding the rows that were missing — not by
  renaming anything.
- **`resolve_native_model` still falls back, and that is now a recorded decision
  rather than an oversight.** Exactly one name in the tree still misses:
  **`diff_target_prop`**, named by `_FAMILY_MODELS["target_prop"]`, has no native
  factory anywhere in `models.native`. Raising on a miss would break that study, so
  the question is not mechanical: is `diff_target_prop` a rule (and needs a
  factory), or a zoo arm that does not belong on the rule lane at all (§4.8's own
  framing)? That is a product decision about the parity study, and it is left to
  whoever owns it. `has_model` is the tool for answering it: `has_model(
  "diff_target_prop")` is `False` today, which is the fact the decision needs.
- **Not done, and named:** the naming itself. Four lists still describe the zoo —
  `_NATIVE_MODEL_FACTORIES`, `NATIVE_MODEL_NAMES`, `computronium/__init__.py`'s
  export map, and `NATIVE_MODEL_NAMES` in the sklearn/lightning layers — and two
  names for one factory (`pepita_mlp` / `lemma_mlp`) are exactly the kind of
  duplication §0.2 condemns. Collapsing them is a rename across the sklearn,
  lightning, serialization and autoscientist call sites; it is §8.15, not a
  side-effect of adding a predicate.

### 4.9 Bring the rule spaces back in line with the arms

`TODO35.md` §17.8-3. `RULE_SPACES` has 8 keys; `_RULE_FAMILIES` names 8
families and two (`hebbian`, `spiking`) have no space, so the sweep skips them
with a warning. Fifteen of eqprop's eighteen knobs and three of fa's six are
now unsampled rather than sampled-and-ignored, because
`consumable_config_keys` derives what an arm can take from its factory
signature (`beta`, `inference_steps`, `settle_steps`, `feedback_scale` are all
real and were being discarded before Round 5 fixed the derivation).

- Either the rule systems grow a way to consume the remaining knobs, or the
  spaces shrink to what is real. **This is a product decision per rule**, and
  it matters to §4.5 directly: a knob the triton rung could consume is a knob
  the reference rung ignores, which is exactly the kind of divergence a parity
  test should catch.
- **Done when** §0.3 item 7 holds.

### 4.10 One name per family, in the sweep too

`TODO35.md` §17.8-4. `forward_only` and `predictive_coding` resolve to the same
pepita arm through `_family_rule_key`'s alias dict and now visibly emit
identical rows. A family whose space and propagator are the same should be one
family, or the alias should be a documented equivalence rather than a dict
entry.

- **Done when** the sweep's family count and its distinct-arm count agree, and
  the alias is either gone or named.

### 4.11 Re-measure and re-pin

`TODO35.md` §16-5. The slow tier and `docs/figures/manifest.json` have not been
re-run since Round 4. Round 5's integration pass moved no demo numerics — every
re-emitted record differed only in `provenance.git_commit` — and the record
edits were reverted rather than committed, because backfilling a pin without
the pass that verifies it is the §11.2 failure. §7's POST-SLOW step is the
thing that would verify it.

- **Done when** `run_tiered_suite.sh --with-slow` is green and the POST-SLOW
  re-pin verify step passes on a fresh pin.

### 4.12 The timeout-marker policy

**DONE 2026-09-26** — on the half that can be checked, and the half that cannot
is now written down rather than assumed. `TODO35.md` §16-1, fourth round running.
Five tests were marked by hand from one `--durations` run; nothing stopped the
next 100 s test from appearing unmarked, and the failure mode is a `Timeout` that
reads like a flake.

- **The plan's own full-suite run supplied the evidence.** `pytest tests/` on
  2026-09-26: 4058 passed, 1 failed —
  `tests/integration/test_demo_pc_alm.py::test_demo_pc_alm`, `Failed: Timeout
  (>120.0s)` from inside a torch-inductor CPU graph, after **36 s when run
  alone**. Not a logic failure and not a flake: an unmarked test whose walltime
  depends on what else the machine is doing. That is the defect, caught by the
  very mechanism the item is about.
- **Landed as** `tests/test_timeout_marker_policy.py`. `KNOWN_LONG` is the list of
  tests *observed* to exceed the 120 s default, and each must carry an explicit
  `@pytest.mark.timeout` — so its budget is a decision on the test rather than a
  surprise in a log. `test_demo_pc_alm` is annotated `600` with the measurement in
  a comment. Two more tests guard the list against rot: a row must point at a test
  that exists, and the global `timeout = 120` must still be the policy the list
  was derived against.
- **The limit, stated rather than papered over:** the *discovery* half cannot be a
  static check. A newly slow test is still found by a full run's `--durations=25`
  and added to `KNOWN_LONG` by hand. The lock makes the annotation enforceable
  once a test is known; it does not make a test known. A `--durations`-driven gate
  would need the suite's runtime budget to be a first-class input, which is a
  larger piece of work than this item and is named in §8.13.
- **The remedy for a row is a marker.** Never a deletion, never a `skip` to make
  the number go away — the same rule as §3, for the same reason.

### 4.13 The knowledge layer's `__getattr__` population

`TODO35.md` §17.8-7. `knowledge/kb.py` has a module `__getattr__` whose names
the import lock treats as excluded because they are not statically derivable.
`KB` was one of them — a name that resolved to nothing. Enumerate the
population once, by hand, in the module's docstring, so the exclusion is a list
someone checked rather than a class nobody looked at.

---

## 5. Results (filled in as §4 lands; empty means not measured)

Measured 2026-09-26, RTX 3080, triton 3.8.0, torch with CUDA, `float32`, seed 0,
3 warmup + 5 timed iterations per (site, scale). Reproduce with §4.1's command;
raw rows in `artifacts/benchmarks/rungs/`. `ratio` is median kernel-rung wall
time ÷ median reference-rung wall time at the same scale, so **below 1.0 means
the fast rung won**.

### 5.1 §4.1 — the ladder, measured for the first time

| site | declared technology | scale 1 | scale 8 | scale 32 | verdict |
|---|---|---|---|---|---|
| `pc_alm_settling` | triton | **0.60** | **0.58** | **0.73** | the one clear win |
| `muon_newton_schulz` | triton | **0.71** | **0.67** | 1.26 | wins small, loses at 2048² |
| `eqprop_forward_step` | triton | **0.84** | **0.84** | **0.91** | small consistent win |
| `pcalm` | triton | 1.03 | 0.97 | 1.13 | noise — see below |
| `local_goodness` | triton | 1.12 | 1.13 | **0.96** | loses until it wins |
| `tile_mesh` | triton | 1.30 | 1.03 | 1.11 | loses |
| `random_projections` | triton | 1.01 | 1.38 | 1.42 | loses, worse with size |
| `energy_minimization` | torch_compile | 1.99 | 1.61 | 1.53 | compile loses |
| `predictive_settling` | torch_compile | 4.86 | 4.29 | 5.00 | compile loses badly |

Six answers fall out of that table, and only the first was expected.

1. **Triton wins at 3 of 9 sites, and decisively at exactly one.** `pc_alm_settling`
   is 0.58–0.73 across every size — the first rung in the tree with a measured
   reason to exist. Per §4.1's ranking, that is where §4.5/§4.6 effort goes first.
2. **Six of the nine kernel rungs are slower than the rung below them.** A
   result, not a failure (§3): each keeps its parity pair. §0.3 item 5 is
   satisfied by rows, not by wins.
3. **The six spec sites are Python-overhead bound, so their ratios are not kernel
   measurements.** Their reference rung costs ~1.0 ms at scale 1 *and* at scale
   32; the floor is Python dispatch, not FLOPs. `tile_mesh` (1.17 → 3.34 ms) and
   `muon` (0.74 → 14.98 ms) are the only two whose timing actually tracks size.
   **Consequence for §4.1's ranking: the honest per-rung comparison needs a
   scale where the work dominates, and for the other seven sites that means either
   a much larger case or a loop that amortises dispatch.** Do not read the
   near-1.0 ratios as "triton ≈ torch"; they are "both ≈ the interpreter".
4. **`torch.compile` is a loss on both sites that use it** (1.5× to 5×), and it is
   the technology `predictive_settling`'s spec declares while its `kernel.py`
   actually imports six triton kernels — §1.5's defect, now with a number attached.
5. **`pcalm`'s ratio is measurement of nothing.** `algorithms/pcalm/kernel.py`
   delegates to `reference.step` in both branches, so its "triton" rung *is* the
   reference rung; 1.03/0.97/1.13 is run-to-run noise and should be read as
   "no triton work happens here". §4.6 is where that stops being true.
6. **`predictive_settling` is the most valuable GPU row in the tree**, and not for
   its speed: it is the site where the declared technology and the imported
   technology disagree, and the first measurement anyone has taken of it.

### 5.2 §4.1's open trade, answered per family

§4.1 asked whether a rung that is slower but parity-clean is worth promoting for
verification value alone. The measured answer, per family, recorded rather than
globalised:

| family | slower? | parity-clean? | answer |
|---|---|---|---|
| `pc_alm_settling` | no — it wins | yes | promote on speed; the usual case |
| `muon`, `eqprop` | no at small sizes | yes | promote on speed, with a size caveat recorded |
| `local_goodness`, `tile_mesh`, `random_projections` | yes | yes | **keep promoted for verification value** — the parity pair is the product (§0.2 purpose 3) and the speed deficit is one measurement on one card |
| `energy_minimization`, `predictive_settling` (`torch_compile`) | yes, 1.5–5× | yes | keep, but the rung under test is the wrong one; see opportunity 2 below |
| `pcalm` | n/a — no triton work | yes | unrankable until §4.6 gives it a real rung |

### 5.3 §4.2 — what "available" says now

| question | before | after |
|---|---|---|
| triton importable? | `HAS_TRITON` / `kernel_available("triton")` — a CUDA check | `TRITON_IMPORTED`, a fact about an import, named as one |
| can triton compile *anything* here? | not asked | `triton_stack_available()` — compiles a baseline canary |
| can *this family's* triton rung run? | `HAS_TRITON_<FAM>`, `True` for 5 families whose kernels do not compile | `triton_rung_available(fam)` — `pc`/`ff`/`pepita`/`snn`/`hebbian`/`complex_substrate` all report **`False`** today |
| is cupy usable? | `return True` from an empty `try` | `HAS_CUPY`, which allocates on the device |
| how many triton kernels compile? | "2 of 14 sampled", from a probe | **5 of 17**, from `availability.py --record`, machine-readable |

`triton_rung_available("fa")` and `triton_rung_available("pcalm")` are `True`, and
that is now a measurement: the two families `local_goodness`, `random_projections`,
`pc_alm_settling` and `algorithms/pcalm` dispatch on have their kernels compiled
before the rung is offered. `triton_rung_available("pc")` is `False` on the same
box in the same second — which is the whole of §1.5 in one line of output.

### 5.4 §4.3 — the registry, before and after

| | before | after |
|---|---|---|
| families bound after `import computronium` | **1** (`eqprop`, via a side-effect import) | **12**, from one table |
| families bound after `all_specs()` | 2 — *the second system's contents changed when you queried the first* | 12 — unchanged, and locked |
| places a binding is written down | 10 module tails + 1 side-effect import + 1 differently-keyed list | **1** (`families.BINDINGS`) |
| `select_backend(spec, "triton")` | inexpressible — `Backend` had two values | expressible; a wrong technology names what the spec has |
| asking "what does 'the kernel for X' mean?" | four answers (§1.5) | `status.family_of()` derives it from the kernel module's imports |
| contrastive backends | 10 classes, registered at an import nothing performed | unbound by default, one explicit function, documented why |

The status table's most useful column is the one §4.3 could not fix by
construction: `compiles` is `none` for **49 of the 54 specs that declare
`kernel_technology="triton"`**, because their `kernel.py` imports no acceleration
kernel module. `algorithm.fa` and `algorithm.pc` are the two that would be looked
for first, and both report a triton rung that nothing delivers. That is §1.4's
"54 declare triton; 7 deliver it" as a queryable column rather than a census
count — and it is the argument for §8.2 (derive the technology) rather than
trusting the field.

### 5.5 The rest of the census

| question | answer |
|---|---|
| Does triton beat torch anywhere? | **yes, at 3 of 9 sites** (§5.1) — measured 2026-09-26 |
| Is there a GPU benchmark row? | **yes** — 9 sites × 3 scales × 2 rungs in `artifacts/benchmarks/rungs/`; the 75 pre-existing rows are still all `device: "cpu"` |
| Why were there no GPU rows before? | geometries were built on CPU and never moved, so every `device="cuda"` run raised a device mismatch; fixed in §4.1 |
| `kernel.py` modules reaching a triton rung | 7 (9 call sites), behind 17 kernels |
| GPU tests covering them | 19, all passing here |
| `HAS_TRITON*` names in the tree | **0** (retired in §4.2) |
| `*KernelBackend` classes with a consumer | 0 of 13 (plus 10 contrastive, never registered) |
| `KernelRegistry` families on plain import | **12**, from one table; unchanged by `all_specs()` |
| Layer B kernels that compile | 5 of 17 with a fixture; 4 of 13 without |
| Specs declaring `kernel_technology="triton"` | 54 |
| Families where the name means more than one thing | 10 |
| Parity tests between rung *n* and rung *n-1* | **two levels** — 64 specs at `step(case)`, plus 5 kernel entry points triton-vs-torch (§4.4) |
| Native-model names silently substituted by the EqProp fallback | **2 closed** (`directed_ep`, `lemma_mlp`); 1 open (`diff_target_prop`, no factory exists) |
| Adjacent-rung defects found by §4.4 | **2** — an EqProp fallback that disagreed with its kernel, and a triton Muon rung running a retired algorithm behind a tautological test |
| Full-suite run (2026-09-26) | 4058 passed, 1 failed — one unmarked >120 s test (§4.12) |
| `PLW0717` findings | 79, opportunistic only (§7) |

---

## 6. Commands

### 6.1 Reproduce the census

```bash
uv run python scripts/probes/todo36_kernel_census.py
uv run python -m computronium.acceleration.availability --check
uv run python -m pytest tests/integration/test_triton_kernel.py \
    tests/integration/test_kernel_equivalence.py \
    tests/acceleration/test_fa_triton_dispatch.py \
    tests/acceleration/test_fa_activation_contract.py -q
```

### 6.2 The check §0.3 asks for — **exists since §4.3**

```bash
uv run python -m computronium.acceleration.status --family fa
uv run python -m computronium.acceleration.status --spec algorithm.pcalm --json
# one line per rung: spec, family, rung, technology, compiles, parity, gpu, status
```

Its absence was the clearest single measure of the confusion. It reads the spec
registry, `availability.compile_report()` and the benchmark rows, and every
column says `none` rather than guessing.

---

## 7. Explicitly not in this plan

- **`PLW0717` (79).** The remaining findings are in-function `try` blocks of
  6–70 statements whose *body* is the work. Extracting the body out of the
  `try` moves statements between two functions in the same file and produces no
  new capability; the `p2p` precedent was worth running because that extraction
  found a live crash, and this one has not been shown to. Take them as
  opportunistic work, never as a tranche (`TODO35.md` §17.5).
- **The presentation layer** (`TODO35.md` §4). A product question with no
  consumer; the next time it is raised, answer "is the absence of a watchable
  run part of why nothing needs it" first.
- **The LM lane's missing training path** (`TODO35.md` §16-4). A product
  decision — an embedding geometry, or a statement that the 5-D path is
  vision/tabular only. Named here so it is not forgotten; not scheduled,
  because it is not blocked on anything in this plan and this plan is not
  blocked on it.
- **Deleting any rung, for any reason, including a bad benchmark.** §3. A slow
  rung is a ranked rung, and a parity pair with a slow member still catches
  defects.
- **Optimising the 55 torch kernel modules as a goal in itself.** They are the
  reference the triton rung is verified against; but note §4.1's ranking may
  legitimately send effort there instead, if that is where the walltime is.

---

## 8. Improvement opportunities found while measuring (§4.1)

Written down so §4.2–§4.6 can inherit them rather than rediscover them. None is
scheduled; they are the things measuring the ladder taught us.

1. **The ratios for 7 of 9 sites are interpreter-bound, not kernel-bound.** Their
   reference rung costs ~1 ms at every scale, so the number is Python dispatch
   overhead. `rungbench` needs a `--loops N` that times N `step()` calls per
   iteration, so the fixed floor divides out and the ratio measures the rung.
   Until then, treat every non-`tile_mesh`, non-`muon` ratio in §5.1 as
   "unmeasured, both rungs at the floor".
2. **`kernel_technology` is a declaration, and it lies twice.** `predictive_settling`
   declares `torch_compile` and imports six triton kernels; `energy_minimization`
   declares `torch_compile` and pays 1.5–5× for it. §4.3 should *derive* the
   technology from what the `kernel` module actually imports — the same
   "measured, not declared" rule §4.2 applies to availability — so the field
   cannot drift from the module it describes.
3. **`pcalm/kernel.py` is a "triton" rung containing no triton.** Both branches
   call `reference.step`. It is a rung in name only, and §5.1's 1.03/0.97/1.13 is
   noise. Either §4.6 gives it real triton work or the spec should stop claiming
   a technology the module does not have.
4. **Only 7 of ~64 `cases.make_case` functions have a size knob.** The `scale`
   parameter §4.1 added is the right shape, but it is 7 copies of one idea. The
   deduplicated form is a single shared helper (a `CaseScale`/`scaled_geometry`
   in the ontology layer) that the remaining ~57 case factories call — and without
   it, no rung of those 57 can ever be compared at more than one size.
5. **19 algorithm `reference.py` modules build their geometry on CPU and never
   move it**, exactly as `pcalm` did. `pcalm` was fixed because §4.1 hit it; the
   other 18 are latent. `tests/property/test_device_hygiene_gate.py` already
   encodes "compose on CPU, then move the geometry, then step" for every
   `(dynamics × credit × update)` cell — what it does not cover is the *case
   factories*, which construct on CPU and depend on the caller moving the
   geometry afterwards. Extending that gate with "`make_case(device="cuda")`
   then `step()` raises nothing, for all 64 specs" turns §4.1's discovery into a
   standing contract. Expect it to be red on arrival; that is the point, and it is
   a *device* gate, not a compile gate, so nothing has to be deleted to satisfy it.
6. **`scripts/bench_dashboard.py` globs `artifacts/benchmarks/*.jsonl`,**
   non-recursively, so it cannot see `artifacts/benchmarks/rungs/`. Either
   `rglob` or the new rows are invisible to the one tool that reads them.
7. **`torch.compile` is a rung that has now lost twice.** Not a deletion argument
   (§3) — but the ladder should record *why* a rung is there, and 1.5–5× slower
   on micro-workloads is a reason a reader deserves to see next to the spec that
   selects it.

8. **The GPU rows are untracked, so §0.3 item 5's evidence cannot be reviewed in
   a diff.** `.gitignore` excludes `artifacts/`, and all 75 pre-existing benchmark
   rows are untracked for the same reason. For a *measurement* that is right; for
   the one measurement the plan's completion criterion names, it means the
   criterion is satisfied only on the box that produced it. Two honest options:
   un-ignore `artifacts/benchmarks/rungs/` (9 small JSONL files, the first
   benchmark evidence ever meant to be reviewed), or move the summary table that
   §5.1 already is into a committed doc and let the raw rows stay local. The
   second is cheaper and loses nothing; the first is what a reviewer would want.
9. **`triton_rung_available` falls back to "triton imports" for a family with no
   fixtures**, and says so in its docstring — but a fallback is still a weaker
   claim, and four families (`tile` and the class-built `eqprop`/`mep` kernels)
   have no fixtures and so no compile evidence from this module. §4.2 left them
   on the import check deliberately: writing their fixtures is the same work as
   §4.5's specifications, and doing it twice would be the duplication §0.2
   condemns. When §4.5 writes a torch reference for a family, the fixture should
   land in the same commit.
10. **`unfixtured_kernels()` is a hard equality against a test-local allowlist.**
    That is deliberate — it forces a decision when a kernel is added — but it
    means the allowlist lives in `tests/acceleration/test_triton_availability.py`
    while the truth lives in `availability.py`. The day a second test needs the
    census, the allowlist belongs beside the fixtures.
11. **There are now three family vocabularies, and §4.3 reconciled two of them.**
    `AlgorithmFamily` (13 values, the binding layer), spec ids
    (`algorithm.pcalm`, the ladder), and `ImplementationSpec.family` (14 values:
    `predictive_coding`, `random_feedback`, `modular`, …). The third is the odd
    one out: it is a *scientific grouping*, not an implementation name, and no two
    values in it correspond to an `AlgorithmFamily` value. The status table prints
    the derived family beside it, so the disagreement is visible; the fix is to
    decide whether `ImplementationSpec.family` means "scientific grouping" (then
    rename the field `scientific_family` and stop expecting it to align) or
    "algorithm family" (then make the values align). That is a naming decision
    with 64 edits behind it, and it belongs to whoever owns the vocabulary.
12. **`select_backend(spec, "triton")` can select a rung whose kernels do not
    compile.** It answers the spec's *declaration*, which is the right answer for
    a dispatch that must not compile anything to decide, and the status table's
    `compiles` column is where the measurement lives. But a caller that wants
    "run triton, or fall back" has to consult `availability` as well; a
    `resolve_available_rung(spec, requested)` that folds the two would be one call
    instead of two, at the cost of a dispatch that compiles kernels. Deliberately
    not done — the trade is recorded here rather than made silently.
13. **§4.12's discovery half needs the suite's walltime budget as an input.** The
    lock added in §4.12 can enforce an annotation but cannot notice a test that
    has become slow. Doing so needs one of: a `--durations` JSON written by
    `conftest.py` on every run with a committed baseline (cheap, but it makes
    every run write a file, and it will churn on any machine-speed change); a
    per-test walltime budget declared next to the test (verbose, 4000 tests); or
    a sharded suite with a per-shard budget (a real change to how CI runs). The
    first is a false-flip risk on shared hardware, the second is maintenance with
    no payoff until a test is actually slow, and the third is a decision for
    whoever owns CI. Not started; the choice is recorded rather than guessed.
14. **The zoo registry was incomplete rather than merely unlabelled**, which
    reframes §4.8: the two silent EqProp substitutions (`directed_ep`,
    `lemma_mlp`) were missing *rows*, not wrong names. One name remains —
    `diff_target_prop` — and it has no factory to point at. Before the naming
    cleanup (§8.15), someone should decide whether target propagation belongs on
    the rule lane at all; if it does, `models/native` needs a
    `create_native_diff_target_prop`, and if it does not, `_FAMILY_MODELS` should
    stop naming it and `resolve_native_model` can raise.
