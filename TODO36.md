# TODO36: One Acceleration System

**Status**: ACTIVE — open. This is a **build** plan, not an audit. It continues
`TODO35.md` (trustworthiness: four rounds of making claims executable) and
`TODO34.md` (test velocity and the presentation layer). Where those closed
defects, this reduces a *system* to one working thing.

**Why this document exists.** `computronium/acceleration/` contains two
parallel kernel systems that were built at different times, share family names,
and answer the question "what is the fast path for FA?" in two incompatible
ways. A session in Round 5 spent an hour deleting code from one of them on a
reachability scan that never established which one was live. This document
ends that ambiguity, and it starts by refusing to decide anything before
measuring.

**The rule that outranks every convenience in here:** *a kernel that does not
compile is a specification nobody wrote down, not code that should not exist.*
Nothing in this plan deletes a kernel. `TODO35.md` §17.9 gives the reasoning
and it was learned the expensive way.

---

## 0. Start here

### 0.1 The one-sentence goal

**One registry, one dispatch, one meaning for "available", one name per family,
and a measured reason for every kernel that stays.**

### 0.2 The decision this plan asks you to make, before any work

The census (§1) says there are two systems. Three outcomes are possible and
they cost very different amounts:

| | outcome | cost | risk |
|---|---|---|---|
| **A** (recommended) | **Layer A is the only training path.** Layer B shrinks to the export path it was built for, and its 16 uncompilable kernels become *specifications* — recovered as torch reference expressions, then optionally re-implemented. | ~2 weeks | low: the working path is untouched |
| **B** | Layer B becomes the training path; Layer A's 9 triton modules are ported onto `KernelRegistry`. | ~2 months | high: today's working path is the thing being replaced, by code that mostly does not compile |
| **C** | Both stay, documented as two systems with one entry point. | ~2 days | buys clarity, not unity. A fallback if the census says A is wrong |

**My recommendation is A**, for three reasons that are measurements rather than
preferences: Layer A has 19 passing GPU tests and Layer B has zero consumers;
Layer B's kernels do not compile (§3); and Layer B's only real customer is
`cli/export_kernel.py`, which needs a *bound backend*, not a training path.

You can overrule this after reading §1. Do not let a session start work in
§4 before the choice is recorded here.

### 0.3 What "finished" means

Every one of these is a property of the tree, checkable by a command in this
document, not a feeling:

1. `grep -rc "KernelRegistry" computronium/ | grep -v ":0"` returns **one**
   consumer, and it is the export path.
2. A single command answers "is the fast path available for FA on this box",
   and its answer covers compilation, not just CUDA.
3. Every family name appears in exactly one registry.
4. Every triton kernel in the tree has a parity test that fails if the kernel
   stops compiling.
5. `artifacts/benchmarks/` contains at least one **GPU** row per triton kernel
   that is reachable, with the reference number beside it.
6. The phrase "the kernel for X" has exactly one referent in the codebase.

---

## 1. The census (measured 2026-09-26, RTX 3080, triton 3.8.0, torch+CUDA)

Reproduce with the commands in §6.1. Every number below is a count, not a
judgement.

### 1.1 The two systems

| | **Layer A** | **Layer B** |
|---|---|---|
| dispatch | `acceleration/registry.py` → `select_backend(spec, "auto")` | `acceleration/kernel_backend.py` → `KernelRegistry.get_best(family, hw)` |
| unit of work | a free function in a triton module | a `*KernelBackend` class with `initialize`/`set_model_ref`/`settle`/`compute_energy`/`backward`/`update_weights` |
| declared by | 64 `ImplementationSpec`s, all with a `kernel` backend | 10 `AlgorithmFamily` entries |
| registration | explicit, at import of `registry.py` | **a side effect of importing a module**; see §1.3 |
| reached by | every training run | the two export CLIs, and nothing else |
| tested | 19 GPU tests pass here | none |
| compiles | yes, for the 9 modules that reach it | 2 of 14 sampled kernels (§3) |

### 1.2 What actually reaches a triton module

64 modules named `kernel.py` live under `algorithms/` and `primitives/`. Of
those, **9 reach a triton module**:

```
algorithms/pcalm/kernel.py
primitives/credit_assignment/local_goodness/kernel.py
primitives/credit_assignment/random_projections/kernel.py
primitives/geometry/tile_mesh/kernel.py
primitives/state_dynamics/energy_minimization/kernel.py
primitives/state_dynamics/pc_alm_settling/kernel.py
primitives/state_dynamics/predictive_settling/kernel.py
acceleration/kernels.py                      (EqPropKernel)
mep/optimizers/strategies/update.py          (Muon)
```

covering `triton_kernels.py` (6), `fa_kernels.py` (2), `pcalm_kernels.py` (1),
`tile_kernels.py` (7) and `compile.py` (1) — **17 kernels, all compiling, all
exercised by 19 passing GPU tests.**

The other 55 are torch or `torch.compile`. That is not a criticism; it is the
shape of a system where triton is used where it pays.

### 1.3 Layer B has no consumer, and its registry is populated by a side effect

- **0 of 10 `*KernelBackend` classes has a consumer.** Every one is referenced
  only by its own `KernelRegistry.register(...)` line and its own `__all__`.
- **`KernelRegistry` holds 1 family after `import computronium`.** The other 9
  register inside a `for hw in HardwareTarget:` loop at the bottom of their
  module, so they exist only once that module is imported.
- **The only thing that imports them is
  `acceleration.get_algorithm_kernels()`** — and both call sites discard its
  return value, with the comment *"populate the registry (lazy import side
  effect)"*. A function whose value is thrown away, called for a global side
  effect, is the mechanism. Its callers are `cli/export_kernel.py` and
  `cli/export_trained_kernel.py`, and nothing else in the tree.

So: `KernelRegistry.get_best(AlgorithmFamily.PC, ...)` returns `None` in any
process that has not run an export CLI.

### 1.4 The registry declares triton 54 times and delivers it 9

The `ImplementationSpec`s carry their own acceleration state, and it is the
first thing a reader checks:

| query | answer |
|---|---|
| specs total | 64 |
| `status == "kernel_verified"` | 25 (39 are `reference_only`) |
| `kernel_technology == "triton"` | **54** (10 declare `torch_compile`) |
| both triton-declared *and* kernel_verified | 22 |
| modules that actually import a triton kernel | **9** |

**54 specs declare triton; 9 modules deliver it.** A `kernel_verified` status
means the *kernel rung* is correct, and for most of the tree that rung is a
torch implementation with a triton label on it. `README.md:1427` reports the 25
faithfully; what it does not say, and what the table makes obvious, is that
"triton" here is a declaration of intent rather than a description of the code
path.

### 1.5 Four ways the tree says "the fast path is available", none agreeing

| source | what it actually reports |
|---|---|
| `kernel_available("triton")` | `torch.cuda.is_available()` — a GPU, not triton |
| `HAS_TRITON_PC` / `_FF` / `_SNN` / `_HEBBIAN` / `_HAS_TRITON` | triton imported — on this box all five are `True` while 12 of the 16 kernels they guard cannot be launched |
| `KERNEL_TECHNOLOGY` on 41 primitives | a string. 34 of the 41 never import a triton kernel |
| `spec.supported_backends` containing `"kernel"` | a torch implementation exists |

Four names, one question, four answers, and the two that claim the most are the
two that know least. This is the `cpu_only` defect and the `HAS_TRITON_*`
defect and the `KERNEL_TECHNOLOGY` defect — the same class three times, and
`TODO35.md` §0.1 says the fix belongs in the code, once, at the boundary.

### 1.6 No speedup has ever been measured

`artifacts/benchmarks/*.jsonl` holds **75 rows**. Every one is
`"backend": "kernel", "device": "cpu"`. There is no GPU row, and no row
comparing a triton kernel against its reference. The speedup claims in
`docs/archive/20260722/` (17.9x over NanoGPT, 200x MoT) are about the
*algorithms*, not about these kernels, and are not evidence for this system.

**This is the first task in §4, not a footnote.** A unification that cannot say
which half is faster is bookkeeping, and it would be bookkeeping in the one
place in the tree where "faster" is the entire justification.

---

## 2. What the 16 unwired kernels are, now that they are back

`TODO35.md` §17.3 deleted them on a "0 importers" inference; §17.9 reverted
that; §17.10 measured them. Summary, because the work in §4.4 depends on it:

| group | count | failure | fix |
|---|---|---|---|
| triton API renames (`libdevice.sigmoid`, `tl.cosh`) | 3 | moved since they were written | mechanical |
| launch shape `tl.dot` refuses (K ≥ 8/16) | 2 | block config vs the contraction | mechanical |
| index / orientation / contraction disagree with a reference | 7 | **the intended maths exists only as this code** | spec first |
| correct today | 2 | `_lif_step_kernel`, `_ff_goodness_kernel` (matches its docstring to 1.9e-5) | — |

The seven are the interesting ones. I tried the cheap fix on
`_pepita_error_modulation_kernel` — `tl.dot` → `tl.sum(err[:, None] * fb,
axis=0)`, the textbook outer product — and it compiled, ran, and was still
**1.76 off** the torch reference, because the operands load in opposite
orientations and only one of them carries a batch stride. Three things had to
be reconciled at once, with no oracle to check against.

**So they are specifications, and §4.4 treats them as such.** The value in
recovering them is the *intent*, which is currently unrecoverable from
anywhere else. Whether any of it is worth a triton implementation is a
measurement, and §4.1 comes first.

---

## 3. Why this plan is not "delete the unused layer"

Recorded once, prominently, because Round 5 got it wrong in public:

- **"0 importers" is not "dead."** `TODO35.md` §14.6 established this for
  documented entry points; §17.9 generalised it. An unwired implementation is
  a claim about the future, and no static import graph contains one.
- **A lint rule is not authority over what ships.** The deletion was motivated
  by `PLW0717` counting a `try` block. Removing the *policy duplication* (six
  modules each guarding their whole body with `try: import triton`) is free and
  worth doing; removing the contents was not, and the extraction is available
  without the deletion.
- **The tree is full of reachable-looking dead code that is not dead.**
  `TODO35.md` §14.6 found five "0-importer" modules that `README.md` documents
  as runnable entry points, and nearly deleted them.

---

## 4. The work, in order

Each step states what is true when it is done, in a form a command can check.
Do not start step *n+1* before step *n* is verified.

### 4.1 Measure first: is triton earning its place?

**Because §1.5 says nobody has.** For each of the 9 modules that reaches
triton, on a GPU, at three input sizes: wall time of the triton path, wall
time of the torch path it guards, and peak memory. Write the rows into
`artifacts/benchmarks/` in the existing schema with `device: "cuda"` and a
`backend` that says which.

- **Done when** `artifacts/benchmarks/` has GPU rows for all 9, each beside its
  reference number, and `TODO36.md` §5 records the result honestly — including
  any module where triton is *slower*, which is a result.
- **This step can end the plan.** If triton wins nowhere, the correct output is
  a short document saying so and a much smaller system, not a unified one.
  Decide that here, before writing any code.

### 4.2 One meaning for "available"

A single function, in `acceleration/`, that answers *"can the fast path for
this family run, here, now?"* and means it: the kernel imports **and compiles**.
Triton's `.warmup()` compiles without launching, so the honest flag is
"compiled once, cached", not "CUDA is present".

- Replace `kernel_available("triton")`, the five `HAS_TRITON_*` flags, and
  `KERNEL_TECHNOLOGY`-as-a-boolean with it. Callers keep working; their
  meaning stops lying.
- **Done when** `HAS_TRITON_PC` and its siblings report what they say, and a
  test asserts that a flag is `False` for a kernel that does not compile
  (`TODO35.md` §17.10's finding is the fixture: 5 flags `True`, 12 kernels
  unlaunchable).

### 4.3 One registry, one dispatch, one name per family

Take outcome **A** from §0.2, or record the alternative you chose and why.

1. `KernelRegistry` becomes exactly what it was built for: **the export
   path's** registry of bindable backends. Document that in its module
   docstring, which currently describes it as if it were the training path.
2. Move the population out of a side effect. `get_algorithm_kernels()` must
   either register on import as a stated contract, or be replaced by an
   explicit `register_all()` the export CLIs call. A registry whose contents
   depend on which module someone imported first is not a registry.
3. Give Layer B's families names that do not collide with Layer A's specs, or
   retire the colliding ones. "FF" currently means `algorithms/ff/kernel.py`
   (torch) *and* `acceleration/ff_kernels.py` (a `FFKernelBackend` with two
   uncompilable kernels) *and* `AlgorithmFamily.FF`.
4. Layer A keeps `select_backend`; it is the one that works and the one 19
   tests cover.

- **Done when** §0.3 items 1 and 3 hold, and the §6.2 command prints one
  unambiguous answer per family.

### 4.4 Recover the specifications (only if §4.1 says the families are worth it)

For each of the 7 kernels whose intent is unrecoverable: **write the torch
expression it is meant to equal, first, as a test.** Then either make the
kernel match that expression or record that the expression is unimplementable
in triton and why. Do not port from the kernel to the test — the kernel is
what is in question.

- **Done when** each of the 7 has a named torch reference in the test suite, and
  the kernel either matches it or has a written reason it cannot.
- **FF is the pilot**: `_ff_goodness_kernel` already compiles and is correct to
  1.9e-5, so only its contrastive update is in question, and FF is a family
  with a real reference in `algorithms/ff/`.

### 4.5 Then, and only then, wire

A recovered spec becomes a reachable kernel through the Layer A pattern, which
`primitives/credit_assignment/local_goodness/kernel.py` demonstrates in about
ten lines: a guarded import, an `is_available()` that means it, and a branch at
the one hot site.

- **Done when** the family appears in §0.3 item 5 with a GPU row and a parity
  test, and `select_backend` reaches it with no flag to set.

### 4.6 The one thing Layer B cannot do yet, and shares with the export CLI

`TODO35.md` §17.8-1: a `System` trains through
`core.pipeline.run_train_step`, which has **no kernel arm**.
`dispatch_train_step` reaches a backend by reading `model._kernel_backend` off
an `nn.Module`, and a `System` has no such attribute. Separately,
`KernelBackend.set_model_ref` is a per-family contract — a `list[nn.Linear]` for
FF and SNN, `(layers, activation)` for PC, a tile algorithm for TILE — so
"bind a System's geometry" is not one call.

Until both exist, `cli/export_trained_kernel.py` is a documented refusal
(named in `test_undefined_name_lock.py`'s `KNOWN_BLOCKED`) and no family can be
accelerated *through a composed System*. This is the single largest piece of
work in the plan and it gates §4.5 for every family except those driven at the
algorithm level.

---

## 5. Results (filled in as §4 lands; empty means not measured)

| question | answer |
|---|---|
| Does triton beat torch anywhere? | **unmeasured** (§4.1) |
| Is there a GPU benchmark row? | **no** — 75 rows, all `device: "cpu"` |
| How many of the 64 kernel modules reach triton? | 9 |
| How many GPU tests cover them? | 19, all passing here |
| `*KernelBackend` classes with a consumer | 0 |
| Layer B kernels that compile | 2 of 14 sampled |
| Families where the name means two things | 10 |
| Specs declaring `kernel_technology="triton"` | 54 |
| Modules that deliver it | 9 |

---

## 6. Commands

### 6.1 Reproduce the census

```bash
uv run python scripts/probes/todo36_kernel_census.py   # to be written, §4.3
COMPUTRONIUM_RECORD_RESULTS=0 uv run python scripts/probes/todo35_r17_kernels_compile.py
uv run python -m pytest tests/integration/test_triton_kernel.py \
    tests/integration/test_kernel_equivalence.py \
    tests/acceleration/test_fa_triton_dispatch.py \
    tests/acceleration/test_fa_activation_contract.py -q
```

### 6.2 The check §0.3 asks for, and which does not exist yet

```bash
uv run python -m computronium.acceleration.status --family fa
# one line: family, registry, triton module, compiles, GPU row?, parity test
```

Its absence is the clearest single measure of the confusion: there is no way to
ask the question today.

---

## 7. Explicitly not in this plan

- **`TODO35.md`'s open items** (§17.8: the LM lane, the timeout-marker policy,
  the zoo registry's missing membership predicate, the rule spaces two rounds
  out of date). They stay there. This plan is not a place to park them.
- **The presentation layer** (`TODO35.md` §4), which is a product question and
  still has no consumer.
- **Deleting anything.** §3.
- **Optimising the 55 torch kernel modules.** They are the reference the fast
  path is measured against; making them faster makes the comparison harder to
  read, not easier.
