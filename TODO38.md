# TODO38: The Coordinate Is the Key

**Status**: ACTIVE. Supersedes TODO37.

---

## 0. The Finding (measured 2026-09-27)

"AlgorithmFamily" exists for one reason: **`BINDINGS` is a dict, and dicts need keys.**
It is not an ontology concept. The six axes already specify everything a backend
needs to know. We built a parallel vocabulary because a string key was easier
than a match, then duplicated the key five times.

Measured state of the five tables:

| Table | Actual size | What it really is |
|---|---|---|
| `AlgorithmFamily` | 23 values | The dict key |
| `BINDINGS` | **22 rows** | family → backend class (`pcalm` has none — a silent gap) |
| `ImplementationSpec.family` | 21 algorithm specs, **43 `None`** | Reverse link, mostly unset |
| `RULE_SPACES` | ~9 rules | **Measured working regions** (probe-tuned ranges), not derivable structure |
| `_FAMILY_MODELS` | **4 keys** | Shortlist for one compute-matched parity study — never a per-family table |

The last two were overstated in TODO37's framing. The first two are the real
duplication. All of it can go, at zero functional loss, per §1.

### 0.1 Feasibility, measured — the coordinate is already in the data

Every one of the 21 algorithm specs carries `uses_primitives`, naming its exact
axes. **No new fields are required**; the coordinate is already recorded:

| algorithm | `uses_primitives` | family |
|---|---|---|
| `backprop` | instantaneous_pass, **reverse_mode**, euclidean | backprop |
| `fast_weight` | instantaneous_pass, **reverse_mode**, euclidean, **fast_weight** | o1memory |
| `eqprop` | **energy_minimization**, thermodynamic_contrast, euclidean | eqprop |
| `directed_ep` | energy_minimization, **random_projections**, euclidean | eqprop |
| `diffusion_eqprop` | **diffusion**, thermodynamic_contrast, euclidean | eqprop |

The dispatch key is therefore **5 axes**: (geometry, dynamics, credit, update,
plasticity). Geometry *is* read — `tile` is `backprop`'s coordinate plus
`tile_mesh`, and both matter. Substrate remains the one non-dispatch axis
(`ternary_eqprop`/`sparse_eqprop` differ only there and share a backend).

**The audit found one real collision and it is a preset defect** (§4 commit 0):
`ff`, `hebbian`, `pepita` all record `local_goodness` + `instantaneous_pass` +
`euclidean`, but the factories compose LocalGoodness (FF), Pepita (PEPITA), and
— wrongly — LocalGoodness for hebbian too. Family was disambiguating specs that
disagree with their own factories.

Three consequences, all of which shrink the plan:

1. **Dispatch reads 5 of the 6 axes** — (geometry, dynamics, credit, update,
   plasticity). Only `Substrate` is not read: `ternary_eqprop` and
   `sparse_eqprop` differ only in substrate and correctly share one backend.
2. **The collision test is decidable.** `backprop` and `fast_weight` differ in
   *only* plasticity; `eqprop` and `directed_ep` in *only* credit; `tile` and
   `backprop` in *only* geometry. If a pair cannot be separated by the 5 axes,
   it genuinely needs one backend — and the audit (§4 commit 0) exists because
   the one pair that failed this test did so because a preset was wrong.
3. **10 of the 22 bindings are not coordinate-derived.** The `*_contrastive`
   families (`fa_contrastive`, …) are an orthogonal *variant* choice, not an
   algorithm identity. In the new design a variant is an argument
   (`select_backend(system, variant="contrastive")`), not a family — which
   removes 10 enum values and 10 rows for free.

### 0.2 A claim in TODO37 that was false

`pcalm` is in the enum, has **no** `BINDINGS` row, and its `kernel.py` returns
`reference_step(case)` in **both** branches while declaring
`KERNEL_TECHNOLOGY = "triton"`. TODO37 §4.6 recorded this as "PCALM triton rung
wired to call primitive settling kernel". That claim was false: the triton work
exists in the *primitive*, and the algorithm rung runs reference code. Nothing
was lost — it was never written. §4.6's checkbox was wrong, and a checkbox that
was never earned is the same defect class as a rung that cannot be selected.

**Nothing else was lost.** Audit of the last 40 commits: `_ns_gram_kernel` /
`_ns_update_kernel` were renamed to `_ns5_*` *and* extended with a new
`_ns5_square_kernel` (TODO37 §4.14's naive→quintic Muon replacement);
`computronium/ceec/*` was extracted to `packages/ceec-core` with `import ceec`
still resolving; 41 `@triton.jit` kernels are live and every other removed
kernel name still exists in exactly one module.

---

## 1. The Design

### Dispatch: the match is the registry

```python
# computronium/acceleration/dispatch.py
DispatchKey = tuple[str, str, str, str, str]
# geometry, dynamics, credit, update, plasticity — substrate is not a dispatch axis

def key_of(system: System) -> DispatchKey:
    """The 5 axes dispatch reads. Substrate is not one of them."""
    return (type(system.geometry).__name__,
            type(system.dynamics).__name__,
            type(system.credit).__name__,
            type(system.update).__name__,
            type(system.plasticity).__name__)

def select_backend(system: System, requested: str = "auto",
                   variant: str | None = None) -> KernelBackend:
    match key_of(system):
        case ("Feedforward", "EnergyMinimization", "ThermodynamicContrast", _, "NullPlasticity"):
            return EqPropKernelBackend()
        case ("Feedforward", "InstantaneousPass", "ReverseMode", _, "NullPlasticity"):
            return BackpropKernelBackend()
        case ("TileMesh", "InstantaneousPass", "ReverseMode", _, "NullPlasticity"):
            return TileKernelBackend()
        # ... one arm per backend; contrastive handled by `variant`, not a key
```

- The match arms **are** `BINDINGS`. Each names only the axes that backend reads.
- `AlgorithmFamily`, `BINDINGS`, `FamilyBinding`, `ImplementationSpec.family`,
  and the 10 `*_contrastive` enum values — **deleted**.
- Rung selection (`reference` vs `kernel`) stays a separate, orthogonal function:
  *which implementation* is a different question from *which algorithm*, and
  TODO37 §4.18's `resolve_available_rung` already answers it with a recorded
  fallback. It keeps working; only its key derivation changes.
- `uses_primitives` is the source for `key_of` when dispatching from a spec
  rather than a live system, so the spec and the system cannot disagree.

### Sweep: knobs declared where they are implemented

`RULE_SPACES` holds measured working regions (e.g. eqprop's `lr ~ 0.05–0.1,
beta ~ 0.01–0.1`, from TODO plan-6 §8.6 probes). **These migrate, they do not
vanish** — and the union is over the coordinate's *axis configs*, not its
primitives alone: `backprop`'s space is `learning_rate, weight_decay,
hidden_dim, num_layers`, and the last two are geometry knobs. The plan §1
statement "the primitives' own hyperparameters" was wrong by half. A knob's
owner is the axis config that reads it.

```python
# on the primitive/dynamics class that owns the knob
@classmethod
def hyperparameters(cls) -> dict[str, NumberRange | DiscreteChoice]:
    return {
        "beta": NumberRange(1e-3, 1e-1, "log"),      # plan-6 §10.2: starved above 0.5
        "max_steps": NumberRange(5, 100, "int"),
    }
```

The sweep proposes a coordinate and unions the `hyperparameters()` of the
primitives it names. A knob the arm cannot consume becomes unrepresentable by
construction — TODO37's phantom-knob lock (§8.14, `exceptions.py`) is then a
property of the design, not a check that must be maintained.

### Validation: parity against the same coordinate's reference rung

The kernel rung's baseline is the **reference rung of the same coordinate** —
that is what a rung means, and `test_rung_parity.py` already tests exactly this
pair. `_FAMILY_MODELS` is deleted; its one consumer (the C1 compute-matched
study) keeps an explicit 4-name list where the study lives.

---

## 2. What Survives Untouched

- The 6-axis ontology and `SystemConfig.validate()`
- `SystemTrainer` — one training API
- All 22 backend classes and their Triton kernels
- Rung parity tests (`test_rung_parity.py`) — unchanged in content
- The measured ranges in `RULE_SPACES` (migrated, attributed to their probes)
- `resolve_available_rung` and its fallback-with-reason contract

## 3. What Is Deleted

`AlgorithmFamily`, `BINDINGS`, `FamilyBinding`, `ImplementationSpec.family`,
`RULE_SPACES` (as a central table), `_FAMILY_MODELS`, the sweep alias layer
(`forward_only` → …), `backends_by_family`, and every `--family` CLI surface,
replaced by `--credit X --dynamics Y` filters.

---

## 4. Commit Sequence

**0. Make `backend` real, or delete the parameter.** The audit of the dispatch's
call sites found that all 14 public factories do this:

```python
backend = select_backend(spec, backend)   # computed
return _create_pepita_mlp(...)            # result never used
```

`create_pepita_mlp(backend="kernel")` trains the **reference** implementation,
silently, while its docstring promises the accelerated rung. The dispatch layer
is decoration at every public entry point — which is why the family vocabulary
could drift for weeks without anyone noticing: **nothing reads it.** The wiring
to fix this already exists (TODO37 §4.7's `attach_kernel_backend()`); the
factories just never call it. Fix: one shared helper
(`finish_with_backend(system, spec, requested)`) called from every factory;
`backend="auto"` keeps its conservative meaning (kernel only when
`triton_rung_available`), so CPU boxes are unaffected. **Risk, named:** this
commit converts invisible defects into visible ones — rungs that were never
reached may fail their first real attach. That is the commit working, not
failing, and the parity suite is what tells us which.

**1. Fix the coordinate's record, then trust it.** The audit found the collision
the design depends on is real, and it is a *preset* defect, not a spec defect:

- `create_hebbian_mlp` composes `LocalGoodnessCredit` — byte-identical to FF.
  Its docstring says "neurons that fire together, wire together", but the code
  trains FF. The spec records the same wrong axes, so spec and factory agree
  with each other and both contradict the algorithm. TemporalTraceCredit (STDP)
  exists and the SNN factory uses it. Fix: hebbian preset composes
  `TemporalTraceCredit`, and the spec follows the fixed factory.
- `algorithm.pepita` spec says `local_goodness`; its factory composes
  `PepitaCredit`. Spec is wrong. Fix the spec.
- Then audit all 21: `uses_primitives` ≡ what the factory composes, asserted by
  a lock that builds each preset and reads back the composed axes. This lock
  would also have caught the false `pcalm` checkbox (§0.2): spec says triton,
  factory must reach a non-reference rung.

**3. Sweep spaces onto the coordinate's axis configs.** Move each `RULE_SPACES` entry to the owning
class's `hyperparameters()`. Sweep unions from coordinates. Old table becomes a
thin compatibility read, then dies. *No dispatch change yet — fully reversible.*

**4. Match dispatch + collision lock.** `select_backend(system)` switches to
coordinate matching, keyed on the 5 dispatch axes read from `uses_primitives`
(commit 0's lock guarantees they match the factories). Locks, in this order:
- **No coordinate resolves to two arms** (the decidable test §0.1 makes possible:
  any pair the 5 dispatch axes cannot separate must share one backend).
- **Every one of the 21 algorithm specs reaches a backend** — closes the
  `pcalm` no-binding gap from §0.2 by giving it a real arm or deleting the claim.
- Contrastive parity pairs keep passing via `variant=`, proving the 10 removed
  enum values cost nothing.

**5. Validation.** `_FAMILY_MODELS` deleted; study shortlist inlined. Parity
pairing stays coordinate-local.

**6. Excision.** Enum, tables, `family` field, aliases, CLI flags removed;
`status` prints coordinates; README capability table updated. Specs' 43
`family=None` rows: field gone, nothing to migrate.

Each commit: all 9 tiers green before landing.

---

## 5. Gates

0. **Preset audit lock green** — for all 21 algorithm specs, the axes the spec
   records ≡ the axes the factory composes. Every hebbian run trains STDP, not
   FF. (Closes the ff/hebbian/pepita collision and the pcalm lie.)
1. `comp run from-config` on all 13 presets — each trains, and hebbian's
   training curve is no longer identical to ff's
2. `test_rung_parity.py` green across all 54 triton specs
3. Collision lock passes: every valid coordinate → exactly one arm
4. `comp continuous --target-cells 100` — proposed coordinates span every
   (dynamics, credit) pair that has an arm, and every knob sampled is one the
   arm's primitives declared
5. `uv run python -m computronium.acceleration.status` — one row per
   coordinate-class with an arm; zero mentions of "family"

---

## 6. Not In This Plan

Pydantic spec validation, `KernelBackend` base class, hypothesis audit —
TODO37 leftovers, all deferred. None of them blocks using the system; all of
them assume the dispatch shape this plan first establishes. Layering them on
top of the family vocabulary would have meant doing them twice.

---

## 7. Progress Ledger

### Commit 0 — DONE. `backend` is real, and it found seven never-reached rungs

`select_backend(spec, backend)` was computed and dropped by all 21 public
factories. `finish_with_backend(system, spec, requested, variant=…)` now resolves
the rung, attaches the backend, and returns the system; every factory ends there.

**Two deviations from the plan, both forced by measurement.**

1. **The match landed in commit 0, not commit 4.** The plan had commit 0 look the
   class up by `spec.family` and commit 4 replace that with coordinate matching.
   Doing it in that order would have *attached* `EqPropKernelBackend` to
   `directed_ep` and `O1MemoryEPv2KernelBackend` to `fast_weight` — algorithms
   the family table says are EqProp and O1Memory and are neither. A wrong
   algorithm is worse than no kernel, so the coordinate gates the attach from the
   first commit and commit 4 is now only the lock plus the table's removal.
2. **`select_backend_class` is keyed on a live system, not on `uses_primitives`.**
   17 of 21 algorithm specs name only 3 of the 5 dispatch axes, so a spec-side
   key has empty slots. The key is the ontology's own discriminators
   (`topology_type`/`dynamics_type`/`credit_type`/`update_type`, plus a plasticity
   class name reduced to its short form), so it needs no table and no second
   vocabulary. `JointSystem` has a real 6th axis; `System` has 5, and an absent
   plasticity reads `null` — the same word `NullPlasticity` reduces to.

**The finding the plan predicted, in numbers.** Nine byte-identical copies of
`_extract_layers(geometry)` looked for `nn.Linear` submodules the ontology's
geometries do not have, found nothing, and let every backend train a *private*
copy of the network. `create_eqprop_mlp(backend="auto")` reported
`{'loss': 1.38, 'accuracy': 0.17}` while `geometry.params` stayed bit-identical:
plausible metrics for weights the system never read. `linear_views(geometry)` in
`kernel_backend.py` is the single replacement — views, not copies, so an in-place
update from either side is visible to the other.

Fixes that followed from making the branch live (each was a never-executed line):

| defect | fix |
|---|---|
| `EqPropKernelBackend._sync_layer_from_kernel` called, never defined | defined; the missing mirror of `_sync_layer_to_kernel` |
| `MEPKernelBackend.bind_system` stored `geometry.transition_modules`, a **method** | `linear_views` — `hasattr` cannot tell a method from a value |
| `O1MemoryEPv2KernelBackend.bind_system`, same bug | `linear_views` |
| `TPKernelBackend.bind_system` needed `geometry.layers`, which does not exist | `linear_views` + `_transposed_inverse` |
| `PEPITAKernelBackend.train_step` passed labels where the output error belongs | `target - std_output`, so `error @ Bᵀ` has a shape |
| `_JointSystem` (6-D) had no `attach_kernel_backend` | added; the frozen dataclass sets the field through `object.__setattr__` |

**Arms that stand** (attach, step, and move the system's parameters —
`tests/acceleration/test_backend_reach.py`): **backprop**, **eqprop**, **pc**,
**routing/mep**, plus `hebbian`'s `temporal_trace` arm, verified by hand and
unreachable until commit 1 moves the hebbian preset off FF.

**Coordinates left with no arm**, each running the reference rung with a logged
reason. Not deleted — the classes and their triton kernels are untouched; what is
missing is the adapter's *training path*:

| coordinate | why there is no arm |
|---|---|
| `fa` / `dfa` | `train_step` calls `backward_contrastive(acts, acts)`, so the contrastive delta is identically zero: the rung runs and updates nothing |
| `pepita` | `backward(acts, errs)` vs `backward(self, activations, error)` — no contrastive delta at all |
| `tp` | `compute_targets` returns a per-layer list; `forward_inverse` takes one target and a layer index. `train_step` bridges neither |
| `spiking_snn` | `stdp_update` is called without the `[B, N, T]` spike trains it indexes with |
| `fast_weight` | `O1MemoryEPv2KernelBackend.train_step` calls `compute_update`, never defined |
| `tile` | `TileKernelBackend` wants `geometry.tile_algorithm`; `TileGeometry` has neither it nor `tile_mesh`, so it would return `loss: 0.0` forever |
| `ff` | `_FFSystem` keeps its own layer stack, optimizers and classifier and copies the geometry once; a backend updating the geometry would train weights the preset stopped reading |
| `directed_ep`, `diffusion_eqprop` | genuinely unaccelerated coordinates; both specs already say `reference_only` |
| `pcalm` | no `PCALMKernelBackend` exists; `pcalm/kernel.py` returns `reference_step` in both branches — TODO38 §0.2's false checkbox, now enforced by the lock |

**A new collision the plan did not have:** `fa` and `dfa` compose *byte-identical*
coordinates (feedforward / instantaneous / random_projections / euclidean / null).
They differ in algorithm, not in axes, so the decidable test says they need one
backend — and `dfa/kernel.py` is a stub that returns `reference_step`, as
`fa/kernel.py` also is. Sharing the FA arm is truthful for both, so the lock
requires one arm per coordinate rather than one per algorithm.

Gate status: `tests/acceleration` + `tests/algorithms` 630 passed / 81 skipped;
new lock 6 passed / 10 skipped.

### Commit 1 — DONE. Coordinate record fixed, preset audit lock green

**Changes made:**
- Fixed PEPITA algorithm spec: changed `uses_primitives` from `primitive.credit_assignment.pc_alm` to `primitive.credit_assignment.pepita` (matches factory's `PepitaCredit`).
- Created `primitive.credit_assignment.pepita` primitive with spec, reference, kernel (fallback), cases, and registration.
- Updated `_CREDIT_TO_PRIMITIVE` mapping in `test_preset_audit_lock.py` to map `"pepita"` credit type to `"primitive.credit_assignment.pepita"`.
- Hebbian factory already used `TemporalTraceCredit` (spec already matched) — no change needed.
- All 21 algorithm specs pass the preset audit lock (`test_preset_audit_lock.py` green).

**Verification:**
- `tests/property/test_preset_audit_lock.py` — 22 passed
- `tests/property/test_params_moved.py` — 33 passed, 1 skipped
- `tests/acceleration/test_all_implementations.py` — all pepita primitive tests pass
- `tests/algorithms/hebbian/` + `tests/algorithms/pepita/` — 26 passed
- `tests/acceleration/` — 377 passed, 81 skipped

### Not yet started

Commits 3, 4, 5, 6 (unchanged from §4). New observations that bear on them:

- **§0.1's claim that all 21 specs name their exact axes is wrong for 17 of them** —
  each names 3 of 5. Commit 1's lock asserts *truth* (every named axis matches
  what the factory composes), not completeness, until the records are completed.
- **The 3-id rename is still the cheapest bridge**: `instantaneous_pass` →
  `instantaneous`, `reverse_mode` → `gradient`, `pc_alm_settling` → `pc_alm` would
  make `uses_primitives` speak the ontology's vocabulary exactly, after which
  `coordinate_of(spec)` becomes derivable and the spec/system agreement check
  needs no table at all.
- **Commit 1's hebbian fix is now load-bearing for the kernel rung.** Composing
  `TemporalTraceCredit` moves hebbian onto the `temporal_trace` arm, which
  `HebbianKernelBackend` does satisfy (4/4 params move, verified by hand).
- **Gate 5 (`status`) still prints families** and `resolve_available_rung` still
  keys its triton-availability probe on `spec.family`, so commit 6 must touch
  `availability.py`, not just `families.py`.
- **The `variant="contrastive"` path is bench-only by construction**: the ten
  contrastive kernels have `initialize` but no `bind_system`/`train_step`, so
  commit 4's "contrastive parity pairs keep passing via `variant=`" holds for
  parity tests and cannot hold for training.
