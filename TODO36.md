# TODO36: One Acceleration System

**Status**: ACTIVE — open. This is the plan series' single live work list. It
absorbs the acceleration unification and everything `TODO35.md` still owed;
`TODO35.md` is closed and its §17 is the record of why the decisions below were
made.

This is a **build** plan, not an audit. `TODO34.md` made the tree fast, provable
and ready to be presented; `TODO35.md` spent four rounds making claims
executable and produced a rule about deletion the hard way. This one reduces a
*system* to one working thing.

**The rule that outranks every convenience in here:** *a kernel that does not
compile is a specification nobody wrote down, not code that should not exist.*
Nothing in this plan deletes a kernel. `TODO35.md` §17.9 is the reasoning and it
was learned in public.

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
| **A** (recommended) | **Layer A is the only training path.** Layer B shrinks to the export path it was built for; its 12 uncompilable kernels become *specifications* — recovered as torch reference expressions, then re-implemented only where §4.1 says it pays. | ~2 weeks | low: the working path is untouched |
| **B** | Layer B becomes the training path; Layer A's 9 call sites are ported onto `KernelRegistry`. | ~2 months | high: today's working path is the thing being replaced, by code that mostly does not compile |
| **C** | Both stay, documented as two systems with one entry point. | ~2 days | buys clarity, not unity. A fallback if the census says A is wrong |

**My recommendation is A**, for three reasons that are measurements rather than
preferences: Layer A has 19 passing GPU tests and Layer B has zero consumers;
Layer B's kernels do not compile (§2); and Layer B's only real customer is
`cli/export_kernel.py`, which needs a *bound backend*, not a training path.

You can overrule this after reading §1. Do not let a session start work in §4
before the choice is recorded here.

### 0.3 What "finished" means

Every item is a property of the tree that a command in §6 can check:

1. The only non-registry module referencing `KernelRegistry` is the export path.
2. One command answers "is the fast path for *family* available on this box",
   and its answer covers compilation, not just CUDA.
3. Every family name appears in exactly one registry.
4. Every triton kernel has a parity test that fails if it stops compiling.
5. `artifacts/benchmarks/` has at least one **GPU** row per reachable triton
   kernel, with the reference number beside it.
6. "The kernel for X" has exactly one referent in the codebase.
7. `scripts/broad_sweep.py` samples only knobs an arm can consume, and no
   family is skipped for want of a rule space.

---

## 1. The census

Reproduce with `uv run python scripts/probes/todo36_kernel_census.py` (§6.1).
Measured 2026-09-26, RTX 3080, triton 3.8.0, torch with CUDA. Every number is a
count; the probe is the source of truth and the numbers below are its output.

### 1.1 The two systems

| | **Layer A** | **Layer B** |
|---|---|---|
| dispatch | `acceleration/registry.py` → `select_backend(spec, "auto")` | `acceleration/kernel_backend.py` → `KernelRegistry.get_best(family, hw)` |
| unit of work | a free function in a triton module | a `*KernelBackend` class |
| declared by | 64 `ImplementationSpec`s, all with a `kernel` backend | 12 `AlgorithmFamily` members |
| registration | explicit, at import of `registry.py` | **a side effect of importing a module** (§1.3) |
| reached by | every training run | the two export CLIs, and nothing else |
| tested | 19 GPU tests pass here | none |
| compiles | yes, for the 17 kernels it reaches | 2 of 14 sampled (§2) |

The `KernelBackend` Protocol declares `initialize`, `forward`, `backward`,
`update_weights`, `get_memory_stats`, `get_settle_telemetry`. It does **not**
declare `set_model_ref`, `settle` or `compute_energy` — the three methods every
concrete backend adds and the three a caller actually needs. So the protocol
describes a shape no family satisfies, which is the same defect as §1.5's
flags: an interface that reports what it would like to be true.

### 1.2 What actually reaches a triton module

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

The other 55 are torch or `torch.compile`. That is not a criticism; it is the
shape of a system where triton is used where it pays.

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

### 1.4 The registry declares triton 54 times and delivers it 9

| query | answer |
|---|---|
| specs total | 64 |
| `status == "kernel_verified"` | 25 (39 `reference_only`) |
| `kernel_technology == "triton"` | **54** (10 declare `torch_compile`) |
| both triton-declared *and* kernel_verified | 22 |
| `kernel.py` modules that import a triton kernel | **7** (9 call sites) |

**54 specs declare triton; 7 modules deliver it.** `kernel_verified` means the
*kernel rung* is correct, and for most of the tree that rung is a torch
implementation with a triton label. `README.md:1427` reports the 25 faithfully;
what it does not say is that "triton" here is a declaration of intent, not a
description of the code path.

### 1.5 Four ways the tree says "the fast path is available", none agreeing

| source | what it actually reports |
|---|---|
| `kernel_available("triton")` | `torch.cuda.is_available()` — a GPU, not triton |
| `HAS_TRITON_PC` / `_FF` / `_SNN` / `_HEBBIAN` / `_HAS_TRITON` | triton imported — on this box all five are `True` while 12 of the 16 kernels they guard cannot be launched |
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
comparing a triton kernel against its reference. The speedup claims in
`docs/archive/20260722/` (17.9x over NanoGPT, 200x MoT) are about the
*algorithms*, not these kernels, and are not evidence for this system.

**This is the first task in §4, not a footnote.** A unification that cannot say
which half is faster is bookkeeping, and it would be bookkeeping in the one
place in the tree where "faster" is the entire justification.

---

## 2. The 16 unwired kernels, now that they are back

`TODO35.md` §17.3 deleted them on a "0 importers" inference; §17.9 reverted
that; §17.10 measured them with
`scripts/probes/todo35_r17_kernels_compile.py`. Summary, because §4.4 depends
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

**So they are specifications, and §4.4 treats them as such.** The value in
recovering them is the *intent*, which is currently unrecoverable from anywhere
else. Whether any of it is worth a triton implementation is a measurement, and
§4.1 comes first.

---

## 3. Why this plan is not "delete the unused layer"

Recorded once, prominently, because Round 5 got it wrong in public:

- **"0 importers" is not "dead."** `TODO35.md` §14.6 established this for
  documented entry points; §17.9 generalised it. An unwired implementation is a
  claim about the future, and no static import graph contains one.
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

Each step states what is true when it is done, in a form a command in §6 can
check. Do not start step *n+1* before step *n* is verified. Steps 4.1–4.6 are
the acceleration system; 4.7–4.12 are carried over from `TODO35.md` and ordered
by what they unblock here.

### 4.1 Measure first: is triton earning its place?

Because §1.6 says nobody has. For each of the 9 call sites, on a GPU, at three
input sizes: wall time of the triton path, wall time of the torch path it
guards, and peak memory. Write the rows into `artifacts/benchmarks/` in the
existing schema with `device: "cuda"` and a `backend` that says which.

- **Done when** `artifacts/benchmarks/` has GPU rows for all 9, each beside its
  reference number, and §5 records the result honestly — including any module
  where triton is *slower*, which is a result.
- **This step can end the plan.** If triton wins nowhere, the correct output is
  a short document saying so and a much smaller system, not a unified one.
  Decide that here, before writing any code.

### 4.2 One meaning for "available"

A single function, in `acceleration/`, that answers *"can the fast path for
this family run, here, now?"* and means it: the kernel imports **and compiles**.
Triton's `.warmup()` compiles without launching, so the honest flag is
"compiled once, cached", not "CUDA is present".

- Replace `kernel_available("triton")`, the five `HAS_TRITON_*` flags, and
  `KERNEL_TECHNOLOGY`-as-a-boolean with it. Callers keep working; their meaning
  stops lying.
- **Done when** `HAS_TRITON_PC` and its siblings report what they say, and a
  test asserts a flag is `False` for a kernel that does not compile (§2's
  finding is the fixture: 5 flags `True`, 12 kernels unlaunchable).

### 4.3 One registry, one dispatch, one name per family

Take outcome **A** from §0.2, or record the alternative you chose and why.

1. `KernelRegistry` becomes exactly what it was built for: **the export path's**
   registry of bindable backends. Document that in its module docstring, which
   currently describes it as if it were the training path.
2. Move the population out of a side effect, all three of them (§1.3). Either
   `register_all()` called explicitly by the export CLIs, or registration at
   import as a stated contract in one place. A registry whose contents depend
   on which module someone imported first — or on whether someone queried
   Layer A — is not a registry.
3. Give Layer B's families names that do not collide with Layer A's specs, or
   retire the colliding ones. "FF" currently means `algorithms/ff/kernel.py`
   (torch), `acceleration/ff_kernels.py` (an `FFKernelBackend`), `PEPITAKernel
   Backend` in the same file, `AlgorithmFamily.FF`, and a `ff` key in
   `get_algorithm_kernels()`.
4. Layer A keeps `select_backend`; it is the one that works and the one 19
   tests cover.

- **Done when** §0.3 items 1 and 3 hold, and §6.2 prints one unambiguous answer
  per family.

### 4.4 Recover the specifications (only if §4.1 says the families are worth it)

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

### 4.5 Then, and only then, wire

A recovered spec becomes a reachable kernel through the Layer A pattern, which
`primitives/credit_assignment/local_goodness/kernel.py` demonstrates in about
ten lines: a guarded import, an `is_available()` that means it, and a branch at
the one hot site.

- **Done when** the family appears in §0.3 item 5 with a GPU row and a parity
  test, and `select_backend` reaches it with no flag to set.

### 4.6 A kernel arm on the System pipeline

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
and it gates §4.5 for every family except those driven at the algorithm level.

### 4.7 A membership predicate for the zoo registry

`TODO35.md` §17.8-2. `backprop_parity._FAMILY_MODELS` names `standard_fa`,
`dfa_deep`, `diff_target_prop`, `fabricpc_graph_pcn`, `directed_ep` — real zoo
arms that are not learning rules, and whose comparison is meaningless on the
rule lane (it would compare one MLP against itself).
`resolve_native_model` "falls back to the EqProp composition" for any unknown
name, a silent substitution in the one place that must not make one.
`scripts/p4lite_surrogate_sanity.py` and `scripts/preliminary_run.py` need the
same thing and now raise `KeyError` naming the rules, which is louder than the
`ImportError` they replaced and no more useful.

- **First move:** `has_model(name)` on the zoo registry, then make
  `resolve_native_model` raise on a miss. This is also the prerequisite §4.5
  needs, because wiring a family means knowing which name asked for it.

### 4.8 Bring the rule spaces back in line with the arms

`TODO35.md` §17.8-3. `RULE_SPACES` has 8 keys; `_RULE_FAMILIES` names 8
families and two (`hebbian`, `spiking`) have no space, so the sweep skips them
with a warning. Fifteen of eqprop's eighteen knobs and three of fa's six are
now unsampled rather than sampled-and-ignored, because
`consumable_config_keys` derives what an arm can take from its factory
signature (`beta`, `inference_steps`, `settle_steps`, `feedback_scale` are all
real and were being discarded before Round 5 fixed the derivation).

- Either the rule systems grow a way to consume the remaining knobs, or the
  spaces shrink to what is real. **This is a product decision per rule**, and
  it is the same shape as `TODO35.md` §14.5's question: the sweep was measuring
  a tuning surface that had stopped existing.
- **Done when** §0.3 item 7 holds.

### 4.9 One name per family, in the sweep too

`TODO35.md` §17.8-4. `forward_only` and `predictive_coding` resolve to the same
pepita arm through `_family_rule_key`'s alias dict and now visibly emit
identical rows. A family whose space and propagator are the same should be one
family, or the alias should be a documented equivalence rather than a dict
entry.

- **Done when** the sweep's family count and its distinct-arm count agree, and
  the alias is either gone or named.

### 4.10 Re-measure and re-pin

`TODO35.md` §16-5. The slow tier and `docs/figures/manifest.json` have not been
re-run since Round 4. Round 5's integration pass moved no demo numerics — every
re-emitted record differed only in `provenance.git_commit` — and the record
edits were reverted rather than committed, because backfilling a pin without
the pass that verifies it is the §11.2 failure. §7's POST-SLOW step is the
thing that would verify it.

- **Done when** `run_tiered_suite.sh --with-slow` is green and the POST-SLOW
  re-pin verify step passes on a fresh pin.

### 4.11 The timeout-marker policy

`TODO35.md` §16-1, fourth round running. Five tests were marked by hand from
one `--durations` run; nothing stops the next 100s test from appearing
unmarked, and the failure mode is a `Timeout` that reads like a flake. A check
over `--durations` output is the lock this class wants, and `TODO35.md` §14.4
rule 1 held it back until a defect of that class was found by it — §15.3 found
three, so it is unblocked.

### 4.12 The knowledge layer's `__getattr__` population

`TODO35.md` §17.8-7. `knowledge/kb.py` has a module `__getattr__` whose names
the import lock treats as excluded because they are not statically derivable.
`KB` was one of them — a name that resolved to nothing. Enumerate the
population once, by hand, in the module's docstring, so the exclusion is a list
someone checked rather than a class nobody looked at.

---

## 5. Results (filled in as §4 lands; empty means not measured)

| question | answer |
|---|---|
| Does triton beat torch anywhere? | **unmeasured** (§4.1) |
| Is there a GPU benchmark row? | **no** — 75 rows, all `device: "cpu"` |
| Kernel modules reaching triton | 7 (9 call sites), behind 17 kernels |
| GPU tests covering them | 19, all passing here |
| `*KernelBackend` classes with a consumer | 0 of 13 (plus 10 contrastive, never registered) |
| `KernelRegistry` families on plain import | 1 (`eqprop`); 2 after Layer A's spec walk |
| Layer B kernels that compile | 2 of 14 sampled |
| Specs declaring `kernel_technology="triton"` | 54 |
| Families where the name means more than one thing | 10 |
| `PLW0717` findings | 79, opportunistic only (§7) |

---

## 6. Commands

### 6.1 Reproduce the census

```bash
uv run python scripts/probes/todo36_kernel_census.py
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
ask the question today. Write it in §4.2, when "available" has a meaning.

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
- **Deleting anything.** §3.
- **Optimising the 55 torch kernel modules.** They are the reference the fast
  path is measured against; making them faster makes the comparison harder to
  read, not easier.
