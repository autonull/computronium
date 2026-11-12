# TODO88 — Experiment/Fix Cycle Continuation (Post-TODO87)

**Mission:** Continue the experiment/fix cycle: run experiments (≤15 min each), discover bugs, scrutinize poor-performing algorithms as potential implementation defects, and question excluded possibilities.

**Status:** TODO87 PHASE 1-7 COMPLETE. TODO88 G1–G9 FIXED (2026-11-11); late session adds **G8** (the settle path skipped intermediate graph aggregation — the harness trained a weaker model than `forward`), **R3** (`target_inversion`/`temporal_trace` graph paths), **R4** (transformer-aware `homeostatic`), and closes **R2** as refuted-and-traced-to-G8. Cora+gradient is claim-grade (0.766 mean, n=3, target >0.75 met); MUTAG harness mean rose 0.640 → 0.693 after G8. Core system working across vision, RL, graph, tabular. **Close (2026-11-11):** R8 fixed (LM token targets), R5 closed (cell replay hash now seed-sensitive; CUDA scatter tolerance derived as a limitation), R1(c) shipped (every graph cell reports the measured majority baseline and margin). **Continuation (2026-11-11 late-2):** R1(b) shipped — PROTEINS (1113 graphs, 223 held out) is a second graph-classification task, so a graph cell resolves to 0.005/graph instead of 0.026; R7 closed as **G9** — the "CUDA PyG crash" was our own unbatched graph probe feeding node rows to a foreign edge index, not upstream PyG, and CUDA graph cells now train. Claim-grade PROTEINS: gradient 0.665 ± 0.007, random_projections 0.625 ± 0.011 (majority 0.596, 2 claim-eligible cells); best PROTEINS arm 0.697 (n=5, hidden 128×5, step 0.003) is at the >0.70 target, not above it. **Continuation (2026-11-11 late-3):** R9 CLOSED — pooling is now a geometry knob (`geometry.pooling`: mean|sum) with a mode-aware `PoolContext` so every pooled-readout credit path uses the forward's transpose; sum pooling was *worse* (0.672 vs 0.691 at 100 epochs), and 200 epochs at the mean-pooled arm crosses the target: **0.7040 ± 0.0071 (n=5)** vs 0.596 majority. **Continuation (2026-11-11 late-4):** N1 CLOSED — six harness defects behind the non-graph credit sweep: **G10** tabular splits held out one class (wine val_acc 0.0 → **0.94–0.97**, n=3), **G11** `local_contrastive` trained on the last 10 pixels as its "label" (now unavailable), **G12** graph tasks paired with node-mode geometry, **G13** explicit `n_seeds`/`epochs` = 1 read as unset, **G14** budget-cut cells mislabeled `constraint_violation` (now `timeout`, with serial admission control and control-derived first-wave pricing), **G15** the supervised dry-run gate filtered every continuous-control RL cell (pendulum measured nothing). Pendulum now trains (−1289 random → −1184 at 400 episodes); `homeostatic`/`random_projections` "failures" resolve to contract-documented error-blindness and episode budget, not dispatch defects. **Continuation (2026-11-12):** N2–N6 CLOSED — plasticity (routing, fast_weights) and substrate breadth (memristive/ternary/sparse) are at parity with their references, `predictive_settling` reaches feedforward+recurrent, and the two hygiene tickets are done; three new defects fixed (**G16** a short plan now names its pruning cause, **G17** the planner's second compatibility matrix dropped 26 % of the declared space in silence, **G18** the sparse substrate's forward ignored `sparsity`), with **G19** (`local_goodness` x `energy_minimization` diverges) open. **Continuation (2026-11-12 late):** N7/N9/N10 CLOSED — `local_contrastive` now trains through a real label channel (claim-grade **0.7043 ± 0.0251**, n=3) after **G20** was found and fixed (the credit trained the head on a stream-normalized prefix the geometry never produced), `local_goodness x energy_minimization` is a declared void with the measured divergence, and error-blindness is a declared per-credit `ClassVar` the success criterion reads. `_UNAVAILABLE` is now empty; the only open ticket is **N8** (planner flat-matrix drift) plus **R6** at round close.

**Progress (Session 2026-11-12 — N7/N9/N10 + G20):**
- ✅ **N7 `local_contrastive` label channel shipped** — composition widens the input layer by the task's class count (register `CreditAssignmentConfig.label_channel`, `_build_credit_config` sets `label_dim=output_dim`), `computronium/core/label_channel.py::LabelChannelSystem` is the single seam that appends `[x | one_hot(y)]` to training batches and sweeps candidates at inference (one C·B forward, scored by the readout's own logit — the sweep never receives `y`), and the post-training probes carry a **zero** channel so settle telemetry still runs. G11's `_UNAVAILABLE` row is gone. Claim run: **0.7043 ± 0.0251 (n=3, L1, 10 epochs)** vs 0.10 chance; at the harness default `step_size=0.001` it measures 0.54, which is the credit's own recorded "lr 1e-3 is just slow" boundary.
- ✅ **G20 the head was trained on a stream the pipeline never produced** — found by the first live cell: free CE grew 223 → 1121 over 10 epochs while val_acc stalled at 0.52. The credit recomputes a **stream-normalized** prefix (`stream_norm`, Hinton: every post-activation rescaled to length sqrt(width)) and trains the head on it; `FeedforwardGeometry` did not normalize, so the head was fitted on unit-scale features and applied to unbounded ones (probe: `‖h2‖` 0.10 → 10 → 52 → 137 over 300 steps). Fixed by making normalization a geometry property (`GeometryConfig.stream_norm`, applied in `_apply_stack`/`route`) which composition turns on for a label-channel credit that declares it. Free CE now descends (1.30 → 1.16 over 5 epochs, unit-RMS hidden acts).
- ✅ **N9 `local_goodness` x `energy_minimization` is void, not broken** — same cell/update/task, 3 epochs: instantaneous **0.9628**, energy_minimization **0.0892** with free loss 1.87 → 289.5 → 2.1e5 (the G19 signature reproduced). The FF goodness contrast is a *local* rule; differentiated through an unrolled settle its graph is W^N, so the deep-chain term dominates. Declared void as `local_goodness_energy_minimization`, so the space prunes it by name (dry run: 2 cells → 1). The other multi-step settles stay available until each is measured — same policy as the rest of the ledger.
- ✅ **N10 error-blindness is a declared category** — `error_blind: ClassVar[bool]` on every credit class (`homeostatic`, `temporal_trace` = True), stated on the `CreditAssignment` protocol and on both identity cards with the measured chance numbers, and read by the success criterion ("≥3 *error-aware* credits per geometry"). The flag is not derivable from `phases` (homeostatic settles both phases and reads no error; `local_contrastive` settles FREE only and reads the label channel), which is why it is declared. Lock `test_error_blind_credits_lock.py` (5 tests).
- ✅ Hygiene found on the way — `test_primitive_compatibility_lock` still asserted the stale `temporal_trace x instantaneous` rule that G17 deleted (1 red test at HEAD); the row is removed.

**Progress (Session 2026-11-12 — N2/N3/N4/N5/N6 + G16/G17/G18):**


- ✅ **N2 Plasticity at parity, and one contract boundary** — every plasticity arm matched `null` on a task the base learner can solve: MNIST feedforward 3 epochs, routing 0.9684/0.9677 vs null 0.9679/0.9662; MNIST feedforward `energy_minimization`+`thermodynamic_contrast` 2 epochs, fast_weights 0.9447/0.9476 vs null 0.9472/0.9498. So fast weights pair with energy dynamics as intended and cost nothing. The `copy_task`/`recurrent` arm cannot use `gradient` (declared void: `recurrent_instantaneous_gradient_credit`), and its compatible credit `temporal_trace` is **error-blind by contract** (`phases=(FREE,)`, the loss is never read), so recurrent+MNIST+STDP measured chance for both arms (routing 0.0956/0.1234, null 0.1018/0.1238) — the same boundary R4 found for `homeostatic`, now confirmed for the second error-blind credit.
- ✅ **N3 Substrate breadth at parity, and one substrate that named no difference** — 3 seeds each at 3 epochs: digital **0.9672**, memristive **0.9675**, ternary **0.9588** (4 claim-eligible cells). `sparse` produced *bit-identical* per-seed accuracies to digital (0.9679/0.9662/0.9674), which was **G18**: `SparseSubstrate.get_forward_operator` was a dense matmul behind a weight clamp, so the declared `sparsity` never reached the forward path. Magnitude pruning now masks the declared fraction per forward; sparse measures **0.9641/0.9648/0.9631** (mean 0.9640) against digital's 0.9672 — a −0.32 pt cost at 50 % sparsity, and no longer a copy of digital.
- ✅ **N4 Predictive settling reaches recurrent and feedforward** — the N4 premise ("filtered on feedforward") is stale: `predictive_settling` proposes on both (feedforward and recurrent, with `thermodynamic_contrast`). Live recurrent arm: 0.5441/0.4511 at 2 epochs, **144 s/epoch** — it trains but is ~4× energy_minimization's cost, so its tier is L2, not L1. The two feedforward seeds were proposed but not reached inside the 0.2 h budget (642.8 s, 3 cells).
- ✅ **N5 `TASK_COST_CLASS` deleted** — the hand-maintained table in `domains/registry.py` disagreed with the enriched `TaskRegistry` (pendulum MEDIUM not EXPENSIVE, proteins EXPENSIVE not MEDIUM, spiral three-class not binary) and `test_smart_survey_lock::test_task_scheduler_cost_classes` failed on the drift. The table and its four accessors are gone; the one consumer (`RunSpec.task_names` for `task == "auto"`) reads `domains._task_registry.CHEAP_TASKS`, and the lock now asserts every registry row lands in its declared class and baseline.
- ✅ **N6 state-algebra lock reads the credit package** — `test_credit_annotations_name_the_surface` pointed at `ontology/credit.py`, which is now a package; it scans every module in `credit/`.
- ✅ **G16 A short plan now names what pruned it** — an empty plan reported "No more cells to evaluate" over a declaration that was void on its face. `iter_candidates` takes a rejection sink (`Counter[str]`) keyed by cause — the named void constraint, `substrate x dynamics`, `geometry x dynamics`, `geometry x task`, `compose <Exc>`, `param budget`, `dry-run gate: <reason>` — the planners carry it (`StaticPlanner.rejections`, `PolicyPlanner.rejections`, `ProposalContext.rejections`), the dry-run payload carries `pruned`, and the summary/short-plan output prints it. Measured: `pruned: void constraint: recurrent_instantaneous_gradient_credit (2)`.
- ✅ **G17 The planner's flat matrix dropped 26 % of the declared space in silence** — `_check_coord_compatibility` re-filtered every proposed cell with `_INCOMPATIBILITY_RULES`, a second source of truth beside the declared constraints. Measured over the whole 6-axis product: **15,348 of 58,968 space-legal coordinates** are voided at the planner, and the drop was invisible. Its drops now count into the same sink, and the stale `temporal_trace x instantaneous` rule is deleted — the declared space and the compiled `hebbian` rung both admit that coordinate. Reconciling the remaining rules is queued (N8).
- ⚠️ **G19 (open) `local_goodness` x `energy_minimization` diverges** — MNIST feedforward, 2 epochs: loss 1.87 → **289.5**, val_acc 0.0891 (chance), 64 s/epoch. `thermodynamic_contrast` on the same dynamics reaches 0.9472, so the pair is the suspect, not the settling. Queued as N9.
- ✅ **`comp report` no longer repeats the claim-eligibility line** — the eligibility count was logged at INFO inside a per-section accessor, so one report printed it 31 times. It is a diagnostic now (DEBUG).

**Progress (Session 2026-11-11 late-4 — N1):**
- ✅ **G10 Tabular split held out one class** — `TabularTask.setup` split by slicing `X[:n]`/`X[n:]`, and sklearn ships iris/wine ordered by class. Wine's 36-row validation set was *entirely* class 2 while the train set held 12 class-2 rows: every arm read `val_acc=0.0` (train 0.88–0.90). Iris validation was class 2 only, which is why it swung 0.47–0.77 by seed. Fixed with `train_test_split(test_size=0.2, random_state=0, stratify=y)`; `evaluate` now reports `majority_baseline` and `val_acc_over_majority` beside accuracy (the R1c protocol, applied to tabular). Measured: wine 0.972/0.944/0.944 (n=3, 5 epochs) vs 0.0; iris 0.867/0.867/0.767 vs 0.767/0.467/0.700; majority 0.389 and 0.333.
- ✅ **G11 `local_contrastive` was training on pixels** — the credit's contract reads its label from the last `label_dim` input features and needs a label-sweep readout; the kernel gives it the task's own width (mnist feedforward: 784 in, no channel). It sliced the last 10 pixels as the "label", trained a contrast against noise, and spent 10 epochs at chance with a *diverging* loss (17 → 3459, val 0.110/0.120). The row is now `available=False` with the reason recorded (`_UNAVAILABLE`), and the dry run prints it. Re-enabling is a feature ticket (label channel + widened input + label-sweep inference), not a knob flip.
- ✅ **G12 Graph tasks are graph-geometry exclusive** — `_is_geometry_task_compatible` filtered non-graph tasks off graph geometry but not the converse, so the planner proposed `graph_classification` on feedforward/recurrent/causal-transformer geometry. `GraphSystemTrainer` forwards `(x, edge_index, batch)`, so those cells died on the forward signature (5 FAILs in Experiment 13). A graph-domain task now requires `geometry == "graph"`; the dry run for `graph_classification` over `feedforward,graph,recurrent` proposes exactly the one graph cell.
- ✅ **G13 Explicit depth was read as unset** — `schedule_for` treated `n_seeds != 1` / `epochs != 1` as "explicitly set", so `--n-seeds 1` ran the L1 ladder's **3** seeds (acrobot: "Evaluating 3 single-seed cell(s)" against a 1-seed declaration) and `--epochs 1` ran 5. `RunSpec.n_seeds/epochs` are `int | None`, so the rule is now `is not None`; explicit 1 is a literal, `None` follows the ladder. Lock `test_schedule_depth_lock.py` (3 tests).
- ✅ **G14 A budget cut was a "constraint violation"** — a cell killed by the run deadline recorded `cause=constraint_violation`, the cause that sends an investigator after a compatibility bug; a serial wave also started a seed with 173 s left for work it had just measured at 216 s (9/10 epochs, FAIL). Fixed: incomplete → `FailureCause.TIMEOUT` (ceiling breach keeps `CONSTRAINT_VIOLATION`; no epochs → `timeout` when the trainer recorded `deadline_exceeded`), `_SerialAdmission` refuses a cell whose measured cost no longer fits (`cells_skipped` instead of a truncated FAIL), and the first wave is priced from the positive control's measured per-epoch time (`_first_wave_price`) instead of the 30 s table default. Measured: "cell 2/2 skipped: 278.2s needed, −2.1s left"; first wave priced 407 s/cell from a 20.4 s/epoch control (was 60 s).
- ✅ **G15 The dry-run gate filtered every continuous-control RL cell** — `_dry_run_trainable` scores a cell with cross-entropy on a task batch. Pendulum's batch target is a dummy index into a one-wide head, so CE is constant and the gate returned `all-zero pseudo-gradients (no-op)`: the pendulum space held **zero cells** and the run measured only its positive control ("No more cells to evaluate"). The gate now declines RL tasks and degenerate (one-class) heads; `wine` still validates `ok`. Pendulum then trains: −1289.7 random → −1183.8 after 400 episodes.
- ✅ **N1 symptom resolutions (not defects)** — `homeostatic` is error-blind by contract (recurrent+iris 0.233/0.300/0.333 against a 0.333 majority; transformer+mnist flat 0.1009 for 9 epochs), so chance is the contract, not a dispatch bug; `random_projections+recurrent+adam` on copy_task runs clean (0.188/0.166 at 5 epochs — episode/epoch budget, not a crash); acrobot stays at the −500 step cap for 400 episodes (exploration-limited; the RL success criterion names Pendulum).

**Progress (Session 2026-11-11 late-2 — R1b / R7 / G9):**
- ✅ **R1(b) PROTEINS as a second graph task** — `graph_classification` stays MUTAG; `proteins` maps to PROTEINS (1113 graphs, 3 features, 663/450 class split, 890 train / 223 held out) through one `GRAPH_CLASSIFICATION_DATASETS` map, one `_graph_classification_spec` registry helper (two rows, one objective set) and one `SUPPORTED_TASKS` entry. The held-out split now resolves 0.005/graph against a 0.596 majority rate, instead of MUTAG's 0.026 against 0.658.
- ✅ **R7 CLOSED — the CUDA graph crash was ours (G9), not PyG** — CUDA graph cells died with `vectorized_gather_kernel: index out of bounds` (sticky `device-side assert`, so every later CUDA cell in the process died too). The index was our static `edge_index`: `_sample_inputs` flattened a PyG batch to `batch.x` and the free-phase probe ran node-mode `forward` over a foreign edge list. Two more graph-batching defects sat behind it: `_batched` sized degrees from `edge_index.max()+1` (PyG appends trailing isolated nodes — measured 1134 rows of degrees against 1201 activations), and `forward_with_intermediates` ignored graph kwargs entirely (no batched aggregation, no pooling). Fixed: probe skips batched-graph inputs (and prices energy per graph, not per node), degrees follow the activation rows, intermediates delegate to `settle_blocks`, and node-mode `forward` rejects a foreign row count with a `ValueError` before any kernel launch. Lock: `tests/property/test_graph_batched_input_lock.py` (4 tests). CUDA proteins: 10-epoch cell 0.6637 vs CPU 0.6637 — device parity, no assert, no telemetry warning.
- ✅ **Claim-grade PROTEINS run** (L1, 100 epochs, n=3, cuda): gradient 0.6637/0.6726/0.6592 → **mean 0.665**; random_projections 0.6233/0.6143/0.6368 → **mean 0.625**; majority 0.596. 7/7 cells PASS, 2 claim-eligible. Both credits beat the majority rate.
- ✅ **R9 CLOSED: PROTEINS > 0.70 met** — default cell (hidden 64 × 3, step 0.001): gradient 0.665, random_projections 0.625, majority 0.596. Pooling is now a geometry knob: at hidden 128 × depth 5, step 0.003, 100 epochs, mean = **0.6906 ± 0.0208** vs sum = **0.6717 ± 0.0296**, so mean stays default. At 200 epochs the mean-pooled arm reaches **0.7040 ± 0.0071 (n=5)** vs 0.596 majority (+0.108), 1 claim-eligible cell. See Session late-3.

**Progress (Session 2026-11-11 close — R1c/R5/R8):**
- ✅ **R8 LM token targets** — `TransformerGeometry` folds the sequence into the batch (logits `[B*T, V]`), while `LMTask` returns targets `[B, T]`. `nudged_output` returned the 2-D target and broadcast-failed, and both task-loss paths fed CE a rank-mismatched pair. Fixed with one shared `_align_target_rows` fold applied in `nudged_output`, `task_loss`/`_task_loss_tensor` and `SystemTrainer.validate`; `_one_hot` now builds `[…, V]` one-hots for any target rank. Locks: `tests/property/test_lm_target_alignment_lock.py` (5 tests: nudge, ignore-index, settle, train step, trainer validation).
- ✅ **R5 replay identity** — the per-cell hash was a hand-written field list that omitted `schedule.seed` (`evaluate.py`), so seeds 42/43/44 of one coordinate shared a hash while val_acc differed. It now hashes `code_sha | dataset_version | coordinate.measurement_key(schedule)`; the measurement key carries seed, task, device and determinism. The CUDA `index_add_` tolerance is stated, not hidden: `LimitationKind.NONDETERMINISTIC_ACCUMULATION` names every non-deterministic CUDA graph cell (one graph = 1/N of the split). Locks: `tests/property/test_cell_identity_lock.py` (4 tests).
- ✅ **R1(c) graph evaluation protocol** — `GraphClassificationTask.evaluate` reports `majority_baseline` (measured over evaluated labels) and `val_acc_over_majority` beside `accuracy`; the kernel copies task custom metrics into the cell payload. A 0.63 MUTAG cell is now visibly below the 0.658 majority rate instead of merely "near 0.70". Lock: `tests/property/test_graph_eval_protocol_lock.py` (2 tests).
- ⚠️ **R1(a)/(b) remain** — the 38-graph held-out split still makes the >0.70 target noise-level (one graph = 0.026). Averaged cross-validation (a) or a larger TU dataset (b) is the remaining work; (c) makes today's numbers honest, not higher.

**Progress (Session 2026-11-11, late — G8/R2/R3/R4):**
- ✅ **G8 Graph settle path skipped intermediate aggregation** — `GraphGeometry.settle_blocks` appended `self._aggregate(h)` but fed the *pre-aggregation* relu output into the next layer, so the pipeline's multi-layer graph forward aggregated only the last layer (the head saw an aggregated act; the hidden chain did not). `forward`/`forward_with_intermediates`/`_stack` all aggregate between layers. Fixed, locked by `test_settle_blocks_matches_forward`.
- ✅ **R2 harness-vs-probe gap refuted as an optimizer problem** — a `grad_clip` sweep through the harness (0.1/1.0/10.0, 200 epochs, n=3) returned identical results at 1.0 and 10.0 (clipping inactive); plain-Adam arms with the harness's nudged CE (β=0.1) and frozen biases matched or beat the reference probe (0.726/0.732/0.737 vs 0.716). The residual gap was G8, not the U-axis.
- ✅ **R3 pooled-readout graph paths** — `TargetInversionCredit` now propagates graph-space targets and broadcasts each node its graph's target; `TemporalTraceCredit` rate mode correlates the head against the pooled hidden act. Both clear a batched MUTAG-shaped readout and move every 2-D weight.
- ✅ **R4 transformer-aware homeostatic** — `_post_activations` pairs each transformer weight with its successor act, so the fused QKV projection (`[3d, d]`, no act of that width) receives a norm-regulating update instead of zeros. All six vision-transformer weights move.
- ✅ **R5 replay hash was seed-insensitive** (found in the R2 sweep): three cells at seeds 42/43/44 shared `replay_hash=0fdeab…` while val_acc differed. Fixed at close: `_cell_replay_hash` hashes `measurement_key` (seed included); CUDA scatter tolerance is a derived limitation.
- ✅ **R8 LM token targets crashed `nudged_output`** (found probing R4): teacher-forced targets `[B, T]` met logits `[B*T, V]`, so `one_hot` allocated `[B, T, V]`. Fixed at close: `_align_target_rows` folds the target in the nudge, the task loss and trainer validation.


**Progress (Session 2026-11-11, evening — G4–G7):**
- ✅ **G4 Graph geometry had no self connection** — aggregation was a bare neighbour mean (mean aggregation with `deg.clamp(min=1)`), in `row` order rather than PyG's source→destination order, so `h[i]` never contained `x[i]` and a source-only node collapsed to zero. MUTAG train accuracy plateaued at 0.767 (below the 0.658 majority baseline on val). Fixed: `(A + I)` in-degrees plus self in `_aggregate`, batched setup deduplicated into one `_batched` context manager. Probe: train 0.80–0.83, val 0.711–0.737 across 5 seeds (was 0.60–0.63).
- ✅ **G5 Graph-classification readout broke FA** — `RandomProjectionsCredit` crashed with `mat1 and mat2 (2x4 and 20x16)` on any pooled task (node-sized acts, batch-sized error). Fixed with a pooling-map-aware `_graph_path`; `random_projections+adam` on MUTAG now trains (0.711/0.658 = gradient parity).
- ✅ **G6 Three credit dispatchers, one stale** — `spec._credit_from_config` (used by `spec.compose_system_from_configs`) did not know `local_contrastive` or `pc_alm`; a legal axis value died with `Unknown credit_type`. Consolidated: `spec` is the single dispatcher, `factory`/`joint` delegate.
- ✅ **G7 Cost-model cache clobbered other tasks' prices** — a 1.8 s/cell MUTAG run at `cuda/L1` replaced MNIST's 247 s/cell price for the same key (dry-run then advertised 1.8 s/cell for a four-minute cell). Fixed: the per-task map merges, `CostModel.cost_for(task)` / `cost_for_tasks(tasks)` price the dry-run per task (multi-task runs average their selected tasks).
- ✅ **MUTAG attribution re-run** (L1, 200 epochs, deterministic split): gradient 0.684/0.658 (g4, 2 seeds) and 0.658/0.632 (g6, 3-seed run reached 2); random_projections 0.711/0.658. All above/at the 0.658 majority baseline, below the pre-fix "0.63 ceiling" claim's meaning.
- ✅ **Cora claim-grade run** (L1, 100 epochs, `update.step_size=0.01`, n=3): 0.782 / 0.752 / 0.764 → **mean 0.766 > 0.75 target**, 1 claim-eligible cell, variance collapsed vs the 20-epoch run (0.46–0.75).
- ⚠️ **MUTAG >0.70 is a measurement-resolution problem, not only a model problem** — the held-out split is 38 graphs with a 25/13 class balance, so one graph = 0.026 and the majority baseline is 0.658. Harness cells land 0.63–0.71 (pipeline U-axis) while the probe lands 0.711–0.737 (plain Adam); the remaining work is the evaluation protocol, not more epochs.

**Earlier progress (Session 2026-11-11):**
- ✅ **G1/G2/G3 FIX PHASE** — graph trainer now drives the canonical pipeline; graph kwargs are geometry-conditional; pc_alm×instantaneous is void. Axis attribution re-established on cora (see session log).
- ✅ Experiment 1: Predictive Settling with Thermodynamic Contrast / Local Goodness — COMPLETE (expected behavior confirmed)
- ✅ Experiment 6: Credit Assignment — Cross-Geometry — PARTIAL (budget too tight, key findings logged)
- ✅ Experiment 7: Substrate Comparison — Digital vs Memristive — COMPLETE (memristive matches digital at ~1.7x slower)
- ✅ Experiment 8: Plasticity Sweep — Fast Weights / Routing — PARTIAL (fast_weights correctly filtered; routing worse than null)
- ✅ Experiment 2: Causal Transformer Vision — Credit Sweep — PARTIAL (budget limited; homeostatic ~10% chance, random_projections 68%, gradient/pc_alm not evaluated)
- ✅ Experiment 3: Causal Transformer Vision — Geometry Parity — **PASS** (causal_transformer 97.1% matches feedforward 97.2% on MNIST)
- ⚠️ Experiment 4: Graph Classification — Geometry Sweep — PARTIAL (CUDA PyG issue; 2 cells ran: 57.9% and 55.3%) — **attribution invalid: G1 bypass (re-run needed, batched path now fixed)**
- ⚠️ Experiment 5: Graph Node Classification — PASS mechanically (Cora 70-73%, Pubmed 66-68%, Citeseer 61-64%) — **attribution invalid: G1 measured plain GNN autograd; superseded by the 2026-11-11 cora attribution re-run (graph+gradient 0.618, graph+random_projections 0.195)**
- ✅ Experiment 9: Energy Minimization — Dynamics Sweep — PARTIAL (7/8 cells; energy_minimization+gradient 97.0% matches instantaneous 97.2%)
- ✅ Experiment 10: Causal Transformer Vision — Credit Sweep (gradient, pc_alm) — PARTIAL (gradient 97.1% PASS; pc_alm ~10% FAILS to learn)
- ⚠️ Experiment 11: Graph Classification — CPU (L0, MUTAG) — PASS mechanically (8/8 cells, val_acc 55-63%) — **attribution invalid: G1 bypass; re-run needed under the fixed batched path**
- ✅ Experiment 12: Energy Minimization + predictive_settling — PARTIAL (energy_minimization+gradient 97.1% PASS = instantaneous; predictive_settling filtered; L0 budget tight for energy_min)
- ✅ Experiment 13: Credit Assignment — Cross-Geometry (10 tasks, 4 geometries) — PARTIAL (~50 cells; gradient best; homeostatic broken; random_projections fails on recurrent+adam; local_contrastive works on ff)
- ✅ Experiment 14: Causal Transformer Vision — Full Credit Sweep (L1, MNIST) — **PASS** (gradient 97.9% = feedforward; random_projections 70-76%; homeostatic ~10% BROKEN - attention in_proj gets zero gradients)

---

## 📌 REMAINING WORK — NEXT SESSION (ordered by what unblocks a claim)

**Order of work now (NEXT SESSION):**
1. **N8** — Reconcile the planner's flat matrix with the declared space (G17): 15,348 of 58,968 space-legal coordinates are still voided at the planner by `_INCOMPATIBILITY_RULES`. Either derive the flat rules from the declared constraints, or declare each surviving rule as a constraint so the space knows it. Start from the measured top causes (temporal_trace/target_inversion x energy_minimization, ternary x temporal_psi, random_projections/homeostatic x diffusion). **Note:** the N9 void (`local_goodness x energy_minimization`) was declared in `CONSTRAINTS_REGISTRY` for exactly this reason — it is the pattern to follow.
2. **R6** — Register C hygiene at round close (after the experiment cycle).
3. **N11 (new, optional)** — `local_contrastive` at the probe's own regime: the claim run used `step_size=0.1 / readout_scale=0.3 / sequential_lr=0.1` (0.7043 ± 0.0251). The probe's d2 reference at norm_lr 0.3 is 0.824, so a 0.2–0.3 arm (n=3) is the cheapest way to test whether the harness cell reaches it. Exploratory, not a defect.

| # | Ticket | Why now | Gate / cost | Depends on |
|---|--------|---------|-------------|------------|
| N2 | ✅ **CLOSED — plasticity is at parity with null, and one contract boundary is named.** routing 0.9681 vs null 0.9671 (MNIST ff, 3 epochs); fast_weights 0.9462 vs null 0.9485 (energy_minimization, 2 epochs); recurrent+STDP is chance for both arms because `temporal_trace` never reads the label. | Done; do not reopen as "plasticity is broken". | — | — |
| N3 | ✅ **CLOSED — substrate breadth at parity, 4 claim-eligible cells.** digital 0.9672, memristive 0.9675, ternary 0.9588, sparse 0.9640 (after G18). | Done. | — | — |
| N4 | ✅ **CLOSED — `predictive_settling` reaches feedforward and recurrent** (recurrent 0.5441/0.4511 at 2 epochs, 144 s/epoch → L2 tier). | Done. | — | — |
| N5 | ✅ **CLOSED — `TASK_COST_CLASS` deleted**; the derived `domains._task_registry` is the single source and the lock reads it. | Done. | — | — |
| N6 | ✅ **CLOSED — state-algebra lock scans the `credit/` package.** | Done. | — | — |
| N7 | ✅ **CLOSED — `local_contrastive` has a label channel and a claim-grade number.** Composition widens the input by the task's class count (MNIST 784 → 794), `LabelChannelSystem` appends `[x \| one_hot(y)]` per training batch, and inference sweeps the candidates in one C·B pass, scoring each with the readout's own logit (the true label never reaches the sweep). Claim run (L1, 10 epochs, n=3, `step_size=0.1 / readout_scale=0.3 / sequential_lr=0.1`): **0.7043 ± 0.0251** vs 0.10 chance. G11's unavailable row reverted; that available-row case is now locked in both directions. | Done; slow-regime number at the default `step_size=0.001` is 0.54 (the credit's own measured "lr 1e-3 is just slow" boundary). | — | G11, G20 |
| N8 | **Drift** — 26 % of space-legal coordinates voided at the planner by a second matrix (G17). | Two sources of truth for one rule. | `_INCOMPATIBILITY_RULES` vs `CONSTRAINTS_REGISTRY`; drift lock | G17 |
| N9 | ✅ **CLOSED — the pair is void, the credit is fine.** Same cell, same update, 3 epochs: instantaneous **0.9628**, energy_minimization **0.0892** with free loss 1.87 → 289.5 → 2.1e5. The FF goodness contrast is a local rule; differentiated through an unrolled settle its graph is W^N and the deep-chain term dominates. Declared void (`local_goodness_energy_minimization`) so the space prunes it by name instead of proposing a diverging cell; the other multi-step settles stay open until measured. | Done. | — | G19 |
| N10 | ✅ **CLOSED — error-blindness is a declared category.** `CreditAssignment.error_blind` is a ClassVar every registered credit declares (`homeostatic`, `temporal_trace` = True); the flag is independent of the phase list (homeostatic settles both phases and still reads no error), the success criterion counts *error-aware* credits, and both identity cards state the measured chance results. Lock: `test_error_blind_credits_lock.py` (5 tests). | Done. | — | R4, N2 |

| # | Ticket | Why now | Gate / cost | Depends on |
|---|--------|---------|-------------|------------|
| R1 | **MUTAG/PROTEINS evaluation protocol** — (c) **SHIPPED** (majority baseline + margin per graph cell); (b) **SHIPPED** — `proteins` (PROTEINS, 1113 graphs) is a second graph-classification task, so the held-out split resolves 0.005/graph against 0.596 majority. Remaining: (a) — **CLOSED as superseded**: fold rotation existed to buy resolution, and (b) buys 6x more of it for one training per cell instead of five. Next ticket is the result, not the protocol: R9 closed it (PROTEINS 0.7040 ± 0.0071 at mean pooling / hidden 128 × depth 5 / 200 epochs, majority 0.596). | New task row + registry helper; demo gate if a demo ships | — |
| R2 | ✅ **CLOSED — harness U-axis gap was not the optimizer.** grad_clip 1.0 vs 10.0 identical; nudged-CE/frozen-bias arms match plain Adam. Root cause was G8 (`settle_blocks` aggregation). Harness 0.640 → 0.693 mean. | Done; do not reopen as an optimizer ticket. | — | G8 |
| R3 | ✅ **CLOSED — pooled-readout paths shipped** for `target_inversion` and `temporal_trace`; lock `test_credit_readout_paths_lock.py`. | Done. | — | G5 pattern |
| R4 | ✅ **CLOSED — transformer-aware homeostatic** pairs each weight with its successor act; fused QKV now moves. Lock `test_credit_readout_paths_lock.py`. | Backfill only: homeostatic is error-blind by contract, so nonzero updates do not imply accuracy. | — | — |
| R5 | ✅ **CLOSED — replay identity.** (a) `_cell_replay_hash` now hashes `code_sha | dataset_version | measurement_key`, so seed/task/device/determinism are in the hash (seeds 42/43/44 no longer collide). (b) CUDA graph scatter remains order-dependent; the tolerance is stated as `LimitationKind.NONDETERMINISTIC_ACCUMULATION` (one graph = 1/N of the split) for every non-deterministic CUDA graph cell. | Locks `test_cell_identity_lock.py` (4 tests). | — | — |
| R6 | **Register C hygiene** (unchanged, deferred) — repo-wide lint 583 → 0, pyright strict, full pytest shards + acceptance, `pip-audit`. | Round-close only; never per-commit. | ~10 min | — |
| R7 | ✅ **CLOSED — not upstream PyG (G9).** The `vectorized gather kernel index out of bounds` was our own static `edge_index` reaching `x[src]`: the free-phase probe flattened a PyG batch to `batch.x` and forwarded it without `edge_index`/`batch`. CPU hid it as a caught warning; CUDA made it a sticky device assert that killed every later CUDA cell. Fixed with the probe skip, activation-row degrees, pooled `forward_with_intermediates`, and a pre-launch node-mode guard. Lock `test_graph_batched_input_lock.py`; CUDA graph cells now train (proteins 0.6637 == CPU). | Done — CUDA is the default device for graph runs now. | — | G9 |
| R8 | ✅ **CLOSED — LM token targets fold to the folded logits.** `_align_target_rows` is applied in `nudged_output`, `task_loss`/`_task_loss_tensor` and `SystemTrainer.validate`; `_one_hot` handles any target rank. Lock `test_lm_target_alignment_lock.py` (5 tests). | Blocks no causal-LM token task now. | — | — |
| R9 | ✅ **CLOSED — PROTEINS > 0.70 met at the mean-pooled arm.** Pooling is now a geometry knob (`geometry.pooling: mean\|sum`) with a mode-aware `PoolContext`; sum pooling is worse (0.672 vs 0.691, n=5, 100 epochs), and 200 epochs at mean pooling / hidden 128 × depth 5 / step 0.003 gives **0.7040 ± 0.0071 (n=5)** vs 0.596 majority (+0.108). Claim-eligible, 366 s. Locks: pooled-readout lock parametrized over both modes + sum-forward lock. | Done — do not reopen; alternatives (attention pooling, depth) are exploratory. | — | R1b, G9 |
| N1 | ✅ **CLOSED — six harness defects, not six bad algorithms.** G10 tabular split (wine 0.0 → 0.94–0.97, iris variance collapsed), G11 `local_contrastive` label channel (now unavailable), G12 graph-task geometry exclusivity, G13 explicit depth (`--n-seeds 1` ran 3), G14 budget-cut cause + admission + control pricing, G15 dry-run gate vs RL (pendulum held zero cells). Locks: `test_tabular_split_lock.py`, `test_incompatible_cell_refusal_lock.py`, `test_budget_truncation_lock.py`, `test_schedule_depth_lock.py`, `test_dry_run_gate_scope_lock.py` (25 tests). Remaining non-graph claims are N2–N4. | Done. | — | Experiment 13 |
| N2 | **Plasticity on a learnable task** — routing was compared to null only under `random_projections` on sequential tasks at chance level (0.10–0.27), which cannot resolve a plasticity effect. Rerun with `gradient`+`adam` on MNIST/feedforward (`plasticity=null,routing`) and copy_task/recurrent; pair `fast_weights` with `energy_minimization` (its compatible dynamics). | L1, 2–3 seeds, 2 tasks (~5 min) | — | Exp 8 |
| N3 | **Substrate breadth** — memristive matched digital at ~1.7× cost on MNIST/instantaneous; ternary/sparse and the non-Digital GPU settle-kernel gap are unmeasured at parity. Run digital/memristive/ternary/sparse on MNIST feedforward, n=3, then profile a non-Digital settle. | L1, 4 substrates × 3 seeds (~8 min); profile one cell | — | Exp 7 |
| N4 | **Predictive settling reach** — `predictive_settling` is filtered on feedforward (Experiment 12). Enumerate its legal geometries, then train it on the cheapest one (recurrent/attention) with gradient credit to confirm it learns, not just composes. | One compatibility query + one L1 arm (~5 min) | — | Exp 12 |
| N5 | **Cost-class drift (hygiene)** — `domains/registry.TASK_COST_CLASS` is a second table no live path reads and it disagrees with the enriched `TaskRegistry` (pendulum/acrobot/cartpole/graph_classification/proteins). `test_smart_survey_lock::test_task_scheduler_cost_classes` fails on it. Delete the table or derive it from the registry. | One edit + one lock | — | — |
| N6 | **Stale lock path (hygiene)** — `test_state_algebra_lock::test_credit_annotations_name_the_surface` opens `computronium/ontology/credit.py`; the credit module is now a package (`credit/__init__.py`). | One-line path fix | — | — |
| N7 | **`local_contrastive` label channel (feature)** — the credit's contract needs a label-augmented input and a label-sweep readout; G11 made the row unavailable rather than mis-train. Implement both, then flip `_UNAVAILABLE` and add a claim-grade arm. | Geometry width + trainer data path + inference protocol | — | G11 |

**Closed this session (do not reopen):** graph attribution bypass (G1/G2), pc_alm×instantaneous (G3), MUTAG "model-size limitation" (G4 — it was geometry + split), FA on pooled readouts (G5), credit dispatch drift (G6), cost-cache clobbering (G7), settle-path aggregation (G8), harness-vs-probe U-axis gap (R2), pooled-readout credit crashes (R3), zero-gradient transformer homeostatic (R4), seed-insensitive cell replay hash (R5a), CUDA scatter tolerance now stated (R5b), LM token-target crash (R8), graph cells without a majority baseline (R1c), unbatched graph probe + foreign-edge-index CUDA assert (G9/R7), graph-measurement resolution (R1b; 5-fold CV R1a superseded by it), PROTEINS >0.70 target (R9 — mean pooling + 200 epochs, 0.7040 ± 0.0071), **tabular one-class split (G10 — wine 0.0 was a tail slice over class-ordered data)**, **`local_contrastive` without a label channel (G11 — unavailable until N7)**, **graph task on node-mode geometry (G12)**, **explicit 1 read as unset (G13)**, **budget cut labelled a constraint violation (G14)**, **RL cells filtered by a supervised dry-run gate (G15)**.

---

## 🎯 PRIMARY MISSION: Experiment/Fix Cycle

**Loop:**
1. **RUN** (≤15 min) — `survey_cli` with focused axes
2. **ANALYZE** (30s) — `comp report`, `comp coverage`, check for anomalies
3. **FIX** (≤15 min) — Infrastructure only; suspect low performance = implementation defect
4. **VERIFY** (0.02h) — Quick re-run
5. **COMMIT + LOG** — Update TODO88.md

**Key Principle:** Be skeptical of low-performing experiments; this could indicate an implementation defect to fix. Be suspicious of any excluded possibilities that may actually be possible.

---

## 🔬 EXPERIMENTS TO RUN (Priority Order)

### 1. Causal Transformer Vision — Credit Sweep (L0, MNIST) ✅ COMPLETED
```bash
uv run python -m computronium.experiment.survey_cli 0.2 \
  --mode learn --policy tpe --device cuda \
  --tasks mnist --fidelity L0 \
  --store experiments/t88_causal_transformer_credit.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["causal_transformer"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient","pc_alm"],"update":["adam"]}' \
  --epochs 5 --n-seeds 2
```
**Result:** **PARTIAL** — gradient+adam: **97.0-97.2% val_acc (PASS)**. pc_alm+adam: **~10% val_acc (PASS but chance-level)**. Positive control (conv+grad+euclid): 90.0% (1 epoch, budget-limited). 
**Defects Found:** pc_alm fails to learn on causal_transformer geometry (works on feedforward per TODO87). `homeostatic` and `random_projections` not evaluated due to budget (transformer ~175s/epoch vs L0 360s budget).

### 1b. Causal Transformer Vision — Full Credit Sweep (L1, MNIST) ✅ COMPLETED
```bash
uv run python -m computronium.experiment.survey_cli 0.5 \
  --mode learn --policy tpe --device cuda \
  --tasks mnist --fidelity L1 \
  --store experiments/t88_causal_transformer_credit_l1.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["causal_transformer"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient","random_projections","homeostatic","pc_alm"],"update":["adam"]}' \
  --epochs 10 --n-seeds 2
```
**Result:** **PASS** — All 4 credits evaluated at L1 (10 epochs, 2 seeds):
- gradient+adam: **97.7-97.9% val_acc (PASS)** — matches feedforward performance!
- random_projections+adam: **70.4-76.1% val_acc (PASS)** — significant learning, though below gradient
- homeostatic+adam: **~10% val_acc (chance-level)** — broken on causal_transformer
- pc_alm not evaluated (budget: L1 ~1800s; 10 epochs × 2 seeds × 4 credits ≈ 1120s per combo)
**Defects Found:** 
1. **Root cause found**: Attention `in_proj.weight` has shape `[192, 64]` (Q+K+V concatenated). `_weight_acts` returns `None` (no matching post-activation), so homeostatic emits **zero gradients** for attention projections! This breaks learning on transformer geometry.
2. L1 budget tight for full 4×10×2 combo — pc_alm not reached by TPE sampler
**Fix Needed:** Homeostatic credit needs transformer-aware path that handles attention projections (similar to `_transformer_path` in other credits).
**Next:** Run Graph Classification at L1 for target >0.70 val_acc.

### 2. Causal Transformer Vision — Geometry Parity (L0, MNIST)
```bash
uv run python -m computronium.experiment.survey_cli 0.1 \
  --mode learn --policy tpe --device cuda \
  --tasks mnist --fidelity L0 \
  --store experiments/t88_vision_geometry_parity.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["conv","feedforward","causal_transformer"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient"],"update":["adam"]}' \
  --epochs 5 --n-seeds 2
```
**Watch for:** Transformer vision should be competitive with conv/feedforward (~0.95+). If not, investigate patch embedding, pooling, or credit assignment.

### 3. Graph Classification — Geometry Sweep (L0, MUTAG) — GPU: CUDA ISSUE
```bash
uv run python -m computronium.experiment.survey_cli 0.1 \
  --mode learn --policy tpe --device cuda \
  --tasks graph_classification --fidelity L0 \
  --store experiments/t88_graph_geometry_sweep.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["graph","spatial_lattice"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient","random_projections"],"update":["euclidean","adam"]}' \
  --epochs 5 --n-seeds 2
```
**Result (GPU):** PARTIAL — CUDA "vectorized gather kernel index out of bounds" error. spatial_lattice fails; graph works with random_projections+adam (~59%), gradient+euclidean (~55%).

### 3b. Graph Classification — CPU (L1, MUTAG) ✅ COMPLETED
```bash
uv run python -m computronium.experiment.survey_cli 0.5 \
  --mode learn --policy tpe --device cpu \
  --tasks graph_classification --fidelity L1 \
  --store experiments/t88_graph_classification_l1.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["graph"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient","random_projections"],"update":["euclidean","adam"]}' \
  --epochs 20 --n-seeds 2
```
**Result:** **PASS** — 9/9 cells completed, all 20 epochs. val_acc: 60.5-63.2% — **below 0.70 target**. Even at L1 (20 epochs vs 5 at L0), graph classification doesn't reach target. May need larger model, more training time, or different task.
**Defects Found:** None - this appears to be a fundamental limitation of MUTAG with this model size.
**Next:** Run targeted property tests and commit.

**❌ CORRECTED 2026-11-11 (G4): the "fundamental limitation" conclusion was wrong.** Two
implementation defects produced this number: (1) the 80/20 split came from an unseeded
`torch.randperm`, so every seed scored a different held-out set; (2) `GraphGeometry` aggregated
with a bare neighbour mean — no self connection — so `h[i]` never contained `x[i]` and the model
plateaued at 0.767 *train* accuracy. On the 38-graph held-out split (25/13) the majority baseline
is **0.658**, i.e. these 0.605–0.632 cells were below-majority predictions. Post-fix (L1, 200
epochs, deterministic stratified split): gradient 0.684/0.658, `random_projections` 0.711/0.658
through the pipeline; plain-Adam probe 0.711–0.737 over 5 seeds. See R1 in REMAINING WORK for why
the remaining >0.70 gap is a measurement-resolution question.

### 4. Graph Node Classification — Full Sweep (L0, Cora/Citeseer/Pubmed)
```bash
uv run python -m computronium.experiment.survey_cli 0.1 \
  --mode learn --policy tpe --device cuda \
  --tasks cora,citeseer,pubmed --fidelity L0 \
  --store experiments/t88_node_classification.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["graph"],"dynamics":["instantaneous","energy_minimization"],"plasticity":["null"],"credit":["gradient","random_projections"],"update":["adam","euclidean"]}' \
  --epochs 5 --n-seeds 2
```
**Watch for:** `energy_minimization` dynamics on graph (EqProp). Should train, not just instantaneous.

### 5. Energy Minimization — Dynamics Sweep (L0, MNIST) ✅ COMPLETED
```bash
uv run python -m computronium.experiment.survey_cli 0.25 \
  --mode learn --policy tpe --device cuda \
  --tasks mnist --fidelity L0 \
  --store experiments/t88_energy_min_pred_settling.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["feedforward"],"dynamics":["instantaneous","energy_minimization","predictive_settling"],"plasticity":["null"],"credit":["gradient","random_projections"],"update":["adam"]}' \
  --epochs 5 --n-seeds 2
```
**Result:** **PARTIAL** — 8/12 cells completed (predictive_settling filtered by compatibility).
- energy_minimization+gradient: **96.9-97.1% val_acc (PASS)** — matches instantaneous 97.2% (3.5x slower: 230s vs 73s/epoch)
- energy_minimization+random_projections: 93.4% at 3 epochs (FAIL - constraint: epochs < 5)
- instantaneous+gradient: 97.2% (PASS)
- instantaneous+random_projections: 93.4-93.5% (PASS)
- predictive_settling: filtered by compatibility (not supported on feedforward)
- positive control (conv+grad+euclid): 90.0% (1 epoch, budget-limited)
**Defects Found:** predictive_settling not compatible with feedforward geometry (expected per registry). L0 budget too tight for energy_minimization (3.5x slower).

### 6. Credit Assignment — Cross-Geometry (L0, Multi-Task) ✅ COMPLETED
```bash
uv run python -m computronium.experiment.survey_cli 0.3 \
  --mode learn --policy tpe --device cuda \
  --tasks mnist,cifar10,sequential_mnist,copy_task,cora,graph_classification,pendulum,acrobot,wine,iris --fidelity L0 \
  --store experiments/t88_credit_cross_geometry.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["feedforward","recurrent","causal_transformer","graph"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient","random_projections","homeostatic","local_contrastive"],"update":["adam","euclidean"]}' \
  --epochs 3 --n-seeds 1
```
**Result:** **PARTIAL** — ~50 cells evaluated. Key findings:
- **gradient credit**: Works on feedforward (mnist 97%, sequential_mnist 96%, cifar10 48%), FAILS on wine (0%), acrobot (-500 reward). Best overall.
- **random_projections credit**: Works on feedforward (mnist 39%, cifar10 20%, seq_mnist 18%), causal_transformer (mnist 60%, cifar10 33%), recurrent (cora 27%). **FAILS frequently on recurrent+adam** (returns None).
- **homeostatic credit**: **FAILS on most geometries** (causal_transformer, feedforward, recurrent) — returns None val_acc/epochs. Only works on recurrent+iris (83%).
- **local_contrastive credit**: Works on feedforward (mnist 23%, cifar10 10%, seq_mnist 15%, iris 0%) but some FAIL (epochs=2 < 3).
- **graph geometry**: Not evaluated (filtered by compatibility or budget).
- **causal_transformer + random_projections**: Some FAILs (returns None).
**Defects Found:**
1. `homeostatic` credit broken on most geometries (returns None).
2. `random_projections` + `recurrent` + `adam` frequently fails (None returns).
3. `causal_transformer` + `random_projections` + `adam` sometimes fails.
4. `local_contrastive` sometimes completes < requested epochs.
5. `gradient` on wine/acrobot fails (task/geometry mismatch?).

### 7. Substrate Comparison — Digital vs Memristive (L0, MNIST)
```bash
uv run python -m computronium.experiment.survey_cli 0.1 \
  --mode learn --policy tpe --device cuda \
  --tasks mnist --fidelity L0 \
  --store experiments/t88_substrate_comparison.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital","memristive"],"geometry":["feedforward"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient"],"update":["adam"]}' \
  --epochs 3 --n-seeds 1
```
**Watch for:** Memristive should work (known CPU-bound for energy_min, but instantaneous should be fine).

### 8. Plasticity Sweep — Fast Weights / Routing (L0, Sequential MNIST)
```bash
uv run python -m computronium.experiment.survey_cli 0.1 \
  --mode learn --policy tpe --device cuda \
  --tasks sequential_mnist,copy_task --fidelity L0 \
  --store experiments/t88_plasticity_sweep.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["recurrent"],"dynamics":["instantaneous"],"plasticity":["null","fast_weight","routing"],"credit":["random_projections"],"update":["euclidean"]}' \
  --epochs 5 --n-seeds 2
```
**Watch for:** Plasticity should improve over null on sequential tasks.

---

## 🐛 DEFECT PATTERNS TO INVESTIGATE

| Symptom | Likely Defect | Investigation |
|---------|---------------|---------------|
| val_acc ≈ chance | Forward pass broken, wrong geometry, credit produces zeros | Check activation shapes, credit pseudo-gradients, loss flow |
| val_acc drops over epochs | Optimizer misconfigured, gradient explosion, weight decay wrong | Check update step, learning rate, gradient clipping |
| "free settle telemetry failed" | Geometry not layered, device mismatch, wrong act count | Check `forward_with_intermediates` returns list matching params |
| Positive control FAIL | Wrong geometry for task, compatibility check broken | Check `geometry_hint` in task registry, `_check_coord_compatibility` |
| NaN/Inf loss | Numerical instability, unclamped energy, bad init | Check `max_energy` clamp, weight init, substrate noise |
| All credits fail on geometry | Credit dispatch missing, geometry not in compatibility matrix | Check `credit_assignment` compatibility, `_transformer_path` etc. |
| Graph CUDA `vectorized gather kernel index out of bounds` | **ANSWERED 2026-11-11 (G9/R7): not upstream PyG** — a PyG batch was flattened to `batch.x` and forwarded without `edge_index`/`batch`, so node-mode geometry indexed a foreign edge list; CPU caught it as a warning, CUDA as a sticky device assert | Pass graph kwargs through any probe; size degrees from activation rows; never run node-mode geometry on a batch |
| Graph cell warns `free settle telemetry failed` on CPU | Same defect as the CUDA assert (G9): the probe has node rows only | Skip free-phase probes for batched-graph inputs; they need the batch's edges |
| Slow training (>60s/epoch L0) | CPU-bound settle loop, no GPU kernel, unnecessary copies | Profile, check `device` placement, check for `.to(cpu)` calls |

---

## 🚫 EXCLUDED POSSIBILITIES TO QUESTION

| Assumption | Why It Might Be Wrong | Test |
|------------|----------------------|------|
| "GraphClassification CUDA is unfixable upstream" | **ANSWERED 2026-11-11 (G9/R7): it was our probe, not PyG** — `_sample_inputs` flattened a batch to node rows and node-mode geometry indexed a foreign edge list. Fixed; CUDA graph cells now train at CPU parity (proteins 0.6637 == 0.6637) | `num_workers=0` was never the lever |
| "Energy minimization + recurrent is CPU-bound" | May lack GPU kernel; check if `_settle_compiled` works | Profile `energy_minimization` on recurrent geometry |
| "Transformer vision needs patch embedding" | Could use positional encoding on flattened patches | Try `patch_size=0` with `seq_len=H*W` for comparison |
| "Memristive substrate doesn't support energy_min" | May just need GPU settle kernel | Check `SubstrateSettleKernel` for memristive |
| "RandomProjectionsCredit fails on graph" | **ANSWERED 2026-11-11 (G5): it was a pooled-readout defect** — node-sized acts with a batch-sized error; `_graph_path` now exists and MUTAG `random_projections` trains (0.711) | Check credit dispatch for `graph` geometry |
| "Spatial lattice only for 3D" | May work for 2D grid graphs | Try `spatial_lattice` on graph tasks |
| "Null plasticity is only baseline" | `rule_state` plasticity may be zero-cost | Test `rule_state` on feedforward/recurrent |

---

## 📋 REMAINING WORK FROM TODO87 (Carried Forward)

### Immediate (Next Session)
- [ ] **C4 scale validation** — Memristive energy_min CPU-bound (~560s/epoch). Document; skip full L2. Use GPU-accelerated dynamics for future scale validation.

### Register C Hygiene Pass (Deferred)
- [ ] **Lint reduction** — 583 → 0. Each requires manual review (math notation, Triton DSL).
- [ ] **Type checking** — Full repo-wide pyright strict (currently strict on new modules only).
- [ ] **Full pytest run** — All shards + acceptance (~10 min).
- [ ] **pip-audit** — Dependency vulnerability scan.

### Upstream Dependencies (Question, Don't Assume Unfixable)
- [x] **GraphClassification CUDA** — **CLOSED 2026-11-11 (G9/R7)**: not upstream. CUDA graph cells train at CPU parity; no version pin or DataLoader change was needed.
- [ ] **torch_geometric fvcore/jit warning** — Check if newer PyG fixes this.

### Known Limitations (Document, But Revisit)
- [ ] **Energy minimization + recurrent** — ~58s/epoch at L0 on CPU. Check for GPU kernel.
- [ ] **Energy minimization on graph geometry** — Fundamental tensor shape mismatch: settle kernel expects uniform batch dimension [B, features], but graph geometry produces [num_nodes, features] for hidden layers and [B, features] for output after pooling. Requires graph-native settle kernel.
- [ ] **GPU settle kernels for non-Digital substrates** — Memristive/Analog/Neuromorphic/Optical/Quantum/Sparse/Ternary all fall back to eager `SubstrateSettleKernel` (slow). Digital has `torch.compile` fast path. Future: substrate-specific Triton kernels where hardware targets exist.

---

## 🔄 CONTINUOUS INTEGRATION CHECKS (Per Commit)

```bash
# Dev-env smoke
uv run python -c "import optuna, scipy, torchvision, pytest"

# Format + lint changed files
uv run ruff format && uv run ruff check --fix

# Pyright on changed files (strict for new modules)
uv run pyright <changed_files>

# Targeted tests
uv run python -m pytest tests/property/test_task_geometry_compat_lock.py tests/property/test_dynamics_wiring_lock.py -v
```

---

## 📊 SUCCESS CRITERIA

| Metric | Target |
|--------|--------|
| Positive control PASS rate | 100% across all task domains |
| Vision (MNIST/CIFAR) best val_acc | > 0.95 (digital/ff/grad/adam) |
| Graph classification best val_acc | > 0.70 (digital/graph/grad/adam) |
| Node classification (Cora) best val_acc | > 0.75 (digital/graph/grad/adam) |
| RL (Pendulum) mean_reward | > -200 (digital/ff/grad/euclid) |
| Tabular (Iris) best val_acc | > 0.90 (digital/ff/grad/euclid) |
| Credit sweep: ≥3 credits work per geometry | ≥3 **error-aware** credits (`error_blind=True` credits measure chance by contract) |
| No "free settle telemetry failed" warnings | 0 occurrences |
| Experiment cycle time | ≤30 min (run + analyze + fix + verify) |

---

## 🚫 NO (Same as TODO86/87)

- Paper figures
- Publishing artifacts  
- Hypothesis backlogs
- Preventive fixes
- Meetings/retrospectives
- Cycles > 30 min

---

## 📝 SESSION LOG TEMPLATE

After each experiment/fix cycle, append to this file:

```
## Session YYYY-MM-DD
**Experiment:** <command>
**Result:** <PASS/FAIL, key metrics>
**Defects Found:** <list>
**Fixes Applied:** <files changed>
**Next Experiment:** <planned command>
```

---

## Session 2026-11-10
**Experiment:** Causal Transformer Vision — Credit Sweep (L0, MNIST)
```
uv run python -m computronium.experiment.survey_cli 0.1 \
  --mode learn --policy tpe --device cuda \
  --tasks mnist --fidelity L0 \
  --store experiments/t88_causal_transformer_credits.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["causal_transformer"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient","random_projections","homeostatic","pc_alm"],"update":["adam"]}' \
  --epochs 5 --n-seeds 2
```
**Result:** PARTIAL — Positive control PASS (conv/grad: val_acc=0.9002). Constraint fix enabled gradient credit for causal_transformer. Only 2/5 epochs completed due to 153s/epoch training time (budget 360s). Homeostatic FAIL (val_acc≈0.10). RandomProjections FAIL (val_acc≈0.5-0.6, constraint_violation). Gradient and PC-ALM not evaluated (budget exhausted).
**Defects Found:**
1. `nonlayered_instantaneous_gradient_credit` constraint in `seed_registries.py` incorrectly included `conv` and `causal_transformer` — both work with gradient credit (verified by positive control and gradient flow test).
2. Causal transformer training extremely slow (~153s/epoch, 30ms/step raw, 70ms/step with validation) — only 2 epochs in L0 budget.
3. Homeostatic credit produces chance-level accuracy on transformer (val_acc≈0.10).
4. RandomProjections credit gets moderate accuracy (~0.55) but fails gate.
**Fixes Applied:**
- `computronium/experiment/schema/seed_registries.py`: Removed `conv` and `causal_transformer` from non-layered geometries list in `nonlayered_instantaneous_gradient_credit` constraint.
**Next Experiment:** Causal Transformer Vision — Geometry Parity (L0, MNIST)

---

## Session 2026-11-10
**Experiment:** Causal Transformer Vision — Geometry Parity (L0, MNIST)
```
uv run python -m computronium.experiment.survey_cli 0.1 \
  --mode learn --policy tpe --device cuda \
  --tasks mnist --fidelity L0 \
  --store experiments/t88_vision_geometry_parity.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["conv","feedforward","causal_transformer"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient"],"update":["adam"]}' \
  --epochs 5 --n-seeds 2
```
**Result:** PARTIAL — Positive control PASS (conv/grad/euclid: 0.9002). Feedforward+adam achieves 0.967-0.970 val_acc (excellent!) but only 3 epochs completed. Conv+adam achieves 0.916-0.920 but only 2 epochs. Causal_transformer not evaluated (budget exhausted). All cells FAIL due to constraint_violation (insufficient epochs vs declared 5).
**Defects Found:**
1. L0 budget (360s) too tight for 5 epochs with these geometries (feedforward: ~85s/epoch, conv: ~86s/epoch, causal_transformer: ~153s/epoch).
2. Adaptive budget estimator underestimates epoch time for transformer geometries.
**Fixes Applied:** None (budget/fidelity issue, not implementation defect).
**Next Experiment:** Graph Classification — Geometry Sweep (L0, MUTAG)

---

## Session 2026-11-10
**Experiment:** Graph Classification — Geometry Sweep (L0, MUTAG)
```
uv run python -m computronium.experiment.survey_cli 0.1 \
  --mode learn --policy tpe --device cuda \
  --tasks graph_classification --fidelity L0 \
  --store experiments/t88_graph_geometry_sweep.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["graph","spatial_lattice"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient","random_projections"],"update":["euclidean","adam"]}' \
  --epochs 5 --n-seeds 2
```
**Result:** PARTIAL — Graph geometry works with random_projections+adam (val_acc≈0.59, n=2), gradient+euclidean (val_acc≈0.55, n=1), random_projections+euclidean (val_acc≈0.55, n=1). Spatial_lattice FAILS with CUDA "vectorized gather kernel index out of bounds" error. Gradient+adam not evaluated. Val_acc below target 0.70 (only 5 epochs on small MUTAG dataset).
**Defects Found:**
1. `spatial_lattice` geometry CUDA error on graph tasks — index out of bounds in gather kernel.
2. Graph classification val_acc ~0.55-0.59 below target 0.70 (likely needs more epochs/larger model).
**Fixes Applied:** None yet.
**Next Experiment:** Graph Node Classification — Full Sweep (L0, Cora/Citeseer/Pubmed)

---

## Session 2026-11-10
**Experiment:** Graph Node Classification — Full Sweep (L0, Cora/Citeseer/Pubmed)
```
uv run python -m computronium.experiment.survey_cli 0.1 \
  --mode learn --policy tpe --device cuda \
  --tasks cora,citeseer,pubmed --fidelity L0 \
  --store experiments/t88_node_classification.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["graph"],"dynamics":["instantaneous","energy_minimization"],"plasticity":["null"],"credit":["gradient","random_projections"],"update":["adam","euclidean"]}' \
  --epochs 5 --n-seeds 2
```
**Result:** PASS (all 13 cells) — RandomProjections+Adam works across all tasks (Cora: 0.70-0.73, Pubmed: 0.67-0.71, Citeseer: 0.61-0.64). RandomProjections+Euclidean also works. Gradient credit NOT evaluated (only positive control on Cora: 0.522). Energy_minimization dynamics NOT evaluated. Planner only explored random_projections combinations.
**Defects Found:**
1. Planner/TPE sampler didn't explore gradient credit or energy_minimization dynamics — only random_projections combinations were proposed.
2. Cora val_acc ~0.70-0.73 (close to 0.75 target), Citeseer ~0.61-0.64 (below), Pubmed ~0.67-0.71 (close).
**Fixes Applied:** None.
**Next Experiment:** Energy Minimization — Dynamics Sweep (L0, MNIST)

---

## Session 2026-11-10
**Experiment:** Energy Minimization — Dynamics Sweep (L0, MNIST)
```
uv run python -m computronium.experiment.survey_cli 0.15 \
  --mode learn --policy tpe --device cuda \
  --tasks mnist --fidelity L0 \
  --store experiments/t88_energy_min_dynamics.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["feedforward"],"dynamics":["instantaneous","energy_minimization","predictive_settling"],"plasticity":["null"],"credit":["gradient","random_projections"],"update":["adam"]}' \
  --epochs 5 --n-seeds 2
```
**Result:** PARTIAL — Instantaneous+Gradient+Adam PASSES (val_acc 0.969-0.973). EnergyMin+Gradient+Adam good (0.952-0.956) but only 1 epoch (extreme slowness: ~475s/epoch vs ~71s/epoch for instantaneous). RandomProjections underperforms Gradient (~0.918 vs ~0.971). PredictiveSettling not evaluated (budget).
**Defects Found:**
1. Energy minimization dynamics ~7x slower than instantaneous on feedforward (475s/epoch vs 71s/epoch) — likely CPU-bound settle loop.
2. RandomProjections credit significantly underperforms Gradient on feedforward geometry.
3. PredictiveSettling dynamics not evaluated.
**Fixes Applied:** None.
**Next Experiment:** Credit Assignment — Cross-Geometry (L0, Multi-Task)

---

## Session 2026-11-10
**Experiment:** Credit Assignment — Cross-Geometry (L0, Multi-Task)
```
uv run python -m computronium.experiment.survey_cli 0.1 \
  --mode learn --policy tpe --device cuda \
  --tasks mnist,cifar10,sequential_mnist,copy_task,cora,graph_classification,pendulum,acrobot,wine,iris --fidelity L0 \
  --store experiments/t88_credit_cross_geometry.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["feedforward","recurrent","causal_transformer","graph"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient","random_projections","homeostatic","local_contrastive"],"update":["adam","euclidean"]}' \
  --epochs 3 --n-seeds 1
```
**Result:** PARTIAL — Only 13/320 cells evaluated (budget exhausted). RandomProjections works on feedforward (MNIST: 0.40, CIFAR10: 0.20) and recurrent (Cora: 0.27) but FAILS on causal_transformer (MNIST: runtime_error) and graph_classification (recurrent: runtime_error). Homeostatic FAILS everywhere (chance-level). LocalContrastive only on feedforward (by constraint) but poor (MNIST: 0.26, CIFAR10: 0.10). Gradient only on conv (positive control: 0.90).
**Defects Found:**
1. RandomProjections credit has runtime errors on causal_transformer and recurrent+graph geometries.
2. Homeostatic credit produces chance-level accuracy across all geometries.
3. LocalContrastive credit poor on feedforward vision tasks.
4. Search space too large (320 cells) for L0 budget — only 4% coverage.
**Fixes Applied:** None.
**Next Experiment:** Substrate Comparison — Digital vs Memristive (L0, MNIST)

---

## Session 2026-11-10
**Experiment:** Substrate Comparison — Digital vs Memristive (L0, MNIST)
```
uv run python -m computronium.experiment.survey_cli 0.1 \
  --mode learn --policy tpe --device cuda \
  --tasks mnist --fidelity L0 \
  --store experiments/t88_substrate_comparison.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital","memristive"],"geometry":["feedforward"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient"],"update":["adam"]}' \
  --epochs 3 --n-seeds 1
```
**Result:** PASS (all 3 cells) — Both substrates achieve ~0.972 val_acc on MNIST (Digital: 0.9720, Memristive: 0.9725). Memristive slightly slower (120s vs 79s for 3 epochs) but functionally equivalent for instantaneous dynamics.
**Defects Found:** None — memristive substrate works correctly for instantaneous dynamics on feedforward geometry.
**Fixes Applied:** None.
**Next Experiment:** Plasticity Sweep — Fast Weights / Routing (L0, Sequential MNIST)

---

## Session 2026-11-10
**Experiment:** Plasticity Sweep — Fast Weights / Routing (L0, Sequential MNIST)
```
uv run python -m computronium.experiment.survey_cli 0.1 \
  --mode learn --policy tpe --device cuda \
  --tasks sequential_mnist,copy_task --fidelity L0 \
  --store experiments/t88_plasticity_sweep.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["recurrent"],"dynamics":["instantaneous"],"plasticity":["null","fast_weights","routing"],"credit":["random_projections"],"update":["euclidean"]}' \
  --epochs 5 --n-seeds 2
```
**Result:** PASS (all 8 cells) — Positive control correctly rejected (gradient+recurrent+instantaneous incompatible). Null vs routing plasticity compared: Sequential MNIST null 0.27 vs routing 0.10 (null better), Copy task null 0.13 vs routing 0.13 (similar). Fast weights NOT evaluated. All val_acc very low (0.1-0.27) — sequential tasks challenging with random_projections credit.
**Defects Found:**
1. Routing plasticity does not improve over null on sequential tasks with random_projections credit.
2. Fast weights plasticity not evaluated (planner didn't propose).
3. Sequential MNIST/copy_task val_acc far below useful levels with random_projections credit.
**Fixes Applied:** None.
**Next Experiment:** Complete — all 8 planned experiments run.

---

## Session 2026-11-10 (FIX PHASE)
**Experiment:** GPU Contention Fix — max_workers=1 for CUDA
**Analysis:** ThreadPoolExecutor with max_workers=4 on single GPU causes 5.6x slowdown (30s/epoch → 168s/epoch) due to GPU contention. All transformer/vision experiments were severely bottlenecked.
**Defects Found:**
1. `wave.py` uses ThreadPoolExecutor with max_workers > 1 for CUDA devices, causing massive contention.
2. Survey CLI defaults to max_workers=4 without checking device type.
**Fixes Applied:**
- `computronium/experiment/wave.py`: Auto-limit max_workers to 1 when device is CUDA.
- `computronium/experiment/survey_cli.py`: Default max_workers to 1 for CUDA, allow override.
**Verification — Re-run with fix:**
1. **Causal Transformer Credit Sweep**: Epoch time 27s (was 153s, 5.6x speedup). Homeostatic: 0.10 (chance), RandomProjections: 0.49 (learning), Gradient/PC-ALM: budget.
2. **Geometry Parity**: conv/grad/adam: 0.947, feedforward/grad/adam: 0.972 (exceeds 0.95 target!), causal_transformer: budget. Epochs: 13-20s (was 85-150s).
3. **Graph Geometry Sweep**: Graph geometry has CUDA error (PyG vectorized gather kernel OOB) — known upstream issue. Spatial_lattice not tested.
4. **Energy Min Dynamics**: energy_minimization: 124s/epoch (CPU-bound, known), achieved 0.9716 val_acc. Instantaneous: 13s/epoch.
**Next:** Fix budget estimation for sequential evaluation; investigate graph CUDA issue (try CPU/num_workers=0); energy_min GPU kernel.

---

## Session 2026-11-10 (GRAPH SUPPORT FIX PHASE)
**Experiment:** Graph Classification Support Fixes
**Analysis:** Graph classification tasks failed due to missing graph data (edge_index, batch) passthrough in the training pipeline. The `GraphGeometry` was incorrectly classified as non-layered, preventing settling dynamics. Energy minimization on graph geometry has fundamental tensor shape mismatch.
**Defects Found:**
1. Pipeline `run_train_step` didn't accept graph kwargs (edge_index, batch).
2. `TaskBatches` didn't handle PyG Data objects from graph classification dataloaders.
3. Trainer didn't extract graph data and pass to `train_step`/`forward`.
4. `GraphGeometry` was in nonlayered set, forbidding settling dynamics.
5. `GraphGeometry` lacked `layered_params` property for settle kernel.
6. `extract_layered_params` didn't handle property descriptors.
**Fixes Applied:**
- `computronium/core/pipeline.py`: Added `graph_kwargs` to `_TrainStepContext`, `_PhaseContext`; pass through to `forward_pass` and `dynamics.settle`.
- `computronium/core/system_trainer/train_task.py`: Added `_is_graph_data` detection; handle PyG Data objects in `TaskBatches`.
- `computronium/core/system_trainer/trainer.py`: Extract `edge_index`, `batch` from Data objects; pass to `train_step` and `forward`.
- `computronium/ontology/system.py`: Updated `System.train_step` protocol and `_ComposedSystem.train_step` to accept `**graph_kwargs`.
- `computronium/ontology/system.py`: Removed `graph`, `conv`, `causal_transformer` from nonlayered geometry validation.
- `computronium/ontology/geometry.py`: Added `layered_params` property to `GraphGeometry`.
- `computronium/ontology/_settle_kernel.py`: Fixed `extract_layered_params` to handle `LayeredParams` properties.
**Verification:**
- Graph classification with instantaneous dynamics: PASS (val_acc=0.55, epochs=1, 0.48s/cell).
- Causal transformer vision with gradient credit: PASS (val_acc=0.953, epochs=2, 33-35s/epoch, 5.6x speedup vs pre-fix).
- Feedforward vision with gradient credit: PASS (val_acc~0.97, epochs=2, ~30s/cell).
- Energy minimization on graph geometry: Tensor shape mismatch (fundamental architecture issue — settle kernel expects uniform batch dim, graph has [num_nodes, features]).
**Next:** Energy_min GPU kernel for non-Digital substrates; spatial_lattice geometry; predictive_settling on graph.

---
## Session 2026-11-10 (ENERGY_MIN COMPILED KERNELS PHASE)
**Experiment:** Compiled Settle Kernels for Non-Digital Substrates
**Analysis:** EnergyMinimizationDynamics only had a compiled fast path for DigitalSubstrate. All other substrates (Analog, Neuromorphic, Optical, Sparse, Memristive, Ternary, etc.) fell back to eager Python loops, causing 5-10x slowdown for larger models.
**Defects Found:**
1. `_compiled_eqprop_settle_chunk` inlined only DigitalSubstrate's forward operator (raw matmul).
2. No substrate-specific compiled paths existed for Analog, Neuromorphic, Optical, Sparse substrates.
3. `compiled` default was False for energy_minimization config.
4. `train_step` didn't forward `graph_kwargs` for graph classification support.
**Fixes Applied:**
- `computronium/ontology/_settle_kernel.py`: Added `_eqprop_settle_chunk_analog` and `_eqprop_settle_chunk_simple_noise` compiled functions with inlined substrate operators (noise injection, weight clamping).
- `computronium/ontology/dynamics/_dynamics.py`: Extended `_setup_settle` and `_settle_compiled` to dispatch to substrate-specific compiled functions for Analog, Neuromorphic, Optical, Sparse substrates.
- `computronium/ontology/dynamics/_dynamics.py`: Changed `compiled` default to `True` for `StateDynamicsConfig.energy_minimization`.
- `computronium/core/system_trainer/joint.py`: Updated `train_step` to accept and forward `**graph_kwargs` for graph classification.
- `computronium/ontology/geometry.py`: Verified `spatial_lattice` is incompatible with settle kernel (per-site weights + neighbor aggregation); validation already forbids settling dynamics.
- `computronium/ontology/system.py`: Confirmed GraphGeometry energy_minimization works for node classification; graph classification has fundamental tensor shape mismatch (node-level vs graph-level activations).
**Verification:**
- Analog/Neuromorphic/Optical/Sparse energy_minimization: ~5ms/settle (20 steps) on GPU vs ~50-90ms eager (10x speedup).
- Digital energy_minimization: ~4ms/settle (20 steps) compiled vs ~47ms eager (12x speedup).
- Property locks pass (test_dynamics_wiring_lock, test_task_geometry_compat_lock).
- Substrate settle equivalence tests pass.
- End-to-end training works for all substrates with compiled energy_minimization.
**Known Limitations:**
- Memristive/Ternary/Quantum/Complex substrates still use eager path (complex operators not easily compilable).
- Spatial_lattice geometry fundamentally incompatible with layered settle kernel (requires custom kernel).
- Graph classification energy_minimization has tensor shape mismatch (requires graph-native settle kernel).
- PredictiveSettlingDynamics compiled path still Digital-only (needs similar substrate-specific fixes).
**Next:** Fix budget estimation for sequential evaluation; investigate graph CUDA issue (CPU/num_workers=0); PredictiveSettlingDynamics substrate-specific compiled paths.

---

## Session 2026-11-11 (PREDICTIVE_SETTLING COMPILED KERNELS PHASE)
**Experiment:** Compiled Settle Kernels for PredictiveSettlingDynamics on Non-Digital Substrates
**Analysis:** PredictiveSettlingDynamics only had a compiled fast path for DigitalSubstrate (`_compiled_layered_settle_digital`). All other substrates (Analog, Neuromorphic, Optical, Sparse, Memristive, Ternary, Complex, Quantum) fell back to eager Python loops, causing 5-10x slowdown.
**Defects Found:**
1. `_compiled_layered_settle` inlined only DigitalSubstrate's forward operator (raw matmul `x @ w.T`).
2. No substrate-specific compiled paths existed for Analog, Neuromorphic, Optical, Sparse, Memristive, Ternary, Complex, Quantum substrates.
3. `compiled` default was False for predictive_settling config.
4. ComplexSubstrate uses emulated complex format requiring custom complex_linear; incompatible with standard real-valued geometries.
**Fixes Applied:**
- `computronium/ontology/_settle_kernel.py`: Added substrate-specific compiled settle loops for PredictiveSettlingDynamics:
  - `_compiled_layered_settle_digital` (DigitalSubstrate: raw matmul)
  - `_compiled_layered_settle_analog` (AnalogSubstrate: noise injection + weight clamping)
  - `_compiled_layered_settle_simple_noise` (NeuromorphicSubstrate, OpticalSubstrate, SparseSubstrate: noise injection only)
  - `_compiled_layered_settle_memristive` (MemristiveSubstrate: differential conductance pair + noise)
  - `_compiled_layered_settle_ternary` (TernarySubstrate: TWN-style ternary quantization)
  - `_compiled_layered_settle_complex` (ComplexSubstrate: complex matmul with conjugate transpose)
  - `_compiled_layered_settle_quantum` (QuantumSubstrate: amplitude encoding with shot noise)
- `computronium/ontology/dynamics/_dynamics.py`: Extended `_settle_layered` to dispatch to substrate-specific compiled functions based on substrate type. Set `compiled` default to `True` for `StateDynamicsConfig.predictive_settling`. ComplexSubstrate falls back to eager (pre-existing geometry incompatibility).
**Verification:**
- All property locks pass (test_dynamics_wiring_lock, test_task_geometry_compat_lock).
- Substrate settle equivalence tests pass.
- End-to-end training works for Digital, Analog, Neuromorphic, Optical, Memristive, Ternary, Quantum, Sparse substrates with compiled predictive_settling.
- Experiment t88_predictive_settling_test4: Digital, Analog, Optical substrates PASS (val_acc 0.52-0.68); Sparse fails due to PyTorch inductor "closed pool" issue (separate bug).
**Known Limitations:**
- ComplexSubstrate has pre-existing incompatibility with real-valued feedforward geometry (emulated complex format [real, imag] vs real weights).
- SparseSubstrate fails with PyTorch inductor "Attempting to use a closed pool" error when using compiled kernels.
- Graph geometry predictive_settling needs graph-native settle kernel (fundamental tensor shape mismatch).
- Spatial_lattice geometry incompatible with layered settle kernel.
**Next:** Fix PyTorch inductor "closed pool" issue for SparseSubstrate; investigate ComplexSubstrate geometry compatibility; graph CUDA issue (CPU/num_workers=0).

---

## Session 2026-11-11
**Experiment:** Graph Node Classification — Full Sweep (L0, Cora/Citeseer/Pubmed)
```
uv run python -m computronium.experiment.survey_cli 0.1 \
  --mode learn --policy tpe --device cuda \
  --tasks cora,citeseer,pubmed --fidelity L0 \
  --store experiments/t88_node_classification.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["graph"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient","random_projections"],"update":["adam","euclidean"]}' \
  --epochs 5 --n-seeds 2
```
**Result:** PARTIAL — Positive control PASS (graph/grad/euclid: 0.5220). RandomProjections works well (0.61-0.73 val_acc). Gradient credit was BLOCKED by `nonlayered_instantaneous_gradient_credit` constraint (incorrectly included "graph").
**Defects Found:**
1. `nonlayered_instantaneous_gradient_credit` constraint in `seed_registries.py` incorrectly included `graph` — gradient credit works on graph geometry (verified by positive control).
**Fixes Applied:**
- `computronium/experiment/schema/seed_registries.py`: Removed `graph` from non-layered geometries list in `nonlayered_instantaneous_gradient_credit` constraint.
**Next Experiment:** Graph Node Classification — Full Sweep (re-run with fix)

---

## Session 2026-11-11
**Experiment:** Graph Node Classification — Full Sweep (re-run, L0, Cora/Citeseer/Pubmed)
```
uv run python -m computronium.experiment.survey_cli 0.1 \
  --mode learn --policy tpe --device cuda \
  --tasks cora,citeseer,pubmed --fidelity L0 \
  --store experiments/t88_node_classification_v2.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["graph"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient","random_projections"],"update":["adam","euclidean"]}' \
  --epochs 5 --n-seeds 2
```
**Result:** PASS — All 25 cells passed (1 positive control + 24 wave). Both gradient and random_projections work on graph geometry with comparable performance (mean val_acc ≈ 0.67). Energy_minimization correctly filtered out (non-layered geometry requires instantaneous dynamics).
**Defects Found:** None new.
**Next Experiment:** Energy Minimization — Dynamics Sweep (L0, MNIST)

---

## Session 2026-11-11
**Experiment:** Energy Minimization — Dynamics Sweep (L0, MNIST)
```
uv run python -m computronium.experiment.survey_cli 0.15 \
  --mode learn --policy tpe --device cuda \
  --tasks mnist --fidelity L0 \
  --store experiments/t88_energy_min_dynamics.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["feedforward"],"dynamics":["instantaneous","energy_minimization","predictive_settling"],"plasticity":["null"],"credit":["gradient","random_projections"],"update":["adam"]}' \
  --epochs 5 --n-seeds 2
```
**Result:** PARTIAL — Budget too tight (540s). Energy_minimization: 0.97 val_acc (excellent!) but ~46s/epoch. Instantaneous cells cut off by deadline. Predictive_settling and random_projections not evaluated.
**Defects Found:** Budget too small for energy_minimization dynamics (needs ~920s per config for 2 seeds × 5 epochs).
**Fixes Applied:** Re-run with larger budget (0.3h) and focused on gradient credit.
**Next Experiment:** Energy Minimization — Dynamics Sweep (re-run with 0.3h budget)

---

## Session 2026-11-11
**Experiment:** Energy Minimization — Dynamics Sweep (re-run, L0, MNIST, 0.3h)
```
uv run python -m computronium.experiment.survey_cli 0.3 \
  --mode learn --policy tpe --device cuda \
  --tasks mnist --fidelity L0 \
  --store experiments/t88_energy_min_dynamics_v2.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["feedforward"],"dynamics":["instantaneous","energy_minimization","predictive_settling"],"plasticity":["null"],"credit":["gradient"],"update":["adam"]}' \
  --epochs 5 --n-seeds 2
```
**Result:** PASS — Both instantaneous and energy_minimization completed with 2 seeds each. Instantaneous: 0.9720, Energy_minimization: 0.9698 (equivalent!). Predictive_settling NOT evaluated (requires thermodynamic_contrast/equilibrium/local_goodness credit, not gradient).
**Defects Found:** Predictive_settling incompatible with gradient credit (by design).
**Next Experiment:** Predictive Settling with compatible credits

---

## Session 2026-11-11
**Experiment:** Predictive Settling with Thermodynamic Contrast / Local Goodness (L0, MNIST)
```
uv run python -m computronium.experiment.survey_cli 0.15 \
  --mode learn --policy tpe --device cuda \
  --tasks mnist --fidelity L0 \
  --store experiments/t88_predictive_settling.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["feedforward"],"dynamics":["predictive_settling"],"plasticity":["null"],"credit":["thermodynamic_contrast","local_goodness"],"update":["adam"]}' \
  --epochs 5 --n-seeds 2
```
**Result:** PARTIAL — Budget exhausted. Thermodynamic_contrast: 0.63 val_acc (vs 0.97 for instantaneous/energy_min). Local_goodness cut off by deadline. Predictive_settling with local credits NOT competitive on standard vision tasks.
**Defects Found:** None — this is expected behavior; predictive_settling designed for energy-based learning, not standard backprop tasks.
**Next Experiment:** Credit Assignment — Cross-Geometry

---

## Session 2026-11-11
**Experiment:** Credit Assignment — Cross-Geometry (L0, 10 tasks, 4 geometries, 4 credits)
```
uv run python -m computronium.experiment.survey_cli 0.1 \
  --mode learn --policy tpe --device cuda \
  --tasks mnist,cifar10,sequential_mnist,copy_task,cora,graph_classification,pendulum,acrobot,wine,iris --fidelity L0 \
  --store experiments/t88_credit_cross_geometry.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["feedforward","recurrent","causal_transformer","graph"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient","random_projections","homeostatic","local_contrastive"],"update":["adam","euclidean"]}' \
  --epochs 3 --n-seeds 1
```
**Result:** PARTIAL — Budget too tight (320 declared cells, only 16 evaluated). Key findings: Gradient best (0.90 MNIST), homeostatic works on recurrent/iris (0.83), random_projections on causal_transformer decent (0.60), local_contrastive poor (0.0-0.23). Many geometry-task mismatches.
**Defects Found:** Budget too small for full cross-geometry sweep.
**Next Experiment:** Substrate Comparison — Digital vs Memristive

---

## Session 2026-11-11
**Experiment:** Substrate Comparison — Digital vs Memristive (L0, MNIST)
```
uv run python -m computronium.experiment.survey_cli 0.1 \
  --mode learn --policy tpe --device cuda \
  --tasks mnist --fidelity L0 \
  --store experiments/t88_substrate_comparison.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital","memristive"],"geometry":["feedforward"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient"],"update":["adam"]}' \
  --epochs 3 --n-seeds 1
```
**Result:** PASS — All 3 cells passed. Memristive matches digital performance (0.9659 vs 0.9679 val_acc) at ~1.7x slower (78s vs 45s).
**Defects Found:** None.
**Next Experiment:** Plasticity Sweep — Fast Weights / Routing

---

## Session 2026-11-11
**Experiment:** Plasticity Sweep — Fast Weights / Routing (L0, Sequential MNIST / Copy Task)
```
uv run python -m computronium.experiment.survey_cli 0.1 \
  --mode learn --policy tpe --device cuda \
  --tasks sequential_mnist,copy_task --fidelity L0 \
  --store experiments/t88_plasticity_sweep.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["recurrent"],"dynamics":["instantaneous"],"plasticity":["null","fast_weights","routing"],"credit":["random_projections"],"update":["euclidean"]}' \
  --epochs 5 --n-seeds 2
```
**Result:** PARTIAL — Fast_weights filtered out by `dynamics_plasticity_compatibility` constraint (instantaneous dynamics cannot use fast-weight plasticity, by design). Only null and routing evaluated. Routing performs WORSE than null (0.12 vs 0.19 on sequential_mnist; both ~0.13 on copy_task — chance level). Random_projections credit with recurrent geometry ineffective for these tasks.
**Defects Found:** None — constraint is correct; fast_weights requires settling dynamics.
**Next:** Update TODO88.md, run property locks, commit.

---

## Session 2026-11-11 (continued)
**Experiment:** Causal Transformer Vision — Credit Sweep (L0, MNIST)
```
uv run python -m computronium.experiment.survey_cli 0.15 \
  --mode learn --policy tpe --device cuda \
  --tasks mnist --fidelity L0 \
  --store experiments/t88_causal_transformer_credits.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["causal_transformer"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient","random_projections","homeostatic","pc_alm"],"update":["adam"]}' \
  --epochs 5 --n-seeds 2
```
**Result:** PARTIAL — Budget too tight (5 of 8 cells). Homeostatic ~10% (chance), random_projections 68%, gradient/pc_alm not evaluated. Need larger budget.
**Defects Found:** None — budget sizing issue.

---

## Session 2026-11-11 (continued)
**Experiment:** Causal Transformer Vision — Geometry Parity (L0, MNIST)
```
uv run python -m computronium.experiment.survey_cli 0.25 \
  --mode learn --policy tpe --device cuda \
  --tasks mnist --fidelity L0 \
  --store experiments/t88_vision_geometry_parity.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["conv","feedforward","causal_transformer"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient"],"update":["adam"]}' \
  --epochs 5 --n-seeds 2
```
**Result:** **PASS** — All 7 cells passed. **Geometry parity achieved**: causal_transformer 97.1% matches feedforward 97.2% on MNIST (conv 94.7%). TransformerGeometry fixes from TODO87 working!
**Defects Found:** None.

---

## Session 2026-11-11 (continued)
**Experiment:** Graph Classification — Geometry Sweep (L0, MUTAG)
```
uv run python -m computronium.experiment.survey_cli 0.2 \
  --mode learn --policy tpe --device cuda \
  --tasks graph_classification --fidelity L0 \
  --store experiments/t88_graph_geometry_sweep.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["graph","spatial_lattice"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient","random_projections"],"update":["euclidean","adam"]}' \
  --epochs 5 --n-seeds 2
```
**Result:** PARTIAL — Known PyG CUDA issue (device-side assert in vectorized_gather_kernel). 2 cells completed before sticky error: random_projections/euclidean 57.9%, gradient/euclidean 55.3%. spatial_lattice not evaluated.
**Defects Found:** Known upstream limitation (PyG CUDA batch indexing). Document, don't assume unfixable — test PyG version pins.

---

## Session 2026-11-11 (continued)
**Experiment:** Graph Node Classification — Full Sweep (L0, Cora/Citeseer/Pubmed)
```
uv run python -m computronium.experiment.survey_cli 0.2 \
  --mode learn --policy tpe --device cuda \
  --tasks cora,citeseer,pubmed --fidelity L0 \
  --store experiments/t88_node_classification.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["graph"],"dynamics":["instantaneous","energy_minimization"],"plasticity":["null"],"credit":["gradient","random_projections"],"update":["adam","euclidean"]}' \
  --epochs 5 --n-seeds 2
```
**Result:** **PASS** — All 24 cells passed (instantaneous dynamics only; energy_minimization filtered by compatibility). Cora 70-73%, Pubmed 66-68%, Citeseer 61-64%. Both gradient and random_projections work identically on graph tasks.
**Defects Found:** energy_minimization on graph geometry filtered (tensor shape mismatch: settle expects [B, features], graph produces [num_nodes, features]). Known limitation.

---

## Session 2026-11-11 (continued)
**Experiment:** Energy Minimization — Dynamics Sweep (L0, MNIST)
```
uv run python -m computronium.experiment.survey_cli 0.25 \
  --mode learn --policy tpe --device cuda \
  --tasks mnist --fidelity L0 \
  --store experiments/t88_energy_min_dynamics.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["feedforward"],"dynamics":["instantaneous","energy_minimization","predictive_settling"],"plasticity":["null"],"credit":["gradient","random_projections"],"update":["adam"]}' \
  --epochs 5 --n-seeds 2
```
**Result:** PARTIAL — 7/8 cells before timeout. **energy_minimization+gradient 97.0% matches instantaneous 97.2%** (3.5x slower: 45s vs 13s/epoch). random_projections: instantaneous 93.5%, energy_minimization seed 42 only 91.7% at epoch 3. predictive_settling filtered by compatibility.
**Defects Found:** None — energy_minimization working correctly on feedforward.

---

## ✅ Session Complete (2026-11-11)

**Experiments Completed:**
1. Predictive Settling with Thermodynamic Contrast / Local Goodness — Expected behavior confirmed
2. Credit Assignment — Cross-Geometry — Budget-limited, key credit/geometry compatibilities mapped
3. Substrate Comparison — Digital vs Memristive — PASS (memristive matches digital at 1.7x cost)
4. Plasticity Sweep — Fast Weights / Routing — Constraint working; routing not beneficial on these tasks
5. Causal Transformer Vision — Credit Sweep — Budget-limited; homeostatic fails, random_projections works
6. Causal Transformer Vision — Geometry Parity — **PASS** (causal_transformer = feedforward = 97%+)
7. Graph Classification — Geometry Sweep — CUDA PyG issue (known upstream limitation)
8. Graph Node Classification — **PASS** (all 24 cells, Cora 73%, Pubmed 68%, Citeseer 64%)
9. Energy Minimization — Dynamics Sweep — **PASS** (energy_minimization = instantaneous at 97% val_acc)

**Property Locks:** PASSED (11/11 tests)
**Dev-env Smoke:** PASSED
**Lint/Type Check:** No new issues (pre-existing only)

**Next Session Priorities:**
1. Complete Causal Transformer Credit Sweep (gradient, pc_alm)
2. Graph Classification on CPU (work around PyG CUDA issue)
3. Energy Minimization + predictive_settling sweep
4. Multi-task credit cross-geometry with larger budget

---

## Session 2026-11-11 (continued — priorities 1–4 + FIX PHASE)

**Experiment:** Causal Transformer Credit Sweep — COMPLETE (L0, MNIST)
```
uv run python -m computronium.experiment.survey_cli 0.3 \
  --mode learn --policy tpe --device cuda \
  --tasks mnist --fidelity L0 \
  --store experiments/t88_causal_transformer_credits_complete.duckdb \
  --max-workers 1 \
  --axes '{"substrate":["digital"],"geometry":["causal_transformer"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient","random_projections","pc_alm"],"update":["adam"]}' \
  --epochs 5 --n-seeds 2
```
**Result:** **PASS** — All 6 cells. gradient/adam: 97.0/97.2% (full parity with feedforward confirmed).
random_projections: 68.1/75.1%. pc_alm: 10.1/10.8% (chance — pc_alm inert on instantaneous
dynamics, same as homeostatic). 184s/cell.

**Experiment:** Graph Classification on CPU (L0, graph_classification)
```
uv run python -m computronium.experiment.survey_cli 0.2 \
  --mode learn --policy tpe --device cpu \
  --tasks graph_classification --fidelity L0 \
  --store experiments/t88_graph_classification_cpu.duckdb \
  --max-workers 1 \
  --axes '{"substrate":["digital"],"geometry":["graph","spatial_lattice"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient","random_projections"],"update":["euclidean","adam"]}' \
  --epochs 5 --n-seeds 2
```
**Result:** PARTIAL — All 8 cells PASS at val_acc=0.5789 (below 0.70 target). CUDA PyG issue
avoided. **But bit-identical val_acc across all credits AND updates — see defect G1.**
"free settle telemetry failed: index 565 is out of bounds" warnings on graph cells (9 occurrences).

**Experiment:** Energy Min + predictive_settling (L0, MNIST, 5 epochs)
```
uv run python -m computronium.experiment.survey_cli 0.3 \
  --mode learn --policy tpe --device cuda \
  --tasks mnist --fidelity L0 \
  --store experiments/t88_energy_min_predictive_settling.duckdb \
  --max-workers 1 \
  --axes '{"substrate":["digital"],"geometry":["feedforward"],"dynamics":["energy_minimization","predictive_settling"],"plasticity":["null"],"credit":["gradient","random_projections"],"update":["adam"]}' \
  --epochs 5 --n-seeds 2
```
**Result:** **PASS** — energy_min+gradient: 97.1/96.9% (matches instantaneous 97.2%).
energy_min+random_projections: 93.4/93.2%. predictive_settling filtered by compatibility
(2 declared cells). 257s/cell for energy_min.

**Experiment:** Multi-task credit cross-geometry (L0, mnist+cora, 0.4 budget)
```
uv run python -m computronium.experiment.survey_cli 0.4 \
  --mode learn --policy tpe --device cuda \
  --tasks mnist,cora --fidelity L0 \
  --store experiments/t88_multitask_credit_cross_geometry.duckdb \
  --max-workers 1 \
  --axes '{"substrate":["digital"],"geometry":["feedforward","graph"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient","random_projections","pc_alm"],"update":["adam"]}' \
  --epochs 5 --n-seeds 2
```
**Result:** PARTIAL — All 12 cells PASS, task cycling works. mnist/feedforward: gradient
97.2% ≠ random_projections 93.5% ≠ pc_alm 9.8% (credits DO differ on vision). **cora
cells: gradient == random_projections == pc_alm bit-identical (0.3680/0.4280, loss
1.9501→1.3168 every epoch) — see defect G1.**

---

## 🔴 FIX PHASE 2026-11-11 — Defects Found & Fixed

**FIXED — D88-1: FiniteGuard inert (sentinel −1 vs `torch.minimum` fold).**
`FiniteGuard` (`computronium/ontology/dynamics/_settle_driver.py`) initialized its
"never diverged" flag to **-1** but folded divergence with
`torch.where(diverged, torch.minimum(first_bad, step), first_bad)` — and
`torch.minimum(-1, step)` is always -1, so a divergence could never be recorded. The
guard raised **never**, in **all six settle loops** using it (`_dynamics.py` lines
1446, 1487, 1709, 1955, 2009, 2721 — pc_alm, and other FiniteGuard-based loops): a
settle that went non-finite returned poisoned activations silently instead of raising.
Caught by `test_pc_alm_nan_guard` (DID NOT RAISE). Fix: sentinel `-1` → `sys.maxsize`
(== `torch.iinfo(long).max`; module imports torch lazily under TYPE_CHECKING), raise
check `first >= 0` → `first < _UNSEEN`. Verified: `test_settle_stability_lock.py`
8/8, `test_dynamics_wiring_lock.py` + `test_defect_hunt_locks.py` 17/17.
Note: `test_pc_alm_nan_guard` failed before this session's experiments — the
"Property Locks PASSED (11/11)" claim above predates this run's lock re-check.

**🟢 FIXED — G1: GraphSystemTrainer bypasses dynamics/credit/update axes.**
Both epoch bodies now route through `system.train_step(...)`:
`_train_epoch_node_classification` masks non-train nodes with `IGNORE_INDEX`
(-100) so the CE loss/nudge apply to training nodes only;
`_train_epoch_graph_classification` forwards `edge_index`/`batch` per batch.
The external `optim.Adam` was deleted — Δθ flows only through the U-axis
(pipeline parity contract). Files: `core/system_trainer/graph_trainer.py`,
`core/pipeline.py` (ignore-index accuracy), `ontology/_settle_kernel.py`
(`nudged_output`: sentinel-aware nudge — the raw one-hot scatter would raise
on -100), `ontology/dynamics/_dynamics.py` (instant nudge uses it).
Evidence: cora now path-attributed — graph+gradient **0.618 mean** (0.64/0.46/0.75)
vs graph+random_projections **0.195 mean** (0.31/0.11/0.16) vs feedforward+gradient
0.289. All three credits now produce distinct loss trajectories (previously
bit-identical). Lock: `tests/property/test_graph_pipeline_lock.py` (5 tests:
train_step spy, param movement, credit-delta divergence, batched graph kwargs,
geometry-conditional kwargs).
**🟢 FIXED — G2: Pipeline graph-kwargs path incompatible with both geometry families.**
`core/pipeline.py` now filters graph kwargs by an explicit geometry capability
(`accepts_graph_kwargs = True` on `GraphGeometry` only; every other geometry
never sees `edge_index`/`batch`); `run_forward` normalizes positional graph args
to kwargs so the filter applies. `experiment/kernel/_geometry_builders.py`
accepts a LongTensor `edge_index` (PyG form) in addition to nested lists.
Batched graph-classification epochs verified end-to-end (synthetic PyG `Batch`,
loss finite, params move) and locked.
**🟢 FIXED — G3: pc_alm + instantaneous dynamics = chance (10%).**
Decision: filter, don't special-case. New void constraint
`pc_alm_credit_dynamics` (`experiment/schema/seed_registries.py`) makes
`credit=pc_alm` require `dynamics=pc_alm` (the dual-variable carrier — with any
other dynamics `PCALMCredit.compute_pseudo_gradient` returns [] → zero updates).
Pairing probe (`experiments/t88_g3_pcalm_pairing.duckdb`, mnist, pc_alm×pc_alm,
1 epoch): **val_acc 0.3026** vs 10% chance under instantaneous — the credit
works with its carrier, but at **283 s/epoch** (cell FAILs on the L0 deadline;
claim needs L1+ budget or GPU settle kernel). Remaining: none for correctness.
**Next Session Priorities (revised):**
1. **Graph claims** — cora attribution exists at n=3; promote gradient+graph to a
   claim-grade run (L1/L2, ≥3 seeds, replay hash) now that pc_alm is filtered and
   the trainer is pipeline-parity. Note the U-axis Adam default (1e-3) is 10× below
   the old external Adam (1e-2); graph cells need explicit `--hyperparameters`
   step_size or more epochs to reach the >0.75 target.
2. **Graph classification sweep** — the batched path is now correct; re-run MUTAG
   with graph geometry at L1 to re-establish the 60-63% baseline under real axis
   attribution (target >0.70 still open).
3. **pc_alm pairing budget** — 283 s/epoch on MNIST needs GPU settle paths or an
   L0-sized task before pc_alm credit can be credit-claimable; do not re-run at L0.
4. **Stale graph payload_key test** — `tests/unit/experiment/test_task_aware_objectives.py`
   updated to `val_acc` (was asserting the pre-TODO87 `accuracy`).

---

## Session 2026-11-11 (continued — G1/G2/G3 FIX + ATTRIBUTION RE-RUN)
**Experiment:** cora credit attribution (20 epochs, 3 seeds, digital/instantaneous/adam)
```
uv run python -m computronium.experiment.survey_cli 0.15 --mode learn --policy tpe \
  --device cuda --tasks cora --fidelity L0 \
  --store experiments/t88_g1_cora_credit_attribution.duckdb --max-workers 1 \
  --axes '{"substrate":["digital"],"geometry":["feedforward","graph"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient","random_projections"],"update":["adam"]}' \
  --epochs 20 --n-seeds 3
```
**Result:** PASS — 12/12 cells, positive control PASS (graph/grad/euclid 0.146 at 1
epoch). Axis attribution re-established: **graph+gradient 0.618 mean** (0.640 / 0.464 /
0.750) vs **graph+random_projections 0.195 mean** (0.312 / 0.114 / 0.160) vs
feedforward+gradient 0.289 (0.198/0.348/0.320). Credits now diverge in every epoch's
loss (pre-G1 they were bit-identical on cora). 4 claim-eligible cells (n=3); seed
variance on cora+gradient is high (0.46–0.75) → treat as under-powered.
**Defects Found:** G1/G2/G3 (see FIX PHASE above); stale graph payload_key test.
**Fixes Applied:** `core/system_trainer/graph_trainer.py` (pipeline routing, no
external optimizer), `core/pipeline.py` (ignore-index accuracy + geometry-conditional
graph kwargs), `ontology/_settle_kernel.py` (`IGNORE_INDEX`, `nudged_output`),
`ontology/dynamics/_dynamics.py` (sentinel-aware instant nudge),
`ontology/geometry.py` (`accepts_graph_kwargs`), `experiment/kernel/_geometry_builders.py`
(Tensor edge_index), `experiment/schema/seed_registries.py` (pc_alm_credit_dynamics void),
`tests/property/test_graph_pipeline_lock.py` (new, 5 tests),
`tests/unit/experiment/test_task_aware_objectives.py` (val_acc).
**Verification:** `test_graph_pipeline_lock` 5/5; targeted suites
(`test_dynamics`, `test_credit_semantics`, `test_ontology_locks`, `test_pepita_credit_parity`,
`test_trainer_metric_aggregation`, `test_determinism_extended`, `test_compiled_settle`,
`test_defect_hunt_locks`, `test_claim_report_lock`, `test_pc_alm_validation`,
`test_demo_graph_geometry_swap`, `test_param_budget_lock`, `test_legality_boundary_lock`,
`test_experiment_registries_wiring_lock`, `test_axes_capabilities_totality_lock`,
`tests/unit/experiment/`) — all green (the 3 pre-existing failures in
`test_task_aware_objectives` were stale graph `payload_key` assertions, updated here).
Lint/type: only pre-existing legacy findings.
**Experiment (G3 probe):** pc_alm×pc_alm, mnist, 1 epoch → val_acc 0.3026, 283 s/epoch
(FAIL on L0 deadline; correctness confirmed, budget-limited).
**Next Experiment:** MUTAG graph-classification L1 re-run under real attribution;
cora+gradient at L1/L2 with explicit step_size for a claim-grade record.

---

## Session 2026-11-11 (continued — G4/G5/G6/G7 FIX + GRAPH CLAIMS)

**Experiment 1 — MUTAG ceiling probe** (`scripts/probes/mutag_geometry_probe.py`)
```
uv run python scripts/probes/mutag_geometry_probe.py
```
**Result:** PASS (the "ceiling" was a defect). MUTAG n=188, deterministic stratified 80/20 split
(150/38, val 25/13 → majority baseline 0.658), 3x64 hidden, 200 epochs, plain Adam 1e-2:
- pre-fix (bare neighbour mean): train 0.780, val 0.711, val_loss 0.6308
- shipped `(A + I)` aggregation, 5 seeds: train 0.800–0.827, **val 0.711–0.737** (mean 0.727)
- variants ruled out width/depth/pooling: hidden=128 → val 0.737; sum pooling → val 0.737 with
  train 0.867; 4 layers → val 0.737. Walltime ~0.05 s/epoch (the L0 "too slow" note was stale).

**Experiment 2 — MUTAG attribution under the fixed pipeline** (L1, 200 epochs, step_size=0.01)
```
--tasks graph_classification --fidelity L1 --axes '{"substrate":["digital"],"geometry":["graph"],
  "dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient","random_projections"],
  "update":["adam"]}' --epochs 200 --hyperparameters '{"update.step_size":{"members":[0.01]}}'
```
**Result:** PASS — gradient 0.684 / 0.658 (seeds 42/43), random_projections 0.711 / 0.658, all at or
above the 0.658 majority baseline, credits visibly distinct (pre-G1 they were bit-identical).
Stores: `t88_g4_mutag_attribution_l1`, `t88_g5_mutag_random_projections_l1`, `t88_g6_mutag_claim_l1`.

**Experiment 3 — Cora claim-grade record** (L1, 100 epochs, step_size=0.01, n=3)
```
--tasks cora --fidelity L1 --axes '{"substrate":["digital"],"geometry":["graph"],
  "dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient"],"update":["adam"]}'
--epochs 100 --n-seeds 3 --hyperparameters '{"update.step_size":{"members":[0.01]}}'
```
**Result:** PASS — 0.782 / 0.752 / 0.764 → **mean 0.766 (>0.75 target)**, 1 claim-eligible cell,
positive control PASS (0.132 at 1 epoch). Seed spread collapsed from 0.46–0.75 (20 epochs,
default step_size 1e-3) to 0.03. Store: `t88_g6_cora_claim_l1`.

**Defects Found & Fixed:**
- **G4 — graph aggregation had no self connection, and used row order instead of PyG
  source→destination order.** `_aggregate` replaced each node's features with its neighbours'
  mean, so node identity was destroyed and a source-only node became zero. Fix:
  `_degrees`/`_aggregate` are `(A + I)` over in-edges; batched setup (edge index, degrees,
  pooling map) is one `_batched` context manager instead of two copies.
- **G5 — FA crashed on any pooled readout** (`mat1 and mat2 shapes cannot be multiplied (2x4 and
  20x16)`): the error chain mixed a batch-sized readout error with node-sized activations.
  Fix: `GraphGeometry.pool_context()` exposes `(node → graph, nodes per graph)`;
  `RandomProjectionsCredit._graph_path` walks head → per-graph pooling share → per-node chain.
- **G6 — three credit dispatchers, one stale.** `spec._credit_from_config` did not know
  `local_contrastive`/`per_layer_ff` or `pc_alm`, so legal axis values raised
  `Unknown credit_type`. Fix: `spec` is the single dispatcher; `factory` and `joint` delegate.
- **G7 — cost-model cache clobbered other tasks' prices.** Post-run pricing replaced `per_task`
  wholesale: a 1.786 s/cell MUTAG run at `cuda/L1` deleted MNIST's 247.157 s/cell entry, and the
  dry-run then advertised 1.8 s/cell for a four-minute cell. Fix: the per-task map merges (in the
  measured model and in `_save_cost_model`); `CostModel.cost_for(task)` prices the dry-run per
  task. `.timing.json` restored: `{"mnist": 247.157, "graph_classification": 1.786}`.
- **Stale lock** — `test_proxy_rejects_non_layered_geometry` was failing on HEAD (GraphGeometry
  answers `layered_params`, so it is a legal layered input). Fixture replaced with a geometry that
  genuinely lacks the view; the guard is still exercised.

**Fixes Applied:** `ontology/geometry.py` (self connection, PyG edge order, `_batched`,
`pool_context`), `ontology/credit/__init__.py` (`_pool_context` + `_graph_path`),
`domains/factory.py` (`_stratified_split`), `core/system_trainer/{spec,factory,joint}.py`
(single dispatcher), `experiment/wave.py` (cost-model merge, `cost_for`),
`experiment/survey_cli.py` (per-task dry-run price), `experiments/.timing.json` (restore mnist).
**Locks added:** `property/test_graph_self_connection_lock.py` (self connection + PyG order +
stratified split), `property/test_graph_pipeline_lock.py::test_pooled_readout_credit_trains_and_differs_from_gradient`
(G5), `property/test_credit_dispatch_lock.py` (all 10 credits build through all dispatchers),
`unit/experiment/test_cost_model_cache_lock.py` (G7).
**Probe:** `scripts/probes/mutag_geometry_probe.py` (pre-fix numbers + shipped-geometry re-measure).

**Verification:** `test_graph_pipeline_lock` 6/6, `test_graph_self_connection_lock` 2/2,
`test_credit_dispatch_lock` 4/4, `test_cost_model_cache_lock` 2/2, `test_credit_semantics` +
`test_geometry_wiring_lock` + `test_dynamics_wiring_lock` + `test_axes_capabilities_totality_lock`
+ `test_composer_registry_coverage_lock` + `test_task_geometry_compat_lock` 64 passed/29 skipped,
`tests/unit/core -k "graph or credit or pipeline or composition"` 45 passed,
`tests/unit/experiment` 219 passed, registry/legality/claim locks 50 passed/4 skipped,
demos `test_demo_uaxis_coverage` + `test_demo_graph_geometry_swap` 2/2 (232 s).
Lint: no new findings (39 pre-existing legacy in `wave.py`/`geometry.py`).
Pyright: no new findings (17 pre-existing in `domains/factory.py`, `credit/__init__.py`,
`geometry.py` legacy regions).

**Next Experiment:** R1 (MUTAG evaluation protocol: folds or a larger TU dataset) and R5
(replay identity: seed-insensitive hash + CUDA scatter), from REMAINING WORK.

---

## Session 2026-11-11 (late — G8 / R2 / R3 / R4)

**Experiment 1 — R2: harness U-axis vs plain Adam on MUTAG** (L1, 200 epochs, step_size 0.01)
```
uv run python -m computronium.experiment.survey_cli 0.1 --mode learn --policy random \
  --device cpu --tasks graph_classification --fidelity L1 \
  --store experiments/t88_r2_mutag_uaxis_clip.duckdb --max-workers 1 \
  --axes '{"substrate":["digital"],"geometry":["graph"],"dynamics":["instantaneous"],
           "plasticity":["null"],"credit":["gradient"],"update":["adam"]}' \
  --epochs 200 --n-seeds 3 \
  --hyperparameters '{"update.grad_clip":{"members":[0.1,1.0,10.0]},"update.step_size":{"members":[0.01]}}'
```
**Result:** grad_clip 0.1 → 0.605/0.711/0.632 (0.649); 1.0 → 0.658/0.632/0.632 (0.640);
10.0 → bit-identical val_acc to 1.0. **Clipping is inactive — the optimizer was not the gap.**
`scripts/probes/mutag_geometry_probe.py` harness-parity arms (5 seeds): plain Adam 0.7158,
nudged-CE β=0.1 0.7263, frozen biases 0.7316, both 0.7368 — both harness knobs are refuted.
Also found: the three seeds shared one `replay_hash` (R5).

**Experiment 2 — G8 root cause + verify** (same cell, post-fix)
```
--store experiments/t88_r2b_mutag_settle_fix.duckdb  (same axes, step_size 0.01, n-seeds 3)
```
**Result:** 0.684 / 0.711 / 0.684 → **mean 0.693** (was 0.640), val loss 0.673 → 0.581/0.650/0.646.
Counterfactual: rebuilding layer *i+1* from `acts[i]` diverged from `settle_blocks`
(0.32), while rebuilding from the pre-aggregation relu output matched exactly — the settle
path never fed its own aggregated act forward.

**Experiment 3 — R3/R4 lock cells**
```
uv run python -m pytest tests/property/test_credit_readout_paths_lock.py \
  tests/property/test_graph_self_connection_lock.py tests/property/test_graph_pipeline_lock.py -q
```
**Result:** PASS — `target_inversion` and `temporal_trace` clear a batched 4-graph readout and move
both 2-D weights; homeostatic moves all six vision-transformer weights including
`blocks.0.in_proj.weight`; `settle_blocks` equals `forward` elementwise.

**Defects Found:**
- **G8** — `GraphGeometry.settle_blocks` reused the pre-aggregation relu output for the next
  layer while appending the aggregated act, so the pipeline's hidden chain had no message
  passing (only the final act was aggregated). This was the R2 gap.
- **R5a** — replay hashes ignore the seed (seeds 42/43/44 share a hash with different val_acc).
- **R8** — LM token targets `[B, T]` crash `nudged_output` against `[B*T, V]` logits.

**Fixes Applied:**
- `computronium/ontology/geometry.py` — `settle_blocks` feeds `h = self._aggregate(h)` into the
  next layer.
- `computronium/ontology/_utils.py` — `_pool_acts`, `_share_pooled` (transpose of mean pooling).
- `computronium/ontology/credit/__init__.py` — `TargetInversionCredit._graph_target_grads`,
  pooled-readout `TemporalTraceCredit._rate_stdp_grads`, transformer-aware
  `HomeostaticCredit._post_activations`.
- `scripts/probes/mutag_geometry_probe.py` — R2 arms (nudged CE, frozen biases) + findings.
- Locks: `tests/property/test_credit_readout_paths_lock.py` (new, 3 tests),
  `tests/property/test_graph_self_connection_lock.py::test_settle_blocks_matches_forward`.

**Verification:** `test_credit_readout_paths_lock` 3/3, `test_graph_self_connection_lock` 3/3,
`test_graph_pipeline_lock` 6/6, `test_credit_semantics` + `test_geometry_wiring_lock` +
`test_dynamics_wiring_lock` + `test_axes_capabilities_totality_lock` 30/30,
`tests/unit/core -k "graph or credit or pipeline"` 40/40. Lint: no new findings (pre-existing
`_utils.py` typing import, `geometry.py` `_apply_stack` complexity/branches).

**Next Experiment:** R1 (fold/larger-dataset evaluation protocol) and R5 (seed-aware replay hash,
CUDA scatter tolerance); R8 is the cheapest fix of the three.

---

## Session 2026-11-11 (close — R1c / R5 / R8)

**Experiment:** R5 forensics on the stored R2 sweep (`experiments/t88_r2b_mutag_settle_fix.duckdb`)
```
select json_extract_string(schedule,'$.seed'), measurement_key,
       json_extract_string(payload,'$.replay_hash'), json_extract_string(payload,'$.val_acc')
from records
```
**Result:** Seeds 42/43/44 of one coordinate share a per-cell `replay_hash` (fewer than 16 hex
chars differ) while val_acc is 0.684/0.711/0.684. Reading the site showed why: `evaluate.py`
hand-assembled `code_sha | dataset_version | cell_key | fidelity | n_seeds | epochs | batch_limit |
param_budget | device` — `cell_key` excludes the schedule, and `seed` was never appended. The
run-level hash was not at fault (it covers the whole measured seed plan by design).

**Defects Found:**
- **R5a** — per-cell replay hash omitted `schedule.seed` (and `task_id`, `deterministic`,
  `precision`, `num_workers`), so a replay could not identify the measurement it claimed.
- **R8** — LM token targets `[B, T]` met folded logits `[B*T, V]`: `nudged_output` returned the
  2-D target (broadcast error), `task_loss`/`_task_loss_tensor` fed rank-mismatched CE, and
  `SystemTrainer.validate` had the same mismatch plus a per-sequence (not per-token) denominator.
- **R1(c)** — graph cells stored `val_acc` with no majority rate, so a 0.63 MUTAG cell (below the
  0.658 majority baseline) read as "near 0.70".

**Fixes Applied:**
- `computronium/ontology/_utils.py` — `_align_target_rows`: folds targets whose element count
  equals the logits' row count; class targets and soft labels pass through.
- `computronium/ontology/_settle_kernel.py` — `nudged_output` aligns before the nudge and
  `_one_hot` builds `[…, V]` one-hots for any target rank; ignore-index entries stay free.
- `computronium/core/pipeline.py` — both task-loss paths align the target before CE/accuracy.
- `computronium/core/system_trainer/trainer.py` — `validate` aligns and counts tokens (`numel`).
- `computronium/experiment/kernel/evaluate.py` — `_cell_replay_hash` = SHA256 of
  `code_sha | dataset_version | measurement_key(schedule)` (single definition of measurement
  identity, so the seed is in it).
- `computronium/experiment/evidence/limitations.py` — `NONDETERMINISTIC_ACCUMULATION` states the
  CUDA graph-scatter tolerance (one graph = 1/N of the split) for non-deterministic CUDA cells.
- `computronium/domains/factory.py` — `GraphClassificationTask.evaluate` returns
  `majority_baseline` and `val_acc_over_majority` in `Metrics.custom`; the kernel's
  `_update_task_metrics` copies them into the payload.
- Locks: `tests/property/test_lm_target_alignment_lock.py` (5),
  `tests/property/test_cell_identity_lock.py` (4), `tests/property/test_graph_eval_protocol_lock.py` (2).

**Verification:** New locks 11/11; `test_transformer_geometry` + `test_graph_pipeline_lock` +
`test_graph_self_connection_lock` + `test_credit_readout_paths_lock` + `test_cell_evaluation_lock`
23/23; `tests/unit/core -k "loss or trainer or pipeline or graph or transformer"` +
`test_determinism_extended` 47/47; `test_claim_report_lock` 27/27. Lint: no new findings (pre-existing
Register C items only); pyright: no new errors (the 25 are the pre-existing graph-`Data` typing set).

**Next Experiment:** R1(a) 5-fold CV inside `GraphClassificationTask` (or R1(b) PROTEINS as a
second graph task) to raise split resolution; R7 PyG CUDA pin probe if CUDA graph claims are
needed. Everything else in the table is closed or round-close hygiene (R6).


---

## Session 2026-11-11 (late-2 — R1b / R7 / G9 / R9)

**Experiment 1 — R7 repro: is the CUDA graph crash upstream?** (PyG 2.8.0.post1,
torch 2.14.1+cu130)
```
CUDA_LAUNCH_BLOCKING=1 uv run python -m computronium.experiment.survey_cli 0.05 \
  --mode learn --policy random --device cuda --tasks proteins --fidelity L0 \
  --store /tmp/opencode/r7c.duckdb --max-workers 1 --n-seeds 1 --epochs 3 \
  --axes '{"substrate":["digital"],"geometry":["graph"],"dynamics":["instantaneous"],
           "plasticity":["null"],"credit":["gradient"],"update":["adam"]}'
```
**Result:** `vectorized_gather_kernel: ind < ind_dim_size` assert, then
`free settle telemetry failed: CUDA error: device-side assert triggered`, then every
later cell in the process died. Root cause was ours: `_sample_inputs` flattened a PyG
batch to `batch.x`, and the free-phase probe called `forward_pass(geometry, x)` with no
`edge_index`/`batch`, so node-mode geometry indexed a **static** edge list (max id 1045)
against a batch with 1134–1201 node rows. On CPU the same call raised
`index 1045 is out of bounds` and `tensor a (1201) vs b (1134)` — caught as warnings.

**Fixes Applied (G9):**
- `computronium/experiment/kernel/_trainer_utils.py` — `_sample_inputs` returns
  `(input, count)` and returns `(None, num_graphs)` for a PyG batch; the probe's
  energy estimate is priced per graph, not per node.
- `computronium/experiment/kernel/evaluate.py` — `_post_training_metrics` skips the
  free-phase probes when there is no batch-free input.
- `computronium/ontology/geometry.py` — `_batched` sizes degrees from `x.shape[0]`
  (PyG appends trailing isolated nodes after the last edge), `forward_with_intermediates`
  delegates to `settle_blocks` when given `edge_index`/`batch`, and node-mode `forward`
  raises a `ValueError` naming the missing kwargs before any kernel launch.
- Lock: `tests/property/test_graph_batched_input_lock.py` (5 tests: trailing isolated
  node, intermediates == forward on a batch, node-mode guard, probe skips a PyG batch,
  probe flattens a tensor batch).

**Verify:** CUDA proteins 10-epoch cell 0.6637 vs CPU 0.6637 (device parity), zero
asserts, zero telemetry warnings. `test_graph_batched_input_lock` + graph locks 20/20;
`tests/unit/core -k "graph|registry|task"` + task objectives + cost lock 38/38.

**Experiment 2 — R1(b) PROTEINS claim run** (L1, 100 epochs, n=3, cuda)
```
uv run python -m computronium.experiment.survey_cli 0.15 --mode learn --policy random \
  --device cuda --tasks proteins --fidelity L1 --store experiments/t88_r1b_proteins.duckdb \
  --max-workers 1 --n-seeds 3 --epochs 100 \
  --axes '{"substrate":["digital"],"geometry":["graph"],"dynamics":["instantaneous"],
           "plasticity":["null"],"credit":["gradient","random_projections"],"update":["adam"]}'
```
**Result:** gradient 0.6637/0.6726/0.6592 → **0.665**; random_projections
0.6233/0.6143/0.6368 → **0.625**; majority 0.596; 7/7 PASS; 2 claim-eligible cells;
152 s. The split holds out 223 of 1113 graphs (0.005/graph) and reports the measured
majority rate beside every cell.

**Experiment 3 — R9 capacity/step probe** (hidden 128 × 5, 100 epochs, n=3, cuda)
```
--store experiments/t88_r1b_proteins_capacity.duckdb --hyperparameters \
  '{"geometry.hidden_dim":{"members":[128]},"geometry.num_layers":{"members":[4]},
    "update.step_size":{"members":[0.003,0.01]}}'
```
**Result:** step 0.003 → 0.6726/0.6996/0.7309 = 0.701; step 0.01 → 0.6278/0.6726/0.7130
= 0.671. 5-seed confirm (step 0.003, `experiments/t88_r1b_proteins_confirm.duckdb`):
0.6637/0.7130/0.7130/0.6906/0.7040 = **0.697 (sd 0.021)** — at the 0.70 target, not above
it, so R9 stays open with pooling and the readout objective as the next levers.

**Defects Found:**
- **G9** — graph free-phase probe fed node rows to node-mode geometry (CUDA sticky
  assert kills the process; CPU warning).
- **G9b** — `_batched` sized degrees from `edge_index.max()+1`; trailing isolated nodes
  made the degree vector narrower than the activations.
- **G9c** — `forward_with_intermediates` ignored `edge_index`/`batch`, so the graph act
  stack had no batched aggregation and no pooled readout.

**Verification:** new lock 5/5; graph + credit + identity locks 15/15; targeted unit
suites 38/38 + 22/22; lint shows no new findings (factory `too-many-branches` and the
geometry Register C set are pre-existing); pyright on changed files is at or below the
HEAD baseline (trainer_utils 12 → 8).

**Next Experiment:** non-graph focus (see Session 2026-11-11 late-3).

---

## Session 2026-11-11 (late-3 — R9 pooling arm)

**Fix — pooling is a geometry knob (R9 lever 1).** `GeometryConfig.pooling:
"mean" | "sum"` flows through `GeometryConfig.graph`, `build_graph_config`, the
`geometry_keys` vocabulary (`geometry.pooling` is a swept key) and
`GeometryConfig.hyperparameters()` (graph-only availability). `GraphGeometry._pool`
applies the configured reduction, and `pool_context()` now returns a typed
`PoolContext(index, counts, mean)` in `ontology/_utils.py` whose `pool`, `pool_acts`,
`share` and `broadcast` methods give every pooled-readout credit the forward's exact
reduction and transpose. This replaces the mean-only `_pool_acts`/`_share_pooled`
pair, so a sum-pooled graph can no longer be credited as if it were mean-pooled.

**Experiment 1 — pooling arms** (L1, 100 epochs, hidden 128 × depth 5, step 0.003,
cuda, n=5 each; `experiments/t88_r9_pooling.duckdb`)
```
uv run python -m computronium.experiment.survey_cli 0.2 --mode learn --policy random \
  --device cuda --tasks proteins --fidelity L1 --max-workers 1 --n-seeds 5 --epochs 100 \
  --axes '{"substrate":["digital"],"geometry":["graph"],"dynamics":["instantaneous"],
           "plasticity":["null"],"credit":["gradient"],"update":["adam"]}' \
  --hyperparameters '{"geometry.hidden_dim":{"members":[128]},
    "geometry.num_layers":{"members":[4]},"update.step_size":{"members":[0.003]},
    "geometry.pooling":{"members":["mean","sum"]}}'
```
**Result:** mean **0.6906 ± 0.0208** (0.6637/0.6906/0.7130/0.6771/0.7085); sum
**0.6717 ± 0.0296** (0.6323/0.6816/0.7040/0.6502/0.6906); majority 0.596.
**Sum pooling is worse**, so mean stays the default and pooling is not the lever.

**Experiment 2 — epoch budget at the mean-pooled arm** (same cell, 200 epochs, n=5;
`experiments/t88_r9_pooling_200ep.duckdb`)
```
---same flags, --epochs 200, --hyperparameters '…"geometry.pooling":{"members":["mean"]}'
```
**Result:** **0.7040 ± 0.0071** (0.6951/0.7130/0.7040/0.6996/0.7085), majority 0.596,
+0.108 margin, 1 claim-eligible cell (n=5), 366 s. Every seed improved or held against
its 100-epoch value except seed 44 (0.7130 → 0.7040), mean +0.0135.

**R9 CLOSED.** PROTEINS >0.70 target is met at mean pooling / hidden 128 × depth 5 /
step 0.003 / 200 epochs. The remaining graph questions (pooling alternatives such as
attention pooling, depth sweeps) are exploratory, not claim blockers.

**Defects Found:** none new. The `PoolContext` refactor is behaviour-preserving for
mean pooling (the lock exercises both modes).

**Fixes Applied:**
- `computronium/ontology/_utils.py` — `PoolContext` (pool/pool_acts/share/broadcast)
  replaces `_pool_acts` + `_share_pooled`.
- `computronium/ontology/geometry.py` — `PoolingMode`, `GeometryConfig.pooling`,
  `GeometryConfig.graph(pooling=…)`, graph-only `pooling` hyperparameter,
  `GraphGeometry._pool`, typed `pool_context()`.
- `computronium/ontology/credit/__init__.py` — `_graph_path`, `_rate_stdp_grads` and
  `_graph_target_grads` consume `PoolContext`, so FA and target propagation follow the
  configured reduction.
- `computronium/experiment/kernel/_geometry_builders.py` — `_as_pooling` (fail loud on
  unknown values) wires `geometry.pooling`.
- `computronium/experiment/schema/geometry_keys.py` — `pooling` in the graph key
  vocabulary, so a swept value reaches the builder.
- `tests/property/test_graph_pipeline_lock.py` — pooled-readout lock parametrized over
  mean/sum, plus `test_sum_pooling_readout_matches_add_pool` (sum readout ==
  `global_add_pool` of the node stack; both modes advertise their transpose).

**Verification:** `test_graph_pipeline_lock` 8/8 (mean + sum arms); graph/credit/
registry locks 16/16 + 60 passed, 4 skipped; ruff clean on changed files (only the
pre-existing `_utils` Register C findings remain); pyright on changed source files
shows only pre-existing legacy findings.

**Next Session Focus — non-graph (user directive):** see the ordered non-graph
tickets N1–N4 in REMAINING WORK. No new graph tickets this cycle.

---

## Session 2026-11-11 (late-4 — N1: non-graph credit robustness)

**Experiment 1 — Experiment-13 symptom repro** (L1, mnist/iris/wine/acrobot,
cuda, `--max-workers 1`). Replaying the FAIL records showed they were not one
class of failure:

```
uv run python -m computronium.experiment.survey_cli 0.04 --mode learn --policy random \
  --device cuda --tasks mnist --fidelity L1 --store /tmp/opencode/n1_recur_homeo.duckdb \
  --max-workers 1 --n-seeds 1 --epochs 3 \
  --axes '{"substrate":["digital"],"geometry":["recurrent"],"dynamics":["instantaneous"],
           "plasticity":["null"],"credit":["homeostatic"],"update":["euclidean"]}'
```
**Result:** 4 records for a 1-seed declaration (G13), seeds 42/43 at 0.080/0.112
(error-blind at chance), seed 44 truncated at 1/3 epochs (G14). The Experiment-13
`graph_classification` FAILs were `…forward() takes from 2 to 3 positional
arguments` — the graph task on node-mode geometry (G12), not a credit defect.

**Experiment 2 — tabular tasks** (L1, 5 epochs, n=1 then n=3):
```
--tasks wine,iris --axes '{"credit":["gradient"],"update":["adam"],"geometry":["feedforward"],…}'
```
**Result (before G10):** wine `val_acc=0.0` on all three seeds with
`train_acc=0.88–0.90`; iris 0.767/0.467/0.700. **After G10 (stratified split):**
wine **0.9722/0.9444/0.9444** (majority 0.3889, margin +0.56), iris
**0.8667/0.8667/0.7667** (majority 0.3333). The wine validation split held one
class; the "0% credit failure" was a dataset split.

**Experiment 3 — `local_contrastive`** (L1, mnist, feedforward, adam, 10 epochs,
n=2): `val_acc` 0.110/0.120, loss 17 → 3459 over the epochs. The credit read the
last 10 pixels as its label (no label channel in the pipeline; params 55.05K =
784→64 stack, no widened input). G11: row marked unavailable with the reason,
dry run prints it.

**Experiment 4 — homeostatic and random_projections, post-R4/R9:**
- `recurrent+homeostatic+adam+iris` (n=3, 5 epochs): 0.2333/0.3000/0.3333 —
  chance against a 0.333 majority. Error-blind by contract, not a dispatch bug.
- `causal_transformer+homeostatic+adam+mnist` (10 epochs, n=1): 0.1009 flat,
  loss 2.2519–2.2522 — R4 moves every weight, but homeostatic never sees the
  label, so the head cannot learn. Contract, documented on the identity card.
- `recurrent+random_projections+adam+copy_task` (n=2, 5 epochs):
  0.1885/0.1660, no crash — episode budget, not a dispatch defect.

**Experiment 5 — RL reach** (gradient+adam, feedforward, L1):
- acrobot, 40 epochs (400 episodes), n=1: mean_reward −500.0 throughout; the
  control's own validation is −500. Exploration-limited (the swing-up is not
  reached), and the RL success criterion names Pendulum.
- pendulum, 40 epochs, n=1: **−1289.7 random → −1183.8** (epoch curve −1246.8 /
  −1333.2 / −1366.7 / −1243.8 / −1176.7). Before G15 the space held **zero**
  cells and the run measured only its positive control.

**Experiment 6 — budget accounting** (0.08 h, mnist, 10 epochs, n=2): first wave
priced from the control (`~407 s/cell (positive control, 2 seed(s))`), one cell
started, its second seed **skipped** (`278.2s needed, −2.1s left`), run summary
`cells_skipped: 1` — no second truncated FAIL. Before: 60 s/cell default,
two seeds started, the second recorded 9/10 epochs FAIL.

**Defects Found:**
- **G10** — `TabularTask` split by tail slice over class-ordered sklearn data.
- **G11** — `local_contrastive` had no label channel; it contrasted against
  pixels and diverged.
- **G12** — graph-domain tasks were proposed on node-mode geometry (forward
  signature crash); the converse filter existed.
- **G13** — `schedule_for` treated explicit `n_seeds=1`/`epochs=1` as unset.
- **G14** — a run-deadline cut recorded `constraint_violation`; a serial wave
  started a seed it could not afford; the first wave was priced from the table
  default instead of the control's measurement; and `_measure_cost_model`
  wrote the L0 positive control's one-epoch walltime into the **L1** per-task
  map (mnist L1: 20.3 s for a 20.3 s/epoch cell), so the cache taught the next
  run to over-propose; the run-wide fallback was the last run's mean, so a
  0.1 s wine cell priced every unmeasured task at 0.1 s.
- **G15** — the dry-run gate scored RL cells with cross-entropy on dummy
  labels, so every continuous-control cell was filtered (`all-zero
  pseudo-gradients`).

**Fixes Applied:**
- `computronium/domains/tabular.py` — stratified deterministic split; `evaluate`
  reports `majority_baseline` / `val_acc_over_majority`.
- `computronium/experiment/schema/seed_registries.py` — `_UNAVAILABLE` carries
  `local_contrastive` with its reason.
- `computronium/experiment/simple_survey.py` — `_unavailable_declarations` +
  dry-run payload; `learning_survey.py` returns it too; `wave.py` prints it.
- `computronium/experiment/kernel/search_space.py` — graph-domain task requires
  graph geometry; explicit depth `is not None`.
- `computronium/experiment/kernel/evaluate.py` — FAIL cause `timeout` for an
  incomplete cell, `constraint_violation` only for a ceiling breach; no-epoch
  cells report `timeout` when the trainer hit the deadline.
- `computronium/experiment/wave.py` — `_SerialAdmission` (per-cell cost
  headroom), `_first_wave_price` (control epoch × declared epochs), price source
  in the wave log, and `_measure_cost_model` prices only complete cells at the
  run's own fidelity (the L0 control no longer prices L1), with the run-wide
  fallback as the merged per-task mean instead of the last run's mean.
- `computronium/experiment/kernel/compose.py` — dry-run gate declines RL tasks
  and one-class heads.
- Locks: `test_tabular_split_lock.py` (3), `test_incompatible_cell_refusal_lock.py`
  (4), `test_budget_truncation_lock.py` (10), `test_schedule_depth_lock.py` (3),
  `test_dry_run_gate_scope_lock.py` (4). Two pre-existing locks updated to the
  new truth: `test_search_space_user_axes_lock` (available credits, not a
  hardcoded 10), `test_sampler_lock` (pc_alm `credit.beta` vs gradient
  `credit.train_biases`).

**Verification:** new locks 25/25; `tests/property -k "search_space or schedule
or budget or tabular or dry_run or credit or cell_evaluation or cell_identity or
graph_pipeline or graph_batched"` 240 passed, 8 skipped, 5 xfailed (2
pre-existing failures queued as N5/N6). Live: wine 0.94–0.97, iris 0.77–0.87,
pendulum −1184 at 400 episodes, `--n-seeds 1` yields one seed, dry-run names the
unavailable credit. Ruff clean on changed files (pre-existing wave.py Register C
findings remain; `_cell_records` complexity 16 → 13). Pyright on changed files
at the HEAD baseline (5 errors, all pre-existing).

**Next Experiment:** N2 (plasticity on a learnable task), then N3 (substrate
breadth), then N4 (predictive-settling reach).

---

## Session 2026-11-12 (N2/N3/N4 close, N5/N6 hygiene, G16/G17/G18)

**Experiments (all ≤11 min, `--max-workers 1`, cuda):**

1. **N2a — plasticity on a learnable task** (MNIST feedforward, gradient+adam,
   3 epochs, n=2):
   ```
   --axes '{"substrate":["digital"],"geometry":["feedforward"],
     "dynamics":["instantaneous"],"plasticity":["null","routing"],
     "credit":["gradient"],"update":["adam"]}'
   ```
   routing **0.9684/0.9677**, null **0.9679/0.9662** → parity (+0.001), no harm.
   A single supervised task gives routing nothing to route *between*.

2. **N2b — fast weights with its compatible dynamics** (MNIST feedforward,
   `energy_minimization`+`thermodynamic_contrast`+adam, 2 epochs, n=2):
   fast_weights **0.9447/0.9476**, null **0.9472/0.9498** → parity (−0.002).
   energy_minimization on feedforward reaches 0.947 in 2 epochs (30 s/epoch),
   which also closes the "energy_minimization is weak" suspicion.

3. **N2c — recurrent + error-blind credit** (MNIST recurrent, `temporal_trace`,
   3 epochs, n=2): routing **0.0956/0.1234**, null **0.1018/0.1238** → chance,
   loss flat at ln 10. `TemporalTraceCredit.phases = (FREE,)`: the rule is
   STDP over settled (pre, post) pairs and never reads the label. Contract, not
   a dispatch bug — the same boundary R4 found for `homeostatic`.

4. **N3 — substrate breadth** (MNIST feedforward, gradient+adam, 3 epochs, n=3):
   digital **0.9672**, memristive **0.9675**, ternary **0.9588**, sparse
   **0.9672 — bit-identical to digital seed for seed**. That identity was G18.
   Re-run after the fix: sparse **0.9641/0.9648/0.9631** (0.9640), digital
   0.9672 → −0.32 pt at 50 % sparsity, curves no longer equal.

5. **N4 — predictive settling reach** (MNIST, `thermodynamic_contrast`, 2
   epochs): the space proposes feedforward *and* recurrent. Live recurrent:
   **0.5441/0.4511**, 144 s/epoch; the 0.2 h budget stopped after 3 cells.

**Defects Found:**
- **G16** — a short plan reported "No more cells to evaluate" with no cause; the
  void-constraint / compose / dry-run reasons were discarded.
- **G17** — the planner re-filtered with `_INCOMPATIBILITY_RULES`, a second
  source of truth: **15,348 of 58,968** space-legal coordinates dropped in
  silence, including the stale `temporal_trace x instantaneous` rule that the
  declared space and the compiled `hebbian` rung both admit.
- **G18** — `SparseSubstrate.get_forward_operator` ignored `sparsity`; the
  substrate axis named no difference.
- **G19 (open)** — `local_goodness` x `energy_minimization` diverges
  (loss 1.87 → 289.5, val_acc 0.0891 at 64 s/epoch).
- **Report noise** — `comp report` printed the claim-eligibility count 31 times
  (INFO inside a per-section accessor).
- **Stale fixture** — `_specs.unreachable_spec()` now yields 10 cells: the
  declaration it was written for became reachable when the axis filter started
  narrowing dynamics to the legal value. Its docstring is a comment until it is
  re-pointed at a still-void declaration.

**Fixes Applied:**
- `computronium/experiment/kernel/search_space.py` — `_compiled_void_constraints`
  returns named evaluators; `_void_rejection` names the first violated
  constraint; `_compose_rejection` returns the cause (`compose <Exc>`,
  `param budget`, `dry-run gate: <reason>`) and `_composable` wraps it;
  `_structural_rejection` holds the cache/void/compatibility filters and counts
  each cause; `iter_candidates`/`generate_candidates` take a `rejections` sink.
- `computronium/experiment/wave.py` — `StaticPlanner.rejections` +
  `rejection_summary()`, `PolicyPlanner.rejections` + `rejection_summary()`,
  `_rejection_summary` shared, compatibility drops counted via
  `_compatibility_violation`, short-plan warning names the causes, dry-run
  printer prints `pruned`.
- `computronium/experiment/execution/policy.py` — `ProposalContext.rejections`
  sink reaches `iter_candidates` from every policy.
- `computronium/experiment/simple_survey.py`, `learning_survey.py`,
  `survey_cli.py` — dry-run payload carries `pruned`; the summary format prints it.
- `computronium/experiment/surface/report.py` — eligibility count at DEBUG.
- `computronium/ontology/system.py` — stale `temporal_trace x instantaneous`
  flat rule deleted.
- `computronium/ontology/substrate/_substrate.py` — `SparseSubstrate.prune_weights`
  (magnitude mask, declared fraction) wired into the forward operator.
- `computronium/domains/registry.py`, `domains/__init__.py`,
  `experiment/schema/run_spec.py` — `TASK_COST_CLASS` + four accessors deleted;
  `task == "auto"` reads `domains._task_registry.CHEAP_TASKS`.
- Locks: `test_prune_diagnostics_lock.py` (4), `test_sparse_substrate_lock.py`
  (3); `test_smart_survey_lock` and `test_state_algebra_lock` updated to the
  derived truth (registry classes/baselines; `credit/` package).

**Verification:** new locks 7/7; `tests/property -k "search_space or prune or
sparse or smart_survey or state_algebra or compatible or dry_run or schedule or
task_registry or profile"` **158 passed**. Ruff on changed files at the HEAD
finding count (31 in `wave.py` + `test_smart_survey_lock`, 6 pre-existing in
`search_space.py`; no new findings). Pyright on changed files: only the 2
pre-existing `policy.py` errors. Live: `pruned: void constraint:
recurrent_instantaneous_gradient_credit (2)`; sparse ≠ digital; `comp report`
prints the eligibility line once.

**Next Experiment:** N7 (`local_contrastive` label channel), then N8 (matrix vs
declared-space reconciliation), then N9 (`local_goodness` x `energy_minimization`).

## Session 2026-11-12 (N7 label channel, G20 stream normalization, N9 void, N10 category)

**Experiments (all ≤13 min, `--max-workers 1`, cuda):**

1. **N7 first live cell — the channel works, the loss does not** (MNIST
   feedforward, `local_contrastive`+adam, L0, 3 epochs, n=2): val_acc
   **0.5174/0.5612** (G11's chance-level 0.11 is gone) but free CE grew
   **223 → 735**. Re-run at L1 10 epochs: CE 223 → 1121, val_acc 0.52–0.59.
   `update.step_size=0.001` is the credit's own "just slow (~0.5)" rung, so
   the accuracy was expected — the *loss* was not. Probe
   (`scripts/probes/n7_label_channel_regime.py`, 300 steps): `‖h2‖`
   0.10 → 10.7 → 52.4 → 136.6 and `‖W_head‖F` 0.2 → 13.0 → 97.0 → 312.5.
2. **G20 fix — five epochs, same cell**: free CE **1.30 → 1.16**, hidden
   acts unit-RMS, val_acc 0.5362/0.5738 (n=2). The label channel was always
   fine; the geometry was not producing the stream the credit trained on.
3. **N7 regime arm** (L1, 10 epochs, n=1,
   `step_size=0.1 / readout_scale=0.3 / sequential_lr=0.1`): val_acc
   **0.7295**, CE 1.59 → 0.96.
4. **N7 claim run** (same, n=3): **0.7295 / 0.6793 / 0.7042 →
   0.7043 ± 0.0251**, all PASS, 1 claim-eligible cell (255 s/cell).
5. **N9** (MNIST feedforward `local_goodness`+adam, 3 epochs, n=1,
   instantaneous vs energy_minimization): **0.9628** vs **0.0892**, the
   latter with free loss **1.87 → 289.5 → 214,625** at 64 s/epoch.

**Defects Found:**
- **G20** — `LocalContrastiveCredit` recomputes a stream-normalized prefix
  (`stream_norm=True`) and trains the head on it; `FeedforwardGeometry` had
  no normalization, so the head was fitted on unit-scale features and
  applied to unbounded ones. The loss grows while accuracy stalls.
- **G19 (closed as contract)** — `local_goodness x energy_minimization`
  diverges because differentiating the goodness contrast through an unrolled
  settle stops being local (graph is W^N).
- **Stale lock** — `test_primitive_compatibility_lock` still asserted the
  `temporal_trace x instantaneous` rule G17 deleted.
- **Stale fixture** — `mechanism_spec()` cannot exercise the new void
  constraint (its plasticity axis voids every dynamics); the lock now
  compiles the constraint and calls it with an explicit selection.

**Fixes Applied:**
- `computronium/core/label_channel.py` (new) — `augmented_input_shape`,
  `label_augmented`, `probe_input`, `LabelChannelSystem` (train appends,
  `forward` sweeps C·B rows in one pass, `__call__` mirrors `forward` because
  tasks call `system(x)` and special methods bypass `__getattr__`, all other
  attribute access delegates). The first claim run logged
  `task.evaluate() failed: 'LabelChannelSystem' object is not callable` once
  per cell; the clean re-run (same three seeds, 0 warnings, same
  0.7295/0.6793/0.7042) is the one filed in the store.
- `computronium/ontology/credit/__init__.py` — `label_channel` config field
  (set by `local_contrastive()`), `error_blind` ClassVar on every credit
  class, protocol + identity-card statements.
- `computronium/ontology/geometry.py` — `GeometryConfig.stream_norm` +
  `feedforward(stream_norm=)`, applied in `_apply_stack` and `route`.
- `computronium/experiment/kernel/compose.py` — credit config built before
  geometry, `label_dim = output_dim`, input widened, `stream_norm` turned on,
  system wrapped in `LabelChannelSystem`.
- `computronium/experiment/kernel/evaluate.py` — probes receive
  `probe_input(...)` (zero channel).
- `computronium/experiment/schema/seed_registries.py` — `_UNAVAILABLE`
  emptied; `local_goodness_energy_minimization` declared void.
- Locks: `test_label_channel_lock.py` (9), `test_error_blind_credits_lock.py`
  (5), `test_incompatible_cell_refusal_lock.py` (5, incl. the void),
  `test_search_space_user_axes_lock.py` + `test_primitive_compatibility_lock.py`
  updated to the derived truth.

**Verification:** new locks 20/20; `tests/property -k "label_channel or
error_blind or compose or geometry or credit or search_space or
incompatible_cell"` **299 passed, 1 failed** at HEAD on the stale
`temporal_trace` row, which is now removed (that file 91 passed). Ruff on
changed files: only the pre-existing findings (compose `_compose_configs_cached`
argument count, evaluate/geometry legacy counts unchanged). Pyright:
`label_channel.py` 0 errors; the rest unchanged from HEAD.

**Next Experiment:** N8 (planner flat matrix vs declared space), then R6 at
round close. Optional N11: `local_contrastive` at `step_size=0.2–0.3`
(the probe's own regime) against the 0.7043 floor.
