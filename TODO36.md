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
comparing a triton rung against the rung below it. The speedup claims in
`docs/archive/20260722/` (17.9x over NanoGPT, 200x MoT) are about the
*algorithms*, not these kernels, and are not evidence for this system.

**This is the first task in §4, not a footnote** — but read §4.1's framing
before assuming what it is for. It ranks. It does not delete.

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

Because §1.6 says nobody has. For each of the 9 call sites, on a GPU, at three
input sizes: wall time of the triton rung, wall time of the rung below it, and
peak memory. Write the rows into `artifacts/benchmarks/` in the existing schema
with `device: "cuda"` and a `backend` that names the technology.

- **Done when** `artifacts/benchmarks/` has GPU rows for all 9, each beside its
  reference number, and §5 records the result honestly — including any site
  where triton is *slower*, which is a result and not a failure.
- **What the numbers are for:** ranking *where triton is closest to winning*,
  so §4.5 and §4.6 spend effort on the families that will benefit first. A rung
  that loses today keeps its parity pair and its place in the ladder; it moves
  down the priority list. **No measurement in this plan is an argument for
  deleting a rung** — §0.2 and §3.
- This step also settles a question §4.4 needs: whether a rung that is slower
  but bit-identical is worth promoting for verification value alone. That is a
  real trade and it deserves a recorded answer per family rather than a global
  rule.

### 4.2 One meaning for "available"

A single function, in `acceleration/`, that answers *"can the triton rung for
this family run, here, now?"* and means it: the kernel imports **and compiles**.
Triton's `.warmup()` compiles without launching, so the honest flag is
"compiled once, cached", not "CUDA is present".

- Replace `kernel_available("triton")`, the five `HAS_TRITON_*` flags, and
  `KERNEL_TECHNOLOGY`-as-a-boolean with it. Callers keep working; their meaning
  stops lying.
- **Done when** `HAS_TRITON_PC` and its siblings report what they say, and a
  test asserts a flag is `False` for a kernel that does not compile (§2's
  finding is the fixture: 5 flags `True`, 12 kernels unlaunchable).

### 4.3 Make the technology a selectable rung

This is the unification, and it is smaller than the census makes it look.

1. Extend the ladder so a rung can be *named*: `Backend` gains a
   technology-qualified form (or `select_backend` gains a `technology`
   argument) so `select_backend(spec, "triton")` is expressible and
   `select_backend(spec, "auto")` picks the highest *promoted* rung.
2. `KernelRegistry` becomes what it was built for: the **binding layer** for
   rungs that need state — `set_model_ref`, `initialize`, the export path's
   need to serialise a *bound* backend. Document that in its module docstring,
   which currently describes it as if it were the training dispatch.
3. Move the population out of a side effect, all three of them (§1.3). Either
   `register_all()` called explicitly by the export CLIs, or registration at
   import as a stated contract in one place. A registry whose contents depend
   on which module someone imported first — or on whether someone queried
   Layer A — is not a registry.
4. Give Layer B's families names that do not collide with Layer A's specs, or
   retire the colliding ones. "FF" currently means `algorithms/ff/kernel.py`
   (torch), `acceleration/ff_kernels.py` (an `FFKernelBackend`),
   `PEPITAKernelBackend` in the same file, `AlgorithmFamily.FF`, and an `ff`
   key in `get_algorithm_kernels()`.
5. Layer A keeps `select_backend`; it is the dispatch 19 tests already cover.

- **Done when** §0.3 items 1–3 hold, and §6.2 prints one unambiguous answer per
  family.

### 4.4 Cross-verification as a product: parity between adjacent rungs

The repo already verifies rung 1 against rung 0 for all 64 specs. Extend the
same machinery one rung up, so that **every family with two implementations has
a parity test between them**, and a family with three has two tests.

- This is where the user's third purpose becomes a test suite. A silent
  numerical defect in the triton rung is caught by the parity test against the
  torch rung, exactly as a defect in the torch rung is caught against the
  reference today.
- **Done when** every reachable triton rung has a parity test against the rung
  below it, recorded with the same `ParityTolerance` the spec already carries,
  and §0.3 item 4 holds.
- Where the two rungs *cannot* be made bit-identical (different reduction
  order), the tolerance is the spec's decision, recorded per family — not a
  global loosening.

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
  `resolve_native_model` raise on a miss. This is also a prerequisite for §4.6,
  because wiring a rung means knowing which name asked for it.

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

`TODO35.md` §16-1, fourth round running. Five tests were marked by hand from
one `--durations` run; nothing stops the next 100s test from appearing
unmarked, and the failure mode is a `Timeout` that reads like a flake. A check
over `--durations` output is the lock this class wants, and `TODO35.md` §14.4
rule 1 held it back until a defect of that class was found by it — §15.3 found
three, so it is unblocked.

### 4.13 The knowledge layer's `__getattr__` population

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
| `kernel.py` modules reaching a triton rung | 7 (9 call sites), behind 17 kernels |
| GPU tests covering them | 19, all passing here |
| `*KernelBackend` classes with a consumer | 0 of 13 (plus 10 contrastive, never registered) |
| `KernelRegistry` families on plain import | 1 (`eqprop`); 2 after Layer A's spec walk |
| Layer B kernels that compile | 2 of 14 sampled |
| Specs declaring `kernel_technology="triton"` | 54 |
| Families where the name means more than one thing | 10 |
| Parity tests between rung *n* and rung *n-1* | 1 level only (reference ↔ kernel) |
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
# one line per rung: family, rung, technology, compiles, parity, GPU row, status
```

Its absence is the clearest single measure of the confusion: there is no way to
ask the question today. Write it in §4.3, when a rung can be named.

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
