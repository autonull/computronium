# TODO97 — Repair First, Measure Second

**Status:** 2026-11-19 · replaces TODO96. The measurement instrument works.
The primitives do not. This plan repairs the primitive layer, then points the
instrument at it.

**Progress:** [2026-11-19] ✅ **S1–S4 COMPLETE** — Migration done, 6/6 locks pass, scaffolding deleted, cheap wiring fixed (graph batching, conv, pc_alm, EPC).
**Progress:** [2026-11-19] ✅ **S5 PARTIAL** — Graph family base box added (cora, 200 epochs), graph geometry measured on cora (val_acc=0.362 > bar 0.316), gradient credit measured on graph (val_acc=0.433). Other graph family primitives screened: feedforward geometry (0.402), euclidean/adam updates, instantaneous dynamics, digital/noisy substrates, null plasticity.

**One sentence:** Eighteen sessions built a microscope; 45 of 75 rows still
have no bound, usable result. TODO97 migrates the 563-file scaffolding into a
3-file protocol, fixes the cheap wiring defects first, calibrates the seven
missing task families, and only then screens at boxes that can answer the
question.

---

## Progress Summary

| Session | Task | Status |
|---|---|---|
| S1 | Migrate primitives to 3-file protocol + registry | ✅ DONE |
| S2 | Delete ~380 per-primitive files + generated tests | ✅ DONE |
| S3 | Verify 6 property locks pass | ✅ DONE |
| S4 | Fix cheap wiring (graph batching, conv/pc_alm/EPC probes) | ✅ DONE |
| S5 | First family base (graph) + first ladder (target_inversion) | 🔄 PARTIAL |
| S5a | Add graph family base box (cora, 200 epochs) | ✅ DONE |
| S5b | Screen graph family primitives | ✅ DONE (9 measured) |
| S5c | First ladder (target_inversion on vision) | ⏳ NEXT |
| S6 | Audit with `scripts/audit.py` | ⏳ PENDING |

---

## 1. What the last 18 sessions bought, and what they missed

| Commit range | Bought | Missed |
|---|---|---|
| `85f62ed3` → `d0869aac` | Census, screen, calibrated bar, interaction slice, deep-dive, extension path | Zero primitive fixes |
| `1f53b4d1`, `550215b0` | Legality cleanup | Zero capability fixes |
| `69c5fb09` | PEPITA reference discovery | PEPITA still `kernel_unverified`; no real kernel |

The instrument is real: one inventory, one record, one gap table, a replay
hash per row. That is worth keeping. The cost was measuring before the
primitives were ready. The map says "57 measured"; 27 of those cells vary the
companions, 11 sit at chance, and 45 rows have no bound result. The screen
records; it does not adjudicate. That was the right design for a recorder and
the wrong product for a laboratory.

**This plan changes the order, not the instrument.**

---

## 2. The corrected inventory

| Fact | Number | Source |
|---|---:|---|
| Primitives | 75 | census |
| Bound measured (vision) | 30 | map (mnist) |
| Bound measured (graph) | 9 | map (cora) |
| Inert (measures companions) | 27 | map |
| Bound at chance (<0.5) | 11 | map |
| Bound mid (0.5–0.85) | 7 | map |
| Bound clear (≥0.85) | 12 | map |
| Rows with no bound, usable result | 45 | 27 + 12 + 6 |
| Defects | 6 (5 ceilings + 1 shape) | map |
| Refused | 12 (8 family, 2 cost, 2 gaps) | map |
| Task families with a base box | 3 of 9 | `BASE_BOXES` (vision, tabular, graph) |
| Declared family rows | ~159 | sum of `task_families` |
| Source scaffolding files | 563 | 383 primitives + 96 generated + 84 algorithms |
| Source files that survive | ~1,400 | ontology 33, experiment 206, acceleration 34, core/domains/models/scripts etc. |
| Test files / functions | 579 / 3,479 | tests tree |
| Structurally duplicate test functions | 721 (21%) | AST normalization |
| Test files that never train | 464 / 579 | grep |
| Kernel files with their own `@triton.jit` | 0 / 75 | grep |
| Kernel-parity tests that pass without requiring a real kernel | 235 | pytest |

**The headline is not 57 measured. It is 39 bound (30 vision + 9 graph), 11 at chance, 45 without a
usable result. Graph family now has a calibrated base box.**

---

## 3. The cleanup: precise, ordered, reversible

The cleanup is a **migration**, not a blind delete. Do it in this order, one
commit:

### 3.1 Tag and baseline first

```bash
git tag pre-todo97
uv run python -m pytest tests/property/test_legality_compile_lock.py \
  tests/property/test_inventory_single_source.py \
  tests/property/test_binding_condition.py \
  tests/property/test_box_identity.py \
  tests/property/test_screen_has_no_verdict.py \
  tests/property/test_extension_path.py -q
```

Record the six-lock baseline. If a lock fails after the migration, revert to
the tag; do not debug forward.

### 3.2 Add the protocol before deleting the wrappers

`computronium/primitives/` survives as **three files**, not zero:

```text
computronium/primitives/
  __init__.py      # public exports
  protocol.py      # StepResult, PrimitiveSpec, PrimitiveProtocol
  registry.py      # 75 PrimitiveSpec rows; one registration per ontology class
```

The ~380 per-primitive files (`<axis>/<name>/{spec,cases,reference,kernel,__init__}.py`)
are deleted only after `registry.py` registers the same 75 ids and
`acceleration.registry` reads the registry. The six locks must pass between
the two steps.

### 3.3 Delete the scaffolding

| Path | Files | Why |
|---|---:|---|
| `computronium/primitives/*/*/{spec,cases,reference,kernel,__init__}.py` | ~380 | Spec cards + micro-cases + adapters + stubs |
| `tests/property/generated/test_primitive_*_invariants.py` | 96 | Two template bodies × 96 names |
| `tests/algorithms/*/` | 84 | Four templates × 21 algorithms |
| `build/`, `dist/`, `computronium.egg-info/` | build artifacts | Stale copies |
| `checkpoint_epoch_*.pt`, `experiment*.duckdb`, `exp_*.db`, `demo.duckdb` | artifacts | Run residue |
| `.venv/` | generated | Not source; `rm -rf`, then `uv sync --dev --all-extras` |

**Source deleted: ~560 files.** Build/venv artifacts are not source and are not
counted in the 563.

### 3.4 What survives

| Layer | Files | Why |
|---|---:|---|
| `computronium/ontology/` | 33 | The real mechanisms |
| `computronium/acceleration/` | 34 | Real Triton/CUDA kernels + dispatch |
| `computronium/experiment/` | 206 | SEC census/screen/verify + kernel |
| `computronium/core/`, `domains/`, `models/`, `nn/`, `training/` | ~400 | Trainer, tasks, compositions |
| `computronium/algorithms/` | 21 | Reference algorithms; tests consolidate to one conformance file |
| `scripts/` | 319 | Probes, scaffolds, docs generation |
| Property locks, ontology parity, integration | ~150 test files | Mechanism locks and end-to-end |

### 3.5 The protocol (one file, three types)

```python
# computronium/primitives/protocol.py
@dataclass(frozen=True, slots=True)
class StepResult:
    weights: list[torch.Tensor]
    activations: list[torch.Tensor]
    metrics: dict[str, float]
    state: dict[str, Any]

@dataclass(frozen=True, slots=True)
class PrimitiveSpec:
    id: str
    axis: Literal["credit","dynamics","geometry","plasticity","substrate","update"]
    name: str
    equations: str
    invariants: tuple[str, ...]
    task_families: tuple[str, ...]
    kernel_status: Literal["implemented","wrapper","stub","absent"] = "absent"
    ontology_class: type

class PrimitiveProtocol(Protocol):
    SPEC: PrimitiveSpec
    def make_task_case(self, task_id: str, box: dict, seed: int) -> Any: ...
    def reference_step(self, case: Any) -> StepResult: ...
    def kernel_step(self, case: Any) -> StepResult: ...
    def fingerprint(self, case: Any) -> str: ...
    def analytic_invariant(self, case: Any) -> bool: ...
```

`registry.py` holds 75 `PrimitiveSpec` rows and one generic `ReferenceAdapter`
that calls the ontology class's declared entrypoint (`step`, `forward`,
`settle`). There is no per-primitive adapter code. `make_task_case` is one
helper over `TaskRegistry` + the spec's config factory; the per-primitive
difference is data, not code.

`kernel_step` is a thin adapter to `computronium/acceleration/`. It raises when
`kernel_status == "absent"`, returns the reference when `"stub"` (for parity
tests only), and dispatches to the acceleration function when `"implemented"`.

---

## 4. Repair order: cheapest falsifier first

### 4.0 The six analytic invariant families

Every primitive gets one invariant from its axis, with a case and an expected
sign. One parameterized test per axis; no 75 handwritten tests.

| Axis | The invariant |
|---|---|
| credit | one-step pseudo-gradient cosine vs backprop, or loss decrease |
| dynamics | energy non-increase, settle convergence, or fixed-point residual |
| geometry | output shape, and one-step output differs from feedforward |
| plasticity | post-step fingerprint differs from `null`, or gate entropy |
| substrate | passivity, parameter-shift vs finite difference, or quantization bound |
| update | orthogonalization, whitening, or norm constraint |

The invariant is the first test in S1; a primitive without one is not screened.

### 4.1 One-step wiring probes

The 11 near-chance bound rows are not one problem. Split them by the cheapest
probe:

### 4.1 One-step wiring probes (hours, no ladder)

| Primitive | Probe | If it fails | If it passes |
|---|---|---|---|
| `geometry.graph` | batch node rows with `edge_index`/`batch`; forward 32 rows | fix the batched path | one-step fingerprint differs from feedforward |
| `geometry.conv` | one-step gradient vs `feedforward` on the same case | fix forward/padding | 3-point ladder (lr, width) |
| `credit.pc_alm` | one-step pseudo-gradient vs `gradient` | fix readout wiring | 3-point ladder (gamma) |
| `dynamics.error_predictive_coding` | one-step settle vs `predictive_settling` | fix target/error | 3-point ladder (beta, steps) |

These four are the cheapest and most likely to resolve the graph defect and
three of the eleven near-chance rows. Run them before any 1-epoch ladder.

### 4.2 The remaining eight: 3-point ladders

| Primitive | Primary knob | Ladder | If all fail → triage |
|---|---|---|---|
| `credit.target_inversion` | target steps, lr | 3 × 1 seed + 1 confirm | defect: target/readout |
| `credit.random_projections` | feedback scale, lr | 3 × 1 seed | capability gap: width/params |
| `credit.forward_tangent` | JVP scale, lr | 3 × 1 seed | gap: memory vs accuracy |
| `credit.zeroth_order` | perturbations, lr | 3 × 1 seed | gap: sample efficiency |
| `credit.local_contrastive` | phases, lr | 3 × 1 seed | gap: label channel |
| `credit.local_goodness` | pos/neg passes, lr | 3 × 1 seed | gap: width |
| `dynamics.spike_integration` | epochs 1/3/10, reset | 3 × 1 seed | defect: reset/decay |
| `plasticity.conflict_adaptive` | continual task, lr | 3 × 1 seed | defect: protocol |

### 4.3 The 5 ceilings: capability gaps, not defects

| Primitive | Task to measure | Box to test (not yet measured) |
|---|---|---|
| `credit.surrogate` | mnist (vision/neuromorphic) | 300k params |
| `geometry.attention` | char_ngram (sequence) | 600k params |
| `geometry.causal_transformer` | tiny_shakespeare (lm) | 600k params |
| `geometry.routing` | mnist (vision) | 300k params |
| `geometry.tile` | mnist (vision) | 1M params |

The "measured box" is a **claim to test**, not a result. Measure it, record
the cost, and publish "requires N parameters on this task". If the box cannot
fit the task, record a capability gap with the budget that closes it.

### 4.4 The 2 gaps and 2 cost caps

| Primitive | Action | Done |
|---|---|---|
| `plasticity.rule_state` | implement `modulate()`; one-step fingerprint differs from `null` | or retire with trigger |
| `plasticity.substrate_coupled` | carry substrate state through the joint transition | or retire with trigger |
| `update.natural_gradient` | diagonal Fisher or smaller model; measure 1 step then 1 epoch | cost model |
| `dynamics.diffusion` | settle steps 30 → 10; measure 1 epoch | cost model |

---

## 5. The full action register (75 primitives)

Legend: **R** reference contract, **K** kernel truth, **I** instrument,
**E** execution repair, **CAP** capability gap (measured larger box), **L**
one-step probe / ladder, **F** family base, **G** gap implement/retire, **C**
capability screen. Every row carries R+K. For inert rows the `val_acc` is the
companion's number, not a verdict on the primitive.

### Credit (19)

| primitive | status | binding | val_acc | action |
|---|---|---|---:|---|
| `eligibility_prop` | refused | — |  | R+K+F |
| `forward_tangent` | measured | bound | 0.165 | R+K+L |
| `gradient` | measured | bound | 0.894 | R+K+C |
| `homeostatic` | measured | inert | 0.135 | R+K+I |
| `hybrid` | measured | bound | 0.737 | R+K+L |
| `local_contrastive` | measured | bound | 0.199 | R+K+L |
| `local_goodness` | measured | bound | 0.340 | R+K+L |
| `local_supervision` | measured | bound | 0.777 | R+K+L |
| `pc_alm` | measured | bound | 0.122 | R+K+L |
| `pepita` | measured | bound | 0.894 | R+K+C |
| `random_projections` | measured | bound | 0.133 | R+K+L |
| `rtrl_reference` | refused | — |  | R+K+F |
| `score_function` | measured | bound | 0.732 | R+K+L |
| `surrogate` | defect | bound |  | R+K+CAP |
| `target_inversion` | measured | bound | 0.119 | R+K+L |
| `temporal_trace` | measured | inert | 0.122 | R+K+I |
| `thermodynamic_contrast` | measured | bound | 0.782 | R+K+L |
| `unbiased_rtrl` | refused | — |  | R+K+F |
| `zeroth_order` | measured | bound | 0.167 | R+K+L |

### Geometry (12)

| primitive | status | binding | val_acc | action |
|---|---|---|---:|---|
| `attention` | defect | bound |  | R+K+CAP |
| `causal_transformer` | defect | bound |  | R+K+CAP |
| `conv` | measured | bound | 0.122 | R+K+L |
| `feedforward` | measured | bound | 0.894 | R+K+C |
| `graph` | defect | bound |  | R+K+E |
| `nca` | measured | bound | 0.896 | R+K+C |
| `ntm` | measured | bound | 0.876 | R+K+C |
| `recurrent` | measured | bound | 0.897 | R+K+C |
| `routing` | defect | bound |  | R+K+CAP |
| `spatial_lattice` | measured | bound | 0.914 | R+K+C |
| `tile` | defect | bound |  | R+K+CAP |
| `tile_mesh` | measured | bound | 0.690 | R+K+L |

### Dynamics (8)

| primitive | status | binding | val_acc | action |
|---|---|---|---:|---|
| `diffusion` | refused | — |  | R+K+F |
| `energy_minimization` | measured | bound | 0.879 | R+K+C |
| `error_predictive_coding` | measured | bound | 0.124 | R+K+L |
| `instantaneous` | measured | inert | 0.894 | R+K+I |
| `lazy` | measured | bound | 0.877 | R+K+C |
| `pc_alm` | measured | bound | 0.640 | R+K+L |
| `predictive_settling` | measured | bound | 0.724 | R+K+L |
| `spike_integration` | measured | bound | 0.132 | R+K+L |

### Plasticity (8)

| primitive | status | binding | val_acc | action |
|---|---|---|---:|---|
| `closed_form_ridge` | refused | — |  | R+K+F |
| `conflict_adaptive` | measured | bound | 0.288 | R+K+L |
| `fast_weights` | measured | bound | 0.892 | R+K+C |
| `null` | measured | inert | 0.894 | R+K+I |
| `routing` | measured | bound | 0.868 | R+K+C |
| `rule_state` | refused | — |  | R+K+G |
| `substrate_coupled` | refused | — |  | R+K+G |
| `temporal_psi` | measured | bound | 0.885 | R+K+C |

### Substrate (10)

| primitive | status | binding | val_acc | action |
|---|---|---|---:|---|
| `analog` | measured | inert | 0.887 | R+K+I |
| `complex` | measured | inert | 0.891 | R+K+I |
| `digital` | measured | inert | 0.894 | R+K+I |
| `memristive` | measured | inert | 0.889 | R+K+I |
| `neuromorphic` | measured | inert | 0.878 | R+K+I |
| `noisy` | measured | inert | 0.891 | R+K+I |
| `optical` | measured | inert | 0.890 | R+K+I |
| `quantum` | refused | — |  | R+K+F |
| `sparse` | measured | inert | 0.885 | R+K+I |
| `ternary` | measured | inert | 0.871 | R+K+I |

### Update (18)

| primitive | status | binding | val_acc | action |
|---|---|---|---:|---|
| `adafactor` | measured | inert | 0.933 | R+K+I |
| `adam` | measured | inert | 0.908 | R+K+I |
| `bayesian_online` | refused | — |  | R+K+F |
| `cascade_synapse` | refused | — |  | R+K+F |
| `elastic_consolidation` | measured | inert | 0.626 | R+K+I |
| `euclidean` | measured | inert | 0.894 | R+K+I |
| `lion` | measured | inert | 0.926 | R+K+I |
| `local_adam` | measured | inert | 0.796 | R+K+I |
| `mean_norm` | measured | inert | 0.887 | R+K+I |
| `muon` | measured | inert | 0.949 | R+K+I |
| `natural_gradient` | refused | — |  | R+K+F |
| `ortho_adam` | measured | inert | 0.947 | R+K+I |
| `quantized_adam` | measured | inert | 0.102 | R+K+I |
| `riemannian_orthogonal` | measured | inert | 0.949 | R+K+I |
| `role_split` | measured | inert | 0.901 | R+K+I |
| `schedule_free` | measured | inert | 0.919 | R+K+I |
| `spectral_constrained` | measured | inert | 0.626 | R+K+I |
| `synaptic_intelligence` | refused | — |  | R+K+F |

---

## 6. Task bases and refusal mapping

### 6.1 The 9 bases

| Family | Base task | Bar | Cost | Status |
|---|---|---|---|---|
| vision | mnist | 0.106 | medium | calibrated |
| tabular | iris | 0.333 | cheap | calibrated |
| graph | cora | 0.316 | medium | add |
| sequence | char_ngram | 27.0 | medium | add |
| continual | copy_task | — | cheap | add |
| rl | cartpole | 20.0 | cheap | add |
| scientific | lorenz_state | 67.4 | cheap | add |
| neuromorphic | spiking_mnist | — | medium | add task + base |
| lm | tiny_shakespeare | 65.0 | expensive | add, pre-register |

Each base gets a 3-seed control, measured walltime, parameter budget, and
replay hash. No screen runs on a family without a base.

### 6.2 Refusal → family (8 family refusals)

| Primitive | Declared families | First screen |
|---|---|---|
| `eligibility_prop` | sequence, continual | char_ngram |
| `rtrl_reference` | sequence | char_ngram |
| `unbiased_rtrl` | sequence | char_ngram |
| `bayesian_online` | continual, sequence | copy_task |
| `cascade_synapse` | continual | copy_task |
| `synaptic_intelligence` | continual | copy_task |
| `closed_form_ridge` | continual, sequence | copy_task |
| `quantum` | scientific | lorenz_state (or a named gap) |

`task_families` becomes an explicit `TaskSpecEnriched` field; `_FAMILY_OF_DOMAIN`
is deleted. A task may serve vision and continual (`split_mnist`) or sequence
and continual (`copy_task`); the old table could not express that.

### 6.3 The 27 inert rows become explicit, not "measured"

| Axis | Instrument | Rows |
|---|---|---|
| substrate (9) | Pareto ruler: `(val_acc, bitwidth, energy, memory, spike_timing)` | bound at bitwidth 1/2/4/8 |
| update (14) | `--own-knobs` (already wired) + 3-point step-size ladder | bound at own lr |
| credit (2) | error-blind contract row on a label-free task | contract |
| dynamics (1) | non-instantaneous box | bound |
| plasticity (1) | non-null box | bound |

---

## 7. Kernel plan: only where the code exists

A reference implementation does not need a Triton kernel. The library is
honest as `reference_only`. A kernel is worth writing only where the
acceleration layer already has the primitive's math and the screen shows a
speed bottleneck.

| Primitive | Existing acceleration code | Kernel action |
|---|---|---|
| `gradient` | `backprop_kernels.py` | wrapper, verify parity |
| `random_projections` | `fa_kernels.py` | wrapper, verify parity |
| `thermodynamic_contrast` | `pc_kernels.py` | wrapper, verify parity |
| `pepita`, `local_goodness` | `ff_kernels.py` | wrapper, verify parity |
| `target_inversion` | `tp_kernels.py` | wrapper, verify parity |
| `temporal_trace` | `snn_kernels.py` | wrapper, verify parity |
| `tile_mesh` | `tile_kernels.py` | wrapper, verify parity |
| `energy_minimization`, `muon` | `mep_kernels.py` | wrapper, verify parity |
| All other 65 | none | `kernel_status="absent"`; reference only |

**Target: 10 primitives across 9 acceleration modules, not 75.** A primitive
with no acceleration code stays reference-only; that is a complete answer, not
a gap.

Kill test: monkeypatch `reference_step` to raise; a kernel test passes only
when the selected path is `implemented`. A `stub` cannot pass.

---

## 8. Test consolidation: keep the mechanism, delete the template

The target is **~150 files / ~1,300 tests**, not 40 / 800. The per-primitive
core is 75 × 3 tests; the task-family and governance suites stay.

| Group | Now | Target | Action |
|---|---:|---:|---|
| `tests/property/generated` | 96 / 182 | 1 / 75 | One parameterized invariants file |
| `tests/algorithms` | 84 / 258 | 22 / 80 | One conformance + semantic per algorithm |
| `tests/property` (locks/meta) | 195 / 1,566 | 40 / 320 | Axis contracts, legality, inventory, screen, CI |
| `tests/unit` | 92 / 896 | 30 / 300 | Schema, config, store, validation |
| `tests/integration` | 57 / 243 | 20 / 70 | One per axis pair + six-axis |
| `tests/acceleration` | 15 / 118 | 8 / 50 | Ladder, parity, kernel isolation |
| `tests/primitives` | 9 / 28 | 6 / 225 | 3 tests per primitive, one file per axis |
| `tests/acceptance` | 9 / 53 | 6 / 35 | Extension path, public API |
| `tests/ceec` | 14 / 109 | 14 / 109 | Governance; keep |
| `tests/platform` | 6 / 17 | 6 / 17 | Packaging; keep |
| Root/probes/biology | 2 / 9 | 2 / 9 | Keep |
| **Total** | **579 / 3,479** | **~155 / ~1,300** | |

The irreducible per-primitive core is 75 × 3 tests: deterministic, analytic
invariant, capability floor or contract check. The task-family suite is 9 × 10. The ontology
suite is one file per axis. Everything else is a mechanism lock, a governance
test, or deleted.

### 8.1 The five rules for a kept test

1. **Name the decision.** "It returns a dict" is not a decision.
2. **Remove the mechanism; the test must fail.** A stub that passes is a comment.
3. **One axis predicate, one parameterized test.** The data varies; the body does not.
4. **A capability test carries a control and a seed count.**
5. **A slow test buys a rung.** Otherwise the screen is cheaper.

### 8.2 The audit gate

`scripts/audit.py` exits 1 on:

- a normalized duplicate body with cluster size > 1 (allow-list: the 75
  per-primitive analytic tests, one per primitive);
- a kernel test that passes with `reference_step` monkeypatched to raise
  unless `kernel_status="implemented"`;
- an empty assertion outside the allow-list;
- a per-primitive subdirectory under `computronium/primitives/`;
- a primitive id without a `PrimitiveSpec` row;
- a task family without a `BASE_BOXES` row;
- a near-chance bound row without a ladder record.

---

## 9. Sessions, dependency-ordered

| Session | Work | Gate | Stop |
|---|---|---|---|
| **S0 Baseline** | Tag `pre-todo97`; run six locks; save output | Six locks green | Any lock red |
| **S1 Migrate** | Add `protocol.py` + `registry.py`; delete ~560 scaffolding files; update six locks | Six locks green; 75 ids registered; `comp verify` works | A lock fails; revert to tag |
| **S2 Wiring** | Fix graph batching; one-step probes for conv, pc_alm, EPC | 4 rows resolved or named defect | A probe with no named mechanism |
| **S3 Bases** | Explicit `task_families`; 7 bases; 3-seed controls; 2 gaps; 2 cost caps | 9/9 calibrated; 12/12 refusals mapped | A family without control/bar |
| **S4 Ladders** | 3-point ladders for the remaining 8 near-chance + 7 mid | 15 triaged (tuned/defect/gap) | An untriaged row |
| **S5 Screens** | Real screens on the 30 bound rows at declared families; 3 seeds | 30 rows with verdict; ~159 family rows planned | A screen on MNIST for a sequence primitive |
| **S6 Gaps** | Measure 5 ceilings at the proper task | 5 gaps with measured box and cost | A gap without a measured box |
| **S7 Kernels** | 10 wrappers to existing acceleration code; kill test; honest `absent` for 65 | 10 implemented; 0 stubs pass | A kernel with no speed/parity |
| **S8 Map + docs** | Regenerate map with verdict/rung/cost; regenerate README/method cards | 0 inert-labeled capability; docs match map | A doc row the map does not carry |
| **S9 Results** | 5 pre-registered viability claims (control-relative, 5 seeds, CI) | 5 claims with CI | A claim without pre-registration |

**S1–S3 are repair. S4–S6 are measurement. S7 is optional acceleration. S8 is
the product. S9 is the science.** No screen runs before its primitive is
wired; no ladder runs before its family has a base.

---

## 10. Definition of done

1. **75/75 primitives registered** with a `PrimitiveSpec`, a task case, an
   analytic invariant, and a fingerprint.
2. **0 inert rows labeled as capability.** 27 rows are bound, contract, or
   named gap.
3. **0 untriaged near-chance rows.** 11 rows become tuned, defect, or
   capability gap with a measured box.
4. **1 graph defect fixed.** Batched node input works; one-step fingerprint
   differs from feedforward.
5. **9/9 task families calibrated.** A base task, a 3-seed control, a bar, a
   cost, and a replay hash each.
6. **~159 declared family rows resolved**, one per `(primitive, declared
   family, box)`; 75/75 primitives carry a bound row, contract row, or named
   capability gap.
7. **10 primitives implemented across 9 acceleration modules**, 65
   reference-only with `kernel_status="absent"`; 0 stubs pass parity.
8. **~155 test files / ~1,300 tests**, 0 exact duplicate bodies, 0 stub-pass,
   0 finiteness-only test.
9. **5 viability claims**, pre-registered, 5 paired seeds, CI, control-relative.
10. **Map and docs regenerate from one source**; `scripts/audit.py` exits 0.

---

## 11. First commands

```bash
# 0. Baseline (DONE)
git tag pre-todo97
uv run python -m pytest \
  tests/property/test_legality_compile_lock.py \
  tests/property/test_inventory_single_source.py \
  tests/property/test_binding_condition.py \
  tests/property/test_box_identity.py \
  tests/property/test_screen_has_no_verdict.py \
  tests/acceptance/test_extension_path.py -q

# 1. Migrate (one commit) (DONE)
#    add computronium/primitives/{__init__,protocol,registry}.py
#    delete ~380 per-primitive files; update six locks
uv run python -m pytest tests/property/test_legality_compile_lock.py \
  tests/property/test_inventory_single_source.py \
  tests/property/test_binding_condition.py \
  tests/property/test_box_identity.py \
  tests/property/test_screen_has_no_verdict.py \
  tests/acceptance/test_extension_path.py -q

# 2. Fix the cheap wires (DONE)
#    graph batching; conv/pc_alm/EPC one-step probes
uv run python scripts/probes/test_one_step_wiring.py

# 3. First family base (graph) + first ladder (target_inversion) (NEXT)
uv run python -m computronium.experiment.sec_loop \
  --track P0 --out results/sec --own-knobs --axis credit

# 4. Audit
uv run python scripts/audit.py
```

---

## 12. What we stop doing

- Measuring before the primitive is wired.
- Publishing "57 measured" when 27 are inert and 11 are at chance.
- Calling a kernel parity test a gate when a stub can pass it.
- Running a 1-epoch screen and calling it a result.
- Adding a task family without a base box and a control.
- Writing ~380 wrapper files for 75 ontology classes.
- Generating 96 test files from 2 templates.
- Screening a sequence primitive on MNIST.
- Claiming "requires 600k params" before measuring the 600k box.
- Treating "more tests" as "more capability".

---

## 13. The rule

**No screen runs on a primitive that has not passed its analytic invariant.**
**No map row is published without verdict, rung, cost, and replay hash.**
**No kernel is claimed without a kill test and measured parity.**
**No family is screened without a calibrated base.**

The instrument is built. This plan points it at working primitives.
