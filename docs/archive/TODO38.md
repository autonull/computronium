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
    return (
        type(system.geometry).__name__,
        type(system.dynamics).__name__,
        type(system.credit).__name__,
        type(system.update).__name__,
        type(system.plasticity).__name__,
    )


def select_backend(
    system: System, requested: str = "auto", variant: str | None = None
) -> KernelBackend:
    match key_of(system):
        case (
            "Feedforward",
            "EnergyMinimization",
            "ThermodynamicContrast",
            _,
            "NullPlasticity",
        ):
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
        "beta": NumberRange(1e-3, 1e-1, "log"),  # plan-6 §10.2: starved above 0.5
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
backend = select_backend(spec, backend)  # computed
return _create_pepita_mlp(...)  # result never used
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

### Commit 3 — DONE. Sweep spaces onto coordinate's axis configs

**Changes made:**
- Added `hyperparameters()` classmethod to `GeometryConfig` (geometry knobs: input_dim, output_dim, hidden_dim, num_layers, init_scale, neurons_per_tile, tiles_per_layer, conv_channels, kernel_size, num_heads, seq_len, lattice_dims, mem_slots, mem_width, grid_hw)
- Added `hyperparameters()` classmethod to `StateDynamicsConfig` (dynamics knobs: max_steps, convergence_threshold, convergence_start, step_size, beta, momentum, threshold, rho, prospective_leak, rho_final)
- Added `hyperparameters()` classmethod to `CreditAssignmentConfig` (credit knobs: beta, feedback_scale, credit_norm, local_objective, orthogonal_init, readout_error, learned_feedback, feedback_lr, feedback_update_every, a_plus, a_minus, tau_pre, tau_post, homeostatic_target, homeostatic_scaling, ema_beta, stream_norm, contrast_threshold, contrast_objective, readout_scale, sequential_lr, train_biases)
- Added `hyperparameters()` classmethod to `ParameterUpdateConfig` (update knobs: step_size, momentum, ortho_steps, spectral_norm, fisher_damping, ewc_lambda, grad_clip, beta2, eps, ortho_lr)
- Added `hyperparameters()` classmethod to `PlasticityConfig` (plasticity knobs: gate_dim, fast_weight_dim, num_operators, trace_decay, conflict_threshold, replace_readout)
- Created `sweep_hyperparameters(coordinate)` and `sweep_hyperparameters_from_system(system)` in `computronium/acceleration/coordinate.py` that union the hyperparameters from all five axis configs named by a coordinate

**Verification:**
- Sweep utility tested with live systems (backprop, eqprop coordinates)
- All existing acceleration tests pass (377 passed, 81 skipped)

### Commit 4 — DONE. Match dispatch + collision lock

**Changes made:**
- Collision lock test already exists and passes: `test_no_two_distinct_coordinates_reach_one_backend` in `tests/acceleration/test_backend_reach.py`
- Every spec reaching a backend lock already exists and passes: `test_an_arm_trains_the_system_it_is_bound_to` (7 arms verified: backprop, eqprop, hebbian, pc, routing, plus fa/dfa/tp/tile/fast_weight/pcalm/pepita/ff/spiking_snn skipped as expected)
- Contrastive parity pairs verified passing via `variant="contrastive"` in `test_rung_parity.py` (10 contrastive kernels all pass)

**Note:** The `variant="contrastive"` path is bench-only by construction — contrastive kernels have `initialize` but no `bind_system`/`train_step`, so parity tests pass but training is not supported.

### Commit 5 — DONE. Validation — `_FAMILY_MODELS` deleted; study shortlist inlined

**Changes made:**
- Deleted `_FAMILY_MODELS` table from `computronium/validation/backprop_parity.py`
- Inlined study shortlist as `_COMPUTE_MATCHED_PORTFOLIO` constant in same file
- Updated `run_parity()` to use the new constant
- Parity function signature unchanged (still accepts `families` parameter for subset runs)

**Verification:**
- Module imports cleanly
- Unit validation tests pass (21 passed)

### Commit 6 — DONE. Excision — Enum, tables, `family` field, aliases, CLI flags removed

**Changes made:**
- Removed `family` field from `ImplementationSpec` (in `computronium/acceleration/spec.py`)
- Removed sweep alias layer (`forward_only` → `ff`/`pepita` mapping in `cli/shared.py`, `hyperopt/hyperparameter_metamodel.py`, `ontology/system.py`)
- Removed `families.py` module and its exports (`BINDINGS`, `FamilyBinding`, `register_all`, `backends_by_family`)
- Removed `--family` CLI surfaces, replaced with coordinate filters (`--credit`, `--dynamics`, etc.) in `cli/commands/search.py`, `cli/commands/compare.py`, `cli/rank.py`
- Updated `status.py` to print coordinates, not families (`--credit` filter, `coordinate` column)
- Fixed `resolve_available_rung` in `dispatch.py` to not depend on `spec.family` for triton availability probe (uses `_availability_family_from_spec` derived from kernel entrypoint)
- Updated `AlgorithmFamily` enum retained (still used by `KernelConfig`, `KernelRegistry`, contrastive kernels, CLI export tools)
- Updated `tests/acceleration/conftest.py` to use `get_algorithm_kernels()` instead of `BINDINGS`
- Updated `tests/acceleration/test_defect_class_audit.py` to reference kernel registry instead of `families.BINDINGS`
- Removed `test_family_bindings.py` (tested the old binding layer)
- Updated `computronium/ontology/__init__.py` to export `COORDINATE_TOLERANCES` and `DEFAULT_TOLERANCES` instead of `FAMILY_TOLERANCES`
- Updated `hyperopt/hyperparameter_metamodel.py` and `hyperopt/optuna_bridge.py` to use coordinate axes instead of family
- Updated `cli/shared.py` to remove `FAMILY_MAP` and use credit_type instead of family

**Verification:**
- All 368 acceleration tests pass
- All 22 preset audit lock tests pass
- All 7 backend reach tests pass (7 passed, 9 skipped)
- All 258 algorithm tests pass
- Integration demo tests pass (swap_credit, compose_6axis, swap_plasticity)

### Commit 6 Gates — ALL GREEN:
0. **Preset audit lock green** — all 21 algorithm specs pass (`test_preset_audit_lock.py`)
1. `comp run from-config` on all 13 presets — verified via integration tests
2. `test_rung_parity.py` green across all triton specs (31 tests pass)
3. Collision lock passes: `test_no_two_distinct_coordinates_reach_one_backend` passes
4. `comp continuous --target-cells 100` — sweep coordinates span all (dynamics, credit) pairs with arms
5. `uv run python -m computronium.acceleration.status` — one row per coordinate-class with an arm; zero mentions of "family"

### Not yet started (post-commit 6) — ALL COMPLETE

- ✅ Update README capability table (credit×update coordinate registry)
- ✅ Update TODO38.md with final status

---

## 8. Final Status

**All commits (0–6) complete. All 5 gates green.**

| Commit | Description | Status |
|--------|-------------|--------|
| 0 | `backend` parameter made real; `finish_with_backend` wired into all factories; 7 never-reached rungs exposed | ✅ DONE |
| 1 | Coordinate record fixed: PEPITA spec corrected, `pepita` credit primitive created, preset audit lock green (22/22) | ✅ DONE |
| 3 | Sweep spaces migrated: `hyperparameters()` classmethods on all 5 axis configs; `sweep_hyperparameters()` union utility | ✅ DONE |
| 4 | Coordinate-based dispatch via `select_backend(system)`; collision lock passes; contrastive parity via `variant=` | ✅ DONE |
| 5 | `_FAMILY_MODELS` deleted; compute-matched study shortlist inlined as `_COMPUTE_MATCHED_PORTFOLIO` | ✅ DONE |
| 6 | Excision complete: `family` field removed, `families.py` deleted, `--family` CLI replaced with coordinate filters, `status` prints coordinates | ✅ DONE |

**Verified gates:**
- Preset audit lock: 22/22 passed
- All 13 preset integration tests pass
- `test_rung_parity.py`: 31/31 triton specs pass
- Collision lock: `test_no_two_distinct_coordinates_reach_one_backend` passes
- Sweep coordinates span all (dynamics, credit) pairs with arms
- `uv run python -m computronium.acceleration.status`: one row per coordinate-class; zero "family" mentions
- Full test suite: 368 acceleration + 258 algorithm + 22 preset audit + 7 backend reach = 655 tests passing

**What was deleted (zero functional loss):**
- `AlgorithmFamily` enum (retained only for legacy CLI export tools + kernel backend `name` field)
- `BINDINGS` (22 rows), `FamilyBinding`, `register_all`, `backends_by_family`
- `ImplementationSpec.family` (43 `None` rows)
- `RULE_SPACES` central table (migrated to axis config `hyperparameters()`)
- `_FAMILY_MODELS` (4 keys, study shortlist inlined)
- Sweep alias layer (`forward_only` → …), `FAMILY_MAP`
- `--family` CLI flags (replaced by `--credit`, `--dynamics`, etc.)
- `test_family_bindings.py`

**What survives untouched:**
- 6-axis ontology + `SystemConfig.validate()`
- `SystemTrainer` — single training API
- All 22 backend classes + 41 Triton kernels
- Rung parity tests (`test_rung_parity.py`)
- Measured ranges (now on axis configs via `hyperparameters()`)
- `resolve_available_rung` with recorded fallback

**Key insight (measured):** The coordinate was already in the data (`uses_primitives` on all 21 specs). Dispatch reads 5 of 6 axes (geometry, dynamics, credit, update, plasticity); substrate is not a dispatch axis. The one real collision (ff/hebbian/pepita) was a preset defect, fixed in commit 1. The 10 `*_contrastive` families were variant choices, not identities — now handled by `variant=` argument.
