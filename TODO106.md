# TODO106 — Property-shard repair

## Scope
`tests/property` was 192 failed / 2722 passed / 51 skipped / 30 xfailed / 4 xpassed
(22m47s). This session rebuilt the invariant-test generator on the real case
builder; `tests/property/generated` is now **186 passed / 6 failed** (5m49s).
The remaining 48 failures are enumerated below with a named cause and a fix
(6 generated + 21 gallery + 21 single-lock).

**State at hand-off**

| Area | Before | Now |
|---|---|---|
| `tests/property/generated` | 192 failed | 6 failed, 186 passed |
| gallery provenance lock | 21 failed | 21 failed (env drift) |
| single-file locks | 19 failed | 19 failed |
| other (`test_protocol_seams`, `rng_seed`, …) | included above | included above |
| **total remaining** | **192** | **48** |

---

## A. Landed this session (do not redo)

**A1. The generator emits the real case protocol.**
`scripts/generate_property_tests.py` emitted `cases.make_case(seed=seed)` and
`call(case)` for every row. Primitive rows expose `build_case(spec, seed=...)`
and `step(spec, case)` instead (`computronium/primitives/cases.py:307`,
`:463`), so every primitive module died with
`AttributeError: module 'computronium.primitives.cases' has no attribute 'make_case'`.
The generator now takes the spec into `_run` and picks the protocol from the
reference module (`_case_shape`); algorithm rows keep `make_case`/`step(case)`.
96 modules were regenerated (`uv run python scripts/generate_property_tests.py`).

**A2. `cases.py` reads the runtime axis segment.**
`spec.axis` is the spec label (`credit_assignment`, `state_dynamics`,
`parameter_update`); the config field and every `match` arm use the runtime
segment (`credit`, `dynamics`, `update`). The one declared map is
`computronium.acceleration.spec.axis_segment`; `cell_config`, `build_case`,
`_payload`, `step` and `invariant` now call it, and the companion list compares
against the same value.

**A3. The case falls back to the family task's shape on demand.**
A graph geometry needs the task's `edge_index` and a lattice needs a spatial
input; neither can exist on the micro `(4,)` vector. `cell_config` tries the
micro shape first and only on failure computes `task_shape`/`task_instance` for
the primitive's family task. Graph rows now compose and their two invariant
tests pass. (The lattice still refuses: see B1.2.)

**Verified:** `uv run python -m pytest tests/property/generated -q` → 186 passed,
6 failed.

---

## B. Remaining failures — cause → fix → verify

### B1. Generated invariant tests (6)

**B1.1 `primitive.substrate.complex` ×2 — a declared-impossible row is run.**
`cases.IMPOSSIBLE["primitive.substrate.complex"] = "complex_substrate_real_compute"`;
`build_case` raises `PrimitiveImpossibleError` and the generated test treats it
as a failure. The refusal is already locked by
`tests/primitives/test_primitive_contract.py:130`.
**Fix:** in `_render`, when `spec.id in IMPOSSIBLE`, emit a module-level
`pytestmark = pytest.mark.skip(reason="impossible: <constraint>")` (one module
per row survives, so the inventory stays complete) — or emit the refusal test
itself (`pytest.raises(PrimitiveImpossibleError, match=constraint)`).
**Verify:** `pytest tests/property/generated -q` → the complex row skips, 0 failures.

**B1.2 `primitive.geometry.spatial_lattice` ×2 — `lattice_dims` is never supplied.**
`computronium/experiment/kernel/_geometry_builders.py:572` raises
`ValueError: spatial_lattice topology requires lattice_dims: (depth, height, width)`
because neither the coordinate params nor the geometry mapping carries it.
Probe (2026-11-26) confirms: adding `geometry.lattice_dims=[1,28,28]` to the
coordinate params composes a legal cell.
**Fix:** in `_geometry_mapping` (or `_fit_geometry`), fill a topology's required
topology params from that geometry's own declared config defaults
(`GeometryConfig.<topology>()` fields, the same source `_build_axis_box` reads) —
never a table beside it.
**Verify:** generated spatial_lattice 2 tests; also fixes
`test_param_budget_lock.py::test_a_ceiling_bounds_every_trainable_geometry[spatial_lattice]`.

**B1.3 `nca` and `plasticity.rule_state` ×1 each — nondeterminism.**
`test_deterministic_under_fixed_seed` digests differ between two `_run(spec, seed)`
calls (`out.weights[...]` mismatch). Two builds under one seed must be identical,
so the reference path draws from a global RNG or mutates shared state between
calls. The invariant is correct; the mechanism is the defect.
**Fix:** find the unseeded draw (nca's update mask; rule_state's carried buffer)
and route it through the case's `torch.Generator` (`_generator(seed, device, k)`),
or reset the buffer in `step`. Keep the invariant unchanged.
**Verify:** the two modules; then `pytest tests/property/generated -q` → 0 failed.

### B2. Gallery provenance lock (21)

`test_env_sha256_is_a_digest_of_this_environment` recomputes
`sha256(capture_environment() - git_commit)`; the records were emitted under
driver `620.70.06`, the host now reports `620.73.04`. The numbers did not move
(`config_sha256` still matches), only the environment key.
**Fix (sanctioned):** re-emit the demo records in *this* environment
(`uv run python -m pytest tests/integration/ -m demo -q`), then re-render the
manifest (`uv run python -m computronium.experiment.surface.cli gallery
--output docs/figures`). Budget one demo gate; never hand-edit `env_sha256`.
**Decision to make:** the lock's own docstring calls a widened key set without a
re-emit "exactly the gap §1.5 names", so the alternative — dropping the driver
version from the digest — is a policy change, not a fix. Either re-emit, or state
the rule change in the lock.
**Verify:** `pytest tests/property/test_gallery_provenance_lock.py -q`.

### B3. Two code defects

**B3.1 `void_rules_learned.py:31` — `existing_void_rules` is undefined (F821).**
`ADD_RULES` is empty today, so the loop body never runs and only the static
lock fires; a regenerated `ADD_RULES` would crash with `NameError`.
**Fix:** keep the registered 4-tuple keys on the registry
(`DefectRegistry.register_void_pattern` appends `(a1, v1, a2, v2)`) and read that
set; or delete the dead body and record why (`# TODO: removal needs a registry
API`). Prefer the registry change — it is the one source.
**Verify:** `pytest tests/property/test_undefined_name_lock.py -q`.

**B3.2 `acceleration/coordinate.py:34` — dead import.**
`ImportError: cannot import name 'AlgorithmFamily' from
'computronium.acceleration.spec'` breaks `test_lockstep_parity`.
**Fix:** delete the import and the fields that used it (the symbol no longer
exists), or restore the symbol if a row still declares it. One source decides.
**Verify:** `pytest tests/property/test_lockstep_parity.py -q`.

### B4. Fixture/API drift (mechanical, minutes each)

**B4.1 `GeometryConfig.conv()` gained required kwargs.**
Signature is now
`(*, input_dim, output_dim, conv_channels, kernel_size=3, in_channels, input_hw, pool_hw, init_scale=0.1)`.
`test_registry_completeness_lock.py:251` and `test_settling_layer_lock.py:34`
call it bare. **Fix:** pass the declared arguments (a tiny helper that builds a
legal conv config belongs in one place both locks read).
**Verify:** both files.

**B4.2 `test_capability_rung_lock.py:91` — message drift.**
Expects `"the row is refused"`; the code now says
`"refused by name: geometry=graph cannot read delayed_cue's input shape (10,)"`.
**Fix:** assert the named-refusal contract (prefix `"refused by name:"` plus the
reason), not a sentence that moved.
**Verify:** `pytest tests/property/test_capability_rung_lock.py -q`.

**B4.3 `test_identity_cards_drift_lock.py:44` — 39 card lines drifted.**
**Fix:** `uv run python scripts/generate_identity_cards.py` and re-run the lock.
**Verify:** the lock.

**B4.4 `test_rng_seed_lock.py:143` — unseeded value assertions.**
Five files assert numeric values without seeding:
`tests/property/test_hybrid_parity.py` (3 tests),
`test_recurrent_geometry_lock.py`, `test_surrogate_credit_lock.py`,
`tests/unit/core/test_cl_credit_arms.py`.
**Fix:** `torch.manual_seed(0)` before the first draw in each (the lock's own
instruction).
**Verify:** the lock.

### B5. Behavior locks that need a decision (not a mechanical fix)

| Lock | Symptom | Question to decide |
|---|---|---|
| `test_budget_truncation_lock` ×2 | `wave.py:1491` `SimpleNamespace` has no `geometry` | the cost model reads a task object that lacks `geometry`; pass the geometry or default it explicitly |
| `test_regression_target_lock:166` | `assert not composes("recurrent")` fails | a recurrent geometry now composes on a time-major input: stale lock, or compose matrix regression? |
| `test_regression_target_lock:229` | target_inversion's hidden gradient ≠ the lock's formula | mechanism changed on purpose? update the formula's derivation or restore it |
| `test_search_space_diverse_sampling_lock:71` | no legal cell in the first 50 of production-map | ordering/filter drift, or an over-narrow space |
| `test_objective_breadth_lock:77` | `('quantum_circuit_learning', 'fidelity')` unmeasured | declare the payload key measured, or drop it |
| `test_policy_generation_lock` ×4 | round_robin_grid / synthesis proposals refused or timeout (`_dynamics.py:1509`, filelock 120s) | proposal legality (grid needs a grid) and a per-cell budget inside the policy test |
| `test_wp11_surface_lock:78` | redelivery no longer raises `DuplicateMeasurementError` | dedup key changed: which field was dropped? |
| `test_hyperparameter_effect_lock:229` | "composition ignored the swept width" | a geometry width knob does not reach sizing: route it, or withdraw the knob |
| `test_lint_count_ratchet:118` | 660 findings > 580 baseline at ruff 0.17.5 | fix ~80 findings, or re-baseline `BASELINE` and `RUFF_VERSION` together (deliberate) |

---

## Ordering (cheapest decisive first)

1. **B1.1** skip the impossible row (generator, minutes) → generated 4/6 green.
2. **B1.2** lattice params from config defaults (one function) → generated
   6/6 green and `param_budget[spatial_lattice]` green.
3. **B3.1 / B3.2** undefined name + dead import (minutes).
4. **B4.x** fixture drift (minutes each).
5. **B1.3** determinism (investigation, domain).
6. **B5** decisions, one commit each, each with the rule it changes.
7. **B2** gallery re-emit (expensive; one demo gate at round close).

## Verification ladder

```bash
# the repaired shard
uv run python -m pytest tests/property/generated -q                    # expect 192 passed
uv run python -m pytest tests/property/test_gallery_provenance_lock.py -q
uv run python -m pytest tests/property/test_undefined_name_lock.py \
  tests/property/test_lockstep_parity.py \
  tests/property/test_registry_completeness_lock.py \
  tests/property/test_settling_layer_lock.py \
  tests/property/test_capability_rung_lock.py \
  tests/property/test_identity_cards_drift_lock.py \
  tests/property/test_rng_seed_lock.py -q
# round close, once
uv run python -m pytest tests/property -q -rf --tb=line > logs/property_<date>.log 2>&1
```

Expect the ruff ratchet to move as B3/B4 land: re-run
`pytest tests/property/test_lint_count_ratchet.py` after each group.

## Notes

- Commit per group (generated / code defects / fixtures / gallery), never one
  mega-commit; each group's lock is the evidence in its message.
- The `pytest -m demo` gate is the only writer of gallery records; do not edit
  `docs/figures/manifest.json` by hand.
- `tests/primitives` runs slower than its quoted 14s: `cell_config` composes a
  full cell per spec (measured 6.3s for `primitive.geometry.conv`). If it needs
  to be cheaper, cache the composed config per `(spec, task)` (already `@cache`)
  and avoid the family-shape fallback for laws that never need it (it is lazy
  today).
