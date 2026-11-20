# TODO97 — Repair First, Measure Second

**Status:** 2026-11-19 · replaces TODO96. The measurement instrument works.
The primitives do not. This plan repairs the primitive layer, then points the
instrument at it.

**Progress:** [2026-11-20] ✅ **S7 CLOSED (ten primitive kernels; four algorithm xfails filed)** — ten `PrimitiveSpec` rows are `kernel_status="implemented"` with an entrypoint, a technology and microbench evidence (`artifacts/benchmarks/<id>.jsonl`): `gradient` (backprop), `random_projections` (FA), `thermodynamic_contrast` (PC), `pepita`/`local_goodness` (FF), `target_inversion` (TP), `temporal_trace` (SNN), `tile_mesh` (tile), `energy_minimization`/`muon` (MEP). Each is a wrapper in `computronium/primitives/kernels.py` over its acceleration module; the other 65 stay `absent`, which is a complete answer. The kill test (`tests/acceleration/test_primitive_kernel_kill.py`) patches `ReferenceAdapter.reference_step` to raise: all 75 rows pass — an implemented row returns its step, an absent row refuses by name, an impossible row is quiet only through its refusal test. Defects fixed on the way: `_resolve_step` imported the module's parent and missed `computronium.primitives.kernels`; `acceleration.registry` mapped the primitive rung through a promotion-name table that had no `"implemented"` key, so `dispatch.auto` never selected a primitive kernel; `microbench` built a deleted per-primitive `cases` module instead of `primitives.cases.build_case`; FA's contrastive pass compared the free phase with itself (every delta zero) and built one feedback matrix for two layers; SNN passed a list as `post_spikes` and reported the settle's empty telemetry as a zero-loss step. **S7b (filed, not closed):** four algorithm factories still `xfail` in `test_backend_reach.py` — `ff` (its preset cannot take a backend, `_attachable` names why), `fast_weight` (no fast-weight kernel), `pcalm` (no PC-ALM backend class), `tile` (its backend expects a `_tile_algo` the geometry does not carry); `fa`/`dfa`, `pepita`, `tp` and `spiking_snn` now attach and move the system's own parameters. `scripts/audit.py` exits 0.

**Progress:** [2026-11-20] ◐ **S8 PARTIAL (docs regenerate from one source; LM delta run)** — the method cards (`comp method-card`) no longer carry a second axis table: `_get_axis_registries` projects the 75 `PrimitiveSpec` rows, so a class added to an axis cannot be missing from the docs. `docs/sec/map.md` is regenerated from `results/sec/map.json` with the map's own status vocabulary (`measured`, `unimplemented`, `defective`, `refused`), so the one unimplemented row is counted instead of dropped. The README counts are generated tokens: `implementation_count`, `kernel_verified_count`, `primitive_kernel_count`, `algorithm_kernel_count`; the acceleration panel now reads 96 implementations (75 primitives + 21 algorithms), 24 kernel-verified (10 primitives + 14 algorithms), and the ontology panel reads 75 primitives (from the registry, not `AXES_REGISTRIES`). The LM delta run re-screened its 11 pre-fix defects: 6 became refusals, **5 remain** — `forward_tangent`, `surrogate`, `zeroth_order`, `fast_weights`, `routing` die on the token lane with shape/dtype errors and are filed as `token_lane` under `test_a_language_task_declares_its_token_lane`. That lock is too broad for the class: it is a geometry refusal test, while these five are credit/plasticity token-shape facts. **Next in S8:** narrow the lock, file the credit/plasticity token-shape class with its failing test, and re-run the LM delta; `scripts/audit.py` already exits 0.

**Progress:** [2026-11-20] ✅ **S5h CLOSED (defect classes filed; the row-state gate repaired)** — the six classes the family screens found are now evidence, not prose. Three closed as **refusals in the declared space** (a capability that works): `sec_loop._is_legal` now applies the planner's own three rules (`_is_geometry_task_compatible`, `_target_lane_rule`, `_batch_layout_rule`), so three time-major credits on `cartpole`/`copy_task`, `nca` on a 21-feature task, and `causal_transformer` on a flat classifier are refused by name instead of dying at train time; `nca` gained its grid branch in the geometry×task table. Three remain **defective with a strict-xfail lock**: the language token lane (14 rows on `tiny_shakespeare`/`char_ngram`), `ntm`'s double backward (1 row on `cartpole`), and the family ceiling (6 rows, already locked in S6). The 47 defect rows were re-derived: 26 became `refused` with the rule that refuses them, 21 carry `defect_class` + `failing_test` from the new one register (`sec_loop.DEFECT_LOCKS`). **The gate was dead**: the screen wrote `defect` and `scripts/audit.py` compared `defective`, so `row_without_lock` and `impossible_without_lock` could never fire; `computronium/experiment/sec_status.py` is now the one row-state source (writer, gate, tests), and its necessity test fails when a defective row omits its lock. `scripts/audit.py` exits 0 (full, reading the nine maps).

**Progress:** [2026-11-20] ✅ **S5 SCREENS COMPLETE (vision + graph) and S6d CLOSED** — the vision map now accounts all **52 declared rows**: **45 measured** (37 bound, 8 inert), **4 defective** (the param-box overruns `credit.surrogate` 234,898 / `geometry.attention` 494,986 / `geometry.routing` 234,898 / `geometry.tile` 628,280 over the 150,000 vision ceiling), **26 refused** (family mismatch or unavailable). The graph map accounts **9/9 declared rows measured** (gradient 0.402, feedforward 0.402, graph 0.362 on cora); the other 66 rows are refused at the graph box, so no graph screen remains. **Eight ladder records** (up from the five S6b wrote): `local_contrastive` **tuned** (readout_scale 10 → 0.4018) and `random_projections` **tuned** (feedback_scale 0.1 → 0.3764); `forward_tangent` 0.1653, `pc_alm` 0.1224, `target_inversion` 0.1137, `geometry.conv` 0.1217 and `error_predictive_coding` 0.0980 and `quantized_adam` 0.0999 stay inside the near-chance band and are `unimplemented` with strict-xfail locks. Three instrument defects surfaced and are fixed with locks: `update_map` **dropped the `ladders` table** on every P0 write (`test_a_screen_keeps_the_ladder_table`); the ladder was **credit-only** (axis from the spec id, base from the row's measured box, axis-aware record validation; `test_the_ladder_sweeps_the_primitive_own_axis`); and `LADDER_KNOBS` named fields the update/plasticity/substrate configs do not declare (`step_size`/`momentum`, `trace_decay`, `noise_level`/`sparsity`; `test_the_knob_table_names_the_axis_own_fields`). `sec_ladder --dry-run` no longer runs the cells it printed. **S6d**: `capability_skip` reads an f-string's constant text and reports a reason it cannot read; the 14 findings are closed — 9 rungless factories are `xfail` with the S7 close, the credit-adapter sources are constructed instead of skipped, declared rows say `declared:` literally, and the dead finite-difference test (0 collected params over deleted modules) is deleted. `scripts/audit.py --static` reports **0 findings**.

**Progress:** [2026-11-19] ✅ **S3b COMPLETE (the calibration gate)** — all nine family bases measured at their declared boxes over `CONTROL_SEEDS=3`, each with bar, cost and replay hash (`results/sec/pilot.json`; 9/9 calibrated, and 9/9 controls clear their bar). The calibration exposed four defects, all fixed: `BASE_COORDINATES` was a second source of the base axes (deleted; `BASE_BOXES[*].base_coordinate` is the one source, read by the calibration, screens, P3 and P4); `tiny_shakespeare` declared `(100,)` while its loader emits 128 tokens; the LM base ran on the default MLP instead of its declared causal transformer; the RL base declared recurrent geometry with gradient/instantaneous dynamics, which cannot compute recurrent grads (now feedforward). Added `spiking_mnist` (MNIST frames as binary spike rasters) because the neuromorphic base named a task that did not exist. `Calibration` now carries the `PassBar`, so perplexity and loss bars clear from below (`has_power` reads `clears_task_bar`); the P0/P3 power checks use the same rule. `scripts/probes/todo97_s3b_calibration.py` reproduces the sweep. Open defect: the graph base composes at 200,967 parameters over its 200,000 ceiling because an explicit `geometry.hidden_dim` bypasses `_fit_geometry`; the failing test is `test_the_graph_base_fits_its_declared_ceiling` (strict xfail).

**Progress:** [2026-11-19] ✅ **S5d COMPLETE (the hard gate)** — `ReferenceAdapter` is real: `make_task_case` builds the axis micro-case from a composed `SystemConfig`, and `reference_step` runs the law through `cases.step`, with no exception swallowed anywhere. `computronium/primitives/cases.py` is the one case/step layer (one builder and one step per axis; the per-primitive difference is data). The declared space is now the legality oracle through `_compiled_void_constraints`, so a law that only runs beside a particular companion gets that companion: credit laws on recurrent/module geometry, sequence credits on a time-major batch, diffusion on a settled geometry. Green: `tests/primitives` 666 passed / 152 declared skips; contract suite 519 passed / 2 declared no-op skips; parity 14 passed / 150 declared absent-kernel skips; the six property locks + the extension path 71 passed. Deleted `test_primitive_wiring.py` (~284 duplicate rung-0 tests, 12 capability skips) — the adapter contract plus the six axis contracts carry the same rungs. Fixed along the way: `update_pseudo_grads` emitted one gradient per parameter instead of one per learnable weight (the credit contract's order); `SystemConfig.validate` now refuses a diffusion settling on a time-major geometry (measured crash in `_compute_interaction_energy`); the plasticity dispatch is one `plasticity_from_config`; `_credit_from_config` is the one credit dispatcher.

**Progress:** [2026-11-19] ✅ **S6c COMPLETE (the audit reads all 13 predicates)** — the six completeness predicates landed in `scripts/audit.py`: `capability_skip`, `impossible_without_lock`, `quiet_row_without_lock`, `unaccounted_row`, `claim_count_mismatch`, `compatibility_alias`. A skip names the environment, or the row's own declaration (`declared:`), and nothing else. `--static` now reports **0 findings**: the seven-finding queue (below) closed, and the environment markers are matched case-insensitively (`triton`, `CuPy`, `CPU fallback`, `no --experiment-db`), so a tool-less skip names the tool and only a capability skip names a missing mechanism. `unaccounted_row`, `claim_count_mismatch`, and `impossible_without_lock` stay 0.

**Progress:** [2026-11-19] ✅ **S6c QUEUE CLOSED (audit --static exits 0)** — the six biology capability skips are gone. The two weight-transport tests now build the native FA System (`create_native_fa_mlp`; `RandomProjectionsCredit` B ≠ Wᵀ with separate storage) instead of the legacy `TileAlgorithm(algorithm="fa")`, which carries no feedback matrices; the energy-descent test asserts its step count; adaptive FA is `xfail(strict=True)` naming the missing `B ← B + η·δ·aᵀ` rule. `_FAMILY_OF_DOMAIN` is deleted: `TaskSpecEnriched.task_families` is the one declaration, populated for all 30 tasks (`split_mnist`: vision+continual, `copy_task`: sequence+continual, `tiny_shakespeare`/`char_ngram`: sequence+lm), `refusal_for` compares family **sets** (one shared family composes), and `base_family` picks the family whose base box is the task. Green: biology 6 passed / 3 xfailed; the six locks + pilot + boundary + all-implementations 226 passed / 79 skipped / 3 xfailed / 3 xpassed.

**Progress:** [2026-11-19] ✅ **S6b COMPLETE (the full audit exits 0)** — `computronium/experiment/sec_ladder.py` runs each near-chance row's 3-point ladder at its own primary knob, 1 seed per rung plus one confirmation seed at the best point, and writes one record into the map's `ladders` table (verdict, rungs, best, cost, replay hash). The knob comes from the active space (`harvest_schema().active`), not a factory signature (D13); the plan's per-primitive knobs are declared in `PRIMARY_KNOBS`. Measured: **`local_contrastive` tuned** (readout_scale 10, 0.402) and **`random_projections` tuned** (feedback_scale 0.1, 0.376) — each is a coordinate, one knob clear of the near-chance band 0.200. **`forward_tangent` (0.185), `pc_alm` (0.122), `target_inversion` (0.114)** stay inside the band: `unimplemented`, with the missing mechanism and a strict-xfail lock (`tests/property/test_ladder_record_lock.py`, 10 passed / 3 xfailed). `scripts/audit.py` (full, not only `--static`): **0 findings**. Note for S8: `results/` is an artifact (gitignored), so the map gate runs locally; CI carries the schema lock only.

**Progress:** [2026-11-19] ✅ **S1–S4 COMPLETE** — Migration done, 6/6 locks pass, scaffolding deleted, cheap wiring fixed (graph batching, conv, pc_alm, EPC).
**Progress:** [2026-11-19] ✅ **S5 PARTIAL** — Graph family base box added (cora, 200 epochs), graph geometry measured on cora (val_acc=0.362 > bar 0.316), gradient credit measured on graph (val_acc=0.433). Other graph family primitives screened: feedforward geometry (0.402), euclidean/adam updates, instantaneous dynamics, digital/noisy substrates, null plasticity.
**Progress:** [2026-11-19] ✅ **S5c TRIAGED** — target_inversion on vision is **unimplemented**: feedback alignment / learned inverses are missing, so the transpose feedback vanishes (val_acc=0.119 ≈ chance 0.10). Works on graph (0.68 @ 6 epochs). The failing lock is the ladder cell; the close condition is a feedback-alignment primitive.
**Progress:** [2026-11-19] ✅ **S4 COMPLETE (extended)** — All 75 primitives pass Rung 0 wiring tests (284 tests, 16 skipped). Created `tests/primitives/test_primitive_wiring.py` covering: instantiate, forward pass, pseudo-gradients (finite & non-zero for error-aware), settle convergence. 6/6 property locks still pass.
**Progress:** [2026-11-19] ✅ **S6a AUDIT GATE INSTALLED** — `scripts/audit.py` implements the seven structural §8.2 predicates (duplicate test bodies, empty assertions, per-primitive subdirectories, primitive-without-spec, family-without-base, near-chance-without-ladder, kernel-stub-pass). Static checks are green; it reports the 5 unimplemented ladders (S6b). The five completeness predicates are specified in §8.2 and land in **S6c**.
**Progress:** [2026-11-19] ✅ **S3 BASES DECLARED** — `TASK_FAMILIES` (9) is now the one family universe, and `BASE_BOXES` carries a row for every family (sequence, continual, rl, scientific, neuromorphic, lm added). Calibration controls (3 seeds, bar, cost, replay hash) closed in S3b (above).
**Progress:** [2026-11-19] ✅ **S2b MIGRATION REPAIR** — Removed the stale per-primitive `kernel_entrypoint`/`kernel_technology` tables (they pointed at deleted modules); `kernel_status` now uses the protocol vocabulary (`absent`, 75/75) until S7. Repaired the four algorithm kernels that imported deleted primitive modules, the `rungbench` per-package sites, and the registry config/ontology name bugs (`PepitaCredit`, `ParameterUpdateConfig`, `GeometryConfig.recurrent`, `SubstrateConfig.optical`).

**Progress:** [2026-11-19] ✅ **S0 TAXONOMY (binding)** — Three states: **impossible / unimplemented / defective**. Only `impossible` may be refused, and only with a refusal test plus a necessity test. `unimplemented` and `defective` are always failing tests. Capability skips and the word "gap" are retired; the audit enforces all three (§8.2).

**One sentence:** Eighteen sessions built a microscope; TODO97 migrates the
563-file scaffolding into a 3-file protocol, fixes the cheap wiring defects
first, calibrates the nine task families, screens at boxes that can answer the
question, and turns ten primitives into kernel rungs behind a kill test and
parity; all nine families are accounted, the docs regenerate from the registry,
and the remaining work is four algorithm rungs (S7b), five LM token-shape
defects (S8), and five pre-registered claims (S9).

---

## Progress Summary

| Session | Task | Status |
|---|---|---|
| S0 | Three-state taxonomy (impossible / unimplemented / defective) | ✅ DONE — binding, §0 |
| S1 | Migrate primitives to 3-file protocol + registry | ✅ DONE |
| S2 | Delete ~380 per-primitive files + generated tests | ✅ DONE |
| S2b | Repair stale kernel tables, algorithm imports, rungbench | ✅ DONE |
| S3 | Verify 6 property locks pass | ✅ DONE |
| S3a | 9/9 task families declared in `BASE_BOXES` | ✅ DONE |
| S3b | 3-seed controls, bar, cost, replay hash per family | ✅ DONE — 9/9 calibrated; graph ceiling defect filed |
| S4 | Fix cheap wiring (graph batching, conv/pc_alm/EPC probes) | ✅ DONE |
| S4x | Rung 0 wiring tests for all 75 primitives (284 tests) | ✅ DONE |
| S5 | First family base (graph) + first ladder (target_inversion) | ✅ DONE — graph 9/9 measured; see S5e |
| S5a | Add graph family base box (cora, 200 epochs) | ✅ DONE |
| S5b | Screen graph family primitives | ✅ DONE (9 measured) |
| S5c | First ladder (target_inversion on vision) | ✅ TRIAGED — unimplemented (feedback alignment missing); graph works |
| S5d | Generic `ReferenceAdapter` typed config (geometry/update/plasticity) | ✅ DONE — cases.py; contract 519 passed, axis contracts green |
| S5e | Screen every declared vision row; ladder every near-chance bound row | ✅ DONE — 52/52 vision accounted (45 measured, 4 defective, 26 refused); 8 ladder records |
| S5f | Screen the remaining families at their base boxes | ✅ DONE — tabular 34/34, continual 48 measured + 6 defect, rl 16 + 6, scientific 6, neuromorphic 11, sequence 46 + 6, lm 28 + 25 |
| S5g | Fix the family-declaration gap the screens exposed | ✅ DONE — every base axis declares its family (lock: `test_every_base_axis_declares_its_family`); lm/scientific/neuromorphic now have declared rows |
| S5h | File the defects the family screens found; repair the row-state gate | ✅ DONE — 6 classes: 3 refused by the declared space, 3 locked (token lane, ntm, ceiling); 47 rows re-derived |
| S6a | Audit gate, static predicates | ✅ DONE — `scripts/audit.py` |
| S6b | Audit measurement gate (5 ladders) | ✅ DONE — 2 tuned, 3 unimplemented; audit 0 |
| S6c | Six completeness predicates in `scripts/audit.py` | ✅ DONE — 0 findings |
| S6d | Skip scanner reads f-strings and non-literal reasons | ✅ DONE — 14 findings closed; 0 static findings |
| S6 | Measure the four params-box overruns at their declared box | ✅ DONE — each fits its declared box: surrogate 234,898/300k, routing 234,898/300k, attention 593,819/600k, tile 629,096/1M, causal_transformer 410,880/600k. They are box-limited, not defective; strict-xfail `test_a_box_overrun_fits_its_family_ceiling` names budget-aware sizing |
| S6e | Close the 21 defective rows (token lane, NTM, ceiling) | ✅ DONE — 14 token-lane rows refused by name; NTM trains on cartpole (trainer truncates the graph); width search fits routing/attention/graph; tile re-triaged `unimplemented` (628,280 floor at a 150k box) |
| S7 | 10 primitive kernels across 9 acceleration modules | ✅ DONE — 10 implemented + 65 absent; kill test + parity + microbench; 4 algorithm xfails filed as S7b |
| S8 | Regenerate map + docs from one source | ◐ PARTIAL — method cards + map doc + README counts read the registry; LM delta run leaves 5 token-shape defects filed |
| S9 | 5 pre-registered viability claims (5 paired seeds, CI) | ⏳ PENDING |

**Session 2026-11-20 (S5f–S6).** The seven remaining family bases were
screened at their declared boxes: tabular 34/34 measured; continual 48 measured
/ 6 defect; rl 16 / 6; scientific 6; neuromorphic 11; sequence 46 / 6; lm
28 / 25 (token-layout class). Five instrument defects the screens exposed were
fixed: a base axis now must declare its own family (lock); `_is_legal` validates against the
task's shape, not MNIST's; a sticky CUDA fault aborts the screen instead of
painting the remaining rows as defects; the ladder predicate treats the base
coordinate as the control; the map records the ruler's primary metric. The four
param-box overruns fit their declared boxes (S6), so they are box-limited, not
defective; budget-aware sizing stays the close condition.

**Session 2026-11-20 (S6e).** The 21 defective rows are closed. The token lane
is a declared contract now (`DomainTask.token_lane` → `TaskShape.token_lane` →
`AxisSpec.reads_tokens`), so `feedforward` on `tiny_shakespeare` and
`causal_transformer` on `char_ngram` are refused by name before training; the
base pair (`causal_transformer` on `tiny_shakespeare`, `attention` on
`char_ngram`) stays legal. The NTM double-backward is fixed in the training
loop, not in the mechanism: `System.detach_state()` truncates the graph the
geometry's buffers carry, and the RL trainer calls it at every environment step
(truncated BPTT). `_fit_geometry` now searches an explicit `hidden_dim` down to
fit the built geometry, which closes the graph base (200,967 → 199,519),
routing and all three attention rows. Tile has no width to shrink (its input
projection is 614,656 of its 628,280 parameters), so the screen writes it
`unimplemented` at the 150k box and stamps the compression lock. The delta
screen also now re-runs map-defective rows; before, a fixed defect stayed
screened forever. The capability test's dead `get_spec` import (migration
residue) now reads `error_blind_credit` on the credit row, so its error-blind
case can report instead of raising an `ImportError`. Locks: `test_a_language_task_declares_its_token_lane`,
`test_ntm_detaches_its_recurrent_state`, `test_a_box_overrun_fits_its_family_ceiling`,
`test_a_box_that_cannot_shrink_is_unimplemented` (all pass) and
`test_a_tile_mesh_fits_its_family_ceiling` (strict xfail, the capability that
would fit it).

### Remaining work (dependency order, 2026-11-20)

1. ~~**S5h — file the six defect classes**~~ ✅ done. The three classes the
   declared space can refuse are **closed as refusals**: `sec_loop._is_legal`
   now reads the planner's three rules, so `eligibility_prop`/`rtrl_reference`/
   `unbiased_rtrl` on a flat task, `nca` on a 21-feature task, and
   `causal_transformer` on a flat classifier are refused by name. The rows
   became `refused` with the rule as their trigger (26 rows). The three
   remaining classes carry a strict-xfail lock and a `defect_class` on every
   row: `token_lane` (14 rows; lock
   `test_a_language_task_declares_its_token_lane`), `recurrent_state_detach`
   (1 row; `test_ntm_detaches_its_recurrent_state`), and `ceiling_overrun`
   (6 rows; `test_a_box_overrun_fits_its_family_ceiling`). The row-state
   vocabulary is one source (`computronium/experiment/sec_status.py`); the
   gate now reports a defective row without its lock.
2. ~~**Close the 21 defective rows**~~ ✅ done (S6e, 2026-11-20). Each became
   a measured row or a named refusal; none is a gap:
   - **token lane (14)** — closed as refusals. `DomainTask.token_lane` (true on
     `LMTask`), `TaskShape.token_lane`, and `AxisSpec.reads_tokens` (true on
     `causal_transformer`) are the one declaration; `search_space._token_lane_rule`
     refuses the mismatch by name (`TOKEN_LANE_RULE`). `feedforward` on
     `tiny_shakespeare` and `causal_transformer` on `char_ngram` are refused
     before the cell runs; the base pair stays legal. Lock:
     `test_a_language_task_declares_its_token_lane` (passes).
   - **recurrent state detach (1)** — fixed. `System.detach_state()`
     (`detach_geometry_state`) truncates the graph a geometry's buffers carry,
     and the RL trainer calls it at every environment step (truncated BPTT).
     `ntm` on `cartpole` trains; `test_ntm_detaches_its_recurrent_state`
     passes, and the budget-8 combination cover stays green.
   - **budget-aware sizing (6)** — five rows fixed, one re-triaged. `_fit_geometry`
     now searches an explicit `hidden_dim` down until the *built* geometry fits
     the family ceiling (ground truth, not an estimator): routing, attention ×3
     (mnist/copy_task/cartpole) and the graph base (200,967 → 199,519/200,000)
     fit. `tile` on mnist has no width to shrink: its input projection is
     784 × 784 = 614,656 alone, so its floor is 628,280 at a 150k box. The
     screen now writes such a row as `unimplemented` (status `UNIMPLEMENTED`,
     `defect_class=ceiling_floor`) and stamps
     `test_a_tile_mesh_fits_its_family_ceiling` (strict xfail: close = an input
     compression narrower than `input_dim`). Passing lock:
     `test_a_box_that_cannot_shrink_is_unimplemented`.
2b. **S5i — the capability suite's hang** (filed, not closed). The full
   `uv run python -m pytest tests/primitives/test_primitive_capability.py` run
   hits the 300 s marker inside `train_on_task`'s DataLoader and produces no
   verdict: a killed run yields no verdict, collect (`pytest <file> --co -q >
   ids.txt`) before any re-run. Mechanism: a capability row trains through an
   unbounded loader, so a row that cannot train hangs instead of failing.
   Close condition: the loader is bounded (`num_workers=0`, bounded steps), and
   the suite reports pass / skip / fail in one run. The two dead imports this
   session fixed (`get_spec`, `task.spec.primary_pass_bar`) were separate test
   defects; the row now reads `error_blind_credit` and the task's own bar key.
3. ~~**S7 — ten kernel wrappers**~~ ✅ done (2026-11-20): the ten primitive
   rows carry a kernel rung, a kill test and parity; the 65 other rows stay
   reference-only. **S7b (filed):** four algorithm factories still `xfail` in
   `tests/acceleration/test_backend_reach.py` — `ff` (`_attachable` refuses its
   preset, which cannot take a backend), `fast_weight` (no fast-weight kernel),
   `pcalm` (no PC-ALM backend class), `tile` (its backend expects a
   `_tile_algo` the geometry does not carry); `fa`/`dfa`, `pepita`, `tp` and
   `spiking_snn` now attach and move the system's parameters.
4. **S8 — map + docs from one source.** ◐ partial. ✅ the method cards
   project the 75 `PrimitiveSpec` rows (no second axis table), `docs/sec/map.md`
   regenerates with the map's own status columns, and the README counts are
   generated tokens (96 implementations, 24 kernel-verified, 75 primitives).
   ✅ the LM delta run is done: its 11 pre-fix defects became 6 refusals and
   **5 remain** — `forward_tangent`, `surrogate`, `zeroth_order`,
   `fast_weights`, `routing` die on the token lane with shape/dtype errors.
   They currently carry `defect_class="token_lane"` and the geometry refusal
   lock, which is too broad for them. **Next:** narrow that lock to the
   geometry contract, file the credit/plasticity token-shape class with its
   own failing test (or implement the token-lane credit path), re-run the LM
   delta until `defective == 0`, then regenerate `docs/sec/map.md`. A fresh
   clone re-derives every row by screening; the committed code carries the
   rules and the locks.
5. **S9 — five pre-registered claims.** The two tuned coordinates
   (`local_contrastive` 0.4018, `random_projections` 0.3764) are the first
   candidates; each needs a pre-registered `n_max`, 5 paired seeds and a CI
   against the control. A claim within 1σ of its bar is `marginal`.

## 0. The three states (binding amendment, 2026-11-19)

Every row, refusal, and test is one of three states. **Only the first may be
quiet.**

| State | Meaning | Evidence | Refused? |
|---|---|---|---|
| **Impossible** | Cannot compose by math, shape, or API. | A **refusal test** (`pytest.raises(..., match="<constraint>")`) **and** a **necessity test** (remove the rule → a known-wrong composition compiles). | Yes. This is the only trap. |
| **Unimplemented** | The primitive, feature, box, or budget does not exist yet. | A **failing test** that names what is missing and the close condition. | No. |
| **Defective** | It exists and should work, but does not. | A **failing test** that names the mechanism. | No. |

Rules:

1. **No capability `pytest.skip`.** Environment skips only (`no CUDA`, `no dataset`), and the reason says so. A capability skip is a test defect.
2. **No "gap" label.** A row is `measured`, `unimplemented`, `defective`, or `impossible`. "Capability gap" is retired.
3. **A small box is unimplemented, never impossible.** The 300k ceiling, the missing family control, the missing budget, and the missing primitive are implementation tasks.
4. **Impossible is proved, not asserted.** No necessity test → not impossible; it is unimplemented or defective, and it gets a failing test.
5. **Keep the impossible set small and counted.** Growth is a taxonomy bug.
6. **A session cannot close a defect it discovers.** It files the failing test, the named mechanism, and the close condition; a later session challenges it.
7. **The map counts classes**: measured / unimplemented / defective / impossible / unaccounted. `unaccounted == 0` is the completeness gate; `defective == 0` is the quality gate.
8. **No backwards compatibility.** The migration deletes the old shape; it
   does not alias, shim, deprecate, or keep a second vocabulary. A legacy name
   that survives is a defect. A conversion with a current caller is not a
   compatibility shim; a bridge kept only to make an old test pass is.

### 0.1 What this forbids (the stuck patterns)

- Measuring before S5d is green.
- Screening a family without a 3-seed control that clears its bar.
- Calling a low cell an algorithm verdict.
- Adding a primitive before the existing census is accounted.
- Claiming a kernel without a kill test and a parity row.
- Quoting a plan count the artifacts do not carry.
- Closing a session on "tests consolidated" or "docs regenerated".
- Keeping a compatibility alias, a deprecated parameter, or a second
  vocabulary for an old shape the migration replaced.

### 0.2 The path (what each gate buys)

1. **S5d** → every primitive has a case, a reference, and an invariant. The
   contract suite is green; measurement can start.
2. **S3b** → every family has a control that clears its bar. A screen can
   answer a question instead of measuring noise.
3. **S6b + S4** → the near-chance and mid rows get a ladder; each becomes
   tuned, defective, or unimplemented with a box.
4. **S5** → the bound rows are screened at their declared family; the map
   gains verdicts.
5. **S7** → ten kernels, each with parity and a kill test; 65 stay absent.
6. **S8 + S9** → the map and docs regenerate from one source; five claims
   are pre-registered, paired, and published with a CI.

### 0.3 Cost, stop, and what time-wasting looks like

- Every rung is priced from a measured pilot. The watchdog is 2× that cost.
  A rung that exceeds its watchdog is a cost-model defect: kill, record,
  re-price.
- Screening (rungs 0–2) may stop freely. A claim (rung 3) uses a
  pre-registered `n_max` with a fixed-n CI and no peeking.
- No session runs without a stated decision and a stop rule.
- A session that ends on "tests consolidated" or "docs regenerated" bought
  structure, not capability: it does not close a capability ticket.
- The historical sink was measuring before wiring. The S5d gate and the audit
  exist so that sink cannot recur.

---

### 0.4 Next actions (dependency order)

**No item starts until the previous gate is green.** S5d is the hard gate: no
screen, ladder, or kernel precedes it. An item closes on a claim, a named
verdict, or a capability that works — never on "tests consolidated".

1. ~~**S5d**~~ ✅ done. The gate is `tests/primitives` (666 passed, 152
   declared skips) and the six property locks (65 passed).
2. ~~**S6c**~~ ✅ done, **queue closed**:
   **a.** ~~six biology capability skips~~ ✅ the tests read the native FA
   credit; adaptive FA is a strict xfail naming its missing rule.
   **b.** ~~`_FAMILY_OF_DOMAIN`~~ ✅ deleted; `TaskSpecEnriched.task_families`
   is the one declaration, and `family_without_base` reads `TASK_FAMILIES`.
3. ~~**S6b**~~ ✅ done. The 5 ladders ran: `local_contrastive` (readout_scale
   10) and `random_projections` (feedback_scale 0.1) are tuned coordinates;
   `forward_tangent`, `pc_alm`, and `target_inversion` are `unimplemented`
   with named mechanisms and strict-xfail locks. The records live in the
   map's `ladders` table; the full `scripts/audit.py` exits 0.
4. ~~**S3b**~~ ✅ done: 9/9 family bases calibrated (3 seeds, bar, cost,
   replay hash); the graph base's 200,967-parameter ceiling defect is filed
   as a strict xfail.
5. ~~**S5h**~~ ✅ done: the six screen defect classes are filed — three closed
   as declared-space refusals, three locked (token lane, ntm detach, ceiling);
   the row-state gate reads one vocabulary (`sec_status.RowStatus`) and
   `scripts/audit.py` exits 0 over the nine maps.
6. ~~**Close the 21 defective rows**~~ ✅ done (S6e): 14 token-lane rows
   refused by name, NTM trains on cartpole, five ceiling boxes fit by width
   search, and the tile floor is `unimplemented` with its lock. **NEXT: S7**
   (10 kernel wrappers), then **S8** (map + docs from one source), **S9**
   (5 pre-registered claims).

---

## 1. What the last 18 sessions bought, and what they missed

| Commit range | Bought | Missed |
|---|---|---|
| `85f62ed3` → `d0869aac` | Census, screen, calibrated bar, interaction slice, deep-dive, extension path | Zero primitive fixes |
| `1f53b4d1`, `550215b0` | Legality cleanup | Zero capability fixes |
| `69c5fb09` | PEPITA reference discovery | PEPITA still `kernel_unverified`; no real kernel |

The instrument is real: one inventory, one record, one exemption table, a replay
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
| Measured (vision) | 45 (37 bound + 8 inert) | map (mnist), 2026-11-20 |
| Measured (graph) | 9 (3 bound + 6 inert) | map (cora), 2026-11-20 |
| Bound at chance (<0.5) | 9 | map (mnist) |
| Bound mid (0.5–0.85) | 9 | map (mnist) |
| Bound clear (≥0.85) | 19 | map (mnist) |
| Defects | 4 (all param-box overruns) | map (mnist) |
| Refused (vision) | 26 (family mismatch / unavailable) | map (mnist) |
| Task families with a base box | 9 of 9 calibrated (3-seed controls) | `BASE_BOXES` |
| Declared family rows | 207 | census sum |
| Source scaffolding files | 563 | 383 primitives + 96 generated + 84 algorithms |
| Source files that survive | ~1,400 | ontology 33, experiment 206, acceleration 34, core/domains/models/scripts etc. |
| Test files / functions | 579 / 3,479 | tests tree |
| Structurally duplicate test functions | 721 (21%) | AST normalization |
| Test files that never train | 464 / 579 | grep |
| Kernel files with their own `@triton.jit` | 0 / 75 | grep |
| Kernel-parity tests that pass without requiring a real kernel | 235 | pytest |

**The headline is the accounted map: 45 vision rows measured (37 bound, 9 at chance), 4 rows defective at the declared box, and 9/9 graph rows measured.**

**Count check (2026-11-20):** the artifacts in `results/sec/map.json` and
`results/sec_graph/map.json` now carry **37 bound vision rows and 3 bound graph
rows** (the graph family's 9 declared rows are measured; 6 are inert
companions). The earlier 39 (30 vision + 9 graph) was the plan's claim, and the
13 + 3 = 16 was the stale artifact. Quote the maps, not this line, and
regenerate both before publishing a count.

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
    axis: Literal["credit", "dynamics", "geometry", "plasticity", "substrate", "update"]
    name: str
    equations: str
    invariants: tuple[str, ...]
    task_families: tuple[str, ...]
    kernel_status: Literal["implemented", "wrapper", "stub", "absent"] = "absent"
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

Measured 2026-11-20 at the row's own measured box (seven records in
`results/sec/map.json` `ladders`). The two tuned rows are coordinates, one knob
clear of the 0.200 band; the five unimplemented rows are strict-xfail locks in
`tests/property/test_ladder_record_lock.py`.

| Primitive | Primary knob | Ladder result | Triage |
|---|---|---|---|
| `credit.target_inversion` | feedback_scale | 0.1137 at every point | unimplemented: transpose feedback vanishes on vision; works on graph (0.68 @ 6 epochs). Needs feedback alignment (random B) or learned inverses for vision. |
| `credit.random_projections` | feedback_scale | **0.3764 tuned** (0.1) | coordinate at the feedback scale |
| `credit.forward_tangent` | feedback_scale | 0.1653 at every point | unimplemented: memory vs accuracy |
| `credit.local_contrastive` | readout_scale | **0.4018 tuned** (10) | coordinate at the readout scale |
| `credit.pc_alm` | beta | 0.1224 at every point | unimplemented: the dual-variable settle is not composed with instantaneous dynamics |
| `geometry.conv` | geometry.hidden_dim | 0.1217 at every point | unimplemented: the conv path does not train at the vision box |
| `dynamics.error_predictive_coding` | beta | 0.0980 at every point | unimplemented: the target/error channel is not carried through the vision step |
| `update.quantized_adam` | step_size | 0.0999 at every point | unimplemented: the quantized update state carries no step at the base box |
| `credit.zeroth_order`, `dynamics.spike_integration`, `plasticity.conflict_adaptive` | their own knob | refused on vision | screen on their declared family: sequence / neuromorphic / continual |

### 4.3 The 5 ceilings: unimplemented boxes, not impossible

Measured at the vision box 2026-11-20 (each row is `defective`: the composed
parameter count exceeds the family's 150,000 ceiling). The larger box is still
to be measured; the numbers below are the observed counts.

| Primitive | Task to measure | Observed / box to test |
|---|---|---|
| `credit.surrogate` | mnist (vision/neuromorphic) | 234,898 params / 300k box |
| `geometry.attention` | char_ngram (sequence) | 494,986 params / 600k box |
| `geometry.causal_transformer` | tiny_shakespeare (lm) | not yet screened (sequence/rl family) / 600k box |
| `geometry.routing` | mnist (vision) | 234,898 params / 300k box |
| `geometry.tile` | mnist (vision) | 628,280 params / 1M box |

The "measured box" is a **claim to test**, not a result. Measure it, record
the cost, and publish "requires N parameters on this task". If the box cannot
fit the task, record **unimplemented** with the budget and the failing test that
closes it. It is never impossible: the mechanism exists, the box does not.

### 4.4 The 2 unimplemented and 2 cost caps

| Primitive | Action | Done |
|---|---|---|
| `plasticity.rule_state` | implement `modulate()`; one-step fingerprint differs from `null` | or retire with trigger |
| `plasticity.substrate_coupled` | carry substrate state through the joint transition | or retire with trigger |
| `update.natural_gradient` | diagonal Fisher or smaller model; measure 1 step then 1 epoch | cost model |
| `dynamics.diffusion` | settle steps 30 → 10; measure 1 epoch | cost model |

---

## 5. The full action register (75 primitives)

Legend: **R** reference contract, **K** kernel truth, **I** instrument,
**E** execution repair, **CAP** unimplemented at the declared box (measured
larger box), **L** one-step probe / ladder, **F** family base, **G**
unimplemented implement/retire, **C** capability screen. Every row carries
R+K. For companion rows the `val_acc` is the companion's number, not a verdict
on the primitive.

**Status vocabulary:** `refused` in this register means "the declared family
does not include this task" — it is **unimplemented** (a base or feature is
missing), not impossible. `defect` is a named mechanism with a failing test.
`measured` is a boxed result. No register row is "gap".

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
| `target_inversion` | measured | bound | 0.119 (vision) / 0.68 (graph) | R+K+L (vision: unimplemented) |
| `temporal_trace` | measured | inert | 0.122 | R+K+I |
| `thermodynamic_contrast` | measured | bound | 0.782 | R+K+L |
| `unbiased_rtrl` | refused | — |  | R+K+F |
| `zeroth_order` | refused (vision) | — |  | R+K+L (screen on sequence) |

### Geometry (12)

| primitive | status | binding | val_acc | action |
|---|---|---|---:|---|
| `attention` | defect | bound |  | R+K+CAP |
| `causal_transformer` | refused (vision) | — |  | R+K+CAP (screen on sequence) |
| `conv` | measured | bound | 0.122 | R+K+L |
| `feedforward` | measured | bound | 0.894 | R+K+C |
| `graph` | measured | bound | 0.362 (cora) | R+K+C |
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
| `spike_integration` | refused (vision) | — |  | R+K+L (screen on neuromorphic) |

### Plasticity (8)

| primitive | status | binding | val_acc | action |
|---|---|---|---:|---|
| `closed_form_ridge` | measured | bound | 0.882 | R+K+C |
| `conflict_adaptive` | refused (vision) | — |  | R+K+L (screen on continual) |
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
| `quantized_adam` | measured | bound | 0.102 | R+K+L (unimplemented at the base box) |
| `riemannian_orthogonal` | measured | inert | 0.949 | R+K+I |
| `role_split` | measured | inert | 0.901 | R+K+I |
| `schedule_free` | measured | inert | 0.919 | R+K+I |
| `spectral_constrained` | measured | inert | 0.626 | R+K+I |
| `synaptic_intelligence` | refused | — |  | R+K+F |

---

## 6. Task bases and refusal mapping

### 6.1 The 9 bases

Measured 2026-11-19 over `CONTROL_SEEDS=3` at each box's declared axes
(`results/sec/pilot.json`); every control clears its bar.

| Family | Base task | Control | Bar (direction) | Seconds | Params / ceiling | Replay |
|---|---|---|---:|---:|---|---|
| vision | mnist | val_acc 0.8908 | 0.106 (max) | 13.8 | 134,794 / 150,000 | `f01b12b9cb206b2a` |
| tabular | iris | val_acc 0.7333 | 0.5055 (max) | 5.5 | 83,587 / 150,000 | `7fb3b41574b1d85e` |
| graph | cora | val_acc 0.4333 | 0.316 (max) | 2.0 | 200,967 / 200,000 † | `970b2defcb782c76` |
| sequence | char_ngram | val_ppl 6.8593 | 27.0 (min) | 15.3 | 86,555 / 150,000 | `750bfeb941d6bbc7` |
| continual | copy_task | val_acc 0.2670 | 0.125 (max) | 15.7 | 86,408 / 150,000 | `26887f83ff31275b` |
| rl | cartpole | mean_reward 45.9333 | 20.0 (max) | 25.1 | 83,458 / 150,000 | `11524dfa975ab009` |
| scientific | lorenz_state | val_loss 0.0891 | 67.415 (min) | 13.4 | 83,459 / 150,000 | `2740a90a0d980e46` |
| neuromorphic | spiking_mnist | val_acc 0.1354 | 0.106 (max) | 3.5 | 134,794 / 150,000 | `41d0d6aa8663370f` |
| lm | tiny_shakespeare | val_ppl 15.2785 | 65.0 (min) | 11.8 | 410,880 / 600,000 | `e0f89bde3c8f633a` |

† The graph base is 967 parameters over its 200,000 ceiling. Mechanism: an
explicit `geometry.hidden_dim` bypasses `_fit_geometry`'s sizing, so the
budget never bounds the build. Failing test:
`test_the_graph_base_fits_its_declared_ceiling` (strict xfail). The control
still clears its bar, so the family is calibrated; the ceiling is a separate
defect, not a low cell.

Each base gets a 3-seed control, measured walltime, parameter budget, and
replay hash. No screen runs on a family without a base.

### 6.2 The 8 family refusals are unimplemented, not impossible

| Primitive | Declared families | First screen |
|---|---|---|
| `eligibility_prop` | sequence, continual | char_ngram |
| `rtrl_reference` | sequence | char_ngram |
| `unbiased_rtrl` | sequence | char_ngram |
| `bayesian_online` | continual, sequence | copy_task |
| `cascade_synapse` | continual | copy_task |
| `synaptic_intelligence` | continual | copy_task |
| `closed_form_ridge` | continual, sequence | copy_task |
| `quantum` | scientific | lorenz_state (unimplemented: no quantum-chemistry task yet) |

A family with no base is **unimplemented**, not impossible: the test fails until
the base exists. `task_families` becomes an explicit `TaskSpecEnriched` field;
`_FAMILY_OF_DOMAIN` is deleted. A task may serve vision and continual
(`split_mnist`) or sequence and continual (`copy_task`); the old table could not
express that.

### 6.3 The 27 companion rows become explicit, not "measured"

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
a failure.

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
- a near-chance bound row without a ladder record;
- **a capability `pytest.skip`** (environment skips only; the reason must say
  `no CUDA` or `no dataset`);
- **an `impossible` row without a refusal test and a necessity test**;
- **an `unimplemented` or `defective` row without a failing test** (or a
  `xfail(strict=True)`), and no `"gap"` label anywhere in the map;
- **a declared `(primitive, family)` row that is unaccounted**: it is not
  measured, unimplemented, defective, or impossible;
- **a plan count that the artifacts do not carry** (the 39-vs-16 mismatch is
  the first one this catches);
- **a compatibility alias or deprecated re-export** of a shape the migration
  deleted (`reference_only`, a per-primitive module path, a
  `_FAMILY_OF_DOMAIN` fallback).

The first seven are structural and implemented (S6a). The last six are the
completeness gate: they are what make a quiet "gap", a silent skip, and a
backwards-compatible crutch impossible. They are specified here and landed in
**S6c**.

**Skip scanner (S6d, closed 2026-11-20).** `capability_skip` now reads an
f-string's constant text and reports a reason it cannot read at all (a name, a
call): an unreadable reason cannot prove the environment. The 14 findings the
literal-only scanner could not see are closed — 9 rungless factories are
`pytest.xfail` with the S7 close, the credit-adapter sources are constructed
instead of skipped, declared rows say `declared:` literally, and the dead
finite-difference test (0 collected params over deleted modules) is deleted.
The lock is `tests/property/test_audit_skip_scan_lock.py`: a fixture f-string
capability skip must be a finding, an environment f-string must not be.

---

## 9. Sessions, dependency-ordered

| Session | Work | Gate | Stop |
|---|---|---|---|
| **S0 Baseline** | Tag `pre-todo97`; run six locks; save output | Six locks green | Any lock red |
| **S1 Migrate** | Add `protocol.py` + `registry.py`; delete ~560 scaffolding files; update six locks | Six locks green; 75 ids registered; `comp verify` works | A lock fails; revert to tag |
| **S2 Wiring** | Fix graph batching; one-step probes for conv, pc_alm, EPC | 4 rows resolved or named defect | A probe with no named mechanism |
| **S3 Bases** | Explicit `task_families`; 9 bases; 3-seed controls; bar, cost, replay | 9/9 calibrated; 12/12 refusals mapped | A family without control/bar |
| **S4x Rung-0 Tests** | 284 wiring tests for all 75 primitives (instantiate, forward, pseudograds, settle) | All pass; 6/6 locks green | A test fails |
| **S4 Ladders** | 3-point ladders for the near-chance rows | 9 triaged: 2 tuned, 7 unimplemented with a lock | An untriaged row |
| **S5 Screens** | Vision + graph: every declared row screened at its family box | ✅ 52/52 vision accounted, 9/9 graph measured; 45+9 measured | A screen on MNIST for a sequence primitive |
| **S5b–S5g Families** | Screen sequence, tabular, continual, rl, neuromorphic, lm, scientific declared rows | 155 rows with verdict | A screen on a family with no control |
| **S5h Defect filing** | ✅ File the six screen defect classes; one row-state source | 0 defective rows without a failing test; audit 0 | A defect class named in prose |
| **S6 Ceilings** | Measure the 4 param-box overruns at the proper task (surrogate, attention, routing, tile) and causal_transformer on sequence | 4 unimplemented rows with a failing test, a measured box, and a cost | An unimplemented row with no failing test |
| **S6d Skip scan** | ✅ Scanner reads f-strings and reports non-literal reasons; 14 findings closed | 0 capability skips | A non-literal skip the gate cannot read |
| **S7 Kernels** | 10 wrappers to existing acceleration code; kill test; honest `absent` for 65 | 10 implemented; 0 stubs pass | A kernel with no speed/parity |
| **S8 Map + docs** | Regenerate map with verdict/rung/cost; regenerate README/method cards | 0 unaccounted rows; docs match map | A doc row the map does not carry |
| **S9 Results** | 5 pre-registered viability claims (control-relative, 5 seeds, CI) | 5 claims with CI | A claim without pre-registration |

**S1–S3 are repair. S4–S6 are measurement. S7 is optional acceleration. S8 is
the product. S9 is the science.** No screen runs before S5d is green; no
ladder runs before its family has a control; no row is closed as "gap".

---

## 10. Definition of done

1. **75/75 primitives registered** with a `PrimitiveSpec`, a task case, an
   analytic invariant, and a fingerprint.
2. **0 unaccounted rows.** Every declared `(primitive, family, box)` row is
   `measured`, `unimplemented` (with a failing test), `defective` (with a
   failing test), `impossible` (with a refusal test + a necessity test), or
   `refused` (a box statement: its trigger names the rule or the scope).
3. **0 capability skips and no "gap" label.** A capability `pytest.skip` is a
   test defect; the map carries the four states only.
4. **0 open defects at the audit.** `defective == 0`; the adapter defect
   (S5d) is the first one that must close.
5. **1 graph defect fixed.** Batched node input works; one-step fingerprint
   differs from feedforward.
6. **9/9 task families calibrated.** A base task, a 3-seed control, a bar, a
   cost, and a replay hash each.
7. **~159 declared family rows resolved**, one per `(primitive, family, box)`.
8. **10 primitives implemented across 9 acceleration modules**, 65
   reference-only with `kernel_status="absent"`; 0 stubs pass parity.
9. **~155 test files / ~1,300 tests**, 0 exact duplicate bodies, 0
   finiteness-only test, 0 empty assertion.
10. **5 viability claims**, pre-registered, 5 paired seeds, CI,
    control-relative; a claim within 1σ of its bar is `marginal`, not met.
11. **Map and docs regenerate from one source**; `scripts/audit.py` exits 0,
    and the plan's counts equal the artifacts'.

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

# 2x. Rung 0 wiring tests for all 75 primitives (DONE)
uv run python -m pytest tests/primitives/test_primitive_wiring.py -x

# 3. First ladder (target_inversion) — TRIAGED as unimplemented on vision
#    (transpose feedback vanishes; works on graph 0.68 @ 6 epochs)
#    Next: ladder on graph family or implement feedback alignment for vision
uv run python -m computronium.experiment.sec_loop \
  --track P0 --out results/sec --own-knobs --axis credit --task cora

# 4. Audit (DONE — 0 findings, 2026-11-20)
uv run python scripts/audit.py
#    --static: 0 findings. Full gate: 0 findings (records are local:
#    results/ is an artifact; S8 makes the map reproducible)
#    --check <name> runs one predicate; --json emits machine-readable findings

# 5. Vision + graph screens (DONE, 2026-11-20)
uv run python -m computronium.experiment.sec_loop --track P0 \
  --axis geometry --axis dynamics --axis plasticity \
  --max-primitives 40 --task mnist --out results/sec --device cuda
uv run python -m computronium.experiment.sec_loop --track P0 \
  --axis substrate --axis update --max-primitives 40 \
  --task mnist --out results/sec --device cuda --own-knobs
uv run python -m computronium.experiment.sec_loop --track P0 \
  --axis credit --axis geometry --axis dynamics --axis plasticity \
  --max-primitives 40 --task cora --out results/sec_graph --device cuda
uv run python -m computronium.experiment.sec_loop --track P0 \
  --axis substrate --axis update --max-primitives 40 \
  --task cora --out results/sec_graph --device cuda

# 6. Ladders for every near-chance bound row (DONE — 8 records)
uv run python -m computronium.experiment.sec_ladder          # every row
uv run python -m computronium.experiment.sec_ladder --only <id>
uv run python -m computronium.experiment.sec_ladder --dry-run  # prints, runs nothing

# 7. Remaining families (DONE — nine maps): one out dir per family base task
uv run python -m computronium.experiment.sec_loop --track P0 \
  --axis <axis> --max-primitives 60 --task <char_ngram|iris|copy_task|cartpole|spiking_mnist> \
  --out results/sec_<family> --device cuda
#    then sec_ladder on that map, then the audit with the new map in MAPS

# 8. Defect classes + the row-state gate (DONE, 2026-11-20)
uv run python -m pytest tests/property/test_family_defect_locks.py \
  tests/property/test_row_state_gate.py -q
uv run python scripts/audit.py          # 0 findings over the nine maps
#    a re-screen now writes RowStatus ("defective", "refused", ...) and stamps
#    defect_class + failing_test from sec_loop.DEFECT_LOCKS
```

---

## 12. What we stop doing

- Measuring before the primitive is wired.
- **Measuring before S5d (the adapter) is green.**
- Publishing "57 measured" when 27 measure companions and 11 are at chance.
- Calling a kernel parity test a gate when a stub can pass it.
- Running a 1-epoch screen and calling it a result.
- Adding a task family without a base box and a control.
- Writing ~380 wrapper files for 75 ontology classes.
- Generating 96 test files from 2 templates.
- Screening a sequence primitive on MNIST.
- Claiming "requires 600k params" before measuring the 600k box.
- Treating "more tests" as "more capability".
- **Treating a defect as a "gap".**
- **Skipping a capability test because it is hard, invalid, or slow.**
- **Accepting "defeat" without a failing test and a named mechanism.**
- **Quoting a plan count the artifacts do not carry.**
- **Closing a session on "tests consolidated" or "docs regenerated".**
- **Writing a row state the gate does not read** (`defect` vs `defective` made
  two lock predicates dead for a session).
- **Publishing a defect class as prose**; a class is filed by landing its
  failing test.

---

## 13. The rule

**No screen runs on a primitive that has not passed its analytic invariant.**
**No map row is published without verdict, rung, cost, and replay hash.**
**No kernel is claimed without a kill test and measured parity.**
**No family is screened without a calibrated base.**
**Every row is impossible, unimplemented, or defective — and only impossible may be quiet.**
**Impossible is proved: a refusal test and a necessity test, or it is not impossible.**
**Unimplemented and defective are failing tests; a skip is a test defect.**
**The screen and the audit read one row-state source; a state nobody reads is a comment.**
**0 unaccounted rows is the completeness gate; 0 open defects is the quality gate.**
**No backwards compatibility: the old shape is deleted, not aliased.**

The instrument is built. This plan points it at working primitives, and it
refuses to let a defect hide as a gap.
